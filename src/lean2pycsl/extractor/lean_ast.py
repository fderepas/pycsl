"""Surface AST for the supported Lean 4 subset.

Mirrors `rocq2pycsl.extractor.gallina` in spirit, with Lean-specific
differences documented below. The two extractor backends (Lark and
Lean-script) both produce these nodes; the translator
(`lean2pycsl.translator.lean`) lowers them to `pycsl_emit.ir`.

Lean 4 differences from Gallina:

  - Operators have both Unicode and ASCII spellings (`∧`/`/\\`,
    `∀`/`forall`, `∣`/`|`, `→`/`->`, …). The Lark parser normalizes
    both to a single ASCII canonical form on the AST.
  - Binders come in three shapes: explicit `(x : T)`, implicit
    `{x : T}`, and instance-implicit `[I : C T]`. The AST records the
    shape so the translator can strip implicit/instance binders before
    absorption (plan §5.3 watch-out).
  - `partial def` is a thing — Lean's escape hatch for non-terminating
    code. The translator emits `#@ \\diverges` for these.
  - `termination_by` is a separate keyword from `def` (unlike Coq's
    `{measure ...}` which lives inside the binder).
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Union


# ──────────────────────────────────────────────────────────────────────
# Binder shape
# ──────────────────────────────────────────────────────────────────────


class BinderShape(str, enum.Enum):
    """How a binder appears at the Lean surface.

    EXPLICIT         — `(x : T)`
    IMPLICIT         — `{x : T}` (the v1 supported subset typically
                       strips these in the translator)
    INSTANCE_IMPLICIT — `[I : C T]` (always stripped)
    """
    EXPLICIT = "explicit"
    IMPLICIT = "implicit"
    INSTANCE_IMPLICIT = "instance_implicit"


@dataclass(frozen=True)
class Binder:
    """One name+type pair carrying its surface shape.

    Multi-name groups like `(a b : Nat)` are normalized to one Binder
    per name at parse time so downstream code never has to think about
    grouping.
    """
    name: str
    ty: str
    shape: BinderShape


# ──────────────────────────────────────────────────────────────────────
# Expression nodes
# ──────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class LVar:
    name: str


@dataclass(frozen=True)
class LLit:
    """Numeric literal. Lean's `True`/`False` arrive as `LVar`, same
    as in the Gallina AST, and the translator promotes them.
    """
    value: int


@dataclass(frozen=True)
class LApp:
    fn: str
    args: tuple["LeanNode", ...]


@dataclass(frozen=True)
class LBinOp:
    """Binary operator at the Lean surface.

    `op` carries the *canonical ASCII* form even when the source used
    Unicode. Translator opmap lifts it to PyCSL surface. The accepted
    set is:

      "+"   "-"   "*"   "/"   "%"        arithmetic
      "="   "<>"  "<="  "<"   ">="  ">"  comparison
      "/\\" "\\/" "->" "<->"             logical
    """
    op: str
    lhs: "LeanNode"
    rhs: "LeanNode"


@dataclass(frozen=True)
class LUnaryOp:
    """Unary operator. `op` ∈ {`~`, `-`} — `~` covers Lean's `Not P`
    and `¬P`, normalized to a single canonical form."""
    op: str
    arg: "LeanNode"


@dataclass(frozen=True)
class LForall:
    var: str
    ty: str
    body: "LeanNode"
    shape: BinderShape = BinderShape.EXPLICIT


@dataclass(frozen=True)
class LExists:
    var: str
    ty: str
    body: "LeanNode"


@dataclass(frozen=True)
class LDvd:
    """Lean's `a ∣ b` — divisibility.

    The argument order matches Lean's convention: `a ∣ b` means "a
    divides b". `pycsl_emit.ir.Divides(d, n)` uses (divisor, dividend),
    so the translator passes `(d=a, n=b)`.
    """
    a: "LeanNode"
    b: "LeanNode"


@dataclass(frozen=True)
class LUnsupported:
    reason: str
    raw: str


LeanNode = Union[
    LVar,
    LLit,
    LApp,
    LBinOp,
    LUnaryOp,
    LForall,
    LExists,
    LDvd,
    LUnsupported,
]


# ──────────────────────────────────────────────────────────────────────
# Top-level container nodes
# ──────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class LTheorem:
    """A `theorem`/`lemma` declaration.

    `pycsl_spec_target` carries the target function name from the
    `@[pycsl_spec "..."]` attribute when present. None when the
    declaration wasn't tagged. The selector uses this to choose which
    theorems become contracts for which Python functions.
    """
    name: str
    binders: tuple[Binder, ...]
    statement: LeanNode
    pycsl_spec_target: str | None = None
    source_line: int = 0


@dataclass(frozen=True)
class LeanDef:
    """A `def` / `noncomputable def` / `partial def` declaration.

    `params` contains the *explicit* binders (implicit/instance are
    stripped at the parser level since the translator can't use them
    anyway). `is_partial` triggers `#@ \\diverges` emission. `measure`
    is set when the source has a `termination_by ... => <expr>` clause.
    """
    name: str
    params: tuple[Binder, ...]
    return_ty: str
    is_partial: bool = False
    measure: LeanNode | None = field(default=None)
    source_line: int = 0


@dataclass(frozen=True)
class LeanModule:
    """Everything an extractor pulled out of one .lean file."""
    theorems: tuple[LTheorem, ...]
    defs: tuple[LeanDef, ...]
    source_path: str = ""

    def def_(self, name: str) -> LeanDef | None:
        for d in self.defs:
            if d.name == name:
                return d
        return None

    def theorem(self, name: str) -> LTheorem | None:
        for t in self.theorems:
            if t.name == name:
                return t
        return None
