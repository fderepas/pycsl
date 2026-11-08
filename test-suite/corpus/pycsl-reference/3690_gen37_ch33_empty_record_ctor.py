r"""Test 3690 -- gen #37 ch33 (expected PASS): a FIELD-LESS record type (a class with a base and no fields: `type marker = {  }`) constructed in a body. The record-literal lowering printed the empty literal `{  }`, a Why3 SYNTAX ERROR (fail-closed, but every such body was unverifiable); it now lowers to `(any marker)` -- exact, the type carries no observable field (and two constructions are NOT provably equal, as in CPython). Honest claim must PROVE.
"""
class Base:
    pass


class Marker(Base):
    pass


#@ requires n >= 0
#@ ensures \result == n + 1
#@ assigns \nothing
def f(n: int) -> int:
    m = Marker()
    k = Marker()
    return n + 1
