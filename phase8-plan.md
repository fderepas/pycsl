# phase8-plan.md — Specification for Phase 8 (Lambda / higher-order)

> **Scope.** Phase 8 of the formal-semantics roadmap (`formal-semantics-completion.md`
> §2, "Lambda — Category A, optional") plus its alignment with the real PyCSL
> pipeline and the reference corpus. This file is the executable specification:
> work items, acceptance gates, non-goals, sequencing.
>
> **Convention notes.** Named repo-root plan file (per project convention). New
> PyCSL-feature plans must extend `test-suite/corpus/pycsl-reference/` — WI-7
> below. Follow the leaf-first / faithful-semantics doctrine: model each Python
> value at its faithful WhyML type, do not coerce to `int`.

---

## 0. Current status (measured, not assumed)

Phase 8 is **partially landed and asymmetric** between the two sides:

**Formal model — a defunctionalized closure model exists but is source-unreachable.**
- `VClosure (param : ident) (body : stmt) (closure : list (ident*val))` — a reified
  single-parameter closure value (`Phase2_State.v:21`; `State.lean`).
- `SCall (result : ident) (fn : expr) (arg : expr)` — a statement-level call
  (`Phase1_AST.v:277`; `AST.lean`). `ELambda` is *deliberately not* in `expr`
  (keeps `expr`/`stmt` non-mutually-recursive — see the `Phase1_AST.v` comment).
- WP arm (`Phase4_WP.v:182`; `WP.lean:140`): a **closed behavioural formula** —
  `match eval_expr fn with VClosure p b c => (∀ st' v, exec (c[p↦arg]) b (OReturned st' v) → Qn (es[r↦v])) | _ => True`.
- SOS `ExecCall` (`Phase3_SOS.v:388`), soundness case (`Phase5b_Soundness.v:159,457`),
  `exec_deterministic` case — all **proved, 0 Admitted / 0 sorry**.
- **The gap:** `eval_expr` never *produces* a `VClosure` (there is no lambda-
  construction construct and no `ELambda`), so no source program can bind a
  closure. The `VClosure` branch of `SCall` is therefore **unreachable from
  source** — the model is sound but *vacuous* with respect to real programs.
  Also: **single parameter only** (`param`/`arg`), whereas Python lambdas are
  n-ary.

**Real tool — ahead, and using a different representation.**
- Front-end parses `lambda a, b: e` → IR `{"type":"Lambda","params":[…],"body":…}`
  (`Module5_IREmitter.py:1025`).
- Module 6 lowers it to a **first-class WhyML `fun`** value:
  `f = lambda x, y: x+y` ⟶ `fun (x:int)(y:int) -> (x+y)` (`_handle_lambda_expr`,
  `expressions.py:3222`; `_lambda_locals`; `find_lambda_vars`). n-ary, expression-level.
- Documented: `annotations.md §7.5`. Corpus: `pycsl-reference/0242.py` (single-param),
  `0243.py` (present). Both are single-thread integer lambdas.

**Consequence.** There are *two inconsistent lambda semantics* in the repo: the
formal **defunctionalized single-arg `SCall`/`VClosure`** and the tool's
**n-ary WhyML `fun`**. They are not connected (a LINK-1 gap specific to lambda),
and the formal one is source-unreachable. Phase 8's job is to make lambda
**faithful, reachable, and consistent** across the model, the tool, the corpus,
and the docs — or to explicitly and honestly bound what stays out of model.

---

## 1. Objective

Deliver a lambda/higher-order model that is (a) **reachable** from source in the
formal semantics, (b) **faithful** to Python lambda semantics (n-ary, lexical
capture, first-class), (c) **consistent** between the formal model and the
tool's Module-6 lowering (LINK 1), and (d) **assured** by soundness proofs
(0 Admitted / 0 sorry, unchanged trust base), reference-corpus tests, and a
soundness-report classification. Keep the roadmap's "optional" status honest:
scope the *minimum reachable+sound* core as mandatory (Stage A) and the richer
capabilities (n-ary, capture, higher-order-in-contracts) as staged follow-ons.

---

## 2. The central design decision

> **✅ DECISION (human reviewer, 2026-07-01): Option 1.** The human reviewer has
> selected **Option 1** — the defunctionalized construction statement `SLambda`
> — as the Phase-8 lambda-construction mechanism. Rationale: strictly additive to
> the proved core (leaf construct, SOS≡WP, `exact Hwp`, 0 new axioms), reachable
> immediately, keeps `expr`/`stmt` non-mutually-recursive, and defers function
> equality / higher-order-in-contracts rather than forcing them. Execution below
> follows Option 1. (Multi-arg is handled by currying — WI-2's documented
> alternative — to keep the change strictly additive to the proved single-param
> `SCall`/`VClosure`.)

**How is a closure constructed in the formal AST?** Three options; the plan
**recommends Option 1** (least invasive, aligns with the existing defunctionalized
`VClosure`, keeps `expr`/`stmt` non-mutually-recursive):

| Option | Construct | Pros | Cons |
|---|---|---|---|
| **1 (recommended)** | A **statement** `SLambda (x : ident) (params : list ident) (body : stmt)` that binds `VClosure` into `reg_state` at `x` (defunctionalized; body captured by *reference to the current reg_state*). | No `expr`/`stmt` mutual recursion; reuses `VClosure`/`SCall`; construction is a leaf state update (easy soundness, mirrors Phase-6 field pattern). | Lambdas are statements-bound-to-a-name, not arbitrary sub-expressions (matches how the corpus already writes them: `f = lambda …`). |
| 2 | Add `ELambda` to `expr`; `eval_expr (ELambda …) = VClosure …`. | Expression-level, closest to Python. | Makes `expr` depend on `stmt` (mutual recursion) → re-proves termination/`wp_mono`/`eval_expr` totality; high blast radius. |
| 3 | Keep tool's WhyML-`fun` representation; add a `fun`-typed value + application to the formal model. | Matches the tool exactly (no LINK-1 gap). | Higher-order WhyML values in the shallow model complicate `wp_mono` and the evaluator-axiom boundary; larger than Option 1. |

**Recommended shape (Option 1).** Model `f = lambda a,b: e` as
`SLambda "f" ["a";"b"] (SReturn e)` binding `VClosure`-with-`params`, and
`r = f(x,y)` as `SCall "r" (EVar "f") [EVar "x"; EVar "y"]` (n-ary — see WI-2).
This is defunctionalized, reachable, and a strict extension of what's already proved.

---

## 3. Work items

### WI-1 — Lambda construction construct (formal, both provers) [MANDATORY]
Add `SLambda x params body` to `stmt` (`Phase1_AST.v`; `AST.lean`), with:
- SOS `ExecLambda`: `exec es (SLambda x ps b) (ONormal (set_reg es (update reg x (VClosure ps b reg))))`
  (capture = snapshot of the current `reg_state`).
- WP arm: `wp (SLambda x ps b) Qn … es = Qn (es[x ↦ VClosure ps b es.reg_state])`.
- Soundness case: identical shape to `SAssign` (SOS outcome ≡ WP term ⟹ `exact Hwp`).
- `exec_deterministic` case; `wp_mono` case (the bound value is closed, like `SCall`).

**Acceptance:** both provers compile; `pycsl_soundness`/`pycslSoundnessVerified`
re-proved; `Print Assumptions` / `#print axioms` unchanged (only the existing
classical axioms).

### WI-2 — Generalise `VClosure`/`SCall` to n-ary [MANDATORY]
Python lambdas are n-ary. Change `VClosure param body cstate` →
`VClosure (params : list ident) body cstate`, and `SCall r fn arg` →
`SCall r fn (args : list expr)`. Bind parameters positionally
(`fold_left update cstate (zip params (map eval args))`); arity mismatch ⟹ WP
`True` / SOS stuck (sound over-approximation). Re-prove the `SCall` WP arm, SOS
`ExecCall`, and soundness case with the list-bind. **Alternative** (smaller
diff, if n-ary proves heavy): keep single-arg and desugar `f(x,y)` via currying
(`SLambda` returns nested closures) — document whichever is chosen.

**Acceptance:** both provers compile; soundness re-proved; a 2-arg call test
lemma evaluates.

### WI-3 — Non-vacuity / reachability witness [MANDATORY]
The Phase-6/7 discipline: prove the model is *live*. A theorem that a concrete
program `SLambda "f" ["a"] (SReturn (EBinop OpAdd (EVar "a") (EInt 1)))` then
`SCall "r" (EVar "f") [EInt 5]` yields `r = 6` — i.e. the WP forces
`lookup reg "r" = VInt 6` — **proved with no axioms** (`Closed under the global
context` / `does not depend on any axioms`). This is the source-reachable
counterpart of the Phase-6 field read-back; it demonstrates the `VClosure`
branch is no longer vacuous.

### WI-4 — Determinism, capture, and shadowing lemmas [SHOULD]
- Capture faithfulness: the closure sees the defining state, not the call-site
  state (`SLambda` snapshots `reg_state`; prove a call observes the captured binding
  even after the outer variable is reassigned).
- Recursion is **out of scope** by construction (an `SLambda`-bound name is not in
  its own captured `cstate`); document this as a deliberate non-goal (WI-9).

### WI-5 — LINK 1 alignment decision (tool ↔ formal) [MANDATORY, design]
Resolve the two-representation mismatch. Pick one and record it in
`ir-schema-spec.md` + `arm-coverage.md`:
- **(5a) Align the tool to the defunctionalized model** — Module 6 keeps emitting
  WhyML `fun`, but the IR `LambdaIR`/`CallIR` sums align constructor-by-constructor
  with the formal `SLambda`/`SCall` (as the Phase-A/B typed-IR migration did for
  other constructs), and a note records that WhyML-`fun` is the *lowering* of the
  same abstract construct the formal model defunctionalizes. **Recommended.**
- **(5b) Document an audited representational boundary** — if full alignment is
  deferred, state explicitly (in `evaluator-axiom-audit.md` and the soundness
  report) that lambda's tool-lowering (WhyML `fun`) is trusted-by-design and NOT
  covered by the formal `SCall` soundness. Honest, but weaker.

**Acceptance:** the chosen story is written; if 5a, the LINK-1 constructor map
includes `SLambda`/`SCall` and the extraction byte-diff (LINK 2) still passes.

### WI-6 — Soundness-report classification [MANDATORY]
Classify lambda as **Interpreted / Shimmed / Ignored** in the soundness report
(the two-plane convention). Runtime plane: the `pycsl_lib` behaviour of a called
lambda (if any shim is needed). Static plane: what the VC actually proves. State
the divergence explicitly.

### WI-7 — Reference corpus [MANDATORY]
Extend `test-suite/corpus/pycsl-reference/` beyond the existing `0242.py`
(single-arg identity-ish) and `0243.py`:
- multi-param lambda (`lambda a,b: a+b`) with `requires`/`ensures`;
- a lambda that **captures** an outer variable (lexical capture faithfulness);
- a lambda **passed as an argument** and called (first-class);
- a lambda **returned** from a function (escape) — or document as non-goal if the
  defunctionalized model can't express escape;
- a **negative** case: arity mismatch / calling a non-lambda — expected `FAIL`
  or vacuous, per the chosen semantics.
Each corpus file: standalone, `assert`-checked `__main__`, `pycsl`-clean, and
(per WI-8) a formal test that CALLS the API and observes a consequence, never
simulates internals.

### WI-8 — Conformance + non-vacuity gates [MANDATORY]
- The new corpus files pass `pycsl` (byte-diff/extraction sweep parallelised per
  `bin/byte-diff-sweep.sh`).
- A formal test per the "test = observable consequence" doctrine: build a lambda,
  call it, observe the returned value (not the closure's own return code).
- Non-vacuity check on the emitted VC (a false postcondition must FAIL) so the
  lambda VC isn't vacuously green.

### WI-9 — Docs reconciliation [MANDATORY]
- `formal-semantics-completion.md` §2 Phase 8: add a "Status (done)" block
  mirroring the Phase 6/7 style; flip the §10-summary Category-A Lambda row.
- `src/formal-semantics/README.md` §10 Category A Lambda: ❌ → ✅ with the
  defunctionalized `SLambda`/n-ary `SCall` description, 0-new-axiom note, and the
  WI-3 non-vacuity witness; update §5 WP table (`SLambda`, `SCall` rows) and §2.2
  non-goals (remove Lambda; keep recursion/escape if deferred).
- `annotations.md §7.5`: reconcile the documented WhyML-`fun` lowering with the
  chosen LINK-1 story (WI-5).

---

## 4. Gate criteria (Phase 8 "done")

1. **Both provers green**: Rocq `make` clean, Lean `lake build` clean; **0 Admitted / 0 sorry**.
2. **Trust base unchanged**: `Print Assumptions pycsl_soundness` / `#print axioms
   pycsl_soundness` show only the pre-existing classical axioms — **0 new axioms**
   from Phase 8. (Same bar met by Phases 6 and 7.)
3. **Reachable + non-vacuous**: WI-3 witness proved with no axioms.
4. **LINK preserved**: extraction byte-diff (LINK 2) still 26/26 (or its current N);
   LINK-1 constructor map updated if 5a.
5. **Corpus + conformance**: WI-7 files `pycsl`-clean; WI-8 formal tests pass and
   the false-postcondition non-vacuity check FAILs as expected.
6. **Docs reconciled**: WI-9 complete; no stale "Lambda ❌ not in AST" claims remain.

---

## 5. Non-goals (explicit, honest)

- **Recursion / named recursive lambdas** — the defunctionalized `SLambda`
  snapshots the defining state and does not bind its own name in the closure;
  Python `lambda` is anonymous and non-recursive anyway. Recursive *functions*
  are a separate concern (function-def semantics), not Phase 8.
- **Escaping closures that outlive their captured locals**, if Option 1's
  snapshot model can't express them soundly — document as a bounded non-goal
  rather than force an unsound rule.
- **Higher-order values inside contracts** (`\forall f, …`, function-valued
  ghost state) — out of the WP calculus's current expression language; a
  possible Phase 8+.
- **`ELambda` as an arbitrary sub-expression** (Option 2) — deferred unless a
  concrete need arises; the `f = lambda …` statement form (Option 1) covers the
  corpus and the documented syntax.
- **The tool's WhyML-`fun` optimisation** is a lowering choice; Phase 8 does not
  require replacing it, only aligning/auditing it (WI-5).

---

## 6. Sequencing, risk, effort

```
Stage A (MANDATORY core):  WI-1 (SLambda) → WI-3 (non-vacuity witness) → WI-6/WI-9(partial)
                           [reachable, sound, single-arg; proves the model is live]
Stage B (faithful n-ary):  WI-2 (n-ary VClosure/SCall) → WI-4 (capture) → corpus WI-7/WI-8
Stage C (alignment):       WI-5 (LINK-1 decision) → WI-9 (full docs) → gate §4
```

| Item | Effort | Risk | Note |
|---|---|---|---|
| WI-1 `SLambda` | Low–Med | Low | mirrors `SAssign`; SOS≡WP ⟹ `exact Hwp` |
| WI-2 n-ary | Med | Med | list-bind re-proofs; currying fallback available |
| WI-3 witness | Low | Low | Phase-6/7 pattern |
| WI-5 LINK-1 | Med | Med | design decision; touches IR schema + byte-diff |
| WI-7 corpus | Low–Med | Low | must CALL the API; capture/first-class cases |
| WI-9 docs | Low | Low | Phase 6/7 doc pattern |

**Overall:** Stage A is a few-hours, low-risk increment that removes the
"source-unreachable / vacuous" blemish and is worth doing even if Phase 8 stays
"optional." Stages B–C are the faithful-and-consistent completion. Total: a
bounded multi-session effort, strictly additive to the proved core (no
`pycsl_soundness` restatement), matching the Phase 6/7 playbook.

---

## 7. Definition of the smallest shippable slice

If only one thing ships: **Stage A** — `SLambda` construction (WI-1) + the
non-vacuity witness (WI-3) + minimal docs (WI-9 partial). That alone converts the
formal lambda model from "present but source-unreachable/vacuous" to
"reachable, live, and proved," which is the single highest-value Phase-8 step and
the honest precondition for claiming any lambda soundness at all.
