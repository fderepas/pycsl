r"""Test 1426 - ROUTE #144, the ORDER: `dataclasses._process_class` walks `cls.__mro__[-1:0:-1]`, the REVERSED MRO, so `Cee(Ay, Bee)(1, 2, 3)` binds bfld=1 and afld=2. The first draft of the #144 repair walked the DECLARED bases left-to-right and PROVED `get() == 1` where CPython gives 2 (a base field cannot be read directly - `o.afld` emits the unmangled name and type-errors - so the probe reads it through the INHERITED METHOD). The merge now reuses the C3 `_in_mro` computed for routes #123/#125. At HEAD this claim is refused for a DIFFERENT reason (the call is over-arity and binds nothing, which is 1443's carrier), so this file guards the REPAIR's own order, not the original defect.
"""
# pycsl-expected: FAIL
from dataclasses import dataclass

_ = 0  # anchor


@dataclass
class Ay:
    afld: int

    #@ requires True
    #@ ensures \result == self.afld
    def get(self) -> int:
        return self.afld


@dataclass
class Bee:
    bfld: int


@dataclass
class Cee(Ay, Bee):
    cfld: int


#@ ensures \result == 1
#@ assigns \nothing
def probe() -> int:
    o = Cee(1, 2, 3)
    return o.get()
