# Plan: no-more-int Part 3 — residual real-type work + an emitter refactor

## Where we are after `no-more-int-2.md`

Parts 1–2 cleared the high-ROI / self-contained items. Done and committed (or, for sum types,
in the working tree awaiting the gate sweep):

| Item | Status |
|---|---|
| **Stage D** float → `real.Real` (soundness fix) | ✅ committed (`15c3872`) |
| **Stage F** referential transparency + sound `lru_cache` | ✅ committed (`01d9d1a`) |
| **Track 3** record-typed parameters (read-only) | ✅ committed (`74891ee`) |
| **Track 2a** sum types + pattern matching *infrastructure* | ✅ built this session (`#@ datatype`, variant `type_decl`, `match`/`case` lowering, exhaustiveness via Why3; drivers 0520/0521) — **uncommitted, gated on the running sweep** |

That last line is the key delta vs no-more-int-2: the Track-2 **spike verdict** ("sum-types +
pattern matching are feasible and independently useful — build them if a tagged-union driver
appears") has now been *realized*. The algebraic-type machinery exists. What remains of Track 2
is only the **json round-trip** (the string-parsing wall), which stays deferred.

So the post-Part-2 surface splits into two halves:

- **(I) Remaining real-type tracks** — still gated on demand-drivers (the Gate-A discipline is
  unchanged: the int-collapse is ~80% deliberate tractability; expand real types only where a
  verification-grade program *fails today* because of the collapse).
- **(II) An emitter refactor** — the no-more-int work (str, float, record, variant, dict) has
  each bolted a new type-branch onto the same dispatch points; the emitter has accreted
  duplication that a behavior-preserving refactor should consolidate. This is *not* gated on a
  driver — it is paying down the debt the feature work created. Detailed in Part B.

---

# PART A — remaining real-type tracks (gated)

## A1 — Track 1: parametric maps (dict value + key)  [Backlog A + B] — T1.1 + T1.2 DONE (string values + string keys)

**Status.** FAIL-driver `0523` committed (`Dict[int, str]`, `\str_length(d[k]) == \str_length(s)`;
fails today — the WhyML is ill-typed, a `string` fed to `map_update_some … (v: int)`). The
emission audit found the value type is hardcoded `int` across ~10 sites (statements.py:426/664
`map_update_some`, the `_coerce_to_int(v)` at the subscript-set, preamble.py:616, expressions.py
DictLit / set / MapGet, functions.py dict-param type) with **no** value-type tracking.

**Discovered T1.1 design (value type ν):**
- **ν side-map.** Capture `Dict[K, V]`'s value type for each dict var (param annotation + local
  `AnnAssign`) — `Module4._get_type_name` loses it (→ bare `dict`). Thread `func_ir["dict_value_types"]`
  : `{var → ν}` (ν ∈ {`int`, `string`}) to Module6 (`self._dict_value_types`).
- **Polymorphic `map_update_some`.** Change the inline `val` (statements.py:426, :664) to
  `val map_update_some (m: map 'k (option 'v)) (k: 'k) (v: 'v) : map 'k (option 'v) ensures {
  result = Map.set m k (Some v) }` — the `ensures` is already polymorphic-compatible, and an int
  dict still instantiates `'v = int` (proofs preserved; preamble line changes → not byte-identical,
  so the **full dict-corpus sweep is the gate**, not the byte-diff).
- **Thread ν at:** the dict literal `{}` (`(const (None: option ν))`), the dict-local declaration
  (`ref (map int (option ν))`), the MapGet **typed default** (`None -> <default ν>`: `0`/`""`), and
  the value coercion (skip `_coerce_to_int(v)` when ν = `string`). Key coercion stays int (κ is T1.2).

**Blast radius: large** (the `None -> <default>` and map-type changes touch every dict-using file).
Gate each sub-stage on the full sweep; budget multiple sweeps. T1.2 (key type κ / string keys) is a
separate sub-stage after T1.1 lands.

**Missing-key decision (resolved): faithful `KeyError`, already implemented.** Python's `dict[k]`
on a missing key raises `KeyError` — there is one semantics, not a "default". PyCSL already models
this faithfully, **opt-in** via `#@ no_exception KeyError`: a dict subscript read becomes a proof
obligation that the key is present (`Map.get d k <> None`; `exception_model.py` trigger
`("map_get", None)`, asserted at `expressions.py:1163`). Drivers `0524` (provably-present key
proves) / `0525` (unproven key fails — teeth) codify it. **Implication for T1.1:** under
`#@ no_exception KeyError` the MapGet `None` arm is a *dead placeholder* (proven unreachable), so the
typed default there is only for WhyML totality, not a semantic value. **Ambient** mode (no
`#@ no_exception KeyError`) keeps the existing optimistic default read (backward-compatible) — so the
typed default still applies there. The earlier "typed default vs option ν" framing was a
verifier-modeling question, not a Python-semantics one; the faithful read is the existing opt-in.

Unchanged from no-more-int-2 §Track 1. `dict`/`set` stay `map int (option int)`; the parsed
`Dict[K, V]` element types are still discarded. Lift to `map κ (option ν)`, κ ∈ {int, string},
ν ∈ {int, string, array int, nested map}. The hard subtlety remains the **typed missing-key
default** (`None -> <default ν>`: `0`/`""`/empty) — recommend the typed-default option (a) to
preserve the corpus's total-read convenience.

- **Gate / driver:** `Dict[int, str]` with `d[k] = s` then `\str_length(d[k]) == \str_length(s)`
  proves (string VALUES carry content through a dict — extends 0510–0514). Then `d["foo"] = v;
  d["foo"] == v` (string KEY).
- **Blast radius: large** — the dict path is core (`_coerce_to_int`, MapGet/MapSet,
  `map_update_some`, dict-literal lowering). Budget multiple sweeps; thread ν first, then κ.
- **Highest practical value of the remaining tracks** (dict-of-strings composes with the string
  model), so this is the first to take if any driver appears.

## A2 — Track 3 follow-ons: record-param mutation + method calls — A2a DONE; A2b gated

Track 3 landed read-only record params. Two follow-ons:

- **A2a — method calls on a record param** (`p.m(args)`): ✅ **DONE.** A one-line union in
  `statements.py::_emit_body_code` folds the (previously write-only) `_record_param_classes` map
  into `_current_record_var_classes`, so `expressions.py::_resolve_dotted_signature` resolves a
  record-param method call exactly like a record local (`c = C(); c.m()`). Driver `0522`
  (`a.bump(k)` propagates the callee's `\result == k + 1`) flips FAIL→PASS; byte-identical for all
  non-record-param-method-call corpus files (additive). **Scope:** A2a delivers only the
  propagation record locals already get — **result-only** and **param-referencing** `ensures`. A
  **field-referencing** callee ensure (`\result == self.x`) still does NOT propagate — but that is
  a *pre-existing* gap that fails for record **locals** too (the method-call contract gap;
  `\result == self.x` is in neither `_module_method_result_ensures` nor
  `_module_method_param_result_ensures` because it references the receiver's field, needing a
  `self`→receiver substitution). It is **out of A2a's scope** and tracked as its own item below.

- **A2c — field-referencing ensure propagation (the method-call contract gap)** — NEW, surfaced by
  A2a. A callee `ensures` that references `self.<field>` is dropped at every method-call site
  (locals AND params), so a getter `def get_x(self): #@ ensures \result == self.x` proves nothing
  at the caller. Fix: extend the result-ensures propagation to capture receiver-field clauses and
  substitute `self`→the receiver instance/param at the call site. Medium risk (touches the method
  result-ensures tables in Module5/Module6). Gated on a driver needing a field-returning method
  (e.g. `StringIO`/getter stubs — cf. the method-call-contract-gap memory).
- **A2b — record-param mutation** (`p.f = v` writing back to the caller): **hard** — Why3 records
  are by-value, so this needs `ref`-passing with a `writes p.f` frame obligation (or a documented
  value-semantics boundary). Gated on a driver that mutates a passed object and observes the write
  caller-side. **Medium-high risk** (frame machinery); defer until a real driver demands it.

## A3 — Track 4: bounded eager itertools  [Backlog G] — NOT STARTED

Unchanged from no-more-int-2 §Track 4. Bounded-array under-approximation of the **eager** subset
(`chain`/`islice`/`product`/`combinations`); lazy/infinite (`cycle`/`count`/`repeat`, `yield`)
stays explicitly out of scope (no SMT-tractable stream model). *Driver:* `len(chain(a, n, b, m))
== n + m` + an element-membership contract. Low value; independent; build only on a concrete
bounded-itertools driver.

## A4 — Track 2b: json round-trip  [Backlog C tail] — SHELVED (string-parsing wall)

The sum-type/recursive-type *infrastructure* (Track 2a) is now built, so the only remaining json
piece is the **round-trip** `loads(dumps(x)) == x`, which requires string → value parsing /
value → string serialization. That is the niche, hard part the spike explicitly did **not**
establish. Stays deferred:

- A real `src/pycsl_lib/json.py` over a *recursive* `#@ datatype` (needs A5 — recursive datatypes
  — and Track 1's `map string json` for `JObj`), plus the round-trip contract under bounded depth,
  likely citing a Rocq/Lean lemma (the `0342` gcd template) since SMT over a recursive union +
  maps is heavy. **Default verdict: don't build** absent a compelling json-content driver.

## A5 — sum-type extensions (follow-ons to Track 2a, this session's build)

The infrastructure shipped with documented boundaries (annotate SKILL §3f). Each is a gated
follow-on:

- **A5a — recursive datatypes** (`#@ datatype Tree = Leaf | Node(Tree, Tree)`): the preamble must
  emit Why3 self-referential / mutually-recursive `type … with …`; payload types currently map a
  fixed `_VPAY` table (int/bool/str/float) and reject a self-reference. Prereq for json (A4) and
  any tree/list-of-self structure. *Driver:* a recursive `depth`/`size` proof (the spike's shape).
  **Medium risk** (recursion + termination `variant` on the recursive function).
- **A5b — captures referenced in contracts**: today a `case`-bound capture is in scope only inside
  its arm, not at the `requires`/`ensures` level. Surfacing per-arm postconditions (or a
  `\match`-style spec operator) is a real extension. Gated on a driver needing it.
- **A5c — guarded / nested / or-patterns** (`case Some(n) if n > 0`, nested ctors, `A | B`): the
  pure_ast pattern parser + the match lowering handle only flat single-level constructor patterns.
  Each is a parser + lowering extension; build on demand.
- **A5d — parametric datatypes** (`Option[T]`): a generic variant over a type param. Composes with
  Track 1's parametric machinery; low priority.

## A6 — cross-cutting: retire `_coerce_to_int` categories

Unchanged discipline from no-more-int-2 §Cross-cutting. `_coerce_to_int`
(`expressions.py:119-148`) erases real types (string→hash, array→0, map→0, tuple→hash,
self→abstract-op). As each track lands, **remove that track's coercion category** rather than
leaving dead erasure: Track 1 removes dict key/value→int; Track 3 (done) removed self/record→int
for record params — *audit that the record-param coercion is actually gone*; a future tuple track
removes tuple→hash. End state: `_coerce_to_int` fires only for genuinely-untyped (`Any`) operands.

## A7 — residual benign collapses (document, do not build)

`bool` as `1/0` and bare `tuple → int` (hash) are rare and benign; leave them and keep them
documented in the τ-table. No driver should chase these.

---

# PART B — emitter refactor (`src/pycsl/*.py`, `src/pycsl/module6_whyml/*.py`)

**Goal:** a *strictly behavior-preserving* refactor that pays down the duplication the
no-more-int feature work accreted, without changing a single byte of emitted WhyML. The corpus
sweep (byte-identical `.mlw` where feasible, else identical pass/fail set) is the contract.

> **Decided scope (2026-06-05): full decomposition — moves 1, 2 AND 3.** Unify the type-dispatch
> and pre-decl exclusion (moves 1–2), THEN split the giants: `Module5_IREmitter.py` → a `module5/`
> package (`collections_synth` / `memoization_rt` / `match_ir` / `module_constants`),
> `expressions.py` → string/float/map/variant handler mixins, `statements.py` → feature-handler
> groups, `pure_ast.py` → tokenizer / pattern-parser / statement-parser. One file (or one
> unification) per commit, a full corpus sweep between every commit, byte-diff `.mlw` where the
> change is purely structural. Runs only AFTER the sum-types commit lands on a clean base.

**Hard invariant:** every step is gated by a full corpus sweep showing **zero pass/fail delta**
vs the pre-refactor baseline. Where practical, also diff the generated `.mlw` byte-for-byte
(`bin/extraction-byte-diff*.sh` patterns) — a true refactor changes *structure, not output*.

### Why now / what the debt looks like
str → float → record → variant → dict each added a parallel branch at the **same dispatch
points**, so the type logic is smeared across many `if symtype == …` / `_is_float_expr` /
`in self._record_types` / `in self._variant_types` ladders:
- `functions.py::_param_type_str` / `_symtype_to_whyml` / `_compute_return_type` — N parallel
  "is it str/float/record/variant?" branches.
- `expressions.py::_coerce_to_int`, `_handle_binop`, `_handle_call_expr` — per-type ladders.
- `statements.py::_emit_first_assign` / `_emit_body_code` pre-decl exclusion set — one
  `body_<kind>_vars` per type (array/dict/lambda/record/variant), all subtracted from
  `pre_decl_vars` in parallel.
- `Module5_IREmitter.py` and `pure_ast.py` are the two giants (1581 / 3775 LOC) carrying many
  unrelated concerns each.

### Target sizes (LOC, pre-refactor)
`pure_ast.py` 3775 · `expressions.py` 1896 · `Module5_IREmitter.py` 1581 · `statements.py` 1432 ·
`Module2_Parser.py` 1111 · `pycsl.py` 1092 · `Module4` 788 · `preamble.py` 715 · `ir_scanner.py`
663 · `Module3` 632 · `functions.py` 586. (~17.9k LOC across the two dirs.)

### Refactor moves (incremental, each its own commit + sweep)

1. **Unify the type-dispatch.** Introduce one `whyml_type_of(symtype) -> WhymlType` resolver (or a
   small dispatch table keyed by the classified kind: `int | string | real | record c | variant t
   | map κ ν | array`) and route `_param_type_str` / `_symtype_to_whyml` / `_compute_return_type`
   through it. Collapses the parallel branches into one place — and makes Track 1 / A5 cheaper to
   add later.
2. **Consolidate the pre-decl exclusion.** Replace the five hand-maintained `body_<kind>_vars`
   subtractions in `_emit_body_code` with one "typed-local kinds" pass that classifies each local
   once; `pre_decl_vars` = locals not in any typed kind. (The variant addition this session is the
   fifth such subtraction — exactly the smell.)
3. **Extract from the giants.** `Module5_IREmitter.py`: split the cohesive concern-clusters
   (collections synthesis, memoization/RT checks, match/pattern IR, module-constant collection)
   into sibling modules under a `module5/` package (mirroring `module6_whyml/`). `pure_ast.py`:
   separate the tokenizer/pattern-parsing/statement-parsing concerns. `expressions.py` /
   `statements.py`: extract the per-feature handler groups (string ops, float ops, dict/map ops,
   variant/match) into focused mixins or modules.
4. **Kill dead erasure as types land** (ties to A6): remove `_coerce_to_int` categories already
   superseded.
5. **Mechanical hygiene:** dead-code/unused-import sweep, docstring/`file:line` anchor refresh
   (the no-more-int line-number anchors in the skills/docs drift after extraction — re-point
   them), consistent naming for the new type-kind vocabulary.

### Risk & ordering
- **Highest risk:** `expressions.py` / `statements.py` / `Module5` are load-bearing for the whole
  corpus. Do the *small* unifications (moves 1–2) first — they have the clearest before/after and
  the tightest sweep. Defer the *big* file splits (move 3) until 1–2 are green, and split **one
  file per commit** with a full sweep between.
- **Never** combine a refactor commit with a behavior change. If a refactor surfaces a latent bug,
  fix it in a *separate* commit with its own driver.
- The `src/self-annotate/src/` tree mirrors `src/pycsl/` — confirm whether the refactor must be
  mirrored there (`bin/check-self-annotate-sync.sh`) or whether that mirror is regenerated.

### Gate (every refactor commit)
1. Full corpus sweep, zero pass/fail delta vs baseline (`/tmp/proof_sweep.sh`).
2. Where the change is purely structural, byte-diff the `.mlw` for a representative sample.
3. `bin/doc-coherency.py --check` green; re-point any moved `file:line` anchors in the skills.
4. One file (or one unification) per commit; descriptive message; **no** behavior change folded in.

---

## Suggested order (overall)

1. **Commit sum types** (Track 2a) once the running sweep is clean — closes the no-more-int-2
   Track-2a verdict.
2. **Part B moves 1–2** (type-dispatch + pre-decl unification) — pure debt paydown, no driver
   needed, makes the remaining tracks cheaper. Highest-leverage, lowest-risk refactor.
3. **Part B move 3** (split the giants) — one file per commit, sweep-gated.
4. **Part A tracks** — only as demand-drivers appear: A2a (param method calls) and A1 (parametric
   maps) are the most likely to be pulled; A4/A5a (json + recursive datatypes) stay default-don't-
   build; A3 (itertools) independent and low-value.

## Critical files (unchanged anchors — refresh after Part B move 3)
`functions.py` (`_param_type_str`/`_symtype_to_whyml`/`_compute_return_type`, `can_emit_as_logic`);
`expressions.py` (`_coerce_to_int` ~119-148, MapGet ~1118, `_handle_binop`); `statements.py`
(`_emit_body_code` pre-decl ~1352, `map_update_some` ~751-769); `preamble.py` (`_emit_type_decls`,
field types ~584-595); `Module5_IREmitter.py`; `pure_ast.py`; `Module2`/`Module4` (datatype +
parametric-type surface); `types.py` (`_collect_*_var_assigns`).
