"""URL phishing model (from PhishGuard) wrapped for ClaimLens.
Fails soft: if the model or a library is missing, functions return None and
the rest of ClaimLens keeps working."""
import os
from concurrent.futures import ThreadPoolExecutor

_DIR = os.path.dirname(os.path.abspath(__file__))
_MODEL_PATH = os.path.join(_DIR, "model", "phishing_model.pkl")
_model = None
_fx = None
_err = None


def _load():
    global _model, _fx, _err
    if _model is not None or _err is not None:
        return
    try:
        import joblib
        from . import feature_extractor as fx
        m = joblib.load(_MODEL_PATH)["model"]
        m.n_jobs = 1  # single URL per call: threads only add overhead
        _model, _fx = m, fx
    except Exception as e:  # noqa: BLE001
        _err = f"{type(e).__name__}: {e}"


def status():
    _load()
    return {"available": _model is not None, "error": _err}


def scan_url(url):
    """-> {'label','phishing_probability'(0-1),'domain','typosquat','matched_words'} or None."""
    _load()
    if _model is None:
        return None
    import numpy as np
    url = (url or "").strip()
    feats = _fx.extract_features_detail(url)
    vec = np.array([[feats[n] for n in _fx.FEATURE_NAMES]], dtype=float)
    p = 1.0 - float(_model.predict_proba(vec)[0][1])  # class 1 = legitimate
    squat = bool(feats.get("IsTyposquatSuspected")) and not bool(feats.get("IsBrandExactMatch"))
    if squat:
        p = max(p, 0.93)  # same safety net PhishGuard uses
    return {
        "url": url,
        "label": "phishing" if p >= 0.5 else "legitimate",
        "phishing_probability": round(p, 3),
        "domain": feats["_domain"],
        "typosquat": squat,
        "matched_words": feats["_matched_suspicious_words"],
    }


def enrich(url):
    """ML verdict + VirusTotal + WHOIS + DNS combined (slow: seconds). None if model unavailable."""
    ml = scan_url(url)
    if ml is None:
        return None
    from . import enrichment, holistic
    key = os.getenv("VIRUSTOTAL_API_KEY", "")
    with ThreadPoolExecutor(max_workers=3) as ex:
        f_vt = ex.submit(enrichment.get_virustotal_report, url, key)
        f_wh = ex.submit(enrichment.get_whois_info, ml["domain"])
        f_dn = ex.submit(enrichment.get_dns_info, ml["domain"])
        vt, wh, dn = f_vt.result(), f_wh.result(), f_dn.result()
    h = holistic.compute_holistic(
        ml_proba_phish=ml["phishing_probability"], typosquat_suspected=ml["typosquat"],
        vt_info=vt, whois_info=wh, dns_info=dn)
    return {"ml": ml, "virustotal": vt, "whois": wh, "dns": dn, "holistic": h}