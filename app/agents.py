"""The four seats' work paths.

Each function takes user input (or code-computed figures), calls
DeepSeek through app/deepseek.py with the seat's grounded system
prompt, and validates the contracted JSON before it reaches the UI.

Determinism rules (SCOPE): money is computed ONLY by code
(app/money.py, app/live.py). AUDITOR's figures are computed here from
transaction records (live pull or the labeled sample below); DeepSeek
narrates them and never sees a number it could invent. SEATBELT
quotes are verified in code to be verbatim substrings of the chat —
a fabricated quote drops the flag.
"""

from __future__ import annotations

from datetime import date

from .deepseek import DeepSeekClient, DeepSeekError
from .money import format_amount, parse_amount, percent_change

# ---------------------------------------------------------------- WITNESS

_WITNESS_VERDICTS = ("NO_CHARGE", "PAID", "UNVERIFIED")


def analyze_invoice(
    text: str,
    client: DeepSeekClient,
    account_transactions: list | None = None,
) -> dict:
    """WITNESS: extract an invoice's claims and rule on it.

    `account_transactions` is the account evidence the verdict may
    use (live-read by app/live.py when credentials are seated; the
    prompt contracts the model to decide only from what it is given).
    """
    result = client.chat_json("witness", {
        "invoice_text": text,
        "account_transactions": account_transactions or [],
    })
    for key in ("amount", "seller", "invoice_id", "phone",
                "verdict", "headline", "body"):
        if key not in result:
            raise DeepSeekError(f"witness result missing key: {key}")
    if result["verdict"] not in _WITNESS_VERDICTS:
        raise DeepSeekError(
            f"witness verdict outside contract: {result['verdict']!r}"
        )
    return result


def enforce_verdict_honesty(result: dict, account_checked: bool) -> dict:
    """A decisive verdict requires a live account check behind it.
    Without one, NO_CHARGE / PAID are unearned — coerce to UNVERIFIED
    and say so. Extraction fields are untouched; only the ruling is
    held back."""
    if account_checked or result.get("verdict") == "UNVERIFIED":
        return result
    result = dict(result)
    result["verdict"] = "UNVERIFIED"
    result["headline"] = (
        "Your account was not checked, so whether money moved "
        "is unconfirmed."
    )
    result["body"] = (
        str(result.get("body", "")).rstrip()
        + " Your account itself was not checked — seat the sandbox "
        "credentials so WITNESS can read it before treating this "
        "as settled."
    )
    return result


# --------------------------------------------------------------- SEATBELT

_RISK_LEVELS = ("HIGH", "MEDIUM", "LOW")


def analyze_chat(text: str, client: DeepSeekClient) -> dict:
    """SEATBELT: flag protection-stripping pressure in a seller chat.

    Code-side honesty guard: a flag survives only if its quote is a
    verbatim substring of the chat the user pasted.
    """
    result = client.chat_json("seatbelt", {"chat_text": text})
    flags = result.get("flags")
    if not isinstance(flags, list):
        raise DeepSeekError("seatbelt result: flags is not a list")
    checked = []
    for f in flags:
        if not isinstance(f, dict) or "flag" not in f or "quote" not in f:
            raise DeepSeekError("seatbelt result: malformed flag entry")
        if f["quote"] and f["quote"] in text:
            checked.append({"flag": f["flag"], "quote": f["quote"]})
    if result.get("risk_level") not in _RISK_LEVELS:
        raise DeepSeekError(
            f"seatbelt risk_level outside contract: "
            f"{result.get('risk_level')!r}"
        )
    if not isinstance(result.get("final_message"), str):
        raise DeepSeekError("seatbelt result: final_message missing")
    return {"flags": checked, "risk_level": result["risk_level"],
            "final_message": result["final_message"]}


# ---------------------------------------------------------------- AUDITOR

# Sample history, PayPal Transaction-Search shape (the live pull is
# normalized into this same shape by app/live.py). fee_amount is the
# per-transaction fee PayPal records; "converted" rows carry the
# disclosed spread rate, computed by code below and labeled computed.
SAMPLE_HISTORY = [
    {"date": "2026-05-04", "counterparty": "MusicWave",
     "kind": "automatic_payment", "amount": "9.99", "fee_amount": "0.00"},
    {"date": "2026-06-04", "counterparty": "MusicWave",
     "kind": "automatic_payment", "amount": "9.99", "fee_amount": "0.00"},
    {"date": "2026-07-04", "counterparty": "MusicWave",
     "kind": "automatic_payment", "amount": "11.99", "fee_amount": "0.00"},
    {"date": "2026-08-04", "counterparty": "MusicWave",
     "kind": "automatic_payment", "amount": "11.99", "fee_amount": "0.00"},
    {"date": "2026-09-04", "counterparty": "MusicWave",
     "kind": "automatic_payment", "amount": "13.99", "fee_amount": "0.00"},
    {"date": "2026-10-04", "counterparty": "MusicWave",
     "kind": "automatic_payment", "amount": "13.99", "fee_amount": "0.00"},
    {"date": "2026-08-03", "counterparty": "StreamBox Premium",
     "kind": "automatic_payment", "amount": "15.99", "fee_amount": "0.00"},
    {"date": "2026-09-03", "counterparty": "StreamBox Premium",
     "kind": "automatic_payment", "amount": "15.99", "fee_amount": "0.00"},
    {"date": "2026-10-03", "counterparty": "StreamBox Premium",
     "kind": "automatic_payment", "amount": "15.99", "fee_amount": "0.00"},
    {"date": "2026-11-03", "counterparty": "StreamBox Premium",
     "kind": "automatic_payment", "amount": "15.99", "fee_amount": "0.00"},
    {"date": "2026-10-03", "counterparty": "CloudPhotos",
     "kind": "automatic_payment", "amount": "9.99", "fee_amount": "0.00"},
    {"date": "2026-10-05", "counterparty": "CloudPhotos",
     "kind": "automatic_payment", "amount": "9.99", "fee_amount": "0.00"},
    {"date": "2026-09-18", "counterparty": "Buyer — camera lens",
     "kind": "goods_services_received", "amount": "250.00",
     "fee_amount": "-9.10"},
    {"date": "2026-10-21", "counterparty": "Buyer — headphones",
     "kind": "goods_services_received", "amount": "89.99",
     "fee_amount": "-3.41"},
    {"date": "2026-10-12", "counterparty": "EU Software Store",
     "kind": "goods_services_sent", "amount": "87.20",
     "fee_amount": "0.00", "converted": True, "spread_rate_pct": "4.00"},
]


def _by_counterparty(txns: list[dict]) -> dict[str, list[dict]]:
    grouped: dict[str, list[dict]] = {}
    for t in txns:
        grouped.setdefault(t["counterparty"], []).append(t)
    for rows in grouped.values():
        rows.sort(key=lambda t: t["date"])
    return grouped


def auditor_figures(txns: list[dict]) -> dict:
    """Compute the X-ray figures from transaction records — code only.

    Returns display-ready strings; the AI narrates these and may not
    alter them. fee totals are sums of PayPal's recorded fee_amount;
    the conversion-spread total is computed from the disclosed rate
    and is labeled computed in the figure itself.
    """
    grouped = _by_counterparty(txns)
    subs, creep = [], []
    for name, rows in grouped.items():
        autos = [r for r in rows if r["kind"] == "automatic_payment"]
        if len(autos) >= 3:
            latest = autos[-1]
            subs.append(
                f"{name} — ${latest['amount']}/mo · "
                f"{len(autos)} charges, latest {latest['date']}"
            )
        if len(autos) >= 2:
            first, last = autos[0], autos[-1]
            if parse_amount(first["amount"]) != parse_amount(last["amount"]):
                pct = percent_change(
                    parse_amount(first["amount"]),
                    parse_amount(last["amount"]),
                )
                creep.append(
                    f"{name} — ${first['amount']} → ${last['amount']} "
                    f"(+{pct}%) across {len(autos)} charges "
                    f"(Auditor's own analysis — PayPal publishes no "
                    f"price-creep report)"
                )
    dupes = []
    for name, rows in grouped.items():
        for a, b in zip(rows, rows[1:]):
            same_amount = parse_amount(a["amount"]) == parse_amount(b["amount"])
            gap = (
                date.fromisoformat(b["date"]) - date.fromisoformat(a["date"])
            ).days
            if same_amount and 0 <= gap <= 7:
                dupes.append(
                    f"{name} — ${a['amount']} charged twice: "
                    f"{a['date']} and {b['date']}"
                )
    fees_cents = sum(abs(parse_amount(t["fee_amount"])) for t in txns)
    spread_cents = 0
    for t in txns:
        if t.get("converted"):
            rate = parse_amount(t["spread_rate_pct"])  # "4.00" -> 400
            spread_cents += round(parse_amount(t["amount"]) * rate / 10000)
    costs = [
        f"PayPal fees paid: ${format_amount(fees_cents)} "
        f"(summed from PayPal's recorded fee_amount — exact)",
        f"Currency conversion spread paid: ${format_amount(spread_cents)} "
        f"(computed at the disclosed 4.00% spread — not an itemized "
        f"PayPal figure)",
    ]
    dates = sorted(t["date"] for t in txns)
    window = (
        {"start": dates[0], "end": dates[-1]}
        if dates else {"start": None, "end": None}
    )
    return {
        "window": window,
        "subscriptions": subs,
        "duplicates": dupes,
        "price_creep": creep,
        "true_costs": costs,
    }


def narrate_xray(figures: dict, client: DeepSeekClient) -> dict:
    """AUDITOR: DeepSeek narrates code-computed figures, verbatim."""
    result = client.chat_json("auditor", {"figures": figures})
    for key in ("summary", "top_action"):
        if not isinstance(result.get(key), str):
            raise DeepSeekError(f"auditor result missing key: {key}")
    return result


# --------------------------------------------------------------- RECEIPTS


def explain_receipt(receipt: dict, client: DeepSeekClient) -> dict:
    """RECEIPTS: plain-language explanation of one stored receipt."""
    result = client.chat_json("receipts", {"receipt": receipt})
    if not isinstance(result.get("explanation"), str):
        raise DeepSeekError("receipts result missing key: explanation")
    if "deadline_note" not in result:
        raise DeepSeekError("receipts result missing key: deadline_note")
    return result
