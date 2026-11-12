# PayPal Protection Suite — SCOPE

**Project:** One app, three agents, all working for the **buyer** — every other entrant in this hackathon works for the seller.
**Event:** PayPal AI Hackathon (Devpost). **Deadline: Thu Nov 12, 2026, 14:00 CST.** Requires meaningful use of BOTH PayPal APIs and AI, a public GitHub repo + license, and a public demo video under 3 minutes.
**Positioning (locked, crowd-checked 2026-11-07 ~04:11 CST):** Lead with A. B sells **conversion**, not detection. C is a one-time **X-ray report**, not a watchdog.
**Status:** Plan only. No code, no repo yet. Build starts only after Carlos seats his sandbox credentials (§7).

---

## 1. Architecture + stack proposal

| Piece | Choice | Rationale (one line) |
|---|---|---|
| Runtime | Python 3.12 + Flask, one process | Matches the house build style; fastest path from zero to a demoable app in 5 days. |
| Storage | SQLite, one file | Cases, reports, and receipts need persistence; anything bigger is ceremony at this scale. |
| PayPal access | Direct HTTPS calls to `api-m3.sandbox.paypal.com` with OAuth2 client-credentials tokens — **no SDK** | The REST surface we need is ~8 endpoints; raw calls keep every request/response visible for honest receipts. |
| AI — vision | A vision-capable LLM call for invoice OCR/extraction | The invoice arrives as an image/PDF screenshot; extraction must be structured JSON, not a chat answer. |
| AI — text | An LLM call for chat-risk analysis (B), verdict wording (A), and report narration (C) | AI must be load-bearing in all three modules — that's a judging requirement, not decoration. |
| AI — provider | **DeepSeek Flash first** (test + default), provider-swappable by config | Develop and acceptance-test on DeepSeek Flash for both text and vision; the app is NOT hard-locked to it — if the A1/B1 fixtures fail on extraction or analysis quality, swap only the failing step to a stronger model and keep the rest. |
| Deterministic core | Plain Python for all money math (fees, creep, duplicates) | The AI never computes a dollar figure; code does, the AI only explains it. |
| UI | Single-page dark command-center (house style: #0B1120 / #CF2B4D / #38BDF8), vanilla JS + one grid component | One screen, three agent panels, giant verdict typography for Module A — accessibility is the feature. |
| Receipts | Every PayPal call logged and stamped **LIVE SANDBOX** or **SIMULATED** in the UI and in stored output | Honesty rule: a dry run is labeled, never dressed up. |
| Repo | Public GitHub under `cc4480`, MIT license, README with setup + sandbox notes | Hackathon requirement; license file lands in the skeleton slice, not at the end. |
| AlterEgo integration | A SEPARATE instance of the same AlterEgo architecture/framework, built containing only the tools this suite needs (Carlos, 2026-11-07, correcting Cho-zen1's earlier "trim the registry" framing; the count is NOT a fixed number — it is simply however many the needed set comes to) | The existing AlterEgo bridge is NOT trimmed or cut down in any way — it keeps all 109 tools, untouched. Instead the same framework is stood up fresh for the suite with only its needed tools in it from the start: health, shell, file read/write/list/search, screenshot + window focus/type/hotkey, and the CDP browser tools it uses (navigate / snapshot / click / type / readback). |

File discipline (house rule): every file **< 250 lines**; one named file-set per agent slice; every slice built by a builder and passed by an **independent checker** before it counts.

---

## 2. The three agents

### Agent A — **WITNESS** (Module A: fake-invoice guardian) — LEAD

- **Job:** Prove whether money actually moved. Takes a scary "PayPal invoice" (fake Norton/Geek Squad renewal class), extracts the claim, checks it against the account's real (sandbox) state, and delivers one giant verdict: *"No money has left your account. This is a request, not a charge. Do not call the number in the note."*
- **Inputs:** Uploaded invoice image/PDF or pasted invoice text; the demo account's PayPal state.
- **PayPal sandbox API surfaces:**
  - Invoicing API v2 — `GET /v2/invoicing/invoices/{invoice_id}` and `GET /v2/invoicing/invoices` (list/search) to find the claimed invoice and read its true status (DRAFT / SENT / PAID / …).
  - Transaction Search API v1 — `GET /v1/reporting/transactions` filtered by invoice ID / counterparty / amount, to prove **no completed transaction** matches the claim.
  - Invoicing API v2 — `POST /v2/invoicing/invoices/{invoice_id}/cancel` for the one-click decline/report action (only when the invoice actually exists in the account).
- **Outputs:** Accessible verdict screen (large type, read-aloud-friendly wording); extraction card (amount, seller name, invoice ID, phone number found in the note — the phone is displayed as *the thing not to call*); decline/report receipt; in "I already called or paid" mode, a **recovery packet** (what was disclosed, what to freeze, who to contact, in order).

### Agent B — **SEATBELT** (Module B: F&F → G&S conversion)

- **Job:** Catch a seller pushing a Friends & Family payment in a chat — then **convert the deal onto the protected rail** instead of just warning about it.
- **Inputs:** Pasted chat transcript (or screenshot); item details the user confirms.
- **PayPal sandbox API surfaces:**
  - Invoicing API v2 — `POST /v2/invoicing/invoices` (create the protected G&S invoice: item description, serial-number field, amount, terms) and `POST /v2/invoicing/invoices/{invoice_id}/send` to issue it.
  - Transaction Search API v1 — `GET /v1/reporting/transactions` in the "already paid" path, to locate the F&F payment in the account and anchor the evidence packet to it.
- **AI surface:** Chat analysis flags F&F demand + urgency + off-platform pressure with quoted evidence from the transcript; generates the polite-but-firm refusal message if the seller won't switch.
- **Outputs:** Risk verdict with the plain statement **"Friends & Family has NO Buyer Protection"**; a ready-to-send protected G&S invoice (with delivery/meetup terms, evidence checklist, and a fee-handling choice: buyer covers fee / seller covers fee / split); if the seller refuses, a firm final message + walk-away recommendation; if already paid, a **first-hour evidence packet** (screenshots to take, messages to save, reporting steps in order).
- **Honesty rule (hard):** The UI states Buyer Protection's exclusions and limits (e.g. items not covered, "significantly not as described" standards, filing windows). G&S is presented as *protected with conditions*, never as a universal guarantee.

### Agent C — **AUDITOR** (Module C: history X-ray)

- **Job:** Read the user's own PayPal history once and hand back the report nobody gives them: what they're still paying for, what they paid twice, what's quietly getting more expensive, and what PayPal actually cost them.
- **Inputs:** The demo account's transaction history (sandbox).
- **PayPal sandbox API surfaces:**
  - Transaction Search API v1 — `GET /v1/reporting/transactions` in ≤31-day windows, paginated backward across the seeded history; fields consumed: gross amount, `fee_amount`, net, currency + conversion details, counterparty, timestamps, transaction status/event codes.
- **Outputs:** One X-ray report with four sections — (1) **forgotten subscriptions** (recurring counterparties with no recent interaction signal), (2) **duplicate charges** (same counterparty + amount inside a tight window), (3) **price creep** per recurring charge (first vs latest amount, % change), (4) **true cost totals**: sum of fees paid and currency-conversion spread actually paid. All figures computed deterministically; the LLM writes only the plain-language summary on top.

---

## 3. Module A access spike — RUN FIRST, before any module code

**Question the whole lead module stands on:** what can a sandbox app actually *read* about an account, and whose account? Timebox: **half of Day 1**. Each test in order; each result kills or confirms a named fallback.

| # | Test | Pass looks like | If it fails |
|---|---|---|---|
| S1 | Client-credentials token → Invoicing `GET` list + detail against a sandbox **business** account we seeded with invoices (incl. one unpaid "renewal" invoice) | App reads its own account's invoices and true statuses | Sandbox invoicing read is broken → Module A's check degrades to invoice-exists/status-only via S2 evidence; escalate before building A2 |
| S2 | Transaction Search `GET /v1/reporting/transactions` against the **same** sandbox account (its own transactions) | Completed transactions returned with amounts/fees; an unpaid invoice correctly shows **no** matching transaction | Own-account Transaction Search unusable in sandbox → kills the "prove no money moved" claim in its strong form; fallback: verdict rests on invoice status alone, worded accordingly ("this invoice is unpaid") and the limitation is disclosed in the demo |
| S3 | **Log in with PayPal** (consumer OAuth) with a sandbox **personal** account: request user consent, then attempt user-context invoice/transaction reads | Third-party-style read of *another* account's state with consent — the live-product shape | **Expected result.** This is the partner gate: no user-scoped transaction read for a non-partner app. This failure does **not** block the demo — it selects Fallback F1 below and becomes an honest line in the README/video ("live third-party account access requires PayPal partner approval; the demo runs on a real sandbox account") |
| S4 | Seeded-data drill: seed the demo account with the full demo dataset (fake-renewal invoice unpaid, one paid invoice, subscription history, one duplicate, one creeped price) and re-run S1/S2 reads end to end | Every module's demo scenario is backed by **real sandbox API responses** | Seeding via API fails → seed through the sandbox web UI by hand; if a data shape can't be created at all, that demo scenario is cut, not faked |

**Fallback ladder for Module A (chosen by spike results, never improvised later):**
- **F0 (S1+S2+S3 pass):** true consented account check. (Not expected; take it if it lands.)
- **F1 (S1+S2 pass, S3 gated — the planned demo shape):** the app checks **one real sandbox account presented honestly as "the demo account."** Every verdict is computed from live sandbox API responses for that account. The UI labels the account as a PayPal sandbox demo account wherever its data appears. This is a real check against a real (sandbox) ledger — not simulated data.
- **F2 (S2 fails):** verdict narrows to invoice-status truth (exists / unpaid / not a charge), Transaction Search absence disclosed. Module A still leads; its claim shrinks to what the receipts prove.

**Kill rule:** if S1 also fails, STOP — do not build Module A on simulated ledger data and call it a check. Re-scope with Carlos before writing module code.

---

## 4. Build order — A first, small slices, builder + checker pairs

Deadline math drives the slicing: **~4.5 effective build days** (Nov 8 is partly consumed by the Vultr submission at 17:00; Nov 12 is submission day — all building stops by Nov 12, 10:00 CST). Every slice below is one builder agent + one independent checker agent; a slice counts only when the checker passes its acceptance criteria. Files < 250 lines each.

**Day 1 (Nov 7 eve – Nov 8): foundation + spike**
- **Slice 0 — Skeleton.** Repo, MIT LICENSE, README skeleton, Flask app shell, dark command-center frame with three empty agent panels, `.env` config for sandbox credentials (never committed), receipt logger stub. *Acceptance:* app boots, `/` renders the three panels, repo public with license, no secrets in git history.
- **Slice 1 — THE SPIKE (§3).** Throwaway scripts only, results written to `SPIKE.md` in the repo. *Acceptance:* S1–S4 each marked pass/fail with the actual API response evidence; fallback (F0/F1/F2) chosen and recorded. **Gate: no module slices start until Slice 1 lands.**

**Day 2 (Nov 9): Module A end-to-end (lead module first, demoable alone)**
- **Slice A1 — Extraction.** Upload/paste → vision LLM → structured JSON {amount, seller, invoice_id, phone_in_note}. *Acceptance:* 3 fixture invoices (incl. one fake Norton renewal) extract all four fields correctly; failure to read an ID degrades gracefully to "not found," never invents one.
- **Slice A2 — Ledger check.** Invoice lookup + transaction search per the spike's chosen fallback; verdict engine returns one of {NO_CHARGE (unpaid request), PAID (real charge found), NOT_FOUND}. *Acceptance:* against the seeded demo account, all three states reachable and correct; every API call stamped LIVE SANDBOX on the receipt.
- **Slice A3 — Verdict screen + actions.** Giant accessible verdict, decline/report via invoice cancel, "I already called or paid" recovery packet generator. *Acceptance:* cancel actually flips the sandbox invoice status (verified by re-read); packet contains the ordered recovery steps; verdict text includes the do-not-call warning whenever a phone number was extracted.

**Day 3 (Nov 10): Module B**
- **Slice B1 — Chat analyzer.** Paste chat → LLM flags {ff_demand, urgency, off_platform} with quoted evidence lines. *Acceptance:* 3 fixture chats (clean sale / soft F&F ask / hard scam pattern) classified correctly with quotes that exist verbatim in the input.
- **Slice B2 — Conversion.** Generate + send the protected G&S invoice via Invoicing API with item, serial field, terms, evidence checklist, fee-handling choice. *Acceptance:* invoice exists in the sandbox account with correct amount/terms for each fee choice; the send receipt is LIVE SANDBOX-stamped.
- **Slice B3 — Refusal + already-paid paths.** Firm final message generator; walk-away recommendation; first-hour evidence packet. *Acceptance:* Buyer Protection exclusions/limits text present verbatim in both the B2 and B3 outputs (checker greps for it — the honesty rule is tested, not trusted).

**Day 4 (Nov 11): Module C + integration**
- **Slice C1 — History puller.** Windowed Transaction Search pagination over the seeded history; normalizes to one local table. *Acceptance:* pulled totals reconcile to the sandbox account's known seeded totals to the cent.
- **Slice C2 — X-ray analysis.** Subscriptions, duplicates, creep, fee/conversion totals — deterministic Python only. *Acceptance:* the seeded duplicate and the seeded creeped subscription are both caught with correct figures; a clean control dataset produces zero false duplicates.
- **Slice C3 — Report + suite integration.** X-ray report page with LLM summary over computed figures; nav/receipts unified across A/B/C. *Acceptance:* every number on the report page traces to a C2 output field (checker spot-checks 5 figures); no module regressed (A and B acceptance suites re-run green).

**Day 5 (Nov 12, morning only): ship**
- **Slice Z — Submission pack.** README final (setup, architecture, honest partner-gate note), demo script rehearsal, Devpost form fields, video recorded + uploaded public. *Acceptance:* fresh-clone README walkthrough works; submission previewed before the 14:00 deadline with ≥1 hour to spare.

---

## 5. Demo video outline (< 3:00, public)

| Time | Beat |
|---|---|
| 0:00–0:15 | Hook, one line on screen: *"Every AI agent in this hackathon works for the seller. These three work for you."* |
| 0:15–1:05 | **Module A.** Show the scary "Norton renewal — $499.99" invoice. Upload it. WITNESS extracts the claim, checks the account, giant verdict: **"No money has left your account."** Show the LIVE SANDBOX receipt. One click declines the invoice; status flips on re-read. |
| 1:05–1:55 | **Module B.** Paste the Marketplace chat: "send the deposit Friends & Family, I have other buyers." SEATBELT flags it with quoted evidence, states F&F has no Buyer Protection — then **generates the protected Goods & Services invoice** and sends it. Show the exclusions line too (honesty on camera). |
| 1:55–2:40 | **Module C.** Run the X-ray on the demo account. Report lands: a forgotten subscription, one duplicate charge, one price that crept 40%, and the total fees actually paid. |
| 2:40–3:00 | Close: three agents, one app, buyer-side. One honest sentence: live third-party account access needs PayPal partner approval; everything shown ran against a real PayPal sandbox account. Repo URL on screen. |

---

## 6. Risks

1. **Partner gate (highest technical risk).** Transaction Search / Activities for *third-party live* accounts require PayPal partner status. Sandbox demo is unaffected; the spike (§3) pins down exactly what the demo can claim. Mitigation: F1 fallback is the planned shape, and the gate itself is disclosed in README + video — judges see honesty, not a hole.
2. **Unpublished gallery caveat.** The crowd check covers everything *publicly visible* as of Nov 7 (Devpost pages, GitHub, launches, press) plus both named near-neighbors (Hunch, Budget Guardian) read firsthand. The official gallery is unpublished and the participant pool is ~16k–30k, so an invisible entrant could be adjacent. This cannot be fully retired — it's the same risk every entrant carries.
3. **Deadline math.** Nov 7 (today, evening) → **Nov 12, 14:00 CST** ≈ 4.5 effective build days; Nov 8 loses hours to the Vultr submission (17:00 CST); the RedTeam app finish also competes for Carlos's attention this weekend. The slice plan front-loads Module A so a demoable, submittable product exists by end of Day 2 even if B/C compress.
4. **Sandbox data quirks.** Transaction Search in live PayPal lags ~3 hours and windows cap at 31 days; sandbox behavior may differ. C1's reconciliation acceptance test exists precisely to catch a silent mismatch before demo day.
5. **Adjacency pressure.** Hunch (in-hackathon) owns F&F *detection*; if Module B's demo lingers on detection, it looks like a copy. The video script spends B's time on the **generated protected invoice**, which Hunch doesn't do.
6. **"Meaningful AI" judging bar.** If any module reads as a thin API wrapper, the entry weakens. Guard: AI does extraction (A), evidence-quoted risk analysis + message drafting (B), and report narration (C) — visible in the demo, not just claimed.
7. **Credential handling.** Sandbox secrets must never enter git, chat logs, or the video. `.env` + `.gitignore` land in Slice 0; the video is recorded with the seeded demo account, never Carlos's real PayPal login.

---

## 7. What Carlos must supply (his steps — agents cannot do these)

1. **PayPal developer account + sandbox app** at developer.paypal.com (his login, his account): create a REST app and hand over the **sandbox Client ID + Secret** by seating them in the project's `.env` himself — never paste them into chat, and agents must never invent or placeholder-guess them. **Nothing in §4 past Slice 1 can run real sandbox calls without this.**
2. **Two sandbox test accounts** created in the same dashboard: one **business** account (plays "the demo user's account" that receives invoices and holds history) and one **personal** account (for the S3 Log in with PayPal spike test).
3. **Product name.** "Protection Suite" is a working title; the final name on the repo/Devpost/video is his call.
4. **Repo confirmation:** public repo name under `cc4480` (suggested: `paypal-buyer-guard`) — his yes before Slice 0 creates it.
5. **Demo video:** he records or approves the final cut and confirms it's set to PUBLIC before submission; submission itself is filed from his Devpost account.

---

*Prepared 2026-11-07. Next step on Carlos's word: Slice 0 + Slice 1 (spike) — in that order, spike before module code.*
