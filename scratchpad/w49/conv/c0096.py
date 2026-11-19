"""probe: annotations"""
_ = 0  # anchor
#@ ensures \result == 0
#@ assigns \nothing
def test_annotations() -> int:
    x: int = 3
    s: str = "ab"
    if x == 3 and len(s) == 2:
        return 0
    return 1
