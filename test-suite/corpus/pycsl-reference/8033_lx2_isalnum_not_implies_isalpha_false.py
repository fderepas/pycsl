r"""Test 8033 -- wall lex-char-class step 4 (expected FAIL): false twin of 8032. The converse does NOT hold: "1".isalnum() is True and "1".isalpha() is False (CPython alnum_not_alpha("1") returns 1), so `\result == 0` must NOT prove -- the definitional model must not over-claim.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ ensures \result == 0
#@ assigns \nothing
def alnum_not_alpha(s: str) -> int:
    if s.isalnum():
        if not s.isalpha():
            return 1
    return 0


if __name__ == "__main__":
    r = alnum_not_alpha("1")
    print("VIOLATION contract" if r != 0 else "result", r)
