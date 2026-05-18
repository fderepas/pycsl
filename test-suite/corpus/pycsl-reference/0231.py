"""Test 0231 — PyCSL Annotation Reference 3.2.6b (not in membership)"""
_ = 0  # anchor
#@ requires \length(arr) > 0
#@ requires 0 not in arr
#@ ensures \result != 0
def test_not_in_contract(arr: list) -> int:
    return arr[0]

if __name__ == "__main__":
    assert test_not_in_contract([1, 2, 3]) == 1
