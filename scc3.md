# scc3.md — unblocking quantification P3 & P4 (the binder/domain type-propagation gap)

Third in the series (`scc.md` = contract-reference ordering; `scc2.md` = `#@ uses` lemma-fact
ordering; this = making typed quantifier bodies *discharge*). P1 gave typed binders, P2 made the
recursive-datatype wrapper prove. P3 (sets) and P4 (objects) are **stop-and-flagged**: their *surfaces*
work but their bodies don't discharge, because a quantifier's **binder type** (P4) and **domain type**
(P3) are not carried into the body's member-access / membership lowering. This plan closes that.

It is a *plan for review* — no code yet. Everything below is grounded in the current tree.

## Grounding (verified)

- **P1 sets the binder sort, not the body's type environment.** `\forall o: C; …` lowers to
  `forall o : c. <body>` (correct sort), but the body emission has no record that `o : c`.
- **P4 blocker — `o.x` → `get_x o`.** A quantifier-bound record var's field access is an `Attribute`
  node; `expressions.py::_handle_attribute_expr` (≈:1398) falls to the getattr stub
  `val get_x (x:int):int` + `(get_x o)` because it doesn't know `o : c`. Probed:
  `\forall o: C; o.x >= 0` emits `forall o : c. ((get_x o) >= 0)` → Why3 `unbound … 'get_x'`.
- **P4's hard part is already free.** A `#@ class invariant self.x >= 0` is emitted as a **Why3 type
  invariant**: `type c = { mutable x: int } invariant { (x >= 0) }`. A Why3 type invariant holds for
  *every* value of `c`, so `forall o : c. P(o)` gets it automatically — **no explicit
  invariant-antecedent insertion is needed** (the plan's original P4 task). Only the `o.x` lowering
  blocks it.
- **P3 blocker — `x in S` is desugared positionally in Module 5.** `Module5_IREmitter._csl_in`
  (≈:342) lowers *every* `x in S` to a positional sequence membership
  `exists _mem. 0 <= _mem < length(S) /\ S[_mem] = x`, regardless of whether `S` is a list or a set.
  For a **set** `S` (a `map int (option int)`, which has no positional order) this is both unsound and
  ill-typed — it emits `Array.length S` / `Map.get S _mem` on a map → `unbound … 'Array.length'`.
  (`symbol_table` *does* record `S: set`; the desugar in `_csl_in` simply doesn't consult it.)
- **A clean set-membership encoding already exists** but on a different path:
  `expressions.py::_emit_membership` (≈:247-251) emits
  `match Map.get S x with Some _ -> true | None -> false` for a set-typed RHS — key membership, no
  positional `exists`. The generic `in` (via `_csl_in`) never reaches it.
- **Even the correct (list) seq-membership doesn't discharge without a trigger.** Probed over a
  *list*: `forall x. (exists i. 0<=i<len ∧ xs[i]=x) -> P` + hypothesis `k in xs` returns **Unknown** —
  the nested `exists` antecedent does not e-match. (This is the brittleness the quantification plan
  flagged for P3.)

So there are **two facets** of one theme ("the body's type/instantiation environment for a quantified
contract is incomplete"), with **distinct fixes**, P4's being the clean win.

---

## Phase A — P4 value mode: propagate the binder type into field access (the clean win)

**Goal.** `\forall o: C; <P over o.field>` discharges, with the class invariant supplied free by the
Why3 type invariant.

**Mechanism.** When emitting a `Forall`/`Exists` whose `binder_type` is a declared class/record,
register `var → <record type>` in a small **binder-type context** for the duration of the body
emission (push on enter, pop on exit — nesting-safe), then have the member-access lowering consult it:

- `expressions.py::_handle_attribute_expr` / `_handle_field_get_expr`: if `obj` is a bound var in the
  binder-type context and `field` is a field of that record, emit `obj.<field>` (qualified via the
  existing `_field_label(<record>, field)`) instead of the `get_<attr>` stub.

This is the *only* change P4 value mode needs — the invariant is already on the type. It reuses the
record-field machinery (`_all_record_fields`, `_field_label`) already used for `self.field`.

**Scope / risk.** Byte-diff-safe for existing corpus: no existing file quantifies over a class
instance, so no existing `obj.field` lowering changes (the new branch only fires for a registered
quantifier-bound record var). Gate on a whole-corpus byte-diff (expect 0 changed files).

**Drivers (Gate-A-first).**
- PASS: `\forall o: C; o.x >= 0` for `C` with `#@ class invariant self.x >= 0` (the probed case) —
  fails today (`unbound get_x`), passes with the fix.
- PASS: a two-field invariant relating fields (`self.lo <= self.hi`) quantified over `C`.
- FAIL twin: the same with **no** class invariant → `forall o: c. o.x >= 0` ranges over
  invariant-free records and is correctly **unprovable** (proves the invariant guard is load-bearing,
  i.e. that the type-invariant is what makes the PASS sound).

---

## Phase B — P3 set membership: dispatch `_csl_in` on the domain type

**Goal.** `x in S` for a set `S` lowers to key membership, not positional sequence membership, so it is
sound, well-typed, and e-matching-friendly.

**Mechanism.** `Module5_IREmitter._csl_in` must branch on the collection's type:
- **set/dict/frozenset** (per `symbol_table` / the resolved type of `node.collection`) → emit a
  set-membership IR node that Module 6 lowers to the clean `Map.get S x` key test (reuse the
  `_emit_membership` map encoding at expressions.py:247-251, or a dedicated `SetMem`-style node) —
  **no positional `exists`, no `Array.length`**.
- **list/array** → keep the current positional `exists` (correct there).

Module 5 has the function `symbol_table` available (it is emitted onto the IR), so `_csl_in` can look
up `node.collection`'s type; if the type isn't locally resolvable (e.g. a nested expression), fall back
to the current behavior. The desugar should preserve the binder/element so Phase C can attach a trigger.

**Scope / risk.** This changes the lowering of `x in S` for **set-typed** collections — which is
currently *broken* (ill-typed `Array.length` on a map), so any corpus file relying on `in` over a set
either doesn't exist or is already failing. Still, gate on a whole-corpus byte-diff and inspect every
changed file: a change should appear only for set-typed `in`, and should turn a previously-broken
emission into a well-typed one. Bounded quantification over a set may then discharge via natural
e-matching on `Map.get S x` even before Phase C.

**Drivers (Gate-A-first).** (Requires the bounded-form surface — the ~15-line transformer desugar
`\forall x [: T] in S; P ≡ \forall x [: T]; (x in S) ==> P`, reverted in this session, re-landed here.)
- PASS: `requires \forall x: int in s; x >= 0`, `requires k in s`, `ensures \result >= 0`,
  `def pick(s: set, k: int): return k` — instantiate the bounded universal at the member `k`.
- FAIL twin: drop `k in s` → the conclusion no longer follows (membership guard is load-bearing).

---

## Phase C — P3 triggers (the brittle part; do only if Phase B isn't enough)

**Goal.** Robust instantiation of bounded quantifiers when natural e-matching is insufficient (deep
bodies, list membership's nested `exists`).

**Mechanism.** For each emitted bounded quantifier, select a trigger from the body's membership /
pure-function / field terms that mentions every bound variable, refuse interpreted-only patterns
(`+`,`*`,`and`, nested quantifiers — matching-loop risk), and emit Why3 `[pattern]` syntax;
`#@ trigger f(x), g(x)` overrides; Module 4 warns when no admissible trigger exists ("valid but never
instantiated"). This is explicitly the **MEDIUM-risk, brittle** part — keep it behind its own drivers
(a missing-trigger FAIL twin; a trigger-override regression asserting loop-free selection) and do not
let trigger selection bleed into Phases A/B.

**Note.** Phase B's `Map.get S x` membership is itself a clean trigger term, so set-bounded
quantification may not need Phase C at all; lists (positional `exists`) are the case most likely to.

---

## Multi-binder (small, independent)

`\forall x: T, y: U; P` — desugar to nested binders in the transformer. Independent of A/B/C; land
whenever a driver wants it.

---

## Gates (every phase)
- **Byte-diff (additivity):** whole-corpus emission byte-identical except the intended cases (Phase A:
  0 changed; Phase B: only set-typed `in`), all four memory models, `PYTHONHASHSEED=0`. Assert no
  SCC-membership change on previously-compiling files (the scc.md discipline).
- **Gate-A driver first** per phase; FAIL twins stay failing.
- **Why3 type-checks** every accepted typed/bounded quantifier (the spec §11 false-green gate).

## Recommended order & why
**A → B → C.** Phase A (P4 value mode) is the cleanest, highest-leverage win — one localized
field-access change, the invariant is free, byte-diff-trivially-safe — so it lands first and validates
the binder-type-context mechanism. Phase B (P3 set membership) is medium (a Module-5 type-dispatch in
`_csl_in`, touching currently-broken set-`in` emission). Phase C (triggers) is the brittle tail — gate
hard, do last, and only if B's natural e-matching is insufficient.

## What this plan does NOT do
- It does not add an `Fset` theory import — the existing `map int (option int)` set model with key
  membership (`Map.get`) is sufficient for bounded quantification; `Fset` would only be needed for
  cardinality/union lemmas (a separate, later concern).
- It does not touch the P4 **ghost-collection mode** (`\forall o: C in registry; …`) — that composes
  Phase A (class binder) with Phase B (set membership over a ghost `set[C]`); land it after both, on
  its own driver.
- It does not implement `#@ by induction on` (the lemma-free P2 alternative) — orthogonal, still open.
