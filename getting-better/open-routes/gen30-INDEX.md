# gen #30 — what to read first

Twenty-three SEV-1 routes (#191–#213 closed, **#214 open**), nineteen planes, and four
measurements that change what the campaign's own numbers mean. This file is the map.

## If you read one thing

`getting-better/gen30-summary-draft.md`. Everything below is the detail behind it.

## The routes, grouped by the question that found them

**"Which spelling did the justification not run?"**
* `route198…` – a bare `return` was the integer 0
* `route199…`, `route203…` – the empty and single-part f-strings
* `route200…`, `route201…`, `route202…` – string actuals at int/array/un-annotated params
* `route206-208…` – a `total` policy over a helper that never returns (`\trusted`, then
  `\diverges` through my own repair twenty minutes later)
* `route213-214…` – the two `getattr` devices, including the three-argument spelling my
  own refusal missed

**"What does this docstring actually claim?"**
* `route204…` – an `#@ interface assigns` narrower than the definition
* `route205…` – an over-claiming `#@ interface` refused at home, believed by every importer
* `route207…` – `no_exception \all` through a `\trusted` method that always raises

**"Is this check reachable at all?"**
* `route209…` – the `protects` trust boundary asked a `pure_ast` matcher about a CSL node
* `route210-211…` – a `#@ check` stamped into a body that is never lowered

**"Who believes this, and who checked it?"**
* `route212…` – **OPEN.** The importing unit believes every contract of an imported module.
  `--verify-imports` is built and off by default; the design note says why "verify the file
  on its own" is the wrong meaning.

## The measurements that reframe the numbers

| what | number | plane |
|---|---|---|
| mirror that is trusted OR trust-dependent | 56%–61% (marker count: 459) | `check-trust-blast-radius.py` |
| un-trusted mirror that makes a VALUE claim | 143 of 933 (15%) | `check-mirror-claim-strength.py` |
| corpus files whose contract says nothing | 1791 of 3888 (46%) | `check-claim-vacuity.py` |
| corpus files run with the prover OFF | 1754 of 3881 (45%) | `check-corpus-contract-truth-args.py` |
| stdlib modules that VERIFY | 84 of 104 | `check-stdlib-modules-verify.py` |
| compiler refusals with a WITNESS | 84 of 198 (58 at first measurement) | `check-refusal-witness-coverage.py` |

## The findings that are not routes, and why each is not

* **The axiom registry disagrees with itself** — the legacy `UnixFs.Struct.*` round-trips
  are unguarded where their successors carry CPython's range conditions. Not a route on
  §2.1.13's terms (exceptional exits are out of scope without `no_exception`), but a defect
  by the repo's own standard.
* **`capwords` never grows a string — except it does** (`'ß'` → `'Ss'`). The model's body
  agrees with the proof, so CPython running THE MODEL agrees; the falsehood is about the
  function the model cites.
* **A `stable_hash` collision, constructed** in 24,726 strings. Not exploitable today
  because the one op that receives a folded literal is a `val`, not a `val function`. One
  keyword of margin, now held by `check-hashed-literal-purity.py`.
* **`#@ complete` / `#@ disjoint` on a bodyless function** are unchecked. The caller
  exploit was built and refused, so nothing consumes the false completeness today; refused
  anyway.

## The lessons, in `getting-better/wall-lessons.md`

(v2) an unmentioned exclusion is an oversight wearing one · (w2) attack a marker before
believing it is forced · (x2) trust has a blast radius, and a PASS count is not a proof
count · (y2) an enforcement mechanism that writes into a body is only as strong as the
guarantee the body is compiled · (z2) a check with no witness has no evidence it can fire ·
(a3) "verify the dependency" is not "verify the file" · (b3) a lowering fix must re-run the
refusal the old shape was accidentally enforcing · (c3) read the axiom registry the way you
read the docstrings.
