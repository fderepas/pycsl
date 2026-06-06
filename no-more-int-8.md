# Plan: no-more-int Part 8 — the residual after Part 7

Standalone successor to `no-more-int-7.md`. Part 7 was *executed end to end*, which both cleared most
of the backlog and — by actually attempting the parked/follow-on items — replaced vague "build on
demand" entries with **precisely-diagnosed blockers**. That is the value of this document: every
remaining item now has a concrete technical reason it isn't done and a concrete dependency that would
unblock it. The honest status is unchanged: **the no-more-int program is essentially complete**; what
remains is a small set of well-scoped follow-ons plus one large *contingent* item (the alias checker)
that §0 showed is not on the self-hosting critical path.

The Gate-A demand-driver discipline still holds (FAIL-driver first → implement → full sweep +
emission-identical byte-diff). House style: re-derive `file:line` by symbol.

## Where we are after Part 7 (all committed + pushed; corpus green at 505 files)

| Built in Part 7 | Drivers |
|---|---|
| **§0 alias audit** — pycsl is alias-clean (`docs/pycsl-alias-audit.md`) | — |
| **A4** inductive framing demo — `mirror(mirror x)==x` over recursive `Json`, imported axiom proved by structural induction (Rocq+Lean) | 0542 |
| **A2b-1** ownership-discipline spec (`docs/pycsl-ownership-discipline.md`) | — |
| **A1-residual** seq-snapshot array-valued dicts | 0543 |
| **Crude R2** — reject mutable default args | 0544 |
| **A5b** multi-payload `\payload(x, Ctor, i)` · **A5c** or-pattern payload binding (already worked) | 0545 · 0546 |
| **A3-residual** — `product` + `islice` length | 0547 · 0548 |
| Earlier (Part 5–7): A2b framing demo (0537–0539), A1-residual nested-map (0532), A3 chain (0530), A5a-residual (0533/0534), A5b projectors (0541), A5c guards/or/nested (0531/0535/0536), A5d construction-based parametric (0540) | — |

---

# PART A — feature gaps the execution SURFACED (each unblocks a parked follow-on)

These are the genuinely new, well-scoped items. Each was hit while attempting a Part-7 follow-on and
is the *real* dependency behind it.

## A8-1 — A5d use-site parametric instantiation  (unblocks type-param `\payload`)
**Blocker found:** A5d (0540) instantiates a parametric datatype by *construction* (`Just(7)` infers
`'a=int`), but a use-site *annotation* `o: Option[int]` does **not** instantiate — the param types as
polymorphic `option 'mu`, so `\payload(o, Just)` fails with "option 'mu, expected int", and any
function taking an annotated parametric param mistypes.
- **Fix:** thread the `[int]` from a `Name[...]` datatype annotation through `Module4` type capture →
  `module6_whyml/functions.py::_param_type_str` so `o: Option[int]` emits `(o: option int)` (the
  param-type analogue of A5d's payload resolution). Then type-param `\payload` works at any
  instantiation, with a polymorphic default `function any_default : 'a` (verified to typecheck/prove
  in Why3) for the dead fall-through arm under the `\is_ctor` guard.
- **Gate / driver:** `def f(o: Option[int]) -> int` with `requires \is_ctor(o, Just)` / `ensures
  \result == \payload(o, Just)`; plus an `Option[str]` sibling to exercise the polymorphic default.
- **Risk:** medium (param-type plumbing + the polymorphic default). **Verdict:** the cleanest of the
  surfaced items; do it when a parametric-datatype-in-contracts driver appears.

## A8-2 — proper array membership `x in arr`  (unblocks chain membership)
**Blocker found:** `x in arr` for an `array int` is **ill-typed today** — the generic `contains_check`
fallback passes the array into an `int` param (`_coerce_str_arg` doesn't coerce arrays). Existing
files never hit it (they use set/dict/string membership). This is a *pre-existing* gap, surfaced by
chain membership.
- **Fix:** model array membership as the real quantified formula `(exists i: int. 0 <= i <
  Array.length arr /\ arr[i] = x)` (in spec context) — mirroring how `\array_eq` unfolds — instead of
  the opaque `contains_check`. Then **chain membership** decomposes for free: `x in chain(a, b)` →
  `(x in a) || (x in b)`, each operand using the real model.
- **Gate / drivers:** (a) `x in arr` with a witness index proves membership; (b) chain decomposition
  `x in a ⇒ x in chain(a, b)` (the 0549 driver the execution reverted).
- **Risk:** medium — touches the membership emitter; verify the existing set/dict/string membership
  paths stay byte-identical (the change is in the *array* fallback only). **Verdict:** worth doing —
  it fixes a real soundness/typing gap, not just chain.

---

# PART B — the ownership-enforcement tail (contingent / order-aware)

## A2b-2 — the alias-check frontend  (CONTINGENT, unchanged)
The full sound alias/ownership analysis. **§0 found pycsl alias-clean**, so this is **not on the
self-hosting critical path** — pull only if third-party code ever needs aliased mutation that must
verify. Gates (incl. the false-reject acceptance gate) are in `no-more-int-7.md` §A2b-2. **Verdict:
do not build absent that demand** — likely a permanent contingent item.

## R3 — store-then-mutate crude enforcement  (needs order-aware flow)
The remaining crude-enforcement check (R2 / mutable-default-args is **done**, 0544): flag `self.x = p`
(p mutable) followed by a mutation of `p`.
- **Blocker found:** a *sound* check needs **statement-order** awareness — `data.append(x)` *before*
  `self.data = data` is legitimate value-building, not R3; an "anywhere"-mutation flag false-rejects
  it. So a naive `ast.walk` heuristic is unsafe.
- **Fix:** a small intra-procedural pass that tracks, in body order, names stored into a self-field
  and flags a *subsequent* mutation of the same name. **Gate:** a positive R3 driver rejected; the
  store-then-no-mutate and mutate-then-store cases accepted (byte-identical corpus).
- **Risk:** low-medium (order-aware but intra-procedural). **Verdict:** nice-to-have hygiene; do when
  the order-aware pass is cheap to add, else leave documented (the boundary is specified regardless).

---

# PART C — imported-axiom follow-ons (the A4 / bridge-usage pattern)

A4 (0542) proved the bridge generalizes flat → inductive. These two are the *same move* on harder
proofs — both collapse from "research wall" to "bridge usage" once a driver appears (the
inductive→bridge-usage principle).

## A8-3 — full json round-trip `loads(dumps(x)) == x`
The headline A4 sequel: a real `decode ∘ encode = id` over a recursive `#@ datatype Json` (uses
recursive datatypes + nested-map `JObj`, both done). **The bridge usage is routine** (registry entry +
`#@ proof` + a `json.py`); **the proof is the work** — `decode` is not structurally recursive, so the
Rocq/Lean round-trip needs Narcissus-grade well-founded-recursion machinery (this is why 0542 used
the clean `mirror` involution instead). **Verdict: default don't-build absent a json-content driver**;
when pulled, it is a verified-parsing effort, not bridge plumbing.

## A8-4 — `combinations` length (binomial)
`len(combinations(a, r)) == C(len(a), r)` — a binomial coefficient, not first-order. **Fits an
imported axiom** (`C(n, r)` properties proved in Rocq/Lean, cited). Low value; build only on a driver.
(`product`/`islice`/`chain` length are done; lazy/infinite itertools stay out of scope.)

---

# PART D — closed (resolved, do NOT pursue)

## A6(b) — remove the int-dict store coercion — **CLOSED: verified unsafe**
The execution disproved the plan's premise. Removing the `else: _coerce_to_int(val_expr)` is **NOT
byte-identical** — it changes 0462's emission (a `self.disk[off] = v` store where the coercion is
load-bearing). Confirmed by byte-diff over all 85 dict-store files (0462 differs). **The defensive net
is not dead; leave it.** This item is closed, not parked — there is no safe removal.

---

## Out of scope (unchanged)
Lazy/infinite iterators (`cycle`/`yield`); faithful mutate-through-alias beyond the ownership
discipline; IDF/SL as a foundation (the Cameleer anti-pattern — escape-valve trigger defined in
`docs/pycsl-ownership-discipline.md` §6).

## Suggested order (by leverage)
1. **A8-2 array membership** — fixes a real soundness/typing gap; unblocks chain membership; clean
   quantified model.
2. **A8-1 A5d use-site instantiation** — unblocks type-param `\payload`; makes A5d annotations work,
   not just construction; do when a parametric-in-contracts driver appears.
3. **A8-3 json round-trip** — the highest-*demonstration*-value, but the proof is real work; pull on a
   json driver.
4. **R3 enforcement** — cheap hygiene when the order-aware pass is convenient.
5. **A8-4 combinations**, then **A2b-2** only if third-party aliased mutation must verify.

## Net assessment
Part 7's execution converted the backlog from "demand-gated unknowns" into "diagnosed follow-ons."
None is on a critical path: A2b-2 is contingent (pycsl alias-clean), the two feature gaps (A8-1, A8-2)
are medium-risk and unblock niche follow-ons, the imported-axiom items (A8-3, A8-4) are bridge-usage
gated on drivers, and A6(b) is **closed as unsafe**. The next milestone remains the **self-hosting
push**, not a verification feature — confirmed, not assumed, by the §0 audit.

## Critical files (re-derive line numbers by symbol)
- A8-1: `Module4_SemanticAnalyzer.py` (parametric annotation capture), `module6_whyml/functions.py`
  (`_param_type_str`), `module6_whyml/preamble.py` (`_fmt_variant` type-params).
- A8-2: `module6_whyml/expressions.py` (`_emit_membership` — the array fallback only).
- A8-3 / A8-4: `module6_whyml/preamble.py` (`_AXIOM_REGISTRY`/`_AXIOM_FUNCTIONS`, post-type-decl
  axiom emission), the recursive-datatype path, the `#@ proof` cross-check.
- R3: a new order-aware pass near `Module4_SemanticAnalyzer.py::_validate_no_mutable_defaults`.

## References
- Position/spec: `docs/handling-aliasing.md`, `docs/pycsl-ownership-discipline.md`,
  `docs/pycsl-alias-audit.md`, `docs/framing-lemma-demonstration.md`. Predecessors:
  `no-more-int-{3..7}.md`, `rq.md`. Canon: Creusot (ICFEM 2022), Narcissus (POPL 2019), Why3 (ESOP
  2013).
