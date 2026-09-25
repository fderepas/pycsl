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

THE POST-STATE AXIS (gen #31). Every clause above is about `\result`. A method that
returns nothing and promises `#@ ensures self._balance == \old(self._balance) + amount`
was outside this oracle's population on BOTH counts — no `\result` clause to read, and
`\old` in the skip list. It is checkable here in a way it is checkable nowhere else in the
battery, because this oracle CONSTRUCTS the pre-state: build the object, SNAPSHOT its
fields, call the method, evaluate the clause against the snapshot. Thirty-two such claims
exist in the PASS-expected corpus, twenty-one of them using `\old`; 31 methods and 96
clause evaluations run, 0 FALSE. A FRESH object is built for every argument tuple —
`\old` names the state before THIS call, and reusing one instance would make the second
tuple's pre-state the first tuple's writes.

The widening was aimed at 32 claims it could newly CHECK. What it found was a file it
could newly RUN: `0554.py::Service.tick` raises `AttributeError` on every call, because
`#@ compose_from` flattens the provider IN THE VERIFIER and CPython's MRO does not.
See NEVER_RETURNS below and
`getting-better/open-routes/finding-a-contract-over-a-function-that-never-returns.md`.

THE RATCHETS: any non-inherited DISAGREE fails; any post-state clause FALSE fails; an
UNNAMED function with no normal exit on any admitted argument fails; the trust-inherited
count may not grow;
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
SKIP_TOKENS = ("\\forall", "\\exists", "\\old", "\\at", "\\separated",
               "\\valid", "\\sum", "\\is_sorted", "\\permutation", "\\array_eq",
               "==>", "\\result[", "\\nothing", "\\let")
# (#49) gen #31 — `\length` LEAVES the skip list and is TRANSLATED instead:
# `\length(x)` is `len(x)`, exactly as `check-class-invariant-establishment`
# does it. A token belongs in a list called "cannot evaluate" only while it
# really cannot be evaluated.
# (#49) gen #31 — `\old` LEAVES the skip list for the POST-STATE axis only, and for a
# measured reason: this oracle CONSTRUCTS the pre-state, so `\old` is the one token it is
# in a better position to evaluate than the prover. A census of the `\result ==` population
# found ZERO functions excluded by `\old` — every instance of it in the corpus is a claim
# about a FIELD after a method call, which is a different axis and the one below.
SKIP_TOKENS_POST = tuple(t for t in SKIP_TOKENS if t != "\\old")
POOL = [0, 1, 2, 3, 5, -1, -2, 7]
_CTOR = {}               # (class, method) -> (ctor arg names, tags, `__init__` requires)
SKIPPED = {}             # exclusion reason -> [(file, function)], filled by collect()
# (#49) gen #31 — the `str`/`bytes` pools. Deterministic and small: four
# values each, chosen to include the empty one, a single character, and the
# FOUR-byte value `0779`'s `#@ requires \length(d) == 4` admits.
STR_POOL = ["", "a", "abcd", "xyz"]
BYTES_POOL = [b"", b"a", b"abcd", b"xyz"]
# (#49) gen #31 — THE LIST POOLS. The census put `list`/`List[...]` parameters at 145
# functions, the largest group left outside this oracle after the predicate axis. Three
# values each: the EMPTY one (where `\length(x) == 0` and every indexing precondition
# bites), a singleton, and a three-element list long enough for an index-2 read.
#
# EVERY CALL GETS A FRESH COPY (`_materialise` below). A corpus function is free to mutate
# its list argument, and a shared pool object would carry the first tuple's mutation into
# the second — the same hazard the post-state axis solves by rebuilding the object, and the
# same wrong answer: the oracle would report a disagreement it had caused itself.
LIST_POOL_INT = [[], [0], [1, 2, 3]]
LIST_POOL_STR = [[], ["a"], ["a", "b", "c"]]
# (#49) gen #31 — sets and dicts, the same shape of pool and the same mutation rule.
SET_POOL_INT = [set(), {0}, {1, 2, 3}]
DICT_POOL_SI = [{}, {"a": 1}, {"a": 1, "b": 2}]
DICT_POOL_II = [{}, {0: 1}, {0: 1, 1: 2}]
MAX_TUPLES = 40          # per function, deterministic prefix of the product
CALL_TIMEOUT = 1.0       # seconds; a corpus loop must not hang the battery
EXEC_TIMEOUT = 2.0
MIN_EVALS = 7300         # 7642 with the set/dict pools; 7578 once the translator was unified and the
                         # disjunction mis-parse repaired; 7392 with the
                         # CONSTRUCTOR-ARGUMENT axis; 7239 with the
                         # LIST-PARAMETER axis; 7063 with the PREDICATE axis (`#@ ensures` clauses over
                         # `\result` that are not equalities — the census found the
                         # inequality family to be the largest evaluable group this oracle
                         # was skipping). Was 6114 with the POST-STATE axis, 5750 with the METHOD
                         # population AND the skip list narrowed
                         # to the clauses actually evaluated (4340 at the first
                         # measurement, functions only, `\nothing` excluding every
                         # empty-frame function). Roughly the same relative margin the
                         # original floor had. Both corpora only grow.
TRUST_INHERITED_BASELINE = 14    # disagreements a caller INHERITS from a trusted callee

# (#49) gen #31 — KNOWN DIVERGENCES, each with its reason and its record. Surfaced when the
# skip list stopped being applied to `#@ assigns` (see `_reqs0` below): `\nothing` had been
# excluding every function with an empty frame, and these five were inside that population.
#
# `struct.unpack` RETURNS A TUPLE — "The result is a tuple even if it contains exactly one
# item", quoted from the RST in `src/pycsl_lib/strct/__init__.py`'s own docstring — and the
# model returns the unpacked SCALAR. So `#@ ensures \result == x` is certified for a
# function whose CPython answer is `(x,)`. Both files are `# pycsl-expected: PASS` and carry
# `#@ proof rocq` + `#@ proof lean` citations; DELETING the citations makes 0753 FAIL, so
# the discharge comes from the audited external proof, not from ordinary verification. The
# registered axiom is a TRUE theorem about a byte codec returning an int — what is wrong is
# the ATTRIBUTION, and nothing in the 3-way cross-check compares the Rocq result TYPE with
# the Python return type.
#
# `getting-better/open-routes/finding-struct-unpack-returns-a-tuple.md`
KNOWN_DIVERGENT = {
    ("0753.py", "roundtrip_u16"): "struct.unpack returns a tuple; discharged by `#@ proof`",
    ("0753.py", "roundtrip_u32"): "struct.unpack returns a tuple; discharged by `#@ proof`",
    ("0778.py", "roundtrip_i16"): "struct.unpack returns a tuple; discharged by `#@ proof`",
    ("0778.py", "roundtrip_i32"): "struct.unpack returns a tuple; discharged by `#@ proof`",
    ("0778.py", "roundtrip_i64"): "struct.unpack returns a tuple; discharged by `#@ proof`",
    # (#49) gen #31 — reachable only after the `str`/`bytes` pools, the `\length`
    # translation and the non-int `\result` landed together. `roundtrip_s4(d: bytes)`
    # is the same defect one type over: CPython answers `(b'abcd',)`.
    ("0779.py", "roundtrip_s4"): "struct.unpack returns a tuple; discharged by `#@ proof`",
}
# (#49) gen #31 — NO NORMAL EXIT ON ANY ADMITTED ARGUMENT. A contract over a function that
# always raises is VACUOUSLY true: the `#@ ensures` constrains a normal exit the function
# does not have, so the prover discharges it and the claim says nothing about any run. This
# is a strictly sharper defect than "raises on SOME argument" (0420, 1302), and separating
# the two is the whole reason the tuple loop stopped breaking on the first raise.
#
# `check-claim-vacuity.py` is the instrument that should have found these and could not:
# its population is CLAUSES that are trivially true, and each of these clauses is a
# perfectly contentful `\result == k`. The vacuity is in the FUNCTION's reachability, one
# level below where that instrument looks. Wall-lesson (v5).
NEVER_RETURNS = {
    ("0496.py", "grab"):
        "`Holder.__new__(cls)` takes no extra argument while `__init__(self, n)` does, so "
        "CPython's `Holder(k)` raises `TypeError: __new__() takes 1 positional argument but "
        "2 were given` — for EVERY k. The model builds `{x = k}` from `__init__` and never "
        "compares `__new__`'s arity with the construction site, so `\\result == k` verifies "
        "for a function with no run at all. `__new__` IS an analysed surface (UB-7.6 "
        "rejects a non-trivial one), which is what makes the missing dimension a defect "
        "rather than a boundary. `finding-a-contract-over-a-function-that-never-returns.md`",
    ("0554.py", "Service.tick"):
        "`#@ compose_from Counter` flattens `bump` into `Service` IN THE VERIFIER; CPython "
        "does not, because `Service` does not inherit `Counter` — `self.bump()` is an "
        "`AttributeError` on every call. Measured across the corpus: ALL ELEVEN composing "
        "classes compose a provider they do not inherit, and in ten of the eleven the "
        "provided name is absent from the instance at runtime. "
        "`finding-a-contract-over-a-function-that-never-returns.md`",
    # (#49) gen #31 — FOUND BY THE PREDICATE AXIS, which widened the population from
    # `#@ ensures \\result == <expr>` to any predicate over `\\result`. Every one of these
    # carries `#@ ensures \\result >= 0` or a `\\str_length` bound — contentful clauses, all
    # of them discharged over a function with no run.
    ("0549.py", "Facade.run"):
        "THE FLAGSHIP. Same defect as 0554: `#@ compose_from CoreEmit, MapOps` flattens the "
        "providers in the VERIFIER, `Facade`'s MRO is `[Facade, object]`, and "
        "`Facade().run(3)` is an `AttributeError`. `1902` is this file made executable and "
        "it verifies. "
        "`finding-a-contract-over-a-function-that-never-returns.md`",
    ("1858_gen31_compose_from_marked_class_verifies.py", "Facade.run"):
        "The gen #31 `#@ mixin`-marker control, same shape as 0549. Kept as written "
        "deliberately: it is the CONTROL for a refusal about the MARKER, and rewriting it "
        "to inherit would change what it controls. "
        "`finding-a-contract-over-a-function-that-never-returns.md`",
    ("0540.py", "use_str"):
        "`#@ datatype Option[T] = Nothing | Just(T)` introduces CONSTRUCTORS with no Python "
        "definition, and the body uses them in EXECUTABLE position — `o = Just(s)` then a "
        "`match`. CPython answers `NameError: name 'Just' is not defined` for every s. The "
        "second directive found this generation whose names have no runtime counterpart; "
        "`#@ compose_from` was the first. "
        "`finding-a-verified-program-that-is-not-the-executed-program.md`",
    ("1003_parametric_datatype_faithful.py", "use_str"):
        "The parametric twin of 0540, same mechanism: `Just`/`Nothing` exist only in the "
        "annotation world. `use_int` in the same file raises identically and is outside "
        "this oracle's population only because it takes no argument. "
        "`finding-a-verified-program-that-is-not-the-executed-program.md`",
    ("0746.py", "Registry.arity"):
        "A `@dataclass` field declared `formal_params: Dict[str, List[str]] = None`. The "
        "ANNOTATION and the DEFAULT disagree — a type checker rejects it without "
        "`Optional` — and PyCSL models the field by the annotation, so `arity` proves "
        "`\\result >= 0` over a map while `Registry().arity(name)` is "
        "`AttributeError: 'NoneType' object has no attribute 'get'`. The file's own "
        "`__main__` block assigns `r.formal_params = {}` before calling, which is the "
        "author working around it by hand. "
        "`finding-a-verified-program-that-is-not-the-executed-program.md`",
    ("0453.py", "FunctionAnalyzer.visit_FunctionDef"):
        "THE INT PLACEHOLDER, measured. `def visit_FunctionDef(self, node: int) -> int` "
        "over a body that calls `node.name.islower()`. `int` is what PyCSL models an AST "
        "node as, so the DECLARED SIGNATURE is unsatisfiable: no int has `.name`, and every "
        "call raises `AttributeError`. This is the conversion track's named #1 blocker "
        "sitting in a green corpus driver — the annotation is not a description of the "
        "argument, it is a placeholder for a type the modeller does not have. "
        "`finding-a-verified-program-that-is-not-the-executed-program.md`",
}
MAX_RAISED = 15                  # FUNCTIONS with at least one call that RAISES on an
                                 # argument their own precondition admits. (#49) gen #31:
                                 # the ratchet counts FUNCTIONS, not raise EVENTS. Once the
                                 # tuple loop stopped breaking on the first raise (so that
                                 # `NEVER_RETURNS` could be told apart from an
                                 # input-dependent raise) the event count became a function
                                 # of the SAMPLING — up to three per function — and a
                                 # ratchet whose number moves when nothing about the corpus
                                 # moved is a ratchet that will be raised without thought.
                                 # Fifteen today: the eight in NEVER_RETURNS, the three
                                 # declared `#@ \diverges` (0051, 0158, 0159), and the
                                 # four input-dependent ones — 0420, 1302, 0199 and 0605.
                                 #
                                 # 0199: `sum_first_two(d: dict)` under
                                 # `#@ ensures \result == d[0] + d[1]` and no `#@ requires`.
                                 # PyCSL models a dict as a TOTAL `map int (option int)` in
                                 # which a missing key reads as 0 — the driver's own
                                 # docstring says so — and a PYTHON DICT IS NOT TOTAL:
                                 # `d[0]` on a dict without key 0 is a KeyError. The model
                                 # asserts a normal exit with a value where CPython has
                                 # none, which is the 0420 shape one container over.
                                 # `finding-a-verified-program-that-is-not-the-executed-program.md`
                                 #
                                 # 0605, whose
                                 # `dig(s, i)` reads `s[i]` under
                                 # `#@ ensures \result == 1 or \result == 0` and NO
                                 # `#@ requires` bounding `i`, so `dig("", 0)` is an
                                 # IndexError on an argument the contract admits. It
                                 # arrived with the disjunction repair: the clause matched
                                 # the equality regex, captured `1 or \result == 0` as a
                                 # right-hand side, and the function had been outside the
                                 # population entirely.
                                 # (#49) gen #31: 3 -> 4 with the widened population. The one
                                 # added is `1302_route108…::wrapper(-1)`, whose `else` branch
                                 # calls a raising callee — route #108 established that the
                                 # raise really does escape, and an `#@ ensures` constrains the
                                 # NORMAL exit only, so the contract is not broken. 0383, which
                                 # the widening also surfaced, is NOT here: it DECLARES
                                 # `#@ raises ZeroDivisionError when n == 0`, and the oracle now
                                 # reads that clause instead of reporting the declared exit.
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


# (#49) gen #31 — (function, parameter) -> the pool its ANNOTATION selects. A module
# global because `collect` builds it and `main` consumes it, exactly like `per`.
PARAM_POOL = {}


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
        # (#49) gen #31 — THE METHOD POPULATION. `defs` is every FunctionDef in the file,
        # so a method arrives here with `self` as its first parameter and the old filter
        # dropped it. A method of a class that `C()` constructs is runnable: build the
        # object, then call it with the same pool. `_owner_of` is the class whose body
        # holds the def, or None for a module-level function; a class whose `__init__`
        # NEEDS an argument has no canonical instance and is skipped, exactly as the
        # zero-argument sibling skips it.
        _owner = {}
        _CTOR.clear()          # per FILE: class names repeat across the corpus
        _mixin_lines = {_ln for _ln, _cs in
                        ((i + 1, l.strip()) for i, l in enumerate(lines))
                        if _cs.startswith("#@") and re.match(r"#@\s*mixin\b", _cs)}
        for _c in ast.walk(tree):
            if not isinstance(_c, ast.ClassDef):
                continue
            # (#49) gen #31 — A `#@ mixin` CLASS IS NOT CONSTRUCTIBLE, and the ORACLE has
            # to honour the same rule the language does. `PYCSL-SEM-MIXIN-INSTANTIATED`
            # (witness 1861) refuses `M()` because a mixin's methods are verified against
            # the COMPOSER's record, so a direct construction produces an object whose own
            # methods were never proved over it. Building one here produced exactly the
            # object that rule describes: `MapOps().handle_get(k)` calls `self.emit`, which
            # a bare `MapOps` does not have, and the oracle reported the AttributeError as
            # a corpus defect. It is an ORACLE defect — the population must exclude what
            # the language forbids. Found by the predicate axis in the same run that found
            # three real ones.
            _cann_i = _c.lineno - 2
            _is_mixin = False
            while _cann_i >= 0 and (not lines[_cann_i].strip()
                                    or lines[_cann_i].strip().startswith("#")):
                if re.match(r"#@\s*mixin\b", lines[_cann_i].strip()):
                    _is_mixin = True
                _cann_i -= 1
            if _is_mixin:
                continue
            # (#49) gen #31 — THE CONSTRUCTOR-ARGUMENT AXIS. A class whose `__init__` takes
            # arguments used to have no canonical instance and was dropped whole; the
            # census counted 67 methods behind that one filter, the last large group after
            # the predicate and list axes. They are constructible the same way everything
            # else here is: from the pools, filtered by `__init__`'s OWN `#@ requires`.
            # The constructor arguments become the LEADING elements of the argument tuple,
            # so `MAX_TUPLES` still bounds the product and the whole thing stays
            # deterministic.
            _ini = next((x for x in _c.body
                         if isinstance(x, ast.FunctionDef) and x.name == "__init__"), None)
            _cargs, _ctags, _creqs = [], [], []
            if _ini is not None:
                _ips = (_ini.args.posonlyargs + _ini.args.args)[1:]
                _need = len(_ips) - len(_ini.args.defaults)
                if _ini.args.kwonlyargs or _ini.args.vararg or _ini.args.kwarg:
                    continue
                if _need > 0:
                    if len(_ips) > 2:
                        continue        # the product would swamp MAX_TUPLES
                    _ctags = [_ann_tag(a.annotation) for a in _ips]
                    if any(t is None or t.startswith(("list:", "set:", "dict:"))
                           for t in _ctags):
                        continue        # a mutable constructor argument: same hole as above
                    _cargs = [a.arg for a in _ips]
                    _ci = _ini.lineno - 2
                    while _ci >= 0 and (not lines[_ci].strip()
                                        or lines[_ci].strip().startswith("#")):
                        _mq = re.match(r"#@\s*requires\s+(.+)$", lines[_ci].strip())
                        if _mq:
                            _creqs.append(_mq.group(1).strip())
                        _ci -= 1
                    if any(t in " ".join(_creqs) for t in SKIP_TOKENS) \
                            or any("\\" in _py(x) for x in _creqs):
                        continue
            for _m in _c.body:
                if isinstance(_m, ast.FunctionDef):
                    _owner[_m.name] = _c.name
                    _CTOR[(_c.name, _m.name)] = (_cargs, _ctags, _creqs)
        for name, node in defs.items():
            # (#49) gen #31 — EVERY EXCLUSION NAMES ITS REASON. Wall-lesson (y5): a census
            # of this oracle's own boundary came back with 206 functions in a bucket
            # labelled "other", and that bucket held three defects in the instrument. A
            # remainder in a census is the finding, not the rounding — so the reasons are
            # recorded here, at the `continue` that causes them, where they cannot drift
            # from the code the way a separate re-implementation would.
            def _skip(_why, _f=f, _n=name):
                SKIPPED.setdefault(_why, []).append((os.path.basename(_f), _n))
            ps = node.args.args
            _cls = _owner.get(name)
            if _cls is not None and ps and ps[0].arg == "self":
                ps = ps[1:]
                if name.startswith("__"):
                    _skip('dunder method')
                    continue
            elif any(a.arg == "self" for a in ps):
                _skip('a `self` parameter outside a class the oracle can construct')
                continue
            if len(ps) > 3:
                _skip('more than 3 parameters')
                continue
            _post_probe = any(re.match(r"#@\s*ensures\s+self\.\w+\s*==", a)
                              for a in annotations_of(node))
            # (#49) gen #31 — a zero-argument METHOD of a class whose `__init__` TAKES
            # arguments is not the sibling oracle's population either: that oracle's
            # instances are `C()`, and this class has none. The tuple is non-empty from the
            # constructor side, so the method is runnable here and nowhere else — which is
            # most of what the constructor axis actually buys.
            _ctor_probe = bool(_CTOR.get((_cls, name), ([], [], []))[0])
            if not ps and not (_cls is not None and (_post_probe or _ctor_probe)):
                _skip('zero-argument: the SIBLING oracle `check-corpus-contract-truth` owns it')
                continue       # a zero-argument function is the SIBLING oracle's population

            # (#49) gen #31 — `str` and `bytes` parameters join `int`/`bool`, and the
            # RETURN annotation is no longer restricted: `\result == d` is an ordinary
            # Python `==` whatever `d` is, and a comparison the oracle cannot make simply
            # raises and is counted.
            _tags = [_ann_tag(a.annotation) for a in ps]
            if any(t is None for t in _tags):
                _skip('parameter type with no pool (Any, Expr, Set, Dict, a record, a nested list)')
                continue
            # (#49) gen #31 — A FUNCTION THAT MUTATES A LIST ARGUMENT IS OUT OF THE
            # POPULATION, and this is an honesty exclusion, not a convenience. For a
            # SCALAR parameter the question does not arise: `int`, `bool`, `str` and
            # `bytes` are immutable, so the name in an `#@ ensures` denotes the argument
            # whatever the body does to its own binding. A `List[T]` is passed as a WhyML
            # `array T`, which is mutable and shared, and whether a bare `xs` in the
            # postcondition means the pre- or post-state array is a question about PyCSL's
            # lowering that this oracle must not GUESS at — guessing gives a disagreement
            # the oracle itself caused, which is the worst thing a truth oracle can print.
            #
            # Measured on a constructed probe: `xs.append(0); return len(xs)` under
            # `#@ ensures \result == \length(xs) + 1` is reported FALSE if `xs` is read
            # after the call and TRUE if it is read before. Both readings are defensible;
            # only one can be right; neither is worth asserting here. ZERO corpus functions
            # in the population mutate a list argument, so this filter costs nothing today
            # and closes the hole before a driver walks into it.
            _listy = {a.arg for a, t in zip(ps, _tags)
                      if t.startswith(("list:", "set:", "dict:"))}
            if _listy:
                _MUT = ("append", "insert", "pop", "extend", "clear", "remove",
                        "sort", "reverse", "__setitem__",
                        "add", "discard", "update", "setdefault", "popitem",
                        "difference_update", "intersection_update",
                        "symmetric_difference_update")
                _mutates = False
                for _n_mu in ast.walk(node):
                    if (isinstance(_n_mu, ast.Call)
                            and isinstance(_n_mu.func, ast.Attribute)
                            and _n_mu.func.attr in _MUT
                            and isinstance(_n_mu.func.value, ast.Name)
                            and _n_mu.func.value.id in _listy):
                        _mutates = True
                    if isinstance(_n_mu, (ast.Assign, ast.AugAssign, ast.Delete)):
                        _tg = (_n_mu.targets if isinstance(_n_mu, ast.Assign)
                               else [_n_mu.target] if isinstance(_n_mu, ast.AugAssign)
                               else _n_mu.targets)
                        for _t_mu in _tg:
                            _base = _t_mu
                            while isinstance(_base, (ast.Subscript, ast.Attribute)):
                                _base = _base.value
                            if isinstance(_base, ast.Name) and _base.id in _listy:
                                _mutates = True
                if _mutates:
                    _skip("mutates a list argument: the pre/post reading of `xs` is not this oracle's to pick")
                    continue
            # A post-state method typically returns `None`; the return annotation only
            # has to be readable when a `\result` clause is actually evaluated.
            if _ann_tag(node.returns) is None \
                    and not (_cls is not None and _post_probe):
                _skip('return type with no pool and no post-state clause to read')
                continue
            ann = annotations_of(node)
            # (#49) gen #31 — `#@ ensures \result == 0 or \result == 1` MATCHES the
            # equality regex and captures `0 or \result == 1` as a right-hand side. That
            # is not a right-hand side, it is the rest of a DISJUNCTION, and the captured
            # text then failed the backslash guard and took the whole function out of the
            # population — 37 of them. A clause whose captured RHS still mentions `\result`
            # is a predicate; it goes to the predicate axis, where it evaluates correctly.
            ens = [m.group(1).strip() for m in
                   (re.match(r"#@\s*ensures\s+\\result\s*==\s*(.+)$", a) for a in ann) if m]
            ens = [x for x in ens if "\\result" not in x]
            # (#49) gen #31 — THE POST-STATE AXIS. Until now every clause this oracle read
            # was about `\result`, so a method that returns nothing and promises
            # `self._balance == \old(self._balance) + amount` was outside the population on
            # BOTH counts — no `\result` clause, and `\old` in the skip list. Thirty-two
            # such claims exist in the PASS-expected corpus, twenty-one of them using
            # `\old`. They are checkable here in a way they are not checkable anywhere
            # else in the battery: construct the object, SNAPSHOT its fields, call the
            # method, evaluate the clause against the snapshot.
            post = [m.group(1).strip() for m in
                    (re.match(r"#@\s*ensures\s+(self\.\w+\s*==.+)$", a) for a in ann) if m]
            # (#49) gen #31 — THE PREDICATE AXIS. Every `#@ ensures` mentioning `\result`
            # that is NOT the `\result == <expr>` shape already harvested above: an
            # inequality, a conjunction, a bound. Evaluated as a predicate with `\result`
            # bound to CPython's answer, exactly as the post-state clauses are.
            preds = [m.group(1).strip() for m in
                     (re.match(r"#@\s*ensures\s+(.+)$", a) for a in ann) if m]
            preds = [x for x in preds
                     if "\\result" in x
                     and not (re.match(r"\\result\s*==", x)
                              and "\\result" not in x[x.index("==") + 2:])
                     and not re.match(r"self\.\w+\s*==", x)]
            if post and _cls is None:
                post = []          # `self.f` outside a class is not a post-state claim
            if not ens and not post and not preds:
                _skip('no clause this oracle reads (`\\result ==`, a `\\result` predicate, or `self.f ==`)')
                continue
            # (#49) gen #31 — THE SKIP LIST APPLIES TO THE CLAUSES THIS ORACLE READS, which
            # are `requires` and `ensures`, NOT to the whole annotation block. `\nothing`
            # can only ever appear in `#@ assigns \nothing`, so testing the joined block
            # against it excluded every function with an empty frame — 102 functions and
            # 1206 evaluations, and five real disagreements among them. The list's own
            # comment says "tokens this oracle cannot evaluate"; a token that cannot appear
            # in what is evaluated does not belong to that set. Wall-lesson (o5).
            _reqs0 = [m.group(1).strip() for m in
                      (re.match(r"#@\s*requires\s+(.+)$", a) for a in ann) if m]
            if ens and any(t in " ".join(_reqs0 + ens) for t in SKIP_TOKENS):
                _skip('a skip token in the clauses read')
                continue
            if post and any(t in " ".join(_reqs0 + post) for t in SKIP_TOKENS_POST):
                post = []
            if preds and any(t in " ".join(_reqs0 + preds) for t in SKIP_TOKENS):
                preds = []
            if not ens and not post and not preds:
                _skip('a skip token in the clauses read')
                continue
            # A name REBOUND at module level (`inc = dec`, route #119's witness library) is
            # not the function whose contract was just read — `ns[name]` would be the other
            # one, and the oracle would report the mismatch as a corpus defect. Skip it: a
            # correctness fix, not an exclusion.
            if any(isinstance(_st, ast.Assign)
                   and any(isinstance(_t, ast.Name) and _t.id == name
                           for _t in _st.targets)
                   for _st in tree.body):
                _skip('the name is REBOUND at module level; `ns[name]` is not this function')
                continue
            if any(re.match(r"#@\s*(act|behavior)\b", a) or re.match(r"#@\s+given\b", a)
                   for a in ann):
                stats["acts"] += 1
                _skip('behaviour block (`#@ act` / `given`): the postcondition is GUARDED')
                continue
            if any(isinstance(_c_ex, ast.Call) and isinstance(_c_ex.func, ast.Name)
                   and _c_ex.func.id in ("exec", "eval")
                   for _c_ex in ast.walk(node)):
                _skip('the body calls `exec`/`eval`')
                continue
            if name in trusted:
                stats["trusted"] += 1
                if not no_exclusions:
                    _skip('`\\trusted`: the contract is assumed, not proven')
                    continue
            if name not in verified and not no_exclusions:
                _skip("outside the file's `# pycsl-flags: --fun` restriction")
                continue
            reqs = [m.group(1).strip() for m in
                    (re.match(r"#@\s*requires\s+(.+)$", a) for a in ann) if m]
            if any("\\" in re.sub(r"\\length\(", "len(", x) for x in reqs + ens):
                _skip('a backslash token the translator cannot render as Python')
                continue
            if any("\\" in _post_py(x) for x in post):
                post = []
            if any("\\" in _pred_py(x) for x in preds):
                preds = []
            if not ens and not post and not preds:
                _skip('a skip token in the clauses read')
                continue
            # (#49) gen #31 — `#@ \diverges` is READ, not listed. A function promised not
            # to return is the one shape where having no normal exit IS the contract, and
            # the directive says so on the function itself; naming each such function in a
            # table would be recording what the source already states.
            _diverges = any(re.match(r"#@\s*\\diverges\b", a) for a in ann)
            _raises_when = [m.group(1).strip() for m in
                            (re.match(r"#@\s*raises\s+\w+\s+when\s+(.+)$", a)
                             for a in ann) if m]
            _cargs, _ctags, _creqs = _CTOR.get((_cls, name), ([], [], []))
            for _c_nm, _c_tg in zip(_cargs, _ctags):
                PARAM_POOL[(name, "\x00ctor\x00" + _c_nm)] = {
                    "str": STR_POOL, "bytes": BYTES_POOL}.get(_c_tg, POOL)
            for _a_pp, _tag in zip(ps, _tags):
                PARAM_POOL[(name, _a_pp.arg)] = {
                    "str": STR_POOL, "bytes": BYTES_POOL,
                    "list:int": LIST_POOL_INT, "list:str": LIST_POOL_STR,
                    "set:int": SET_POOL_INT,
                    "dict:si": DICT_POOL_SI, "dict:ii": DICT_POOL_II}.get(_tag, POOL)
            per.setdefault(f, []).append(
                (name, [a.arg for a in ps], ens, reqs, bool(reach(name) & trusted),
                 _cls, _raises_when, post, preds, _diverges,
                 (_cargs, _creqs)))
    return per, stats


class _CtorLater(Exception):
    """Internal: the instance is built per argument tuple, not once per function."""


def _ann_tag(a):
    r"""The pool tag for a parameter annotation, or None if this oracle has no values for it.

    `int` / `bool` / `str` / `bytes` are the scalar pools. `list`, `List`, `List[int]`,
    `List[bool]` and `List[str]` are the list ones — `List[str]` gets strings, everything
    else gets ints, because a list of ints is what `\length`, indexing and summation
    clauses are written over. A parameterised list of anything else (records, nested lists)
    returns None and the function stays out of the population.
    """
    if isinstance(a, ast.Name):
        if a.id in ("int", "bool", "str", "bytes"):
            return a.id
        if a.id in ("list", "List"):
            return "list:int"
        if a.id in ("set", "Set"):
            return "set:int"
        if a.id in ("dict", "Dict"):
            # (#49) gen #31 — a BARE `dict` gets the INT-KEYED pool, because that is the
            # model: `0199.py`'s own docstring says a dict parameter is "modelled as a
            # total `map int (option int)` (a missing key reads as 0)". Handing it
            # string keys would test a program the model does not describe.
            return "dict:ii"
        return None
    if isinstance(a, ast.Subscript) and isinstance(a.value, ast.Name):
        _c = a.value.id
        _el = a.slice
        if _c in ("list", "List"):
            if isinstance(_el, ast.Name) and _el.id in ("int", "bool", "str"):
                return "list:str" if _el.id == "str" else "list:int"
        elif _c in ("set", "Set"):
            if isinstance(_el, ast.Name) and _el.id in ("int", "bool"):
                return "set:int"
        elif _c in ("dict", "Dict") and isinstance(_el, ast.Tuple) \
                and len(_el.elts) == 2 \
                and all(isinstance(x, ast.Name) for x in _el.elts):
            _k, _v = _el.elts[0].id, _el.elts[1].id
            if _v in ("int", "bool"):
                if _k == "str":
                    return "dict:si"
                if _k in ("int", "bool"):
                    return "dict:ii"
    return None


def _materialise(v):
    """A fresh copy of a pool value for THIS call. Scalars are immutable and pass through;
    a list is copied, because a corpus function may mutate its argument and the pool must
    not carry that into the next tuple."""
    if isinstance(v, list):
        return list(v)
    if isinstance(v, set):
        return set(v)
    if isinstance(v, dict):
        return dict(v)
    return v


def _py(expr):
    r"""The CSL-to-Python translation every clause here goes through.

    (#49) gen #31 — `\str_length` and `\str_sub` join `\length`. They were translated on
    the `\result`-predicate path and NOT on the `#@ requires` path, so a function whose
    postcondition the oracle could read was dropped because its PRECONDITION mentioned the
    same token — 22 functions, every one of them a string driver (0482-0492). A clause
    language needs ONE translator, not one per axis; two translators is how a token ends up
    evaluable in one position and untranslatable in the position next to it.
    """
    out = re.sub(r"\\length\(", "len(", expr)
    out = re.sub(r"\\str_length\(", "len(", out)
    out = re.sub(r"\\str_sub\(([^,()]+),\s*([^,]+?),\s*(.+?)\)\s*$", r"(\1)[(\2):(\3)]", out)
    out = re.sub(r"\\str_sub\(([^,()]+),\s*([^,]+?),\s*([^,()]+)\)", r"(\1)[(\2):(\3)]", out)
    return out.replace("&&", " and ").replace("||", " or ")


def _pred_py(expr):
    r"""An `#@ ensures` clause that is a PREDICATE over `\result`, in Python.

    The oracle's original population was `#@ ensures \result == <expr>`, which it checks by
    comparing CPython's answer with the right-hand side. That shape is the sharpest one but
    it is not the only evaluable one: `\result >= 0` is an ordinary Python comparison once
    `\result` has a value, and the CENSUS says the inequality family is the single largest
    group of `#@ ensures` clauses this oracle could evaluate and did not — 102 clauses of
    `\result >= 0` alone, and a long tail of `>= x`, `> 0`, `>= 1`, `>= 5`.

    `\result` binds to `_RES`; `\str_length` joins `\length` as `len`, for the same reason
    `\length` left the skip list in gen #31 — a token belongs in a list called "cannot
    evaluate" only while it really cannot be evaluated.
    """
    return _py(re.sub(r"\\result\b", "_RES", expr))


def _post_py(expr):
    r"""A post-state clause, in Python, against a snapshot taken before the call.

    `\old(self.F)` becomes `_OLD["F"]` — the field as it was, which is exactly what this
    oracle holds and the reason `\old` is evaluable here. A REMAINING `\old(` can only
    wrap a parameter, and every parameter in this population is annotated `int`, `bool`,
    `str` or `bytes` — all IMMUTABLE, and bound in the evaluation namespace to the
    ARGUMENT, which IS the pre-state value whatever the body rebinds. So it drops to
    parentheses. Anything else still carries a backslash and is rejected by the caller.
    """
    return _py(re.sub(r"\\old\(", "(",
                      re.sub(r"\\old\(\s*self\.(\w+)\s*\)", r'_OLD["\1"]', expr)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verbose", action="store_true")
    ap.add_argument("--census", action="store_true",
                    help="print this oracle's OWN BOUNDARY: every function it skipped and "
                         "the named reason, counted. Wall-lesson (y5) — a census is only "
                         "as honest as its smallest labelled bucket, so there is no "
                         "'other': each exclusion is recorded at the `continue` that "
                         "causes it. Read it before believing a green run means coverage.")
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
    if args.census:
        _tot = sum(len(v) for v in SKIPPED.values())
        _inpop = sum(len(v) for v in per.values())
        print("[*] corpus-contract-truth-args CENSUS — %d function(s) IN the population, "
              "%d skipped, every one with a named reason:" % (_inpop, _tot))
        for _why, _fns in sorted(SKIPPED.items(), key=lambda kv: -len(kv[1])):
            print("    %5d  %s" % (len(_fns), _why))
            print("           e.g. %s" % (", ".join("%s::%s" % x for x in _fns[:3]),))
        print("[*] There is no 'other' row by construction: every `continue` in collect() "
              "records its reason. If a row's mechanism is one you do not recognise, that "
              "row is the next widening — or the next bug.")
        return 0

    agree = 0
    disagree, inherited, unrunnable, raised = [], [], [], []
    funcs = 0
    posts = posts_disagree = 0        # post-state CLAUSE evaluations, reported separately
    post_funcs = set()
    never_returns = []                # admitted by its own `requires`, raised on EVERY one
    preds_n = preds_disagree = 0      # `#@ ensures` PREDICATES over `\result`
    pred_funcs = set()

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
                unrunnable += [(os.path.basename(f), it[0], type(exc).__name__)
                               for it in items]
                continue
            finally:
                signal.setitimer(signal.ITIMER_REAL, 0)
                if sys.path and sys.path[0] == d:
                    sys.path.pop(0)
            for (name, params, ens, reqs, inherits, cls, raises_when, post, preds,
                 diverges, ctor) in items:
                ctor_names, ctor_reqs = ctor
                funcs += 1
                if post:
                    post_funcs.add((os.path.basename(f), cls, name))
                if preds:
                    pred_funcs.add((os.path.basename(f), cls, name))
                _obj = None
                if cls is None:
                    fn = ns.get(name)
                else:
                    # Build ONE instance per method and bind the method on it. A class that
                    # cannot be constructed is reported, never silently dropped.
                    if ctor_names:
                        fn = None            # built per tuple, from the pools, below
                    try:
                        if ctor_names:
                            raise _CtorLater()
                        with contextlib.redirect_stdout(io.StringIO()), \
                             contextlib.redirect_stderr(io.StringIO()):
                            signal.setitimer(signal.ITIMER_REAL, CALL_TIMEOUT)
                            _obj = ns[cls]()
                            signal.setitimer(signal.ITIMER_REAL, 0)
                        fn = getattr(_obj, name)
                    except _CtorLater:
                        pass
                    except BaseException as exc:
                        signal.setitimer(signal.ITIMER_REAL, 0)
                        unrunnable.append((os.path.basename(f), cls + "." + name,
                                           type(exc).__name__))
                        continue
                if not ctor_names and not callable(fn):
                    unrunnable.append((os.path.basename(f), name, "not callable"))
                    continue
                tested = 0
                _admitted = _raised_here = 0
                _pools = ([PARAM_POOL.get((name, "\x00ctor\x00" + _p), POOL)
                           for _p in ctor_names]
                          + [PARAM_POOL.get((name, _p), POOL) for _p in params])
                for tup in itertools.product(*_pools):
                    if tested >= MAX_TUPLES:
                        break
                    tup = tuple(_materialise(v) for v in tup)
                    ctup, tup = tup[:len(ctor_names)], tup[len(ctor_names):]
                    if ctor_names:
                        # `__init__`'s OWN precondition filters the constructor arguments,
                        # exactly as the method's filters the method's. A constructor whose
                        # `#@ requires` refuses an argument was never promised anything
                        # about the object it would have built.
                        try:
                            _cenv = dict(zip(ctor_names, ctup))
                            if not all(eval(_py(r), dict(ns), dict(_cenv))
                                       for r in ctor_reqs):
                                continue
                        except Exception:
                            break
                        try:
                            signal.setitimer(signal.ITIMER_REAL, CALL_TIMEOUT)
                            with contextlib.redirect_stdout(io.StringIO()), \
                                 contextlib.redirect_stderr(io.StringIO()):
                                _obj = ns[cls](*ctup)
                            signal.setitimer(signal.ITIMER_REAL, 0)
                            fn = getattr(_obj, name)
                        except BaseException as exc:
                            signal.setitimer(signal.ITIMER_REAL, 0)
                            unrunnable.append((os.path.basename(f), cls + "." + name,
                                               type(exc).__name__))
                            break
                    env = dict(zip(params, tup))
                    # (#49) gen #31 — A FRESH OBJECT PER CALL for the post-state axis.
                    # `\old` names the state before THIS call; reusing one instance across
                    # the product would make the second tuple's pre-state the first
                    # tuple's writes, and `deposit` would look like it disagreed when the
                    # oracle was the thing that was wrong.
                    if post and not ctor_names:
                        try:
                            signal.setitimer(signal.ITIMER_REAL, CALL_TIMEOUT)
                            with contextlib.redirect_stdout(io.StringIO()), \
                                 contextlib.redirect_stderr(io.StringIO()):
                                _obj = ns[cls]()
                            signal.setitimer(signal.ITIMER_REAL, 0)
                            fn = getattr(_obj, name)
                        except BaseException as exc:
                            signal.setitimer(signal.ITIMER_REAL, 0)
                            unrunnable.append((os.path.basename(f), cls + "." + name,
                                               type(exc).__name__))
                            break
                    try:
                        if not all(eval(_py(r), dict(ns), dict(env, self=_obj))
                                   for r in reqs):
                            continue
                    except Exception:
                        break
                    # a DECLARED exceptional exit is not a broken promise
                    try:
                        if any(eval(_py(w), dict(ns), dict(env, self=_obj))
                               for w in raises_when):
                            continue
                    except Exception:
                        pass
                    _admitted += 1
                    _old_snap = dict(vars(_obj)) if (post and _obj is not None) else {}
                    try:
                        signal.setitimer(signal.ITIMER_REAL, CALL_TIMEOUT)
                        with contextlib.redirect_stdout(io.StringIO()), \
                             contextlib.redirect_stderr(io.StringIO()):
                            got = fn(*tup)
                        signal.setitimer(signal.ITIMER_REAL, 0)
                        claims = [eval(_py(e), dict(ns), dict(env, self=_obj))
                                  for e in ens]
                        pclaims = [eval(_post_py(e), dict(ns),
                                        dict(env, self=_obj, _OLD=_old_snap))
                                   for e in post]
                        rclaims = [eval(_pred_py(e), dict(ns),
                                        dict(env, self=_obj, _RES=got))
                                   for e in preds]
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
                        if _raised_here < 3:
                            raised.append((os.path.basename(f), name, tup,
                                           type(exc).__name__))
                        # (#49) gen #31 — KEEP GOING, up to three. The first version broke
                        # out here, and a `break` cannot tell "raises on THIS argument"
                        # from "has no normal exit on ANY argument its own precondition
                        # admits". The second is a different and sharper defect — a
                        # contract over a function that never returns is VACUOUSLY true
                        # and certifies nothing at all — so it gets its own bucket below.
                        # ... and it keeps going to the END of the sampled product, not
                        # to the third raise. (#49) gen #31, measured: `0605.py::dig(s, i)`
                        # reads `s[i]`, the pool's first eight tuples all carry `s = ""`,
                        # and a loop that stopped at the third raise never reached
                        # `("a", 0)` — where `dig` returns 0 perfectly well. It was
                        # reported as having NO NORMAL EXIT, which is exactly the false
                        # alarm this bucket exists to avoid. Only the first three raises
                        # are RECORDED (the report stays readable); the loop is bounded by
                        # MAX_TUPLES as it always was.
                        _raised_here += 1
                        continue
                    tested += 1
                    got = int(got) if isinstance(got, bool) else got
                    bad = None
                    for e_src, claim in zip(ens, claims):
                        claim = int(claim) if isinstance(claim, bool) else claim
                        if got != claim:
                            bad = (os.path.basename(f), name, tup, e_src, claim, got)
                            break
                    if bad is None:
                        for p_src, pclaim in zip(post, pclaims):
                            if pclaim is not True:
                                # the clause IS the comparison: it either held or it did not
                                bad = (os.path.basename(f), (cls or "") + "." + name, tup,
                                       p_src, pclaim, "post-state")
                                posts_disagree += 1
                                break
                        else:
                            posts += len(post)
                    if bad is None:
                        for r_src, rclaim in zip(preds, rclaims):
                            if rclaim is not True:
                                bad = (os.path.basename(f), (cls + "." if cls else "") + name,
                                       tup, r_src, got, "predicate")
                                preds_disagree += 1
                                break
                        else:
                            preds_n += len(preds)
                    if bad is None:
                        agree += 1
                    elif inherits:
                        inherited.append(bad)
                    else:
                        disagree.append(bad)
                if _admitted and not tested and not diverges:
                    never_returns.append((os.path.basename(f),
                                          (cls + "." if cls else "") + name, _admitted))

    share = stats["no_proof"] / float(stats["files"]) if stats["files"] else 0.0
    print("[*] corpus-contract-truth-args: %d function(s), %d argument-level "
          "evaluation(s) — %d AGREE, %d DISAGREE, %d inherited from a `\\trusted` "
          "callee, %d RAISED on an admitted argument, %d unrunnable."
          % (funcs, agree + len(disagree) + len(inherited), agree, len(disagree),
             len(inherited), len(raised), len(unrunnable)))
    _nr_bad = [r for r in never_returns if (r[0], r[1]) not in NEVER_RETURNS]
    print("[*] corpus-contract-truth-args: NO-NORMAL-EXIT — %d function(s) raised on EVERY "
          "argument their own `requires` admits, %d of them named in NEVER_RETURNS with a "
          "reason. A contract over such a function is vacuously true."
          % (len(never_returns), len(never_returns) - len(_nr_bad)))
    for _f, _n, _a in sorted(never_returns):
        print("      %-44s %s" % (_f + "::" + _n,
                                  NEVER_RETURNS.get((_f, _n), "*** UNNAMED ***")[:150]))
    print("[*] corpus-contract-truth-args: POST-STATE — %d method(s) promising "
          "`self.f == ...` after the call, %d clause evaluation(s) against a pre-call "
          "snapshot, %d FALSE. `\\old(self.f)` is read from the snapshot; a fresh object "
          "is built for every argument tuple."
          % (len(post_funcs), posts + posts_disagree, posts_disagree))
    print("[*] corpus-contract-truth-args: PREDICATES — %d function(s) whose `#@ ensures` "
          "is a predicate over `\\result` rather than an equality, %d clause evaluation(s), "
          "%d FALSE."
          % (len(pred_funcs), preds_n + preds_disagree, preds_disagree))
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
    _seen_known = set()
    for b in disagree:
        _key = (b[0], b[1])
        if _key in KNOWN_DIVERGENT and not args.selftest_no_exclusions:
            _seen_known.add(_key)
            continue
        if b[5] == "predicate":
            print("[!]   POSTCONDITION FALSE OF ITS OWN PROGRAM: %s::%s%r — `ensures %s` is "
                  "FALSE with `\\result` = %r. The file is expected to PASS and its "
                  "precondition admits that argument." % b[:5], file=sys.stderr)
        elif b[5] == "post-state":
            print("[!]   POST-STATE CLAIM FALSE OF ITS OWN PROGRAM: %s::%s%r — after the "
                  "call, `ensures %s` evaluates to %r against a snapshot taken before it. "
                  "The file is expected to PASS and its precondition admits that argument."
                  % b[:5], file=sys.stderr)
        else:
            print("[!]   CONTRACT FALSE OF ITS OWN PROGRAM: %s::%s%r — `ensures \\result == "
                  "%s` says %r, CPython answers %r. The file is expected to PASS and its "
                  "precondition admits that argument." % b, file=sys.stderr)
        rc = 1
    if not args.selftest_no_exclusions:
        _gone = set(KNOWN_DIVERGENT) - _seen_known
        if _gone:
            for _k in sorted(_gone):
                print("[!]   KNOWN DIVERGENCE NO LONGER REPRODUCES: %s::%s (%s). That is "
                      "GOOD NEWS that has to be RECORDED — remove it from KNOWN_DIVERGENT "
                      "in the same commit that fixed it."
                      % (_k[0], _k[1], KNOWN_DIVERGENT[_k]), file=sys.stderr)
            rc = 1
        elif _seen_known:
            print("[*] corpus-contract-truth-args: %d KNOWN divergence(s), each named in "
                  "KNOWN_DIVERGENT with its reason and its record "
                  "(`finding-struct-unpack-returns-a-tuple.md`)." % len(_seen_known))
    if args.selftest_no_exclusions:
        if disagree:
            print("[+] SELFTEST: %d disagreement(s) found with the exclusions dropped — "
                  "the oracle bites." % len(disagree))
            return 1
        print("[!] SELFTEST FAILED: dropping every exclusion found NO disagreement, so "
              "this oracle cannot detect a false contract at all.", file=sys.stderr)
        return 2
    if _nr_bad:
        ok = False
        print("[!]   A FUNCTION WITH NO NORMAL EXIT ON ANY ADMITTED ARGUMENT IS NOT NAMED: "
              "%s. Its `#@ ensures` is vacuously true — the prover discharges a claim about "
              "an exit the function does not have. Diagnose it and add it to NEVER_RETURNS "
              "with its reason, or repair it." % (_nr_bad,), file=sys.stderr)
    _raised_funcs = {(r[0], r[1]) for r in raised}
    if len(_raised_funcs) > MAX_RAISED:
        print("[!]   RAISED-ON-ADMITTED-ARGUMENT FUNCTION COUNT GREW: %d > %d (%d raise "
              "event(s), sampled up to three per function). Each one is a contract that "
              "promises a value on an argument where CPython raises: %s"
              % (len(_raised_funcs), MAX_RAISED, len(raised),
                 sorted(_raised_funcs)), file=sys.stderr)
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
