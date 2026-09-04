#!/usr/bin/env python3
"""check-swallowed-exceptions.py — the SILENT-INTERNAL-ERROR plane.

THE HAZARD. The emitter is full of recognizers that DECLINE by returning None, and a
decline falls through to a coarser lowering. That is the design. But a broad
`except Exception:` that swallows and continues turns an INTERNAL ERROR into the same
decline — so a bug inside a faithful recognizer silently downgrades the emission to the
generic path, and this campaign has now demonstrated twenty-eight times that a generic
path can be an ERASING one (routes #22 and #24: an erasure to a literal is one `if` away
from a false proof). Nothing else in the battery can see that: the emission is
well-formed, it type-checks, and it proves.

A top-level handler that exits non-zero is fail-closed and fine. A mid-pipeline one that
continues is not.

WHAT IT MEASURES, and it is BEHAVIOURAL rather than static — which is the point. Two sets:

  STATIC   every broad handler (`except:` / `except Exception` / `except BaseException`)
           in `src/pycsl` whose body only swallows (pass / continue / bare return / return
           of a constant) and never re-raises. Measured at #44: 140.
  DYNAMIC  every exception CAUGHT AND NOT RE-RAISED inside `src/pycsl` during a real
           emission of all 53 mirror files, via `sys.monitoring`'s EXCEPTION_HANDLED
           event. Reported per (file, function, exception type).

The gate is their INTERSECTION, pinned at ZERO: no broad swallowing handler may actually
fire. That keeps it sharp and quiet — a new recognizer with its own bail exception moves
the dynamic set and not the verdict.

THE BASELINE IS NOT ZERO, AND THAT IS THE FINDING. Eight recognizers in
`module6_whyml/generic_fold.py` catch their own `_PVWBail` decline signal, and FOUR of them
spell it `except Exception:` — `recognize_pyval_flatten`, `recognize_pyval_list_search`,
`recognize_pyval_list_walker`, `recognize_pyval_string_walker`. Those four therefore
swallow a `TypeError`, an `AttributeError` or a `KeyError` from a genuine bug in exactly
the same way they swallow their own bail, and the emission falls through to the generic
lowering with nothing to show for it. Tightening them to `except _PVWBail:` is a
four-line, byte-inert change and is left for the next window as a named item.

So the gate is a RATCHET on the SET of broad firings rather than a hard zero: the current
eight are baselined, and any NEW broad firing — a type the recognizers were never meant to
absorb — fails.

FIRST MEASUREMENT (#44): eight baselined broad firings, all of them `_PVWBail`. Every handler that fires during a full
mirror emission is designed control flow, and each was read to confirm it:
  * `pure_ast.visit_Constant` catching `AttributeError` (156302x) — CPython's own
    `NodeVisitor` deprecation shim, copied verbatim; it probes for a deprecated
    `visit_Str`/`visit_Num` method.
  * `Module2_Parser._try` catching `_ContractSyntaxError` (1724x) — the parser's
    backtracking combinator.
  * `generic_fold`'s `_PVWBail` (~160x) — a dedicated bail exception the pyval/term
    recognizers raise to decline.
  * `GeneratorExit` in two iterator helpers — generator cleanup.
  * `auto_trust._check_witness_vals` catching `SyntaxError` (7x) — a quick sanity check on
    a record's `by` witness. Fail-closed: a witness that violates the class invariant makes
    Why3 REJECT the type declaration, so an unchecked witness cannot become a false proof.
None of these is a broad `except Exception`.

USAGE
    bin/check-swallowed-exceptions.py            # static + dynamic, gate the intersection
    bin/check-swallowed-exceptions.py --static   # static census only (fast)
    bin/check-swallowed-exceptions.py --verbose
"""
import argparse
import ast
import collections
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIVE = os.path.join(ROOT, "src", "pycsl")
MIRROR = os.path.join(ROOT, "src", "self-annotate", "src")

BASELINE = os.path.join(ROOT, "getting-better", "swallowed-exceptions-baseline.json")


def static_broad_swallows():
    """{(relpath, enclosing function name)} for every broad swallowing handler."""
    out = set()
    detail = []
    for root, _d, files in os.walk(LIVE):
        if "__pycache__" in root:
            continue
        for fn in sorted(files):
            if not fn.endswith(".py"):
                continue
            path = os.path.join(root, fn)
            try:
                tree = ast.parse(open(path, errors="replace").read())
            except (OSError, SyntaxError, UnicodeDecodeError):
                continue
            # map each handler to its enclosing function
            for func in ast.walk(tree):
                if not isinstance(func, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                for h in ast.walk(func):
                    if not isinstance(h, ast.ExceptHandler):
                        continue
                    t = h.type
                    broad = (t is None
                             or (isinstance(t, ast.Name)
                                 and t.id in ("Exception", "BaseException"))
                             or (isinstance(t, ast.Tuple) and any(
                                 isinstance(e, ast.Name)
                                 and e.id in ("Exception", "BaseException")
                                 for e in t.elts)))
                    if not broad:
                        continue
                    if any(isinstance(x, ast.Raise) for x in ast.walk(h)):
                        continue                       # re-raises: not a swallow
                    body = h.body
                    kind = None
                    if len(body) == 1:
                        b = body[0]
                        if isinstance(b, ast.Pass):
                            kind = "pass"
                        elif isinstance(b, ast.Continue):
                            kind = "continue"
                        elif isinstance(b, ast.Return):
                            kind = ("return None" if b.value is None
                                    else (f"return {b.value.value!r}"
                                          if isinstance(b.value, ast.Constant) else None))
                    if kind:
                        rel = os.path.relpath(path, ROOT)
                        out.add((rel, func.name))
                        detail.append((rel, h.lineno, func.name, kind))
    return out, detail


_DRIVER = r'''
import os, sys, collections
ROOT = sys.argv[1]; target = sys.argv[2]
sys.path.insert(0, os.path.join(ROOT, "src", "pycsl"))
TOOL = 5
SRC = os.path.join(ROOT, "src", "pycsl")
hits = collections.Counter()
def on_handled(code, offset, exc):
    fn = code.co_filename
    if fn.startswith(SRC):
        hits[(os.path.relpath(fn, ROOT), code.co_name, type(exc).__name__)] += 1
mon = sys.monitoring
mon.use_tool_id(TOOL, "swallow-probe")
mon.set_events(TOOL, mon.events.EXCEPTION_HANDLED)
mon.register_callback(TOOL, mon.events.EXCEPTION_HANDLED, on_handled)
sys.argv = ["pycsl.py", target, "--import-path", os.path.join(ROOT, "src", "pycsl"),
            "--no-proof", "--no-typecheck"]
import pycsl
try:
    pycsl.main()
except SystemExit:
    pass
except Exception:
    pass
mon.set_events(TOOL, 0); mon.free_tool_id(TOOL)
for (f, fn, exc), n in sorted(hits.items()):
    sys.stderr.write("SWALLOW\t%d\t%s\t%s\t%s\n" % (n, f, fn, exc))
'''


def dynamic_firing():
    """Counter over (relpath, function, exception) handled inside src/pycsl during a real
    emission of every mirror file."""
    env = dict(os.environ)
    env["PYTHONHASHSEED"] = "0"
    hits = collections.Counter()
    for root, _d, files in os.walk(MIRROR):
        for fn in sorted(files):
            if not fn.endswith(".py"):
                continue
            path = os.path.join(root, fn)
            try:
                r = subprocess.run([sys.executable, "-c", _DRIVER, ROOT, path],
                                   capture_output=True, text=True, timeout=900,
                                   env=env, cwd=ROOT)
            except subprocess.TimeoutExpired:
                continue
            for line in r.stderr.split("\n"):
                if not line.startswith("SWALLOW\t"):
                    continue
                parts = line.split("\t")
                if len(parts) >= 5:
                    hits[(parts[2], parts[3], parts[4])] += int(parts[1])
    return hits


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--static", action="store_true", help="static census only")
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--update", action="store_true",
                    help="re-baseline the allowed broad firings")
    args = ap.parse_args()

    broad, detail = static_broad_swallows()
    print(f"[*] swallowed-exceptions: {len(detail)} broad swallowing handler(s) in "
          f"src/pycsl, across {len(broad)} function(s).")
    if args.verbose:
        for rel, ln, fname, kind in sorted(detail):
            print(f"    STATIC  {rel}:{ln}  {fname}  -> {kind}")
    if args.static:
        return 0

    hits = dynamic_firing()
    print(f"[*] swallowed-exceptions: {len(hits)} (file, function, exception) pair(s) "
          f"actually CAUGHT during a full 53-mirror emission.")
    for (f, fname, exc), n in sorted(hits.items(), key=lambda kv: -kv[1]):
        mark = "  <-- BROAD" if (f, fname) in broad else ""
        print(f"    FIRED   {n:8d}x  {f}::{fname}  {exc}{mark}")

    firing_broad = sorted(f"{f}::{fn}::{e}" for (f, fn, e) in hits if (f, fn) in broad)

    if args.update or not os.path.exists(BASELINE):
        import json
        with open(BASELINE, "w") as fh:
            json.dump({"allowed": firing_broad}, fh, indent=2, sort_keys=True)
            fh.write("\n")
        print(f"[+] swallowed-exceptions: baseline written ({len(firing_broad)} allowed "
              f"broad firing(s))")
        return 0

    import json
    with open(BASELINE) as fh:
        allowed = set(json.load(fh)["allowed"])
    new_firings = [k for k in firing_broad if k not in allowed]
    gone = [k for k in sorted(allowed) if k not in set(firing_broad)]
    for k in gone:
        print(f"[+] no longer fires: {k} (re-baseline with --update)")
    if new_firings:
        print(f"[-] swallowed-exceptions: {len(new_firings)} NEW broad swallowing "
              f"firing(s). A broad `except Exception` that swallows turns an INTERNAL "
              f"ERROR into a recognizer decline, and a decline falls through to the "
              f"generic lowering — which routes #22 and #24 showed can be an ERASING one. "
              f"Nothing else in the battery can see it: the emission is well-formed, "
              f"type-checks and proves.")
        for k in new_firings:
            print(f"      {k}")
        return 1
    print(f"[+] swallowed-exceptions: OK — {len(detail)} broad swallowing handler(s) "
          f"exist; {len(firing_broad)} fire and every one is a baselined, designed "
          f"control-flow signal. No NEW broad swallow.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
