# cleared-array.md — content-preserving comprehension model

**Goal.** Make list/set/dict comprehensions content-faithful: `[f(x) for x in src]` should let a driver
prove `result[i] == f(src[i])` and `len(result) == len(src)`, instead of the opaque `list_comp` /
`list_comp_stmts` that keep only a length + element-TYPE. Also covers `sorted`/`reversed`/`filter`.

**Feature** (emission changes). Incremental behind a spike: the make-or-break is lifting the element
expression into a DEFINING law; do it for the simple element shapes first, keep opaque for the rest.

---

## 1. Context / verdict (today, with citations)

- `[elt for t in src (if cond)]` lowers to an abstract array/seq with only a length law: over a seq
  source → `list_comp_seq`/`snapshot`; the `stmt-list` case → `val list_comp_stmts (src) : array int`
  (expressions.py:5018); the generic fallback → `val list_comp (x: int) : int` (5032). The element
  CONTENT is unmodeled — `result[i]` is arbitrary.
- `sorted` → `sorted_1`/`sorted_seq` (arbitrary array; the permutation AND sortedness are LOST).
  `reversed` → `array_rev`. `filter` → length `<=` only.
- **Root cause:** the element expression `f` is an arbitrary sub-expression, so it can't be attached to
  the result array as a per-index law without lifting `f` into a Why3 logic function.

**Verdict.** Emit a comprehension as a DEFINING function `comp_<n>(src)` whose `ensures` gives, for each
supported element shape, `Array.length result = <len> /\ forall i. 0<=i<len -> result[i] = <lifted f>(src[i])`.
Supported element shapes lift; unsupported fall back to the current opaque `list_comp` (documented).

---

## 2. Gate B — SMT-feasibility spike FIRST (hand-write `.mlw`)

Confirm a per-index defining law reasons tractably (a quantified `forall i` over an array is the classic
E-matching risk):

```whyml
module CompSpike
  use int.Int use array.Array use option.Option use map.Map
  (* map-comprehension: result[i] = f(src[i]) *)
  function f (x: int) : int
  val comp (src: array int) : array int
    ensures { Array.length result = Array.length src }
    ensures { forall i. 0 <= i < Array.length src -> result[i] = f (src i) }
  goal elt_law : forall src: array int, i: int.
      0 <= i < Array.length src -> (comp src)[i] = f (src i)     (* make-or-break *)
  goal len_law : forall src. Array.length (comp src) = Array.length src
  (* filter length bound (cond drops the ->=): *)
  val filt (src: array int) : array int
    ensures { Array.length result <= Array.length src }
  goal filt_len : forall src. Array.length (filt src) <= Array.length src
end
```
- Record **Valid + timing** (Alt-Ergo, Z3). If `elt_law` proves fast and doesn't blow up when instantiated
  at multiple indices, GO. If the quantified law slows the corpus sweep materially, restrict to the
  *identity* comprehension (`[x for x in src]`, content = `src[i]`) first and expand.
- Decide: array (mutable) vs seq (immutable) result shape reusing the existing `snapshot`/`materialize`
  bridge; the per-index law must survive the seq↔array coercion.

---

## 3. Stages (element shape by element shape)

**S0 — spike** → GO/NO-GO + timing.

**S1 — identity `[x for x in src]`.** `result[i] = src[i]`, `len = len src`. No lifting needed. The
simplest content law; unblocks the many "materialize a copy" comprehensions.

**S2 — projection `[x.field for x in src]` / `[x[k] for x in src]`.** Lift the element to a projection
function `proj(e) = <field/subscript>`; `result[i] = proj(src[i])`. Reuses the emit_ir/record projections.

**S3 — call `[g(x) for x in src]`** where `g` is a module function/method with a known signature. Lift `g`
to its logic symbol (or its abstract `val` with the propagated ensures); `result[i] = g(src[i])`.

**S4 — filter `[x for x in src if cond]`.** Keep the `len result <= len src` bound (already emitted), and
add the SOUND content-subset law only if `cond` lifts (else length-only). Do NOT claim the exact contents.

**S5 — `sorted`.** Model as a permutation-with-sortedness: `permut result src /\ sorted result` (Why3
`array.IntArraySorted`/`Permut`) for `array int`; for `sorted(seq string)` add a string-ordering sorted
law. This is a REAL theory add — spike it separately (S0-bis) before committing; it's the highest-value
but hardest. If the permutation predicate is intractable, keep `sorted_1` opaque (documented).

**S6 — dict/set comprehensions.** `{k: v for …}` → `map` with `Map.get result k = <lifted v>` per inserted
key; `{f(x) for x in src}` (set) → membership law. Guard on the key/value shapes lifting.

**S7 — self-annotate mirror re-verify.** The emitter's own comprehensions (e.g. `[self._expr_to_whyml(a)
for a in expr["args"]]`) gain content laws — re-run the mirror; may unblock `_split_tuple_type`
(leaf-campaign #36, a comprehension over `.split()`).

---

## 4. Critical files
- `src/pycsl/module6_whyml/expressions.py` — the `ListCompExpr` handler (~4974) + `list_comp`/`list_comp_stmts`
  emission (5018/5032) + the element-shape lifting.
- `src/pycsl/module6_whyml/preamble.py` — the `comp_<n>` `val` signatures + `use array.Array`/`array.Permut`
  for the sorted case.
- `src/pycsl/module6_whyml/statements.py` — seq↔array bridge interaction (`snapshot`/`materialize`).

## 5. Out-of-scope / soundness
- Only lift element shapes that map to a SOUND per-index law; unsupported elements (side-effecting,
  multi-generator, nested unliftable) stay opaque `list_comp`, DOCUMENTED — never a false content claim.
- `sorted`: `permut result src` is honest; `sorted result` is honest; do NOT claim stability unless
  modeled. `filter`: length bound only unless `cond` lifts.
- No new `proof_axiom_allowlist` entry (the `ensures` on the abstract `val` is a definitional contract,
  discharged where the comprehension is USED, not assumed globally).

## 6. Gates (FEATURE — not byte-diff 0)
Full-corpus proof sweep green (multiple, high blast radius); emission differential = exactly the
comprehension-using programs; mirror re-verifies; `list_comp`/`list_comp_stmts` opaque count drops per
shape migrated; τ-table + comprehension-semantics doc updated; NO new axiom.

## 7. Reference corpus
One driver per shape: `[x for x in a]` → `#@ ensures result[i] == a[i]`; `[x.f for x in a]`; `[g(x) for
x in a]`; `sorted(a)` → `#@ ensures is_sorted(result) and permutation`; `filter` length bound; a NEGATIVE
driver (`# pycsl-expected: FAIL`) asserting a false content claim. Update annotations.md + traceability.

**Expected outcome:** identity/projection/call comprehensions become content-faithful (`result[i] ==
f(src[i])`), `sorted` gains permutation+sortedness (if the spike holds), and the unliftable-element +
exact-filter-contents cases remain the honest residual.
