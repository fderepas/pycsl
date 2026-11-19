"""Test 0940 — r1-setop I1 (POSITIVE, string twin of 0833/0821): by-ref Set[str] PARAM is string-keyed.

r1-setop-impl.md I1 (self-tcb-reduction). The string-element twin of the `Set[int]` param
0821/0833: an in-place `s.add(x)` on a `Set[str]` PARAMETER (a mutated-collection param, so
Python's by-reference escape makes it a caller-visible mutable `ref`) is modelled as a
STRING-keyed `ref (map string (option int))` — the set element IS the key, so `s.add(x)`
writes the RAW native string element (`s := map_update_some !s x 0`) and the contract
`#@ ensures x in s` reads it back through the same raw native string key
(`Map.get !s x <> None`). NO `str_hash_op`: the write and the membership read agree on the
injective Why3 string key (a mismatch would be a WhyML type error).

UNPROVABLE / ill-typed under the retired int-keyed lowering (`ref (map int (option int))`):
the `.add`/membership already emit the raw string key `x` (Module5's usage-based κ inference
tags a set param whose `.add`/`in` uses a provably-string key), so the int-keyed parameter
TYPE disagreed with the string-keyed operations — a `map int` indexed by a `string`. I1
threads κ=string from `_dict_key_types` into the by-ref set param TYPE so the plane agrees.

Complements 0833 (`Set[int]` stays `map int (option int)`, byte-identical): the κ=string
branch fires only for a provably-string set element, so `Set[int]` params are untouched.
"""
_ = 0  # anchor
from typing import Set


#@ ensures x in s
def add_it(s: Set[str], x: str) -> None:
    s.add(x)
