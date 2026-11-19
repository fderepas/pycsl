r"""Test 2570 — route #256 (expected PASS UNDER THE DECLARED MODEL ASSUMPTION FIELD-DISJOINT).

`T.poke` (`assigns self.xs`) writes `self.xs[0] = 7` and returns `self.ys[0]` under `requires
self.ys[0] == 0`; `ensures \result == 0` PROVES: the model gives each mutable field its own region, so
a write through `self.xs` leaves `self.ys` unchanged (the emitted frame says so). CPython returns 7 for
`L = [0]; T(L, L).poke()` (see `__main__`): Python lets two fields hold ONE list. A VERIFIED caller that
builds that alias is refused (R167, routes #243/#244); the residue is an alias built in unverified code,
which is the ownership discipline's rule R1. This is the counterexample of the declared assumption
FIELD-DISJOINT ("two distinct mutable fields hold distinct objects"), which `pycsl --soundness-report`
lists for this file (`t__poke: mutates self.xs, also accesses self.ys`) and the reference docs state.
There is no strict mode (every list/dict/set field frame rests on it).
"""
# pycsl-model-assumption: FIELD-DISJOINT
# pycsl-expected: PASS
from dataclasses import dataclass, field
from typing import List


@dataclass
class T:
    xs: List[int] = field(default_factory=list)
    ys: List[int] = field(default_factory=list)

    #@ requires \length(self.xs) == 1 and \length(self.ys) == 1
    #@ requires self.ys[0] == 0
    #@ ensures \result == 0
    #@ assigns self.xs
    def poke(self) -> int:
        self.xs[0] = 7
        return self.ys[0]


if __name__ == "__main__":
    L = [0]
    print(T([0], [0]).poke(), T(L, L).poke())  # 0 7: the claim is FALSE for the aliased record
