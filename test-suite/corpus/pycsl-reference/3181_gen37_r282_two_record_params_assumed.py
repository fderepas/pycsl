r"""Test 3181 — route #282 (expected PASS UNDER THE DECLARED MODEL ASSUMPTION PARAM-DISJOINT).

`f(a, b)` over two `A` record parameters (`assigns a.v`) writes `a.v = b.v + 1`; `ensures b.v ==
\old(b.v)` PROVES: each record parameter is its own Why3 record. CPython violates it for `x = A();
f(x, x)`. A VERIFIED `f(x, x)` fails closed (illegal alias, corpus 3191). `--soundness-report` lists
PARAM-DISJOINT (`f: writes through a, also accesses b`). No strict mode.
"""
# pycsl-model-assumption: PARAM-DISJOINT
# pycsl-expected: PASS


class A:
    def __init__(self) -> None:
        self.v: int = 0


#@ ensures b.v == \old(b.v)
#@ assigns a.v
def f(a: A, b: A) -> None:
    a.v = b.v + 1


if __name__ == "__main__":
    x = A()
    f(x, x)
    print(x.v)  # 1: b.v changed from 0 to 1
    assert x.v == 1
