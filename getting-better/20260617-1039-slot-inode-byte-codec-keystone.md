# Gap-5 keystone: the `slot_inode` byte-codec lands as a primitive, but does NOT retire a dirscan trust

DATE: 2026-06-17
LOOP: test-supervise-sl, executing 17-1007-report.md step 1 (the keystone)

## What landed (DONE, verified)

A **cross-validated** forward (value) byte→decode axiom for the directory per-slot
inode field:

```
UnixFs.Dir.slot_inode_byte_decode :
  forall disk blk k b0 b1 [disk[blk*512 + 32*k]].
    disk[blk*512 + 32*k]     = b0 ->
    disk[blk*512 + 32*k + 1] = b1 ->
    slot_inode disk blk k = 256*b0 + b1
```

- Cross-validated: `test-suite/corpus/pycsl-reference/0711.proofs/{rocq,lean}/SlotInodeByteDecode.{v,lean}`.
  - Rocq (coqc, coq-4.14 switch): **Closed under the global context** — only abstract Section
    Variables, 0 `Axiom`/`Admitted`.
  - Lean ($HOME/.elan/bin): **"does not depend on any axioms"** (⊆ {propext, Quot.sound}).
  - This is even stronger than the bar: the fact is pure definitional unfolding (the decode is
    `256*rd(off) + rd(off+1)`, identical to the existing `EmptyDiskSlotsDead.v` definition).
- Wired: added to `_AXIOM_REGISTRY` in `src/pycsl/module6_whyml/preamble.py`, reusing the SAME
  abstract `slot_inode` symbol (no new `_AXIOM_FUNCTIONS` entry).
- Exhibited + tested: `test-suite/corpus/pycsl-reference/0711.py` — proves SUCCESS, all Valid,
  fast (≤33k steps). Two functions: the bare value fact, and the END-TO-END write rung (store
  the two big-endian bytes, conclude `slot_inode == inode_num`) — the exact shape
  `_write_dir_entry`/`_write_entry` would prove for their write-side `slot_inode` ensures.
- Inert/safe: cited NOWHERE in the committed os module. Full corpus byte-diff sweep =
  **0 differences** across all 601 shared `.mlw` (only new file: `0711.mlw`). proof2why3
  crosscheck = 0 FAIL (SKIP, the standard array-subscript parser-gap outcome, same as the
  sibling Dir axioms). Both gates unperturbed.

## The decisive finding: the keystone is NECESSARY but NOT SUFFICIENT to retire a dirscan trust

I piloted retiring the simplest write-side trust, `_write_dir_entry` (`\trusted reviewer:
dirscan-fidelity`), using the new axiom. Result, measured in `--fun` isolation:

1. **The inode-VALUE ensures proves.** With `_pack_direntry` strengthened to expose
   `\result[0]*256 + \result[1] == inode_num`, plus post-blit asserts materializing the byte
   terms in the axiom's trigger form, the body discharges
   `slot_inode(self.dir, blk, slot) == inode_num` — **Valid**. The keystone works.

2. **The trust does NOT retire**, because it bundles three obligations, only one of which the
   byte codec touches:
   - inode-field VALUE: `slot_inode == inode_num` — **byte-codec provable** (above).
   - name-field VALUE: `slot_name == name` — needs the `field_to_str` STRING codec threaded
     through `_pad_name`→blit→decode (the documented E-match-explosive part).
   - the `\forall k != slot` FRAME + the class invariant (`uniq`/`slots_lt32`) preservation —
     stated over the ABSTRACT `slot_inode`/`slot_name`. Once the body materializes concrete
     `self.dir[...]` byte terms (needed for rung 1), the new axiom + the uniq/slots_lt32 axiom
     web fire across the disk → **Type-invariant goals Timeout at 9.05M steps** (measured).
     This is exactly the global E-matching explosion the prior sessions documented
     ("DON'T concretize slot_name … would worsen the noise + risk the green __init__").

A `\trusted` is all-or-nothing per method; the value half proving while the frame+invariant
half explodes means the trust **stays**. Net TCB delta on the os: **0 (8→8)**.

## Why this sharpens (and partially refutes optimism in) 17-1007-report.md

The report's Gap-5 hypothesis was that a byte codec would, "in one stroke," retire the 6
dirscan trusts + close `_unpack_direntry` + unlock by-name resolution. The measured reality:
the byte codec retires the **inode-VALUE** sub-obligation only. The binding constraints are
(a) the **string** codec for the name field and (b) **class-invariant maintenance over the
abstract symbol surviving byte materialization** — neither of which the inode-byte codec
addresses, and (b) is the same 9M-step explosion wall the report's Part-1 route (b) hit.

So steps 2–5 (which depend on retiring trusts / a directory-region byte invariant riding
through every mutator) remain **blocked by the invariant-maintenance explosion**, not by the
absence of a byte decode. Per the plan's stop condition, I STOPPED here and logged this.

## What a future session needs (the real remaining work, in order)

1. **Tame the uniq/slots_lt32 E-matching under materialized byte terms.** The wall is that
   `slot_inode_byte_decode` (byte-keyed) coexisting with the uniq/slots_lt32 axioms (slot_inode-
   keyed) over the same disk explodes. Candidate: prove the frame/invariant maintenance ENTIRELY
   inside a cross-validated lemma keyed so NO byte term and NO slot_inode term coexist in any VC
   (the `remove_unique_absent` discipline, extended to the insert/write case with the byte rung
   folded away). Hard — this is the genuine research frontier.
2. **The `slot_name` string codec rung** (`field_to_str` threaded `_pad_name`→blit→decode) for
   the name-VALUE ensures — separately E-match-heavy (Phase-A measured ~23M steps for the
   round-trip alone).
3. Only with BOTH can a write-side dirscan trust retire; the read-side trusts (`_dir_lookup`/
   `_dir_find_slot`/`_dir_find_free`) ADDITIONALLY need the inductive loop→`dir_lookup`/scan
   fidelity, which is not byte-derivable at all (it is `scan_reflects_present`'s job).

## Ergonomic gap surfaced

Retiring a `\trusted` that bundles a VALUE ensures + a FRAME/invariant ensures is currently
all-or-nothing: there is no way to body-prove the provable sub-ensures while keeping the
unprovable ones trusted. A per-ensures trust granularity (`#@ \trusted reviewer: <kind>` on a
SINGLE clause, the rest body-verified) would let the byte-codec land the inode-VALUE half out
of the TCB today, shrinking the trusted SURFACE even where the whole method can't yet retire.
Worth considering as a PyCSL feature — it would make incremental de-trusting measurable.
