# genexp-erasure-wall-impl.md — R2 implementation plan (spike-first; refutation exit)

Synthesized from `genexp-erasure-wall.md` (CORRECTED) + `genexp-erasure-wall-response.md`
(Gate R **CONFIRM-WITH-CARVE-OUT**, 10 mandatory conditions). Route **R2**: build a faithful,
bounded `any`/`all` lowering. R3 (the `hval` carrier swap) is explicitly OUT of scope and gated
behind response-condition 7.

**Status of condition 1 (probe wired into the battery, ledger of 12, exits 1 on a NEW erasure):
DONE — commit `50247ac3`, landed before this plan, as the review required.**

## What is being built
`any(pred(x) for x in seq)` / `all(...)` currently lower — in EVERY context, program and spec — to
```
val any_1 (a: array int) : bool          (* unconstrained *)
… (if (any_1 (Array.make 1 0)) then 1 else 0)
```
`seq` is dropped and the predicate is erased. There is exactly ONE handler:
`src/pycsl/module6_whyml/expressions.py:5392`, `if func_name in ("any","all")`.

Target shape (the reviewer's `anyfold.mlw`, proven Valid on z3 AND Alt-Ergo, axiom-free):
```whyml
let function any_p (a: array int) : bool
  ensures { result <-> exists k. 0 <= k < a.length /\ <pred>(a[k]) }   (* IFF, condition 3 *)
= let r = ref false in
  for i = 0 to Array.length a - 1 do
    invariant { !r <-> exists k. 0 <= k < i /\ <pred>(a[k]) }
    if <pred>(a[i]) then r := true
  done; !r
```

## Gate S — the make-or-break SPIKE, FIRST, before any emitter edit
The reviewer already proved the SHAPE (`anyfold.mlw`). What is NOT proven, and what can still sink
R2, is that **PyCSL's emitter can generate it with the predicate inlined at the bound variable**.
That is this plan's falsifier, and it is a different question from the oracle's.

1. Re-run the reviewer's `anyfold.mlw` under `why3 prove -P z3` and `-P alt-ergo` → reproduce all
   five goals Valid + `grep -c '^ *axiom'` == 0. (Cheap; confirms the target is still valid.)
2. **THE FALSIFIER — emit ONE hand-written fixture through PyCSL, unmodified emitter, and read the
   `.mlw`:** does the emitter have ANY route from a genexp AST node to a body-carrying construct?
   Specifically, take `any(x > 10 for x in xs)` and determine whether the genexp's element
   expression (`x > 10`) and its bound variable (`x`) survive into Module 5's IR at all, or whether
   the IR has already discarded them by the time `expressions.py:5392` sees the call. Inspect the
   IR (`--dump-ir` or equivalent) — do NOT infer it from the emitted WhyML.
   - **PASS** (the predicate + bound var are present in the IR) → build.
   - **REFUTE** (Module 5 discards the genexp body before Module 6 — i.e. the erasure happens at
     IR construction, not at lowering) → the fix is a Module-5 feature, NOT a Module-6 one, and the
     costed scope in this plan is WRONG. **Record CERTIFIED-BOUNDARY-AT-M5, re-plan, do NOT grind.**
3. Second falsifier, only if (2) passes — **the predicate is an arbitrary expression over the bound
   variable, and the emitter must inline it under a binder.** Spike the HARDEST real shape in the
   mirror, not the easy one: `any(self._pattern_has_constructor(a) for a in pat.get("alternatives",
   []))` — a genexp whose predicate is a RECURSIVE SELF-CALL. If a recursive call cannot appear
   inside the generated fold (termination/variant, or the self-receiver), the IRScanner family is
   not reachable by R2 even though trivial predicates are. Record which sub-class R2 actually
   clears; do not claim the family.

## Build (only if Gate S passes)
(a) `expressions.py:5392` — replace the `any_1`/`all_1` abstract-op emission with a generated
    bounded fold, gated so it fires only for the genexp/comprehension argument form; a bare
    `any(arr)` (no genexp) keeps its current path unless the same fold applies.
(b) Emit the fold as a pure **`let function`** (condition 4) so the result is usable in `assert` /
    `ensures`; local `ref`s keep the interface effect-free (`purity1.mlw` Valid).
(c) The postcondition MUST be an **iff** (condition 3), never a one-directional `->`.
(d) **Contract grammar (condition 5):** a genexp inside `#@ assert` currently does not PARSE
    (`expected ')' (got NAME 'for')`). Both planes must be fixed in one change. If the grammar work
    turns out to be its own subsystem, SPLIT the increment and say so — do not silently ship the
    program plane only and claim the wall.
(e) Reference fixtures, `git add -f`, per the campaign convention: a program-position
    `any(genexp)` AND a `#@ assert all(genexp)`, each with a POSITIVE driver and an EVIL TWIN that
    reads the opposite answer (condition 6). Non-vacuity is the evil twin, NOT a mutation test —
    lesson (l) is precisely that a mutation test cannot see this family.

## Gate battery (driver-verified FRESH, per increment)
Fidelity (`self-annotate-mirror-check.sh` 52/52; `check-self-annotate-sync.sh` drift MUST NOT rise
above its current 5) ∧ whole-file Why3 proof of every touched mirror file ∧ **mirror-wide L3-tc
sweep, all 52** (run #4 lesson (a) — a past run shipped two type-broken mirror files because every
other gate passed) ∧ corpus byte-diff 0 **with the emitted population asserted at 782** (lesson (k)
— a zero diff over a zero population is a false green; the reviewer hit a 543-file short sweep) ∧
ledger == 3 (`Print Assumptions` / `#print axioms`) ∧ count MUST NOT RISE from 981 ∧
`bin/check-emitted-vacuity.py` exit 0, with any cleared IRScanner entry REMOVED from
`KNOWN_ERASURES` in the same commit ∧ **z3-inclusive proving** (condition 9: Alt-Ergo alone cannot
prove `"Number" <> "String"`).

## Honest costed scope
R2 removes an unconstrained oracle from at least 11 verified functions and repairs `#@ assert
all(...)`. It does **NOT** by itself de-vacuify the 8 fully-erased IRScanner predicates — their
`obj: Any` is independently int-erased, and that is R3. **Do not report R2 as "the 9 fixed".** The
honest success criterion for R2 is: the `any_1`/`all_1` oracle no longer appears in any emitted
mirror `.mlw`, the two fixtures prove with their evil twins, and the vacuity ledger shrinks by
whatever it actually shrinks by — possibly zero, if `obj` erasure keeps the IRScanner bodies
input-blind.

## Refutation exit
Gate S step 2 REFUTE (erasure happens in Module 5) → CERTIFIED-BOUNDARY-AT-M5 + re-plan.
Gate S step 3 REFUTE (no recursive predicate under the binder) → build R2 for the non-recursive
sub-class only, and record explicitly that the IRScanner family stays vacuous and gated.
Either way: record, commit the finding, do NOT grind.
