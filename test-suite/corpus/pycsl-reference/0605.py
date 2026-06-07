"""Test 0605 — a string predicate on a computed receiver keeps its receiver (07-0647-spec S3.2/R12).

`s[i].isdigit()` has a computed receiver `s[i]`; it MUST be passed to the predicate
(`isdigit_1 (s[i])`), not dropped to a receiver-less `isdigit_0 ()` — dropping it severs the
result from the value tested (a silent faithfulness violation). RED on the prior commit
(receiver lost).
"""
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ ensures \result == 1 or \result == 0
#@ assigns \nothing
def dig(s: str, i: int) -> int:
    if s[i].isdigit():
        return 1
    return 0
