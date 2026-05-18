"""Test 0103 — Python Reference 4.2.1: Binding of names"""
_ = 0  # anchor
#@ ensures \result == 0
def test_binding_of_names() -> int:
    """Ref 4.2.1: Binding of names."""
    return 0

if __name__ == "__main__":
    assert test_binding_of_names() == 0
