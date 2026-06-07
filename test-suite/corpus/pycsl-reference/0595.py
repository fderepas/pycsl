"""Test 0595 — global record array-field subscript read/write are concrete (0442.md B1).

Reading or writing a module-global record's array field (`d.disk[i]`) must use the concrete
array ops (`d.disk[i]`, `d.disk[i] <- v` + `Array.length` bounds), NOT the abstract
`subscript_get/set (x:int)` — which, against the `array int` field, is a hard Why3 type error.
Here `poke` writes `d.disk[i] <- v` then reads it back twice; with concrete, consistent reads
the round-trip difference is provably `0`. Before the fix the body emitted
`subscript_set/get d.disk …` and the file did not type-check (the global-record Attribute
receiver, carried under `object`, was not resolved by `_field_type_of`). RED on the prior commit.
"""
# pycsl-flags: --memory-model hoare

#@ class invariant \length(self.disk) >= 8
class Disk:
    def __init__(self) -> None:
        self.disk: list = [0, 0, 0, 0, 0, 0, 0, 0]


d = Disk()


#@ requires 0 <= i and i < 8
#@ ensures \result == 0
#@ assigns d.disk
def poke(i: int, v: int) -> int:
    d.disk[i] = v
    x = d.disk[i]
    y = d.disk[i]
    return y - x
