# 3-class email model (safe / marketing / phishing) - update for Claim Lens

Unzip over your project root (it overwrites the files below), then:

    python3 -W ignore -m ml.train_email3      # retrain any time
    # restart the server, then reload the Chrome extension

New:      ml/emailfeatures.py  ml/seed_data.py  ml/holdout.py  ml/train_email3.py  core/risk.py  ml/models/email3.pkl
Changed:  core/mlmodels.py (predict_email3)  core/emailcheck.py (brand false-positive fix)
          app/emailpage.py (/api/email-lite now uses sender + links + 3 classes + rules)
          extension/content.js (shows MARKETING / SUSPICIOUS / NOT SURE + reasons)
Do NOT apply wire_ml.patch: it imports core.risk.combine with a different signature and is out of date.

## Make it accurate on YOUR mail (important)
The built-in training data is a synthetic seed, so the reported score is only a smoke test.
Add real labelled mail (Gmail: open mail -> Show original -> save as .eml) to:
    ml/data/modern/safe/   ml/data/modern/marketing/   ml/data/modern/phishing/
Aim for 100+ per class, then re-run ml.train_email3. With 30+ real mails it holds out 25%
and prints a real test score. Real mail is weighted x5 over the seed.
