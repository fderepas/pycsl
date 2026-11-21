r"""Test 3191 — route #282 VERIFIED-CALLER ALIAS CONTROL (expected FAIL): the callee of 3181 called from VERIFIED code as `f(x, x)`.
`g` claims `\result == 0`; CPython returns 1. Fails closed (Why3 "illegal alias", L3-tc).
"""
# pycsl-expected: FAIL
class A:
    def __init__(self) -> None:
        self.v: int = 0

#@ ensures b.v == \old(b.v)
#@ assigns a.v
def f(a: A, b: A) -> None:
    a.v = b.v + 1

#@ ensures \result == 0
def g() -> int:
    x = A()
    f(x, x)
    return x.v


if __name__ == "__main__":
    print(g())  # 1
    assert g() == 1
