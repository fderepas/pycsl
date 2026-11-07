r"""Test 8034 -- wall lex-char-class step 5 (expected PASS): `<expr> in "<short literal>"` is lowered to a per-literal op whose ensures ENUMERATES the substrings of the literal (exact Python semantics, no string theory needed). Both directions are used: "_" is in "_'" (so the first branch is dead), and a 2-character needle in "_'" can only be "_'" itself.
"""
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ ensures \result == 0
#@ assigns \nothing
def lit_member(s: str) -> int:
    if s == "_" and not (s in "_'"):
        return 1
    if s in "_'" and len(s) == 2 and s != "_'":
        return 2
    return 0


if __name__ == "__main__":
    for s in ["", "_", "'", "_'", "'_", "a", "__"]:
        r = lit_member(s)
        print("VIOLATION contract" if r != 0 else "result", r)
