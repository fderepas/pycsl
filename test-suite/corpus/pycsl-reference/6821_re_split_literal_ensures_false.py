"""lv3 SOUNDNESS WITNESS (expected FAIL): 6820's `re.split` loop under a false claim.

The `re_split_op` model claims nothing about the pieces (a fresh `array string` of any
length), so a contract it cannot carry must NOT prove: a `Verification SUCCESS` here
would mean the new loop arm assumed a fact. Control: 6820 PROVES.
"""
# pycsl-expected: FAIL
import re


#@ ensures \result == 0
def count_pieces(ty: str) -> int:
    n = 0
    #@ loop invariant n >= 0
    for tok in re.split(r"(\W+)", ty):
        n += 1
    return n
