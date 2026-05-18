"""Test 0012 — Python Reference 2.1.10: End marker"""
_ = 0  # anchor
#@ ensures \result == 0
def test_end_marker() -> int:
    """The end of input serves as an implicit end marker."""
    return 0

if __name__ == "__main__":
    assert test_end_marker() == 0
