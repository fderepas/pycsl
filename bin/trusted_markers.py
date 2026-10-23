#!/usr/bin/env python3
r"""trusted_markers.py — THE ONE `\trusted` marker -> def attachment walk, importable.

WHY THIS FILE EXISTS. Two consumers need to know which `def` a `#@ \trusted` marker governs:

  * `bin/count-trusted-directives.py` — the AUTHORITATIVE marker count (markers / grep /
    offset / attached / unattached, plus the stale-marker half under `--emit-dir`);
  * `bin/check-trusted-reasons.py` — the out-of-band reason taxonomy
    (`getting-better/trusted-reasons.tsv`), which keys one row per live marker.

If each carried its own walk, the two could disagree about the population, and a
disagreement between two walks over the same tree is exactly the class of bug this repo
keeps finding (the one-vs-two-underscore `--emit-dir` naming split documented in
`count-trusted-directives.py`; the prose-mention-reads-as-marker trap below). So the
constants and the attachment predicate live HERE, once, and both scripts import them.
`count-trusted-directives.py`'s output and exit code are unchanged by the factoring — the
code below is moved verbatim, not rewritten.

BEWARE (inherited from count-trusted-directives.py): a walk upward from a `def` through the
comment block must require the marker to be the line's FIRST token. Prose comments that
MENTION `\trusted` otherwise read as markers.

QUALNAMES (used by the reason side file, not by the count). `iter_trusted_defs` enumerates
functions in `ast.walk` order — the order the count plane has always used, so its stale-row
print order cannot move — and gives each one its FULL nested qualname: every enclosing
`class` / `def` / `async def` name joined with `.` (`Class.method.inner`; no `<locals>`).
Qualnames can collide within one file (the lifted nested `def rec` appears twice in
`module6_whyml/statements.py`). COLLISION RULE: among ALL function defs in the file that share
a qualname — trusted or not — the first in source order `(lineno, col_offset)` keeps the bare
qualname, the second gets `#2`, the third `#3`, and so on. Numbering over ALL defs (not only
trusted ones) is deliberate: the campaign's common operation is CONVERTING a stub, and
converting the first `rec` must not silently renumber a still-trusted `rec#2` to `rec`.
"""
from __future__ import annotations

import ast
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIRROR = os.path.join(ROOT, "src/self-annotate/src")
MIN_MIRROR_FILES = 40   # true population 53; a floor on the INPUT, never on the metric (gen #4)

# A MARKER is a `#@` line whose first token is `\trusted`. Anything else that merely
# contains the substring is prose.
MARKER = re.compile(r"^#@\s*\\trusted\b")
CONTAINS = "#@ \\trusted"

_FUNC = (ast.FunctionDef, ast.AsyncFunctionDef)
_SCOPE = (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)


def _block_marker_line(lines, lineno):
    """Index of the `\trusted` marker governing the def at `lineno`, or None.

    Walks up through the contiguous `#@` / `#` / decorator / blank block, exactly as
    `check-untrusted-emitted.py` does — plain comments and blank lines are part of the
    block (omitting them stops the walk at any justification comment and reads a trusted
    stub as un-trusted)."""
    i = lineno - 2
    while i >= 0:
        s = lines[i].strip()
        if s.startswith("#@") or s.startswith("#") or s.startswith("@") or s == "":
            if MARKER.match(s):
                return i
            i -= 1
            continue
        return None
    return None


def qualnames(tree):
    """{id(function node): disambiguated full qualname} for every def in `tree`."""
    parent = {}
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            parent[child] = node
    raw = {}
    for node in ast.walk(tree):
        if not isinstance(node, _FUNC):
            continue
        parts = [node.name]
        p = parent.get(node)
        while p is not None:
            if isinstance(p, _SCOPE):
                parts.append(p.name)
            p = parent.get(p)
        raw[node] = ".".join(reversed(parts))
    by_name = {}
    for node, q in raw.items():
        by_name.setdefault(q, []).append(node)
    out = {}
    for q, nodes in by_name.items():
        for k, node in enumerate(sorted(nodes, key=lambda n: (n.lineno, n.col_offset))):
            out[id(node)] = q if k == 0 else "%s#%d" % (q, k + 1)
    return out


def iter_trusted_defs(tree, lines):
    """Yield `(node, marker_index, qualname)` for every def governed by a `\trusted` marker,
    in `ast.walk` order."""
    names = qualnames(tree)
    for node in ast.walk(tree):
        if not isinstance(node, _FUNC):
            continue
        m = _block_marker_line(lines, node.lineno)
        if m is not None:
            yield node, m, names[id(node)]
