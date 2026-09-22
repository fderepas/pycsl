#!/usr/bin/env python3
r"""L-PLANE ORACLE (SLOW): does the stdlib MODEL LAYER actually verify?

WHY THIS EXISTS (gen #30). The semantics reference's Trusted Computing Base appendix makes
a load-bearing claim about `src/pycsl_lib/`:

    "Critically, the contracts are no longer un-checked assertions. Each model's bodies are
     themselves body-verified within the library (e.g. the `os` filesystem model carries
     zero bare `\trusted`), so a contract a consumer relies on is discharged by the
     library's own machine-checked proofs."

That is a CHECKABLE CLAIM, and route #212 is the reason to check it: an importing unit
believes every contract of an imported module — frames, postconditions, class invariants —
and NOTHING verifies the module. The appendix's sentence is exactly the thing that would
make that belief safe, so it should be measured rather than cited.

WHAT IT MEASURES. Every `.py` under `src/pycsl_lib/`, compiled with `--import-path src` so
that a module's OWN imports resolve (without it, a package module fails for a reason that
has nothing to do with its contracts — measured, and it cost two false failures in the
corpus-dependency sweep the same day). Each module lands in one of three buckets: VERIFIES,
FAILS (the prover leaves a goal), or REFUSED (a pipeline error — the front end rejects it).

THE RATCHET is the FAILING SET, baselined by name. A module that starts failing fails this
gate; a module that starts verifying is reported so its entry can be removed. The baseline
is not a shrug: each entry says what kind of failure it is, because "the model does not
verify" and "the model cannot be compiled standalone" are different facts about the TCB.

WHY SLOW. It runs the prover over ~104 modules, including the `os` filesystem model. It
belongs in `--slow`, and it carries a per-module timeout so one heavy model cannot hang the
battery.

Usage:  bin/check-stdlib-modules-verify.py [--verbose] [--timeout SECS]
"""
import argparse
import glob
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIB = os.path.join(ROOT, "src", "pycsl_lib")
PY = os.path.join(ROOT, ".venv", "bin", "python3")
PY = PY if os.path.exists(PY) else "python3"
DRIVER = os.path.join(ROOT, "src", "pycsl", "pycsl.py")
MIN_MODULES = 90          # 104 at the first measurement

# module (path relative to src/pycsl_lib) -> why it is here.
# FILLED FROM THE FIRST MEASUREMENT — see the commit that added this plane.
BASELINE = {}


def classify(path, timeout):
    try:
        p = subprocess.run([PY, DRIVER, "--import-path", os.path.join(ROOT, "src"), path],
                           capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return "TIMEOUT"
    out = (p.stdout or "") + (p.stderr or "")
    if "Verification SUCCESS" in out:
        return "VERIFIES"
    if "PIPELINE ERROR" in out:
        return "REFUSED"
    return "FAILS"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--timeout", type=int, default=420)
    args = ap.parse_args()

    files = sorted(glob.glob(os.path.join(LIB, "**", "*.py"), recursive=True))
    if len(files) < MIN_MODULES:
        print("[!] stdlib-modules-verify: REFUSING — %d module(s) found, expected at "
              "least %d." % (len(files), MIN_MODULES), file=sys.stderr)
        return 2

    bad = {}
    for f in files:
        rel = os.path.relpath(f, LIB)
        verdict = classify(f, args.timeout)
        if verdict != "VERIFIES":
            bad[rel] = verdict
        if args.verbose:
            print("    %-10s %s" % (verdict, rel))

    print("[*] stdlib-modules-verify: %d module(s); %d VERIFY, %d do not (%s)."
          % (len(files), len(files) - len(bad), len(bad),
             ", ".join("%s %d" % (k, sum(1 for v in bad.values() if v == k))
                       for k in ("FAILS", "REFUSED", "TIMEOUT"))))

    rc = 0
    for rel in sorted(set(bad) - set(BASELINE)):
        print("[!]   NEWLY NOT VERIFYING: %s (%s). The TCB appendix says a consumer's "
              "contracts are discharged by the library's own machine-checked proofs; this "
              "module no longer has one." % (rel, bad[rel]), file=sys.stderr)
        rc = 1
    for rel in sorted(set(BASELINE) - set(bad)):
        print("[+]   %s NOW VERIFIES — remove its baseline entry." % rel)

    if rc:
        print("[!] stdlib-modules-verify: NOT OK.", file=sys.stderr)
    else:
        print("[+] stdlib-modules-verify: OK — the non-verifying set is the known one "
              "(%d module(s))." % len(bad))
    return rc


if __name__ == "__main__":
    sys.exit(main())
