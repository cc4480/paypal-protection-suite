# RECEIPTS seat — PayPal-grounded role research (2026-11-08)

**Headline:** PayPal publishes NO dedicated "records keeper / receipts / case documentation" job title. The case-documentation work lives INSIDE the disputes/claims customer-operations roles. Anyone claiming a standalone PayPal "Evidence Specialist" title is inventing it (researcher confidence 0.8 that the absence is genuine).

## Real titles (same family as Seatbelt)
- **Payments & Disputes Specialist** (inside "Customer Solutions Teammate (Payments)" posting, Account Protection & Financial Services) — conf 0.85, via Indeed mirror of PayPal's own posting text.
- **Customer Service Teammate — Disputes and Claims** — conf 0.85, via WayUp mirror.
- Umbrella family: Customer Solutions Teammate / Customer Solution Agent 2 — conf 0.8.
- Caveat: sources are job-board MIRRORS of PayPal postings, not paypal.com pages; wording is PayPal's. Third-party "dispute specialist" postings (merchants hiring people to fight PayPal) were EXCLUDED — not PayPal roles.

## What the real function actually does (PayPal-sourced)
1. Resolution Center is the single system of record — cases, prompts, evidence requests all live there (conf 0.95).
2. Respond to evidence requests with the SPECIFIC proof type requested, before the case deadline (Seller Protection: proof generally within 10 days) (0.9).
3. Proof must meet PayPal's exact definitions: proof of delivery = carrier doc with delivery DATE + "delivered" status + recipient ADDRESS; proof of shipment = date + recipient address; intangibles = "compelling evidence" (system-of-record showing date provided) (0.9).
4. Evidence goes through the Resolution Center's own upload flow, WITH a short description attached (FAQ1455) (0.9).
5. Keep/retrieve the transaction record: statements via History → Download or paypal.com/reports/accountStatements (0.95).
6. Data access/copy requests via Privacy "Data and Privacy" settings (0.9).
7. Programmatic mirror: Disputes API submits typed evidence (PROOF_OF_FULFILLMENT, PROOF_OF_REFUND, OTHER), notes ≤2,000 chars, docs attached (0.9).

## Limits / deadlines the seat must speak
- Dispute open: within 180 days of payment. Dispute stage: 20 days, then escalate or it closes (generally cannot reopen). Claim evidence response: ~10 days. Appeal: 10 days, WITH NEW information — resubmitting the same docs is a known failure mode (0.85–0.9).
- Miss the Resolution Center deadline → can lose protection eligibility (0.9).
- Signature confirmation required for Seller Protection at ≥$750 USD (0.9).
- Evidence files (Disputes API): <10 MB per file, ≤50 MB per request, JPG/JPEG/GIF/PNG/PDF only (0.9). (Braintree limits differ — don't mix.)
- Rejected in practice (PayPal-documented): proof-of-delivery address ≠ transaction address; redirected shipments; late uploads (0.85).
- User-pullable records: up to 7 YEARS of activity, ≤12 months per request, PDF/CSV/TAB/Quicken/QuickBooks; large logs up to 5 business days, only last 3 large logs saved (0.95).
- PayPal retention of personal data: relationship + 10 years (EU statement); US statement gives principle, no flat number (0.85).
- NOT published: how long PayPal internally retains closed-case evidence files; any internal case-documentation QA standard. Unknown from public sources.

## Grounded job description
RECEIPTS = Case Records & Evidence Keeper (mirrors the Payments & Disputes Specialist function): the suite's system of record — every PayPal call logged and stamped LIVE SANDBOX vs SIMULATED, every verdict tied to the API response that produced it; assembles the recovery packet (transaction record, claim timeline 180/20/~10/10, evidence files in PayPal-accepted formats, described and labeled). Decides nothing, invents nothing.

Sources: PayPal Resolution Center + Seller Protection articles, FAQ1455, statements help (HELP145), Privacy Principles, Disputes API docs, PayPal postings via Indeed/WayUp (full URLs in researcher report, 2026-11-08).
