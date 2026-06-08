"""Test 0653 — value-returning record-method call (the companion the void Gap-7 fix must not regress).

`b = Box(5); return b.get()` proves `\result == 5` via the existing field-RESULT-ensures path
(`val b_get_0 (self: box) : int ensures { result = self.x }`). Pairs with 0652 so a regression in the
shared `field_spec` resolution path (extended by gap7-spec-rev2) is caught either way.
"""


class Box:
    #@ assigns self.x
    #@ ensures self.x == v
    def __init__(self, v: int) -> None:
        self.x: int = v

    #@ assigns \nothing
    #@ ensures \result == self.x
    def get(self) -> int:
        return self.x


#@ ensures \result == 5
#@ assigns \nothing
def driver() -> int:
    b = Box(5)
    return b.get()
