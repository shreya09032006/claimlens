import asyncio

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

import urlcheck

router = APIRouter()


class UrlIn(BaseModel):
    url: str


def _clean(u):
    u = (u or "").strip()
    if not u or len(u) > 2048:
        raise HTTPException(400, "Provide a URL under 2048 characters")
    return u


@router.get("/api/url-status")
async def url_status():
    return urlcheck.status()


@router.post("/api/url-check")
async def url_check(b: UrlIn):
    r = await asyncio.to_thread(urlcheck.scan_url, _clean(b.url))
    if r is None:
        raise HTTPException(503, "URL model not available: " + str(urlcheck.status()["error"]))
    return r


@router.post("/api/url-enrich")
async def url_enrich(b: UrlIn):
    r = await asyncio.to_thread(urlcheck.enrich, _clean(b.url))
    if r is None:
        raise HTTPException(503, "URL model not available: " + str(urlcheck.status()["error"]))
    return r