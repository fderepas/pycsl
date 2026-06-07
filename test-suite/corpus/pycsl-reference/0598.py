"""Test 0598 — bytes-method fill-char argument is typed `array int` (0442.md C1).

`s.encode(...).ljust(30, b'\x00')` — the fill char `b'\x00'` lowers to a bytes literal
`(let _alit = Array.make 1 0 in _alit)` (an `array int`), but the `ljust` stub previously typed
that argument `int` → Why3 type error. The fill arg is now recognised as `array int`, so the
padded result (length >= 30) discharges a downstream `\valid(b, 30)`. RED on the prior commit.
"""
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ requires \valid(b, 30)
#@ ensures \result == b[0]
#@ assigns \nothing
def first(b: list) -> int:
    return b[0]


#@ assigns \nothing
def run(name: str) -> int:
    padded = name.encode('utf-8').ljust(30, b'\x00')
    return first(padded)
