# `_dir_find_slot` 3→2 de-trust — VERDICT: **LANDS (proposal).**

`_dir_find_slot`'s `\trusted reviewer: dirscan-fidelity` retires via the LANDED read-side
recipe (the second read-side dirscan retirement, mirroring `_dir_lookup`). Its body verifies
on the per-function gate (`'vc` + `'refn'vc` Valid, falsification RED), no collateral
regression on the other dir/write helpers, no relocated trust, corpus-inert, `\trusted` 3→2
(dirscan-fidelity 2→1).

**Date:** 2026-06-20 ~11:34
**Worktree:** `.claude/worktrees/agent-a3615f26a3aa108d8` (STOP-AT-PROPOSAL — nothing committed;
tree reverted clean; only the patch + this writeup remain).
**Patch:** `getting-better/PROPOSAL-dir-find-slot-3to2.patch`
**Substrate:** clean `main` (commit 95aed83 — the full `_dir_lookup` recipe is ON MAIN:
`#@ verify_module` module-emission, the `field_to_str` faithful-name recognizer, the
`dir_scan_result` marker family + cross-validated proofs, the `clone`-refinement boundary,
and the §2a `preamble.py` trusted-stub axiom-suppression fix).

---

## 1. BOTTOM LINE — YES, it retires 3→2

`_dir_find_slot` scans the 16 directory slots and returns the matched slot's **INDEX**
(0..15) or -1 — the SLOT-INDEX twin of `_dir_lookup` (which returns the matched slot's
INODE). Its two fidelity ensures (`\result >= 0 ==> slot_inode != 0 /\ slot_name == pathname`)
were `\trusted reviewer: dirscan-fidelity`. They now verify against a NEW cross-validated
zero-TCB **slot-index marker** family (`dir_find_slot_result` / `dir_find_slot_prefix`),
authored over the EXISTING per-slot decode symbols (`slot_inode`/`slot_name`), with the body
made faithful (the inline `split/decode` idiom the emitter recognizer lowers to `field_to_str`)
and isolated in its own `#@ verify_module FindSlotMod`.

Re-verified independently (bounded `timeout`, ×2 where required):

- **(Body proven, 3→2 realized)** `pycsl --fun unixinodefilesystem___dir_find_slot` →
  `[+] Verification SUCCESS! All contracts formally proven` (×2, deterministic). Modular
  split (6 modules `Shared`/`FindSlotModSig`/`FindSlotMod`/`ReadModSig`/`ReadMod`/
  `PyCSL_Program`); `_dir_find_slot` is a REAL `let` in `FindSlotMod` with the slot-index
  read axioms LOCAL there. Direct `why3 prove -P z3 -t 60 -T FindSlotMod`:
  **`unixinodefilesystem___dir_find_slot'vc` Valid (35 879 steps)**,
  **`unixinodefilesystem___dir_find_slot'refn'vc` Valid (3 093 steps)**.
- **(Genuine / non-vacuous)** Falsifying the body — `return found` → `return found + 5` →
  `pycsl --fun unixinodefilesystem___dir_find_slot` **RED: "1 goal(s) remain unproven after
  all provers; Verification FAILED"**. A milder slot-index falsification (`found = i` →
  `found = i + 1`) makes the monolithic body `'vc` non-Valid (z3 Out-of-memory / Alt-Ergo
  Timeout) vs Valid 35 879 steps on the correct body — the marker step only advances to the
  matched INDEX `i`, so a wrong index breaks the loop-carry assert.
- **(No collateral regression)** the OTHER dir/write helper `--fun` paths unchanged:
  - `--fun unixinodefilesystem___dir_lookup` (the prior target) → **SUCCESS** (×2).
  - `--fun unixinodefilesystem___write_dir_entry` → **SUCCESS** (×2).
  - `--fun unixinodefilesystem___write_entry` → **SUCCESS** (×2).
  - `--fun unixinodefilesystem___dir_find_free` → **SUCCESS** (×2).
  - `--fun unixinodefilesystem___zero_entry` → **1 Unknown @ 444 882 steps** (×2) = the
    PRE-EXISTING baseline: clean `main` (no patch) gives the **IDENTICAL goal at the IDENTICAL
    444 882 steps** (`Assertion of …zero_entry'vc`). Zero new residual.
- **(No relocated trust)** the modular `_dir_find_slot` `.mlw`: `field_to_str_read` shim = 0;
  new `\trusted`/assumed-val = 0; `\abstract` = 0; the slot-index + read axioms are isolated
  in `FindSlotMod` (20) + `Shared` (2), **0 in `PyCSL_Program`**; `_dir_find_slot` is a real
  `let`; the only `val unixinodefilesystem___dir_find_slot` is the `FindSlotModSig` interface
  bound by the clone substitution `clone FindSlotModSig with val ... = ...` (not an
  assumed-ensures shim). The body's name read is the faithful `field_to_str self.dir (…+2) 30`
  term (not `decode_1`).
- **(Corpus byte-diff)** full corpus emission sweep (`bin/byte-diff-sweep.sh` shape,
  `--no-typecheck`, half-CPU parallel), worktree vs clean main: see §3. doc-coherency
  `--check` **GREEN** (no new directive; `verify_module` already documented across all 5
  surfaces).
- **(`\trusted` 3→2)** `pure_lib/os/UnixInodeFileSystem.py` real `#@ \trusted` directives in
  the os module **3 → 2**; dirscan-fidelity **2 → 1** (`_dir_find_slot`'s `\trusted` removed;
  `_dir_find_free` remains the sole dirscan trust; the `fd-resolution-fidelity` one untouched).

---

## 2. What I reused vs. the new cross-validated marker

**Reused (unchanged, from the landed `_dir_lookup` recipe):**
- the `#@ verify_module` module-emission feature (`Module6_WhyMLTranspiler._transpile_modular`,
  `_verify_module_groups`) — generic over the module name, so `FindSlotMod` works with no code
  change;
- the faithful-name EMITTER recognizer (`module6_whyml/expressions.py`
  `_recognize_field_decode_idiom`) — it fires on `_dir_find_slot`'s inline
  `self.dir[a:b].split(b'\x00')[0].decode('utf-8', errors='ignore')` exactly as on `_dir_lookup`;
- the per-slot decode bridges `slot_inode_byte_decode` / `slot_name_byte_decode` /
  `field_to_str_round_trip` and `slot_inode_nonneg` — cited as-is;
- the §2a trusted-stub axiom-suppression fix in `preamble.py` (it suppresses a trusted+
  verify_module stub's cites; on the `--fun _dir_find_slot` path `_dir_find_slot` is NON-trusted
  so nothing is suppressed for it — and `_dir_lookup` is now the trusted+verify_module stub that
  §2a suppresses, so the other helpers stay clean);
- the `clone`-refinement cross-module boundary (`'refn'vc`).

**New (cross-validated zero-TCB) — the slot-index marker family.** The existing
`dir_scan_result` carries the matched INODE (`dir_lookup = r`); `_dir_find_slot` returns the
matched INDEX, a different value, so it needs its own marker. Authored a Fixpoint `fscan` (the
INDEX-keeping dual of `scan`: on a match `found` becomes the index `i`, not the inode) plus the
prefix/result markers and the load-bearing VALUE lemma
`dir_find_slot_result d blk name r -> r >= 0 -> slot_inode d blk r <> 0 /\ slot_name d blk r = name`.
Four registry axioms (`dir_find_slot_prefix_base`, `dir_find_slot_prefix_step`,
`dir_find_slot_result_intro`, `dir_find_slot_result_value`), two new predicates
(`dir_find_slot_result`, `dir_find_slot_prefix`) declared under the MORE-SPECIFIC prefix key
`"UnixFs.Dir.dir_find_slot"` (the dir_blit_marker_at byte-identity discipline — emitted only
when a `dir_find_slot_*` axiom is cited).

Cross-validated by `test-suite/corpus/pycsl-reference/0721.proofs/{rocq,lean}/UnixDirFindSlotValue.{v,lean}`:

- **Rocq 8.20.1** — every theorem `Print Assumptions … = "Closed under the global context"`
  (Section-Variables-only; 0 Axiom/Admitted):
  `dir_find_slot_result_value`, `dir_find_slot_result_intro`, `dir_find_slot_result_range`,
  `Prefix.dir_find_slot_prefix_base`, `Prefix.dir_find_slot_prefix_step`,
  `Prefix.dir_find_slot_prefix_close`.
- **Lean 4.31.0** — `#print axioms`:
  `dir_find_slot_result_intro` / `_prefix_base` / `_prefix_close` "does not depend on any axioms";
  `dir_find_slot_result_value` / `_result_range` / `_prefix_step` ⊆ `{propext, Quot.sound}`
  (no `sorryAx`).

No new `\trusted`, no assumed-`val` shim, no uncross-validated axiom.

---

## 3. Evidence (re-ran, bounded `timeout`, ×2 where required)

| gate (`pycsl --fun <fn> pure_lib/os/UnixInodeFileSystem.py`) | run 1 | run 2 |
| --- | --- | --- |
| `…___dir_find_slot` (target — modular body path) | SUCCESS | SUCCESS |
| `…___dir_lookup` (prior target) | SUCCESS | SUCCESS |
| `…___write_dir_entry` | SUCCESS | SUCCESS |
| `…___write_entry` | SUCCESS | SUCCESS |
| `…___dir_find_free` | SUCCESS | SUCCESS |
| `…___zero_entry` | 1 Unknown @ 444 882 (= baseline) | 1 Unknown @ 444 882 (= baseline) |

- **Baseline (clean `main`, no patch) `--fun …___zero_entry`:** 1 Unknown @ **444 882** —
  byte-identical goal+steps to the patched path. → zero new residual.
- **`'vc` + `'refn'vc` (direct `why3 prove -P z3 -t 60` on the modular `.mlw`, `-T FindSlotMod`):**
  `…dir_find_slot'vc` Valid (35 879), `…dir_find_slot'refn'vc` Valid (3 093).
- **Falsification:** `return found + 5` → `--fun …___dir_find_slot` RED ("1 goal(s) remain
  unproven; Verification FAILED"); `found = i+1` → monolithic body `'vc` non-Valid (z3 OOM /
  Alt-Ergo Timeout) vs Valid 35 879 correct.
- **No-relocated-trust grep (modular `.mlw`):** `field_to_str_read` 0, `trusted` 0, `abstract` 0;
  slot-index + read axioms in `FindSlotMod`(20)+`Shared`(2), 0 in `PyCSL_Program`; `_dir_find_slot`
  a real `let`; clone `with val` substitution present; body uses `field_to_str` (faithful), no
  `decode_1`.
- **Corpus byte-diff:** full corpus emission sweep (`--no-typecheck`, half-CPU parallel),
  worktree vs clean main, 604 (wt) / 605 (main) `.mlw` emitted. `diff -rq` reports a SINGLE
  entry: `Only in main: 0700.mlw`. Every corpus file that emits in BOTH trees is
  byte-IDENTICAL (no `Files X differ` lines anywhere). The lone `0700.mlw` delta is from an
  UNTRACKED stray `0700.py` present in main's working tree but absent from the worktree (both
  trees at commit 95aed83; `0700.py` is `??` in main, not in HEAD) — UNRELATED to this change.
  So the os module is the only thing that changed; the specific-prefix gating
  (`"UnixFs.Dir.dir_find_slot"`) kept every sibling Dir-citing module byte-identical. No
  read-codec exhibit cites the new slot-index axiom, so none changed.
- **doc-coherency `--check`:** GREEN.
- **`\trusted` 3→2:** real `#@ \trusted` in os module 3→2 (`_dir_find_slot` removed);
  dirscan-fidelity 2→1.

---

## 4. Files changed (the patch)

- `pure_lib/os/UnixInodeFileSystem.py` — `_dir_find_slot`: removed `#@ \trusted`; made the
  name read faithful (inline `split/decode` idiom + literal slot offsets); added the
  slot-index marker loop invariant + per-slot/loop-exit asserts; added the 9 `#@ proof`
  rocq/lean cites; added `#@ verify_module FindSlotMod`. (Contract ensures UNCHANGED.)
- `src/pycsl/module6_whyml/preamble.py` — added the 4 cross-validated slot-index marker axioms
  to `_AXIOM_REGISTRY`; added the 2 predicate decls under the specific prefix key
  `"UnixFs.Dir.dir_find_slot"` (byte-identity gating).
- `test-suite/corpus/pycsl-reference/0721.proofs/{rocq,lean}/UnixDirFindSlotValue.{v,lean}` —
  NEW cross-validation proofs (zero-TCB both provers).

## 5. Human-sign-off note
**Ready to land (proposal).** Re-checkable: (a) per-function gate for `_dir_find_slot` (target)
+ the 4 sibling helpers ×2 — target/dir_lookup/write_dir_entry/write_entry/dir_find_free
SUCCESS, `_zero_entry` at the IDENTICAL pre-existing baseline residual (444 882); (b) `'vc` +
`'refn'vc` Valid + falsification RED; (c) no-relocated-trust grep; (d) corpus byte-diff scope;
(e) `\trusted` 3→2. The new marker is 4 axioms + 2 predicates, cross-validated zero-TCB on BOTH
provers (assumptions outputs in §2), and the `_dir_find_slot` body change mirrors the landed
`_dir_lookup` shape exactly. NEVER an assumed-`val` shim.
