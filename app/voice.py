import asyncio
import os
import uuid

from fastapi import APIRouter, Request, Response
from fastapi.responses import FileResponse
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Gather

from core import config
from core.audio import speak
from core.formatting import T, EN
from app.web import _run

router = APIRouter()
os.makedirs("data/audio", exist_ok=True)
LANGS = {"1": ("hi", "hi-IN"), "2": ("mr", "mr-IN"), "3": ("ml", "ml-IN"), "4": ("en", "en-IN")}
_jobs = {}


def xml(r):
    return Response(content=str(r), media_type="application/xml")


def _callback(to, frm):
    Client(config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN).calls.create(
        to=to, from_=frm, url=f"{config.PUBLIC_URL}/voice/incoming?cb=1")


@router.post("/voice/incoming")
async def incoming(request: Request):
    f = await request.form()
    r = VoiceResponse()
    if os.getenv("MISSED_CALL") == "1" and not request.query_params.get("cb"):
        r.reject(reason="busy")
        asyncio.get_event_loop().run_in_executor(None, _callback, f.get("From"), f.get("To"))
        return xml(r)
    g = Gather(num_digits=1, action="/voice/lang", method="POST", timeout=6)
    g.say("Welcome to Claim Lens. For Hindi press 1. For Marathi press 2. For Malayalam press 3. For English press 4.", language="en-IN")
    r.append(g)
    r.redirect("/voice/incoming", method="POST")
    return xml(r)


@router.post("/voice/lang")
async def lang(request: Request):
    f = await request.form()
    code, stt = LANGS.get(f.get("Digits", "4"), LANGS["4"])
    r = VoiceResponse()
    g = Gather(input="speech", language=stt, action=f"/voice/check?l={code}", method="POST",
               speech_timeout="auto", timeout=8)
    g.say("Please say the message you want to check, after the beep.", language="en-IN")
    r.append(g)
    r.redirect("/voice/incoming", method="POST")
    return xml(r)


async def _work(job, text, code):
    try:
        res = await _run(text, code)
        if not res["claims"]:
            msg, tl = "I could not find a claim to check in that message.", "en"
        else:
            c = res["claims"][0]
            t = T.get(code, EN)
            local = code != "en" and c.get("explanation_local")
            msg = f"{t['labels'][c['label']]}. " + (c["explanation_local"] if local else c["explanation_en"])
            tl = code if local else "en"
        name = f"{job}.mp3"
        open(f"data/audio/{name}", "wb").write(await speak(msg, tl))
        _jobs[job] = name
    except Exception as e:
        print("voice error:", e)
        _jobs[job] = "error"


@router.post("/voice/check")
async def check(request: Request):
    f = await request.form()
    code = request.query_params.get("l", "en")
    text = (f.get("SpeechResult") or "").strip()
    r = VoiceResponse()
    if not text:
        r.say("Sorry, I did not catch that.", language="en-IN")
        r.redirect("/voice/incoming", method="POST")
        return xml(r)
    job = uuid.uuid4().hex[:10]
    asyncio.create_task(_work(job, text, code))
    r.say("Checking. Please hold.", language="en-IN")
    r.redirect(f"/voice/result?id={job}&t=0", method="POST")
    return xml(r)


@router.post("/voice/result")
async def result(request: Request):
    job = request.query_params.get("id")
    tries = int(request.query_params.get("t", "0"))
    v = _jobs.get(job)
    r = VoiceResponse()
    if v and v != "error":
        r.play(f"{config.PUBLIC_URL}/audio/{v}")
        g = Gather(num_digits=1, action="/voice/incoming", method="POST", timeout=5)
        g.say("To check another message, press 1.", language="en-IN")
        r.append(g)
        r.say("Thank you. Goodbye.", language="en-IN")
    elif v == "error" or tries >= 8:
        r.say("Sorry, something went wrong. Please try again later.", language="en-IN")
    else:
        r.pause(length=4)
        r.redirect(f"/voice/result?id={job}&t={tries + 1}", method="POST")
    return xml(r)


@router.get("/audio/{name}")
async def audio(name: str):
    if not name.endswith(".mp3") or "/" in name or ".." in name:
        return Response(status_code=404)
    return FileResponse(f"data/audio/{name}", media_type="audio/mpeg")
