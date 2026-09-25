# gen #31 — what to read first

Three SEV-1 routes closed (#213 both arms, #224, **#225**), a FOURTH found and its first two
increments landed (**#226**), the directive-enforcement plane taken from 32 to **52 of 53**,
`#@ reveal` implemented, and NINE directives found dropping a name the user wrote in silence.
Routes **#226 (one carrier left of four), #214 and #221 are OPEN** — check
`bin/check-open-route-carriers.py`, which RUNS their carriers, before believing any index.

THE SECOND HALF OF THE GENERATION WAS ABOUT INSTRUMENTS. Asked of route #226, "which
existing instrument should have found this, and why did it not" produced two extensions and
one new plane in a day — and then the same question, asked of an EXCLUSION LIST rather than
of a population, produced the generation's other finding: `struct.unpack` returns a tuple,
and six proof-cited corpus functions certify `\result == x`. Three instruments could have
seen it and each had a different boundary.

## If you read one thing

`getting-better/driver-progress.log`, from the gen #31 entries onward. This file is the map.

## The routes

* **#224** — `#@ conforms_to` was unchecked by default. The refinement goal now follows the
  DIRECTIVE, via a `from_conforms_to` IR tag, so declaring conformance does not silently
  turn on the implicit inheritance Liskov obligation for every based class.
  Witness `1855`, control `1856`.
* **#213** — both arms of the per-site `getattr` device. The device is applied to
  `!_pyobj_state`, keeping route #197's equality where justified and losing it across a
  write. `route213-214-the-getattr-devices.md`.
* **#225** — `route225-a-returned-empty-list-has-length-1024.md`. A function returning `[]`
  CERTIFIED `\length(\result) == 1024` while the TRUE claim `== 0` was refused. The THIRD
  position of one mechanism: #159 repaired indexing (gen #29), #196 the argument boundary
  (gen #30), and the RETURN carries the false length across a function boundary where a
  caller ASSUMES it. Witnesses `1869`/`1870`/`1871`.

* **#226 — OPEN, SEV-1.** A `#@ class invariant` the CONSTRUCTOR never establishes is
  assumed by every method: `invariant { n >= 5 } by { n = 10 }` is emitted for an
  `__init__` that sets `n = 0`, and the `by` witness is SYNTHESIZED FROM THE INVARIANT.
  Found because an unrelated increment's FALSE TWIN verified. Carrier registered.
  **Read the route file's CORRECTION section before quoting it**: the emitter DOES raise
  the invariant VC where a record is CONSTRUCTED, so the obligation is attached to the
  CONSTRUCTION SITE rather than to the CLASS — a file that defines the class, publishes
  `def read(c: C) -> int` for it and constructs nothing is never asked, which is the
  ordinary shape of a library module and the reason this is SEV-1. FOUR carriers, and
  the prepared increment closes ONE of them (the 113 corpus classes whose `__init__`
  takes only `self` and stores int literals); a parameter-initialised field, a
  computed/control-flow store, and `@dataclass` stay open and are recorded, not closed.
  `route226-a-class-invariant-the-constructor-never-establishes.md`.

## The findings that are not routes, and why each is worth its file

* `finding-a-name-that-resolves-to-nothing-is-dropped-in-silence.md` — SIX directives.
  `Callable[[Rekt], int]` became `int`; `#@ uses`, `#@ reveal` and `#@ footprint` (in a file
  with no `#@ happy`) were dropped; `#@ ghost`'s type keyword and `#@ proof`'s prover
  keyword are the two found after the first four were repaired. EIGHT other directives DO
  refuse, which is what makes it a defect rather than a policy.
* `finding-array-import-missing-for-a-list-field-only-program.md` — one rule ("the record
  decl is emitted from the FIELD") stated correctly in TWO adjacent disjunctions and
  implemented for one witness each, so a class whose only array is a list field dies on
  `unbound type symbol 'array'` and a dict-of-lists field on `'seq'`.
* `finding-hard-error-claims-audited.md` — the `#@ datatype` match-exhaustiveness refusal,
  **WITHDRAWN after its census came out zero**, because one constructed counter-program
  showed the rule would forbid a good program.
* `finding-thread-entry-and-releases-are-inert.md` — the directive plane's ENTIRE
  outstanding debt, and the only reason it is not at 53 of 53. Re-measured independently
  late in the generation and it holds exactly; it now carries an ADDENDUM, because going
  back to `releases` to write the pair it cannot have produced the next file.
* `finding-a-mutex-name-that-resolves-to-nothing.md` — `#@ critical` / `#@ acquires` /
  `#@ releases` never validate the mutex NAME, and **this one corrects the sweep above**:
  `#@ critical` was listed as one of the CONTROLS that refuse an unknown name. It does not.
  The file that produced that verdict wrote to a protected shared variable inside the
  block, so the refusal came from the PROTECTION analysis. Two of seven controls were a
  different check wearing a name check's clothes, and they hid three more instances of
  exactly what the sweep was hunting. Wall-lesson (e5).
* `finding-a-list-out-of-a-dict-cannot-be-passed-anywhere.md` — the measured answer to
  "why has the `\trusted` count not moved in thirty generations". The cheapest stub in the
  mirror is FIVE lines; built on an offline copy of the tree and put through the real
  whole-file proof it needs two patches AND a modelling decision (`List[T]` parameter is
  `array T`, `Dict[K, List[T]]` value is `seq T`, no bridge). Carries the matrix of which
  read forms work for which element types; every FAILED cell but one is a missing branch
  beside a present one.

## THE QUESTION NOBODY HAD ASKED: DOES THE CORPUS RUN?

Every oracle in this battery executes a corpus function BECAUSE A CLAUSE ASKED IT TO, so a
file whose clauses none of them can read is a file nobody has ever run. Asked directly, the
question took an afternoon and produced the generation's largest finding —
`finding-a-verified-program-that-is-not-the-executed-program.md`, **NINETEEN functions across
FIVE mechanisms**, every one in a `# pycsl-expected: PASS` driver — plus a new plane and four
corpus repairs.

    `#@ datatype` constructors, declared and never defined       11 functions,  9 files
    `#@ compose_from` provider methods                            3             3
    the verifier supplying a name or value Python lacks           3             3
        0640 `ast.literal_eval` with no `import ast`
        0642 `exec` splicing — *"verification-equivalent"*, and it is not
        0199 a dict modelled TOTAL, where Python raises KeyError
    a `@dataclass` annotation contradicting its default           1             1
    the `int` placeholder making a signature unsatisfiable        1             1

`bin/check-corpus-executes.py` is the plane: does the file LOAD, and does its own
`if __name__ == "__main__"` self-check pass. It found a driver that is not a Python program
at all (`1190`, `@mutable_state` used and never defined, NameError at import), a circular
fixture CPython refuses, and **two author-written self-checks that had never executed in any
run** (`0312` names a function the file does not define; `0452` compares a `bytearray` with a
`list`). A self-check nobody runs is a comment.

**Two bugs in that plane, both caught before it landed, and the second by arithmetic on its
own report**: a bare-dict namespace broke `dataclasses`' annotation resolution (17 false
alarms), and an unrestored `sys.modules` made three drivers sharing one fixture report two
different verdicts depending on glob order — 1380 loaded plus 2 failures is not 1384.
Wall-lessons (w5), (y5), (z5).

## THE FINDING THAT CAME OUT OF A POPULATION WIDENING

`finding-a-contract-over-a-function-that-never-returns.md`. Two PASS-expected corpus
functions have **no normal exit on any argument their own `#@ requires` admits**, so their
`#@ ensures` is discharged over no runs at all. A vacuous proof wearing a contentful
clause — and every vacuity instrument here looks at the CLAUSE, which is why none of them
saw it. Wall-lesson (v5).

* `0496.py::grab` — `__new__(cls)` takes no extra argument while `__init__(self, n)` does,
  so `Holder(k)` is a `TypeError` for every k while `\result == k` verifies. `__new__` is
  an ANALYSED surface (UB-7.6 rejects a non-trivial one), so the missing arity comparison
  is a defect, not a boundary.
* `0554.py::Service.tick` — `#@ compose_from Counter` flattens `bump` into `Service` in the
  VERIFIER; CPython's MRO does not, so `self.bump()` is an `AttributeError` on every call.
  **Censused: all ELEVEN composing classes in the corpus compose a provider they do not
  inherit, and in ten of the eleven the provided name is absent at runtime. Not one
  composing class in the corpus is executable Python.**

**Then the obvious repair was tried, and PyCSL REFUSED it.** Writing `class Facade(CoreEmit,
MapOps)` makes the flagship run — `run(3)` is 3, `run(-1)` is 0, both `>= 0` — and route
#95's shadow check rejected it with "'Facade' defines its own 'emit'" of a class whose
entire body is `run`: `own_tails` comes from the IR function list, where the base-class
binding has already materialised `facade__emit`. The directive that exists to make mixin
composition machine-checkable was refusing the only spelling of it that performs the
composition. **Repaired** with a SAMENESS test (same line, column, body, contracts — the
base list is deliberately not consulted), measured against the strongest program it admits:
witness `1902` (PASS, and it RUNS), controls `1903` (weak provider still FAILS — route #95
is not reopened) and `1904` (a real override is still REFUSED). `0554`'s stateful case
remains open: it gets past the front end and dies in the emitted WhyML on `unbound function
or predicate symbol 'count'`.

## THE FINDING THAT CAME OUT OF AN EXCLUSION LIST

`struct.unpack` returns a TUPLE. Six corpus functions across three PASS-expected drivers
(0753, 0778, 0779) declare `#@ ensures \result == x` over `return struct.unpack(...)`, and
all six verify. Deleting the `#@ proof rocq|lean` citations makes 0753 FAIL, so the
discharge is the audited-external-proof opt-in — a FINDING, not a SEV-1 route, and still a
defect in a CHECKED surface: the registered axiom is a true theorem about a byte codec
returning an INT, and nothing in the 3-way cross-check compares the Rocq result TYPE with
the Python return type.

**Three instruments could have found it and each has a different population boundary.**
`check-corpus-contract-truth-args` had `\nothing` in a skip list whose stated purpose is
"tokens this oracle cannot evaluate" — a token that appears ONLY in `#@ assigns \nothing`,
a clause it never reads — and tested the whole annotation block, excluding every empty-frame
function (416 -> 519 functions, 4367 -> 5750 evaluations). `check-stdlib-contract-fidelity`
has `\length` in ITS skip list, and could not call the real function anyway because the
shim models a format STRING as an int. The zero-argument oracle needs a literal `== N`.
One defect, sitting in the intersection of three boundaries.
`finding-struct-unpack-returns-a-tuple.md`, wall-lesson (o5).

## The two INSTRUMENTS this generation added, both from one question

**"Which existing instrument should have found this route, and why did it not?"** Asked of
route #226, it had two answers:

* `check-corpus-contract-truth` — the sharpest oracle in the battery, and its POPULATION was
  zero-argument FUNCTIONS with a literal `\result == N`. Route #226's carrier is a METHOD
  with a COMPARISON: outside it on both axes. Extended to zero-argument methods of
  `C()`-constructible classes and to the comparison operators: **390 runnable contracts ->
  432, 378 agreeing -> 417, 0 DISAGREE**, and it now reports route #226's own carrier when
  pointed at it.
* `check-corpus-contract-truth-args` — the POST-STATE axis. Every clause it read was about
  `\result`, so a method promising `#@ ensures self._balance == \old(self._balance) +
  amount` was outside the population on both counts. It is checkable there and nowhere else
  in the battery, because that oracle CONSTRUCTS the pre-state: build the object, snapshot
  the fields, call, evaluate against the snapshot. **548 functions / 6011 evaluations ->
  579 / 6114; 31 methods, 96 post-state clause evaluations, 0 FALSE.** And the widening's
  real yield was a file it could newly RUN, not a claim it could newly check.
* `check-class-invariant-establishment` — **did not exist**. For every PASS-expected corpus
  class that `C()` constructs, build the object and evaluate its own `#@ class invariant` on
  it. 75 classes, 84 clauses, 0 FALSE; and it reports all three of the shapes route #226's
  emitter repair deliberately cannot state (`@dataclass`, computed, control-flow).

Both were validated the only way a detector can be: **run it on the thing it was written to
detect.** A green corpus proves REACH, not SENSITIVITY.

## The six questions that found everything above (four during, two added at the end)

1. **Take one sentence of `annotations.md`, build the smallest program it describes, and run
   it BOTH ways.** Five directives left the uncovered list this way in one morning.
2. **Where a field's value comes from a FIXED SET, write the version that resolves to
   nothing.** Six hits. (My first phrasing said "admits an identifier" and missed two.)
3. **Where a sentence has TWO CLAUSES, test both.** A probe of one half retires a whole row
   and reads like a finding — how `sibling_concrete` and `propagate_frame` sat uncovered.
4. **Before landing a rule, construct the strongest program it would FORBID and check
   whether that program is good.** This is what withdrew the exhaustiveness refusal and
   widened the `Callable` admissible set to TypeVars.
5. **Re-run your own CONTROLS on the smallest program that carries the directive and
   nothing else.** Added late, and it paid immediately: two of question 2's seven controls
   were answered by a neighbouring check, which hid three more silent names. A control is a
   claim; the corpus-shaped witness is the trap, because real programs bring the
   neighbouring check with them.
6. **Copy the tree and build the repair OFFLINE.** `cp -a src $SCRATCH/tree/src`, patch
   there, run `python3 $SCRATCH/tree/src/pycsl/pycsl.py`. "No live edits while a battery is
   in flight" is a rule about the tree, not about the work — and an offline copy is also
   how a repair gets measured on real corpus files before it is ever applied. Route #226's
   repair, the mutex refusal and the field-param pair were all built and verified this way,
   with a gate running the whole time.

## The lessons, if you read only the lessons

`wall-lessons.md` (q4) through (a5). The load-bearing ones: a green byte-diff means nothing
in the CORPUS moved (t4); a census measures the existing population, a rule applies to every
program that could be written (u4); run a new audit against your own newest increment first
(v4); the comfortable version of a bound is the one to check (y4); an increment is not
landed until it is committed (a5).
