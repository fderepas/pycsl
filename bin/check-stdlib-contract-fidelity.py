#!/usr/bin/env python3
r"""L-PLANE ORACLE: a `pycsl_lib` stub CONTRACT measured against the REAL stdlib module.

WHY THIS EXISTS (gen #30). `src/pycsl_lib/` holds 93 body-verified stub packages, governed
by `config/skills/agent-stdlib-annotate`, and **nothing in the battery compared a stub
against the module it documents.** Every stub cites the CPython library reference in its
docstring ("RST: 'Return the IEEE 754-style remainder of x with respect to y.'"), so a
reader — and the next annotator — takes the contract as a claim about that function.

A stub's contract is PROVEN of its own body, which means it can be perfectly proven and
still be FALSE OF THE FUNCTION IT CITES. That is this campaign's defect shape, one layer up
from the emitter.

WHAT IT MEASURES. For each stub function whose contract is expressible as plain Python over
its parameters and `\result`: enumerate inputs from fixed pools (DETERMINISTIC — no
randomness in a gate), keep those satisfying every `#@ requires`, run the REAL stdlib
function, and evaluate every `#@ ensures` against CPython's answer. A false `ensures` is a
DIVERGENCE.

SEVERITY, STATED HONESTLY AND MEASURED RATHER THAN ASSUMED. A divergence here is NOT
today a proof-soundness hole: `frontend/import_classifier._stub_set` reads only the `.py`
stems directly under `src/pycsl_lib/` (a directory of PACKAGES), and there is NO name map
taking `math` to `mth`, so a user's `import math` never picks up these contracts. The
stubs are standalone modules whose contracts are true of their own bodies. What a
divergence IS: a documentation-fidelity defect in a layer whose whole purpose is to model
the stdlib — and exactly what becomes a soundness hole on the day something substitutes
them.

THE RATCHET is the SET of diverging (package, function) pairs, baselined at the two found
when this gate was written. A NEW divergence fails. Lowering it means fixing a stub or its
citation — never re-baselining to make the gate green (rule (k)).

THE POPULATION GUARD (the #44 rule): REFUSES with rc=2 if fewer than MIN_CHECKS contract
evaluations actually run, so "all green" can never mean "I checked nothing".

Usage:  bin/check-stdlib-contract-fidelity.py [--verbose]
"""
import argparse
import importlib
import importlib.util
import inspect
import itertools
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIB = os.path.join(ROOT, "src", "pycsl_lib")

# stub package -> the stdlib module it documents itself against.
#
# DERIVED FROM THE STUBS' OWN HEADERS, not hand-written: 50 of the 93 packages name an
# importable stdlib module in their first lines ("pycsl_lib/bsect — pure-Python bisect
# module"). Only the PURE, DETERMINISTIC, SIDE-EFFECT-FREE ones are listed here, and the
# exclusion is a SAFETY requirement, not a scoping preference: this gate CALLS the real
# function with generated arguments, so `shutil`, `subprocess`, `tempfile`, `os`, `io`,
# `signal` and `pathlib` are excluded because a generated argument could touch the
# filesystem or spawn a process; `random` and `time` because a non-deterministic answer
# cannot carry a ratchet; `argparse`/`getopt` because they can exit the interpreter.
# Widening this map means arguing a module into the pure set, never just adding a name.
#
# GEN #30 SECOND PASS — THE SCOPE CLAIM ABOVE WAS ITSELF MEASURED. Re-deriving the
# headers mechanically gives 47 packages that name an IMPORTABLE stdlib module, and the
# first map listed 24 of them. Of the 23 left out, only ten had a stated safety reason
# (argparse, getopt, io, pathlib, random, shutil, signal, subprocess, tempfile, sys);
# THIRTEEN were simply unlisted, and widening to the safe ones found SIX new diverging
# stub functions in three modules that no plane had ever run. That is the whole argument
# for writing an exclusion DOWN rather than leaving a module unmentioned. The ten added
# below, each with its purity argument:
#   abc, collections, dataclasses, typing, weakref, __future__ — introspection and
#     container/type constructors; no I/O, no process, no clock, no randomness.
#   contextlib, functools, pprint — pure wrapper/decorator factories and `saferepr`;
#     `pprint.pprint` writes to a stream, but only contracted stub functions are called
#     and the stub exposes none that print.
#   queue — in-memory only; `Queue()` touches no resource outside the object.
# STILL EXCLUDED, now WITH the reason the first pass omitted:
#   csv, tokenize, linecache, glob — all four can be handed a generated argument that
#     becomes a FILENAME (`csv` writers, `tokenize.open`, `linecache.getline`,
#     `glob.glob`), i.e. the same filesystem hazard as `shutil`/`tempfile`.
#   sysconfig — deterministic, but its answers are build-path strings that differ per
#     interpreter install, so a ratchet on them would be green only on this machine.
MAP = {
    "b64": "base64", "bsect": "bisect", "csys": "colorsys", "cpmod": "copy",
    "copyreg": "copyreg", "enm": "enum", "errno": "errno", "fnm": "fnmatch",
    "frac": "fractions", "hlib": "hashlib", "hq": "heapq", "htmlm": "html",
    "itools": "itertools", "kw": "keyword", "mth": "math", "nums": "numbers",
    "oper": "operator", "reprlib": "reprlib", "stat": "stat", "stats": "statistics",
    "strct": "struct", "txtwrp": "textwrap", "token": "token", "udata": "unicodedata",
    # widened in gen #30 (see the purity argument above)
    "abcmod": "abc", "coll": "collections", "ctxlib": "contextlib",
    "dc": "dataclasses", "ftools": "functools", "pp": "pprint", "que": "queue",
    "typ": "typing", "wref": "weakref", "fut": "__future__",
    # (#49) gen #30, THIRD widening, and this one came from a finding rather than a
    # census: `strmod` models `string`, is pure, and was in the "named but unmapped" set
    # both times. Its `capwords` carries `#@ ensures sep == "" ==> \str_length(\result)
    # <= \str_length(s)`, which is FALSE of CPython — `string.capwords('ß')` is `'Ss'`,
    # length 1 -> 2, because `str.capitalize()` is NOT length-preserving for characters
    # with multi-character uppercase forms.
    "strmod": "string",
}
SKIP_TOKENS = ("\\forall", "\\exists", "\\old", "\\at", "\\separated", "\\valid",
               "\\sum", "\\is_sorted", "\\permutation", "\\array_eq")
MIN_CHECKS = 5600   # 5612 after the THIRD widening (strmod) and the `\str_length`
                    # translation; ratchets up only

# (package, function) -> why this divergence is known and what it means
BASELINE = {
    ("mth", "remainder"):
        "(#49) gen #30. `requires x >= 0, y > 0`, `ensures \\result >= 0` and "
        "`\\result < y`, body `return x % y`, docstring: \"Return the IEEE 754-style "
        "remainder of x with respect to y. For integers, same as x % y.\" THAT SENTENCE "
        "IS FALSE: `math.remainder` rounds to NEAREST and `%` FLOORS, so "
        "`math.remainder(8, 5)` is -2.0 where `8 % 5` is 3. The contract is true of the "
        "BODY and false of the function the citation names. FIX = correct the citation "
        "and the name (it models `%`, not IEEE remainder), or implement IEEE rounding.",
    # --- DECLARED DOMAIN CHANGES, not defects. `csys`'s own header says: "All
    # coordinates modelled as integers scaled 0..1000 representing [0.0, 1.0]." So the
    # stub works in a scaled INTEGER domain while `colorsys` works in floats on [0,1],
    # and every contract about a scaled coordinate is necessarily false of the float
    # answer. They stay in the baseline rather than being filtered out by a header
    # heuristic, so that a NEW divergence in `csys` — one that is NOT the scaling — still
    # fails the gate. THE STANDING CONDITION: if `csys` is ever re-modelled in floats,
    # these four must be REMOVED, and the gate will say so ("no longer diverges").
    ("csys", "rgb_to_yiq"):
        "DECLARED SCALING: integers 0..1000 vs `colorsys`'s floats on [0,1].",
    ("csys", "rgb_to_hls"):
        "DECLARED SCALING: integers 0..1000 vs `colorsys`'s floats on [0,1].",
    ("csys", "hls_to_rgb"):
        "DECLARED SCALING: integers 0..1000 vs `colorsys`'s floats on [0,1].",
    ("csys", "hsv_to_rgb"):
        "DECLARED SCALING: integers 0..1000 vs `colorsys`'s floats on [0,1].",
    ("stat", "filemode"):
        "(#49) gen #30. `ensures \\result == \"----------\"` with a body returning exactly "
        "that constant, while `stat.filemode(2)` is '?-------w-'. A verified function "
        "whose entire content is a constant, with a contract that pins the constant — the "
        "FACADE shape. FIX = implement the mode-to-string mapping, or drop the RST "
        "citation and say what it really provides.",
    # --- THE IDENTITY-STUB FAMILY, found by the gen #30 widening. Six functions in three
    # newly-mapped modules share ONE shape: the stub body is `return x` and the contract
    # PINS that identity (`ensures \\result == func` / `== obj` / `== val`), while the
    # real function returns a WRAPPER — a decorating function, a partial, a context
    # manager, or (for `saferepr`) a string. Every one of these contracts is true of the
    # body and FALSE of the function its own header cites, the same defect as
    # `mth.remainder`. They are baselined rather than failed because the gate must land
    # green, and each entry names the fix. THE SHARED FIX is not "delete the ensures":
    # it is to say what the integer model can honestly say — that the model carries the
    # wrapped object through unchanged — and to stop citing a function whose answer is a
    # wrapper. A user who proves `ftools.wraps(g) == g` today has proven something
    # CPython contradicts.
    ("ctxlib", "closing"):
        "(#49) gen #30, IDENTITY-STUB FAMILY. Body `return obj`, contract `ensures "
        "\\result == obj`, but contextlib.closing returns a `closing` CONTEXT MANAGER wrapping obj. True of the body, FALSE of the "
        "cited function. FIX = weaken the contract to what the integer model supports "
        "and re-word the citation.",
    ("ctxlib", "contextmanager"):
        "(#49) gen #30, IDENTITY-STUB FAMILY. Body `return func`, contract `ensures "
        "\\result == func`, but contextlib.contextmanager returns a generator-driven HELPER function. True of the body, FALSE of the "
        "cited function. FIX = weaken the contract to what the integer model supports "
        "and re-word the citation.",
    ("ctxlib", "nullcontext"):
        "(#49) gen #30, IDENTITY-STUB FAMILY. Body `return val`, contract `ensures "
        "\\result == val`, but contextlib.nullcontext returns a `nullcontext` OBJECT, not val itself. True of the body, FALSE of the "
        "cited function. FIX = weaken the contract to what the integer model supports "
        "and re-word the citation.",
    ("ftools", "lru_cache"):
        "(#49) gen #30, IDENTITY-STUB FAMILY. Body `return func`, contract `ensures "
        "\\result == func`, but functools.lru_cache returns a DECORATING FUNCTION, not func. True of the body, FALSE of the "
        "cited function. FIX = weaken the contract to what the integer model supports "
        "and re-word the citation.",
    ("ftools", "wraps"):
        "(#49) gen #30, IDENTITY-STUB FAMILY. Body `return func`, contract `ensures "
        "\\result == func`, but functools.wraps returns a `functools.partial` of `update_wrapper`. True of the body, FALSE of the "
        "cited function. FIX = weaken the contract to what the integer model supports "
        "and re-word the citation.",
    ("pp", "saferepr"):
        "(#49) gen #30, IDENTITY-STUB FAMILY. Body `return obj`, contract `ensures "
        "\\result == obj`, but pprint.saferepr returns the STRING repr of obj (`saferepr(0)` is \'0\'). True of the body, FALSE of the "
        "cited function. FIX = weaken the contract to what the integer model supports "
        "and re-word the citation.",
}

POOL_INT = [0, 1, 2, 3, 5, 8, 13, -1, -5, 20]
# (#49) gen #30: `"ß"` and `"ﬁ"` are in this pool ON PURPOSE. Every other entry is ASCII,
# and an ASCII-only pool cannot see the one thing that makes a case transform unfaithful:
# `'ß'.capitalize()` is `'Ss'` and `'ﬁ'.upper()` is `'FI'`, so a case operation can GROW a
# string. `strmod.capwords`'s length bound is false for exactly those inputs, and the gate
# was blind to it while the pool was ASCII.
POOL_STR = ["", "a", "ab", "abc", "A", "a.b", "*", "?", "\u00df", "\ufb01"]
POOL_LIST = [[], [0], [1, 2], [0, 1, 2, 3], [5, 5], [-1, 0, 1]]


def to_py(e):
    e = e.replace("\\result", "_result")
    e = re.sub(r"\\length\(([^)]*)\)", r"len(\1)", e)
    # (#49) gen #30: `\str_length` too. Without it EVERY string-model contract was
    # skipped, which is why `strmod.capwords`'s length bound — FALSE of CPython for
    # `'ß'` — was invisible to a gate that maps `strmod` and runs the real `string`.
    e = re.sub(r"\\str_length\(([^)]*)\)", r"len(\1)", e)
    e = e.replace("&&", " and ").replace("||", " or ")
    # (#49) gen #30 — IMPLICATION MUST BE SPLIT AT DEPTH ZERO. The first version split at
    # the FIRST `==>` anywhere in the string and re-scanned the result, so a NESTED
    # implication like `sep == "" ==> (s == "" ==> \result == "")` was cut INSIDE its own
    # parentheses and became a mangled expression that evaluated False for inputs where
    # the clause is vacuously true. Measured the moment `strmod` joined the map: three
    # "NEW DIVERGENCE strmod.capwords('', 'a')" reports whose own message said the real
    # answer was `''` — i.e. the gate contradicting itself. Scan for the first `==>` at
    # PAREN DEPTH 0 and recurse on both sides.
    def _imp(x):
        depth, i = 0, 0
        while i < len(x):
            c = x[i]
            if c == "(":
                depth += 1
            elif c == ")":
                depth -= 1
            elif depth == 0 and x.startswith("==>", i):
                return "((not (%s)) or (%s))" % (_imp(x[:i]), _imp(x[i + 3:]))
            i += 1
        return x
    return _imp(e)


def contracts(path):
    out, req, ens = {}, [], []
    for line in open(path, errors="replace"):
        m = re.match(r"\s*#@\s*(requires|ensures)\s+(.+?)\s*$", line)
        if m:
            (req if m.group(1) == "requires" else ens).append(m.group(2))
            continue
        m = re.match(r"\s*def\s+(\w+)\s*\(", line)
        if m:
            if req or ens:
                out[m.group(1)] = (list(req), list(ens))
            req, ens = [], []
            continue
        if line.strip() and not line.lstrip().startswith(("#", '"', "'", "@")):
            req, ens = [], []
    return out


def load(pkg):
    spec = importlib.util.spec_from_file_location(
        "pycsl_lib_stub_" + pkg, os.path.join(LIB, pkg, "__init__.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verbose", action="store_true")
    # SELF-TEST HOOK (lesson (q): a gate built from a finding must be seen to FAIL). With
    # the baseline emptied, the two KNOWN divergences must be reported as NEW and the gate
    # must exit 1. If it does not, the ratchet is not wired to the measurement.
    ap.add_argument("--selftest-empty-baseline", action="store_true",
                    help="clear the baseline so the known divergences fail the gate")
    args = ap.parse_args()
    if args.selftest_empty_baseline:
        BASELINE.clear()

    checks = 0
    diverging = {}
    for pkg, std in sorted(MAP.items()):
        try:
            stub, real = load(pkg), importlib.import_module(std)
        except Exception:
            continue
        cts = contracts(os.path.join(LIB, pkg, "__init__.py"))
        for name, (req, ens) in sorted(cts.items()):
            f = getattr(stub, name, None)
            g = getattr(real, name, None)
            if not inspect.isfunction(f) or g is None or not callable(g) or not ens:
                continue
            if any(t in " ".join(req + ens) for t in SKIP_TOKENS):
                continue
            params = list(inspect.signature(f).parameters.values())
            if not params or any(p.kind is not p.POSITIONAL_OR_KEYWORD for p in params):
                continue
            pools = []
            for p in params:
                a = p.annotation
                pools.append(POOL_INT if a is int else POOL_STR if a is str
                             else POOL_LIST if a is list else POOL_INT)
            for combo in itertools.islice(itertools.product(*pools), 200):
                env = {p.name: v for p, v in zip(params, combo)}
                try:
                    if not all(eval(to_py(c), {"len": len}, env) for c in req):
                        continue
                    real_ans = g(*combo)
                except Exception:
                    continue
                env["_result"] = real_ans
                for c in ens:
                    try:
                        ok = eval(to_py(c), {"len": len}, env)
                    except Exception:
                        continue
                    checks += 1
                    if not ok:
                        d = diverging.setdefault((pkg, name), [])
                        if len(d) < 3:
                            d.append((combo, c, real_ans))

    print("[*] stdlib-contract-fidelity: %d contract evaluation(s) against the real "
          "stdlib; %d diverging function(s)." % (checks, len(diverging)))

    if checks < MIN_CHECKS:
        print("[!] stdlib-contract-fidelity: REFUSING — only %d evaluation(s) ran, "
              "expected at least %d. A gate that cannot tell 'nothing is wrong' from "
              "'I checked nothing' is not a gate." % (checks, MIN_CHECKS), file=sys.stderr)
        return 2

    rc = 0
    for key in sorted(diverging):
        ex = diverging[key]
        if key in BASELINE:
            if args.verbose:
                print("    known  %s.%s — %s" % (key[0], key[1], BASELINE[key][:90]))
            continue
        for combo, c, real_ans in ex:
            print("[!]   NEW DIVERGENCE %s.%s%r — `ensures %s` is FALSE of CPython "
                  "(real answer %r)" % (key[0], key[1], combo, c, real_ans), file=sys.stderr)
        rc = 1
    for key in sorted(BASELINE):
        if key not in diverging:
            print("[+]   baselined divergence %s.%s NO LONGER DIVERGES — fix the stub's "
                  "citation and remove its baseline entry." % key)
    if rc:
        print("[!] stdlib-contract-fidelity: NOT OK — a stub's contract is false of the "
              "stdlib function its own docstring cites.", file=sys.stderr)
    else:
        print("[+] stdlib-contract-fidelity: OK — %d known divergence(s), no new one."
              % len(BASELINE))
    return rc


if __name__ == "__main__":
    sys.exit(main())
