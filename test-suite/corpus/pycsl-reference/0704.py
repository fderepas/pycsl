"""Test 0704 — contract subscript of a module-global's array field (spec-15 / gap-15 Wall B).

A wrapper's `#@ ensures` SUBSCRIPTS a module-global record's array field —
`<global>.<field>[expr]`, e.g. `_lib.arr[0]` — a syntax that previously FAILED AT
PARSE (`Unexpected token '[' … Previous tokens: [Token('CNAME','arr')]`). The grammar
admitted `self.<field>[i]` (`field_subscript`) and bare `name[i]` (`subscript_access`)
and `<global>.<field>` whole (`param_field_access`, gap-10), but had NO production for
the INDEXED read of a module-global's array field. spec-15 adds exactly one `?atom`
alternative (`global_field_subscript`) + its AST node + transformer + Module5 lowering
to `Subscript(Attribute(Var(global), field), index)`, riding the EXISTING gap-10
global-field projection + spec-context `Array.get` machinery (Module6 unchanged).

The method `get0` (on the module-global `_lib`) reports `self.arr[0]`, which parses as
the existing `field_subscript`. The wrapper `peek0` calls `_lib.get0()` and its
`#@ ensures \result == _lib.arr[0]` RE-STATES the consequence through the NEW
`<global>.<field>[expr]` production. The wrapper's postcondition VC links the callee's
`\result == self.arr[0]` (resolved in the caller context to `_lib.arr[0]`) to the
wrapper's `\result == _lib.arr[0]` — proving the consequence CROSSES to the wrapper.
This is the os fstat/dup-wrapper shape (gap-15 Wall B), distilled to a single file.

The class invariant `\length(self.arr) == 4` pins the array length so the body's
array-read bounds VC also discharges. Expected PASS.
"""
# pycsl-flags: --memory-model hoare


#@ class invariant \length(self.arr) == 4
class Lib:
    def __init__(self) -> None:
        self.arr: list = [0, 0, 0, 0]

    #@ requires 0 <= self.arr[0]
    #@ assigns \nothing
    #@ ensures \result == self.arr[0]
    def get0(self) -> int:
        return self.arr[0]


_lib = Lib()


#@ requires 0 <= _lib.arr[0]
#@ assigns \nothing
#@ ensures \result == _lib.arr[0]
def peek0() -> int:
    return _lib.get0()


if __name__ == "__main__":
    pass
