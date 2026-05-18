"""Test 0232 — PyCSL Annotation Reference 3.2.6b (in combined)"""
_ = 0  # anchor
#@ requires \length(arr) >= 2
#@ ensures \result in arr
def test_in_second(arr: list) -> int:
    return arr[1]

if __name__ == "__main__":
    assert test_in_second([5, 7]) == 7
