r"""Test 2548 — route #254 CONTROL (expected PASS): the same callee `g` (mutates `x`, reads `y`) handed two
DISTINCT sets — directly, through a forwarding function, and with a fresh literal in the read slot — keeps
proving: the #254 rule refuses only an object that may reach two slots of one call.
CPython: `m1()`, `m2()`, `m3()` are all False.
"""
# pycsl-expected: PASS
from typing import Set


#@ requires not (1 in y)
#@ ensures \result == False
#@ assigns x
def g(x: Set[int], y: Set[int]) -> bool:
    x.add(1)
    return 1 in y


#@ requires not (1 in q)
#@ ensures \result == False
#@ assigns p
def mm(p: Set[int], q: Set[int]) -> bool:
    return g(p, q)


#@ ensures \result == False
#@ assigns \nothing
def m1() -> bool:
    a: Set[int] = set()
    b: Set[int] = set()
    return g(a, b)


#@ ensures \result == False
#@ assigns \nothing
def m2() -> bool:
    a: Set[int] = set()
    b: Set[int] = set()
    return mm(a, b)


#@ ensures \result == False
#@ assigns \nothing
def m3() -> bool:
    a: Set[int] = set()
    return g(a, set())


if __name__ == "__main__":
    print(m1(), m2(), m3())
