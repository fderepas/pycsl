r"""Test 1806 — ROUTE #216, THE SECOND DOOR (now REFUSED): `#@ conforms_to` with a DUNDER
member.

Protocol conformance records its override pairs in `Module5_IREmitter`, not in
`ir_resolve.apply_inheritance`, so it is an INDEPENDENT recorder — and it had the same
hole, which is what makes #216 a property of the dunder DROP rather than of one collector.

Spelled `m`, this program FAILS with `goal c__m_refines_p` in the emission. Spelled
`__len__`, it reported `All contracts formally proven` over a module whose entire body was
`type p = {  }`.

Now refused with `PYCSL-SEM-DUNDER-OVERRIDE-UNCHECKED`.
"""
# pycsl-flags: --check-behavioral-subtyping --memory-model hoare
# pycsl-expected: FAIL
_ = 0  # anchor
from typing import Protocol


class P(Protocol):
    #@ ensures \result >= 5
    def __len__(self) -> int:
        ...


#@ conforms_to P
class C:
    #@ ensures \result == 0
    def __len__(self) -> int:
        return 0
