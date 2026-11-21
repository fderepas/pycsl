"""Test 0103 — Python Reference 4.2.1: Binding of names"""
_ = 0  # anchor
#@ ensures \result == 0
#@ assigns \nothing
def test_binding_of_names() -> int:
    """Ref 4.2.1: an assignment BINDS a name in the current scope, and a later assignment
    REBINDS it — the name refers to whatever it was last bound to, and a read after the
    rebinding sees the new value. The contract states the value after two bindings, which
    is an obligation on the emitter's local-slot model (a `ref` that is written twice),
    not on any literal. Previously the body was `return 0`."""
    x = 1
    x = x + 1
    y = x
    x = 99
    if x == 99 and y == 3:
        return 0
    return 1

if __name__ == "__main__":
    assert test_binding_of_names() == 0
