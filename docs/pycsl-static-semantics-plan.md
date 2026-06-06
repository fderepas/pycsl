# Plan: PyCSL Static Semantics Reference

**Goal:** Produce `docs/pycsl-static-semantics-reference.md` — the formal
specification of PyCSL's well-formedness rules, type system, and scope
resolution.

**Source of truth:** `test-suite/annotations.md` (paragraph numbering
preserved), `Module3_Weaver.py`, `Module4_SemanticAnalyzer.py`.

---

## 1  Scope

The static semantics reference defines the judgement:

$$\Gamma \vdash_{\text{wf}} A \;\text{ok}$$

meaning "annotation $A$ is well-formed in context $\Gamma$". A syntactically
correct annotation (per the concrete syntax) may still be rejected if it
violates scope rules, type constraints, or usage restrictions.

This document covers:

- **Context construction** ($\Gamma$): how the symbol table is built from
  Python function signatures, local assignments, class fields, and ghost
  variables.
- **Variable resolution:** which names are in scope for each annotation kind.
- **Type mapping:** how Python type hints are mapped to the specification
  logic's type universe (`int`, `list`, `Any`).
- **Well-formedness rules** for each directive and expression form.
- **Error conditions:** what triggers `PyCSLSemanticError`.

The document does NOT define the denotation of annotations (translational
semantics) — only which annotations are accepted or rejected.

---

## 2  Structure (mirrors `annotations.md` paragraph numbering)

### §1  Context Construction

_Prerequisite for all subsequent sections._

#### §1.1  Function scope ($\Gamma_f$)

Define how `Module4_SemanticAnalyzer.visit_FunctionDef` builds the scope:

1. **Arguments:** For each `arg` in `node.args.args` (excluding `self`),
   add $\text{arg.name} : \tau$ where $\tau = \text{type\_hint}$ or `Any`.
2. **Local variables:** Walk `ast.Assign` and `ast.AnnAssign` in the function
   body; add each target name with its annotation type (or `Any`).
3. **Ghost variables:** Walk `csl_ghost_assigns`; add each target as `int`.

Formally:

$$\Gamma_f = \Gamma_{\text{args}} \cup \Gamma_{\text{locals}} \cup \Gamma_{\text{ghost}}$$

#### §1.2  Class scope ($\Gamma_c$)

Define how `visit_ClassDef` builds the field table:

- Walk `__init__` body for `self.field = expr` and `self.field: T = expr`.
- Fields are available in class invariant expressions and in method scopes
  (via `self.field` syntax).

#### §1.3  Module scope ($\Gamma_m$)

Define how `visit_Module` collects:
- `shared` variable declarations (name → mutex mapping)
- `mutex_invariant` declarations
- `lock_order` declarations

#### §1.4  Type mapping function $\tau$

$$\tau(\texttt{int}) = \text{int}, \quad \tau(\texttt{list}) = \text{list}, \quad \tau(\texttt{bool}) = \text{int}, \quad \tau(\_) = \text{Any}$$

---

### §2  Directive Well-Formedness

_Corresponds to annotations.md §2._

For each directive, define the well-formedness judgement:

#### §2.1  Function/Method Contracts

| § | Directive | Well-formedness rule |
|---|-----------|---------------------|
| 2.1.1 | `requires` | $\Gamma_f \vdash e : \text{ok}$; $\texttt{\\result} \notin \text{FV}(e)$ |
| 2.1.2 | `ensures` | $\Gamma_f \cup \{\texttt{\\result}\} \vdash e : \text{ok}$ |
| 2.1.3 | `assigns` | Each target $t$ must be: a variable in $\Gamma_f$, a `self.field` in $\Gamma_c$, an `AssignsRegion` with list-typed base, or `\nothing` |
| 2.1.4 | `\variant` | $\Gamma_f \vdash e : \text{ok}$ |
| 2.1.5 | `\variant` (structural) | $\Gamma_f \vdash e : \text{ok}$; ordering name must be a valid CNAME |
| 2.1.6 | `\diverges` | No expression to check; presence noted |
| 2.1.7 | `\trusted` | No expression to check; presence noted |
| 2.1.8 | `bounded_int(N)` | $N$ must be a positive integer literal |
| 2.1.9 | `raises ExcType when cond` | $\Gamma_f \vdash \text{cond} : \text{ok}$; ExcType is a CNAME |
| 2.1.10 | `thread_entry` | No expression to check; only valid with concurrent memory model |

#### §2.2  Loop Contracts

| § | Directive | Well-formedness rule |
|---|-----------|---------------------|
| 2.2.1 | `loop invariant` | $\Gamma_f \vdash e : \text{ok}$; scope is the *enclosing function's* scope |
| 2.2.2 | `loop variant` | $\Gamma_f \vdash e : \text{ok}$ |

#### §2.3  Class Contracts

| § | Directive | Well-formedness rule |
|---|-----------|---------------------|
| 2.3.1 | `class invariant` | $\text{FV}(e) \subseteq \text{dom}(\Gamma_c)$; only field references and constants |

#### §2.4  Program Point Annotations

| § | Directive | Well-formedness rule |
|---|-----------|---------------------|
| 2.4.1 | `label` | Name must be a valid CNAME; no scope check (defines a new label) |
| 2.4.2 | `ghost` assign | Target becomes part of $\Gamma_{\text{ghost}}$; expression must be well-formed |
| 2.4.3 | `ghost` aug-assign | Target must already be in $\Gamma_{\text{ghost}}$ |
| 2.4.4 | `critical` | Mutex must be declared via `#@ shared ... protected_by` |
| 2.4.5 | `acquires` | Same as `critical` |
| 2.4.6 | `releases` | Same as `critical` |

---

### §3  Expression Well-Formedness

_Corresponds to annotations.md §3._

#### §3.1  Atoms

For each atom, define when it is well-formed:

| § | Atom | Well-formedness rule |
|---|------|---------------------|
| 3.1.1 | Number | Always well-formed |
| 3.1.2 | Variable $x$ | $x \in \text{dom}(\Gamma_f)$ |
| 3.1.3 | `self.field` | `field` $\in \text{dom}(\Gamma_c)$; only valid in method context |
| 3.1.4 | `arr[i]` | `arr` $\in \text{dom}(\Gamma_f)$; $\Gamma_f \vdash i : \text{ok}$ |
| 3.1.4b | `arr[i][j]` | `arr` $\in \text{dom}(\Gamma_f)$; $\Gamma_f \vdash i, j : \text{ok}$ |
| 3.1.5 | `\result` | Only valid inside `ensures` clauses |
| 3.1.6 | `\old(e)` | $\Gamma_f \vdash e : \text{ok}$ |
| 3.1.7 | `\at(e, L)` | $\Gamma_f \vdash e : \text{ok}$; $L$ must be a declared label |
| 3.1.8 | `\length(arr)` | `arr` $\in \text{dom}(\Gamma_f)$ |
| 3.1.9 | `\valid(arr, n)` | `arr` $\in \text{dom}(\Gamma_f)$; $\tau(\text{arr}) \in \{\text{list}, \text{List}, \text{Any}\}$ |
| 3.1.10 | `\separated(a, na, b, nb)` | Both bases must be list-typed in $\Gamma_f$ |
| 3.1.11 | `\length2d(a, m, n)` | `a` $\in \text{dom}(\Gamma_f)$; $\Gamma_f \vdash m, n : \text{ok}$ |
| 3.1.12 | `\valid2d(a, i, j)` | Same as `\length2d` |
| 3.1.13 | `\nothing` | Only valid as assigns target |
| 3.1.14 | String literal | Always well-formed |
| 3.1.15 | `\is_sorted(arr, lo, hi)` | `arr` $\in \text{dom}(\Gamma_f)$; $\Gamma_f \vdash \text{lo}, \text{hi} : \text{ok}$ |
| 3.1.16 | `\sum(arr, lo, hi)` | Same as `\is_sorted` |
| 3.1.17 | `f(args)` | `f` must be a known pure function (`assigns \nothing`, not `\diverges`) |
| 3.1.18 | Boolean | Always well-formed |
| 3.1.19 | None | Always well-formed |
| 3.1.20 | `arr[lo:hi]` | `arr` $\in \text{dom}(\Gamma_f)$; $\Gamma_f \vdash \text{lo}, \text{hi} : \text{ok}$ |

#### §3.2  Operators

For each binary/unary operator: both operands must be well-formed.
No type checking on operand types (all integers in the WhyML model).

#### §3.3  Quantifiers

- `\forall x; body`: $\Gamma_f \cup \{x : \text{int}\} \vdash \text{body} : \text{ok}$
- Bound variable $x$ shadows any $x$ in $\Gamma_f$.
- Nesting: inner quantifier extends the context further.

#### §3.4  Assigns Targets

- `\nothing`: always valid
- Variable $x$: $x \in \text{dom}(\Gamma_f)$
- `self.field`: `field` $\in \text{dom}(\Gamma_c)$
- `arr[lo..hi]`: `arr` $\in \text{dom}(\Gamma_f)$, $\tau(\text{arr}) \in \{\text{list}, \text{List}, \text{Any}\}$

---

### §4  Unsupported Constructs

_Corresponds to annotations.md §4._

Explicitly state that these are rejected at parse time (not static
semantics), with the exception of §4.1 (pure function calls) which
imposes a static semantics constraint.

### §4.1  Pure Function Eligibility

A function $f$ may appear in a contract expression iff:

1. $f$ has `#@ assigns \nothing`
2. $f$ is not annotated `#@ \diverges`
3. $f$ is in scope (defined in the same module or imported)

This check is performed during Module4's scope analysis.

---

### §5  Memory Model Constraints

_Corresponds to annotations.md §5._

| § | Memory Model | Additional static constraints |
|---|-------------|-------------------------------|
| 5.1 | Hoare | None (default) |
| 5.2 | Typed | `\valid` and `\separated` require list-typed params |
| 5.3 | Store | Same as Typed |
| 5.4 | Concurrent | `shared` declarations required; `critical`/`acquires`/`releases` checked; lock_order required for nested acquire |

#### §5.4  Concurrent Model Well-Formedness

1. **Protected-access check:** every read/write to a `shared` variable must
   occur inside a `critical` or `acquires` block for its protecting mutex.
2. **Lock-order check:** nested mutex acquisitions must respect the declared
   `lock_order` (if present). If absent and nesting occurs → error.
3. **Mutex invariant scope:** invariant expression for mutex $M$ may only
   reference variables protected by $M$.

---

### §6–§7  Class Contracts and \old/\at

_Corresponds to annotations.md §6–§7._

- `\old(e)`: $e$ must reference only function parameters and `self.field`
  values available at function entry.
- `\at(e, L)`: label $L$ must have been declared before the annotation
  that references it (forward references are invalid).

---

## 3  Methodology

1. **Read** `Module4_SemanticAnalyzer.py` line by line, extracting every
   check that raises `PyCSLSemanticError`.
2. **Map** each check to the corresponding annotations.md paragraph.
3. **Formalize** each check as an inference rule using the notation:

$$\frac{\text{premises}}{\Gamma \vdash A : \text{ok}}$$

4. **Identify gaps:** any paragraph in annotations.md that has no
   corresponding check in Module4 (under-specified) or any check in
   Module4 that has no paragraph (undocumented).
5. **Write** the reference document section by section.

---

## 4  Verification

- For each well-formedness rule, there should be a **positive** test
  (annotations.md reference test that passes) and a **negative** test
  (test that triggers `PyCSLSemanticError`).
- Cross-check against `test-suite/corpus/pycsl-reference/` for coverage.
- Tests 0254, 0255 (concurrent semantic errors) serve as negative tests
  for §5.4.

---

## 5  Estimated Effort

| Phase | Effort |
|-------|--------|
| Extract all semantic checks from Module4 | 3h |
| Formalize as inference rules | 4h |
| Write §1–§5 with examples | 4h |
| Gap analysis (Module4 vs annotations.md) | 2h |
| Negative test coverage review | 2h |
| **Total** | **~15h** |
