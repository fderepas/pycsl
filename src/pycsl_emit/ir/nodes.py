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


# ──────────────────────────────────────────────────────────────────────
# Lists / arrays / tuples / dicts / strings
# ──────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class Length:
    """`\\length(arr)` — length of a `list` or `array` parameter."""
    arr: "Node"


@dataclass(frozen=True)
class Nth:
    """`arr[i]` — indexed access on a `list`/`array` parameter."""
    arr: "Node"
    i: "Node"


@dataclass(frozen=True)
class Tuple:
    """Tuple literal `(a, b, ...)`."""
    args: tuple["Node", ...]


@dataclass(frozen=True)
class Proj:
    """i-th projection of a tuple. `i` is an int index (0-based)."""
    t: "Node"
    i: int


@dataclass(frozen=True)
class MapGet:
    """Dict lookup: `\\map_get(d, k)`."""
    d: "Node"
    k: "Node"


@dataclass(frozen=True)
class MapSet:
    """Dict insert/update: `\\map_set(d, k, v)`."""
    d: "Node"
    k: "Node"
    v: "Node"


@dataclass(frozen=True)
class MapEmpty:
    """`\\empty_map`."""
    pass


@dataclass(frozen=True)
class HasKey:
    """`\\has_key(d, k)`."""
    d: "Node"
    k: "Node"


@dataclass(frozen=True)
class StrConcat:
    """`a ^ b`."""
    a: "Node"
    b: "Node"


@dataclass(frozen=True)
class StrLength:
    """`\\str_length(s)`."""
    s: "Node"


@dataclass(frozen=True)
class StrSub:
    """`\\str_sub(s, lo, hi)` — substring `[lo, hi)`."""
    s: "Node"
    lo: "Node"
    hi: "Node"


@dataclass(frozen=True)
class StrLit:
    """String literal `"<value>"`."""
    value: str


# ──────────────────────────────────────────────────────────────────────
# Class instances
# ──────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class FieldGet:
    """Object field access: `<obj>.<name>`."""
    obj: "Node"
    name: str


@dataclass(frozen=True)
class ClassInstance:
    """Marker on a Var indicating it is an instance of class `cls`.

    Used as a type tag the translator consults to decide whether to emit
    field-access vs name-lookup. Has no direct surface form.
    """
    cls: str


# ──────────────────────────────────────────────────────────────────────
# Ghost list (PyCSL `ghost_list`)
# ──────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class ListNil:
    """Empty ghost list: `\\nil`."""
    pass


@dataclass(frozen=True)
class ListCons:
    """Prepend to a ghost list: `\\cons(head, tail)`."""
    head: "Node"
    tail: "Node"


@dataclass(frozen=True)
class ListLen:
    """`\\list_length(l)` — distinct from `Length` (which is for `list`
    parameters/arrays). Uses Why3's `list.Length` axioms downstream."""
    l: "Node"


@dataclass(frozen=True)
class ListAppend:
    """`\\append(l1, l2)`."""
    l1: "Node"
    l2: "Node"


@dataclass(frozen=True)
class ListNthAt:
    """`\\nth(l, i)` — head-tracking only; do NOT pair with `\\mem`/`\\hd`
    in invariants (per invariant-writer/SKILL.md)."""
    l: "Node"
    i: "Node"


# ──────────────────────────────────────────────────────────────────────
# Ghost set (PyCSL `ghost_set` — Sets and ghost_set are the same type)
# ──────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class SetEmpty:
    """`\\set_empty`."""
    pass


@dataclass(frozen=True)
class SetAdd:
    """`\\set_add(s, x)`."""
    s: "Node"
    x: "Node"


@dataclass(frozen=True)
class SetRemove:
    """`\\set_remove(s, x)`."""
    s: "Node"
    x: "Node"


@dataclass(frozen=True)
class SetMem:
    """`\\set_mem(x, s)`."""
    x: "Node"
    s: "Node"


@dataclass(frozen=True)
class SetUnion:
    """`\\set_union(a, b)`. AC — canonicalizer flattens + sorts."""
    a: "Node"
    b: "Node"


@dataclass(frozen=True)
class SetInter:
    """`\\set_inter(a, b)`. AC — canonicalizer flattens + sorts."""
    a: "Node"
    b: "Node"


@dataclass(frozen=True)
class SetDiff:
    """`\\set_diff(a, b)`."""
    a: "Node"
    b: "Node"


@dataclass(frozen=True)
class SetSubset:
    """`\\set_subset(a, b)`."""
    a: "Node"
    b: "Node"


@dataclass(frozen=True)
class SetEq:
    """`\\set_eq(a, b)`. Symmetric — canonicalizer normalizes operand order."""
    a: "Node"
    b: "Node"


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
    Length,
    Nth,
    Tuple,
    Proj,
    MapGet,
    MapSet,
    MapEmpty,
    HasKey,
    StrConcat,
    StrLength,
    StrSub,
    StrLit,
    FieldGet,
    ListNil,
    ListCons,
    ListLen,
    ListAppend,
    ListNthAt,
    SetEmpty,
    SetAdd,
    SetRemove,
    SetMem,
    SetUnion,
    SetInter,
    SetDiff,
    SetSubset,
    SetEq,
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
