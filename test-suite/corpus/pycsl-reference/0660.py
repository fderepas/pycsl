"""Test 0660 — Track B (b-impl P1/P2): #@ interface narrowing + narrowing VC.

`pack16` has a rich DEFINITION contract (length + the byte-value reconstruction) and a narrow
`#@ interface ensures \length == 2`. The tool emits a narrowing VC `pack16__narrows_ens_0`
(definition ⟹ interface) in the owning `let` — which proves (the interface promises strictly less).
`#@ reveal pack16` in `caller` is a no-op within the owning unit (the definition is the visible `let`).
This is opacity, first-class: importers would see only `\length == 2` (the wall-#3 fix, exercised
cross-module in the os codec); here, single-file, the definition + the proven narrowing are checked.
"""


#@ requires 0 <= a and a <= 65535
#@ assigns \nothing
#@ ensures \length(\result) == 2
#@ ensures \result[0] * 256 + \result[1] == a
#@ interface ensures \length(\result) == 2
def pack16(a: int) -> list:
    return bytes([a // 256, a % 256])


#@ reveal pack16
#@ requires 0 <= x and x <= 65535
#@ assigns \nothing
#@ ensures \result == 2
def caller(x: int) -> int:
    d = pack16(x)
    return len(d)
