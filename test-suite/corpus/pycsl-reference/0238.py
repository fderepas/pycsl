"""Test 0238 — PyCSL Annotation Reference 7.2 (tuple unpacking)"""
_ = 0  # anchor
#@ requires y > 0
#@ ensures \result >= 0
def test_tuple_unpack(x: int, y: int) -> int:
    q, r = divmod(x, y)
    return q

if __name__ == "__main__":
    assert test_tuple_unpack(10, 3) == 3
    assert test_tuple_unpack(9, 3) == 3
