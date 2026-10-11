import os

import joblib

from ml.features import features

_email = _url = None


def _load():
    global _email, _url
    if _email is None and os.path.exists("ml/models/email.joblib"):
        _email = joblib.load("ml/models/email.joblib")
    if _url is None and os.path.exists("ml/models/url.joblib"):
        _url = joblib.load("ml/models/url.joblib")


def predict_email(text):
    _load()
    if _email is None:
        return None
    tf, clf = _email.named_steps["tfidf"], _email.named_steps["clf"]
    x = tf.transform([text])
    p = float(clf.predict_proba(x)[0][1])
    names = tf.get_feature_names_out()
    contrib = []
    row = x.tocoo()
    for j, v in zip(row.col, row.data):
        n = str(names[j])
        if n.startswith("char__"):
            continue            # character n-grams are not readable; explain with words only
        if n.replace("word__", "").split(" ")[0] in {"com", "www", "http", "https", "net", "org", "html"}:
            continue            # generic URL pieces say nothing to a reader
        contrib.append((n.replace("word__", ""), float(v * clf.coef_[0][j])))
    contrib.sort(key=lambda t: -t[1])
    return {"label": "phishing" if p >= 0.5 else "legitimate", "probability": round(p, 3),
            "pushed_toward_phishing": [w for w, c in contrib[:6] if c > 0],
            "pushed_toward_legitimate": [w for w, c in contrib[::-1][:4] if c < 0]}


def predict_url(url):
    _load()
    if _url is None:
        return None
    rf, names = _url["model"], _url["names"]
    f = features(url)
    p = float(rf.predict_proba([f])[0][1])
    imp = sorted(zip(names, rf.feature_importances_, f), key=lambda t: -t[1])[:5]
    return {"label": "phishing" if p >= 0.5 else "legitimate", "probability": round(p, 3),
            "key_signals": [{"feature": n, "value": round(float(v), 3)} for n, _, v in imp]}