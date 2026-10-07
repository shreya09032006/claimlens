(function () {
  if (window.__claimlens14) { window.__claimlens14.scan(true); return; }
  const COL = {low: "#2e7d32", medium: "#ef6c00", high: "#c62828", none: "#777"};
  let badge = null, lastKey = "", timer = null;

  function alive() { try { return !!(chrome.runtime && chrome.runtime.id); } catch (e) { return false; } }
  function box() {
    if (badge && document.documentElement.contains(badge)) return badge;
    badge = document.createElement("div");
    badge.style.cssText = "position:fixed;top:70px;right:16px;z-index:2147483647;width:320px;max-height:70vh;overflow:auto;background:#0b0b0b;color:#fff;font:13px/1.5 Arial,sans-serif;border-radius:12px;border:1px solid #444;border-left:6px solid #777;padding:12px;box-shadow:0 6px 24px rgba(0,0,0,.5)";
    document.documentElement.appendChild(badge);
    return badge;
  }
  function btn(label, fn) {
    const x = document.createElement("button");
    x.textContent = label;
    x.style.cssText = "cursor:pointer;padding:6px 10px;border-radius:6px;border:1px solid #888;background:#222;color:#fff;font-size:12px";
    x.onclick = fn;
    return x;
  }
  function status(text, level) {
    const b = box();
    b.style.display = "block";
    b.style.borderLeftColor = COL[level || "none"];
    b.textContent = text;
  }
  function send(m, cb) {
    if (!alive()) { status("Claim Lens was reloaded. Close this Gmail tab and open a new one."); return; }
    try { chrome.runtime.sendMessage(m, cb); } catch (e) { status("Claim Lens was reloaded. Close this Gmail tab and open a new one."); }
  }
  function render(d, p) {
    const b = box();
    b.style.display = "block";
    b.style.borderLeftColor = COL[d.level];
    b.textContent = "";
    const t = document.createElement("div");
    t.style.cssText = "font-size:15px;font-weight:600;margin-bottom:6px";
    t.textContent = (d.level === "low" ? "✅ " : "🚩 ") + "Claim Lens: " + d.level.toUpperCase() + " risk";
    b.appendChild(t);
    const list = document.createElement("div");
    if (!d.findings.length) list.textContent = "No red flags found in the visible email. For the digital signature check, use Full signature check.";
    d.findings.forEach(f => { const r = document.createElement("div"); r.textContent = (f.sev === "high" ? "🔴 " : "🟠 ") + f.msg; list.appendChild(r); });
    b.appendChild(list);
    const bar = document.createElement("div");
    bar.style.cssText = "display:flex;gap:6px;margin-top:10px;flex-wrap:wrap";
    const note = document.createElement("div");
    note.style.cssText = "margin-top:8px;color:#9a9a9a;font-size:12px";
    bar.appendChild(btn("Check claims", () => send({type: "claims", text: (p.subject + ". " + p.body).slice(0, 1500)})));
    bar.appendChild(btn("Full signature check", () => full(p, note)));
    bar.appendChild(btn("Close", () => { b.style.display = "none"; }));
    b.appendChild(bar);
    b.appendChild(note);
  }
  async function full(p, note) {
    note.textContent = "Fetching the original email...";
    let raw = "", how = "visible text only";
    try {
      const m = location.pathname.match(/\/mail\/u\/(\d+)/);
      const u = m ? m[1] : "0";
      const body = document.querySelector("div.a3s");
      const holder = body && body.closest("[data-legacy-message-id]");
      const id = holder ? holder.getAttribute("data-legacy-message-id") : "";
      if (id) {
        const r = await fetch("/mail/u/" + u + "/?view=om&th=" + id, {credentials: "include"});
        const t = await r.text();
        if (r.ok && /^(Received|Delivered-To|Return-Path|Authentication-Results|DKIM-Signature|From):/mi.test(t.slice(0, 5000))) { raw = t; how = "original source"; }
      }
    } catch (e) {}
    if (!raw) raw = "From: " + p.sender + "\nSubject: " + p.subject + "\nContent-Type: text/plain\n\n" + p.body + "\n\n" + p.links.map(l => l.text + " -> " + l.href).join("\n");
    note.textContent = "Opening the email checker (" + how + ")...";
    send({type: "stash", raw});
  }
  function scan(force) {
    if (!alive()) return;
    const subjEl = document.querySelector("h2.hP") || document.querySelector("h2[data-thread-perm-id]") || document.querySelector("h2");
    const body = document.querySelector("div.a3s.aiL") || document.querySelector("div.a3s");
    if (!body) {
      lastKey = "";
      if (force) status("Claim Lens: open an email first, then right-click again.");
      else if (badge) badge.style.display = "none";
      return;
    }
    const se = document.querySelector("span.gD[email]") || document.querySelector("span[email]");
    const sender = se ? se.getAttribute("email") : "";
    const links = Array.from(body.querySelectorAll("a[href]")).map(a => ({href: a.href, text: a.textContent.trim()}));
    const p = {sender, subject: subjEl ? subjEl.textContent.trim() : "", body: body.innerText.slice(0, 4000), links};
    const key = p.subject + "|" + sender + "|" + p.body.length;
    if (!force && key === lastKey && badge && badge.style.display !== "none") return;
    lastKey = key;
    status("Claim Lens is checking this email...");
    send({type: "check", data: p}, res => {
      if (chrome.runtime.lastError) { status("Claim Lens error: " + chrome.runtime.lastError.message); return; }
      if (res && res.ok) render(res.d, p);
      else status("Claim Lens could not reach the server (" + (res && res.err) + "). Check that uvicorn and ngrok are running.");
    });
  }
  window.__claimlens14 = {scan};
  try { chrome.runtime.onMessage.addListener(m => { if (m.type === "showbadge") scan(true); }); } catch (e) {}
  new MutationObserver(() => { clearTimeout(timer); timer = setTimeout(() => { try { scan(false); } catch (e) {} }, 900); })
    .observe(document.body, {childList: true, subtree: true});
  console.log("Claim Lens 1.4 loaded");
})();
