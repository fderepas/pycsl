#!/usr/bin/env python3
"""L-PLANE ORACLE: a CONVERTED method whose CALL SITES still go through an abstract val.

`bin/check-untrusted-emitted.py` asks whether an un-trusted (converted) function is
EMITTED AS A DEFINITION rather than re-abstracted to a `val`. That is necessary and not
sufficient. Module 6 lowers `self.<m>(...)` two ways:

  * the CONCRETE sibling application `(<class>__<m> self args)`, which gives the caller the
    callee's real BODY and contract; and
  * a synthesized receiver-less abstract op `val self__<m>_<n> ... : <ret>`, whose result is
    UNCONSTRAINED.

When a method is converted but its call sites take the second route, the `let` is emitted,
it is proved, `check-untrusted-emitted` is green, the mirror byte-diff is 0, fidelity is
unchanged and emitted-vacuity sees nothing — yet no caller can see a single thing the body
computes. `_Parser._if_tail`, `_else_block`, `_import_as_names`, `block` and `statement`
were all in exactly that state when this check was written: `if_stmt`'s `orelse` child was
an ARBITRARY array rather than the parsed one.

That is not UNSOUND (an unconstrained result is an over-approximation, exactly like a
`\trusted` stub), but it is a LOST CONVERSION: the proof was paid for and the faithfulness
gain never reached any caller. This check MEASURES it, so it can only shrink.

Usage:
    bin/check-shadowed-selfcalls.py [--emit-dir DIR] [--max N]

With no `--emit-dir` it emits every mirror under `src/self-annotate/src` itself (requires
`why3` on PATH; see wall-lessons (aa)). `--max N` fails when more than N shadowed methods
are found; the default is the recorded baseline, so the check is a RATCHET.
"""
import argparse
import glob
import os
import re
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIRROR = os.path.join(ROOT, "src", "self-annotate", "src")
BASELINE = 55          # measured 2026-08-28, relaunch #9 — a RATCHET, only lower it

_DEF = re.compile(r'^  (?:let rec|let|with) ([A-Za-z_0-9]+)', re.M)
_VAL = re.compile(r'^  val (self__([A-Za-z_0-9]+)_(\d+)) ', re.M)


def emit_all(out_dir: str) -> None:
    py = os.path.join(ROOT, ".venv", "bin", "python3")
    if not os.path.exists(py):
        py = sys.executable
    env = dict(os.environ, PYTHONHASHSEED="0")
    for src in sorted(glob.glob(os.path.join(MIRROR, "**", "*.py"), recursive=True)):
        mlw = src[:-3] + ".mlw"
        if os.path.exists(mlw):
            os.remove(mlw)
        subprocess.run(
            [py, os.path.join(ROOT, "src", "pycsl", "pycsl.py"), src,
             "--import-path", os.path.join(ROOT, "src", "pycsl"),
             "--no-proof", "--keep-mlw"],
            cwd=ROOT, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if os.path.exists(mlw):
            rel = os.path.relpath(src, MIRROR)[:-3].replace(os.sep, "_")
            os.replace(mlw, os.path.join(out_dir, rel + ".mlw"))


def scan(emit_dir: str):
    """(shadowed, call_sites) — shadowed methods and the call sites that bypass them."""
    shadowed, sites = [], 0
    for f in sorted(glob.glob(os.path.join(emit_dir, "*.mlw"))):
        s = open(f).read()
        defs = set(_DEF.findall(s))
        for full, meth, _ar in _VAL.findall(s):
            hit = [d for d in defs if d.endswith("__" + meth)]
            if not hit:
                continue        # the callee really is a `\trusted` stub — expected
            uses = len(re.findall(r"\b" + re.escape(full) + r"\b", s)) - 1
            if uses <= 0:
                continue        # declared but never applied — no bypass
            concrete = len(re.findall(r"\(" + re.escape(hit[0]) + r" ", s))
            shadowed.append((os.path.basename(f), full, hit[0], uses, concrete))
            sites += uses
    return shadowed, sites


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--emit-dir", help="directory of already-emitted mirror .mlw files")
    ap.add_argument("--max", type=int, default=BASELINE)
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    tmp = None
    emit_dir = args.emit_dir
    if not emit_dir:
        tmp = tempfile.mkdtemp(prefix="shadowed-selfcalls-")
        emit_all(tmp)
        emit_dir = tmp
    if not glob.glob(os.path.join(emit_dir, "*.mlw")):
        print("[!] shadowed-selfcalls: no .mlw files found — nothing measured "
              "(is `why3` on PATH? see wall-lessons (aa))")
        return 1

    shadowed, sites = scan(emit_dir)
    if args.verbose:
        for f, val, definition, uses, concrete in sorted(
                shadowed, key=lambda r: -r[3]):
            print(f"    {uses:3d} bypassing use(s), {concrete} concrete   "
                  f"{f}::{val} shadows `{definition}`")
    print(f"[*] shadowed-selfcalls: {len(shadowed)} CONVERTED method(s) whose call sites "
          f"go through an abstract `val self__<m>_<n>`; {sites} bypassing call site(s).")
    if len(shadowed) > args.max:
        print(f"[!] shadowed-selfcalls: {len(shadowed)} > allowed {args.max} — a "
              f"conversion landed whose body no caller can see.")
        return 1
    print(f"[+] shadowed-selfcalls: OK (ratchet {args.max}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
