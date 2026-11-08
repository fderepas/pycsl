r"""Test 3184 — route #282 (expected PASS UNDER THE DECLARED MODEL ASSUMPTION PARAM-DISJOINT).

`A.bump(self, o)` (`assigns self.v`) writes `self.v = o.v + 1`; `ensures o.v == \old(o.v)` PROVES: the
receiver and a parameter of its own class are distinct Why3 records. CPython violates it for
`x.bump(x)`. A VERIFIED `x.bump(x)` is ill-typed (fail-closed, corpus 3194). `--soundness-report`
lists PARAM-DISJOINT (`a__bump: writes through self, also accesses o`). No strict mode.
"""
# pycsl-model-assumption: PARAM-DISJOINT
# pycsl-expected: PASS


class A:
    def __init__(self) -> None:
        self.v: int = 0

    #@ ensures o.v == \old(o.v)
    #@ assigns self.v
    def bump(self, o: "A") -> None:
        self.v = o.v + 1


if __name__ == "__main__":
    x = A()
    x.bump(x)
    print(x.v)  # 1: o.v changed from 0 to 1
    assert x.v == 1
