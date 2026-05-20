# From Formal Proofs to PyCSL Contracts — Sub-Plan

> Companion to `self-annotate-plan.md`.  
> Details the methodology for transforming the mechanized soundness proofs
> in `src/formal-semantics/rocq/` and `src/formal-semantics/lean/` into
> concrete `#@` annotations on the PyCSL implementation.

---

## 0. The Problem: What Does "Proof → Contract" Actually Mean?

The parent plan (`self-annotate-plan.md` §3) says:

> "Each WP rule in Phase4_WP.v / WP.lean maps to one function in Module6."

But this glosses over the central difficulty: **the formal proofs reason
about a denotational model (association-list state, mathematical integers,
inductively-defined AST), while the implementation operates on Python
dicts, string-building, JSON IR, and WhyML code generation**. There is no
direct syntactic correspondence between a Rocq `Fixpoint` clause and a
Python `if/elif` branch.

This document makes the translation methodology precise.

---

## 1. Two Distinct Semantic Gaps

### Gap A — Abstraction Refinement

The formal semantics models state as `list (ident × val)` and expressions
as inductive types. The implementation represents state as Python
dictionaries, WhyML strings, and a multi-pass pipeline. Every formal
theorem implicitly assumes:

- Variables are unbounded integers (no machine word overflow).
- The state is a total function from identifiers to values.
- Array access is bounds-checked and returns 0 on out-of-range.
- Expression evaluation is pure and terminating.

To derive contracts from the formal model, each of these assumptions
must be made explicit as a `#@ requires` precondition, or the abstraction
gap must be argued away.

**Relevant research:**

- Leroy, X. (2009). "Formal verification of a realistic compiler."
  *Communications of the ACM*, 52(7), 107–115.
  — The CompCert project faces the same gap: the formal semantics of
  Clight is in Coq, but the compiler passes are OCaml extracted from
  Coq. The approach is *extraction + simulation proofs*. PyCSL cannot
  extract (the implementation is hand-written Python), so we must
  instead *annotate* the Python to bridge the gap.

- Appel, A. W. (2011). "Verified Software Toolchain."
  *ESOP 2011*, LNCS 6602, 1–17. Springer.
  — VST bridges C code and separation-logic specifications through
  "Verifiable C" annotations. Our `#@` contracts play the same role
  as VST's `/*@ ... */` ACSL annotations.

### Gap B — Structural Mismatch

The formal model is a *Fixpoint* (recursive function) over inductive
`stmt`. The implementation is an *imperative* Python method with
`if/elif/elif/.../else` chains, mutable accumulator strings, and
auxiliary calls. There is no 1:1 mapping from Rocq case arms to Python
branches.

**Relevant research:**

- Filliâtre, J.-C. & Paskevich, A. (2013). "Why3 — Where Programs Meet
  Provers." *ESOP 2013*, LNCS 7792, 125–128. Springer.
  — Why3's own design philosophy: contracts bridge the gap between a
  mathematical specification (in WhyML's logic) and an imperative
  implementation (in WhyML's programming language). The key insight is
  that the contract language is *shared* between the mathematical model
  and the implementation.

- Baudin, P. et al. (2021). "ACSL: ANSI/ISO C Specification Language."
  *Frama-C documentation*.
  — ACSL annotations on C code serve the same purpose: bridging a
  formal model (weakest precondition, separation logic) with an
  imperative implementation. PyCSL's `#@` syntax is directly inspired
  by ACSL.

---

## 2. The Translation Methodology

We propose a three-step methodology for each function in the
implementation:

### Step 1 — Identify the Formal Correspondent

For each Python function `f` in the implementation, identify which
formal object(s) it implements:

| Implementation function | Formal correspondent(s) |
|---|---|
| `Module6._stmts_to_whyml` (SAssign branch) | `wp (SAssign x e) Qn Qr Qc pre_st st = Qn (update st x (eval_expr st e))` |
| `Module6._handle_while_stmt` | `wp (SWhile inv var cond body) …` (Phase4_WP.v:45–66) |
| `Module6._handle_assign_stmt` | `wp (SAssign x e) …` (Phase4_WP.v:23–24) |
| `Module6._expr_to_whyml` | `eval_expr` (Phase2_State.v:50–72) |
| `Module6._handle_for_stmt` | `wp (SFor x arr inv var body) …` (Phase4_WP.v:68–94) |
| `Module5._py_stmts_to_ir` (return branch) | `SReturn e` AST constructor (Phase1_AST.v:75) |
| `Module5.visit_ClassDef` | No formal correspondent (classes are §2.2 non-goals) |

Functions with no formal correspondent receive **Layer A** contracts only
(structural preservation: lengths ≥ 0, no data loss, assignments
declared).

### Step 2 — Extract the Logical Content

For a function with a formal correspondent, the proof theorem tells us
exactly what property the function must preserve. The extraction follows
a systematic pattern:

#### 2a. The WP rule becomes the `ensures` clause.

Consider `wp (SAssign x e)`:
```coq
| SAssign x e =>
    Qn (update st x (eval_expr st e))
```

This says: *after emitting WhyML for an assignment, the normal-completion
postcondition `Qn` must hold in the state where `x` has been updated to
`eval_expr(e)`*.

In the implementation, `_handle_assign_stmt` produces a WhyML string.
The *semantic* content of that string is: `x := <whyml_expr>`. The
contract captures that the WhyML output is semantically equivalent to
the formal rule:

```python
#@ ensures \result != ""
#@ ensures is_valid_whyml_assign(\result, stmt["target"], stmt["value"])
```

But the predicate `is_valid_whyml_assign` is not expressible in PyCSL's
current contract language (it would require string parsing). This is the
fundamental challenge — see §3.

#### 2b. The SOS rule becomes the `requires` (well-formedness).

The soundness theorem `pycsl_soundness` requires that `exec st s out`
holds — i.e., the statement is well-formed and the execution terminates.
This translates to `requires` clauses on the implementation:

```python
#@ requires stmt is not None
#@ requires "target" in stmt
#@ requires "value" in stmt
```

These are the implementation-level preconditions that ensure the function
doesn't crash — they are the *refinement* of the formal model's
implicit well-formedness.

#### 2c. The invariant/variant lemma becomes loop annotations.

`Phase5a_WhileInv.v` proves `while_inv_preserved`, which says: if the
invariant holds at loop entry and the variant decreases each iteration,
then the invariant holds at loop exit. In the implementation, the
*loops that iterate over invariants and variants* (the `i_inv_w` and
`i_var_w` loops in `_handle_while_stmt`) must carry their own loop
invariants:

```python
#@ loop invariant 0 <= i_inv_w and i_inv_w <= n_inv_w
#@ loop variant n_inv_w - i_inv_w
```

These are already present in the codebase. The formal proof justifies
*why* these annotations are sufficient.

### Step 3 — Encode as `#@` Annotations

Once the logical content is extracted, it must be encoded in PyCSL's
annotation language. This step faces three technical challenges (§3–§5).

---

## 3. Challenge: The String-Building Barrier

The central obstacle is that Module6 produces **WhyML strings**, and the
formal proofs reason about **abstract syntax trees and state
transformers**. The contracts we can write in PyCSL are about Python-level
values (integers, lists, dictionaries), not about the semantic content of
generated WhyML code.

### 3.1 What We Can Express

PyCSL contracts can assert:
- **Frame conditions**: `#@ assigns self._known_collection_sizes, …`
- **Non-emptiness**: `#@ ensures \result != ""`
- **Length bounds**: `#@ ensures \length(result_lines) >= 0`
- **Pure function markers**: `#@ assigns \nothing`
- **Structural invariants**: `#@ loop invariant 0 <= i and i <= n`
- **Termination**: `#@ loop variant n - i`

### 3.2 What We Cannot Express (Directly)

PyCSL contracts *cannot* currently assert:
- "The generated WhyML string, when parsed, represents the AST
  `SAssign(x, e)`."
- "The generated WhyML is semantically equivalent to the WP rule."
- "The output satisfies the Why3 type checker."

### 3.3 The Workaround: Layered Trust

Following the *Foundational Proof-Carrying Code* (FPCC) approach of
Appel & Felty (2000), we adopt a **layered trust model**:

**Layer 0 (Kernel Trust)** — Rocq + Lean type-checkers.
- The soundness theorem is machine-checked. This is our TCB (Trusted
  Computing Base) for the *mathematics*.

**Layer 1 (Structural Trust)** — PyCSL contracts on the implementation.
- We prove that the implementation's *control flow* mirrors the formal
  model: each statement type is handled, each WP rule arm is visited,
  frame conditions are respected, loops terminate.
- This does NOT prove semantic equivalence of the generated WhyML.
- It DOES prove the implementation doesn't silently drop statements,
  corrupt state, or diverge.

**Layer 2 (Output Trust)** — Why3's own type-checker + SMT solvers.
- When the user runs `pycsl` on their program, Why3 checks the generated
  WhyML. If Why3 accepts it and SMT provers discharge the VCs, the
  output is correct *by construction* (Why3 is part of the TCB).

The combination of Layers 0 + 1 + 2 closes the trust gap:
```
Rocq/Lean prove the WP rules correct (math)
    ↓
PyCSL contracts prove the implementation is structurally faithful
    ↓
Why3 + SMT prove the generated output is semantically valid
```

**Relevant research:**

- Appel, A. W. & Felty, A. P. (2000). "A semantic model of types and
  machine instructions for proof-carrying code."
  *POPL 2000*, 243–253. ACM.
  — Introduces FPCC: layered trust with a small TCB (logic kernel),
  medium trust (type system proofs), and verified compiler output.

- Leroy, X. & Blazy, S. (2008). "Formal verification of a C-like memory
  model and its uses for verifying program transformations."
  *Journal of Automated Reasoning*, 41(1), 1–31.
  — Shows how to stratify a verification effort between memory model
  (Coq), C semantics (Clight), and compiler passes (OCaml).

---

## 4. Challenge: Continuation-Passing Style vs. String Accumulation

### 4.1 The Formal Model's CPS Structure

The WP calculus uses three continuations:
```
wp s Qn Qr Qc pre_st st
```
- `Qn` — normal completion (statement finished, control continues)
- `Qr` — return (early termination via `return`)
- `Qc` — continue (loop body requests next iteration)

This CPS structure is inherent to the mathematical formulation. The
`SSeq` rule composes `wp s1` and `wp s2` by threading `Qn` of s1 into
the initial state of s2:
```coq
wp (SSeq s1 s2) Qn Qr Qc pre_st st =
  wp s1 (fun st' => wp s2 Qn Qr Qc pre_st st') Qr Qc pre_st st
```

### 4.2 The Implementation's String Accumulation

Module6's `_stmts_to_whyml` does not use CPS. It accumulates WhyML
code as a string, using Python exceptions (`Return` exception in WhyML)
for early termination:

```python
def _stmts_to_whyml(self, stmts, local_refs, declared_refs, indent, in_loop):
    # Process stmts[0], get code string
    # Recursively process stmts[1:], get rest string
    # Concatenate: code + ";\n" + rest
```

The `Qn` continuation becomes *string concatenation with ";\n"*.
The `Qr` continuation becomes *WhyML `raise Return`*.
The `Qc` continuation becomes *WhyML `raise PyCSL_Continue`*.

### 4.3 Contracts That Capture This Correspondence

The contracts must express that the three continuations are correctly
realized:

```python
def _stmts_to_whyml(self, stmts, local_refs, declared_refs, indent, in_loop):
    """Emit WhyML for a statement sequence.

    Formal correspondent: wp (SSeq s1 s2) = wp s1 (λst'. wp s2 …) Qr Qc
    """
    #@ requires stmts is not None
    #@ requires \length(stmts) >= 0
    #@ assigns self._known_collection_sizes, self._known_collection_elements
    #@ assigns self._array_locals, self._dict_locals, self._lambda_locals
    #@ assigns self._record_locals, self._has_early_ret
    #@ assigns self._abstract_ops, self._havoc_counter
    #@ ensures \result is not None
```

The `assigns` clause mirrors the formal frame condition: `wp (SSeq s1 s2)`
only modifies the state through `update`, and the implementation only
modifies the mutable fields listed in `assigns`.

For the `Qr` (return) case, the contract must reflect that:
- If any sub-statement is a `SReturn`, the generated WhyML contains a
  `raise Return <expr>` or the function body is wrapped in
  `try … with Return r -> r end`.
- The implementation's `_has_early_ret` flag tracks this.

```python
#@ ensures self._has_early_ret ==> "Return" in \result or "try" in \result
```

This is a *string-level property* — weaker than the semantic property
from the formal proof, but verifiable by PyCSL.

---

## 5. Challenge: Coverage of WP Rule Arms

The `wp` fixpoint in Rocq/Lean has 10 cases:
```
SSkip, SAssign, SAugAssign, SArraySet, SSeq, SIf, SWhile, SFor, SReturn, SContinue
```

The implementation's `_stmts_to_whyml` is a single function with an
`if/elif` chain dispatching on `stmt["stmt"]`. Each branch must be
covered by a contract that traces back to the corresponding WP rule.

### 5.1 Per-Branch Traceability Matrix

| WP Rule | Rocq line | Lean line | M6 dispatch key | M6 handler | Contract strategy |
|---|---|---|---|---|---|
| `wp SSkip` | Phase4_WP.v:21 | WP.lean:16 | `"Pass"` | inline | `assigns \nothing` |
| `wp SAssign` | Phase4_WP.v:23–24 | WP.lean:18–19 | `"Assign"` | `_handle_assign_stmt` | assigns clause; ensures non-empty output |
| `wp SAugAssign` | Phase4_WP.v:26–30 | WP.lean:21–24 | `"AugAssign"` | inline at ~line 1380 | assigns clause; ensures output contains `:=` |
| `wp SArraySet` | Phase4_WP.v:32–35 | WP.lean:26–29 | `"ArraySet"` | inline | assigns clause; ensures output contains `<-` |
| `wp SSeq` | Phase4_WP.v:37–39 | WP.lean:31–32 | sequential recursion | `_stmts_to_whyml` (recursive) | recursive structure; concat with `;\n` |
| `wp SIf` | Phase4_WP.v:41–43 | WP.lean:34–36 | `"If"` | inline at ~line 1485 | ensures output contains `if … then … else` |
| `wp SWhile` | Phase4_WP.v:45–66 | WP.lean:38–53 | `"While"` | `_handle_while_stmt` | loop invariant on `i_inv_w`; variant on `i_var_w` |
| `wp SFor` | Phase4_WP.v:68–94 | WP.lean:55–79 | `"For"` | `_handle_for_stmt` | desugaring correctness (Phase3b_Desugar) |
| `wp SReturn` | Phase4_WP.v:96–97 | WP.lean:81–82 | `"Return"` | inline at ~line 1468 | ensures output contains `raise Return` or bare value |
| `wp SContinue` | Phase4_WP.v:99–100 | WP.lean:84–85 | `"Continue"` | inline at ~line 1478 | ensures output = `raise PyCSL_Continue` |

### 5.2 Cross-Check Between Rocq and Lean Paths

The self-annotation plan calls for two parallel annotation tracks
(Rocq-derived and Lean-derived). For WP rule contracts, the two paths
should produce **identical** contracts because the WP rules are
syntactically identical in both provers.

Differences would indicate:
1. A bug in one of the formal proofs.
2. An abstraction choice made differently in Rocq vs. Lean (e.g., the
   `desugar_correct` lemma is `Admitted` in Rocq but `sorry` in Lean —
   the desugaring correctness is not fully machine-checked in either
   prover).
3. A contract that is expressible in one prover's logic but not the
   other's (unlikely, since PyCSL's contract language is simpler than
   either).

---

## 6. The Soundness Theorem as a Metatheorem on Contracts

The `pycsl_soundness` theorem (Phase5b_Soundness.v:20–59,
Soundness.lean:16–69) says:

```
∀ st s out Qn Qr Qc pre_st,
  exec st s out →
  wp s Qn Qr Qc pre_st st →
  outcomePost Qn Qr Qc out
```

In plain English: *if the program executes to outcome `out`, and the WP
holds in the initial state, then the appropriate postcondition holds in
the final state.*

This is a **metatheorem** about the contract system itself. It does NOT
directly translate to a `#@` annotation. Instead, it justifies *why*
the Layer B contracts (WP rule contracts) are correct:

- Each Layer B contract on `_handle_*_stmt` captures one arm of the WP
  fixpoint.
- The soundness theorem guarantees that if all arms are implemented
  correctly, then the combined system is sound.
- The "if all arms are implemented correctly" part is what the contracts
  verify.

### 6.1 What the Soundness Proof Requires from the Implementation

Reading the proof structure, each case of `pycsl_soundness` applies the
induction hypothesis to sub-statements. This means the implementation
must satisfy:

1. **Compositionality**: `_stmts_to_whyml` must process each statement
   independently, without side effects that corrupt later statements.
   → `#@ assigns` clauses on each handler.

2. **Exhaustiveness**: Every `stmt` type must be handled.
   → The `if/elif` chain must cover all 10 cases (verified by inspection
   + a contract asserting `\result != ""` for all inputs).

3. **Invariant threading**: Loop invariants in the WhyML output must
   appear between `while` and `do`, not after `done`.
   → Structural contract on the string output format.

4. **Variant embedding**: Loop variants must be emitted as `variant { … }`
   clauses.
   → Same structural contract.

### 6.2 What the Soundness Proof Does NOT Require

The soundness proof is *parametric* in the state representation (it
works for any `state` type with `lookup` and `update`). It therefore
does NOT require the implementation to use any particular data structure.

This is why we can use Python dicts, JSON IR, and WhyML strings —
the abstraction refinement gap (§2, Gap A) is tolerated by the
parametricity of the formal model.

**Relevant research:**

- Reynolds, J. C. (1983). "Types, abstraction, and parametric
  polymorphism." *Information Processing 83*, 513–523.
  — Parametricity (the "free theorem") underpins our ability to bridge
  the abstraction gap: the formal model works for *any* state type,
  so it works for Python dicts.

- Wadler, P. (1989). "Theorems for free!"
  *FPCA '89*, 347–359. ACM.
  — Formalizes the parametricity principle: a polymorphic function
  satisfies certain properties "for free" from its type alone.

---

## 7. The Translation for Each Proof File

### 7.1 Phase1_AST.v / AST.lean → Module2 + Module5 Contracts

**What the proof establishes**: The grammar of `stmt`, `expr`,
`contract_expr`, `func_spec` as inductive types with constructors.

**Translation to contracts**: Module2's dataclass definitions must
mirror the inductive types. Each dataclass field corresponds to a
constructor argument. The contract asserts well-formedness:

```python
@dataclass
class Requires:
    #@ class invariant self.expr is not None
    expr: Any
```

For Module5 (IR emitter), the contract asserts that every emitted IR
node corresponds to a valid `stmt` or `expr` constructor:

```python
def _py_stmts_to_ir(self, stmts):
    #@ requires stmts is not None
    #@ ensures \forall i, 0 <= i and i < \length(\result) ==> \result[i] is not None
    ...
```

### 7.2 Phase2_State.v / State.lean → Module6 Expression Evaluator

**What the proof establishes**: `eval_expr`, `eval_bool`, `eval_z`,
`eval_contract` are total functions on the state.

**Translation to contracts**: `_expr_to_whyml` is the implementation
counterpart. It must be pure (no mutable state modification beyond
the abstract-ops accumulator):

```python
def _expr_to_whyml(self, expr_ir, local_refs, ...):
    #@ assigns self._abstract_ops
    #@ ensures \result is not None
```

The `assigns self._abstract_ops` acknowledges that expression evaluation
may trigger abstract operation declarations (e.g., for `getattr`). The
formal model hides this behind the `eval_expr` total function.

### 7.3 Phase3_SOS.v / SOS.lean → Structural Properties of Module6

**What the proof establishes**: The `exec` relation is deterministic
(`exec_deterministic`) and covers all statement types.

**Translation to contracts**: Determinism means that for the same IR
input, `_stmts_to_whyml` must produce the same WhyML output.
This is a *purity-up-to-side-effects* property:

```python
def _stmts_to_whyml(self, stmts, ...):
    #@ assigns self._known_collection_sizes, ...  # listed explicitly
    # Implicit: same input ⟹ same output (determinism from SOS proof)
```

### 7.4 Phase3b_Desugar.v / DesugarDef.lean → For-Loop Handling

**What the proof establishes**: `desugar` transforms `SFor` into an
equivalent `SWhile` with an index variable `_pycsl_idx`. The correctness
lemma `desugar_correct` (Admitted/sorry) requires `fresh_in_stmt`.

**Translation to contracts**: `_handle_for_stmt` must ensure the index
variable doesn't clash with user variables. The `for_idx = "_pycsl_idx"`
constant in the formal model becomes:

```python
def _handle_for_stmt(self, stmt, ...):
    #@ requires stmt["iter_var"] != "_pycsl_idx"
    #@ ensures "_pycsl_idx" in \result or "for_idx" in \result
```

The `Admitted`/`sorry` on `desugar_correct` means this is the weakest
link: we should add a test that exercises for-loop desugaring with
adversarial variable names.

### 7.5 Phase4_WP.v / WP.lean → Module6 Statement Handlers

This is the core translation. See §5.1 for the per-branch matrix.

Each handler's contract has three components:

1. **`requires`**: Well-formedness of the IR node (keys present, types
   correct).
2. **`assigns`**: Frame condition listing all mutable fields modified.
3. **`ensures`**: The output is non-empty and contains the expected
   WhyML keywords.

Example for `_handle_while_stmt`:

```python
def _handle_while_stmt(self, stmt, rest, local_refs, declared_refs, indent, in_loop):
    """Formal correspondent: wp (SWhile inv var cond body) (Phase4_WP.v:45-66)
    
    The WP rule requires:
    1. Invariant holds at entry.
    2. For all states satisfying inv ∧ cond, body preserves inv and
       decreases var.
    3. When ¬cond, Qn holds.
    
    The implementation:
    1. Emits `while <cond> do` with `invariant { <inv> }` and
       `variant { <var> }` clauses.
    2. Emits the body inside the loop.
    3. Why3 checks that the WhyML annotations match the WP rule.
    """
    #@ requires stmt is not None
    #@ requires "test" in stmt
    #@ assigns self._known_collection_sizes, self._known_collection_elements
    #@ assigns self._array_locals, self._dict_locals, self._lambda_locals
    #@ assigns self._record_locals, self._has_early_ret
    #@ assigns self._abstract_ops, self._havoc_counter, self._in_spec
    #@ ensures \result != ""
```

### 7.6 Phase5a_WhileInv.v / WhileInv.lean → Loop Annotations on Loops

**What the proof establishes**: `while_inv_preserved` — if the body
soundness hypothesis holds and the invariant holds at loop entry, then
the invariant holds after arbitrarily many iterations.

**Translation to contracts**: This proof justifies the existing loop
annotations in `_handle_while_stmt`:

```python
#@ loop invariant 0 <= i_inv_w and i_inv_w <= n_inv_w
#@ loop variant n_inv_w - i_inv_w
while i_inv_w < n_inv_w:
    ...
```

The formal proof says: these annotations are *sufficient* to guarantee
correctness. The PyCSL contract system (which is itself proven sound
by `pycsl_soundness`) then verifies them mechanically via Why3.

This is the **self-referential bootstrap**: the tool verifies itself
using the same methodology that it was proven correct for.

### 7.7 Phase5b_Soundness.v / Soundness.lean → Top-Level `transpile`

**What the proof establishes**: The main soundness theorem.

**Translation to contracts**: The top-level `transpile` function
(in `Module6_WhyMLTranspiler.py`) receives the entire contract:

```python
def transpile(self):
    """Formal correspondent: pycsl_soundness (Phase5b_Soundness.v)
    
    The theorem guarantees that if wp holds in the initial state and
    exec terminates, then the postcondition holds in the final state.
    
    The implementation assembles all WhyML components and returns the
    complete .mlw file.
    """
    #@ assigns self._all_record_fields, self._module_func_names
    #@ assigns self._bounded_int, self._current_params, ...
    #@ ensures \result is not None
    #@ ensures \length(\result) > 0
```

---

## 8. Concrete Annotation Strategy per Module

### 8.1 Module6 — Three Passes

**Pass 1 (Frame Conditions)**: For every function in Module6, determine
its `assigns` clause by inspecting all `self.*` mutations. This is
mechanical and does not require reading the formal proofs.

**Pass 2 (WP Rule Linkage)**: For each statement handler, read the
corresponding WP rule in Phase4_WP.v and write a docstring comment
linking the Python function to the formal theorem. Add `ensures`
contracts that capture the *structural* properties of the output.

**Pass 3 (Loop Invariants)**: For every `while` loop in Module6, write
`loop invariant` and `loop variant` annotations. Many already exist.
The remaining ones are in auxiliary loops (e.g., iterating over
shared declarations, type declarations, etc.).

### 8.2 Modules 1–5 — Structural Contracts Only

Modules 1–5 have no direct correspondent in the formal proofs (except
Module2's AST node classes). Contracts are Layer A only:

- `assigns` clauses on every mutating function.
- `ensures \length(...) >= 0` on list-returning functions.
- `loop invariant` / `loop variant` on all loops.
- `assigns \nothing` on pure functions.

### 8.3 Coverage Report Format

The final coverage report (Phase 9 in the parent plan) should be a
table with columns:

```
| Function | Proof File | Theorem/Lemma | Contract Layer | Status |
```

Status values: `annotated-verified`, `annotated-unverified`, `no-contract`
(with justification).

---

## 9. Open Research Questions

### 9.1 Can We Prove Semantic Equivalence?

The Layer 1 contracts verify *structural* properties (frame conditions,
non-empty output, loop termination). They do NOT verify that the generated
WhyML is *semantically equivalent* to the WP rule.

Full semantic equivalence would require either:
1. **Extraction**: Generate the Python implementation from the Rocq/Lean
   proof (à la CompCert). Feasible but would require rewriting PyCSL in
   Coq's extraction-compatible fragment.
2. **Deep embedding**: Model the WhyML string syntax in PyCSL's contract
   language, then express "the output string, when parsed, represents
   the WP rule." This would require extending PyCSL with string-level
   predicates.
3. **Testing**: Execute the generated WhyML on concrete inputs and
   compare with the formal model's evaluation (Phase Tests.v /
   Tests.lean). This is the pragmatic approach.

**Relevant research:**

- Letouzey, P. (2008). "Extraction in Coq: An Overview."
  *CiE 2008*, LNCS 5028, 359–369. Springer.
  — Coq extraction to OCaml/Haskell. Could potentially generate the
  PyCSL transpiler from the formal model, but Python is not a supported
  extraction target.

- Anand, A. et al. (2017). "CertiCoq: A verified compiler for Coq."
  *CoqPL 2017*.
  — Compiles Gallina to C via CPS, with a verified compilation chain.
  The CertiCoq approach could, in principle, be extended to generate
  Python.

### 9.2 What Is the TCB?

After self-annotation, the Trusted Computing Base for PyCSL is:

| Component | Trust level |
|---|---|
| Rocq kernel (8.20) | Machine-checked (highest trust) |
| Lean kernel (4.29) | Machine-checked (highest trust) |
| Why3 kernel + SMT solvers | Machine-checked for Why3; empirical for Z3/Alt-Ergo |
| Python interpreter (3.12) | Empirical (large, battle-tested) |
| PyCSL transpiler (Modules 1–6) | **Structurally verified** via self-annotation |
| PyCSL contract parser (Module2) | Self-referential (parses its own annotations) |

The self-referential nature of Module2 (it parses its own `#@` syntax)
is a classic bootstrapping problem. It is analogous to the C compiler
bootstrapping problem (the C compiler is compiled by a C compiler).

**Relevant research:**

- Thompson, K. (1984). "Reflections on Trusting Trust."
  *Communications of the ACM*, 27(8), 761–763.
  — The classic "trusting trust" attack: a compiler can embed a
  backdoor that reproduces itself. For PyCSL, the analogous concern
  is: if Module2 has a bug that causes it to misparse `#@` annotations,
  the self-annotation would not detect the bug. Mitigation: the
  formal proofs in Rocq/Lean are *external* to Python and do not go
  through Module2.

- Chlipala, A. (2017). "Certified Programming with Dependent Types."
  MIT Press.
  — Chapter 15 discusses proof-producing compilation and the bootstrapping
  problem. The key insight: use an *external* verifier (Rocq/Lean) to
  check the *output* of the self-hosted tool.

---

## 10. Summary

| Aspect | Approach |
|---|---|
| **Gap A** (abstraction refinement) | Layered trust: formal model (Rocq/Lean) + structural contracts (PyCSL) + output verification (Why3) |
| **Gap B** (structural mismatch) | Per-branch traceability matrix linking each `if/elif` arm to a WP rule |
| **String barrier** | Layer 1 contracts verify structural properties; Layer 2 (Why3) verifies semantic output |
| **CPS vs. string accumulation** | `assigns` clauses mirror frame conditions; `Qr`/`Qc` become WhyML exceptions |
| **Coverage** | 10 WP rules → 10 M6 contract groups; cross-checked between Rocq and Lean paths |
| **Metatheory** | `pycsl_soundness` is a metatheorem about the contract system, not itself a contract |
| **TCB** | Rocq + Lean + Why3 + Python interpreter |

### References

1. Appel, A. W. (2011). "Verified Software Toolchain." ESOP 2011.
2. Appel, A. W. & Felty, A. P. (2000). "A semantic model of types and
   machine instructions for proof-carrying code." POPL 2000.
3. Anand, A. et al. (2017). "CertiCoq: A verified compiler for Coq."
   CoqPL 2017.
4. Baudin, P. et al. (2021). "ACSL: ANSI/ISO C Specification Language."
   Frama-C documentation.
5. Chlipala, A. (2017). "Certified Programming with Dependent Types."
   MIT Press.
6. Filliâtre, J.-C. & Paskevich, A. (2013). "Why3 — Where Programs Meet
   Provers." ESOP 2013.
7. Leroy, X. (2009). "Formal verification of a realistic compiler."
   Communications of the ACM, 52(7).
8. Leroy, X. & Blazy, S. (2008). "Formal verification of a C-like memory
   model." Journal of Automated Reasoning, 41(1).
9. Letouzey, P. (2008). "Extraction in Coq: An Overview." CiE 2008.
10. Reynolds, J. C. (1983). "Types, abstraction, and parametric
    polymorphism." Information Processing 83.
11. Thompson, K. (1984). "Reflections on Trusting Trust."
    Communications of the ACM, 27(8).
12. Wadler, P. (1989). "Theorems for free!" FPCA '89.
