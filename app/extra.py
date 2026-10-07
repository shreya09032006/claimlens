from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from core.redflags import scan

router = APIRouter()


class ScanIn(BaseModel):
    text: str


@router.post("/api/scan")
async def api_scan(b: ScanIn):
    return scan(b.text)


HEAD = r"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>TITLE</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@300..700&family=Instrument+Serif:ital@1&display=swap">
<style>
html,body{background:#000 !important;color:#fff}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:Inter,system-ui,sans-serif;min-height:100dvh}
a{color:inherit;text-decoration:none}
.page{max-width:560px;margin:0 auto;padding:22px 20px 56px}
header{display:flex;justify-content:space-between;align-items:center;margin-bottom:34px;gap:10px;flex-wrap:wrap}
.logo{font-size:15.5px;font-weight:600}
nav{display:flex;gap:6px;flex-wrap:wrap}
nav a{display:inline-flex;align-items:center;height:34px;padding:0 14px;border-radius:7px;border:1px solid rgba(198,198,198,.55);background:linear-gradient(105deg,#050505,#2a2a2a 48%,#4a4a4a);color:#f3f3f3;font-size:13px}
h1{text-align:center;font-weight:500;font-size:36px;letter-spacing:-.045em;line-height:1.1}
h1 em{font-family:"Instrument Serif",serif;font-style:italic;font-weight:400;color:#9a9a9a}
.sub{text-align:center;color:#9a9a9a;font-size:15px;line-height:1.55;margin:14px auto 24px;max-width:430px}
.panel{display:flex;flex-direction:column;gap:12px;padding:16px;border-radius:14px;border:1px solid rgba(198,198,198,.28);background:rgba(255,255,255,.05)}
textarea{width:100%;height:130px;padding:14px;font:15.5px Inter,sans-serif;color:#fff;background:rgba(0,0,0,.55);border:1px solid rgba(255,255,255,.18);border-radius:10px;resize:vertical;outline:none}
button,.btn{font:13.5px Inter,sans-serif;color:#fff;cursor:pointer;height:44px;padding:0 16px;border-radius:6px;font-weight:500;border:1px solid rgba(198,198,198,.5);background:rgba(255,255,255,.08);display:inline-flex;align-items:center;justify-content:center}
.p{color:#111 !important;background:linear-gradient(180deg,#fff,#cfcfcf) !important}
.card{background:rgba(8,8,8,.82);border:1px solid rgba(255,255,255,.14);border-left:6px solid #777;border-radius:12px;padding:16px;margin-top:16px;line-height:1.6}
.lang{padding:14px;border-radius:10px;border:1px solid rgba(255,255,255,.14);background:rgba(8,8,8,.7);margin-top:10px}
.lang b{font-size:18px}.lang small{display:block;color:#9a9a9a;margin-top:4px}
.ex{color:#9a9a9a;font-size:13px;margin-top:12px;line-height:1.7}
.ex a{color:#8ab4ff;cursor:pointer;text-decoration:underline}
</style></head><body><div class="page">
<header><a class="logo" href="/">🔍 Claim Lens</a>
<nav><a href="/app">Checker</a><a href="/dashboard">Ledger</a><a href="/languages">Languages</a><a href="/privacy">Privacy</a></nav></header>
"""


@router.get("/languages", response_class=HTMLResponse)
async def languages():
    return HEAD.replace("TITLE", "Claim Lens - Languages") + r"""
<style>
.lang{text-align:center;cursor:pointer;transition:.3s}
.lang:hover{border-color:#fff;box-shadow:0 0 22px rgba(170,200,255,.25)}
.lang b{display:block;font-size:20px}
.tryit{display:inline-block;margin-top:10px;font-size:12.5px;padding:5px 12px;border-radius:12px;background:rgba(255,255,255,.1);color:#ddd}
.sample{color:#bbb;font-size:14px;margin-top:8px;line-height:1.5}
</style>
<h1 style="text-align:center">Your <em>language</em>,<br>your verdict.</h1>
<div class="sub" style="text-align:center">Tap a language to try it. We check a sample claim and answer in that language, with a voice reply.</div>
<div class="lang" data-l="hi" data-q="गरम पानी पीने से कोरोना ठीक हो जाता है।"><b>हिन्दी · Hindi</b><div class="sample">गरम पानी पीने से कोरोना ठीक हो जाता है।</div><span class="tryit">Try in Hindi →</span></div>
<div class="lang" data-l="mr" data-q="दर पंधरा मिनिटांनी गरम पाणी प्यायल्याने कोविड बरा होतो."><b>मराठी · Marathi</b><div class="sample">दर पंधरा मिनिटांनी गरम पाणी प्यायल्याने कोविड बरा होतो.</div><span class="tryit">Try in Marathi →</span></div>
<div class="lang" data-l="ml" data-q="ചൂടുവെള്ളം കുടിച്ചാൽ കോവിഡ് മാറും."><b>മലയാളം · Malayalam</b><div class="sample">ചൂടുവെള്ളം കുടിച്ചാൽ കോവിഡ് മാറും.</div><span class="tryit">Try in Malayalam →</span></div>
<div class="lang" data-l="en" data-q="Drinking hot water every 15 minutes cures COVID-19"><b>English</b><div class="sample">Drinking hot water every 15 minutes cures COVID-19</div><span class="tryit">Try in English →</span></div>
<div class="panel" style="margin-top:22px">
<a class="btn p" href="/app">🌐 Use the web checker</a>
<a class="btn" href="/scan">🚩 Instant scam scan</a>
<a class="btn" href="https://wa.me/15556407358">💬 Open on WhatsApp</a></div>
<div class="sub" style="margin-top:18px;font-size:13px;text-align:center">On WhatsApp, send <b>hindi</b>, <b>marathi</b>, <b>malayalam</b>, <b>english</b> or <b>auto</b> to lock your language. <b>voice off</b> turns off audio replies.</div>
</div><script>
document.querySelectorAll(".lang").forEach(function(c){c.onclick=function(){location.href="/app?lang="+c.dataset.l+"&q="+encodeURIComponent(c.dataset.q)}});
</script></body></html>"""


@router.get("/scan", response_class=HTMLResponse)
async def scan_page():
    return HEAD.replace("TITLE", "Claim Lens - Scam scan") + r"""
<h1>Instant <em>scam</em> scan.</h1>
<div class="sub">Paste any message. We look for scam red flags such as OTP requests, fake urgency, fees and hidden links. The result is instant.</div>
<div class="panel">
<textarea id="t" placeholder="Paste the message here..."></textarea>
<button class="p" id="go">Scan for red flags</button></div>
<div id="out"></div>
<div class="ex">Try a sample:<br>
<a onclick="fill(0)">Bank KYC scam</a> · <a onclick="fill(1)">Job fee scam</a> · <a onclick="fill(2)">Free money chain</a> · <a onclick="fill(3)">Normal message</a></div>
</div><script>
const $=id=>document.getElementById(id);
const S=["Your SBI account will be blocked today. Share your OTP and call 9876543210 to update KYC immediately.",
"Congratulations! You are selected for a job. Pay a registration fee of Rs 500 within 2 hours. Apply: https://bit.ly/jobs123",
"Government is giving free Rs 5000 cashback. Forward this to 10 friends and groups to get it. Last date today.",
"Hi, the family dinner is at 8 pm on Saturday. Let me know who is coming."];
const COL={low:"#2e7d32",medium:"#ef6c00",high:"#c62828"};
const esc=s=>String(s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
function fill(i){$("t").value=S[i];$("go").click()}
$("go").onclick=async()=>{const t=$("t").value.trim();if(!t)return;
 const r=await fetch("/api/scan",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({text:t})});
 const d=await r.json();
 $("out").innerHTML='<div class="card" style="border-left-color:'+COL[d.level]+'"><div style="font-size:20px;font-weight:600">'+(d.level==="low"?"✅":"🚩")+' Scam risk: '+d.level.toUpperCase()+'</div>'+
 (d.flags.length?'<div style="margin-top:8px">'+d.flags.map(f=>"• "+esc(f)).join("<br>")+'</div>':'<div style="margin-top:8px;color:#9a9a9a">No red flags found. That does not prove the message is true, so use the checker to verify its claims.</div>')+
 '<div style="margin-top:12px"><a class="btn" href="/app">Verify its claims in the checker</a></div></div>'};
</script></body></html>"""
