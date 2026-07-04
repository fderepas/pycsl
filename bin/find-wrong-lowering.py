#!/usr/bin/env python3
"""find-wrong-lowering.py — detector harness for the wrong-lowering audit.

Runs a PyCSL driver and classifies the verdict. Used by the D2/D3/D4/D5
probes in getting-better/wrong-lowering/. Re-runnable to catch regressions.

Verdicts:
  PROVEN   — all VCs Valid (default non-vacuity gate ON unless --no-vacuity)
  UNPROVEN — some VC Unknown/Timeout/failed (can't prove)
  TYPEERR  — WhyML type error / pipeline error (ill-typed lowering)
  VACUOUS  — vacuity gate reported a vacuous function

Usage:
  bin/find-wrong-lowering.py run <file.py> [--no-vacuity] [--no-proof]
  bin/find-wrong-lowering.py mlwtype <file.py>   # emit .mlw, print signatures
"""
import subprocess, sys, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PYCSL = os.path.join(ROOT, "src", "pycsl", "pycsl.py")

def run(pyfile, no_vacuity=False, no_proof=False, timeout=180):
    env = dict(os.environ, PYTHONHASHSEED="0")
    cmd = [sys.executable, PYCSL, pyfile]
    if no_vacuity: cmd.append("--no-check-vacuity")
    if no_proof: cmd.append("--no-proof")
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=env)
    except subprocess.TimeoutExpired:
        return "UNPROVEN", "harness-timeout"
    out = p.stdout + p.stderr
    low = out.lower()
    if "vacu" in low and ("fail" in low or "vacuous" in low):
        if re.search(r'vacuous', low):
            return "VACUOUS", out[-400:]
    if ("type error" in low or "typing error" in low or "not typecheck" in low
            or "does not type-check" in low or "l3-tc ✗" in low
            or "this expression has type" in low):
        return "TYPEERR", out[-400:]
    if "verification success" in low or "verification succeeded" in low or "all contracts formally proven" in low:
        return "PROVEN", out[-200:]
    if "no-proof" in low and "success" in low:
        return "PROVEN", out[-200:]
    if "failed" in low or "incomplete" in low or "unproven" in low or "unknown" in low:
        return "UNPROVEN", out[-400:]
    if "error" in low or "exception" in low or "traceback" in low:
        return "TYPEERR", out[-400:]
    return "UNPROVEN", out[-400:]

def mlwtype(pyfile):
    env = dict(os.environ, PYTHONHASHSEED="0")
    subprocess.run([sys.executable, PYCSL, "--keep-mlw", "--no-proof", pyfile],
                   capture_output=True, text=True, env=env)
    mlw = pyfile[:-3] + ".mlw" if pyfile.endswith(".py") else pyfile + ".mlw"
    if not os.path.exists(mlw):
        print("NO MLW"); return
    for line in open(mlw):
        s = line.strip()
        if s.startswith("let ") or s.startswith("val ") or s.startswith("type "):
            print(s)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__); sys.exit(1)
    cmd, f = sys.argv[1], sys.argv[2]
    flags = sys.argv[3:]
    if cmd == "run":
        v, detail = run(f, no_vacuity="--no-vacuity" in flags, no_proof="--no-proof" in flags)
        print(f"{v}\t{f}")
        if "-v" in flags: print(detail)
    elif cmd == "mlwtype":
        mlwtype(f)
