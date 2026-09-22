#!/usr/bin/env python3
r"""L-PLANE ORACLE: every `#@ \trusted` marker under `src/pycsl_lib/`.

WHY THIS EXISTS (gen #30). The campaign's headline metric is the `\trusted` marker count,
and two planes maintain it — `bin/count-trusted-directives.py` and
`bin/check-trusted-reasons.py`. **Both scope to the MIRROR root `src/self-annotate/src`.**
So the 459 headline count excludes `src/pycsl_lib/` entirely, and the stdlib layer's trust
surface is outside every trust gate.

It is not empty. Two markers live there, and one of them is bare:

  * `mth.isqrt` — `#@ \trusted reviewer: newton-method-variant`, with a stated reason (the
    Newton's-method VARIANT needs nonlinear arithmetic beyond Alt-Ergo's reach) and a
    contract (`requires x >= 0`, `ensures \result >= 0`) that is TRUE of `math.isqrt`.
    Honest trust: named, reasoned, and weak enough to be right.
  * `hlib.Sha256.update` — a BARE `#@ \trusted`: **no reviewer, no reason**, in a class
    whose `hexdigest` returns `[0] * 64` under `ensures \length(\result) == 64`, i.e. an
    all-zero digest behind a length-only contract.

`config/skills/agent-stdlib-annotate/SKILL.md` is explicit that this layer carries ZERO
`\trusted` and that an irreducibly-opaque kernel "becomes an abstract `val` pinned by a
cited `#@ proof` — never `\trusted`". The rule existed, the violation existed, and no plane
connected them.

WHAT IT MEASURES. Every `#@ \trusted` marker under `src/pycsl_lib/`, keyed on
(module, function). The set is a RATCHET: a NEW marker fails. Each baselined entry records
whether it carries a `reviewer:` clause and what closing it would take. A marker that
DISAPPEARS is reported so its entry can go with it.

WHY THE BARE ONE IS BASELINED RATHER THAN FAILED. A gate that is red the day it lands
cannot be added to a green battery, and inventing a `reviewer:` identity to silence it
would be worse than recording it. It is in the baseline WITH ITS DEFECT NAMED, which is the
same treatment `check-swallowed-exceptions` gave its eight firings before they were driven
to zero.

Usage:  bin/check-stdlib-trusted-markers.py [--verbose]
"""
import argparse
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIB = os.path.join(ROOT, "src", "pycsl_lib")
MIN_FILES = 80   # 93 packages at the first measurement; the layer only grows

# (module, function) -> (has a `reviewer:` clause, why it is here / what closing it takes)
BASELINE = {
    ("mth", "isqrt"): (True,
        "`reviewer: newton-method-variant`. The BODY is Newton's method; its loop VARIANT "
        "needs nonlinear arithmetic beyond Alt-Ergo. The contract is `requires x >= 0` / "
        "`ensures \\result >= 0`, which is TRUE of `math.isqrt`, so the trust buys "
        "termination, not a value claim. CLOSING IT = a variant proof, or an abstract "
        "`val` pinned by a cited `#@ proof rocq|lean` lemma (the skill's prescribed route "
        "for an irreducibly-opaque kernel)."),
    ("hlib", "update"): (False,
        "**BARE `#@ \\trusted` — NO reviewer, NO reason.** In `Sha256`, whose `hexdigest` "
        "returns `[0] * 64` under `ensures \\length(\\result) == 64`: an all-zero digest "
        "behind a length-only contract. The skill says this layer carries ZERO `\\trusted` "
        "and that an opaque kernel becomes an abstract `val` pinned by a cited proof, "
        "never `\\trusted`. CLOSING IT = give the marker a `reviewer:` and a reason at "
        "minimum; properly, make the compression function an abstract `val` and let "
        "`hexdigest`'s contract say only what the model supports."),
}


def markers():
    out, files = [], 0
    for f in sorted(glob.glob(os.path.join(LIB, "**", "*.py"), recursive=True)):
        files += 1
        mod = os.path.relpath(f, LIB).replace(os.sep + "__init__.py", "").replace(".py", "")
        lines = open(f, errors="replace").read().split("\n")
        for i, l in enumerate(lines):
            m = re.match(r"\s*#@\s*\\trusted\b(.*)$", l)
            if not m:
                continue
            tail = m.group(1)
            fn = "<unattached>"
            for j in range(i + 1, min(i + 10, len(lines))):
                d = re.match(r"\s*def\s+(\w+)\s*\(", lines[j])
                if d:
                    fn = d.group(1)
                    break
            out.append((mod, fn, "reviewer:" in tail))
    return out, files


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    found, files = markers()
    if files < MIN_FILES:
        print("[!] stdlib-trusted-markers: REFUSING — the walk saw only %d file(s), "
              "expected at least %d. The glob is broken; this is not a pass."
              % (files, MIN_FILES), file=sys.stderr)
        return 2

    keys = {(m, f) for m, f, _r in found}
    new = sorted(k for k in keys if k not in BASELINE)
    gone = sorted(k for k in BASELINE if k not in keys)
    noreviewer = sorted((m, f) for m, f, r in found if not r)

    if args.verbose:
        for m, f, r in sorted(found):
            print("    %s %s.%s%s" % ("ok " if (m, f) in BASELINE else "NEW", m, f,
                                      "" if r else "   [NO reviewer:]"))

    print("[*] stdlib-trusted-markers: %d file(s) scanned; %d `\\trusted` marker(s), "
          "%d without a `reviewer:` clause." % (files, len(keys), len(noreviewer)))

    rc = 0
    for k in gone:
        print("[+]   baselined marker %s.%s IS GONE — remove its baseline entry." % k)
    for k in new:
        print("[!]   NEW `\\trusted` MARKER %s.%s under src/pycsl_lib/. This layer's skill "
              "says it carries ZERO trusted markers and that an opaque kernel becomes an "
              "abstract `val` pinned by a cited `#@ proof`, never `\\trusted`." % k,
              file=sys.stderr)
        rc = 1
    if rc:
        print("[!] stdlib-trusted-markers: NOT OK — the stdlib trust surface grew.",
              file=sys.stderr)
    else:
        print("[+] stdlib-trusted-markers: OK — %d known marker(s), none new (%d of them "
              "still lack a `reviewer:` clause and are named in the baseline)."
              % (len(BASELINE), len(noreviewer)))
    return rc


if __name__ == "__main__":
    sys.exit(main())
