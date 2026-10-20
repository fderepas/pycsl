# dict-value-wall — implementation plan (driver, gen #37, 2026-10-20)

Inputs: `dict-value-wall.md` (report, d5ef5b08) and `dict-value-wall-response.md` (independent
fable review, 1b837e40, 17 oracle runs). Both agree the wall is a MODELLING CHOICE and that no
measured combination of routes converts more than ~2-4 markers; the review re-ranks the routes by
markers per unit cost: R2a > R2b > R2c-local > R1 (leaf by leaf) > R3 (fail-closed) > R4 > R6 >
R2c-caller > R5. This plan executes the top three, in order, each spike-first with a refutation
exit, and records the rest as ranked levers.

Stack: the work rides on the `pycsl-land27` worktree (main + ch27's `_record_answer` /
`_tag_of_value`, whose 21-mirror re-proof is still OWED). R2a changes exactly the preamble line
that land27 already moves in those 21 mirrors, so folding R2a into land27 BEFORE its stage-2 proofs
pays for both with one round of re-proofs.

## Step 0 — fix the land27 seam's own red-team findings FIRST (precondition)
Red-team round 7 reported, inside the ch26/ch27 hval receiver seam: (F4) a non-map receiver
answers the default instead of raising AttributeError; (F5) `<hval> or ""` projects HInt/HArr to
`""`. Driver reproduces each (rc=0 + CPython counterexample) before any further work. A reproduced
false proof is repaired IN land27 (fail-closed: decline the seam when the receiver is not provably a
map / the hval is not provably HStr), with witness + control, before Step 1.

## Step 1 — R2a: spec the key equality (make-or-break spike first)
SPIKE (S1, hand `.mlw` + land27 emit, z3 AND alt-ergo): `val function hpairs_key_eq (a b: string)
: bool ensures { result <-> a = b }` in the land27 preamble; witnesses: (a) present-key read at the
head, (b) present key BEHIND a non-matching binding (two-key; the review measured alt-ergo cannot
separate string literals there, z3 can), (c) truthiness of a present HStr, each with a false twin.
PASS = (a)(b)(c) Valid under the default prover portfolio pycsl uses (if alt-ergo-only fails (b)
but the portfolio includes z3 and pycsl reports Valid, PASS) AND every false twin non-Valid AND the
spec is satisfiable (`goal false` Unknown/sat). REFUTE -> CERTIFIED-BOUNDARY for "present-key hval
reads" (record: needs literal-distinctness reasoning the portfolio lacks), keep land27 as is.
Ledger: the spec is a realizable Why3 `val` specification (precedent: `str_eq_op`,
`str_replace_op`, `map_nonempty`, stdlib `String.(=)`), not a kernel axiom; `Print Assumptions` /
`#print axioms` stays 3; correct the preamble comment ("Why3 has no native program string =" is
wrong: stdlib/string.mlw:487) and the report's "NOT an axiom" wording.
BUILD (on PASS): the one preamble line + comment; re-emit; mover set must equal land27's 21 mirrors
+ the 30 hval corpus files (diff = this line); M1: all 30 re-proved matching labels, all hval
false twins in the corpus still non-Valid (the review's soundness question).

## Step 2 — R2b: `for x in <HArr>` index loop + `"k" in <hval map>`
SPIKE (S2): hand `.mlw` over the land27 hval theory: an index loop over `HArr` elements with a
definitional length/get (sentinel-totality caveat: a non-HArr hval gives length 0 — state it), and
`in` as `pairs_get m k <> None`; prove a field read of element i, false twin fails. Then emit the
census's `_collect_generic_decls` retyped to `PyVal` and check L3-tc + honest body.
REFUTE -> CERTIFIED-BOUNDARY (reason recorded). PASS -> build in Module 6 (fail-closed recognizers,
no helper extraction in mirrored files), battery below.

## Step 3 — R2c-local: store into a LOCALLY BUILT dict value (value semantics)
SPIKE (S3): only for a dict literal built in the function and never escaping before the store;
prove the functional update equals Python's observable result; caller-tree stores stay the
R2c-caller memory-model boundary (no contract shape for assigns-through-path).

## Ranked levers recorded (not executed here)
R1 leaf-by-leaf retype (yield 1/19, cost = a whole-file proof per mover); R3 per-kind `value`
routing (fail-closed only; `IrNumF` reads 0 under `num_of`); R4 cross-mixin self-method typing
(gate on the underdeclaration plane; ALSO fix the plane gap found by rsurv: NodeVisitor
`generic_visit` dispatch is invisible to the underdeclaration arms); R6 declare cluster G a
CERTIFIED-BOUNDARY after the three `assigns \nothing`-but-appends trusted frames are made honest;
R2c-caller; R5 field declarations (HOLE-T delta unmeasured).

## Gate battery (every increment, driver-verified FRESH)
fidelity (check-self-annotate-sync + self-annotate-mirror-check) ∧ check-trusted-reasons ∧ mirror
emit diff vs base (each mover whole-file 0 non-Valid, LOW queue) ∧ corpus+pyref byte-diff (M1:
diff == the intended change, every mover re-proved to its label) ∧ witnesses (honest PASS failing
at base + false twins) ∧ fast planes 61/61 ∧ --slow 84/84 on the landed stack ∧ ledger 3 ∧
non-vacuity. Refutation exits as above; never grind.

## Cost
Step 0: ~1 h. Step 1: spike ~30 min, build ~15 min, re-proofs ride on land27's stage 2 (~12 h LOW).
Step 2: spike ~1 h, build ~3 h + re-proofs. Step 3: spike ~1 h.
