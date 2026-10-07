from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

PAGE = r"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#000000"><link rel="manifest" href="/manifest.webmanifest">
<link rel="icon" href="/icon-192.png"><title>Claim Lens — Checker</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@300..700&family=Instrument+Serif:ital@1&display=swap">
<style>
html,body{background:#000 !important;color:#fff}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:Inter,system-ui,-apple-system,"Segoe UI",sans-serif;-webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility;position:relative;min-height:100dvh}
a{color:inherit;text-decoration:none}
.bg{position:fixed;inset:0;z-index:0;background:#000;overflow:hidden}
.bg video{width:100%;height:100%;object-fit:cover}
.bg::after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.72),rgba(0,0,0,.86))}
.grain{position:fixed;inset:0;z-index:100;pointer-events:none;opacity:.07;background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")}
.page{position:relative;z-index:1;max-width:560px;margin:0 auto;padding:22px 20px 56px;min-height:100dvh;display:flex;flex-direction:column}
header{display:flex;justify-content:space-between;align-items:center;margin-bottom:34px}
.logo{display:inline-flex;align-items:center;gap:9px;font-size:15.5px;font-weight:600;letter-spacing:-.03em}
.logo svg{width:22px;height:22px}
nav{display:flex;gap:6px}
nav a{display:inline-flex;align-items:center;height:34px;padding:0 14px;border-radius:7px;border:1px solid rgba(198,198,198,.55);
background:linear-gradient(105deg,#050505,#2a2a2a 48%,#4a4a4a);color:#f3f3f3;font-size:13px;letter-spacing:-.01em;transition:.35s}
nav a:hover{border-color:rgba(235,235,235,.9);background:linear-gradient(105deg,#111,#3a3a3a 45%,#6a6a6a);box-shadow:0 0 18px rgba(200,210,230,.18)}
.badge{display:inline-flex;align-items:center;gap:8px;align-self:center;margin-bottom:20px;padding:8px 14px;border-radius:5px;
background:linear-gradient(90deg,#7d7d7d,#2a2a2a 52%,#0a0a0a);color:#f2f2f2;font-size:12.5px;letter-spacing:-.01em}
.badge svg{width:16px;height:18px;fill:#fff;filter:drop-shadow(0 0 3px rgba(255,255,255,.45))}
h1{display:flex;flex-direction:column;align-items:center;text-align:center;font-weight:500;font-size:40px;letter-spacing:-.045em;line-height:1.1}
h1 em{font-family:"Instrument Serif","Times New Roman",serif;font-style:italic;font-weight:400;font-size:1.08em;letter-spacing:-.03em;color:#9a9a9a}
.sub{text-align:center;color:#9a9a9a;font-size:15px;line-height:1.55;letter-spacing:-.015em;margin:16px auto 26px;max-width:420px}
.panel{display:flex;flex-direction:column;gap:12px;padding:16px;border-radius:14px;border:1px solid rgba(198,198,198,.28);
background:linear-gradient(135deg,rgba(255,255,255,.08),rgba(0,0,0,.55) 46%,rgba(150,170,200,.07));backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);
box-shadow:inset 0 1px 0 rgba(255,255,255,.1)}
textarea{width:100%;height:130px;padding:14px;font:15.5px Inter,sans-serif;color:#fff;background:rgba(0,0,0,.55);border:1px solid rgba(255,255,255,.18);border-radius:10px;resize:vertical;outline:none}
textarea:focus{border-color:rgba(220,230,255,.7)}
textarea::placeholder{color:#777}
.row{display:flex;gap:10px;flex-wrap:wrap;align-items:center}
select,button,input[type=file]{font:13.5px Inter,sans-serif;color:#fff}
select,input[type=file]{padding:10px 12px;border-radius:8px;border:1px solid rgba(198,198,198,.4);background:rgba(0,0,0,.5)}
input[type=file]{flex:1;min-width:0;font-size:13px}
select{flex:1}
input[type=file]::file-selector-button{margin-right:10px;padding:6px 10px;border-radius:6px;border:1px solid rgba(198,198,198,.45);background:linear-gradient(105deg,#050505,#2a2a2a 48%,#4a4a4a);color:#f3f3f3;font:12.5px Inter,sans-serif;cursor:pointer}
button{position:relative;overflow:hidden;cursor:pointer;height:40px;padding:0 16px;border-radius:6px;font-weight:500;letter-spacing:-.02em;
border:1px solid rgba(198,198,198,.5);background:linear-gradient(135deg,rgba(255,255,255,.12),rgba(0,0,0,.5) 46%,rgba(150,170,200,.1));transition:.35s}
button:hover{border-color:rgba(220,230,255,.85);box-shadow:0 0 22px rgba(170,200,255,.25)}
button:disabled{opacity:.5;cursor:default}
button.p{width:100%;height:44px;font-size:14.5px;color:#111;border:1px solid #fff;background:linear-gradient(180deg,#fff,#e7e7e7 48%,#cfcfcf);box-shadow:inset 0 1px 0 rgba(255,255,255,.95)}
button.p:hover{background:linear-gradient(180deg,#fff,#f3f6ff 42%,#d5def2);box-shadow:inset 0 1px 0 #fff,0 0 26px rgba(186,208,255,.4)}
#mic{width:100%}
#st{color:#9a9a9a;font-size:13.5px;text-align:center;min-height:18px}
.card{background:rgba(8,8,8,.82);border:1px solid rgba(255,255,255,.14);border-left:6px solid #777;border-radius:12px;padding:16px;margin:16px 0 0}
.lb{font-size:20px;font-weight:600;letter-spacing:-.02em}.cl{color:#bbb;margin:6px 0 10px;font-size:15px}.ex{line-height:1.55;font-size:15px}.lo{margin-top:10px;line-height:1.6;font-size:16.5px}
.card .row{margin-top:12px}.card button{height:36px;font-size:13px;padding:0 12px}
.ev{background:rgba(255,255,255,.06);border-radius:8px;padding:10px;margin-top:8px;font-size:13px;color:#ccc}
.ev a{color:#8ab4ff;word-break:break-all}
.tag{display:inline-block;font-size:12px;background:rgba(255,255,255,.1);border-radius:10px;padding:2px 9px;margin-left:6px;color:#ccc;font-weight:400}
.ext{background:rgba(8,8,8,.7);border:1px dashed rgba(255,255,255,.22);border-radius:10px;padding:12px;color:#aaa;font-size:13.5px;margin-top:16px}
.hint{color:#777;font-size:12.5px;margin-top:auto;padding-top:34px;line-height:1.6;text-align:center}
@media(max-width:420px){h1{font-size:34px}header{margin-bottom:26px}}
</style></head><body>
<div class="grain"></div>
<div class="bg"><video autoplay muted loop playsinline preload="auto" src="https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260818_072341_50851634-bbc3-4c33-9acc-7647d4db44aa.mp4"></video></div>
<div class="page">
<header><a class="logo" href="/"><svg viewBox="0 0 24 24" fill="currentColor"><g transform="rotate(-30 12 12)"><circle cx="7.3" cy="3.2" r="1.45"/><rect x="5.5" y="4.7" width="3.6" height="14.6" rx="1.8"/><rect x="14.9" y="4.7" width="3.6" height="14.6" rx="1.8"/><circle cx="16.7" cy="20.8" r="1.45"/></g></svg>Claim Lens</a>
<nav><a href="/">Home</a><a href="/dashboard">Ledger</a><a href="/languages">Languages</a><a href="/privacy">Privacy</a></nav></header>
<div class="badge"><svg viewBox="0 0 24 24"><path d="M12 2.6C12.55 2.6 12.88 3.15 13.08 4.7c.62 4.7 1.52 5.6 6.22 6.22 1.55.2 2.1.53 2.1 1.08s-.55.88-2.1 1.08c-4.7.62-5.6 1.52-6.22 6.22-.2 1.55-.53 2.1-1.08 2.1s-.88-.55-1.08-2.1c-.62-4.7-1.52-5.6-6.22-6.22C3.15 12.88 2.6 12.55 2.6 12s.55-.88 2.1-1.08c4.7-.62 5.6-1.52 6.22-6.22C11.12 3.15 11.45 2.6 12 2.6Z"/></svg>Fact-checking for every forward</div>
<h1><span>Check any</span><em>forward</em><span>before you share it.</span></h1>
<div class="sub">Paste text or a link, upload a screenshot, voice note or PDF, or record your voice.</div>
<div class="panel">
<textarea id="t" placeholder="Paste the forwarded message or a link..."></textarea>
<input type="file" id="f" accept="image/*,audio/*,application/pdf">
<button id="mic">🎤 Record</button>
<div class="row"><select id="l"><option value="">Auto language</option><option value="en">English</option><option value="hi">हिन्दी</option><option value="mr">मराठी</option><option value="ml">മലയാളം</option></select></div>
<button class="p" id="go">Check</button>
<div id="st"></div>
</div>
<div id="out"></div>
<div class="hint">📲 On Android, open this page in Chrome and choose <b>Add to Home screen</b>. Claim Lens then appears in your <b>Share</b> menu, so you can check any message before you forward it.</div>
</div><script>
const $=id=>document.getElementById(id);
const EMO={"Verified":"✅","False":"❌","Outdated":"⏳","Partly supported":"⚠️","Cannot be confirmed":"❓"};
const COL={"Verified":"#2e7d32","False":"#c62828","Outdated":"#ef6c00","Partly supported":"#f9a825","Cannot be confirmed":"#757575"};
const esc=s=>String(s==null?"":s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
let cur=null,curText="";
async function call(url,opts){const r=await fetch(url,opts);let d=null;try{d=await r.json()}catch(e){}if(!r.ok)throw new Error((d&&d.detail)||"Error");return d}
async function go(p){$("go").disabled=true;$("st").textContent="Checking… up to a minute";$("out").innerHTML="";
 try{cur=await p;render(cur);$("st").textContent=""}catch(e){$("st").textContent="Error: "+e.message}$("go").disabled=false}
function sendText(t){curText=t;return call("/api/check",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({text:t,lang:$("l").value||null})})}
function sendFile(f){const fd=new FormData();fd.append("file",f);if($("l").value)fd.append("lang",$("l").value);curText=f.name;return call("/api/check-file",{method:"POST",body:fd})}
$("go").onclick=()=>{const f=$("f").files[0],t=$("t").value.trim();if(f)go(sendFile(f));else if(t)go(sendText(t));else $("st").textContent="Add text, a link or a file first."};
let mr,ch=[];
$("mic").onclick=async()=>{
 if(mr&&mr.state==="recording"){mr.stop();return}
 try{const s=await navigator.mediaDevices.getUserMedia({audio:true});mr=new MediaRecorder(s);ch=[];
  mr.ondataavailable=e=>ch.push(e.data);
  mr.onstop=()=>{s.getTracks().forEach(x=>x.stop());$("mic").textContent="🎤 Record";const b=new Blob(ch,{type:mr.mimeType});
   const ext=/mp4/.test(b.type)?"m4a":"webm";go(sendFile(new File([b],"voice."+ext,{type:b.type})))};
  mr.start();$("mic").textContent="⏹ Stop"}catch(e){$("st").textContent="Microphone not available"}};
function render(d){let h="";
 if(d.extracted_text)h+=`<div class="ext"><b>Read from your input:</b><br>${esc(d.extracted_text)}</div>`;
 if(d.redflags&&d.redflags.level!=="low"&&d.redflags.flags.length)h+=`<div class="card" style="border-left-color:#ef6c00"><div class="lb">🚩 Scam risk: ${esc(d.redflags.level.toUpperCase())}</div><div class="ex">${d.redflags.flags.map(f=>"• "+esc(f)).join("<br>")}</div></div>`;
 if(!d.claims.length)h+=`<div class="card">No factual claim found to check.</div>`;
 d.claims.forEach((c,i)=>{
  const ev=(c.evidence||[]).map(e=>`<div class="ev">📌 "${esc(e.quote)}"<br><small>${esc(e.source)} • ${esc(e.date||"—")}</small><br><a href="${esc(e.url)}" target="_blank" rel="noopener">${esc(e.url)}</a></div>`).join("");
  const conf=c.label==="Cannot be confirmed"?"":` <span class="tag">${Math.round(c.confidence*100)}% confident</span>`;
  const rep=d.repeat>1?`<span class="tag">♻️ checked ${d.repeat} times</span>`:"";
  const loc=c.explanation_local?`<div class="lo">${esc(c.explanation_local)}</div>`:"";
  const unc=c.label==="Cannot be confirmed"?`<button data-a="human" data-i="${i}">👤 Ask a human</button>`:"";
  h+=`<div class="card" style="border-left-color:${COL[c.label]}"><div class="lb">${EMO[c.label]} ${esc(c.label)}${conf}${rep}</div>
  <div class="cl">${esc(c.claim_local||c.text)}</div><div class="ex">${esc(c.explanation_en)}</div>${loc}
  <div class="row"><button data-a="listen" data-i="${i}">🔊 Listen</button><button data-a="card" data-i="${i}">🖼️ Share card</button><button data-a="copy" data-i="${i}">📋 Copy</button>${unc}</div>${ev}</div>`});
 $("out").innerHTML=h}
$("out").onclick=async e=>{const b=e.target.closest("button");if(!b)return;const c=cur.claims[+b.dataset.i],a=b.dataset.a,tl=cur.target_language||"en";
 try{
 if(a==="listen"){const loc=c.explanation_local&&tl!=="en";const r=await fetch("/tts",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({text:loc?c.explanation_local:c.explanation_en,lang:loc?tl:"en"})});if(!r.ok)throw 0;new Audio(URL.createObjectURL(await r.blob())).play()}
 if(a==="card"){const r=await fetch("/api/card",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({claim:c,lang:tl})});if(!r.ok)throw 0;const u=URL.createObjectURL(await r.blob());const x=document.createElement("a");x.href=u;x.download="claim-lens-card.png";x.click()}
 if(a==="copy"){await navigator.clipboard.writeText(`${EMO[c.label]} ${c.label}: ${c.text}\n${c.explanation_local||c.explanation_en}\nChecked with Claim Lens`);b.textContent="✅ Copied"}
 if(a==="human"){await call("/api/human",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({text:c.text})});b.textContent="✅ Sent to a human reviewer"}
 }catch(err){alert("That did not work, please try again")}};
if("serviceWorker"in navigator)navigator.serviceWorker.register("/sw.js").catch(()=>{});
const q=new URLSearchParams(location.search);const sh=[q.get("title"),q.get("text"),q.get("url")].filter(Boolean).join("\n").trim();
if(q.get("lang")){$("l").value=q.get("lang")}
if(q.get("q")){$("t").value=q.get("q");go(sendText(q.get("q")))}
const sid=q.get("sid");if(sid){go(call("/api/share/"+sid))}
if(sh){$("t").value=sh;go(sendText(sh))}
</script></body></html>"""


@router.get("/app", response_class=HTMLResponse)
async def page():
    return PAGE
