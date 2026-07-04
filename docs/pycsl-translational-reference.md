# PyCSL Translational Semantics Reference

**Version:** 1.5  
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
| `float` | `real` | Why3 `real.RealInfix` (`+.`/`-.`/…); float literals are real constants. Was the unsound `int` (no-more-int Stage D) |
| `list` | `array int` | Hoare/Concurrent model (default — fixed-length, mutable, region-bearing) |
| `list` (grown) | `ref (seq int)` | **07-1705-rev4: a list that is *grown* (`+=` / `+` concat) is modelled as a growable immutable `seq.Seq` value in a region-free ref** — `array.Array` is fixed-length and cannot be rebound (Why3 region rule, `07-1732-findings.md`). Init `[…]`→`Seq.cons` chain; `+=`→`a := !a ++ snapshot(b)` (length-additive + element-preserving, **provable**); `len`→`Seq.length`, `a[i]`→`Seq.get`. A grown PARAM is shadowed at entry `let a = ref (snapshot a)`; `return a` materialises back to `array int` (`materialize`, a fresh array). The seq-promotion analysis (Module5 `seq_promoted_vars`) selects these; `Seq.*` is emitted only in body context (a contract uses the array entry value). Supersedes the old effect-opaque `array_extend` |
| `list` | `loc` + `_len` | Typed/Store model |
| `dict` / `set` / `frozenset` | `map κ (option ν)` | Parametric map (no-more-int A1): κ ∈ {`int`, `string`}, and the value type **ν ∈ {`int`, `string`, `seq int`, nested `map …`}**, where — `int` (the default), `string` (str-valued dict), `seq int` (list-valued dict, **immutable seq snapshot** — no mutate-through-alias; A1-residual, driver 0543), and a nested `map …` (dict-of-dict, double subscript). Default `map int (option int)`. `set`/`frozenset` use the same model (value ignored). **κ = string ⇒ `map string (option ν)` with the NATIVE, injective Why3 string key** (`String.(=)`, no `str_hash_op`), so distinct keys are provably non-aliasing (cleared-hash.md, drivers 0755–0758). κ = string is inferred for a `Dict[str, _]` param/AnnAssign local, a string-key literal (`{"a": …}`), and string-key USAGE (`d[k]`/`k in d`/`d.get(k)` with a string literal or `str`-typed key) — Module5 `_build_function_symbol_table`. **Residual κ-unknown:** a record *field* dict/set and any dict with a non-inferable key type keep the legacy `map int` + opaque `str_hash_op` fallback (documented, never claimed collision-sound). Implementation: the ν ladder is consolidated into three helpers `_dv_empty_default`/`_dv_missing_default`/`_dv_store_value` in `module6_whyml/expressions.py` (refactor F1) |
| `tuple` | `int` (hash) | **Intentional benign collapse (A7).** A bare tuple value hashes to an `int`; element types are NOT modeled. Rare and benign — a future tuple track would lift this, but no driver demands it. (Ghost tuples `\mk_tuple`/`\fst`/`\snd` in *contracts* are modeled faithfully — §T.6.) |
| `None` / `-> None` | `unit` | Return type for void functions |
| Class `C` | Record type `c` | Lowercase name. Covers `self`, `C()` locals, **and** a registered `C`-typed parameter (read-only field access; Track 3 — mutation of a record param out of scope) |
| `#@ datatype D` | Variant type `d` | Sum type `type d = A \| B int \| …` (§T.4.5); constructed with `B(7)`, consumed by `match` (§T.5.12) |
| No annotation | `int` | Default |

> **Intentional benign collapses (A7).** Two entries above are deliberate, documented
> approximations rather than debt: `bool` → `int` (`1`/`0` in body, `true`/`false` in spec) and a
> bare `tuple` → `int` (hash). Both are rare in practice and sound for the contexts they appear in;
> no demand-driver should chase lifting them. Everything else in the table is a faithful model of
> the Python type.

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

### §T.2.5b  Bounded expansion (`#@ for`)

`#@ for <var> in range(lo, hi):` is desugared (Module 3) to ordinary `requires`/`ensures` — there is
**no** new WhyML construct and **no** new translation rule. For each integer `m` in `[lo, hi)`
(upper-exclusive) and each body clause `C`, the desugarer emits `C[<var> := m]` with `<var>` replaced by
the integer literal `m` (matching a source integer literal, so the emitted index is `m`, not `m.0`):

$$\mathcal{T}\llbracket \texttt{\#@ for i in range(0,n): requires P(i)} \rrbracket
= \texttt{requires \{ P(0) \}} \;\dots\; \texttt{requires \{ P(n-1) \}}$$

The output is **ground** (no quantifier) and **byte-identical** to the corresponding hand-written
clauses — `#@ for` lowers through the existing requires/ensures translation, contributing nothing of its
own. (Contrast `\forall`, §T.6/§3.3, which lowers to a real Why3 quantifier.) `lo`/`hi` are
compile-time integer constants (v1: literals). See `test-suite/annotations.md` §2.9.

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

### §T.2.5c  Contract opacity — the narrowing VC (`#@ interface` / `#@ reveal`)

A function with a `#@ interface` contract emits, **in its owning unit**, a *narrowing VC* proving the
interface is a sound weakening of the definition (`b-spec.md`, Track B). Module 6 emits Why3 `goal`s:

$$\texttt{goal narrows\_ens} : \forall \text{params}, result.\; \mathit{def\_requires} \rightarrow
\mathit{def\_ensures} \rightarrow \mathit{iface\_ensures} \quad(\text{the definition's ensures implies the interface's})$$

$$\texttt{goal narrows\_req} : \forall \text{params}.\; \mathit{iface\_requires} \rightarrow
\mathit{def\_requires} \quad(\text{the interface precondition implies the definition's})$$

An interface that claims **more** than the definition proves makes a goal unprovable → the function is
rejected. Lowering of the contracts themselves is unchanged: the **definition** lowers to the function's
verified `let` (as today); the **interface** is what an importer's `val` stub exports, so callers see the
narrow contract by default. `#@ reveal <fn>` opts a call site into `<fn>`'s definition facts (within the
owning unit a no-op — the definition is already the visible `let`; across modules it cites the exported
definition-fact). With no `#@ interface`, no narrowing VC is emitted and interface = definition
(transparent — existing emission byte-identical). See `annotations.md` §2.10, static-semantics §2.y.

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

**`footprint` / parametric & protects HAPPY (07-1143).** These desugar entirely to the same
per-site `#@ check` primitive (§ check), so they add **no** new WhyML/IR construct. A `protects
<paths>` HAPPY emits `#@ check False` at each non-exempt direct write of a protected (possibly
dotted) path. A parametric `#@ happy <name>(p): protects <path>[LO:HI]` with a method's `#@
footprint <name>(arg)` emits `#@ check (LO[p:=arg] <= i && i < HI[p:=arg])` at each write
`<path>[i]` — the bounds are the region with `p` substituted by `arg`. Each carries an `origin`
comment naming the HAPPY and site.

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

- `Module5_IREmitter.py:1364` includes `"reviewer": <value>` in the
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
the 0-`\trusted` policy (`attic/stdlib-coverage-tooling/check-no-trusted-stubs.py`).

This is the canonical translation for irreducibly-opaque library stubs —
e.g. `ast.literal_eval`, whose parsed value is uninterpreted but whose
bounded raises set (`ValueError`/`SyntaxError`) makes a `try/except`
wrapper provably total (corpus `0449`).

_Corresponds to `annotations.md` §2.1.14._

### §T.2.12  Lemma Functions (`lemma`)

$$\mathcal{T}_f\llbracket \texttt{def f(p): \#@ lemma … -> None} \rrbracket
= \texttt{let [rec] lemma f (p) : unit requires \{H\} ensures \{C\} [variant \{m\}] = }\,\mathcal{T}_s\llbracket\text{body}\rrbracket$$

The `lemma` keyword instructs Why3 to (a) verify the body against the contract and
(b) expose the contract as a logical fact `forall p. H -> C` to subsequent goals.
`functions.py::_emit_function` selects the `let lemma` / `let rec lemma` keyword when
`func["lemma"]` (recursion or a multi-member SCC → `let rec lemma`), and forces the
result type to `unit` (a `-> None` proof function). The proof body lowers like any
function body ($\mathcal{T}_s$): a recursive self-call lowers to a recursive call, so
Why3 derives the induction hypothesis from the lemma's own verified, terminating
contract; `match` over a `#@ datatype` is the proof's case split; `pass` is `()`.

Unlike `#@ proof` (§T.2.10, an `axiom` in the preamble) and `\trusted`/`\abstract`
(§T.2.6/§T.2.7, a `val`), a lemma is **checked** — it adds no axiom that isn't itself
verified. Module 4 rejects a recursive lemma without `#@ \variant` and a
`lemma`+`\diverges` combination (static-semantics §2.1.16) before emission.

_Corresponds to `annotations.md` §2.1.16._

### §T.2.13  Uses citations (`uses`)

$$\mathcal{T}_f\llbracket \texttt{def f(): \#@ uses L …} \rrbracket = \varepsilon\quad(\text{no emission})$$

`#@ uses L` produces **no WhyML**. Its sole effect is on *declaration order*: `scc.py` adds a
call-graph edge `f → L`, so the cited lemma `L` is emitted before `f` and its exported fact
`forall params. H -> C` is in scope when `f`'s goal is discharged. This closes scc2.md's case (B) — a
goal (e.g. `\forall x: Nat; to_int(x) >= 0`) that relies on a lemma's general fact without *naming* the
lemma, so no contract-reference edge (§T contract lowering) would otherwise order it. **Implementation:**
`Module2` (`Uses` + `uses_decl`), `Module3_Weaver` (`csl_uses`), `Module5_IREmitter` (`uses` on the
function IR), `scc.py::sort_functions_by_scc` (the ordering edge). Contrast a body call to the lemma,
which also forces the order but instantiates a throwaway argument. _Corresponds to `annotations.md`
§2.1.17._

### §T.2.7  Diverging Functions (`\diverges`)

The `diverges` keyword omits the termination obligation.  No `variant`
clause is emitted, and WhyML does not require a termination proof:

```whyml
  let f (...) : R
    diverges
  = ...
```

### §T.2.7n  No-inline Methods (`no_inline`)

A method marked `#@ no_inline` (no-inline.md) is a **modular-verification
boundary**. Its body is emitted as a normal verified `let` (proven once against
its contract). At each call site on a module-global instance, the IR-inliner
**leaves the call in place** instead of splicing the body; Module6 lowers it as a
**contract-call** — an abstract `val` carrying the callee's result-only `ensures`
(resolved by `_resolve_dotted_signature`'s module-global branch), so the caller
discharges its postcondition from the contract rather than re-proving the body:

```whyml
  let lib__seven (self: lib) : int = (* body verified once *) 7

  val _lib_seven_0 () : int            (* contract-call at the use site *)
    ensures { result = 7 }
  let caller () : int = (_lib_seven_0 ())   (* proves from the ensures, body not re-proven *)
```

This avoids re-proving a large body in every caller's context (the os `sys_write`
inlining blow-up — 6 SMT timeouts). **Soundness:** the body stays a verified
`let`, so a false `ensures` makes the *callee* fail; nothing is moved into the TCB.

### §T.2.7s  Sibling-concrete Methods (`sibling_concrete`)

A method marked `#@ sibling_concrete` (allocator-frame §2.7) **opts in** to a
CONCRETE intra-class sibling-call lowering. By default a `self.<m>(...)` call is
lowered to an abstract `val` stub carrying only the callee's propagated `ensures`;
for a marked callee, Module6's `_handle_dotted_call` instead emits a direct call to
the verified `let`, `(<class>__<m> self args)`, so the caller obtains the callee's
**full contract AND its type/class-invariant guarantee** on the post-state (the
abstract stub conveys neither). `scc.find_self_method_calls` adds the
callee-before-caller ordering edge for marked callees only.

```whyml
  let c__bump (self: c) : unit          (* verified let; maintains `invariant x >= 0` *)
    ensures { self.x = old self.x + 1 } = ...

  let c__bump_loop (self: c) (n: int) : unit =
    while ... do (c__bump self) done    (* CONCRETE call: caller inherits `x >= 0` as an atom *)
```

This is the key to the os allocators: `_alloc_block`'s loop concrete-calls the
marked `_set_bitmap` and inherits the disk class invariant (`uniq` /
`inode_bytes_valid`) as a single atom (with the loop invariant carrying it), instead
of re-deriving the double-`forall`. Decoupled from `no_inline` (does not change
wrapper inlining). **Soundness:** a concrete call to a verified `let` is the method's
real semantics — it adds nothing to the TCB. Default off → byte-identical.

### §T.2.7f  Frame-propagating Methods (`propagate_frame`)

A method marked `#@ propagate_frame` (os-roadmap M4) **opts in** to carrying its
QUANTIFIED single-cell self-field FRAME `ensures` onto its abstract boundary `val`.
By default, `#@ assigns self.f` lowers to `writes { self.f }` on the boundary stub,
which frames `self.f` as a WHOLE — a caller sees the entire field havoced (only a
result-pinned cell survives). For a marked callee, Module6 additionally emits the
method's frame clauses of the shape `\forall k. guard -> self.f[k] == \old(self.f[k])`
as `ensures` on the boundary `val`, so a caller can prove every *other* cell preserved.

Two frame shapes are propagated (built by `_build_method_field_param_frame_ensures_map`
and `_build_method_result_frame_ensures_map` respectively, threaded through
`_resolve_dotted_signature` → `_dotted_ensures_suffix`):

- **param-referencing** frames (the os `_zero_entry` slot frame
  `\forall k. ... slot_inode(self.disk, x0, k) == \old(...)`), trigger pinned on the
  post-state decode application;
- **`\result`-referencing** single-cell frames
  (`\forall k != \result. self.f[k] == \old(self.f[k])`), where `\result` lowers to the
  `val`'s `result` keyword — its return value, i.e. the call's result — so binding is
  automatic with no explicit substitution.

```whyml
  val _filesystem_sys_dup_1 (self: unixinodefilesystem) (x0: int) : int
    writes { self.fd_open, self.fd_inode, self.fd_offset, self.fd_flags, self.next_fd }
    ensures { result = -1 \/ result >= 3 }
    (* propagated frame: every OTHER fd_open cell is preserved by the call *)
    ensures { forall k. 0 <= k < 64 /\ k <> result -> self.fd_open[k] = old self.fd_open[k] }
```

This is the key to retiring the os `fd-resolution-fidelity` trusts: with the frame
propagating, a caller (the os `__init__` wrapper / a composed test) proves the table is
not full after a prior `open` (the constructor starts `fd_open` all-free, and each
syscall preserves all but one cell), so the honest free-slot side-condition `_alloc_fd`
discharges survives the import boundary. **Opt-in ON PURPOSE:** a broad frame trigger
can E-match-poison term-rich sibling callers, so the marker asserts "this method's callers
need *and* can absorb the frame". **Soundness:** the propagated `\forall` is the SAME
frame the callee's body verifies (a true frame of the body), never a fabricated or
broadened one — it adds nothing to the TCB. Default off → byte-identical.

### §T.2.7g  Fresh-globals Drivers (`fresh_globals`)

A top-level driver marked `#@ fresh_globals` (fresh-globals.md) **opts in** to
re-establishing each module-global singleton's CONSTRUCTOR post-state as an ASSUMED
fact at its body entry. Why3 verifies every importer function with each shared mutable
module-global in an ARBITRARY state (other functions could have mutated it), so an
internals-blind driver cannot otherwise establish the freshly-imported initial state
(e.g. the os `_filesystem` fd table being all-free at entry). For a marked driver,
Module6 (`functions._emit_function`) emits, as the FIRST body statement, an `assume`
of each global's constructor `#@ ensures` with `self` rewritten to the global name
(`preamble._fresh_globals_facts` / `_subst_self_in_expr`):

```whyml
  let dup_of_valid_source_is_valid (p: string) : int
    requires { true }
    ensures  { result = 1 }
  =
    assume { forall k. 0 <= k < 64 -> _filesystem.fd_open[k] = 0 };   (* fresh_globals *)
    try ... with Return r -> r end
```

The assumed fact is **proof-backed**, not an arbitrary literal: for each global whose
class declares a constructor `#@ ensures`, `preamble._emit_module_globals` ALSO emits a
checked function that re-constructs the same constructor literal and carries the ensures
as its postcondition, so Why3 PROVES the post-state holds of the freshly constructed
global (the `Array.make 64 0` witness):

```whyml
  let _filesystem_fresh_init () : unixinodefilesystem
    ensures { forall k. 0 <= k < 64 -> result.fd_open[k] = 0 }
  = { disk = Array.make 131072 0; ...; fd_open = Array.make 64 0; ... }
```

The same `_fresh_globals_facts` lowering feeds both the checked goal (`self` → `result`)
and the driver `assume` (`self` → the global), so the assumed fact is exactly the proven
one. **Soundness / confinement:** Module4 (`core_ir_semantic._check_fresh_globals`)
REJECTS the directive on a method or on any callee (§2.1.6g) — it is sound only for an
independent entry point that runs on a freshly-imported global. This RETIRES the os
`fd-resolution-fidelity` no-ENFILE reviewer trust: with the free-slot side-condition
established at the driver entry (and carried across a prior `open`/`dup` by the
`propagate_frame` single-cell frame, §T.2.7f), the honest free-slot-CONDITIONED dup body
theorem (zero-trust, via `_alloc_fd`'s completeness) proves the formal test — replacing
the FALSE unconditioned `\result>=3` body theorem the trust used to assume.

### §T.2.7m  Module-emission (`verify_module <name>`)

A function tagged `#@ verify_module <name>` is emitted into its OWN top-level Why3
`module <name>` instead of the single flat `module PyCSL_Program`. The transpiler
partitions the program's functions by their `verify_module` group (untagged → the flat
default module). For each emitted module it re-declares the shared infrastructure — `use`s,
helpers, the `val function`/`predicate` symbols, witness/class-invariant axioms, and the
abstract stubs — and emits ONLY that group's `#@ proof`-cited axioms (axiom selection is
per-module because the axiom emitter scans only the functions in the module). The concrete
record type is declared once in a common base `module` that every emitted module `use`s,
because Why3 cannot `clone`-substitute a defined (concrete, field-bearing) type.

A cross-module `self.<m>(...)` call — to a sibling in a different `verify_module` group, or
in the flat default module — is lowered to the callee's PROVEN contract via Why3 module
**`clone`-refinement**: an interface `module <name>Sig` declares the callee's contract as a
bodyless `val` (the contract only, no body, no axioms); the owning provider `module <name>`
re-declares the shared symbols, holds its group's axioms LOCALLY, emits the real
`let <fn> = <body>` discharging the contract, and ends with `clone <name>Sig with
val <fn> = <fn>, …` — for which Why3 generates the synthetic refinement VC `<fn>'refn'vc`
proving the implementation satisfies the interface contract (validated non-vacuous: a
contract that over-claims relative to the body makes `'refn'vc` unprovable). The consumer
`module` `use`s the interface `module` and calls `<name>Sig.<fn>` (the proven contract),
NOT an abstract `val self__<fn>_<n>` stub. The boundary is therefore a PROVEN interface —
never an assumed `val`, a new `\trusted`, or a new axiom. The net TCB is unchanged: every
function is proved exactly once, against a contract that is itself proved; the directive
only changes WHICH declarations share the SMT context at each VC, isolating one group's
axioms from another's goals (e.g. the os read-side `field_to_str`/`dir_scan_*` axioms out
of scope for the directory writers' per-byte goals, and the write-side `dir_blit_marker*`
axioms out of scope for `_dir_lookup`'s read goals — resolving the co-residence OOM).

Why3 `scope` does NOT provide this isolation — a `scope` is a namespace, and an `axiom` is
global within its enclosing `module` regardless of scope nesting; only separate top-level
`module`s isolate axioms. Default (untagged) → the single flat `module PyCSL_Program` is
emitted unchanged → corpus byte-identical (see static §2.1.6m, concrete §2.1.6m).

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

**Axioms over user datatypes (emission order).** An imported axiom may quantify over a
`#@ datatype` (§T.4.5) — e.g. `forall x : json. mirror (mirror x) = x` proved by structural
induction in Rocq+Lean (driver 0542). For the axiom to typecheck, its formula must be emitted
**after** the type declarations. PyCSL therefore emits preamble axioms (`_emit_preamble_axioms`)
*after* `_emit_type_decls`, not inside the base `_emit_preamble`. This is what lets the
`\permutation` framing demo (§T.6.5, 0537–0539) and the inductive `mirror`-involution bridge
(`docs/framing-lemma-demonstration.md`) generalize the flat→inductive axiom pattern. (For the
mechanism to fire, the `#@ proof` directives must be **contiguous** with the function's other `#@`
annotations.)

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

### §T.4.5  Datatype / sum-type emission (`#@ datatype`)

A module-level `#@ datatype D = A | B(int) | …` declares a Why3 **variant type** — the same
`_emit_type_decls` machinery that emits class records (§T.4.1), via its `kind:"variant"` branch:

$$\mathcal{T}\llbracket \texttt{\#@ datatype Box = Some(int) | Pair(int,int) | Empty} \rrbracket
= \texttt{type box = Some int | Pair int int | Empty}$$

Payload types map through the same τ (§T.2.2): `int`/`bool` → `int`, `str` → `string`, `float`
→ `real`. The constructors are registered (`Module5` constructors registry), so:

| PyCSL | WhyML | Notes |
|-------|-------|-------|
| `o = Some(7)` (applied ctor) | `let o = ref (Some 7) in` | a typed variant local (not a coarsened `int ref 0`) — `types.py::_collect_variant_var_assigns` excludes it from the int pre-decl path |
| `o = Red` (nullary ctor) | `Red` | bare constructor name |
| `match o: case …` | Why3 `match … with … end` | constructor-pattern lowering, §T.5.12(b) |

**Implementation:** `Module1_Ingestor` (the `datatype ` prefix), `Module2_Parser`
(`DatatypeDecl` + variant grammar), `Module3_Weaver` (collection into the module AST),
`Module5_IREmitter` (variant `type_decl` + constructors registry), `preamble.py::_emit_type_decls`
(variant branch), `expressions.py` (constructor lowering). **Out of scope:** recursive /
parametric datatypes, guarded/nested/or-patterns. _Corresponds to `annotations.md` §2.6._

### §T.4.6  Mixin composition (`#@ mixin` / `#@ compose_from`)

Tier-1 mixin composition lowers in two steps — **verify-once** (each mixin in isolation) then
**flatten-on-compose** — reusing the class-record (§T.4.1) and method (§T.4.3) machinery; no new proof
theory.

**(a) Verify-once.** A `#@ mixin`'s declared `depends_method`/`requires_method` interface lowers to an
abstract `val` (the abstract-op / val-bridge pattern, **`\abstract`, never `\trusted`**), and each
provided method is verified once against it:

$$\mathcal{T}\llbracket \texttt{\#@ depends\_method emit: (self, x:int)->int; ensures \textbackslash result>=0} \rrbracket
= \texttt{val self\_emit\_n (x0: int) : int  ensures \{ result >= 0 \}}$$

So `MapOps.handle_get` calling `self.emit(k)` discharges against `self_emit_n`'s contract
(`module6_whyml/functions.py::_mixin_dep_pseudo_functions`). The mixin proves in isolation (corpus
`0553`).

**(b) Flatten-on-compose.** `pycsl.py::_apply_composition` (an IR→IR pass after inheritance) **checks**
the composition (unique provider per dependency; no two-provider collision; every `self.<field>` write
declared `shared_state`/`touches_field`/`__init__`) then **clones** each provided method
`<mixin>__m → <composer>__m` (retyping `self` to the composer):

$$\texttt{\#@ compose\_from CoreEmit, MapOps; class Facade} \;\Rightarrow\;
\texttt{facade\_\_emit, facade\_\_handle\_get}\ \text{(cloned)} \;+\; \texttt{facade\_\_run}$$

so `self.handle_get(k)` in `Facade.run` resolves end-to-end and `\result >= 0` proves (corpus `0549`).
When a real provider is flattened in, the abstract pseudo-`val` is skipped so it doesn't shadow the
concrete contract (`functions.py`).

**Additivity.** The directives are purely additive: a file with no `#@ compose_from` produces an empty
`compositions` list and `_apply_composition` is a no-op, so **non-mixin corpus emission is
byte-identical** (verified across all 480 emitting non-mixin files, all four memory models — the
emission-identical gate).

**Out of scope (getattr dispatch).** The real facade's *dynamic* `getattr(self, _EXPR_DISPATCH[t])`
routing is **not** modelled here — Tier 1 lowers the mixin algebra over statically-named providers; the
dispatch table is a separate coverage obligation (static-semantics §2.6). **Implementation:** `Module2`
(the 7 directive decls), `Module3_Weaver` (`csl_is_mixin`/`csl_compose_from`/…), `Module5_IREmitter`
(`compositions` + per-method `provides`/`shared_state`/`touches_field`), `pycsl.py::_apply_composition`,
`functions.py`. _Corresponds to `annotations.md` §2.7._

### §T.4.7  Inductive predicates (`#@ inductive`)

$$\mathcal{T}\llbracket \texttt{\#@ inductive p(x: T): R\_i: } c_i \rrbracket
= \texttt{inductive p }\tau(T)\texttt{ = }\;|\;\texttt{R\_i : }\mathcal{T}_e\llbracket c_i\rrbracket\;\dots$$

`preamble.py::_emit_inductive_decls` emits the predicate **after** the type declarations (its rules
may reference datatype constructors) and **before** axioms/functions (which may mention it in a
contract). The arg list is the predicate's *types only* (Why3 `inductive p t1 t2`), mapped through τ
(`int`/`bool`/`str`→`string`/`float`→`real`, a datatype/class lowercased). Each rule's clause
$c_i$ is an ordinary contract expression lowered by $\mathcal{T}_e$ in spec context, so
`\forall m: int; even(m) ==> even(m+2)` → `forall m : int. (even m) -> (even (m + 2))`; a predicate
application `p(args)` lowers to `(p args)` (registered in `_inductive_preds`). **A Why3 `inductive`
takes no closing `end`** — an `end` would close the enclosing module — and that holds for a mutual
group too: a `#@ with q(sig): …` continuation (P2) joins one Why3 group `inductive p … = | … with q …
= | …` (all members registered in `_inductive_preds`; Why3 checks positivity group-wide).

Unlike a `#@ datatype` (a `type`) or a `#@ lemma` (a checked `let lemma`), an inductive predicate is
an uninterpreted least-fixpoint relation; **Why3 checks strict positivity** when it processes the
declaration, so a non-positive rule is rejected at the Why3 layer. **Implementation:** `Module1`
(`_INDUCTIVE_HDR` indentation block-folder — header + `name: clause` lines fold into one contract),
`Module2` (`InductiveDecl` + `inductive_rule+` grammar — rules parsed inline; no `rule` keyword),
`Module3` (hoist to `csl_inductives`), `Module5` (`inductive_decls` IR),
`preamble.py::_emit_inductive_decls`, `expressions.py` (predicate-application lowering).
_Corresponds to `annotations.md` §2.8._

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

There are **two** lowerings, selected by the pattern kind:

**(a) Value patterns** (literals / wildcard) → chained if/else:

$$\mathcal{T}_s\llbracket \texttt{match x: case v1: S1 case v2: S2 ...} \rrbracket$$
$$= \texttt{if } \text{cond}(v_1) \texttt{ then begin } \mathcal{T}_s\llbracket S_1 \rrbracket
  \texttt{ end else if } \text{cond}(v_2) \texttt{ then begin } \mathcal{T}_s\llbracket S_2 \rrbracket
  \texttt{ end ...}$$

Guards are combined with `&&`; the wildcard `_` is the final `else`.

**(b) Constructor patterns over a `#@ datatype`** (§T.4.5) → a **real Why3 `match … with`**, so
exhaustiveness is solver-checked:

$$\mathcal{T}_s\llbracket \texttt{match v: case A(): S1 case B(n): S2 ...} \rrbracket
= \texttt{match } v \texttt{ with | A -> } \mathcal{T}_s\llbracket S_1 \rrbracket
  \texttt{ | B n -> } \mathcal{T}_s\llbracket S_2 \rrbracket \texttt{ ... end}$$

Each `case Ctor(c1, …)` binds the payload captures `c1 …` in its arm. A missing or extra
constructor is a Why3 error (no `_` is synthesized for an exhaustive constructor set).

**Implementation:** `_handle_match_stmt` (the variant branch dispatches on the subject's IR being
a known variant type; `_match_pattern_to_ir` produces the `Constructor` pattern IR).

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

#### `\in_globals(name)` — introspection, three-valued (07-1839)

A *true-only* lower bound over the statically-declared module bindings (functions, module
globals, constants, classes — the compile-time analogue of the runtime `globals()` dict; no
runtime dict is emitted):

$$\mathcal{T}_e\llbracket \texttt{\\in\_globals(name)} \rrbracket =
\begin{cases} \texttt{true} & name \in \text{module bindings (decided-true)} \\
\texttt{(in\_globals\_op } h(name)\texttt{)} & \text{otherwise (unknown — uninterpreted bool)} \end{cases}$$

The world is **open** (`import`/`exec` may inject names), so a name's absence yields an
uninterpreted `val in_globals_op (n:int):bool` — neither provably `true` nor `false`. The
decided-`false` direction is **never** emitted (it would be unsound). **Implementation:**
`_handle_in_globals_expr`; binding set from `_module_binding_names`.

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

#### `\permutation(a, b)`

$$\mathcal{T}_e\llbracket \texttt{\\permutation(a, b)} \rrbracket
= \texttt{(permut } \mathcal{T}_e\llbracket a \rrbracket\ \mathcal{T}_e\llbracket b \rrbracket \texttt{)}$$

`permut` is an **uninterpreted** binary predicate emitted into the preamble
(`predicate permut (a b : …)` with no body) — permutation is not first-order, so
$\mathcal{T}$ does **not** unfold it. Its meaning is supplied *externally* by a
proof-assistant-imported axiom: a `#@ proof` directive (§T.2.10) registers a
Rocq/Lean-proved fact (e.g. `permut_refl`, `rev_permutation`) into `_AXIOM_REGISTRY`,
emitted as `axiom pycsl_axiom_<target>` **after** the type declarations so it may
quantify over user datatypes. This is the framing-lemma / "axiom-from-bridge" pattern;
see `docs/framing-lemma-demonstration.md` and drivers 0537–0539.

**Implementation:** `_handle_permutation_expr`; preamble `_AXIOM_REGISTRY`/`_AXIOM_FUNCTIONS`.

#### `\is_ctor(x, Ctor)`

$$\mathcal{T}_e\llbracket \texttt{\\is\_ctor(x, Ctor)} \rrbracket
= \texttt{(match } \mathcal{T}_e\llbracket x \rrbracket \texttt{ with Ctor \_ … -> true | \_ -> false end)}$$

The datatype discriminator: true iff `x`'s head constructor is `Ctor`. The arity of
the wildcard payload is read from the datatype's constructor registry (`_constructors`).

**Implementation:** `_handle_ctor_test_expr`.

#### `\payload(x, Ctor[, i])`

$$\mathcal{T}_e\llbracket \texttt{\\payload(x, Ctor, i)} \rrbracket
= \texttt{(match } \mathcal{T}_e\llbracket x \rrbracket \texttt{ with Ctor … z\_i … -> z\_i | \_ -> }d\texttt{ end)}$$

The datatype projector: the `i`-th payload (default `i = 0`) of `x` viewed as `Ctor`.
`z_i` is a fresh binder in the `i`-th payload position; all other positions are
wildcards. The fall-through default `d` is the type-appropriate zero
(`0` for `int`, `""` for `string`, an empty map, etc.) for the payload's τ; it is
dead under an `\is_ctor(x, Ctor)` guard. Together `\is_ctor`/`\payload` let a contract
name a `match` capture **without** a surrounding `match` (annotations.md §2.6). Type-param
payloads (`Option[T]` at a use-site annotation) remain a follow-on (no-more-int Part 8, A8-1).

**Implementation:** `_handle_ctor_payload_expr` (uses the payload index and `_constructors`).
Drivers: 0541 (projectors), 0545 (multi-payload index), 0546 (or-pattern binding).

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

**Soundness classification (Phase 8).**
- **Static plane (Interpreted):** the applied lambda's value contract is proved
  by Why3 — a lambda bound and immediately/eventually called produces a VC over
  its body (witnessed by `pycsl-reference/0242`, `0243`, `0745`, all Valid; and
  a *false*-postcondition lambda program fails, so the VC is non-vacuous).
- **Runtime plane:** the lambda is an ordinary WhyML `fun` value; no `pycsl_lib`
  shim is required (it is `Interpreted`, not `Shimmed`).
- **Formal model (LINK 1):** the mechanized semantics models lambda by the
  *defunctionalized* `SLambda` (construction) + `SCall` (application) with a
  `VClosure` value — see `formal-semantics-completion.md` §2 Phase 8. The tool's
  WhyML-`fun` lowering above is a **sound lowering of the same construct**; the
  constructor-by-constructor IR alignment (5a) is the future LINK-1 refinement,
  the current representational boundary being documented (5b) in
  `src/self-annotate/arm-coverage.md`.
- **Divergence / Ignored:** first-class function *passing* (a lambda through a
  function parameter) and returning/escaping lambdas are **Ignored** — a
  documented non-goal (`phase8-plan.md` §5); such programs are rejected or
  fail verification rather than silently accepted.

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

**Content-faithful, not merely length (cleared-string.md).** Because each bridge pins its result
to a *native* `string.String` symbol (`concat` / `String.substring`) and Why3 1.8.2's
`string.String` is a **rich** theory — `length_concat`, `prefixof_concat`, `substring_length`,
`concat_substring`, `substring_substring`, `s_at`/`concat_at` — the exact CONTENT of concatenation
and slicing is provable with **zero new axiom**: `(a + b)[:len(a)] == a` (driver 0765),
`s[0:2] + s[2:4] == s[0:4]` (driver 0766), `s[0:i] + s[i:] == s`. This is a strict gain over the
old length-only reading, which is why the plan's `chars : seq int` codepoint model was **not**
needed — the native decomposition reasons better (spike
`test-suite/corpus/conformance/spikes/cleared-string-content.mlw`; choices.md cleared-string S0).

The `str_sub_op` length lemma and the `str_contains_op`/find witnesses are baked into the
bridge `ensures` because the general `String.length (substring …)` / existential-occurrence
algebra otherwise exhausts the SMT solver (the bridge `ensures` are *assumed*, being on an
abstract `val`). `startswith`/`endswith`/`find` apply to **any string-valued receiver** — a simple
`str`-typed name OR a *derived* string expression `(a + b).startswith(a)`, `s[i:].startswith(p)`
(lowered through `_str_method_recv_and_tail`; driver 0767); only a **multi-dot** receiver
(`self.name.startswith(…)`) or a non-string receiver keeps the opaque predicate-as-`0/1`-op model.
**Mixed string/int** comparison (a `str` vs an opaque int, e.g. a `.decode()` result) reverts to the
legacy opaque int-equality by hashing the string side (`str_hash_op`).

**Residual opacity (documented, honest boundary — cleared-string.md §5).** `lower`/`upper`:
Why3's `string.String` exposes **no** case-folding operation, and Python's `str.lower()`/`.upper()`
use *full* Unicode folding which is **not length-preserving** (`"ß".upper() == "SS"`), so
`str_case_op` keeps only the sound non-emptiness law (`len s ≥ 1 → len result ≥ 1`); its result is
an opaque `val` (each call fresh), so no CONTENT and not even `s.lower() == s.lower()` is claimed —
modelling simple/ASCII case folding + the literal→codepoint value bridge is high-cost / low-demand
and deferred. `replace` (string→string): the char-for-char case keeps `len pat = len rep → len
result = len s` (sound); the general grow/shrink case stays length-only (never claims length
preservation). Also opaque: `strip` (`len result ≤ len s` only), `split` (list-of-strings),
`.decode`/`.encode` (codec, the bytes↔str boundary), `%`/f-string CONTENT, and all lexicographic
code-point reasoning.

**Implementation:** `expressions.py` (`_is_string_expr`, `_content_string_method`,
`_emit_membership`, `_handle_binop`, `_handle_subscript`, `_handle_slice_access_expr`),
`functions.py` (`_param_type_str` + method-param loop → `string`), `preamble.py`
(`use string.String`).

### §T.6.16  `collections` constructors (real models)

The `collections` constructors are recognised by name (the bare form after
`from collections import X`) and **reduce to existing primitive models** — they are *not* opaque
stub calls — so realistic programs verify with content (`collections-plan.md`):

| Python | WhyML model | Reuses | Boundary |
|---|---|---|---|
| `defaultdict(int)` | `map int (option int)` (empty) | dict read/write; missing key → 0 | factory arg dropped; non-`int` factory out (default is hard-wired 0) |
| `Counter()` | same dict model | dict read/write; `c[k]+=1` desugars to `c[k]=c[k]+1` | `most_common`/ranking out |
| `OrderedDict()` | same dict model | dict alias | insertion order NOT modelled |
| `deque()` | empty `ArrayLit` → growable list (`Array.make 1024 0` + `_len`) | append/index/len | `appendleft`/`popleft`/`pop` out; seeded iterable modelled as empty |
| `namedtuple('P',[…])` | synthetic record `{f:int;…}` | Tier-A parametrized construction (§T.4.2) | literal fields only; dynamic fields → opaque |
| `ChainMap`/`User*` | opaque int handle | — | composition / subclass hooks out (Tier 3) |

Two supporting changes: `Module5._py_stmt_augassign` gained a `Subscript` arm so `c[k] += 1`
(and plain `arr[i] += v`) desugars to a store of `(c[k]) op v` instead of being silently
dropped; `Module5._synthesize_namedtuple_records` turns a module-level `Name = namedtuple(…)`
into a record `type_decl` with an implicit `__init__`. Seeded iterables / unmodelled members are
**sound under-approximations** — content that depends on them fails to prove, never proves falsely.

**Implementation:** `ir_scanner.py` (`find_array_and_dict_vars`, `uses_inline_set_or_dict_ops`),
`expressions.py::_handle_call_expr` (empty-ctor lowering), `Module5_IREmitter.py`
(`_py_expr_call` deque→ArrayLit, `_py_stmt_augassign` subscript arm,
`_synthesize_namedtuple_records`).

### §T.6.17  `itertools` length (`chain` / `product` / `islice`)

`len(...)` over an `itertools` combinator with **array operands of known length** lowers to the
closed-form length arithmetic — the combinator's *length* is first-order even though its element
stream is not, so $\mathcal{T}$ computes the length symbolically without materialising the iterator:

| Python | `len(...)` lowering | Notes |
|---|---|---|
| `chain(a, b, …)` | `\length(a) + \length(b) + …` | concatenation length; membership `x in chain(a,b)` is **out** (A8-2, ill-typed array membership) |
| `product(a, b, …)` | `\length(a) * \length(b) * …` | Cartesian-product cardinality |
| `islice(a, stop)` | `min(\length(a), stop)` | bounded prefix; `islice(a, start, stop)` → `max(0, min(\length(a), stop) - start)` |

Only the **length** is modelled (drivers 0530 chain, 0547 product, 0548 islice); the element stream
itself stays opaque, and `combinations` length (a binomial coefficient — not first-order) is a
gated imported-axiom follow-on (no-more-int Part 8, A8-4). Lazy/infinite iterators
(`cycle`/`count`/generators) are out of scope.

**Implementation:** `expressions.py::_iter_len_expr` (the chain/product/islice length builder),
reached from `_handle_len_call`.

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
| Floating-point arithmetic | Modeled as Why3 `real` (§T.2.2) | Real arithmetic/comparison verify; **mixed float/int** arithmetic and **transcendentals** (sin/cos/exp…) stay out of scope (opaque ops over `real`) |
| Integer overflow | Modeled as unbounded | Matches Python semantics |
| String operations | Real `string.String` content (§T.6) | length/concat/substring/structural `==` verify; **no char/code-point type** (`ord`, char ordering), and `upper`/`lower`/`strip`/`replace`/`split` and `.encode`/`.decode` stay opaque |
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
| G2 | ~~String hashing is lossy~~ **RESOLVED + content-faithful (cleared-string.md)** | Runtime `str` is Why3 `string.String` with real content (τ(str)=string; §T.6.15). Concatenation and slicing prove their exact CONTENT (not just length) via Why3 1.8.2's rich native theory — `(a+b)[:len a]==a` (0765), `s[0:2]+s[2:4]==s[0:4]` (0766) — with NO new axiom; `startswith`/`endswith`/`find` accept derived string receivers (0767). The `chars:seq int` codepoint model in the plan was NOT needed (native decomposition reasons better; spike + choices.md cleared-string S0). Residual (honest, documented): no code-point/char type; `upper`/`lower` (no Why3 case-fold op; full-Unicode folding not length-preserving), general grow/shrink `replace`, `strip`, `split`, `.decode`/`.encode`, `%`/f-string content stay opaque; `str`-keyed record-field dicts still hash the key | Case-fold codepoint model & general replace deferred |
| G3 | Boolean/int duality | `True + 1 = 2` in Python; in spec `true + 1` is a type error | The spec/body distinction handles this, but mixed use is fragile |
| G4 | `None` mapped to `0` in non-ghost context | `None` and `0` are indistinguishable in WhyML for regular Python values | **Partially resolved:** ghost dicts use `map int (option int)` (§T.8.5), so `\has_key` distinguishes absent keys from keys with value 0. Raw Python `None` in non-ghost context still maps to 0. |
| G5 | Array literals use fixed size 1024 | `[]` becomes `Array.make 1024 0` regardless of actual size | Use dynamic allocation or parametric size |
| G6 | Dict/Set comprehensions abstract; **ListComp content-faithful for simple shapes** (cleared-array.md S1–S4) | `[x for x in a]` / `[x+1 for x in a]` (identity / pure-int `+ - *` arithmetic over the loop target, over an `array int` source) now carry a per-index law `result[i] = <elt[target:=src[i]]>` + `length result = length src`; a filter `[x for x in a if …]` keeps only `length result <= length src`. Unliftable element shapes (call/projection with captures, string/seq/emit_ir elements, multi-generator) and `{}`/`{k:v for …}`/`{f(x) for …}` stay opaque | Implement concrete dict/set theories; lift more element shapes (projection/call) |
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
| List comprehensions (content) | Content-faithful for identity / pure-int `+ - *` arithmetic over the loop target (cleared-array.md S1–S4); filter keeps a length bound; other element shapes + dict/set comps opaque | Use explicit loops for unliftable elements |

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

### §T.14.4  `Union` / `Optional` / `X | Y` annotations (typing-engagement ty1)

PEP 484 `Union[X, Y]`, PEP 604 `X | Y`, and `Optional[X]` (= `Union[X, None]`)
are desugared at the front-end normalization seam
(`Module5_IREmitter._normalize_union_annotation`) into a per-annotation-site
synthesized `type_decl` of kind `variant`:

```whyml
type _union_<func>_<idx> = Arm_<idx>_0 of <T_0> | Arm_<idx>_1 of <T_1> | Arm_<idx>_None
```

**Translation table:**

| Form | IR `return_annotation` / symbol_table entry | WhyML |
|------|---------------------------------------------|-------|
| `x: Union[int, str]` | `_union_<f>_<i>` | `type _union_<f>_<i> = Arm_<i>_0 int \| Arm_<i>_1 string` |
| `x: Optional[int]` | `_union_<f>_<i>` | `type _union_<f>_<i> = Arm_<i>_0 int \| Arm_<i>_None` |
| `x: int \| str` | `_union_<f>_<i>` | same as `Union[int, str]` (C1) |
| `-> Optional[int]` | `_union_<f>_<i>` | return type is the variant; body auto-injects |

**Per-arm VCs** (`functions._emit_union_arm_vc`): C2 (injection —
`forall v: T_arm. exists u. u = Arm_i v`) and C3 (projection —
`forall u. match u with Arm_i v -> v=v | _ -> true end`).

**`is None` narrowing (C5):** `if x is None:` on a Union-typed `x` lowers to
`match x with Arm_<i>_None -> <true> | _ -> <false>` (Why3 forbids `=` on
algebraic types in a program `if`).

**Return-value auto-injection:** a function returning `Optional[int]` whose
body returns `expr` (an int) emits `Arm_<i>_0 (expr)`.

**`Any` arm (GT1):** dropped from the synthesized variant; reported in
`--soundness-report`. The static plane discharges C2/C3 against non-`Any`
arms only.

**Runtime shim** (`src/pycsl_lib/typ/__init__.py`): `Union(*args)` is
`#@ ensures \result == val` (identity, no validation — R1–R8, D4 no-blend).

### §T.14.5  `sorted` / `any` / `all` builtins

| Form | Why3 emission |
|------|---------------|
| `sorted(arr)` | abstract `val sorted_1 (a: array int) : array int` **+ length/sortedness/permutation `ensures`** |
| `any(arr)` | abstract `val any_1 (a: array int) : bool` |
| `all(arr)` | abstract `val all_1 (a: array int) : bool` |

**`sorted` (cleared-array.md S5, spike-proven S0-bis).** `sorted_1` now carries
three **definitional `ensures`** — discharged where `sorted` is *used*, NOT a
global axiom:

$$\texttt{sorted\_1}(a):\quad
  \texttt{Array.length result = Array.length } a
  \;\wedge\;
  (\forall i.\ 0 \le i < \texttt{len} - 1 \Rightarrow \texttt{result}[i] \le \texttt{result}[i{+}1])
  \;\wedge\;
  \texttt{permut result } a.$$

The sortedness clause is the exact formula `\is_sorted(result, 0, \length(result))`
lowers to, and the permutation clause reuses the SAME uninterpreted `permut`
predicate that `\permutation(result, a)` lowers to (argument order `result, a`),
so a driver's `\is_sorted` / `\permutation` postconditions match the emission
directly (corpus `0760`). The conjunction is satisfiable (a sorted permutation
always exists) ⇒ no vacuity; adding `ensures` to an abstract val is monotone ⇒
cannot regress a previously-opaque proof. `any_1` / `all_1` remain opaque.

The target of `s = sorted(arr)` is tracked as array-typed (via
`is_array_val` recognising the `(sorted_1 ` prefix), so the pre-decl
path emits `let s = (sorted_1 arr) in` instead of `let s = ref 0 in`.

### §T.14.5a  Content-faithful list comprehensions (cleared-array.md S1–S4)

A list comprehension `[elt for t in src (if cond)]` is lowered by
`_content_comp` (`module6_whyml/expressions.py`) to a **per-instance abstract
val** `list_content_comp_<n>` carrying a per-index content law — *when* the
element shape is liftable — and otherwise falls through to the opaque
length-only `list_comp` path (§T.11.1 G6).

**Liftable shape (S1 identity, S3 arithmetic):** exactly one generator whose
target `t` is a plain name, an `array int` source `src` (NOT a `seq` local —
the seq comprehension path owns those), no filter, and an element `elt` that is
a **pure, total `int`** expression over the loop target `t` ONLY (identity `t`,
integer literals, and the total operators `+ - *`; division/modulo, calls,
subscripts, attributes, comparisons and booleans are excluded — they are not
guaranteed pure-int logic terms, and division would leak partiality into a logic
`ensures`). The emitted val:

$$\texttt{list\_content\_comp}_n(\textit{src}):\quad
  \texttt{Array.length result = Array.length } \textit{src}
  \;\wedge\;
  \bigl(\forall i.\ 0 \le i < \texttt{len}\ \textit{src} \Rightarrow
     \texttt{result}[i] = \textit{elt}[\,t := \textit{src}[i]\,]\bigr).$$

The element is lowered once with the target `t` rebound (via a fresh scalar
binder `_celt = src[i]`) to the per-index source read, in logic context. The
free variables of `elt` must be `⊆ {t}` (a captured enclosing local is not a
parameter of the val ⇒ opaque fallback). Corpus: `0761` (identity), `0762`
(arithmetic), `0764` (NEGATIVE — a false `result[i] = a[i]+1` claim on an
identity comprehension is correctly rejected).

**Filter (S4):** a comprehension with an `if` keeps ONLY the sound bound
`Array.length result <= Array.length src` — the surviving elements are not at
their source indices, so no per-index content law holds (corpus `0763`). The
*exact* filtered contents are a documented residual.

**Residuals (opaque, never a false content claim):** unliftable element shapes
(call `[g(x) …]`, projection `[x.f …]` / `[x[k] …]`, string / seq / emit_ir
elements, multi-generator, captured locals) fall through to `list_comp` /
`list_comp_stmts` / `list_comp_seq_*` (length-only or fully opaque); set/dict
comprehensions stay opaque (§T.11.1 G6). No new `proof_axiom_allowlist` entry —
the content law is a definitional `ensures` on the abstract val, discharged
where the comprehension is used.

### §T.14.6  `Literal[v1, ..., vn]` annotations (typing-engagement ty1)

PEP 586 `Literal[v1, ..., vn]` is desugared at the front-end normalization seam
(`Module5_IREmitter._normalize_literal_annotation`) into a per-annotation-site
synthesized **ground `requires` clause** (parameters) or **ground `ensures`
clause** (return) — a finite disjunction of concrete-value equalities:

```whyml
let function f (x: int)
  requires { (x = 1 \/ x = 2) }   (* synthesized from x: Literal[1, 2] *)
  ensures  { ... }                  (* user-written *)
= ...
```

**Translation table:**

| Form | IR `return_annotation` / symbol_table entry | WhyML |
|------|---------------------------------------------|-------|
| `x: Literal[1, 2]` | `int` + synthesized `requires` | `requires { (x = 1 \/ x = 2) }` |
| `x: Literal["a", "b"]` | `str` + synthesized `requires` | `requires { (x = "a" \/ x = "b") }` (`use string.String` auto-imported) |
| `x: Literal[True, False]` | `int` + synthesized `requires` | `requires { (x = 1 \/ x = 0) }` (bool-as-int convention) |
| `x: Literal[None]` | `int` + synthesized `requires` | `requires { (x = 0) }` (None → 0) |
| `x: Literal[1]` (L5b degenerate) | `int` + synthesized `requires` | `requires { (x = 1) }` (no `\/` wrapper) |
| `-> Literal[1, 2]` | `int` + synthesized `ensures` | `ensures { (\result = 1 \/ \result = 2) }` |

The synthesized clause reuses the EXISTING `contracts.requires` / `contracts.ensures`
IR list and the EXISTING `BinOp`(`or`)/`==`/`Number`/`String`/`Bool`/`None` IR
expression nodes — **no new IR node, no IR_VERSION bump, no new VC kind.** The
synthesized clause is appended AFTER the user-written `requires`/`ensures` (order
within `requires`/`ensures` is logically conjunctive and commutative, so this is a
rendering detail only).

**Per-clause VC mapping (L1–L5c):** L1 (value set) IS the synthesized
`requires`/`ensures` VC — Why3 discharges it as a standard precondition/
postcondition goal. L2 (narrowing by equality — `if x == 1:`) is emergent from
the standard path-condition VC on the existing `if x == v` lowering (the
disjunction is in the precondition, the path condition is the runtime `==` test,
and Why3's precondition-preservation-on-branch refines the disjunction on each
branch — no new node). L2a (chained narrowing) is L2 applied repeatedly. L2b
(`is None` for `Literal[None]`) lowers `is None` to `== 0` (the None convention),
then L2 applies. L3 (match/if-chain exhaustiveness) is emergent from the existing
postcondition VCs. L4/L4a/L4b/L5c are normalization-time rejections
(`_classify_literal_value`). L5/L5a/L5b are normalization-time canonicalization
(de-dup, source order, degenerate single-value).

**Rejected forms:** `Literal[b"x"]` (L4a — bytes not supported by PEP 586);
`Literal[Literal[...]]` (L5c — no nested Literal); `Literal[Color.RED]` (L4b —
Enum members out of scope); `Literal[1, "a"]` (sound stricter-than-S1 —
mixed-kind literals, PyCSL parameter types are monomorphic).

**Runtime shim** (`src/pycsl_lib/typ/__init__.py`): `Literal(*args, val)` is
`#@ ensures \result == val` (identity, no validation — LR1–LR8, LD3 no-blend).
The static L1 value-set obligation is NOT discharged by the shim (it is a
precondition VC, invisible to the runtime).

**No GT gap** is tagged for `Literal` — the literal value set is finite,
enumerated, and decidable (two-plane spec §4 confirms full soundness).

### §T.14.7  `Final[T]` annotations (typing-engagement ty1)

PEP 591 `Final[T]` (and bare `Final`) is **lowered at the front-end
normalization seam** to the degenerate single-attribute, single-writer form of
HAPPY's no-write confinement. The annotation's *type* is the inner type `T`
(F3 — no narrowing): `_normalize_final_annotation` recognizes `Final[T]`
(Subscript value=Name "Final") and bare `Final` (Name "Final"), returns `τ(T)`
(or `"Any"` for bare `Final`), and records the name in a per-module
**final registry** (`program_ir["final_registry"]`, omitted when empty →
byte-identical for Final-free modules). The write-policy is a
**static-semantics check** (`core_ir_semantic._check_final`), NOT a VC:

```whyml
(* x: Final[int] = 5  →  module constant x = 5 (the existing module-constant
   path). The type is `int` (F3 — Final does not narrow). NO synthesized
   contract, NO new IR node. *)

(* attr: Final[int] in class C  →  field type `int` (the existing field-type
   path). The write-policy is NOT emitted as a VC; it is a write-site check. *)
```

**Translation table:**

| Form | IR symbol_table / field type | WhyML | Write-policy |
|------|------------------------------|-------|--------------|
| `x: Final[int] = 5` (module) | `int` (module-constant path unchanged) | `constant x: int = 5` (existing path) | F1: declaration is the only write; any `Assign`/`AugAssign` to `x` in a function body → `PyCSLSemanticError` |
| `attr: Final[int]` (class body) | field type `int` (existing field path) | record field `attr: int` (existing path) | F2: `__init__`-only writes; any `FieldAssign`/`FieldAugAssign` to `self.attr` in a function body → `PyCSLSemanticError` |
| `x: Final[int]` (parameter) | `int` | `let f (x: int) = ...` (F3 — no `requires` synthesized) | (deferred — parameter Final is not registered; see spec §8 Q2) |
| `x: Final` (bare, module) | `Any` (no inference) | `constant x: int = <init>` | F1 (as above) |

**Per-clause VC mapping (F1/F2/F3 — there are NO VCs):** the write-policy is
decidable syntactically (a write either is or is not textually inside the
allowed perimeter), NOT by SMT. F1 (write-once) and F2 (`__init__`-only) are
the `_check_final` write-site walk (a `core_ir_semantic` check, modeled on
HAPPY's `_check_happy` pattern in its degenerate single-attribute,
single-writer form). F3 (no narrowing) is satisfied by construction — the
type tag is `T`, not a refined type; no narrowing VC is emitted (there is no
VC at all). F2a (the class-body `attr: Final[T]` declaration is not a write)
is normalization-time (the front-end emits an `Assign` ONLY when
`stmt.value is not None`). F2b (subclass `__init__` writes) is a documented
strictness gap (§6 of the spec): a subclass `D(C)`'s `__init__` write is not
caught (dunders are skipped from `ir["functions"]`) — a soundness-preserving
under-approximation.

**No new IR node, no IR_VERSION bump, no new VC kind.** The final registry
is an additive module-level metadata key; Module 6 ignores it, so emission is
byte-identical for every Final-free driver.

**Runtime shim** (`src/pycsl_lib/typ/__init__.py`): `Final(x0, x1, val)` is
`#@ ensures \result == val` (identity, no validation — FR1–FR6, FD2 no-blend).
It is explicitly NOT a write-guard descriptor — introducing one would blend
the planes (FR6). The static write-policy is NOT discharged by the shim (it is
a semantic check, invisible to the runtime).

**No GT gap** is tagged for `Final` — the write-restriction is a syntactic
write-site check (decidable by construction; the two-plane spec §4 confirms
full soundness).

---

### §T.14.8  `-> NoReturn` annotations (typing-engagement ty1)

_Corresponds to annotations.md §12.11._

PEP 484 `-> NoReturn` (and `-> typing.NoReturn`) is **lowered at the
front-end normalization seam** to a `false` postcondition: the function never
returns normally (it raises or diverges). `_build_function_ir`
(`Module5_IREmitter.py`) recognizes `NoReturn` (Name) and `typing.NoReturn`
(Attribute) in the return annotation and sets the IR flag `is_noreturn: true`
(a new optional `FunctionIR` field, IR v1.3 — emitted ONLY when true, so every
non-NoReturn driver stays byte-identical). The `return_annotation` stays `None`
(no return-value type — the body never reaches a normal exit); Module 6's
`find_return_type` yields `unit` (no `Return` statement).

```
T[[ def f() -> NoReturn: raise E() ]] =

  let f () : unit
    ensures { false }        (* NR1 — never returns normally *)
    raises { E }
  =
    raise E
```

**Static plane (Interpreted):** `is_noreturn: true` drives four obligations:

- **NR1** (`ensures { false }`): `functions.py:_emit_contracts` emits the
  `false` postcondition when `func_is_noreturn` is true. The VC discharges by
  the ABSENCE of a normal-exit path (the body raises or diverges), not by an
  inconsistent context.
- **NR2a** (body supports divergence): `core_ir_semantic._check_noreturn`
  rejects a NoReturn body containing a `Return` (normal-exit path) or lacking
  any `Raise` / diverging construct (`While`/`For`/`CriticalSection`/`Call`).
  A conservative sound under-approximation (stricter than S1 is permitted).
- **NR3** (unreachable successor): `core_ir_semantic._check_noreturn_successors`
  flags any statement following a call to a NoReturn function as dead code.
- **NR4** (vacuity-gate exemption): `pycsl.py:_run_vacuity_gate` SKIPS any
  function whose IR carries `is_noreturn: true`. The exemption is keyed on the
  IR flag (from the `-> NoReturn` annotation), NOT on the inferred `false`
  postcondition — the latter would exempt every genuinely-vacuous function.
  The probe is not emitted for the NoReturn function; a genuinely-vacuous
  function (no NoReturn) is still probed and flagged.

**Runtime plane (Shimmed):** `src/pycsl_lib/typ/__init__.py` provides a
`NoReturn` alias object (a module-level constant) — introspectable, NO
enforcement (NR-R1–NR-R5, NR-D2 no-blend). The runtime does NOT enforce
divergence (NR-R3). The static `false` postcondition is NOT discharged by the
shim.

**IR_VERSION bump (1.2 → 1.3, additive).** The `is_noreturn` field is ABSENT on
non-NoReturn functions (emitted only when true), so a `"1.0"`/`"1.1"`/`"1.2"`
IR without it remains byte-identical and ingestable. `"1.3"` is added to
`ACCEPTED_IR_VERSIONS`; older versions are kept.

**No GT gap** is tagged for `NoReturn` — the `false` postcondition is a genuine
proof obligation (the function must be shown to diverge or raise). The NR4
vacuity-gate exemption is a gate-precision concern (prevents a false POSITIVE),
not a soundness gap.

---

### §T.14.9  `TypedDict` annotations (typing-engagement ty2 / PEP 589)

PEP 589 `class Point(TypedDict): x: int; y: int` (and the functional form
`Point = TypedDict("Point", {"x": int, "y": int})`, plus PEP 655
`Required[T]`/`NotRequired[T]` per-key totality and `total=False` class-level
totality) is **lowered at the front-end normalization seam** to a record
`type_decl` with one field per declared key. Per the two-plane spec
(`typing-engagement/ty2/typeddict-twoplane-spec.md`) and the core-agent hard
rule (`typing-global-impl.md` §5, TY2): a TypedDict class synthesizes a WhyML
record `type td = { x: int; y: int }`, field access `p["x"]` becomes
record-field access `p.x`, and construction `{"x": 1, "y": 2}` becomes a
record literal.

**Normalization** (`Module5_IREmitter._emit_typeddict_record` /
`_synthesize_typeddict_functional`): the `visit_ClassDef` seam recognizes
`class X(TypedDict)` (a base name `TypedDict`) and dispatches to
`_emit_typeddict_record`, which walks the class body's `AnnAssign`s (the
`x: int` field declarations) and emits a record `type_decl` with one field
per declared key (field types resolved via the existing
Union/Optional/Final/Literal-aware resolver
`_field_type_from_annotation_inst`). Per-key totality (PEP 655) and
class-level totality (`total=False`) apply: a not-required key's type is
`Optional[T]` (reusing the TY1 Union variant synthesis). The functional form
`Point = TypedDict("Point", {...})` is recognized by
`_synthesize_typeddict_functional` (best-effort: only literal dicts; a
non-literal fields dict synthesizes nothing — byte-identical fallback).

**Field-access lowering**
(`module6_whyml/expressions._typeddict_field_access`, invoked from
`_handle_subscript`): a string-literal subscript `p["x"]` on a
TypedDict-record-typed receiver lowers to a record-field read `p.x` (via the
existing `_field_label`). Why3 type-checks the field's declared type natively
(T5/T6). A non-literal index or an unknown key falls through to the opaque
`subscript_get` path (Why3 rejects — static error). Non-TypedDict receivers
fall through unchanged (byte-identical).

**Construction lowering**
(`module6_whyml/expressions._typeddict_record_literal`, invoked from the
`DictLit` branch of `_expr_to_whyml`): a dict literal `{"x": 1, "y": 2}` in a
TypedDict construction context (the enclosing function's return type is a
TypedDict record) lowers to a record literal `{ x = 1; y = 2 }` in declaration
order. Why3 type-checks each field's value against the declared type and
rejects missing/extra fields natively (T8/T9). Non-TypedDict dict literals
fall through to the existing empty-map stub (byte-identical).

**Static plane (Interpreted):** the record `type_decl` with one field per
declared key; field access is a record-field read; construction is a record
literal. Each clause T2–T9 in the two-plane spec maps to one VC or one S5
conformance case (Why3 record-type-checking).

**Runtime plane (Shimmed):** a thin shim in
`src/pycsl_lib/typ/__init__.py.TypedDict` exposes the introspectable class
object with `#@ ensures \result == val` — identity, no validation (R1–R8,
D4 no-blend). A TypedDict instance IS a plain dict at runtime (S4); the shim
does NOT construct instances, only the class object. The class form
`class Point(TypedDict)` is lowered at the front-end seam — it never reaches
the shim; the functional form reaches the shim as an opaque identity call.

**No IR_VERSION bump.** The TypedDict construct reuses the EXISTING `type_decl`
(record) IR node and adds ONE optional boolean field `is_typeddict` (defaults
`False`), so the IR schema is backward-compatible: `type_decl.get("is_typeddict",
False)` reads as `False` for every pre-existing record. `IR_VERSION` stays at
`1.3`; `ACCEPTED_IR_VERSIONS` is unchanged.

**GT7** (analogous, NOT a new code) — D3 documents the
`isinstance`-against-TypedDict asymmetry: the static T2 record-shape
obligation must NOT be discharged by any runtime `isinstance`/presence check
(R4 raises `TypeError`; even `"x" in p` is the dict-plane behaviour, not the
static record-shape judgment). Tagged in the report as a
`no_blend_typeddict_isinstance` note.

**GT-T2-future** (out of scope) — cross-TypedDict structural subtyping (a
TypedDict with a superset of keys assignable to one with a subset) is flagged
for a future TY2 enhancement. This delivery limits T2 to same-named
assignability.

### §T.14.10  `NamedTuple` annotations (typing-engagement ty2 / PEP 526)

PEP 526 `class Point(NamedTuple): x: int; y: int` (and the functional form
`Point = NamedTuple("Point", [("x", int), ("y", int)])` per PEP 484) is
**lowered at the front-end normalization seam** to a record `type_decl` with
one field per declared key, in declaration order (positional index is
significant). Per the two-plane spec
(`typing-engagement/ty2/namedtuple-twoplane-spec.md`) and the core-agent hard
rule (`typing-global-impl.md` §5, TY2): a NamedTuple class synthesizes a
WhyML record `type nt = { x: int; y: int }` (reusing the TypedDict record
seam), named field access `p.x` becomes record-field access, positional access
`p[0]` becomes record-field access by index, and construction `Point(1, 2)`
becomes a record literal.

**Normalization** (`Module5_IREmitter._emit_namedtuple_record` /
`_synthesize_namedtuple_functional`): the `visit_ClassDef` seam recognizes
`class X(NamedTuple)` (a base name `NamedTuple`) and dispatches to
`_emit_namedtuple_record`, which walks the class body's `AnnAssign`s (the
`x: int` field declarations, in declaration order) and emits a record
`type_decl` with one field per declared key (field types resolved via the
existing Union/Optional/Final/Literal-aware resolver
`_field_type_from_annotation_inst`). A field with a default (`x: int = 0`,
N1b) populates `field_defaults`; a field without a default is a required
positional argument (N7). The record carries `init_params` (field names in
order) and `init_body` (each field set from its same-named param) so
positional construction `Point(1, 2)` reuses the EXISTING Tier-A parametrized
record construction (`_call_record_constructor`). The functional form
`Point = NamedTuple("Point", [...])` is recognized by
`_synthesize_namedtuple_functional` (best-effort: only literal
`[("name", type), ...]` lists; a non-literal fields list synthesizes nothing
— byte-identical fallback). The pre-existing `_synthesize_namedtuple_records`
(functional `collections.namedtuple` form, all-int fields) is NOT modified —
it handles a different factory.

**Named-field-access lowering** (the EXISTING
`module6_whyml/expressions._handle_attribute_expr` path): a NamedTuple-
record-typed param is added to `_record_locals` by `_param_type_str`, so
`p.x` emits `p.x` (a record-field read). Why3 type-checks the field's declared
type natively (N4). An unknown attribute (`p.z`) is a Why3 type error (the
field doesn't exist). Non-NamedTuple receivers fall through unchanged
(byte-identical).

**Positional-access lowering**
(`module6_whyml/expressions._namedtuple_positional_access`, invoked from
`_handle_subscript`): an integer-literal subscript `p[0]` on a
NamedTuple-record-typed receiver lowers to a record-field read of the field
at that declaration index (`p[0]` → `p.x`, `p[1]` → `p.y`, via the existing
`_field_label`). Why3 type-checks the field's declared type natively (N5). An
out-of-range index (`p[2]` on a 2-field Point) or a non-literal index falls
through to the opaque `subscript_get` path (Why3 rejects — static error).
Non-NamedTuple receivers fall through unchanged (byte-identical).

**Construction lowering** (the EXISTING
`module6_whyml/expressions._call_record_constructor` path): a positional call
`Point(1, 2)` with `init_params` matching arity emits a record literal
`{ x = 1; y = 2 }` in declaration order. Why3 type-checks each field's value
against the declared type natively (N6).

**Static plane (Interpreted):** the record `type_decl` with one field per
declared key (in declaration order); named field access is a record-field
read; positional access is a record-field read by index; construction is a
record literal. Each clause N2–N7 in the two-plane spec maps to one VC or one
S5 conformance case (Why3 record-type-checking).

**Runtime plane (Shimmed):** a thin shim in
`src/pycsl_lib/typ/__init__.py.NamedTuple` exposes the introspectable class
object with `#@ ensures \result == val` — identity, no validation (R1–R9,
D4 no-blend). A NamedTuple instance IS a plain tuple at runtime (S4); the
shim does NOT construct instances, only the class object. The class form
`class Point(NamedTuple)` is lowered at the front-end seam — it never reaches
the shim; the functional form reaches the shim as an opaque identity call.

**No IR_VERSION bump.** The NamedTuple construct reuses the EXISTING `type_decl`
(record) IR node and adds ONE optional boolean field `is_namedtuple` (defaults
`False`), so the IR schema is backward-compatible: `type_decl.get("is_namedtuple",
False)` reads as `False` for every pre-existing record. `IR_VERSION` stays at
`1.3`; `ACCEPTED_IR_VERSIONS` is unchanged.

**GT7** (analogous, NOT a new code) — D3 documents the
`isinstance`-against-NamedTuple asymmetry: the static N2 record-shape
obligation must NOT be discharged by any runtime `isinstance`/tuple-shape
check (R4 is a tuple-ness check, not a type-enforcement check). Tagged in the
report as a `no_blend_namedtuple_isinstance` note.

### §T.14.11  `@overload` annotations (typing-engagement ty2 / PEP 484)

PEP 484 `@overload` — a sequence of `@overload def f(p_i: T_i) -> R_i: ...`
stubs (each with a literal `...`/`pass` body) followed by one non-`@overload`
implementation `def f(p) -> R: <body>` — is lowered as a **guarded contract
family** (the TY2 hard rule: "overload -> a guarded contract family proved
against the single implementation"). NO `\trusted`; NO IR_VERSION bump (reuses
the existing `contracts.ensures` list + the existing `==>`/`isinstance` IR
shapes).

**Front-end recognition** (`src/pycsl/frontend/Module5_IREmitter.py`):
`_is_overload_stub(node)` returns True iff `node.decorator_list` contains a
`Name("overload")` or `Attribute(attr="overload")` AND `node.body` is exactly
`[Expr(Constant(Ellipsis))]` or `[Pass]` (O1a — the `...`/`pass` body). The
stub is NOT emitted as a function IR node (its body is discarded — R1). A
stub's `#@ ensures Q_i` must PRECEDE the `@overload` decorator (the CSL
contract-placement convention — a `#@` between `@overload` and `def` lands on
the decorator line, not the `def` line).

**Guard synthesis** (`_synthesize_overload_guard` / `_build_overload_param_guard`
/ `_overload_type_name`): for each stub parameter `p_i: T_i`, the guard is
`isinstance(p_i, T_i)` — the IR `{"type": "Call", "func": "isinstance", "args":
[Var(p_i), Var(T_i)]}`. For each stub `#@ ensures Q_i`, the guarded
postcondition `{"type": "BinOp", "op": "==>", "left": <guard>, "right": <Q_i
IR>}` is built and collected into `self._pending_overloads[name]`.

**Implementation attachment** (`visit_FunctionDef`): when the non-`@overload`
implementation `def f(...)` is visited, the collected guarded postconditions
are appended to `func_ir["contracts"]["ensures"]` (after the user-written +
Literal ensures, like the Literal accumulator pattern). Then the existing
function-IR path proceeds (byte-identical for non-overload drivers — the
`_is_overload_stub` check is a pure decorator-name + body-shape test that
fires only when `@overload` is present).

**Module 6 lowering** (`src/pycsl/module6_whyml/`): NO new code. The guarded
postcondition `G_i ==> Q_i` lowers through the EXISTING `_emit_contracts` path
(`functions.py:266`): each `ensures` clause is rendered via `_expr_to_whyml`,
which handles `BinOp("==>")` via the existing identifier map
(`identifiers.py:23` maps `==>` → `->`) and `Call("isinstance", ...)` via
`_handle_isinstance` (`expressions.py:2024` → `(subtag (typeof p_i) <T_i
tag>)`). The resulting WhyML line is
`ensures { (subtag (typeof p_i) <T_i tag>) -> <Q_i whyml> }`. The
implementation's body proves each `G_i ==> Q_i` under the guard assumption
(O6). At a call site `f(v)`, the argument's static type selects the active
overload by type-based assignability (O4) — native Why3 type-checking when the
implementation's parameter is typed. For the guard to be a decided type
judgment, the implementation's parameter must carry a type annotation (TY2
scope restriction — divergence-by-strictness; an unannotated implementation
yields a symbolic `typeof_op` guard, sound but imprecise).

**Runtime shim** (`src/pycsl_lib/typ/__init__.py.overload`): a thin identity
(`#@ ensures \result == val`) that performs NO validation (R1–R7). The real
runtime `overload(func)` registers `func` and returns `_overload_dummy` (S4);
the shim models this as identity — the stub is discarded at runtime (R1) and
the implementation runs (R2). The `ensures \result == val` carries ONLY the
identity postcondition — the static guarded-postcondition family is NOT
discharged by the shim (it is Why3 SMT over the guard, invisible to the
runtime).

**No IR_VERSION bump.** The `@overload` construct reuses the EXISTING
`contracts.ensures` list and the EXISTING `==>`/`isinstance` IR shapes. NO new
IR node, NO new field. The IR schema is unchanged; `IR_VERSION` stays at `1.3`;
`ACCEPTED_IR_VERSIONS` is unchanged.

**GT7** (analogous, NOT a new code) — D1 documents the `isinstance`-dispatch
no-blend trap: the static O4/O5 type-based-selection obligation must NOT be
discharged by any runtime `isinstance` check in the implementation (R4 is
value dispatch, not type judgment). The guard is a WhyML spec formula over the
parameter's type tag (decided from Γ's τ); the runtime `isinstance` is body
code (a value check). Tagged in the report as a
`no_blend_overload_isinstance` note.

---

### §T.14.12  `Protocol` / `@runtime_checkable` / `#@ conforms_to` annotations (typing-engagement ty2 / PEP 544)

PEP 544 `Protocol` — `class P(Protocol): def m(self, ...) -> R: ...` — is lowered
as a **contract interface** (the TY2 hard rule: "Protocol -> a contract interface,
conformance as per-method behavioural refinement"). NO `\trusted`; NO IR_VERSION
bump (reuses the EXISTING `abstract` function flag + the EXISTING `overrides` IR
list + the EXISTING refinement-goal emitter).

**Front-end recognition** (`src/pycsl/frontend/Module5_IREmitter.py`):
`_is_protocol_class(node)` returns True iff `node.bases` contains a `Name("Protocol")`
or `Attribute(attr="Protocol")`. `_emit_protocol_interface(node)` then synthesizes
(a) a marker record `type_decl` with `is_protocol: True` and NO fields (a protocol
has no instance state — the record is the interface anchor), and (b) each protocol
member `def m(self, ...) -> R: ...` as a function IR node with `abstract: True`
(a bodyless `val` with its contract — the refinement target, P1a). The member's
`#@ ensures/requires/assigns` is the refinement TARGET. The member's body
(`...`/`pass` by PEP 544 convention) is NOT lowered. `self._protocols[P] = {m1,
m2, ...}` records the member names for the conformance pass. NOTE: no
`generic_visit(node)` — the protocol members are emitted explicitly by
`_emit_protocol_interface`; `generic_visit` would re-visit each member and emit
it AGAIN.

**Conformance declaration** (`#@ conforms_to P`, a class-level directive harvested
by `Module3_Weaver.visit_ClassDef` from `Module2_Parser.ConformsToDecl`): when a
non-protocol class `C` carries `#@ conforms_to P`, `_populate_protocol_conformance`
(AFTER `generic_visit` so `C__m` is in `program_ir["functions"]`) records, for
each member `m` of `P` that `C` provides, an `(C__m, P__m)` override pair in the
EXISTING `overrides` IR list. A class missing a member raises `PYCSLSEMANTICERROR`
(P3 — non-conformance is a static error). A conformance declaration against a
non-Protocol class also raises (P3). PEP 544 conformance is structural/implicit;
PyCSL's TY2 scope requires the explicit directive (divergence-by-strictness — an
implicit structural search is outside the per-module verification model).

**Module 6 lowering** (`src/pycsl/module6_whyml/`): NO new code for the member. The
`abstract: True` flag lowers through the EXISTING `_emit_function` path
(`functions.py:620`): `func_abstract = func.get("abstract", False)` →
`emit_as_val = func_trusted or func_abstract` → a bodyless `val` with the contract
is emitted. The return type of an abstract member whose body has no return
statement is promoted from the `-> T` annotation (the contract's return type is
the annotation, not the empty body — `_compute_return_type` promotes `ann` when
`abstract` and `return_type == "unit"`). The conformance refinement goal lowers
through the EXISTING `_emit_subtyping_goals` path (`functions.py:794`): for each
`overrides` entry, `_render_refinement_goal` emits
`goal <C__m>_refines_<p> : forall self: C, .... ((pre_P -> pre_C) /\\ (post_C ->
post_P))` — the per-method behavioural-refinement VC (P2). This is discharged by
Why3/SMT from the two contracts (no body execution required). The
`assigns`-refinement (`assigns(C.m) ⊆ assigns(P.m)`) is NOT separately checked by
the existing emitter (it checks pre weakening + post strengthening); a protocol
member's `assigns` is typically `\nothing` (a pure query).

**Runtime shim** (`src/pycsl_lib/typ/__init__.py.runtime_checkable`): a thin
identity (`#@ ensures \result == val`) that performs NO validation (R1–R7). The
real runtime `runtime_checkable(cls)` (S4) returns `cls` unchanged after installing
a `hasattr`-loop `__instancecheck__` that checks attribute PRESENCE ONLY (R3 — not
signature, not contract, not attribute type); the shim models this as identity.
The `ensures \result == val` carries ONLY the identity postcondition — the static
per-method refinement VC is NOT discharged by the shim (it is Why3 SMT over the two
contracts, invisible to the runtime).

**No IR_VERSION bump.** The `Protocol` construct reuses the EXISTING `abstract`
function flag + the EXISTING `overrides` IR list, and adds a record-level
`is_protocol: True` boolean (same shape as `is_typeddict`/`is_namedtuple`, which
did NOT bump the version). NO new IR node, NO new wire-format field. The IR schema
is unchanged; `IR_VERSION` stays at `1.3`; `ACCEPTED_IR_VERSIONS` is unchanged.

**GT7** (THIS IS the canonical GT7 trap, not an analogue) — D1 documents the
`@runtime_checkable` presence-vs-conformance divergence: the static P2/P4
per-method contract-refinement obligation must NOT be discharged by any runtime
`isinstance`/`hasattr` presence check (R3 is attribute presence, a value check,
NOT the contract-refinement type judgment). The refinement goal is a WhyML spec
formula over the two contracts (discharged by SMT); the runtime `hasattr` is a
value check. Tagged in the report as a `no_blend_protocol_presence` note.

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

---

## §T.Ann  Annotation Lowering Table (S7 Transcription — TY0)

> **Tier-0 (TY0) transcription.** This section pins the **de facto** lowering
> of Python-side annotations (`: T` and `-> R`) to WhyML types as of the S7
> witness sweep (`typing-engagement/ty0-witness/VERDICTS.md`, 13 probed
> forms). It is a transcription of existing emitter behavior, not a design
> choice — the table below records what `module6_whyml/functions.py` and
> `frontend/Module5_IREmitter.py` actually emit today. No `src/pycsl/` code
> was modified to produce this section. The §T.2.2 type-mapping table is
> the *intended* mapping; this section is the *observed* S7 baseline for the
> bare-annotation forms that the §T.2.2 table does not exhaustively enumerate.

### §T.Ann.1  Disposition Key

Each probed annotation form receives one of three dispositions
(VERDICTS.md §disposition key):

- **INTERPRETED** — the annotation lowers to a concrete WhyML type **distinct
  from the unannotated default** (`int`). The unannotated baseline is
  `let f (x: int) : int` (VERDICTS.md §baseline).
- **IGNORED** — the annotation is present in source but PyCSL drops it
  silently: the emitted WhyML signature is byte-identical to the unannotated
  baseline, and no error is raised.
- **REJECTED** — PyCSL raises a parse/semantic error on the form. (No form
  in the S7 sweep was rejected.)

### §T.Ann.2  Full Lowering Table

| # | Annotation form | Source line | Disposition | Emitted WhyML | # cite |
|---|-----------------|-------------|-------------|---------------|--------|
| 1a | `int` | `def f(x: int) -> int` | IGNORED | `let f (x: int) : int` (= baseline; `int` is the default `int_type`, so the annotation carries no info) | `src/pycsl/frontend/Module5_IREmitter.py:1757-1801` (return_annotation capture), `:1693` (arg symbol_table capture); `src/pycsl/module6_whyml/functions.py:52` (default `int_type` fallback) |
| 1b | `bool` | `def f(x: bool) -> bool` | IGNORED | `let f (x: int) : int` (no `bool` arm in `_param_type_str` / `_compute_return_type`; falls through to default `int`) | `src/pycsl/module6_whyml/functions.py:13-52`, `:514-544` |
| 1c | `float` | `def f(x: float) -> float` | INTERPRETED | `let f (x: real) : real` | `src/pycsl/module6_whyml/functions.py:38-40` (param), `:534-535` (return) |
| 2a | `bytes` | `def f(x: bytes) -> bytes` | INTERPRETED (L3-tc ✗ — see §T.Ann.4) | `let f (x: array int) : array int` (the `array` WhyML theory is NOT imported by the default-model preamble for this bare-`bytes`-only signature shape, so the resulting module fails L3 type-check in isolation) | `src/pycsl/module6_whyml/functions.py:29-33` (param), `:522-524` (return); preamble-import gap in `src/pycsl/module6_whyml/preamble.py` |
| 2b | `str` | `def f(x: str) -> str` | INTERPRETED | `let f (x: string) : string` | `src/pycsl/module6_whyml/functions.py:34-37` (param), `:532-533` (return) |
| 3a | `list` | `def f(x: list) -> list` | INTERPRETED | `let f (x: array int) : array int` (bare `list` lowers to `array int`) | `src/pycsl/module6_whyml/functions.py:29` (param, `symtype in ("list", "bytes", "bytearray")`), `:522-524` (return) |
| 3b | `dict` | `def f(x: dict) -> dict` | INTERPRETED | `let f (x: map int (option int)) : map int (option int)` | `src/pycsl/module6_whyml/functions.py:27-28` (param, `symtype in ("set", "dict", "frozenset")`), `:530-531` (return) |
| 3c | `tuple` (bare) | `def f(x: tuple) -> tuple` | IGNORED | `let f (x: int) : int` (no bare-`tuple` arm; falls through to default `int`. Subscripted `Tuple[int, int]` IS handled via the tuple-return refinement path `_refine_tuple_return_type`, but the bare form is not.) | `src/pycsl/module6_whyml/functions.py:13-52`, `:514-544` |
| 4 | `-> None` (non-lemma) | `def f(x: int) -> None: return None` | IGNORED | `let f (x: int) : int` with body `0` (`return_annotation == "None"` IS consulted for `#@ lemma` ghost discipline → `unit`, but for a non-lemma function it has no effect on the WhyML return type, and `return None` is emitted as `0`) | `src/pycsl/frontend/Module5_IREmitter.py:1761-1762`; `src/pycsl/module6_whyml/functions.py:521-544` (only `lemma` branch consults it for `unit`, `:556-559`); `src/pycsl/core_ir_semantic.py:763-765` |
| 5 | stringized fwd-ref | `def f(x: "Foo") -> "Foo"` | IGNORED | `let f (x: int) : int` (param: `_m5_get_type_name` has no `ast.Constant` arm → returns `"Any"` → default `int`; return: `return_annotation = "Foo"` is captured but no Module 6 arm matches it → default `int`. Asymmetric — see static-semantics §11.3) | `src/pycsl/frontend/Module5_IREmitter.py:1607-1632` (no `ast.Constant` arm), `:1761-1762` |
| 6a | bare name, class AFTER | `def f_before(x: Foo) -> Foo` (`class Foo` below) | IGNORED | `let f_before (x: int) : int` (`Foo` captured into `symbol_table["x"] = "Foo"` and `return_annotation = "Foo"`, but `Foo` is not in `_record_types` / `_variant_types` — no `#@ datatype` / record decl — so `_param_type_str` falls through to default `int`. Forward position is irrelevant.) | `src/pycsl/module6_whyml/functions.py:13-52`, `:514-544`; `src/pycsl/frontend/Module5_IREmitter.py:1607-1632` |
| 6b | bare name, class BEFORE | `def f_after(x: Bar) -> Bar` (`class Bar` above) | IGNORED | `let f_after (x: int) : int` (same as 6a: a bare Python `class Bar` without `#@ datatype` / record annotation is not registered in `_record_types`; position before/after makes no difference) | `src/pycsl/module6_whyml/functions.py:13-52`, `:514-544` |
| 6c | UNDEFINED name | `def f(x: "Baz") -> "Baz"` (`Baz` never defined) | IGNORED | `let f (x: int) : int`, L3-tc ✓ (no name-resolution / forward-reference check on annotations at any pipeline stage — GT5 gap, see static-semantics §11.1) | `src/pycsl/frontend/Module5_IREmitter.py:1607-1632`; `src/pycsl/core_ir_semantic.py` (no annotation-name-resolution pass) |

### §T.Ann.3  INTERPRETED Set (Distinct Concrete WhyML Type)

The five (six, counting the unprobed `set`/`frozenset` siblings of `dict`)
annotation forms that lower to a concrete WhyML type distinct from the
default `int`:

| Annotation | WhyML type | # cite |
|------------|-----------|--------|
| `float` | `real` | `src/pycsl/module6_whyml/functions.py:38-40`, `:534-535` |
| `str` | `string` | `src/pycsl/module6_whyml/functions.py:34-37`, `:532-533` |
| `list` | `array int` | `src/pycsl/module6_whyml/functions.py:29`, `:522-524` |
| `dict` | `map int (option int)` | `src/pycsl/module6_whyml/functions.py:27-28`, `:530-531` |
| `bytes` | `array int` (⚠ L3-tc gap — §T.Ann.4) | `src/pycsl/module6_whyml/functions.py:29-33`, `:522-524` |

### §T.Ann.4  IGNORED Set (Silently Dropped to Default `int`)

The eight annotation forms that are silently dropped to the default `int` /
`int`-typed body, with no diagnostic:

| Annotation | Reason for drop | # cite |
|------------|----------------|--------|
| `int` | Redundant — `int` is already the default `int_type` | `src/pycsl/module6_whyml/functions.py:52` |
| `bool` | No `bool → bool` arm in `_param_type_str` / `_compute_return_type` | `src/pycsl/module6_whyml/functions.py:13-52`, `:514-544` |
| `tuple` (bare) | No bare-`tuple` arm (subscripted `Tuple[…]` IS handled via a separate refinement path) | `src/pycsl/module6_whyml/functions.py:13-52`, `:514-544` |
| `-> None` (non-lemma) | `return_annotation == "None"` captured but only consulted by the `#@ lemma` branch | `src/pycsl/module6_whyml/functions.py:521-544`, `:556-559`; `src/pycsl/frontend/Module5_IREmitter.py:1761-1762` |
| stringized param `"Foo"` | `_m5_get_type_name` has no `ast.Constant` arm → returns `"Any"` → default `int` | `src/pycsl/frontend/Module5_IREmitter.py:1607-1632` |
| stringized return `-> "Foo"` | Raw string captured into `return_annotation` but no Module 6 arm matches it | `src/pycsl/frontend/Module5_IREmitter.py:1761-1762`; `src/pycsl/module6_whyml/functions.py:514-544` |
| bare class name (`Foo`, `Bar`) | Class not registered in `_record_types` (no `#@ datatype` / record decl) → falls through | `src/pycsl/module6_whyml/functions.py:13-52`; `src/pycsl/frontend/Module5_IREmitter.py:1607-1632` |
| UNDEFINED name (`"Baz"`) | No name-resolution pass exists (GT5 gap) → falls through | `src/pycsl/frontend/Module5_IREmitter.py:1607-1632`; `src/pycsl/core_ir_semantic.py` |

### §T.Ann.5  The `bytes` L3-Type-Check Gap

**Currently, PyCSL lowers** `x: bytes` / `-> bytes` to the WhyML type
`array int` (`src/pycsl/module6_whyml/functions.py:29-33` for parameters,
`:522-524` for returns — the `bytes`/`bytearray`/`list` arm). However, the
default `hoare`-model preamble (`src/pycsl/module6_whyml/preamble.py`)
only imports `use array.Array` when the array theory is *triggered* by an
array-typed local or similar emission — a signature that is *only*
`bytes`-typed (no array locals) does not trigger the import, producing a
WhyML module that fails L3 type-check with:

```
unbound type symbol 'array'
```

(VERDICTS.md §2a). The annotation IS interpreted (it lowers to a concrete
type), but the resulting module is broken in the default model in
isolation. The `typed` / `store` memory models import `array` unconditionally
and are likely unaffected; and a real program with array locals alongside a
`bytes` parameter will trigger the import and type-check. The gap is
specific to the bare-`bytes`-only-signature case. This is recorded as S7
SURPRISE.2 — not fixed in TY0.

---

## §T.TY3 — Whole-module monomorphization (TypeVar/Generic, PEP 484 + PEP 695)

The monomorphization machinery is a **step-5 IR-resolution pass**
(`frontend/monomorphize.py:apply_monomorphization`), wired into
`frontend/ir_resolve.resolve` AFTER `apply_inline_globals` and BEFORE Module 6
(WhyML emission). It operates on the resolved IR dict + the woven AST; it is a
no-op (early return) when no type_decl/function carries `type_params`, keeping
every non-generic module byte-identical (total additivity). *Cites S1; the
closed-module enabling assumption per `docs/typing-global-overview.md` §4.1.*

### §T.TY3.1 — IR shape (v1.4, additive)

A new optional TYPE-DECL field `type_params` and a new optional FUNCTION field
`type_params`, each a list of `{"name": str, "bound": Optional[str], "kind":
str}`. ABSENT on non-generic decls (emitted only when non-empty) →
byte-identical for unaffected drivers. `IR_VERSION` is bumped 1.3 → 1.4
(additive; `"1.4"` added to `ACCEPTED_IR_VERSIONS`).

### §T.TY3.2 — COLLECT

`_collect_instantiations` scans the IR `functions` bodies for
`Call(Subscript(Name(generic), <concrete-type>))` patterns and annotation
subscripts; `_collect_instantiations_ast` scans the woven AST for module-level
sites (`if __name__ == ...` blocks, which are NOT in the IR functions list).
Returns the deduped `(generic, concrete_type)` set.

### §T.TY3.3 — GT3 / GT4 loud-fails

`_check_gt3_schema_only` rejects any `type_params` entry whose `kind !=
"TypeVar"` (ParamSpec/TypeVarTuple). `_check_gt4_polymorphic_recursion` scans
the AST for a generic function `f[T]` whose body calls `f[T]()` (the TypeVar
itself — non-terminating).

### §T.TY3.4 — BOUNDS (invariant, GT2)

`_check_bounds` verifies each `(generic, concrete_type)` with a bound `B`
satisfies `concrete == bound` (invariant checking). Rejects `Any` (GT1).

### §T.TY3.5 — EMIT

`_emit_specializations` deep-copies the generic's type_decl + methods for each
`(generic, concrete_type)` pair, substituting the TypeVar by the concrete type
in field types, signatures (`symbol_table`, `return_annotation`, `self_type`),
and contract clauses (recursively via `_subst_type_in_ir`), with name-mangling
(`Stack` → `Stack_int`, `stack__push` → `stack_int__push`). Call sites
`Stack[int]()` → `Stack_int()` and annotations are rewritten. The original
generic decl + methods are REMOVED (replaced by the copies).

### §T.TY3.6 — CLASSIFY

Specialized copies are ordinary monomorphic IR (Interpreted by default). An
un-instantiated generic is recorded Ignored/GT8 in
`ir["monomorphization_report"]["uninstantiated"]`.

### §T.TY3.7 — Gap: multi-instantiation field-mangling

When two specialized copies share field names (e.g. `Stack_int._items` and
`Stack_str._items`), Module 6's record field-mangling prefixes the field names
but does NOT consistently rewrite the invariant/requires/body references. This
is a Module 6 consistency gap (see `typing-engagement/ty3/33-1700-typing-gap-9.md`),
NOT a monomorphization bug. The single-instantiation path (the feasibility-probe
shape) proves 10/10 VCs.

### §T.TY3.8 — `Callable` (PEP 484) — function-type parameter

A `Callable[[A1, ..., An], R]`-typed parameter lowers to a curried WhyML
**function-type parameter** (C1). The call site `f(a1, ..., an)` already lowers
to WhyML application `(f a1 ... an)` (the existing Call lowering — unchanged);
once `f` carries a function type, Why3's typecheck discharges the arg-type
obligation (C2) and the result type (C3). No `\trusted`. No new IR field.

**Recognition (Module 5).** `_m5_get_type_name_legacy` recognizes a `Subscript`
whose head is `Callable` and encodes the arg-list + return type into the
EXISTING `symbol_table` value string as `"callable:<a1>,...-><r>"` (e.g.
`"callable:int,str->bool"`). This is a new tag VALUE, NOT a new IR field — no
`IR_VERSION` bump (IR stays at 1.4). The encoding is constructed by
`_encode_callable_annotation`; `_callable_type_tag` refuses unsupported
arg/return types (C5 — `bytes`/`list`/`dict`/`set`/`Any`/nested-`Callable`/
ellipsis) with `PYCSL-TY3-CALLABLE-SCOPE` (sound scope limit). `Any` is refused
with `PYCSL-TY3-GT1`.

**Emission (Module 6).** `module6_whyml/functions.py:_param_type_str` gains one
branch: if the symbol_table value starts with `"callable:"`, `_callable_whyml_arrow`
parses the encoding and emits `(f: <w1> -> ... -> <wr>)` (a curried Why3 arrow
type). The tag→WhyML map (`_callable_tag_to_whyml`): `int`/`bool`→`int` (PyCSL
int-encodes bool), `str`→`string`, `float`→`real`, a record/variant name→its
WhyML name; an unknown bare name falls back to `int` (Why3 then rejects a
mismatched application — sound, never weaker than S1).

**Call site.** Unchanged — the existing Call lowering already emits `(f a1 ...
an)` as WhyML application; with `f` now function-typed, the application
type-checks. C4: a value postcondition on a bare callable is correctly
unprovable (`f` is opaque); refused, NOT shortcut.

**Validation (core_ir_semantic).** `_check_callable_params` is a
belt-and-suspenders well-formedness guard on the `"callable:"` encoding
(rejects a malformed encoding with `PYCSL-TY3-CALLABLE-SHAPE` so a
mis-recognition cannot silently fall through to the WhyML `int` default).

**IR shape.** No change (IR v1.4). The callable descriptor lives in the
existing `symbol_table` value slot. Byte-identical for every non-Callable
driver (the branch triggers only on `head == "Callable"`).

