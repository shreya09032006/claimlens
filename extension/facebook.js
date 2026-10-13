(() => {
  if (window.__claimLensFacebookInstalled) return;
  window.__claimLensFacebookInstalled = true;

  const BUTTON_ATTR = "data-claim-lens-button";
  const POST_ATTR = "data-claim-lens-post";
  const MESSAGE_ATTR = "data-claim-lens-message";
  let panel;

  const style = document.createElement("style");
  style.textContent = `
    .cl-fb-check {
    display: block !important;
    visibility: visible !important;
    opacity: 1 !important;
    position: relative !important;
    z-index: 999999 !important;
    width: fit-content !important;
    margin: 12px 0 !important;
    padding: 10px 14px !important;
    border: 2px solid #1877f2 !important;
    border-radius: 8px !important;
    background: #1877f2 !important;
    color: #ffffff !important;
    font: bold 14px Arial, sans-serif !important;
    cursor: pointer !important;
    }

    .cl-fb-check:hover {
    background: #0757a6 !important;
    color: #ffffff !important;
}

    #claim-lens-fb-panel {
      position: fixed;
      right: 16px;
      top: 80px;
      width: min(410px, calc(100vw - 32px));
      max-height: 78vh;
      overflow: auto;
      z-index: 2147483647;
      box-sizing: border-box;
      padding: 14px;
      border: 1px solid #cbd5e1;
      border-radius: 14px;
      background: white;
      color: #172033;
      box-shadow: 0 8px 32px #0004;
      font: 14px/1.5 Arial, sans-serif;
    }
    #claim-lens-fb-panel a {
      color: #0757a6;
      overflow-wrap: anywhere;
    }
    #claim-lens-fb-panel .cl-title {
      font-weight: 700;
      font-size: 17px;
      margin-bottom: 8px;
    }
    #claim-lens-fb-panel .cl-close {
      float: right;
      border: 0;
      background: #eee;
      border-radius: 6px;
      padding: 4px 8px;
      cursor: pointer;
    }
    #claim-lens-fb-panel .cl-evidence {
      border-top: 1px solid #ddd;
      margin-top: 9px;
      padding-top: 8px;
    }
  `;

  (document.head || document.documentElement).appendChild(style);

  // ---------------- RESULTS PANEL ----------------

  function makePanel() {
    if (panel && panel.isConnected) return panel;

    panel = document.createElement("section");
    panel.id = "claim-lens-fb-panel";
    panel.setAttribute("role", "dialog");
    panel.setAttribute("aria-label", "Claim Lens fact check");
    document.documentElement.appendChild(panel);

    return panel;
  }

  function addText(parent, tag, text, className) {
    const el = document.createElement(tag);
    if (className) el.className = className;
    el.textContent = text;
    parent.appendChild(el);
    return el;
  }

  function showStatus(message) {
    const p = makePanel();
    p.replaceChildren();

    const close = addText(p, "button", "Close", "cl-close");
    close.onclick = () => p.remove();

    addText(p, "div", "CLAIM LENS — FACT CHECK", "cl-title");
    addText(p, "p", message);
  }

  function renderReport(data) {
    const p = makePanel();
    p.replaceChildren();

    const close = addText(p, "button", "Close", "cl-close");
    close.onclick = () => p.remove();

    addText(p, "div", "CLAIM LENS — FACT CHECK", "cl-title");

    const claims = Array.isArray(data?.claims) ? data.claims : [];

    if (!claims.length) {
      addText(
        p,
        "p",
        "No checkable factual claim was identified. Try checking the caption or message text.",
      );
    }

    claims.slice(0, 3).forEach((claim, index) => {
      const label = String(claim.label || "Cannot be confirmed");

      const color =
        label === "Verified"
          ? "#18794e"
          : label === "False"
            ? "#b42318"
            : label === "Outdated"
              ? "#b54708"
              : "#6b5b00";

      const section = document.createElement("div");
      section.className = "cl-evidence";

      const verdict = addText(
        section,
        "div",
        `${index + 1}. ${label}`,
        "cl-title",
      );

      verdict.style.color = color;

      addText(section, "p", String(claim.text || "Claim"));

      addText(
        section,
        "p",
        String(
          claim.explanation_local ||
            claim.explanation_en ||
            "No explanation was returned.",
        ),
      );

      const evidence = Array.isArray(claim.evidence) ? claim.evidence : [];

      if (evidence.length) {
        addText(section, "strong", "Source evidence");

        evidence.slice(0, 3).forEach((item) => {
          const row = document.createElement("p");
          const url = String(item.url || "");

          if (/^https?:\/\//i.test(url)) {
            const a = document.createElement("a");
            a.href = url;
            a.target = "_blank";
            a.rel = "noopener noreferrer";
            a.textContent = String(item.source || item.title || "Open source");
            row.appendChild(a);
          } else {
            row.textContent = String(
              item.source || item.title || "Source URL unavailable",
            );
          }

          if (item.date) {
            row.appendChild(document.createTextNode(` · ${item.date}`));
          }

          if (item.quote) {
            addText(
              row,
              "div",
              `Evidence: “${String(item.quote).slice(0, 240)}”`,
            );
          }

          section.appendChild(row);
        });
      } else {
        addText(
          section,
          "p",
          "No direct supporting source was found. Treat this claim as unverified, not as proven true or false.",
        );
      }

      p.appendChild(section);
    });

    addText(
      p,
      "p",
      "Automated fact-check: review the linked sources before sharing. A lack of evidence does not prove a claim is false.",
    );
  }

  // ---------------- BACKEND REQUEST ----------------

  function requestCheck(text, kind = "content") {
    if (!text || !text.trim()) {
      showStatus("No readable text was found to check.");
      return;
    }

    showStatus(
      kind === "message"
        ? "Checking this individual message and searching for source evidence…"
        : "Checking this post and searching for source evidence…",
    );

    chrome.runtime.sendMessage(
      {
        type: "facebook-factcheck",
        text: text.trim().slice(0, 8000),
      },
      (response) => {
        if (chrome.runtime.lastError) {
          showStatus("Extension error: " + chrome.runtime.lastError.message);
          return;
        }

        if (!response || !response.ok) {
          showStatus(
            "Claim Lens could not reach the backend. Check that FastAPI and your public HTTPS URL are running. " +
              (response?.err || ""),
          );
          return;
        }

        renderReport(response.d);
      },
    );
  }

  // ---------------- SHARED HELPERS ----------------

  function cleanText(value) {
    return String(value || "")
      .replace(/\s+/g, " ")
      .trim();
  }

  function makeCheckButton(label, callback) {
    const button = document.createElement("button");
    button.className = "cl-fb-check";
    button.type = "button";
    button.textContent = label;

    button.addEventListener("click", (event) => {
      event.preventDefault();
      event.stopPropagation();
      callback();
    });

    return button;
  }

  function hasDirectButton(node) {
    return Array.from(node.children).some((child) =>
      child.classList?.contains("cl-fb-check"),
    );
  }

  // ---------------- FACEBOOK FEED POSTS ----------------

  function getPostText(post) {
    const clone = post.cloneNode(true);

    clone
      .querySelectorAll(
        ".cl-fb-check, #claim-lens-fb-panel, " +
          "[aria-label*='Like'], [aria-label*='Comment'], " +
          "[aria-label*='Share']",
      )
      .forEach((el) => el.remove());

    return cleanText(clone.innerText || clone.textContent || "").slice(0, 8000);
  }

  function getPostImageDescriptions(post) {
    return Array.from(post.querySelectorAll("img[alt]"))
      .map((img) => cleanText(img.alt))
      .filter((alt) => alt.length > 8)
      .filter((alt) => !/profile picture|avatar|emoji|icon/i.test(alt))
      .slice(0, 5);
  }

  function addPostButtons() {
    const articles = Array.from(document.querySelectorAll('[role="article"]'));

    for (const post of articles) {
      if (!(post instanceof HTMLElement)) continue;
      if (post.closest("#claim-lens-fb-panel")) continue;
      if (post.hasAttribute(POST_ATTR)) continue;

      // Use the outer article if Facebook nests articles.
      if (post.parentElement?.closest('[role="article"]')) continue;

      const text = getPostText(post);

      if (text.length < 25 || text.length > 12000) continue;

      if (hasDirectButton(post)) continue;

      post.setAttribute(POST_ATTR, "1");

      const button = makeCheckButton(
        "🛡️ Check this post with Claim Lens",
        () => {
          const caption = getPostText(post);
          const descriptions = getPostImageDescriptions(post);

          const combined = [
            caption,
            descriptions.length
              ? "Image descriptions: " + descriptions.join("; ")
              : "",
          ]
            .filter(Boolean)
            .join("\n\n");

          requestCheck(combined, "post");
        },
      );

      post.appendChild(button);
    }
  }

  // ---------------- MESSENGER INDIVIDUAL MESSAGES ----------------

  function getChatRoots() {
    const roots = new Set();

    // Messenger pop-out windows on Facebook.
    document.querySelectorAll('[role="dialog"]').forEach((el) => {
      if (
        el.querySelector('[contenteditable="true"]') &&
        el.querySelector('[role="main"], [role="grid"], [role="list"]')
      ) {
        roots.add(el);
      }
    });

    // Full Messenger interface.
    document
      .querySelectorAll('[role="main"], [data-pagelet*="ChatTab"]')
      .forEach((el) => {
        if (el.querySelector('[contenteditable="true"]')) {
          roots.add(el);
        }
      });

    return Array.from(roots);
  }

  function getMessageText(node) {
    const clone = node.cloneNode(true);

    clone
      .querySelectorAll(
        ".cl-fb-check, button, [role='button'], " +
          "[contenteditable='true'], textarea, input",
      )
      .forEach((el) => el.remove());

    return cleanText(clone.innerText || clone.textContent || "");
  }

  function findIndividualMessageBubbles(root) {
    // Prefer Facebook's message-specific accessible labels/roles when available.
    const candidates = Array.from(
      root.querySelectorAll(
        '[role="row"], [data-scope="messages_table"] [dir="auto"], ' +
          '[data-testid*="message"], [data-testid*="Message"]',
      ),
    );

    const bubbles = new Set();

    for (const candidate of candidates) {
      if (!(candidate instanceof HTMLElement)) continue;
      if (candidate.closest("#claim-lens-fb-panel")) continue;
      if (candidate.closest('[contenteditable="true"]')) continue;
      if (candidate.closest("button, [role='button']")) continue;

      const text = getMessageText(candidate);

      // Skip names, timestamps, empty containers, and entire chat histories.
      if (text.length < 12 || text.length > 1800) continue;

      let bubble = candidate;

      // Walk up only while the parent still represents a compact message.
      for (let depth = 0; depth < 3; depth++) {
        const parent = bubble.parentElement;
        if (!parent || parent === root) break;

        const parentText = getMessageText(parent);

        if (parentText.length > 1800) break;

        // Stop before a parent containing multiple independent messages.
        const siblingMessages = Array.from(parent.children).filter(
          (child) =>
            child instanceof HTMLElement && getMessageText(child).length >= 12,
        );

        if (siblingMessages.length > 1) break;

        bubble = parent;
      }

      if (bubble !== root) bubbles.add(bubble);
    }

    // Keep the smallest candidates; discard containers that wrap another
    // candidate, which helps prevent duplicate buttons per message.
    return Array.from(bubbles).filter((bubble) => {
      return !Array.from(bubbles).some(
        (other) => other !== bubble && bubble.contains(other),
      );
    });
  }

  function addMessageButtons() {
    for (const root of getChatRoots()) {
      if (!(root instanceof HTMLElement)) continue;

      const bubbles = findIndividualMessageBubbles(root);

      for (const bubble of bubbles) {
        if (bubble.hasAttribute(MESSAGE_ATTR)) continue;
        if (bubble.hasAttribute(BUTTON_ATTR)) continue;
        if (hasDirectButton(bubble)) continue;

        const text = getMessageText(bubble);

        if (text.length < 12 || text.length > 1800) continue;

        bubble.setAttribute(MESSAGE_ATTR, "1");
        bubble.setAttribute(BUTTON_ATTR, "1");

        const button = makeCheckButton("🛡️ Check this message", () => {
          const message = getMessageText(bubble);
          requestCheck(message, "message");
        });

        bubble.appendChild(button);
      }
    }
  }

  // ---------------- SELECTED-TEXT SHORTCUT ----------------

  document.addEventListener("keydown", (event) => {
    if (
      (event.ctrlKey || event.metaKey) &&
      event.shiftKey &&
      event.key.toLowerCase() === "l"
    ) {
      const selected = cleanText(window.getSelection()?.toString() || "");

      if (selected) requestCheck(selected.slice(0, 8000));
    }
  });

  // ---------------- DYNAMIC FACEBOOK CONTENT ----------------

  function attachButtons() {
    // Find readable caption text blocks across the Facebook feed.
    const textNodes = Array.from(document.querySelectorAll('div[dir="auto"]'));

    for (const caption of textNodes) {
      if (!(caption instanceof HTMLElement)) continue;
      if (caption.closest("#claim-lens-fb-panel")) continue;
      if (caption.closest(".cl-fb-check")) continue;

      const captionText = cleanText(caption.innerText || caption.textContent);

      // Skip short labels, comments with little text, and huge text blocks.
      if (captionText.length < 25 || captionText.length > 3000) continue;

      // Find the nearest ancestor that looks like a complete feed post.
      let post = null;
      let current = caption;

      for (let level = 0; current && level < 14; level++) {
        const text = cleanText(current.innerText || "");

        const hasPostActions = Array.from(
          current.querySelectorAll("[aria-label]"),
        ).some((el) =>
          /actions for this post/i.test(el.getAttribute("aria-label") || ""),
        );

        if (
          hasPostActions &&
          text.length >= captionText.length &&
          text.length < 10000
        ) {
          post = current;
          break;
        }

        current = current.parentElement;
      }

      if (!post) continue;

      // Don't add more than one button to the same post container.
      if (post.querySelector(".cl-fb-check")) continue;

      const button = makeCheckButton(
        "🛡️ Check this post with Claim Lens",
        () => {
          const descriptions = getPostImageDescriptions(post);

          const combined = [
            captionText,
            descriptions.length
              ? "Image descriptions: " + descriptions.join("; ")
              : "",
          ]
            .filter(Boolean)
            .join("\n\n");

          requestCheck(combined, "post");
        },
      );

      button.setAttribute("data-claim-lens-button", "1");

      // Put the button immediately after the caption.
      caption.insertAdjacentElement("afterend", button);

      console.log(
        "Claim Lens button added below caption:",
        captionText.slice(0, 80),
      );
    }
  }

  function runFacebookChecks() {
    attachButtons();
    addMessageButtons();
  }

  runFacebookChecks();

  let debounce;

  const observer = new MutationObserver(() => {
    clearTimeout(debounce);
    debounce = setTimeout(runFacebookChecks, 700);
  });

  observer.observe(document.documentElement, {
    childList: true,
    subtree: true,
  });

  console.log(
    "Claim Lens loaded: post-caption and individual-message checks enabled.",
  );
})();
