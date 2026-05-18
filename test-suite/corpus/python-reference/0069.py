"""Test 0069 — Python Reference 3.2.13.2.2: Special writable attributes"""
_ = 0  # anchor
#@ ensures \result == 0
def test_special_writable_attributes() -> int:
    """Ref 3.2.13.2.2: Special writable attributes."""
    return 0

if __name__ == "__main__":
    assert test_special_writable_attributes() == 0
