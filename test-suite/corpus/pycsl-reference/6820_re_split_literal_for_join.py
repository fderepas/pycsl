"""lv3 WITNESS (expected PASS): `for tok in re.split(<pattern literal>, <str>)`.

The loop iterates the receiver-passing `array string` `re_split_op` (a plain `val`,
content unmodelled: an over-approximation that assumes nothing), materialised once, so
the loop has a real bound and a termination variant, the target `tok` is a string, and
`"".join(parts)` over the accumulated pieces is a string. The pattern `(\\W+)` is a
literal that compiles and has exactly one capture group spanning the whole pattern
(every piece is a `str`, never `None`). `count_pieces` claims the count of pieces is non-negative (the loop carries it);
`rejoin` is the mirror's `_normalize_type_string` loop (type-safety and termination).
Base: REFUSED (route #325, `re.split` had no model). Control of 6821/6822.
"""
# pycsl-expected: PASS
import re


#@ ensures \result >= 0
def count_pieces(ty: str) -> int:
    n = 0
    #@ loop invariant n >= 0
    for tok in re.split(r"(\W+)", ty):
        n += 1
    return n


#@ assigns \nothing
def rejoin(ty: str) -> str:
    parts = []
    for tok in re.split(r"(\W+)", ty):
        if tok and tok[0].isalpha():
            parts.append(tok.lower())
        else:
            parts.append(tok)
    return "".join(parts)
