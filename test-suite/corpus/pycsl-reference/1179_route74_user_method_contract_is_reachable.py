"""1179 — ROUTE #74 POSITIVE CONTROL: the user's own method contract is reachable.

The same program as 1178, claiming what is TRUE of it (CPython answers 7). This is what
makes the repair more than a refusal: the call site now carries the CALLEE'S OWN verified
postcondition —

    val self_isdigit_0 () : int
      ensures { (result = 7) }          (was: ensures { result = 0 || result = 1 })

— so the false oracle axiom is not merely suppressed, it is REPLACED by the contract the
user actually proved.
"""
# pycsl-expected: PASS
# pycsl-flags: --memory-model hoare
_ = 0


class C:
    #@ ensures \result == 7
    #@ assigns \nothing
    def isdigit(self) -> int:
        return 7

    #@ ensures \result == 7
    #@ assigns \nothing
    def g(self) -> int:
        return self.isdigit()
