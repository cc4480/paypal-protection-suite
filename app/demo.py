"""The Demo Account — a sample-data ledger the agents really run on.

Carlos's direction (2026-11-11): the suite carries a lot of
simulation; what it needs is sample DATA the agents run through
all their real motions. So when no sandbox credentials are seated,
the agents do not stop at the door — they operate on this built-in
sample account instead:

  * the ledger holds sample invoices and ~180 days of sample
    transactions in PayPal's own shapes;
  * every read/write goes through the same app/live.py code the
    live sandbox client feeds — invoice search, transaction
    search, cancel + re-read, create + send, history normalize;
  * nothing about the motions is simulated. Only the data is
    sample, and everything it produces is stamped SAMPLE ACCOUNT.

Receipts stay truthful through the existing machinery: each demo
call records a SIMULATED receipt whose reason says the call ran
against the sample ledger and no PayPal API call was made. The
moment real credentials are seated, the routes stop using this
client and the same code runs against PayPal.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import date, timedelta

from .money import format_amount, parse_amount
from .paypal_client import PayPalError
from .receipts import SIMULATED, Receipt, ReceiptLog

DEMO_STAMP = "SAMPLE ACCOUNT"
DEMO_REASON = (
    "demo account (sample data) — the call ran against the suite's "
    "built-in sample ledger; no PayPal API call was made"
)
DEMO_RECIPIENT = "buyer-demo@example.com"


# ------------------------------------------------------------------ seed

def _txn(days_ago: int, name: str, code: str, value: str,
         currency: str = "USD", fee: str | None = None,
         subject: str | None = None) -> dict:
    day = date.today() - timedelta(days=days_ago)
    info: dict = {
        "transaction_initiation_date": f"{day.isoformat()}T10:00:00Z",
        "transaction_amount": {"value": value, "currency_code": currency},
        "transaction_event_code": code,
    }
    if fee is not None:
        info["fee_amount"] = {"value": fee}
    if subject:
        info["transaction_subject"] = subject
    payer = (
        {"payer_name": {"alternate_full_name": name}} if name else {}
    )
    return {"transaction_info": info, "payer_info": payer}


def _seed_transactions() -> list[dict]:
    """Sample history with real patterns for AUDITOR to find:
    a forgotten subscription, a price creep, a same-week duplicate,
    recorded fees, and an EUR purchase carrying conversion spread.
    Dates are anchored to today so the 31-/180-day windows the
    agents read always contain the story."""
    rows = []
    for days in (100, 70, 40, 10):  # StreamBox Premium — forgotten sub
        rows.append(_txn(days, "StreamBox Premium", "T0012", "-15.99"))
    music = [(150, "-9.99"), (120, "-9.99"), (90, "-11.99"),
             (60, "-11.99"), (30, "-13.99")]  # MusicWave — price creep
    for days, value in music:
        rows.append(_txn(days, "MusicWave", "T0012", value))
    for days in (20, 18):  # CloudPhotos — charged twice, 2 days apart
        rows.append(_txn(days, "CloudPhotos", "T0012", "-9.99"))
    rows.append(_txn(55, "Buyer — camera lens", "T0006", "250.00",
                     fee="-9.10"))
    rows.append(_txn(25, "Buyer — headphones", "T0006", "89.99",
                     fee="-3.41"))
    rows.append(_txn(45, "", "T0006", "-87.20", currency="EUR",
                     subject="EU Software Store"))
    rows.append(_txn(15, "Paycheck — Studio", "T0006", "1200.00"))
    rows.append(_txn(12, "Corner Grocery", "T0006", "-32.40"))
    rows.append(_txn(8, "Refund — Bookstore", "T0006", "18.50"))
    rows.append(_txn(5, "City Transit", "T0006", "-25.00"))
    return rows


def _seed_invoices() -> list[dict]:
    """Two sample invoices. The fake Norton invoice from the demo
    email is deliberately NOT here — WITNESS's no-match verdict on
    it is earned by a real search that finds nothing."""
    return [
        {
            "id": "DEMO-INV-1001", "status": "SENT",
            "detail": {"invoice_number": "LCR-2026-041",
                       "currency_code": "USD",
                       "note": "Lens calibration — sample invoice."},
            "amount": {"value": "120.00", "currency_code": "USD"},
            "invoicer": {"name": "Lakeside Camera Repair"},
            "primary_recipients": [
                {"billing_info": {"email_address": DEMO_RECIPIENT}}],
            "items": [{"name": "Lens calibration", "quantity": "1",
                       "unit_amount": {"currency_code": "USD",
                                       "value": "120.00"}}],
        },
        {
            "id": "DEMO-INV-1002", "status": "PAID",
            "detail": {"invoice_number": "DPS-1187",
                       "currency_code": "USD",
                       "note": "Poster run — sample invoice."},
            "amount": {"value": "64.50", "currency_code": "USD"},
            "invoicer": {"name": "Downtown Print Shop"},
            "primary_recipients": [
                {"billing_info": {"email_address": DEMO_RECIPIENT}}],
            "items": [{"name": "Poster printing", "quantity": "1",
                       "unit_amount": {"currency_code": "USD",
                                       "value": "64.50"}}],
        },
    ]


def seed_if_empty(conn: sqlite3.Connection) -> None:
    count = conn.execute(
        "SELECT COUNT(*) FROM demo_invoices").fetchone()[0]
    if count:
        return
    for inv in _seed_invoices():
        conn.execute(
            "INSERT INTO demo_invoices (id, payload) VALUES (?, ?)",
            (inv["id"], json.dumps(inv)),
        )
    for detail in _seed_transactions():
        day = detail["transaction_info"][
            "transaction_initiation_date"][:10]
        conn.execute(
            "INSERT INTO demo_transactions (date, detail) VALUES (?, ?)",
            (day, json.dumps(detail)),
        )
    conn.commit()


# ----------------------------------------------------------------- client

class DemoClient:
    """PayPalClient-shaped, backed by the sample ledger.

    Same method shapes as app/paypal_client.py so app/live.py runs
    unchanged. Every call records its SIMULATED receipt with the
    demo reason — the audit trail never pretends a network call
    happened.
    """

    def __init__(self, conn: sqlite3.Connection, receipts: ReceiptLog,
                 module: str = "demo") -> None:
        self.conn = conn
        self.receipts = receipts
        self.module = module
        seed_if_empty(conn)

    # -- plumbing -------------------------------------------------------
    def _record(self, operation: str, summary: dict) -> None:
        self.receipts.record(Receipt(
            module=self.module, operation=operation, mode=SIMULATED,
            method="LOCAL", endpoint="demo-account", http_status=200,
            ok=True,
            detail={"reason": DEMO_REASON, "summary": summary},
        ))

    def _load(self, invoice_id: str) -> dict:
        row = self.conn.execute(
            "SELECT payload FROM demo_invoices WHERE id = ?",
            (invoice_id,),
        ).fetchone()
        if row is None:
            raise PayPalError(404, {
                "name": "RESOURCE_NOT_FOUND",
                "message": f"no demo-account invoice {invoice_id}",
            })
        return json.loads(row[0])

    def _save(self, invoice: dict) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO demo_invoices (id, payload)"
            " VALUES (?, ?)",
            (invoice["id"], json.dumps(invoice)),
        )
        self.conn.commit()

    # -- Invoicing -------------------------------------------------------
    def list_invoices(self, page: int = 1, page_size: int = 100,
                      fields: str | None = None) -> dict:
        rows = self.conn.execute(
            "SELECT payload FROM demo_invoices ORDER BY id").fetchall()
        items = [json.loads(r[0]) for r in rows]
        self._record("invoices_list", {
            "total_items": len(items),
            "invoices": [{"id": i["id"], "status": i["status"]}
                         for i in items],
        })
        return {"items": items, "total_items": len(items)}

    def get_invoice(self, invoice_id: str) -> dict:
        invoice = self._load(invoice_id)
        self._record("invoices_get", {
            "id": invoice_id, "status": invoice["status"]})
        return invoice

    def create_invoice(self, payload: dict) -> dict:
        count = self.conn.execute(
            "SELECT COUNT(*) FROM demo_invoices").fetchone()[0]
        invoice_id = f"DEMO-INV-{1003 + count}"
        total = sum(
            parse_amount(it["unit_amount"]["value"])
            * int(it.get("quantity", "1"))
            for it in payload.get("items", [])
        )
        invoice = {
            **payload,
            "id": invoice_id,
            "status": "DRAFT",
            "amount": {
                "value": format_amount(total),
                "currency_code": (payload.get("detail") or {}).get(
                    "currency_code", "USD"),
            },
        }
        self._save(invoice)
        self._record("invoices_create", {
            "id": invoice_id, "status": "DRAFT"})
        return {
            "id": invoice_id, "status": "DRAFT",
            "links": [{
                "rel": "self",
                "href": "https://demo.paypal-suite.local"
                        f"/v2/invoicing/invoices/{invoice_id}",
            }],
        }

    def send_invoice(self, invoice_id: str, note: str = "",
                     send_to_recipient: bool = True) -> dict:
        invoice = self._load(invoice_id)
        invoice["status"] = "SENT"
        self._save(invoice)
        self._record("invoices_send", {
            "id": invoice_id, "status": "SENT"})
        return {"id": invoice_id, "status": "SENT"}

    def cancel_invoice(self, invoice_id: str, note: str = "") -> dict:
        invoice = self._load(invoice_id)
        invoice["status"] = "CANCELLED"
        self._save(invoice)
        self._record("invoices_cancel", {
            "id": invoice_id, "status": "CANCELLED"})
        return {"id": invoice_id, "status": "CANCELLED"}

    def record_invoice_payment(self, invoice_id: str,
                               amount_value: str, currency: str = "USD",
                               method: str = "OTHER") -> dict:
        invoice = self._load(invoice_id)
        invoice["status"] = "PAID"
        self._save(invoice)
        self._record("invoices_record_payment", {
            "id": invoice_id, "status": "PAID"})
        return {"id": invoice_id, "status": "PAID"}

    # -- Transaction Search ----------------------------------------------
    def list_transactions(self, start, end, **kw) -> list[dict]:
        rows = self.conn.execute(
            "SELECT detail FROM demo_transactions"
            " WHERE date >= ? AND date <= ? ORDER BY date",
            (start.date().isoformat(), end.date().isoformat()),
        ).fetchall()
        details = [json.loads(r[0]) for r in rows]
        self._record("transactions_list", {
            "total_items": len(details), "returned": len(details)})
        return details
