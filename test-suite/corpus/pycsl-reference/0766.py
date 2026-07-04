"""Test 0766 — string slicing is content-faithful (adjacent slices rejoin).

cleared-string.md S4. `s[0:2] + s[2:4] == s[0:4]` — a genuine slice-CONTENT law
(`concat_substring` in Why3's native `string.String`), not a tautology and not a
mere length fact. `s[i:j]` lowers to `str_sub_op` pinned to `String.substring`,
so the concatenation of two adjacent slices provably equals the wider slice —
unprovable under the old length-only substring model.
"""
_ = 0  # anchor


#@ requires len(s) >= 4
#@ ensures \result == s[0:4]
#@ assigns \nothing
def adjacent(s: str) -> str:
    return s[0:2] + s[2:4]
