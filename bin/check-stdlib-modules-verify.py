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

(#49) AND A SECOND MEASUREMENT THE FIRST ONE NEEDED. "84 of 104 modules verify" is true
and was being read as evidence for the appendix's sentence. NINE of those 84 carry no
`#@ ensures` at all, and SEVEN carry no `#@` whatever — they come back "Verification
SUCCESS" because the emitter produced no goal. `htm.escape(s) -> s` under
`#@ assigns \nothing` is the shape: real `html.escape('<')` is `'&lt;'`, the model returns
the string unchanged, and it promises nothing about it. So the honest headline is **75
modules with a postcondition to discharge**, not 84.

AND THE NINE SPLIT IN THREE, in two steps, which is itself the lesson: the first split
(7 shims + 2 informative) was made from a static scan, and the first RUN of the split
showed it was still wrong — `fut` and `world` have a `def`, but their ONLY def is
`__init__`, which returns None and can carry no `\result` claim. They are shims with a
constructor, not modules that compute something and promise nothing. THE DISCRIMINATOR IS
A VALUE-RETURNING FUNCTION, and the informative class is ONE module: `udata`. SEVEN have
no `def` at all — `kw` is a constant keyword list, `re` is a re-export shim, `types_stub`
is three empty classes, `fut` is a `_Feature` constant — so they verify with no
postcondition because there is NOTHING TO CLAIM, and that is innocent. TWO had value-returning
functions and promised nothing: `htm` (escape/unescape, each `return s` under
`#@ assigns \nothing`) and `udata` (`lookup` returns the NAME while its docstring says it
returns the character). `htm` was given a true length law the same day
(`\str_length(\result) >= \str_length(s)` for escape, `<=` for unescape, both measured
against CPython over 4000 random strings); `udata.lookup` has no honest claim available —
`\str_length(\result) == 1` is true of CPython and FALSE of the model — so the divergence
is NAMED in the module instead. The ceiling is on the INFORMATIVE half. The count is DERIVED from the source
every run (not a name list), so a module that gains a postcondition leaves the class by
itself, and it is ratcheted downward.

>>> A PROVER SAYING SUCCESS OVER ZERO GOALS IS NOT EVIDENCE. The same reading error
>>> `check-claim-vacuity` was built for, one layer up.

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
import re as _re
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


# (#49) gen #30. Nine of the 84 verifying modules carry no `#@ ensures`; seven of those
# carry no `#@` at all. `htm.escape(s) -> s` under `assigns \nothing` is the shape:
# real `html.escape('<')` is `'&lt;'`, and the model returns the string unchanged while
# promising nothing about it — so it VERIFIES, truthfully, and the verification is worth
# nothing. A ceiling that may only shrink, checked against a DERIVED set.
MAX_NO_ENSURES = 1        # modules with a VALUE-RETURNING function and no `#@ ensures`. Nine
                          # verified with no postcondition at the first measurement; SEVEN
                          # of those have no `def` at all (a constant list, a re-export
                          # shim, empty class stubs) and are counted separately, because
                          # "nothing to claim" and "computes something and claims nothing"
                          # are different facts. The two informative ones were `htm` (given
                          # a true length law the same day) and `udata` (no honest claim
                          # exists; named in the module instead). Then 2 -> 1: `fut` and
                          # `world` define ONLY `__init__`, which returns None and can
                          # have no `\result` claim, so they belong with the shims.


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

    bad, vacuous, no_ann, no_defs = {}, [], [], []
    for f in files:
        rel = os.path.relpath(f, LIB)
        verdict = classify(f, args.timeout)
        if verdict != "VERIFIES":
            bad[rel] = verdict
        else:
            # (#49) gen #30 — WHAT "VERIFIES" IS WORTH, PER MODULE. A module with no
            # `#@ ensures` emits no value obligation, so the prover discharging it says
            # nothing about what its functions RETURN; a module with no `#@` at all
            # emits nothing whatever. Both come back "Verification SUCCESS", and the
            # headline "84 of 104 modules verify" counted them alongside the `os`
            # filesystem model. This is the claim-vacuity shape applied to the TCB
            # appendix's own load-bearing sentence, and it is DERIVED (recomputed every
            # run from the source) rather than a name list, so a module that gains a
            # postcondition leaves the class by itself.
            src = open(f, encoding="utf-8", errors="replace").read()
            n_ann = len(_re.findall(r"^\s*#@", src, _re.M))
            n_ens = len(_re.findall(r"^\s*#@\s*ensures", src, _re.M))
            # A THIRD DISTINCTION, and the run that produced 9 -> 7 + 2 is what showed
            # it was needed: `fut` and `world` have a `def`, but their ONLY def is
            # `__init__`, which returns None and can have no `\result` to claim. Counting
            # them with `udata` (which has value-returning functions and promises nothing
            # about them) put two innocent modules in the informative class. So the
            # discriminator is a def that is NOT a constructor.
            n_def = len([_m for _m in _re.findall(r"^\s*def\s+(\w+)\s*\(", src, _re.M)
                         if _m not in ("__init__", "__new__")])
            if n_ann == 0:
                no_ann.append(rel)
            if n_ens == 0:
                # SPLIT THE CLASS, because the two halves are not the same fact. A module
                # with NO `def` at all (a constant list, a re-export shim, empty class
                # stubs) verifies with no postcondition because there is nothing to claim
                # — innocent, and the count should say so. A module WITH function bodies
                # and no postcondition is the informative half: it computes something and
                # promises nothing.
                (vacuous if n_def else no_defs).append(rel)
        if args.verbose:
            print("    %-10s %s" % (verdict, rel))

    print("[*] stdlib-modules-verify: %d module(s); %d VERIFY, %d do not (%s)."
          % (len(files), len(files) - len(bad), len(bad),
             ", ".join("%s %d" % (k, sum(1 for v in bad.values() if v == k))
                       for k in ("FAILS", "REFUSED", "TIMEOUT"))))
    _v = len(files) - len(bad)
    print("[*] stdlib-modules-verify: of the %d that VERIFY, %d have FUNCTION BODIES and "
          "no `#@ ensures` (they compute something and promise nothing) and %d have no "
          "VALUE-RETURNING function at all (a constant list, a re-export shim, empty class "
          "stubs, or only `__init__` — nothing to claim, and innocent). %d carry no `#@` "
          "annotation whatever. The honest "
          "headline is %d module(s) with a postcondition to discharge, not %d."
          % (_v, len(vacuous), len(no_defs), len(no_ann),
             _v - len(vacuous) - len(no_defs), _v))
    if args.verbose:
        for rel in sorted(vacuous):
            print("    NO-ENSURES  %s   [has function bodies]" % rel)
        for rel in sorted(no_defs):
            print("    NO-DEFS     %s   [nothing to claim]" % rel)

    rc = 0
    for rel in sorted(set(bad) - set(BASELINE)):
        print("[!]   NEWLY NOT VERIFYING: %s (%s). The TCB appendix says a consumer's "
              "contracts are discharged by the library's own machine-checked proofs; this "
              "module no longer has one." % (rel, bad[rel]), file=sys.stderr)
        rc = 1
    for rel in sorted(set(BASELINE) - set(bad)):
        print("[+]   %s NOW VERIFIES — remove its baseline entry." % rel)
    if len(vacuous) > MAX_NO_ENSURES:
        print("[!]   NO-ENSURES COUNT GREW: %d > %d. A module that verifies while claiming "
              "nothing about any return value is not evidence for the TCB appendix's "
              "sentence; this count may only shrink." % (len(vacuous), MAX_NO_ENSURES),
              file=sys.stderr)
        rc = 1

    if rc:
        print("[!] stdlib-modules-verify: NOT OK.", file=sys.stderr)
    else:
        print("[+] stdlib-modules-verify: OK — the non-verifying set is the known one "
              "(%d module(s)); %d module(s) with BODIES verify with no postcondition "
              "(ceiling %d), plus %d with no `def` at all."
              % (len(bad), len(vacuous), MAX_NO_ENSURES, len(no_defs)))
    return rc


if __name__ == "__main__":
    sys.exit(main())
