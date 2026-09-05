#!/usr/bin/env python3
"""NO CORPUS DRIVER MAY CRASH THE PIPELINE — a hard 0.

THE DEFECT CLASS. PyCSL's answer to a construct it cannot model faithfully is a
REFUSAL: `[!] PIPELINE ERROR:` followed by a message that names the construct and says
why. An INTERNAL CRASH — `[!] UNEXPECTED PIPELINE ERROR:` followed by a Python
exception string — is a different thing wearing the same exit code. It is fail-closed
only for as long as nothing catches it, it tells the reader nothing, and, most
importantly here, IT IS INVISIBLE TO THE REFERENCE SUITE: a `# pycsl-expected: FAIL`
test passes whether it refuses cleanly or dies on an `AttributeError`.

That is not hypothetical. `pycsl-reference/0540` sat in the corpus as a red test for at
least two relaunches with

    [!] UNEXPECTED PIPELINE ERROR: 'str' object has no attribute 'get'

and the cause was an IR-KEY COLLISION — `type_params` written by two producers with two
incompatible shapes — which turned out to be a real defect worth fixing on its own
terms, not the "unimplemented syntax" the test's own docstring claimed. Relaunch #45
found a second instance the same day (an unknown `#@ proof` citation raising
`NameError` because `PyCSLIRError` was never imported).

WHAT THIS GATE DOES. It runs every `pycsl-reference` driver through the front end and
Module 6 with `--no-proof --no-typecheck` — emission only, which is where a crash of
this kind occurs — and fails on any `UNEXPECTED PIPELINE ERROR`. Hard 0: a refusal that
crashes is never correct, whatever the driver was trying to do.

It is deliberately NOT limited to expected-FAIL drivers. A crash in a driver that is
supposed to PASS is louder, but the suite catches that one; the ones the suite cannot
see are exactly the expected-FAIL population.
"""
import argparse
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORPUS = os.path.join(ROOT, "test-suite", "corpus", "pycsl-reference")
PY = os.path.join(ROOT, ".venv", "bin", "python3")
if not os.path.exists(PY):
    PY = sys.executable
PYCSL = os.path.join(ROOT, "src", "pycsl", "pycsl.py")
MIN_FILES = 900          # zero-input guard; the corpus only grows


def run_one(path):
    flags = []
    with open(path, errors="replace") as fh:
        for line in fh:
            if line.startswith("# pycsl-flags:"):
                flags = line.split(":", 1)[1].split()
                break
    cmd = [PY, PYCSL, "--no-proof", "--no-typecheck"] + flags + [path]
    env = dict(os.environ, PYTHONHASHSEED="0")
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=300,
                             env=env, cwd=ROOT)
    except subprocess.TimeoutExpired:
        return None
    blob = (out.stdout or "") + (out.stderr or "")
    if "UNEXPECTED PIPELINE ERROR" in blob:
        detail = ""
        for i, l in enumerate(blob.splitlines()):
            if "UNEXPECTED PIPELINE ERROR" in l:
                rest = blob.splitlines()[i + 1:i + 2]
                detail = rest[0].strip() if rest else ""
                break
        return (os.path.basename(path), detail)
    return None


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--jobs", type=int, default=6)
    args = ap.parse_args()

    files = sorted(os.path.join(CORPUS, f) for f in os.listdir(CORPUS)
                   if f.endswith(".py"))
    if len(files) < MIN_FILES:
        print("[!] internal-crash-free: only %d driver(s) found — the corpus path or "
              "glob is broken. NOT A PASS." % len(files))
        return 2

    with ThreadPoolExecutor(max_workers=args.jobs) as ex:
        results = [r for r in ex.map(run_one, files) if r is not None]

    print("[*] internal-crash-free: %d pycsl-reference driver(s) run through the "
          "front end + Module 6 (emission only); %d produced an INTERNAL CRASH."
          % (len(files), len(results)))
    for name, detail in sorted(results):
        print("    CRASH  %-52s %s" % (name, detail))
    if results:
        print("[-] internal-crash-free: an `UNEXPECTED PIPELINE ERROR` is a crash "
              "wearing a refusal's exit code, and the reference suite cannot see it "
              "on an expected-FAIL driver. Hard 0.")
        return 1
    print("[+] internal-crash-free: OK — 0 (hard ratchet).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
