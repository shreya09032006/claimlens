import asyncio
from .claims import extract_claims
from .retrieval import retrieve
from .judge import judge
from .config import LANG_NAMES


def _script_lang(text):
    import re
    counts = {"ml": len(re.findall(r"[\u0D00-\u0D7F]", text)),
              "dev": len(re.findall(r"[\u0900-\u097F]", text))}
    return counts


async def _check_one(claim: str, target: str):
    evidence = await retrieve(claim)
    return await judge(claim, evidence, target)


async def check_text(text: str, target_lang=None):
    lang, claims = await extract_claims(text)
    sc = _script_lang(text)
    if sc['ml'] == 0 and lang == 'ml':
        lang = 'mr' if sc['dev'] > 0 else 'en'
    if target_lang in LANG_NAMES:
        target = target_lang
    else:
        target = lang if lang in LANG_NAMES else "en"
    results = await asyncio.gather(*[_check_one(c, target) for c in claims])
    from .redflags import scan
    return {"language": lang, "target_language": target, "claims": list(results), "redflags": scan(text)}
