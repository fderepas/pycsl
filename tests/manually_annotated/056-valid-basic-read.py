"""Phase 1 test: \valid precondition on basic array reads."""


#@ requires \valid(arr, n)
#@ requires n > 0
#@ ensures \result == arr[0]
#@ assigns \nothing
def first_element(arr: list, n: int) -> int:
    """Return the first element of arr, requiring arr to be a valid region of size n."""
    return arr[0]


#@ requires \valid(arr, n)
#@ requires n >= 2
#@ ensures \result == arr[0] + arr[1]
#@ assigns \nothing
def sum_first_two(arr: list, n: int) -> int:
    """Return the sum of the first two elements."""
    return arr[0] + arr[1]
