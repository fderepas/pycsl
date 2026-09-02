#!/usr/bin/env python3
r"""L-PLANE ORACLE: a `\trusted` mirror stub whose PARAMETER LIST is not the live one's.

`bin/check-self-annotate-sync.sh` and `bin/check-self-annotate-mirror-sync.py` compare the
BODY of every UN-TRUSTED mirror method against the live emitter's, which is what keeps a
converted proof about the real code. A `\trusted` stub has no body to compare, so nothing
checked its INTERFACE — and the interface is the entire content of a trusted stub. It is
the thing every mirror caller is typed against and the thing the `#@ requires`/`#@ ensures`
/`#@ assigns` clauses are asserted OF.

MEASURED when this check was written (relaunch #31): **16 `\trusted` stubs disagree with
their live counterpart's parameter list, and 0 converted methods do** — the asymmetry is
exactly the coverage hole:

  * 10 are MISSING a live parameter the stub never grew. `_handle_dotted_call` declares
    `(self, func_name, args)` while the live signature has been `(self, func_name, args,
    arg_irs)` since relaunch #29 added `arg_irs` for the `str_hash_op` coercion; `resolve`
    is missing `import_paths`; `_m5_get_type_name` and `_normalize_union_annotation` are
    missing `dedup`; `_emit_first_assign` is missing `local_refs`. The mirror's trusted
    interface is for a function that no longer exists.
  * 6 are pure RENAMES (`expr` where the live parameter is `node`), which is harmless to
    the model but blocks `bin/probe-conversion-candidates.py`'s signature-preserving port
    (it refuses to splice a live body into a header whose binders have other names), so
    those six stubs cannot be MEASURED at all until the names agree.

RATCHET, only lower it. A drift may be repaired in either direction — grow the stub to the
live signature, or rename the binder — but every repair changes the emitted `val` and so
costs a whole-file re-proof of that mirror.

Usage:  bin/check-mirror-signature-drift.py [--max N] [--verbose]
"""
import argparse
import ast
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIRROR = os.path.join(ROOT, "src", "self-annotate", "src")
LIVE = os.path.join(ROOT, "src", "pycsl")

BASELINE = 16          # 6 renames + 10 missing-parameter stubs, all `\trusted`.
                       # A RATCHET — only lower it.


def _params(fn):
    a = fn.args
    return ([x.arg for x in a.posonlyargs] + [x.arg for x in a.args]
            + ([a.vararg.arg] if a.vararg else [])
            + [x.arg for x in a.kwonlyargs]
            + ([a.kwarg.arg] if a.kwarg else []))


def _is_trusted(lines, fn) -> bool:
    i = min([d.lineno for d in fn.decorator_list] + [fn.lineno]) - 2
    while i >= 0:
        st = lines[i].strip()
        if not (st.startswith("#") or st.startswith("@") or st == ""):
            return False
        if st.startswith("#@") and "\\trusted" in st:
            return True
        i -= 1
    return False


def scan():
    """[(rel, qualname, trusted, mirror_params, live_params)]"""
    out = []
    for root, _d, fs in os.walk(MIRROR):
        for f in sorted(fs):
            if not f.endswith(".py"):
                continue
            p = os.path.join(root, f)
            rel = os.path.relpath(p, MIRROR)
            lp = os.path.join(LIVE, rel)
            if not os.path.exists(lp):
                continue
            src = open(p).read()
            lines = src.split("\n")
            try:
                mt = ast.parse(src)
                lt = ast.parse(open(lp).read())
            except SyntaxError:
                continue
            lmap = {}

            def build(scope, cls):
                for n in scope:
                    if isinstance(n, ast.ClassDef):
                        build(n.body, n.name)
                    elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        lmap[(cls, n.name)] = n

            build(lt.body, None)

            def walk(scope, cls):
                for n in scope:
                    if isinstance(n, ast.ClassDef):
                        walk(n.body, n.name)
                    elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        lf = lmap.get((cls, n.name))
                        if lf is None:
                            continue          # mirror-only scaffolding; not this check's job
                        mp, lpp = _params(n), _params(lf)
                        if mp == lpp:
                            continue
                        out.append((rel, (cls + "." if cls else "") + n.name,
                                    _is_trusted(lines, n), mp, lpp))

            walk(mt.body, None)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max", type=int, default=BASELINE)
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    drift = scan()
    renames = [d for d in drift if len(d[3]) == len(d[4])]
    missing = [d for d in drift if len(d[3]) < len(d[4])]
    extra = [d for d in drift if len(d[3]) > len(d[4])]
    conv = [d for d in drift if not d[2]]

    print(f"[*] mirror-signature-drift: {len(drift)} function(s) whose mirror parameter "
          f"list differs from the live one "
          f"({len(renames)} renamed, {len(missing)} missing a live parameter, "
          f"{len(extra)} with a parameter the live function does not have; "
          f"{len(conv)} of them CONVERTED rather than `\\trusted`).")
    for rel, q, tr, mp, lp in drift:
        kind = ("RENAMED" if len(mp) == len(lp)
                else "MISSING" if len(mp) < len(lp) else "EXTRA")
        print(f"    {kind:8s} [{'trusted' if tr else 'CONVERTED'}] {rel}::{q}\n"
              f"             mirror={mp}\n             live  ={lp}")

    rc = 0
    if conv:
        print(f"[!] mirror-signature-drift: {len(conv)} CONVERTED method(s) drift. A "
              f"converted method is proved AS the live function; its signature must be "
              f"the live one. This is a hard failure, not a ratchet.")
        rc = 1
    if len(drift) > args.max:
        print(f"[!] mirror-signature-drift: {len(drift)} > ratchet {args.max}. A "
              f"`\\trusted` stub's INTERFACE is its entire content — every mirror caller "
              f"is typed against it and every `#@` clause is asserted of it. Grow the stub "
              f"to the live signature (or rename the binder) and re-prove that mirror.")
        rc = 1
    if rc == 0:
        print(f"[+] mirror-signature-drift: OK ({len(drift)} / ratchet {args.max}, "
              f"0 converted).")
    return rc


if __name__ == "__main__":
    sys.exit(main())
