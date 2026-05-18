"""Test 0390 — Python Reference 5.1: :mod:`importlib` (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_5_1_b(x: int) -> int:
    """Variation B for :mod:`importlib`."""
    return x + x

if __name__ == "__main__":
    assert test_ref_5_1_b(3) == 6
