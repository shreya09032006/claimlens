import asyncio
from urllib.parse import urlparse
import httpx
from .config import TAVILY_API_KEY, FACTCHECK_API_KEY, ALLOWLIST


def _domain(url: str) -> str:
    return urlparse(url).netloc.replace("www.", "")


def _norm_date(raw):
    if not raw:
        return None
    raw = str(raw).strip()
    if len(raw) >= 10 and raw[4:5] == "-" and raw[7:8] == "-":
        return raw[:10]
    try:
        from email.utils import parsedate_to_datetime
        return parsedate_to_datetime(raw).date().isoformat()
    except Exception:
        return None


async def _factcheck(client: httpx.AsyncClient, claim: str):
    r = await client.get(
        "https://factchecktools.googleapis.com/v1alpha1/claims:search",
        params={"query": claim, "key": FACTCHECK_API_KEY, "pageSize": 5},
    )
    r.raise_for_status()
    out = []
    for c in r.json().get("claims", []):
        for rev in c.get("claimReview", [])[:1]:
            out.append({
                "source": rev.get("publisher", {}).get("site") or _domain(rev.get("url", "")),
                "url": rev.get("url", ""),
                "title": rev.get("title", ""),
                "snippet": f"Rated '{rev.get('textualRating', '')}': {c.get('text', '')}",
                "date": _norm_date(rev.get("reviewDate")),
            })
    return out


async def _tavily(client: httpx.AsyncClient, claim: str):
    r = await client.post(
        "https://api.tavily.com/search",
        headers={"Authorization": f"Bearer {TAVILY_API_KEY}"},
        json={
            "query": claim,
            "include_domains": ALLOWLIST,
            "max_results": 5,
            "topic": "general",
        },
    )
    r.raise_for_status()
    out = []
    for x in r.json().get("results", []):
        out.append({
            "source": _domain(x["url"]),
            "url": x["url"],
            "title": x.get("title", ""),
            "snippet": x.get("content", "")[:1500],
            "date": _norm_date(x.get("published_date")),
        })
    return out


_QSYS = """Rewrite a claim into 3 short English web-search queries for fact-checking.
Use standard medical and official terminology (e.g. PCOD -> PCOS polycystic ovary syndrome, sugar -> diabetes, BP -> hypertension, TB -> tuberculosis). Keep key numbers, names and dates.
Return {"queries": ["...", "...", "..."]}"""


async def _queries(claim: str):
    try:
        from .llm import ask_json
        d = await ask_json(_QSYS, claim, 300)
        qs = [q for q in d.get("queries", []) if isinstance(q, str) and q.strip()]
        return ([claim] + qs)[:4]
    except Exception as e:
        print("query rewrite failed:", str(e)[:80])
        return [claim]


async def retrieve(claim: str):
    async with httpx.AsyncClient(timeout=20) as client:
        qs = await _queries(claim)
        tasks = []
        for q in qs:
            tasks += [_factcheck(client, q), _tavily(client, q)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
    evidence, seen = [], set()
    for res in results:
        if isinstance(res, Exception):
            print("retrieval error:", str(res)[:100])
            continue
        for e in res:
            if e["url"] in seen:
                continue
            seen.add(e["url"])
            evidence.append(e)
    for i, e in enumerate(evidence, 1):
        e["id"] = i
    return evidence
