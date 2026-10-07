import asyncio
import io
import httpx
from google.genai import types

from .llm import client
from .config import GEMINI_MODELS, GROQ_API_KEY

FALLBACK_MODEL = "gemini-3.8-flash-lite"  # change if it 404s

IMAGE_PROMPT = (
    "Extract all text from this image exactly as written, in its original language. "
    "If it is a screenshot of a chat, post or forward, include the full message text. "
    "If there is no text, state in one sentence any factual claim the image makes. "
    "Return only the text, nothing else."
)
AUDIO_PROMPT = (
    "Transcribe this voice note exactly, in its original language. "
    "Return only the transcript, nothing else."
)


def _tesseract(data: bytes) -> str:
    import pytesseract
    from PIL import Image

    img = Image.open(io.BytesIO(data))
    try:
        return pytesseract.image_to_string(img, lang="eng+hin+mar+mal").strip()
    except Exception:
        return pytesseract.image_to_string(img, lang="eng").strip()


async def _gemini_media(data: bytes, mime: str, prompt: str) -> str:
    part = types.Part.from_bytes(data=data, mime_type=mime)
    models = GEMINI_MODELS * 2
    last = None
    for attempt, model in enumerate(models):
        try:
            resp = await client.aio.models.generate_content(
                model=model, contents=[part, prompt]
            )
            return (resp.text or "").strip()
        except Exception as e:
            last = e
            print(f"gemini media failed (attempt {attempt + 1}, {model}):", str(e)[:150])
            await asyncio.sleep(min(3 * (attempt + 1), 12))
    raise last


async def image_to_text(data: bytes, mime: str) -> str:
    try:
        text = await _gemini_media(data, mime, IMAGE_PROMPT)
        if text:
            return text
    except Exception:
        pass
    print("Switching to local Tesseract OCR...")
    return await asyncio.to_thread(_tesseract, data)


async def _whisper(data: bytes, filename: str, mime: str) -> str:
    async with httpx.AsyncClient(timeout=60) as http:
        r = await http.post(
            "https://api.groq.com/openai/v1/audio/transcriptions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            files={"file": (filename, data, mime)},
            data={"model": "whisper-large-v3-turbo", "response_format": "verbose_json"},
        )
        if r.status_code >= 400:
            raise RuntimeError(f"whisper {r.status_code}: {r.text[:300]}")
        j = r.json()
        text = (j.get("text") or "").strip()
        names = {"hindi": "Hindi", "marathi": "Marathi", "malayalam": "Malayalam",
                 "tamil": "Tamil", "telugu": "Telugu", "bengali": "Bengali",
                 "gujarati": "Gujarati", "kannada": "Kannada", "urdu": "Hindi"}
        lang = names.get((j.get("language") or "").lower())
        if lang and text:
            text = f"[Spoken language: {lang}] " + text
        return text


async def audio_to_text(data: bytes, filename: str = "audio.ogg", mime: str = "audio/ogg") -> str:
    try:
        return await _whisper(data, filename, mime)
    except Exception as e:
        print("whisper failed, trying Gemini audio:", str(e)[:150])
    return await _gemini_media(data, mime, AUDIO_PROMPT)


async def file_to_text(data: bytes, mime: str, filename: str = "file") -> str:
    mime = (mime or "").lower()
    if mime.startswith("image/"):
        return await image_to_text(data, mime)
    if mime == "application/pdf":
        return await pdf_to_text(data)
    if mime.startswith("audio/") or mime in ("video/ogg", "application/ogg"):
        return await audio_to_text(data, filename, mime)
    raise ValueError(f"Unsupported file type: {mime}")


import re as _re


def find_url(text: str):
    m = _re.search(r"https?://[^\s]+", text or "")
    return m.group(0).rstrip(").,]") if m else None


def _fetch_url(url: str) -> str:
    import trafilatura
    html = trafilatura.fetch_url(url)
    if not html:
        return ""
    return (trafilatura.extract(html) or "").strip()


async def url_to_text(url: str) -> str:
    text = await asyncio.to_thread(_fetch_url, url)
    return text[:6000]


def _pdf_text(data: bytes) -> str:
    import fitz
    doc = fitz.open(stream=data, filetype="pdf")
    out = []
    for i, page in enumerate(doc):
        if i >= 8:
            break
        out.append(page.get_text())
    return "\n".join(out).strip()


async def pdf_to_text(data: bytes) -> str:
    text = await asyncio.to_thread(_pdf_text, data)
    return text[:6000]
