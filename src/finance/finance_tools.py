from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


def growth_rate(old: float, new: float) -> float:
    old = float(old)
    new = float(new)
    if old == 0.0:
        raise ValueError("old value cannot be zero for growth_rate")
    return (new - old) / old


def cagr(begin: float, end: float, periods: float) -> float:
    begin = float(begin)
    end = float(end)
    periods = float(periods)
    if begin <= 0.0:
        raise ValueError("begin must be > 0 for cagr")
    if periods <= 0.0:
        raise ValueError("periods must be > 0 for cagr")
    return (end / begin) ** (1.0 / periods) - 1.0


def npv(rate: float, cashflows: List[float]) -> float:
    rate = float(rate)
    if not cashflows:
        raise ValueError("cashflows required")
    total = 0.0
    for t, cf in enumerate(cashflows):
        total += float(cf) / ((1.0 + rate) ** t)
    return total


def irr(
    cashflows: List[float],
    *,
    guess: float = 0.1,
    max_iter: int = 80,
    tol: float = 1e-8,
) -> float:
    if not cashflows:
        raise ValueError("cashflows required")
    has_pos = any(float(c) > 0.0 for c in cashflows)
    has_neg = any(float(c) < 0.0 for c in cashflows)
    if not (has_pos and has_neg):
        raise ValueError("cashflows must include at least one positive and one negative value")

    rate = float(guess)
    for _ in range(int(max_iter)):
        f = 0.0
        df = 0.0
        for t, cf in enumerate(cashflows):
            cf = float(cf)
            denom = (1.0 + rate) ** t
            f += cf / denom
            if t > 0:
                df += -t * cf / ((1.0 + rate) ** (t + 1))

        if abs(f) <= tol:
            return rate
        if df == 0.0:
            break
        next_rate = rate - f / df
        if next_rate <= -0.999999:
            break
        if abs(next_rate - rate) <= tol:
            return next_rate
        rate = next_rate

    lo, hi = -0.9, 10.0
    f_lo = npv(lo, cashflows)
    f_hi = npv(hi, cashflows)
    if f_lo == 0.0:
        return lo
    if f_hi == 0.0:
        return hi
    if f_lo * f_hi > 0.0:
        raise ValueError("unable to bracket IRR")

    for _ in range(120):
        mid = (lo + hi) / 2.0
        f_mid = npv(mid, cashflows)
        if abs(f_mid) <= tol:
            return mid
        if f_lo * f_mid <= 0.0:
            hi, f_hi = mid, f_mid
        else:
            lo, f_lo = mid, f_mid
    return (lo + hi) / 2.0


def pv(rate: float, nper: int, *, pmt: float = 0.0, fv: float = 0.0, when: str = "end") -> float:
    rate = float(rate)
    nper = int(nper)
    pmt = float(pmt)
    fv = float(fv)
    when = _normalize_when(when)

    if nper < 0:
        raise ValueError("nper must be >= 0")
    if rate == 0.0:
        return -(fv + pmt * nper)

    factor = (1.0 + rate) ** nper
    adj = 1.0 if when == "end" else (1.0 + rate)
    return -(fv + pmt * adj * (factor - 1.0) / rate) / factor


def fv(rate: float, nper: int, *, pmt: float = 0.0, pv: float = 0.0, when: str = "end") -> float:
    rate = float(rate)
    nper = int(nper)
    pmt = float(pmt)
    pv = float(pv)
    when = _normalize_when(when)

    if nper < 0:
        raise ValueError("nper must be >= 0")
    if rate == 0.0:
        return -(pv + pmt * nper)

    factor = (1.0 + rate) ** nper
    adj = 1.0 if when == "end" else (1.0 + rate)
    return -(pv * factor + pmt * adj * (factor - 1.0) / rate)


@dataclass(frozen=True)
class PaymentRow:
    period: int
    payment: float
    interest: float
    principal: float
    balance: float


def amortization_schedule(
    *,
    principal: float,
    annual_rate: float,
    years: float,
    payments_per_year: int = 12,
) -> Dict[str, object]:
    principal = float(principal)
    annual_rate = float(annual_rate)
    years = float(years)
    payments_per_year = int(payments_per_year)
    if principal <= 0.0:
        raise ValueError("principal must be > 0")
    if years <= 0.0:
        raise ValueError("years must be > 0")
    if payments_per_year <= 0:
        raise ValueError("payments_per_year must be > 0")

    nper = int(round(years * payments_per_year))
    r = annual_rate / payments_per_year
    if r == 0.0:
        payment = principal / nper
    else:
        payment = (r * principal) / (1.0 - (1.0 + r) ** (-nper))

    rows: List[PaymentRow] = []
    balance = principal
    for p in range(1, nper + 1):
        interest = balance * r
        principal_paid = payment - interest
        balance = max(0.0, balance - principal_paid)
        rows.append(
            PaymentRow(
                period=p,
                payment=float(payment),
                interest=float(interest),
                principal=float(principal_paid),
                balance=float(balance),
            )
        )
        if balance <= 1e-10:
            break

    total_interest = sum(r.interest for r in rows)
    total_payment = sum(r.payment for r in rows)
    return {
        "payment": float(payment),
        "total_interest": float(total_interest),
        "total_payment": float(total_payment),
        "periods": len(rows),
        "schedule": [r.__dict__ for r in rows],
    }


def break_even_quantity(*, fixed_cost: float, price: float, variable_cost: float) -> float:
    fixed_cost = float(fixed_cost)
    price = float(price)
    variable_cost = float(variable_cost)
    if price <= variable_cost:
        raise ValueError("price must be greater than variable_cost")
    if fixed_cost < 0.0:
        raise ValueError("fixed_cost must be >= 0")
    return fixed_cost / (price - variable_cost)


def _normalize_when(when: str) -> str:
    w = (when or "end").strip().lower()
    if w in ("end", "e", "0"):
        return "end"
    if w in ("begin", "b", "1", "start"):
        return "begin"
    raise ValueError("when must be 'end' or 'begin'")
