from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

PAGE = r"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>Claim Lens — Fact-checking for every forward</title>
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='white'%3E%3Cg transform='rotate(-30 12 12)'%3E%3Ccircle cx='7.3' cy='3.2' r='1.45'/%3E%3Crect x='5.5' y='4.7' width='3.6' height='14.6' rx='1.8'/%3E%3Crect x='14.9' y='4.7' width='3.6' height='14.6' rx='1.8'/%3E%3Ccircle cx='16.7' cy='20.8' r='1.45'/%3E%3C/g%3E%3C/svg%3E">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,100..900&family=Instrument+Serif:ital@1&display=swap">
<style>
html,body{background:#000000 !important;color:#ffffff}
*{box-sizing:border-box;margin:0;padding:0}
:root{--bg:#000;--text:#fff;--muted:#9a9a9a;--stat:#d8d8d8;--border:rgba(255,255,255,.16);
--logo:15.5px;--logo-mark:22px;--nav:14px;--nav-h:40px;--btn:13.5px;--btn-h:40px;--hero-btn-h:42px;
--h1:48px;--lede:15.5px;--badge:12.5px;--stat-size:13.5px;--header-y:22px;--header-x:40px;
--stats-x:72px;--stats-y:36px;--hero-gap:85px;--copy-max:860px;--lede-max:470px}
html,body{background:#000000;background:var(--bg);color:#fff;color:var(--text)}
html{scroll-behavior:smooth}
body{font-family:"Inter",system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
-webkit-font-smoothing:antialiased;-moz-osx-font-smoothing:grayscale;text-rendering:optimizeLegibility;overflow-x:hidden;position:relative}
a{color:inherit;text-decoration:none}button{font-family:inherit}
.hero-photo{position:fixed;inset:0;z-index:0;overflow:hidden;background:#000}
.hero-photo video{width:100%;height:100%;object-fit:cover;opacity:1}
.grain{position:fixed;inset:0;z-index:100;pointer-events:none;opacity:.07;
background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")}
.page{position:relative;z-index:1;display:grid;grid-template-rows:auto 1fr auto;min-height:100vh;min-height:100dvh}
.header{display:grid;grid-template-columns:1fr auto 1fr;align-items:center;padding:var(--header-y) var(--header-x) 10px;z-index:50;position:relative}
.logo{display:inline-flex;align-items:center;gap:9px;justify-self:start;font-size:var(--logo);font-weight:600;letter-spacing:-.03em;color:#fff}
.logo svg{width:var(--logo-mark);height:var(--logo-mark)}
.logo-suffix{font-weight:400}
#site-nav{display:flex;align-items:center;gap:8px;justify-self:center}
#site-nav a{position:relative;overflow:hidden;display:inline-flex;align-items:center;height:var(--nav-h);padding:0 18px;border-radius:7px;
border:1px solid rgba(198,198,198,.55);background:linear-gradient(105deg,#050505 0%,#2a2a2a 48%,#4a4a4a 100%);
color:#f3f3f3;font-size:var(--nav);font-weight:400;letter-spacing:-.01em;white-space:nowrap;
transition:background .35s ease,border-color .35s ease,box-shadow .35s ease}
#site-nav a::before{content:"";position:absolute;inset:0;background:linear-gradient(115deg,transparent 30%,rgba(255,255,255,.16) 50%,transparent 70%);transform:translateX(-120%);transition:transform .6s ease}
#site-nav a:hover{border-color:rgba(235,235,235,.9);background:linear-gradient(105deg,#111 0%,#3a3a3a 45%,#6a6a6a 100%);box-shadow:0 0 18px rgba(200,210,230,.18)}
#site-nav a:hover::before{transform:translateX(120%)}
.header-cta{justify-self:end}
.burger{display:none;width:42px;height:42px;border-radius:6px;border:1px solid var(--border);background:rgba(8,8,8,.55);z-index:60;
place-items:center;align-content:center;gap:5px;cursor:pointer;margin-left:8px}
.burger span{display:block;width:16px;height:1.5px;border-radius:1px;background:#fff;transition:transform .25s,opacity .2s}
.burger:hover{border-color:rgba(255,255,255,.32);background:rgba(255,255,255,.05)}
body.menu-open .burger span:nth-child(1){transform:translateY(6.5px) rotate(45deg)}
body.menu-open .burger span:nth-child(2){opacity:0}
body.menu-open .burger span:nth-child(3){transform:translateY(-6.5px) rotate(-45deg)}
.menu-backdrop{display:none}
.btn{position:relative;isolation:isolate;overflow:hidden;display:inline-flex;align-items:center;justify-content:center;height:var(--btn-h);padding:0 16px;border-radius:6px;
font-size:var(--btn);font-weight:500;letter-spacing:-.02em;line-height:1;white-space:nowrap;cursor:pointer;
transition:background .35s,border-color .35s,box-shadow .35s,color .35s,filter .35s}
.btn::after{content:"";position:absolute;inset:0;z-index:-1;background:linear-gradient(115deg,transparent 20%,rgba(255,255,255,.45) 48%,transparent 76%);transform:translateX(-130%);transition:transform .65s ease}
.btn:hover::after{transform:translateX(130%)}
.btn-solid{background:linear-gradient(180deg,#fff 0%,#e7e7e7 48%,#cfcfcf 100%);color:#111;border:1px solid #fff;box-shadow:inset 0 1px 0 rgba(255,255,255,.95)}
.btn-solid:hover{background:linear-gradient(180deg,#fff 0%,#f3f6ff 42%,#d5def2 100%);border-color:#f2f6ff;box-shadow:inset 0 1px 0 #fff,0 0 22px rgba(186,208,255,.35),0 8px 18px rgba(255,255,255,.12)}
.hero-actions .btn-solid:hover{box-shadow:inset 0 1px 0 #fff,0 0 26px rgba(186,208,255,.4),0 8px 18px rgba(255,255,255,.14)}
.btn-ghost{background:linear-gradient(135deg,rgba(255,255,255,.12),rgba(0,0,0,.5) 46%,rgba(150,170,200,.1));color:#fff;border:1px solid rgba(198,198,198,.55);
box-shadow:inset 0 1px 0 rgba(255,255,255,.12);backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px)}
.btn-ghost:hover{background:linear-gradient(135deg,rgba(210,225,255,.18),rgba(0,0,0,.35) 48%,rgba(180,195,220,.16));border-color:rgba(220,230,255,.8);
box-shadow:inset 0 1px 0 rgba(255,255,255,.22),0 0 24px rgba(170,200,255,.28)}
.hero-actions .btn{height:var(--hero-btn-h);padding:0 18px}
.hero{display:flex;align-items:flex-end;justify-content:center;padding:8px 24px var(--hero-gap);min-height:0}
.hero-copy{position:relative;z-index:1;display:flex;flex-direction:column;align-items:center;text-align:center;max-width:var(--copy-max);width:100%}
.badge{display:inline-flex;align-items:center;gap:8px;margin-bottom:22px;padding:9px 15px;border:0;border-radius:5px;
background:linear-gradient(90deg,#7d7d7d 0%,#2a2a2a 52%,#0a0a0a 100%);color:#f2f2f2;font-size:var(--badge);font-weight:400;letter-spacing:-.01em}
.badge-star{width:18px;height:20px;fill:#fff;filter:drop-shadow(0 0 3px rgba(255,255,255,.45))}
h1{display:flex;flex-direction:column;align-items:center;font-weight:500;font-size:var(--h1);letter-spacing:-.045em;line-height:1.12;color:#fff}
.headline-line{display:block;overflow:hidden;padding:.06em .15em .14em}
h1 em{font-family:"Instrument Serif","Times New Roman",Times,serif;font-style:italic;font-weight:400;font-size:1.08em;letter-spacing:-.03em;color:#9a9a9a}
.lede{max-width:var(--lede-max);margin-top:18px;color:#9a9a9a;font-size:var(--lede);font-weight:400;line-height:1.55;letter-spacing:-.015em}
.hero-actions{display:flex;flex-wrap:wrap;justify-content:center;gap:10px;margin-top:26px}
.stats{display:flex;align-items:center;justify-content:space-between;gap:24px;padding:0 var(--stats-x) var(--stats-y);padding-bottom:max(var(--stats-y),env(safe-area-inset-bottom));color:#d8d8d8}
.stat{display:inline-flex;align-items:center;gap:14px;font-size:var(--stat-size);letter-spacing:-.015em;white-space:nowrap}
.stat svg{width:20px;height:20px;flex:none}.stat .stat-icon-wide{width:38px;height:21px}
.stat b{font-weight:600;color:#fff}
/* entrance motion */
.appear{opacity:1;animation-duration:1.05s;animation-fill-mode:both;animation-timing-function:cubic-bezier(.16,1,.3,1);animation-delay:var(--d,.08s)}
.appear--scale{animation-name:in-scale}.appear--soft{animation-name:in-soft}.appear--mask{animation-name:in-mask}
.appear--pop{animation-name:in-pop}.appear--btn{animation-name:in-btn}.appear--side{animation-name:in-side}.appear--stat{animation-name:in-stat}
.lede.appear{animation-duration:1.25s}
.badge-star{animation:in-star .9s .28s both}
h1 em{animation:in-em 1.2s .72s both}
.is-in{animation:none !important;opacity:1;transform:none;clip-path:none;filter:none}
@keyframes in-scale{from{opacity:0;transform:scale(.84)}to{opacity:1;transform:none}}
@keyframes in-soft{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}
@keyframes in-mask{from{opacity:0;transform:translateY(40%)}to{opacity:1;transform:none}}
@keyframes in-pop{0%{opacity:0;transform:scale(.9)}70%{opacity:1;transform:scale(1.03)}100%{opacity:1;transform:scale(1)}}
@keyframes in-btn{from{opacity:0;transform:translateY(18px) scale(.94)}to{opacity:1;transform:none}}
@keyframes in-side{from{opacity:0;transform:translateX(22px)}to{opacity:1;transform:none}}
@keyframes in-stat{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:none}}
@keyframes in-star{0%{transform:scale(.2) rotate(-50deg)}65%{transform:scale(1.2) rotate(8deg)}100%{transform:none}}
@keyframes in-em{from{opacity:.35;filter:blur(4px)}to{opacity:1;filter:none}}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{transition:none !important;animation:none !important}
.appear,.hero-photo,.hero h1 em,.badge-star{opacity:1;transform:none;clip-path:none;filter:none}}
/* responsive */
@media (min-width:1600px){:root{--logo:17px;--logo-mark:24px;--nav:15px;--nav-h:44px;--btn:15px;--btn-h:44px;--hero-btn-h:48px;--h1:64px;--lede:18px;--badge:13.5px;--stat-size:15px;--header-y:28px;--header-x:64px;--stats-x:96px;--stats-y:44px;--copy-max:980px;--lede-max:540px}
#site-nav a{padding:0 20px}.badge{margin-bottom:26px}.lede{margin-top:22px}.hero-actions{margin-top:30px;gap:12px}.stat svg{width:22px;height:22px}.stat .stat-icon-wide{width:45px;height:24px}}
@media (min-width:1920px){:root{--logo:18px;--logo-mark:26px;--nav:16px;--nav-h:48px;--btn:16px;--btn-h:48px;--hero-btn-h:52px;--h1:76px;--lede:20px;--badge:14.5px;--stat-size:16px;--header-y:32px;--header-x:80px;--stats-x:120px;--stats-y:52px;--copy-max:1120px;--lede-max:620px}
#site-nav{gap:10px}#site-nav a{padding:0 22px}.btn{padding:0 22px}.stat .stat-icon-wide{width:48px;height:26px}}
@media (min-width:2560px){:root{--h1:88px;--lede:22px;--header-x:120px;--stats-x:160px;--copy-max:1280px;--lede-max:680px}}
@media (min-width:1280px) and (max-width:1599px){:root{--h1:54px;--lede:16px;--header-x:48px;--stats-x:80px;--copy-max:900px}}
@media (min-width:901px) and (max-width:1279px){:root{--logo:15px;--nav:13px;--nav-h:36px;--btn:13px;--btn-h:38px;--hero-btn-h:40px;--h1:42px;--lede:15px;--badge:12px;--stat-size:12.5px;--header-y:16px;--header-x:28px;--stats-x:36px;--stats-y:28px;--hero-gap:64px;--copy-max:760px;--lede-max:440px}
#site-nav a{padding:0 14px}.badge{margin-bottom:16px}.lede{margin-top:14px}.hero-actions{margin-top:20px}}
@media (min-width:901px) and (max-height:850px){:root{--header-y:14px;--stats-y:24px;--hero-gap:48px;--h1:40px}.badge{margin-bottom:12px}.lede{margin-top:12px}.hero-actions{margin-top:16px}}
@media (min-width:901px) and (max-height:720px){:root{--h1:34px;--lede:14px;--hero-gap:32px;--stats-y:18px;--nav-h:30px;--btn-h:34px;--hero-btn-h:36px}.badge{margin-bottom:8px}}
@media (min-width:901px){html,body{height:100%;overflow:hidden}.page{height:100vh;height:100dvh;overflow:hidden}}
@media (max-width:900px){
html,body{height:auto;overflow-y:auto}
:root{--logo:16px;--btn:15px;--btn-h:46px;--hero-btn-h:48px;--h1:36px;--lede:16.5px;--badge:13.5px;--stat-size:15px;--header-x:16px;--header-y:18px;--stats-x:20px;--stats-y:28px;--hero-gap:36px}
.header{grid-template-columns:1fr auto auto;gap:8px;padding-left:max(16px,env(safe-area-inset-left));padding-right:max(16px,env(safe-area-inset-right))}
.logo,.header-cta,.burger{z-index:80}
.burger{display:grid}
.header-cta{height:42px}
.menu-backdrop{display:block;position:fixed;inset:0;z-index:40;background:rgba(8,8,8,.42);opacity:0;visibility:hidden;transition:opacity .28s,visibility .28s}
body.menu-open .menu-backdrop{opacity:1;visibility:visible;backdrop-filter:blur(24px);-webkit-backdrop-filter:blur(24px)}
#site-nav{position:fixed;inset:0;z-index:45;flex-direction:column;justify-content:center;gap:12px;background:transparent;
padding:96px 22px 32px;padding-top:max(96px,calc(env(safe-area-inset-top) + 88px));opacity:0;visibility:hidden;transition:opacity .28s,visibility .28s}
body.menu-open #site-nav{opacity:1;visibility:visible}
#site-nav a{width:100%;height:56px;font-size:19px;border-radius:10px;justify-content:center}
body.menu-open{overflow:hidden}
.hero{padding:20px 20px 64px}
.hero-copy,.lede{max-width:100%}
.stats{flex-direction:column;justify-content:center;gap:16px}
.stat{white-space:normal}}
@media (max-width:560px){:root{--h1:34px;--lede:16px;--header-x:16px}.hero-actions{flex-direction:column;width:100%}.hero-actions .btn{width:100%}}
</style></head>
<body style="background:#000;color:#fff">
<div class="grain"></div>
<div class="hero-photo appear"><video autoplay muted loop playsinline preload="auto"
src="https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260818_072341_50851634-bbc3-4c33-9acc-7647d4db44aa.mp4"></video></div>
<div class="page">
<div class="menu-backdrop"></div>
<header class="header">
<a class="logo appear appear--scale" href="/" aria-label="Claim Lens" style="--d:.08s">
<svg viewBox="0 0 24 24" fill="currentColor"><g transform="rotate(-30 12 12)"><circle cx="7.3" cy="3.2" r="1.45"/><rect x="5.5" y="4.7" width="3.6" height="14.6" rx="1.8"/><rect x="14.9" y="4.7" width="3.6" height="14.6" rx="1.8"/><circle cx="16.7" cy="20.8" r="1.45"/></g></svg>
<span>Claim Lens</span></a>
<nav id="site-nav" aria-label="Primary">
<a class="appear appear--scale" href="/app" style="--d:.16s">Checker</a>
<a class="appear appear--soft" href="/dashboard" style="--d:.28s">Ledger</a>
<a class="appear appear--scale" href="/languages" style="--d:.40s">Languages</a>
<a class="appear appear--soft" href="/privacy" style="--d:.52s">Privacy</a>
<a class="appear appear--scale" href="/scan" style="--d:.60s">Scan</a>
<a class="appear appear--soft" href="/email" style="--d:.68s">Email</a>
</nav>
<a class="btn btn-solid header-cta appear appear--scale" href="https://wa.me/15556407358" style="--d:.34s">Try on WhatsApp</a>
<button class="burger appear appear--scale" aria-controls="site-nav" aria-expanded="false" aria-label="Open menu" style="--d:.34s"><span></span><span></span><span></span></button>
</header>
<main class="hero" id="top"><div class="hero-copy">
<div class="badge appear appear--pop" style="--d:.22s">
<svg class="badge-star" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2.6C12.55 2.6 12.88 3.15 13.08 4.7c.62 4.7 1.52 5.6 6.22 6.22 1.55.2 2.1.53 2.1 1.08s-.55.88-2.1 1.08c-4.7.62-5.6 1.52-6.22 6.22-.2 1.55-.53 2.1-1.08 2.1s-.88-.55-1.08-2.1c-.62-4.7-1.52-5.6-6.22-6.22C3.15 12.88 2.6 12.55 2.6 12s.55-.88 2.1-1.08c4.7-.62 5.6-1.52 6.22-6.22C11.12 3.15 11.45 2.6 12 2.6Z"/></svg>
Fact-checking for every forward</div>
<h1><span class="headline-line appear appear--mask" style="--d:.42s">Check any <em>forward</em> before</span>
<span class="headline-line appear appear--mask" style="--d:.62s">you share it.</span></h1>
<p class="lede appear appear--soft" style="--d:.82s">Send a message, screenshot, voice note, link or PDF. Claim Lens finds trusted sources and replies with a verdict you can understand, in your own language.</p>
<div class="hero-actions">
<a class="btn btn-solid appear appear--btn" href="https://wa.me/15556407358" style="--d:.96s">Try on WhatsApp</a>
<a class="btn btn-ghost appear appear--side" href="/app" style="--d:1.10s">Open web checker</a>
<a class="btn btn-ghost appear appear--side" href="/scan" style="--d:1.20s">Scam scan</a>
</div></div></main>
<footer class="stats">
<div class="stat appear appear--stat" style="--d:1.12s">
<svg viewBox="0 0 24 24"><defs><linearGradient id="a" x1="3" y1="2" x2="14" y2="22" gradientUnits="userSpaceOnUse"><stop stop-color="#fff" stop-opacity=".38"/><stop offset="1" stop-color="#3a3a3a" stop-opacity=".62"/></linearGradient><linearGradient id="b" x1="3" y1="2" x2="14" y2="22" gradientUnits="userSpaceOnUse"><stop stop-color="#3a3a3a" stop-opacity=".38"/><stop offset="1" stop-color="#fff" stop-opacity=".62"/></linearGradient></defs><rect x="3.4" y="2.6" width="7.2" height="18.8" rx="3.6" fill="url(#a)"/><rect x="13.4" y="2.6" width="7.2" height="18.8" rx="3.6" fill="url(#b)"/><rect x="9.2" y="10.9" width="5.6" height="2.2" rx="1.1" fill="#4a4a4a"/></svg>
<span><b id="s1">0</b> claims checked</span></div>
<div class="stat appear appear--stat" style="--d:1.28s">
<svg viewBox="0 0 24 24"><rect x="2.4" y="2.4" width="19.2" height="19.2" rx="6.2" fill="#fff"/><g stroke="#111" stroke-width="1.85" stroke-linecap="round" stroke-linejoin="round" fill="none"><path d="M12 7.1v7.4"/><path d="M8.15 12.35L12 16.2l3.85-3.85"/></g></svg>
<span><b id="s2">0</b> repeat forwards answered instantly</span></div>
<div class="stat appear appear--stat" style="--d:1.44s">
<svg class="stat-icon-wide" viewBox="0 0 40 22"><circle cx="10.2" cy="11" r="9.2" fill="#2b2b2b"/><circle cx="20.2" cy="11" r="9.2" fill="#fff"/><circle cx="30.2" cy="11" r="9.2" fill="#f26b1d"/>
<g font-family="Inter,sans-serif" font-weight="700" font-size="9" text-anchor="middle"><text x="10.2" y="14" fill="#fff">हि</text><text x="20.2" y="14" fill="#111">म</text><text x="30.2" y="14" fill="#fff">മ</text></g></svg>
<span>Hindi, Marathi, Malayalam &amp; English</span></div>
</footer>
</div>
<script>
(function(){
var all=document.querySelectorAll(".appear");
all.forEach(function(el){el.addEventListener("animationend",function(){el.classList.add("is-in")},{once:true})});
requestAnimationFrame(function(){requestAnimationFrame(function(){
 var ok=false;
 var t=document.querySelector(".logo");
 try{ok=t.getAnimations().some(function(a){return a.playState==="running"||a.playState==="finished"})}catch(e){}
 if(!ok){document.querySelectorAll(".appear,.hero-photo").forEach(function(el){el.classList.add("is-in")})}
})});
var b=document.querySelector(".burger"),bd=document.querySelector(".menu-backdrop");
function setMenu(o){document.body.classList.toggle("menu-open",o);b.setAttribute("aria-expanded",o?"true":"false");b.setAttribute("aria-label",o?"Close menu":"Open menu")}
b.addEventListener("click",function(){setMenu(!document.body.classList.contains("menu-open"))});
bd.addEventListener("click",function(){setMenu(false)});
document.querySelectorAll("#site-nav a").forEach(function(a){a.addEventListener("click",function(){setMenu(false)})});
document.addEventListener("keydown",function(e){if(e.key==="Escape")setMenu(false)});
window.matchMedia("(min-width:901px)").addEventListener("change",function(m){if(m.matches)setMenu(false)});
fetch("/api/stats").then(function(r){return r.json()}).then(function(d){
 document.getElementById("s1").textContent=d.total;
 document.getElementById("s2").textContent=Math.max(0,d.total-d.unique);
}).catch(function(){});
})();
</script></body></html>"""


@router.get("/", response_class=HTMLResponse)
async def landing():
    return PAGE


@router.get("/health")
async def health():
    return {"status": "ok"}
