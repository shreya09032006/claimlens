(function () {
  if (window.__claimlens14) { window.__claimlens14.scan(true); return; }
  const COL = {safe: "#2e7d32", marketing: "#1565c0", suspicious: "#ef6c00", phishing: "#c62828", unsure: "#777", unavailable: "#777", none: "#777"};
  let badge = null, lastKey = "", failedKey = "", timer = null, rawWhy = "";

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
    b.style.borderLeftColor = COL[d.verdict] || COL.unavailable;
    b.textContent = "";
    const t = document.createElement("div");
    t.style.cssText = "font-size:15px;font-weight:600;margin-bottom:6px";
    const a = document.createElement("div");
    if (d.verdict === "phishing") {
      t.textContent = "Claim Lens: PHISHING email";
      a.textContent = "The model thinks this is a phishing email. Do not click links or open attachments.";
    } else if (d.verdict === "safe") {
      t.textContent = "Claim Lens: SAFE email";
      a.textContent = "No signs of phishing or promotion found.";
    } else if (d.verdict === "marketing") {
      t.textContent = "Claim Lens: MARKETING email";
      a.textContent = "Looks like a promotion or newsletter, not a scam. Still avoid entering passwords from its links.";
    } else if (d.verdict === "suspicious") {
      t.textContent = "Claim Lens: SUSPICIOUS email";
      a.textContent = "Some warning signs found. Do not click links or share codes until you verify the sender.";
    } else if (d.verdict === "unsure") {
      t.textContent = "Claim Lens: NOT SURE";
      a.textContent = "The evidence is mixed. Check the sender address before acting on this email.";
    } else {
      t.textContent = "Claim Lens: model not ready";
      a.textContent = "Train the model first: python3 -W ignore -m ml.train_phishing_email";
    }
    b.appendChild(t);
    b.appendChild(a);
    (d.reasons || []).forEach(x => { const r = document.createElement("div"); r.style.cssText = "margin-top:4px;color:#ddd"; r.textContent = "• " + x; b.appendChild(r); });
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
  function findIk() {
    const html = document.documentElement.innerHTML;
    let m = html.match(/[?&;]ik=([a-z0-9]{8,})/i) || html.match(/["']ik["']\s*[:,]\s*["']([a-z0-9]{8,})["']/i);
    if (m) return m[1];
    try {
      for (const e of performance.getEntriesByType("resource")) {
        m = e.name.match(/[?&]ik=([a-z0-9]{8,})/i);
        if (m) return m[1];
      }
    } catch (e) {}
    return "";
  }
  async function getRaw() {
    rawWhy = "";
    try {
      const m = location.pathname.match(/\/mail\/u\/(\d+)/);
      const u = m ? m[1] : "0";
      const body = document.querySelector("div.a3s.aiL") || document.querySelector("div.a3s");
      const holder = body && body.closest("[data-message-id]");
      const mid = holder ? holder.getAttribute("data-message-id").replace("#", "") : "";
      if (!mid) { rawWhy = "no message id found on the page"; return ""; }
      const ik = findIk();
      if (!ik) { rawWhy = "no Gmail session key found"; return ""; }
      const r = await fetch("/mail/u/" + u + "/?ik=" + ik + "&view=om&permmsgid=" + encodeURIComponent(mid), {credentials: "include"});
      const t = await r.text();
      if (!r.ok) { rawWhy = "Gmail answered HTTP " + r.status; return ""; }
      if (!/^(Received|Delivered-To|Return-Path|Authentication-Results|DKIM-Signature|From|ARC-)[A-Za-z-]*:/mi.test(t.slice(0, 8000))) { rawWhy = "Gmail returned an unexpected page"; return ""; }
      return t;
    } catch (e) { rawWhy = "request error: " + e; }
    return "";
  }
  async function full(p, note) {
    note.textContent = "Fetching the original email...";
    const raw = await getRaw();
    if (!raw) {
      note.textContent = "Could not read the original email automatically. Use the three dots, Show original, then click Send to Claim Lens on that page.";
      return;
    }
    note.textContent = "Opening the email checker (original source)...";
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
    if (force) failedKey = "";
    if (!force && key === failedKey) return;   // this email already failed: do not retry or nag
    if (!force && key === lastKey && badge && badge.style.display !== "none") return;
    lastKey = key;
    status("Claim Lens is checking this email...");
    send({type: "check", data: p}, res => {
      const fail = msg => {
        failedKey = key;                                  // remember, so we do not repeat for this email
        if (force) status(msg);                           // only tell the user when they asked (right-click)
        else if (badge) badge.style.display = "none";
      };
      if (chrome.runtime.lastError) { fail("Claim Lens error: " + chrome.runtime.lastError.message); return; }
      if (res && res.ok) render(res.d, p);
      else fail("Claim Lens could not reach the server (" + (res && res.err) + "). Check that uvicorn and ngrok are running.");
    });
  }
  window.__claimlens14 = {scan};
  try { chrome.runtime.onMessage.addListener(m => { if (m.type === "showbadge") scan(true); }); } catch (e) {}
  new MutationObserver(() => { clearTimeout(timer); timer = setTimeout(() => { try { scan(false); } catch (e) {} }, 900); })
    .observe(document.body, {childList: true, subtree: true});
  console.log("Claim Lens 1.4 loaded");
})();