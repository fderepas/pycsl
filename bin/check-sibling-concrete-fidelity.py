#!/usr/bin/env python3
r"""check-sibling-concrete-fidelity.py — THE POPULATION THE FIDELITY PLANE SKIPS.

`bin/check-self-annotate-mirror-sync.py` (via `bin/check-self-annotate-sync.sh`) pairs each
mirror def with the live def OF THE SAME QUALIFIED NAME IN THE SAME FILE and requires a
verbatim body. A mirror def whose live twin lives in a SIBLING FILE therefore is not in its
population at all: it is not one of the "896 un-trusted verbatim" it reports, and changing it
is INVISIBLE.

That population is not empty and it is not incidental. `#@ sibling_concrete` (32 uses across 7
mirror files) exists precisely to put a CONCRETE copy of a sibling mixin's method into a mirror
file, so that this file's `self._m(...)` call sites lower to the real body instead of a
receiver-less abstract `val` whose result is unconstrained (the shadowed-selfcall repair,
lesson (ay)). The copy is UN-TRUSTED, so its own contract is PROVED — and the file's OTHER
verified functions call it to discharge THEIR obligations.

PROVEN BY PERTURBATION (#49, gen #31), which is why this plane exists rather than being
reasoned about: changing the body of the `sibling_concrete` duplicate of `_field_label` in
`self-annotate/src/module6_whyml/statements.py` left the fidelity plane printing

    OK: all 896 un-trusted self-annotate mirror functions … are verbatim copies of the live
    source; 37 class-level constants are subsets of live            (exit 0)

and the only script that DID see it (`bin/self-annotate-mirror-check.sh`) reports every
mirror-only def as undifferentiated DRIFT and is registered in no battery.

AND THREE HAD ALREADY DRIFTED when this was written — see DIVERGING_BASELINE below.

WHAT THIS PLANE ASKS. For every UN-TRUSTED mirror def with no same-file live twin: does the
LIVE tree contain a def of the same BARE name whose normalized body and parameter list are
IDENTICAL? Normalization is imported from the sync plane itself, so the two agree by
construction on what "verbatim" means (docstring dropped, annotations dropped, `ast.unparse`d).

  * DIVERGING — a live def of that name exists and NONE of them matches. Ratcheted on the SET,
    which may only shrink; a NEW member fails loud.
  * UNRESOLVED — no live def of that bare name anywhere. Hard zero except `mutable_state`, the
    modelling decorator every mirror file defines for itself.
  * CLASS VIEWS — a mirror-only `class` (the `TypedDict` IR views). Its annotated FIELD NAMES
    must be a SUBSET of the live class's, matching the convention the sync plane already uses
    for class-level constants.

Usage:  bin/check-sibling-concrete-fidelity.py [--list] [--self-test]
Exit 1 on a new divergence, an unallowed unresolved def, or a class-view field not live.
"""
from __future__ import annotations

import argparse
import ast
import copy
import importlib.util
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIVE = os.path.join(ROOT, "src/pycsl")
MIRROR = os.path.join(ROOT, "src/self-annotate/src")

# The sync plane's own normalizer + signature + walker. Imported rather than re-implemented so
# the two planes cannot drift apart on what "verbatim" means (the whole point of this file is
# that a second opinion on fidelity must use the SAME definition of it).
_spec = importlib.util.spec_from_file_location(
    "_mirror_sync", os.path.join(ROOT, "bin/check-self-annotate-mirror-sync.py"))
_sync = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_sync)              # guarded by `if __name__ == "__main__"` there

# (#49, gen #31) FIRST MEASUREMENT — the three that had ALREADY drifted when the plane was
# written. Each is a real divergence with content, not a formatting artefact:
#   _array_coerce_arg   live `module6_whyml/expressions.py` returns '(any (array int))' twice;
#                       the mirror copy returns '(Array.make 1 0)'. `any` is a FRESH
#                       UNCONSTRAINED array WITH AN EFFECT and `Array.make 1 0` is a pure
#                       one-element array, so a proof against the second says nothing about a
#                       compiler that emits the first.
#   _field_type_of      live `module6_whyml/types.py`; the `receiver_name == "self"` branch.
#   _rhs_yields_map     live `module6_whyml/types.py`; the `t == "Call"` branch — live handles
#                       `getattr(self, f, {})` with 2..3 args, the mirror `fn.startswith("self.")`.
# MAY ONLY SHRINK. Repairing one means re-porting the live body verbatim and re-proving the
# mirror file, or re-`\trusted`ing the copy and taking the marker cost.
DIVERGING_BASELINE = {
    ("module6_whyml/statements.py", "StatementEmissionMixin._array_coerce_arg"),
    ("module6_whyml/statements.py", "StatementEmissionMixin._field_type_of"),
    ("module6_whyml/statements.py", "StatementEmissionMixin._rhs_yields_map"),
}

# `mutable_state` is the mirror's OWN modelling decorator: every mirror file that uses
# `@mutable_state` also defines it, and there is deliberately no live counterpart. Any OTHER
# unresolved mirror-only def is a def modelling nothing, and fails.
UNRESOLVED_ALLOWLIST = {"mutable_state"}


def _live_bare_index():
    """bare name -> [(relpath, FunctionDef)] over the WHOLE live tree."""
    idx = {}
    for dirpath, _dn, fns in os.walk(LIVE):
        for fn in sorted(fns):
            if not fn.endswith(".py"):
                continue
            path = os.path.join(dirpath, fn)
            rel = os.path.relpath(path, LIVE)
            try:
                for qn, (body, _tr) in _sync.methods(path).items():
                    idx.setdefault(qn.rsplit(".", 1)[-1], []).append((rel, body))
            except (SyntaxError, OSError):
                continue
    return idx


def _class_fields(path):
    """mirror/live {ClassName: {annotated field names}} for module-level classes."""
    out = {}
    try:
        tree = ast.parse(open(path).read())
    except (SyntaxError, OSError):
        return out
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            out[node.name] = {s.target.id for s in node.body
                              if isinstance(s, ast.AnnAssign)
                              and isinstance(s.target, ast.Name)}
    return out


def audit():
    idx = _live_bare_index()
    live_classes = {}
    for dirpath, _dn, fns in os.walk(LIVE):
        for fn in fns:
            if fn.endswith(".py"):
                for cn, flds in _class_fields(os.path.join(dirpath, fn)).items():
                    live_classes.setdefault(cn, set()).update(flds)

    same, diverging, unresolved, badclass, classes_ok, trusted_stubs = [], [], [], [], 0, 0
    for dirpath, _dn, fns in os.walk(MIRROR):
        for fn in sorted(fns):
            if not fn.endswith(".py"):
                continue
            mp = os.path.join(dirpath, fn)
            rel = os.path.relpath(mp, MIRROR)
            lp = os.path.join(LIVE, rel)
            if not os.path.exists(lp):
                continue                      # unmirrored file: check-mirror-coverage's half
            try:
                md, ld = _sync.methods(mp), _sync.methods(lp)
            except (SyntaxError, OSError):
                continue
            for qn in sorted(md):
                body, trusted = md[qn]
                if qn in ld:
                    continue                  # the sync plane's population
                if trusted:
                    trusted_stubs += 1        # a cross-mixin MRO boundary stub: by design
                    continue
                bare = qn.rsplit(".", 1)[-1]
                cands = idx.get(bare, [])
                if not cands:
                    (unresolved if bare not in UNRESOLVED_ALLOWLIST
                     else same).append((rel, qn, "allowlisted" if bare in
                                        UNRESOLVED_ALLOWLIST else ""))
                    continue
                if any(lbody == body for _lrel, lbody in cands):
                    same.append((rel, qn, cands[0][0]))
                else:
                    diverging.append((rel, qn, ",".join(c[0] for c in cands)))
            # mirror-only module-level CLASS views
            mcls, lcls = _class_fields(mp), _class_fields(lp)
            for cn, flds in sorted(mcls.items()):
                if cn in lcls:
                    continue
                if cn not in live_classes:
                    unresolved.append((rel, "class " + cn, ""))
                elif not flds <= live_classes[cn]:
                    badclass.append((rel, "class " + cn,
                                     ",".join(sorted(flds - live_classes[cn]))))
                else:
                    classes_ok += 1
    return same, diverging, unresolved, badclass, classes_ok, trusted_stubs


def self_test():
    """PERTURB A KNOWN-SAME MEMBER AND REQUIRE THE COMPARISON TO FIRE.

    A fidelity plane that has never been shown to fail is not an oracle. This mutates the
    normalized body of one member the audit classified SAME and asserts the comparison then
    reports DIVERGING — the same mutation test the sync plane pins itself with, and the exact
    experiment that found the hole this plane closes."""
    same, _dv, _un, _bc, _co, _ts = audit()
    pick = [s for s in same if s[2] and s[2] != "allowlisted"]
    if not pick:
        print("[!] sibling-concrete-fidelity: --self-test found NO same-member to mutate.")
        return 1
    rel, qn, lrel = pick[0]
    mp = os.path.join(MIRROR, rel)
    body, _tr = _sync.methods(mp)[qn]
    idx = _live_bare_index()
    bare = qn.rsplit(".", 1)[-1]
    cands = idx.get(bare, [])
    assert any(lbody == body for _r, lbody in cands), "picked member is not SAME"
    mutated = (body[0], list(body[1]) + ["_ZZZ_PERTURBATION = 1"])
    if any(lbody == mutated for _r, lbody in cands):
        print("[!] sibling-concrete-fidelity: --self-test FAILED — a mutated body still "
              "compared EQUAL to live. The comparison is not sensitive; do not trust this plane.")
        return 1
    print("[+] sibling-concrete-fidelity: --self-test OK — mutating "
          "%s::%s (live %s) makes the comparison report DIVERGING." % (rel, qn, lrel))
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()

    same, diverging, unresolved, badclass, classes_ok, trusted_stubs = audit()
    dv_set = {(r, q) for r, q, _c in diverging}
    print("[*] sibling-concrete-fidelity: %d un-trusted mirror-only def(s) resolve to a "
          "VERBATIM live twin in a sibling file; %d diverge; %d unresolved; "
          "%d class view(s) OK; %d \\trusted cross-mixin stub(s) (by design)."
          % (len(same), len(diverging), len(unresolved), classes_ok, trusted_stubs))
    if args.list:
        for tag, rows in (("SAME", same), ("DIVERGING", diverging),
                          ("UNRESOLVED", unresolved), ("CLASS-FIELD-NOT-LIVE", badclass)):
            for r, q, c in rows:
                print("    %-20s %s :: %s   %s" % (tag, r, q, c))

    rc = 0
    new = dv_set - DIVERGING_BASELINE
    if new:
        print("[!] sibling-concrete-fidelity: %d NEW DIVERGENCE(S) — an UN-TRUSTED mirror body "
              "is not the live code it models, and the sync plane cannot see it (its live twin "
              "is in a sibling file):" % len(new))
        for r, q in sorted(new):
            print("      %s :: %s" % (r, q))
        print("    Re-port the live body verbatim and re-prove the mirror file, or mark the copy")
        print("    `#@ \\trusted` and take the marker cost. Do NOT widen the baseline.")
        rc = 1
    gone = DIVERGING_BASELINE - dv_set
    if gone:
        print("[*] sibling-concrete-fidelity: %d baseline divergence(s) REPAIRED — tighten "
              "DIVERGING_BASELINE:" % len(gone))
        for r, q in sorted(gone):
            print("      %s :: %s" % (r, q))
    if unresolved:
        print("[!] sibling-concrete-fidelity: %d mirror-only def(s) resolve to NO live def at "
              "all — they model nothing:" % len(unresolved))
        for r, q, _c in sorted(unresolved):
            print("      %s :: %s" % (r, q))
        rc = 1
    if badclass:
        print("[!] sibling-concrete-fidelity: %d mirror-only class view(s) carry a field the "
              "live class does not have:" % len(badclass))
        for r, q, c in sorted(badclass):
            print("      %s :: %s   extra: %s" % (r, q, c))
        rc = 1
    if rc == 0:
        print("[+] sibling-concrete-fidelity: OK — no new divergence, every mirror-only def "
              "resolves, every class view is a subset of live.")
    return rc


if __name__ == "__main__":
    sys.exit(main())
