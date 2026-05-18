"""Test 0236 — PyCSL Annotation Reference 3.1.20 (slice in body)"""
# pycsl-flags: --no-proof
_ = 0  # anchor
#@ requires \length(arr) >= 3
#@ ensures \result >= 0
def test_slice_body(arr: list) -> int:
    sub = arr[0:2]
    return arr[0]

if __name__ == "__main__":
    assert test_slice_body([1, 2, 3]) == 1
