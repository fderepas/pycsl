"""Route #420 SOUNDNESS WITNESS (expected FAIL): the `recognize_pyval_flatten` bespoke lowering
dropped the declared contract.

Derived from corpus 0948 (same body; contract changed): `flatten` declares `#@ ensures False`.
MEASURED at base `b8bd00a9d`: the recognizer replaced the function with a hand-built WhyML
group carrying a fixed `requires { true }` / `ensures { true }`, the declared claim never
reached the emitted WhyML, and the run printed `Verification SUCCESS! All contracts formally
proven.` (a false proof). With the route #420 gate (`generic_fold.bespoke_contract_ok`) the
recognizer declines a function whose contract it does not establish; the generic lowering
carries the claim or refuses, so this file must NOT prove. Control: corpus 0948 (the
same shape under `ensures True`) still PROVES, byte-identical.
"""
# pycsl-expected: FAIL
from typing import Any, List


#@ requires True
#@ ensures False
#@ assigns \nothing
def flatten(node: Any) -> List[Any]:
    # Collect this node and all its sub-nodes at any depth (the self-node HEAD
    # variant: `out.append(node)` before the spine fold → `Cons v_node (...)`).
    out: List[Any] = []
    if isinstance(node, tuple):
        out.append(node)
        for sub in node:
            out.extend(flatten(sub))
    return out
