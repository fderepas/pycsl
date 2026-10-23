r"""Test 1443 - ROUTE #144, the MULTIPLE-INHERITANCE shape as it stands AT HEAD: `Cee(1, 2, 3)` is over-arity for the model's one-element `init_params`, so it binds NOTHING and the inherited `get()` reads `afld`'s DEFINITE default - `\result == 0` PROVED while CPython returns 2. 1426 is the twin that the FIRST DRAFT of the repair made provable by walking the DECLARED bases instead of the reversed MRO; this one is the carrier that existed before any repair.
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


#@ ensures \result == 0
#@ assigns \nothing
def probe() -> int:
    o = Cee(1, 2, 3)
    return o.get()
