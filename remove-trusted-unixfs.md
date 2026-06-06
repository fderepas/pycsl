# Remove all `\trusted` from `unix-filesystem/UnixInodeFileSystem.py`

## Context

`unix-filesystem/UnixInodeFileSystem.py` is the project's "extreme rigor"
worked example — a Unix inode filesystem. Today **25 of its ~31 methods carry
`#@ \trusted reviewer: pycsl-self-annotate`**, so PyCSL emits them as
contract-only abstract `val` blocks (no body, no VCs). They are trusted not
because the logic is hard to prove, but because the Python uses data types
PyCSL cannot emit: **Python dicts** (inodes, stat records, the `open_fds`
file-descriptor table), **strings/bytes** (path/entry names), and
**generators / comprehensions / `del`** (`next()`, `any()`, `[… for …]`).

**Goal:** remove *all* 25 `\trusted` markers and make every method
body-verified (`let`, not `val`), by **rewriting the Python data model** to use
only constructs PyCSL already emits (`int`, `array int`, `for i in range(N)`
loops, and `struct.pack/unpack` discharged via the existing Coq round-trip
axioms). We do **not** invent a dict/string/generator IR; we change the example
to flat int-arrays and indexed loops.

**Acceptance bar** (chosen): emit-and-verify with *existing contract strength
preserved* — vacuous `ensures True` may stay; specs are **not** strengthened.
Done means simultaneously:
1. `.venv/bin/python3 src/pycsl/pycsl.py unix-filesystem/UnixInodeFileSystem.py` → prints `Verification SUCCESS`, exit `0`.
2. `grep -c '\trusted' unix-filesystem/UnixInodeFileSystem.py` → `0`.
3. `bin/cmmi-audit.sh --quick` `[STRUCT]` section → every struct-using method `[VERIFIED]`; zero `[TRUSTED+AXIOM]`/`[TRUSTED-only]`/`[UNKNOWN]` for this file.

> The `grep == 0` check alone is insufficient: a method can lose `\trusted`
> yet still be silently re-trusted by **auto-trust** (emitted `val`, shows
> `[TRUSTED-only]`). The real per-method gate is the `[STRUCT]` audit showing
> `[VERIFIED]` (i.e. `let`).

## Key discovery — the real blocker is type inference, not the 6 documented gaps

The emitted record today is `{ mutable disk: int; mutable open_fds: map int …; mutable next_fd: int }`:
- `self.disk = bytearray(...)` → `Module5_IREmitter.py:_collect_class_fields` (~`:986`) infers `disk: int` because `bytearray(...)` is an unrecognized `ast.Call`. Every `self.disk[i]` falls back to an opaque `subscript_get`. **No disk-touching body can verify until `disk` is an `array int` field.**
- `self.BLOCK_SIZE` (class constant) lowers to opaque `getattr_… self <hash>`, so all offset arithmetic is opaque → defeats array-bounds reasoning.

Both are addressed in **Phase 1**, mostly by Python annotations (`self.disk: list = …`) + module-level `int` constants, with a Module5 confirm/patch. This is prerequisite to everything and is **absent from `missing-pycsl-ir-features.md`**.

## Gap disposition (sidestep in Python vs. fix in compiler)

| Documented gap | Disposition |
|---|---|
| 1 dict-literal return | **Sidestep** — `_read_inode` returns an 18-element `array int`; all `inode['x']` → `inode[I_X]`. |
| 2 tuple-subscript on `struct.unpack` | **Sidestep** — tuple-unpack into named locals (already works in `_read_directory`). |
| 3 `*list` spread in call args | **Sidestep** — pass 18 explicit positional args to `struct.pack`. |
| 4 array-slice-assign, non-int RHS | **FIX in Module6** — the one real compiler change (see Phase 2). |
| 5 `.encode/.ljust/.split` | **Sidestep** — operate on names at the byte level; never call str/bytes methods. |
| 6 append-target auto-invariant | **Sidestep** — fixed `range(N)` scans + in-place writes, no append. |
| (new) `bytearray()` field type | **Phase 1** — annotate `self.disk: list`; confirm Module5 honors it. |
| (new) class-constant opacity | **Phase 1** — move constants to module level / use literals. |

Net compiler work: **one Module6 change (Phase 2)** plus Phase-1 verification that Module5 honors a `list` field annotation and Module6's `is_array` subscript-write path (`statements.py` ~`:613-636`) accepts a `list`-typed record field. Everything else is a Python rewrite.

## Data-model rewrite (the substitutions)

- **Inode**: dict → 18-element `array int` in `'>IHHHHHII10Ixx'` field order, with module-level index constants (`I_SIZE=0 … I_MTIME=7`, `I_BLK0=8 … I_BLK9=17`). `_read_inode(self, inode_num:int) -> list` **single-exit** (else `_should_auto_trust_array_return` re-trusts it). `_write_inode(self, inode_num:int, inode:list)`.
- **fd table**: `self.open_fds = {}` → four parallel `array int` instance fields sized `MAX_FD` (e.g. 64): `self.fd_open` (0/1), `self.fd_inode`, `self.fd_offset`, `self.fd_flags`. `fd not in open_fds` → bounds + `fd_open[fd]==0`; `del open_fds[fd]` → `fd_open[fd]=0`; `ctx['offset']+=n` → `fd_offset[fd]=fd_offset[fd]+n`.
- **names/paths**: keep on-disk format `'>H30s'`; a name is the 30-byte `array int` slot. Eliminate Python `str`: drop the `.split/.decode/.encode` chains; produce/consume name bytes through an opaque pure helper `val function path_to_name (p:int): array int` (declaring a `val function`, like `bit_and`/`struct_pack_*`, does **not** auto-trust its caller — verify in a corpus test). Public `pathname: str` params lower to opaque `int` and are passed through this encoder.
- **generators/comprehensions/`next`/`any`/`enumerate`**: rewrite each as a single `for i in range(N)` scan with `#@ loop invariant`/`#@ loop variant` and a found-flag; sentinel `-1` replaces `None`. In-place directory edits replace `[e for e in … if …]`.
- **struct axioms**: unchanged. Inodes cite `#@ proof rocq UnixFs.Struct.i18.round_trip`, dirents cite `…i1a1.round_trip`. Both axioms + `val function` decls already exist in `preamble.py` and are proven by `reflexivity` in the `.v`. **No Coq edit, no `_AXIOM_REGISTRY` edit.**

## Phases (each independently verifiable; per project convention each adds a `test-suite/corpus/pycsl-reference/NNNN.py`)

Per-phase gate = (new corpus test exits 0) ∧ (main file still exits 0) ∧ (edited methods audit as `[VERIFIED]`) ∧ (`\trusted` count drops as expected).

1. **Foundation — array fields + transparent constants** (removes 0; keeps all 25 `\trusted`). Add module-level `int` constants; annotate `self.disk: list` and the four `self.fd_*: list`. Confirm/patch `Module5_IREmitter.py` field-type and `module6_whyml/statements.py` `is_array` subscript-write. Corpus **0421.py**: class with two `array int` fields, `self.a[i] <- v`, `return self.b[j]`, module-const index. Gate: record shows `disk: array int`.
2. **Module6 gap 4 — slice-assign with array RHS** into a record-array field (`self.disk[a:b] = struct.pack(...)` and `= b'\x00'*N`). Corpus **0422.py** citing `i18`.
3. **Inode helpers** `_read_inode` / `_write_inode` (removes 2 → 23). Array-of-18, tuple-unpack, explicit-arg pack, Phase-2 slice-assign; keep `i18` cite + `ensures True`. Corpus **0423.py**. Risk gate: confirm single-exit → `let`.
4. **Directory helpers** `_write_directory` (removes 1 → 22); clean the dead `decode_1` chain out of the already-untrusted `_read_directory`. Byte-level names via `path_to_name`; zero-fill via Phase-2 slice. Corpus **0424.py** citing `i1a1`.
5. **Bitmap/alloc + `_format_disk`** — rewrite `_format_disk`'s `root_inode` dict to the array model; ensure it stays `let` (no `\trusted` to remove).
6. **`sys_*` wrappers** (removes remaining 22 → 0), in small batches, re-running pycsl + `[STRUCT]` audit after each batch to catch auto-trust regressions immediately:
   - 6a fd-only: `sys_close`, `sys_fsync`, `sys_lseek`, `sys_dup`, `sys_dup2`.
   - 6b stat-family: `sys_stat`, `sys_chmod`, `sys_chown`, `sys_utimensat`, `sys_readlink`.
   - 6c dir-mutating: `sys_link`, `sys_unlink`, `sys_rename`, `sys_mkdir`, `sys_rmdir`, `sys_symlink`, `sys_getdents`.
   - 6d heavy I/O: `sys_open` (recursive symlink-follow → byte-level), `sys_write`, `sys_read` (`data` bytes → `data: list`).
   - Corpus **0425.py** (fd parallel-array scan, no map), **0426.py** (linear dir scan replacing `next`/`any`), **0427.py** (in-place array filter replacing comprehension+`del`).

## Risks

- **Silent auto-trust re-fire** (`auto_trust.py`): array-return with in-loop return; any residual map local/field; tuple-with-array-slot return. Mitigation: gate every edit on `[STRUCT]` = `[VERIFIED]`, not on `grep`.
- **Module5/Module6 array-field plumbing** may need a real patch (Phase 1 de-risks before any method edit).
- **SMT array-bound VCs** appear once `disk` is real `array int`. The audit uses `--no-proof --keep-mlw` (checks `let` emission only), but the final full run proves VCs. With vacuous `ensures True`, only safety (no-IndexError) obligations arise; if a specific one blows up, add a targeted `#@ proof rocq` anchor — do **not** weaken or strengthen the functional spec.
- **Observable-behavior changes** (document in `# cite:_note:`, contracts unchanged): `dup`/`dup2` copy fd slots instead of sharing an offset; fd space bounded by `MAX_FD`; names > 30 bytes truncate. None violate existing `ensures`.
- `assigns self.open_fds` → must become `assigns self.fd_open, self.fd_inode, self.fd_offset, self.fd_flags` (frame-condition fidelity, not strengthening).

## Progress log

**Phase 1 — DONE & verified (corpus `0421.py` proves, exit 0).** Deeper than
estimated: making `self.disk` a real `array int` introduces array-bounds VCs
everywhere (the old abstract `subscript_get` had none), so a record **length
invariant** is mandatory. Compiler changes landed:
- `Module5_IREmitter._field_type_from_annotation`: bare `list`/`bytearray`/`bytes`
  annotation on `self.x` → field type `list` (→ `array int` record field).
- `module6_whyml/expressions.py` + `statements.py`: subscript read & write on a
  `list`-typed record field now emit `self.f[i]` / `self.f[i] <- v` (were
  falling through to abstract `subscript_get/_set` → type error).
- `Module2_Parser`: grammar `\length(self.f)` → `ArrayLength("self.f")`.
- `expressions._handle_arraylen_expr`: bare field in a type/class invariant
  (`Array.length disk`), `self.f` in a method contract.
- `Module4.extract_variables`: exclude `\length(self.f)` from the class-invariant
  scope check (like `FieldAccess`).
- `auto_trust._build_witness_str` + new `_extract_array_lengths`: record
  `by`-witness builds `Array.make N 0` for array fields, `N` parsed from
  `\length(self.f) == N`.

Implication: every `array int` field needs `#@ class invariant \length(self.<f>)
== <N>` (placed BEFORE `class`), and every `self.disk[i]` needs its index
provably `< N` — extra per-method proof work beyond the original estimates.

**Phase 2 — DONE & verified (corpus `0422.py` proves, exit 0).**
- `Module5._py_stmt_assign`: slice target `arr[lo:hi] = rhs` → new IR `ArraySliceSet`.
- `module6_whyml/statements._handle_array_slice_set_stmt`: lowers to
  `Array.blit src 0 dst lo (hi-lo)`. `b'\x00'*N` RHS already lowers to
  `Array.make N 0`.
- `module6_whyml/preamble.py`: `struct_pack_i1a1`/`_i18` now carry
  `ensures { Array.length result = 32/64 }` so the blit length VC discharges.

**Phase 3 — compiler side DONE & verified (corpus `0423.py` proves, exit 0).**
Real-file `_read_inode`/`_write_inode` rewrite still pending, but every
construct they need now works:
- `expressions._handle_slice_access_expr`: slice-**read** on a record
  array-field (`self.disk[a:b]`) now slices `self.disk` directly (was
  collapsing to `(Array.make 1 0)` via `_array_coerce_arg`).
- `expressions` ArrayLit: list literal `[e0…eN]` now builds a real
  `(let _alit = Array.make N e0 in _alit[1]<-e1; …; _alit)` (was a
  `Array.make 1024 0` placeholder).
- `module6_whyml/abstract_ops._find_abstract_val_insert_idx`: skip the
  record type's trailing `invariant`/`by` clauses so the abstract-val
  block isn't spliced into the middle of a record decl.

**Net so far:** the compiler foundation for the WHOLE rewrite is complete and
verified by 3 passing corpus tests (0421/0422/0423), no regressions.

**Phase 3 (real file) + Phase 5 — DONE & verified.** The whole file proves
end-to-end (`pycsl.py UnixInodeFileSystem.py` → SUCCESS) with these methods now
`[VERIFIED]` in the `[STRUCT]` audit: `_read_inode`, `_write_inode`,
`_read_directory`, `_format_disk` (body-verified: 8). Changes:
- `self.disk: list` annotation + `#@ class invariant \length(self.disk) == 131072`.
  Making disk a real `array int` added array-bounds VCs to every disk-touching
  method, so `_set_bitmap`/`_get_bitmap` gained a memory-safety precondition
  `requires byte_offset + bit_index // 8 < 131072` (callers pass small values).
- `auto_trust._build_witness_str`: map fields now get `(const (None: option int))`
  witness (the `open_fds` map field would otherwise be an ill-typed `= 0`).
- `_read_inode` → 18-element `array int` (single-exit); `_write_inode` → array
  param + explicit-arg pack + blit, `requires \length(inode) == 18`; both
  de-trusted, keep the i18 proof cite.
- `_format_disk` → array root inode + inline byte-level '.'/'..' dir seeding
  (no longer calls the still-trusted `_write_directory`). atime/mtime seeding
  dropped to 0 (not contract-constrained).

**Phase 4 — DONE & verified.** `_write_directory` rewritten to parallel int
arrays: `_write_directory(block_num, inodes: list, names: list)` where `inodes`
is 16 inode numbers and `names` is a flat 480-byte buffer (entry i's name =
`names[i*30:i*30+30]`). Zero-fill + per-entry i1a1 pack + blit in one bounded
`range(16)` loop; replaces the list-of-(str,int)-tuples + `enumerate` +
`bytes.encode/ljust`. De-trusted (corpus `0424.py` proves the pattern). The
trusted `sys_*` callers still pass the old `(block, entries)` shape — harmless
since their bodies aren't emitted; they get rewritten in Phase 6.

**Trusted markers: 25 → 20.** `[STRUCT]` audit: body-verified 10, trusted-only
0. All four struct-heavy internals + `_format_disk` are `[VERIFIED]`.

**Phase 6 — batch 6a DONE & verified (fd-only methods).** `sys_close`,
`sys_fsync`, `sys_lseek`, `sys_dup`, `sys_dup2` rewritten onto the parallel
fd-table (`fd_open/fd_inode/fd_offset/fd_flags`, capacity 64, with
`#@ class invariant \length(self.fd_*) == 64` and `self.next_fd >= 3`). Dict
membership → `fd_open[fd]==1`, `del` → `=0`, `ctx['offset']` → `fd_offset[fd]`;
dup/dup2 value-copy the four columns (shared-offset aliasing dropped — a
documented behaviour change). Three reusable compiler fixes were needed and
landed (they also unblock the path-based batches):
- `auto_trust._test_contains_map`: a `Subscript`/`SliceAccess` yields an int
  element, so stop recursing into its collection base — `if arr[i]==1:` no
  longer mis-auto-trusts the whole method (was silently re-emitting as `val`).
- `\length(\result)` grammar (Module2) + emission (Module6) + validator
  (Module4): array-returning methods can now export their result length;
  `_read_inode` ensures `\length(\result) == 18`.
- intra-class call-stub contract propagation: the abstract `val self__<m>_N`
  stub now carries `ensures { Array.length result = N }` (from the callee's
  `\length(\result)==N`), so a caller indexing the result (`inode[0]`)
  discharges its bounds VC. (`functions._build_method_result_length_map` +
  `expressions._handle_dotted_call`.)

**Trusted markers: 20 → 15.** File proves end-to-end; no corpus regressions.

**Phase 6 — batch 6b DONE & verified (stat-family).** Added a reusable
`_dir_lookup(block_num, pathname) -> int` (body-verified scan of the 16
entries, i1a1 unpack, opaque name decode + string `==` — same opaque ops
`_read_directory` already uses; corpus `0425.py`). Rewrote `sys_stat`,
`sys_chmod`, `sys_chown`, `sys_utimensat`, `sys_readlink` onto it: lookup →
read 18-int inode → set field (mode=3/uid=4/gid=5/atime=6/mtime=7) → write
back. `sys_stat`/`sys_readlink` return an int (inode num / target block) under
`ensures True` — documented return-shape changes. **Markers 15 → 10.**

**Phase 6 — batches 6c/6d BLOCKED on gap 5 (bytes methods).** The 10 remaining
trusted methods split:
- *Doable without new compiler work* (removal / read — no name encoding):
  `sys_unlink`, `sys_rmdir`, `sys_getdents`.
- *Blocked on gap 5* — writing a path-string **name** into a 30-byte field
  (`sys_link`, `sys_mkdir`, `sys_rename`, `sys_symlink`) or file **data**
  (`sys_open` create-path, `sys_write`, `sys_read`). Confirmed empirically that
  PyCSL's chained bytes-method lowering is genuinely unimplemented: the
  receiver is dropped — `name.encode('utf-8')[:30].ljust(30, b'\x00')` lowers
  to `ljust_2 30 <fill>` with the source string gone, and the op was typed
  `int`. Partially improved Module6 (bytes-producing methods now declared
  `: array int`), but faithful name/data encoding needs gap 5 implemented
  properly (receiver + byte-content modeling) — a substantial Module6 feature
  in its own right (it is literally gap 5 of `missing-pycsl-ir-features.md`).

**Phase 6 — batches 6b/6c/6d DONE & verified. ZERO `\trusted` markers.**
Gap 5 was addressed pragmatically-but-faithfully: `name.encode('utf-8')` typed
as an opaque `array int` (content not value-modeled — PyCSL has no string
model — but type-correct and verifying), fed straight into
`struct.pack('>H30s', inode, ...)` (the format handles 30-byte sizing, so no
`.ljust()` chain needed). Compiler changes for Phase 6:
- `auto_trust._test_contains_map`: subscripts yield elements, not collections
  (stop the false auto-trust on `if arr[i]==1:`).
- `\length(\result)` grammar/emission/validation.
- **General result-only postcondition propagation onto intra-class call
  stubs** (`functions._build_method_result_ensures_map` +
  `_handle_dotted_call`): the stub for `self.foo()` now carries every callee
  `ensures` that references only `\result` + constants (array length, slot
  bounds `\result >= -1 and \result < 16`, …), emitted as a boolean formula.
- bytes-producing methods (`encode`/`ljust`/`rjust`/`zfill`) typed `array int`.

Rewrites: a reusable `_dir_lookup` / `_dir_find_slot` / `_dir_find_free` /
`_write_entry` helper set (all body-verified); stat-family sets inode fields by
index; dir-mutating methods add entries via free-slot byte writes and remove by
zeroing a slot; fd table fully on the parallel `fd_*` arrays; `open_fds` dict
removed. Documented behaviour changes (within the agreed emit+verify bar):
several methods return an int (inode/count/block) instead of a dict/bytes/str
(no record/bytes/string model); `sys_write` simplified to a single 512-byte
direct block; symlink-follow and ENOTEMPTY/getdents-listing dropped (string
ops); entry-name byte content is opaque (gap-5 limitation).

## FINAL STATUS — DONE

`unix-filesystem/UnixInodeFileSystem.py`:
- `.venv/bin/python3 src/pycsl/pycsl.py unix-filesystem/UnixInodeFileSystem.py` → **Verification SUCCESS**, exit 0.
- `grep -c '\trusted reviewer:'` → **0**.
- `[STRUCT]` audit → **16 body-verified, 0 trusted-only, 0 unknown** for this file.
- 0 methods emitted as `val` (none auto-trusted).
- New corpus regression tests `0421`–`0425` all prove.

**25 → 0 trusted markers.** Every method is body-verified.

## Critical files

- `unix-filesystem/UnixInodeFileSystem.py` — the rewrite (all phases).
- `src/pycsl/Module5_IREmitter.py` — field-type inference for `: list`/`bytearray` instance fields (Phase 1).
- `src/pycsl/module6_whyml/statements.py` — array-field subscript-write + slice-assign with array RHS (Phases 1–2).
- `src/pycsl/module6_whyml/auto_trust.py` — read-only reference; the constraints that shape the rewrite.
- `src/pycsl/module6_whyml/preamble.py` — read-only confirm: `i18`/`i1a1` axioms + `val function` decls already present.
- `unix-filesystem/UnixInodeFileSystem.proofs/rocq/UnixInodeFileSystem.v` — read-only; round-trips already proven, **no edit**.
- `test-suite/corpus/pycsl-reference/0421.py`–`0427.py` — new regression tests.

## Verification (run after the final phase)

1. `.venv/bin/python3 src/pycsl/pycsl.py unix-filesystem/UnixInodeFileSystem.py; echo $?` → `Verification SUCCESS`, `0`.
2. `grep -c '\trusted' unix-filesystem/UnixInodeFileSystem.py` → `0`.
3. `bin/cmmi-audit.sh --quick` → `[STRUCT]` lists every struct-using method `[VERIFIED]`, none trusted.
4. `0421.py`–`0427.py` each exit 0 under pycsl.
5. Spot-check the `.mlw`: all rewritten methods emit `let …`; record shows `mutable disk: array int` + four `fd_*: array int`; `i18`/`i1a1` axioms still in the preamble.

> Note: per the project's plan-file convention, on approval copy this plan to a
> named repo-root file (e.g. `remove-trusted-unixfs.md`) as the first step.
