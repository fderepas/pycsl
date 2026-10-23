"""Test 0619 — `list += list` concatenation proves the length law (07-1705-rev4 P5).

Python `a += b` on lists is concatenation. A growable list is modelled as a
`ref (seq int)`, so the concat `c := !c ++ snapshot(b)` and the return `materialize !c`
let the function PROVE `\\length(\\result) == \\length(a) + \\length(b)` — the faithful
length-additive law, not merely type-checking (the earlier opaque `array_extend` could only
do the latter; 07-1321 S4).

RELAUNCH #48: the accumulator is now a LOCAL `c` rather than the PARAMETER `a`, and the
subject — the length-additive law for `+=` on a growable seq — is unchanged. The reason is
route #49's second shape: `a += b` on a list PARAMETER grows a local SNAPSHOT with no
`writes {a}` frame, so the caller's list is modelled as UNCHANGED while Python has grown it
(`g(a); return len(a)` proved the old length; witness 1083). This driver's own contract was
never wrong — it speaks only about `\\result` — but the SHAPE it demonstrated was, so it is
demonstrated on the shape that is faithful. Two rewrites that do NOT work are recorded so
nobody retries them: `return a + b` and `c = a[:]; c += b` both fail to discharge the length
law."""
# pycsl-flags: --memory-model hoare


#@ requires \length(a) >= 0 and \length(b) >= 0
#@ ensures \length(\result) == \length(a) + \length(b)
#@ assigns \nothing
def cat(a: list, b: list) -> list:
    c = []
    c += a
    c += b
    return c
