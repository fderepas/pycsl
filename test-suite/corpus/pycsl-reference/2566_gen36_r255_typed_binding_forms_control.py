r"""Test 2566 — route #255 CONTROL (expected PASS): the binding forms route #255 adds to the erased-local
fixpoint (walrus, tuple unpack) and the call results it erases (missing/`Any` return, non-unit callee)
leave TYPED values alone: a walrus or tuple-unpack target bound from an `int`, the result of a function
declared `-> int`, and `len` of an `Any` value (CPython enforces an `int` result) keep their laws.
CPython: `f(3, [1])` is 0 and `k(5)` is 0.
"""
# pycsl-expected: PASS
from typing import Any, List


#@ ensures \result == z
#@ assigns \nothing
def h(z: int) -> int:
    return z


#@ ensures \result == 0
#@ assigns \nothing
def f(n: int, x: Any) -> int:
    a, b = n, n
    w = h(n)
    c = len(x)
    if (v := n) > 0:
        return (v - v) + (a - b) + (w - w) + (c - c)
    return (a - b) + (w - w) + (c - c)


#@ ensures \result == 0
#@ assigns \nothing
def k(n: int) -> int:
    v = abs(n)
    return v - v


if __name__ == "__main__":
    print(f(3, [1]), k(5))
