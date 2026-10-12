from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from core.redflags import scan

router = APIRouter()


class ScanIn(BaseModel):
    text: str


@router.post("/api/scan")
async def api_scan(b: ScanIn):
    from core.ingest import find_url, url_to_text
    text = b.text.strip()
    u = find_url(text)
    extra = {}
    scan_text = text
    if u:
        extra["link"] = u
        if any(x in u for x in ("mail.google.com", "instagram.com", "facebook.com")):
            extra["note"] = "That site is private, so only the link itself was checked. Paste the post text or a screenshot in the Checker for the claims."
        else:
            try:
                page = await url_to_text(u)
            except Exception:
                page = ""
            if page:
                scan_text = text + "\n" + page
                extra["read"] = page[:300]
            else:
                extra["note"] = "I could not open that link, so only the link itself was checked."
        r = scan(scan_text)
    if u:
        try:
            import asyncio
            import urlcheck
            m = await asyncio.to_thread(urlcheck.scan_url, u)
        except Exception:
            m = None
        if m:
            extra["url_ml"] = m
            p = m["phishing_probability"]
            pct = round(p * 100)
            if p >= 0.8:
                r["flags"] = r["flags"] + [f"The link's web address looks like phishing (URL model: {pct}% likely)"]
                r["level"] = "high"
            elif p >= 0.5:
                r["flags"] = r["flags"] + [f"The link's web address looks somewhat suspicious (URL model: {pct}%)"]
                if r["level"] == "low":
                    r["level"] = "medium"
    r.update(extra)
    return r


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

@media(max-width:600px){
 header{flex-direction:column;align-items:flex-start !important;gap:12px}
 nav{flex-wrap:wrap}
 nav a{height:32px !important;padding:0 11px !important;font-size:12.5px !important}
 h1{font-size:30px !important}
 .page,.w{padding-left:14px !important;padding-right:14px !important}
 textarea{height:110px !important}
 .card .row{gap:6px}
 .r{flex-direction:column;gap:4px}
 img,video{max-width:100%}
}
html,body{overflow-x:hidden}
</style></head><body><div class="page">
<header><a class="logo" href="/"> Claim Lens</a>
<nav><a href="/app">Checker</a><a href="/dashboard">Ledger</a><a href="/languages">Languages</a><a href="/privacy">Privacy</a></nav></header>
"""


@router.get("/languages", response_class=HTMLResponse)
async def languages():
    return r"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#000000"><title>Claim Lens - Languages</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@300..700&family=Instrument+Serif:ital@1&display=swap">
<style>
html,body{background:#000 !important;color:#fff}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:Inter,system-ui,sans-serif;-webkit-font-smoothing:antialiased;min-height:100dvh;position:relative;overflow-x:hidden}
a{color:inherit;text-decoration:none}
.bg{position:fixed;inset:0;z-index:0;background:#000;overflow:hidden}
.bg video{width:100%;height:100%;object-fit:cover}
.bg::after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.72),rgba(0,0,0,.86))}
.page{position:relative;z-index:1;min-height:100dvh;display:flex;flex-direction:column;padding:18px 40px 22px}
header{display:flex;justify-content:space-between;align-items:center;gap:14px;margin-bottom:18px}
.logo{font-size:15.5px;font-weight:600;letter-spacing:-.03em;white-space:nowrap}
nav{display:flex;flex-wrap:wrap;justify-content:flex-end;gap:6px;padding:6px;border:1px solid rgba(198,198,198,.28);border-radius:12px;background:rgba(255,255,255,.04)}
nav a{display:inline-flex;align-items:center;justify-content:center;height:34px;padding:0 15px;border-radius:8px;color:#cfcfcf;font-size:13.5px;transition:.25s}
nav a:hover{background:rgba(255,255,255,.1);color:#fff}
nav a.on{background:linear-gradient(180deg,#fff,#d6d6d6);color:#111;font-weight:500}
main{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;max-width:900px;width:100%;margin:0 auto}
h1{text-align:center;font-weight:500;font-size:36px;letter-spacing:-.045em;line-height:1.1}
h1 em{font-family:"Instrument Serif",serif;font-style:italic;font-weight:400;color:#9a9a9a}
.sub{text-align:center;color:#9a9a9a;font-size:14.5px;line-height:1.5;margin:10px auto 18px;max-width:460px}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;width:100%}
.lang{text-align:center;cursor:pointer;padding:14px 12px;border-radius:12px;border:1px solid rgba(198,198,198,.28);
background:linear-gradient(135deg,rgba(255,255,255,.08),rgba(0,0,0,.55) 46%,rgba(150,170,200,.07));backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);transition:.3s}
.lang:hover{border-color:#fff;box-shadow:0 0 22px rgba(170,200,255,.25)}
.lang b{display:block;font-size:18px}
.sample{color:#bbb;font-size:13px;margin:6px 0 8px;line-height:1.45}
.tryit{display:inline-block;font-size:12px;padding:4px 12px;border-radius:12px;background:rgba(255,255,255,.12);color:#ddd}
.actions{display:flex;gap:10px;margin-top:14px;width:100%}
.btn{flex:1;display:inline-flex;align-items:center;justify-content:center;height:42px;padding:0 12px;border-radius:6px;font-size:13.5px;font-weight:500;
border:1px solid rgba(198,198,198,.5);background:linear-gradient(135deg,rgba(255,255,255,.12),rgba(0,0,0,.5) 46%,rgba(150,170,200,.1));color:#fff;text-align:center}
.btn:hover{border-color:rgba(220,230,255,.85);box-shadow:0 0 22px rgba(170,200,255,.25)}
.btn.p{color:#111;border-color:#fff;background:linear-gradient(180deg,#fff,#e7e7e7 48%,#cfcfcf)}
.hint{text-align:center;color:#777;font-size:12.5px;margin-top:12px;line-height:1.5}
@media(max-width:900px){.page{padding:16px 16px 28px}header{flex-direction:column;align-items:flex-start}nav{width:100%;display:grid;grid-template-columns:repeat(3,1fr);gap:5px}nav a{height:38px;padding:0 6px;font-size:13px}}
@media(max-width:600px){h1{font-size:30px}.grid{grid-template-columns:1fr}.actions{flex-direction:column}main{justify-content:flex-start}}
</style></head><body>
<div class="bg"><video autoplay muted loop playsinline preload="auto" src="https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260818_072341_50851634-bbc3-4c33-9acc-7647d4db44aa.mp4"></video></div>
<div class="page">
<header><a class="logo" href="/"> Claim Lens</a>
<nav><a href="/">Home</a><a href="/app">Checker</a><a href="/dashboard">Ledger</a><a href="/languages" class="on">Languages</a><a href="/scan">Scan</a><a href="/email">Email</a><a href="/privacy">Privacy</a></nav></header>
<main>
<h1>Your <em>language</em>, your verdict.</h1>
<div class="sub">Tap a language to try it. We check a sample claim and answer in that language, with a voice reply.</div>
<div class="grid">
<div class="lang" data-l="hi" data-q="गरम पानी पीने से कोरोना ठीक हो जाता है।"><b>हिन्दी · Hindi</b><div class="sample">गरम पानी पीने से कोरोना ठीक हो जाता है।</div><span class="tryit">Try in Hindi →</span></div>
<div class="lang" data-l="mr" data-q="दर पंधरा मिनिटांनी गरम पाणी प्यायल्याने कोविड बरा होतो."><b>मराठी · Marathi</b><div class="sample">दर पंधरा मिनिटांनी गरम पाणी प्यायल्याने कोविड बरा होतो.</div><span class="tryit">Try in Marathi →</span></div>
<div class="lang" data-l="ml" data-q="ചൂടുവെള്ളം കുടിച്ചാൽ കോവിഡ് മാറും."><b>മലയാളം · Malayalam</b><div class="sample">ചൂടുവെള്ളം കുടിച്ചാൽ കോവിഡ് മാറും.</div><span class="tryit">Try in Malayalam →</span></div>
<div class="lang" data-l="en" data-q="Drinking hot water every 15 minutes cures COVID-19"><b>English</b><div class="sample">Drinking hot water every 15 minutes cures COVID-19</div><span class="tryit">Try in English →</span></div>
</div>
<div class="actions"><a class="btn p" href="/app"> Web checker</a><a class="btn" href="/scan"> Scam scan</a><a class="btn" href="https://wa.me/15556407358"> WhatsApp</a></div>
<div class="hint">On WhatsApp, send <b>hindi</b>, <b>marathi</b>, <b>malayalam</b>, <b>english</b> or <b>auto</b> to lock your language. <b>voice off</b> turns off audio replies.</div>
</main></div>
<script>document.querySelectorAll(".lang").forEach(function(c){c.onclick=function(){location.href="/app?lang="+c.dataset.l+"&q="+encodeURIComponent(c.dataset.q)}});</script>
</body></html>"""


@router.get("/scan", response_class=HTMLResponse)
async def scan_page():
    return r"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#000000"><title>Claim Lens - Scam scan</title>
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
main{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;max-width:640px;width:100%;margin:0 auto}
h1{text-align:center;font-weight:500;font-size:38px;letter-spacing:-.045em;line-height:1.1}
h1 em{font-family:"Instrument Serif",serif;font-style:italic;font-weight:400;color:#9a9a9a}
.sub{text-align:center;color:#9a9a9a;font-size:14.5px;line-height:1.5;margin:10px auto 18px;max-width:480px}
.panel{width:100%;display:flex;flex-direction:column;gap:12px;padding:16px;border-radius:14px;border:1px solid rgba(198,198,198,.28);
background:linear-gradient(135deg,rgba(255,255,255,.08),rgba(0,0,0,.55) 46%,rgba(150,170,200,.07));backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px)}
textarea{width:100%;height:110px;padding:14px;font:15px Inter,sans-serif;color:#fff;background:rgba(0,0,0,.55);border:1px solid rgba(255,255,255,.18);border-radius:10px;resize:vertical;outline:none}
textarea:focus{border-color:rgba(220,230,255,.7)}
textarea::placeholder{color:#777}
button,.btn{font:13.5px Inter,sans-serif;cursor:pointer;height:44px;padding:0 16px;border-radius:6px;font-weight:500;border:1px solid #fff;color:#111;
background:linear-gradient(180deg,#fff,#e7e7e7 48%,#cfcfcf);display:inline-flex;align-items:center;justify-content:center}
.btn.g{color:#fff;border-color:rgba(198,198,198,.5);background:linear-gradient(135deg,rgba(255,255,255,.12),rgba(0,0,0,.5) 46%,rgba(150,170,200,.1))}
.card{width:100%;background:rgba(8,8,8,.82);border:1px solid rgba(255,255,255,.14);border-left:6px solid #777;border-radius:12px;padding:14px 16px;margin-top:14px;line-height:1.6;font-size:14.5px}
.ex{color:#9a9a9a;font-size:13px;margin-top:12px;text-align:center;line-height:1.8}
.ex a{color:#8ab4ff;cursor:pointer;text-decoration:underline}
@media(max-width:900px){.page{padding:16px 16px 28px}header{flex-direction:column;align-items:flex-start}nav{width:100%;display:grid;grid-template-columns:repeat(3,1fr);gap:5px}nav a{height:38px;padding:0 6px;font-size:13px}}
@media(max-width:600px){h1{font-size:30px}main{justify-content:flex-start}}
</style></head><body>
<div class="bg"><video autoplay muted loop playsinline preload="auto" src="https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260818_072341_50851634-bbc3-4c33-9acc-7647d4db44aa.mp4"></video></div>
<div class="page">
<header><a class="logo" href="/"> Claim Lens</a>
<nav><a href="/">Home</a><a href="/app">Checker</a><a href="/dashboard">Ledger</a><a href="/languages">Languages</a><a href="/scan" class="on">Scan</a><a href="/email">Email</a><a href="/privacy">Privacy</a></nav></header>
<main>
<h1>Instant <em>scam</em> scan.</h1>
<div class="sub">Paste a message or a link. We look for scam red flags such as OTP requests, fake urgency, fees, shortened links and risky web addresses. The result is instant.</div>
<div class="panel">
<textarea id="t" placeholder="Paste the message or link here..."></textarea>
<button id="go">Scan for red flags</button></div>
<div id="out" style="width:100%"></div>
<div class="ex">Try a sample: <a onclick="fill(0)">Bank KYC scam</a> · <a onclick="fill(1)">Job fee scam</a> · <a onclick="fill(2)">Free money chain</a> · <a onclick="fill(3)">Short link</a> · <a onclick="fill(4)">Normal message</a></div>
</main></div>
<script>
const $=id=>document.getElementById(id);
const S=["Your SBI account will be blocked today. Share your OTP and call 9876543210 to update KYC immediately.",
"Congratulations! You are selected for a job. Pay a registration fee of Rs 500 within 2 hours. Apply: https://bit.ly/jobs123",
"Government is giving free Rs 5000 cashback. Forward this to 10 friends and groups to get it. Last date today.",
"https://bit.ly/claim-your-prize",
"Hi, the family dinner is at 8 pm on Saturday. Let me know who is coming."];
const COL={low:"#2e7d32",medium:"#ef6c00",high:"#c62828"};
const esc=s=>String(s==null?"":s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
function fill(i){$("t").value=S[i];$("go").click()}
$("go").onclick=async()=>{const t=$("t").value.trim();if(!t)return;
 $("go").disabled=true;$("go").textContent="Scanning...";
 try{
 const r=await fetch("/api/scan",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({text:t})});
 const d=await r.json();
 $("out").innerHTML='<div class="card" style="border-left-color:'+COL[d.level]+'"><div style="font-size:20px;font-weight:600">'+(d.level==="low"?"":"")+' Scam risk: '+d.level.toUpperCase()+'</div>'+
 (d.link?'<div style="color:#9a9a9a;font-size:13px;margin-top:4px">Link: '+esc(d.link)+'</div>':'')+
 (d.flags.length?'<div style="margin-top:8px">'+d.flags.map(f=>"• "+esc(f)).join("<br>")+'</div>':'<div style="margin-top:8px;color:#9a9a9a">No red flags found. That does not prove it is true, so verify its claims in the checker.</div>')+
 (d.note?'<div style="margin-top:8px;color:#e0b060;font-size:13px">'+esc(d.note)+'</div>':'')+
 (d.read?'<div style="margin-top:8px;color:#9a9a9a;font-size:13px">Page text read: '+esc(d.read)+'...</div>':'')+
 (d.url_ml?(LINK=d.link,'<div id="deep" style="margin-top:8px;color:#9a9a9a;font-size:13px">URL model: '+Math.round(d.url_ml.phishing_probability*100)+'% phishing · <a style="color:#8ab4ff;cursor:pointer" onclick="deep()">Deep check</a></div>'):'')+
 '<div style="margin-top:12px"><a class="btn g" href="/app">Verify its claims in the checker</a></div></div>';
 }catch(e){$("out").innerHTML='<div class="card">Something went wrong, please try again.</div>'}
 $("go").disabled=false;$("go").textContent="Scan for red flags"};
 let LINK="";
async function deep(){const o=$("deep");o.textContent="Checking WHOIS, DNS and VirusTotal...";
 try{const r=await fetch("/api/url-enrich",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({url:LINK})});
 const d=await r.json();const h=d.holistic;
 o.innerHTML="Overall: <b>"+esc(h.label)+"</b> ("+h.score+"/100) · sources: "+esc(h.sources_used.join(", "))+(h.overrides.length?"<br>"+h.overrides.map(esc).join("<br>"):"");
 }catch(e){o.textContent="Deep check failed."}}

 const q0=new URLSearchParams(location.search).get("q");if(q0){$("t").value=q0;$("go").click()}
</script></body></html>"""