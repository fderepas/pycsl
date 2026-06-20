# Module-emission ASSEMBLY (`_transpile_modular`) for the `_dir_lookup` 4→3 de-trust — VERDICT: **PARTIAL — the 4-module emitter is BUILT and the proven shape is emitted + `'refn'vc` Valid + corpus-inert; but the retirement does NOT land because the project's per-function `--fun` gate path (which trusts `_dir_lookup`) is deliberately NOT split, so the write-side co-residence 9.5M regression REMAINS on that path.**

**Date:** 2026-06-20 ~11:30
**Worktree:** `.claude/worktrees/agent-acfcb36f3676f8607` (STOP-AT-PROPOSAL — nothing committed; tree reverted clean; only the patch + this writeup + the validation `.mlw` remain).
**Patch:** `getting-better/PROPOSAL-module-emission-FINISHED-dir-lookup.patch` (1339 lines, 16 files — foundation + the finished `_transpile_modular` assembly).
**Validation artifact:** `getting-better/VALIDATION-module-emission-os-split.mlw` (the emitter's REAL output: the 4-module split of the real os, 2073 lines — re-emit with `pycsl --no-proof --no-typecheck --keep-mlw pure_lib/os/UnixInodeFileSystem.py`).
**Substrate:** clean HEAD `9ca7922` + `getting-better/PROPOSAL-module-emission-dir-lookup.patch` (the foundation) applied, then `_transpile_modular` implemented.

---

## 1. BOTTOM LINE

The multi-module emitter ASSEMBLY is **finished and produces the proven 4-module shape** — this is real, verifiable progress past the prior PARTIAL (which fail-loud `NotImplementedError`-ed). Independently re-verified by me (parent-style full checks, not the impl agent's self-report):

- **The emitter emits the validated shape.** `pycsl pure_lib/os/UnixInodeFileSystem.py` with `_dir_lookup` tagged `#@ verify_module ReadMod` now emits 4 top-level `module`s: `Shared` / `ReadModSig` / `ReadMod` / `PyCSL_Program` (verified: `grep '^module' …mlw`). Typechecks clean (`why3 prove --type-only` rc=0, benign warnings only).
- **The cross-module boundary is the PROVEN `clone`-refinement, NOT an assumed shim.** `ReadModSig` holds `_dir_lookup`'s contract as a bodyless `val`; `ReadMod` holds the real `let` + the READ axioms LOCALLY + `clone ReadModSig with val unixinodefilesystem___dir_lookup = unixinodefilesystem___dir_lookup`; `PyCSL_Program`'s 17 syscall consumers call `ReadModSig.unixinodefilesystem___dir_lookup`. **Re-verified Valid (Z3):** `unixinodefilesystem___dir_lookup'vc` **Valid (37 393 steps)** in `ReadMod` WITH the read axioms; `unixinodefilesystem___dir_lookup'refn'vc` **Valid (3 206 steps)**.
- **`'refn'vc` is genuinely NON-VACUOUS (I probed both directions).** Weakening the interface precondition (drop `block_num = 5`) → `'refn'vc` **Timeout/RED** (the let hardcodes block 5, can't refine the weaker contract). Strengthening the interface `ensures` (`result >= 0`) → `'refn'vc` **non-Valid (OOM)**. Falsifying the body (`!found + 1`) → the body `'vc` correctly goes **Timeout/RED** (post `result = dir_lookup …` fails). So body-fidelity is caught by `'vc` and the interface↔let match is caught by `'refn'vc`.
- **NO relocated trust in the emitted shape.** In the modular os `.mlw`: read-family axioms (`field_to_str`/`dir_scan_*`/`slot_*`) appear ONLY in `ReadMod` (0 in `PyCSL_Program`); the only `val unixinodefilesystem___dir_lookup` is the `ReadModSig` interface contract (line 86), NOT an assumed-ensures consumer shim; 0 `field_to_str_read` shim; 0 new `\trusted`; 0 new axiom.
- **CORPUS-INERT, re-verified.** Full parallel byte-diff sweep, MY tree vs a foundation-only baseline worktree: **604/604 reference `.mlw` byte-identical** (`diff -rq` rc=0). The `#@ verify_module` directive is provably opt-in.
- **Source `\trusted` on `_dir_lookup` is removed** (it's `verify_module`-tagged + verified, not trusted). The remaining `dirscan-fidelity` trusts at `_dir_find_slot`/`_dir_find_free` are SEPARATE items, unaffected.

**BUT the retirement does NOT land**, for one precisely-scoped reason:

- **The project gates the os write helpers via `--fun <fn>` (per-function)** — confirmed in `config/skills/pycsl-monitoring/SKILL.md:429` ("running `--fun unixinodefilesystem___write_dir_entry`"). On any `--fun <write-helper>` path, `_dir_lookup` is marked **trusted** by the `--fun` filter (`pycsl.py:504`). The modular trigger guard (`Module6_WhyMLTranspiler.py:413`) is `verify_module and **not trusted** and not abstract`, so when `_dir_lookup` is trusted the emitter takes the FLAT path. In the flat path, the trusted `_dir_lookup` stub STILL carries its `#@ proof` read-axiom cites, so `_emit_preamble_axioms` re-emits the read axioms **co-resident** with the write-helper goal. **Re-verified at the GATE:** `pycsl --fun unixinodefilesystem___zero_entry pure_lib/os/UnixInodeFileSystem.py` → `[-] 1 goal(s) remain unproven … Timeout (30.00s, 9 102 940 steps)` — the 9.5M co-residence regression the mission requires GONE is **still present**.
- **The FULL-file gate (`pycsl …UnixInodeFileSystem.py`, no `--fun`) — the other bar — does NOT complete in budget** (timed out at 590s, exit 143, no verdict). The whole-program run is too heavy (the PARTIAL writeup §5 flagged this). So even the full-gate datum cannot be produced this pass.

**Net:** the sound mechanism is PROVEN and the emitter now ASSEMBLES it correctly on the `_dir_lookup`-as-verify-target path (body `'vc` Valid, `'refn'vc` Valid + non-vacuous, no relocated trust, corpus-inert). But the regression that the retirement must clear lives on the **write-helper `--fun` gate path**, where `_dir_lookup` is trusted and the split does NOT fire. To land 4→3 the emitter must isolate the trusted `_dir_lookup` stub's read axioms TOO — and that case has no real `let` to discharge a `'refn'vc`, so it cannot use the proven refinement; doing it soundly is the remaining wall (§3).

I did **NOT** emit any assumed-`val` cross-module shim, new `\trusted`, or new axiom. The emitter fails by NOT splitting on the trusted path (flat, byte-identical, sound) rather than by emitting an unsound split.

---

## 2. The `_transpile_modular` implementation (file:line) + how it partitions axioms + rewrites cross-module calls

All in `src/pycsl/Module6_WhyMLTranspiler.py` unless noted:

- **Trigger guard** — `transpile()` `:413`: `if any(f.get("verify_module") and not f.get("trusted") and not f.get("abstract") for f in functions): return self._transpile_modular(...)`. (This guard is the crux of the GAP — see §1/§3.)
- **`_transpile_modular`** — `:746`. Calls `self._compute_shared_module_maps(functions)` ONCE (`:614`, the full-program contract-propagation maps), builds `self._verify_module_of = {whyml_fn → group}`, then emits, in order: the `Shared` base module, one `<G>Sig` interface + one `<G>` provider per group, and `PyCSL_Program` main. Each module is bracketed `module <name> … end` and gets its OWN abstract-val block.
- **Helpers** — `_emit_prefunctions_infra` `:668` (the shared preamble/use/helpers/record/predicate/globals body, parameterized); `_reset_module_accumulators` `:712` (per-module reset of `_abstract_ops={}`, `_axiom_emitted_decls`, `_class_inv_axioms_emitted` so each module gets its own abstract-stub + axiom set); `_sig_val_from_let` `:720` (strips a `let` body + `variant` → a bodyless interface `val`); `_collect_shared_symbol_decls` `:896` (pre-seeds each module's `_axiom_emitted_decls` with the shared `val function`/`predicate` names so the symbol comes from `use Shared` while the axiom still emits + constrains it); `_shared_use_lines` `:926`.
- **Axiom partition (AUTOMATIC, per-module sub-IR):** each module calls `_emit_preamble_axioms({**self.ir, "functions": <subset>})` (`preamble.py:2026` scans only `ir["functions"]` for `proof` cites). `ReadMod` gets the group fns' subset → only the cited READ axioms; `PyCSL_Program` gets the non-group subset → the WRITE axioms, **0** read axioms. Re-verified in the emitted `.mlw` (§1).
- **Cross-module call rewrite** — `src/pycsl/module6_whyml/expressions.py:845-857` in `_handle_dotted_call`: when `self._verify_module_of[callee] != self._current_emit_group`, emit `(<G>Sig.<callee> self args)` (the proven interface contract) instead of the abstract `val self__<m>` stub. Injected alongside the existing `_composed_provider_methods` concrete-call branch. `self._current_emit_group` is set per module during emission.
- **`Shared` base module:** the concrete `unixinodefilesystem` record + invariants + record-witness axioms + concrete predicates + the shared `val function`/`predicate` decls + globals. A *defined* record can't be clone-substituted, so it lives here and every other module `use Shared`. (This is the 4th module; sound — shared by `use`, not by axiom.)

---

## 3. The precise remaining wall (scoped for the next pass)

**The retirement requires the write-helper `--fun` gate to clear the 9.5M co-residence Timeout.** On that path `_dir_lookup` is trusted (`pycsl.py:504`), so:

1. The guard at `Module6_WhyMLTranspiler.py:413` (`not f.get("trusted")`) makes the emitter take the FLAT path → read axioms co-reside → 9.5M Timeout (re-verified).
2. To fix it, the emitter must isolate the **trusted** `_dir_lookup` stub's cited read axioms into a module the write helpers do NOT `use`, while the write helpers still see the stub's *contract* (so their syscall calls remain sound). That is the same `Shared`+`<G>Sig`+`<G>` partition — BUT a trusted stub has **no real `let`**, so there is **no `'refn'vc` to discharge**: the `<G>Sig` interface `val` would be a genuine ASSUMED boundary (= the existing `\trusted` on `_dir_lookup`). 
3. **Soundness call (human-gated):** isolating a *trusted* stub's axioms relocates NO trust IF the interface `val` IS the trusted stub (net `\trusted` unchanged at 4 on that path — the stub stays trusted, only its axioms move out of the write goals' context). But that path does NOT achieve 4→3 — `_dir_lookup` is still trusted whenever a write helper is the verify target. The 4→3 retirement is only realized on a gate path that **proves `_dir_lookup`'s body** (the `verify_module`-target path or a full-file run), and on that path the split already works (body `'vc` + `'refn'vc` Valid, §1).

So the genuine open question is a GATE-HARNESS one, not an emitter-soundness one: **does the project accept the 4→3 retirement when it is realized only under a gate that verifies `_dir_lookup`'s body (the tagged-target / full-file path), given the per-function `--fun <write-helper>` path keeps `_dir_lookup` trusted + flat (and therefore at the 9.5M regression)?** Options for the next pass:
   - **(a)** Make the per-function gate run `--fun unixinodefilesystem___dir_lookup` (its own target) AND each write helper as SEPARATE gate invocations, each taking the modular path for the function it verifies. The write-helper invocation still trusts `_dir_lookup` → still flat → still 9.5M. So (a) alone does NOT clear the write regression; the write helpers need the read axioms gone from THEIR context independently.
   - **(b)** Extend the directive: when `_dir_lookup` is trusted by `--fun`, STILL emit its cited read axioms into an isolated `ReadMod`-style module (provider with the trusted stub as a bodyless `val`, NO `'refn'vc`), and have `PyCSL_Program` `use ReadModSig` (contract only). Net `\trusted` unchanged (4) on that path; the read axioms leave the write goals' SMT context → clears the 9.5M. This is sound (no relocated trust — the stub WAS trusted), and is the concrete next step. The emitter helpers are mostly in place; the change is the guard at `:413` (fire on trusted too, with a `'refn'vc`-less provider) + a trusted-stub branch in `_transpile_modular`.
   - **(c)** Full-file gate path: needs the whole-program run to fit the budget (it timed out at 590s). Likely needs per-module gate dispatch (run each module's theory separately) — the PARTIAL writeup §5 item 7 flagged this gate-wiring as the one harness change.

**Recommended:** (b) for the write-side regression + the existing modular path for the `_dir_lookup` body, gated as separate per-function/per-module runs, with the gate harness counting the `'refn'vc` (pickable only via a full-theory `-T <module>` run, not `-G "<fn>'refn'vc"`).

---

## 4. Verification evidence (what I re-ran myself, bounded `timeout`)

- **Emitter shape:** `pycsl --no-proof --no-typecheck --keep-mlw pure_lib/os/UnixInodeFileSystem.py` → 4 modules (`Shared`/`ReadModSig`/`ReadMod`/`PyCSL_Program`); `why3 prove --type-only` rc=0.
- **`'vc` + `'refn'vc`:** `why3 prove -P z3 -t 60 …mlw -T ReadMod` → `unixinodefilesystem___dir_lookup'vc` Valid (37 393 steps), `…'refn'vc` Valid (3 206 steps).
- **Non-vacuity probes:** weaker interface precond → `'refn'vc` Timeout/RED; stronger interface ensures → `'refn'vc` OOM (non-Valid); falsified body → body `'vc` Timeout/RED.
- **Write helpers, RAW `why3 prove` over the modular `.mlw` (`-T PyCSL_Program -G …'vc` + `split_vc`, Z3):** `_zero_entry`/`_write_dir_entry`/`_write_entry` ALL subgoals Valid, max ~453K steps (sub-second). (Confirms the *isolated* write context proves trivially — matches the PARTIAL's claim.)
- **GATE (the authoritative regression measurement):** `pycsl --fun unixinodefilesystem___zero_entry …` → 1 goal unproven, Timeout 9 102 940 steps (**regression PRESENT**, because the `--fun` path trusts `_dir_lookup` → flat → read axioms co-reside). `pycsl --fun unixinodefilesystem___dir_lookup …` → `[+] Verification SUCCESS` (its own body path DOES split; but that path doesn't exercise the write helpers).
- **FULL-file gate:** `pycsl …UnixInodeFileSystem.py` (no `--fun`) → timed out at 590s, no verdict.
- **Corpus byte-diff:** my tree vs foundation-only baseline → 604/604 reference `.mlw` byte-identical.
- **No-relocated-trust grep on the modular `.mlw`:** read axioms 0 in `PyCSL_Program`; only `val …dir_lookup` is the `ReadModSig` interface; 0 `field_to_str_read`; 0 new `\trusted`/axiom.

---

## 5. Patch + writeup + tree
- **Patch:** `getting-better/PROPOSAL-module-emission-FINISHED-dir-lookup.patch` (1339 lines, 16 files: foundation + the finished `_transpile_modular` assembly in `Module6_WhyMLTranspiler.py`, the cross-module rewrite in `module6_whyml/expressions.py`, per-module reset in `module6_whyml/abstract_ops.py` + `preamble.py`, and the 0720.proofs).
- **This writeup:** `getting-better/20260620-1130-module-emission-FINISHED-dir-lookup-4to3-PARTIAL.md`.
- **Validation artifact:** `getting-better/VALIDATION-module-emission-os-split.mlw` (the emitter's real 4-module output).
- **Tree:** reverted clean (only the patch + the two writeups + the validation `.mlw` remain). **NOT committed.** Stash empty. Baseline worktree removed.

## 6. Human-sign-off note
**PARTIAL, NOT ready to land.** Solid + re-checkable now: (a) the emitter ASSEMBLES the proven 4-module shape (re-emit the os file); (b) `'refn'vc` Valid + non-vacuous, body `'vc` Valid (re-run `why3 prove -T ReadMod`); (c) no relocated trust (grep the modular `.mlw`); (d) corpus-inert 604/604 (byte-diff sweep). NOT done / the wall: the retirement does not land because the project's `--fun <write-helper>` gate path trusts `_dir_lookup` and the guard (`Module6_WhyMLTranspiler.py:413`, `not trusted`) keeps that path FLAT → the 9.5M co-residence Timeout REMAINS there; and the full-file gate does not complete in budget. The next pass must either (b) split the *trusted* `_dir_lookup` stub's read axioms out of the write helpers' context (sound, net trust unchanged on that path; concrete and scoped in §3), or change the gate harness to realize the retirement only on a body-verifying gate path — a human TCB/gate-policy decision, not an emitter-soundness one.
