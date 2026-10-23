"""Route #216 CARRIER, the `#@ conforms_to` door (expects SUCCESS — the false certificate).

Protocol conformance records its override pairs in `Module5_IREmitter`, not in
`ir_resolve.apply_inheritance`, and has the same hole. Spelled `m`, this file reports
FAILED with `goal c__m_refines_p`. Spelled `__len__` it reports

    [+] Verification SUCCESS! All contracts formally proven.

over a module whose entire body is `type p = {  }`.

(#49) STATUS UPDATE, SAME NIGHT: route #216 is now CLOSED by a refusal at the
`_run_pipeline` choke point (`PYCSL-SEM-DUNDER-OVERRIDE-UNCHECKED`), gated on
`--check-behavioral-subtyping`. THIS FILE NOW REFUSES, and that flip is the evidence of
closure. It is kept as the pre-refusal reproduction; the standing corpus witnesses are
1805 (this shape), 1806 (the `#@ conforms_to` door), 1807 (a dunder with no override, which
must still PASS) and 1808 (the same violation spelled `m`, which must still FAIL).

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
