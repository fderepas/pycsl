"""Test 0543 — array-valued dicts via the seq SNAPSHOT model (A1-residual,
no-more-int-7 §B').

`Dict[str, List[int]]` stores its list value as an immutable Why3 `seq int`
SNAPSHOT taken at the store site (`docs/pycsl-ownership-discipline.md` §3), NOT a
mutable `array int` alias — so it sidesteps the mutable-aliasing wall the
no-more-int-5 spike hit ("instantiates pure type variable 'v with a mutable type
array"). The snapshot is a sound value-semantics under-approximation.

`d[k] = xs` stores `array_to_seq(xs)` (length-preserving); `len(d[k])` is
`Seq.length`. Under `\\length(xs) == 3` the stored snapshot has length 3, so
reading it back gives `len(d[k]) == 3`.

Fails today: `List[int]` dict values are unrecognized (ν defaults to int), so an
`array int` value is fed into an `int` slot (the reverted spike's ill-typed
WhyML). Flips when ν threads `seq int` + the array→seq snapshot + `Seq.length`.
"""
_ = 0  # anchor
from typing import Dict, List


#@ requires \length(xs) == 3
#@ ensures \result == 3
#@ assigns \nothing
#@ no_exception KeyError
def store_and_len(k: str, xs: List[int]) -> int:
    d: Dict[str, List[int]] = {}
    d[k] = xs
    return len(d[k])
