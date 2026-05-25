"""Surface AST for the supported Gallina subset.

This is the interchange layer between the two extractor backends (Lark
and SerAPI) and the `translator.gallina` walker that lowers everything
to `pycsl_emit.ir`.

Design notes:

- The AST mirrors the surface syntax of Gallina, *not* the elaborated
  Coq kernel term. We carry only what the v1 supported subset needs.
- Binders record the source-side type as a raw string (`"nat"`, `"Z"`,
  `"int"`, etc.). The translator decides whether `nat` warrants an
  automatic `requires v >= 0` clause.
- `GUnsupported` is the explicit "I saw this and couldn't translate"
  marker so `--strict` mode can fail loudly while the default mode can
  still emit a partial annotation set with an unsupported diff.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Union


# ──────────────────────────────────────────────────────────────────────
# Expression nodes
# ──────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class GVar:
    """A bare identifier — variable, function symbol, or constructor.

    The translator decides on context whether this is a variable that
    should map to the IR Var, or a constructor like `True`/`False`.
    """
    name: str


@dataclass(frozen=True)
class GLit:
    """Numeric or boolean literal.

    Coq's `0`, `1`, `42` parse to int. `True` and `False` are *not*
    literals at the Gallina level; they appear as `GVar("True")` /
    `GVar("False")` and the translator promotes them to `IR.Lit(bool)`.
    Keeping them out of GLit avoids ambiguity in the parser.
    """
    value: int


@dataclass(frozen=True)
class GApp:
    """Function application: `f x y z`.

    Gallina applies left-associatively. We normalize to (head, args)
    form during parsing.
    """
    fn: str
    args: tuple["GallinaNode", ...]


@dataclass(frozen=True)
class GBinOp:
    """A binary operator at the Gallina surface.

    `op` carries the surface token: `"+"`, `"-"`, `"*"`, `"="`, `"<>"`,
    `"<="`, `"<"`, `">="`, `">"`, `"/\\"`, `"\\/"`, `"->"`, `"<->"`,
    `"mod"`, `"div"`.

    The translator maps these to PyCSL surface operators (`=` → `==`,
    `<>` → `!=`, `/\\` → `and`, `->` → `==>`, etc.).
    """
    op: str
    lhs: "GallinaNode"
    rhs: "GallinaNode"


@dataclass(frozen=True)
class GUnaryOp:
    """A unary operator. `op` is `"~"` (negation) or `"-"` (numeric)."""
    op: str
    arg: "GallinaNode"


@dataclass(frozen=True)
class GForall:
    """`forall v : T, body`.

    Multi-binder Gallina (`forall a b : nat, P`) is normalized to a
    nested `GForall` chain at parse time, so each node carries exactly
    one variable.
    """
    var: str
    ty: str
    body: "GallinaNode"


@dataclass(frozen=True)
class GExists:
    """`exists v : T, body`."""
    var: str
    ty: str
    body: "GallinaNode"


@dataclass(frozen=True)
class GDivides:
    """Coq's `(d | n)` divisibility notation in `Nat`.

    Kept as a first-class node because the operational/existential/
    guarded encoding decision lives in `pycsl_emit.translator.divides`,
    not in the extractor.
    """
    d: "GallinaNode"
    n: "GallinaNode"


@dataclass(frozen=True)
class GUnsupported:
    """An expression the backend recognized but cannot translate.

    Always carries a useful reason for `--strict` error reports.
    """
    reason: str
    raw: str


GallinaNode = Union[
    GVar,
    GLit,
    GApp,
    GBinOp,
    GUnaryOp,
    GForall,
    GExists,
    GDivides,
    GUnsupported,
]


# ──────────────────────────────────────────────────────────────────────
# Top-level container nodes
# ──────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class GTheorem:
    """A `Theorem`/`Lemma`/`Proposition` vernac.

    `binders` is the outer quantifier sequence (in source order). The
    statement is what comes after the binders' colon-comma. Proofs are
    NOT extracted — we treat the theorem as a trusted oracle.
    """
    name: str
    binders: tuple[tuple[str, str], ...]   # (var, ty)
    statement: GallinaNode
    source_line: int = 0


@dataclass(frozen=True)
class GFunctionDef:
    """A `Definition`/`Fixpoint`/`Function` vernac.

    `params` are the explicit arguments (in declaration order).
    `measure` is the inner `<expr>` from `{measure <expr> <var>}` when
    present, otherwise None — the translator emits `#@ \\variant` only
    when this is set or the function is recursive (caller decides).
    `body` is intentionally absent in v1; we don't transport proofs or
    function definitions.
    """
    name: str
    params: tuple[tuple[str, str], ...]
    return_ty: str
    measure: GallinaNode | None = field(default=None)
    is_recursive: bool = False
    source_line: int = 0


@dataclass(frozen=True)
class GallinaModule:
    """Everything an extractor found in a single `.v` file.

    `theorems` and `functions` preserve source order so downstream
    diagnostics can cite line numbers.
    """
    theorems: tuple[GTheorem, ...]
    functions: tuple[GFunctionDef, ...]
    source_path: str = ""

    def function(self, name: str) -> GFunctionDef | None:
        for f in self.functions:
            if f.name == name:
                return f
        return None

    def theorem(self, name: str) -> GTheorem | None:
        for t in self.theorems:
            if t.name == name:
                return t
        return None
