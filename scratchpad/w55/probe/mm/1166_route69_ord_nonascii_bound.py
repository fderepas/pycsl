"""1166 — ROUTE #69 NEGATIVE: `ord` of a non-ASCII string proves a FALSE BOUND.

No `no_exception`, no exception, no opt-in of any kind — this is a false postcondition about
an ordinary TOTAL Python expression. A string literal is emitted as its UTF-8 BYTES, and
Why3 `Char` codes are 0..255 by the theory's own axioms, so `ord` reads the FIRST BYTE.
CPython answers 8364.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model typed
_ = 0
#@ ensures \result < 256
#@ assigns \nothing
def f() -> int:
    return ord("€")
