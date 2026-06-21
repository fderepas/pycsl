#!/usr/bin/env python3
"""Tier-1 false-twin (spec mutation) harness — DRAFT.

Soundness discipline (soundness-issue.md, Tier 1). A verifier must REJECT a wrong
spec. This harness mutates a PROVEN postcondition into a provably-WRONG one and
asserts the proof now FAILS. A mutant that still reports `Verification SUCCESS` is
a false-green by *some* mechanism — the merge-collapse bug fixed in fa3668d, a
future emitter bug, a vacuous context, etc. Unlike `--check-vacuity` (which only
catches an INCONSISTENT context), this catches "the tool proved something false"
regardless of cause, end-to-end through the whole prove → merge → success stack.

Mutation operators (conservative — only well-typed, guaranteed-false flips):
  * `#@ ensures \result == <int>`   ->  `\result == <int+1>`
  * `#@ ensures \result == <int>`   ->  `\result == <int-1>`   (when int+1 form is degenerate)
A proven `\result == N` pins the unique returned value, so `== N±1` is necessarily
false on the reachable path; the proof MUST fail. One mutant per ensures line, run
independently, with proof FORCED ON (any `--no-proof` in the file's pycsl-flags is
overridden — a false twin is meaningless without proving).

STATUS: draft. Runnable now (`--self-test`, or pass test files). NOT yet wired into
CI; intended to become a gate over src/pycsl_lib_test/ and the proof corpus.

Usage:
    bin/false-twin.py --self-test
    bin/false-twin.py src/pycsl_lib_test/formal_os_query.py [more files...]
    bin/false-twin.py --glob 'src/pycsl_lib_test/formal_*.py'

Exit code: 0 if every mutant correctly FAILED; 1 if any mutant SURVIVED (false-green)
or the harness could not run.
"""
from __future__ import annotations

import argparse
import glob as _glob
import os
import re
import subprocess
import sys
import tempfile
from typing import List, Optional, Tuple

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PYCSL = os.path.join(ROOT, "src", "pycsl", "pycsl.py")
PYTHON = os.path.join(ROOT, ".venv", "bin", "python3")
if not os.path.exists(PYTHON):
    PYTHON = sys.executable

# `#@ ensures \result == <int>`  (optionally parenthesised, with surrounding text).
_ENSURES_RESULT_EQ_INT = re.compile(
    r'(#@\s*ensures\b[^\n]*?\\result\s*==\s*)(-?\d+)(\b)')


def _mutants(source: str) -> List[Tuple[str, str]]:
    """Return [(label, mutated_source)] — one per mutatable `\result == N` ensures."""
    out: List[Tuple[str, str]] = []
    lines = source.splitlines(keepends=True)
    for i, line in enumerate(lines):
        m = _ENSURES_RESULT_EQ_INT.search(line)
        if not m:
            continue
        n = int(m.group(2))
        flipped = n + 1
        new_line = line[:m.start(2)] + str(flipped) + line[m.end(2):]
        mutated = "".join(lines[:i] + [new_line] + lines[i + 1:])
        out.append((f"line{i+1}:result=={n}->{flipped}", mutated))
    return out


def _run_pycsl(path: str) -> Tuple[bool, str]:
    """Run pycsl with proof FORCED ON. Returns (reported_success, tail_of_output)."""
    cmd = [PYTHON, PYCSL, path]   # no --no-proof: a false twin must actually prove
    env = dict(os.environ, PYTHONHASHSEED="0")
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=600, env=env)
    except subprocess.TimeoutExpired:
        return False, "<timeout>"   # timeout = not a success = mutant correctly killed
    out = r.stdout + "\n" + r.stderr
    success = "[+] Verification SUCCESS" in out
    return success, out.strip().splitlines()[-1] if out.strip() else ""


def _check_file(path: str) -> Tuple[int, int, List[str]]:
    """Mutate `path`, run each mutant. Returns (killed, total, survivors[])."""
    src = open(path).read()
    muts = _mutants(src)
    killed = 0
    survivors: List[str] = []
    for label, mutated in muts:
        fd, tmp = tempfile.mkstemp(suffix=".py", prefix=".ftwin_",
                                   dir=os.path.dirname(os.path.abspath(path)))
        try:
            with os.fdopen(fd, "w") as f:
                f.write(mutated)
            success, _tail = _run_pycsl(tmp)
            if success:
                survivors.append(f"{os.path.basename(path)} :: {label}")
            else:
                killed += 1
        finally:
            if os.path.exists(tmp):
                os.remove(tmp)
    return killed, len(muts), survivors


def _self_test() -> int:
    """The canonical regression witness for the merge false-green: getpid_constant's
    `\result == 1` mutated to `== 2` MUST fail. If it survives, the bug is back."""
    target = os.path.join(ROOT, "src", "pycsl_lib_test", "formal_os_query.py")
    if not os.path.exists(target):
        print(f"[!] self-test target missing: {target}")
        return 1
    src = open(target).read()
    mut = re.sub(r'(#@\s*ensures\s*\\result\s*==\s*)1\b(\s*\n(?:#@[^\n]*\n)*def getpid_constant)',
                 r'\g<1>2\g<2>', src, count=1)
    if mut == src:
        print("[!] self-test could not locate getpid_constant's ensures")
        return 1
    fd, tmp = tempfile.mkstemp(suffix=".py", prefix=".ftwin_self_",
                               dir=os.path.dirname(target))
    try:
        with os.fdopen(fd, "w") as f:
            f.write(mut)
        success, tail = _run_pycsl(tmp)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)
    if success:
        print("[-] SELF-TEST FAILED: getpid_constant `\\result == 2` SURVIVED "
              "(false-green is back — the merge collapse has regressed).")
        return 1
    print("[+] self-test passed: getpid_constant `\\result == 2` correctly FAILED.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Tier-1 false-twin (spec mutation) harness")
    ap.add_argument("files", nargs="*", help="PyCSL test files to mutate")
    ap.add_argument("--glob", help="glob of files to mutate")
    ap.add_argument("--self-test", action="store_true",
                    help="run the getpid_constant regression witness only")
    args = ap.parse_args()

    if args.self_test:
        return _self_test()

    files = list(args.files)
    if args.glob:
        files += _glob.glob(args.glob)
    if not files:
        ap.print_help()
        return 1

    total_killed = total_muts = 0
    all_survivors: List[str] = []
    for path in files:
        killed, n, survivors = _check_file(path)
        total_killed += killed
        total_muts += n
        all_survivors += survivors
        mark = "ok" if not survivors else "SURVIVORS"
        print(f"[{mark}] {os.path.basename(path)}: {killed}/{n} mutants killed")

    print(f"\nTotal: {total_killed}/{total_muts} mutants killed.")
    if all_survivors:
        print("[-] SURVIVING MUTANTS (false-greens — the verifier proved a wrong spec):")
        for s in all_survivors:
            print(f"    {s}")
        return 1
    print("[+] All mutants killed — no false-greens detected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
