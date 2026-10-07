import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
FACTCHECK_API_KEY = os.getenv("FACTCHECK_API_KEY")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_FROM = os.getenv("TWILIO_WHATSAPP_FROM")
PUBLIC_URL = os.getenv("PUBLIC_URL", "").rstrip("/")
VALIDATE_TWILIO = os.getenv("VALIDATE_TWILIO", "0") == "1"

with open("data/allowlist.txt") as f:
    ALLOWLIST = [l.strip() for l in f if l.strip()]

LABELS = ["Verified", "False", "Outdated", "Partly supported", "Cannot be confirmed"]

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

LLM_PRIMARY = os.getenv("LLM_PRIMARY", "groq")

GEMINI_MODELS = [m.strip() for m in os.getenv("GEMINI_MODELS", GEMINI_MODEL).split(",") if m.strip()]

GROQ_MODELS = [m.strip() for m in os.getenv("GROQ_MODELS", GROQ_MODEL).split(",") if m.strip()]

LANG_NAMES = {
    "en": "English", "hi": "Hindi", "mr": "Marathi", "ml": "Malayalam",
    "ta": "Tamil", "te": "Telugu", "bn": "Bengali", "gu": "Gujarati", "kn": "Kannada",
}

META_ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")
META_PHONE_NUMBER_ID = os.getenv("META_PHONE_NUMBER_ID")
META_VERIFY_TOKEN = os.getenv("META_VERIFY_TOKEN", "claimlens123")
