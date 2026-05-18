"""Test 0113 — PyCSL Annotation Reference 3.2.7 (variation B)"""
_ = 0  # anchor
#@ ensures \result == x + x + x
def test_triple_add(x: int) -> int:
    """Triple addition."""
    return x + x + x

if __name__ == "__main__":
    assert test_triple_add(4) == 12
