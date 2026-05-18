"""Test 0192 — Python Reference 8.6.1: Overview"""
_ = 0  # anchor
#@ ensures \result == 0
def test_match_overview() -> int:
    """Overview of match statement semantics."""
    point = (1, 2)
    match point:
        case (0, 0):
            return 1
        case (x, y):
            assert x == 1 and y == 2
            return 0

if __name__ == "__main__":
    assert test_match_overview() == 0
