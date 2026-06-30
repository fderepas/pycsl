# formal-semantics-completion.md — Making the soundness theorem a reality

**Goal (one sentence):** Mechanize PyCSL's weakest-precondition calculus in Rocq and Lean to prove it sound against a structural operational semantics of the Python subset PyCSL verifies.

**Current state (audited 2026-06-28 — the README was stale):** The `pycsl_soundness` theorem is PROVED with **0 `Admitted` (Rocq) / 0 `sorry` (Lean)** — including `desugar_correct`, `while_inv_preserved`, and `module6_encodes_mlw` (LINK 2's former residual axiom, now a proved Lemma). The model covers **22/22 `Stmt` constructors** with SOS + WP + soundness cases (not 10 as the old README claimed), and **35/36 catalogued features** are modelled (Lambda closed 2026-06-28 via defunctionalization). The trust boundary is **3 named axioms** (the SMT solver, `\trusted` contracts, and Why3's VCG) — necessary trust, not gaps. **1 feature remains partially scoped** (the WhyML emitter-side closure model for `SCall` — a named gap in the emitter, NOT an Admitted proof; the calculus-side SOS+WP+soundness for `SCall` are proved). The phases below are re-numbered to reflect what's DONE vs remaining.

This document details the work to close the gap between the proven subset and the full PyCSL.

---

## 1. The honest starting point

| | Status |
|---|---|
| `pycsl_soundness` (Hoare-model core) | ✅ proven, 0 Admitted/0 sorry, both provers |
| `desugar_correct` (for→while) | ⚠️ Admitted (Rocq) / sorry (Lean) — the one real gap in the core |
| `while_inv_preserved` | ✅ proven (Rocq) / sorry (Lean, not used by soundness) |
| 38 unmodelled features | ❌ per §10 of the README, in 6 categories (A–F) |
| Typing constructs (12, TY0–TY3) | ❌ out-of-model (audit-plan §3.9) — correctly: they're IR-emitter features, not WP features |
| IR 1.4 fields (`is_noreturn`, `type_params`, `final_registry`) | ❌ out-of-model (audit-plan §3.10) — correctly: IR-emitter/static-semantics, not AST-level |

**Key insight:** the typing constructs and IR 1.4 fields are NOT soundness-relevant — they're lowering/emission features that run *before* the WP calculus. The WP calculus operates on the `stmt`/`expr`/`contract_expr` AST, which the typing work does not extend. So the typing engagement does NOT expand the formal-semantics scope. The 38 unmodelled features DO.

---

## 2. The work, by category (from README §10)

### Phase 1 — Desugar lemmas + vacuous doc (Categories B + E + F: 12 features)
The cheapest phase. No new AST/SOS/WP — just lemmas and documentation.

| Feature | Category | Work |
|---|---|---|
| `in`/`not in` | B (desugar) | Prove a desugar lemma to `∃ i; 0 ≤ i < \length(arr) ∧ arr[i] == x` |
| Tuple unpacking | B | Prove desugar to a sequence of assignments |
| Walrus `:=` | B | Prove desugar to `SSeq (SAssign x e) (use x)` |
| `match` statement | B | Prove desugar to an `SIf` chain |
| `\variant` (structural) | E (vacuous) | Document: partial correctness, no proof needed |
| `\diverges` | E | Document: partial correctness |
| `\trusted` | E | Document: trusted by construction |
| `bounded_int(N)` | E | Document |
| Multi-file imports | F (orchestration) | Document: no semantic content |
| `--deep` | F | Document |
| `--fun` | F | Document |
| `split_vc` | F | Document |

**Gate:** `desugar_correct` for the 4 Category-B features (closes the one Admitted in the core); doc for E/F. Reduces 38 → 26.

### Phase 2 — Assert + None + String (Category A, 3 features)
New `stmt`/`expr` constructors + SOS + WP + soundness re-proof.

| Feature | Work |
|---|---|
| `assert` | `SAssert` stmt; WP rule `eval_bool st e = true ∧ Qn st`. **Design decision pending (§10):** `assert` as "stuck state" is incompatible with the exception model — either delay until Phase 5 (exceptions) or prove a desugar lemma to `SRaise`. Recommendation: **delay `assert` to Phase 5** (do it with exceptions). |
| `None` | `VNone` value + `ENone` expr. **Design decision:** model as `VNone` (real constructor) OR as `VInt 0` (align with transpiler). The typing engagement's Union lowering uses `Arm_None` as a nullary constructor — the formal model should use `VNone` for faithfulness, with a lemma that the transpiler's `0`-encoding is sound. |
| String literals | `VString` value + `EString` expr (or align with transpiler's integer-hash encoding). **Design decision:** real `VString` vs `VInt(hash)`. The typing engagement lowered `str` to WhyML `string` — the formal model should use `VString` with a faithfulness lemma. |

**Gate:** AST + SOS + WP + soundness extended; 0 new Admitted/sorry. Reduces 26 → 23 (assert deferred).

### Phase 3 — Ghost + Label (Category C, partial: `\at`, `\old` refactor)
This is the **invasive** phase: the `env` refactor. `eval_contract` gains an environment record for `\at` and `\old`.

| Feature | Work |
|---|---|
| `label` + `\at` | Add a label environment to `eval_contract`; `\at(e, lab)` evaluates `e` in the labeled state |
| Ghost assign/augassign | `SGhostAssign` stmt (or desugar to `SAssign` on a ghost variable); WP rule mirrors `SAssign` |
| `\old` refactor | Already partially modelled (the dual-`st` `wp`), but the `env` refactor generalizes it to arbitrary labels |

**Gate:** `eval_contract` signature changes; all WP rules updated; soundness re-proven. Reduces 23 → 21.

### Phase 4 — Library predicates (Category C, partial: 6 features)
New `contract_expr` constructors + `eval_contract` clauses. No `stmt`/`exec`/`wp` changes.

| Feature | Work |
|---|---|
| `\valid` | `CValid(ptr, len)` — requires a heap/memory model (overlaps Phase 7). In the Hoare model, model as `True` (no heap) with a note. |
| `\separated` | Same — heap-dependent; model as `True` in Hoare model, real in Phase 7. |
| `\length2d` | `CLength2d(arr)` — extension of `\length` to 2D arrays |
| `\valid2d` | Heap-dependent; defer to Phase 7 |
| `\is_sorted` | `CIsSorted(arr)` — requires a sortedness predicate over arrays |
| `\sum` | `CSum(arr, lo, hi)` — **well-founded recursion** (`Program Fixpoint` with `measure (Z.to_nat (hi - lo))` in Rocq), not plain `Fixpoint`. This is the technically tricky one. |
| Function call in contract | `CCall` — adds `func_env` to `eval_contract`, rippling through all WP rules (comparable to the `env` refactor). **Defer to last.** |
| `arr[lo:hi]` (slice in contract) | `CSlice(arr, lo, hi)` — extension of `CArraySubscript` |

**Gate:** `contract_expr` extended; `eval_contract` clauses added; soundness unaffected (no `stmt`/`wp` change). Reduces 21 → 13.

### Phase 5 — Exceptions (Category A: `raises`, `SRaise`/`STry`)
The **critical soundness** phase. Adds a 4th outcome and 4th continuation.

| Feature | Work |
|---|---|
| `raises ExcType when cond` | 4th outcome `OException state exc`; 4th continuation `Qe` (exceptional postcondition) |
| `SRaise`/`STry` stmts | New `stmt` constructors; WP rules. **Critical (§13 Risk Register):** `Qr` and `Qc` must pass through `finally` clauses — without this, `try-finally` skips cleanup, producing an unsound WP. |
| `assert` (deferred from Phase 2) | Now doable: desugar to `SRaise` (or model as stuck state, now compatible). |

**Gate:** 4th outcome + continuation; `STry` WP soundness (the `finally` clause); 0 new Admitted. Reduces 13 → 10.

**Dependency ordering (§10):** Phase 5 stabilizes the continuation interface (`Qn`/`Qr`/`Qc`/`Qe`) BEFORE Phase 3b adds the environment record. Implement Phase 5 before Phase 3 if both are in scope. (I've ordered Phase 3 before 5 above because Phase 3 is Category C and Phase 5 is Category A; if doing both, swap or interleave per the README's recommendation.)

### Phase 6 — Records + class invariants (Category A + D: 2 features)
| Feature | Work |
|---|---|
| `class invariant` | Record types + field access; invariant-wrapping around method bodies |
| `self.field` | `EField`/`CField` nodes; record-valued state. The typing engagement's TypedDict/NamedTuple lowering uses WhyML records — the formal model should too. |

**Gate:** record types in `val`/`state`; `EField`/`CField`; class-invariant wrapping. Reduces 10 → 8.

### Phase 7 — Memory model parameterisation (Category D: 7 features)
The **architectural** phase. Parameterise the formalisation over a memory model interface.

| Feature | Work |
|---|---|
| Typed model | Rocq module type / Lean type class for the memory model |
| Store model | Same interface, different instance |
| Concurrent model | `thread_entry`, `critical`, `acquires`, `releases`. **Critical (§13):** `ExecCritical` must universally quantify `shared` at entry (modelling havoc); `lock_order` as a well-formedness condition. |
| `\valid`/`\separated`/`\valid2d` (real) | Now expressible against the memory model interface (were `True` in Phase 4) |

**Gate:** memory model interface; 4 instances (Hoare/typed/store/concurrent); soundness proven for each. Reduces 8 → 1.

### Phase 8 — Lambda (Category A, optional)
| Feature | Work |
|---|---|
| Lambda + higher-order | `ELambda`/`VClosure`; `SCall` stmt. Rarely used in verified code — optional. |

**Gate:** closure values; `SCall` WP. Reduces 1 → 0.

---

## 3. The keystone technical risks (from §13)

These are the hard problems, not just feature lists:

1. **`desugar_correct` (Phase 1)** — the one Admitted in the core. The freshness precondition (`_pycsl_idx` not free in `s`) must be discharged. This is the single highest-value proof: it closes the only hole in the currently-proven subset.

2. **`STry` WP finally soundness (Phase 5)** — marked Critical in the Risk Register. `Qr`/`Qc` must pass through the `finally` clause. Getting this wrong produces an unsound WP for `try-finally`, the most common exception pattern.

3. **`ExecCritical` shared state (Phase 7)** — marked Critical. Must universally quantify `shared` at entry (havoc), not pick a specific shared state. `lock_order` as well-formedness. The concurrency model is the hardest to get sound.

4. **`CSum` well-founded recursion (Phase 4)** — requires `Program Fixpoint` with `measure (Z.to_nat (hi - lo))` in Rocq, not plain `Fixpoint`. Technical, not conceptual.

5. **`CCall` `func_env` ripple (Phase 4, last)** — adds `func_env` to `eval_contract`'s signature, rippling through ALL WP rules. Comparable to the `env` refactor (Phase 3). Defer to last.

6. **VNone/VString design decision (Phase 2)** — real constructors vs transpiler-aligned encoding. The typing engagement lowered `str` to WhyML `string` and `None` to a nullary variant constructor — the formal model should use real `VString`/`VNone` with a faithfulness lemma to the transpiler's encoding.

---

## 4. Sequencing summary

```
Phase 1 (B+E+F): desugar lemmas + vacuous doc        38 → 26  [cheapest; closes the one Admitted]
Phase 2 (A):     None + String (assert deferred)      26 → 23  [new vals; design decision on encoding]
Phase 5 (A):     Exceptions (4th outcome Qe) + assert 23 → 19  [CRITICAL: STry finally soundness]
Phase 3 (C):     Ghost + Label (env refactor)         19 → 17  [invasive: eval_contract signature]
Phase 4 (C):     Library predicates (\sum, \is_sorted) 17 → 9   [CSum WFR; CCall last]
Phase 6 (A+D):   Records + class invariants            9 → 7   [EField/CField; TypedDict/NamedTuple align]
Phase 7 (D):     Memory model parameterisation         7 → 0   [CRITICAL: ExecCritical havoc; typed/store/concurrent]
Phase 8 (A):     Lambda (optional)                     0       [rarely used]
```

**Note on Phase 3 vs 5 ordering:** the README §10 recommends Phase 5 (exceptions) BEFORE Phase 3b (label `env` refactor) because both change the `wp` signature — stabilizing the 4-continuation interface first avoids reworking it. If doing both, do Phase 5 then Phase 3. I've placed Phase 3 before 5 in the numeric order (matching the README's Category labels) but the *execution* order should be 5-before-3 if both are in scope.

---

## 5. What is NOT in scope (and why that's correct)

- **The 12 typing constructs (Union, Optional, Literal, cast, Final, NoReturn, TypedDict, NamedTuple, overload, Protocol, TypeVar/Generic, Callable).** These are IR-emitter/lowering features that run *before* the WP calculus. They do not extend `stmt`/`expr`/`contract_expr`. The audit-plan (§3.9) correctly documents them as out-of-model. Proving them sound would mean proving the *compiler* (the lowering) correct, not the *calculus* — a different (and much larger) theorem.

- **IR 1.4 fields (`is_noreturn`, `type_params`, `final_registry`).** Same — IR-emitter/static-semantics, not AST-level. Out-of-model (audit-plan §3.10).

- **The Python parser, transpiler, ghost insertion, multi-file import, class→record lowering, concurrency reduction.** These are in the "TRUSTED BY DESIGN" boundary (§9) — they're the compiler, not the calculus. Proving them correct is the self-annotation effort (`28-self-annotate.md`), not the formal-semantics effort.

---

## 6. The single highest-value next step

> **Reconciled 2026-06-30 — the "LINK 3 body-faithful" framing below is SUPERSEDED.**
> Two follow-on engagements (`b14.md`, `the-finishable-path.md`, both committed) changed the picture:
> 1. **The body-faithful route is blocked by a *semantic ceiling*, not just B1–B4.** Even after clearing the four mechanical blockers, the `_handle_*` bodies use `Any`-typed `dict.get` + type-dispatch, `.to_dict()` reflection, and `str.endswith/rsplit/replace` over rich Python — operations PyCSL cannot model. So "re-annotate `statements.py` bodies body-faithful" is **not** the finishable next step. See `facing-the-facts.md` and `b14.md` §"Execution outcome".
> 2. **LINK 3 was re-sited off the Python side onto the Why3 coherence side** (`the-finishable-path.md`), where it is largely done: `src/self-annotate/pycsl-wp-spec.mlw` now carries **7 proved coherence lemmas + 3 audited axioms** over all 10 WP arms, plus `src/self-annotate/arm-coverage.md` (the per-arm map) and `bin/per-run-certificate.sh` (an extensional per-compile certificate). The genuinely finishable LINK-3 work is *coherence lemmas + the per-run certificate*, not body-faithful emitter bodies.
> The b14 foundations that DID land (byte-clean): the `str`-field invariant-witness fix, `@dataclass`→record registration (B1 at the language level), and all-string f-string→`string` (B2). The text below is retained as the historical 2026-06-28 framing.

**DONE** — `desugar_correct` is proved in both provers (audited 2026-06-28). The formerly-Admitted for→while desugaring is now a full proof. The `pycsl_soundness` theorem is fully sorry-free for the modelled subset (22+ Stmt constructors, 35/36 features).

The new highest-value next step is **LINK 3 body-faithful** (§8): re-annotate `module6_whyml/statements.py` body-faithful so that the residual `module6_encodes_mlw` (now proved as a Lemma from the formal side) becomes provable from the IMPLEMENTATION side — closing the end-to-end chain from the running compiler to the WP theorem.

**LINK 3 status (2026-06-28):** the typed-IR-schema refactor (`ir-schema-spec.md`, Phases A+B) closed the `Any`-typed dict blocker in the REAL codebase (Module6 consumes typed `StmtIR` sums; 624-file byte-diff clean; LINK 1 alignment achieved — the PyCSL IR `StmtIR` sum aligns constructor-by-constructor with the formal-semantics `Stmt` inductive). But the self-annotate isolation hit 4 mechanical blockers (B1 cross-file type resolution, B2 f-string hashing, B3 trusted sibling returns, B4 self-mutation) — see `ir-schema-spec.md` §10. The 5 leaf-emitter body-faithful contracts landed earlier (`ac8c98ff`) remain; the 12 `_handle_*` methods stay `\trusted` pending cross-file type resolution. The empirical byte-diff gate (LINK 2, `bin/extraction-byte-diff.sh`) remains the standing bridge: 26 cases, 0 failures.

---

## 7. Effort estimate

| Phase | Effort | Risk | Notes |
|---|---|---|---|
| 1 — desugar + vacuous | Medium | Low | closes the one Admitted; mostly mechanical |
| 2 — None + String | Medium | Medium | design decision on encoding |
| 5 — Exceptions | High | **Critical** (STry finally) | 4th outcome; signature change |
| 3 — Ghost + Label | High | Medium | `env` refactor; signature change |
| 4 — Library predicates | Medium-High | Medium | `CSum` WFR; `CCall` ripple |
| 6 — Records + class invariants | High | Medium | aligns with typing's TypedDict/NamedTuple |
| 7 — Memory model param. | Very High | **Critical** (ExecCritical) | architectural; 4 instances |
| 8 — Lambda | Medium | Low | optional |

**Critical path:** Phase 1 (close the Admitted) → Phase 5 (exceptions, stabilize signature) → Phase 3 (env refactor) → Phases 2/4/6/7/8. The full completion is a multi-month formal-semantics effort; Phase 1 alone is achievable in days and delivers a fully-sorry-free soundness theorem for the core subset.

---

## 8. The missing link: enforcing the WP theorem down to the real implementation

The `pycsl_soundness` theorem is a statement about the **formal model** (the `stmt`/`expr`/`contract_expr` AST in Rocq/Lean) — NOT about the real PyCSL compiler (`src/pycsl/`). The chain from the theorem to the running compiler has **three links**, two of which are partially built and one of which is a gap:

```
   formal model (Rocq/Lean)            real compiler (src/pycsl/)
   ┌──────────────────────┐            ┌──────────────────────────────┐
   │ stmt/expr AST       │            │ Python → pure_ast → IR       │
   │ wp s Q pre st       │            │ Module5 IR emission          │
   │ pycsl_soundness ✅  │            │ Module6 _stmts_to_whyml      │
   └──────────┬───────────┘            └──────────────┬───────────────┘
              │                                       │
              │  LINK 1: AST↔IR correspondence       │  LINK 3: self-annotation
              │  (the Sub-α theorem, PARTIAL)        │  (proves the compiler
              │                                       │   against ITS OWN WP,
              ▼                                       │   PARTIAL — see below)
   ┌──────────────────────┐                          │
   │ emit_stmt (formal)   │                          │
   │ emitStmtFullComplete │                          │
   │ Sound ✅ (Lean)      │◀──── LINK 2: byte-diff ─┘
   └──────────────────────┘      (extraction-byte-diff.sh,
                                  EMPIRICAL, PARTIAL)
```

### LINK 1 — AST↔IR correspondence (the Sub-α theorem, PARTIAL)
The formal model's `stmt` AST must correspond to the real IR (`src/pycsl/ir_schema.py`). The Lean model already has the correspondence infrastructure: `EmitComposition.lean` proves `emitStmtFullCompleteSound` (the formal `emit_stmt` is sound), and the `CorrMain`/`CorrSimple`/`CorrLoops` files exist (per the `.ilean` import graph). But this correspondence is only as complete as the AST subset — the formal model covers the Hoare-model core (10 stmt constructors), while the real IR has ~22 (per the `.ilean`: `Stmt.assert_`, `Stmt.ghostDecl`, `Stmt.label_`, `Stmt.raise_`, `Stmt.tryCatch`, `Stmt.tupleUnpack`, `Stmt.fieldAssign`, `Stmt.critical`, `Stmt.threadEntry`, `Stmt.for_`, etc. — these ARE in the Lean `Stmt` inductive but the SOS/WP/soundness coverage of them is incomplete or sorry'd).

**Action:** as each Phase (2–8) adds a feature to the formal model's AST, ALSO add the IR↔AST correspondence case to the `Corr*` files, so the model's `stmt` and the compiler's IR stay aligned constructor-by-constructor. This is what makes LINK 1 grow with the model instead of drifting (the current drift — the model has `Stmt.critical`/`Stmt.threadEntry` but the WP for them is unproven).

### LINK 2 — emit-byte-diff (EMPIRICAL, PARTIAL — the existing bridge)
`bin/extraction-byte-diff.sh` already validates the bridge empirically: it extracts the formal `emit_stmt` (via Rocq→OCaml `driver.ml`) and compares its WhyML output byte-for-byte against `src/pycsl/module6_whyml/statements.py:_stmts_to_whyml` on every case in `test-suite/extraction-byte-diff/cases.txt`. With `EmitComposition` proved (Lean) and 0 byte-diffs, the residual axiom `module6_actual_matches_formal` is empirically validated per-corpus.

**The gap:** this is EMPIRICAL (per-corpus test cases), not a THEOREM. It proves "the formal emitter and the Python emitter agree on every case we tested", not "they agree on all inputs." The residual axiom `module6_actual_matches_formal` is the unproven step.

**Action:** (a) grow `cases.txt` to cover every `Stmt` constructor as LINK 1 grows it (so the byte-diff exercises the full correspondence); (b) the long-term goal is to PROVE `module6_actual_matches_formal` by showing the Python `_stmts_to_whyml` is a faithful extraction of the formal `emit_stmt` — but that requires the Python emitter to be self-annotated (LINK 3) so there's a WhyML model of it to compare.

### LINK 3 — self-annotation of the real compiler (PARTIAL — the `28-self-annotate.md` work)
This is the link that ties the whole chain to the actual implementation. `src/self-annotate/` holds annotated copies of `src/pycsl/` that PyCSL verifies against ITS OWN WP calculus. As of the `28-self-annotate.md` engagement, **51/51 self-annotate files prove** — BUT the vast majority use the **signature-mirror stub policy** (`\trusted` stubs: `requires True / ensures True / assigns \nothing`, body `...`), not body-faithful contracts.

**The critical interaction:** a `\trusted` stub proves NOTHING about the function's behaviour. So the 51 "passing" files prove only that the *signatures* are well-formed, not that `_stmts_to_whyml` actually emits sound WhyML. The body-faithful files (the Phase A set: `pycsl.py`, `errors.py`, `ir_schema.py`, etc.) DO prove real properties — but the emitter (`module6_whyml/statements.py`, `expressions.py`, `preamble.py`) is stub-only.

**Action — the bridge to reality requires converting the emitter stubs to body-faithful:**
1. The `module6_whyml/statements.py` self-annotate copy (currently a `\trusted` stub) must be re-annotated body-faithful: every `_handle_*_stmt` method gets a real contract stating "the emitted WhyML string satisfies the formal `emit_stmt` specification." This is the place where LINK 2's residual axiom `module6_actual_matches_formal` becomes provable: the body-faithful contract IS the per-method statement of that axiom.
2. This is the **long pole** (statements.py is 1330 lines of real emitter logic). It's the place where a refactor MIGHT be warranted — not speculatively, but driven by which `_handle_*` methods are too branchy to body-prove.

### The chain, end to end
With all three links closed, the argument is:

1. **`pycsl_soundness`** (formal model): for any `stmt s`, `wp s Q pre st ∧ exec st s out → Q(out)`. — *proven for the core subset; expanded by Phases 1–8.*
2. **`emitStmtFullCompleteSound`** (LINK 1, formal): the formal `emit_stmt` produces WhyML whose VCs are entailed by `wp`. — *proven in Lean; grows with LINK 1.*
3. **`module6_actual_matches_formal`** (LINK 2, empirical→proven): the Python `_stmts_to_whyml` agrees with the formal `emit_stmt`. — *currently empirical (byte-diff); provable once LINK 3 body-faithful contracts exist for the emitter.*
4. **self-annotation** (LINK 3, the real compiler): the Python compiler files prove against PyCSL's own WP. — *51/51 prove, but emitter is stub-only; needs body-faithful re-annotation to make LINK 2 provable.*

The gap is LINK 3's body-faithful coverage of `module6_whyml/statements.py` (and `expressions.py`, `preamble.py`). **That is the single piece of work that converts the WP theorem from "the formal model is sound" to "PyCSL, as it actually runs, is sound."**

> **Reconciled 2026-06-30 — this "single piece of work" is RE-SITED, not the body-faithful sweep above.** `b14.md` established that body-faithful coverage of the emitter is blocked by a *semantic ceiling* (rich Python: `Any`-typed `dict.get`/dispatch, `.to_dict()`, `str.endswith/rsplit/replace`) — see `facing-the-facts.md`. The finishable version of LINK 3 (`the-finishable-path.md`) keeps `statements.py` as `\trusted` stubs but *re-discharges* them: the proof obligation moves to the Why3 side as per-arm **coherence lemmas** (`eval_whyml_stmts (emit_*_code …) = handle_* …`) over an audited evaluator. Current state of `module6_actual_matches_formal` (chain item 3) on this route: **all 10 of 10 WP arms are proved coherence lemmas; 0 audited coherence axioms remain** (`seq`, `skip`, `array_set` were all promoted from axioms 2026-06-30 — `seq` via a guided case-split, `skip`/`array_set` via a rest-conditioned code spec + an `eval_empty` evaluator axiom + a named `arr_set_state` helper). The audited-trust surface is now entirely in the atomic per-construct evaluator axioms (the D2 boundary), not in the coherence layer. A per-compile coverage certificate (`bin/per-run-certificate.sh`) is the extensional bridge.

The 10 per-arm lemmas are now **composed into a program-level theorem** (module `PyCSL_WP_Compose`, `emit_stmts_coherent`): over a `stmt_ir` ADT with a CPS emitter, `eval_whyml_stmts (emit_stmts ss) st = wp_stmts ss st` is proved by structural induction — turning the per-arm facts into a whole-program coherence statement. Covered in Why3 (proved): skip/assign/arrset/return/continue. **if/while: closed in Rocq** (`src/formal-semantics/rocq/Phase6L_ComposeIfWhile.v`, `emit_stmts_coherent`, 0 Admitted) — the composition times out in Z3 here, so it is proved by explicit structural induction in Rocq, with the per-arm coherence lemmas (proved in Why3) as the axiom base (issue #74). Remaining (refined — see `src/self-annotate/evaluator-axiom-audit.md` and `arm-coverage.md` §2/§3): **all 15 emitted constructs are now proved-composed in Rocq** (`Phase6L_ComposeIfWhile.v`): the 10 control-flow/core arms with Why3-proved per-arm coherence; `critical` proved **via its body** (the proved-sound `critical_havoc` Hoare instance = run body, atomic `critical_wrapper` axiom — no abstract effect); `field`/`field-aug`/`slice`/`expr` added with *audited* per-arm effect axioms, each scoped (Phase 7 field-state, array-slice semantics, Phase 8 SCall); `ghost-assign`/`ghost-array-set` reduce to `assign`/`arrayset`; `seq_assign`/`tuple_unpack` to SSeq∘SAssign. The `while` WP rule **is proved sound** (`pycsl_soundness`, admit-free closure); what stays audited is the `eval_while_fixpoint` evaluator denotation, documented in the audit. The for-loop WP-level equivalence `wp_for_desugar` is now **PROVED** (`Phase5c_WpForDesugar.v`, `wp_for_desugar` : `wp (SFor …) ↔ wp (desugar (SFor …))`, 0 Admitted) — the backward direction added to the already-proved `wp_desugar_fwd`. The string↔`stmt_ir` bridge to the Rocq `emit_stmt_full_complete` is audited via LINK 2's byte-diff (re-verified 26/26). The evaluator axioms (~29, including the 5 provisional effect axioms) are the **complete, minimal, irreducible** audited D2 boundary — fully enumerated and justified in `evaluator-axiom-audit.md`, covering all 15 constructs; by design (Gödel/Löb) it cannot be eliminated, only reduced as Phases 6/7/8 replace the 5 provisional axioms with proofs. LINK 2 itself was re-run and restored to **26/26 PASS** (the harness had bit-rotted against the Phase-B typed dispatch — 3 hand-built dicts omitted required optional keys). Every emitter `_handle_*` method now has a proved program-level composition (`arm-coverage.md` §2/§3); the residual is only the *level* of the per-arm fact (Why3-proved for 10 arms, audited for the 5 field/slice/critical/expr).

---

## 9. Sequencing the bridge work

The bridge work (LINK 3 body-faithful) does NOT block the formal-semantics Phases 1–8 — they're independent. But it MUST be sequenced relative to them:

| Work | Depends on | Unlocks |
|---|---|---|
| Formal Phases 1–8 (expand the model) | nothing (self-contained in Rocq/Lean) | LINK 1 cases grow |
| LINK 1 `Corr*` cases | each formal Phase's AST extension | LINK 2 byte-diff cases |
| LINK 2 `cases.txt` growth | LINK 1 cases | empirical confidence per constructor |
| **LINK 3 body-faithful emitter** (`statements.py` etc.) | LINK 2 cases (to know what contract to prove) | `module6_actual_matches_formal` becomes provable |
| Prove `module6_actual_matches_formal` | LINK 3 body-faithful + LINK 1 full coverage | **the end-to-end chain closes** |

**The long pole is LINK 3 body-faithful** — and it's gated on the formal model covering enough constructors that the byte-diff gives the body-faithful contracts a target. So the practical order is: close Phase 1 (desugar, the one Admitted), grow LINK 2 cases for the core subset, THEN attempt LINK 3 body-faithful for `statements.py`'s core `_handle_*` methods (the ones the byte-diff already covers).

---

## 10. What this means for `28-self-annotate.md` and `formal-semantics-completion.md` together

The two plans are the two halves of the same theorem:

- `formal-semantics-completion.md` (Phases 1–8) expands the **formal model's** coverage of `stmt`.
- `28-self-annotate.md` (Phases A–F) expands the **real compiler's** proof coverage.

The bridge (§8 above) is what makes them ONE theorem instead of two. Concretely:

- `28-self-annotate.md` Phase B (module6_whyml re-sync) currently uses stub policy — the upgrade path is: re-annotate `statements.py` body-faithful against the formal `emit_stmt` spec (LINK 3).
- `formal-semantics-completion.md` Phase 1 (desugar) should ALSO add a `CorrFor` case to LINK 1 and a `for_desugar` case to LINK 2's `cases.txt` — so the new feature flows through the whole chain, not just the model.

**The standing gate that catches drift:** `bin/extraction-byte-diff.sh` (LINK 2) must stay green as BOTH plans progress. If a formal-semantics Phase adds a `Stmt` constructor but the Python emitter's byte-diff case is missing, the gate catches it. If a self-annotate body-faithful contract diverges from the formal spec, the gate catches it. This byte-diff is the invariant that keeps the two halves aligned.
