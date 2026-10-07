import json
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from core import ledger

router = APIRouter()


@router.get("/api/stats")
async def stats():
    d = ledger._load()
    labels, rows = {}, []
    for e in d.values():
        cl = (e.get("result") or {}).get("claims") or []
        if not cl:
            continue
        lab = cl[0]["label"]
        labels[lab] = labels.get(lab, 0) + e["count"]
        rows.append({"claim": cl[0]["text"], "label": lab, "count": e["count"], "ts": e["ts"]})
    try:
        human = json.load(open("data/human_queue.json"))
    except Exception:
        human = []
    rows.sort(key=lambda r: (-r["count"], -r["ts"]))
    return {"total": sum(e["count"] for e in d.values()), "unique": len(d),
            "labels": labels, "top": rows[:8],
            "recent": sorted(rows, key=lambda r: -r["ts"])[:8], "human": human[-8:]}


PAGE = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Claim Lens Ledger</title>
<style>
html,body{background:#000;color:#fff}
body{font-family:system-ui,sans-serif;margin:0}
.w{max-width:900px;margin:0 auto;padding:20px}
nav{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:22px}
nav a{padding:8px 14px;border-radius:7px;border:1px solid rgba(198,198,198,.55);background:linear-gradient(105deg,#050505,#2a2a2a 48%,#4a4a4a);color:#f3f3f3;font-size:13px;text-decoration:none}
h1{margin:0 0 6px}.sub{color:#9a9a9a;margin-bottom:18px}
.g{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin-bottom:18px}
.k{background:#111;border:1px solid #222;border-radius:12px;padding:14px}
.k b{font-size:28px;display:block}
.c{background:#111;border:1px solid #222;border-radius:12px;padding:16px;margin-bottom:16px}
.r{display:flex;justify-content:space-between;gap:12px;padding:8px 0;border-bottom:1px solid #222}
.r:last-child{border:0}.t{font-size:13px;color:#fff;padding:2px 8px;border-radius:10px;white-space:nowrap}
.bar{height:14px;border-radius:7px;margin:6px 0}

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

.r{display:flex;align-items:flex-start;justify-content:space-between;gap:14px}
.r > span:first-child{flex:1 1 auto;min-width:0;overflow-wrap:anywhere;line-height:1.45}
.r > span:last-child{flex:0 0 auto;white-space:nowrap;display:inline-flex;align-items:center;gap:8px}
.t{white-space:nowrap}
@media(max-width:600px){
 .w{padding:14px}
 nav{gap:5px}
 nav a{padding:7px 11px;font-size:12.5px}
 h1{font-size:26px}
 .g{grid-template-columns:1fr 1fr}
 .k b{font-size:24px}
 .r{flex-direction:column;align-items:flex-start;gap:6px}
 .r > span:last-child{white-space:normal}
}

nav{display:flex;justify-content:center;flex-wrap:wrap;gap:6px;padding:6px;margin:0 auto 26px;width:fit-content;max-width:100%;
 border:1px solid rgba(198,198,198,.28);border-radius:12px;background:rgba(255,255,255,.04)}
nav a{display:inline-flex;align-items:center;justify-content:center;height:36px;padding:0 16px;border-radius:8px;border:1px solid transparent;
 background:transparent;color:#cfcfcf;font-size:13.5px;letter-spacing:-.01em;transition:.25s}
nav a:hover{background:rgba(255,255,255,.1);color:#fff}
nav a.on{background:linear-gradient(180deg,#fff,#d6d6d6);color:#111;font-weight:500}
h1,.sub{text-align:center}
@media(max-width:600px){
 nav{display:grid;grid-template-columns:repeat(3,1fr);width:100%;gap:5px;padding:5px}
 nav a{height:38px;padding:0 6px;font-size:13px}
}
</style></head><body><div class="w">
<nav><a href="/">Home</a><a href="/app">Checker</a><a href="/dashboard" class="on">Ledger</a><a href="/languages">Languages</a><a href="/scan">Scan</a><a href="/email">Email</a><a href="/privacy">Privacy</a></nav>
<h1> Claim Lens Ledger</h1>
<div class="sub">Every checked claim becomes a reusable public record.</div>
<div class="g" id="k"></div>
<div class="c"><b>Verdicts</b><div id="b"></div></div>
<div class="c"><b>Most re-checked claims</b><div id="top"></div></div>
<div class="c"><b>Latest checks</b><div id="rec"></div></div>
<div class="c"><b>Sent to human fact-checkers</b><div id="hum"></div></div>
</div><script>
const COL={"Verified":"#2e7d32","False":"#c62828","Outdated":"#ef6c00","Partly supported":"#f9a825","Cannot be confirmed":"#757575"};
const esc=s=>String(s==null?"":s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const row=r=>'<div class="r"><span>'+esc(r.claim)+'</span><span><span class="t" style="background:'+COL[r.label]+'">'+esc(r.label)+'</span> x'+r.count+'</span></div>';
async function load(){
 const d=await (await fetch("/api/stats")).json();
 document.getElementById("k").innerHTML=
  '<div class="k"><b>'+d.total+'</b>checks served</div><div class="k"><b>'+d.unique+'</b>unique claims</div>'+
  '<div class="k"><b>'+(d.total-d.unique)+'</b>repeat checks (free)</div><div class="k"><b>'+d.human.length+'</b>human requests</div>';
 const mx=Math.max(1,...Object.values(d.labels));
 document.getElementById("b").innerHTML=Object.entries(d.labels).map(([l,n])=>'<div>'+esc(l)+' ('+n+')<div class="bar" style="width:'+(n/mx*100)+'%;background:'+COL[l]+'"></div></div>').join("")||"No data yet";
 document.getElementById("top").innerHTML=d.top.map(row).join("")||"No data yet";
 document.getElementById("rec").innerHTML=d.recent.map(row).join("")||"No data yet";
 document.getElementById("hum").innerHTML=d.human.map(h=>'<div class="r"><span>'+esc(h.text)+'</span><span>'+esc(h.who)+'</span></div>').join("")||"None yet";
}
load();setInterval(load,5000);
</script></body></html>"""


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard():
    return PAGE
