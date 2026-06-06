# Grow the Phase B/C corpus to nine diverse data types

**Status:** ⚠️ **Historical document.** This plan uses the
colon-separated `#@ proof rocq:` / `#@ proof lean:` directive form
that was removed from the language on 2026-05-27. The current
directive syntax is `#@ proof <prover> <qualname>` (space-separated,
load-bearing). The text below is preserved as historical context; do
not re-execute its steps.

Date: 2026-05-26
Scope: Extend `rocq2pycsl` + `lean2pycsl` + `pycsl_bridge` so the cross-prover loop works for **lists, tuples, dicts, strings, arrays, booleans, ghost_list, ghost_set, and class instances** — eight primitive/abstract data types plus class instances.

## Context

The Phase B/C golden corpora today hold only `double` per tool (plus an empty `gcd/` placeholder in `rocq2pycsl`). All entries operate on `int` parameters. `rocq2pycsl-plan.md §8` and `lean2pycsl-plan.md §8` explicitly mark *inductive types and class instances in theorem statements* as **unsupported** in the converter — that's the gap.

PyCSL itself already supports all nine data types: `list`/`array` parameters, `tuple2/3/4`, `ghost_dict`, `string`, native `bool`-as-0/1 encoding (per the `pycsl-annotate/SKILL.md §3` rule that bare `True`/`False` are forbidden in contracts), `ghost_list`, `ghost_set`, and `#@ class invariant`. The reference test suite has 95 tests exercising these. The Phase B converters lag behind.

**Naming note:** "Sets" in PyCSL is the `ghost_set` ghost type — no separate Set type exists. This plan therefore treats Sets and `ghost_set` as a single fixture (`set_union_eq`).

The bar per fixture: bridge produces RECONCILED status for the paired Rocq + Lean fixture, the emitted Python discharges all obligations under Why3 + Alt-Ergo, and a manifest entry records the pairing.

---

## Recommended approach

Six phases. Phases 1–4 lay shared groundwork; Phase 5 ships eight primitive/abstract-type fixtures; Phase 6 closes class-instance support which warrants its own phase due to emitter scaffolding.

### Phase 1 — Shared IR additions (`pycsl_emit`)

Add the language-agnostic vocabulary that Rocq and Lean translators will both target. Pattern: mirror how `Divides` already lives in the IR.

**New nodes in `src/pycsl_emit/ir/nodes.py`:**

*Lists / arrays / tuples / dicts / strings:*

| Node | Purpose | PyCSL surface emission |
|---|---|---|
| `Length(arr)` | `\length(arr)` — used for both `list` and `array` types | `\length(<arr>)` |
| `Nth(arr, i)` | `arr[i]` indexing in contracts | `<arr>[<i>]` |
| `Tuple(args)` | Tuple literal | `\mktuple(<args>)` (ghost) or `(<args>)` (return-type) |
| `Proj(t, i)` | i-th projection of a tuple | `\proj(<t>, <i>)` or `<t>[<i>]` |
| `MapGet(d, k)` | Dict lookup | `\map_get(<d>, <k>)` |
| `MapSet(d, k, v)` | Dict insert/update | `\map_set(<d>, <k>, <v>)` |
| `MapEmpty()` | Empty dict | `\empty_map` |
| `HasKey(d, k)` | Dict key membership | `\has_key(<d>, <k>)` |
| `StrConcat(a, b)` | String concatenation | `<a> ^ <b>` |
| `StrLength(s)` | `\str_length(s)` | `\str_length(<s>)` |
| `StrSub(s, lo, hi)` | Substring `[lo, hi)` | `\str_sub(<s>, <lo>, <hi>)` |
| `StrLit(value)` | String literal | `"<value>"` (PyCSL surface) |

*Class instances:*

| Node | Purpose | PyCSL surface emission |
|---|---|---|
| `FieldGet(obj, name)` | Object field access | `<obj>.<name>` |
| `ClassInstance(cls)` | Marker for "this is an instance of class `cls`" (carried on Var so the translator can decide whether to emit field access vs name lookup) | (no direct surface; used as a type tag on Var) |

*ghost_list:*

| Node | Purpose | PyCSL surface emission |
|---|---|---|
| `ListNil()` | Empty ghost list | `\nil` |
| `ListCons(head, tail)` | Prepend to ghost list | `\cons(<head>, <tail>)` |
| `ListLen(l)` | Length of ghost list — distinct from `Length` for arrays (uses Why3's `list.Length`) | `\list_length(<l>)` |
| `ListAppend(l1, l2)` | Concatenate two ghost lists | `\append(<l1>, <l2>)` |
| `ListNthAt(l, i)` | i-th element (no default — `\nth` per skill warning: head-tracking only, no `\mem`) | `\nth(<l>, <i>)` |

*ghost_set (a.k.a. Sets — these are the same in PyCSL):*

| Node | Purpose | PyCSL surface emission |
|---|---|---|
| `SetEmpty()` | Empty ghost set | `\set_empty` |
| `SetAdd(s, x)` | Add element | `\set_add(<s>, <x>)` |
| `SetRemove(s, x)` | Remove element | `\set_remove(<s>, <x>)` |
| `SetMem(x, s)` | Element membership | `\set_mem(<x>, <s>)` |
| `SetUnion(a, b)` | Union | `\set_union(<a>, <b>)` |
| `SetInter(a, b)` | Intersection | `\set_inter(<a>, <b>)` |
| `SetDiff(a, b)` | Difference | `\set_diff(<a>, <b>)` |
| `SetSubset(a, b)` | Subset relation | `\set_subset(<a>, <b>)` |
| `SetEq(a, b)` | Set equality | `\set_eq(<a>, <b>)` |

**Booleans** require no new IR node. PyCSL's contract grammar forbids bare `True`/`False`; `pycsl_emit.ir.Lit(True)` already renders as `1 == 1` and `Lit(False)` as `0 == 1` (`src/pycsl_emit/translator/render.py`). Boolean parameters are encoded as 0/1 integers in PyCSL contracts; the translator (Phases 3 & 4) auto-injects `requires b == 0 or b == 1` per bool-typed parameter and maps boolean operators (`andb` → `b1 * b2`, `orb` → `b1 + b2 - b1*b2`, `negb` → `1 - b`) onto existing `BinOp`/`UnaryOp` nodes.

**Arrays** also require no new IR node — PyCSL's `array` ghost type has the same surface ops as `list` (`\length`, `arr[i]`). The translator records the source-side annotation as `ty="array"` and the emitter handles it identically to `list`. The distinction matters for Rocq/Lean grammar recognition (Lean's `Array` is a separate type from `List`) but not for the IR.

**Files to edit:**
- `src/pycsl_emit/ir/nodes.py` — add the new dataclasses
- `src/pycsl_emit/ir/pretty.py` — `_lines` arms for each
- `src/pycsl_emit/ir/json_io.py` — `to_dict` / `from_dict` arms (mandatory: the bridge round-trips IR through disk)
- `src/pycsl_emit/translator/render.py` — `_render` arms emitting the PyCSL surface forms above

**Tests:** extend `src/pycsl_emit/tests/ir/test_pretty.py`, `test_json_io.py`, and `src/pycsl_emit/tests/translator/test_render.py` — one assertion per new node, plus round-trip coverage.

### Phase 2 — Canonicalizer rules (`pycsl_bridge`)

Without canonicalization, `Length(arr)` from Rocq (`length l`) and `Length(arr)` from Lean (`l.length`) might differ in surface AST shape even though semantically identical.

**Files to edit:**
- `src/pycsl_bridge/canonicalizer/normalize.py` — recurse through the new nodes; rewrite common surface variants to canonical form:
  - `Nth(arr, i)` produced from Rocq's `nth i l 0` (default-zero) ≡ Lean's `l[i]!` (panic-on-OOB)
  - `Proj(t, 0)` ≡ `fst t` (Rocq) ≡ `t.fst` (Lean); same for `Proj(t, 1)` ≡ `snd`/`.snd`
  - `MapGet(d, k)` ≡ Rocq `find k d` (FMaps) ≡ Lean `d.find? k`
  - `StrConcat` is right-associative in canonical form (matches WhyML's `concat`); Rocq's `(a ++ b) ++ c` and Lean's `(a ++ b) ++ c` both rewrite to `a ++ (b ++ c)`
  - `StrLength` over `StrConcat`: do **not** rewrite to `\str_length(a) + \str_length(b)` (non-conservative; let the contract express it explicitly when wanted)
  - `FieldGet(obj, "x")` canonicalizes to itself — Rocq's record projection `r.(x)` (or `x r`) and Lean's `r.x` both produce `FieldGet(r, "x")`
  - **ghost_list ops:** `ListCons` is **not** AC (the order of `cons` is meaningful); `ListAppend` is associative — rewrite to right-associative form to match Why3's `concat`. `ListLen(ListAppend(a, b))` → `ListLen(a) + ListLen(b)` is **safe** (Why3 `Length_Cons` axiom guarantees it) and is the standard idiom recommended in `invariant-writer/SKILL.md §"Ghost Variables in Loop Invariants"`.
  - **ghost_set ops:** `SetUnion`, `SetInter` are AC — flatten and sort by structural hash (the existing AC handler from `Divides`'s era handles this once we register them as AC ops). `SetSubset(a, a)` → `Lit(True)`; `SetEq` symmetric, normalize operand order.
  - **Boolean op normalization:** `1 - (1 - b)` → `b`; `b * 1` → `b` (already covered by existing AC simplification); `b * b` → `b` for known-boolean `b` is **not** added because the canonicalizer can't infer "b is boolean" without type tracking
- `src/pycsl_bridge/tests/canonicalizer/test_normalize.py` — assertion per equivalence

### Phase 3 — `rocq2pycsl` grammar + translator extensions

Extend the Lark grammar to recognize list, tuple, dict, string, array, bool, ghost_list (`list T` used as a ghost), ghost_set (`T -> bool` characteristic-function representation), and record types in binders and theorem statements; extend the Gallina→IR translator to lower the new constructs to the IR nodes from Phase 1.

**Files to edit:**

- `src/rocq2pycsl/extractor/gallina_grammar.lark` — extend `type_expr` to accept:
  - `list <type>` (Rocq's `Coq.Lists.List` — used for both list parameters AND ghost_list)
  - `array <type>` or `Vector.t <type> <expr>` (Coq's array library; document the chosen surface form in the file header)
  - `<type> * <type>` (Coq pair, prod)
  - `<type> -> option <type>` (Coq idiom for finite maps; cleaner than FMaps)
  - `<type> -> bool` (Coq idiom for sets via characteristic function — cleaner than `Coq.MSets`)
  - `string` (Coq's `Coq.Strings.String`)
  - `bool` (Coq's `Init.Datatypes.bool`)
  - **Record types** for class instances: a record type appears in a binder as a single `CNAME` (the record's name). No new type production needed; the translator dispatches at lowering time on whether the type name refers to a known `Record` declaration.
  - Add productions for string literals: `STRING_LIT: "\"" /[^"]*/ "\""` at the atom level
- `src/rocq2pycsl/extractor/lark_backend.py` — `_AstBuilder` arms for the new productions; add Gallina AST nodes (`GListType`, `GArrayType`, `GProdType`, `GMapType`, `GSetType`, `GStringType`, `GBoolType`, `GStringLit`) so the translator can dispatch on them
- `src/rocq2pycsl/translator/gallina.py` — extend `_lower` with:
  - `App("length", [l])` → `Length(l)` for `list` params; `ListLen(l)` for `ghost_list` (translator decides on binder type)
  - `App("nth", [i, l, _default])` → `Nth(l, i)` for `list`; `ListNthAt(l, i)` for `ghost_list`
  - `App("fst", [t])` → `Proj(t, 0)`; `App("snd", [t])` → `Proj(t, 1)`
  - Pair literal `(a, b)` → `Tuple([a, b])`
  - List constructors: `App("nil", [])` → `ListNil()`; `App("cons", [h, t])` → `ListCons(h, t)`
  - List ops: `App("app", [l1, l2])` → `ListAppend(l1, l2)`
  - Dict-as-function calls: `App("d", [k])` where `d` is dict-typed → `MapGet(d, k)`
  - **Set ops** (when `s : T -> bool` is recognized as a set): `App("s", [x])` → `SetMem(x, s)`; `App("set_add", [s, x])` → `SetAdd(s, x)`; `App("set_union", [a, b])` → `SetUnion(a, b)`; etc. for `set_inter`, `set_diff`, `set_subset`, `set_eq`. For empty set, recognize `fun _ => false` literal → `SetEmpty()`.
  - `App("String.append", [a, b])` or `App("append", [a, b])` (when both args are string-typed) → `StrConcat(a, b)`
  - `App("String.length", [s])` → `StrLength(s)`
  - `App("substring", [s, lo, hi])` → `StrSub(s, lo, hi)`
  - **Boolean operators:** `App("andb", [a, b])` → `BinOp("*", a, b)`; `App("orb", [a, b])` → `BinOp("-", BinOp("+", a, b), BinOp("*", a, b))`; `App("negb", [b])` → `BinOp("-", Lit(1), b)`; `App("eqb", [a, b])` → `BinOp("==", a, b)`
  - **Auto-emitted precondition:** each `bool`-typed parameter gets a `requires (b == 0) or (b == 1)` clause, mirroring how `nat`-typed parameters get `requires b >= 0`
  - **Record field access:** when a binder is typed as `R` and `R` was declared via `Record R := { ... }`, calls of the form `<field> r` (Rocq's record projection syntax) or `r.(field)` lower to `FieldGet(r, "<field>")`. The translator carries a small `record_fields: dict[str, set[str]]` map populated by the grammar pass (which now recognizes `Record` declarations).
  - **Class invariant theorems:** a Rocq theorem of the form `forall (r : R), <pred> r` with no other binders is recognized as a class invariant for record `R`; emitted as PyCSL `#@ class invariant <pred>` (placed before the class declaration in the Python target). `pycsl-annotate/SKILL.md §5` documents how PyCSL class invariants work.
  - Identifier remapping: when a theorem has a `list nat` binder, the absorber records `ty="list"` on the IR Forall (the translator already accepts arbitrary `ty` strings; no schema change needed)

**Tests:** add unit tests in `src/rocq2pycsl/tests/extractor/test_lark_backend.py` covering each new type production. Add translator tests in `src/rocq2pycsl/tests/translator/test_gallina.py` covering each lowering rule, including the boolean encoding, ghost_list ops, and ghost_set ops.

### Phase 4 — `lean2pycsl` grammar + translator extensions

Mirror Phase 3 for Lean. Lean's notation is method-style rather than free-function, so additional surface-syntax recognition is needed.

**Files to edit:**

- `src/lean2pycsl/extractor/lean_grammar.lark` — extend type productions:
  - `List <type>`
  - `Array <type>` (Lean's native array type — distinct from `List`)
  - `<type> × <type>` (Unicode times; normalize in `normalize_unicode`)
  - `<type> → Option <type>` (Lean dict-as-function representation)
  - `<type> → Bool` (Lean set-as-characteristic-function representation)
  - `String` (Lean's native string type)
  - `Bool` (Lean's boolean type)
  - Method syntax: `<expr> . length`, `<expr> . fst`, `<expr> . snd`, `<expr> . append` (Unicode-safe terminal)
  - **structure types** (Lean's class equivalent): like Rocq, a structure type appears as a single `IDENT` in binders; the translator dispatches on the type name
- `src/lean2pycsl/extractor/lark_backend.py` — `_AstBuilder` arms for the new productions
- `src/lean2pycsl/translator/lean.py` — extend `_lower` with:
  - `LApp("List.length", [l])` or method-syntax `Proj(l, "length")` → `Length(l)` (for List params) or `ListLen(l)` (for ghost lists)
  - List constructors: `LApp("List.nil", [])` → `ListNil()`; cons via Lean's `::` infix or `List.cons` → `ListCons(h, t)`
  - `LApp("List.append", [l1, l2])` or `++` infix → `ListAppend(l1, l2)`
  - Method projections `t.fst` / `t.snd` → `Proj(t, 0)` / `Proj(t, 1)`
  - Pair literal `(a, b)` → `Tuple([a, b])`
  - Dict reads `d.find? k` (Lean Std.HashMap idiom) or function-call `d k` → `MapGet(d, k)`
  - **Set ops** (when `s : T → Bool` is recognized): `s x` → `SetMem(x, s)`; standard set-op identifiers (`Set.union`, `Set.inter`, `Set.diff`, `Set.subset`, `Set.eq`, `Set.empty`) lower to the matching IR nodes.
  - `s ++ t` (where both are String) → `StrConcat(s, t)`
  - `s.length` → `StrLength(s)`
  - `String.extract s lo hi` → `StrSub(s, lo, hi)`
  - **Boolean operators:** Lean's `&&`/`||`/`!` over `Bool` map to the same 0/1 encoding as Rocq (Phase 3): `&&` → `*`, `||` → `+ - *` chain, `!` → `1 - `; comparison `==` between Bools maps to integer `==`
  - **Auto-emitted precondition:** each `Bool`-typed parameter gets `requires (b == 0) or (b == 1)` mirroring Rocq
  - **Structure field access:** Lean's `r.field` syntax lowers to `FieldGet(r, "field")` when the grammar has recognized `r`'s type as a known structure
  - **Class invariant theorems:** a Lean theorem of the form `∀ (r : R), <pred> r` over a known structure `R` becomes a PyCSL `#@ class invariant`

**Tests:** mirror Phase 3's test additions in `src/lean2pycsl/tests/`.

### Phase 5 — Eight primitive/abstract-data-type golden fixtures

For each of **lists, tuples, dicts, strings, arrays, booleans, ghost_list, ghost_set**, build a fixture in *all three* Phase B/C tools: `src/rocq2pycsl/tests/golden/<name>/`, `src/lean2pycsl/tests/golden/<name>/`, and `src/pycsl_bridge/tests/golden/<name>/`. Each follows the existing `double` shape (`spec.v` or `spec.lean`, `impl.py`, `config.toml`, `expected.py`). The class-instance fixture lives in Phase 6.

**Fixture 1 — Lists: `array_sum_nonneg`**

Python:
```python
def array_sum_nonneg(arr: list, n: int) -> int:
    s = 0
    i = 0
    while i < n:
        s = s + arr[i]
        i = i + 1
    return s
```

Rocq theorem:
```coq
Theorem array_sum_nonneg_nonneg :
  forall (arr : list nat) (n : nat),
    n <= length arr ->
    (forall i : nat, i < n -> nth i arr 0 >= 0) ->
    array_sum_nonneg arr n >= 0.
```

Emitted PyCSL contract uses `\length(arr)`, `\forall i; 0 <= i < n ==> arr[i] >= 0`, `\result >= 0`. Discharges under Alt-Ergo as a textbook accumulator-of-non-negatives example.

**Fixture 2 — Tuples: `divmod_pair`**

Python:
```python
def divmod_pair(a: int, b: int) -> tuple:
    return (a // b, a % b)
```

Rocq theorem uses `fst`/`snd`; Lean uses `.fst`/`.snd`. Emitted contract uses `\result[0]` / `\result[1]`.

**Fixture 3 — Dicts: `dict_insert_lookup`**

Python (returns the inserted value; the proof property is about the abstract dict):
```python
def dict_insert_lookup(d: dict, k: int, v: int) -> int:
    #@ ghost gd : ghost_dict = \empty_map
    #@ ghost gd = \map_set(gd, k, v)
    return v
```

Rocq theorem (dict as `nat -> option nat`): `forall d k v, dict_insert_lookup d k v = v`. Emitted contract uses `\map_get(\map_set(d, k, v), k) == v` over a `ghost_dict`.

**Fixture 4 — Strings: `concat_length`**

Python:
```python
def concat_length(s: str, t: str) -> int:
    return len(s) + len(t)
```

Rocq theorem: `forall s t : string, concat_length s t = String.length (s ++ t)`. Emitted PyCSL contract uses `\str_length(s)`, `\str_length(t)`, `s ^ t`.

**Fixture 5 — Arrays: `array_fill_zero`**

Distinct from lists in source language (Coq `array nat` / Lean `Array Nat`) but mapped to the same Python `arr: list` parameter. **First fixture exercising mutating frame conditions on an array region** (`#@ assigns arr[0..n]`).

Python:
```python
def array_fill_zero(arr: list, n: int) -> None:
    i = 0
    while i < n:
        arr[i] = 0
        i = i + 1
```

Emitted contract:
```
#@ requires n >= 0 and n <= \length(arr)
#@ ensures \forall i; 0 <= i and i < n ==> arr[i] == 0
#@ assigns arr[0..n]
```

**Fixture 6 — Booleans: `bool_xor`**

Python:
```python
def bool_xor(a: bool, b: bool) -> bool:
    return (a or b) and not (a and b)
```

Rocq: `Theorem bool_xor_correct : forall a b : bool, bool_xor a b = xorb a b.`

Lean: `theorem bool_xor_correct : ∀ (a b : Bool), bool_xor a b = (a != b) := sorry`.

Emitted PyCSL contract using the 0/1 encoding:
```
#@ requires (a == 0) or (a == 1)
#@ requires (b == 0) or (b == 1)
#@ ensures (\result == 0) or (\result == 1)
#@ ensures \result == (a + b - 2 * a * b)
#@ assigns \nothing
```

`a + b - 2*a*b` is the integer formula for xor when `a, b ∈ {0, 1}`. Alt-Ergo discharges via linear arithmetic with the 0/1 preconditions in scope.

**Fixture 7 — ghost_list: `list_length_after_append`**

The fixture demonstrates `ghost_list` operations that PyCSL already supports (`\nil`, `\cons`, `\list_length`, `\append`). The Python body computes a count by repeatedly appending to a ghost list, mirroring the pattern from `invariant-writer/SKILL.md §"Ghost Variables in Loop Invariants"`.

Python:
```python
def list_length_after_append(n: int) -> int:
    #@ ghost a : ghost_list = \nil
    #@ ghost b : ghost_list = \nil
    i = 0
    while i < n:
        #@ ghost a += i
        i = i + 1
    return i
```

Rocq theorem (list as `list nat`, working with `app`):
```coq
Theorem list_length_after_append_eq :
  forall (n : nat), list_length_after_append n = n.

(* The deeper property the corpus exercises is the append-length identity: *)
Theorem list_append_length :
  forall (l1 l2 : list nat),
    length (app l1 l2) = length l1 + length l2.
```

Emitted PyCSL contract uses the `\list_length(\append(...))` identity directly in a loop invariant:
```
#@ requires n >= 0
#@ ensures \result == n
#@ assigns \nothing
```
with loop body invariant `\list_length(\append(a, b)) == i` (provable in PyCSL per the `Length_Cons` axiom; cited verbatim from `invariant-writer/SKILL.md`).

**Fixture 8 — ghost_set: `set_union_eq`**

Demonstrates `ghost_set` ops. Uses a characteristic-function representation in Rocq/Lean.

Python:
```python
def set_union_eq(n: int) -> int:
    #@ ghost s1 : ghost_set = \set_empty
    #@ ghost s2 : ghost_set = \set_empty
    i = 0
    while i < n:
        #@ ghost s1 += i
        #@ ghost s2 += i
        i = i + 1
    return i
```

Rocq theorem (set as `nat -> bool`):
```coq
Definition set_add (s : nat -> bool) (x : nat) : nat -> bool :=
  fun y => orb (s y) (Nat.eqb x y).
Definition set_eq (a b : nat -> bool) : Prop :=
  forall x, a x = b x.

Theorem set_union_eq_correct :
  forall n, set_union_eq n = n /\
            forall x, x < n -> set_eq (build_set n) (build_set n).
```

Emitted PyCSL contract uses `\set_eq` directly:
```
#@ requires n >= 0
#@ ensures \result == n
#@ assigns \nothing
```
with loop invariant `\set_eq(s1, s2)` (provable since both ghost sets are built identically).

**Reference corpus addition (mandatory for every Phase 5 fixture).** Each of the eight fixtures above MUST also be added to the PyCSL reference test corpus at `test-suite/corpus/pycsl-reference/` so it runs under `./bin/run-reference-tests.sh` alongside the existing 95 reference tests. The numbering convention follows the existing files (`0331.py`, `0332.py` were the most recently added for the `#@ proof` directive); the eight Phase 5 fixtures get the next eight sequential numbers (e.g. `0333.py` … `0340.py`). For each:

- `test-suite/corpus/pycsl-reference/<NNNN>.py` — the same `impl.py` body as the Phase 5 fixture, with PyCSL contract annotations *and* a `#@ proof rocq: <theorem_name>` / `#@ proof lean: <theorem_name>` pair pointing back to the `spec.v` / `spec.lean` theorems that justify it.
- `test-suite/annotations.md` — a new row in the relevant section (e.g. §2.1.11 for `#@ proof`, or the data-type-specific section for `ghost_list`/`ghost_set`/`array`) referencing `<NNNN>.py` as the worked example.
- `test-suite/traceability-pycsl.md` — a row tying `<NNNN>.py` back to the documentation section it exercises.

The bar: `./bin/run-reference-tests.sh` reports 95+8 = 103 passing tests after Phase 5 (mirrored: 95+8+1 = 104 after Phase 6).

### Phase 6 — Class instance golden fixture

The class-instance fixture is bigger than the primitive ones because it touches:
- Class detection (parser recognizes `Record R := { ... }` in Rocq and `structure R where ...` in Lean)
- Field-access translation
- Class-invariant theorem detection
- Python emitter placement (the `#@ class invariant` line goes *before* `class`, not before any specific `def`)

**Fixture — `BankAccount` with `deposit` and `withdraw` methods.**

Python:
```python
#@ class invariant self._balance >= 0
class BankAccount:
    def __init__(self) -> None:
        self._balance: int = 0

    #@ requires amount >= 0
    #@ ensures self._balance == \old(self._balance) + amount
    #@ assigns self._balance
    def deposit(self, amount: int) -> None:
        self._balance = self._balance + amount

    #@ requires amount >= 0
    #@ requires amount <= self._balance
    #@ ensures self._balance == \old(self._balance) - amount
    #@ assigns self._balance
    def withdraw(self, amount: int) -> None:
        self._balance = self._balance - amount
```

Rocq (record + theorems about methods):
```coq
Record BankAccount := { balance : nat }.

Definition deposit (b : BankAccount) (amount : nat) : BankAccount :=
  {| balance := balance b + amount |}.

Definition withdraw (b : BankAccount) (amount : nat) : BankAccount :=
  {| balance := balance b - amount |}.

Theorem deposit_balance :
  forall b amount, balance (deposit b amount) = balance b + amount.

Theorem withdraw_safe :
  forall b amount, amount <= balance b ->
    balance (withdraw b amount) = balance b - amount.

Theorem bank_account_invariant_preserved :
  forall b amount, balance b >= 0 ->
    balance (deposit b amount) >= 0 /\
    (amount <= balance b -> balance (withdraw b amount) >= 0).
```

Lean equivalent uses `structure BankAccount where balance : Nat` and `b.balance` accessors.

**Implementation work in Phase 6 (on top of Phase 1–4 generalities):**

- `src/rocq2pycsl/extractor/gallina_grammar.lark` — `Record R := { field1 : ty ; field2 : ty }` production
- `src/rocq2pycsl/extractor/lark_backend.py` — `_maybe_record(d)` peer of `_maybe_theorem` / `_maybe_function_def`
- `src/rocq2pycsl/translator/gallina.py` — class-invariant detection (theorem over a single record-typed binder with no other body): emit a `class invariant` contract instead of a method contract
- `src/lean2pycsl/extractor/lean_grammar.lark` — `structure R where field : ty` production
- `src/lean2pycsl/extractor/lark_backend.py` — `_maybe_structure(d)`
- `src/lean2pycsl/translator/lean.py` — same class-invariant detection
- `src/pycsl_emit/emitter/annotator.py` — small extension: support a `class_invariants: list[str]` kwarg on a new `annotate_class` that places `#@ class invariant <expr>` lines before the `class` keyword (mirroring the existing `annotate_function`); see `pycsl-concrete-syntax-reference.md §6` for placement rules
- `src/pycsl_bridge/cli.py` — for class-invariant theorems the bridge emits a `class_invariants` block alongside the per-method `annotations`

**Tests in Phase 6:**

- `src/rocq2pycsl/tests/extractor/test_lark_backend.py` — `Record` parsing
- `src/lean2pycsl/tests/extractor/test_lark_backend.py` — `structure` parsing
- `src/{rocq2pycsl,lean2pycsl,pycsl_bridge}/tests/golden/bank_account/` — full fixture
- Per-tool end-to-end test files extended with the class fixture
- `src/pycsl_bridge/tests/test_end_to_end.py` — assert manifest entries cover both methods AND the class invariant

**Reference corpus addition for Phase 6.** Like the Phase 5 fixtures, the `bank_account` class fixture MUST also live in `test-suite/corpus/pycsl-reference/` as the next sequential number (e.g. `0341.py`), with the same Python source as `src/.../golden/bank_account/impl.py` plus `#@ proof rocq:` / `#@ proof lean:` directives. Update `test-suite/annotations.md` (the `#@ class invariant` row) and `test-suite/traceability-pycsl.md` to reference the new file.

---

## Critical files (summary)

Per "describe the pattern once, list representative paths":

**IR + shared backend:**
- `src/pycsl_emit/ir/nodes.py`
- `src/pycsl_emit/ir/{pretty,json_io}.py`
- `src/pycsl_emit/translator/render.py`
- `src/pycsl_emit/emitter/annotator.py` (class-invariant placement, Phase 6)

**Canonicalizer:**
- `src/pycsl_bridge/canonicalizer/normalize.py`

**rocq2pycsl extensions:**
- `src/rocq2pycsl/extractor/gallina_grammar.lark`
- `src/rocq2pycsl/extractor/lark_backend.py`
- `src/rocq2pycsl/extractor/gallina.py` (new G* surface AST nodes)
- `src/rocq2pycsl/translator/gallina.py`

**lean2pycsl extensions (mirror shape):**
- `src/lean2pycsl/extractor/lean_grammar.lark`
- `src/lean2pycsl/extractor/lark_backend.py`
- `src/lean2pycsl/extractor/lean_ast.py`
- `src/lean2pycsl/translator/lean.py`

**Bridge integration:**
- `src/pycsl_bridge/cli.py` (class-invariant emission path)

**Reference corpus additions (nine new files):**
- `test-suite/corpus/pycsl-reference/0333.py` (list — array_sum_nonneg)
- `test-suite/corpus/pycsl-reference/0334.py` (tuple — divmod_pair)
- `test-suite/corpus/pycsl-reference/0335.py` (dict — dict_insert_lookup)
- `test-suite/corpus/pycsl-reference/0336.py` (string — concat_length)
- `test-suite/corpus/pycsl-reference/0337.py` (array — array_fill_zero)
- `test-suite/corpus/pycsl-reference/0338.py` (bool — bool_xor)
- `test-suite/corpus/pycsl-reference/0339.py` (ghost_list — list_length_after_append)
- `test-suite/corpus/pycsl-reference/0340.py` (ghost_set — set_union_eq)
- `test-suite/corpus/pycsl-reference/0341.py` (class — bank_account)
- `test-suite/annotations.md` (new rows: one per data type)
- `test-suite/traceability-pycsl.md` (new traceability rows)

(Exact numbering: confirm the next free number by running `ls test-suite/corpus/pycsl-reference/ | sort | tail` before authoring. The numbers above assume `0332.py` is the highest existing file, as it was at the close of the `#@ proof` directive work.)

**Nine new fixture directories per Phase B/C tool (pattern):**
- `src/{rocq2pycsl,lean2pycsl,pycsl_bridge}/tests/golden/array_sum_nonneg/` (list)
- `src/{rocq2pycsl,lean2pycsl,pycsl_bridge}/tests/golden/divmod_pair/` (tuple)
- `src/{rocq2pycsl,lean2pycsl,pycsl_bridge}/tests/golden/dict_insert_lookup/` (dict)
- `src/{rocq2pycsl,lean2pycsl,pycsl_bridge}/tests/golden/concat_length/` (string)
- `src/{rocq2pycsl,lean2pycsl,pycsl_bridge}/tests/golden/array_fill_zero/` (array — first frame-condition fixture)
- `src/{rocq2pycsl,lean2pycsl,pycsl_bridge}/tests/golden/bool_xor/` (bool)
- `src/{rocq2pycsl,lean2pycsl,pycsl_bridge}/tests/golden/list_length_after_append/` (ghost_list)
- `src/{rocq2pycsl,lean2pycsl,pycsl_bridge}/tests/golden/set_union_eq/` (ghost_set)
- `src/{rocq2pycsl,lean2pycsl,pycsl_bridge}/tests/golden/bank_account/` (class)

Each fixture directory contains: `spec.v` or `spec.lean`, `impl.py`, `config.toml`, `expected.py`.

**Tests per Phase B/C tool (extending existing files):**
- `src/rocq2pycsl/tests/test_end_to_end.py`
- `src/lean2pycsl/tests/test_end_to_end.py`
- `src/pycsl_bridge/tests/test_end_to_end.py`
- Extractor + translator unit tests in each `tests/extractor/` and `tests/translator/` subdirectory

---

## Existing utilities to reuse

- IR pattern from `Divides`: the new nodes follow the same dataclass + JSON encoder + pretty-printer + render arm. `Divides` is the worked example to copy from.
- The canonicalizer's `_canon` walker already handles AC operators and unary/binary ops generically — extend per node type by adding cases in the existing `if isinstance(...)` chain. `SetUnion` and `SetInter` can register as AC operators with the existing flatten-and-sort machinery.
- The Rocq/Lean Lark grammars already have a `type_expr: qident` production that's a no-op; replace with a small `?type_expr` tree that accepts the new constructors and falls back to `qident` for the int-only case (so existing tests still parse).
- The Rocq translator already accepts arbitrary `ty` strings on `GForall` — no schema change needed there; just propagate the new strings.
- `pycsl_emit.ir.Lit(True)` / `Lit(False)` already render as `1 == 1` / `0 == 1` (per `pycsl-annotate/SKILL.md §3`'s rule against bare booleans). Boolean *parameters* are encoded as 0/1 integers; the translator adds the `requires b == 0 or b == 1` clause automatically.
- `Module2_Parser` accepts `\result[i]` already (per `pycsl-concrete-syntax-reference.md §7`); ghost dict atoms (`\empty_map`, `\map_get`, `\map_set`), ghost list atoms (`\nil`, `\cons`, `\list_length`, `\append`, `\nth`), ghost set atoms (`\set_empty`, `\set_add`, `\set_union`, `\set_inter`, `\set_diff`, `\set_subset`, `\set_eq`, `\set_mem`), string atoms (`s ^ t`, `\str_length`, `\str_sub`), and class invariants are all documented in `pycsl-annotate/SKILL.md`. **The PyCSL side itself needs no changes.**
- `invariant-writer/SKILL.md §"Ghost Variables in Loop Invariants"` documents the provable patterns for `ghost_list` (head-tracking via `\nth(log, 0)`; **AVOID** `\mem` and `\hd` in invariants — they cause OOM / `absurd` errors). The corpus must follow these recommendations.
- The emitter's `annotate_function` (added in the bridge work) already supports `prefix_comments`. Adding a `class_invariants` parameter is a small parallel extension; the libcst module-level walker can find a `class` node by `qualname` just as it currently finds `def`.

---

## Verification

After each phase:

```bash
# Phase 1 — IR backend self-tests
PYTHONPATH=src .venv/bin/python -m pytest src/pycsl_emit/ -v

# Phase 2 — canonicalizer rules
PYTHONPATH=src .venv/bin/python -m pytest src/pycsl_bridge/tests/canonicalizer/ -v

# Phase 3 — rocq2pycsl
PYTHONPATH=src .venv/bin/python -m pytest src/rocq2pycsl/ -v

# Phase 4 — lean2pycsl
PYTHONPATH=src .venv/bin/python -m pytest src/lean2pycsl/ -v

# Phase 5 — primitive/abstract-type end-to-end per fixture
PYTHONPATH=src .venv/bin/python -m pytest src/pycsl_bridge/tests/test_end_to_end.py -v

# Phase 6 — class fixture
PYTHONPATH=src .venv/bin/python -m pytest src/pycsl_bridge/tests/test_end_to_end.py::test_bank_account_reconciles -v
```

Final gate (after all six phases):

```bash
# All four packages green
PYTHONPATH=src .venv/bin/python -m pytest \
    src/pycsl_emit src/rocq2pycsl src/lean2pycsl src/pycsl_bridge

# Reference suite grows by nine (eight Phase 5 + one Phase 6); previous 834/836 → 843/845
./bin/run-reference-tests.sh
# Sanity: confirm the nine new files are picked up
ls test-suite/corpus/pycsl-reference/033{3,4,5,6,7,8,9}.py test-suite/corpus/pycsl-reference/034{0,1}.py

# Live bridge run for each new fixture must discharge all obligations
for fx in array_sum_nonneg divmod_pair dict_insert_lookup concat_length array_fill_zero bool_xor list_length_after_append set_union_eq bank_account; do
  rm -rf /tmp/$fx && mkdir -p /tmp/$fx/{rocq,lean}
  cp src/rocq2pycsl/tests/golden/$fx/*  /tmp/$fx/rocq/
  cp src/lean2pycsl/tests/golden/$fx/*  /tmp/$fx/lean/
  cp src/rocq2pycsl/tests/golden/$fx/impl.py /tmp/$fx/
  PYTHONPATH=src .venv/bin/python -m pycsl_bridge.cli \
      --rocq-config /tmp/$fx/rocq/config.toml \
      --lean-config /tmp/$fx/lean/config.toml \
      --python-src  /tmp/$fx/impl.py \
      --output      /tmp/$fx/out.py \
      --manifest    /tmp/$fx/manifest.toml -v
  # Expected: "reconciled=1, ..., disagreement=0" + "pycsl: N/N obligations Valid"
done
```

The bar per fixture: bridge run prints `reconciled=1` and `pycsl: N/N obligations Valid` with `N >= 2`. If any fixture's `ensures` clause doesn't discharge under Alt-Ergo, weaken it to a provable property rather than papering over with `--no-proof`; the corpus exists to demonstrate the full loop closes for each data type.

Per-fixture extra checks:

```bash
# Class fixture
grep -c '^#@ class invariant' /tmp/bank_account/out.py     # >= 1
grep -c '^    #@ requires amount' /tmp/bank_account/out.py  # >= 2 (deposit + withdraw)

# Bool fixture
grep -c '^#@ requires (a == 0)' /tmp/bool_xor/out.py        # 1
grep -c '^#@ requires (b == 0)' /tmp/bool_xor/out.py        # 1

# Ghost_list fixture
grep -c 'ghost_list' /tmp/list_length_after_append/out.py   # >= 1
grep -c '\\\\list_length' /tmp/list_length_after_append/out.py  # appears in invariant

# Ghost_set fixture
grep -c 'ghost_set' /tmp/set_union_eq/out.py                # >= 1
grep -c '\\\\set_eq' /tmp/set_union_eq/out.py                # appears in invariant
```

---

## Risks and scope cuts

- **Dict semantics in Rocq vs Lean.** Coq's `FMaps`/Lean's `Std.HashMap` are non-trivial libraries with different APIs. The plan dodges this by representing dicts as `nat -> option nat` / `Nat → Option Nat` — a function type that exists in both languages and maps cleanly to PyCSL's `ghost_dict` (a `map int (option int)`). If a real `Std.HashMap`/`FMap` example becomes necessary later, it lives in a follow-up plan.
- **Set semantics: characteristic function only.** PyCSL's `ghost_set` is `map int bool`; Rocq's `Coq.MSets` and Lean's `Std.HashSet` are richer but harder to translate. The plan uses `T -> bool` (Rocq) / `T → Bool` (Lean) — direct PyCSL `ghost_set` analog. `MSets`/`HashSet` fixtures are a follow-up.
- **ghost_list head-tracking caveat.** Per `invariant-writer/SKILL.md`, `\mem(x, l)` and `\hd(l)` cause OOM and `absurd`-term errors respectively in PyCSL loop invariants. The `list_length_after_append` fixture sticks to `\list_length`, `\append`, and `\nth(log, 0)`. The Rocq/Lean theorems must avoid generating `\mem`-style obligations.
- **List length as `Nat` overflow.** Coq's `length : list A -> nat` always returns a non-negative; PyCSL's `\length` returns an unbounded int. The `requires n >= 0` precondition expresses the gap, but the `array_sum_nonneg` example also needs `n <= \length(arr)` to keep `arr[i]` safe — both are emitted automatically by the translator's nat-handling.
- **Strings: ASCII only.** Rocq's `string` is an ASCII-only `list ascii` under the hood. Lean's `String` is UTF-8. PyCSL's `\str_length` follows Why3's `String.length` (codepoint count, model-dependent). The corpus fixture uses ASCII-only literals to avoid semantic mismatch; non-ASCII strings live in a follow-up plan.
- **Arrays vs Lists in Coq.** Coq has no built-in `array` type the way Lean does. The plan accepts both `array nat` (treating it as a synonym for `list nat`) and `Vector.t nat n` (length-indexed); the grammar maps either to the same `Length`/`Nth` IR. If the user wants true mutable-array semantics, the WhyML `array.Array` mapping already exists in `Module6_WhyMLTranspiler` and the converter already emits `assigns arr[0..n]` — that's what the `array_fill_zero` fixture exercises.
- **Booleans encoded as 0/1, not propositions.** PyCSL's contract grammar forbids bare `True`/`False` (`pycsl-annotate/SKILL.md §3`). The bool fixture encodes Python `bool` parameters as 0/1 integers and emits `requires (b == 0) or (b == 1)` per param. This loses some elegance — `xor` becomes the arithmetic expression `a + b - 2*a*b` — but stays inside the existing PyCSL contract grammar. A future enhancement could add a `BoolLit` mode that emits `1 == 1` / `0 == 1`, but that's not needed for the corpus.
- **Class instances: single-class fixtures only.** Multi-class hierarchies (inheritance, mixins) are out of scope. The `bank_account` fixture is a single concrete class; the converter grammars can be extended later for inheritance if needed. PyCSL itself supports `#@ class invariant` per `pycsl-concrete-syntax-reference.md §6`; no PyCSL changes are required.
- **Canonicalizer confluence.** The new rewrite rules introduce more equivalences but the existing AC/divides rules already give us the proof technique (test-driven, no formal confluence proof needed for v1). If a disagreement reveals a missing equivalence, add it incrementally.

---

## Effort estimate

| Phase | Days |
|---|---|
| 1 — IR additions (incl. ghost_list, ghost_set node families) | 3 |
| 2 — Canonicalizer rules (incl. AC for SetUnion/SetInter) | 1.5 |
| 3 — rocq2pycsl extensions | 3.5 |
| 4 — lean2pycsl extensions | 3.5 |
| 5 — Eight primitive/abstract fixtures | 3 |
| 6 — Class fixture + emitter scaffolding | 3 |
| **Total** | **~2.5 weeks** |
