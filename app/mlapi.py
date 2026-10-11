import json

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from core import mlmodels

router = APIRouter()


class TextIn(BaseModel):
    text: str


class UrlIn(BaseModel):
    url: str


@router.post("/api/ml/email")
async def ml_email(b: TextIn):
    r = mlmodels.predict_email(b.text)
    if r is None:
        raise HTTPException(503, "Email model not trained yet")
    return r


@router.post("/api/ml/url")
async def ml_url(b: UrlIn):
    r = mlmodels.predict_url(b.url)
    if r is None:
        raise HTTPException(503, "URL model not trained yet")
    return r


@router.get("/api/ml/metrics")
async def ml_metrics():
    try:
        return json.load(open("ml/models/metrics.json"))
    except Exception:
        return {}
