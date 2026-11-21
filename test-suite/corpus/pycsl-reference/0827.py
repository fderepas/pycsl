"""Test 0827 — WL-04a regression lock (POSITIVE, List[float] LITERAL): a `List[float]`
built by a LIST LITERAL — a LOCAL or a `-> List[float]` RETURN — realizes its float
ELEMENTS faithfully as `array real`; the fractional value is preserved, never
truncated to int.

Before the fix, an indexed read of a float list-literal LOCAL folded to the
int-truncated element (`a = [1.5, 2.5]; a[1]` → `2`, an `int` vs `real` collision),
and a `-> List[float]` return literal collapsed likewise — ill-typed WhyML
(Detector D2: TYPEERR). PyCSL now builds the literal as `array real` and folds a
fixed-index read to the FAITHFUL real value, so `a[1]` is `2.5` and a
`-> List[float]` return's `\result[0]` reads a `real` natively.

Ground truth: for `a = [1.5, 2.5]`, `a[1]` is `2.5`; for `return [1.5, 2.5]`,
`\result[0]` is `1.5` — fractional values preserved.
"""
_ = 0  # anchor
from typing import List


#@ ensures \result == 2.5
def snd_float_local() -> float:
    """A float list LITERAL LOCAL's element is a REAL — fractional value preserved."""
    a = [1.5, 2.5]
    return a[1]


#@ ensures \result[0] == 1.5
#@ ensures \result[1] == 2.5
def make_float_list() -> List[float]:
    """A `-> List[float]` return built by a literal is an `array real`, read natively."""
    return [1.5, 2.5]


if __name__ == "__main__":
    assert snd_float_local() == 2.5
    r = make_float_list()
    assert r[0] == 1.5
    assert r[1] == 2.5
