"""Route #420 SOUNDNESS WITNESS (expected FAIL): the `recognize_pyval_string_walker` bespoke lowering
dropped the declared contract.

Derived from corpus 0942 (same body; contract changed): `first_binder_name` declares `#@ ensures False`.
MEASURED at base `b8bd00a9d`: the recognizer replaced the function with a hand-built WhyML
group carrying a fixed `requires { true }` / `ensures { true }`, the declared claim never
reached the emitted WhyML, and the run printed `Verification SUCCESS! All contracts formally
proven.` (a false proof). With the route #420 gate (`generic_fold.bespoke_contract_ok`) the
recognizer declines a function whose contract it does not establish; the generic lowering
carries the claim or refuses, so this file must NOT prove. Control: corpus 0942 (the
same shape under `ensures True`) still PROVES, byte-identical.
"""
# pycsl-expected: FAIL
from typing import Any, Optional


#@ requires True
#@ ensures False
#@ assigns \nothing
def first_binder_name(node: Any) -> Optional[str]:
    # Walk a nested-tuple binder_annot: find the first ("Id", NAME) field's NAME.
    if not isinstance(node, tuple):
        return None
    for field in node:
        if isinstance(field, tuple) and len(field) >= 2 and field[0] == "Id":
            return field[1]
    return None
