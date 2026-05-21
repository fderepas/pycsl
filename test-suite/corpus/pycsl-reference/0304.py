"""Test 0304 — Negative: ghost string += (augmented assignment rejected at Module4)"""
# pycsl-expected: FAIL
# pycsl-flags: --no-proof
_ = 0  # anchor

#@ requires n >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def bad_string_aug(n: int) -> int:
    #@ ghost acc : string = ""
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop variant n - i
    while i < n:
        #@ ghost acc += "x"
        i = i + 1
    return i

if __name__ == "__main__":
    print("PASS")
