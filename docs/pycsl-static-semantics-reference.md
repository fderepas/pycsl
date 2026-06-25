# PyCSL Static Semantics Reference

**Status:** Normative  
**Version:** 1.3  
**Source of truth:** This document specifies the well-formedness rules that
determine which syntactically valid PyCSL annotations are accepted or
rejected. It is derived from the implemented checks in
`Module3_Weaver.py` and `Module4_SemanticAnalyzer.py`, cross-referenced
against `test-suite/annotations.md` (paragraph numbering preserved).

**Scope:** This document defines the judgement Γ ⊢ A : ok ("annotation A
is well-formed in context Γ"). It does NOT define the concrete syntax
(see `pycsl-concrete-syntax-reference.md`) or the translation to WhyML
(see `pycsl-translational-reference.md`).

**Companion documents:**
- `pycsl-concrete-syntax-reference.md` — what strings are syntactically valid
- `pycsl-translational-reference.md` — what the annotations mean (via WhyML)

---

## Table of Contents

1. [Context Construction](#1-context-construction)
2. [Directive Well-Formedness](#2-directive-well-formedness)
3. [Expression Well-Formedness](#3-expression-well-formedness)
4. [Unsupported Constructs](#4-unsupported-constructs)
5. [Memory Model Constraints](#5-memory-model-constraints)
6. [Class Contract Well-Formedness](#6-class-contract-well-formedness)
7. [Temporal Expressions: \\old and \\at](#7-temporal-expressions-old-and-at)
8. [Weaving Constraints](#8-weaving-constraints)
9. [Error Catalogue](#9-error-catalogue)
10. [Gap Analysis](#10-gap-analysis)
11. [Annotation Well-Formedness (S7 Transcription — TY0)](#11-annotation-well-formedness-s7-transcription--ty0)

---

## 1. Context Construction

_Prerequisite for all subsequent sections._

The static semantics are defined relative to a **context** (symbol table)
Γ that maps variable names to type names. There are three kinds of context:

### 1.1 Function Scope (Γ_f)

_Implemented in `Module4_SemanticAnalyzer._build_function_scope`._

When entering a `def` node, the function scope is constructed as:

```
Γ_f = Γ_args ∪ Γ_locals ∪ Γ_ghost
```

#### 1.1.1 Arguments (Γ_args)

For each argument `arg` in `node.args.args`:

```
            ⎧ τ(annotation)   if arg.annotation is present
Γ_args(arg) = ⎨
            ⎩ Any             otherwise
```

The special argument `self` is **excluded** from the scope (field access
uses the class scope Γ_c instead).

#### 1.1.2 Local Variables (Γ_locals)

The function body is walked (via `ast.walk`) for:

1. **`ast.Assign`**: For each `ast.Name` target `x`, add `x : Any`.
2. **`ast.AnnAssign`**: For target `x: T`, add `x : τ(T)`.
3. **`ast.For`**: the loop target is added as `Any` — a bare `Name` target `x`, or each
   `Name` element of a tuple target `for x, y in …` (so loop variables are in scope for the
   loop's `#@ loop invariant` clauses). (`Module4_SemanticAnalyzer._build_function_scope`.)

Variables that match a module-level `shared` declaration are **excluded**
from local scope (they are handled by the concurrency checker).

#### 1.1.3 Ghost Variables (Γ_ghost)

For each `#@ ghost x = expr` encountered (via `csl_ghost_assigns`
attributes on AST nodes), add `x : int`.

Ghost variables may appear in `requires`, `ensures`, `loop invariant`,
and `\variant` expressions.

### 1.2 Class Scope (Γ_c)

_Implemented in `Module4_SemanticAnalyzer._collect_class_field_types`._

When entering a `class` node, the class field table is constructed by
scanning the `__init__` method body:

1. **`ast.Assign`**: For each target `self.field = expr`, add
   `field : Any`.
2. **`ast.AnnAssign`**: For each target `self.field: T = expr`, add
   `field : τ(T)`.

Fields collected into Γ_c are available:
- In `#@ class invariant` expressions (§2.3)
- In method scopes (via `self.field` syntax in §3.1.3)

After all methods in the class are visited, Γ_c is reset to empty.

### 1.3 Module Scope (Γ_m)

_Implemented in `Module4_SemanticAnalyzer.visit_Module`._

When entering a `Module` node, the module-level concurrency state is
collected:

| Attribute | Source | Structure |
|-----------|--------|-----------|
| `_shared_vars` | `#@ shared` declarations | `Dict[str, Optional[str]]` — var_name → mutex (or `None` for unprotected) |
| `_mutex_invariants` | `#@ mutex_invariant` declarations | `Dict[str, CSLNode]` — mutex_name → invariant expression |
| `_lock_order` | `#@ lock_order` declaration | `Optional[List[str]]` — ordered list of mutex names |
| `_module_constants` | top-level `NAME = <int literal>` | `Dict[str, int]` — single-assignment module int constants |

**Module-level constants in contracts.** A module-level name bound **exactly once** to an
integer literal (`K_IHDR = 0`, `LIMIT = 8`; `collect_module_constants`) is a *constant*: it is
admitted in `requires`/`ensures`/loop invariants and **resolved to its literal** in both body and
spec emission (`expressions.py::_handle_var_expr`), exactly like a class-body constant
(`self.CAP` → `(64)`, §1.2). So `#@ ensures kinds[0] == K_IHDR` discharges with `K_IHDR ↦ 0`.

A module-level name that is **reassigned** (more than one module-level binding, or written via a
`global` statement) is **mutable global state** and is *excluded* — it is neither inlined nor
admitted in contracts, and a reference raises `Undefined variable`. This is by design: a value
that varies across calls and is not a parameter, field, or ghost has no well-defined meaning in
the per-function frame model (the same reason `#@ shared` concurrency globals are excluded from
contract scope). The sound way to reason about a mutable global is a `#@ ghost` mirror, not a
direct reference. Drivers: `0506` (constant proves), `0507` (false bound fails), `0508` (mutable
global rejected); `0290`/`0291` (the original `K_IHDR`/`BASE` failures, now admitted).

### 1.4 Type Mapping Function τ

The type mapping function converts Python type annotations to the
specification logic's type universe:

```
τ(int)            = int
τ(bool)           = int       (* FAITHFUL int-encoding (verified 2026-06): a bool value is
                                 Why3 `int` valued 0/1 — a `-> bool` function emits `: int` with
                                 `exception Return int`, bool params/locals are `int`, and a
                                 contract reads `\result == 0 or \result == 1`. Bool literals
                                 lower to 1/0 (so `\result == True` becomes `result = 1`);
                                 bool-producing expressions (compare / and-or-not / isinstance)
                                 coerce to `(if X then 1 else 0)` at value boundaries, while pure
                                 guard and spec contexts emit native WhyML boolean formulas,
                                 bridged to the encoding by `= 1`. Unlike the retired τ(float)=int
                                 (lossy → unsound, now `real`), 0/1 is a *lossless* injection of a
                                 genuinely 2-valued type, so it is deliberately RETAINED under
                                 no-more-int. *)
τ(str)            = string    (* real Why3 string.String — runtime str values carry content.
                                 A str parameter/local/return is a `string`; literals are
                                 `"..."`; len / + / [i] / [a:b] / == lower to String.length /
                                 concat / substring / structural = (see translational §T.6).
                                 Unifies the old dual model: the \str_length / \str_sub / ^
                                 operators now apply to runtime str, not only ghost strings.
                                 NB no char type: s[i] is a length-1 string, so no ord / code
                                 points / lexicographic char ordering — see the limitations *)
τ(float)          = real      (* Why3 real.RealInfix — was the unsound τ(float)=int. Float
                                 literals are real constants; +/-/*//​ and </<=/>/>= lower to the
                                 RealInfix `+.`/`-.`/`*.`/`/.`/`<.`… (arithmetic in a body bridges
                                 through `val float_*_op : real`). Mixed float/int arithmetic is
                                 out of scope; transcendentals stay opaque ops over real *)
τ(list)           = list
τ(List)           = list      (* typing.List alias *)
τ(List[T])        = list      (* parametric list — element type opaque *)
                              (* 07-1705-rev4: representation is selected by the seq-promotion
                                 analysis. A list that is GROWN (`+=` / `+` concat) lowers to a
                                 growable `seq int` (immutable, region-free ref); all other lists
                                 stay `array int`. The mark propagates across `b = a`; a list that
                                 must be BOTH grown and 2-D is a representation conflict, rejected
                                 (no silent mis-model). Translational §T.2 list rows. *)
τ(bytes)          = int †     (* byte buffer *)
τ(bytearray)      = int †     (* mutable byte buffer *)
τ(dict)           = dict
τ(Dict[K, V])     = dict      (* parametric dict — key/value types opaque *)
τ(set)            = dict      (* sets share the dict model; see translational §T.14.2 *)
τ(Set[T])         = dict
τ(frozenset)      = dict      (* frozensets share the set/dict model *)
τ(FrozenSet[T])   = dict
τ(Tuple[T1, ...]) = tuple
τ(tuple)          = int †     (* bare tuple — unlike the recognized Tuple[T1, ...] above *)
τ(C)              = record    (* user-defined class C → a WhyML record of its fields, for
                                 `self`, locally-constructed instances, AND a bare C-typed
                                 parameter whose class is registered — read-only field access
                                 `p.field`; mutation of a record parameter is out of scope (‡).
                                 A `#@ mixin` C with shared/owned fields is the same `record`;
                                 a `#@ compose_from` class flattens its mixins' provided methods +
                                 fields into this record (§2.6, Tier 1) *)
τ(D)              = variant   (* a `#@ datatype D = Red | Some(int) | Pair(int,int)` declares a
                                 REAL Why3 algebraic type `type d = Red | Some int | Pair int int`
                                 (payloads int/bool→int, str→string, float→real). Constructors
                                 lower to nullary/applied ctors (`Red`, `(Some 7)`); `match`/`case`
                                 lowers to a Why3 `match … with | Ctor caps -> … end` with
                                 solver-checked exhaustiveness. Recursive (single + mutual-SCC),
                                 parametric (`Option[T]`), guarded/nested/or-patterns, and
                                 captures-in-contracts (`\is_ctor`/`\payload`) are all SUPPORTED
                                 (§ datatype note); only in-place variant-field mutation and
                                 use-site type-param `\payload` remain out of scope *)
τ(Optional[T])    = τ(T)      (* None maps to 0; the optional-ness adds no type info *)
τ(Union[T, None]) = τ(T)      (* equivalent to Optional[T] *)
τ(Union[T1, T2])  = τ(T1)     (* heuristic: first non-None component *)
τ(_)              = Any       (* all other types, including no annotation *)
```

**Where the collapse happens.** The τ universe is *not* materialized as a single function in
Module5. Module4's `_get_type_name` stores the **raw** type tag in the symbol table (bare names
verbatim — `str`, `bytes`, `MyClass`; subscript heads lowercased), and `_build_function_ir` only
separately computes the lowercased *return* head (a `str` return stays `"str"`, not `int`). The
collapse to the WhyML universe (`int` / `array int` / `map int (option int)`) happens **at
emission** in `module6_whyml/functions.py` (`_param_type_str`, `_symtype_to_whyml`,
`_return_type`). So a reader inspecting `_build_function_ir` will *not* find `str`/`float`/`bytes`
mapped to `int` there — that is the emitter's doing. τ above describes the net result.

**† Context-dependent (parameter vs field).** The τ above gives the *parameter / return*
realization (`_param_type_str`/`_return_type`), where `bytes` / `bytearray` / bare `tuple`
coarsen to `int`. As an instance **field** the realization differs: `_field_type_from_annotation`
maps
these (and `list`/`Tuple[...]`) to `list` → `array int` in the WhyML record, because a byte
buffer / tuple field is array-backed (e.g. the `self.disk: bytearray` virtual disk). So the
same annotation can be `int` as a parameter but `array int` as a field.

**‡ Classes / records.** A class introduces a record type in `Γ_c` (§1.2): `self`, the
result of a constructor call `C()`, **and** a bare `C`-typed *parameter* whose class is registered
in `_record_types` are all typed as the class's WhyML record (field defaults per `τ`). A record
parameter gives **read-only** field access — `p.field` is a direct record read in both body and
contract (`functions.py::_param_type_str` + the method loop; the old coarsen-to-`int` +
opaque `getattr_<cls>` path is gone for record params). **Out of scope:** *mutating* a record
parameter (Why3 records are by-value, so a write does not flow back to the caller — needs the
frame/`writes` machinery). A **method call** on a record param (`p.m(args)`) now resolves the
callee contract exactly like a record local (no-more-int-3 A2a): `statements.py::_emit_body_code`
unions the param→record map into `_current_record_var_classes`, so result-only and
param-referencing `ensures` propagate to the call site. A *field-referencing* callee ensure
(`\result == self.x`) still does not propagate — a pre-existing method-call gap that fails for
record locals too, tracked as A2c. A class with no registered record (e.g. an unresolved import)
still coarsens to `int`.

**§ Sum types / `#@ datatype`.** A module-level `#@ datatype` directive declares a real Why3
algebraic type emitted by `preamble.py::_emit_type_decls` (the `kind:"variant"` branch, beside the
`record` branch). Constructors are registered (`Module5` constructors registry) and lowered as
nullary names or applied calls; a `match`/`case` over a variant value lowers to a Why3 `match …
with … end` (`statements.py::_handle_match_stmt`), so **exhaustiveness is solver-checked** (a
missing or extra constructor is a hard error). A variant local `o = Some(7)` binds
`let o = ref (Some 7) in` with the inferred variant type (not a coarsened `int`). **Now supported
(no-more-int Part 5–7):** recursive datatypes — single (`Tree = Leaf | Node(int, Tree, Tree)`) and
mutual-SCC (emitted as `type a = … with b = …`); parametric datatypes (`Option[T]`, instantiated
per use by construction `Just(7)`); guarded / nested / or-patterns in `match`; and
captures-referenced-at-the-contract-level via the `\is_ctor(x, Ctor)` discriminator and
`\payload(x, Ctor[, i])` projector (so a contract can name a `match` capture *without* a `match` —
concrete-syntax §3.1.27–29, translational §T.6.5). **Still out of scope:** in-place mutation of a
variant field (value semantics — rebuild instead), and `\payload` over a *type-parameter* payload
at a use-site annotation `o: Option[int]` (follow-on, no-more-int Part 8 A8-1). See `pycsl-annotate`
SKILL §3f for the surface and limitations.

**§ Inductive predicates / `#@ inductive`.** A module-level `#@ inductive p(params):` header plus its
4-space-indented `<name>: <horn-clause>` rule lines (no `rule` keyword — the indentation block folds
them in at Module 1, and Module 2 parses them into `InductiveDecl.rules` inline) declare a
**least-fixpoint relation** (hoisted to `csl_inductives`; Module 5 → `inductive_decls`
IR; `preamble.py::_emit_inductive_decls` emits `inductive p t1 … = | Rule : clause …` after the type
declarations and before functions/axioms — a single predicate takes **no** closing `end`). Each rule
body is an ordinary contract expression, so `\forall m: int; even(m) ==> even(m + 2)` reuses the
typed-quantifier/implication/predicate-application grammar; a predicate application `p(args)` lowers to
`(p args)` (registered in `_inductive_preds`, never an abstract op). A predicate is **logic-only**:
usable in contracts and lemmas, never in executable position. **Well-formedness:** each rule's
conclusion must apply the predicate being defined, and the predicate must occur only **strictly
positively** in premises — **enforced by Why3** at verification (`non strictly positive occurrence`),
so a non-positive definition cannot verify. **Mutually-inductive `with` groups (P2)** join multiple
predicates into one `inductive p … with q …` (positivity checked group-wide; corpus `0574`/`0575`), and
the **relational form** (non-structural multi-arg predicates) uses the same machinery (`0572`).
A **universally-quantified consequence** `\forall x; p(x) ==> Q` (a `#@ lemma`) is discharged by
induction on the derivation: PyCSL drives Why3's `induction_pr` transformation (after `split_vc`) for
any inductive-declaring module (`0581`). Still a follow-on: a *Module-4 pre-check* for positivity /
conclusion-shape / arity / executable-position. Cross-references: `annotations.md` §2.8, translational
§T.4.7; corpus `0562`/`0563`/`0572`/`0574`/`0575`/`0581`.

**§ Collections (`collections` module).** A handful of `collections` constructors are recognized
**by bare name** (import-independent) and routed to an existing modeled universe member rather than
an opaque `int` stub — so a local built from them carries real content:

| Constructor | τ realization | Model |
|---|---|---|
| `defaultdict(int)`, `Counter()`, `OrderedDict()` | `dict` | `map int (option int)`; a missing key reads `0` (which *is* `defaultdict(int)` / `Counter` semantics) |
| `deque()` | `list` → `array int` | right-end `append` / `dq[i]` / `len` carry content (the growable-list model) |
| `namedtuple('P', [f…])` | `record` | a synthesized WhyML record of the (literal) fields (Tier-A record construction) |

**Out of scope (sound under-approximations / opaque):** `defaultdict(list/set)` and other non-`int`
factories (the missing-key default is hard-wired `0`); deque left-end / `pop` (`appendleft` /
`popleft` / `pop` are unmodeled — only right-end append/index/len); insertion order for
`OrderedDict`; `Counter.most_common` / ranking; `ChainMap` / `UserDict` / `UserList` (opaque int
handles); a `deque`/`Counter` built from an iterable is modeled as **empty** (a sound
under-approximation — never proves a false content claim). See `pycsl-stdlib-coverage` SKILL for the
per-member tier table.

The `float` / `bytes` / `bytearray` / `frozenset` / bare-`tuple` / class / datatype rows were
previously absorbed by the `τ(_) = Any` catch-all; they are listed explicitly here because they
are *modeled* (mapped to a concrete universe member), not treated as opaque `Any`.

**String model (τ(str) = string).** Runtime `str` is the Why3 `string.String` value type — the
same model the ghost-string layer (`#@ ghost s : string`) already used, now unified so the dual
int-hash/real-string split is gone. Because Python strings are immutable values and Why3
`string` is a value type (no heap, no aliasing), `str` handling is identical across all memory
models (hoare/concurrent/typed/store) — one code path, not four. The emitter
(`functions.py::_param_type_str` and the method-parameter loop) types a `str` parameter as
`string`; `Module6_whyml/expressions.py` lowers the operations through abstract `val …_op`
bridges (`str_length_op`, `str_concat_op`, `str_eq_op`, `str_sub_op`, `str_contains_op`,
`str_startswith_op` / `str_endswith_op` / `str_find_op`), each tying its result to the
corresponding `String.*` logic symbol via an `ensures` (the logic symbols cannot appear in a
program/value context directly). **Limitations:** no character/code-point type (`s[i]` is the
length-1 substring `String.substring s i 1`), so `ord`, character ordering, and codepoint-level
parsing stay out of reach; string→string transforms (`upper`/`lower`/`strip`/`replace`) and
`split` remain opaque abstract ops; `bytes`↔`str` codecs (`.decode`/`.encode`) stay opaque
(decode is an opaque `int`, the bytes↔str boundary). `str`-keyed dicts still key on the int
hash (the dict model is `map int (option int)`).

The type universe is intentionally coarse: PyCSL does not perform
full type inference. The type mapping is used only for:
- Determining whether `\valid` / `\separated` bases are list-typed
- Determining whether subscript assignment targets are list-typed
- Determining whether `assigns` region bases are list-typed
- Selecting the WhyML return type in `module6_whyml/functions.py`'s
  `_emit_function` (`τ(...) = list` flips the return type from `int` to
  `array int`).

---

## 2. Directive Well-Formedness

_Corresponds to `annotations.md` §2._

### 2.1 Function/Method Contracts

_Corresponds to `annotations.md` §2.1._

#### §2.1.15 Guarded cases (`act` / `given` / `complete` / `disjoint`)

```
   act b: every `#@ given e` and `#@ ensures e` is well-formed in Γ_f
   \result ∉ FV(e) for every `#@ given e`        names(complete/disjoint) ⊆ acts
   ───────────────────────────────────────────────────────────────────────────
                       act/complete/disjoint well-formed in Γ_f
```

**Rule:** Each clause inside `#@ act b:` is well-formed under the same Γ_f as a
top-level clause. `\result` may **not** appear in a `#@ given` guard (it is a
pre-state predicate). Every name listed by `#@ complete …` / `#@ disjoint …`
must resolve to an `act` defined on the same function; duplicate act names are
rejected. (Enforced by `Module4._validate_acts`.)

#### §2.4.7 Statement checkpoints (`#@ assert` / `#@ check`)

```
   \result ∉ FV(e)
   ─────────────────────────────────────────
        `#@ assert e` / `#@ check e` ok
```

**Rule:** the **only** static check is that `\result` does not occur (a checkpoint is a
mid-body obligation, bound before any return). `Module4._validate_checkpoints` does **not**
perform a scope check on `e` — mid-body local bindings (and thus whether each name is in
scope) are deliberately left to the back-end prover. (So, unlike `requires`/`ensures`, an
unknown identifier in a checkpoint is not a Module4 error.)

#### §2.5 Module-level HAPPY meta-property (`happy` / `\preserves`)

```
   region bounds LO, HI well-formed in Γ_module     names(except) ⊆ methods(module)
   every non-exempt `\trusted`/`\abstract` method m carries `#@ \preserves`
   ─────────────────────────────────────────────────────────────────────────────
                       `#@ happy N: region LO..HI writes self.f outside region …` ok
```

**Rule.** Each `except` name must resolve to a method defined in the module — a name
matching no method is rejected (a typo would silently widen coverage). A HAPPY whose field
is never written warns (the property is inert). Each non-exempt `\trusted`/`\abstract`
method has no checkable body, so it must opt into the trust boundary with `#@ \preserves`
(theorem clause 2); its absence is a hard error. Validation: exempt-name and inert-field
checks in `Module4._validate_happy`; the trust-boundary requirement in
`Module3_Weaver._expand_happy_properties`.

**Rule (`footprint` / parametric & protects forms, 07-1143).** A `#@ footprint <name>(arg)`
must name a parametric HAPPY `<name>` declared in the module (`#@ happy <name>(p): protects
<path>[LO:HI]`); the meta-pass binds `p := arg` and injects a per-site containment check
`LO[p:=arg] <= i and i < HI[p:=arg]` at each write of `<path>[i]` in the declaring method. A
non-exempt method with no `footprint` writing the path, and any non-exempt direct write of a
`protects <paths>` (subsystem-ownership) field, get `#@ check False`. Aliasing a protected base
into a non-exempt local is a hard error (`Module3_Weaver._check_protect_aliasing`).

**Soundness (composition theorem, `meta.md`).** If every body-verified method discharges a
`#@ check φ(ℓ)` at each write site of `self.f` (universal coverage, clause 1) and every other
mutator is exempt or carries the `\preserves` region-preservation `ensures` (clause 2), then
no execution writes the protected region. No alias analysis is needed (the obligation is at
the location written; value-semantic arrays bar local-alias escape) and no caller reasoning
(an indirect write is caught at the callee's own site).

The field-subscript atom `self.f[i]` is well-formed where `self.f` is an instance array field
in scope (Γ_f), with `i : int`; it is the term used in `\preserves` postconditions.

#### §2.1.1 Precondition (`requires`)

```
    Γ_f ⊢ e : ok       \result ∉ FV(e)
   ────────────────────────────────────
    Γ_f ⊢ requires(e) : ok
```

**Rule:** The expression `e` must be well-formed in the function scope.
`\result` must NOT appear in `e` (enforced by `_validate_contract` with
`is_postcondition=False`).

**Error (E1):** `"Invalid use of '\result' in <context>. It is only
allowed in 'ensures'."`

**Error (E2):** `"Undefined variable '<var>' referenced in contract for
<context>. Available variables in scope: [...]"`

#### §2.1.2 Postcondition (`ensures`)

```
    Γ_f ∪ {\result} ⊢ e : ok
   ─────────────────────────
    Γ_f ⊢ ensures(e) : ok
```

**Rule:** The expression `e` must be well-formed in the function scope
**extended with `\result`**. `\result` IS allowed in `e`.

#### §2.1.3 Frame Condition (`assigns`)

```
    ∀ t ∈ targets(A):
      t = \nothing                                    ∨
      t = Var(x)       ∧  x ∈ dom(Γ_f)              ∨
      t = FieldAccess(self, f)  ∧  f ∈ dom(Γ_c)     ∨
      t = AssignsRegion(arr, lo, hi)  ∧
          arr ∈ dom(Γ_f) ∧ τ(Γ_f(arr)) ∈ {list, List, Any}
   ─────────────────────────────────────────────────────────
    Γ_f ⊢ assigns(A) : ok
```

**Rule:** Each assigns target must be:
1. `\nothing` — no mutation allowed.
2. A variable `x` that exists in the function scope.
3. A field `self.field` where `field` exists in the class scope.
4. An array region `arr[lo..hi]` where `arr` is in scope AND is list-typed.

**Error (E3):** `"Assigns region references undefined variable '<arr>'
in <context>."`

**Error (E4):** `"Assigns region on non-list variable '<arr>' (type
'<type>') in <context>."`

#### §2.1.4 Function Variant (`\variant`)

```
    Γ_f ⊢ e : ok       \result ∉ FV(e)
   ─────────────────────────────────────
    Γ_f ⊢ function_variant(e) : ok
```

**Rule:** Same as precondition — expression must be well-formed, `\result`
disallowed.

#### §2.1.5 Structural Variant (`\variant(e, ordering)`)

```
    Γ_f ⊢ e : ok       ordering ∈ CNAME
   ──────────────────────────────────────
    Γ_f ⊢ function_variant_structural(e, ordering) : ok
```

**Rule:** Expression must be well-formed. The ordering name must be a
valid identifier (enforced by the parser; no additional static check).

#### §2.1.6 Diverges (`\diverges`)

```
   ─────────────────────────
    Γ_f ⊢ diverges : ok
```

**Rule:** Always well-formed (no expression to check). Presence is noted
as a flag on the function AST node (`csl_diverges = True`).

**Contradiction check (W1):** If both `\variant` and `\diverges` appear
on the same function, the Weaver raises a `ValueError`:
`"\\variant and \\diverges are contradictory"`.

#### §2.1.6n No inline (`no_inline`)

```
   ─────────────────────────
    Γ_f ⊢ no_inline : ok
```

**Rule:** Always well-formed (no expression to check). Presence is noted as a
flag on the function AST node (`csl_no_inline = True`) and carried into the
function IR (`"no_inline": True`). It marks a method on a module-global instance
as a **modular-verification boundary** (no-inline.md): the IR-inliner leaves its
calls in place (rather than splicing the body), so the body is verified once and
callers reuse its contract. Sound iff the body remains a verified `let` (a false
`ensures` makes the *callee*, not the caller, fail). See translational §T.2.7n.

#### §2.1.6s Sibling concrete (`sibling_concrete`)

```
   ──────────────────────────────
    Γ_f ⊢ sibling_concrete : ok
```

**Rule:** Always well-formed (no expression to check). Presence is a flag on the
function AST node (`csl_sibling_concrete = True`) carried into the function IR
(`"sibling_concrete": True`). It is **opt-in** and affects only how an intra-class
`self.<m>()` call to THIS method is lowered (allocator-frame §2.7): such a call
becomes a CONCRETE call to the verified `let` rather than the default abstract `val`
stub, so the caller obtains the callee's full contract and its type/class-invariant
guarantee on the post-state. Decoupled from `no_inline` (it does not change whether
the body is inlined into wrappers). Sound: a concrete call to a verified `let` is the
method's real semantics — it adds no trust. See translational §T.2.7s.

#### §2.1.6f Propagate frame (`propagate_frame`)

```
   ──────────────────────────────
    Γ_f ⊢ propagate_frame : ok
```

**Rule:** Always well-formed (no expression to check). Presence is a flag on the
function AST node (`csl_propagate_frame = True`) carried into the function IR
(`"propagate_frame": True`). It is **opt-in** and affects only how THIS method's
QUANTIFIED single-cell self-field FRAME `ensures` are carried onto its abstract
boundary `val` (os-roadmap M4). Without it, `#@ assigns self.f` frames the whole field
`self.f` and a caller sees it havoced (only a result-pinned cell survives). With it,
the method's frame clauses of the shape `\forall k. guard -> self.f[k] == \old(self.f[k])`
are emitted onto the boundary `val`, so a caller can prove every *other* cell preserved.
Two frame shapes qualify: param-referencing frames and `\result`-referencing single-cell
frames (`\forall k != \result. self.f[k] == \old(self.f[k])`). Sound: the propagated
`\forall` is the SAME frame the callee's body verifies (a true frame of the body), never
a fabricated or broadened one — it adds no trust. See translational §T.2.7f.

#### §2.1.6g Fresh globals (`fresh_globals`)

```
    kind(f) ≠ method     f ∉ ⋃_g calltargets(body(g))
   ──────────────────────────────────────────────────────
              Γ_f ⊢ fresh_globals : ok
```

**Rule:** Presence is a flag on the function AST node (`csl_fresh_globals = True`)
carried into the function IR (`"fresh_globals": True`). Unlike the always-ok flag
directives, `fresh_globals` carries a **CONFINEMENT side-condition enforced by Module4**
(`core_ir_semantic._check_fresh_globals`): the directive is rejected (error
`PYCSL-SEM-FRESH-GLOBALS`) on (1) a **method** (`kind(f) = method`, a `self`-receiver
function) and (2) any function that is a **callee** — i.e. whose name appears as a call
target in *any* function body in the unit. Both rejections are soundness-critical: the
directive re-establishes each module-global singleton's constructor post-state as an
**assumed** entry fact, which is true only when the function is an independent entry point
running on a freshly-imported global (import ran the constructor). A method runs on an
arbitrary live `self`/shared global, and a callee inherits its caller's possibly-mutated
global — assuming the fresh state in either case would be unsound. The assumed fact is the
constructor's own `#@ ensures` (`self` → the global), which Module6 additionally emits as a
checked `let g_fresh_init () : C ensures {…} = <constructor literal>` proving the post-state
of the freshly constructed global — so the assume is proof-backed, never an arbitrary
literal. See translational §T.2.7g.

#### §2.1.6m Verify module (`verify_module <name>`)

```
   ──────────────────────────────────
    Γ_f ⊢ verify_module <name> : ok
```

**Rule:** Always well-formed (the argument is a `CNAME` group label; no expression to
check). Presence is carried on the function AST node (`csl_verify_module = "<name>"`) into
the function IR (`"verify_module": "<name>"`). It is **opt-in**: a function tagged
`#@ verify_module <name>` is emitted into its own top-level Why3 `module <name>` (rather
than the single flat `module PyCSL_Program`), so that only the `#@ proof` axioms cited by
the functions in that group are in scope for its goals. Functions sharing the same `<name>`
co-reside in one module; shared infrastructure (the concrete record type, `val function`s,
predicates, witness/class-invariant axioms, abstract stubs) is re-declared per module, with
the concrete record type shared through a common base `module` that every emitted module
`use`s (a defined record type cannot be `clone`-substituted). **Soundness:** a cross-module
`self.<m>(...)` call is lowered to the callee's PROVEN contract via Why3 module
`clone`-refinement — the interface `module` declares the contract, and the owning provider
`module` discharges the synthetic refinement VC `<fn>'refn'vc` proving the real `let`
implements that contract — so the boundary is a proven interface, NOT an assumed `val`, a
new `\trusted`, or a new axiom; the net trusted base is unchanged (every function is proved
exactly once, against a contract that is itself proved). The directive only changes WHICH
declarations share the SMT context at each VC (a feasibility lever, not a trust lever) —
resolving the os read+write axiom co-residence (`field_to_str`/`dir_scan_*` vs
`dir_blit_marker*`) that OOMs the directory writers. Why3 `scope` does NOT provide this
isolation (a scope is a namespace; an `axiom` is global within the enclosing module); only
separate top-level `module`s isolate axioms. Default (untagged) → byte-identical emission.
See translational §T.2.7m.

#### §2.1.7 Trusted (`\trusted [reviewer: <REVIEWER_ID>]`)

```
   ────────────────────────────────────────
    Γ_f ⊢ trusted(reviewer?) : ok
```

**Rule:** Always well-formed. Presence is noted as a flag
(`csl_trusted = True`) on the function-def AST node; the optional
`reviewer:` clause is captured separately as `csl_reviewer: str`
(empty string when absent).

**Reviewer field semantics.** The reviewer name is **not** checked
at the static-semantics layer. `Module3_Weaver._dispatch_function_contracts`
emits a warning (not an error) when `csl_trusted = True` but
`csl_reviewer = ""`:

> *"`\trusted` has no reviewer — add `reviewer: <name>` to document
> who is accountable for this trust assumption."*

The reviewer name is therefore an **accountability attribution**:
it documents *who* (a human, a team, or a generator process)
stands behind the assumption that the function's contracts hold of
its body, since PyCSL itself does not verify the body. The tag
value follows the convention in `annotations.md` §2.1.7 ("Reviewer
tag convention"):

- A **human identifier** (`alice`, `charlie-mhe@example.org`) when
  a person reviewed the function and attests.
- A **process identifier** (`pycsl-self-annotate`,
  `auto-trust-rule-array-return`) when an automated tool emitted
  the `\trusted` directive and the trust delegates to that tool's
  documented rules.

An anonymous `\trusted` (no reviewer field) is permitted by the
grammar but flagged by the warning above. Project convention
treats anonymous `\trusted` as a review blocker.

**No new error codes** — the existing `E*` catalogue does not gain
an entry for reviewer-related violations.

_Corresponds to `annotations.md` §2.1.7._

#### §2.1.14 Abstract (`\abstract`)

```
   ────────────────────────────────────────
    Γ_f ⊢ abstract : ok
```

**Rule:** Always well-formed. Presence is noted as a flag
(`csl_abstract = True`) on the function-def AST node
(`Module3_Weaver._dispatch_function_contracts`), read into the IR as
`abstract: True` (`Module5_IREmitter`).

**Distinction from `\trusted`.** Both cause Module 6 to emit a bodyless
`val` (signature + contract, no body). The difference is provenance, and
it is a *policy* distinction, not a typing one:

- `\trusted` asserts a present Python body is correct without checking it
  (trust); `attic/stdlib-coverage-tooling/check-no-trusted-stubs.py` forbids it on library stubs.
- `\abstract` asserts there is no meaningful body — the contract (plus any
  `#@ proof` axioms) *is* the definition. Sound: an uninterpreted `val`
  constrains callers only by its spec. It is **not** counted as `\trusted`
  and emits no reviewer warning.

No new error codes. _Corresponds to `annotations.md` §2.1.14._

#### §2.1.16 Lemma (`lemma`)

```
    f carries #@ lemma     f has ≥1 ensures     ¬ f.diverges
    return(f) = None     assigns(f) = \nothing     no `return <v>` in body
    no call to a \trusted symbol in body
   ─────────────────────────────────────────────────────────────────────
    Γ_f ⊢ lemma : ok
```

**Rule.** Module 4 (`_validate_lemma`) enforces well-formedness + the one soundness
property Why3 can't see:

- **Ghost discipline.** Return type `None` (→ WhyML `unit`), `assigns \nothing`, and no
  `return <value>` in the body (a lemma computes nothing; the body is the proof).
- **`\diverges` forbidden**; at least one `#@ ensures` (the conclusion).
- **No trust-leakage.** A plain `#@ lemma` body may not call a `\trusted` function —
  Why3 cannot catch this (the trusted `val`'s contract is axiomatic), so it would
  smuggle an unverified fact into a checked lemma.

**Termination is Why3's, not Module 4's (decision A).** `#@ \variant` on a recursive
lemma is *optional*: Why3 infers a structural variant and rejects ill-founded recursion
via its termination VC, so a non-terminating "lemma" cannot export `False`. (Requiring
the annotation was redundant *and* over-restrictive — it rejected provable lemmas.)
Likewise the **contract-call-position ban** (a lemma name used as a term in a
`#@ requires`/`#@ ensures`) is left to Why3 — a `let lemma` is not a usable term, so
Why3 rejects it; no PyCSL pre-check.

_Corresponds to `annotations.md` §2.1.16 and translational §T.2.12._

#### §2.1.17 Uses (`uses`)

```
    name ∈ CNAME      name is a function/lemma in scope
   ───────────────────────────────────────────────────
    Γ_f ⊢ uses(name) : ok
```

**Rule.** `#@ uses <lemma>` cites a lemma whose general fact this function relies on but does not
*name* (scc2.md). It is **ordering-only**: Module 3 records it on `csl_uses`, Module 5 carries it as
`uses` on the function IR, and the SCC sort (`scc.py`) adds an edge so the cited lemma is emitted
before this function (its `forall …` fact then in scope to discharge e.g. a universal over a recursive
datatype). It produces **no WhyML** and adds no axiom — soundness is unaffected (it only changes
declaration order; an out-of-scope or misspelled citation surfaces as the underlying proof failing, not
as new trust). _Corresponds to `annotations.md` §2.1.17 and translational §T.2.13._

#### §2.1.8 Bounded Integers (`assumes bounded_int(N)`)

```
    N ∈ ℕ⁺
   ──────────────────────────────
    Γ_f ⊢ bounded_int(N) : ok
```

**Rule:** `N` must be a positive integer literal. This is enforced at
parse time by the `NUMBER` terminal.

#### §2.1.9 Raises (`raises ExcType when cond`)

```
    ExcType ∈ CNAME       Γ_f ⊢ cond : ok
   ──────────────────────────────────────────
    Γ_f ⊢ raises(ExcType, cond) : ok
```

**Rule:** The exception type must be a valid identifier (enforced by
parser). The condition expression must be well-formed in the function
scope. `\result` is NOT allowed in the condition (checked via
`is_postcondition=False`).

#### §2.1.10 Thread Entry (`thread_entry`)

```
   ────────────────────────────
    Γ_f ⊢ thread_entry : ok
```

**Rule:** Always well-formed syntactically. Semantically meaningful only
when `--memory-model concurrent` is active. No static check is performed
on the memory model at Module4 level.

#### §2.1.11 _(reserved — colon-separated provenance `proof` directive removed 2026-05-27)_

The provenance-only `#@ proof rocq: <qualname>` / `#@ proof lean:
<qualname>` directive (colon-separated) was removed from the
language on 2026-05-27. The companion-proof file layout it described
still applies; the linkage is now via the load-bearing
`#@ proof rocq <q>` / `#@ proof lean <q>` directive at §2.1.12
(space-separated, no colon). The section number is reserved to keep
cross-references stable.

#### §2.1.12 Proof Citation (`proof`) — Rocq + Lean as Cross-Validated Spec Sources

```
    prover ∈ {rocq, lean}      qualname: dotted identifier
   ──────────────────────────────────────────────────────────
    Γ_module ⊢ proof(prover, qualname) : ok
```

**Rule:** Always well-formed syntactically. `prover` is restricted to
`{rocq, lean}` by the grammar terminal. The `qualname` is opaque to PyCSL
at parse time — resolution is delegated to the `proof2why3` tool (for
extracting the theorem statement into the WhyML preamble) and to
`pycsl --audit-proof` (for verifying that the cited theorem actually
exists in the companion proof sources).

**Namespace-aware audit semantics.** The qualname `A.B.C.thm` is
well-formed under `--audit-proof` iff parsing of some `.v` / `.lean`
file in the proof directory yields a theorem named `thm` declared
inside the nested module/namespace path `A.B.C`. The audit reads the
proof files with a state machine that tracks `Module`/`End` (Rocq)
or `namespace`/`end` (Lean) and records every top-level declaration
keyword (`Theorem`, `Lemma`, `Definition`, `Fixpoint`, ... for Rocq;
`theorem`, `lemma`, `def`, `inductive`, ... for Lean). Default proof
dirs: `<file>.proofs/{rocq,lean}/`. See `src/pycsl/audit_proof.py`
for the supported subset.

**Scope:** Module-level. Unlike function-level directives (§2.1.1–2.1.11),
`proof` is not attached to a function — it declares a theory-level
axiom available to the entire module.

**Implementation:** `Module2_Parser` records each `proof` as an
`ProofDecl(prover, qualname)` AST node. `Module3_Weaver` collects
them into the module-level IR. `Module5_IREmitter` serializes them.
`Module6_WhyMLTranspiler` invokes `proof2why3 emit` for each entry,
producing `axiom pycsl_axiom_<target> : …` in the WhyML preamble.

**Cross-validation semantics ("Rocq + Lean as Cross-Validated Spec
Sources").** When both a `rocq` and a `lean` directive reference the same
`pycsl_target` name, the `proof2why3 cross-check` tool extracts both
theorem statements, canonicalizes them (alpha-normalize, AC-flatten,
`nat`/`Nat` → `int + ≥ 0`), and verifies equality. If the canonical
forms differ, the cross-check exits with a `disagreement` status and a
structured diff — the pipeline halts rather than emit a potentially
unsound axiom.

**No new error codes** at the PyCSL static-analysis level — validation
is deferred to `proof2why3`. If the proof source cannot be found or
the `pycsl_target` attribute is missing, `proof2why3` raises an error
during Module6's preamble emission phase.

_Corresponds to `annotations.md` §2.1.12._

#### §2.1.13 No-exception (`no_exception E1, E2, …` / `no_exception \all`)

```
    {E_1, …, E_n} ⊆ KNOWN_EXCEPTIONS        ∀i: E_i ∉ raised(f)
   ───────────────────────────────────────────────────────────────
              Γ_f ⊢ no_exception(E_1, …, E_n) : ok
```

```
              raised(f) = ∅
   ──────────────────────────────────
    Γ_f ⊢ no_exception(\all) : ok
```

where `raised(f) = { E | raises(E, _) ∈ Γ_f }` is the set of exception
names declared in the function's `raises` clauses, and
`KNOWN_EXCEPTIONS = {ZeroDivisionError, IndexError, KeyError,
ValueError, StopIteration}` (Phase 1 — see
`src/pycsl/exception_model.py`).

**Proof obligation.** Under the function's precondition `P`, every IR
operation `op` in the body satisfying `(kind(op), subkind(op)) ∈
dom(TRIGGERS)` must discharge each `trigger(op, E)` for which
`E ∈ no_exception_set(f) ∨ no_exception_all(f)`:

```
    Γ, P ⊢ trigger(op, E)        for every op such that E ∈ active(f)
```

where `active(f) = no_exception_set(f) ∪ (no_exception_all(f) ?
KNOWN_EXCEPTIONS : ∅)` and `TRIGGERS` is the table in
`exception_model.py`.

**Rule (conflict rejection).** `no_exception(E) ∧ raises(E, _) ∈ Γ_f`
is rejected by `Module4_SemanticAnalyzer._validate_no_exception` with a
`PyCSLSemanticError`. The `\all` form additionally requires
`raised(f) = ∅`; otherwise rejected.

**Rule (unknown name).** Any name in the directive that is not in
`KNOWN_EXCEPTIONS` is rejected as a `PyCSLSemanticError` listing the
known set.

**Inter-procedural propagation (workplan §1.4).** At a call site
`g(args)` inside a function `f`, the obligation imposed on `f` for each
`E ∈ active(f)`:

- If `g` declares `no_exception E` (proved): no obligation at the call
  site for `E`.
- If `g` declares `raises(E, P_g)`: the call site must discharge `¬P_g`
  in the local context.
- Otherwise (`g` is unannotated for `E`): no obligation by default
  (ambient mode, preserving backward compatibility); pessimistic under
  `--strict-no-exception-propagation`, in which case the call site must
  discharge `false` (i.e. the call cannot be proved without strengthening
  `g`'s annotations).

The CLI flag is off by default and treated as opt-in; ambient mode is
the default per workplan §11.3.

_Corresponds to `annotations.md` §2.1.13._

### 2.2 Loop Contracts

_Corresponds to `annotations.md` §2.2._

#### §2.2.1 Loop Invariant (`loop invariant`)

```
    Γ_f ⊢ e : ok       \result ∉ FV(e)
   ─────────────────────────────────────
    Γ_f ⊢ loop_invariant(e) : ok
```

**Rule:** The invariant expression is validated against the **enclosing
function's scope** (not a separate loop scope). `\result` is disallowed.

**Implementation note:** `visit_While` calls `_validate_contract` with
`is_postcondition=False`, which checks both `\result` absence and variable
scope.

#### §2.2.2 Loop Variant (`loop variant`)

```
    Γ_f ⊢ e : ok       \result ∉ FV(e)
   ─────────────────────────────────────
    Γ_f ⊢ loop_variant(e) : ok
```

**Rule:** Same as loop invariant.

#### §2.2.3 Allow iteration mutation (`allow_iteration_mutation`)

```
   ──────────────────────────────────────────────
    Γ_f ⊢ allow_iteration_mutation : ok
```

**Rule:** Always well-formed syntactically (no operands). Semantically
significant only when attached to a `for` statement — it sets the
per-loop flag that suppresses the UB-7.1 check performed by
`IRScanner.find_iteration_mutations`. Module 5 propagates the flag as
`allow_iteration_mutation: true` on the IR for-loop node; Module 4
consults it via `pycsl.py:_run_pipeline` immediately after IR
validation.

**Verification stance.** UB-7.1 is a *hard error* by default —
mutating the iterated collection corrupts CPython's iterator state.
The annotation opts a single `for` loop out of the check; nested
loops inside it are still checked. Prefer rewriting (`for k in
list(d):`) to the annotation when feasible.

**Error (UB-7.1 without the annotation):** `"UB-7.1 — the loop body
mutates the iterated collection '<C>'. ... Either rewrite to iterate
over a snapshot ... or annotate the loop with
`#@ allow_iteration_mutation`."`

**Cross-reference:** `config/skills/pycsl-ub-catalog/SKILL.md` §7.1
and `annotations.md` §2.2.3.

### 2.3 Class Contracts

_Corresponds to `annotations.md` §2.3._

#### §2.3.1 Class Invariant (`class invariant`)

```
    FV(e) ⊆ dom(Γ_c)
   ─────────────────────────────────
    Γ_c ⊢ class_invariant(e) : ok
```

**Rule:** Every free variable in the invariant expression must be a known
class field (i.e., must appear in Γ_c). Class invariant expressions
should only reference `self.field` and constants.

**Error (E5):** `"Undefined variable '<var>' in class invariant for
'<ClassName>'. Class invariants should only reference self.field or
constants. Available fields: [...]"`

**Implementation note:** `visit_ClassDef` calls `extract_variables` on
the invariant expression. `FieldAccess` nodes are excluded from variable
extraction (they are validated separately via the field table). Variables
that appear as bare names (e.g., numeric constants used in comparisons)
ARE checked against Γ_c.

#### §2.3.2 Allow finalizer (`allow_finalizer`)

```
   ─────────────────────────────────
    Γ_c ⊢ allow_finalizer : ok
```

**Rule:** Always well-formed syntactically (no operands). Sets the
per-class `csl_allow_finalizer` flag consulted by
`Module3_Weaver.visit_ClassDef`, which otherwise rejects any class
body containing a `def __del__` with `PyCSLSemanticError`.

**Verification stance.** UB-7.5 is a *hard error* by default —
CPython's finalizer protocol is non-deterministic (timing depends
on the garbage collector and may be skipped at interpreter
shutdown). The annotation documents the boundary so the rest of
the class can still be verified; contracts that reference lifetime
(e.g. "the finalizer releases X") remain at risk.

**Error (UB-7.5 without the annotation):** `"Class '<name>' (line
<lno>): `__del__` finalizer is rejected under UB-7.5. ... Either
remove `__del__` or annotate the class with `#@ allow_finalizer` to
acknowledge that any lifetime-dependent contracts are at risk."`

**Cross-reference:** `config/skills/pycsl-ub-catalog/SKILL.md` §7.5
and `annotations.md` §2.3.2.

### 2.4 Program Point Annotations

_Corresponds to `annotations.md` §2.4._

#### §2.4.1 Label (`label`)

```
    name ∈ CNAME
   ─────────────────────
    Γ ⊢ label(name) : ok
```

**Rule:** The label name must be a valid identifier (enforced by parser).
No scope check — the label **defines** a new program point.

**Implementation note:** Labels are attached to AST nodes by the Weaver
via `csl_labels`. No Module4 validation is performed on labels; they are
used by `\at` expressions (§3.1.7) which reference them by name.

#### §2.4.2 Ghost Assign (`ghost x = expr`)

```
    Γ_f ⊢ expr : ok
   ─────────────────────────────────
    Γ_f ⊢ ghost_assign(x, expr) : ok
```

**Rule:** The ghost expression must be well-formed. The target variable
`x` is added to Γ_ghost (and thus becomes part of Γ_f for subsequent
checks).

**Implementation note:** Ghost variables are collected during
`_build_function_scope`. The first `ghost x = expr` declares the variable;
subsequent `ghost x += expr` modify it.

#### §2.4.2b Typed Ghost Declaration (`ghost x : T = expr`)

```
    ghost_type T ∈ {string, array, ghost_dict, ghost_list,
                    ghost_set, tuple2, tuple3, tuple4}
    Γ_f ⊢ expr : ok
   ───────────────────────────────────────────────────────────
    Γ_f ⊢ ghost_typed_assign(x, T, expr) : ok
    with Γ_ghost[x ↦ T]
```

**Ghost type to WhyML type mapping (τ_ghost):**

| Ghost type | WhyML type |
|---|---|
| `string` | `ref string` |
| `array` | `array int` (not a ref) |
| `ghost_dict` | `ref (map int (option int))` |
| `ghost_list` | `ref (list int)` |
| `ghost_set` | `ref (map int bool)` |
| `tuple2` | `ref (int, int)` |
| `tuple3` | `ref (int, int, int)` |
| `tuple4` | `ref (int, int, int, int)` |

**Rule:** The declared ghost type must be one of the **eight** `GHOST_TYPE` keywords above
(grammar terminal `GHOST_TYPE`, `Module2_Parser.py`). `int` is **not** a `GHOST_TYPE` keyword
— it is the *default* tag for the untyped form `#@ ghost x = e` (`GhostAssignDecl.declared_type`
defaults to `"int"`), so `#@ ghost x : int = e` is not accepted by the typed-declaration rule.
The initial expression must be well-formed. Subsequent `ghost x = e` and `ghost x += e` treat
`x` as having the declared type.

_Corresponds to `annotations.md` §11.1._

#### §2.4.3 Ghost Augmented Assign (`ghost x += expr`)

```
    x ∈ dom(Γ_ghost)       Γ_f ⊢ expr : ok
   ──────────────────────────────────────────
    Γ_f ⊢ ghost_aug_assign(x, op, expr) : ok
```

**Rule:** The target must already exist as a ghost variable. The
expression must be well-formed.

**Implementation note:** Currently no explicit check that `x` was
previously declared as a ghost variable. The variable scope check in
`_validate_contract` will catch references to undeclared variables.

#### §2.4.4 Critical Section (`critical mutex`)

```
    mutex ∈ dom(Γ_m._shared_vars) ∨ mutex ∈ CNAME
   ──────────────────────────────────────────────────
    Γ ⊢ critical(mutex) : ok
```

**Rule:** The mutex name should correspond to a protecting mutex declared
via `#@ shared ... protected_by`. No explicit validation in Module4 for
the mutex name itself — the semantic check occurs when the protected access
checker walks the function body.

#### §2.4.5 Acquires (`acquires mutex`)

Same rule as `critical`.

**Translational alias.** `#@ acquires L` is operationally **equivalent
to `#@ critical L`** — Module 3 weaves both into the same
`csl_critical_mutex` field on the `with` node, Module 5 emits the
same `CriticalSection` IR node, and Module 6 emits the same
havoc+assume/assert pattern (translational reference §T.7.4). The
alias exists for protocol-style annotation when the acquire point
is named explicitly alongside a later `releases` line; the two
directives are interchangeable. See `annotations.md` §10 (line 852).

#### §2.4.6 Releases (`releases mutex`)

Same rule as `critical`.

**Informational only.** Unlike `acquires`, `#@ releases L` produces
**no WhyML emission** (translational reference §T.7.4). The release
point is implicit at the end of the `with` block; the explicit
directive documents the release for human readers and protocol
traces. Module 3 stores it on `csl_releases`; Module 6 reads it but
emits nothing. See `annotations.md` §10 (line 855).

### 2.6 Mixin Composition (Tier 1)

_Corresponds to `annotations.md` §2.7 and concrete-syntax §2.5._

A `#@ mixin` class declares `provides`/`depends_method`/`requires_method`/`shared_state`/
`touches_field`; a `#@ compose_from` class composes several mixins. The well-formedness of the
*composition* is checked by a Module 4 pass (`pycsl.py::_apply_composition`, run after inheritance),
not by per-directive rules alone.

```
    M_1, …, M_n are `#@ mixin` classes      every depends/requires_method of each M_i
    has EXACTLY ONE provider among M_1…M_n   no method has ≥2 providers (no collision)
    every `self.f` written by an M_i method is shared_state/touches_field/__init__-declared
   ──────────────────────────────────────────────────────────────────────────────────────
    Γ ⊢ compose_from(M_1, …, M_n) : ok
```

**Per-directive rules.**
- `mixin` / `compose_from` — well-formed before a `class`; `provides`/`shared_state`/`touches_field`/
  `depends_method`/`requires_method` before a `def`. (`Module3_Weaver`: `csl_is_mixin`,
  `csl_compose_from`, `csl_provides`, `csl_mixin_shared_state`, `csl_touches_field`, `csl_method_deps`.)
- `shared_state f: T` (D1) — declares **deliberately shared** facade state; multiple mixins may
  read/write `f` (not a conflict). A write to `f` must appear in the method's `assigns` (existing
  check). `touches_field f: T` (D1) — an **owned** field; two owners ⇒ conflict (Tier 2).
- `depends_method m: σ` (D2, concrete) / `requires_method m: σ` (D2, abstract) — the declared contract
  is emitted as an abstract `val` and the mixin is verified **once** against it (`\abstract`, never
  `\trusted`); on `compose_from` the concrete provider is checked to **refine** it.

**Errors (each a distinct `PyCSLSemanticError`, exercised by the negative corpus):** a dependency with
**no** provider (`0550`); a method with **two** providers — a silent collision needing Tier-2
`#@ resolve` (`0552`); a mixin method writing an **undeclared** `self.<field>` (`0551`).

**Determinism/purity (D3).** No separate `#@ deterministic`/`#@ pure` directive exists in Tier 1; a
referentially-transparent dependency is expressed with `#@ assigns \nothing`, which the existing RT
inference (`module5/memoization_rt.py::_detect_purity`) already treats as pure.

**Out of scope (soundness boundary — getattr dispatch).** PyCSL's real facade routes handlers through
**dynamic, dict-keyed dispatch** — `getattr(self, _EXPR_DISPATCH[t])` (`module6_whyml/expressions.py`)
and `_STMT_HANDLERS[s]` (`statements.py`). Tier 1 verifies the mixin **algebra over statically-named
providers** and scopes that dynamic dispatch **out**: routing correctness is a separate *coverage*
obligation (the IR-type domain is exhausted by the table's keys — the same shape as "all WP arms
covered"), **orthogonal** to composition soundness. No `\trusted` is added to the mixin methods; the
dispatch *table* is the boundary. Recognising `getattr(self, TABLE[t])` and lowering it to a
`depends_method` over the table's value set (Tier 1.5) is gated on a real self-hosting driver. Tier 2
(conflict resolution) and Tier 3 (diamonds, general variance) are likewise gated.

**Cross-reference:** `mixin.md` / `mixin-ready.md` (D1–D4, R2), `annotations.md` §2.7,
`pycsl-annotate` SKILL; corpus `0549`–`0553`.

---

### 2.x  Bounded contract expansion (`#@ for`)

A `#@ for <var> in range(<lo>, <hi>):` block is well-formed iff:

1. **Static integer bounds.** `<lo>` and `<hi>` are integer literals (v1; named integer constants are a
   staged follow-on). A non-constant bound is a hard error — never a silent fallback to `\forall` or to
   skipping expansion.
2. **Integer index.** `<var>` is an integer, bound **only** within the block (it does not escape), used
   only in integer positions; the expanded clause is type-checked normally after substitution, so a
   misuse surfaces as an ordinary clause error on the ground form.
3. **Non-empty body**, each line a `requires`/`ensures` clause that **mentions `<var>`** (a body clause
   independent of `<var>` would yield identical copies — flagged).
4. **No nesting** (v1): a `#@ for` body may not contain another `#@ for` (the body grammar admits only
   `requires`/`ensures`).

Because the block desugars to ground clauses that already have a defined meaning, it introduces **no new
proof obligation kind** — well-formedness of the expansion is inherited from the clauses it produces.

**Cross-reference:** `sugar-for-spec.md`, `annotations.md` §2.9, concrete-syntax §2.1.16, translational
§T.2.5b; corpus `0666`.

---

### 2.y  Contract opacity (`#@ interface` / `#@ reveal`)

A function may carry a narrow **interface** contract alongside its rich **definition** contract
(`b-spec.md`, Track B). Well-formedness:

1. **Interface clause kind.** `#@ interface` must be followed by `ensures`, `requires`, or `assigns` —
   the same clause kinds as a definition contract; the payload is checked exactly like its definition
   counterpart (same expression well-formedness, §3).
2. **Soundness — the interface is a weakening of the definition.** The interface may not claim more than
   the definition proves. This is discharged, not assumed: the **narrowing VC** (translational §T.2.5c)
   emits Why3 goals `definition ⟹ interface` (for `ensures`) and `interface ⟹ definition` (for
   `requires`) in the owning unit; an over-claiming interface yields an unprovable goal and is rejected.
   So a caller relying on the interface relies only on a fact the definition established — opacity adds
   nothing to the trusted base.
3. **`#@ reveal <fn>`** names a function in scope; it opts the enclosing call site into `<fn>`'s
   definition contract. Within `<fn>`'s owning unit it is a no-op (the definition is the visible `let`).
4. **Absence is transparent.** With no `#@ interface`, the interface *is* the definition — existing code
   is unaffected.

**Cross-reference:** `b-spec.md`, `annotations.md` §2.10, concrete-syntax §2.1.17–§2.1.18, translational
§T.2.5c.

---

## 3. Expression Well-Formedness

_Corresponds to `annotations.md` §3._

The expression well-formedness judgement Γ ⊢ e : ok is defined
recursively over the expression structure.

### 3.1 Atoms

_Corresponds to `annotations.md` §3.1._

#### §3.1.1 Integer Literal (`NUMBER`)

```
   ──────────────────
    Γ ⊢ Number(n) : ok
```

Always well-formed.

#### §3.1.2 Variable (`CNAME`)

```
    x ∈ dom(Γ_f)
   ──────────────────
    Γ_f ⊢ Var(x) : ok
```

**Error (E2):** `"Undefined variable '<x>' referenced in contract for
<context>."`

**Implementation:** `extract_variables` collects all `Var` nodes;
`_validate_contract` checks each against `current_scope`.

#### §3.1.3 Field Access (`self.field`)

```
    field ∈ dom(Γ_c)       (* within a method context *)
   ─────────────────────────
    Γ_c ⊢ FieldAccess(self, field) : ok
```

**Implementation note:** `FieldAccess` nodes are **excluded** from
`extract_variables` (line 58: `return set()`). They are validated
separately. In the current implementation, there is no explicit check
that `field ∈ dom(Γ_c)` for individual field accesses in function
contracts — this is a **known gap** (see §10).

#### §3.1.4 Subscript (`arr[i]`)

```
    arr ∈ dom(Γ_f)       Γ_f ⊢ i : ok
   ─────────────────────────────────────
    Γ_f ⊢ SubscriptAccess(arr, i) : ok
```

The array name is extracted as a variable by `extract_variables`.
The index expression is recursively checked.

#### §3.1.4b Chained Subscript (`arr[i][j]`)

```
    arr ∈ dom(Γ_f)       Γ_f ⊢ i : ok       Γ_f ⊢ j : ok
   ─────────────────────────────────────────────────────────
    Γ_f ⊢ ChainedSubscript(arr, i, j) : ok
```

Both indices and the array name are checked.

#### §3.1.5 Result (`\result`)

```
    is_postcondition = True
   ─────────────────────────
    Γ_f ⊢ Result : ok
```

**Error (E1):** Raised when `\result` appears outside an `ensures` clause.

**Implementation:** `contains_result` traverses the expression tree.
`_validate_contract` checks `is_postcondition` flag.

#### §3.1.5b Result Subscript (`\result[i]`)

```
    is_postcondition = True       Γ_f ⊢ i : ok
   ──────────────────────────────────────────────
    Γ_f ⊢ ResultSubscript(i) : ok
```

`\result[i]` is treated specially: `contains_result` returns `True` for
`SubscriptAccess` nodes where `array == "\\result"`. The `\result` name
is excluded from variable scope checking.

#### §3.1.6 Old (`\old(e)`)

```
    Γ_f ⊢ e : ok
   ─────────────────────
    Γ_f ⊢ Old(e) : ok
```

The inner expression is recursively checked. No additional constraint
on what `e` may reference (any in-scope expression is valid).

#### §3.1.7 At (`\at(e, L)`)

```
    Γ_f ⊢ e : ok       L ∈ declared_labels
   ─────────────────────────────────────────
    Γ_f ⊢ At(e, L) : ok
```

**Implementation note:** Currently, there is no Module4 check that label
`L` has been declared before use. The label is accepted as a CNAME and
passed through. Forward references to undeclared labels may produce errors
at the WhyML level. This is a **known gap** (see §10).

#### §3.1.8 Array Length (`\length(arr)`)

```
    arr ∈ dom(Γ_f)
   ──────────────────────────
    Γ_f ⊢ ArrayLength(arr) : ok
```

The array name is extracted as a variable.

#### §3.1.9 Valid (`\valid(arr, n)`)

```
    arr ∈ dom(Γ_f)       τ(Γ_f(arr)) ∈ {list, List, Any}
    Γ_f ⊢ n : ok
   ──────────────────────────────────────────────────────
    Γ_f ⊢ Valid(arr, n) : ok
```

**Error (E6):** `"\\valid base '<arr>' is not a list parameter in
<context> (got type '<type>')."`

**Implementation:** `_validate_predicate_bases` performs this check
recursively for all `Valid` nodes in the expression tree. The `None`
type (undeclared variable) is accepted — this allows `\valid` to be
used with parameters that have no type annotation.

#### §3.1.10 Separated (`\separated(a, na, b, nb)`)

```
    a ∈ dom(Γ_f)    τ(Γ_f(a)) ∈ {list, List, Any}
    b ∈ dom(Γ_f)    τ(Γ_f(b)) ∈ {list, List, Any}
    Γ_f ⊢ na : ok   Γ_f ⊢ nb : ok
   ───────────────────────────────────────────────
    Γ_f ⊢ Separated(a, na, b, nb) : ok
```

**Error (E7):** `"\\separated base '<base>' is not a list parameter in
<context> (got type '<type>')."`

Same implementation as `\valid` via `_validate_predicate_bases`.

#### §3.1.11 Length2D (`\length2d(a, m, n)`)

```
    a ∈ dom(Γ_f)       Γ_f ⊢ m : ok       Γ_f ⊢ n : ok
   ──────────────────────────────────────────────────────
    Γ_f ⊢ Length2D(a, m, n) : ok
```

**Implementation note:** No explicit list-type check for the base of
`\length2d`. The base name is extracted as a variable by
`extract_variables` and checked for scope membership.

#### §3.1.12 Valid2D (`\valid2d(a, i, j)`)

Same rule as `\length2d`.

#### §3.1.13 Nothing (`\nothing`)

```
    context = assigns_target
   ─────────────────────────
    Γ ⊢ Nothing : ok
```

Only valid as an assigns target. This is enforced by the grammar
(§3.4), not by Module4.

#### §3.1.14 String Literal

```
   ────────────────────────────
    Γ ⊢ StringLiteral(s) : ok
```

Always well-formed.

#### §3.1.15 IsSorted (`\is_sorted(arr, lo, hi)`)

```
    arr ∈ dom(Γ_f)       Γ_f ⊢ lo : ok       Γ_f ⊢ hi : ok
   ──────────────────────────────────────────────────────────
    Γ_f ⊢ IsSorted(arr, lo, hi) : ok
```

The base and both bounds are checked via variable extraction.

#### §3.1.16 Sum (`\sum(arr, lo, hi)`)

Same rule as `\is_sorted`.

#### §3.1.17 Function Call (`f(args)`)

```
    f ∈ dom(Γ_f) ∨ f is a defined function
    ∀ a ∈ args: Γ_f ⊢ a : ok
   ──────────────────────────────────────────
    Γ_f ⊢ CallExpr(f, args) : ok
```

**Implementation note:** Module4 does NOT enforce the pure function
eligibility criteria (§4.1) at the static semantics level. Function
call well-formedness is limited to scope checking the function name
and arguments. Pure function eligibility is checked later during IR
emission (Module5).

#### §3.1.18 Boolean (`True`, `False`)

```
   ──────────────────────────
    Γ ⊢ CSLBool(v) : ok
```

Always well-formed.

#### §3.1.19 None

```
   ──────────────────────
    Γ ⊢ CSLNone : ok
```

Always well-formed.

#### §3.1.20 Slice (`arr[lo:hi]`)

```
    arr ∈ dom(Γ_f)       Γ_f ⊢ lo : ok       Γ_f ⊢ hi : ok
   ──────────────────────────────────────────────────────────
    Γ_f ⊢ CSLSlice(arr, lo, hi) : ok
```

The array name and both bounds are checked via variable extraction.

#### §3.1.21 Empty Map (`\empty_map`)

```
   ──────────────────────
    Γ_f ⊢ \empty_map : ok
```

Unconditionally well-formed. Lowers to `const (None: option int)` in WhyML.

#### §3.1.22 Map Get (`\map_get(d, k)`)

```
    Γ_f ⊢ d : ok       Γ_f ⊢ k : ok
   ────────────────────────────────────
    Γ_f ⊢ \map_get(d, k) : ok
```

Both the dict expression and key must be well-formed. No type constraint
is enforced at Module4 — `d` is expected to be a `ghost_dict`-typed variable.

#### §3.1.23 Map Set (`\map_set(d, k, v)`)

```
    Γ_f ⊢ d : ok       Γ_f ⊢ k : ok       Γ_f ⊢ v : ok
   ────────────────────────────────────────────────────────
    Γ_f ⊢ \map_set(d, k, v) : ok
```

All three arguments must be well-formed.

#### §3.1.24 Map Remove (`\map_remove(d, k)`)

```
    Γ_f ⊢ d : ok       Γ_f ⊢ k : ok
   ────────────────────────────────────
    Γ_f ⊢ \map_remove(d, k) : ok
```

Both arguments must be well-formed. Returns the dict with key `k` set to absent.

#### §3.1.25 Has Key (`\has_key(d, k)`)

```
    Γ_f ⊢ d : ok       Γ_f ⊢ k : ok
   ────────────────────────────────────
    Γ_f ⊢ \has_key(d, k) : ok
```

Both arguments must be well-formed. Lowers to `Map.get !d k <> None`.

#### §3.1.26 Map Eq (`\map_eq(d1, d2)`)

```
    Γ_f ⊢ d1 : ok       Γ_f ⊢ d2 : ok
   ─────────────────────────────────────
    Γ_f ⊢ \map_eq(d1, d2) : ok
```

Both dict arguments must be well-formed. Lowers to a universally
quantified equality in WhyML — may be expensive for SMT solvers in
deep loop invariants; restrict to shallow comparisons.

_Corresponds to `annotations.md` §11.2._

### 3.2 Operators

_Corresponds to `annotations.md` §3.2._

For all binary and unary operators, the rule is structural:

#### Binary Operators (§3.2.2–§3.2.8)

```
    Γ ⊢ left : ok       Γ ⊢ right : ok
   ─────────────────────────────────────
    Γ ⊢ BinOp(left, op, right) : ok
```

No type checking on operand types. All values are treated as integers
in the WhyML model (booleans are 0/1, None is 0).

#### Unary Operators (§3.2.9)

```
    Γ ⊢ e : ok
   ──────────────────────────
    Γ ⊢ UnaryOp(op, e) : ok
```

#### Membership (§3.2.6b)

```
    Γ ⊢ element : ok       Γ ⊢ collection : ok
   ──────────────────────────────────────────────
    Γ ⊢ CSLIn(element, collection) : ok
    Γ ⊢ CSLNotIn(element, collection) : ok
```

### 3.3 Quantifiers

_Corresponds to `annotations.md` §3.3._

#### Forall (§3.2.1)

```
    Γ_f ∪ {x : int} ⊢ body : ok
   ──────────────────────────────
    Γ_f ⊢ Forall(x, body) : ok
```

**Bound variable scoping:** The bound variable `x` is typed `int` and
added to the scope for the duration of the body. If `x` shadows an
existing variable in Γ_f, the shadowed variable is inaccessible within
the quantifier body.

**Implementation:** `extract_variables` handles this via:
```python
if isinstance(node, QuantifierNode):
    return extract_variables(node.body) - {node.var}
```

This subtracts the bound variable from the set of free variables,
ensuring that `x` is not checked against the outer scope.

**Nesting:** Quantifiers may be nested. Each nesting level extends the
scope with an additional bound variable:

```
Γ_f ⊢ \forall i; \forall j; P(i, j) : ok
  ↔  Γ_f ∪ {i : int} ∪ {j : int} ⊢ P(i, j) : ok
```

#### Exists (§3.2.1)

Same rule as `Forall`. The keyword `\exist` (singular) is an alias for
`\exists` (handled by the parser).

### 3.4 Assigns Targets

_Corresponds to `annotations.md` §3.4._

| § | Target | Well-formedness rule |
|---|--------|---------------------|
| 3.4.1 | `\nothing` | Always valid |
| 3.4.2 | `x` | `x ∈ dom(Γ_f)` |
| 3.4.3 | `x, y` | `{x, y} ⊆ dom(Γ_f)` |
| 3.4.4 | `self.field` | `field ∈ dom(Γ_c)` |
| 3.4.5 | `arr[lo..hi]` | `arr ∈ dom(Γ_f)`, `τ(arr) ∈ {list, List, Any}`, `Γ_f ⊢ lo, hi : ok` |

**Error (E3, E4):** See §2.1.3.

---

## 4. Unsupported Constructs

_Corresponds to `annotations.md` §4._

Constructs listed in `annotations.md` §4 are **rejected at parse time**
(Module2, not Module4). No static semantics rules are needed for them
since they never produce an AST node.

### 4.1 Pure Function Eligibility

_Corresponds to `annotations.md` §4.1._

A function `f` may appear in a contract expression iff:

1. `f` has `#@ assigns \nothing` (no side effects)
2. `f` is not annotated `#@ \diverges`
3. `f` is in scope (defined in the same module or imported)
4. If recursive, `f` must have a `#@ \variant` annotation

**Implementation note:** These eligibility checks are NOT performed by
Module4. They are deferred to Module5 (IR emission), where the function's
metadata is available. Module4 only performs scope checking on the
function name (as a `CallExpr` atom whose function name is treated as
a `CNAME` variable).

**Gap:** This means that a call to a non-pure function in a contract
expression will pass Module4 but fail at Module5 or Module6 with a
potentially confusing error message.

---

## 5. Memory Model Constraints

_Corresponds to `annotations.md` §5._

### 5.1 Hoare Model (Default)

No additional static constraints. All annotations are accepted.

### 5.2 Typed Model

**Additional constraint:** `\valid(arr, n)` and `\separated(a, na, b, nb)`
bases must be list-typed parameters.

This is enforced by `_validate_predicate_bases` (see §3.1.9, §3.1.10).
The check applies regardless of memory model (it is not gated on
`--memory-model typed`).

### 5.3 Store Model

Same constraints as Typed.

### 5.4 Concurrent Model

_Corresponds to `annotations.md` §5.4._

The concurrent model adds three static checks:

#### 5.4.1 Protected Access Check

_Implemented in `_check_protected_in_stmts` and the dispatch table
`_PROTECTED_HANDLERS`._

**Rule:** Every read or write to a `shared` variable must occur inside a
`with` block annotated with `#@ critical <mutex>` or `#@ acquires <mutex>`
for the variable's protecting mutex.

```
    var ∈ shared_vars
    protecting_mutex(var) = M
    M ∈ held_mutexes(current_position)
   ──────────────────────────────────────
    access(var) : ok
```

**Error (E8):** `"Function '<f>': unprotected <read/write> of shared
variable '<var>' (protected_by '<mutex>', but held mutexes are <held>)."`

**Statement dispatch table:** The protected access checker walks the
function body using a dispatch table:

| AST Node | Handler | Checks |
|----------|---------|--------|
| `ast.With` | `_protected_with` | Extends held set; checks nesting |
| `ast.If` | `_protected_if` | Recurses into both branches |
| `ast.While` / `ast.For` | `_protected_loop` | Recurses into body |
| `ast.Assign` | `_protected_assign` | Checks targets and value for shared access |
| `ast.AugAssign` | `_protected_aug_assign` | Checks target for shared write |
| `ast.Return` | `_protected_return` | Checks return value for shared read |
| `ast.Expr` | `_protected_expr` | Checks expression for shared read |

**Unprotected shared variables:** Variables declared with `#@ shared x`
(without `protected_by`) are **lenient** — Module4 does not raise an error
for unprotected access. The `ConcurrencyChecker` may issue a warning.

#### 5.4.2 Lock Order Check

_Implemented in `_protected_with`._

**Rule:** When a function acquires a mutex while already holding one or
more other mutexes (nested `with` blocks), a `#@ lock_order` declaration
must exist at module level.

```
    held ≠ ∅       acquiring(mutex)       lock_order = None
   ──────────────────────────────────────────────────────────
    ERROR
```

**Error (E9):** `"Function '<f>': nested mutex acquisition of '<mutex>'
while holding <held> requires a module-level '#@ lock_order' declaration."`

If a lock order IS declared, the acquisition must respect it:

```
    held = {m₁}       acquiring(m₂)       order = [..., m₁, ..., m₂, ...]
    index(m₁) < index(m₂)
   ─────────────────────────────────────────────────────────────────────────
    acquire(m₂) : ok
```

**Error (E10):** `"Function '<f>': lock_order violation — acquiring
'<m2>' while holding '<m1>' violates declared order <order>."`

#### 5.4.3 Mutex Invariant Scope

_Implemented in `_validate_mutex_invariant_scope`._

**Rule:** The invariant expression for mutex `M` may only reference
variables that are protected by `M`.

```
    protected(M) = {v | shared_vars(v) = M}
    FV(invariant) ⊆ protected(M) ∪ dom(Γ_f) ∪ short_names
   ──────────────────────────────────────────────────────────
    mutex_invariant(M, invariant) : ok
```

**Leniency:** Variables in Γ_f (function scope, though at module level
this is typically empty) and short names (≤ 2 characters, common in
quantifier-bound variables like `i`, `j`) are accepted without error.

**Error (E11):** `"Mutex invariant for '<mutex>': variable '<var>' is not
a shared variable protected by '<mutex>'. Protected variables: [...]"`

---

## 6. Class Contract Well-Formedness

_Corresponds to `annotations.md` §6._

### 6.1 Invariant Scope

Class invariant expressions are validated in `visit_ClassDef`:

1. `extract_variables(inv.expr)` returns the set of free variables.
2. `FieldAccess` nodes are excluded (they reference `self.field`, which
   is validated via Γ_c in the field table).
3. Each remaining variable must exist in Γ_c.

### 6.2 Cross-Field Invariants

An invariant may reference multiple fields:

```python
""  # pycsl
#@ class invariant self._lo <= self._hi
```

Both `_lo` and `_hi` must be in Γ_c (i.e., assigned in `__init__`).

### 6.3 Multiple Stacked Invariants

Multiple `#@ class invariant` lines are independently checked. Each
invariant expression undergoes the same scope validation.

### 6.4 Method Contract Interaction

When a method is visited via `visit_FunctionDef`, the class field table
Γ_c is available (set by the enclosing `visit_ClassDef`). Method
contracts may reference `self.field` in `requires`, `ensures`, and
`assigns` clauses.

**Invariant preservation:** The static semantics do NOT check that method
contracts are strong enough to preserve the class invariant. This is a
**proof obligation** discharged by Why3 at verification time.

---

## 7. Temporal Expressions: `\old` and `\at`

_Corresponds to `annotations.md` §7._

### 7.1 `\old(expr)`

Validated by recursive expression checking:
```
    Γ_f ⊢ e : ok
   ─────────────────
    Γ_f ⊢ Old(e) : ok
```

The inner expression may reference function parameters, local variables,
and `self.field`. No additional constraint restricts what `e` may
reference.

### 7.2 `\at(expr, L)`

Validated by recursive expression checking:
```
    Γ_f ⊢ e : ok
   ─────────────────────
    Γ_f ⊢ At(e, L) : ok
```

**Known gap:** The label `L` is NOT checked against declared labels.
Undeclared labels pass Module4 and may produce errors at Module6 or
Why3.

---

## 8. Weaving Constraints

_Implemented in `Module3_Weaver`._

The Weaver performs one non-trivial static check:

### 8.1 Variant / Diverges Contradiction (W1)

```
    \variant ∈ contracts(f)       \diverges ∈ contracts(f)
   ──────────────────────────────────────────────────────────
    ERROR
```

**Error (W1):** `"Function '<f>' (line <n>): \\variant and \\diverges
are contradictory — one asserts termination, the other denies it."`

### 8.2 Contract Attachment

The Weaver attaches contracts to AST nodes based on line numbers:

| Contract Type | Attached To | Attribute |
|---------------|-------------|-----------|
| `Requires` | `ast.FunctionDef` | `csl_requires` |
| `Ensures` | `ast.FunctionDef` | `csl_ensures` |
| `Assigns` | `ast.FunctionDef` | `csl_assigns` |
| `FunctionVariant` | `ast.FunctionDef` | `csl_function_variants` |
| `Diverges` | `ast.FunctionDef` | `csl_diverges` (bool) |
| `Trusted` | `ast.FunctionDef` | `csl_trusted` (bool) |
| `RaisesDecl` | `ast.FunctionDef` | `csl_raises` |
| `BoundedIntDecl` | `ast.FunctionDef` | `csl_bounded_int` (int) |
| `ThreadEntry` | `ast.FunctionDef` | `csl_thread_entry` (bool) |
| `ProofDecl` | `ast.Module` | `csl_proof` (list, §2.1.12) |
| `LoopInvariant` | `ast.While` / `ast.For` | `csl_invariants` |
| `LoopVariant` | `ast.While` / `ast.For` | `csl_variants` |
| `GhostAssignDecl` | Any `ast.stmt` | `csl_ghost_assigns` |
| `ClassInvariant` | `ast.ClassDef` | `csl_class_invariants` |
| `Label` | Any `ast.stmt` | `csl_labels` |
| `SharedDecl` | `ast.Module` | `csl_shared_decls` |
| `MutexInvariant` | `ast.Module` | `csl_mutex_invariants` |
| `LockOrder` | `ast.Module` | `csl_lock_order` |
| `CriticalSection` | `ast.With` | `csl_critical_mutex` |
| `Acquires` | `ast.With` | `csl_acquires` |
| `Releases` | `ast.With` | `csl_releases` |

If a contract type appears on a line associated with the wrong AST node
type (e.g., `loop invariant` before a `def`), the contract is silently
ignored (it will not be attached to any attribute). This is by design —
the Weaver only looks for contracts matching the expected types for each
visitor method.

---

## 9. Error Catalogue

Complete catalogue of errors raised during static analysis.

### Module3 (Weaver) Errors

| ID | Condition | Error Type | Message |
|----|-----------|------------|---------|
| W1 | `\variant` + `\diverges` on same function | `ValueError` | `"\\variant and \\diverges are contradictory"` |

### Module4 (Semantic Analyzer) Errors

| ID | Condition | Error Type | Message |
|----|-----------|------------|---------|
| E1 | `\result` in non-`ensures` context | `PyCSLSemanticError` | `"Invalid use of '\\result' in <context>. It is only allowed in 'ensures'."` |
| E2 | Undefined variable in contract | `PyCSLSemanticError` | `"Undefined variable '<var>' referenced in contract for <context>."` |
| E3 | Assigns region on undefined variable | `PyCSLSemanticError` | `"Assigns region references undefined variable '<arr>' in <context>."` |
| E4 | Assigns region on non-list variable | `PyCSLSemanticError` | `"Assigns region on non-list variable '<arr>' (type '<type>') in <context>."` |
| E5 | Undefined variable in class invariant | `PyCSLSemanticError` | `"Undefined variable '<var>' in class invariant for '<class>'."` |
| E6 | `\valid` base not list-typed | `PyCSLSemanticError` | `"\\valid base '<arr>' is not a list parameter in <context>."` |
| E7 | `\separated` base not list-typed | `PyCSLSemanticError` | `"\\separated base '<base>' is not a list parameter in <context>."` |
| E8 | Unprotected shared variable access | `PyCSLSemanticError` | `"Function '<f>': unprotected <action> shared variable '<var>'."` |
| E9 | Nested acquisition without lock_order | `PyCSLSemanticError` | `"Function '<f>': nested mutex acquisition requires '#@ lock_order'."` |
| E10 | Lock order violation | `PyCSLSemanticError` | `"Function '<f>': lock_order violation — acquiring '<m2>' while holding '<m1>'."` |
| E11 | Mutex invariant references unprotected variable | `PyCSLSemanticError` | `"Mutex invariant for '<mutex>': variable '<var>' is not protected."` |
| E12 | Subscript assignment to undefined variable | `PyCSLSemanticError` | `"Subscript assignment to undefined variable '<arr>' in <context>."` |
| E13 | Subscript assignment to non-list/dict variable | `PyCSLSemanticError` | `"Subscript assignment to non-list/dict variable '<arr>' (type '<type>') in <context>."` (accepted target types: `list`, `List`, `dict`, `Dict`, `Any`) |
| E14 | Mutable default argument (ownership R2) | `PyCSLSemanticError` | `"Mutable default argument in <f>: a list/dict/set default is a single object shared across all calls (a shared-aliasing bug) and is outside PyCSL's value-semantics boundary (ownership discipline R2). Use a `None` sentinel and initialise the collection in the body."` Triggered when a `def f(…, x=<default>)` default is an `ast.List`/`Dict`/`Set` literal or a `list(...)`/`dict(...)`/`set(...)` call (positional **or** keyword-only defaults). Enforced by `Module4._validate_no_mutable_defaults`; spec'd in `docs/pycsl-ownership-discipline.md` §2/§5. The order-aware store-then-mutate sibling (R3) is **not** enforced yet (no-more-int Part 8). |

**Total:** 15 error sites (1 in Module3, 14 in Module4).

---

## 10. Gap Analysis

Discrepancies between the implemented static checks and the expected
well-formedness rules.

### 10.1 Missing Checks (Under-Specified)

| Feature | Expected Check | Current Status |
|---------|---------------|----------------|
| `self.field` scope in function contracts | `field ∈ dom(Γ_c)` for each `FieldAccess` in requires/ensures | **Not checked.** `FieldAccess` is excluded from `extract_variables`. Undeclared fields will pass Module4 and produce errors at Module6 (WhyML). |
| `\at(e, L)` label existence | Label `L` must be declared before use | **Not checked.** Any CNAME is accepted. Undeclared labels produce WhyML errors. |
| Pure function eligibility (§4.1) | `assigns \nothing`, not `\diverges`, has `\variant` if recursive | **Deferred to Module5.** Module4 only checks scope. |
| Ghost augmented assign pre-declaration | Target must already be a ghost variable | **Not explicitly checked.** Relies on scope checking to catch undeclared variables. |
| `bounded_int(N)` range | `N` must be 8, 16, 32, or 64 | **Not checked.** Any positive integer is accepted by the parser. Invalid values will produce errors at Module6. |

### 10.2 Extra Checks (Not in annotations.md)

| Feature | Check | annotations.md |
|---------|-------|----------------|
| Subscript assignment type checking (E12, E13) | `arr[i] = v` requires `arr` to be `list`/`dict`-typed (or `Any`); **only checked when the enclosing function carries ≥1 contract/loop annotation** (the `has_annotations` guard) | Not documented. This is a Python-level semantic check, not a contract-level check. |
| Mutex invariant scope (E11) | Invariant may only reference protected variables | Implied by §5.4 but not explicitly stated in annotations.md §10.1.3. |

### 10.3 Test Coverage for Error Conditions

| Error | Positive Test (passes) | Negative Test (triggers error) |
|-------|----------------------|-------------------------------|
| E1 (`\result` misuse) | 0012 (ensures) | No dedicated negative test |
| E2 (undefined variable) | All passing tests | No dedicated negative test |
| E5 (class invariant scope) | 0006, 0076 | No dedicated negative test |
| E6, E7 (`\valid`/`\separated` type) | 0016, 0017, 0094–0097 | No dedicated negative test |
| E8 (unprotected shared access) | 0250–0253 | 0254 (XFAIL) |
| E9 (missing lock_order) | 0257–0261 | 0255 (XFAIL) |
| E10 (lock_order violation) | 0257–0261 | No dedicated negative test |
| E11 (mutex invariant scope) | 0250–0253 | 0256 (XFAIL) |
| E14 (mutable default arg, R2) | — | 0544 (`# pycsl-expected: FAIL`) |
| W1 (variant/diverges contradiction) | 0049, 0051 | No dedicated negative test |

**Recommendation:** Add dedicated negative tests for E1, E2, E5, E6/E7,
W1. Current negative test coverage for concurrency errors (E8, E9, E11)
is adequate (XFAIL tests 0254, 0255, 0256).

---

## 11. Annotation Well-Formedness (S7 Transcription — TY0)

> **Tier-0 (TY0) transcription.** This section pins the **de facto**
> well-formedness rules for *Python-side* annotations (the `: T` and
> `-> R` parts of a `def`) as of the S7 witness sweep
> (`typing-engagement/ty0-witness/VERDICTS.md`, 13 probed forms). It is a
> transcription of existing behavior, not a design choice. No `src/pycsl/`
> code was modified to produce this section. This section concerns only
> Python-side annotations — the well-formedness of the `#@` *contract*
> directives is covered in §2.

### 11.1 No Name-Resolution Pass on Annotations (GT5 Gap)

```
   (no rule — the judgement is vacuously true)
   ─────────────────────────────────────────────
   Γ ⊢ annotation(x : N) : ok   for any name N, defined or not
```

**Rule (S7 baseline).** As of S7 (TY0), PyCSL performs **no**
name-resolution / forward-reference check on Python annotations at any
pipeline stage. An annotation `x: Foo` (or the stringized form `x: "Foo"`)
is accepted by Module 4 regardless of whether `Foo` is defined in the
module, defined later, defined in another unit, or never defined at all.
The annotation name is **not** validated against `Γ_m`, `Γ_c`, or any
record/variant type registry. # cite: `src/pycsl/core_ir_semantic.py`
(there is no annotation-name-resolution pass in the semantic analyzer);
# cite: `src/pycsl/frontend/Module5_IREmitter.py:1607-1632`
(`_m5_get_type_name` returns whatever `ast.Name.id` it sees without
validating it against any symbol table — see VERDICTS.md §6c).

> **GT5 gap (tagged).** Forward-reference resolution order is **not
> implemented**. The S7 witnesses `s11_fwd_after_def.py` (class defined
> BEFORE the function) and `s12_fwd_before_def.py` (class defined AFTER
> the function) both emit the identical default signature `let f (x: int) :
> int` — the position of the class definition relative to the function is
> irrelevant to PyCSL. The undefined-name witness `s13_fwd_undefined.py`
> (`x: "Baz"`, `Baz` never defined) is silently accepted and lowered to
> `int`, exit code 0. # cite: `src/pycsl/frontend/Module5_IREmitter.py:1607-1632`;
> # cite: `src/pycsl/core_ir_semantic.py`. See VERDICTS.md §6a/§6b/§6c
> for the three forward-reference cases.

This contradicts the assumption (recorded in VERDICTS.md §SURPRISES.5)
that an UNDEFINED annotation name would be `REJECTED`. It is not — it is
`IGNORED`, falling through to the default `int` at emission time (see
translational §N for the lowering table).

### 11.2 `bool` / `tuple` / `-> None` (non-lemma) — Accepted, No Effect

Three annotation forms are syntactically accepted (§11 of the concrete-syntax
reference) and pass Module 4 well-formedness, but have **no static-semantics
effect** — they do not alter the symbol-table type tag in a way that any
Module 4 check consults:

- **`x: bool`** is accepted. `bool` is captured into the symbol table as
  the raw tag `"bool"`, but no `_validate_*` arm in Module 4 reads it, and
  the emitter (translational §N) has no `bool → bool` arm, so the
  annotation is silently dropped to the default `int`. # cite:
  `src/pycsl/frontend/Module5_IREmitter.py:1607-1632` (the tag is captured
  verbatim); # cite: VERDICTS.md §1b.
- **`x: tuple`** (bare) is accepted. Same as `bool`: the raw tag `"tuple"`
  is stored, no Module 4 arm consults it, and the emitter has no bare-`tuple`
  arm (subscripted `Tuple[int, int]` is handled by a separate tuple-return
  refinement path, not the bare-name form). # cite:
  `src/pycsl/frontend/Module5_IREmitter.py:1607-1632`; # cite: VERDICTS.md §3c.
- **`-> None`** on a **non-`#@ lemma`** function is accepted. The
  `return_annotation` is set to `"None"`, but Module 4 only consults this
  for `#@ lemma` ghost discipline (forcing the WhyML return type to `unit`).
  For a regular function, `-> None` does NOT constrain the WhyML return
  type — it stays `int`, and `return None` lowers to the body literal `0`.
  # cite: `src/pycsl/frontend/Module5_IREmitter.py:1757-1801` (the
  `return_annotation` capture); # cite:
  `src/pycsl/core_ir_semantic.py:763-765` (the lemma ghost-discipline
  comment); # cite: VERDICTS.md §4.

### 11.3 Stringized Parameter Annotations — Asymmetry

A stringized parameter annotation `x: "Foo"` is accepted at parse time but
is **not** captured into the parameter's symbol-table entry as a class name.
`_m5_get_type_name` only handles `ast.Name` and `ast.Subscript` annotation
nodes — it has no `ast.Constant` arm — so the parameter's type tag becomes
`"Any"`, which falls through every consumer to the default `int`. The
return-side annotation `-> "Foo"` IS captured as the raw string `"Foo"`
into `return_annotation`, but no Module 6 arm recognizes it, so it also
falls through to `int`. This is an asymmetry between the parameter and
return sides of the same stringized form. # cite:
`src/pycsl/frontend/Module5_IREmitter.py:1607-1632` (no `ast.Constant` arm
in `_m5_get_type_name`); # cite:
`src/pycsl/frontend/Module5_IREmitter.py:1761-1762` (return side captures
the raw string); # cite: VERDICTS.md §5, §SURPRISES.6.

---

## Appendix A. Implementation Cross-Reference

| Module4 Method | Checks | Error IDs |
|---------------|--------|-----------|
| `_validate_contract` | `\result` usage (E1), variable scope (E2), predicate bases (E6, E7) | E1, E2, E6, E7 |
| `_validate_predicate_bases` | `\valid`/`\separated` base types | E6, E7 |
| `_build_function_scope` | Scope construction from args, locals, ghosts | — |
| `_validate_function_contracts` | Orchestrates requires/ensures/assigns/variant checks | E1, E2, E6, E7 |
| `_validate_assigns_regions` | Assigns region base scope and type | E3, E4 |
| `_validate_subscript_assignments` | Array assignment target type | E12, E13 |
| `visit_ClassDef` | Class invariant field scope | E5 |
| `visit_Module` | Module-level concurrency declarations, mutex invariant scope | E11 |
| `_check_protected_in_stmts` | Protected access checker (dispatch table) | E8 |
| `_protected_with` | Nested mutex acquisition, lock order | E9, E10 |
| `_check_shared_access` | Individual shared variable access | E8 |
| `_validate_mutex_invariant_scope` | Mutex invariant variable scope | E11 |

---

## Appendix B. Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-05-20 | Initial release. All 14 error sites in Module3/Module4 documented. Inference rules formalized for all directives and expressions. Gap analysis identifies 5 missing checks and 2 extra checks. |

## Appendix C. Trusted Computing Base

The standard-library models at `src/pycsl_lib/` are consumed as **trusted
stubs** by an importing program's proof: that program is verified against the
model's `#@` contracts, not against CPython. Those contracts are therefore a
trust boundary for the *consumer*.

Critically, the contracts are no longer un-checked assertions. Each model's
bodies are themselves **body-verified within the library** (e.g. the `os`
filesystem model carries zero bare `\trusted`), so a contract a consumer relies
on is discharged by the library's own machine-checked proofs. What remains in the
trusted computing base reduces to:

- the **faithfulness of each model to CPython semantics** — the models are
  hand-written transcriptions anchored to `cpython/Doc/library/*.rst`; a model
  that faithfully implements the wrong behaviour would still be internally
  consistent; and
- the **cited cross-validated axiom families** at irreducibly-opaque kernels
  (each pinned by a named `#@ proof rocq|lean` lemma, cross-checked zero-TCB in
  both Rocq and Lean — see `_AXIOM_REGISTRY` in
  `src/pycsl/module6_whyml/preamble.py`).

This is a strictly smaller TCB than blanket trust in hand-curated contracts. See
`config/skills/pycsl-stdlib-coverage/SKILL.md` for the model-building discipline.
