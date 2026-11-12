"""Tests for the Demo Account (app/demo.py) — Carlos's direction:
sample DATA, real motions. Without sandbox credentials the agents
run the same app/live.py code against the built-in sample ledger:
WITNESS really searches it, decline really cancels + re-reads,
SEATBELT really creates + sends (fee math included), AUDITOR's
pull really normalizes the ledger's transactions and the figures
find the planted patterns. Everything stamped SAMPLE ACCOUNT;
receipts stay SIMULATED with the demo reason — no fake LIVE.
"""

import json
import sqlite3

import pytest

from app import agent_routes, agents, live
from app.config import AppConfig
from app.demo import DemoClient
from app.receipts import ReceiptLog
from app.routes import create_app


class FakeDeepSeek:
    """Witness extraction whose claimed invoice id is settable."""

    def __init__(self, invoice_id="INV2-NRTN-8841-2207"):
        self.invoice_id = invoice_id
        self.payloads = []

    def chat_json(self, seat, payload):
        self.payloads.append((seat, payload))
        if seat == "witness":
            return {
                "amount": "$499.99", "seller": "Norton Renewal",
                "invoice_id": self.invoice_id,
                "phone": "1-888-555-0147",
                "verdict": "NO_CHARGE",
                "headline": "No money has left your account.",
                "body": "The invoice is not in the account.",
            }
        if seat == "auditor":
            return {"summary": "Summary.", "top_action": "Act."}
        raise AssertionError(f"unexpected seat {seat}")


@pytest.fixture()
def demo_http(tmp_path, monkeypatch):
    ai = FakeDeepSeek()
    cfg = AppConfig(environ={
        "SUITE_DB_PATH": str(tmp_path / "demo.db"),
        "FLASK_SECRET_KEY": "test",
        "DEEPSEEK_API_KEY": "sk-test-placeholder",
    })
    app = create_app(cfg)
    app.config.update(TESTING=True)
    monkeypatch.setattr(
        agent_routes, "DeepSeekClient", lambda config: ai)
    return app.test_client(), ai, cfg


# ------------------------------------------------------------ WITNESS

def test_demo_witness_searches_ledger_and_earns_verdict(demo_http):
    http, ai, _ = demo_http
    resp = http.post("/api/witness/check", json={
        "text": "Norton invoice INV2-NRTN-8841-2207 for $499.99"})
    data = resp.get_json()
    assert resp.status_code == 200
    assert data["account_check"] == "demo"
    assert data["paypal_stamp"] == "SAMPLE ACCOUNT"
    # The verdict survives BECAUSE a real search backed it: the
    # fake Norton invoice is absent from the ledger by design.
    assert data["verdict"] == "NO_CHARGE"
    assert data["account_invoice"] is None
    calls = [p for seat, p in ai.payloads if seat == "witness"]
    assert len(calls) == 2
    evidence = calls[1]["account_transactions"]
    assert any(e.get("type") == "transaction" for e in evidence)
    assert not any(e.get("type") == "invoice" for e in evidence)


def test_demo_witness_match_finds_seeded_invoice(
        tmp_path, monkeypatch):
    ai = FakeDeepSeek(invoice_id="LCR-2026-041")
    cfg = AppConfig(environ={
        "SUITE_DB_PATH": str(tmp_path / "demo2.db"),
        "FLASK_SECRET_KEY": "test",
        "DEEPSEEK_API_KEY": "sk-test-placeholder",
    })
    app = create_app(cfg)
    app.config.update(TESTING=True)
    monkeypatch.setattr(
        agent_routes, "DeepSeekClient", lambda config: ai)
    http = app.test_client()
    data = http.post("/api/witness/check", json={
        "text": "Lakeside invoice LCR-2026-041 for $120.00"}).get_json()
    assert data["account_invoice"]["id"] == "DEMO-INV-1001"
    assert data["account_invoice"]["status"] == "SENT"


def test_demo_decline_flips_seeded_invoice(demo_http):
    http, _, _ = demo_http
    data = http.post("/api/witness/decline",
                     json={"invoice_id": "DEMO-INV-1001"}).get_json()
    assert data["status_before"] == "SENT"
    assert data["status_after"] == "CANCELLED"
    assert data["stamp"] == "SAMPLE ACCOUNT"


# ------------------------------------------------------------ SEATBELT

def test_demo_convert_creates_invoice_in_ledger(demo_http):
    http, _, cfg = demo_http
    resp = http.post("/api/seatbelt/convert", json={
        "item": "Camera", "amount": "250.00", "fee_choice": "buyer"})
    data = resp.get_json()
    assert resp.status_code == 200
    assert data["stamp"] == "SAMPLE ACCOUNT"
    assert data["status"] == "SENT"
    assert data["total_charged"] == "259.55"  # real gross-up math
    assert data["recipient"] == "buyer-demo@example.com"
    # The invoice now EXISTS in the ledger — WITNESS can decline it.
    out = http.post("/api/witness/decline",
                    json={"invoice_id": data["invoice_id"]}).get_json()
    assert out["status_before"] == "SENT"
    assert out["status_after"] == "CANCELLED"
    assert cfg  # silence linter; cfg documents the fixture


# ------------------------------------------------------------- AUDITOR

def test_demo_xray_computes_from_ledger(demo_http):
    http, _, _ = demo_http
    data = http.post("/api/auditor/xray", json={}).get_json()
    assert data["stamp"] == "SAMPLE ACCOUNT"
    assert data["records"] == 18
    figs = data["figures"]
    assert any("StreamBox" in s for s in figs["subscriptions"])
    assert any("MusicWave" in s and "40.04%" in s
               for s in figs["price_creep"])
    assert len(figs["duplicates"]) == 1
    assert "CloudPhotos" in figs["duplicates"][0]
    costs = " ".join(figs["true_costs"])
    assert "$12.51" in costs  # 9.10 + 3.41 recorded fees
    assert "$3.49" in costs   # 4.00% of the 87.20 EUR purchase


# ------------------------------------------------------------- receipts

def test_demo_receipts_stay_simulated_with_reason(demo_http):
    http, _, cfg = demo_http
    http.post("/api/seatbelt/convert", json={
        "item": "Camera", "amount": "250.00"})
    conn = sqlite3.connect(str(cfg.database_path))
    rows = conn.execute(
        "SELECT mode, detail FROM receipts"
        " WHERE endpoint = 'demo-account'").fetchall()
    conn.close()
    assert rows, "demo calls must leave receipts"
    for mode, detail in rows:
        assert mode == "SIMULATED"
        assert "demo account" in json.loads(detail)["reason"]


def test_demo_client_direct_motions(tmp_path):
    from app.db import connect
    conn = connect(tmp_path / "d.db")
    client = DemoClient(conn, ReceiptLog(conn), module="witness")
    evidence, found = live.witness_evidence(
        client, {"invoice_id": "INV2-NRTN-8841-2207"})
    assert found is None
    assert any(e["type"] == "transaction" for e in evidence)
    figures = agents.auditor_figures(live.pull_history(client))
    assert figures["subscriptions"]
