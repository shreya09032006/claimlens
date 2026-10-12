const SITE = "https://unknotted-waking-omen.ngrok-free.dev";
const HDR = {"Content-Type": "application/json", "ngrok-skip-browser-warning": "1"};

chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.removeAll(() => {
    chrome.contextMenus.create({id: "cl-email", title: "Check with Claim Lens", contexts: ["page", "selection", "link"], documentUrlPatterns: ["https://mail.google.com/*"]});
    chrome.contextMenus.create({id: "cl-text", title: "Check with Claim Lens", contexts: ["selection"], documentUrlPatterns: ["http://*/*", "https://*/*"]});
    chrome.contextMenus.create({id: "cl-link", title: "Check this link with Claim Lens", contexts: ["link"], documentUrlPatterns: ["http://*/*", "https://*/*"]});
    chrome.contextMenus.create({id: "cl-phish", title: "Check link for phishing (Claim Lens)", contexts: ["link"], documentUrlPatterns: ["http://*/*", "https://*/*"]});
  });
});

chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  if (info.menuItemId === "cl-email") {
    try { await chrome.scripting.executeScript({target: {tabId: tab.id}, files: ["content.js"]}); } catch (e) {}
    setTimeout(() => chrome.tabs.sendMessage(tab.id, {type: "showbadge"}).catch(() => {}), 300);
    return;
  }
  if (info.menuItemId === "cl-phish") {
    const url = info.linkUrl || "";
    const show = res => chrome.scripting.executeScript({target: {tabId: tab.id}, func: clLinkBadge, args: [url, res]}).catch(() => {});
    show({loading: true});
    fetch(SITE + "/api/url-check", {method: "POST", headers: HDR, body: JSON.stringify({url})})
      .then(r => { if (!r.ok) throw new Error("server " + r.status); return r.json(); })
      .then(d => show({ok: true, d}))
      .catch(e => show({ok: false, err: String(e)}));
    return;
  }
  const q = info.menuItemId === "cl-text" ? info.selectionText : info.linkUrl;
  chrome.tabs.create({url: SITE + "/app?q=" + encodeURIComponent(q || "")});
});

chrome.runtime.onMessage.addListener((msg, sender, reply) => {
  if (msg.type === "check") {
    fetch(SITE + "/api/email-lite", {method: "POST", headers: HDR, body: JSON.stringify(msg.data)})
      .then(r => { if (!r.ok) throw new Error("server " + r.status); return r.json(); })
      .then(d => reply({ok: true, d})).catch(e => reply({ok: false, err: String(e)}));
    return true;
  }
  if (msg.type === "claims") chrome.tabs.create({url: SITE + "/app?q=" + encodeURIComponent(msg.text)});
  if (msg.type === "stash") {
    fetch(SITE + "/api/email-stash", {method: "POST", headers: HDR, body: JSON.stringify({raw: msg.raw})})
      .then(r => { if (!r.ok) throw new Error("server " + r.status); return r.json(); })
      .then(d => chrome.tabs.create({url: SITE + "/email?sid=" + d.sid}))
      .catch(() => chrome.tabs.create({url: SITE + "/email"}));
  }
});

// Runs inside the web page (injected), so it must be fully self-contained.
function clLinkBadge(url, res) {
  let b = document.getElementById("cl-link-badge");
  if (!b) {
    b = document.createElement("div");
    b.id = "cl-link-badge";
    b.style.cssText = "position:fixed;top:16px;right:16px;z-index:2147483647;width:320px;max-height:70vh;overflow:auto;background:#0b0b0b;color:#fff;font:13px/1.5 Arial,sans-serif;border-radius:12px;border:1px solid #444;border-left:6px solid #777;padding:12px;box-shadow:0 6px 24px rgba(0,0,0,.5)";
    document.documentElement.appendChild(b);
  }
  b.textContent = "";
  const add = (text, css) => { const d = document.createElement("div"); d.style.cssText = css || ""; d.textContent = text; b.appendChild(d); };
  let col = "#777";

  if (res.loading) {
    add("Claim Lens is checking this link...");
  } else if (!res.ok) {
    add("Claim Lens could not reach the server (" + res.err + "). Check that uvicorn and ngrok are running.");
  } else {
    const d = res.d, p = d.phishing_probability, pct = Math.round(p * 100);
    let title, advice;
    if (p >= 0.8) {
      col = "#c62828"; title = "Claim Lens: FRAUDULENT link";
      advice = "This web address looks like phishing. Do not open it or enter any details.";
    } else if (p >= 0.5) {
      col = "#ef6c00"; title = "Claim Lens: SUSPICIOUS link";
      advice = "Some warning signs in this web address. Verify the site before entering anything.";
    } else {
      col = "#2e7d32"; title = "Claim Lens: link looks SAFE";
      advice = "No phishing signs in the web address. This is not a guarantee, so stay careful with passwords.";
    }
    add(title, "font-size:15px;font-weight:600;margin-bottom:6px");
    add(advice);
    add(d.domain + " · " + pct + "% phishing likelihood", "margin-top:6px;color:#9a9a9a;font-size:12px;word-break:break-all");
    if (d.typosquat) add("• Looks like a fake of a well-known brand", "margin-top:4px;color:#ddd");
    if (d.matched_words && d.matched_words.length) add("• Contains words like: " + d.matched_words.join(", "), "margin-top:4px;color:#ddd");
  }

  b.style.borderLeftColor = col;
  const x = document.createElement("button");
  x.textContent = "Close";
  x.style.cssText = "margin-top:10px;cursor:pointer;padding:6px 10px;border-radius:6px;border:1px solid #888;background:#222;color:#fff;font-size:12px";
  x.onclick = () => b.remove();
  b.appendChild(x);
}