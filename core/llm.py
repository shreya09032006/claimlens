import asyncio
import hashlib
import json
import os
import re
import time

import httpx
from google import genai
from google.genai import types

from .config import GEMINI_API_KEY, GROQ_API_KEY, GEMINI_MODELS, GROQ_MODELS, LLM_PRIMARY

client = genai.Client(api_key=GEMINI_API_KEY)

_CACHE_DIR = ".cache"
os.makedirs(_CACHE_DIR, exist_ok=True)
_cool = {}  # (provider, model) -> time until which it is skipped


def _parse(text: str) -> dict:
    text = (text or "").strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text).strip()
    return json.loads(text)


async def _gemini(model: str, system: str, user: str, max_tokens: int) -> dict:
    config = types.GenerateContentConfig(
        system_instruction=system + "\n\nReturn ONLY valid JSON.",
        response_mime_type="application/json",
        max_output_tokens=max_tokens,
        temperature=0.1,
    )
    resp = await client.aio.models.generate_content(model=model, contents=user, config=config)
    return _parse(resp.text)


async def _groq(model: str, system: str, user: str, max_tokens: int) -> dict:
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": system + "\n\nReturn ONLY valid JSON."},
            {"role": "user", "content": user},
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.1,
        "max_tokens": max_tokens,
    }
    if "gpt-oss" in model:
        body["reasoning_effort"] = "low"
    async with httpx.AsyncClient(timeout=40) as http:
        r = await http.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
            json=body,
        )
        if r.status_code >= 400:
            raise RuntimeError(f"groq {r.status_code}: {r.text[:300]}")
        return _parse(r.json()["choices"][0]["message"]["content"])


def _chain():
    g = [("gemini", m) for m in GEMINI_MODELS] if GEMINI_API_KEY else []
    q = [("groq", m) for m in GROQ_MODELS] if GROQ_API_KEY else []
    return (q + g) if LLM_PRIMARY == "groq" else (g + q)


def _cooldown(err: str) -> int:
    e = err.lower()
    if "429" in e or "resource_exhausted" in e or "rate limit" in e:
        if "per day" in e or "tpd" in e or "rpd" in e or "perday" in e:
            return 1800
        return 60
    if "404" in e or "not_found" in e or "decommissioned" in e:
        return 3600
    if "503" in e or "unavailable" in e:
        return 20
    return 5


async def ask_json(system: str, user: str, max_tokens: int = 2048) -> dict:
    key = hashlib.sha256((system + "||" + user).encode()).hexdigest()
    path = os.path.join(_CACHE_DIR, key + ".json")
    if os.path.exists(path):
        return json.load(open(path))

    chain = _chain()
    last = None
    for _ in range(4):
        now = time.time()
        usable = [(p, m) for p, m in chain if _cool.get((p, m), 0) <= now]
        if not usable:
            wait = min(_cool.get(pm, 0) for pm in chain) - now
            await asyncio.sleep(max(1, min(wait, 20)))
            continue
        for provider, model in usable:
            try:
                fn = _groq if provider == "groq" else _gemini
                out = await fn(model, system, user, max_tokens)
                print(f"LLM ok: {provider}/{model}")
                json.dump(out, open(path, "w"))
                return out
            except Exception as e:
                last = e
                msg = str(e)
                _cool[(provider, model)] = time.time() + _cooldown(msg)
                print(f"{provider}/{model} failed:", msg[:100])
    raise last or RuntimeError("No LLM available")
