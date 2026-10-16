r"""Test 2346 — route #247 (expected FAIL): an `Optional[str]` parameter is a synthesized `_union_*`
variant whose tag `tag_variant` decided `isinstance(x, str)` FALSE (`(6 = 1)`); `\result == 0` PROVED at
afe28c69. CPython `f("a")` = 1.
"""
# pycsl-expected: FAIL
from typing import Optional


#@ ensures \result == 0
#@ assigns \nothing
def f(x: Optional[str]) -> int:
    if isinstance(x, str):
        return 1
    return 0


if __name__ == "__main__":
    assert f("a") == 1
