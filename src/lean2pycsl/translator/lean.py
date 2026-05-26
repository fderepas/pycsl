"""Lower Lean surface AST into pycsl_emit IR + contract structure.

The translator owns the Lean-specific decisions in
lean2pycsl-plan.md §5:

  - §5.1 Operator mapping (= → ==, ∧ → and, ∣ → IR.Divides, etc.).
  - §5.3 Binder absorption + strip implicit/instance-implicit binders
    BEFORE matching against the function's explicit parameter list.
  - §5.4 \\result substitution.
  - §5.5 Variant extraction from `termination_by ... => <expr>`.
  - §5.5 `partial def` → `#@ \\diverges` instead of variant.
  - §5.6 Purity: every non-partial def emits `#@ assigns \\nothing`.
  - §5.7 Type-class-quantified theorems are rejected (no path from
    `Decidable Bool` etc. to PyCSL).
  - Top-level `/\\` split into separate ensures (plan §7 worked example).
  - `Nat` quantifiers carry an implicit `requires v >= 0` (plan §7
    worked example output emits this).
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
    FieldGet,
)

from ..extractor.lean_ast import (
    Binder,
    BinderShape,
    LApp,
    LBinOp,
    LDvd,
    LeanDef,
    LExists,
    LForall,
    LLit,
    LTheorem,
    LUnaryOp,
    LUnsupported,
    LVar,
    LeanNode,
)


# ──────────────────────────────────────────────────────────────────────
# Output container
# ──────────────────────────────────────────────────────────────────────


@dataclass
class FunctionContract:
    """Contract for one Python function, ready for the emitter."""
    requires: list[IRNode] = field(default_factory=list)
    ensures: list[IRNode] = field(default_factory=list)
    assigns: str = "\\nothing"
    variant: IRNode | None = None
    diverges: bool = False

    # Theorems we recognized but couldn't fully translate. Surfaced by
    # the CLI as warnings (or errors under --strict).
    unsupported: list[tuple[str, str, str]] = field(default_factory=list)


# Lean surface operator → PyCSL surface operator (lifted to IR).
_BINOP_MAP: dict[str, str] = {
    # Arithmetic
    "+": "+",
    "-": "-",
    "*": "*",
    "/": "//",
    "%": "%",
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


# `Nat` quantifiers get an automatic `>= 0` constraint, like Coq's
# `nat`. `Int`, `Bool`, and anything else don't.
_NONNEG_TYPES = frozenset({"Nat"})


# Types we treat as "concrete first-order" — anything else triggers
# the §5.7 "type-class quantification" rejection.
_SUPPORTED_TYPES = frozenset({
    "Nat", "Int", "Bool", "Prop", "Z",   # Z is a Lean alias users sometimes write
    "String",                             # Lean's native String type
    "_",                                  # unknown from bare binders — let it through
})

# Polymorphic type constructors we recognize as supported (their argument
# can be any supported type — we don't recursively check it in v1).
_POLYMORPHIC_HEADS = frozenset({"List", "Array", "Option"})


class TranslationError(ValueError):
    """Raised for translation failures that should abort under --strict."""


# ──────────────────────────────────────────────────────────────────────
# Public entry point
# ──────────────────────────────────────────────────────────────────────


def translate_function(
    func: LeanDef,
    spec_theorems: Iterable[LTheorem],
    *,
    strict: bool = False,
) -> FunctionContract:
    """Build a `FunctionContract` for `func` from the given spec theorems.

    Mirrors `rocq2pycsl.translator.translate_function` so the contracts
    produced by the two pipelines have the same shape — that's the
    foundation the bridge will stand on.
    """
    contract = FunctionContract()

    # We only absorb against the *explicit* parameters; implicit and
    # instance-implicit binders never appear in the Python signature.
    explicit_params = [
        (b.name, b.ty) for b in func.params if b.shape is BinderShape.EXPLICIT
    ]
    func_param_names = [name for name, _ in explicit_params]

    for thm in spec_theorems:
        try:
            ensures_nodes = _translate_theorem(thm, func, func_param_names)
        except TranslationError as e:
            if strict:
                raise
            contract.unsupported.append((thm.name, str(e), ""))
            continue
        contract.ensures.extend(ensures_nodes)

    # Nat-typed explicit params → requires p >= 0.
    # Bool-typed explicit params → requires (p == 0) or (p == 1).
    for name, ty in explicit_params:
        if ty in _NONNEG_TYPES:
            contract.requires.append(BinOp(">=", Var(name), Lit(0)))
        elif ty == "Bool":
            contract.requires.append(
                BinOp(
                    "or",
                    BinOp("==", Var(name), Lit(0)),
                    BinOp("==", Var(name), Lit(1)),
                )
            )

    if func.is_partial:
        contract.diverges = True
    elif func.measure is not None:
        try:
            contract.variant = _lower(func.measure, func, func_param_names)
        except TranslationError as e:
            if strict:
                raise
            contract.unsupported.append(("<termination_by>", str(e), ""))

    return contract


# ──────────────────────────────────────────────────────────────────────
# Theorem translation
# ──────────────────────────────────────────────────────────────────────


def _translate_theorem(
    thm: LTheorem,
    func: LeanDef,
    func_param_names: list[str],
) -> list[IRNode]:
    """Translate one theorem to a list of PyCSL ensures-clause IR nodes.

    Lean-specific binder-prep (plan §5.3): instance-implicit binders are
    *always* stripped; implicit binders are stripped because they're not
    user-visible in the Python signature; explicit binders are
    candidates for absorption.

    Type-class quantification (plan §5.7): if any *explicit* binder has
    a type outside the supported set, raise — there's no path from
    `Decidable Bool` etc. to a PyCSL contract.
    """
    explicit_binders = [b for b in thm.binders if b.shape is BinderShape.EXPLICIT]
    for b in explicit_binders:
        if _looks_like_type_class(b.ty):
            raise TranslationError(
                f"theorem quantified over type class {b.ty!r} — not supported "
                f"(see lean2pycsl-plan §5.7; specialize to a concrete type)"
            )

    # Absorb the longest matching prefix of explicit binders.
    absorbed: set[str] = set()
    survivors: list[Binder] = []
    iter_explicit = iter(explicit_binders)
    for next_param_name in func_param_names:
        b = next(iter_explicit, None)
        if b is None or b.name != next_param_name:
            if b is not None:
                survivors.append(b)
            break
        absorbed.add(b.name)
    # Pull in any binders after the iterator was paused.
    for b in iter_explicit:
        survivors.append(b)

    body_ir = _lower(thm.statement, func, func_param_names, absorbed=absorbed)
    for b in reversed(survivors):
        body_ir = Forall(var=b.name, ty=b.ty, body=body_ir)
        if b.ty in _NONNEG_TYPES:
            body_ir = _add_nat_guard(body_ir, b.name)

    return _split_top_conjunction(body_ir)


def _add_nat_guard(node: IRNode, var: str) -> IRNode:
    """Wrap a Forall body with `v >= 0 ==> body` for Nat binders."""
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
    """Split top-level `and` into separate clauses (one per ensures)."""
    if isinstance(node, BinOp) and node.op == "and":
        return _split_top_conjunction(node.lhs) + _split_top_conjunction(node.rhs)
    return [node]


def _looks_like_type_class(ty: str) -> bool:
    """Heuristic: anything with uppercase-letter head that isn't in
    the supported list is treated as a type-class quantification.

    Accepts polymorphic types (`List Nat`, `Array Nat`, `Option Nat`),
    arrow types (`Nat -> Bool`, `Nat -> Option Nat`), and product types
    (`Nat * Nat`) — these are all needed for the corpus' compound data
    types and aren't real type classes.
    """
    ty = ty.strip()
    if ty in _SUPPORTED_TYPES:
        return False
    if not ty:
        return False
    # Arrow and product types: split on the top-level operator and
    # accept if both sides are themselves supported.
    if "->" in ty:
        # Conservative: any arrow type is allowed (Lean would have
        # caught a real type-class error upstream during elaboration).
        return False
    if " * " in ty:
        return False
    # Polymorphic-constructor application: `List Nat`, `Array Nat`,
    # `Option Nat`, `Vector Nat 3`, etc.
    head = ty.split()[0]
    if head in _POLYMORPHIC_HEADS:
        return False
    # If the type *starts* with an uppercase letter and isn't on the
    # whitelist, assume it's a type class / structure / inductive.
    return head[0].isupper()


# ──────────────────────────────────────────────────────────────────────
# Expression lowering
# ──────────────────────────────────────────────────────────────────────


def _lower(
    node: LeanNode,
    func: LeanDef,
    func_param_names: list[str],
    *,
    absorbed: set[str] = frozenset(),  # type: ignore[assignment]
) -> IRNode:
    if isinstance(node, LVar):
        if node.name == "True":
            return Lit(True)
        if node.name == "False":
            return Lit(False)
        # Lean dot syntax: `t.fst`, `t.snd`, `l.length`, `r.field_name`.
        # The parser emits these as qident LVars; recognize and lower.
        if "." in node.name:
            base, _, suffix = node.name.rpartition(".")
            # Don't intercept fully-qualified names like `List.nil` —
            # those are not field access. We use a simple heuristic:
            # the base must be a bare identifier (no dots) AND start
            # with a lowercase letter (likely a variable, not a module).
            if base and "." not in base and base[0].islower():
                if suffix == "length":
                    return Length(arr=Var(base))
                if suffix == "fst":
                    return Proj(t=Var(base), i=0)
                if suffix == "snd":
                    return Proj(t=Var(base), i=1)
                # Generic field access (works for class instances).
                return FieldGet(obj=Var(base), name=suffix)
        return Var(node.name)
    if isinstance(node, LLit):
        return Lit(node.value)
    if isinstance(node, LApp):
        return _lower_app(node, func, func_param_names, absorbed)
    if isinstance(node, LBinOp):
        py_op = _BINOP_MAP.get(node.op)
        if py_op is None:
            raise TranslationError(f"unknown Lean operator {node.op!r}")
        return BinOp(
            op=py_op,
            lhs=_lower(node.lhs, func, func_param_names, absorbed=absorbed),
            rhs=_lower(node.rhs, func, func_param_names, absorbed=absorbed),
        )
    if isinstance(node, LUnaryOp):
        if node.op == "~":
            return UnaryOp("not", _lower(node.arg, func, func_param_names, absorbed=absorbed))
        if node.op == "-":
            return UnaryOp("-", _lower(node.arg, func, func_param_names, absorbed=absorbed))
        raise TranslationError(f"unknown unary operator {node.op!r}")
    if isinstance(node, LForall):
        return Forall(
            var=node.var,
            ty=node.ty,
            body=_lower(node.body, func, func_param_names, absorbed=absorbed),
        )
    if isinstance(node, LExists):
        return Exists(
            var=node.var,
            ty=node.ty,
            body=_lower(node.body, func, func_param_names, absorbed=absorbed),
        )
    if isinstance(node, LDvd):
        # Lean: `a ∣ b` = "a divides b".
        # IR:   `Divides(d, n)` with d = divisor, n = dividend.
        return Divides(
            d=_lower(node.a, func, func_param_names, absorbed=absorbed),
            n=_lower(node.b, func, func_param_names, absorbed=absorbed),
        )
    if isinstance(node, LUnsupported):
        raise TranslationError(
            f"unsupported Lean fragment: {node.reason} ({node.raw!r})"
        )
    raise TranslationError(f"unknown Lean node {type(node).__name__}")


def _lower_app(
    node: LApp,
    func: LeanDef,
    func_param_names: list[str],
    absorbed: set[str],
) -> IRNode:
    """Lower a Lean application, substituting `\\result` where appropriate.

    `func.name applied to absorbed params in declaration order` becomes
    a `Result()` placeholder. Recognized Lean operators map to the IR
    nodes from Phase 1. Anything else becomes a generic IR.App.
    """
    if node.fn == func.name and _matches_absorbed_args(node.args, func_param_names, absorbed):
        return Result()

    def lo(a):
        return _lower(a, func, func_param_names, absorbed=absorbed)

    fn = node.fn
    args = node.args

    # ── List / array operations ──────────────────────────────────────
    if fn in ("List.length", "Array.size") and len(args) == 1:
        return Length(arr=lo(args[0]))
    # `List.nth l i` or `Array.get arr i` — Lean signature.
    if fn in ("List.nth", "List.get", "Array.get") and len(args) == 2:
        return Nth(arr=lo(args[0]), i=lo(args[1]))
    # Lean's `l.get! i` style → after dot-syntax lowering this arrives
    # as `LApp("l.get", (i,))` — we recognize by checking the fn suffix.
    if "." in fn and len(args) == 1:
        base, _, suffix = fn.rpartition(".")
        if suffix in ("get", "get!", "getD") and base and base[0].islower():
            return Nth(arr=Var(base), i=lo(args[0]))
    if fn in ("List.append", "Array.append") and len(args) == 2:
        from pycsl_emit.ir import ListAppend
        return ListAppend(l1=lo(args[0]), l2=lo(args[1]))
    if fn in ("List.cons",) and len(args) == 2:
        from pycsl_emit.ir import ListCons
        return ListCons(head=lo(args[0]), tail=lo(args[1]))

    # ── Tuple / pair operations ──────────────────────────────────────
    if fn in ("Prod.fst", "Prod.mk.fst") and len(args) == 1:
        return Proj(t=lo(args[0]), i=0)
    if fn in ("Prod.snd",) and len(args) == 1:
        return Proj(t=lo(args[0]), i=1)
    if fn in ("Prod.mk",) and len(args) == 2:
        return IRTuple(args=(lo(args[0]), lo(args[1])))

    # ── String operations ────────────────────────────────────────────
    if fn in ("String.length",) and len(args) == 1:
        return StrLength(s=lo(args[0]))
    if fn in ("String.append",) and len(args) == 2:
        return StrConcat(a=lo(args[0]), b=lo(args[1]))
    if fn in ("String.extract",) and len(args) == 3:
        return StrSub(s=lo(args[0]), lo=lo(args[1]), hi=lo(args[2]))

    # ── Boolean operations ───────────────────────────────────────────
    # Lean's Bool operators in the 0/1 encoding.
    if fn in ("Bool.and", "and") and len(args) == 2:
        return BinOp(op="*", lhs=lo(args[0]), rhs=lo(args[1]))
    if fn in ("Bool.or", "or") and len(args) == 2:
        a_ir = lo(args[0])
        b_ir = lo(args[1])
        return BinOp(
            op="-",
            lhs=BinOp(op="+", lhs=a_ir, rhs=b_ir),
            rhs=BinOp(op="*", lhs=a_ir, rhs=b_ir),
        )
    if fn in ("Bool.not", "not") and len(args) == 1:
        return BinOp(op="-", lhs=Lit(1), rhs=lo(args[0]))
    if fn in ("Bool.xor", "Bool.bne") and len(args) == 2:
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
    if len(args) != len(absorbed):
        return False
    expected_prefix = func_param_names[: len(absorbed)]
    for arg, expected in zip(args, expected_prefix):
        if not isinstance(arg, LVar) or arg.name != expected:
            return False
        if expected not in absorbed:
            return False
    return True
