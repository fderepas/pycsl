"""Test 0461 — Python Reference 7.2.1: Augmented assignment (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 5
def test_augmented_a(x: int) -> int:
    """Augmented assignment +=."""
    y = x
    y += 5
    return y

if __name__ == "__main__":
    assert test_augmented_a(3) == 8
