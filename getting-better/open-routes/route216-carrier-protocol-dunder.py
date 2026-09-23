"""Route #216 CARRIER, the `#@ conforms_to` door (expects SUCCESS — the false certificate).

Protocol conformance records its override pairs in `Module5_IREmitter`, not in
`ir_resolve.apply_inheritance`, and has the same hole. Spelled `m`, this file reports
FAILED with `goal c__m_refines_p`. Spelled `__len__` it reports

    [+] Verification SUCCESS! All contracts formally proven.

over a module whose entire body is `type p = {  }`.

Run: pycsl.py --memory-model hoare --check-behavioral-subtyping <this file>
"""
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
