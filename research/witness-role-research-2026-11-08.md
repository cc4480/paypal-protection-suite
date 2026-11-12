# WITNESS — Real PayPal Role Research (2026-11-08)

PayPal-first web research for the PayPal Protection Suite's WITNESS agent (fake-invoice guardian).
Rule applied: actual PayPal roles/policies only, each claim sourced; where PayPal publishes nothing, stated plainly.

## Headline finding
There is NO single published PayPal job titled "fake-invoice investigator" or anything like it. The work WITNESS
mirrors is split across three real, named PayPal functions:
1. **Risk Analyst — Global Scam Risk team** (closest match: scam-specific, victim-protection mission)
2. **Analyst, Risk Management — "Customer Protection & Loss Prevention"** function (PayPal's own posting names INVOICE as a high-risk area)
3. **Fraud Operations Specialist / Analyst, Risk Operations** (queue triage + investigations)
…plus two PayPal *systems*, not people: the in-account **Report/Cancel/Decline** flow for suspicious invoices/requests, and the **Resolution Center** unauthorized-activity investigation.
Oversight org for investigations: **Global Financial Crimes & Customer Protection (GFC&CP / GFCCP)**, home of **Global Investigations**.

## 1. Exact real titles at PayPal (with sources)
- **Risk Analyst** (Global Scam Risk team), REQ ID R0110609 — "specialize in creating, driving, and executing solutions to mitigate scam on PayPal's platform and protect many innocent users globally… The global scam risk team is responsible for reducing the loss generated from scam." Source: PayPal posting mirrored at jobaaj.com/job/paypal-risk-analyst-bengaluru-karnataka-india-0-to-15-years-400427
- **Analyst, Risk Management** — posting section 3 is literally headed "Customer Protection & Loss Prevention": "Identify and mitigate fraud, declines, and collusion, particularly in high-risk areas such as invoice and Business Account creation." Source: builtin.com/job/analyst-risk-management/6886082 (PayPal posting, published 2025-10-30)
- **Fraud Operations Specialist** (title used inside the "Analyst, Risk Operations" posting) — monitor real-time queues, identify high-risk activity, validate info with customers/institutions. Source: jobs.anitab.org/companies/paypal/jobs/67626811-analyst-risk-operations
- **Analyst, Risk Operations** (SME variant) — "complete risk investigations… analyzing and prioritizing internal and external escalations." Source: jobs.anitab.org/companies/paypal/jobs/69438892-analyst-risk-operations
- **Sr Analyst, Global Investigations** — Fraud Incident Manager within FIRM (Fraud Incident Response and Management), part of Fraud & Insider Defense (FIND), for complex fraud attacks — escalation tier, NOT the front-line invoice role. Source: apna.co listing of PayPal posting.
- **Special Investigations Analyst** (Global Investigations, under GFC&CP) — internal fraud/insider matters; adjacent, not the consumer invoice role. Source: indeed.com listing of PayPal posting.

## 2. Actual responsibilities (itemized, sourced)
From the **Risk Analyst (scam team)** posting:
- Thoroughly examine customer account activity and information to uncover potential fraudulent activities or reasons behind dispute filings; differentiate customers with malicious intent from those genuinely raising disputes.
- Review suspicious accounts to validate the solution's accuracy.
- Monitor scam activity across PayPal's products, identify patterns, "address the scammers to protect the innocent users."
- Identify gaps in processes that impact users (analytics + manual account reviews).
From the **Analyst, Risk Management** posting:
- Identify and mitigate fraud/collusion in high-risk areas "such as invoice and Business Account creation" while keeping customer experience seamless.
- Analyze large datasets to detect emerging fraud patterns; streamline dispute resolution workflows; maintain SOPs.
From **Fraud Operations Specialist** duties:
- Monitor real-time queues, identify high-risk activity; conduct periodic internal account reviews for suspicious activity; interact with financial institutions and customers to validate information; complete reporting per policies/procedures.
From **PayPal Help Center** (what the user-facing side of this work instructs — the behavior WITNESS must mirror):
- Suspicious invoice/request: don't pay it; don't call phone numbers in the note; don't open suspicious links; never send payment to a crypto wallet in the note. (help1059, help201)
- Cancel in Activity (web) or Decline in the app; report in-account via "Report this invoice"/"Report". (help995)
- Suspicious EMAIL/website (not in-account): forward to phishing@paypal.com, then delete it; "We'll investigate it for you." (help1059/help201)
- If money actually moved without authorization: report via Resolution Center ("I want to report unauthorized activity"); PayPal investigates; email answer within 10 days. (help136)

## 3. Limits — what the role can NOT do (sourced)
- An invoice/money request is NOT a charge: PayPal's systems show it "Pending" until paid (PayPal Help, reminder article); Invoicing API lifecycle is DRAFT → SENT → UNPAID → PAID only when a payment is recorded (developer.paypal.com invoicing docs). Nobody at PayPal treats an unpaid invoice as money moved — WITNESS must not either.
- An unpaid invoice has nothing to refund: to request a refund for a COMPLETED payment, "you'll need to contact the seller" (help136).
- Purchase Protection does NOT cover unauthorized transactions — those are a different claim type under the User Agreement's "Liability for Unauthorized Transactions and Other Errors"; Purchase Protection itself covers only Item Not Received and Significantly Not As Described (PayPal Purchase Protection program page, updated 2026-01-26).
- Error/unauthorized protection is time-boxed: PayPal's EFT Error Resolution terms reimburse in full only for unauthorized transactions reported within 60 days of notice/awareness; investigation results within 10 business days (20 for POS/outside US) (paypal.com EFT rights page).
- Investigative roles work from PayPal's own data/tools: postings describe internal tools, queues, account reviews — no authority over the victim's bank, email provider, or the scammer's phone carrier is published anywhere. Plain gap: PayPal does NOT publish what happens internally after a user taps "Report this invoice," nor any SLA for it.
- Compliance investigators (Analyst, Compliance Investigations) work under FinCEN/OFAC + the Acceptable Use Policy and PayPal's Ethics and Compliance Standards — that's the AML org, a different job from the scam/invoice roles; do not merge them into WITNESS.

## 4. Policies / systems the role works under
- PayPal Help Center articles help1059 ("What are invoice scams and payment request scams"), help995 (cancel/report a suspicious request or invoice), help201 (common scams), help136 (report unauthorized activity).
- Resolution Center (unauthorized activity investigations).
- phishing@paypal.com intake ("We'll investigate it for you").
- User Agreement: Liability for Unauthorized Transactions and Other Errors; EFT Rights and Error Resolution (60-day rule, 10-business-day investigation answer).
- Purchase Protection program terms (INR/SNAD only).
- PayPal Invoicing product/API: invoice lifecycle statuses DRAFT/SENT/UNPAID/PAID/PARTIALLY_PAID/CANCELLED — the mechanical definition of "money moved."
- Acceptable Use Policy (referenced by the compliance/investigations postings).

## 5. WITNESS job description (grounded only in the above)
"WITNESS works the job of PayPal's scam-risk and customer-protection analysts at the single-user scale: when a frightening 'PayPal invoice' arrives, it examines the claim against the account's real activity — the same check PayPal's Help Center prescribes — and states the one fact that decides everything: whether any money actually moved (an unpaid invoice sits at Pending/UNPAID and is not a charge). If nothing moved, WITNESS walks the user through PayPal's own remedy — cancel or decline it in Activity, report it in-account, forward any fake email to phishing@paypal.com and delete it — and never lets the user call a number printed in the invoice. If money did move without authorization, WITNESS builds the recovery packet for the only channel PayPal offers for that: a Resolution Center unauthorized-activity report, inside the User Agreement's timeframes. Like the analysts it mirrors, it works only from the account's own records, documents everything it found, and claims no power PayPal itself doesn't give the real role — no refunds of unpaid invoices, no promises outside PayPal's stated protections."

## Confidence notes
- Titles + scam-team duties: HIGH (PayPal postings, mirrors of careers.pypl.com text with REQ ID).
- Invoice-area duty in Analyst, Risk Management: HIGH (posting text verbatim).
- Help Center flows, Resolution Center 10-day email, phishing intake: HIGH (paypal.com pages read directly).
- 60-day / 10-business-day figures: HIGH for PayPal's published EFT terms (older legal page, still live on paypal.com — regional variants differ).
- "What PayPal does internally with an invoice report": NOT PUBLISHED — deliberately left blank, not filled with boilerplate.
