"""S4 RUNTIME gate — R1/R2: TypeVar/Generic are introspectable objects, no check.

Per the two-plane spec §2: `TypeVar("T", bound=int)` constructs an object whose
`__bound__` is `int`; `Generic[T]` / `C[int]` constructs a GenericAlias recording
`__args__`; the bound is NOT checked at runtime (R3). A shim that CHECKED
anything S3 says is unchecked FAILS this gate.

This driver exercises the shim's identity/introspection behaviour. It is a
runtime-only check (no formal proof) — the shim's contract is `ensures \result
== \result` (identity), and `C[int]()` is the ordinary constructor.
"""
# pycsl-flags: --no-proof
# pycsl-expected: SUCCESS (shim is identity; no enforcement)
from typing import TypeVar, Generic

T = TypeVar("T", bound=int)

class C(Generic[T]):
    def __init__(self):
        self._v = 0

if __name__ == "__main__":
    # R1: TypeVar is an introspectable object.
    assert T.__name__ == "T"
    assert T.__bound__ is int
    # R2: C[int] is a GenericAlias; C[int]() is an ordinary instance.
    c = C[int]()
    assert isinstance(c, C)
    # R3: the bound is NOT checked at runtime — C[str]() constructs fine.
    c2 = C[str]()
    assert isinstance(c2, C)
    print("R1/R2/R3 OK")
