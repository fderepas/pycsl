"""Test 0389 — Python Reference 5.1: :mod:`importlib` (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_5_1_a(x: int) -> int:
    """Variation A for :mod:`importlib`."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_5_1_a(4) == 5
