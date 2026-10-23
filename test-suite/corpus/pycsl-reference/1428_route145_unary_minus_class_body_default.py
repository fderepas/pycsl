r"""Test 1428 - ROUTE #145: the CLASS-BODY `@dataclass` default collector keyed on `isinstance(value, ast.Constant)` and PYTHON'S PARSER DOES NOT FOLD, so `xfld: int = -7` is a `UnaryOp`, got no `field_defaults` entry, and fell to `_field_default`'s DEFINITE 0. `\result == 0` PROVED while CPython returns -7. This is gen #27's route #139 one level up: #139 repaired the `__init__`-BODY collector and left this one.
"""
# pycsl-expected: FAIL
from dataclasses import dataclass

_ = 0  # anchor


@dataclass
class Pee:
    xfld: int = -7


#@ ensures \result == 0
#@ assigns \nothing
def probe() -> int:
    p = Pee()
    return p.xfld
