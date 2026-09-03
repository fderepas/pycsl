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
MAX_UNMIRRORED_DEFS = 550
MAX_UNMIRRORED_FILES = 41


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
            names = {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
            if names or rel not in out:
                out.setdefault(rel, set()).update(names)
    return out


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
    if "--list" in sys.argv or n_missing > MAX_UNMIRRORED_DEFS:
        for r in sorted(missing, key=lambda k: -len(missing[k])):
            print("    %-44s %3d unmirrored  e.g. %s"
                  % (r, len(missing[r]), ", ".join(missing[r][:3])))

    rc = 0
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
