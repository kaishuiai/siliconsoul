from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from typing import List, Optional


@dataclass(frozen=True)
class EquationSolution:
    roots: List[float]
    kind: str
    message: str = ""


def solve_linear(a: float, b: float) -> EquationSolution:
    a = float(a)
    b = float(b)
    if a == 0.0:
        if b == 0.0:
            return EquationSolution(roots=[], kind="infinite", message="0 = 0")
        return EquationSolution(roots=[], kind="none", message="no solution")
    return EquationSolution(roots=[-b / a], kind="single")


def solve_quadratic(a: float, b: float, c: float) -> EquationSolution:
    a = float(a)
    b = float(b)
    c = float(c)
    if a == 0.0:
        return solve_linear(b, c)

    disc = b * b - 4.0 * a * c
    if disc < 0.0:
        return EquationSolution(roots=[], kind="none", message="no real roots")
    if disc == 0.0:
        return EquationSolution(roots=[-b / (2.0 * a)], kind="single")
    r = sqrt(disc)
    return EquationSolution(roots=[(-b - r) / (2.0 * a), (-b + r) / (2.0 * a)], kind="two")
