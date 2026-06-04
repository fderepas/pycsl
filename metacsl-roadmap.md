# Roadmap: toward cross-cutting properties in PyCSL (`act` → statement-assert → MetAcsl)

> Records the sequencing and the **shared-primitive** rationale for evolving PyCSL's
> contract surface toward MetAcsl-style meta-properties. Companion to `act.md`.

## What we want from MetAcsl — and what we don't

The value of a MetAcsl-style layer for PyCSL is **exactly one thing: cross-cutting,
whole-program security/integrity invariants over many functions** — e.g. "no function but
`encrypt` writes the secret page", "no read touches a higher-clearance buffer". One
*high-level requirement* (a HILARE) that **expands** into many ordinary per-site obligations,
discharged by the base verifier.

We explicitly **do not** want the part of MetAcsl/ACSL motivated by Frama-C's **multi-plugin
ecosystem** (WP/Eva/E-ACSL all consuming the same annotations). PyCSL has a single backend
(Why3/SMT via Module6); that coordination machinery buys us nothing. This is the same reason
PyCSL uses `act`/`given` rather than ACSL's `behavior`/`assumes`: we borrow the *idea*
(expand high-level → existing primitives → prove, 0-`\trusted`), not the vocabulary or the
plugin-shaped design.

## The through-line: every layer desugars to primitives the verifier already trusts

| Layer | Surface | Expands / desugars to | Scope |
|---|---|---|---|
| Contracts (today) | `requires`/`ensures`/`loop invariant` | — (base primitives) | one function |
| **`act` (`act.md`)** | `act`/`given`/`complete`/`disjoint` | function `requires`/`ensures` (`==>`,`\old`) | one function |
| **MetAcsl (future)** | one HILARE (`\writing`/`\reading`, `\written`/`\read`, weak/strong invariant) | a `#@ assert`/`check` injected at every matching site | whole program |

Each layer keeps PyCSL's discipline: a high-level construct lowers to obligations the
verifier already proves; **0 `\trusted`** is preserved at every stage.

## Stages (do in order; each de-risks the next)

### Stage 1 — `act` blocks (`act.md`) — *do first*
Function-local guarded cases. Self-contained, low-risk, ships the DRY/case-analysis value,
and **locks nothing**: the surface is stable; only the *lowering* changes later. It also
establishes and exercises the "surface → desugar → existing primitives" pattern the meta
layer will reuse at larger scope. It is *not* a detour.

### Stage 2 — a real statement-level proof obligation — *the shared foundation*
A genuine `#@ assert` / `#@ check` that emits WhyML `assert { … }` the prover discharges.
**This does not exist today:** PyCSL's Python `assert` statement is emitted as `()` and
skipped (`module6_whyml/statements.py:1199`). This primitive is the hinge between the two
features:

- **`act` needs it to become faithful.** `act.md` lowers `complete`/`disjoint` to
  `ensures \old(…)` *precisely because* there is no real assert — and that workaround carries
  a documented soundness caveat (a normal-return `ensures` is vacuous on `raises` paths, so
  completeness is under-checked for functions that always raise). With Stage 2, `complete`/
  `disjoint` move to a function-entry `assert { A1 || A2 }` — the faithful semantics — and the
  caveat disappears.
- **MetAcsl cannot avoid it.** A HILARE expands into a per-*site* obligation (an assertion at
  every write/read), which is exactly a statement-level `assert`. The `ensures \old`
  workaround is function-contract-scoped and cannot express it.

So build Stage 2 once, with **`act`'s `complete`/`disjoint` as its first customer** — a small,
well-understood case that validates the primitive (and removes `act`'s caveat) before MetAcsl
leans on it.

### Stage 3 — MetAcsl-style meta-property layer
A whole-program pass that takes one high-level cross-cutting requirement and **expands** it
into Stage-2 assertions injected at every matching program point, then lets Module6/Why3
discharge them. In a *modular* verifier like PyCSL (each function proved in isolation against
callee contracts), a whole-program property is enforced exactly this way: by materialising it
as a per-function/per-site obligation everywhere it must hold. See the `acsl` skill's
`references/metacsl-reference.md` for the HILARE model (target/context/property; the
`\writing`/`\reading` contexts; `\written`/`\read` meta-variables; the transformation
semantics) — adopt the *model*, drop the plugin/CLI surface.

## Why this order, not another

- **Not "MetAcsl-first / redesign `act` for it":** over-engineering. The architectures are
  already compatible (both desugar), `act`'s surface is stable, and designing the meta layer
  before any concrete HILARE use case is building blind. YAGNI.
- **Not "ship `act` and forget the future":** that would make `act`'s normal-return caveat
  permanent and rediscover the assert-primitive need later. Naming Stage 2 now reframes the
  caveat as *temporary — fixed by the primitive we need for Stage 3 anyway*.
- **`act` genuinely locks nothing:** users' `act`/`given`/`complete`/`disjoint` code is
  unaffected when Stage 2 swaps the internal lowering. Migration is invisible at the surface.

## Open decision points (defer until their stage)

- **Stage 2:** surface of the statement obligation (`#@ assert` vs `#@ check` — prove-and-assume
  vs prove-and-discard, mirroring ACSL); how the entry-assert for `complete`/`disjoint`
  interacts with the function's preconditions-as-hypotheses; whether to also discharge on
  abrupt-exit paths.
- **Stage 3:** which cross-cutting properties to target first (integrity vs confidentiality);
  how a "site" is identified in PyCSL's IR (writes/reads to which constructs); how the
  expansion interacts with the memory model (`hoare` vs typed/store).

## Invariants to hold across all stages

0-`\trusted`; desugar/expand to existing primitives; determinism (ordered emission — no
hash-seed flakiness); each new directive passes `bin/doc-coherency.py --check` across the five
normative surfaces; reference-corpus demos (incl. a negative case that must *fail*) for every
feature.
