"""Test 0351 — Python Reference 3.3.5.1: The purpose of *__class_getitem__* (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_3_3_5_1_a(x: int) -> int:
    """Variation A for The purpose of *__class_getitem__*."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_3_3_5_1_a(4) == 5
