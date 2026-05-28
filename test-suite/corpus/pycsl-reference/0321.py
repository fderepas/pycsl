"""Test 0321 — PyCSL Annotation Reference 11.4.3b — Ghost string ^ concatenation proof"""
_ = 0  # anchor

#@ requires n >= 0
#@ ensures \result == n
#@ assigns \nothing
def test_ghost_string_concat(n: int) -> int:
    #@ ghost s : string = ""
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop invariant \str_length(s) == i
    #@ loop variant n - i
    while i < n:
        #@ ghost s = s ^ "x"
        i = i + 1
    return i

if __name__ == "__main__":
    assert test_ghost_string_concat(0) == 0
    assert test_ghost_string_concat(3) == 3
    print("PASS")
