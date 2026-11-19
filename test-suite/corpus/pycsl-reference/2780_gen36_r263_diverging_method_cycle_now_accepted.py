r"""Test 2780 — route #263 (expected PASS; FAILED at 283d1033): the 2770 cycle HONESTLY marked
`#@ \diverges` — partial correctness (`\result == 0` IF it returns), which is what the
circular assumption of the stub's postcondition soundly gives. The stub now carries
`diverges`, so Why3 accepts the `diverges` clause (before: "this expression does not
diverge"). CPython: RecursionError — it never returns, so the partial claim is vacuously true.
"""
class C:
    def __init__(self) -> None:
        self.n: int = 0

    #@ ensures \result == 0
    #@ assigns \nothing
    #@ \diverges
    def m(self, k: int) -> int:
        return self.m(k)

if __name__ == "__main__":
    import sys; sys.setrecursionlimit(100)
    try:
        print(C().m(1))
    except RecursionError:
        print("RecursionError")
