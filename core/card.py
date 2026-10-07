import io
import textwrap
from PIL import Image, ImageDraw, ImageFont

COLORS = {
    "Verified": (46, 125, 50), "False": (198, 40, 40), "Outdated": (239, 108, 0),
    "Partly supported": (249, 168, 37), "Cannot be confirmed": (117, 117, 117),
}
LABELS = {
    "en": {"Verified": "VERIFIED", "False": "FALSE", "Outdated": "OUTDATED",
           "Partly supported": "PARTLY TRUE", "Cannot be confirmed": "NOT CONFIRMED"},
    "hi": {"Verified": "सत्यापित", "False": "गलत", "Outdated": "पुराना",
           "Partly supported": "आंशिक सही", "Cannot be confirmed": "पुष्टि नहीं"},
    "mr": {"Verified": "पडताळले", "False": "चुकीचे", "Outdated": "कालबाह्य",
           "Partly supported": "अंशतः बरोबर", "Cannot be confirmed": "पुष्टी नाही"},
    "ml": {"Verified": "സ്ഥിരീകരിച്ചു", "False": "തെറ്റ്", "Outdated": "കാലഹരണപ്പെട്ടത്",
           "Partly supported": "ഭാഗികമായി ശരി", "Cannot be confirmed": "സ്ഥിരീകരിച്ചിട്ടില്ല"},
}
FONT = {"hi": "NotoSansDevanagari", "mr": "NotoSansDevanagari", "ml": "NotoSansMalayalam"}


def _font(lang, size):
    for name in (FONT.get(lang, "NotoSans"), "NotoSans"):
        try:
            return ImageFont.truetype(f"data/fonts/{name}.ttf", size)
        except Exception:
            continue
    return ImageFont.load_default()


def _wrap(draw, text, font, width):
    lines, cur = [], ""
    for word in text.split():
        t = (cur + " " + word).strip()
        if draw.textlength(t, font=font) <= width:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def make_card(claim: dict, lang: str) -> bytes:
    lang = lang if lang in LABELS else "en"
    local = lang != "en" and claim.get("explanation_local")
    claim_txt = (claim.get("claim_local") if local and claim.get("claim_local") else claim["text"])
    reason = claim["explanation_local"] if local else claim["explanation_en"]
    sentences = reason.replace("।", ".").split(". ")
    reason = ". ".join(sentences[:2]).strip()
    if not reason.endswith((".", "।")):
        reason += "."
    source = ""
    if claim.get("evidence"):
        e = claim["evidence"][0]
        source = f"{e['source']}" + (f" • {e['date']}" if e.get("date") else "")

    W, pad = 1080, 60
    color = COLORS[claim["label"]]
    img = Image.new("RGB", (W, 1400), "white")
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 190], fill=color)
    d.text((pad, 50), LABELS[lang][claim["label"]], font=_font(lang, 84), fill="white")

    y = 240
    d.text((pad, y), "Claim Lens", font=_font("en", 34), fill=(120, 120, 120))
    y += 70
    for line in _wrap(d, claim_txt, _font(lang, 46), W - 2 * pad)[:5]:
        d.text((pad, y), line, font=_font(lang, 46), fill=(25, 25, 25))
        y += 66
    y += 30
    d.line([pad, y, W - pad, y], fill=(220, 220, 220), width=3)
    y += 40
    for line in _wrap(d, reason, _font(lang, 40), W - 2 * pad)[:8]:
        d.text((pad, y), line, font=_font(lang, 40), fill=(60, 60, 60))
        y += 60
    y += 30
    if source:
        d.text((pad, y), "Source: " + source, font=_font("en", 34), fill=(90, 90, 90))
        y += 60
    d.text((pad, y + 30), "Checked with Claim Lens • Verify before you forward",
           font=_font("en", 30), fill=(150, 150, 150))
    img = img.crop((0, 0, W, min(1400, y + 130)))
    buf = io.BytesIO()
    img.save(buf, "PNG")
    return buf.getvalue()
