r"""Test 1424 - ROUTE #144: a `@dataclass`'s `init_params` is built from THIS class's `AnnAssign`s only, and `ir_resolve` merged `fields` but NOT `init_params`. Python's synthesized `__init__` takes the base dataclasses' fields FIRST, so a legal `C(1, 2)` looked OVER-arity to the model, `_call_record_constructor`'s over-arity arm bound NOTHING, and every field took `_field_default`'s DEFINITE 0: `\result == 0` PROVED while CPython returns 2. `apply_inheritance` now prepends the base dataclasses' fields.
"""
# pycsl-expected: FAIL
from dataclasses import dataclass

_ = 0  # anchor


@dataclass
class B:
    a: int


@dataclass
class C(B):
    b: int


#@ ensures \result == 0
#@ assigns \nothing
def probe() -> int:
    c = C(1, 2)
    return c.b
