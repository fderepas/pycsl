"""Canonicalizer tests.

Each case asserts that two surface-different but logically-equivalent
inputs canonicalize to the *same* IR. This is the contract the
reconciler depends on.
"""

from __future__ import annotations

import pytest

from pycsl_emit.ir import (
    App,
    BinOp,
    Divides,
    Exists,
    Forall,
    Lit,
    Result,
    UnaryOp,
    Var,
)

from pycsl_bridge.canonicalizer import canonicalize, structural_hash


def _eq_after_canon(a, b):
    return canonicalize(a) == canonicalize(b)


# ──────────────────────────────────────────────────────────────────────
# Divides — the headline cross-prover canonicalization
# ──────────────────────────────────────────────────────────────────────


def test_divides_operational_is_canonical():
    """The IR.Divides node always canonicalizes to `n % d == 0`."""
    d = Divides(d=Var("d"), n=Var("n"))
    out = canonicalize(d)
    assert out == BinOp("==", BinOp("%", Var("n"), Var("d")), Lit(0))


def test_divides_with_result_substitution():
    d = Divides(d=Result(), n=Var("a"))
    assert canonicalize(d) == BinOp("==", BinOp("%", Var("a"), Result()), Lit(0))


def test_existential_form_canonicalizes_to_operational():
    """`∃ k; n == d * k` → `(n % d) == 0`.

    This is the case where one formalism emits the faithful existential
    spelling and the other emits the operational `%` form.
    """
    operational = Divides(d=Var("d"), n=Var("n"))
    existential = Exists(
        "k", "int",
        BinOp("==", Var("n"), BinOp("*", Var("d"), Var("k"))),
    )
    assert _eq_after_canon(operational, existential)


def test_existential_with_swapped_factor_order():
    """`∃ k; n == k * d` (factor order swapped) also canonicalizes."""
    operational = Divides(d=Var("d"), n=Var("n"))
    existential = Exists(
        "k", "int",
        BinOp("==", Var("n"), BinOp("*", Var("k"), Var("d"))),
    )
    assert _eq_after_canon(operational, existential)


def test_existential_with_swapped_equality_sides():
    """`∃ k; d * k == n` also canonicalizes."""
    operational = Divides(d=Var("d"), n=Var("n"))
    existential = Exists(
        "k", "int",
        BinOp("==", BinOp("*", Var("d"), Var("k")), Var("n")),
    )
    assert _eq_after_canon(operational, existential)


def test_existential_with_unrelated_body_is_not_divides():
    """`∃ k; k = 5` is NOT a divides — keep it as Exists."""
    e = Exists("k", "int", BinOp("==", Var("k"), Lit(5)))
    out = canonicalize(e)
    assert isinstance(out, Exists)


# ──────────────────────────────────────────────────────────────────────
# Arithmetic identities
# ──────────────────────────────────────────────────────────────────────


def test_add_zero_is_identity():
    assert canonicalize(BinOp("+", Var("a"), Lit(0))) == Var("a")
    assert canonicalize(BinOp("+", Lit(0), Var("a"))) == Var("a")


def test_mul_one_is_identity():
    assert canonicalize(BinOp("*", Var("a"), Lit(1))) == Var("a")
    assert canonicalize(BinOp("*", Lit(1), Var("a"))) == Var("a")


def test_mul_zero_absorbs():
    assert canonicalize(BinOp("*", Var("a"), Lit(0))) == Lit(0)


def test_double_negation_collapses():
    e = UnaryOp("not", UnaryOp("not", Var("p")))
    assert canonicalize(e) == Var("p")


def test_and_true_is_identity():
    assert canonicalize(BinOp("and", Var("p"), Lit(True))) == Var("p")
    assert canonicalize(BinOp("and", Lit(True), Var("p"))) == Var("p")


def test_or_false_is_identity():
    assert canonicalize(BinOp("or", Var("p"), Lit(False))) == Var("p")


def test_and_false_is_absorbing():
    assert canonicalize(BinOp("and", Var("p"), Lit(False))) == Lit(False)


def test_or_true_is_absorbing():
    assert canonicalize(BinOp("or", Var("p"), Lit(True))) == Lit(True)


# ──────────────────────────────────────────────────────────────────────
# AC flatten + sort
# ──────────────────────────────────────────────────────────────────────


def test_and_is_commutative():
    a = BinOp("and", Var("a"), Var("b"))
    b = BinOp("and", Var("b"), Var("a"))
    assert _eq_after_canon(a, b)


def test_and_is_associative():
    a = BinOp("and", BinOp("and", Var("a"), Var("b")), Var("c"))
    b = BinOp("and", Var("a"), BinOp("and", Var("b"), Var("c")))
    assert _eq_after_canon(a, b)


def test_addition_is_commutative():
    a = BinOp("+", Var("a"), Var("b"))
    b = BinOp("+", Var("b"), Var("a"))
    assert _eq_after_canon(a, b)


def test_long_and_chains_with_permuted_order():
    a = BinOp(
        "and",
        BinOp("and", Var("a"), Var("b")),
        BinOp("and", Var("c"), Var("d")),
    )
    b = BinOp(
        "and",
        BinOp("and", Var("d"), Var("c")),
        BinOp("and", Var("b"), Var("a")),
    )
    assert _eq_after_canon(a, b)


def test_implication_is_NOT_commutative():
    """`P ==> Q` is not equivalent to `Q ==> P`; the canonicalizer must
    preserve the original asymmetry."""
    a = BinOp("==>", Var("p"), Var("q"))
    b = BinOp("==>", Var("q"), Var("p"))
    assert not _eq_after_canon(a, b)


# ──────────────────────────────────────────────────────────────────────
# Alpha renaming
# ──────────────────────────────────────────────────────────────────────


def test_forall_alpha_renames_to_v0():
    a = Forall("x", "int", BinOp("==", Var("x"), Var("x")))
    b = Forall("y", "int", BinOp("==", Var("y"), Var("y")))
    assert _eq_after_canon(a, b)
    out = canonicalize(a)
    assert isinstance(out, Forall) and out.var == "v0"


def test_nested_forall_renames_in_pre_order():
    a = Forall(
        "outer", "int",
        Forall("inner", "int", BinOp("==", Var("outer"), Var("inner"))),
    )
    b = Forall(
        "a", "int",
        Forall("b", "int", BinOp("==", Var("a"), Var("b"))),
    )
    assert _eq_after_canon(a, b)


def test_free_variables_are_not_renamed():
    """The Python parameter `a` (free, comes from absorbed binders)
    must survive canonicalization unchanged."""
    expr = BinOp("==", BinOp("%", Var("a"), Result()), Lit(0))
    assert canonicalize(expr) == expr


# ──────────────────────────────────────────────────────────────────────
# Worked example: gcd contracts from rocq2pycsl vs lean2pycsl
# ──────────────────────────────────────────────────────────────────────


def test_gcd_dvd_left_canonicalizes_identically():
    """Both `Divides(d=Result(), n=Var("a"))` (operational style) and
    the existential variant should produce the same canonical IR."""
    rocq_style = Divides(d=Result(), n=Var("a"))
    lean_style_via_existential = Exists(
        "k", "int",
        BinOp("==", Var("a"), BinOp("*", Result(), Var("k"))),
    )
    assert _eq_after_canon(rocq_style, lean_style_via_existential)


def test_gcd_greatest_with_inner_forall_uses_canonical_bound_name():
    """The unabsorbed `d` quantifier appears in both pipelines. Whether
    the var was named `d` (Rocq) or `d` (Lean), the canonical form
    uses `v0`."""
    rocq_style = Forall(
        "d", "int",
        BinOp(
            "==>",
            BinOp("and",
                  BinOp("==", BinOp("%", Var("a"), Var("d")), Lit(0)),
                  BinOp("==", BinOp("%", Var("b"), Var("d")), Lit(0))),
            BinOp("==", BinOp("%", Result(), Var("d")), Lit(0)),
        ),
    )
    out = canonicalize(rocq_style)
    assert isinstance(out, Forall)
    assert out.var == "v0"
    # The free vars `a`, `b`, and `Result` are not renamed.
    assert "a" in str(out) and "b" in str(out) and "Result" in str(out)


# ──────────────────────────────────────────────────────────────────────
# Stability
# ──────────────────────────────────────────────────────────────────────


def test_canonicalize_is_idempotent():
    """`canonicalize(canonicalize(x)) == canonicalize(x)`."""
    expr = BinOp(
        "and",
        BinOp("+", Var("a"), Lit(0)),
        UnaryOp("not", UnaryOp("not", Var("p"))),
    )
    once = canonicalize(expr)
    twice = canonicalize(once)
    assert once == twice


def test_structural_hash_is_deterministic():
    a = canonicalize(BinOp("+", Var("a"), Var("b")))
    assert structural_hash(a) == structural_hash(a)


# ──────────────────────────────────────────────────────────────────────
# Phase 2 — rewrite rules for the new IR nodes
# ──────────────────────────────────────────────────────────────────────


def test_str_concat_canonical_is_right_associative():
    """(a ^ b) ^ c  ≡  a ^ (b ^ c)."""
    from pycsl_emit.ir import StrConcat

    left = StrConcat(a=StrConcat(a=Var("a"), b=Var("b")), b=Var("c"))
    right = StrConcat(a=Var("a"), b=StrConcat(a=Var("b"), b=Var("c")))
    assert canonicalize(left) == canonicalize(right)


def test_list_append_canonical_is_right_associative():
    from pycsl_emit.ir import ListAppend

    left = ListAppend(l1=ListAppend(l1=Var("a"), l2=Var("b")), l2=Var("c"))
    right = ListAppend(l1=Var("a"), l2=ListAppend(l1=Var("b"), l2=Var("c")))
    assert canonicalize(left) == canonicalize(right)


def test_list_len_distributes_over_append():
    """`\\list_length(\\append(a, b))` → `\\list_length(a) + \\list_length(b)`."""
    from pycsl_emit.ir import ListAppend, ListLen

    expr = ListLen(l=ListAppend(l1=Var("a"), l2=Var("b")))
    out = canonicalize(expr)
    # The Lit(0) base case isn't hit here, so we expect a + AC tree.
    assert isinstance(out, BinOp) and out.op == "+"


def test_list_len_of_nil_is_zero():
    from pycsl_emit.ir import ListLen, ListNil

    out = canonicalize(ListLen(l=ListNil()))
    assert out == Lit(0)


def test_list_len_of_cons_is_one_plus_rest():
    from pycsl_emit.ir import ListCons, ListLen, ListNil

    expr = ListLen(l=ListCons(head=Var("x"), tail=ListNil()))
    out = canonicalize(expr)
    # 1 + 0 → 1 after AC simplification.
    assert out == Lit(1)


def test_proj_of_tuple_literal_indexes():
    """Proj(Tuple(a, b), 0) → a."""
    from pycsl_emit.ir import Proj, Tuple

    assert canonicalize(Proj(t=Tuple(args=(Var("a"), Var("b"))), i=0)) == Var("a")
    assert canonicalize(Proj(t=Tuple(args=(Var("a"), Var("b"))), i=1)) == Var("b")


def test_set_union_is_commutative_and_associative():
    from pycsl_emit.ir import SetUnion

    a_b = SetUnion(a=Var("a"), b=Var("b"))
    b_a = SetUnion(a=Var("b"), b=Var("a"))
    assert canonicalize(a_b) == canonicalize(b_a)

    # (a ∪ b) ∪ c ≡ a ∪ (b ∪ c) — also AC.
    left = SetUnion(a=SetUnion(a=Var("a"), b=Var("b")), b=Var("c"))
    right = SetUnion(a=Var("a"), b=SetUnion(a=Var("b"), b=Var("c")))
    assert canonicalize(left) == canonicalize(right)


def test_set_union_with_empty_drops_empty():
    from pycsl_emit.ir import SetEmpty, SetUnion

    assert canonicalize(SetUnion(a=SetEmpty(), b=Var("s"))) == Var("s")
    assert canonicalize(SetUnion(a=Var("s"), b=SetEmpty())) == Var("s")
    assert canonicalize(SetUnion(a=SetEmpty(), b=SetEmpty())) == SetEmpty()


def test_set_inter_with_empty_collapses_to_empty():
    from pycsl_emit.ir import SetEmpty, SetInter

    assert canonicalize(SetInter(a=Var("s"), b=SetEmpty())) == SetEmpty()
    assert canonicalize(SetInter(a=SetEmpty(), b=Var("s"))) == SetEmpty()


def test_set_subset_reflexive_to_true():
    from pycsl_emit.ir import SetSubset

    assert canonicalize(SetSubset(a=Var("s"), b=Var("s"))) == Lit(True)


def test_set_eq_symmetric():
    from pycsl_emit.ir import SetEq

    a_b = SetEq(a=Var("a"), b=Var("b"))
    b_a = SetEq(a=Var("b"), b=Var("a"))
    assert canonicalize(a_b) == canonicalize(b_a)


def test_canonicalize_recurses_through_new_nodes_with_forall():
    """A Forall over `\\set_eq(a, b)` still gets alpha-renamed."""
    from pycsl_emit.ir import SetEq

    expr = Forall(var="x", ty="int", body=SetEq(a=Var("a"), b=Var("b")))
    out = canonicalize(expr)
    assert isinstance(out, Forall)
    assert out.var == "v0"
