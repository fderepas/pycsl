"""Test 0354 — Python Reference 3.3.5.2: *__class_getitem__* versus *__getitem__* (variation B)"""
_ = 0  # anchor
#@ ensures \result == x * 2
def test_ref_3_3_5_2_b(x: int) -> int:
    """Variation B for *__class_getitem__* versus *__getitem__*."""
    return x + x

if __name__ == "__main__":
    assert test_ref_3_3_5_2_b(3) == 6
