import json
import sys

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import train_test_split

from ml.features import features, NAMES

if len(sys.argv) > 1:
    df = pd.read_csv(sys.argv[1])
else:
    from ucimlrepo import fetch_ucirepo
    d = fetch_ucirepo(id=967)
    df = d.data.features.copy()
    df["label"] = d.data.targets.iloc[:, 0].values

url_col = next(c for c in df.columns if c.lower() == "url")
df = df[[url_col, "label"]].dropna().drop_duplicates(subset=[url_col])
print("rows:", len(df), "| label counts:", df["label"].value_counts().to_dict())

# PhiUSIIL documents 1 = legitimate, 0 = phishing. We store phishing = 1.
y = (df["label"] == 0).astype(int)
print("phishing share:", round(float(y.mean()), 3), "(PhiUSIIL should be roughly 0.43)")

X = pd.DataFrame([features(u) for u in df[url_col]], columns=NAMES)
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
rf = RandomForestClassifier(n_estimators=100, max_depth=20, min_samples_leaf=3, n_jobs=-1, class_weight="balanced", random_state=42)
rf.fit(Xtr, ytr)
pred = rf.predict(Xte)
rep = classification_report(yte, pred, output_dict=True)
cm = confusion_matrix(yte, pred).tolist()
print(classification_report(yte, pred, target_names=["legitimate", "phishing"]))
print("confusion matrix [[TN, FP], [FN, TP]]:", cm)
imp = sorted(zip(NAMES, rf.feature_importances_), key=lambda t: -t[1])[:8]
print("top features:", [(n, round(float(v), 3)) for n, v in imp])

joblib.dump({"model": rf, "names": NAMES}, "ml/models/url.joblib", compress=3)
try:
    m = json.load(open("ml/models/metrics.json"))
except Exception:
    m = {}
m["url"] = {"train": len(Xtr), "test": len(Xte), "precision": rep["1"]["precision"], "recall": rep["1"]["recall"],
            "f1": rep["1"]["f1-score"], "confusion": cm, "algorithm": "Random Forest (URL-string features)",
            "top_features": [[n, float(v)] for n, v in imp]}
json.dump(m, open("ml/models/metrics.json", "w"), indent=2)
print("saved ml/models/url.joblib")
