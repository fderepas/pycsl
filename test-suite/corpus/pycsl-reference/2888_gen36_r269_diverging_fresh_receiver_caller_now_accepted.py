r"""Test 2888 — route #269 R1 (expected PASS; FAILED at 8b0bfbbd): 2880 with the caller
HONESTLY marked `#@ \diverges` — partial correctness, `\result == 7` IF it returns. The
`C().spin(k)` stub now carries `diverges`, so Why3 accepts the clause (before: "this
expression does not diverge"). `m`'s `requires k <= 0` keeps every argument it ADMITS
terminating (the contract-truth plane samples them; a precondition on `spin` itself would
meet route #167's fail-closed assert at a receiver-form call); the stub's divergence is what
Why3 needs either way. CPython: `m(0)` returns 7.
"""
class C:
    def __init__(self) -> None:
        self.n: int = 0

    #@ ensures \result == 0
    #@ assigns \nothing
    #@ \diverges
    def spin(self, k: int) -> int:
        while k > 0:
            k = k + 1
        return 0

    #@ requires k <= 0
    #@ ensures \result == 7
    #@ assigns \nothing
    #@ \diverges
    def m(self, k: int) -> int:
        C().spin(k)
        return 7

if __name__ == "__main__":
    print(C().m(0))
