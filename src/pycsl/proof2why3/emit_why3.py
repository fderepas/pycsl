"""IR → WhyML axiom-body serializer (proof2why3 Phase 5 —
todo-saturday.md Item 3).

Inverse of `parser.parse_type_expr` ∘ `_preprocess_whyml` on the
canonicalizable subset of the IR. Used by `bin/proof2why3-emit.py`
to auto-generate `_AXIOM_REGISTRY` entries from cross-checked Rocq +
Lean theorems.

Design constraints:

- **Precedence-aware**: the emitter parenthesizes only where the
  parser's grammar requires it (BinOp under a tighter-binding parent,
  App in argument position). The grammar is the one in
  `proof2why3/parser.py` (parse_atom / parse_expr / arrow chain).
- **Round-trip**: `canonicalize(parse_type_expr(emit(t))) == canonicalize(t)`
  for every Term in the canonicalizable subset. Bound names are
  alpha-renamed to `v0`/`v1`/… by canonicalization; the emitter
  preserves whatever binder name lives in the input Term (typically
  `v0`/`v1`/… post-canonicalization, or `a`/`b`/… for hand-curated
  registry entries pre-canonicalization).
- **Unsupported terms** emit a `<<UNSUPPORTED:reason>>` sentinel.
  The merge tool should detect this and leave the existing registry
  entry intact (don't overwrite with garbage).

Surface details:
- Quantifier separator uses Why3's `.` (dot), not the parser's
  internal `,` (comma). The cross-check's `_preprocess_whyml` flips
  `.` → `,` before parsing; the emitter is the inverse.
"""
from __future__ import annotations

from proof2why3.ir import (
    App, BinOp, BoolLit, Exists, Forall, IntLit, Term, UnaryOp, Unsupported,
    Var,
)


# Precedence levels — higher binds tighter. Mirrors parser.py grammar.
_PREC_TOP = 0           # outside quantifier / top-level
_PREC_ARROW = 1         # right-leaning `->`
_PREC_OR = 2            # `\\/`
_PREC_AND = 3           # `/\\`
_PREC_CMP = 4           # `= > >= < <= <> !=`
_PREC_ADD = 5           # `+ -`
_PREC_MUL = 6           # `* mod` (folded as App for `mod`)
_PREC_APP = 7           # `head arg0 arg1 ...`
_PREC_ATOM = 8          # ident, literal, paren'd expr


_BINOP_PREC = {
    "->": _PREC_ARROW,
    "\\/": _PREC_OR,
    "/\\": _PREC_AND,
    "=":  _PREC_CMP, ">": _PREC_CMP, ">=": _PREC_CMP,
    "<":  _PREC_CMP, "<=": _PREC_CMP, "<>": _PREC_CMP, "!=": _PREC_CMP,
    "+":  _PREC_ADD, "-": _PREC_ADD,
    "*":  _PREC_MUL,
}


def _pp(t: Term, parent_prec: int) -> str:
    """Pretty-print `t` inside a context whose minimum-required
    precedence is `parent_prec`. Wraps with parens if our own
    precedence is strictly less than the parent's."""
    if isinstance(t, Var):
        return t.name
    if isinstance(t, IntLit):
        return str(t.value)
    if isinstance(t, BoolLit):
        return "true" if t.value else "false"
    if isinstance(t, Unsupported):
        return f"<<UNSUPPORTED:{t.reason}>>"
    if isinstance(t, Forall):
        binders = " ".join(t.binders)
        body = _pp(t.body, _PREC_TOP)
        s = f"forall {binders} : {t.ty}. {body}"
        return f"({s})" if parent_prec > _PREC_TOP else s
    if isinstance(t, Exists):
        binders = " ".join(t.binders)
        body = _pp(t.body, _PREC_TOP)
        s = f"exists {binders} : {t.ty}. {body}"
        return f"({s})" if parent_prec > _PREC_TOP else s
    if isinstance(t, BinOp):
        op_prec = _BINOP_PREC.get(t.op, _PREC_CMP)
        if t.op == "->":
            # Right-assoc: rhs at same prec, lhs at op_prec+1.
            lhs = _pp(t.lhs, op_prec + 1)
            rhs = _pp(t.rhs, op_prec)
        else:
            # Left-assoc: lhs at same prec, rhs at op_prec+1.
            lhs = _pp(t.lhs, op_prec)
            rhs = _pp(t.rhs, op_prec + 1)
        s = f"{lhs} {t.op} {rhs}"
        return f"({s})" if parent_prec > op_prec else s
    if isinstance(t, UnaryOp):
        # `not` and arithmetic `-`. Both bind tighter than * but we
        # parenthesize the arg at atom level to be safe.
        arg = _pp(t.arg, _PREC_ATOM)
        s = f"{t.op} {arg}"
        return f"({s})" if parent_prec > _PREC_MUL else s
    if isinstance(t, App):
        if not t.args:
            return t.head
        # Each argument must parse as a single atom — wrap in parens
        # if it would otherwise gobble more tokens.
        args_s = " ".join(_pp(a, _PREC_ATOM) for a in t.args)
        s = f"{t.head} {args_s}"
        return f"({s})" if parent_prec > _PREC_APP else s
    raise TypeError(f"_pp: unknown term type {type(t)}")


def ir_to_whyml_axiom_body(term: Term) -> str:
    """Serialize a Term back to a WhyML axiom-body string.

    The output is suitable for direct inclusion as a value in
    `_AXIOM_REGISTRY` (Module 6 preamble). Round-trip through
    `parse_type_expr` + `canonicalize` produces the same canonical
    form as the input."""
    return _pp(term, _PREC_TOP)


def contains_unsupported(term: Term) -> bool:
    """True if any sub-term is an `Unsupported` leaf. Used by the
    merge tool to skip non-round-trippable entries rather than
    overwriting the existing hand-curated body with a sentinel."""
    if isinstance(term, Unsupported):
        return True
    if isinstance(term, (Var, IntLit, BoolLit)):
        return False
    if isinstance(term, App):
        return any(contains_unsupported(a) for a in term.args)
    if isinstance(term, BinOp):
        return contains_unsupported(term.lhs) or contains_unsupported(term.rhs)
    if isinstance(term, UnaryOp):
        return contains_unsupported(term.arg)
    if isinstance(term, (Forall, Exists)):
        return contains_unsupported(term.body)
    raise TypeError(f"contains_unsupported: unknown {type(term)}")
