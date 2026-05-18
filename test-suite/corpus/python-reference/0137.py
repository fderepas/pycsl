"""Test 0137 — Python Reference 6.2.5: Displays for lists, sets and dictionaries"""
_ = 0  # anchor
#@ ensures \result == 3
def test_list_displays() -> int:
    """List displays: [a, b, c] or [expr for x in iter]."""
    a = [1, 2, 3]
    return len(a)

if __name__ == "__main__":
    assert test_list_displays() == 3
