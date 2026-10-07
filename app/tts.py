import asyncio
import io
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from gtts import gTTS

from core.config import LANG_NAMES

router = APIRouter()


class TTSIn(BaseModel):
    text: str
    lang: str = "en"


def _synth(text: str, lang: str) -> bytes:
    buf = io.BytesIO()
    gTTS(text=text, lang=lang).write_to_fp(buf)
    return buf.getvalue()


@router.post("/tts")
async def tts(body: TTSIn):
    if body.lang not in LANG_NAMES:
        raise HTTPException(status_code=400, detail="Unsupported language")
    if not body.text.strip():
        raise HTTPException(status_code=422, detail="No text")
    try:
        audio = await asyncio.to_thread(_synth, body.text[:900], body.lang)
    except Exception as e:
        print("tts error:", e)
        raise HTTPException(status_code=503, detail="Speech service unavailable")
    return Response(content=audio, media_type="audio/mpeg")
