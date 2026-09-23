# pycsl-flags: --memory-model hoare
# ROUTE #219 CARRIER 3 (expects SUCCESS today — a SECURITY POLICY silently unenforced).
#
# `#@ happy ... postcond` is the trust-boundary surface: a NAMED property attached to a
# target method and verified as an ordinary contract. Module 3 FINDS the target (it walks
# the AST, where dunders are present) and attaches the clause, so nothing is refused —
# and then Module 5 drops the method, so nothing is checked.
#
# `self.v = 0` from 5 plainly violates `self.v >= \old(self.v)`. Rename `__enter__` to
# `bump` and the identical file FAILS.
#@ happy no_decrease:
#@     targets __enter__
#@     postcond self.v >= \old(self.v)
class C:
    def __init__(self) -> None:
        self.v: int = 5

    #@ assigns self.v
    def __enter__(self) -> int:
        self.v = 0
        return 0
