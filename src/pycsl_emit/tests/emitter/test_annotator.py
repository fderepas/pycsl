"""Emitter golden tests.

Each case is a (before, qualname, annotations, expected_after) tuple.
The annotator MUST:
  - Place `#@` lines flush against the `def` (no blank between).
  - Preserve unrelated code and user comments above the function.
  - Replace any prior `#@` block from an earlier run.
"""

from __future__ import annotations

import textwrap

import pytest

from pycsl_emit.emitter import annotate_source, find_function
from pycsl import pure_ast as _past   # installed-package path (works without src/pycsl on sys.path)


def _strip(s: str) -> str:
    return textwrap.dedent(s).lstrip("\n")


def test_top_level_function_no_existing_leading_lines():
    before = _strip("""
        def gcd(a: int, b: int) -> int:
            if b == 0:
                return a
            return gcd(b, a % b)
    """)
    expected = _strip("""
        #@ requires a >= 0 and b >= 0
        #@ ensures a % \\result == 0
        #@ assigns \\nothing
        def gcd(a: int, b: int) -> int:
            if b == 0:
                return a
            return gcd(b, a % b)
    """)
    out = annotate_source(
        before,
        "gcd",
        [
            "requires a >= 0 and b >= 0",
            "ensures a % \\result == 0",
            "assigns \\nothing",
        ],
    )
    assert out == expected


def test_preserves_existing_user_comment_above_def():
    before = _strip("""
        # the canonical euclidean algorithm
        def gcd(a: int, b: int) -> int:
            return a
    """)
    expected = _strip("""
        # the canonical euclidean algorithm
        #@ requires a >= 0
        def gcd(a: int, b: int) -> int:
            return a
    """)
    out = annotate_source(before, "gcd", ["requires a >= 0"])
    assert out == expected


def test_strips_trailing_blank_line_so_annotations_sit_flush():
    """A blank line between user comment and def is preserved above
    the annotation block, but no blank is left between the last `#@`
    and the def itself."""
    before = (
        "# explanation\n"
        "\n"
        "def gcd(a: int, b: int) -> int:\n"
        "    return a\n"
    )
    out = annotate_source(before, "gcd", ["requires a >= 0"])
    # The annotation block must be immediately above `def`:
    assert "#@ requires a >= 0\ndef gcd" in out
    # The user's blank line should be gone — we strip *all* trailing
    # blanks before laying our annotations flush against the def.
    assert "# explanation\n#@ requires a >= 0\ndef gcd" in out


def test_replaces_previous_annotation_block_on_rerun():
    before = _strip("""
        #@ requires a > 0
        #@ assigns \\nothing
        def gcd(a: int, b: int) -> int:
            return a
    """)
    expected = _strip("""
        #@ requires a >= 0 and b >= 0
        #@ ensures \\result >= 0
        def gcd(a: int, b: int) -> int:
            return a
    """)
    out = annotate_source(
        before,
        "gcd",
        ["requires a >= 0 and b >= 0", "ensures \\result >= 0"],
    )
    assert out == expected


def test_method_qualname_inside_class():
    before = _strip("""
        class Calculator:
            def add(self, x: int, y: int) -> int:
                return x + y

            def sub(self, x: int, y: int) -> int:
                return x - y
    """)
    out = annotate_source(
        before,
        "Calculator.sub",
        ["requires x >= y", "ensures \\result >= 0"],
    )
    assert "    #@ requires x >= y\n    #@ ensures \\result >= 0\n    def sub(" in out
    # `add` must remain untouched.
    assert "    def add(self, x: int, y: int) -> int:\n        return x + y" in out


def test_normalizes_inputs_that_already_have_hash_at():
    """Callers may pass `#@ requires ...` or just `requires ...` —
    both should produce the same canonical output."""
    before = "def f(x: int) -> int:\n    return x\n"
    a = annotate_source(before, "f", ["requires x >= 0"])
    b = annotate_source(before, "f", ["#@ requires x >= 0"])
    assert a == b


def test_missing_qualname_raises():
    before = "def gcd(a, b):\n    return a\n"
    with pytest.raises(KeyError):
        annotate_source(before, "does_not_exist", ["requires True"])


def test_unrelated_module_content_untouched():
    before = _strip("""
        import math
        from typing import Tuple

        def helper(x: int) -> int:
            return x + 1

        def gcd(a: int, b: int) -> int:
            return a

        CONSTANT = 42
    """)
    out = annotate_source(before, "gcd", ["requires a >= 0"])
    assert "import math" in out
    assert "from typing import Tuple" in out
    assert "def helper(x: int) -> int:\n    return x + 1" in out
    assert "CONSTANT = 42" in out


def test_locator_finds_nested_function():
    src = _strip("""
        def outer(x: int) -> int:
            def inner(y: int) -> int:
                return y + 1
            return inner(x)
    """)
    module = _past.parse(src)
    match = find_function(module, "outer.inner")
    assert match is not None
    assert match.node.name == "inner"
