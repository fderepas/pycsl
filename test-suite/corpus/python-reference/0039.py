"""Test 0039 — Python Reference 3.2.1: None"""
_ = 0  # anchor
#@ ensures \result == 0
def test_none_type() -> int:
    """None is the sole value of NoneType."""
    x = None
    if x is None:
        return 0
    return 1

if __name__ == "__main__":
    assert test_none_type() == 0
