#!/usr/bin/env python3
r"""L-PLANE: does the reference corpus RUN AS PYTHON?

WHY THIS EXISTS (gen #31). Every other instrument in this battery executes a corpus
function BECAUSE A CLAUSE ASKED IT TO. `check-corpus-contract-truth` runs a function when it
finds `#@ ensures \result == <literal>`; its parameterized sibling when it finds a clause
over the parameters. Neither ever asks the question underneath both of them:

    IS THIS FILE A PYTHON PROGRAM THAT RUNS?

Asked directly, in one afternoon, it found a `# pycsl-expected: PASS` driver that raises
`NameError` AT IMPORT (`1190_route76_accessor_positive_control.py` used `@mutable_state` and
defined it nowhere — not one function that fails, the whole module), and two driver
SELF-CHECKS that had never executed in any run, ever:

    0312.py   assert test_ghost_list_mem(0) == 0     the file defines `..._nth`. NameError.
    0452.py   assert echo_bytes(b"...") == list(...) `bytearray == list` is False in Python
                                                     however equal the elements are.

A self-check nobody runs is a comment. This plane runs them.

WHAT IT DOES NOT CHECK. Nothing about contracts, proofs or emission — those have five
instruments each. This one has exactly two questions and they are both about CPython.

THE RATCHETS (the #44 rule: a gate that cannot tell "nothing is wrong" from "I looked at
nothing" is not a gate): rc=2 below MIN_LOADED / MIN_SELFCHECKED; rc=1 for any failure not
NAMED below with its reason. A named entry that stops failing is also reported — that is
good news, and good news has to be recorded rather than silently absorbed.

Usage:  bin/check-corpus-executes.py [--verbose]
"""
import argparse
import contextlib
import glob
import io
import os
import re
import signal
import sys
import subprocess
import types
import warnings

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORPORA = [os.path.join(ROOT, "test-suite", "corpus", "pycsl-reference"),
           os.path.join(ROOT, "test-suite", "corpus", "python-reference")]
TIMEOUT = 5.0
MIN_LOADED = 1375          # measured 1384 — ALL of them — once 0065/0186/0187 (the
                           # circular fixture's import form) and 1190 (`@mutable_state`
                           # used and never defined) were repaired. 1377 when this plane
                           # was first run. Both corpora only grow.
MIN_SELFCHECKED = 835      # measured 844 — ALL of them — once 0312 (a self-check naming a
                           # function the file does not define) and 0452 (a `bytearray`
                           # compared with a `list`) were repaired. 839 when this plane was
                           # first run.

# A file whose MODULE BODY does not load under this harness. Each one NAMED, with what a
# package context does to it — because "the instrument cannot load it" and "the program
# cannot load" are different sentences and only the second is a defect.
KNOWN_LOAD_FAILURES = {}

# A file with a LEADING-DOT import is not runnable by `exec`ing it standalone — a relative
# import needs a parent package, and that is a property of the INVOCATION, not of the
# program. `0061` exists precisely to test `from .mod import name`. So those files are run
# the way Python runs them: as a package module, in a subprocess, from the repo root. The
# first version of this plane listed them as KNOWN_LOAD_FAILURES with an explanation, which
# is the honest version of "my harness cannot do this" — and then the harness learned to,
# and the table is EMPTY. An explanation in an exclusion table is a debt, not a fact.
RELATIVE_IMPORT = re.compile(r"^\s*from\s+\.", re.M)
# A file whose own `if __name__ == \"__main__\"` self-check raises. Empty is the goal.
KNOWN_SELFCHECK_FAILURES = {}


def _alarm(_sig, _frm):
    raise TimeoutError("module body timed out")


def _files():
    out = []
    for c in CORPORA:
        out += sorted(glob.glob(os.path.join(c, "*.py")))
    return sorted(set(out))


def _run(f, src, as_main):
    """Exec a corpus file. Returns None on success, else (exception type, message).

    The namespace is a REGISTERED `types.ModuleType`, not a bare dict. `dataclasses`
    resolves string annotations (any file with `from __future__ import annotations`)
    through `sys.modules[cls.__module__].__dict__`, and a bare dict gives
    `'NoneType' object has no attribute '__dict__'` — SEVENTEEN files reported as load
    failures on the first run of this probe, every one of which loads perfectly well under
    `python3 <file>`. The probe has to measure the program, not itself.
    """
    d = os.path.dirname(f)
    name = ("corpus_exec_probe_"
            + os.path.basename(f).replace(".", "_").replace("-", "_")
            + ("__main" if as_main else ""))
    mod = types.ModuleType(name)
    sys.modules[name] = mod
    ns = mod.__dict__
    ns["__name__"] = "__main__" if as_main else name
    ns["__file__"] = f
    sys.path.insert(0, d)
    # (#49) gen #31 — SNAPSHOT `sys.modules`. A corpus file that imports `multi_file_lib.*`
    # leaves those modules cached, and a CIRCULAR fixture leaves one cached in a
    # PARTIALLY-INITIALISED state. Without this the plane's verdict depends on FILE ORDER:
    # 0065 failed, left `circ_a` half-built in the cache, and 0186 then "passed" by reusing
    # it while 0187 failed. Three files, one defect, two different answers. Restoring the
    # cache gives every file the import state it would have in its own interpreter.
    _mods0 = dict(sys.modules)
    try:
        with contextlib.redirect_stdout(io.StringIO()), \
             contextlib.redirect_stderr(io.StringIO()):
            signal.setitimer(signal.ITIMER_REAL, TIMEOUT)
            exec(compile(src, f, "exec"), ns)
            signal.setitimer(signal.ITIMER_REAL, 0)
        return None
    except BaseException as e:
        signal.setitimer(signal.ITIMER_REAL, 0)
        return (type(e).__name__, str(e)[:90])
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        if sys.path and sys.path[0] == d:
            sys.path.pop(0)
        sys.modules.pop(name, None)
        for _k in [k for k in sys.modules if k not in _mods0]:
            del sys.modules[_k]
        sys.modules.update(_mods0)


def _run_as_package_module(f):
    """`python3 -m <dotted path>` from the repo root, which is how Python runs a module
    whose imports are relative. Both the load and the `__main__` self-check happen in that
    one invocation, because `-m` sets `__name__` to `"__main__"` by definition."""
    rel = os.path.relpath(f, ROOT)[:-3].replace(os.sep, ".")
    try:
        p = subprocess.run([sys.executable, "-m", rel], cwd=ROOT,
                           capture_output=True, timeout=TIMEOUT * 4)
    except subprocess.TimeoutExpired:
        return ("TimeoutError", "`python3 -m %s` timed out" % rel)
    if p.returncode == 0:
        return None
    tail = (p.stderr.decode("utf-8", "replace").strip().split("\n") or [""])[-1]
    return ("ExitCode%d" % p.returncode, tail[:90])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()
    signal.signal(signal.SIGALRM, _alarm)

    loaded = checked = skipped = 0
    load_bad, self_bad = {}, {}
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for f in _files():
            src = open(f, errors="replace").read()
            if "# pycsl-expected: FAIL" in src:
                skipped += 1
                continue
            if re.search(r"^# pycsl-flags:.*--no-proof", src, re.M):
                skipped += 1
                continue
            base = os.path.basename(f)
            if RELATIVE_IMPORT.search(src):
                err = _run_as_package_module(f)
                if err is None:
                    loaded += 1
                    checked += 1 if "__main__" in src else 0
                else:
                    load_bad[base] = err
                continue
            err = _run(f, src, as_main=False)
            if err is None:
                loaded += 1
            else:
                load_bad[base] = err
                continue                      # a file that will not load has no self-check
            if "__main__" not in src:
                continue
            err = _run(f, src, as_main=True)
            if err is None:
                checked += 1
            else:
                self_bad[base] = err

    print("[*] corpus-executes: %d of %d PASS-expected proof-on file(s) LOAD under CPython; "
          "%d of %d with a `__main__` block pass their OWN self-check. (%d skipped: "
          "expected-FAIL or `--no-proof`.)"
          % (loaded, loaded + len(load_bad), checked, checked + len(self_bad), skipped))

    rc = 0
    for base, (typ, msg) in sorted(load_bad.items()):
        why = KNOWN_LOAD_FAILURES.get(base)
        if why is None:
            print("[!]   DOES NOT LOAD: %s — %s: %s. A `# pycsl-expected: PASS` driver that "
                  "is not a Python program is not one function that fails, it is the whole "
                  "module — and nothing else in this battery reads a corpus file AS A "
                  "PROGRAM. Repair it, or name it in KNOWN_LOAD_FAILURES with the reason."
                  % (base, typ, msg), file=sys.stderr)
            rc = 1
        elif args.verbose:
            print("    known-load-failure  %-10s %s" % (base, why))
    for base, (typ, msg) in sorted(self_bad.items()):
        why = KNOWN_SELFCHECK_FAILURES.get(base)
        if why is None:
            print("[!]   SELF-CHECK FAILS: %s — %s: %s. The driver's own `__main__` "
                  "assertion, written by its author about its own program, is FALSE. A "
                  "self-check nobody runs is a comment. Repair it, or name it in "
                  "KNOWN_SELFCHECK_FAILURES with the reason."
                  % (base, typ, msg), file=sys.stderr)
            rc = 1
        elif args.verbose:
            print("    known-selfcheck-failure  %-10s %s" % (base, why))

    for base in sorted(set(KNOWN_LOAD_FAILURES) - set(load_bad)):
        print("[!]   KNOWN LOAD FAILURE NO LONGER REPRODUCES: %s. That is GOOD NEWS that has "
              "to be RECORDED — remove it from KNOWN_LOAD_FAILURES in the same commit that "
              "fixed it." % base, file=sys.stderr)
        rc = 1
    for base in sorted(set(KNOWN_SELFCHECK_FAILURES) - set(self_bad)):
        print("[!]   KNOWN SELF-CHECK FAILURE NO LONGER REPRODUCES: %s. Remove it from "
              "KNOWN_SELFCHECK_FAILURES in the same commit that fixed it." % base,
              file=sys.stderr)
        rc = 1

    if loaded < MIN_LOADED or checked < MIN_SELFCHECKED:
        print("[!] corpus-executes: REFUSING — only %d loaded and %d self-checked, expected "
              "at least %d and %d. A gate that cannot tell 'nothing is wrong' from 'I looked "
              "at nothing' is not a gate." % (loaded, checked, MIN_LOADED, MIN_SELFCHECKED),
              file=sys.stderr)
        return 2
    if rc:
        print("[!] corpus-executes: NOT OK.", file=sys.stderr)
        return rc
    print("[+] corpus-executes: OK — every PASS-expected corpus file loads as Python, and "
          "every self-check its author wrote passes.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
