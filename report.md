# PyCSL Verification Report — `pure_lib/os`

**Date:** 2026-06-06  
**Tool version:** PyCSL main @ `35441ec` (with inliner fixes)  
**Provers:** Alt-Ergo 2.6.2, Z3 4.13.3 — 30 s timelimit  
**Memory model:** Hoare  

---

## 1  Overall Results

| Metric | Count | % |
|--------|------:|---:|
| **Valid** | 3 920 | 93.4 |
| Timeout | 72 | 1.7 |
| Unknown | 206 | 4.9 |
| Invalid | 0 | 0.0 |
| **Total VCs** | **4 198** | |

Previous run (before inlining): **67 / 109 Valid (61.5 %)**.  
The inlining pass closes the method-call contract gap (A2c) for
module-level globals, bringing verification from 61 % to 93 %.

---

## 2  Per-Function Breakdown

| Function | Valid | T/O | Unk | Total | Rate |
|----------|------:|----:|----:|------:|-----:|
| write | 183 | 21 | 0 | 204 | 89.7 % |
| makedirs | 868 | 0 | 17 | 885 | 98.1 % |
| open | 631 | 1 | 10 | 642 | 98.3 % |
| listdir | 67 | 0 | 9 | 76 | 88.2 % |
| rename | 157 | 2 | 7 | 166 | 94.6 % |
| scandir | 67 | 0 | 9 | 76 | 88.2 % |
| mkdir | 429 | 0 | 8 | 437 | 98.2 % |
| remove | 396 | 0 | 8 | 404 | 98.0 % |
| unlink | 396 | 0 | 8 | 404 | 98.0 % |
| walk | 23 | 3 | 5 | 31 | 74.2 % |
| link | 34 | 4 | 3 | 41 | 82.9 % |
| chmod | 22 | 2 | 2 | 26 | 84.6 % |
| readlink | 13 | 0 | 4 | 17 | 76.5 % |
| rmdir | 190 | 0 | 4 | 194 | 97.9 % |
| truncate | 22 | 1 | 2 | 25 | 88.0 % |
| access | 11 | 1 | 1 | 13 | 84.6 % |
| symlink | 144 | 1 | 1 | 146 | 98.6 % |
| lseek | 104 | 0 | 1 | 105 | 99.0 % |
| read | 52 | 0 | 1 | 53 | 98.1 % |
| lstat | 10 | 0 | 1 | 11 | 90.9 % |
| stat | 10 | 0 | 1 | 11 | 90.9 % |
| _filesystem (init) | 12 | 0 | 1 | 13 | 92.3 % |
| close | 12 | 0 | 0 | 12 | 100 % |
| dup | 19 | 0 | 0 | 19 | 100 % |
| fstat | 6 | 0 | 0 | 6 | 100 % |
| direntry_is_dir | 3 | 0 | 0 | 3 | 100 % |
| direntry_is_file | 3 | 0 | 0 | 3 | 100 % |
| direntry_is_symlink | 3 | 0 | 0 | 3 | 100 % |
| unixinodefilesystem | 13 | 0 | 0 | 13 | 100 % |

**Fully proven functions (100 %):**
`close`, `dup`, `fstat`, `direntry_is_dir`, `direntry_is_file`,
`direntry_is_symlink`, `unixinodefilesystem` (record witness).

---

## 3  Failure Classification

| Sub-goal category | Count | % of failures |
|--------------------|------:|--------------:|
| Index in array bounds | 45 | 32.4 % |
| Precondition | 36 | 25.9 % |
| Postcondition | 33 | 23.7 % |
| Loop invariant preservation | 22 | 15.8 % |
| Loop variant decrease | 3 | 2.2 % |
| **Total** | **139** | |

*(Note: each failure spawns two VC attempts — one per prover — so 278 failing
VC lines correspond to 139 distinct sub-goals.)*

---

## 4  Root Cause Analysis

### 4.1  Disk initialisation: `Array.make 0 0` (Critical — 1 root cause, ~60 VCs affected)

The `_filesystem` global is emitted as:

```whyml
let _filesystem : unixinodefilesystem = {
  disk = (Array.make 0 0); ...
}
```

The class invariant requires `Array.length disk >= 131072`, but `__init__`
constructs `bytearray(num_blocks * self.BLOCK_SIZE)` which PyCSL cannot
evaluate (it contains a runtime parameter `num_blocks` and a class constant
`self.BLOCK_SIZE`). It falls back to a 0-element array.

**Impact:** The invariant is immediately violated at construction, so every
function that indexes into `_filesystem.disk` (most of them) produces
unprovable "Index in array bounds" and "Precondition" sub-goals for
`Array.sub` / `Array.blit` calls.

**Fix:** Rewrite `__init__` to use a literal size that PyCSL can evaluate:
```python
self.disk: list = bytearray(131072)  # 256 * 512
```
Or extend PyCSL to evaluate `self.NUM_BLOCKS * self.BLOCK_SIZE` as a
compile-time constant when both `NUM_BLOCKS` and `BLOCK_SIZE` are class-level
int constants.

### 4.2  Missing `ensures \length(\result) == 18` on `_unpack_inode` (Medium — ~20 VCs)

The class method stub `unixinodefilesystem___read_inode` has the contract
`ensures { Array.length result = 18 }`, but the module-level helper
`_unpack_inode` (used after inlining) only has `ensures { true }`.

After inlining, `inode = _unpack_inode(data)` produces a result of unknown
length, so `inode[2]` and `inode[8]` fail bounds checks.

**Fix:** Add `#@ ensures \length(\result) == 18` to `_unpack_inode` in
`UnixInodeFileSystem.py`.

### 4.3  Missing `ensures \length(\result) == 2` on `_pack_uint16_be` and similar (Medium — ~10 VCs)

Pack functions return arrays whose lengths are needed for `Array.blit`
bounds proofs.  Their current contract is `ensures True`.

**Fix:** Add length postconditions:
- `_pack_uint16_be`: `ensures \length(\result) == 2`
- `_pack_uint32_be`: `ensures \length(\result) == 4`
- `_pack_inode`: `ensures \length(\result) == 64`
- `_pack_direntry`: `ensures \length(\result) == 32`

### 4.4  Loop invariant in `_dir_lookup` is too weak for bounds proof (Medium — ~15 VCs)

The inlined `_dir_lookup` loop has:
```whyml
invariant { 0 <= !_idx_i && !_idx_i <= 16 }
invariant { !found == -1 || (!found >= 0 && !found < 32) }
```

But the loop body does `Array.sub _filesystem.disk offset (offset + 32)`
which needs `offset + 32 <= Array.length _filesystem.disk`. The invariant
doesn't carry the relationship between `offset` and `_filesystem.disk`
length, and with the disk size unknown (§4.1), the prover can't close it.

**Fix:** Primarily blocked by §4.1. Once disk size is fixed, an invariant
like `offset >= 0 && offset + 16 * 32 <= Array.length _filesystem.disk`
may be needed, or the existing `block_num < 256` precondition + disk size
= 131072 should suffice.

### 4.5  `write` function: deep inlining creates 200+ VCs (Low — 21 VCs)

`write` → `sys_write` is the most complex inlined function: it contains
nested loops (`block write loop` inside `main write loop`), inode updates,
bitmap operations, and `_write_inode` calls.  The resulting VC is very large
(the `write` function alone produces 204 VCs).  21 of these time out at 30 s,
mostly on:
- **Array bounds** for `Array.blit` on `_filesystem.disk` (blocked by §4.1)
- **Loop invariant preservation** for the write loop's `fd_offset` tracking
- **Preconditions** for `_pack_inode` and `Array.blit` length arguments

### 4.6  `walk` loop variant: `16 - i` with `iter_length !names` (Low — 3 VCs)

```whyml
while !_idx_i < (iter_length !names) do
  variant { (16 - !_idx_i) }
```

The variant `16 - i` assumes `names` has at most 16 elements, but
`iter_length` is abstract (opaque), so Why3 can't prove
`iter_length !names <= 16` → can't prove the variant decreases to 0.

**Fix:** Either replace `iter_length` with a concrete `Array.length`
(requires `names` to be array-typed), or add an axiom / precondition
bounding `iter_length !names <= 16`.

### 4.7  Postcondition propagation for `open` (Low — 10 VCs)

`open` has `ensures { result == -1 || result >= 3 }`.  After inlining
`sys_open` (which allocates an fd via `_alloc_fd`), the prover must trace
through the full fd-allocation loop and inode setup to conclude the result
is either -1 or ≥ 3.  With 642 VCs total and 10 failures, the postcondition
is almost proven but a few branches (error paths) are too complex.

---

## 5  Recommended Fix Priority

| Priority | Fix | Affected VCs | Effort |
|----------|-----|-------------|--------|
| **P0** | Fix disk init size (§4.1) | ~60 | 1 line in `__init__` |
| **P1** | Add `\length` ensures on `_unpack_inode` (§4.2) | ~20 | 1 line |
| **P1** | Add `\length` ensures on `_pack_*` helpers (§4.3) | ~10 | 4 lines |
| **P2** | Fix `walk` loop variant (§4.6) | 3 | Moderate |
| **P3** | Strengthen `write` invariants (§4.5) | 21 | Complex |
| **P3** | Strengthen `open` postcondition path (§4.7) | 10 | Complex |

**Estimated improvement after P0 + P1:** ~90 additional VCs proven →
**~4010 / 4198 (95.5 %+)**.

---

## 6  PyCSL Tool Fixes Applied This Session

| File | Fix | Impact |
|------|-----|--------|
| `ir_inline.py` | Freshen dotted func strings (`entries.append` → `entries__inlN.append`) | Prevented wrong-variable array writes |
| `ir_inline.py` | Add `String` to simple actuals | Prevented string-to-int ref assignment |
| `types.py` | Extend `_field_type_of` for module-global fields | Enabled array subscript on `_filesystem.fd_open[fd]` |
| `types.py` | Seed-based transitive array propagation | Enabled `entries = _inl_res = arr_local` chain |
| `statements.py` | Pass IRScanner seed to `_collect_array_var_assigns` | Cross-collector type propagation |
| `pycsl.py` | Import module-level helper functions | Enabled `_unpack_direntry` etc. in inlined code |

---

## 7  OS Module Changes Applied This Session

| File | Change | Reason |
|------|--------|--------|
| `UnixInodeFileSystem.py` | `_pack_*` return type `bytes` → `list` | PyCSL maps `list` to `array int` |
| `UnixInodeFileSystem.py` | `ensures \result >= 0` → `ensures True` on pack functions | Can't compare `array int >= 0` |
| `UnixInodeFileSystem.py` | Added `\valid(data, N)` contracts on helpers | Correct array parameter typing |
| `UnixInodeFileSystem.py` | Rewrote `_set_bitmap` to avoid `~` operator | PyCSL has no bitwise NOT |
| `__init__.py` | Rewrote `listdir`/`scandir` to scan directly | Avoid tuple-in-array limitation |
| `__init__.py` | Added `data: list` annotation on `write` | Correct array parameter propagation |

---

## 8  Conclusion

The inlining approach is a decisive success: it closes the A2c gap and
brings proof coverage from 61 % to 93 %.  The remaining 7 % of failures
are dominated by a single fixable root cause (disk initialisation size)
plus missing length postconditions on helper functions.  With the P0 + P1
fixes (estimated 5 lines of annotation), coverage should exceed 95 %.

The deeper failures in `write` (21 VCs) and `open` (10 VCs) arise from
the sheer size of the inlined verification conditions and may benefit from
modular verification strategies (verify `sys_write` independently, then
use its contract at the `os.write` call site) once PyCSL's contract
propagation for module globals is extended.
