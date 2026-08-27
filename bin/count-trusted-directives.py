#!/usr/bin/env python3
r"""count-trusted-directives.py — the AUTHORITATIVE `\trusted` count, and the
reconciliation against the grep the campaign has always quoted.

WHY THIS EXISTS. Every window of the self-TCB-reduction campaign reports its progress as

    grep -rcF '#@ \trusted' src/self-annotate/src --include=*.py   (summed)

That command counts LINES CONTAINING the substring, not MARKERS. Measured 2026-08-27
(relaunch #4): **25 of the hits are not markers at all**. They are one line of boilerplate
MODULE DOCSTRING, repeated verbatim in 25 mirror files:

    annotated `#@ \trusted reviewer: pycsl-self-annotate`; bodies ...

So the campaign's absolute figure has always been 25 too high. Every DELTA ever reported is
correct — the offset is constant while the mirror file set is — but the absolute number is
not, and any statement of the form "the floor is N" inherits the error.

WHAT THIS REPORTS
  markers      the number of real `#@ \trusted` DIRECTIVES (line starts with `#@`, the
               marker is the first token) — the number that should be quoted
  grep         the historical `grep -cF` figure, for continuity with every prior window
  offset       grep - markers, itemised, so a CHANGE in the offset is visible rather than
               silently folded into the count
  attached     markers that sit in the `#@`/comment/decorator block directly above a `def`
               — an UNATTACHED marker is a defect (it annotates nothing) and exits 1

SECOND CHECK — STALE MARKERS (the converse of `check-untrusted-emitted.py`). That gate asks
"is every UN-trusted function really emitted as a definition?" (the auto-trust valve hazard).
This one asks the opposite: "is any TRUSTED function nonetheless emitted as a real
definition?" — which would mean the marker asserts an assumption that is not being made, and
the count is OVERSTATED. Several `_py_expr_*` / `_py_stmt_*` handlers are emitted by bespoke
whole-body lowerings in `module6_whyml/functions.py` regardless of their marker, so this is a
live possibility, not a theoretical one. Requires an emitted mirror tree (`--emit-dir`);
skipped without one.

BASELINE 2026-08-27: markers **592**, grep **617**, offset **25** (all the docstring line),
0 unattached, 0 stale.

BEWARE (this bit the author): a walk upward from a `def` through the comment block must
require the marker to be the line's FIRST token. Prose comments that MENTION `\trusted`
("...unlike the same clause on a `#@ \trusted` stub...") otherwise read as markers — that
false positive reported six converted `_Parser` methods as trusted-but-defined, all of which
evaporated under strict matching. Same family as the four naming traps documented in
`check-untrusted-emitted.py`.

Usage:  bin/count-trusted-directives.py [--emit-dir DIR]
Exit 1 on an unattached marker or a stale (trusted-but-defined) function.
"""
from __future__ import annotations

import ast
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIRROR = os.path.join(ROOT, "src/self-annotate/src")

# A MARKER is a `#@` line whose first token is `\trusted`. Anything else that merely
# contains the substring is prose.
MARKER = re.compile(r"^#@\s*\\trusted\b")
CONTAINS = "#@ \\trusted"


# Declaration scanners. The identifier is CAPTURED and then tested, rather than being
# spliced into the pattern — otherwise regex backtracking makes the Why3 KEYWORDS part of
# the name. Measured: `[A-Za-z0-9_]*rec\b` after an optional ` rec` happily matches the
# `rec` of `let rec <something-else>`, so a mirror function named `rec` (the lifted nested
# `def rec` in `module6_whyml/statements.py`) was reported as trusted-but-defined twice.
# Same family as the four naming traps documented in `check-untrusted-emitted.py`.
LET_DECL = re.compile(
    r"^\s*(?:let|with)\b(?:\s+rec\b)?(?:\s+function\b)?\s+(?P<n>[A-Za-z0-9_]+)", re.M)
VAL_DECL = re.compile(
    r"^\s*val\b(?:\s+function\b)?(?:\s+rec\b)?\s+(?P<n>[A-Za-z0-9_]+)", re.M)
WHYML_KEYWORDS = {"rec", "function", "constant", "predicate", "ghost", "lemma", "type",
                  "exception", "val", "let", "with"}


def _emitted_as(txt, pattern, base):
    """The emitted declaration text for `base`, or None. A declaration counts when its
    identifier IS the Python name or is that name with an emitter-added prefix
    (`<class>__<name>`), never when it is a Why3 keyword."""
    for m in pattern.finditer(txt):
        n = m.group("n")
        if n in WHYML_KEYWORDS:
            continue
        if n == base or n.endswith("_" + base):
            return m.group(0).strip()[:70]
    return None


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


def main() -> int:
    emit_dir = None
    argv = sys.argv[1:]
    if "--emit-dir" in argv:
        emit_dir = argv[argv.index("--emit-dir") + 1]

    markers = 0
    grep_hits = 0
    offset_lines = []
    unattached = []
    attached = 0
    stale = []

    for f in sorted(glob.glob(os.path.join(MIRROR, "**/*.py"), recursive=True)):
        rel = os.path.relpath(f, MIRROR)
        src = open(f).read()
        lines = src.split("\n")
        marker_idx = set()
        for i, l in enumerate(lines):
            if CONTAINS in l:
                grep_hits += 1
                if MARKER.match(l.strip()):
                    marker_idx.add(i)
                else:
                    offset_lines.append((rel, i + 1, l.strip()[:70]))
        markers += len(marker_idx)

        try:
            tree = ast.parse(src)
        except SyntaxError:
            continue

        claimed = set()
        trusted_defs = []
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            m = _block_marker_line(lines, node.lineno)
            if m is not None:
                claimed.add(m)
                trusted_defs.append(node.name)
        attached += len(claimed)
        for i in sorted(marker_idx - claimed):
            unattached.append((rel, i + 1, lines[i].strip()[:70]))

        if emit_dir:
            mlw = os.path.join(emit_dir, rel.replace("/", "__")[:-3] + ".mlw")
            if os.path.exists(mlw):
                txt = open(mlw).read()
                for name in trusted_defs:
                    let = _emitted_as(txt, LET_DECL, name)
                    val = _emitted_as(txt, VAL_DECL, name)
                    if let and not val:
                        stale.append((rel, name, let))

    print(f"[*] trusted-directives: markers {markers} · grep-substring {grep_hits} · "
          f"offset {grep_hits - markers} · attached {attached} · unattached {len(unattached)}")
    if offset_lines:
        seen = {}
        for rel, ln, text in offset_lines:
            seen.setdefault(text, []).append(rel)
        print("    OFFSET (substring hits that are NOT markers):")
        for text, files in sorted(seen.items()):
            print(f"      {len(files):3d}x  {text}")
    for u in unattached:
        print(f"    [!] UNATTACHED marker (annotates nothing): {u}")
    if emit_dir:
        print(f"    stale (trusted but emitted as a definition): {len(stale)}")
        for s in stale:
            print(f"      [!] {s}")
    bad = bool(unattached) or bool(stale)
    if bad:
        print("[!] trusted-directives: FAIL")
        return 1
    print("[+] trusted-directives: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
