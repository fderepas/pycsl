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
# THE FIRST MEASUREMENT (gen #30): 104 modules, 84 VERIFY, 20 do not — 13 REFUSED, 5
# FAILS, 2 TIMEOUT. Every entry below was re-run WITH `--import-path src`.
BASELINE = {
    # ---- REFUSED: the front end rejects the module outright. Each of these was re-run
    # WITH `--import-path src` so the verdict is not an artefact of compiling a package
    # module standalone (that artefact is real: it cost two false failures in the
    # corpus-dependency sweep the same day).
    "json/__init__.py": "REFUSED — route #119's constant-rebinding guard: `BACKSLASH` is "
        "bound as a default argument (`_b=BACKSLASH`). The whole `json` package is a "
        "near-verbatim transcription of CPython's, not a model written for PyCSL, and "
        "FOUR of its files carry ZERO `#@` annotations.",
    "json/_api.py": "REFUSED — same package, same cause.",
    "json/decoder.py": "REFUSED — same package; this is the file the guard names.",
    "json/encoder.py": "REFUSED — same package; 370 code lines, ZERO annotations.",
    "json/scanner.py": "REFUSED — same package.",
    "json/tool.py": "REFUSED — same package.",
    "iomod/__init__.py": "REFUSED.",
    "proc/__init__.py": "REFUSED.",
    "re/_engine.py": "REFUSED — 478 lines, 35 annotations.",
    "subproc/__init__.py": "REFUSED.",
    "sysmod/__init__.py": "REFUSED.",
    "tmpf/__init__.py": "REFUSED.",
    "warn/__init__.py": "REFUSED.",
    # ---- FAILS: the prover leaves a goal. These are the honest "model does not verify"
    # cases, and one of them is the TCB appendix's own example.
    "os/path.py": "FAILS — `Sub-goal postcondition of goal basename'vc` is a Timeout at "
        "5.5M steps. The appendix names the `os` filesystem model as its example of a "
        "body-verified model.",
    "os/UnixInodeFileSystem.py": "FAILS — 2990 lines, 717 annotations; the largest model "
        "in the layer.",
    "dc/__init__.py": "FAILS.",
    "syscfg/__init__.py": "FAILS.",
    "tm/__init__.py": "FAILS.",
    # ---- TIMEOUT: not a verdict, a budget. Recorded as its own class so nobody reads it
    # as "fails".
    "os/__init__.py": "TIMEOUT at 900s (864 lines, 213 annotations).",
    "csys/__init__.py": "TIMEOUT.",
}


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

    # THE INSTRUMENT FACT THIS PLANE MUST NOT TRIP OVER: `why3` is NOT on the default
    # PATH in this repo (it lives behind `scratchpad/g29/env.sh`). Without it EVERY module
    # "fails", which is a false RED of the loudest possible kind — measured on this plane's
    # first run, which reported 104 of 104 not verifying. Refuse instead of reporting.
    import shutil as _sh
    if _sh.which("why3") is None:
        print("[!] stdlib-modules-verify: REFUSING — `why3` is not on PATH, so every "
              "module would report as failing. Source the environment first "
              "(`. scratchpad/g29/env.sh`).", file=sys.stderr)
        return 2

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
