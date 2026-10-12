# Credits

## Phishing email model
The phishing-email classifier (TF-IDF + Logistic Regression) and its Streamlit demo come from
**Phishing-email-detection** by Lalitkumar21: https://github.com/Lalitkumar21/Phishing-email-detection
(`ml/train_phishing_email.py` and `ml/demo_streamlit.py` are based on that project's
`model-training.ipynb` and `testing_model.py`).

## Dataset
`ml/data/Phishing_Email.csv` is the **zefang-liu/phishing-email-dataset** from Hugging Face:
https://huggingface.co/datasets/zefang-liu/phishing-email-dataset
Check the dataset page for its licence before redistributing it.

## Claim Lens
The Gmail extension, fact-checking pipeline, scam red-flag scanner, sender verification
(SPF / DKIM / DMARC) and the combined verdict are part of this project.