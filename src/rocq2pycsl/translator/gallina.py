"""Lower Gallina surface AST into pycsl_emit IR + contract structure.

The translator owns the language-specific decisions in
rocq2pycsl-plan.md §5:

  - §5.1 Logical/arithmetic operator mapping (=, /\\, ->, mod, …)
  - §5.3 Binder absorption: outer ∀ binders matching the target
    function's params disappear into PyCSL parameter scope.
  - §5.4 \\result substitution: applications of the function symbol to
    absorbed parameters become `Result()`.
  - §5.5 Variant extraction from `{measure …}`.
  - §5.6 Purity: every non-monadic def emits `assigns \\nothing`.
  - Top-level `/\\` is split into separate ensures clauses (§5.3).
  - `nat`-typed quantifiers in surviving binders carry an implicit
    `requires v >= 0` (open question §10.2; we emit by default).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from pycsl_emit.ir import (
    App,
    BinOp,
    Divides,
    Exists,
    Forall,
    Lit,
    Node as IRNode,
    Result,
    UnaryOp,
    Var,
    Length,
    Nth,
    Tuple as IRTuple,
    Proj,
    MapGet,
    StrConcat,
    StrLength,
    StrSub,
)

from ..extractor.gallina import (
    GApp,
    GBinOp,
    GDivides,
    GExists,
    GForall,
    GFunctionDef,
    GLit,
    GTheorem,
    GUnaryOp,
    GUnsupported,
    GVar,
    GallinaNode,
)


# ──────────────────────────────────────────────────────────────────────
# Output container
# ──────────────────────────────────────────────────────────────────────


@dataclass
class FunctionContract:
    """Contract for a single Python function, ready for the emitter.

    Members map directly to PyCSL `#@` clauses. The translator decides
    which ensures lines to split and whether to emit `requires v >= 0`
    side conditions; the caller hands these to
    `pycsl_emit.translator.render` and then to the annotator.
    """
    requires: list[IRNode] = field(default_factory=list)
    ensures: list[IRNode] = field(default_factory=list)
    assigns: str = "\\nothing"
    variant: IRNode | None = None
    diverges: bool = False

    # Theorems that we recognized but couldn't fully translate. Each
    # entry is a (theorem-name, reason, raw-source) triple. The CLI
    # surfaces these as warnings (or errors with --strict).
    unsupported: list[tuple[str, str, str]] = field(default_factory=list)


# Coq surface operator → PyCSL surface operator (lifted to IR).
_BINOP_MAP: dict[str, str] = {
    # Arithmetic — Coq's `/` is integer division on nat; we map to PyCSL `//`.
    "+": "+",
    "-": "-",
    "*": "*",
    "mod": "%",
    "div": "//",
    # Comparison
    "=": "==",
    "<>": "!=",
    "<": "<",
    ">": ">",
    "<=": "<=",
    ">=": ">=",
    # Logical
    "/\\": "and",
    "\\/": "or",
    "->": "==>",
    "<->": "<==>",
}


# ──────────────────────────────────────────────────────────────────────
# Public entry point
# ──────────────────────────────────────────────────────────────────────


class TranslationError(ValueError):
    """Raised for translation failures that should abort under --strict."""


def translate_function(
    func: GFunctionDef,
    spec_theorems: Iterable[GTheorem],
    *,
    strict: bool = False,
) -> FunctionContract:
    """Build a `FunctionContract` for `func` from the given spec theorems.

    `spec_theorems` is the subset of theorems the user has nominated as
    contracts for `func` (selected upstream — see
    `extractor.selector`).

    With `strict=True`, any `GUnsupported` fragment or any theorem whose
    binders don't absorb cleanly raises `TranslationError`. Without
    strict, those become entries in `contract.unsupported` so the rest
    of the contract can still be emitted.
    """
    contract = FunctionContract()

    # Determine the parameter prefix that will be absorbed: each
    # `∀ <var> : <ty>, …` whose head matches the function's next param
    # name. The remaining binders survive as PyCSL `\\forall` quantifiers
    # in the ensures clause.
    func_param_names = [name for name, _ in func.params]

    for thm in spec_theorems:
        try:
            ensures_nodes = _translate_theorem(thm, func, func_param_names)
        except TranslationError as e:
            if strict:
                raise
            contract.unsupported.append((thm.name, str(e), ""))
            continue
        contract.ensures.extend(ensures_nodes)

    # nat-typed params → requires p >= 0 preconditions.
    # bool-typed params → requires (p == 0) or (p == 1) (0/1 encoding).
    # list/array-typed params → no auto-precondition (the user's theorem
    # carries any explicit `n <= length arr` clauses).
    for name, ty in func.params:
        if ty == "nat":
            contract.requires.append(
                BinOp(">=", Var(name), Lit(0))
            )
        elif ty == "bool":
            contract.requires.append(
                BinOp(
                    "or",
                    BinOp("==", Var(name), Lit(0)),
                    BinOp("==", Var(name), Lit(1)),
                )
            )

    # Variant from {measure …}.
    if func.measure is not None:
        try:
            contract.variant = _lower(func.measure, func, func_param_names)
        except TranslationError as e:
            if strict:
                raise
            contract.unsupported.append(
                ("<measure>", str(e), "")
            )

    return contract


# ──────────────────────────────────────────────────────────────────────
# Theorem translation: binder absorption + statement lowering
# ──────────────────────────────────────────────────────────────────────


def _translate_theorem(
    thm: GTheorem,
    func: GFunctionDef,
    func_param_names: list[str],
) -> list[IRNode]:
    """Translate one theorem to a list of PyCSL ensures-clause IR nodes.

    Binder-absorption rule (rocq2pycsl-plan §5.3):
      - As long as the next outer ∀ binder name *matches the next
        function parameter name in declaration order*, drop it.
      - Stop at the first mismatch; the rest of the binders survive as
        PyCSL `\\forall` in the IR.
    Then walk the statement, replacing every `func.name(absorbed_params…)`
    with `Result()` (§5.4) and splitting a top-level `/\\` into separate
    clauses.
    """
    binders = list(thm.binders)
    absorbed: set[str] = set()
    while binders and len(absorbed) < len(func_param_names):
        next_param = func_param_names[len(absorbed)]
        bname, _bty = binders[0]
        if bname != next_param:
            break
        absorbed.add(bname)
        binders.pop(0)

    # Anything left in `binders` is reflected back into the IR as a
    # surviving quantifier wrapping the body.
    body_node = thm.statement
    body_ir = _lower(body_node, func, func_param_names, absorbed=absorbed)
    for var, ty in reversed(binders):
        body_ir = Forall(var=var, ty=ty, body=body_ir)
        # Surviving `nat` binders get an implicit non-negativity
        # constraint in the body, expressed as an implication.
        if ty == "nat":
            body_ir = _add_nat_guard(body_ir, var)

    return _split_top_conjunction(body_ir)


def _add_nat_guard(node: IRNode, var: str) -> IRNode:
    """Wrap a Forall body with a `v >= 0 ==> body` guard for nat binders."""
    if isinstance(node, Forall):
        return Forall(
            var=node.var,
            ty=node.ty,
            body=BinOp(
                "==>",
                BinOp(">=", Var(var), Lit(0)),
                node.body,
            ),
        )
    return node


def _split_top_conjunction(node: IRNode) -> list[IRNode]:
    """Split top-level `and` chains into a list of clauses.

    Per rocq2pycsl-plan §5.3, a `/\\` at the top of a postcondition is
    cosmetically split into multiple `#@ ensures` lines — finer-grained
    goals are easier for Why3 to discharge.
    """
    if isinstance(node, BinOp) and node.op == "and":
        return _split_top_conjunction(node.lhs) + _split_top_conjunction(node.rhs)
    return [node]


# ──────────────────────────────────────────────────────────────────────
# Expression lowering
# ──────────────────────────────────────────────────────────────────────


def _lower(
    node: GallinaNode,
    func: GFunctionDef,
    func_param_names: list[str],
    *,
    absorbed: set[str] = frozenset(),  # type: ignore[assignment]
) -> IRNode:
    """Recursive GallinaNode → IRNode lowering."""
    if isinstance(node, GVar):
        # `True` / `False` constructors → boolean Lit.
        if node.name == "True":
            return Lit(True)
        if node.name == "False":
            return Lit(False)
        return Var(node.name)
    if isinstance(node, GLit):
        return Lit(node.value)
    if isinstance(node, GApp):
        return _lower_app(node, func, func_param_names, absorbed)
    if isinstance(node, GBinOp):
        py_op = _BINOP_MAP.get(node.op)
        if py_op is None:
            raise TranslationError(f"unknown Gallina operator {node.op!r}")
        return BinOp(
            op=py_op,
            lhs=_lower(node.lhs, func, func_param_names, absorbed=absorbed),
            rhs=_lower(node.rhs, func, func_param_names, absorbed=absorbed),
        )
    if isinstance(node, GUnaryOp):
        if node.op == "~":
            return UnaryOp("not", _lower(node.arg, func, func_param_names, absorbed=absorbed))
        if node.op == "-":
            return UnaryOp("-", _lower(node.arg, func, func_param_names, absorbed=absorbed))
        raise TranslationError(f"unknown unary operator {node.op!r}")
    if isinstance(node, GForall):
        return Forall(
            var=node.var,
            ty=node.ty,
            body=_lower(node.body, func, func_param_names, absorbed=absorbed),
        )
    if isinstance(node, GExists):
        return Exists(
            var=node.var,
            ty=node.ty,
            body=_lower(node.body, func, func_param_names, absorbed=absorbed),
        )
    if isinstance(node, GDivides):
        return Divides(
            d=_lower(node.d, func, func_param_names, absorbed=absorbed),
            n=_lower(node.n, func, func_param_names, absorbed=absorbed),
        )
    if isinstance(node, GUnsupported):
        raise TranslationError(
            f"unsupported Gallina fragment: {node.reason} ({node.raw!r})"
        )
    raise TranslationError(f"unknown Gallina node {type(node).__name__}")


def _lower_app(
    node: GApp,
    func: GFunctionDef,
    func_param_names: list[str],
    absorbed: set[str],
) -> IRNode:
    """Lower a Gallina application, substituting `\\result` where appropriate.

    `func.name applied to the absorbed parameters in declaration order`
    becomes a `Result()` placeholder. Recognized Coq idioms (`length`,
    `nth`, `fst`, `snd`, `andb`, `orb`, `negb`, `String.length`, etc.)
    map to the corresponding IR nodes from Phase 1. Any other application
    becomes a regular IR.App.
    """
    if node.fn == func.name and _matches_absorbed_args(node.args, func_param_names, absorbed):
        return Result()

    # Helper to lower each argument once.
    def lo(a):
        return _lower(a, func, func_param_names, absorbed=absorbed)

    fn = node.fn
    args = node.args

    # ── List / array operations ──────────────────────────────────────
    # Coq's `length l` and `List.length l` and `Datatypes.length l`.
    if fn in ("length", "List.length", "Datatypes.length") and len(args) == 1:
        return Length(arr=lo(args[0]))
    # `nth i l default` — drop the default; PyCSL preconditions enforce bounds.
    if fn in ("nth", "List.nth") and len(args) == 3:
        return Nth(arr=lo(args[1]), i=lo(args[0]))
    # `app l1 l2`, `List.app l1 l2` — list append.
    if fn in ("app", "List.app") and len(args) == 2:
        from pycsl_emit.ir import ListAppend
        return ListAppend(l1=lo(args[0]), l2=lo(args[1]))
    # `cons h t`, `List.cons h t`.
    if fn in ("cons", "List.cons") and len(args) == 2:
        from pycsl_emit.ir import ListCons
        return ListCons(head=lo(args[0]), tail=lo(args[1]))

    # ── Tuple / pair operations ──────────────────────────────────────
    if fn in ("fst", "Datatypes.fst") and len(args) == 1:
        return Proj(t=lo(args[0]), i=0)
    if fn in ("snd", "Datatypes.snd") and len(args) == 1:
        return Proj(t=lo(args[0]), i=1)
    if fn in ("pair", "Datatypes.pair") and len(args) == 2:
        return IRTuple(args=(lo(args[0]), lo(args[1])))

    # ── String operations ────────────────────────────────────────────
    if fn in ("String.length",) and len(args) == 1:
        return StrLength(s=lo(args[0]))
    if fn in ("String.append", "append") and len(args) == 2:
        # `append` is ambiguous (list vs string). String-typed lowering
        # is decided here based on theorem context elsewhere; we default
        # to StrConcat for `String.append`. Bare `append` is treated as
        # list append above; the String.* qualified form lowers here.
        if fn == "String.append":
            return StrConcat(a=lo(args[0]), b=lo(args[1]))
    if fn in ("substring", "String.substring") and len(args) == 3:
        return StrSub(s=lo(args[0]), lo=lo(args[1]), hi=lo(args[2]))

    # ── Boolean operations ───────────────────────────────────────────
    if fn in ("andb", "Bool.andb") and len(args) == 2:
        return BinOp(op="*", lhs=lo(args[0]), rhs=lo(args[1]))
    if fn in ("orb", "Bool.orb") and len(args) == 2:
        # a || b  ≡  a + b - a*b  in the 0/1 encoding.
        a_ir = lo(args[0])
        b_ir = lo(args[1])
        return BinOp(
            op="-",
            lhs=BinOp(op="+", lhs=a_ir, rhs=b_ir),
            rhs=BinOp(op="*", lhs=a_ir, rhs=b_ir),
        )
    if fn in ("negb", "Bool.negb") and len(args) == 1:
        return BinOp(op="-", lhs=Lit(1), rhs=lo(args[0]))
    if fn in ("eqb", "Bool.eqb", "Nat.eqb") and len(args) == 2:
        return BinOp(op="==", lhs=lo(args[0]), rhs=lo(args[1]))
    if fn in ("xorb", "Bool.xorb") and len(args) == 2:
        # a XOR b in 0/1 encoding: a + b - 2*a*b.
        a_ir = lo(args[0])
        b_ir = lo(args[1])
        return BinOp(
            op="-",
            lhs=BinOp(op="+", lhs=a_ir, rhs=b_ir),
            rhs=BinOp(
                op="*",
                lhs=Lit(2),
                rhs=BinOp(op="*", lhs=a_ir, rhs=b_ir),
            ),
        )

    # Fallback: generic application.
    return App(
        fn=fn,
        args=tuple(lo(a) for a in args),
    )


def _matches_absorbed_args(
    args: tuple,
    func_param_names: list[str],
    absorbed: set[str],
) -> bool:
    """True iff `args` is exactly `[Var(p) for p in absorbed-prefix]`."""
    if len(args) != len(absorbed):
        return False
    # The absorbed set is a prefix of func_param_names; respect that order.
    expected_prefix = func_param_names[: len(absorbed)]
    for arg, expected in zip(args, expected_prefix):
        if not isinstance(arg, GVar) or arg.name != expected:
            return False
        if expected not in absorbed:
            return False
    return True
