"""Tests for the comment stripper and vernac splitter."""

from __future__ import annotations

from rocq2pycsl.extractor.lex import split_vernacs, strip_comments


def test_strip_comments_simple():
    assert strip_comments("a (* hi *) b") == "a          b"


def test_strip_comments_nested():
    src = "x (* outer (* inner *) more *) y"
    out = strip_comments(src)
    # Everything between `(*` and `*)` becomes spaces; structure preserved.
    assert "x " in out
    assert " y" in out
    assert "inner" not in out and "outer" not in out


def test_strip_comments_preserves_newlines():
    src = "a\n(* line2\nline3 *)\nb"
    out = strip_comments(src)
    # Newlines inside comments must be preserved so source-line numbers
    # remain accurate downstream.
    assert out.count("\n") == 3


def test_strip_comments_string_literal_passthrough():
    src = 'a "this (* is *) text" b'
    out = strip_comments(src)
    # Comment markers inside string literals must not trigger stripping.
    assert "(* is *)" in out


def test_split_vernacs_basic():
    src = "Theorem foo : 1 + 1 = 2. Theorem bar : 0 = 0."
    out = split_vernacs(src)
    assert [v.body for v in out] == [
        "Theorem foo : 1 + 1 = 2",
        "Theorem bar : 0 = 0",
    ]


def test_split_vernacs_preserves_line_numbers():
    src = "\n\nTheorem foo : 1 = 1.\n\nTheorem bar : 2 = 2."
    out = split_vernacs(src)
    assert len(out) == 2
    assert out[0].line == 3
    assert out[1].line == 5


def test_split_vernacs_qualified_dot_not_a_terminator():
    # `Nat.add` contains a `.` that must NOT split the vernac.
    src = "Theorem foo : Nat.add 1 1 = 2."
    out = split_vernacs(src)
    assert len(out) == 1
    assert "Nat.add" in out[0].body


def test_split_vernacs_handles_trailing_proof_block():
    src = (
        "Theorem foo : True.\n"
        "Proof.\n"
        "trivial.\n"
        "Qed."
    )
    out = split_vernacs(src)
    bodies = [v.body for v in out]
    assert "Theorem foo : True" in bodies
    assert "Proof" in bodies
    assert "trivial" in bodies
    assert "Qed" in bodies


def test_split_vernacs_ignores_blank_text_between_dots():
    src = ".  .  Theorem foo : True."
    out = split_vernacs(src)
    assert [v.body for v in out] == ["Theorem foo : True"]
