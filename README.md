# PayPal Protection Suite

**Every protection tool out there works for the seller. These three work for you.**

One app, three buyer-side agents, built for the PayPal AI Hackathon (Devpost):

- **WITNESS** — fake-invoice guardian. Upload a scary "PayPal invoice" (the
  Norton/Geek Squad renewal scam class); WITNESS extracts the claim, checks it
  against the account's real PayPal state, and answers one question in giant
  type: *did money actually move?*
- **SEATBELT** — catches a seller pushing a Friends & Family payment and
  **converts the deal onto the protected Goods & Services rail** by generating
  a real G&S invoice. Buyer Protection is presented with its exclusions and
  limits, never as a universal guarantee.
- **AUDITOR** — a one-time X-ray of your own PayPal history: forgotten
  subscriptions, duplicate charges, price creep, and the true total of fees
  and conversion spread you paid. All figures computed deterministically;
  the AI only narrates.

## Honest access note — two modes, always labeled

The app runs in one of two modes, and the UI and every receipt say which:

- **Live sandbox mode** — with your own PayPal sandbox credentials in `.env`,
  every agent motion runs against the real PayPal sandbox REST API
  (invoicing + Transaction Search). Receipts are stamped **LIVE**.
- **Demo account mode** — with no credentials, the app runs on a built-in
  sample account: a small seeded ledger (invoices + transactions in real
  PayPal shapes, see `app/demo.py`). The *same* agent code runs every motion —
  WITNESS really searches the ledger, decline really cancels and re-reads,
  SEATBELT really creates and sends the invoice with real fee math, AUDITOR
  really computes over the pulled history. Results are stamped
  **SAMPLE ACCOUNT**, and receipts record the demo reason. Sample data is
  labeled, never dressed up as live.

A decisive WITNESS verdict is only possible after an account check in either
mode — the honesty rule is enforced in code (`agents.enforce_verdict_honesty`),
not by convention.

**Demo video:** `paypal-demo-final.mp4` in this repo (1:36) walks all three
agents end to end.

## Setup

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env   # then fill in YOUR sandbox credentials (see below)
.venv/bin/python run.py
```

No credentials handy? Skip the `.env` step — the app runs in demo account
mode so you can click through every agent motion.

### Sandbox credentials (you supply these — never commit them)

1. At <https://developer.paypal.com/dashboard/> create a REST app and open
   its **Sandbox** tab.
2. Create two sandbox test accounts in the same dashboard: one **business**
   (the demo account) and one **personal**.
3. Put the app's sandbox Client ID + Secret and the two account emails into
   `.env` (see `.env.example` for the exact key names). `.env` is gitignored.

## Access spike

Before any module code, the project runs a hard-gated access spike
(S1 own-account invoice reads → S2 Transaction Search → S3 user-context
reads → S4 seeded drill):

```bash
.venv/bin/python -m spike.run_spike          # writes SPIKE.md + receipts
.venv/bin/python -m spike.seed_demo_account  # S4 seeding helper
```

See `SCOPE.md` for the full plan. Without credentials the spike is skipped
and the app starts in demo account mode (above).

## Stack

Python 3.12 + Flask, SQLite, raw HTTPS to the PayPal sandbox REST API
(no SDK — every request/response stays visible for honest receipts),
vision/text LLM calls for extraction, analysis, and narration; all money
math is deterministic Python.

## License

MIT — see `LICENSE`.
