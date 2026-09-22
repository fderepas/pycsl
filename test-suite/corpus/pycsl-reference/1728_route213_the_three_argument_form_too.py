r"""Test 1728 — ROUTE #213, THE SPELLING MY OWN REFUSAL MISSED.

The first version of #213's refusal was keyed on `len(args) <= 2`, because the witness
(1726) happened to use the NO-DEFAULT form. The THREE-ARGUMENT form has exactly the same
defect: for an UNKNOWN-class receiver, route #197's per-site constant is used whether or
not a default is written, so

    x = getattr(o, "a", 0)
    mutate(o)                 # writes o.a = 99
    y = getattr(o, "a", 0)
    return x - y

PROVED `\result == 0` WITH THE NARROW CHECK IN PLACE. CPython answers -98 for an object
whose `a` is 1.

This is the campaign's own lesson (i) — NAME WHICH SPELLINGS WERE RUN — missed on my own
patch for the SECOND time in one day (route #208 was the first, twenty minutes after #206).
Both times the cause was identical: I derived the guard from the shape of the witness I had
just written instead of from the property the guard is about.

The refusal is now arity-blind. Controls: 1727 (two reads, no call) and corpus 1073 (two
DIFFERENT getattr expressions with the same `{}` default, which must stay provably equal —
route #47's granularity) both still prove.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
from typing import Any

_ = 0  # anchor


#@ assigns o.a
def mutate(o: Any) -> None:
    o.a = 99


#@ assigns o.a
#@ ensures \result == 0
def f(o: Any) -> int:
    x = getattr(o, "a", 0)
    mutate(o)
    y = getattr(o, "a", 0)
    return x - y
