"""Test 0673 — negative: `\length` on a dict in a NESTED while invariant.

`_validate_predicate_bases` uses the INNERMOST enclosing while's line — here the inner
loop — so the context is `while loop at line N inside function 'f'` with the inner N.
Pins the nearest-enclosing-loop line tracking the B4 IR walk must reproduce.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


def f(d: dict) -> int:
    i = 0
    while i < 2:
        #@ loop invariant \length(d) >= 0
        while i < 1:
            i = i + 1
        i = i + 1
    return 0
