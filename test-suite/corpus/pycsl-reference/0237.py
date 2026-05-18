"""Test 0237 — PyCSL Annotation Reference 3.1.20 (slice in contract)"""
_ = 0  # anchor
#@ requires \length(arr) >= n and n >= 0
#@ ensures \result >= 0
def test_slice_contract(arr: list, n: int) -> int:
    return arr[0]

if __name__ == "__main__":
    assert test_slice_contract([5, 6, 7], 2) == 5
