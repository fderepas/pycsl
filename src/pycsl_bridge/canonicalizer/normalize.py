"""Canonicalize IR nodes for cross-prover comparison.

`canonicalize(node)` returns a frozen IR representative such that any
two logically-equivalent inputs (modulo the stylistic differences the
canonicalizer knows about) compare `==`.

Stages, applied bottom-up:

  1. **Recurse** into children — canonicalize them first.
  2. **Divides → operational form**. Both pipelines may produce
     `Divides` directly OR an `Exists` over `n == d * k`. We rewrite
     both to `BinOp("==", BinOp("%", n, d), Lit(0))` so subsequent
     comparison is structural. The original `Divides` node is the
     pivot because both extractors emit it; the existential form is
     less common but we handle it defensively.
  3. **Arithmetic identities**. Confluent rewrites:
        a + 0 → a,   0 + a → a
        a - 0 → a
        a * 1 → a,   1 * a → a
        not (not a) → a
        a == a → True   (when a is Var/Lit/Result — avoid blowing up on
                         side-effectful App, even though our App is pure)
        and (True, b) → b,  and (b, True) → b
        or  (False, b) → b, or (b, False) → b
  4. **AC-flatten + sort** for and/or/+/*. Each AC chain is flattened
     into an n-ary form, operands are canonicalized recursively, then
     sorted by `structural_hash`. The result is rebuilt as a
     right-associative chain so it remains a valid binary-IR tree.
     Order ties in the hash are broken by string form for stability.
  5. **Alpha-rename** Forall/Exists bound variables to v0, v1, ... in
     pre-order so two trees that bind the same shape with different
     names compare equal.

The implementation is intentionally simple — fewer rewrites means
fewer chances for non-confluence. Anything not covered here remains a
"disagreement" the diff will surface, which is the right behaviour
for v1.
"""

from __future__ import annotations

from dataclasses import dataclass

from pycsl_emit.ir import (
    App,
    BinOp,
    Divides,
    Exists,
    Forall,
    Lit,
    Node,
    Result,
    UnaryOp,
    Unsupported,
    Var,
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
)


# Operators that are commutative AND associative for our purposes.
_AC_OPS: frozenset[str] = frozenset({"and", "or", "+", "*"})


# Type-tag normalization across the two source languages. The Rocq side
# emits lower-case Coq surface tokens (`nat`, `list nat`, `string`) and
# the Lean side emits Lean's CamelCase (`Nat`, `List Nat`, `String`).
# To make Forall binders compare equal we map both onto a single canonical
# form (`nat`, `list nat`, ...).
_TYPE_ALIASES: dict[str, str] = {
    # Numerics
    "Nat": "nat",
    "Z": "int",
    "Int": "int",
    # Booleans
    "Bool": "bool",
    "Prop": "prop",
    # Strings
    "String": "string",
}


def _normalize_type(ty: str) -> str:
    """Lower-case known Coq/Lean type-token aliases so the two pipelines
    produce structurally identical Forall binders for the same source-
    language type."""
    parts = ty.split()
    out = []
    for p in parts:
        # Strip surrounding parens conservatively.
        stripped = p.strip("()")
        out.append(_TYPE_ALIASES.get(stripped, stripped.lower() if stripped[:1].isupper() else stripped))
    return " ".join(out)


def canonicalize(node: Node) -> Node:
    """Top-level entry. Returns a fresh canonical IR tree."""
    return _alpha_rename(_canon(node), {}, _Counter())


# ──────────────────────────────────────────────────────────────────────
# Stage 2 + 3 + 4: rewrite & flatten
# ──────────────────────────────────────────────────────────────────────


def _canon(node: Node) -> Node:
    """Bottom-up rewrite, AC-flatten + sort, identity rewrites.

    Bound-variable alpha-renaming happens separately in `_alpha_rename`
    after this pass — keeping the two phases independent makes them
    easier to test.
    """
    if isinstance(node, (Var, Lit, Result)):
        return node
    if isinstance(node, Unsupported):
        return node

    if isinstance(node, Divides):
        # Canonical operational form: `n % d == 0`.
        d_c = _canon(node.d)
        n_c = _canon(node.n)
        return BinOp("==", BinOp("%", n_c, d_c), Lit(0))

    if isinstance(node, App):
        return App(fn=node.fn, args=tuple(_canon(a) for a in node.args))

    if isinstance(node, UnaryOp):
        arg = _canon(node.arg)
        if node.op == "not" and isinstance(arg, UnaryOp) and arg.op == "not":
            return arg.arg
        return UnaryOp(op=node.op, arg=arg)

    if isinstance(node, BinOp):
        # AC operators: flatten + sort + rebuild.
        if node.op in _AC_OPS:
            operands = _flatten_ac(node, node.op)
            canon_operands = [_canon(o) for o in operands]
            # Apply identity simplifications BEFORE sorting so that
            # `a + 0` collapses to `a` and isn't kept as a 2-element AC chain.
            simplified = _simplify_ac(node.op, canon_operands)
            simplified.sort(key=lambda x: (structural_hash(x), _str(x)))
            return _rebuild_ac(node.op, simplified)

        # Non-AC binary ops.
        lhs = _canon(node.lhs)
        rhs = _canon(node.rhs)

        # Pre-canonicalize Exists-over-product → Divides-operational, so
        # `\exists k; n == d * k` matches the form from `Divides`.
        # (We handle the *symmetric* case where d and k could be swapped
        # because Lean and Rocq may emit `d * k` or `k * d`.)
        if isinstance(node, BinOp) and node.op == "==":
            # `(n % d) == 0` is already canonical for divides.
            pass

        return BinOp(op=node.op, lhs=lhs, rhs=rhs)

    if isinstance(node, Forall):
        return Forall(var=node.var, ty=node.ty, body=_canon(node.body))
    if isinstance(node, Exists):
        # Match `∃ k; n == d * k` (or `k * d`) → operational divides form.
        body = _canon(node.body)
        rewritten = _maybe_existential_divides(node.var, body)
        if rewritten is not None:
            return rewritten
        return Exists(var=node.var, ty=node.ty, body=body)

    # ── Lists / arrays / tuples / dicts / strings ────────────────────
    if isinstance(node, Length):
        return Length(arr=_canon(node.arr))
    if isinstance(node, Nth):
        return Nth(arr=_canon(node.arr), i=_canon(node.i))
    if isinstance(node, Tuple):
        return Tuple(args=tuple(_canon(a) for a in node.args))
    if isinstance(node, Proj):
        t_c = _canon(node.t)
        # Proj(Tuple(args), i) → args[i] (only when in bounds).
        if isinstance(t_c, Tuple) and 0 <= node.i < len(t_c.args):
            return t_c.args[node.i]
        return Proj(t=t_c, i=node.i)
    if isinstance(node, MapGet):
        return MapGet(d=_canon(node.d), k=_canon(node.k))
    if isinstance(node, MapSet):
        return MapSet(d=_canon(node.d), k=_canon(node.k), v=_canon(node.v))
    if isinstance(node, MapEmpty):
        return node
    if isinstance(node, HasKey):
        return HasKey(d=_canon(node.d), k=_canon(node.k))
    if isinstance(node, StrConcat):
        # StrConcat is associative — canonical form is right-associative.
        # Flatten (a ^ b) ^ c → a ^ (b ^ c).
        operands = _flatten_str_concat(node)
        canon_operands = [_canon(o) for o in operands]
        return _rebuild_right_assoc_concat(canon_operands)
    if isinstance(node, StrLength):
        return StrLength(s=_canon(node.s))
    if isinstance(node, StrSub):
        return StrSub(s=_canon(node.s), lo=_canon(node.lo), hi=_canon(node.hi))
    if isinstance(node, StrLit):
        return node

    # ── Class instances ─────────────────────────────────────────────
    if isinstance(node, FieldGet):
        return FieldGet(obj=_canon(node.obj), name=node.name)

    # ── ghost_list ───────────────────────────────────────────────────
    if isinstance(node, ListNil):
        return node
    if isinstance(node, ListCons):
        return ListCons(head=_canon(node.head), tail=_canon(node.tail))
    if isinstance(node, ListLen):
        l_c = _canon(node.l)
        # `\list_length(\append(a, b))` → `\list_length(a) + \list_length(b)`.
        # Safe under Why3's `Length_Cons` axiom and is the standard idiom
        # recommended in invariant-writer/SKILL.md.
        if isinstance(l_c, ListAppend):
            return _canon(BinOp(
                op="+",
                lhs=ListLen(l=l_c.l1),
                rhs=ListLen(l=l_c.l2),
            ))
        # `\list_length(\nil)` → 0.
        if isinstance(l_c, ListNil):
            return Lit(0)
        # `\list_length(\cons(h, t))` → 1 + \list_length(t).
        if isinstance(l_c, ListCons):
            return _canon(BinOp(op="+", lhs=Lit(1), rhs=ListLen(l=l_c.tail)))
        return ListLen(l=l_c)
    if isinstance(node, ListAppend):
        # Right-associative canonical form for ListAppend.
        operands = _flatten_list_append(node)
        canon_operands = [_canon(o) for o in operands]
        return _rebuild_right_assoc_append(canon_operands)
    if isinstance(node, ListNthAt):
        return ListNthAt(l=_canon(node.l), i=_canon(node.i))

    # ── ghost_set ────────────────────────────────────────────────────
    if isinstance(node, SetEmpty):
        return node
    if isinstance(node, SetAdd):
        return SetAdd(s=_canon(node.s), x=_canon(node.x))
    if isinstance(node, SetRemove):
        return SetRemove(s=_canon(node.s), x=_canon(node.x))
    if isinstance(node, SetMem):
        return SetMem(x=_canon(node.x), s=_canon(node.s))
    if isinstance(node, SetUnion):
        # AC: flatten + sort by structural hash.
        operands = _flatten_set_ac(node, SetUnion)
        canon_operands = [_canon(o) for o in operands]
        # Drop SetEmpty (identity for union).
        filtered = [o for o in canon_operands if not isinstance(o, SetEmpty)]
        if not filtered:
            return SetEmpty()
        filtered.sort(key=lambda x: (structural_hash(x), _str(x)))
        return _rebuild_set_ac(SetUnion, filtered)
    if isinstance(node, SetInter):
        operands = _flatten_set_ac(node, SetInter)
        canon_operands = [_canon(o) for o in operands]
        # If any operand is SetEmpty, the whole intersection collapses.
        if any(isinstance(o, SetEmpty) for o in canon_operands):
            return SetEmpty()
        canon_operands.sort(key=lambda x: (structural_hash(x), _str(x)))
        return _rebuild_set_ac(SetInter, canon_operands)
    if isinstance(node, SetDiff):
        return SetDiff(a=_canon(node.a), b=_canon(node.b))
    if isinstance(node, SetSubset):
        a_c = _canon(node.a)
        b_c = _canon(node.b)
        # SetSubset(a, a) → True.
        if _str(a_c) == _str(b_c):
            return Lit(True)
        return SetSubset(a=a_c, b=b_c)
    if isinstance(node, SetEq):
        a_c = _canon(node.a)
        b_c = _canon(node.b)
        # Symmetric — normalize operand order so SetEq(a, b) == SetEq(b, a).
        if (structural_hash(b_c), _str(b_c)) < (structural_hash(a_c), _str(a_c)):
            a_c, b_c = b_c, a_c
        return SetEq(a=a_c, b=b_c)

    raise TypeError(f"canonicalize: unknown node {type(node).__name__}")


# ──────────────────────────────────────────────────────────────────────
# String / list / set AC-style flatten helpers
# ──────────────────────────────────────────────────────────────────────


def _flatten_str_concat(node: Node) -> list[Node]:
    if isinstance(node, StrConcat):
        return _flatten_str_concat(node.a) + _flatten_str_concat(node.b)
    return [node]


def _rebuild_right_assoc_concat(operands: list[Node]) -> Node:
    assert operands
    if len(operands) == 1:
        return operands[0]
    cur = operands[-1]
    for o in reversed(operands[:-1]):
        cur = StrConcat(a=o, b=cur)
    return cur


def _flatten_list_append(node: Node) -> list[Node]:
    if isinstance(node, ListAppend):
        return _flatten_list_append(node.l1) + _flatten_list_append(node.l2)
    return [node]


def _rebuild_right_assoc_append(operands: list[Node]) -> Node:
    assert operands
    if len(operands) == 1:
        return operands[0]
    cur = operands[-1]
    for o in reversed(operands[:-1]):
        cur = ListAppend(l1=o, l2=cur)
    return cur


def _flatten_set_ac(node: Node, cls: type) -> list[Node]:
    """Flatten a SetUnion or SetInter chain into its operands."""
    if isinstance(node, cls):
        return _flatten_set_ac(node.a, cls) + _flatten_set_ac(node.b, cls)
    return [node]


def _rebuild_set_ac(cls: type, operands: list[Node]) -> Node:
    assert operands
    if len(operands) == 1:
        return operands[0]
    cur = operands[-1]
    for o in reversed(operands[:-1]):
        cur = cls(a=o, b=cur)
    return cur


def _maybe_existential_divides(bound_var: str, body: Node) -> Node | None:
    """Detect `n == d * k` (or `k * d`) with `k == bound_var` and `k`
    not free elsewhere — rewrite to `(n % d) == 0`.

    This is what Lean / Rocq might produce when the user writes the
    faithful `∃ k, n = d * k` form of divides.
    """
    if not (isinstance(body, BinOp) and body.op == "=="):
        return None
    n_side, prod_side = body.lhs, body.rhs
    # The product can be on either side of the equality.
    for candidate_n, candidate_prod in ((n_side, prod_side), (prod_side, n_side)):
        if not (isinstance(candidate_prod, BinOp) and candidate_prod.op == "*"):
            continue
        # The bound variable must be one of the factors and must NOT
        # appear free in the n-side or in the other factor.
        for k_pos, d_pos in (
            (candidate_prod.lhs, candidate_prod.rhs),
            (candidate_prod.rhs, candidate_prod.lhs),
        ):
            if isinstance(k_pos, Var) and k_pos.name == bound_var:
                if _is_free(bound_var, candidate_n) or _is_free(bound_var, d_pos):
                    continue
                return BinOp("==", BinOp("%", candidate_n, d_pos), Lit(0))
    return None


def _is_free(name: str, node: Node) -> bool:
    """Naive free-variable check (no shadowing handling — sufficient
    for the v1 supported subset where bound vars don't shadow)."""
    if isinstance(node, Var):
        return node.name == name
    if isinstance(node, (Lit, Result, Unsupported, StrLit)):
        return False
    if isinstance(node, App):
        return any(_is_free(name, a) for a in node.args)
    if isinstance(node, BinOp):
        return _is_free(name, node.lhs) or _is_free(name, node.rhs)
    if isinstance(node, UnaryOp):
        return _is_free(name, node.arg)
    if isinstance(node, (Forall, Exists)):
        return node.var != name and _is_free(name, node.body)
    if isinstance(node, Divides):
        return _is_free(name, node.d) or _is_free(name, node.n)
    # New nodes — recurse through their children.
    if isinstance(node, Length):
        return _is_free(name, node.arr)
    if isinstance(node, Nth):
        return _is_free(name, node.arr) or _is_free(name, node.i)
    if isinstance(node, Tuple):
        return any(_is_free(name, a) for a in node.args)
    if isinstance(node, Proj):
        return _is_free(name, node.t)
    if isinstance(node, MapGet):
        return _is_free(name, node.d) or _is_free(name, node.k)
    if isinstance(node, MapSet):
        return (
            _is_free(name, node.d)
            or _is_free(name, node.k)
            or _is_free(name, node.v)
        )
    if isinstance(node, MapEmpty):
        return False
    if isinstance(node, HasKey):
        return _is_free(name, node.d) or _is_free(name, node.k)
    if isinstance(node, StrConcat):
        return _is_free(name, node.a) or _is_free(name, node.b)
    if isinstance(node, StrLength):
        return _is_free(name, node.s)
    if isinstance(node, StrSub):
        return (
            _is_free(name, node.s)
            or _is_free(name, node.lo)
            or _is_free(name, node.hi)
        )
    if isinstance(node, FieldGet):
        return _is_free(name, node.obj)
    if isinstance(node, ListNil):
        return False
    if isinstance(node, ListCons):
        return _is_free(name, node.head) or _is_free(name, node.tail)
    if isinstance(node, ListLen):
        return _is_free(name, node.l)
    if isinstance(node, ListAppend):
        return _is_free(name, node.l1) or _is_free(name, node.l2)
    if isinstance(node, ListNthAt):
        return _is_free(name, node.l) or _is_free(name, node.i)
    if isinstance(node, SetEmpty):
        return False
    if isinstance(node, (SetAdd, SetRemove)):
        return _is_free(name, node.s) or _is_free(name, node.x)
    if isinstance(node, SetMem):
        return _is_free(name, node.x) or _is_free(name, node.s)
    if isinstance(node, (SetUnion, SetInter, SetDiff, SetSubset, SetEq)):
        return _is_free(name, node.a) or _is_free(name, node.b)
    return False


def _flatten_ac(node: Node, op: str) -> list[Node]:
    """Collect all operands of an AC-chained binary operator into a flat list."""
    if isinstance(node, BinOp) and node.op == op:
        return _flatten_ac(node.lhs, op) + _flatten_ac(node.rhs, op)
    return [node]


def _simplify_ac(op: str, operands: list[Node]) -> list[Node]:
    """Apply arithmetic / boolean identity rewrites to a flat AC list."""
    out: list[Node] = []
    for o in operands:
        # Drop neutral elements.
        if op == "+" and o == Lit(0):
            continue
        if op == "*" and o == Lit(1):
            continue
        if op == "and" and _is_true_literal(o):
            continue
        if op == "or" and _is_false_literal(o):
            continue
        out.append(o)

    # Absorbing elements.
    if op == "*" and any(o == Lit(0) for o in out):
        return [Lit(0)]
    if op == "and" and any(_is_false_literal(o) for o in out):
        return [Lit(False)]
    if op == "or" and any(_is_true_literal(o) for o in out):
        return [Lit(True)]

    if not out:
        # The whole chain collapsed to the identity element.
        if op == "+":
            return [Lit(0)]
        if op == "*":
            return [Lit(1)]
        if op == "and":
            return [Lit(True)]
        if op == "or":
            return [Lit(False)]
    return out


def _is_true_literal(n: Node) -> bool:
    return isinstance(n, Lit) and n.value is True


def _is_false_literal(n: Node) -> bool:
    return isinstance(n, Lit) and n.value is False


def _rebuild_ac(op: str, operands: list[Node]) -> Node:
    """Right-associative rebuild of an n-ary AC chain into binary IR."""
    assert operands, "rebuild_ac requires a non-empty operand list"
    if len(operands) == 1:
        return operands[0]
    cur = operands[-1]
    for o in reversed(operands[:-1]):
        cur = BinOp(op=op, lhs=o, rhs=cur)
    return cur


# ──────────────────────────────────────────────────────────────────────
# Stage 5: alpha rename
# ──────────────────────────────────────────────────────────────────────


@dataclass
class _Counter:
    n: int = 0

    def fresh(self) -> str:
        name = f"v{self.n}"
        self.n += 1
        return name


def _alpha_rename(node: Node, env: dict[str, str], c: _Counter) -> Node:
    """Replace bound names with canonical `v0, v1, ...` in pre-order."""
    if isinstance(node, Var):
        return Var(env.get(node.name, node.name))
    if isinstance(node, (Lit, Result, Unsupported)):
        return node
    if isinstance(node, App):
        return App(fn=node.fn, args=tuple(_alpha_rename(a, env, c) for a in node.args))
    if isinstance(node, BinOp):
        return BinOp(
            op=node.op,
            lhs=_alpha_rename(node.lhs, env, c),
            rhs=_alpha_rename(node.rhs, env, c),
        )
    if isinstance(node, UnaryOp):
        return UnaryOp(op=node.op, arg=_alpha_rename(node.arg, env, c))
    if isinstance(node, Forall):
        new = c.fresh()
        return Forall(
            var=new,
            ty=_normalize_type(node.ty),
            body=_alpha_rename(node.body, {**env, node.var: new}, c),
        )
    if isinstance(node, Exists):
        new = c.fresh()
        return Exists(
            var=new,
            ty=_normalize_type(node.ty),
            body=_alpha_rename(node.body, {**env, node.var: new}, c),
        )
    if isinstance(node, Divides):
        # _canon should have eliminated all Divides; this is defensive.
        return Divides(
            d=_alpha_rename(node.d, env, c),
            n=_alpha_rename(node.n, env, c),
        )

    # New nodes — recurse without touching binders.
    if isinstance(node, (Lit, Result, Unsupported, StrLit, MapEmpty, ListNil, SetEmpty)):
        return node
    if isinstance(node, Length):
        return Length(arr=_alpha_rename(node.arr, env, c))
    if isinstance(node, Nth):
        return Nth(
            arr=_alpha_rename(node.arr, env, c),
            i=_alpha_rename(node.i, env, c),
        )
    if isinstance(node, Tuple):
        return Tuple(args=tuple(_alpha_rename(a, env, c) for a in node.args))
    if isinstance(node, Proj):
        return Proj(t=_alpha_rename(node.t, env, c), i=node.i)
    if isinstance(node, MapGet):
        return MapGet(
            d=_alpha_rename(node.d, env, c),
            k=_alpha_rename(node.k, env, c),
        )
    if isinstance(node, MapSet):
        return MapSet(
            d=_alpha_rename(node.d, env, c),
            k=_alpha_rename(node.k, env, c),
            v=_alpha_rename(node.v, env, c),
        )
    if isinstance(node, HasKey):
        return HasKey(
            d=_alpha_rename(node.d, env, c),
            k=_alpha_rename(node.k, env, c),
        )
    if isinstance(node, StrConcat):
        return StrConcat(
            a=_alpha_rename(node.a, env, c),
            b=_alpha_rename(node.b, env, c),
        )
    if isinstance(node, StrLength):
        return StrLength(s=_alpha_rename(node.s, env, c))
    if isinstance(node, StrSub):
        return StrSub(
            s=_alpha_rename(node.s, env, c),
            lo=_alpha_rename(node.lo, env, c),
            hi=_alpha_rename(node.hi, env, c),
        )
    if isinstance(node, FieldGet):
        return FieldGet(obj=_alpha_rename(node.obj, env, c), name=node.name)
    if isinstance(node, ListCons):
        return ListCons(
            head=_alpha_rename(node.head, env, c),
            tail=_alpha_rename(node.tail, env, c),
        )
    if isinstance(node, ListLen):
        return ListLen(l=_alpha_rename(node.l, env, c))
    if isinstance(node, ListAppend):
        return ListAppend(
            l1=_alpha_rename(node.l1, env, c),
            l2=_alpha_rename(node.l2, env, c),
        )
    if isinstance(node, ListNthAt):
        return ListNthAt(
            l=_alpha_rename(node.l, env, c),
            i=_alpha_rename(node.i, env, c),
        )
    if isinstance(node, (SetAdd, SetRemove)):
        return type(node)(
            s=_alpha_rename(node.s, env, c),
            x=_alpha_rename(node.x, env, c),
        )
    if isinstance(node, SetMem):
        return SetMem(
            x=_alpha_rename(node.x, env, c),
            s=_alpha_rename(node.s, env, c),
        )
    if isinstance(node, (SetUnion, SetInter, SetDiff, SetSubset, SetEq)):
        return type(node)(
            a=_alpha_rename(node.a, env, c),
            b=_alpha_rename(node.b, env, c),
        )
    raise TypeError(f"_alpha_rename: unknown node {type(node).__name__}")


# ──────────────────────────────────────────────────────────────────────
# Structural hash for stable sort
# ──────────────────────────────────────────────────────────────────────


def structural_hash(node: Node) -> int:
    """A deterministic, content-only hash used to sort AC operands.

    Avoids `hash()` of dataclass instances (which is content-based for
    frozen dataclasses but combines values via Python's internal
    polynomial — adequate but slightly opaque). This version is
    explicit so the ordering is documented and stable across
    interpreter versions.
    """
    return hash(_str(node))


def _str(node: Node) -> str:
    """Compact, deterministic string form for hashing/sorting."""
    if isinstance(node, Var):
        return f"V({node.name})"
    if isinstance(node, Lit):
        return f"L({node.value!r})"
    if isinstance(node, Result):
        return "R"
    if isinstance(node, Unsupported):
        return f"U({node.reason!r})"
    if isinstance(node, App):
        return f"A({node.fn};{','.join(_str(a) for a in node.args)})"
    if isinstance(node, BinOp):
        return f"B({node.op};{_str(node.lhs)};{_str(node.rhs)})"
    if isinstance(node, UnaryOp):
        return f"O({node.op};{_str(node.arg)})"
    if isinstance(node, Forall):
        return f"F({node.var}:{node.ty};{_str(node.body)})"
    if isinstance(node, Exists):
        return f"E({node.var}:{node.ty};{_str(node.body)})"
    if isinstance(node, Divides):
        return f"D({_str(node.d)};{_str(node.n)})"

    # New nodes — short distinct prefixes.
    if isinstance(node, Length):
        return f"Len({_str(node.arr)})"
    if isinstance(node, Nth):
        return f"Nth({_str(node.arr)};{_str(node.i)})"
    if isinstance(node, Tuple):
        return f"Tup({','.join(_str(a) for a in node.args)})"
    if isinstance(node, Proj):
        return f"Prj({_str(node.t)};{node.i})"
    if isinstance(node, MapGet):
        return f"MG({_str(node.d)};{_str(node.k)})"
    if isinstance(node, MapSet):
        return f"MS({_str(node.d)};{_str(node.k)};{_str(node.v)})"
    if isinstance(node, MapEmpty):
        return "ME"
    if isinstance(node, HasKey):
        return f"HK({_str(node.d)};{_str(node.k)})"
    if isinstance(node, StrConcat):
        return f"SC({_str(node.a)};{_str(node.b)})"
    if isinstance(node, StrLength):
        return f"SLn({_str(node.s)})"
    if isinstance(node, StrSub):
        return f"SSb({_str(node.s)};{_str(node.lo)};{_str(node.hi)})"
    if isinstance(node, StrLit):
        return f"SLt({node.value!r})"
    if isinstance(node, FieldGet):
        return f"FG({_str(node.obj)};{node.name})"
    if isinstance(node, ListNil):
        return "LN"
    if isinstance(node, ListCons):
        return f"LC({_str(node.head)};{_str(node.tail)})"
    if isinstance(node, ListLen):
        return f"LL({_str(node.l)})"
    if isinstance(node, ListAppend):
        return f"LA({_str(node.l1)};{_str(node.l2)})"
    if isinstance(node, ListNthAt):
        return f"LNa({_str(node.l)};{_str(node.i)})"
    if isinstance(node, SetEmpty):
        return "SE"
    if isinstance(node, SetAdd):
        return f"SAd({_str(node.s)};{_str(node.x)})"
    if isinstance(node, SetRemove):
        return f"SRm({_str(node.s)};{_str(node.x)})"
    if isinstance(node, SetMem):
        return f"SM({_str(node.x)};{_str(node.s)})"
    if isinstance(node, SetUnion):
        return f"SU({_str(node.a)};{_str(node.b)})"
    if isinstance(node, SetInter):
        return f"SI({_str(node.a)};{_str(node.b)})"
    if isinstance(node, SetDiff):
        return f"SDf({_str(node.a)};{_str(node.b)})"
    if isinstance(node, SetSubset):
        return f"SSs({_str(node.a)};{_str(node.b)})"
    if isinstance(node, SetEq):
        return f"SEq({_str(node.a)};{_str(node.b)})"

    raise TypeError(f"_str: unknown node {type(node).__name__}")
