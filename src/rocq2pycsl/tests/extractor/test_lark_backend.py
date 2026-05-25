"""Lark-backend extractor tests."""

from __future__ import annotations

import textwrap

from rocq2pycsl.extractor.gallina import (
    GApp,
    GBinOp,
    GDivides,
    GExists,
    GForall,
    GLit,
    GUnaryOp,
    GVar,
)
from rocq2pycsl.extractor.lark_backend import (
    _AstBuilder,
    _PARSER,
    parse_module,
)


def _parse(src: str):
    """Helper to parse a bare expression (skipping module-level handling)."""
    tree = _PARSER.parse(src)
    return _AstBuilder().transform(tree)


# ──────────────────────────────────────────────────────────────────────
# Atoms
# ──────────────────────────────────────────────────────────────────────


def test_parse_variable():
    assert _parse("a") == GVar("a")


def test_parse_number():
    assert _parse("42") == GLit(42)


def test_parse_qualified_name():
    assert _parse("Nat.add") == GVar("Nat.add")


def test_parse_parens_around_var():
    assert _parse("(a)") == GVar("a")


# ──────────────────────────────────────────────────────────────────────
# Arithmetic
# ──────────────────────────────────────────────────────────────────────


def test_parse_addition():
    assert _parse("a + b") == GBinOp("+", GVar("a"), GVar("b"))


def test_parse_addition_is_left_associative():
    # a + b + c → ((a + b) + c)
    expected = GBinOp("+", GBinOp("+", GVar("a"), GVar("b")), GVar("c"))
    assert _parse("a + b + c") == expected


def test_parse_mul_higher_than_add():
    # a + b * c → a + (b * c)
    expected = GBinOp("+", GVar("a"), GBinOp("*", GVar("b"), GVar("c")))
    assert _parse("a + b * c") == expected


def test_parse_unary_minus():
    assert _parse("- a") == GUnaryOp("-", GVar("a"))


def test_parse_mod_and_div():
    assert _parse("a mod b") == GBinOp("mod", GVar("a"), GVar("b"))
    assert _parse("a div b") == GBinOp("div", GVar("a"), GVar("b"))


# ──────────────────────────────────────────────────────────────────────
# Comparison and logic
# ──────────────────────────────────────────────────────────────────────


def test_parse_equality():
    assert _parse("a = b") == GBinOp("=", GVar("a"), GVar("b"))


def test_parse_inequality_using_lt_gt():
    assert _parse("a <> b") == GBinOp("<>", GVar("a"), GVar("b"))
    assert _parse("a <= b") == GBinOp("<=", GVar("a"), GVar("b"))
    assert _parse("a < b") == GBinOp("<", GVar("a"), GVar("b"))
    assert _parse("a > b") == GBinOp(">", GVar("a"), GVar("b"))
    assert _parse("a >= b") == GBinOp(">=", GVar("a"), GVar("b"))


def test_parse_conjunction_and_disjunction():
    assert _parse("P /\\ Q") == GBinOp("/\\", GVar("P"), GVar("Q"))
    assert _parse("P \\/ Q") == GBinOp("\\/", GVar("P"), GVar("Q"))


def test_parse_implication():
    assert _parse("P -> Q") == GBinOp("->", GVar("P"), GVar("Q"))


def test_parse_negation():
    assert _parse("~ P") == GUnaryOp("~", GVar("P"))


def test_implication_is_right_associative():
    # P -> Q -> R → P -> (Q -> R)
    expected = GBinOp("->", GVar("P"), GBinOp("->", GVar("Q"), GVar("R")))
    assert _parse("P -> Q -> R") == expected


def test_arithmetic_then_comparison_then_implication():
    # n + 1 < m -> P → ((n + 1) < m) -> P
    inner = GBinOp(
        "<",
        GBinOp("+", GVar("n"), GLit(1)),
        GVar("m"),
    )
    expected = GBinOp("->", inner, GVar("P"))
    assert _parse("n + 1 < m -> P") == expected


# ──────────────────────────────────────────────────────────────────────
# Function application
# ──────────────────────────────────────────────────────────────────────


def test_parse_application():
    assert _parse("f a b") == GApp("f", (GVar("a"), GVar("b")))


def test_parse_qualified_application():
    assert _parse("Nat.add a b") == GApp("Nat.add", (GVar("a"), GVar("b")))


def test_parse_nested_application_with_parens():
    # f (g a) b → App(f, [App(g, a), b])
    expected = GApp("f", (GApp("g", (GVar("a"),)), GVar("b")))
    assert _parse("f (g a) b") == expected


# ──────────────────────────────────────────────────────────────────────
# Quantifiers
# ──────────────────────────────────────────────────────────────────────


def test_parse_forall_single_binder_typed():
    expected = GForall("a", "nat", GBinOp("=", GVar("a"), GVar("a")))
    assert _parse("forall a : nat, a = a") == expected


def test_parse_forall_multiple_binders_share_type():
    # forall a b : nat, ... → nested Forall chain
    out = _parse("forall a b : nat, P")
    assert isinstance(out, GForall)
    assert out.var == "a" and out.ty == "nat"
    assert isinstance(out.body, GForall)
    assert out.body.var == "b" and out.body.ty == "nat"
    assert out.body.body == GVar("P")


def test_parse_forall_grouped_typed_binders():
    out = _parse("forall (a b : nat) (c : Z), P")
    # Chain: Forall(a, nat, Forall(b, nat, Forall(c, Z, P)))
    assert out.var == "a" and out.ty == "nat"
    assert out.body.var == "b" and out.body.ty == "nat"
    assert out.body.body.var == "c" and out.body.body.ty == "Z"


def test_parse_exists():
    out = _parse("exists k : nat, a = k")
    assert isinstance(out, GExists)
    assert out.var == "k" and out.ty == "nat"
    assert out.body == GBinOp("=", GVar("a"), GVar("k"))


# ──────────────────────────────────────────────────────────────────────
# Divides
# ──────────────────────────────────────────────────────────────────────


def test_parse_divides_basic():
    assert _parse("(d | n)") == GDivides(d=GVar("d"), n=GVar("n"))


def test_parse_divides_with_applications():
    # (gcd a b | a)
    out = _parse("(gcd a b | a)")
    assert isinstance(out, GDivides)
    assert out.d == GApp("gcd", (GVar("a"), GVar("b")))
    assert out.n == GVar("a")


def test_parse_divides_inside_conjunction():
    out = _parse("(d | a) /\\ (d | b)")
    assert out == GBinOp(
        "/\\",
        GDivides(d=GVar("d"), n=GVar("a")),
        GDivides(d=GVar("d"), n=GVar("b")),
    )


# ──────────────────────────────────────────────────────────────────────
# Module-level parsing
# ──────────────────────────────────────────────────────────────────────


def test_parse_module_with_one_theorem():
    src = "Theorem foo : forall a : nat, a = a."
    mod = parse_module(src, source_path="t.v")
    assert len(mod.theorems) == 1
    t = mod.theorems[0]
    assert t.name == "foo"
    # Outer forall got peeled into `binders`; the statement is the body.
    assert t.binders == (("a", "nat"),)
    assert t.statement == GBinOp("=", GVar("a"), GVar("a"))


def test_parse_module_ignores_require_and_open():
    src = textwrap.dedent("""
        Require Import Arith.
        Open Scope nat_scope.

        Theorem foo : 1 + 1 = 2.
        Proof. reflexivity. Qed.
    """)
    mod = parse_module(src)
    assert [t.name for t in mod.theorems] == ["foo"]
    assert mod.functions == ()


def test_parse_module_picks_up_definition_and_fixpoint():
    src = textwrap.dedent("""
        Definition succ (n : nat) : nat := n + 1.
        Fixpoint length (l : list nat) : nat := 0.
    """)
    mod = parse_module(src)
    names = [f.name for f in mod.functions]
    assert names == ["succ", "length"]
    succ = mod.function("succ")
    assert succ.params == (("n", "nat"),)
    assert succ.return_ty == "nat"
    assert succ.is_recursive is False
    length = mod.function("length")
    assert length.is_recursive is True


def test_parse_module_function_with_measure():
    src = "Function gcd (a b : nat) {measure b} : nat := a."
    mod = parse_module(src)
    g = mod.function("gcd")
    assert g is not None
    assert g.params == (("a", "nat"), ("b", "nat"))
    assert g.measure == GVar("b")
    assert g.is_recursive is True


def test_parse_module_gcd_corpus():
    src = textwrap.dedent("""
        Require Import Arith.

        Function gcd (a b : nat) {measure b} : nat := a.

        Theorem gcd_divides : forall a b : nat, (gcd a b | a) /\\ (gcd a b | b).

        Theorem gcd_greatest :
          forall a b d : nat, (d | a) -> (d | b) -> (d | gcd a b).
    """)
    mod = parse_module(src)
    assert [t.name for t in mod.theorems] == ["gcd_divides", "gcd_greatest"]
    assert [f.name for f in mod.functions] == ["gcd"]

    # Outer ∀ binders on `gcd_divides`:
    gd = mod.theorem("gcd_divides")
    assert gd.binders == (("a", "nat"), ("b", "nat"))
    # Body should be a top-level /\ of two divides.
    assert isinstance(gd.statement, GBinOp)
    assert gd.statement.op == "/\\"
    assert isinstance(gd.statement.lhs, GDivides)
    assert isinstance(gd.statement.rhs, GDivides)

    # `gcd_greatest` should peel three binders and produce a chain of `->`.
    gg = mod.theorem("gcd_greatest")
    assert gg.binders == (("a", "nat"), ("b", "nat"), ("d", "nat"))
    # `(d | a) -> (d | b) -> (d | gcd a b)` parses right-assoc.
    s = gg.statement
    assert isinstance(s, GBinOp) and s.op == "->"
    # innermost should still be a `->`
    assert isinstance(s.rhs, GBinOp) and s.rhs.op == "->"
