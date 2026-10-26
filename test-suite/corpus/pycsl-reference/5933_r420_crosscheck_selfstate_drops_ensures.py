"""Route #420 SOUNDNESS WITNESS (expected FAIL): the `recognize_crosscheck_selfstate_bool` bespoke lowering
dropped the declared contract.

Derived from corpus 0962 (same body; contract changed): `IRCrossCheckResult.registry_skipped` declares `#@ ensures False`.
MEASURED at base `b8bd00a9d`: the recognizer replaced the function with a hand-built WhyML
group carrying a fixed `requires { true }` / `ensures { true }`, the declared claim never
reached the emitted WhyML, and the run printed `Verification SUCCESS! All contracts formally
proven.` (a false proof). With the route #420 gate (`generic_fold.bespoke_contract_ok`) the
recognizer declines a function whose contract it does not establish; the generic lowering
carries the claim or refuses, so this file must NOT prove. Control: corpus 0962 (the
same shape under `ensures True`) still PROVES, byte-identical.
"""
# pycsl-expected: FAIL
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


# opaque base "Term" marker: the `Optional[Term]` canon fields carry it as an
# inhabitable option with an OPAQUE payload (`option int`).
class Term:
    pass


@dataclass
class IRCrossCheckResult:
    registry_raw: str = ""
    rocq_canon: Optional[Term] = None
    lean_canon: Optional[Term] = None
    registry_canon: Optional[Term] = None

    #@ requires True
    #@ ensures False
    #@ assigns \nothing
    def registry_skipped(self) -> bool:
        return (not self.registry_raw) and (
            self.rocq_canon is not None or self.lean_canon is not None
        )
