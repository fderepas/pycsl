"""Test 0352 — Python Reference 3.3.5.1: The purpose of *__class_getitem__* (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_3_3_5_1_b(x: int) -> int:
    """Variation B for The purpose of *__class_getitem__*."""
    return x + x

if __name__ == "__main__":
    assert test_ref_3_3_5_1_b(3) == 6
