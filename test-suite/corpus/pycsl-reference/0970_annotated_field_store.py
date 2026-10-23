"""Test 0970 — an ANNOTATED store through a non-Name target is a STORE, not a no-op.

`Module5_IREmitter._py_stmt_annassign` is

    if isinstance(stmt.target, ast.Name) and stmt.value is not None:
        ir_stmts.append({"stmt": "Assign", ...})

so `self.x: int = 5` — an `AnnAssign` whose target is an ATTRIBUTE — produced NO IR AT ALL
and the store VANISHED from the model. That is the same fail-OPEN `_py_stmt_assign` was
already fixed for; its own comment records the earlier plain-assignment version of this
bug as "an UNSOUND fail-OPEN: a caller/body could prove the field UNCHANGED after a real
mutation".

`frontend/desugar.normalize_annotated_stores` rewrites the annotated form to the plain one
before Module 5 sees it (outside `__init__`, where the annotation is how the record field
TYPE is recovered), so `_py_stmt_assign` decides — here, a `FieldAssign`.

NEGATIVE TEST, measured: with the normalization removed, `set_to` emits an EMPTY body, the
`ensures self.v == 5` goal is FALSE and the file reports `Verification FAILED`.
"""
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


class Box:
    #@ requires True
    #@ ensures self.v == 0
    #@ assigns self.v
    def __init__(self) -> None:
        self.v: int = 0

    #@ requires True
    #@ ensures self.v == 5
    #@ assigns self.v
    def set_to(self) -> None:
        self.v: int = 5

    #@ requires True
    #@ ensures \result == self.v
    #@ assigns \nothing
    def get(self) -> int:
        return self.v


#@ requires True
#@ ensures \result == 5
#@ assigns \nothing
def driver() -> int:
    b = Box()
    b.set_to()
    return b.get()
