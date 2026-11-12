"""Deterministic money math — the only place dollar figures are computed.

SCOPE rule: the AI never computes a dollar figure; code does. All amounts
are handled as integer minor units (cents) internally so sums reconcile
to the cent. PayPal amount strings arrive as decimal strings ("499.99",
fees often negative like "-14.80") and are parsed exactly via Decimal —
never via float.
"""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

CENT = Decimal("0.01")


def parse_amount(value: str | None) -> int:
    """Parse a PayPal decimal string into integer cents.

    Raises ValueError on anything that is not an exact decimal string —
    loud failure beats a silently wrong figure.
    """
    if value is None:
        raise ValueError("amount is None")
    try:
        dec = Decimal(str(value).strip())
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"unparseable amount: {value!r}") from exc
    cents = (dec * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return int(cents)


def format_amount(cents: int) -> str:
    """Format integer cents back to a canonical decimal string."""
    sign = "-" if cents < 0 else ""
    whole, frac = divmod(abs(cents), 100)
    return f"{sign}{whole}.{frac:02d}"


def sum_amounts(values: list[str]) -> int:
    """Sum PayPal decimal strings, returning integer cents."""
    return sum(parse_amount(v) for v in values)


def percent_change(old_cents: int, new_cents: int) -> Decimal:
    """Percentage change from old to new, as a Decimal percent value.

    Returns Decimal('0') when the old value is zero (no meaningful base).
    """
    if old_cents == 0:
        return Decimal("0")
    change = (Decimal(new_cents - old_cents) / Decimal(abs(old_cents))) * 100
    return change.quantize(CENT, rounding=ROUND_HALF_UP)


def gross_fee_net(gross_cents: int, fee_cents: int) -> int:
    """Net after fee. PayPal reports fees as negative amounts, so net is
    gross + fee (fee already signed). Kept as a named helper so every
    module reconciles the same way."""
    return gross_cents + fee_cents
