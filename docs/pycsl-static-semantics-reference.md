# PyCSL Static Semantics Reference

**Status:** Normative  
**Version:** 1.4  
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
| `_module_const_dicts` | top-level `NAME = {"k":"v", …}` (str→str) | `Dict[str, Dict[str, str]]` — single-assignment module constant str→str dict literals; recognized at a `NAME.get(k, default)` site as a chained `string` if-then-else |

**Module-level constants in contracts.** A module-level name bound **exactly once** to an
integer literal (`K_IHDR = 0`, `LIMIT = 8`; `collect_module_constants`) is a *constant*: it is
admitted in `requires`/`ensures`/loop invariants and **resolved to its literal** in both body and
spec emission (`expressions.py::_handle_var_expr`), exactly like a class-body constant
(`self.CAP` → `(64)`, §1.2). So `#@ ensures kinds[0] == K_IHDR` discharges with `K_IHDR ↦ 0`.

A module-level name bound **exactly once** to a **str→str dict literal** (`OP_MAP = {"==":"=", …}`,
all keys AND values plain string literals; `collect_module_const_dicts`) is likewise a *constant
mapping*: a `NAME.get(k, default)` read folds to a faithful chained `string` if-then-else
(`if k = "==" then "=" else … else default`; `expressions.py::_lower_dict_get_call`), the module-level
analog of a class-body scalar constant fold. It requires an EXPLICIT default (2 args); a non-str→str
dict, `.get(k)` without a default, an empty/reassigned dict, or a same-named local (which shadows the
constant) all keep the opaque behavior (fail-closed — never a false value). Drivers: reference locks
`0872` (POSITIVE hit + default), `0873` (NEGATIVE wrong-value twin).

**String-valued `or` / `and` (`_is_string_expr` / `_handle_binop`).** When **BOTH** operands of a
Python `a or b` / `a and b` are `string`-typed, the whole expression is itself `string`-typed —
Python's `or`/`and` return one of the *operands* (not a bool), and a string's truthiness is
non-emptiness. `_is_string_expr` therefore types a both-string `or`/`and` (the `or` right arm may
also be `None`, the `<get> or ""` idiom modeled as `""`) as `string`, so it flows as a `string`
local / return and routes `+`, `.lower()`, etc. through the string ops. In **body** context
`_handle_binop` lowers `s or t` to `(if str_length_op s > 0 then s else t)` and `s and t` to
`(if str_length_op s > 0 then t else s)` (`str_length_op ⊨ String.length`; `String.length` is a
logic symbol, illegal in a program body). The result is `string`-typed: used where a bool/int is
expected it fails closed at Why3 type-check (WL-02 — never a silent coercion). Bool/int operands are
UNCHANGED (the `&&`/`||` connective, `if … then 1 else 0`), and in **spec** context `and`/`or` stay
the boolean connectives. This unblocks self-TCB free functions such as `identifiers.safe_exc_name`
(`return name.lstrip("_") or name`, both operands `string`), whose `or` previously LEAKED to an int
truthiness. Reference locks `0874` (POSITIVE — `or`/`and`, non-empty & empty first operand),
`0875` (NEGATIVE wrong-branch twin); Gate-B spike
`test-suite/corpus/conformance/spikes/string_or_and_spike.mlw` (Z3 discharges every hit + default
and refutes both false twins; Alt-Ergo, lacking a string theory, decides only the empty-operand
duals — best-of-N pipeline is sound either way). No new axiom (`str_length_op` is the pre-existing
length bridge); no `\trusted`.

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
τ(bytes)          = int †     (* IMMUTABLE byte buffer; a LITERAL carries its REAL byte content
                                 (array int built from the exact bytes) so `b"abc"[0]==97` PROVES
                                 and `0<=b[i]<256` is derivable (WL-06b, translational §T.15.7); an
                                 element write `b[i]=v` is REJECTED (Python TypeError). An unknown
                                 PARAMETER carries an IMPLICIT byte-RANGE precondition
                                 `forall i. 0<=b[i]<256` (a type-level guarantee — every real bytes
                                 element is in [0,256); WL-06c, translational §T.15.8), so a range
                                 read PROVES without a user requires; its EXACT byte content still
                                 stays opaque (user `requires` only). *)
τ(bytearray)      = int †     (* MUTABLE byte buffer (element write = sound array mutation); an
                                 unknown PARAMETER carries the same implicit byte-RANGE precondition
                                 (WL-06c). A caller-visible `bytearray` PARAMETER element write is
                                 rejected (frame boundary, §WL-05). *)
τ(dict)           = dict
τ(Dict[K, V])     = dict      (* κ=string ⇒ map string (option ν), native String.(=); else map int *)
τ(set)            = dict      (* sets share the dict model; see translational §T.14.2 *)
τ(Set[T])         = dict
τ(frozenset)      = dict      (* frozensets share the set/dict model *)
τ(FrozenSet[T])   = dict
τ(Tuple[T1, ..., Tn]) = record   (* WL-03/WL-03b: a RECOGNIZED fixed-length Tuple with known
                                 scalar slots (int/bool→int, str→string, float→real — WL-03b)
                                 is a synthesized per-slot record `type pytuple_<tags> =
                                 { field0: τ(T1); …; field{n-1}: τ(Tn) }`, for a PARAMETER and
                                 a record FIELD (not just a locally-constructed/returned tuple).
                                 `t[i]` lowers to the i-th record field (`t[1] : string` for
                                 Tuple[int, str]; `t[1] : real` for Tuple[int, float]) via the
                                 NamedTuple positional-access model — faithfully typed, not the
                                 opaque `int` collapse. A container/class slot, or a
                                 variable-length `Tuple[T, ...]` (Ellipsis), is NOT recognized →
                                 the bare-tuple `int †` row. *)
τ(tuple)          = int †     (* bare tuple — unlike the recognized Tuple[T1, ..., Tn] above *)
τ(C)              = record    (* user-defined class C → a WhyML record of its fields, for
                                 `self`, locally-constructed instances, AND a bare C-typed
                                 parameter whose class is registered — field READ `p.field`, and
                                 a field STORE `p.field = v` on a MUTABLE record is caller-visible
                                 (§WL-05d: `p.field <- v`, inferred `writes`); a PURE (list-element)
                                 record's field store fails closed (‡).
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
τ(Optional[T])    = _union_<scope>_<idx>   (* typing-engagement ty1: Optional[X]
                                   IS Union[X, None]; synthesizes a per-site
                                   variant with arm τ(T) + nullary Arm_None *)
τ(Union[T, None]) = _union_<scope>_<idx>   (* C1b: equivalent to Optional[T] *)
τ(Union[T1, T2,…])= _union_<scope>_<idx>   (* one arm per T_i; Any dropped (GT1);
                                   de-duplicated (C1a); None → nullary ctor *)
τ(A | B)          = _union_<scope>_<idx>   (* PEP 604: same as Union[A, B] (C1) *)
τ(Literal[v1,…,vn]) = base(v_i)            (* typing-engagement ty1: Literal lowers to a
                                   ground `requires { x = v1 \/ … \/ x = vn }`
                                   (L1) — NOT a sum type. base(v_i) is "int" for
                                   int/bool/None, "str" for str. Mixed-kind rejected
                                   (sound stricter-than-S1 — monomorphic params).
                                   De-duplicated (L5a); degenerate Literal[v] (L5b)
                                   → bare `requires { x = v }`. L4a rejects bytes;
                                   L5c rejects nested Literal/Enum. No new IR node. *)
τ(Final[T])        = τ(T)               (* typing-engagement ty1: Final is a write-restriction,
                                   NOT a type refinement (F3 — no narrowing). The
                                   annotation's type is the inner type T. The
                                   write-policy (F1 write-once at declaration /
                                   F2 __init__-only) is NOT a τ rule — it is a
                                   static-semantics write-site check
                                   (`core_ir_semantic._check_final`), reusing HAPPY's
                                   no-write confinement pattern in its degenerate
                                   single-attribute, single-writer form. Bare `Final`
                                   (no slice) → "Any" (no inference). No new IR node,
                                   no IR_VERSION bump, no new VC kind. *)
τ(Final)            = Any                (* bare `Final` (PEP 591 inferred type) → opaque
                                   Any tag; the name carries the write-restriction but
                                   no type refinement (sound: no narrowing claim). *)
τ(NoReturn)         = unit               (* typing-engagement ty1 / 28-0000-typing-spec-4:
                                   `-> NoReturn` (PEP 484) is a CONTROL-FLOW judgment, not
                                   a return-value type. The function never returns normally
                                   (it raises or diverges), so there is no return value —
                                   the WhyML return type is `unit` (the body has no `Return`).
                                   The lowering sets the `is_noreturn` IR flag (IR v1.3,
                                   additive — absent on non-NoReturn functions); Module 6
                                   emits `ensures { false }` (NR1). NR2a (body supports
                                   divergence) is a static-semantics check
                                   (`core_ir_semantic._check_noreturn`); NR3 (dead
                                   successor) is `_check_noreturn_successors`; NR4
                                    (vacuity-gate exemption) is in `pycsl.py`. No new IR
                                    node beyond the `is_noreturn` flag. *)
τ(TypedDict)       = record_name        (* typing-engagement ty2 / 29-1700-typing-spec-5:
                                    `class Point(TypedDict): x: int; y: int` (PEP 589) lowers
                                    at the front-end seam to a record `type_decl` with one
                                    field per declared key. The class name is the record key
                                    (`Point`); Module 6 resolves it to the WhyML record type
                                    `point`. Field access `p["x"]` is a record-field read
                                    (T5); construction `{"x": 1, "y": 2}` is a record literal
                                    (T8). Per-key totality (PEP 655 Required/NotRequired)
                                    and class-level `total=False` wrap a not-required key's
                                    type as `Optional[T]` (reusing the TY1 Union variant
                                    synthesis). The record carries an optional `is_typeddict:
                                    True` field (backward-compatible — defaults False; NO
                                    IR_VERSION bump) gating Module 6's subscript/literal
                                    lowering paths. Static-semantics check
                                    `core_ir_semantic._check_typeddict_access` flags a
                                    non-literal TypedDict subscript index (T5 requires
                                    literal keys). *)
τ(NamedTuple)      = record_name        (* typing-engagement ty2 / 30-1700-typing-spec-6:
                                    `class Point(NamedTuple): x: int; y: int` (PEP 526) lowers
                                    at the front-end seam to a record `type_decl` with one
                                    field per declared key, in declaration order (positional
                                    index is significant — N5 maps `p[i]` to the i-th field).
                                    The class name is the record key (`Point`); Module 6
                                    resolves it to the WhyML record type `point`. Named field
                                    access `p.x` is a record-field read (N4, via the existing
                                    `_handle_attribute_expr` path — a NamedTuple-record-typed
                                    param is in `_record_locals`); positional access `p[0]` is
                                    a record-field read by index (N5,
                                    `_namedtuple_positional_access`); construction
                                    `Point(1, 2)` is a record literal (N6, via the existing
                                    `_call_record_constructor` path — the record carries
                                    `init_params` / `init_body`). A field with a default
                                    (`x: int = 0`, N1b) populates `field_defaults`; a field
                                    without a default is a required positional argument (N7 —
                                    wrong arity is a hard `PYCSL-SEM-NAMEDTUPLE-ARITY` error).
                                    The record carries an optional `is_namedtuple: True` field
                                    (backward-compatible — defaults False; NO IR_VERSION bump)
                                    gating Module 6's positional-subscript lowering path.
                                    Static-semantics check
                                    `core_ir_semantic._check_namedtuple_access` flags a
                                    non-literal NamedTuple subscript index (N5 requires
                                    literal indices) and rejects wrong-arity construction
                                    (N7). *)
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

**§ Flat faithful-element list param (wrong-lowering-to-fix.md §WL-04).** A parameter annotated with
a FLAT `List[str]` / `List[float]` — a list whose element is a faithful NON-INT LEAF — does NOT
collapse its element to `int`. Module5 (`_m5_get_list_flat_elem_whyml`) records the WhyML element type
(`str`→`string`, `float`→`real`) in the IR field `param_list_flat_elem`, and the emitter realizes the
parameter as `array string` / `array real` (`_param_type_str`, right after the nested
`_list_nested_elem` branch). The subscript READ is UNCHANGED (`Array.get` is element-polymorphic), so
`a[i] : string`/`: real` matches a str/float use site (return) and `\result == a[i]` is provable
(drivers `wl04_list_{str,float}_elem_COLLAPSED.py`; locks 0817/0818, NEGATIVE 0819). A flat
`List[int]`/`List[bool]` has NO entry → byte-identical `array int` (int-leaf is the τ-blessed default).
This is the one-level-up analog of the nested `array (seq τ)` model below. A `List[str]`/`List[float]`
LOCAL/RETURN built by a LIST LITERAL is the CONSTRUCTION analog, now covered by **§WL-04a (FIXED)**:
the list-literal lowering (`module6_whyml/expressions.py`, `ArrayLitExpr`) detects an all-string
(resp. all-float) literal and builds `array string`/`array real` with the faithful element values (not
`_coerce_to_int` hashing/truncation); a `-> List[float]` return resolves to `array real` and a
contract `\result[i]` on any `array τ` return lowers to a native `Array.get` (drivers
`wl04a_list_literal_*.py`; locks 0826/0827, NEGATIVE 0828). A MIXED-element literal is REJECTED
fail-closed (**§WL-04g** below); a `List[<record>]` literal is covered by §WL-04c.

**§ MIXED-element list literal — REJECTED (wrong-lowering-to-fix.md §WL-04g, DOCUMENTED SOUND
BOUNDARY).** A HETEROGENEOUS list literal (`[1, "x"]`, `[1, 2.5]`, `[1, Point(2, 3)]`) has NO faithful
`array τ` element type: a Python list is heterogeneous, but a WhyML `array` is HOMOGENEOUS. Every
UNIFORM element shape is already handled by an earlier rule (all-int/bool `array int`; all-str/all-float
§WL-04a; all-equal-arity-tuple `array (t0,…)`; all-record §WL-04c), so a NON-int-faithful element (a
`str` literal, a `float` `Number`, a `Tuple`, or a known-record constructor `Call`) surviving to the
int-coercion FALLBACK proves the literal is MIXED. The int-coercion default is UNSOUND there — a `str`
element hashes to a WELL-TYPED int, so `[1, "x"]` used to build `array int` with `a[1] = 976090257`
(under `PYTHONHASHSEED=0`) and a contract `\result == 976090257` on `a[1]` PROVED, a claim FALSE of
real Python where `a[1]` is the STRING `"x"` (a SEVERITY-1 UNSOUNDNESS, now fixed); a `float`/record
element ill-typed the `array int` (silent Why3 TYPEERR). The static rule (`module6_whyml/
expressions.py::_mixed_literal_reject_kind`, called from the `ArrayLitExpr` fallback) FAILS CLOSED with
a clear `PyCSLSemanticError` naming the offending element kind and directing the user to a homogeneous
list, a `Tuple` (fixed-arity heterogeneous slots), or a record/`@dataclass` (heterogeneous fields). A
homogeneous all-int/bool/expression literal is NOT flagged (byte-identical `array int`). Drivers
`wl04g_mixed_int_{str,float,record}_falsetwin.py` (REJECTED — no false content claim proves),
`wl04g_mixed_int_str_UNSOUND.py` (PROVEN pre-fix → now REJECTED), `wl04g_homogeneous_int_POSITIVE.py`
(PROVEN — no over-rejection); boundary spike `wl04g_mixed_literal_boundary_spike.mlw`; locks 0850
(POSITIVE), NEGATIVE 0851/0852/0853.

**§ Flat RECORD-element list param (wrong-lowering-to-fix.md §WL-04b).** A parameter (and
pass-through return) annotated with a FLAT `List[R]` whose element `R` is a KNOWN record — a user
`@dataclass`/`NamedTuple`, or a recognized `Tuple[T1, …, Tn]` (WL-03's synthesized `pytuple_<tags>`) —
does NOT collapse its element to `int`. Module5 (`_m5_get_list_record_elem`, using the pre-collected
`_m5_record_class_names` + `_m5_tuple_slot_tags`) records the element RECORD class name in
`param_list_flat_elem` and subtracts a record-list param from the 2-D `matrix int` detection; the
emitter resolves it (`_param_type_str` → `array <record>`, registering `_record_array_params`) so
`a[i]` reads a REAL record and `a[i].field` / `a[i][k]` projects the faithful field
(`_handle_attribute_expr` → `(let _rec_ = a[i] in _rec_.<label>)`; `_namedtuple_positional_access` →
the k-th slot). The record leaf is the record-typed analog of the str/float flat leaf. Because Why3
FORBIDS a MUTABLE element inside `array`, a record used as a `List[<record>]` element is emitted PURE
(immutable fields — Module5 `list_element_record_types` drives the preamble `mutable`-drop;
byte-identical for records NOT so used); tuples are immutable, and a field-mutated
dataclass-in-a-list fails CLOSED at Why3 type-check (never a silent unsound update). The projection
comprehension `[p.x for p in a]` over a record source is lowered natively too. Drivers
`wl04b_list_{record,tuple}_elem_COLLAPSED.py` (PROVEN), false-twin `wl04b_list_record_falsetwin.py`
(UNPROVEN); locks 0829/0830 (POSITIVE), NEGATIVE 0831. Residuals (int-collapse / opaque kept): a
record slot of container type. (A `float` slot is now the faithful `real` — §WL-03b below; the
`List[<record>]` LITERAL is now covered by §WL-04c below; a FILTERED record-projection comprehension
by §WL-04d; a `List[<plain-class-with-__init__>]` element by §WL-04e.)

**§ Flat RECORD-element list LITERAL (wrong-lowering-to-fix.md §WL-04c).** The CONSTRUCTION analog of
§WL-04b. A list LITERAL whose elements are ALL full-arity positional constructor CALLS to the SAME
CONTENT-FAITHFUL record (`a = [Point(1, 2), Point(3, 4)]`, `return [Point(1, 2), Point(3, 4)]`) builds
`array <record>` with each element the FAITHFUL record literal (`{ x = 1; y = 2 }`, the constructor
args threaded via `_call_record_constructor`) — NOT the int-coercion collapse. The emitter
(`expressions.py::_expr_to_whyml` `ArrayLitExpr` arm, gated by `_record_ctor_list_elem`) registers the
local as a record-array local (`_track_collection_metadata` → `_record_array_locals`), so `a[i].field`
(local) and `\result[i].field` (on a `-> List[R]` return) project the real field via the same
`(let _rec_ = … in _rec_.<label>)` path as §WL-04b. The element record is emitted PURE (Module5
`_m5_list_literal_record_elem` adds it to `list_element_record_types` after `generic_visit`). FAITHFUL
CONSTRUCTION IS REQUIRED: only a record whose constructor sets EVERY field from a positional param (a
`NamedTuple`, a recognized `Tuple`, an explicit-`__init__` positional class, and — **since §WL-07** — a
`@dataclass`) is threaded. **UPDATE (§WL-07 — a fixed severity-1 unsoundness):** the `@dataclass`-ctor
arg-drop is FIXED — a `@dataclass` now synthesizes its `init_params`/`init_body`, so its literal element
is content-faithful (`[Point(1, 2)][0].x == 1` PROVES; driver `wl07_dataclass_literal_TRUE.py`). Drivers
`wl04c_list_record_literal_COLLAPSED.py` (PROVEN), false-twin
`wl04c_list_record_literal_falsetwin.py` (UNPROVEN); Gate-B spike
`spikes/wl04c_list_record_literal_spike.mlw` (Alt-Ergo AND Z3, no cited lemma); locks 0839 (POSITIVE),
NEGATIVE 0840. Residual (kept fail-closed): a MIXED-record literal.

**§ `@dataclass` / record constructor argument binding (wrong-lowering-to-fix.md §WL-07 — a fixed
severity-1 unsoundness).** A `@dataclass` with no explicit `__init__` has its constructor synthesized by
Python (`__init__(self, f1, …, fn)` binds each field positionally, in declaration order). PyCSL formerly
DROPPED these args (`_collect_init_construction` only walked an explicit `__init__`), so `Point(1, 2)`
built `{ x = 0; y = 0 }` and `Point(1, 2).x == 0` PROVED — FALSE of real Python (fail-OPEN). PyCSL now
synthesizes the dataclass ctor's `init_params`/`init_body` and binds args by POSITIONAL PREFIX (a partial
call keeps trailing defaults). EXPLICIT KEYWORD args (`Point(x=1, y=2)`) — formerly dropped from the Call
IR for EVERY record constructor (plain classes too) — are captured in `CallExpr.keywords` and bound by
name. A `**kwargs` splat stays a documented fail-open residual (unknown runtime values → field default).
SMT spike `spikes/wl07_dataclass_ctor_spike.mlw` (Alt-Ergo AND Z3, no cited lemma); drivers
`wl07_dataclass_{ctor_UNSOUND,ctor_TRUE,kw_UNSOUND,literal_TRUE}.py`; locks 0869 (POSITIVE), 0870 /
0871 (NEGATIVE — the positional / keyword false-`== 0` twins).

**§ FILTERED RECORD-projection comprehension (wrong-lowering-to-fix.md §WL-04d).** A FILTERED
projection comprehension `[p.x for p in a if <cond(p)>]` over a flat `List[<record>]` source `a`
(`array <record>`, §WL-04b) previously fell through `_content_comp`'s record branch to the opaque
`val list_comp (x:int):int`, so a `-> List[int]` return (`array int`) was returned an int → ill-typed
WhyML (TYPEERR — fail-closed but unusable). The RESULT LENGTH is data-dependent
(`0 <= len(result) <= len(a)`), so NO exact length / per-index content law is provable; the sound
faithful law (`expressions.py::_filter_record_proj_law`, a per-instance `list_content_comp_<n>` val) is
the length BOUND `Array.length result <= Array.length src` plus a membership+predicate+projection
existential — for each result index `i` there EXISTS a source index `j` with the record `src[j]`
passing the predicate AND `result[i]` equal to its projected field. Every output came from some
retained input (Python semantics), an honest under-approximation (the source index is lost to
compaction). From it the FILTER CONSEQUENCE transfers to the projected result whenever the predicate
constrains the projected field (`[p.x for p in a if p.x > 0]` yields only positive elements). The
element and predicate are lowered NATIVELY over the record binder (`(src[j]).field`, via
`_push_quant_binder`), the SAME projection a driver's `\result[i]` / `a[j].x` lowers to. A predicate
that does NOT lift to a pure-bool term over the target keeps the SOUND length-bound-only law (still
`array int` — never the prior TYPEERR). Driver `wl04d_filtered_record_proj_COLLAPSED.py` (PROVEN),
false-twin `wl04d_filtered_record_proj_falsetwin.py` (UNPROVEN); Gate-B spike
`spikes/wl04d_filtered_record_proj_spike.mlw` (Alt-Ergo AND Z3, no cited lemma; the length-equality /
per-index false twins NOT entailed); locks 0841 (POSITIVE), NEGATIVE 0842. Residuals (kept opaque /
length-bound-only): a FILTERED TUPLE-SLOT projection (`[t[0] for t in a if …]`, the element is a
subscript not an attribute), and a projection whose element is not a pure-int field term.

**§ Flat PLAIN-CLASS-element list param (wrong-lowering-to-fix.md §WL-04e).** Extends §WL-04b's
recognized-element set to a PLAIN class with an explicit positional `__init__`
(`class Point: def __init__(self, x, y): self.x = x; self.y = y`) — NOT a `@dataclass`/`NamedTuple`/
recognized `Tuple`. Such a class is already emitted as a record `type_decl` by `visit_ClassDef` and
its constructor is CONTENT-FAITHFUL (`Point(1, 2).x` proves `== 1`, not `== 0`), so a flat `List[Point]`
PARAMETER/RETURN resolves to `array <record>` exactly like §WL-04b: `a[i]` reads a REAL record,
`a[i].field` projects the faithful field, and a constructed record STORED into the array element
(`a[0] = Point(5, 6)` → the faithful `{ x = 5; y = 6 }`) reads its written field back. The class is
recognized by `_m5_is_plain_positional_record_class` (pre-`generic_visit` scan of `node.body`,
mirroring the dataclass/NamedTuple pre-scan) — it is added to `_m5_record_class_names`, so the
UNCHANGED `_m5_get_list_record_elem` / `_param_type_str` / `_handle_attribute_expr` §WL-04b threading
applies. Recognition is FAITHFUL-ONLY: a plain `__init__` whose ANY `self.<attr>` is set from a
non-positional-param expression (constant / computation / keyword-only param) is REJECTED (kept at the
`array int` collapse — fail-closed). The element record is emitted PURE (added to
`list_element_record_types`); a field-mutated plain-class-in-a-list has the SAME fail-closed posture as
§WL-04b (the element write is dropped, the post-mutation claim UNPROVEN — byte-identical to the
`@dataclass` path). Additive: a plain class NOT used as a flat `List[R]` element never reaches
`_m5_get_list_record_elem`, so a bigger recognition set changes NOTHING unless a `List[<plain-class>]`
annotation exists (full-corpus byte-diff = 0). Drivers `wl04e_list_plainclass_elem_COLLAPSED.py`
(PROVEN — read law + store-read-back), false-twin `wl04e_list_plainclass_elem_falsetwin.py` (UNPROVEN);
Gate-B spike `spikes/wl04e_list_plainclass_elem_spike.mlw` (Alt-Ergo AND Z3, no cited lemma); locks
0843 (POSITIVE), NEGATIVE 0844. Residual (kept fail-closed): a plain-`__init__` class whose ctor is
NOT purely positional; a record slot of container type (a `float` slot is now the faithful `real` —
§WL-03b below).

**§ Float record/tuple FIELD SLOT (wrong-lowering-to-fix.md §WL-03b).** The WL-03 synthesized per-slot
record and the §WL-04b `List[<record>]` element/record models recognized slot/field types int/bool/str
ONLY, so a `float` field slot collapsed to `int` — an UNSOUND leak that truncated a fractional read
(`t[1]` of a `Tuple[int, float]`, `q.f` / `a[i].f` of a `@dataclass`/`self.f: float` record, holding
`2.5`, read `2`). WL-03b realizes a `float` field slot as the faithful Why3 `real` (τ(float)=real,
no-more-int Stage D): Module5 `_M5_TUPLE_SLOT_TAGS` maps `float`→`real` (so `Tuple[int, float]`
synthesizes `pytuple_int_real = { field0: int; field1: real }`) and `_field_type_from_annotation`
maps a `float`-annotated field to the `real` tag; the preamble record emitter maps that tag to a `real`
field (`_build_witness_str` gets a `0.0` real witness). The projection `t[1]` / `q.f` / `a[i].f` then
reads a `real`; the float comparison routes through Why3 `real` equality (a `2.5` literal on either
side drives the real `=`). Because `real` is a PURE type, a record with a `real` field is legal at an
`array` element position — the §WL-04b PURE-element constraint is preserved. A float field read used
where an int is expected remains a fail-closed real-vs-int TYPEERR (never a silent truncation). Drivers
`wl03b_float_record_slot_COLLAPSED.py` (PROVEN — tuple slot + plain record field + `List[R]` element),
false-twin `wl03b_float_record_slot_falsetwin.py` (UNPROVEN — the int-truncation `== 2.0` claim); Gate-B
spike `spikes/wl03b_float_record_slot_spike.mlw` (7 goals Valid on Alt-Ergo AND Z3, no cited lemma);
locks 0845 (POSITIVE), NEGATIVE 0846. Additive: the corpus has no `float` record/tuple field, so the
full-corpus byte-diff is 0. Residual (kept int-collapse / opaque): a record slot of CONTAINER type
(`Point` with a `List[int]` field) — a mutable container nested in a record nested in an `array` hits
the Why3 mutable-element and `array (array τ)` type-rejection (the nested-list boundary); a sound
pure-`seq`/`map` field representation is future work.

**§ Nested containers (nested-list.md).** A parameter annotated with a container whose ELEMENT
is itself a container — `List[List[τ]]`, `List[Dict[K,V]]`, `List[Set[τ]]`, recursively — does NOT
collapse its element to `int`. Module5 (`_m5_get_list_nested_elem_whyml` → the shared recursive
`_m5_annotation_to_whyml_type`) records the outer list's faithful element type in
`param_list_nested_elem`, and the emitter realizes the parameter as `array (seq τ)` /
`array (map κ (option ν))` (`_param_type_str`). The OUTER list stays `array` (a flat `List[τ]` is
byte-identically `array τ`); the INNER collection is a PURE Why3 type (`seq`/`map`) — Why3 forbids a
mutable element inside `array`. A READ-ONLY nested-annotated parameter is EXCLUDED from the
`matrix int` 2-D detection (`_detect_array_dimensions`). Depth is bounded (≤4); an unknown/too-deep
leaf keeps the scalar `int` default. The subscript READ composes RECURSIVELY to the depth bound
(nested-list.md §8/§9 EXTENSION): `_handle_subscript`/`_nested_access_type` peel one container level
per index level, so `a[i][j][k]` → `Seq.get (Seq.get (a[i]) j) k` (and `len(a[i][j])` → `Seq.length`)
up to depth 4 (drivers 0805 depth-3, 0806 NEGATIVE; depth-4 in the Gate-B spike). A FIFTH level is
beyond the type-recursion cap → the param is not nested-elem → the deep read falls to the opaque
`subscript_get` and does NOT type-check as a faithful read (rejected, never silently accepted;
driver 0807).

**§ In-place inner mutation (nested-list-mutable.md).** A `List[List[int]]` parameter that the body
IN-PLACE INNER-MUTATES — `a[i][j] = v` (an `ArraySet` whose array is itself a `Subscript` rooted at
the param; Module5 `_collect_inner_mutated_params`) — CANNOT use the read-only `array (seq int)` model
(its inner `seq` is immutable). A usage/mutation analysis instead routes such a parameter to the MUTABLE
built-in `matrix int` model: it is dropped from `param_list_nested_elem` and kept in `array2d_params`.
Lowering: `a[i][j]=v`→`Matrix.set`, `a[i][j]`→`Matrix.get`, `len(a)`→`a.rows`, `len(a[i])`→`a.columns`.
The two representations COEXIST — read-only nested lists stay on `array (seq τ)` (ragged-capable); only
an inner-mutated INT-leaf param uses `matrix int` (RECTANGULAR, uniform `columns`). A NON-int-leaf
inner mutation (`List[List[str]]` → `array (seq string)`, immutable `seq`) is REJECTED (a hard
type/verification failure, never silently accepted); `a[i].append(..)` (shape-change) stays opaque;
ragged in-place mutation is out of the rectangular `matrix` model. `\length2d`-contract rectangular
params likewise use `matrix int`.

**§ In-place mutation of a dict/set PARAMETER (wrong-lowering-to-fix.md §WL-05b; UB catalog §7.9).**
An item-mutation `d[k] = v` of a `Dict[...]` parameter — and the set twin `s.add(x)`/`s.discard(x)`/
`s.remove(x)` of a `Set[...]`/`frozenset` parameter — of a **STANDALONE function** is **FAITHFULLY
SUPPORTED**: Python passes dicts/sets BY REFERENCE, so an inner-mutated dict/set param is modelled as a
caller-visible **mutable `ref (map κ (option ν))`** with a sound **`writes {d}`** frame. `d[k]=v` lowers
to `d := map_update_some !d k v`, reads to `!d` / `Map.get !d k` UNIFORMLY, and the mutation ESCAPES to
the caller (the call site passes the bare ref). USAGE-DRIVEN: only an inner-mutated param is promoted; a
READ-ONLY dict/set param keeps the by-value `map …` type (byte-identical). Promotion is decided by a
module-level FIXPOINT (direct item-mutation + transitive param forwarding). A mutating callee should
carry a postcondition on the param post-state (`#@ ensures d["a"] == 5`) for a caller to rely on the
escape. **Still out of scope (REJECTED, code `PYCSL-WHYML-PARAM-COLLECTION-MUT`):** a mutated dict/set
**METHOD** param (its types feed the cross-method call-contract map, which the ref promotion would
desync), the `@mutable_state` param no-op, a PURE-record (list-element) field store and a
subscript/nested-base field store `a[i].f=v` (‡ below, §WL-05d) and nested-list inner mutation
(above). (A MUTABLE-record param field store `p.f=v` and a LIST param element store `a[i]=v` are
SUPPORTED — ‡ below, §WL-05d.) Drivers: 0820/0821/0832/0833 positive (write-read-back + caller-visibility), 0822/0823 positive
(LOCAL), 0834 negative (false post-mutation claim FAILS).

**‡ Classes / records.** A class introduces a record type in `Γ_c` (§1.2): `self`, the
result of a constructor call `C()`, **and** a bare `C`-typed *parameter* whose class is registered
in `_record_types` are all typed as the class's WhyML record (field defaults per `τ`). A record
parameter gives a direct record read `p.field` in both body and
contract (`functions.py::_param_type_str` + the method loop; the old coarsen-to-`int` +
opaque `getattr_<cls>` path is gone for record params). A field STORE `p.field = v` on a MUTABLE
record param is **caller-visible** (wrong-lowering-to-fix.md §WL-05d): it lowers to the native
`p.field <- v` and Why3 infers the `writes {p.field}` frame on the concrete `let`, so the mutation
flows back to the caller (Python objects are by-reference). **Fail-closed:** a record pinned PURE
because it is a `List[<record>]` element is field-immutable (Why3 forbids a mutable element inside
`array`), so its field store is REJECTED (`PYCSL-WHYML-PARAM-COLLECTION-MUT`); likewise a store
through a subscript/nested base (`a[i].f = v`). Before §WL-05d these were silent-drop no-ops — a
severity-1 fail-OPEN (a caller could prove the field UNCHANGED after a real mutation). A **method
call** on a record param (`p.m(args)`) now resolves the
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
(decode is an opaque `int`, the bytes↔str boundary). A `str`-keyed dict/set now keys on the
**native, injective Why3 string** (`dict[str, ν] ~ map string (option ν)`, `String.(=)`), so distinct
keys are provably non-aliasing (cleared-hash.md) — the key type κ = string is inferred for a
parameter/AnnAssign local (`Dict[str, _]`), a string-key literal (`{"a": …}`), string-key USAGE
(`d[k]`/`k in d`/`d.get(k)` with a string literal or `str`-typed key), a string **concatenation** key
(`d[a + b]`, both operands `str` — `str_concat_op` is pinned to left-cancellative Why3 `concat`, so
`a != c ⇒ d[a+b]` non-aliasing is provable; cleared-hash.md residual-close 1a, driver `0795`), AND a
**record FIELD** whose declared type is `Dict[str, ν]` / `Set[str]` / `FrozenSet[str]` (cleared-hash.md
S4). For such a field the WhyML record field is `map string (option ν)` and EVERY field-dict/set op site
(store `self.d[k]=v`, subscript-read `self.d[k]`, `.get`, membership `k in self.d`, set `.add`/`.discard`)
reads and writes the RAW native string key in lockstep — a mismatch would be a WhyML type error.
**Residual κ-unknown / opacity boundary (CLOSED, honest):** a dict whose key the model cannot pin to a
decidable/injective string (an un-annotated field from `{}`, a non-`str` key, or a derived-string key
like `s.upper()` — an opaque `str_upper_op`, genuinely non-injective) keeps the legacy `map int (option ν)`
+ the opaque `str_hash_op` fallback. This is NOT collision-sound and is never claimed so: a distinct-key
non-aliasing claim on such a dict stays UNPROVABLE (cleared-hash.md 1b, driver `0796`,
`# pycsl-expected: FAIL`), and NO false injectivity axiom is placed on `str_hash_op`
(`proof_axiom_allowlist` unchanged). A bare `str→int` coercion (`hash(s)` `0485`, a `.decode()`-result
string equality `0425`) is a SEPARATE opacity — not a dict key (no `map` in its `.mlw`) — and `hash()`'s
opaque `int` result IS the faithful Python semantics.

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

The subscript-projection atom `a[i].field` / `\result[i].field` (cleared-array.md S2,
`SubscriptFieldAccess`) is well-formed where `a` is a subscriptable collection in scope and
`i : int`; it lowers to `Attribute(Subscript(a, i), field)`. In the int-collapsed list model
the element `a[i]` is an `int`, so `.field` denotes the abstract getter `get_field : int → int`
(emitted as a deterministic pure `val function` in spec context — logic-usable and
single-valued). No field-existence check is imposed: the getter is uninterpreted, so the atom is
a sound opaque read; it is the CONSUMER term of a projection-comprehension content law
`\result[k] == a[k].field`.

#### §2.5a `Final[T]` write-policy (typing-engagement ty1 / PEP 591)

```
   x: Final[T] declared at module scope          ─────────────────────────────
                                                  `x = …` outside its declaration ok
   (the declaration is the single permitted write; any function-body write is a reassignment)

   attr: Final[T] declared in class C's body      ─────────────────────────────
   `self.attr = …` textually inside C.__init__     `self.attr = …` ok
   (a write outside C.__init__ — in any other method of C, in a subclass __init__,
    or anywhere else — is a static error)
```

**Rule.** `Final[T]` is a *write-restriction annotation*, not a type refinement (F3 —
the type is `T`). The write-policy is the degenerate single-attribute, single-writer
form of HAPPY's no-write confinement: F1 (module/class-level Final — write-once at the
declaration) and F2 (instance-attribute Final — `__init__`-only writes). The check is a
*syntactic write-site walk* over the IR body (`core_ir_semantic._check_final`), NOT a VC:
a write either is or is not textually inside the allowed perimeter (the declaration for
F1, the declaring class's `__init__` for F2). The front-end collects a per-module
`final_registry` (`program_ir["final_registry"]`, omitted when empty → byte-identical
for Final-free modules); the core walks each `ir["functions"]` body for `Assign`/
`AugAssign` to a registered module-level Final name (F1 violation) or `FieldAssign`/
`FieldAugAssign` to `self.<attr>` for a registered class_attr Final (F2 violation).
`__init__` is a dunder (skipped from `ir["functions"]`), so its write is modelled via
the record's `field_defaults` / `init_body` path, NOT as a function-body statement —
correctly not flagged. Validation: `_normalize_final_annotation` + `_collect_final_registry`
in `Module5_IREmitter`; `_check_final` in `core_ir_semantic`.

**Strictness gap (F2b).** A subclass `D(C)`'s `__init__` write to `self.attr` is NOT
flagged (dunders are skipped from `ir["functions"]`). PEP 591 rejects this; PyCSL does
not. This is a soundness-preserving under-approximation: the write executes at runtime
(FR3 — no enforcement), and no static claim depends on it. See
`typing-engagement/ty1/27-0000-typing-spec-3.md` §6.

#### §2.5b `-> NoReturn` body-supports-divergence (typing-engagement ty1 / PEP 484)

```
   def f() -> NoReturn: return …          def f() -> NoReturn: raise …
   def f() -> NoReturn: x = 1             def f() -> NoReturn: while True: …
   (NR2a violation — normal exit)         (NR2a ok — raises or diverges)
```

**Rule.** `-> NoReturn` (PEP 484) carries the postcondition `false` (NR1 — the
function never returns normally). The body MUST support that claim: every path
must raise or diverge. `core_ir_semantic._check_noreturn` enforces two
conservative sound conditions (stricter than S1 is permitted):

- **No `Return` statement** — any `Return` (with or without a value) anywhere
  in the body is a normal-exit path → `PyCSLSemanticError` (code
  `PYCSL-SEM-NORETURN`). Even a `Return` inside a provably-dead branch is
  rejected (sound — a dead `Return` indicates a logic error).
- **At least one `Raise` or diverging construct** — a body with no `Raise` and
  no `While`/`For`/`CriticalSection`/`Call` provably falls off the end (a
  normal exit) → rejected.

Why3 provides defense-in-depth: if a normal-exit path slips past this check,
the `ensures { false }` VC fails at proof time. Validation: `_build_function_ir`
in `Module5_IREmitter` (sets `is_noreturn`); `_check_noreturn` in
`core_ir_semantic`.

**NR3 (dead successor).** `_check_noreturn_successors` flags any statement
following a bare-expression `Call` to a NoReturn function as dead code (the
callee's `false` postcondition makes the continuation unreachable). This is
the dead-branch class `soundness-issue.md` §7 identifies — a dead branch proves
`false` SOUNDLY, which is NOT vacuity.

**NR4 (vacuity-gate exemption).** The non-vacuity gate
(`pycsl.py:_run_vacuity_gate`) exempts declared-NoReturn functions from the
vacuity probe: their `false` postcondition is the SPEC (NR1), not a vacuity
signal. The exemption is keyed on the IR `is_noreturn` flag (from the
`-> NoReturn` annotation), NOT on the inferred postcondition — the latter
would exempt every genuinely-vacuous function, defeating the gate.

**The non-vacuity gate is ON BY DEFAULT (fail-closed).** After a file verifies,
every body-bearing function is re-probed with an injected `ensures false`
(`split_vc`, one goal per NORMAL-EXIT path); a function VACUOUS on ALL its exits
(its assumed context is logically inconsistent, so every postcondition —
including a false one — discharges for free) FAILS the run, naming the
function. This closes the SMT nonlinear-integer-division vacuity soundness hole
(`non-lin-int-div-fixed.md`; `csys-vacuity-investigation/ROOT-CAUSE.md`): a VC
whose hypotheses the solver turns inconsistent can no longer certify a false
`ensures` as green. Opt out with `--no-check-vacuity` (fast dev / byte-diff
sweeps; `--no-proof` also skips it, so the gate never runs on the byte-diff
path). **Two exemptions** — a function whose SOUND green is expected-vacuous on
its unreachable normal exit: declared `-> NoReturn` (`is_noreturn`, NR1/NR4)
AND `#@ \diverges` (the IR `diverges` flag — a diverging function satisfies any
postcondition). The exempt-set is computed where the IR is in scope
(`_run_pipeline`) and passed on `args._vacuity_exempt` to the gate in
`_run_proofs`.

#### §2.5c `TypedDict` literal-key access (typing-engagement ty2 / PEP 589)

**Rule.** A subscript `p["x"]` on a TypedDict-record-typed variable `p` (PEP
589) requires the index to be a string *literal* naming a declared field (T5).
A non-literal index or an unknown key is a static error (Why3 rejects the
lowered record-field read at type-check). `core_ir_semantic._check_typeddict_access`
walks the body IR for `Subscript` nodes whose receiver is a TypedDict-record-
typed variable and flags a warning when the index is non-literal, surfacing
the issue earlier than the Why3 type error.

**No GT gap** is tagged for the literal-key check — it is a precision concern
(a non-literal key cannot be a record-field read), not a soundness gap. The
runtime plane (plain-dict subscript) is unaffected (R5/R6, D1 no-blend).

#### §2.5d `NamedTuple` literal-index access & arity (typing-engagement ty2 / PEP 526)

**Rule (N5 — literal-index access).** A subscript `p[i]` on a NamedTuple-
record-typed variable `p` (PEP 526) requires the index `i` to be an integer
*literal* in the range `[0, nfields)` (N5). A non-literal index or an
out-of-range index is a static error (Why3 rejects the lowered record-field
read at type-check — an out-of-range index falls through to the opaque
`subscript_get` path, which Why3 rejects because the record type is not
`int`). `core_ir_semantic._check_namedtuple_access` walks the body IR for
`Subscript` nodes whose receiver is a NamedTuple-record-typed variable and
flags a warning when the index is non-literal, surfacing the issue earlier
than the Why3 type error.

**Rule (N7 — wrong-arity construction).** A call `Point(...)` to a NamedTuple
constructor (PEP 526) requires the number of positional arguments to be in
the range `[min_arity, nfields]`, where `min_arity` is the count of fields
WITHOUT a default (N1b — a field with a default makes the trailing positional
argument optional). A wrong-arity call is a hard static error:
`core_ir_semantic._check_namedtuple_access` walks the body IR for `Call`
nodes to a NamedTuple constructor and raises `PYCSL-SEM-NAMEDTUPLE-ARITY`
when the call arity is wrong. This mirrors the TypedDict GAP-001 missing-key
rejection: the shared `_call_record_constructor` default-fills missing args
soundly but imprecisely, so this check makes the wrong-arity case a static
error (N7), not a silent default-fill.

**No GT gap** is tagged for the literal-index or arity checks — they are
precision concerns, not soundness gaps. The runtime plane (plain-tuple
subscript / plain-tuple construction) is unaffected (R6/R7, D1 no-blend).

#### §2.5e `@overload` guarded contract family (typing-engagement ty2 / PEP 484)

**Rule (O1 — overload family recognition).** A function `f` is an overload
family iff there exist N ≥ 1 `@overload`-decorated stubs
`@overload def f(p_i: T_i) -> R_i: ...` (each with a literal `...`/`pass` body,
O1a) followed by exactly one non-`@overload` implementation `def f(p) -> R:
<body>` (O1b), all at the same scope and same name `f`. A stub with a non-`...`
body is NOT an overload stub (it is a regular decorated function). The stubs'
declaration order is the resolution order (first match wins). `Module5_IREmitter.
_is_overload_stub` recognizes the family at the `visit_FunctionDef` seam.

**Rule (O2/O3 — guard synthesis + guarded postcondition).** For each overload
stub `i` with parameter `p_i: T_i`, the static plane synthesizes a **guard**
`G_i = isinstance(p_i, T_i)` (the same metatype-tag vocabulary
`_handle_isinstance` uses — `(subtag (typeof p_i) <T_i tag>)`, a WhyML bool).
For each stub `#@ ensures Q_i`, a **guarded postcondition** `ensures { G_i ==>
Q_i }` is synthesized (`_synthesize_overload_guard`) and attached to the
implementation's `contracts.ensures`. A stub with no `#@ ensures` contributes
no guarded clause (its guard is still synthesized for selection but adds no
VC). The `==>` implication is parsed by `Module2_Parser` IMPL_OP and lowered to
WhyML `->` by `identifiers.py`.

**Rule (O4/O5 — type-based call-site selection, NO-BLEND).** At a call site
`f(v)` where `v` has static type `T_v`, the active overload is the first stub
`i` (in declaration order) whose guard `G_i` is satisfied by `T_v`. The
selection is a **type-based VC** — discharged by proving `T_v` assignable to
`T_i` (native Why3 type-checking when the implementation's parameter is typed),
NOT by any runtime check. A lowering that let the implementation's runtime
`isinstance` dispatch SATISFY the static selection obligation would blend the
planes (D1). The guard is a WhyML spec formula over the parameter's type tag
(decided from Γ's τ); the runtime `isinstance` is body code (a value check) —
different WhyML terms.

**Rule (O6 — implementation proves the family).** The implementation's single
body proves EACH guarded postcondition `G_i ==> Q_i` under the guard
assumption `G_i`. This is the "guarded contract family proved against the
single implementation" (TY2 hard rule). One Why3 VC per guarded postcondition.

**TY2 scope restriction (divergence-by-strictness).** For the guard `G_i` to
be a **decided** type judgment (not a symbolic `typeof_op` placeholder), the
implementation's parameter must carry a type annotation. PEP 484 does not
require the implementation to be annotated, but PyCSL's sound lower bound may
be stricter than S1 (§0). An unannotated implementation yields a symbolic
guard (sound but imprecise — the call-site selection VC is discharged only
when the body unconditionally establishes the postcondition).

**GT7** (analogous, NOT a new code) — D1 documents the `isinstance`-dispatch
no-blend trap: the static O4/O5 type-based-selection obligation must NOT be
discharged by any runtime `isinstance` check in the implementation (R4 is
value dispatch, not type judgment). Tagged in the report as a
`no_blend_overload_isinstance` note.

#### §2.5f `Protocol` contract interface & conformance (typing-engagement ty2 / PEP 544)

**Rule (P1 — protocol declaration).** `class P(Protocol): ...` declares a protocol
type — a contract interface (a named collection of method contracts).
`Module5_IREmitter._is_protocol_class` recognizes the family at the `visit_ClassDef`
seam (bare head name `Protocol` or dotted `typing.Protocol` in `node.bases`).
`_emit_protocol_interface` synthesizes a marker record (`is_protocol: True`, no
fields) + each member as an `abstract: True` function (a bodyless `val` with its
contract — the refinement target, P1a).

**Rule (P1b — `@runtime_checkable` is a runtime marker).** `@runtime_checkable`
decorates a protocol to opt it into runtime `isinstance`/`issubclass` support. It
has NO static-plane effect: a non-`@runtime_checkable` protocol has the SAME static
conformance semantics as a `@runtime_checkable` one. The static plane IGNORES
`@runtime_checkable` (it is a runtime-plane concern).

**Rule (P2/P4 — per-method behavioural refinement, the load-bearing rule).** A
class `C` **conforms to** protocol `P` iff, for every member `m` of `P`, `C` has a
method `m` whose contract **refines** `P.m`'s contract: `requires(C.m) ⟹
requires(P.m)` (weaker-or-equal pre), `ensures(P.m) ⟹ ensures(C.m)` (stronger-or-
equal post), `assigns(C.m) ⊆ assigns(P.m)` (narrower frame). Conformance is
declared via the class-level directive `#@ conforms_to P`; for each member `m` of
`P` that `C` provides, `_populate_protocol_conformance` records an `(C__m, P__m)`
override pair in the EXISTING `overrides` IR list. `--check-behavioral-subtyping`
emits the per-method refinement goal `forall self: C, .... ((pre_P -> pre_C) /\\
(post_C -> post_P))` — the per-method contract-refinement VC. This is a per-method
VC (NOT a presence check): it is discharged by Why3/SMT from the two contracts.

**Rule (P3 — non-conformance rejected).** A class `C` that lacks a member of `P`
raises a static error (`PYCSLSEMANTICERROR`); a member whose contract does NOT
refine `P.m`'s contract makes the refinement goal unprovable, so verification
FAILS. A conformance declaration against a non-Protocol class also raises.

**Rule (P5 — NO-BLEND, the canonical GT7 trap).** The static conformance obligation
(P2/P4) is a per-method contract-refinement VC — a WhyML formula over the two
contracts. It must NOT be discharged by any runtime `isinstance`/`hasattr` check.
The runtime `@runtime_checkable` isinstance (R3) checks attribute PRESENCE ONLY —
it is a value check on the object, NOT the contract-refinement type judgment. The
two are carried as SEPARATE facts: the static conformance VC is discharged by
contract refinement; the runtime isinstance is discharged by the object's attribute
presence at run time. A lowering that let the weak runtime presence check SATISFY
the static conformance obligation would blend the planes — this is the GT7
canonical failure.

**TY2 scope restriction (divergence-by-strictness).** PEP 544 conformance is
structural and implicit; PyCSL's TY2 scope requires the explicit `#@ conforms_to P`
directive. An implicit structural search would require whole-program analysis
(every class against every protocol), which is outside PyCSL's per-module
verification model. The explicit directive makes conformance a discharged per-method
VC within the module.

**GT7** (THIS IS the canonical GT7 trap, not an analogue) — D1 documents the
`@runtime_checkable` presence-vs-conformance divergence: the static P2/P4
per-method contract-refinement obligation must NOT be discharged by any runtime
`isinstance`/`hasattr` presence check (R3 is attribute presence, a value check,
NOT the contract-refinement type judgment). Tagged in the report as a
`no_blend_protocol_presence` note.

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

### 3.5 IR-node ADT recognition (the `emit_ir` sum — tier3-p1 expr family)

_Realizes the Phase-0 spike `tier3_ir_node_adt_spike.mlw` in the emitter
(`triage-ranked-tcb-tier3.md` T3.1). This is a Module-6 WhyML-emission typing
rule, not an IR-schema change: `IR_VERSION` stays `1.4`, the goldens are
unchanged._

A parameter or local whose static type is an IR-node base name
(`τ(x) ∈ {ExprIR, StmtIR, IRNode, ContractExprIR}`) has WhyML type `emit_ir`,
the pure algebraic sum declared in the preamble ADT theory. Its reflection is
typed by the fixed projection classes:

| reflection | result type | note |
|---|---|---|
| `x.get("type")` | `string` (via `kind_of`) — OR the bool `(is_binop x)` when compared `== "BinOp"` | the equality against a constructor-kind literal is the DISCRIMINANT (§T.16); it is a well-typed `bool`. |
| `x.get("op")` | `string` (via `op_of`) | a LEAF projection. |
| `x.get("left")` / `x.get("right")` | `emit_ir` (via `left_of` / `right_of`) | a SUB-NODE projection — distinct result type-class from a leaf. A sub-node result feeds a recursive call (which expects `emit_ir`); a leaf result feeds a `string` context. A type mismatch (e.g. using `left_of x` where an `int` is expected) fail-closes at Why3 L3-type-check — never a silent coercion. |

**Termination (T3.1.4).** A function that is recursive over its `emit_ir`
parameter, and carries no explicit `#@ \variant`, is well-formed only if it
terminates; the emitter supplies the obligation by injecting
`variant { size x }` on the ADT subtree measure. The guarded size-decrease
lemmas (`is_binop e → size (left_of e) < size e`) and `size e ≥ 1` discharge it
with no axiom. An unrecognized node kind / an `Opaque` node is fail-closed (no
faithful projection is fabricated).

**Gate.** The ADT theory is emitted only when the module uses an IR-node type
(or has a `@mutable_state` class); every other program is unaffected
(byte-identical emission).

**Completed EXPR family (increment 3).** The discriminant rule generalizes beyond
`BinOp` to the whole fixed-arity expr family: `x.get("type") == "K"` types as the
`bool` `(is_K x)` for `K ∈ {Var, Number, String, Subscript, Attribute, Call,
MkTuple, FieldGet, BinOp}`, each `is_K` a match-based constructor test satisfying
`is_K x ↔ kind_of x = "K"` on every real node. A sub-node projection
(`x.get("value")`/`.get("index")`/`.get("object")`/`.get("left")`/`.get("right")`)
types as `emit_ir` and may feed a recursive call; a leaf projection
(`x.get("name")`/`.get("attr")`/`.get("func")`/`.get("op")`/`.get("field")`) types
as `string`. The `FieldGet` object read is a LEAF `string` (`fgobject_of`), in
contrast to the `Attribute` object read which is a SUB-node (`object_of`) — the
type-class distinction (`string` vs `emit_ir`) is enforced at Why3 L3-type-check,
never a silent coercion. Termination for a recursion guarded by any of these
discriminants is discharged by the corresponding guarded size-decrease lemma
(`is_sub e → size (svalue_of e) < size e`, etc.). The list-shaped kinds
(`ArrayLit`/`SetLit`/`Tuple`/`DictLit`) remain on the `kind_of` string path
(no structural `list emit_ir` projection yet); `Tuple` additionally cannot use
`is_tuple` because the ADT's tuple ctor reports `kind_of = "MkTuple"`.

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

---

## §S.TY3 — TypeVar / Generic static semantics (PEP 484 + PEP 695)

The static plane treats a generic `C[T]` as a **template**: the declaration is
NOT itself a proof obligation. The obligations arise at each CONCRETE
instantiation `C[int]`, where `T` is replaced by the concrete type and the
whole class is specialized. This is **whole-module monomorphization**. *Cites
S1 (the typing spec); PEP 484/695 (S2) yield to S1 on conflict. See the
two-plane spec `typing-engagement/ty3/typevar-generic-twoplane-spec.md`.*

### §S.TY3.1 — COLLECT (G2, closed-world)

A generic is discharged by scanning the closed module for concrete
instantiation sites (`C[int]()` calls, `x: C[int]` annotations). Each
`(generic, concrete-type)` pair is one instantiation site. An **un-instantiated**
generic emits NO specialized copy (G5) — only its declaration is checked.

### §S.TY3.2 — EMIT (G3, name-mangled substitution)

For each `(C, A)` pair, emit ONE specialized copy: `C` → `C_<A>` (e.g.
`Stack_int`); `T` substituted by `A` in field types, signatures, and contract
clauses; methods `C__m` → `C_<A>__m`. The copy is an ordinary monomorphic
class. The ORIGINAL generic decl + methods are REMOVED (replaced by the copies).

**No-blend (G3a, D1):** an un-instantiated generic carries NO per-instance
theorem. Claiming `Stack.pop` returns `int` when no `Stack_int` was emitted is a
defect — the static plane refuses the claim.

### §S.TY3.3 — BOUNDS (G4, instantiation-time obligation)

A `T: B` bound makes each instantiation `C[A]` admissible iff `A` is a subtype
of `B`. Today PyCSL checks **invariantly** (A must be exactly B) — stricter
than S1, legitimate divergence-by-strictness. Reject code: `PYCSL-TY3-BOUND`.

### §S.TY3.4 — Un-instantiated generic (G5, declaration-only)

A generic never instantiated stays as declaration-only: its method bodies are
NOT lowered to WhyML, NO VC is generated. The soundness report records it
**Ignored/GT8**.

### §S.TY3.5 — Loud-fails (GT3, GT4)

- **GT3** (`PYCSL-TY3-GT3`): `ParamSpec`/`TypeVarTuple` are schema-only — a
  generic using them is rejected.
- **GT4** (`PYCSL-TY3-GT4`): polymorphic recursion — a generic function `f[T]`
  that calls `f[T]()` (with the TypeVar itself) does not terminate under
  monomorphization; rejected.

### §S.TY3.6 — Variance (GT2, deferred)

Co/contravariance is NOT interpreted in TY3's first delivery. Instantiations
are checked invariantly (§S.TY3.3). Divergence-by-strictness, recorded (GT2).

### §S.TY3.7 — `Any` refusal (GT1)

`Any` never instantiates a `TypeVar` (the consistency relation is deliberately
unsound). `C[Any]` is rejected with `PYCSL-TY3-GT1`.

### §S.TY3.8 — `Callable` function-type obligation (PEP 484)

A parameter `f: Callable[[A1, ..., An], R]` carries a **function-type
obligation** (C1): `f` is a value of function type. The proof obligations arise
at the CALL SITE on `f` and are discharged by Why3's own typecheck at the
application (the existing `(f a1 ... an)` lowering):

- **C2 (arg-type match).** A call `f(a1, ..., an)` requires each `ai` to have
  type `τ(Ai)` positionally; a mismatch is a static WhyML type error (reject
  code: the Why3 typecheck diagnostic). *Cites S1, PEP 484 (S2).*
- **C3 (result type).** The call yields a value of type `τ(R)`; a declared
  return annotation that disagrees is a static WhyML type error. *Cites S1.*
- **C4 (no value postcondition from a bare Callable).** A bare `Callable`
  guarantees only arg/result TYPES, not a specific return VALUE. A postcondition
  asserting a value of `f(...)` (e.g. `ensures \result == x + 1` where the body
  is `return f(x)`) is **unprovable** — `f` is an opaque function value. This is
  sound: the static plane refuses a value theorem the function-type does not
  justify. A `\trusted` shortcut is refused (NO-BLEND, §S.TY3.9).
- **C5 (scope limit — stricter than S1, sound).** Only `int`/`bool`/`str`/
  `float` and record/variant class names are admissible as Callable arg/return
  types. `bytes`, `list`/`dict`/`set`, `Any` (GT1), a nested `Callable`, and
  `Callable[..., R]` (ellipsis / `ParamSpec`-derived, GT3) are rejected with
  `PYCSL-TY3-CALLABLE-SCOPE`. Divergence-by-strictness, recorded.

### §S.TY3.9 — `Callable` no-blend (D1, the keystone)

The static function-type obligation is a **proof-time judgment** (a WhyML arrow
parameter + Why3 typecheck). The runtime `callable(x)` / `isinstance(x,
Callable)` is a **presence check** (signature-agnostic). The static signature
obligation must NOT be discharged by the runtime presence check — the
coherent-and-wrong trap, Callable edition. Defended by the independence of the
spec-agent and conformance-agent from the core-agent (§4.2 of the overview).

