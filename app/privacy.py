from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

PAGE = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#000000"><title>Claim Lens - Privacy</title>
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
main{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;max-width:900px;width:100%;margin:0 auto}
h1{text-align:center;font-weight:500;font-size:38px;letter-spacing:-.045em;line-height:1.1}
h1 em{font-family:"Instrument Serif",serif;font-style:italic;font-weight:400;color:#9a9a9a}
.sub{text-align:center;color:#9a9a9a;font-size:14.5px;line-height:1.5;margin:10px auto 20px;max-width:480px}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;width:100%}
.card{padding:16px 18px;border-radius:12px;border:1px solid rgba(198,198,198,.28);
background:linear-gradient(135deg,rgba(255,255,255,.08),rgba(0,0,0,.55) 46%,rgba(150,170,200,.07));backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px)}
.card b{display:block;font-size:15.5px;margin-bottom:6px}
.card p{color:#b5b5b5;font-size:13.5px;line-height:1.6}
.foot{text-align:center;color:#777;font-size:12.5px;margin-top:16px}
@media(max-width:900px){.page{padding:16px 16px 28px}header{flex-direction:column;align-items:flex-start}nav{width:100%;display:grid;grid-template-columns:repeat(3,1fr);gap:5px}nav a{height:38px;padding:0 6px;font-size:13px}}
@media(max-width:600px){h1{font-size:30px}.grid{grid-template-columns:1fr}main{justify-content:flex-start}}
</style></head><body>
<div class="bg"><video autoplay muted loop playsinline preload="auto" src="https://d8j0ntlcm91z4.cloudfront.net/user_38xzZboKViGWJOttwIXH07lWA1P/hf_20260818_072341_50851634-bbc3-4c33-9acc-7647d4db44aa.mp4"></video></div>
<div class="page">
<header><a class="logo" href="/">Claim Lens</a>
<nav><a href="/">Home</a><a href="/app">Checker</a><a href="/dashboard">Ledger</a><a href="/languages">Languages</a><a href="/scan">Scan</a><a href="/email">Email</a><a href="/privacy" class="on">Privacy</a></nav></header>
<main>
<h1>Your data, <em>your</em> control.</h1>
<div class="sub">What Claim Lens does with the messages you check, in plain words.</div>
<div class="grid">
<div class="card"><b>Only used to check your message</b><p>Messages, screenshots, voice notes, links and PDFs are used only to produce a fact-check result for you.</p></div>
<div class="card"><b>Never sold, never used for ads</b><p>We do not sell your data and we do not use it for advertising.</p></div>
<div class="card"><b>Processed by AI and search services</b><p>To find the verdict, content may be sent to third-party AI and search services. Please do not submit anything private.</p></div>
<div class="card"><b>The shared ledger</b><p>Checked claims, not your phone number, are saved so a repeat forward can be answered instantly and cheaply.</p></div>
<div class="card"><b>Gmail extension</b><p>When you open an email, the sender, subject, visible text and links are sent to our server to check for phishing. Nothing is stored beyond the check.</p></div>
<div class="card"><b>Contact</b><p>mhatreshreya111@gmail.com</p></div>
</div>
<div class="foot">Claim Lens is a student project.</div>
</main></div></body></html>"""


@router.get("/privacy", response_class=HTMLResponse)
async def privacy():
    return PAGE
