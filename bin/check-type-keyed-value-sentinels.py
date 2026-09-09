#!/usr/bin/env python3
"""check-type-keyed-value-sentinels — the 30th plane.

WHY IT EXISTS. The 27th plane (`check-type-keyed-constant-answers.py`) polices Module-6
arms that are KEYED ON A TYPE and answer a Why3 **bool** constant. Nothing policed arms
keyed on a type that answer a **value** constant — a sentinel, a zero, a filled-in
default. ROUTE #56 LIVED EXACTLY IN THAT GAP: `_union_read_projection` answered a `None`
Optional-union local with the carrier's zero, so `| _ -> 0` made a `None` local and a
genuine `0` the same Why3 term and `x == 0` proved true where Python answers False.

THE SHAPE THIS FINDS is a dict literal whose keys are all TYPE NAMES, consumed by a
`.get(<key>, <literal default>)` — i.e. "look the type up; if you do not recognize it,
answer this constant". Every such site is a place where the emitter answers a question it
may not be entitled to answer, and the DEFAULT arm is where the answer is least justified,
because it fires for the types nobody thought about.

EACH SITE MUST BE CLASSIFIED in BASELINE below with a verdict:
  SAFE-TYPED   the default is ill-typed against every comparand that could reach it, so
               the site fails closed on a Why3 type error rather than deciding. NOTE this
               is an ACCIDENT, not a guard: route #56 was invisible for exactly this
               reason at the `str` carrier while being live at `int`. A SAFE-TYPED verdict
               must name the carrier it was measured at.
  OPAQUE       the default routes through an opaque (route #44's `pycsl_none`, route #50's
               `pycsl_none_str`, ...), so the arm answers "unknown" rather than a value.
  WITNESSED    the site is exercised by a corpus witness that pins its behaviour.
  OPEN         a live or unargued site. A single OPEN entry is not a failure here (the
               27th plane carries OPEN entries too), but it MUST be named.

EXIT CODES
  0  every site found is classified, and every classified site was found
  1  an UNCLASSIFIED site (a new one) or a STALE entry (a baseline entry matching no site)
  2  refusal: fewer than MIN_SITES sites scanned, so the module paths are broken and the
     result means nothing (the #44 rule: a gate that cannot tell "nothing is wrong" from
     "I looked at nothing" is not a gate)
"""
from __future__ import annotations

import argparse
import ast
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
M6 = os.path.join(ROOT, "src", "pycsl", "module6_whyml")

# A dict literal counts as TYPE-KEYED when every key is one of these.
TYPE_NAMES = {"int", "bool", "str", "string", "float", "real", "bytes",
              "list", "dict", "set", "tuple", "emit_ir", "none", "None"}

MIN_SITES = 3

# (file, enclosing function, sorted keys, default literal) -> verdict + why
BASELINE = {
    ("expressions.py", "_handle_dotted_call", "real|string", "'0'"):
        "SAFE-TYPED at str + OPAQUE at int. This fills an OMITTED ARGUMENT whose parameter "
        "default is `None`. Measured at str (relaunch #51): `def g(s: str = None) -> int` "
        "called as `g()` leaves BOTH goals Unknown, including the TRUE one, so the fill "
        "path does not decide. At int the guard is `pwt != \"int\"`, so an int param's "
        "`None` default falls through to the ordinary `None` lowering and therefore to "
        "route #44's opaque.",
    ("expressions.py", "_handle_call_expr", "real|string", "'0'"):
        "SAFE-TYPED at str + OPAQUE at int — the sibling fill site, same argument and same "
        "measurement as `_handle_dotted_call` above. Relaunch #51.",
    ("expressions.py", "_union_local_field_projection", "float|real|str|string", "'0'"):
        "SAFE-TYPED (measured, relaunch #51): a FIELD read through a `None` union local, "
        "`x: Optional[R] = None` then `x.n == 0`, dies with a Why3 usage error where "
        "Python raises AttributeError. NOTE the verdict is a TYPE ACCIDENT, not a guard — "
        "the same accident hid route #56 at the `str` carrier while it was live at `int`. "
        "If a `int`-carrier field read ever reaches this arm, re-measure it.",
    ("expressions.py", "_union_read_projection", "emit_ir|float|real|str|string", None):
        "ROUTE #56 — the `int` carrier DECIDED here. `| _ -> 0` made a `None` Optional-union "
        "local and a genuine `0` the same Why3 term, so `x == 0` proved true where Python "
        "answers False. The fall-through now answers route #44's EXISTING `pycsl_none` "
        "opaque: same type, no new model, undecided instead of wrong. Relaunch #51.",
}


def enclosing_func(tree, lineno):
    best = None
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.lineno <= lineno <= (node.end_lineno or node.lineno):
                if best is None or node.lineno > best.lineno:
                    best = node
    return best.name if best else "<module>"


def literal(node):
    """Render a literal-ish AST node, or None if it is not a literal."""
    if isinstance(node, ast.Constant):
        return repr(node.value)
    return None


def scan_file(path):
    src = open(path, encoding="utf-8").read()
    tree = ast.parse(src)
    out = []
    for node in ast.walk(tree):
        # <dict literal>.get(x, <default>)
        if not (isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "get"
                and isinstance(node.func.value, ast.Dict)):
            continue
        d = node.func.value
        keys = []
        ok = True
        for k in d.keys:
            if isinstance(k, ast.Constant) and isinstance(k.value, str):
                keys.append(k.value)
            else:
                ok = False
        if not ok or not keys:
            continue
        if not set(keys).issubset(TYPE_NAMES):
            continue
        dflt = literal(node.args[1]) if len(node.args) > 1 else None
        out.append((os.path.basename(path), enclosing_func(tree, node.lineno),
                    "|".join(sorted(keys)), dflt, node.lineno))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    if not os.path.isdir(M6):
        print(f"[!] type-keyed-value-sentinels: {M6} is not a directory. NOT A PASS.")
        return 2

    sites = []
    for fn in sorted(os.listdir(M6)):
        if fn.endswith(".py"):
            sites.extend(scan_file(os.path.join(M6, fn)))

    if len(sites) < MIN_SITES:
        print(f"[!] type-keyed-value-sentinels: only {len(sites)} site(s) scanned, "
              f"expected at least {MIN_SITES}. The module path or the recognizer is "
              f"broken. THIS IS A REFUSAL, NOT A PASS.")
        return 2

    seen = set()
    unclassified = []
    for (f, fun, keys, dflt, line) in sites:
        key = (f, fun, keys, dflt)
        seen.add(key)
        if key not in BASELINE:
            unclassified.append((f, fun, keys, dflt, line))
        elif args.verbose:
            print(f"    ok   {f}:{line} {fun} keys={keys} default={dflt}")
            print(f"         {BASELINE[key]}")

    stale = [k for k in BASELINE if k not in seen]

    if unclassified or stale:
        for (f, fun, keys, dflt, line) in unclassified:
            print(f"[-] UNCLASSIFIED type-keyed VALUE sentinel: {f}:{line} in {fun}")
            print(f"      keys={keys}  default={dflt}")
            print( "      Classify it in BASELINE. A default arm answers for the types")
            print( "      nobody thought about — measure it at the `int` carrier before")
            print( "      calling it safe (that is the carrier route #56 decided at).")
        for k in stale:
            print(f"[-] STALE baseline entry (matches no site): {k}")
        print(f"[!] type-keyed-value-sentinels: {len(unclassified)} unclassified, "
              f"{len(stale)} stale, over {len(sites)} site(s).")
        return 1

    print(f"[+] type-keyed-value-sentinels: OK — {len(sites)} site(s), every one "
          f"classified.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
