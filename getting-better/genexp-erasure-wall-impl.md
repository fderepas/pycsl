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

---

## §GATE-S — SPIKE OUTCOME: **REFUTE of this plan's scope (re-plan, cheap), not of R2 itself**

Count unchanged (981), ledger 3, no emitter edit made.

**Step 2 (the falsifier) REFUTES the Module-6-only scope, and the emitter says so in its own
comment.** `src/pycsl/module6_whyml/expressions.py:5392` reads:

> *"Unsupported iterable shapes (generator expressions etc.) get **dropped to `0` at the IR
> level**; coerce that to an array placeholder so the abstract val type-checks."*

Confirmed structurally: `grep -c GeneratorExp src/pycsl/frontend/Module5_IREmitter.py` → **0**.
`ast.GeneratorExp` is absent from `_PY_EXPR_HANDLERS`, so `_py_expr_to_ir` returns the fallback
`{"type": "UnknownPyExpr"}` and `_array_coerce_arg` renders it `Array.make 1 0`. **The erasure
happens at IR CONSTRUCTION (Module 5), before Module 6 ever sees a predicate.** Editing the
Module-6 handler alone could not have worked, and the plan's costed scope was wrong.

**The re-plan is CHEAP, not session-scale** — which is why this is REFUTE-and-re-plan rather than
CERTIFIED-BOUNDARY. `ast.ListComp`/`SetComp`/`DictComp` ARE handled (`Module5_IREmitter.py:1052-4`,
`_py_expr_listcomp` at 1210) and preserve `elt` + `generators`. A `GeneratorExp` is structurally
identical to a `ListComp`, so Module 5 needs one dispatch entry plus a handler modelled on the
existing one.

**Step 2 also found a SECOND erasure layer the report and the review both missed.** The bracketed
form `any([x > 10 for x in xs])` DOES reach Module 6 carrying a real `ListComp` IR — and is erased
there anyway, by a different oracle:

```
let function g_form (xs: array int) : int = (if (any_1 (Array.make 1 0)) then 1 else 0)   (* genexp   *)
let function l_form (xs: array int) : int = (if (any_1 (list_comp 0))    then 1 else 0)   (* listcomp *)
  val list_comp (x: int) : int      (* unconstrained, argument int-erased to 0 *)
```

So R2 must clear TWO layers: `UnknownPyExpr` in M5 **and** `list_comp` in M6.

**Step 2 also REFUTES the plan's byte-inertness claim in part.** The review verified 0 corpus sites
for `any_1`/`all_1`, and that stands. But `list_comp` appears in **1 corpus file (`0042.mlw`)**, and
14 corpus programs contain a list comprehension. So:
- gating the fold to the `any`/`all` argument position ONLY → still byte-inert (0 corpus sites);
- touching the GENERAL `ListComp` lowering → **NOT byte-inert**, and needs an M1 sanctioned reset
  with `0042` re-proving. Do not conflate these two; the second is a separate authorization.

### Re-planned increments (each separately spike-gated)
- **R2a** — Module 5 `ast.GeneratorExp` handler mirroring `_py_expr_listcomp` (dispatch entry +
  handler). Makes the predicate and bound variable reach Module 6. Byte-inert (no corpus genexp
  reaches an emitted site today). Small.
- **R2b** — Module 6: generate the bounded iff-specified fold for `any`/`all` **when the argument
  IR is a comprehension**, replacing `any_1`/`all_1` at that position only. Byte-inert by the gate
  above. Must be a pure `let function` (condition 4) with an iff postcondition (condition 3).
- **R2c** — contract-grammar genexp support so `#@ assert all(x >= 0 for x in a)` parses
  (condition 5). Currently `expected ')' (got NAME 'for')`. Independent of R2a/R2b; if it proves
  to be its own subsystem, ship R2a+R2b and say the spec plane is unfixed — do NOT claim the wall.
- **Step 3 (recursive-predicate falsifier) NOT YET RUN.** It only becomes answerable once R2a
  lands and a genexp body actually reaches Module 6. Until then, whether the IRScanner family is
  reachable at all is OPEN, and R2 must not be described as fixing it.

---

## §R2b OUTCOME — **BUILT for the simple-predicate sub-class; Gate S step 3 ANSWERED (IRScanner is out of reach)**

Commit `82e02ad4`. Count 981 -> 981, ledger 3, corpus diff = exactly the 2 new fixtures.

**What works.** `any(P(x) for x in it)` / `all(...)` now emit the reviewer's bounded fold with a
full **iff** postcondition (response condition 3), as a pure `let function` (condition 4), the
predicate lowered through the emitter's existing `subst` binder channel. Fixtures 0936 (positive,
PROVES a real statement about the input) and 0937 (evil twin, MUST NOT prove — and does not).
Both the genexp and the bracketed list-comp form share one spec-hashed definition.

**Gate S step 3 — the recursive-predicate falsifier — is now ANSWERED, and it REFUTES the
IRScanner half of R2.** Instrumenting every bail path and running it over the whole mirror
accounts for all 21 remaining `any_1 (Array.make 1 0)` sites:

| sites | reason | reachable? |
|---|---|---|
| **18** (all of IRScanner) | `predicate-needed-op: iRScanner_uses_string_1` — the predicate is a **recursive self-call** | **NO** — needs `let rec function … with …` mutual recursion + a termination variant; the fold is a standalone `let function` in the abstract-ops block and cannot reference the function being defined |
| 1 (`_handle_fieldassign_stmt`) | `stripped.startswith(p)` over a list of **strings** | plausibly — needs a parameterized element type (the fold hardcodes `a: array int`) |
| 1 (Module5_IREmitter) | `predicate-lost-binder: elt_type=BinOp` | unknown — the binder does not survive lowering |

So **R2 does not de-vacuify the 8 fully-erased IRScanner predicates**, exactly as this plan's
"honest costed scope" warned it might not. Their `obj: Any` int-erasure (R3) was never the only
blocker — the recursion is a second, independent one. The vacuity ledger stays at **12**.

### Remaining, in dependency order (each still spike-gated)
- **R2d — mutual-recursion folds.** The only route to the IRScanner 18. Emit the fold INSIDE the
  recursive group (`let rec function f … with _any_fold_f …`) with a shared `variant`. This is a
  materially larger emitter change than R2a/R2b and must be spiked before it is authorized.
- **R2e — parameterized element type** (`array string`, `array <record>`): unlocks the
  `startswith` site and is a prerequisite for any string-predicate fold.
- **R2c — contract-grammar genexp** (response condition 5): `#@ assert all(x >= 0 for x in a)`
  still does not PARSE. Untouched by R2a/R2b; the spec plane remains unrepaired.
- **R3** — unchanged and still gated behind response condition 7 (assoc-list `hval` proving its
  evil twin with the map arm present).

## §R2e SPIKE OUTCOME — REFUTE-as-bounded: R2e is SESSION-SCALE, needs authorization (like R2d/R3)

Gate-S spike (`scratchpad/anyspike/r2e.py`, no emitter edit). The 2 non-recursive string-predicate
sites (`_handle_fieldassign_stmt`, `_union_arm_tag`) need FOUR coordinated capabilities, not the
"parameterized element type" this plan scoped:
1. **Element-type parameterization.** The fold hardcodes `a: array int`; `any(x == "" for x in xs)`
   over a `List[str]` emits `_any_fold (a: array int)` applied to `array string` → L3-tc TYPE ERROR.
2. **Faithful string-predicate lowering INSIDE the fold.** Even typed, `x == ""` lowers to
   `a[_fk] = 313406155` (the int-hash of `""`) — a vacuous comparison; it must be `str_eq_op a[_fk] ""`.
3. **Closure-capture threading.** `any(s.startswith(p) for p in prefixes)` captures the FREE var `s`;
   a standalone `let function _any_fold (a: ...)` cannot see it, so it must be threaded as an extra
   fold parameter. Today it fully erases to `any_1 (Array.make 1 0)`.
4. **A faithful `startswith` model.**
This is the same tier as R2d (mutual-recursion) and R3 (hval carrier swap): a multi-capability
emitter build, NOT a bounded increment. **Disposition: CERTIFIED-BOUNDARY-as-bounded; authorize
first.** No silent vacuity exists in the booked corpus from R2b's int-only fold — a string element
TYPE-FAILS at L3-tc (caught), it does not int-hash silently.

**Bounded Phase-2 frontier is now EXHAUSTED** (R2a/R2b landed; self-state vacuity gate landed; R2c
grammar, R2d, R2e, R3 all session-scale / authorize-first). Per driver §A.3 the run stops early.
