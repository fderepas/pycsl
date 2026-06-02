"""Shared first-order IR for cross-prover statement comparison
(proof2why3 Phase 3a — sticky-01.md).

Replaces the v0 regex-based string normalizer with structured ASTs.
Rocq, Lean, and WhyML axiom bodies are all parsed into the SAME IR
shape, after which canonicalization (Phase 3b) produces hashable
representatives that compare via structural equality.

Design constraints:

- **First-order** — no dependent types, no higher-order quantifiers,
  no type-class instances. The gcd theorem family fits cleanly;
  richer theorems (mathlib analysis, dependent CC, …) need a more
  expressive IR.
- **Hashable** — every node implements __hash__ so canonical forms
  collapse via set/dict membership.
- **Unsupported** is a leaf type for constructs the parser doesn't
  understand. Any diff involving Unsupported is a hard FAIL.

Production gap vs sertop/Lean-Elab (per sticky-01.md Phase 1+2):
the parsers here consume the prover's *pretty-printer* output, not
its elaborated AST. Notational quirks (implicit arg insertion,
elaboration unification, type-class dispatch) can confuse them.
For 0342's surface they're sufficient; broader rollout needs
sertop + Lean meta-script extraction.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Tuple


# Frozen dataclasses give us free __hash__ + __eq__ from the field tuple.


@dataclass(frozen=True)
class Var:
    """A free or bound variable reference."""
    name: str

    def pp(self) -> str:
        return self.name


@dataclass(frozen=True)
class IntLit:
    value: int

    def pp(self) -> str:
        return str(self.value)


@dataclass(frozen=True)
class BoolLit:
    value: bool

    def pp(self) -> str:
        return "true" if self.value else "false"


@dataclass(frozen=True)
class App:
    """N-ary application `head arg0 arg1 …`."""
    head: str
    args: Tuple["Term", ...]

    def pp(self) -> str:
        if not self.args:
            return self.head
        return f"({self.head} {' '.join(a.pp() for a in self.args)})"


@dataclass(frozen=True)
class BinOp:
    """Binary operator. The operator is a string token in a small
    canonical set: `=`, `>`, `>=`, `<>`, `+`, `-`, `*`, `mod`, `\\/`,
    `/\\`, `->`, `iff`. We use BinOp for both arithmetic and logical
    operators; the canonicalization step folds them into n-ary
    sorted forms via App nodes for AC operators."""
    op: str
    lhs: "Term"
    rhs: "Term"

    def pp(self) -> str:
        return f"({self.lhs.pp()} {self.op} {self.rhs.pp()})"


@dataclass(frozen=True)
class UnaryOp:
    """Unary operator (currently only logical `not` and arithmetic `-`)."""
    op: str
    arg: "Term"

    def pp(self) -> str:
        return f"({self.op} {self.arg.pp()})"


@dataclass(frozen=True)
class Forall:
    """Universal quantifier with a flat binder list `forall x1 x2 … : ty, body`.

    The binder type `ty` is a string token from a small canonical set
    (`int`, `nat`, `bool`, …); nat/Nat are normalized to int with
    side conditions in Phase 3b."""
    binders: Tuple[str, ...]
    ty: str
    body: "Term"

    def pp(self) -> str:
        binders = " ".join(self.binders)
        return f"(forall {binders} : {self.ty}, {self.body.pp()})"


@dataclass(frozen=True)
class Exists:
    binders: Tuple[str, ...]
    ty: str
    body: "Term"

    def pp(self) -> str:
        binders = " ".join(self.binders)
        return f"(exists {binders} : {self.ty}, {self.body.pp()})"


@dataclass(frozen=True)
class Unsupported:
    """A leaf for constructs the parser can't represent. Carries the
    raw token slice for diagnostic purposes."""
    reason: str
    raw: str

    def pp(self) -> str:
        return f"<UNSUPPORTED: {self.reason}>"


Term = "Var | IntLit | BoolLit | App | BinOp | UnaryOp | Forall | Exists | Unsupported"


# Utility constructors --------------------------------------------------


def mk_arrow_chain(hyps: List[Term], conclusion: Term) -> Term:
    """Build `hyp0 -> hyp1 -> ... -> conclusion` as a right-leaning
    BinOp(`->`, ...) chain."""
    out: Term = conclusion
    for h in reversed(hyps):
        out = BinOp("->", h, out)
    return out


def flatten_arrow_chain(t: Term) -> Tuple[List[Term], Term]:
    """Inverse of mk_arrow_chain: split a right-leaning `->` chain
    into (hypotheses, conclusion)."""
    hyps: List[Term] = []
    cur = t
    while isinstance(cur, BinOp) and cur.op == "->":
        hyps.append(cur.lhs)
        cur = cur.rhs
    return hyps, cur


def free_vars(t: Term) -> set:
    """Compute the set of free variable names in `t`. Used by
    canonicalization's alpha-rename step."""
    if isinstance(t, Var):
        return {t.name}
    if isinstance(t, (IntLit, BoolLit, Unsupported)):
        return set()
    if isinstance(t, App):
        out = set()
        for a in t.args:
            out |= free_vars(a)
        return out
    if isinstance(t, BinOp):
        return free_vars(t.lhs) | free_vars(t.rhs)
    if isinstance(t, UnaryOp):
        return free_vars(t.arg)
    if isinstance(t, (Forall, Exists)):
        return free_vars(t.body) - set(t.binders)
    raise TypeError(f"free_vars: unknown term type {type(t)}")
