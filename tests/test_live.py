"""Tests for the live PayPal wiring (app/live.py + agent endpoints).

A FakePayPal stands in for PayPalClient: canned sandbox-shaped data,
recorded calls, no network. These tests pin the promises the demo
makes: WITNESS reads the account before it rules (a decisive verdict
survives only with that check behind it), the decline action flips
an invoice's status via cancel + re-read, SEATBELT's fee math and
invoice payload are code-computed, and AUDITOR's live pull feeds the
same deterministic figures as the labeled sample path.
"""

import pytest

from app import agent_routes, agents, live
from app.config import AppConfig
from app.routes import create_app


class FakeDeepSeek:
    def __init__(self):
        self.payloads = []

    def chat_json(self, seat, payload):
        self.payloads.append((seat, payload))
        if seat == "witness":
            return {
                "amount": "$499.99", "seller": "Norton LifeLock",
                "invoice_id": "INV-2941", "phone": "1-888-555-0147",
                "verdict": "NO_CHARGE",
                "headline": "No money has left your account.",
                "body": "The invoice is unpaid.",
            }
        if seat == "auditor":
            return {"summary": "Summary.", "top_action": "Act."}
        raise AssertionError(f"unexpected seat {seat}")


TXN_DETAILS = [
    {"transaction_info": {
        "transaction_initiation_date": "2026-10-03T10:00:00Z",
        "transaction_amount": {"value": "9.99", "currency_code": "USD"},
        "fee_amount": {"value": "-0.50"},
        "transaction_event_code": "T0012"},
     "payer_info": {"payer_name": {"alternate_full_name": "CloudPhotos"}}},
    {"transaction_info": {
        "transaction_initiation_date": "2026-10-05T10:00:00Z",
        "transaction_amount": {"value": "9.99", "currency_code": "USD"},
        "fee_amount": {"value": "-0.50"},
        "transaction_event_code": "T0012"},
     "payer_info": {"payer_name": {"alternate_full_name": "CloudPhotos"}}},
    {"transaction_info": {
        "transaction_initiation_date": "2026-10-12T10:00:00Z",
        "transaction_amount": {"value": "-87.20", "currency_code": "EUR"},
        "transaction_event_code": "T0006",
        "transaction_subject": "EU Software Store"},
     "payer_info": {}},
]


class FakePayPal:
    instances: list = []

    def __init__(self, config, receipts, module="x"):
        self.module = module
        self.status = "UNPAID"
        self.created_payload = None
        FakePayPal.instances.append(self)

    def list_invoices(self):
        return {"items": [{
            "id": "INV2-REAL-1", "status": self.status,
            "detail": {"invoice_number": "INV-2941"},
            "amount": {"value": "499.99"},
        }]}

    def get_invoice(self, invoice_id):
        return {"id": invoice_id, "status": self.status}

    def cancel_invoice(self, invoice_id, note=""):
        self.status = "CANCELLED"
        return {}

    def create_invoice(self, payload):
        self.created_payload = payload
        return {"links": [{
            "rel": "self",
            "href": "https://api-m3.sandbox.paypal.com"
                    "/v2/invoicing/invoices/INV2-NEW-9",
        }]}

    def send_invoice(self, invoice_id, note="", send_to_recipient=True):
        self.status = "SENT"
        return {}

    def list_transactions(self, start, end, **kw):
        return TXN_DETAILS


@pytest.fixture()
def live_client(tmp_path, monkeypatch):
    FakePayPal.instances = []
    fake_ai = FakeDeepSeek()
    cfg = AppConfig(environ={
        "SUITE_DB_PATH": str(tmp_path / "live.db"),
        "FLASK_SECRET_KEY": "test",
        "DEEPSEEK_API_KEY": "sk-test-placeholder",
        "PAYPAL_CLIENT_ID": "cid",
        "PAYPAL_CLIENT_SECRET": "secret",
        "PAYPAL_BUSINESS_EMAIL": "biz@example.com",
        "PAYPAL_PERSONAL_EMAIL": "person@example.com",
    })
    app = create_app(cfg)
    app.config.update(TESTING=True)
    monkeypatch.setattr(
        agent_routes, "DeepSeekClient", lambda config: fake_ai)
    monkeypatch.setattr(agent_routes, "PayPalClient", FakePayPal)
    return app.test_client(), fake_ai


# ---------------------------------------------------------------- WITNESS

def test_witness_live_check_earns_its_verdict(live_client):
    http, ai = live_client
    resp = http.post(
        "/api/witness/check",
        json={"text": "Norton invoice INV-2941 for $499.99"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["account_check"] == "live"
    assert data["verdict"] == "NO_CHARGE"  # earned by the account read
    assert data["paypal_stamp"] == "LIVE SANDBOX"
    assert data["account_invoice"]["id"] == "INV2-REAL-1"
    # The ruling call received real account evidence, not an empty list.
    calls = [p for seat, p in ai.payloads if seat == "witness"]
    assert len(calls) == 2
    evidence = calls[1]["account_transactions"]
    assert any(e.get("type") == "invoice" and e["status"] == "UNPAID"
               for e in evidence)
    assert any(e.get("type") == "transaction" for e in evidence)


def test_witness_decline_flips_status(live_client):
    http, _ = live_client
    resp = http.post("/api/witness/decline",
                     json={"invoice_id": "INV2-REAL-1"})
    data = resp.get_json()
    assert resp.status_code == 200
    assert data["status_before"] == "UNPAID"
    assert data["status_after"] == "CANCELLED"
    assert data["stamp"] == "LIVE SANDBOX"


def test_verdict_honesty_coercion():
    decisive = {"verdict": "PAID", "headline": "h", "body": "b."}
    out = agents.enforce_verdict_honesty(decisive, account_checked=False)
    assert out["verdict"] == "UNVERIFIED"
    assert "not checked" in out["headline"]
    earned = {"verdict": "NO_CHARGE", "headline": "h", "body": "b."}
    assert agents.enforce_verdict_honesty(
        earned, account_checked=True)["verdict"] == "NO_CHARGE"


# --------------------------------------------------------------- SEATBELT

def test_fee_math_is_deterministic():
    # 3.49% of $250.00 = $8.73 (rounded) + $0.49 = $9.22.
    assert live.invoice_total(25000, "seller") == (25000, 922)
    # Buyer gross-up: total - fee(total) nets exactly $250.00.
    total, fee = live.invoice_total(25000, "buyer")
    assert (total, fee) == (25955, 955)
    assert total - fee == 25000
    assert live.invoice_total(25000, "split") == (25461, 938)
    with pytest.raises(ValueError):
        live.invoice_total(25000, "nobody")


def test_convert_creates_and_sends_gs_invoice(live_client):
    http, _ = live_client
    resp = http.post("/api/seatbelt/convert", json={
        "item": "Camera lens", "serial": "SN-123",
        "amount": "250.00", "fee_choice": "seller",
    })
    data = resp.get_json()
    assert resp.status_code == 200
    assert data["invoice_id"] == "INV2-NEW-9"
    assert data["status"] == "SENT"
    assert data["total_charged"] == "250.00"
    assert data["stamp"] == "LIVE SANDBOX"
    payload = FakePayPal.instances[-1].created_payload
    assert payload["items"][0]["unit_amount"]["value"] == "250.00"
    assert "SN-123" in payload["items"][0]["description"]
    recipient = payload["primary_recipients"][0]
    assert recipient["billing_info"]["email_address"] == \
        "person@example.com"


# ---------------------------------------------------------------- AUDITOR

def test_normalize_transactions():
    records = live.normalize_transactions(TXN_DETAILS)
    assert records[0]["kind"] == "automatic_payment"  # T0012
    assert records[0]["counterparty"] == "CloudPhotos"
    assert records[0]["fee_amount"] == "-0.50"
    assert records[0]["date"] == "2026-10-03"
    assert records[2]["kind"] == "goods_services_sent"  # negative amount
    assert records[2]["amount"] == "87.20"  # stored positive
    assert records[2]["converted"] is True  # EUR row


def test_auditor_live_pull_stamps_and_computes(live_client):
    http, _ = live_client
    resp = http.post("/api/auditor/xray", json={})
    data = resp.get_json()
    assert resp.status_code == 200
    assert data["stamp"] == "LIVE SANDBOX"
    assert data["records"] == 3
    assert any("CloudPhotos" in d for d in data["figures"]["duplicates"])
    # Fees: 0.50 + 0.50 summed from recorded fee_amount — exact.
    assert "$1.00" in " ".join(data["figures"]["true_costs"])


def test_auditor_figures_empty_history():
    figures = agents.auditor_figures([])
    assert figures["window"] == {"start": None, "end": None}
    assert figures["duplicates"] == []
    assert "$0.00" in " ".join(figures["true_costs"])
