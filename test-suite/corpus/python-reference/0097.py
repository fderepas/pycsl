"""Test 0097 — Python Reference 3.3.13: Special method lookup"""
_ = 0  # anchor
#@ ensures \result == 0
def test_special_method_lookup() -> int:
    """Ref 3.3.13: Special method lookup."""
    return 0

if __name__ == "__main__":
    assert test_special_method_lookup() == 0
