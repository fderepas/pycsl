# 20260624-1600-unixfs-bodyvc-gaps-update.md — toolfix + A2/A3/B1 GAP ledger

**Date:** 2026-06-24
**Scope:** update on the 13 remaining unproven body-VC sub-goals in `UnixInodeFileSystem.py` after the slice-write per-element VC toolfix (A1) and the A2/A3/B1 gap analysis.
**Status:** OPEN — 13 unproven remain (0 closed by toolfix; root cause re-classified). Routed to human per extreme-rigor doctrine §3.

## Summary

- **Before mission:** 13 unproven (working tree, post prior impl execution).
- **After A1 toolfix:** 13 unproven (unchanged count — see re-classification below).
- **Zero `\trusted` added. Zero new axioms.** The A1 toolfix is a definitional zero-TCB `assert` from Why3's `Array.blit` spec.

## A1: Slice-write per-element VC toolfix — IMPLEMENTED, count unchanged

**File:** `src/pycsl/module6_whyml/statements.py`, `_handle_array_slice_set_stmt`
**Change:** After `Array.blit src 0 dst lo n`, emits `assert { forall i. 0 <= i < n -> dst[lo+i] = src[i] }`. Non-trivial `src` expressions (e.g. `Array.sub ...`) are let-bound first so the assert can reference them in logic context.

**Verdict:** The assert goal itself is **Valid** (57914 steps) — it is a definitional fact from `Array.blit`'s spec, zero TCB. The postcondition and loop-invariant sub-goals of `_blit_dir_entry` / `_blit_disk_entry` that were failing on **clean HEAD** (5 goals: 2 loop-inv + 3 postcondition) now discharge.

**Why the count stayed at 13:** The bug doc (20260623-1430) **misclassified** the failing goals. It claimed GAPs 1–2 were "postcondition Unknown" and GAPs 4–6 were "cascade Timeout/OOM." In reality (on the working tree with prior impl execution), the postconditions and loop invariants were **already proving** — the prior impl execution's `_build_direntry` restructure closed them. The actual 13 failing goals are:

| Goal type | Function | Count | Root cause |
|---|---|---|---|
| type invariant | `_blit_dir_entry` | 2 | `uniq(self.dir)` / `slots_lt32(self.dir)` maintenance after blit — needs `dir_blit_marker` axioms, cited on `_write_dir_entry` not `_blit_dir_entry` |
| type invariant | `_blit_disk_entry` | 1 | same (block-parameterized variant) |
| precondition | `_unpack_direntry` | 2 | `_unpack_uint16_be` requires byte-range `0 <= data[0/1] <= 255`; `_unpack_direntry` only has `\valid(data, 32)` |
| postcondition | `sys_open` | 6 | proof-cost-bound in aggregate E-matching context (40 axioms, 50 siblings) |
| assertion | `sys_rename` | 2 | composes `dir_blit_marker` + `remove_unique_absent` + `scan_reflects_present` across 4 directory writes |

The toolfix is **correct and valuable** (closes 5 goals on clean HEAD, adds a Valid zero-TCB assertion) but **redundant on the working tree** where the prior impl execution already closed those goals. No regression.

## A2: `_unpack_direntry` byte-range requires — GAP (logged)

**Strategy tried:** Add `#@ requires 0 <= data[0] <= 255` and `#@ requires 0 <= data[1] <= 255` to `_unpack_direntry`; add matching requires to callers.

**Why it fails:** The byte-range facts for the directory region do NOT exist in the current TCB:
- `inode_bytes_valid(self.disk)` covers `[512, 2560)` = blocks 1–4. Block 5 (root dir, `[2560, 3072)`) is **NOT** covered.
- `self.dir` has `uniq` / `slots_lt32` invariants but **no byte-range invariant**.
- Callers (`_read_directory` — dead code; `listdir`/`scandir` in `__init__.py`) read from `self.disk` at `block_num * 512`, which for block 5 is outside `inode_bytes_valid`'s range.

**Routes considered:**
- (a) New class invariant covering directory block byte ranges → TCB growth, needs cross-validation + maintenance on every `self.disk` writer → **human-gated**.
- (b) New cross-validated axiom `UnixFs.Dir.dir_bytes_in_range` → **human-gated TCB addition**.
- (c) Restructure `_unpack_direntry` to avoid `_unpack_uint16_be` → can't avoid needing `data[0] >= 0` for the `ensures \result[0] >= 0` postcondition.

**Verdict:** GAP — logged, routed to human. Adding byte-range invariants is a human-gated TCB decision.

## A3: `sys_open` (6 goals) + `sys_rename` (2 goals) — GAP (logged)

**Strategy A (F3 modular verification):** Extract `sys_open`/`sys_rename` into a minimal-context file with `val` stubs for helpers. The **G0 probe** (scratch file with `sys_open` body + minimal context) was assessed but not executed due to the high extraction complexity (8 helper methods, each needing val stub contracts; 6 complex existentially-quantified postconditions over `dir_lookup` + fd table). The postconditions compose abstract predicates across multiple branches (O_CREAT, ENOENT, permission, ENFILE) — even in isolation they may not discharge without the marker axioms.

**Strategy B (cross-validated axioms):** `UnixFs.Dir.open_resolves_name` and `UnixFs.Dir.rename_presence_absence` lemmas in Rocq + Lean. This is a **human-gated TCB addition**.

**Verdict:** GAP — logged, routed to human. F3 extraction is the recommended path but is high-effort; Strategy B is human-gated.

## B1: `os.path.abspath`, `normpath`, `splitext` — GAP (logged, kept `\abstract`)

**Strategy A (pure-Python reimplementation):**
- `splitext`: blocked by tuple-return-type inference (H12 — PyCSL defaults tuple components to `int`; `return (root, ext)` with string components fails type inference). Workaround (return int) would be unfaithful to CPython API.
- `normpath`: `..` resolution requires list append/pop with complex postconditions; `//` collapse postcondition ("no `//` in result") needs `str.find` (blocked). Too complex for SMT.
- `abspath`: transitively blocked by `normpath`.

**Verdict:** GAP — all three kept `\abstract` (zero-TCB bodyless val, no ensures). Honest residual. See `bugs-to-report/20260623-1500-os-path-tool-gaps.md`.

## No-regression confirmation

- `src/pycsl_lib/os/__init__.py`: **SUCCESS** (0 unproven) — unchanged.
- `src/pycsl_lib/os/UnixInodeFileSystem.py`: **13 unproven** — unchanged (toolfix redundant on working tree but correct).
- 23 `formal_os_*.py` formal tests: **all 23 PASS** — unchanged.
- `bin/check-proof-crosscheck.sh`: **0 FAIL** — unchanged.
- Zero `\trusted` anywhere.
