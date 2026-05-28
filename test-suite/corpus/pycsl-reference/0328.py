"""Test 0328 — PyCSL Annotation Reference 11.7.1"""
""  # pycsl
# Memory-model parity: ghost arrays (\copy, \copy_range, \make) require hoare model.
# Under typed/store, array parameters are `loc` (int pointer), not `array int`,
# so Array.copy / Array.sub are type-incorrect in generated WhyML.
# pycsl-flags: --memory-model hoare

#@ requires \length(arr) >= n and n >= 0
#@ ensures \result == n
#@ assigns \nothing
def copy_range_hoare_only(arr: list, n: int) -> int:
    #@ ghost snap : array = \copy_range(arr, 0, n)
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop invariant \forall j; 0 <= j and j < i ==> snap[j] == arr[j]
    #@ loop variant n - i
    while i < n:
        i += 1
    return i


if __name__ == "__main__":
    assert copy_range_hoare_only([10, 20, 30], 3) == 3
    assert copy_range_hoare_only([], 0) == 0
