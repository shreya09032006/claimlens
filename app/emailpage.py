import asyncio
from typing import Optional

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse

from core.emailcheck import check
from core.risk import combine
from app.extra import HEAD

router = APIRouter()


@router.post("/api/email")
async def api_email(file: Optional[UploadFile] = File(None), text: Optional[str] = Form(None)):
    raw = await file.read() if file else (text or "").encode()
    if not raw.strip():
        raise HTTPException(422, "Paste the email source or upload a .eml file")
    return await asyncio.to_thread(check, raw)


@router.get("/email", response_class=HTMLResponse)
async def page():
    return r"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#000000"><title>Claim Lens - Email check</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@300..700&family=Instrument+Serif:ital@1&display=swap">
<style>
html,body{background:#000 !important;color:#fff}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:Inter,system-ui,sans-serif;-webkit-font-smoothing:antialiased;min-height:100dvh;position:relative;overflow-x:hidden}
a{color:inherit;text-decoration:none}
.bg{position:fixed;inset:0;z-index:0;background:#000;overflow:hidden}
.bg video{width:100%;height:100%;object-fit:cover}
.bg::after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.72),rgba(0,0,0,.86))}
.page{position:relative;z-index:1;min-height:100dvh;display:flex;flex-direction:column;padding:18px 40px 28px}
header{display:flex;justify-content:space-between;align-items:center;gap:14px;margin-bottom:18px}
.logo{font-size:15.5px;font-weight:600;letter-spacing:-.03em;white-space:nowrap}
nav{display:flex;flex-wrap:wrap;justify-content:flex-end;gap:6px;padding:6px;border:1px solid rgba(198,198,198,.28);border-radius:12px;background:rgba(255,255,255,.04)}
nav a{display:inline-flex;align-items:center;justify-content:center;height:34px;padding:0 15px;border-radius:8px;color:#cfcfcf;font-size:13.5px;transition:.25s}
nav a:hover{background:rgba(255,255,255,.1);color:#fff}
nav a.on{background:linear-gradient(180deg,#fff,#d6d6d6);color:#111;font-weight:500}
main{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;max-width:680px;width:100%;margin:0 auto}
h1{text-align:center;font-weight:500;font-size:38px;letter-spacing:-.045em;line-height:1.1}
h1 em{font-family:"Instrument Serif",serif;font-style:italic;font-weight:400;color:#9a9a9a}
.sub{text-align:center;color:#9a9a9a;font-size:14.5px;line-height:1.5;margin:10px auto 18px;max-width:500px}
.panel{width:100%;display:flex;flex-direction:column;gap:12px;padding:16px;border-radius:14px;border:1px solid rgba(198,198,198,.28);
background:linear-gradient(135deg,rgba(255,255,255,.08),rgba(0,0,0,.55) 46%,rgba(150,170,200,.07));backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px)}
textarea{width:100%;height:120px;padding:14px;font:14.5px Inter,sans-serif;color:#fff;background:rgba(0,0,0,.55);border:1px solid rgba(255,255,255,.18);border-radius:10px;resize:vertical;outline:none}
textarea:focus{border-color:rgba(220,230,255,.7)}
textarea::placeholder{color:#777}
input[type=file]{width:100%;padding:10px 12px;border-radius:8px;border:1px solid rgba(198,198,198,.4);background:rgba(0,0,0,.5);color:#ccc;font-size:13px}
input[type=file]::file-selector-button{margin-right:10px;padding:6px 10px;border-radius:6px;border:1px solid rgba(198,198,198,.45);background:linear-gradient(105deg,#050505,#2a2a2a 48%,#4a4a4a);color:#f3f3f3;font:12.5px Inter,sans-serif;cursor:pointer}
button{font:13.5px Inter,sans-serif;cursor:pointer;height:44px;padding:0 16px;border-radius:6px;font-weight:500;border:1px solid #fff;color:#111;background:linear-gradient(180deg,#fff,#e7e7e7 48%,#cfcfcf)}
button:disabled{opacity:.6}
#st{text-align:center;color:#9a9a9a;font-size:14px;min-height:18px}
.card{width:100%;background:rgba(8,8,8,.82);border:1px solid rgba(255,255,255,.14);border-left:6px solid #777;border-radius:12px;padding:14px 16px;margin-top:14px;line-height:1.6;font-size:14.5px;overflow-wrap:anywhere}
.ex{color:#8c8c8c;font-size:13px;margin-top:12px;text-align:center;line-height:1.6}
@media(max-width:900px){.page{padding:16px 16px 28px}header{flex-direction:column;align-items:flex-start}nav{width:100%;display:grid;grid-template-columns:repeat(3,1fr);gap:5px}nav a{height:38px;padding:0 6px;font-size:13px}}
@media(max-width:600px){h1{font-size:30px}main{justify-content:flex-start}}
</style></head><body>
<div class="bg"><video autoplay muted loop playsinline preload="auto" src="https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260818_072341_50851634-bbc3-4c33-9acc-7647d4db44aa.mp4"></video></div>
<div class="page">
<header><a class="logo" href="/"> Claim Lens</a>
<nav><a href="/">Home</a><a href="/app">Checker</a><a href="/dashboard">Ledger</a><a href="/languages">Languages</a><a href="/scan">Scan</a><a href="/email" class="on">Email</a><a href="/privacy">Privacy</a></nav></header>
<main>
<h1>Email <em>phishing</em> check.</h1>
<div class="sub">Upload the original email (.eml) or paste its full source. We verify the sender's digital signature (DKIM), SPF and DMARC, and look for fake links.</div>
<div class="panel">
<textarea id="t" placeholder="Paste the full email source here (Gmail: three dots, Show original)..."></textarea>
<input type="file" id="f" accept=".eml,message/rfc822,text/plain">
<button id="go">Check this email</button><div id="st"></div></div>
<div id="out" style="width:100%"></div>
<div class="ex">Gmail: open the email, tap the three dots, then <b>Download message</b> (gives a .eml) or <b>Show original</b> then copy all.</div>
</main></div>
<script>
const $=id=>document.getElementById(id);
const COL={low:"#2e7d32",medium:"#ef6c00",high:"#c62828"};
const SEV={high:"High: ",medium:"Medium: ",info:"Note: "};
const esc=s=>String(s==null?"":s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
$("go").onclick=async()=>{const f=$("f").files[0],t=$("t").value.trim();if(!f&&!t){$("st").textContent="Add the email source or a file.";return}
 $("st").textContent="Checking...";const fd=new FormData();if(f)fd.append("file",f);else fd.append("text",t);
 try{const r=await fetch("/api/email",{method:"POST",body:fd});const d=await r.json();if(!r.ok)throw new Error(d.detail||"Error");
  const a=d.auth;
  $("out").innerHTML='<div class="card" style="border-left-color:'+COL[d.level]+'"><div style="font-size:20px;font-weight:600">'+(d.level==="low"?"":"")+" Phishing risk: "+d.level.toUpperCase()+'</div>'+
  '<div style="color:#bbb;margin:6px 0">From: '+esc(d.from)+'<br>Subject: '+esc(d.subject)+'</div>'+
  '<div style="margin:8px 0">SPF: <b>'+esc(a.spf||"n/a")+'</b> · DKIM: <b>'+esc(a.dkim||"n/a")+'</b> · DMARC: <b>'+esc(a.dmarc||"n/a")+'</b><br>Signature checked here: <b>'+(a.dkim_verified_here===true?"valid":a.dkim_verified_here===false?"not valid":"not available")+'</b>'+(a.dkim_domain?" (signed by "+esc(a.dkim_domain)+")":"")+'</div>'+
  (d.findings.length?d.findings.map(x=>SEV[x.sev]+" "+esc(x.msg)).join("<br>"):"No red flags found.")+
  (d.links.length?'<div style="margin-top:10px;color:#9a9a9a;font-size:13px">Links found: '+d.links.map(esc).join(", ")+'</div>':"")+'</div>';
  $("st").textContent=""}catch(e){$("st").textContent="Error: "+e.message}};
const sid=new URLSearchParams(location.search).get("sid");
if(sid){fetch("/api/email-stash/"+sid).then(r=>r.json()).then(d=>{$("t").value=d.raw;$("go").click()}).catch(()=>{$("st").textContent="That email expired, please try again."})}
</script></body></html>"""


from pydantic import BaseModel
from typing import List
from urllib.parse import urlparse
import re as _re
from core.emailcheck import _brand_check, _root, _dom
from core.redflags import scan as _scan


class Link(BaseModel):
    href: str = ""
    text: str = ""


class Lite(BaseModel):
    sender: str = ""
    subject: str = ""
    body: str = ""
    links: List[Link] = []


def _shown_domain(text):
    """Return a regex match only if the link text really shows a web address.

    Degree names and abbreviations such as 'B.Tech', 'Ph.D' or 'B.Com' look like
    domains but are not, so the first label must be 3+ letters and the text must
    start with http(s)://, www., or be essentially just the address.
    """
    t = (text or "").strip().lower()
    m = _re.search(r"([a-z0-9-]+\.)+[a-z]{2,}", t)
    if not m or len(m.group(0).split(".")[0]) < 3:
        return None
    looks_like_url = t.startswith(("http://", "https://", "www.")) or len(t) <= len(m.group(0)) + 25
    return m if looks_like_url and " " not in t.split("/")[0] else None


@router.post("/api/email-lite")
async def email_lite(d: Lite):
    f = []
    from_d = _dom(d.sender) or d.sender.split("@")[-1].lower()
    _brand_check(from_d, f, "Sender domain")
    seen = []
    for l in d.links[:40]:
        hd = (urlparse(l.href).hostname or "").lower()
        if not hd or hd.endswith("google.com"):
            continue
        seen.append(hd)
        _brand_check(hd, f, "Link domain")
        m = _shown_domain(l.text)
        if m and _root(m.group(0)) != _root(hd):
            f.append(("high", f"Link text shows '{m.group(0)}' but really goes to '{hd}'"))
        if _re.search(r"(bit\.ly|tinyurl|cutt\.ly|rb\.gy)", hd):
            f.append(("medium", f"Shortened link hides the real site ({hd})"))
    for fl in _scan(d.subject + " " + d.body[:4000])["flags"]:
        f.append(("medium", fl))
    uniq = list(dict.fromkeys(f))
    high = sum(1 for s, _ in uniq if s == "high")
    med = sum(1 for s, _ in uniq if s == "medium")
    level = "high" if high >= 1 or med >= 3 else "medium" if med >= 1 else "low"
    c = combine(level, d.subject + " " + d.body[:4000], sender=d.sender)
    findings = [{"sev": s, "msg": m} for s, m in uniq]
    if c["level"] == "low":      # verdict is low: drop weak rule hits, they only confuse
        findings = []
        if c.get("category") != "promotional":
            c["note"] = None
    if c["note"]:
        findings.append({"sev": "info", "msg": c["note"]})
    return {"level": c["level"], "from": from_d, "findings": findings, "ml": c["ml"], "category": c.get("category")}


import uuid as _uuid

_stash = {}


class Stash(BaseModel):
    raw: str


@router.post("/api/email-stash")
async def email_stash(b: Stash):
    sid = _uuid.uuid4().hex[:10]
    _stash[sid] = b.raw[:300000]
    return {"sid": sid}


@router.get("/api/email-stash/{sid}")
async def email_stash_get(sid: str):
    raw = _stash.pop(sid, None)
    if raw is None:
        raise HTTPException(404, "Expired")
    return {"raw": raw}