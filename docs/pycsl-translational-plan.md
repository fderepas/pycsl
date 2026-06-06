# Plan: PyCSL Translational Semantics Reference

**Goal:** Produce `docs/pycsl-translational-reference.md` — the formal
specification of the translation function $\mathcal{T}$ that maps a valid
Python program annotated with PyCSL contracts to a Why3 WhyML module.

**Source of truth:** `test-suite/annotations.md` (paragraph numbering
preserved), `Module5_IREmitter.py`, `Module6_WhyMLTranspiler.py`.

---

## 1  Scope

### 1.1  What This Document Defines

A translation function

$$\mathcal{T} : \text{AnnotatedPython} \to \text{WhyML}$$

such that if $\text{Why3} \vdash \mathcal{T}\llbracket P \rrbracket \; \textbf{Valid}$
then the original Python program $P$ satisfies its PyCSL annotations.

Because Why3's WP calculus and type system are already formally defined
(Filliâtre & Paskevich, ESOP 2013; mechanized in Coq by Clochard et al.),
the soundness obligation reduces to proving:

$$\text{If } \mathcal{T}\llbracket P \rrbracket \text{ is Valid in Why3, then }
P \models \text{Spec}(P)$$

where $\text{Spec}(P)$ is the set of PyCSL annotations attached to $P$.

### 1.2  What This Document Does NOT Cover

- The concrete syntax of PyCSL (see `pycsl-concrete-syntax-reference.md`)
- The static semantics / well-formedness rules (see `pycsl-static-semantics-reference.md`)
- Why3's internal WP calculus (well-documented in the Why3 literature)
- The SMT encoding of Why3 goals (delegated to Alt-Ergo, Z3, CVC5)

---

## 2  Architecture of the Translation

The actual implementation splits $\mathcal{T}$ into two composed functions:

$$\mathcal{T} = \mathcal{W} \circ \mathcal{I}$$

where:

- $\mathcal{I}$ : AnnotatedPython → IR  (implemented by Module5\_IREmitter)
- $\mathcal{W}$ : IR → WhyML  (implemented by Module6\_WhyMLTranspiler)

The IR is a JSON-like intermediate representation with explicit types:
`Function`, `Class`, `IfElse`, `While`, `Assign`, `Return`, `Assert`,
`Subscript`, `BinOp`, `Call`, etc.

The reference document will define $\mathcal{T}$ directly (Python → WhyML),
noting where the IR boundary falls, but proving soundness on the composed
translation.

---

## 3  Structure (mirrors `annotations.md` paragraph numbering)

### §T.1  Module-Level Translation

_Relates to annotations.md §1 and §9._

$$\mathcal{T}\llbracket \texttt{module} \; M \rrbracket =
  \texttt{module M} \; \{ \text{prelude} \; ; \; \mathcal{T}\llbracket \text{body} \rrbracket \}$$

- **Prelude:** memory model theory imports (`hoare`, `typed`, `store`,
  `concurrent`), `use int.Int`, `use list.List`, `use ref.Ref`, etc.
- **Memory model selection** (§5): determines which prelude modules are
  imported and how mutable state is modelled.

### §T.2  Function Translation

_Corresponds to annotations.md §2.1._

#### §T.2.1  Basic Function

$$\mathcal{T}\llbracket
  \texttt{def f(x1: T1, ...) -> R:} \;
  \texttt{\#@ requires P} \;
  \texttt{\#@ ensures Q} \;
  \texttt{\#@ assigns A} \;
  \texttt{body}
\rrbracket$$

$$= \texttt{let f (x1: } \tau(T1) \texttt{) ... : } \tau(R) \;
  \texttt{requires \{} \mathcal{T}_e\llbracket P \rrbracket \texttt{\}} \;
  \texttt{ensures \{ result } {=} \; \mathcal{T}_e\llbracket Q[\texttt{\\result} \mapsto \texttt{result}] \rrbracket \texttt{\}} \;
  \texttt{= } \mathcal{T}_s\llbracket \text{body} \rrbracket$$

where $\mathcal{T}_e$ is the expression translator and $\mathcal{T}_s$ is
the statement translator.

#### §T.2.2  Recursive Function

When the call graph contains a cycle, use `let rec` with `variant`:

$$\texttt{let rec f (...) variant \{} \mathcal{T}_e\llbracket V \rrbracket \texttt{\} = ...}$$

#### §T.2.3  \trusted Functions

$$\mathcal{T}\llbracket \texttt{def f(...): \#@ \\trusted ...} \rrbracket
= \texttt{val f (...) : R requires \{...\} ensures \{...\}}$$

No body emitted — the contract is assumed as an axiom.

#### §T.2.4  \diverges Functions

Omit the default termination obligation. No `variant` clause emitted.

#### §T.2.5  raises Clauses

$$\texttt{raises \{ E -> } \mathcal{T}_e\llbracket \text{cond} \rrbracket \texttt{ \}}$$

### §T.3  Loop Translation

_Corresponds to annotations.md §2.2._

#### §T.3.1  While Loop

$$\mathcal{T}\llbracket
  \texttt{while C:} \;
  \texttt{\#@ loop invariant I} \;
  \texttt{\#@ loop variant V} \;
  \texttt{body}
\rrbracket$$

$$= \texttt{while } \mathcal{T}_e\llbracket C \rrbracket \texttt{ do} \;
  \texttt{invariant \{} \mathcal{T}_e\llbracket I \rrbracket \texttt{\}} \;
  \texttt{variant \{} \mathcal{T}_e\llbracket V \rrbracket \texttt{\}} \;
  \mathcal{T}_s\llbracket \text{body} \rrbracket \;
  \texttt{done}$$

#### §T.3.2  For Loop (Desugaring)

Python `for x in range(n):` is desugared to a `while` loop:

$$\mathcal{T}\llbracket \texttt{for x in range(n): body} \rrbracket$$

$$= \texttt{let x = ref 0 in} \;
  \texttt{while !x < } \mathcal{T}_e\llbracket n \rrbracket \texttt{ do} \;
  \texttt{invariant \{ 0 <= !x <= } \mathcal{T}_e\llbracket n \rrbracket \texttt{ \}} \;
  \mathcal{T}_s\llbracket \text{body} \rrbracket \; \texttt{;} \;
  \texttt{x := !x + 1} \;
  \texttt{done}$$

User-supplied invariants are merged with the implicit bounds invariant.

#### §T.3.3  For-Each over List

$$\mathcal{T}\llbracket \texttt{for x in arr: body} \rrbracket$$

Desugared to index-based while loop with `arr[!i]` access.

### §T.4  Class Translation

_Corresponds to annotations.md §2.3 and §6._

#### §T.4.1  Class → Record + Module

$$\mathcal{T}\llbracket
  \texttt{class C:} \;
  \texttt{\#@ class invariant I} \;
  \texttt{fields, methods}
\rrbracket$$

$$= \texttt{type c = \{ mutable f1: } \tau(T1) \texttt{; ... \}} \;
  \texttt{invariant \{} \mathcal{T}_e\llbracket I \rrbracket \texttt{\}}$$

Methods become top-level functions with an extra `self: c` parameter.

#### §T.4.2  Constructor (__init__)

$$\mathcal{T}\llbracket \texttt{\_\_init\_\_(self, ...): ...} \rrbracket
= \texttt{let create (...) : c ensures \{} \mathcal{T}_e\llbracket I \rrbracket \texttt{\} = ...}$$

The class invariant appears as a postcondition of the constructor.

### §T.5  Statement Translation ($\mathcal{T}_s$)

| Python | WhyML |
|--------|-------|
| `x = e` | `x := ` $\mathcal{T}_e\llbracket e \rrbracket$ |
| `x += e` | `x := !x + ` $\mathcal{T}_e\llbracket e \rrbracket$ |
| `if C: S1 else: S2` | `if ` $\mathcal{T}_e\llbracket C \rrbracket$ `then` $\mathcal{T}_s\llbracket S1 \rrbracket$ `else` $\mathcal{T}_s\llbracket S2 \rrbracket$ |
| `return e` | $\mathcal{T}_e\llbracket e \rrbracket$ (last expression) |
| `assert e` | `assert {` $\mathcal{T}_e\llbracket e \rrbracket$ `}` |
| `arr[i] = e` | array update via `set arr !i` $\mathcal{T}_e\llbracket e \rrbracket$ |
| `self.f = e` | record field mutation |

### §T.6  Expression Translation ($\mathcal{T}_e$)

_Corresponds to annotations.md §3._

#### §T.6.1  Atoms

| PyCSL | WhyML |
|-------|-------|
| Integer $n$ | $n$ |
| Variable $x$ | `!x` (dereferenced ref) |
| `self.f` | `self.f` (record access) |
| `arr[i]` | `get !arr !i` |
| `\result` | `result` |
| `\old(e)` | `(old ` $\mathcal{T}_e\llbracket e \rrbracket$ `)` |
| `\at(e, L)` | `(at ` $\mathcal{T}_e\llbracket e \rrbracket$ ` 'L)` |
| `\length(arr)` | `length !arr` |
| `\valid(arr, n)` | `0 <= n < length !arr` |
| `\separated(a, na, b, nb)` | `na + nb <= length !a ...` |
| `\is_sorted(arr, lo, hi)` | `forall i j. lo <= i <= j < hi -> get !arr i <= get !arr j` |
| `\sum(arr, lo, hi)` | recursive `sum` function call |
| `\nothing` | (empty assigns frame — implicit) |
| `True` | `True` |
| `False` | `False` |
| `None` | `()` (unit) |

#### §T.6.2  Operators

| PyCSL | WhyML |
|-------|-------|
| `a + b` | $\mathcal{T}_e\llbracket a \rrbracket$ `+` $\mathcal{T}_e\llbracket b \rrbracket$ |
| `a - b` | subtraction |
| `a * b` | multiplication |
| `a // b` | `div` (Euclidean) |
| `a % b` | `mod` |
| `a == b` | `=` |
| `a != b` | `<>` |
| `a < b`, etc. | `<`, `>`, `<=`, `>=` |
| `a and b` | `/\` (logical conjunction) |
| `a or b` | `\/` (logical disjunction) |
| `not a` | `not` |
| `a ==> b` | `->` (implication) |

#### §T.6.3  Quantifiers

$$\mathcal{T}_e\llbracket \texttt{\\forall x; body} \rrbracket
= \texttt{forall x: int. } \mathcal{T}_e\llbracket \text{body} \rrbracket$$

$$\mathcal{T}_e\llbracket \texttt{\\exists x; body} \rrbracket
= \texttt{exists x: int. } \mathcal{T}_e\llbracket \text{body} \rrbracket$$

#### §T.6.4  Function Calls

$$\mathcal{T}_e\llbracket f(e_1, \ldots, e_n) \rrbracket
= \texttt{f } \mathcal{T}_e\llbracket e_1 \rrbracket \ldots \mathcal{T}_e\llbracket e_n \rrbracket$$

### §T.7  Memory Models

_Corresponds to annotations.md §5._

| Model | State representation | Mutable locals | Arrays |
|-------|---------------------|----------------|--------|
| Hoare | `ref` per variable | `let x = ref v` | `ref (array int)` |
| Typed | Same + `\valid`/`\separated` axioms | Same | Same + bounds theory |
| Store | Global store map | `let s = ref (Map.empty)` | Via store |
| Concurrent | Per-thread refs + mutex records | Same as Hoare | Same as Hoare |

#### §T.7.4  Concurrent Model Translation

$$\mathcal{T}\llbracket \texttt{critical m: body} \rrbracket
= \texttt{acquire m; } \mathcal{T}_s\llbracket \text{body} \rrbracket \texttt{; release m}$$

With mutex invariant restored/re-established at acquire/release boundaries.

### §T.8  Ghost and Label Translation

_Corresponds to annotations.md §2.4 and §7._

| PyCSL | WhyML |
|-------|-------|
| `#@ ghost x = e` | `let ghost x = ref ` $\mathcal{T}_e\llbracket e \rrbracket$ |
| `#@ ghost x += e` | `ghost x := !x + ` $\mathcal{T}_e\llbracket e \rrbracket$ |
| `#@ label L` | `'L` (WhyML label) |

### §T.9  Assigns Frame Translation

_Corresponds to annotations.md §3.4._

$$\mathcal{T}\llbracket \texttt{assigns x, self.f, arr[lo..hi]} \rrbracket
= \texttt{writes \{ x, self.f \} ...}$$

Array region assigns emit a frame condition:

$$\forall i. \lnot(\text{lo} \le i < \text{hi}) \Rightarrow \text{arr}[i] = \text{old}(\text{arr}[i])$$

---

## 4  Soundness Argument Outline

The reference document will include a semi-formal soundness argument
structured as follows:

### 4.1  Axiomatization

List all axioms assumed (trusted contracts, library stubs). These are the
trust base.

### 4.2  Preservation Lemmas

For each translation rule $\mathcal{T}\llbracket \cdot \rrbracket$, argue
informally that the WhyML output faithfully represents the Python
semantics:

1. **Expression faithfulness:** $\mathcal{T}_e$ preserves evaluation
   semantics (integer arithmetic maps exactly, list operations map to
   array operations with matching axioms).
2. **Statement faithfulness:** $\mathcal{T}_s$ preserves control flow
   (sequential composition, branching, loops with invariant/variant).
3. **Contract faithfulness:** requires/ensures map one-to-one to WhyML
   pre/postconditions.
4. **Frame faithfulness:** assigns clause maps to WhyML writes +
   unchanged conditions.

### 4.3  Trust Boundaries

Explicitly enumerate what is NOT proven:

- Python runtime behavior (GC, exceptions outside `raises`)
- Integer overflow (unless `bounded_int` is declared)
- Floating-point arithmetic (not supported)
- I/O and side effects beyond the formal model
- External libraries (trusted stubs are axioms)

### 4.4  Relationship to Formal Semantics

Reference the Rocq and Lean proofs in `src/formal-semantics/` that
mechanize the WP calculus soundness for the core language subset.

---

## 5  Methodology

1. **Read** `Module6_WhyMLTranspiler.py` (3002 lines) method by method,
   documenting the mapping for each `_handle_*` and `_emit_*` function.
2. **Read** `Module5_IREmitter.py` (881 lines) to understand the IR schema.
3. **For each annotations.md paragraph**, write the corresponding
   $\mathcal{T}$ rule with a concrete before/after example.
4. **Validate** each rule by running `pycsl --keep-mlw` on the
   corresponding reference test and comparing the generated WhyML
   against the predicted output.
5. **Identify gaps:** any Python/PyCSL construct that is handled in code
   but not documented (or vice versa).

---

## 6  Verification

- For every $\mathcal{T}$ rule, produce a "golden" WhyML output from a
  reference test (via `--keep-mlw`) and archive it.
- Any change to Module5/Module6 that alters the WhyML output for existing
  tests must trigger an update to this reference document.

---

## 7  Estimated Effort

| Phase | Effort |
|-------|--------|
| Read and map Module5 IR schema | 3h |
| Read and map Module6 WhyML emission | 6h |
| Write §T.1–§T.9 with examples | 6h |
| Soundness argument (§4) | 4h |
| Golden output generation | 2h |
| Cross-reference and gap analysis | 2h |
| **Total** | **~23h** |

---

## 8  References

- Filliâtre, J.-C. & Paskevich, A. (2013). *Why3 — Where Programs Meet
  Provers*. ESOP 2013. LNCS 7792.
- Clochard, M. et al. (2018). *Instrumenting a weakest-precondition
  calculus for counterexample generation*. Journal of Logical and
  Algebraic Methods in Programming.
- Baudin, P. et al. (2021). *ACSL: ANSI/ISO C Specification Language*.
  (Inspiration for PyCSL's annotation syntax.)
- Leino, K.R.M. (2010). *Dafny: An Automatic Program Verifier for
  Functional Correctness*. LPAR 2010.
