"""Raw-HTTPS PayPal sandbox client — no SDK (SCOPE §1).

Every request/response stays visible: each public method performs exactly
the calls it documents and records a receipt stamped LIVE SANDBOX (the
stamp is applied only after a real HTTP exchange happened). If the
credentials are missing, Config.require_credentials() raises before any
network traffic — the client cannot quietly fall back to anything fake.

Endpoint shapes verified against PayPal's public developer docs
(Invoicing API v2, Transaction Search v1, OAuth2 token) on 2026-11-07.
"""

from __future__ import annotations

import time
from datetime import datetime, timedelta, timezone

import requests

from .config import PayPalConfig
from .receipts import LIVE, Receipt, ReceiptLog

INVOICE_STATUSES = (
    "DRAFT", "SENT", "SCHEDULED", "PAID", "UNPAID", "PARTIALLY_PAID",
    "PARTIALLY_REFUNDED", "REFUNDED", "CANCELLED", "PAYMENT_PENDING",
    "MARKED_AS_PAID", "MARKED_AS_REFUNDED",
)
MAX_TX_WINDOW_DAYS = 31  # Transaction Search hard limit (docs).


class PayPalError(RuntimeError):
    def __init__(self, status: int, body: dict | str) -> None:
        self.status = status
        self.body = body
        name = body.get("name", "") if isinstance(body, dict) else ""
        msg = body.get("message", "") if isinstance(body, dict) else str(body)
        super().__init__(f"PayPal HTTP {status} {name}: {msg}".strip())


def date_windows(
    start: datetime, end: datetime, max_days: int = MAX_TX_WINDOW_DAYS
) -> list[tuple[datetime, datetime]]:
    """Split [start, end] into contiguous windows of at most max_days.

    Pure and deterministic — Transaction Search rejects ranges over 31
    days, so Module C pages backward through these windows.
    """
    if end < start:
        raise ValueError("end before start")
    windows: list[tuple[datetime, datetime]] = []
    cursor = start
    span = timedelta(days=max_days) - timedelta(seconds=1)
    while cursor <= end:
        window_end = min(cursor + span, end)
        windows.append((cursor, window_end))
        cursor = window_end + timedelta(seconds=1)
    return windows


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class PayPalClient:
    def __init__(
        self,
        config: PayPalConfig,
        receipts: ReceiptLog,
        session: requests.Session | None = None,
        module: str = "spike",
    ) -> None:
        self.config = config
        self.receipts = receipts
        self.session = session or requests.Session()
        self.module = module
        self._token: str | None = None
        self._token_expires_at = 0.0

    # -- transport ------------------------------------------------------
    def _request(self, method: str, path: str, operation: str, **kw):
        self.config.require_credentials()
        url = self.config.api_base + path
        headers = kw.pop("headers", {})
        if path != "/v1/oauth2/token":
            headers.setdefault("Authorization", f"Bearer {self._access_token()}")
        headers.setdefault("Content-Type", "application/json")
        resp = self.session.request(method, url, headers=headers, timeout=30, **kw)
        body: dict | str
        try:
            body = resp.json() if resp.content else {}
        except ValueError:
            body = resp.text
        self.receipts.record(Receipt(
            module=self.module, operation=operation, mode=LIVE,
            method=method, endpoint=path, http_status=resp.status_code,
            ok=resp.ok,
            detail={"summary": _summarize(operation, body)},
        ))
        if not resp.ok:
            raise PayPalError(resp.status_code, body)
        return body

    def _access_token(self) -> str:
        if self._token and time.time() < self._token_expires_at - 60:
            return self._token
        body = self._request(
            "POST", "/v1/oauth2/token", "oauth_token",
            auth=(self.config.client_id, self.config.client_secret),
            data={"grant_type": "client_credentials"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        self._token = body["access_token"]
        self._token_expires_at = time.time() + int(body.get("expires_in", 3600))
        return self._token

    # -- Invoicing API v2 ------------------------------------------------
    def list_invoices(self, page: int = 1, page_size: int = 100,
                      fields: str | None = None) -> dict:
        params = {"page": page, "page_size": page_size, "total_required": "true"}
        if fields:
            params["fields"] = fields
        return self._request("GET", "/v2/invoicing/invoices",
                             "invoices_list", params=params)

    def get_invoice(self, invoice_id: str) -> dict:
        return self._request("GET", f"/v2/invoicing/invoices/{invoice_id}",
                             "invoices_get")

    def create_invoice(self, invoice: dict) -> dict:
        return self._request("POST", "/v2/invoicing/invoices",
                             "invoices_create", json=invoice)

    def send_invoice(self, invoice_id: str, note: str = "",
                     send_to_recipient: bool = True) -> dict:
        body = {"note": note, "send_to_recipient": send_to_recipient,
                "send_to_invoicer": False}
        return self._request("POST",
                             f"/v2/invoicing/invoices/{invoice_id}/send",
                             "invoices_send", json=body)

    def record_invoice_payment(self, invoice_id: str, amount_value: str,
                               currency: str = "USD",
                               method: str = "OTHER") -> dict:
        """Record an external payment against an invoice (seeding/demo)."""
        body = {"method": method,
                "amount": {"currency_code": currency, "value": amount_value}}
        return self._request(
            "POST", f"/v2/invoicing/invoices/{invoice_id}/payments",
            "invoices_record_payment", json=body)

    def cancel_invoice(self, invoice_id: str, note: str = "") -> dict:
        body = {"note": note, "send_to_recipient": True,
                "send_to_invoicer": False}
        return self._request("POST",
                             f"/v2/invoicing/invoices/{invoice_id}/cancel",
                             "invoices_cancel", json=body)

    # -- Transaction Search v1 -------------------------------------------
    def list_transactions(self, start: datetime, end: datetime,
                          fields: str = "all", page_size: int = 500,
                          extra_params: dict | None = None) -> list[dict]:
        """All transaction_details across every ≤31-day window and page."""
        details: list[dict] = []
        for w_start, w_end in date_windows(start, end):
            page = 1
            while True:
                params = {
                    "start_date": _iso(w_start), "end_date": _iso(w_end),
                    "fields": fields, "page_size": page_size, "page": page,
                }
                if extra_params:
                    params.update(extra_params)
                body = self._request("GET", "/v1/reporting/transactions",
                                     "transactions_list", params=params)
                details.extend(body.get("transaction_details", []))
                total_pages = int(body.get("total_pages", 1) or 1)
                if page >= total_pages:
                    break
                page += 1
        return details


def _summarize(operation: str, body) -> dict:
    """Small, safe receipt summary — counts and ids, never secrets."""
    if not isinstance(body, dict):
        return {"raw": str(body)[:200]}
    if operation == "oauth_token":
        return {"token_type": body.get("token_type"),
                "expires_in": body.get("expires_in")}
    if operation == "invoices_list":
        return {
            "total_items": body.get("total_items"),
            "invoices": [
                {"id": i.get("id"), "status": i.get("status"),
                 "invoice_number": (i.get("detail") or {}).get("invoice_number")}
                for i in body.get("items", [])
            ],
        }
    if operation in ("invoices_get", "invoices_create"):
        return {"id": body.get("id"), "status": body.get("status")}
    if operation == "transactions_list":
        return {"total_items": body.get("total_items"),
                "returned": len(body.get("transaction_details", [])),
                "last_refreshed": body.get("last_refreshed_datetime")}
    return {"keys": sorted(body.keys())[:12]}


def invoice_id_from_create_response(body: dict) -> str | None:
    """Create returns HATEOAS links; the new id is in the self href."""
    for link in body.get("links", []):
        href = link.get("href", "")
        if "/v2/invoicing/invoices/" in href:
            return href.rstrip("/").rsplit("/", 1)[-1]
    return body.get("id")
