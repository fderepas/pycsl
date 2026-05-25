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
) -> cst.Module:
    """Return a new module with `annotations` attached to `qualname`.

    `annotations` is a list of strings *without* the leading `#@`; the
    annotator prepends that token plus a single space.

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
        new_leading = _rebuild_leading_lines(combined, annotations)
        new_func = match.node.with_changes(leading_lines=new_leading)
        new_body = list(module.body)
        new_body[0] = new_func
        return module.with_changes(header=(), body=tuple(new_body))

    new_func = match.node.with_changes(
        leading_lines=_rebuild_leading_lines(match.node.leading_lines, annotations)
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
) -> str:
    """Convenience: parse `source`, annotate, return the new source string."""
    module = cst.parse_module(source)
    return annotate_function(module, qualname, annotations).code


# ──────────────────────────────────────────────────────────────────────


def _rebuild_leading_lines(
    existing: Sequence[cst.EmptyLine],
    annotations: Sequence[str],
) -> tuple[cst.EmptyLine, ...]:
    """Produce `(preserved_user_lines, annotation_block)` as one tuple.

    Strategy:
      1. Strip any *trailing* `#@` lines from `existing` (those were
         emitted by a previous run; they're being replaced).
      2. Strip any *trailing* blank lines from what remains (we want no
         gap between the user's comments and our annotation block).
      3. Build the annotation block: one `#@ <line>` per annotation, no
         blank line at the end.
    """
    preserved: list[cst.EmptyLine] = list(existing)

    # Strip trailing `#@` lines (output of a previous run).
    while preserved and _is_hash_at(preserved[-1]):
        preserved.pop()

    # Strip trailing blank lines so the `#@` block sits flush against the def.
    while preserved and _is_blank(preserved[-1]):
        preserved.pop()

    new_block = [_make_hash_at_line(text) for text in annotations]
    return tuple(preserved) + tuple(new_block)


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
