#!/usr/bin/env python3
"""Cumulative sibling_concrete marker triage for ONE mirror file.
Usage: triage.py <mirror.py> <meth1> <meth2> ...
Marks each method in turn; emits after each; reverts that one marker if L3-tc fails."""
import os, subprocess, sys, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from mark import mark
from unmark import unmark

ROOT = "/home/fabrice/git/pycsl"
env = dict(os.environ, PYTHONHASHSEED="0",
           PATH="/home/fabrice/.opam/framac-coq8/bin:" + os.environ["PATH"])

def emit(path):
    mlw = path[:-3] + ".mlw"
    if os.path.exists(mlw): os.remove(mlw)
    r = subprocess.run([sys.executable, "src/pycsl/pycsl.py", path,
                        "--import-path", "src/pycsl", "--no-proof", "--keep-mlw"],
                       cwd=ROOT, env=env, capture_output=True, text=True)
    ok = "L3-tc ✓" in r.stdout and "SUCCESS" in r.stdout
    err = ""
    if not ok:
        tail = [l for l in (r.stdout + r.stderr).split("\n") if l.strip()][-3:]
        err = " | ".join(tail)
    if os.path.exists(mlw): os.remove(mlw)
    return ok, err

path = sys.argv[1]
meths = sys.argv[2:]
base_ok, base_err = emit(path)
if not base_ok:
    print("BASE-FAIL", base_err); sys.exit(1)
kept, dropped = [], []
for m in meths:
    st = mark(path, m)
    if st != "MARKED":
        dropped.append((m, st)); continue
    ok, err = emit(path)
    if ok:
        kept.append(m)
    else:
        unmark(path, m)
        dropped.append((m, err[:170]))
print("KEPT:", " ".join(kept) or "(none)")
for m, why in dropped:
    print("  DROPPED", m, "::", why)
