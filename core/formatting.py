import os

SHOW_ENGLISH = os.getenv("SHOW_ENGLISH", "1") == "1"

EMOJI = {
    "Verified": "", "False": "", "Outdated": "",
    "Partly supported": "", "Cannot be confirmed": "",
}

EN = {
    "claim": "Claim", "evidence": "Evidence", "conf": "confident",
    "labels": {"Verified": "Verified", "False": "False", "Outdated": "Outdated",
               "Partly supported": "Partly supported", "Cannot be confirmed": "Cannot be confirmed"},
}
T = {
    "en": EN,
    "hi": {"claim": "दावा", "evidence": "प्रमाण", "conf": "विश्वास",
           "labels": {"Verified": "सत्यापित", "False": "गलत", "Outdated": "पुराना",
                      "Partly supported": "आंशिक रूप से सही", "Cannot be confirmed": "पुष्टि नहीं हो सकी"}},
    "mr": {"claim": "दावा", "evidence": "पुरावा", "conf": "खात्री",
           "labels": {"Verified": "पडताळले", "False": "चुकीचे", "Outdated": "कालबाह्य",
                      "Partly supported": "अंशतः बरोबर", "Cannot be confirmed": "पुष्टी करता आली नाही"}},
    "ml": {"claim": "അവകാശവാദം", "evidence": "തെളിവ്", "conf": "ഉറപ്പ്",
           "labels": {"Verified": "സ്ഥിരീകരിച്ചു", "False": "തെറ്റ്", "Outdated": "കാലഹരണപ്പെട്ടത്",
                      "Partly supported": "ഭാഗികമായി ശരി", "Cannot be confirmed": "സ്ഥിരീകരിക്കാനായില്ല"}},
}


def _conf(c, t):
    if c["label"] == "Cannot be confirmed":
        return ""
    return f" ({int(c['confidence'] * 100)}% {t['conf']})"


def format_whatsapp(result: dict):
    if not result["claims"]:
        return ["I couldn't find a factual claim to check in this message. Forward a message that states something as fact."]
    lang = result.get("target_language", "en")
    t = T.get(lang, EN)
    local = lang != "en" and lang in T
    msgs = []
    for i, c in enumerate(result["claims"], 1):
        emoji = EMOJI[c["label"]]
        if local and c.get("explanation_local"):
            claim_txt = c.get("claim_local") or c["text"]
            m = (f"{emoji} *{t['labels'][c['label']]}*{_conf(c, t)}\n"
                 f"_{t['claim']} {i}:_ {claim_txt}\n\n{c['explanation_local']}")
            msgs.append(m[:1500])
            if SHOW_ENGLISH:
                msgs.append((f" *{c['label']}* — {c['text']}\n\n{c['explanation_en']}")[:1500])
        else:
            m = (f"{emoji} *{c['label']}*{_conf(c, EN)}\n"
                 f"_Claim {i}:_ {c['text']}\n\n{c['explanation_en']}")
            if c.get("explanation_local"):
                m += f"\n\n{c['explanation_local']}"
            msgs.append(m[:1500])
        if c["evidence"] and c["label"] != "Cannot be confirmed":
            ev = "\n\n".join(
                f" \"{e['quote']}\"\n{e['source']} • {e['date'] or '—'}\n{e['url']}"
                for e in c["evidence"]
            )
            msgs.append((f"*{t['evidence']}*\n" + ev)[:1500])
    return msgs
