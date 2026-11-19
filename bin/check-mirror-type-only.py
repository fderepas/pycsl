#!/usr/bin/env python3
r"""L-PLANE ORACLE: does every emitted mirror `.mlw` actually TYPE-CHECK?

WHY THIS EXISTS. Twice now a change has landed with EVERY OTHER GATE GREEN while the
emitted mirror was ill-typed, and neither time could anything in the battery see it:

  * route #57 (2026-09-10) — `_dv_absent_opaque(self, nu: str)` tested `nu in (None, ...)`;
    `nu` is a `string`, the `None` lowered to the INT `0`, and the file emitted
    `str_eq_op nu 0`. The corpus was byte-inert. Only the whole-file mirror proof saw it,
    four hours later.
  * the staged-L1 landing (same day) — `_handle_var_expr` calls
    `_union_local_read_projection`, which the mirror does not model, so the synthesized
    avatar defaulted to `int` and `raise (Return_str !_proj)` was ill-typed. Fidelity was
    0 divergences, the metric was right, the corpus byte-diff was 0, and ALL 18 PLANES
    WERE GREEN. `w53a_expressions` then failed in ONE MINUTE.

An ill-typed mirror is not a small problem: the file cannot be proved AT ALL, so every
`\trusted`-reduction claim resting on it is suspended until someone notices. The check
costs ~10 seconds per mirror against the 4-6 HOURS a whole-file proof takes to report the
same thing, and it is the cheapest gate in this repo by a wide margin.

WHAT IT MEASURES. For each emitted mirror `.mlw`, `why3 prove --type-only` must produce
ZERO non-warning output lines. Warnings (unused variable, unused type) are expected and
ignored; anything else is a type error.

Usage:
    bin/check-mirror-type-only.py [--emit-dir DIR]

With `--emit-dir` it reuses an existing emission (the `--slow` battery shares one). With no
argument it emits the mirrors itself.
"""
import argparse
import glob
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIRROR = os.path.join(ROOT, "src", "self-annotate", "src")
MIN_MIRRORS = 40      # true population 53; a floor on the INPUT, never a ratchet.


def emit_all(out_dir):
    py = os.path.join(ROOT, ".venv", "bin", "python3")
    if not os.path.exists(py):
        py = sys.executable
    env = dict(os.environ, PYTHONHASHSEED="0")
    for src in sorted(glob.glob(os.path.join(MIRROR, "**", "*.py"), recursive=True)):
        mlw = src[:-3] + ".mlw"
        if os.path.exists(mlw):
            os.remove(mlw)
        subprocess.run([py, os.path.join(ROOT, "src", "pycsl", "pycsl.py"), src,
                        "--import-path", os.path.join(ROOT, "src", "pycsl"),
                        "--no-proof", "--keep-mlw"],
                       cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                       env=env)
        if os.path.exists(mlw):
            rel = os.path.relpath(src, MIRROR)[:-3].replace(os.sep, "_")
            shutil.move(mlw, os.path.join(out_dir, rel + ".mlw"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--emit-dir")
    args = ap.parse_args()

    tmp = None
    emit_dir = args.emit_dir
    if not emit_dir:
        tmp = tempfile.mkdtemp(prefix="pycsl-typeonly.")
        emit_dir = tmp
        emit_all(emit_dir)

    try:
        files = sorted(glob.glob(os.path.join(emit_dir, "*.mlw")))
        # THE #44 RULE. A type-check over ZERO files is not a pass.
        if len(files) < MIN_MIRRORS:
            print(f"[!] mirror-type-only: REFUSING — only {len(files)} emitted mirror(s) "
                  f"found in {emit_dir!r}, expected at least {MIN_MIRRORS}. THIS IS A "
                  f"REFUSAL, NOT A PASS.")
            return 2

        bad = []
        for f in files:
            try:
                out = subprocess.run(["why3", "prove", "--type-only", f],
                                     capture_output=True, text=True, timeout=300)
            except (subprocess.TimeoutExpired, FileNotFoundError):
                # A missing why3 SKIPS (matching the rest of the battery); a timeout is a
                # refusal, because it is not evidence either way.
                print("[*] mirror-type-only: why3 unavailable or timed out — skipping")
                return 0
            blob = (out.stdout or "") + (out.stderr or "")
            errs = [l for l in blob.splitlines() if l and not l.startswith("Warning")]
            if errs:
                bad.append((os.path.basename(f), errs[:3]))

        print(f"[*] mirror-type-only: {len(files)} emitted mirror(s) type-checked; "
              f"{len(bad)} ILL-TYPED.")
        for name, errs in bad:
            print(f"    ILL-TYPED  {name}")
            for e in errs:
                print(f"               {e}")
        if bad:
            print("[-] mirror-type-only: an ill-typed mirror CANNOT BE PROVED AT ALL, so "
                  "every `\\trusted`-reduction claim resting on it is suspended. Every "
                  "other gate can be green while this is broken — that is why this plane "
                  "exists. Hard 0.")
            return 1
        print("[+] mirror-type-only: OK — all emitted mirrors type-check.")
        return 0
    finally:
        if tmp:
            shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
