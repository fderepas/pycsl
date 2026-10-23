"""Test 1083 — ROUTE #49's SECOND SHAPE: `a += [x]` on a list PARAMETER, and the plane that
found it was two hours old.

FALSE OF THE PROGRAM: `f([0, 0])` returns 3 in Python, because `a += b` on lists is an
IN-PLACE extend and the caller's list grows.

Same defect as 1080/1081 through a different STATEMENT KIND, so the `.append` refusal does
not reach it: the augmented assignment has its own handler and its own path to the
seq-promotion snapshot. At the parent commit ee263c41 `\\result == 2` PROVED, and it still
proved with the `.append` refusal in place — which is exactly why the second arm exists.

HOW IT WAS FOUND is the part worth carrying: `bin/check-param-mutator-visibility.py` had ten
cells when it was written and `.append` was its only DROPPED one. Extending the table to
seventeen — the remaining ordinary mutators of each receiver type — turned up this second
DROPPED cell within the hour. A table with four cells is a sample; a table with seventeen is
a census of the surface Python programs actually use.

The refusal is gated on the target being a COLLECTION, not merely a parameter, and that
distinction is the whole correctness of the arm: `a += 1` on an INT parameter is FAITHFUL as
a local update, because Python integers are immutable and the caller genuinely does not see
it. Only a list target is passed by reference.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ requires True
#@ ensures True
#@ assigns a
def g(a: list) -> None:
    a += [1]


#@ requires \length(a) == 2
#@ ensures \result == 2
#@ assigns a
def f(a: list) -> int:
    g(a)
    return len(a)
