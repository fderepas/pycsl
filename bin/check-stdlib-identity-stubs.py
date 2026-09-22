#!/usr/bin/env python3
r"""L-PLANE ORACLE: a `pycsl_lib` function whose body is `return <a parameter>` and whose
contract PINS that identity.

WHY THIS EXISTS (gen #30, the THIRD stdlib plane). The first two cover the two shapes I
had found: `check-stdlib-contract-fidelity.py` CALLS the real function (so it carries a
safety deny-list and can only reach pure modules), and `check-stdlib-pinned-facades.py`
covers, statically, the bodies that are a single CONSTANT pinned by their own contract.
Widening the fidelity map in gen #30 turned up SIX diverging functions that are neither:
`ctxlib.closing/contextmanager/nullcontext`, `ftools.lru_cache/wraps`, `pp.saferepr`. Their
shape is

    #@ ensures \result == func
    def wraps(func):
        return func

— the body is the IDENTITY on a parameter and the contract pins it. The contract is true
of the body and FALSE of the function the module's own header cites: real
`functools.wraps` returns a `functools.partial` of `update_wrapper`, real
`contextlib.closing` returns a context-manager OBJECT, real `pprint.saferepr` returns a
STRING. A user who proves `ftools.wraps(g) == g` has proven something CPython contradicts.

WHY A PLANE AND NOT SIX BASELINE ENTRIES. Because the shape is POPULOUS and most of it is
OUT OF THE CALLING GATE'S REACH. The census finds 82 of them across 30 packages, and they
sit in `os`, `shutl`, `pkl`, `rng`, `hmacmod` — modules the fidelity gate must never call.
So the six that were caught were caught by ACCIDENT OF PURITY, not by coverage: the same
defect in `shutl.move` (real `shutil.move` returns the DESTINATION path, not `src`) can
never be found by calling. This gate is the static complement, exactly as the facade gate
is for constants.

NOT EVERY MEMBER IS A DEFECT, and the gate does not pretend otherwise. `mth.fabs` under
`requires x >= 0` IS the identity; `typ.cast` really does return its value; `astmod`'s
in-place transformers really do return the node they were handed. The population splits
three ways and each entry says which it is:

  FAITHFUL   — the real function really is the identity here (or is under the stated
               precondition). Sound, and it stays sound.
  DIVERGES   — the real function returns something else. Already PROVEN so by the calling
               gate, and cross-checked here: every DIVERGES entry in a module the fidelity
               map covers must also appear in THAT gate's baseline, or this gate fails.
  UNADJUDICATED — the module is outside the calling gate's reach and no one has ruled on
               it yet. This is the honest state for most of the population, and it is
               WRITTEN DOWN rather than left as an unmentioned gap — the gen #30 lesson
               from the fidelity plane's own scope claim ("an unmentioned exclusion is not
               an exclusion, it is an oversight wearing one").

THE RATCHET is the set, keyed by (package, function). A NEW identity-stub fails: it must
be argued into one of the three classes. One that DISAPPEARS is reported so its entry goes
with it. UNADJUDICATED is a debt counter, printed every run, and MAX_UNADJUDICATED holds
it from growing.

THE POPULATION GUARD (the #44 rule): rc=2 if the walk sees fewer than MIN_FUNCTIONS
functions at all, so "no identity stubs" can never mean "I parsed nothing".

Usage:  bin/check-stdlib-identity-stubs.py [--verbose] [--selftest-empty-baseline]
"""
import argparse
import ast
import glob
import os
import sys
import warnings

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIB = os.path.join(ROOT, "src", "pycsl_lib")
MIN_FUNCTIONS = 700      # 870 at the first measurement
MIN_STUBS = 70           # 82 at the first measurement; the stub set only grows

FAITHFUL, DIVERGES, UNADJ = "FAITHFUL", "DIVERGES", "UNADJUDICATED"

# (package, function) -> (class, why)
BASELINE = {
    # ---- DIVERGES: proven false against the real function by the calling gate.
    ("ctxlib", "closing"): (DIVERGES,
        "real `contextlib.closing` returns a closing CONTEXT MANAGER wrapping obj."),
    ("ctxlib", "contextmanager"): (DIVERGES,
        "real `contextlib.contextmanager` returns a generator-driven HELPER function."),
    ("ctxlib", "nullcontext"): (DIVERGES,
        "real `contextlib.nullcontext` returns a nullcontext OBJECT, not the value."),
    ("ftools", "lru_cache"): (DIVERGES,
        "real `functools.lru_cache` returns a DECORATING FUNCTION."),
    ("ftools", "wraps"): (DIVERGES,
        "real `functools.wraps` returns a `functools.partial` of `update_wrapper`."),
    ("pp", "saferepr"): (DIVERGES,
        "real `pprint.saferepr` returns the STRING repr — `saferepr(0)` is `'0'`."),

    # ---- FAITHFUL: the real function is the identity, here or under the precondition.
    ("mth", "fabs"): (FAITHFUL, "`requires x >= 0`, so `abs(x) == x`."),
    ("mth", "floor"): (FAITHFUL, "integer model: `floor` of an int is the int."),
    ("mth", "ceil"): (FAITHFUL, "integer model: `ceil` of an int is the int."),
    ("mth", "trunc"): (FAITHFUL, "integer model: `trunc` of an int is the int."),
    ("oper", "pos"): (FAITHFUL, "`operator.pos(x)` is `+x`, the identity on ints."),
    ("oper", "abs_val"): (FAITHFUL, "guarded by `requires x >= 0` in the stub."),
    ("oper", "index"): (FAITHFUL, "`operator.index` of an int is that int."),
    ("nums", "to_int"): (FAITHFUL, "int of an int."),
    ("typ", "cast"): (FAITHFUL, "`typing.cast(t, v)` really does return `v` unchanged."),
    ("typ", "Union"): (FAITHFUL, "erased type constructor; the model carries the value."),
    ("typ", "Literal"): (FAITHFUL, "erased type constructor; the model carries the value."),
    ("typ", "Final"): (FAITHFUL, "erased type constructor; the model carries the value."),
    ("typ", "TypedDict"): (FAITHFUL, "erased type constructor; the model carries the value."),
    ("typ", "NamedTuple"): (FAITHFUL, "erased type constructor; the model carries the value."),
    ("typ", "overload"): (FAITHFUL, "`typing.overload` returns the function it decorates."),
    ("typ", "runtime_checkable"): (FAITHFUL,
        "`typing.runtime_checkable` returns the class it decorates."),
    ("astmod", "copy_location"): (FAITHFUL, "`ast.copy_location` returns `new_node`."),
    ("astmod", "fix_missing_locations"): (FAITHFUL,
        "`ast.fix_missing_locations` returns the node it was handed."),
    ("astmod", "increment_lineno"): (FAITHFUL, "`ast.increment_lineno` returns the node."),
    ("abcmod", "abstractmethod"): (FAITHFUL,
        "`abc.abstractmethod` returns the function, with `__isabstractmethod__` set."),
    ("cpmod", "copy"): (FAITHFUL,
        "in the INTEGER model a copy is `==` to its original, which is all the contract "
        "claims; the calling gate agrees on the pool."),
    ("cpmod", "deepcopy"): (FAITHFUL, "same as `copy` in the integer model."),
    ("gettext_stub", "gettext"): (FAITHFUL,
        "with no catalogue installed, `gettext.gettext(s)` returns `s`."),
    ("htmlm", "escape"): (FAITHFUL, "the contract is GUARDED (`s == 0 ==> ...`), not a "
        "bare identity; the empty/0 case is the one it pins."),
    ("htmlm", "unescape"): (FAITHFUL, "guarded the same way."),
    ("htmlm", "escape_quote"): (FAITHFUL, "guarded the same way."),
    ("txtwrp", "fill"): (FAITHFUL, "guarded (`text == 0 ==> \\result == 0`)."),
    ("strmod", "capwords"): (FAITHFUL,
        "doubly guarded (`sep == \"\" ==> (s == \"\" ==> \\result == \"\")`)."),
    ("wref", "ref"): (FAITHFUL,
        "MODEL-DOMAIN identity: the stub's `ref` carries the referent through because the "
        "integer model has no weak references; the calling gate evaluates it and the "
        "contract holds on the pool. Re-open if the model ever grows real references."),
    ("wref", "proxy"): (FAITHFUL, "same model-domain argument as `ref`."),

    # ---- UNADJUDICATED: outside the calling gate's reach, not yet ruled on.
    ("abcmod", "abstractclassmethod"): (UNADJ, "deprecated alias; returns a classmethod "
        "OBJECT in CPython — likely DIVERGES, needs the call to confirm."),
    ("abcmod", "abstractstaticmethod"): (UNADJ, "same shape as abstractclassmethod."),
    ("abcmod", "update_abstractmethods"): (UNADJ, "returns the class; likely FAITHFUL."),
    ("copyreg", "constructor"): (UNADJ, "`copyreg.constructor` returns None in CPython."),
    ("csvmod", "write_row"): (UNADJ, "csv is on the filesystem deny-list."),
    ("cvar", "context_var_get"): (UNADJ, "contextvars model; no citation run."),
    ("cvar", "context_var_set"): (UNADJ, "contextvars model; no citation run."),
    ("dec", "getcontext_prec"): (UNADJ, "decimal context model; no citation run."),
    ("ftools", "partial"): (UNADJ,
        "real `functools.partial(f)` returns a partial OBJECT, not `f` — but it compares "
        "unequal only because the model has no callables; adjudicate with the six."),
    ("ftools", "cache"): (UNADJ, "same family as `lru_cache`; the calling gate did not "
        "reach it (no contract it could evaluate on the pool)."),
    ("hmacmod", "new_hmac"): (UNADJ, "returns an HMAC object; the stub models the digest "
        "SIZE, so this may be a declared domain change."),
    ("hmacmod", "digest"): (UNADJ, "same size-domain question."),
    ("hpq", "heappushpop"): (UNADJ, "size-domain model of heapq."),
    ("hpq", "heapreplace"): (UNADJ, "size-domain model of heapq."),
    ("hpq", "heapify"): (UNADJ, "size-domain model of heapq."),
    ("hpq", "nsmallest"): (UNADJ, "size-domain model of heapq."),
    ("hpq", "nlargest"): (UNADJ, "size-domain model of heapq."),
    ("hq", "heapreplace"): (UNADJ, "size-domain model of heapq."),
    ("hq", "heapify"): (UNADJ, "size-domain model of heapq."),
    ("hq", "heappushpop"): (UNADJ, "size-domain model of heapq."),
    ("hq", "heapify_max"): (UNADJ, "size-domain model of heapq."),
    ("hq", "heappushpop_max"): (UNADJ, "size-domain model of heapq."),
    ("hq", "heapreplace_max"): (UNADJ, "size-domain model of heapq."),
    ("itools", "count_n"): (UNADJ, "counter-domain model of itertools."),
    ("itools", "repeat_n"): (UNADJ, "counter-domain model of itertools."),
    ("nums", "rational_num"): (UNADJ, "numerator accessor of the rational model."),
    ("nums", "rational_den"): (UNADJ, "denominator accessor of the rational model."),
    ("os", "_encode_name"): (UNADJ, "`os` is on the calling gate's deny-list."),
    ("os", "_decode_name"): (UNADJ, "`os` is on the calling gate's deny-list."),
    ("os", "fsdecode"): (UNADJ, "`os.fsdecode(str)` IS the identity; confirm for bytes."),
    ("os", "fsencode"): (UNADJ, "`os.fsencode(str)` returns BYTES — likely DIVERGES."),
    ("os", "fspath"): (UNADJ, "`os.fspath(str)` is the identity; confirm for PathLike."),
    ("os", "getenv"): (UNADJ, "returns `default` only when the name is unset."),
    ("os", "expanduser"): (UNADJ,
        "marked `#@ interface`; `os.path.expanduser` REWRITES a leading `~`."),
    ("pkl", "dump"): (UNADJ, "real `pickle.dump` returns None — size-domain model."),
    ("pp", "pformat"): (UNADJ,
        "real `pprint.pformat` returns a STRING, like `saferepr`; two stubs share the "
        "name in this package (one on `obj`, one on `obj_size`) and only the `obj` one "
        "was evaluated."),
    ("rng", "sample_len"): (UNADJ, "`random` is on the non-determinism deny-list."),
    ("shutl", "copy"): (UNADJ,
        "real `shutil.copy` returns the DESTINATION path, not `src` — likely DIVERGES, "
        "and unreachable by calling (filesystem)."),
    ("shutl", "copy2"): (UNADJ, "same as `shutl.copy`."),
    ("shutl", "move"): (UNADJ, "real `shutil.move` returns the destination."),
    ("strct", "calcsize"): (UNADJ, "fmt-domain model of struct."),
    ("strct", "pack"): (UNADJ, "real `struct.pack` returns BYTES."),
    ("strct", "unpack"): (UNADJ, "real `struct.unpack` returns a TUPLE."),
    ("strct", "unpack_from"): (UNADJ, "real `struct.unpack_from` returns a TUPLE."),
    ("strct", "pack_into"): (UNADJ, "real `struct.pack_into` returns None."),
}
MAX_UNADJUDICATED = 45   # 45 at the first measurement; a debt that may only shrink


def census():
    """Every (package, function, param) whose body is `return <param>` under a pinning
    `#@ ensures` that mentions that parameter. Pure AST; nothing is imported or called."""
    stubs, functions = [], 0
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for path in sorted(glob.glob(os.path.join(LIB, "**", "*.py"), recursive=True)):
            src = open(path, encoding="utf-8").read()
            lines = src.splitlines()
            try:
                tree = ast.parse(src)
            except SyntaxError:
                continue
            pkg = os.path.basename(os.path.dirname(path))
            for node in ast.walk(tree):
                if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                functions += 1
                body = [n for n in node.body
                        if not (isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant)
                                and isinstance(n.value.value, str))]
                if len(body) != 1 or not isinstance(body[0], ast.Return):
                    continue
                ret = body[0].value
                if not isinstance(ret, ast.Name):
                    continue
                params = [a.arg for a in node.args.args if a.arg != "self"]
                if ret.id not in params:
                    continue
                ann = []
                i = node.lineno - 2
                while i >= 0 and (not lines[i].strip() or lines[i].strip().startswith("#")):
                    if lines[i].strip().startswith("#@"):
                        ann.append(lines[i].strip())
                    i -= 1
                if any("ensures" in a and "\\result ==" in a for a in ann):
                    stubs.append((pkg, node.name, ret.id))
    return stubs, functions


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--selftest-empty-baseline", action="store_true",
                    help="run with an EMPTY baseline; must exit 1 (proves the gate bites)")
    args = ap.parse_args()

    baseline = {} if args.selftest_empty_baseline else BASELINE
    stubs, functions = census()

    if functions < MIN_FUNCTIONS:
        print("[!] stdlib-identity-stubs: REFUSING — the walk saw only %d function(s), "
              "expected at least %d. The glob is broken; this is not a pass."
              % (functions, MIN_FUNCTIONS), file=sys.stderr)
        return 2
    if len(stubs) < MIN_STUBS and not args.selftest_empty_baseline:
        print("[!] stdlib-identity-stubs: REFUSING — %d identity stub(s) found, expected "
              "at least %d. The matcher is broken; this is not a pass."
              % (len(stubs), MIN_STUBS), file=sys.stderr)
        return 2

    keys = {(p, f) for p, f, _ in stubs}
    new = sorted(k for k in keys if k not in baseline)
    gone = sorted(k for k in baseline if k not in keys)
    unadj = sorted(k for k in keys if baseline.get(k, (None,))[0] == UNADJ)
    diverges = sorted(k for k in keys if baseline.get(k, (None,))[0] == DIVERGES)

    if args.verbose:
        for p, f, a in sorted(stubs):
            cls = baseline.get((p, f), ("NEW", ""))[0]
            print("    %-13s %-9s %-22s <- %s" % (cls, p, f, a))

    print("[*] stdlib-identity-stubs: %d function(s) scanned; %d identity stub(s) with a "
          "pinning contract; %d DIVERGES, %d UNADJUDICATED."
          % (functions, len(keys), len(diverges), len(unadj)))

    rc = 0
    # Cross-check: a DIVERGES in a module the CALLING gate covers must also be in ITS
    # baseline, or the two planes disagree about the same function.
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "_fid", os.path.join(ROOT, "bin", "check-stdlib-contract-fidelity.py"))
        fid = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(fid)
        for k in diverges:
            if k[0] in fid.MAP and k not in fid.BASELINE:
                print("[!]   %s.%s is DIVERGES here but is NOT in the calling gate's "
                      "baseline, and its module IS in that gate's map. The two planes "
                      "disagree." % k, file=sys.stderr)
                rc = 1
    except Exception as exc:                                  # pragma: no cover
        print("[!]   cross-check against the calling gate failed: %r" % (exc,),
              file=sys.stderr)
        rc = 1

    for k in gone:
        print("[+]   baselined identity stub %s.%s IS GONE — remove its entry." % k)
    for k in new:
        print("[!]   NEW IDENTITY STUB %s.%s — a body `return <param>` pinned by its own "
              "`ensures`. Argue it into FAITHFUL (the real function IS the identity), "
              "DIVERGES (it is not, and the calling gate agrees), or UNADJUDICATED, and "
              "add it to the baseline." % k, file=sys.stderr)
        rc = 1
    if len(unadj) > MAX_UNADJUDICATED:
        print("[!]   UNADJUDICATED count %d exceeds the ceiling %d — this debt may only "
              "shrink." % (len(unadj), MAX_UNADJUDICATED), file=sys.stderr)
        rc = 1

    if rc:
        print("[!] stdlib-identity-stubs: NOT OK.", file=sys.stderr)
    else:
        print("[+] stdlib-identity-stubs: OK — %d known stub(s), none new; %d still "
              "UNADJUDICATED (ceiling %d)." % (len(baseline), len(unadj),
                                               MAX_UNADJUDICATED))
    return rc


if __name__ == "__main__":
    sys.exit(main())
