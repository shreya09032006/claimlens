"""Train the phishing email model from the Phishing-email-detection project.

Original project: https://github.com/Lalitkumar21/Phishing-email-detection
Original dataset: https://huggingface.co/datasets/zefang-liu/phishing-email-dataset
The pipeline below is the one from that project's model-training.ipynb (TF-IDF with
5000 features and English stop words, then Logistic Regression, 80/20 split with
random_state=20). Only the file paths and the metrics export are new.

Run from the Claim Lens project root:
    python3 -W ignore -m ml.train_phishing_email
    python3 -W ignore -m ml.train_phishing_email path/to/Phishing_Email.csv
"""
import json
import sys

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split

CSV = sys.argv[1] if len(sys.argv) > 1 else "ml/data/Phishing_Email.csv"

df = pd.read_csv(CSV).dropna(subset=["Email Text"])
y = (df["Email Type"] == "Phishing Email").astype(int)        # 1 = phishing, 0 = safe
x_train, x_test, y_train, y_test = train_test_split(
    df["Email Text"], y, test_size=0.2, random_state=20)

vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)
model = LogisticRegression()
model.fit(vectorizer.fit_transform(x_train), y_train)

pred = model.predict(vectorizer.transform(x_test))
print("Accuracy:", round(accuracy_score(y_test, pred), 4))
print(classification_report(y_test, pred, target_names=["safe", "phishing"]))
print("confusion [[TN, FP], [FN, TP]]:", confusion_matrix(y_test, pred).tolist())

joblib.dump(model, "ml/models/phishing_model.pkl")
joblib.dump(vectorizer, "ml/models/vectorizer.pkl")

rep = classification_report(y_test, pred, output_dict=True)
try:
    metrics = json.load(open("ml/models/metrics.json"))
except Exception:
    metrics = {}
metrics["email_phishing_lr"] = {
    "algorithm": "TF-IDF (5000 words) + Logistic Regression",
    "source": "github.com/Lalitkumar21/Phishing-email-detection; dataset zefang-liu/phishing-email-dataset",
    "train": len(x_train), "test": len(x_test),
    "accuracy": round(accuracy_score(y_test, pred), 4),
    "precision": round(rep["1"]["precision"], 4), "recall": round(rep["1"]["recall"], 4),
    "f1": round(rep["1"]["f1-score"], 4),
    "confusion": confusion_matrix(y_test, pred).tolist(),
}
json.dump(metrics, open("ml/models/metrics.json", "w"), indent=2)
print("\nsaved ml/models/phishing_model.pkl and ml/models/vectorizer.pkl")