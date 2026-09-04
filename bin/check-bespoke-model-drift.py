#!/usr/bin/env python3
"""check-bespoke-model-drift.py — the HAND-WRITTEN-MODEL plane.

WHAT THIS IS FOR. Some converted mirror methods do NOT get their WhyML from the generic
lowering. They get it from a `_emit_<X>_bespoke` function in `module6_whyml/functions.py`
that is keyed on the METHOD NAME and writes the model out by hand. That is a legitimate
technique — the generic lowering cannot express these bodies — but it breaks the one
assumption every other plane rests on: that the model is DERIVED FROM the body.

For a bespoke-modelled method, editing the live body and dutifully syncing the mirror
leaves:

    check-self-annotate-sync.sh   GREEN   (the two sources now agree)
    L3-tc                         GREEN   (the model still type-checks)
    the whole-file proof          GREEN   (it proves the OLD model)
    the mirror emission           BYTE-IDENTICAL

...and the model has silently stopped being the body. Relaunch #44 walked into exactly
this on `_py_stmt_assign` (route #28) WITH the warning in front of it: the live body grew
a `FieldAssign` arm, the mirror was synced, every plane was green, and the emitted `.mlw`
still read `else ()`.

THE TELL IS COUNTER-INTUITIVE AND WORTH STATING: the BYTE-IDENTICAL EMISSION IS THE
SYMPTOM. A real change to a body whose model is derived from it MUST move the emission. If
it does not, the model is hand-written — go and find it.

WHAT THIS GATE DOES. It drives the emission with `PYCSL_BESPOKE_CENSUS=1` (an env-gated
stderr line at each bespoke dispatch site; nothing is emitted on a normal run), resolves
each bespoke-modelled method back to its mirror source, and stores a FINGERPRINT of that
method's body. If a fingerprint changes and the baseline has not been updated, it FAILS
and says which `_emit_..._bespoke` function must move with it.

It is deliberately a fingerprint, not a proof of correspondence: no mechanical check can
decide that a hand-written model means the same as a body. What it CAN do is guarantee
nobody changes one without being told about the other.

USAGE
    bin/check-bespoke-model-drift.py            # check against the baseline
    bin/check-bespoke-model-drift.py --update   # re-baseline (after moving BOTH)
    bin/check-bespoke-model-drift.py --list     # method -> bespoke emitter
"""
import argparse
import ast
import hashlib
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIRROR = os.path.join(ROOT, "src", "self-annotate", "src")
BASELINE = os.path.join(ROOT, "getting-better", "bespoke-model-baseline.json")


# The driver the census runs in a subprocess. It MONKEY-PATCHES every `_emit_*_bespoke`
# method at runtime and then emits one mirror file.
#
# WHY A WRAPPER AND NOT A HOOK IN THE EMITTER. The first version of this gate added a
# `_bespoke_census` helper to `module6_whyml/functions.py`. It was env-gated and emitted
# nothing — and it still cost something real: `bin/check-mirror-coverage.py` went
# 550 -> 551, because a live function with no mirror counterpart is not `\trusted`, it is
# ABSENT, and the headline `\trusted` count structurally cannot see it. #43 recorded that
# exact hazard ("converting a `\trusted` stub is progress, and quietly adding an unmirrored
# live helper beside it now is not") and this gate walked straight into it. Wrapping from
# OUTSIDE keeps `src/pycsl` byte-for-byte unchanged, so the plane costs the perimeter
# nothing — and it is still a MEASUREMENT of the real dispatch, not a static guess about
# it. A static parse of the dispatcher would have been the tempting alternative and is the
# wrong one: the `_is_*` recognizers are not uniform (some return a tuple, some match on
# `endswith`, some on a table), so a static reader would silently miss members — and an
# incomplete census is the "I looked at nothing" failure this campaign keeps finding.
_DRIVER = r"""
import os, sys, types
ROOT = sys.argv[1]
target = sys.argv[2]
sys.path.insert(0, os.path.join(ROOT, "src", "pycsl"))
import module6_whyml.functions as F
recs = []
for _cls in [c for c in vars(F).values() if isinstance(c, type)]:
    for _nm in list(vars(_cls)):
        if not (_nm.startswith("_emit_") and _nm.endswith("_bespoke")):
            continue
        _orig = getattr(_cls, _nm)
        def _mk(orig, nm):
            def wrapper(self, func, *a, **k):
                try:
                    recs.append((nm, str(func.get("self_type") or "-"),
                                 str(func.get("name") or "-")))
                except Exception:
                    pass
                return orig(self, func, *a, **k)
            return wrapper
        setattr(_cls, _nm, _mk(_orig, _nm))
sys.argv = ["pycsl.py", target, "--import-path", os.path.join(ROOT, "src", "pycsl"),
            "--no-proof", "--no-typecheck"]
import pycsl
try:
    pycsl.main()
except SystemExit:
    pass
except Exception:
    pass
for r in recs:
    sys.stderr.write("BESPOKE\t%s\t%s\t%s\n" % r)
"""


def census():
    """{(mirror-rel-path, class, method): emitter} — driven from the REAL emission, with
    the bespoke emitters wrapped from outside so `src/pycsl` is not touched."""
    env = dict(os.environ)
    env["PYTHONHASHSEED"] = "0"
    rows = {}
    targets = []
    for root, _d, files in os.walk(MIRROR):
        for fn in sorted(files):
            if fn.endswith(".py"):
                targets.append(os.path.join(root, fn))
    for path in targets:
        try:
            r = subprocess.run([sys.executable, "-c", _DRIVER, ROOT, path],
                               capture_output=True, text=True, timeout=900,
                               env=env, cwd=ROOT)
        except subprocess.TimeoutExpired:
            continue
        for line in r.stderr.split("\n"):
            if not line.startswith("BESPOKE\t"):
                continue
            _tag, emitter, cls, wname = (line.split("\t") + ["", "", ""])[:4]
            prefix = cls.lower() + "__"
            meth = wname[len(prefix):] if wname.startswith(prefix) else wname
            rows[(os.path.relpath(path, MIRROR), cls, meth)] = emitter
    return rows


def body_fingerprint(cls, meth):
    """A hash of the method's body, normalised for whitespace and comments, found by
    searching the WHOLE mirror for `cls.meth`. The search must be tree-wide, not
    per-emitting-file: an IMPORTING mirror re-emits an imported class's bespoke methods,
    so the same method is reached through several files and is DEFINED in only one.
    `cls == "-"` means a module-level function. Returns (relpath, fingerprint) or None."""
    for root, _d, files in os.walk(MIRROR):
        for fn_name in sorted(files):
            if not fn_name.endswith(".py"):
                continue
            path = os.path.join(root, fn_name)
            try:
                tree = ast.parse(open(path, errors="replace").read())
            except (OSError, SyntaxError, UnicodeDecodeError):
                continue
            if cls == "-":
                cands = [n for n in tree.body
                         if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                         and n.name == meth]
            else:
                cands = []
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef) and node.name == cls:
                        cands += [n for n in node.body
                                  if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                                  and n.name == meth]
            if cands:
                # ast.dump drops comments and formatting: only a real semantic change
                # moves the fingerprint.
                body = "".join(ast.dump(s) for s in cands[0].body)
                return (os.path.relpath(path, MIRROR),
                        hashlib.sha256(body.encode()).hexdigest()[:16])
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--update", action="store_true")
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args()

    rows = census()
    cur = {}
    unresolved = []
    for (_emitting_path, cls, meth), emitter in sorted(rows.items()):
        found = body_fingerprint(cls, meth)
        if found is None:
            unresolved.append((f"{cls}.{meth}", emitter))
            continue
        defpath, fp = found
        key = f"{defpath}::{cls}.{meth}"
        cur[key] = {"emitter": emitter, "fingerprint": fp}

    print(f"[*] bespoke-model-drift: {len(cur)} mirror method(s) whose WhyML model is "
          f"HAND-SYNTHESIZED, across {len(set(v['emitter'] for v in cur.values()))} "
          f"`_emit_..._bespoke` function(s).")
    if args.list:
        for k in sorted(cur):
            print(f"    {k:70s} <- {cur[k]['emitter']}")
        for k, e in unresolved:
            print(f"    {k:70s} <- {e}   (UNRESOLVED source)")
        return 0
    for k, e in unresolved:
        print(f"    [~] source not found for {k} (model by {e})")

    if args.update or not os.path.exists(BASELINE):
        with open(BASELINE, "w") as fh:
            json.dump(cur, fh, indent=2, sort_keys=True)
            fh.write("\n")
        print(f"[+] bespoke-model baseline written: {len(cur)} method(s)")
        return 0

    with open(BASELINE) as fh:
        base = json.load(fh)

    moved, added, gone = [], [], []
    for k, v in sorted(cur.items()):
        if k not in base:
            added.append((k, v["emitter"]))
        elif base[k]["fingerprint"] != v["fingerprint"]:
            moved.append((k, v["emitter"]))
    for k in sorted(base):
        if k not in cur:
            gone.append(k)

    for k, e in added:
        print(f"[+] NEW bespoke-modelled method: {k} <- {e} (re-baseline with --update)")
    for k in gone:
        print(f"[~] no longer bespoke-modelled: {k} (re-baseline with --update)")

    if moved:
        print(f"[-] BESPOKE-MODELLED BODY CHANGED in {len(moved)} method(s). Its WhyML "
              f"model is HAND-WRITTEN and does NOT follow the body:")
        for k, e in moved:
            print(f"      {k}\n          model written by  {e}  "
                  f"(module6_whyml/functions.py)")
        print("[-] Every other plane will stay GREEN through this — mirror-sync compares "
              "the two SOURCES, L3-tc checks the OLD model, and the emission may be "
              "BYTE-IDENTICAL (which is itself the tell). Move the `_emit_..._bespoke` "
              "function in the same increment, read the emitted .mlw to confirm, then "
              "re-run with --update.")
        return 1

    print(f"[+] bespoke-model-drift: OK — {len(cur)} hand-written model(s), no body moved "
          f"without its model.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
