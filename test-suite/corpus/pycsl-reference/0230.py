"""Test 0230 — PyCSL Annotation Reference 3.2.6b (in membership)"""
_ = 0  # anchor
#@ requires \length(arr) > 0
#@ ensures \result in arr
def test_in_contract(arr: list) -> int:
    return arr[0]

if __name__ == "__main__":
    assert test_in_contract([10, 20, 30]) == 10
