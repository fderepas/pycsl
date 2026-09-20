r"""Test 1683 - ROUTE #193 carrier (gen #30): the PLACEHOLDER array for an iterable the IR could not represent had a KNOWN LENGTH. `_array_coerce_arg` answered `(Array.make 1 0)` - a DEFINITE length-1 array - and `sorted_1` carries `ensures { Array.length result = Array.length a }`, so `len(sorted(x for x in [3, 1, 2]))` PROVED `\result == 1` while CPython answers 3. The defence written beside the placeholder, "the abstract vals have no axioms about their input contents", is about CONTENTS and says nothing about LENGTH. The placeholder is now the OPAQUE `pycsl_unknown_array`, so the length is UNDECIDED. Same family as route #192: a DEFINITE stand-in for an UNKNOWN value is not a placeholder, it is an answer.
"""
# pycsl-expected: FAIL
from typing import List

_ = 0  # anchor


#@ ensures \result == 1
def probe() -> int:
    xs: List[int] = sorted(x for x in [3, 1, 2])
    return len(xs)
