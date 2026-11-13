r"""Test 9885 -- W-hash (dict-value-model-r4 §2.5, expected PASS): CONTROL: a `PyVal` parameter hashed under `no_exception \all` where a dominating `isinstance` narrows it to hashable builtin classes -- the `if` body, an early `return` on the negation, and a tuple of classes -- is DERIVED hashable and admitted; each function PROVES. REFUSED at base (a `PyVal` value was denied as `Any`).
"""
# pycsl-expected: PASS
from typing import Any

PyVal = Any


#@ no_exception \all
#@ ensures \result == n + 1
def f(v: PyVal, n: int) -> int:
    if isinstance(v, str):
        s = {v}
        return n + 1
    return n + 1


#@ no_exception \all
#@ ensures \result == n + 1
def g(v: PyVal, n: int) -> int:
    if not isinstance(v, str):
        return n + 1
    s = {v}
    return n + 1


#@ no_exception \all
#@ ensures \result == n + 1
def h(v: PyVal, n: int) -> int:
    if isinstance(v, (str, int)):
        s = {v}
    return n + 1


if __name__ == "__main__":
    print(f("a", 0), f([1], 0), g("a", 0), g([1], 0), h(1, 0), h([1], 0))
