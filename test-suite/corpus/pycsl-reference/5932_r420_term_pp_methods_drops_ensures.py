"""Route #420 SOUNDNESS WITNESS (expected FAIL): the `recognize_term_pp_methods` bespoke lowering
dropped the declared contract.

Derived from corpus 0960 (same body; contract changed): `App.pp` declares `#@ ensures False` (the multi-function family recognizer; not covered by the levers-r3 term gate).
MEASURED at base `b8bd00a9d`: the recognizer replaced the function with a hand-built WhyML
group carrying a fixed `requires { true }` / `ensures { true }`, the declared claim never
reached the emitted WhyML, and the run printed `Verification SUCCESS! All contracts formally
proven.` (a false proof). With the route #420 gate (`generic_fold.bespoke_contract_ok`) the
recognizer declines a function whose contract it does not establish; the generic lowering
carries the claim or refuses, so this file must NOT prove. Control: corpus 0960 (the
same shape under `ensures True`) still PROVES, byte-identical.
"""
# pycsl-expected: FAIL
from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class Var:
    name: str
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def pp(self) -> str:
        return self.name


@dataclass(frozen=True)
class Num:
    value: int
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def pp(self) -> str:
        return str(self.value)


@dataclass(frozen=True)
class Flag:
    value: bool
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def pp(self) -> str:
        return "true" if self.value else "false"


@dataclass(frozen=True)
class App:
    head: str
    args: Tuple['T', ...]
    #@ requires True
    #@ ensures False
    #@ assigns \nothing
    def pp(self) -> str:
        if not self.args:
            return self.head
        return f"({self.head} {' '.join(a.pp() for a in self.args)})"


@dataclass(frozen=True)
class Bin:
    op: str
    lhs: 'T'
    rhs: 'T'
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def pp(self) -> str:
        return f"({self.lhs.pp()} {self.op} {self.rhs.pp()})"


@dataclass(frozen=True)
class Quant:
    binders: Tuple[str, ...]
    ty: str
    body: 'T'
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def pp(self) -> str:
        binders = " ".join(self.binders)
        return f"(forall {binders} : {self.ty}, {self.body.pp()})"


T = "Var | Num | Flag | App | Bin | Quant"


#@ requires True
#@ ensures True
#@ assigns \nothing
def has_var(t: T) -> bool:
    if isinstance(t, Var):
        return True
    if isinstance(t, (Num, Flag)):
        return False
    if isinstance(t, App):
        return any(has_var(a) for a in t.args)
    if isinstance(t, Bin):
        return has_var(t.lhs) or has_var(t.rhs)
    if isinstance(t, Quant):
        return has_var(t.body)
    raise TypeError("unknown")
