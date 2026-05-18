"""Test 0079 — Python Reference 3.3.2.4: __slots__"""
_ = 0  # anchor
#@ ensures \result == 0
def test_slots() -> int:
    """__slots__ restrict instance attributes."""
    class C:
        __slots__ = ("x", "y")
    c = C()
    c.x = 1
    c.y = 2
    assert c.x + c.y == 3
    return 0

if __name__ == "__main__":
    assert test_slots() == 0
