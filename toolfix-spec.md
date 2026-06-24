# toolfix-spec.md — PyCSL slice-write per-element VC emission

**Date:** 2026-06-23
**Status:** DONE (implementation landed, all gates satisfied)
**Motivated by:** `bugs-to-report/20260623-1430-unixfs-bodyvc-gaps.md` GAPs 1–6 (9 of the 13 remaining unproven body-VCs in `UnixInodeFileSystem.py`)

---

## High-level goal

When PyCSL lowers a Python slice assignment `dst[lo:hi] = src` (where `src` is an array-typed expression) to the WhyML `Array.blit src 0 dst lo (hi - lo)`, it must additionally emit a **per-element equality postcondition** at the call site so that downstream `#@ ensures` and `#@ assert` clauses can reason about the individual bytes of `dst` after the blit.

Today the slice-write handler (`_handle_array_slice_set_stmt` in `src/pycsl/module6_whyml/statements.py:408`) emits only the `Array.blit` call. Why3's `Array.blit` specification guarantees `forall i. 0 <= i < len -> dst[lo+i] == src[i]` internally, but this fact is **not surfaced as a VC or an assumption** that the caller's postconditions can use. The result: any `#@ ensures` on a function that does a slice write — e.g. `self.dir[off] * 256 + self.dir[off+1] == inode_num` — is unprovable because the solver cannot connect `self.dir[off]` to `entry[0]` across the `Array.blit`.

This single tool gap **cascades** to 9 of the 13 remaining unproven goals: the `_blit_*` postconditions are Unknown (2+1), and their callers (`_write_dir_entry`, `_write_entry`, `_zero_entry`) are Timeout/OOM because their `#@ assert` lines depend on the blit's postconditions.

---

## What must change

After emitting `Array.blit src 0 dst lo n`, the handler must emit an inline WhyML `assert` that states the per-element equality:

```why3
assert { forall i : int. 0 <= i < n -> dst[lo + i] = src[i] }
```

where `n = hi - lo`. This is a **definitional fact** about `Array.blit` (Why3's stdlib proves it from `blit`'s specification), so emitting it as an `assert` adds **zero TCB** — it is a hint that lets the solver use the fact, not a new axiom.

## Why an `assert` and not an `axiom` or `ensures`

- **Not an axiom:** the fact is already proven in Why3's `Array.blit` spec; we are not adding trust, just surfacing an existing fact to the caller's proof context.
- **Not an `ensures` on the function:** the `ensures` is already on `_build_direntry` (the source of `entry`); the gap is connecting `_build_direntry`'s `ensures \result[0]*256 + \result[1] == inode_num` to `self.dir[off]*256 + self.dir[off+1] == inode_num` after the blit. The `assert` bridges that gap.
- **An `assert` is the right granularity:** it fires at the blit site, is checked by the solver (not assumed), and is visible to all downstream `ensures`/`assert` clauses in the same function body.

## Scope of the fix

| Aspect | Detail |
|---|---|
| **File** | `src/pycsl/module6_whyml/statements.py` |
| **Function** | `_handle_array_slice_set_stmt` (line ~408) |
| **Change** | After the `Array.blit` emission, emit an `assert { forall i. 0 <= i < (hi-lo) -> dst[lo+i] = src[i] }` |
| **WhyML shape** | `assert { forall i : int. (0 <= i /\ i < n) -> (dst[lo + i] = src[i]) }` |
| **Condition** | Only when `src` is array-typed (the existing handler already guards on this) |

## Expected impact

| GAP | Sub-goals | Expected after fix |
|---|---|---|
| GAP 1 `_blit_dir_entry` | 2 Unknown | **Valid** (the `ensures self.dir[off]*256 + self.dir[off+1] == inode_num` discharges from `_build_direntry`'s ensures + the blit assert) |
| GAP 2 `_blit_disk_entry` | 1 Unknown | **Valid** (same) |
| GAP 4 `_write_dir_entry` | 1 Timeout | **Valid** (the `#@ assert` lines that depend on the blit's postconditions now discharge) |
| GAP 5 `_write_entry` | 1 OOM | **Valid** (same, on `self.disk`) |
| GAP 6 `_zero_entry` | 1 OOM | **Valid** (same) |
| GAP 3 `_unpack_direntry` | 1 Unknown | **Not fixed** by this toolfix (different root cause — byte-range requires propagation, not slice-write) |
| GAP 7 `sys_open` | 6 Timeout | **Not fixed** (proof-cost-bound in aggregate, needs F3 modular verification) |
| GAP 8 `sys_rename` | 2 Timeout | **Not fixed** (same) |

**Projected unproven count after this fix:** 13 → 4 (GAP 3's 1 + GAP 7's 2 + GAP 8's 1 — the cascade goals close automatically once GAPs 1–2 are fixed).

## Gating

1. **No regression:** `__init__.py` stays SUCCESS; all 21 formal tests stay PASS; `bin/check-proof-crosscheck.sh` 0 FAIL.
2. **Byte-diff:** the generated WhyML for files NOT using slice-write must be byte-identical (DIFFERS=0). Files using slice-write (`_blit_dir_entry`, `_blit_disk_entry`) will DIFFER (the new `assert`).
3. **Zero TCB growth:** no new `\trusted`, no new axiom. The `assert` is a definitional fact from Why3's `Array.blit` spec.
4. **Corpus:** if a new `#@` directive is added (not expected — this is an emitter-only change), run `bin/doc-coherency.py --check`.

## Open question

Should the `assert` be emitted unconditionally for every slice write, or only when the function has `#@ ensures` that reference `dst` elements? Unconditional is simpler and sound; conditional would reduce proof context noise. **Recommendation: unconditional** — the assert is cheap (Why3 discharges it trivially from `blit`'s spec) and the solver benefits from having the fact available.
