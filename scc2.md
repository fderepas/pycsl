# scc2.md — the lemma-fact ordering gap, and what `scc.md` does / does not cover

Companion to `scc.md`. Implementing `scc.md`'s contract-reference edges surfaced that its Phase-4
**P2 quantified-wrapper** example needs a *second*, distinct ordering that the contract-edge mechanism
does not provide. This doc records (1) what the full P2 wrapper still needs, and (2) what `scc.md`
deliberately or inadvertently left undone.

## Background: the two ordering needs, separated

The P2 quantified-fact wrapper (the recursive-datatype case):

```python
#@ datatype Nat = Z | S(Nat)

#@ \variant n
#@ assigns \nothing
def to_int(n: Nat) -> int:
    match n:
        case Z():  return 0
        case S(m): return 1 + to_int(m)

#@ lemma                                  # proves the universal by induction
#@ ensures to_int(n) >= 0
#@ \variant n
#@ assigns \nothing
def to_int_nonneg(n: Nat) -> None:
    match n:
        case Z():  pass
        case S(m): to_int_nonneg(m)

#@ ensures \forall x: Nat; to_int(x) >= 0   # the wrapper — the goal we want discharged
#@ assigns \nothing
def all_nonneg() -> int:
    return 0
```

It has **two** independent ordering requirements:

- **(A) `to_int` must precede `all_nonneg`.** `to_int` is *named* in the wrapper's `ensures`, so emitting
  the wrapper first yields Why3 `unbound function or predicate symbol 'to_int'`. **This is a contract
  *reference* — exactly what `scc.md` fixes, and it is done.** (Verified: with the contract-edge fix,
  `to_int` now emits before `all_nonneg`.)
- **(B) the lemma `to_int_nonneg` must precede `all_nonneg`.** The wrapper's goal `forall x. to_int x
  >= 0` is discharged by the lemma's exported *general fact* `forall n. to_int n >= 0`, which is in
  scope only for goals emitted *after* the lemma. **But the wrapper never *names* the lemma** — the
  dependency is on the lemma's proven fact, not on a symbol. So no contract-reference edge exists, and
  `scc.md`'s mechanism does nothing for it.

(A) is a **symbol-reference** dependency (well-formedness: unbound symbol if violated). (B) is a
**proof** dependency (the WhyML is well-typed either way; it just fails to *discharge* if the fact
isn't in scope). Observed today, after the contract-edge fix: the wrapper compiles (no unbound symbol)
but the proof comes back **`Unknown` / timeout** — the SMT backend tries the universal directly, can't
do the induction, and never sees the lemma's fact because the lemma is emitted after the wrapper.

---

## 1. What the full P2 quantified-wrapper needs (beyond `scc.md`)

Closing (B). Four candidate mechanisms, best-fit first:

1. **`#@ by induction on x` on the wrapper (preferred — quantification.md P2's original mechanism).**
   Drive Why3's `induction_ty_lex` (structural) / `induction_pr` transformation on the tagged goal in
   the proof harness. The wrapper proves its own universal **without any separate lemma** — so there is
   no ordering problem to solve at all. Cleanest because it makes the wrapper self-contained.
   *Work:* recognise the `#@ by induction on <binder>` clause (parse + weave) and, in the proof engine
   where Why3 is invoked, apply the induction transformation to that goal before dispatch.

2. **A `#@ uses <lemma>` citation (fits `scc.md`'s model — turns (B) into a named reference).
   ✅ IMPLEMENTED — this is the route taken.** Driver `0565` shows the full P2 wrapper discharging via
   `#@ uses to_int_nonneg` (no body call): the citation adds an ordering edge through the very SCC
   machinery `scc.md` added → the lemma is emitted before the wrapper → its general fact is in scope →
   the `\forall` goal discharges. Subtlety borne out in practice: an *explicit lemma call*
   (`to_int_nonneg(t)`) instantiates the fact at one argument `t`, which does **not** by itself
   discharge a `forall`-over-all-`x` goal; the citation's job is purely **ordering** — the lemma's
   *general* fact (in scope once emitted-before) does the discharging. `#@ uses` is exactly that
   non-instantiating, ordering-only clause (emits no WhyML). The right shape is a clause that
   *forces the order without instantiating*. Small, reviewable, consistent with "ordering follows
   declared intent."

3. **Lemma-priority ordering (heuristic — not recommended).** Emit every lemma as early as its own
   dependencies allow (a lemma is a globally useful fact). It would make the wrapper pass with no new
   surface. But it is exactly the kind of *implicit* ordering `scc.md` argued against: the order would
   follow a global heuristic rather than a declared dependency, it has its own byte-diff impact on
   files containing lemmas, and it hides the wrapper→lemma reliance from the reader.

4. **Source-order tie-break (rejected here).** If independent declarations broke ties by source order,
   the lemma (written before the wrapper) would emit first and the wrapper would discharge. But
   `scc.md` explicitly **unbundled** the tie-break (it is byte-diff-risky and a separate change), and
   relying on source order is fragile — reorder the source and the proof silently breaks. Not a fix.

**Recommendation:** close (B) with **(1) `#@ by induction on`** for the self-contained case and/or
**(2) a `#@ uses` citation** for genuine lemma reuse — both express the dependency *explicitly*, the
same principle that motivated `scc.md` (orderings should reflect declared references, not luck or
global magic). Avoid (3)/(4) for the same reason `scc.md` rejected body-only edges.

This work belongs to **quantification P2**, not to `scc.md`: `scc.md` is the *prerequisite* (it
supplies (A)); (B) is P2's own remaining step.

---

## 2. What was NOT done in `scc.md`

`scc.md` (as implemented) delivers the contract-**reference** edge mechanism, and only that. Verified
working on the named-reference regression twin (a function whose contract references a pure helper
defined later in source, no body call — the helper now emits first and it proves). Explicitly *not*
covered:

- **(B) lemma-fact ordering — the implicit proof dependency above. ✅ NOW CLOSED (separately, by
  `#@ uses`).** `scc.md`'s contract-edge mechanism alone does not make the wrapper pass — it fixes only
  the named `to_int` ordering (A), after which the wrapper still times out for lack of the lemma's fact
  (B). **`scc.md` Phase 4 conflated (A) and (B).** So the `scc.md` fix landed with the **named-reference
  twin** (`0564`, caller cites a pure helper) — what its mechanism actually enables — and (B) was closed
  *afterwards* by the `#@ uses` citation (§1.2 above; driver `0565`). The two are distinct edges through
  the same SCC machinery: (A) is a contract *reference*, (B) is an explicit *citation*.

- **Source-order tie-break** — `scc.md` Phase 3 deliberately *unbundled* it as a separate,
  byte-diff-gated change. Still not done; the SCC order for independent declarations is whatever the
  existing Tarjan traversal produces (the contract-edge fix only *adds edges*, it does not touch
  tie-breaking).

- **Rejecting impure contract references** — `scc.md`'s "Unbundle" section flagged this as a separate
  *policy* decision (today an impure reference in a contract lowers to an abstract `val`, which is
  harmless for ordering). Not implemented; references to non-logic symbols still get no edge and no
  rejection.

- **A Module-4 contract-purity well-formedness check** — related to the above; `scc.md` noted impure
  contract calls are "really a well-formedness error," but enforcing that is unbundled and unbuilt.

- **The Phase-0 diagnostic / whole-corpus byte-diff gate** — the contract-edge fix is implemented and
  verified on the twin, but the gating measurement (whole-corpus emission byte-diff confirming the only
  changes are legitimate reorderings, with *no* SCC-membership change on previously-compiling files) is
  the step that must pass before the fix is committed. At the time of writing it is running, not yet
  complete; the fix is therefore staged, not landed.

## Net

`scc.md` closed the **named-reference** ordering gap (A) — `ff11f18`, driver `0564`. The **full P2
quantified-wrapper** needed one more, orthogonal piece — making the lemma's fact available (B) — and
that is now done via the **`#@ uses` citation** (driver `0565`), *not* via a tie-break or a global
lemma-priority heuristic. Both routes go through the same SCC machinery (a reference edge for (A), a
citation edge for (B)). The full P2 wrapper now **discharges**. (`#@ by induction on` — the
self-contained, lemma-free alternative of §1.1 — remains an open future ergonomic, not needed for the
wrapper to pass.)
