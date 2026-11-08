"""Route #420 SOUNDNESS WITNESS (expected FAIL): the `recognize_term_free_vars` bespoke lowering
dropped the declared contract.

Derived from corpus 0956 (same body; contract changed): `fvs` declares `#@ ensures False`.
MEASURED at base `b8bd00a9d`: the recognizer replaced the function with a hand-built WhyML
group carrying a fixed `requires { true }` / `ensures { true }`, the declared claim never
reached the emitted WhyML, and the run printed `Verification SUCCESS! All contracts formally
proven.` (a false proof). With the route #420 gate (`generic_fold.bespoke_contract_ok`) the
recognizer declines a function whose contract it does not establish; the generic lowering
carries the claim or refuses, so this file must NOT prove. Control: corpus 0956 (the
same shape under `ensures True`) still PROVES, byte-identical.
"""
# pycsl-expected: FAIL
from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class Leaf:
    name: str


@dataclass(frozen=True)
class App:
    head: str
    args: Tuple["Expr", ...]


@dataclass(frozen=True)
class Bin:
    op: str
    lhs: "Expr"
    rhs: "Expr"


@dataclass(frozen=True)
class Quant:
    binders: Tuple[str, ...]
    body: "Expr"


Expr = "Leaf | App | Bin | Quant"


#@ ensures False
#@ assigns \nothing
def fvs(e: Expr) -> set:
    if isinstance(e, Leaf):
        return {e.name}
    if isinstance(e, App):
        out = set()
        for a in e.args:
            out |= fvs(a)
        return out
    if isinstance(e, Bin):
        return fvs(e.lhs) | fvs(e.rhs)
    if isinstance(e, Quant):
        return fvs(e.body) - set(e.binders)
    raise TypeError("unknown")
