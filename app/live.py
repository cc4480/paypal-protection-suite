"""Live PayPal operations — the wiring between the agents and the sandbox.

Everything here takes a PayPalClient-shaped object (the real client in
app/paypal_client.py, a fake in tests) and performs the account reads
and writes the three agents promise:

  WITNESS  — read the account's invoices + recent transactions as
             evidence; cancel an invoice and re-read its status.
  SEATBELT — create + send the protected Goods & Services invoice, with
             the fee math computed here, never by the AI.
  AUDITOR  — pull Transaction Search history and normalize it into the
             record shape app/agents.py computes figures from.

Every client call records its own LIVE SANDBOX receipt inside the
client; this module adds no stamps of its own.
"""

from __future__ import annotations

import time
from datetime import datetime, timedelta, timezone

from .money import format_amount, parse_amount
from .paypal_client import invoice_id_from_create_response

# PayPal's published Goods & Services rate (seatbelt prompt ground
# truth): 3.49% + $0.49. Fee figures computed from it are estimates and
# are labeled computed wherever they are shown.
GS_FEE_RATE_NUM = 349
GS_FEE_FIXED_CENTS = 49


# ---------------------------------------------------------------- WITNESS

def _slim_transaction(detail: dict) -> dict:
    ti = detail.get("transaction_info", {}) or {}
    payer = detail.get("payer_info", {}) or {}
    name = (payer.get("payer_name", {}) or {}).get("alternate_full_name")
    return {
        "type": "transaction",
        "date": (ti.get("transaction_initiation_date") or "")[:10],
        "counterparty": name or ti.get("transaction_subject") or "unknown",
        "amount": (ti.get("transaction_amount", {}) or {}).get("value"),
        "event_code": ti.get("transaction_event_code"),
        "invoice_id": ti.get("invoice_id"),
    }


def witness_evidence(client, extracted: dict) -> tuple[list, dict | None]:
    """Read the account for WITNESS: the claimed invoice + recent txns.

    Returns (evidence, invoice_summary). The claimed invoice matches on
    the resource id or on the invoice number the extraction read.
    """
    evidence: list[dict] = []
    invoice_summary = None
    claimed = extracted.get("invoice_id")
    body = client.list_invoices()
    for item in body.get("items", []) or []:
        number = (item.get("detail") or {}).get("invoice_number")
        if claimed and claimed in (item.get("id"), number):
            invoice_summary = {
                "id": item.get("id"),
                "invoice_number": number,
                "status": item.get("status"),
                "amount": (item.get("amount") or {}).get("value"),
            }
            evidence.append({"type": "invoice", **invoice_summary})
            break
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=31)
    for detail in client.list_transactions(start, end)[:50]:
        evidence.append(_slim_transaction(detail))
    return evidence, invoice_summary


def decline_invoice(client, invoice_id: str) -> dict:
    """Cancel the invoice in the account, then re-read its status."""
    before = client.get_invoice(invoice_id)
    client.cancel_invoice(
        invoice_id,
        note="Declined from the PayPal Protection Suite (WITNESS).",
    )
    after = client.get_invoice(invoice_id)
    return {
        "invoice_id": invoice_id,
        "status_before": before.get("status"),
        "status_after": after.get("status"),
    }


# --------------------------------------------------------------- SEATBELT

def gs_fee_cents(total_cents: int) -> int:
    """PayPal's Goods & Services fee on a total: 3.49% + $0.49."""
    return (total_cents * GS_FEE_RATE_NUM + 5000) // 10000 \
        + GS_FEE_FIXED_CENTS


def invoice_total(amount_cents: int, fee_choice: str) -> tuple[int, int]:
    """(total_cents, fee_cents) for a who-covers-the-fee choice."""
    if fee_choice == "seller":
        total = amount_cents
    elif fee_choice == "buyer":
        # Gross up so the recipient nets the full amount after the fee.
        total = -(-(amount_cents + GS_FEE_FIXED_CENTS) * 10000
                  // (10000 - GS_FEE_RATE_NUM))
    elif fee_choice == "split":
        total = amount_cents + gs_fee_cents(amount_cents) // 2
    else:
        raise ValueError(f"unknown fee choice: {fee_choice!r}")
    return total, gs_fee_cents(total)


_FEE_NOTES = {
    "buyer": "Buyer covers the PayPal Goods & Services fee.",
    "seller": "Seller covers the PayPal Goods & Services fee.",
    "split": "The PayPal Goods & Services fee is split buyer/seller.",
}


def convert_deal(client, *, item: str, amount_cents: int, serial: str,
                 fee_choice: str, recipient_email: str,
                 invoicer_email: str = "") -> dict:
    """Create + send the protected G&S invoice; return its live summary."""
    total, fee = invoice_total(amount_cents, fee_choice)
    number = f"SB-{int(time.time())}"
    description = item if not serial else f"{item} — serial/ID: {serial}"
    payload: dict = {
        "detail": {
            "invoice_number": number,
            "currency_code": "USD",
            "note": (
                "Protected Goods & Services invoice created by SEATBELT "
                "(PayPal Protection Suite). " + _FEE_NOTES[fee_choice]
                + " Evidence checklist: keep the chat, photograph the "
                "item and serial at handoff, keep this invoice and the "
                "payment confirmation."
            ),
            "term": "Pay on receipt through this invoice only — "
                    "never Friends & Family.",
        },
        "primary_recipients": [
            {"billing_info": {"email_address": recipient_email}}
        ],
        "items": [{
            "name": (item or "Item")[:120],
            "description": description[:1000],
            "quantity": "1",
            "unit_amount": {
                "currency_code": "USD",
                "value": format_amount(total),
            },
        }],
    }
    if invoicer_email:
        payload["invoicer"] = {"email_address": invoicer_email}
    created = client.create_invoice(payload)
    invoice_id = invoice_id_from_create_response(created)
    client.send_invoice(
        invoice_id,
        note="Your protected Goods & Services invoice from SEATBELT.",
    )
    after = client.get_invoice(invoice_id)
    return {
        "invoice_id": invoice_id,
        "invoice_number": number,
        "status": after.get("status"),
        "item": item,
        "amount": format_amount(amount_cents),
        "fee_choice": fee_choice,
        "fee_estimate": format_amount(fee),
        "total_charged": format_amount(total),
        "recipient": recipient_email,
        "stamp": "LIVE SANDBOX",
    }


# ---------------------------------------------------------------- AUDITOR

_AUTOMATIC_CODES = {"T0012", "T0013"}  # pre-approved / billing-agreement


def normalize_transactions(details: list[dict]) -> list[dict]:
    """Transaction Search details -> AUDITOR's record shape.

    Amounts are stored as positive strings (direction lives in `kind`);
    fees are stored as negative strings, matching the fixture shape
    app/agents.py computes from. Non-USD rows are marked converted at
    the disclosed spread rate, labeled computed downstream.
    """
    out: list[dict] = []
    for d in details:
        ti = d.get("transaction_info", {}) or {}
        payer = d.get("payer_info", {}) or {}
        amount_info = ti.get("transaction_amount", {}) or {}
        fee_info = ti.get("fee_amount", {}) or {}
        try:
            amount_cents = parse_amount(amount_info.get("value"))
            fee_cents = parse_amount(fee_info.get("value") or "0.00")
        except ValueError:
            continue
        code = ti.get("transaction_event_code") or ""
        if code in _AUTOMATIC_CODES:
            kind = "automatic_payment"
        elif amount_cents < 0:
            kind = "goods_services_sent"
        else:
            kind = "goods_services_received"
        name = (
            (payer.get("payer_name") or {}).get("alternate_full_name")
            or ti.get("transaction_subject")
            or "Unknown counterparty"
        )
        record = {
            "date": (ti.get("transaction_initiation_date") or "")[:10],
            "counterparty": name,
            "kind": kind,
            "amount": format_amount(abs(amount_cents)),
            "fee_amount": format_amount(-abs(fee_cents)),
        }
        currency = amount_info.get("currency_code")
        if currency and currency != "USD":
            record["converted"] = True
            record["spread_rate_pct"] = "4.00"
        out.append(record)
    return out


def pull_history(client, days: int = 180) -> list[dict]:
    """Live AUDITOR pull: Transaction Search over the last `days`."""
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=days)
    return normalize_transactions(client.list_transactions(start, end))
