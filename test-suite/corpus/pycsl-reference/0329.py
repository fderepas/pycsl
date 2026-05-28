"""Test 0329 — PyCSL Annotation Reference 11.8.1"""
_ = 0  # anchor
# Proof test for \str_sub: length of a prefix substring equals the prefix length.
# Relies on Why3's substring_length axiom (in string.String):
#   x >= 0 && 0 <= start < length s -> length(substring s start x) = x
#   (when start + x <= length s)

#@ requires n >= 0
#@ ensures \result == n
#@ assigns \nothing
def str_sub_proof(n: int) -> int:
    #@ ghost s : string = ""
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop invariant \str_length(s) == i
    #@ loop invariant i > 0 ==> \str_length(\str_sub(s, 0, i)) == i
    #@ loop variant n - i
    while i < n:
        #@ ghost s = s ^ "x"
        i = i + 1
    return i


if __name__ == "__main__":
    assert str_sub_proof(0) == 0
    assert str_sub_proof(3) == 3
    print("PASS")
