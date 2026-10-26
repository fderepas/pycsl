"""Route #420 SOUNDNESS WITNESS (expected FAIL): the `recognize_term_isinstance_fold` bespoke lowering
dropped the declared contract.

Derived from corpus 0950 (same body; contract changed): `has_bad` declares `#@ ensures False`.
MEASURED at base `b8bd00a9d`: the recognizer replaced the function with a hand-built WhyML
group carrying a fixed `requires { true }` / `ensures { true }`, the declared claim never
reached the emitted WhyML, and the run printed `Verification SUCCESS! All contracts formally
proven.` (a false proof). With the route #420 gate (`generic_fold.bespoke_contract_ok`) the
recognizer declines a function whose contract it does not establish; the generic lowering
carries the claim or refuses, so this file must NOT prove. Control: corpus 0950 (the
same shape under `ensures True`) still PROVES, byte-identical.
"""
# pycsl-expected: FAIL
from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class Leaf:
    name: str


@dataclass(frozen=True)
class Bad:
    reason: str


@dataclass(frozen=True)
class Neg:
    op: str
    arg: "Expr"


@dataclass(frozen=True)
class Pair:
    op: str
    left: "Expr"
    right: "Expr"


Expr = "Leaf | Bad | Neg | Pair"


#@ requires True
#@ ensures False
#@ assigns \nothing
def has_bad(e: Expr) -> bool:
    if isinstance(e, Bad):
        return True
    if isinstance(e, Leaf):
        return False
    if isinstance(e, Neg):
        return has_bad(e.arg)
    if isinstance(e, Pair):
        return has_bad(e.left) or has_bad(e.right)
    raise TypeError("unknown")
