"""Route #420 SOUNDNESS WITNESS (expected FAIL): the `recognize_generic_fold` bespoke lowering
dropped the declared contract.

Derived from corpus 0883 (same body; contract changed): `collect_written` declares `#@ ensures False`.
MEASURED at base `b8bd00a9d`: the recognizer replaced the function with a hand-built WhyML
group carrying a fixed `requires { true }` / `ensures { true }`, the declared claim never
reached the emitted WhyML, and the run printed `Verification SUCCESS! All contracts formally
proven.` (a false proof). With the route #420 gate (`generic_fold.bespoke_contract_ok`) the
recognizer declines a function whose contract it does not establish; the generic lowering
carries the claim or refuses, so this file must NOT prove. Control: corpus 0883 (the
same shape under `ensures True`) still PROVES, byte-identical.
"""
# pycsl-expected: FAIL
from typing import Any, Set


#@ requires True
#@ ensures False
#@ assigns written
def collect_written(node: Any, written: Set[str]) -> None:
    if isinstance(node, dict):
        if node.get("stmt") == "ArraySet":
            arr = node.get("array")
            if (isinstance(arr, dict) and arr.get("type") == "FieldGet"
                    and arr.get("object") == "self"):
                written.add(arr.get("field"))
        for v in node.values():
            collect_written(v, written)
    elif isinstance(node, list):
        for x in node:
            collect_written(x, written)
