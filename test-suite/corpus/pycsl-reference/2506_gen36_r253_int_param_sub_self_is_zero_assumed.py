r"""Test 2506 — route #253 (expected PASS UNDER THE DECLARED MODEL ASSUMPTION BUILTIN-EXACT).

`def f(x: int): return x - x` with `ensures \result == 0` PROVES: the model reads `x: int` as an
EXACT `int`, whose `-` is integer subtraction. CPython returns 7 for `f(I(5))` with
`class I(int): def __sub__(s, o): return 7` (see `__main__`) — a subclass instance is accepted
wherever `int` is (by Python and by type checkers). This is the counterexample of the declared
assumption BUILTIN-EXACT ("a value whose static type is a builtin is an exact instance of it — no
dunder-overriding subclass"), which `pycsl --soundness-report` lists for this file and the reference
docs state. There is no strict mode for it (dropping it would leave no builtin arithmetic at all).
"""
# pycsl-model-assumption: BUILTIN-EXACT
# pycsl-expected: PASS


#@ ensures \result == 0
#@ assigns \nothing
def f(x: int) -> int:
    return x - x


if __name__ == "__main__":
    class I(int):
        def __sub__(self, other: object) -> int:
            return 7
    print(f(5), f(I(5)))  # 0 7: the claim is FALSE for the subclass instance
