"""Lexical preprocessing for Lean 4 source.

Lean 4 comment syntax mirrors Coq's `(*...*)` *and* adds C-style
single-line `--` comments. Both nested forms are supported.

`strip_comments(src)` collapses comments to whitespace (preserving
newlines so source-line numbers stay intact).

Lean 4 doesn't have a single token like Coq's `.` to delimit top-level
commands — declarations are separated by their structural keywords
(`theorem`, `def`, `lemma`, …). `split_decls(src)` returns
`Declaration` records by scanning for those keywords at column 0,
preserving the raw text body so downstream regex-based dispatch can
classify each declaration.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Declaration:
    """One top-level Lean declaration (raw body, line-anchored).

    `body` is the text from the leading keyword through the end of the
    declaration (just before the next top-level keyword).
    `line` is the 1-indexed source line of the first character of body.
    """
    body: str
    line: int


def strip_comments(src: str) -> str:
    """Remove `(* ... *)` blocks (nestable) and `-- ...` line comments.

    String literals are passed through unchanged. Whitespace replaces
    each comment so source-line numbers stay accurate.
    """
    out: list[str] = []
    i = 0
    depth = 0      # `(* *)` nesting depth
    in_string = False
    while i < len(src):
        ch = src[i]
        nxt = src[i + 1] if i + 1 < len(src) else ""

        # String literal passthrough.
        if depth == 0 and not in_string and ch == '"':
            in_string = True
            out.append(ch)
            i += 1
            continue
        if in_string:
            if ch == "\\" and i + 1 < len(src):
                out.append(ch)
                out.append(src[i + 1])
                i += 2
                continue
            if ch == '"':
                in_string = False
            out.append(ch)
            i += 1
            continue

        # Block comment.
        if ch == "(" and nxt == "*":
            depth += 1
            out.append("  ")
            i += 2
            continue
        if ch == "*" and nxt == ")" and depth > 0:
            depth -= 1
            out.append("  ")
            i += 2
            continue
        if depth > 0:
            out.append("\n" if ch == "\n" else " ")
            i += 1
            continue

        # Line comment (only at depth 0). Replace through end of line.
        if ch == "-" and nxt == "-":
            j = i
            while j < len(src) and src[j] != "\n":
                out.append(" ")
                j += 1
            i = j
            continue

        out.append(ch)
        i += 1
    return "".join(out)


# Top-level decl keywords. Matched at column 0 (after a newline) or at
# the start of the file. We don't anchor on attribute prefixes here —
# `@[pycsl_spec ...]` may sit on its own line before the keyword; the
# caller's regex handles that.
_DECL_HEADS = (
    "theorem", "lemma", "proposition", "example",
    "def", "noncomputable", "partial", "abbrev",
)


_DECL_START_RE = re.compile(
    r"(?m)^(?:@\[[^\]]*\]\s*)*(?:" + "|".join(_DECL_HEADS) + r")\b"
)


def split_decls(src: str) -> list[Declaration]:
    """Split top-level Lean declarations.

    The strategy: scan for `(?m)^<keyword>` matches and slice the source
    between them. Optional leading `@[attr]` blocks are absorbed into
    the declaration that follows.

    Each `Declaration.body` runs from its opening keyword (or its
    `@[...]` attribute prefix) up to — but not including — the next
    top-level keyword's column-0 anchor.
    """
    matches = list(_DECL_START_RE.finditer(src))
    out: list[Declaration] = []
    for idx, m in enumerate(matches):
        start = m.start()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(src)
        body = src[start:end].rstrip()
        line = src[:start].count("\n") + 1
        if body:
            out.append(Declaration(body=body, line=line))
    return out
