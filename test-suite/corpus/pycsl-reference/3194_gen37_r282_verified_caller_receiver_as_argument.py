r"""Test 3194 — route #282 VERIFIED-CALLER ALIAS CONTROL (expected FAIL): the method of 3184 called from VERIFIED code as `x.bump(x)`.
`g` claims `\result == 0`; CPython returns 1. Fails closed (ill-typed self-call, L3-tc).
"""
# pycsl-expected: FAIL
class A:
    def __init__(self) -> None:
        self.v: int = 0

    #@ ensures o.v == \old(o.v)
    #@ assigns self.v
    def bump(self, o: "A") -> None:
        self.v = o.v + 1

#@ ensures \result == 0
def g() -> int:
    x = A()
    x.bump(x)
    return x.v


if __name__ == "__main__":
    print(g())  # 1
    assert g() == 1
