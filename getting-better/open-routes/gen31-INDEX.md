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

THE THIRD PART OF THE GENERATION ASKED THE QUESTION UNDERNEATH THE INSTRUMENTS: **does the
corpus RUN?** Nineteen PASS-expected functions raise on every argument their own precondition
admits, across five mechanisms; a new plane (`check-corpus-executes.py`) now asks it on every
gate; and the same question turned on the conversion track produced the campaign's headline —
**two `\trusted` stubs that convert and prove**, of which the four-check discipline says land
exactly one.

## If you read one thing

`getting-better/driver-progress.log`, from the gen #31 entries onward. This file is the map.

## If you read TWO things, the second is this

`finding-two-trusted-stubs-that-convert-and-prove.md`. It is the first time this
TCB-reduction campaign has taken a `\trusted` marker all the way to "measured, checked, and
ready to retire" — and the first time it has said, with evidence, that a SECOND candidate
which also converts and also proves **must not be landed**. The sentence to carry away:

> A green whole-file proof is NECESSARY for retiring a trust marker and nowhere near
> sufficient. `\trusted` is not a hole in the proof; it is a LABEL on a claim nobody checked,
> and removing the label re-files the claim from ASSUMED to PROVED — an improvement only if
> the model can SEE the thing the claim is about.

For `message` it can (an assumed frame becomes a proved one). For `_cache_root` it cannot:
the body is a `mkdir`, the lowering gives it no frame, and `#@ assigns \nothing` would be
certified over a directory creation. That failure generalised to a seventeen-stub
DO-NOT-CONVERT list in `finding-assigns-nothing-over-a-subprocess.md`.

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

## TWO `\trusted` STUBS CONVERT AND PROVE — AND ONLY ONE OF THEM MAY LAND

`finding-two-trusted-stubs-that-convert-and-prove.md`. The campaign's headline number moving,
demonstrated rather than planned:

    errors.py::message                    converted -> the file PROVES  (~11 s)
    audit_proof_reverify.py::_cache_root  converted -> the file PROVES  (~28 s)

**And the four-check discipline separated them on the FIRST check, in four minutes.** The
emit-diff says:

* `message` — the abstract `val` becomes a `let` carrying four `self.f = old self.f` clauses
  that the proof DISCHARGES, and `super().__str__()` becomes `val str_dunder_op () : string`
  with no defining axiom: the SAME opacity the `val` already had. An ASSUMED frame becomes a
  PROVED one. **Landable.**
* `_cache_root` — the body is `root.mkdir(parents=True, exist_ok=True)`, and the lowering
  emits `val root_mkdir_0 () : int`, nullary, no `writes`. So the model sees no effect and
  **CERTIFIES the declared `#@ assigns \nothing` over a directory creation.** Not landable.

**A green whole-file proof is NECESSARY for retiring a marker and nowhere near sufficient** —
the single most important sentence for whoever works the remaining 454 candidates.

That failure generalised: `finding-assigns-nothing-over-a-subprocess.md` censuses **17
receiver-confirmed `\trusted` stubs** that declare `#@ assigns \nothing` while their live
body calls `subprocess.run`/`Popen`, `os.makedirs` or `os.remove` — a clause both
`annotations.md` and the static-semantics reference gloss as *"pure, side-effect-free"*.
`check-trusted-frame-honesty.py` was built for exactly this shape and says so in its header;
its POPULATION is `self.<attr>` stores, so a module-level function that shells out to
`why3 prove` mutates no attribute and the plane is silent. The list doubles as a
DO-NOT-CONVERT list.

## THE CONVERSION SURFACE, MAPPED BY FORTY-NINE TWO-LINE PROGRAMS

`finding-the-conversion-surface-mapped-by-two-line-programs.md`. The backlog had ranked the
conversion blockers three times by COUNTING bodies. Forty-nine probes, twenty seconds each,
replaced the ranking with facts:

* **strings: 16 of 16 VERIFY** — split (with and without a maxsplit), startswith, replace,
  slicing, indexing, len, `+`, `==`, substring `in`, `str()`, `int()`. When a conversion
  fails, it is not the strings. A negative result, and the most useful kind.
* **f-strings are not a wall** (186 bodies, three shapes, all verify), and neither are list
  comprehensions or dict literals in the shapes that dominate. What fails is narrow: a
  comprehension over a `range` or with a CALL element, dict/set comprehensions, the set
  literal, `",".join(xs)`.
* **dicts**: `d[k]`, `.get`, `in`, `d[k] = v`, `len(d.keys())` verify; `len(d)`,
  `for k in d`, `.setdefault` and a nested `Dict[str, Dict]` do not. `len(d)` fails and
  `len(d.keys())` works — then censused at ONE corpus instance, in an expected-FAIL witness,
  so it is recorded as NOT worth building.

Every probe carries `#@ ensures True`: a VERIFY means the construct LOWERS, not that the
lowering is FAITHFUL. That is the right scope for a conversion blocker and the wrong scope
for a soundness claim, and keeping the two apart is what makes the map cost an afternoon.

## THE CONVERSION TRACK'S TOP ITEM, MEASURED THREE TIMES AND SMALLER EACH TIME

The backlog ranked conversion blockers three times by COUNTING. Probing instead:

1. **104 of the 435 still-`\trusted` functions sit behind ONE refusal** — the in-place
   mutators. `.append` VERIFIES (and is the single largest construct in the population, 154
   functions, which is why counting misleads); `extend`/`pop`/`insert`/`sort`/`remove`/
   `reverse`/dict `.update` are all refused by one message that states its own repair:
   *"the call becomes an abstract operation that takes NEITHER the receiver NOR a `writes`
   clause"*. It is a SOUNDNESS FENCE with a measured witness (`0982`: `xs.reverse(); return
   xs[0]` PROVED `== 0` where Python answers 7) and `.append`'s faithful lowering is the
   template, at `statements.py` ~3017.

2. **The `Set[str]` / `str.join` / `List[str]` cluster is ONE cause**, and it is not a
   fixpoint. `Module5_IREmitter` has TWO κ extractors thirty lines apart: the FIELD one
   handles `Set[str]` and says why in its docstring — *"a set's element IS its key"* — and
   the PARAMETER one handles only `Dict[str, V]`. The gen #31 shape for the FIFTH time: one
   rule, two adjacent places, implemented in one. Reading κ from the DECLARATION at the
   parameter site makes the carrier VERIFY with the `Set[int]` control still green, and
   needs no propagation pass — both ends of a call edge read the same declaration.

3. Sized, re-sized and re-sized again: "double-digit-hour proof bill" (written while the
   second re-proof was still running) became "two mirror files, one of them clean, one call
   edge" became "the call edge was a symptom of the extractor". Wall-lesson (e6).

The gap is GATED so it cannot be rediscovered: `setelem-carrier-read-only-str-set-membership.py`
plus two controls in `check-open-route-carriers.py` (5 carriers -> 8).

## THE CONVERSION TRACK, MOVED BY TEN TWO-LINE PROGRAMS

`finding-a-set-has-no-element-type-and-no-union.md`. The backlog has ranked conversion
candidates three times in three generations, each ranking by reading or counting them. This
one was produced by PROBING the operators instead, and it replaced the ranking with a single
line of source.

    m in held            Set[int]   SUCCESS      held.add(m)        Set[str]   SUCCESS
    m in held            Set[str]   FAILED       held.add(m); m in held        SUCCESS
    s | {x} in @mutable_state       SUCCESS      s | {x} standalone            FAILED
    a | b  anywhere                 FAILED       len/& /-/^/.union/.intersection  FAILED

**`module6_whyml/functions.py` ~137** explains every row:

    _sk = "string" if (_mut_coll and kt.get(arg) == "string") else "int"

A MUTATED `Set[str]` param is string-keyed; a read-only one "must STAY `map int`" because it
feeds sibling `val` bridges typed `map int` — and the comment names what is missing: *"that
cross-method κ=string agreement is the deferred I4 fixpoint"*. The mechanism was accepted
only after it PREDICTED an eleventh probe (`add` then test → verifies, because the `add`
promotes the param), which is wall-lesson (a6).

Deleting the `_mut_coll` conjunct on an offline tree makes the read-only membership verify,
with the `Set[int]` control green and **0 of the 14 emittable set-using corpus files moved**.
Censused exposure: **ZERO read-only `Set[str]` params in either corpus**; 39 in `\trusted`
mirror stubs; 120 mirror functions already converted and PROVING today (their keys are
`.get()` results the tagger cannot prove are strings, so κ stays int and everything agrees).

FIVE CORRECTIONS in that one record, every one caught by measuring instead of asserting —
which is the method the generation is actually about.

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

## THE TWO OPERATIONAL FAILURES THIS GENERATION PAID FOR, because they will recur

* **A full `/tmp` presents as a broken shell — and a broken gate presents as a FINDING.**
  Twenty-five minutes of every Bash call returning exit 1 with no output, mis-diagnosed
  twice, was a 7.6 GB tmpfs filled by this campaign's own best habit: `cp -a src` at 76 MB a
  copy, eight in one session plus five from earlier windows. The gate running at the time
  reported dozens of `MOVED` files in a PROVED corpus — the signature of the most serious
  thing this campaign looks for — and it was truncated writes. `df -h /tmp` would have found
  it in ten seconds. Wall-lessons (g6), (h6), and (c6)'s second paragraph: never `pkill -f` a
  pattern that can match the harness's own shell.

* **A marker is a syntactic position, not a string.** Three instruments in one session
  matched `\trusted` by SUBSTRING and so matched sentences ABOUT the marker: the raw count
  (485 vs 460 — `count-trusted-directives.py` prints the 25-line gap on every run), the
  conversion screen's candidate list (456 vs **410**), and `convert_one.py`, which DELETED a
  line of prose and reported a successful conversion. The repo had the right rule written
  down twice. Wall-lesson (j6).

## The lessons, if you read only the lessons

`wall-lessons.md` (q4) through (a5). The load-bearing ones: a green byte-diff means nothing
in the CORPUS moved (t4); a census measures the existing population, a rule applies to every
program that could be written (u4); run a new audit against your own newest increment first
(v4); the comfortable version of a bound is the one to check (y4); an increment is not
landed until it is committed (a5).
