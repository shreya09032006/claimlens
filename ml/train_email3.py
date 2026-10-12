"""Train the 3-class email model: safe / marketing / phishing.

Run from the project root:   python3 -W ignore -m ml.train_email3

Training data (all optional except the seed, which is built in):
  1. ml/seed_data.py                      synthetic modern seed (bootstrap only)
  2. ml/data/modern/safe|marketing|phishing/*.eml|*.txt   YOUR real labelled emails  (weighted x5)
  3. ml/data/Phishing_Email.csv           old dataset: only its 'Safe Email' rows are used,
                                          a small sample, as plain business mail (the old
                                          'Phishing' rows are 2000s spam and are NOT used)

Evaluation: a hand-written holdout (ml/holdout.py) and, if you add real mail, a stratified
split of your own mail. The synthetic seed itself is never used for the reported score.
"""
import email
import glob
import json
import os
import sys
from email import policy
from email.utils import parseaddr
from html.parser import HTMLParser

import joblib
import numpy as np
import pandas as pd
import scipy.sparse as sp
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MaxAbsScaler

from ml.emailfeatures import extract
from ml.holdout import HOLDOUT
from ml.seed_data import generate

CLASSES = ["safe", "marketing", "phishing"]
LEGACY_SAFE = int(os.environ.get("LEGACY_SAFE", 1500))


class _L(HTMLParser):
    def __init__(self):
        super().__init__(); self.links, self._h, self._t = [], None, ""
    def handle_starttag(self, tag, a):
        if tag == "a": self._h, self._t = dict(a).get("href"), ""
    def handle_data(self, d):
        if self._h is not None: self._t += d
    def handle_endtag(self, tag):
        if tag == "a" and self._h is not None: self.links.append({"href": self._h, "text": self._t.strip()}); self._h = None


def load_dir(root="ml/data/modern"):
    out = []
    for lab in CLASSES:
        for f in glob.glob(f"{root}/{lab}/*"):
            try:
                if f.endswith(".eml"):
                    m = email.message_from_bytes(open(f, "rb").read(), policy=policy.default)
                    b = m.get_body(preferencelist=("html", "plain")); c = b.get_content() if b else ""
                    p = _L(); p.feed(c)
                    import re
                    body = re.sub(r"<[^>]+>", " ", c)
                    out.append(dict(sender=parseaddr(str(m.get("From", "")))[1], subject=str(m.get("Subject", "")),
                                    body=body[:6000], links=p.links, label=lab))
                else:
                    out.append(dict(sender="", subject="", body=open(f, errors="ignore").read()[:6000], links=[], label=lab))
            except Exception as e:
                print("skip", f, e)
    return out


def legacy_safe():
    p = "ml/data/Phishing_Email.csv"
    if not os.path.exists(p) or LEGACY_SAFE <= 0:
        return []
    df = pd.read_csv(p).dropna(subset=["Email Text"])
    df = df[df["Email Type"] == "Safe Email"]
    df = df[df["Email Text"].str.len().between(80, 3000)].sample(min(LEGACY_SAFE, len(df)), random_state=1)
    return [dict(sender="", subject="", body=t, links=[], label="safe") for t in df["Email Text"]]


def featurize(rows):
    T, N = zip(*[extract(r["sender"], r["subject"], r["body"], r["links"]) for r in rows])
    return list(T), np.array(N)


def fit(rows, w):
    T, N = featurize(rows)
    vec = TfidfVectorizer(stop_words="english", ngram_range=(1, 2), max_features=4000, min_df=2, sublinear_tf=True)
    sc = MaxAbsScaler()
    X = sp.hstack([vec.fit_transform(T), sp.csr_matrix(sc.fit_transform(N) * 2.0)]).tocsr()
    clf = LogisticRegression(max_iter=2000, C=3.0, class_weight="balanced")
    clf.fit(X, [r["label"] for r in rows], sample_weight=w)
    return vec, sc, clf


def predict(model, rows):
    vec, sc, clf = model
    T, N = featurize(rows)
    X = sp.hstack([vec.transform(T), sp.csr_matrix(sc.transform(N) * 2.0)]).tocsr()
    return clf.predict(X), clf.predict_proba(X)


def report(name, y, p):
    print(f"\n== {name} ({len(y)} emails) ==")
    print(classification_report(y, p, labels=CLASSES, zero_division=0))
    print("confusion (rows=true, cols=pred)", CLASSES); print(confusion_matrix(y, p, labels=CLASSES))
    return float((np.array(y) == np.array(p)).mean())


if __name__ == "__main__":
    seed = generate(500)
    real = load_dir()
    leg = legacy_safe()
    print(f"seed={len(seed)}  your real mail={len(real)}  legacy safe={len(leg)}")
    real_test = []
    if len(real) >= 30:
        real_tr, real_test = train_test_split(real, test_size=0.25, random_state=3, stratify=[r["label"] for r in real])
    else:
        real_tr = real
    rows = seed + leg + real_tr
    w = [1.0] * (len(seed) + len(leg)) + [5.0] * len(real_tr)
    model = fit(rows, w)

    hp, _ = predict(model, HOLDOUT)
    acc_h = report("hand-written holdout", [r["label"] for r in HOLDOUT], hp)
    metrics = {"model": "TF-IDF(1-2gram) + 27 structural features + multinomial LR, 3 classes",
               "train_rows": len(rows), "your_real_rows": len(real), "holdout_accuracy": round(acc_h, 4)}
    if real_test:
        rp, _ = predict(model, real_test)
        metrics["real_test_accuracy"] = round(report("YOUR real mail (held out)", [r["label"] for r in real_test], rp), 4)
    else:
        print("\nNo real mail found in ml/data/modern/. Scores above come from a 24-mail hand-written set only;")
        print("add your own labelled .eml/.txt files and re-run to get a trustworthy number.")

    joblib.dump({"vec": model[0], "scaler": model[1], "clf": model[2], "classes": list(model[2].classes_)}, "ml/models/email3.pkl")
    try:
        allm = json.load(open("ml/models/metrics.json"))
    except Exception:
        allm = {}
    allm["email_3class"] = metrics
    json.dump(allm, open("ml/models/metrics.json", "w"), indent=2)
    print("\nsaved ml/models/email3.pkl")
