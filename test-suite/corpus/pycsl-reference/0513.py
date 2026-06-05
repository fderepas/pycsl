"""Test 0513 — string + dict: a slice length stored in a dict.

`d[2] = len(s[a:b])` stores the length of a substring; reading it back proves `\result == b - a`
(the `str_sub_op` bounds-guarded length lemma, carried through a dict slot)."""
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ requires 0 <= a and a <= b and b <= \str_length(s)
#@ ensures \result == b - a
def slice_len(s: str, a: int, b: int) -> int:
    d = {}
    d[2] = len(s[a:b])
    return d[2]
