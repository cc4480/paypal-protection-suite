# PayPal Protection Suite — Devpost submission draft (Slice Z prep)

Prepared 2026-11-11 ~08:55 CST by Cho-zen1 research run. Draft only — nothing submitted, no repo created. Video recorded (1:36 tight cut); sandbox keys still missing. Status refreshed 2026-11-11 ~19:45 CST.
Deadline: Thu Nov 12, 2026, 14:00 CST. Building stops 10:00 CST that day (SCOPE.md §4).

## Status verified 2026-11-11 ~19:45 CST (supersedes the 13:20 CST section below — kept for the record)

- **Demo video DONE (2026-11-11 ~15:12 CST, Carlos's pacing call):** retimed to **1:36** — every scene's action now lands as its narration ends, no 5–10 s dead air. Full voiceover mixed in, 8th-scene logo end-card included. Delivered in chat; file link good until Fri Nov 13 ~15:15 CST. Composition synced to the PC `/video`.
- **Demo Account DONE (2026-11-11 ~15:40 CST, Carlos's direction: sample DATA, real motions — "not simulate it"):** built-in sample ledger (2 seeded invoices + 18 sample transactions) behind a PayPalClient-shaped DemoClient; the same `app/live.py` code runs every motion. Live-verified on the PC with the real DeepSeek key: WITNESS searched the ledger and earned NO_CHARGE on the Norton invoice (deliberately absent); SEATBELT created + sent DEMO-INV-1005 ($259.55, real $9.55 gross-up fee math), then decline flipped it SENT → CANCELLED with a re-read; AUDITOR computed the planted patterns itself (StreamBox sub, MusicWave +40.04% creep, CloudPhotos duplicate, $12.51 fees, $3.49 spread). Tests **52/52 on both copies**. Everything stamped SAMPLE ACCOUNT; receipts logged SIMULATED with the reason.
- **Retrain:** worker (Qwen2.5-0.5B) DONE — all 16,191 steps, adapter written. Analyst (Qwen3-0.6B) at **51%** (step 8,271/16,191 at the 19:33 CST check), still training. Neither holds the demo — the demo runs on DeepSeek end to end, per Carlos 15:43 CST.
- **Access spike: still BLOCKED on credentials only.** Keys are the one remaining gate. Carlos asked for the URL at 15:43 CST and was given https://developer.paypal.com/dashboard/ (Apps & Credentials → Sandbox → Default Application). PayPal sign-up was left at the "Confirm your email" step earlier today (code sent to hello@secscan.info) — unfinished unless he completed it since. Keys go into the PC `.env` by his hand only, never through chat. The moment they land: restart app + full live acceptance (real invoice check, real decline, real history pull).
- **Bridge: DOWN AGAIN this evening.** It recovered during the evening (up from ~18:48 CST), then the tunnel dropped again — state change recorded 20:06 CST (02:06 UTC Nov 12). This blocks the app restart and live acceptance until Carlos restarts it at the PC (elevated PowerShell: kill bridge `server.py` processes, then `Start-ScheduledTask -TaskName 'AlterEgo Bridge (Elevated)'`).
- No git repo yet — public repo under `cc4480` still needs Carlos's yes on the suggested name `paypal-protection-suite`.
- Video is recorded but not yet uploaded PUBLIC — that upload + pasting the URL into Devpost is still his step (or his yes).

## Status verified 2026-11-11 ~13:20 CST (VM copy + Cho-zen copy, hash-identical) — superseded by the section above

- Test suite: **45/45 passed** on both copies (34 original + 9 live-wiring tests with a fake PayPal client + 2 landing-page tests).
- **Live wiring DONE (2026-11-11, Cho-zen1):** the PayPal client is no longer dead code. WITNESS now reads the account (invoice match + 31-day Transaction Search) before ruling, and its verdict is code-coerced to UNVERIFIED whenever no live check ran — verified live on the PC: the Norton fixture now returns UNVERIFIED / account_check=not_checked instead of an unearned NO_CHARGE. SEATBELT has a real convert endpoint (creates + sends the G&S invoice, fee math in code: 3.49% + $0.49, buyer gross-up nets exactly). AUDITOR pulls real Transaction Search history (180 days, normalized) when credentials exist and stamps it LIVE SANDBOX; a failed pull is a loud 502, never a silent sample. Decline/cancel endpoint cancels + re-reads status. UI buttons for decline + generate are wired to the real endpoints.
- **Landing page DONE (2026-11-11 ~14:05 CST, Carlos's order; hero reworked ~14:14–14:20 CST on his direction):** `/` is the front door — the PayPal wordmark over a giant centered "PayPal Protection Suite" title on generated backdrop art, product framing throughout (no hackathon talk in the UI), a slow Ken Burns drift on the backdrop and carousel art (pure CSS, no new library), a 3-slide carousel with generated art (one image per agent), plain-words what-it-does cards, the honesty section (F&F / 180 days / protected with conditions), and the live status pill; the shell lives at `/app` with a back-link. Verified live on the PC at each step: / 200 with hero markers, /app 200, backdrop image 200 at exact bytes, /api/status unchanged.
- Access spike: **still BLOCKED on credentials only** — `SPIKE.md` (run 2026-11-07) records zero PayPal calls made; no `.env` PayPal credentials seated on either copy. S1–S4 have never been attempted, not failed. The kill rule (SCOPE §3) only triggers if S1 fails once run. The wiring above is unit-proven with a fake client; the spike + seed + live acceptance run the moment the keys land.
- No git repo yet (`~/workspace/paypal-suite` is not a git repository) — public repo under `cc4480` still needs Carlos's name confirmation.
- No demo video yet — tomorrow morning, after keys + seeding so the video shows LIVE SANDBOX receipts. **[SUPERSEDED 15:12 CST: video recorded, retimed to 1:36, delivered — see status section above.]**
- PC app is UP on :5000 running the new code incl. the landing page (venv python, restarted 2026-11-11 ~14:03 CST; start command: `cd C:\Users\Cho-zen\paypal-suite; .venv\Scripts\python.exe run.py`).

## Gates only Carlos can clear (SCOPE §7 — his steps, agents cannot do these)

1. **Bridge restart** (also unblocks the retrain check and any PC work — bridge recovered during the evening of Nov 11, then the tunnel dropped again, recorded 20:06 CST Nov 11). Steps already given in chat: elevated PowerShell, kill bridge `server.py` processes, `Start-ScheduledTask -TaskName 'AlterEgo Bridge (Elevated)'`. Until it is back, no app restart or live acceptance run is possible.
2. **Seat sandbox credentials himself** in the project's `.env` (never paste into chat): PayPal sandbox Client ID + Secret from developer.paypal.com, plus the two sandbox test-account emails (business = demo account, personal = S3 test). `.env.example` lists the exact key names.
3. **Final product name — DECIDED 2026-11-11:** "PayPal Protection Suite" stays (Carlos's call). Suggested repo name is now `paypal-protection-suite` to match (still needs his yes before creation).
4. **Record/approve the demo video** (< 3:00, public) and confirm it is PUBLIC before submission; file the submission from his Devpost account.

Order that saves tomorrow: restart bridge + seat keys TODAY, so the spike (S1–S4), demo-account seeding, live re-verify of A/B/C, video recording, and submission pack all fit before the 10:00 CST build stop — not compressed into the 10:00–14:00 window.

## Devpost draft fields (from SCOPE.md positioning + README.md)

**Project name:** PayPal Protection Suite (DECIDED by Carlos 2026-11-11 — name kept; the PayPal wordmark now sits in the landing hero and the monogram in the app header)
**Tagline:** Every AI agent in this hackathon works for the seller. These three work for you.
**Repo:** [NEEDS CARLOS — suggested: https://github.com/cc4480/paypal-protection-suite — confirm before creation]
**Demo video:** DONE — 1:36 tight cut, delivered in chat (link good until Fri Nov 13 ~15:15 CST), composition synced to PC `/video`. [NEEDS CARLOS — upload PUBLIC, paste URL]

**What it does (inspiration + what it does):**
PayPal scams hit buyers, and every protection tool out there is built for sellers. This suite flips it: three buyer-side agents in one app. WITNESS takes a scary "PayPal invoice" — the fake Norton/Geek Squad renewal class — extracts the claim, checks it against the account's real PayPal state, and answers one question in giant type: did money actually move? SEATBELT catches a seller pushing a Friends & Family payment and converts the deal onto the protected Goods & Services rail by generating a real G&S invoice, with Buyer Protection stated with its exclusions, never as a guarantee. AUDITOR X-rays your own PayPal history once: forgotten subscriptions, duplicate charges, price creep, and the true total of fees and conversion spread you paid.

**How we built it:**
Flask + SQLite, raw HTTPS to the PayPal sandbox REST APIs (no SDK) so every request and response is visible for honest receipts. All money math is deterministic Python; the AI does extraction (WITNESS), evidence-quoted risk analysis and message drafting (SEATBELT), and report narration (AUDITOR) — load-bearing in all three modules, not decoration. DeepSeek Flash is the test default for vision and text. Every PayPal call is logged and stamped LIVE SANDBOX or SIMULATED in the UI and in stored output; a dry run is labeled, never dressed up.

**Honest access note (goes in README and video close):**
Live third-party account access — reading another user's PayPal history with their consent — requires PayPal partner approval. The demo runs against one real PayPal sandbox account, labeled in the UI as the demo account, and every verdict is computed from live sandbox API responses for that account.

**Challenges:**
The partner gate above is the biggest one: S3 (Log in with PayPal, user-context reads) is expected to fail for a non-partner app, which selects the F1 fallback — one real sandbox demo account, presented honestly. The access spike (S1–S4) pins down exactly what the demo can claim before any module code runs; if S1 fails, the build stops rather than faking ledger data.

**Built with:** Python, Flask, SQLite, PayPal REST APIs (Invoicing v2, Transaction Search v1), DeepSeek.

**Video outline (< 3:00, SCOPE §5):**
0:00–0:15 hook — "Every AI agent in this hackathon works for the seller. These three work for you."
0:15–1:05 Module A — $499.99 "Norton renewal" invoice; WITNESS verdict "No money has left your account"; LIVE SANDBOX receipt; one-click decline flips status on re-read.
1:05–1:55 Module B — Marketplace chat demanding F&F; SEATBELT flags it, states F&F has no Buyer Protection, generates and sends the protected G&S invoice; exclusions line on camera.
1:55–2:40 Module C — X-ray report: a forgotten subscription, one duplicate, one price crept 40%, total fees paid.
2:40–3:00 close — three agents, one app, buyer-side; partner-approval sentence; repo URL on screen.

## After PayPal (for sequencing, not for this submission)

Mathematics for Systems Security (Devpost) — deadline Sun Nov 15, 2026, 08:00 CST. Standalone app, engines built in as native modules, no external MCP server/token/bridge; Seclayer kept out of the public entry. Build starts after the PayPal submission lands Thu afternoon.
