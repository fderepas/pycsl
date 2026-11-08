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
  * `hlib.Sha256.update` — WAS a BARE `#@ \trusted` (no reviewer, no reason) when this
    plane landed; gen #30 MEASURED why it cannot be dropped and gave it
    `reviewer: field-append-has-no-certified-lowering`. The body appends to a collection
    held in a FIELD, which PyCSL refuses outright (the append is emitted against a fresh
    local with no write-back); and the refusal's own advice, "rewrite it as an indexed
    store", was followed literally and ALSO fails — the `index in array bounds` sub-goal
    is un-dischargeable because `__init__` can leave `self._input` empty, which is exactly
    the `IndexError` CPython raises for that rewrite. The marker is forced, not lazy. The
    class still returns `[0] * 64` from `hexdigest` under a length-only contract, and that
    remains the open item.

`config/skills/agent-stdlib-annotate/SKILL.md` is explicit that this layer carries ZERO
`\trusted` and that an irreducibly-opaque kernel "becomes an abstract `val` pinned by a
cited `#@ proof` — never `\trusted`". The rule existed, the violation existed, and no plane
connected them.

WHAT IT MEASURES. Every `#@ \trusted` marker under `src/pycsl_lib/`, keyed on
(module, function). The set is a RATCHET: a NEW marker fails. Each baselined entry records
whether it carries a `reviewer:` clause and what closing it would take. A marker that
DISAPPEARS is reported so its entry can go with it.

WHY THE BARE ONE WAS BASELINED RATHER THAN FAILED, AND WHY IT NO LONGER IS. A gate that is
red the day it lands cannot be added to a green battery, and inventing a `reviewer:`
identity to silence it would be worse than recording it — so it went into the baseline WITH
ITS DEFECT NAMED, the treatment `check-swallowed-exceptions` gave its eight firings before
they were driven to zero. The count then reached zero the same way theirs did: by MEASURING
the marker (see above) and writing the measured reason into it, not by editing this file.
The `reviewer:` requirement is therefore now ENFORCED — a marker without one fails — which
is the whole point of driving a recorded defect to zero.

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
    ("hlib", "update"): (True,
        "`reviewer: field-append-has-no-certified-lowering` (gen #30; it was BARE when "
        "this plane landed). The body appends to a collection held in a FIELD. PyCSL "
        "REFUSES an un-trusted field-append: it is emitted against a fresh local array "
        "with no write-back, so the method would satisfy `assigns \\nothing` and "
        "re-establish a `\\length` class invariant while the model left the field "
        "unchanged. The refusal advises 'rewrite it as an indexed store'; followed "
        "literally (`self._input[i] = data[i]`, `data: list`, invariants + variant) the "
        "`index in array bounds` sub-goal is UN-DISCHARGEABLE, because `__init__` can "
        "leave `self._input` empty — the same `IndexError` CPython raises. The marker "
        "buys the missing lowering, not a value claim. CLOSING IT = a certified "
        "field-append lowering (write-back plus a length model), NOT an annotation "
        "change. STILL OPEN AND SEPARATE: `hexdigest` returns `[0] * 64` under a "
        "length-only contract — an all-zero digest the length contract cannot see."),
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
    # Gen #30: the recorded defect was driven to zero by measuring the one bare marker and
    # writing its measured reason into it, so the requirement is now ENFORCED, not merely
    # reported. A marker without a `reviewer:` clause fails whether or not it is baselined.

    if args.verbose:
        for m, f, r in sorted(found):
            print("    %s %s.%s%s" % ("ok " if (m, f) in BASELINE else "NEW", m, f,
                                      "" if r else "   [NO reviewer:]"))

    print("[*] stdlib-trusted-markers: %d file(s) scanned; %d `\\trusted` marker(s), "
          "%d without a `reviewer:` clause." % (files, len(keys), len(noreviewer)))

    rc = 0
    for k in gone:
        print("[+]   baselined marker %s.%s IS GONE — remove its baseline entry." % k)
    for k in noreviewer:
        print("[!]   `\\trusted` MARKER %s.%s CARRIES NO `reviewer:` CLAUSE. Every marker "
              "under src/pycsl_lib/ must name who trusts it and why; the count reached "
              "zero in gen #30 and this gate holds it there." % k, file=sys.stderr)
        rc = 1
    for k in new:
        print("[!]   NEW `\\trusted` MARKER %s.%s under src/pycsl_lib/. This layer's skill "
              "says it carries ZERO trusted markers and that an opaque kernel becomes an "
              "abstract `val` pinned by a cited `#@ proof`, never `\\trusted`." % k,
              file=sys.stderr)
        rc = 1
    if rc:
        why = []
        if new:
            why.append("the stdlib trust surface grew")
        if noreviewer:
            why.append("a marker carries no `reviewer:` clause")
        print("[!] stdlib-trusted-markers: NOT OK — %s." % " and ".join(why),
              file=sys.stderr)
    else:
        print("[+] stdlib-trusted-markers: OK — %d known marker(s), none new, %d without "
              "a `reviewer:` clause (enforced at zero since gen #30)."
              % (len(BASELINE), len(noreviewer)))
    return rc


if __name__ == "__main__":
    sys.exit(main())
