# Plan: mixin-ready — making `mixin.md` code-ready

Standalone companion to `mixin.md`. `mixin.md` is **design-ready** (Gate-A flagship, tiering, the
D1–D4 design decisions, staged S0–S4, gates, critical files) but **not code-ready**: four gaps and one
substantive risk block "start coding now." This plan resolves each so S0 can begin immediately. It
does **not** restate mixin.md's design — read both together; mixin.md owns the *what*, this owns the
*can-we-start*.

The five things this resolves (from the readiness analysis):
- **R0 — pre-flight** (the Gate-A driver is unwritten; the directives don't parse).
- **R1 — the Tier-1 refinement check is under-specified** (and is reusable, not new theory).
- **R2 — the getattr-dispatch risk** (the real facade dispatches dynamically; `provides`/`depends`
  model static resolution).
- **R3 — no effort sizing.**
- **R4 — the self-hosting demand is asserted, not established** (risk of speculative building).

---

## R0 — Pre-flight: write the Gate-A driver FIRST + a reality probe (do before any source change)

The discipline's literal step 0, currently undone (confirmed: no corpus file uses `#@ mixin`; the
directives don't parse; Module1/Module2 have no recognition). This is the first *and* cheapest action,
and it doubles as syntax validation.

1. **Write the flagship `# pycsl-expected: FAIL` driver** (mixin.md's Gate-A file) into
   `test-suite/corpus/pycsl-reference/` (next free number — currently **0550**; docstring +
   `_ = 0 # anchor`). Confirm it fails *for the right reason* — a **parse/weave error on `#@ mixin`**,
   not an unrelated failure. (Today the probe errors at the first `#@ provides`, which is correct: the
   directives are unrecognised.)
2. **Write the three negative drivers** (missing provider, undeclared-field write, silent method
   collision), each committed `# pycsl-expected: FAIL` and *staying* failing.
3. **getattr reality probe (cheap, ~½ day):** hand-trace one real handler path in
   `Module6_WhyMLTranspiler` — e.g. `_EXPR_DISPATCH["MapGet"] → _handle_map_get_expr` via
   `getattr(self, _EXPR_DISPATCH[t])`. Confirm concretely that the call is **dict-keyed dynamic
   dispatch**, not a static `self._handle_map_get_expr(...)`. This grounds R2's decision in the actual
   code, not the model.

**Exit:** four committed FAIL drivers + a one-paragraph probe note in this file's R2 section. No source
behaviour changed yet.

---

## R1 — Pin the Tier-1 refinement check (and REUSE the existing one)

mixin.md S2 says "check each provider refines each dependency" but shelves the *general* refinement
(contravariant args / covariant results) to Tier 3 — leaving Tier 1's check undefined. **Resolution:
Tier 1 is conflict-free and single-provider, so it needs only EXACT-signature refinement, which PyCSL
already emits.**

- **Signature:** the provider's WhyML signature must **equal** the declared `depends_method` /
  `requires_method` signature (same arity and parameter/return types). No variance — exact match.
  Variance is Tier 3; do not build it.
- **Contract:** the standard one-directional refinement VC of the provider's contract against the
  dependency's. For dependency `requires R_d ensures E_d` and provider `requires R_p ensures E_p`:
  - `R_d → R_p`  (the provider accepts at least what the dependency promises), and
  - `R_d ∧ E_p → E_d`  (the provider delivers at least what the dependency requires).
- **Reuse — no new theory:** this is exactly the **Layer D Liskov refinement** PyCSL already emits.
  `functions.py::_emit_subtyping_goals` / `_render_refinement_goal` (line ~342/364) generate precisely
  this goal per overriding method. Tier-1 composition emits the *dependency* as an abstract `val`
  (`requires R_d ensures E_d`, via `abstract_ops.py`), verifies the mixin once against it, and on
  `compose_from` emits `_render_refinement_goal(provider, dependency)` — the provider-as-override
  against the dependency-as-base. **The refinement machinery is done; S2 only wires it.**

**Exit:** S2's refinement step is "call `_render_refinement_goal` with provider↦sub, dependency↦base,"
with exact-signature pre-check. Documented, no new prover support.

---

## R2 — The getattr-dispatch gap: SCOPE IT OUT of Tier 1 (the principled cut)

The substantive risk: PyCSL's facade dispatches via `getattr(self, _EXPR_DISPATCH[t])` /
`_STMT_HANDLERS.get(s)` — **dynamic, dict-keyed** — but `#@ provides`/`#@ depends_method` model
**static** resolution. Three options were on the table: (a) model the dispatch tables, (b) refactor
the facade to static calls, (c) scope the dispatch layer out of Tier 1.

**Decision: (c).** The getattr dispatch is **orthogonal** to mixin composition, so cutting it is
principled, not a dodge:
- **What the mixin discipline checks:** that providers/dependencies/shared-state **compose soundly** —
  each handler mixin is correct against its declared interface, every dependency has exactly one
  provider, the provider refines it, shared-state writes are in `assigns`, init-hooks fire. This is a
  *static algebra over the mixins*.
- **What the dispatch table is:** a *lookup* (`IR-type → handler-name`) whose only correctness property
  is **coverage** — "every IR type that can occur has a registered handler." That is an
  **exhaustiveness** obligation (the same shape as the "all WP arms covered" property), **not** a
  composition property. It is sound to discharge it separately (or leave it as a documented runtime
  invariant) without weakening the mixin check.
- **So Tier 1 verifies the mixin algebra over statically-named providers; the `getattr` tables stay
  out of scope, documented as a complementary coverage obligation.** No `\trusted` is added to the
  mixin methods themselves; the dispatch *table* is the boundary.
- **Tier 1.5 (gated follow-on, only on a driver that needs it):** recognise the `getattr(self,
  TABLE[t])` pattern and lower it to a `depends_method` on the table's value set, plus a coverage
  assertion that `TABLE`'s keys exhaust the IR-type domain. This is the *only* path that verifies the
  dispatch routes correctly — build it only when a self-hosting driver demands it.

**Consequence for self-hosting:** Tier 1 makes PyCSL's facade *compositionally* checkable (the mixins
and their wiring), which is mixin.md's stated goal; it does **not** by itself verify the dynamic
dispatch. That honest boundary must be stated in mixin.md's out-of-scope list (it currently is not).

**Probe note (R0 step 3, confirmed 2026-06-06).** The facade dispatch is **dict-keyed dynamic**, as
modelled. Both hot paths resolve a method *name string* out of a dict and invoke it via `getattr`:
`module6_whyml/expressions.py:1877-1879` — `handler = self._EXPR_DISPATCH.get(t); … getattr(self,
handler)(expr, …)` (so `MapGet` → the *string* `"_handle_map_get_expr"` → `getattr`), and
`module6_whyml/statements.py:716-718` — `handler = self._STMT_HANDLERS.get(s_type); … getattr(self,
handler)(stmt, …)`. Neither is a static `self._handle_map_get_expr(...)` call. This confirms decision
(c): the dispatch tables are a *coverage* obligation (IR-type domain exhausted by `TABLE` keys),
orthogonal to the mixin composition algebra — correctly scoped **out** of Tier 1.

---

## R3 — Effort sizing (Tier 1)

Rough, to set expectations — Tier 1 only; Tier 2/3 gated.

| Stage | Scope | Size |
|---|---|---|
| **R0 pre-flight** | 4 FAIL drivers + getattr probe | ~1 day |
| **S0 surface+parse** | Module1 prefixes, Module2 grammar+AST, Module3 weave for the 6 Tier-1 directives | ~3–5 days |
| **S1 verify-once** | emit `depends/requires_method` as abstract `val`s; verify each provided method | ~3–5 days |
| **S2 composition check** (the heart) | Module4 pass: unique-provider, refinement (reuse R1), shared/owned field split (D1), init-hook (D4) | ~1–2 weeks |
| **S3 flatten+emit** | compose methods+fields+invariants into the record model; byte-identical non-mixin corpus | ~3–5 days |
| **S4 RT reuse + docs** | wire `#@ deterministic/pure` to RT inference (D3); 5-surface doc-coherency | ~2–3 days |

**Tier-1 total: ~4–5 weeks.** S2 dominates and carries the most risk (the new Module4 pass); everything
else is plumbing or reuse.

---

## R4 — The self-hosting demand: the flagship IS the demand-driver (self-hosting is the motivation)

mixin.md justifies the work by "when PyCSL annotates its own source." If self-hosting is not an
in-flight commitment, building the machinery *for* it would be speculative — the §8 anti-pattern.
**Resolution:** the demand-driver discipline is satisfied **without** requiring self-hosting to be
in-flight, because the **flagship + negative drivers are genuine Gate-A drivers** — they fail today
(directives don't parse) and pass when Tier 1 lands. So:

- **The demand is the corpus drivers** (real, committed, FAIL-first), making this a *legitimate gated
  feature* on its own terms.
- **Self-hosting is the motivating use case and eventual beneficiary, not a prerequisite.** When the
  self-hosting milestone starts, it inherits a checked mixin algebra; until then, the feature stands on
  its drivers.
- **Honest caveat (links R2):** the flagship is a *faithful-but-idealised* miniature — it uses static
  `provides`/`depends`, not getattr dispatch. So passing it proves the mixin algebra works, **not**
  that PyCSL's real facade is fully self-verifying (that needs Tier 1.5). State this in the flagship's
  docstring so the driver doesn't over-claim.

This keeps the work demand-driven and non-speculative while being honest that full self-hosting is a
larger, later thing.

---

## Updated, code-ready stage plan (supersedes mixin.md's "Stages" for execution)

Each stage: entry = prior stage's exit + its driver committed; exit = driver flips/holds + full sweep
clean + byte-diff on non-mixin corpus.

0. **R0 pre-flight** — 4 FAIL drivers (flagship + 3 negatives) committed; getattr probe noted. *First
   file: none (drivers only).*
1. **S0 surface+parse** — the 6 Tier-1 directives parse (flagship reaches `--no-proof` without a parse
   error). *First file: `Module1_Ingestor.py` `_MODULE_PREFIXES` + `Module2_Parser.py` grammar.*
2. **S1 verify-once** — a mixin's provided method proves against an abstract dependency `val`. *First
   file: `module6_whyml/abstract_ops.py` (interface `val`s) + `functions.py` (verify-once emission).*
3. **S2 composition check** — Module4 pass: unique-provider; refinement via `_render_refinement_goal`
   (R1); D1 field split; D4 init-hook. Flagship flips to PASS; negatives stay FAIL. *First file:
   `Module4_SemanticAnalyzer.py` (new pass, after MRO).*
4. **S3 flatten+emit** — composed `Facade` proves end-to-end; non-mixin corpus byte-identical. *First
   file: `preamble.py`/`functions.py` (composed record + methods).*
5. **S4 RT + docs** — `#@ deterministic/pure` → RT inference (D3); 5-surface doc-coherency including
   the **R2 boundary** (getattr dispatch out of scope) added to the static-semantics out-of-scope list.

**YAGNI exit** (unchanged): stop at any stage the flagship doesn't need; Tier 2 (conflicts) / Tier 3
(diamonds, variance) and Tier 1.5 (getattr) start only on a real driver.

---

## What is now decided vs still open

**Decided (was open):**
- Tier-1 refinement = exact-signature + the Liskov VC, **reusing `_render_refinement_goal`** (R1).
- getattr dispatch is **out of Tier-1 scope** (a separate coverage obligation), Tier 1.5 gated (R2).
- Effort ≈ 4–5 weeks, S2-dominated (R3).
- Demand = the flagship/negative drivers; self-hosting = motivation, not prerequisite (R4).

**Still open (resolve during S2, not blocking start):**
- Exact representation of `shared_state` in the composed record's `assigns`/invariant conjunction
  (D1) — concrete during S2 against the flagship.
- Whether init-hook checking (D4) needs Module4 flow or a syntactic check — decide when writing the
  S2 pass; start syntactic.

## Critical files (delta from mixin.md)
- **Add:** `functions.py::_emit_subtyping_goals` / `_render_refinement_goal` — **reused** for the
  Tier-1 refinement VC (R1), not reimplemented.
- **Boundary to document:** `Module6_WhyMLTranspiler.py::_EXPR_DISPATCH` / `statements.py::_STMT_HANDLERS`
  — the getattr layer Tier 1 scopes out (R2); Tier 1.5 target.
- Otherwise as mixin.md (Module1/2/3 surface, Module4 composition pass, abstract_ops, class-record,
  `module5/memoization_rt.py` for D3).

## Net
With R0–R4 resolved, mixin.md is **code-ready**: the first action is R0 (write the FAIL drivers — also
the cheapest), then S0. The two things that turned "design-ready" into "code-ready" were (1) realising
the Tier-1 refinement check is **already implemented** (`_render_refinement_goal`), and (2) cutting the
**getattr dispatch** out of Tier-1 as a separate coverage concern — which removes the only risk that
could have invalidated the whole approach.
