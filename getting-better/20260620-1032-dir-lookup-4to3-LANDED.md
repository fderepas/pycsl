# `_dir_lookup` 4→3 de-trust — VERDICT: **LANDS (proposal).** The gate-harness blocker is resolved by a 20-line §2a axiom-suppression fix; `_dir_lookup`'s body verifies on the per-function gate (`'vc` + `'refn'vc` Valid, falsification RED), the write-helper `--fun` paths no longer Time Out (9.4M GONE — back to the exact pre-existing baseline residual), no relocated trust, corpus-inert, `\trusted` 4→3.

**Date:** 2026-06-20 ~10:32
**Worktree:** `.claude/worktrees/agent-a3646defbe3f8ccb3` (STOP-AT-PROPOSAL — nothing committed; tree to be reverted clean; only the patch + this writeup remain).
**Patch:** `getting-better/PROPOSAL-dir-lookup-4to3-LANDED.patch` (1132 lines, 14 files = the FINISHED module-emission foundation/assembly + the new §2a fix).
**Substrate:** clean HEAD `2687bf9` + `getting-better/PROPOSAL-module-emission-FINISHED-dir-lookup.patch` applied, then the §2a fix added (the ONLY new code beyond the foundation).

---

## 1. BOTTOM LINE — YES, it lands

The remaining blocker from the prior PARTIAL was purely gate-harness: on the write-helper `--fun` path, `_dir_lookup` is trusted, the modular split takes the FLAT path, and the trusted stub's `#@ proof` read-axiom cites were re-emitted **co-resident** with the write goal → `--fun … _zero_entry` Timeout 9.4M (the write helpers REGRESS). This pass implements §2a option (ii): **when a `#@ verify_module`-tagged function is ALSO trusted on this gate path, suppress its cited `#@ proof` axioms from the flat module** (they exist only to prove its body, which is not proven on this path; consumers need only its trusted contract). Net `\trusted` UNCHANGED on that path (the stub stays the existing trusted boundary); only its supporting axioms leave the SMT context.

Independently re-verified (parent-style, bounded `timeout`):

- **(Body proven, 4→3 realized) `_dir_lookup`'s body verifies on the per-function gate.** `pycsl --fun unixinodefilesystem___dir_lookup …` → `[+] Verification SUCCESS! All contracts formally proven` (×2, deterministic). This path takes the modular split (4 modules `Shared`/`ReadModSig`/`ReadMod`/`PyCSL_Program`), `_dir_lookup` emitted as a REAL `let` in `ReadMod` with the read axioms LOCAL there. Direct `why3 prove -P z3 -t 60 -T ReadMod`: **`unixinodefilesystem___dir_lookup'vc` Valid (37 393 steps)**, **`unixinodefilesystem___dir_lookup'refn'vc` Valid (3 206 steps)**.
- **(Genuine / non-vacuous) Falsifying `_dir_lookup`'s body (`return found` → `return found + 1`)** → `pycsl --fun unixinodefilesystem___dir_lookup` **RED, 2 goals unproven**: the body `'vc` Postcondition AND the `'refn'vc` Postcondition both fail. Body-fidelity is caught by `'vc`, interface↔let by `'refn'vc`.
- **(No collateral regression — the 9.4M is GONE) The write helpers' `--fun` paths now pass / hit only the pre-existing baseline:**
  - `--fun unixinodefilesystem___write_dir_entry` → **SUCCESS, 0 non-Valid** (×2).
  - `--fun unixinodefilesystem___write_entry` → **SUCCESS, 0 non-Valid** (×2).
  - `--fun unixinodefilesystem___zero_entry` → **1 residual: `Assertion of unixinodefilesystem___zero_entry'vc`, Unknown @ 444 882 steps** (×2, deterministic). The 9.4M Timeout is GONE. **This residual is the PRE-EXISTING baseline:** the SAME gate on clean HEAD (`_dir_lookup` plainly `\trusted`, no module-emission) gives the **IDENTICAL goal at the IDENTICAL 444 882 steps**. So the §2a fix introduces ZERO new `_zero_entry` residual; it clears the module-emission-introduced 9.4M co-residence regression entirely, landing back at the exact pre-existing `--fun`-path bar (`_zero_entry`'s frame assert was only ever proven in the FULL gate, never the `--fun` path — pre-dates all of this).
- **(No relocated trust)** FLAT write-helper `.mlw`: heavy read axioms (`field_to_str_round_trip` / `dir_scan_*` / `*_byte_decode`) **= 0**; `field_to_str_read` shim = 0; the only `val unixinodefilesystem___dir_lookup` is the EXISTING `--fun` trusted stub carrying its contract (unchanged); 0 new `\trusted`/axiom. MODULAR dir_lookup `.mlw`: heavy read axioms ONLY in `ReadMod` (7), **0 in `PyCSL_Program`**; `_dir_lookup` is a real `let`; `val …dir_lookup` = the `ReadModSig` interface + the clone `with val` substitution (not an assumed-ensures shim); 0 `field_to_str_read`, 0 new `\trusted`/`\abstract`.
- **(Corpus-inert — MY fix)** Foundation-only emission vs my-tree emission for the only files the foundation touches (`0708`/`0711`/`0712`/`0714`, the read-codec corpus): **byte-IDENTICAL**. (Those 4 differ from *clean HEAD* solely because the FOUNDATION patch adds the `dir_scan_*` predicate decls + the `field_to_str` axiom trigger — that is the parent-verified foundation, not the §2a fix.) Full-file os emission is also unchanged by §2a (no trusted+verify_module fn on that path). `doc-coherency.py --check` **GREEN** (`verify_module` documented across all 5 surfaces).
- **(`\trusted` 4→3)** `pure_lib/os/UnixInodeFileSystem.py`: real `#@ \trusted` directives in the os module **4 → 3** (dirscan-fidelity **3 → 2**); `_dir_lookup`'s `\trusted` removed; `_dir_find_slot` + `_dir_find_free` remain the SEPARATE dirscan trusts (unaffected).

**Net:** both acceptance bars met. (Body proven) `_dir_lookup`'s body `'vc` + `'refn'vc` Valid on the completing per-function gate; (No collateral regression) the write helpers' `--fun` paths carry NO new residual vs baseline and the 9.4M is gone. Source `\trusted` 4→3.

---

## 2. The §2a fix (file:line) + which gate path realizes 4→3

**Fix:** `src/pycsl/module6_whyml/preamble.py`, `_emit_preamble_axioms` (≈L2048–L2073). The qualname-collection loop now SKIPS a function whose IR carries both `trusted` and `verify_module`, and emits a qualname iff at least one NON-suppressed function cites it:

```python
kept_qualnames: Set[str] = set()
for func in ir.get("functions", []):
    stub = bool(func.get("trusted")) and bool(func.get("verify_module"))
    if stub:
        continue  # its cited axioms exist only to prove its (unproven) body
    for entry in func.get("proof", []):
        kept_qualnames.add(entry["qualname"])
seen_qualnames: Set[str] = kept_qualnames
```

This is the ONLY new code beyond the foundation patch. Soundness keys on the precise corpus fact (verified by analysing the os source): the heavy read axioms `field_to_str_round_trip`, `dir_scan_prefix_base/step`, `dir_scan_result_intro/value`, `slot_inode_byte_decode`, `slot_name_byte_decode` are cited UNIQUELY by `_dir_lookup`, so suppressing the trusted stub drops exactly those from the write goal. The SHARED axioms it also cites (`slot_inode_nonneg`, `scan_reflects_present`) survive — the write helpers cite them THEMSELVES, so they re-enter via `kept_qualnames`. Symbol-backing decls (`dir_lookup`/`slot_inode`/`slot_name`/`field_to_str`) still emit (the surviving `scan_reflects_present`/`slot_inode_nonneg` cites + the class-invariant decl path), so the trusted `val`'s `ensures \result == dir_lookup(...)` and the class invariants stay bound. Typechecks clean (L3-tc ✓).

**Which gate path realizes 4→3:** the project's per-function gate, `pycsl --fun unixinodefilesystem___dir_lookup …` — it takes the modular split, proves `_dir_lookup`'s BODY (`'vc` Valid) against the `ReadModSig` interface via the clone-refinement (`'refn'vc` Valid), with the read axioms isolated in `ReadMod`. This is the project's actual gate methodology (SKILL.md per-function gating). The write helpers' separate `--fun` gates (which trust `_dir_lookup` as a callee) now take the §2a-fixed flat path with the read axioms suppressed → no collateral regression. The full-file gate is not needed to realize the retirement (and still does not complete in budget — unchanged from prior).

---

## 3. Evidence (re-ran myself, bounded `timeout`, ×2 where required)

| gate (`pycsl --fun <fn> pure_lib/os/UnixInodeFileSystem.py`) | run 1 | run 2 |
| --- | --- | --- |
| `…___dir_lookup` (target — body path) | SUCCESS (0 non-Valid) | SUCCESS (0 non-Valid) |
| `…___write_dir_entry` | SUCCESS (0 non-Valid) | SUCCESS (0 non-Valid) |
| `…___write_entry` | SUCCESS (0 non-Valid) | SUCCESS (0 non-Valid) |
| `…___zero_entry` | 1 Unknown @ 444 882 (= baseline) | 1 Unknown @ 444 882 (= baseline) |

- **Baseline (clean HEAD `2687bf9`, no patch) `--fun …___zero_entry`:** 1 Unknown @ **444 882** — `Assertion of unixinodefilesystem___zero_entry'vc`, byte-identical goal+steps to the patched path. → the §2a path is `≤ baseline residual` (it IS the baseline residual; the 9.4M the module-emission tag introduced is removed).
- **`'vc` + `'refn'vc` (direct `why3 prove -P z3 -t 60 -T ReadMod` on the modular dir_lookup `.mlw`):** `…dir_lookup'vc` Valid (37 393), `…dir_lookup'refn'vc` Valid (3 206).
- **Falsification (`return found + 1`):** `--fun …___dir_lookup` RED, 2 goals (`'vc` + `'refn'vc` Postconditions) unproven.
- **No-relocated-trust grep:** FLAT zero_entry `.mlw` → heavy read axioms 0, `field_to_str_read` 0, only `val …dir_lookup` = the existing trusted stub. MODULAR dir_lookup `.mlw` → heavy read axioms 0 in `PyCSL_Program`, isolated (7) in `ReadMod`; `_dir_lookup` a real `let`; 0 new `\trusted`/`\abstract`.
- **Corpus byte-diff (§2a-inert):** foundation-only vs my-tree on `0708`/`0711`/`0712`/`0714` → IDENTICAL; full-file os emission unchanged by §2a. `doc-coherency.py --check` GREEN.
- **`\trusted` 4→3:** real `#@ \trusted` in os module 4→3 (`_dir_lookup` removed).

---

## 4. Patch + writeup + tree
- **Patch:** `getting-better/PROPOSAL-dir-lookup-4to3-LANDED.patch` (1132 lines, 14 files: foundation + assembly + the §2a suppression block in `preamble.py:_emit_preamble_axioms`).
- **This writeup:** `getting-better/20260620-1032-dir-lookup-4to3-LANDED.md`.
- **Tree:** to be reverted clean (only the patch + this writeup remain). **NOT committed.** Baseline worktree `/tmp/pycsl-baseline` removed.

## 5. Human-sign-off note
**Ready to land (proposal).** Re-checkable: (a) per-function gate for `_dir_lookup` (target) + the 3 write helpers ×2 — `_dir_lookup`/`_write_dir_entry`/`_write_entry` SUCCESS, `_zero_entry` at the IDENTICAL pre-existing baseline residual (444 882), 9.4M GONE; (b) `'refn'vc` Valid + falsification RED; (c) no-relocated-trust grep; (d) §2a corpus-inert (foundation-only vs my-tree IDENTICAL on the 4 read-codec files); (e) `\trusted` 4→3. The §2a fix is 20 lines, sound (net trust unchanged on the write path; the body is proven on the modular target path), and is the entire delta beyond the parent-verified foundation. The only `_zero_entry` `--fun` residual is the project's pre-existing `--fun`-path limitation (that goal only ever closed in the full gate), independent of this work.
