# `_dir_find_free` 2→1 de-trust — VERDICT: **LANDS (proposal).**

`_dir_find_free`'s `\trusted reviewer: dirscan-fidelity` retires via the LANDED read-side
recipe — the THIRD and LAST dirscan retirement (mirroring `_dir_lookup` PR #53 and
`_dir_find_slot` PR #54). Its body verifies on the per-function gate (`'vc` + `'refn'vc`
Valid, falsification RED, the required `ensures 1==0` non-vacuity probe RED), no collateral
regression on the other dir/write helpers, no relocated trust, corpus byte-identical,
`\trusted` 2→1 (dirscan-fidelity 1→0 — fully retired; only `fd-resolution-fidelity` remains).

**Date:** 2026-06-20 ~12:12
**Worktree:** `.claude/worktrees/agent-a1dbbd8e97077a9dd` (STOP-AT-PROPOSAL — nothing committed;
tree reverted clean; only the patch + this writeup remain).
**Patch:** `getting-better/PROPOSAL-dir-find-free-2to1.patch` (applies cleanly; `git apply --check` OK)
**Substrate:** clean `main` (commit 5f9a095 — the full read-side recipe is ON MAIN:
`#@ verify_module` module-emission (`_transpile_modular`), the `clone`-refinement boundary,
the per-slot `slot_inode_byte_decode`/`slot_inode_nonneg` keystones, the §2a trusted-stub
axiom suppression, and the `dir_find_slot`/`dir_scan` marker families + byte-identity prefix
gating).

---

## 1. BOTTOM LINE — YES, it retires 2→1

`_dir_find_free` scans the 16 directory slots and returns the INDEX (0..15) of the LAST FREE
slot (`slot_inode == 0`), or -1 if the block is full — the FREE-SLOT twin of `_dir_find_slot`
(which returns the LAST live-match INDEX). It reads **ONLY** `slot_inode` (NO name decode), so
— as the mission predicted — the faithful-NAME EMITTER recognizer is UNNEEDED here; this is
strictly SIMPLER than `_dir_find_slot`. Its single fidelity ensures
(`\result >= 0 ==> slot_inode(self.dir, block_num, \result) == 0`) was
`\trusted reviewer: dirscan-fidelity`. It now verifies against a NEW cross-validated zero-TCB
**free-slot-index marker** family (`dir_find_free_result` / `dir_find_free_prefix`), authored
over the EXISTING per-slot decode symbol `slot_inode`, with the body made faithful (literal
slot byte offsets bridged by `slot_inode_byte_decode`) and isolated in its own
`#@ verify_module FindFreeMod`.

Re-verified independently (bounded `timeout`, ×2 where required):

- **(Body proven, 2→1 realized)** `pycsl --fun unixinodefilesystem___dir_find_free` →
  `[+] Verification SUCCESS! All contracts formally proven` (×2, deterministic). Modular split
  (Shared / FindFreeModSig / FindFreeMod / FindSlotModSig / FindSlotMod / ReadModSig / ReadMod
  / PyCSL_Program); `_dir_find_free` is a REAL `let` in `FindFreeMod` (.mlw line 120) with the
  free-slot-index read axioms LOCAL there. Direct `why3 prove -P z3 -t 60 -T FindFreeMod`:
  **`unixinodefilesystem___dir_find_free'vc` Valid (29 990 steps)**,
  **`unixinodefilesystem___dir_find_free'refn'vc` Valid (2 799 steps)**.
- **(Genuine / non-vacuous — the mandated probe)** injecting `#@ ensures 1 == 0` before the
  `def` → `--fun` **RED ("2 goal(s) remain unproven; Verification FAILED")**. A wrong-result
  falsification `return found` → `return found + 5` → `--fun` **RED**. A milder slot-index
  falsification (`found = i` → `found = i + 1`) makes the direct `'vc` **Unknown (732 566 steps,
  z3)** vs Valid 29 990 on the correct body — IDENTICAL behaviour to the LANDED `_dir_find_slot`
  twin (verified: the landed `_dir_find_slot` also passes `found=i+1` under the `--fun` split but
  blows up the monolithic/direct `'vc`; the `dir_find_*_prefix` predicate is not axiomatized as a
  function of its index, exactly as on the landed twin — the value-fidelity ensures is what the
  de-trust binds, and `ensures 1==0` / `+5` are RED as required).
- **(No collateral regression)** the OTHER dir/write helper `--fun` paths SUCCESS (×2):
  `_dir_find_slot`, `_dir_lookup`, `_write_dir_entry`, `_write_entry` — all SUCCESS ×2.
  `_zero_entry` → **1 Unknown @ 444 882 steps** (×2) = the PRE-EXISTING baseline (clean-main
  contract, identical goal at identical 444 882 steps). Zero new residual.
- **(No relocated trust)** the modular `_dir_find_free` `.mlw`: `field_to_str_read` = 0;
  `trusted` = 0; `abstract` = 0; `_dir_find_free` is a real `let`; the only
  `val unixinodefilesystem___dir_find_free` is the `FindFreeModSig` interface (sig line 90)
  bound by the clone substitution `clone FindFreeModSig with val ... = ...` (line 159), NOT an
  assumed-ensures shim. The 4 `dir_find_free_*` axioms emit ONLY in FindFreeMod (cross-validated).
- **(Corpus byte-diff)** full corpus emission sweep (`--no-typecheck`, half-CPU parallel),
  worktree src vs clean-main src, **604 / 604** `.mlw` emitted, `diff -rq` exit 0 — EVERY corpus
  file byte-IDENTICAL. The specific-prefix gating (`"UnixFs.Dir.dir_find_free"`) kept every
  sibling Dir-citing exhibit byte-identical; no corpus exhibit cites the new free-slot axiom.
  doc-coherency `--check` **GREEN** (no new directive; `verify_module` + `proof` already
  documented across all 5 surfaces).
- **(`\trusted` 2→1)** real `#@ \trusted reviewer:` directives in os module **2 → 1**;
  dirscan-fidelity **1 → 0** (FULLY retired). Only `fd-resolution-fidelity` (sys_open's
  fd-resolution) remains — exactly the last trust the mission named.

---

## 2. What I reused vs. the new cross-validated marker

**Reused (unchanged, from the landed recipe):**
- the `#@ verify_module` module-emission feature (generic over the name → `FindFreeMod` works
  with no code change);
- the per-slot inode keystones `slot_inode_byte_decode` (bridges the two literal slot bytes to
  `slot_inode self.dir 5 i`) and `slot_inode_nonneg` — cited as-is;
- the `clone`-refinement cross-module boundary (`'refn'vc`);
- the §2a trusted-stub axiom-suppression (`_dir_find_free` is now NON-trusted, so nothing is
  suppressed for it; the other trusted+verify_module stubs stay clean);
- the byte-identity prefix-gating discipline (a MORE-SPECIFIC predicate key, emitted only when
  the matching axiom family is cited).
- **NOT reused:** the faithful-NAME EMITTER recognizer / `field_to_str` codec — `_dir_find_free`
  reads only `slot_inode`, never the name field, so no name decode is present. (Simpler twin.)

**New (cross-validated zero-TCB) — the free-slot-index marker family.** `_dir_find_free` returns
the LAST FREE INDEX (guard `slot_inode == 0`), a different value/condition than both
`dir_scan_result` (matched INODE) and `dir_find_slot_result` (last live-match INDEX), so it
needs its own marker — and it carries NO `name` parameter. Authored a Fixpoint `ffscan` (the
FREE-slot dual of `fscan`: on a free slot `found` becomes the index `i`) plus the prefix/result
markers and the load-bearing VALUE lemma
`dir_find_free_result d blk r -> r >= 0 -> slot_inode d blk r = 0`. Four registry axioms
(`dir_find_free_prefix_base`, `dir_find_free_prefix_step`, `dir_find_free_result_intro`,
`dir_find_free_result_value`), two new predicates (`dir_find_free_result`,
`dir_find_free_prefix`, no `name` arg) declared under the MORE-SPECIFIC prefix key
`"UnixFs.Dir.dir_find_free"` (byte-identity gating — emitted only when a `dir_find_free_*`
axiom is cited).

Cross-validated by `test-suite/corpus/pycsl-reference/0722.proofs/{rocq,lean}/UnixDirFindFreeValue.{v,lean}`:

- **Rocq 8.20.1** — every theorem `Print Assumptions … = "Closed under the global context"`
  (Section-Variables-only; 0 Axiom/Admitted):
  `dir_find_free_result_value`, `dir_find_free_result_intro`, `dir_find_free_result_range`,
  `Prefix.dir_find_free_prefix_base`, `Prefix.dir_find_free_prefix_step`,
  `Prefix.dir_find_free_prefix_close`.
- **Lean 4.31.0** — `#print axioms`:
  `dir_find_free_result_intro` / `_prefix_base` / `_prefix_close` "does not depend on any axioms";
  `dir_find_free_result_value` / `_result_range` / `_prefix_step` ⊆ `{propext, Quot.sound}`
  (no `sorryAx`).

No new `\trusted`, no assumed-`val` shim, no uncross-validated axiom.

---

## 3. Evidence (re-ran, bounded `timeout`, ×2 where required)

| gate (`pycsl --fun <fn> pure_lib/os/UnixInodeFileSystem.py`) | run 1 | run 2 |
| --- | --- | --- |
| `…___dir_find_free` (target — modular body path) | SUCCESS | SUCCESS |
| `…___dir_find_slot` | SUCCESS | SUCCESS |
| `…___dir_lookup` | SUCCESS | SUCCESS |
| `…___write_dir_entry` | SUCCESS | SUCCESS |
| `…___write_entry` | SUCCESS | SUCCESS |
| `…___zero_entry` | 1 Unknown @ 444 882 (= baseline) | 1 Unknown @ 444 882 (= baseline) |

- **SENTINEL:** the emitted modular `.mlw` contains `predicate dir_find_free_result` /
  `predicate dir_find_free_prefix`, `module FindFreeMod`, the real `let
  unixinodefilesystem___dir_find_free`, and `clone FindFreeModSig with val … = …` — confirming
  the EDITED worktree emitter ran (PYTHONPATH=$PWD/src:$PWD/src/pycsl override; `import pycsl`
  resolves to the worktree `src`).
- **Baseline (clean-main contract) `--fun …___zero_entry`:** 1 Unknown @ **444 882** — identical
  goal+steps to the patched path → zero new residual.
- **`'vc` + `'refn'vc` (direct `why3 prove -P z3 -t 60`, `-T FindFreeMod`):**
  `…dir_find_free'vc` Valid (29 990), `…dir_find_free'refn'vc` Valid (2 799).
- **Non-vacuity (mandated):** `#@ ensures 1 == 0` before the def → `--fun` RED (2 goals
  unproven). `return found + 5` → `--fun` RED. `found = i + 1` → direct `'vc` Unknown (732 566)
  vs Valid 29 990 (same behaviour as the landed `_dir_find_slot` twin).
- **No-relocated-trust grep (modular `.mlw`):** `field_to_str_read` 0, `trusted` 0, `abstract` 0;
  `_dir_find_free` a real `let`; clone `with val` substitution present; 4 `dir_find_free_*`
  axioms in FindFreeMod only.
- **Corpus byte-diff:** worktree src vs clean-main src, 604/604 `.mlw`, `diff -rq` exit 0 — all
  byte-identical.
- **doc-coherency `--check`:** GREEN.
- **`\trusted` 2→1:** real `#@ \trusted reviewer:` in os module 2→1 (`_dir_find_free` removed);
  dirscan-fidelity 1→0 (FULLY retired).

---

## 4. Files changed (the patch)

- `pure_lib/os/UnixInodeFileSystem.py` — `_dir_find_free`: removed `#@ \trusted`; made the inode
  read faithful (literal slot byte offsets `5*512 + 32*i` so `slot_inode_byte_decode` fires);
  added the free-slot-index marker loop invariant + per-slot/loop-exit asserts; added the 6
  `#@ proof` rocq/lean cites; added `#@ verify_module FindFreeMod`. (Contract ensures UNCHANGED.)
- `src/pycsl/module6_whyml/preamble.py` — added the 4 cross-validated free-slot marker axioms to
  `_AXIOM_REGISTRY`; added the 2 predicate decls under the specific prefix key
  `"UnixFs.Dir.dir_find_free"` (byte-identity gating).
- `test-suite/corpus/pycsl-reference/0722.proofs/{rocq,lean}/UnixDirFindFreeValue.{v,lean}` —
  NEW cross-validation proofs (zero-TCB both provers).

## 5. Human-sign-off note
**Ready to land (proposal).** Re-checkable: (a) per-function gate for `_dir_find_free` (target)
+ the 4 sibling helpers ×2 — target/dir_find_slot/dir_lookup/write_dir_entry/write_entry
SUCCESS, `_zero_entry` at the IDENTICAL pre-existing baseline residual (444 882); (b) `'vc` +
`'refn'vc` Valid + `ensures 1==0` probe RED + `+5` falsification RED; (c) no-relocated-trust
grep; (d) corpus byte-diff exit 0; (e) `\trusted` 2→1, dirscan-fidelity FULLY retired. The new
marker is 4 axioms + 2 predicates, cross-validated zero-TCB on BOTH provers (assumptions outputs
in §2), and the `_dir_find_free` body mirrors the landed `_dir_find_slot` shape — minus the name
decode (simpler twin). NEVER an assumed-`val` shim. After this, only `fd-resolution` (sys_open)
remains.
