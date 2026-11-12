"""Receipt logging — the honesty layer.

Every PayPal interaction goes through a ReceiptLog so it can be stamped:

  LIVE SANDBOX — a real HTTPS call was made to the PayPal sandbox API.
  SIMULATED    — no call was made (fixture, dry run, or blocked). A
                 SIMULATED receipt must always say *why* no call happened.

The rule from SCOPE §1: a dry run is labeled, never dressed up. Anything
that did not touch api-m3.sandbox.paypal.com can never be stamped LIVE.
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime, timezone

LIVE = "LIVE SANDBOX"
SIMULATED = "SIMULATED"
MODES = (LIVE, SIMULATED)


def stamp_for(made_api_call: bool) -> str:
    """The one stamping rule, kept pure so it can be unit-tested."""
    return LIVE if made_api_call else SIMULATED


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass
class Receipt:
    module: str
    operation: str
    mode: str
    method: str | None = None
    endpoint: str | None = None
    http_status: int | None = None
    ok: bool = False
    detail: dict = field(default_factory=dict)
    created_at: str = field(default_factory=utcnow_iso)

    def __post_init__(self) -> None:
        if self.mode not in MODES:
            raise ValueError(
                f"receipt mode must be one of {MODES}, got {self.mode!r}"
            )
        if self.mode == SIMULATED and not self.detail.get("reason"):
            raise ValueError(
                "a SIMULATED receipt must carry detail['reason'] "
                "explaining why no live call was made"
            )


class ReceiptLog:
    """Appends receipts to SQLite and keeps an in-memory copy."""

    def __init__(self, conn: sqlite3.Connection | None = None) -> None:
        self.conn = conn
        self.receipts: list[Receipt] = []

    def record(self, receipt: Receipt) -> Receipt:
        self.receipts.append(receipt)
        if self.conn is not None:
            self.conn.execute(
                "INSERT INTO receipts (created_at, module, operation, mode,"
                " method, endpoint, http_status, ok, detail)"
                " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    receipt.created_at,
                    receipt.module,
                    receipt.operation,
                    receipt.mode,
                    receipt.method,
                    receipt.endpoint,
                    receipt.http_status,
                    1 if receipt.ok else 0,
                    json.dumps(receipt.detail, default=str),
                ),
            )
            self.conn.commit()
        return receipt

    def simulated(
        self,
        module: str,
        operation: str,
        reason: str,
        detail: dict | None = None,
    ) -> Receipt:
        merged = {"reason": reason, **(detail or {})}
        return self.record(
            Receipt(module=module, operation=operation, mode=SIMULATED,
                    detail=merged)
        )
