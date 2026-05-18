"""Test 0043 — PyCSL Annotation Reference 4.9"""
_ = 0  # anchor
#@ ensures \result >= 0
def test_no_ternary(x: int) -> int:
    """if/else ternary is NOT supported in contracts."""
    if x >= 0:
        return x
    return -x

if __name__ == "__main__":
    assert test_no_ternary(-3) == 3
