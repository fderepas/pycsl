"""Route #420 SOUNDNESS WITNESS (expected FAIL): the `recognize_term_flatten_arrow` bespoke lowering
dropped the declared contract.

Derived from corpus 0954 (same body; contract changed): `split_chain` declares `#@ ensures False`.
MEASURED at base `b8bd00a9d`: the recognizer replaced the function with a hand-built WhyML
group carrying a fixed `requires { true }` / `ensures { true }`, the declared claim never
reached the emitted WhyML, and the run printed `Verification SUCCESS! All contracts formally
proven.` (a false proof). With the route #420 gate (`generic_fold.bespoke_contract_ok`) the
recognizer declines a function whose contract it does not establish; the generic lowering
carries the claim or refuses, so this file must NOT prove. Control: corpus 0954 (the
same shape under `ensures True`) still PROVES, byte-identical.
"""
# pycsl-expected: FAIL
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple


@dataclass(frozen=True)
class Leaf:
    name: str


@dataclass(frozen=True)
class Bin:
    op: str
    lhs: "Expr"
    rhs: "Expr"


Expr = "Leaf | Bin"


#@ requires True
#@ ensures True
#@ assigns \nothing
def norm(e: Expr) -> Expr:
    if isinstance(e, Leaf):
        return e
    if isinstance(e, Bin):
        return Bin(e.op, norm(e.lhs), norm(e.rhs))
    raise TypeError("unknown")


#@ requires True
#@ ensures False
#@ assigns \nothing
def split_chain(t: Expr) -> Tuple[List[Expr], Expr]:
    hyps: List[Expr] = []
    cur = t
    while isinstance(cur, Bin) and cur.op == "->":
        hyps.append(cur.lhs)
        cur = cur.rhs
    return hyps, cur
