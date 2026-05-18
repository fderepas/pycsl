"""Test 0462 — Python Reference 7.2.1: Augmented assignment (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 3
def test_augmented_b(x: int) -> int:
    """Augmented assignment *=."""
    y = x
    y *= 3
    return y

if __name__ == "__main__":
    assert test_augmented_b(4) == 12
