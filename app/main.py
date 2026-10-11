from typing import Optional
import asyncio
from fastapi import FastAPI, Request, BackgroundTasks, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from twilio.rest import Client
from twilio.request_validator import RequestValidator
from twilio.twiml.messaging_response import MessagingResponse

from core import config
from core.pipeline import check_text
from core.formatting import format_whatsapp
from app.mlapi import router as ml_router
from app.emailpage import router as email_router
from app.dashboard import router as dash_router
from app.extra import router as extra_router
from app.voice import router as voice_router
from app.web import router as web_router
from app.landing import router as landing_router
from app.privacy import router as privacy_router
from app.meta import router as meta_router
from app.static_page import router as page_router
from app.tts import router as tts_router
from app.upload import router as upload_router

app = FastAPI(title="Claim Lens")
app.include_router(ml_router)
app.include_router(email_router)
app.include_router(dash_router)
app.include_router(extra_router)
app.include_router(voice_router)
app.include_router(web_router)
app.include_router(landing_router)
app.include_router(privacy_router)
app.include_router(meta_router)
app.include_router(page_router)
app.include_router(tts_router)
app.include_router(upload_router)
twilio_client = Client(config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN)
validator = RequestValidator(config.TWILIO_AUTH_TOKEN)


class CheckIn(BaseModel):
    text: str
    lang: Optional[str] = None


@app.post("/check")
async def check(body: CheckIn):
    return await check_text(body.text, body.lang)


def _send(to: str, text: str):
    twilio_client.messages.create(from_=config.TWILIO_WHATSAPP_FROM, to=to, body=text)


async def _process(to: str, text: str):
    try:
        result = await check_text(text)
        for m in format_whatsapp(result):
            await asyncio.to_thread(_send, to, m)
    except Exception as e:
        print("pipeline error:", e)
        await asyncio.to_thread(_send, to, "Sorry, something went wrong. Please try again.")


@app.post("/whatsapp")
async def whatsapp(request: Request, background: BackgroundTasks):
    form = await request.form()
    params = dict(form)

    if config.VALIDATE_TWILIO:
        sig = request.headers.get("X-Twilio-Signature", "")
        if not validator.validate(config.PUBLIC_URL + "/whatsapp", params, sig):
            raise HTTPException(status_code=403, detail="Invalid signature")

    sender = params.get("From", "")
    body = (params.get("Body") or "").strip()
    resp = MessagingResponse()

    if int(params.get("NumMedia", "0")) > 0:
        resp.message("Images and voice notes are coming soon. For now, please send text.")
    elif not body:
        resp.message("Please forward a message to check.")
    else:
        resp.message("🔍 Checking…")
        background.add_task(_process, sender, body)

    return Response(content=str(resp), media_type="application/xml")


@app.get("/")
async def health():
    return {"status": "ok"}
