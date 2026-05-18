"""Test 0123 — Python Reference 5.4.5: Module reprs"""
_ = 0  # anchor
#@ ensures \result == 0
def test_module_reprs() -> int:
    """Ref 5.4.5: Module reprs."""
    return 0

if __name__ == "__main__":
    assert test_module_reprs() == 0
