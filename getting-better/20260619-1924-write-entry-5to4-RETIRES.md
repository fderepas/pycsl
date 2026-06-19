# `_write_entry` dirscan-fidelity `\trusted` retirement — os `\trusted` 5 → 4

**Result: RETIRES.** `_write_entry` is de-trusted via a cross-validated, zero-TCB
block-parameterized unique-marker fold. FULL body gate ×2 green for `_write_entry`
(0 non-Valid, both runs), residual ≤ baseline (the `sys_rename` Assertion), landed
retirements intact, full-corpus byte-diff = only os changes, `__init__` gate SUCCESS.

This is a STOP-AT-PROPOSAL writeup. Nothing is committed; the de-trust is NOT in the
tree. The full edit is staged-and-captured at
`getting-better/PROPOSAL-write-entry-detrust.patch`. The parent re-runs the FULL gate
×2 + four probes + recompiles the proofs + confirms the landed retirements before
bringing the TCB decision to the human.

---

## 1. The target and the key difference

`_write_entry` (`pure_lib/os/UnixInodeFileSystem.py`) writes a 32-byte directory entry
at `slot` of an **ARBITRARY block `block_num`** of `self.disk` (it seeds the `.`/`..`
loopback entries of a fresh subdirectory data block in `sys_mkdir`). Its ensures
reference `slot_inode(self.disk, block_num, slot)` / `slot_name(self.disk, block_num,
slot)` over an arbitrary block.

The two landed retirements (`_write_dir_entry`, `_zero_entry`) mutate `self.dir` and
are **hardcoded to block 5** — their cross-validated marker family (`dir_blit_marker`,
0716 `DirBlitMarker.{v,lean}`) bakes in block 5 (offset `2560 = 5*512`, conclusions
`slot_inode d1 5 s`). That family does NOT apply to an arbitrary block. The mission was
to GENERALIZE it.

## 2. The generalization — `dir_blit_marker_at` (block-parameterized marker)

New cross-validated kernel: `test-suite/corpus/pycsl-reference/0718.proofs/{rocq,lean}/DirBlitMarkerAt.{v,lean}`.
It is the block-5 family with the constant `5` replaced by a variable `blk` everywhere
it is the *mutated block*: the marker's `slot_off blk s` byte pins and the byte-region
frame base `blk*512`, and the corollary conclusions `slot_inode/slot_name d1 blk s`.
`slot_off`/`slot_inode`/`slot_name`/`field_to_str`/`name_val` are already generic over
the block argument, so this is the SAME proof with `5 → blk`. The block-5 theorems are
the `blk := 5` instances.

Four theorems (exactly what `_write_entry`'s VALUE+FRAME ensures need — NOT a block-5
`insert`, because `_write_entry` does not maintain the block-5 `uniq`/`slots_lt32`
directory-uniqueness invariants, which are `self.dir`/block-5 facts):

- `dir_blit_marker_at_intro` — byte facts → marker (DEFINITIONAL, zero trust).
- `dir_blit_marker_at_value_inode` — `slot_inode d1 blk s = 256*b0+b1`.
- `dir_blit_marker_at_value_name` — `slot_name d1 blk s = name` (byte round-trip,
  discharged INSIDE the kernel — the os body never materializes the string codec).
- `dir_blit_marker_at_frame_only` — `∀k≠s`: `slot_inode/slot_name d1 blk k` unchanged.

WhyML axioms added to `_AXIOM_REGISTRY` (`src/pycsl/module6_whyml/preamble.py`):
`UnixFs.Dir.dir_blit_marker_at_{intro,value_inode,value_name,frame_only}`, keyed
`[dir_blit_marker_at d0 d1 blk s b0 b1 name]` (a UNIQUE trigger — fires ONLY at the
asserted marker atom, never on a raw `disk[...]` byte read).

### Cross-validation (zero-TCB, both provers)

Rocq (`coqc DirBlitMarkerAt.v`, `Print Assumptions`): all four — **Section Variables
only** (Closed under the global context; 0 axioms).

Lean (`lean DirBlitMarkerAt.lean`, `#print axioms`):
```
dir_blit_marker_at_intro       does not depend on any axioms
dir_blit_marker_at_value_inode does not depend on any axioms
dir_blit_marker_at_value_name  depends on axioms: [propext, Quot.sound]
dir_blit_marker_at_frame_only  depends on axioms: [propext, Quot.sound]
```
i.e. ⊆ {propext, Quot.sound}. Zero-TCB on both.

## 3. The de-trusted body

`_write_entry` loses `#@ \trusted reviewer: dirscan-fidelity`, cites the four
`dir_blit_marker_at_*` axioms, and:
1. blits via a new pure-byte helper `_blit_disk_entry` (the `self.disk` twin of
   `_blit_dir_entry`; opaque off → no slot-web axiom matches its loop);
2. materializes each marker antecedent as its OWN cheap assert (robustness lever) —
   inode-byte sum, per-char name bytes, **single-point** null-pad, block-`blk`
   byte-region frame — all in `entry_offset` form to match the helper's `off`-keyed
   ensures, with a one-line arithmetic bridge `entry_offset == block_num*512 + 32*slot`;
3. folds the UNIQUE `dir_blit_marker_at` atom; the value_inode + value_name +
   frame_only corollaries discharge the four ensures in marker-keyed steps.

Robustness fix history (this run): the first attempt timed out (4.23M steps) on the
null-pad assert — the `∀i` instantiation at the symbolic `block_num*512+...` index
E-match-exploded. Fixed by (a) a single-point null-pad ensures on `_blit_disk_entry`
(no `∀` instantiation in `_write_entry`), and (b) stating the byte asserts in
`entry_offset` form. After the fix `_write_entry`'s heaviest goal is **58760 steps**
(≈5× under the ~300K edge).

## 4. FULL body gate ×2 evidence (the authoritative measure)

`PYTHONHASHSEED=0 pycsl.py pure_lib/os/UnixInodeFileSystem.py` (full module, not `--fun`):

| run | `_write_entry` goals | `_write_entry` non-Valid | max steps | total unproven (whole module) |
|-----|----------------------|--------------------------|-----------|-------------------------------|
| baseline (HEAD, trusted) | n/a (trusted) | — | — | **2** (both `sys_rename` Assertion) |
| FG1 (de-trusted)         | 11 | **0** | 58760 | 1 (`sys_rename` Assertion) |
| FG2 (de-trusted)         | 11 | **0** | 58760 | 1 (`sys_rename` Assertion) |

- `_write_entry`: 0 non-Valid in BOTH runs, with margin.
- Residual is the **baseline `sys_rename` Assertion** (the documented residual). Both
  de-trusted runs show ≤ baseline (1 ≤ 2; the baseline's second `sys_rename` timeout is
  prover nondeterminism, not introduced by the de-trust).
- Per-helper scan (both runs): the ONLY non-Valid goal in the whole module is in
  `sys_rename` — no relocated explosion anywhere.

### Landed retirements intact (both runs)
`_write_dir_entry`: 0 non-Valid. `_zero_entry`: 0 non-Valid. `_blit_disk_entry` (new
helper): 0 non-Valid.

### `__init__` gate
`pycsl.py pure_lib/os/__init__.py` → **SUCCESS, 0 non-Valid, exit 0.**

## 5. Four genuineness probes (single-probe injections, `--fun` judged on the probe goal)

| # | probe | expected | observed |
|---|-------|----------|----------|
| 1 | consistency: `(inode_num≠0 and <32) ==> 1==0` | Unknown/FAILED (not vacuous) | **FAILED — 2 goals unproven** ✓ |
| 2 | value: clean `slot_inode==inode_num`, `slot_name==name` | Valid | **Valid (--fun + FG1/FG2)** ✓ |
| 3 | value-falsif: `slot_inode == inode_num + 1` | RED | **FAILED — 1 goal unproven** ✓ |
| 4 | frame-falsif: drop `k != slot` (claims mutated slot framed) | RED | **FAILED — 1 goal unproven** ✓ |

Probe 1 is the vacuity check (the in-place-blit `\old(self.disk)==self.disk` collapse
risk): the de-trusted body is NOT vacuously false. All four probes reverted after use.

## 6. Corpus inertness — byte-diff = only os changes

The new `dir_blit_marker_at` predicate declaration would, under the naive emission rule
(emit all `UnixFs.Dir.` decls whenever any `UnixFs.Dir.*` axiom is cited), leak a `+1`
line into the two corpus modules that cite `UnixFs.Dir.*` (0711, 0712). Fixed by
**gating**: the predicate is keyed under the more-specific prefix
`"UnixFs.Dir.dir_blit_marker_at"`, so it is emitted ONLY when a `dir_blit_marker_at*`
axiom is cited (the os module), never for a bare `scan_reflects_present` citation.

Full-corpus byte-diff (HEAD preamble vs proposed preamble, all 604 emitting `.py` of
668): **ALL CORPUS `.mlw` IDENTICAL.** The os module emits `dir_blit_marker_at` (10
occurrences: 1 decl + 4 axioms + body uses).

`bin/doc-coherency.py --check`: **in sync (exit 0)** — no `#@` directive surface
changed (the additions are proof-citable lemma names = registry values, not directives).

## 7. `\trusted` 5 → 4

`#@ \trusted` directive count in `pure_lib/os/UnixInodeFileSystem.py`: **5 → 4**.
Removed: `_write_entry`'s `\trusted reviewer: dirscan-fidelity`. Remaining 4: three
`dirscan-fidelity` (`_dir_lookup` and the two read-side scan bindings) + one
`fd-resolution-fidelity` (`sys_open`).

## 8. Files in the proposal (`PROPOSAL-write-entry-detrust.patch`, 4 source files)

- `pure_lib/os/UnixInodeFileSystem.py` — de-trust `_write_entry` + new `_blit_disk_entry`.
- `src/pycsl/module6_whyml/preamble.py` — 4 `dir_blit_marker_at_*` axioms + gated predicate decl.
- `test-suite/corpus/pycsl-reference/0718.proofs/rocq/DirBlitMarkerAt.v` — Rocq cross-validation.
- `test-suite/corpus/pycsl-reference/0718.proofs/lean/DirBlitMarkerAt.lean` — Lean cross-validation.

## 9. Human sign-off note

This proposal removes one human-reviewed `dirscan-fidelity` trust clause (the
arbitrary-block write-side decode↔bytes correspondence) and replaces it with
machine-proven, dual-prover-cross-validated, zero-TCB block-parameterized marker
corollaries. The on-disk-bytes ↔ abstract-decode correspondence that the reviewer used
to vouch for is now discharged inside the 0718 kernel proof (the `5 → blk`
generalization of the already-landed 0716 block-5 proof). **Recommended for the human
TCB decision** after the parent's independent re-verification.
