r"""Test 8035 -- wall lex-char-class step 5 (expected FAIL): false twin of 8034. The fold must not over-claim: "'" IS a substring of "_'" (CPython lit_member("'") returns 1), so `\result == 0` must NOT prove.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ ensures \result == 0
#@ assigns \nothing
def lit_member(s: str) -> int:
    if s in "_'" and s != "_" and s != "":
        return 1
    return 0


if __name__ == "__main__":
    r = lit_member("'")
    print("VIOLATION contract" if r != 0 else "result", r)
