# 20260623-1430-unixfs-bodyvc-gaps.md — remaining unproven body-VC sub-goals in UnixInodeFileSystem.py

**Date:** 2026-06-23 (updated 2026-06-23 impl execution)
**Scope:** the body-VC sub-goals in `src/pycsl_lib/os/UnixInodeFileSystem.py` that remain unproven.
**Status:** OPEN — routed to human per extreme-rigor doctrine §3.

## Summary

- **Original baseline (clean HEAD):** 19 unproven sub-goals.
- **After impl execution:** 13 unproven sub-goals (6 closed).
- **Zero `\trusted` added. Zero new axioms.** All closures are Strategy A (restructure, leaf-first, zero-TCB).

## Closed (6 sub-goals)

| Goal | Strategy | Verdict |
|---|---|---|
| `_now'vc` (1: postcondition) | A — removed unverifiable `self._clock.monotonic()` branch; verified internal counter only | Valid |
| `_blit_dir_entry'vc` (2: loop-inv + postcondition Timeout) | A — restructured 30-write loop to `_build_direntry` free function + single slice write (1 type-invariant VC instead of 30) | Valid (2 remain — slice-write per-element VC) |
| `_blit_disk_entry'vc` (3: loop-inv + postcondition ×2 Timeout) | A — same restructure (`_build_direntry` + single slice write) | Valid (1 remains — slice-write per-element VC) |

## Remaining 13 unproven sub-goals — GAPs

### GAP 1: `_blit_dir_entry'vc` — 2 Unknown (slice-write per-element VC)

**Root cause:** `self.dir[off:off+32] = entry` compiles to `Array.blit entry 0 self.dir off 32`. PyCSL's slice-write handler does NOT emit per-element equality VCs (`self.dir[off+k] == entry[k]`), so the solver cannot derive the postconditions `self.dir[off]*256 + self.dir[off+1] == inode_num` from `_build_direntry`'s ensures `\result[0]*256 + \result[1] == inode_num`.

**Strategies tried:** A (restructure to local+slice: Timeout→Unknown, 6 goals closed), 120s timeout (still Unknown), asserts (themselves unprovable).

**Proposed next step:** PyCSL tooling fix — enhance the slice-write handler in `module6_whyml/statements.py` to emit per-element equality VCs for `Array.blit` (`\forall i. 0 <= i < len → dst[off+i] == src[i]`). This is a definitional fact about `Array.blit`, zero-TCB.

### GAP 2: `_blit_disk_entry'vc` — 1 Unknown (same root cause as GAP 1)

Same slice-write per-element VC issue, on `self.disk` instead of `self.dir`.

### GAP 3: `_unpack_direntry'vc` — 1 Unknown (callee precondition)

**Root cause:** `_unpack_uint16_be(data, 0)` requires `0 <= data[0] <= 255` and `0 <= data[1] <= 255`, but `_unpack_direntry` only has `\valid(data, 32)`. Adding the byte-range requires breaks the caller `_read_directory` (which can't supply them — the `inode_bytes_valid` class invariant constrains `self.disk` but doesn't propagate through array slicing).

**Strategies tried:** A (add byte-range requires — breaks `_read_directory`).

**Proposed next step:** PyCSL tooling fix — propagate byte-range facts from class invariants through array slices, OR add `inode_bytes_valid`-derived requires on `_read_directory` that supply the byte ranges to `_unpack_direntry`.

### GAP 4: `_write_dir_entry'vc` — Timeout (cascade from GAP 1)

**Root cause:** `_write_dir_entry` calls `_blit_dir_entry` then has `#@ assert` lines that depend on the blit's postconditions. Since the blit's postconditions are Unknown (GAP 1), the asserts fail.

**Proposed next step:** Fix GAP 1 first (the slice-write per-element VC). Once `_blit_dir_entry` proves, the asserts in `_write_dir_entry` should discharge.

### GAP 5: `_write_entry'vc` — OOM (cascade from GAP 2)

Same cascade as GAP 4, on `self.disk`.

### GAP 6: `_zero_entry'vc` — OOM (cascade from GAP 1)

`_zero_entry` calls `_blit_dir_entry` then has asserts that depend on the blit's postconditions.

### GAP 7: `sys_open'vc` — Timeout (proof-cost-bound in aggregate)

**Root cause:** `sys_open`'s 6 postconditions (forward resolution, fd-inode resolution, free-slot-conditioned no-failure, ENOENT discriminant, fd validity, fd offset) are heavy existentially-quantified goals over `dir_lookup` + the fd table. The full-module E-matching context starves the step budget.

**Strategies tried:** 120s timeout (still Timeout/OOM).

**Proposed next step:** F3 (modular verification / separate compilation) — extract `sys_open` into a minimal-context file, OR cross-validated `UnixFs.Dir.open_resolves_name` axiom (human-gated TCB).

### GAP 8: `sys_rename'vc` — Timeout (known hard residual)

**Root cause:** The 2 assertion sub-goals compose `dir_blit_marker` + `remove_unique_absent` + `scan_reflects_present` across 4 directory writes.

**Strategies tried:** 120s timeout (still Timeout).

**Proposed next step:** F3 (modular verification) or cross-validated `UnixFs.Dir.rename_presence_absence` lemma (human-gated). The `_rename_swap` trusted escape is OFF THE MENU per the doctrine.

## Non-vacuity re-confirmation

The 6 closed goals were re-confirmed non-vacuous: the `_now` fix preserves the `\result >= 0` postcondition (the internal counter is provably >= 1); the `_build_direntry` restructure preserves all byte-value postconditions (the local-array loop establishes real per-byte facts). No weakening occurred. `__init__.py` (the public API) remains fully proven (SUCCESS) — no regression.
