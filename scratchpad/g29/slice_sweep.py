#!/usr/bin/env python3
"""ROUTE #190's completeness evidence: an EXHAUSTIVE sweep of string-slice bounds.

Route #190 was found with four hand spellings. This walks the whole small neighbourhood —
every (lower, upper) pair drawn from {absent, -3..3} on a fixed 5-character string — and
for each one runs the real pipeline TWICE:

  * with a claim that is FALSE of the program (CPython's answer + 1). A `Verification
    SUCCESS` here is a FALSE PROOF: the model decided a wrong length.
  * with the claim that is TRUE. A SUCCESS here is COMPLETENESS (the model knows the real
    length); a failure is merely incomplete, and is reported but not a finding.

Usage:  slice_sweep.py <tree-root> [out-dir]
"""
import os
import subprocess
import sys

ROOT = sys.argv[1] if len(sys.argv) > 1 else "/home/fabrice/git/pycsl"
OUT = sys.argv[2] if len(sys.argv) > 2 else "/tmp/g29_slice_sweep"
PYCSL = os.path.join(ROOT, "src", "pycsl", "pycsl.py")
PY = "/home/fabrice/git/pycsl/.venv/bin/python3"
S = "abcde"

BOUNDS = [None, -3, -2, -1, 0, 1, 2, 3]


def spell(b):
    if b is None:
        return ""
    if b < 0:
        return "0 - %d" % (-b,)
    return str(b)


def run(src, path):
    open(path, "w").write(src)
    try:
        out = subprocess.run([PY, PYCSL, path], capture_output=True, text=True,
                             timeout=400,
                             env={**os.environ, "PYTHONHASHSEED": "0"}).stdout
    except subprocess.TimeoutExpired:
        return "TIMEOUT"
    if "PIPELINE ERROR" in out:
        return "REFUSED"
    if "Verification SUCCESS" in out:
        return "SUCCESS"
    return "FAILED"


os.makedirs(OUT, exist_ok=True)
false_proofs, complete, incomplete, refused = [], [], [], []
for lo in BOUNDS:
    for hi in BOUNDS:
        real = len(S[(lo if lo is not None else None):(hi if hi is not None else None)])
        tag = "%s_%s" % (spell(lo) or "x", spell(hi) or "x")
        tag = tag.replace(" ", "").replace("-", "m")
        body = ('_ = 0  # anchor\n\n\n#@ ensures \\result == %d\n'
                'def probe() -> int:\n    s: str = "%s"\n    t: str = s[%s:%s]\n'
                '    return len(t)\n')
        # MORE THAN ONE WRONG ANSWER PER CELL. The first version of this sweep claimed
        # `real + 1` only and reported zero on a tree where route #190 was live: the
        # model's wrong answer there is 0 (an ERASED value), not `real + 1`. Ask about
        # both, and count the cell as a false proof if EITHER proves.
        vf = "FAILED"
        for _bad in (0, real + 1):
            if _bad == real:
                continue
            _v = run(body % (_bad, S, spell(lo), spell(hi)),
                     os.path.join(OUT, "false%d_%s.py" % (_bad, tag)))
            if _v == "SUCCESS":
                vf = "SUCCESS"
                break
            if _v == "REFUSED":
                vf = "REFUSED"
        vt = run(body % (real, S, spell(lo), spell(hi)),
                 os.path.join(OUT, "true_%s.py" % tag))
        if vf == "SUCCESS":
            false_proofs.append((spell(lo), spell(hi), real))
            print("FALSE-PROOF s[%s:%s] real=%d" % (spell(lo), spell(hi), real), flush=True)
        elif vf == "REFUSED":
            refused.append((spell(lo), spell(hi)))
        if vt == "SUCCESS":
            complete.append((spell(lo), spell(hi)))
        elif vt == "FAILED":
            incomplete.append((spell(lo), spell(hi), real))
print("SLICE-SWEEP-DONE cells=%d false_proofs=%d complete=%d incomplete=%d refused=%d"
      % (len(BOUNDS) ** 2, len(false_proofs), len(complete), len(incomplete), len(refused)),
      flush=True)
