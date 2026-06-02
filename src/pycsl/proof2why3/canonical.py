"""IR canonicalization (proof2why3 Phase 3b — sticky-01.md).

Takes a Term tree from `parser.parse_type_expr` and applies a confluent
sequence of structural transformations until a fixed point. The
output is a hashable representative — two semantically-equivalent
inputs canonicalize to structurally equal Terms.

Transformations (mirror sticky-01.md §3 / cross-validated-spec-sources
§6):

1. **nat/Nat → int with side conditions.**
   `forall x : nat, P(x)` becomes
   `forall x : int, x >= 0 -> P(x)`.
   Applied recursively under nested quantifiers.

2. **Alpha-rename** bound variables in each quantifier to v0, v1, ….

3. **Comparison-direction normalization.**
   `a <= b` rewrites to `b >= a`, `a < b` to `b > a`.

4. **Redundant hypothesis absorption.**
   Two duplicate hypotheses in an arrow chain collapse to one.
   `H -> H -> C` → `H -> C`.
   `H1 >= 0 -> H1 > 0 -> C` keeps both because they aren't equal;
   the v0 string normalizer absorbed these but at the IR level we
   keep them (the registry should match exactly).

5. **AC-flatten** disjunction / conjunction chains to sorted n-ary
   form via a stable sort by `pp()`.

6. **Sort top-level arrow hypothesis list** (independent hypotheses
   are commutative w.r.t. the conclusion).

The fixpoint iteration terminates because each transformation is
monotone w.r.t. a total well-founded order on Terms.
"""
from __future__ import annotations

from typing import Dict, List, Tuple

from proof2why3.ir import (
    App, BinOp, BoolLit, Exists, Forall, IntLit, Term, UnaryOp, Unsupported,
    Var, flatten_arrow_chain, mk_arrow_chain,
)


# ---------------------------------------------------------------------------
# Substitution
# ---------------------------------------------------------------------------


def substitute(t: Term, mapping: Dict[str, str]) -> Term:
    """Rename free variable names in `t` according to `mapping`.
    Capture-avoiding: bound binders that shadow a mapped name keep
    their original (we don't push the rename through)."""
    if isinstance(t, Var):
        return Var(mapping.get(t.name, t.name))
    if isinstance(t, (IntLit, BoolLit, Unsupported)):
        return t
    if isinstance(t, App):
        return App(
            head=mapping.get(t.head, t.head),
            args=tuple(substitute(a, mapping) for a in t.args),
        )
    if isinstance(t, BinOp):
        return BinOp(t.op, substitute(t.lhs, mapping), substitute(t.rhs, mapping))
    if isinstance(t, UnaryOp):
        return UnaryOp(t.op, substitute(t.arg, mapping))
    if isinstance(t, (Forall, Exists)):
        # Restrict mapping: bound binders shadow it.
        inner_map = {k: v for k, v in mapping.items() if k not in t.binders}
        kind = Forall if isinstance(t, Forall) else Exists
        return kind(binders=t.binders, ty=t.ty,
                    body=substitute(t.body, inner_map))
    raise TypeError(f"substitute: unknown {type(t)}")


# ---------------------------------------------------------------------------
# Step 1 — nat → int with side conditions
# ---------------------------------------------------------------------------


_NAT_TYPES = {"nat", "Nat"}


def _expand_nat_to_int(t: Term) -> Term:
    """Recursively rewrite each `forall vs : nat, body` to
    `forall vs : int, v >= 0 -> v >= 0 -> ... -> body`."""
    if isinstance(t, Forall):
        new_body = _expand_nat_to_int(t.body)
        if t.ty in _NAT_TYPES:
            side: List[Term] = [
                BinOp(">=", Var(b), IntLit(0)) for b in t.binders
            ]
            conclusion_with_side = mk_arrow_chain(side, new_body)
            return Forall(binders=t.binders, ty="int",
                          body=conclusion_with_side)
        return Forall(binders=t.binders, ty=t.ty, body=new_body)
    if isinstance(t, Exists):
        new_body = _expand_nat_to_int(t.body)
        if t.ty in _NAT_TYPES:
            return Exists(binders=t.binders, ty="int", body=new_body)
        return Exists(binders=t.binders, ty=t.ty, body=new_body)
    if isinstance(t, App):
        return App(head=t.head, args=tuple(_expand_nat_to_int(a) for a in t.args))
    if isinstance(t, BinOp):
        return BinOp(t.op, _expand_nat_to_int(t.lhs), _expand_nat_to_int(t.rhs))
    if isinstance(t, UnaryOp):
        return UnaryOp(t.op, _expand_nat_to_int(t.arg))
    return t


# ---------------------------------------------------------------------------
# Step 2 — alpha rename to v0, v1, ...
# ---------------------------------------------------------------------------


def _alpha_rename(t: Term, counter: List[int]) -> Term:
    """Recursive alpha-rename. `counter` is a mutable single-element
    list serving as a fresh-name counter, shared across the traversal."""
    if isinstance(t, (Var, IntLit, BoolLit, Unsupported)):
        return t
    if isinstance(t, App):
        return App(head=t.head,
                   args=tuple(_alpha_rename(a, counter) for a in t.args))
    if isinstance(t, BinOp):
        return BinOp(t.op,
                     _alpha_rename(t.lhs, counter),
                     _alpha_rename(t.rhs, counter))
    if isinstance(t, UnaryOp):
        return UnaryOp(t.op, _alpha_rename(t.arg, counter))
    if isinstance(t, (Forall, Exists)):
        # Assign fresh names to this binder group.
        new_names = []
        mapping: Dict[str, str] = {}
        for old in t.binders:
            new = f"v{counter[0]}"
            counter[0] += 1
            new_names.append(new)
            mapping[old] = new
        renamed_body = substitute(t.body, mapping)
        renamed_body = _alpha_rename(renamed_body, counter)
        kind = Forall if isinstance(t, Forall) else Exists
        return kind(binders=tuple(new_names), ty=t.ty, body=renamed_body)
    raise TypeError(f"_alpha_rename: unknown {type(t)}")


def alpha_normalize(t: Term) -> Term:
    """Alpha-rename all bound variables to v0, v1, … left-to-right.
    Top-level entry that initializes the counter."""
    counter = [0]
    return _alpha_rename(t, counter)


# ---------------------------------------------------------------------------
# Step 3 — comparison direction normalization
# ---------------------------------------------------------------------------


_FLIP_COMPARISON = {
    "<=": ">=",
    "<":  ">",
}


def _flip_comparisons(t: Term) -> Term:
    """Rewrite `a <= b` → `b >= a` and `a < b` → `b > a` recursively."""
    if isinstance(t, (Var, IntLit, BoolLit, Unsupported)):
        return t
    if isinstance(t, App):
        return App(head=t.head,
                   args=tuple(_flip_comparisons(a) for a in t.args))
    if isinstance(t, BinOp):
        if t.op in _FLIP_COMPARISON:
            return BinOp(
                _FLIP_COMPARISON[t.op],
                _flip_comparisons(t.rhs),
                _flip_comparisons(t.lhs),
            )
        return BinOp(t.op, _flip_comparisons(t.lhs), _flip_comparisons(t.rhs))
    if isinstance(t, UnaryOp):
        return UnaryOp(t.op, _flip_comparisons(t.arg))
    if isinstance(t, (Forall, Exists)):
        kind = Forall if isinstance(t, Forall) else Exists
        return kind(binders=t.binders, ty=t.ty, body=_flip_comparisons(t.body))
    raise TypeError(f"_flip_comparisons: unknown {type(t)}")


# ---------------------------------------------------------------------------
# Step 4 — redundant hypothesis dedup in arrow chains
# ---------------------------------------------------------------------------


def _dedup_arrow_chain(t: Term) -> Term:
    """Walk into Foralls/etc., and at each arrow chain remove
    duplicate hypotheses preserving first occurrence order."""
    if isinstance(t, BinOp) and t.op == "->":
        hyps, conclusion = flatten_arrow_chain(t)
        seen: List[Term] = []
        for h in hyps:
            recursed = _dedup_arrow_chain(h)
            if recursed not in seen:
                seen.append(recursed)
        return mk_arrow_chain(seen, _dedup_arrow_chain(conclusion))
    if isinstance(t, (Var, IntLit, BoolLit, Unsupported)):
        return t
    if isinstance(t, App):
        return App(head=t.head,
                   args=tuple(_dedup_arrow_chain(a) for a in t.args))
    if isinstance(t, BinOp):
        return BinOp(t.op, _dedup_arrow_chain(t.lhs), _dedup_arrow_chain(t.rhs))
    if isinstance(t, UnaryOp):
        return UnaryOp(t.op, _dedup_arrow_chain(t.arg))
    if isinstance(t, (Forall, Exists)):
        kind = Forall if isinstance(t, Forall) else Exists
        return kind(binders=t.binders, ty=t.ty, body=_dedup_arrow_chain(t.body))
    raise TypeError(f"_dedup_arrow_chain: unknown {type(t)}")


# ---------------------------------------------------------------------------
# Step 5 — AC-flatten disjunction / conjunction chains, sort
# ---------------------------------------------------------------------------


def _ac_normalize(t: Term) -> Term:
    """Sort commutative `\\/` and `/\\` operands."""
    if isinstance(t, BinOp) and t.op in (r"\/", r"/\\"):
        # Collect all conjuncts/disjuncts at this level.
        operands: List[Term] = []

        def collect(node: Term) -> None:
            if isinstance(node, BinOp) and node.op == t.op:
                collect(node.lhs)
                collect(node.rhs)
            else:
                operands.append(_ac_normalize(node))

        collect(t)
        operands_sorted = sorted(operands, key=lambda x: x.pp())
        # Re-fold as right-leaning chain so structural equality holds.
        out = operands_sorted[-1]
        for o in reversed(operands_sorted[:-1]):
            out = BinOp(t.op, o, out)
        return out
    if isinstance(t, (Var, IntLit, BoolLit, Unsupported)):
        return t
    if isinstance(t, App):
        return App(head=t.head, args=tuple(_ac_normalize(a) for a in t.args))
    if isinstance(t, BinOp):
        return BinOp(t.op, _ac_normalize(t.lhs), _ac_normalize(t.rhs))
    if isinstance(t, UnaryOp):
        return UnaryOp(t.op, _ac_normalize(t.arg))
    if isinstance(t, (Forall, Exists)):
        kind = Forall if isinstance(t, Forall) else Exists
        return kind(binders=t.binders, ty=t.ty, body=_ac_normalize(t.body))
    raise TypeError(f"_ac_normalize: unknown {type(t)}")


# ---------------------------------------------------------------------------
# Step 6 — sort top-level arrow hypotheses (commutative)
# ---------------------------------------------------------------------------


def _sort_arrow_hypotheses(t: Term) -> Term:
    """Sort the hypothesis list of each arrow chain stably.

    Independent hypotheses (e.g., `a >= 0`, `b >= 0`, `a > 0 \\/ b > 0`)
    are commutative w.r.t. the conclusion — sorting makes the
    canonical form independent of source-syntactic ordering."""
    if isinstance(t, BinOp) and t.op == "->":
        hyps, conclusion = flatten_arrow_chain(t)
        hyps_normalized = [_sort_arrow_hypotheses(h) for h in hyps]
        conclusion_normalized = _sort_arrow_hypotheses(conclusion)
        # NOTE: we DON'T sort here because sorting changes the meaning
        # of dependent hypotheses (e.g., `b > 0 -> mod a b = 0` —
        # the order matters if `mod a b` requires `b != 0`).
        # For first-order Hoare contracts the order is usually
        # independent, but we'd need a dependency analysis to confirm.
        # Keep source order for v1.
        return mk_arrow_chain(hyps_normalized, conclusion_normalized)
    if isinstance(t, (Var, IntLit, BoolLit, Unsupported)):
        return t
    if isinstance(t, App):
        return App(head=t.head,
                   args=tuple(_sort_arrow_hypotheses(a) for a in t.args))
    if isinstance(t, BinOp):
        return BinOp(t.op, _sort_arrow_hypotheses(t.lhs),
                     _sort_arrow_hypotheses(t.rhs))
    if isinstance(t, UnaryOp):
        return UnaryOp(t.op, _sort_arrow_hypotheses(t.arg))
    if isinstance(t, (Forall, Exists)):
        kind = Forall if isinstance(t, Forall) else Exists
        return kind(binders=t.binders, ty=t.ty,
                    body=_sort_arrow_hypotheses(t.body))
    raise TypeError(f"_sort_arrow_hypotheses: unknown {type(t)}")


# ---------------------------------------------------------------------------
# Public entry — canonicalize
# ---------------------------------------------------------------------------


def _flatten_foralls(t: Term) -> Term:
    """Collapse nested `forall x : T, forall y : T, body` (same type)
    into `forall x y : T, body`.

    Lean's `forallE` is unary; Coq's `Prod` is also unary but the
    pretty-printer flattens chains. The IR's `Forall(binders=tuple,
    ty, body)` IS the flattened form. This pass folds adjacent
    same-type Foralls so both extraction backends produce the same
    shape post-canonicalization.

    The pass is correct when the inner body has no arrow hypothesis
    between the binders (a hypothesis between binders is a real
    dependency on the first binder and breaks the flattening). We
    DO flatten across `arrow -> Forall` boundaries because the
    outer forall introduces the binder before the hypothesis can
    reference it — but if the hypothesis between binders mentions
    later binders, that's a Pi-type and should not be flattened.

    For the gcd-family this is safe: hypotheses are flat and
    independent.
    """
    if isinstance(t, Forall):
        new_body = _flatten_foralls(t.body)
        # Walk through any leading arrow chain hyps, gathering them
        # alongside subsequent Foralls of the same type.
        binders = list(t.binders)
        cur = new_body
        gathered_hyps: List[Term] = []
        while True:
            if isinstance(cur, Forall) and cur.ty == t.ty:
                # Fold this binder in.
                binders.extend(cur.binders)
                cur = cur.body
                continue
            if isinstance(cur, BinOp) and cur.op == "->":
                # Look ahead: is there another same-type Forall later?
                # If yes, gather this hypothesis; the binder dependency
                # is independent (gcd-family assumption).
                inner = cur.rhs
                while isinstance(inner, BinOp) and inner.op == "->":
                    inner = inner.rhs
                if isinstance(inner, Forall) and inner.ty == t.ty:
                    # The hypotheses bind to v0; they stay where they
                    # are. Continue scanning past them.
                    gathered_hyps.append(cur.lhs)
                    cur = cur.rhs
                    continue
            break
        # Re-emit: forall binders : ty, hyps -> ... -> remaining body.
        body_out = cur
        if gathered_hyps:
            body_out = mk_arrow_chain(gathered_hyps, cur)
        return Forall(binders=tuple(binders), ty=t.ty, body=body_out)
    if isinstance(t, Exists):
        return Exists(binders=t.binders, ty=t.ty,
                      body=_flatten_foralls(t.body))
    if isinstance(t, (Var, IntLit, BoolLit, Unsupported)):
        return t
    if isinstance(t, App):
        return App(head=t.head,
                   args=tuple(_flatten_foralls(a) for a in t.args))
    if isinstance(t, BinOp):
        return BinOp(t.op, _flatten_foralls(t.lhs), _flatten_foralls(t.rhs))
    if isinstance(t, UnaryOp):
        return UnaryOp(t.op, _flatten_foralls(t.arg))
    raise TypeError(f"_flatten_foralls: unknown {type(t)}")


def _camel_to_snake(name: str) -> str:
    """Convert camelCase / PascalCase identifier to snake_case.

    Used for cross-prover name normalization: Lean's `wpGenCorrect`
    canonicalizes to the same `wp_gen_correct` as Rocq's snake_case.
    """
    import re as _re
    # Insert underscore before any uppercase letter that follows a
    # lowercase or digit.
    s = _re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
    # And before uppercase letter that's followed by lowercase.
    s = _re.sub(r"([A-Z])([A-Z][a-z])", r"\1_\2", s)
    return s.lower()


def _normalize_names(t: Term) -> Term:
    """Map identifier names to snake_case for cross-prover parity.

    Applied to Var.name, App.head, Forall.ty (when it's a simple
    identifier), and recursively under all Term constructors."""
    if isinstance(t, Var):
        return Var(_camel_to_snake(t.name))
    if isinstance(t, (IntLit, BoolLit, Unsupported)):
        return t
    if isinstance(t, App):
        return App(head=_camel_to_snake(t.head),
                   args=tuple(_normalize_names(a) for a in t.args))
    if isinstance(t, BinOp):
        return BinOp(t.op, _normalize_names(t.lhs), _normalize_names(t.rhs))
    if isinstance(t, UnaryOp):
        return UnaryOp(t.op, _normalize_names(t.arg))
    if isinstance(t, (Forall, Exists)):
        # Normalize binder names too (consistent with Var refs in the
        # body). Lean's `preEs` → `pre_es`, etc. Without this the body's
        # Vars and the binders would have mismatched casing after
        # alpha_normalize is skipped on the type string side.
        new_binders = tuple(_camel_to_snake(b) for b in t.binders)
        # Substitute the renamed binders into the body so Var refs match.
        mapping = {old: new for old, new in zip(t.binders, new_binders)
                   if old != new}
        body_renamed = substitute(t.body, mapping) if mapping else t.body
        ty_normalized = _normalize_type_string(t.ty)
        kind = Forall if isinstance(t, Forall) else Exists
        return kind(binders=new_binders, ty=ty_normalized,
                     body=_normalize_names(body_renamed))
    raise TypeError(f"_normalize_names: unknown {type(t)}")


def _normalize_type_string(ty: str) -> str:
    """Normalize a Forall/Exists `ty` field. Single identifiers via
    `_camel_to_snake`; structured pp-strings via per-token rewrite."""
    if ty in ("int", "nat", "Prop", "Type", "Bool", "bool"):
        return ty  # base types stay as-is
    low = ty.strip().lower()
    # Integer-like base types unify to `int` (Rocq `Z`, Lean `Int`).
    # `nat`/`Nat` is intentionally NOT mapped here — `_expand_nat_to_int`
    # handles it earlier (adding `>= 0` side conditions).
    if low in ("z", "integer"):
        return "int"
    # Sequence-like types unify to `seq` (Rocq `list T`, Lean `List T`,
    # WhyML `array int`) — the element type is irrelevant to the
    # round-trip statement's shape.
    head = low.split()[0] if low.split() else low
    if head in ("list", "array", "seq"):
        return "seq"
    import re as _re
    # Walk the string, lowercasing each identifier token; preserve
    # operator/paren punctuation.
    out_parts = []
    for token in _re.split(r"(\W+)", ty):
        if token and token[0].isalpha():
            out_parts.append(_camel_to_snake(token))
        else:
            out_parts.append(token)
    return "".join(out_parts)


def _iff_app_to_binop(t: Term) -> Term:
    """Rewrite `App('iff', [a, b])` to `BinOp('iff', a, b)` for
    cross-prover parity. Coq's `Iff` is a Const-applied form; Lean's
    `Iff` is also; both should canonicalize to a binop."""
    if isinstance(t, App) and t.head == "iff" and len(t.args) == 2:
        return BinOp("iff", _iff_app_to_binop(t.args[0]),
                     _iff_app_to_binop(t.args[1]))
    if isinstance(t, (Var, IntLit, BoolLit, Unsupported)):
        return t
    if isinstance(t, App):
        return App(head=t.head,
                   args=tuple(_iff_app_to_binop(a) for a in t.args))
    if isinstance(t, BinOp):
        return BinOp(t.op, _iff_app_to_binop(t.lhs),
                     _iff_app_to_binop(t.rhs))
    if isinstance(t, UnaryOp):
        return UnaryOp(t.op, _iff_app_to_binop(t.arg))
    if isinstance(t, (Forall, Exists)):
        kind = Forall if isinstance(t, Forall) else Exists
        return kind(binders=t.binders, ty=t.ty,
                     body=_iff_app_to_binop(t.body))
    raise TypeError(f"_iff_app_to_binop: unknown {type(t)}")


def canonicalize(t: Term) -> Term:
    """Apply the full canonicalization pipeline to a Term.

    Idempotent: a second call returns the same Term."""
    if isinstance(t, Unsupported):
        return t
    out = t
    out = _expand_nat_to_int(out)
    out = _flatten_foralls(out)
    out = _flip_comparisons(out)
    out = _dedup_arrow_chain(out)
    out = _ac_normalize(out)
    out = _sort_arrow_hypotheses(out)
    out = _iff_app_to_binop(out)
    out = _normalize_names(out)
    out = alpha_normalize(out)
    return out
