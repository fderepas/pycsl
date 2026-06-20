# Scope/module-emission Milestone-0 de-risking spike — VERDICT: **YES (with one load-bearing correction to the mechanism)**

**Date:** 2026-06-20 ~06:40
**Worktree:** `.claude/worktrees/agent-a96ae93ac7fb98bf6` (SPIKE — nothing committed; tree reverted to clean HEAD, only the two artifacts kept)
**Artifacts:** `getting-better/SPIKE-scope-emission.mlw` (the hand-built target shape) + this writeup.
**Substrate:** clean HEAD `9a0ce90` + `getting-better/PROPOSAL-dir-lookup-faithful-name-detrust.patch` (the sound read-side de-trust) applied to emit the os `.mlw`.
**Tooling:** Why3 1.8.2, Alt-Ergo 2.6.2, Z3 4.13.3, `PYTHONHASHSEED=0`.

---

## 1. BOTTOM LINE — **YES, axiom-family isolation resolves the read+write co-residence regression.**

Emitting the os helpers so the READ-side (`field_to_str` / `slot_name` / `dir_scan_*`) and
WRITE-side (`dir_blit_marker*`) axiom families are **NOT co-resident in any single goal's
context** makes the regression GO AWAY. In ONE hand-built `.mlw`:

- `_dir_lookup` (read context): **0 non-Valid**, best-of Alt-Ergo+Z3, deterministic ×2.
- `_write_dir_entry` / `_write_entry` / `_zero_entry` (write context): **0 non-Valid**, ×2.
- Plus the record type-invariant goal (`unixinodefilesystem'vc`): **0 non-Valid**.
- **No OOM, no Timeout in the union.** Max load-bearing step count **~435 K** (`_zero_entry`,
  Z3) — i.e. the SAME `_zero_entry` that **Times Out at 9 519 348 steps** in the flat module
  (`--fun` gate path) is **Valid at ≤435 K** once the read axioms are out of its context.
  That is the exact contrast the mission demanded, achieved in one module.

### THE LOAD-BEARING CORRECTION (a clean soundness result the parent MUST act on before the build)

**Why3 1.8.2 `scope` does NOT isolate axioms.** The design proposal (`scope-emission-design-proposal.md` §1/§3) and the prior GAP doc claim "two sibling `scope`s with contradictory axioms each prove in isolation." **That claim is FALSE for plain `scope`.** Decisive probe (`/tmp` throwaways, reproduced twice):

```
module M
  val function f (x:int) : int
  scope A  axiom a_ax: forall x. f x = 1   goal a_g: f 0 = 1   end
  scope B  axiom b_ax: forall x. f x = 2   goal b_false: 1 = 2 end   (* pure falsehood *)
```
→ `b_false : 1 = 2` proves **Valid (0.01s)**. The two scopes' contradictory axioms ARE
co-resident, so `False` is derivable — a `scope` is a NAMESPACE, not an axiom-visibility
boundary. The whole module is one theory; every `axiom` is global from its point of
declaration. (I first built the spike with `scope`s and `_zero_entry` STILL timed out at
9.3 M steps — identical to flat — confirming scopes do not prune the context.)

**Separate top-level `module`s DO isolate.** The same contradiction across two `module`s:
```
module A  ... axiom a_ax: f x = 1  goal a_false: 1 = 2  end
module B  ... axiom b_ax: f x = 2  goal b_false: 1 = 2  end
```
→ both `1 = 2` goals return **Unknown (sat)** — each module's axiom set is consistent and
local; the contradiction does NOT leak. This is real isolation.

**Consequence for the feature:** the mechanism that resolves co-residence is **module
emission (a `module` per verification context with re-declared shared infra), NOT `scope`
emission.** The design's soundness argument (proven-contract cross-boundary calls via the
narrowing VC, TCB unchanged) is intact and applies verbatim — only the Why3 construct
changes from `scope` to `module`+(implicit re-decl / `clone`). The "Module6 scope-emission"
build should be a **module-emission** build. Everything else in the proposal stands.

---

## 2. The structure built (how axioms were partitioned; how the boundary was modeled)

`getting-better/SPIKE-scope-emission.mlw` — two top-level modules, shared infra re-declared
in each (so neither sees the other's axioms):

**ReadMod**
- Shared decls: `use`s, `pycsl_div/mod`, the `val function`s (`field_to_str`, `slot_inode`,
  `slot_name`, `dir_lookup`, `bit_*`, str ops), predicates, the `unixinodefilesystem` record
  + its type invariant, the abstract `val self__*` / `val *_op` stubs.
- **Witness axioms hoisted BEFORE the record** (so the type-invariant `by {…}` witness sees
  them): `empty_disk_slots_dead`, `establish_uniq`, `establish_slots_lt32`, `ibv_intro/elim`,
  `block_content_eq_*`. (Matching the flat module's layout, where these precede the type.)
- **Other shared axioms:** `slot_inode_byte_decode`, `slot_inode_nonneg`, `bit_and_one`.
- **READ-only axioms:** `dir_scan_prefix_base/step`, `dir_scan_result_intro/value`,
  `slot_name_byte_decode`, `field_to_str_round_trip`, `scan_reflects_present`,
  `dir_lookup_frame`, `remove_reflects_absent`, `remove_unique_absent`.
- Body: `_dir_lookup`.

**WriteMod**
- Same shared decls + witness axioms + other shared axioms.
- **WRITE-only axioms:** `dir_blit_marker_at_{frame_only,intro,value_inode,value_name}`,
  `dir_blit_marker_{frame_only,insert,intro,intro_zero,value_inode}`.
- **Cross-module boundary:** `_blit_dir_entry` and `_blit_disk_entry` as **bodyless `val`s**
  carrying their contracts (copied verbatim from the flat emission, where they are real
  `let`s that discharge those contracts).
- Bodies: `_write_dir_entry`, `_write_entry`, `_zero_entry`.

The toxic terms are gone from where they don't belong: WriteMod has **no** `field_to_str_round_trip`
/ `slot_name_byte_decode` / `dir_scan_prefix_step` (the axioms whose auto-triggers E-match the
write helpers' per-byte array accesses), and ReadMod has **no** `dir_blit_marker*`.

### Boundary soundness — FLAGGED honestly
The blit `val`s **assume** their contract in this spike (a trust, to model the boundary — the
mission explicitly permits `val`-with-proven-contract for Milestone-0). In the real build this
MUST be a **PROVEN interface**: `_blit_dir_entry`/`_blit_disk_entry` are emitted as real `let`s
in their own module and discharge those contracts, and the narrowing VC proves the consumed
contract follows from the definition (design §4). I did NOT introduce any *new* logical content
at the boundary — the contracts are byte-identical to the flat emission's proven ones.

---

## 3. Scoped(module-split) ×2 evidence vs the flat-module regression baseline

### Flat-module regression baseline (co-resident read+write — reproduced)
`pycsl --fun unixinodefilesystem___zero_entry` on the patched os (read axioms module-wide):
- `_zero_entry` assertion (`self.dir[2560+32·slot+2] = 0`): **Timeout 30 s, 9 519 348 steps**
  (Z3); the gate reports 1 goal unproven → **FAILED**. (Matches the GAP's ~9.8 M.)
- Full body gate: Z3 full-file pass exhausts memory (catastrophic OOM, no summary).

### Module-split spike — per-function cross-prover union (best of Alt-Ergo + Z3)
Run with `why3 prove -a split_vc --timelimit 20`, both provers, **two independent runs**:

| function (target)        | sub-goals | union-Valid | non-Valid | max load-bearing step |
|--------------------------|----------:|------------:|----------:|----------------------:|
| `_dir_lookup`            | 21        | 21          | **0**     | 51 024 (Z3)           |
| `_write_dir_entry`       | 10        | 10          | **0**     | 51 686 (Z3)           |
| `_write_entry`           | 11        | 11          | **0**     | 50 413 (Z3)           |
| `_zero_entry`            | 9         | 9           | **0**     | **435 297 (Z3)**      |
| `unixinodefilesystem'vc` | 42        | 42          | **0**     | 25 558                |

Determinism (×2): the per-prover non-Valid SETS are byte-stable across both runs —
- Z3 non-Valid = `{_write_dir_entry line 412}` (both runs); covered by **Alt-Ergo Valid, 85 steps**.
- Alt-Ergo non-Valid = `{lines 190, 414, 437}` (both runs); each covered by **Z3 Valid, 44–50 K steps**.
- → best-of-both union = **0 non-Valid, identical both runs.**

**The contrast nailed:** `_zero_entry`, which Times Out at 9.5 M steps in the flat module, is
**Valid at ≤435 K steps** in the module-split — a >20× headroom under the wall, no OOM. The
exact functions that regress flat are Valid once isolated, in ONE `.mlw`, read AND write
co-present (as modules) but not co-resident (as contexts).

---

## 4. Scope/module-isolation soundness probe — PASS

Three independent probes:

1. **Synthetic-contradiction probe (the decisive mechanism test).** `scope` siblings with
   `f x=1` / `f x=2`: `1=2` proves **Valid** ⇒ scopes leak. Separate `module`s with the same:
   `1=2` returns **sat/Unknown** ⇒ modules isolate. (This is *why* the spike uses modules.)

2. **Directional axiom-visibility probe on the actual os modsplit.** A goal restating a
   WRITE axiom (`dir_blit_marker → slot_inode = 256·b0+b1`) placed in **ReadMod** (no blit
   axioms): **Timeout 4.8 M steps, NOT Valid.** The same goal in **WriteMod** (has the axiom):
   **Valid 0.03 s / 36 006 steps.** Symmetric for a READ axiom (`dir_scan_result → dir_lookup=r`)
   in WriteMod: **Timeout 5.1 M, NOT Valid**; in ReadMod: **Valid 0.03 s / 31 725 steps.**
   The ~150× blow-up with no Valid verdict proves the cross-module axioms are genuinely out
   of scope.

3. **Consistency probe on the real os axiom set.** `1=2` in each os module: **Timeout, NOT
   Valid** — confirming neither module's local axiom set is inconsistent (the partition does
   not accidentally create or hide a contradiction; the os axioms are mutually consistent,
   which is why probe 3 alone can't distinguish isolation — probes 1+2 do).

Net: a write-context goal does NOT see read axioms and vice-versa, and no module's axiom set
is inconsistent. Isolation is sound.

---

## 5. Caveats / what the parent must re-check before authorizing the L–XL build

1. **Build the MODULE-emission feature, not `scope`-emission.** `scope` is proven NOT to
   isolate axioms in Why3 1.8.2 (§1, §4 probe 1). The proposal's soundness argument is fine;
   only the emitted construct must be `module` (per verification context, shared infra
   re-declared/cloned) instead of `scope`. **Re-run probe 1 to confirm before building.**
2. **The cross-module boundary `val`s are ASSUMED here (a spike trust).** The real build must
   emit each called helper as a real `let` discharging its contract, with the Track-B
   narrowing VC proving the consumed contract — so the net TCB is unchanged (design §4). The
   contracts I used are byte-identical to the flat emission's already-proven ones.
3. **Shared-infra re-declaration cost.** Each module re-declares the type, val-functions,
   predicates, witness axioms, and abstract stubs. This is the leanness lever that works
   (it is what removes the toxic axioms), but the emitter must route axiom selection
   per-module and re-emit shared decls — the medium-high blast radius the proposal flagged.
4. **Type-invariant witness needs the establish/ibv axioms hoisted before the record** in
   each module (I had to do this; without it the witness goes Unknown). The emitter already
   hoists class-invariant axioms (`preamble.py` `_emit_class_inv_axioms`) — that ordering must
   be preserved per-module.
5. **`_dir_lookup` line-959 `slot_name = name` goal:** in this spike it is covered (Z3 within
   `_dir_lookup`'s 51 K-step envelope); confirm it survives the real emitter's exact goal split.

I did NOT build any emitter code (per the spike mandate). I did NOT commit. The verdict is a
clean **YES for the mechanism** (axiom isolation resolves co-residence) with the **mandatory
substitution of `module` for `scope`** as the isolating construct.

---

## 6. Reproduce

```
# from the worktree, on clean HEAD:
git apply getting-better/PROPOSAL-dir-lookup-faithful-name-detrust.patch
PYTHONHASHSEED=0 .venv/bin/python3 src/pycsl/pycsl.py --keep-mlw --no-proof --no-typecheck pure_lib/os/UnixInodeFileSystem.py
# flat regression: pycsl --fun unixinodefilesystem___zero_entry  -> Timeout 9.5M
# the spike target shape (already built):
why3 prove -a split_vc -P "Alt-Ergo,2.6.2" --timelimit 20 getting-better/SPIKE-scope-emission.mlw
why3 prove -a split_vc -P "Z3,4.13.3"      --timelimit 20 getting-better/SPIKE-scope-emission.mlw
# union: 0 non-Valid on the 4 targets + the type goal. Z3-Unknown line412 <- AE 85 steps;
#        AE-Timeout 190/414/437 <- Z3 44-50K steps.
# isolation: the synthetic 1=2 scope-vs-module probe + the directional axiom-visibility probe.
```

---

## PARENT VERIFICATION NOTE (independent)

**Construct correction CONFIRMED by my own probe (decisive):**
- `scope` does NOT isolate axioms: two sibling scopes with `f x=1` / `f x=2` over a
  module-level `f` let `goal 1=2` prove **Valid (6 steps)** — co-resident, a scope is
  just a namespace.
- separate `module`s DO isolate: the same contradictory axioms in modules A/B leave
  `goal 1=2` in B **Unknown** — B sees only its own axiom.
So the feature is **MODULE-emission** (separate top-level Why3 modules), NOT
scope-emission. #38's Why3 construct is corrected; its soundness argument
(proven-contract cross-boundary calls via the narrowing VC, unchanged TCB) is intact.

**Co-residence resolution CONFIRMED:** the hand-built module-split `.mlw` re-ran ×2
with NO OOM (the flat module OOM'd); the `_zero_entry` that Timed Out at ~9.5M steps
flat is union-Valid (≤435K) once isolated. Verified the run completes; agent's
per-function union-Valid ×2 evidence holds.

**Caveat for the build (flagged by the spike, binding):** the cross-module helper
`val`s ASSUME their contract in this Milestone-0 `.mlw` (permitted for the spike). The
real build MUST emit them as real `let`s discharging those contracts via the Track-B
narrowing VC (`_emit_narrowing_vc`, commit b3d65d1) — a PROVEN cross-module interface,
never an assumed `val`/new trust. GREEN only if no new trust is introduced.
