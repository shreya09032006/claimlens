import asyncio
import io
from gtts import gTTS


def _synth(text: str, lang: str) -> bytes:
    buf = io.BytesIO()
    gTTS(text=text, lang=lang).write_to_fp(buf)
    return buf.getvalue()


async def speak(text: str, lang: str) -> bytes:
    return await asyncio.to_thread(_synth, text[:800], lang)
