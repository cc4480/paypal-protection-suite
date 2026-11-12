# AUDITOR — Real PayPal Role Research (2026-11-08)

Task: research AUDITOR's title and job — exactly what it does FOR PAYPAL, actual roles/responsibilities, PayPal-first sources only. Confidence scored per claim. Where PayPal publishes nothing, it says so.

AUDITOR (suite definition): one-time X-ray of a user's own PayPal history — forgotten subscriptions/automatic payments, duplicate charges, price creep, true total of fees + currency-conversion spread paid. Figures deterministic; AI only narrates.

## 1. Exact real title(s) at PayPal for this work

**Headline finding: PayPal publishes NO consumer-facing role or employee title called "Auditor" for reviewing a user's own account history.** That review work is split in two in PayPal's real world: (a) the account holder does it themselves with Activity / Statements / Resolution Center (Help Center), and (b) inside PayPal, the reconciliation-and-analysis of payment/billing activity sits with analyst/accountant titles in Global Billing and Payments / Global Finance Operations. Confidence 0.85 (based on PayPal Help, developer docs, fee pages, and careers postings searched 2026-11-08; absence can't be proven absolutely).

Real PayPal titles found, PayPal-sourced:
- **Finance Business Support Analyst** — "The PayPal Global Billing and Payments department is seeking a Finance Business Support Analyst to support … finance and other funds out operations." Posted on PayPal's own Workday ATS (wd1.myworkdaysite.com/recruiting/paypal/jobs, req R0138563, published 2026-10-22). Confidence 0.9.
- **Payment Operations Analyst** — PayPal's Global Finance Operations org sought a "Payment Operations Analyst for the Accounts Receivable Operations team": apply payments, resolve unmatched cash, handle complex escalations to SLA (posting reproduced on Built In). Confidence 0.8.
- **Senior Finance Analyst, Business Intelligence, FP&A (Payments Processing Finance)** — "supports the Payments Processing Finance [team] in managing daily finance operations across payment processing activities, with a focus on transaction economics and merchant profitability analysis"; also owns PayPal's Transaction Expense (TE) analysis — "analyze the key drivers of transaction margin." (Simplify Jobs / Career.io reproductions of PayPal postings, Oct 2026.) Confidence 0.8.
- **Reconciliation Accountant** — "responsible for the preparation and analysis of general ledger account reconciliations for multiple PayPal products … analyzing reconciling differences, root cause analysis" (PayPal posting R0079023, reproduced on Huntr). Confidence 0.75.
- **Accounts Payable / Accounts Receivable Analyst** — same essential-responsibility boilerplate: "timely and effective reconciliation of all assigned General Ledger accounts … research and resolve outstanding reconciling items." Confidence 0.8.

## 2. Actual responsibilities (itemized, sourced)

From the PayPal postings above — the real internal version of AUDITOR's job:
1. Reconcile assigned accounts timely and effectively; clear reconciling items per company policy. (Finance Business Support Analyst / AP / AR postings — 0.9)
2. Research, track, and resolve outstanding reconciling items and related issues; root-cause analysis of differences. (Same postings; Reconciliation Accountant — 0.85)
3. Triage and support front-line escalations related to funding, refunds, and funds movement. (Finance Business Support Analyst — 0.85)
4. Execute daily finance operations within SLAs across payment-processing activity; transaction economics / transaction-expense (TE) analysis and margin drivers. (Senior Finance Analyst, Payments Processing Finance — 0.85)
5. Identify and recommend process-improvement opportunities in reporting, reconciliation, and analysis. (Multiple postings — 0.85)

From PayPal's consumer systems — the work AUDITOR automates for the user:
6. Inventory automatic payments: PayPal defines an automatic payment as "also known as a subscription, billing agreement, or recurring payment," managed at Settings → Payments → Subscriptions and saved businesses / Automatic Payments; from there the user can cancel and change the backup payment method. PayPal keeps track of where the account is saved as a payment method. (PayPal Help Center, "What is an automatic payment and how do I update or cancel one?" — 0.95)
7. Review account activity and pull statements/reports: "You can download a report of your transaction activity for up to the past seven years as a PDF, Quicken, QuickBooks, CSV, or TAB file. Your request can include up to 12 months of activity at a time." (PayPal Help Center, "How do I view and download statements and reports?" — 0.95)
8. Retrieve history programmatically: "Use the Transaction Search API to get the history of transactions for a PayPal account" — endpoints for transactions, balances, balance/net-activity summary, and daily summary. (PayPal Developer, Transaction Search v1 — 0.95)
9. Flag billing errors incl. duplicates for remedy: PayPal's own dispute taxonomy classifies "Billing or subscription errors — duplicate charges, multiple transactions, or incorrect amounts"; billing-error cases are handled directly as claims, and "if a buyer is incorrectly charged or charged twice … the account holder can file a claim." PayPal Help's billing-issue article: multiple charges for the same transaction may come from clicking Send Money more than once; remedy is contact the recipient for a refund / report in the Resolution Center. (PayPal Developer disputes overview + PayPal Help "How do I report a billing issue?" — 0.9)
10. Total the fees actually charged: Transaction Search records carry a per-transaction fee_amount ("Total PayPal fees for this transaction") in transaction_info — so fees-paid is a summable field, not an estimate. (PayPal Transaction Search spec, via the official OpenAPI reproduced in DeepWiki/RubyDoc SDK docs — 0.85)

## 3. Limits (what can / can't be seen)

- **API window: 3 years.** Transaction Search "lists transactions for the previous three years"; balances likewise. (PayPal SDK/API docs — 0.9)
- **31 days per query.** Max range per Transaction Search call is 31 days; longer histories need separate calls. Partner endpoint notes a typical 3–6 hour delay before transactions appear; the account-owner API notes up to 3 hours. (PayPal Developer — 0.9)
- **Statements go further than the API: 7 years**, but only 12 months per request. (PayPal Help — 0.95) So a "lifetime" X-ray beyond 3 years is a statements job, not an API job.
- **Third-party access is partner-gated.** "To use the API on behalf of third parties, you must be part of the PayPal partner network." An agent reading *another* user's history needs that enrollment; an agent reading the demo/own account does not. (PayPal Developer — 0.95)
- **Dispute clock: 180 days.** "The buyer has 180 days from the payment date to dispute a transaction"; disputes get up to 20 days to resolve before escalation; billing errors/duplicates go straight to claims. AUDITOR can find an old duplicate, but PayPal's remedy window for it may already be closed. (PayPal Developer disputes — 0.9)
- **Conversion spread: disclosed as a schedule, not itemized per transaction.** PayPal's consumer fee page publishes the spread (below) and says "or such other amount as may be disclosed to you during the transaction." PayPal does NOT publish a per-transaction "spread paid" field separate from the exchange rate applied — so AUDITOR's spread total is necessarily computed from the disclosed spread % and the rates in the records, and must be labeled as such; the hard, exact number in the record is fee_amount. (Inference from the fee page + API field list — 0.7)
- **Price creep has no PayPal-published detection feature.** PayPal publishes no tool, report, or role that tracks a subscription's price rising over time; AUDITOR's price-creep pass is original analysis over the automatic-payment/transaction records, not a mirrored PayPal function. Stated plainly per the task rules. (0.85)

## 4. Policies / systems AUDITOR stands on

- **Consumer fee schedule (PayPal US, paypal.com/us/digital-wallet/paypal-consumer-fees):** sending domestic personal transactions from balance/bank = no fee; cards 2.90% + fixed fee ($0.30 USD fixed for personal). **Currency Conversion Spread: 4.00%** for paying for goods/services in another currency, F&F where the recipient receives a different currency, and Payouts conversions; **3.00% for all other transactions** — in each case "or such other amount as may be disclosed to you during the transaction." Confidence 0.95.
- **Commercial fee schedule (context for any G&S the user received):** US merchant rates widely reproduced from PayPal's merchant fee page — PayPal Checkout 3.49% + $0.49, standard card 2.99% + $0.49, +1.50% international. NOTE: sourced from reproductions of PayPal's page, not the page itself in this pass — confidence 0.75.
- **Automatic Payments system:** subscriptions/billing agreements live in Settings → Payments; canceling there stops future pulls and the funding method can be changed per merchant; agreements can also be set up in-app under Subscriptions / Linked Businesses. (PayPal Help — 0.95)
- **Statements & Reports system:** History/reports + monthly statements (paypal.com/reports/accountStatements); formats PDF/Quicken/QuickBooks/CSV/TAB; large history logs can take up to 5 business days to generate; last 3 large logs saved. (PayPal Help — 0.9)
- **Resolution Center:** the remedy channel AUDITOR's findings point to — report a problem, dispute (180 days), escalate to a claim; unauthorized-activity reports get an email response within 10 days. (PayPal Help + Developer — 0.9)

## 5. AUDITOR job description (grounded only in the above)

AUDITOR is the PayPal Protection Suite's reconciliation analyst for one person's own PayPal account — the consumer mirror of the work PayPal's Global Billing and Payments Finance Business Support Analysts and Payment Operations Analysts do on PayPal's ledgers: pull the account's complete transaction history (Transaction Search, 31 days at a time, back 3 years; statements back 7), reconcile it to the cent, and research every reconciling item. It inventories every automatic payment (subscription / billing agreement) the account carries, detects billing errors in PayPal's own dispute taxonomy — duplicate charges, multiple transactions, incorrect amounts — tracks each recurring charge's price over time, and totals what the account actually paid: the per-transaction fee_amount PayPal records, plus the currency-conversion cost computed at PayPal's disclosed spread (4% on purchases and cross-currency personal payments, 3% on other conversions). Every figure is computed deterministically from the records; the AI only narrates the findings and points each problem at its real remedy — cancel in Settings → Payments, dispute in the Resolution Center inside the 180-day window. AUDITOR never moves money and never invents a number PayPal didn't record or disclose.

## Sources
- PayPal Consumer Fees (US): https://www.paypal.com/us/digital-wallet/paypal-consumer-fees?locale.x=en_US
- PayPal Help — automatic payments (via PayPal's help host): https://poc-dynamic.paypal.com/tm/cshelp/article/what-is-an-automatic-payment-and-how-do-i-update-or-cancel-one-help240
- PayPal Help — statements and reports: https://www.paypal.com/sg/cshelp/article/how-do-i-view-and-download-statements-and-reports-help145
- PayPal Help — report a billing issue: https://www.paypal.com/th/cshelp/article/how-do-i-report-a-billing-issue-help272?locale.x=en_TH
- PayPal Developer — Transaction Search v1: https://developer.paypal.com/api/transaction-search/v1/
- PayPal Developer — Transaction Search API for partners: https://developer.paypal.com/limited-release/commerce-platform/v3/reports/transaction-search-api-for-partners/
- PayPal Developer — disputes overview: https://developer.paypal.com/disputes/overview?mark=subscribe
- PayPal careers (Workday ATS) — Finance Business Support Analyst R0138563: https://wd1.myworkdaysite.com/recruiting/paypal/jobs/job/Bangalore-Karnataka-India/Finance-Business-Support-Analyst_R0138563?utm_source=jobsbylevel&utm_medium=job_board&utm_campaign=apply
- PayPal posting reproductions: Senior Finance Analyst (Simplify Jobs), Sr Analyst FP&A / Transaction Expense (Career.io), Payment Operations Analyst + AP/AR Analysts (Built In), Reconciliation Accountant (Huntr).
- Official Transaction Search OpenAPI constraints/fields (DeepWiki mirror of paypal/paypal-rest-api-specifications; RubyDoc PayPal Server SDK docs).

## What PayPal does not publish (gaps, plainly)
- No consumer "auditor" title or own-history audit service.
- No per-transaction currency-spread-paid field (spread is schedule-disclosed: 4%/3%).
- No price-creep tracking feature or role.
- The merchant fee page itself was not opened in this pass (rates above are from reproductions — re-verify against paypal.com before publishing them in the app).
