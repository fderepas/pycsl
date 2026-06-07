"""Test 0588 — `zfill(N)` establishes a length lower bound for a downstream `\valid` (1009.md R2).

A bytes-producing pad method (`s.zfill(30)`, like `ljust`/`rjust`) lowers to an abstract
`val zfill_1 (x0: int) : array int`. PyCSL now emits `ensures { Array.length result >= x0 }`
on it (Python pads to AT LEAST the width `x0`), AND tracks the bound local as array-typed so
it is `ref (array int)`, not `ref 0`. Together these discharge `needs30`'s `\valid(b, 30)`
precondition (`Array.length b >= 30`) when fed an `encode(...).zfill(30)` result — the pattern
that blocks `_pack_direntry`'s `\valid(name_bytes, 30)` in the `os` module. RED on the prior
commit (the result typed `int`, a hard Why3 type error).
"""
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ requires \valid(b, 30)
#@ ensures \result == b[0]
#@ assigns \nothing
def needs30(b: list) -> int:
    return b[0]


#@ assigns \nothing
def run(name: str) -> int:
    padded = name.encode('utf-8').zfill(30)
    return needs30(padded)
