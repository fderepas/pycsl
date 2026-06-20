---
name: pycsl-monitoring
description: >-
  The accumulated, Gate-S-audited knowledge base of the `test-supervise-sl`
  squeeze loop (the monitor that drives `formal-test-sl`). Holds the proven
  patterns for getting PyCSL formal tests to fully prove, the coherent-and-wrong
  catalog for formal tests (the vacuous-test shapes), per-module coverage ledgers,
  and the discipline for adding knowledge (only via Gate S, traceable, carve-outs
  cite the upper bound). Consult and update this whenever supervising or monitoring
  a fleet of formal-test runs, deciding whether a learned heuristic is in-band,
  diagnosing why a formal test will not prove, or recording coverage. Trigger
  phrasings: "monitor the formal-test loop", "what patterns make a formal test
  prove", "is this formal test vacuous", "record formal-test coverage", "audit a
  consolidated formal-test skill", "Gate S on a PyCSL heuristic", "what's the os
  formal-test coverage".
---

# pycsl-monitoring — knowledge store for `test-supervise-sl`

This skill is the **persistent, disjoint knowledge base** that the supervising loop
`test-supervise-sl` (see `test-supervise-sl.md`) accumulates while monitoring the
base loop `formal-test-sl` (see `formal-test-sl.md`). It is written **only by the
disjoint skill-monitor**, never by the base loop about itself (that would be
self-judging). Everything here has passed **Gate S** (`sl-monitoring-sl`).

## BINDING: the extreme-rigor path is the ONLY path

`test-supervise-sl` is the bearer of the extreme-rigor doctrine (full text in
`test-supervise-sl.md` §Doctrine). The operative rule, restated here because every
run reads this store: **a residual is NEVER closed by adding trust.** A raw
`\trusted`, a reviewer-trusted helper, or a "ready trusted swap" (e.g.
`_rename_swap`) is **struck from the option set** — it is a Gate-B/Gate-C REJECT, not
a choice. The only sanctioned closure routes are (a) Rocq+Lean cross-validated +
cited `#@ proof`, (b) a restructured / re-folded proof, (c) a different prover /
tactic. **If none discharges the goal, the target is a LOGGED GAP routed to the
human — never a trusted "done", and never offered as "accept the trusted swap".**
Adopting even a cross-validated axiom (kernel-PROVED, not bare `\trusted`) is a
human-gated TCB decision, not the loop's. Recorded GAPs under this rule (e.g.
`sys_rename`, see §C) stay open until a rigorous route lands.

## Discipline for adding knowledge (non-negotiable)

- **Gate S first.** A heuristic enters this file only after the skill-monitor
  classified it (ignore-signal vs defer-to-oracle), ran the matching check (trigger
  / validity test against the PyCSL oracle), and returned PASS or CARVE-OUT. A
  REJECT is logged, not kept.
- **Grounded & traceable.** Each entry cites the upper-bound clause (spec /
  methodology rule) it serves, and the run/inputs that revealed it.
- **Carve, don't discard.** Narrow an over-general skill with a bound-deferring
  exception; keep the valid core.
- **Safe direction.** An entry may only make a formal test *stronger / more
  faithful*, never license a weaker or vacuous one.
- **Disjoint authorship.** Only the monitor writes here. The base loop may *propose*
  a skill (a returned soft output); it does not *enter* it.

---

## 0. Tooling landed by this loop

- **Per-goal best-of-N prover dispatch (LANDED 2026-06-18, `src/pycsl/pycsl.py`).**
  A goal is now **Valid iff ANY first-class prover proves it Valid**, instead of
  the legacy `why3 prove -P A -P B` single call — which (with `-a split_vc`) runs
  ONLY the LAST `-P` per goal, so the default `[Alt-Ergo, Z3]` effectively ran
  **Z3-only** and masked every Alt-Ergo-only win behind a Z3 `Unknown`. The new
  dispatch (`_dispatch_provers` / `_merge_best_of_n` / `_verdict_rank`) runs each
  prover as its OWN `why3 prove` call and keeps the BEST per-goal verdict.
  - **SOUND:** a goal is promoted to Valid ONLY when a prover's `Prover result is:`
    line literally reads `Valid` (the `_verdict_rank` chokepoint; `Invalid`,
    `Unknown`, `Timeout`, `Out of memory`, `Failure` can never be promoted).
    Best-of-N over sound provers is sound. Soundness probe: a false ensures
    (`return x` under `ensures \result==x+1`) stays **Unknown → FAIL exit 1** after
    the change; a mixed file (one true + one false goal) correctly reports the false
    one unproven.
  - **TIMING preserved:** attempts the **last-listed (legacy-reported) prover
    first** and EARLY-EXITS once all goals are Valid, so Z3-proved goals cost ~one
    Z3 pass (unchanged); only Z3-residual goals pay a second (Alt-Ergo) pass. Order
    is soundness-neutral (Valid-iff-ANY ⇒ same accepted set for any order). Running
    Alt-Ergo first instead is catastrophic (0665 inode codec: ~40s Z3-only →
    minutes of Alt-Ergo 30s/goal timeouts before Z3).
  - **`-p <prover>` unchanged:** a single prover takes the byte-identical legacy
    single-call path (still forces exactly that prover).
  - **Emission unaffected:** the change is entirely in the proving path
    (post-`--no-proof`); corpus byte-diff 0/605.
  - **Consequence:** `0714.py` (the `field_to_str_frame` exhibit) now verifies
    SUCCESS under the DEFAULT pipeline with **NO `# pycsl-flags: -p alt-ergo` pin**
    (removed). The future `_write_dir_entry` citation site no longer needs an
    Alt-Ergo pin. Resolves the proposal in
    `getting-better/20260618-1710-field-to-str-frame-z3-cannot-apply-nested-forall-frame.md`
    (now marked IMPLEMENTED).

## A. Proven patterns (what makes a PyCSL formal test fully prove)

*(Seeded from the os work; each is a PASS/CARVE under Gate S.)*

1. **Test the observable CONSEQUENCE, not the op's return code.** A formal test is
   setup → operate → observe (write→read-back; mkdir→stat-sees-it→rmdir→stat-gone).
   Asserting the op's own `\result` is vacuous. *(Serves: the consequence rule.)*
2. **Call the public API; never simulate.** The driver calls `os.*` / the module
   API; it never re-implements the op on the data structure or inlines internals.
   Enforced physically: the driver author's context has API + spec only, not the
   internals — so it *cannot* simulate. *(Serves: the calls-the-API rule.)*
3. **Leaf-first, compose-don't-re-derive.** When a clause won't discharge, the cause
   is usually a missing **leaf VALUE contract**; fix bottom-up (the codec leaves'
   value contracts compose into the inode round-trip; the syscall reuses proven
   contracts via `#@ no_inline`). Never weaken the test to land.
4. **Cross a `#@ no_inline` boundary with a FOLDED uninterpreted atom, never a bare
   `∀i`.** A `\forall i …` (and `\array_eq`, which lowers to the same `∀i`) does NOT
   propagate across a `no_inline` boundary (Alt-Ergo and Z3 both go Unknown). Fold
   the per-element fact into an uninterpreted predicate (e.g. `block_content_eq`)
   with definitional intro/elim; the atom crosses as one term. *(This is the gap-17
   content-round-trip mechanism.)*
5. **A non-vacuous range/value postcondition needs an early-return guard.** If an
   early path (`if n == 0: return 0`) returns before establishing the claimed field,
   guard the ensures antecedent (e.g. `\result >= 1`) — else the claim is false on
   that input. *(Carve-out from the fd_block empty-write bug this session.)*
6. **Re-run the gate on the COMMITTED artifact; never re-report an intermediate
   count.** A green taken from an intermediate run while the committed file is red is
   the self-declared-done collapse. Run `PYTHONHASHSEED=0` on the file as it stands.
7. **Keep array-heavy reopen/read/write consequence theorems in their OWN file.**
   A light fd-chain / namespace theorem that PROVES in isolation can flip to
   `Unknown` purely by being co-located with a heavy `open→write→close→reopen→read`
   theorem in the same module (shared E-matching context starves the light goal's
   step budget). Byte-identical body + import set, different verdict — the only
   variable is the sibling theorems. Diagnose by re-proving the goal alone; do NOT
   blame a missing contract. *(Carve-out: split `content_round_trip*` out of
   `formal_os_fd`/`formal_os_rwsize` this session; see
   `getting-better/20260616-2050-formal-test-context-pollution.md`.)*
8. **Co-import an array-trigger op (`mkdir`+`access`) with a return-code-only
   filesystem stub.** Importing `chmod`/`truncate` alone yields
   `unbound type symbol 'array'` at L3-tc — the emitter omits `use array.Array`
   when no imported contract carries an explicit array term, even though the
   pulled-in helper `val`s reference `array int`. Co-importing+calling `mkdir`
   (whose `dir_lookup` ensures is an array term) emits the `use`. *(CONFIRMED
   emitter bug: `bugs-to-report/20260616-2050-import-stub-missing-use-array.md`.)*

9. **Adding a leaf precondition can RELOCATE a residual, not close it — re-prove the
   CALLER in isolation before claiming the win.** A failing callee Precondition
   sub-goal (e.g. `_unpack_direntry` calling `_unpack_uint16_be` with `0<=data[..]<=255`
   it can't establish) is "fixed" by requiring the byte-range at the callee — but that
   only makes the callee prove; the obligation moves to EVERY caller, which may equally
   lack the fact. Verdict rule: a fix that keeps the total non-Valid COUNT the same (or
   adds an unmet caller obligation) is NOT a win, it is a relocation → REVERT. Diagnose
   by `--fun <caller>` after the edit: if the same Unknown fingerprint reappears at the
   caller, the real missing fact is upstream (here: a directory-region disk byte-range
   predicate the model doesn't have). Route bottom-up to the genuine source fact;
   if that needs a model extension, it's a GAP, not a cheap win. *(Carve-out from the
   2026-06-17 `_unpack_direntry` WIN-1 probe;
   `getting-better/20260617-0909-direntry-byte-range-gap.md`.)*
10. **Retiring a `\trusted` stdlib leaf: string-UNIVERSAL ensures retires, transform-
   SPECIFIC does not.** The decisive classifier — *is the ensures true of an ARBITRARY
   result string, regardless of what the transform does?* If YES (e.g.
   `\str_length(\result) >= 0`, "result is a string"), it retires cleanly to
   `#@ \abstract` + `#@ proof rocq|lean <Lemma>` citing a `forall s. ...` lemma that
   needs NO transform definition — kernel-PROVED in both provers (Rocq "Closed", Lean
   no-axioms), byte-diff 0, gates green. If it depends on what the transform DOES
   (`capwords` `len <= len`, `f("")==""`), it is STILL retirable — but only by writing a
   FAITHFUL kernel DEFINITION of the transform and proving the property about THAT (a
   real `Definition`/`Fixpoint`, not an assumed `Variable`), then citing it. The
   residual trust becomes the definition's FAITHFULNESS (auditable: keep it transparently
   matching the spec), not a silent assertion. What is forbidden is a cited axiom that
   re-assumes the property about an abstract symbol (surfaces as a kernel `Axiom`/extra
   Lean axiom, fails `--reverify`). *(strmod 2026-06-17: bare-trust 7→**0** — 6 universal
   retired via `Pycsl.Strmod.StrLen.length_nonneg`; `capwords` retired via
   `Pycsl.Strmod.Capwords` over a faithful `capwords_def =
   join_sp(map capitalize (split_ws s))`, Rocq "Closed" / Lean ⊆{propext,Quot.sound}.)*
11. **A no-ENFILE / free-resource trust on a MONOTONIC-COUNTER model is NOT retirable by
   adding a precondition — it needs a model upgrade.** Class-4 trusts that assert "a
   fresh resource is always available" (e.g. os `fd-resolution-fidelity` on `sys_open`/
   `sys_dup`: `\result >= 3`) are genuinely FALSE at resource exhaustion. De-trusting +
   adding the honest precondition (`requires next_fd < 64`) makes the LEAF body verify
   (measured: `sys_dup` 46/0, zero trust) — but if that precondition is **not
   establishable through the public API** (no op bounds the counter; `close` doesn't free
   a slot), it reds the public formal tests (`formal_os_fd`/`fdchain`). **A precondition
   that reds a previously-green formal test is a REGRESSION, even when the leaf itself
   verifies cleanly** → revert. The doctrine-correct route is a faithful **allocator** (a
   free-slot scan + an occupancy invariant the caller can establish), OR a logged GAP —
   never a bare `\trusted`, never a precondition the API can't discharge. *(os
   `fd-resolution-fidelity` ×2, 2026-06-18:
   `getting-better/20260617-2317-os-fd-resolution-fidelity-class4-wall.md`.)* Corollary
   (os-gate blind spot, reconfirmed): the `__init__` gate stays green when a callee
   precondition is added because it imports `sys_*` as trusted `val`s — green there does
   NOT mean a wrapper discharges the new precondition; ALWAYS run the public formal tests.
12. **Building the allocator (A.11) is a MODEL-SOUNDNESS win but may not retire the trust —
   the blocker can move to the import-boundary frame-ensures propagation.** os gained a
   faithful `_alloc_fd` (verified, zero trust; first-free-slot scan + honest ENFILE),
   `sys_open`/`sys_dup`/`sys_creat` routed through it, body gate 2047→2092, full suite
   18/18, `__init__` 1159/0 — a genuine model upgrade (the monotonic `next_fd` counter,
   which falsely read "full" after 61 opens, is retired). BUT bare `\trusted` stayed 8:
   the honest free-slot-conditioned `\result>=3` is body-provable, yet the side-condition
   "a free slot exists" cannot SURVIVE THE IMPORT BOUNDARY — each syscall `val` havocs the
   whole `fd_open` array, and the propagation machinery
   (`_build_method_field_param_frame_ensures_map` / `_dotted_ensures_suffix`) **drops
   `\result`-referencing quantified single-cell frame ensures** (kept frames must be
   quantifier-bearing, self-field+param, NO `\result`). So a faithful model fix can leave
   a NAMED TOOL gap as the residual wall. Land the soundness win; log the tool-gap GAP;
   never force a retirement that reds a gate/test. *(os fd-reuse allocator, 2026-06-18:
   `getting-better/20260618-0903-os-fd-import-boundary-frame-gap.md`.)*
13. **The import-boundary `\result`-frame propagation gap (A.12) is now SOLVED — and the
   wall moved ONE deeper to module-global-initial-state.** A new
   `_build_method_result_frame_ensures_map` (twin of the param-frame map; opt-in via
   `#@ propagate_frame`) carries `\result`-referencing single-cell self-field frames across
   the method-call/import boundary. Key fact: inside the abstract `val`, `\result` lowers to
   Why3's `result` keyword automatically — no substitution needed. **Corpus-inert** (byte-diff
   0/603 — only os emits it). With it, `sys_dup`'s free-slot-conditioned no-ENFILE is
   body-provable AND the free-slot fact survives a prior `open`. BUT the retirement STILL
   doesn't land (`\trusted` 8): the internals-blind `dup_of_valid_source_is_valid` needs the
   module-global `_filesystem` CONSTRUCTOR initial state (all fds free) at importer-function
   entry — PyCSL HAVOCS the global at entry, and assuming it blanket is UNSOUND across an
   API-call sequence. So the residual wall is now **module-global-init surfacing** (a
   fresh-instance / per-test constructor-invariant mechanism), not frame propagation. The
   sound frame is banked; the retirement lands once global-init is surfaced. *(os fd
   import-boundary frame fix, 2026-06-18; the UPDATE section of the same gap doc.)*
14. **Module-global constructor state (e.g. fresh-import all-free `fd_open`) is HAVOC'd at
   EVERY importer-function entry — and surfacing it soundly is a `by-construction`, not a
   `requires`, mechanism.** Proof: an `#@ assert (\exists k. fd_open[k]==0)` on the FIRST
   line of a formal test — before any syscall — FAILS; the `let _filesystem = {all-free
   literal}` is only initialization, and Why3 verifies each function with the shared mutable
   global in an arbitrary state. **Diagnostic:** if a chain proves ONLY under a
   `requires`-assumed entry fact (here `requires \forall k. fd_open[k]==0` made
   `dup(dup(open(p)))>=3` prove zero-trust), the residual gap is GLOBAL-INIT SURFACING, not
   frame propagation. **The forbidden move** is shipping that `requires` — it's a blanket
   precondition FALSE in any post-sequence (post-many-opens) context. **The sound route** is
   a NEW tool mechanism (`#@ fresh_globals`-style) that RE-ESTABLISHES the constructor
   post-state BY CONSTRUCTION at a standalone internals-blind driver's entry (sound only
   because such a driver is an independent entry point on the freshly-imported global, never
   inter-called with a pre-mutated one), plus a constructor `#@ ensures` capturing that
   post-state (often absent). High-blast-radius, human-gated. Corollary (audit, for
   `pycsl-audit-pycsl-language`): an UNCONDITIONED no-failure/no-ENFILE ensures over a body
   that routes through a first-free-slot allocator is a **FALSE BODY THEOREM** — the body
   theorem is the free-slot-CONDITIONED form; the unconditioned form is honest only behind a
   trust or a soundly-surfaced entry fact. *(os fd-resolution-fidelity, 2026-06-18:
   `getting-better/20260618-0903-os-fd-import-boundary-frame-gap.md`.)*
   **RESOLVED (2026-06-18, `\trusted` 8→7):** built `#@ fresh_globals` — an opt-in,
   Module4-CONFINED directive that re-establishes a module-global singleton's constructor
   post-state at a standalone driver's entry, sound BY CONSTRUCTION (the assume is the
   constructor's PROVEN `#@ ensures`, re-checked against the literal initializer; Module4
   rejects the directive on methods + callees where it'd be unsound — `PYCSL-SEM-FRESH-GLOBALS`).
   `sys_dup`'s `fd-resolution-fidelity` RETIRED: body+wrapper rewritten to the free-slot-
   CONDITIONED form, `dup_of_valid_source_is_valid` marked `#@ fresh_globals`; body proves
   zero-trust, full suite 18/18, corpus byte-diff 0 (directive corpus-inert), os body 2135 /
   `__init__` 1182. The retirement is SOUND (a false body theorem replaced by a conditioned
   one + a confined proof-backed entry fact), NOT trust relocation. **Still GAP — `sys_open`'s
   `fd-resolution-fidelity`** is a DISTINCT wall: de-trusting leaves 11 unproven goals
   (the `dir_lookup` resolution `<==>` + fd→inode binding non-derivable across the `no_inline`
   opaque name-scan — the dirscan-fidelity class, NOT global-init); needs the dir_lookup
   correspondence folded into a cross-validated predicate (the `block_content_eq` pattern).
   *(`#@ fresh_globals` milestone, 2026-06-18; the first os trust retirement.)*
15. **Per-retirement verification MUST include the full `__init__` TYPECHECK gate — `--fun`
   body gates + byte-diff (`--no-typecheck`) HIDE type errors.** A `--fun` leaf gate typechecks
   only the leaf; the corpus byte-diff sweep runs `--no-typecheck` (emission only). Neither
   catches an emitter type leak that only manifests when the leaf is INLINED into a different
   host context (a string-typed value assigned to an int-typed local in a wrapper). The #53
   `_dir_lookup` faithful-name landing passed every `--fun`+byte-diff check yet left the os
   `__init__` gate RED for three retirements because `pycsl pure_lib/os/__init__.py` (the full
   typecheck) was never re-run. **Rule:** after ANY emitter change touching value lowering, run
   `pycsl pure_lib/os/__init__.py` (which typechecks the WHOLE module, all inline sites) at
   least once per retirement — not just `--fun`/byte-diff. *(faithful-name string-type leak,
   2026-06-20; `getting-better/PROPOSAL-faithful-name-stringtype-fix.patch`.)*

## B. Coherent-and-wrong catalog for formal tests (what the monitor hunts)

| Shape | Tell | How the monitor catches it |
|---|---|---|
| **Self-return assertion** | `#@ ensures \result == 0 or 1` — holds even if the op fails | Gate C non-vacuity seed: break the op, the test must FAIL |
| **Simulation** | the driver mutates the data structure / inlines internals instead of calling the API | API-only audit; the physical barrier prevents it at source |
| **Adjacent-weaker** | proves the byte-COUNT round-trip while claiming the byte-VALUE round-trip (`formal_0008` `back == c` int-vs-array) | clause map: the `ensures` must be the *intended* property, not a weaker cousin |
| **Plane blend** | a `--no-proof` (emission) green reported as "proven" | no-blend: emission ≠ proof |
| **Honorary green** | "the gate is green" from a stale/partial run | re-run on the committed file; scan EVERY status incl. `Out of memory` |
| **Aggregate noise mistaken for a residual** | a goal fails in the full-file gate but proves in `--fun` isolation | re-check residuals per-method before recording them as real |
| **Empty-disk artifact mistaken for a no-trust retirement** | a de-trusted helper's fidelity ensures appears `Valid` in `--fun` isolation, but the property has no logical path from the body (binds an uninterpreted symbol with no defining axiom) | the isolated pass rides the canonical zeroed `by{}` witness, not the body. Triangulate constants (`==0` ✓, `==1` ✓, `==7` ✗ = perf artifact, not logic) AND run the SOUNDNESS PROBE: add a `#@ requires` that forces a non-canonical disk (e.g. `slot_inode(self.dir,5,0)==3`); if the ensures then fails, the isolated pass was the empty-disk artifact. Decisive test is the FULL body gate (real non-canonical `self`) — there it OOMs/reds. NOT a retirement. *(dirscan-fidelity pilot, 2026-06-17.)* |
| **Stale test after a model upgrade** | a committed `formal_*` file FAILS at L3-tc with `int`-vs-`string` type errors, or its header claims a consequence is "UNPROVABLE/Unknown" that now proves | the model gained str-typed path params / `dir_lookup` consequence ensures since the test was written; RUN it, fix the param types, and rewrite the stale header to the now-passing reality (don't trust the comment) |
| **Context pollution mis-blamed on a missing contract** | a theorem is `Unknown` in-module but the author "fixes" it by weakening or adding a contract | re-prove the goal ALONE; if it passes in isolation the contract is fine — split the file instead (pattern A.7) |
| **Partial-codec-rung mistaken for a trust retirement** | a new (even cross-validated) byte/string codec axiom makes ONE sub-ensures of a `\trusted` method prove in `--fun`, reported as "the trust is retired" | a `\trusted reviewer` covers the WHOLE method — enumerate every clause: a VALUE ensures may now prove while the `\forall k!=slot` FRAME + `uniq`/`slots_lt32` class-invariant ensures still EXPLODE (Type-invariant Timeout, millions of steps) the moment the body materializes concrete byte terms. A trust is all-or-nothing per method; retirement requires EVERY clause body-proven AND both gates green. Run the FULL method gate, not just the rung. *(slot_inode byte-codec keystone, 2026-06-17.)* |
| **Banked keystone whose narrow trigger never fires on the real body** | a byte-decode axiom keyed `[disk[blk*512+32*k]]` is merged + cross-validated and assumed "ready", but the mutator body indexes through a let-bound ref (`self.dir[!entry_offset]`) so the trigger never E-matches and the ensures still Times-out (8.5M steps) even with the byte VALUES available | a deliberately-narrow byte-keyed trigger (the safety that prevents the GLOBAL `slot_inode`-atom explosion) is exactly what stops it firing at a mutator that abstracts the index behind a variable. Verify firing by inspecting the emitted `.mlw` (does the literal `disk[blk*512+32*k]` term appear at the assert?), not by assuming "the keystone is banked, so it applies". Closing it requires literal-index restructuring OR a `slot_inode`-keyed bridge (a human-gated TCB axiom) OR Why3 normalization — NOT autonomous. *(dirscan write-side pilot `_write_dir_entry`, 2026-06-17.)* |
| **Keystone axiom asserted but never CITED → silently absent from the `.mlw`** | a de-trust pilot adds body asserts matching a keystone's conclusion, sees `Unknown`, and concludes "the trigger doesn't fire / the keystone is too weak" — when in fact the keystone **is not even in the emitted module** | keystone axioms are **emission-gated by `#@ proof` citation**: a helper that asserts the conclusion but does not also `#@ proof rocq/lean <Axiom>` gets `Unknown` because the axiom was never emitted. This is DISTINCT from (and was the real cause beneath) the "trigger never fires" row — the prior write-side run mis-diagnosed an *absent* axiom as a *non-matching* one. Verify by grepping the emitted `.mlw` for the axiom NAME before reasoning about its trigger. With the cite added AND a literal-offset blit, the inode half of `_write_dir_entry` discharges zero-trust (slot_inode Postcond + frame + all `uniq`/`slots_lt32` Type-invariants Valid; body 8→6 goals, baseline 3). *(dir_lookup-correspondence pilot, 2026-06-18; `getting-better/20260617-1240-dirscan-write-keystone-trigger-gap.md` UPDATE.)* |
| **Opaque-offset blit helper proves its bytes but the round-trip antecedent never reaches the caller (method-call contract gap)** | the "keep the string axiom out of the loop" structural lesson is applied — a byte-only helper with opaque `off` and PURE-byte ensures — yet the caller's decode-site `field_to_str(...)==name` assert still OOMs, as if the round-trip didn't fire | the helper's self-field-referencing quantified byte ensures (`self.dir[off+i]==ord(name[i])`) are DROPPED across the method-call boundary when the helper lowers to an abstract `val` (the field-referencing-ensures propagation gap) — so the round-trip's antecedent never arrives. **FIX: `#@ sibling_concrete`** on the helper inlines its REAL verified byte semantics at the call site; the antecedent is then concrete and BOTH string axioms (bridge + round-trip) fire ONCE, O(1). Measured: with `sibling_concrete` the slot_name VALUE Postcondition `slot_name(self.dir,5,slot)==name` and the `field_to_str(...)==name` assert go from OOM to **Valid (~50K / 48K steps)** — the ~23M-step string wall is GONE. The structural lesson is NECESSARY but not sufficient; `sibling_concrete` is the missing half for a write helper that mutates a self-field. *(slot_name Postcondition close, 2026-06-18; `getting-better/20260618-1640-slot-name-postcondition-closed-frame-residual.md`.)* |
| **The slot-locality FRAME (`∀k≠slot. decode unchanged`) is NOT zero-TCB-definitional — it needs a NEW byte-region frame axiom (the disjoint-region twin of the RETIRED `block5_decode_frame`)** | the goal-#2 doc hoped the slot_name/slot_inode `∀k≠slot` frame would be "definitional, no human gate" (derivable by unfolding the decode over disjoint byte regions) | in WhyML `slot_name`/`slot_inode` are ABSTRACT `val function`s — NO body to unfold — so the frame can ONLY come from an EMITTED byte-keyed axiom. The retired `block5_decode_frame` requires FULL block-5 agreement, which a blit BREAKS (slot's bytes change). The missing fact is `field_to_str_frame`: byte agreement on `[off,off+width)` ⟹ `field_to_str` equal; composed with `slot_name_byte_decode` it gives the `∀k≠slot` slot_name frame (disjoint windows). **Authored + cross-validated this run, zero-TCB BOTH provers** (Rocq Closed under global context, Section-Variables-only; Lean `[propext,Quot.sound]`); corpus-INERT (os `.mlw` byte-identical present-but-uncited). DECISIVE measure on de-trusted `_zero_entry`: slot_name FRAME **OOM → Valid (42K steps)**, and the Type-invariant explosion **150M-step Timeout → fast-Unknown** once the entry_offset is written as `block_num*512+32*slot` (trigger-aligned). It is a NEW axiom = a **human-gated TCB decision** (doctrine option (b)), NOT autonomous — but it is the BANKED rung-1 of the dirscan write-side retirement, and it defuses the (3c) "keystone poisons every mutator's invariant VC" wall. **LANDED 2026-06-18 (rung-1 banked, permanent, in-tree):** registry entry `_AXIOM_REGISTRY["UnixFs.Field.field_to_str_frame"]` (emission-gated, UNCITED ⇒ corpus byte-diff **0/shared**, inert) + exhibit `0714.py` + persisted `0714.proofs/{rocq,lean}/FieldToStrFrame.{v,lean}` (Rocq Section-Variables-only / closed under global context; Lean `[propext,Quot.sound]`); 0714 verifies SUCCESS. **Z3 divergence (NEW):** Z3 cannot APPLY the nested-∀ frame antecedent (Alt-Ergo: Valid 20 steps; Z3: Unknown 17627) — because `why3 prove -P A -P B` reported the LAST `-P`, a default-pipeline goal needing this axiom FAILED; 0714 previously pinned `# pycsl-flags: -p alt-ergo`. **RESOLVED 2026-06-18 by the per-goal best-of-N prover dispatch (§0):** the default pipeline now accepts a goal Valid by ANY prover, so 0714 verifies SUCCESS with the pin REMOVED, and the future `_write_dir_entry` citation site no longer needs an Alt-Ergo pin. *(goal #3 frame, 2026-06-18; `getting-better/20260618-2030-...md` + `getting-better/20260618-1710-field-to-str-frame-z3-cannot-apply-nested-forall-frame.md`.)* |
| **Materializing a byte VALUE term to fire a keystone RE-triggers the explosion (the byte term and the slot atoms cannot coexist)** | with the frame solved, the residual `slot_inode(slot)==0` VALUE postcondition is fast-Unknown; the instinct is to add a post-loop `#@ assert self.dir[entry_offset]==0` or split the inode bytes out of the folded loop invariant to feed the keystone trigger | BOTH REGRESS hard (22–28M-step Timeout, and the previously-Valid frames go Timeout too): the moment a literal `self.dir[entry_offset]` byte term is in scope alongside the abstract slot/uniq/slots_lt32 web, the E-matching storms. KEEP the byte facts FOLDED (`∀j. self.dir[entry_offset+j]=0`). The invariant-maintenance goals (`zero_preserves_*`, already cross-validated + cited) are DOWNSTREAM of this VALUE decode (they need `slot_inode d1 5 slot=0` as antecedent) — so (3b) is not a missing lemma but a starved one. The doctrine-clean close is a SINGLE folded `zero_preserves_dir_invariant`/`insert_preserves_dir_invariant` that takes the byte rung as a folded hypothesis and concludes the value + frame + uniq + slots_lt32 in one step (byte rung discharged offline), so no byte term ever shares a body VC with a slot atom — a NEW human-gated cross-validated axiom. *(goal #3 value/invariant, 2026-06-18.)* |
| **The folded byte-rung maintenance axiom is CORRECT logic but its byte-keyed trigger POISONS sibling byte mutators (fold moves the coexistence from the body assert to the emitted-axiom instantiation, not eliminating it)** | the doctrine-prescribed close is authored: a folded `insert/zero_preserves_dir_invariant_blit` keyed on the blitted byte `[d1[2560+32*s]]`, taking PURE-BYTE hypotheses (blitted inode bytes + byte-region frame + freshness) and concluding value+frame+uniq+slots_lt32 in one step, byte→slot rung discharged offline. CROSS-VALIDATED zero-TCB BOTH provers (Rocq Section-Variables-only; Lean `[propext,Quot.sound]`). The expectation: "no byte term and no slot atom coexist in a body VC." | The fold AVOIDS the *abstract-symbol* trigger but its BYTE key `[d1[2560+32*s]]` matches the SHAPE `disk[2560+<expr>]` — exactly the index EVERY block-5 byte-blit produces. So the axiom fires INSIDE the `#@ sibling_concrete` byte helper `_blit_dir_entry` (whose ensures are PURE BYTES, no slot atoms), instantiating its four-way slot-web conclusion into the helper's byte VC: `_blit_dir_entry` Postcondition goes from clean to **Timeout 869,354,004 steps / OOM**, and `_write_dir_entry` Postcondition OOMs (the slot_name VALUE still needs the round-trip materialized to bridge the freshness `requires` to the axiom antecedent). De-trust drops `\trusted` 7→6 SYNTACTICALLY but the body REDS the gate (2–3 baseline → 3 with 2 NEW explosive goals) = REGRESSION, NOT a retirement. The cross-validated axiom is BANKED (eligible); the remaining engineering is making the WhyML trigger fire EXACTLY ONCE at the genuine apply site (a unique marker atom à la gap-17 `block_content_eq`, OR keep the byte helper a clean abstract `val`, OR split the module so the helper and the cited mutators don't share a preamble) — each a human TCB/tooling decision, NOT autonomous, NOT a `\trusted`. *(\write_dir_entry 7→6 retirement attempt, 2026-06-18; getting-better/20260618-2350-write-dir-entry-7to6-retirement-proposal.md + PROPOSAL-write-dir-entry-detrust.patch.)* |
| **The unique-marker-atom (gap-17 `block_content_eq` discipline) ELIMINATES the trigger-poison — but the de-trust then hits an A.7 aggregate-context wall at the GENUINE apply site (the marker-discharge proves in `--fun` but OOMs in the full module)** | route 1: replace the byte-keyed trigger `[d1[2560+32*s]]` with a UNIQUE uninterpreted predicate `dir_blit_marker d0 d1 s b0 b1 name` (declared in `_AXIOM_FUNCTIONS`, intro+insert keyed `[dir_blit_marker ...]`). Crucially, FOLD BOTH slot VALUE decodes (inode AND name) into the marker conclusion so `_write_dir_entry` cites ONLY the marker axioms and DROPS the `slot_inode_byte_decode`/`slot_name_byte_decode`/`field_to_str_round_trip` cites (those key on the generic `disk[blk*512+32*k]`/`field_to_str` shape, so citing them emits them module-wide and they explode ANY sibling byte loop). Rewrite the byte helper to write the dirent DIRECTLY (2 inode bytes + one 30-byte name loop), not via `_pad_name`+`_pack_direntry`+`Array.blit` (that 3-stage transform explodes the per-byte name ensures regardless). | The marker fires EXACTLY ONCE at the asserted atom — `_blit_dir_entry` goes from **Timeout 8.6e9 steps → SUCCESS**, the poison is GONE and does NOT relocate. `_write_dir_entry` PROVES in `--fun` (REAL: falsification = wrong-slot blit reds it; soundness probe `requires slot_inode(self.dir,5,0)==3` still greens it ⇒ not an empty-disk artifact). The marker intro/insert are CROSS-VALIDATED zero-TCB (Rocq Section-Variables-only; Lean intro=no axioms, insert=`[propext,Quot.sound]`; `name` modelled as char-code list, same as `field_to_str_round_trip`). **BUT the FULL body gate STILL reds** (baseline 2 → 3, +1 new): `_write_dir_entry`'s marker-discharge OOMs/Timeouts (5.46M steps) in the full module — the os axiom web (scan_reflects_present/remove_*/dir_lookup_frame/establish_*) starves its step budget. Pinning the conclusion with explicit asserts just relocates Postcondition→Assertion (same 3 goals). This is **catalog-B pattern A.7 aggregate-context pollution at the genuine site**, NOT trigger-poison/vacuity/logic-gap. The doctrine-clean follow-on is a MODULE SPLIT (verify the dir mutators against a smaller axiom set) or Why3 trigger/weight tuning — high blast radius, human-gated, NOT a `\trusted`. The marker is BANKED (eligible). *(\write_dir_entry 7→6 route 1, 2026-06-19; getting-better/20260619-0130-write-dir-entry-7to6-route1-gap.md + PROPOSAL-write-dir-entry-detrust-v2.patch; proofs 0716.proofs/{rocq,lean}/DirBlitMarker.{v,lean} inside the patch.)* |
| **The "A.7 too-many-axioms-in-scope" diagnosis is REFUTED for `_write_dir_entry`: the axiom scope at the failing VC is byte-IDENTICAL between `--fun` (proves) and the full file (OOMs); the real driver is the full-module PROGRAM APPARATUS, and axiom narrowing does NOT close the two frame postconditions** | the module-split mission assumed the wall was the cited dir axioms (scan_reflects_present/remove_*/dir_lookup_frame) in scope at `_write_dir_entry`. DIRECT measurement: emit full vs `--fun` and `diff` the axioms (15 = 15, identical names), the predicate/function decls (identical), and the `_write_dir_entry` `let` body (byte-identical). `--fun` differs ONLY by trusting every sibling (emit as `val`), which removes the abstract self-call-stub apparatus (`self__dir_lookup_2`/`self__dir_find_slot_2`/… — 17 of them, all referencing slot_inode/slot_name/dir_lookup) and the 60 sibling `let` bodies. | The two `∀k≠slot. slot_inode self.dir 5 k == \old(...)` frame postconditions OOM/Timeout in EVERY full-module configuration tested: all 15 axioms (Z3 OOM 8.86s / Alt-Ergo Timeout 329247–452958); narrowed to 11 (drop the 4 read-side dir axioms) — STILL fail (Z3 Unknown 376826 / OOM; AE Timeout); narrowed to 9 (also drop establish_uniq/slots_lt32) — STILL fail; helper as abstract `val` not `sibling_concrete`-inlined — STILL fail (Z3 OOM / 11.8M; AE Timeout); self-call-stub ensures stripped — STILL fail identically. They prove ONLY under `--fun` (every sibling trusted, ZERO self-stubs; ~48K steps each). So the frames are at the SMT feasibility edge and tip into OOM in the presence of the program apparatus, INDEPENDENT of the `#@ proof` axiom set. The doctrine-clean close is a PyCSL **scope/module emission** feature (none exists today — the emitter produces one flat `module PyCSL_Program`) reproducing the `--fun`-lean context for `_write_dir_entry` via a SOUND Why3 `scope` boundary. Why3 scope axiom-isolation VERIFIED sound (two sibling scopes with contradictory axioms each prove their own goal in isolation; cross-scope call typechecks) — but it is a substantial, high-blast-radius emitter feature and the lean context must be ~`--fun`-aggressive, so it is a human architecture + TCB decision, NOT autonomous, NOT a `\trusted`. Generalisable diagnostic: before blaming "axioms in scope," `diff` the full-emission vs `--fun` axiom set; if identical, the wall is apparatus-context feasibility, and narrowing axioms will NOT help — only a scope that prunes the program apparatus will. *(\write_dir_entry 7→6 module-split, 2026-06-19; getting-better/20260619-0905-write-dir-entry-7to6-modulesplit-GAP.md.)* |
| **A `--fun` (or trusted-`val`) "proves" can be VACUOUS in a branch where an opaque in-place mutator collapses `\old(self.f)` and `self.f` to one SMT term** | a de-trust whose helper is an opaque `val` mutating a `mutable` field in place (no `writes`/fresh-array reframing in the emitted `.mlw`) — its `--fun` Valid was accepted because the soundness probe (non-canonical disk) and a same-property falsification both passed | in the post-state VC `\old(self.dir)` and `self.dir` both lower to `(dir self)`, so any predicate keyed on both states (here `dir_blit_marker d0 d1 ...`) DEGENERATES to `d0=d1`; an over-strong all-`k` antecedent (freshness) then contradicts the value conclusion at the mutated slot (`slot_name≠name` vs `slot_name=name`) → the branch context is INCONSISTENT → its postconditions prove vacuously. The standard soundness/falsification probes MISS it (E-matching is goal-directed). DIAGNOSTIC: add a guarded `#@ ensures <branch-guard> ==> 1 == 0`; if it proves **Valid**, that branch is inconsistent and everything there is vacuous; localize with the guarded-`->false` at intermediate asserts; read the Alt-Ergo Tableaux unsat core for the culprit atom. FIX: narrow the over-strong antecedent to exclude the mutated slot (`k <> s`) in BOTH the axiom and the function's `requires` — sound iff the kernel proof only ever used it at `k<>s` (same theorem, unused premise dropped); re-cross-validate. Found in ALREADY-BANKED route-1 substrate (v2 patch); repaired in v3. *(route-1 vacuity repair, 2026-06-19; getting-better/20260619-1130-route1-vacuity-repair-SUCCESS.md + PROPOSAL-write-dir-entry-detrust-v3-vacuity-repaired.patch.)* |

## C. Per-module coverage ledger

### os (`pure_lib/os/`) — as of 2026-06-17 (re-measured ground truth)
- **Body gate (authoritative, full file):** **2016 Valid / 8 residual** (grep count;
  the 8 = 5 UNIQUE non-Valid + 3 summary echoes). Unique residuals re-confirmed
  2026-06-17 (PYTHONHASHSEED=0, Alt-Ergo 2.6.2 / Z3 4.13.3, load ~2-5): `_unpack_direntry`
  ×2 (Unknown 320459/337358), `_now` ×1 (Out of memory), `sys_rename` ×2 (Timeout
  4621194 + Out of memory). `sys_write` proved this run (the historical "×3 aggregate
  noise" was absent — aggregate noise is non-deterministic; re-measure, don't trust a
  stale count). **0 `\trusted`.**
- **`__init__` gate:** **1159/0 GREEN, SUCCESS, exit 0** — WITNESSED clean 2026-06-17
  on the committed working tree (no edits to `__init__.py` or `UnixInodeFileSystem.py`
  survived; the WIN-1 experiment was reverted before this run).
- **`_unpack_direntry` residual — diagnosed CONFIRMED, the prescribed cheap fix does
  NOT close it (it RELOCATES).** Root cause: `_unpack_uint16_be` is emitted as a `let
  function` (NOT inlined) carrying `requires 0<=data[offset..+1]<=255`; `_unpack_direntry`
  calls it with only `\valid(data,32)`, so the 2 byte-range preconditions can't
  discharge. Adding the minimal 2-clause `#@ requires 0<=data[0..1]<=255` to
  `_unpack_direntry` makes the LEAF prove (Valid 2016→2018) but moves the SAME Unknown
  (fingerprints 381631/304712) to its sole caller `_read_directory`, which reads
  `self.disk[entry_offset:+32]` (block 5, offset≥2560) and has NO byte-range fact:
  the only disk byte-range predicate `inode_bytes_valid` covers ONLY `[512,2560)` (the
  inode table), per `src/pycsl/module6_whyml/preamble.py:551-557`. The directory region
  `[2560,3072)` is unconstrained. Net residual stays 8 + an unmet caller obligation →
  strictly worse → REVERTED. **This is a LOGGED GAP**, not "fix found / deferred": the
  faithful close needs a directory-region (or whole-disk) byte-range predicate
  established in the constructor and maintained by every disk mutator — a substantial,
  `__init__`-gate-risky model extension, NOT a cheap win. See
  `getting-better/20260617-0909-direntry-byte-range-gap.md`. The prior
  `bugs-to-report/20260616-1929-noinline-leaf-not-val-in-importer.md` is SUPERSEDED
  (the blocker is byte-range, not `no_inline` re-verification; the 2-clause version
  fails at the BODY gate before reaching `__init__`).
- **Proven formal tests:** `formal_os_roundtrip` (18/18, totality), `formal_os_content`
  (48/0, on-fd write→pread==data content round-trip), plus the topical
  `formal_os_*` family. As of 2026-06-16 (test-supervise-sl os mission) ALL 19
  `formal_os_*.py` files prove SUCCESS / 0 non-Valid / 0 `\trusted`, each
  re-confirmed non-vacuous from the supervisor's disjoint base (seeded
  falsification flips to FAILED). Every public `os.*` symbol in `__init__.py` has
  a proven consequence (not return-code-only) EXCEPT `walk` (yields, geometry
  only) and the pure stubs (chflags/confstr/copy_file_range/getxattr/listxattr/
  kill/islink — total constants by spec) and chmod/truncate (return-code only;
  no mode/size accessor — model gap, below).
- **Leaf-first extensions this session (zero new trust, body-faithful):**
  `sys_close` gained `\result==0 ⇒ fd_open[fd]==0` (close post-state); `sys_fstat`
  gained the EBADF twin `fd_open[fd]==0 ⇒ \result==-1`; `sys_lseek` gained the
  SEEK_SET consequence `whence==0 ∧ offset≥0 ∧ open ⇒ \result==offset ∧
  fd_offset[fd]==offset`. Propagated to the public `close`/`fstat`/`lseek`
  wrappers. New tests: `formal_os_close` (close→fstat==EBADF) and `formal_os_lseek`
  (lseek SET returns pos). Body gate failing-goal set UNCHANGED by these edits
  (same step-count fingerprints: 320459/337358/4621194) → no regression.
- **Barrier-integrity cleanup (2026-06-17):** `formal_os_io.py` was a barrier
  violation AND a bundle of vacuous self-return assertions — it constructed
  `UnixInodeFileSystem` directly and called `sys_dup2/getdents/fsync/ftruncate/creat/
  chown/utimensat` (NONE of which are public `os.*` symbols — only `dup` is), asserting
  only each op's return code. RECLASSIFIED + renamed to `pure_lib_test/internal_os_io.py`
  (functions `internal_os_*`), with a docstring that loudly states (a) it reaches
  internals BY NECESSITY (no public API exists for these ops) and (b) the assertions
  are return-code SAFETY bounds, NOT consequences — so it is explicitly NOT in the
  public `formal_os_*` family. Still SUCCESS / 0 non-Valid / 0 `\trusted`. LESSON:
  when an op has no public API, an honestly-labeled internal smoke test is the
  doctrine-compliant home — never a `formal_os_*`-named return-code-only "consequence"
  test (that is the self-return vacuity shape masquerading as coverage).
- **Open frontiers (logged gaps, not failures):** reopen-by-name content/size
  round-trip (write count is `<=` not `==`; reopened size unpinned through
  reopen-by-name) — the on-FD round-trip IS proven (`formal_os_content`);
  open(absent,O_RDONLY)==-1 with absence NOT pre-established (a never-created
  name's `dir_lookup` is havoc'd — provable only WITH an established absence, as
  in `formal_os_enoent` after mkdir→rmdir); **chmod mode-reflected / truncate
  size==length — LOGGED GAP, NOT a cheap win** (probed 2026-06-17): no public
  mode/size accessor (`sys_stat` returns only the inode NUMBER), no `inode_mode`
  logic accessor, no MODE-field round-trip ensures on `_read_inode`/`_write_inode`
  (only field 0=size and field 8=block have read-back ensures); closing it is a
  multi-rung extension (accessor + codec round-trip rung + sys_* consequence ensures
  across `no_inline` + NEW public observer API + `__init__` wrapper plumbing + the
  formal test). See `getting-better/20260617-0914-chmod-truncate-consequence-gap.md`;
  multi-block content; `sys_rename` no-trust closure — **a LOGGED GAP, not a trust
  candidate**: the only doctrine-compliant routes are a different prover / a
  restructured proof / composing its already-cross-validated lemmas in-context; the
  ready reviewer-trusted `_rename_swap` is OFF THE MENU (see the BINDING rule above).
- **`dirscan-fidelity` ×6 TCB debt — RETIREMENT IS SMT-INFEASIBLE, a structural wall
  (probed 2026-06-17; net TCB delta 0, 6→6, nothing retired/weakened).** The 6
  `#@ \trusted reviewer: dirscan-fidelity` directives (`_dir_lookup`, `_dir_find_slot`,
  `_dir_find_free`, `_write_dir_entry`, `_write_entry`, `_zero_entry`) bind their byte-
  scan body to the abstract symbols `slot_inode`/`slot_name`/`dir_lookup`, declared as
  **uninterpreted `val function`** (`preamble.py:771-774`). NO axiom DEFINES them over
  the concrete bytes (`preamble.py` slot_inode axioms 123-575 are all RELATIONAL:
  presence⇔existential, frame, uniqueness, nonneg, all-dead-on-zeroed). So the bodies
  have no logical path to the fidelity ensures. **Route (a) blocked:** the
  `UnixDirScan{,Absent}` Rocq/Lean lemmas prove the scan STRUCTURE for an ABSTRACT
  decode (`UnixDirScan.v:27-33` `Variable slot_inode`) — they deliberately abstract the
  byte↔slot bridge away; the bridge itself is unprovable even in a kernel because the
  name byte-CONTENT is opaque (Gap 5, unmodeled). **Route (b) blocked:** de-trusting
  `_dir_find_free` → its postcondition OOMs in the FULL body gate (the `--fun` "Valid"
  was an empty-disk artifact — see the catalog row; soundness probe
  `requires slot_inode(self.dir,5,0)==3` flips it to FAIL); de-trusting `_write_entry`
  → Unknown/Timeout/OOM even in `--fun`. All six share the identical wall (same three
  symbols, same missing bridge). Per the HARD CONSTRAINT, removing a `\trusted` that
  reds a gate is a REGRESSION, not a retirement → directives STAY, logged GAP routed to
  the human. The real close = a concrete byte-decode definitional axiom for the three
  symbols, cross-validated Rocq+Lean — blocked TODAY by Gap 5 (name bytes unmodeled);
  a substantial model extension, human-gated. See
  `getting-better/20260617-1001-dirscan-fidelity-structural-wall.md`.
  - **KEYSTONE UPDATE 2026-06-17 (Gap-5 byte codec LANDED as a primitive; still net TCB 0,
    8→8 on the os).** The inode-FIELD byte→decode is now a cross-validated axiom
    `UnixFs.Dir.slot_inode_byte_decode` (preamble `_AXIOM_REGISTRY`; proofs
    `0711.proofs/{rocq,lean}/SlotInodeByteDecode.{v,lean}` — Rocq Closed under global
    context, Lean depends on NO axioms; exhibited+proven SUCCESS in corpus `0711.py`,
    ≤33k steps; byte-keyed trigger `[disk[blk*512+32*k]]` so it NEVER fires on the
    abstract `slot_inode` atoms; corpus byte-diff 0/601, both gates green). It is
    NECESSARY but NOT SUFFICIENT to retire a write-side trust: a `\trusted reviewer:
    dirscan-fidelity` bundles THREE obligations — (i) inode-VALUE `slot_inode==inode_num`
    (now byte-codec PROVABLE, Valid in `--fun`); (ii) name-VALUE `slot_name==name` (needs
    the `field_to_str` STRING codec, the ~23M-step E-match wall); (iii) the `\forall k!=slot`
    FRAME + `uniq`/`slots_lt32` class-invariant maintenance over the ABSTRACT symbol — and
    (iii) **EXPLODES** the moment the body materializes concrete `disk[...]` byte terms
    (Type-invariant Timeout 9.05M steps, measured), because the byte-keyed decode axiom and
    the `slot_inode`-keyed uniq/slots_lt32 axioms then coexist over the same disk. A
    `\trusted` is all-or-nothing per method, so the value half proving while the
    invariant half explodes ⇒ trust STAYS. The real remaining wall is therefore NOT
    "no byte decode" (it now exists) but **invariant-maintenance E-matching surviving
    byte materialization** + the string codec. See
    `getting-better/20260617-1039-slot-inode-byte-codec-keystone.md`.
  - **KEYSTONE UPDATE 2026-06-17 (Gap-5 STRING half LANDED as a primitive; net TCB still 0
    new on the os).** The name-FIELD byte→decode now exists too, as a cross-validated BRIDGE
    axiom `UnixFs.Dir.slot_name_byte_decode` (preamble `_AXIOM_REGISTRY`; proofs
    `0712.proofs/{rocq,lean}/SlotNameByteDecode.{v,lean}` — Rocq Closed under the global
    context, Lean depends ONLY on {propext, Quot.sound}; exhibited+proven SUCCESS in corpus
    `0712.py`, 24 Valid / 0 non-Valid; corpus byte-diff 0/shared, both gates byte-identical).
    The bridge states `slot_name disk blk k = field_to_str disk (blk*512+32*k+2) 30` (a
    32-byte `'>H30s'` slot = 2-byte inode + 30-byte name, so the name field starts at +2),
    byte-keyed on `[disk[blk*512+32*k+2]]` (the FIRST name-field byte) so it NEVER fires on
    abstract `slot_name` atoms; composing it with the already-merged `field_to_str_round_trip`
    gives the write-side `slot_name == name`. This RESOLVES obligation (ii) of the
    dirscan-fidelity bundle as a *banked primitive* — but it is STILL NOT a trust retirement:
    obligation (iii) (invariant-maintenance E-matching over the abstract symbol surviving
    byte materialization) remains the wall, exactly as for the inode half. Net: both VALUE
    halves (inode + name) are now byte-codec PROVABLE; the FRAME/invariant half is the open
    keystone for Step 2.
  - **STRUCTURAL LESSON (Gate-S PASS, slot_name string keystone, 2026-06-17): keep the
    string axiom OUT of the byte-blit loop.** The string round-trip itself crosses SMT in
    O(1) when its byte hypotheses are *given* (a probe with the per-byte facts as `requires`
    proved `slot_name == name` in ~20k steps — the round-trip + bridge APPLY fast). The
    ~23M-step E-match explosion is NOT the decode; it is the byte-keyed decode trigger firing
    *per loop iteration* inside the encode loop (the loop writes `disk[off+i]` where
    `off = blk*512+32*k+2`, so the trigger term `disk[blk*512+32*k+2]` materializes every
    iteration and drags `field_to_str`/string reasoning into pure-byte loop-invariant goals).
    FIX: factor the blit into a byte-ONLY helper whose contract names no `slot_name`/
    `field_to_str` and whose field offset is an OPAQUE parameter `off` (so the trigger pattern
    cannot syntactically match per-iteration); let the string axioms fire EXACTLY ONCE at the
    decode site in the caller, with the byte facts already in hand. This is the general
    discipline for any byte-keyed codec axiom used by a write helper: opaque-offset blit
    helper + single decode-site application. Trigger-tested: with the inline loop both the
    null-tail invariant and the postcondition Timeout at 5–9M steps; after factoring, the
    whole exhibit is 24/24 Valid.
  - **WRITE-SIDE PILOT 2026-06-17 (`_write_dir_entry`, net TCB 0, 8→8, working tree
    byte-identical to HEAD after revert).** De-trusting the simplest dir mutator and
    running `--fun unixinodefilesystem___write_dir_entry` pins obligation (iii) to a
    SHARPER root than "byte-materialization E-matching": **(1)** the leaf pack helpers
    DISCARD byte VALUES — `_pack_uint16_be` had NO contract; `_pack_direntry` ensured only
    `\length==32`. With value ensures added (`_pack_uint16_be`: `\result[0]*256+\result[1]==v`;
    `_pack_direntry`: `\result[0]*256+\result[1]==inode_num`, `\forall i<30. \result[i+2]==name_bytes[i]`)
    — both `--fun` SUCCESS — the slot_name Postcondition explosion drops **68M → 1.5M steps**.
    This is the genuinely-missing FOUNDATION (pattern A.3, leaf-first), proven and bankable.
    **(2)** Even then the keystone STILL does not fire: the body indexes via a let-bound ref
    `self.dir[!entry_offset]` (`entry_offset := block_num*512 + slot*32`), and the keystone
    trigger `[disk[blk*512+32*k]]` does not E-match the deref (and `slot*32` ≠ `32*k`
    syntactically). The `slot_inode==inode_num` assert Times-out at 8.5M with the keystone
    never applied (confirmed by reading the emitted `.mlw`). This is the DUAL of the
    opaque-offset discipline above: an opaque/let-bound offset that keeps the trigger from
    firing *per-iteration in the loop* ALSO keeps it from firing *at the decode site where
    you WANT it*. Closing it needs literal-index restructuring of the blit (`block_num*512 +
    32*slot`, no ref) OR a `slot_inode`-keyed bridge (human-gated TCB) OR Why3 trigger
    normalization. Per doctrine the de-trust reds the gate (5→7 goals) → REGRESSION →
    reverted → logged GAP. See
    `getting-better/20260617-1240-dirscan-write-keystone-trigger-gap.md`. New catalog
    row B: "Banked keystone whose narrow trigger never fires on the real body".
  - **WRITE-SIDE PILOT 2026-06-18 (`_write_dir_entry`, dir_lookup-correspondence run;
    net TCB 0, 7→7, tree byte-identical to HEAD; INODE HALF SOLVED).** The 2026-06-17
    pilot above had TWO compounding causes, only one diagnosed. Applying its own step-2
    fix — (a) literal-offset blit `5*512 + 32*slot` (no `!entry_offset` ref, `32*slot`
    aligned) AND (b) **`#@ proof rocq/lean slot_inode_byte_decode` to actually EMIT the
    keystone** (the prior run never cited it, so the axiom was absent from the `.mlw` —
    a cause beyond trigger-shape; new catalog row B "asserted but never CITED") — the
    inode half discharges zero-trust: slot_inode write-side Postcond Valid, slot_inode
    frame Valid, ALL `uniq`/`slots_lt32` Type-invariants Valid. Body (authoritative "N
    goal(s) remain", PYTHONHASHSEED=0): baseline **3** → bare de-trust **8** →
    fix applied **6**. The 3 genuinely-new residual goals — the precisely-relocated
    wall: (1) Precondition `inode_num<65536` (trivial `#@ requires`), (2) slot_name
    Postcond (string-extensionality round-trip wall — needs the per-char chain folded
    behind ONE more cited atom), (3) slot_name slot-locality frame (needs the
    `block5_decode_frame`-class lemma re-emitted; corpus byte-diff territory). NOT
    shipped — the inode half alone leaves the body +3 over baseline = body-gate
    REGRESSION. Campaign target stays 7. See the UPDATE in
    `getting-better/20260617-1240-dirscan-write-keystone-trigger-gap.md`.
  - **WRITE-SIDE PILOT 2026-06-18b (`_write_dir_entry` slot_name Postcondition CLOSED;
    net TCB 0, body 3→8 so NOT shipped; tree byte-identical to HEAD).** Goal (2) of the
    residual trio — the slot_name string-extensionality round-trip wall — is now **closed
    at the method level**, zero-trust, no weakening, no new axiom. Route: factor the name
    blit into an OPAQUE-OFFSET byte-only helper `_blit_name_field` (0712's
    `encode_name_field` shape — the byte-keyed trigger `disk[blk*512+32*k+2]` cannot match
    an opaque `off`, so the loop is a clean byte loop) marked **`#@ sibling_concrete`**, +
    literal-offset inode bytes, + the 3 keystone cites
    (`slot_inode_byte_decode`/`slot_name_byte_decode`/`field_to_str_round_trip`), + the
    round-trip antecedent requires (`\str_length(name)<=30`, no-embedded-null). DECISIVE:
    the structural lesson ALONE is insufficient — the opaque helper hits the **method-call
    contract gap** (self-field-referencing byte ensures don't propagate → OOM at the
    decode site); `#@ sibling_concrete` inlines the real verified semantics so the
    antecedent is concrete and both string axioms fire ONCE, O(1). Measured (`--fun`):
    slot_name Postcond → **Valid (~50K steps)**, `field_to_str(...)==name` assert → Valid
    (48029 steps); the ~23M-step wall is GONE. The ONLY remaining write-side wall is now
    goal (3): the slot_name slot-locality FRAME (`∀k≠slot. slot_name unchanged`, OOM) +
    `uniq`/`slots_lt32` Type-invariant maintenance (Timeout 3.1e9/2.0e8) — AND the
    byte-keystone EMISSION poisons every dir-mutator's invariant VC (`_blit_name_field`
    Type-inv 320K Unknown → 5–6M Timeout once keystones emitted). Doctrine-compliant close
    of (3) = a folded cross-validated invariant-maintenance lemma keyed so no byte term and
    no slot_inode/slot_name term coexist — a NEW cross-validated Rocq+Lean axiom =
    HUMAN-GATED TCB. Reverted; logged GAP. See
    `getting-better/20260618-1640-slot-name-postcondition-closed-frame-residual.md`. New
    catalog row B: "Opaque-offset blit helper proves its bytes but the round-trip antecedent
    never reaches the caller (method-call contract gap)".
  - **WRITE-SIDE PILOT 2026-06-18c (goal #3 frame SOLVED, explosion TAMED; net TCB 0,
    7→7, tree byte-identical to HEAD).** Goal (3a) — the slot_name/slot_inode `∀k≠slot`
    slot-locality FRAME, OOM in every prior run — is now **SOLVED** by a NEW cross-validated
    zero-TCB lemma `field_to_str_frame` (byte agreement on `[off,off+width)` ⟹ `field_to_str`
    equal; the disjoint-region twin of the RETIRED `block5_decode_frame`, which required FULL
    block agreement a blit breaks). Authored + cross-validated this run: Rocq **Closed under
    the global context** (Section-Variables-only), Lean **`[propext, Quot.sound]`**;
    corpus-INERT (os `.mlw` byte-identical present-but-uncited). Probed in isolation on the
    SIMPLEST mutator `_zero_entry` (same frame + uniq/slots_lt32 walls, no string round-trip):
    slot_name FRAME **OOM → Valid (42K steps)**; Type-invariant explosion **150M-step Timeout
    → fast-Unknown** once entry_offset is written `block_num*512+32*slot` (trigger-aligned).
    Goal (3a) hope of "zero-TCB definitional, no human gate" is REFUTED at the WhyML level
    (slot_name/slot_inode are abstract `val function`s — no body to unfold — so ANY frame is
    a NEW emitted byte-keyed axiom = human-gated). RESIDUAL decomposed to a clean dependency
    chain: the ROOT is the `slot_inode(slot)==0` VALUE decode (the ROOT-CAUSE-#2 keystone
    trigger wall — materializing the byte term re-triggers the explosion, 22–28M Timeout), and
    the uniq/slots_lt32 maintenance goals are DOWNSTREAM of it (the cross-validated
    `zero_preserves_*` need its `slot_inode d1 5 slot=0` antecedent). Doctrine-clean finish =
    a folded `zero_preserves_dir_invariant`/`insert_preserves_dir_invariant` (byte rung folded
    behind a cited atom, never coexisting with slot atoms) — a NEW human-gated cross-validated
    axiom. `field_to_str_frame` is the BANKED rung-1 (recommend landing it alone: inert +
    cross-validated). Reverted; logged GAP. See
    `getting-better/20260618-2030-field-to-str-frame-closes-goal3a-decomposed-residual.md`.
    Two new catalog rows B (the frame-axiom-not-definitional finding; the
    byte-term-cannot-coexist-with-slot-atoms finding).

*(Other modules: `re` 16/16 stub-level; `warnings` 18/18 body + 3/3 formal;
`json` 6/6 thin-API. Add ledgers here as missions cover them.)*

---

## D. Outputs the loop files elsewhere

- **`getting-better/`** — ergonomic feature ideas (PyCSL/tooling improvements that
  would make formal tests easier). One concern per `YYYYMMDD-hhmm-name.md`.
- **`bugs-to-report/`** — candidate PyCSL bugs with minimal repro and
  `STATUS: CONFIRMED|UNCONFIRMED`. One per `YYYYMMDD-hhmm-name.md`.

These are *proposals*, not knowledge — they live outside this skill until acted on.
When a bug is fixed or a feature lands, fold the resulting durable lesson back here
(under A/B) via Gate S.
