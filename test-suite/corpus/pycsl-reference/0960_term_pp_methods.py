"""class-variant-impl.md §OUTCOME-TS RESIDUAL (self-tcb-reduction driver-backlog
item 3): a POSITIVE witness for the RECORD⇄VARIANT BRIDGE that converts the
per-class `.pp` METHODS of a frozen-dataclass term ADT.

Unlike 0958 (a SINGLE-FUNCTION `_pp` isinstance-dispatch catamorphism), here the
pretty-printer is a family of per-variant METHODS on the RECORD types
(`App.pp(self)`, `Bin.pp(self)`, ...), each body a straight-line string build that
recurses via the VIRTUAL `child.pp()` on a `Term`-typed field — the class IS the
dispatch (there is no isinstance inside a method).

The bridge (all source-only, 0 new stubs, ledger 3): (a) the recursive record
fields emit the VARIANT field types (`args: list term`, `lhs/rhs: term`,
`binders: list string`); (b) a SYNTHESIZED unified `pp_term (v_t: term) : string`
catamorphism is assembled from all the pp bodies (`child.pp()` -> `pp_term child`),
a structural `variant { v_t }` fold over the certified `term` inductive (co-landed
axiom-free with `Phase2i_TermIR.v` / `TermIR.lean`; the `str_concat_op`/`str_of_int`
are the leaves' abstract `val`s, spec'd by `concat`, NOT axioms); (c) each
recursive `<cls>__pp (self: <rec>) : string = pp_term (<Ctor> self.<f>...)`
(record→variant injection + delegation). The non-recursive leaves
(Var/Num/Flag) keep their own direct bodies.

`has_var` (an isinstance existence fold) seeds the constructor set + types
`App.args` as `list term` (its `any(has_var(a) for a in t.args)` self-recursion).

PROVES. A facade regression (dropping a recursion, mis-copying a separator, or
losing the arm-per-constructor structure) changes this file's emission (the
mutation-test / vacuity-gate non-vacuity lock; the carrier forces `ensures True`,
so there is no postcondition evil-twin — exactly like the pyval walkers). The 0961
twin (Bin separator ` ` -> `~`) is byte-different here. The recognizer is
fail-closed + gated on `needs_term`, so every other corpus file emits identically.
"""
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
    #@ ensures True
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
