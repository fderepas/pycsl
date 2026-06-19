# Design Proposal — Per-function Why3 `scope` emission for apparatus-context VC isolation

DATE: 2026-06-19
STATUS: DESIGN ONLY (no code change). Basis for a human go/no-go.
AUTHOR LOOP: test-supervise-sl (extreme-rigor doctrine bearer; soundness is non-negotiable).

> **TL;DR recommendation: SPIKE-FIRST, do not build yet. Effort to build: L–XL.**
> The single biggest open risk — *whether a principled, sound scope is actually as lean
> as `--fun`* — is unproven and is exactly the thing the GAP measurements leave open.
> A ~1-day hand-written-`.mlw` spike resolves go/no-go for a fraction of the build cost.
> If the spike fails, the honest answer is **don't build it** and route the
> `_write_dir_entry` frame postconditions to Why3 prover/trigger tuning or a model
> restructure instead.

---

## 1. Problem statement (cited, not re-derived)

The os dirscan-fidelity `\trusted` retirement (`_write_dir_entry`, `\trusted` 7→6) is
blocked on ONE residual, diagnosed in
`getting-better/20260619-0905-write-dir-entry-7to6-modulesplit-GAP.md`. Restating its
measured evidence (do not re-derive):

- The two `∀k≠slot` **frame** postconditions of `_write_dir_entry`
  (`slot_inode self.dir 5 k == \old(...)` and the `slot_name` twin) **PROVE under `--fun`**
  (~48K steps each, both provers) but **OOM/Timeout in the full module**
  (GAP §"What I measured": Z3 OOM 8.86s / Alt-Ergo Timeout 329247–452958 steps).
- It is **NOT** the cited-axiom set. Direct measurement (GAP §"`--fun` vs full = IDENTICAL"):
  the emitted axiom set is **byte-identical** between `--fun` and the full file (15 = 15,
  identical names); the predicate/function decls are identical; the `_write_dir_entry`
  `let` block is **byte-identical**. Narrowing the cited axioms 15→11→9 does **not** close
  the frames (GAP §"Axiom narrowing … INSUFFICIENT").
- The real driver is the **full-module PROGRAM APPARATUS**: ~60 sibling `let` bodies + 17
  abstract self-call stubs (`self__dir_lookup_2`, `self__dir_find_slot_2`, … — all
  referencing `slot_inode`/`slot_name`/`dir_lookup`) inflating the SMT context past the
  feasibility edge (GAP §"Why the module split does NOT close it").
- `--fun` works ONLY because it trusts every sibling (emits each as a bodyless `val`) and
  drops the self-call stubs — which is **UNSOUND** as a real gate (it assumes, rather than
  proves, every sibling).
- A sound Why3 `scope` boundary that reproduces the `--fun`-lean context for
  `_write_dir_entry` *inside* the full module is the doctrine-clean close. Why3 scope
  axiom-isolation was **VERIFIED sound** this campaign (GAP §"Why3 scope axiom-isolation").
  PyCSL today emits ONE flat `module PyCSL_Program` — no scope/module/clone machinery.

**Independent re-confirmation of the Why3 mechanism (this proposal).** A throwaway probe
(`/tmp`, now removed) reproduced the isolation claim with Why3 1.8.2 + Alt-Ergo: two
sibling `scope`s in ONE module, with *contradictory* axioms over same-shaped symbols
(`slot k = 1` in `Lean`, `slot2 k = 2` in `Outer`), each proved its own `goal` in
isolation (Valid, 4 steps); and a cross-scope call `Outer.call_lean k = Lean.use_sib k`
typechecked and verified (`call_lean'vc` Valid) against `Lean.use_sib`'s PROVEN contract —
with NO body and NO axiom leakage across the boundary. The Why3 substrate is exactly as
the GAP doc claims.

### General applicability

The primary motivating use case is the dirscan retirement, but the mechanism generalises
to *any* large module where a function's VC tips into OOM/Timeout because the SMT context
is polluted by **sibling apparatus** (sibling `let` bodies + abstract self-call stubs +
module-global axioms), independent of the function's own cited axioms. The monitoring
skill already documents the symptom family in two places:

- A.7 / catalog-B "context pollution mis-blamed on a missing contract" — a theorem
  `Unknown` in-module but Valid in `--fun`/isolation; fix is to *split*, not to weaken
  (`config/skills/pycsl-monitoring/SKILL.md` A.7; row B "Aggregate noise mistaken for a
  residual"; `getting-better/20260616-2050-formal-test-context-pollution.md`).
- The generalised diagnostic the GAP doc adds: *before blaming "axioms in scope," `diff`
  the full-emission vs `--fun` axiom set; if identical, the wall is apparatus-context
  feasibility, and only a scope that prunes the program apparatus will help.*

So the feature, if it works, is a general "verify this function against a lean,
sound sub-context" capability — not a one-off os hack. That said, the dirscan frames are
the *worst* case (they need ~`--fun`-level leanness), so they are the right de-risking target.

---

## 2. Current emitter analysis (where the flat module + apparatus come from)

PyCSL emits the entire program as ONE flat `module PyCSL_Program`. The assembly is
`Module6_WhyMLTranspiler.transpile()`
(`src/pycsl/Module6_WhyMLTranspiler.py:391-587`):

| Apparatus | Emitted by | Site |
|---|---|---|
| `module PyCSL_Program` header | `_emit_preamble` → `_emit_preamble_uses` | `preamble.py:1246` (`"module PyCSL_Program"`), called at `Module6_WhyMLTranspiler.py:400` |
| **module-global axioms** (`#@ proof`-cited, e.g. `slot_inode_byte_decode`, `field_to_str_round_trip`, the marker axioms) | `_emit_preamble_axioms` — scans EVERY function's `#@ proof` entries, emits each cited axiom once, module-globally | `preamble.py:1650-1714` (registry lookup `_AXIOM_REGISTRY[qn]`, `preamble.py:1706`); called `Module6_WhyMLTranspiler.py:463` / `:472` |
| **class-invariant axioms** (uniq / slots_lt32 maintenance) | `_emit_class_inv_axioms`, hoisted before the record so they are in scope at the establishment VC | `preamble.py:1614-1648`; called `Module6_WhyMLTranspiler.py:435` |
| **record/datatype decls** | `_emit_type_decls` | `Module6_WhyMLTranspiler.py:437-438` |
| **module globals** (`_filesystem` singleton) | `_emit_module_globals` | `preamble.py:2067`; called `Module6_WhyMLTranspiler.py:465`/`:476` |
| **every function as a real `let` body** (the ~60 sibling `let`s) | `_emit_function`, in SCC order | loop `Module6_WhyMLTranspiler.py:579-581`; `sort_functions_by_scc` at `:579` |
| **abstract self-call stubs** (`self__dir_lookup_2`, …, 17 of them) | abstracted at each `self.<m>(...)` call site to a `val self__foo_<n>` carrying the callee's propagated contract clauses | documented `functions.py:716-723` ("every `self.foo(...)` is abstracted as `val self__foo_<n> …`"); the propagated clauses are built by the `_build_method_*_ensures_map` family, `Module6_WhyMLTranspiler.py:544-571` |
| **trailing abstract-val block** | `_insert_abstract_val_block` | `abstract_ops.py:150-191`; called `Module6_WhyMLTranspiler.py:587` |
| **module terminator** | `out.append("end")` | `Module6_WhyMLTranspiler.py:586` |

**How a single function's VC ends up with all of it in scope.** Because everything above
is appended into one `out` list bracketed by `"module PyCSL_Program"` … `"end"`, a Why3
`axiom`/`val`/`let` is in scope for *every* `goal` from its point of declaration onward
(flat theory). So when Why3 generates `unixinodefilesystem___write_dir_entry'vc`, the SMT
context it ships to Alt-Ergo/Z3 contains: all module-global axioms, all class-invariant
axioms, the record + globals, AND every sibling `let`'s declaration plus the 17 self-call
stubs (each carrying `slot_inode`/`slot_name`/`dir_lookup` references). That is the
"apparatus" the GAP measured. `--fun X` (`pycsl.py:484-488`, per the GAP) re-emits every
*other* function as a bodyless `val` and drops the self-stubs — which prunes the apparatus
but trusts the siblings (unsound).

**Key emitter fact for the design:** there is **no scope/module/clone emission anywhere**
— `grep` for `scope`/`clone` in the emitter finds only the English word "scope" in
comments. A scope boundary is a genuinely new emission capability.

---

## 3. Why3 mechanism — scope/clone isolation with sound cross-scope calls

Why3 `scope` (and the heavier `module` + `clone`) provide **lexical symbol + axiom
isolation** while keeping cross-scope calls sound and typechecked:

- Symbols (`val function`, `axiom`, `let`, `predicate`) declared inside `scope S … end`
  are visible *inside* S and, from outside, only via the qualified name `S.foo`.
- An `axiom` constrains its symbols only **within its enclosing scope** (and from its
  declaration point onward). Two sibling scopes can carry *contradictory* axioms over
  identically-shaped symbols and each proves in isolation — **verified** (GAP §"Why3 scope
  axiom-isolation"; re-confirmed by the probe in §1: `lean_ax: slot k = 1` and
  `outer_ax: slot2 k = 2` coexist, each goal Valid).
- A cross-scope call is sound because the callee is referenced by its **declared contract**
  (a `val`'s `ensures`, or a `let`'s proven `ensures`), not its body — the caller's VC sees
  only the contract. The probe's `Outer.call_lean k = Lean.use_sib k` verified against
  `Lean.use_sib`'s `ensures { result = 1 }`, which `Lean` itself discharged from its own
  axiom — **no axiom and no body crossed the boundary.**

### What a "lean scope for `_write_dir_entry`" would contain

A sound lean scope `WriteDirEntry` would hold, and ONLY hold:

1. The `_write_dir_entry` `let` body itself (so its VC is generated and fully discharged).
2. The `#@ proof` axioms it genuinely needs — the dir-blit marker axioms (intro/insert),
   the slot decode/round-trip keystones it cites, and the class-invariant
   (uniq/slots_lt32) axioms — and **only** those (the read-side dir axioms
   scan_reflects_present/remove_*/dir_lookup_frame stay in the outer scope, per the GAP's
   "the lean context that works is essentially hide everything but the marker axioms").
3. The record type + the `slot_inode`/`slot_name`/`dir_lookup` `val function` declarations
   (typing), but NOT the sibling `let` bodies and NOT the 17 self-call stubs.
4. For any sibling `_write_dir_entry` *calls* (e.g. `_blit_dir_entry`): the sibling's
   **PROVEN contract only** — a bodyless `val` whose `ensures` is exactly what that sibling
   discharged *in its own scope*. NOT the sibling's body, NOT its self-stubs.

The outer module then references the lean scope's proven `_write_dir_entry` contract by
qualified name; every consumer (`sys_rename`, `_read_directory`, …) sees only that
contract, exactly as it sees a sibling today via the abstract-val stub.

---

## 4. The soundness argument (load-bearing)

**The bar.** The boundary must be a **PROVEN interface, NEVER a `\trusted`.** Any design
that *relocates trust* — a boundary that ASSUMES rather than PROVES a sibling's contract —
is **disqualified** under the extreme-rigor doctrine (`test-supervise-sl.md` §Doctrine 3;
`pycsl-monitoring/SKILL.md` "BINDING"). This is precisely what separates a sound scope
split from `--fun`: `--fun` *assumes* every sibling (`val` with no obligation to prove it);
a scope split *proves* every sibling in its own scope and only then exposes its contract.

**The argument, spelled out:**

1. The lean scope `WriteDirEntry` must **FULLY DISCHARGE** the `_write_dir_entry` body — all
   its VCs (the two frame postconditions, the value postconditions, the marker discharge,
   the uniq/slots_lt32 type-invariants) Valid, zero `\trusted`, inside that scope.
2. Every sibling `_write_dir_entry` calls is represented by its **VERIFIED contract**, where
   "verified" means: that sibling is *also* emitted as a real `let` (in its own scope or the
   outer module) and its contract is discharged there. The contract `_write_dir_entry`
   consumes is the *same* contract the sibling proved — never a wider one. This is exactly
   the **narrowing-VC discipline** already in the codebase (§ below): the visible interface
   must be a sound weakening of (i.e. provable from) the definition.
3. Symmetrically, the outer module exposes `_write_dir_entry` to its consumers by its
   proven contract only, and the *consumers* are still proven in the outer scope — so no
   obligation is dropped anywhere; it is only **relocated to where it is discharged**.
4. The net TCB is therefore **unchanged**: every function is proved exactly once, against a
   contract that is itself proved. No new axiom, no `\trusted`, no weakened clause. The
   ONLY thing the scope changes is *which other declarations share the SMT context* at each
   VC — a performance/feasibility lever, not a trust lever. (Soundness probe for the
   eventual implementation, per the catalog: re-run `requires slot_inode(self.dir,5,0)==3`
   to confirm the lean-scope pass is not an empty-disk artifact; and a falsification
   probe — a wrong-slot blit must RED the lean scope.)

### Relation to the existing Track-B opacity machinery (`#@ interface` / `#@ reveal`, b3d65d1)

This is the crucial reuse question, and the honest answer is: **scope emission should
GENERALISE Track-B, and Track-B already supplies the soundness primitive — but the two are
distinct mechanisms that compose.**

Track-B (commit b3d65d1; corpus exhibit `test-suite/corpus/pycsl-reference/0660.py`) gives
a function TWO contracts: a rich **definition** (verified against the body) and a narrow
**`#@ interface`** (what importers see). Crucially it emits a **narrowing VC**
`<fn>__narrows_ens_k` / `<fn>__narrows_req` in the owning unit
(`functions.py:314-362`, `_emit_narrowing_vc`):

```
goal <fn>__narrows_ens_k : forall params, _res. (def_req) -> (def_ens) -> (iface_ens)
goal <fn>__narrows_req    : forall params.       (iface_req) -> (def_req)
```

This is **already the exact soundness primitive a scope boundary needs**: it PROVES (does
not assume) that the contract a consumer sees (`iface`) follows from what the body
established (`def`) — fail-loud, an over-claiming interface makes the goal unprovable
(b3d65d1 commit message: "manual PROVE-neg … fails narrows_ens_0"). And it is already
**opt-in + corpus-inert**: absent `#@ interface`, interface = definition, byte-identical
(b3d65d1: "os holds at 23 (feature inert without #@ interface)").

**Honest comparison:**

| | Track-B `#@ interface` (b3d65d1) | Scope emission (proposed) |
|---|---|---|
| What it controls | *which CONTRACT* a consumer sees (narrow vs rich) | *which DECLARATIONS share the SMT context* at a VC (apparatus pruning) |
| Soundness primitive | narrowing VC: `def ⟹ iface`, proven | the SAME narrowing-VC discipline, applied at the scope boundary |
| Solves the dirscan wall? | **No.** The frames OOM with the *full apparatus in scope* regardless of contract narrowness; the GAP measured that narrowing the cited axioms (a contract-level lever) does NOT help | **Yes (if lean enough).** It removes sibling `let`s + self-stubs from the VC context |
| Relationship | the *interface/narrowing* half | the *context-isolation* half; consumes Track-B's narrowing VC to keep the boundary proven |

So: **scope emission is NOT subsumed by Track-B, and Track-B is NOT subsumed by scope
emission.** Track-B narrows the *contract*; the dirscan wall is a *context* problem
(identical axioms in scope, GAP §2). But scope emission **must reuse Track-B's narrowing
VC** as its boundary-soundness check — that is what makes the boundary PROVEN, not trusted.
The b3d65d1 P4 finding is also a direct warning for option (b) below: applying `#@ interface`
to `_pack_inode` could narrow the ensures but the definition's REQUIRES could not be
soundly narrowed and **bloated the 8 callers → os timed out** (b3d65d1 commit message).
A scope split has the symmetric hazard — the *requires* a lean scope needs must be
establishable by every cross-scope caller.

---

## 5. Design options

### Option (a) — per-function `#@ verify_scope` directive: emit ONE function (+ its declared deps) into a lean Why3 `scope`

A function tagged `#@ verify_scope` is emitted inside its own `scope <Fn>`, which imports:
its body; the `#@ proof` axioms it cites (and ONLY those — not the module-global set); the
record + the `val function` typing decls; and, for each sibling it calls, that sibling's
**proven contract** as a bodyless `val` (reusing the existing abstract-val + Track-B
narrowing machinery for the boundary). The outer module references `<Fn>.<fn>`'s proven
contract; consumers are unchanged.

- **Soundness:** highest — the function is fully discharged in the lean scope; siblings are
  proven elsewhere and crossed by contract via the narrowing VC. No trust relocation.
- **Reproduces `--fun`-lean context?** Closest of the three: only the cited axioms + called
  siblings' contracts share the VC context; the ~60 sibling bodies and 17 self-stubs are
  GONE. This is the configuration the GAP says is needed.
- **Blast radius:** medium-high. New `#@` directive (5 normative surfaces + skill, §6); new
  emission path in `transpile()` that brackets a function in `scope … end` and re-routes its
  axiom selection from module-global to scope-local; the abstract-val/self-stub machinery
  must be told to emit *into* the scope and to pull only cited axioms.
- **Effort:** L.

### Option (b) — generalise Track-B `#@ interface` to a whole-class / partition boundary

Promote the existing `#@ interface` from per-function to a **partition**: a group of
functions emitted into one `scope`, exposing narrow interfaces to the rest of the module.

- **Soundness:** sound *iff* every cross-partition call's required contract is establishable
  — but the b3d65d1 **P4 finding is a live counterexample**: narrowing ensures while the
  definition's requires can't be narrowed bloats callers and times out os. A whole-class
  boundary inherits that hazard at scale.
- **Reproduces `--fun`-lean context?** Partially — it prunes *cross-partition* apparatus,
  but a partition still co-locates all its members' apparatus. If `_write_dir_entry`'s
  partition includes the other dir mutators, their self-stubs/bodies still pollute its VC.
- **Blast radius:** medium (reuses Track-B parsing/IR), but the P4 requires-bloat trap is real.
- **Effort:** M–L.

### Option (c) — opt-in `#@ partition <name>` grouping functions into independently-verified scopes (coarse)

Author assigns functions to named partitions; each partition is a scope; cross-partition
calls go by proven contract.

- **Soundness:** same primitive as (a)/(b); sound if cross-partition requires are
  establishable.
- **Reproduces `--fun`-lean context?** Only if the partition is a SINGLETON `{_write_dir_entry}`
  — at which point it degenerates to option (a). For the dirscan wall the partition must be
  ~singleton (the GAP: the lean context is essentially "hide everything but the marker
  axioms + the clean blit `val`"), so (c) buys nothing over (a) for this case.
- **Blast radius / effort:** similar to (a) but with more author surface (a grouping scheme).

**Recommendation among options: (a)**, with the boundary soundness check **reusing Track-B's
narrowing VC**. It targets the measured need (singleton-lean context) most directly and adds
the least author surface. (b)/(c) are generalisations to consider only *after* (a) proves the
mechanism works for the worst case.

---

## 6. Blast radius / corpus inertness

The feature MUST be **opt-in and corpus-inert by default** (existing modules' emitted `.mlw`
byte-identical; the byte-diff gate stays 0/N). Achieved exactly as Track-B (b3d65d1) and
`#@ propagate_frame` / `#@ fresh_globals` already do:

- A function is scoped ONLY if it carries `#@ verify_scope`. The `transpile()` loop
  (`Module6_WhyMLTranspiler.py:579-581`) keeps emitting flat `let`s for every unmarked
  function; the scope-bracketing branch fires only when `func.get("verify_scope")` is set
  (mirroring `func.get("interface")` at `functions.py:603`, `func.get("propagate_frame")`
  at `functions.py:1304`, `func.get("fresh_globals")` at `functions.py:640`).
- Default-empty marker set → no module without the marker reorders → **byte-identical**
  (the same pattern the codebase uses for `_sibling_concrete_methods`,
  `Module6_WhyMLTranspiler.py:486-487`, explicitly "Default-empty -> … byte-identical").
- The new `#@` directive is **doc-coherency-gated**: per
  `config/skills/pycsl-doc-coherency/SKILL.md` and `bin/doc-coherency.py --check`, a new
  directive must appear in `test-suite/annotations.md` (canonical) + `README.md` +
  `docs/pycsl-concrete-syntax-reference.md` + `docs/pycsl-static-semantics-reference.md` +
  `docs/pycsl-translational-reference.md` + a relevant `config/skills/` skill (the 5
  normative surfaces + a skill). The PyCSL-language gate (`pycsl-audit-pycsl-language`)
  additionally requires wiring through grammar → validate → IR → WhyML with a
  *semantically faithful* lowering — here the faithfulness claim is the §4 soundness
  argument (every function proved once, against a proven contract).
- A reference-corpus exhibit is required by the new-feature convention
  (`memory/feedback_reference_corpus.md`): add a `test-suite/corpus/pycsl-reference/####.py`
  demonstrating `#@ verify_scope` (the natural shape is a two-function module where the
  scoped function proves in-scope but would OOM flat — a shrunk dirscan analogue).

---

## 7. Incremental rollout + concrete first milestone

**Milestone 0 (the de-risking SPIKE — do this BEFORE writing any emitter code; see §8).**
Hand-write the lean-scope `.mlw` for `_write_dir_entry` (copy the `--fun` emission, wrap
`_write_dir_entry` + its cited marker/decode axioms + a bodyless `val _blit_dir_entry` with
its proven contract into `scope WriteDirEntry … end`, leave the rest of the module flat
outside). Run `why3 prove -G unixinodefilesystem___write_dir_entry'vc` best-of-N. **Decision
gate:** do the two frame postconditions go **Valid** with this *sound* scope (siblings
present as proven contracts in the outer module, NOT trusted away)? If YES → build option
(a). If NO → the scope is not lean enough; **abandon the feature**, route to §8 alternatives.

**Milestone 1 (smallest sound build).** Implement `#@ verify_scope` for a single function:
bracket it in `scope <Fn> … end`, emit scope-local cited axioms, emit called siblings as
proven-contract `val`s with the Track-B narrowing VC enforcing the boundary, reference
`<Fn>.<fn>` from the outer module. Tag `_write_dir_entry` (and `#@ proof`-cite only the
marker axioms in its scope). **Success criteria:** both frame postconditions Valid in-module;
`__init__` gate green; corpus byte-diff 0; `\trusted` os 7→6; soundness + falsification
probes pass.

**Generalisation.** Once Milestone 1 holds, tag the other 5 dirscan helpers (`_write_entry`,
`_zero_entry`, `_dir_lookup`, `_dir_find_slot`, `_dir_find_free` — the
`pycsl-monitoring/SKILL.md` §C "dirscan-fidelity ×6") and retire them one at a time, each a
separate lean scope, each gated. Beyond os, `#@ verify_scope` becomes the standard tool for
any function the A.7 diagnostic flags as apparatus-polluted.

---

## 8. Risks, alternatives, honest cost/benefit, recommendation

### Effort: **L–XL** to build option (a). **S (~1 day)** for the de-risking spike.

### The single biggest risk — and why it gates everything

**Will a *principled, sound* scope actually be as lean as `--fun`?** This is **unproven and
is the crux.** The GAP doc is explicit (§"Why the module split does NOT close it"): "the lean
context that works is essentially *hide everything but the marker axioms + the clean blit
`val`*, not a small axiom subset — so the scope would be very aggressive." `--fun` is lean
because it has **zero** sibling bodies and **zero** self-stubs. A *sound* scope for
`_write_dir_entry` still needs, at minimum, the bodyless `val` contracts of the siblings it
calls (and possibly the typing decls for `slot_inode`/`slot_name`/`dir_lookup` that the
marker axioms reference). If even those few contract-`val`s re-introduce enough E-matching
to tip the frames back into OOM, **a sound scope is NOT lean enough and the feature does not
solve the problem.** The GAP could not measure this because no sound scope was built — which
is exactly why the spike (Milestone 0) must come first. **I flag this as the key open risk,
not as a solved problem.** Do not build the XL feature on the unverified assumption that the
principled lean context matches the unsound `--fun` one.

Secondary risks:
- **Requires-bloat at the boundary** (the b3d65d1 P4 trap, §4): if the lean scope needs a
  `requires` that cross-scope callers can't establish, it relocates the wall to the callers
  (catalog A.9 "adding a leaf precondition RELOCATES a residual"). Mitigated by the narrowing
  VC's `narrows_req` direction, but must be measured.
- **Blast radius on the emitter:** scoping touches the most load-bearing assembly path
  (`transpile()`), axiom selection (module-global → scope-local), and the abstract-val/self-
  stub routing. High regression surface; the byte-diff gate is the guard.

### Alternatives (assessed honestly)

1. **Why3 prover-weight / trigger / `meta` tuning** (GAP §"What a future session needs" item 2;
   `pycsl-monitoring/SKILL.md` row B for `field_to_str_frame`). LOW blast radius, no new
   feature — tune the marker/decode axiom triggers or solver weights so the two frames are
   feasible in the full apparatus. **This is the cheapest alternative and should be tried in
   the SAME spike window** (it may close the frames without ANY scope feature). Uncertain,
   but if it works, the whole proposal is moot — an honest and valuable outcome.
2. **Restructure the os model** so `_write_dir_entry`'s frames don't depend on the polluting
   apparatus (e.g. fold the frame into a single cited maintenance atom that doesn't coexist
   with the sibling stubs — the catalog-B "folded `insert/zero_preserves_dir_invariant`"
   route). Medium effort, model-local, no new language surface.
3. **Accept the GAP.** `_write_dir_entry` stays `\trusted` (os `\trusted` stays 7), logged
   to the human, marker banked. Zero cost, zero risk; the residual is honestly tracked.

### Recommendation

**SPIKE-FIRST.** Spend ~1 day on Milestone 0 (hand-written sound lean scope) **and**
alternative-1 (prover/trigger tuning) in parallel, on the existing
`PROPOSAL-write-dir-entry-detrust-v2.patch` substrate. Decision tree:

- If alternative-1 closes the frames → ship that (LOW blast radius); **don't build scope
  emission.**
- Else if the sound lean scope closes the frames → build option (a), Milestone 1 (effort L),
  reusing Track-B's narrowing VC for the boundary; retire the dirscan ×6 incrementally.
- Else (the sound scope is not lean enough, the key risk realised) → **don't build it**;
  keep the GAP, route to model-restructure (alternative 2) or accept (alternative 3).

I do **not** recommend committing to the L–XL build today. The feature is architecturally
clean and doctrine-compliant (PROVEN boundary, not trust), and would be genuinely general —
but its payoff hinges entirely on the unverified leanness assumption, and a cheap spike
resolves that before the expensive build. Building first and discovering the sound scope
isn't lean enough would be the costly mistake this proposal exists to prevent.
