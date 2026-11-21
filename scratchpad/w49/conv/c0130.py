"""probe: references"""
_ = 0  # anchor
#@ ensures \result == 0
#@ assigns \nothing
def test_references() -> int:
    x: int = 5
    y: int = x
    x = 6
    if y == 5 and x == 6:
        return 0
    return 1
