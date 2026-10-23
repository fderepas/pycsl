#!/usr/bin/env python3
r"""L-PLANE ORACLE: the reference corpus's OWN PASSING contracts, measured against CPython.

WHY THIS EXISTS. `bin/check-value-differential.py` runs each of its 75 CURATED drivers
under CPython and checks the literal in its `#@ ensures \result == <int>` against the
observed answer — the strongest instrument in the battery, because it curates nothing and
re-measures the ground truth on every run. But its population is 75 files that someone
chose.

The PASS-expected files of `test-suite/corpus/pycsl-reference/` AND
`test-suite/corpus/python-reference/` have never been checked that way, and **378 of them
already contain a ZERO-ARGUMENT function with a LITERAL `#@ ensures \result == N`** — a
claim that is directly runnable, with no new drivers to write. This plane extends the
value-differential's reach from a curated 75 to both corpora, for free.

WHAT A FAILURE HERE MEANS, and it is the sharpest verdict in the battery: a corpus test
that PASSES the prover while its own postcondition is FALSE of the program it is written
about. That is a route witness hiding inside a green test.

FIRST MEASUREMENT (gen #30): 216 runnable contracts, **195 AGREE with CPython, 0
DISAGREE**, 21 not runnable standalone. Putting the corpus directory on `sys.path` then
recovered the multi-file ones. The remainder are programs CPython CANNOT run at all —
they name types that only a `#@ datatype` declaration introduces — so they have no ground
truth to disagree with, which is a category and not a gap. Every unrunnable case is
REPORTED with its exception type, never silently dropped: a plane that cannot tell
"agreed" from "could not run" is not a plane.

THE POPULATION GUARD (the #44 rule). A gate of this shape is trivially satisfiable by
running nothing, so it REFUSES (rc=2) if fewer than MIN_RUNNABLE contracts actually
execute. The corpus only grows, so the floor is set just under the first measurement.

WHAT IT DOES NOT CHECK: contracts with parameters, non-literal right-hand sides,
quantifiers, or `\result` of a non-int/bool return. Those are the value-differential
corpus's job, and writing a driver there is the way to cover one.

Usage:  bin/check-corpus-contract-truth.py [--verbose]
"""
import argparse
import ast
import contextlib
import glob
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORPORA = [os.path.join(ROOT, "test-suite", "corpus", "pycsl-reference"),
           os.path.join(ROOT, "test-suite", "corpus", "python-reference")]
# (#49) gen #31 — NO NORMAL EXIT, and for a ZERO-ARGUMENT function there is no
# input-dependence to argue about: if it raises, it raises always, so every entry here is a
# contract discharged over no runs at all. This bucket used to be folded into "could not
# run standalone" together with modules that would not even LOAD — the same conflation the
# parameterized sibling removed in gen #30, kept here for a generation longer, and worth
# EIGHTEEN corpus functions the moment it was separated.
#
# Each one is named with its reason. An UNNAMED one fails the plane.
# `getting-better/open-routes/finding-a-verified-program-that-is-not-the-executed-program.md`
_DT = ("`#@ datatype` declares the constructors and Python defines them NOWHERE, while the "
       "body uses them in EXECUTABLE position (an assignment and a `match`). NameError on "
       "every call. The directive's names have no runtime counterpart — the same species as "
       "`#@ compose_from`, one directive over.")
NEVER_RETURNS = {
    ("0521.py", "build_and_read"): _DT,
    ("0527.py", "left_is_leaf"): _DT,
    ("0531.py", "guarded"): _DT,
    ("0533.py", "leaf_is_zero"): _DT,
    ("0535.py", "is_red_or_green"): _DT,
    ("0536.py", "unwrap"): _DT,
    ("0540.py", "use_int"): _DT,
    ("0546.py", "get"): _DT,
    ("1003_parametric_datatype_faithful.py", "use_int"): _DT,
    # NOT HERE, and the reason is worth a line: `0968_requires_method_frame.py::Counter`
    # raised `AttributeError: no attribute 'bump'` on the first split of this bucket, and
    # it is NOT a defect — `Counter` is a `#@ mixin`, verified in ISOLATION against an
    # abstract `val`, and the COMPOSER is what supplies `bump`. A mixin was never meant to
    # run standalone, so the oracle stopped constructing one. The finding is what the
    # COMPOSER does, and that is the `#@ compose_from` family recorded in the parameterized
    # sibling's own NEVER_RETURNS.
    ("0640.py", "f"):
        "`return ast.literal_eval(\"-5\")` in a file that never imports `ast`. PyCSL "
        "evaluates the call at VERIFICATION time with the host's own `ast` — which is what "
        "makes `\\result == -5` provable — and CPython answers `NameError: name 'ast' is "
        "not defined`. The verifier supplies a name the program does not have.",
    ("0642.py", "f"):
        "`exec(\"x = 5\\ny = x + 1\"); return y`. PyCSL splices the parsed statements in "
        "place, and the driver's own docstring calls the result "
        "'verification-equivalent … exactly as if written inline'. IT IS NOT: `exec` inside "
        "a function body CANNOT create a local binding in CPython, so `y` is unbound and "
        "the call is a NameError. Byte-identical emission to the inline form is evidence "
        "that the MODEL matches the inline form; it is not evidence that PYTHON does.",
}
MIN_RUNNABLE = 390   # first measurement 366 (functions only); the METHOD population
                     # added 39 more runnable contracts in its first measurement
                     # (42 candidates, 39 agree, 0 disagree, 3 unrunnable), so the
                     # floor moves with the reach. Both corpora only grow.


# (#49) gen #31 — THE COMPARISON OPERATORS, not only `==`. Route #226's carrier claims
# `\result >= 5`; a plane that reads only `==` could not have seen it.
OPS = {"==": lambda a, b: a == b, "!=": lambda a, b: a != b,
       ">=": lambda a, b: a >= b, "<=": lambda a, b: a <= b,
       ">": lambda a, b: a > b, "<": lambda a, b: a < b}
_ENS = re.compile(r"#@\s*ensures\s+\\result\s*(==|!=|>=|<=|>|<)\s*(-?\d+)\s*$")


def _claim_above(lines, lineno):
    """The `#@ ensures \result <op> <int>` attached to the def at `lineno`, and whether a
    `#@ requires` is attached too.

    Walks UPWARD and stops at the first line that is not a `#@` directive, a decorator or
    blank. A fixed window let the PREVIOUS method's block answer for this one — measured:
    `multi_file_lib/r119_plainlib.py`'s `K.n` picked up `K.m`'s `== 1` and read as a
    disagreement."""
    claim, has_req = None, False
    i = lineno - 2
    while i >= 0:
        t = lines[i].strip()
        if t.startswith("#@"):
            if re.match(r"#@\s*requires\b", t):
                has_req = True
            m = _ENS.match(t)
            if m and claim is None:
                claim = (m.group(1), int(m.group(2)))
            i -= 1
        elif t.startswith("@") or t == "":
            i -= 1
        else:
            break
    return claim, has_req


def candidates():
    out = []
    files = []
    for c in CORPORA:
        files += sorted(glob.glob(os.path.join(c, "*.py")))
        files += sorted(glob.glob(os.path.join(c, "**", "*.py"), recursive=True))
    for f in sorted(set(files)):
        src = open(f, errors="replace").read()
        if "# pycsl-expected: FAIL" in src:
            continue
        lines = src.split("\n")
        for i, l in enumerate(lines):
            m = re.match(r"\s*#@\s*ensures\s+\\result\s*==\s*(-?\d+)\s*$", l)
            if not m:
                continue
            for j in range(i + 1, min(i + 6, len(lines))):
                d = re.match(r"def (\w+)\(\s*\)\s*->\s*(int|bool)\s*:", lines[j].strip())
                if d:
                    out.append((f, None, d.group(1), "==", int(m.group(1))))
                    break
        # (#49) gen #31 — THE METHOD POPULATION. A zero-argument method of a class that
        # `C()` constructs is just as runnable as a zero-argument function, and it is the
        # shape route #226 carries. A method with a `#@ requires` is SKIPPED: its
        # precondition may be false of a default-constructed object, and then its
        # postcondition says nothing about it.
        try:
            tree = ast.parse(src)
        except Exception:
            continue
        for cls in ast.walk(tree):
            if not isinstance(cls, ast.ClassDef):
                continue
            # (#49) gen #31 — A `Protocol` CANNOT BE INSTANTIATED, and neither can a
            # `#@ mixin`. Building one produced `TypeError: Protocols cannot be
            # instantiated` and the plane reported it as a corpus function with no normal
            # exit — an ORACLE defect wearing a finding's clothes. A population must
            # exclude what the LANGUAGE (here Python's own `typing`, there PyCSL's
            # `PYCSL-SEM-MIXIN-INSTANTIATED`) forbids. Found by splitting the raise bucket,
            # in the same run that found eighteen real ones.
            _bases = {ast.unparse(b).split("[")[0].rsplit(".", 1)[-1] for b in cls.bases}
            if "Protocol" in _bases:
                continue
            _ci = cls.lineno - 2
            _mix = False
            while _ci >= 0 and (not lines[_ci].strip()
                                or lines[_ci].strip().startswith("#")):
                if lines[_ci].strip().startswith("#@") and \
                        lines[_ci].strip()[2:].strip().startswith("mixin"):
                    _mix = True
                _ci -= 1
            if _mix:
                continue
            init = next((x for x in cls.body
                         if isinstance(x, ast.FunctionDef) and x.name == "__init__"), None)
            if init is not None:
                nreq = (len(init.args.args) + len(init.args.posonlyargs)
                        - len(init.args.defaults))
                if nreq > 1 or init.args.kwonlyargs or init.args.vararg:
                    continue
            for meth in cls.body:
                if not isinstance(meth, ast.FunctionDef):
                    continue
                if len(meth.args.args) != 1 or meth.args.kwonlyargs or meth.args.vararg:
                    continue
                rt = meth.returns
                if not (isinstance(rt, ast.Name) and rt.id in ("int", "bool")):
                    continue
                claim, has_req = _claim_above(lines, meth.lineno)
                if claim is not None and not has_req:
                    out.append((f, cls.name, meth.name, claim[0], claim[1]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    rows = candidates()
    agree = 0
    disagree = []
    unrunnable = []
    raised = []                 # the FUNCTION raised: no normal exit, on no argument at all
    for f, cls, fn, op, claim in rows:
        src = open(f, errors="replace").read()
        ns = {"__name__": "corpus_contract_probe"}
        # MULTI-FILE tests import a sibling module out of the corpus directory. Putting
        # that directory on `sys.path` turns 8 `ModuleNotFoundError`s into real
        # measurements — coverage the first version left on the table. The path entry is
        # removed again so one test cannot shadow a name for the next.
        sys.path.insert(0, os.path.dirname(f))
        try:
            with contextlib.redirect_stdout(io.StringIO()), \
                 contextlib.redirect_stderr(io.StringIO()):
                exec(compile(src, f, "exec"), ns)
            if cls is None:
                if fn not in ns:
                    unrunnable.append((os.path.basename(f), fn, "not defined after exec"))
                    continue
                try:
                    got = ns[fn]()
                except BaseException as _e_fn:
                    raised.append((os.path.basename(f), fn, type(_e_fn).__name__,
                                   str(_e_fn)[:60]))
                    continue
            else:
                if cls not in ns:
                    unrunnable.append((os.path.basename(f), cls + "." + fn,
                                       "class not defined after exec"))
                    continue
                try:
                    got = getattr(ns[cls](), fn)()
                except BaseException as _e_fn:
                    raised.append((os.path.basename(f), cls + "." + fn,
                                   type(_e_fn).__name__, str(_e_fn)[:60]))
                    continue
        except Exception as e:
            unrunnable.append((os.path.basename(f), fn, type(e).__name__))
            continue
        finally:
            if sys.path and sys.path[0] == os.path.dirname(f):
                sys.path.pop(0)
        if isinstance(got, bool):
            got = int(got)
        if not isinstance(got, int):
            unrunnable.append((os.path.basename(f), fn, "non-int result"))
            continue
        _who = fn if cls is None else (cls + "." + fn)
        if OPS[op](got, claim):
            agree += 1
            if args.verbose:
                print("    ok  %s::%s %s %d" % (os.path.basename(f), _who, op, claim))
        else:
            disagree.append((os.path.basename(f), _who, "%s %d" % (op, claim), got))

    print("[*] corpus-contract-truth: %d runnable literal-result contract(s) — "
          "%d AGREE with CPython, %d DISAGREE, %d could not run standalone."
          % (len(rows), agree, len(disagree), len(unrunnable)))
    if args.verbose:
        for b in unrunnable:
            print("    unrunnable  %s::%s (%s)" % b)

    _nr_bad = [r for r in raised if (r[0], r[1]) not in NEVER_RETURNS]
    print("[*] corpus-contract-truth: NO-NORMAL-EXIT — %d zero-argument function(s) RAISE "
          "on the only call there is, so their `#@ ensures` is discharged over no runs at "
          "all; %d named with a reason. (Distinct from %d module(s) that would not load.)"
          % (len(raised), len(raised) - len(_nr_bad), len(unrunnable)))
    for _r in sorted(raised):
        print("      %-46s %s: %s" % (_r[0] + "::" + _r[1], _r[2], _r[3]))
    if _nr_bad:
        print("[!]   A ZERO-ARGUMENT FUNCTION WITH NO NORMAL EXIT IS NOT NAMED: %s. Its "
              "`#@ ensures` is vacuously true — the prover discharges a claim about an exit "
              "the function does not have. Diagnose it and add it to NEVER_RETURNS with its "
              "reason, or repair it." % ([(r[0], r[1], r[2]) for r in _nr_bad],),
              file=sys.stderr)
        return 1

    if agree + len(disagree) < MIN_RUNNABLE:
        print("[!] corpus-contract-truth: REFUSING — only %d contract(s) actually ran, "
              "expected at least %d. A gate that cannot tell 'nothing is wrong' from "
              "'I ran nothing' is not a gate." % (agree + len(disagree), MIN_RUNNABLE),
              file=sys.stderr)
        return 2

    if disagree:
        for b in disagree:
            print("[!]   DISAGREES WITH CPYTHON: %s::%s — the contract claims %r, the "
                  "program returns %r" % b, file=sys.stderr)
        print("[!] corpus-contract-truth: NOT OK — a corpus test whose own postcondition "
              "is FALSE of its own program is a route witness hiding inside a green test.",
              file=sys.stderr)
        return 1

    print("[+] corpus-contract-truth: OK — every runnable corpus postcondition is true of "
          "the program it is written about.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
