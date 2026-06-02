"""Project Lean meta-extractor JSON into the shared IR
(proof2why3 Phase B — sticky-02.md).

The companion extractor `bin/proof2why3-lean-extract.lean` emits one
JSON object per cited qualname:

    {"qualname": "Pycsl.Reference.Gcd.gcd_step",
     "type": "∀ (a b : Nat), b > 0 → a.gcd b = b.gcd (a % b)",
     "ast": {<recursive Expr tree>}}

This module's `project_to_ir` walks the AST and produces the
`proof2why3.ir.Term` representation that the canonicalizer accepts.

Strategy:

  - de Bruijn indices in the AST are resolved to the surrounding
    binder names via a context stack.
  - `app` chains are linearized into n-ary `App(head, args)` form.
  - Type-class instance plumbing (`HMul.hMul`, `instHMod`, `Nat.instMod`,
    `outParam`, `OfNat`, …) is recognized at the App head and
    stripped — the IR represents `a + b` as `BinOp("+", a, b)`,
    not as `App("HAdd.hAdd", [Nat, Nat, Nat, instHAdd, a, b])`.

  - Numeric literals via `OfNat.ofNat 0` are recognized and replaced
    by `IntLit(0)`.

  - Standard library calls are normalized to short names via the
    same prefix table as the v1 surface parser
    (`Nat.gcd → gcd`, `HMod.hMod → mod`, etc.).

  - Anything not recognized falls through to `Unsupported`.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from proof2why3.ir import (
    App, BinOp, BoolLit, Exists, Forall, IntLit, Term, UnaryOp, Unsupported,
    Var,
)


# Type-class instance plumbing constants emitted by Lean's elaborator
# that should be stripped at the App head. The head ITSELF maps to the
# logical operator; trailing args are the actual operands after
# stripping the type + instance args at fixed positions.
#
# Format: head_name → (operator, n_skip_prefix_args, kind)
#   kind ∈ {"binop", "app"}
#
# For `HAdd.hAdd : (α : Type u) → (β : Type v) → (γ : outParam (Type w)) → HAdd α β γ → α → β → γ`
# the elaborated form is `HAdd.hAdd Nat Nat Nat instHAdd a b` — 4 type/instance
# args followed by the two operands.

_OP_TABLE_BINOP: Dict[str, Tuple[str, int]] = {
    # Standard ring/field operators (HAdd/HSub/HDiv as binops).
    "HAdd.hAdd": ("+",   4),
    "HSub.hSub": ("-",   4),
    "HMul.hMul": ("*",   4),
    "HDiv.hDiv": ("/",   4),
    # NOTE: HMod.hMod is intentionally NOT in this table — it's
    # handled below as an App("mod", [lhs, rhs]) for parity with the
    # Rocq-side `mod a b` prefix form. See note in project_to_ir.
    # Comparison via LE/LT/GE/GT/Eq/Ne typeclasses.
    "LE.le":     (">=",  2),  # NOTE: swap by flipping in canonical step
    "LT.lt":     (">",   2),
    "GE.ge":     (">=",  2),
    "GT.gt":     (">",   2),
    "Eq":        ("=",   1),  # `Eq α a b` — 1 type arg, 2 operands.
    "Ne":        ("<>",  1),
    # Logical connectives.
    "And":       (r"/\\", 0),
    "Or":        (r"\/",  0),
    "Iff":       ("iff",  0),
}

# For LE.le / LT.lt — the actual logical direction. Lean's `a ≤ b` is
# `LE.le a b`; v1 normalizer flips to `b >= a`. We keep that here for
# parity.
_FLIP_DIRECTION = {"LE.le": True, "LT.lt": True, "GE.ge": False, "GT.gt": False}


# Library-prefix strips applied to const names before they become Vars.
_PREFIX_STRIPS: List[Tuple[str, str]] = [
    ("Nat.gcd",    "gcd"),
    ("Nat.modulo", "mod"),
    ("Nat.add",    "add"),
    ("Nat.mul",    "mul"),
    ("Nat.sub",    "sub"),
    ("Nat.le",     "<="),
    ("Nat.lt",     "<"),
    # Phase C: Lean's `Iff` / `And` / `Or` / `Not` types.
    ("Iff",        "iff"),
]


def _body_references_bvar_0(ast: Any, depth: int = 0) -> bool:
    """Recursively check whether a Lean Expr JSON tree references
    bvar(depth) — the de Bruijn index corresponding to the innermost
    binder. If unused, the enclosing Forall is a logical arrow
    hypothesis (not a value-level quantifier)."""
    if not isinstance(ast, dict):
        return False
    kind = ast.get("kind", "")
    if kind == "bvar":
        return ast.get("idx", -1) == depth
    if kind == "app":
        return (_body_references_bvar_0(ast.get("fn"), depth)
                or _body_references_bvar_0(ast.get("arg"), depth))
    if kind in ("forall", "lam"):
        # Entering a new binder increases the depth of our target.
        return _body_references_bvar_0(ast.get("body"), depth + 1) \
               or _body_references_bvar_0(ast.get("ty"), depth)
    if kind == "let":
        return (_body_references_bvar_0(ast.get("val"), depth)
                or _body_references_bvar_0(ast.get("ty"), depth)
                or _body_references_bvar_0(ast.get("body"), depth + 1))
    if kind == "proj":
        return _body_references_bvar_0(ast.get("expr"), depth)
    # const, fvar, lit, sort, mvar, unsupported — no bvar refs
    return False


def _strip_const_name(name: str) -> str:
    for src, dst in _PREFIX_STRIPS:
        if name == src:
            return dst
    return name


def _linearize_app(ast: Dict[str, Any]) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """Collapse a nested `{"kind":"app", "fn":..., "arg":...}` chain into
    `(head, args_in_left_to_right_order)`."""
    args: List[Dict[str, Any]] = []
    cur = ast
    while isinstance(cur, dict) and cur.get("kind") == "app":
        args.insert(0, cur["arg"])
        cur = cur["fn"]
    return cur, args


def _is_ofnat_lit(ast: Dict[str, Any]) -> Optional[int]:
    """Detect `OfNat.ofNat Nat n instOfNat` patterns and return n."""
    head, args = _linearize_app(ast)
    if not (isinstance(head, dict) and head.get("kind") == "const"
            and head.get("name") == "OfNat.ofNat"):
        return None
    # OfNat.ofNat α n inst → 3 args: type, raw nat literal, instance.
    if len(args) >= 2:
        lit = args[1]
        if isinstance(lit, dict) and lit.get("kind") == "lit":
            try:
                return int(lit.get("value", ""))
            except ValueError:
                return None
        # Raw nat literal sometimes shows as bvar-shaped; recurse into
        # nested OfNat / Nat constructor.
        head2, args2 = _linearize_app(lit)
        if isinstance(head2, dict) and head2.get("kind") == "lit":
            try:
                return int(head2.get("value", ""))
            except ValueError:
                return None
    return None


def project_to_ir(ast: Dict[str, Any],
                  ctx: Optional[List[str]] = None) -> Term:
    """Recursively project a Lean Expr JSON object to a shared IR Term."""
    if ctx is None:
        ctx = []
    if not isinstance(ast, dict):
        return Unsupported(reason=f"non-dict ast: {type(ast)}", raw=str(ast))
    kind = ast.get("kind", "")
    if kind == "forall":
        binder = ast["binder"]
        ty_ast = ast["ty"]
        body_ast = ast["body"]
        ty_term = project_to_ir(ty_ast, ctx)
        # Phase C v1: anonymous binders are arrow hypotheses; named
        # binders are quantifiers. Heuristic: a binder is anonymous if
        # its name pattern-matches a known auto-generated form OR if
        # its body doesn't reference the bound variable via bvar 0
        # (i.e. the dependency is logical, not value-level).
        is_anon = (
            binder.startswith("_")
            or "._@._internal._hyg" in binder
            or "._@._" in binder
            or not _body_references_bvar_0(body_ast)
        )
        if is_anon:
            return BinOp("->", ty_term, project_to_ir(body_ast, ctx + ["_hyp"]))
        body_term = project_to_ir(body_ast, ctx + [binder])
        ty_str = (ty_term.name if isinstance(ty_term, Var) else ty_term.pp())
        return Forall(binders=(binder,), ty=ty_str, body=body_term)
    if kind == "app":
        head, args = _linearize_app(ast)
        # Try OfNat literal recognition first (head appears at app spine).
        olit = _is_ofnat_lit(ast)
        if olit is not None:
            return IntLit(olit)
        # Recognize known binop heads.
        if isinstance(head, dict) and head.get("kind") == "const":
            hname = head.get("name", "")
            # HMod.hMod: 4 type/instance args, then lhs + rhs operands.
            # Emit as App("mod", [lhs, rhs]) to match Rocq's prefix
            # rendering of `PeanoNat.Nat.modulo a b`.
            if hname == "HMod.hMod" and len(args) >= 6:
                lhs = project_to_ir(args[4], ctx)
                rhs = project_to_ir(args[5], ctx)
                return App(head="mod", args=(lhs, rhs))
            if hname in _OP_TABLE_BINOP:
                op, n_skip = _OP_TABLE_BINOP[hname]
                ops = args[n_skip:]
                if len(ops) == 2:
                    lhs = project_to_ir(ops[0], ctx)
                    rhs = project_to_ir(ops[1], ctx)
                    if _FLIP_DIRECTION.get(hname, False):
                        return BinOp(op, rhs, lhs)
                    return BinOp(op, lhs, rhs)
                # Variadic And/Or — fall through to generic App.
            # Standard library predicate / function call.
            short = _strip_const_name(hname)
            arg_terms = [project_to_ir(a, ctx) for a in args]
            # Skip leading args that are constants for types/instances
            # (heuristic: a leading Var that names a type stays as is for
            # simple functions; but for gcd-family Lean wraps `Nat.gcd`
            # with implicit type args). For Nat.gcd → gcd, the args are
            # just the two Nat operands; no implicit args at the head.
            return App(head=short, args=tuple(arg_terms))
        # Non-const head: project the head and the args separately.
        head_term = project_to_ir(head, ctx)
        arg_terms = [project_to_ir(a, ctx) for a in args]
        if isinstance(head_term, Var):
            return App(head=head_term.name, args=tuple(arg_terms))
        return Unsupported(reason=f"non-trivial head {head_term}",
                            raw=str(ast)[:100])
    if kind == "const":
        return Var(_strip_const_name(ast.get("name", "?")))
    if kind == "bvar":
        idx = ast.get("idx", 0)
        if 0 <= idx < len(ctx):
            return Var(ctx[len(ctx) - 1 - idx])
        return Unsupported(reason=f"bvar idx {idx} out of context ({len(ctx)})",
                            raw=str(ast))
    if kind == "fvar":
        return Var(ast.get("id", "?fvar"))
    if kind == "lit":
        v = ast.get("value", "")
        try:
            return IntLit(int(v))
        except ValueError:
            return Var(str(v))
    if kind == "sort":
        # Lean's universes: level "0" = Prop; higher levels = Type.
        level = ast.get("level", "")
        if str(level) in ("0", "Prop"):
            return Var("Prop")
        return Var("Type")
    if kind == "unsupported":
        return Unsupported(reason="lean-unsupported", raw=str(ast.get("raw", "")))
    return Unsupported(reason=f"unknown lean kind {kind}", raw=str(ast)[:100])
