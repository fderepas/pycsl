"""Route #420 SOUNDNESS WITNESS (expected FAIL): the `recognize_pyval_list_walker` bespoke lowering
dropped the declared contract.

Derived from corpus 0945 (same body; contract changed): `collect_leaf` declares `#@ no_exception IndexError`, but `iid[0]` raises IndexError on `iid == ()` (CPython: `collect_leaf(("Leaf", ()))` -> IndexError).
MEASURED at base `b8bd00a9d`: the recognizer replaced the function with a hand-built WhyML
group carrying a fixed `requires { true }` / `ensures { true }`, the declared claim never
reached the emitted WhyML, and the run printed `Verification SUCCESS! All contracts formally
proven.` (a false proof). With the route #420 gate (`generic_fold.bespoke_contract_ok`) the
recognizer declines a function whose contract it does not establish; the generic lowering
carries the claim or refuses, so this file must NOT prove. Control: corpus 0945 (the
same shape under `ensures True`) still PROVES, byte-identical.
"""
# pycsl-expected: FAIL
from typing import Any, List


#@ requires True
#@ ensures True
#@ assigns \nothing
#@ no_exception IndexError
def collect_leaf(node: Any) -> List[str]:
    # The per-node reader: a (Leaf (Id NAME) ...) accumulator walker (the callee
    # the search cross-calls when the guard fires).
    out: List[str] = []
    if not isinstance(node, tuple):
        return out
    if node and node[0] == "Leaf":
        if len(node) >= 2:
            iid = node[1]
            if isinstance(iid, tuple) and iid[0] == "Id" and len(iid) >= 2:
                out.append(iid[1])
    return out


#@ requires True
#@ ensures True
#@ assigns \nothing
def find(payload: Any) -> List[str]:
    # Search the tree for the first Leaf subtree and return its collected names.
    if isinstance(payload, tuple):
        if payload and payload[0] == "Leaf":
            return collect_leaf(payload)
        for sub in payload:
            r = find(sub)
            if r:
                return r
    return []
