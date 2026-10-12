import email
import re
from email import policy
from email.utils import parseaddr
from html.parser import HTMLParser
from urllib.parse import urlparse

from .redflags import scan

BRANDS = {
    "sbi": ["sbi.co.in", "onlinesbi.sbi", "sbi.com"], "hdfc": ["hdfcbank.com"],
    "icici": ["icicibank.com", "icicilombard.com"], "paytm": ["paytm.com"],
    "amazon": ["amazon.in", "amazon.com"], "google": ["google.com"],
    "microsoft": ["microsoft.com"], "paypal": ["paypal.com"], "netflix": ["netflix.com"],
    "incometax": ["incometax.gov.in"],
}


def _dom(addr):
    a = parseaddr(addr or "")[1]
    return a.split("@")[-1].lower().strip() if "@" in a else ""


def _root(d):
    p = [x for x in (d or "").lower().split(".") if x]
    if len(p) >= 3 and p[-2] in ("co", "gov", "org", "ac", "net", "com", "nic"):
        return ".".join(p[-3:])
    return ".".join(p[-2:])


class _Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links, self._href, self._txt = [], None, ""

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self._href, self._txt = dict(attrs).get("href"), ""

    def handle_data(self, data):
        if self._href is not None:
            self._txt += data

    def handle_endtag(self, tag):
        if tag == "a" and self._href is not None:
            self.links.append((self._href, self._txt.strip()))
            self._href = None


def shown_domain(text):
    """Return a regex match only if the link text really shows a web address.

    Degree names and abbreviations such as 'B.Tech', 'Ph.D' or 'B.Com' look like
    domains but are not: the first label must be 3+ letters, and the text must start
    with http(s):// or www., or be essentially just the address.
    """
    t = (text or "").strip().lower()
    m = re.search(r"([a-z0-9-]+\.)+[a-z]{2,}", t)
    if not m or len(m.group(0).split(".")[0]) < 3:
        return None
    looks_like_url = t.startswith(("http://", "https://", "www.")) or len(t) <= len(m.group(0)) + 25
    return m if looks_like_url and " " not in t.split("/")[0] else None


def _brand_check(domain, out, where):
    # match inside one label at a time: joining labels ("links.bigbasket.com" -> "linksbigbasketcom")
    # created false hits such as "sbi" across "links" + "bigbasket"
    labels = [x.replace("-", "") for x in domain.split(".")]
    for b, real in BRANDS.items():
        if any(b in x for x in labels) and not any(domain == r or domain.endswith("." + r) for r in real):
            out.append(("high", f"{where} '{domain}' imitates {b.upper()} but is not its real domain"))
            return


def check(raw: bytes) -> dict:
    raw = raw.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")
    msg = email.message_from_bytes(raw, policy=policy.default)
    f = []
    from_d = _dom(str(msg.get("From", "")))
    rp_d = _dom(str(msg.get("Return-Path", "")))
    rt_d = _dom(str(msg.get("Reply-To", "")))

    ar = " ".join(str(h) for h in (msg.get_all("Authentication-Results") or []))
    auth = {}
    for k in ("spf", "dkim", "dmarc"):
        m = re.search(k + r"=(\w+)", ar, re.I)
        auth[k] = m.group(1).lower() if m else None

    dk_ok, dk_dom = None, None
    sig = msg.get("DKIM-Signature")
    if sig:
        m = re.search(r"\bd=([^;\s]+)", str(sig))
        dk_dom = m.group(1).lower() if m else None
        try:
            import dkim
            dk_ok = bool(dkim.verify(raw))
        except Exception:
            dk_ok = None
    auth["dkim_verified_here"] = dk_ok
    auth["dkim_domain"] = dk_dom

    if auth["dkim"] == "fail" or auth["spf"] in ("fail", "softfail") or auth["dmarc"] == "fail":
        f.append(("high", "The receiving mail server recorded a failed SPF, DKIM or DMARC check"))
    elif not any(auth[k] for k in ("spf", "dkim", "dmarc")):
        f.append(("info", "No authentication results found. Paste the full original source (Gmail: Show original)"))
    if not sig:
        f.append(("medium", "The email carries no DKIM digital signature"))
    elif dk_ok is False and not auth["dkim"]:
        f.append(("info", "Signature could not be verified here. Copying an email often breaks it, so use the original file"))
    if dk_dom and from_d and _root(dk_dom) != _root(from_d):
        f.append(("high", f"Signed by '{dk_dom}', but the sender shows '{from_d}'"))
    if rp_d and from_d and _root(rp_d) != _root(from_d):
        f.append(("medium", f"Bounce address '{rp_d}' differs from sender '{from_d}'"))
    if rt_d and from_d and _root(rt_d) != _root(from_d):
        f.append(("high", f"Replies go to '{rt_d}', not to the sender '{from_d}'"))
    _brand_check(from_d, f, "Sender domain")

    body = msg.get_body(preferencelist=("html", "plain"))
    content = body.get_content() if body else ""
    text = re.sub(r"<[^>]+>", " ", content)
    p = _Links()
    try:
        p.feed(content)
    except Exception:
        pass
    seen = []
    for href, txt in p.links:
        hd = (urlparse(href).hostname or "").lower()
        if not hd:
            continue
        seen.append(hd)
        _brand_check(hd, f, "Link domain")
        m = shown_domain(txt)
        if m and "@" not in txt and not any(k in hd for k in ("inflection", "track", "click", "trk", "redirect", "sendgrid", "mailchimp", "list-manage")) and _root(m.group(0)) != _root(hd):
            f.append(("high", f"Link text shows '{m.group(0)}' but really goes to '{hd}'"))
        if re.search(r"(bit\.ly|tinyurl|cutt\.ly|rb\.gy)", hd):
            f.append(("medium", f"Shortened link hides the real site ({hd})"))
    for fl in scan(str(msg.get("Subject", "")) + " " + text)["flags"]:
        f.append(("medium", fl))

    uniq = list(dict.fromkeys(f))
    high = sum(1 for s, _ in uniq if s == "high")
    med = sum(1 for s, _ in uniq if s == "medium")
    level = "high" if high >= 1 or med >= 3 else "medium" if med >= 1 else "low"
    return {"level": level, "from": from_d, "subject": str(msg.get("Subject", "")),
            "auth": auth, "links": list(dict.fromkeys(seen))[:8],
            "findings": [{"sev": s, "msg": m} for s, m in uniq]}