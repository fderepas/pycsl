# GAP: `_unpack_direntry` body-gate residual needs a directory-region disk byte-range model fact (NOT a cheap win)

**STATUS: LOGGED GAP routed to the human.** Not closeable without a model extension.
No trust was added; the working tree is at baseline (2016 Valid / 8 residual / 0 `\trusted`).

## The residual (confirmed)

Body gate (`pure_lib/os/UnixInodeFileSystem.py`, PYTHONHASHSEED=0, Alt-Ergo 2.6.2 /
Z3 4.13.3): the 8 non-Valid grep matches resolve to **5 unique residuals** (3 are
echoed in the summary):

| function | sub-goal | result (step fingerprint) |
|---|---|---|
| `_unpack_direntry` | Precondition | Unknown (320459) |
| `_unpack_direntry` | Precondition | Unknown (337358) |
| `_now` | Postcondition | Out of memory |
| `sys_rename` | Assertion | Timeout (4621194) |
| `sys_rename` | Assertion | Out of memory |

(The summary's 3 echoed lines reuse the `_unpack_direntry` Unknown fingerprints
320459/337358 and the `sys_rename` Timeout 4621194 — i.e. `sys_write` proved this
run; the historical "sys_write ×3 aggregate noise" was not present.)

## Root cause (confirmed at the WhyML level)

`_unpack_uint16_be` (`UnixInodeFileSystem.py:15-24`) carries a hand-written contract
that requires `0 <= data[offset] <= 255` and `0 <= data[offset+1] <= 255` (needed
for its `0 <= \result <= 65535` ensures). It is emitted as a `let function` with
that contract (NOT inlined) — confirmed in the generated mlw:

```
let function _unpack_uint16_be (data: array int) (offset: int) : int
  requires { ((0 <= data[offset]) && (data[offset] <= 255)) }
  requires { ((0 <= data[(offset + 1)]) && (data[(offset + 1)] <= 255)) }
  ...
let _unpack_direntry (data: array int) : (int, array int)
  requires { (32 >= 0 && 32 <= Array.length data) }   -- ONLY \valid(data,32)
  ...
  inode_num := (_unpack_uint16_be data 0);            -- must discharge data[0..1] in 0..255
```

`_unpack_direntry`'s only precondition is `\valid(data, 32)` (length). The two
`_unpack_uint16_be data 0` precondition sub-goals (`0 <= data[0..1] <= 255`) cannot
be discharged from a length fact. **This exactly matches the mission's diagnosis.**

## Why the prescribed cheap retry does NOT close it (tested, then reverted)

Adding the minimal 2-clause precondition to `_unpack_direntry`
(`#@ requires 0 <= data[0] and data[0] <= 255` + the `data[1]` twin) **does make the
leaf prove** (Valid 2016 → 2018; `--fun _unpack_direntry` → SUCCESS). But it does
**not reduce the residual count** — it RELOCATES the obligation to the sole caller
`_read_directory` (`UnixInodeFileSystem.py:846-859`), which now fails 2 preconditions
with the SAME Unknown class (fingerprints 381631 / 304712), confirmed both in the
full gate and in `--fun unixinodefilesystem___read_directory` isolation. Net residual
stays at 8, and an unmet caller obligation is introduced — strictly worse. Reverted.

`_read_directory` reads `entry_bytes = self.disk[entry_offset : entry_offset + 32]`
where `entry_offset = block_num*512 + i*32`, `block_num ∈ [0,256)`. To discharge the
relocated precondition it must know `0 <= self.disk[entry_offset .. +1] <= 255` — a
**disk byte-range fact for the directory region**.

## Why no existing fact covers it

The only disk byte-range predicate is `inode_bytes_valid(self.disk)`, whose
definitional intro/elim axioms (`src/pycsl/module6_whyml/preamble.py:551-557`) pin:

```
inode_bytes_valid d  <->  forall i. 512 <= i < 2560 -> 0 <= d[i] <= 255
```

The covered range is `[512, 2560)` — the **inode table only**. The directory region
(block 5 = offset `2560`, entries through `3072`) and the rest of the disk are NOT
byte-range-constrained. This is precisely why `_read_inode` (which reads the inode
region and calls `_unpack_inode` with a full 64-byte-range precondition) PROVES,
while `_read_directory` cannot.

## The faithful fix (a model extension — NOT a cheap win)

Either:
1. **Extend `inode_bytes_valid`'s range** (or add a sibling `dir_bytes_valid`
   predicate) to cover `[2560, 3072)` — or, more generally, a whole-disk byte-range
   predicate `forall i. 0 <= i < len -> 0 <= d[i] <= 255`; AND
2. **Establish** it in the constructor / `_format_disk` (the zeroed disk trivially
   satisfies it), AND
3. **Maintain** it across EVERY disk mutator (`_write_entry`, `_zero_entry`,
   `_write_block_at`, `_poke`, `_write_inode`, `_alloc_block`, … — each writes bytes
   it must show are in `[0,255]`), via maintained loop/class invariants, exactly as
   `inode_bytes_valid` is carried today (the `block5_decode_frame` / per-mutator
   write-post pattern).

This touches the preamble axioms, the constructor, and the frame plumbing of every
mutator — a substantial, E-matching-sensitive change with real regression risk to
the load-bearing `__init__` gate. Under the extreme-rigor doctrine this is NOT a
cheap win: it is logged here and routed to the human, NOT closed by trust and NOT
worked around by weakening `_unpack_uint16_be`'s `<= 255` precondition (which the
`<= 65535` ensures genuinely needs).

## Note on the prior `no_inline`-import hypothesis

`bugs-to-report/20260616-1929-noinline-leaf-not-val-in-importer.md` attributed the
prior 32-clause-attempt stall to `#@ no_inline` re-verifying the leaf body in the
importer. The CLEANER root cause is the one above: the residual is a genuine missing
caller-side byte-range fact, independent of `no_inline`. The 2-clause minimal retry
(this run, machine load avg ~2 on 14 cores) did NOT even reach the `__init__` gate
because it fails at the body gate first (relocated residual). See that bug report's
updated status.
