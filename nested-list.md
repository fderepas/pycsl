# nested-list.md — stop nested `List[List[int]]` collapsing to `array int`

**Goal.** Lower a nested list to its FAITHFUL nested WhyML type — `List[List[int]]` → `array (array int)`
(or `seq (seq int)`; the SMT spike decides), `List[Dict[str,int]]` → `array (map string (option int))`,
recursively — so an inner element `a[i]` is a real, faithfully-typed collection you can index (`a[i][j]`)
and reason about, instead of an opaque `int`. This is the shared root cause behind two documented
boundaries: `cleared-array` **subscript-projection comprehensions** `[x[k] for x in a]` and the general
"nested/derived element typing" residual.

This is a **feature** (emission changes for nested-collection programs), NOT a refactor. High blast
radius (the list-type path is core) — sequence carefully, budget multiple sweeps.

---

## 1. Context / verdict (what happens today, with citations)

- A `List[T]` param/local lowers via `functions.py::_param_type_str` (and the body-local
  first-assign/return paths in `functions.py`/`types.py`) to `array <elem>`, where `<elem>` is a SCALAR
  element-type string tracked in `_array_elem_types` / `_seq_value_types` / `return_value_type`
  (functions.py:195/212/781/1077). For a NESTED list the inner element type is not threaded, so `<elem>`
  defaults to `int` → the outer becomes `array int` and the inner list is GONE. (Confirmed empirically by
  the cleared-array run: both `List[List[int]]` and `List[Dict[str,int]]` collapse the param to `array
  int`, symbol-table kind `'list'`.)
- Partial infrastructure ALREADY exists and must be reused, not reinvented:
  - **Recursive value-type precedent** — `Module5_IREmitter.py::_m5_get_dict_value_type` recursively maps
    `Dict[str, Dict[..]]` → `map int (option (map ..))` and `Dict[str, List[T]]` → `seq T`. It is the
    template; it is just ad-hoc (hardcoded 1–2 levels, dict-value only) and needs generalizing.
  - **A 2D path** — `_param_type_str` maps `array2d_params` → Why3 `matrix int`. So a flat 2-D case has a
    representation, but the *general* `array2d_params` detection does not catch arbitrary `List[List[T]]`
    and does not compose beyond depth 2 or with non-int leaves.
  - **String-keyed maps** (`map string`, cleared-hash) and **seq element types** (`seq int`/`seq string`)
    are already faithfully modeled — nested lists just need to COMPOSE these.
- **Design-philosophy check** (pycsl-how-to-develop §8.4): the int-collapse is ~80% deliberate
  tractability. Nested lists are a case where the collapse loses REAL structure that concrete features
  demand (subscript-projection content). Promote the type here because a driver needs it — not globally.

**Verdict.** Introduce ONE shared recursive `annotation → WhyML-type` function (generalizing
`_m5_get_dict_value_type`) that maps any nested container annotation to its faithful type, and thread it
through the list param/local/return element-type and the subscript lowering, so `a[i]` is emitted at the
inner collection's real type. Non-nested and un-annotated lists stay byte-identical (`array int`).

---

## 2. Gate B — SMT-feasibility spike FIRST (hand-write `.mlw`), decide the representation

The make-or-break is nested INDEXING content, and — if nested lists are ever MUTATED — the array-of-arrays
ALIASING semantics. LEAD with both:

```whyml
module NestedSpike
  use int.Int use array.Array use seq.Seq
  (* Candidate A: array of arrays (mutable) — aliasing is the risk *)
  goal read_A : forall a: array (array int), i j: int.
      0 <= i < Array.length a -> 0 <= j < Array.length a[i] -> a[i][j] = a[i][j]
  goal alias_A : forall a: array (array int), i j v: int.
      0 <= i < Array.length a -> 0 <= j < Array.length a[i] ->
      (a[i][j] <- v; a[i][j]) = v                         (* nested update reads back *)
  (* Candidate B: seq of seqs (immutable) — no aliasing, read-only content *)
  goal read_B : forall s: seq (seq int), i j: int.
      0 <= i < Seq.length s -> 0 <= j < Seq.length (Seq.get s i) ->
      Seq.get (Seq.get s i) j = Seq.get (Seq.get s i) j
end
```
- Record **Valid vs timeout + timing** (Alt-Ergo AND Z3) for each candidate. The DECISION: `array (array
  int)` (mutable, faithful to Python list mutation, but the inner arrays alias — a `matrix` may be cleaner
  for rectangular 2-D) vs `seq (seq int)` (immutable, no aliasing, ideal for read-only nested access such
  as the subscript-projection comprehension) vs Why3 `matrix int` (flat 2-D, only rectangular int). Pick by
  what reasons best for the DEMAND (read-only content first; mutation only if a driver needs it).
- **YAGNI scoping:** if full mutable nested arrays are intractable, ship the READ-ONLY nested model (seq
  of seqs / matrix) — which is exactly what the subscript-projection comprehension and nested-read drivers
  need — and keep in-place nested MUTATION (`a[i][j]=v` on a list) as a documented boundary.

---

## 3. Stages

**S0 — spike (above)** → representation decided + committed fixture under `test-suite/corpus/conformance/spikes/`.

**S1 — one recursive `annotation → WhyML type`.** Generalize `_m5_get_dict_value_type` into a shared
`_m5_annotation_to_whyml_type(ann)` that recurses uniformly: `int/bool`→`int`, `str`→`string`,
`float`→`real`, `List[T]`→`<seq|array> <rec(T)>`, `Dict[K,V]`→`map <κ(K)> (option <rec(V)>)`,
`Set[T]`/`frozenset[T]`→`map <rec(T)> (option int)`, `Tuple[..]`→existing tuple type, record/variant→their
whyml name; unknown→the current scalar default (documented residual). Re-express the existing dict-value
and (if kept) `matrix` paths through it so there is ONE recursion, not several. Bound the depth with a
`max-nesting` guard → fall back to the scalar default + a note (no silent unbounded blowup).

**S2 — thread the element type into list emission.** Route the list param/local/return WhyML type
(`_param_type_str`, the first-assign/`_rhs_yields_array`, `return_value_type`) through S1 so `List[List[int]]`
emits `array (array int)` and `_array_elem_types[v]` carries the full inner type string (not just `int`).
Additive/guarded: a plain `List[int]` (leaf `int`) is byte-identical to today.

**S3 — subscript `a[i]` yields the inner collection.** In the subscript lowering (`expressions.py`
`_handle_subscript`/`Array.get`), when `a`'s element type is a collection, emit `a[i]` at that inner type
(so `a[i][j]` / `a[i][k]` / `k in a[i]` type-check and reason). Reuse the array/seq/map read machinery per
the inner kind.

**S4 — nested literals + comprehension source.** A nested literal `[[1,2],[3]]` and a nested-typed
comprehension source lower with the inner elements at their real type. This is what UNBLOCKS
`cleared-array` subscript-projection `[x[k] for x in a]` (its choices.md boundary) — wire that content law
to fire once the source's element type is a faithfully-typed collection.

**S5 — consumers + `len`.** `len(a[i])` (inner length), `sum`/membership over `a[i]`, and the
subscript-projection comprehension content law. Keep everything the recursion can't type as the documented
scalar fallback.

**S6 — self-annotate mirror re-verify.** The emitter's own nested structures (if any reach the changed
paths) re-verify; mirror-sync green, `\trusted` non-increasing.

---

## 4. Critical files
- `src/pycsl/frontend/Module5_IREmitter.py` — `_m5_get_dict_value_type` → the generalized
  `_m5_annotation_to_whyml_type`; the param/local/return element-type tagging.
- `src/pycsl/module6_whyml/functions.py` — `_param_type_str` (list→array, the `matrix` 2-D path),
  `_seq_value_types`/`_array_elem_types`/`return_value_type` plumbing.
- `src/pycsl/module6_whyml/types.py` — RHS classification (`_rhs_yields_array`, first-assign kind).
- `src/pycsl/module6_whyml/expressions.py` — subscript lowering (S3), the element-type-aware read paths.
- `src/pycsl/module6_whyml/preamble.py` — `needs_array`/`use array.Array`/`seq.Seq`/`matrix.Matrix`
  imports for the nested type actually chosen.

## 5. Out-of-scope / soundness
- **Mutable nested aliasing** — `array (array int)`'s inner arrays alias; if in-place nested mutation
  (`a[i][j]=v`, `a[i].append(...)`) isn't in the shipped representation, REJECT it or keep it opaque with
  a documented boundary — never emit an unsound update. (The read-only `seq (seq int)` model sidesteps this.)
- **Un-annotated / unknown-leaf lists** stay `array int` (the scalar default) — documented residual, never
  a false nested claim.
- **Depth bound** — cap nesting; deeper falls back to scalar + note (avoid emission/E-matching blowup).
- **Ragged vs rectangular** — a `matrix` model assumes rectangular; `array (array _)`/`seq (seq _)` allow
  ragged. Pick per the spike; document the assumption.
- No new global axiom (this is a type-representation change; the nested read/index laws are Why3 stdlib).

## 6. Gates (FEATURE — not byte-diff 0)
Full corpus PROVES (`PYTHONHASHSEED=0 PYCSL_SKIP_CONFORMANCE_CHECK=1 bin/run-reference-tests.sh --pycsl`;
the 3 pre-existing failures 0540/0700/0701 are NOT regressions); emission differential = EXACTLY the
nested-collection programs (flat `List[int]`/`Dict[..]` byte-identical — verify); the `cleared-array`
subscript-projection driver flips from opaque to content-faithful; `proof_axiom_allowlist` unchanged;
mirror-sync green; 5-surface docs (τ-table: `List[List[T]] ~ array (array τ)` / chosen repr;
concrete/static/translational; the mutation + ragged + depth residuals) + `annotations.md` updated,
`bin/doc-coherency.py --check` green. HIGH blast radius → sweep after S2, S3, S4.

## 7. Reference corpus
- Nested read: `List[List[int]]` param, `#@ ensures \result == a[i][j]` (content through two indices).
- `len(a[i])` inner length.
- Subscript-projection comprehension `[x[k] for x in a]` over `List[List[int]]` → `result[i] == a[i][k]`
  (the cleared-array boundary now lifted) + its positive driver.
- `List[Dict[str,int]]` element `a[i][key]` faithful read (composes with cleared-hash `map string`).
- NEGATIVE `# pycsl-expected: FAIL`: a false nested-content claim (`\result == a[i][j]+1`) stays unprovable;
  and — if nested mutation is out of scope — a driver showing `a[i][j]=v` is rejected/opaque, not silently
  accepted.

**Expected outcome:** nested lists carry their real structure (`array/seq (array/seq τ)`,
`array (map ..)`), inner elements are indexable and content-faithful, and the cleared-array
subscript-projection boundary is lifted. In-place nested mutation, ragged-vs-rectangular beyond the chosen
repr, and unknown-leaf lists remain the honest, documented residual.

---

## 8. OUTCOME (branch ghost-assign-bc6)

**Representation chosen: `List[List[τ]] ~ array (seq τ)`; `List[Dict[str,int]] ~ array (map string (option int))`.**
The Gate-B spike (`test-suite/corpus/conformance/spikes/nested-list.mlw`) proved `array (array τ)` is
Why3 TYPE-REJECTED (a mutable element inside `array` — "instantiates pure type variable 'a with a mutable
type"). `array (seq τ)` wins: outer `array` stays byte-identical to a flat list; inner `seq`/`map` is a
PURE type. All spike goals Valid (Alt-Ergo 0.03s / Z3 <0.02s), incl. nested read `a[i][j]`, inner length,
outer row-replacement `a[i]=row`, and the subscript-projection `[x[k] for x in a]`. Decision in `choices.md`.

**Stages — all landed:**
- **S0 spike** — DONE. `choices.md`, committed fixture `spikes/nested-list.mlw`.
- **S1 one recursion** — DONE. `Module5_IREmitter._m5_annotation_to_whyml_type` (element-position pure
  type, depth-bounded ≤4) + `_m5_get_list_nested_elem_whyml`. The existing `_m5_get_dict_value_type` is
  consistent (it already returns `seq τ`/`map ..` in value position); the `matrix int` path is kept
  disjoint (`\length2d`-contract-only, nested-annotated params excluded from `array2d`).
- **S2 element type into list emission** — DONE. `param_list_nested_elem` threaded Module5→Module6;
  `_param_type_str` emits `array (seq τ)` / `array (map κ (option ν))`; preamble imports gated. Flat
  lists BYTE-IDENTICAL (verified: full 677-file corpus emission diff = 0).
- **S3 `a[i]` yields the inner collection** — DONE. `_handle_subscript` routes `a[i][j]`→`Seq.get`,
  `a[i][key]`→`Map.get` (`_list_nested_elem`). `len(a[i])`→`Seq.length` (`_handle_len_call`). Drivers
  0797/0798/0800.
- **S4 nested comprehension source** — DONE (LIFTS cleared-array subscript-projection). `_content_comp` →
  `_nested_subscript_comp` emits the per-index content law `result[i] = Seq.get (a[i]) k`, captured index
  var threaded as an extra val param. Driver 0799; the `cleared-array.md` boundary note flipped to LIFTED.
- **S5 consumers + `len`** — DONE (inner `len` above; subscript-projection content law).
- **S6 self-annotate mirror** — the changed emitter methods are additive and inert on `@mutable_state`
  paths; nested-annotated params absent from the mirror. Mirror-sync green, `\trusted` non-increasing.

**cleared-array subscript-projection boundary: LIFTED** (driver 0799 proves `\result[i] == a[i][k]`).

**Emission differential** = exactly the new nested-collection programs. Flat `List[int]`/`Dict[..]`
byte-IDENTICAL across all 677 corpus files (before/after `.mlw` diff empty). No `proof_axiom_allowlist`
change (definitional `ensures`; Seq/Map read laws are Why3 stdlib). doc-coherency `--check` green.

**Drivers added:** 0797 (nested read), 0798 (inner len), 0799 (subscript-projection comprehension —
boundary lifted), 0800 (`List[Dict[str,int]]` element read), 0801 (NEGATIVE false nested content),
0802 (POSITIVE in-place inner mutation read-back — see §9), 0803 (POSITIVE non-aliasing — §9),
0804 (NEGATIVE non-int-leaf inner mutation rejected — §9).

**Residual boundaries (honest, never a false claim):** (1) in-place INNER ELEMENT mutation `a[i][j]=v`
is now SUPPORTED for RECTANGULAR int-leaf `List[List[int]]` via the mutable `matrix int` model (§9);
a NON-int-leaf inner mutation, `a[i].append(..)` (shape-change), and ragged in-place mutation remain
boundaries (§9); (2) `a[i][j][k]` deeper than 2 levels, and a target-dependent comprehension index
`x[f(x)]` — opaque; (3) an un-annotated / bare-`list` nested param, or a leaf deeper than the depth
bound — stays `array int`; (4) a `\length2d`-contract rectangular param stays `matrix int`.

---

## 9. OUTCOME 2 — in-place inner element mutation `a[i][j]=v` (nested-list-mutable, branch ghost-assign-bc6)

**Representation chosen: an in-place inner-mutated `List[List[int]]` ~ `matrix int`** (the mutable
built-in Why3 2-D structure), coexisting per-param with the read-only `array (seq τ)` model.

**Gate-B spike** (`test-suite/corpus/conformance/spikes/nested-list-mutable.mlw`, decision in `choices.md`).
Compared `matrix int` vs flattened `array int`+offsets (both tractable; `array (array int)` already
type-rejected). The emitted imperative `let` VCs — read `Matrix.get`, update read-back
`(set a i j v; get a i j)=v`, non-aliasing `(i2,j2)≠(i,j) → get unchanged`, `dims_preserved`, `innerlen`
— all **Valid in BOTH Alt-Ergo (≤0.05s) AND Z3 (≤0.01s)**. (Z3 times out only on the pure ghost-`update`
GOAL forms — map-update E-matching — which are NOT emitted; Alt-Ergo proves them; per
`smt_timeout_not_unprovable` an SMT timeout on a non-emitted goal is not a boundary.) `matrix` WINS on
tractability + built-in status (zero custom machinery; the plan's natural target).

**Coexistence strategy (usage/mutation analysis).** A nested-list param has ONE WhyML type. Module5
`_collect_inner_mutated_params` detects the `a[i][j]=v` write; an INT-leaf inner-mutated param is dropped
from `param_list_nested_elem` and kept in `array2d_params` → emitted as `matrix int`. A read-only nested
param stays on `array (seq τ)` (ragged-capable). This is the SOUND minimal-disruption choice: the landed
read drivers 0797/0798 use RAGGED inputs and prove per-row `len(a[i])`, which a rectangular `matrix`
(single `columns`) cannot express — so UNIFYING all rectangular-int nested lists onto `matrix` was
rejected (would break 0797/0798). Lowering: `a[i][j]=v`→`Matrix.set`, `a[i][j]`→`Matrix.get`,
`len(a)`→`a.rows`, `len(a[i])`→`a.columns` (the last two new in `_handle_len_call`).

**What now works vs stays boundary.** WORKS: rectangular int-leaf `a[i][j]=v` read-back (0802) +
non-aliasing (0803), fully usable alongside `a[i][j]` read and `len`. BOUNDARY (honest, never a false
claim): a NON-int-leaf inner mutation (`List[List[str]]` = immutable `array (seq string)`) is REJECTED
(hard type/verification failure; NEGATIVE 0804); `a[i].append(..)` (shape-change / nested growable) stays
OPAQUE (`append_1` no-op — no false post-state claim); ragged in-place mutation is out of the rectangular
`matrix` model (UB catalog §7.8 — the rectangular assumption is a structural precondition, same stance as
the `\length2d` matrix path). No unsound update is ever emitted (Matrix get/set/frame are Why3 stdlib).

**Emission differential** = EXACTLY the new mutable-nested programs. Read-only nested drivers 0797–0800
and flat `List[int]`/`Dict[..]` byte-IDENTICAL (the routing fires only on a nested param the body
inner-mutates via `a[i][j]=v` — no passing corpus file did this before). No `proof_axiom_allowlist`
change. doc-coherency + mirror-sync green.
