# a2-a3-plan.md — Model the emitter's string ops (A2) and transpiler state (A3)

> **Purpose.** The two remaining **Ceiling-A** modeling gaps from
> `semantic-ceiling-plan.md §2` — **A2** (the emitter's own string operations) and
> **A3** (the transpiler's mutable state) — that, together with the now-complete
> `phase-b-expr-plan.md`, are the prerequisites for making the compositional
> `_handle_*` emitter methods **body-faithful** (semantic-ceiling WI-C1/C4).
>
> **Where this sits.** `phase-b-expr` cleared the A1 piece of Ceiling A (the
> reflective `Dict[str, Any]` dispatch — the emitter now consumes typed `ExprIR`).
> What still blocks un-`\trusted`-ing an emitter method's body is: (A2) it *builds
> and inspects strings* with operations PyCSL can't yet reason about, and (A3) it
> *mutates transpiler state* with no record model, so its `assigns` frame can't be
> stated soundly. This plan closes both. It does **not** touch **Ceiling B**
> (the metacircular string→semantics adequacy), which stays the audited evaluator
> axioms (D2) — see §7.
>
> **Convention.** Named repo-root plan file. Byte-identical gate after every step
> (`bin/byte-diff-sweep.sh`). Reference-corpus additions. Leaf-first: model the
> smallest verifiable surface a real method needs before scaling.

---

## 0. Grounding (measured, current `main`)

**A2 — string operations the emitter bodies actually use** (counts across
`module6_whyml/`, on the WhyML strings it builds and the IR string fields it
inspects):

| op | uses | op | uses | op | uses |
|---|---:|---|---:|---|---:|
| `.join` | 89 | `.replace` | 33 | `.rsplit` | 15 |
| `.startswith` | 87 | `.lower` | 25 | `.lstrip` | 13 |
| `.strip` | 41 | `.endswith` | 20 | `.decode` | 9 |
| `.split` | 35 | | | `.rstrip`/`.encode` | 6/6 |

Partial models already exist (emitted for *user* string code, reusable):
`str_length_op` (12), `str_sub_op` (12), `str_concat_op` (8), `str_eq_op` (7),
`str_hash_op` (6), `str_startswith_op` (2), `str_endswith_op` (2),
`str_find_op` (2), `str_contains_op` (3), `String.length`/`String.substring`
(76/17), plus `stable_hash` (10, a Python-level gensym).

**A3 — transpiler state the emitter reads/mutates** (of 246 distinct `self._*`):
the dominant mutator is `self._add_abstract_op(...)` (**97** calls, appends to
`self._abstract_ops`); other mutated fields include `_dict_locals`,
`_array_locals`, `_seq_locals`, `_record_locals` (sets, `.add`),
`_havoc_counter` (int, `+= 1`), `_in_spec` (bool flag, set/reset). Read-only
config: `_value_semantic`, `_current_self_type`, `_record_types`, `_heap_var`,
`_formal_params`, `_current_params`, `_array_locals` (membership), etc.

---

## 1. Objective & success criterion

**Objective.** Give PyCSL (a) a faithful-or-audited model for every string
operation the leaf/compositional emitter methods use (A2), and (b) a
transpiler-state record so those methods' `assigns` frames are soundly stateable
and provable (A3) — such that a `_handle_*` method, once un-`\trusted`, verifies
against its body-faithful `ensures \result == <the WhyML string>` + `assigns
<touched state>`.

**Done =** for the leaf + simple-compositional handlers (`assign`, `return`,
`pass`/`break`/`continue`, `if`, `seq`, and their `_expr_to_whyml` leaf
dependencies), the body verifies body-faithful with:
- every string op in the body modeled (faithfully, or as an enumerated trusted
  primitive with an audited length/shape spec);
- a sound `assigns` clause over the transpiler-state record;
- **byte-diff 0** (A2/A3 are modeling + framing, not emission changes);
- the residual trust limited to the enumerated string primitives (§A2) + the
  audited evaluator axioms (Ceiling B / D2), nothing opaque.

---

## 2. A2 — string operations model

### 2.1 The two faithfulness tiers (be honest about which op gets which)
Not every Python string op is first-order expressible over Why3 `string.String`.
Split them:

- **Tier F — faithful** (`string.String` theory has it, or it's a clean recursion):
  `length`, `substring`/slice, concatenation (`^`/`concat`), equality,
  `startswith`/`endswith` (prefix/suffix predicates), `lt`/`le` (lexicographic).
  Most already exist (§0) — this tier is *completion + audit*, not invention.
- **Tier T — trusted primitive with an audited length/shape spec** (content not
  first-order expressible): `replace`, `split`/`rsplit`, `strip`/`lstrip`/`rstrip`,
  `lower`/`upper`, `join`, `format`/`%`, `decode`/`encode`. Model each as an
  abstract `val` whose `ensures` pins only what is *sound and useful* (e.g.
  `join`: result length ≥ Σ parts; `strip`: length ≤ input; `replace`/`split`:
  an opaque result with a documented boundary), never a false content claim.
  This mirrors the existing `str_mod_op` pattern (`length ≥ 0` only).

### 2.2 `stable_hash` (gensym)
Used to mint fresh names. Model as an **injective `int → string`** (audited
`∀ i≠j. h i ≠ h j`) or replace the call with `self._havoc_counter` (already an
int counter). Freshness is the only property the emitter relies on.

### 2.3 A2 work items
| WI | Item | Gate |
|---|---|---|
| **A2.1** | Enumerate every string op in the target leaf/simple handlers + its callee `_expr_to_whyml` leaves; tag each Tier F / Tier T | list reviewed; nothing untagged |
| **A2.2** | Complete Tier-F models (`startswith`/`endswith` predicates, prefix/suffix) and *audit* the existing `str_*_op` set (each has a sound `ensures`) | each op has an audited spec; byte-diff 0 |
| **A2.3** | Add Tier-T primitives (`replace`/`split`/`rsplit`/`strip*`/`lower`/`upper`/`join`) with length/shape `ensures` only; document each boundary in `evaluator-axiom-audit.md` | primitives enumerated; boundaries documented |
| **A2.4** | `stable_hash` → injective primitive (or counter); prove the freshness fact the emitter needs | freshness lemma; byte-diff 0 |
| **A2.5** | A **PyCSL-level probe** per op: a standalone `#@`-annotated function using that op proves its intended contract (the `leaf-emitter-witnesses.py` pattern) | each probe SUCCESS; a false-postcondition probe FAILS (non-vacuity) |

---

## 3. A3 — transpiler-state record model

### 3.1 The model
Introduce a **transpiler-state record** capturing the mutable fields the emitter
touches — not all 246 `self._*`, but the ~8 genuinely mutated ones:
`_abstract_ops` (via `_add_abstract_op`), `_dict_locals`, `_array_locals`,
`_seq_locals`, `_record_locals`, `_havoc_counter`, `_in_spec`, `declared_refs`.
Model each at its faithful WhyML type (set of strings, int, bool). This lets a
method state `#@ assigns self._abstract_ops, self._havoc_counter, …` soundly and
prove it — the `assigns`-framing half of Ceiling A.

### 3.2 Leaf-first framing
- **Contract the state mutators first** (the leaves): `_add_abstract_op` gets
  `#@ assigns self._abstract_ops` + a set-membership `ensures`; the `.add`/`+= 1`
  mutations similarly. A composite `_handle_*` that calls them then composes the
  frames.
- A method that mutates **nothing** (e.g. `_handle_pass`/`_handle_continue`) gets
  `#@ assigns \nothing` — already provable, the first witnesses.

### 3.3 A3 work items
| WI | Item | Gate |
|---|---|---|
| **A3.1** | Enumerate the mutated state fields per target handler (leaf-first); classify pure (`assigns \nothing`) vs. state-touching | per-method assigns-set determined |
| **A3.2** | Transpiler-state record: faithful WhyML types for the ~8 mutated fields; `#@ ghost`/record model in the self-annotate mirror | record type-checks |
| **A3.3** | Contract the state mutators (`_add_abstract_op`, `.add`, `havoc_counter`, `_in_spec` set/reset) with sound `assigns` + `ensures` | mutator contracts prove |
| **A3.4** | Frame the pure handlers (`pass`/`break`/`continue`) `assigns \nothing`, then the simple state-touching ones | frames prove; byte-diff 0 |

---

## 4. The payoff — connect to a body-faithful handler (the whole point)

With A2 (string ops modeled) + A3 (assigns frameable) + `phase-b-expr` (typed
fields), the pipeline of `semantic-ceiling-plan.md §3` closes for a target arm:

```
_handle_X body ─(A1 done: typed fields; A2: string ops; A3: assigns frame)─►
        ensures \result == handle_X_code(...)   +   assigns <state>
                         │
                         ▼  (already proved in pycsl-wp-spec.mlw)
           X_code_state_coherent : eval_whyml_stmts(handle_X_code …) = wp_X …
                         │
                         ▼  residual trust
         audited evaluator axiom X_semantics (Ceiling B / D2, enumerated)
```

So the emitter method stops being `\trusted`; its correctness reduces to a proved
string-shape contract + a proved assigns frame + the proved coherence lemma +
one audited evaluator axiom per construct. **No new opaque trust** — the
`\trusted` body is *replaced* by (a) enumerated string primitives and (b) the
pre-existing D2 axioms.

---

## 5. Sequencing (thinnest vertical slice first)

```
Slice 0 (prove the route on the SIMPLEST arm — `_handle_pass`/`continue`):
   A3.4 (assigns \nothing) + A2 (none needed) + un-\trust + connect to coherence.
   ⇒ one arm body-faithful, residual = 1 audited axiom. Falsifiable PoC.
Slice 1 (assign leaf): A2.1–A2.2 for its string ops (ident/concat) + A3.3 for
   its state mutation (declared_refs) → `_handle_assign_stmt` body-faithful.
Slice 2 (leaves ↑): the `_expr_to_whyml` leaf shapes assign depends on.
Slice 3 (simple compositional): if/seq/while/for.
Slice 4 (Tier-T ops as needed): add `replace`/`split`/`strip`/… only when a
   target handler needs them (avoid speculative modeling).
Slice 5: corpus + non-vacuity gates (A2.5); docs.
```

**Rationale.** Slice 0 is the cheap proof-or-falsification that A3's assigns-frame
route works end-to-end on the trivial arm (no strings). Slice 1 is the first arm
needing A2. If Slice 0/1 don't close, that localizes the wall early (and the
fallback is unchanged: stratified trust + the coherence route already cover LINK 3).

---

## 6. Gate criteria

1. **Byte-identical** across the 627-file sweep after every step — A2/A3 are
   modeling + framing, never emission changes.
2. **Self-annotate proves** the target method body-faithful and it is **no longer
   `\trusted`** (`bin/self-annotate-mirror-check.sh`).
3. **No new opaque trust.** The residual is only the enumerated Tier-T string
   primitives (each with an audited `ensures`, listed in
   `evaluator-axiom-audit.md`) + the pre-existing D2 evaluator axioms. `Print
   Assumptions`-style audit for the mlw side.
4. **Non-vacuity.** For each converted method and each new string primitive, a
   deliberately-false `ensures` FAILS.
5. **Reference corpus.** A `pycsl-reference` case per newly-modeled string op stays
   Valid; the leaf-emitter witnesses extended.

---

## 7. Non-goals / honest boundaries

- **Ceiling B is NOT addressed.** A2/A3 clear the *remaining Ceiling-A* pieces
  (string reasoning + assigns framing) so the body can be **type-checked and
  framed**; the string-shape contract's *adequacy* (that the emitted WhyML, when
  evaluated, performs the WP transformation) still rests on the audited evaluator
  axioms — irreducible by Gödel/Löb (`facing-the-facts.md §5`, `semantic-ceiling.md`).
- **Content semantics of `replace`/`split`/`format`** are NOT modeled — Tier T
  gives sound length/shape specs only. A body that *depends on the content* of a
  `replace` result (rather than its shape) is out of scope; if a target handler
  needs it, that handler stays `\trusted` with a named note (not a silent hole).
- **The full 246-field transpiler state** is NOT modeled — only the ~8 fields the
  *target* handlers mutate (leaf-first). Handlers touching un-modeled state stay
  `\trusted`, enumerated.
- **The contract/spec subsystem** (`contract_expr`, still dict-typed — see
  `phase-b-expr-plan.md §17`) is out of scope; A2/A3 target the runtime-`_handle_*`
  emitter path, not spec emission.

---

## 8. Effort & risk

| Piece | Effort | Risk | Note |
|---|---|---|---|
| A2 Tier-F completion/audit | Low–Med | Low | mostly exists; audit + fill gaps |
| A2 Tier-T primitives | Med | Low (sound length/shape) | many ops, but each a small audited `val` |
| A2 `stable_hash` | Low | Low | injective/counter |
| A3 state record + mutator contracts | Med–High | Med | the `assigns`-framing is the novel part |
| Slice-0/1 end-to-end connect | Med | Med | the falsifiable PoC; localizes any wall |

**Overall.** This is the *direct route* to body-faithful emitter contracts. It is
bounded and gated, but its payoff is **incremental over the already-standing LINK 3**
(the Why3-side coherence lemmas + the 26/26 byte-diff already discharge the
emitter's obligation with the D2 residual). The honest value of A2/A3 is *reducing
the `\trusted` surface of the real emitter*, one arm at a time — not a new
soundness result. Recommend executing **Slice 0 first** as the cheap
proof-or-falsification before committing to the full A2/A3 build-out.

---

## 9. Smallest first experiment (Slice 0, concretely)

Target: **`_handle_pass`/`_handle_continue`** (extracted leaf, no strings, no
state) — or `_handle_assign_stmt`'s **`assigns \nothing`-adjacent** path.
1. A3.4: annotate `#@ assigns \nothing` + the body-faithful `ensures \result ==
   indent ^ "raise PyCSL_Continue"` (already proven viable — `leaf-emitter-witnesses.py`).
2. Un-`\trust` it in the self-annotate mirror; `self-annotate-mirror-check.sh`.
3. Connect its `ensures` to the `continue`/`skip` coherence obligation.
4. `Print Assumptions`-style audit: residual = one evaluator axiom, nothing opaque.
5. Byte-diff 0; a false `ensures` FAILS.

If 1–5 close, the assigns-frame + string-witness route is validated end-to-end and
Slices 1–5 are its systematic extension. If a step resists (e.g. the self-annotate
`ir_schema` import opacity of `b14.md` B1 re-bites for a non-trivial method), that
is the precise, early signal — and the fallback (stratified trust, coherence route)
is unchanged and already in place.

---

## 10. EXECUTION RESULTS (2026-07-01) — the falsifiable probes ran; the ceiling is confirmed, precisely

Executed the plan's §9-recommended falsifiable probes first (empirical A2 tier map
+ the mirror/Slice-0 preconditions). Outcome: **A2 is not a primitive-addition —
it is a string-theory + contract-grammar extension, and A3/Slice-0 re-hit the
b14 B1 self-annotate opacity.** The route is confirmed blocked, with fresh,
precise evidence. New durable artifact: `src/self-annotate/string-op-tier-map.py`
(the Tier-F ops that prove; the Tier-T gap listed).

### 10.1 A2 — measured tier map (probed as `#@` functions)
| op | in a **body** | in/with a **contract** |
|---|---|---|
| `s + t` (concat) | ✅ (`str_concat`) | ✅ `ensures \result == s + t` |
| `.startswith` / `.endswith` | ✅ (`str_startswith_op`, bool) | ❌ **parse error** — spec grammar can't express `s.startswith(p)` |
| `len(s)` → `\length(s)` | — | ❌ FAILS (str-length not connected to `\length`) |
| `.replace` | emitted | ❌ even `\length(\result) >= 0` FAILS (no length ensures) |
| `.strip` / `.split` / `.rsplit` / `.join` / `.lower` / `.upper` / `.decode` | emitted | ❌ no length/shape model |
| `\length(s + t)` nested in a spec | — | ❌ **parse error** |

**Conclusion:** an emitter body that builds output by **concatenation + f-strings +
bool dispatch** (`startswith`) is already body-faithful-provable (the
`leaf-emitter-witnesses.py` continue/pass/raise confirm this). But any body that
**transforms string content** with `replace`/`split`/`strip`/`join` is **not**
— those need (a) audited length/shape `val` primitives added to the string theory
*and* (b) contract-grammar support to *state* the relations. That is the real A2 —
a bounded but genuine feature, not a quick primitive drop-in.

### 10.2 A3 / Slice-0 — precondition check
- The self-annotate mirror `src/self-annotate/src/module6_whyml/statements.py` still
  carries **31 `\trusted`** methods — the `b14.md` B1 `ir_schema` import-opacity in
  single-file isolation (the emitter's own IR types are opaque in the mirror). So
  un-`\trusting` a real handler (Slice 0) is gated on the same B1 wall the whole
  ir-schema-C / b14 history is stuck on — **not** on A2/A3.
- The *string-shape contract itself* for the trivial leaves already proves in
  isolation (`leaf-emitter-witnesses.py`), so A3's `assigns \nothing` half is sound;
  the block is the mirror's import opacity, not the framing.

### 10.3 Verdict & fallback (per §8/§9)
- **A2 is a real, bounded feature** (string-theory length/shape prims + grammar),
  worth doing on its own merits for *user* string code — but its emitter payoff is
  incremental over the standing LINK 3 (coherence lemmas + 26/26 byte-diff already
  discharge the emitter obligation to the D2 residual).
- **A3/Slice-0 are gated on b14 B1**, not on A2/A3 modeling — so the a2-a3 route to
  a body-faithful *real* emitter method cannot close until B1 (single-file
  cross-module type resolution in self-annotate) is solved. That is a distinct,
  documented blocker (`ir-schema-spec.md §10`, `b14.md`).
- **Fallback taken** (unchanged, already in place): stratified trust — the
  Why3-side per-arm coherence lemmas remain LINK 3's discharge, with the audited
  D2 evaluator axioms as the residual.

**Net:** the falsifiable execution did its job — it *located* the two real walls
(A2 = a string-theory+grammar feature; A3/Slice-0 = the b14 B1 opacity) instead of
grinding into them. No `_handle_*` was un-`\trusted`; no emitter/prover code was
touched. The deliverable of this pass is the precise A2 tier map + the confirmation
that Slice-0 is B1-gated, not A2/A3-gated.
