r"""Test 5393 -- gen #37 route #382 (expected PASS): CONTROL: hashable stdlib values FrozenSet / Fraction / Decimal / date; an unhashed SimpleNamespace parameter (CPython ok).
"""
# pycsl-expected: PASS
from fractions import Fraction
from decimal import Decimal
from datetime import date
from typing import FrozenSet
import types

#@ no_exception \all
#@ ensures \result == 1
def g(f: FrozenSet[int], q: Fraction, c: Decimal, d: date, p: types.SimpleNamespace) -> int:
    s = {f, q, c, d}
    m = {q: 1, d: 2}
    return 1

if __name__ == "__main__":
    print(g(frozenset([1]), Fraction(1, 2), Decimal("1.5"), date(2026, 1, 1),
            types.SimpleNamespace()))
