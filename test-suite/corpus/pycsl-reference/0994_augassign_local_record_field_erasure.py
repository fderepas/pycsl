"""Test 0994 — `p.f op= v` on a record-typed LOCAL or PARAMETER was DROPPED. The second
exploitable half of ROUTE #23, and unlike `0993` it is closed by a CAPABILITY rather than
a refusal.

`_py_stmt_augassign` had no arm for an `Attribute` target whose base is a Name other than
`self`, so `e.v += 5` produced NO IR at all. Measured, before the fix, on exactly this
body with `#@ ensures \result == 0`:

    [+] Verification SUCCESS! All contracts formally proven.

while Python returns 5.

THE PLAIN TWIN WAS ALREADY HANDLED. `_py_stmt_assign` grew a `FieldAssign` arm for
`p.f = v` (p in the function symbol table) precisely because that store used to be a
silent no-op — Python objects are passed BY REFERENCE, so a store to a record param field
escapes to the caller. `e.v = e.v + 5` therefore always FAILED this contract correctly.
The augmented spelling was the only way through, which is what made it worth probing.

Desugared to that same proven arm — `p.f = (p.f) op v` — exactly as `c[k] op= v` is
desugared to the `ArraySet` arm beside it. Companion `0995` carries the TRUE
postcondition `\result == 5` over the identical body and PROVES, which nothing could do
before; without it, a test suite cannot tell "the erasure is closed" from "the construct
is banned".

This file is `pycsl-expected: FAIL`: the postcondition is FALSE of the program.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


class E:
    #@ requires True
    #@ ensures self.v == 0
    #@ assigns self.v
    def __init__(self) -> None:
        self.v: int = 0


#@ requires True
#@ ensures \result == 0
def bump() -> int:
    e = E()
    e.v += 5
    return e.v


if __name__ == "__main__":
    print(bump())
