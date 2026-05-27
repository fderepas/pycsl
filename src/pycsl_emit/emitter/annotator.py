"""Insert `#@` annotation lines immediately before a `def`.

The placement rule from `config/skills/pycsl-annotate/SKILL.md`:

  > Place contracts as `#@` comments immediately before the `def`
  > keyword, with NO blank lines between the last `#@` line and `def`.

This module guarantees that rule: the emitted `leading_lines` end with a
contiguous block of `#@` lines and no trailing `EmptyLine` before the
function.

Existing non-`#@` leading lines (regular comments, blank lines authored
by the user) are preserved above the new annotation block. Existing
`#@` lines on the same function are replaced — re-running the tool
produces a clean result rather than accumulating duplicates.
"""

from __future__ import annotations

from typing import Iterable, Sequence

import libcst as cst

from .locator import find_function, FunctionMatch


_HASH_AT = "#@"


def annotate_function(
    module: cst.Module,
    qualname: str,
    annotations: Sequence[str],
    *,
    prefix_comments: Sequence[str] = (),
) -> cst.Module:
    """Return a new module with `annotations` attached to `qualname`.

    `annotations` is a list of strings *without* the leading `#@`; the
    annotator prepends that token plus a single space.

    `prefix_comments` is an optional list of regular Python comments
    (the leading `#` is added if missing) that go *above* the `#@`
    block. Used by `pycsl_bridge` to emit `# proof rocq: <thm>` /
    `# proof lean: <thm>` traceability lines without invoking the
    contract grammar.

    Raises `KeyError` if the qualname doesn't resolve.
    """
    match = find_function(module, qualname)
    if match is None:
        raise KeyError(f"no function {qualname!r} in module")

    # Special case: libcst stores leading lines for the *very first* module
    # statement inside `Module.header`, not on the statement itself. When the
    # target def is module.body[0], we merge header + leading_lines so the
    # rebuild logic sees a unified leading-line sequence.
    is_first_in_module = (
        match.parent_body is module
        and match.index == 0
        and len(module.header) > 0
    )

    if is_first_in_module:
        combined = tuple(module.header) + tuple(match.node.leading_lines)
        new_leading = _rebuild_leading_lines(combined, annotations, prefix_comments)
        new_func = match.node.with_changes(leading_lines=new_leading)
        new_body = list(module.body)
        new_body[0] = new_func
        return module.with_changes(header=(), body=tuple(new_body))

    new_func = match.node.with_changes(
        leading_lines=_rebuild_leading_lines(
            match.node.leading_lines, annotations, prefix_comments
        )
    )

    new_body = list(match.parent_body.body)
    new_body[match.index] = new_func
    new_parent = match.parent_body.with_changes(body=tuple(new_body))

    if match.parent_body is module:
        return new_parent  # type: ignore[return-value]
    # Nested case: rebuild ancestors. libcst doesn't let us mutate in place,
    # so we run a transformer that replaces the matched body wholesale.
    return module.visit(_BodyReplacer(match.parent_body, new_parent))


def annotate_source(
    source: str,
    qualname: str,
    annotations: Sequence[str],
    *,
    prefix_comments: Sequence[str] = (),
) -> str:
    """Convenience: parse `source`, annotate, return the new source string."""
    module = cst.parse_module(source)
    return annotate_function(
        module, qualname, annotations, prefix_comments=prefix_comments
    ).code


# ──────────────────────────────────────────────────────────────────────


def _rebuild_leading_lines(
    existing: Sequence[cst.EmptyLine],
    annotations: Sequence[str],
    prefix_comments: Sequence[str] = (),
) -> tuple[cst.EmptyLine, ...]:
    """Produce `(preserved_user_lines, prefix_comments, annotation_block)`
    as one tuple.

    Strategy:
      1. Strip any *trailing* `#` proof-attribution comments from
         `existing` (output of a previous bridge run; they're being
         replaced).
      2. Strip any *trailing* `#@` lines from what remains (output of a
         previous converter run).
      3. Strip any *trailing* blank lines so the new content sits flush
         against the def.
      4. Append `prefix_comments` as regular `#` lines.
      5. Append the `#@` annotation block.
    """
    preserved: list[cst.EmptyLine] = list(existing)

    # Strip trailing `#@` lines (output of a previous converter run).
    while preserved and _is_hash_at(preserved[-1]):
        preserved.pop()

    # Strip trailing blank lines so the new content sits flush against the def.
    while preserved and _is_blank(preserved[-1]):
        preserved.pop()

    new_prefix = [_make_plain_comment(text) for text in prefix_comments]
    new_block = [_make_hash_at_line(text) for text in annotations]
    return tuple(preserved) + tuple(new_prefix) + tuple(new_block)


def _is_hash_at(line: cst.EmptyLine) -> bool:
    return line.comment is not None and line.comment.value.startswith(_HASH_AT)


def _is_blank(line: cst.EmptyLine) -> bool:
    return line.comment is None


def _make_hash_at_line(text: str) -> cst.EmptyLine:
    """Build an `EmptyLine` carrying a `#@ <text>` comment.

    `text` is the bare contract content (no leading `#@`, no leading
    whitespace). Callers pass things like `"requires x >= 0"`.
    """
    stripped = text.strip()
    # Tolerate callers who pre-prefix with `#@` so the API is robust to
    # both styles. Normalize to a canonical `#@ ` prefix.
    if stripped.startswith(_HASH_AT):
        stripped = stripped[len(_HASH_AT):].lstrip()
    return cst.EmptyLine(comment=cst.Comment(f"{_HASH_AT} {stripped}"))


def _make_plain_comment(text: str) -> cst.EmptyLine:
    """Build an `EmptyLine` carrying a regular `# <text>` comment.

    Used for proof-attribution lines (pycsl_bridge). The caller's
    `text` may or may not include the leading `#`; we normalize to one.
    """
    stripped = text.lstrip()
    if stripped.startswith("#"):
        return cst.EmptyLine(comment=cst.Comment(stripped))
    return cst.EmptyLine(comment=cst.Comment(f"# {stripped}"))


class _BodyReplacer(cst.CSTTransformer):
    """Replace a specific IndentedBlock/Module node by identity.

    Used for nested functions and class methods, where we need to
    swap the inner body inside an ancestor that libcst won't let us
    mutate directly.
    """

    def __init__(
        self,
        original: cst.IndentedBlock | cst.Module,
        replacement: cst.IndentedBlock | cst.Module,
    ) -> None:
        super().__init__()
        self._original = original
        self._replacement = replacement

    def on_leave(self, original_node, updated_node):
        if original_node is self._original:
            return self._replacement
        return updated_node
