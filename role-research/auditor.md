# AUDITOR — PayPal-grounded role research (2026-11-08)
Full report: ~/workspace/paypal-suite/research/auditor-role-research-2026-11-08.md

**Headline:** PayPal publishes NO consumer-facing role/title called "Auditor" for reviewing a user's own history (conf 0.85). In PayPal's world the account holder does it themselves (Activity/Statements/Resolution Center); inside PayPal it sits with analyst/accountant titles in Global Billing and Payments / Global Finance Operations.

## Real titles
- **Finance Business Support Analyst** — Global Billing and Payments (PayPal's own Workday ATS, req R0138563) — conf 0.9.
- **Payment Operations Analyst** — Global Finance Operations, Accounts Receivable Operations — 0.8.
- **Senior Finance Analyst, Payments Processing Finance / FP&A** — owns transaction economics + Transaction Expense analysis — 0.8.
- **Reconciliation Accountant** (R0079023) — GL reconciliations, root-cause analysis — 0.75.

## What the real work is
Reconcile assigned accounts to the cent, clear/research/resolve reconciling items with root cause; triage escalations on funding/refunds/funds movement; daily payment-processing finance ops within SLAs; transaction-expense/margin analysis. Consumer systems Auditor automates: automatic-payments inventory ("also known as a subscription, billing agreement, or recurring payment" — Settings → Payments → Subscriptions, conf 0.95); activity/statements review (0.95); Transaction Search pulls (0.95); billing-error flags in PayPal's OWN dispute taxonomy ("duplicate charges, multiple transactions, or incorrect amounts" are named billing/subscription errors, 0.9); fee totals — every Transaction Search record carries per-transaction **fee_amount**, so fees-paid is SUMMABLE, not estimated (0.85).

## Limits (hard, PayPal-sourced)
- Transaction Search API: previous **3 years only, max 31 days per query, ~3-hour appearance delay** (0.9). Third-party use = partner-gated (0.95).
- Statements reach **7 years, 12 months per request** — an X-ray beyond 3 years is a statements job, not an API job (0.95).
- Dispute clock: 180 days from payment; an old duplicate can be FOUND after its remedy window closed (0.9).
- Conversion spread is schedule-disclosed, NOT itemized per transaction — no per-transaction "spread paid" field exists; Auditor's spread total must be computed from the disclosed % and LABELED as computed. The exact recorded number is fee_amount (0.7).
- Price creep: PayPal publishes NO feature/report/role for it — that pass is Auditor's ORIGINAL analysis, not a mirrored PayPal function (0.85).

## PayPal numbers Auditor speaks
- Consumer fees: domestic personal from balance/bank no fee; cards 2.90% + fixed (US fee page, 0.95).
- Currency Conversion Spread: **4.00%** (goods/services in another currency, cross-currency F&F, Payouts), **3.00%** all other transactions (0.95).
- Commercial (0.75, from reproductions — re-verify before publishing in-app): Checkout 3.49% + $0.49; standard card 2.99% + $0.49; +1.50% international.

## Grounded job description
Auditor = reconciliation analyst for one person's own account (consumer mirror of PayPal's Global Billing & Payments analysts): pulls complete history (API 31 days at a time back 3 years; statements back 7), reconciles to the cent, inventories every automatic payment, detects billing errors in PayPal's own taxonomy, tracks recurring-charge prices over time, totals real fees (fee_amount) + conversion cost at disclosed spreads (4%/3%, labeled computed). AI only narrates; every finding points at its real remedy (cancel in Settings → Payments; dispute in Resolution Center inside 180 days). Never moves money, never invents a number PayPal didn't record or disclose.
