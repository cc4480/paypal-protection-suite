/* Protection Suite shell behavior.
   Honesty contract: previews render FIXTURE data and every preview surface
   carries a visible SIMULATED stamp. Live buttons never fake a result —
   without the needed key they show the server's own explanation of what
   is missing. Live AI results (the suite's DeepSeek seats) carry a
   DEEPSEEK stamp; nothing AI-produced is ever stamped LIVE SANDBOX —
   that stamp is reserved for real calls to the PayPal sandbox. */
"use strict";

const $ = (id) => document.getElementById(id);
let SUITE_READY = false;

function stamp(el, mode) {
  el.innerHTML = "";
  const s = document.createElement("span");
  s.className = "stamp " + (
    mode === "LIVE SANDBOX" ? "stamp-live"
    : mode === "DEEPSEEK" ? "stamp-ai"
    : "stamp-sim");
  s.textContent = mode;
  el.appendChild(s);
}

function blocked(el, sliceNote) {
  if (!SUITE_READY) {
    el.textContent = "Live checks are not on yet. Seat the sandbox app " +
      "credentials in .env (PAYPAL_CLIENT_ID + PAYPAL_CLIENT_SECRET — see " +
      ".env.example), then re-run the access spike. Use the Preview button " +
      "to click through the full flow — it is stamped SIMULATED.";
  } else {
    el.textContent = "Sandbox credentials are seated. " + sliceNote;
  }
  el.hidden = false;
}

function showBlocked(el, message) {
  el.textContent = message;
  el.hidden = false;
}

function postJSON(url, payload) {
  return fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload || {}),
  }).then((r) => r.json().then((data) => ({ ok: r.ok, data })));
}

/* ---- tabs ------------------------------------------------------------ */
const TABS = Array.from(document.querySelectorAll(".tab"));

function selectTab(tab, moveFocus) {
  TABS.forEach((t) => {
    const on = t === tab;
    t.classList.toggle("active", on);
    t.setAttribute("aria-selected", on ? "true" : "false");
    t.tabIndex = on ? 0 : -1;
    $("panel-" + t.dataset.panel).classList.toggle("active", on);
  });
  if (tab.dataset.panel === "receipts") loadReceipts();
  try {
    history.replaceState(null, "", "#" + tab.dataset.panel);
  } catch (e) { /* file:// or sandboxed frame — hash is a nicety */ }
  if (moveFocus) tab.focus();
}

TABS.forEach((tab, i) => {
  tab.addEventListener("click", () => selectTab(tab, false));
  tab.addEventListener("keydown", (ev) => {
    let j = null;
    if (ev.key === "ArrowRight") j = (i + 1) % TABS.length;
    else if (ev.key === "ArrowLeft") j = (i - 1 + TABS.length) % TABS.length;
    else if (ev.key === "Home") j = 0;
    else if (ev.key === "End") j = TABS.length - 1;
    if (j !== null) { ev.preventDefault(); selectTab(TABS[j], true); }
  });
});

(function openFromHash() {
  const name = (location.hash || "").replace("#", "");
  const tab = TABS.find((t) => t.dataset.panel === name);
  if (tab && !tab.classList.contains("active")) selectTab(tab, false);
})();

/* ---- readiness -------------------------------------------------------- */
fetch("/api/status").then((r) => r.json()).then((s) => {
  SUITE_READY = !!s.ready;
  const pill = $("ready-pill");
  pill.textContent = s.ready ? "READY — LIVE SANDBOX" : "DEMO ACCOUNT";
  pill.className = "pill " + (s.ready ? "pill-ok" : "pill-warn");
  let note = s.ready
    ? "Live sandbox account connected at " + s.api_base + "."
    : "No sandbox keys seated, so the agents are running on the Demo " +
      "Account — built-in sample data, every motion real, results " +
      "stamped SAMPLE ACCOUNT. Seat PAYPAL_CLIENT_ID + " +
      "PAYPAL_CLIENT_SECRET in .env to switch to the live account.";
  if (s.deepseek) {
    note += s.deepseek.ready
      ? " AI seats on (" + s.deepseek.model + ")."
      : " AI seats off: DEEPSEEK_API_KEY not seated.";
  }
  $("ready-note").textContent = note;
}).catch(() => { $("ready-note").textContent = "Status check failed."; });

/* ---- WITNESS ---------------------------------------------------------- */
const SAMPLE_INVOICE = {
  mode: "SIMULATED", amount: "$499.99", seller: "Norton Support Renewal",
  invoice_id: "INV2-SAMPLE-RENEWAL", phone: "1-800-555-0142",
  verdict: "NO_CHARGE",
  headline: "No money has left your account.",
  body: "This is a request for payment, not a charge. The invoice is " +
    "unpaid, and no completed transaction matches it. Do not call the " +
    "number in the note — that number is the scam.",
};

function renderVerdict(d) {
  $("extraction-card").hidden = false;
  stamp($("extraction-stamp"), d.stamp || d.mode);
  $("claim-amount").textContent = d.amount || "—";
  $("claim-seller").textContent = d.seller || "—";
  $("claim-invoice").textContent = d.invoice_id || "—";
  $("claim-phone").textContent = d.phone || "—";
  const v = $("verdict");
  v.hidden = false;
  v.classList.toggle("paid", d.verdict === "PAID");
  stamp($("verdict-stamp"), d.paypal_stamp || d.stamp || d.mode);
  $("verdict-headline").textContent = d.headline;
  $("verdict-body").textContent = d.body;
}

let WITNESS_INVOICE_ID = null;

$("btn-witness-preview").addEventListener("click", () => renderVerdict(SAMPLE_INVOICE));
$("btn-check").addEventListener("click", () => {
  const text = $("invoice-text").value.trim();
  if (!text) {
    showBlocked($("witness-blocked"), "Paste the invoice text first — or use the Preview button.");
    return;
  }
  $("witness-blocked").hidden = true;
  postJSON("/api/witness/check", { text }).then(({ ok, data }) => {
    if (!ok) { showBlocked($("witness-blocked"), data.message || "The check failed."); return; }
    WITNESS_INVOICE_ID = data.account_invoice ? data.account_invoice.id : null;
    renderVerdict(data);
    if (data.account_check === "live") {
      $("decline-result").textContent = data.account_invoice
        ? "Account checked LIVE: invoice " + data.account_invoice.invoice_number +
          " is " + data.account_invoice.status + " in the sandbox account."
        : "Account checked LIVE: no invoice in the account matches this one.";
    } else if (data.account_check === "demo") {
      $("decline-result").textContent = data.account_invoice
        ? "Demo account checked: invoice " + data.account_invoice.invoice_number +
          " is " + data.account_invoice.status + " in the sample data. " +
          "You can decline it below — the cancel really runs."
        : "Demo account checked: no invoice in the sample data matches " +
          "this one. The verdict is earned — against sample data.";
    } else if (data.account_check === "failed") {
      $("decline-result").textContent = "The live account check failed — the verdict above is UNVERIFIED.";
    } else {
      $("decline-result").textContent = "Account not checked — seat the sandbox credentials for a live verdict.";
    }
  }).catch(() => showBlocked($("witness-blocked"), "The check could not reach the suite server."));
});
$("btn-recovery").addEventListener("click", () => {
  $("recovery-packet").hidden = !$("recovery-packet").hidden;
});
$("btn-decline").addEventListener("click", () => {
  if (!WITNESS_INVOICE_ID) {
    $("decline-result").textContent = "No matching invoice was found in the account on the last check — nothing to decline.";
    return;
  }
  postJSON("/api/witness/decline", { invoice_id: WITNESS_INVOICE_ID }).then(({ ok, data }) => {
    $("decline-result").textContent = ok
      ? "Done — invoice " + data.invoice_id + " was " + data.status_before +
        ", now " + data.status_after + " (" + (data.stamp || "") + ")."
      : (data.message || "The decline failed.");
  }).catch(() => { $("decline-result").textContent = "The decline could not reach the suite server."; });
});

/* ---- SEATBELT ---------------------------------------------------------- */
const SAMPLE_FLAGS = [
  { flag: "Friends & Family demand", quote: "“send the deposit Friends & Family, it's cheaper”" },
  { flag: "Urgency pressure", quote: "“I have three other buyers coming today, need it in the next hour”" },
  { flag: "Off-platform pressure", quote: "“don't message me on here, text my number instead”" },
];
const FINAL_MESSAGE = "I’m happy to buy it, but I only pay through a PayPal " +
  "Goods & Services invoice so we’re both protected. I’ve sent one covering " +
  "the item, the serial number, and our meetup terms — fee handled as we " +
  "agreed. If that doesn’t work for you, I’ll have to pass. Thanks!";

function renderFlags(flags, finalMessage, stampMode, riskLevel) {
  $("risk-card").hidden = false;
  stamp($("risk-stamp"), stampMode);
  $("risk-level").textContent = riskLevel ? "Risk level: " + riskLevel : "";
  const ul = $("risk-list");
  ul.innerHTML = "";
  if (!flags.length) {
    const li = document.createElement("li");
    li.textContent = "No protection-stripping pressure found in this chat.";
    ul.appendChild(li);
  }
  flags.forEach((f) => {
    const li = document.createElement("li");
    li.innerHTML = "<strong></strong><blockquote></blockquote>";
    li.querySelector("strong").textContent = f.flag;
    li.querySelector("blockquote").textContent = f.quote;
    ul.appendChild(li);
  });
  $("refusal-card").hidden = false;
  $("final-message").value = finalMessage;
}

$("btn-seatbelt-preview").addEventListener("click", () =>
  renderFlags(SAMPLE_FLAGS, FINAL_MESSAGE, "SIMULATED", null));
$("btn-analyze").addEventListener("click", () => {
  const text = $("chat-text").value.trim();
  if (!text) {
    showBlocked($("seatbelt-blocked"), "Paste the seller chat first — or use the Preview button.");
    return;
  }
  $("seatbelt-blocked").hidden = true;
  postJSON("/api/seatbelt/analyze", { text }).then(({ ok, data }) => {
    if (!ok) { showBlocked($("seatbelt-blocked"), data.message || "The analysis failed."); return; }
    renderFlags(data.flags, data.final_message, data.stamp || "DEEPSEEK", data.risk_level);
  }).catch(() => showBlocked($("seatbelt-blocked"), "The analysis could not reach the suite server."));
});
$("btn-generate").addEventListener("click", () => {
  const payload = {
    item: $("inv-item").value.trim(),
    serial: $("inv-serial").value.trim(),
    amount: $("inv-amount").value.trim(),
    fee_choice: document.querySelector("input[name=fee]:checked").value,
  };
  postJSON("/api/seatbelt/convert", payload).then(({ ok, data }) => {
    $("invoice-result").hidden = false;
    if (!ok) {
      stamp($("invoice-stamp"), "SIMULATED");
      $("invoice-summary").textContent = data.message || "The invoice could not be created.";
      return;
    }
    stamp($("invoice-stamp"), data.stamp || "LIVE SANDBOX");
    $("invoice-summary").textContent = "Created + sent: invoice " +
      data.invoice_number + " (" + data.invoice_id + ") — " + data.item +
      " — total $" + data.total_charged + " to " + data.recipient +
      ". Fee covered by: " + data.fee_choice + " (fee ≈ $" +
      data.fee_estimate + ", computed at PayPal's published rate). " +
      "Status: " + data.status + ".";
  }).catch(() => {
    $("invoice-result").hidden = false;
    $("invoice-summary").textContent = "The invoice creation could not reach the suite server.";
  });
});

/* ---- AUDITOR ----------------------------------------------------------- */
const SAMPLE_XRAY = {
  subs: ["StreamBox Premium — $15.99/mo · no watch activity in 74 days (sample)"],
  dupes: ["CloudPhotos — $9.99 charged twice: Mar 3 and Mar 5 (sample)"],
  creep: ["MusicWave — $9.99 → $13.99 (+40.04%) across 6 months (sample)"],
  costs: ["PayPal fees paid: $212.47 (sample)", "Currency conversion spread paid: $38.12 (sample)"],
  summary: "Sample narration: you are paying for one subscription you no " +
    "longer use, you were charged twice for the same week of photo " +
    "storage, and one subscription quietly rose 40%. Fees and conversion " +
    "spread cost you $250.59 in the sample window.",
};

function fillList(id, items) {
  const ul = $(id);
  ul.innerHTML = "";
  items.forEach((t) => {
    const li = document.createElement("li");
    li.textContent = t;
    ul.appendChild(li);
  });
}

$("btn-auditor-preview").addEventListener("click", () => {
  $("xray-report").hidden = false;
  stamp($("xray-stamp"), "SIMULATED");
  fillList("xray-subs", SAMPLE_XRAY.subs);
  fillList("xray-dupes", SAMPLE_XRAY.dupes);
  fillList("xray-creep", SAMPLE_XRAY.creep);
  fillList("xray-costs", SAMPLE_XRAY.costs);
  $("xray-summary").textContent = SAMPLE_XRAY.summary;
  $("xray-action").textContent = "";
  $("xray-note").textContent = "";
});
$("btn-xray").addEventListener("click", () => {
  $("auditor-blocked").hidden = true;
  postJSON("/api/auditor/xray", {}).then(({ ok, data }) => {
    if (!ok) { showBlocked($("auditor-blocked"), data.message || "The X-ray failed."); return; }
    const f = data.figures;
    $("xray-report").hidden = false;
    stamp($("xray-stamp"), data.stamp || "SIMULATED");
    fillList("xray-subs", f.subscriptions);
    fillList("xray-dupes", f.duplicates);
    fillList("xray-creep", f.price_creep);
    fillList("xray-costs", f.true_costs);
    $("xray-summary").textContent = data.narration
      ? data.narration.summary
      : data.narration_note;
    $("xray-action").textContent = data.narration
      ? "Top action: " + data.narration.top_action : "";
    $("xray-note").textContent = data.data_note;
  }).catch(() => showBlocked($("auditor-blocked"), "The X-ray could not reach the suite server."));
});

/* ---- RECEIPTS ------------------------------------------------------------ */
function loadReceipts() {
  fetch("/api/receipts").then((r) => r.json()).then((data) => {
    const body = $("receipts-body");
    body.innerHTML = "";
    if (!data.receipts.length) {
      body.innerHTML = "<tr><td colspan='7'>No PayPal calls recorded yet — " +
        "run the access spike and they will appear here, stamped.</td></tr>";
      return;
    }
    data.receipts.forEach((r) => {
      const tr = document.createElement("tr");
      const cells = [r.created_at, r.module, r.operation, "", r.http_status ?? "—", r.ok ? "yes" : "no"];
      cells.forEach((c, i) => {
        const td = document.createElement("td");
        if (i === 3) stamp(td, r.mode); else td.textContent = c;
        tr.appendChild(td);
      });
      const td = document.createElement("td");
      const btn = document.createElement("button");
      btn.className = "btn btn-quiet";
      btn.textContent = "Explain";
      btn.addEventListener("click", () => explainReceipt(r.id));
      td.appendChild(btn);
      tr.appendChild(td);
      body.appendChild(tr);
    });
  });
}

function explainReceipt(id) {
  const out = $("receipt-explain");
  out.textContent = "Explaining…";
  postJSON("/api/receipts/explain", { id }).then(({ ok, data }) => {
    if (!ok) { out.textContent = data.message || "The explanation failed."; return; }
    out.textContent = data.explanation +
      (data.deadline_note ? " " + data.deadline_note : "");
  }).catch(() => { out.textContent = "The explanation could not reach the suite server."; });
}
$("btn-refresh-receipts").addEventListener("click", loadReceipts);
