from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

PAGE = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Claim Lens - Privacy</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@300..700&family=Instrument+Serif:ital@1&display=swap">
<style>
html,body{background:#000 !important;color:#fff}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:Inter,system-ui,sans-serif;-webkit-font-smoothing:antialiased;min-height:100dvh}
a{color:inherit;text-decoration:none}
.page{max-width:620px;margin:0 auto;padding:22px 20px 60px}
header{display:flex;justify-content:space-between;align-items:center;margin-bottom:34px;gap:10px;flex-wrap:wrap}
.logo{font-size:15.5px;font-weight:600}
nav{display:flex;gap:6px;flex-wrap:wrap}
nav a{display:inline-flex;align-items:center;height:34px;padding:0 14px;border-radius:7px;border:1px solid rgba(198,198,198,.55);background:linear-gradient(105deg,#050505,#2a2a2a 48%,#4a4a4a);color:#f3f3f3;font-size:13px}
nav a:hover{border-color:#fff}
h1{text-align:center;font-weight:500;font-size:38px;letter-spacing:-.045em;line-height:1.1}
h1 em{font-family:"Instrument Serif",serif;font-style:italic;font-weight:400;color:#9a9a9a}
.sub{text-align:center;color:#9a9a9a;font-size:15px;line-height:1.55;margin:14px auto 26px;max-width:440px}
.card{padding:18px;border-radius:12px;border:1px solid rgba(255,255,255,.14);background:linear-gradient(135deg,rgba(255,255,255,.07),rgba(0,0,0,.55) 50%);margin-bottom:12px}
.card b{display:block;font-size:16px;margin-bottom:6px}
.card p{color:#b5b5b5;font-size:14.5px;line-height:1.65}
.foot{text-align:center;color:#777;font-size:13px;margin-top:22px}
</style></head><body><div class="page">
<header><a class="logo" href="/">🔍 Claim Lens</a>
<nav><a href="/app">Checker</a><a href="/dashboard">Ledger</a><a href="/languages">Languages</a><a href="/scan">Scan</a><a href="/email">Email</a><a href="/privacy">Privacy</a></nav></header>
<h1>Your data, <em>your</em> control.</h1>
<div class="sub">What Claim Lens does with the messages you check, in plain words.</div>
<div class="card"><b>🔒 Only used to check your message</b><p>Messages, screenshots, voice notes, links and PDFs are used only to produce a fact-check result for you.</p></div>
<div class="card"><b>🚫 Never sold, never used for ads</b><p>We do not sell your data and we do not use it for advertising.</p></div>
<div class="card"><b>🤖 Processed by AI and search services</b><p>To find the verdict, content may be sent to third-party AI and search services. Please do not submit anything private.</p></div>
<div class="card"><b>📒 The shared ledger</b><p>Checked claims, not your phone number, are saved so a repeat forward can be answered instantly and cheaply.</p></div>
<div class="card"><b>✉️ Contact</b><p>mhatreshreya111@gmail.com</p></div>
<div class="foot">Claim Lens is a student project.</div>
</div></body></html>"""


@router.get("/privacy", response_class=HTMLResponse)
async def privacy():
    return PAGE
