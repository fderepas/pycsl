# PyCSL Translational Semantics Reference

**Version:** 1.4  
**Date:** 2026-06-01  
**Status:** Normative  
**Source of truth:** `Module5_IREmitter.py`, `Module6_WhyMLTranspiler.py`,
`test-suite/annotations.md`

---

## §1  Introduction

### §1.1  Purpose

This document defines the translation function

$$\mathcal{T} : \text{AnnotatedPython} \to \text{WhyML}$$

that maps a valid Python program annotated with PyCSL contracts to a
Why3 WhyML module.  The function is **sound** in the following sense:

> If $\text{Why3} \vdash \mathcal{T}\llbracket P \rrbracket \;\textbf{Valid}$,
> then $P \models \text{Spec}(P)$.

Because Why3's WP calculus and type system are already formally defined
(Filliâtre & Paskevich, ESOP 2013; mechanized in Coq by Clochard et al.),
the soundness obligation reduces to proving that $\mathcal{T}$ is a
faithful translation — that is, the WhyML output has the same semantic
content as the original annotated Python.

### §1.2  Scope

This document covers:

- The complete translation of every PyCSL construct to WhyML
- All four memory models (Hoare, Typed, Store, Concurrent)
- Concrete before/after examples from the reference test suite
- A semi-formal soundness argument with trust boundaries

This document does **not** cover:

- Concrete syntax of PyCSL (see `pycsl-concrete-syntax-reference.md`)
- Static well-formedness rules (see `pycsl-static-semantics-reference.md`)
- Why3's internal WP calculus (see Why3 Reference Manual)
- SMT encoding of Why3 goals (delegated to Alt-Ergo, Z3, CVC5)

### §1.3  Architecture of $\mathcal{T}$

The implementation decomposes $\mathcal{T}$ into two composed functions:

$$\mathcal{T} = \mathcal{W} \circ \mathcal{I}$$

where:

| Component | Implementation | Role |
|-----------|----------------|------|
| $\mathcal{I}$ | `Module5_IREmitter.py` (881 lines) | AnnotatedPython → IR (JSON) |
| $\mathcal{W}$ | `Module6_WhyMLTranspiler.py` (facade, 159 lines) + `module6_whyml/` (10 mixin/helper modules, ~4,600 lines) | IR → WhyML text |

The **IR** is a JSON-like intermediate representation with typed nodes:
`Function`, `Class`, `While`, `For`, `Assign`, `Return`, `Assert`,
`Subscript`, `BinOp`, `Call`, `GhostAssign`, `Label`, etc.

This reference defines $\mathcal{T}$ directly (Python → WhyML), noting
where the IR boundary falls.

### §1.4  Notation

| Symbol | Meaning |
|--------|---------|
| $\mathcal{T}\llbracket \cdot \rrbracket$ | Full translation (module level) |
| $\mathcal{T}_f\llbracket \cdot \rrbracket$ | Function-level translation |
| $\mathcal{T}_s\llbracket \cdot \rrbracket$ | Statement translator |
| $\mathcal{T}_e\llbracket \cdot \rrbracket$ | Expression translator |
| $\tau(\cdot)$ | Type mapping (Python annotation → WhyML type) |
| `!x` | WhyML dereference of ref cell `x` |
| `x := v` | WhyML ref assignment |

---

## §T.1  Module-Level Translation

_Corresponds to `annotations.md` §1 and §9._

### §T.1.1  Module Structure

$$\mathcal{T}\llbracket \texttt{module } M \rrbracket =
  \texttt{module PyCSL\_Program} \; \{ \; \text{prelude} \; ; \;
  \text{helpers} \; ; \; \text{types} \; ; \;
  \mathcal{T}_f\llbracket \text{functions} \rrbracket \; \}
  \; \texttt{end}$$

Every PyCSL translation produces a single WhyML module named
`PyCSL_Program`.  The module body consists of four sections emitted
in order:

1. **Prelude** — `use` imports for Why3 theories
2. **Helpers** — Division/modulo wrappers, exception declarations
3. **Type declarations** — Record types for classes
4. **Functions** — All translated functions

**Implementation:** `_emit_preamble`, `_emit_type_decls`,
`_emit_function`.

### §T.1.2  Prelude (Theory Imports)

The prelude depends on the memory model and which features are used:

**Always emitted:**
```whyml
module PyCSL_Program
  use int.Int
  use int.EuclideanDivision
  use ref.Ref
```

**Conditionally emitted:**

| Condition | Import |
|-----------|--------|
| Arrays used (Hoare/Concurrent) | `use array.Array` |
| 2D arrays used (Hoare/Concurrent) | `use matrix.Matrix` |
| `min()`/`max()` used | `use int.MinMax` |
| Strings used | `use string.String` |
| Bounded integers declared | `use mach.int.Int{N}` |
| Typed/Store memory model | `use map.Map` + type/predicate decls |

**Implementation:** `_emit_preamble_uses`.

### §T.1.3  Memory Model Prelude

#### Hoare Model (default)

No additional declarations beyond the conditional imports above.

#### Typed Model

```whyml
  use map.Map
  type loc = int
  constant max_addr : int = 1073741824
  val ghost int_mem : ref (map loc int)

  predicate valid (m: map loc int) (base: loc) (n: int) =
    n >= 0 /\ base >= 0 /\ base + n <= max_addr

  predicate separated (a: loc) (na: int) (b: loc) (nb: int) =
    a + na <= b \/ b + nb <= a
```

**Verified example (test 0080):**
```python
#@ ensures \result == 0
def test_zero_literal() -> int:
    return 0
```
→
```whyml
  use map.Map
  type loc = int
  constant max_addr : int = 1073741824
  val ghost int_mem : ref (map loc int)
  predicate valid (m: map loc int) (base: loc) (n: int) = ...
  predicate separated (a: loc) (na: int) (b: loc) (nb: int) = ...

  let test_zero_literal () : int
    ensures  { (result = 0) }
    writes   { int_mem }
  = 0
```

#### Store Model

Same structure as Typed, but the heap variable name is `store` instead
of `int_mem`.

#### Concurrent Model

Same as Hoare for local state, plus shared-state declarations
(see §T.7.4).

### §T.1.4  Helper Functions

#### Division and Modulo Wrappers

When floor division (`//`) or modulo (`%`) appear in function bodies,
helper functions are emitted to enforce the division-by-zero precondition:

```whyml
  let pycsl_div (x: int) (y: int) : int
    requires { [@expl:division by zero] y <> 0 }
    ensures { result = div x y }
  = div x y

  let pycsl_mod (x: int) (y: int) : int
    requires { [@expl:modulo by zero] y <> 0 }
    ensures { result = mod x y }
  = mod x y
```

When `ZeroDivisionError` is declared as a raised exception, the helpers
use `raises` instead of `requires`:

```whyml
  let pycsl_div (x: int) (y: int) : int
    ensures { result = div x y }
    raises { ZeroDivisionError -> y = 0 }
  = if y = 0 then raise ZeroDivisionError else div x y
```

**Note:** In specification contexts (requires/ensures), `//` and `%`
translate directly to `div` and `mod` without the wrapper.

**Implementation:** `_emit_preamble_helpers`.

#### Exception Declarations

When the function body contains early returns or the function declares
`raises`, exception types are emitted:

```whyml
  exception Return int        (* early return with value *)
  exception Return_void       (* early return from void function *)
  exception ValueError        (* user-declared exception *)
  exception ZeroDivisionError (* division-by-zero exception *)
```

**Implementation:** `_emit_preamble_exceptions`.

---

## §T.2  Function Translation

_Corresponds to `annotations.md` §2.1._

### §T.2.1  Basic Function

$$\mathcal{T}_f\llbracket
  \texttt{def f(x}_1\texttt{:}\,T_1\texttt{, ...)} \to R \texttt{:} \;
  \texttt{\#@ requires } P \;
  \texttt{\#@ ensures } Q \;
  \texttt{body}
\rrbracket$$

$$= \texttt{let f (x}_1\texttt{: } \tau(T_1)\texttt{) ... : } \tau(R) \;
  \texttt{requires \{} \mathcal{T}_e\llbracket P \rrbracket \texttt{\}} \;
  \texttt{ensures  \{} \mathcal{T}_e\llbracket Q \rrbracket \texttt{\}} \;
  \texttt{=} \;
  \mathcal{T}_s\llbracket \text{body} \rrbracket$$

**Verified example (test 0001):**
```python
#@ requires x >= 0
#@ ensures \result >= 0
def test_precondition(x: int) -> int:
    return x + 1
```
→
```whyml
  let test_precondition (x: int) : int
    requires { (x >= 0) }
    ensures  { (result >= 0) }
  =
    (x + 1)
```

### §T.2.2  Type Mapping $\tau$

| Python type | WhyML type | Notes |
|-------------|-----------|-------|
| `int` | `int` | Arbitrary precision |
| `bool` | `int` | `True` → `1`, `False` → `0` in body; `true`/`false` in spec |
| `str` | `string` | Why3 `string.String` value type — real content (see §T.6 string ops); memory-model-independent |
| `float` | `int` | **Unsound** — no float theory |
| `list` | `array int` | Hoare/Concurrent model |
| `list` | `loc` + `_len` | Typed/Store model |
| `None` / `-> None` | `unit` | Return type for void functions |
| Class `C` | Record type `c` | Lowercase name |
| No annotation | `int` | Default |

### §T.2.3  Recursive Functions

When the call graph contains a cycle, `let rec` replaces `let`.
A `variant` clause is required for termination:

$$\mathcal{T}_f\llbracket \texttt{def f(...): \#@ \textbackslash variant V ...} \rrbracket
= \texttt{let rec f (...) : R} \;
  \texttt{variant \{} \mathcal{T}_e\llbracket V \rrbracket \texttt{\}} \;
  \texttt{= ...}$$

The plain form `#@ \variant V` emits `variant { V }` with **no** `with` clause. The
**structural** form `#@ \variant (V, ord)` (a named well-founded ordering) additionally
emits `with ord` — this is the only way `with subterm` appears (cf. real test `0050`,
`#@ \variant (n, subterm)`). (Note: bare `variant` without the backslash is the *loop*
variant `#@ loop variant`; the function-level directive is `\variant`.)

**Example (plain recursion variant):**
```python
#@ requires n >= 0
#@ ensures \result >= 0
#@ \variant n
def count_down(n: int) -> int:
    if n <= 0:
        return 0
    return count_down(n - 1) + 1
```
→
```whyml
  let rec count_down (n: int) : int
    requires { (n >= 0) }
    ensures  { (result >= 0) }
    variant  { n }
  =
    try
    if (n <= 0) then begin
      raise (Return 0)
    end else begin
      raise (Return ((count_down (n - 1)) + 1))
    end
    with Return r -> r end
```

**Note:** Early returns in recursive functions use the exception
mechanism (see §T.5.7).

### §T.2.4  Mutually Recursive Functions (SCC)

For strongly connected components (SCCs), the first function uses
`let rec` and subsequent functions use `and`:

```whyml
  let rec f (...) = ...
  and g (...) = ...
```

### §T.2.5  Pure (Logic) Functions

When the function body is a single expression with no mutation,
it is emitted as a `let function`:

```whyml
  let function f (x: int) (y: int) : int
    ensures  { (result = (x + y)) }
  =
    (x + y)
```

**Verified example (test 0020):**
```python
#@ ensures \result == x + y
def test_nothing(x: int, y: int) -> int:
    return x + y
```
→
```whyml
  let function test_nothing (x: int) (y: int) : int
    ensures  { (result = (x + y)) }
  =
    (x + y)
```

### §T.2.5a  Guarded cases (`act` / `given` / `complete` / `disjoint`)

Acts are desugared (Module 3) to ordinary requires/ensures — there is **no** new
WhyML construct. For an act with guard `A` (the conjunction of its `#@ given`):

$$\mathcal{T}\llbracket \texttt{\#@ act b: given A; ensures E} \rrbracket
= \texttt{ensures \{ (old A) -> E \}}$$

$$\mathcal{T}\llbracket \texttt{\#@ act b: given A; requires R} \rrbracket
= \texttt{requires \{ A -> R \}}$$

`complete`/`disjoint` desugar to **function-entry `#@ assert` checkpoints** (not
`ensures`): `Module3_Weaver._desugar_acts` collects them into `entry_cps` and attaches
them to the first body statement, so they are discharged **on all paths** (at entry the
state *is* the pre-state, so the guards need **no `\old`**):

$$\mathcal{T}\llbracket \texttt{\#@ complete b1,b2} \rrbracket
= \texttt{assert \{ A1 || A2 \}} \quad\text{(at function entry)}$$

$$\mathcal{T}\llbracket \texttt{\#@ disjoint b1,b2} \rrbracket
= \texttt{assert \{ not (Ai \&\& Aj) \}} \quad\text{(per unordered pair, at entry)}$$

A per-act `ensures` is tagged `(* act b *)` for traceability. `\old` of a
boolean guard is emitted without `<> 0` coercion (`_to_bool` treats `\old(e)` as
boolean iff `e` is). Because the `complete`/`disjoint` obligations are entry asserts,
they hold on **every** path (not just normal return) — this is the Phase-2 migration that
removed `act`'s earlier normal-return-only caveat.

### §T.2.5b  Statement checkpoints (`#@ assert` / `#@ check`)

A statement-position checkpoint emits a real WhyML obligation before the statement
it precedes (distinct from the Python `assert` statement, which translates to `()`):

$$\mathcal{T}\llbracket \texttt{\#@ assert P} \rrbracket = \texttt{assert \{ P \};}
\qquad
\mathcal{T}\llbracket \texttt{\#@ check P} \rrbracket = \texttt{check \{ P \};}$$

`assert { P }` proves `P` and makes it a hypothesis for the rest of the block;
`check { P }` proves `P` without adding it. `P` is emitted in spec (boolean) context,
so `\old`/comparisons are handled as in a contract.

### §T.2.5c  HAPPY meta-property (`happy` / `\preserves`)

A HAPPY introduces **no** new WhyML construct: Module 3's meta-pass expands it (front-end
only) into the §T.2.5b checkpoints. For a HAPPY `region LO..HI writes self.f outside region
except E`, at each write of `self.f` in every method `m ∉ E`:

$$\mathcal{T}\llbracket \texttt{self.f[i] = v} \rrbracket_{\text{HAPPY}}
= \texttt{check \{ i < LO || i >= HI \};}\ \ \mathcal{T}\llbracket \texttt{self.f[i] = v} \rrbracket$$

$$\mathcal{T}\llbracket \texttt{self.f[a:b] = v} \rrbracket_{\text{HAPPY}}
= \texttt{check \{ b <= LO || a >= HI \};}\ \ \mathcal{T}\llbracket \texttt{self.f[a:b] = v} \rrbracket$$

(an augmented subscript `self.f[i] |= v` is a point write). Each emitted `check` is preceded
by an attribution comment `(* happy <name> @ self.f L<line> *)`, so a failed obligation names
the property and the offending site. For a non-exempt `\trusted`/`\abstract` writer carrying
`#@ \preserves`, the meta-pass synthesizes and attaches the region-preservation postcondition

$$\texttt{ensures \{ forall i. (LO <= i \&\& i < HI) -> self.f[i] = (old self.f[i]) \}}$$

emitted on its `val` (§T.2.6) and thus **assumed** at call sites. The field-subscript term
`self.f[i]` lowers to a subscript of the record field `f` (hoare: `self.f[i]`); `\old(self.f[i])`
to `(old self.f[i])`.

### §T.2.6  Trusted Functions (`\trusted [reviewer: <name>]`)

$$\mathcal{T}_f\llbracket \texttt{def f(...): \#@ \\trusted ...} \rrbracket
= \texttt{val f (...) : R requires \{...\} ensures \{...\}}$$

The keyword `val` declares the function signature with contracts but
**no body**.  The contracts are assumed as axioms — the function is
trusted, not verified.

**Reviewer field has no emission effect.** The optional
`reviewer: <REVIEWER_ID>` clause (§2.1.7 of the concrete-syntax
reference) is consumed at parse time, stored as
`csl_reviewer: str` on the AST node, propagated through Module 5
into the IR's `reviewer` field, but **does not influence the WhyML
output**. The translation produces the same `val` declaration
whether the reviewer field is present or absent.

The field exists for accountability, not for verification:

- `Module5_IREmitter.py:1146` includes `"reviewer": <value>` in the
  function IR so downstream tools (audit scripts, the
  self-annotation mirror-check, future LLM judges) can inspect who
  attested the trust.
- `Module6_WhyMLTranspiler` reads the field but never emits it into
  the `.mlw` file.

A future "trust-chain audit" tool may use the reviewer field to
verify that every `val f` in a compiled `.mlw` traces back to a
known reviewer; that audit lives outside the translation rule.

_Corresponds to `annotations.md` §2.1.7._

### §T.2.7  Abstract Functions (`\abstract`)

$$\mathcal{T}_f\llbracket \texttt{def f(...): \#@ \\abstract ...} \rrbracket
= \texttt{val f (...) : R requires \{...\} ensures \{...\} raises \{...\}}$$

The source directive is the grammar production `abstract_decl` (`#@ \abstract`).
Identical *WhyML shape* to the `\trusted` rule (§T.2.6) — a bodyless
`val` — but a distinct *source* and *policy*. `\trusted` trusts a present
Python body unchecked; `\abstract` declares there is no meaningful body,
so the contract (plus any `#@ proof` axioms) is the complete, sound
definition of an uninterpreted operation. `functions.py:_emit_function`
selects the `val` form when `func["trusted"] or func["abstract"]`, but
`\abstract` does **not** set the trusted flag, so it does not count toward
the 0-`\trusted` policy (`bin/check-no-trusted-stubs.py`).

This is the canonical translation for irreducibly-opaque library stubs —
e.g. `ast.literal_eval`, whose parsed value is uninterpreted but whose
bounded raises set (`ValueError`/`SyntaxError`) makes a `try/except`
wrapper provably total (corpus `0449`).

_Corresponds to `annotations.md` §2.1.14._

### §T.2.7  Diverging Functions (`\diverges`)

The `diverges` keyword omits the termination obligation.  No `variant`
clause is emitted, and WhyML does not require a termination proof:

```whyml
  let f (...) : R
    diverges
  = ...
```

### §T.2.8  Exception-Raising Functions (`raises`)

$$\mathcal{T}_f\llbracket \texttt{\#@ raises E when cond} \rrbracket
= \texttt{raises \{ E ->} \mathcal{T}_e\llbracket \text{cond} \rrbracket \texttt{\}}$$

**Verified example (test 0206):**
```python
#@ ensures \result >= 0
#@ raises ValueError when n < 0
def checked_abs(n: int) -> int:
    if n < 0:
        raise ValueError
    return n
```
→
```whyml
  exception ValueError

  let checked_abs (n: int) : int
    ensures  { (result >= 0) }
    raises { ValueError -> (n < 0) }
  =
    if (n < 0) then begin
      raise ValueError
    end;
    n
```

**Implementation:** `_emit_contracts`, `_emit_function`.

### §T.2.9  _(reserved — colon-separated provenance `proof` directive removed 2026-05-27)_

The provenance-only `#@ proof rocq:` / `#@ proof lean:` (colon-
separated) directive was removed from the language on 2026-05-27.
The companion-proof discipline it documented lives under the
load-bearing `#@ proof rocq <q>` / `#@ proof lean <q>` rule
(§T.2.10, space-separated). The section number is reserved to keep
cross-references stable.

### §T.2.10  Proof Citation (`proof`) — Rocq + Lean as Cross-Validated Spec Sources

$$\mathcal{T}_m\llbracket \texttt{\#@ proof prover qualname} \rrbracket = \texttt{axiom pycsl\_axiom\_<target> : <Why3\_formula>}$$

**Audit independence.** The namespace-aware audit (`pycsl --audit-proof`,
see static-semantics reference §2.1.12) is independent of WhyML
emission. It runs as a short-circuit at the CLI level — `--audit-proof`
parses the cited proof files, reports PASS/FAIL, and exits without
invoking the rest of the pipeline. The translation rule below applies
only when the regular verify path runs.

`proof` produces WhyML output:
`Module6_WhyMLTranspiler` invokes `proof2why3 emit` for each declared
`proof`, which:

1. **Extracts** the theorem statement tagged with
   `pycsl_target="<qualname>"` from the Rocq or Lean source.
2. **Canonicalizes** the statement (alpha-normalize variable names,
   AC-flatten commutative operators, rewrite `nat`/`Nat` to
   `int + ≥ 0` precondition).
3. **Cross-checks** — when both a `rocq` and a `lean` directive reference
   the same target, verifies their canonical forms are equal. This is the
   **"Rocq + Lean as Cross-Validated Spec Sources"** pattern.
4. **Emits** a Why3 `axiom` block in the preamble:

```why3
(* proof rocq:Pycsl.Reference.Gcd.gcd_divides_a
   = proof lean:Pycsl.Reference.Gcd.gcd_divides_a
   (canonical forms verified equal) *)
axiom pycsl_axiom_gcd_divides_a :
  forall a b : int.
    a >= 0 -> b >= 0 -> (a > 0 \/ b > 0) ->
    mod a (gcd a b) = 0
```

**Trust model.** The emitted axiom is trusted because:
- The Rocq kernel and Lean kernel independently verified the theorem.
- The cross-check verified that both formalizations state the same
  property (in canonical form).
- Why3's own type-checker rejects malformed axiom syntax.

**Cross-check statuses** (recorded in the TOML manifest):

| Status | Axiom emitted? | Notes |
|---|---|---|
| `reconciled` | Yes | Both provers agree |
| `rocq-only` | Yes (with warning) | Only Rocq statement found |
| `lean-only` | Yes (with warning) | Only Lean statement found |
| `disagreement` | **No** (pipeline halts) | Canonical forms differ |

**Worked example:** test 0342 (Euclidean GCD) with 5 cross-validated
axioms (gcd_result_nonneg, gcd_divides_a, gcd_divides_b, gcd_0, gcd_step).

_Corresponds to `annotations.md` §2.1.12._

### §T.2.11  Bounded Integers (`assumes bounded_int(N)`)

$$\mathcal{T}_f\llbracket \texttt{def f(...): \#@ assumes bounded\_int(N) ...} \rrbracket
= \texttt{use mach.int.IntN}\;+\;\mathcal{T}_f\llbracket \texttt{def f with } \tau(\texttt{int}) := \texttt{intN} \rrbracket$$

`#@ assumes bounded_int(N)` directs Module 6 to import
`mach.int.IntN` in the preamble and rewrite every `int`-typed
parameter, local, and return type of the annotated function to
`intN`. The directive is consumed at function-emission time
(`assumes` is a PyCSL contract keyword, not a Why3 one); the only
artefacts at the WhyML level are the `use mach.int.IntN` line and
the per-binding `intN` type tag.

**Effect on arithmetic.** Inside the annotated function, `+`, `-`,
`*` over `intN` auto-generate overflow proof obligations from the
`mach.int.IntN` theory's `requires { Int.in_bounds (a + b) }`. The
annotator does not write these — they ride on the type rewrite.

**Supported N.** Module 6 accepts `N` ∈ {8, 16, 32, 64} (per the
Why3 `mach.int` module set). Other values pass the parser
(§2.1.8 of the static-semantics reference) but produce a `use`
error at Why3 compilation time.

_Corresponds to `annotations.md` §2.1 row 8._

---

## §T.3  Loop Translation

_Corresponds to `annotations.md` §2.2._

### §T.3.1  While Loop

$$\mathcal{T}_s\llbracket
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

**Verified example (test 0004):**
```python
#@ requires n >= 0
#@ ensures \result == n * (n - 1) // 2
def test_loop_invariant(n: int) -> int:
    s = 0
    i = 0
    #@ loop invariant s == i * (i - 1) // 2
    #@ loop invariant 0 <= i and i <= n
    #@ loop variant n - i
    while i < n:
        s += i
        i += 1
    return s
```
→
```whyml
  let test_loop_invariant (n: int) : int
    requires { (n >= 0) }
    ensures  { (result = (div (n * (n - 1)) 2)) }
  =
    let s = ref 0 in
    let i = ref 0 in
    s := 0;
    i := 0;
    while (!i < n) do
      invariant { (!s = (div (!i * (!i - 1)) 2)) }
      invariant { ((0 <= !i) && (!i <= n)) }
      variant { (n - !i) }
      s := (!s + !i);
      i := (!i + 1)
    done;
    !s
```

**Key observations:**

1. **Mutable locals become refs:** `let s = ref 0 in` followed by
   `s := 0` (initialization).
2. **Dereference in expressions:** All reads of mutable locals use `!x`.
3. **Division in spec vs body:** `//` in `ensures` → `div` directly;
   `//` in body → `pycsl_div` wrapper.
4. **Multiple invariants:** Each `loop invariant` produces a separate
   `invariant { ... }` clause.

### §T.3.2  For-Range Loop (Desugaring)

$$\mathcal{T}_s\llbracket \texttt{for x in range(n): body} \rrbracket$$

$$= \texttt{let x = ref 0 in} \;
  \texttt{while !x < } \mathcal{T}_e\llbracket n \rrbracket \texttt{ do} \;
  \texttt{invariant \{ 0 <= !x /\textbackslash{} !x <= }
    \mathcal{T}_e\llbracket n \rrbracket \texttt{ \}} \;
  \texttt{variant \{ } \mathcal{T}_e\llbracket n \rrbracket
    \texttt{ - !x \}} \;
  \mathcal{T}_s\llbracket \text{body} \rrbracket \texttt{;} \;
  \texttt{x := !x + 1} \;
  \texttt{done}$$

The desugaring automatically injects:
- A **bounds invariant**: `0 <= !x /\ !x <= n`
- A **variant**: `n - !x`

User-supplied invariants are merged with the implicit bounds invariant.

**Implementation:** `_handle_for_stmt`,
`_classify_iterable`.

### §T.3.3  For-Each over Array

$$\mathcal{T}_s\llbracket \texttt{for x in arr: body} \rrbracket$$

$$= \texttt{let \_idx\_x = ref 0 in} \;
  \texttt{while !\_idx\_x < (length arr) do} \;
  \texttt{invariant \{ ... \}} \;
  \texttt{variant \{ (length arr) - !\_idx\_x \}} \;
  \texttt{let x = ref (!\_idx\_x) in} \;
  \mathcal{T}_s\llbracket \text{body} \rrbracket \texttt{;} \;
  \texttt{\_idx\_x := !\_idx\_x + 1} \;
  \texttt{done}$$

**Verified example (test 0208):**
```python
#@ requires \length(arr) > 0
#@ ensures \result >= 0
def count_positive(arr: list) -> int:
    c = 0
    #@ ghost total = 0
    #@ loop invariant 0 <= c and c <= _idx_i
    #@ loop invariant total == _idx_i
    #@ loop variant \length(arr) - _idx_i
    for i in arr:
        if arr[i] > 0:
            c += 1
    return c
```
→
```whyml
  let count_positive (arr: array int) : int
    requires { ((length arr) > 0) }
    ensures  { (result >= 0) }
  =
    let i = ref 0 in
    let c = ref 0 in
    c := 0;
    let ghost total = ref 0 in
    ghost total := 0;
    let _idx_i = ref 0 in
    while !_idx_i < (length arr) do
      invariant { ((0 <= !c) && (!c <= !_idx_i)) }
      invariant { (!total = !_idx_i) }
      variant { ((length arr) - !_idx_i) }
      let i = ref (!_idx_i) in
      if (arr[!i] > 0) then begin
        c := (!c + 1)
      end;
      _idx_i := !_idx_i + 1
    done;
    !c
```

**Key observation:** The synthetic index variable `_idx_i` is introduced;
user invariants may reference it.

### §T.3.4  For-Each over Generic Iterable

When the iterable is not recognized as an array or `range()`, abstract
operations are emitted:

```whyml
  val iter_length (x: int) : int
  val iter_get (x: int) (i: int) : int
```

These are trusted (uninterpreted) functions, creating a trust boundary.

### §T.3.5  Continue and Break

**Continue:** When the loop body contains `continue`, the body is wrapped
in a try/with block:

```whyml
  while ... do
    ...
    try
      ... body with continue raising PyCSL_Continue ...
    with PyCSL_Continue -> ()
    end
  done
```

**Break:** When the loop body contains `break`, the entire loop is wrapped:

```whyml
  try
    while ... do
      ... body with break raising PyCSL_Break ...
    done
  with PyCSL_Break -> ()
  end
```

### §T.3.6  Allow iteration mutation (`allow_iteration_mutation`)

$$\mathcal{T}_s\llbracket \texttt{\#@ allow\_iteration\_mutation; for x in C: body} \rrbracket
= \mathcal{T}_s\llbracket \texttt{for x in C: body} \rrbracket$$

The annotation has **no WhyML output**. It is consumed entirely at the
pre-transpilation stage: Module 5 propagates the `csl_allow_iteration_mutation`
flag as `allow_iteration_mutation: true` on the IR for-loop node;
Module 4's UB-7.1 check
(`IRScanner.find_iteration_mutations` invoked from
`pycsl.py:_run_pipeline`) honours the flag by skipping the loop. Once
the loop reaches Module 6, the annotation has already been satisfied
and translation proceeds as for an ordinary `for` loop (§T.3.2–§T.3.4).

The boundary is documentary, not verifying — the WhyML emission does
not include any assertion about iterator-state preservation. Treat the
annotation as a static-analysis opt-out, not as a contract.

_Corresponds to `annotations.md` §2.2.3._

---

## §T.4  Class Translation

_Corresponds to `annotations.md` §2.3 and §6._

### §T.4.1  Class → WhyML Record

$$\mathcal{T}\llbracket
  \texttt{class C:} \;
  \texttt{\#@ class invariant I} \;
  \texttt{\_\_init\_\_(self, ...): self.f}_1 = v_1 \ldots
\rrbracket$$

$$= \texttt{type c = \{ mutable f}_1\texttt{: int; ... \}} \;
  \texttt{invariant \{} \mathcal{T}_e\llbracket I \rrbracket \texttt{\}} \;
  \texttt{by \{ f}_1 \texttt{= 0; ... \}}$$

**Verified example (test 0006):**
```python
#@ class invariant self._value >= 0
class Counter:
    def __init__(self):
        self._value = 0

    #@ requires amount >= 0
    #@ ensures self._value == \old(self._value) + amount
    def increment(self, amount: int) -> int:
        self._value += amount
        return self._value
```
→
```whyml
  type counter = { mutable _value: int }
    invariant { (_value >= 0) }
    by { _value = 0 }

  let counter__increment (self: counter) (amount: int) : int
    requires { (amount >= 0) }
    ensures  { (self._value = ((old self._value) + amount)) }
  =
    self._value <- (self._value + amount);
    self._value
```

**Key observations:**

1. **Class name lowercased:** `Counter` → `counter`
2. **Fields are mutable:** `mutable _value: int`
3. **Invariant witness:** `by { _value = 0 }` provides a default
   witness proving the invariant is satisfiable.
4. **Methods become top-level:** `increment` → `counter__increment`
   with explicit `self: counter` parameter.
5. **Field mutation:** `self._value += amount` → `self._value <- ...`
6. **`\old` on fields:** `\old(self._value)` → `(old self._value)`

### §T.4.2  Constructor (`__init__` / `__new__`)

`__init__` is **not** emitted as a callable method; it *drives construction*. A
constructor call `C(...)` lowers to a **fresh WhyML record literal** whose fields are
the declared instance fields (discovered from `__init__`), and the class invariant is an
implicit postcondition (Why3's type-invariant mechanism — the literal must satisfy it).

**Field initialisation (parametrized construction, `base_op.md` Tier A).** Each field is
initialised by, in priority order: (1) a **parametrized override** — if the call arity
matches `__init__`'s formals and the field's `__init__` initialiser is a flat top-level
`self.f = <expr over the params>`, the actual args are substituted into that expression
(`Module5._collect_init_construction` captures the param list + initialiser IR;
`expressions.py::_call_record_constructor` splices the lowered args via a `RawWhyml` IR
node and `_subst_params`); (2) otherwise the field's **type-correct default** —
`Array.make <len> 0` for a list/array field (length from `_array_init_size`), the empty
`map` for dict/set, or the captured int constant (fallback `0`). So `Point(2,3)` with
`self.x=a; self.y=a+b` lowers to `{ x = 2; y = (2 + 3) }`. *Scope:* only scalar (int)
fields take a substituted value; list/dict fields, non-param-dependent inits, and inits
with control flow / method calls / `*args` keep the default witness (sound, less precise).

**`__new__`.** A trivial `__new__` (`return super().__new__(cls)` / `object.__new__(cls)`)
is the default allocation and is accepted (construction proceeds via `__init__`). A
non-trivial `__new__` (caching, singletons, returning another/conditional instance) is
**rejected** at weave time (UB-7.6) — allocation interposition cannot be soundly
represented when `C(...)` is a fresh record literal. See `config/skills/pycsl-ub-catalog`
§7.6; corpus `0495`/`0496`/`0497`.

### §T.4.3  Method Translation

Methods are emitted as top-level `let` functions with the naming
convention `classname__methodname`.  The `self` parameter has the
record type:

```whyml
  let classname__method (self: classname) (arg: int) : int = ...
```

**Implementation:** `_emit_type_decls`.

### §T.4.4  Allow finalizer (`allow_finalizer`)

$$\mathcal{T}\llbracket \texttt{\#@ allow\_finalizer; class C: ...} \rrbracket
= \mathcal{T}\llbracket \texttt{class C: ...} \rrbracket$$

The annotation has **no WhyML output**. It is consumed entirely at
weave time: `Module3_Weaver.visit_ClassDef` records the
`csl_allow_finalizer` flag and uses it to suppress the UB-7.5 hard
reject for classes containing a `def __del__`. Once the class
reaches Module 6, translation proceeds exactly as for any other
class (§T.4.1–§T.4.3).

The `__del__` method itself is **not** translated. PyCSL's WhyML
model has no concept of object lifetime or garbage collection;
modelling the finalizer would either require an unsound
"finalizer runs eventually" axiom or an unprovably-strong
"finalizer runs at well-defined points" axiom. The annotation
documents this gap rather than closing it.

Contracts in the class that reference the finalizer's effect (e.g.
`#@ ensures self._handle == 0` "after finalization") cannot be
verified — Module 4 does not flag such contracts, but Module 6 will
not produce VCs that involve `__del__` either. Annotators should
treat `allow_finalizer` as a class-level boundary marker, not as a
mechanism for proving lifetime-dependent properties.

_Corresponds to `annotations.md` §2.3.2._

---

## §T.5  Statement Translation ($\mathcal{T}_s$)

_Corresponds to `annotations.md` §2 (general flow)._

### §T.5.1  Variable Assignment

**First assignment (declaration):**

$$\mathcal{T}_s\llbracket x = e \rrbracket_{\text{first}}
= \texttt{let x = ref } \mathcal{T}_e\llbracket e \rrbracket
  \texttt{ in}$$

**Subsequent assignment (mutation):**

$$\mathcal{T}_s\llbracket x = e \rrbracket_{\text{later}}
= \texttt{x := } \mathcal{T}_e\llbracket e \rrbracket$$

**Verified example (test 0031):**
```python
#@ ensures \result == x + 1
def test_assigns_variable(x: int) -> int:
    y = x + 1
    return y
```
→
```whyml
  let test_assigns_variable (x: int) : int
    ensures  { (result = (x + 1)) }
  =
    let y = ref 0 in
    y := (x + 1);
    !y
```

**Implementation:** `_handle_assign_stmt`.

### §T.5.2  Augmented Assignment

$$\mathcal{T}_s\llbracket x \mathrel{+}= e \rrbracket
= \texttt{x := !x + } \mathcal{T}_e\llbracket e \rrbracket$$

Similarly for `-=`, `*=`, `//=`, `%=`.

**Implementation:** `_handle_augassign_stmt`.

### §T.5.3  Field Assignment

$$\mathcal{T}_s\llbracket \texttt{self.f = e} \rrbracket
= \texttt{self.f <- } \mathcal{T}_e\llbracket e \rrbracket$$

**Implementation:** `_handle_fieldassign_stmt`.

### §T.5.4  Field Augmented Assignment

$$\mathcal{T}_s\llbracket \texttt{self.f += e} \rrbracket
= \texttt{self.f <- self.f + } \mathcal{T}_e\llbracket e \rrbracket$$

**Implementation:** `_handle_fieldaugassign_stmt`.

### §T.5.5  Array Element Assignment

#### Hoare/Concurrent Model

$$\mathcal{T}_s\llbracket \texttt{arr[i] = e} \rrbracket
= \texttt{arr[}\mathcal{T}_e\llbracket i \rrbracket\texttt{] <- }
  \mathcal{T}_e\llbracket e \rrbracket$$

#### Typed/Store Model

$$\mathcal{T}_s\llbracket \texttt{arr[i] = e} \rrbracket
= \texttt{int\_mem := Map.set !int\_mem (arr + }
  \mathcal{T}_e\llbracket i \rrbracket\texttt{) }
  \mathcal{T}_e\llbracket e \rrbracket$$

**Verified example (test 0120):**
```python
#@ requires \length(arr) >= 1
#@ ensures arr[0] == 0
def test_assigns_elem(arr: list) -> None:
    arr[0] = 0
```
→
```whyml
  let test_assigns_elem (arr: array int) : unit
    requires { ((length arr) >= 1) }
    ensures  { (arr[0] = 0) }
  =
    arr[0] <- 0
```

**Implementation:** `_handle_array_set_stmt`.

### §T.5.6  If-Else Statement

$$\mathcal{T}_s\llbracket \texttt{if C: S1 else: S2} \rrbracket
= \texttt{if } \mathcal{T}_e\llbracket C \rrbracket
  \texttt{ then begin } \mathcal{T}_s\llbracket S_1 \rrbracket
  \texttt{ end else begin } \mathcal{T}_s\llbracket S_2 \rrbracket
  \texttt{ end}$$

Conditions are coerced to boolean using `_to_bool()`.  In specification
contexts, Python boolean operators map directly to WhyML logical
connectives.  In body contexts, comparison results are wrapped in
`(if ... then 1 else 0)` when used as integer values.

**Implementation:** `_handle_if_stmt`.

### §T.5.7  Return Statement

**Terminal return** (last statement in function):

$$\mathcal{T}_s\llbracket \texttt{return e} \rrbracket_{\text{tail}}
= \mathcal{T}_e\llbracket e \rrbracket$$

**Early return** (not the last statement, or inside a loop):

$$\mathcal{T}_s\llbracket \texttt{return e} \rrbracket_{\text{early}}
= \texttt{raise (Return } \mathcal{T}_e\llbracket e \rrbracket \texttt{)}$$

The function body is wrapped in:
```whyml
  try
    ... body ...
  with Return r -> r end
```

**Verified example (test 0102):**
```python
#@ ensures x >= 0 ==> \result == x
#@ ensures x < 0 ==> \result == 0 - x
def test_abs_impl(x: int) -> int:
    if x >= 0:
        return x
    else:
        return 0 - x
```
→
```whyml
  exception Return int

  let test_abs_impl (x: int) : int
    ensures  { ((x >= 0) -> (result = x)) }
    ensures  { ((x < 0) -> (result = (0 - x))) }
  =
    try
    if (x >= 0) then begin
      raise (Return x)
    end else begin
      raise (Return (0 - x))
    end
    with Return r -> r end
```

**Implementation:** `_handle_return_stmt`.

### §T.5.8  Assert Statement

Python `assert` statements are runtime checks.  In the WhyML output
they are **skipped** (emitted as `()`), since PyCSL contracts are the
formal specification — Python asserts are not part of the verification
condition.

**Implementation:** `_stmts_to_whyml`.

### §T.5.9  Raise Statement

$$\mathcal{T}_s\llbracket \texttt{raise E} \rrbracket
= \texttt{raise E}$$

Exception types must be pre-declared (see §T.1.4).

### §T.5.10  Try/Except Statement

$$\mathcal{T}_s\llbracket \texttt{try: S1 except E: S2} \rrbracket
= \texttt{try } \mathcal{T}_s\llbracket S_1 \rrbracket
  \texttt{ with E -> } \mathcal{T}_s\llbracket S_2 \rrbracket
  \texttt{ end}$$

Variables assigned in the try body are pre-declared as refs before the
`try` block to ensure they are in scope in the handler.

**Implementation:** `_handle_try_stmt`.

### §T.5.11  Tuple Unpacking

$$\mathcal{T}_s\llbracket \texttt{a, b = f(x)} \rrbracket
= \texttt{let (\_t0, \_t1) = f x in} \;
  \texttt{a := \_t0; b := \_t1}$$

**Implementation:** `_handle_tuple_unpack_stmt`.

### §T.5.12  Match/Case Statement

Match statements are translated to chained if/else:

$$\mathcal{T}_s\llbracket \texttt{match x: case p1: S1 case p2: S2 ...} \rrbracket$$
$$= \texttt{if } \text{cond}(p_1) \texttt{ then begin } \mathcal{T}_s\llbracket S_1 \rrbracket
  \texttt{ end else if } \text{cond}(p_2) \texttt{ then begin } \mathcal{T}_s\llbracket S_2 \rrbracket
  \texttt{ end ...}$$

Guards are combined with `&&`.

**Implementation:** `_handle_match_stmt`.

---

## §T.6  Expression Translation ($\mathcal{T}_e$)

_Corresponds to `annotations.md` §3._

### §T.6.1  Literals

| Python/PyCSL | WhyML | Context | Notes |
|--------------|-------|---------|-------|
| Integer `n` | `n` | Both | Direct mapping |
| `True` | `true` | Spec | Boolean literal |
| `True` | `1` | Body | Integer encoding |
| `False` | `false` | Spec | Boolean literal |
| `False` | `0` | Body | Integer encoding |
| `None` | `0` | Both | Unit/zero encoding |
| String `"s"` | `"s"` (Why3 string literal) | Both | Real `string.String` content (see §T.6 string ops). Only re-hashed to int where an int is required — a dict key, or an abstract-op arg over a non-string operand |
| `[]` (empty) | `(Array.make 1024 0)` | Body | Fixed-size default |
| `[e0, e1, …]` (non-empty) | `(let _alit = Array.make N e0 in _alit[1] <- e1; …; _alit)` | Body | Concrete array literal |
| `{}` / Dict literal | `(const (None: option int))` | Body | Empty `map int (option int)` (cf. §T.14.1) |

**Implementation:** `_expr_to_whyml`.

### §T.6.2  Variables

**In specification context (requires/ensures):**

$$\mathcal{T}_e\llbracket x \rrbracket_{\text{spec}}
= \texttt{!x} \quad \text{(ref dereferenced)}$$

**In body context:**

$$\mathcal{T}_e\llbracket x \rrbracket_{\text{body}}
= \texttt{!x} \quad \text{(ref dereferenced)}$$

Parameters (non-ref) are used directly without `!`.

**Implementation:** `_handle_var_expr`.

### §T.6.3  Field Access

$$\mathcal{T}_e\llbracket \texttt{self.f} \rrbracket
= \texttt{self.f}$$

Record field access is direct — no dereference needed since `self` is
passed by reference in WhyML's record semantics.

**Implementation:** `_handle_field_get_expr`.

### §T.6.4  Array/List Subscript Access

#### Hoare/Concurrent Model

$$\mathcal{T}_e\llbracket \texttt{arr[i]} \rrbracket
= \texttt{arr[}\mathcal{T}_e\llbracket i \rrbracket\texttt{]}$$

#### Typed/Store Model

$$\mathcal{T}_e\llbracket \texttt{arr[i]} \rrbracket
= \texttt{(Map.get !int\_mem (arr + }
  \mathcal{T}_e\llbracket i \rrbracket\texttt{))}$$

**Implementation:** `_handle_subscript`.

### §T.6.5  Special Atoms

#### `\result`

$$\mathcal{T}_e\llbracket \texttt{\\result} \rrbracket = \texttt{result}$$

Used only in `ensures` clauses (enforced by static semantics §E1).

#### `\old(e)`

$$\mathcal{T}_e\llbracket \texttt{\\old(e)} \rrbracket
= \texttt{(old } \mathcal{T}_e\llbracket e \rrbracket \texttt{)}$$

Special case for field access:
$$\mathcal{T}_e\llbracket \texttt{\\old(self.f)} \rrbracket
= \texttt{(old self.f)}$$

**Verified example (test 0013):**
```python
#@ ensures arr[0] == \old(arr[1])
#@ ensures arr[1] == \old(arr[0])
def test_old_expr(arr: list) -> None:
    tmp = arr[0]
    arr[0] = arr[1]
    arr[1] = tmp
```
→
```whyml
  let test_old_expr (arr: array int) : unit
    ...
    ensures  { (arr[0] = (old arr[1])) }
    ensures  { (arr[1] = (old arr[0])) }
  = ...
```

**Implementation:** `_handle_old_expr`.

#### `\at(e, L)`

$$\mathcal{T}_e\llbracket \texttt{\\at(e, L)} \rrbracket
= \texttt{(}\mathcal{T}_e\llbracket e \rrbracket \texttt{ at L)}$$

Special case for `\at(e, PRE)`:
$$\mathcal{T}_e\llbracket \texttt{\\at(e, PRE)} \rrbracket
= \texttt{(old } \mathcal{T}_e\llbracket e \rrbracket \texttt{)}$$

Typed/Store model with subscript:
$$\mathcal{T}_e\llbracket \texttt{\\at(arr[i], L)} \rrbracket
= \texttt{(Map.get (int\_mem at L) (arr + }
  \mathcal{T}_e\llbracket i \rrbracket\texttt{))}$$

**Implementation:** `_handle_at_expr`.

#### `\length(arr)`

##### Hoare/Concurrent Model

$$\mathcal{T}_e\llbracket \texttt{\\length(arr)} \rrbracket
= \texttt{(length arr)}$$

##### Typed/Store Model

$$\mathcal{T}_e\llbracket \texttt{\\length(arr)} \rrbracket
= \texttt{arr\_len}$$

A sidecar variable holds the array length.

**Implementation:** `_handle_arraylen_expr`.

#### `\valid(arr, n)`

##### Hoare/Concurrent Model

$$\mathcal{T}_e\llbracket \texttt{\\valid(arr, n)} \rrbracket
= \texttt{(n >= 0 \&\& n <= length arr)}$$

##### Typed/Store Model

$$\mathcal{T}_e\llbracket \texttt{\\valid(arr, n)} \rrbracket
= \texttt{(valid !int\_mem arr n)}$$

Uses the predicate declared in the typed model prelude.

**Implementation:** `_handle_valid_expr`.

#### `\separated(a, na, b, nb)`

##### Hoare/Concurrent Model

$$\mathcal{T}_e\llbracket \texttt{\\separated(a, na, b, nb)} \rrbracket
= \texttt{true}$$

**Note:** In the Hoare model, arrays are separate by construction (each
is an independent WhyML array object), so separation is trivially true.

##### Typed/Store Model

$$\mathcal{T}_e\llbracket \texttt{\\separated(a, na, b, nb)} \rrbracket
= \texttt{(separated a na b nb)}$$

Uses the predicate declared in the typed model prelude.

**Implementation:** `_handle_separated_expr`.

#### `\is_sorted(arr, lo, hi)`

$$\mathcal{T}_e\llbracket \texttt{\\is\_sorted(arr, lo, hi)} \rrbracket
= \texttt{(forall \_si : int. lo <= \_si /\textbackslash{} \_si < hi - 1 -> arr[\_si] <= arr[\_si + 1])}$$

**Implementation:** `_handle_issorted_expr`.

#### `\sum(arr, lo, hi)`

$$\mathcal{T}_e\llbracket \texttt{\\sum(arr, lo, hi)} \rrbracket
= \texttt{(pycsl\_sum arr lo hi)}$$

A recursive sum function is defined in the prelude when needed.

**Implementation:** `_handle_sum_node_expr`.

#### `\nothing`

$$\mathcal{T}_e\llbracket \texttt{\\nothing} \rrbracket$$

In the context of `assigns`, indicates that the function modifies no
heap state.  See §T.9 for how this affects frame conditions.

### §T.6.6  Binary Operators

| PyCSL (spec) | WhyML (spec) | PyCSL (body) | WhyML (body) |
|-------------|-------------|-------------|-------------|
| `a + b` | `(a + b)` | `a + b` | `(a + b)` |
| `a - b` | `(a - b)` | `a - b` | `(a - b)` |
| `a * b` | `(a * b)` | `a * b` | `(a * b)` |
| `a // b` | `(div a b)` | `a // b` | `(pycsl_div a b)` |
| `a % b` | `(mod a b)` | `a % b` | `(pycsl_mod a b)` |
| `a == b` | `(a = b)` | `a == b` | `(if a = b then 1 else 0)` |
| `a != b` | `(a <> b)` | `a != b` | `(if a <> b then 1 else 0)` |
| `a < b` | `(a < b)` | `a < b` | `(if a < b then 1 else 0)` |
| `a <= b` | `(a <= b)` | ... | ... |
| `a > b` | `(a > b)` | ... | ... |
| `a >= b` | `(a >= b)` | ... | ... |
| `a and b` | `(a && b)` | `a and b` | `(a && b)` |
| `a or b` | `(a \|\| b)` | `a or b` | `(a \|\| b)` |
| `not a` | `(not a)` | `not a` | `(if not a then 1 else 0)` |
| `a ==> b` | `(a -> b)` | — | — |

**Key distinction:** In specification contexts, operators map to logical
connectives.  In body contexts, comparison and boolean operators are
wrapped in `(if ... then 1 else 0)` to produce integer results.

**Array repeat:** `[0] * n` → `(Array.make n 0)`

**Implementation:** `_handle_binop`.

### §T.6.7  Quantifiers

$$\mathcal{T}_e\llbracket \texttt{\\forall x; body} \rrbracket
= \texttt{(forall x : int. } \mathcal{T}_e\llbracket \text{body} \rrbracket \texttt{)}$$

$$\mathcal{T}_e\llbracket \texttt{\\exists x; body} \rrbracket
= \texttt{(exists x : int. } \mathcal{T}_e\llbracket \text{body} \rrbracket \texttt{)}$$

**Verified example (test 0021/0100):**
```python
#@ ensures \forall i; 0 <= i and i < n ==> arr[i] >= 0
def test_quantifiers(arr: list, n: int) -> None:
```
→
```whyml
    ensures  { (forall i : int. (((0 <= i) && (i < n)) -> (arr[i] >= 0))) }
```

**Note:** Quantified variables are always typed as `int`.

**Implementation:** `_expr_to_whyml` (Forall/Exists cases) in `module6_whyml/expressions.py`.

### §T.6.8  Function Calls

$$\mathcal{T}_e\llbracket f(e_1, \ldots, e_n) \rrbracket
= \texttt{(f } \mathcal{T}_e\llbracket e_1 \rrbracket \ldots
  \mathcal{T}_e\llbracket e_n \rrbracket \texttt{)}$$

**Built-in call translations:**

| Python | WhyML |
|--------|-------|
| `len(arr)` | `(length arr)` |
| `min(a, b)` | `(MinMax.min a b)` |
| `max(a, b)` | `(MinMax.max a b)` |
| `abs(x)` | literal: folded; else `(abs_conv x)` (uninterpreted `val abs_conv (x:int):int`) |
| `int(x)` | `x` (identity) |
| `bool(x)` | `(bool_conv x)` (uninterpreted `val bool_conv (x:int):int`) |
| `isinstance(x, T)` | `(isinstance_check x t)` — uninterpreted `val isinstance_check (x:int)(t:int):bool` (or `isinstance_check_<T>` when `x` is `self`); **not** `true` |
| `hasattr(x, a)` | `(hasattr_check x a)` — uninterpreted `val hasattr_check (x:int)(a:int):bool`; **not** `true` |
| `sum(arr)` | all-literal: folded; else abstract `(sum_1 arr)`. (The contract atom `\sum(arr,lo,hi)` is the one that emits `pycsl_sum` — see §T.6.5.) |

**Implementation:** `_handle_call_expr`.

### §T.6.9  Conditional Expression

$$\mathcal{T}_e\llbracket \texttt{a if C else b} \rrbracket
= \texttt{(if } \mathcal{T}_e\llbracket C \rrbracket
  \texttt{ then } \mathcal{T}_e\llbracket a \rrbracket
  \texttt{ else } \mathcal{T}_e\llbracket b \rrbracket \texttt{)}$$

**Implementation:** `_handle_ifexpr_expr`.

### §T.6.10  Named Expression (Walrus Operator)

$$\mathcal{T}_e\llbracket \texttt{(x := e)} \rrbracket$$

If `x` is already a ref:
$$= \texttt{(begin x := } \mathcal{T}_e\llbracket e \rrbracket
  \texttt{; !x end)}$$

If `x` is new:
$$= \texttt{(let x = ref } \mathcal{T}_e\llbracket e \rrbracket
  \texttt{ in !x)}$$

**Implementation:** `_handle_named_expr_expr`.

### §T.6.11  Lambda Expression

$$\mathcal{T}_e\llbracket \texttt{lambda x: e} \rrbracket
= \texttt{(fun x -> } \mathcal{T}_e\llbracket e \rrbracket \texttt{)}$$

**Implementation:** `_handle_lambda_expr`.

### §T.6.12  Slice Access

$$\mathcal{T}_e\llbracket \texttt{arr[lo:hi]} \rrbracket
= \texttt{(array\_slice arr lo hi)}$$

Where `array_slice` is an abstract trusted operation.

**Implementation:** `_handle_slice_access_expr`.

### §T.6.13  2D Array Operations

$$\mathcal{T}_e\llbracket \texttt{\\length2d(m, rows, cols)} \rrbracket
= \texttt{(m.rows = rows \&\& m.columns = cols)}$$

$$\mathcal{T}_e\llbracket \texttt{\\valid2d(m, r, c)} \rrbracket
= \texttt{(valid\_index m r c)}$$

$$\mathcal{T}_s\llbracket \texttt{m[r][c] = e} \rrbracket
= \texttt{set m r c } \mathcal{T}_e\llbracket e \rrbracket$$

**Implementation:** `_handle_length2d_expr`,
`_handle_valid2d_expr`.

### §T.6.14  F-Strings

F-strings are translated as integer hash values (f-string interpolation is out of scope for
the string-content model — see §T.6.15):

$$\mathcal{T}_e\llbracket \texttt{f"..."} \rrbracket = \text{hash}(\ldots)$$

**Implementation:** `_handle_fstring_expr`.

### §T.6.15  String Operations (runtime `str` → `string.String`)

Runtime `str` is the Why3 `string.String` value type (τ(str) = string; §T.2.2). The logic
symbols `String.length` / `concat` / `String.substring` / structural `=` are usable directly in
**spec** context, but **not** as program (body) values ("Logical symbol … used in a non-ghost
context"). So each body operation is bridged through an abstract `val …_op` whose `ensures` ties
its program result to the logic symbol; the spec uses the logic symbol directly (gated on
`self._in_spec`). A string operand is detected by `_is_string_expr` (a `String` literal, a
`StrConcat`/`StrSub` op, a `str`-typed `Var`, or a `Subscript`/`SliceAccess` whose base is a
string — so `s[a:b] == t` routes to the string path).

| Python (`s`,`t` : str) | Spec lowering | Body bridge (`ensures`) | Impl |
|---|---|---|---|
| `len(s)` | `String.length s` | `str_length_op s` ⊨ `result = String.length s` | `_handle_len_call` |
| `s + t` | `concat s t` | `str_concat_op a b` ⊨ `result = concat a b` | `_handle_binop` |
| `s == t` / `s != t` | `s = t` / `not (s = t)` | `str_eq_op a b` ⊨ `result <-> (a = b)` | `_handle_binop` |
| `s[a:b]` | `String.substring s a (b-a)` | `str_sub_op s lo len` ⊨ `result = String.substring s lo len` **and** in-bounds ⇒ `String.length result = len` | `_handle_slice_access_expr` |
| `s[i]` | `String.substring s i 1` | `str_sub_op s i 1` (length-1 string; no char type) | `_handle_subscript` |
| `needle in haystack` | — | `str_contains_op h n` ⊨ `result <-> (∃ i. 0≤i ∧ i+len n ≤ len h ∧ substring h i (len n) = n)` | `_emit_membership` |
| `s.startswith(p)` | — | `str_startswith_op s p : int`, `result∈{0,1}` and `result=1 <-> substring s 0 (len p) = p` | `_content_string_method` |
| `s.endswith(q)` | — | `str_endswith_op s q : int`, `result=1 <-> substring s (len s-len q) (len q) = q` | `_content_string_method` |
| `s.find(sub)` | — | `str_find_op s sub : int`, `result≥-1` and `result≥0 -> substring s result (len sub) = sub` | `_content_string_method` |

The `str_sub_op` length lemma and the `str_contains_op`/find witnesses are baked into the
bridge `ensures` because the general `String.length (substring …)` / existential-occurrence
algebra otherwise exhausts the SMT solver (the bridge `ensures` are *assumed*, being on an
abstract `val`). `startswith`/`endswith`/`find` apply only to a **simple `str`-typed receiver**;
a chained or non-`str` receiver (`node.name.startswith(…)`) keeps the opaque
predicate-as-`0/1`-op model. **Mixed string/int** comparison (a `str` vs an opaque int, e.g. a
`.decode()` result) reverts to the legacy opaque int-equality by hashing the string side
(`str_hash_op`). **Opaque / deferred:** `upper`/`lower`/`strip`/`replace` (string→string),
`split` (list-of-strings), `.decode`/`.encode` (codec, the bytes↔str boundary), f-strings, and
all code-point / lexicographic reasoning.

**Implementation:** `expressions.py` (`_is_string_expr`, `_content_string_method`,
`_emit_membership`, `_handle_binop`, `_handle_subscript`, `_handle_slice_access_expr`),
`functions.py` (`_param_type_str` + method-param loop → `string`), `preamble.py`
(`use string.String`).

---

## §T.7  Memory Models

_Corresponds to `annotations.md` §5._

### §T.7.1  Hoare Model (Default)

The Hoare model uses WhyML's native `ref` cells and `array` types.

| Concept | Representation |
|---------|---------------|
| Mutable local | `let x = ref v in` |
| Array parameter | `arr: array int` |
| Array access | `arr[i]` |
| Array mutation | `arr[i] <- v` |
| Array length | `(length arr)` |
| Separation | `true` (trivially separate) |

This is the simplest and most efficient model.  The `\valid` and
`\separated` predicates become trivial or are expressed directly in
terms of WhyML array operations.

### §T.7.2  Typed Model

The Typed model introduces a flat memory map for pointer-like reasoning.

| Concept | Representation |
|---------|---------------|
| Heap | `val ghost int_mem : ref (map loc int)` |
| Array base address | `arr : loc` |
| Array length | `arr_len : int` (sidecar) |
| Array access | `(Map.get !int_mem (arr + i))` |
| Array mutation | `int_mem := Map.set !int_mem (arr + i) v` |
| `\valid(arr, n)` | `(valid !int_mem arr n)` — predicate checking bounds |
| `\separated(a, na, b, nb)` | `(separated a na b nb)` — non-overlapping ranges |
| Frame condition | `ensures { forall l: int. ¬in_range(l) -> Map.get !int_mem l = Map.get (old !int_mem) l }` |

### §T.7.3  Store Model

Identical to the Typed model but with the heap variable named `store`
instead of `int_mem`.

### §T.7.4  Concurrent Model

The Concurrent model extends Hoare with shared state and mutex invariants.

#### Shared State Declarations

Module-level variables annotated as shared are emitted as `val` (global
mutable refs):

```whyml
  val counter : ref int
```

#### Mutex Invariants

```whyml
  predicate lock_counter_inv = (!counter >= 0)

  let _check_initial_lock_counter () : unit =
    assert { lock_counter_inv }
```

#### Critical Sections

$$\mathcal{T}_s\llbracket \texttt{critical m: body} \rrbracket$$

On entry (acquire semantics):
```whyml
  (* Havoc shared variables *)
  let _any_counter_0 = any int in
  counter := _any_counter_0;
  assume { lock_counter_inv };
```

On exit (release semantics):
```whyml
  assert { lock_counter_inv };
```

**Verified example (test 0250):**
```python
#@ shared counter
#@ mutex_invariant lock_counter: counter >= 0
#@ \diverges
#@ thread_entry
def worker() -> int:
    #@ critical lock_counter
    counter += 1
    return 0
```
→
```whyml
  val counter : ref int
  predicate lock_counter_inv = (!counter >= 0)
  let _check_initial_lock_counter () : unit =
    assert { lock_counter_inv }

  let worker () : int
    diverges
  =
    let _any_counter_0 = any int in
    counter := _any_counter_0;
    assume { lock_counter_inv };
    counter := !counter + 1;
    assert { lock_counter_inv };
    0
```

**Semantics:** The havoc+assume pattern models the fact that other threads
may have modified shared state arbitrarily, subject to the mutex
invariant.  The assert at exit proves that the critical section
maintains the invariant.

**Implementation:** `_emit_shared_state`,
`_handle_critical_section_stmt`.

#### `protected_by` clause

$$\mathcal{T}\llbracket \texttt{\#@ shared X protected\_by L} \rrbracket
= \mathcal{T}\llbracket \texttt{\#@ shared X} \rrbracket$$

The `protected_by L` clause does **not** change the WhyML emission
for the variable declaration — `shared X` and
`shared X protected_by L` both emit `val X : ref int`. The clause is
consumed by:

1. **`ConcurrencyChecker`** — which checks that every read/write of
   `X` lies inside a `with` block paired with `#@ critical L` (the
   same `L` named by `protected_by`). Violations produce
   `ConcurrencyWarning` records; warnings become hard errors under
   `--strict-concurrent-checks` (UB-7.3).
2. **The mutex-invariant predicate name** — a `#@ mutex_invariant L: P`
   on the same `L` produces `predicate L_inv = P`. The
   `protected_by L` link is what tells Module 6 to havoc `X` (and
   any other variable protected by `L`) at critical-section entry.

A `#@ shared X` without `protected_by` is flagged by the checker as
"unprotected shared state" but the WhyML emission is identical —
the runtime risk is the user's to accept or annotate.

#### `acquires` ≡ `critical` (alias)

$$\mathcal{T}_s\llbracket \texttt{\#@ acquires L; with L: body} \rrbracket
\equiv \mathcal{T}_s\llbracket \texttt{\#@ critical L; with L: body} \rrbracket$$

`#@ acquires L` is an alias for `#@ critical L`: Module 3 weaves both
into the same `csl_critical_mutex` field on the `with` node, and
Module 5 emits the same `CriticalSection` IR node. The two
directives are interchangeable. The alias exists for protocol-style
annotation where the acquire point is named explicitly (e.g. when
the same `with` block is conceptually paired with a later `releases`
line); the WhyML output is identical to the `critical` form
documented above.

_Corresponds to `annotations.md` §10 (line 852)._

#### `releases` — informational, no emission

$$\mathcal{T}_s\llbracket \texttt{\#@ releases L; ...} \rrbracket = \texttt{()}$$

`#@ releases L` is stored on the `with` node (`csl_releases` field)
but produces **no WhyML output**. The release point is implicit at
the end of the `with` block; the explicit `releases` line is
documentation for human readers and for tools that pair acquire/
release points in protocol-style traces. Treat the directive as a
comment with structured shape — Module 6 reads it but emits nothing.

_Corresponds to `annotations.md` §10 (line 855)._

#### `lock_order` — deadlock check, no emission

$$\mathcal{T}_m\llbracket \texttt{\#@ lock\_order m\_1, m\_2, ..., m\_n} \rrbracket = \texttt{()}$$

`#@ lock_order` is a **module-level static check**, not a translation
rule. It produces no WhyML output. The directive declares a total
order on mutex acquisition, and `ConcurrencyChecker._check_function`
flags any function that holds two locks `m_i`, `m_j` simultaneously
with `i > j` (nested `with` blocks in violation of the declared
order).

When `--strict-concurrent-checks` is set, violations become hard
`PyCSLSemanticError`s; otherwise they are warnings (UB-7.3). The
absence of WhyML emission is by design — the proof obligation that
deadlocks cannot occur is *out of scope* for PyCSL's per-function
verification model (deadlock is a global property of concurrent
execution traces). The static order check is the affordable
approximation.

_Corresponds to `annotations.md` §10 (lines 422–425)._

---

## §T.8  Ghost and Label Translation

_Corresponds to `annotations.md` §2.4 and §7._

### §T.8.1  Ghost Variable Declaration

$$\mathcal{T}_s\llbracket \texttt{\#@ ghost x = e} \rrbracket
= \texttt{let ghost x = ref } \mathcal{T}_e\llbracket e \rrbracket
  \texttt{ in}$$

### §T.8.2  Ghost Variable Update

$$\mathcal{T}_s\llbracket \texttt{\#@ ghost x += e} \rrbracket
= \texttt{ghost x := !x + } \mathcal{T}_e\llbracket e \rrbracket$$

Similarly for `ghost x -= e`, `ghost x *= e`.

**Verified example (test 0207):**
```python
#@ requires n >= 0
#@ ensures \result == n
def count_to_n(n: int) -> int:
    i = 0
    #@ ghost count = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop invariant count == i
    #@ loop variant n - i
    while i < n:
        #@ ghost count += 1
        i += 1
    return i
```
→
```whyml
  let count_to_n (n: int) : int
    requires { (n >= 0) }
    ensures  { (result = n) }
  =
    let i = ref 0 in
    i := 0;
    let ghost count = ref 0 in
    ghost count := 0;
    while (!i < n) do
      invariant { ((0 <= !i) && (!i <= n)) }
      invariant { (!count = !i) }
      variant { (n - !i) }
      ghost count := !count + 1;
      i := (!i + 1)
    done;
    !i
```

**Key observations:**

1. Ghost variables are declared with `let ghost` — they exist only
   for specification purposes and are erased at compilation.
2. Ghost updates use `ghost x := ...` — the `ghost` keyword tells
   Why3 the update has no computational effect.
3. Ghost variables can appear in loop invariants and ensures clauses.

**Implementation:** `_handle_ghost_assign_stmt`.

### §T.8.3  Labels

$$\mathcal{T}_s\llbracket \texttt{\#@ label L} \rrbracket
= \texttt{label L in}$$

Labels mark program points for `\at(e, L)` expressions.

**Verified example (test 0014):**
```python
#@ ensures arr[0] == \old(arr[0]) + 2
def test_at_expr(arr: list) -> None:
    #@ label MID
    arr[0] = arr[0] + 1
    arr[0] = arr[0] + 1
```
→
```whyml
  let test_at_expr (arr: array int) : unit
    ...
    ensures  { (arr[0] = ((old arr[0]) + 2)) }
  =
    label MID in
    arr[0] <- (arr[0] + 1);
    arr[0] <- (arr[0] + 1)
```

**Implementation:** `_stmts_to_whyml`.

### §T.8.4  Typed Ghost Variable Declaration

$$\mathcal{T}_s\llbracket \texttt{\#@ ghost x : T = e} \rrbracket
= \texttt{let ghost x = ref (} \mathcal{T}_e\llbracket e \rrbracket \texttt{) in}$$

The declared ghost type `T` determines the WhyML type of `x`. For `ghost_dict`,
the initial expression `\empty_map` lowers to `(const (None: option int))`, which
allows Why3 to infer `x : ref (map int (option int))`.

_Corresponds to `annotations.md` §11.1._

### §T.8.5  Ghost Dict Expression Translation

Ghost dicts use `map int (option int)` in WhyML. Present values are wrapped in
`Some`; absent keys hold `None`.

**Preamble** (auto-emitted by `_scan_preamble_needs` when `needs_ghost_dict` is set):
```whyml
use map.Map
use map.Const
use option.Option
```

**Emission table** — _Corresponds to `annotations.md` §11.2 and §11.9._

| Operation | PyCSL | Emitted WhyML |
|-----------|-------|---------------|
| Empty map | `\empty_map` | `(const (None: option int))` |
| Get | `\map_get(d, k)` | `(match Map.get !d k with \| Some v_ -> v_ \| None -> 0 end)` |
| Set | `\map_set(d, k, v)` | `(Map.set !d k (Some v))` |
| Remove | `\map_remove(d, k)` | `(Map.set !d k None)` |
| Has key | `\has_key(d, k)` | `(Map.get !d k <> None)` |
| Equality | `\map_eq(d1, d2)` | `(forall k: int. Map.get !d1 k = Map.get !d2 k)` |

**Design note:** The option-type representation ensures that `\has_key` is
correct even when the stored value is 0. Under the old sentinel-0 design,
`Map.get !d k <> 0` treated a stored 0 as "absent". With `map int (option int)`,
`Some 0` is unambiguously present, and `None` is unambiguously absent.

**Verified example (tests 0294, 0330):**
```python
#@ ghost d : ghost_dict = \empty_map
#@ loop invariant i > 0 ==> \has_key(d, 1)
#@ loop invariant i > 0 ==> \map_get(d, 1) == 0
while i < n:
    #@ ghost d = \map_set(d, 0, i + 1)
    #@ ghost d = \map_remove(d, 0)
    #@ ghost d = \map_set(d, 1, 0)
    i = i + 1
```

**Implementation:** `_handle_map_empty_expr`, `_handle_map_get_expr`,
`_handle_map_set_expr`, `_handle_map_remove_expr`, `_handle_has_key_expr`,
`_handle_map_eq_expr` in `module6_whyml/expressions.py`. Preamble detection:
`_scan_preamble_needs` (in `module6_whyml/preamble.py`) → `needs_ghost_dict`.

### §T.8.6  Ghost Dict Augmented Assign

$$\mathcal{T}_s\llbracket \texttt{\#@ ghost d += \textbackslash mktuple(k, v)} \rrbracket
= \texttt{ghost d := Map.set } \texttt{!d } k \texttt{ (Some } v \texttt{)}$$

The `\mktuple(k, v)` shorthand is a ghost-dict-specific form of augmented assign
(§2.4.3 in the concrete and static semantics references). It inserts or updates
key `k` with value `v`, wrapping `v` in `Some` per the option-type design.

_Corresponds to `annotations.md` §11.2 row 5._

### §T.8.7  No-exception Predicate Library

When any function in the file declares a `no_exception` clause
(`csl_no_exception` non-empty or `csl_no_exception_all` true), the
preamble emitter `PreambleEmissionMixin._emit_preamble_no_exception_predicates`
lifts the Phase 1 predicate vocabulary from
`src/pycsl/exception_model.py` (`PREDICATE_LIBRARY`) into the WhyML
module:

```why3
predicate no_div_zero (b: int) = b <> 0
predicate in_bounds (n: int) (i: int) = 0 <= i /\ i < n
predicate non_neg_shift (n: int) = n >= 0
```

The predicates are referenced by the per-operation `assert { … }`
injected by §T.8.8 (added by PR 3 of the NoException workplan).

### §T.8.8  No-exception VC Injection (Phase 1 trigger table)

For each IR operation in a function body, Module 6 looks up the
operation key in `exception_model.TRIGGERS`. If the key matches and the
function context's `no_exception_all` or `no_exception_set` covers the
associated exception name, the emitter prepends an `assert { trigger }`
line. The translation rules are:

| Source operation | IR key | Emitted line (when annotated) |
|---|---|---|
| `a / b`, `a // b`, `a % b` | `("binop", "/")`, `("binop", "//")`, `("binop", "%")` | `assert { no_div_zero (T_e[[b]]) };` |
| `divmod(a, b)` | `("call", "divmod")` | `assert { no_div_zero (T_e[[b]]) };` |
| `a << n`, `a >> n` | `("binop", "<<")`, `("binop", ">>")` | `assert { non_neg_shift (T_e[[n]]) };` |
| `arr[i]` (read) | `("subscript", "read")` | `assert { in_bounds (Array.length arr) (T_e[[i]]) };` |
| `arr[i] = v` (write) | `("subscript", "write")` | `assert { in_bounds (Array.length arr) (T_e[[i]]) };` |
| `d[k]` | `("map_get", None)` | `assert { has_key (!d) (T_e[[k]]) };` |
| `d.pop(k)` | `("attr_call", "pop")` | `assert { has_key (!d) (T_e[[k]]) };` |

The injection is gated by the function's `no_exception` context: the
unannotated case emits the operation without an assertion (preserves
backward compatibility — see workplan §11.3). Worked example for
`divide_256(n)`:

```python
#@ requires n != 0
#@ ensures \result == 256 // n
#@ assigns \nothing
#@ no_exception ZeroDivisionError
def divide_256(n: int) -> int:
    return 256 // n
```

translates to:

```why3
let divide_256 (n: int) : int
  requires { n <> 0 }
  ensures { result = div 256 n }
= assert { no_div_zero n };
  pycsl_div 256 n
```

_Corresponds to `annotations.md` §2.1.13._

---

## §T.9  Assigns Frame Translation

_Corresponds to `annotations.md` §3.4._

### §T.9.1  Frame Conditions

The `assigns` clause specifies which mutable state a function may modify.
The translation depends on the memory model.

#### Hoare/Concurrent Model

In the Hoare model, frame conditions are handled implicitly by WhyML's
type system — arrays and refs that are not passed as parameters cannot
be modified.  No explicit `writes` clause is emitted.

#### Typed/Store Model

$$\mathcal{T}\llbracket \texttt{\#@ assigns \\nothing} \rrbracket$$

$$= \texttt{ensures  \{ !int\_mem = old !int\_mem \}}$$

This states that the heap is unchanged.

$$\mathcal{T}\llbracket \texttt{\#@ assigns arr[lo..hi]} \rrbracket$$

$$= \texttt{writes   \{ int\_mem \}} \\
  \texttt{ensures  \{ forall l: int. (not (arr + lo <= l \&\& l < arr + hi))} \\
  \quad\texttt{-> Map.get !int\_mem l = Map.get (old !int\_mem) l \}}$$

This emits both a `writes` clause (declaring that the heap may change)
and a frame postcondition (asserting that all locations outside the
assigned region are unchanged).

### §T.9.2  Multiple Assigns Regions

When multiple regions are assigned, the frame condition excludes all
of them:

$$\forall l.\;\lnot\bigl(\text{in\_region}_1(l) \lor \text{in\_region}_2(l)
  \lor \ldots\bigr) \Rightarrow
  \text{Map.get}(!h, l) = \text{Map.get}(\text{old}\;!h, l)$$

**Implementation:** `_emit_frame_condition`.

---

## §T.10  Soundness Argument

### §T.10.1  Axiomatization (Trust Base)

The following are assumed without proof and constitute the trust base
of the translation:

| Axiom | Source | Risk |
|-------|--------|------|
| Why3's WP calculus is sound | Filliâtre & Paskevich, ESOP 2013 | Low (mechanized in Coq) |
| Alt-Ergo / Z3 / CVC5 are correct | SMT solver implementations | Low (extensively tested) |
| `\trusted` function contracts | User-supplied axioms | **High** — not verified |
| Library stubs (`src/pycsl_lib/`) | Hand-written contracts | **Medium** — not verified |
| Abstract operations (`val iter_length`, etc.) | Transpiler-generated | **Medium** — uninterpreted |
| Integer arithmetic is unbounded | Python semantics | Low (CPython uses bigints) |
| Python's `//` matches Euclidean `div` | Language semantics | **Note**: Python uses floored division, which differs from Euclidean for negative operands |

### §T.10.2  Preservation Lemmas

For each $\mathcal{T}$ rule, we argue informally that the translation
is faithful:

#### Expression Faithfulness

**Claim:** $\mathcal{T}_e$ preserves evaluation semantics.

- **Integer arithmetic:** `+`, `-`, `*` map directly.  WhyML integers
  are arbitrary-precision, matching Python's `int`.
- **Division:** `//` maps to Euclidean `div` (with caveat: Python uses
  floored division for negative operands — see §T.10.1).
- **Comparisons:** `==`, `!=`, `<`, `<=`, `>`, `>=` map to `=`, `<>`,
  `<`, `<=`, `>`, `>=` respectively.
- **Boolean operators:** `and`/`or` map to `&&`/`||` (`identifiers.py`) in
  **both** spec and body context; `not` maps to `not`. (`not` still takes the
  `(if not a then 1 else 0)` form in body context.)
- **Array access:** `arr[i]` maps to WhyML array indexing (Hoare) or
  `Map.get` (Typed/Store), both of which model random-access reads.

#### Statement Faithfulness

**Claim:** $\mathcal{T}_s$ preserves control flow.

- **Sequential composition:** Statements separated by `;` in WhyML.
- **Branching:** `if/else` maps directly to `if/then/else`.
- **Loops:** `while` maps directly with invariant/variant annotations.
- **For loops:** Desugared to `while` with explicit index — the index
  increment and bounds invariant faithfully model `range()` semantics.
- **Early return:** Modeled via exceptions (`raise Return v`), which is
  sound because WhyML exceptions have the same control-flow semantics
  as Python exceptions.

#### Contract Faithfulness

**Claim:** Contracts map one-to-one to WhyML pre/postconditions.

- Each `requires` → one `requires { ... }` clause
- Each `ensures` → one `ensures { ... }` clause
- Each `loop invariant` → one `invariant { ... }` clause
- Each `loop variant` → one `variant { ... }` clause
- Each `raises E when cond` → one `raises { E -> cond }` clause

No contracts are dropped or rewritten during translation.

#### Frame Faithfulness

**Claim:** `assigns` maps to WhyML writes + unchanged conditions.

- `assigns \nothing` → heap equality postcondition
- `assigns arr[lo..hi]` → `writes { int_mem }` + frame postcondition
  excluding the assigned region

### §T.10.3  Trust Boundaries

The following Python features are **not verified** and constitute the
boundary beyond which PyCSL provides no guarantees:

| Feature | Status | Reason |
|---------|--------|--------|
| Python GC / reference counting | Not modeled | WhyML has no GC theory |
| Floating-point arithmetic | Not supported | No float theory in translation |
| Integer overflow | Modeled as unbounded | Matches Python semantics |
| String operations | Hashed to int | Lossy — collisions possible |
| I/O (file, network, print) | Not modeled | Side effects beyond formal model |
| Dynamic typing / duck typing | Static types assumed | Annotation must provide types |
| Exceptions not declared in `raises` | Not tracked | Only declared exceptions modeled |
| `eval()`, `exec()`, `__import__` | Not supported | Dynamic code not analyzable |
| Generators, async/await, yield | Not supported | Not in formal model |
| Metaclasses, descriptors | Not supported | Not in formal model |

### §T.10.4  Relationship to Formal Semantics

The Rocq and Lean proofs in `src/formal-semantics/` mechanize the WP
calculus soundness for the core language subset (arithmetic, assignment,
sequencing, while loops, if/else).  These proofs establish that if the
WP calculus says a program satisfies its specification, then any concrete
execution of the program in the formal operational semantics also
satisfies the specification.

The translation $\mathcal{T}$ maps Python constructs into this verified
core.  Constructs outside the core (exceptions, classes, arrays) are
modeled using Why3's built-in theories, whose soundness is established
by the Why3 project itself.

---

## §T.11  Gap Analysis

### §T.11.1  Translation Gaps

| ID | Gap | Impact | Recommendation |
|----|-----|--------|----------------|
| G1 | Python floored division vs WhyML Euclidean division | For negative operands, `(-7) // 2` is `-4` in Python but `div (-7) 2 = -3` in WhyML | Add a `pycsl_floordiv` helper that matches Python semantics |
| G2 | ~~String hashing is lossy~~ **RESOLVED** | Runtime `str` is now Why3 `string.String` with real content (τ(str)=string; §T.6.15) — content `==`/`+`/`len`/slice/index/`in`/`startswith`/`endswith`/`find` are sound. Residual gaps: no code-point/char type; `upper`/`lower`/`strip`/`replace`/`split` and `.decode`/`.encode` stay opaque; f-strings hash; `str`-keyed dicts still hash the key | Code-point model & string→string transforms deferred |
| G3 | Boolean/int duality | `True + 1 = 2` in Python; in spec `true + 1` is a type error | The spec/body distinction handles this, but mixed use is fragile |
| G4 | `None` mapped to `0` in non-ghost context | `None` and `0` are indistinguishable in WhyML for regular Python values | **Partially resolved:** ghost dicts use `map int (option int)` (§T.8.5), so `\has_key` distinguishes absent keys from keys with value 0. Raw Python `None` in non-ghost context still maps to 0. |
| G5 | Array literals use fixed size 1024 | `[]` becomes `Array.make 1024 0` regardless of actual size | Use dynamic allocation or parametric size |
| G6 | Dict/Set/ListComp are abstract | `{}`, `[x for x in ...]`, `{k:v for ...}` use uninterpreted functions | Implement concrete dict/set theories |
| G7 | `isinstance` / `hasattr` are **uninterpreted** `bool` ops (`isinstance_check` / `hasattr_check`), not concrete | Single type system limitation | Support union types or tagged variants |
| G8 | For-each over non-array iterables | Uses abstract `iter_length` / `iter_get` | Provide concrete implementations per type |
| G9 | `\map_eq` generates a `forall` quantifier | Wide `\map_eq` in deep loop invariants may exceed solver budget | Restrict `\map_eq` to shallow comparisons; prefer explicit key tracking in loop invariants |

### §T.11.2  Undocumented Features

The following translations are implemented in code but were not
specified in `test-suite/annotations.md`:

| Feature | Implementation | Note |
|---------|---------------|------|
| `\result[i]` | Subscript with Result base | Subscript access on return value |
| `bounded_int(N)` | `use mach.int.IntN` | Machine-width integers |
| Chained subscript `arr[i][j]` | Nested Subscript nodes | 2D array access pattern |
| Walrus operator `:=` | `_handle_named_expr_expr` | Python 3.8+ named expressions |
| F-string expressions | `_handle_fstring_expr` | Hashed to integer |
| `with` statement | `_handle_with_stmt` | Context manager protocol |
| `delete` statement | `_handle_delete_stmt` | Variable deletion |

### §T.11.3  Missing Translations

The following constructs appear in Python but have no translation:

| Construct | Status | Workaround |
|-----------|--------|------------|
| `class` inheritance | Not supported | Flatten class hierarchy |
| `@property`, `@staticmethod` | Not supported | Use plain methods |
| `*args`, `**kwargs` | Not supported | Use explicit parameters |
| `yield` / generators | Not supported | Use explicit loops |
| `async` / `await` | Not supported | Use concurrent model |
| `global` / `nonlocal` | Not supported | Use explicit parameter passing |
| List/dict comprehensions (concrete) | Abstract only | Use explicit loops |

---

## §T.14  Body-level data structures (dict, set, multi-arg range, builtins)

Beyond the `#@ ghost ...` ghost variables (§T.7–§T.8), Python function
bodies may declare ordinary mutable dicts, sets, lists, and use a
restricted set of builtins. Module6 lowers each to specific WhyML.
Tests: 0345–0351.

### §T.14.1  Body `dict`

| Form | Why3 emission |
|------|---------------|
| `d = {}` / `d = dict()` | `let d = ref (const (None: option int)) in` |
| `d[k] = v` | `d := map_update_some !d k v` |
| `d[k]` (read) | `(match Map.get !d k with \| Some v_ -> v_ \| None -> 0 end)` |
| `k in d` | `(match Map.get !d k with \| Some _ -> true \| None -> false end)` |
| `k not in d` | `(match Map.get !d k with \| Some _ -> false \| None -> true end)` |

`map_update_some` is a program-level `val` whose `ensures` clause is
`result = Map.set m k (Some v)`. The wrapper is needed because
`Map.set` itself is a logic-only function — Why3 rejects assigning its
result back to a non-ghost ref with "ghost modification in non-ghost
variable".

The body-dict path is triggered when `IRScanner.find_array_and_dict_vars`
adds the variable to `dict_vars` (Call to `dict`, DictLit, SetLit, etc.)
or when `_handle_assign_stmt`'s `is_dict_val` detection fires.

**Preamble uses**: `map.Map`, `map.Const`, `option.Option` are imported
when `_scan_preamble_needs` finds any body dict (`needs_body_dict`).

### §T.14.2  Body `set`

Sets share the dict's `map int (option int)` model. Present keys
map to `Some 0`, absent keys to `None`.

| Form | Why3 emission |
|------|---------------|
| `set()` / `frozenset()` | `(const (None: option int))` |
| `{a, b, c}` (SetLit) | chained `(map_update_some … 0)` on a `const None` base |
| `s.add(x)` (ExprStmt) | `s := map_update_some !s x 0` |
| `s.discard(x)` / `s.remove(x)` | `s := map_update_none !s x` |
| `x in s` / `x not in s` | same `match Map.get` as dict |

`map_update_none` is parallel to `map_update_some` with `ensures
{ result = Map.set m k None }`.

### §T.14.3  Multi-argument `range(start, stop)`

`_classify_iterable` recognises 2-arg `range`:

```
T[[for i in range(start, stop): body]]
  =  let _idx_i = ref start in
     while !_idx_i < stop do
       <invariants> <variants>
       T[[body]];
       _idx_i := !_idx_i + 1
     done
```

For 1-arg `range(n)`, `start` defaults to `0` (existing behaviour).

### §T.14.4  `Optional[T]` and `Union[T1, T2]` return annotations

Module5's `_build_function_ir` handles `ast.Subscript` return
annotations:

- `-> Optional[T]` ⇒ `return_annotation = <T>.lower()`. Since PyCSL
  models `None` as `0`, the optional-ness adds no type-level info
  Module6 could use; the inner type stands.
- `-> Union[T, None]` ⇒ same as Optional (heuristic picks first
  non-`None` component).
- `-> Union[T1, T2, …]` ⇒ heuristic: first non-`None` component (rare
  case; document loudly).

### §T.14.5  `sorted` / `any` / `all` builtins

| Form | Why3 emission |
|------|---------------|
| `sorted(arr)` | abstract `val sorted_1 (a: array int) : array int` |
| `any(arr)` | abstract `val any_1 (a: array int) : bool` |
| `all(arr)` | abstract `val all_1 (a: array int) : bool` |

The abstract vals have no axioms about their results. Contracts cannot
meaningfully assert order or element identity through `sorted_1` etc.

The target of `s = sorted(arr)` is tracked as array-typed (via
`is_array_val` recognising the `(sorted_1 ` prefix), so the pre-decl
path emits `let s = (sorted_1 arr) in` instead of `let s = ref 0 in`.

---

## §T.15  Bytes / Bytearray Type Unification

_Corresponds to annotations.md §12.6._

Python `bytes` and `bytearray` lower to WhyML `array int`. The
translation is structural, not directive-driven — no `#@` syntax
is involved.

### §T.15.1  Parameter typing

For a parameter `p: bytes` or `p: bytearray`, the function
emission (`functions.py`) declares the parameter as
`(p: array int)` in the Hoare memory model (or
`(p: loc) (p_len: int)` in typed/store models, matching the
existing list/array convention).

`T_param(p: bytes) = (p: array int)`
`T_param(p: bytearray) = (p: array int)`

### §T.15.2  Byte-string literal translation

Bytes literals lower to `ArrayLit` of byte-valued `Number` IR
nodes at Module5 emission time:

`T_lit(b'\x00\x01\x02') = {"type": "ArrayLit", "elts":
[{"type": "Number", "value": 0}, {"type": "Number", "value": 1},
{"type": "Number", "value": 2}]}`

The `b'\x00' * N` idiom (single-byte literal × int) composes
naturally with the existing `[default] * size → Array.make`
BinOp handler:

`T_e(b'\x00' * 512) = (Array.make 512 0) : array int`

### §T.15.3  Call-site argument-type inference

`_handle_dotted_call` in `expressions.py` inspects each
argument's emitted WhyML expression. When the expression's prefix
matches one of `(Array.make `, `(array_slice `, `(Array.make_init
`, `(array_copy `, `(array_concat `, OR when the argument is a
bare identifier referring to an `array int`-typed local/param,
the corresponding abstract-val parameter slot is declared as
`array int` (overriding the default `int`).

Before this rule: `struct.unpack(fmt, entry_bytes)` where
`entry_bytes` came from `(array_slice self.disk ...)` produced
the abstract declaration `val struct_unpack_2 (x0: int) (x1: int)
: (int, int)` and the call typechecked against the wrong arity
— Why3 rejected with `array int @rho but is expected to have type
int`.

After this rule: the same call produces `val struct_unpack_2 (x0:
int) (x1: array int) : (int, int)` and the body typechecks
cleanly.

### §T.15.4  Soundness

The change is purely in PyCSL's emission of abstract symbols. No
new axioms about `bytes`-or-`array int` semantics are added —
just type coherence so the WhyML compiles. Soundness is
preserved by Why3: any axiom-free abstract symbol has the same
soundness floor as a `\trusted` declaration (no logical claim,
no commitment beyond typing).

### §T.15.5  Gap

`bytes` semantics — `.encode`, `.decode`, `.ljust`, `.split`, the
byte-range constraint 0..255, `struct.pack` / `struct.unpack`
round-trip — are out of scope of §T.15. Those are
`missing-bytes-struct-feature.md` Phases 2-5 (format-string-aware
emission + Rocq round-trip axioms + per-method bytes-method
modeling).

---

## §T.12  Complete Method Index

### Module5 CSL Node Handlers

| Handler | CSL Node | IR Type |
|---------|----------|---------|
| `_csl_binop` | `CSLBinOp` | `BinOp` |
| `_csl_unaryop` | `CSLUnaryOp` | `UnaryOp` |
| `_csl_field_access` | `CSLFieldAccess` | `FieldGet` |
| `_csl_var` | `CSLVar` | `Var` |
| `_csl_number` | `CSLNumber` | `Number` |
| `_csl_string` | `CSLStringLiteral` | `String` |
| `_csl_bool` | `CSLBool` | `Bool` |
| `_csl_none` | `CSLNone` | `None` |
| `_csl_result` | `CSLResult` | `Result` |
| `_csl_old` | `CSLOld` | `Old` / `OldField` |
| `_csl_nothing` | `Nothing` | `Nothing` |
| `_csl_forall` | `Forall` | `Forall` |
| `_csl_exists` | `Exists` | `Exists` |
| `_csl_array_length` | `ArrayLength` | `ArrayLen` |
| `_csl_subscript` | `SubscriptAccess` | `Subscript` |
| `_csl_chained_subscript` | `ChainedSubscript` | Nested `Subscript` |
| `_csl_assigns_region` | `AssignsRegion` | `AssignsRegion` |
| `_csl_valid` | `Valid` | `Valid` |
| `_csl_separated` | `Separated` | `Separated` |
| `_csl_at` | `CSLAt` | `At` |
| `_csl_length2d` | `Length2D` | `Length2D` |
| `_csl_valid2d` | `Valid2D` | `Valid2D` |
| `_csl_contract_wrapper` | Requires/Ensures/LoopInvariant/LoopVariant | (wrapper) |
| `_csl_function_variant` | `FunctionVariant` | `FunctionVariant` |
| `_csl_call_expr` | `CallExpr` | `Call` |
| `_csl_is_sorted` | `IsSorted` | `IsSorted` |
| `_csl_sum` | `Sum` | `Sum` |
| `_csl_in` | `CSLIn` | `In` |
| `_csl_not_in` | `CSLNotIn` | `NotIn` |
| `_csl_slice` | `CSLSlice` | `Slice` |
| `_csl_map_empty` | `MapEmptyExpr` | `MapEmpty` |
| `_csl_map_get` | `MapGetExpr` | `MapGet` |
| `_csl_map_set` | `MapSetExpr` | `MapSet` |
| `_csl_map_remove` | `MapRemoveExpr` | `MapRemove` |
| `_csl_has_key` | `HasKeyExpr` | `HasKey` |
| `_csl_map_eq` | `MapEqExpr` | `MapEq` |

### Module5 Python Statement Handlers

| Handler | Python AST | IR Statement |
|---------|-----------|-------------|
| `_py_stmt_assign` | `ast.Assign` | `Assign` / `FieldAssign` / `ArraySet` / `TupleUnpack` |
| `_py_stmt_augassign` | `ast.AugAssign` | `AugAssign` / `FieldAugAssign` |
| `_py_stmt_return` | `ast.Return` | `Return` |
| `_py_stmt_while` | `ast.While` | `While` |
| `_py_stmt_for` | `ast.For` | `For` |
| `_py_stmt_if` | `ast.If` | `IfElse` |
| `_py_stmt_continue` | `ast.Continue` | `Continue` |
| `_py_stmt_assert` | `ast.Assert` | `Assert` |
| `_py_stmt_raise` | `ast.Raise` | `Raise` |
| `_py_stmt_try` | `ast.Try` | `TryExcept` |
| `_py_stmt_with` | `ast.With` | `With` |
| `_py_stmt_pass` | `ast.Pass` | (skipped) |
| `_py_stmt_break` | `ast.Break` | `Break` |
| `_py_stmt_delete` | `ast.Delete` | `Delete` |

### Module6 Statement Handlers

| Handler | Line Range | IR → WhyML |
|---------|-----------|------------|
| `_handle_assign_stmt` | 1372–1444 | `Assign` → `let x = ref v in` / `x := v` |
| `_handle_while_stmt` | 1446–1508 | `While` → `while ... do ... done` |
| `_handle_for_stmt` | 1543–1630 | `For` → desugared `while` |
| `_handle_try_stmt` | 1632–1690 | `TryExcept` → `try ... with ... end` |
| `_handle_ghost_assign_stmt` | 1692–1720 | `GhostAssign` → `let ghost` / `ghost x :=` |
| `_handle_tuple_unpack_stmt` | 1722–1760 | `TupleUnpack` → `let (a, b) = ...` |
| `_handle_array_set_stmt` | 1762–1811 | `ArraySet` → `arr[i] <- v` / `Map.set` |
| `_handle_if_stmt` | 1813–1854 | `IfElse` → `if ... then ... else ...` |
| `_handle_match_stmt` | 1856–1892 | `Match` → chained `if/else` |
| `_handle_critical_section_stmt` | 1894–1937 | `Critical` → havoc+assume/assert |
| `_handle_augassign_stmt` | 1939–1963 | `AugAssign` → `x := !x op v` |
| `_handle_fieldassign_stmt` | 1965–1996 | `FieldAssign` → `self.f <- v` |
| `_handle_fieldaugassign_stmt` | 1998–2031 | `FieldAugAssign` → `self.f <- self.f op v` |
| `_handle_return_stmt` | 2033–2064 | `Return` → `v` / `raise (Return v)` |
| `_handle_expr_stmt` | 2066–2093 | `Expr` → expression as statement |
| `_stmts_to_whyml` | 2098–2184 | Dispatcher for all statement types |

### Module6 Expression Handlers

| Handler | Line Range | IR → WhyML |
|---------|-----------|------------|
| `_handle_binop` | 686–771 | `BinOp` → `(a op b)` |
| `_handle_len_call` | 773–804 | `len()` → `(length arr)` |
| `_handle_join_call` | 806–829 | `str.join()` → abstract |
| `_handle_sum_call` | 831–848 | `sum()` → `pycsl_sum` |
| `_handle_dotted_call` | 850–861 | `obj.method()` → abstract |
| `_handle_call_expr` | 863–941 | `Call` → `(f a b ...)` |
| `_handle_subscript` | 943–996 | `Subscript` → `arr[i]` / `Map.get` |
| `_handle_attribute_expr` | 997–1010 | `Attr` → `obj.field` |
| `_handle_var_expr` | 1012–1031 | `Var` → `!x` / `x` |
| `_handle_field_get_expr` | 1033–1052 | `FieldGet` → `self.f` |
| `_handle_fstring_expr` | 1053–1069 | F-string → hash |
| `_handle_unaryop_expr` | 1071–1084 | `UnaryOp` → `(- x)` / `(not x)` |
| `_handle_old_expr` | 1086–1099 | `Old` → `(old e)` |
| `_handle_at_expr` | 1101–1118 | `At` → `(e at L)` |
| `_handle_ifexpr_expr` | 1120–1133 | `IfExpr` → `(if c then a else b)` |
| `_handle_named_expr_expr` | 1135–1147 | Named expr → `(begin x := v; !x end)` |
| `_handle_slice_access_expr` | 1149–1161 | `Slice` → `(array_slice ...)` |
| `_handle_arraylen_expr` | 1163–1174 | `ArrayLen` → `(length arr)` |
| `_handle_valid_expr` | 1176–1187 | `Valid` → bounds check / `valid` predicate |
| `_handle_separated_expr` | 1189–1202 | `Separated` → `true` / `separated` predicate |
| `_handle_length2d_expr` | 1204–1216 | `Length2D` → dimension check |
| `_handle_valid2d_expr` | 1218–1230 | `Valid2D` → index validity |
| `_handle_issorted_expr` | 1232–1244 | `IsSorted` → `forall` quantification |
| `_handle_sum_node_expr` | 1246–1258 | `Sum` → `(pycsl_sum arr lo hi)` |
| `_handle_lambda_expr` | 1260–1270 | `Lambda` → `(fun x -> e)` |
| `_handle_setlit_expr` | 1272–1284 | `SetLit` → `(set_empty ())` |
| `_handle_map_empty_expr` | — | `MapEmpty` → `(const (None: option int))` |
| `_handle_map_get_expr` | — | `MapGet` → `match Map.get !d k with \| Some v_ -> v_ \| None -> 0 end` |
| `_handle_map_set_expr` | — | `MapSet` → `(Map.set !d k (Some v))` |
| `_handle_map_remove_expr` | — | `MapRemove` → `(Map.set !d k None)` |
| `_handle_has_key_expr` | — | `HasKey` → `(Map.get !d k <> None)` |
| `_handle_map_eq_expr` | — | `MapEq` → `(forall k: int. Map.get !d1 k = Map.get !d2 k)` |
| `_expr_to_whyml` | 1289–1341 | Main dispatcher for all expression types |

### Module6 Emission Functions

| Function | Line Range | Purpose |
|----------|-----------|---------|
| `_emit_preamble_uses` | 2418–2459 | Theory `use` imports |
| `_emit_preamble_exceptions` | 2461–2484 | Exception declarations |
| `_emit_preamble_helpers` | 2486–2524 | `pycsl_div` / `pycsl_mod` |
| `_emit_preamble` | 2526–2532 | Orchestrates prelude emission |
| `_emit_shared_state` | 2538–2583 | Concurrent model shared vars |
| `_emit_type_decls` | 2589–2657 | Record types for classes |
| `_emit_contracts` | 2760–2795 | requires/ensures/variant/diverges |
| `_emit_body_code` | 2797–2851 | Function body WhyML |
| `_emit_function` | 2853–2911 | Complete function emission |
| `_emit_frame_condition` | 2186–2220 | Assigns → writes + frame |

---

## §T.13  References

1. Filliâtre, J.-C. & Paskevich, A. (2013). *Why3 — Where Programs
   Meet Provers*. ESOP 2013. LNCS 7792.

2. Clochard, M. et al. (2018). *Instrumenting a weakest-precondition
   calculus for counterexample generation*. Journal of Logical and
   Algebraic Methods in Programming.

3. Baudin, P. et al. (2021). *ACSL: ANSI/ISO C Specification Language*.
   (Inspiration for PyCSL's annotation syntax.)

4. Leino, K.R.M. (2010). *Dafny: An Automatic Program Verifier for
   Functional Correctness*. LPAR 2010.

5. Why3 Reference Manual. https://why3.lri.fr/doc/

---

## Appendix A: Golden Output Gallery

The following are complete verified WhyML outputs generated by
`pycsl --keep-mlw` on reference tests.

### A.1  Basic Function (Test 0001)

**Input:**
```python
#@ requires x >= 0
#@ ensures \result >= 0
def test_precondition(x: int) -> int:
    return x + 1
```

**Output:**
```whyml
module PyCSL_Program
  use int.Int
  use int.EuclideanDivision
  use ref.Ref

  let test_precondition (x: int) : int
    requires { (x >= 0) }
    ensures  { (result >= 0) }
  =
    (x + 1)

end
```

### A.2  While Loop with Invariant (Test 0004)

**Input:**
```python
#@ requires n >= 0
#@ ensures \result == n * (n - 1) // 2
def test_loop_invariant(n: int) -> int:
    s = 0
    i = 0
    #@ loop invariant s == i * (i - 1) // 2
    #@ loop invariant 0 <= i and i <= n
    #@ loop variant n - i
    while i < n:
        s += i
        i += 1
    return s
```

**Output:**
```whyml
module PyCSL_Program
  use int.Int
  use int.EuclideanDivision
  use ref.Ref

  let pycsl_div (x: int) (y: int) : int
    requires { [@expl:division by zero] y <> 0 }
    ensures { result = div x y }
  = div x y

  let pycsl_mod (x: int) (y: int) : int
    requires { [@expl:modulo by zero] y <> 0 }
    ensures { result = mod x y }
  = mod x y

  let test_loop_invariant (n: int) : int
    requires { (n >= 0) }
    ensures  { (result = (div (n * (n - 1)) 2)) }
  =
    let s = ref 0 in
    let i = ref 0 in
    s := 0;
    i := 0;
    while (!i < n) do
      invariant { (!s = (div (!i * (!i - 1)) 2)) }
      invariant { ((0 <= !i) && (!i <= n)) }
      variant { (n - !i) }
      s := (!s + !i);
      i := (!i + 1)
    done;
    !s

end
```

### A.3  Class with Invariant (Test 0006)

**Input:**
```python
#@ class invariant self._value >= 0
class Counter:
    def __init__(self):
        self._value = 0

    #@ requires amount >= 0
    #@ ensures self._value == \old(self._value) + amount
    def increment(self, amount: int) -> int:
        self._value += amount
        return self._value
```

**Output:**
```whyml
module PyCSL_Program
  use int.Int
  use int.EuclideanDivision
  use ref.Ref

  type counter = { mutable _value: int }
    invariant { (_value >= 0) }
    by { _value = 0 }

  let counter__increment (self: counter) (amount: int) : int
    requires { (amount >= 0) }
    ensures  { (self._value = ((old self._value) + amount)) }
  =
    self._value <- (self._value + amount);
    self._value

end
```

### A.4  Concurrent Model (Test 0250)

**Input:**
```python
#@ shared counter
#@ mutex_invariant lock_counter: counter >= 0
#@ \diverges
#@ thread_entry
def worker() -> int:
    #@ critical lock_counter
    counter += 1
    return 0
```

**Output:**
```whyml
module PyCSL_Program
  use int.Int
  use int.EuclideanDivision
  use ref.Ref

  val counter : ref int
  predicate lock_counter_inv = (!counter >= 0)
  let _check_initial_lock_counter () : unit =
    assert { lock_counter_inv }

  let worker () : int
    diverges
  =
    let _any_counter_0 = any int in
    counter := _any_counter_0;
    assume { lock_counter_inv };
    counter := !counter + 1;
    assert { lock_counter_inv };
    0

end
```

### A.5  Exception with Raises (Test 0206)

**Input:**
```python
#@ ensures \result >= 0
#@ raises ValueError when n < 0
def checked_abs(n: int) -> int:
    if n < 0:
        raise ValueError
    return n
```

**Output:**
```whyml
module PyCSL_Program
  use int.Int
  use int.EuclideanDivision
  use ref.Ref
  exception ValueError

  let checked_abs (n: int) : int
    ensures  { (result >= 0) }
    raises { ValueError -> (n < 0) }
  =
    if (n < 0) then begin
      raise ValueError
    end;
    n

end
```
