"""The phishing email model (from the Phishing-email-detection project).

TF-IDF + Logistic Regression, trained by:  python3 -W ignore -m ml.train_phishing_email
Files: ml/models/phishing_model.pkl and ml/models/vectorizer.pkl
"""
import os

import joblib

_model = _vec = None


def _load():
    global _model, _vec
    if _model is None and os.path.exists("ml/models/phishing_model.pkl") \
            and os.path.exists("ml/models/vectorizer.pkl"):
        _model = joblib.load("ml/models/phishing_model.pkl")
        _vec = joblib.load("ml/models/vectorizer.pkl")


def predict_email(text):
    """Return {'label': 'phishing' | 'safe', 'probability': 0-1}, or None if not trained."""
    _load()
    if _model is None:
        return None
    p = float(_model.predict_proba(_vec.transform([text]))[0][1])
    return {"label": "phishing" if p >= 0.5 else "safe", "probability": round(p, 3)}


_m3 = None


def _load3():
    global _m3
    if _m3 is None and os.path.exists("ml/models/email3.pkl"):
        _m3 = joblib.load("ml/models/email3.pkl")


def predict_email3(sender="", subject="", body="", links=None):
    """3-class model: {'label': safe|marketing|phishing|unsure, 'probs': {...}, 'confidence': 0-1}.

    Returns None if ml/models/email3.pkl is missing (train with: python3 -W ignore -m ml.train_email3).
    'unsure' means the top class got less than 50%, so we do not pretend to know.
    """
    _load3()
    if _m3 is None:
        return None
    import numpy as np
    import scipy.sparse as sp
    from ml.emailfeatures import extract
    text, num = extract(sender, subject, body, links or [])
    X = sp.hstack([_m3["vec"].transform([text]), sp.csr_matrix(_m3["scaler"].transform(np.array([num])) * 2.0)]).tocsr()
    pr = _m3["clf"].predict_proba(X)[0]
    probs = {c: round(float(p), 3) for c, p in zip(_m3["classes"], pr)}
    top = max(probs, key=probs.get)
    return {"label": top if probs[top] >= 0.5 else "unsure", "probs": probs, "confidence": probs[top]}
