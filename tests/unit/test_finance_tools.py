import math

import pytest

from src.finance.finance_tools import (
    amortization_schedule,
    break_even_quantity,
    cagr,
    fv,
    growth_rate,
    irr,
    npv,
    pv,
)
from src.finance.math_tools import solve_linear, solve_quadratic


def test_growth_rate_and_cagr():
    assert growth_rate(100, 110) == 0.1
    assert abs(cagr(100, 121, 2) - 0.1) < 1e-12
    with pytest.raises(ValueError):
        growth_rate(0, 10)
    with pytest.raises(ValueError):
        cagr(0, 10, 2)
    with pytest.raises(ValueError):
        cagr(10, 12, 0)


def test_npv_and_irr():
    cfs = [-1000, 400, 400, 400]
    v = npv(0.1, cfs)
    assert abs(v - (cfs[0] + 400 / 1.1 + 400 / (1.1**2) + 400 / (1.1**3))) < 1e-9
    r = irr(cfs)
    assert 0.05 < r < 0.2
    assert abs(npv(r, cfs)) < 1e-6
    with pytest.raises(ValueError):
        irr([100, 200, 300])


def test_pv_fv_roundtrip_and_when_validation():
    pv_value = pv(0.1, 2, fv=121, pmt=0, when="end")
    assert abs(pv_value - (-100.0)) < 1e-9
    fv_value = fv(0.1, 2, pv=-100, pmt=0, when="end")
    assert abs(fv_value - 121.0) < 1e-9
    with pytest.raises(ValueError):
        pv(0.1, 2, fv=121, when="bad")


def test_amortization_schedule_and_break_even():
    out = amortization_schedule(principal=1000, annual_rate=0.12, years=1, payments_per_year=12)
    assert out["payment"] > 0
    assert out["periods"] >= 10
    schedule = out["schedule"]
    assert schedule[-1]["balance"] <= 1.0
    assert break_even_quantity(fixed_cost=1000, price=10, variable_cost=6) == 250.0
    with pytest.raises(ValueError):
        break_even_quantity(fixed_cost=1000, price=6, variable_cost=6)


def test_equation_solvers():
    s = solve_linear(2, 4)
    assert s.kind == "single"
    assert s.roots == [-2.0]
    s2 = solve_quadratic(1, -3, 2)
    assert s2.kind == "two"
    assert sorted([round(x, 6) for x in s2.roots]) == [1.0, 2.0]
