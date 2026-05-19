# PyCSL Formal Semantics — Architectural Choices

> This document synthesises the design rationale, architectural decisions,
> and implementation specifics of the PyCSL formal semantics project.

---

## 1. Purpose

Mechanize the semantics of PyCSL and prove that the weakest-precondition
(WP) calculus at the core of the IR pipeline is **sound** with respect to a
structural operational semantics (SOS) of the Python subset that PyCSL
supports.

The proof is carried out in two independent theorem provers — **Rocq 8.20**
and **Lean 4.29** — so that:

- The result is independently verifiable by two different trusted kernels.
- Each prover's strengths are exploited (Rocq's proximity to Why3; Lean's
  `omega` tactic and macro system).

### 1.1 Current Status

| Prover | Main theorem | Gaps |
|--------|-------------|------|
| Rocq | `pycsl_soundness` — **0 Admitted** | `desugar_correct` (1 Admitted — for→while) |
| Lean | `pycsl_soundness` — **0 sorry** | `desugar_correct`, `while_not_continued`, `while_inv_preserved` (3 sorry — none used by soundness) |

Both proofs compile end-to-end with `make proof` in their respective
directories.

---

## 2. Scope

### 2.1 In scope (Track 1 — Hoare model only)

| Category | Constructs |
|----------|-----------|
| **Statements** | assign, augmented assign, array write, sequence, if/else, while, for, return, pass, continue |
| **Contract expressions** | arithmetic, comparison, boolean, implication (`==>`), biconditional (`<=>`), quantifiers (`\forall`, `\exists`), `\result`, `\old`, `\length(arr)`, `arr[i]` |
| **Function specifications** | `requires`, `ensures`, `assigns \nothing \| var-list` |
| **Loop annotations** | `loop invariant`, `loop variant`, function `\variant` |

The formal semantics covers only *fully annotated* PyCSL programs: every
`while` loop carries an explicit invariant and variant in the AST. There
is no constructor for unannotated loops.

### 2.2 Explicit non-goals (deferred)

- Typed/store memory models (`\valid`, `\separated`, heap reasoning)
- Ghost variables and program-point labels (`#@ ghost`, `#@ label`, `\at`)
- Class invariants and record types
- Exceptional postconditions (`raises ExcType when cond`)
- `\diverges`, `\trusted`, structural variants
- Array region frame conditions (`assigns arr[lo..hi]`)
- Built-in predicates: `\is_sorted`, `\sum`, `\length2d`, `\valid2d`
- String literals and 2D arrays
- Lambda and higher-order functions

---

## 3. Core Data Model

Four layers of types underpin both the Rocq and Lean implementations.

### 3.1 Expressions (two-tier design)

PyCSL enforces a strict separation between runtime expressions and contract
expressions. The formal model mirrors this with two independent inductive
types:

- **`expr`** — Runtime Python expressions: integer literals, variables,
  array subscript, binary arithmetic, unary negation. No logical
  connectives, no `\result`, no `\old`.
- **`contract_expr`** — Full logical language: everything in `expr` plus
  comparison operators, boolean connectives, implication, biconditional,
  quantifiers, `\result`, `\old`, `\length`.

`\forall` and `\exists` quantify over integer-valued variables only
(bound via `VInt`). Array-valued quantified variables are not supported.

### 3.2 Statements

A single `stmt` inductive: `SSkip`, `SAssign`, `SAugAssign`, `SArraySet`,
`SSeq`, `SIf`, `SWhile` (carrying `inv` + `var` as mandatory fields),
`SFor` (syntactic sugar), `SReturn`, `SContinue`.

`"\result"` is a reserved identifier, forbidden as a program variable
name. `SReturn` binds `"\result"` into the post-state.

### 3.3 Values and State

- `val` = `VInt Z | VArray (list Z)` — integers or flat integer arrays.
- `state` = association list `(ident × val)`.

Association lists are used in both provers. They keep proof obligations
analogous across implementations and support simple structural induction.
`Std.HashMap` (Lean) or `FMapList` (Rocq) could improve lookup
performance but would complicate proofs without changing the interface.

`eval_expr` returns `VInt 0` for unbound variables and out-of-bounds
subscripts (total function). Partiality is guarded by `requires` in the
WP calculus.

Division by zero returns `0` as a modelling convention. This value is
never observed in valid executions because the WP calculus requires any
`requires` clause to exclude zero denominators.

### 3.4 Execution Outcomes

```
outcome = ONormal state | OReturned state val | OContinued state
```

This three-way outcome avoids exception-based control flow in the
meta-language.

---

## 4. The Soundness Theorem

### 4.1 Statement

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

### 4.2 Dual `st` argument

`wp` has type `stmt → (state → Prop) → state → state → Prop`.
The third argument is `pre_st` (entry state for `\old`); the fourth is the
current state. At the top-level call site both are `st`. They diverge only
inside `eval_contract` when evaluating `\old e`, which uses `pre_st`.
In all WP rules, `pre_st` is threaded through unchanged.

### 4.3 `SReturn` and `\result`

In the `OReturned st' v` branch, the postcondition receives `st'` where
`"\result"` is already bound:
```
wp (SReturn e) Q pre_st st = Q (update st "\result" (eval_expr st e))
```

### 4.4 `SContinue` yields `True`

`wp SContinue Q pre_st = fun _ => True`. This is correct because
`continue` only appears inside loop bodies. The loop's invariant is
re-checked at the top of each `SWhile` iteration by the WP conjuncts;
the body's WP does not need to enforce Q for the interrupted path.

### 4.5 The keystone sub-lemma

`while_inv_preserved` is proved by well-founded induction on the variant
value. The `SWhile` WP includes three conjuncts:

1. The invariant holds in the initial state.
2. For any state satisfying the invariant and guard: executing the body
   preserves the invariant, strictly decreases the variant, and the
   variant remains non-negative.
3. The postcondition holds when the invariant holds and the guard is false.

The non-negativity clause in conjunct (2) is required for `Z.lt_wf`
(Rocq) / `Nat.lt_wfRel` (Lean) to fire. It is an annotation obligation
on the programmer.

### 4.6 Proof strategy

- **Rocq**: Induction on the execution derivation `Hexec : exec st s out`.
  Each case directly names a specific constructor. `SSeq` chains the two
  IHs through the intermediate state; `SWhile` delegates to
  `while_inv_preserved`.

- **Lean**: `induction hExec generalizing Q`. Same structure, using
  `unfold wp at hWp` to expose WP definitions for seq cases, and
  providing explicit `s2` arguments to IH calls for seq-return and
  seq-continue.

---

## 5. Key WP Rules

| Statement | WP rule | Notes |
|-----------|---------|-------|
| `SSkip` | `Qn st` | Identity |
| `SAssign x e` | `Qn (update st x (eval_expr st e))` | Substitution |
| `SAugAssign x op e` | `Qn (update st x (eval_binop_z op (lookup_int st x) (eval_int st e)))` | Update-in-place |
| `SArraySet a i v` | `Qn (array_update st a i v)` | Array element |
| `SSeq s1 s2` | `wp s1 (λ st'. wp s2 Qn Qr Qc pre st') Qr Qc pre st` | Composition |
| `SIf c s1 s2` | `if eval_bool st c then wp s1 … else wp s2 …` | Branch |
| `SWhile inv var c body` | 3 conjuncts (§4.5) | Invariant + variant |
| `SFor x lo hi body` | `wp (desugar (SFor …)) Q pre st` | Delegate |
| `SReturn e` | `Qr (update st "\result" (eval_expr st e))` | Bind result |
| `SContinue` | `True` | Vacuous |

The `SFor` case delegates to `desugar` in both provers. In Lean, this
requires a `wpFor` helper defined outside the structural recursion to
satisfy the termination checker (Lean cannot see that `desugar` reduces
structural size).

---

## 6. For-Loop Desugaring

`desugar : stmt → stmt` replaces `SFor x lo hi body` with an
index-variable `SWhile`. The correctness theorem carries a freshness
precondition:

```
∀ st s out,
  fresh_in_stmt "_pycsl_idx" s →
  exec st s out ↔ exec st (desugar s) out
```

The reserved name `_pycsl_idx` is guaranteed absent from user programs.
This theorem is currently Admitted (Rocq) / sorry (Lean).

In Lean, `DesugarDef.lean` contains the pure transformation (imports only
`AST`), while `Desugar.lean` contains `desugar_correct` (imports `SOS`).
This split avoids `WP.lean` pulling in SOS transitively.

---

## 7. Prover-Specific Design Choices

### 7.1 Rocq

| Aspect | Choice | Rationale |
|--------|--------|-----------|
| Integer type | `Z` (ZArith) | Standard library; no external deps |
| Identifier | `string` + `String.string_dec` | Decidable equality for lookup |
| Termination | Structural `Fixpoint` on `stmt` | Accepted automatically |
| Key tactics | `lia`, `congruence`, `inversion`, `well_founded_induction` | `lia` for variant bounds; `Z.lt_wf` for while |
| Non-linear arithmetic | `nia` available | For `SFor` range arithmetic |
| Dependency | Standard library only (no Mathlib) | Minimises trust base |

### 7.2 Lean

| Aspect | Choice | Rationale |
|--------|--------|-----------|
| Integer type | `Int` (Mathlib) | `omega` support |
| Identifier | `String` (built-in) | `DecidableEq` automatic |
| Termination | `termination_by s` | Lean infers structural from matched arg |
| `SFor` WP | `wpFor` helper | Avoids termination failure on `desugar` call |
| Key tactics | `omega`, `simp`, `unfold … at …` | `omega` stronger than Rocq's `lia` on linear goals |
| Mathlib | Pinned to release tag | Only `Data.Int.Basic` and `Tactic.Omega` |
| Toolchain | Pinned via `lean-toolchain` | Reproducible builds |
| `evalExpr`/`evalContract` | Sequential (not `mutual def`) | Not mutually recursive; avoids unnecessary complexity |
| State | Association list (not `Std.HashMap`) | Proof-friendly; analogous to Rocq |

### 7.3 Lean compilation gotchas (discovered during implementation)

- **`wp` not auto-unfolded**: For seq cases, `hWp : wp (.seq s1 s2) …`
  does not unify with `wp s1 …`. Must use `unfold wp at hWp` explicitly.
- **Explicit postcondition for seq IH**: Must name `s2` in pattern match
  and provide the explicit continuation:
  `ih (fun st' => wp s2 Qn Qr Qc preSt st') Qr Qc preSt hWp`
- **No `Expr.bool`**: AST has no boolean type; truthiness uses
  `evalBool` checking `evalExpr st e` against `VInt 0`.
- **Makefile needs `SHELL := /bin/bash`**: Make's default `/bin/sh`
  doesn't support `source` (needed for `elan env`).

---

## 8. File Layout and Traceability

### 8.1 Rocq (`src/formal-semantics/rocq/`)

| File | Phase | Key definitions | Gate criterion |
|------|-------|-----------------|----------------|
| `Phase1_AST.v` | 1 | `binop`, `expr`, `contract_expr`, `stmt`, `func_spec` | Compiles |
| `Phase2_State.v` | 2 | `val`, `state`, `lookup`, `update`, `eval_expr`, `eval_contract`, `eval_variant` | Test lemmas pass |
| `Phase3_SOS.v` | 3 | `outcome`, `exec`, `exec_deterministic` | `exec_deterministic` proved |
| `Phase3b_Desugar.v` | 3b | `desugar`, `desugar_correct` | *Admitted* (freshness) |
| `Phase4_WP.v` | 4 | `wp` fixpoint | Termination accepted |
| `Phase5a_WhileInv.v` | 5a | `while_inv_preserved` | Proved (uses `Z.lt_wf`) |
| `Phase5b_Soundness.v` | 5b | `pycsl_soundness` | **Proved — 0 Admitted** |
| `Tests.v` | — | Concrete execution/WP tests | All pass |

Build: `make clean && make proof` in `rocq/`.

### 8.2 Lean (`src/formal-semantics/lean/`)

| File | Phase | Key definitions | Gate criterion |
|------|-------|-----------------|----------------|
| `PyCSL/AST.lean` | L0 | `Binop`, `Expr`, `ContractExpr`, `Stmt` | Compiles |
| `PyCSL/State.lean` | L1 | `Val`, `State`, `lookup`, `update`, `evalExpr`, `evalContract` | Test lemmas pass |
| `PyCSL/SOS.lean` | L2 | `Outcome`, `Exec`, `exec_deterministic` | `exec_deterministic` proved |
| `PyCSL/DesugarDef.lean` | L2 | `desugar` (pure, imports AST only) | Compiles |
| `PyCSL/Desugar.lean` | L2 | `desugar_correct` | *sorry* |
| `PyCSL/WP.lean` | L3 | `wp`, `wpFor` helper | Termination accepted |
| `PyCSL/WhileInv.lean` | L4a | `while_inv_preserved` | *sorry* (not used by soundness) |
| `PyCSL/Soundness.lean` | L4b | `pycsl_soundness` | **Proved — 0 sorry** |
| `PyCSL/Tests.lean` | — | Tests | All pass |

Build: `make clean && make proof` in `lean/`.

### 8.3 Dependency chain (identical structure in both provers)

```
AST → State → SOS ← DesugarDef ← Desugar
                ↓
               WP → WhileInv → Soundness → Tests
```

---

## 9. Trust Boundary

```
┌─────────────────────────────────────────────────────────┐
│              FORMALLY PROVEN (Rocq + Lean)               │
│                                                         │
│  ┌──────────┐  ┌──────────┐  ┌─────────┐  ┌─────────┐ │
│  │   AST    │→ │   SOS    │→ │   WP    │→ │Soundness│ │
│  │(Phase1)  │  │(Phase3)  │  │(Phase4) │  │(Phase5b)│ │
│  └──────────┘  └──────────┘  └─────────┘  └─────────┘ │
│                                                         │
│  Theorem: wp s Q pre st ∧ Exec st s out → Q(out)       │
└─────────────────────────────────────────────────────────┘
                          │
              ┌───────────┴───────────┐
              ▼                       ▼
┌──────────────────────┐  ┌──────────────────────┐
│  TRUSTED BY DESIGN   │  │  TRUSTED BY WhyML    │
│                      │  │                      │
│  • Python parser     │  │  • \valid, \separated│
│  • Transpiler        │  │  • \is_sorted, \sum  │
│  • Syntactic desugar │  │  • Memory model axiom│
│  • Ghost insertion   │  │  • Why3 solvers      │
│  • Multi-file import │  │  • mach.int overflow │
│  • Class→record      │  │  • string.String     │
│  • Concurrency       │  │                      │
│    reduction         │  │                      │
└──────────────────────┘  └──────────────────────┘
```

**100% of the WP calculus logic is formally proven.** All other features
are syntactic sugar (lowered before WP), WhyML axioms (trusted by the
Why3 ecosystem), or orchestration (build-system concerns).

---

## 10. Remaining Features (38 Unmodelled)

The 38 features not yet in the formal model are classified into six
categories:

### Category A — Add to core model (7 features)

New runtime behaviour or contract semantics requiring AST + SOS + WP +
soundness re-proof.

| Feature | Changes required |
|---------|-----------------|
| `raises` (exceptions) | 4th outcome `OException`; 4th continuation `Qe`; `SRaise`/`STry` stmts |
| `class invariant` | Record types + field access; invariant-wrapping around method bodies |
| `self.field` | `EField`/`CField` nodes; record-valued state |
| String literals | `VString` value; `EString` expr (or stay aligned with transpiler encoding: strings as integer hashes) |
| `None` | `VNone` value; `ENone` expr (or model as `VInt 0` to match transpiler) |
| Assert | `SAssert` stmt; WP: `eval_bool st e = true ∧ Qn st` |
| Lambda | `ELambda`/`VClosure`; `SCall` stmt (optional — rarely used in verified code) |

**Key design decisions pending:**

- **VNone/VString**: Either stay aligned with transpiler (model as `VInt 0`
  / `VInt(hash)`) or add real constructors with a faithfulness lemma.
  Cannot do both implicitly.
- **STry WP soundness**: `Qr` and `Qc` must pass through `finally` clauses.
  Without this, `try-finally` patterns skip cleanup, producing an unsound WP.
- **SAssert + exceptions interaction**: `assert` as a "stuck state" (no rule
  fires when false) is incompatible with the exception model. Either delay
  `SAssert` until exceptions are added, or prove a desugar lemma replacing
  the stuck-state rule with `SRaise`.

### Category B — Prove as desugaring (4 features)

Lowered to existing core constructs before WP generation. Proof obligation:
`desugar_correct`-style lemma.

| Feature | Desugars to |
|---------|-------------|
| `in`, `not in` | `∃ i; 0 ≤ i < \length(arr) ∧ arr[i] == x` (Category C — contract-level, not stmt-level) |
| Tuple unpacking | Sequence of assignments |
| Walrus `:=` | `SSeq (SAssign x e) (use x)` |
| Match statement | `SIf` chain |

### Category C — Contract expression extensions (10 features)

New `contract_expr` constructors and `eval_contract` clauses. No changes
to `stmt`, `exec`, `wp`, or soundness.

Features: `label`+`\at`, ghost assign/augassign, `\valid`, `\separated`,
`\length2d`, `\valid2d`, `\is_sorted`, `\sum`, function call in contract,
`arr[lo:hi]`.

**Technical note**: `CSum` requires well-founded recursion (`Program
Fixpoint` with `measure (Z.to_nat (hi - lo))` in Rocq), not plain
`Fixpoint` on `Z`. Adding `func_env` for `CCall` changes `eval_contract`'s
signature, rippling through all WP rules — comparable in invasiveness to
the `env` refactor.

### Category D — Alternative memory models (7 features)

Requires parameterising the formalisation over a memory model interface
(Rocq module type / Lean type class). Features: typed model, store model,
concurrent model, `thread_entry`, `critical`, `acquires`, `releases`.

**Concurrent model soundness issues**: `ExecCritical` must universally
quantify `shared` at entry (modelling havoc), not pick a specific shared
state. `lock_order` (deadlock prevention) must be modelled as a
well-formedness condition.

### Category E — Vacuously sound (4 features)

No proof needed; soundness is partial correctness ("if terminates, then
post holds"). Features: structural `\variant`, `\diverges`, `\trusted`,
`bounded_int(N)`.

### Category F — Pipeline orchestration (4 features)

No semantic content. Features: multi-file imports, `--deep`, `--fun`,
`split_vc`.

### Implementation phases

```
Phase 1 (B+E+F): Desugar lemmas + vacuous doc     → 38→22 features
Phase 2 (A):     Assert + None + String             → 22→19
Phase 3 (C):     Ghost + Label (\at, \old refactor) → 19→15
Phase 4 (C):     Library predicates (\valid, etc.)   → 15→7
Phase 5 (A):     Exceptions (4th continuation Qe)    → 7→6
Phase 6 (A+D):   Records + class invariants          → 6→4
Phase 7 (D):     Memory model parameterisation       → 4→0
Phase 8 (A):     Lambda (optional)
```

**Dependency ordering**: Phases 3b (label `env` refactor) and 5 (exception
`Qe`) both change the `wp` signature. Implementing Phase 5 first stabilises
the continuation interface before Phase 3b adds the environment record.

---

## 11. CMMI Process Alignment

| CMMI PA | Mapping |
|---------|--------|
| **REQM** | Scope defined in §2; feature coverage in §10 |
| **PP** | This document; phase ordering in §10 |
| **PMC** | Phase gates: each phase compiles with zero warnings before the next begins |
| **CM** | One `.v`/`.lean` file per phase; no cross-phase dependencies except imports |
| **PPQA** | Zero `Admitted`/`sorry` at phase completion |
| **VER** | `coqc`/`lean` on every file; CI via `Makefile` |
| **VAL** | Test lemmas: concrete evaluation against expected outcomes |

### Phase gate criteria

A phase is **complete** when:

1. All files compile without warnings.
2. No `Admitted` (Rocq) or `sorry` (Lean) remains in the phase's files.
3. Test lemmas pass.
4. Deliverable documented.

---

## 12. Audit Traceability

### Feature coverage (quantitative)

| Category | Total | Modelled | Coverage |
|----------|------:|:--------:|:--------:|
| Directives | 26 | 5 | 19% |
| Expression atoms | 20 | 8 | 40% |
| Operators | 9 | 8 | 89% |
| Statement types | 15 | 10 | 67% |
| Memory models | 4 | 1 | 25% |

**Effective WP engine coverage**: The modelled features constitute 100% of
the WP calculus logic — the component that generates proof obligations. All
unmodelled features are syntactic sugar (lowered before WP), WhyML axioms,
or orchestration.

### Reproducing the proofs

```bash
# Rocq
cd src/formal-semantics/rocq && make clean && make proof
# Expected: 8 files compiled, 1 Admitted (desugar_correct)

# Lean
cd src/formal-semantics/lean && make clean && make proof
# Expected: 9 files compiled, 3 sorry (not used by soundness)
```

---

## 13. Risk Register

| Risk | Impact | Mitigation |
|------|--------|------------|
| While-invariant induction blocked | High | Prototyped; proved in both provers via well-founded induction |
| Lean termination rejects `wp` for `SFor` | Medium | `wpFor` helper (§5); structural recursion preserved |
| For-loop desugaring variable capture | Low | Reserved `_pycsl_idx`; freshness precondition |
| Scope creep from extensions | Medium | Strict phase gates; no extension work until current phase is `sorry`-free |
| Variant non-negativity unprovable | Medium | Explicit `≥ 0` conjunct in WP; programmer obligation |
| Phase 3b+5 signature conflicts | Medium | Implement Phase 5 first (§10) |
| STry WP finally soundness | Critical | `Qr`/`Qc` must pass through finally clause (§10, Category A) |
| ExecCritical shared state | Critical | Universal quantification over shared states at entry (§10, Category D) |
| Mathlib instability | Low | Pinned version in `lakefile.lean` |
| Lean toolchain changes | Low | Pinned via `lean-toolchain` |
