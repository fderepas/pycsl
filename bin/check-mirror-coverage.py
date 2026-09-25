#!/usr/bin/env python3
r"""check-mirror-coverage.py — THE PLANE THE METRIC STRUCTURALLY CANNOT SEE.

`bin/count-trusted-directives.py` counts `#@ \trusted` markers in the MIRROR. That number
answers "how much of what the mirror models is assumed rather than proved". It cannot answer
"how much of the live emitter the mirror models AT ALL", because a live function with no
mirror counterpart carries no marker to count. It is not trusted; it is ABSENT.

`bin/self-annotate-mirror-check.sh` walks the other direction — it reports MIRROR-ONLY defs
(drift where the mirror has something the source does not). Nothing measured live-only defs.

FIRST MEASUREMENT (#43): of 1820 live functions in the 49 files that HAVE a mirror,
**550 (30.2%) have no mirror counterpart**, concentrated in the big emitters —
`module6_whyml/expressions.py` 142, `functions.py` 97, `statements.py` 92, `preamble.py` 71,
`frontend/Module5_IREmitter.py` 35. A further 36 live files have no mirror at all.

WHAT THIS IS AND IS NOT. It is NOT an unsoundness: an unmirrored function is simply outside
the self-verification perimeter, exactly like a file that is not mirrored. It IS a limit on
what the headline number means, and the honest way to hold that limit is a ratchet that can
only shrink — so converting a `\trusted` stub is progress, and quietly adding an unmirrored
live helper beside it is not.

Route #15 is the concrete case that motivated this: its Module 6 emitter
`_emit_init_contract_checks` is live-only. That is sound today (it is reachable only from
`transpile` / `_emit_prefunctions_infra`, both `\trusted` in the mirror, so the verified
perimeter is unchanged in shape) — but it is exactly the kind of addition that should be
COUNTED rather than invisible.

Usage:  bin/check-mirror-coverage.py [--list]
Exit 1 if the unmirrored count exceeds the ratchet.
"""
from __future__ import annotations

import ast
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIVE = os.path.join(ROOT, "src/pycsl")
MIRROR = os.path.join(ROOT, "src/self-annotate/src")

# (#43) FIRST MEASUREMENT. 550 live defs in mirrored files have no mirror counterpart, and
# 41 live files have no mirror at all (the 36 in the first hand-census excluded def-less
# files; this script counts every .py, which is the honest denominator). Both may go DOWN,
# never up.
# (#49, relaunch #55) TIGHTENED 550 -> 549. The plane had been reporting
# "549 < ratchet 550 — lower the constant" and nobody had. That one slot of slack is not
# free: route #60's repair added ONE nested helper `def` to `_reset_function_state`,
# which silently consumed it, and the whole 31-plane battery stayed GREEN because the
# comparison is `>`. The defect only surfaced when a second repair added two more and
# pushed the count to 552. A ratchet with headroom cannot see the first regression that
# uses it up, so it is lowered to the measured truth here and the two repairs were
# rewritten to use no nested `def` at all.
MAX_UNMIRRORED_DEFS = 549
MAX_UNMIRRORED_FILES = 41

# (#49) gen #31 — **THE CAMPAIGN'S OWN HEADLINE, MADE A RATCHET.** This is a TCB-REDUCTION
# driver: the number it exists to lower is the count of `\trusted` mirror functions, and
# until now NOTHING MEASURED IT. The handoff files carry "`\trusted` markers 460
# (unchanged)" forward from generation to generation, and **no counting rule reproduces
# 460**: `#@ \trusted reviewer:` markers are 485, functions whose leading `#@` block carries
# `\trusted` are 487, all `\trusted` occurrences are 596, and excluding `pycsl.py` gives
# 454. A headline nobody can recompute is a headline nobody can be wrong about.
#
# THE RULE, stated so it is reproducible: a `FunctionDef` under `src/self-annotate/src`
# whose immediately-preceding comment block contains `\trusted`. Measured 487.
#
# It is a CEILING, because the campaign's direction is down. A conversion that retires a
# stub lowers it and the ratchet must be lowered in the same commit — which is the same
# contract every other ratchet here makes, and the reason to have one at all.
MAX_TRUSTED_FUNCS = 487


def _defs(root):
    out = {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d != "__pycache__"]
        for f in sorted(filenames):
            if not f.endswith(".py"):
                continue
            p = os.path.join(dirpath, f)
            rel = os.path.relpath(p, root)
            try:
                tree = ast.parse(open(p, encoding="utf-8").read())
            except (SyntaxError, UnicodeDecodeError):
                continue
            # `ast.AsyncFunctionDef` too (gen #4). It was omitted, so an async def counted
            # as neither live nor mirrored and simply left the coverage census. Measured
            # today: 0 async defs in src/pycsl and 0 in the mirror, so this changes nothing
            # now — it is closed because the first `async def` added to the emitter would
            # have been invisible to the coverage ratchet with nothing to announce it.
            names = {n.name for n in ast.walk(tree)
                     if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
            if names or rel not in out:
                out.setdefault(rel, set()).update(names)
    return out


MIN_LIVE_DEFS = 1600        # (#49) gen #31: measured 1823. A FLOOR on the POPULATION.
MIN_MIRRORED_FILES = 50     # (#49) gen #31: measured 53 mirrored file(s).


def _trusted_funcs(root):
    """Functions in the mirror whose leading `#@` block carries `\\trusted`.

    The block is read UPWARD from the `def`, across blank lines and comments, which is the
    same convention every other instrument in this battery uses to attach annotations to a
    definition.
    """
    import ast
    n, per_file = 0, {}
    for dirpath, _dirnames, filenames in os.walk(root):
        for fn in sorted(filenames):
            if not fn.endswith(".py"):
                continue
            f = os.path.join(dirpath, fn)
            src = open(f, errors="replace").read()
            lines = src.split("\n")
            try:
                tree = ast.parse(src)
            except SyntaxError:
                continue
            c = 0
            for node in ast.walk(tree):
                if not isinstance(node, ast.FunctionDef):
                    continue
                i = node.lineno - 2
                while i >= 0 and (not lines[i].strip()
                                  or lines[i].strip().startswith("#")):
                    if "\\trusted" in lines[i]:
                        c += 1
                        break
                    i -= 1
            if c:
                per_file[os.path.relpath(f, root)] = c
            n += c
    return n, per_file


def main():
    live, mirror = _defs(LIVE), _defs(MIRROR)
    shared = [r for r in live if r in mirror]
    total = sum(len(live[r]) for r in shared)
    missing = {r: sorted(live[r] - mirror[r]) for r in shared if live[r] - mirror[r]}
    n_missing = sum(len(v) for v in missing.values())
    unmirrored_files = sorted(r for r in live if r not in mirror)

    print("[*] mirror-coverage: %d live def(s) across the %d MIRRORED file(s); "
          "%d have NO mirror counterpart (%.1f%%). %d live file(s) have no mirror at all."
          % (total, len(shared), n_missing,
             100.0 * n_missing / max(total, 1), len(unmirrored_files)))
    n_trusted, trusted_per_file = _trusted_funcs(MIRROR)
    print("[*] mirror-coverage: %d mirror function(s) carry `\\trusted` — the TCB this "
          "campaign exists to shrink, counted by a stated rule (a `def` whose leading `#@` "
          "block contains the marker) so the number can be recomputed rather than quoted."
          % n_trusted)
    if "--list" in sys.argv:
        for r in sorted(trusted_per_file, key=lambda k: -trusted_per_file[k])[:10]:
            print("    %-44s %3d trusted" % (r, trusted_per_file[r]))
    if "--list" in sys.argv or n_missing > MAX_UNMIRRORED_DEFS:
        for r in sorted(missing, key=lambda k: -len(missing[k])):
            print("    %-44s %3d unmirrored  e.g. %s"
                  % (r, len(missing[r]), ", ".join(missing[r][:3])))

    # (#49) gen #31 — ZERO-INPUT GUARD. Both ratchets below are UPPER bounds, and an empty
    # walk satisfies an upper bound perfectly: a broken `LIVE`/`MIRROR` root or a renamed
    # mirror tree yields 0 live defs, 0 shared files, 0 unmirrored defs, and the plane
    # prints OK. The two floors below bound the POPULATION instead, so the plane refuses
    # rather than passing on nothing — the #44 rule, already carried by
    # `byte-diff-sweep.sh` (900 sources), `run-soundness-planes.sh` (MIN_PLANES) and
    # `check-directive-enforcement.py` (its derived-population refusal).
    if total < MIN_LIVE_DEFS or len(shared) < MIN_MIRRORED_FILES:
        print("[!] mirror-coverage: REFUSING — %d live def(s) across %d mirrored file(s), "
              "expected at least %d / %d. The walk is broken, so an unmirrored count of 0 "
              "means nothing. THIS IS A REFUSAL, NOT A PASS."
              % (total, len(shared), MIN_LIVE_DEFS, MIN_MIRRORED_FILES), file=sys.stderr)
        return 2

    rc = 0
    if n_trusted > MAX_TRUSTED_FUNCS:
        print("[!] mirror-coverage: TCB RATCHET BROKEN — %d > %d `\\trusted` mirror "
              "function(s). This driver exists to make that number go DOWN. If a new stub "
              "is genuinely required, say why in the commit and raise the ceiling "
              "deliberately; if a conversion retired one, LOWER the ceiling in the same "
              "commit." % (n_trusted, MAX_TRUSTED_FUNCS), file=sys.stderr)
        rc = 1
    if n_missing > MAX_UNMIRRORED_DEFS:
        print("[!] mirror-coverage: RATCHET BROKEN — %d > %d unmirrored def(s). A live "
              "function with no mirror counterpart is not `\\trusted`, it is ABSENT: it "
              "carries no marker, so the headline count cannot see it."
              % (n_missing, MAX_UNMIRRORED_DEFS))
        rc = 1
    if len(unmirrored_files) > MAX_UNMIRRORED_FILES:
        print("[!] mirror-coverage: FILE RATCHET BROKEN — %d > %d unmirrored file(s)."
              % (len(unmirrored_files), MAX_UNMIRRORED_FILES))
        rc = 1
    if rc == 0:
        if n_missing < MAX_UNMIRRORED_DEFS:
            print("[+] mirror-coverage: %d < ratchet %d — lower the constant."
                  % (n_missing, MAX_UNMIRRORED_DEFS))
        print("[+] mirror-coverage: OK — measured %d unmirrored def(s) / %d unmirrored "
              "file(s) (ratchets %d / %d)."
              % (n_missing, len(unmirrored_files),
                 MAX_UNMIRRORED_DEFS, MAX_UNMIRRORED_FILES))
    return rc


if __name__ == "__main__":
    sys.exit(main())
