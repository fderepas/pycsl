"""Test 0602 — a class whose name is a Why3 reserved word lowers safely (07-0647-spec S1.1/R8).

`class Match` would map to the Why3 keyword `match` (a syntax error in `type match = …`). The
generated type name MUST be a legal, non-reserved identifier (`py_match`), consistently at the
type declaration and every reference. RED on the prior commit (syntax error).
"""
# pycsl-flags: --memory-model hoare
#@ class invariant self.pos >= 0
class Match:
    def __init__(self) -> None:
        self.pos: int = 0


m = Match()


#@ ensures \result >= 0
#@ assigns \nothing
def peek() -> int:
    return m.pos
