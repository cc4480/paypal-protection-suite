"""Config gating + client mechanics.

No network: the client is driven against a stub transport. Fixtures here
are unit-test data for the client's request/receipt machinery — they are
never presented as live results anywhere.
"""

from datetime import datetime, timedelta, timezone

import pytest

from app.config import ConfigError, PayPalConfig
from app.paypal_client import PayPalClient, date_windows
from app.receipts import LIVE, ReceiptLog

UTC = timezone.utc


def _cfg(**over):
    env = {"PAYPAL_CLIENT_ID": "cid", "PAYPAL_CLIENT_SECRET": "sec"}
    env.update(over)
    return PayPalConfig(env)


def test_missing_keys_fail_loud_and_named():
    cfg = PayPalConfig({})
    assert cfg.missing_keys == ["PAYPAL_CLIENT_ID", "PAYPAL_CLIENT_SECRET"]
    with pytest.raises(ConfigError) as exc:
        cfg.require_credentials()
    assert "PAYPAL_CLIENT_ID" in str(exc.value)
    assert "PAYPAL_CLIENT_SECRET" in str(exc.value)


def test_default_api_base_is_sandbox():
    assert _cfg().api_base == "https://api-m3.sandbox.paypal.com"


def test_date_windows_never_exceed_31_days_and_stay_contiguous():
    start = datetime(2026, 1, 1, tzinfo=UTC)
    end = datetime(2026, 3, 15, tzinfo=UTC)
    windows = date_windows(start, end)
    assert windows[0][0] == start and windows[-1][1] == end
    for w_start, w_end in windows:
        assert w_end - w_start <= timedelta(days=31)
    for (_, prev_end), (next_start, _) in zip(windows, windows[1:]):
        assert next_start - prev_end == timedelta(seconds=1)


def test_date_windows_single_and_invalid():
    start = datetime(2026, 11, 1, tzinfo=UTC)
    assert len(date_windows(start, start + timedelta(days=10))) == 1
    with pytest.raises(ValueError):
        date_windows(start + timedelta(days=1), start)


class FakeResponse:
    def __init__(self, body, status=200):
        self._body, self.status_code = body, status
        self.content = b"{}" if body else b""
        self.ok = 200 <= status < 300

    def json(self):
        return self._body


class FakeSession:
    """Records calls; answers token + invoice list from fixtures."""

    def __init__(self):
        self.calls = []

    def request(self, method, url, headers=None, timeout=None, **kw):
        self.calls.append({"method": method, "url": url,
                           "headers": headers or {}, **kw})
        if url.endswith("/v1/oauth2/token"):
            assert kw.get("auth") == ("cid", "sec")
            assert kw["data"] == {"grant_type": "client_credentials"}
            return FakeResponse({"access_token": "tok-123",
                                 "token_type": "Bearer", "expires_in": 3600})
        if url.endswith("/v2/invoicing/invoices"):
            assert headers["Authorization"] == "Bearer tok-123"
            assert kw["params"]["total_required"] == "true"
            return FakeResponse({
                "total_items": 1, "total_pages": 1,
                "items": [{"id": "INV2-FIXTURE", "status": "SENT",
                           "detail": {"invoice_number": "RENEWAL-2027-001"}}],
                "links": []})
        raise AssertionError(f"unexpected URL {url}")


def test_client_oauth_then_list_and_receipt_stamped_live():
    session = FakeSession()
    log = ReceiptLog()
    client = PayPalClient(_cfg(), log, session=session)
    body = client.list_invoices()
    assert body["items"][0]["status"] == "SENT"
    client.list_invoices()  # token must be cached: still one token call
    token_calls = [c for c in session.calls if "oauth2" in c["url"]]
    assert len(token_calls) == 1
    assert [r.mode for r in log.receipts] == [LIVE, LIVE, LIVE]
    assert log.receipts[-1].detail["summary"]["invoices"][0]["id"] == "INV2-FIXTURE"


def test_client_refuses_to_call_without_credentials():
    session = FakeSession()
    client = PayPalClient(PayPalConfig({}), ReceiptLog(), session=session)
    with pytest.raises(ConfigError):
        client.list_invoices()
    assert session.calls == []  # zero network attempts
