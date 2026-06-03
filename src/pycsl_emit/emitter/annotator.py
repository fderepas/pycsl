"""Insert `#@` annotation lines immediately before a `def` — libcst-free.

Placement rule (`config/skills/pycsl-annotate/SKILL.md`): contracts go as `#@`
comments immediately before the construct, with NO blank line between the last
`#@` line and the `def`. Existing user comments/blank lines above are preserved;
a previous run's `#@` block is replaced (re-running is idempotent).

Implementation: parse with the pure-Python `pure_ast` (positions only), locate
the target function, and splice the annotation lines into the source TEXT just
above the construct — leaving every other byte untouched. This is strictly more
faithful than a parse→re-render round-trip (it only edits the leading region)
and removes the libcst dependency from this package's hot path.
"""

from __future__ import annotations

from typing import Sequence

try:                                  # verify-pipeline / tests: src/pycsl on sys.path
    import pure_ast as ast
except ModuleNotFoundError:           # installed console scripts (rocq2pycsl, …)
    from pycsl import pure_ast as ast

from .locator import find_function, FunctionMatch  # noqa: F401

_HASH_AT = "#@"


def annotate_source(
    source: str,
    qualname: str,
    annotations: Sequence[str],
    *,
    prefix_comments: Sequence[str] = (),
) -> str:
    """Return `source` with `annotations` attached to `qualname`.

    `annotations` are bare contract strings (no leading `#@`; the token + one
    space is prepended; a pre-supplied `#@ ` is tolerated). `prefix_comments`
    are plain `#` comments placed *above* the `#@` block (used by pycsl_bridge
    for `# proof rocq: …` traceability). Raises `KeyError` if `qualname` doesn't
    resolve.
    """
    match = find_function(ast.parse(source), qualname)
    if match is None:
        raise KeyError(f"no function {qualname!r} in module")
    node = match.node

    # Insertion point: the construct's first line — its first decorator if any,
    # else the `def` line (annotating before the decorators matches where the
    # contract harvester reads leading lines from).
    decs = getattr(node, "decorator_list", None) or []
    ins = min([d.lineno for d in decs], default=node.lineno) - 1   # 0-based

    lines = source.splitlines(keepends=True)
    indent = lines[ins][: len(lines[ins]) - len(lines[ins].lstrip())] if ins < len(lines) else ""
    eol = "\n"
    if ins < len(lines) and lines[ins].endswith("\r\n"):
        eol = "\r\n"

    # Strip the previous run's trailing `#@` block, then any trailing blank
    # lines, so the new block sits flush against the construct. Preserve
    # everything above (user comments, code).
    j = ins
    while j - 1 >= 0 and _is_hash_at(lines[j - 1]):
        j -= 1
    while j - 1 >= 0 and lines[j - 1].strip() == "":
        j -= 1

    block = [f"{indent}{_plain(c)}{eol}" for c in prefix_comments]
    block += [f"{indent}{_HASH_AT} {_norm(a)}{eol}" for a in annotations]
    return "".join(lines[:j] + block + lines[ins:])


def _is_hash_at(line: str) -> bool:
    return line.strip().startswith(_HASH_AT)


def _norm(text: str) -> str:
    """Bare contract content — tolerate a pre-supplied `#@` prefix."""
    s = text.strip()
    if s.startswith(_HASH_AT):
        s = s[len(_HASH_AT):].lstrip()
    return s


def _plain(text: str) -> str:
    """Normalize a prefix comment to a single leading `#`."""
    s = text.lstrip()
    return s if s.startswith("#") else f"# {s}"
