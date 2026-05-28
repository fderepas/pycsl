"""Test 0315 — PyCSL Annotation Reference 7.2.2 — Ghost array \\copy preserves elements (proof)"""
_ = 0  # anchor

#@ requires \length(arr) >= n and n >= 0
#@ ensures \result == n
#@ assigns \nothing
def test_ghost_copy_proof(arr: list, n: int) -> int:
    #@ ghost snap : array = \copy(arr)
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop invariant i > 0 ==> snap[i - 1] == arr[i - 1]
    #@ loop variant n - i
    while i < n:
        i = i + 1
    return i

if __name__ == "__main__":
    assert test_ghost_copy_proof([1, 2, 3], 3) == 3
    assert test_ghost_copy_proof([], 0) == 0
    print("PASS")
