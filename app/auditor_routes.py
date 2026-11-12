"""AUDITOR endpoints + the receipt explainer.

Split from app/agent_routes.py to keep files small. With sandbox
credentials seated, the X-ray pulls real Transaction Search history
(app/live.py) and stamps it LIVE SANDBOX; without them the same
pull runs over the Demo Account's sample ledger (app/demo.py) and
stamps it SAMPLE ACCOUNT — the figures are always computed from
transaction records by code, never narrated into existence. A
failed live pull is a loud 502 — never a silent fall back to the
sample dressed as a live report.

The DeepSeek/PayPal client classes are resolved through the
agent_routes module at call time, so tests keep one patch point.
"""

from __future__ import annotations

import json
import sqlite3

from flask import Blueprint, current_app, jsonify, request

from . import agent_routes, agents, live
from .db import connect as db_connect
from .deepseek import DeepSeekError
from .demo import DEMO_STAMP, DemoClient
from .paypal_client import PayPalError
from .receipts import LIVE, ReceiptLog, utcnow_iso

bp = Blueprint("auditor", __name__)

_DEMO_NOTE = (
    "Demo account — no sandbox credentials seated, so AUDITOR ran "
    "the real history pull over the suite's built-in sample ledger "
    "(sample transactions, PayPal-shaped). Every figure is computed "
    "by the same code the live pull feeds; seat sandbox keys to run "
    "it on the real account. Fee totals are sums of recorded "
    "fee_amount; the spread total is computed at the disclosed "
    "rate and labeled."
)

_LIVE_NOTE = (
    "Live pull from the demo sandbox account (Transaction Search, "
    "last 180 days). Figures are computed by code; fee totals are "
    "sums of recorded fee_amount, the spread total is computed at "
    "the disclosed rate and labeled."
)


@bp.post("/api/auditor/xray")
def auditor_xray():
    cfg = current_app.config["SUITE"]
    if cfg.paypal.has_credentials:
        try:
            records = live.pull_history(
                agent_routes._paypal(cfg, "auditor"))
        except PayPalError as exc:
            return jsonify(
                error="paypal_failed",
                message=f"The live history pull failed: {exc}"), 502
        stamp = LIVE
        data_note = _LIVE_NOTE
    else:
        conn = db_connect(cfg.database_path)
        client = DemoClient(conn, ReceiptLog(conn), module="auditor")
        records = live.pull_history(client)
        stamp = DEMO_STAMP
        data_note = _DEMO_NOTE
    figures = agents.auditor_figures(records)
    narration = None
    narration_note = None
    if cfg.deepseek.has_key:
        try:
            narration = agents.narrate_xray(
                figures, agent_routes.DeepSeekClient(cfg.deepseek))
        except DeepSeekError as exc:
            narration_note = f"Narration failed: {exc}"
    else:
        narration_note = (
            "Narration is off: DEEPSEEK_API_KEY is not seated. "
            "The figures above are computed by code."
        )
    report = {
        "figures": figures,
        "narration": narration,
        "narration_note": narration_note,
        "engine": "deepseek" if narration else "code-only",
        "stamp": stamp,
        "data_note": data_note,
        "records": len(records),
    }
    conn = db_connect(cfg.database_path)
    try:
        conn.execute(
            "INSERT INTO xray_reports (created_at, window_start,"
            " window_end, report) VALUES (?, ?, ?, ?)",
            (utcnow_iso(), figures["window"]["start"] or "",
             figures["window"]["end"] or "", json.dumps(report)),
        )
        conn.commit()
    finally:
        conn.close()
    return jsonify(report)


@bp.post("/api/receipts/explain")
def receipts_explain():
    cfg = current_app.config["SUITE"]
    if not cfg.deepseek.has_key:
        return agent_routes._ai_unavailable()
    body = request.get_json(silent=True) or {}
    receipt_id = body.get("id")
    conn = sqlite3.connect(str(cfg.database_path))
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute(
            "SELECT id, created_at, module, operation, mode, method,"
            " endpoint, http_status, ok, detail FROM receipts"
            " WHERE id = ?",
            (receipt_id,),
        ).fetchone()
    finally:
        conn.close()
    if row is None:
        return jsonify(error="no_such_receipt",
                       message="No receipt with that id."), 404
    item = dict(row)
    try:
        item["detail"] = json.loads(item["detail"])
    except (TypeError, ValueError):
        item["detail"] = {}
    try:
        result = agents.explain_receipt(
            item, agent_routes.DeepSeekClient(cfg.deepseek))
    except DeepSeekError as exc:
        return jsonify(error="deepseek_failed", message=str(exc)), 502
    return jsonify({**result, "engine": "deepseek",
                    "model": cfg.deepseek.model})
