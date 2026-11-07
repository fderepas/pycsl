r"""Test 8032 -- wall lex-char-class step 4 (expected PASS: UNPROVABLE at base): definitional `isalnum`. CPython: a string is alnum iff it is non-empty and every character is alpha / decimal / digit / numeric, and isalpha is the same with alpha only -- so `s.isalpha()` implies `s.isalnum()` on EVERY string. With the char-quantified definitions (emitted because isalnum co-occurs with isalpha) the implication is a theorem; no axiom.
"""
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ ensures \result == 0
#@ assigns \nothing
def alpha_not_alnum(s: str) -> int:
    if s.isalpha():
        if not s.isalnum():
            return 1
    return 0


if __name__ == "__main__":
    for s in ["", "a", "a1", "1", "_", "été", "½", "ab"]:
        r = alpha_not_alnum(s)
        print("VIOLATION contract" if r != 0 else "result", r)
