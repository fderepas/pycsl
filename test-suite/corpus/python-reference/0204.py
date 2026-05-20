"""Test 0204 — Python Reference 8.6.4.10: Class Patterns"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ ensures \result == 3
def test_match_class_patterns() -> int:
    """Class patterns: ClassName(attr=val)."""
    class Point:
        __match_args__ = ("x", "y")
        def __init__(self, x, y):
            self.x = x
            self.y = y
    match Point(1, 3):
        case Point(x=1, y=y):
            return y
        case _:
            return 0

if __name__ == "__main__":
    assert test_match_class_patterns() == 3
