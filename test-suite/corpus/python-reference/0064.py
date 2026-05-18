"""Test 0064 — Python Reference 3.2.11.1: Special attributes"""
_ = 0  # anchor
#@ ensures \result == 0
def test_special_attributes() -> int:
    """Ref 3.2.11.1: Special attributes."""
    return 0

if __name__ == "__main__":
    assert test_special_attributes() == 0
