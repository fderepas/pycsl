r"""Test 1952 — gen #36 (expected PASS): an UNSHADOWED module-level string constant
(`PREFIX = "warn: "`) is classified as a string by `_is_string_expr`, matching its lowering
to the real Why3 literal (0442 C5), so `PREFIX + s` takes the faithful `str_concat_op` (length
law) and `len(PREFIX + s) == len(s) + 6` proves. Before, the constant was not classified and
the claim did not prove. (The same classification routes the mirror's
`_ERR_UNPROTECTED_WRITE % (...)` to the string `str_mod_op`.) Twin: 1953 (must FAIL).
"""
# pycsl-expected: PASS
from __future__ import annotations
_ = 0  # anchor

PREFIX = "warn: "


#@ ensures \result == len(s) + 6
def tag_len(s: str) -> int:
    t = PREFIX + s
    return len(t)
