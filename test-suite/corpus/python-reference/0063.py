"""Test 0063 — Python Reference 3.2.10.2: Special methods"""
_ = 0  # anchor
#@ ensures \result == 0
def test_special_methods() -> int:
    """Ref 3.2.10.2: Special methods."""
    return 0

if __name__ == "__main__":
    assert test_special_methods() == 0
