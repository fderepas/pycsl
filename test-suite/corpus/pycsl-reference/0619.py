"""Test 0619 — `list += list` concatenation proves the length law (07-1705-rev4 P5).

Python `a += b` on lists is concatenation. A grown list PARAM is modelled as a growable
`ref (seq int)` (shadowed at entry via `let a = ref (snapshot a)`), so the concat
`a := !a ++ snapshot(b)` and the return `materialize !a` let the function PROVE
`\length(\result) == \length(a) + \length(b)` — the faithful length-additive law, not merely
type-checking (the earlier opaque `array_extend` could only do the latter; 07-1321 S4).
"""
# pycsl-flags: --memory-model hoare


#@ requires \length(a) >= 0 and \length(b) >= 0
#@ ensures \length(\result) == \length(a) + \length(b)
#@ assigns \nothing
def cat(a: list, b: list) -> list:
    a += b
    return a
