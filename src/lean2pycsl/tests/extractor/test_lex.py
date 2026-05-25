"""Tests for the Lean 4 lexer (comments + declaration splitter)."""

from __future__ import annotations

import textwrap

from lean2pycsl.extractor.lex import split_decls, strip_comments


def test_strip_block_comment():
    assert strip_comments("a (* hi *) b") == "a          b"


def test_strip_nested_block_comment():
    out = strip_comments("x (* outer (* inner *) more *) y")
    assert "inner" not in out and "outer" not in out
    assert out.startswith("x ") and out.endswith(" y")


def test_strip_line_comment():
    out = strip_comments("foo -- this is a comment\nbar")
    assert "this" not in out
    # Newline preserved so line numbers stay accurate.
    assert out.count("\n") == 1
    assert out.endswith("bar")


def test_strip_line_comment_does_not_eat_into_next_line():
    out = strip_comments("a -- comment\nb -- another\nc")
    lines = out.splitlines()
    assert lines[0].startswith("a ")
    assert lines[1].startswith("b ")
    assert lines[2].startswith("c")


def test_strip_string_literal_passthrough():
    out = strip_comments('let s := "hello -- not a comment" in x')
    assert "-- not a comment" in out


def test_split_decls_simple():
    src = textwrap.dedent("""
        theorem foo : 1 = 1 := rfl

        def bar (n : Nat) : Nat := n + 1

        lemma baz : 0 ≤ 0 := by rfl
    """)
    out = split_decls(src)
    heads = [d.body.split()[0] for d in out]
    assert heads == ["theorem", "def", "lemma"]


def test_split_decls_preserves_line_numbers():
    src = "\n\ntheorem foo : 1 = 1 := rfl\n\ndef bar : Nat := 0\n"
    out = split_decls(src)
    assert out[0].line == 3
    assert out[1].line == 5


def test_split_decls_includes_attribute_prefix():
    """An `@[pycsl_spec "..."]` attribute on its own line must be
    absorbed into the declaration body that follows it."""
    src = textwrap.dedent("""
        @[pycsl_spec "gcd"]
        theorem gcd_dvd_left : forall a b, gcd a b = a := sorry
    """)
    out = split_decls(src)
    assert len(out) == 1
    assert "@[pycsl_spec" in out[0].body
    assert "theorem gcd_dvd_left" in out[0].body


def test_split_decls_handles_modifiers():
    src = textwrap.dedent("""
        partial def loop : Nat := loop

        noncomputable def f (n : Nat) : Nat := n
    """)
    out = split_decls(src)
    heads = [d.body.split(None, 2)[:2] for d in out]
    assert heads == [["partial", "def"], ["noncomputable", "def"]]
