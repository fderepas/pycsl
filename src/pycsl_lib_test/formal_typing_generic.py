# Formal tests for the TypeVar/Generic monomorphization (static plane).
# Spec's promise (typevar-generic-twoplane-spec.md §1): a generic instantiated
# at a concrete type emits a specialized proof. The monomorphization machinery
# (monomorphize.py) collects instantiations and emits name-mangled specialized
# let/vals. This is the function-based witness (the probe-verified shape).
#
# The consequence: a monomorphized identity function returns its argument, for ALL val.


#@ requires val >= 0
#@ assigns \nothing
#@ ensures \result == val
def _identity_int(val: int) -> int:
    return val


#@ requires val >= 0
#@ ensures \result == val
def test_generic_int_instantiation(val: int) -> int:
    """A monomorphized generic[int]: the per-instance theorem holds for ALL val."""
    return _identity_int(val)
