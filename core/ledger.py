import hashlib
import json
import re
import time

FILE = "data/ledger.json"
IMG = "data/images.json"
TTL = 7 * 24 * 3600
_norms = {}


def _load():
    try:
        return json.load(open(FILE))
    except Exception:
        return {}


def key(text: str, lang) -> str:
    norm = re.sub(r"\W+", " ", (text or "").lower()).strip()
    k = hashlib.sha256(f"{norm}|{lang or ''}".encode()).hexdigest()
    _norms[k] = norm
    return k


def _sim(a: str, b: str) -> float:
    x, y = set(a.split()), set(b.split())
    return len(x & y) / len(x | y) if x and y else 0.0


def lookup(k: str):
    d = _load()
    e = d.get(k)
    if not e:
        norm = _norms.get(k, "")
        for k2, v in d.items():
            if v.get("norm") and _sim(norm, v["norm"]) >= 0.8:
                k, e = k2, v
                break
    if not e or time.time() - e["ts"] > TTL:
        return None, 0
    e["count"] += 1
    d[k] = e
    json.dump(d, open(FILE, "w"))
    return e["result"], e["count"]


def store(k: str, result: dict):
    d = _load()
    d[k] = {"result": result, "count": 1, "ts": time.time(), "norm": _norms.get(k, "")}
    json.dump(d, open(FILE, "w"))


def image_text(data: bytes):
    try:
        import io, imagehash
        from PIL import Image
        h = imagehash.phash(Image.open(io.BytesIO(data)))
        d = json.load(open(IMG))
        for k, v in d.items():
            if h - imagehash.hex_to_hash(k) <= 6:
                return v
    except Exception:
        pass
    return None


def remember_image(data: bytes, text: str):
    try:
        import io, imagehash
        from PIL import Image
        h = str(imagehash.phash(Image.open(io.BytesIO(data))))
        try:
            d = json.load(open(IMG))
        except Exception:
            d = {}
        d[h] = text
        json.dump(d, open(IMG, "w"))
    except Exception as e:
        print("image hash error:", e)
