#!/usr/bin/env python3
r"""L-PLANE ORACLE: what the import classifier's TRUSTED_STUB label actually resolves, and
which `pycsl_lib` package names would SHADOW a real stdlib module the day it resolves
anything.

WHY THIS EXISTS (gen #30). Two other stdlib planes rest their soundness argument on one
sentence: the facade gate says its `os` stubs are sound today because "nothing substitutes
these contracts for the real module (no name map takes `os` to `pycsl_lib/os`)", and the
identity-stub gate inherits it. That sentence was an ASSERTION. This gate measures it, and
the measurement is sharper than the assertion in both directions.

WHAT WAS MEASURED. `frontend/import_classifier.py` classifies every import as
TRUSTED_STUB / UNVERIFIED / UNRESOLVED, and its own docstring calls the stub set "the
trusted-stub mechanism PyCSL already uses for stdlib coverage". Its `_stub_set` is

    {p.stem for p in stub_dir.iterdir() if p.suffix == ".py"}

and `src/pycsl_lib/` holds 93 PACKAGES and exactly ONE top-level `.py` file, its own
`__init__.py`. So the stub set is `{"__init__"}` and **TRUSTED_STUB is unreachable for
every stub in the layer**. The docstring's parenthetical says why: the layer was "renamed
from `data/lib_stubs/`", a FLAT directory of `.py` files, and the glob was never renamed
with it. Nothing downstream branches on the label (only UNVERIFIED raises), which is
exactly why nobody noticed.

THE SECOND REASON, INDEPENDENT OF THE FIRST. Even with the glob repaired, a stub is found
by ITS OWN NAME — `mth`, `bsect`, `txtwrp` — and `pycsl_lib/mth/__init__.py` says in its
first lines that it is "Named 'mth' to avoid stdlib name clash". A user writes `import
math`, never `import mth`, so the repaired lookup would still resolve nothing for the
modules the naming convention covers.

THE DANGER THAT SURVIVES BOTH. NINE package names were NOT renamed and collide with real
stdlib modules: copyreg, errno, http, json, os, re, reprlib, stat, token. On the day
someone "fixes" `_stub_set` to see packages — a one-line, obviously-correct-looking
change — `import os`, `import json` and `import re` in USER code begin resolving to this
layer's integer models, and the facade gate's pinned constants become claims about the
real world: `os.islink(p) == 0` is then a proof that nothing is ever a symlink.

WHAT THIS GATE HOLDS.
  1. The live `_stub_set` result is what it is measured to be (`{"__init__"}`). If it ever
     grows, the fix must be argued through item 3, not merged as a typo repair.
  2. The package census, with a floor, so "no collisions" can never mean "I saw no
     packages".
  3. The COLLISION SET, baselined by name. A new `pycsl_lib` package whose name is a real
     stdlib module name fails: renaming it (the `mth` convention) is the cheap fix, and
     doing it before the glob is repaired is the whole point.
  4. The count of PINNED FACADES and IDENTITY STUBS that live in colliding packages — the
     contracts that would go from "true of the body" to "false of the world" on that day.

Usage:  bin/check-stub-import-resolution.py [--verbose]
"""
import argparse
import glob
import importlib.util
import os
import sys
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIB = os.path.join(ROOT, "src", "pycsl_lib")
MIN_PACKAGES = 80          # 93 at the first measurement

# The stub set the LIVE `_stub_set` returns today. Not a wish: a measurement.
EXPECTED_STUB_SET = {"__init__"}

# `pycsl_lib` package names that ARE real stdlib module names. Baselined so a NEW one
# fails and has to be renamed under the `mth` convention instead.
COLLISIONS = {
    "copyreg", "errno", "http", "json", "os", "re", "reprlib", "stat", "token",
}


def live_stub_set():
    """Call the SHIPPING `_stub_set` on the SHIPPING directory — no reimplementation."""
    src = os.path.join(ROOT, "src", "pycsl")
    sys.path.insert(0, src)
    try:
        spec = importlib.util.spec_from_file_location(
            "_ic", os.path.join(src, "frontend", "import_classifier.py"))
        ic = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(ic)
        return ic, set(ic._stub_set(Path(LIB)))
    finally:
        sys.path.remove(src)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--selftest-fake-stub-dir", action="store_true",
                    help="point the walk at a scratch layer that DOES ship top-level .py "
                         "stubs, including `os.py`; must exit 1 (proves the gate bites "
                         "on the day the lookup starts resolving)")
    args = ap.parse_args()

    global LIB
    if args.selftest_fake_stub_dir:
        import tempfile
        tmp = tempfile.mkdtemp(prefix="stubres-selftest-")
        for i in range(MIN_PACKAGES + 1):
            os.makedirs(os.path.join(tmp, "pkg%d" % i))
            open(os.path.join(tmp, "pkg%d" % i, "__init__.py"), "w").close()
        open(os.path.join(tmp, "os.py"), "w").close()
        LIB = tmp

    packages = sorted(os.path.basename(os.path.dirname(p))
                      for p in glob.glob(os.path.join(LIB, "*", "__init__.py")))
    if len(packages) < MIN_PACKAGES:
        print("[!] stub-import-resolution: REFUSING — %d package(s) found, expected at "
              "least %d. The walk is broken; this is not a pass."
              % (len(packages), MIN_PACKAGES), file=sys.stderr)
        return 2

    try:
        ic, stubs = live_stub_set()
    except Exception as exc:
        print("[!] stub-import-resolution: REFUSING — could not load the live import "
              "classifier: %r" % (exc,), file=sys.stderr)
        return 2

    collide = sorted(p for p in packages if p in sys.stdlib_module_names)
    rc = 0

    if stubs != EXPECTED_STUB_SET:
        print("[!]   THE LIVE STUB SET CHANGED: %s (expected %s). TRUSTED_STUB now "
              "resolves something it did not before. Before accepting this, check the "
              "collision list below: a package named `os`, `json` or `re` that the "
              "classifier can suddenly SEE makes this layer's integer models shadow the "
              "real module for user code."
              % (sorted(stubs), sorted(EXPECTED_STUB_SET)), file=sys.stderr)
        rc = 1

    new_collisions = sorted(set(collide) - COLLISIONS)
    gone_collisions = sorted(COLLISIONS - set(collide))
    for name in new_collisions:
        print("[!]   NEW COLLIDING PACKAGE `pycsl_lib/%s` — that is a real stdlib module "
              "name. Rename it under the `mth`/`bsect`/`txtwrp` convention (the layer's "
              "own stated reason for those names is 'to avoid stdlib name clash')."
              % name, file=sys.stderr)
        rc = 1
    for name in gone_collisions:
        print("[+]   collision `%s` is GONE — remove it from COLLISIONS." % name)

    # How much contract would change meaning on the day the lookup resolves.
    exposed = {"facades": 0, "identity": 0}
    for plane, key in (("check-stdlib-pinned-facades.py", "facades"),
                       ("check-stdlib-identity-stubs.py", "identity")):
        try:
            spec = importlib.util.spec_from_file_location(
                "_p_" + key, os.path.join(ROOT, "bin", plane))
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            exposed[key] = sum(1 for (pkg, _fn) in mod.BASELINE if pkg in COLLISIONS)
        except Exception as exc:
            print("[!]   could not read %s's baseline: %r" % (plane, exc), file=sys.stderr)
            rc = 1

    if args.verbose:
        print("    live stub set: %s" % sorted(stubs))
        print("    colliding packages: %s" % collide)

    print("[*] stub-import-resolution: %d package(s); live stub set %s; %d colliding "
          "name(s); %d pinned facade(s) and %d identity stub(s) sit in colliding packages."
          % (len(packages), sorted(stubs), len(collide),
             exposed["facades"], exposed["identity"]))

    if rc:
        print("[!] stub-import-resolution: NOT OK.", file=sys.stderr)
    else:
        print("[+] stub-import-resolution: OK — TRUSTED_STUB resolves nothing in this "
              "layer (the glob sees files, the layer ships packages), and the %d "
              "colliding package name(s) are the known ones." % len(collide))
    return rc


if __name__ == "__main__":
    sys.exit(main())
