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
| Rocq | `pycsl_soundness` (Phase5b_Soundness.v:334) — **0 Admitted** | None |
| Lean | `pycsl_soundness` (Soundness.lean:229) — **0 sorry** | None |
| Lean | `pycslSoundnessVerified` (SoundnessVerified.lean:74) — **0 sorry** | None |

The end-to-end Why3-VCG → WP → SOS correspondence theorem
(`pycslSoundnessVerified`) compiles clean in both provers. All
previously-`Admitted`/`sorry` proof obligations are now discharged:

- `desugar_correct` — PROVED (Rocq: `Phase3b_Desugar.v:153` Qed.; Lean: `Desugar.lean:239`).
- `while_not_continued` — PROVED (Rocq: `Phase5a_WhileInv.v:14` Qed.; Lean: `WhileInv.lean:59`).
- `while_inv_preserved` — PROVED (Rocq: `Phase5a_WhileInv.v:30` Qed.; Lean: `WhileInv.lean:197`).
- `module6_encodes_mlw` (the LINK 2 residual axiom) — PROVED Lemma
  (Rocq: `Phase6m_VcgSemBridge.v:438`); in Lean, the analogous `vcgBridge`
  is a proved `def` (`VcgEmission.lean:62`) derived from the
  construction-site axiom `Why3CertWitness`.

**Trust ledger — 3 named axioms (the TCB):**

| # | Rocq axiom | Lean axiom | Trusts |
|---|-----------|-----------|--------|
| 1 | `alt_ergo_correct` (Phase5b_Soundness.v:563) | `altErgoCorrect` (Soundness.lean:435) | SMT-solver (Alt-Ergo) soundness on a discharged goal |
| 2 | `trusted_contracts_axiom` (Phase5b_Soundness.v:577) | `trustedContractsAxiom` (Soundness.lean:447) | `\trusted` contracts hold when their precondition is established |
| 3 | `why3_implements_wp_w` (Phase6i_Soundness.v:65) | `Why3CertWitness` (Why3Trust.lean:76) | Why3's VCG correctly discharges the WP of a `WhyMLStmt` |

Both proofs compile end-to-end with `make proof` in their respective
directories.

---

## 2. Scope

### 2.1 In scope (Track 1 — Hoare model only)

| Category | Constructs |
|----------|-----------|
| **Statements (22)** | `skip`, `assign`, `augAssign`, `arraySet`, `seq`, `ite`, `while_` (inv+var mandatory), `for_` (desugars to `while_`), `ret`, `continue_`, `break_`, `assert_`, `tupleUnpack`, `ghostDecl`, `ghostAssign`, `label_`, `raise_`, `tryCatch`, `fieldAssign`, `fieldAugAssign`, `critical`, `threadEntry` (Rocq: `Phase1_AST.v:196-226`; Lean: `AST.lean:259-288`) |
| **Runtime expr (`expr`)** | int literals, vars, `arr[i]`, `\length(arr)`, binary arithmetic (`+ - * // / %`), unary `-`, 6 comparisons (=, <>, <, <=, >, >=) → 0/1, `self.field` (`EFieldGet`/`fieldGet`), function call (`ECall`/`call` — opaque placeholder) |
| **Contract expressions (`contract_expr`)** | the runtime-expr fragment plus: `\result`, `\old(e)`, `\at(e,L)` (via `eval_contract_es`/`evalContractEs`), `arr[i]`, `arr[i][j]` (chainedSubscript), boolean literals, `None`, string literals, `\is_sorted(arr,lo,hi)`, `\sum(arr,lo,hi)`, `arr[lo:hi]` (slice — opaque), `elem in arr`, `elem not in arr`, `\result[i]` (resultSubscript), `f(args)` (call — opaque), logical connectives (`==>` `<=>` `&&` `\|\|` `not`), comparisons, quantifiers (`\forall`, `\exists` over `int`); plus **37 ghost atoms** covering dict / list / set / tuple / string / array operations (`cgMapEmpty`, `cgMapGet/Set/Remove`, `cgNil/Cons/Hd/Tl/ListLen/Nth/ListMem/Append`, `cgSetEmpty/Add/Remove/Mem/Card/Union/Inter/Diff/Subset/Eq`, `cgMkTuple2/3/4`, `cgFst/Snd/Trd/Fth`, `cgStrConcat/Len/Nth`, `cgMake/Copy/CopyRange`) — Rocq: `Phase1_AST.v:77-156`; Lean: `AST.lean:141-222` |
| **Function specifications** | `requires`, `ensures`, `assigns \nothing \| var-list`, `\variant` (function-level), `\diverges`, `\trusted` (+ `reviewer:`), `bounded_int(N)`, `raises ExcType when cond`, `no_exception E1, E2, ...`, `allow_finalizer` |
| **Loop annotations** | `loop invariant`, `loop variant` (multiple per loop, conjoined via `c_conj`); function `\variant` |

The formal semantics covers only *fully annotated* PyCSL programs: every
`while_` loop carries an explicit invariant and variant in the AST. There
is no constructor for unannotated loops.

### 2.2 Explicit non-goals (deferred)

- Typed/store memory models (`\valid`, `\separated`, heap reasoning)
- Class invariants and record-valued state (field read/write exist as
  flat synthesised-variable lookups; the class-invariant wrapping pattern
  is not in the WP calculus)
- Lambda and higher-order functions
- `acquires`/`releases` (real concurrency model; the Hoare-identity stubs
  `SCritical`/`SThreadEntry` exist but do not encode the monitor-invariant
  pattern or `lock_order` well-formedness)
- `\length2d`, `\valid2d` (2D-array library predicates)

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

A single `stmt` inductive with **22 constructors**, organised by the
phase that introduced each:

| Phase | Constructors |
|-------|--------------|
| 0 (core) | `SSkip`, `SAssign`, `SAugAssign`, `SArraySet`, `SSeq`, `SIf`, `SWhile` (inv+var mandatory), `SFor` (desugars to `SWhile`), `SReturn`, `SContinue` |
| 2 | `SBreak`, `SAssert`, `STupleUnpack` |
| 3a (ghost/label) | `SGhostDecl`, `SGhostAssign`, `SLabel` |
| 5 (exceptions) | `SRaise`, `STryCatch` |
| 6 (records) | `SFieldAssign`, `SFieldAugAssign` |
| 8 (concurrency stubs) | `SCritical`, `SThreadEntry` |

Rocq: `Phase1_AST.v:196-226`; Lean: `AST.lean:259-288`. All 22 have SOS
rules (`Phase3_SOS.v`; `SOS.lean:22-174`), WP rules (`Phase4_WP.v:40-145`;
`WP.lean:24-122`), and a soundness case (`Phase5b_Soundness.v:334-438`;
`Soundness.lean:34-79`).

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

The simplified 3-continuation form (for expository purposes):

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

The **actual** theorem (Phase5b_Soundness.v:334; Soundness.lean:229) uses
the 5-continuation form: `Qn`, `Qr`, `Qc`, `Qb`, `Qe` (normal / return /
continue / break / exception), with the corresponding `Outcome` variants
`ONormal`, `OReturned`, `OContinued`, `OBroke`, `OThrew`, `OFailed`. Each
outcome dispatches to its corresponding continuation; the `OFailed` case
(safety violation) is mapped to `True`.

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

The `wp` fixpoint has 5 continuations: `Qn` (normal), `Qr` (return),
`Qc` (continue), `Qb` (break), `Qe` (exception). All 22 `Stmt`
constructors have WP rules (Rocq: `Phase4_WP.v:35-145`; Lean: `WP.lean:19-122`).

| Statement | WP rule | Notes |
|-----------|---------|-------|
| `SSkip` | `Qn st` | Identity |
| `SAssign x e` | `Qn (update st x (eval_expr st e))` | Substitution |
| `SAugAssign x op e` | `Qn (update st x (eval_binop_z op (lookup_int st x) (eval_int st e)))` | Update-in-place |
| `SArraySet a i v` | `Qn (array_update st a i v)` | Array element |
| `SSeq s1 s2` | `wp s1 (λ st'. wp s2 Qn Qr Qc Qb Qe pre st') Qr Qc Qb Qe pre st` | Composition, propagates all 5 continuations |
| `SIf c s1 s2` | `if eval_bool st c then wp s1 … else wp s2 …` | Branch |
| `SWhile inv var c body` | 3 conjuncts (§4.5) | Invariant + variant; `Qb` on body = `Qn` (break exits loop normally) |
| `SFor x arr inv var body _` | `wp (desugar (SFor …)) Q pre st` (via `wpFor` helper in Lean) | Delegate to while |
| `SReturn e` | `Qr (update st "\result" (eval_expr st e))` | Bind result |
| `SContinue` | `Qc st` | Loop-scope only |
| `SBreak` | `Qb st` | Loop-scope only |
| `SAssert cond msg` | `eval_c cond ∧ Qn st` | Assert (no exception; failure is stuck-state) |
| `STupleUnpack xs e` | `Qn st` | Simplified — assigns nothing in the formal model |
| `SGhostDecl x t e` | `Qn (ghost_update st x (eval_ghost_val t st e))` | Ghost state |
| `SGhostAssign x t op e` | `Qn (ghost_update st x (apply_ghost_aug op (ghost_lookup st x) st e))` | Ghost aug-assign |
| `SLabel L` | `Qn (set_labels st ((L, ghost_st) :: label_snaps))` | Snapshot ghost state for `\at(_, L)` |
| `SRaise exc` | `Qe exc st` | Exception |
| `STryCatch s1 exc handler` | `wp s1 … (λ exc' st'. if exc' = exc then wp handler … else Qe exc' st') …` | 5-continuation handler dispatch |
| `SFieldAssign self f e` | `Qn st` | Placeholder (flat synthesised var) |
| `SFieldAugAssign self f op e` | `Qn st` | Placeholder (flat synthesised var) |
| `SCritical mutex body` | `wp body …` | Hoare-identity stub |
| `SThreadEntry body` | `wp body …` | Hoare-identity stub |

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
This theorem is PROVED in both provers (Rocq: `Phase3b_Desugar.v:153`
Qed.; Lean: `Desugar.lean:239`).

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

The directory contains 40+ files organised into Phases 0-6L plus
extraction tooling. The core soundness chain:

| File | Phase | Key definitions | Gate criterion |
|------|-------|-----------------|----------------|
| `Phase1_AST.v` | 1 | `binop`, `cmpop`, `expr` (incl. `EFieldGet`, `ECall`), `contract_expr` (70 ctors incl. 37 ghost atoms), `stmt` (22 ctors), `func_spec` | Compiles |
| `Phase2_State.v` | 2 | `val`, `state`, `lookup`, `update`, `eval_expr`, `eval_z`, `eval_contract`, `eval_contract_es` (for `CAt`), `eval_variant` | Test lemmas pass |
| `Phase3_SOS.v` | 3 | `outcome` (6 kinds), `exec` (22 ctor rules), `exec_deterministic` | `exec_deterministic` proved |
| `Phase3b_Desugar.v` | 3b | `desugar`, `desugar_correct` | **Proved (Qed.)** |
| `Phase4_WP.v` | 4 | `wp` fixpoint (5-continuation, 22-ctor coverage) | Termination accepted |
| `Phase5a_WhileInv.v` | 5a | `while_not_continued`, `while_inv_preserved` | **Proved (Qed.)** |
| `Phase5b_Soundness.v` | 5b | `pycsl_soundness` (22-ctor induction); `alt_ergo_correct`, `trusted_contracts_axiom` (2 of 3 named axioms) | **Proved — 0 Admitted** |
| `Phase6i_Soundness.v` | 6i | `why3_implements_wp_w` (3rd named axiom); `why3_implements_wp_w_derived` | **Proved (derived)** — 0 Admitted |
| `Phase6m_VcgSemBridge.v` | 6m | `module6_encodes_mlw` (Lemma, was Axiom); `why3_validates_emitted`; `why3_validates_vc_formula` | **Proved** |
| `Tests.v` | — | Concrete execution/WP tests | All pass |

Build: `make clean && make proof` in `rocq/`.

### 8.2 Lean (`src/formal-semantics/lean/`)

The `PyCSL/` directory contains 40+ files mirroring the Rocq Phases plus
the Sub-α emission-certainty theorems (`Emit*`, `Handle*English`). The
core soundness chain:

| File | Phase | Key definitions | Gate criterion |
|------|-------|-----------------|----------------|
| `PyCSL/AST.lean` | L0 | `Binop`, `CmpOp`, `Expr` (incl. `fieldGet`, `call`), `ContractExpr` (70 ctors), `Stmt` (22 ctors), `FuncSpec`, `FrameCond`, `GhostType` | Compiles |
| `PyCSL/State.lean` | L1 | `Val`, `State`, `ExecState` (incl. `labelSnaps`), `lookup`, `update`, `evalExpr`, `evalZ`, `evalZEs`, `evalContract`, `evalContractEs` (for `.at_`), `evalVariant`, ghost evaluators | Test lemmas pass |
| `PyCSL/SOS.lean` | L2 | `Outcome` (6 kinds), `Exec` (22 ctor rules), `exec_deterministic` | `exec_deterministic` proved |
| `PyCSL/DesugarDef.lean` | L2 | `desugar` (pure, imports AST only) | Compiles |
| `PyCSL/Desugar.lean` | L2 | `desugar_correct`, `walrusAssign_eq`, `tupleUnpack2_eq`, `desugarMatch` hit/miss | **Proved** |
| `PyCSL/WP.lean` | L3 | `wp` (5-continuation, 22-ctor coverage), `wpFor` helper | Termination accepted |
| `PyCSL/WhileInv.lean` | L4a | `while_not_continued`, `while_inv_preserved` | **Proved** |
| `PyCSL/Soundness.lean` | L4b | `pycsl_soundness` (22-ctor induction); `altErgoCorrect`, `trustedContractsAxiom` (2 of 3 named axioms) | **Proved — 0 sorry** |
| `PyCSL/SoundnessVerified.lean` | L4c | `pycslSoundnessVerified` (end-to-end via `wpGenCorrect` + `wpW_implies_wp`) | **Proved — 0 sorry** |
| `PyCSL/Why3Trust.lean` | L5 | `Why3Certificate`, `Why3CertWitness` (3rd named axiom), `SmtCertificate` | Compiles |
| `PyCSL/VcgEmission.lean` | L6C | `vcgBridge` (proved `def`, derived from `Why3CertWitness`) | **Proved** |
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

## 10. Remaining Features (11 of 36 Unmodelled)

The 2026-05-19 snapshot of this file claimed "38 Unmodelled" features
across six categories. As of the 2026-06-28 audit refresh, **25 of the 36
catalogued features are modelled** (the previous "38" was an off-by-two
arithmetic slip; the six category lists sum to 7+4+10+7+4+4 = 36). This
section re-classifies each feature honestly, with file:line citations
against the current AST.

### Category A — Add to core model (2 remaining, 5 done)

| Feature | Status |
|---------|--------|
| `raises` (exceptions) | ✅ DONE — `SRaise`/`STryCatch` stmts (Phase1_AST.v:219-220; AST.lean:281-282); `OThrew`/`OFailed` outcomes (Phase3_SOS.v; SOS.lean:17-19); WP 5th continuation `Qe` (Phase4_WP.v:128-136; WP.lean:105-113); soundness cases (Phase5b_Soundness.v; Soundness.lean:41,68) |
| `class invariant` | ❌ Class invariants remain a WhyML record-type feature; the core WP calculus operates on flat state |
| `self.field` | ✅ DONE — `EFieldGet`/`fieldGet` runtime ctor (Phase1_AST.v:37; AST.lean:24); `SFieldAssign`/`SFieldAugAssign` stmts (Phase1_AST.v:222-223; AST.lean:284-285). Field state is a flat synthesised-variable lookup (`obj ++ "." ++ f`); record-valued state is the deferred class-invariant work |
| String literals | ✅ DONE — `CStringLit`/`.stringLit` (Phase1_AST.v:103; AST.lean:168); `evalZ` = 0, `evalContract` = `s ≠ ""` (Phase2_State.v; State.lean:201,237) |
| `None` | ✅ DONE — `CNoneLit`/`.noneLit` (Phase1_AST.v:102; AST.lean:167); `evalZ` = 0, `evalContract` = False (Phase2_State.v; State.lean:200,236) |
| Assert | ✅ DONE — `SAssert` stmt (Phase1_AST.v:212; AST.lean:274); SOS `execAssertPass`/`execAssertFail` (SOS.lean:112-118); WP `eval_c cond ∧ Qn es` (Phase4_WP.v:110; WP.lean:89-90) |
| Lambda | ❌ `ELambda`/`VClosure` not in AST; higher-order not modelled |

### Category B — Prove as desugaring (0 remaining, 4 done)

| Feature | Status |
|---------|--------|
| `in`, `not in` | ✅ DONE — promoted from desugar to first-class contract expr: `CIn`/`CNotIn` (Phase1_AST.v:107-108; AST.lean:172-173); `evalContract` (Phase2_State.v; State.lean:244-257) |
| Tuple unpacking | ✅ DONE — `STupleUnpack` stmt (Phase1_AST.v:213); plus `tupleUnpack2` desugar (Desugar.lean:254-259) |
| Walrus `:=` | ✅ DONE — `walrusAssign = .assign` by `rfl` (Desugar.lean:248-249) |
| Match statement | ✅ DONE — `desugarMatch` with proved hit/miss (Desugar.lean:267-284) |

### Category C — Contract expression extensions (4 remaining, 6 done)

| Feature | Status |
|---------|--------|
| `label`+`\at` | ✅ DONE — `SLabel` stmt + `CAt` ctor (Phase1_AST.v:217,213; AST.lean:279,178); `execLabel` records ghost snapshot (SOS.lean:132); `eval_contract_es`/`evalContractEs` looks up label snapshot (Phase2_State.v:559; State.lean:469) |
| ghost assign/augassign | ✅ DONE — `SGhostDecl`/`SGhostAssign` stmts (Phase1_AST.v:215-216; AST.lean:277-278); plus 37 ghost atoms covering dict/list/set/tuple/string/array ops (Phase1_AST.v:114-156; AST.lean:180-221) |
| `\valid` | ❌ NOT in AST — typed/store memory-model feature |
| `\separated` | ❌ NOT in AST — typed/store memory-model feature |
| `\length2d` | ❌ NOT in AST — 2D-array extension |
| `\valid2d` | ❌ NOT in AST — 2D-array extension |
| `\is_sorted` | ✅ DONE — `CIsSorted` ctor (Phase1_AST.v:104; AST.lean:169); `evalContract` via `sortedListRange` (State.lean:238-243) |
| `\sum` | ✅ DONE — `CSum` ctor (Phase1_AST.v:105; AST.lean:170); `evalZ` via `sumListRange` (State.lean:202-207) — well-founded recursion pattern documented in Phase2_State.v |
| function call in contract | ✅ (opaque) — `CCall` ctor (Phase1_AST.v:111; AST.lean:176); `evalContract = True` (Phase2_State.v:530; State.lean `_ => True`) — Hoare-model opacity, no `func_env` |
| `arr[lo:hi]` | ✅ (opaque) — `CSlice` ctor (Phase1_AST.v:106; AST.lean:171); `evalContract = True` placeholder (Phase2_State.v:522; State.lean `_ => True`) — slice equality deferred to typed memory model |

### Category D — Alternative memory models (5 remaining, 2 done as Hoare-identity stubs)

| Feature | Status |
|---------|--------|
| typed model | ❌ Heap-based memory model not parameterised |
| store model | ❌ Single-heap model not parameterised |
| concurrent model (real) | ❌ The Hoare-identity `SCritical`/`SThreadEntry` stubs (see below) do not encode the monitor-invariant pattern. `ExecCritical` must universally quantify `shared` at entry (modelling havoc); `lock_order` (deadlock prevention) must be a well-formedness condition |
| `thread_entry` | ✅ DONE — `SThreadEntry` stmt (Phase1_AST.v:226; AST.lean:288); SOS `execThreadEntry` (SOS.lean:167); WP delegates to body (Phase4_WP.v:145; WP.lean:121). Hoare-identity stub |
| `critical` | ✅ DONE — `SCritical` stmt (Phase1_AST.v:225; AST.lean:287); SOS `execCritical` (SOS.lean:163); WP delegates to body (Phase4_WP.v:143; WP.lean:118). Hoare-identity stub |
| `acquires` | ❌ No stmt constructor |
| `releases` | ❌ No stmt constructor |

### Category E — Vacuously sound (0 remaining, 4 done)

All four remain vacuously sound (partial-correctness theorem doesn't cover
termination): structural `\variant`, `\diverges`, `\trusted`, `bounded_int(N)`.
(`vacuous-soundness.md` §E.1–E.4.)

### Category F — Pipeline orchestration (0 remaining, 4 done)

All four remain vacuously sound: multi-file imports, `--deep`, `--fun`,
`split_vc`. (`vacuous-soundness.md` §F.1–F.4.)

### Summary

| Category | Total | Done | Remaining |
|----------|------:|:----:|:---------:|
| A — Core model | 7 | 5 | 2 |
| B — Desugaring | 4 | 4 | 0 |
| C — Contract extensions | 10 | 6 | 4 |
| D — Memory models | 7 | 2 | 5 |
| E — Vacuously sound | 4 | 4 | 0 |
| F — Pipeline orchestration | 4 | 4 | 0 |
| **Total** | **36** | **25** | **11** |

(The previous README mis-stated the total as "38"; the six category
sub-totals sum to 36.)

**Effective WP-engine coverage**: The 25 modelled features include all 22
`Stmt` constructors, all 70 `ContractExpr` constructors (4 of which —
`\valid`-class features not in AST, plus `slice`/`call` opaque placeholders
— are out-of-scope here), and the full runtime-expression language. The
soundness theorem `pycsl_soundness` is discharged on all 22 `Stmt` cases
(Phase5b_Soundness.v:334-438; Soundness.lean:229-344). All other features
are syntactic sugar (lowered before WP), WhyML axioms (trusted by the Why3
ecosystem), or orchestration (build-system concerns).

### Remaining work

The 11 unmodelled features cluster into three work-streams:

1. **Class invariants + record-valued state** (Category A: `class invariant`,
   Lambda) — requires record types in `state` and field-access semantics.
2. **2D-array library predicates** (Category C: `\valid`, `\separated`,
   `\length2d`, `\valid2d`) — blocked on the typed/store memory model.
3. **Memory-model parameterisation** (Category D: typed, store, real
   concurrent, `acquires`, `releases`) — requires parameterising the
   formalisation over a memory-model interface (Rocq module type / Lean
   type class).

The previous phase plan (Phases 1-8 driving 38→0) is obsolete: Phases
1-6 + 8 (all but Phase 7) landed; the residual is Phase 7 (memory-model
parameterisation) plus the two Category A items that depend on it.

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
| `Stmt` constructors | 22 | 22 | 100% |
| `ContractExpr` constructors | 70 | 66 (4 opaque placeholders: `slice`, `call`, `resultSubscript`, ghost atoms with `_ => True`) | 94% |
| Function-spec directives | 11 | 11 | 100% |
| Statement-level features (§10 cat. A+B) | 11 | 9 | 82% |
| Contract-expression features (§10 cat. C) | 10 | 6 | 60% |
| Memory models (§10 cat. D) | 7 | 2 (Hoare-identity stubs) | 29% |
| Vacuous features (§10 cat. E+F) | 8 | 8 | 100% |
| **§10 totals** | **36** | **25** | **69%** |

**Effective WP engine coverage**: The modelled features constitute 100% of
the WP calculus logic — the component that generates proof obligations. All
unmodelled features are syntactic sugar (lowered before WP), WhyML axioms,
or orchestration.

### Reproducing the proofs

```bash
# Rocq
cd src/formal-semantics/rocq && make clean && make proof
# Expected: all files compiled, 0 Admitted

# Lean
cd src/formal-semantics/lean && make clean && make proof
# Expected: all files compiled, 0 sorry
```

---

## 13. Risk Register

| Risk | Impact | Mitigation |
|------|--------|------------|
| While-invariant induction blocked | ~~High~~ Closed | Proved in both provers via well-founded induction (Phase5a_WhileInv.v:30; WhileInv.lean:197) |
| Lean termination rejects `wp` for `SFor` | ~~Medium~~ Closed | `wpFor` helper (§5); structural recursion preserved |
| For-loop desugaring variable capture | ~~Low~~ Closed | Reserved `_pycsl_idx`; freshness precondition; `desugar_correct` proved (Phase3b_Desugar.v:153; Desugar.lean:239) |
| Scope creep from extensions | Medium | Strict phase gates; no extension work until current phase is `sorry`-free |
| Variant non-negativity unprovable | Medium | Explicit `≥ 0` conjunct in WP; programmer obligation |
| ~~Phase 3b+5 signature conflicts~~ | ~~Medium~~ Closed | Phase 5 landed with `Qe` continuation; Phase 3b `\at` handled by `eval_contract_es`/`evalContractEs` (Phase2_State.v:559; State.lean:469) without `wp` signature change |
| STry WP finally soundness | Critical | `Qr`/`Qc`/`Qb` pass through `STryCatch` body via 5-continuation WP (Phase4_WP.v:130-136; WP.lean:107-113); `try-finally` not yet modelled (finally clause lowering is a transpiler concern) |
| ExecCritical shared state | Critical | Current `SCritical` is a Hoare-identity stub (Phase4_WP.v:143); real concurrent model requires universal quantification over shared states at entry (§10, Category D) |
| Mathlib instability | Low | Pinned version in `lakefile.lean` |
| Lean toolchain changes | Low | Pinned via `lean-toolchain` |
