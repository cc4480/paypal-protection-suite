"""Agent endpoints — WITNESS and SEATBELT (AUDITOR + the receipt
explainer live in app/auditor_routes.py).

Moved out of routes.py so each file stays small. Includes the live
PayPal wiring (app/live.py): with sandbox credentials seated,
WITNESS reads the account before it rules and SEATBELT creates +
sends the real Goods & Services invoice. Without credentials each
path degrades honestly — UNVERIFIED verdicts, plain 503s — never a
dressed-up fake. Without DEEPSEEK_API_KEY the AI seats refuse with
an honest 503. Money is always computed by code (app/money.py,
app/live.py); the AI only extracts, flags, and narrates.
"""

from __future__ import annotations

import json

from flask import Blueprint, current_app, jsonify, request

from . import agents, live
from .config import ConfigError
from .db import connect as db_connect
from .deepseek import DeepSeekClient, DeepSeekError
from .demo import DEMO_RECIPIENT, DEMO_STAMP, DemoClient
from .money import parse_amount
from .paypal_client import PayPalClient, PayPalError
from .receipts import LIVE, ReceiptLog, utcnow_iso

bp = Blueprint("agents", __name__)


def _cfg():
    return current_app.config["SUITE"]


def _ai_unavailable():
    return jsonify(
        error="deepseek_not_configured",
        message=(
            "AI is not on yet. Seat DEEPSEEK_API_KEY in .env "
            "(your own key, never via chat), then restart the "
            "suite. Previews still work and stay stamped SIMULATED."
        ),
    ), 503


def _paypal_unavailable():
    return jsonify(
        error="paypal_not_configured",
        message=(
            "Live PayPal is not on yet. Seat PAYPAL_CLIENT_ID + "
            "PAYPAL_CLIENT_SECRET in .env (your own sandbox keys, "
            "never via chat), then restart the suite."
        ),
    ), 503


def _record_case(cfg, module: str, kind: str, payload: dict) -> None:
    conn = db_connect(cfg.database_path)
    try:
        conn.execute(
            "INSERT INTO cases (created_at, module, kind, status,"
            " payload) VALUES (?, ?, ?, 'done', ?)",
            (utcnow_iso(), module, kind, json.dumps(payload)),
        )
        conn.commit()
    finally:
        conn.close()


def _text_arg() -> str:
    body = request.get_json(silent=True) or {}
    return str(body.get("text", "")).strip()


def _paypal(cfg, module: str) -> PayPalClient:
    conn = db_connect(cfg.database_path)
    return PayPalClient(cfg.paypal, ReceiptLog(conn), module=module)


def _account(cfg, module: str):
    """The account the agents run on: (client, mode).

    Live sandbox when credentials are seated; otherwise the Demo
    Account (app/demo.py) — the built-in sample ledger the same
    app/live.py code operates on, stamped SAMPLE ACCOUNT.
    """
    if cfg.paypal.has_credentials:
        return _paypal(cfg, module), "live"
    conn = db_connect(cfg.database_path)
    return DemoClient(conn, ReceiptLog(conn), module=module), "demo"


# ---------------------------------------------------------------- WITNESS

@bp.post("/api/witness/check")
def witness_check():
    cfg = _cfg()
    if not cfg.deepseek.has_key:
        return _ai_unavailable()
    text = _text_arg()
    if not text:
        return jsonify(error="empty_text",
                       message="Paste the invoice text first."), 400
    ai = DeepSeekClient(cfg.deepseek)
    try:
        extracted = agents.analyze_invoice(text, ai, [])
    except DeepSeekError as exc:
        return jsonify(error="deepseek_failed", message=str(exc)), 502
    account_check = "not_checked"
    account_invoice = None
    result = extracted
    client, mode = _account(cfg, "witness")
    try:
        evidence, account_invoice = live.witness_evidence(
            client, extracted)
        result = agents.analyze_invoice(text, ai, evidence)
        account_check = mode
    except (PayPalError, ConfigError) as exc:
        account_check = "failed"
        result = {**extracted, "account_error": str(exc)}
    # A decisive verdict needs a real account read behind it — the
    # live sandbox or the demo ledger both count; the stamp says
    # which account was read.
    result = agents.enforce_verdict_honesty(
        result, account_check in ("live", "demo"))
    result = {
        **result,
        "account_check": account_check,
        "account_invoice": account_invoice,
        "engine": "deepseek",
        "model": cfg.deepseek.model,
        "stamp": "DEEPSEEK",
    }
    if account_check == "live":
        result["paypal_stamp"] = LIVE
    elif account_check == "demo":
        result["paypal_stamp"] = DEMO_STAMP
    _record_case(cfg, "witness", "invoice_check", result)
    return jsonify(result)


@bp.post("/api/witness/decline")
def witness_decline():
    cfg = _cfg()
    body = request.get_json(silent=True) or {}
    invoice_id = str(body.get("invoice_id", "")).strip()
    if not invoice_id:
        return jsonify(
            error="missing_invoice_id",
            message="No invoice id — run a check first and decline "
                    "the invoice it found in the account."), 400
    client, mode = _account(cfg, "witness")
    try:
        outcome = live.decline_invoice(client, invoice_id)
    except PayPalError as exc:
        return jsonify(error="paypal_failed", message=str(exc)), 502
    _record_case(cfg, "witness", "invoice_decline", outcome)
    return jsonify({
        **outcome,
        "stamp": LIVE if mode == "live" else DEMO_STAMP,
        "account_mode": mode,
    })


# --------------------------------------------------------------- SEATBELT

@bp.post("/api/seatbelt/analyze")
def seatbelt_analyze():
    cfg = _cfg()
    if not cfg.deepseek.has_key:
        return _ai_unavailable()
    text = _text_arg()
    if not text:
        return jsonify(error="empty_text",
                       message="Paste the seller chat first."), 400
    try:
        result = agents.analyze_chat(text, DeepSeekClient(cfg.deepseek))
    except DeepSeekError as exc:
        return jsonify(error="deepseek_failed", message=str(exc)), 502
    _record_case(cfg, "seatbelt", "chat_analysis", result)
    return jsonify({**result, "engine": "deepseek",
                    "model": cfg.deepseek.model, "stamp": "DEEPSEEK"})


@bp.post("/api/seatbelt/convert")
def seatbelt_convert():
    cfg = _cfg()
    body = request.get_json(silent=True) or {}
    item = str(body.get("item", "")).strip()
    serial = str(body.get("serial", "")).strip()
    fee_choice = str(body.get("fee_choice", "buyer")).strip()
    client, mode = _account(cfg, "seatbelt")
    recipient = (
        str(body.get("recipient_email", "")).strip()
        or cfg.paypal.personal_email
        or (DEMO_RECIPIENT if mode == "demo" else "")
    )
    try:
        amount_cents = parse_amount(str(body.get("amount", "")))
    except ValueError:
        return jsonify(
            error="bad_amount",
            message="Enter the amount as dollars and cents, "
                    "e.g. 250.00."), 400
    if not item or amount_cents <= 0:
        return jsonify(
            error="bad_input",
            message="Name the item and a positive amount first."), 400
    if fee_choice not in ("buyer", "seller", "split"):
        return jsonify(
            error="bad_fee_choice",
            message="Fee choice must be buyer, seller, or split."), 400
    if not recipient:
        return jsonify(
            error="missing_recipient",
            message="No recipient email — set PAYPAL_PERSONAL_EMAIL "
                    "in .env or pass recipient_email."), 400
    try:
        outcome = live.convert_deal(
            client,
            item=item, amount_cents=amount_cents, serial=serial,
            fee_choice=fee_choice, recipient_email=recipient,
            invoicer_email=cfg.paypal.business_email)
    except PayPalError as exc:
        return jsonify(error="paypal_failed", message=str(exc)), 502
    if mode == "demo":
        outcome = {**outcome, "stamp": DEMO_STAMP,
                   "account_mode": "demo"}
    _record_case(cfg, "seatbelt", "gs_invoice", outcome)
    return jsonify(outcome)



