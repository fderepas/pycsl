"""Test 0138 — Python Reference 6.2.6: List displays"""
_ = 0  # anchor
#@ ensures \result == 3
def test_set_displays() -> int:
    """Set displays: {a, b, c}."""
    s = {1, 2, 3, 2}
    return len(s)

if __name__ == "__main__":
    assert test_set_displays() == 3
