# os-model-impl2.md — achieving functional correctness for the os module

**Status:** Implementation document (self-contained; supersedes the phasing in os-model-impl.md)
**Goal:** prove that the verified os is a *correct filesystem* — a file faithfully stores and returns
its content and is retrievable by name — not only that it is *safe* (no crashes, in-bounds, well-formed
return codes). The single acceptance test is `pure_lib_test/formal_0008.py`:

> create file `f`, write content `c`, close; reopen `f`, read it back; **`#@ ensures \result == True`** —
> the read equals `c`, for all symbolic `f` and `c` in range.

This document is written to be read on its own. §1 states where the os is today; §2 explains the one
obstacle everything turns on; §3 is the architecture; §4 the concrete components; §5 the build order
(leading with the decisive feasibility probe); §6 proof-cost management; §7 the faithfulness rules; §8
the fallback architecture; §9 acceptance.

---

## STEP-0 RESULT (BREAKTHROUGH, 2026-06-09) + refined remaining path

**The decisive feasibility probe SUCCEEDED — the proof-cost wall is dissolved.** The rich inode codec
(per-byte / per-field value contracts, `#@ no_inline`) was ported into the os, with the disk-region
byte-invariant and the 18 field-range `requires` on `_write_inode`. The full os proof **completes at 0
unproven** with the rich codec in scope — the c-impl aggregate blow-up does **not** recur on the
now-clean os (no_inline syscalls + the eliminated axioms). Only three per-syscall discharge gaps
appeared, closed by faithful POSIX guards (link EMLINK, chmod invalid-mode, truncate/ftruncate oversized
length). **So the §2 obstacle is solved without an axiom: the inode round-trip holds by composition from
the byte leaves' value contracts.** Committed as the C3 foundation.

**Read-after-write inode consistency landed too:** `_write_inode` now proves the persisted inode region
decodes back to the written size (`inode[0]`) and data block (`inode[8]`), so a file's block is
recoverable by a later `_read_inode` — and the os still proves 0 unproven. Committed.

**Refined remaining path (the hard part is now the cross-call *effect* contracts, not the codec cost).**
Implementing C1 revealed that composing the round-trip needs each syscall in the chain to **expose its
effect**, which the current count/return-code contracts do not:

- **`sys_write` must ensure *what* it wrote**, not just the byte count — i.e. the file's data block holds
  `c` after the call (a content-effect ensures, the data-region analogue of the inode readback just
  added to `_write_inode`).
- **`pread` (C1) must ensure its result equals the file's data-block slice** — but the block is resolved
  *inside* `pread` (`fd → inode → inode[8]`), so the contract must expose that resolution for a caller
  to connect `pread`'s result to what `write` stored.
- **C2 (value-modeled names)** and **C4 (framing across close/open)** remain as in §4/§5, plus the
  **success-precondition** discharge (C5) so `\result == True` is non-vacuous.

These are intricate effect-contract design choices with proof-cost implications (each enriched contract
rides into callers), best advanced with measurement at each step rather than blind. The foundation is
proven viable; what remains is composition, not feasibility.

---

## 1. Where the os is today

The os module proves **0 unproven goals** with a one-family trusted-axiom base (a bitwise bound). But
the contracts discharged are **safety/structural**: array accesses are in bounds, the disk-length and
fd-column class invariants hold, every syscall returns a well-formed code. The existing round-trip
driver only asserts `\result == 0 or \result == 1` — a postcondition satisfied *even if every operation
fails*. Nothing proves a file round-trips.

Two concrete shortfalls block a real test:

- **`read` returns a byte count, not content.** `sys_read` advances `fd_offset` and returns `n`; it
  never touches the data block. There is no operation that returns the bytes read, so a content
  comparison is not even type-correct (`read(...) == c` compares an `int` to a buffer).
- **Directory names are stored opaquely.** `_pad_name` reduces a name to an unspecified 30-byte buffer
  and `_dir_lookup` compares decoded-from-opaque bytes, so `_dir_lookup(f)` cannot be proven to
  re-find the file just created under `f`.

## 2. The one obstacle: the inode round-trip

The content round-trip cannot be proven from a disk-slice round-trip alone. A file's data lives in a
**dynamically allocated block whose number is stored in the file's inode** (`inode[8]`), and the inode
itself lives on disk as 64 packed bytes. So:

- `write` allocates block `B`, sets `inode[8] = B`, and persists the inode via
  `_write_inode → _pack_inode` (64 bytes blitted into the inode region).
- *Any* later read — even on the same fd, and certainly after a reopen — recovers the block via
  `_read_inode → _unpack_inode → inode[8]`.

For the recovered block to provably equal the written block, the codec must **round-trip on that
field**: `_unpack_inode(_pack_inode(inode))[8] == inode[8]`. The current codec carries only
`ensures \length(\result) == 64/18`, so it yields **no field values** — the recovered block is unknown,
and the read's slice location cannot be pinned. The same is true of any inode field a proof needs
(size `inode[0]`, type/mode for an open's permission check). **This is the obstacle: functional
correctness requires the inode to round-trip through the disk codec, and the codec must carry the
field-level contracts that make the round-trip provable.**

A cross-validated *axiom* for this round-trip was deliberately removed (it was vestigial for the safety
proof) and must **not** be re-added — the round-trip has to be *proven*. Proving it needs the **rich
codec contracts**, which historically were proof-cost-bound *in the full module* (each codec function
proved standalone in seconds but the cost compounded across the eight call sites). Closing the obstacle
therefore has two parts: (a) give the codec field-level contracts that establish the round-trip, and
(b) keep those contracts **affordable** in the os. §3–§6 are how.

## 3. Architecture

Extend the existing concrete model (real disk bytes, real syscalls) with four capabilities; prove the
functional properties directly against it, using a **representation invariant** to carry the
round-trip. This is the lighter of the two viable architectures; §8 gives the heavyweight
ghost-refinement fallback if the proof cost proves intractable.

The four capabilities:

1. **A content-returning read** — so content is observable (P1).
2. **A field-level (rich) inode codec whose round-trip is proven** — so a persisted block/size/mode is
   recoverable (the §2 obstacle).
3. **A representation invariant on the inode** — a field-range invariant on a typed inode that supplies
   the rich `_pack_inode`'s preconditions at every call site (so the round-trip is usable without
   widening any contract unfaithfully), validated previously by micro-probes.
4. **Value-modeled directory names** — so a name resolves to the inode it was created under (P2).

Affordability (§6) is achieved by verifying the rich codec **once** (a separated, minimal-context
module and/or `#@ no_inline` so its body is one VC, not re-proved at each call site) and letting the
syscalls use its **contract**.

## 4. Components

### C3 — the rich inode codec + round-trip (the hard core; do its probe first, §5)
- **Rich `_pack_inode`:** `requires` the 18 field ranges (`0 <= fields[k] <= MAX_k`); `ensures` the 64
  result bytes are in `[0,255]` and encode the fields (the per-byte value formulas). Built
  leaf-compositionally from the body-verified byte leaves (`_pack_uint{16,32}_be`), which already carry
  exact value contracts (`result[0]*256+result[1] == v`, etc.). Proves standalone today (~tens of
  seconds in a minimal context).
- **Rich `_unpack_inode`:** `requires` the 64 input bytes in `[0,255]`; `ensures` each of the 18 result
  fields equals the decoding formula of its bytes. The inverse of the leaves' contracts.
- **The round-trip** then composes by value: `_unpack_inode(_pack_inode(fields))[k] == fields[k]`,
  because `unpack_leaf(pack_leaf(v)) == v` for each uint leaf. No axiom — discharged from the leaves'
  contracts.
- **Affordability:** verify the codec where it is cheap — keep it in a minimal-context module
  (`codec.py` exists and proves the round-trip in ~42 s) and/or mark `_pack_inode`/`_unpack_inode`
  `#@ no_inline` so each is one verified VC and callers reuse the contract. Resolve the import so the os
  sees the rich contract without `--deep` (the shallow resolver injects an imported function only if the
  *importing file* calls it — so `UnixInodeFileSystem` itself must import the codec, and the resolution
  of that transitive import must be made to work without pulling the whole closure).

### C3-inv — the inode representation invariant (supplies C3's requires)
- Model the inode as a **typed value** carrying a field-range invariant
  (`0 <= field_k <= MAX_k` for each of the 18 fields). This invariant **supplies** the rich
  `_pack_inode`'s 18 `requires` at every `_write_inode` call site — faithfully (the ranges are
  established, not narrowed away). Micro-probes previously confirmed: the invariant discharges the
  requires at a call site, and **survives bounded computed mutations** (`inode[0] = new_size` with
  `new_size <= disk_size = 131072 < 2^32`, `inode[8] = B` with `B < 256`, a timestamp from the clock).
- A **disk-region byte-invariant** `\forall i. 512 <= i < 2560 ==> 0 <= disk[i] <= 255` supplies the
  rich `_unpack_inode`'s byte-range `requires` for `_read_inode` (the inode region holds bytes). It is
  maintained only by the inode-region writers (`_write_inode`, the formatter), since every other write
  is outside `[512,2560)` and preserved by frame; probes confirmed it survives slice writes affordably.

### C1 — content-returning read
- Add a read that returns the bytes: `sys_pread(fd, nbytes, offset) -> list` (+ an `os.pread` wrapper),
  reading from an explicit offset so it does not perturb `fd_offset`. It resolves the fd's inode and
  data block exactly as `sys_write` does and returns `Array.sub` of the data region.
- Contract: on the success path, `ensures \length(\result) == nbytes` and the result equals the disk
  slice (so the round-trip can equate it to what `write` stored). The counting `sys_read` stays intact
  so `formal_0001` and existing callers are unaffected; `pread` is the content view P1/P4 use.

### C2 — value-modeled directory names
- Give the directory a value-determined name→inode association. Least-invasive shape: a parallel
  `_dir_names` of 16 **string** slots for the root directory block, with a class invariant on its
  length (mirroring the fd-column length invariants).
- `_write_entry(slot, inode_num, name)` sets `_dir_names[slot] := name` (the value) alongside the
  existing byte write; `_dir_lookup(pathname)` scans `_dir_names[i]` and compares with `str_eq`,
  returning the matching slot's inode. Then "create `f`" stores `f` by value and "open `f`" finds it
  because `str_eq f f` is *Valid* by reflexivity; distinct names stay distinct because `str_eq f g` is
  false when `f != g`. The byte directory block is retained for on-disk-format fidelity but is no longer
  the resolution path.
- **Risk to confirm early:** the WhyML string theory must give `str_eq` reflexivity and discrimination
  decidably. If it does not, that is a *finding* that pushes C2 toward a `map string int`
  (name→inode) representation — not a place to add an axiom.

### C4 — persistence framing
- Make `assigns` precise so the operations *between* the write and the content read provably touch
  neither the file's data region nor `_dir_names`: `close` assigns only `fd_open`; `open` (existing-file
  path) only the `fd_*` columns + `next_fd`; `lseek` only `fd_offset`. With those frames, the written
  content and the name mapping are invariant across close→open→seek. The create path of `open` does
  write the data/name structures, but P4's reopen takes the existing-file path, so its frame excludes
  them.

### C5 — open-success preconditions
- `\result == True` requires the reopen to provably return `fd >= 3`. The driver must establish the
  conditions under which create/open/write succeed — in particular a known credential so the permission
  check passes. `_check_perm` returns 1 when `cur_uid == 0`, but the class invariant is only
  `cur_uid >= 0`; the driver (or a strengthened invariant) must make `cur_uid == 0` available so the
  root-bypass branch is provably taken. The remaining success conditions (an inode and a block are
  allocatable in a fresh filesystem; a just-created name resolves) follow from C2/C3.

## 5. Build order (lead with the decisive probe)

C3 is the only component whose feasibility is uncertain; everything else is engineering. So measure it
first, in isolation, before investing in C1/C2/C4.

- **Step 0 — C3 feasibility probe (decisive).** Give `_pack_inode`/`_unpack_inode` the rich contracts
  (§C3) with `#@ no_inline`, add C3-inv (the inode field-range invariant + the region byte-invariant),
  and run the **full os proof**. *Question:* does the os still prove **0 unproven** with the rich codec
  in scope, within an acceptable time budget (raise `--timelimit` as needed)? This is the c-impl wall
  re-measured on the now-clean os (no_inline syscalls, axioms shed). **Decision point:** affordable →
  proceed to Step 1; intractable even with `no_inline` + minimal context → switch to the §8 ghost
  refinement (or escalate the proof budget as a dedicated effort). Commit nothing that regresses the
  0-unproven baseline.

- **Step 1 — C1 + P1.** Add `pread`; prove **P1** (open, write `c`, `pread` from offset 0 → equals `c`,
  same fd). Ship a *failure-expressible* sibling: preading after writing a different buffer must **fail**
  to prove equality (so P1 is not vacuous).

- **Step 2 — C2 + P2.** Add `_dir_names`; rewrite `_write_entry`/`_dir_lookup`; re-prove every
  directory-touching syscall with the new field framed; prove **P2** (create `f` → `lookup f` is its
  inode; absent name → −1). This is the most regression-prone step (the field rides every directory
  syscall's frame).

- **Step 3 — C4 + P3.** Tighten the frames; prove **P3** (content and identity survive close→reopen).

- **Step 4 — compose P4.** Wire C5's preconditions into the driver; prove `formal_0008` `\result == True`.

Each step is gated on the full os holding at **0 unproven**, the TCB staying **one family**, the corpus
byte-clean, `formal_0001` green, and (Steps 1–3) its property's failure-expressible sibling.

## 6. Managing the proof cost

The historical wall was the rich codec's quantified contracts inflating quantifier instantiation
(E-matching) at every goal that could see them. Levers, in order of preference:

1. **Verify the codec once.** `#@ no_inline` on `_pack_inode`/`_unpack_inode` (each body → one VC, not
   re-proved per call site) and/or the separated minimal-context module — so the syscalls reason
   against a *contract*, not the body.
2. **Narrow what the syscalls see.** Track-B `#@ interface` on the codec so the os imports only the
   field-level facts it needs (e.g. the round-trip identity and field ranges), not the full per-byte
   ensures.
3. **Localize.** Only the inode-region reasoning needs the rich codec; the bitmap, directory, and data
   regions are framed out by their disjoint disk ranges — keep the rich facts from leaking into goals
   that do not need them.
4. **Budget.** Raise `--timelimit` for the codec-bearing goals; add a second prover for split VCs. This
   is the last lever, not the first — the dominant cost is instantiation breadth, not raw time.

The Step-0 probe exists precisely to learn whether levers 1–3 bring the cost under control before the
rest is built.

## 7. Faithfulness rules (non-negotiable)

- **No re-added round-trip axiom.** The round-trip must be *proven* from the leaves' value contracts.
  The os shed its codec axiom; it does not come back.
- **No totalized codec.** The byte leaves genuinely reject out-of-range input; their `requires` stay,
  and callers discharge them via the representation invariant — never by pretending the codec is total.
- **No vacuous success.** `\result == True` is earned by establishing the real success preconditions,
  not by returning `True` on failure paths. Every functional property ships a failure-expressible
  sibling.
- **A genuine SMT limit is a finding, not an axiom.** If `str_eq` does not discriminate, or a round-trip
  field truly cannot be discharged, surface and justify it explicitly and revisit the architecture —
  do not paper over it.

## 8. Fallback architecture — ghost refinement

If the Step-0 probe shows the rich codec is intractable in-context even with §6's levers, switch to a
data-refinement model: introduce a **ghost logical filesystem** (maps `inode# → fields`,
`inode# → content`, `name → inode#`) and a **representation invariant** tying it to the concrete disk
(`disk inode region == pack(ghost fields)`, `_dir_names == ghost names`, `data blocks == ghost
content`). Each syscall maintains the invariant; the functional properties P1–P4 are then proven against
the *ghost* model — value-level and cheap — while the invariant carries them down to the real bytes.
This is the standard way functional correctness of low-level code is verified (abstract spec +
refinement). It is heavier (the invariant must be maintained by every syscall) but moves the round-trip
cost out of every goal and into one invariant-preservation obligation per writer. Treat it as the
principled escalation, scoped only if the direct architecture's cost cannot be tamed.

## 9. Acceptance

Done when **all** hold:

1. `pure_lib_test/formal_0008.py` proves `\result == True` (*Valid*) for symbolic `f`, `c` in range.
2. The full os proof stays at **0 unproven**; `formal_0001` still passes.
3. The trusted-axiom base stays **one family** — no round-trip axiom reintroduced.
4. P1, P2, P3 each have a driver whose postcondition would **fail** if its fidelity were violated, so P4
   is established, not vacuous.
5. Corpus byte-clean; doc-coherency green; the os class invariants (disk-length, fd-column lengths,
   credential/clock non-negativity) preserved throughout.
