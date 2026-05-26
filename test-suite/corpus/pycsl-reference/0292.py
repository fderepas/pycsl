"""Test 0292 — PyCSL Annotation Reference 7.1 — Ghost string variable"""
_ = 0  # anchor

#@ requires n >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def count_chars(n: int) -> int:
    #@ ghost acc : string = ""
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop variant n - i
    while i < n:
        #@ ghost acc = acc ^ "x"
        i = i + 1
    return i


if __name__ == "__main__":
    assert count_chars(0) == 0
    assert count_chars(3) == 3
    print("PASS")
