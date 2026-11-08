r"""Test 1672 - ROUTE #190 carrier (gen #29): a DYNAMIC negative STRING INDEX. `s[i]` shares the `str_sub_op` bridge with the slice, and the emitter's negative-index fence keys on a LITERAL (its own comment says `String.substring s (-1) 1` does not read from the end), so a negative index reaching the bridge through a PARAMETER decided the empty string: `#@ requires i == -1` then `len(s[i])` PROVED `\result == 0` while CPython returns 1. The guarded content law closes it — the bridge now decides nothing for `lo < 0`.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ requires i == 0 - 1
#@ ensures \result == 0
def probe(i: int) -> int:
    s: str = "abc"
    t: str = s[i]
    return len(t)
