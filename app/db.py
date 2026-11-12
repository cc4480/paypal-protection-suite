"""SQLite storage — one file, stdlib only.

Tables:
  receipts     — every PayPal call (or would-be call) with its LIVE
                 SANDBOX / SIMULATED stamp. This is the audit trail the UI
                 shows; honesty is stored, not just displayed.
  cases        — WITNESS checks and SEATBELT conversions (module work).
  xray_reports — AUDITOR reports (module work).
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS receipts (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at   TEXT NOT NULL,
    module       TEXT NOT NULL,
    operation    TEXT NOT NULL,
    mode         TEXT NOT NULL CHECK (mode IN ('LIVE SANDBOX', 'SIMULATED')),
    method       TEXT,
    endpoint     TEXT,
    http_status  INTEGER,
    ok           INTEGER NOT NULL DEFAULT 0,
    detail       TEXT NOT NULL DEFAULT '{}'
);
CREATE TABLE IF NOT EXISTS cases (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at   TEXT NOT NULL,
    module       TEXT NOT NULL,
    kind         TEXT NOT NULL,
    status       TEXT NOT NULL DEFAULT 'open',
    payload      TEXT NOT NULL DEFAULT '{}'
);
CREATE TABLE IF NOT EXISTS xray_reports (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at   TEXT NOT NULL,
    window_start TEXT NOT NULL,
    window_end   TEXT NOT NULL,
    report       TEXT NOT NULL DEFAULT '{}'
);
CREATE TABLE IF NOT EXISTS demo_invoices (
    id           TEXT PRIMARY KEY,
    payload      TEXT NOT NULL DEFAULT '{}'
);
CREATE TABLE IF NOT EXISTS demo_transactions (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    date         TEXT NOT NULL,
    detail       TEXT NOT NULL DEFAULT '{}'
);
"""


def connect(db_path: Path | str) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA)
    conn.commit()
    return conn


def init_db(db_path: Path | str) -> None:
    conn = connect(db_path)
    conn.close()
