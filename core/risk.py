"""core/risk.py - the ML model decides; rules and header checks can only escalate.

ML score (0-100) -> level:  70+ high | 30-69 medium | under 30 low (safe)
Rule/header checks: a 'high' result from them (failed SPF/DKIM, lookalike
domain, 3+ red flags...) keeps the level at high. Weak rule flags alone
(e.g. a phone number in a footer) never raise the level; they are shown
as evidence only.
"""
import re

from core import mlmodels

_RANK = {"low": 0, "medium": 1, "high": 2}


def ml_level(p: float) -> str:
    return "high" if p >= 0.70 else "medium" if p >= 0.30 else "low"


# ---- "Promotional" mode: bulk marketing mail that is not phishing-like ----
def _rx(*parts):
    return re.compile("|".join(parts), re.I)


_BULK = _rx(
    r"unsubscribe", r"you are receiving (this|these)", r"you.re receiving (this|these)",
    r"you received this email because", r"you have subscribed", r"you subscribed",
    r"subscribed to (our|the)", r"mailing list", r"view (this email )?in (your )?browser",
    r"manage (your )?(email )?preferences", r"opt.?out",
)
_OFFER = _rx(
    r"\d+\s*%\s*(off|refund|discount)", r"\boffer\b", r"\bsale\b", r"discount",
    r"limited (time|period)", r"coupon", r"promo code", r"\bexclusive\b", r"\bdeal\b",
    r"shop now", r"buy now", r"enrol+ now", r"register now", r"free trial", r"hurry",
    r"offer ends", r"ends on", r"last date", r"cashback", r"money.?back", r"\u20b9\s?\d",
    r"\bpercentile\b", r"\bcourse\b", r"webinar",
)
_BULK_SENDER = _rx(
    r"@(?:e|em|email|emails|mail|mailer|news|newsletter|offers|promo|promos|marketing"
    r"|updates|info|mkt|go)\.[\w-]+\.[\w.]+",
)
_MORE = _rx(r"read more", r"learn more", r"new arrivals", r"this week on", r"newsletter")
_TRANS = _rx(
    r"order number", r"order #", r"has shipped", r"out for delivery", r"delivered",
    r"invoice", r"receipt", r"\botp\b", r"one.time password", r"debited", r"credited",
    r"your refund", r"has been processed", r"sign.in to your", r"security alert",
    r"reset your password", r"verify your email",
)


def promo_cues(text: str, sender: str = "") -> list:
    """Return the marketing cues found, or [] if it does not look like bulk marketing."""
    if _TRANS.search(text):
        return []        # orders, receipts, OTPs and alerts are not marketing
    bulk = _BULK.search(text)
    bulk_sender = _BULK_SENDER.search(sender + " " + text)
    offer = _OFFER.search(text)
    n_offer = len(_OFFER.findall(text))
    more = _MORE.search(text)
    if not (bulk_sender or (bulk and (offer or more)) or n_offer >= 3):
        return []
    cues = []
    if bulk_sender:
        cues.append("sent from a bulk-mail address (" + bulk_sender.group(0).lower() + ")")
    if bulk:
        cues.append("mailing-list wording (" + bulk.group(0).lower() + ")")
    if offer:
        cues.append("offer or sales wording (" + offer.group(0).lower().strip() + ")")
    elif more:
        cues.append("newsletter wording (" + more.group(0).lower() + ")")
    return cues


def combine(rule_level: str, text: str, sender: str = "") -> dict:
    ml = mlmodels.predict_email(text)
    if ml is None:                       # model not trained / file missing: fall back to rules
        return {"level": rule_level, "ml": None, "note": None, "category": None, "promo_cues": []}
    p = ml["probability"]
    level, note = ml_level(p), None
    if rule_level == "high" and _RANK[level] < 2:
        level = "high"
        note = "Strong red flags were found by the rule and header checks."
    elif rule_level != "low" and level == "low":
        note = "Some weak red flags were found, but the wording reads like a normal message."
    if level != "low" and note is None:   # verdict came from the model alone: say so
        words = ", ".join(ml["pushed_toward_phishing"][:4])
        note = f"The wording resembles phishing emails (ML model score {round(p * 100)} / 100)" + (f": {words}." if words else ".")
    category, cues = None, []
    if level == "low":                   # only a message that is NOT phishing-like can be called promotional
        cues = promo_cues(text, sender)
        if cues:
            category = "promotional"
            note = "Looks like bulk marketing mail: " + "; ".join(cues) + ". Not phishing-like (ML model score " + str(round(p * 100)) + " / 100)."
    return {"level": level, "ml": ml, "note": note, "category": category, "promo_cues": cues}