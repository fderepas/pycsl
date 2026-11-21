"""Route #420 SOUNDNESS WITNESS (expected FAIL): the `recognize_term_string_pp` bespoke lowering
dropped the declared contract.

Derived from corpus 0958 (same body; contract changed): `pp` declares `#@ ensures False`.
MEASURED at base `b8bd00a9d`: the recognizer replaced the function with a hand-built WhyML
group carrying a fixed `requires { true }` / `ensures { true }`, the declared claim never
reached the emitted WhyML, and the run printed `Verification SUCCESS! All contracts formally
proven.` (a false proof). With the route #420 gate (`generic_fold.bespoke_contract_ok`) the
recognizer declines a function whose contract it does not establish; the generic lowering
carries the claim or refuses, so this file must NOT prove. Control: corpus 0958 (the
same shape under `ensures True`) still PROVES, byte-identical.
"""
# pycsl-expected: FAIL
from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class Var:
    name: str


@dataclass(frozen=True)
class Num:
    value: int


@dataclass(frozen=True)
class Flag:
    value: bool


@dataclass(frozen=True)
class App:
    head: str
    args: tuple


@dataclass(frozen=True)
class Bin:
    op: str
    lhs: "T"
    rhs: "T"


@dataclass(frozen=True)
class Quant:
    binders: tuple
    body: "T"


T = "Var | Num | Flag | App | Bin | Quant"

_PREC_TOP = 0
_PREC_CMP = 4
_PREC_APP = 7
_PREC_ATOM = 8
_OPPREC = {"->": 1, "\\/": 2}


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


#@ ensures False
#@ assigns \nothing
def pp(t: T, parent_prec: int) -> str:
    if isinstance(t, Var):
        return t.name
    if isinstance(t, Num):
        return str(t.value)
    if isinstance(t, Flag):
        return "true" if t.value else "false"
    if isinstance(t, Quant):
        binders = " ".join(t.binders)
        body = pp(t.body, _PREC_TOP)
        s = f"forall {binders} . {body}"
        return f"({s})" if parent_prec > _PREC_TOP else s
    if isinstance(t, Bin):
        op_prec = _OPPREC.get(t.op, _PREC_CMP)
        if t.op == "->":
            lhs = pp(t.lhs, op_prec + 1)
            rhs = pp(t.rhs, op_prec)
        else:
            lhs = pp(t.lhs, op_prec)
            rhs = pp(t.rhs, op_prec + 1)
        s = f"{lhs} {t.op} {rhs}"
        return f"({s})" if parent_prec > op_prec else s
    if isinstance(t, App):
        if not t.args:
            return t.head
        args_s = " ".join(pp(a, _PREC_ATOM) for a in t.args)
        s = f"{t.head} {args_s}"
        return f"({s})" if parent_prec > _PREC_APP else s
    raise TypeError("unknown")
