"""lv3 SOUNDNESS WITNESS (expected FAIL / refused): a `re.split` pattern whose capture
group need NOT participate in a match.

`re.split(r"(a)|b", "xby")` is `['x', None, 'y']`: the piece is `None` where the
group did not take part, so typing the loop target `str` would be unfaithful. The new
`_classify_iterable` arm accepts a pattern only with no group or ONE group spanning the
WHOLE pattern; `(a)|b` is neither, so the arm declines and the file keeps the old
behaviour (no model -> refused). Control: 6820 (`(\\W+)`, accepted) PROVES.
"""
# pycsl-expected: FAIL
import re


#@ ensures \result >= 0
def count_pieces(s: str) -> int:
    n = 0
    #@ loop invariant n >= 0
    for tok in re.split(r"(a)|b", s):
        n += len(tok)
    return n
