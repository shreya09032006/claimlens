const SITE = "https://unknotted-waking-omen.ngrok-free.dev";
const HDR = {"Content-Type": "application/json", "ngrok-skip-browser-warning": "1"};

chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.removeAll(() => {
    chrome.contextMenus.create({id: "cl-email", title: "Check with Claim Lens", contexts: ["page", "selection", "link"], documentUrlPatterns: ["https://mail.google.com/*"]});
    chrome.contextMenus.create({id: "cl-text", title: "Check with Claim Lens", contexts: ["selection"], documentUrlPatterns: ["http://*/*", "https://*/*"]});
    chrome.contextMenus.create({id: "cl-link", title: "Check this link with Claim Lens", contexts: ["link"], documentUrlPatterns: ["http://*/*", "https://*/*"]});
  });
});

chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  if (info.menuItemId === "cl-email") {
    try { await chrome.scripting.executeScript({target: {tabId: tab.id}, files: ["content.js"]}); } catch (e) {}
    setTimeout(() => chrome.tabs.sendMessage(tab.id, {type: "showbadge"}).catch(() => {}), 300);
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
