# gen #31 — what to read first

Three SEV-1 routes closed (#213 both arms, #224, **#225**), the directive-enforcement plane
taken from 32 to 51 of 53, `#@ reveal` implemented, and SIX directives found dropping a name
the user wrote in silence. Routes **#214 and #221 remain OPEN** — check
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
* `finding-thread-entry-and-releases-are-inert.md` — now the directive plane's ENTIRE
  outstanding debt, and the only reason it is not at 53 of 53.

## The four questions that found everything above

1. **Take one sentence of `annotations.md`, build the smallest program it describes, and run
   it BOTH ways.** Five directives left the uncovered list this way in one morning.
2. **Where a field's value comes from a FIXED SET, write the version that resolves to
   nothing.** Six hits. (My first phrasing said "admits an identifier" and missed two.)
3. **Where a sentence has TWO CLAUSES, test both.** A probe of one half retires a whole row
   and reads like a finding — how `sibling_concrete` and `propagate_frame` sat uncovered.
4. **Before landing a rule, construct the strongest program it would FORBID and check
   whether that program is good.** This is what withdrew the exhaustiveness refusal and
   widened the `Callable` admissible set to TypeVars.

## The lessons, if you read only the lessons

`wall-lessons.md` (q4) through (a5). The load-bearing ones: a green byte-diff means nothing
in the CORPUS moved (t4); a census measures the existing population, a rule applies to every
program that could be written (u4); run a new audit against your own newest increment first
(v4); the comfortable version of a bound is the one to check (y4); an increment is not
landed until it is committed (a5).
