r"""Test 2362 — route #247 (expected PASS): CONTROL. On an `Any` parameter the identity-keyed `set` (7)
and `dict` (4) tests stay EXCLUSIVE: no Python value is both (`class X(dict, set)` is a layout-conflict
TypeError), so `\result == 1` PROVES (CPython: 1 for `{1}`, `{}`, `5`).
"""
# pycsl-expected: PASS
from typing import Any


#@ ensures \result == 1
#@ assigns \nothing
def f(x: Any) -> int:
    a = 0
    if isinstance(x, set):
        a = 1
    b = 0
    if isinstance(x, dict):
        b = 1
    if a == 1 and b == 1:
        return 0
    return 1


if __name__ == "__main__":
    assert f({1}) == 1 and f({}) == 1 and f(5) == 1
