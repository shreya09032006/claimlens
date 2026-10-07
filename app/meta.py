import asyncio
import httpx
from fastapi import APIRouter, Request, BackgroundTasks, Response

from core import config
from core.pipeline import check_text
from core.formatting import format_whatsapp
from core.ingest import file_to_text, find_url, url_to_text
from core.audio import speak
from core import ledger
from core.card import make_card

router = APIRouter()
GRAPH = "https://graph.facebook.com/v21.0"
_seen = set()
_FWD_WARN = {
    "en": "🚨 This message has been forwarded many times and it is *{label}*. Please do NOT forward it. Share the card below in your group instead.",
    "hi": "🚨 यह संदेश कई बार फॉरवर्ड हुआ है और यह *{label}* है। कृपया इसे आगे न भेजें। इसके बजाय नीचे का कार्ड अपने ग्रुप में डालें।",
    "mr": "🚨 हा संदेश अनेकदा फॉरवर्ड झाला आहे आणि तो *{label}* आहे. कृपया हा पुढे पाठवू नका. त्याऐवजी खालील कार्ड तुमच्या ग्रुपमध्ये टाका.",
    "ml": "🚨 ഈ സന്ദേശം പലതവണ ഫോർവേഡ് ചെയ്യപ്പെട്ടു, ഇത് *{label}* ആണ്. ദയവായി ഫോർവേഡ് ചെയ്യരുത്. പകരം താഴെയുള്ള കാർഡ് ഗ്രൂപ്പിൽ പങ്കിടുക.",
}
import json, os
_PREFS_FILE = "data/prefs.json"


def _load_prefs():
    try:
        d = json.load(open(_PREFS_FILE))
        return d.get("lang", {}), set(d.get("voice_off", []))
    except Exception:
        return {}, set()


import re as _re

_VOICE_OFF = ("voice off", "audio off", "no voice")
_VOICE_ON = ("voice on", "audio on")


def _split_cmds(body: str):
    """Pull commands off the start or end of a message. Returns (remaining_text, [commands])."""
    text = body.strip()
    cmds = []
    names = list(_VOICE_OFF) + list(_VOICE_ON) + list(_LANG_CMDS.keys())
    names.sort(key=len, reverse=True)
    changed = True
    while changed and text:
        changed = False
        for n in names:
            pat_end = _re.compile(r"(?:^|[\s.,;:!?\-]+)" + _re.escape(n) + r"[\s.!?]*$", _re.IGNORECASE)
            pat_start = _re.compile(r"^[\s]*" + _re.escape(n) + r"(?:[\s.,;:!?\-]+|$)", _re.IGNORECASE)
            m = pat_end.search(text)
            if m:
                cmds.append(n.lower())
                text = text[:m.start()].strip()
                changed = True
                break
            m = pat_start.match(text)
            if m:
                cmds.append(n.lower())
                text = text[m.end():].strip()
                changed = True
                break
    return text, cmds


_pref, _voice_off = _load_prefs()


def _save_prefs():
    try:
        json.dump({"lang": _pref, "voice_off": sorted(_voice_off)}, open(_PREFS_FILE, "w"))
    except Exception as e:
        print("prefs save error:", e)
_LANG_CMDS = {
    "marathi": "mr", "मराठी": "mr", "hindi": "hi", "हिन्दी": "hi", "हिंदी": "hi",
    "malayalam": "ml", "മലയാളം": "ml", "english": "en", "auto": "auto", "guardian on": "g_on", "guardian off": "g_off",
}


def _headers():
    return {"Authorization": f"Bearer {config.META_ACCESS_TOKEN}"}


async def _send(to: str, text: str):
    async with httpx.AsyncClient(timeout=20) as c:
        r = await c.post(
            f"{GRAPH}/{config.META_PHONE_NUMBER_ID}/messages",
            headers=_headers(),
            json={"messaging_product": "whatsapp", "to": to, "type": "text",
                  "text": {"body": text, "preview_url": False}},
        )
        if r.status_code >= 400:
            print("meta send error:", r.status_code, r.text[:300])



async def _send_audio(to: str, text: str, lang: str):
    try:
        mp3 = await speak(text, lang)
        async with httpx.AsyncClient(timeout=40) as c:
            up = await c.post(
                f"{GRAPH}/{config.META_PHONE_NUMBER_ID}/media",
                headers=_headers(),
                data={"messaging_product": "whatsapp", "type": "audio/mpeg"},
                files={"file": ("verdict.mp3", mp3, "audio/mpeg")},
            )
            if up.status_code >= 400:
                print("media upload error:", up.status_code, up.text[:200])
                return
            mid = up.json()["id"]
            r = await c.post(
                f"{GRAPH}/{config.META_PHONE_NUMBER_ID}/messages",
                headers=_headers(),
                json={"messaging_product": "whatsapp", "to": to, "type": "audio", "audio": {"id": mid}},
            )
            if r.status_code >= 400:
                print("audio send error:", r.status_code, r.text[:200])
    except Exception as e:
        print("audio error:", e)



async def _send_card(to: str, claim: dict, lang: str):
    try:
        png = await asyncio.to_thread(make_card, claim, lang)
        async with httpx.AsyncClient(timeout=40) as c:
            up = await c.post(
                f"{GRAPH}/{config.META_PHONE_NUMBER_ID}/media",
                headers=_headers(),
                data={"messaging_product": "whatsapp", "type": "image/png"},
                files={"file": ("card.png", png, "image/png")},
            )
            if up.status_code >= 400:
                print("card upload error:", up.status_code, up.text[:200])
                return
            r = await c.post(
                f"{GRAPH}/{config.META_PHONE_NUMBER_ID}/messages",
                headers=_headers(),
                json={"messaging_product": "whatsapp", "to": to, "type": "image",
                      "image": {"id": up.json()["id"], "caption": "📤 Share this in your group"}},
            )
            if r.status_code >= 400:
                print("card send error:", r.status_code, r.text[:200])
    except Exception as e:
        print("card error:", e)



_last = {}
QUEUE = "data/human_queue.json"


async def _send_human_button(to: str):
    async with httpx.AsyncClient(timeout=20) as c:
        r = await c.post(
            f"{GRAPH}/{config.META_PHONE_NUMBER_ID}/messages",
            headers=_headers(),
            json={"messaging_product": "whatsapp", "to": to, "type": "interactive",
                  "interactive": {"type": "button",
                                  "body": {"text": "Want a human fact-checker to look at this?"},
                                  "action": {"buttons": [{"type": "reply",
                                                          "reply": {"id": "human", "title": "Ask a human"}}]}}},
        )
        if r.status_code >= 400:
            print("button error:", r.status_code, r.text[:200])


async def _human_request(to: str):
    import time
    try:
        q = json.load(open(QUEUE))
    except Exception:
        q = []
    q.append({"who": "…" + to[-4:], "text": _last.get(to, ""), "ts": int(time.time())})
    json.dump(q, open(QUEUE, "w"))
    await _send(to, "👤 Request logged for human review. You can also send it to a fact-checking tipline: "
                + os.getenv("TIPLINE_URL", "https://www.boomlive.in/"))


GUARD_FILE = "data/guardians.json"


def _guardians():
    try:
        return json.load(open(GUARD_FILE))
    except Exception:
        return []


async def _guardian_alert(label, claim, n, exclude=None):
    for g in _guardians():
        if g != exclude:
            await _send(g, f"🛡️ *Guardian alert*\nA claim already marked *{label}* has now been checked {n} times:\n\"{claim[:200]}\"\nIf it is in your family group, post the correction there.")


async def _download(media_id: str):
    async with httpx.AsyncClient(timeout=40) as c:
        info = await c.get(f"{GRAPH}/{media_id}", headers=_headers())
        info.raise_for_status()
        j = info.json()
        f = await c.get(j["url"], headers=_headers())
        f.raise_for_status()
        return f.content, j.get("mime_type", "application/octet-stream")


async def _process(to: str, text=None, media_id=None, fwd=False):
    try:
        await _send(to, "🔍 *Claim Lens* is checking…")
        if media_id:
            data, mime = await _download(media_id)
            m0 = mime.split(";")[0]
            text = ledger.image_text(data) if m0.startswith("image/") else None
            if text:
                await _send(to, "🖼️ I've seen this image before.")
            else:
                text = await file_to_text(data, m0, "upload")
                if text and m0.startswith("image/"):
                    ledger.remember_image(data, text)
            if not text:
                await _send(to, "I couldn't read anything from that file.")
                return
            await _send(to, ("🎤 " if mime.startswith("audio") else "📄 " if "pdf" in mime else "🖼️ ") + text[:300])
        if text and not media_id:
            u = find_url(text)
            if u and len(text.strip()) < len(u) + 40:
                page = await url_to_text(u)
                if not page:
                    await _send(to, "I couldn't read that link. Please paste the message text or send a screenshot.")
                    return
                await _send(to, "🔗 " + page[:300].replace("\n", " ") + "…")
                text = page
        lk = ledger.key(text, _pref.get(to))
        cached, n = ledger.lookup(lk)
        if cached:
            result = cached
            await _send(to, f"♻️ Already checked {n} times by Claim Lens users. Showing the saved result.")
            bad0 = [c for c in result["claims"] if c["label"] in ("False", "Outdated")]
            if bad0 and n >= 2:
                await _guardian_alert(bad0[0]["label"], bad0[0]["text"], n, to)
        else:
            result = await check_text(text, _pref.get(to))
            ledger.store(lk, result)
        bad = [c for c in result["claims"] if c["label"] in ("False", "Outdated", "Partly supported")]
        if fwd and bad:
            tl = result.get("target_language", "en")
            await _send(to, _FWD_WARN.get(tl, _FWD_WARN["en"]).format(label=bad[0]["label"]))
        for m in format_whatsapp(result):
            await _send(to, m)
        rf = result.get("redflags") or {}
        if rf.get("level") in ("medium", "high"):
            await _send(to, "🚩 *Scam risk: " + rf["level"].upper() + "*\n" + "\n".join("• " + f for f in rf["flags"][:4]))
        if result["claims"] and all(c["label"] == "Cannot be confirmed" for c in result["claims"]):
            await _send(to, "ℹ️ I couldn't verify this with trusted public sources. Don't apply or pay through links from forwards: open the organisation's official website yourself, and never pay money for a job, scheme or prize. Check with the issuer before forwarding.\n\n🔎 *What would change this:* an official notice on the organisation's own website, or a published fact-check.\n👤 *Want a human to check it?* Send it to a fact-checking tipline such as Boom Live or Factly, or report it at cybercrime.gov.in.")
        if result["claims"] and all(c["label"] == "Cannot be confirmed" for c in result["claims"]):
            _last[to] = text
            await _send_human_button(to)
        if result["claims"]:
            top = result["claims"][0]
            if top["label"] != "Cannot be confirmed":
                await _send_card(to, top, result.get("target_language", "en"))
        if result["claims"] and to not in _voice_off:
            c = result["claims"][0]
            tl = result.get("target_language", "en")
            if tl != "en" and c.get("explanation_local"):
                await _send_audio(to, c["explanation_local"], tl)
            else:
                await _send_audio(to, c["explanation_en"], "en")
    except Exception as e:
        print("pipeline error:", e)
        await _send(to, "Sorry, something went wrong. Please try again.")


@router.get("/webhook")
async def verify(request: Request):
    q = request.query_params
    if q.get("hub.mode") == "subscribe" and q.get("hub.verify_token") == config.META_VERIFY_TOKEN:
        return Response(content=q.get("hub.challenge", ""), media_type="text/plain")
    return Response(status_code=403)


@router.post("/webhook")
async def incoming(request: Request, background: BackgroundTasks):
    data = await request.json()
    try:
        value = data["entry"][0]["changes"][0]["value"]
        for msg in value.get("messages", []):
            if msg["id"] in _seen:
                continue
            _seen.add(msg["id"])
            sender, t = msg["from"], msg["type"]
            ctx = msg.get("context") or {}
            fwd = bool(ctx.get("forwarded") or ctx.get("frequently_forwarded"))
            print("FORWARD FLAGS:", ctx.get("forwarded"), ctx.get("frequently_forwarded"))
            print("INCOMING FROM:", repr(sender))
            if t == "text":
                rest, cmds = _split_cmds(msg["text"]["body"])
                notes = []
                for c in cmds:
                    if c in _VOICE_OFF:
                        _voice_off.add(sender)
                        notes.append("🔇 Voice replies are off. Send *voice on* to turn them back on.")
                    elif c in _VOICE_ON:
                        _voice_off.discard(sender)
                        notes.append("🔊 Voice replies are on.")
                    elif c in ("guardian on", "guardian off"):
                        g = _guardians()
                        if c == "guardian on" and sender not in g:
                            g.append(sender)
                        if c == "guardian off" and sender in g:
                            g.remove(sender)
                        json.dump(g, open(GUARD_FILE, "w"))
                        notes.append("🛡️ Guardian mode " + ("on. I will alert you when a known false claim keeps circulating." if c == "guardian on" else "off."))
                    elif c in _LANG_CMDS:
                        code = _LANG_CMDS[c]
                        _pref[sender] = None if code == "auto" else code
                        notes.append("✅ Language: " + code)
                if cmds:
                    _save_prefs()
                for n in dict.fromkeys(notes):
                    background.add_task(_send, sender, n)
                if rest and not (cmds and len(rest) < 3):
                    background.add_task(_process, sender, rest, None, fwd)
            elif t == "interactive":
                rid = (msg.get("interactive", {}).get("button_reply") or {}).get("id")
                if rid == "human":
                    background.add_task(_human_request, sender)
            elif t in ("image", "audio", "document"):
                background.add_task(_process, sender, None, msg[t]["id"], fwd)
            else:
                background.add_task(_send, sender, "Please send text, a screenshot or a voice note.")
    except (KeyError, IndexError):
        pass
    return {"ok": True}
