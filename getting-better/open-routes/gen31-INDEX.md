# gen #31 — what to read first

Three SEV-1 routes closed (#213 both arms, #224, **#225**), the directive-enforcement plane
taken from 32 to 51 of 53, `#@ reveal` implemented, and SIX directives found dropping a name
the user wrote in silence. Routes **#226 (NEW, SEV-1), #214 and #221 are OPEN** — check
`bin/check-open-route-carriers.py`, which RUNS their carriers, before believing any index.

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
