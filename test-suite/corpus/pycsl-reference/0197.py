"""Test 0197 - PyCSL Annotation Reference 1.1 (is_sorted contract atom)"""
_ = 0  # anchor
#@ requires \length(arr) >= n
#@ requires n >= 2
#@ requires \is_sorted(arr, 0, n)
#@ ensures arr[0] <= arr[1]
def first_le_second(arr: list, n: int) -> int:
    """Given a sorted array, first element <= second element."""
    return arr[0]
