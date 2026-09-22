#!/usr/bin/env python3
r"""L-PLANE ORACLE: the reference corpus's PARAMETERIZED passing contracts, measured
against CPython on a fixed argument pool.

WHY THIS EXISTS (gen #30). `bin/check-corpus-contract-truth.py` runs every ZERO-ARGUMENT
literal postcondition in both corpora under CPython — 379 candidates, 367 agreeing — and
its own header names what it does not do:

    WHAT IT DOES NOT CHECK: contracts with parameters, non-literal right-hand sides,
    quantifiers, or `\result` of a non-int/bool return. Those are the value-differential
    corpus's job, and writing a driver there is the way to cover one.

That sentence was read the way this campaign reads every justification: as a CHECKABLE
CLAIM about coverage. "Writing a driver" covers ONE contract by hand; the corpus holds
FIVE HUNDRED parameterized ones that are just as runnable, because an `#@ ensures \result
== <arithmetic over the parameters>` is a Python expression once the parameters have
values. This plane supplies the values from a fixed pool, filtered by the function's own
`requires`, and compares.

WHAT A FAILURE HERE MEANS — the same sharp verdict as its zero-argument sibling: a corpus
test that PASSES the prover while its own postcondition is FALSE of its own program, on an
argument its own precondition admits. That is a route witness hiding inside a green test.

FIRST MEASUREMENT (gen #30): 412 functions, 4340 argument-level evaluations, **0
DISAGREE**. Getting to that zero took four exclusions, and EACH ONE IS A FINDING rather
than a convenience:

  `\trusted` functions are EXCLUDED, and so are their CALLERS. 0053 is the type case:
      #@ ensures \result == 2 * x
      #@ \trusted
      def double_int(x: int) -> int:  return x + x + x     # THREE x, deliberately
  The trusted contract is assumed, not proven, so the disagreement is the DOCUMENTED PRICE
  OF TRUST. What is not documented anywhere else is the BLAST RADIUS: `foobar`, which
  merely CALLS `double_int` and has a body of its own, proves `\result == 2 * x` while
  CPython answers `3 * x`. Those are counted separately and reported every run
  (TRUST_INHERITED_BASELINE), because "one trusted function" and "every caller of one
  trusted function" are different sizes of claim.

  `# pycsl-flags: --fun NAME` files are RESTRICTED to NAME and its transitive callees.
  0054 and 0055 carry a function whose spec is marked "intentionally wrong" in a comment
  and which `--fun` means the run never verifies. Checking it would be checking something
  the suite never claimed.

  `#@ act` / `given` behaviour blocks are SKIPPED (2 functions): their postconditions are
  GUARDED, and evaluating a guarded `ensures` unconditionally is a bug in the ORACLE, not
  a finding about the corpus. `0455.clamp10` is the witness — `ensures \result == 10`
  holds only under `given x >= 10`.

  `# pycsl-flags: --no-proof` files are SKIPPED, and their number is THE FINDING OF THIS
  PLANE: **1754 of the 3881 corpus files — 45% — run with the prover switched off.** For
  those files a suite PASS means "the pipeline did not crash", not "the contracts hold",
  and two of them (`ceil_overclaim_fails.py`, `floor_overclaim_fails.py`) carry a
  deliberately too-strong postcondition under `# pycsl-expected: PASS`, which is only
  consistent BECAUSE proving is off. Nothing was wrong with those files; what was wrong
  was that no instrument printed the 45%. The share is now printed every run and capped.

THE RATCHETS: any non-inherited DISAGREE fails; the trust-inherited count may not grow;
the `--no-proof` SHARE may not grow. THE POPULATION GUARD (the #44 rule): rc=2 below
MIN_EVALS evaluations, so a green can never mean "I ran nothing".

Usage:  bin/check-corpus-contract-truth-args.py [--verbose]
"""
import argparse
import ast
import contextlib
import glob
import io
import itertools
import os
import re
import signal
import sys
import warnings

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORPORA = [os.path.join(ROOT, "test-suite", "corpus", "pycsl-reference"),
           os.path.join(ROOT, "test-suite", "corpus", "python-reference")]

# CSL tokens this oracle cannot evaluate as Python. A contract carrying one is skipped
# whole — an oracle that guesses at `\forall` reports its own bugs as corpus defects.
SKIP_TOKENS = ("\\forall", "\\exists", "\\old", "\\at", "\\length", "\\separated",
               "\\valid", "\\sum", "\\is_sorted", "\\permutation", "\\array_eq",
               "==>", "\\result[", "\\nothing", "\\let")
POOL = [0, 1, 2, 3, 5, -1, -2, 7]
MAX_TUPLES = 40          # per function, deterministic prefix of the product
CALL_TIMEOUT = 1.0       # seconds; a corpus loop must not hang the battery
EXEC_TIMEOUT = 2.0
MIN_EVALS = 3800         # 4340 at the first measurement; the corpus only grows
TRUST_INHERITED_BASELINE = 14    # disagreements a caller INHERITS from a trusted callee
MAX_RAISED = 3                   # calls that RAISE on an argument the precondition admits.
# THE THREE, EACH NAMED, because "3" on its own would be a shrug:
#   0159.py::diverges_inc(0)      RecursionError. `#@ \diverges` over `return
#                                 diverges_inc(x)` — the file EXISTS to be non-terminating,
#                                 and CPython's recursion limit is how non-termination
#                                 shows up in a differential. Correct, and not a defect.
#   0496.py::grab(0)              TypeError. `Holder(k)` is a class the oracle's plain
#                                 `exec` cannot construct the way the model does. An
#                                 instrument limit, not a claim about the program.
#   0420.py::roundtrip_two_ints(0, -1)   `struct.error`. THIS ONE IS THE OBSERVATION. The
#                                 function claims `#@ ensures \result == x0` with NO range
#                                 precondition and PROVES it by citing
#                                 `UnixFs.Struct.i2.round_trip`, which is quantified
#                                 `forall fmt x0 x1 : int` with NO guard — while
#                                 `struct.pack('>HH', x0, x1)` RAISES for any x0 outside
#                                 [0, 65536). The SUCCESSOR family in the same registry,
#                                 `Pycsl.Struct.Std.round_trip_u16u32`, carries
#                                 `0 <= x0 < 65536 ->` and its comment says the guard is
#                                 "faithful to CPython's out-of-range struct.error". So the
#                                 repo's own standard disagrees with the legacy axiom.
NO_PROOF_SHARE_CEILING = 0.46    # 1754/3881 = 0.452 at the first measurement


class _Timeout(Exception):
    pass


def _alarm(_sig, _frm):
    raise _Timeout()


def _calls(node):
    return {n.func.id for n in ast.walk(node)
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}


def collect(no_exclusions=False):
    """Per file: the functions whose contracts this oracle can evaluate, plus the census
    numbers for everything it deliberately leaves out."""
    files = []
    for c in CORPORA:
        files += sorted(glob.glob(os.path.join(c, "*.py")))
        files += sorted(glob.glob(os.path.join(c, "**", "*.py"), recursive=True))
    files = sorted(set(files))
    per, stats = {}, {"files": len(files), "no_proof": 0, "acts": 0, "trusted": 0,
                      "fun_restricted": 0}
    for f in files:
        src = open(f, errors="replace").read()
        if "# pycsl-expected: FAIL" in src:
            continue
        if re.search(r"^# pycsl-flags:.*--no-proof", src, re.M):
            stats["no_proof"] += 1
            if not no_exclusions:
                continue
        lines = src.split("\n")
        try:
            tree = ast.parse(src)
        except SyntaxError:
            continue
        m = re.search(r"^# pycsl-flags:.*--fun\s+(\w+)", src, re.M)
        only = m.group(1) if m else None
        defs = {n.name: n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}

        def annotations_of(node):
            out, i = [], node.lineno - 2
            while i >= 0 and (not lines[i].strip() or lines[i].strip().startswith("#")):
                if lines[i].strip().startswith("#@"):
                    out.append(lines[i].strip())
                i -= 1
            return out

        trusted = {n for n, d in defs.items()
                   if any("\\trusted" in a for a in annotations_of(d))}

        def reach(name, seen=None):
            seen = set() if seen is None else seen
            if name in seen or name not in defs:
                return seen
            seen.add(name)
            for c in _calls(defs[name]):
                if c in defs:
                    reach(c, seen)
            return seen

        verified = reach(only) if only else set(defs)
        if only:
            stats["fun_restricted"] += len(defs) - len(verified)
        for name, node in defs.items():
            ps = node.args.args
            if not ps or len(ps) > 3 or any(a.arg == "self" for a in ps):
                continue
            if not all(isinstance(a.annotation, ast.Name)
                       and a.annotation.id in ("int", "bool") for a in ps):
                continue
            if not (isinstance(node.returns, ast.Name)
                    and node.returns.id in ("int", "bool")):
                continue
            ann = annotations_of(node)
            ens = [m.group(1).strip() for m in
                   (re.match(r"#@\s*ensures\s+\\result\s*==\s*(.+)$", a) for a in ann) if m]
            if not ens:
                continue
            if any(t in " ".join(ann) for t in SKIP_TOKENS):
                continue
            if any(re.match(r"#@\s*(act|behavior)\b", a) or re.match(r"#@\s+given\b", a)
                   for a in ann):
                stats["acts"] += 1
                continue
            if name in trusted:
                stats["trusted"] += 1
                if not no_exclusions:
                    continue
            if name not in verified and not no_exclusions:
                continue
            reqs = [m.group(1).strip() for m in
                    (re.match(r"#@\s*requires\s+(.+)$", a) for a in ann) if m]
            if any("\\" in x for x in reqs + ens):
                continue
            per.setdefault(f, []).append(
                (name, [a.arg for a in ps], ens, reqs, bool(reach(name) & trusted)))
    return per, stats


def _py(expr):
    return expr.replace("&&", " and ").replace("||", " or ")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--selftest-no-exclusions", action="store_true",
                    help="drop the `--no-proof`, `\\trusted` and `--fun` exclusions and "
                         "run the oracle over everything; must exit 1, because the corpus "
                         "really does contain deliberately-false contracts (0053's "
                         "trusted `return x + x + x` under `ensures \\result == 2 * x`). "
                         "This is the gate's BITE TEST on real data, not a fixture.")
    args = ap.parse_args()

    signal.signal(signal.SIGALRM, _alarm)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        per, stats = collect(no_exclusions=args.selftest_no_exclusions)
    agree = 0
    disagree, inherited, unrunnable, raised = [], [], [], []
    funcs = 0

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for f, items in per.items():
            ns = {"__name__": "corpus_contract_args_probe"}
            d = os.path.dirname(f)
            sys.path.insert(0, d)
            try:
                with contextlib.redirect_stdout(io.StringIO()), \
                     contextlib.redirect_stderr(io.StringIO()):
                    signal.setitimer(signal.ITIMER_REAL, EXEC_TIMEOUT)
                    exec(compile(open(f, errors="replace").read(), f, "exec"), ns)
                    signal.setitimer(signal.ITIMER_REAL, 0)
            except BaseException as exc:
                signal.setitimer(signal.ITIMER_REAL, 0)
                unrunnable += [(os.path.basename(f), n, type(exc).__name__)
                               for n, _, _, _, _ in items]
                continue
            finally:
                signal.setitimer(signal.ITIMER_REAL, 0)
                if sys.path and sys.path[0] == d:
                    sys.path.pop(0)
            for name, params, ens, reqs, inherits in items:
                funcs += 1
                fn = ns.get(name)
                if not callable(fn):
                    unrunnable.append((os.path.basename(f), name, "not callable"))
                    continue
                tested = 0
                for tup in itertools.product(POOL, repeat=len(params)):
                    if tested >= MAX_TUPLES:
                        break
                    env = dict(zip(params, tup))
                    try:
                        if not all(eval(_py(r), {"__builtins__": {}}, dict(env))
                                   for r in reqs):
                            continue
                    except Exception:
                        break
                    try:
                        signal.setitimer(signal.ITIMER_REAL, CALL_TIMEOUT)
                        with contextlib.redirect_stdout(io.StringIO()), \
                             contextlib.redirect_stderr(io.StringIO()):
                            got = fn(*tup)
                        signal.setitimer(signal.ITIMER_REAL, 0)
                        claims = [eval(_py(e), {"__builtins__": {}}, dict(env))
                                  for e in ens]
                    except BaseException as exc:
                        signal.setitimer(signal.ITIMER_REAL, 0)
                        # (#49) gen #30 — A CALL THAT **RAISES** IS NOT THE SAME AS A
                        # MODULE THAT WILL NOT LOAD. The first version lumped both into
                        # "unrunnable", and that hid the sharpest observation this oracle
                        # has made: `0420.py::roundtrip_two_ints` claims
                        # `#@ ensures \result == x0` with NO range precondition and PROVES
                        # it, while `struct.pack('>HH', x0, x1)` RAISES `struct.error` for
                        # any x0 outside [0, 65536) — the model asserts a normal exit with
                        # value x0 where CPython has none. §2.1.13 puts exceptional exits
                        # out of scope unless `#@ no_exception` is declared, so this is
                        # REPORTED rather than failed — but it is reported, with a ceiling,
                        # because the repo's OWN standard disagrees with it: the successor
                        # axiom family `Pycsl.Struct.Std.round_trip_*` carries per-field
                        # range guards whose comment says they are "faithful to CPython's
                        # out-of-range struct.error", while the legacy
                        # `UnixFs.Struct.i2.round_trip` this file cites is UNGUARDED.
                        raised.append((os.path.basename(f), name, tup,
                                       type(exc).__name__))
                        break
                    tested += 1
                    got = int(got) if isinstance(got, bool) else got
                    bad = None
                    for e_src, claim in zip(ens, claims):
                        claim = int(claim) if isinstance(claim, bool) else claim
                        if got != claim:
                            bad = (os.path.basename(f), name, tup, e_src, claim, got)
                            break
                    if bad is None:
                        agree += 1
                    elif inherits:
                        inherited.append(bad)
                    else:
                        disagree.append(bad)

    share = stats["no_proof"] / float(stats["files"]) if stats["files"] else 0.0
    print("[*] corpus-contract-truth-args: %d function(s), %d argument-level "
          "evaluation(s) — %d AGREE, %d DISAGREE, %d inherited from a `\\trusted` "
          "callee, %d RAISED on an admitted argument, %d unrunnable."
          % (funcs, agree + len(disagree) + len(inherited), agree, len(disagree),
             len(inherited), len(raised), len(unrunnable)))
    print("[*] corpus-contract-truth-args: EXCLUSIONS — %d file(s) carry `--no-proof` "
          "(%.1f%% of %d corpus files: a PASS there means the pipeline did not crash, "
          "NOT that the contracts hold), %d `\\trusted` function(s), %d behaviour-block "
          "function(s), %d function(s) outside a `--fun` restriction."
          % (stats["no_proof"], 100.0 * share, stats["files"], stats["trusted"],
             stats["acts"], stats["fun_restricted"]))
    if args.verbose:
        for r in raised:
            print("    RAISED     %s::%s%r  -> %s (the contract promises a value on an "
                  "argument its own `requires` admits)" % r)
        for b in inherited:
            print("    inherited  %s::%s%r  ensures %s -> %r, CPython %r" % b)
        for u in unrunnable[:40]:
            print("    unrunnable %s::%s (%s)" % u)

    evals = agree + len(disagree) + len(inherited)
    if evals < MIN_EVALS:
        print("[!] corpus-contract-truth-args: REFUSING — only %d evaluation(s) ran, "
              "expected at least %d. A gate that cannot tell 'nothing is wrong' from "
              "'I ran nothing' is not a gate." % (evals, MIN_EVALS), file=sys.stderr)
        return 2

    rc = 0
    for b in disagree:
        print("[!]   CONTRACT FALSE OF ITS OWN PROGRAM: %s::%s%r — `ensures \\result == "
              "%s` says %r, CPython answers %r. The file is expected to PASS and its "
              "precondition admits that argument." % b, file=sys.stderr)
        rc = 1
    if args.selftest_no_exclusions:
        if disagree:
            print("[+] SELFTEST: %d disagreement(s) found with the exclusions dropped — "
                  "the oracle bites." % len(disagree))
            return 1
        print("[!] SELFTEST FAILED: dropping every exclusion found NO disagreement, so "
              "this oracle cannot detect a false contract at all.", file=sys.stderr)
        return 2
    if len(raised) > MAX_RAISED:
        print("[!]   RAISED-ON-ADMITTED-ARGUMENT COUNT GREW: %d > %d. Each one is a "
              "contract that promises a value where CPython has no normal exit at all."
              % (len(raised), MAX_RAISED), file=sys.stderr)
        rc = 1
    if len(inherited) > TRUST_INHERITED_BASELINE:
        print("[!]   TRUST BLAST RADIUS GREW: %d caller-level disagreements inherited "
              "from `\\trusted` callees, ceiling %d."
              % (len(inherited), TRUST_INHERITED_BASELINE), file=sys.stderr)
        rc = 1
    if share > NO_PROOF_SHARE_CEILING:
        print("[!]   `--no-proof` SHARE GREW: %.1f%% of corpus files run with the prover "
              "off, ceiling %.1f%%. Every one of those is a suite PASS that proves "
              "nothing." % (100.0 * share, 100.0 * NO_PROOF_SHARE_CEILING),
              file=sys.stderr)
        rc = 1

    if rc:
        print("[!] corpus-contract-truth-args: NOT OK.", file=sys.stderr)
    else:
        print("[+] corpus-contract-truth-args: OK — every parameterized postcondition "
              "this oracle can evaluate is TRUE of its own program on the pool (%d "
              "evaluations); %d inherited disagreement(s) at the ceiling."
              % (evals, len(inherited)))
    return rc


if __name__ == "__main__":
    sys.exit(main())
