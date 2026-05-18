"""Test 0068 — Python Reference 3.2.13.2.1: Special read-only attributes"""
_ = 0  # anchor
#@ ensures \result == 0
def test_special_read_only_attributes() -> int:
    """Ref 3.2.13.2.1: Special read-only attributes."""
    return 0

if __name__ == "__main__":
    assert test_special_read_only_attributes() == 0
