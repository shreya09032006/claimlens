import asyncio
from typing import Optional

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import HTMLResponse

from core.emailcheck import check
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
    return HEAD.replace("TITLE", "Claim Lens - Email check") + r"""
<h1>Email <em>phishing</em> check.</h1>
<div class="sub">Upload the original email (.eml) or paste its full source. We verify the sender's digital signature (DKIM), SPF and DMARC, and look for fake links.</div>
<div class="panel">
<textarea id="t" placeholder="Paste the full email source here (Gmail: three dots, Show original)..."></textarea>
<input type="file" id="f" accept=".eml,message/rfc822,text/plain" style="color:#ccc;font-size:13px">
<button class="p" id="go">Check this email</button><div id="st" style="text-align:center;color:#9a9a9a;font-size:14px"></div></div>
<div id="out"></div>
<div class="ex">Gmail: open the email, tap the three dots, then <b>Download message</b> (gives a .eml) or <b>Show original</b> then copy all.</div>
</div><script>
const $=id=>document.getElementById(id);
const COL={low:"#2e7d32",medium:"#ef6c00",high:"#c62828"};
const SEV={high:"🔴",medium:"🟠",info:"ℹ️"};
const esc=s=>String(s==null?"":s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
$("go").onclick=async()=>{const f=$("f").files[0],t=$("t").value.trim();if(!f&&!t){$("st").textContent="Add the email source or a file.";return}
 $("st").textContent="Checking...";const fd=new FormData();if(f)fd.append("file",f);else fd.append("text",t);
 try{const r=await fetch("/api/email",{method:"POST",body:fd});const d=await r.json();if(!r.ok)throw new Error(d.detail||"Error");
  const a=d.auth;
  $("out").innerHTML='<div class="card" style="border-left-color:'+COL[d.level]+'"><div style="font-size:20px;font-weight:600">'+(d.level==="low"?"✅":"🚩")+" Phishing risk: "+d.level.toUpperCase()+'</div>'+
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
        m = _re.search(r"([a-z0-9-]+\.)+[a-z]{2,}", l.text.lower())
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
    return {"level": level, "from": from_d, "findings": [{"sev": s, "msg": m} for s, m in uniq]}


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
