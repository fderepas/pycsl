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

# THE MARKER DEFINITION AND THE MARKER -> DEF ATTACHMENT WALK LIVE IN `bin/trusted_markers.py`
# (convergence-metric Phase 3), moved there VERBATIM so that `bin/check-trusted-reasons.py`
# keys its side file off the SAME walk this plane counts with. Two walks that could disagree
# about the population is the bug class this file's own naming note documents. The names are
# re-exported here unchanged:
#   MIRROR, MIN_MIRROR_FILES (40; a floor on the INPUT, never on the metric, gen #4),
#   MARKER (a `#@` line whose first token is `\trusted`; anything else is prose), CONTAINS,
#   _block_marker_line, and iter_trusted_defs (the ast.walk-order enumeration used below).
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from trusted_markers import (  # noqa: E402
    MIRROR, MIN_MIRROR_FILES, MARKER, CONTAINS, _block_marker_line, iter_trusted_defs)


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


def main() -> int:
    emit_dir = None
    argv = sys.argv[1:]
    if "--emit-dir" in argv:
        emit_dir = argv[argv.index("--emit-dir") + 1]

    # --metrics: the CONVERGENCE view of this plane's population (Phase 2 of
    # getting-better/convergence-metric-implement.md). It prints the body-verified fraction
    # computed FROM PROOF VERDICTS, not from the absence of a marker, alongside the 459/484
    # pair this script has always reported. The marker count is KEPT AS A COLUMN and
    # DEMOTED, never deleted -- every historical figure in the campaign is stated in it.
    # This branch is additive: it delegates and returns, and cannot alter the gate verdict
    # that the plane battery depends on.
    #
    # Phase 3 adds the REASON HISTOGRAM (why each marker is trusted), delegated to
    # `bin/check-trusted-reasons.py`, which reads the out-of-band side file
    # `getting-better/trusted-reasons.tsv` against the SAME marker walk this plane counts
    # with. It runs the full reasons check, so side-file drift shows up here too, and the
    # exit code is the verified-fraction rc if that failed, else the reasons rc. Under
    # `--json` the histogram goes to STDERR so stdout stays one parseable JSON document.
    # The default (non --metrics) path below is untouched.
    if "--metrics" in argv:
        import subprocess as _sp
        _here = os.path.dirname(os.path.abspath(__file__))
        vf = os.path.join(_here, "verified-fraction.py")
        rest = [a for a in argv if a != "--metrics"]
        rc = _sp.call([sys.executable, vf] + rest)
        sys.stdout.flush()
        rc_reasons = _sp.call([sys.executable, os.path.join(_here, "check-trusted-reasons.py")],
                              stdout=(sys.stderr if "--json" in rest else None))
        return rc or rc_reasons

    matched_mlw = 0

    markers = 0
    grep_hits = 0
    offset_lines = []
    unattached = []
    attached = 0
    stale = []

    # ZERO-INPUT GUARD (gen #4, the #44 rule). This plane owns the campaign's HEADLINE
    # number and had no floor of any kind: a broken glob, a moved MIRROR or a partial
    # checkout printed "[+] trusted-directives: OK" with `markers 0`, which reads as total
    # success for a campaign whose whole goal is to drive markers DOWN. The guard is on the
    # POPULATION (mirror .py files, a stable ~53) and deliberately NOT on the marker count,
    # because that count is SUPPOSED to fall and a floor there would fight the work.
    _mirror_files = sorted(glob.glob(os.path.join(MIRROR, "**/*.py"), recursive=True))
    if len(_mirror_files) < MIN_MIRROR_FILES:
        print("[!] trusted-directives: REFUSING — only %d mirror .py file(s) found under "
              "%s, expected at least %d. THIS IS A REFUSAL, NOT A PASS."
              % (len(_mirror_files), MIRROR, MIN_MIRROR_FILES))
        sys.exit(2)
    for f in _mirror_files:
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
        for node, m, _qualname in iter_trusted_defs(tree, lines):
            claimed.add(m)
            trusted_defs.append(node.name)
        attached += len(claimed)
        for i in sorted(marker_idx - claimed):
            unattached.append((rel, i + 1, lines[i].strip()[:70]))

        if emit_dir:
            # TWO NAMING CONVENTIONS EXIST IN THIS REPO AND THEY DISAGREE (gen #4). This
            # plane mapped a source to its emission with `replace("/", "__")` — TWO
            # underscores — while every OTHER --emit-dir consumer
            # (check-yield-erasure, check-shadowed-selfcalls, check-trusted-frame-honesty,
            # check-computed-rhs-erasure, check-avatar-frame-parity) uses
            # `replace(os.sep, "_")` — ONE. So no single directory could feed them all, and
            # the failure was SILENT IN BOTH DIRECTIONS: measured, the single-underscore
            # directory made check-yield-erasure report 0 generators against a true 3 (a
            # FALSE GREEN) and check-trusted-frame-honesty report "RATCHET BROKEN — 48 > 0"
            # (a FALSE RED). Accept either spelling here so a shared emission is possible.
            _stem = rel[:-3]
            for _cand in (_stem.replace("/", "__"), _stem.replace(os.sep, "_")):
                mlw = os.path.join(emit_dir, _cand + ".mlw")
                if os.path.exists(mlw):
                    break
            if os.path.exists(mlw):
                matched_mlw += 1
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
        # A STALE COUNT OF 0 FROM AN EMPTY DIRECTORY IS NOT A PASS (gen #4, the #44 rule).
        # DEMONSTRATED before this guard existed: pointing --emit-dir at an EMPTY directory
        # printed "stale ...: 0" and "[+] trusted-directives: OK", indistinguishable from a
        # clean sweep of all 53 mirrors. The whole point of this half of the plane is to
        # catch a `\trusted` marker that is not actually taking effect, and it was reporting
        # success for having opened no files at all.
        if matched_mlw < MIN_MIRROR_FILES:
            print(f"[!] trusted-directives: REFUSING — --emit-dir matched only "
                  f"{matched_mlw} of {len(_mirror_files)} mirror source(s); expected at "
                  f"least {MIN_MIRROR_FILES}. The directory is empty, stale, or uses a "
                  f"naming convention this plane does not recognise. "
                  f"THIS IS A REFUSAL, NOT A PASS.")
            sys.exit(2)
        print(f"    stale (trusted but emitted as a definition): {len(stale)} "
              f"(over {matched_mlw} matched emission(s))")
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
