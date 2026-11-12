# WITNESS — PayPal-grounded role research (2026-11-08)
Full report: ~/workspace/paypal-suite/research/witness-role-research-2026-11-08.md

**Headline:** No single published PayPal job titled anything like "fake-invoice investigator" (stated plainly). The work splits across three real named functions + two PayPal systems (in-account Report/Cancel/Decline flow; Resolution Center unauthorized-activity investigation). Investigations org above them: **Global Financial Crimes & Customer Protection (GFC&CP)**, home of Global Investigations.

## Real titles
- **Risk Analyst — Global Scam Risk team** (REQ R0110609) — closest single match: "specialize in creating, driving, and executing solutions to mitigate scam on PayPal's platform… responsible for reducing the loss generated from scam." Conf high.
- **Analyst, Risk Management** — posting section literally headed "Customer Protection & Loss Prevention": "Identify and mitigate fraud, declines, and collusion, particularly in high-risk areas such as INVOICE and Business Account creation." Conf high.
- **Fraud Operations Specialist / Analyst, Risk Operations** — queue triage, investigations. Conf high.
- NOT Witness's tier (flagged to prevent inflation): Sr Analyst Global Investigations / Special Investigations Analyst — complex/internal-fraud escalation tier.

## What the real roles do (posting-verbatim)
Examine account activity to uncover fraud vs genuine disputes; review suspicious accounts; monitor scam activity across products, identify patterns, "address the scammers to protect the innocent users"; mitigate fraud/collusion in invoice creation; analyze large datasets for emerging fraud patterns; maintain SOPs; monitor real-time high-risk queues; validate info with customers and financial institutions.

## User-facing behavior Witness must mirror (PayPal Help, read directly: help1059/995/201/136)
Don't pay a suspicious invoice; NEVER call phone numbers in the invoice note; never pay a crypto wallet named in the note; Cancel (web) / Decline (app) in Activity; report in-account via "Report this invoice"; forward suspicious email to phishing@paypal.com then delete it; if money actually moved without authorization → Resolution Center report; PayPal investigates, emails within 10 days.

## Limits / ground truth
- An invoice/money request is NOT a charge: requests show "Pending" until paid; Invoicing API lifecycle DRAFT → SENT → UNPAID → PAID only when payment recorded. This is the mechanical ground truth for "did money actually move?"
- Unpaid invoice has nothing to refund; completed payment → "contact the seller."
- Purchase Protection does NOT cover unauthorized transactions (only INR/SNAD); unauthorized claims live under the UA's Liability for Unauthorized Transactions section.
- EFT Error Resolution: full reimbursement promised only for unauthorized transactions reported within 60 days; investigation results in 10 business days (20 POS/outside US).
- GAP stated plainly: PayPal does not publish what happens internally after "Report this invoice," nor any SLA for it. Left blank, not filled with boilerplate.

## Grounded job description
Witness works the scam-risk/customer-protection analyst job at single-user scale: examines the claim against the account's real activity, states the deciding fact (did money move — an unpaid invoice sits at Pending/UNPAID and is not a charge), walks PayPal's own remedy (cancel/decline, report in-account, forward to phishing@paypal.com, never call the number in the note), and if money did move unauthorized, builds the packet for a Resolution Center unauthorized-activity report inside the UA timeframes. Claims no power PayPal doesn't give the real role.
