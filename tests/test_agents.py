"""Tests for Step 1 (real tab sections) and Step 2 (real prompts).

The four DeepSeek system prompts in app/prompts/ are the grounded job
descriptions from the 2026-11-08 role research. These tests pin the
ground-truth facts each prompt must carry, the no-key honesty gate
(503, never a fabricated AI result), the code-side quote guard, and
AUDITOR's deterministic figures (fees summed from fee_amount, spread
computed-and-labeled, creep from percent_change).
"""

import sqlite3
from pathlib import Path

import pytest

from app import agent_routes, agents
from app.config import AppConfig, ConfigError
from app.deepseek import DeepSeekError, load_prompt
from app.routes import create_app

SHELL_HTML = (
    Path(__file__).resolve().parent.parent
    / "app" / "templates" / "shell.html"
)


@pytest.fixture()
def client(tmp_path):
    cfg = AppConfig(environ={
        "SUITE_DB_PATH": str(tmp_path / "agents.db"),
        "FLASK_SECRET_KEY": "test",
    })
    app = create_app(cfg)
    app.config.update(TESTING=True)
    return app.test_client(), cfg


def _flat(seat: str) -> str:
    """Prompt text, whitespace-normalized, for phrase checks."""
    return " ".join(load_prompt(seat).lower().split())


# ------------------------------------------------------------ tab structure

def test_tabs_are_real_sections_with_aria_wiring():
    html = SHELL_HTML.read_text(encoding="utf-8")
    for name in ("witness", "seatbelt", "auditor", "receipts"):
        assert f'id="tab-{name}"' in html
        assert f'aria-controls="panel-{name}"' in html
        assert f'id="panel-{name}"' in html
        assert f'aria-labelledby="tab-{name}"' in html
    assert 'role="tablist"' in html
    assert html.count('role="tabpanel"') == 4


# ------------------------------------------------------------------ prompts

def test_witness_prompt_grounded():
    text = _flat("witness")
    assert "pending" in text and "unpaid" in text
    assert "not a charge" in text
    assert "phishing@paypal.com" in text
    assert "resolution center" in text
    assert "60-day" in text


def test_seatbelt_prompt_grounded():
    text = _flat("seatbelt")
    assert "categorically ineligible" in text
    assert "never be recategorized" in text
    assert "180 days" in text and "20 days" in text
    assert "3.49% + $0.49" in text


def test_auditor_prompt_grounded():
    text = _flat("auditor")
    assert "fee_amount" in text
    assert "computed" in text  # spread must be labeled computed
    assert "own original analysis" in text  # price creep, labeled
    assert "3 years" in text and "31 days" in text


def test_receipts_prompt_grounded():
    text = _flat("receipts")
    assert "resolution center" in text
    assert "system of record" in text
    assert "180 days" in text and "20 days" in text
    # stamps come from real calls, not from the AI:
    assert "live sandbox means a real https call" in text


def test_missing_prompt_is_a_loud_error():
    with pytest.raises(DeepSeekError):
        load_prompt("no-such-seat")


# -------------------------------------------------------------- honesty gate

def test_deepseek_config_gate():
    cfg = AppConfig({})
    assert cfg.deepseek.has_key is False
    with pytest.raises(ConfigError) as exc:
        cfg.deepseek.require_key()
    assert "DEEPSEEK_API_KEY" in str(exc.value)


def test_status_reports_deepseek_readiness(client):
    http, _ = client
    data = http.get("/api/status").get_json()
    assert data["deepseek"]["ready"] is False
    assert data["deepseek"]["model"]  # a model name is always reported


def test_agent_endpoints_refuse_without_key(client):
    http, _ = client
    for url, payload in (
        ("/api/witness/check", {"text": "invoice"}),
        ("/api/seatbelt/analyze", {"text": "chat"}),
        ("/api/receipts/explain", {"id": 1}),
    ):
        resp = http.post(url, json=payload)
        assert resp.status_code == 503, url
        assert resp.get_json()["error"] == "deepseek_not_configured"


def test_xray_still_answers_without_key(client):
    http, _ = client
    # Figures are code-computed; only the narration needs the key.
    resp = http.post("/api/auditor/xray", json={})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["narration"] is None
    assert "DEEPSEEK_API_KEY" in data["narration_note"]
    # No credentials: the X-ray runs over the Demo Account ledger.
    assert data["stamp"] == "SAMPLE ACCOUNT"


# ------------------------------------------------------- deterministic money

def test_auditor_figures_reconcile_exactly():
    figures = agents.auditor_figures(agents.SAMPLE_HISTORY)
    costs = " ".join(figures["true_costs"])
    # fee_amount values in the fixture: 9.10 + 3.41 = 12.51, exact.
    assert "$12.51" in costs and "exact" in costs
    # Spread: 4.00% of the 87.20 converted purchase = 3.49, computed.
    assert "$3.49" in costs and "computed" in costs
    assert len(figures["duplicates"]) == 1  # CloudPhotos, 2 days apart
    creep = " ".join(figures["price_creep"])
    assert "MusicWave" in creep and "40.04%" in creep
    assert "own analysis" in creep  # labeled as Auditor's own
    assert any("StreamBox" in s for s in figures["subscriptions"])


# ------------------------------------------------------------ wired endpoints

class FakeClient:
    """Stands in for DeepSeekClient; returns contracted JSON per seat."""

    def chat_json(self, seat, payload):
        if seat == "witness":
            return {
                "amount": "$1.00", "seller": "Test Seller",
                "invoice_id": "INV-1", "phone": "not stated",
                "verdict": "NO_CHARGE",
                "headline": "No money has left your account.",
                "body": "The invoice is unpaid.",
            }
        if seat == "seatbelt":
            return {
                "flags": [
                    {"flag": "F&F demand", "quote": "friends and family"},
                    {"flag": "Invented", "quote": "words never written"},
                ],
                "risk_level": "HIGH",
                "final_message": "Please pay by Goods & Services invoice.",
            }
        if seat == "auditor":
            return {"summary": "Summary.", "top_action": "Cancel one sub."}
        if seat == "receipts":
            return {"explanation": "A simulated preview call.",
                    "deadline_note": None}
        raise AssertionError(f"unexpected seat {seat}")


@pytest.fixture()
def ai_client(tmp_path, monkeypatch):
    cfg = AppConfig(environ={
        "SUITE_DB_PATH": str(tmp_path / "ai.db"),
        "FLASK_SECRET_KEY": "test",
        "DEEPSEEK_API_KEY": "sk-test-placeholder",
    })
    app = create_app(cfg)
    app.config.update(TESTING=True)
    monkeypatch.setattr(
        agent_routes, "DeepSeekClient", lambda config: FakeClient())
    return app.test_client(), cfg


def test_witness_endpoint_runs_prompt_path_and_records_case(ai_client):
    http, cfg = ai_client
    resp = http.post("/api/witness/check",
                     json={"text": "You owe $1.00, invoice INV-1"})
    assert resp.status_code == 200
    data = resp.get_json()
    # No PayPal credentials in this cfg, so WITNESS reads the Demo
    # Account: the ledger search really ran (INV-1 is not in it),
    # so the NO_CHARGE verdict is earned — against sample data,
    # stamped as such. (The UNVERIFIED coercion still guards any
    # path where no account read happens at all; see test_live.)
    assert data["verdict"] == "NO_CHARGE"
    assert data["account_check"] == "demo"
    assert data["paypal_stamp"] == "SAMPLE ACCOUNT"
    assert data["engine"] == "deepseek"
    conn = sqlite3.connect(str(cfg.database_path))
    try:
        rows = conn.execute(
            "SELECT module, kind FROM cases").fetchall()
    finally:
        conn.close()
    assert rows == [("witness", "invoice_check")]


def test_seatbelt_endpoint_drops_fabricated_quotes(ai_client):
    http, _ = ai_client
    resp = http.post(
        "/api/seatbelt/analyze",
        json={"text": "just send it friends and family, trust me"})
    assert resp.status_code == 200
    data = resp.get_json()
    assert [f["flag"] for f in data["flags"]] == ["F&F demand"]
    assert data["risk_level"] == "HIGH"


def test_xray_endpoint_narrates_code_figures(ai_client):
    http, cfg = ai_client
    resp = http.post("/api/auditor/xray", json={})
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["narration"]["summary"] == "Summary."
    assert "$12.51" in " ".join(data["figures"]["true_costs"])
    conn = sqlite3.connect(str(cfg.database_path))
    try:
        count = conn.execute(
            "SELECT COUNT(*) FROM xray_reports").fetchone()[0]
    finally:
        conn.close()
    assert count == 1


def test_explain_unknown_receipt_is_404(ai_client):
    http, _ = ai_client
    resp = http.post("/api/receipts/explain", json={"id": 999})
    assert resp.status_code == 404
