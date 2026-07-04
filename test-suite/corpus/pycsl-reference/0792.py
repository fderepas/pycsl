"""Test 0792 — .replace() content: not-contains identity + char-for-char length + fold.

cleared-string RESIDUALS item 2. `str.replace` lowers to a DETERMINISTIC
`val function str_replace_op` carrying two SOUND laws for CPython all-occurrences
replace (Why3 has no faithful all-occurrences content axiom, so we claim only what
is sound):
  * `replace_absent` — if `pat` occurs NOWHERE in `s` (`"x" not in s`), the result
    EQUALS `s` (native substring-existential negation); this is a genuine CONTENT
    law unprovable under the old length-only model;
  * `replace_same_len` — char-for-char (`len pat == len rep`) preserves length;
  * `fold_replace` — a fully-literal call is CONSTANT-FOLDED by Python's own
    `str.replace`, so `"a.b.c".replace(".","_") == "a_b_c"` is exact content.
The general grow/shrink content stays the honest residual — see the negative 0794.
"""
_ = 0  # anchor


#@ requires "x" not in s
#@ ensures \result == s
#@ assigns \nothing
def replace_absent(s: str) -> str:
    return s.replace("x", "yy")


#@ ensures \result == len(s)
#@ assigns \nothing
def replace_same_len(s: str) -> int:
    r = s.replace("a", "b")
    return len(r)


#@ ensures \result == "a_b_c"
#@ assigns \nothing
def fold_replace() -> str:
    return "a.b.c".replace(".", "_")
