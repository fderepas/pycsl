"""Test 0282 — Negative: \\result in loop invariant (semantic error E1)"""
# pycsl-expected: FAIL

#@ ensures \result >= 0
#@ assigns \nothing
def bad_loop(n: int) -> int:
    i = 0
    #@ loop invariant \result >= 0
    #@ loop variant n - i
    while i < n:
        i = i + 1
    return i

if __name__ == "__main__":
    print("PASS")
