import json
import sys

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

path = sys.argv[1] if len(sys.argv) > 1 else "ml/data/emails.csv"
df = pd.read_csv(path)
print("columns:", list(df.columns), "rows:", len(df))

text_col = next((c for c in df.columns if c.lower() in ("text", "body", "email text", "email_text", "message", "content")), None)
label_col = next((c for c in df.columns if c.lower() in ("label", "email type", "email_type", "class", "target", "type")), None)
if len(sys.argv) > 3:
    text_col, label_col = sys.argv[2], sys.argv[3]
if not text_col or not label_col:
    sys.exit("Could not detect columns. Run: python3 -m ml.train_email file.csv TEXT_COLUMN LABEL_COLUMN")
print("text column:", text_col, "| label column:", label_col)


def to_bin(v):
    s = str(v).strip().lower()
    if "phish" in s or "spam" in s or s in ("1", "1.0", "true", "malicious"):
        return 1
    return 0


df = df[[text_col, label_col]].dropna()
df[text_col] = df[text_col].astype(str)
df = df[df[text_col].str.strip().str.len() > 20].drop_duplicates(subset=[text_col])
y = df[label_col].map(to_bin)
print("label mapping check (original -> 0/1):")
print(pd.crosstab(df[label_col].astype(str), y))
print("class balance:", y.value_counts().to_dict())

Xtr, Xte, ytr, yte = train_test_split(df[text_col], y, test_size=0.2, random_state=42, stratify=y)
pipe = Pipeline([
    ("tfidf", TfidfVectorizer(ngram_range=(1, 2), max_features=50000, min_df=2, sublinear_tf=True, stop_words="english")),
    ("clf", LogisticRegression(max_iter=1000, class_weight="balanced")),
])
pipe.fit(Xtr, ytr)
pred = pipe.predict(Xte)
rep = classification_report(yte, pred, output_dict=True)
cm = confusion_matrix(yte, pred).tolist()
print(classification_report(yte, pred, target_names=["legitimate", "phishing"]))
print("confusion matrix [[TN, FP], [FN, TP]]:", cm)

joblib.dump(pipe, "ml/models/email.joblib", compress=3)
try:
    m = json.load(open("ml/models/metrics.json"))
except Exception:
    m = {}
m["email"] = {"train": len(Xtr), "test": len(Xte), "precision": rep["1"]["precision"], "recall": rep["1"]["recall"],
              "f1": rep["1"]["f1-score"], "confusion": cm, "algorithm": "TF-IDF + Logistic Regression"}
json.dump(m, open("ml/models/metrics.json", "w"), indent=2)
print("saved ml/models/email.joblib")
