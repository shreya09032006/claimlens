from datetime import date
import re


def _clean(t):
    t = re.sub(r"[#*_`>]+", " ", t or "")
    return re.sub(r"\s+", " ", t).strip()


def _quote(q, snippet, claim):
    qn, sn = _clean(q), _clean(snippet)
    if len(qn) >= 20 and qn in sn:
        out = qn
    else:
        words = set(w for w in re.findall(r"\w+", claim.lower()) if len(w) > 3)
        sents = re.split(r"(?<=[.!?])\s+", sn) or [sn]
        out = max(sents, key=lambda x: len(words & set(re.findall(r"\w+", x.lower()))))
    if len(out) > 220:
        cut = out[:220]
        i = max(cut.rfind(". "), cut.rfind("; "))
        out = cut[: i + 1] if i > 80 else cut.rsplit(" ", 1)[0] + "…"
    return out


from .llm import ask_json
from .config import LABELS, LANG_NAMES

SYSTEM = """You are a strict fact-checking judge.
Use ONLY the evidence provided. Never use outside knowledge.
Labels:
- Verified: evidence clearly supports the whole claim.
- False: evidence clearly contradicts the claim.
- Outdated: the claim was true earlier but a date, deadline or figure has since changed or passed. Compare today's date and the evidence dates.
- Partly supported: some parts are supported, others wrong or missing.
- Cannot be confirmed: evidence is missing, unrelated or inconclusive.
Return JSON:
{"label": "...", "confidence": 0.0-1.0,
 "claim_local": "the claim itself translated into EXACTLY the same target language as explanation_local (never any other language or script); empty string if English",
 "explanation_en": "2-3 plain sentences: what is right/wrong and why",
 "explanation_local": "the same explanation written in the target language named in the user message, in simple, grammatically correct everyday words (check gender and number agreement, and write it as a native speaker would, not as a literal translation); empty string if the target language is English",
 "used": [{"id": 1, "quote": "short exact quote copied from that evidence snippet"}]}
Only cite evidence ids whose snippet DIRECTLY supports or contradicts the claim. Never cite a snippet that is merely related in topic. Prefer at most 2 citations.
Strict rules:
- False requires evidence that directly contradicts the claim. Evidence that is merely unrelated, or silent on the claim, is NOT a contradiction: use Cannot be confirmed.
- A rumour, hearsay or prediction ("someone said", "will happen next week") with no direct evidence is Cannot be confirmed.
- Verified requires evidence that explicitly supports every part of the claim.
- If the claim itself states a deadline or date that is earlier than today's date but presents it as still open or upcoming, and the evidence shows that date has passed, was extended, or the rule changed, the label is Outdated.
- Outdated applies when the claim presents something as current or upcoming (a deadline, rate, scheme, rule) but the evidence shows it has expired or changed."""

CANNOT = {
    "en": "I could not find reliable sources to confirm or deny this. Please do not forward it until it is verified.",
    "hi": "मुझे इसकी पुष्टि या खंडन करने के लिए भरोसेमंद स्रोत नहीं मिले। कृपया सत्यापित होने तक इसे आगे न भेजें।",
    "mr": "याची पुष्टी किंवा खंडन करण्यासाठी मला विश्वासार्ह स्रोत सापडले नाहीत. पडताळणी होईपर्यंत कृपया हे पुढे पाठवू नका.",
    "ml": "ഇത് സ്ഥിരീകരിക്കാനോ നിഷേധിക്കാനോ വിശ്വസനീയമായ ഉറവിടങ്ങൾ കണ്ടെത്താനായില്ല. സ്ഥിരീകരിക്കുന്നതുവരെ ദയവായി ഇത് ഫോർവേഡ് ചെയ്യരുത്.",
}


def _cannot(claim, target):
    return {
        "text": claim,
        "label": "Cannot be confirmed",
        "confidence": 0.0,
        "explanation_en": CANNOT["en"],
        "explanation_local": "" if target == "en" else CANNOT.get(target, ""),
        "evidence": [],
    }


async def judge(claim: str, evidence: list, target: str):
    if not evidence:
        return _cannot(claim, target)

    evidence = evidence[:6]
    ev_text = "\n\n".join(
        f"[{e['id']}] {e['source']} | date: {e['date'] or 'unknown'} | {e['title']}\n{e['snippet']}"
        for e in evidence
    )
    user = (
        f"Today's date: {date.today().isoformat()}\n"
        f"Target language for explanation_local: {LANG_NAMES.get(target, 'English')} ({target})\n"
        f"Claim: {claim}\n\nEvidence:\n{ev_text}"
    )
    data = await ask_json(SYSTEM, user)

    label = data.get("label")
    if label not in LABELS:
        return _cannot(claim, target)

    by_id = {e["id"]: e for e in evidence}
    cited = []
    for u in data.get("used", []):
        e = by_id.get(u.get("id"))
        if not e:
            continue
        quote = _quote(u.get("quote", ""), e["snippet"], claim)
        if any(c["url"] == e["url"] for c in cited):
            continue
        cited.append({"quote": quote, "source": e["source"], "date": e["date"], "url": e["url"]})

    if label != "Cannot be confirmed" and not cited:
        return _cannot(claim, target)

    return {
        "text": claim,
        "claim_local": "" if target == "en" else data.get("claim_local", ""),
        "label": label,
        "confidence": 0.0 if label == "Cannot be confirmed" else float(data.get("confidence", 0.5)),
        "explanation_en": data.get("explanation_en", ""),
        "explanation_local": "" if target == "en" else data.get("explanation_local", ""),
        "evidence": [] if label == "Cannot be confirmed" else cited,
    }
