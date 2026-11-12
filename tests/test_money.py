"""Deterministic money math — exact cents, no floats anywhere."""

from decimal import Decimal

import pytest

from app.money import (
    format_amount,
    gross_fee_net,
    parse_amount,
    percent_change,
    sum_amounts,
)


def test_parse_amount_exact():
    assert parse_amount("499.99") == 49999
    assert parse_amount("0.01") == 1
    assert parse_amount("-14.80") == -1480  # PayPal fees arrive negative
    assert parse_amount("129.00") == 12900
    assert parse_amount("7") == 700


def test_parse_amount_rejects_garbage():
    with pytest.raises(ValueError):
        parse_amount("not-a-price")
    with pytest.raises(ValueError):
        parse_amount(None)
    with pytest.raises(ValueError):
        parse_amount("")


def test_format_amount_roundtrip():
    for s in ("499.99", "0.01", "-14.80", "129.00", "0.00"):
        assert format_amount(parse_amount(s)) == s


def test_sum_reconciles_to_the_cent():
    parts = ["9.99", "9.99", "13.99", "499.99", "-14.80"]
    assert sum_amounts(parts) == 51916
    assert format_amount(sum_amounts(parts)) == "519.16"


def test_percent_change_creep():
    # The AUDITOR creep case: $9.99 -> $13.99 is +40.04%
    assert percent_change(999, 1399) == Decimal("40.04")
    assert percent_change(1000, 1000) == Decimal("0.00")
    assert percent_change(0, 500) == Decimal("0")


def test_gross_fee_net_uses_signed_fee():
    # gross $499.99, fee reported as -14.80 -> net 485.19
    assert gross_fee_net(49999, -1480) == 48519
