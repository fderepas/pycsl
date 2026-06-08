# c-impl.md — Track C: data refinement for the os inode (probe result + application plan)

**Date:** 2026-06-08
**Status:** Probe GREEN + application plan. The cheap probe (b-p4-rev2 §6) **passed**; the os
application is scoped below.
**Owner:** [STDLIB] (`pure_lib/os/**`) + [TOOL] (`src/pycsl/**`, L0″ for the coupling).
**Depends on:** B (committed `b3d65d1`), the field-access-arg passthrough (committed `8ed74d5`), L0′
(committed `8c7278e`).

---

## 1. The probe result (committed `8ed74d5`, driver 0661) — GREEN

**Question (b-p4-rev2 §4(c)):** does a typed-inode **representation invariant** discharge `_pack_inode`'s
18 real field-range `requires` at a call site, collapsing the 18×8 requires-bloat — *faithfully* (the
leaves keep their real preconditions; the ranges are supplied, not narrowed away)?

**Answer: yes.** A class whose `fields` array carries `0 <= self.fields[k] <= MAX_k` as a class
invariant discharges **all 18** of `_pack_inode`'s real range preconditions at `_pack_inode(self.fields)`
**from the invariant**, in ~4s for one call site (driver 0661). One tool gap had to close first: a
record-field array arg (`self.fields`) was clobbered to a placeholder by `_array_coerce_arg` (severing
it from its invariant) — fixed by passing through dotted field-access args.

**Crucially, this needs only L0′ (field access in an invariant → `Array.get`), NOT L0″** — a field-range
invariant contains no function call. So the *requires-collapse* (the actual P4 blocker) is reachable now;
**L0″ is only needed for the heavier coupling invariant** (§4).

## 2. What the os application actually requires (the real scope)

`_write_inode(self, inode_num, inode: list)` calls `_pack_inode(inode)`. The probe used a *class with a
maintained invariant*; the os inode is a **bare mutable `list`** populated from heterogeneous sources:

- **Literals** (in range by inspection): `root_inode = [512, 1, 2, 493, 0,…]`; `inode = [0,1,1,420,…]`.
- **Disk reads**: `inode = self._read_inode(n)` — fields are bytes-derived, bounded by the codec.
- **Computed mutations** (the hard part): `inode[0] = new_size` (`offset + written`), `inode[8+k] =
  p_block` (a block number), `inode[7] = self._now()` (a clock tick).

So the field ranges are not free — each computed mutation must be **provably in range**:
- `new_size ≤ disk_size = 131072 < 2³²` (uint32 size) — needs a *size ≤ disk* fact;
- `p_block ∈ [0, 256)` — already bounded by `_alloc_block`'s contract;
- `_now() ≥ 0` and `< 2³²` — needs a clock-bound invariant.

**This is why the requires-bloat timed out**: there is no maintained invariant tying these together, so
each `_write_inode` call site re-derives 18 ranges from scratch across the whole syscall. Track C's job
is to *install that invariant* so the ranges are maintained, not re-derived.

## 3. Application plan — give the inode a maintained field-range invariant

The faithful, probe-validated path (no totalizing — b-p4-rev2):

| Step | Action | Gate |
|---|---|---|
| **C0** | (done) probe + field-access passthrough + 0661 | ✓ `8ed74d5` |
| **C1** | Add `#@ requires 0 <= inode[k] <= MAX_k` (the 18 ranges) to **`_write_inode`** — its param precondition. `_pack_inode`'s requires then discharge from `_write_inode`'s precondition (one hop). | **[PROVE]** `_write_inode` proves; `_pack_inode`'s requires discharge from the param pre |
| **C2** | At each of the 6 syscall call sites, establish the 18 ranges for the `inode` being written. **Literals**: trivial. **Disk-read inodes**: from `_unpack_inode`'s ensures (each field is a bounded byte combination — needs `_unpack_inode` field-range ensures, an [STDLIB] contract add). **Computed mutations**: from the bounding facts (§2) — `new_size ≤ 131072`, `p_block` from `_alloc_block`, `_now()` bound. | **[PROVE]** each syscall discharges the 18 ranges; **[measure]** affordable (the probe shows ~4s/site, so ~6 sites ≈ linear) |
| **C3** | Apply B to `_pack_inode`: rich 18-field **definition** + `#@ interface ensures \length==64`. Now its ensures ride only revealing sites (none in os) and its requires discharge via C1/C2. | **[byte-diff]** os stub: `\length` + the 18 ranges *discharged at callers*; **[PROVE]** os **holds at 23** |
| **C4** | Re-prove the round-trip (`_read_inode(_write_inode(n,I)) == I` or field-wise) — now over the **real** os codec, with the ranges supplied by the invariant. | **[PROVE]** round-trip in os |
| **C5** | Corpus + formal + coverage + doc | green |

**The decisive open risk is C2** (the computed-mutation bounds), not C1/C3. The probe proved the
*mechanism*; C2 is whether the os's `new_size`/`_now()` bounds are *establishable* without a new blow-up.

> **C2 micro-probe: GREEN (driver 0662, ~5s).** A field-range invariant **survives computed mutations**
> — `self.fields[0] = new_size` (`requires new_size ≤ 131072 < 2³²`) and `self.fields[7] = tick`
> (bounded) — and the 18 `requires` **discharge AFTER the mutations** (the invariant is maintained for
> the mutated fields; the others survive by frame). So the mechanism for the hard case (bounded
> computed mutation preserving the representation invariant) is validated. What remains for the real os
> is *sourcing* the bounds (`new_size ≤ disk_size`, `_now()` bound, `p_block` from `_alloc_block`) and
> the model refactor (bare `list` inode → typed object carrying the invariant) — engineering, not an
> unknown mechanism.

## 3a. Refactor progress + the C2b finding (the disk-read path)

**C1 — proven (then reverted to keep os green).** Adding the 18 field-range `requires` to `_write_inode`
+ `_pack_inode`'s rich def: `_write_inode` proves standalone (`_pack_inode`'s requires discharge one hop
from the param requires), and a **literal-inode** syscall (`sys_mkdir`, inode `[0,1,1,420,…]`) discharges
the 18 ranges trivially. **But `sys_write` FAILS** — it reads its inode via `_read_inode`→`_unpack_inode`,
which only ensures `\length==18`, so the disk-read inode's field *values* are unknown-range.

**The disk-read path needs a chain, and every link is now probed GREEN:**
1. **`_unpack_inode` field-range ensures** — `0 <= \result[k] <= MAX_k`. Provable *from* byte bounds:
   `u16 = data[0]*256+data[1]` with `0<=data[i]<=255` proves `0<=u16<=65535` (probed ✓). But needs the
   input bytes ∈[0,255], i.e. ⇒
2. **A quantified disk byte-range invariant** `∀i. 0<=self.disk[i]<=255` — there is none today (the disk
   is `array int`). This was the feared array-state-wall risk; **it is affordable**:
   - byte write `disk[pos]=val` preserves it — **2s** (driver 0663);
   - **slice** write `disk[a:a+64]=data` (byte-valued) over the **full 131072** disk preserves it —
     **2s** (driver 0664). No blowup — Why3's array theory frames the localized update cheaply.

So **all five Track C mechanisms are GREEN**: 0661 (discharge), 0662 (survives computed mutation), C1
(`_write_inode` one-hop), 0663/0664 (quantified disk-byte invariant affordable), u16 (field-range from
bytes). The refactor is fully de-risked at the mechanism level.

**Remaining = pure application (large but no unknown):** add the disk-byte invariant to
`UnixInodeFileSystem`; add `_unpack_inode` field-range ensures; C1's `_write_inode` requires; `_pack_inode`
rich def + interface; then ensure **every** os disk write (inode, data block, bitmap, directory) writes
byte-valued data so the invariant is maintained — the one real application risk is a write that stores a
non-byte (would surface as a failed invariant-preservation VC, fail-loud), not a missing mechanism.

## 3b. Application launch findings (2026-06-09) — the real-os complexity, reverted to keep os green

Launched the full application (add the disk-content invariant + fix the writers). Findings:

- **Whole-disk byte invariant** (`∀i. 0<=disk[i]<=255`) generates fine but **breaks every one of the ~13
  disk writers** — each must now prove its written data is byte-valued (`__format_disk`, `__set_bitmap`,
  `__write_entry`, … all `remain unproven`/`FAILED`).
- **Region-scoped invariant** (`∀i∈[512,2560). …`, the inode region) is the right reduction in principle
  — data/bitmap/directory writes are outside the region and should be **framed** — BUT:
  - **Framing needs disjointness proofs** (`write_index ∉ [512,2560)`), which depend on **caller
    context** (the bitmap/data offsets). `--fun <method>` runs standalone and **can't see the caller's
    offset**, so it over-reports breakage; only a **full-os run (~20 min each)** truly assesses it.
  - **The bitmap writes via BITWISE ops** (`disk[p] |= (1<<b)`, uninterpreted `bit_*`) — so even where
    `__set_bitmap` writes, the result is **not provably ∈[0,255]**; preserving a byte invariant there
    needs a bit-level axiom (it already cites `Bitmap.bit_and_one_in_zero_one`), not just framing.
- **No incremental-green path**: the invariant breaks **all** writers at once; os only returns to 23
  once **every** writer is fixed (or framed) — so "gate os continuously" can't keep os green *during*
  the refactor, and each assessment costs a ~20-min full-os run.

**Conclusion (reverted — os back to 23):** Track C's *mechanisms* are all proven (§1, §3a, 0661–0664),
but the real-os *application* is a **multi-session, intricate** effort: per-writer disjointness (region
scope) **or** byte-source proofs (whole-disk), plus the bitmap's **bitwise byte-ness** (needs a
bit-axiom), assessed only by ~20-min full-os iterations. It is not completable in one stretch, and
half-applied it leaves os red. The honest next step is a *dedicated* application pass: region-scoped
invariant + fix the **two inode-region writers** (`_write_inode`, `__format_disk`, sourcing bytes from
a `_pack_inode` that ensures `0<=\result[i]<=255`) + supply caller-side disjointness for the framed
writers, iterating against full-os — banked here as scoped, not forced half-done.

## 3c. Application pass 2 (2026-06-09) — each piece proves standalone; the wall is in-context proof cost

Did the four application tasks. Each component proves **standalone**, but they do not yet *land
together* in the full os because of an **in-context proof-cost wall** (a function provable in seconds
standalone is slow/intractable inside the full `UnixInodeFileSystem` file).

- **C-app-3 `_pack_inode` rich def — GREEN.** Leaf-compositional body + definition (length + the 18 field
  VALUES + a quantified byte-ensures `∀i<64. 0<=result[i]<=255`) + interface (length + bytes). Proves
  `--fun` in ~minutes. The byte-ensures is what lets `_write_inode`'s blit preserve the region invariant.
- **C-app-2 `_unpack_inode` field-range ensures — proves standalone (12s), context-slow (>300s).**
  - Two pitfalls found + fixed in isolation: (1) the **block-field loop** must be **unrolled** (else the
    block ranges 8–17 need a loop invariant); (2) a **quantified** byte-requires (`∀i<64. 0<=data[i]<=255`)
    **times out on instantiation** — **specific** per-byte requires (`data[0..63]`) prove the 18 ranges
    in **12s** (standalone probe). The leaves already `ensures 0<=\result<=MAX`, so the field ranges
    follow directly *given* the byte bounds.
  - **But in the full file, `--fun _unpack_inode` times out >300s** — the context (other functions, the
    larger preamble/axioms) inflates each goal far beyond the 12s standalone cost.
- **C-app-1 region invariant + layout — understood.** Bitmaps live at byte_offset 0/4 → `[0,36)`,
  directory = block 5 → `[2560,3072)`, data = block ≥6 → `[3072,…)`: **every non-inode write is outside
  `[512,2560)`**, so they frame from existing block/offset bounds (the bitmap's bitwise byte-ness is a
  non-issue — it's outside the region). Only `_write_inode` + `__format_disk` write the region.
- **C1 `_write_inode` — proven** standalone (requires discharge one-hop); **literal-inode** syscalls
  (`sys_mkdir`) discharge trivially; **disk-read** syscalls (`sys_write`) need C-app-2's `_unpack_inode`
  ranges, which need the region invariant to feed the 64 byte-bounds at `_read_inode`.

**The recurring wall, named:** every richly-contracted codec function (`_pack_inode`, `_unpack_inode`,
the inode round-trip, B's `_pack_inode`-in-os) proves **standalone** but is **slow or intractable in
context** (full file / full os), and each iteration is a 300s–1200s run. Landing the full chain
(region invariant → `_unpack` ranges with `_read_inode` feeding 64 byte-bounds from the quantified disk
invariant → C1 → `__format_disk` → full-os framing of the non-inode writers → os@23) is a multi-step
grind where *each* step is a multi-hundred-second-to-20-minute proof, several of which need the same
kind of instantiation/loop tuning found above. **Reverted to keep os at 23.** This is not a missing
mechanism (all proven) — it is that the faithful, richly-contracted os is *proof-cost-bound in
aggregate*, the same wall `try.md` first hit, now confirmed to recur at each codec function and to
compound across the chain.

## 4. The coupling invariant + L0″ (the heavier, later milestone — distinct from C1–C5)

C1–C5 give a **verified, faithful, round-tripping codec inside os at 23** via a *field-range* invariant
(no L0″). The *full* abstraction barrier — syscalls reasoning over an **abstract inode** `ginode` and
never touching bytes — needs the **coupling invariant** `∀n. ginode[n] == _unpack_inode(disk[512+64n:+64])`,
which **calls `_unpack_inode` inside a class invariant** → the L0″ wall (`challenging-the-plan2.md`:
functions unbound in a class invariant). L0″ (a logic view of the codec usable in invariants) is the
prerequisite for *that* level. It is **not** required for C1–C5 (the requires-collapse), so it is
sequenced after — pursue it only if content-level syscall specs (reasoning about inode *contents*) are
wanted beyond the round-trip.

## 5. Soundness / faithfulness

- **No precondition is narrowed or totalized** (b-p4-rev2): `_pack_inode` and the leaves keep their real
  `requires`. The ranges are *supplied* by a maintained invariant — the faithful discharge.
- **B is unchanged**: the ensures-narrowing is sound (committed); C adds the requires-side discharge.
- **Fail-safe**: if a computed mutation cannot be proven in range (C2), that is a *real* finding (the os
  could write an out-of-range field that `_pack_inode` would raise on) — surfaced, not hidden.

> **In one line:** the C-probe is GREEN — a field-range representation invariant collapses `_pack_inode`'s
> 18×8 requires-bloat faithfully (driver 0661, needs L0′ + the now-landed field-access passthrough, NOT
> L0″). The os application (C1–C5) installs that invariant on the inode; its one real risk is C2 — proving
> the *computed* field mutations (`new_size ≤ 131072 < 2³²`, `_now()` bound, `p_block` from `_alloc_block`)
> are in range — which a one-syscall micro-probe should settle before the full sweep. The heavier coupling
> invariant (abstract-inode reasoning) needs L0″ and is a later, separate milestone.
