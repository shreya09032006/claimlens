import re

RULES = [
    (r"\b(otp|cvv|pin|password)\b", "Asks for an OTP, PIN or password"),
    (r"(kyc|account.{0,12}(blocked|suspended|closed)|sim.{0,12}(blocked|deactivat))", "Threatens to block your account or SIM"),
    (r"(free|cashback|prize|lottery|won|reward|gift).{0,40}(rs\.?|₹|rupees|lakh|crore|\d{3,})|(rs\.?|₹)\s?\d[\d,]*.{0,40}(free|cashback|prize|reward)", "Promises free money or a prize"),
    (r"(share|forward).{0,40}(\d+|ten|everyone|friends|groups)", "Pressures you to forward it to many people"),
    (r"(within \d+ (hours|minutes)|last date|expires|urgent|immediately|hurry|limited time|today only)", "Creates false urgency"),
    (r"(registration fee|processing fee|security deposit|pay.{0,30}(job|loan|offer|claim))", "Asks you to pay a fee for a job, loan or offer"),
    (r"(bit\.ly|tinyurl|cutt\.ly|is\.gd|rb\.gy|wa\.link|t\.co/)", "Uses a shortened link that hides the real site"),
    (r"https?://[^\s]*\.(xyz|top|click|buzz|icu|live|shop|cfd|sbs)\b", "Link on a domain type often used by scams"),
    (r"(\.apk\b|install.{0,30}\bapp\b|download.{0,30}\bapp\b)", "Asks you to install an app or APK"),
    (r"((call|whatsapp|contact).{0,50}[6-9]\d{9}|[6-9]\d{9}.{0,50}(call|whatsapp|contact))", "Pushes you to contact an unknown number"),
    (r"(government|govt|rbi|sbi|pm modi|trai|income tax).{0,60}(free|scheme|giving|offer)", "Claims to be an official scheme; check the official website"),
]


def scan(text: str) -> dict:
    t = (text or "").lower()
    flags = [msg for pat, msg in RULES if re.search(pat, t)]
    level = "high" if len(flags) >= 3 else "medium" if len(flags) == 2 else "low"
    return {"level": level, "flags": flags}
