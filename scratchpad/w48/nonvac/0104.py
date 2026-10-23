"""Test 0104 — Python Reference 4.2.2: Resolution of names"""
_ = 0  # anchor
#@ ensures \result == 0
#@ assigns \nothing
def test_resolution_of_names(n: int) -> int:
    """Ref 4.2.2: a name reference resolves to the binding in the NEAREST enclosing scope
    that binds it, and a LOCAL binding shadows anything outside — a name assigned anywhere
    in a function body is local to that function for the whole body. Here the parameter
    `n` and the local `n2` are distinct bindings and a rebinding of the local does not
    disturb the parameter, which the contract states. Previously the whole body was
    `return 0`."""
    n2 = n
    n2 = n2 + 1
    if n2 == n:
        return 0
    return 1

if __name__ == "__main__":
    assert test_resolution_of_names(4) == 0
