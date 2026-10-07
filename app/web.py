import asyncio
import json
import time
from typing import Optional

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import Response, JSONResponse
from pydantic import BaseModel

from core import ledger
from core.pipeline import check_text
from core.ingest import file_to_text, find_url, url_to_text
from core.card import make_card
from app import meta

router = APIRouter()


class In(BaseModel):
    text: str
    lang: Optional[str] = None


class CardIn(BaseModel):
    claim: dict
    lang: str = "en"


async def _run(text, lang):
    lk = ledger.key(text, lang)
    cached, n = ledger.lookup(lk)
    if cached:
        cached["repeat"] = n
        bad = [c for c in cached["claims"] if c["label"] in ("False", "Outdated")]
        if bad and n >= 2:
            try:
                await meta._guardian_alert(bad[0]["label"], bad[0]["text"], n)
            except Exception as e:
                print("guardian error:", e)
        return cached
    res = await check_text(text, lang)
    ledger.store(lk, res)
    res["repeat"] = 1
    return res


@router.post("/api/check")
async def api_check(body: In):
    text = body.text.strip()
    if not text:
        raise HTTPException(422, "Nothing to check")
    extracted = None
    u = find_url(text)
    if u and len(text) < len(u) + 40:
        if any(x in u for x in ("mail.google.com", "outlook.live.com", "outlook.office.com")):
            raise HTTPException(422, "Email pages are private, so I can't read them from a link. Open the email and use the Claim Lens badge, or paste the text.")
        page = await url_to_text(u)
        if not page:
            raise HTTPException(422, "I could not read that link. Paste the text instead.")
        extracted, text = page[:400], page
    res = await _run(text, body.lang)
    if extracted:
        res["extracted_text"] = extracted
    return res


@router.post("/api/check-file")
async def api_check_file(file: UploadFile = File(...), lang: Optional[str] = Form(None)):
    data = await file.read()
    mime = (file.content_type or "").split(";")[0]
    text = ledger.image_text(data) if mime.startswith("image/") else None
    if not text:
        try:
            text = await file_to_text(data, mime, file.filename or "file")
        except ValueError as e:
            raise HTTPException(415, str(e))
        except Exception as e:
            print("ingest error:", e)
            raise HTTPException(503, "The AI service is busy. Try again in a minute.")
        if text and mime.startswith("image/"):
            ledger.remember_image(data, text)
    if not text:
        raise HTTPException(422, "Could not read anything from this file")
    res = await _run(text, lang)
    res["extracted_text"] = text[:600]
    return res


@router.post("/api/card")
async def api_card(b: CardIn):
    png = await asyncio.to_thread(make_card, b.claim, b.lang)
    return Response(png, media_type="image/png")


@router.post("/api/human")
async def api_human(b: In):
    try:
        q = json.load(open("data/human_queue.json"))
    except Exception:
        q = []
    q.append({"who": "web", "text": b.text[:300], "ts": int(time.time())})
    json.dump(q, open("data/human_queue.json", "w"))
    return {"ok": True}


@router.get("/manifest.webmanifest")
async def manifest():
    return JSONResponse({
        "name": "Claim Lens", "short_name": "Claim Lens", "start_url": "/app", "display": "standalone",
        "background_color": "#000000", "theme_color": "#000000",
        "icons": [{"src": "/icon-192.png", "sizes": "192x192", "type": "image/png"},
                  {"src": "/icon-512.png", "sizes": "512x512", "type": "image/png"}],
        "share_target": {"action": "/share", "method": "POST", "enctype": "multipart/form-data",
                         "params": {"title": "title", "text": "text", "url": "url",
                                    "files": [{"name": "file", "accept": ["image/*", "application/pdf"]}]}},
    }, media_type="application/manifest+json")


@router.get("/sw.js")
async def sw():
    return Response("self.addEventListener('fetch',function(){});", media_type="application/javascript")


@router.get("/icon-{size}.png")
async def icon(size: int):
    import io
    from PIL import Image, ImageDraw
    size = 512 if size > 300 else 192
    img = Image.new("RGB", (size, size), "black")
    d = ImageDraw.Draw(img)
    r = size * 0.26
    c = (size * 0.45, size * 0.45)
    d.ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r], outline="white", width=max(6, size // 22))
    d.line([c[0] + r * 0.72, c[1] + r * 0.72, size * 0.8, size * 0.8], fill="white", width=max(8, size // 18))
    buf = io.BytesIO()
    img.save(buf, "PNG")
    return Response(buf.getvalue(), media_type="image/png")


import uuid
from fastapi import Request
from fastapi.responses import RedirectResponse

_shared = {}
_SOCIAL = ("instagram.com", "facebook.com", "fb.watch", "x.com", "twitter.com", "tiktok.com", "youtube.com/shorts")


@router.post("/share")
async def share(request: Request):
    form = await request.form()
    sid = uuid.uuid4().hex[:10]
    item = {"text": " ".join(str(form.get(k) or "") for k in ("title", "text", "url")).strip()}
    f = form.get("file")
    if f is not None and hasattr(f, "read"):
        item["data"] = await f.read()
        item["mime"] = (f.content_type or "").split(";")[0]
        item["name"] = f.filename
    _shared[sid] = item
    return RedirectResponse(f"/app?sid={sid}", status_code=303)


@router.get("/api/share/{sid}")
async def api_share(sid: str):
    it = _shared.pop(sid, None)
    if not it:
        raise HTTPException(404, "This share expired. Please share again.")
    if it.get("data"):
        text = await file_to_text(it["data"], it["mime"], it.get("name") or "file")
        if not text:
            raise HTTPException(422, "Could not read anything from this file")
        res = await _run(text, None)
        res["extracted_text"] = text[:600]
        return res
    text = it["text"]
    if not text:
        raise HTTPException(422, "Nothing was shared")
    try:
        return await api_check(In(text=text))
    except HTTPException as e:
        if e.status_code == 422 and any(x in text.lower() for x in _SOCIAL):
            raise HTTPException(422, "Instagram and other social apps block link reading. Take a screenshot of the post and share or upload that, or paste its caption.")
        raise
