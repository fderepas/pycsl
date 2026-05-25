"""IR node types.

Mirrors `rocq2pycsl-plan.md` §4 and `lean2pycsl-plan.md` §4 exactly. The
two converters target this shared shape so the bridge can compare them.

Design notes:

- Every binder records the source-language type as a string (`"nat"`,
  `"int"`, `"Nat"`, `"Z"`). It is *advisory* — the translator decides
  whether to emit a `requires v >= 0` for `nat`/`Nat` quantifiers.
- `Result` is a placeholder that the translator substitutes for the
  target function symbol applied to absorbed parameters.
- `Unsupported` is the explicit "didn't translate" marker so a partial
  pipeline can still produce a useful diff. The `reason` is human text;
  `raw` is whatever fragment the extractor was looking at.
- AC operators (`and`, `or`, `+`, `*`) use `BinOp` here. The bridge's
  canonicalizer is responsible for AC-flattening into n-ary form
  (pycsl-bridge-plan.md §3.2).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Union


# ──────────────────────────────────────────────────────────────────────
# Expression nodes
# ──────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class Var:
    name: str


@dataclass(frozen=True)
class Lit:
    value: Union[int, bool]


@dataclass(frozen=True)
class Result:
    """Placeholder for the target function applied to its absorbed parameters.

    The translator replaces every occurrence after binder absorption.
    """
    pass


@dataclass(frozen=True)
class App:
    """Pure function application: `f(x, y, z)`.

    `fn` is a string (the function name). Higher-order functions are
    intentionally not supported in v1 — see Unsupported.
    """
    fn: str
    args: tuple["Node", ...]


@dataclass(frozen=True)
class BinOp:
    """Binary operator. `op` is the PyCSL surface form already.

    Allowed `op` values: `+`, `-`, `*`, `//`, `%`, `==`, `!=`, `<`, `>`,
    `<=`, `>=`, `and`, `or`, `==>`, `<==>`.
    """
    op: str
    lhs: "Node"
    rhs: "Node"


@dataclass(frozen=True)
class UnaryOp:
    """Unary operator. Allowed `op` values: `not`, `-`."""
    op: str
    arg: "Node"


@dataclass(frozen=True)
class Forall:
    """Universal quantifier: `\\forall var; body`.

    `ty` records the source-language type (e.g. `"nat"`, `"int"`, `"Nat"`)
    so downstream stages can emit a `>= 0` side condition for naturals.
    """
    var: str
    ty: str
    body: "Node"


@dataclass(frozen=True)
class Exists:
    var: str
    ty: str
    body: "Node"


@dataclass(frozen=True)
class Divides:
    """Divisibility: `d divides n`, i.e. `\\exists k; n == d * k`.

    Kept as a first-class node because the operational/existential/
    guarded encoding decision happens in the translator, not the
    extractor. See pycsl_emit.translator.divides.
    """
    d: "Node"
    n: "Node"


@dataclass(frozen=True)
class Unsupported:
    """A fragment the extractor could not translate.

    Always surfaces as an explicit error in `--strict` mode; otherwise
    embedded in the IR so the bridge can show a structured diff.
    """
    reason: str
    raw: str


Node = Union[
    Var,
    Lit,
    Result,
    App,
    BinOp,
    UnaryOp,
    Forall,
    Exists,
    Divides,
    Unsupported,
]


# ──────────────────────────────────────────────────────────────────────
# Top-level container nodes
# ──────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class Theorem:
    """A theorem statement, post-extraction.

    `binders` are the outer quantifiers in source order. The translator
    decides which prefix to absorb (they must match the target function's
    parameter list in name and order) and which to keep as PyCSL `\\forall`.
    """
    name: str
    binders: tuple[tuple[str, str], ...]   # (var, ty) pairs
    statement: Node


@dataclass(frozen=True)
class FunctionDef:
    """The target function's surface declaration on the proof side.

    Carries just enough context for the translator to know parameter
    names/types and the termination measure when present.
    """
    name: str
    params: tuple[tuple[str, str], ...]    # (var, ty) pairs in declaration order
    return_ty: str
    measure: Node | None = field(default=None)
    # Reserved for future use; not consumed by v1 translator.
    body: Node | None = field(default=None)
