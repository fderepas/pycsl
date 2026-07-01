# a3-plan.md — Model the transpiler state so emitter handlers can state & prove `assigns`

> **Purpose.** Give the emitter's mutable transpiler state a WhyML **record model**
> so a state-mutating `_handle_*` method can state a sound `#@ assigns self._…`
> frame and have it proven. This is the **A3** half of what
> `no-more-int-emitter-plan.md §7` identified as the two remaining walls to scaling
> L5 (the first un-`\trusted` handler, `_handle_ghost_array_set_stmt`): the other
> handlers all **mutate transpiler state** (so cannot be `assigns \nothing`) **and**
> reflect on IR dicts. A3 removes the *mutation-frame* wall; the `.to_dict()`/dict-
> reflection wall is a separate plan.
>
> **Where it sits.** `ghost_array_set` closed because it was the unique
> zero-mutation leaf. Every other real handler in `statements.py` mutates state
> (`_add_abstract_op`, `_dict_locals.add`, `_havoc_counter += 1`, …) — the mirror's
> **B4** blocker: "there is no transpiler-state record model, so the frame
> (`assigns`) cannot be stated soundly." A3 builds that model.
>
> **Honest scope up front (read before executing).** §7 measured that *every*
> remaining mirror handler does **both** IR-reflection **and** state mutation. So
> **A3 alone closes NONE of the current handlers** — it is the *necessary* mutation-
> half prerequisite, paired with the `.to_dict()`/dict-reflection modeling. A3 is
> therefore validated on **mutation-only witnesses** (synthetic methods that mutate
> state but do not reflect), the way `leaf-emitter-witnesses.py` validated the
> string/frame contracts before a real handler closed. Do not expect a real handler
> to flip to verified on A3 alone. (Supersedes the sketch in `a2-a3-plan.md §3`.)
>
> **Convention.** Named repo-root plan file. Byte-identical gate on the 627-file
> corpus wherever achievable; `assigns`-proof + non-vacuity gates on the witnesses.
> Leaf-first: model only the fields a target method mutates.

---

## 0. Grounding (measured, current mirror `statements.py`)

Mutation sites per state field (the `assigns` targets):

| field | sites | mutation kind | faithful WhyML type |
|---|---:|---|---|
| `_abstract_ops` (via `_add_abstract_op`) | 19 | method appends a `val` decl string | set of string |
| `_in_spec` | 10 | bool flag set/reset | bool |
| `_array_locals` | 3 | `.add(name)` | set of string |
| `_dict_locals` / `_record_locals` / `_lambda_locals` | 1 ea | `.add(name)` | set of string |
| `_ghost_{string,set,list,dict,array}_vars` | 1 ea | `.add(name)` | set of string |
| `_havoc_counter` / `_slice_set_tmp_counter` | 1 ea | `+= 1` | int |
| `_known_collection_sizes[k]` | 1 | map item set | map string int |
| `_current_record_var_classes` / `_current_append_targets` / `_inline_array_temps` | 1 ea | map/set update | map / set |
| `_has_early_ret` | 1 | bool set | bool |

**The frame machinery already exists** (partly): `statements.py::_emit_frame_condition`
turns a method's `self.<field>` assigns into the emitted `val`'s writes, and the OS
model proves `#@ assigns self.disk` on a record-typed `self` (`preamble.py`). A3 is:
make the *transpiler class* a record whose fields are the ~15 mutated state fields,
so the SAME `assigns self.<field>` path applies to them.

---

## 1. Objective & success criterion

**Objective.** The emitter class (as `self` in a `_handle_*` method) is modelled as
a WhyML **record** with a field per mutated transpiler-state slot, at its faithful
type; each mutation (`.add`, `+= 1`, item-set, `_add_abstract_op`) lowers to a
record-field write; and a method states `#@ assigns self._abstract_ops,
self._dict_locals, …` which the existing frame machinery **proves**.

**Done =**
- a **mutation-only witness** method (mutates a chosen set of state fields, no
  reflection, no string building) verifies with a correct `#@ assigns self._…` and
  its frame is proven — and a WRONG `assigns` (omitting a mutated field, or
  claiming `\nothing`) FAILS (non-vacuity);
- `_add_abstract_op` itself carries `#@ assigns self._abstract_ops` and a caller
  composing it inherits the frame;
- **byte-diff 0** across the 627-file corpus (A3 is modeling + framing on the
  self-annotate/emitter path; corpus drivers don't have a transpiler-state record);
- residual trust unchanged (no new opaque axioms).

---

## 2. The model

### 2.1 Transpiler-state record
Introduce a record type for the emitter's mutable state — **only the ~15 mutated
fields** (leaf-first; not the 246 `self._*`). Each at its faithful WhyML type:
- set-of-string: `_abstract_ops`, `_array_locals`, `_dict_locals`, `_record_locals`,
  `_lambda_locals`, `_ghost_{string,set,list,dict,array}_vars`, `_current_append_targets`;
- int: `_havoc_counter`, `_slice_set_tmp_counter`;
- bool: `_in_spec`, `_has_early_ret`;
- map: `_known_collection_sizes` (string→int), `_current_record_var_classes`,
  `_inline_array_temps`.

`self` in a `_handle_*` method is this record (mutable). Reuse the record-typed-`self`
lowering that already exists for user classes (`_current_self_type` → record; `self.x`
→ record field) — the transpiler class is just another record whose fields happen to
be the state slots.

### 2.2 Mutation lowerings (per kind)
| Python | WhyML | assigns |
|---|---|---|
| `self._dict_locals.add(x)` | `self._dict_locals := Set.add x self._dict_locals` | `self._dict_locals` |
| `self._havoc_counter += 1` | `self._havoc_counter := self._havoc_counter + 1` | `self._havoc_counter` |
| `self._known_collection_sizes[k] = v` | `self._known_collection_sizes := Map.set … k v` | `self._known_collection_sizes` |
| `self._in_spec = True/False` | `self._in_spec := true/false` | `self._in_spec` |
| `self._add_abstract_op(s)` | call to the method (below) | inherits `_abstract_ops` |

### 2.3 `_add_abstract_op` — the dominant mutator (a framed method)
Model `_add_abstract_op` as a method with `#@ assigns self._abstract_ops` +
`ensures` that its arg is now a member (`Set.mem s (result-state)._abstract_ops`).
A `_handle_*` calling it inherits `assigns self._abstract_ops` through the existing
call-frame propagation (`_emit_frame_condition` / method `assigns` on the val).
This is the single highest-leverage piece — 19 of the mutation sites are this call.

---

## 3. Work items (leaf-first)

| WI | Item | Gate |
|---|---|---|
| **A3.1** | Enumerate, per target handler, the exact mutated-field set (extend the §0 census script to per-method). Pick the **fewest-field** handler as the witness driver. | per-method assigns-set determined |
| **A3.2** | Transpiler-state record type (the ~15 fields, faithful types); `self` in a `_handle_*` bound to it (reuse record-`self` lowering). | record type-checks; `self._x` reads/writes lower to fields |
| **A3.3** | Mutation lowerings §2.2 for each kind (`.add` / `+= 1` / item-set / flag). | each lowers to a record write; byte-diff 0 |
| **A3.4** | `_add_abstract_op` framed (`assigns self._abstract_ops` + membership `ensures`); call-frame propagation to callers. | its frame proves; a caller inherits it |
| **A3.5** | **Mutation-only witness** (`transpiler-state-witnesses.py`, the leaf-witness pattern): a method that only mutates a field-set proves its `assigns`; a wrong `assigns` FAILS. | witness SUCCESS + non-vacuity |
| **A3.6** | Apply to the fewest-field real handler's **frame** (its `assigns` proven even though the handler as a whole still needs the reflection modeling to fully close). | that handler's assigns clause proves in isolation |
| **A3.7** | Docs: mark mirror **B4** progress; note the remaining `.to_dict()`/reflection wall for a full close. | docs reconciled |

---

## 4. Gate criteria

1. **Byte-identical** across the 627-file sweep — the transpiler-state record and
   its mutation lowerings only fire for the emitter/self-annotate path; corpus
   drivers have no such record, so emission is unchanged. Any diff is a regression.
2. **Witness proves** (A3.5): a mutation-only method verifies with its `assigns`.
3. **Non-vacuity**: omitting a mutated field from `assigns`, or claiming
   `assigns \nothing` on a mutating body, FAILS.
4. **`_add_abstract_op` frame** proven and inherited by a caller (A3.4).
5. **No new opaque trust** — the state record is faithful WhyML types; residual is
   the pre-existing audited base.

---

## 5. Sequencing

```
Slice 0 (validate the model, no real handler): A3.2 record + A3.3 lowerings for
   ONE field kind (a set) + A3.5 mutation-only witness that `.add`s to it.
   ⇒ proves the record + `assigns self._x` route end-to-end. Falsifiable PoC.
Slice 1 (the dominant mutator): A3.4 — `_add_abstract_op` framed + caller-inherit.
Slice 2 (remaining kinds): counters (`+= 1`), maps (item-set), flags (`_in_spec`).
Slice 3 (real handler frame): A3.6 on the fewest-field handler — prove its
   `assigns`, documenting that a FULL close still needs the reflection modeling.
Slice 4: corpus + non-vacuity gates; docs (B4).
```

**Rationale.** Slice 0 is the cheap proof-or-falsification that a transpiler-state
record + `assigns self._x` works at all (independent of any real handler). If it
resists — e.g. the record-`self` lowering assumes read-only `self` and rejects a
mutable-`self` write — that is the precise early signal, and the fallback (the
handler stays `\trusted`, enumerated) is unchanged.

---

## 6. Non-goals / honest boundaries

- **A3 does NOT close any current handler by itself.** §7: every remaining handler
  also reflects on IR dicts (`stmt.X.to_dict().get(...)`). A3 proves the *frame*;
  the reflection modeling (a separate plan) proves the *body type-checks*. Both are
  needed to un-`\trust` a real handler. A3's deliverable is the frame half + its
  witness, not a verified handler.
- **Value-faithful `ensures \result == …`** is out of scope (that is the B3 sibling-
  value modeling) — A3 is `assigns`, not `ensures`.
- **Only the ~15 mutated fields** are modelled, not the full 246-field state; a
  handler touching an un-modelled field stays `\trusted`, enumerated.
- **Mutable-`self` semantics.** If the existing record-`self` path is read-only
  (user record params are value-semantic, mutation out of scope — see
  `expressions.py` "mutating a record param is out of scope"), A3 needs a
  mutable-`self` extension. Slice 0 surfaces this immediately; if it is a large
  change, that becomes A3's true first work item (and is called out here so it is
  not a surprise).

---

## 7. Effort & risk

| Piece | Effort | Risk | Note |
|---|---|---|---|
| State record + read `self.x` | Low–Med | Low | reuse record-`self` lowering |
| Mutable-`self` writes (`.add`, `:=`) | Med–High | **Med–High** | record params may be read-only today (§6) — the crux |
| `_add_abstract_op` frame + inherit | Med | Med | reuse `_emit_frame_condition` |
| Witnesses + non-vacuity | Low | Low | leaf-witness pattern |

**Overall.** Bounded and gated, but the **mutable-`self`** question (can a record-
typed `self` be written and framed?) is the real risk and the first thing Slice 0
tests. Recommend executing **Slice 0 first** as the cheap proof-or-falsification
before committing to the full A3 build-out — exactly as B1's §6 experiment and the
no-more-int L1 measurement de-risked those.

---

## 8. Smallest first experiment (Slice 0, concretely)

A `transpiler-state-witnesses.py` with a minimal record + one set field + a method:
```
#@ assigns self._dict_locals
def mark(self, name: str) -> None:
    self._dict_locals.add(name)      # → self._dict_locals := Set.add name self._dict_locals
# and a non-vacuity twin with `#@ assigns \nothing` that MUST fail.
```
1. Model `self` as the state record; lower `.add` to a set write.
2. `assigns self._dict_locals` proves; the `\nothing` twin FAILS.
3. Byte-diff 0 on the corpus.

If 1–3 close, the transpiler-state frame route is validated and Slices 1–3 extend
it (dominant `_add_abstract_op`, then counters/maps/flags, then a real handler's
frame). If mutable-`self` resists, that is A3's real first problem, surfaced cheaply.

---

## 9. EXECUTION RESULT (2026-07-01) — Slice 0 FALSIFIED A3's foundation; mutable-`self` is the true prerequisite

Ran the §8 Slice-0 falsifiable probes first (as §5/§7 mandate). **Outcome: the
approach is falsified — `assigns` cannot soundly frame a state-mutating emitter
method on PyCSL's current `self` semantics.** Evidence (probes in scratchpad):

| probe | result | meaning |
|---|---|---|
| `bump` writes `self.n`, `#@ assigns self.n` | **SUCCESS** | a record method type-checks a field write |
| `bump` writes `self.n`, `#@ assigns \nothing` | **SUCCESS** ⚠️ | **non-vacuity FAILS** — a wrong frame passes |
| same, but `#@ assigns \nothing` on a **global**-mutating method | **SUCCESS** ⚠️ | `assigns` isn't checked for concrete bodies at all |
| `bump` + `#@ ensures self.n == \old(self.n)+1` | **SUCCESS** | the write IS modelled — within the method |
| caller: `s = St(0); s.bump(); ` `#@ ensures \result == s.n == 1` | **FAILED** | **the mutation does NOT escape** — value-semantics |

**Root cause.** PyCSL models a record `self`/param **by value**: a method's field
write mutates a LOCAL copy, is invisible to the caller, and needs no WhyML `writes`
clause. `statements.py:988` confirms a concrete body "cannot INFER its `writes` from
mutations"; the `assigns→writes` translation exists **only for abstract `val`
declarations** (the OS model's `writes {self.disk}`), not for verified bodies. So:
- every `assigns` on a state-mutating handler is **trivially `\nothing`** (nothing
  escapes) → the frame is **vacuous** and any clause passes;
- the real transpiler state **persists** across handler calls (a shared mutable
  `self`), which value-semantics cannot represent.

**Verdict — A3 as scoped is BLOCKED, and the true prerequisite is deeper than the
plan assumed.** A sound transpiler-state frame needs **mutable-reference `self` /
persistent shared-record semantics** in PyCSL: `self` as a mutable record whose
field writes ARE observable to callers and ARE checked against a `writes`/`assigns`
obligation. That is a substantial **verifier capability** (shared mutable state +
frame-checking of concrete bodies), not the bounded modeling pass A3 envisioned
(reusing the existing `assigns self.field` machinery — which §9 shows is
declaration-only, not a proven obligation).

**No code landed** (probes only; the emitter/mirror untouched). The falsifiable
Slice-0 did exactly its job: it proved, cheaply, that the frame route does not hold
on the current foundation, and located the real blocker. **Recommend a separate
"mutable-self / persistent-state" verifier plan** BEFORE any transpiler-state
modeling — A3 sits on top of it. Until then the state-mutating handlers stay
`\trusted` (enumerated), and the standing fallback (stratified trust) is unchanged.

**Net for the L5-scaling arc:** the two walls §7 named are now BOTH probed —
`.to_dict()`/dict-reflection (modeling) and A3 (mutation frame). A3's turns out to
rest on an even more basic gap (mutable-`self`), so the honest next step is that
verifier capability, not more emitter modeling.
