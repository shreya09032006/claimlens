"""Feature extraction for the 3-class email model (safe / marketing / phishing).

Works from what the Gmail extension already sends: sender, subject, body, links.
Text alone cannot separate a bank alert, a sale mail and a phishing mail, so on top of
the words we add structural signals: where links go, lookalike domains, shorteners,
unsubscribe wording, credential requests, and so on.
"""
import re
from urllib.parse import urlparse

from core.emailcheck import BRANDS, _root, shown_domain

FREE_MAIL = {"gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "rediffmail.com", "proton.me", "protonmail.com"}
SHORTENERS = ("bit.ly", "tinyurl.com", "cutt.ly", "rb.gy", "is.gd", "wa.link", "t.co", "goo.gl", "shorturl.at")
BAD_TLDS = (".xyz", ".top", ".click", ".buzz", ".icu", ".live", ".shop", ".cfd", ".sbs", ".monster", ".cyou", ".rest")
ESP_HINTS = ("sendgrid", "mailchimp", "list-manage", "mandrillapp", "amazonses", "klclick", "mailgun",
             "sparkpost", "mailjet", "hubspot", "braze", "clevertap", "netcore", "moengage", "customeriomail")
TRACK_HINTS = ESP_HINTS + ("inflection", "track", "click", "trk", "redirect", "bounce")
TRACK_LABELS = {"links", "link", "email", "mail", "e", "em", "go", "url", "click", "trk", "t", "r", "news", "mailer"}


def is_tracker(h):
    """True for click-tracking / email-service hosts, which legitimately differ from the text shown."""
    return any(k in h for k in TRACK_HINTS) or h.split(".")[0] in TRACK_LABELS
R = lambda p: re.compile(p, re.I)
PATS = {
    "unsub":      R(r"unsubscribe|opt[- ]?out|manage (your )?(email )?preferences|view (this email )?in (your )?browser|you are receiving this"),
    "promo":      R(r"\b\d{1,2}\s?%\s?off|flat \d+|use code|coupon|promo code|sale\b|deal\b|discount|bestseller|new arrival|shop now|order now|buy now|limited[- ]time offer|festival"),
    "cred":       R(r"\b(otp|cvv|pin|password|passcode)\b.{0,40}(share|send|enter|reply|confirm|verify|provide)|(share|send|enter|reply|confirm|verify|provide).{0,40}\b(otp|cvv|pin|password|passcode)\b|verify your (account|identity|kyc|details)|confirm your (account|identity|details|password)|log ?in to (keep|restore|verify|avoid)"),
    "safe_otp":   R(r"do not share (it|this|your)|never share|(valid|expires?) (for|in) \d+ (min|minutes)|if you did not (request|initiate)"),
    "threat":     R(r"(account|card|sim|access|service).{0,25}(block|suspend|clos|deactivat|restrict|terminat|lock)|legal action|penalt|arrest|will be (deleted|disabled)"),
    "urgent":     R(r"within \d+ (hours?|minutes?)|immediately|urgent|act now|last (date|warning|chance)|today only|expires? (today|soon|in)|final notice|24 hours"),
    "fee":        R(r"(registration|processing|redelivery|delivery|customs|release|security) (fee|charge|deposit)|refundable (security )?(amount|deposit|fee)|deposit.{0,30}(seat|offer|job)|pay.{0,25}(fee|charge|to (claim|receive|release))|gift cards?"),
    "prize":      R(r"you (have )?(won|been selected)|lottery|prize|claim your (reward|refund|gift)|refund.{0,20}(pending|waiting|approved)|congratulations"),
    "generic":    R(r"dear (customer|user|account holder|member|sir|madam|valued)|valued customer"),
    "attach":     R(r"attached|attachment|invoice|\.(zip|html|htm|exe|apk|iso)\b|open the (file|document)"),
    "trans":      R(r"order (#|no|number|id)|invoice (#|no)|receipt|your (booking|ticket|payment|transaction|statement)|has been (shipped|delivered|dispatched|credited|debited)|tracking"),
    "personal":   R(r"\b(hi|hey|hello)\s+[a-z]{2,}\b|thanks,|regards,|see you|let me know|can we|could you|meeting|standup|lunch|tomorrow"),
}
NUMERIC = ["n_links", "n_domains", "frac_off", "shortener", "bad_tld", "ip_host", "brand_imitate", "text_mismatch",
           "free_sender_brand", "esp_link", "brand_official_links", "excl", "upper", "len_log", "digits_ratio"] + list(PATS)


def _dom(addr):
    a = (addr or "").strip().lower()
    a = a.split("<")[-1].rstrip(">")
    return a.split("@")[-1].strip() if "@" in a else ""


def _brands_in(text):
    t = text.lower()
    return [b for b in BRANDS if re.search(r"\b" + b + r"\b", t)]


def extract(sender="", subject="", body="", links=None):
    """Return (text_for_tfidf, numeric_feature_list)."""
    links = links or []
    text = f"{subject}\n{body}"
    sd = _dom(sender)
    sroot = _root(sd) if sd else ""
    hosts, off, mism, ip, short, badtld, imit, esp, official = [], 0, 0, 0, 0, 0, 0, 0, 0
    claimed = _brands_in(text + " " + sd)
    for l in links:
        href = l.get("href", "") if isinstance(l, dict) else l[0]
        txt = l.get("text", "") if isinstance(l, dict) else l[1]
        h = (urlparse(href).hostname or "").lower()
        if not h:
            continue
        hosts.append(h)
        r = _root(h)
        if sroot and r != sroot:
            off += 1
        if re.fullmatch(r"\d{1,3}(\.\d{1,3}){3}", h):
            ip += 1
        if any(h == s or h.endswith("." + s) for s in SHORTENERS):
            short += 1
        if h.endswith(BAD_TLDS):
            badtld += 1
        if any(k in h for k in ESP_HINTS):
            esp += 1
        labs = [x.replace("-", "") for x in h.split(".")]
        for b, real in BRANDS.items():
            if any(b in x for x in labs) and not any(h == x or h.endswith("." + x) for x in real):
                imit += 1
            elif any(h == x or h.endswith("." + x) for x in real):
                official += 1
        m = shown_domain(txt)
        if m and "@" not in txt and not is_tracker(h) and _root(m.group(0)) != r:
            mism += 1
    for b, real in BRANDS.items():  # lookalike sender domain
        slabs = [x.replace("-", "") for x in sd.split(".")]
        if sd and any(b in x for x in slabs) and not any(sd == x or sd.endswith("." + x) for x in real):
            imit += 1
    free_brand = int(sd in FREE_MAIL and bool(claimed))
    n = len(hosts)
    letters = [c for c in text if c.isalpha()]
    f = {
        "n_links": min(n, 20) / 20, "n_domains": min(len(set(hosts)), 8) / 8, "frac_off": off / n if n else 0,
        "shortener": min(short, 3) / 3, "bad_tld": min(badtld, 3) / 3, "ip_host": min(ip, 1),
        "brand_imitate": min(imit, 3) / 3, "text_mismatch": min(mism, 3) / 3, "free_sender_brand": free_brand,
        "esp_link": min(esp, 3) / 3, "brand_official_links": min(official, 3) / 3,
        "excl": min(text.count("!"), 10) / 10,
        "upper": (sum(c.isupper() for c in letters) / len(letters)) if letters else 0,
        "len_log": min(len(text), 8000) / 8000,
        "digits_ratio": (sum(c.isdigit() for c in text) / len(text)) if text else 0,
    }
    for k, p in PATS.items():
        f[k] = min(len(p.findall(text)), 3) / 3
    return text, [float(f[k]) for k in NUMERIC]
