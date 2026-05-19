# PyCSL Formal Semantics — Master Plan (Final)

> **Traceability note:** This is the reviewed and corrected final version.
> The original plan is preserved unchanged at `formal-semantics-plan.md`.
> All changes are annotated with `[REVISED]` or `[ADDED]`.

## 1. Purpose

Mechanize the semantics of PyCSL: prove that the weakest-precondition (WP) calculus
at the core of the IR pipeline is **sound** with respect to a structural operational
semantics (SOS) of the Python subset that PyCSL supports.

The proof is carried out in two independent theorem provers — **Rocq** (primary) and
**Lean 4** (secondary port) — so that:

- The result is independently verifiable by two different trusted kernels.
- Each prover's specific strengths are exploited (Rocq's proximity to Why3; Lean's
  `omega` tactic and macro system for contract syntax embedding).

---

## 2. Scope

### 2.1 In scope (Track 1 — hoare model only)

| Category | Constructs |
|----------|-----------|
| **Statements** | assign, augmented assign, array write, sequence, if/else, while, for, return, pass, continue |
| **Contract expressions** | arithmetic, comparison, boolean, implication (`==>`), biconditional (`<=>`), quantifiers (`\forall`, `\exists`), `\result`, `\old`, `\length(arr)`, `arr[i]` |
| **Function specifications** | `requires`, `ensures`, `assigns \nothing \| var-list` |
| **Loop annotations** | `loop invariant`, `loop variant`, function `\variant` |

### 2.2 Explicit non-goals (deferred to Track 3)

- Typed/store memory models (`\valid`, `\separated`, heap reasoning)
- Ghost variables and program-point labels (`#@ ghost`, `#@ label`, `\at`)
- Class invariants and record types
- Exceptional postconditions (`raises ExcType when cond`)
- `\diverges`, `\trusted`, structural variants
- Array region frame conditions (`assigns arr[lo..hi]`)
- Built-in predicates: `\is_sorted`, `\sum`, `\length2d`, `\valid2d`
- String literals and 2D arrays

> **[ADDED]** The formal semantics covers only *fully annotated* PyCSL programs:
> every `while` loop must carry an explicit invariant and variant in the AST.
> Unannotated Python programs are outside scope. The `SWhile` constructor
> in the `stmt` inductive carries `inv` and `var` fields; there is no constructor
> for unannotated loops.

---

## 3. Architecture — Three Tracks

```
Track 1: Rocq (primary)              Track 2: Lean 4 (port)
  Phase 0  Scope                       Phase L0  AST port
  Phase 1  AST in Gallina              Phase L1  State & evaluation
  Phase 2  State & evaluation          Phase L2  SOS as Lean Prop
  Phase 3  Structural Operational      Phase L3  WP calculus
           Semantics (SOS)             Phase L4a While invariant lemma
  Phase 3b For-loop desugaring         Phase L4b Soundness proof
  Phase 4  WP calculus                 Phase L5  (bonus) #@ syntax macros
  Phase 5a While invariant lemma
  Phase 5b Soundness theorem

Track 3: Extensions (post-port)
  Phase 6  Typed/store memory models
  Phase 7  Module 6 transpiler connection
  Phase 8  Ghost variables
  Phase 9  Class invariants and record types
```

> **[REVISED]** Track 2 phases L4a and L4b were split (previously a single L4) to
> mirror the Rocq Phase 5a/5b split. `while_inv_preserved` and `pycsl_soundness` are
> the two hardest proofs; each deserves its own gate criterion.

**Sequencing rule:** Track 2 begins only after all `Admitted` blocks in Track 1 are
closed. Track 3 begins after Track 2 is complete.

> **[ADDED]** **Exploratory exception:** a lightweight parallel Lean prototype may be
> run through Phase L3 (WP definition only, with `sorry`) while Rocq Phase 5a is in
> progress, solely to validate Lean build infrastructure and termination checker
> behaviour. This exploratory work is not merged until Rocq is `Admitted`-free. The
> gate for *merging* Track 2 remains after Track 1 is complete.

---

## 4. Core Data Model

Four layers of types underpin both the Rocq and Lean implementations:

### 4.1 Expressions (two-tier design)

PyCSL enforces a strict separation between runtime expressions and contract
expressions. The formal model mirrors this with two independent inductive types:

- **`expr`** — Runtime Python expressions: integer literals, variables, array
  subscript, binary arithmetic, unary negation. No logical connectives, no `\result`,
  no `\old`.
- **`contract_expr`** — Full logical language: everything in `expr` plus comparison
  operators, boolean connectives, implication, biconditional, quantifiers, `\result`,
  `\old`, `\length`.

> **[ADDED]** `\forall` and `\exists` quantify over integer-valued variables only
> (bound via `VInt`). Array-valued quantified variables are not supported in Track 1.

### 4.2 Statements

A single `stmt` inductive with constructors: `SSkip`, `SAssign`, `SAugAssign`,
`SArraySet`, `SSeq`, `SIf`, `SWhile` (carrying invariant + variant), `SFor`
(syntactic sugar), `SReturn`, `SContinue`.

> **[ADDED]** `SWhile` carries `inv : contract_expr` and `var : contract_expr` as
> mandatory fields. This means the formal model represents only annotated while loops.
> Every `SWhile` node in a Track 1 program must have been produced from a fully
> annotated PyCSL source.

### 4.3 Values and State

- `val` = `VInt Z | VArray (list Z)` — all runtime values are integers or flat
  integer arrays.
- `state` = association list `(ident × val)` — maps variable names to values.

### 4.4 Execution Outcomes

```
outcome = ONormal state | OReturned state val | OContinued state
```

This three-way outcome avoids the need for exception-based control flow in the
meta-language.

---

## 5. The Soundness Theorem (Goal Statement)

```
∀ (st : state) (s : stmt) (Q : state → Prop) (out : outcome),
  exec st s out →
  wp s Q st st →
  match out with
  | ONormal st'     => Q st'
  | OReturned st' _ => Q st'
  | OContinued _    => True
  end.
```

> **[ADDED — dual `st` explanation]** `wp` has type
> `stmt → (state → Prop) → state → state → Prop`. The third argument is `pre_st`
> (the entry state, used to evaluate `\old` sub-expressions in contracts); the
> fourth is the current state. At the top-level call site both are `st` — the initial
> state before the statement executes. They diverge only inside `eval_contract` when
> evaluating `\old e`, which evaluates `e` in `pre_st` rather than the current state.
> In all WP rules, `pre_st` is threaded through unchanged.

> **[ADDED — `SReturn` and `\result`]** In the `OReturned st' v` branch the
> postcondition receives `st'`. To allow postconditions that reference `\result`, the
> returned state `st'` is defined to include a binding `"\result" → v`. Concretely:
> `wp (SReturn e) Q pre_st st = Q (update st "\result" (eval_expr st e))`.
> The `\result` key is reserved and cannot appear as a program variable.

> **[ADDED — `OContinued` explanation]** The `OContinued _` branch yields `True`
> (the WP is vacuously satisfied for `continue`). This is correct because `SContinue`
> only appears inside loop bodies. The loop's invariant is re-checked at the top of
> each iteration by the `SWhile` WP; the body's WP need not enforce the postcondition
> for the interrupted control path.

**The keystone sub-lemma is `while_inv_preserved`**, proved by well-founded induction on
the variant value.

> **[ADDED — variant non-negativity]** The `SWhile` WP includes three conjuncts:
> (1) the invariant holds in the initial state, (2) for any state satisfying the
> invariant and the guard, executing the body preserves the invariant *and* strictly
> decreases the variant *and* the variant is non-negative, (3) the postcondition `Q`
> holds in any state where the invariant holds and the guard is false.
> The non-negativity clause in conjunct (2) is required for well-founded induction
> on `Z` to fire in Phase 5a/L4a.

---

## 6. CMMI Process Areas Alignment

This project follows a CMMI-inspired process structure across both prover
implementations:

| CMMI PA | Mapping in this project |
|---------|------------------------|
| **Requirements Management (REQM)** | Scope defined in §2; each phase has an explicit deliverable (see §7) |
| **Project Planning (PP)** | This plan; prover-specific plans in `rocq/rocq-plan-final.md` and `lean/lean-plan-final.md` |
| **Project Monitoring & Control (PMC)** | Phase gates: each phase must compile without errors before the next begins |
| **Configuration Management (CM)** | One `.v` / `.lean` file per phase; no cross-phase dependencies except imports |
| **Process & Product Quality Assurance (PPQA)** | Proof obligations: zero `Admitted`/`sorry` at phase completion |
| **Verification (VER)** | `coqc` / `lean --run` on every file; CI integration via `Makefile` |
| **Validation (VAL)** | Test lemmas: concrete evaluation of example programs against expected outcomes |

### 6.1 Phase Gate Criteria

A phase is **complete** when:

1. All `.v` or `.lean` files in the phase compile without warnings.
2. No `Admitted` (Rocq) or `sorry` (Lean) remains in the phase's files.
3. The phase's test lemmas (concrete evaluation tests) all pass.
4. The phase's deliverable is documented in the prover-specific plan.

### 6.2 Traceability

Each file in the Rocq and Lean trees maps to exactly one phase. The prover-specific
plans (`rocq/rocq-plan-final.md`, `lean/lean-plan-final.md`) contain a file-by-file
traceability table linking every source file to its phase, its purpose, and its
upstream dependency.

---

## 7. Phase Deliverables Summary

| Phase | Deliverable | Success Criterion |
|-------|-------------|-------------------|
| 0 | Scope document | Reviewed, no open questions |
| 1 | AST definitions | Compiles; test: construct and pattern-match example AST |
| 2 | State model + evaluators | Compiles; test lemmas: eval concrete programs |
| 3 | SOS relation | Compiles; `exec_deterministic` proved |
| 3b | For-loop desugaring | `desugar_correct` proved (with freshness precondition) |
| 4 | WP calculus | Compiles; structural recursion accepted; `SReturn` binds `\result` |
| 5a | While invariant lemma | `while_inv_preserved` proved (no `Admitted`); non-negativity is explicit hypothesis |
| 5b | Soundness theorem | `pycsl_soundness` proved (no `Admitted`) |
| L0–L3 | Lean port phases | All Lean files compile |
| L4a | Lean while invariant lemma | `while_inv_preserved` proved (no `sorry`) |
| L4b | Lean soundness theorem | `pycsl_soundness` proved (no `sorry`) |
| L5 | Syntax macros | Example annotated function type-checks via macros |

> **[REVISED]** Phase 3b success criterion now requires the freshness precondition
> `fresh "_pycsl_idx" s` to appear in the theorem statement (not merely in the proof).
> Phases L4a and L4b are new (split from original L4).

---

## 8. Directory Structure

```
src/formal-semantics/
├── formal-semantics-plan.md          ← original plan (preserved, do not modify)
├── formal-semantics-plan-final.md    ← this file
├── rocq/
│   ├── rocq-plan.md                  ← original Rocq plan (preserved)
│   ├── rocq-plan-final.md            ← reviewed Rocq plan
│   ├── Makefile                      ← coqc build rules
│   ├── _CoqProject                   ← Rocq project file
│   ├── Phase1_AST.v                  ← binop, expr, contract_expr, stmt, func_spec
│   ├── Phase2_State.v                ← val, state, lookup, update, eval_expr,
│   │                                    eval_contract, eval_variant
│   ├── Phase3_SOS.v                  ← outcome, exec relation, exec_deterministic
│   ├── Phase3b_Desugar.v             ← desugar, desugar_correct (with freshness)
│   ├── Phase4_WP.v                   ← wp fixpoint (SReturn binds \result)
│   ├── Phase5a_WhileInv.v            ← while_inv_preserved
│   ├── Phase5b_Soundness.v           ← pycsl_soundness
│   └── Tests.v                       ← concrete evaluation test lemmas
└── lean/
    ├── lean-plan.md                  ← original Lean plan (preserved)
    ├── lean-plan-final.md            ← reviewed Lean plan
    ├── lean-toolchain                ← pinned Lean version (e.g. leanprover/lean4:v4.12.0)
    ├── lakefile.lean                 ← Lake build (Mathlib pinned to release tag)
    ├── PyCSL/
    │   ├── AST.lean
    │   ├── State.lean
    │   ├── SOS.lean
    │   ├── DesugarDef.lean           ← pure desugar transformation (no SOS import)
    │   ├── Desugar.lean              ← desugar_correct (imports SOS)
    │   ├── WP.lean                   ← wp + wpFor helper for SFor termination
    │   ├── WhileInv.lean             ← while_inv_preserved
    │   ├── Soundness.lean            ← pycsl_soundness
    │   ├── Macros.lean               ← (bonus) #@ syntax embedding
    │   └── Tests.lean
    └── PyCSL.lean
```

---

## 9. Risk Register

| Risk | Impact | Mitigation |
|------|--------|------------|
| While-invariant mutual induction blocked | High — blocks Phase 5a and all downstream | Prototype proof sketch in Rocq first; use `measure` or `Function` if structural induction fails |
| Lean termination checker rejects `wp` for `SFor` | Medium — blocks Phase L3 | Use `wpFor` helper definition (see Lean plan §4.4); structural recursion on remaining cases is preserved |
| For-loop desugaring introduces fresh variable capture | Low — blocks Phase 3b | Use reserved name `_pycsl_idx`; theorem carries `fresh "_pycsl_idx" s` as explicit precondition |
| Scope creep from Track 3 features | Medium — delays completion | Strict phase gates; no Track 3 work until Track 2 is `sorry`-free |
| Variant non-negativity unprovable from invariant | Medium — blocks Phase 5a | WP for `SWhile` includes explicit `eval_variant ≥ 0` conjunct; this is an annotation obligation on the programmer |
| Lean exploratory prototype diverges from final Rocq design | Low | Exploratory prototype is `sorry`-heavy and not merged; it informs infrastructure only |

---

## 10. References

- `form/01-global-plan.md` — Original global plan with full Rocq code sketches
- `form/02-Rocq.md` — Detailed Rocq implementation with all Phase 1–5b code
- `form/03-Lean.md` — Lean 4 port specification with Phase L0–L5 code
- `config/skills/pycsl-software-architecture/SKILL.md` — Pipeline architecture
- `config/skills/rocq-prover/SKILL.md` — Rocq proof tactics reference
- `config/skills/pycsl-annotate/SKILL.md` — Contract syntax and annotation rules
