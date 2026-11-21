r"""Test 8031 -- wall lex-char-class step 3 (expected FAIL): false twin of 8030. Determinism relates equal receivers only; it claims NOTHING about which strings are digits, so `\result == 0` for `s[i].isdigit()` must NOT prove (CPython: mismatch("7", 0) returns 1).
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ requires 0 <= i and i < len(s)
#@ ensures \result == 0
#@ assigns \nothing
def mismatch(s: str, i: int) -> int:
    c = s[i]
    if s[i].isdigit():
        return 1
    return 0


if __name__ == "__main__":
    r = mismatch("7", 0)
    print("VIOLATION contract" if r != 0 else "result", r)
