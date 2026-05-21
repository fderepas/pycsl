"""Test 0293 — PyCSL Annotation Reference 7.2 — Ghost array variable"""
# pycsl-flags: --no-proof
_ = 0  # anchor

#@ requires \length(arr) == n and n >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def sum_array(arr: list, n: int) -> int:
    #@ ghost snap : array = \copy(arr)
    total = 0
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop invariant total >= 0
    #@ loop variant n - i
    while i < n:
        total = total + arr[i]
        i = i + 1
    return total


if __name__ == "__main__":
    assert sum_array([1, 2, 3], 3) == 6
    assert sum_array([], 0) == 0
    print("PASS")
