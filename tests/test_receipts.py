"""Receipt stamping — the honesty layer's rules, tested directly."""

import pytest

from app import db
from app.receipts import LIVE, SIMULATED, Receipt, ReceiptLog, stamp_for


def test_stamp_rule_is_binary_and_honest():
    assert stamp_for(made_api_call=True) == LIVE
    assert stamp_for(made_api_call=False) == SIMULATED


def test_simulated_receipt_must_say_why():
    with pytest.raises(ValueError, match="reason"):
        Receipt(module="spike", operation="s1", mode=SIMULATED)
    ok = Receipt(module="spike", operation="s1", mode=SIMULATED,
                 detail={"reason": "no credentials seated"})
    assert ok.mode == SIMULATED


def test_unknown_mode_rejected():
    with pytest.raises(ValueError):
        Receipt(module="x", operation="y", mode="PROBABLY LIVE")


def test_log_persists_stamps_to_sqlite(tmp_path):
    conn = db.connect(tmp_path / "t.db")
    log = ReceiptLog(conn)
    log.record(Receipt(module="spike", operation="invoices_list", mode=LIVE,
                       method="GET", endpoint="/v2/invoicing/invoices",
                       http_status=200, ok=True,
                       detail={"summary": {"total_items": 2}}))
    log.simulated("spike", "spike_run", reason="blocked in test")
    rows = conn.execute(
        "SELECT mode, operation FROM receipts ORDER BY id").fetchall()
    assert [(r["mode"], r["operation"]) for r in rows] == [
        (LIVE, "invoices_list"), (SIMULATED, "spike_run")]
