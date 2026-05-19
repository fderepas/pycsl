# PyCSL Formal Semantics — Master Plan

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

---

## 3. Architecture — Three Tracks

```
Track 1: Rocq (primary)              Track 2: Lean 4 (port)
  Phase 0  Scope                       Phase L0  AST port
  Phase 1  AST in Gallina              Phase L1  State & evaluation
  Phase 2  State & evaluation          Phase L2  SOS as Lean Prop
  Phase 3  Structural Operational      Phase L3  WP calculus
           Semantics (SOS)             Phase L4  Soundness proof
  Phase 3b For-loop desugaring         Phase L5  (bonus) #@ syntax macros
  Phase 4  WP calculus
  Phase 5a While invariant lemma
  Phase 5b Soundness theorem

Track 3: Extensions (post-port)
  Phase 6  Typed/store memory models
  Phase 7  Module 6 transpiler connection
  Phase 8  Ghost variables
  Phase 9  Class invariants and record types
```

**Sequencing rule:** Track 2 begins only after all `Admitted` blocks in Track 1 are
closed. Track 3 begins after Track 2 is complete.

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

### 4.2 Statements

A single `stmt` inductive with constructors: `SSkip`, `SAssign`, `SAugAssign`,
`SArraySet`, `SSeq`, `SIf`, `SWhile` (carrying invariant + variant), `SFor`
(syntactic sugar), `SReturn`, `SContinue`.

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

**In English:** if the WP calculus says that precondition `wp s Q st st` holds for
statement `s` with postcondition `Q`, and `s` executes from state `st` producing
outcome `out`, then the postcondition `Q` holds in the final state.

The keystone sub-lemma is `while_inv_preserved`, proved by well-founded induction on
the variant value. This is the only case that requires induction beyond structural
recursion on the statement AST.

---

## 6. CMMI Process Areas Alignment

This project follows a CMMI-inspired process structure across both prover
implementations:

| CMMI PA | Mapping in this project |
|---------|------------------------|
| **Requirements Management (REQM)** | Scope defined in §2; each phase has an explicit deliverable (see §7) |
| **Project Planning (PP)** | This plan; prover-specific plans in `rocq/rocq-plan.md` and `lean/lean-plan.md` |
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
plans (`rocq/rocq-plan.md`, `lean/lean-plan.md`) contain a file-by-file traceability
table linking every source file to its phase, its purpose, and its upstream
dependency.

---

## 7. Phase Deliverables Summary

| Phase | Deliverable | Success Criterion |
|-------|-------------|-------------------|
| 0 | Scope document | Reviewed, no open questions |
| 1 | AST definitions | Compiles; test: construct and pattern-match example AST |
| 2 | State model + evaluators | Compiles; test lemmas: eval concrete programs |
| 3 | SOS relation | Compiles; `exec_deterministic` proved |
| 3b | For-loop desugaring | `desugar_correct` proved |
| 4 | WP calculus | Compiles; structural recursion accepted by termination checker |
| 5a | While invariant lemma | `while_inv_preserved` proved (no `Admitted`) |
| 5b | Soundness theorem | `pycsl_soundness` proved (no `Admitted`) |
| L0–L4 | Lean port | All Lean files compile; `pycsl_soundness` proved (no `sorry`) |
| L5 | Syntax macros | Example annotated function type-checks via macros |

---

## 8. Directory Structure

```
src/formal-semantics/
├── formal-semantics-plan.md          ← this file
├── rocq/
│   ├── rocq-plan.md                  ← Rocq-specific plan with file traceability
│   ├── Makefile                      ← coqc build rules
│   ├── _CoqProject                   ← Rocq project file
│   ├── Phase1_AST.v                  ← binop, expr, contract_expr, stmt, func_spec
│   ├── Phase2_State.v                ← val, state, lookup, update, eval_expr,
│   │                                    eval_contract, eval_variant
│   ├── Phase3_SOS.v                  ← outcome, exec relation, exec_deterministic
│   ├── Phase3b_Desugar.v             ← desugar, desugar_correct
│   ├── Phase4_WP.v                   ← wp fixpoint
│   ├── Phase5a_WhileInv.v            ← while_inv_preserved
│   ├── Phase5b_Soundness.v           ← pycsl_soundness
│   └── Tests.v                       ← concrete evaluation test lemmas
└── lean/
    ├── lean-plan.md                  ← Lean-specific plan with file traceability
    ├── lakefile.lean                 ← Lake build configuration
    ├── PyCSL/
    │   ├── AST.lean                  ← Binop, Expr, ContractExpr, Stmt, FuncSpec
    │   ├── State.lean                ← Val, State, lookup, update, evalExpr,
    │   │                                evalContract, evalVariant
    │   ├── SOS.lean                  ← Outcome, Exec inductive, exec_deterministic
    │   ├── Desugar.lean              ← desugar, desugar_correct
    │   ├── WP.lean                   ← wp definition
    │   ├── WhileInv.lean             ← while_inv_preserved
    │   ├── Soundness.lean            ← pycsl_soundness
    │   ├── Macros.lean               ← (bonus) #@ syntax embedding
    │   └── Tests.lean                ← concrete evaluation test lemmas
    └── PyCSL.lean                    ← root import file
```

---

## 9. Risk Register

| Risk | Impact | Mitigation |
|------|--------|------------|
| While-invariant mutual induction blocked | High — blocks Phase 5a and all downstream | Prototype proof sketch in Rocq first; use `measure` or `Function` if structural induction fails |
| Lean termination checker rejects `wp` | Medium — blocks Phase L3 | Use `termination_by structural s` or `WellFoundedRelation` on `Stmt.sizeOf` |
| For-loop desugaring introduces fresh variable capture | Low — blocks Phase 3b | Use a reserved name (`_pycsl_idx`) guaranteed absent from user programs |
| Scope creep from Track 3 features | Medium — delays completion | Strict phase gates; no Track 3 work until Track 2 is `sorry`-free |

---

## 10. References

- `form/01-global-plan.md` — Original global plan with full Rocq code sketches
- `form/02-Rocq.md` — Detailed Rocq implementation with all Phase 1–5b code
- `form/03-Lean.md` — Lean 4 port specification with Phase L0–L5 code
- `config/skills/pycsl-software-architecture/SKILL.md` — Pipeline architecture
- `config/skills/rocq-prover/SKILL.md` — Rocq proof tactics reference
- `config/skills/pycsl-annotate/SKILL.md` — Contract syntax and annotation rules
