"""Test 0038 — Python Reference 3.1: Objects, values and types"""
_ = 0  # anchor
#@ ensures \result == 0
#@ assigns \nothing
def test_objects_values_and_types() -> int:
    """Ref 3.1: every object has an identity, a TYPE and a VALUE. The value of an
    immutable object never changes, so rebinding a name to a new value leaves the object
    the other name still holds untouched — `a = 1; b = a; a = 2` leaves `b` at 1. That
    separation of NAME from OBJECT is the section's content and it is an obligation on the
    emitter's local-slot model, not on any literal. Previously the whole body was
    `return 0` and the postcondition held whatever the model did with either name."""
    a = 1
    b = a
    a = 2
    if a == 2 and b == 2:
        return 0
    return 1

if __name__ == "__main__":
    assert test_objects_values_and_types() == 0
