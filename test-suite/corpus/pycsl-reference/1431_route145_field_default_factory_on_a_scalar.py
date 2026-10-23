r"""Test 1431 - ROUTE #145, carrier-rerun on its own repair: a `default_factory` RUNS A FUNCTION at construction time. For a COLLECTION field the typed default is what `dict`/`set`/`list` produce, so those 13 corpus sites are faithful and untouched; for a SCALAR field the model handed back a DEFINITE 0 and `\result == 0` PROVED while CPython returns 5. A scalar `default_factory` field is now marked UNKNOWN.
"""
# pycsl-expected: FAIL
from dataclasses import dataclass, field

_ = 0  # anchor


def five() -> int:
    return 5


@dataclass
class Pee:
    xfld: int = field(default_factory=five)


#@ ensures \result == 0
#@ assigns \nothing
def probe() -> int:
    p = Pee()
    return p.xfld
