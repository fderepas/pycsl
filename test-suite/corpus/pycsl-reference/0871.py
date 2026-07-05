"""Test 0871 — WL-07 regression lock (NEGATIVE, keyword arm). # pycsl-expected: FAIL

Locks the KEYWORD-construction arm of the WL-07 fix. Before the fix, EXPLICIT
keyword arguments were dropped from the Call IR entirely (a pre-existing fail-OPEN
hole affecting every record constructor, plain classes too), so `Point(x=1, y=2)`
fell every field to its zero default and `kw_arg_drop_UNSOUND` — which returns
`p.x` (== 1) but CLAIMS `\result == 0` — PROVED. FALSE of real Python.

With the WL-07 fix keyword args are captured in `CallExpr.keywords` and bound by
name, so `Point(x=1, y=2).x == 1` and the false `== 0` claim is UNPROVEN. If this
test ever PASSES, keyword-argument record construction has regressed to dropping
its args.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from dataclasses import dataclass


@dataclass
class Point:
    x: int
    y: int


#@ ensures \result == 0
def kw_arg_drop_UNSOUND() -> int:
    """Returns Point(x=1, y=2).x (== 1) but claims == 0. FALSE."""
    p = Point(x=1, y=2)
    return p.x


if __name__ == "__main__":
    assert kw_arg_drop_UNSOUND() == 1
