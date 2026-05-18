"""Test 0169 — Python Reference 7.2.1: Augmented assignment statements"""
_ = 0  # anchor
#@ ensures \result == 6
def test_augmented_assignment() -> int:
    """+=, -=, *=, etc."""
    x = 1
    x += 2
    x *= 2
    return x

if __name__ == "__main__":
    assert test_augmented_assignment() == 6
