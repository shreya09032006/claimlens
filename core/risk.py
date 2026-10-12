"""Combine the ML prediction with rule evidence into one verdict.

The ML model reads wording; the rules read facts (lookalike domains, link/text mismatch,
shorteners, failed SPF/DKIM). A fact beats a guess, so any HIGH finding means phishing
whatever the model says, and a marketing/safe label is downgraded when several soft red
flags pile up. The model alone never produces a 'phishing' label on weak evidence.
"""
from urllib.parse import urlparse

from ml.emailfeatures import BAD_TLDS, SHORTENERS, _dom, is_tracker
from .emailcheck import BRANDS, _brand_check, _root, shown_domain
from .redflags import scan

TRUSTED = {_root(d) for v in BRANDS.values() for d in v} | {
    "github.com", "gitlab.com", "apple.com", "atlassian.com", "slack.com", "notion.so", "dropbox.com", "digitalocean.com"}
def lite_findings(sender="", subject="", body="", links=None):
    """Rule evidence from what the Gmail badge sends (no raw headers). [(sev, message)]"""
    f, sd = [], _dom(sender)
    if sd:
        _brand_check(sd, f, "Sender domain")
    for l in links or []:
        href, txt = (l.get("href", ""), l.get("text", "")) if isinstance(l, dict) else l
        h = (urlparse(href).hostname or "").lower()
        if not h:
            continue
        _brand_check(h, f, "Link domain")
        m = shown_domain(txt)
        if m and "@" not in txt and not is_tracker(h) and _root(m.group(0)) != _root(h):
            f.append(("high", f"Link text shows '{m.group(0)}' but really goes to '{h}'"))
        if any(h == s or h.endswith("." + s) for s in SHORTENERS):
            f.append(("medium", f"Shortened link hides the real site ({h})"))
        if h.endswith(BAD_TLDS):
            f.append(("medium", f"Link on a domain type often used by scams ({h})"))
        try:
            import urlcheck
            seen = set()
            for l in links or []:
                href = l.get("href", "") if isinstance(l, dict) else l[0]
                h = (urlparse(href).hostname or "").lower()
                if not h or h in seen or is_tracker(h) or _root(h) in TRUSTED or len(seen) >= 6:
                    continue
                seen.add(h)
                m = urlcheck.scan_url(href)
                if m and m["phishing_probability"] >= 0.9:
                    f.append(("medium", f"Link looks like phishing to the URL model ({h})"))
        except Exception:
            pass
    for fl in scan(f"{subject} {body}")["flags"]:
        f.append(("medium", fl))
    roots = {_root(urlparse(l.get("href", "") if isinstance(l, dict) else l[0]).hostname or "") for l in (links or [])} - {""}
    if not f and _root(sd) in TRUSTED and roots <= {_root(sd)}:
        f.append(("ok", f"Sender and all links belong to {_root(sd)}"))
    return list(dict.fromkeys(f))


def combine(ml, findings, auth=None):
    """ml: result of predict_email3 (or None). findings: [(sev, msg)]. auth: optional {'spf','dkim','dmarc'}."""
    hard = [m for s, m in findings if s == "high"]
    soft = [m for s, m in findings if s == "medium"]
    auth = auth or {}
    failed = [k.upper() for k in ("spf", "dkim", "dmarc") if (auth.get(k) or "") in ("fail", "softfail")]
    reasons = hard + (["Failed " + "/".join(failed) + " check on the sender"] if failed else []) + soft[:3]
    p = (ml or {}).get("probs", {})
    label = (ml or {}).get("label", "unsure")
    if hard or failed:
        out = "phishing"
    elif label == "phishing":
        if soft:
            out = "phishing"
        elif p.get("phishing", 0) >= 0.9:
            out = "suspicious"
        else:  # model alone, no rule evidence: show its best non-phishing guess instead of a false alarm
            out = max((c for c in p if c != "phishing"), key=p.get)
    elif label in ("safe", "marketing"):
        weak_phish = p.get("phishing", 0) >= 0.3 and len(soft) >= 1
        out = "suspicious" if (len(soft) >= 3 or weak_phish) else label
    else:  # unsure
        out = "suspicious" if len(soft) >= 2 else "unsure"
    return {"label": out, "confidence": (ml or {}).get("confidence"), "probs": p, "reasons": reasons}