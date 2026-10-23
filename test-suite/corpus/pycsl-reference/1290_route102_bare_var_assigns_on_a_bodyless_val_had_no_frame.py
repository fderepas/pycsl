# pycsl-flags: --memory-model hoare
# pycsl-expected: FAIL
"""1290 — (#49) ROUTE #102 EXPLOIT ARM: a BARE `#@ assigns g` on a bodyless `val` emitted no
`writes` either — the FOURTH spelling of "this stub writes through a parameter", and the
fourth one the frame collectors did not cover.

`#@ assigns g` lowers to IR `{"type": "Var", "name": "g"}`. Like route #101's `Subscript`,
it matched neither the `Attribute`/`FieldGet` loop nor the `AssignsRegion` loop, and it never
reached `_unframed_regions`, so route #98's refusal could not fire. MEASURED AT 5795cfef:
this file reported `Verification SUCCESS! All contracts formally proven.` CPython returns 5.

Gen #17 NAMED this carrier when it recorded route #101 and said to CHECK it rather than
assume the one repair covered it. It was checked, it was LIVE, and it is its own route —
>>> A CARRIER SURVIVING (OR PRECEDING) A REPAIR IS A SECOND ROUTE, NOT A FOOTNOTE TO THE
>>> FIRST ONE.

Must FAIL: the third collector arm keys on the RESOLVED write root, so a bare `Var` naming an
array parameter now yields `writes { g }`.
"""


#@ \trusted reviewer: route102
#@ requires \length(g) > 0
#@ assigns g
def scramble(g: list) -> None:
    g[0] = 5


#@ requires \length(a) > 0
#@ requires a[0] == 7
#@ ensures \result == 7
def driver(a: list) -> int:
    scramble(a)
    return a[0]
