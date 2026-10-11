"""Train the email/message phishing model on emails.csv + the Indian synthetic set.

Run from the project root:
    python3 -W ignore -m ml.train_email_v2
Optional: python3 -W ignore -m ml.train_email_v2 --fast   (uses 20k of the big emails, for a quick test)
"""
import json
import sys

import joblib
import pandas as pd
from scipy.sparse import hstack
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.pipeline import FeatureUnion, Pipeline

MAXC = 2000          # characters kept per email (speed)
SYN_WEIGHT = 15      # the 549 Indian rows are tiny next to 82k emails, so weight them up
FAST = "--fast" in sys.argv

# ---- 1. big English email set ----
big = pd.read_csv("ml/data/emails.csv")[["text_combined", "label"]].dropna()
big.columns = ["text", "label"]
big["text"] = big["text"].astype(str)
big = big[big["text"].str.len() > 20].drop_duplicates("text")
big["label"] = big["label"].astype(int)
if FAST:
    big = big.sample(20000, random_state=1)
big["src"] = "big"

# ---- 2. Indian synthetic set ----
syn = pd.read_csv("ml/data/indian_emails.csv")
syn["label"] = (syn["label"] == "phishing").astype(int)
syn["src"] = "syn"

# Hold out whole scam/genuine TYPES from the synthetic set. The model never sees these
# kinds of message in training, so this tests generalisation, not memorised templates.
HOLD = {"courier", "reward", "statement", "webinar", "credit", "sim"}
syn_hold = syn[syn["type"].isin(HOLD)]
syn_train = syn[~syn["type"].isin(HOLD)]

big_tr, big_te = train_test_split(big, test_size=0.2, random_state=42, stratify=big["label"])
train = pd.concat([big_tr, syn_train], ignore_index=True)
w = train["src"].map({"big": 1.0, "syn": float(SYN_WEIGHT)}).values
print(f"train: {len(big_tr)} big + {len(syn_train)} synthetic | held-out: {len(big_te)} big, {len(syn_hold)} synthetic (unseen types)")

pipe = Pipeline([
    ("tfidf", FeatureUnion([
        ("word", TfidfVectorizer(ngram_range=(1, 2), max_features=60000, min_df=2, sublinear_tf=True, stop_words="english")),
        ("char", TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), max_features=120000, min_df=3, sublinear_tf=True)),
    ])),
    ("clf", LogisticRegression(max_iter=1000, class_weight="balanced")),
])
pipe.fit(train["text"].str[:MAXC], train["label"], clf__sample_weight=w)


def report(name, df):
    pred = pipe.predict(df["text"].str[:MAXC])
    rep = classification_report(df["label"], pred, output_dict=True, zero_division=0)
    cm = confusion_matrix(df["label"], pred).tolist()
    print(f"\n== {name}  (n={len(df)})")
    print(classification_report(df["label"], pred, target_names=["legitimate", "phishing"], zero_division=0))
    print("confusion [[TN, FP], [FN, TP]]:", cm)
    return {"n": len(df), "precision": rep["1"]["precision"], "recall": rep["1"]["recall"], "f1": rep["1"]["f1-score"], "confusion": cm}


m_big = report("held-out big emails (English)", big_te)
m_syn = report("held-out Indian synthetic (UNSEEN types)", syn_hold)
for lang in ["en", "hinglish", "hi", "mr"]:
    sub = syn_hold[syn_hold["language"] == lang]
    if len(sub) > 5 and sub["label"].nunique() == 2:
        report(f"  unseen types, language={lang}", sub)

joblib.dump(pipe, "ml/models/email.joblib", compress=3)
try:
    m = json.load(open("ml/models/metrics.json"))
except Exception:
    m = {}
m["email"] = {"algorithm": "TF-IDF (word + char n-grams) + Logistic Regression",
              "train": len(train), "big_heldout": m_big, "indian_unseen_types": m_syn,
              "note": "Indian set is synthetic; no real-world test set yet"}
json.dump(m, open("ml/models/metrics.json", "w"), indent=2)
print("\nsaved ml/models/email.joblib")