# Plan: parametric & algebraic types beyond `int` — no-more-int Part 2 (detailed)

## Context

`no-more-int.md` Part 1 (float→real; referential-transparency / sound `lru_cache`) is **done**.
Part 2 was a gated backlog of the remaining real-type work; this file expands it into an
executable plan while keeping the discipline established in the weighing:

> The int-collapse is ~20% genuine debt and ~80% deliberate tractability. So **every track below
> stays gated**: it starts only on a *named demand-driver — a verification-grade program that
> fails today because of the collapse* — and the recursive/lazy tracks additionally require a
> **Stage-0 SMT-feasibility spike** before any build (the strings-plan Gate-B pattern). The
> int-domain is PyCSL's strength; expand real types only where a driver proves the need.

### Why these are hard / wanted

| Track | Backlog item | Real model | Driver class |
|---|---|---|---|
| 1 — Parametric maps | A (dict value), B (dict key) | `map κ (option ν)` | a dict of strings / nested dict that needs content |
| 2 — Algebraic types | C (sum/recursive + json) | `type t = A \| B x \| …` + match | a tagged union / json round-trip |
| 3 — Records | E (class params) | `C`-param → `record c` | an object-passing API reading a field |
| 4 — Iterators | G (eager itertools) | bounded array under-approx | a bounded `chain`/`islice` length/element proof |

### Dependency graph

```
Track 1 (parametric maps A+B) ─┐
                               ├─► Track 2 (json: JObj = map string json) 
Track 2a (sum/recursive types)─┘
Track 3 (records E)            ── independent
Track 4 (iterators G)         ── independent
```

Do **Track 1 (A+B together — they share the parametric-map machinery)** first if any driver
appears; Track 2 (json) needs both Track 1 (string-keyed nested maps) AND sum types, so it is
last and spike-gated. Tracks 3 and 4 are independent and can be slotted on their own drivers.

---

## Track 1 — Parametric maps: dict value & key types  [Backlog A + B]

**Goal.** `dict` / `set` stop being `map int (option int)` (key int, value int) and carry the
parsed-but-discarded `Dict[K, V]` / `Set[T]` element types: `map κ (option ν)` where κ ∈
{`int`, `string`} and ν ∈ {`int`, `string`, `array int`, a nested `map …`}.

**Why A+B together:** both flow from the same place — the `Dict[K, V]` annotation's element types,
currently dropped (`_get_type_name` returns the bare head `dict`). Capturing them feeds both the
key and the value type.

### Sub-stages
- **T1.0 — capture element types.** `Module4._get_type_name` / `Module5` type tracking: for a
  `Dict[K, V]` (or `Set[T]`) annotation, record the element types on the symbol table (e.g.
  `dict<string,int>` tags, or a side map `func_ir["dict_elem_types"]`). Today the subscript head
  is lowercased to `dict` and `K,V` are lost (static-semantics §1.4: "key/value types opaque").
- **T1.1 — value type ν (Backlog A).** Thread ν into: the dict type emission
  (`functions.py:26-27`/`preamble.py:584-595` → `map κ (option ν)`); MapGet (`expressions.py:
  1118-1122` — the `Some v_ -> v_` arm and the `None -> <default ν>` arm); MapSet
  (`statements.py:751-769` — `map_update_some (m: map κ (option ν)) (k: κ) (v: ν)`); the dict
  literal lowering (`expressions.py:~1516`, stop forcing value `0`). **Stop `_coerce_to_int`** on
  a value whose ν is known (`expressions.py:119-148`).
- **T1.2 — key type κ (Backlog B).** Same threading for the key: `map string …`; stop hashing
  string keys (`_coerce_to_int:122`, the MapGet/MapSet key coercion). Why3 `string` has decidable
  equality, so `Map.get (m: map string ν) (k: string)` is well-formed.

### The hard subtlety — the missing-key default
Today a missing key reads `0` (the `None -> 0` arm; this is what makes `defaultdict(int)` free).
With a parametric ν the default is **type-specific**: `0` for int, `""` for string,
`(Array.make 0 0)` for array, the empty map for a nested map. Two options:
- **(a) typed default** — emit `None -> <default ν>` per ν. Keeps the convenient
  total-read model; the `defaultdict` story generalises (`defaultdict(str)` → `""`).
- **(b) expose `option ν`** — `d[k]` returns the option; the caller must handle `None`
  (matches Python's `KeyError` more faithfully, but breaks the current total-read convenience and
  every existing dict test). **Recommend (a)** (typed default) to preserve the corpus.

### Gate & driver
*Driver (commit `# pycsl-expected: FAIL` first):* a `Dict[int, str]` where `d[k] = s` then a
postcondition `\str_length(d[k]) == \str_length(s)` proves — i.e. **string VALUES carry content
through a dict** (extends the string+dict drivers 0510–0514, which only stored int values). Then
B's driver: `d["foo"] = v; d["foo"] == v` (string KEY). **Blast radius is large** — the dict path
is core; full-sweep each sub-stage, and the `None -> <default>` change touches every dict read.

### Critical files
`Module4_SemanticAnalyzer.py` (`_get_type_name` element capture); `Module5_IREmitter.py` (dict
elem-type tracking); `module6_whyml/functions.py:26-27`, `preamble.py:584-595` (map type);
`expressions.py:119-148` (`_coerce_to_int`), `:1118-1122` (MapGet); `statements.py:751-769`
(MapSet / `map_update_some`).

---

## Track 2 — Algebraic + recursive types → json  [Backlog C] — SPIKE RUN: infra feasible, round-trip deferred

**Spike result (T2.-1, run):** a hand-written Why3 `type json = JNull | JBool bool | JInt int |
JStr string | JArr (list json)` plus structural-identity goals and a recursive `depth` function
**all proved Valid** under Alt-Ergo (0.03–0.04s). So **sum/recursive types + pattern matching +
recursion are feasible** — the infrastructure (T2.0–T2.2) is buildable and is *independently
useful* (Optional, any tagged union, exhaustiveness), so it should NOT be gated on json. What the
spike did NOT establish is the **json round-trip** `loads(dumps(x)) == x` — that needs string
parsing/serialization (string → value), which remains the hard/niche part. **Revised verdict:**
build sum-types + pattern matching on a tagged-union driver if one appears (feasible); keep the
json *round-trip* deferred/opaque (the string-parsing wall).



**Goal.** Emit Why3 algebraic/recursive types and pattern matching, then build a real `json`
value union with a verifiable round-trip. **This is a new language capability** (PyCSL emits only
records + built-in `option`), the largest item, and the headline-but-niche one — **do not start
without (1) a real json driver AND (2) a passing SMT spike.**

### T2.-1 — the SMT feasibility spike (the gate; hand-written `.mlw`, no PyCSL)
Before any pipeline work, hand-write the Why3:
```why3
type json = JNull | JBool bool | JInt int | JStr string
          | JArr (list json) | JObj (list (string, json))
```
and prove a *small, fixed-depth* round-trip / structural lemma under Alt-Ergo/Z3. Record Valid vs
timeout. **If even a depth-2 round-trip needs heavy hand-proof, stop** — keep json opaque and
document (the YAGNI exit). The map-vs-assoc-list choice for `JObj` is part of the spike (a `map
string json` may reason worse than an association `list (string, json)`).

### T2.0 — sum-type surface + parse (only if the spike passes)
A Python surface for a tagged union — recommend reusing the **`@dataclass` + class-per-variant**
or an `Enum`-tagged shape, or a dedicated `#@ datatype` declaration. Parse in Module2; validate in
Module4; record a `type_decl` of `kind: "variant"` (parallel to `kind: "record"`).

### T2.1 — algebraic `type` emission
`preamble.py::_emit_type_decls`: emit `type t = C1 | C2 ty | …` (and mutually-recursive `with`
for json's self-reference). New, beside the existing `record` branch.

### T2.2 — pattern matching (IR + lowering)
`match x: case …` → a new `Match` IR (Module5) and a WhyML `match … with | C1 -> … | C2 v -> …
end` (Module6 statements). This is the consumer side of variants — needed to *use* json values.

### T2.3 — the json module
Build `src/pycsl_lib/json.py` over the variant type (replacing the opaque int stub); the round-trip
contract under stated constraints (bounded depth), citing the spike's lemma via `#@ proof
rocq|lean` if SMT alone won't close it (the gcd template `0342`).

### Gate & driver
*Driver:* `loads(dumps(x)) == x` on a small fixed value. **Default verdict: don't build** unless a
real program needs json-content verification — json is niche for an integer-domain verifier.

### Critical files
`module6_whyml/preamble.py` (`_emit_type_decls` variant branch); `Module5_IREmitter.py` (Match IR,
variant `type_decl`); `module6_whyml/statements.py` (match lowering); `Module2_Parser.py` /
`Module4_SemanticAnalyzer.py` (datatype surface); `src/pycsl_lib/json.py` + `json_demo.py`.

---

## Track 3 — Record-typed parameters  [Backlog E] — ✅ DONE (read-only)

**Status (implemented):** a bare class-typed parameter whose class is in `_record_types` is typed
as the Why3 record (functions.py `_param_type_str` + the method loop) and registered in
`_record_locals`/`_record_param_classes`, so `p.field` is a **direct read** (the opaque
`getattr_<cls>`/`self_to_int_<cls>` path is gone for record params). Contracts gained
`p.field` access — a new CSL grammar rule `CNAME "." CNAME -> param_field_access` (Module2)
reusing `FieldAccess` with a non-`self` object, routed by `_csl_field_access` through the body's
`Attribute` path (`_handle_attribute_expr`). Driver `0519` (`add_coords(p: Point)` proves over
`p.x`/`p.y`); class-test regression sample (0033/0077/0440/0441/0442/0450/0453) clean.
**Read-only only:** mutating a record param is out of scope (Why3 records are by-value — a
follow-on needs the frame/`writes` machinery). Method calls on a record param (`p.m(...)`) are a
small follow-on (union `_record_param_classes` into `_current_record_var_classes`).



**Goal.** A bare `C`-typed parameter stops coarsening to `int` (with opaque `getattr_<cls>` /
`self_to_int_<cls>`) and becomes the record type `c`, so `obj.field` is a direct record read —
the same model already used for `self` and locally-constructed instances.

### Sub-stages
- **T3.1 — type the param as the record.** `functions.py::_param_type_str` (and the method loop):
  when `symtype` names a class in `self._record_types`, emit `({safe}: {whyml_name})` instead of
  the `int` fallback (`:36`). Requires the record to be registered before the param is typed —
  cross-module classes (via `_resolve_imports`/`_apply_inheritance`) must populate `_record_types`
  first (they already do for construction; confirm ordering).
- **T3.2 — field reads/writes on a param.** `expressions.py::_handle_attribute_expr` and the
  external set/del paths: `obj.field` where `obj` is a record-typed param → `obj.<label>` direct
  access (drop the opaque `getattr_<cls>` at `:1141`). Retire the `self_to_int_<cls>` coercion
  (`_coerce_to_int:145`) for record params.
- **T3.3 — method calls on a param.** `obj.m(args)` where `obj: C` → the mangled `c__m obj args`
  (already works for record locals via `_current_record_var_classes`; extend to params).

### The hard subtlety — value vs aliasing
Why3 records are passed by value; a function mutating a record param (`obj.f = v`) does not write
back to the caller's instance (unlike Python's reference semantics). So: a param that is *read* is
fine; a param that is *mutated* needs either `ref`-passing (a `writes`/frame obligation) or a
documented value-semantics boundary. **Recommend:** read-only record params first (T3.1–T3.3 read
paths); mutation of a record param is a follow-on with the frame machinery.

### Gate & driver
*Driver:* `def f(p: Point) -> int: return p.x` with `requires p.x == 5; ensures \result == 5`,
proven by a **direct field read** (today `p.x` is an opaque `getattr` and the proof can't see `5`).

### Critical files
`module6_whyml/functions.py:36` (param type); `expressions.py:~1069`/`~1141` (attribute read,
opaque getattr), `:145` (`self_to_int` coercion); `Module5`/`preamble` `_record_types` ordering.

---

## Track 4 — Bounded iterators / itertools  [Backlog G]

**Goal.** A bounded-array under-approximation for the **eager** itertools subset; the lazy/infinite
operators stay explicitly out of scope (no coinductive/stream model — genuinely not SMT-tractable).

### Sub-stages
- **T4.1 — eager operators over arrays.** `chain(a, b)` → a concatenated `array int` with
  `len = len a + len b`; `islice(a, lo, hi)` → `Array.sub`; `product`/`combinations` → bounded
  enumeration with a cardinality contract (`len(product(a,b)) == len a * len b`). Each as a real,
  body-verified function over `array int` (no opaque `iter_*` ops).
- **T4.2 — `for x in <eager-iterable>`.** Confirm the existing for-loop over an array covers the
  eager case; no generator/`yield` model.

### Out of scope (documented, not faked)
`cycle` / `count` / `repeat` / any infinite generator; `yield`/generator functions; lazy
composition. These need a stream model PyCSL cannot soundly express — keep the opaque stub +
document the boundary (mirrors heapq's "full heap invariant deferred" note).

### Gate & driver
*Driver:* `len(chain(a, n, b, m)) == n + m` and an element-membership contract over the eager
result. Low value; build only on a concrete bounded-itertools driver.

### Critical files
`module6_whyml/expressions.py` (eager itertools lowering, the `iter_length`/`iter_get` opaque ops
to replace); `src/pycsl_lib/itertools.py` + `itertools_demo.py`.

---

## Cross-cutting — retiring `_coerce_to_int`

`_coerce_to_int` (`expressions.py:119-148`) is the boundary that erases real types (string→hash,
array→0, map→0, tuple→hash, self→abstract-op). As each track lands its real type, **remove that
track's coercion category** rather than leaving dead erasure: Track 1 removes the dict
key/value→int coercions; Track 3 removes `self`/record→int; a future tuple track removes the
tuple→hash. The end state: `_coerce_to_int` only fires for genuinely-untyped (`Any`) operands.

## Gating discipline (applies to every track)

1. Write the failing demand-driver and commit it `# pycsl-expected: FAIL`.
2. (Tracks 2 only) pass the Stage-0 SMT spike first; YAGNI-exit if it fails.
3. Implement the minimal sub-stage; flip the driver to passing.
4. **Full corpus sweep** (`PYTHONHASHSEED=0`, honor `# pycsl-flags:`/`# pycsl-expected:`, diff vs
   the committed baseline) — these are core-path changes; require zero new regressions.
5. τ-table + doc-coherency green; UB/limitations docs updated.
6. Stop at the YAGNI exit if the driver turns out not to need the track.

## Suggested order (each still gated on its own driver)

1. **Track 3 (record params)** — most self-contained, clearest driver, reuses the record model.
2. **Track 1 (parametric maps)** — high value (dict-of-strings, composes with the string work),
   but high blast radius; budget multiple sweeps.
3. **Track 4 (eager itertools)** — independent, low-ish value, only on demand.
4. **Track 2 (json / sum types)** — last, spike-gated, default-don't-build.
