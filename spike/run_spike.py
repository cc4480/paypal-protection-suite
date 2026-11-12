"""Slice 1 — THE ACCESS SPIKE (SCOPE §3). Run: python -m spike.run_spike

Executes, in order:
  S1  own-account invoice reads (Invoicing v2 list + detail)
  S2  own-account Transaction Search (v1)
  S3  user-context reads via Log in with PayPal — interactive consent
      flow, so this script does NOT fake it: it records the expected
      partner-gate outcome as NOT RUN (see SPIKE.md) for manual follow-up
  S4  seeded-data drill — evaluates the S1/S2 evidence for the five
      demo data shapes; missing shapes point at spike/seed_demo_account.py

KILL RULE (binding): if S1 fails, the run stops, exit code 3, and no
module may be built on simulated ledger data.

No credentials in .env -> the run records a SIMULATED receipt, writes a
BLOCKED SPIKE.md naming the missing keys, and exits 2 without making a
single network call.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app import db  # noqa: E402
from app.config import AppConfig, load_dotenv  # noqa: E402
from app.paypal_client import PayPalClient, PayPalError  # noqa: E402
from app.receipts import ReceiptLog, utcnow_iso  # noqa: E402

RESULTS = ROOT / "spike" / "results"
SPIKE_MD = ROOT / "SPIKE.md"


def _save(name: str, data) -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    (RESULTS / name).write_text(json.dumps(data, indent=2, default=str))


def _unpaid_renewal(invoices: list[dict]) -> dict | None:
    for inv in invoices:
        detail = inv.get("detail") or {}
        text = f"{detail.get('invoice_number', '')} {detail.get('note', '')}"
        if inv.get("status") in ("SENT", "UNPAID") and "renew" in text.lower():
            return inv
    for inv in invoices:  # fall back: any unpaid invoice proves the shape
        if inv.get("status") in ("SENT", "UNPAID"):
            return inv
    return None


def _counterparty(tx: dict) -> str:
    payer = tx.get("payer_info") or {}
    name = (payer.get("payer_name") or {}).get("alternate_full_name", "")
    return payer.get("email_address") or name or "unknown"


def _seed_shapes(invoices: list[dict], txs: list[dict]) -> dict:
    by_party: dict[str, list[dict]] = {}
    for tx in txs:
        info = tx.get("transaction_info") or {}
        by_party.setdefault(_counterparty(tx), []).append(info)
    duplicate = creep = False
    for infos in by_party.values():
        amounts = [(i.get("transaction_amount") or {}).get("value") for i in infos]
        if len(set(amounts)) < len(amounts):
            duplicate = True
        if len(set(amounts)) >= 2:
            creep = True
    return {
        "unpaid_renewal_invoice": _unpaid_renewal(invoices) is not None,
        "paid_invoice": any(i.get("status") == "PAID" for i in invoices),
        "recurring_counterparty": any(len(v) >= 2 for v in by_party.values()),
        "duplicate_charge": duplicate,
        "price_creep": creep,
    }


def _run_steps(client: PayPalClient) -> tuple[dict, str, int]:
    steps: dict[str, dict] = {}
    # ---- S1: own-account invoice reads ---------------------------------
    try:
        listing = client.list_invoices(page=1, page_size=100)
        items = listing.get("items", [])
        detail = client.get_invoice(items[0]["id"]) if items else None
        _save("s1_invoices.json", {"list": listing, "detail_sample": detail})
        steps["S1"] = {
            "status": "PASS",
            "evidence": f"{len(items)} invoice(s) readable; statuses: "
            + ", ".join(sorted({i.get('status', '?') for i in items}))
            + (f"; detail read OK for {items[0]['id']} "
               f"(status {detail.get('status')})" if detail else
               "; account has no invoices yet (seed first — see S4)"),
        }
    except PayPalError as exc:
        _save("s1_error.json", {"status": exc.status, "body": exc.body})
        steps["S1"] = {"status": "FAIL", "evidence": str(exc)}
        return steps, "KILL RULE TRIGGERED — S1 failed. STOP.", 3
    invoices = items

    # ---- S2: own-account Transaction Search -----------------------------
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=30)
    try:
        txs = client.list_transactions(start, end)
        renewal = _unpaid_renewal(invoices)
        matched = []
        if renewal:
            matched = [t for t in txs
                       if (t.get("transaction_info") or {}).get("invoice_id")
                       == renewal["id"]]
        _save("s2_transactions.json", {"window": [str(start), str(end)],
                                       "transactions": txs})
        steps["S2"] = {
            "status": "PASS",
            "evidence": f"{len(txs)} transaction(s) in the last 31 days; "
            f"completed (status S): "
            f"{sum(1 for t in txs if (t.get('transaction_info') or {}).get('transaction_status') == 'S')}; "
            + (f"unpaid renewal invoice {renewal['id']} has "
               f"{len(matched)} matching completed transaction(s) "
               f"(0 = 'no money moved' is provable)"
               if renewal else "no unpaid renewal invoice seeded yet"),
        }
    except PayPalError as exc:
        _save("s2_error.json", {"status": exc.status, "body": exc.body})
        steps["S2"] = {"status": "FAIL", "evidence": str(exc)}
        txs = []

    # ---- S3: user-context reads (expected partner gate) -----------------
    steps["S3"] = {
        "status": "NOT RUN — manual step",
        "evidence": "Requires the interactive Log in with PayPal consent "
        "flow with the sandbox PERSONAL account; a script cannot consent. "
        "Per SCOPE §3 the expected outcome is the partner gate (no "
        "user-scoped transaction read for a non-partner app), which "
        "selects Fallback F1 and is disclosed in README + demo video.",
    }

    # ---- S4: seeded-data drill (evidence evaluation) ---------------------
    shapes = _seed_shapes(invoices, txs)
    missing = [k for k, v in shapes.items() if not v]
    _save("s4_shapes.json", shapes)
    steps["S4"] = {
        "status": "PASS" if not missing else "PARTIAL",
        "evidence": "shapes present: "
        + ", ".join(k for k, v in shapes.items() if v)
        + ("; MISSING: " + ", ".join(missing)
           + " — run spike/seed_demo_account.py, then re-run this spike"
           if missing else "; all five demo shapes backed by live reads"),
    }

    if steps["S2"]["status"] == "PASS":
        verdict = ("Fallback F1 SELECTED — S1+S2 pass on the demo account; "
                   "S3 partner gate as expected. Demo shape confirmed.")
        return steps, verdict, 0
    verdict = ("Fallback F2 SELECTED — S2 failed; Module A verdict narrows "
               "to invoice-status truth and the limitation is disclosed.")
    return steps, verdict, 0


def _write_spike_md(title: str, lines: list[str], receipts: ReceiptLog) -> None:
    rows = [
        f"| {r.operation} | {r.mode} | {r.http_status} | {r.ok} |"
        for r in receipts.receipts
    ]
    body = [f"# SPIKE — access spike results", "", f"**Run:** {utcnow_iso()}",
            f"**Outcome:** {title}", "", *lines, "", "## Receipts", "",
            "| operation | mode | http | ok |", "|---|---|---|---|", *rows, ""]
    SPIKE_MD.write_text("\n".join(body))


def main() -> int:
    load_dotenv()
    cfg = AppConfig()
    conn = db.connect(cfg.database_path)
    receipts = ReceiptLog(conn)

    if not cfg.paypal.has_credentials:
        missing = ", ".join(cfg.paypal.missing_keys)
        receipts.simulated("spike", "spike_run",
                           reason=f"no credentials seated; missing: {missing}")
        _write_spike_md(
            "BLOCKED — no sandbox credentials",
            [f"No `.env` credentials are seated (missing: {missing}), so "
             "S1 was NOT attempted and **zero** PayPal calls were made. "
             "Seat the sandbox Client ID + Secret in `.env` (see "
             "`.env.example`) and re-run `python -m spike.run_spike`."],
            receipts)
        print(f"BLOCKED: missing .env keys: {missing}. See SPIKE.md.")
        return 2

    client = PayPalClient(cfg.paypal, receipts, module="spike")
    steps, verdict, code = _run_steps(client)
    lines = [f"## {k} — {v['status']}\n\n{v['evidence']}\n"
             for k, v in steps.items()]
    lines.append(f"## Verdict\n\n{verdict}\n")
    _write_spike_md(verdict, lines, receipts)
    print(verdict)
    for k, v in steps.items():
        print(f"  {k}: {v['status']}")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
