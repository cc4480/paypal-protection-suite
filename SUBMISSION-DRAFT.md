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
3. **Final product name — DECIDED 2026-11-11:** "PayPal Protection Suite" stays (Carlos's call). **Repo CREATED 2026-11-11 ~21:25 CST at Carlos's direction: https://github.com/cc4480/paypal-protection-suite — PUBLIC, MIT license, demo video included in the repo.**
4. **Demo video:** DONE (1:36, in the repo). The official rules require it **uploaded to YouTube, publicly visible**, link pasted on the form — Carlos's upload from his account at submission time. (Rules re-read + full requirements audit done 2026-11-11 ~21:30 CST: every other requirement verified filled — public repo + MIT license at root, text description, tools statement, functional demo via fresh-clone run, eligibility, English, built during the submission period.)
5. **Keys — Carlos's call 2026-11-11 ~21:15 CST:** he is having trouble getting the sandbox keys, so the submission goes WITHOUT them: the app ships in its built-in demo account mode (sample data, every motion real, stamped SAMPLE ACCOUNT). Live sandbox mode is wired and ready — seating PAYPAL_CLIENT_ID + PAYPAL_CLIENT_SECRET in `.env` switches it with no code change.

State the night before: tests 52/52 on both copies; app live on the PC (landing + shell 200, DeepSeek ready, account_mode demo); repo public and verified reachable anonymously. A turn-in task is set for Thu 2026-11-12 12:00 CST to assemble the final pack ahead of the 14:00 deadline.

## Devpost draft fields (from SCOPE.md positioning + README.md)

**Project name:** PayPal Protection Suite (DECIDED by Carlos 2026-11-11 — name kept; the PayPal wordmark now sits in the landing hero and the monogram in the app header)
**Tagline:** Every protection tool out there works for the seller. These three work for you.
**Repo:** https://github.com/cc4480/paypal-protection-suite (PUBLIC, created 2026-11-11)
**Demo video:** DONE — 1:36 tight cut, shipped inside the repo as `paypal-demo-final.mp4`. [CARLOS at submission: the rules require the video on **YouTube, publicly visible**, with the link on the submission form — upload it from his account and paste the YouTube URL]

**What it does (inspiration + what it does):**
PayPal scams hit buyers, and every protection tool out there is built for sellers. This suite flips it: three buyer-side agents in one app. WITNESS takes a scary "PayPal invoice" — the fake Norton/Geek Squad renewal class — extracts the claim, checks it against the account's real PayPal state, and answers one question in giant type: did money actually move? SEATBELT catches a seller pushing a Friends & Family payment and converts the deal onto the protected Goods & Services rail by generating a real G&S invoice, with Buyer Protection stated with its exclusions, never as a guarantee. AUDITOR X-rays your own PayPal history once: forgotten subscriptions, duplicate charges, price creep, and the true total of fees and conversion spread you paid.

**How we built it:**
Flask + SQLite, raw HTTPS to the PayPal sandbox REST APIs (no SDK) so every request and response is visible for honest receipts. All money math is deterministic Python; the AI does extraction (WITNESS), evidence-quoted risk analysis and message drafting (SEATBELT), and report narration (AUDITOR) — load-bearing in all three modules, not decoration. DeepSeek is the model for vision and text. Every PayPal call is logged and stamped LIVE or SAMPLE ACCOUNT in the UI and in stored output; sample data is labeled, never dressed up.

**Honest access note (goes in README and video close):**
Live third-party account access — reading another user's PayPal history with their consent — requires PayPal partner approval. The submitted demo runs on the app's built-in demo account: a seeded sample ledger (PayPal-shaped invoices and transactions) that the same agent code runs against, with every result stamped SAMPLE ACCOUNT. Seat real sandbox credentials and the identical code runs against the live PayPal sandbox instead.

**Challenges:**
The partner gate above is the biggest one: S3 (Log in with PayPal, user-context reads) is expected to fail for a non-partner app. The build answers it with honesty enforced in code: a decisive WITNESS verdict is impossible without an account check, and the app ships with a built-in demo account whose sample data is stamped as such on every screen and receipt — the motions are real, the data is labeled. Getting live sandbox credentials seated was the other fight; the two-mode design means the submission never depends on them.

**Built with:** Python, Flask, SQLite, PayPal REST APIs (Invoicing v2, Transaction Search v1), DeepSeek.

**Video (SHIPPED — supersedes the SCOPE §5 outline):**
1:36 final cut, 8 scenes incl. logo end-card ("Three agents. One side: yours."), generated voiceover, faithful recreations of the app's real screens and figures (Norton invoice $499.99, SEATBELT $250 → $259.55, AUDITOR X-ray findings). File: `paypal-demo-final.mp4` in the repo.

## After PayPal (for sequencing, not for this submission)

Mathematics for Systems Security (Devpost) — deadline Sun Nov 15, 2026, 08:00 CST. Standalone app, engines built in as native modules, no external MCP server/token/bridge; Seclayer kept out of the public entry. Build starts after the PayPal submission lands Thu afternoon.
