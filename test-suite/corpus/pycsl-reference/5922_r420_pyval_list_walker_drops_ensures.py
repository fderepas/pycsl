"""Route #420 SOUNDNESS WITNESS (expected FAIL): the `recognize_pyval_list_walker` bespoke lowering
dropped the declared contract.

Derived from corpus 0943 (same body; contract changed): `walk_path` declares `#@ ensures False`.
MEASURED at base `b8bd00a9d`: the recognizer replaced the function with a hand-built WhyML
group carrying a fixed `requires { true }` / `ensures { true }`, the declared claim never
reached the emitted WhyML, and the run printed `Verification SUCCESS! All contracts formally
proven.` (a false proof). With the route #420 gate (`generic_fold.bespoke_contract_ok`) the
recognizer declines a function whose contract it does not establish; the generic lowering
carries the claim or refuses, so this file must NOT prove. Control: corpus 0943 (the
same shape under `ensures True`) still PROVES, byte-identical.
"""
# pycsl-expected: FAIL
from typing import Any, List


#@ requires True
#@ ensures False
#@ assigns \nothing
def walk_path(node: Any) -> List[str]:
    # Walk a nested (Dot <parent> (Id NAME)) tree, collecting the Id names
    # left-to-right; a reversed leaf list exercises `.extend(reversed(...))`.
    out: List[str] = []
    if not isinstance(node, tuple):
        return out
    if node and node[0] == "Leaf":
        if len(node) >= 2:
            segs = node[1]
            rev: List[str] = []
            if isinstance(segs, tuple):
                for seg in segs:
                    if isinstance(seg, tuple) and seg[0] == "Id" and len(seg) >= 2:
                        rev.append(seg[1])
            out.extend(reversed(rev))
    elif node and node[0] == "Dot":
        if len(node) >= 3:
            out.extend(walk_path(node[1]))
            iid = node[2]
            if isinstance(iid, tuple) and iid[0] == "Id" and len(iid) >= 2:
                out.append(iid[1])
    return out
