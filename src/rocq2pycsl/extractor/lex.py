"""Lexical preprocessing for Coq source.

Two helpers shared by the Lark backend:

  strip_comments(src)  — remove `(* ... *)` blocks, nested-comment safe
  split_vernacs(src)   — split on vernac terminators (`.` followed by
                         whitespace or EOF), preserving qualified names
                         like `Nat.add`

These run before Lark sees any input. They keep the Lark grammar small
because we don't need to encode comment handling or top-level command
boundaries in the grammar itself.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Vernac:
    """One Coq vernacular command (its body, excluding the trailing `.`).

    `line` is the 1-indexed source line of the first character of `body`.
    """
    body: str
    line: int


def strip_comments(src: str) -> str:
    """Remove `(* ... *)` blocks, properly nested.

    String literals (`"..."`) are passed through unchanged. We're
    permissive about everything else — the goal is to feed the
    Lark grammar text with no comment noise.

    Whitespace replaces each comment so source-line numbers stay
    accurate (newlines inside the comment are preserved).
    """
    out: list[str] = []
    i = 0
    depth = 0
    in_string = False
    while i < len(src):
        ch = src[i]
        nxt = src[i + 1] if i + 1 < len(src) else ""

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
            # Inside a comment — replace non-newline chars with spaces.
            out.append("\n" if ch == "\n" else " ")
            i += 1
            continue
        out.append(ch)
        i += 1
    return "".join(out)


# A vernac terminator is `.` followed by whitespace or EOF, *not* inside
# a qualified identifier like `Nat.add`. The lookahead handles that.
_VERNAC_TERMINATOR = re.compile(r"\.(?=\s|$)")


def split_vernacs(src: str) -> list[Vernac]:
    """Split Coq source (comments already stripped) into Vernac records.

    Empty/whitespace-only chunks are dropped.
    """
    out: list[Vernac] = []
    pos = 0
    line = 1
    for m in _VERNAC_TERMINATOR.finditer(src):
        chunk = src[pos : m.start()]
        # Compute the starting line of this chunk by counting newlines
        # in everything we've consumed so far.
        first_nonspace = _strip_leading_blank_lines(chunk)
        body = chunk[first_nonspace:].strip()
        if body:
            start_line = line + _count_newlines(chunk[:first_nonspace])
            out.append(Vernac(body=body, line=start_line))
        line += _count_newlines(src[pos : m.end()])
        pos = m.end()
    # Anything after the final `.` is ignored (typical Coq files end with `.`).
    return out


def _strip_leading_blank_lines(chunk: str) -> int:
    """Return the index in `chunk` of the first non-whitespace character."""
    for idx, ch in enumerate(chunk):
        if not ch.isspace():
            return idx
    return len(chunk)


def _count_newlines(s: str) -> int:
    return s.count("\n")
