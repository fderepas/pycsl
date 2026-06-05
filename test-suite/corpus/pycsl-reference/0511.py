"""Test 0511 — string + dict: concat-length additivity through a dict.

`d[1] = len(s + t)` stores the length of the concatenation; reading it back proves
`\result == \str_length(s) + \str_length(t)` (concat-length additivity, via `str_concat_op` +
`str_length_op`, carried through a dict slot)."""
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ ensures \result == \str_length(s) + \str_length(t)
def concat_len(s: str, t: str) -> int:
    d = {}
    d[1] = len(s + t)
    return d[1]
