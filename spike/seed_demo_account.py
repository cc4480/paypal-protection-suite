"""S4 seeding helper — run: python -m spike.seed_demo_account

Creates the invoice-side demo shapes on the sandbox BUSINESS (demo)
account via the Invoicing API, idempotently (existing invoice numbers are
skipped):

  1. The fake-renewal invoice — sent, UNPAID. Item: "Norton 360 Deluxe —
     Annual Renewal", $499.99, note carries a 555 phone number (the scam
     pattern Module A exists for). Recipient: the sandbox personal acct.
  2. One PAID invoice — created, sent, then an external payment recorded
     against it so its status flips to PAID.

What the API cannot seed: real transaction history (subscriptions, a
duplicate charge, a creeped price). Those need payments between sandbox
accounts — do them by hand in the sandbox (send money from the personal
account to the business account: the same $9.99 twice in one week for the
duplicate; $9.99 then $13.99 a month apart for the creep). The spike's S4
step reports which shapes are still missing after each run.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app import db  # noqa: E402
from app.config import AppConfig, load_dotenv  # noqa: E402
from app.paypal_client import (  # noqa: E402
    PayPalClient,
    invoice_id_from_create_response,
)
from app.receipts import ReceiptLog  # noqa: E402

RENEWAL_NUMBER = "RENEWAL-2027-001"
PAID_NUMBER = "ORDER-2026-1042"


def _invoice(number: str, recipient: str, item: str, amount: str,
             note: str) -> dict:
    return {
        "detail": {"invoice_number": number, "currency_code": "USD",
                   "note": note, "terms_and_conditions": "Demo data."},
        "invoicer": {"name": {"given_name": "Demo", "surname": "Merchant"}},
        "primary_recipients": [
            {"billing_info": {"name": {"given_name": "Demo",
                                       "surname": "Buyer"},
                              "email_address": recipient}}
        ],
        "items": [{"name": item, "quantity": "1",
                   "unit_amount": {"currency_code": "USD", "value": amount}}],
        "amount": {"currency_code": "USD", "value": amount},
    }


def main() -> int:
    load_dotenv()
    cfg = AppConfig()
    if not cfg.paypal.has_credentials:
        print("BLOCKED: missing .env keys: "
              + ", ".join(cfg.paypal.missing_keys))
        return 2
    recipient = cfg.paypal.personal_email
    if not recipient:
        print("BLOCKED: PAYPAL_PERSONAL_EMAIL not set — invoices need a "
              "recipient (the sandbox personal test account).")
        return 2

    conn = db.connect(cfg.database_path)
    client = PayPalClient(cfg.paypal, ReceiptLog(conn), module="seed")
    existing = {  # idempotency: never seed the same invoice number twice
        (i.get("detail") or {}).get("invoice_number"): i.get("id")
        for i in client.list_invoices(page=1, page_size=100).get("items", [])
    }

    if RENEWAL_NUMBER in existing:
        print(f"skip renewal invoice (exists: {existing[RENEWAL_NUMBER]})")
    else:
        created = client.create_invoice(_invoice(
            RENEWAL_NUMBER, recipient,
            "Norton 360 Deluxe - Annual Renewal", "499.99",
            "Your subscription renews today. To cancel, call "
            "1-800-555-0142 within 24 hours."))
        inv_id = invoice_id_from_create_response(created)
        client.send_invoice(inv_id, note="Demo seed: fake renewal, unpaid.")
        print(f"created + sent UNPAID renewal invoice {inv_id}")

    if PAID_NUMBER in existing:
        print(f"skip paid invoice (exists: {existing[PAID_NUMBER]})")
    else:
        created = client.create_invoice(_invoice(
            PAID_NUMBER, recipient, "USB-C Docking Station", "129.00",
            "Demo seed: a real, paid order."))
        inv_id = invoice_id_from_create_response(created)
        client.send_invoice(inv_id)
        client.record_invoice_payment(inv_id, "129.00")
        status = client.get_invoice(inv_id).get("status")
        print(f"created + paid invoice {inv_id} (status now {status})")

    print("Reminder: subscription/duplicate/creep history is seeded by "
          "hand between the sandbox accounts (see module docstring).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
