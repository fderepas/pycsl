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
helper functions are emitted to enforce the division-by-zero precondition
and to realize Python's **floored** semantics.

Python `//` rounds toward −∞ and `%` takes the sign of the **divisor**;
Why3's `int.EuclideanDivision` `div`/`mod` use a non-negative remainder.
The two AGREE when the divisor is positive and DIVERGE when it is negative
(e.g. `(-7)//(-2)` is `3` in Python but `div (-7) (-2) = 4` in Euclidean).
The helpers correct Euclidean `div`/`mod` by a sign-of-divisor adjustment:
for a negative divisor with a non-zero remainder, `floordiv = div − 1` and
`floormod = mod + y`.

```whyml
  let pycsl_div (x: int) (y: int) : int
    requires { [@expl:division by zero] y <> 0 }
    ensures { result = (if mod x y <> 0 && y < 0 then div x y - 1 else div x y) }
  = if mod x y <> 0 && y < 0 then div x y - 1 else div x y

  let pycsl_mod (x: int) (y: int) : int
    requires { [@expl:modulo by zero] y <> 0 }
    ensures { result = (if mod x y <> 0 && y < 0 then mod x y + y else mod x y) }
  = if mod x y <> 0 && y < 0 then mod x y + y else mod x y
```

When `ZeroDivisionError` is declared as a raised exception, the helpers
use `raises` instead of `requires`:

```whyml
  let pycsl_div (x: int) (y: int) : int
    ensures { result = (if mod x y <> 0 && y < 0 then div x y - 1 else div x y) }
    raises { ZeroDivisionError -> y = 0 }
  = if y = 0 then raise ZeroDivisionError
    else (if mod x y <> 0 && y < 0 then div x y - 1 else div x y)
```

**Note:** In specification contexts (requires/ensures), `//` and `%`
translate to the same floored correction inline over `div`/`mod`
(operands bound once with `let`), so a body `a // b` and a contract
`\result == a // b` denote the identical floored value. `//` and `%` stay
**integer** (`int.Int`) in both operands and result.

**Implementation:** `_emit_preamble_helpers`.

#### True Division (`/`) — real, not integer (WL-02)

Python `/` is **true division** and ALWAYS returns a `float` — even on integer
operands (`5 / 2 == 2.5`). It is a DIFFERENT operator from floor division `//`
(above) and must NOT be conflated. In a body **and** in a contract, `a / b`
lowers to a **real** division: both int operands are lifted to `real` via
`real.FromInt` (`from_int`). The VALUE is NOT an exact real division (route #58):
two int LITERALS are folded to the binary64 quotient CPython computes, rendered by the
same `repr` normalization as a float literal, and every other operand shape lowers to
one uninterpreted deterministic `val function float_truediv_op (a b: int) : real`. The imports `use real.RealInfix` / `use real.FromInt` are triggered by
`IRScanner.uses_true_division` (a BinOp with IR op `"/"`; `//` is IR op `"div"`).

- **Contract (`_in_spec`):** `from_int a /. from_int b` (a `real` term;
  `from_int` is a pure logic symbol, admissible in the logical context).
- **Body:** `from_int` is a logic symbol and is not usable in a program
  (non-ghost) term, so the int→real lift and the division are bundled into one
  abstract `val`. Since ROUTE #58 that `val` is UNINTERPRETED and DETERMINISTIC —
  it no longer pins an exact real value, because doing so decided orderings the
  language answers the other way:

```whyml
  val function float_truediv_op (a b: int) : real
```

  and two INT LITERALS never reach it at all: they are FOLDED to the binary64
  quotient CPython computes, rendered by the same `repr` normalization a float
  literal uses (`5 / 2` emits `2.5`, `1 / 3` emits `0.3333333333333333`).

Because a `/` result is a `real`, using it at `int` type (e.g. `-> int` with
`#@ ensures \result == 2`) is a **real-vs-int type error** — fail-closed, never
a silent integer truncation (consistent with the int/float-mixing boundary). To
assert an integer quotient, use `//`. Both-`float` operands were already handled
by the `real` arithmetic path (`float_div_op`); this rule additionally covers
`/` on integer operands.

SMT feasibility (Alt-Ergo + Z3, no cited lemma):
`test-suite/corpus/conformance/spikes/wl02_truediv_real_spike.mlw`
(`from_int 5 /. from_int 2 = 2.5`, and the old `5/2 = 2.0` is refuted).
Regression locks: `0813.py` (POSITIVE, `5/2==2.5` at `float`; `5//2==2` guard),
`0814.py` (NEGATIVE, `# pycsl-expected: FAIL`, old int-truncation `5/2==2`).

**Implementation:** `_handle_binop` (`module6_whyml/expressions.py`),
`float_truediv_op`; import scan `IRScanner.uses_true_division`.

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
| `float` | `real` | Float literals are real constants and the ORDERINGS lower to `real.RealInfix` (`<.`/`<=.`/…), but ARITHMETIC (`+`/`-`/`*`/`/`) is UNINTERPRETED — one deterministic abstract `val function float_*_op (a b: real) : real`, spec path and body path alike. Lowering `+` to `+.` decided `0.1 + 0.2 == 0.3`, false of the program (route #53; witnesses 1117-1120). Was the unsound `int` (no-more-int Stage D) |
| `list` | `array int` | Hoare/Concurrent model (default — fixed-length, mutable, region-bearing) |
| `List[str]` / `List[float]` (FLAT, faithful non-int leaf) PARAM | `array string` / `array real` | **wrong-lowering-to-fix.md §WL-04 (FIXED) — a FLAT `List[τ]` PARAMETER whose element `τ` is a faithful NON-INT LEAF carries the faithful element type**, the one-level-up analog of the nested `array (seq τ)` model. Module5 `_m5_get_list_flat_elem_whyml` maps `List[str]`→`string` / `List[float]`→`real` into the IR field `param_list_flat_elem`; Module6 `_param_type_str` emits `array {τ}` (right after the nested `_list_nested_elem` branch). The subscript READ is UNCHANGED (`Array.get` is element-polymorphic), so `a[i] : string`/`: real` matches a str/float return and `\result == a[i]` is provable. A flat `List[int]`/`List[bool]` has NO entry (→ byte-identical `array int`; int-leaf is the τ-blessed default), and a nested `List[<container>]` is owned by `_m5_get_list_nested_elem_whyml` (→ `array (seq τ)`). Drivers `getting-better/wrong-lowering/wl04_list_{str,float}_elem_COLLAPSED.py` (PROVEN); Gate-B spike `test-suite/corpus/conformance/spikes/wl04_list_flat_elem_spike.mlw` (Alt-Ergo AND Z3); reference locks 0817/0818 (POSITIVE), NEGATIVE 0819. **Boundary:** the LOCAL / RETURN LIST-LITERAL construction is now covered by §WL-04a (next row); `List[<record>]` flat element is a follow-on. |
| `List[str]` / `List[float]` (FLAT) LOCAL / RETURN built by a LIST LITERAL | `array string` / `array real` | **wrong-lowering-to-fix.md §WL-04a (FIXED) — the CONSTRUCTION analog of the flat param row.** A list literal (`a = ["x", "y"]`, `return ["a", "b"]`, `return [1.5, 2.5]`) whose elements are ALL string literals (resp. ALL float `Number`s) is built at the faithful element type: `module6_whyml/expressions.py::_expr_to_whyml` (`ArrayLitExpr` arm) emits `(let _alit = Array.make n e0 in _alit[i] <- ei; …; _alit)` with the REAL string/real element values — NOT the `_coerce_to_int` hashing (`Array.make n 747471683`) / truncation. The indexed-read constant-fold (`types.py::_track_collection_metadata`) folds a pure-float literal to the faithful real (`a[1]`→`2.5`, not the int-truncated `2`). A `-> List[float]` return annotation resolves to `array real` (Module5 `_m5_get_list_flat_elem_whyml` return fallback → `functions.py::_compute_return_type` `array real` arm; `-> List[str]`→`array string` already existed), and a contract `\result[i]` on ANY `array τ` return lowers to a native `Array.get` (`_handle_subscript` L0, widened from `array int`-only). An all-`int`/`bool` literal stays `array int` BYTE-IDENTICAL; a MIXED (`[1, "x"]`/`[1, 2.5]`/`[1, Point(2,3)]`) literal is REJECTED fail-closed (§WL-04g below — no faithful `array τ` element type). Drivers `getting-better/wrong-lowering/wl04a_list_literal_*.py` (PROVEN); Gate-B spike `test-suite/corpus/conformance/spikes/wl04a_list_literal_elem_spike.mlw` (Alt-Ergo AND Z3); reference locks 0826/0827 (POSITIVE), NEGATIVE 0828. |
| `List[<record>]` (FLAT, record leaf) PARAM / RETURN | `array <record>` (record PURE) | **wrong-lowering-to-fix.md §WL-04b (FIXED) — the RECORD-leaf analog of the flat str/float param row.** A flat `List[R]` PARAMETER (and pass-through RETURN) whose element `R` is a KNOWN record — a user `@dataclass`/`NamedTuple` class OR a recognized `Tuple[T1, …, Tn]` (WL-03's synthesized per-slot record `pytuple_<tags>`) — carries the faithful element record, so `a[i]` reads a REAL record and `a[i].field` / `a[i][k]` projects the faithful field (was the collapsed `array int` with an opaque `get_field`/`subscript_get` element read). Threading: Module5 `_m5_get_list_record_elem` maps the `List[R]` element to the record CLASS NAME into `param_list_flat_elem` (using the pre-collected `_m5_record_class_names` + `_m5_tuple_slot_tags`), and subtracts a record-list param from the 2-D `matrix int` detection (so `a[i][1]` on a `List[Tuple[…]]` is a slot read, not a matrix cell); Module6 `_param_type_str` resolves the record via `_record_types` → `array <whyml>` + registers `_record_array_params`; `_handle_attribute_expr` lowers `a[i].field` to `(let _rec_ = a[i] in _rec_.<label>)`, `_namedtuple_positional_access` lowers `a[i][k]`, `_compute_return_type` resolves a `-> List[R]` return. **Why3 forbids a MUTABLE element inside `array`** (SMT-established, same constraint as the nested `array (seq τ)` model), so a record used as a `List[<record>]` element is emitted **PURE** (immutable fields — Module5 `list_element_record_types` drives the preamble `mutable`-drop; byte-identical for every record NOT so used). Tuples/NamedTuples are immutable; a `List[<dataclass>]` reads its fields only — a field-mutated dataclass-in-a-list fails CLOSED at Why3 type-check (never a silent unsound update). The projection COMPREHENSION `[p.x for p in a]` over a record source is lowered NATIVELY too (`list_content_comp` `src: array <record>`, `result[i] = (src[i]).x`), so 0769/0770 prove via the same `(a[i]).x` as the contract (false twin 0771 stays UNPROVEN). Drivers `getting-better/wrong-lowering/wl04b_list_{record,tuple}_elem_COLLAPSED.py` (PROVEN), `wl04b_list_record_falsetwin.py` (UNPROVEN); Gate-B spike `test-suite/corpus/conformance/spikes/wl04b_list_record_elem_spike.mlw` (Alt-Ergo AND Z3, no cited lemma); reference locks 0829 (POSITIVE `List[<dataclass>]`), 0830 (POSITIVE `List[Tuple[int,str]]`), NEGATIVE 0831. **Boundary:** the `List[<record>]` LITERAL is now covered by §WL-04c (next row); a FILTERED projection comprehension over a record source by §WL-04d; a `List[<plain-class-with-__init__>]` element by §WL-04e; a `float` record slot is now the faithful `real` by §WL-03b; a record slot of CONTAINER type keeps the prior (int-collapse / opaque) model (documented residual). |
| `List[<record>]` (FLAT, record leaf) LOCAL / RETURN built by a LIST LITERAL | `array <record>` (record PURE) | **wrong-lowering-to-fix.md §WL-04c (FIXED) — the CONSTRUCTION analog of the flat record param row.** A list literal whose elements are ALL full-arity positional constructor CALLS to the SAME CONTENT-FAITHFUL record (`a = [Point(1, 2), Point(3, 4)]`, `return [Point(1, 2), Point(3, 4)]`) builds `array <record>` with each element the FAITHFUL record literal (`{ x = 1; y = 2 }` — the ctor args threaded via `_call_record_constructor`) — NOT the `_coerce_to_int` collapse. `expressions.py::_expr_to_whyml` (`ArrayLitExpr` arm), gated by `_record_ctor_list_elem`, emits `(let _alit = Array.make n {…} in _alit[i] <- {…}; …; _alit)`; `types.py::_track_collection_metadata` registers the local in `_record_array_locals`, so `a[i].field` (local) and `\result[i].field` (on a `-> List[R]` return, `_func_return_type == "array <record>"`) project the real field via the same `(let _rec_ = … in _rec_.<label>)` path as §WL-04b (`_handle_attribute_expr` extended to the record-array local + the `\result[i]` subscript base; `_namedtuple_positional_access` extended to the record-array local). The element record is emitted PURE (Module5 `_m5_list_literal_record_elem`, computed AFTER `generic_visit` so class-based NamedTuples are populated, adds it to `list_element_record_types`). **FAITHFUL CONSTRUCTION IS REQUIRED:** only a record whose constructor sets EVERY field from a positional param (`NamedTuple` / recognized `Tuple` / explicit-`__init__` positional class / — **since §WL-07** — a `@dataclass`) is threaded. **UPDATE (§WL-07):** the `@dataclass`-ctor arg-drop that formerly kept a `@dataclass`-literal element fail-closed is FIXED — a `@dataclass` now synthesizes its `init_params`/`init_body`, so its literal `[Point(1, 2)]` is content-faithful (`a[0].x == 1` PROVES; driver `wl07_dataclass_literal_TRUE.py`). Drivers `getting-better/wrong-lowering/wl04c_list_record_literal_COLLAPSED.py` (PROVEN), `wl04c_list_record_literal_falsetwin.py` (UNPROVEN); Gate-B spike `test-suite/corpus/conformance/spikes/wl04c_list_record_literal_spike.mlw` (Alt-Ergo AND Z3, no cited lemma); reference locks 0839 (POSITIVE local + return), NEGATIVE 0840. **Boundary:** a MIXED-record literal keeps the fail-closed (int-collapse / opaque / TYPEERR) model. |
| `[p.x for p in a if <cond(p)>]` (FILTERED projection over `List[<record>]`) | `array int` (length BOUND + membership/predicate/projection existential) | **wrong-lowering-to-fix.md §WL-04d (FIXED) — a FILTERED projection comprehension over the flat `array <record>` source of §WL-04b.** Previously fell through `_content_comp`'s record branch to the opaque `val list_comp (x:int):int`, so a `-> List[int]` return (`array int`) was returned an int → ill-typed WhyML (TYPEERR — fail-closed but unusable). The RESULT LENGTH is data-dependent (`0 <= len(result) <= len(a)`), so NO exact length / per-index content law is provable (claiming either would be UNSOUND). The sound faithful law (`expressions.py::_filter_record_proj_law`, a per-instance `list_content_comp_<n>` val) is the length BOUND `Array.length result <= Array.length src` PLUS a membership+predicate+projection existential: `forall i. 0<=i<len result -> exists j. 0<=j<len src /\ (let p = src[j] in <cond> /\ result[i] = <p.field>)`. Every output came from some retained input (Python semantics), an honest under-approximation (the source index is lost to compaction). From it the FILTER CONSEQUENCE transfers to the projected result whenever the predicate constrains the projected field (`[p.x for p in a if p.x > 0]` yields only positive elements). The element and predicate are lowered NATIVELY over the record binder (`(src[j]).field`, via `_push_quant_binder` + `_comp_cond_pure_bool` extended with the `getters` accumulator for record-field predicates), the SAME projection a driver's `\result[i]` / `a[j].x` lowers to — sound, no new axiom (definitional `ensures`; Array read law is Why3 stdlib). A predicate that does NOT lift to a pure-bool term over the target keeps the SOUND length-bound-only law (still `array int` — never the prior TYPEERR). Drivers `getting-better/wrong-lowering/wl04d_filtered_record_proj_COLLAPSED.py` (PROVEN), `wl04d_filtered_record_proj_falsetwin.py` (UNPROVEN); Gate-B spike `test-suite/corpus/conformance/spikes/wl04d_filtered_record_proj_spike.mlw` (Alt-Ergo AND Z3, no cited lemma; the length-EQUALITY / per-index-content false twins NOT entailed); reference locks 0841 (POSITIVE), NEGATIVE 0842. **Boundary:** a FILTERED TUPLE-SLOT projection (`[t[0] for t in a if …]`, the element is a subscript not an attribute) and a non-pure-int projection element keep the opaque / length-bound-only model. |
| `List[<plain-class-with-__init__>]` (FLAT, record leaf) PARAM / RETURN | `array <record>` (record PURE) | **wrong-lowering-to-fix.md §WL-04e (FIXED) — extends §WL-04b's recognized-element set to a PLAIN class.** A flat `List[Point]` where `Point` is a PLAIN class with an explicit positional `__init__` (`def __init__(self, x, y): self.x = x; self.y = y`) — NOT a `@dataclass`/`NamedTuple`/recognized `Tuple` — was NOT recognized as a list-element record, so it collapsed to `array int` with the opaque `get_x` element read. Such a class is ALREADY emitted as a record `type_decl` by `visit_ClassDef` and its constructor is CONTENT-FAITHFUL (`Point(1, 2).x` proves `== 1`, not `== 0`), so it now resolves to `array <record>` exactly like §WL-04b: `a[i]` reads a REAL `point`, `a[i].field` projects the faithful field (`(let _rec_ = a[i] in _rec_.<label>)`), and a constructed record STORED into the array element (`a[0] = Point(5, 6)` → the faithful `{ x = 5; y = 6 }`, §WL-04c ctor threading) reads its written field back. Threading is a SINGLE recognition seam: `_m5_is_plain_positional_record_class` (a pre-`generic_visit` scan of `node.body`, mirroring the dataclass/NamedTuple pre-scan) adds the class name to `_m5_record_class_names`, so the UNCHANGED §WL-04b `_m5_get_list_record_elem` → `_param_type_str` → `array <record>` → `_record_array_params` path applies. Recognition is FAITHFUL-ONLY: a plain `__init__` whose ANY `self.<attr>` is set from a non-positional-param expression (constant / computation / keyword-only param) is REJECTED (kept at the `array int` collapse — fail-closed). The element record is emitted PURE (`list_element_record_types`); a field-mutated plain-class-in-a-list has the SAME fail-closed posture as §WL-04b (byte-identical to the `@dataclass` path — the element write is dropped, the post-mutation claim UNPROVEN). ADDITIVE: a plain class NOT used as a flat `List[R]` element never reaches `_m5_get_list_record_elem`, so a bigger recognition set changes NOTHING unless a `List[<plain-class>]` annotation exists (full-corpus byte-diff = 0). Drivers `getting-better/wrong-lowering/wl04e_list_plainclass_elem_COLLAPSED.py` (PROVEN — read law + store-read-back), `wl04e_list_plainclass_elem_falsetwin.py` (UNPROVEN); Gate-B spike `test-suite/corpus/conformance/spikes/wl04e_list_plainclass_elem_spike.mlw` (Alt-Ergo AND Z3, no cited lemma); reference locks 0843 (POSITIVE), NEGATIVE 0844. **Boundary:** a plain-`__init__` class whose ctor is NOT purely positional keeps the prior model; a `float` record slot is now the faithful `real` (§WL-03b next row); a record slot of CONTAINER type keeps the prior (int-collapse / opaque) model. |
| `float` record/tuple FIELD SLOT | `real` field | **wrong-lowering-to-fix.md §WL-03b (FIXED) — a `float` field slot is the faithful Why3 `real`, not the int collapse.** The WL-03 synthesized per-slot record and the §WL-04b `List[<record>]` element/record models recognized slot/field types int/bool/str ONLY, so a `float` field slot collapsed to `int` — an UNSOUND leak that truncated a fractional read (`t[1]` of a `Tuple[int, float]`, `q.f` / `a[i].f` of a `@dataclass`/`self.f: float` record, holding `2.5`, read `2`). WL-03b realizes it as `real` (τ(float)=real, no-more-int Stage D): Module5 `_M5_TUPLE_SLOT_TAGS` maps `float`→`real` (so `Tuple[int, float]` synthesizes `pytuple_int_real = { field0: int; field1: real }`) and `_field_type_from_annotation` maps a `float`-annotated field to the `real` tag; the preamble record emitter maps that tag to a `real` field (`_build_witness_str` gets a `0.0` real witness). The projection `t[1]` / `q.f` / `a[i].f` reads a `real`; the float comparison routes through Why3 `real` equality (a `2.5` literal on either side drives the real `=`). Because `real` is a PURE type, a record with a `real` field is legal at an `array` element position — the §WL-04b PURE-element constraint is preserved. A float field read used where an int is expected stays a fail-closed real-vs-int TYPEERR (never a silent truncation). Drivers `getting-better/wrong-lowering/wl03b_float_record_slot_COLLAPSED.py` (PROVEN — tuple slot + plain record field + `List[R]` element), `wl03b_float_record_slot_falsetwin.py` (UNPROVEN — the int-truncation `== 2.0` claim); Gate-B spike `test-suite/corpus/conformance/spikes/wl03b_float_record_slot_spike.mlw` (7 goals Valid on Alt-Ergo AND Z3, no cited lemma); reference locks 0845 (POSITIVE), NEGATIVE 0846. ADDITIVE: the corpus has no `float` record/tuple field, so the full-corpus byte-diff is 0. **Boundary:** a record slot of CONTAINER type (`Point` with a `List[int]` field) — a mutable container nested in a record nested in an `array` hits the Why3 mutable-element and `array (array τ)` type-rejection (the nested-list boundary); a sound pure-`seq`/`map` field representation is future work. |
| MIXED / heterogeneous list literal (`[1, "x"]`, `[1, 2.5]`, `[1, Point(2,3)]`) | REJECTED (fail-closed `PyCSLSemanticError`) | **wrong-lowering-to-fix.md §WL-04g (DOCUMENTED SOUND BOUNDARY) — a heterogeneous list literal has NO faithful `array τ` element type: a Python list is heterogeneous but a WhyML `array` is HOMOGENEOUS.** Every UNIFORM shape is already claimed by an earlier row (all-int/bool `array int`; all-str/all-float §WL-04a; all-equal-arity-tuple `array (t0,…)`; all-record §WL-04c); so a NON-int-faithful element (a `str` literal, a `float` `Number`, a `Tuple`, or a known-record constructor `Call`) surviving to the int-coercion FALLBACK PROVES the literal is mixed. The int-coercion default is UNSOUND on it: a `str` element HASHES to a WELL-TYPED int (`[1, "x"]` emitted `array int` with `a[1] = 976090257` under `PYTHONHASHSEED=0`, so the contract `\result == 976090257` on `a[1]` PROVED — a claim FALSE of real Python where `a[1]` is the STRING `"x"`: this was a SEVERITY-1 UNSOUNDNESS, now fixed), while a `float`/record element ill-typed the `array int` (silent Why3 TYPEERR / broken emission). The FIX (`module6_whyml/expressions.py::_mixed_literal_reject_kind`, called from the `ArrayLitExpr` fallback) FAILS CLOSED: it raises a clear `PyCSLSemanticError` naming the offending element kind and pointing the user at a homogeneous list, a `Tuple` (fixed-arity heterogeneous slots), or a record/`@dataclass` (heterogeneous fields). A HOMOGENEOUS all-int/bool/expression literal is NOT flagged (stays `array int`, byte-identical). A future faithful model would require a heterogeneous-sum element type (a Why3 variant over the element categories) — well beyond the homogeneous `array` model. Drivers `getting-better/wrong-lowering/wl04g_mixed_int_{str,float,record}_falsetwin.py` (all REJECTED — the false content claim NEVER proves), `wl04g_mixed_int_str_UNSOUND.py` (was PROVEN pre-fix, now REJECTED), `wl04g_homogeneous_int_POSITIVE.py` (PROVEN — no over-rejection); boundary spike `test-suite/corpus/conformance/spikes/wl04g_mixed_literal_boundary_spike.mlw` (the sound homogeneous `array int` Valid on Alt-Ergo AND Z3; the mixed-float array Why3 TYPE-rejected — the boundary witness); reference locks 0850 (POSITIVE homogeneous), NEGATIVE 0851 (int+str, the headline soundness lock), 0852 (int+float), 0853 (int+record). Full-corpus byte-diff = 0 (no corpus program is a mixed literal). |
| `List[List[τ]]` (NESTED, read-only) | `array (seq τ)` | **nested-list.md — a list whose element is itself a container carries its FAITHFUL nested type, recursively (`_m5_annotation_to_whyml_type`).** The OUTER list stays `array` (byte-identical to a flat `List[τ] = array τ`; `len(a)`/`a[i]`/outer whole-row reassignment `a[i]=row` unchanged); the INNER collection is a **PURE** Why3 type — `seq τ` for `List`, `map κ (option ν)` for `Dict[K,V]`, `map (…) (option int)` for `Set`. Pure is MANDATORY: Why3 forbids a mutable element inside `array` (`array (array τ)` is type-rejected; Gate-B spike `test-suite/corpus/conformance/spikes/nested-list.mlw`). So `a[i]` is a real `seq`/`map`, `a[i][j]`→`Seq.get (a[i]) j`, `a[i][key]`→`Map.get (a[i]) key`, `len(a[i])`→`Seq.length (a[i])`, and the subscript-projection comprehension `[x[k] for x in a]` is content-faithful (`result[i] = Seq.get (a[i]) k`). Drivers 0797–0800; NEGATIVE 0801 (false content). **DEEPER nesting (nested-list.md §8/§9 EXTENSION):** the subscript READ composes RECURSIVELY to the depth bound — `a[i][j][k]`→`Seq.get (Seq.get (a[i]) j) k`, `len(a[i][j])`→`Seq.length` — via `_nested_access_type` (peel one container level per index level), for `List[List[List[τ]]]` ~ `array (seq (seq τ))` up to depth 4 (driver 0805 depth-3, depth-4 in Gate-B spike `nested-list-deep.mlw`; NEGATIVE 0806; a depth-5 read is beyond the cap → opaque/rejected, driver 0807). A **TARGET-DEPENDENT** comprehension index `[x[f(x)] for x in a]` where `f(x)` lifts to a pure int term over `len(x)` (e.g. `x[len(x)-1]`) is ALSO content-faithful — `result[i] = Seq.get (a[i]) (Seq.length (a[i]) - 1)` (`_lift_target_seq_index`; driver 0808, NEGATIVE 0809). An index that does NOT so lift (a `g(x)` call over the seq) stays opaque. Depth-bounded (≤4); an unknown/too-deep leaf keeps the scalar `int` default (documented residual). Un-annotated/bare-`list` nested params stay `array int` (never a false nested claim). |
| `List[List[int]]` (NESTED, in-place inner-mutated) | `matrix int` | **nested-list-mutable.md — in-place inner ELEMENT mutation.** A `List[List[int]]` param that the body IN-PLACE INNER-MUTATES (`a[i][j] = v`, an `ArraySet` with a `Subscript` array — Module5 `_collect_inner_mutated_params`) CANNOT use the read-only `array (seq int)` model (its inner `seq` is a PURE/immutable Why3 value). A **usage/mutation analysis** routes it instead to the MUTABLE built-in Why3 **`matrix int`** (the two representations COEXIST — selected per-param by whether the body inner-mutates it; read-only nested lists stay ragged-capable on `array (seq τ)`). Lowering: `a[i][j]=v`→`Matrix.set a i j v`, `a[i][j]`→`Matrix.get a i j`, `len(a)`→`a.rows`, `len(a[i])`→`a.columns`. The update reads back (`(set a i j v; get a i j)=v`) and is NON-ALIASING (a distinct cell is unchanged) — Gate-B spike `test-suite/corpus/conformance/spikes/nested-list-mutable.mlw`, Valid in Alt-Ergo AND Z3. Drivers 0802 (read-back), 0803 (non-aliasing). No new axiom (Matrix get/set/frame laws are Why3 stdlib `matrix.Matrix`). **RECTANGULAR** (uniform `columns`) + **int-leaf** only. A NON-int-leaf inner mutation (`List[List[str]]`/`List[List[float]]`) is now covered by §WL-04f (next row); `a[i].append(..)` (shape-change) stays OPAQUE (`append_1` no-op — no false post-state claim); ragged in-place mutation is out of the rectangular `matrix` model (UB catalog). Un-annotated/bare-`list` `\length2d`-contract params also use `matrix int` (rectangular 2-D, 0018/0019). |
| `List[List[str]]` / `List[List[float]]` (NESTED, in-place inner-mutated, NON-int leaf) | `array (seq string)` / `array (seq real)` | **wrong-lowering-to-fix.md §WL-04f (nested-inner-mutation) — the NON-int-leaf twin of the `matrix int` row.** An inner-mutated nested list whose leaf is a faithful NON-int type (`string`/`real`) has NO mutable 2-D built-in, but the OUTER `array` IS mutable, so `a[i][j] = v` lowers to an OUTER-array store of a **functionally-updated inner seq** (option c): `a[i] <- Seq.set a[i] j v` (Module6 `_handle_array_set_stmt`, guarded on a `seq `-leaf `_list_nested_elem` param + non-String indices). The inner `seq` stays PURE/immutable (`array (array τ)` is Why3 TYPE-rejected). Reads are UNCHANGED (`a[i][j]`→`Seq.get a[i] j`); `Seq.set`'s `requires 0 <= j < length` is the IndexError obligation. The update reads back (`(a[i]<-Seq.set a[i] j v; Seq.get a[i] j)=v`), and outer/inner frame + dims are preserved — Gate-B spike `test-suite/corpus/conformance/spikes/nested-list-inner-mutable-seq.mlw`, Valid in Alt-Ergo AND Z3 (false twin unproven). No new axiom (Seq/Array laws are Why3 stdlib). **SOUND under aliasing:** the value-semantics store diverges from Python's in-place reference mutation ONLY under inner aliasing, which is UNEXPRESSIBLE in PyCSL — an inner list can be neither bound to a local (`b = a[i]` type-fails: a local defaults to `int`) nor shared across outer slots (`a = [row, row]` type-fails: `array (array τ)` is rejected) — so every expressible post-state is faithful and caller-visibility matches (the native `array` store is a `writes {a}` effect). Drivers 0804 (str read-back), 0847 (float read-back + non-aliasing); NEGATIVE 0848 (false twin — post cell `!= v`, stays UNPROVEN). **Boundary:** the `seq int` leaf routes to `matrix int` (previous row, not here); a **MAP leaf** (`List[Dict[int,int]]` ~ `array (map int (option int))`) inner item write `a[i][k]=v` is REJECTED (fail-closed TYPEERR — the map analog `a[i] <- map_update a[i] k (Some v)` is an unspiked follow-on; NEGATIVE 0849); `a[i].append(..)` shape-change and ragged mutation stay OPAQUE/out-of-model as above. |
| `list` (grown) | `ref (seq int)` | **07-1705-rev4: a list that is *grown* (`+=` / `+` concat) is modelled as a growable immutable `seq.Seq` value in a region-free ref** — `array.Array` is fixed-length and cannot be rebound (Why3 region rule, `07-1732-findings.md`). Init `[…]`→`Seq.cons` chain; `+=`→`a := !a ++ snapshot(b)` (length-additive + element-preserving, **provable**); `len`→`Seq.length`, `a[i]`→`Seq.get`. A grown PARAM is shadowed at entry `let a = ref (snapshot a)`; `return a` materialises back to `array int` (`materialize`, a fresh array). The seq-promotion analysis (Module5 `seq_promoted_vars`) selects these; `Seq.*` is emitted only in body context (a contract uses the array entry value). Supersedes the old effect-opaque `array_extend` |
| `list` | `loc` + `_len` | Typed/Store model |
| `dict` / `set` / `frozenset` | `map κ (option ν)` | Parametric map (no-more-int A1): κ ∈ {`int`, `string`}, and the value type **ν ∈ {`int`, `string`, `seq int`, nested `map …`}**, where — `int` (the default), `string` (str-valued dict), `seq int` (list-valued dict, **immutable seq snapshot** — no mutate-through-alias; A1-residual, driver 0543), and a nested `map …` (dict-of-dict, double subscript). Default `map int (option int)`. `set`/`frozenset` use the same model (value ignored). **κ = string ⇒ `map string (option ν)` with the NATIVE, injective Why3 string key** (`String.(=)`, no `str_hash_op`), so distinct keys are provably non-aliasing (cleared-hash.md, drivers 0755–0758 locals, 0772–0776 record fields). κ = string is inferred for a `Dict[str, _]` param/AnnAssign local, a string-key literal (`{"a": …}`), string-key USAGE (`d[k]`/`k in d`/`d.get(k)` with a string literal or `str`-typed key), a string CONCATENATION key `d[a + b]` (both operands `str`; `str_concat_op` pinned to left-cancellative Why3 `concat`, so `a != c ⇒ d[a+b]` non-aliasing proves — cleared-hash.md residual-close 1a, driver 0795) — Module5 `_build_function_symbol_table` — AND a record FIELD declared `Dict[str, ν]`/`Set[str]`/`FrozenSet[str]` (cleared-hash.md S4: `field_key_types` on the record type flips the field map to `map string`; every field op site — store `self.d[k]=v`, subscript `self.d[k]`, `.get`, membership `k in self.d`, set `.add`/`.discard` — reads/writes the raw native string key in lockstep). **Residual κ-unknown (CLOSED honest boundary):** a dict/set whose key the model cannot pin to a decidable/injective string (an un-annotated field from `{}`, a non-`str` key, or a derived-string key like `s.upper()`) keeps the legacy `map int` + opaque `str_hash_op` fallback — NOT collision-sound: a distinct-key non-aliasing claim on it stays UNPROVABLE (driver 0796, `# pycsl-expected: FAIL`), NO false injectivity axiom on `str_hash_op` (`proof_axiom_allowlist` unchanged). Non-dict-key hashing (`hash(s)` 0485, decode-equality 0425) is a SEPARATE out-of-scope opacity. Implementation: the ν ladder is consolidated into three helpers `_dv_empty_default`/`_dv_missing_default`/`_dv_store_value` in `module6_whyml/expressions.py` (refactor F1) |
| module-level constant `Dict[str,str]` `.get(k, default)` | chained `string` if-then-else | **module-const-dict-get — a MODULE-LEVEL constant str→str dict literal read via `.get(k, default)` folds to a faithful chained string-valued if-then-else.** A top-level `OP_MAP = {"==":"=", "!=":"<>", …}` (all keys AND values plain string literals, bound EXACTLY once, not `#@ shared`/`global`) is collected by `frontend/module_collect.py::collect_module_const_dicts` into the IR field `module_const_dicts` (parallel to `module_constants`; str→str shape, source order preserved). At a `NAME.get(k, default)` reflection site (`module6_whyml/expressions.py::_lower_dict_get_call`) it lowers to `(if k = "==" then "=" else if k = "!=" then "<>" else … else default)` — string equality bridges through the abstract `str_eq_op` in a body (native `=` on strings is program-illegal) / polymorphic `=` in a spec; the mapped values and default are real Why3 `string` literals (`whyml_string_literal`). This is the exact `OP_MAP.get(op, op)` shape in `identifiers.op_translate`, whose string arg previously LEAKED to an opaque int `val` (the self-tcb-reduction target's sole missing feature). The result is `string`-typed: used where an int is expected it fails closed at Why3 type-check (WL-02 — never a silent value→int coercion). **Requires an EXPLICIT default (2 args)**; a same-named local/param SHADOWS the module constant (checked first). Reference locks 0872 (POSITIVE — hit + default), NEGATIVE 0873 (wrong-value twin); Gate-B spike `test-suite/corpus/conformance/spikes/modconstdict_get_spike.mlw` (Z3 discharges every hit + default and refutes both false twins; best-of-N pipeline SUCCESS). **Boundary / fail-closed residuals:** a non-str→str dict (any non-string key or value), `.get(k)` WITHOUT a default (None-returning), an empty dict, a reassigned name, and a non-literal / class-level dict all keep the current opaque behavior (never a false value). No new axiom (`str_eq_op` is the pre-existing string-equality bridge); no `\trusted`. **Alt-Ergo note:** the fall-through arms need string-literal DISEQUALITY, which Alt-Ergo (no string theory) cannot decide — Z3's native string theory discharges them, and the best-of-N pipeline is sound either way (both provers refute the false twin). |
| `tuple` | `int` (hash) | **Intentional benign collapse (A7).** A bare tuple value hashes to an `int`; element types are NOT modeled. Rare and benign — a future tuple track would lift this, but no driver demands it. (Ghost tuples `\mk_tuple`/`\fst`/`\snd` in *contracts* are modeled faithfully — §T.6.) |
| `None` / `-> None` | `unit` | Return type for void functions |
| Class `C` | Record type `c` | Lowercase name. Covers `self`, `C()` locals, **and** a registered `C`-typed parameter. Field READS project directly (Track 3). A field STORE `p.f = v` on a MUTABLE record param/local is caller-visible (wrong-lowering-to-fix.md §WL-05d: lowers to `p.f <- v`, Why3 infers `writes {p.f}`); a record pinned PURE because it is a `List[<record>]` element is field-immutable, so such a store FAILS CLOSED. |
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

**Divergence is carried to every call site (route #269).** A call that Module 6 lowers to
a bodyless `val` stub would otherwise TERMINATE for Why3 and give a caller its termination
for free. `pycsl.py::_run_pipeline` therefore post-processes the emission: (1) every plain
program `val` whose name is a stub spelling `<...>_<m>_<arity>[_c<h>][_<k>]` of a
`\diverges` function or method `m` of the unit carries `diverges`, whichever producer minted
it (`self.m()`, `obj.m()`, `C().m()`, `super().m()`, `C.m()`, the fixed Module 5 dispatcher
stub `self__py_expr_to_ir_1`); matching is by name, so an ambiguous match makes more callers
owe `\diverges`, never fewer. Logic `val function`/`predicate`/`ghost`/`constant` symbols are
model operations, not call stubs, and are untouched. (2) An emitted `let`/`with` of a
`\diverges` function always carries `diverges`, even when a bespoke scaffold wrote its header.
(3) A call to a `\diverges` callee that VANISHES from the emission (an opaque comprehension,
generator or lambda lowering) is represented by an application of the opaque
`val pycsl_opaque_call_diverges (_u: unit) : unit diverges` at the head of the caller's body,
so a caller not declared `\diverges` fails its termination VC and an honestly declared one
type-checks. A vanished call to a callee that may RAISE (declared `raises`, or an escaping
`raise`, transitively) or that carries a non-trivial `requires` (never checked at a vanished
call) is refused (`PYCSL-SEM-VANISHED-CALL-EFFECT`).

**Vanished writes (route #274).** The same refusal covers a call, in such a position (the
eager first iterable of a generator included), to a callee with a FRAME — a declared `assigns`
other than `\nothing`, or, frame undeclared, a body that writes a field/element/slice, deletes
an element or calls a collection mutator on anything but a fresh local container (closed
transitively) — and any receiver mutator (`out.append(y)`). It is excused only when the
function's own emitted blocks apply the callee at least as many times as its IR calls it (a
bespoke concrete comprehension lowering such as the Module 5 mirror's `_cc_<k>` loops): one
visible application does not cover a second, vanished write. A callee emitted only as `val`s
without `writes` has no modelled effect to lose.

**Definition-time evaluation (route #273).** A nested `def`/`lambda`/`class` inside a lowered
function is lifted (or lowered to a `Lambda` node) WITHOUT the expressions CPython evaluates
when the statement runs: defaults, decorators, annotations, class bases and class-body
statements. They are therefore restricted (`PYCSL-SEM-DEF-TIME-EVALUATION`): defaults must be
literals, bare names, signed numeric literals or displays of those; decorators (dotted) names;
annotations and bases type-shaped; a nested class body only defs, nested classes, `pass`,
docstrings and name bindings of literals. Module-level definitions (import time) are outside
the rule. A bare-name default is admitted only when the name is never rebound in the enclosing
function nor declared `global` / `nonlocal` (route #340, §T.6.37): its def-time value is then
its call-time value.

**Recursion and `no_exception \all` (scope).** `\all` is the Phase-1 set
`exception_model.KNOWN_EXCEPTIONS`; RecursionError is not in it and the interpreter's
recursion limit is not modelled. A TERMINATING recursion (`\variant`) under `no_exception \all`
is therefore proved without regard to the recursion depth — a deep enough call still raises
RecursionError in CPython; that is outside the claim. A `\diverges` function declaring
`no_exception \all` that REACHES a call-graph cycle (itself included) is refused
(`PYCSL-SEM-DIVERGES-NO-EXCEPTION-RECURSION`): an unbounded Python recursion does not run
forever, it raises RecursionError, so the claim would hold of the model only.

**Cross-module cycles.** An imported function is a trusted stub in the importer, and the
importer is a stub in the dependency's verification, so a cycle through the module boundary
would be assumed circularly on both sides. The route #263 call graph reads an imported
function's body (kept by `ir_resolve`) for calls back into module-level functions of the
importing unit; a cycle through an imported stub is refused (`PYCSL-SEM-CROSS-MODULE-RECURSION`)
unless every member is `\diverges`. Residual: a cycle that leaves through an imported CLASS's
method (a receiver of an imported type) is not tracked.

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
initialised by, in priority order: (1) a **parametrized override** — if the field's
`__init__` initialiser is a flat top-level `self.f = <expr over the params>`, the actual
args are substituted into that expression (`Module5._collect_init_construction` captures
the param list + initialiser IR; `expressions.py::_call_record_constructor` splices the
lowered args via a `RawWhyml` IR node and `_subst_params`); (2) otherwise the field's
**type-correct default** — `Array.make <len> 0` for a list/array field (length from
`_array_init_size`), the empty `map` for dict/set, or the captured int constant (fallback
`0`). So `Point(2,3)` with `self.x=a; self.y=a+b` lowers to `{ x = 2; y = (2 + 3) }`.
*Scope:* only scalar (int) fields take a substituted value; list/dict fields,
non-param-dependent inits, and inits with control flow / method calls / `*args` keep the
default witness (sound, less precise).

**`@dataclass` positional/keyword binding (`wrong-lowering-to-fix.md` §WL-07 — a fixed
severity-1 unsoundness).** A `@dataclass` with **no explicit `__init__`** has its
constructor *synthesized* by Python — `__init__(self, f1, …, fn)` binds each declared
field from the same-position positional arg, in field-DECLARATION order. Previously
`_collect_init_construction` only walked an explicit `__init__`, so a `@dataclass` got
**empty** `init_params`/`init_body` and *every* field fell to its zero default: `Point(1,
2)` emitted `{ x = 0; y = 0 }` and `Point(1, 2).x == 0` **PROVED** — a claim FALSE of real
Python (`.x` is `1`, fail-OPEN). It now synthesizes the dataclass ctor's
`init_params`/`init_body` (the class-body AnnAssign fields in declaration order,
`self.f = f`), mirroring the NamedTuple record path, so the args are threaded exactly like
a NamedTuple / recognized `Tuple` / explicit-`__init__` positional class. Binding is by
**positional prefix** (`len(args) <= len(init_params)`): a full call binds every field, a
PARTIAL call binds the provided prefix and leaves each trailing field at its declared
default (Python's default semantics — `Box(7)` with `h: int = 5` → `{ w = 7; h = 5 }`), an
over-arity call binds nothing (fail-closed). **Keyword args** (`Point(x=1, y=2)`,
`Point(1, y=2)`) — previously DROPPED from the Call IR entirely (a pre-existing fail-OPEN
hole for **every** record constructor, plain classes too) — are now captured in
`CallExpr.keywords` (`ir_schema.py`, gated on non-empty → byte-identical wire dict for a
keyword-free call) and bound BY NAME on top of the positional prefix. A `**kwargs` splat
(`kw.arg is None`) is NOT captured → the field keeps its default (a documented fail-open
residual: a splat's runtime values are unknown, so no faithful per-field claim is made —
prefer explicit positional/keyword construction). This LIFTS §WL-04c's dataclass-literal
fail-close: a `[Point(1, 2)]` `@dataclass` literal is now content-faithful (`a[0].x == 1`
PROVES). SMT spike `test-suite/corpus/conformance/spikes/wl07_dataclass_ctor_spike.mlw`
(Alt-Ergo AND Z3, no cited lemma); drivers `getting-better/wrong-lowering/wl07_dataclass_
{ctor_UNSOUND,ctor_TRUE,kw_UNSOUND,literal_TRUE}.py`; reference locks 0869 (POSITIVE),
0870 (NEGATIVE positional false), 0871 (NEGATIVE keyword false).

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

An indented `#@ assigns` in the dependency window lowers to the abstract `val`'s **`writes`**
clause, by the same route a method's own `#@ assigns` takes — the declared targets are filtered
to the labels the receiver's record actually emits, and a target the record does not carry falls
back to the coarse `_pyobj_state` cell. Omitting it leaves the dependency FRAMELESS: the abstract
`val` then declares no effect at all, so every method that calls the dependency may declare
`#@ assigns \nothing` however much state the real provider writes — a false frame no proof plane
can see, because the model has no effect to contradict it.

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
condition. **Except under `no_exception \all`** (route #332, §T.6.30), where the
contract claims no AssertionError escapes and the assert is an obligation.

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

**(c) Every other pattern kind is REFUSED — $\mathcal{T}_s$ is partial here.**

`Module5_IREmitter._py_pattern_to_ir` emits **seven** pattern kinds. Lowering (a) interprets
`Value`, `Wildcard`, `Capture` and `Or`; lowering (b) interprets `Constructor` **when its head
names a constructor the emission declared**. Everything else — sequence patterns
(`case [1, 2]:`, `case [*rest]:`), mapping patterns (`case {"k": v}:`), class patterns on a type
that is not a `#@ datatype` (`case str():`), as-patterns over any of those, and the `Unknown`
residue — is rejected with `PYCSL-R30-UNINTERPRETED-PATTERN`.

Until relaunch #45 they were not rejected; they were **erased**, and the erasure was a false
proof rather than a lost fact:

* lowering (a) ended in a bare `return "true"`, so an uninterpreted arm got an
  **unconditionally true** condition and was taken whatever the subject was. In the DEFAULT
  `hoare` model with no flags, `match x: case [1, 2]: return 1 / case _: return 2` under
  `#@ requires x == 5` proved `#@ ensures \result == 1` from the emission `if true then 1
  else 2`, while Python returns 2 (route #30, witness `pycsl-reference/1011`);
* lowering (b) wrote an **undeclared** constructor name verbatim into the arm head, and Why3
  reads a lowercase identifier that is not a known constructor as a fresh **variable binder** —
  an irrefutable catch-all. `case str():` emitted `match x with | str -> 1 | _ -> 2` and proved
  the same false contract (witness `1012`). Its own fall-through, a bare `_`, was the third
  instance of the identical mistake.

**Neither literal can be repaired by flipping it.** An always-`false` condition (or a
never-matching pattern) is unsound in the other direction: on a subject the pattern really does
match, the model takes a *later* arm, so the same false-contract proof returns with the arms
swapped. The condition for an uninterpreted pattern is **unknown**, and a boolean has no room
for that — refusal is the only sound total answer.

---

### §T.5.10b  `with` over a USER-DEFINED context manager is REFUSED

The context-manager **protocol** is not modelled at all. Neither `__enter__` nor
`__exit__` is called, and the statement does not even reach the IR — Module 5 inlines the
`with` body and drops the header, so `with c: pass` arrives at Module 6 as a bare `Pass`:

    class CM:
        def __init__(self):        self.n = 0
        def __exit__(self, *a):    self.n = 5
    c = CM(); with c: pass
    return c.n            # `#@ ensures \result == 0` PROVED; Python gives 5

The emission was `let c = { n = 0 } in (); c.n` (route #38, witness
`pycsl-reference/1030`). Call the setup and teardown explicitly around the block.

**The refusal is a WHITELIST, because the first version — a blacklist over "does this
class define `__enter__`/`__exit__`" — was walked past twice by ordinary code (route #39,
witnesses `1033` and `1035`):**

* `c: CM = CM()` is an `AnnAssign`, and the name-binding census read plain `Assign` nodes
  only, so the name resolved to no class at all;
* `class CM(Base)` with the protocol on `Base` was never in the set, because the class scan
  read each `ClassDef`'s own body and did not close over inheritance.

Both re-ran route #38's exploit verbatim and proved `\result == 0` where Python gives 5.
The enumeration of ways to *name* a value is open-ended, so the current rule is positive:
**once the unified AST defines a class carrying `__enter__`/`__exit__`/`__aenter__`/
`__aexit__` — closed under inheritance — every `with` in it is refused
(`PYCSL-R38-CONTEXT-MANAGER-DROPPED`) unless its context expression is positively
recognized**, namely a call to (W1) an in-file `@contextmanager` generator, or an in-file
function whose returns are all such calls (a *fixpoint*: `require_parens` returns
`delimit_if(…)` returns `self.delimit(…)`); or (W2) one of a small set of stdlib context
managers with no value-model footprint (`open`, `tempfile.*`, `os.fdopen`, `io.StringIO`,
an executor, `nullcontext`, `suppress`, `closing`, `redirect_std*`).

A file that defines no such class is untouched, which is what keeps the 33 `with <lock>:`
critical sections in `pycsl-reference` working (witness `1034`).

**A name that IS a context-manager class is never allow-listed, by W1 or by W2.** W2 has
to match on the callee's *last segment* — the same manager is written `open(...)`,
`tempfile.NamedTemporaryFile(...)` and `contextlib.closing(...)` — so a user class named
`closing` that defines `__enter__`/`__exit__` matched the allowlist and was let through:
the allowlist was laundering the exact thing it exists to exclude, and `\result == 0`
proved where Python returns 5 (witness `1047`).

**Known residue.** W1 keys on a *simple* method name across the whole unified AST, so if
one class's `foo` is a `@contextmanager` and another's is not, `with self.foo()` on the
second is still allow-listed. Making that class-aware is the next tightening; it is not a
one-liner, because `pure_ast` genuinely defines `block` twice — once as a plain method and
once as a `@contextmanager` — so an "every definition must qualify" rule would refuse the
mirror's own 14 `with self.block()` sites outright.

**The neighbouring ratchet had been counting the other half of this for two windows.**
`bin/check-dropped-mutation.py`'s `CTXBIND = 51` records "`with … as X` — the binding is
not read". The binding is the visible half; the protocol *calls* are the half that carries
the state change.

### §T.5.10c  Every bare `with` must be PROVABLY INERT, in every file (route #257)

§T.5.10b's whitelist ran only in a file that DEFINES a context-manager class, so every
context manager the file does not define walked past it: an IMPORTED class whose
`__enter__` writes `self.n`, an in-file or imported `@contextmanager` function or method
that writes a field, a plain call returning such an object, and a multi-item `with c, d:`
each proved `\result == 0` where Python returns 1 or 2 (witnesses `2560`-`2566`).

The rule is now file-independent and fail-closed (`PYCSL-R257-CONTEXT-MANAGER-NOT-INERT`).
Outside a `\trusted`/`\abstract` function (whose body is never lowered), every BARE `with`
item is refused unless it is

* **(L)** a name bound *only* by `<name> = threading.Lock()` / `threading.RLock()` with
  `import threading` — a lock's enter/exit touches no modelled value (all 49 corpus
  critical sections have this shape); or
* **(G)** a call to an in-file *producer*, resolved per class (`self.m` inside a method of
  `K`, `m` defined once in `K` and overridden by no in-file subclass; or a module-level
  `def` bound exactly once), where the producer is `@contextmanager` (resolved through
  `contextlib`) with exactly one top-level `yield`, or is exactly `return <producer call>` /
  `return nullcontext()`; its body has no `global`/`nonlocal`/`try`/`with`/`raise`/`del`/
  `assert`/loop/comprehension/nested def, stores only to locals or to `self.<attr>` of a
  `K` whose model record has **no fields**, and calls only producers, `len`/`isinstance`, or
  in-file defs framed exactly `assigns \nothing` with no `raises`. A `\trusted` producer
  qualifies only as a `self` method of a field-less `K` whose `assigns` names only `self`
  fields (the mirror's `_Unparser.delimit_if`) — its reviewed frame is trusted to cover
  the protocol of the manager it returns. The call's arguments obey the same call rule.

`with … as` items stay with route #20's refusal; `async with` is refused outright (witness
`2568`); an attribute context expression is refused (`2567`). The mirror's 41
`with self.block()/delimit()/require_parens()/delimit_if()` sites are (G) on `_Unparser`,
whose record is `{ }`; `1031`'s `blk()` (body `yield`) is (G); control `2570` pins the
mirror shape. This also closes §T.5.10b's *known residue* for bare items: (G) resolves per class, not by a simple
method name.

**Scope.** A `@contextmanager` GENERATOR is not refused, and witness `1031` pins that: all
52 `with` statements in the self-annotation mirror are generator CMs (`self.block()`,
`self.delimit()`) or builtins (`open`, `tempfile`, `os`), none of which has the protocol
*methods*. That is a scoping decision, not a soundness claim —
`bin/check-yield-erasure.py`'s ratchet of 2 records that `_Unparser.block` drops its
indent/dedent and that the `with` body is modelled nowhere for it. It is unobservable only
while the emitted `_unparser` record is empty, which is precisely why converting
`_Unparser.__init__` must arrive together with a context-manager protocol model.

---

### §T.5.11b  `try ... else:` — modelled, unless the block jumps out

Python runs a `try`'s `else:` clause when the body completed **without** an exception,
which is the same point as "the end of the try body" provided the block cannot itself
raise into the handlers. $\mathcal{T}_s$ appends the lowered `else` to the try body on
exactly that condition — no `raise` anywhere in the lowering.

**A `return` lowers to `raise (Return …)`.** So an `else:` that returns fails that test
and was, until relaunch #45, **dropped in silence**:

    try:     x = 1
    except ValueError: return 3
    else:    return 2        # absent from the emission entirely
    return 1                 # `#@ ensures \result == 1` PROVED; Python returns 2

(route #37, witness `pycsl-reference/1028`). The block is now **refused**
(`PYCSL-R37-TRY-ELSE-DROPPED`) when it contains a `return`/`raise`/`break`/`continue`; an
`else:` that cannot jump out is still emitted, and witness `1029` holds that capability in
place.

**The ratchet was green throughout, and that is the lesson rather than the bug.**
`bin/check-dropped-mutation.py` classifies this shape as `TRYFINAL` and the counter stood
at 10: the drop was *counted*. Route #21 had already established, for the `finally` half of
the same counter, that a counted drop can be exploitable — and refused it. The `else` half
was left counted and unrefused on identical evidence.

**And route #21's own fence left a third shape counted (route #156, gen #29).** A `finally`
WITHOUT handlers is emitted only when the lowered try body contains no `raise`; when the body
jumps out (`return`/`raise`/`break`/`continue`) the block was dropped on every path:

    x = 0
    try:
        try:     raise ValueError
        finally: x = 7
    except ValueError: pass
    return x                 # `#@ ensures \result != 7` PROVED; Python returns 7

This shape is now **refused** (`PYCSL-R156-TRY-FINALLY-JUMP-DROPPED`) in any non-trusted function;
a handler-less `finally` whose body cannot jump out is still emitted (witness `1530`), and
`check-dropped-mutation` counts the refused shape as REFUSED (TRYFINAL 9 -> 5).

---

### §T.5.12a  The exception model after gen #29 (routes #167-#184)

Fourteen repairs landed in gen #29 turn call sites and handler paths from *assumed* into
*checked*. Collected here because they share one mechanism: a construct the emitter models as
"cannot fail" is a construct whose failure path the proof deletes.

**Call sites of a stubbed method (routes #167, #176, #182).** A `<recv>.<m>(...)` the emitter
cannot lower concretely becomes an abstract `val`. That stub used to carry neither the callee's
PRECONDITION nor its RAISES:

    class C:
        #@ requires self.x != 0
        def get(self) -> int: return self.x // self.x
    c = C(0); c.get(); return 5        # `#@ ensures \result == 5` PROVED; CPython ZeroDivisionError

The call site now ASSERTS each non-trivial `requires`, rendered with the callee's parameters
substituted by the call's arguments and `self` by the receiver (anything not faithfully
renderable asserts `false`), and — when the calling function has a handler for it — may RAISE what
the callee can let escape (declared `raises`, an escaping `raise`, transitively through the file's
call graph; imported stubs included). `C(0).go()` and `super().go()`, which reach the generic
unannotated-call fallback with a bare method name, are covered by the same two rules.

**Handled implicit exceptions (routes #170-#174, #177, #178, #182).** Without `no_exception`, an
implicit raise is ambient: a missing-key dict read answers the placeholder, an empty list literal
is a 1024-cell placeholder array, `int(<str>)` is an opaque total function. That is sound while the
exception ESCAPES and wrong once a handler CATCHES it — the handler's path is dead in the proof and
taken in Python. A function that CLAIMS something (a non-trivial `ensures`, an in-body assertion, a
loop invariant/variant, or a class invariant it must re-establish) and catches one of the modelled
implicit exceptions is now checked as if it declared `no_exception` for it; a dict read inside such
a function RAISES `KeyError` on a missing key instead of answering the placeholder; comprehensions,
tuple unpacks, negative shifts and calls into uncontracted or imported callees that can raise
implicitly are refused rather than discharged; and a handler that only an UNMODELLED exception could
reach (`AttributeError`, `OverflowError`, `UnicodeDecodeError`, or any broad `except Exception`) is
refused outright.

**Exception identity (routes #175, #179, #181).** Why3 exceptions are flat tags: a user
`class MyErr(ValueError)` raised under `except ValueError` escaped the handler in the proof, and a
`raise` inside `__init__` vanished into the record literal a construction lowers to. Both are refused
now, reading the SOURCE (the resolved IR has already merged inheritance away) of the main file AND of
the modules it imports; plain-name aliases of an exception class are resolved.
**A user class named like a builtin (route #305):** the tag of a user exception is its bare name, so
a user `class KeyError(Exception)` was the builtin `KeyError` tag with the builtin's `EXCEPTION_BASES`
row (`with LookupError -> ... | KeyError -> ...` caught it; the implicit `KeyError` of `d[5]` was
caught by the user class's handler). Any binding of a builtin exception name is refused before emission
(`PYCSL-R305-BUILTIN-EXCEPTION-NAME-SHADOWED`); no distinct tag is emitted.
**Builtin subclasses (route #260):** `exception_model.EXCEPTION_BASES` lists every CPython builtin
exception class with all its ancestors, so a handler `except LookupError` / `ArithmeticError` /
`ValueError` / `Exception` / `BaseException` gets one Why3 `with` arm per raised subclass tag
(`raise KeyError` under `except LookupError` used to escape the handler and prove the other path).
And a function whose every normal exit is dead while its spec carries an ADDED, undeclared
`raises { E }` arm is reported VACUOUS by the non-vacuity gate (declare the raise, or annotate
`-> NoReturn`).
**Self-calls and the class invariant (route #261):** a `self.<m>(...)` call in a class with a
`#@ class invariant` passes `self` to the abstract operation, as `<local>.<m>(...)` does, so Why3
checks the invariant at the call instead of assuming the callee's invariant-dependent result.
**A callee's undeclared raise behind a method stub (route #272):** a METHOD call lowers to an
abstract `val` that carries the callee's `ensures` and none of its exceptions — only a DECLARED
`#@ raises`, and only through the route #100/#105/#186 wrap, which resolves `self.…` and variable
receivers bound to a class of this unit (typed, constructor-bound, module-global), not `C.m(...)`
or `C().m(...)`. An escaping `raise` the callee does not declare is read partially for the callee
itself (an added `raises { E }` on its own `let`), so a caller's `no_exception` was discharged by
nobody (`self.chk(k)`, `c.chk(k)`, `C.chk(k)`, `C().chk(k)`, `self.d.chk(k)`, chains through a
method or a module function, all PROVED `no_exception \all`; CPython raises). A module-function call
is applied concretely and Why3's effect typing already sees the callee's own `raise`. RULE
(`PYCSL-SEM-UNDECLARED-CALLEE-RAISE`, ir-semantic, refused): a function claiming `no_exception`
(`\all`: any exception; a named list: a listed class, a subclass of one, or a name outside the
modelled hierarchy) may not make a call whose HIDDEN set it covers outside a handler catching it.
HIDDEN of a method callee = its escaping undeclared raises (a bare or computed `raise` is unknown),
its declared ones when the receiver form is not one the wrap resolves, and the HIDDEN of its own
calls not caught there (transitively, over route #263's call graph; a declared `raises` on an
intermediate does not excuse them — the hidden path never checks its condition); of a
module-function callee, the HIDDEN of its calls only. `\trusted`/`\abstract`/imported callees speak
by their contract only (route #207 refuses a bodyless method under `no_exception`; an imported
function's stub carries the `raises` its body shows); `super().m()` is refused by route #161;
constructors are route #179's.

**A function's own explicit `raise` under its `no_exception` (route #304).** The escaping set of
the body (`IRScanner.collect_escaping_exceptions`, handler-aware) used to become `raises { E }` on
the function's OWN `let` for every class, and Why3 checks `ensures` on normal termination only, so
`#@ no_exception ValueError` + `ensures \result == 0` + `if x < 0: raise ValueError` PROVED (CPython
raises); likewise under `\all` for any class, a user subclass of a listed class, and methods. RULE
(`_emit_function_block`): each escaping class covered by the DECLARED claim (`\all`: any; a named
list: the class or an ancestor — builtin `exception_model.bases_closure` plus the program's class
bases snapshotted by `_run_pipeline` before the inheritance merge clears them; unknown ancestry is
covered) is dropped from the inferred `raises`, and the lowered body becomes
`try (<body>) with E -> (assert { [@expl:no_exception: own raise E reachable] false }; absurd) end`.
A raise caught by a handler of the same function never reaches the wrapper; the #171 handler-widened
context is not consulted.

**Inlined global-instance methods (routes #168, #169).** `_g.m()` is spliced into the caller. A
discarded tail `return <e>` dropped `<e>` — its division check, its nested mutating call — so it is
now bound to a fresh local; and only the callee's own single-name binds were freshened, so a
tuple-unpack target overwrote the caller's variable and a name read from module scope resolved to a
caller local. Tuple targets are freshened; a spliced identifier the caller binds is refused.

**`None` is not the integer 0 (routes #183, #184).** A field whose only initialiser is `None`, a
`None` element of a list literal and a `None` value of a dict literal answered a DEFINITE zero
(`c.v == 0`, `xs[0] == 0`, `d["a"] == 0` all PROVED True; `xs[0] + 1` PROVED `== 1` where CPython
raises TypeError). They now answer route #44's opaque `pycsl_none`, so the comparison is UNDECIDED.
The remaining `None` positions — STORES (`xs[0] = None`, `self.v = None`, `append(None)`) and
Optional locals — keep the integer-0 lowering; that is route #56, whose repair is a distinguishable
`None` in the value model (measured: giving the typed `NoneExpr` arm the opaque moves 16 mirror
emissions).

**A walrus inside a comprehension (route #180).** PEP 572 binds it in the CONTAINING function, and
the comprehension lowers to an opaque value, so `y = 0; [(y := x) for x in [1, 2, 3]]; return y`
proved `0`. Refused.

#### Which callee a call site gets (routes #166, #185-#189)

Five of gen #29's routes are one question asked five ways: **which callee does this call site get,
and is that answer single-valued?** They are worth reading together, because each repair closed one
spelling and the next generator found the next.

* **#166 — one stub NAME, two callees.** The abstract stub is named from the call's SPELLING
  (`<receiver>_<method>_<arity>`), so `o.get()` on a `C` and `o.get()` on a `D` both registered
  `o_get_0`, and `_add_abstract_op` resolved the clash by KEEPING THE LONGER declaration. Repair: a
  different declaration under a taken name gets its own name.
* **#185 — a field receiver mis-KEYS the callee.** `self.inner.get()` resolved to `outer__inner_get`,
  a name no function carries, so routes #167 (precondition) and #176 (may-raise) looked up nothing.
  Repair: an unmatched key falls back to the method-name match.
* **#186 — the same mis-keying on the `raises` wrap.** The key handed to
  `_wrap_call_with_callee_raises_assert` was computed in the same block and kept the broken spelling,
  so a declared `#@ raises E when P` produced no `assert { not P }`. Repair: the same fallback, with
  an `assert { false }` when several raising candidates match (attaching one class's condition to
  another's callee would be a WRONG fact, not a missing one).
* **#188 — the disambiguating suffix COLLIDES.** #166's fix suffixes a clashing name with
  `_c{stable_hash(decl) % 100000}` — 100000 buckets — and the keep-the-longer resolution is still
  underneath it, so two callees whose suffixes collide share one contract again. The collision is
  constructible: `ensures \result == 123` and `ensures \result == 441` both hash to `_c84185`.
  Repair: the suffix is injective per base name. **A hash-derived NAME is not a disambiguator unless
  the collision case is handled** — the two other `% 100000` names in the emitter (the `any`/`all`
  fold and the string fold) take the same reading, and are fail-closed only INCIDENTALLY, by Why3's
  duplicate-symbol rejection.
* **#189 — one receiver NAME, two classes.** `IRScanner.find_record_var_classes` `update()`s every
  nested scope into one flat map, so `if flag > 0: o = D() else: o = C()` resolved `o` to `C` and the
  single call site carried `C.get`'s `ensures` on every path. Repair: a function that binds one name
  to two record classes and then calls a method on it is refused — the scanner itself is the
  certified `sdict` dict-fold, and every in-scanner marking loses that lowering.

**A module body is not in the IR (route #187).** `#@ fresh_globals` re-establishes each module-global
singleton's CONSTRUCTOR post-state as an ASSUMED entry fact, and the IR records a global as
`{name, class, value}` only — every other top-level statement is dropped. `counter = Counter();
counter.n = 7` then a `fresh_globals` driver returning `counter.n` PROVED `\result == 0` (CPython 7),
as did the same with a top-level `counter.bump()`. The existing confinement checked only that the
driver is not a method and is called by nobody; neither looks at the module body. A `fresh_globals`
file's module body may now contain only imports, definitions, a docstring and simple bindings that
neither rebind a name nor read a global singleton.

---

### §T.5.12b  `and` / `or` in a VALUE position return the OPERAND

Python's `and` and `or` are **selection**, not conjunction: `0 or 5` is `5` and `3 and 7`
is `7`. Until relaunch #45 the emitter lowered them in a body as
`if <l> ∧ <r> then 1 else 0` under a comment reading "In body context, Python's and/or
return int", so `x = 0 or 5` proved `x == 1` (route #35, witness
`pycsl-reference/1023`). The lowering is **correct in a condition and wrong in a value**,
and nothing at the emission site knows which consumer it has, so the value-preserving
form is emitted wherever the result is not already a Python bool — and it is equally
correct in a condition, because the truthiness then tested is that of the *selected*
operand, which is the operand Python would have tested.

$$\mathcal{T}_e\llbracket \texttt{a or b} \rrbracket
= \texttt{(let l = } a' \texttt{ in if l <> 0 then l else } b' \texttt{)}$$
$$\mathcal{T}_e\llbracket \texttt{a and b} \rrbracket
= \texttt{(let l = } a' \texttt{ in if l <> 0 then } b' \texttt{ else l)}$$

**Two separate questions decide $a'$ and whether the rule fires at all**, and conflating
them is how the first attempt emitted `bool <> 0` and took mirror L3-tc from 53/53 to
40/53:

* **Python-boolishness** decides whether `1`/`0` is *already* faithful. It is, when the
  operand's Python value is a bool — a comparison, a `not`, a bool literal, a
  quantifier, a bool-returning builtin (`isinstance`/`hasattr`/`any`/`all`), an inductive
  predicate, or an `and`/`or` of those. The recursion through nested `and`/`or` is
  load-bearing: the both-boolean case emits the *int* `if … then 1 else 0`, so
  `a == 0 and b == 3 and c == 1` would otherwise look mixed. Both operands boolish →
  the emission is **unchanged**, which is why the ordinary `a == b or c == d` shape does
  not move.
* **Why3 typing** decides whether an operand may be selected raw. `_to_bool` returns
  exactly `(<x> <> 0)` when — and only when — it coerced an *int* expression; every
  other branch hands back a Why3 *bool* (`Array.length … <> 0`, `hval_truthy …`,
  `py_isinstance_…_op`, a comparison). So $a' = a$ under that string equality and
  $a' = $ `(if <a as bool> then 1 else 0)` otherwise. A boolean operand's int encoding is
  faithful because Python's `True` **is** `1`.

The string-operand and `emit_ir`-operand cases above already selected the operand; this
is the general case catching up with them.

---

### §T.5.12c  The `for` loop variable survives the loop

Python leaves a loop variable bound to its **last** value, and to its previous value when
the loop body never ran. The binder opens the target with an inner `let` inside the loop
body, so the name is shadowed for the loop's duration and the OUTER ref kept its pre-loop
value afterwards:

    i = 0
    for i in range(3):
        pass
    return i        # Python: 2      model, before relaunch #45: 0

That proved `\result == 0` (route #36, witness `pycsl-reference/1025`), and so did the
same program **without** the `i = 0` (witness `1026`) — Module 6 declares the target as an
outer ref whether or not the source pre-assigns it, so the leak needs no stale value.
The binder now assigns the outer ref immediately **before** opening the inner `let`, which
reproduces Python exactly, never-ran case included.

**Scope, stated rather than implied.** The write-back fires only for a target the function
reads OUTSIDE its loop (a target read only inside is already faithful; a fresh target read
afterwards is an unbound Why3 name and fails closed), and only for an **index-valued**
loop, where the bound term IS the counter and is therefore int-typed like the outer ref.
A general element write-back is not well-typed: the outer ref takes its type from the
first assignment to that name, which need not be the loop's element type — measured, an
unconditional write-back took mirror L3-tc to 51/53 and an `any int` havoc to 52/53 (the
mirror's own `stmt_control_flow.py` has an `emit_ir`-typed loop target).

The **sequence** case is admitted on a pair of conditions that pin *both* types instead of
guessing one: the target is in none of the non-int local classes `_typed_local_vars`
excludes from the integer `ref 0` pre-declaration (so its outer ref really is an `int`
ref), **and** the iterable is a formal parameter whose symbol type is `list` (so its
element really is an `int`). Witness `pycsl-reference/1027`. Note that
`_current_array1d_params` is *not* the right source for the second half — it is empty at
the binder for a plain `a: list` parameter, so a version keyed on it never fires while
looking exactly as though it does.

**Route #302 — every other lowering, flow-aware.** The residue above was a real false
proof: `x = ""; for x in e: pass; return x` proved `\result == ""` (CPython `e[0]`), and
so did the char loop, `s.split()`, `sorted(e)`, a local list, `range(5, 0, -1)` (its
element is not the bare counter), a loop under an `if` or in a `try`, a `break`-exited
loop, and a body that re-binds its own target (witnesses `pycsl-reference/3630`–`3639`).
`_reset_function_state` now walks each plain-name loop target's reads along their
statement paths (the route #301 walk): a read is **stale** when a statement holding a
plain loop on the name is met before a top-level re-binding (`Assign`/`TupleUnpack`),
or the read sits in a non-binding loop holding one; a read in the body of a loop that
binds the name, in a comprehension binding it, or in a (dropped) `assert` is not. A read
is a `Var`, an `AugAssign` of the name, a field store through it or a call of it. For a
stale name the binder writes the element back to the outer ref for **every** iteration
lowering, whatever the types: where the outer ref's type is the element's this is
Python's last-value semantics exactly (never-ran case included); where it is not, the
emission does not type-check and the function fails closed (L3-tc) — a stale proof
is never produced. When the loop body itself re-binds the target (an assignment, an
inner loop on the name, a walrus), Python keeps one variable, so that loop binds the
outer ref directly and opens no inner `let`. A name re-bound before every later read
keeps the old emission byte-identical (root/pyref/mirror: 0 moved).

---

### §T.5.12d  The `...` literal is an OPAQUE value, not the integer 0

Module 5 lowers `...` to `{"type": "Number", "value": 0, "py_ellipsis": True}` — it has
no IR node of its own. Relaunch #12 recorded that as "a silent WRONG-VALUE erasure ...
left alone deliberately" and never probed it. The erasure is not a *loss*, it is a
**conflation**: `...` became the *literal* integer 0, so every comparison against 0
decided the wrong way. All six of these proved a contract that is FALSE of the program
(route #40, witnesses `1036`–`1040`):

| program | model said | Python does |
|---|---|---|
| `x = ...; if x:` | `!x <> 0` — false | `bool(Ellipsis)` is **True** |
| `if ...:` | false | **True** |
| `x = ...; if x == 0:` | **true** | `Ellipsis == 0` is False |
| `x = 0; if x is ...:` | **true** | `0 is Ellipsis` is False |
| `x = ...; x + 5` | `5` | `TypeError` |
| `return ...` | `0` | returns `Ellipsis` |

$\mathcal{T}_e$ now emits an **opaque** `val function pycsl_ellipsis : int` with no
defining axiom, so every one of those goals is undecidable instead of decided wrongly.
Nothing that merely holds, passes or returns a `...` is refused — only claims *about its
integer value* stop being provable.

**Why opacity rather than a refusal.** Two concrete methods in the self-annotation mirror
use `...` in a value position (`pure_ast._Unparser.visit_Constant`, `pure_ast.atom`), both
in the *comparison* position that witness `1038` exploits, and no syntactic test separates
them from the exploit. Opacity closes both at once and makes the mirror's own model
*more* faithful: `value is ...` lowers to `!value = pycsl_ellipsis` instead of
`!value = 0`. The one faithful consumer is untouched — `_py_expr_constant`'s own
`expr.value is ...` is recognized upstream as `(is_pvellipsis <pyconst_val>)`.

**Both spellings of the singleton are covered.** `Ellipsis` — the builtin *name* for the
same object — went through `_py_expr_name`, which returned a bare
`{"type": "Number", "value": 0}` carrying none of the literal's marker, so `x is Ellipsis`
still answered `0 = 0` and `x = 0; if x is Ellipsis:` proved (witness `1048`).
`frontend/desugar.py::normalize_stores` now rewrites the Load-context name into the
literal — semantically exact, since they denote the same object — so route #40's opacity
covers both. `... is Ellipsis` proves (witness `1049`, and `python-reference/0041`), and
`<int> is Ellipsis` does not. The rewrite is skipped if the module *binds* the name.

**The general shape, and it is the reason to read this section:** a Python *singleton*
modelled as an integer literal is indistinguishable from that integer inside the model.
`None` is lowered to `0` on the same terms and has the same three exploits
(`None == 0`, `<int> is None`, `None + 5`); that residue is recorded in the driver
backlog with its reopening capability (a tagged value model), because `None`-as-`0` is
load-bearing across the whole emitter in a way `...` is not.

---

### §T.5.12f  A COMPLEX literal is REFUSED

`_py_expr_constant` lowered `isinstance(expr.value, complex)` to
`{"type": "Number", "value": int(expr.value.real)}`: the imaginary part **discarded**, the
real part **truncated to an int**. There is no complex model anywhere in the pipeline, so
the model received an ordinary integer and then *decided* on it (route #43, witnesses
`1050`–`1052`):

| program | model | Python |
|---|---|---|
| `x = 3j; if x == 0:` | taken | `3j == 0` is **False** |
| `x = 1 + 2j; if x == 1:` | taken | `(1+2j) == 1` is **False** |
| `x = 3j; if x:` | **not** taken | `bool(3j)` is **True** |

A complex literal anywhere in the unified AST is now refused
(`PYCSL-R43-COMPLEX-LITERAL-ERASED`). **Refused rather than made opaque, on a
measurement**: the whole repository contains exactly *one* complex literal
(`python-reference/0044`, an `assert`-only coverage driver, now `pycsl-expected: FAIL`),
so opacity would buy no program anything, while the refusal says the true thing — PyCSL
models no complex arithmetic, and `c.real` / `c.imag` are not modelled either.

---

### §T.5.12k  A `getattr` DEFAULT was the integer 0, and so was the no-default form

`_lower_getattr`'s absent-attribute path coerced a **non-scalar default** to the literal
`0`, and the comment justified it as "the dict/list content is then unmodeled (fails-safe)".
It is not fails-safe: an *unmodelled* value is undecidable and the integer `0` is
**decidable**, so the model did not lose the default — it *decided* with it (route #47,
witnesses `1070`–`1073`):

| program | model | Python |
|---|---|---|
| `d = getattr(c, "missing", {}); if d == 0:` | taken | `{} == 0` is **False** |
| `d = getattr(c, "missing", []); if d == 0:` | taken | `[] == 0` is **False** |
| `d = getattr(c, "missing"); if d == 0:` | taken | **AttributeError** — no value at all |

The third row is the worst: Python produces no value there, and `if len(args_ir) <= 2:
return "0"` fabricated a zero out of nothing.

Route #22 (§T.5.12b, witness `0991`) closed the case where the attribute **is declared** and
deliberately left ABSENCE alone. That was right about *which* value is returned and silent
about *how that value is modelled*.

Both paths now answer an opaque `val function` with no defining axiom, **keyed on the
default's own IR hash**. The granularity is a semantic decision each time, and this is its
third distinct answer in this family: route #41 needed **per-name** constants (two erased
locals are different objects), route #44 needed a **shared** one (`None` is one object), and
here two *syntactically identical* defaults denote equal values — `{} == {}` and
`{1: 2} == {1: 2}` are both True in Python — so they must share a constant and stay provably
equal, while `{} == []` and `{1: 2} == {3: 4}` must become undecidable rather than decided.

The no-default form is made **opaque rather than refused, on a measurement**:
`bin/check-getattr-erasure.py` reports ABSENT 7 / UNKNOWN 19, and for an object of *unknown*
static type the attribute may well exist, so a refusal would break nineteen sites to state
something true of at most seven. **Residue, stated:** opacity models "some value" where
Python has none, so a contract about the `AttributeError` itself is still not expressible.

---

### §T.5.12l  A SEEDED collection drops its seed, and the empty map's default is DECIDED

`Counter(...)`, `OrderedDict(...)` and `defaultdict(f, seed)` all reduced to
`(const (None: option int))`, and the comment called it "a sound under-approximation:
content that depends on the seed fails to prove, never proves falsely". That is the one
claim the coercion could not make. `(const None)` is not an *unknown* map, it is the
**empty** one, and the model's missing-key default is the integer `0` — so a dropped seed is
not merely lost: every read of a seeded key becomes the decidable `0` (route #48, witnesses
`1076`–`1079`):

| program | model | Python |
|---|---|---|
| `c = Counter([1,1,2]); if c[1] == 0:` | taken | `c[1]` is **2** |
| `d = OrderedDict([(1,5)]); if d[1] == 0:` | taken | `d[1]` is **5** |
| `d = defaultdict(int, {1:5}); if d[1] == 0:` | taken | `d[1]` is **5** |

**The factory form is untouched, and that is the point.** An empty `Counter()` and a
`defaultdict(int)` really do answer `0` for a missing key, so the empty-map model is
*faithful* for them — `pycsl-reference/0498` is the driver that says so and it must keep
proving. Only a construction that carries a **seed** becomes opaque, keyed on the seed's own
IR hash for the reason §T.5.12k's is keyed on the default's. `defaultdict`'s *first*
argument is a factory and its *second* is a seed, so the two are treated differently inside
one constructor — witness `1078` is what pins the argument position.

Census of the whole tree: eleven mentions of the three names and **not one live site carries
a seed**, so this is byte-inert *by measurement*, not by construction.

---

### §T.5.12m  `a.append(x)` on a list PARAMETER was invisible to the caller

Python passes a list argument by reference, so an `append` inside a callee must be visible
to the caller. It was not (route #49, witnesses `1080`–`1082`):

```whyml
  let g (a: array int) : unit
    requires { true } ensures { true }
  =
    let a = ref (snapshot a) in        (* a LOCAL COPY *)
    a := Seq.snoc !a 1                 (* appended to the COPY *)
```

`g` carries **no `writes` clause at all**, so Why3 knows `a` is unchanged across the call and
the caller proves `Array.length a = 0` afterwards. The mutation is not un-modelled, it is
modelled as **absent** — and the callee could even declare `assigns \nothing` while doing it,
with nothing catching the frame lie, because the model and the declaration agree with each
other and both disagree with Python.

**`append` was the odd one out of its own family**, which is what makes a refusal the right
answer rather than a fifth special case: `pop`, `insert`, `clear`, `extend` and `remove` on a
list parameter were already REFUSED; `a[0] = v`, `d[k] = v`, `s.add` and `s.discard` through
a parameter are CALLER-VISIBLE; and a LOCAL list's appends are faithful (`1082`). So the
refusal is keyed on the receiver being a **formal parameter**, never on `.append` itself.

`bin/check-param-mutator-visibility.py` is the plane that makes this table visible without
probing each cell by hand: it *generates* a driver per cell whose caller asserts the
collection is unchanged — a contract false of the program — and runs the real pipeline, so
"proves" means DROPPED. `bin/check-dropped-mutation.py` does not overlap it: that plane's
population is Module 5's assignment-family statements, where a statement produces no IR at
all, and here the statement *is* in the IR and it is the lowering that copies.

---

### §T.5.12n  `Optional[str]`: `None` was the empty string, and `is None` was `false`

A `None` bound to a **string-typed local** inside a `@mutable_state` class emitted `s := ""`,
and `x is None` on a string operand answered the **literal `false`** (route #50, witnesses
`1085`–`1088`). The comment above that arm called it "a sound always-present model". It is
neither: a model *approximates* a branch, and this **deleted** one —

```whyml
    if ((if false || false then 1 else 0) <> 0) then begin   (* the `is None` early return *)
      raise (Return__union__field_type_of_1 Arm_1_None)      (* ...now unreachable *)
```

— so every contract over that function was proved on a **strict subset** of the reachable
states. That emission is from the `module6_whyml/types.py` mirror, i.e. the defect was live in
PyCSL's own self-annotation, not only in user code.

The repair is **type-preserving**, which is why it is small: an opaque `val function
pycsl_none_str : string` with no defining axiom is the absent sentinel, so the local stays a
`ref string`. `is None` then has **three** answers, keyed on the BINDING rather than on the
type:

| binding at the guard | lowering | why |
|---|---|---|
| a live `None` record (linear) | `true` / `false` | the name **is** the singleton here — a fact |
| `AMBIG` (see §T.5.12o) | `(str_eq_op x pycsl_none_str)` | the model does not know which path ran |
| never bound to `None` | `false` / `true` | the always-present answer, unchanged and byte-inert |

`s == ""` becomes undecidable rather than decidably true, which is the correct answer: the
model does not know the local is not the empty string. The linear case is a **completeness
gain** (`1087` failed before this change and proves now): the old read handed a str local the
INT opaque `pycsl_none`, which Why3 type-rejected — fail-closed by type accident.

**Stated residue**: a local bound from a CALL that returns `Optional[str]` is not
syntactically `None`-bound, so it still reads as always-present.

---

### §T.5.12o  The erased-locals record is flow-insensitive, and a branch walks past it

Routes #41/#44/#45 record a local whose binding the model cannot represent — a generator, a
non-empty tuple, `None`, a NaN — and key their lowerings on that record. The record is
**linear**: written when the assignment is emitted, cleared when the name is rebound. That is
exactly right for facts used to REFUSE and wrong for facts used to DECIDE, because
`bool(x) is False` and `x is the None singleton` are **path** facts (route #46, witnesses
`1089`–`1091`):

```python
    if c > 0: x = None          # then-branch records `None`
    else:     x = 5             # else-branch CLEARS the record
    if x == 0: return 7         # reads the ordinary `!x`, which the model holds at 0
```

$\mathcal{T}$ now walks the function body **once before emitting it** and marks every name
bound to `None`/NaN on some path and to something else on another as `AMBIG`: its value is
the per-name opaque, its truthiness is left undecided, and the linear recorder may not
overwrite the mark.

Three things about the scan are load-bearing, each of them measured rather than argued:

* **It carries a nesting DEPTH.** If every binding of a name is at the top level of the body,
  emission order is execution order and the linear record is already exact, so it is left
  alone (`1090`). Ambiguity needs a *conditional* binding.
* **The opaque carries the local's own WhyML type** (`ref ""` → `string`, `ref 0` → `int`),
  never the symbol table's Python tag: an unannotated str local is tagged `Any`. The first
  spelling fed `pycsl_erased_receiver_name : int` into `str_eq_op`.
* **A name that already has a faithful optional carrier is skipped** — `_optional_union_locals`,
  `_iropt_ir_local_vars`, `_iropt_str_local_vars`, `_emit_ir_local_vars` each model `None`
  exactly, so the degeneration this route closes cannot arise for them. Every ambiguous name
  in the `pure_ast` mirror is one of these.

**The NaN half is a REFUSAL, and route #45 is why**: making the value opaque cannot close
`x == x`, because an opaque constant is still equal to itself. A comparison over a
possibly-NaN name is rejected (`PYCSL-WHYML-AMBIGUOUS-NAN-COMPARISON`), and the taint follows
arithmetic — IEEE 754 makes every operation with a NaN operand NaN, so `y = x + 1` is
possibly-NaN too.

---

### §T.5.12p  `is` between two VALUE-typed operands is not identity

Route #42 gave `is` its own IR operator, narrowed it back to `==`/`!=` at the
`generate_json` choke point carrying the additive `py_is` marker, and whitelisted exactly one
shape: an identity test against a `bool` LITERAL. Everything else still lowers to `==`
(route #52, witnesses `1092`–`1093`):

```python
    a: str = "a"
    b: str = a + "b"        # built at RUN time — a fresh object
    c: str = "ab"           # a compile-time constant
    if b is c:              # Python: False.   Model: str equality -> True
```

For an object whose `__eq__` is the DEFAULT one, equality **is** identity, and that is why the
enum-member, sentinel and class-object idioms this tree uses are modelled correctly. For a
type with VALUE equality — `str`, `int`, `float`, `bytes`, `tuple`, `list`, `dict`, `set`,
`frozenset` — it is not, and the model decided the test as equality.

$\mathcal{T}_e$ now REFUSES an identity test where either operand can be SHOWN value-typed —
a literal of such a type, or a name the symbol table types as one — with two exemptions that
are part of the semantics rather than concessions:

* **`x is x`** is True in Python for every type (identity is reflexive, and one name denotes
  one object), so the same-variable shape is admitted whatever its type (`1093`).
* **the SINGLETON family** — `x is None`, `x is Ellipsis`, `x is NotImplemented` — is modelled
  faithfully by §T.5.12n and routes #40/#44 *downstream* of this handler, so it is let
  through. The first spelling omitted this and took SEVEN of the fifty-three mirror files out
  of emission altogether (46 of 53) against a census that predicted zero: the census says
  where to look, the measurement is the gate.

**This refusal is a BLACKLIST, and that is a departure from route #42's whitelist rule made on
a measurement.** The whitelist form — admit only where the emitter can SHOW equality implies
identity — would have to refuse all six non-singleton `is` sites in the tree
(`operator_precedence is not _Precedence.FACTOR`, `stmt.origin is not _ABSENT`,
`type(C) is Meta`, and three `Ellipsis`/`NotImplemented` tests), every one of which the `==`
lowering gets right, because nothing in the emitter can show a name is identity-typed. The
residue is therefore stated rather than hidden: an *unannotated* local holding a string is not
refused.

---

### §T.5.12q  A dict literal had two models, and the reader used the wrong one

`len({1: 10, True: 20})` is **1** in Python — `True` hashes and compares equal to `1`, so the
second entry overwrites the first — and `d[1]` is **20**. The model proved 2 and 10
respectively (route #54, witnesses `1095`–`1099`). The emitted body shows both models at once:

```whyml
    let d = ref (map_update_some (map_update_some (const (None: option int)) 1 10) 1 20) in
    2                       (* <- `len(d)`, folded from the LITERAL's entry count *)
```

The **map is faithful**: two updates at the same key in source order, the later winning,
exactly Python. The **constant fold** that answers `len(d)` and `d[k]` never consulted it —
it counted the literal's syntactic entries and matched keys by their source form, so
`True` and `1`, and `"\x61"` and `"a"`, were different keys to it.

$\mathcal{T}$ now gives the fold **Python's own key equality**: each literal key is normalised
to its value (a `Bool` key is the int `1`/`0`), the size is the count of DISTINCT normalised
keys, and a later entry SHADOWS an earlier one at the same key — which is what the map was
already doing. The repair is EXACT rather than fail-closed: `len(...) == 1` and `d[1] == 20`
both failed before and prove now.

**This is route #48 mirrored.** There a seeded collection dropped its seed; here the seed is
kept in the map and dropped by the reader. The rule that catches both: *a fold over a literal
is sound only where the fold's key equality is the model's key equality.*

**The fold answers only what the source text decides** (routes #61 and #297). A dict literal
with ANY key the fold cannot normalise to a Python value (a name, `-0`, `2 - 1`, `+1`, a call)
or a non-integral float key registers NEITHER a size NOR an element map: a non-literal key may
equal a literal one at runtime and overwrite it (`{0: 1, k: 2}[0]` is 2 when `k == 0`), so
`len(d)` / `d[0]` read the faithful map or fail closed. The same holds for a set literal with
a non-literal element (two values the fold cannot see may be equal) and for any list / tuple /
set literal with a `Starred` element (`*ys` contributes `len(ys)` elements and shifts every
later index). The name is then blacklisted like a rebound collection, so a later literal
binding in another arm cannot register for it. The inline `len(<literal>)` fold follows the
same rule (no `Starred`; all-literal set/dict elements counted DISTINCT under Python equality),
and the indexed-read fold accepts an `int` index only (`a[1.0]` raises `TypeError`). A plain
non-literal element of a list/tuple keeps the SIZE fold and the literal positions' element
fold: one syntactic element is exactly one runtime element at its own index.

**The fold is per NAME, so it needs a name with exactly one static binding** (route #300). The
emitter registers a literal's size/elements when it emits the binding, and it cannot see the
branch or loop the binding sits in; a literal binding in ONE arm after a non-literal first
binding (`d = e; if c == 1: d = {"a": 1}; return len(d)`, or a parameter re-bound in one arm)
used to answer on EVERY path. The per-function pre-pass now counts every static binding of each
name — a formal parameter, `with ... as`, any Assign / AugAssign / GhostAssign / `for` /
walrus / comprehension target, a `TupleUnpack` or tuple-`for` target list, an `except ... as`
name, a `match` capture — and a name bound more than once is fold-unsafe (no size, no
elements; a literal-bound one is also a rebound collection), whatever its first binding was.

**A starred element is not wrapped element-wise into an `hval`** (route #299). A `PyVal`
dict-literal value is tagged into `hval` element by element (`HArr` over `HCons`, `HMap` over
`PCons`). A list literal with a `Starred` element (`[*range(2), 3]`, `[*"q"]`) or a dict
literal with a `**m` entry lowers instead to an unconstrained carrier of the right constructor,
`(HArr (any hval_list))` / `(HMap (any hpairs))`: `isinstance(x, list|dict)` stays decided,
the length, truthiness, membership and the `hval_to_seq` bridge are unknown. In a
specification (no `any`) such a literal is refused.

---

### §T.5.12r  `is None` was decided from a TYPE where only a BINDING could justify it

Route #50 established that a string `is None` test has more than one right answer and that
*which* answer is right is a question about the **binding**, not about the type. It gave the
arm two binding-justified answers — DECIDED under a live linear `None` record, OPAQUE under
route #46's `AMBIG` — and left a third, the always-present `false`, for a name the function
never binds to `None`. That third answer was justified by nothing but the operand's type, and
there are three ways to reach it with **no binding in the function at all** (route #51,
witnesses `1100`–`1102`):

| shape | the operand | why the model had no binding fact |
|---|---|---|
| (a) | a local bound from a CALL whose `-> str` is contradicted by `return None` | the callee's real return set |
| (b) | a `str`-declared dataclass FIELD a caller stored `None` into | a field's value comes from outside the method |
| (c) | a `str`-declared PARAMETER a caller passed `None` | a parameter's value comes from outside the function |

Shape (c) is the cheapest reproduction in the class and needs no lie at all — a Python type
hint is not enforced, so the caller simply passes `None`:

```python
    def probe(self, s: str) -> int:
        if s is None: return 0
        return 7                   #@ ensures \result == 7   <- PROVED. Python returns 0.
```

$\mathcal{T}$ now makes the always-present answer only about a name the function actually
**binds** (collected by route #46's existing pre-scan walk). A parameter, a `self.<f>` field
and every non-name operand get the same type-preserving `pycsl_none_str` opaque that route #50
installed one arm above, so this adds **no new model**.

**The `int` path already answered this way and `str` was the odd one out.** The `s: int` and
`s: bool` spellings of the same file FAIL CLOSED today — they reach route #44's opaque
`pycsl_none` — so this makes the string path consistent with a model the tree has been paying
for all along, rather than introducing a new cost.

**It is live in the mirror, in the emitter's own contract parser.** `expect_name(self,
val: str = None)` declares `str` and DEFAULTS TO `None`, so its guard emitted

```whyml
    (if true && (not (at_name self (cons py_val empty))) then 1 else 0)   (* before *)
    (if (not (str_eq_op py_val pycsl_none_str)) && (not (…)) then 1 else 0)   (* after *)
```

— the `val is not None` conjunct was the literal `true`, i.e. **deleted**, and every
`expect_name()` call with no argument takes exactly that path.

**Measured**: 1 of 53 mirror emissions moves (2 lines, the file above), all 53 still emit and
all 53 type-check; 0 of 903 pre-existing corpus emissions move; both fidelity planes
byte-identical. Witness `1102` is the precision guard that keeps this a **narrowing** rather
than a retreat — a local bound to a literal in the same function still gets the DECIDED
answer, and a repair that made every string `is None` opaque would lose it.

**Shape (a) is closed the other way round — by refusing the lie, not by weakening the
caller.** A local bound from a call *is* a bound name, so $\mathcal{T}$ should keep deciding
with it; what makes that decision honest is the callee's annotation being TRUE. Module 4's
`PYCSL-SEM-RETANN` therefore refuses a function annotated `-> str` that can `return None`,
scoped to `-> str` because the `-> int` spelling already fails closed. **That scope claim
was measured for the EXPLICIT `return None` only, and route #198 (gen #30) found the
spelling it had not run:** a BARE `return` in an int-returning function lowered to
`raise (Return 0)`, so `#@ ensures \result == 0` PROVED while CPython answers `None`
(§T.5.12h). The check's own helper `_returns_literal_none` counts both spellings; Module 6
did not. Repaired at the emitter, so the scope claim is true again — this time for both
spellings, and this time both were measured.

**The same lie one argument position to the left: route #200 (gen #30).** A `str` actual
passed to a parameter the callee DECLARES `int` is the argument-side twin of a `-> str`
that returns `None` — Python does not enforce the hint, and the model believes it. There it
is worse than a deleted branch: `_coerce_dotted_args` replaces the string by
`stable_hash` of its own text, so a callee contract that NAMES that integer is DECIDED.
`stable_hash` ships in this repository, so the integer is one line to compute:
`def callee(p: int)` with `ensures p == 747471683 ==> \result == 1` — true of its own
body — called as `callee("a")` emitted `(callee 747471683)` and PROVED `\result == 1`
while CPython answers 2, with the TRUE twin REFUSED (witnesses `1697`/`1698`). Module 4's
`PYCSL-SEM-STRARG` refuses it. **Route #202 (gen #30) then corrected the key, an hour
later.** Keying on the DECLARED annotation was chosen because the 46 sites where a string
literal reaches an `int` param across the 53 mirror emissions are `int` by ERASURE — and
that population is exactly the hole: an un-annotated parameter is erased to `int` and gets
the same hash, so `def callee(p) -> int` carrying `ensures p == 747471683 ==> \result == 1`
called as `callee("a")` still PROVED. The refusal now keys on the condition that actually
matters — **the callee's own contract MENTIONS the parameter** — because that is the only
way a nameable hash can reach a caller's proof: a callee's VC quantifies over `p`, so a
contract that does not name `p` cannot transmit the substitution. The same change covers
the KEYWORD slot (the IR keeps keyword actuals in `node["keywords"]`, so `callee(p="a")`
walked past a check that read `args` — witness `1703`) and SKIPS a vararg formal, which
packs every remaining actual into one sequence (witness `1704`; without it, corpus `0931`'s
`member_of("+", "+", "-")` would be refused). Witnesses `1697`/`1698`/`1701`/`1702`.
Censused clean on 1628 corpus files and 53 mirror files. The collection spellings of that
same arm were already closed by routes #194/#195.

**And that lie was live in the emitter's own `if`-statement handler.**
`stmt_control_flow::_try_union_is_none_match` declared `-> str` and returned `None`, so its
`return None` emitted as `raise (Return_str "")` — **`None` as the empty string, on the
RETURN path**, which is route #50's defect in the one place route #50 did not reach — and its
caller's `if union_match is not None:` emitted as

```whyml
    if true then begin                      (* before *)
    if (not (match !union_match with Arm_0_None -> true | _ -> false end)) then begin
```

The "the pattern does not apply, fall back to the normal `if` lowering" path was **deleted**,
so every proof of `_handle_if_stmt` ran over a strict subset of its reachable states.
Correcting the annotation to `Optional[str]` makes the return a faithful union and the
caller's test a real discriminant: 1 of 53 mirror emissions moves (75 lines, that file), all
53 emit and type-check, and 0 of 905 corpus emissions move.

**Stated residue**: a callee that returns `None` IMPLICITLY, by falling off the end, has no
`return None` for that check to see; it fails closed today, but by a TYPE ACCIDENT (Why3
expects `()` where a `string` is supplied) rather than by design.

---

### §T.5.12s  `if <dict>:` was decided TRUE, and the justification described a shape the arm outgrew

A dict/set is modelled as a `map` with no int value, so the usual `<> 0` truthiness coercion
would be a Why3 TYPE ERROR. $\mathcal{T}$ answered the literal `true` instead, justified — in
the emitter's own comment and in `bin/check-type-keyed-constant-answers.py`'s baseline — as
*"the over-approximation that lets the real check, the `in` that follows, happen"*. The same
baseline NAMED the risk it was taking: *"an EMPTY dict is falsy in Python, so a contract that
depends on the else branch would be proved over a subset."*

It does. With a real postcondition instead of `ensures True` (route #55, witnesses
`1104`–`1107`):

```python
    def probe(self, d: Dict[int, int]) -> int:   #@ ensures \result == 7
        if d: return 7
        return 0                    # `o.probe({})` returns 0 in Python. PROVED anyway.
```

```whyml
    if true then begin raise (Return 7) end else begin raise (Return 0) end
```

The arm Python takes for an empty dict is **unreachable**, so the postcondition is proved over
a STRICT SUBSET of the reachable states. This is §T.5.12r's sentence at a different type and a
different connective: **decided from a TYPE where only a value fact could justify it.** The
`set` spelling proves too; a `list` fails closed, because a list carries a length model.

**The justification was right about the shape it described, and the arm had outgrown it.** On
a BARE guard there is no `in` that follows at all. So the guard is now the shape itself:
`true` is answered only where this truthiness test is the **left conjunct of an `and` whose
other conjunct is a membership test on the same name** — there an empty map makes that test
False anyway, so `true` is EXACT rather than an over-approximation — and every other dict/set
present-guard gets a per-name opaque `bool`.

**Measured, and the measurement is why the repair has this shape rather than a blunter one.**
The blunt version (opaque everywhere) was built first and REFUSED after reading its emission
diff: it moved the one live site in the tree — `module6_whyml/expressions.py`'s
`if subst and name in subst:` — where `true and (name in subst)` is exactly what Python
computes, so the blunt fix would have LOST precision to correct nothing and owed a re-proof of
one of the two slowest mirrors. The shape-sensitive repair leaves that site byte-identical:
**0 of 53 mirror emissions and 0 of 905 corpus emissions move, and no re-proof is owed.**
Witness `1107` is the precision guard and is negative-tested both ways — it proves with the
subsumption exemption and fails without it.

---

### §T.5.12j  A chained comparison in a `#@` clause is a CONJUNCTION

`0 <= x <= 3` inside a `requires`, an `ensures`, a `loop invariant` or a class invariant was
lowered **left-associatively** to `((0 <= x) <= 3)` — a `bool` compared to an `int`. Why3
type-rejects that, so the clause failed *closed* rather than proving something wrong; but it
did not mean what it reads as, and `0 <= i <= 3` is the canonical loop-invariant idiom.
The unsound direction was probed first and is closed too: `ensures False == False == True`
emits `((0 = 0) = 1)` and is type-rejected on the same grounds.

$\mathcal{T}_e$ now rewrites a comparison whose **left operand is itself a comparison** into
the conjunction Python means: `a op1 b op2 c` becomes `(a op1 b) ∧ (b op2 c)`.

**The expansion is safe in a clause in a way it is not in program code**, and that is why it
needs no machinery. §T.5.11's `desugar_chained_comparisons` (route #33) has to bind the
middle operand with a walrus, because Python evaluates it **exactly once** and a program
operand may have effects; a contract expression is *pure by construction*, so mentioning the
middle operand twice is semantically free — no temporary, no purity allow-list.

**Measured byte-inert on both planes** — 0 of 875 corpus emissions and 0 of 53 mirror
emissions — because not one `#@` clause in the tree writes a chain, precisely *because* it
never worked. Every existing clause is already in the expanded `0 <= i and i <= n` form.
Witnesses `1074` (the capability, in both a `requires`/`ensures` pair and a `loop invariant`)
and `1075` (its refutation: the same chain on a body that violates it must still fail, so
the expansion is not collapsing to `true`).

`pycsl-reference/0969`'s docstring used to assert that "the `#@` annotation grammar has
always expanded chains correctly", citing `0865`. That was false and is corrected in place:
`0865` is written in the already-expanded form.

---

### §T.5.12t  A PLACEHOLDER HAS EVERY PROPERTY ITS REPRESENTATION HAS

Four routes in gen #30 (#193, #194, #195, #196) and one more a day later (#197) are one
defect wearing five costumes: **where the model does not know a value, it must not name
one** — and a stand-in named for one purpose answers every question its representation can
answer.

| where | the stand-in | the question it answered wrongly | now |
|---|---|---|---|
| an iterable the IR cannot represent, at an `array int` param (#193) | `(Array.make 1 0)` | `sorted_1`'s `Array.length result = Array.length a` made `len(sorted(x for x in [3,1,2]))` prove `== 1` | `any (array int)` |
| an array/map actual at an INT-ERASED param (#194) | the literal `0` | the callee's `ensures p == 0 ==> \result == 1` read it | `(any int)` |
| `[]` at an INT-ERASED param (#195) | the literal `0` | same contract, `self.f([])` proved `\result == 1` (`[] == 0` is False) | `(any int)` |
| `[]` at an `array int` param (#196) | `(Array.make 1024 0)` | `\result == \length(ns)` handed the caller `1024`, and CPython's own answer 0 was REFUSED | `(Array.make 0 0)` — FAITHFUL, not opaque |
| `getattr(o, "a", 0)` on an UNKNOWN-typed `o` (#197) | the DEFAULT | the body read it and the contract read `\result`; the emission even warned `unused variable o` | a PER-SITE opaque |

**THE PROBE THAT FOUND FOUR OF THEM, stated once because it is the transferable part:** give
the callee a contract that is **TRUE OF ITS OWN BODY** and that **READS** the property the
substitution changes; call it with the substituted-away shape; run CPython. A callee with
`ensures True` hides every defect of this family completely, which is why the call boundary
survived 190 routes unprobed.

**Two distinctions the repairs turn on, and both cost a wrong first attempt:**

* **OPAQUE is not always the right answer — sometimes FAITHFUL is.** `[]` really does have
  length 0, so #196's repair is the genuinely empty array, and witness `1690` now proves
  `len([]) == 0` at a call boundary, which the model could not prove before. A repair that
  only made the length undecided would have left a true fact unprovable.
* **A PER-SITE opaque is not the same as `any`.** `any` is fresh at every evaluation; a
  per-site opaque is stable, so two reads of the same expression agree. #197's first version
  used `any` and the emission census refuted it — it would have replaced route #47's existing
  per-site opaques and lost that equality for nothing.

And one accident worth keeping: a spelling can be shared. Before #191 the Python `None` and
the integer `0` both lowered to `"0"`, so a lift recognising `None` **by that spelling** was a
coincidence, not a rule. #191 broke the coincidence in the safe direction (a missed lift, a
loud type error) and #192 is the same break read the other way.

**Route #201 (gen #30): the same function's TAIL, and the second half of the same false
defence.** `_array_coerce_arg` opens by explaining itself — "a length-1 placeholder array
works because the abstract vals have no axioms about their input contents". #193 falsified
the CONTENTS-vs-LENGTH half of that sentence and repaired the `"0"` arm. The other half —
*the only consumers are abstract vals* — was still standing, and it is false too: a
**user-declared `List[int]` parameter** reaches the same coercion.

| program | model (before #201) | Python |
|---|---|---|
| `def callee(p: List[int])` reading `len(p) == 1`, called `callee("ab")` | `(callee (Array.make 1 0))`, `\result == 1` **PROVED** | `len("ab")` is 2, so **2** |
| the same with the TRUE claim `\result == 2` | REFUSED | **True** |

The tail now answers `(any (array int))` like the arm above it. Censused before the change:
the placeholder fires **0 times** across all 1624 corpus files and all 53 mirror emissions —
the device that proved a false contract about a user's program was used by nothing this
repository verifies. Witnesses `1699` (carrier) and `1700` (a genuine 3-element list actual
still arrives with the length it has, so the repair is a narrowing and not a retreat).

### §T.5.12h  `None` is NOT the integer 0 in a VALUE position

`None` USED TO LOWER to the literal `0`, and that was the **Optional convention** the whole
union/carrier machinery is built on: `x is None` on a `Union`-typed local is a constructor
check, on an `iropt_ir`/`iropt_str` carrier it is a `match` on the absent arm, on an
`option`-returning call it is a `None`/`Some` discriminant, and a dozen more recognizers sit
above the fall-through. Under that convention the model is internally consistent. What was
not consistent is what happened when NONE of those recognizers fired (route #44, witnesses
`1058`–`1064`):

| program | model | Python |
|---|---|---|
| `x = None; if x == 0:` | taken | `None == 0` is **False** |
| `x = 0; if x is None:` | taken | `0 is None` is **False** |
| `x = None; return x + 5` | `\result == 5` | **TypeError** — no value at all |
| `#@ ensures \result == None` on `-> int`, body `return 0` | **PROVED** | `0 == None` is **False** |

The fourth needs no branch and no unusual body: any function returning `0` could carry that
contract and be "verified", because `\result == None` lowered to `result = 0`. A contract
that is false of its own program, proving directly, is the worst end of this family.

**Route #191 (gen #30) finished the job: the `None` LITERAL ITSELF is the opaque, in every
position.** Route #44 intercepted the *reads* — a `None`-bound local, the `is None`
fall-through — and route #184 the two literal *builders* (a `None` element of a list literal,
a `None` value of a dict literal). The typed `NoneExpr` leaf of `_expr_to_whyml` still
answered the int `0`, and every STORE reached it, so

| program | model (before #191) | Python |
|---|---|---|
| `xs[0] = None; xs[0] == 0` | **PROVED** True | **False** |
| `d["a"] = None; d["a"] == 0` | **PROVED** True | **False** |
| `b.v = None; b.v == 0` (post-construction) | **PROVED** True | **False** |
| `xs.append(None); xs[0] == 0` | **PROVED** True | **False** |

The leaf now answers `pycsl_none` like its dict-shaped twin, so all four are UNDECIDED
(witnesses `1673`–`1676`), an ordinary integer store is untouched (`1677`), and — because the
opaque is ONE shared constant — `b.v is None` after a `None` store still PROVES (`1678`).

The cost was two lifts that had been recognising the Python `None` **by the WhyML spelling
`"0"`**: `_option_record_param_upgrade`'s sibling, which lifts an omitted / explicit `None`
actual into an `Optional[<record>]` parameter's `option` type, and the `_union_*` twin beside
it, which substitutes a synthesized union's nullary `None` arm. Both now recognise
`pycsl_none` as well. Read the other way, those lifts also turned a **genuine integer `0`**
into the option's `None` — `self.tag(0)` emitted `(parser__tag self (None: option tok))` and
`self.expect("RPAREN", 0)` emitted `(Arm_0_None : _union_expect_0)`, so a callee contract
`ensures start == None ==> \result == 1` discharged in the caller and `\result == 1` PROVED
while CPython returns 2. That is **route #192**, closed in the same generation: the `"0"`
spelling is dropped from both lifts, which after #191 costs the legitimate actuals nothing
(an omitted optional argument and an explicit `None` both arrive as `pycsl_none`) and turns an
integer actual into a type error — refused rather than answered wrongly.

**A read of a `None`-bound local is now the opaque `val function pycsl_none : int`** — route
#41's device one singleton later — and the `is None` fall-through compares against that same
constant. Two things about the granularity, because it is a semantic decision each time and
not a convention:

* **Shared, not per-name.** Route #41 needed per-name constants because an erased generator
  and an erased tuple are *different objects*, so one constant would let the model prove
  `x == y` for two of them. `None` really is one object, so the shared constant is faithful
  and keeps `x = None; y = None; x == y` provable — Python's answer (`1063`).
* **Truthiness stays decided.** `bool(None)` *is* `False`, so the literal `0` is the correct
  truth value; `_to_bool` answers `false` rather than refusing or going opaque (`1064`).
  Route #41 refuses there because a generator is always truthy while the model reads `0` —
  the opposite situation. One dict, three different truthiness answers, and the record's
  suffix is what distinguishes them.

The fall-through takes a **faithful arm first**: a `\result` whose function declares a plain
scalar return can never be the `None` singleton, so `\result != None` is `true` and
`\result == None` is `false`. `pycsl-reference/0229` had been discharging that clause only
*by accident*, as `result <> 0`. **That arm is gated on the Python return annotation and not
on the WhyML return type**, and the gate is load-bearing: an `Optional[τ]` return degenerates
to the WhyML type `int`, so the WhyML type alone would have fired on
`_Parser.accept_op` (`ensures \result != None ==> self.i > \old(self.i)`) and handed every
*caller* an unconditional guarantee that is false on its `return None` path.

**Route #198 (gen #30): the LAST spelling of the same statement.** After #191 the `None`
*literal* is the opaque everywhere — but Python has a second spelling of `return None`, the
**bare `return`**, and it never goes through the literal at all: `_handle_return_stmt` sees
`stmt.value is None`, writes the unit `"()"`, and an int-returning function then collapsed
that to the literal `"0"` on its way into `raise (Return 0)`.

| program | model (before #198) | Python |
|---|---|---|
| `def f(x: int) -> int:` / `if x > 0: return` , `ensures \result == 0` | **PROVED** | `f(1)` is `None`; `None == 0` is **False** |
| the same, `ensures \result != 0` (TRUE of Python) | REFUSED | **True** |
| the same program spelled `return None` | REFUSED (correct, via #191) | — |

One statement, two spellings, two different answers. The bare spelling now emits the same
`pycsl_none`, which is why the repair needed no new device: it made the two spellings agree.
`(any int)` would have been sound too and was rejected for #191's own reason — `any` is fresh
at every evaluation and cannot keep two `None`s equal, while the shared constant can.
Witnesses `1693` (carrier) and `1694` (a real early return still carries its value).

The `-> str` spelling of the same program is REFUSED at the FRONT END instead, by route #51's
`_check_scalar_return_annotation`; that check's own scope argument — "`-> int` fails closed
today" — had been measured for the explicit `return None` only, and this is the spelling it
had not run.

**Route #203 (gen #30): the f-string arm underneath #199's.** `_handle_fstring_expr` has
three lowerings — a faithful `string` concat chain when every segment is string-typed, the
same chain via `int_to_string` inside a `@mutable_state` class or a `-> str` function, and
an INT-MODEL joiner underneath both. In that joiner a multi-part f-string is wrapped in
`str_concat` (an abstract op with no axioms) and a string-typed part in `str_hash_op`, so
both are opaque. A **single-part** f-string whose part is not string-typed returned the part
itself:

| program | model (before #203) | Python |
|---|---|---|
| `n = 5; s = f"{n}"; s == "5"` | `s := !n`, then `!s = 1359629258` — **decided FALSE** | `f"{5}"` IS `"5"`, so **True** |

so `#@ ensures \result == 2` PROVED and the TRUE twin was REFUSED. This is a wrong
*decision*, not a lost value. The single-part case now answers a **value-keyed opaque**
(`val function str_of_int_hash`), so no literal's hash is provably equal to it and
`f"{n}" == f"{n}"` still proves (witnesses `1705`/`1706`). Scoped to `len(parts) == 1`
because that is the only shape that escaped: censused at **0** occurrences across the 1630
corpus files, the 53 mirror files and `pycsl_lib`, against 575 f-strings in the mirror
overall.

**Route #291 (gen #37): the value-keyed renderer was keyed on the INT model, where `True` IS 1.**
`b = True; x = 1; f"{b}" == f"{x}"` PROVED True (CPython `"True"` vs `"1"`), and so did `f"{b!r}"`,
`f"{b:}"` (empty spec) and `f"{True}" == f"{1}"`. The two value-keyed families —
`str_of_int_hash` (single-part f-string) and `pycsl_format_<c>_i_*` (a `FormattedValue` with a conversion,
an empty spec, or a computed spec) — now classify the int-model operand: SHOWN bool (bool literal,
comparison, `not`, `bool(...)`, a `bool`-typed name or `-> bool` call; an unannotated local whose every
plain binding is one of these) renders through `str_of_bool_hash` / `pycsl_format_<c>_b_*`; SHOWN exact
int (int literal, `len`/`int`/`abs`/`ord`/`hash`/`sum`, `-`/`//`/`<<`/`>>`/unary `-`/`~`, an `int`-typed
name or `-> int` call — BUILTIN-EXACT) keeps the `i` key; anything else renders through a program `val`
(`str_of_value_op`, `pycsl_format_<c>_u_*`), fresh per evaluation. A NON-EMPTY literal spec with no
conversion keeps the `i` key for a bool too: `format(True, ">5") == "    1"`, CPython formats it as the
int. Witnesses 3346-3350 (FAIL), controls 3351 and 1706 (PASS).

**Route #292 (gen #37): legacy cited struct laws are keyed on the exact format.**
`UnixFs.Struct.{i2,i18,i1a1}.round_trip` are stated over `struct_{pack,unpack}_<slot_id>`, and `slot_id`
records only WhyML slot types, so `>??`, `<ff`, `<dd` shared `struct_pack_i2` with `>HH` and the
unguarded round-trip PROVED `\result == x0` (CPython `roundtrip(5, 0)` is `True`). Each law now names
only its documented format (`>HH`, `>IHHHHHII10Ixx`, `>H30s`); any other format of that shape lowers to
`struct_{pack,unpack}_<id>_h<hex(fmt)>`, which no law names (3352-3354 FAIL, 3355 PASS). Every cited
`#@ proof` lemma is listed by `--soundness-report` as a TCB entry (JSON `cited_lemmas`).

**Route #293 (gen #37): `os.path.relpath` is impure.** CPython's `posixpath.relpath` calls `abspath`,
which reads the cwd; it was a `val function`, so `relpath("a", "/")` before and after `os.chdir` PROVED
equal. It is now a plain `val` like `abspath`/`realpath`/`expanduser`; the remaining `val function`
set (`basename`, `dirname`, `normpath`, `join`, the `split*` slots) is lexical in CPython (3356-3357
FAIL, 3358 PASS).

**Route #287 (gen #37): a lambda's body is censused like a comprehension element.** `sorted(xs,
key=lambda v: ...)` lowers to `sorted_perm_1 xs` and drops the key body, so `key=lambda v: 10 // v`
PROVED `no_exception \all` and, inside `try ... except ZeroDivisionError`, a length claim. Under an
active `no_exception` context (declared, or widened by a handler, route #171) a `Lambda` whose body
matches a `TRIGGER_EXPR_SHAPES` shape of an active exception is refused (3340-3344), exactly as route
#285 does for comprehensions; a raise-free key (`v + 1`) keeps its claim (3345).

**Route #294 (gen #37): the ν-typed empty base is for an EMPTY construction only.** The first
assignment of a dict local whose value type ν is not `int` (`string`, `hval`, `emit_ir`, `seq int`,
nested `map …`) replaced its lowered RHS with `(const (None: option ν))` WHATEVER the RHS was, so
`e: Dict[str, str] = func` (a parameter, a local, a call, `dict(func)`, a conditional) declared `e`
empty and `"name" in e` PROVED False (CPython True). `_emit_first_assign` now substitutes the empty
base only when the RHS is a dict literal (the fold puts its entries back on that base) or already
lowered to the int-typed everywhere-None map (`dict()`, the factory-form `defaultdict`/`Counter`, the
same empty value re-annotated); any other RHS is KEPT — it type-checks against ν (`ref func`) or is an
L3-tc error, a refusal (3430-3439). Census sibling: an emitter-local `Set[str]` (annotated, some
assignment `= set()`) lowered EVERY assignment to `StrSet.empty ()`; only `set()` is the empty set now,
any other RHS keeps its lowering (3442-3443 refused; 3441 controls PASS).

**Residue, stated rather than implied.** The record is *linear* — rebinding clears it — so a
`None` bound in one branch of an `if` and something else in the other walks past it. That is
`getting-better/open-routes/route46-none-branch-join.md`, which also records the *sticky*
repair that was built and refuted twice: `_to_bool` reads the same dict, and
"`bool(x)` is `False`" is a **path** fact that a flow-insensitive record cannot carry.

---

### §T.5.12i  NaN breaks the reflexivity of `==`, and opacity cannot repair it

`float(<str>)` has no model and lowers to an abstract `val py_float_1 (x0: int) : int` — an
opaque **int**. So `x = float("nan"); if x == x:` emitted `!x = !x`, which is *reflexivity of
`=`*: every value model has it, and NaN is the one Python value that does not (route #45,
witnesses `1065`–`1069`).

| program | model | Python |
|---|---|---|
| `x = float("nan"); if x == x:` | taken | `nan == nan` is **False** |
| `x = float("nan"); y = x + 1; if y == y:` | taken | still NaN — **False** |

**This is the first route in the campaign whose standing repair does not apply.** §T.5.12d,
§T.5.12e and §T.5.12h all closed a wrong-value erasure by making the value *opaque*. Here the
value was already opaque and was still equal to itself: an opaque constant satisfies `c = c`.
Opacity does not repair a broken equivalence relation.

What repairs it is that NaN's comparison semantics are **totally determined**: every ordering
and `==` is False and `!=` is True, whatever the other operand, *including the same NaN*. So
$\mathcal{T}_e$ lowers a comparison with a NaN operand **exactly** — `false` for `== < <= >
>=`, `true` for `!=` — rather than refusing it or making it undecidable. **The fix therefore
improves completeness as well as soundness**, which is the opposite of the usual trade:
`x != x`, `if x:` and `x < 1` are all *true* of the program, all unprovable before, and all
prove now (`1067`–`1069`).

Two details that are decisions rather than conventions:

* **Arithmetic propagates; comparisons do not.** IEEE 754 makes every arithmetic operation
  with a NaN operand NaN, so `y = x + 1` records `y` as NaN too (`1066`). A comparison yields
  a `bool`, so it stops the propagation. A fix that recognized only the direct `float("nan")`
  local would have been the same mistake one operator later — the lesson `1044` records for
  route #41 and `1054` for route #42.
* **`bool(float("nan"))` is `True`** — NaN is not zero — the exact opposite of `None` in
  §T.5.12h, and the third distinct truthiness answer the one erased-locals dict now carries
  (refuse for a generator, `false` for `None`, `true` for NaN).

A genuinely `float`-annotated operand is **not** affected: `f(a: float) -> if a == a` already
failed closed, because that routes through the `real` comparison path. The defect was
confined to the `float(<str>)` constructor's degeneration to `int`.

---

### §T.5.12g  `is` is NOT `==`, and the bool singleton proved it

`_PY_OP_MAP` mapped `ast.Is` -> `"=="` and `ast.IsNot` -> `"!="`, so by the time
$\mathcal{T}_e$ saw a comparison the distinction between *identity* and *equality* was
already gone. Separately, `_handle_binop`'s documented **bool-as-int convention** rewrites
a `Bool` literal operand of `==`/`!=` to `1`/`0` (this is what makes the formal-test idiom
`#@ ensures \result == True` lower correctly against an int-encoded `\result`). Each
convention is defensible alone. Together they made `is` and `==` *the same operator* on a
bool literal, and Python says they are not — `is` is object identity against a **singleton**,
and a genuine `int` is never the `True` object (route #42, witnesses `1053`-`1055`):

| program | model | Python |
|---|---|---|
| `x = 1; if x is True:` | taken | `1 is True` is **False** |
| `x = 0; if x is False:` | taken | `0 is False` is **False** |
| `x = 1; if x is not True:` | **not** taken | `1 is not True` is **True** |
| `x = 1; if x == True:` | taken | `1 == True` is **True** — *correct*, the control |

The last row is what localizes the defect: value equality was right all along.

**The IR now has a distinct `is` operator.** `ast.Is` lowers to `"is"` and `ast.IsNot` to
`"is not"`, and `Module5_IREmitter.generate_json` — the single choke point *both* Module 5
entry paths go through, `pycsl.py`'s pipeline and `ir_resolve.resolve`'s dependency
sub-pipeline — narrows the op back to `"=="`/`"!="` while recording the identity fact in an
**additive** `py_is` key. Every existing recognizer (the `is None` union and
optional-carrier paths, the `is Ellipsis` `PVEllipsis` arm, `_optfield_guard_name`,
`recognize_collect_field_sites`, every `op == "=="` test in Module 6, `ir_scanner`,
`auto_trust`, `types`) therefore sees exactly the string it saw before, and the corpus
emission is byte-inert **by construction** — the same additive-marker device route #40 used
for `py_ellipsis`.

`_expr_to_whyml` is the one consumer of `py_is`, and it applies a **whitelist**:
`X is True` / `X is False` is admitted only when the emitter can *show* `X` is a Python
`bool` — a bool literal, a comparison or membership result, a `not`, or a local the symbol
table types `bool`. Everything else is refused (`PYCSL-R42-IS-BOOL-SINGLETON`). The
whitelist direction is the point: a type-directed *blacklist* ("refuse when the operand is
an int-typed `Var`") closes the table above and leaves every `Call`-valued and every
unannotated operand unrefused — an under-approximation keyed on a partial resolution, which
is precisely the mistake routes #39 and #41 were about. Witness `1057` exercises the
admitted arm, so a later narrowing of the whitelist to nothing goes red rather than passing
as a "fix".

The refusal sits in $\mathcal{T}_e$ and **not** in the front end, and that placement is
load-bearing: a front-end refusal walks every function, including the eighteen
`classify(...) is not False` / `r is True` tri-state sites in the self-annotation mirror's
own `module6_whyml/functions.py`. Those sites' `Optional[bool]` *is* modelled — by the
bespoke `(bool, bool)` lowerings in `module6_whyml/generic_fold.py` — and their bodies never
reach the generic expression lowering, so the whitelist sees exactly the sites the generic
path actually decides.

**Residue, stated rather than implied.** Only the *bool* singleton is closed. `is` against
anything else still narrows to `==`: `is None` keeps its own load-bearing handling, `is ...`
/ `is Ellipsis` fail closed through route #40's opacity, `x is y` on equal small ints agrees
with CPython's constant folding, and the object-identity shapes (`[1] is [1]`, `C() is C()`)
fail closed only *by accident*, on a Why3 type error rather than a refusal. A completeness
fix could remove that accident at any time. Carrying `py_is` all the way into a genuine
identity relation is the reopening capability.

---

### §T.5.12e  An ERASED local is opaque on every read, not just in a guard

A local bound to a **generator expression**, a **non-empty set literal**, a **non-empty
tuple literal** or an expression the model does not represent is emitted as the literal
`0`. Routes #25/#26/#27 refused its **truthiness** in `_to_bool`. That refusal was placed
where the defect was *visible* — the guard — and not where the erasure *is*, so every
other consumer of the same local stayed exploitable (route #41, witnesses `1041`–`1045`):

    x = (i for i in [1,2,3]); if x == 0: return 7   # `\result == 7` PROVED; Python: 0
    x = {1,2,3};              if x == 0: return 7   # PROVED; Python: 0
    x = (1,2);                if x == 0: return 7   # PROVED; Python: 0
    x = (i for i in [1,2,3]); if x  < 1: return 7   # PROVED; Python: TypeError
    x = (1,2);                return x + 5          # `\result == 5` PROVED; Python: TypeError

$\mathcal{T}_e$ now lowers a **read** of such a name to a per-name opaque
`val function pycsl_erased_<x> : int` with no defining axiom, which closes all five at
once. **Per-name matters**: one shared constant would let the model prove `x == y` for
two distinct erased locals, trading one unsoundness for another. The **binding** is
untouched (`x := 0` still), so no statement emission moves, and `_erased_truthy_locals`
is cleared on rebinding, so `x = (1,2); x = 5; return x` is unaffected.

The `_to_bool` refusal of §T.5.13 is kept: with opacity the guard would merely be
*undecidable*, and a refusal that names the cause is a better answer than a silent
"cannot prove".

**The EMPTY literal is recorded too** (witness `1046`). Routes #25/#26/#27 recorded a
local only when the set/tuple literal was non-empty, and that guard is exactly right for
*truthiness* — an empty container **is** falsy, so `0` is the faithful truth value. It is
wrong for the *value*: `() == 0` is False in Python and the literal `0` made it decidably
true. The record now carries a `#empty` suffix that `_to_bool` skips, so the truthiness
stays faithful and unrefused while the opaque read fires on every recorded name. The
price is measured and accepted: `x = (); if x:` no longer proves, because the read is
opaque.

---

### §T.5.13  List locals: truthiness, `len`, and the constant folds

A list LOCAL is lowered to a Why3 `array int`, and three facts about it are answered from
emitter-side metadata rather than from the array: its **truthiness** (`_array_locals`), its
**length** (`_known_collection_sizes`) and its **elements** (`_known_collection_elements`).
All three were unsound until relaunch #45 and all three are now bounded.

**Truthiness.** `if <list local>:` used to emit `true` for every array local, on the stated
grounds that the array is *always allocated*. Allocation is not truthiness: `[]` is **falsy**
in Python, so `a = []; if a: return 1; return 2` proved `\result == 1` from the emission
`if true then 1 else 2` while Python returns 2 (route #31, witness `pycsl-reference/1015`).
`Array.length a <> 0` is not the repair on its own — an empty list literal lowers to the
placeholder `Array.make 1024 0`, so the Why3 length of the one case that matters is 1024. The
faithful answers are now emitted where the model has them: the statically known literal size
for an unconditionally bound local, the sidecar `X_len` ref for an append target, and
`Array.length <> 0` for an array-typed parameter or element-typed local. Where none applies
the truthiness is **refused** (`PYCSL-R31-UNMODELLED-LIST-TRUTHINESS`). Witness `1016` proves
the faithful capability in both directions.

**The two constant folds are a CACHE, and until relaunch #45 they had no invalidation.**
`_known_collection_elements[a] = {0: "5"}` is written when the literal is bound and was
never removed when `a` was written to, so the read folded to the literal whatever happened
in between. `a = [5]; a[0] = 9; return a[0]` proved `\result == 5` (route #34, witness
`1017`); so did an alias then a store (`b = a; b[0] = 9`, `1018`), an alias then an append
(`1019`), a slice assignment (`1020`) and a CALLEE that mutates the list it was handed
(`1021`). The emitted WhyML for every one of those stores is *faithful* — `let b = a in
b[0] <- 9` really does mutate `a`, because Why3 arrays are references. It is the read that
never consulted it.

`_reset_function_state` now runs a **pre-pass over the whole function body** and refuses to
register a fold for any name it sees mutated or aliased anywhere: an indexed / slice / `del`
store, an assignment of the bare name to another name, any method call on the name, or the
name passed to a call that is not one of a short list of non-mutating builtins. The pre-pass
is required rather than tidy — sequential invalidation would still fold a read that sits
*before* the store in a loop body, because on every iteration but the first the store has
already happened. A plain indexed store poisons only the ELEMENT fold, which keeps the
deliberate dict-store size tracking working.

**"An indexed store does not change the length" is TRUE FOR LISTS AND FALSE FOR DICTS**, and
that premise — which is what this paragraph used to assert — was route #60. `a[0] = 9` leaves
`len(a)` alone; `d[k] = v` ADDS A KEY whenever `k` is absent. The size tracker resolved it by
incrementing on every store SITE, so it was blind to key equality (`d={1:1}; d[1]=2` folded 2,
Python 1), to a SYMBOLIC store key (undecidable at emission), to the CALLER's dict (a store on
a dict PARAMETER folded `len` to 1 while Python answers caller-size + 0 or 1), to REACHABILITY
(a store under `if c > 0:` counted unconditionally) and to ITERATION COUNT (a store in a loop
body counted ONCE, so `d={}; for i in range(n): d[i]=i; len(d)` proved `\result == 1` for
every n). Seven carriers each proved a FALSE claim while the true twin stayed Unknown.

$\mathcal{T}$ now gives the dict-store tracker a WHITELIST, per route #42's rule: the size
fold survives stores only where the emitter can SHOW the post-store size — the name bound
EXACTLY ONCE to a top-level dict literal, EVERY store at the function's TOP LEVEL (so
reachability and iteration count are not in question), EVERY store key a LITERAL, and the
literal's keys and the store keys PAIRWISE DISTINCT under Python's own key equality (the same
normalisation route #54 gave the literal fold, so `{1:1}` then `d[True]=2` is a repeat).
Anything else is added to `_fold_unsafe_sizes` in `_reset_function_state`, never registered by
`_track_collection_metadata`, and `len(d)` falls through and FAILS CLOSED — which is what
`len(d)` on a dict parameter WITHOUT a store already did. Negative witnesses `1133`-`1139`,
positive controls `1140`-`1142`. Byte-inert over both corpora. Witness `1022` shows the
fix removes the wrong answer without removing the right one: `\result == 9` now proves.

**The two constant folds are valid only for a single, unconditional binding.** Both maps are
keyed by the local's *name* alone and were written in emission order, so a name bound to a
literal in one arm of a conditional handed its size and its contents to every path:

    if c == 0: a = [9, 9, 9]          if c == 0: a = [7]
    else:      a = [1, 2]             else:      a = [9]
    return len(a)     -> folded 2     return a[0]     -> folded 9
    Python (c == 0):  3               Python (c == 0): 7

Both proved (routes #32 / #33, witnesses `1013` / `1014`). A second binding of the same target
now **poisons** both maps, and the read falls through to the real array — which, for a name
bound only inside the arms, Why3 correctly rejects as out of scope. Recording the last literal
seen, which is what the emitter did, is the one answer that is wrong on every path but one.

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
| `[e0, e1, …]` (non-empty, HOMOGENEOUS) | `(let _alit = Array.make N e0 in _alit[1] <- e1; …; _alit)` | Body | Concrete array literal (`array int`/`string`/`real`/`<record>` per the uniform element type; a HETEROGENEOUS literal is REJECTED — §WL-04g) |
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

#### The four array atoms are VALUE-MODEL ONLY — refused under `typed` / `store`

The lowerings above — `\is_sorted`, `\array_eq`, `\permutation` and `\sum`, and
equally `\length2d` and `\valid2d` — are stated for the **value-semantic** memory models (`hoare`, the default, and
`concurrent`). Under the heap models (`--memory-model typed` and `--memory-model
store`) an array is a `loc` base plus a length companion and the element read is
`Map.get !int_mem (base + i)`, so none of the four formulas above is even well-typed:
they are written over a Why3 `array int` value.

Until relaunch #45 the emitter did not say so. Each handler was written
`if self._value_semantic: <the formula above>` with a **fall-through literal** —
`true` for the three predicates and `0` for `\sum` — so under `typed`/`store` a
postcondition `\is_sorted(arr, 0, 3)` emitted as `ensures { true }` and **a contract
false of the program was provable** (route #29; witnesses
`pycsl-reference/1004`–`1008`). $\mathcal{T}$ is now **partial** here: the pipeline
REFUSES all four atoms under a heap model with `PYCSL-R29-HEAP-SPEC-ERASURE`, before
emission, on the resolved IR.

`false` was **not** an acceptable substitute for the erased literal: it is fail-closed
in an `ensures` and fail-**open** in a `requires`, where `requires { false }` makes
every goal of the function vacuously provable. Only a refusal is sound in every clause
position.

A faithful heap lowering is expressible and is the recorded reopening capability:
`\is_sorted(a, lo, hi)` is
`forall i. lo <= i < hi - 1 -> Map.get !int_mem (a + i) <= Map.get !int_mem (a + i + 1)`,
and `\array_eq` is the same shape over two bases plus their `_len` companions.
`\permutation` needs an uninterpreted predicate over `(loc, len)` pairs and `\sum` a
heap-indexed recursive function.

`\length2d` and `\valid2d` are refused on the same grounds one step earlier:
`_handle_length2d_expr` and `_handle_valid2d_expr` carry the identical
`if value_semantic: <formula>` / `return "true"` shape, and were masked under a heap
model only by `unbound type symbol 'matrix'` — an unrelated missing `use` that a
completeness fix could remove at any time. Pins `pycsl-reference/1009`–`1010`.

The one `return "true"` that is **sound** and stays is `\separated` under the *value*
model: Why3's region typing rejects an aliased array application outright ("This
application creates an illegal alias"), so two array parameters there really are
always separated.

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
| `s.lower()` / `s.upper()` | — | `str_lower_op`/`str_upper_op` : **deterministic** `val function`, `len s≥1→len result≥1` + IDEMPOTENCE (fold-marker predicate) ; **literal receiver constant-folded** (Python's own `str.lower`/`upper`) | `_handle_string_value_method` |
| `s.replace(p,r)` | — | `str_replace_op` : **deterministic** `val function`, `len p=len r → len result=len s` + not-contains identity (`p` nowhere in `s` ⇒ `result=s`) ; **all-literal call constant-folded** | `_handle_string_value_method` |
| `s or t` / `s and t` (BOTH `str`) | (spec: `&&`/`\|\|` boolean) | **body: string ITE over EMPTINESS** — `s or t` → `(if str_length_op s > 0 then s else t)`; `s and t` → `(if str_length_op s > 0 then t else s)` (Python string truthiness is non-emptiness; the result is the operand itself, `string`-typed, NOT a bool) | `_handle_binop` |

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

**`lower`/`upper` — deterministic + idempotent + literal-folded (cleared-string RESIDUALS item 1).**
`str_lower_op`/`str_upper_op` are now **deterministic** `val function`s (not fresh-per-call `val`s),
carrying, besides the sound non-emptiness law (`len s ≥ 1 → len result ≥ 1`), the UNIVERSAL sound
content law **idempotence** — Python `str.lower()`/`.upper()` are idempotent for *all* strings
(Unicode included) — encoded via a fresh "already-folded" marker predicate (`str_is_lowerf`/
`str_is_upperf`: the output is folded, and a folded input is a fixed point ⇒ `f(f s)=f(s)`), so **no
new `axiom`** and no self-reference. Determinism + idempotence prove `s.lower().lower() == s.lower()`
(driver 0791); distinct symbols keep `s.lower() == s.upper()` **Unknown** (no false collapse; driver
0793). A **string-literal receiver is constant-folded** by Python's own method, giving exact,
*full-Unicode-faithful* content (`"Hello World".upper() == "HELLO WORLD"`; `"ß".upper()` would fold to
`"SS"`). Residual (honest boundary): the per-char ASCII case-MAP on a **symbolic** string is not
modelled — it would require a code-point bridge (`chars : seq int`), an `is_ascii` contract predicate,
and `ord`-on-derived-subscript (a large new contract surface, zero corpus demand, and a codepoint
theory that risks slowing the heavy os/self-annotate sweep); full Unicode folding (`ß→SS`) is
inherently not per-char/length-preserving and stays out of scope on symbolic strings. The
SMT-feasibility of the sound core is recorded in
`test-suite/corpus/conformance/spikes/cleared-string-residuals.mlw` (AE + Z3, all content goals
Valid; the `lower s = s` sentinel correctly Unknown).

**`replace` — deterministic + not-contains identity + literal-folded (cleared-string RESIDUALS item 2).**
`str_replace_op` is a **deterministic** `val function` carrying two sound laws for CPython's
all-occurrences replace: (a) char-for-char `len pat = len rep → len result = len s`; (b) **not-contains
identity** — if `pat` occurs *nowhere* in `s` (stated as the negation of the substring-existential the
`in`/`not in` operator emits, so a driver `requires pat not in s` connects), then `result = s` (driver
0792). Empty `pat` is auto-excluded (it "occurs" at every index), matching CPython, whose empty-pat
`replace` **differs** from Why3 `replaceall` — so we deliberately do **not** pin the result to
`String.replaceall`. An **all-literal** call (`"a.b.c".replace(".","_")`) is constant-folded by Python.
Residual (honest boundary): the general grow/shrink CONTENT (single/multi-occurrence decomposition) is
**not soundly reachable** — Why3's `replaceall` has *no* content axiom beyond empty-pat/not-contains,
and CPython's all-occurrences semantics ≠ Why3's first-occurrence `replace` (whose
`replace_substring_indexof` decomposition we cannot borrow without proving single-occurrence). No
length law is claimed for grow/shrink (driver 0794 confirms the false length claim is rejected).

**Still opaque:** `strip` (`len result ≤ len s` only), `split` (list-of-strings), `.decode`/`.encode`
(codec, the bytes↔str boundary), `%`/f-string CONTENT, and all lexicographic code-point reasoning on
symbolic strings.

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

### §T.6.18  Operand evaluation order (route #307)

Python evaluates the operands of an operator, the receiver and arguments of a call, the
elements of a literal and the parts of an f-string LEFT-TO-RIGHT. Why3 evaluates the
arguments of an application (and the operands of an infix operator, and the components of a
tuple) RIGHT-TO-LEFT — measured on Why3 1.8.2: `sub (x := 1; !x) !x` is 1, and in
`(raise E) + (x := 1; !x)` the write happens before the raise. Emitted as one nested
application, `x - (x := 1) + 1` proved `\result == 1` (CPython 0).

$\mathcal{T}_e$ therefore sequences an n-ary program node (binary operator other than the lazy
`and`/`or`, string concatenation, subscript, slice, call with its receiver and keyword
arguments, tuple/list/set/dict literal, f-string) whose operand $k$ is EFFECTFUL — it
contains a walrus, a `yield`/`await`, or a call not known pure (a module function or `self.`
method whose contract is `assigns \nothing` with no `raises`, or a builtin / `str`-`dict` query
method no user function shadows):

$$\mathcal{T}_e(op(e_0,\dots,e_{n-1})) = \texttt{let } t_0 = \mathcal{T}_e(e_0) \texttt{ in } \dots \texttt{ let } t_j = \mathcal{T}_e(e_j) \texttt{ in } op(t_0,\dots,t_j,\mathcal{T}_e(e_{j+1}),\dots)$$

for the operands $e_i$, $i \le \min(k, n-2)$, that are not INERT (a literal, a unary operator
on a numeric literal, or a read of a local when the node contains no walrus) and are followed
by a non-inert operand. An operand with evidence of a mutable-container type (a dict/list/set
field, element or call result) stays inline: Python observes a container's contents when it
is CONSUMED, and Why3 models dicts/sets/growable lists as values, so a binder would snapshot
it. The dict-literal assignment fold (`map_update_some` over the keys and values) binds
every lowered key and value in Python order (`_pycsl_dk<i>`/`_pycsl_dv<i>`) when the same
predicate finds the display order-sensitive. REFUSED (PyCSLIRError, "route #307"): an
effectful container operand that would need binding; a `for ... in range(start, stop)`
header that needs sequencing (the loop header binds `stop` first); and any construct whose
lowering RE-DERIVES a bound operand from its shape instead of consuming the binder (an
operand the lowering drops entirely keeps only its binder). Spec contexts are untouched
(logic terms have no effects); dict literals of an `@mutable_state` emitter-model class
(IR-node constructions, mirror-only) keep their unsequenced emission.

### §T.6.19  Erased values are still evaluated (route #310)

A value with no model is erased to Why3's unconstrained `(any int)`: the binding of a
tuple/set local, and `_coerce_to_int`'s tuple / array / map arms wherever a display reaches
an `int` position. Erasing the TEXT erased the evaluation with it: `xs = [0]; t = (inc(xs),
0); return xs[0]` proved `\result == 0` (CPython 1). With $D$ an EFFECTFUL display (route
#307's predicate, probed as "$D$ is sequenced before a copy of itself"):

$$\mathcal{T}_s(t = D) = t \mathrel{:=} (\texttt{let \_ = } \mathcal{T}_e(D) \texttt{ in (any int)})$$

and, in $\mathcal{T}_e$, a node whose effectful display operand $D$ (not bound by §T.6.18) is
absent from the node's lowering (coerced, `len` folded from its shape, dropped by a
fallback) is lowered as $\texttt{let \_ = } \mathcal{T}_e(D) \texttt{ in } \mathcal{T}_e(node)$ when
every operand before $D$ is inert or bound and none after it is bound; a conditional arm or
any other position is REFUSED (PyCSLIRError, "route #310"). Statement sites: a subscript
store evaluates an erased value display before the store; an expression-statement call
evaluates an erased display argument before the call (refused if a non-inert operand
precedes it); a `for` over an erased display materialises it once before the loop; the
dict-literal fold evaluates an erased value display at its position; `raise E(a)` evaluates
an effectful `a` before `raise E`, and a `raise` whose dropped parts (second/keyword
arguments, `from` cause, computed exception) contain a call is refused
(`PYCSL-SEM-ERASED-EFFECT-R310`). Pure displays keep their emission byte-for-byte.

### §T.6.20  Every erased operand; slice bounds; method keywords (routes #311-#314)

§T.6.19 extends to every operand $O$ of an n-ary node (§T.6.18's operand lists, plus the
slice access $\texttt{SliceAccess}(v, lo, hi, st)$ whose operands are $v, lo, hi, st$ in that
order): when $O$ is effectful and not bound, its standalone lowering $\mathcal{T}_e(O)$ is a
PROBE (the node is re-emitted unchanged, so a position-dependent lowering keeps its text, and
abstract operations the probe registered are withdrawn); if $\mathcal{T}_e(O)$ is absent from
$\mathcal{T}_e(node)$ the node is lowered as $\texttt{let \_ = } \mathcal{T}_e(O) \texttt{ in }
\mathcal{T}_e(node)$ under §T.6.19's position conditions, else REFUSED — also when a
not-known-pure call of $O$ reappears in $\mathcal{T}_e(node)$ (re-derived: it would run twice).
$O$ is left dropped when every not-known-pure call in it lowers to an application of an
abstract `val` with no `writes`/`raises`/`requires`/`reads`/`diverges`, to `(any T)`, or to an
application-free text (no effect in the model). A `for` over any erased effectful iterable
is materialised before the loop. Slice bounds: $\mathcal{T}_e(v[lo:hi]) =
\texttt{let } s_{lo} = \mathcal{T}_e(lo) \texttt{ in Array.sub } v\ s_{lo}\ (\mathcal{T}_e(hi) - s_{lo})$
whenever $hi$ is effectful and $lo$ non-inert (route #311). Method keywords (route #314): a
keyword argument of a builtin-type method is refused in `_reset_function_state` except
`sort` and a string-literal `encoding`/`errors` of `encode`/`decode`, rewritten
positionally ($s.\texttt{decode}(e, \texttt{errors}{=}r) \equiv s.\texttt{decode}(e, r)$, CPython's
signature).
### §T.6.21  A construction is a field initialiser or refused (route #315)

$\mathcal{T}_e(K(\vec a))$ is the record literal $\{ f_i = \sigma(e_i) \}$ of `__init__`'s
recognised stores $\texttt{self.}f_i = e_i$ under the parameter substitution $\sigma$
(`(any int)` for each field the capture cannot state); the constructor body itself has no
image. That is faithful only if executing the body has no effect outside the new object,
no precondition and no raise beyond those the literal carries (a captured
$\sigma(e_i)$ keeps its own division/bounds obligation). Measured at d4e39ef2: `a[0] += 1`,
`self.n = inc(a)` (also inside a list/dict/slice/`sorted`, a `print`, an `if` test),
`self.xs = a; self.xs[0] = 5`, `self.xs += [5]`, an inherited or nested such constructor, a
dataclass `__post_init__` (also through an `InitVar`) and a user exception's `__init__` each
proved a caller claim CPython falsifies; `self.n = first(a)` under `K([])` proved past a
violated `requires` (CPython IndexError); a conditional `10 // d` / `a[0]` lost its raise.
The source scan in `_run_pipeline` (annotations.md §7.10) therefore admits $\mathcal{T}_e(K(\vec a))$
only for a class whose constructor is a field initialiser, closed over constructed classes
and inherited constructors; any other construction in a non-trusted function is REFUSED
(`PYCSL-R315-UNMODELLED-CONSTRUCTOR`). Emission is byte-identical wherever it is admitted.
### §T.6.23  `range` stops captured once; nested and aliased list rebinds refused (routes #318-#320)

$\mathcal{T}_s(\texttt{for } i \texttt{ in range}(a, b)\texttt{: } B) =
\texttt{let } \_stop = \mathcal{T}_e(b) \texttt{ in let } \_idx = \texttt{ref } \mathcal{T}_e(a)
\texttt{ in while } !\_idx < \_stop \texttt{ do } \ldots$ whenever $\mathcal{T}_e(b)$ is not an
integer literal, an immutable identifier, or `Array.length`/`str_length_op` of one (those
cannot change in the loop and keep their text; the #29 program-length hoist `_len_<idx>`
is unchanged). Previously the guard was `!_idx < T_e(b)`, re-evaluated per iteration
(route #318: `n = 2; for i in range(n): n = 5` iterated five times). A start/stop pair that
is evaluation-order sensitive is refused by route #307 before this point.

A first binding $p = e$ of a formal parameter lowers to
$\texttt{let } p = \mathcal{T}_e(e) \texttt{ in } \mathcal{T}_s(\text{rest of the block})$; this
is the Python scope only when the block is the function body, so a parameter whose first
binding is nested is refused (`PYCSL-M6-PARAM-REBIND-NESTED-BLOCK`, route #319; a
`ref` over an `array` parameter is ill-typed in Why3 once a fresh array is assigned).
$\mathcal{T}_s(xs = [v_1..v_n])$ for an array local is
$xs\_len := 0;\ xs[!xs\_len] \leftarrow v_1; \ldots$ — the SAME array — which is the Python
rebinding only when no other name, container, callee or running `for` holds it; otherwise
`PYCSL-M6-LIST-LITERAL-REBIND-ALIASED` (route #320).

### §T.6.22  The write effect of a method stub and of a bodyless `val` (routes #316 / #317)

A plain verified function is applied as its `let`, and Why3 infers its effect from the body,
so a caller of `def g(xs): xs[0] = 5` sees `xs` written. A METHOD call is
$\mathcal{T}_e(o.m(\vec a)) = (\texttt{val } o\_m\_n\ \vec x)$, and a `\trusted` / imported
function is a bodyless `val`: their effect is only what the declaration states. Before
routes #316/#317 that was `writes { self.f }` from `assigns self.f` and nothing else, so a
method or an imported helper doing `xs[0] = 5` was read as leaving `xs` unchanged (measured:
12 method shapes, an imported function and an imported class method each proved
`ys[0] == 0`, CPython 5). Now, with $W(F)$ the conservative parameter write set of
static-semantics "routes #316 / #317": the method stub carries
$\texttt{writes}\ \{ x_i \mid a_i \in W(m),\ x_i : \texttt{array}\ \tau \}$ (the whole-array effect
Why3 infers for a `let`); the bodyless `val` of a function with no `assigns` carries
$\texttt{writes}\ \{ p \mid p \in W(F) \}$; a declared method frame that omits a written parameter,
a method writing a global, and an override writing a position its base does not are refused.
`self`-field writes stay checked by the method body's `ensures { self.f = old self.f }`
frame (route #34). Emission is byte-identical for every method/stub whose body writes no
parameter.

### §T.6.25  Literal folds over int literals only; float module constants; contract slices (routes #322 / #324)

A fold $\mathcal{T}_e(\texttt{abs}(n)) = |n|$, $\mathcal{T}_e(\texttt{sum}([n_1,\dots,n_k])) = \sum n_i$
(and the known-element / default maps) is defined only when every $n_i$ is an INT literal;
for a float literal no fold applies and the general lowering runs (before route #322 the
fold computed $|\lfloor n \rfloor|$ / $\sum \lfloor n_i \rfloor$, so `abs(2.5) == 2` was proved).
`int(n)` for a finite float literal folds to $\mathrm{trunc}(n)$, which is its meaning.
A float module constant ($\texttt{math}.c$, $c \in \{\texttt{pi},\texttt{e},\texttt{tau},
\texttt{inf},\texttt{nan}\}$, the `cmath` ones, `sys.float_info`) has no image: its generic
lowering was the opaque $(\texttt{get\_}c\ \texttt{math}) : \texttt{int}$ and is refused before
Module 6 (`_run_pipeline`, IR walk + module/class-level bindings; also through `from math import *`
and `getattr(math, "pi")` / a non-literal `getattr` on the module).
In a contract, $\mathcal{T}_s(s[a:b]) = \texttt{String.substring}\ s\ a'\ (b' - a')$ with
$x' = x$ for a non-negative int literal or an omitted bound, else
$x' = \texttt{if}\ x < 0\ \texttt{then}\ \max(x + |s|, 0)\ \texttt{else}\ x$; Why3's
`substring` (empty for an offset outside $[0, |s|)$ or a length $\le 0$, clipped at the end)
then coincides with CPython's step-1 slice. The body side keeps route #190's guarded
`str_sub_op`.
### §T.6.26  The opaque-int fallback is not an int model (route #325)

_Corresponds to `annotations.md` §7.15._

Where $\mathcal{T}_e$ has no image for a value it emits a fresh uninterpreted symbol of type
`int`: $\texttt{val constant}\ n : \texttt{int}$, $(\texttt{get\_}x\ r)$,
$(\texttt{getattr\_}C\ \textit{self}\ h)$, $(\texttt{subscript\_get}\ r\ i)$,
$(m\_f\_k\ \vec a) : \texttt{int}$. Its Why3 meaning is "SOME integer", so every theorem of
$\mathbb{Z}$ holds of it — sound only if the Python value IS an int. The check runs on the
emitted module, after every lowering (`_run_pipeline`, before Why3): an ORIGIN is such a
symbol standing for a module-level name of the file, an import / module or class object, a
class-level attribute, a `getattr(...)` fallback, or a call of an imported / builtin
callable, minus the KNOWN-INT set of annotations.md §7.15. Taint flows through `let x = e in`,
`x := e`, a getter / subscript / opaque operation applied to a tainted term, a tuple, a
constructor or container builder, `raise (Return e)` / a declaration's tail (the function is
then tainted), a user function's parameter, and a call stub `r_m_k` whose receiver $r$ is
tainted (Module 6 drops the receiver). A tainted occurrence is admitted only as an argument of
an opaque operation, the right-hand side of a binding, a return, a discarded statement, or one
side of a program `=` / `<>` whose other side holds no term of the same origin (no
reflexivity: a NaN is not equal to itself). Any other position — an int operator or ordering,
a modelled function, a contract term — is refused. Binders follow WhyML scoping (a `let`
scopes from its `in` to its enclosing group or block; `F` and `f` fold to one WhyML name).

### §T.6.29  More origins, unpacking and precise binders for the opaque-int check (routes #328 / #330 / #331)

_Corresponds to `annotations.md` §7.18._

The §T.6.26 check is extended, still on the emitted module in `_run_pipeline`. ORIGINS: a
module / class-level name bound by ANY binding form at any nesting outside a function or
lambda body (Assign / AnnAssign / AugAssign targets with tuple and starred elements, `for`,
`with`, `except .. as`, walrus, `match` captures, nested `def` / `class`); a target paired
with a value is classified by it, `for x in range(..)` binds an int, any other target is of
unknown type. A record label $\ell$ typed `int` of a class whose field $f$ has a shown
non-int initialiser or annotation ($\ell$ = `_field_label(record, f)`, inherited through the
class bases): the read $r.\ell$ is the unit. A `None` / `Optional[int]` field and a
string-encoding model operation (`repr_conv`, `format_conv`, other `*_conv` except `abs` /
`bool` / `int` / `round`, `str_of_int_hash`, `str_of_bool_hash`, `str_of_value_op`,
`str_concat`) are origins whose `=` / `<>` stay admitted everywhere (no NaN). Under
`--strict-bare-containers`, the elements $p[i]$ / $(\texttt{subscript\_get}\ p\ i)$ of a
bare-container parameter $p$. A `complex` annotation is refused outright. FLOW: a tuple
pattern `let (a, b) = (u, v) in` taints the component $u$ occupies (all names when the
right-hand side is not a literal tuple). SINKS added: the key of `Map.get` / `Map.mem` /
`Map.set` (a lookup compares keys by equality and yields the map's value), a `writes` /
`reads` / `alias` item (a location), and a generated frame `X.ℓ = old X.ℓ`. BINDERS: a
`match` / `try` arm's pattern variables scope from the arm's `|` / `with` to the next arm,
and a `for` index over its `do .. done` (both were declaration-wide). BARE-CONTAINER-INT is a
declared model assumption (§T.10.5).
### §T.6.32  Field origins by the type of every stored value (route #334)

_Corresponds to `annotations.md` §7.21._

The §T.6.29 field rule is replaced by a classifier over the Python AST, still inline in
`_run_pipeline`. For a class $C$ and field $f$, $\mathit{St}(C, f)$ is every store of $f$ in
$C$, its bases and its descendants (class-level and `self.f` assignments with tuple targets
paired element-wise, starred / `for` / `with` / comprehension targets with an unknown value,
`+=` as `0 op e`, `setattr(self, "f", e)`, a dynamic `setattr` taints every field, dataclass
`field(default=e)`); for a dict field, $\mathit{St}_v(C, f)$ is its display values, `self.f[k]
= e`, `.setdefault(k, e)`, `.update(..)` (unknown). Each stored expression is walked to a kind:
INT (int / bool literal, int operators, `**` by a non-negative literal, locals followed through
every binding of the storing def, walrus, int / unannotated parameters, known-int globals,
other fields followed through their stores, `len int ord hash id bool round(x)`, `abs min max`
of int arguments, a user `-> int` function / method), NONE (a `None` leaf: `=` / `<>` admitted,
§T.6.29), IFLOAT (an integral float literal, $|v| < 2^{53}$), UNK (unknown type) or OTHER
(shown non-int). The label $\ell$ = `_field_label(record, f)` typed `int` is an origin unless
every kind is INT; UNK is dropped when some store annotates $f$ `int` / `bool` / `Final[int]` /
`ClassVar[int]` (annotation trust). An IFLOAT origin is admitted only as a DIRECT operand of
`<`, `<=`, `>`, `>=`, `=`, `<>` (its int and float values compare equally); any other use is
refused. A dict field whose VALUES are not all INT, and under `--strict-bare-containers` a
bare `dict` / `Dict` / `Mapping` parameter, makes its `map .. (option int)` label a VALUE
origin: `match Map.get u k with | Some v -> ..` reads a value (the match carries the origin),
`| Some _ -> ..` and `Map.mem` only test membership (admitted). An OPAQUE class (no record
type: `C()` is a stub `c_<n>`, `c.f` a getter `get_f`) is an origin whose getters of
provably-int fields stay int. Two sinks were added to keep the mirror emitting: an argument at
a `'a`-typed parameter of a `val` (`str_mod_op "fmt" (a, u)`: no int theory applies there), the
head found skipping string-literal arguments.

### §T.6.34  Annotation resolution and the int-default erasure (routes #336 / #337)

_Corresponds to `annotations.md` §7.23._

**Resolution (Module 5, `visit_Module`, before any type reader runs).** Let $A$ be the map
from a module-level name bound exactly once by `X: TypeAlias = T`, `type X = T` (no type
parameters), `X = TypeAliasType("X", T)` or a plain `X = T` whose names are all type names, to
$T$ (`Any` / `object` / string targets and the IR sentinels excluded). Every parameter,
return and annotated-local annotation node is rewritten to a fixpoint (at most 16 rounds) by
$X \mapsto A(X)$, `Annotated[T, ..]` $\mapsto T$, `Sequence[T]` / `MutableSequence[T]` /
`tuple[T, ...]` / `Tuple[T, ...]` $\mapsto$ `List[T]`, `Mapping[K, V]` / `MutableMapping[K, V]`
$\mapsto$ `Dict[K, V]`, `Literal[None]` $\mapsto$ `None`. Hence
$\tau(\text{rewritten}) = \tau(\text{direct spelling})$ byte for byte. A parameter whose
pre-rewrite head (through $A$, `Optional`, `Annotated`) is `Sequence`, `Mapping` or a
`tuple[T, ...]` is READ-ONLY: a subscript store / `del` / augmented assignment, a method call
other than `count index get keys values items copy`, or an argument position of any call but
the pure builtins raises `PYCSL-R336-READONLY-VIEW-STORE` (stage `ir-emit`).

**Erasure (Module 6, `_reset_function_state`, the route #249 set).** Let $L$ = {`int bool
str float list tuple dict set frozenset bytes bytearray List Dict Set FrozenSet Tuple`, the IR
sentinels} $\cup$ records $\cup$ variants $\cup$ tags prefixed `_union_` / `option:` /
`callable:` (plus `TParamNode` / `CallKw` / `ast.ClassDef|Module` under their `_uses_*`
gates). A formal $p$ with annotation tag $a \notin L$ joins $\mathit{erased}$; a return tag
$\notin L \cup$ {`None NoReturn Iterator Generator Iterable`} sets `ret_erased`, and a call
of such a function is an erased call (`_r249_any_ret_funcs`). An element / key / value of an
annotated container whose type is outside what the readers model (Module 5 `r249_erased_
containers`: `int`/`bool`/`str`, records outside sets, `float` only at `List`-only depth or a
fixed `Tuple` slot, dict values in `_m5_get_dict_value_type`'s shapes, `int`/`bool`/`str`
keys) is tagged `k` / `v`. In `_union_arm_tag`, a capitalised arm that is not a declared
record returns `Any`, so the annotation is the erased `Any` of §T.6 route #258. Erased values
then follow routes #251 / #252 unchanged (uninterpreted `pycsl_py_*` operators; refused
under `no_exception` and in builtin-typed slots).

**Operators on `self` (Module 5, same pass).** In a def whose first positional parameter is
`self`, a `BinOp` with `self` as an operand, a `UnaryOp` other than `not` on `self`, an
`AugAssign` to `self`, or a `Compare` with an ordering operator and `self` as an operand stamps
the def; `_build_function_ir` raises `PYCSL-R337-SELF-OPERATOR`. (A non-record class's methods
take `self: <c>` with `type <c> = int`, so these were int operators.)

### §T.6.35  Override annotation refinement (R5) and the any-code field-store census (route #338)

_Corresponds to `annotations.md` §7.24._

R5 joins R1-R4 in the route #278 block of `_run_pipeline` (inline; mirror twin `\trusted`). For
a recorded pair (sub $P.t$ refines base $X.t$) it reads both Python defs from the source AST
(the IR flattens `Optional[int]` to a `_union_*` name) and, writing $\lfloor a \rfloor$ for the
member set of an annotation (`Union` / `Optional` / `|` split; `None` a member; `typing.` and
`List`/`Dict`/`Set`/`Tuple` capitalisation normalised; absent = $\{\mathtt{Any}\}$), requires
$\lfloor \mathit{ret}_P \rfloor \sqsubseteq \lfloor \mathit{ret}_X \rfloor$ and, per
positional parameter $i \ge 1$, $\lfloor \mathit{par}^i_X \rfloor \sqsubseteq \lfloor
\mathit{par}^i_P \rfloor$, where $L \sqsubseteq H$ iff the wider side is absent, or $H$ meets
$\{\mathtt{Any}, \mathtt{object}\}$, or every $m \in L$ has $\uparrow m \cap H \ne
\emptyset$, $\uparrow m$ being $m$, its ancestors among the file's classes, and `int` for
`bool`. A failure raises `PYCSL-SEM-OVERRIDE-REFINEMENT`. No goal is emitted: the lowering of
`b.m()` (a `val` typed by $X.t$'s annotation) is unchanged, R5 only makes it faithful.

The §T.6.32 store set becomes $\mathit{St}(C, f) \cup \mathit{Ext}(C, f)$. $\mathit{Ext}$ walks
the whole module (enclosing def tracked) for every attribute store NOT already counted as a
`self` store — assignment / annotated / augmented (`0 op e`, plus an unknown dict-value store)
/ `for` / `with` / comprehension targets, tuple targets paired element-wise, `del x.f` and
`delattr` / `object.__delattr__` (value: a non-int marker), `setattr` / `object.__setattr__`
(dynamic name: `*`), `x.f[k] = e`, `x.f.update / setdefault / __setitem__`, and `__dict__` /
`vars(x)` stores (`*`). The receiver $x$ resolves to a class $K$ (a method's `self`, a parameter
annotated $K$, a local every binding of which is `K(..)`): the store joins $K$'s set (hence its
bases' and descendants' views, as in §T.6.32); a parameter annotated with builtin scalar /
container names only joins no set; any other receiver joins every class storing $f$. In the
kind walk, an UNANNOTATED parameter of the storing def is INT unless the names mentioned by
unverified module code (every statement outside a def body: module level, `__main__`, class
bodies, decorators, defaults; class bases excluded) meet $\{$the def, its class, the class's
descendants$\}$, where it is UNK; and `k.m()` on a receiver resolved to $K$ is INT when $m$ is
annotated `-> int` / `-> bool` in $K$ or a base.

### §T.6.36  Class bases by name; constructor store forms (routes #341 / #342)

_Corresponds to `annotations.md` §7.25._

One inline block of `_run_pipeline`, after the boundary re-validation of the resolved IR
(mirror twin `\trusted`; no emission changes, only refusals). Over the source AST: let
$\mathit{Bd}$ be the names the file binds otherwise than by `class` / import (a `Name` in
store or del context, a `def`, a parameter, an `except` / `match` capture). A base $b$ of any
class is admitted iff $b$ is a `Name` $\notin \mathit{Bd}$, or an `Attribute` chain whose root
is an imported name $\notin \mathit{Bd}$, or a `Subscript` on `Generic` / `Protocol`; otherwise
`PYCSL-R341-CLASS-BASE-NOT-A-NAME`. Any `__class__` attribute store / delete, or `setattr` /
`delattr` / `__setattr__` / `__delattr__` with the constant name `"__class__"`, raises
`PYCSL-R342-CLASS-REASSIGNMENT`.

From the resolved IR, for each record $C$ with merged `class_invariants` $I_C \ne \emptyset$:
$F_C$ = the fields $f$ of `FieldGet(self, f)` nodes in $I_C$, plus $\star$ if another node
mentions `self`. $F$ = $\bigcup_C F_C$ ($\star$ expanded to $C$'s fields). Every module-level
statement outside a def / class / lambda that stores or deletes an attribute named in $F$, or
calls `setattr` / `delattr` / `__setattr__` / `__delattr__` with a name in $F$ or a non-constant
name, raises `PYCSL-R342-EXTERNAL-INVARIANT-STORE`. For each class $K$ of the file on the base
closure of such a $C$ (bases by name / attribute tail), $R_K = \bigcup F_C$; each `__init__` /
`__post_init__` of $K$ with first parameter $s$ is walked whole (nested classes and defs
rebinding $s$ skipped) and raises `PYCSL-R342-CONSTRUCTOR-STORE-FORM` on: an attribute
$s.f$ in store / del context with $f \in R_K$ (or $\star \in R_K$) that is not a direct
target of a top-level `Assign` / `AnnAssign`; $s$`.__dict__` / `__setattr__` / `__delattr__`; a
`Name` $s$ in store context, or in load context that is neither an attribute root nor the first
argument of the builtin `type` / `isinstance` / `id`; a call $s.m(\ldots)$; a `super().a(..)`
other than the first non-docstring statement `super().__init__(..)`; a `return` outside a
nested def. Hence every invariant-carrying construction that reaches route #226's goal is the
straight-line store sequence the goal reads, and the remaining no-goal case is a straight-line
store of a computed value (route #226's open carrier).

### §T.6.37  Enum members; nested-def bare-name defaults (routes #339 / #340)

_Corresponds to `annotations.md` §7.26._

Two inline blocks of `_run_pipeline`, beside route #273's definition-time block (mirror twin
`\trusted`; no emission changes, only refusals). Over the source AST:

(#339) $\mathcal{E}$ = the classes with a base whose name (or attribute tail) is in
$\{\texttt{Enum},\texttt{IntEnum},\texttt{Flag},\texttt{IntFlag},\texttt{StrEnum},\texttt{ReprEnum}\}
\cup \mathcal{E}$ (fixpoint); for $C \in \mathcal{E}$, $D_C$ = its dunders (own and of its
enum bases, less `__init__`, `__new__`, `__init_subclass__` and the attribute dunders), $M_C$
= its non-dunder, non-sunder class-body binding names, $\mathit{int}_C$ = some base chain names
`IntEnum` / `IntFlag` / `int`. $C$ is TRANSPARENT iff $\mathit{int}_C \wedge D_C = \emptyset$;
its member $C.M$ keeps $\mathcal{T}$'s int getter `get_M _class_c`. For every OPAQUE $C$,
an annotation $\mathit{ann}(C)$ is `C`, `"C"`, `Optional[C]` or `C | None` (any other
annotation mentioning $C$ is refused); per lowered function $F$ the member expressions are
$C.M$ ($M \in M_C$), `C(..)`, `C[..]`, calls to a function / method name annotated
$\to \mathit{ann}(C)$, attributes named as a field annotated $\mathit{ann}(C)$, and the names
bound (fixpoint over assignment / annotated assignment / walrus value, `for` / comprehension
target over `C`, parameters annotated $\mathit{ann}(C)$, module-level bindings) to one. Each
member expression $e$ is admitted by its PARENT only: an `Assign` / `AnnAssign` / walrus value
with name targets; a `Compare` whose operators adjacent to $e$ are `is` / `is not`, or `==` /
`!=` / left operand of `in` / `not in` when $\{\texttt{\_\_eq\_\_},\texttt{\_\_ne\_\_}\} \cap
D_C = \emptyset$ (an `in` display element likewise; a `match` subject / value likewise); an
`If` / `While` / `IfExp` / `Assert` test, a `not` operand or a `BoolOp` in such a test when
$\{\texttt{\_\_bool\_\_},\texttt{\_\_len\_\_}\} \cap D_C = \emptyset$; `.value` / `.name`; an
expression statement; a `return` in a function annotated $\to \mathit{ann}(C)$; an argument /
keyword / default whose parameter is annotated $\mathit{ann}(C)$; `isinstance` / `id` / `type`
(`hash` when `__hash__` $\notin D_C$). Every other parent, an `AugAssign` to a member name, and
the class name $C$ as a call argument (other than to `isinstance` / `issubclass`) raise
`PYCSL-SEM-ENUM-MEMBER-OPERATION`. Hence no int operation of $\mathcal{T}$ is applied to an
opaque member, and no user operator dunder is bypassed by $\mathcal{T}$'s int operators. The
classifier ($\mathcal{E}$, $D_C$, $M_C$, $\mathit{int}_C$) is the one of §T.6.41 (routes #352-#356).

(#340) For each lowered $F$ let $B_F$ = the names bound anywhere in $F$ (store / del `Name`s,
nested `def` / `class` names, import aliases, `except` / `match` captures) $\cup$ every
`global` / `nonlocal` name of the module. A bare `Name` $x$ in a default of a nested `def` /
`lambda` of $F$ is admitted iff $x \notin B_F$; then $x$ denotes one value over the whole run
of $F$, and the lifted call's call-time read `(g !x)` equals CPython's def-time binding.
Otherwise `PYCSL-SEM-DEF-TIME-EVALUATION`.

### §T.6.38  Erased field-less receiver, builtins on erased values, MRO-resolved R5, foreign attribute bases (routes #343 / #344 / #345)

_Corresponds to `annotations.md` §7.27._

(1) In `_reset_function_state`'s route #249 pre-scan, for a function with `kind = method` whose
`self_type` $c$ is neither a record nor a variant (case-insensitive), $\mathtt{self} \in E$
(the erased set) before the binding fixpoint; the fixpoint and `_handle_binop`'s copy of the
erased-operand walk do not descend into the base of an `Attribute` / `FieldGet` whose base is
`Var self`, nor into the first argument of a propagating `getattr(self, ..)`, and (as before)
never erase `self.m(..)`. Route #252's sites then refuse any $E$-expression flowing into a
builtin-typed parameter / field / return. The declaration `type c = int` and the binder
`(self: c)` are unchanged. (2) In `_expr_to_whyml`'s dispatch, a program-context `Call` of a
builtin $f$ in the dunder-dispatching set (§7.27 (2)) that no unit function shadows, inside a
function with a non-empty `no_exception` set or `no_exception \all`, with an argument (or
keyword value, or starred value) $a$ for which route #251's `r251_erased?` probe answers yes,
lowers to `(begin assert { [@expl:PyCSL-R343 ..] false }; ⟦f(..)⟧ end)`. (3) In the route
#278 block of `_run_pipeline`, for a pair side $K.t$ with no def $(K, t)$ in the source map, the
C3 linearization $L[K]$ over the file's classes (bases by `Name`, iteratively: $L[K] = K \cdot
\mathit{merge}(L[B_1], \ldots, L[B_n], [B_1, \ldots, B_n])$, a base outside the file taken as
$[B]$, no consistent merge or a cycle stopping the walk) gives the first $K' \in L[K]$ with a
def $(K', t)$; R5 compares that def. (4) In the route #341 block, an `Attribute` base $r.a$ that
passes the imported-root check raises `PYCSL-R341-CLASS-BASE-NOT-A-NAME` when $a$ names a class of
the file, unless $r$ is a `Name` bound only by `import s [as r]` with $s$ the file's own module
stem (no `from`-import or other `import` binding $r$).

### §T.6.39  Post-init, definite assignment, immutable and unhashable records (routes #346 / #347 / #348 / #349)

_Corresponds to `annotations.md` §7.28._

One inline block of `_run_pipeline`, appended to §T.6.36's (mirror twin `\trusted`; refusals
only, no emission change). Over the source AST: $\mathit{bn}(K)$ = the base names of class $K$
(a `Name`, or an `Attribute`'s tail), $\mathit{clo}(K)$ = the left-to-right depth-first closure
of $\mathit{bn}$ from $K$ (an over-approximation of the MRO's class set), $\mathit{DC}$ the
`@dataclass` classes with their literal options (non-literal = unknown).

**#346.** For each resolved-IR record $C$ with merged `class_invariants` $\ne \emptyset$: if
$\mathit{clo}(C) \cap \mathit{DC} \ne \emptyset$ and some $K \in \mathit{clo}(C)$ defines
`__post_init__`, raise `PYCSL-R346-POST-INIT-INVARIANT`.

**#348.** $\mathit{Imm}$ = classes with a `NamedTuple` base, $\mathit{DC}$ classes with
`frozen` true or unknown, names bound by `x = namedtuple(..)` / `x = NamedTuple(..)`, closed
under $\mathit{clo}$; $\mathit{IF}$ = their field names ($\star$ for a non-literal field list).
Per def, $\tau(x)$ = the top-level classes of $x$'s annotations (through `Optional` / `Union` /
`|` / strings) and constructor bindings, empty when any binding is un-annotated; $\tau(s) =
\{K\}$ for the first parameter of a method of $K$. A store / del / augmented `Attribute`
$r.f$, or `setattr` / `delattr`$(r, f, ..)$ ($f = \star$ when non-constant), raises
`PYCSL-R348-IMMUTABLE-RECORD-STORE` iff $\tau(r) \cap \mathit{Imm} \ne \emptyset$, or
$\tau(r) \not\subseteq$ the file's classes and $f \in \mathit{IF} \cup \{\star\}$ or $\star \in
\mathit{IF}$.

**#349.** $U$ = the classes unhashable by Python's rule (§7.28 (4)) evaluated along
$\mathit{clo}$. Every annotation whose head is a keyed collection (`Set`, `FrozenSet`, `Dict`,
`Mapping`, `DefaultDict`, `Counter`, ...) and whose first argument's top-level classes meet $U$
raises `PYCSL-R349-UNHASHABLE-RECORD`; so does each hashing position of §7.28 (4) whose operand
$e$ has $\tau(e) \cap U \ne \emptyset$ ($\tau$ extended to constructor calls and to `x.f` for
a typed $x$ by $f$'s class-body annotation).

**#347.** For each class, in increasing $|\mathit{clo}|$ (ancestors first), the constructor's
definitely-assigned set $\mathit{DA}(K)$: for an own `__init__` with first parameter $s$, a
bottom-up summary $\langle G, R \rangle$ per statement ($G$ = fields stored on fall-through, or
$\bot$ when it never falls through; $R$ = the sets stored at each `return`): assignments /
augmented / annotated-with-value / `with .. as` targets $s.f$ and `setattr(s, "f", ..)` gen
$\{f\}$; `super().__init__(..)` gens $\mathit{DA}$ of the first in-file ancestor, `B.__init__(s,
..)` gens $\mathit{DA}(B)$; `raise` / `break` / `continue` = $\langle\bot, []\rangle$, `return`
= $\langle\bot, [\emptyset]\rangle$; sequence accumulates; `if` meets ($\bot$ is the top);
loops give $\langle\emptyset, R_{body} \cup R_{else}\rangle$; `with` gives its targets only;
`try` meets body;else with every handler then joins `finally`; `match` meets its cases
($\emptyset$ without an irrefutable last case). $\mathit{DA}(K) = \bigcap (\{G\} \cup R)$ minus
every `del` $s.f$ ($\emptyset$ if any `delattr`). A `@dataclass` without own `__init__`: its
and its dataclass ancestors' annotated fields except `ClassVar` and `field(init=False)` without
default; a NamedTuple: its fields; else $\mathit{DA}$ of the first in-file ancestor. $M =
\bigcup_K (\mathit{Fld}(K) \setminus \mathit{DA}(K) \setminus \mathit{CA}(K))$ with
$\mathit{Fld}$ the $s.f$ stores of every method over $\mathit{clo}(K)$ plus dataclass /
NamedTuple fields and $\mathit{CA}$ the class-body bindings over $\mathit{clo}(K)$. In every
non-trusted def whose IR contract has `no_exception_all` or names `AttributeError` /
`Exception` / `BaseException`, an `Attribute` load / del / augmented target $r.f$ with $f \in
M$ and $r$ not an imported module raises `PYCSL-R347-FIELD-MAYBE-UNASSIGNED`.

### §T.6.40  Parameter defaults of the annotated kind; read-only view escapes (routes #350 / #351)

_Corresponds to `annotations.md` §7.29._

Two inline blocks of `_run_pipeline`, after route #273's definition-time block (mirror twin
`\trusted`; no emission change, only refusals). Module 5 has already rewritten annotations in
place (route #336), so both read a fresh parse of the SOURCE, restricted to the defs of the
lowered trees $\mathcal{L}$ of route #273 (matched by line and name). $\mathit{Al}$ = the module
names bound exactly once at module level (`Assign` / `AnnAssign` / `type` statement; no
`global`, `nonlocal` or augmented rebinding) with their values.

(#350) For every def $g$ in a tree of $\mathcal{L}$ and every annotated parameter $p : A$ with a
default $d$, let $\mathit{arms}(A)$ be $A$ split through $\mathit{Al}$, `Optional` (adding the
`None` arm), `Union`, `|`, `Annotated` and string forward references. Resolve $d$: a bare name
in $\mathit{Al}$ becomes its value; a bare name that is a parameter of a def of the tree carries
that parameter's annotation set $O$. The pair is admitted iff some arm $a$ admits $d$:
$a \in \{\texttt{Any},\texttt{object}\} \cup \mathit{TypeVars}$; $d$ = `None` and $a$ = `None`;
$a \in \{\texttt{int},\texttt{float},\texttt{complex},\texttt{bool},\texttt{str},\texttt{bytes}\}$
and $d$ a (signed) literal of a type in its numeric-tower set ($\texttt{bool} \subseteq
\texttt{int} \subseteq \texttt{float} \subseteq \texttt{complex}$), or $d$ an outer parameter
with $O \subseteq \{a\}$ ($\{\texttt{int},\texttt{bool}\}$ for `int`); $a$ = `Literal[`$v_i$`]`
and $d = v_i$; $a$ a container head and $d$ a display of its kind (list / tuple / dict / set;
`Sequence` admits list, tuple and strings); any other head and $d$ a non-literal, non-`None`
expression (a scalar literal is admitted only for a head that is neither a container nor a
class of the file). When exactly one arm admits a display, each element (key / value) is
checked against the element annotation(s) the same way, and a fixed `Tuple[..]` needs the
arity. No admitting arm raises `PYCSL-SEM-DEFAULT-ANNOTATION-MISMATCH`. Hence every omitted
argument binds a value of the parameter's verified type.

(#351) For each tree $F \in \mathcal{L}$, $V_0$ = the parameters (of any def of $F$) whose
annotation resolves, through $\mathit{Al}$ / `Optional` / `Annotated`, to `Sequence[..]`,
`Mapping[..]` or `tuple[T, ...]`. $\mathit{flow}(e)$ = the names reached from $e$ through
`IfExp` branches, `BoolOp` operands, walrus / starred values, display elements, slice
subscripts' value and `+` / `*` operands. $V$ = the fixpoint of $V_0 \cup \{y \mid y$ bound
by `y = e` / `y := e` / `y: T = e` / `for y in (display)` with $\mathit{flow}(e) \cap V \ne
\emptyset\}$. With $\mathit{own}(n)$ the innermost def / lambda of $n$, raise
`PYCSL-SEM-READONLY-VIEW-ESCAPE` when $\mathit{flow}(e) \cap V \neq \emptyset$ for: `return e`
where $\mathit{own}$'s return annotation is absent, has an arm outside
$\{\texttt{Sequence},\texttt{Mapping},\texttt{Iterable},\texttt{Collection},\texttt{Reversible},
\texttt{Container},\texttt{Iterator},\texttt{AbstractSet},\texttt{Any},\texttt{object},
\texttt{None}\} \cup \{\texttt{tuple[T, ...]}\} \cup \mathit{TypeVars}$, or $e$ contains a
display; a lambda body $e$; an `Assign` / `AnnAssign` / `AugAssign` value $e$ with an attribute
or subscript target, or an `AnnAssign` to a name annotated outside that set; an argument $e$
of a call other than route #336's read-only builtins (a bare parameter of $V_0$ there is route
#336's own refusal in Module 5). A subscript store / `del` / augmented assignment / mutating
method call on $y \in V \setminus V_0$ is refused likewise. Hence the only list / dict the
model may store into is one that was never a read-only view argument.

### §T.6.41  Enum base resolution, MRO-wide dunders, flags, value lookup, class-object attributes (routes #352 / #353 / #354 / #355 / #356)

_Corresponds to `annotations.md` §7.30._

The classifier of §T.6.37 (#339) is replaced inside the same inline `_run_pipeline` block
(mirror twin `\trusted`; refusals only, no emission change). Over the source AST:

**Base resolution (#352).** $\mathit{imp}(y)$ = `E:X` for `from enum import X as y` ($X$ an enum
class name; otherwise unknown), the enum module for `import enum [as y]`, `S` for an import from
a stdlib module other than `enum`, `U` otherwise. A base expression is resolved (through
`Subscript` heads and module-level aliases bound exactly once) to a token: `C:n` for a file class
$n$; $\mathit{imp}(y)$ for an imported name (the module itself is `U`); `E:X` for a bare enum
class name (`T:X` when a non-`enum` star import is present); `B:n` for a builtin; for an
`Attribute` $r.\ldots.a$: `E:a` when $r$ is the enum module and the chain has length 1, `S` when
$r$ is a stdlib module and $a$ is not an enum class name, `T:a` when $a$ is an enum class name,
`U` otherwise; any other expression is `U`. A class keyword adds `K`. $\mathit{anc}(n)$ = the
file classes reachable through `C:` tokens (fixpoint; the class set of $n$'s C3 MRO restricted
to the file), $\mathit{tok}(n) = \bigcup_{m \in \mathit{anc}(n)} \mathit{tok}_0(m)$.
$\mathcal{E}$ = $\{n \mid \mathit{tok}(n)$ holds an `E:` or `T:` token$\}$; $\mathcal{E}^?$ =
$\{n \notin \mathcal{E} \mid \texttt{U} \in \mathit{tok}(n)$ and $n$'s body has a non-lambda
plain binding of a non-dunder name$\}$.

**Dunders and int-likeness (#353, #354).** $D_n = \bigcup_{m \in \mathit{anc}(n)}$ (dunders bound
in $m$'s body, less those of §T.6.37), plus every operator dunder for $n \in \mathcal{E}^?$;
$M_n$ likewise for member names. $\mathit{int}_n$ iff $\mathit{tok}(n) \cap
\{\texttt{E:IntEnum}, \texttt{B:int}\} \neq \emptyset$ and $\mathit{tok}(n) \subseteq
\{\texttt{E:IntEnum}, \texttt{E:Enum}, \texttt{E:ReprEnum}, \texttt{B:int}, \texttt{B:object}\}
\cup \{\texttt{C:}m \mid m \in \mathcal{E}\}$ — so `IntFlag` / `Flag`, a keyword, a non-enum
mixin, a stdlib / unknown base each make $n$ OPAQUE. $n$ is TRANSPARENT iff $\mathit{int}_n \wedge
D_n = \emptyset$; §T.6.37's context rule applies to every opaque $n \in \mathcal{E} \cup
\mathcal{E}^?$ with these $D_n$ / $M_n$, and its `hash` admission now requires
$\{\texttt{\_\_hash\_\_}, \texttt{\_\_eq\_\_}\} \cap D_n = \emptyset$.

**Value lookup (#355).** For every $n \in \mathcal{E}$ and every `Call` $n(\ldots)$ in a lowered
function: admitted iff it has exactly one positional argument and no keyword, and the argument
is $n.M$ ($M \in M_n$), or a `Constant` $v$ with $\mathit{type}(v) \in \{\texttt{int},
\texttt{str}\}$ such that some member of $n$'s own body is bound to a `Constant` $w$ with
$\mathit{type}(w) = \mathit{type}(v) \wedge w = v$, every non-`C:` token of $\mathit{tok}(n)$ is
an enum class or `B:object` / `B:int` / `B:str` (not both an int and a str mixin), no class of
$\mathit{anc}(n)$ binds `__new__`, and $\mathit{type}(v)$ is `int` under an int mixin, `str` under
a str mixin. Hence an admitted lookup is one CPython's `_value2member_map_` resolves.

**Class-object attributes (#356).** For every $n \in \mathcal{E}$, an `Attribute` $n.X$ in a
lowered function whose context is not `Load`, or whose $X \notin M_n$ and $X$ is bound in no
body of $\mathit{anc}(n)$, raises `PYCSL-SEM-ENUM-MEMBER-OPERATION`.

### §T.6.42  Field-less values, protocol operations on erased values, whole-class-body R5 (routes #357 / #358 / #359)

_Corresponds to `annotations.md` §7.31._

(1) In `_reset_function_state`'s route #255 resolution, a method candidate $g$ of a call
spelling $f$ whose name is in the unit-level `any_ret` set (return annotation outside the
lowered tags, §T.6.34) adds $f$ itself (`self.me`) to `any_ret`. The fixpoint and
`_handle_binop`'s copy of the erased-operand walk answer yes for an `UnknownPyExpr` node and for
a `Call` whose callee string ends in `.__class__`. In `_run_pipeline`, before route #290's
computed-callee rule, a `Call` whose callee is `type(e)` (one argument) or an `Attribute`
`.__class__` raises `PYCSL-R357-DYNAMIC-CONSTRUCTOR` when it lies in a module-level function or
class method whose IR contract has `no_exception_all` or a non-empty `no_exception`, or when an
argument / keyword value is not an `ast.Constant`. (2) Under the same context condition as
§T.6.38 (2) (program context, non-empty `no_exception` or `\all`, a non-empty route #249
scope), with $P(a)$ = route #251's `r251_erased?` probe: `_classify_iterable`'s two opaque
`iter_length` bounds become `(begin assert { [@expl:PyCSL-R358 ..] false }; (iter_length ..)
end)` when $P(\mathit{iter})$; `_to_bool(w, e)` returns `(begin assert {..} false; ⟦to_bool⟧
end)` when $P(e)$ (the re-entry carries `_pycsl_r358n`); in `_expr_to_whyml`, after the typed
fast paths, a `FieldGet` / `Attribute` with base $b$ (`self` spelled as a string base included),
$P(b)$, and attribute $a \notin \mathtt{dir(object)} \cup$ the method names and `self.f` /
`setattr(self, "f", ..)` stores of the IR functions whose `self_type` is $b$'s declared class; a
`ListComp` / `SetComp` / `DictComp` / `GenExp` with $P(\mathit{iter})$ for some generator; a
`Call` with a `str` / `list` / `dict` / `set` / `tuple` (literal `receiver`, or a dotted name of
that symbol type, or a route #249 container) receiver, method $\ne$ `append`, and $P$ of some
argument (only the index of `insert`) — each lowers to `(begin assert { [@expl:PyCSL-R358 ..]
false }; ⟦node⟧ end)`, the node re-emitted once with `_pycsl_r358n` (stripped on entry).
(3) In the route #278 block (now entered whenever `check_behavioral_subtyping` holds): $\mathit{ND}$
= the (class, name) pairs a class body binds other than by a top-level `def` (assignment /
augmented / annotated-with-value / `for` / `with` / `del` targets, walrus targets in a
statement header, imports, `except .. as`, `match` captures, nested `def` / `class`; nested
function / class scopes not entered). In the per-pair MRO walk of §T.6.38 (3), a side's own
class in $\mathit{ND}$, or a first-binding $K' \in L[K]$ with $(K', t) \in \mathit{ND}$, or (for
the sub side, when the base's class is a file class) a $K' \notin$ the file's classes,
$K' \ne$ `object` and not a builtin class lacking $t$ in its non-`object` MRO `__dict__`s, adds
an R5 violation. Then, for every file class $K$ with a consistent $L[K]$ and every $t$ with
$(A, t)$ a top-level def for some $A \in L[K]_{1..}$: the first $K' \in L[K]$ that is in
$\mathit{ND}$ for $t$, or outside the file under the same exemptions, before any top-level def
of $t$, adds a violation reported as `PYCSL-SEM-OVERRIDE-REFINEMENT`.

### §T.6.43  Slots, dataclass pseudo-fields, explicit `super(X, self)` (routes #360 / #361 / #362 / #363)

_Corresponds to `annotations.md` §7.32._

Inline in §T.6.39's block of `_run_pipeline` (mirror twin `\trusted`; refusals plus a sharper
§T.6.39 #347 summary, no emission change), with its $\mathit{bn}$, $\mathit{clo}$,
$\mathit{DC}$, $\tau$. New facts over the source AST:
$\mathit{PF}(K)$ = for $K \in \mathit{DC}$, the class-body `AnnAssign` names whose annotation
head (through a string annotation and one subscript) is `InitVar` or `KW_ONLY` (a `Name` or an
`Attribute`'s tail), $\mathit{IV}(K) \subseteq \mathit{PF}(K)$ the `InitVar` ones;
$\mathit{SL}(K)$ = the union of $K$'s literal class-body `__slots__` values (a `str` constant
$\mapsto$ itself; a `Tuple` / `List` / `Set` of `str` constants; a `Dict` with `str` constant
keys) and, for `@dataclass(slots=` non-false-literal `)`, $K$'s annotated names — undefined when
$K$ binds no `__slots__`; any other class-body binding of `__slots__` raises
`PYCSL-R360-SLOTS-STORE`; $\mathit{mro}(K)$ = the C3 merge of $[\mathit{mro}(B) \mid B \in
\mathit{bn}(K)] \cdot [\mathit{bn}(K)]$ with $\mathit{mro}(B) = [B]$ for a non-file $B$ (computed
in increasing $|\mathit{clo}|$), $\bot$ when the merge fails or a file base's is $\bot$.

**#360.** $K$ is FULLY SLOTTED iff every $A \in \mathit{mro}(K)$ (else $\mathit{clo}(K)$) is a
file class with $\mathit{SL}(A)$ defined or is `object` / `Generic` / `Protocol`, and
`__dict__` $\notin \bigcup_A \mathit{SL}(A)$. Each store site of §T.6.39 #348 ($r.f$ store /
del / augmented, `setattr` / `delattr`$(r, f, ..)$, $f = \star$ when non-constant) with $K \in
\tau(r)$ fully slotted and $f \notin \bigcup_{A} \mathit{SL}(A)$ raises
`PYCSL-R360-SLOTS-STORE`, except $r$ the first parameter of a `classmethod`.

**#362.** In #346's loop, for a record $C$ with merged `class_invariants` $\ne \emptyset$ and
$\mathit{clo}(C) \cap \mathit{DC} \ne \emptyset$: if $\mathit{PF}(K) \ne \emptyset$ for some
$K \in \mathit{clo}(C)$, raise `PYCSL-R362-INITVAR-INVARIANT`.

**#361.** $\mathit{PF}$ names are removed from #347's dataclass $\mathit{DA}$ and $\mathit{Fld}$
(with `ClassVar`). With $P = \bigcup_K \mathit{PF}(K)$: in every def whose IR function is not
`trusted` / `abstract`, an `Attribute` $r.f$ (any context; $r$ not an imported module) or
`getattr` / `setattr` / `delattr`$(r, \texttt{"f"}, ..)$ with $f \in P$ raises
`PYCSL-R361-DATACLASS-PSEUDO-FIELD`.

**#363.** In #347's statement summary, `super().__init__(..)` keeps its gen (the first in-file
ancestor's $\mathit{DA}$); `super(X, s).__init__(..)` with `Name` arguments, $s$ the
constructor's first parameter, $\mathit{mro}(K) \ne \bot$ and $X \in \mathit{mro}(K)$ gens
$\mathit{DA}(A)$ for the first $A$ after $X$ in $\mathit{mro}(K)$ (stopping, with
$\emptyset$, at a non-file class); every other `super(..)` argument shape gens $\emptyset$.

### §T.6.44  Class-scope bindings, componentwise tuple hashing, fixpoint record hashability, the enum member set (routes #364 / #365 / #366 / #367)

_Corresponds to `annotations.md` §7.33._

Refusals only, inside the inline blocks of §T.6.39 (#349) and §T.6.41 (mirror twin `\trusted`;
no emission change). $B(c)$ = the bindings of class $c$'s scope: every `Name` in `Store` / `Del`
context, `def` / `class` name, import alias, match / except capture reachable from its body
without entering a `def`, `class` or `lambda` body; a binding is a DEF binding iff it is a
top-level undecorated `def`.

**#364.** $\mathit{eq}(c)$ iff `__eq__` $\in B(c)$. If `__hash__` $\in B(c)$, $c$'s own hash is
hashable iff every `__hash__` binding is a def binding, else unhashable; then the §T.6.39 order
(dataclass options, $\mathit{eq}(c)$, inheritance) decides.

**#366.** $U$ = the least fixpoint of $U \mapsto \{c \mid c$ unhashable by the closure rule of
§T.6.39 read against $U$, or $c$ is field-hashed (NamedTuple / namedtuple, frozen or
`unsafe_hash=True` dataclass, along its base closure) and some field annotation $a$ has
$\neg H_U(a)\}$, over the classes and functional namedtuples of the file (iterated to stability;
an unstable bound makes every class unhashable). $H_U$: `None` / `...` and the names `int`,
`str`, `float`, `bool`, `bytes`, `complex`, `None`, `NoneType`, `Literal`, `frozenset`,
`FrozenSet`, `type`, `Type` (also as subscript heads) are hashable; a file class $n$ iff $n
\notin U$; string forms are parsed; `|`, `Optional`, `Union`, `Tuple`, `tuple` need every
argument, `Annotated` / `Final` / `ClassVar` their first; anything else (an untyped field
included) is not.

**#365.** $\mathit{dp}(a)$ = the names of annotation $a$ through Optional / Union / `|` / string
forms and every `Tuple` / `tuple` argument, plus `#UB` for an unhashable builtin container head
reached inside a tuple. For a function, $\mathit{dt}(x)$ = $\bigcup \mathit{dp}$ over $x$'s
annotations $\cup \bigcup \kappa(v)$ over its bound values $v$ (fixpoint), where $\kappa(e)$ is
the class set of §T.6.39 for $e$, entering `Tuple` displays (components marked in-tuple),
`NamedExpr` values and both `IfExp` arms, adding $\mathit{dt}(x)$ for a name, and `#UB` for an
in-tuple list / dict / set display or list-headed name. A hashed expression $h$ (§T.6.39's
positions; a `Set[..]` / `Dict[..]` annotation by $\mathit{dp}$ of its first argument) is
refused iff $\kappa(h) \cap (U \cup \{\texttt{\#UB}\}) \neq \emptyset$.

**#367.** $I(c)$ = the names of $c$'s `_ignore_` when $B(c)$ holds exactly one `_ignore_`
binding and it is a top-level `Assign` / `AnnAssign` of a `Constant` string (split on commas and
blanks) or a `List` / `Tuple` of string constants; any other `_ignore_` raises
`PYCSL-SEM-ENUM-MEMBER-OPERATION` for $c \in \mathcal{E} \cup \mathcal{E}^?$. A top-level binding
$t$ is in $M_c$ iff $t \notin I(c)$, $t$ is not private (`__x`, not ending `__`), not a CPython
dunder / sunder (`enum._is_dunder` / `_is_sunder`), it binds a value, and that value is not a
`Lambda`, a `nonmember(..)` (resolved through `from enum import`), or a call of the unshadowed
builtins `property` / `classmethod` / `staticmethod`; `member(v)` contributes $v$ to the literal
values. Names in $I(c)$, private names and value-less annotations leave the class-attribute set
of §T.6.41 (#356). $D_c$ and the `__new__` test range over $B(c)$.

### §T.6.45  The constructor-invariant goal over the int-field projection (route #226, gen #37)

_Corresponds to `annotations.md` §7.34._

In `_emit_type_decls`, for a record with class invariants $I_1 .. I_k$ (IR), when increments 1/2
emitted no `_check_class_inv_<C>` goal: let $P$ = the fields $f$ of the `FieldGet(self, f)`
leaves of the $I_j$, where every other node is a `BinOp` / `UnaryOp` / `Compare` / `BoolOp`, an
int `Number` or a bool constant. The goal is emitted only if every $f \in P$ is a record field
of type `int`, not in `init_unknown_fields` / `init_unknown_cf_fields`, with value $v_f$ = an
int literal of `init_body`, or $\mathcal{T}_{id}(p)$ for an `init_body` binding `Var p` with $p
\in$ `init_params` of `param_types` `int` / `bool` / unknown, or `field_defaults[f]` when
`init_body` has no binding; let $U$ = those parameters. If some $f' \in P$ has label $\ell(f')
\in U$ and $v_{f'} \neq \ell(f')$, no goal is stated (increments 1/2 skip that case too); the
program never reaches it: before Module 6, `_run_pipeline` refuses a class whose `init_body` binds a
field $f$ read by the invariants to a parameter $p$ with $\mathcal{T}_{id}(p) \in \{g,
\mathcal{T}_{id}(g), \mathcal{T}_{id}(C)\_g\}$ for another field $g \neq f$ they read
(`PYCSL-R226-INIT-PARAM-FIELD-NAME-CLASH`, stage `ir-semantic`). The invariants are
lowered as for the type's `invariant` clauses, and every identifier of the result must be an
$\ell(f)$, $f \in P$. The `init_contract_check.requires` clauses are split at top-level `and`;
a conjunct is kept iff its variables are a non-empty subset of $U$ and its nodes are of the
kinds above, lowered with symbol table $U \mapsto$ `int` and every identifier in $U$. Emitted:
`goal _check_class_inv_<C> : forall <ℓ(P) ∪ U> : int. ℓ(f) = v_f -> .. -> <kept requires> ->
(⟦I_1⟧) /\ .. /\ (⟦I_k⟧)`. Fields outside $P$ are not bound.

### §T.6.46  Dataclass specifier resolution, constructor arity, the enum descriptor rule, MRO hash lookup, hashed fields / subscripts (routes #369 / #370 / #371 / #372)

_Corresponds to `annotations.md` §7.35._

Refusals only, inside the inline blocks of §T.6.39 / §T.6.43 (#369, #371, #372) and §T.6.41
(#370) of `_run_pipeline` (mirror twin `\trusted`; no emission change).

**#369 (resolution).** $\rho(e)$, for a `@dataclass` annotation head $h$ (a string
annotation parsed once, one `Subscript` stripped) or a default callee: an attribute chain
$e_0.a_1 \ldots a_k$ resolves $e_0$ and appends the suffix (only onto a module path); a `Name`
$n$ imported by `from M import X as n` (level 0, $M$ stdlib or `typing_extensions` $\to$
`typing`) is `M.X`, by `import M as n` is `M`; a non-stdlib / relative import, a name imported
twice differently, or imported AND module-bound is $\bot$; a module-level name bound exactly once
(through `if` / `try` / `with` / loop bodies) to a `Name` / `Attribute` / `Subscript` is
$\rho$ of that value, to a string constant $\rho$ of its parse, to another constant `const`, to a
`BinOp` `union`, to a `typing` / `collections` `TypeVar` / `NewType` / ... call `safe`, to a
`def` / `class` that definition; any other binding is $\bot$; a star import makes every unbound
name $\bot$; a builtin is `builtins.n`; an unbound name is `unbound`. With $\Sigma$ =
\{`typing.ClassVar` $\mapsto$ `ClassVar`, `dataclasses.InitVar` $\mapsto$ `InitVar`,
`dataclasses.KW_ONLY` $\mapsto$ `KW_ONLY`\} and $\mathit{sp}(e)$ the tail spelling: refused
(`PYCSL-R369-DATACLASS-SPECIFIER`) iff, for a member of a model dataclass: it is nested in
class-body control flow, $\rho(h) \in \Sigma \wedge \Sigma(\rho(h)) \neq \mathit{sp}(h)$,
$\rho(h) \notin \Sigma \wedge \mathit{sp}(h) \in \Sigma$, $\rho(h) = \bot$; for its default
call $c$: $(\rho = \texttt{dataclasses.field}) \neq (\mathit{sp} = \texttt{field})$, $\rho(c) =
\bot$ or a file `def`, or (for `field`) a positional / `**` / unknown / repeated keyword, both
`default` and `default_factory`, an `init` / `kw_only` that is not a `bool` constant.

**#369 (arity).** $\sigma(C)$ = (positional parameters with a has-default bit, keyword-only
parameters with a has-default bit, `*`, `**`, positional-only names) from the first class $a$ of
$C$'s C3 MRO (§T.6.43) that has a top-level undecorated `def __init__` (its parameters minus the
first), else is a model dataclass with `init=True` (the annotated members of the MRO's
dataclasses from $a$ up, in reverse MRO order, later declarations keeping the first position;
$\rho = $ `ClassVar` skipped, `KW_ONLY` marks the rest of that class keyword-only; `init=False`
excluded; keyword-only by `field(kw_only=..)`, else the class's `kw_only=` or the sentinel;
has-default = a value that is not a `field(..)` call, or a `field` with `default` /
`default_factory`); reaching `object` or the MRO's end gives $\sigma = ()$. $\sigma$ is
undefined for an unknown MRO, a class keyword or a `__new__` binding on the MRO, a non-file
base before $a$, a duplicated class, an `__init__` bound otherwise. A call `C(args, kws)` of a
file class name never rebound, in a function not `\trusted` / `\abstract`, without `*` / `**`
arguments and with $\sigma(C)$ defined, is refused (`PYCSL-R369-CONSTRUCTOR-ARITY`) iff
$|\mathit{args}| > |\mathit{pos}|$ without `*`, a keyword repeats a positional binding or names a
positional-only parameter or no parameter (without `**`), or a parameter without default stays
unbound.

**#370.** In §T.6.41's member scan, for a top-level binding $t$ of class $c$ with value $v$
(after `member(..)` unwrapping): the namespace key is $k = \texttt{\_}c'\,t$ for $t$ = `__x`
not ending `__` ($c'$ = $c$ without leading underscores, non-empty), else $t$; $t$ is private
iff `enum._is_private`$(c, k)$ or $t$ is a source `__x`. $v$ has UNKNOWN status iff $t$ is not
a `def` / `class`, $v$ is no descriptor of §T.6.44 and not `auto()`, and $v$ contains a node
other than `Constant`, `Tuple` / `List` / `Set` / `Dict`, `JoinedStr` / `FormattedValue`,
`UnaryOp` / `BinOp` / `BoolOp` / `Compare` (with their operator and context nodes) and `Name`s
of earlier members. Private and unknown-status names leave $M_c$ and the class-attribute set,
and an unknown-status value makes the literal value list unknown. A `Load` of `_ignore_` in
$B(c)$ makes the member set unknown (refused like a non-literal `_ignore_`). §T.6.41's
class-object rule now admits `C.X` only for $X \in M_C$, or as the `func` of a `Call` when $X$
is an own `def` / builtin `staticmethod(..)` / `classmethod(..)` binding of a file class of $C$'s
MRO.

**#371.** In §T.6.39 / §T.6.44, a class's hashability is decided by the first class of its C3
MRO whose own scope decides (§T.6.44 #364's rule, the dataclass options, an own `__eq__`); a
functional namedtuple on the MRO decides by its $U$ membership; `list` / `dict` / `set` /
`bytearray` are unhashable; other non-file bases are skipped; an unknown MRO is unhashable. Then
§T.6.44 #366's field rule applies.

**#372.** $\phi(c, f)$ = $\bigcup \mathit{dp}(a)$ over $f$'s class-body and `self.f: T`
annotations $a$ $\cup$ for each `self.f = e` of a method of $c$ (first parameter `self`, not a
static / class method): $\mathit{dp}$ of $e$'s annotation for a typed parameter, $\{D\}$ for a
file-class / immutable-record constructor call, the literal's type name, `int` for an operator /
f-string, `list` / `dict` for a display, else `#UNK` (also for a tuple / `for` / `with` /
walrus target). In a function, $\kappa(b.f)$ (§T.6.44 #365) adds $\bigcup \phi(c', f)$ over the
classes $c$ of $\kappa(b)$ and $c' \in$ closure$(c)$; $\kappa(b[i])$ adds, for each annotation
of the name $b$ (or of the field $b$), through Optional / Union / `|` / Annotated / Final /
string forms, $\mathit{dp}$ of: the first argument of `List` / `Sequence` / `MutableSequence` /
`Deque`, the second of `Dict` / `Mapping` / `MutableMapping` / `DefaultDict` / `OrderedDict` /
`ChainMap`, the $i$-th of `Tuple` for a literal in-range $i$ (else every one, `...` dropped);
a `For` / `comprehension` target $n$ over such a name / field gets (into $\mathit{dt}(n)$)
$\mathit{dp}$ of the first argument of the list-likes above and of `Set` / `FrozenSet` /
`AbstractSet` / `MutableSet` / `Iterable` / `Iterator` / `Collection` / `Reversible` / `Container`,
the first (key) argument of the mappings, every `Tuple` argument; three passes. A hashed $h$ with `#UNK` $\in \kappa(h)$ is refused when $U \neq \emptyset$.

### §T.6.47  Nested-def calls in methods, mangled slot names, erased augmented assignment and star-unpacking, `getattr` over class-body bindings (routes #373 / #374 / #375 / #376)

_Corresponds to `annotations.md` §7.36._

All inline (no new def; ledger 3). Mirror twins: `_reset_function_state`, `_handle_augassign_stmt`,
`_handle_assign_stmt`, `_expr_to_whyml` and `_run_pipeline` are `\trusted`; `_lower_getattr` has
no twin.

**#373** (`_reset_function_state`, route #255's call-spelling resolution; $N$ = the names of
the defs nested at any depth in a method of the file, computed from the source in
`_run_pipeline`). For a call spelling $g \in N$ with no `.` that resolves to no unit function,
no class, no enforced builtin and no passthrough builtin: if some method's short name (its unit name without the `<class>__`
prefix) is $g$ — a def nested in a method, lifted to a method of the class — and not every
such method has return annotation `int` or `bool`, then $g \in \mathit{any\_ret}$, i.e.
$\mathcal{T}(g(\bar a))$ (the opaque stub `g_<n> \bar a : int`) is in route #249's erased set:
$\mathcal{T}_{\mathit{binop}}$ lowers `==` / `!=` / arithmetic / ordering on it to the
uninterpreted `pycsl_py_*` symbols and route #252 refuses its flow into a builtin-typed slot.

**#374** (`_run_pipeline`, the #360 store check of §T.6.43). $\mathit{mg}(n, c)$ =
`_` $\cdot$ $c$.lstrip(`_`) $\cdot$ $n$ when $n$ starts with `__`, does not end with `__` and
$c$.lstrip(`_`) $\neq \epsilon$; else $n$. The slot union over the MRO is $\bigcup_{a}
\{\mathit{mg}(s, a) \mid s \in \mathit{slots}(a)\}$; an attribute store `o.n` is checked as
$\mathit{mg}(n, \mathit{lex}(o.n))$ with $\mathit{lex}$ the innermost lexically enclosing
`ClassDef` (no mangling at module scope); a `setattr` / `delattr` string is unmangled.

**#375.** (a) `_handle_augassign_stmt`: under an active `no_exception` (program context), when
route #251's probe `r251_erased?` holds of `Var t` or of the value $v$, $\mathcal{T}(t \mathbin{op}=
v)$ = `begin assert { [@expl:PyCSL-R375 ..] false }; end;` $\cdot$ the previous lowering.
(b) `_expr_to_whyml`, at its head: for a `ArrayLit` / `ListLit` / `List` / `SetLit` / `Set` /
`Tuple` / `MkTuple` / `MkList` node with a `Starred` element (any `no_exception` or none), or
a `Call` with a `Starred` argument (under an active `no_exception`), whose value the probe calls
erased (program context), $\mathcal{T}(e)$ =
`(begin assert { [@expl:PyCSL-R375 ..] false }; ` $\mathcal{T}(e)$ ` end)` (re-entry marked
`_pycsl_r358n`); `_handle_assign_stmt`'s pure-display placeholder of route #310 keeps such a
display evaluated (`(let _ = .. in (any int))`).

**#376** (`_run_pipeline` computes, `_lower_getattr` reads `class_binds_r376`). $CB(c)$ = the
names bound by class $c$'s body (any statement not inside a nested `def` / `class` / `lambda`:
`def` / `class` names, `Name` stores except a value-less annotation, import aliases) $\cup$
$\{\ast\}$ if $c$ binds `__getattr__` / `__getattribute__`; $CB^*(c) = CB(c) \cup
\bigcup_{a} CB(a)$ over $c$'s FILE ancestors (a base outside the file contributes nothing). A
`getattr(o, "k"[, d])` classified ABSENT (route #197: $o$'s record class $c$ is known and does
not declare $k$; also route #309's `_current_record_var_classes` arm) raises
`PYCSL-R376-GETATTR-CLASS-BINDING` when $c \notin \mathrm{dom}(CB^*)$, $\ast \in CB^*(c)$,
$k \in CB^*(c)$, $k \in$ `dir(object)` or $k$ is a dunder; otherwise the default is the answer as
before.

### §T.6.49  Class-body single binding, starred call arguments, `init=False` / `super().__init__` arity, metaclass `__call__` (routes #377 / #378 / #379 / #380)

_Corresponds to `annotations.md` §7.38._

Refusals only; no emission change. #377 / #378 sit in `Module3_Weaver.process` (the shared step
of the file and dependency pipelines, mirror twin `\trusted`), #379 / #380 in §T.6.46's inline
arity block of `_run_pipeline` (mirror twin `\trusted`).

**#377 / #378.** For each class body $B$, let $\beta_B(n)$ be the binding sites of $n$ found by
the scope walk of routes #122 / #130 (every child of $B$ except nested function / lambda bodies:
`def` / `class` statements, `Name` stores and deletes, import aliases, except-as and match
captures). Refused iff $|\beta_B(n)| \geq 2$ and some site is a `def` / `class` statement or the
target of an `AnnAssign`, unless (in source order) every site is a `def`, the first decorated
`property` and each later one decorated `n.setter` / `n.getter` / `n.deleter`; or every site is a
`def` and all but the last are decorated `overload` / `typing.overload`.

**#379.** For a call $c$ with a `Starred` positional or a `**` keyword in a function not
`\trusted` / `\abstract`: the candidate callees are the file class $C$ (a name never rebound or
imported: refused outright), the module-level `def`s named $f$ (a name not imported), or, for
`e.m(..)`, every top-level `def m` of a file class (dropping the first parameter except for a
`staticmethod`, or a plain method called as `C.m(..)` on a file class). Refused
(`PYCSL-R379-STARRED-CALL-ARGUMENT`) iff there is a candidate and $c$ has a `**` argument, or a
candidate has no `*args`, or a `Starred` sits at a position below the candidate's positional
parameter count, or the `*args` name occurs in the candidate's `#@` lines.

**#380.** In §T.6.46's $\sigma$: a model dataclass with `init=False` (a literal) is skipped (the
walk continues), so `object` may be reached. For `super().__init__(args, kws)` in a method of
$X$ (or `super(X, self)`): for every file class $S$ with known MRO $m \ni X$, with $t$ the part of
$m$ after $X$: $t = []$ gives $\sigma = ()$ when $\sigma(S)$ is defined; $t_0$ a file class with
$\mathrm{MRO}(t_0) = t$ and $\sigma(t_0)$ defined gives $\sigma(t_0)$; otherwise no check. For
`C.__init__(e, args, kws)`, $\sigma(C)$ binds `args`. Each $\sigma$ is checked by §T.6.46's
binding rule. A construction `C(..)` (§T.6.46's call shape) is refused
(`PYCSL-R380-METACLASS-CALL`) iff a class of $C$'s MRO has a `metaclass=` $M$ that is neither the
unrebound `type`, nor `abc.ABCMeta` (imported from `abc`), nor a file class whose MRO consists
of file classes binding no `__call__` and `type` / `ABCMeta`.

### §T.6.48  The constructor-invariant goal over array-length terms (route #226 increment 2c, gen #37)

_Corresponds to `annotations.md` §7.37._

Extends §T.6.45. A leaf `ArrayLen(self.f)` of the $I_j$ is admitted when $f$ is a record field
whose emitted label type $\tau_f$ (the `_emitted_record_field_types` entry of $\ell(f)$) starts with
`array `, and $f \notin$ `init_unknown_fields` / `init_unknown_cf_fields`; such $f$ join $P$ as
ARRAY fields. Their binding: for an `init_body` binding `Var p` with $p \in$ `init_params` whose
`param_types` entry is not `int` / `bool` / `str` / `float`, $v_f = \mathcal{T}_{id}(p)$ and $p$
is typed $\tau_f$; with no `init_body` binding and `field_defaults[f]` $= N \ge 0$ (Module 5's
literal initial length, `_array_init_size`), the premise is `(Array.length ℓ(f)) = N`; otherwise
no goal. A parameter bound to both an int and an array field, or to two array fields of
different types, yields no goal. Every identifier of the lowered invariants must be an
$\ell(f)$, `Array` or `length`. A `requires` conjunct may also contain `Call(len, [Var p])` or
`ArrayLen(p)` for an array-typed $p \in U$, lowered with symbol table $p \mapsto$ `list` (so to
`Array.length p`). Binders are grouped by type in first-occurrence order:
`forall <b..> : τ1, <b..> : τ2. ...`; an all-int binder list prints as in §T.6.45. Emitted:
`goal _check_class_inv_<C> : forall <groups>. <premises> -> (⟦I_1⟧) /\ .. /\ (⟦I_k⟧)`.

### §T.6.51  The constructor's end state of list fields; unstatable `\length` goals refused (routes #384 / #385, gen #37)

_Corresponds to `annotations.md` §7.40._

Refines §T.6.48's binding of an ARRAY field $f$ of $P$ by a map $\sigma_C(f)$ computed in
`_run_pipeline` over the source of $C$'s own `__init__` (a class without one takes its first file
base's map), passed to Module 6 as `ctor_len_r384`. Walking the TOP-LEVEL statements in order:
a store `self.f = e` with $e$ a fresh list of literal length — `List` without `Starred` ($n$ =
number of elements), `[..] * K` / `K * [..]` ($n \cdot \max(K, 0)$), `bytearray(K)` / `bytes(K)`
with $K \ge 0$, `list()` / `bytearray()` / `bytes()` ($0$), $K$ an int literal (or unary minus) or a
module constant with exactly one binding in the file and the builtin names unbound — sets
$\sigma(f) = \mathrm{LEN}(n)$; `self.f = p`, $p$ an `__init__` parameter, sets $\mathrm{PARAM}(p)$;
any other store sets $\mathrm{UNKNOWN}$. A statement `self.f.m(args)` with $\sigma(f) = \mathrm{LEN}(n)$
and call / attribute / subscript / walrus / lambda / starred-free args maps $n$ by `append`,
`insert` $+1$, `extend(<list or tuple display>)` $+k$, `pop()` / `pop(i)` ($-1$, $n \ge 1$,
$-n \le i < n$), `clear` $0$, `reverse` / `sort` $n$; other methods: UNKNOWN. In every statement,
an occurrence of `self.g` ($g$ already stored) other than the statement's own target / receiver,
`len(self.g)`, or a non-slice `self.g[i]` load / store sets $\sigma(g) = $ UNKNOWN; a `Call` other than
`len` after a PARAM store, and an `__init__` attribute (another constructor) after any store, set
the stored fields UNKNOWN. A PARAM($p$) field becomes UNKNOWN if $p$ occurs anywhere in `__init__`
other than as that store's value, `len(p)` or a non-slice `p[i]`; a `return` / `yield` / `await`
outside nested scopes makes every field UNKNOWN. In Module 6: $\sigma(f) = \mathrm{LEN}(n)$ gives the
premise `(Array.length ℓ(f)) = n` (overriding `field_defaults` and admitting $f \in$
`init_unknown_fields`); UNKNOWN, or §T.6.48's binding failing for an array field, is a STATE
obstacle: no goal, and when the projection found no TERM obstacle Module 6 emits the marker
comment `(* PYCSL-R384-NO-GOAL <C>: <why> *)` and `_run_pipeline` raises
`PYCSL-R384-INVARIANT-GOAL-UNSTATABLE` on it after `transpile()`. Before Module 6, a `Call` whose function is `super(..).__init__` or `B.__init__`
($B$ a file class) in a method of a file class $K$ is refused
(`PYCSL-R385-DELEGATED-INIT-REQUIRES-UNCHECKED`) when a file class reachable from $K$'s bases (resp.
$B$ and its bases) has a non-empty `init_contract_check.requires` and a `param_types` entry outside
`""`, `int`, `bool`.

### §T.6.52  Locally rebound builtin names; class-body members under `global` or a compound statement (routes #386 / #387, gen #37)

_Corresponds to `annotations.md` §7.41._

Both are side conditions of `Module3_Weaver.process` (file and dependency pipelines); the
translation is unchanged where they hold. Let $\mathcal{B}$ be route #131's builtin-name set
(`_nb_builtin_names`). (#386) For every scope $S$ that is the module or a function / method
body (not descending into nested def / class / lambda bodies or comprehension targets), let
$R(S) \subseteq \mathcal{B}$ be the names bound in $S$ by a store, a parameter, a nested
`def` / `class` statement (function scopes only), or an `import` / `from .. import` other than
one from `builtins` / `__builtin__`. If some $x \in R(S)$ has a `Name` load anywhere under $S$'s
node (nested scopes included), the translation is undefined (refused). For every `Lambda` with a
parameter $x \in \mathcal{B}$, and every comprehension with a target name $x \in \mathcal{B}$, a
load of $x$ under that node is likewise refused. (#387) For every `ClassDef` body $K$, walking
$K$ without entering nested def / class / lambda bodies: a `Global` / `Nonlocal` statement naming
$x$ with $x$ among $K$'s binding sites is refused; a `FunctionDef` / `AsyncFunctionDef` /
`ClassDef` / `AnnAssign` reached through an `If`, `While`, `For`, `AsyncFor`, `Try`, `TryStar`,
`With`, `AsyncWith` or `Match` node of $K$ is refused, unless every such node on the path is an
`If` whose test is the constant `True` and the path enters its `body`. Both append to the existing raise sites
(route #131's "a name's runtime value is not the one the model reads", route #122's "a name's
runtime binding is not the `def` the model resolves it to").

### §T.6.53  Unmodelled base classes (systematic rule S1, gen #37)

_Corresponds to `annotations.md` §7.42._

A side condition of `_run_pipeline` (the route #341 base walk; the translation is unchanged where
it holds). Let $M$ be the BASE-MODEL table $\{$`builtins.object`, `builtins.type`, `enum.`$\{$`Enum`,
`IntEnum`, `Flag`, `IntFlag`, `StrEnum`$\}$, `typing`/`typing_extensions.`$\{$`NamedTuple`,
`Protocol`, `Generic`, `TypedDict`$\}$, `abc.ABC`, `ast.NodeVisitor`, `ast.NodeTransformer`$\}$.
Outside the top-level `if __name__ ...:` driver, let $L$ be the set of loaded names and, for each
`ClassDef` $C$ with $C \in L$, resolve each base head (a `Name` or attribute chain, through a
subscript) through the file's `import` / `from .. import` bindings, or as a builtin class name not
rebound in the file, to a qualified pair $(m, a)$. If the root of $m$ is a standard-library module
(`sys.stdlib_module_names`, `builtins`, `typing_extensions`), $(m, a) \notin M$, and $a$ is neither
a builtin `BaseException` subclass nor `int` / `str` beside a base of $M$ from `enum`, the translation
is undefined (refused, `PYCSL-S1-UNMODELLED-BASE`). The same condition is applied, WITHOUT the
$C \in L$ filter, to every class of each dependency module reached from the file's imports (route
#181's resolution: the file's directory and `--import-path`, transitively); and an unresolved base
name in a file containing `from` $m$ `import *` with $m$ a standard-library module is refused.
File classes and user-module bases are unaffected.

### §T.6.54  `getattr` defaults over a partially modelled lookup (systematic rule GD, gen #37)

_Corresponds to `annotations.md` §7.43._

Extends route #376's side condition on `getattr(o, n, d)` with $o$ a known record of class $C$ and
$n$ not a field of $C$ (ABSENT): the per-class map $B(C)$ (`class_binds_r376`) additionally
contains `*` when a class of the base closure of $C$ over the file's classes has a base that
resolves to a standard-library module or a builtin class other than `object` (or is unresolved in
a file with a standard-library star import), or when the module outside the top-level `if __name__ ...:` driver
contains a call of `setattr` / `delattr` / `vars` or an attribute `__dict__` / `__setattr__` /
`__delattr__`; and $B(C)$ contains `_C__x` for every attribute `__x` (not a dunder) under $C$'s
body. If `*` $\in B(C)$ or $n \in B(C)$ the translation is undefined (refused); otherwise it is
unchanged (the default $d$).

### §T.6.55  Typing constructs as values (systematic rule TC, gen #37)

_Corresponds to `annotations.md` §7.44._

Let $T$ be the least set of the file's classes (outside the `__main__` driver) such that $C \in T$
when a base of $C$ resolves to `typing` / `typing_extensions` `.Protocol` or `.TypedDict`, or a
base of $C$ is a file class of $T$ obtained through `TypedDict`. A `Name` load of $C \in T$ outside
the driver that is not under an annotation, a `returns`, a class base, or the first two arguments /
the keyword values of a `cast` / `TypeVar` / `NewType` call makes the translation undefined
(refused, `PYCSL-TC-TYPING-CONSTRUCT-VALUE`).

### §T.6.56  Starred arguments to builtins (systematic rule SB, gen #37)

_Corresponds to `annotations.md` §7.45._

Extends route #379's side condition: in a lowered function, a `Call` whose callee is a `Name` $f$
that the file neither binds nor imports, that names no file class, and that is an attribute of
the `builtins` module, with a `Starred` positional argument or a `keyword` whose `arg` is `None`,
makes the translation undefined (refused).
### §T.6.57  Outside bases and stdlib values by their real class, containers in every hashing position, propagated element types (routes #381 / #382 / #383, gen #37)

_Corresponds to `annotations.md` §7.46._

Refusals only, inside the inline block of §T.6.39 / §T.6.44 / §T.6.46 of `_run_pipeline` (mirror
twin `\trusted`; no emission change). **Resolution.** Each base or annotation name $n$ not bound
by a file class, a functional namedtuple or a module type alias is mapped to a qualified name
$q(n)$ through the file's imports (`_im369`) or `builtins.`; $q(n) = ?$ when $n$ is bound in the
module otherwise. For $q$ in an allow-listed stdlib module whose spec lies in the interpreter's
stdlib directory, the object $o$ is imported (a `typing` alias by `get_origin`); $\beta(n)$ (as a
base) $= U$ when $o$ is not a class, `__hash__` is None, or $o$ is a subclass of `slice` /
`memoryview` / `types.MappingProxyType` / `weakref.ref`; else $S$. $\nu(n)$ (as a value) $= ?$
for `Any` / `object` / a TypeVar / an unresolvable name; $U$ as $\beta$ or when one of `list` /
`dict` / `set` / `bytearray` / `deque` is a subclass of $o$; else $S$. A name with several
resolutions takes the worst ($U > ? > S$). **#381.** In §T.6.46 #371's MRO walk an outside base
with $\beta = U$ decides unhashable (an $S$ base is skipped). **#382.** For a hashed $h$, the
`#UB` (container) mark of §T.6.44 #365 is added at any depth (not only inside a tuple) for a
name whose annotation head is a container and for a display; every class name $c \in \kappa(h)$
outside the file adds `#UB` when $\nu(c) = U$ and `#UNK` when $\nu(c) = ?$; an un-parameterised
`tuple` / `Tuple` type adds `#UNK`. **#383.** $\tau(e)$, a set of type expressions per
expression node, computed in post-order passes over the function: annotations of
parameters / locals (through module aliases $\alpha$: a module name bound once to a name /
attribute / subscript / `|` / string type, not an import, class or def), $\{C\}$ for `self` and
constructor calls, literal types, displays and comprehensions as `#list[..]` / `#set[..]` /
`#dict[..]` / `#tuple[..]`, a subscript's element / value / component (a slice keeps the
sequence), field annotations and stores (§T.6.46 #372's $\phi$, plus a parameter's annotation),
`-> T` of a file method / function, the mapping / sequence / set / `str` methods and the common
builtins; un-annotated locals join $\tau$ of all their bindings (a local read before any binding
is typed is $\bot$, dropped at bindings; the passes iterate to a fixpoint, at most 12, else every
local is underivable); a field absent from $C$'s file closure contributes only the fields of the
file subclasses of $C$ (underivable when a class body binds the name, an outside base is on the
MRO, the attribute is stored through a non-`self` receiver, or the file uses `setattr` /
`vars` / `__dict__` / `__setattr__`); anything else is UNDERIVABLE (`#UND`, no class), and so is a
$\nu = ?$ atom of a `Subscript` / `Call` / `Starred` node or of an iteration element. Each
$\tau(e)$, unfolded through Optional / Union / `|` / Annotated / Final / ClassVar and Tuple
components, adds its class names to $\kappa(e)$. A hashed $h$ with `#UNK` $\in \kappa(h)$ is
refused when $U \neq \emptyset$ (§T.6.46).

### §T.6.58  A value of an unknown class is refused in a hashing position (allow-list polarity, route #383 addendum, gen #37)

_Corresponds to `annotations.md` §7.47._

Refusal only, in the same inline block as §T.6.57 (mirror twin `\trusted`; no emission change).
The un-parameterised `tuple` / `Tuple` atom of $\tau$ now adds `#UNKT` to $\kappa$ (not
`#UNK`). Let $G$ be the set of guarded subscript nodes: for each `If` whose first body statement
$s$ is an `Assign` / `AnnAssign` / `AugAssign` / `Expr` / `Return` with no `Call` / `NamedExpr` /
`Yield` / `YieldFrom` / `Await` / `Lambda` node, and each conjunct `A in B` of its test (a single
`In`; the test itself or an `and` conjunct whose later conjuncts contain none of those nodes), a
subscript node `B'[A']` of $s$ is in $G$ when $\delta(A') = \delta(A)$ and $\delta(B') =
\delta(B)$, where $\delta$ rewrites `x.get(K)` ($K$ a constant, $x$ a local whose annotation
heads are all `dict` / `defaultdict` / `OrderedDict` and with no binding of unknown class) to
`x[K]` and is the AST dump of an expression built only of names, attributes, subscripts and
constants (undefined otherwise). For a hashed $h$ at node $n$: when `#UNK` $\in \kappa(h)$ or
`#UNKT` $\in \kappa(h)$, $\kappa(h)$ gains $U$ (§T.6.46, as before) and, when `#UNK` $\in
\kappa(h)$ and $n \notin G$, also `#UB`; $h$ is refused when $\kappa(h) \cap (U \cup
\{\texttt{\#UB}\}) \neq \emptyset$.

### §T.6.59  Base names resolved by scope (route #392, gen #37)

_Corresponds to `annotations.md` §7.48._

Refusals only, inline in `_run_pipeline` before S1 (§T.6.53; mirror twin `\trusted`; no
emission change). For every class statement $K$ of the main file and of each dependency module,
and each base whose head (through one subscript and an attribute chain) is a name $x$, let
$s_0$ be the scope enclosing $K$ and $s_0, s_1, \ldots$ the chain of enclosing scopes in which
class bodies other than $s_0$ are skipped. $B(s)(x) \subseteq \{\mathit{class}, \mathit{import},
\mathit{other}, \mathit{global}\}$ collects the bindings of $x$ in $s$ (its parameters, and its
body without entering nested def / class / lambda bodies: a `class` statement, an import, a
`global` declaration, any other store / def / except / match capture / `nonlocal`). $\rho(x)$ is
read at the first $s_i$ with $B(s_i)(x) \setminus \{\mathit{global}\} \neq \emptyset$ (a
$\mathit{global}$ in a function jumps to the module): $\mathit{class}$ when that set is
$\{\mathit{class}\}$, $\mathit{import}$ when it is $\{\mathit{import}\}$, $\mathit{other}$
otherwise; when no scope binds $x$, $\mathit{builtin}$ if `builtins` has $x$, else $\mathit{star}$
if the module has a standard-library star import, else $\mathit{unbound}$. S1 resolves a base
through the imports only when $\rho = \mathit{import}$, as `builtins.x` only when $\rho =
\mathit{builtin}$ and as a star-import name only when $\rho = \mathit{star}$. In §T.6.46 / §T.6.57,
a `Name` base $x$ of a main-file class with $\rho(x) \in \{\mathit{import}, \mathit{builtin},
\mathit{star}\}$ while a class named $x$ exists in the file is the token `x@` in the base lists
(so in $\mathit{clo}$ and the C3 MRO), and $\beta(\texttt{x@})$ is computed from $q(x)$ as for
any outside base.

### §T.6.60  Sources of a hashed value's class: module globals, class attributes, stdlib objects, copies, iterables (route #394, gen #37)

_Corresponds to `annotations.md` §7.49._

Refusals only, in the inline block of §T.6.57 (mirror twin `\trusted`; no emission change).
New atoms: `#H` (a hashable object, no class), `#UNK` as an element type. $\gamma(g)$ for a
module name bound once (§T.6.57's module binding map, no `global g`, not imported) and
$\gamma_C(k)$ for a name bound once at the top of the body of a file class $C$ (a single
definition of $C$) are computed (two passes, in binding order) by a post-order map $\mu$ over the
initializer: a constant / f-string $\mapsto$ its type; a tuple display $\mapsto$
`#tuple[`$\mu$ of components`]`; a lambda, a module class / def name $\mapsto$ `#H`; a call of a
module file class or functional namedtuple $\mapsto$ that class, of an unbound builtin
`frozenset` / `str` / `int` / `float` / `bool` / `bytes` / `complex` / `range` $\mapsto$ that
type, of `list` / `sorted` / `set` / `dict` $\mapsto$ `#list` / `#set` / `#dict` of `#UND`; a
name in $\gamma$ $\mapsto \gamma$; an operator over primitives $\mapsto$ their types (a comparison
`bool`); `D.k` $\mapsto \gamma_D(k)$; a list / set / dict display $\mapsto$ `#list[E]` / `#set[E]`
/ `#dict[K, V]` with $E, K, V$ the unions of the element / key / value $\mu$ when the root
display is the whole initializer and the bound name is READ-ONLY (§7.49), else `#UNK`; anything
else `#UND`. Class bodies: an undecorated / static / class method or a nested class $\mapsto$
`#H`; a sole `@property` $\mapsto$ its `-> T`; an `Enum` member (a non-sunder name of a class
whose closure reaches an `enum.` base) $\mapsto C$. $\iota(e)$ for a load rooted at a
standard-library import or an unbound builtin name: the real object $o$ (imported as §T.6.57):
a primitive constant $\mapsto$ its type, `hash(o)` succeeding $\mapsto$ `#H`, else `#UND`. In
$\tau$ (§T.6.57): a name load that is not a parameter (of the function or of any def / lambda
nested in it), a nested def / class name, a local, or a binding of an enclosing function
$\mapsto \gamma(x)$, else $\iota$; `C.k` for a module file class $C$ $\mapsto \gamma_A(k)$ of the
first class $A$ of $C$'s MRO whose body binds $k$ (`#UND` past an outside base, when $k$ is stored
through a non-`self` receiver, or with dynamic attribute stores); `o.k` with $o$ of class $C$ and
no field $k$ in $C$'s closure $\mapsto$ the union over $C$ and its file subclasses of the first
binder's $\gamma_A(k)$ (same exclusions); `copy.copy(x)` / `copy.deepcopy(x)` /
`dataclasses.replace(x, ..)` (callee resolved through a stdlib import, not shadowed)
$\mapsto \tau(x)$. At a call `set` / `frozenset` / `Counter` / `dict` / `.fromkeys` whose first
argument $a$ is neither a display nor a §T.6.44 annotated name, the hashed values are the
element types $\epsilon(a)$ (for `dict`: the first component of each `#tuple`, `#UND`
otherwise; skipped when every $\tau(a)$ atom is a mapping), unfolded like $\kappa$.

### §T.6.61  Hashability over file subclasses (route #395, gen #37)

_Corresponds to `annotations.md` §7.50._

Refusal only, in §T.6.46's unhashability fixpoint (mirror twin `\trusted`). Let $H_v$ be the IR
functions that are neither `trusted` nor `abstract` and carry `no_exception_all`, and $D$ the file
classes with a top-level `def __hash__` whose IR name `c____hash__` ($c$ the lowered class name)
is not in $H_v$. After each fixpoint step computes $u'(C)$ for every class, every class $A$ in
$\mathit{clo}(C) \setminus \{C\}$ of a file class $C$ with $u'(C)$ or $C \in D$ gets $u'(A) =
\mathit{true}$; the iteration continues to the fixpoint. $U$ is its true set.

### §T.6.63  Builtin exception bases and their constructor (route #393, gen #37)

_Corresponds to `annotations.md` §7.52._

Refines §T.6.53: the builtin-exception exemption from $M$ holds only for $a \in E$, the
allow-list of builtin exception classes whose constructor accepts every positional arity
(`BaseException`, `Exception`, `ArithmeticError`, ..., `ZeroDivisionError`; the literal set
`_exok1` of `_run_pipeline`), or $a \in Y = \{$`SyntaxError`, `IndentationError`,
`TabError`$\}$; $a \in \{$`BaseExceptionGroup`, `ExceptionGroup`, `UnicodeDecodeError`,
`UnicodeEncodeError`, `UnicodeTranslateError`$\}$ makes the translation undefined. An entry
$a \in Y$ yields the shape SYNTAX: at most two positional arguments, none starred, no keyword,
and a second one only as a `Tuple` display of 4 or 6 non-starred elements. In route #369's signature
walk over the file MRO of a class $C$ (§T.6.49), the first non-file entry $a \in E$, not bound or
imported by the file, yields the signature $(\mathit{self}, {*}\mathit{args})$ with no keyword
parameter; the same signature checks `super().__init__(..)` when the next MRO entry is such an
$a$, and `a.__init__(self, ..)`. A construction `C(..)` of a class whose MRO contains such an
$a$ and whose signature is undetermined makes the translation undefined
(`PYCSL-R369-CONSTRUCTOR-ARITY`). Emission is unchanged where the translation is defined.

### §T.6.64  `getattr` defaults: subclass closure and store forms (routes #396 / #397, gen #37)

_Corresponds to `annotations.md` §7.53._

Replaces the definition of $B(C)$ in §T.6.54. Let $\mathrm{own}(C)$ be: every `str` field (other
than `type_comment`) of every node under $C$'s class scope (not entering a `def` / `lambda`),
except nodes of the kinds `Constant`, `keyword`, `arg`, `MatchClass`, `alias`, f-string
`Interpolation`, and `Name` / `Attribute` in `Load` context, plus the alias names of an
`Import` / `ImportFrom` (`*` for a star); the `attr` of every `Attribute` in `Store` / `Del`
context inside a `def` of $C$'s body (not a `@staticmethod`) whose receiver is a `Name` equal to
that `def`'s first parameter (never rebound, nor shadowed by a nested parameter, there); `_C__x`
for every `__x` of these and every attribute `__x` under $C$; `*` as in §T.6.54. Let $G$ be the
`attr` of every other `Store` / `Del` `Attribute` of the module outside the top-level driver
(class-scope ones included). With $\mathrm{anc}(D)$ the file-class ancestors of $D$
(reflexive), $B(C) = G \cup \bigcup \{\mathrm{own}(A) \mid D \text{ a file class},\ C \in
\mathrm{anc}(D),\ A \in \mathrm{anc}(D)\}$, plus `*` under the dynamic-store condition of
§T.6.54 (now also a call of `exec` / `eval`). The side condition of §T.6.54 is otherwise unchanged.

### §T.6.65  TypedDict values: attributes and optional keys (route #398, gen #37)

_Corresponds to `annotations.md` §7.54._

Extends §T.6.55: an `Assign` `X = f(..)` with $f$ resolving to `typing` / `typing_extensions`
`.TypedDict` puts $X$ in $T$. For each file TypedDict $X$ (class or functional form) let $K(X)$
be its keys and $O(X) \subseteq K(X)$ its optional keys (§7.54; `*` when the key set or the
totality is not a literal). On the resolved IR of every non-`trusted` function, the translation
is undefined (`PYCSL-R398-TYPEDDICT-ACCESS`) at: an `Attribute` node of the function's `body`
(outside `body` an `Attribute` is treated as a key read below) with `attr` $\in \bigcup K$
whose `object` is not a `Var` `self` / `cls` or a `Var` whose symbol-table type is known and
names no file TypedDict; a `Subscript` with a `String` index, a `get` / `pop` / `setdefault` call
with a `String` first argument, or an `in` / `not in` with a `String` left operand, whose key is in
$\bigcup O$ (or `*` occurs), unless the receiver is a `Var` of a known type that is not a TypedDict
$X$ with the key (or `*`) in $O(X)$.

### §T.6.66  Builtins reached through `builtins` imports (route #399, gen #37)

_Corresponds to `annotations.md` §7.55._

Extends §T.6.56: the callee also counts as a builtin when it is a `Name` bound by `from builtins
import a [as b]`, or an `Attribute` whose value is a `Name` bound by `import builtins [as b]`
(or `__builtins__`, not rebound) — resolved through the file's imports outside the driver.

### §T.6.67  `ast.NodeVisitor` dispatch (route #400, gen #37)

_Corresponds to `annotations.md` §7.56._

Let $V$ be the file classes whose base closure over file classes contains a base resolving to
`ast.NodeVisitor` / `ast.NodeTransformer`. If some $C \in V$ derives from `NodeTransformer`, or
$C$ or a file ancestor of $C$ defines a `def visit_*`, then a `Call` whose `func` is an
`Attribute` `visit` / `generic_visit` inside a module-level function or a method whose IR entry
is not `trusted` / `abstract` makes the translation undefined
(`PYCSL-R400-NODEVISITOR-DISPATCH`).

### §T.6.68  Hashing sites call `__hash__` / `__eq__` (route #402, gen #37)

_Corresponds to `annotations.md` §7.57._

Refusal only, in §T.6.46's unhashability fixpoint and §T.6.61's step (mirror twin `\trusted`;
no emission change). $H_v$ (§T.6.61) is narrowed to the IR functions that are neither `trusted`
nor `abstract`, carry `no_exception_all`, have an empty `requires` list and a
`return_annotation` of `bool` for a name ending in `____eq__`, `int` otherwise. In the MRO walk,
when the deciding class $A$ binds `__hash__` only by top-level undecorated `def`s and
`a____hash__` $\notin H_v$ ($a$ the lowered name of $A$), $u'(C) = \mathit{true}$.

A second least fixpoint $q$ over the file classes and functional namedtuples: $q'(C)$ is true when
$C$'s C3 linearisation is unknown, or its first file class $A$ that binds `__eq__` in its own
body has a binding list other than one top-level undecorated `def` with `a____eq__` $\in H_v$, or
its first file class that is a `@dataclass` with `eq` $\ne$ `False` or an immutable record (§T.6.39's
$\mathit{imm}$) has, over its base closure's annotated fields, an annotation that is not eq-safe
under $q$ (an `_HB366` name; a file class $K$ with $\neg q(K)$; Optional / Union / `|` / Tuple /
List / Set / FrozenSet / Dict of eq-safe annotations; the first argument of Annotated / Final /
ClassVar; Literal / type), or its functional-namedtuple ancestor has $q$; then every file base
of a class with $q'$ gets $q'$. $Q$ is the true set at the fixpoint (all classes, when the
iteration bound is reached).

At a hashing site $n$ (§T.6.46) that is not a `Call` of the builtin `hash`, a `Set` with one
non-`Starred` element or a `Dict` with one non-`None` key, the hashed value's class set $K$
(including its tuple elements; `#UNK` / `#UNKT` read as $Q$) with $K \cap U = \emptyset$ and
$K \cap Q \ne \emptyset$ makes the translation undefined (`PYCSL-R402-UNVERIFIED-EQ`).
### §T.6.69  Constructor goals are mandatory for admitted class invariants (route #226 polarity flip, run #3)

_Corresponds to `annotations.md` §7.58._

Let $C$ be a record of a class defined in the translated file with $\mathit{Inv}_C \neq \emptyset$,
whose record type is emitted. The translation is defined only if Module 6 emits
`goal _check_class_inv_c` for $C$ (§T.6.45 / §T.6.48 / §T.6.51, or stage 2d below), or $C$'s
`__init__` (its own, else its first file base's) is `\trusted`; otherwise it is undefined
(`PYCSL-R226-INVARIANT-GOAL-NOT-STATED`). Stage 2d runs when no earlier goal and no route #384
state obstacle exists. `_run_pipeline` computes, from the source AST, the end state
$\sigma(f)$ of every field stored by `__init__`'s top-level statements: $\mathsf{INT}(n)$,
$\mathsf{BOOL}(b)$, $\mathsf{PARAM}(p)$ (p a parameter with no store / `global` / `nonlocal` in
`__init__`), $\mathsf{EXPR}(e)$ (e over int parameters and literals, `+ - *`, unary `-`, two-argument
`max` / `min` as `if a >= b then a else b`), or
unknown; $\mathit{fill}(f) = c$ for `[c] * K` / `bytearray(K)` with only `len` / element-read
mentions afterwards; every state is unknown when `__init__` has a bare `self` other than
`type(self)`, a non-leading `super`, a store into another object's attribute, a
`return` / `yield` / `await`, or a call outside `len type int bool abs min max` after a store.
With $L$ = the labels of $C$'s fields occurring in the lowered invariant $\overline{I}$
(string literals removed), stage 2d emits
$\forall \vec{\ell}, \vec{p}.\ \bigwedge_{\ell \in L} \pi(\ell) \to \bigwedge R \to \overline{I}$,
with $\pi(\ell)$ = `f = n` / `f = b` / `f = p` / `f = e`, or for an array field the route #384
premise `(Array.length f) = N` plus `forall _k226. 0 <= _k226 < N -> f[_k226] = c` when
$\overline{I}$ reads elements (else no goal); $R$ the `#@ requires` conjuncts whose
identifiers are bound parameters, quantifier / `let` binders, Why3 builtins or other records'
labels. No goal when a parameter binder is the label of a field it does not bind or occurs in
$\overline{I}$, when $\overline{I}$ names `_k226`, or when a field of $L$ has another type.

### §T.6.70  Bespoke lowerings and the declared contract (route #420)

_Corresponds to `annotations.md` §7.59._

Let $R$ be a shape recognizer of Module 6 (`generic_fold.recognize_*`, and the
`FunctionEmissionMixin`-local `_is_*` / `_recognize_*` handlers of `_emit_function_block`) and
$H_R \subseteq \{\texttt{requires}, \texttt{ensures}\}$ the clause kinds its group emits as
obligations on the function's top-level `let`. $R$ may replace $f$ only if
`bespoke_contract_ok`$(f, H_R)$: $f$ is `trusted` / `abstract`, or every clause of a kind
$\notin H_R$ is the literal `True`, every `raises` entry has no condition or the literal `True`,
and $f$ has no `no_exception` / `no_exception_all`. A multi-function recognizer (cluster, pair,
family) whose result references a function failing the predicate is re-evaluated on the
functions satisfying it. A function $R$ declines is translated by the generic function rules, which carry its
contract or make the translation undefined.

### §T.6.71  A verified `__eq__` takes any `other` (route #403, gen #37)

_Corresponds to `annotations.md` §7.60._

Refusal only, in §T.6.68's EQ-RISKY fixpoint (mirror twin `\trusted`; no emission change). A
class body's `__eq__` binding counts as the one verified `def` only when, besides §T.6.68's
conditions, its `args` are exactly two positional parameters (no positional-only, keyword-only,
`*` or `**` parameter) and the second one's annotation is the `Name` `object` (no file class
named `object`). Otherwise $q'(C)$ holds for the deciding class and the hashing sites of §T.6.68
are undefined (`PYCSL-R402-UNVERIFIED-EQ`).

### §T.6.72  Metaclasses (route #404, gen #37)

_Corresponds to `annotations.md` §7.61._

Refusal only, in S1 (§T.6.53; no emission change). The BASE-MODEL table no longer holds
`builtins.type`; a base resolving to it is admitted iff the class body is a sequence of
`Pass` / `Expr(Constant(str | Ellipsis))` and no `Attribute` store / delete on the class name
nor `setattr` / `delattr` of it occurs in the module. A `metaclass=` keyword whose value
resolves (through the imports of the module, or as the unbound builtin `type`, or as the name
of a `ClassDef` of the module) to anything other than `builtins.type`, `abc.ABCMeta`,
`enum.EnumMeta`, `enum.EnumType` or a file class makes the translation undefined
(`PYCSL-S1-UNMODELLED-BASE`); a file class deriving from `type` through file classes (a least
fixpoint over `Name` bases the scope resolver reads as "class") must satisfy the same body
condition. The checks apply to the classes S1 checks (named outside the `__main__` driver in
the main file, closed under the `metaclass=` names of checked classes; every class of a
dependency module).

### §T.6.73  Classes created by calls (route #405, gen #37)

_Corresponds to `annotations.md` §7.62._

Refusal only, over the whole module tree (the `__main__` block included; no emission change). A
`Call` whose callee resolves, through every import of the module, to `builtins.type` (with at
least two arguments, or a starred one), `builtins.type.__new__` (at least three),
`types.new_class` or `dataclasses.make_dataclass` (with a `bases=` or `**` keyword) makes the
translation undefined (`PYCSL-R405-DYNAMIC-SUBCLASS`) unless its bases argument is the empty
`Tuple` literal.

### §T.6.74  The call census of attribute stores (route #406, gen #37)

_Corresponds to `annotations.md` §7.63._

Refusal only (no emission change). Over the module tree without its top-level `if __name__
...` blocks, $\mathit{dyn}_{406}$ holds when a string `Constant` is `__dict__` / `__setattr__` /
`__delattr__` / `__class__`, or a `Call` with an argument or keyword value of kind `Name` /
`Attribute` / `Subscript` / `Starred` / `NamedExpr` has a callee that is (a) a name or dotted
name rooted at a standard-library import (not rebound in the module) whose target's first
component is not in $S_{406}$ or that is in $X_{406}$; (b) an attribute of a `Call` of kind (a),
or of a name assigned from one, whose attribute is not in $K_{406}$ (container / `str` / `re`
/ logging methods); (c) a dunder attribute of an unbound builtin class, other than the
read-only dunders (`__instancecheck__`, `__eq__`, `__repr__`, ...). Under
$\mathit{dyn}_{406}$: §T.6.64's map gives every class `*` (a `getattr` default is refused,
`PYCSL-R376-GETATTR-CLASS-BINDING`); §T.6.60's attribute load over a file-class receiver and
`C.k` add `#UNK` (refused when hashed, `PYCSL-R349-UNHASHABLE-RECORD`); §T.6.60's dynamic flag
($\mathit{dy}_{383}$) is set.

### §T.6.75  Hashed-value sources: container expressions, store-only bindings, stdlib objects, copies (routes #407-#410, gen #37)

_Corresponds to `annotations.md` §7.64._

Refusal only, in §T.6.60's derivation (no emission change). (#407) In a module / class-body
initializer: `BoolOp` is the union of its operands; `IfExp` of its two branches; `UnaryOp(Not)`
is `bool`; a `BinOp` / `UnaryOp` with an operand of class `#list` / `#set` / `#dict` / `#tuple`
/ `#UNK` is that container with `#UNK` elements (`#UNK` for a `#UNK` operand); a
`Subscript` / `Attribute` / `Starred` / `UnaryOp` / method `Call` whose receiver is such a
container is, for a `Slice` of `#list` / `#tuple`, that container with `#UNK` elements, for an
index of `#list` / `#tuple` / `#dict`, the element (value) classes, else `#UNK`; a `Name` bound in
the same class body reads that binding. (#408) A module name's bindings are the store-context
`Name`s of module-level targets (a `Name` under a `Subscript` / `Attribute` target is a load).
(#409) The stdlib object classification runs before the derivation and also serves module
initializers; an object whose type has `__hash__ = None`, is an instance of `list` / `dict` /
`set` / `bytearray` / `MutableMapping` / `MutableSequence` / `MutableSet`, or whose `hash`
raises, or that is reached through an attribute of an object that is neither a module nor a
class, is `#UNK`; a method `Call` on a dotted stdlib name whose object is neither a module nor a
class is `#UNK`. (#410) $\mathit{CP}$ is the set of file classes $A$ with some file class $D$,
$A \in \mathit{clo}(D)$, whose closure binds `__copy__` / `__deepcopy__` / `__replace__` /
`__reduce__` / `__reduce_ex__` (all file classes when such a name is stored through a non-`self`
receiver or $\mathit{dy}_{383}$ holds); `copy.copy` / `copy.deepcopy` / `copy.replace` /
`dataclasses.replace` map a class of $\mathit{CP}$ to `#UNK`.
### §T.6.81  True division: zero divisor obligation (route #412, gen #37)

_Corresponds to `annotations.md` §7.70._

In a body whose `no_exception` set (or `\all`) covers ZeroDivisionError, i.e. when the
`("binop", "/")` trigger row applies: float $x / y$ lowers to
`(float_div_op` $\mathcal{T}(x)$ `(begin assert { ` $\mathcal{T}(y)$ ` <> 0.0 }; ` $\mathcal{T}(y)$ ` end))`
and int $a / b$ to `(float_truediv_op` $\mathcal{T}(a)$ `(begin assert { no_div_zero (` $\mathcal{T}(b)$ `) }; ` $\ldots$ $\mathcal{T}(b)$ ` end))`.
Spec context and functions without `no_exception` are unchanged.

### §T.6.82  Int true division: overflow obligation (route #413, gen #37)

_Corresponds to `annotations.md` §7.71._

Under `no_exception_all`, in a body, the right-operand block of int $a / b$ (§T.6.81) also holds
`assert { (- M * b <= a <= M * b) \/ (M * b <= a <= - M * b) }` with $M = (2^{53}-1) \cdot 2^{971}$
(DBL_MAX) written as a decimal literal: $|a| \le M |b|$, so $|a / b| \le M$ and the correctly
rounded quotient is finite.

### §T.6.83  Py_ssize_t limits (route #414, gen #37)

_Corresponds to `annotations.md` §7.72._

Under `no_exception_all`, in a body, with $S = 2^{63} - 1$, each obligation wrapping the size
operand in a `begin assert { .. }; .. end` block: `len(range(`$e_1$`))` owes $\mathcal{T}(e_1) \le S$,
`len(range(`$e_1, e_2$`))` owes $\mathcal{T}(e_2) - \mathcal{T}(e_1) \le S$, `len(range(`$e_1, e_2, e_3$`))` owes
$-S \le \mathcal{T}(e_2) - \mathcal{T}(e_1) \le S$; str $s * n$ (`str_repeat_op`) owes $-(S+1) \le n \le S \wedge (n \le 0 \vee
\texttt{String.length}\ s \cdot n \le S)$; `[x] * n` (`Array.make`) owes $n \le S$; $x \ll n$ owes
$x = 0 \vee n \le S$. MemoryError is not modelled.

### §T.6.84  `%` formatting allow-list (route #415, gen #37)

_Corresponds to `annotations.md` §7.73._

Refusal only, at the `str_mod_op` site of `_handle_binop` (no emission change for an admitted
site). Under `no_exception_all`, or a named set holding `KeyError` when the format is not a
literal or contains `%(`, the translation of $f \mathbin{\%} r$ is undefined
(`PYCSL-R415-UNCHECKED-PERCENT-FORMAT`) unless $f$ is a `String` literal whose `%`-directives are `%%` or a conversion in
$\{$`s`, `d`, `i`, `r`$\}$ preceded only by flags and a literal width / precision, the non-`%%` directives $d_1..d_k$ match the operands $o_1..o_k$ of a
`Tuple` $r$ (or $k = 1$ and $r$ is not a `Tuple`), and each $o_i$ is int-read (an `int` / `bool`
`Number`, a `Var` typed `int` / `bool`, a `Call` of `len` / `int` / `abs` / `ord` / `hash` /
`sum`) or, when $d_i \ne$ `%d`, str- or float-read.

### §T.6.85  UB-7.1 over dict views (route #416, gen #37)

_Corresponds to `annotations.md` §7.74._

Refusal only, inline in `_run_pipeline` after `IRScanner.find_iteration_mutations` (mirror twin
`\trusted`; no emission change): a `For` (at any depth of `body` / `orelse` / `finalbody` / `match`
arms, not opted out by `allow_iteration_mutation`) whose `iter` is
`Call(func = "`$r$`.keys" | "`$r$`.values" | "`$r$`.items")` has iterated collection $r$, exactly
as a `For` over `Var(`$r$`)`: it is refused when `_collect_mutations` finds a mutation of $r$ in its body.
### §T.6.91  Sequence repetition (route #417, run #3)

_Corresponds to `annotations.md` §7.80._

Refusal only, at the head of `_handle_binop`: for $e_1 * e_2$, the translation is undefined
(`PYCSL-R417-SEQUENCE-REPEAT`) when $e_1$ is an `ArrayLit` / `ListLit` with $k \ne 1$ elements, or
$e_1$ or $e_2$ is a `Tuple`. The admitted `[`$x$`] * `$n$ keeps its translation `Array.make` $n$
$\mathcal{T}(x)$ (with §T.6.83's bound under `no_exception_all`). An `ArrayLit` with a `Starred`
element (not erased, §T.6 route #375) translates to `(any (array int))`, a fresh unconstrained array
(it no longer translates as a one-element `Array.make 1` of the operand); `any` is not a logic term,
so in a specification context (unreachable: the contract grammar has no `*x`) it fails Why3 typing.

### §T.6.92  Contract string literals (route #417, run #3)

_Corresponds to `annotations.md` §7.81._

`_ContractParser._parse_atom_primary`: a `STRING` token $t$ becomes `StringLiteral(literal_eval(`$t$`))`
(Python's decoding of the double-quoted literal), so $\mathcal{T}$ of a contract literal equals
$\mathcal{T}$ of the same literal in a body (`whyml_string_literal` of the decoded value).

### §T.6.93  Range materialization and int-to-float bounds (route #417, run #3)

_Corresponds to `annotations.md` §7.82._

In `_handle_call_expr`, under `no_exception_all` in a body, after the arguments are translated: for
`list(range(`$\bar e$`))` / `sorted(range(`$\bar e$`))` (one positional argument, no keywords), the
argument is wrapped `begin assert { `$B(\bar e)$` }; `$\mathcal{T}(\texttt{range}(\bar e))$` end` with
§T.6.83's operand bound $B$; for `float(`$e$`)` with $e$ int-read, $\mathcal{T}(e)$ is replaced by
`let _fl417 = `$\mathcal{T}(e)$` in begin assert { -DBL_MAX <= _fl417 <= DBL_MAX }; _fl417 end`, with
DBL_MAX $= (2^{53}-1) \cdot 2^{971}$ as a literal; with $e$ str-, float- or bool-read nothing is added;
otherwise the translation is undefined (`PYCSL-R417-UNCHECKED-FLOAT-CONVERSION`). In
`_classify_iterable`'s opaque fallback, when the int coercion of the iterable drops a term that carries
`[@expl:no_exception: OverflowError reachable]` assertions, those assertions are materialized in a `let`
before the loop. Each obligation carries the attribute `[@r417_`$h$`]`, $h$ a stable hash of the call
node's IR, appended to the driver-owned list `transpiler.r417_obls` (created by `_run_pipeline` before
`transpile()`). After `transpile()`, `_run_pipeline` counts, for each recorded tag $t$, the calls of the
IR (`list` / `sorted` / `float` `Call` dicts, through `expr_from_dict(..).to_dict()`) whose tag is $t$,
$n_{src}(t)$, and refuses (`PYCSL-R417-ERASED-OBLIGATION`) when `[@`$t$`]` occurs in the module fewer than
$\max(1, n_{src}(t))$ times.

### §T.6.94  Hashing sources: constant-name dynamic stores, stdlib function results (route #417, run #3)

_Corresponds to `annotations.md` §7.83._

Refusal only, inline in `_run_pipeline` (mirror twin `\trusted`; no emission change). In the
hashed-value class derivation: a field read `o.`$a$ (receiver of a file class) and a class
attribute `C.`$a$ add `#UNK` when $a \in$ `_sa417`, the attribute names of constant-name
`setattr` / `__setattr__` / `__dict__[..]` / `vars(..)[..]` stores anywhere in the file; a `Call`
whose callee resolves (`_nd409`) to a standard-library object that is callable, not a `type` and not
`builtins.*` (and not a copy function, §T.6.75) has class `_hr417[`$q$`]` when listed, else `#UNK`.


### §T.6.121  Module-global / class-body value classes: polarity (route #421, run #3)

_Corresponds to `annotations.md` §7.110._

Refusal only, inline in `_run_pipeline` (mirror twin `\trusted`; no emission change). For a module
name $g$ (or a class-body name of $C$) with bindings $b_1..b_n$ (`_md408` / the class body), the
class set is $\bigcup_i \mathcal{C}(b_i)$ where $\mathcal{C}(b) = \{\texttt{\#UNK}\}$ for a binding
that is not a single-target assignment / `def` / `class` (and for every binding when $g$ is declared
`global` or also imported), and otherwise the initializer's derivation `_dz394`, in which every
expression node no row recognises answers `#UNK` (formerly `#UND`); the operator child of a
`BinOp` / `UnaryOp` / `BoolOp` / `Compare` is no longer read as an operand; a `Call` whose callee
resolves to a standard-library function answers `_hr417` (hoisted, shared with `_ty383`) or `#UNK`;
a call of an annotated module `def` answers its `-> T`. `#UNK` in a hashing position is refused
(`PYCSL-R349-UNHASHABLE-RECORD`).

### §T.6.122  Local rows: unbound str methods, Enum values, nested defs (route #422, run #3)

_Corresponds to `annotations.md` §7.111._

In `_ty383`: a call `str.m(x, ..)` / `bytes.m(x, ..)` (callee receiver resolving to `builtins.str` /
`bytes`) takes the receiver class `str` / `bytes`; the str / bytes method rows return the receiver
class for a fixed list, `str` for `__repr__` / `__format__` / `bytes.hex`, no class for a name the type does not have, and `#UNK` otherwise;
`e.value` with $e$ of a file Enum class $E$ answers $\bigcup$ `_ev422[E]` (member initializer
classes recorded by §T.6.121's derivation) under the MRO condition of §7.111, else `#UNK`; `g(..)`
with $g \in$ `_nd422` (nested undecorated `def g(..) -> T`, sole binding) answers $T$; a module
function name shadowed locally no longer reads `_mf383`.

### §T.6.123  Class-creating references (route #423, run #3)

_Corresponds to `annotations.md` §7.112._

Refusal only (`_run_pipeline`, after §T.6.73's rule). `_rs423` marks every `Name` / `Attribute` load
whose dotted name (through `_im405`, or `builtins.type`) resolves to a `type` subclass, or names a
file class with such a base (`_mc423`, two passes). A marked node outside annotations is admitted
only in the positions of §7.112; otherwise `PYCSL-R405-DYNAMIC-SUBCLASS`. A load resolving to a stdlib class whose metaclass overrides `__call__` (`_ec423`) is refused as the callee of a call with two or more arguments or a keyword.

### §T.6.124  `__class_getitem__` (route #424, run #3)

_Corresponds to `annotations.md` §7.113._

Refusal `PYCSL-R424-CLASS-GETITEM` for a `Subscript` (outside annotations) or an alias assignment
whose value is a `Name` of `_cg424` (file classes whose file MRO binds `__class_getitem__`). In
`_ty383`, a `Subscript` whose receiver class is `#H` answers `#UNK`.

### §T.6.125  Explicit `__init__` (route #425, run #3)

_Corresponds to `annotations.md` §7.114._

Refusal `PYCSL-R425-EXPLICIT-INIT` (outside the `__main__` driver) for an `Attribute` load
`.__init__` that is not the callee of a call in a `def __init__` whose receiver is a `super(..)` call,
or a class reference with the method's first parameter as first argument; and for `getattr` /
`methodcaller` / `attrgetter` with a constant `"__init__"` argument.

### §T.6.126  Format-spec bounds (route #426, run #3)

_Corresponds to `annotations.md` §7.115._

In the literal-spec arm of the `FormattedValue` lowering, for conversion none and an operand shown to
be an int (`_int284`), with presentation type $t$: $t \in \{e,E,f,F,g,G,\%\}$ under `\all` wraps the
operand in `assert { [@expl:no_exception: OverflowError reachable] [@r417_h] -DBL_MAX <= x <= DBL_MAX }`;
$t = c$ under `\all` asserts `0 <= x < 1114112` (same label), else the `("call", "chr")` row. The tag
$h$ = `stable_hash(repr(node))` is registered in `r417_obls`; the driver now also counts
`FormattedValue` nodes in §T.6.93's erased-obligation census.

### §T.6.127  Generator expressions in UB-7.1 (route #427, run #3)

_Corresponds to `annotations.md` §7.116._

In `_run_pipeline`'s UB-7.1 pass, the iterated receivers of a `For` are collected by a worklist over
its `iter`: a `GenExp` contributes each generator's `iter` (marked lazy), a `Call` `r.keys` /
`r.values` / `r.items` contributes $r$, a lazy `Var` contributes its name; each receiver is checked
with `IRScanner._collect_mutations`.

### §T.6.128  Safe-module callees resolve to functions (route #428, run #3)

_Corresponds to `annotations.md` §7.117._

In §T.6.73's `_dy406` census, a standard-library callee $q$ of a `_sm406` module is safe only when
importing its longest module prefix and walking the remaining attributes reaches a callable without
crossing a class, and the callable is not a class unless $q \in$ `_ck428`.

### §T.6.141  Jumps inside `finally:` (route #431, run #3)

_Corresponds to `annotations.md` §7.130._

$\mathcal{T}$ of `Try(b, h, o, F)` lowers a `Return` / `Break` / `Continue` of $F$ on the path where
$b$ terminated normally only; on the exceptional path of $b$ the jump would discard the exception,
which no lowering represents. So before Module 6 (`_run_pipeline`, next to route #156, on the final
IR) the translation is undefined, and the run refused, for a non-trusted function whose body holds a
`Try` / `TryStar` with a `finalbody` containing a `Return`, or a `Break` / `Continue` not under a
`For` / `While` of that `finalbody`.

### §T.6.142  Underivable hashed values under a TypeError claim (route R-gate, run #3)

_Corresponds to `annotations.md` §7.131._

In `_run_pipeline`'s #349-#383 hashing pass, for each hashed leaf $e$ of a site $n$ of function
$f$ (the `_wq365` walk: tuple components, `IfExp` arms, a `NamedExpr`'s value; a hashed iterable's
element classes `_hc349` for `_xe394` sites), let $C(e) = $ `_ex346`$(e) \cup$ `_eh372`$(e)$ $\cup$
`_dt365`$(e)$ (for a name) $\cup \{\#UB\}$ (for a display). When $\#UND \in C(e)$ or $C(e) = \emptyset$
(a `Slice` under a subscript whose base derives only as a sequence / tuple / `str` excepted) and
$n \notin$ `_gr383g`, $f$ joins `_und430`; if $f$ is not trusted / abstract and claims TypeError
(IR `no_exception_all`, or `no_exception` $\cap$ {TypeError, Exception, BaseException}, or the same
in the `#@` block above the `def`), the translation is undefined and the run refused. The
derivation $\mathcal{T}_{ty}$ of `list(x)` / `set(x)` (one positional argument, no keyword) is
`#list[Union[el(x)]]` / `#set[Union[el(x)]]`.

### §T.6.143  Callee TypeError by hashing (route #430, run #3)

_Corresponds to `annotations.md` §7.132._

`_run_pipeline` sets `transpiler.und_hash_r430 = _und430` (kept off the IR, like
`class_bases_r304`). In `_reset_function_state`'s route #178 summary, under `no_exception_all`
the active set gains `TypeError`, a function $g \in$ `und_hash_r430` without `no_exception_all`
gains `TypeError` in its raw summary, and the summary is closed over same-file calls as before; a
call in the claimed body to a $g$ whose closed summary meets only `TypeError` is refused with
`PYCSL-R430-CALLEE-UNDERIVABLE-HASH` (KeyError / IndexError / ValueError keep route #178's
message).
### §T.6.101  String literals: one model character per code point, solver-faithful encoding (route #411, run #3)

_Corresponds to `annotations.md` §7.90._

(1) `whyml_string_literal`: a code point $0x80 \le c \le 0xFF$ is written `\x`$hh(c)$ (one `string`
character), no longer its UTF-8 bytes. (2) Final pass, inline at the end of `_run_pipeline` (mirror
twin `\trusted`): every WhyML string literal of the emitted text (outside `(* .. *)` and `[@..]` /
`[#..]`) is decoded by Why3's lexer rules (`lexlib.mll`) to bytes $b_1 \dots b_k$. Let
$P = \{32..126\} \setminus \{34, 92\}$. If every $b_i \in P$ the literal is unchanged. Otherwise it
becomes $\mathit{fold}_\texttt{pystr\_cat}$ over maximal $P$-runs (as plain literals) and
`(pystr_chr` $b_i$`)` for each $b_i \notin P$. When any literal was rewritten, the module
```
module PyCSL_StrLit
  use int.Int  use string.String
  function pystr_code (s: string) : int
  val function pystr_chr (n: int) : string
    ensures { 0 <= n < 256 -> String.length result = 1 /\ pystr_code result = n }
    ensures { (0 <= n < 32 \/ n = 34 \/ n = 92 \/ 126 < n < 256) -> result <> " " /\ ... /\ result <> "~" }
  val function pystr_cat (a b: string) : string  ensures { result = String.concat a b }
end
```
(the second clause lists the 93 one-character literals of $P$) precedes the first module, and every
`module` whose text names `pystr_chr` / `pystr_cat` gets `use PyCSL_StrLit`. Each clause holds of the
one-character string of code point $n$ (with `pystr_code` its code), so the specification is
satisfiable and asserts nothing false of the denoted Python value; the guard $0 \le n < 256$ keeps
injectivity finite. `string.Char` is deliberately not used: it relates no `Char` to the solver's
characters, and its axioms perturbed unrelated goals (measured).

### §T.6.144  Attribute receivers that may be `None` or of several classes (route #432, run #3)

_Corresponds to `annotations.md` §7.133._

In `_run_pipeline`, after the #349-#383 hashing pass of function $f$ (not trusted / abstract,
claiming AttributeError: IR `no_exception_all`, or `no_exception` $\cap$ {AttributeError, Exception,
BaseException}, or the same in the `#@` block above the `def`), for each `Attribute` load
$R.a$ outside annotations let $C(R) = $ `_ex346`$(R) \cup$ `_eh372`$(R)$ ($\cup \{None\}$ for a
parameter defaulted to `None`). The type-atom derivation $\mathcal{T}_{ty}$ expands
`Optional[T]` to the atoms of $T$ and `None` (route #432; before, `None` only for `Union[T, None]`
/ `T | None`). Let $K(S)$ be $S$ minus the `#`-marks, `Any` and `object`. The site is admitted
when $|K(S)| \le 1 \wedge None \notin K(S)$, or every $c \in K(S)$ is a builtin class with
`hasattr(c, a)`, for $S = C(R)$, or else for $S = N(R)$, the narrowed set: the climb from $R.a$
to the function entry collects guards $(T, p)$ until a kill (a node whose own tokens --
stores / `del` of a name, attribute stores, calls -- meet $\{N(root)\}$, plus $\{C\} \cup
\{A(f) \mid f \in path\}$ for an attribute path or a `global` / `nonlocal` root; a crossed loop, a
`while` whose test holds the access, or a comprehension kills when ANY of its nodes does; a nested def /
lambda / generator expression stops the climb); leaves of $T$ under
$p$ give not-None / `isinstance` classes; $N(R) = (B \cap_{isinstance} \ldots) \setminus \{None\}$
with $B$ the base set ($C(R)$, or the classes of `v` for a stopping `R = v`, or
$(C(R) \setminus \{None\}) \cup cls(v)$ for `if R is None: ...; R = v`). Otherwise the
translation is undefined and the run refused (`PYCSL-R432-OPTIONAL-RECEIVER-ATTRIBUTE`). No
emission changes.

### §T.6.145  `join` element classes (route #433, run #3)

_Corresponds to `annotations.md` §7.134._

In the same position, for $f$ claiming TypeError, a `Call` `S.join(it)` (one positional
argument, no keyword) with $K(C(S)) = \{str\}$ (resp. $\subseteq \{bytes, bytearray\}$) is
admitted iff the arms of `_ei383`$(it)$ (through `Optional` (+ `None`) / `Union` / `|` /
`Annotated` / `Final`, aliases and string annotations) are non-empty and all `str` (resp.
`bytes` / `bytearray`); otherwise refused (`PYCSL-R433-JOIN-ELEMENT-CLASS`).

### §T.6.146  Orderability of compared values (route #437, run #3)

_Corresponds to `annotations.md` §7.135._

For $f$ claiming TypeError, the compared type list $G$ of `sorted(it)` / `min(it)` / `max(it)`
(`_ei383`$(it)$; for a mapping's `.items()`, each `#tuple`'s first component), `min` / `max`
with $\ge 2$ positional arguments (their `_ty383`), `L.sort()` with every `_ty383`$(L)$ a
`List` / `list` / `#list` subscript (`_ei383`$(L)$), replaced by `int` / `float` / `str` for a
builtin `key=` and by `_ty383`(body) for a lambda `key=`, is admitted iff the worklist
$\{G\}$ empties: a group's arms all in {int, bool, float}, or all `str`, or all in {bytes,
bytearray}, or all parameterised tuples (push the group of position-$i$ components for each
$i$, a `Tuple[T, ...]` contributing $T$ to every position), or all parameterised lists (push
their elements); any other arm, an empty group or a mix refuses the site
(`PYCSL-R437-UNORDERED-ELEMENTS`).

### §T.6.147  `ord` length obligation (route #434, run #3)

_Corresponds to `annotations.md` §7.136._

In `_handle_call_expr`'s `ord` arm, in a body under `no_exception_all` (and when the driver list
`r434_ok` exists), for the call node $c$ with argument $a$ and tag $h$ = `r434_` + `stable_hash(repr(c))`:
$a$ a one-character `String` literal, or a `Subscript` (index, not slice) of a str expression,
appends $h$ to `r434_ok` and lowers unchanged; another str expression $a$ lowers as
`(let _o434 = ⟦a⟧ in begin assert { [@expl:no_exception: TypeError reachable] [@h] String.length
_o434 = 1 }; _o434 end)` in the argument position of `ord_op` / `pycsl_vord_op`; anything else is
undefined (refused, `PYCSL-R434-ORD-LENGTH`).

FAIL-CLOSED CENSUS. After `transpile()`, `_run_pipeline` walks the `body` of every IR function that
is neither `trusted` nor `abstract` and has `contracts.no_exception_all`, and counts $n_h$, the
sites with tag $h$: `ord(a)` with $a$ not a one-character `String` literal; `T.m(..)`
(§T.6.148); a method call whose §T.6.149 parameter is present and not an int literal. If
$\#\{[@h]\text{ in the module}\} + \#\{h \in \texttt{r434\_ok}\} < n_h$ for some $h$, the translation is
undefined (`PYCSL-R434-UNCHECKED-SITE`). CALLEE SUMMARY: in `_reset_function_state`'s route #178
summary, under `no_exception_all` the active set gains `TypeError` when some function holds such a
site (`_cs434`, the same predicate over every IR function), each such function without
`no_exception_all` gains `TypeError` in its raw summary, and a call to a $g$ whose closed summary
meets only `TypeError` is refused with `PYCSL-R434-CALLEE-UNCHECKED-SITE` (§T.6.143's message when
$g \in$ `und_hash_r430`).

PATH VALUES. Module 5 erases a `Path` annotation to `str`, so the source decides: after the census,
`_run_pipeline` parses the source and, for each `def` whose name is the (method-stripped) name of an IR
function with `no_exception_all`, computes the Path names $P$ (parameters / `AnnAssign` targets annotated
`*Path*`, closed under `Assign` / `AnnAssign` / walrus bindings from a Path value) and refuses
(`PYCSL-R434-ORD-PATH`) a call `ord(a)` where $a$ is a Path value: a name in $P$, `x.parent`, a `/` with a
Path operand, a call of `Path` / `PurePath` / ... or of `resolve` / `with_suffix` / ..., a subscript,
conditional or walrus of one.

### §T.6.148  Unbound builtin descriptors (route #435, run #3)

_Corresponds to `annotations.md` §7.137._

At the head of `_handle_call_expr`, under the same conditions as §T.6.147, a `Call` with no
`receiver` and `func` = `T.m` (one dot), $T \in$ {str, bytes, bytearray, int, float, complex, bool,
list, dict, set, frozenset, tuple, type, object}, $m \notin$ {maketrans, fromhex, from_bytes,
fromkeys, from_number}: let $K$(args[0]) be `str` for a `String` / `FString`, the Python class of a
`Number` value, `bool` for `Bool`, the symbol-table type head of a `Var` (`List`/`Dict`/`Set`/
`Tuple`/`FrozenSet` normalised; `float` / `complex` mapped to none), the result class of a
receiver-less call of a builtin of a fixed table (`str repr chr format ascii hex oct bin` -> str,
`len ord hash int` -> int, ...), and none otherwise. If $T$ = object or $K$ = $T$, $h$ is appended to
`r434_ok` and the lowering continues; otherwise the translation is undefined
(`PYCSL-R435-UNBOUND-DESCRIPTOR`).

### §T.6.149  C `ssize_t` / `int` method parameters (route #436, run #3)

_Corresponds to `annotations.md` §7.138._

At the head of `_handle_call_expr`, under the same conditions, a method call (a `receiver`, or a
dotted `func`) whose tail $m$ has a row $(i, k, b)$ -- split / rsplit $(1,$ maxsplit$, 63)$,
replace $(2,$ count$, 63)$, insert / center / ljust / rjust / zfill $(0, -, 63)$, to_bytes $(0,$
length$, 63)$, expandtabs $(0,$ tabsize$, 31)$, hex $(1,$ bytes_per_sep$, 31)$ -- takes $a$ =
args[$i$], else the keyword $k$. An int literal $v$ (or `-` of one) with $v \notin [-2^b, 2^b)$ is
undefined (`PYCSL-R436-SSIZE-ARGUMENT`); in range it owes nothing. A `String` / `FString` / `Bool`,
a str / float / bool name or a str / float expression appends $h$ to `r434_ok`. A pure int form $a$
(`Var`, int `Number`, `BinOp` `+ - *` and `UnaryOp` `- +` of pure forms, `len(Var)`) lowers the call
as `(begin assert { [@expl:no_exception: OverflowError reachable] [@h] - 2^b <= ⟦a⟧ < 2^b }; ⟦c⟧
end)`, where ⟦c⟧ is the rest of `_handle_call_expr` on the same node (guarded against re-entry by
the entry `("#g436", id(node))` in `r434_ok`); any other $a$ is undefined
(`PYCSL-R436-SSIZE-ARGUMENT`).

### §T.6.150  Un-parameterised tuples are underivable when hashed (route #438, run #3)

_Corresponds to `annotations.md` §7.139._

In §T.6.142's leaf test, the condition $\#UND \in C(e) \lor C(e) = \emptyset$ becomes
$\#UND \in C(e) \lor \#UNKT \in C(e) \lor C(e) = \emptyset$, and a hashed iterable ($n$'s
`_xe394` site) counts when its element classes `_hc349` hold `#UND` or `#UNKT`. `#UNKT` is the
marker $\mathcal{T}_{ty}$ adds for a `tuple` / `Tuple` name that is not a file class, at any depth
of an annotation (a component included). Both consequences of §T.6.142 follow: $f$ joins
`_und430` (§T.6.143), and a claimed, non-trusted $f$ is refused. The deny-list handling of
`#UNKT` (§7.47) is unchanged.

### §T.6.151  Structural types, user-module callees, computed-name stores (route #439, run #3)

_Corresponds to `annotations.md` §7.140._

(1) The value verdict `_kv381` of an outside class object $o$ that is neither unhashable nor
admits a builtin container is `?` (unknown) when $o$`._is_protocol` is `True` or
`__subclasshook__` $\in$ `vars(o)`; `_pr439` is the set of file classes with a base `Protocol` /
`Protocol[..]` resolving (by `_im369`) to `typing.Protocol`, and a class name of `_pr439` in a
hashed leaf's class set adds `#UNK`. (2) Before `transpiler.und_hash_r430` is set,
`_run_pipeline` closes the file's imports over `_resolve_module_path` (skipping a
`sys.stdlib_module_names` top-level module and anything under `src/pycsl/Lib/`), parses each
user module, and adds to `_und430` the IR name ($g$, or `cls.lower()__g` for a method) of every
function without `#@ no_exception \all` in the `#@` block above its `def` whose body may hash
(the syntactic set of §7.140 (2)), closed over same-module calls. (3) `_sd439` is set by a
`setattr` / `__setattr__` whose name argument is not a string constant, or a subscript store /
`.update(..)` on `x.__dict__` / `vars(x)` with a computed key; then $\mathcal{T}_{ty}$ of an
instance-field read of a file class, and of `C.k` of a file class, includes `#UND`.

### §T.6.152  The builtin signature table (routes #440 / #441, run #3)

_Corresponds to `annotations.md` §7.141._

In `_run_pipeline`, after §T.6.144-§T.6.146 for function $f$ (not trusted / abstract) with claim
set $X \neq \emptyset$ (`_cx432`), for each `Call` $c$ in post-order (`_po383`), outside
annotations and `assert` messages: let the callee be a builtin name $g \in$ dom(`_FT440`) not
bound by the module or $f$ (row $\rho = $ `_FT440`$[g]$), or an attribute $R.m$. For $R.m$:
(a) $R$ rooted at an import: if $m \in F$ (the module's function names $\cup$ every file class's
methods) and neither `unparse(R.m)` nor its `__` spelling names an IR function, the site is
refused ($\top$), else skipped; (b) $R$ = `super()`: skipped; (c) $R$ an unshadowed builtin
type $T$: $K = \{T\}$ and the first argument must have class set exactly $\{T\}$; (d) $R$ a file
class name: admitted iff $m$ is bound in a class body along its MRO, else refused (AE, or $\top$
with a non-file base); (e) otherwise $K$ = the class keys of `_ty383`$(R)$ (Optional / Union /
`|` / Annotated / Final / ClassVar / aliases / string annotations expanded; heads mapped by
`_CN440`: `List` / `#list` $\to$ list, `Dict` / `TypedDict` $\to$ dict, `#iter` / `Iterable`
$\to$ iter, ..., a file class $C \to$ C:$C$, anything else ?), replaced by the `isinstance`
classes when §T.6.144's narrowing decided $R$ (`_nr440`), minus None. For each $k \in K$:
? / callable: skipped if $m \in$ dom$_m$(`_MT440`), refused ($\top$) if $m \in F$; C:$C$:
admitted iff $m \in$ `_me383`$[C]$ or bound / a field along $C$'s file MRO, else
$\rho = $ `_MT440`$[(b, m)]$ for its first non-file base $b$ with a row, else refused (AE, or $\top$
with a non-file base); a builtin $k$: $\rho = $ `_MT440`$[(k, m)]$, else refused ($\top$ if
`hasattr`$(k, m)$, else AE). With $\rho = (lo, hi, kw, codes, \_)$: a `*` argument is admitted
only when $hi = \infty$ and every code is `*`; else refused (TE) unless $lo \le n \le hi$ for the
$n$ positional arguments, every keyword is in $kw$ (or $kw$ has `*`), and each argument's class
keys (`_ty383`, or `_rs440` -- the result class recorded for an admitted call whose row decides
it -- when `_ty383` is `#UND` / `#UNK`), its element keys (`_ei383`) and tuple component keys
satisfy its code (`int(x, base)`: $x$ bytes-like or `str`). A refusal is raised iff $X$ covers it:
AE $\Leftarrow X \cap \{\backslash all, AttributeError, Exception, BaseException\}$, TE likewise
with TypeError, $\top$ always (`PYCSL-R440-METHOD-NOT-ADMITTED`, `PYCSL-R441-BUILTIN-SIGNATURE`).
$\mathcal{T}_{ty}$ changes in two rows: `BinOp(Mult)` of a sequence-typed operand (a `#list` /
`List` / `list` / `#tuple` / `Tuple` / `tuple` subscript, `str`, `bytes`) by an `int` / `bool`
operand is the sequence's type list; the receiver type list of a method-call row has its
`Optional` / `Union` / `|` members expanded and `None` dropped. No emission changes.

### §T.6.160  Resolved isinstance narrowing; underivable attribute receivers (routes #442 / #443, run #3)

_Corresponds to `annotations.md` §7.150._

(#442) In §T.6.144's leaves, `isinstance(R, E)` contributes classes only when `isinstance`
$\notin$ `_bound341` $\cup$ `_imp341` $\cup$ `_cls341` $\cup$ `_lb383` $\cup$ `_ln394`, no star import, and
each element $e$ of $E$ ($E$ a name or a literal tuple) is resolved: $e$ a `Name` outside
`_bound341` $\cup$ `_imp341` $\cup$ `_cls341` $\cup$ `_lb383` $\cup$ `_ln394` with `builtins.`$e$ a class $c$,
`type(c) is type` and not `issubclass(type(None), c)`. Otherwise the leaf contributes nothing. (#443) Let $S$ be the narrowed set $N(R)$ (or $C(R)$).
The site is refused (`PYCSL-R443-UNDERIVABLE-RECEIVER-ATTRIBUTE`) when $S = \emptyset$, or $S \cap
\{$`#UND`, `#UNK`, `#UNKT`, `#UB`, `Any`, `object`$\} \ne \emptyset$, or some $c \in K(S)$ is not
known ($c \in$ `_NT432`, or a file class outside `_bound341` $\cup$ `_imp341`, or bound once by a
level-0 `from M import c` with $M$ in the ten-module list of §7.150 and `getattr(M, c)` a class
with metaclass `type`, not `object`) -- unless $R$ is a `Name` bound only by `Import` statements
(outside `_bound341` $\cup$ `_cls341` $\cup$ `_lb383` $\cup$ `_ln394`, no `ImportFrom` of it, no star import), or $R.a$ is the callee of a 2-positional-argument
`.get` call whose receiver, after stripping `or {}` / `or []`, is `N.get(..)` with
`dict_value_types[N] == "hval"` in the function's IR and no `FunctionDef` / `Lambda` between the
access and the function (Module 6 emits the `PyCSL-DVW-R5` map assertion there). In $\mathcal{T}_{ty}$, a method call $b.m(..)$ on a type atom `None` (a name
or the constant) with `not hasattr(None, m)` yields bottom (`#BOT`) instead of `#UND`. No
emission changes.

### §T.6.170  Term transform with a read-only `Dict[str, str]` parameter (lv2, run #3)

_Corresponds to `annotations.md` §7.160._

$\mathcal{T}$ of a function $f(t: U, m: \texttt{Dict[str, str]}) \to U$ ($U$ the term union,
`dict_key_types`/`dict_value_types` of $m$ = `string`, no default) accepted by
`_recognize_term_transform_strmap` is the group: `val function f__get (m: term__strdict) (k
d: string) : string`, `val function f__restrict (m: term__strdict) (ks: list string) :
term__strdict` (and `type term__strdict` in the term theory), then `let rec f (v_t: term)
(v_m: term__strdict) : term ensures { true } variant { v_t }` with one `match` arm per
constructor $C$: `return t` $\mapsto$ `v_t`; `return C(e_1..e_k)` $\mapsto$ `C b_1..b_k` with
$t.F \mapsto$ `v_F`, $f(t.G, m) \mapsto$ `(f v_G v_m)` ($G$ a `term` field),
`tuple(f(a, m) for a in t.L)` $\mapsto$ `(f__list v_L v_m)` ($L$ a `list term` field),
`m.get(t.F, t.F)` $\mapsto$ `(f__get v_m v_F v_F)` ($F$ a `string` field); a leading
`x = {k: v for k, v in m.items() if k not in t.B}` ($B$ a `list string` field) $\mapsto$
`let v__lm = f__restrict v_m v_B in ..` with $f(t.G, x) \mapsto$ `(f v_G v__lm)`; the
two-constructor `kind = A if isinstance(t, A) else B; return kind(..)` arm maps each of $A$,
$B$ alike. `f__list` is the element-wise map (`variant { l }`). Any other statement or
expression declines (the function stays on the generic path). Gated by
`_term_contract_trivial` like every term recognizer.

### §T.6.28  Identifier lowering is checked injective; identity tests in every position (routes #327 / #329 / #333)

_Corresponds to `annotations.md` §7.17._

$\mathcal{T}_{id}(x)$ (`whyml_ident`) maps `_` to `py_underscore`, `.` to `_`, non-ASCII
to its ASCII decomposition, lowercases the first character and prefixes a WhyML keyword
with `py_`. It is not injective ($\mathcal{T}_{id}(N) = \mathcal{T}_{id}(n)$,
$\mathcal{T}_{id}(\texttt{result}) = \mathcal{T}_{id}(\texttt{py\_result})$), and two
source names with one image denote ONE WhyML variable. So before Module 6 (`_run_pipeline`,
on the final IR) the translation is defined only when $\mathcal{T}_{id}$ is injective on
each scope $S$: for every function, $S$ = formal parameters $\cup$ every `Var` read $\cup$
every binding target (`target`, `targets`, quantifier `var`) of its body and contracts,
and no member of $S$ may map into the `_tu_*` binder space; at module level, $S$ = the IR
function names $\cup$ the module-level value bindings of the source (outside `def` /
`class` bodies and the `__main__` driver); for classes, the lowercased names. Otherwise
the program is refused (`PYCSL-R327-IDENT-COLLISION`). An injective encoding was measured
and rejected: it re-emits ~1962 of 3077 root, 48 of 510 pyref and 48 of 53 mirror files.

Route #333 adds two side conditions to the same check. Exception tags: $\mathcal{T}_{exc}(E)$
(`safe_exc_name`) strips leading underscores. Let $C_{exc}$ be the source classes that
derive (syntactically, transitively) from a builtin `BaseException` subclass or are named
by an IR `exc_type`, and $O$ = every source class $\cup$ every imported name $\cup$ the
builtin exception names. The translation is defined only if no $c \in C_{exc}$ and
$o \in O$, $o \neq c$, have $\mathcal{T}_{exc}(c) = \mathcal{T}_{exc}(o)$; an `exc_type`
that is only the stripped spelling of $c$ (no class of that name) denotes $c$ itself.
Generated binders: let $G$ be the census of the emitter's own binders in function scope
(`_rsv333`: the prefixes `_idx_`, `_len_idx_`, `_stop_idx_`, `_hv_idx_`, `_rl_idx_`,
`_callit_idx_`, `_split_idx_`, `_seqlit_idx_`, `_any_`, `_all_fold_`, `_inl_`, `_tu_`,
`_u_`, `_lf_`, `_cc_`, `_csrc_`, `_cdf_`, `_mem_`, `_dk_`, `_h_f_`, `_r230_`, `_r251_`,
`_class_`, `_union_`, `_pf_`, `_pycsl_`, `_wl<k>c_`, `__pycsl_`, `__and_`, `__or_`,
`__happy_`, `_for_target`, and the exact temporaries `_alit`, `_u`, `_hl`, `_rec_`, `_row`,
`_ci`, `_celt`, `_si`, `_csl_forall`, `_s_eq`, `_pyobj_state`, ...). For each scope $S$,
no USER-SPELLED member (a source `Name` / parameter or a `#@` token) may satisfy
$\mathcal{T}_{id}(x) \in G$; the front end's own generated names in the IR
(`_for_target`, `_inl_res__inl<k>`) are exempt. Renaming $G$ into a namespace no Python
identifier reaches was measured and rejected: it re-emits 586 / 12 / 37 (root / pyref /
mirror) files; the refusal moves none.

The `is` rules (§T.6.x routes #42 / #52) are evaluated in $\mathcal{T}_e$ on the node
carrying the `py_is` marker, whether it arrives as the root wire dict or as the
`OpaqueExpr` that `ir_schema.expr_from_dict` builds for a marked child of a typed node
(`not`, if-expression test, boolean operand, comprehension filter).

### §T.6.24  Collections constructors and the itertools length model (routes #321 / #323)

$\mathcal{T}_e(\texttt{Counter}()) = \mathcal{T}_e(\texttt{OrderedDict}()) =
\mathcal{T}_e(\texttt{defaultdict}(f)) = \texttt{(const (None: option int))}$, the empty map
whose read of a missing key is 0 — faithful for `Counter` and for $f \in \{$`int`,
`lambda: 0`$\}$ only, so every other factory (and none: `KeyError`) is refused. A seeded
construction is $\texttt{pycsl\_seeded\_map}_{h}$, $h$ the hash of the seed's IR (tagged
with `Counter` for a counter): an UNINTERPRETED constant, so the translation is sound only
if equal $h$ means equal maps — true for a LITERAL seed and false for a name (measured at
67edf13c: `Counter(xs)` before and after `xs = [2]` shared $h$; `Counter([(1,1)])` and
`OrderedDict([(1,1)])` shared $h$), hence non-literal seeds are refused. Keyword and starred
arguments have no image and are refused. The map read $\mathcal{T}_e(d[k])$ does not insert
$k$, which CPython's `defaultdict.__getitem__` does; the scan in `_reset_function_state`
(annotations.md §7.13) admits a `defaultdict` local only when its key set is unobservable or
every read is fused into a store of the same key, so the two agree on every observation.
$\mathcal{T}(\texttt{len}(\texttt{list}(\textit{it}(\vec a))))$ is
$\sum |a_i|$ / $\prod |a_i|$ / $\min(|a_0|, n)$ only for an $\textit{it}$ resolved through
the module's import table to `itertools.chain` / `product` / `islice`, with positional,
unstarred $\vec a$; a keyword or starred operand is refused and an unresolved callee falls to
the generic call path.

### §T.6.27  Import resolution is CPython's or refused (route #326)

$\mathcal{T}$ of an importing program is taken relative to a resolution
$\rho(m) \in \textit{Files} \cup \{\bot\}$ of each imported dotted name $m$; the
translation is sound only if $\rho(m)$ is the module CPython binds to $m$ at the import
statement. $\rho$ searches the roots $R = [\textit{dir}(\textit{main}),
\textit{cwd}, \texttt{src/}, \textit{import-path}\ldots]$ and, in each, returns
$r/m/\texttt{\_\_init\_\_.py}$ before $r/m\texttt{.py}$ (CPython's `FileFinder` order;
the module-first order bound the wrong body when both exist). For
$\textit{top}(m) \in \texttt{stdlib\_module\_names} \cup
\texttt{builtin\_module\_names}$, a hit is admitted only when it is byte-identical to the
interpreter's own `stdlib/` source (recursively for a package), and otherwise the program has
no image (`PYCSL-SEM-IMPORT-SHADOWS-STDLIB`): CPython's built-in/frozen finders and the
startup-populated `sys.modules` precede every path entry. $\rho$ is a function of the
source tree only, so a program that can change CPython's binding has no image
(`PYCSL-SEM-IMPORT-STATE-MANIPULATED`): a reference to `sys.{path, modules, meta_path,
path_hooks, path_importer_cache}` other than a pure read, the `sys` object escaping as a
value, dynamic-import machinery with some $\rho(m) \ne \bot$, or such an edit in the top
level of a resolved dependency. The one admitted edit,
`sys.path.insert(0, dirname(abspath(__file__)))`, prepends $R_0$ itself.

### §T.6.30  `assert` under `no_exception \all` (route #332)

Let $N_f$ be the declared no-exception set of $f$ ($\top$ for `\all`). The §T.5.8
erasure $\mathcal{T}_s\llbracket \texttt{assert } c[, m] \rrbracket = \texttt{()}$ is
kept when $\texttt{AssertionError} \notin N_f$ (it does not hold for any base of it:
`Exception`, `BaseException`); there a failing assert aborts and the contract, partial
with respect to AssertionError, says nothing about that run. When
$N_f = \top$ or $N_f \cap \{\texttt{AssertionError}, \texttt{Exception},
\texttt{BaseException}\} \ne \emptyset$:
$$\mathcal{T}_s\llbracket \texttt{assert } c[, m] \rrbracket
= \texttt{if } \mathcal{B}\llbracket \mathcal{T}_e\llbracket c \rrbracket \rrbracket
  \texttt{ then () else assert \{ [@expl:no\_exception: AssertionError reachable] false \}}$$
with $\mathcal{T}_e$ the PROGRAM translation (its own trigger VCs, §T.6) and $\mathcal{B}$
the `if`-test truthiness coercion. $m$ is evaluated by CPython only on the failing branch,
which the VC makes unreachable, so it is not translated. The effect screen
(`PYCSL-M6-ASSERT-EFFECTFUL-TEST`) still precedes. A `for`-target read inside such an assert
is a read for the loop-target write-back analyses (routes #36/#301/#302).

### §T.6.33  Inherited class invariants and the constructor chain (route #335)

For a record $S$ with C3 MRO $S = K_0, K_1, \ldots, K_m$, the constructor chain is the
longest prefix walk $K_{i_0}, K_{i_1}, \ldots$ where classes without an `__init__` are skipped
and each $K_{i_j}$ that defines one is followed by $K_{i_{j+1}}$ only when its body begins
with `super().__init__(...)`; an unmodelled class (no `type_decl`, not a fieldless class
without `__init__`) and a synthesized dataclass constructor end it. $\mathit{own}(K)$ is the
set of fields $K.$`__init__` stores outside control flow, and
$\mathit{owner}(f) = $ the first $K_{i_j}$ with $f \in \mathit{own}(K_{i_j})$. For every
field $f$ named by an invariant of $S$ (own or inherited) that belongs to a base and not to
$\mathit{own}(S)$, `apply_inheritance` requires $\mathit{owner}(f)$ to exist, the merged
`field_defaults`$[f]$ to equal $\mathit{owner}(f)$'s literal unless $f$ is bound in the merged
`init_body` or unknown, and no $K_i$ to define a method or a non-constant class-body binding
named $f$; otherwise it raises `PYCSL-R335-INHERITED-INVARIANT-CONSTRUCTION`. Nothing is
emitted differently: the goal `_check_class_inv_S` (§T.6, route #226) and the receiver
assumption of route #277 are unchanged for every class that passes.

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
| `str(x)`, `repr(x)`, `format(x)`, `print(…, x, …)`, `f"{x}"` / `f"{x!r}"` / `f"{x:d}"`, `"%d" % x` with `x` an int (route #281) | `("call", "int_str")` | `(- 10^4300) < T_e[[x]] /\ T_e[[x]] < 10^4300` (literal constants), asserted on the OPERAND: `(str_of_int (begin assert { … }; x end))`. For an f-string part with a literal spec: when the presentation type (last spec character, if a letter or `%`) is none/`d`/`n`, or a conversion is present (route #284: `:5`, `:05d`, `:,`, `:>10` included) |
| `f"{v:spec}"` with a literal spec invalid for the formatted type, a computed spec `f"{x:{w}}"`, a `%` format that CPython's `%` rejects or that is not a literal (route #284) | `("call", "format_spec")` | `assert { false };` on the operand, `(pycsl_format_… (begin assert { false }; v end))`. Validity is decided at emit time by CPython `format(sample, spec)` / `fmt % samples` (sample `0` for an operand shown to be an int, `""` for a str or after a conversion, BOTH otherwise; a width/precision of more than 6 digits is undecided) |

**Comprehensions (route #285).** A `ListComp` / `SetComp` / `DictComp` / `GenExp` is lowered
WITHOUT these per-element assertions; instead `_reset_function_state` refuses it under an active
context when its element / key / value / condition / iterable contains a shape that
`exception_model.TRIGGER_EXPR_SHAPES` maps to a row whose exception is active (and refuses every
comprehension when a `TRIGGERS` row lacks a census entry).

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
| Python's `//`/`%` are floored (rounds toward −∞; remainder sign = divisor) | Language semantics | Low — realized faithfully: `pycsl_div`/`pycsl_mod` correct Euclidean `div`/`mod` by a sign-of-divisor adjustment (WL-01 FIXED); positive-divisor case is byte-identical to Euclidean |
| **FLOAT-FINITE** — every `float` value is finite and non-NaN | $\tau(\texttt{float}) = \texttt{real}$ (no NaN/±inf) | **Medium** — DECLARED MODEL ASSUMPTION (§T.10.5): reported by `--soundness-report`, dropped by `--strict-float-finite`; counterexample corpus 2500-2502 |
| **BUILTIN-EXACT** — a builtin-typed value is an exact instance (no dunder-overriding subclass) | $\tau$ of every builtin | **Medium** — DECLARED MODEL ASSUMPTION (§T.10.5): reported by `--soundness-report`, no strict mode; counterexample corpus 2506 |
| **LATIN1-STR** — every `str` value consists of code points 0..255 (`ord(c) < 256`; `chr(n)` modelled only for `0 <= n < 256`) | $\tau(\texttt{str}) = \texttt{string}$ of Why3 `string.Char` (`axiom code`: every code < 256) | **Medium** — DECLARED MODEL ASSUMPTION (§T.10.5): reported by `--soundness-report`, dropped by `--strict-latin1`; counterexample corpus 3020-3023 |
| **BARE-CONTAINER-INT** — an element of a parameter annotated with a bare container (`list`, `List`, `Sequence`, `tuple`, ...), or a VALUE of a bare `dict` / `Dict` / `Mapping` (route #334), is an `int` | $\tau$(`list`) = `array int`, $\tau$(`List`) = `int` read by `subscript_get` | **Medium** — DECLARED MODEL ASSUMPTION (§T.10.5): reported by `--soundness-report`, dropped by `--strict-bare-containers`; counterexample corpus 4363-4364 |
| **HVAL-STR-KEYS** — every dict nested inside a `PyVal` value has `str` keys | $\tau$(`Dict[str, PyVal]`) = `map string (option hval)` with `HMap` over `hpairs` keyed by `string`; the nested-key walk `hval_keys_get` returns a `string` | **Medium** — DECLARED MODEL ASSUMPTION (§T.10.5): reported by `--soundness-report`, dropped by `--strict-hval-keys`; counterexample corpus 3550-3553 |
| **CLASS-EXACT** — a user-class-typed value is an exact instance (no override is seen) | a method call through an `A`-typed receiver lowers against `A.m`'s contract | **Medium** — DECLARED MODEL ASSUMPTION (§T.10.5) ONLY under `--assume-class-exact`; the default emits the refinement goals and refusals of route #277/#278 instead; counterexample corpus 3100-3101 |
| **FIELD-DISJOINT** — two distinct mutable fields hold distinct objects | one Why3 region per mutable field (frames such as `ensures { self.ys = old self.ys }`) | **Medium** — DECLARED MODEL ASSUMPTION (§T.10.5): reported by `--soundness-report`, no strict mode; counterexample corpus 2570 |
| **PARAM-DISJOINT** — two distinct mutable parameters (or a parameter and `self` / a module-level name), and two distinct elements of a container parameter, hold distinct objects | one Why3 region per `ref`/record parameter (frames such as `ensures { ys = old ys }`), an `array` of independent `array`/`seq` values for `List[List[_]]` | **Medium** — DECLARED MODEL ASSUMPTION (§T.10.5): reported by `--soundness-report`, no strict mode; counterexample corpus 3180-3188 |

### §T.10.2  Preservation Lemmas

For each $\mathcal{T}$ rule, we argue informally that the translation
is faithful:

#### Expression Faithfulness

**Claim:** $\mathcal{T}_e$ preserves evaluation semantics.

- **Integer arithmetic:** `+`, `-`, `*` map directly.  WhyML integers
  are arbitrary-precision, matching Python's `int`.
- **Division:** `//` (floor) and `%` map to floored `pycsl_div`/`pycsl_mod`,
  which correct Euclidean `div`/`mod` by a sign-of-divisor adjustment so the
  result matches Python for every divisor sign (WL-01 FIXED — the positive
  divisor case coincides with Euclidean). `/` (true division) is a separate
  concern (WL-02).
- **Comparisons:** `==`, `!=`, `<`, `<=`, `>`, `>=` map to `=`, `<>`,
  `<`, `<=`, `>`, `>=` respectively.
- **Boolean operators:** `and`/`or` map to `&&`/`||` (`identifiers.py`) in
  **both** spec and body context; `not` maps to `not`. (`not` still takes the
  `(if not a then 1 else 0)` form in body context.)
  **CORRECTION (relaunch #55) — THIS ROW IS TRUE OF THE *CONDITION* POSITION ONLY.** In a
  VALUE position Python's `and`/`or` return an OPERAND, not a boolean, and $\mathcal{T}$
  correctly does the same — see §T.5.12b, which is the accurate description and which this
  row (and the §T.6.6 operator table) contradicted. MEASURED both ways: `return a and b`
  with `a == 3`, `b == 5` proves `\result == 5`, CPython's answer, while the boolean reading
  `\result == 1` does NOT prove; `return a or b` with `a == 0` proves `\result == 5`. No
  soundness consequence — the emitter was right and the summary row was stale — but a reader
  following this row would write a driver the model refuses, and three soundness routes this
  window (#60, #61, #62) began as documentation that asserted something untrue.
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

### §T.10.5  Declared Model Assumptions (routes #250, #253, #256, #276)

Four rows of the §T.10.1 trust base are properties of $\tau$ rather than of any emitted
text: no `assume`, `axiom` or `val` carries them, so `bin/check-assumed-facts.py` (which
classifies emitted assumed facts) cannot see them. They are DECLARED instead — the same
treatment as the reviewed HASH-EQ-CONSISTENCY axiom (UB-7.2, `--strict-hash-eq-consistency`,
corpus 0411/0412): named, listed by `pycsl --soundness-report` under "declared model
assumptions" (JSON `model_assumptions`, each entry with `statement`, `counterexample`,
`strict_mode` and `relied_on_by` = the function, operator and values that rely on it), and
pinned in the corpus by a counterexample that PROVES under the default model (header
`# pycsl-model-assumption: <NAME>`, `# pycsl-expected: PASS`).

**FLOAT-FINITE** — every float value is finite and non-NaN. $\tau(\texttt{float}) =
\texttt{real}$ and `real` has no NaN, so reflexivity of `==`/`<=` and trichotomy hold for
every float value: `ensures x == x` (2500), `ensures x <= x` (2501), `requires x != y ensures
x < y or y < x` (2502) PROVE for `x: float`, and CPython refutes each with `float("nan")`.
Reported for every comparison/`min`/`max` touching a float.
*Strict mode* `--strict-float-finite` (opt-in) lowers, in both paths,

    a OP b  ⟶  (let _pf_a = a in let _pf_b = b in
                 (_pf_a OP. _pf_b) && ok _pf_a && ok _pf_b)     (OP ∈ < <= > >=;
                                                                  == as <=. both ways)
    a != b  ⟶  not (a == b as above)
    ok v    ≡  (v <. pycsl_float_nan || v >. pycsl_float_nan)
    let constant pycsl_float_nan : real = 1.0 /. 3.0              (a definition, no axiom)

`1/3` is not dyadic, so no finite binary64 value and no float literal is the sentinel, but a
parameter or an uninterpreted `float_*_op` result may be. The non-NaN test avoids the logic
`=` (unavailable on `real` in program code); the let-binding evaluates a body operand once.
Under the flag 2503-2505 (the same three claims) FAIL and the controls 2507 (`\result == 1.5`,
a guarded branch, order facts from a precondition, transitivity) PROVE. Cost: 0517 and 1124 —
TRUE claims of the shape `\result == <float arithmetic>` — FAIL, alongside 0818/0847/1120,
which are FALSE for a NaN input. Not covered: ±inf, signed zero, comparisons outside the
binary-operator lowering (a future float `min`/`max` lowering; today `max` on floats is the
int `MinMax.max` and fails closed with a type error), and there is no spec-level `math.isnan`.

**BUILTIN-EXACT** — a value whose static type is a builtin (`int`, `float`, `str`, `bool`,
`bytes`, `tuple`, `list`, `dict`, `set`, `frozenset`) is an exact instance of that type: its
operators are the builtin's, not a subclass's overridden dunders. `def f(x: int): return x - x`
PROVES `\result == 0` (2506); with `class I(int): def __sub__(s, o): return 7`, CPython's
`f(I(5))` is 7, and Python and type checkers both accept the subclass instance. Reported for
every operator node that reads a builtin-typed variable, field or `\result`. There is no
strict mode: fail-closed would remove all builtin arithmetic. (Values that are NOT
builtin-typed — `Any`, `object`, unannotated, TypeVar — are not under this assumption: their
operators are already uninterpreted, routes #249/#251/#252. Route #255 widened that population to every
binding form — a walrus target, a tuple-unpack target, a `match` capture, a lambda parameter bound
from an erased call argument — and to call RESULTS: a unit function or method whose return annotation
is missing, `Any`, `object` or a TypeVar, a `Class.method`/`obj.method` resolved to one, and a
builtin handing back (part of) an erased argument (`abs`, `max`, `getattr`, `next`, `sorted`, ...).)
`bool` is such a subclass of `int` (it overrides `__repr__`/`__str__`/`__format__`'s empty-spec case):
an `int`-typed parameter given `True` is rendered by the value-keyed int renderer (route #291), so
`f"{n}"` for `n: int` is assumed to be the decimal text, not `"True"`.

**CLASS-EXACT** — a value typed with a user class is an exact instance of it. A call `a.m(…)`
with `a: A` lowers to `A.m`'s stub (its `ensures`, its `raises` wrap, its frame), while CPython
runs the override of `type(a)`. Since route #277 the DEFAULT discharges this instead of assuming
it: `_emit_subtyping_goals` emits, for every override pair (computed over the C3 MRO in
`ir_resolve.apply_inheritance`, route #278),

    goal p__t_refines_x : forall self: p, <params>, result.
      ((pre_X -> pre_P) /\ (post_P -> post_X))
      /\ ((pre_X /\ cond_P(E)) -> (cond_X(E1) \/ …))     for each `raises E when cond_P(E)` of P

and `_run_pipeline` refuses (PYCSL-SEM-OVERRIDE-REFINEMENT) an override whose escaping exceptions,
`no_exception` claim, `assigns` locations or positional parameters do not refine the base's
(static semantics App. C.1, "What the default override check covers"). Under
`--assume-class-exact` only the `#@ conforms_to` pairs are emitted, and `--soundness-report` lists
CLASS-EXACT with every override pair and every method call of the unit.

**HVAL-STR-KEYS** — every dict nested inside a `PyVal` value has `str` keys. The `hval`
value model (`type hval = HStr string | HInt int | HArr hval_list | HMap hpairs | HNode hval`,
`hpairs = PNil | PCons string hval hpairs`) keys every nested dict by `string`, while the
annotation `Dict[str, PyVal]` constrains only the TOP-level keys. Two lowerings rely on it: the
`.items()` walk over an `hval` local/param read binds the key `let k = ref (hval_keys_get
(hval_as_map xs) !i)`, a `string` symbol-typed `str`, and the bare `for k in m` binds the
`HMap` arm `HStr (hval_keys_get (hval_as_map m) !i)`. So `isinstance(k, str)` folds to true and
`isinstance(k, int)` to false: 3550-3553 PROVE `\result == True`, CPython refutes them with
`{"xs": {1: 2}}`. A read by a `str` needle (`pairs_get`) is faithful in both modes: the
`hpairs` of a dict are its `str`-keyed entries, and a `str` needle can match only a `str` key.
*Strict mode* `--strict-hval-keys` (opt-in) lowers both key views to the uninterpreted

    val function hval_keys_hget (m: map string (option hval)) (i: int) : hval   (no spec, no axiom)
    for k, v in xs.items()   ⟶  let k = (hval_keys_hget (hval_as_map xs) !i) in   (k a pyval local)
    for k in m  (HMap arm)   ⟶  | HMap _ -> hval_keys_hget (hval_as_map m) !i

so 3554-3557 FAIL and the controls 3558 PROVE. Cost (measured, route #298): a key that flows
into a `str` sink (`return k` from `-> str`, `"None" in k`, an f-string, `seq string` append,
a `map string` key) does not type-check, which is why the faithful key is not the default:
3 self-annotation mirrors would need a new pyval-to-str coercion at 13 sinks.

**BARE-CONTAINER-INT** — an element of a parameter annotated with a BARE container (`list`,
`List`, `Sequence`, `Iterable`, `tuple`, `Tuple`, ... with no element type) is an int. Such a
parameter lowers to `array int` (`list`) or to an `int` read by `subscript_get` (`List`), so
`xs[0] % 1 == 0` (4363) and `xs[0] * 0 == 0` (4364) PROVE, and CPython refutes them with
`[0.5]` and `["a"]`. Reported for every function with such a parameter. Under
`--strict-bare-containers` the element is an origin of the §T.6.29 check, so 4348-4349 are
refused. Cost (measured, route #330): 90 corpus files (76 of them unlabelled proved drivers)
use a bare-container element as an int, which is why the strict reading is not the default.
Route #334 extends it to a VALUE of a bare `dict` / `Dict` / `Mapping` parameter (`map ..
(option int)`): `d["a"] % 1 == 0` proves (4443) and is refused under the strict flag (4427);
making it an origin by default refused 3 corpus files and 1 mirror file (measured).

**LATIN1-STR** — every str value consists of code points 0..255. $\tau(\texttt{str})$ is the
Why3 `string`, whose characters are `string.Char`s, and Why3's `axiom code: forall c. 0 <= code c
< 256` holds for every one of them; `ord` lowers to `Char.code (Char.get s i)` (contract) /
`char_code_at`, `ord_op` (body, `ensures { 0 <= result < 256 }`) and `chr(n)` to `(Char.chr
n).contents`, which round-trips only below 256 (`axiom code_chr`). So `requires len(s) == 1
ensures \result < 256` over `return ord(s)` (3020), `ensures \result != 300` over `return
ord(chr(300))` (3021), `ensures ord(s) < 256` (3022) and `ord(s[0]) < 256` (3023) PROVE, and CPython
refutes them with `"€"` (8364) and 300. Every `ord`/`chr` site relies on it directly, and so do the
cited codec lemmas stated over `Char.code` (`field_to_str_round_trip`, the os `dir_blit_marker*`
facts); str VALUES in general rely on it, because the str sort is the 8-bit string. Reported for
every `ord`/`chr` call and every function reading a str value.
*Strict mode* `--strict-latin1` (opt-in) lowers, in both paths,

    ord(s[i])  ⟶  pycsl_cp s i              (body: val pycsl_vord_at, ensures result = pycsl_cp s i)
    ord(x)     ⟶  pycsl_cp x 0              (body: val pycsl_vord_op)
    ord("c")   ⟶  the code point of c       (a one-character ASCII literal)
    chr(n)     ⟶  pycsl_chr n               (body: val pycsl_vchr_op — length 1,
                                             result = pycsl_chr n, 0 <= n < 0x110000 -> pycsl_cp result 0 = n)
    function pycsl_cp (s: string) (i: int) : int =
      let r = pycsl_cp_raw s i in if 0 <= r <= 1114111 then r else 0   (a definition, no axiom)

Under the flag 3024-3027 FAIL and the controls 3029 PROVE (including `ord(chr(n)) == n` over the
whole range, which the default model cannot prove). Cost: the proofs that pass `ord(name[i])` to a
lemma over `Char.code` (route #276 resolution lists the measured files). Not covered: the str sort
stays 8-bit (pigeonhole over > 256 distinct one-character values is derivable in principle), and a
non-ASCII literal is emitted as UTF-8 bytes in both modes. `ord` of a string whose length is not 1
raises `TypeError`, which lies outside the `no_exception` universe (`KNOWN_EXCEPTIONS`), so no
`len(s) == 1` obligation is owed under `no_exception` — a declared scope limit, not a repair.

**FIELD-DISJOINT** — two distinct mutable fields (a `list`/`dict`/`set` or a record value; of one
record, or the same field of two record values) hold distinct objects. Each mutable field is its own
Why3 region, so a write through `self.xs` leaves `self.ys` unchanged (the emitted frame says so);
Python lets two fields hold ONE list. `T.poke` (`assigns self.xs`) with `self.xs[0] = 7; return
self.ys[0]` under `requires self.ys[0] == 0` PROVES `\result == 0` (2570), and CPython returns 7 for
`L = [0]; T(L, L).poke()`. A VERIFIED program cannot build the alias: storing a non-fresh dict/set
into a field or an escaping slot is refused (R167, routes #243/#244), one object in a mutating slot and
another slot of one call is refused (route #254), and Why3 itself rejects two list refs in one call.
The residue is an alias built in UNVERIFIED code — the ownership discipline's rule R1
(`docs/pycsl-ownership-discipline.md` §2). Reported for every function that mutates a mutable field
in place and also reads or mutates another mutable field (matched by field name, conservatively). No
strict mode: refusing such a method instead (route #256's option (b)) was measured at 15 root-corpus
files (e.g. the `Bank.transfer` drivers 0723-0725) and 7 mirror files (41 methods, among them
`_emit_body_code`), and PyCSL has no separation precondition in which to state the disjointness.


**PARAM-DISJOINT** — FIELD-DISJOINT's twin for parameters and elements (route #282). A `List`/`dict`/
`set` parameter is its own `ref` (or by-value array) region, a record parameter its own record value,
the receiver `self` its own record, and a `List[List[int]]` an array of independent element values, so
the WP frame of a write through one of them says nothing changes behind another: `f(xs, ys)` with
`assigns xs[0]`, `xs[0] = ys[0] + 1` PROVES `ensures ys[0] == \old(ys[0])` (3180) and CPython
violates it for `a = [1]; f(a, a)`; the same holds for two record parameters (3181), for
`xss[0][0] = 9` against `xss[1][0]` with `xss = [r, r]` (3182), two dicts (3183), `self` and a
parameter of its class (3184, `x.bump(x)`), a parameter and a list field of `self` (3185,
`T(L).m(L)`), a parameter and an element of a `List[List[int]]` (3186, `f(r, [r])`), and a caller
forwarding two of its own parameters (3188, `h(p, q)` -> `f(p, q)`). A module-level list a function
reads is counted as a handle too (`f(G)`), although no proving witness of that shape exists: such a
global is emitted as an opaque `val constant` (no corpus file; the probe times out). A VERIFIED program cannot build these aliases: Why3 rejects
one list ref in two arguments ("illegal alias"), a dict/set in a mutating slot and another slot is
refused (route #254, PYCSL-WHYML-COLLECTION-ALIAS), a non-fresh mutable stored into a field or escaping
slot is refused (R167, routes #243/#244), `[r, r]` / `m.append(r)` give an `array (array int)` that
the `matrix` parameter rejects, and `x.bump(x)` is ill-typed (all fail closed, controls 3189-3196). The
residue is an alias built in UNVERIFIED code — rule R1 of the ownership discipline
(`docs/pycsl-ownership-discipline.md` §2). Reported for every function that writes through one
mutable handle (a parameter, `self`, or a module-level name it reads: subscript store/`del`, field
store, augmented assignment, any method call on it, passing it to a non-builtin call, an `assigns`
location rooted at it) and also reads or writes another handle, and for every function that writes an
element of a container handle; handle types are not matched (over-, never under-reported). No strict
mode: the measured population is 112 of the root corpus files (180 functions) and 33 of the 53 mirror
files (2731 entries, e.g. every `self`-mutating method that reads an IR node parameter), and PyCSL has
no separation precondition in which to state the disjointness.
---

## §T.11  Gap Analysis

### §T.11.1  Translation Gaps

| ID | Gap | Impact | Recommendation |
|----|-----|--------|----------------|
| G1 | ~~Python floored division vs WhyML Euclidean division~~ **RESOLVED (WL-01 FIXED)** | The divergence is on a **negative divisor**, not a negative dividend: `(-7)//2` is `-4` in BOTH Python and Euclidean `div` (the earlier "`div (-7) 2 = -3`" note was wrong — Euclidean agrees here). The real bug was `(-7)//(-2)` (Python `3`, Euclidean `4`) and `7%(-2)` (Python `-1`, Euclidean `1`), which PyCSL proved as the false Euclidean values. `pycsl_div`/`pycsl_mod` now emit floored `div`/`mod` corrected by a sign-of-divisor adjustment (`if mod x y <> 0 && y < 0 then div x y − 1`, `+ y` for mod); positive-divisor emission is byte-identical to Euclidean. SMT (Alt-Ergo + Z3) discharge the concrete cases; no new axiom. Drivers: reference 0811 (POSITIVE), 0812 (NEGATIVE FAIL twin); repro `getting-better/wrong-lowering/wl01_*`. | Done — floored `pycsl_div`/`pycsl_mod` |
| G2 | ~~String hashing is lossy~~ **RESOLVED + content-faithful (cleared-string.md)** | Runtime `str` is Why3 `string.String` with real content (τ(str)=string; §T.6.15). Concatenation and slicing prove their exact CONTENT (not just length) via Why3 1.8.2's rich native theory — `(a+b)[:len a]==a` (0765), `s[0:2]+s[2:4]==s[0:4]` (0766) — with NO new axiom; `startswith`/`endswith`/`find` accept derived string receivers (0767). The `chars:seq int` codepoint model in the plan was NOT needed (native decomposition reasons better; spike + choices.md cleared-string S0). `lower`/`upper` are now deterministic + idempotent + literal-constant-folded (cleared-string RESIDUALS item 1; drivers 0791/0793) and `replace` gains a not-contains identity + literal fold (item 2; drivers 0792/0794). Residual (honest, documented): no code-point/char type; the per-char ASCII case-MAP on a SYMBOLIC string (needs a codepoint bridge + `is_ascii` contract surface, zero demand), full-Unicode folding (`ß→SS`, not length-preserving), general grow/shrink `replace` CONTENT (CPython all-occurrences ≠ Why3 first-occurrence `replace`; no faithful `replaceall` content axiom), `strip`, `split`, `.decode`/`.encode`, `%`/f-string content stay opaque (`str`-keyed record-field dicts/sets use the native string key — cleared-hash.md S4, drivers 0772–0776) | Symbolic per-char case-MAP & general-replace content are the residual |
| G3 | Boolean/int duality | `True + 1 = 2` in Python; in spec `true + 1` is a type error | The spec/body distinction handles this, but mixed use is fragile |
| G4 | `None` mapped to `0` in non-ghost context | `None` and `0` are indistinguishable in WhyML for regular Python values | **Partially resolved:** ghost dicts use `map int (option int)` (§T.8.5), so `\has_key` distinguishes absent keys from keys with value 0. Raw Python `None` in non-ghost context still maps to 0. |
| G5 | Array literals use fixed size 1024 | `[]` becomes `Array.make 1024 0` regardless of actual size | Use dynamic allocation or parametric size |
| G6 | **List/Dict/Set comprehensions content-faithful for lifting shapes** (cleared-array.md S1–S5 + items 1,3,4) | LIST `[x for x in a]` / `[x+1 for x in a]` / `[p.x for p in a]` / `[g(x) for x in a]` (identity / pure-int `+ - *` / FIELD PROJECTIONS / CALLS to a pure `let function`, over the loop target, `array int` source) carry a per-index law `result[i] = <elt[target:=src[i]]>` + `length result = length src`. FILTER `[x for x in a if cond]` keeps `length <=` and — identity element + lifting pure-bool `cond` — the content-SUBSET law (each survivor satisfies `cond` and ∈ src). DICT `{x: v for x in a}` (identity key + pure-int value) → `Map.get result (a[i]) = Some v`; SET `{f(x) for x in a}` (pure-int elt) → `Map.get result (f(a[i])) = Some 0` (membership). Subscript projection `[x[k] …]` is now content-faithful over a NESTED source (nested-list.md S4: `List[List[τ]]`→`array (seq τ)`, `result[i] = Seq.get (a[i]) k`), INCLUDING a **TARGET-DEPENDENT** index `[x[len(x)-1] …]` that lifts to a pure int term over `len(x)` (nested-list.md §8/§9 EXTENSION, `_lift_target_seq_index`: `result[i] = Seq.get (a[i]) (Seq.length (a[i]) - 1)`; driver 0808, NEGATIVE 0809). Residuals stay opaque: non-identity dict key / non-pure-int value/elt, string/emit_ir elements, multi-generator, and a subscript index that does NOT lift (a `g(x)` call over the seq) | — |
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
| `@property` getter | `Module5_IREmitter._should_skip_method` | Emitted as an ordinary nullary method `<class>__<name> (self: <class>)`; the decorator itself carries no semantics, so the getter is translated exactly like a plain 0-argument method and its `#@` contract is discharged the same way |

### §T.11.3  Missing Translations

The following constructs appear in Python but have no translation:

| Construct | Status | Workaround |
|-----------|--------|------------|
| `class` inheritance | Not supported | Flatten class hierarchy |
| `@staticmethod` | Not supported | Use plain methods |
| `*args`, `**kwargs` | Not supported | Use explicit parameters |
| `yield` / generators | Not supported | Use explicit loops |
| `async` / `await` | Not supported | Use concurrent model |
| `global` / `nonlocal` | Not supported | Use explicit parameter passing |
| List comprehensions (content) | Content-faithful for identity / pure-int `+ - *` / field projections `p.x` / CALLS `g(x)` to a pure `let function` over the loop target (cleared-array.md S1–S5 + items 1,3,4); filter keeps a length bound + (identity elt, lifting `cond`) a content-subset law; dict `{x: v …}` (identity key) + set `{f(x) …}` carry membership laws; subscript projection `[x[k] …]` + non-identity/non-pure-int shapes opaque | Use explicit loops for unliftable elements |

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
| `del d[k]` (DelSubscript) | `d := map_update_none !d k` |
| `d[k]` (read) | `(match Map.get !d k with \| Some v_ -> v_ \| None -> 0 end)` |
| `k in d` | `(match Map.get !d k with \| Some _ -> true \| None -> false end)` |
| `k not in d` | `(match Map.get !d k with \| Some _ -> false \| None -> true end)` |

**`del d[k]` (wrong-lowering-to-fix.md §WL-05c).** Module 5 emits a typed `DelSubscript`
IR (`ir_schema.DelSubscriptStmt`) — NOT the old blanket `Pass` no-op, which silently
dropped the deletion and let a read/claim of the deleted key unsoundly prove its old
value. Module 6 (`statements.py::_handle_del_subscript_stmt`) clears the key with
`map_update_none` (= `Map.set m k None`) for a **LOCAL** dict/set, on the caller-visible
`ref (map …)` for a **STANDALONE** dict/set **parameter** (WL-05b promotion, whose seed
now also detects `DelSubscript`), and **REJECTS** it on a dict/set **METHOD** parameter
(the WL-05 caller-visible-mutation boundary — see the §WL-05c note below). A non-dict/set
`del` (`del a[i]` on a list, `del name`, `del obj.attr`, slice delete) stays the prior
unmodelled no-op.

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

**§ Caller-visible dict/set PARAMETER mutation (wrong-lowering-to-fix.md §WL-05b; UB catalog §7.9).**
The `d := map_update_some !d k v` / `s := map_update_some !s x 0` emissions above assume the collection
is a `ref` — the `:=`/`!d` deref is well-typed only for a `ref`. For a **STANDALONE function**, a
`Dict[...]`/`Set[...]` **parameter** that the body INNER-mutates is therefore promoted to a mutable
`ref (map κ (option ν))` with a sound `writes {d}` frame:

```
T[[def f(d: Dict[κ,ν]) with d item-mutated]]
  =  let f (d: ref (map κ (option ν))) : … writes { d } = …   (* reads: !d / Map.get !d k *)
```

Python passes dicts/sets BY REFERENCE, so the write is VISIBLE to the caller: at the call site
`f(x)` the argument at a mutated position is passed as the **bare ref** `x` (not `!x`), so `f`'s
`writes {d}` mutation escapes and `x`'s post-state reflects it (`_handle_call_expr`). Promotion is
USAGE-DRIVEN via a module-level FIXPOINT (`_build_func_mutated_collection_params`: direct item-mutation +
transitive param forwarding) — a READ-ONLY dict/set param keeps the by-value `map …` type
(BYTE-IDENTICAL). A mutating callee should state the post-value (`#@ ensures d["a"]==5`) for a caller to
rely on it, else the frame havocs the param. **Still REJECTED** (code `PYCSL-WHYML-PARAM-COLLECTION-MUT`,
`_reject_param_collection_mutation`): a mutated dict/set **METHOD** param (its types feed the cross-method
call-contract map), the `@mutable_state` param no-op, a `List[<record>]` element field store `a[i].f=v`
and a PURE-record param field store (§WL-05d fail-closed), and nested-list inner mutation. (A MUTABLE-record
param field store `p.f=v` and a LIST param element store `a[i]=v` are now SUPPORTED — §WL-05d.)
Drivers 0820/0821/0832/0833 (positive), 0822/0823 (LOCAL positive), 0834 (negative false-claim).

**§WL-05c — dict/set METHOD-param mutation is a DOCUMENTED BOUNDARY; `del d[k]` fail-OPEN fixed.**
The STANDALONE promotion above does NOT extend to a **METHOD** dict/set parameter: a method call
`obj.m(d)` lowers to a SEPARATE synthesized abstract `val` (over five call-site variants —
plain-abstract, `self.`-concrete, cross-module `<G>Sig` refinement, `#@ sibling_concrete`,
composed-provider), all fed by `_module_method_param_types`. Promoting the method param to `ref (map …)`
would have to thread the ref type + `writes {x_i}` + the propagated ensures through ALL FIVE in sync;
a miss on any path (ensures propagated without the matching `writes`) fails OPEN, and set `.add` on a
method param is overloaded with the sound `@mutable_state` no-op. So a mutated dict/set method param
stays **REJECTED** (or the sound `@mutable_state` no-op). The `del d[k]` row above is the WL-05c fail-OPEN
fix: `del` used to be a blanket Module-5 `Pass` no-op that unsoundly proved a deleted key survived; it is
now faithful (local / standalone-param) or rejected (method param). Spike
`test-suite/corpus/conformance/spikes/wl05c_del_spike.mlw`; drivers `wl05c_*`; locks 0854–0857.

**§WL-05d — record/list PARAMETER item/field-mutation.** The by-reference escape of a dict/set param
(WL-05b) has three siblings for record/list params, settled per-sub-case:

```
T[[def f(a: List[τ]) with a[i]=v]]   =  let f (a: array τ) : … = a[i] <- v      (* Why3 INFERS writes {a} *)
T[[def f(p: C) with p.x=v, C mutable]] =  let f (p: c) : … = p.x <- v            (* Why3 INFERS writes {p.x} *)
```

- **(A) LIST param element store `a[i] = v`** — ALREADY sound with no code change: a `List[int]` param is
  ALREADY `array int` (a Why3 MUTABLE type), so `a[i] = v` lowers to the native `a[i] <- v` and Why3
  INFERS the write effect on the concrete `let` → caller-visible. Write-read-back PROVES, a caller
  observes the write, a false-twin stays UNPROVEN.
- **(B) RECORD/@dataclass param field store `p.x = v`** — a standalone (non-list-element) record param is
  a MUTABLE Why3 record `{ mutable x; … }`; the store lowers to `p.x <- v` (Why3 infers `writes {p.x}`),
  caller-visible + sound. This was a **severity-1 fail-OPEN before WL-05d**: Module 5 (`_py_stmt_assign`)
  emitted a `FieldAssign` IR ONLY for a `self` attribute base, so a non-`self` `p.x = v` matched NO arm
  and was SILENTLY DROPPED (a no-op) — a caller/body could prove the field UNCHANGED after a real
  mutation (`p.x = 5` then `ensures p.x == 3` proved Valid). Module 5 now emits `FieldAssign(object=<var>)`
  when the attribute base is a Name in the function symbol table (a param/local).
- **Fail-closed:** a field store through a **non-Name base** (`a[i].f = v` subscript base, `x.y.f = v`
  nested) is REJECTED at Module 5, and a field store on a record whose class is pinned PURE in
  `_list_element_record_types` (a `List[<record>]` element — immutable, Why3 forbids a mutable element
  inside `array`) is REJECTED at Module 6 (`_handle_fieldassign_stmt`) — code
  `PYCSL-WHYML-PARAM-COLLECTION-MUT`. Both previously silent-drop fail-OPENs.
- **Unchanged (separate boundary):** a **module-GLOBAL singleton** field store `g.v = n` (attribute base
  is a Name NOT in the function symbol table) keeps its prior no-op — the HAPPY subsystem-ownership tests
  (0611–0613) rely on it; module-global mutable-record aliasing is a distinct class outside this scope.
- Spike `test-suite/corpus/conformance/spikes/wl05d_record_param_mut_spike.mlw` (5/5 goals Valid on
  Alt-Ergo AND Z3, no new axiom); drivers `wl05d_*`; locks 0858 (POSITIVE store), 0859 (POSITIVE
  caller-visible), 0860 (NEGATIVE — the fixed severity-1 false-twin), 0861 (NEGATIVE — list-element field
  store REJECTED). Full-corpus byte-diff 0; `\trusted` non-increasing.

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

**`Any` arm (route #258):** a Union with an arm the model cannot type (`Any`,
`object`, an unknown/lowercase name, a nested `Optional`/`Union`, an unmodelled
generic such as `Sequence[int]`) is NOT a variant: the whole annotation lowers to
the erased `Any` value (an `int` term with route #249/#251/#252's erased
treatment). Dropping the arm (the former GT1 lowering) made `Optional[Any]` a
None-only type, so `x is not None` was dead and false claims proved.

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

### §T.14.5a  Content-faithful list comprehensions (cleared-array.md S1–S4 + S2)

A list comprehension `[elt for t in src (if cond)]` is lowered by
`_content_comp` (`module6_whyml/expressions.py`) to a **per-instance abstract
val** `list_content_comp_<n>` carrying a per-index content law — *when* the
element shape is liftable — and otherwise falls through to the opaque
length-only `list_comp` path (§T.11.1 G6).

**Liftable shape (S1 identity, S3 arithmetic, S2 projection, item 1 call):**
exactly one generator whose target `t` is a plain name, an `array int` source
`src` (NOT a `seq` local — the seq comprehension path owns those), no filter, and
an element `elt` that lowers to a **pure, total `int`** logic term over the loop
target `t` ONLY, built from: the identity `t`, integer literals, the total
operators `+ - *`, — **cleared-array.md S2** — FIELD PROJECTIONS `e.attr` over a
liftable base (`[p.x for p in a]`, `[p.x + p.y for p in a]`), and —
**cleared-array item 1** — CALLS `g(e, …)` to a module function already emitted
as a pure `let function` (`[g(x) for x in a]`; see the call-comprehension note
below). Division/modulo, comparisons and booleans are excluded — they are not
guaranteed pure-int logic terms, and division would leak partiality into a logic
`ensures`. **SUBSCRIPT projection `x[k]` (nested-list.md S4)** is ALSO liftable
when `src` is a NESTED-list param (`array (seq τ)` / `array (map κ (option ν))`,
`_list_nested_elem`): `_nested_subscript_comp` emits the content law
`result[i] = Seq.get (src[i]) k` (seq) / `Map.get (src[i]) key` (map), with the
captured index var `k` threaded as an extra val parameter; driver 0799. The index
may also be TARGET-DEPENDENT (nested-list.md §8/§9 EXTENSION) when it lifts to a pure
int term over `len(x)` (`_lift_target_seq_index`): `[x[len(x)-1] for x in a]` →
`result[i] = Seq.get (src[i]) (Seq.length (src[i]) - 1)` (driver 0808, NEGATIVE 0809).
The generic (non-nested) emitted val:

$$\texttt{list\_content\_comp}_n(\textit{src}):\quad
  \texttt{Array.length result = Array.length } \textit{src}
  \;\wedge\;
  \bigl(\forall i.\ 0 \le i < \texttt{len}\ \textit{src} \Rightarrow
     \texttt{result}[i] = \textit{elt}[\,t := \textit{src}[i]\,]\bigr).$$

The element is lowered once with the target `t` rebound (via a fresh scalar
binder `_celt = src[i]`) to the per-index source read, in logic context. The
free variables of `elt` must be `⊆ {t}` (a captured enclosing local is not a
parameter of the val ⇒ opaque fallback). Corpus: `0761` (identity), `0762`
(arithmetic), `0769` (projection), `0770` (arithmetic-over-projection),
`0764`/`0771` (NEGATIVE — a false content claim, respectively `result[i]=a[i]+1`
on an identity comprehension and `result[k]=a[k].y` on an `[p.x …]` projection,
is correctly rejected).

**Projection lowering (S2) — the getter must be logic-usable.** In the
int-collapsed list model a source element `src[i]` is an `int`, so a projection
`p.x` lowers to the abstract getter `get_x : int → int`
(`_handle_attribute_expr`). The per-index law is therefore
`result[i] = get_x(src[i])`, a faithful re-expression of `a[i].x`. Two enabling
choices make this consumable and sound:

- **Getter as a pure `val function` in spec context.** `_handle_attribute_expr`
  emits `get_attr` as a `val function` (not a program `val`) whenever the access
  occurs in a logic/spec context (`self._in_spec`). A program `val` is
  non-deterministic and unusable in an `ensures`; the `val function` form is a
  deterministic pure symbol — usable in logic and denoting ONE value across every
  mention, so a driver's `\result[k] == a[k].x` (same `get_x`) matches the
  content law. This is a faithful refinement (a field read *is* deterministic);
  it removes spurious non-determinism, never adds a value claim. It is inert on
  every existing corpus program (0 of them emit a spec-context `get_` fallback)
  and byte-identical for body-only getters (still a plain `val`).
- **Subscript-then-projection contract syntax `a[k].field`.** The consumer form
  `\result[k] == a[k].x` requires the contract grammar to parse a projection off
  a subscripted element; see the concrete-syntax reference (`SubscriptFieldAccess`
  → `Attribute(Subscript(…), field)`, the SAME IR the body path produces).
- **Self-field base `self.f[i].sub` (concrete syntax §3.1.4d).** The same
  production with `self.<field>` as the collection base. Module 5
  (`_csl_subscript_field`) lowers the dotted base `"self.<field>"` to
  `Attribute(Subscript(FieldGet(self, field), index), sub)` — byte-for-byte the
  IR the body path emits for `self.toks[self.i].py_type` — so Module 6's
  self-field array-read projector (`expressions.py`, `_record_array_fields`)
  emits the native `(let _rec_ = toks[i] in _rec_.<label>)` instead of the
  unbound abstract getter `get_<sub>` (an unbound symbol fails the whole file).
  Two supporting refinements: (a) `_record_array_fields` is registered in a
  PRE-PASS before class invariants are lowered (`preamble.py`), since the
  invariant is emitted inside the record declaration, ahead of the witness loop
  that previously populated it; (b) a class invariant of the shape
  `self.<f>[<idx>].<sub> == "<literal>"` PINS that element field in the record's
  `by {}` inhabitance witness (`_extract_elem_field_pins`) — sound because
  `Array.make N <lit>` makes every element the same literal, so the pin holds at
  every index. Conflicting pins are dropped rather than guessed, leaving an
  honestly failing inhabitance goal. Corpus 0900 / 0901.

**Call comprehension (item 1) — the callee must be a logic symbol.** A call
`g(e, …)` lifts only when `g` is a **module function already emitted as a pure
`let [rec] function`** — i.e. `emits_as_logic_symbol(g)` (pure = `assigns
\nothing`, non-diverging, non-method, non-lemma, no local refs). Such a `g` IS
usable in a logic term, so the per-index law `result[i] = g(src[i])` type-checks
and a driver's own `\result[k] == g(a[k])` denotes the SAME `let function g`.
The gate reads the set of functions emitted as logic symbols SO FAR
(`_emitted_logic_funcs`, populated in callee-before-caller SCC order), so `g` is
already declared when the caller's comprehension is processed. Because the
content-law val references a USER function, it cannot go in the early abstract-op
block (which precedes ALL functions — `g` would be unbound there); it is
**deferred** (`_late_content_ops`) and spliced in just before the using
function's `let` line by `_insert_late_content_ops`, landing after `g`. Sound: a
pure `let function` is a total deterministic logic symbol, so `result[i] =
g(src[i])` is a faithful re-expression of `[g(x) for x in a]`. Corpus `0783`
(positive `\result[k] == g(a[k])`), `0784` (NEGATIVE — false `= g(a[k]) + 1`
rejected). A NON-pure callee never enters `_emitted_logic_funcs`, so it never
lifts (opaque fallback), and a mis-anchored deferral fails the L3 typecheck
loudly (never a false proof).

**Filter (S4 + item 4):** a comprehension with an `if` always keeps the sound
bound `Array.length result <= Array.length src`. When the element is the
IDENTITY (`[x for x in a if cond]`) AND every filter predicate `cond` lifts to a
pure-bool logic term over the target (a comparison `< <= > >= == !=` of pure-int
terms, or an `and`/`or`/`not` of such), it ALSO carries the **content-subset
law** (`_filter_subset_law`): each survivor satisfies `cond` and appears in `src`
—

$$\forall i.\ 0 \le i < \texttt{len result} \Rightarrow
  \textit{cond}[\,t := \texttt{result}[i]\,]
  \;\wedge\;
  \bigl(\exists j.\ 0 \le j < \texttt{len src} \wedge
    \texttt{result}[i] = \texttt{src}[j]\bigr).$$

The source index of a survivor is LOST (the survivors are compacted), so no
per-index content law holds — only the honest subset facts. A non-identity
element or a non-lifting predicate keeps the length-only bound. Corpus `0763`
(length bound), `0789` (positive `\result[k] > 0`), `0790` (NEGATIVE — false
over-strong `\result[k] >= 5` rejected).

**Dict / set comprehensions (item 3).** `{k: v for x in a}` and `{f(x) for x in
a}` (`_dict_content_comp` / `_set_content_comp`) now carry content laws when the
key/value/element shapes lift, over an `array int` source with one generator and
no filter:

- **Dict `{x: v(x) for x in a}` — IDENTITY key + pure-int value.** Lowers to a
  `map int (option int)` with the per-source membership law
  `∀ i. Map.get result (src[i]) = Some (v[t:=src[i]])`. The identity-key guard is
  the soundness pin: a non-injective key would make the per-source law unsound
  (Python keeps the LAST colliding write), but with an identity key every
  collision maps to the SAME key and — the value being a deterministic function
  of the key — the SAME value, so insertion order is irrelevant. It is an
  under-approximation of the domain (nothing about keys not in `src`). A
  non-identity key stays opaque (`dict_comp`). Corpus `0785` (positive
  `\has_key` + `\map_get`), `0786` (NEGATIVE — false value rejected).
- **Set `{f(x) for x in a}` — pure-int element.** Lowers to a `map int (option
  int)` (set model, present = `Some 0`) with the membership law
  `∀ i. Map.get result (f[t:=src[i]]) = Some 0` — every produced element is
  present. Sound under-approximation (nothing about ABSENT elements). Corpus
  `0787` (positive `\has_key`), `0788` (NEGATIVE — a non-produced element's
  membership rejected).

A function returning a set/dict/frozenset triggers the `map.Map`/`option.Option`
import in the preamble even with no body-level map op (the signature type is
`map int (option int)`).

**Residuals (opaque, never a false content claim):** the following element
shapes fall through to `list_comp` / `list_comp_stmts` / `list_comp_seq_*`
(length-only or fully opaque):

- **Subscript projection `[x[k] …]`** — **LIFTED (nested-list.md S4).** A
  `List[List[τ]]` source now lowers to `array (seq τ)` (a `List[Dict[..]]` source
  to `array (map κ (option ν))`), so the loop target `x` IS a real `seq`/`map` and
  `x[k]` is a faithful `Seq.get`/`Map.get`. `[x[k] for x in a]` carries the
  per-index content law `result[i] = Seq.get (a[i]) k` (`_nested_subscript_comp`),
  proving `\result[i] == a[i][k]` (driver 0799). The captured index var `k` becomes
  an extra parameter of the abstract val. **DEEPER nesting + TARGET-DEPENDENT index
  (nested-list.md §8/§9 EXTENSION):** a deeper `a[i][j][k]` NOW reads content-faithfully
  to the depth-4 bound (`_nested_access_type`; drivers 0805/0806, beyond-cap 0807), and
  a target-dependent index `[x[f(x)] for x in a]` whose `f(x)` lifts to a pure int term
  over `len(x)` (e.g. `x[len(x)-1]`) carries the law
  `result[i] = Seq.get (a[i]) (Seq.length (a[i]) - 1)` (`_lift_target_seq_index`; driver
  0808, NEGATIVE 0809). Residual: an index that does NOT lift (a `g(x)` call over the
  seq, a non-`len` seq op), a read deeper than depth 4, or an un-annotated leaf stays
  opaque; those keep the scalar `int` / opaque path.
- **Non-identity dict key / non-lifting dict value / non-pure-int set element** —
  the collision-unsoundness / purity guards above are not met; opaque `dict_comp`
  / `set_comp`.
- string / seq / emit_ir elements, multi-generator, captured locals.

No new `proof_axiom_allowlist` entry — every content law is a definitional
`ensures` on the abstract val, discharged where the comprehension is used.

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

`bytes` semantics — `.encode`, `.decode`, `.ljust`, `.split`,
`struct.pack` / `struct.unpack` round-trip beyond cleared-pack —
are out of scope of §T.15 (format-string-aware emission + Rocq
round-trip axioms + per-method bytes-method modeling). **DONE since
this note:** faithful byte CONTENT of a `bytes` LITERAL and the
byte-range constraint `0..255` (both §T.15.7, WL-06b); the
coherent `b[i]`/`len(b)` read (§T.15.6, WL-06); the implicit
byte-RANGE invariant `0<=b[i]<256` for an *unknown* `bytes`/
`bytearray` PARAMETER (§T.15.8, WL-06c); and faithful byte CONTENT of
an ASCII str-LITERAL `.encode()` plus the constructor
`ValueError`-as-precondition (both §T.15.9, WL-06d). What remains is
the exact CONTENT of an unknown `bytes` parameter (user `requires`
only), non-literal / non-ASCII `.encode`, `.decode`, and the
deeper-`struct` / byte-method semantics above — see §T.15.9's boundary
table.

### §T.15.6  Byte read `b[i]` and `len(b)` (WL-06)

Because a `bytes`/`bytearray` value is the `array int`-backed
buffer (§T.15.1), a subscript READ `b[i]` lowers to a native
array read `Array.get b i` — a coherent `int` byte read — and
`len(b)` lowers to `Array.length b`, exactly as for a `list`/array
parameter. In `expressions.py`, `_handle_subscript` and the `len`
handler recognize a `bytes`/`bytearray` symbol-table type on the
same array branch as `list`.

`T_e(b[i]) = (b[i])` (`Array.get`, an `int`), guarded by an
IndexError bounds VC (`0 <= i < Array.length b`).
`T_e(len(b)) = (Array.length b)`.

Before the fix (WL-06, `wrong-lowering-to-fix.md`), a bytes/
bytearray subscript READ routed instead to the opaque
`val subscript_get (x:int)(i:int):int` applied to `b : array int`
— an `array int` vs `int` type error (fail-closed TYPEERR): the
read was BOTH un-verifiable AND internally inconsistent. The fix
makes the emission COHERENT and type-checking.

**Residual (superseded for LITERALS by §T.15.7).** For a `bytes`
value with *unknown* content (a `bytes` PARAMETER), the byte value
stays the τ-blessed `bytes=int†` opaque residual: what is soundly
provable is that the read is a well-typed `int` denoting a fixed
buffer cell (so a body `b[i]` and a contract `b[i]` denote the SAME
value, and distinct indices are independent cells), NOT the exact
byte value. §T.15.7 makes the CONTENT of a `bytes` LITERAL faithful.

### §T.15.7  Faithful byte CONTENT of a `bytes` literal + immutability (WL-06b)

A `bytes` LITERAL already lowers to an `ArrayLit` of the REAL byte
values (§T.15.2), and Module6 emits that `ArrayLit` as a native
`array int` constructed with those exact values
(`Array.make n v0; a[1] <- v1; …`). Therefore a byte-content READ
of a literal denotes the ACTUAL byte and PROVES:

`T_lit(b"abc") = (let a = Array.make 3 97 in a[1] <- 98; a[2] <- 99; a)`

so `b[0] = 97`, `b[1] = 98`, `b[2] = 99` are provable (ordinals of
`'a','b','c'`), and hex escapes carry their real byte
(`b"\x01\xff\x80" → [1, 255, 128]`). The **byte-RANGE invariant**
`0 <= b[i] < 256` is DERIVABLE for every index of a literal — no
axiom, it follows from the concrete construction (each literal byte
is a Python `int` in `[0,256)`). A FALSE byte-content claim
(`b"abc"[0] == 98`) is NOT provable (0837). The coarse
`bytes = int†` `array int` SHAPE is KEPT — this is content
faithfulness ON TOP of it, additive.

To realize this content faithfully, Module5's
`_build_function_symbol_table` classifies a local bound to a `bytes`
LITERAL (`b = b"…"`) as symbol-table type `"bytes"` (not `"Any"`),
which routes its `b[i]`/`len(b)` through the §T.15.6 native-array
branch. A `bytes(...)`/`bytearray(...)` CONSTRUCTOR call is left
`"Any"` (unchanged — no emission change for existing corpus code).

**Immutability.** A Python `bytes` object is IMMUTABLE: `b[i] = v`
raises `TypeError: 'bytes' object does not support item assignment`.
The `"bytes"` classification lets `core_ir_semantic._sa_immutable_walk`
REJECT a subscript-store `b[i] = v` to a `bytes` variable
UNCONDITIONALLY (not gated on annotation, `PYCSL-SEM-SUBSCRIPT`) —
so it never lowers to an unsound mutable `Array.set` (0838). A
`bytearray` is MUTABLE and is NOT rejected: its element write is a
genuine, sound `array` mutation (a mutable byte buffer must be a
`bytearray` or a `list`).

**Range invariant for an unknown PARAMETER — §T.15.8.** The byte-
RANGE part of this faithfulness (`0<=b[i]<256`) is now available for
an *unknown* `bytes`/`bytearray` PARAMETER too (not just a literal),
via an implicit precondition — see §T.15.8. Only the EXACT byte
value of an unknown parameter remains opaque (user `requires` only).

### §T.15.8  Byte-RANGE invariant for an unknown `bytes`/`bytearray` PARAMETER (WL-06c)

For a `bytes` LITERAL the range `0<=b[i]<256` is DERIVABLE from the
concrete construction (§T.15.7). For an UNKNOWN `bytes`/`bytearray`
PARAMETER the coarse model is an arbitrary `array int`, so the range
is NOT known to the solver — yet it is TRUE of every real Python
`bytes`/`bytearray` object (a byte cannot hold a value outside
[0,256); an out-of-range byte cannot be constructed). This is a
TYPE-LEVEL guarantee, so PyCSL EMITS it as an IMPLICIT precondition
on each `bytes`/`bytearray` parameter `b`:

`requires { forall i. 0 <= i < Array.length b -> 0 <= b[i] < 256 }`

emitted by `functions._bytes_param_range_requires` immediately before
the user contract. Consequently a byte read of an UNKNOWN parameter is
provably in range WITHOUT the user writing the bound (`ensures
0<=\result<256` PROVES; corpus lock 0862). The emission is:

- **STRICTLY gated** on the symbol-table type being `bytes`/`bytearray`
  — a `List[int]`/`array int` parameter carries NO [0,256) bound and
  is NEVER given the invariant (soundness: an arbitrary int list is
  not byte-ranged).
- **ADDITIVE and SOUND.** It adds ONLY the range bound: a false
  SPECIFIC-value claim (`\result == 97` for an arbitrary parameter)
  stays UNPROVEN — the range does not pin a value (corpus lock 0863;
  false-twin driver `wl06c_bytes_param_specific_falsetwin.py`). The
  distinct-index/coherence guards (0594/0825) still fail. No verified
  corpus caller passes a `bytes` argument (all bytes-parameter
  functions are leaves), so no call-site discharge obligation is
  created — every non-bytes-parameter function is byte-identical.
- **NO new axiom, NO `\trusted`.** The invariant is a native
  first-order `requires` discharged by the SMT backend (spike
  `wl06c_bytes_param_range_spike.mlw`, Valid on Alt-Ergo AND Z3).

**User `requires` still bounds the exact value.** The invariant does
NOT reveal the byte content, so a user `#@ requires b[0] == 65` is
still what makes `\result == 65` prove (corpus lock 0864) — the
escape hatch for the opaque content is unchanged.

**Write posture.** The invariant is an ENTRY precondition, and it is
never violated in-body because no `bytes`/`bytearray` PARAMETER
element write is emitted: a `bytes` write is rejected as immutable
(§T.15.7), and a `bytearray` PARAMETER element write is rejected as a
caller-visibility/frame boundary (the SAME boundary for which
dict/set/record parameter mutation is rejected, §T.2 / WL-05 —
driver `wl06c_bytearray_param_write_REJECTED.py`, verdict REJECTED).
**ROUTE #64 (relaunch #55) — THE OBLIGATION WAS ALREADY NEEDED, FOR LOCALS.** Everything
above is correct about PARAMETERS, and that is exactly what made the gap hard to see: the
entry invariant really is never violated in-body, because a parameter element write really
is rejected. But a LOCAL `bytearray` element write IS emitted and IS faithful — measured,
`b = bytearray([1,2]); b[0] = 9; return b[0]` proves `9`, CPython's answer — and it carried
NO `ValueError` obligation at all. So `#@ no_exception \all`, the strongest form of a
POSITIVE claim that the body raises nothing, PROVED for `b = bytearray([1]); b[0] = 999`,
which CPython refuses to run (`ValueError: byte must be in range(0, 256)`). The mechanism was
never broken — `a // 0` under `no_exception ZeroDivisionError` correctly fails to prove — the
trigger ROW was simply absent. `exception_model.TRIGGERS` now carries
`("subscript", "write_bytes")` requiring `0 <= v < 256`, selected by the emitter when the
receiver is known to be `bytes`/`bytearray`; the condition is INLINE rather than a new
`PREDICATE_LIBRARY` entry, because that library is emitted wholesale into the preamble of
every unit declaring `no_exception`. An IN-RANGE store still discharges (control `1150`), so
this is a real obligation and not a refusal; negative witness `1149`.

A future faithful caller-visible `bytearray` mutation model would
additionally carry a Python-`ValueError` write obligation `0<=v<256`
(writing 300 into a byte buffer raises `ValueError`).

**Remaining follow-on (§T.15.5, §T.15.9).** `str↔bytes` encode/decode
(beyond the ASCII-literal `.encode()` of §T.15.9), the
`.ljust`/`.split`/`.strip` byte-methods, `.hex`/`int.from_bytes`/
`int.to_bytes`/bytes `+`, and full `struct` beyond the cleared-pack
round-trip stay out of scope — and the EXACT CONTENT of an unknown
`bytes` PARAMETER (its individual byte values) remains opaque (only a
user-supplied `requires`/element bound can constrain it; the RANGE is
now implicit).

### §T.15.9  str-LITERAL `.encode()` content + constructor `ValueError` precondition (WL-06d)

Two additive, independently-gated refinements (`wrong-lowering-to-fix.md`
§WL-06d, spike `wl06d_str_encode_literal_spike.mlw`, Valid on Alt-Ergo
AND Z3):

**(P1-literal) ASCII str-LITERAL `.encode()` byte content.** A pure-ASCII
string LITERAL `"abc".encode()` constant-folds to the `array int` byte
literal of its code points — EXACTLY like a `bytes` literal (§T.15.7):

`T_e("abc".encode()) = (let _a = Array.make 3 97 in _a[1] <- 98; _a[2] <- 99; _a)`

so `"abc".encode()[0] == 97` PROVES, the byte-RANGE invariant
`0 <= b[i] < 256` is derivable (no axiom), and a FALSE content claim
(`"abc".encode()[0] == 98`) stays UNPROVEN (locks 0865/0866). This is
`expressions._encode_string_literal`, fired ONLY when: the method tail is
`encode`; the receiver is a STRING LITERAL; at most one positional arg,
and if present a string literal naming an ASCII-agreeing encoding
(`ascii`/`utf-8`/`latin-1`/…); and EVERY code point is ASCII (`ord < 128`)
— under which ascii, utf-8 and latin-1 all emit `byte == ord`. A
non-literal receiver, a non-ASCII code point (utf-8 is multi-byte / ascii
raises), an unmodelled encoding, or an empty string DECLINES to the sound
opaque `encode_N : array int` val (no over-claim). `.decode` (beyond the
cited null-terminated-field NAME-decode idiom) stays opaque.

**(P3) `bytes([...])`/`bytearray([...])` `ValueError`-as-precondition.**
Python `bytes([v])`/`bytearray([v])` raises `ValueError: bytes must be in
range(0, 256)` if ANY source element is outside `[0,256)`. The constructor
`bytes_new`/`bytearray_new` (whose ensures preserve length + per-element
content `result[i] == x[i]`) now carries the PRECONDITION:

`requires { forall i:int. 0 <= i < Array.length x -> 0 <= x[i] < 256 }`

modelled the SAME way an IndexError bounds VC guards `b[i]` (§T.15.6): an
out-of-range element makes the range VC undischargeable, so
`bytes([300])[0] == 300` FAILS CLOSED (locks 0867/0868) instead of proving
a false normal-return — a severity-1 unsoundness BEFORE WL-06d. The content
law for an in-range source (`bytes([65,66,67])[0] == 65`) is unchanged and
still PROVES; the range precondition is discharged by every real
byte-packing caller (`bytes([v // 256, v % 256])` under a `0 <= v <= 65535`
requires, etc.), so the fix is fully additive (the corpus files that
construct bytes gain only the one `requires` line, all still prove).

**Boundary map (audited: none of these is unsound — each is fail-closed
or opaque).**

| surface | current stance | reason |
|---|---|---|
| `"lit".encode()` ASCII | FAITHFUL content (P1-literal) | §T.15.9 fold |
| `s.encode()` (var / non-ASCII) | opaque `encode_N` | code-point content unknown; utf-8 multi-byte |
| `b.decode()` | opaque (cited field-decode idiom aside) | inverse of an opaque model |
| `bytes([...])` content + range | FAITHFUL + `ValueError` precondition (P3) | §T.15.9 |
| EXACT value of unknown `bytes` param | opaque (RANGE implicit, WL-06c) | user `requires` only |
| `struct.pack`/`unpack` whitelisted scalar / `4s` | FAITHFUL, cited Rocq+Lean round-trip | `Pycsl.Struct.Std` (struct_format.py) |
| `struct` non-whitelisted shape | opaque `struct_{pack,unpack}_N` | no cited round-trip proof (extend = new proof) |
| `b.hex()`, `int.from_bytes`, `int.to_bytes`, `b + b2` | fail-closed TYPEERR / opaque | no faithful byte model emitted |
| `b[i:j]` slice | opaque `array_slice` (content-blind) | no length/content law on the slice |

Extending any opaque row to FAITHFUL requires either format-string-aware
emission with a cited Rocq+Lean round-trip lemma (never `\trusted`) or a
faithful `string`↔`array int` codec model — out of scope of the
wrong-lowering campaign.

---

## §T.16  IR-node ADT recognizer (the `emit_ir` variant — tier3-p1 expr family)

An emitter-shaped function whose parameter (or local) is typed as an IR node
(`node: ExprIR` / `StmtIR` / `IRNode` / `ContractExprIR`) lowers that value to
the **pure algebraic sum `emit_ir`**, so the reflection the emitter performs on
its own IR — `ir.get("type")` (discriminant), `ir.get(field)` (projection), and
structural recursion into sub-nodes — self-verifies. This realizes, in the live
emitter, the Phase-0 WhyML feasibility spike
(`test-suite/corpus/conformance/spikes/tier3_ir_node_adt_spike.mlw`) whose five
laws discharge on Alt-Ergo AND Z3 with no axiom
(`triage-ranked-tcb-tier3.md` T3.1.1/T3.1.2/T3.1.4).

**Gate (`Module6_WhyMLTranspiler.transpile`).** The `emit_ir` theory is emitted
iff some function's `symbol_table` carries an IR-node base name
(`_uses_ir_node_param`) OR the module has a `@mutable_state` class. A program
with neither — every corpus program — emits **byte-identically** (the 743
non-ADT reference `.mlw` are unchanged; only the 11 pre-existing emit_ir tests
gain the additive declarations below).

| Python (emitter-shaped) | WhyML lowering | mechanism |
|---|---|---|
| `node: ExprIR` param/local | `(node: emit_ir)` | `functions.py::_param_type_str` — the IR-node ADT is in scope (`preamble.py::_emit_exprir_theory`). |
| `node.get("type") == "BinOp"` | `(is_binop node)` | **T3.1.2 / spike LAW 1** — a match-based constructor DISCRIMINANT, NOT `str_eq_op (kind_of node) "BinOp"`. The two agree on every real IR node (Module 5 never emits an `IrOther` whose kind is a registry tag — the commit-d2479fe9 fail-closed boundary), but `is_binop` excludes the `IrOther "BinOp"` catch-all, which is what makes the size-decrease law hold. Gated on NOT `@mutable_state` (the self-annotate mirror keeps its already-proven `kind_of` path; Phase 2 adopts `is_K`). `expressions.py::_emit_ir_kind_discriminant`. |
| `node.get("op")` | `(op_of node)` : `string` | **spike LAW 2** — the operator STRING leaf. |
| `node.get("left")` / `.get("right")` | `(left_of node)` / `(right_of node)` : `emit_ir` | **spike LAW 2** — the SUB-NODES. Contrast a leaf projection (`op_of` → `string`) with a sub-node projection (`left_of` → `emit_ir`), mirroring the `FieldGet.object` (LEAF string) vs `Attribute.object` (SUB-node) asymmetry the spike pins. |
| a recursive function over the `emit_ir` param (`def f(node): … f(node.get("left")) …`) | function-level `variant { size node }` injected | **T3.1.4 / spike LAW 3** — the emitter injects the subtree-size measure (`functions.py::_emit_function`). `size` is a structural `let rec function` (`ensures { result >= 1 }`, `variant { e }`); the guarded lemmas `size_left_dec`/`size_right_dec` (`is_binop e → size (left_of e) < size e`, PROVEN no axiom) discharge each recursive call's decrease, and `size e ≥ 1` gives the int well-foundedness lower bound. This is the termination piece tier-1's `ir_scanner` lacked. |
| unrecognized node kind / `Opaque` | fail-closed | an unknown reflection key keeps the opaque `val` (no faithful lowering fabricated). |

The additive theory declarations (`preamble.py::_emit_exprir_theory`):
`type ir_num = INum int | IReal real` (the faithful numeric-leaf carrier, risk 7
/ no-more-int), the `IrBinOp op left right` constructor, `is_binop`, `op_of`,
`left_of`, `right_of`, the `size` measure, and the two size-decrease lemmas.

**Certificate coupling.** Phase 0's Rocq/Lean certificate (record-valued state)
established the soundness of this construct; this increment's WhyML emission is
certificate-backed by the Phase-0 spike and awaits the Phase-3 mechanized-proof
integration (co-lands per `triage-ranked-tcb-tier3.md`).

Reference locks: 0878 (POSITIVE — `node_size`/`binop_operator` prove the
discriminant + projections + terminating recursion), 0879 (NEGATIVE twin — a
false size/discriminant claim stays UNPROVEN). No new axiom, no `\trusted`
increase.

**Increment 3 — the REST of the fixed-arity EXPR family.** The BinOp recognizer
above is extended to `Var`/`Number`/`String`/`Subscript`/`Attribute`/`Call`/
`MkTuple`/`FieldGet` (registered in `expressions.py::_KIND_DISCRIMINANT`), each
lowering `node.get("type") == "K"` to a real match-based `(is_K node)`:

| Python (emitter-shaped) | WhyML lowering | mechanism |
|---|---|---|
| `node.get("type") == "Subscript"` / `.get("value")` / `.get("index")` | `(is_sub node)` / `(svalue_of node)` / `(sindex_of node)` | discriminant + SUB-node projections; recursion terminates via `size_svalue_dec`/`size_sindex_dec`. |
| `node.get("type") == "Attribute"` / `.get("object")` / `.get("attr")` | `(is_attribute node)` / `(object_of node)` : `emit_ir` / `(name_of node)` : `string` | `object_of` is a SUB-node (recurses; `size_object_dec`); `attr` a leaf. |
| `node.get("type") == "Call"` / `.get("func")` | `(is_call node)` / `(func_of node)` : `string` | discriminant + string leaf; `arg0_of` decreases via `size_arg0_dec`. |
| `node.get("type") == "MkTuple"` / `.get("elts")[0..1]` | `(is_tuple node)` / `(elt0_of node)` / `(elt1_of node)` | fixed-arity tuple; `size_elt0_dec`/`size_elt1_dec`. |
| `node.get("type") == "Var" / "Number" / "String" / "FieldGet"` | `(is_var node)` / `(is_num node)` / `(is_str node)` / `(is_fieldget node)` | LEAF discriminants (no sub-node). `FieldGet` is the NEW `IrFieldGet string string` ctor — `fgobject_of`/`field_of` are BOTH string leaves (§5e: FieldGet.object is a LEAF, unlike Attribute.object). |

The soundness invariant is `is_K ↔ kind_of e = "K"` on every real node, so `Tuple`
is intentionally ABSENT (its `kind_of` is `"MkTuple"`); the list-shaped kinds
`ArrayLit`/`SetLit`/`Tuple`/`DictLit` are DEFERRED (a faithful `elts` projection
needs a structural `list emit_ir` + mutual `size_list`, reworking the opaque
`args_of : array emit_ir` — a genuinely new shape, not the additive BinOp move).
Reference locks 0880 (POSITIVE — `expr_size` proves `\result >= 1` recursing
Subscript/Attribute/BinOp + the 4 leaf discriminants) / 0881 (NEGATIVE twin — a
false `is_sub` claim stays UNPROVEN). Feasibility: 4/4 tried real handler idioms
(`_handle_var_expr`/`_handle_subscript`/`_handle_attribute_expr`/
`_handle_call_expr`) lower via the ADT and prove. Coupling COVERED (no new value
shape). No new axiom, no `\trusted` increase.

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

