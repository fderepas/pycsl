# Module-emission feature (axiom isolation) for the `_dir_lookup` 4→3 de-trust — VERDICT: **PARTIAL — sound MECHANISM PROVEN end-to-end + directive shipped (corpus-inert, fully documented); multi-module emitter ASSEMBLY not completed (the remaining wall is precisely scoped)**

**Date:** 2026-06-20 ~07:43
**Worktree:** `.claude/worktrees/agent-a9bf35722dc59ed55` (STOP-AT-PROPOSAL — nothing committed; tree reverted clean, only the patch + this writeup + the validation artifact remain)
**Patch:** `getting-better/PROPOSAL-module-emission-dir-lookup.patch` (996 lines, 15 files — the read-side foundation + the module-emission directive foundation + 5-surface docs + skill)
**Validation artifact:** `getting-better/VALIDATION-module-emission-os-split.mlw` (the hand-built 4-module split of the real os, where the SOUND clone-refinement boundary is proven non-vacuous)
**Substrate:** clean HEAD `9a0ce90` + `getting-better/PROPOSAL-dir-lookup-faithful-name-detrust.patch` (the sound read-side de-trust foundation) applied.

---

## 1. BOTTOM LINE

`_dir_lookup` does **NOT** retire 4→3 in this pass, but the build is a *precise, honest partial*, not a dead end. Two load-bearing results were PROVEN (the hardest open risks the design proposal flagged), and the directive foundation is fully shipped + verified inert + documented:

1. **The sound, axiom-isolated cross-module mechanism is PROVEN at the Why3 level and validated on the REAL os axiom families.** The construct is **Why3 module `clone`-refinement** — NOT an assumed `val`, NOT a hand-emitted narrowing VC, but the *native* Why3 refinement obligation, which is strictly stronger and cleaner. An interface `module` declares a callee's contract; the owning provider `module` (holding its group's axioms LOCALLY) proves the real `let` *implements* it via the synthetic VC `<fn>'refn'vc`; consumers `use` the interface and call the proven contract — and they do **NOT** see the provider's axioms. Verified (`/tmp/xmod_refine.mlw`, reproduced): `provided'refn'vc` **Valid**, `no_read_ax_leak` **Unknown** (isolation holds), `uses_provided'vc` **Valid** (sound consumer). On the real os module (`getting-better/VALIDATION-module-emission-os-split.mlw`): `unixinodefilesystem___dir_lookup'refn'vc` **Valid both provers ×2** and **non-vacuous** (a deliberately-wrong impl → `'refn'vc` Unknown); `_dir_lookup'vc` Valid in the provider WITH read axioms (Z3 41 716 steps); the record type-invariant Valid; the consumer sees only the proven contract.
   - **This is a genuine no-relocated-trust resolution.** A subagent investigation (file:line evidence) confirmed the EXISTING abstract `self.<m>()` stub is an *assumed* `val ... ensures{...}`, sound today ONLY because the real `let m` is co-resident — so a naive split (move `_dir_lookup` out, consumers keep the assumed stub) WOULD relocate trust. The `clone`-refinement boundary closes exactly that hole: the provider PROVES the contract the consumer assumes. Net TCB unchanged.

2. **The regression that blocks the read-side de-trust is CONFIRMED real at the GATE level (the mission's bar), not a measurement artifact.** With the read-side foundation patch applied, `pycsl --fun unixinodefilesystem___zero_entry pure_lib/os/UnixInodeFileSystem.py` → **Timeout 9 581 567 steps** (one goal unproven → gate FAILED). This matches the Milestone-0 spike's ~9.5 M exactly and the PARTIAL-gate-gap doc's diagnosis. (A raw `why3 prove` over the flat `.mlw` does NOT reproduce it — the regression is specific to the `--fun` GATE path, which re-emits the whole preamble incl. the READ axioms while proving each WRITE goal, tipping it over. Honest note: a subagent that measured only raw `why3 prove` over `/tmp/os_flat.mlw` did NOT see the co-residence effect; the GATE measurement above is the authoritative one and DOES reproduce it.)

3. **The opt-in directive `#@ verify_module <name>` is SHIPPED, wired end-to-end, corpus-byte-inert, and fully documented** — the foundation a future session completes the emitter on. What is NOT done: the multi-module emitter *assembly* itself (it raises a clear, doctrine-compliant `NotImplementedError` rather than emit an under-verified split). So the full body gate ×2 on `_dir_lookup` retiring 4→3 was **not run** (the emitter does not yet produce the proven shape) — this is the precise GAP.

**I did NOT fall back to an assumed-`val` cross-module shim.** The boundary mechanism is the proven `clone`-refinement; the emitter that would wire it is the unfinished part, and it fails loud rather than emit something unsound.

---

## 2. The emitter mechanism (file:line) + the directive + the cross-module soundness

### 2.1 The directive — wired through the full pipeline (verified end-to-end)
`#@ verify_module <name>` (a method-level directive carrying a group label):
- **Grammar** — `src/pycsl/frontend/Module2_Parser.py`: rule `verify_module_decl: "verify_module" CNAME` (added to the `decl` alternatives), dataclass `VerifyModule(name)`, transformer `verify_module_decl(self, name)`.
- **Weaver** — `src/pycsl/frontend/Module3_Weaver.py`: `node.csl_verify_module = ""` default + `elif isinstance(c, VerifyModule): node.csl_verify_module = c.name`.
- **IR** — `src/pycsl/frontend/Module5_IREmitter.py`: `"verify_module": getattr(node, 'csl_verify_module', "") or ""`.
- **Transpiler gate** — `src/pycsl/Module6_WhyMLTranspiler.py:transpile()`: `if any(f.get("verify_module") for f in functions): return self._transpile_modular(...)`. Default (no tag) falls through to the unchanged flat `module PyCSL_Program`.
- **Verified end-to-end:** tagging `_dir_lookup` with `#@ verify_module ReadMod` → the IR carries `func["verify_module"] == "ReadMod"` at the transpiler (confirmed by a monkeypatch probe), and the gate fires.

### 2.2 The partition for `_dir_lookup` (why it is so clean)
- **`_dir_lookup` calls NO siblings** (it only reads `self.dir`) → the READ module has **zero** cross-module calls — fully self-contained, no boundary needed *on the read side at all*.
- **`_dir_lookup`'s consumers are the `sys_*` syscalls** (17 call sites), all in the flat module. They are the ones that must call the proven contract across the boundary.
- **The write helpers** (`_zero_entry`/`_write_dir_entry`/`_write_entry`) call `_blit_*`, NOT `_dir_lookup`, and cite the WRITE axiom family — they stay in the flat module, which then carries NO read axioms.

### 2.3 The cross-module soundness — Why3 module `clone`-refinement (PROVEN, not assumed)
The validated target shape (4 modules, `getting-better/VALIDATION-module-emission-os-split.mlw`):
- **`Shared`** — the concrete `unixinodefilesystem` record + its invariants + concrete predicates + record-witness axioms (a *defined* record type cannot be `clone`-substituted, so it is shared by `use`, not cloned). `use`d by all three modules below.
- **`DirSig`** (interface) — shared abstract symbols (`val function field_to_str/slot_inode/slot_name/dir_lookup/bit_*`) + `_dir_lookup`'s contract as a bodyless `val unixinodefilesystem___dir_lookup … requires{…} ensures{…}`. NO read/write axioms.
- **`ReadImpl`** (provider) — shared abstract symbols + the **READ axioms LOCALLY** + the real `let unixinodefilesystem___dir_lookup = <body>` + trailing `clone DirSig with val unixinodefilesystem___dir_lookup = unixinodefilesystem___dir_lookup, …`. Why3 generates `unixinodefilesystem___dir_lookup'refn'vc` (the refinement obligation) → **Valid, non-vacuous**.
- **`PyCSL_Program`** (main) — everything else, the **WRITE axioms** but NOT the read axioms, `use DirSig`, the `sys_*` consumers call `DirSig.unixinodefilesystem___dir_lookup`.

**Why this is sound (net TCB unchanged):** every function is proved exactly once against a contract that is itself proved; `_dir_lookup`'s contract is discharged in `ReadImpl` (`'vc`) AND proven to be the interface contract (`'refn'vc`); consumers see only the proven contract; no module sees another's axioms (the directional axiom-visibility probe: a read-axiom goal placed in the write context is Unknown/Timeout, and vice-versa). The only thing the split changes is WHICH declarations share the SMT context at each VC — a feasibility lever, not a trust lever.

**Why3 `scope` is the WRONG construct (re-confirmed):** a `scope` is a namespace; an `axiom` is global within its enclosing `module` regardless of scope nesting (probe: two sibling scopes with `f x=1`/`f x=2` prove `goal 1=2` Valid). Only separate top-level `module`s isolate (the same axioms in modules A/B → `1=2` Unknown). The feature is correctly **module-emission**.

### 2.4 The emitter helpers built (the assembly scaffold)
`src/pycsl/Module6_WhyMLTranspiler.py`:
- `_verify_module_groups(functions)` → `{group → [whyml fn names]}`, deterministic.
- `_compute_shared_module_maps(functions)` → the SHARED cross-function lookup state (return-types, all the contract-propagation `_module_method_*_ensures` maps, no_exception summary), computed once from the full function set (a cross-module call still needs the callee's propagated contract).
- `_transpile_modular(functions, type_decls)` → the entry the gate calls. **Currently raises a clear, actionable `NotImplementedError`** listing the requested groups and the precise remaining work (it does NOT emit an under-verified or unsound split — fail-loud per the doctrine).

---

## 3. FULL-gate ×2 + no-relocated-trust grep + corpus byte-diff scope

### 3.1 Full body gate ×2 — NOT RUN on the retirement (this is the GAP)
The multi-module emitter assembly is incomplete, so the emitter does not yet produce the proven 4-module shape; therefore the FULL body gate ×2 on `_dir_lookup` retiring 4→3 could not be run. What WAS measured:
- **Gate-level regression (the blocker), CONFIRMED ×1 (deterministic):** `pycsl --fun unixinodefilesystem___zero_entry` → Timeout **9 581 567 steps**, gate FAILED.
- **The SOUND mechanism, validated ×2 on the real os axioms** (`getting-better/VALIDATION-module-emission-os-split.mlw`, best-of Alt-Ergo+Z3, two runs): `unixinodefilesystem___dir_lookup'refn'vc` Valid (Z3 3 714 steps / AE 6 steps) + non-vacuous; `_dir_lookup'vc` Valid (Z3 41 716 steps) WITH read axioms; record type-invariant Valid; the consumer sound. (The write helpers' gate-equivalent pass under module-emission is the datum that REQUIRES the finished emitter — see §5.)

### 3.2 No-relocated-trust grep
- **Source `\trusted`:** the patch's read-side foundation removes the `dirscan-fidelity` directive on `_dir_lookup` (HEAD 4 → 3) **once the emitter produces the split**; in THIS partial the source still carries 4 (the read-side change is banked, not active, because the emitter does not yet split). **Net `\trusted` is therefore unchanged at 4 in the as-shipped partial** — nothing relocated, nothing added.
- **The module-emission additions add ZERO trust of any class:** no assumed-ensures `val`, no `field_to_str_read` shim, no new `\trusted`, no new axiom. The cross-module boundary is the proven `'refn'vc` (validated non-vacuous). The directive's emitter path fails loud rather than emit an assumed boundary.
- **The foundation read-side grep (banked):** `field_to_str` is a `val function` with NO ensures (no logical content); `_dir_lookup` name is a genuine `field_to_str … 30` TERM (0 `decode_1`/`str_hash_op`); 0 `field_to_str_read` shim.

### 3.3 Corpus byte-diff scope — directive is INERT (604/604 real files identical)
Full parallel emission sweep, MY tree (read-side foundation + module-emission directive + docs) vs the foundation-only baseline (read-side foundation alone): **0 real differences** — all 604 emitted `.mlw` byte-identical. (The single apparent diff, `0700.mlw`, is a stale orphan: there is no `0700.py` and no tracked `0700` — a sweep-hygiene artifact, not an emission difference.) The os file is byte-identical to its pre-directive emission. **The `#@ verify_module` directive is provably opt-in and corpus-inert.**
- Beyond the directive, the patch's read-side foundation changes exactly **4** reference `.mlw` (0708/0711/0712/0714 — the `field_to_str`/`slot_name` byte-codec corpus), as documented in the foundation writeup.
- **doc-coherency `--check` → rc=0:** `verify_module` documented across all 5 normative surfaces (README, annotations.md §2.1.29, concrete-syntax §2.1.6m, static-semantics §2.1.6m, translational §T.2.7m) + the `pycsl-annotate` skill. The grammar↔annotations cross-check passes.

---

## 4. Patch + writeup paths
- **Patch:** `getting-better/PROPOSAL-module-emission-dir-lookup.patch` (996 lines, 15 files: the read-side foundation `pure_lib/os/UnixInodeFileSystem.py` + `module6_whyml/{expressions,preamble}.py` + 0720.proofs; the module-emission directive `frontend/{Module2_Parser,Module3_Weaver,Module5_IREmitter}.py` + `Module6_WhyMLTranspiler.py`; the 5 doc surfaces + the `pycsl-annotate` skill).
- **This writeup:** `getting-better/20260620-0743-module-emission-dir-lookup-4to3-PARTIAL.md`.
- **Validation artifact:** `getting-better/VALIDATION-module-emission-os-split.mlw` (the proven 4-module split of the real os).

---

## 5. The precise remaining emitter work (the wall, scoped for the next pass)

`_transpile_modular` must emit the validated 4-module shape (`Shared` + `<G>Sig` + `<G>` + `PyCSL_Program`). The pieces, in dependency order:

1. **Factor the body-assembly** (`transpile()` lines ~399-598) into a re-callable `_emit_one_module(module_name, funcs_in_module, declared_types, …)` that brackets `module <name> … end`, with per-module **reset** of the accumulators that the flat path leaves global: `self._abstract_ops = {}`, `self._axiom_emitted_decls`, `self._class_inv_axioms_emitted` (each emitted module needs its OWN abstract-stub block and axiom set). The shared maps (`_compute_shared_module_maps`, already built) stay computed once.
2. **Per-module axiom selection** is AUTOMATIC: `_emit_preamble_axioms(ir)` scans only `ir["functions"]`, so pass a per-module sub-IR (`{**ir, "functions": funcs_in_module}`). The READ axioms appear only in the ReadMod sub-IR (only `_dir_lookup` cites them); the WRITE axioms only in PyCSL_Program.
3. **The `Shared` base module** = preamble `use`s + helpers + the shared `val function`/`predicate` decls + the concrete record type WITH invariants + the record-witness axioms (hoisted before the record, as `_emit_class_inv_axioms` already does). A *defined* record type cannot be `clone`-substituted → it MUST live in `Shared`, `use`d by every other module. (This forced the 4th module in validation; it is sound — shared by `use`, not by axiom.)
4. **The `<G>Sig` interface module** per group = `use Shared` + each group function's contract as a bodyless `val <fn> … requires{…} ensures{…}` (reuse `_emit_contracts` with the `emit_as_val` path).
5. **The `<G>` provider module** = `use Shared` + the group's cited axioms (sub-IR) + the real `let <fn>` bodies (`_emit_function`) + a trailing `clone <G>Sig with val <fn> = <fn>` for each group function. **Clone-substitution syntax (verified in Why3 1.8.2):** a `val function`/`val`/bodyless-`val` all substitute with the **`val`** keyword (`val f = f`); `val function f = f` is a syntax error and `function f = f` triggers "program function must be refined instead". Since the shared symbols come from `use Shared`, the clone substitutes ONLY the contract `val`s (Why3 emits a benign "no abstract symbol" warning but still generates the real `'refn'vc`).
6. **The `PyCSL_Program` main module** = `use Shared` + `use <G>Sig` (for every group) + the WRITE axioms (its own sub-IR) + all the non-group `let` bodies. The cross-module call rewrite: in `_handle_dotted_call` (`src/pycsl/module6_whyml/expressions.py:842`), when the callee's `verify_module` group ≠ the current function's group, emit `(<G>Sig.<callee> self args)` (the proven contract) instead of the abstract `val self__<m>_<n>` stub. (Clean injection point: alongside the existing `_composed_provider_methods` concrete-call branch at line 852.)
7. **Gate wiring:** the synthetic `'refn'vc` cannot be addressed by `-G "<fn>'refn'vc"` ("Goal not found") — it must be picked up via a full-theory run (`why3 prove … -T <G>`) and filtered. The body gate (`pycsl --fun` / full) must run per-module and include the `'refn'vc` in the 0-non-Valid count. This is the one place the gate harness needs a small change.

**The single remaining open RISK to measure first** (before completing the build): does the FINISHED emitter's `PyCSL_Program` (write helpers, NO read axioms) pass the **GATE** (`--fun` re-emission path) at 0 non-Valid — i.e. does removing the read axioms from the write helpers' module actually clear the 9.5 M `--fun` timeout? The validation artifact shows the write helpers prove under split_vc/Z3 once isolated, and the gate-level 9.5 M regression is driven by the read axioms being in the `--fun` preamble — so the expectation is YES, but it is only confirmable by the finished per-module gate. (Caveat: under a *whole-VC* Z3 run, the large write bodies `_write_dir_entry`/`_write_entry` Timeout in BOTH flat and split — they need the gate's `split_vc` + best-of-both-provers to pass, which they do per the validation; confirm the finished emitter's gate uses that path.)

---

## 6. Human-sign-off note

This is a **PARTIAL, NOT ready to land.** What is solid and re-checkable now: (a) the SOUND clone-refinement cross-module mechanism (`'refn'vc` Valid + non-vacuous on the real os axioms — re-run `getting-better/VALIDATION-module-emission-os-split.mlw`, or the minimal `/tmp/xmod_refine.mlw` recipe in the patch comments); (b) the gate-level 9.5 M regression (re-run `pycsl --fun unixinodefilesystem___zero_entry` with the foundation patch); (c) the `#@ verify_module` directive shipped corpus-inert + 5-surface-documented (re-run the byte-diff sweep + `bin/doc-coherency.py --check`). What is NOT done: the multi-module emitter assembly (`_transpile_modular` fails loud), so `_dir_lookup` does NOT yet retire 4→3 through the gate. The parent should: complete §5 items 1-7, then re-run the FULL body gate ×2 (all four functions 0 non-Valid through the gate, `'refn'vc` Valid, 9.5 M gone), the no-relocated-trust grep (`\trusted` 4→3 net, nothing relocated), the corpus byte-diff (only the os module emits as modules; everything else byte-identical), the module-isolation probe, and recompile 0720.proofs — before bringing the retirement to the human.

**Tree:** reverted clean (only the patch + this writeup + the validation `.mlw` remain). **NOT committed.** Stash empty.

---

## PARENT VERIFICATION NOTE
Re-ran the validation: `_dir_lookup'refn'vc` (clone-refinement obligation) **Valid**
(3639–5253 steps, pre+post subgoals) — the SOUND cross-module boundary holds on the real
os. Module isolation independently re-confirmed by my own probe (`scope` → `goal 1=2`
Valid = co-resident; separate `module`s → Unknown = isolated). So the clone-refinement is
a genuine proven interface (no relocated trust), and module-emission (not scope-emission)
is correct. The 6 OOM / 30 raw-non-Valid elsewhere in the 2083-line hand-built POC are
best-of-N per-prover raw counts + pre-existing `sys_rename` residuals, NOT a soundness
issue (the POC is the boundary proof, not the clean emitter output). VERDICT CONFIRMED:
sound mechanism + directive shipped; the precise remaining piece is the multi-module
emitter ASSEMBLY (`_transpile_modular`), which fails loud rather than emit unsound.
