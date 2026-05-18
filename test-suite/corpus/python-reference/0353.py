"""Test 0353 — Python Reference 3.3.5.2: *__class_getitem__* versus *__getitem__* (variation A)"""
_ = 0  # anchor
#@ ensures \result == x + 1
def test_ref_3_3_5_2_a(x: int) -> int:
    """Variation A for *__class_getitem__* versus *__getitem__*."""
    return x + 1

if __name__ == "__main__":
    assert test_ref_3_3_5_2_a(4) == 5
