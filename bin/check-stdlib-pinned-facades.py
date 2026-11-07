#!/usr/bin/env python3
r"""L-PLANE ORACLE: a `pycsl_lib` function whose body is a CONSTANT and whose contract PINS
that constant.

WHY THIS EXISTS (gen #30), and why it is a SECOND gate rather than part of the first.
`bin/check-stdlib-contract-fidelity.py` measures a stub's contract against the real stdlib
function by CALLING it — so it carries a safety deny-list, and `os` is on it (a generated
argument to `os.chflags` is not a test). That leaves the sharpest facade set in the layer
entirely outside its reach, so this gate covers it STATICALLY: no execution, pure AST.

THE SHAPE. A function whose body is a single `return <literal>` **and** whose `#@ ensures
\result == <the same literal>` pins it. That is a verified function which computes nothing
and claims exactly the nothing it computes. It is SOUND today — the contract is true of the
body, and nothing substitutes these contracts for the real module (no name map takes `os`
to `pycsl_lib/os`) — and it is precisely the set that turns FALSE on the day something
does: **a proof that `islink(p) == 0` is a proof that nothing is ever a symlink.**

Compare the blunter census it replaces: 124 of 870 `pycsl_lib` functions (14.3%) have a
single-constant body, and most are honest empty-defaults. Twelve of them also PIN the
constant, and those twelve are the actionable set.

THE RATCHET is that set, baselined by name. A NEW one fails. Removing one — by giving the
function a real body, or by weakening its contract to something true of the module it
cites — is the way down, and the gate says so when a baselined entry disappears.

THE POPULATION GUARD (the #44 rule): REFUSES with rc=2 if the walk finds fewer than
MIN_FUNCTIONS functions at all, so "no facades" can never mean "I parsed nothing".

Usage:  bin/check-stdlib-pinned-facades.py [--verbose]
"""
import argparse
import ast
import warnings
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIB = os.path.join(ROOT, "src", "pycsl_lib")
MIN_FUNCTIONS = 700   # 870 at the first measurement

# (module, function) -> why it is here and what removing it would take
BASELINE = {
    ("os", "getcwd"): "returns 0 for the current directory.",
    ("os", "get_exec_path"): "returns 0 for the exec path.",
    ("os", "chflags"): "returns 0 unconditionally — no flags are ever set.",
    ("os", "confstr"): "returns 0 for every configuration string.",
    ("os", "copy_file_range"): "returns 0 bytes copied, always.",
    ("os", "getxattr"): "returns 0 for every extended attribute.",
    ("os", "listxattr"): "returns 0 for every listing.",
    ("os", "_kill"): "returns 0 — the signal is never delivered.",
    ("os", "islink"): "returns 0 — NOTHING IS EVER A SYMLINK. The sharpest of the set: a "
                      "caller proving `islink(p) == 0` has proved a fact about the real "
                      "filesystem that this body cannot support.",
    ("os", "is_junction"): "returns 0 — nothing is ever a junction.",
    ("stat", "filemode"): "returns the constant \"----------\" for every mode; "
                          "`stat.filemode(2)` is '?-------w-'. Relabelled in gen #30 with "
                          "the faithful fix PRICED (ten independent bit tests over a "
                          "string model with no per-character theory).",
    ("sysmod", "get_float_info_max_10_exp"):
        "returns 308 — and this one is FAITHFUL: `sys.float_info.max_10_exp` IS 308, "
        "checked against CPython. It is in the baseline because the SHAPE is the same and "
        "the gate keys on shape, not on truth; a reader should not have to re-derive that "
        "this particular constant is the right one.",
}


def facades():
    # A stub source may carry an odd escape in a docstring; parsing it is not our
    # business to warn about and the noise would drown the verdict.
    warnings.filterwarnings("ignore", category=SyntaxWarning)
    out, total = [], 0
    for f in sorted(glob.glob(os.path.join(LIB, "**", "*.py"), recursive=True)):
        src = open(f, errors="replace").read()
        lines = src.split("\n")
        try:
            tree = ast.parse(src)
        except SyntaxError:
            continue
        mod = os.path.relpath(f, LIB).replace(os.sep + "__init__.py", "")
        mod = mod.replace(".py", "")
        for n in ast.walk(tree):
            if not isinstance(n, ast.FunctionDef):
                continue
            total += 1
            body = [s for s in n.body
                    if not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant)
                            and isinstance(s.value.value, str))]
            if not (len(body) == 1 and isinstance(body[0], ast.Return)
                    and isinstance(body[0].value, ast.Constant)):
                continue
            val = body[0].value.value
            for i in range(max(0, n.lineno - 12), n.lineno):
                m = re.match(r"\s*#@\s*ensures\s+\\result\s*==\s*(.+?)\s*$", lines[i])
                if m and m.group(1).strip().strip('"') == str(val).strip('"'):
                    out.append((mod, n.name, val))
                    break
    return out, total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    found, total = facades()
    if total < MIN_FUNCTIONS:
        print("[!] stdlib-pinned-facades: REFUSING — the walk saw only %d function(s), "
              "expected at least %d. The glob or the parse is broken; this is not a pass."
              % (total, MIN_FUNCTIONS), file=sys.stderr)
        return 2

    keys = {(m, n) for m, n, _v in found}
    new = sorted(k for k in keys if k not in BASELINE)
    gone = sorted(k for k in BASELINE if k not in keys)

    if args.verbose:
        for m, n, v in sorted(found):
            print("    %s %s.%s -> %r"
                  % ("ok " if (m, n) in BASELINE else "NEW", m, n, v))

    print("[*] stdlib-pinned-facades: %d function(s) scanned; %d body-is-a-constant AND "
          "contract-pins-it." % (total, len(keys)))

    rc = 0
    for k in gone:
        print("[+]   baselined facade %s.%s IS GONE — give it a real body or a weaker "
              "contract, then remove its baseline entry." % k)
    for k in new:
        print("[!]   NEW PINNED FACADE %s.%s — a verified function that computes nothing "
              "and claims exactly that. Sound while nothing substitutes this layer for the "
              "real module; false the moment something does." % k, file=sys.stderr)
        rc = 1
    if rc:
        print("[!] stdlib-pinned-facades: NOT OK — the facade set grew.", file=sys.stderr)
    else:
        print("[+] stdlib-pinned-facades: OK — %d known facade(s), none new."
              % len(BASELINE))
    return rc


if __name__ == "__main__":
    sys.exit(main())
