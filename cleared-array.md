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

---

## 8. OUTCOME (landed)

### Round 1 (commit dcaf2367) — S1, S3, S4, S5
- **S1 identity** `[x for x in a]` → `result[i] == a[i]`: LANDED (0761).
- **S3 arithmetic** `[x+1 for x in a]` → `result[i] == a[i]+1` (pure-int `+ - *`): LANDED (0762).
- **S4 filter** `[x for x in a if …]` → `len result <= len src` only: LANDED (0763).
- **S5 `sorted`** → permutation + adjacent-sortedness + equal length: LANDED (0760).
- Round 1 kept **projection** and **call** OPAQUE ("int-heavy model — don't reliably lower to pure-int
  logic terms").

### Round 2 (this run, branch ghost-assign-bc6) — S2 projection LIFTED; call/subscript stay opaque
**Spike (GO).** `proj_call_spike.mlw`: the per-index projection law `result[i] = get_f(src[i])`
consumed at a driver use-site at TWO indices, and the call law `result[i] = g(src[i])` with a
propagated `ensures`. Why3 1.8.2:
| VC | Alt-Ergo | Z3 |
|---|---|---|
| test_proj (projection law, 2-index) | Valid 0.03s / 27 steps | Valid 0.01s / 7014 steps |
| test_call (call law + propagated post) | Valid 0.03s / 22 steps | Valid 0.01s / 7161 steps |
Both SMT-tractable, no E-matching blowup. The SMT law was never the obstacle.

**S2 projection `[p.x for p in a]` / `[p.x + p.y for p in a]` — NOW CONTENT-FAITHFUL.** Root
diagnosis: in the int-collapsed list model a source element is an `int`, so `p.x` lowers to the
abstract getter `get_x : int → int`. That is FINE for a content law (`result[i] = get_x(src[i])` is a
faithful re-expression of `a[i].x`) once TWO gaps are closed:
1. The getter was a program `val` (non-deterministic, unusable in an `ensures`). Fix: emit it as a
   pure `val function` in spec context (`_handle_attribute_expr`, gated on `self._in_spec`). Sound
   refinement (a field read *is* deterministic); INERT on the corpus (0 of 105 getattr-in-contract
   files emit a spec-context `get_` fallback).
2. The contract grammar could not PARSE the consumer `a[k].x` (subscript-then-projection). Fix: a new
   `SubscriptFieldAccess` atom (`Module2_Parser` + `Module5_IREmitter`) lowering to
   `Attribute(Subscript(…), field)` — the SAME IR the body path produces.
The `_content_comp` whitelist now accepts `Attribute` element nodes over the target (and arithmetic
over them). Drivers: 0769 (projection), 0770 (arithmetic-over-projection), 0771 (NEGATIVE — a false
`result[k] == a[k].y` on an `[p.x …]` comprehension is correctly rejected, clean Unknown not a
typecheck error).

**Call `[g(x) for x in a]` — STAYS OPAQUE (documented, sharpened).** A module function `g` lowers to a
program `let g`, which is NOT usable in a logic term; a driver's own `\result == g(a[i])` does not even
type-check today (`unbound function or predicate symbol 'g'` — demonstrated). Lifting the call would
require a separate language feature (purity analysis + spec-callable `let function` emission), and
there is NO existing consumer. YAGNI exit; not a limitation of the comprehension path.

**Subscript projection `[x[k] for x in a]` — STAYS OPAQUE (documented, sharpened).** The source
`List[List[int]]` / `List[Dict[…]]` collapses to `array int` (empirically verified), so `x` is an `int`
and `x[k]` has no faithfully-typed collection element to index — the recent `map string` dict model
never reaches a *list element*. No faithful law is expressible.

**Dict/set comprehensions (S6), `reversed` — unchanged** (Round-1 residual; choices.md).

**Gates:** corpus proof sweep green (no new regressions beyond 0540/0700/0701); emission differential =
exactly the comprehension/projection programs (getter `val function` toggle inert on all existing
files); doc-coherency green; NO new `proof_axiom_allowlist` entry (definitional `ensures` on the
abstract val, discharged at the use site).
