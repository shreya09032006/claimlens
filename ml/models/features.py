import math
import re
from urllib.parse import urlparse

SHORT = ("bit.ly", "tinyurl.com", "cutt.ly", "rb.gy", "is.gd", "t.co")
BAD_TLD = ("xyz", "top", "click", "buzz", "icu", "live", "shop", "cfd", "sbs", "tk", "ml", "ga", "cf", "gq")
WORDS = ("login", "verify", "secure", "account", "update", "bank", "confirm", "signin", "password", "kyc", "otp", "wallet")

NAMES = ["url_len", "host_len", "path_len", "query_len", "dots", "hyphens", "underscores", "slashes",
         "digits", "digit_ratio", "letters_ratio", "specials", "at_sign", "is_ip", "https", "subdomains",
         "bad_tld", "shortener", "keyword_hits", "entropy", "has_port", "double_slash", "tld_len", "host_digits"]


def _entropy(s):
    if not s:
        return 0.0
    c = {}
    for ch in s:
        c[ch] = c.get(ch, 0) + 1
    n = len(s)
    return -sum(v / n * math.log2(v / n) for v in c.values())


NAMES = ["host_len", "dots", "hyphens", "host_digits", "host_digit_ratio", "is_ip",
         "subdomains", "bad_tld", "shortener", "keyword_hits", "entropy",
         "tld_len", "has_port", "at_sign", "punycode", "longest_label"]

def features(url):
    u = (url or "").strip()
    p = urlparse(u if "://" in u else "http://" + u)
    host = (p.hostname or "").lower()
    parts = host.split(".") if host else []
    tld = parts[-1] if parts else ""
    hd = sum(ch.isdigit() for ch in host)
    return [
        len(host), host.count("."), host.count("-"), hd, hd / max(len(host), 1),
        int(bool(re.fullmatch(r"\d{1,3}(\.\d{1,3}){3}", host))),
        max(len(parts) - 2, 0),
        int(tld in BAD_TLD),
        int(any(host == s or host.endswith("." + s) for s in SHORT)),
        sum(w in host for w in WORDS),          # keywords in the host only
        _entropy(host),
        len(tld), int(p.port is not None), int("@" in u),
        int("xn--" in host),
        max((len(x) for x in parts), default=0),
    ]