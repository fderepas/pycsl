"""lv3 SOUNDNESS WITNESS (expected FAIL): 6823 under a claim only one branch could give.

`str_split_ws_op` claims nothing about its pieces, so the model cannot decide whether
`s.split()` is empty: `\\result == 1` must NOT prove (it would mean the truth test was
decided by the model rather than left to `s`). Control: 6823 PROVES.
"""
# pycsl-expected: FAIL


#@ ensures \result == 1
def nonblank(s: str) -> int:
    if s.split():
        return 1
    return 0
