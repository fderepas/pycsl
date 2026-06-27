# Formal tests for the NoReturn lowering (static plane, NR1/NR3).
# Spec's promise (noreturn-twoplane-spec.md §1): -> NoReturn carries a false
# postcondition (NR1) and successors are unreachable (NR3). NoReturn is a type
# marker (= None), not a callable shim, so these test the LOWERING.
#
# NR1: a NoReturn function that raises discharges (false post by path-absence).


#@ ensures False
def test_noreturn_raises() -> None:
    """A -> NoReturn function that raises discharges the false post (NR1)."""
    raise Exception()
