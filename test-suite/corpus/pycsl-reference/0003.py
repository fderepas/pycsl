"""Test 0003 — PyCSL Annotation Reference 2.1.3"""
_ = 0  # anchor
#@ requires \length(arr) > 0
#@ ensures \result == arr[0]
#@ assigns \nothing
def test_frame_condition(arr: list) -> int:
    """Frame condition: assigns restricts what may be mutated."""
    return arr[0]

if __name__ == "__main__":
    a = [42, 1, 2]
    assert test_frame_condition(a) == 42
    assert a == [42, 1, 2]  # unchanged
