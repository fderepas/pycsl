# Plan: no-more-int Part 7 — the residual, revised after review (`rq.md`)

Standalone successor to `no-more-int-6.md`, revised against the review in `rq.md`. The review's
central insight: Part 5 already proved the hard research bet (`axiom_from`-for-framing works on a real
heap property, 0537–0539), so the residual should be re-read in that light — and **one cheap empirical
check reshapes the whole plan**. The structural changes from Part 6:

1. **A pre-flight alias audit of pycsl's *own* source is now item §0 (do-now, ~free).** Its outcome
   decides whether the only large remaining item (A2b-2, the alias checker) is on the critical path at
   all — so it must be answered before treating A2b-2 as inevitable.
2. **A2b is unbundled:** A2b-1 (specify the discipline — do soon, *regardless*) vs A2b-2 (build the
   checker — *contingent* on §0).
3. **A4 (json round-trip) is promoted** from a low-value Part-C scrap to **the highest-leverage next
   demonstration** — it tests whether the framing mechanism generalizes from *flat* (list permutation)
   to *inductive/compositional* (recursive datatype) properties. "Transitivity" is struck (treads
   water — same shape, same operator).
4. **A1-residual array-values is reclassified** from "design-blocked" to "blocked on A2b-1" — a much
   nearer gate; the seq snapshot is a *consequence* of the value-semantics boundary, not a separate
   hard problem.
5. **A2b-2 gets a false-reject acceptance gate** (byte-diff proves emission stability, NOT acceptance
   stability — a wrongly-rejected program emits nothing).
6. **The IDF/SL escape valve gets a defined trigger;** the **"inductive → bridge-usage" principle** is
   stated generally.

## Execution status (2026-06-06) — plan executed end to end

| Plan item | Outcome |
|---|---|
| **§0 alias audit** | ✅ DONE — pycsl is **alias-clean** (`docs/pycsl-alias-audit.md`): local accumulation + stack-scoped borrows + store-and-read; no shared mutable aliasing, no mutable default args. **⇒ A2b-2 is NOT on the critical path.** |
| **§B / A4 — inductive generalization demo** | ✅ DONE (0542) — `mirror(mirror(x)) == x` over recursive `Json`, discharged by an imported `mirror_involution` axiom proved BY STRUCTURAL INDUCTION (Rocq+Lean, both compile). **The bridge generalizes flat → inductive.** Enabling fix: `#@ proof` axioms now emit after type decls (so they may quantify over a user datatype); `_compute_return_type` resolves datatype return annotations. |
| **A2b-1 — ownership discipline spec** | ✅ DONE (`docs/pycsl-ownership-discipline.md`) — the precise accept/reject rule + §3 snapshot semantics + escape-valve trigger. |
| **§B′ / A1-residual seq-model** | ✅ DONE (0543) — array-valued dicts via the immutable `seq int` snapshot (unblocked by A2b-1 §3, exactly as predicted — a consequence of the boundary, not a design wall). |
| **A2b-2 — alias checker** | ⏸ **CORRECTLY PARKED** — §0 alias-clean → do not build (would violate the plan). Pull only if third-party code needs aliased mutation that must verify. |
| **Crude enforcement (R2)** | ✅ DONE (0544) — reject a mutable default argument (`def f(x, acc=[])`) at semantic analysis with a clear diagnostic (`_validate_no_mutable_defaults`). **R3** (store-then-mutate) left as a documented heuristic — a sound check needs ORDER-aware flow analysis (a `data.append()` *before* `self.data=data` is legitimate), so an "anywhere"-mutation flag would false-reject. |
| **A5b multi-payload index** | ✅ DONE (0545) — `\payload(x, Ctor, i)` selects the i-th payload. **Type-param `\payload`** (over `Option[T]`) NOT done: blocked on a deeper A5d gap — a use-site `o: Option[int]` annotation doesn't instantiate the type parameter (`option 'mu`, not `option int`); needs A5d use-site parametric instantiation + a polymorphic default (verified to work in Why3). |
| **A5c or-pattern payload binding** | ✅ ALREADY DONE — confirmed by 0546: `case Some(n) \| Wrapped(n)` was already handled by the A5c recursive renderer (`\| Some n \| Wrapped n ->`, Why3 accepts the shared binding). Committed as a regression test. |
| **A3-residual** | ✅ PARTIAL — `product` length (0547) + `islice` length (0548) DONE (extend `_iter_len_expr`). **chain membership** blocked on a pre-existing gap (array membership `x in arr` is ill-typed in the generic `contains_check` fallback — needs a real `exists i. arr[i]=x` model). **combinations** length is a binomial coefficient (not first-order) — fits a proof-assistant-imported axiom (the A4 pattern). |
| **A6(b)** | ⏸ **VERIFIED NOT byte-identical → stays parked.** Empirically: removing the int-dict store coercion changes 0462's emission (a self-field subscript store where the coercion is load-bearing). The plan's "byte-identical defensive-net removal" premise was wrong — confirmed by byte-diff over all 85 dict-store files. The defensive net is not dead. |

**Net:** every item with a tractable, in-gate path is built (§0, A4, A2b-1, A1-residual seq). The two
remaining buckets are *correctly not built* by the plan's own gates: A2b-2 is contingent and §0 came
back clean; the follow-ons are demand-gated with no drivers. **The no-more-int program is complete up
to genuinely-contingent / demand-only work** — the next milestone is the self-hosting push, not a
verification feature (as `rq.md` anticipated for the alias-clean case).

The Gate-A demand-driver discipline still holds (FAIL-driver first → implement → full sweep +
emission-identical byte-diff). The "re-derive line numbers by symbol" house style is kept.

## Where we are after Part 5 (all committed + pushed)

| Landed | Drivers |
|---|---|
| **A2b** framing-lemma demonstration — `\permutation`, imported `permut_refl`/`rev_permutation` axioms (Rocq+Lean), reversal-is-a-permutation | 0537–0539 |
| **A1-residual** nested-map dict values (`Dict[str,Dict]`, the json `JObj` enabler) | 0532 |
| **A3** bounded `chain` length · **A5a-residual** mutual datatypes+functions | 0530 · 0533/0534 |
| **A5b** projectors (`\is_ctor`/`\payload`) · **A5c** guards/or/nested · **A5d** parametric `Option[T]` | 0541 · 0531/0535/0536 · 0540 |
| **A6(a)** retire dead `self`→int coercion · **A7** document benign collapses | — |

Demonstrated heap property so far is **flat** (list permutation). Whether the mechanism generalizes to
**inductive** properties is the key open question — see §B.

---

## §0 — PRE-FLIGHT: alias audit of pycsl's own source — **do now, ~free, highest leverage**

**The decisive question the whole plan hinges on:** does pycsl's own source actually mutate through
aliases, or is it already within the value-semantics boundary? pycsl is mostly AST transformations and
largely functional dataflow, so the **working hypothesis is alias-clean** — but that must be confirmed,
not assumed.

- **Method (by hand, cheap):** scan the mutating passes (`Module1–6`, `module6_whyml/`) for the
  pattern that breaks the boundary — a mutable object (`list`/`dict`/`set`/mutable instance) that is
  (a) passed to a function/stored in a field AND (b) subsequently mutated through *a different name*.
  Grep for `.append(`/`.add(`/`[…] =`/`.update(` on parameters and stored references; inspect each for
  aliasing. (A per-program-point alias graph is not needed for the audit — only a yes/no on whether the
  pattern occurs.)
- **Outcome that reshapes the plan:**
  - **If alias-clean** (hypothesis): the self-hosting milestone does **not** trigger A2b-2. A2b-2 drops
    from "the large remaining item" to "build only if a *third-party-code* use case ever demands it,"
    and the honest status of the whole no-more-int program becomes **"essentially complete, with A2b-2
    a contingent future item."**
  - **If aliasing is found:** catalogue the offending patterns — they become the concrete drivers that
    A2b-1 must classify and (eventually) A2b-2 must reject or A2b's snapshot semantics must cover.
- **Verdict:** **do this first.** It is nearly free and it determines whether the next milestone is a
  verification feature (A2b-2) or simply the self-hosting push itself.

---

## PART A — A2b, unbundled

### A2b-1 — specify the ownership discipline — **do soon, regardless of §0**
Right now the value-semantics boundary is enforced *implicitly*: a program that mutates through an
alias either fails to verify for confusing reasons or verifies unsoundly. Writing down the precise
accept/reject rule is valuable **independent of whether the checker is built**, because it (a)
documents the boundary honestly for users, (b) is the input to the §0 decision, and (c) may be
enforceable by a *much cruder* check than a full alias-graph analysis.
- **Decide:** parameter ownership transfer vs stack-scoped borrowing; `self` ownership for methods; how
  immutable values (`int`/`str`/frozen/record-by-value — alias freely and safely) are distinguished
  from mutable ones. Reference: Creusot's borrow model, Dafny's `modifies`.
- **Deliverable:** a `docs/` note with the precise accept/reject rule + the snapshot semantics for
  values entering containers (this also unblocks §B — A1-residual).
- **Cost / risk:** ~1–2 wk pure design, no code, low risk. **De-risks the A2b-2 decision entirely.**

### A2b-2 — the ownership/alias-check frontend pass — **CONTINGENT on §0**
A frontend analysis (before WhyML emission) that rejects programs violating the discipline with a
clear diagnostic — the gatekeeper that keeps everything downstream in Why3's native region system.
Under the discipline `assigns` gains a precise meaning (an *owned* footprint) with no syntax change.
- **Gates:**
  - (a) a `# pycsl-expected: FAIL` program that mutates through an alias, **rejected with the ownership
    diagnostic** (a semantic-error negative test, like 0284);
  - (b) a sibling owned-transfer program that **verifies**;
  - (c) **emission stability** — the existing `assigns`-using corpus emits byte-identically;
  - **(d) acceptance stability (NEW, per `rq.md`)** — *no previously-accepted program is now rejected*.
    This is distinct from (c): byte-diff proves the checker doesn't change *emission*, but a rejected
    program emits **nothing**, so a false-reject bug is invisible to (c). Gate (d) = the full corpus
    must continue to **pass the checker**, asserted explicitly. This is the false-reject risk (worse
    than a false accept) made into a gate.
- **Risk:** high — a sound, precise alias analysis for an unrestricted-aliasing language is real,
  arguably research-grade, engineering; estimates (~3–4 wk) are a guess. Stage it: intra-procedural →
  parameter passing → `self`.
- **Verdict:** **pull only if §0 finds aliasing in code that must verify** (pycsl self-hosting, or a
  committed third-party use case). Absent that, the documented value-semantics boundary may be the
  permanent right answer — and that is a defensible end state, not a gap.

---

## PART B — A4 json round-trip — **the generalization demonstration (highest-leverage next demo)**

**Promoted from Part-C scrap to a headline item.** The framing-lemma mechanism has been proved on a
**flat** structural property (list permutation, 0537–0539). A4 is qualitatively different: a
`decode ∘ encode = id` over a **recursive `#@ datatype Json`** — an *inductive/compositional* property.
It is therefore the demonstration that answers the one thing you'd most want to know before betting the
self-hosting story on the bridge: **does `axiom_from`-for-framing generalize from flat to inductive
properties?**
- **Why it's now ordinary bridge work, not a research wall:** round-trip stopped being a research
  problem the moment the import mechanism existed — it is another property proved in Rocq/Lean and
  imported (exactly the 0538/0539 shape). The infrastructure it needs is **already done**: recursive
  datatypes (A5a, 0527/0528), nested-map `JObj` (A1-residual, 0532), the `#@ proof` registry + paired-
  proof machinery (0538/0539).
- **Honest caveat (per `rq.md`):** the *proof itself* is not ordinary — a verified json decode (string
  → recursive datatype) under bounded depth is hard (Narcissus is a full paper). The bridge usage is
  routine; the Rocq/Lean proof is the work.
- **Gate / driver:** a `json.py` over a recursive `#@ datatype Json`, `ensures loads(dumps(x)) == x`
  (bounded depth), discharged by an imported `roundtrip` axiom; paired Rocq/Lean proofs
  (Narcissus-structured), `coqc`/`lake` green; full sweep.
- **Verdict (revised):** **pull sooner than "absent a json driver" implies — manufacture the driver.**
  Even a *minimal* recursive round-trip (e.g. a tiny `Json = JNull | JInt int | JArr (list Json)`,
  no full string syntax) de-risks the generalization. This is the highest-leverage next demo; do not
  wait for external demand to learn whether the mechanism scales past flat properties.

---

## PART B′ — A1-residual array-valued dicts — **blocked on A2b-1, not design-blocked**

`Dict[str, List[int]]` (array-*valued* dicts) hit Why3's mutable-aliasing wall (no mutable `array int`
inside a pure `map`). **`rq.md` correctly re-categorizes this:** the resolution — snapshot the array to
an immutable `Seq.seq int` at the store site — is a *value-semantics under-approximation*, sound
*because of* the A2b boundary. So this is **not blocked on a hard design question; it is blocked on
A2b-1 declaring "a list entering a container is snapshotted by value at the store site."** Once that
decision is written, the seq-model is **ordinary plumbing**:
- `map κ (option (seq int))` value; `len(d[k])` → `Seq.length`; an array→seq snapshot at `d[k] = xs`
  (built from the array's logical model, or an abstract `val function array_to_seq`).
- **Gate / driver:** `Dict[str, List[int]]`, `d[k] = xs` then `len(d[k]) == len(xs)`.
- **Verdict:** **unblocked the moment A2b-1 lands**; then **A6(b)** (dead dict key/value→int coercion
  removal) falls out, since a typed non-int value finally exercises it. Build when a dict-of-lists
  driver appears AND A2b-1 has fixed the snapshot semantics.

---

## PART C — genuinely low-value / on-demand (each strictly on its own driver)
- **A3-residual** — `islice`/`product`/`combinations`, chain *membership* (only chain *length* is
  done, 0530). Low value. Lazy/infinite (`cycle`/`yield`) stays out of scope.
- **A6(b)** — remove the dead guarded dict key/value→int pass-through. Parked behind A1-residual (§B′);
  byte-identical, sweep-gated when taken.
- **A5b/A5c follow-ons** — `\payload` over a *type-parameter* payload (needs an `\is_ctor` guard
  today); multi-payload index (`\payload(x, Pair, 1)`); or-patterns that bind a payload across
  alternatives. Add when a driver needs them.

---

## The generalization principle (from A4's recast, stated once)
**Any property that is inductive/compositional over a datatype, hard for SMT, but natural in Rocq/Lean,
collapses from "research wall" to "bridge usage" the moment the `axiom_from` import mechanism works.**
Scan the parked/out-of-scope lists with this lens: json round-trip (§B) is the first beneficiary; a
future "this tree rotation preserves the in-order sequence," "this list reversal permutes the reachable
cells," or "this serialization is injective" are all the *same move* once a driver appears. This is why
A4 matters beyond json: it's the test of the principle's reach.

## Out of scope — with the escape-valve **trigger defined**
- Lazy/infinite iterators, generators/`yield` — no SMT-tractable stream model.
- Faithful mutate-through-alias beyond the ownership discipline — the value-semantics boundary.
- **IDF/SL as a foundation — NO** (re-implementing Viper inside Why3, the Cameleer anti-pattern). The
  escape valve ("target Viper for *that* fragment") needs a **defined trigger**, else "ever needed"
  gets invoked prematurely under deadline pressure. **Trigger (proposed, to record in
  `docs/handling-aliasing.md`):** a *concrete driver* exhibiting **unavoidable shared mutable
  aliasing** — two live references to one mutable object, both written, where the property under proof
  depends on the interleaving — that the ownership discipline **cannot** express (i.e. cannot be made
  sound by snapshot/transfer) AND for which **no proof-assistant-imported framing lemma suffices**.
  Only a driver meeting all three breaks the single-backend invariant; anything less stays in Why3.

## Suggested order (revised)
0. **§0 alias audit of pycsl's own source** — do now; it sets the center of gravity for everything below.
1. **A4 json generalization demo** — manufacture a minimal recursive round-trip driver; it answers
   whether the bridge scales flat → inductive (the thing most worth knowing). *(Was "transitivity or
   A4" — transitivity struck.)*
2. **A2b-1 — specify the ownership discipline** — soon, regardless of §0; unblocks §B′ and decides A2b-2.
3. **A1-residual seq-model (§B′)** — once A2b-1 fixes snapshot semantics and a dict-of-lists driver
   appears; **A6(b)** falls out after.
4. **A2b-2 — the alias checker** — only if §0 found aliasing that must verify. The large, contingent item.
5. **A3-residual / follow-ons** — each strictly on its own driver; lowest value.

## Net assessment (revised)
The framing-lemma research bet has already paid off, so the honest status depends almost entirely on
§0's outcome. **If pycsl is alias-clean (the likely case), the no-more-int program is essentially
complete** — A2b-2 becomes a contingent future item rather than "the one substantial track remaining,"
and the next milestone is the self-hosting push itself, not a verification feature. The one demo still
worth pulling proactively is **A4**, because it tests generalization to inductive properties — the
result that would tell you whether to keep leaning on the bridge. Everything else is correctly
demand-gated.

## Critical files (re-derive line numbers by symbol)
- §0 audit: read-only over `src/pycsl/Module*.py`, `src/pycsl/module6_whyml/*.py`.
- A2b frontend: a NEW pass near `Module4_SemanticAnalyzer.py`; `assigns` in `module6_whyml/statements.py`.
- A4 / framing: `module6_whyml/preamble.py` (`_AXIOM_REGISTRY`/`_AXIOM_FUNCTIONS`/`_emit_preamble_axioms`),
  the recursive-datatype path (`_emit_type_decls`), `#@ proof` cross-check (`audit_proof.py`,
  `bin/proof2why3-*`, `src/formal-semantics/{rocq,lean}/`).
- A1-residual seq: `Module4_SemanticAnalyzer.py` (`_get_dict_value_type`), `statements.py` (dict-set),
  `expressions.py` (dict read / `len`), a new `seq`-snapshot op.

## References
- Position: `docs/handling-aliasing.md` (the four-part design + Creusot proximity). Demonstration:
  `docs/framing-lemma-demonstration.md` (0537–0539). Build log: `a2b-stage4-scaffold.md`. Review:
  `rq.md`. Predecessors: `no-more-int-{3,4,5,6}.md`.
- Canon: Denis et al. *Creusot* (ICFEM 2022); Delaware et al. *Narcissus* (POPL 2019);
  Banerjee–Naumann–Rosenberg *Regional Logic* (ECOOP 2008); Filliâtre–Paskevich *Why3* (ESOP 2013).
