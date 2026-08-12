from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Set, Tuple

from module6_whyml.identifiers import whyml_ident, safe_mutex_name, safe_exc_name
from module6_whyml.ir_scanner import IRScanner


class PreambleEmissionMixin:
    """Preamble emission: top-of-file `use` clauses, exception type declarations, helper let-bindings, axiom blocks, shared state for the concurrent memory model, record/sum type declarations, and opaque class aliases. Mixed into Module6_WhyMLTranspiler."""

    # §2.1.12 — registry of hand-curated axiom bodies for `#@ proof`
    # qualnames. MVP step before `proof2why3` extraction lands (see
    # docs/cross-validated-spec-sources.md). Each entry's body is the canonical statement that
    # the paired Rocq + Lean theorems establish — cross-checked
    # manually for the MVP, automatically via the cross-check
    # pipeline in v1.
    _AXIOM_REGISTRY: Dict[str, str] = {
        # Pycsl.Reference.Gcd — Euclidean GCD properties.
        # Cross-validated by 0342.proofs/rocq/gcd.v + 0342.proofs/lean/Gcd.lean.
        # The `a >= 0 -> b >= 0 ->` side conditions on each entry mirror
        # the `nat`-lift: Rocq+Lean prove these theorems over `nat`, and
        # the WhyML `int` axioms add the non-negativity side conditions
        # explicitly. Identified as missing from gcd_step + gcd_result_nonneg
        # by `python -m pycsl.proof2why3.crosscheck` (sticky-01.md Phase 1+2+3 v0).
        "Pycsl.Reference.Gcd.gcd_result_nonneg":
            "forall a b : int. a >= 0 -> b >= 0 -> 0 <= gcd a b",
        "Pycsl.Reference.Gcd.gcd_result_positive":
            "forall a b : int. a >= 0 -> b >= 0 -> (a > 0 \\/ b > 0) -> gcd a b > 0",
        "Pycsl.Reference.Gcd.gcd_divides_a":
            "forall a b : int. a >= 0 -> b >= 0 -> (a > 0 \\/ b > 0) -> mod a (gcd a b) = 0",
        "Pycsl.Reference.Gcd.gcd_divides_b":
            "forall a b : int. a >= 0 -> b >= 0 -> (a > 0 \\/ b > 0) -> mod b (gcd a b) = 0",
        "Pycsl.Reference.Gcd.gcd_0":
            "forall a : int. a >= 0 -> gcd a 0 = a",
        "Pycsl.Reference.Gcd.gcd_step":
            "forall a b : int. a >= 0 -> b >= 0 -> b > 0 -> "
            "gcd a b = gcd b (mod a b)",
        "Pycsl.Reference.Gcd.gcd_greatest":
            "forall a b k : int. a >= 0 -> b >= 0 -> k >= 0 -> "
            "(a > 0 \\/ b > 0) -> "
            "k > 0 -> mod a k = 0 -> mod b k = 0 -> k <= gcd a b",

        # Pycsl.Reference.Perm — permutation framing lemmas over the
        # `\permutation` predicate (`predicate permut`). no-more-int A2b
        # stage-4: the uninterpreted `permut` is constrained by
        # proof-assistant-imported axioms. `permut_refl` (reflexivity) is the
        # first, cross-validated by 0538.proofs/rocq/Perm.v (Permutation_refl)
        # + 0538.proofs/lean/Perm.lean (List.Perm.refl). The axiom is stated
        # over `array int` (the logic model of an array), which the stage-4
        # spike verified is sound — no `seq` snapshot needed (Gap 2 obviated).
        "Pycsl.Reference.Perm.permut_refl":
            "forall s : array int. permut s s",
        # The framing lemma: reversing a list permutes its elements. The SMT
        # solver cannot derive this (uninterpreted `permut`, no multiset
        # reasoning) — it is the proof-assistant-imported axiom that does.
        # Cross-validated by 0539.proofs/rocq/Rev.v (`Permutation_rev`) +
        # 0539.proofs/lean/Rev.lean (`List.reverse_perm`).
        "Pycsl.Reference.Perm.rev_permutation":
            "forall s : array int. permut (array_rev s) s",

        # Pycsl.Reference.Json — an INDUCTIVE property over a recursive
        # `#@ datatype Json` (no-more-int A4 generalization demo). `json_mirror`
        # swaps every `JPair`'s children; mirroring twice is the identity.
        # Cross-validated by 0542.proofs/rocq/Json.v + lean/Json.lean
        # (`mirror_involution`, proved by structural induction). The axiom
        # quantifies over the user type `json`, which is why `#@ proof` axioms
        # are now emitted AFTER the type declarations.
        "Pycsl.Reference.Json.mirror_involution":
            "forall x : json. json_mirror (json_mirror x) = x",

        # UnixFs.Bitmap — bitwise properties needed by inode/block
        # bitmap allocators. Cross-validated by
        # unix-filesystem/UnixInodeFileSystem.proofs/rocq/UnixInodeFileSystem.v.
        # Discharges Z3 timeout on `(x >> y) & 1 ∈ {0, 1}` in
        # _get_bitmap (3.4B-step Z3 blowup → 0-step axiom citation).
        "UnixFs.Bitmap.bit_and_one_in_zero_one":
            "forall n : int. 0 <= bit_and n 1 /\\ bit_and n 1 < 2",

        # UnixFs.Struct — struct.pack / struct.unpack round-trip per
        # format slot_id. Cross-validated by the witness Coq model
        # in unix-filesystem/UnixInodeFileSystem.proofs/rocq/
        # UnixInodeFileSystem.v (Module UnixFs.Struct.Fmt_<id>).
        # Witness closes round-trip by `reflexivity`; the WhyML axiom
        # constrains the abstract `val function struct_pack_<id>` /
        # `val function struct_unpack_<id>` symbols emitted by
        # Module6's `_handle_struct_call` dispatch.
        #
        # Note: array equality in Why3 is by Array.= (extensional).
        # The tuple-result equality decomposes per-component, which
        # the SMT solver dispatches by structural matching.
        "UnixFs.Struct.i1a1.round_trip":
            "forall fmt : int. forall x0 : int. forall x1 : array int. "
            "struct_unpack_i1a1 fmt (struct_pack_i1a1 fmt x0 x1) = (x0, x1)",

        "UnixFs.Struct.i2.round_trip":
            "forall fmt x0 x1 : int. "
            "struct_unpack_i2 fmt (struct_pack_i2 fmt x0 x1) = (x0, x1)",

        "UnixFs.Struct.i18.round_trip":
            "forall fmt x0 x1 x2 x3 x4 x5 x6 x7 x8 x9 "
            "x10 x11 x12 x13 x14 x15 x16 x17 : int. "
            "struct_unpack_i18 fmt "
            "(struct_pack_i18 fmt x0 x1 x2 x3 x4 x5 x6 x7 x8 x9 "
            "x10 x11 x12 x13 x14 x15 x16 x17) "
            "= (x0, x1, x2, x3, x4, x5, x6, x7, x8, x9, "
            "x10, x11, x12, x13, x14, x15, x16, x17)",

        # ==========================================================================
        # Pycsl.Struct.Std (cleared-pack) — the FAITHFUL, GUARDED round-trip family
        # for a SINGLE standard-size unsigned-int struct slot ('>H' = u16, '>I'/'>L'
        # = u32). Unlike the legacy `UnixFs.Struct.iN.round_trip` (unguarded
        # shape-model witnesses proven by reflexivity over uninterpreted symbols),
        # these are anchored by CONCRETE big-endian base-256 BYTE-CODEC definitions
        # of pack/unpack, cross-validated in BOTH provers:
        #   test-suite/corpus/pycsl-reference/0753.proofs/{rocq/Struct.v,lean/Struct.lean}
        #   (Pycsl.Struct.Std.{round_trip_u16,round_trip_u32}; also size_u* and the
        #    guard_necessity_u* counterexamples showing the guard is load-bearing —
        #    unpack(pack 65536) = 0 ≠ 65536). Rocq: coqc exit 0, no Admitted/Axiom;
        #   Lean 4.31: lean exit 0, #print axioms ⊆ {propext, Classical.choice,
        #   Quot.sound}, no sorry.
        # The in-range guard is the SOUNDNESS PRECONDITION (real struct.pack RAISES
        # struct.error out-of-range for standard sizes): it is BOTH the pack `val`'s
        # `requires` (a call-site VC — see _AXIOM_FUNCTIONS below) AND the axiom
        # antecedent. Dropping it makes the law FALSE (byte truncation) — hence the
        # `# pycsl-expected: FAIL` negative driver 0755.
        # ==========================================================================
        "Pycsl.Struct.Std.round_trip_u16":
            "forall fmt x0 : int. 0 <= x0 < 65536 -> "
            "struct_unpack_fu16 fmt (struct_pack_fu16 fmt x0) = x0",

        "Pycsl.Struct.Std.round_trip_u32":
            "forall fmt x0 : int. 0 <= x0 < 4294967296 -> "
            "struct_unpack_fu32 fmt (struct_pack_fu32 fmt x0) = x0",

        # cleared-pack RESIDUALS (items 1-2): the faithful family widened to a
        # per-field width/signedness tag. Same anchor discipline as u16/u32:
        # pack/unpack are DEFINED as concrete big-endian base-256 byte codecs (signed
        # via two's complement) in the driver .proofs, so each round-trip is a genuine
        # theorem, guarded by the per-field in-range `requires` (faithful to CPython's
        # out-of-range struct.error). Cross-validated Rocq + Lean, no Admitted/sorry.
        #
        # item 1 — MULTI-SLOT unsigned '>HI' = (u16, u32), tags u16u32. The per-field
        # tag makes the symbol distinct from any legacy `iN` shape (closes the S0
        # collision: '>HH'=u16u16 and '<ii'=i32i32 no longer share `struct_pack_i2`).
        "Pycsl.Struct.Std.round_trip_u16u32":
            "forall fmt x0 x1 : int. 0 <= x0 < 65536 -> 0 <= x1 < 4294967296 -> "
            "struct_unpack_fu16u32 fmt (struct_pack_fu16u32 fmt x0 x1) = (x0, x1)",

        # item 2 — SIGNED singles (two's complement, range [-2^(8N-1), 2^(8N-1))).
        # '>h'=i16, '>i'/'>l'=i32, '>q'=i64.
        "Pycsl.Struct.Std.round_trip_i16":
            "forall fmt x0 : int. -32768 <= x0 < 32768 -> "
            "struct_unpack_fi16 fmt (struct_pack_fi16 fmt x0) = x0",
        "Pycsl.Struct.Std.round_trip_i32":
            "forall fmt x0 : int. -2147483648 <= x0 < 2147483648 -> "
            "struct_unpack_fi32 fmt (struct_pack_fi32 fmt x0) = x0",
        "Pycsl.Struct.Std.round_trip_i64":
            "forall fmt x0 : int. -9223372036854775808 <= x0 < 9223372036854775808 -> "
            "struct_unpack_fi64 fmt (struct_pack_fi64 fmt x0) = x0",

        # items 1+2 — MULTI-SLOT SIGNED '<ii' = (i32, i32), tags i32i32. Demonstrates
        # the tag resolving the collision: a two-int32 format is `struct_pack_fi32i32`,
        # NEVER the same symbol as a two-uint16 `>HH`.
        "Pycsl.Struct.Std.round_trip_i32i32":
            "forall fmt x0 x1 : int. -2147483648 <= x0 < 2147483648 -> "
            "-2147483648 <= x1 < 2147483648 -> "
            "struct_unpack_fi32i32 fmt (struct_pack_fi32i32 fmt x0 x1) = (x0, x1)",

        # item 3 — FIXED-BYTES 's' round-trip = array identity under the length guard.
        # '>4s' packs a 4-byte buffer verbatim and unpacks it back. Byte-codec anchor
        # is the trivial list identity `take N (pad N d) = d` when `length d = N`.
        "Pycsl.Struct.Std.round_trip_s4":
            "forall fmt : int, d : array int. Array.length d = 4 -> "
            "struct_unpack_fs4 fmt (struct_pack_fs4 fmt d) = d",

        # UnixFs.Dir — directory-scan reflection. The bounded scan over the 16
        # root-directory slots returns a non-negative inode IFF some live slot
        # decodes to `name`. INDUCTIVE over the slot loop (SMT times out:
        # gap-9, 14.6M/11.6M/18.8M steps). Cross-validated by
        # unix-filesystem/UnixInodeFileSystem.proofs/{rocq,lean}/UnixDirScan.{v,lean}
        # (UnixFs.Dir.scan_reflects_present): induction on the prefix length +
        # per-slot case split. Rocq: Closed under the global context (0 axioms);
        # Lean: axioms subseteq {propext, Quot.sound}. The slot_inode>=0 side
        # condition (decoded inode from unsigned bytes) is an EXPLICIT antecedent
        # `(forall j. 0 <= j < 16 -> slot_inode disk blk j >= 0)`, mirroring the
        # section-discharged `slot_inode_nonneg` / `hnn` hypothesis of both proofs
        # — keeping the axiom faithful (NOT over-strong). In WhyML it is
        # discharged by the companion `UnixFs.Dir.slot_inode_nonneg` axiom below
        # (the unsigned-byte fact), so callers cite both.
        "UnixFs.Dir.scan_reflects_present":
            "forall disk : array int. forall blk : int. forall name : string. "
            "( forall j : int. 0 <= j < 16 -> slot_inode disk blk j >= 0 ) -> "
            "( ( dir_lookup disk blk name >= 0 ) "
            "<-> "
            "( exists k : int. 0 <= k < 16 "
            "/\\ slot_inode disk blk k <> 0 "
            "/\\ slot_inode disk blk k < 32 "
            "/\\ slot_name disk blk k = name ) )",

        # =========================================================================
        # M4 rename directory-closure INFRASTRUCTURE (3 lemmas: dir_lookup_present_
        # witness, dir_lookup_present_zero_frame, dir_lookup_remove_absent). STATUS:
        # cross-validated (Rocq Closed / Lean ⊆ {propext, Quot.sound}) but currently
        # UNCITED. They PROVE sys_rename's directory presence/absence, but integrating
        # them does NOT close sys_rename: its add+remove proof is a genuine SMT
        # E-MATCHING DIVERGENCE (confirmed — 1.7M→4.9M steps at 30s→120s without
        # converging; every config tried: inline, lean/minimal no_inline helper, scalar
        # carry, all 3 lemmas — diverges or OOMs). Kept as ready infrastructure for a
        # future closure (a different prover, a restructured proof, or a reviewer-
        # justified trusted swap). See 14-1814-os-roadmap.md (sys_rename row).
        # =========================================================================
        # UnixFs.Dir.dir_lookup_present_witness (M4 rename — add+remove COEXISTENCE fix).
        # The NARROW-TRIGGER presence corollary of scan_reflects_present: a single
        # EXPLICIT witness slot k that is a live in-range match for `name` gives
        # dir_lookup >= 0 — WITHOUT introducing the matches-existential into the goal.
        #
        # Why a separate fact: scan_reflects_present's IFF triggers on every dir_lookup
        # term, so in sys_rename's final state it introduces the matches-∃ for BOTH the
        # present name (newpath) AND the absent name (oldpath); the oldpath-∃ then
        # interleaves with the absence axioms (remove_unique_absent / remove_reflects_
        # absent) — the E-matching balloon that left rename at 3 (the add+remove
        # coexistence). nm-FREE form: the looked-up name IS the witness slot's own name
        # (slot_name disk blk k), so the trigger [slot_inode disk blk k, slot_name disk
        # blk k] fires ONCE PER SLOT (~16) — NOT once per (name, slot) pair, which a
        # [dir_lookup, slot_inode] trigger would (O(names×slots) re-explosion). It
        # discharges the presence on the materialised witness slot (fslot, post-write+
        # zero), never co-introducing the ∃ that fed the absence search. The looked-up
        # `name` is recovered at the call site from slot_name(self.dir,5,fslot)==newpath.
        # The `forall j. slot_inode >= 0` antecedent (the scan's `<-` direction
        # uses it to bound the returned inode) is discharged at the call site by
        # slot_inode_nonneg, exactly as for scan_reflects_present. Reuses the SAME
        # dir_lookup/slot_inode/slot_name symbols (no new _AXIOM_FUNCTIONS entry).
        # Cross-validated by
        # unix-filesystem/UnixInodeFileSystem.proofs/{rocq,lean}/UnixDirScan.{v,lean}
        # (theorem dir_lookup_present_witness): the `<-`/witness direction of
        # scan_reflects_present. Rocq 8.20.1: Closed under the global context (0 axioms);
        # Lean 4.31.0: axioms ⊆ {propext, Quot.sound}.
        "UnixFs.Dir.dir_lookup_present_witness":
            "forall disk : array int, blk : int, k : int "
            "[dir_lookup disk blk (slot_name disk blk k)]. "
            "( forall j : int. 0 <= j < 16 -> slot_inode disk blk j >= 0 ) -> "
            "0 <= k < 16 -> slot_inode disk blk k <> 0 -> slot_inode disk blk k < 32 -> "
            "dir_lookup disk blk (slot_name disk blk k) >= 0",

        # UnixFs.Dir.dir_lookup_present_zero_frame (M4 rename — SCALAR presence carry).
        # Zeroing slot s preserves the PRESENCE of any other name: the present witness for
        # `name` in d0 cannot be slot s (its name is `name` <> slot_name d0 5 s), so it
        # survives the frame off s and still matches in d1. This is the unlink-style SCALAR
        # carry (cf. dir_lookup_frame): sys_rename establishes dir_lookup(newpath) >= 0 in
        # the POST-WRITE state, then carries it across the final old-slot zero AS A SCALAR
        # — so the presence proof (post-write) and the absence proof (post-zero) never do
        # heavy E-matching in the same disk state (the add+remove coexistence that the
        # single-state proof could not escape). Trigger [dir_lookup d1 5 name, slot_inode
        # d1 5 s] fires on the post-zero lookup + the removed slot; the antecedent
        # dir_lookup d0 5 name >= 0 is the already-established post-write presence (no new
        # term cascade). `name <> slot_name d0 5 s` is newpath != oldpath at the call site.
        # Reuses the SAME dir_lookup/slot_inode/slot_name symbols. Cross-validated by
        # unix-filesystem/UnixInodeFileSystem.proofs/{rocq,lean}/UnixDirScan.{v,lean}
        # (theorem dir_lookup_present_zero_frame): the surviving-witness argument over
        # scan_reflects_present. Rocq 8.20.1: Closed under the global context (0 axioms);
        # Lean 4.31.0: axioms ⊆ {propext, Quot.sound}.
        "UnixFs.Dir.dir_lookup_present_zero_frame":
            "forall d0 d1 : array int, s : int, name : string "
            "[dir_lookup d1 5 name, slot_inode d1 5 s]. "
            "0 <= s < 16 -> slot_inode d1 5 s = 0 -> "
            "( forall k : int. 0 <= k < 16 -> k <> s -> "
            "    slot_inode d1 5 k = slot_inode d0 5 k /\\ "
            "    slot_name  d1 5 k = slot_name  d0 5 k ) -> "
            "name <> slot_name d0 5 s -> "
            "dir_lookup d0 5 name >= 0 -> "
            "dir_lookup d1 5 name >= 0",

        # UnixFs.Content.block_content_eq_intro / _elim (gap-17 content round-trip) —
        # the DEFINITIONAL intro/elim for the folded `block_content_eq` content atom
        # (same zero-trust shape as ibv_intro/elim / uniq_intro/elim). `block_content_eq
        # d blk data` ≜ the first `length data` bytes of data-block `blk` equal `data`.
        # INTRO: sys_write / sys_pread prove the per-byte `\forall i` INLINE (from the
        # Array.blit / Array.sub spec, where it discharges) then fold to the atom, which
        # PROPAGATES across no_inline. ELIM: the round-trip caller unfolds the two atoms
        # (write's data-side + pread's result-side) INLINE and composes them to
        # `array_eq(result, data)`. Trigger [block_content_eq d blk data] so it fires
        # only where the atom appears (sys_write/sys_pread/wrappers/the round-trip test) —
        # never poisoning other methods.
        "UnixFs.Content.block_content_eq_intro":
            "forall d : array int, blk : int, data : array int "
            "[block_content_eq d blk data]. "
            "( forall i : int. 0 <= i < Array.length data -> d[blk * 512 + i] = data[i] ) "
            "-> block_content_eq d blk data",
        "UnixFs.Content.block_content_eq_elim":
            "forall d : array int, blk : int, data : array int "
            "[block_content_eq d blk data]. block_content_eq d blk data -> "
            "( forall i : int. 0 <= i < Array.length data -> d[blk * 512 + i] = data[i] )",

        # UnixFs.Dir.slot_inode_nonneg — the unsigned-byte fact: a decoded
        # directory-slot inode number is always non-negative (it is read from
        # unsigned disk bytes via `_unpack_direntry`'s uint fields). This is the
        # `slot_inode_nonneg` / `hnn` HYPOTHESIS of the scan_reflects_present
        # proofs (UnixDirScan.{v,lean}), surfaced as an explicit named fact so it
        # discharges the `forall j. slot_inode disk blk j >= 0` antecedent of
        # scan_reflects_present without a per-call class invariant. Same trust
        # class as the scan axiom (a faithful property of the abstract decode);
        # the proofs CARRY it as an assumption, so it is genuinely part of this
        # family's TCB, named here rather than smuggled into the IFF.
        "UnixFs.Dir.slot_inode_nonneg":
            "forall disk : array int. forall blk : int. forall k : int. "
            "slot_inode disk blk k >= 0",

        # UnixFs.Dir.slot_inode_byte_decode (Gap-5 keystone, WRITE SIDE) — the
        # forward (value) byte->decode fact. slot_inode (disk, blk, k) is the
        # 2-byte big-endian inode field of the 32-byte dirent at slot k of block
        # blk: 256*disk[blk*512+32*k] + disk[blk*512+32*k+1] (the SAME field
        # empty_disk_slots_dead / block5_decode_frame read; this is its forward
        # value direction). Lets a directory write helper that has just blitted
        # those two bytes and proved disk[off]=b0, disk[off+1]=b1 conclude
        # slot_inode disk blk k = 256*b0 + b1 = inode_num — RETIRING the write-side
        # dirscan-fidelity trust on _write_entry / _zero_entry / _write_dir_entry
        # without unfolding the abstract slot_inode symbol globally.
        #
        # TRIGGER DISCIPLINE (the keystone safety): keyed on the BYTE expression
        # [disk[blk * 512 + 32 * k]], NOT on [slot_inode disk blk k]. So it fires
        # ONLY where the explicit slot-byte term already appears (a write helper's
        # post-blit state), NEVER on the ubiquitous abstract slot_inode atoms that
        # the uniq / slots_lt32 / scan axiom web triggers on — avoiding the
        # measured global E-matching explosion of a `slot_inode = <bytes>`
        # definition (os-coverage-progress: "DON'T concretize slot_name", "would
        # worsen the noise + risk the green __init__"). The decode is read from the
        # bytes only when the bytes are present.
        #
        # Faithful — a property of _unpack_uint16_be of the dirent inode field; the
        # SAME slot_inode symbol (no new _AXIOM_FUNCTIONS entry). Cross-validated by
        # unix-filesystem/UnixInodeFileSystem.proofs/{rocq,lean}/SlotInodeByteDecode.{v,lean}
        # (theorem slot_inode_byte_decode): unfold the 2-byte decode, rewrite the
        # two byte hypotheses, close by reflexivity. Rocq 8.20.1: Closed under the
        # global context (only abstract Section Variables, 0 Axiom/Admitted); Lean
        # 4.30.0: "does not depend on any axioms" (subseteq {propext, Quot.sound}).
        "UnixFs.Dir.slot_inode_byte_decode":
            "forall disk : array int. forall blk : int. forall k : int. "
            "forall b0 b1 : int "
            "[disk[blk * 512 + 32 * k]]. "
            "disk[blk * 512 + 32 * k] = b0 -> "
            "disk[blk * 512 + 32 * k + 1] = b1 -> "
            "slot_inode disk blk k = 256 * b0 + b1",

        # UnixFs.Dir.slot_name_byte_decode (Gap-5 keystone, STRING half) — the
        # BRIDGE from the abstract per-slot NAME decode to the field_to_str codec.
        # A directory slot is 32 bytes (struct '>H30s'): a 2-byte big-endian inode
        # field then a 30-byte null-padded name field. slot_name (disk, blk, k) is
        # the decoded name in that 30-byte field, which starts 2 bytes into the
        # slot — i.e. EXACTLY field_to_str disk (blk*512+32*k+2) 30 (the SAME
        # scan-to-first-null '>Ns' decode validated in FieldToStrRoundTrip).
        #
        # This bridge composes with the already-registered field_to_str_round_trip
        # to give the write-side NAME byte->decode: a directory write helper that
        # has just blitted a fresh dirent name (disk[off+2+i]=ord(name[i]) for
        # i<len, disk[off+2+len]=0, len<=30, no embedded null) gets
        # field_to_str disk (off+2) 30 = name from the round-trip, then this bridge
        # rewrites that to slot_name disk blk k = name — the string twin of
        # slot_inode_byte_decode (the inode half). It is the BANKED string-half
        # keystone for the future directory write helpers; it does NOT by itself
        # retire any dirscan trust (that remains blocked on invariant maintenance).
        #
        # TRIGGER DISCIPLINE (the keystone safety, mirroring slot_inode_byte_decode):
        # keyed on the BYTE expression [disk[blk * 512 + 32 * k + 2]] (the FIRST
        # name-field byte), NOT on [slot_name disk blk k]. So it fires ONLY where an
        # explicit name-field-byte term already appears (a write helper's post-blit
        # state), NEVER on the ubiquitous abstract slot_name atoms that the uniq /
        # dir_lookup / scan axiom web triggers on — avoiding the measured global
        # string E-matching explosion. The decode is read from the bytes only when
        # the bytes are present.
        #
        # SMT cannot discharge the slot_name=name CONCLUSION directly: that is the
        # field_to_str round-trip, by string EXTENSIONALITY over the 30-byte scan
        # (the measured ~23M-step Alt-Ergo/Z3 string wall). So this bridge is the
        # SAME cited-axiom trust class as field_to_str_round_trip: SMT only ever
        # APPLIES the bridge equality (O(1)) and the round-trip (O(1)); all the
        # extensionality reasoning is discharged offline in the proof assistants.
        #
        # Faithful — slot_name is the dirent name field of the SAME 32-byte '>H30s'
        # dirent the rest of UnixFs.Dir reads; the SAME abstract slot_name symbol
        # (no new _AXIOM_FUNCTIONS entry). Cross-validated by
        # test-suite/corpus/pycsl-reference/0712.proofs/{rocq,lean}/SlotNameByteDecode.{v,lean}
        # (theorem slot_name_byte_decode): slot_name is defined there as
        # field_to_str (slot_off blk k + 2) 30 over the scan-to-first-null model,
        # and the write-direction round-trip is proved by string extensionality (no
        # admits). Rocq 8.20.1: Closed under the global context (0 Axiom/Admitted,
        # only the abstract Section Variable rd); Lean 4.31.0: #print axioms ⊆
        # {propext, Quot.sound}.
        "UnixFs.Dir.slot_name_byte_decode":
            "forall disk : array int. forall blk : int. forall k : int "
            "[disk[blk * 512 + 32 * k + 2]]. "
            "slot_name disk blk k = field_to_str disk (blk * 512 + 32 * k + 2) 30",

        # UnixFs.Dir.remove_reflects_absent (gap-11) — the ABSENCE twin of
        # scan_reflects_present. After the live entry at slot s is zeroed
        # (remove-witness: slot_inode disk blk s = 0) and provided `name` lived
        # only at s (uniqueness: every OTHER slot decoding to `name` is dead),
        # the bounded 16-slot scan finds no match, so dir_lookup < 0. This is the
        # `<-`/absence half of scan_reflects_present's IFF specialised to an empty
        # matches-set; the remove-witness and uniqueness are explicit HYPOTHESES
        # (NOT assertions), exactly the gap-9 trust class. Cross-validated by
        # unix-filesystem/UnixInodeFileSystem.proofs/{rocq,lean}/UnixDirScanAbsent.{v,lean}
        # (theorem remove_reflects_absent): same scan_reflects_prefix induction.
        # Rocq: Closed under the global context (0 axioms); Lean: axioms subseteq
        # {propext, Quot.sound}. The `forall j. slot_inode disk blk j >= 0`
        # antecedent is discharged at the call site by slot_inode_nonneg (above);
        # the `0 <= s < 16` antecedent is carried for call-site symmetry (vacuous
        # in both proofs — the witness alone empties the matches-set). Reuses the
        # SAME abstract slot_inode/slot_name/dir_lookup symbols (no new
        # _AXIOM_FUNCTIONS entry needed).
        "UnixFs.Dir.remove_reflects_absent":
            "forall disk : array int. forall blk : int. forall name : string. "
            "forall s : int. "
            "( forall j : int. slot_inode disk blk j >= 0 ) -> "
            "( 0 <= s < 16 ) -> "
            "( slot_inode disk blk s = 0 ) -> "
            "( forall k : int. 0 <= k < 16 -> k <> s -> "
            "    slot_name disk blk k = name -> slot_inode disk blk k = 0 ) -> "
            "dir_lookup disk blk name < 0",

        # UnixFs.Dir.remove_unique_absent (M4 directory-absence fix) — the PRODUCER
        # twin of remove_reflects_absent. remove_reflects_absent CONSUMES the absence
        # witness (every other same-named slot is dead) to conclude dir_lookup < 0;
        # this lemma PRODUCES that witness from the directory invariants. Over a
        # pre-removal disk d0 that is `uniq` + `slots_lt32` (the FOLDED predicates,
        # taken as opaque hypotheses — NOT their unfolded \forall i,j bodies) where
        # slot s is the live entry being removed, and a post-removal disk d1 equal to
        # d0 off slot s (frame) with slot s now dead: every OTHER slot k whose name
        # equals the removed name (slot_name d0 5 s) is dead on d1.
        #
        # CRITICAL — why this is stated over the FOLDED `uniq`/`slots_lt32` atoms: the
        # removers (sys_unlink/sys_rename) carry `uniq self.disk` as a class invariant
        # but CANNOT have uniq_elim/slots_lt32_elim in scope (their \forall i,j /
        # \forall k instantiate combinatorially in the term-rich remover bodies → the
        # E-matching explosion that blocks M4 — 15-0838-remove-unique-absent.md §2).
        # By taking `uniq d0`/`slots_lt32 d0` as OPAQUE hypotheses and discharging
        # all the unfolding INSIDE the cross-validated proof, the removers APPLY this
        # in O(1) with NO elim in their VC. Multi-trigger [slot_inode d1 5 s,
        # slot_inode d0 5 s] (the block5_decode_frame precedent) so it fires exactly
        # for the removed slot. Reuses the SAME uniq/slots_lt32/slot_inode/slot_name
        # symbols (no new _AXIOM_FUNCTIONS entry). Cross-validated by
        # unix-filesystem/UnixInodeFileSystem.proofs/{rocq,lean}/RemoveUniqueAbsent.{v,lean}
        # (theorem remove_unique_absent): one application of `uniq` at the pair (k,s),
        # finite, no induction. Rocq 8.20.1: Closed under the global context (0 axioms);
        # Lean 4.30.0: does not depend on any axioms.
        "UnixFs.Dir.remove_unique_absent":
            "forall d0 d1 : array int, s : int "
            "[slot_inode d1 5 s, slot_inode d0 5 s]. "
            "uniq d0 -> slots_lt32 d0 -> "
            "0 <= s < 16 -> slot_inode d0 5 s <> 0 -> slot_inode d1 5 s = 0 -> "
            "( forall k : int. 0 <= k < 16 -> k <> s -> "
            "    slot_inode d1 5 k = slot_inode d0 5 k ) -> "
            "( forall k : int. 0 <= k < 16 -> k <> s -> "
            "    slot_name  d1 5 k = slot_name  d0 5 k ) -> "
            "( forall k : int. 0 <= k < 16 -> k <> s -> "
            "    slot_name d1 5 k = slot_name d0 5 s -> slot_inode d1 5 k = 0 )",

        # UnixFs.Dir.dir_lookup_remove_absent (M4 rename — add+remove COEXISTENCE fix).
        # The COMBINED, narrow-trigger absence: remove_unique_absent (produces the
        # empty-matches witness from uniqueness) FUSED with remove_reflects_absent
        # (concludes dir_lookup < 0), as ONE applied fact keyed on the removed slot s.
        # Why combined+narrow: remove_reflects_absent alone triggers on every dir_lookup
        # term, so it fires for the PRESENT name too (newpath, and the per-slot
        # dir_lookup(slot_name k) terms the presence witness creates) — trying to prove
        # those absent (false) is the absence-side E-matching balloon. nm-free: the absent
        # name IS the removed slot's old name slot_name d0 5 s, and the multi-trigger
        # [slot_inode d1 5 s, slot_inode d0 5 s] (the remove_unique_absent precedent) fires
        # exactly for the removed slot — NOT on dir_lookup — so it never matches the
        # presence terms. The looked-up `oldpath` is recovered at the call site from the
        # carried slot_name(self.dir,5,old_slot)==oldpath. `forall j. slot_inode d1 5 j >= 0`
        # discharged by slot_inode_nonneg. Reuses the SAME uniq/slots_lt32/dir_lookup/
        # slot_inode/slot_name symbols (no new _AXIOM_FUNCTIONS entry). Cross-validated by
        # unix-filesystem/UnixInodeFileSystem.proofs/{rocq,lean}/UnixDirScanAbsent.{v,lean}
        # (theorem dir_lookup_remove_absent): remove_unique_absent's uniqueness argument
        # inlined + remove_reflects_absent. Rocq 8.20.1: Closed under the global context
        # (0 axioms); Lean 4.31.0: axioms ⊆ {propext, Quot.sound}.
        "UnixFs.Dir.dir_lookup_remove_absent":
            "forall d0 d1 : array int, s : int "
            "[slot_inode d1 5 s, slot_inode d0 5 s]. "
            "( forall j : int. slot_inode d1 5 j >= 0 ) -> "
            "uniq d0 -> slots_lt32 d0 -> "
            "0 <= s < 16 -> slot_inode d0 5 s <> 0 -> slot_inode d1 5 s = 0 -> "
            "( forall k : int. 0 <= k < 16 -> k <> s -> "
            "    slot_inode d1 5 k = slot_inode d0 5 k ) -> "
            "( forall k : int. 0 <= k < 16 -> k <> s -> "
            "    slot_name  d1 5 k = slot_name  d0 5 k ) -> "
            "dir_lookup d1 5 (slot_name d0 5 s) < 0",

        # ============================================================================
        # FOLDED directory-invariant MAINTENANCE facts (M4 — 15-0838 Part A, sound
        # realization). These REPLACE uniq_intro/uniq_elim/slots_lt32_intro/
        # slots_lt32_elim. The elims unfold the FOLDED `uniq`/`slots_lt32` class-inv
        # atoms into a nested `forall i,j` / `forall k`, triggered on the ubiquitous
        # `uniq self.disk` atom — which E-match-explodes in the term-rich directory
        # removers (15-0838 §2). The cited-axiom path is per-MODULE, so "cite the
        # elim only in leaf writers" does NOT scope it away from the removers
        # (15-0838's Part A mechanism is unsound). The sound fix: state each
        # establishment / frame / zero / insert maintenance step over the OPAQUE
        # `uniq`/`slots_lt32` predicates, discharging the unfolding inside a
        # cross-validated proof — so NO method's VC ever carries the explosive nested
        # quantifiers. Triggers bind all binders and fire O(1) at the writer/
        # constructor site (no nested quantifier introduced into any goal). All
        # cross-validated by unix-filesystem/UnixInodeFileSystem.proofs/{rocq,lean}/
        # DirInvariantMaintenance.{v,lean}: Rocq Closed under the global context;
        # Lean depends on no axioms. Reuse the SAME uniq/slots_lt32/slot_inode/
        # slot_name symbols (no new _AXIOM_FUNCTIONS entry).

        # ESTABLISH: a disk whose every block-5 slot is dead satisfies the invariant
        # (the constructor's Array.make-0 witness, via empty_disk_slots_dead).
        "UnixFs.Dir.establish_uniq":
            "forall d : array int [uniq d]. "
            "( forall k : int. 0 <= k < 16 -> slot_inode d 5 k = 0 ) -> uniq d",
        "UnixFs.Dir.establish_slots_lt32":
            "forall d : array int [slots_lt32 d]. "
            "( forall k : int. 0 <= k < 16 -> slot_inode d 5 k = 0 ) -> slots_lt32 d",

        # NOTE: frame_preserves_uniq / frame_preserves_slots_lt32 RETIRED (M4 #1) — with
        # the root directory in its own field self.dir, non-directory writes (assigns
        # self.disk) preserve uniq(self.dir)/slots_lt32(self.dir) from the frame alone, so
        # these frame facts are obsolete. Cross-validated proofs kept in
        # DirInvariantMaintenance.{v,lean} for reference.

        # ZERO: clearing slot s dead (the remover's _zero_entry), rest framed,
        # preserves the invariant (the live set only shrinks).
        "UnixFs.Dir.zero_preserves_uniq":
            "forall d0 d1 : array int, s : int [slot_inode d1 5 s, uniq d0]. "
            "uniq d0 -> slot_inode d1 5 s = 0 -> "
            "( forall k : int. 0 <= k < 16 -> k <> s -> "
            "    slot_inode d1 5 k = slot_inode d0 5 k /\\ "
            "    slot_name  d1 5 k = slot_name  d0 5 k ) -> "
            "uniq d1",
        "UnixFs.Dir.zero_preserves_slots_lt32":
            "forall d0 d1 : array int, s : int [slot_inode d1 5 s, slots_lt32 d0]. "
            "slots_lt32 d0 -> slot_inode d1 5 s = 0 -> "
            "( forall k : int. 0 <= k < 16 -> k <> s -> "
            "    slot_inode d1 5 k = slot_inode d0 5 k ) -> "
            "slots_lt32 d1",

        # INSERT: slot s becomes live with a name NOT already live (the EEXIST guard),
        # rest framed (the directory adders' _write_entry). nm-free: the inserted name
        # is `slot_name d1 5 s` itself, so the fact triggers without a name binder.
        "UnixFs.Dir.insert_preserves_uniq_folded":
            "forall d0 d1 : array int, s : int [slot_name d1 5 s, uniq d0]. "
            "uniq d0 -> 0 <= s < 16 -> "
            "( forall k : int. 0 <= k < 16 -> "
            "    slot_inode d0 5 k <> 0 -> slot_inode d0 5 k < 32 -> "
            "    slot_name d0 5 k <> slot_name d1 5 s ) -> "
            "( forall k : int. 0 <= k < 16 -> k <> s -> "
            "    slot_inode d1 5 k = slot_inode d0 5 k /\\ "
            "    slot_name  d1 5 k = slot_name  d0 5 k ) -> "
            "( slot_inode d1 5 s <> 0 -> slot_inode d1 5 s < 32 ) -> "
            "uniq d1",
        "UnixFs.Dir.insert_preserves_slots_lt32":
            "forall d0 d1 : array int, s : int [slot_inode d1 5 s, slots_lt32 d0]. "
            "slots_lt32 d0 -> 0 <= s < 16 -> slot_inode d1 5 s < 32 -> "
            "( forall k : int. 0 <= k < 16 -> k <> s -> "
            "    slot_inode d1 5 k = slot_inode d0 5 k ) -> "
            "slots_lt32 d1",

        # ====================================================================
        # ROUTE 1 (test-supervise-sl 2026-06-19): the UNIQUE-MARKER-ATOM form of
        # the folded byte-rung directory-invariant maintenance fact for the dir
        # mutators (_write_dir_entry / _zero_entry).
        #
        # WHY (the trigger-poison wall, 20260618-2350 + catalog-B):
        #   The byte-keyed fold `insert/zero_preserves_dir_invariant_blit` keyed on
        #   `[d1[2560 + 32 * s]]` is CORRECT logic (cross-validated zero-TCB) but its
        #   byte key matches the SHAPE `disk[2560 + <expr>]` — EXACTLY the index every
        #   block-5 byte read produces. So it fires INSIDE the pure-byte helper
        #   `_blit_dir_entry`, dragging the abstract slot_inode/slot_name/uniq/slots_lt32
        #   web into that helper's byte VC -> Timeout 869,354,004 steps / OOM.
        #
        # THE FIX (gap-17 `block_content_eq` discipline): introduce a UNIQUE
        # uninterpreted predicate `dir_blit_marker d0 d1 s b0 b1` (declared in
        # _AXIOM_FUNCTIONS["UnixFs.Dir."]) and key BOTH the byte->marker intro AND the
        # marker->maintenance facts on `[dir_blit_marker d0 d1 s b0 b1]`. The marker
        # atom appears ONLY where the genuine mutator body asserts it
        # (`#@ assert dir_blit_marker(...)` at the real apply site) — it CANNOT match a
        # bare `disk[2560 + <expr>]` byte read, so the maintenance axioms never fire in
        # `_blit_dir_entry` or any other block-5 toucher. The axiom fires EXACTLY ONCE,
        # at the asserted marker.
        #
        # ZERO-TCB / cross-validation: the three facts are the SAME logic as
        # insert/zero_preserves_dir_invariant_blit, refactored through the marker.
        #   - dir_blit_marker_intro is DEFINITIONAL (the marker is conservatively DEFINED
        #     by its byte hypotheses; the intro is one direction of `marker <-> bytes`,
        #     used to ESTABLISH the marker from the bytes). ZERO trust.
        #   - dir_blit_marker_insert / _zero are the cross-validated maintenance steps:
        #     from the marker (= the byte facts, by definition) + uniq/slots_lt32 d0 +
        #     freshness, conclude value + frame + uniq + slots_lt32. Cross-validated by
        #     test-suite/corpus/pycsl-reference/0716.proofs/{rocq,lean}/DirBlitMarker.{v,lean}
        #     (Rocq Section-Variables-only / Closed under global context; Lean
        #     [propext, Quot.sound]). In the kernel the marker is DEFINED as the
        #     conjunction of its byte hypotheses, so dir_blit_marker_intro is `fun h => h`
        #     (definitional) and the maintenance theorems are the blit theorems with the
        #     byte hyps packaged behind the definition — same proof, zero new TCB.
        #
        # No byte term and no slot atom ever coexist in a body VC: `_blit_dir_entry`
        # carries only bytes (and the marker trigger cannot match its byte reads);
        # `_write_dir_entry` carries the marker atom + slot atoms (its contract already
        # references slot_inode/slot_name — that is the genuine apply site, where slot
        # atoms are expected) but NO loose `disk[2560+...]` blit term in the slot-web VC.
        # dir_blit_marker_intro (DEFINITIONAL, zero trust): the marker is conservatively
        # DEFINED as the conjunction of ALL the byte facts a directory-entry blit at slot
        # s establishes — the two inode bytes (b0,b1), the per-char name-field bytes, the
        # null-pad, and the byte-region frame — PLUS the name well-formedness the
        # round-trip needs (len<=30, no embedded null). The intro fires ONLY on the marker
        # atom (the trigger), so it never matches a bare disk[...] read. The string codec
        # (field_to_str) is referenced ONLY here behind the marker, NOT cited module-wide,
        # so the byte->string round-trip never poisons a sibling byte mutator.
        "UnixFs.Dir.dir_blit_marker_intro":
            "forall d0 d1 : array int, s b0 b1 : int, name : string "
            "[dir_blit_marker d0 d1 s b0 b1 name]. "
            "0 <= String.length name -> String.length name <= 30 -> "
            "d1[2560 + 32 * s] = b0 -> d1[2560 + 32 * s + 1] = b1 -> "
            "( forall i : int. 0 <= i < String.length name -> "
            "    Char.code (Char.get name i) <> 0 ) -> "
            "( forall i : int. 0 <= i < String.length name -> "
            "    d1[2560 + 32 * s + 2 + i] = Char.code (Char.get name i) ) -> "
            "( String.length name < 30 -> d1[2560 + 32 * s + 2 + String.length name] = 0 ) -> "
            "( forall b : int. 0 <= b < 512 -> "
            "    (b < 32 * s \\/ 32 * s + 32 <= b) -> d1[2560 + b] = d0[2560 + b] ) -> "
            "dir_blit_marker d0 d1 s b0 b1 name",
        # dir_blit_marker_intro_zero (ZERO-ENTRY intro corollary, cross-validated):
        # establish the marker for a ZEROED entry (b0=b1=0, EMPTY name) from the
        # MINIMAL byte facts. The general dir_blit_marker_intro above carries EIGHT
        # antecedents (the two inode bytes, the per-char name-field bytes, the per-char
        # nonzero codes, the null-pad, the name-len bounds, and the byte-region frame);
        # in the FULL-module aggregate E-matching context establishing the marker
        # through it for _zero_entry costs ~314K steps (measured in --fun) and the
        # full-module aggregate tips it OVER the prover step budget (Unknown). For a
        # ZEROED entry the name is EMPTY (String.length name = 0), so the two per-char
        # foralls are VACUOUS, the len bounds are trivial, and the null-pad collapses to
        # the SINGLE byte fact d1[2560+32*s+2] = 0. This lean intro establishes the
        # marker from just the two inode-byte pins, the head name byte = 0, and the
        # byte-region frame, firing the marker fold in ONE cheap marker-keyed step — the
        # zero-entry twin of dir_blit_marker_frame_only's lean specialisation for
        # _write_dir_entry's frames. The conclusion keeps b0,b1 universally quantified
        # and pins them to the disk bytes (so it matches the ASSERTED atom
        # `dir_blit_marker(.., self.dir[2560+32*slot], self.dir[2560+32*slot+1], "")`);
        # b0,b1 themselves need NOT be individually 0 — the marker carries them opaquely
        # and dir_blit_marker_value_inode later concludes slot_inode = 256*b0+b1 (= 0 via
        # _blit_dir_entry's sum ensures), so no per-byte zero fact is needed. It is the
        # SAME conjunction the general intro builds, specialised to the empty name;
        # NOTHING is widened — the trigger stays the marker atom. Cross-validated by
        # test-suite/corpus/pycsl-reference/0716.proofs/{rocq,lean}/DirBlitMarker.{v,lean}
        # (theorem dir_blit_marker_intro_zero): Rocq Section-Variables-only / Closed
        # under the global context; Lean #print axioms ⊆ {propext, Quot.sound}.
        "UnixFs.Dir.dir_blit_marker_intro_zero":
            "forall d0 d1 : array int, s b0 b1 : int, name : string "
            "[dir_blit_marker d0 d1 s b0 b1 name]. "
            "String.length name = 0 -> "
            "d1[2560 + 32 * s] = b0 -> d1[2560 + 32 * s + 1] = b1 -> "
            "d1[2560 + 32 * s + 2] = 0 -> "
            "( forall b : int. 0 <= b < 512 -> "
            "    (b < 32 * s \\/ 32 * s + 32 <= b) -> d1[2560 + b] = d0[2560 + b] ) -> "
            "dir_blit_marker d0 d1 s b0 b1 name",
        # dir_blit_marker_insert (cross-validated): from the marker (= the byte facts +
        # name well-formedness, by definition) + uniq/slots_lt32 d0 + inode range +
        # freshness, conclude BOTH slot VALUE decodes (inode AND name=name), the
        # slot-locality frame, uniq d1, slots_lt32 d1 — in ONE marker-keyed step. The
        # name VALUE comes from the field_to_str round-trip discharged INSIDE the kernel
        # proof (0716 DirBlitMarker), so the os body provides ONLY the marker atom and
        # NEVER materializes the string codec in its VC.
        "UnixFs.Dir.dir_blit_marker_insert":
            "forall d0 d1 : array int, s b0 b1 : int, name : string "
            "[dir_blit_marker d0 d1 s b0 b1 name]. "
            "dir_blit_marker d0 d1 s b0 b1 name -> "
            "uniq d0 -> slots_lt32 d0 -> 0 <= s < 16 -> "
            "256 * b0 + b1 <> 0 -> 256 * b0 + b1 < 32 -> "
            # VACUITY REPAIR (v3): freshness restricted to k <> s. The target slot s
            # is being OVERWRITTEN, so whether d0's slot s already held `name` is
            # irrelevant to whether the insert manufactures a duplicate live-name pair.
            # The original all-k freshness was OVER-STRONG: under the in-place-mutation
            # `\old(self.dir) == self.dir` collapse (the blit is an opaque val that
            # mutates the array in place, so d0 and d1 are the SAME array term in the
            # body VC), the all-k antecedent fired at k=s on the POST-state — where slot
            # s IS live with `name` — forcing slot_name=name AND (from freshness)
            # slot_name<>name, i.e. False (the live-branch inconsistency). The Rocq/Lean
            # cross-validation only ever applies freshness at slots <> s (DirBlitMarker.v
            # Hfresh used at j<>s / i<>s only), so the k<>s-restricted axiom is the SAME
            # theorem with an unused hypothesis dropped — still zero-TCB.
            "( forall k : int. 0 <= k < 16 -> k <> s -> "
            "    slot_inode d0 5 k <> 0 -> slot_inode d0 5 k < 32 -> "
            "    slot_name d0 5 k <> name ) -> "
            "( slot_inode d1 5 s = 256 * b0 + b1 "
            "  /\\ slot_name d1 5 s = name "
            "  /\\ ( forall k : int. 0 <= k < 16 -> k <> s -> "
            "         slot_inode d1 5 k = slot_inode d0 5 k /\\ "
            "         slot_name  d1 5 k = slot_name  d0 5 k ) "
            "  /\\ uniq d1 /\\ slots_lt32 d1 )",
        # dir_blit_marker_frame_only (SPIKE-2, cross-validated): the SLOT-LOCALITY
        # FRAME alone, marker-keyed. From the marker (= the byte facts, by
        # definition) and the slot-in-range fact, conclude that EVERY slot k <> s
        # decodes IDENTICALLY in d1 and d0 — WITHOUT needing uniq/slots_lt32/range/
        # freshness. This is a STRICT corollary of dir_blit_marker_insert: it is
        # `slot_frame_of_region` (DirBlitMarker.{v,lean}) applied to the marker
        # definition's byte-region-frame conjunct. dir_blit_marker_insert ALREADY
        # derives this exact frame conjunct (`Hsf`/`hsf`) purely from the marker's
        # frame component, independent of the value/uniq/freshness antecedents, so
        # the corollary is the SAME sub-derivation exposed as its own theorem — zero
        # new TCB. WHY EMIT IT SEPARATELY: in the FULL-module aggregate E-matching
        # context, the two `forall k<>s` frame postconditions of _write_dir_entry
        # starve when forced to go through the four-way conjunction of the heavier
        # _insert axiom (it drags slot_name VALUE + uniq d1 + slots_lt32 d1 into the
        # frame VC). This lean, frame-only marker-keyed fact lets the frame goals
        # close directly. Cross-validated by
        # test-suite/corpus/pycsl-reference/0716.proofs/{rocq,lean}/DirBlitMarker.{v,lean}
        # (theorem dir_blit_marker_frame_only): Rocq Section-Variables-only / Closed
        # under the global context; Lean #print axioms ⊆ {propext, Quot.sound}.
        "UnixFs.Dir.dir_blit_marker_frame_only":
            "forall d0 d1 : array int, s b0 b1 : int, name : string "
            "[dir_blit_marker d0 d1 s b0 b1 name]. "
            "dir_blit_marker d0 d1 s b0 b1 name -> "
            "0 <= s < 16 -> "
            "( forall k : int. 0 <= k < 16 -> k <> s -> "
            "    slot_inode d1 5 k = slot_inode d0 5 k /\\ "
            "    slot_name  d1 5 k = slot_name  d0 5 k )",
        # dir_blit_marker_value_inode (ZERO-ENTRY corollary, cross-validated): the
        # inode VALUE decode alone, marker-keyed. From the marker (= the byte facts,
        # by definition) conclude slot_inode d1 5 s = 256 * b0 + b1 — needing ONLY the
        # marker's two inode-byte conjuncts (d1[2560+32*s]=b0, d1[2560+32*s+1]=b1), NOT
        # liveness/uniq/slots_lt32/range/freshness. It is the `Hvali`/`hvali`
        # sub-derivation that dir_blit_marker_insert performs (unfold slot_inode,
        # rewrite the two inode bytes), exposed as its own theorem. CRUCIALLY, unlike
        # dir_blit_marker_insert it does NOT require 256*b0+b1 <> 0, so it APPLIES to
        # the REMOVE primitive _zero_entry (b0=b1=0): the caller instantiates it to
        # slot_inode self.dir 5 slot = 256*0+0 = 0 (the dead-slot value postcondition).
        # The lone marker-keyed value fact lets _zero_entry's value goal close directly
        # without dragging the name round-trip / uniq / slots_lt32 of the heavier
        # _insert axiom into its VC. Cross-validated by
        # test-suite/corpus/pycsl-reference/0716.proofs/{rocq,lean}/DirBlitMarker.{v,lean}
        # (theorem dir_blit_marker_value_inode): Rocq Section-Variables-only / Closed
        # under the global context; Lean #print axioms = "does not depend on any
        # axioms" (⊆ {propext, Quot.sound}).
        "UnixFs.Dir.dir_blit_marker_value_inode":
            "forall d0 d1 : array int, s b0 b1 : int, name : string "
            "[dir_blit_marker d0 d1 s b0 b1 name]. "
            "dir_blit_marker d0 d1 s b0 b1 name -> "
            "slot_inode d1 5 s = 256 * b0 + b1",

        # ====================================================================
        # READ-SIDE dir_scan_result marker family — the read dual of the
        # dir_blit_marker family. Retires the READ-side dirscan-fidelity trust on
        # _dir_lookup by carrying the VALUE conclusion
        # `dir_lookup self.dir 5 pathname = found` across SMT via a unique marker,
        # the same discipline the write side used. Cross-validated zero-TCB by
        # test-suite/corpus/pycsl-reference/0720.proofs/{rocq,lean}/UnixDirScanValue.{v,lean}:
        #   - Rocq: every theorem "Section Variables" only (0 Axiom/Admitted).
        #   - Lean: dir_scan_result_value/_intro/_prefix_base/_prefix_close "does not
        #     depend on any axioms"; dir_scan_prefix_step ⊆ {propext, Quot.sound}.
        #
        # The marker fires ONLY at the atoms _dir_lookup's body asserts (the loop-carry
        # invariant + the loop-exit close), NEVER on a bare dir_lookup/slot_inode term,
        # so the gap-9 existential witness is discharged OFFLINE in the kernel and never
        # enters the WhyML goal — exactly the dir_blit_marker once-firing discipline.
        #
        # dir_scan_prefix_base (DEFINITIONAL, zero trust): the loop-init rung.
        # `found = -1` over the empty (0-slot) prefix. Trigger on the marker atom.
        "UnixFs.Dir.dir_scan_prefix_base":
            "forall d : array int, blk : int, name : string "
            "[dir_scan_prefix d blk name 0 (-1)]. "
            "dir_scan_prefix d blk name 0 (-1)",
        # dir_scan_prefix_step (cross-validated): the loop-body update rung. From the
        # prefix marker at slot i, peeling slot i — using the per-slot decode facts
        # slot_inode/slot_name d blk i (the SAME body name-match the loop body tests) —
        # advances the marker to slot i+1 with the body's `if` update of `found`.
        # Keyed [dir_scan_prefix d blk name i r], so it fires once per loop iteration
        # at the carried marker, NEVER on a bare scan term. This is the NON-inductive
        # rung: the induction is discharged offline; SMT only applies one O(1) step.
        "UnixFs.Dir.dir_scan_prefix_step":
            "forall d : array int, blk i r : int, name : string "
            "[dir_scan_prefix d blk name i r]. "
            "0 <= i -> i < 16 -> "
            "dir_scan_prefix d blk name i r -> "
            "( ( slot_inode d blk i <> 0 /\\ slot_inode d blk i < 32 "
            "      /\\ slot_name d blk i = name ) -> "
            "    dir_scan_prefix d blk name (i + 1) (slot_inode d blk i) ) "
            "/\\ ( not ( slot_inode d blk i <> 0 /\\ slot_inode d blk i < 32 "
            "             /\\ slot_name d blk i = name ) -> "
            "    dir_scan_prefix d blk name (i + 1) r )",
        # dir_scan_result_intro (DEFINITIONAL close, zero trust): the full-prefix rung
        # i=16 IS the scan result — fold the loop-exit prefix marker into the result
        # marker. Keyed [dir_scan_prefix d blk name 16 r].
        "UnixFs.Dir.dir_scan_result_intro":
            "forall d : array int, blk r : int, name : string "
            "[dir_scan_prefix d blk name 16 r]. "
            "dir_scan_prefix d blk name 16 r -> "
            "dir_scan_result d blk name r",
        # dir_scan_result_value (cross-validated VALUE lemma — the load-bearing read
        # dual of dir_blit_marker_value_inode): the marker carries
        # dir_lookup d blk name = r. The whole inductive last-live-match argument is
        # discharged offline in UnixDirScanValue (dir_lookup := scan ... 16 (-1) and the
        # marker = that scan); SMT only applies this O(1) equality at the asserted atom.
        # Keyed [dir_scan_result d blk name r] — fires EXACTLY ONCE at the close.
        "UnixFs.Dir.dir_scan_result_value":
            "forall d : array int, blk r : int, name : string "
            "[dir_scan_result d blk name r]. "
            "dir_scan_result d blk name r -> "
            "dir_lookup d blk name = r",
        # ====================================================================
        # READ-SIDE SLOT-INDEX dir_find_slot_result marker family — the SLOT-INDEX
        # twin of the dir_scan_result family. Retires the READ-side dirscan-fidelity
        # trust on _dir_find_slot, which returns the slot INDEX (0..15) of the LAST
        # live slot named `pathname`, or -1 (whereas _dir_lookup returns the matched
        # slot's INODE). Carries the slot's VALUE-fidelity (slot_inode <> 0 /\
        # slot_name = name at the returned index) across SMT via a unique marker, the
        # same once-firing discipline as dir_scan_result. Cross-validated zero-TCB by
        # test-suite/corpus/pycsl-reference/0721.proofs/{rocq,lean}/UnixDirFindSlotValue.{v,lean}:
        #   - Rocq: every theorem "Closed under the global context" (Section Variables
        #     only, 0 Axiom/Admitted).
        #   - Lean: dir_find_slot_result_intro/_prefix_base/_prefix_close "does not
        #     depend on any axioms"; _result_value/_result_range/_prefix_step ⊆
        #     {propext, Quot.sound}.
        #
        # The marker fires ONLY at the atoms _dir_find_slot's body asserts (the
        # loop-carry prefix invariant + the loop-exit close), NEVER on a bare
        # slot_inode/slot_name term — exactly the dir_scan_result once-firing discipline.
        # The Fixpoint `fscan` is the INDEX-keeping dual of `scan`: on a match, found
        # becomes the INDEX i (not the inode). The whole last-match argument is
        # discharged offline; SMT only applies the O(1) rungs.
        #
        # dir_find_slot_prefix_base (DEFINITIONAL, zero trust): the loop-init rung.
        # `found = -1` over the empty (0-slot) prefix. Trigger on the marker atom.
        "UnixFs.Dir.dir_find_slot_prefix_base":
            "forall d : array int, blk : int, name : string "
            "[dir_find_slot_prefix d blk name 0 (-1)]. "
            "dir_find_slot_prefix d blk name 0 (-1)",
        # dir_find_slot_prefix_step (cross-validated): the loop-body update rung. From
        # the prefix marker at slot i, peeling slot i — using the per-slot decode facts
        # slot_inode/slot_name d blk i (the SAME body match the loop body tests) —
        # advances the marker to slot i+1. On a match `found` becomes the INDEX i (NOT
        # the inode). Keyed [dir_find_slot_prefix d blk name i r] so it fires once per
        # loop iteration at the carried marker, NEVER on a bare term. The induction is
        # discharged offline; SMT only applies one O(1) step.
        "UnixFs.Dir.dir_find_slot_prefix_step":
            "forall d : array int, blk i r : int, name : string "
            "[dir_find_slot_prefix d blk name i r]. "
            "0 <= i -> i < 16 -> "
            "dir_find_slot_prefix d blk name i r -> "
            "( ( slot_inode d blk i <> 0 /\\ slot_inode d blk i < 32 "
            "      /\\ slot_name d blk i = name ) -> "
            "    dir_find_slot_prefix d blk name (i + 1) i ) "
            "/\\ ( not ( slot_inode d blk i <> 0 /\\ slot_inode d blk i < 32 "
            "             /\\ slot_name d blk i = name ) -> "
            "    dir_find_slot_prefix d blk name (i + 1) r )",
        # dir_find_slot_result_intro (DEFINITIONAL close, zero trust): the full-prefix
        # rung i=16 IS the slot-index scan result — fold the loop-exit prefix marker
        # into the result marker. Keyed [dir_find_slot_prefix d blk name 16 r].
        "UnixFs.Dir.dir_find_slot_result_intro":
            "forall d : array int, blk r : int, name : string "
            "[dir_find_slot_prefix d blk name 16 r]. "
            "dir_find_slot_prefix d blk name 16 r -> "
            "dir_find_slot_result d blk name r",
        # dir_find_slot_result_value (cross-validated VALUE lemma — the load-bearing
        # slot-index fidelity): when r >= 0 the returned slot decodes to a LIVE entry
        # named `name` (slot_inode <> 0 /\ slot_name = name). This is EXACTLY
        # _dir_find_slot's two fidelity ensures. The last-match argument is discharged
        # offline in UnixDirFindSlotValue; SMT only applies this O(1) implication.
        # Keyed [dir_find_slot_result d blk name r] — fires EXACTLY ONCE at the close.
        "UnixFs.Dir.dir_find_slot_result_value":
            "forall d : array int, blk r : int, name : string "
            "[dir_find_slot_result d blk name r]. "
            "dir_find_slot_result d blk name r -> "
            "r >= 0 -> "
            "slot_inode d blk r <> 0 /\\ slot_name d blk r = name",
        # READ-SIDE FREE-SLOT-INDEX dir_find_free_result marker family — the
        # FREE-slot twin of the dir_find_slot_result family. Retires the READ-side
        # dirscan-fidelity trust on _dir_find_free, which returns the slot INDEX
        # (0..15) of the LAST FREE slot (slot_inode == 0), or -1 if the block is
        # full. Unlike _dir_find_slot it reads ONLY slot_inode (NO name decode),
        # and the guard is the free condition `slot_inode == 0` (not the live-match
        # slot_inode <> 0 /\ slot_name == name). Carries the slot's free-fidelity
        # (slot_inode == 0 at the returned index) across SMT via a unique marker,
        # the same once-firing discipline as dir_find_slot_result. Cross-validated
        # zero-TCB by
        # test-suite/corpus/pycsl-reference/0722.proofs/{rocq,lean}/UnixDirFindFreeValue.{v,lean}:
        #   - Rocq: every theorem "Closed under the global context" (Section
        #     Variables only, 0 Axiom/Admitted).
        #   - Lean: dir_find_free_result_intro/_prefix_base/_prefix_close "does not
        #     depend on any axioms"; _result_value/_result_range/_prefix_step ⊆
        #     {propext, Quot.sound}.
        #
        # The marker fires ONLY at the atoms _dir_find_free's body asserts (the
        # loop-carry prefix invariant + the loop-exit close), NEVER on a bare
        # slot_inode term — exactly the dir_find_slot_result once-firing discipline.
        # The Fixpoint `ffscan` is the FREE-slot dual of `fscan`: on a free slot,
        # found becomes the INDEX i.
        #
        # dir_find_free_prefix_base (DEFINITIONAL, zero trust): the loop-init rung.
        # `found = -1` over the empty (0-slot) prefix. Trigger on the marker atom.
        "UnixFs.Dir.dir_find_free_prefix_base":
            "forall d : array int, blk : int "
            "[dir_find_free_prefix d blk 0 (-1)]. "
            "dir_find_free_prefix d blk 0 (-1)",
        # dir_find_free_prefix_step (cross-validated): the loop-body update rung.
        # From the prefix marker at slot i, peeling slot i — using the per-slot
        # decode fact slot_inode d blk i (the SAME body guard the loop tests) —
        # advances the marker to slot i+1. On a free slot `found` becomes the INDEX
        # i. Keyed [dir_find_free_prefix d blk i r] so it fires once per loop
        # iteration at the carried marker, NEVER on a bare term. The induction is
        # discharged offline; SMT only applies one O(1) step.
        "UnixFs.Dir.dir_find_free_prefix_step":
            "forall d : array int, blk i r : int "
            "[dir_find_free_prefix d blk i r]. "
            "0 <= i -> i < 16 -> "
            "dir_find_free_prefix d blk i r -> "
            "( ( slot_inode d blk i = 0 ) -> "
            "    dir_find_free_prefix d blk (i + 1) i ) "
            "/\\ ( ( slot_inode d blk i <> 0 ) -> "
            "    dir_find_free_prefix d blk (i + 1) r )",
        # dir_find_free_result_intro (DEFINITIONAL close, zero trust): the
        # full-prefix rung i=16 IS the free-slot-index scan result — fold the
        # loop-exit prefix marker into the result marker. Keyed
        # [dir_find_free_prefix d blk 16 r].
        "UnixFs.Dir.dir_find_free_result_intro":
            "forall d : array int, blk r : int "
            "[dir_find_free_prefix d blk 16 r]. "
            "dir_find_free_prefix d blk 16 r -> "
            "dir_find_free_result d blk r",
        # dir_find_free_result_value (cross-validated VALUE lemma — the
        # load-bearing free-slot fidelity): when r >= 0 the returned slot has
        # slot_inode == 0 (it is FREE). This is EXACTLY _dir_find_free's fidelity
        # ensures (\result >= 0 ==> slot_inode == 0). The last-free argument is
        # discharged offline in UnixDirFindFreeValue; SMT only applies this O(1)
        # implication. Keyed [dir_find_free_result d blk r] — fires EXACTLY ONCE.
        "UnixFs.Dir.dir_find_free_result_value":
            "forall d : array int, blk r : int "
            "[dir_find_free_result d blk r]. "
            "dir_find_free_result d blk r -> "
            "r >= 0 -> "
            "slot_inode d blk r = 0",
        # ====================================================================
        # BLOCK-PARAMETERIZED marker family (2026-06-19) — the arbitrary-block
        # generalization of the block-5 dir_blit_marker family above. _write_entry
        # mutates self.disk at an ARBITRARY block `block_num` (ensures reference
        # slot_inode(self.disk, block_num, slot) / slot_name(self.disk, block_num,
        # slot)), so the block-5-hardcoded family does NOT apply. These four axioms
        # add a `blk` parameter to the marker, slot_off, and the byte-region-frame
        # base (blk*512); slot_off/slot_inode/slot_name/field_to_str are ALREADY
        # generic over the block argument. The block-5 family is the blk=5 instance
        # of THESE — same proof, 5 -> blk. SCOPE: _write_entry's ensures are VALUE
        # (slot_inode + slot_name at slot) + FRAME (forall k <> slot); it does NOT
        # maintain the block-5 directory uniqueness invariants uniq/slots_lt32
        # (those are self.dir/block-5 facts established by the live-insert callers,
        # NOT a property of an arbitrary-block write), so there is NO block-
        # parameterized `insert` — only intro + value_inode + value_name + frame.
        # The new predicate `dir_blit_marker_at` is declared in _AXIOM_FUNCTIONS;
        # its trigger [dir_blit_marker_at d0 d1 blk s b0 b1 name] is UNIQUE, so it
        # fires ONLY at _write_entry's asserted marker atom, NEVER inside a sibling
        # byte mutator. Cross-validated zero-TCB by
        # test-suite/corpus/pycsl-reference/0718.proofs/{rocq,lean}/DirBlitMarkerAt.{v,lean}
        # (Rocq Section-Variables-only / Closed under the global context; Lean
        # #print axioms ⊆ {propext, Quot.sound}).
        #
        # dir_blit_marker_at_intro (DEFINITIONAL, zero trust): byte facts -> marker,
        # generalised over blk. IDENTICAL antecedents to dir_blit_marker_intro but
        # with slot_off blk s (not slot_off 5 s = 2560 + ...) and the byte-region
        # frame base blk*512 (not 2560).
        "UnixFs.Dir.dir_blit_marker_at_intro":
            "forall d0 d1 : array int, blk s b0 b1 : int, name : string "
            "[dir_blit_marker_at d0 d1 blk s b0 b1 name]. "
            "0 <= String.length name -> String.length name <= 30 -> "
            "d1[blk * 512 + 32 * s] = b0 -> d1[blk * 512 + 32 * s + 1] = b1 -> "
            "( forall i : int. 0 <= i < String.length name -> "
            "    Char.code (Char.get name i) <> 0 ) -> "
            "( forall i : int. 0 <= i < String.length name -> "
            "    d1[blk * 512 + 32 * s + 2 + i] = Char.code (Char.get name i) ) -> "
            "( String.length name < 30 -> "
            "    d1[blk * 512 + 32 * s + 2 + String.length name] = 0 ) -> "
            "( forall b : int. 0 <= b < 512 -> "
            "    (b < 32 * s \\/ 32 * s + 32 <= b) -> "
            "    d1[blk * 512 + b] = d0[blk * 512 + b] ) -> "
            "dir_blit_marker_at d0 d1 blk s b0 b1 name",
        # dir_blit_marker_at_value_inode: slot_inode d1 blk s = 256*b0+b1 — the two
        # inode-byte conjuncts only. The `Hvali` sub-derivation, generalised over blk.
        "UnixFs.Dir.dir_blit_marker_at_value_inode":
            "forall d0 d1 : array int, blk s b0 b1 : int, name : string "
            "[dir_blit_marker_at d0 d1 blk s b0 b1 name]. "
            "dir_blit_marker_at d0 d1 blk s b0 b1 name -> "
            "slot_inode d1 blk s = 256 * b0 + b1",
        # dir_blit_marker_at_value_name: slot_name d1 blk s = name (the byte
        # round-trip), generalised over blk. The `Hvaln` sub-derivation
        # (name_round_trip) exposed as its own block-parameterized theorem;
        # _write_entry needs it for the slot_name(self.disk, block_num, slot) == name
        # ensures. The name round-trip is discharged INSIDE the 0718 kernel proof, so
        # the os body provides ONLY the marker atom and never materializes the string
        # codec (field_to_str) in its VC.
        "UnixFs.Dir.dir_blit_marker_at_value_name":
            "forall d0 d1 : array int, blk s b0 b1 : int, name : string "
            "[dir_blit_marker_at d0 d1 blk s b0 b1 name]. "
            "dir_blit_marker_at d0 d1 blk s b0 b1 name -> "
            "slot_name d1 blk s = name",
        # dir_blit_marker_at_frame_only: every slot k <> s decodes identically in d1
        # and d0 (slot_inode AND slot_name), generalised over blk. The
        # `slot_frame_of_region_at` corollary applied to the marker's byte-region-frame
        # conjunct — needs ONLY the marker and slot-in-range, NOT uniq/range/freshness.
        "UnixFs.Dir.dir_blit_marker_at_frame_only":
            "forall d0 d1 : array int, blk s b0 b1 : int, name : string "
            "[dir_blit_marker_at d0 d1 blk s b0 b1 name]. "
            "dir_blit_marker_at d0 d1 blk s b0 b1 name -> "
            "0 <= s < 16 -> "
            "( forall k : int. 0 <= k < 16 -> k <> s -> "
            "    slot_inode d1 blk k = slot_inode d0 blk k /\\ "
            "    slot_name  d1 blk k = slot_name  d0 blk k )",
        # ====================================================================

        # UnixFs.Dir.dir_lookup_frame (M4 — sys_unlink reorder) — dir_lookup is the
        # bounded 16-slot scan, a function of the per-slot decodes ONLY, so disks
        # agreeing on every block-5 slot decode have equal dir_lookup. Lets sys_unlink
        # lay the remove witness FIRST (block 5 fresh) and free the inode blocks AFTER
        # (writes in block 0 only), carrying `dir_lookup(self.disk,5,pathname) < 0` as a
        # SCALAR loop invariant — no per-slot terms in the loop, so no E-matching storm
        # (the per-slot loop-carry alternative exploded, 15-0838 §2.9). Trigger on the
        # dir_lookup pair (binds d0,d1); the per-slot-eq antecedent is discharged from
        # _set_bitmap's byte frame via block5_decode_frame. Reuses the SAME dir_lookup/
        # slot_inode/slot_name symbols. Cross-validated by
        # unix-filesystem/UnixInodeFileSystem.proofs/{rocq,lean}/DirLookupFrame.{v,lean}
        # (theorem dir_lookup_frame): scan_frame induction. Rocq Closed under the global
        # context; Lean axioms ⊆ {propext, Quot.sound}.
        "UnixFs.Dir.dir_lookup_frame":
            "forall d0 d1 : array int, name : string "
            "[dir_lookup d1 5 name, dir_lookup d0 5 name]. "
            "( forall k : int. 0 <= k < 16 -> "
            "    slot_inode d1 5 k = slot_inode d0 5 k /\\ "
            "    slot_name  d1 5 k = slot_name  d0 5 k ) -> "
            "dir_lookup d1 5 name = dir_lookup d0 5 name",

        # UnixFs.Dir.insert_preserves_unique (gap-12) — the INSERT companion of
        # remove_reflects_absent and the MAINTENANCE lemma for the directory-
        # uniqueness class invariant. Over two disks d0 (pre-write) and d1
        # (post-write) related by the _write_entry slot-locality frame: if the
        # no-duplicate-live-names invariant holds on d0, and slot s becomes live
        # with a name nm that was NOT already live on d0 (the EEXIST guard), and
        # every OTHER slot agrees byte-for-byte with d0 (the frame), THEN the
        # invariant is preserved on d1. Faithful (NOT over-strong): it asserts
        # ONLY the structural fact that a fresh-name single-slot insert under an
        # unchanged frame cannot manufacture a duplicate live-name pair — it says
        # nothing about the decode-vs-bytes correspondence (that stays in the
        # trusted dirscan-fidelity decode ensures). Same trust KIND as
        # remove_reflects_absent; the remover side needs NO axiom (clearing a slot
        # only shrinks the live set, discharged directly in WhyML). Reuses the
        # SAME slot_inode/slot_name symbols (no new _AXIOM_FUNCTIONS entry).
        # Cross-validated by
        # unix-filesystem/UnixInodeFileSystem.proofs/{rocq,lean}/InsertPreservesUnique.{v,lean}
        # (theorem insert_preserves_unique): a finite 4-way case split, no
        # induction. Rocq 8.20.1: Closed under the global context (0 Axiom/Admitted,
        # only the abstract Section Variables); Lean 4.30.0: #print axioms =
        # [propext, Quot.sound] subseteq allowlist, no sorry.
        "UnixFs.Dir.insert_preserves_unique":
            "forall d0 : array int. forall d1 : array int. forall blk : int. "
            "forall s : int. forall nm : string. "
            "( forall j : int. 0 <= j < 16 -> slot_inode d0 blk j >= 0 ) -> "
            "( 0 <= s < 16 ) -> "
            "( forall i j : int. 0 <= i < 16 -> 0 <= j < 16 -> "
            "    slot_inode d0 blk i <> 0 -> slot_inode d0 blk i < 32 -> "
            "    slot_inode d0 blk j <> 0 -> slot_inode d0 blk j < 32 -> "
            "    slot_name d0 blk i = slot_name d0 blk j -> i = j ) -> "
            "( forall k : int. 0 <= k < 16 -> "
            "    slot_inode d0 blk k <> 0 -> slot_inode d0 blk k < 32 -> "
            "    slot_name d0 blk k <> nm ) -> "
            "( forall k : int. 0 <= k < 16 -> k <> s -> "
            "    slot_inode d1 blk k = slot_inode d0 blk k /\\ "
            "    slot_name  d1 blk k = slot_name  d0 blk k ) -> "
            "( slot_inode d1 blk s <> 0 -> slot_inode d1 blk s < 32 ) -> "
            "( slot_name  d1 blk s = nm ) -> "
            "( forall i j : int. 0 <= i < 16 -> 0 <= j < 16 -> "
            "    slot_inode d1 blk i <> 0 -> slot_inode d1 blk i < 32 -> "
            "    slot_inode d1 blk j <> 0 -> slot_inode d1 blk j < 32 -> "
            "    slot_name d1 blk i = slot_name d1 blk j -> i = j )",

        # UnixFs.Dir.empty_disk_slots_dead (gap-13, Wall E) — the EMPTY-DISK
        # ESTABLISHMENT axiom for the directory-uniqueness class invariant. The
        # abstract per-slot decode slot_inode (disk, blk, k) is the 2-byte
        # big-endian inode field of the 32-byte dirent at slot k of block blk
        # (256*disk[off] + disk[off+1], off = blk*512 + 32*k). If every byte of
        # block blk's 512-byte region reads as 0, the decoded inode is 0 for
        # every one of the 16 slots — hence no slot is live, so the
        # no-duplicate-live-names invariant holds VACUOUSLY. This is the
        # ANTECEDENT-discharge dual of slot_inode_nonneg: it lets the
        # constructor's `Array.make 131072 0` witness and the `_filesystem`
        # module-global instance ESTABLISH the invariant on the zeroed disk.
        # Faithful (a property of `_unpack_uint16_be` of all-zero bytes, NOT an
        # over-claim). Reuses the SAME slot_inode symbol (no new _AXIOM_FUNCTIONS
        # entry). Cross-validated by
        # unix-filesystem/UnixInodeFileSystem.proofs/{rocq,lean}/EmptyDiskSlotsDead.{v,lean}
        # (theorem empty_disk_slots_dead): rewrite the two field bytes to 0 under
        # the region-zero hypothesis, close by lia/omega; no induction. Rocq
        # 8.20.1: Closed under the global context (0 Axiom/Admitted, only the
        # abstract Section Variables); Lean 4.30.0: #print axioms = [propext,
        # Quot.sound] subseteq allowlist, no sorry.
        "UnixFs.Dir.empty_disk_slots_dead":
            "forall disk : array int. forall blk : int. "
            "( forall b : int. blk * 512 <= b < blk * 512 + 512 -> disk[b] = 0 ) -> "
            "( forall k : int. 0 <= k < 16 -> slot_inode disk blk k = 0 )",

        # UnixFs.Dir.block5_decode_frame (gap-13, Wall M) — the DECODE-LOCALITY
        # frame axiom. slot_inode/slot_name (disk, 5, k) read ONLY the 32 bytes of
        # slot k's dirent, all inside block 5's region [2560, 3072). Hence two
        # disks d0, d1 agreeing on every byte of [2560, 3072) have identical
        # block-5 decode at every slot k in [0, 16). This is the frame that lets
        # the directory-uniqueness class invariant ride UNTOUCHED through every
        # non-block-5 disk write: each disk-writing HELPER (_write_inode,
        # _set_bitmap, _alloc_inode, _alloc_block, _block_roundtrip) proves a
        # block-5 byte-frame from its Array.blit/single-byte write
        # (its written region is disjoint from [2560,3072)), and this axiom
        # converts that byte-frame into a DECODE-frame ensures, so the 7
        # non-directory syscalls (chmod/chown/utimensat/write/truncate/
        # ftruncate/open) that delegate to those helpers maintain `uniq` with
        # ZERO body annotation. Same byte-local-decode trust class as
        # _write_entry/_zero_entry's slot-locality frames and as
        # empty_disk_slots_dead. Reuses the SAME slot_inode/slot_name symbols (no
        # new _AXIOM_FUNCTIONS entry). Cross-validated by
        # unix-filesystem/UnixInodeFileSystem.proofs/{rocq,lean}/Block5DecodeFrame.{v,lean}
        # (theorem block5_decode_frame): rewrite every read under the byte-
        # agreement window; no funext, no induction. Rocq 8.20.1: Closed under
        # the global context (0 Axiom/Admitted, only the abstract Section
        # Variables); Lean 4.30.0: #print axioms = [propext, Quot.sound]
        # subseteq allowlist, no sorry.
        # TRIGGERED (gap directory-frame rework, 2026-06-13): flattened prenex form
        # with a multi-pattern trigger so the frame fires O(1) per slot when BOTH the
        # new- and old-disk slot terms are present (the writers' `slot_x disk 5 k =
        # \old(slot_x disk 5 k)` ensures), instead of E-match-exploding (42M+ steps).
        # Logically IDENTICAL to the validated statement (k pulled out of the
        # conclusion into the antecedent; triggers are proof hints, not logic), so
        # Block5DecodeFrame.{v,lean} still apply unchanged.
        # NOTE: block5_decode_frame RETIRED (M4 #1) — it converted a block-5 BYTE frame
        # into a slot-decode frame so non-directory writers could prove the (block-5-in-
        # self.disk) directory preserved. With the directory in its own field self.dir,
        # that preservation is automatic from `assigns self.disk`, so this axiom is
        # obsolete. Cross-validated proof kept in Block5DecodeFrame.{v,lean} for reference.
        # allocator-frame plan §2a: DEFINITIONAL intro/elim for the abstract `uniq` /
        # `inode_bytes_valid` predicates (a conservative definition `pred d <-> P(d)`,
        # sound by construction — equivalent to `predicate pred (d) = P(d)` but kept
        # OPAQUE so a callee's maintained invariant matches a caller's goal as an atom).
        # `_intro` (P -> pred) establishes the predicate (constructor, directory
        # mutators); `_elim` (pred -> P) unfolds it where the body is needed (mutators
        # feeding insert_preserves_unique). Triggered on the predicate atom so they fire
        # only when that atom is in play. NOT cross-validated (definitional, not a fact).
        "UnixFs.Dir.uniq_intro":
            "forall d : array int [uniq d]. "
            "( forall i j : int. (0 <= i < 16 /\\ 0 <= j < 16 /\\ "
            "slot_inode d 5 i <> 0 /\\ slot_inode d 5 i < 32 /\\ "
            "slot_inode d 5 j <> 0 /\\ slot_inode d 5 j < 32 /\\ "
            "slot_name d 5 i = slot_name d 5 j) -> i = j) -> uniq d",
        "UnixFs.Dir.uniq_elim":
            "forall d : array int [uniq d]. uniq d -> "
            "( forall i j : int. (0 <= i < 16 /\\ 0 <= j < 16 /\\ "
            "slot_inode d 5 i <> 0 /\\ slot_inode d 5 i < 32 /\\ "
            "slot_inode d 5 j <> 0 /\\ slot_inode d 5 j < 32 /\\ "
            "slot_name d 5 i = slot_name d 5 j) -> i = j)",
        "UnixFs.Dir.ibv_intro":
            "forall d : array int [inode_bytes_valid d]. "
            "( forall i : int. 512 <= i < 2560 -> 0 <= d[i] <= 255 ) -> "
            "inode_bytes_valid d",
        "UnixFs.Dir.ibv_elim":
            "forall d : array int [inode_bytes_valid d]. inode_bytes_valid d -> "
            "( forall i : int. 512 <= i < 2560 -> 0 <= d[i] <= 255 )",
        # M4 (os-roadmap): DEFINITIONAL intro/elim for the `slots_lt32` disk invariant —
        # every block-5 dirent slot decodes to an inode number < 32 (the FS has 32 inodes;
        # dirents only ever reference `_alloc_inode` results in [1,32) or the dead 0). This is
        # the bound `uniq`'s antecedent needs to apply to ALL live slots, so the directory
        # ABSENCE assert (`\forall k≠s. slot_name(k)==p -> slot_inode(k)==0`) closes. NOT
        # byte-derivable (a 2-byte field can hold up to 65535) → a genuine maintained invariant,
        # same definitional (ZERO-trust) intro/elim shape as `uniq` / `inode_bytes_valid`.
        # Maintained on non-block-5 writes by `block5_decode_frame` (slot decode unchanged) and
        # on the dir mutators by their write-post (`_write_entry` sets `inode<32` from
        # `_alloc_inode`; `_zero_entry` sets 0). Established on the zeroed disk via
        # `empty_disk_slots_dead`.
        "UnixFs.Dir.slots_lt32_intro":
            "forall d : array int [slots_lt32 d]. "
            "( forall k : int. 0 <= k < 16 -> slot_inode d 5 k < 32 ) -> "
            "slots_lt32 d",
        "UnixFs.Dir.slots_lt32_elim":
            "forall d : array int [slots_lt32 d]. slots_lt32 d -> "
            "( forall k : int. 0 <= k < 16 -> slot_inode d 5 k < 32 )",
        # UnixFs.Field.field_to_str_round_trip (string-codec Phase A') — the
        # string ↔ fixed-width null-padded byte-field codec ROUND-TRIP. `field_to_str
        # d off width` is the decoded name in the `width`-byte field at `off`: the
        # bytes d[off..off+width), read as chars, up to the first null (or the full
        # width if none). The axiom is the ENCODE→DECODE direction: for a `name` that
        # (i) fits the field (`length name <= width`), (ii) has no embedded null, (iii)
        # is byte-for-byte present (`d[off+i] = ord(name[i])`), and (iv) is
        # null-terminated when shorter than the field — the decode RECOVERS it exactly
        # (`field_to_str d off width = name`). This is the Python `struct '>Ns'` field
        # round-trip, faithful to `name.encode()` + null-pad + truncate-free pack.
        #
        # SMT cannot discharge this directly: the proof is by string EXTENSIONALITY
        # (equal length + equal char-at-i), and Alt-Ergo/Z3 over Why3's AXIOMATIC
        # `string.String` E-match-explode on `eq_string` (validated: ~23M-step timeout,
        # string-codec Phase A de-risking, 14-string-field-codec-plan.md §2.5). So the
        # round-trip is a CITED axiom — SMT only ever APPLIES it (O(1)); all the
        # extensionality reasoning lives in the proof assistants. Cross-validated by
        # test-suite/corpus/pycsl-reference/0708.proofs/{rocq,lean}/FieldToStrRoundTrip.{v,lean}
        # (theorem field_to_str_round_trip): `field_to_str` is defined there as the
        # scan-to-first-null decode over an abstract byte-reader; the round-trip is
        # proved by string extensionality + the per-char byte round-trip
        # (`chr (code c) = c`), no admits. Rocq 8.20.1: closed under the global context
        # (0 Axiom/Admitted, only the abstract Section Variables); Lean 4.30.0:
        # #print axioms ⊆ {propext, Quot.sound}, no sorry.
        # TRIGGER [field_to_str d off width] (CONFINEMENT, sound): without it Why3
        # auto-selects triggers from the antecedent byte atoms (`[off + i]`,
        # `[off + String.length name]`), which E-MATCH the WRITE-side null-pad /
        # per-char goals (`dir[2560+32*slot+2+i] = ...`) and explode them to OOM —
        # the measured _write_dir_entry regression. Keying on the `field_to_str`
        # decode term confines the axiom to read-side goals where a `field_to_str`
        # term is present (i.e. `_dir_lookup`'s faithful name), NEVER the write side.
        # A trigger only RESTRICTS instantiation (never adds a fact), so this is
        # soundness-neutral; the conclusion `field_to_str d off width = name` is
        # unchanged and the cross-validation (0708.proofs) still applies verbatim.
        "UnixFs.Field.field_to_str_round_trip":
            "forall d : array int. forall off width : int. forall name : string "
            "[field_to_str d off width]. "
            "0 <= String.length name -> String.length name <= width -> "
            "( forall i : int. 0 <= i < String.length name -> "
            "    Char.code (Char.get name i) <> 0 ) -> "
            "( forall i : int. 0 <= i < String.length name -> "
            "    d[off + i] = Char.code (Char.get name i) ) -> "
            "( String.length name < width -> d[off + String.length name] = 0 ) -> "
            "field_to_str d off width = name",

        # UnixFs.Field.field_to_str_frame (string-codec Phase A', DISJOINT-REGION
        # FRAME) — the byte-locality twin of `field_to_str_round_trip`. The decode of
        # a `width`-byte null-padded field at `off` depends ONLY on the bytes
        # d[off..off+width): if two disks d0, d1 AGREE byte-for-byte over that exact
        # window (`forall i. 0 <= i < width -> d0[off+i] = d1[off+i]`), they decode
        # to the SAME name (`field_to_str d0 off width = field_to_str d1 off width`).
        # This is the disjoint-region frame the dir-mutators need: a blit that
        # rewrites slot `s`'s 32-byte entry leaves every OTHER slot k≠s's name window
        # untouched, so composed with `slot_name_byte_decode`
        # (`slot_name d 5 k = field_to_str d (2560+32*k+2) 30`) it supplies the
        # `∀k≠s. slot_name d1 5 k = slot_name d0 5 k` slot_name frame. It is the
        # DISJOINT-REGION twin of the retired `block5_decode_frame` (which required
        # FULL block-5 byte agreement — broken by any in-block blit); this frame only
        # asks for agreement on the SINGLE field's window, which a disjoint blit
        # always supplies.
        #
        # SMT cannot discharge this directly: like the round-trip, the proof is by
        # induction over the scan-to-first-null decode (the abstract `field_to_str`
        # has no WhyML body to unfold — it is a logic `function` constrained only by
        # axioms), which E-match-explodes over Why3's axiomatic strings. So it is a
        # CITED axiom — SMT only ever APPLIES it (O(1)) under the byte-frame
        # antecedent; the induction lives in the proof assistants. The TRIGGER is the
        # SAME shape as `slot_name_byte_decode`/round-trip — keyed on BOTH decode
        # terms `[field_to_str d1 off width, field_to_str d0 off width]` so it fires
        # ONLY when both field decodes are already present in the goal (a frame
        # between two named disk states), never on a lone decode (no global
        # E-matching). Cross-validated by
        # test-suite/corpus/pycsl-reference/0714.proofs/{rocq,lean}/FieldToStrFrame.{v,lean}
        # (theorem field_to_str_frame): `field_to_str` is the scan-to-first-null
        # decode over an abstract byte-reader (the SAME concrete model as
        # FieldToStrRoundTrip); the frame is proved by induction on the scan fuel /
        # width — agreeing bytes feed the same scan branch at every step. Rocq 8.20.1:
        # closed under the global context (0 Axiom/Admitted, only the abstract Section
        # Variables); Lean 4.30.0: #print axioms ⊆ {propext, Quot.sound}, no sorry.
        "UnixFs.Field.field_to_str_frame":
            "forall d0 d1 : array int. forall off width : int "
            "[field_to_str d1 off width, field_to_str d0 off width]. "
            "0 <= width -> "
            "( forall i : int. 0 <= i < width -> d0[off + i] = d1[off + i] ) -> "
            "field_to_str d0 off width = field_to_str d1 off width",

        # allocator-frame §5 reference fixture — DEFINITIONAL intro/elim for the
        # `field_nonneg` predicate (conservative definition `field_nonneg x <-> x >= 0`;
        # ZERO trust). Used by the corpus test for predicate-in-`#@ class invariant`.
        "Pycsl.Reference.FieldPred.field_nonneg_intro":
            "forall x : int [field_nonneg x]. x >= 0 -> field_nonneg x",
        "Pycsl.Reference.FieldPred.field_nonneg_elim":
            "forall x : int [field_nonneg x]. field_nonneg x -> x >= 0",

        # Pycsl.Strmod.StrLen.length_nonneg — the STRING-UNIVERSAL
        # length-non-negativity fact that pins every "result is a string" leaf
        # in src/pycsl_lib/strmod (template_substitute / template_safe_substitute /
        # _format_field_nonempty / Template.substitute / Template.safe_substitute
        # / Formatter.format). EVERY string — whatever transform produced it —
        # has non-negative length; this is a GENERIC fact about the abstract
        # string type, provable with NO transform definition. Each strmod leaf is
        # an abstract `val` whose sole sound `ensures` is exactly this instance
        # (`String.length result >= 0`); citing this cross-validated lemma
        # replaces bare reviewer-`\trusted` with a named, proof-assistant-anchored
        # fact (the auditable trusted core). NOTE: this is deliberately NOT
        # transform-specific — facts that depend on what a transform DOES (e.g.
        # capwords' `length result <= length s`, or `f("") == ""`) are NOT true
        # of an arbitrary `val` and remain honest GAPs (stay `\trusted`), never
        # faked as a cited axiom. Cross-validated by
        # src/pycsl_lib/strmod/__init__.proofs/{rocq,lean}/StrLen.{v,lean} (theorem
        # length_nonneg): `string` is modelled as `list Z` / `List Int`,
        # `String.length` as `Z.of_nat (length _)` / `(_.length : Int)`, which is
        # a count, hence >= 0. Rocq 8.20.1: closed under the global context
        # (0 Axiom/Admitted); Lean 4.31.0: does not depend on any axioms (no sorry).
        "Pycsl.Strmod.StrLen.length_nonneg":
            "forall s : string. String.length s >= 0",

        # Pycsl.Strmod.Capwords — the TWO TRANSFORM-SPECIFIC facts of a FAITHFUL
        # CPython `string.capwords` model (default sep=None path). Unlike the
        # STRING-UNIVERSAL `length_nonneg` above (true of an ARBITRARY result),
        # these depend on what capwords DOES (whitespace tokenize -> per-word
        # capitalize -> single-space join) and are FALSE of an arbitrary string
        # transform. They are therefore NOT provable about an abstract `val`
        # alone: they are stated about a DEFINED logic symbol `capwords_def`
        # (the abstract `val function capwords_def` declared by _AXIOM_FUNCTIONS
        # below, whose intended interpretation IS the concrete definition in the
        # proofs). The capwords leaf in src/pycsl_lib/strmod is an `#@ \abstract` val
        # whose default-sep (sep = "") ensures is `result = capwords_def s`, from
        # which the length bound and empty law follow by these two axioms. This
        # retires the LAST bare reviewer-`\trusted` in strmod, replacing it with
        # a NAMED, proof-assistant-anchored definition (the auditable trusted
        # core = the faithfulness of `capwords_def`).
        #
        # Cross-validated by src/pycsl_lib/strmod/__init__.proofs/{rocq,lean}/
        # Capwords.{v,lean}: `string` is `list Z` / `List Int`; `capwords_def` is
        # whitespace-tokenize (CPython str.split() default whitespace
        # {space,\t,\n,\r,\f,\v}, drop empties, trim) -> capitalize (first upper,
        # rest lower; length-preserving) -> single-space join, MATCHING
        # string.capwords(s) = ' '.join(x.capitalize() for x in s.split()).
        # Rocq 8.20.1: closed under the global context (0 Axiom/Admitted);
        # Lean 4.31.0: #print axioms = {propext, Quot.sound} (no sorry).
        "Pycsl.Strmod.Capwords.capwords_length_nongrowing":
            "forall s : string. String.length (capwords_def s) <= String.length s",
        "Pycsl.Strmod.Capwords.capwords_empty":
            "capwords_def \"\" = \"\"",

        # Pycsl.Csys.Colorsys — nonlinear integer-division bounds for the HSV
        # conversion (de-trusting csys `rgb_to_hsv`; non-lin-int-div-fixed.md S5).
        # SMT (Alt-Ergo/Z3 over int.EuclideanDivision) times out on these bounds
        # through the deep sector branches; each is an honest arithmetic fact,
        # cross-validated by src/pycsl_lib/csys/__init__.proofs/rocq/Colorsys.v
        # + .../lean/Colorsys.lean (0 Axiom/Admitted/sorry). `sat_bound`: the HSV
        # saturation `(diff*1000)//mx` is <= 1000 since diff <= mx (div monotone,
        # div (mx*1000) mx = 1000). `hue_bound`: the hue offset `(n*1000)//(6*diff)`
        # lies in [-167, 167] since |n| <= diff (upper div 1000 6 = 166; lower
        # div (-1000) 6 = -167).
        "Pycsl.Csys.Colorsys.sat_bound":
            "forall d m : int [div (d * 1000) m]. "
            "0 <= d -> d <= m -> m > 0 -> div (d * 1000) m <= 1000",
        "Pycsl.Csys.Colorsys.hue_bound":
            "forall n d : int [div (n * 1000) (6 * d)]. d > 0 -> (0 - d) <= n -> n <= d -> "
            "(0 - 167) <= div (n * 1000) (6 * d) /\\ div (n * 1000) (6 * d) <= 167",
    }

    # gap-13: axioms that CONSTRAIN the axiom-func symbols a `#@ class invariant`
    # applies (and therefore must be emitted BEFORE the record type whose
    # invariant uses them, so the establishment / per-method type-invariant VCs
    # can see them — a Why3 `axiom` only constrains its symbols from its point of
    # declaration onward). Emitted by `_emit_class_inv_axioms` ahead of the record
    # (gated by `_class_inv_refs_axiom_func`) and skipped by the later
    # `_emit_preamble_axioms` so they appear exactly once. Both are low-fan-out,
    # byte-local decode facts (no `dir_lookup` existential), so hoisting them does
    # not reintroduce the gap-9 E-matching blowup.
    _CLASS_INV_AXIOMS: frozenset = frozenset({
        "UnixFs.Dir.empty_disk_slots_dead",
        # block5_decode_frame RETIRED (M4 #1): directory now in its own field self.dir,
        # so non-directory writes preserve it from the frame alone (no byte->decode step).
        # inode_bytes_valid keeps its definitional intro/elim (a different, non-
        # directory invariant — its single `forall i` does not E-match-explode).
        "UnixFs.Dir.ibv_intro",
        "UnixFs.Dir.ibv_elim",
        # gap-17 content round-trip: the folded `block_content_eq` content atom's
        # DEFINITIONAL intro/elim (trigger [block_content_eq d blk data] → fires only in
        # sys_write/sys_pread/their wrappers/the round-trip test, never elsewhere).
        "UnixFs.Content.block_content_eq_intro",
        "UnixFs.Content.block_content_eq_elim",
        # M4: directory-uniqueness + slots_lt32 ESTABLISHED via establish_* (the
        # constructor `by`-witness over self.dir = Array.make 0). The maintenance facts
        # (frame_preserves_*/zero_preserves_*/insert_preserves_*) are ALL RETIRED (M4 #1):
        # non-directory writes preserve the directory (self.dir) from `assigns self.disk`
        # alone; the directory MUTATORS (_write_dir_entry/_zero_entry) are \trusted vals
        # whose post ASSUMES the class invariant — so nothing verifies a directory-write
        # maintenance VC, and these facts had no remaining use. They only added E-matching
        # noise (firing on the ubiquitous uniq/slots_lt32 + slot_* atoms). Cross-validated
        # proofs kept in DirInvariantMaintenance.{v,lean} for reference.
        "UnixFs.Dir.establish_uniq",
        "UnixFs.Dir.establish_slots_lt32",
        # allocator-frame §5 reference fixture (predicate-in-class-invariant corpus test).
        "Pycsl.Reference.FieldPred.field_nonneg_intro",
        "Pycsl.Reference.FieldPred.field_nonneg_elim",
    })

    # allocator-frame plan §2a: axioms that are DEFINITIONAL (a conservative definition
    # `pred d <-> P(d)` of an abstract predicate, given as the intro/elim pair) — sound by
    # construction, equivalent to a `predicate pred (d) = P(d)` body, so they add ZERO to
    # the trusted base. Labeled distinctly from the cross-validated Rocq+Lean facts.
    # NOTE: the directory uniq/slots_lt32 intro/elim are NO LONGER emitted (M4 —
    # replaced by the cross-validated FOLDED maintenance facts above, which are NOT
    # definitional but Rocq+Lean cross-validated). Their bodies remain in
    # _AXIOM_REGISTRY (inert — cited nowhere) for reference. inode_bytes_valid keeps
    # its definitional pair (different invariant, no explosion).
    _DEFINITIONAL_AXIOMS: frozenset = frozenset({
        "UnixFs.Dir.ibv_intro",
        "UnixFs.Dir.ibv_elim",
        "UnixFs.Content.block_content_eq_intro",
        "UnixFs.Content.block_content_eq_elim",
        "Pycsl.Reference.FieldPred.field_nonneg_intro",
        "Pycsl.Reference.FieldPred.field_nonneg_elim",
    })

    # Functions that an axiom block needs declared. Looked up by qualname
    # prefix; declarations emitted once each when any matching axiom fires.
    # Values are List[str] so a single prefix can carry several function
    # declarations — required for `UnixFs.Struct.<slot_id>.round_trip`
    # axioms that mention both `struct_pack_<id>` and `struct_unpack_<id>`.
    _AXIOM_FUNCTIONS: Dict[str, List[str]] = {
        "Pycsl.Reference.Gcd.": ["function gcd (a : int) (b : int) : int"],
        # allocator-frame §5 reference fixture: a named (abstract) predicate over an int
        # field, for the corpus test that exercises `#@ class invariant p(self.field)`
        # binding to a registry predicate (the `_names_of` `predicate`-recognition of
        # commit 755f89e). Its meaning is the definitional intro/elim below.
        "Pycsl.Reference.FieldPred.": ["predicate field_nonneg (x: int)"],
        # Pycsl.Strmod.Capwords: the abstract `val function capwords_def` (a LOGIC
        # symbol — referenceable in the capwords leaf's `ensures` and in the two
        # cross-validated axioms above). Its intended interpretation is the
        # concrete faithful definition in __init__.proofs/{rocq,lean}/Capwords.
        "Pycsl.Strmod.Capwords.": ["val function capwords_def (s: string) : string"],
        # string-codec Phase A': the abstract string ↔ byte-field decode. Logic-only
        # (`function`, no body) — the SAME abstract symbol used in CONTRACTS and
        # constrained by the cross-validated `field_to_str_round_trip`/`field_to_str_frame`
        # axioms above. The faithful read-name EMITTER lowering (the null-terminated-field
        # decode recognizer, see `_recognize_field_decode_idiom` in
        # module6_whyml/expressions.py) emits a genuine `field_to_str self.dir off 30`
        # TERM in `_dir_lookup`'s body via a Why3 `pure { ... }` block — which lifts a
        # LOGIC term into program position WITHOUT turning the symbol into a `val` (so it
        # is NOT a `val`/assumed-ensures shim, NOT a new symbol, NOT a new axiom, and adds
        # NO program/safety VC that would perturb the write-side `field_to_str_round_trip`
        # E-matching). `field_to_str` thus stays a pure logic `function`, byte-stable for
        # every non-`_dir_lookup` VC; the body term is the exact symbol the axioms key on.
        "UnixFs.Field.": [
            "val function field_to_str (d: array int) (off: int) (width: int) : string",
        ],
        # Declare the `\permutation` predicate before its axioms. Same symbol
        # `_handle_permutation_expr` emits via `_add_abstract_op` — the
        # abstract-val dedup skips it here so it is declared exactly once.
        "Pycsl.Reference.Perm.": ["predicate permut (a: array int) (b: array int)"],
        # The `rev_permutation` axiom additionally needs `array_rev` (the
        # `reversed(...)` model) declared before it. Keyed on the longer prefix
        # so `permut_refl` (which doesn't mention it) stays unchanged.
        "Pycsl.Reference.Perm.rev_permutation":
            ["val function array_rev (a: array int) : array int"],
        # A4: `json_mirror` over the user `json` datatype. The axiom block is
        # emitted after `_emit_type_decls`, so `json` is in scope here.
        "Pycsl.Reference.Json.":
            ["val function json_mirror (x: json) : json"],
        # Declare bit_and here (before the axiom block) so the axiom
        # `forall n. 0 <= bit_and n 1 < 2` typechecks. Uses Why3's
        # `val function` idiom — both program and logic symbol — so
        # the body of _get_bitmap can call it AND the axiom can
        # constrain it. Abstract-ops dedupes against this declaration.
        "UnixFs.Bitmap.": ["val function bit_and (x : int) (y : int) : int"],
        # UnixFs.Struct: round-trip axioms per format slot_id.
        # Each format gets its own pack/unpack `val function` symbol
        # so the axiom (forall fmt args, unpack (pack args) = args)
        # typechecks against the same symbols emitted by Module6's
        # `_handle_struct_call` dispatch.
        "UnixFs.Struct.i1a1.": [
            "val function struct_pack_i1a1 (fmt: int) (x0: int) (x1: array int) : array int\n"
            "    ensures { Array.length result = 32 }",
            "val function struct_unpack_i1a1 (fmt: int) (data: array int) : (int, array int)",
        ],
        "UnixFs.Struct.i2.": [
            "val function struct_pack_i2 (fmt: int) (x0: int) (x1: int) : array int",
            "val function struct_unpack_i2 (fmt: int) (data: array int) : (int, int)",
        ],
        "UnixFs.Struct.i18.": [
            "val function struct_pack_i18 (fmt: int) "
            "(x0: int) (x1: int) (x2: int) (x3: int) (x4: int) (x5: int) "
            "(x6: int) (x7: int) (x8: int) (x9: int) (x10: int) (x11: int) "
            "(x12: int) (x13: int) (x14: int) (x15: int) (x16: int) (x17: int) "
            ": array int\n"
            "    ensures { Array.length result = 64 }",
            "val function struct_unpack_i18 (fmt: int) (data: array int) : "
            "(int, int, int, int, int, int, int, int, int, "
            "int, int, int, int, int, int, int, int, int)",
        ],
        # Pycsl.Struct.Std (cleared-pack): the faithful single-slot uint families.
        # The pack `val`s carry BOTH the S1 size law (`length = calcsize`) and the
        # S2 in-range `requires` — the latter is a CALL-SITE VC (real struct.pack
        # raises out-of-range), making the guard load-bearing. Cited via
        # `#@ proof rocq|lean Pycsl.Struct.Std.round_trip_u{16,32}`.
        # NOTE keys are the EXACT cited qualnames (matched by `qn.startswith`);
        # each pulls only its own width's decls.
        "Pycsl.Struct.Std.round_trip_u16": [
            "val function struct_pack_fu16 (fmt: int) (x0: int) : array int\n"
            "    requires { 0 <= x0 < 65536 }\n"
            "    ensures  { Array.length result = 2 }",
            "val function struct_unpack_fu16 (fmt: int) (data: array int) : int",
        ],
        "Pycsl.Struct.Std.round_trip_u32": [
            "val function struct_pack_fu32 (fmt: int) (x0: int) : array int\n"
            "    requires { 0 <= x0 < 4294967296 }\n"
            "    ensures  { Array.length result = 4 }",
            "val function struct_unpack_fu32 (fmt: int) (data: array int) : int",
        ],
        # cleared-pack RESIDUALS: per-field width/sign-tagged faithful families.
        # Each pack `val` carries the S1 size law (`length = calcsize`) AND the S2
        # per-field in-range `requires` (a CALL-SITE VC; real struct.pack raises
        # out-of-range). Multi-slot unpack returns a tuple in field order.
        # item 1 — multi-slot unsigned u16u32 (6 bytes).
        "Pycsl.Struct.Std.round_trip_u16u32": [
            "val function struct_pack_fu16u32 (fmt: int) (x0: int) (x1: int) : array int\n"
            "    requires { 0 <= x0 < 65536 }\n"
            "    requires { 0 <= x1 < 4294967296 }\n"
            "    ensures  { Array.length result = 6 }",
            "val function struct_unpack_fu16u32 (fmt: int) (data: array int) : (int, int)",
        ],
        # item 2 — signed singles (two's complement).
        "Pycsl.Struct.Std.round_trip_i16": [
            "val function struct_pack_fi16 (fmt: int) (x0: int) : array int\n"
            "    requires { -32768 <= x0 < 32768 }\n"
            "    ensures  { Array.length result = 2 }",
            "val function struct_unpack_fi16 (fmt: int) (data: array int) : int",
        ],
        "Pycsl.Struct.Std.round_trip_i32": [
            "val function struct_pack_fi32 (fmt: int) (x0: int) : array int\n"
            "    requires { -2147483648 <= x0 < 2147483648 }\n"
            "    ensures  { Array.length result = 4 }",
            "val function struct_unpack_fi32 (fmt: int) (data: array int) : int",
        ],
        "Pycsl.Struct.Std.round_trip_i64": [
            "val function struct_pack_fi64 (fmt: int) (x0: int) : array int\n"
            "    requires { -9223372036854775808 <= x0 < 9223372036854775808 }\n"
            "    ensures  { Array.length result = 8 }",
            "val function struct_unpack_fi64 (fmt: int) (data: array int) : int",
        ],
        # items 1+2 — multi-slot signed i32i32 (8 bytes).
        "Pycsl.Struct.Std.round_trip_i32i32": [
            "val function struct_pack_fi32i32 (fmt: int) (x0: int) (x1: int) : array int\n"
            "    requires { -2147483648 <= x0 < 2147483648 }\n"
            "    requires { -2147483648 <= x1 < 2147483648 }\n"
            "    ensures  { Array.length result = 8 }",
            "val function struct_unpack_fi32i32 (fmt: int) (data: array int) : (int, int)",
        ],
        # item 3 — fixed-bytes s4 (array identity under the length guard).
        "Pycsl.Struct.Std.round_trip_s4": [
            "val function struct_pack_fs4 (fmt: int) (d: array int) : array int\n"
            "    requires { Array.length d = 4 }\n"
            "    ensures  { Array.length result = 4 }",
            "val function struct_unpack_fs4 (fmt: int) (data: array int) : array int",
        ],
        # UnixFs.Content (gap-17): the inode SIZE view. `inode_size disk ino`
        # is the big-endian uint32 decode of the four on-disk bytes at
        # 512 + ino*64 (the inode SIZE field, struct '>I...' field 0). It is a
        # DEFINED logic function (= the concrete decode), NOT an abstract
        # `val function` + axiom — so it adds ZERO trust and ZERO registry axiom:
        # Why3 unfolds the definition, and _read_inode/_write_inode's body-proven
        # decode ensures already establish the bytes. Naming it keeps the content
        # round-trip contracts (sys_read returns it, sys_write sets it, sys_open
        # frames it) legible across the abstract close/reopen. Emitted only when a
        # contract references `inode_size(...)` (the os model) — other files stay
        # byte-identical.
        "UnixFs.Content.": [
            "function inode_size (disk: array int) (ino: int) : int =\n"
            "    disk[512 + ino*64 + 0] * 16777216 + disk[512 + ino*64 + 1] * 65536\n"
            "    + disk[512 + ino*64 + 2] * 256 + disk[512 + ino*64 + 3]",
            # gap-17 content round-trip: the FOLDED content-equality predicate. An
            # uninterpreted atom (NOT a defined predicate that auto-unfolds) so it
            # crosses the no_inline boundary as ONE atom — the per-byte `\forall i`
            # content claim does NOT propagate (Alt-Ergo+Z3 Unknown), but this folded
            # atom does (exactly the uniq / inode_bytes_valid pattern). Its meaning is
            # fixed by the DEFINITIONAL intro/elim below (zero trust). `block_content_eq
            # d blk data` ≜ the first `length data` bytes of data-block `blk` of disk `d`
            # equal `data` element-for-element.
            "predicate block_content_eq (d: array int) (blk: int) (data: array int)",
        ],
        # UnixFs.Dir: the directory-scan reflection axiom's backing symbols.
        # `slot_inode`/`slot_name` are the abstract per-slot decode (disk, blk,
        # k) -> inode / name; `dir_lookup` is the logic model of the bounded
        # scan result. All three are `val function` (program + logic) so the os
        # model's `_dir_lookup` can BIND its result to `dir_lookup` and its
        # name_present predicate to the `slot_inode`/`slot_name` existential —
        # the load-bearing risk-2 binding that makes the cited ensures
        # constrain the REAL scan. Abstract-ops dedup skips these here.
        "UnixFs.Dir.": [
            "val function slot_inode (disk: array int) (blk: int) (k: int) : int",
            "val function slot_name  (disk: array int) (blk: int) (k: int) : string",
            "val function dir_lookup (disk: array int) (blk: int) (name: string) : int",
            # allocator-frame plan §2a: the two disk class invariants as ABSTRACT
            # (opaque) predicates, so a callee that maintains them exposes
            # `uniq self.disk` / `inode_bytes_valid self.disk` as a single ATOM that a
            # caller's exit-invariant goal matches directly — instead of the inline
            # double-`forall` the caller cannot cheaply discharge (the allocators'
            # fast-Unknown goals). Their meaning is fixed by the definitional
            # intro/elim axioms below (a conservative definition: sound by
            # construction, no proof-assistant validation needed).
            "predicate uniq (d: array int)",
            "predicate inode_bytes_valid (d: array int)",
            # M4: every block-5 dirent slot decodes to an inode < 32 (see slots_lt32_intro/elim).
            "predicate slots_lt32 (d: array int)",
            # ROUTE 1 (2026-06-19): the UNIQUE marker atom for the dir-mutator
            # invariant-maintenance fold. An uninterpreted predicate (NOT a defined
            # predicate that auto-unfolds) keyed by dir_blit_marker_intro /
            # dir_blit_marker_insert / dir_blit_marker_zero — all triggered
            # `[dir_blit_marker d0 d1 s b0 b1]`, so the maintenance step fires ONLY
            # where the mutator body asserts the marker, NEVER on a raw
            # `disk[2560+<expr>]` byte read (the trigger-poison wall fix). d0 = pre,
            # d1 = post, s = slot, (b0,b1) = the two blitted inode bytes.
            "predicate dir_blit_marker (d0 d1: array int) (s b0 b1: int) (name: string)",
            # READ-SIDE marker: the read dual of dir_blit_marker.
            # `dir_scan_result d blk name r` ≜ "r is the bounded 16-slot scan result
            # dir_lookup d blk name". A UNIQUE uninterpreted atom keyed
            # [dir_scan_result d blk name r] — fires ONLY where _dir_lookup's body
            # asserts it at loop exit, NEVER on a bare dir_lookup/slot_inode term, so
            # the value conclusion crosses SMT without re-introducing the gap-9
            # existential witness (it is discharged offline in UnixDirScanValue.{v,lean}).
            "predicate dir_scan_result (d: array int) (blk: int) (name: string) (r: int)",
            # READ-SIDE loop-carry prefix marker (the NON-inductive rung):
            # `dir_scan_prefix d blk name i r` ≜ "r is the scan result over the first i
            # slots". Carried as a loop invariant; advanced one slot per iteration via
            # dir_scan_prefix_step (O(1) marker-keyed), closed at i=16 to dir_scan_result.
            "predicate dir_scan_prefix (d: array int) (blk: int) (name: string) (i: int) (r: int)",
        ],
        # READ-SIDE SLOT-INDEX markers (the slot-index twin of dir_scan_result/
        # dir_scan_prefix): `dir_find_slot_result d blk name r` ≜ "r is the bounded
        # 16-slot index scan result" (the LAST live-match INDEX, or -1);
        # `dir_find_slot_prefix d blk name i r` ≜ "r is that index-scan over the
        # first i slots". UNIQUE uninterpreted atoms keyed
        # [dir_find_slot_result d blk name r] / [dir_find_slot_prefix d blk name i r],
        # firing ONLY where _dir_find_slot's body asserts them, NEVER on a bare
        # slot_inode/slot_name term, so the slot-index fidelity crosses SMT without
        # re-introducing the last-match argument (discharged offline in
        # UnixDirFindSlotValue.{v,lean}).
        #
        # GATING (byte-identity, same discipline as dir_blit_marker_at): keyed on the
        # MORE-SPECIFIC prefix "UnixFs.Dir.dir_find_slot" (NOT the general "UnixFs.Dir."
        # list above) so these two predicate declarations are emitted ONLY when a
        # dir_find_slot_* axiom is cited (i.e. by _dir_find_slot's os module), NOT for
        # every UnixFs.Dir.* citation. Sibling corpus modules (0711/0712) that cite
        # scan_reflects_present etc. but never the slot-index marker stay byte-identical.
        # `startswith` matches both prefixes for a dir_find_slot_* qualname, so the os
        # module still gets BOTH the general Dir decls AND these predicates.
        "UnixFs.Dir.dir_find_slot": [
            "predicate dir_find_slot_result (d: array int) (blk: int) (name: string) (r: int)",
            "predicate dir_find_slot_prefix (d: array int) (blk: int) (name: string) (i: int) (r: int)",
        ],
        # READ-SIDE FREE-SLOT-INDEX markers (the free-slot twin of
        # dir_find_slot_result/dir_find_slot_prefix): `dir_find_free_result d blk r`
        # ≜ "r is the bounded 16-slot free-index scan result" (the LAST free INDEX,
        # or -1); `dir_find_free_prefix d blk i r` ≜ "r is that free-index-scan over
        # the first i slots". UNIQUE uninterpreted atoms keyed
        # [dir_find_free_result d blk r] / [dir_find_free_prefix d blk i r], firing
        # ONLY where _dir_find_free's body asserts them, NEVER on a bare slot_inode
        # term, so the free-slot fidelity crosses SMT without re-introducing the
        # last-free argument (discharged offline in UnixDirFindFreeValue.{v,lean}).
        # No `name` parameter — _dir_find_free reads only slot_inode.
        #
        # GATING (byte-identity, same discipline as dir_find_slot): keyed on the
        # MORE-SPECIFIC prefix "UnixFs.Dir.dir_find_free" so these two predicate
        # declarations are emitted ONLY when a dir_find_free_* axiom is cited (i.e.
        # by _dir_find_free's os module), NOT for every UnixFs.Dir.* citation.
        # `startswith` matches both prefixes for a dir_find_free_* qualname, so the
        # os module still gets BOTH the general Dir decls AND these predicates.
        "UnixFs.Dir.dir_find_free": [
            "predicate dir_find_free_result (d: array int) (blk: int) (r: int)",
            "predicate dir_find_free_prefix (d: array int) (blk: int) (i: int) (r: int)",
        ],
        # BLOCK-PARAMETERIZED marker (2026-06-19): the arbitrary-block twin of
        # dir_blit_marker for _write_entry, which mutates self.disk at an ARBITRARY
        # block `block_num` (not the hardcoded block 5 of self.dir). Extra `blk`
        # parameter; keyed [dir_blit_marker_at d0 d1 blk s b0 b1 name] so it fires
        # ONLY where _write_entry's body asserts it, never on a raw disk[...] read.
        # Cross-validated zero-TCB by 0718.proofs (DirBlitMarkerAt.{v,lean}); the
        # block-5 family is its blk=5 instance (same proof, 5 -> blk).
        #
        # GATING: keyed on the MORE-SPECIFIC prefix "UnixFs.Dir.dir_blit_marker_at"
        # (NOT the general "UnixFs.Dir." list above) so the predicate declaration is
        # emitted ONLY when a dir_blit_marker_at* axiom is cited (i.e. by _write_entry's
        # os module), NOT for every UnixFs.Dir.* citation. This preserves byte-identity
        # for sibling corpus modules (0711/0712) that cite scan_reflects_present etc.
        # but never the block-parameterized marker. `startswith` matches both prefixes
        # for a dir_blit_marker_at_* qualname, so the os module still gets BOTH the
        # general Dir decls AND this predicate.
        "UnixFs.Dir.dir_blit_marker_at": [
            "predicate dir_blit_marker_at (d0 d1: array int) (blk s b0 b1: int) (name: string)",
        ],
    }

    @staticmethod
    def _func_returns_string_seq(func: Dict[str, Any]) -> bool:
        """str-list-elements: does `func` return a seq local whose elements are STRING
        (`seq_value_types[v] == "string"`)? Such a list is emitted as `array string` and
        carried through the `Return_seq_str (seq string)` exception."""
        svt = func.get("seq_value_types", {})
        if not svt:
            return False
        found = [False]

        def rec(node: Any) -> None:
            if isinstance(node, dict):
                if node.get("stmt") == "Return":
                    v = node.get("value")
                    if (isinstance(v, dict) and v.get("type") == "Var"
                            and svt.get(v.get("name")) == "string"):
                        found[0] = True
                for x in node.values():
                    rec(x)
            elif isinstance(node, list):
                for x in node:
                    rec(x)

        rec(func.get("body", []))
        return found[0]

    def _scan_preamble_needs(self, functions: List[Dict[str, Any]],
                             all_bodies: List[Any]) -> Dict[str, Any]:
        """Scan all function bodies once to collect feature flags for preamble emission."""
        has_list_param = any(
            v in ("list", "dict")
            for func in functions
            for v in func.get("symbol_table", {}).values()
        )
        needs_matrix = any(func.get("array2d_params") for func in functions)
        # Phase 3 of missing-bytes-struct-feature.md: axioms in
        # _AXIOM_REGISTRY may mention `array int` (e.g. round_trip on
        # struct_pack_i1a1). If any cited axiom contains that token,
        # force `use array.Array` even when the body is \trusted and
        # the IR scanner finds no array usage.
        axiom_needs_array = False
        for func in functions:
            for entry in func.get("proof", []):
                qn = entry.get("qualname", "")
                body = self._AXIOM_REGISTRY.get(qn, "")
                if "array int" in body or "array " in body:
                    axiom_needs_array = True
                    break
                # cleared-pack: the round-trip axiom body may be array-free
                # (`struct_unpack_fu16 fmt (struct_pack_fu16 fmt x0) = x0`) while
                # the BACKING `_AXIOM_FUNCTIONS` `val function` decls it pulls
                # return/consume `array int`. Scan those decls too, else the
                # emitted `val function struct_pack_fu16 … : array int` has no
                # `use array.Array` in scope.
                for prefix, fn_decls in self._AXIOM_FUNCTIONS.items():
                    if qn.startswith(prefix) and any(
                            "array int" in d or "array " in d for d in fn_decls):
                        axiom_needs_array = True
                        break
                if axiom_needs_array:
                    break
            if axiom_needs_array:
                break
        # gap-9: an axiom-backing logic function with an `array int` parameter
        # (`dir_lookup`/`slot_inode`/`slot_name`) may be applied in a CONTRACT
        # without its qualname being cited in THIS module (the importer/driver
        # case: the os wrappers' `dir_lookup(disk, 5, name) >= 0` presence view,
        # propagated from a trusted stub). Force `use array.Array` so the emitted
        # `val function dir_lookup (disk: array int) …` decl typechecks.
        if not axiom_needs_array:
            array_fn_names: Set[str] = set()
            for _decls in self._AXIOM_FUNCTIONS.values():
                for _d in _decls:
                    if "array int" in _d or "array " in _d:
                        _p = _d.split()
                        if len(_p) >= 3 and _p[0] == "val" and _p[1] == "function":
                            array_fn_names.add(_p[2])
                        elif len(_p) >= 2 and _p[0] == "function":
                            array_fn_names.add(_p[1])

            def _refs_array_fn(node: Any) -> bool:
                if isinstance(node, dict):
                    if node.get("type") == "Call" and node.get("func") in array_fn_names:
                        return True
                    return any(_refs_array_fn(v) for v in node.values())
                if isinstance(node, list):
                    return any(_refs_array_fn(v) for v in node)
                return False

            for func in functions:
                contracts = func.get("contracts", {}) or {}
                if any(_refs_array_fn(contracts.get(k, []))
                       for k in ("requires", "ensures", "assigns")):
                    axiom_needs_array = True
                    break
        # 07-1311 Q4: collection-typed quantifier binders (in contracts) need their
        # theory even with no array/map locals — `\forall a: list;` → array.Array,
        # `\forall m: dict;` → map.Map. Scan the whole function IR (contracts + body).
        _coll_binders: Set[str] = set()
        for func in functions:
            _coll_binders |= IRScanner.collection_binder_kinds(func)
        _binder_needs_array = bool(_coll_binders & {"list", "bytes", "bytearray"})
        _binder_needs_map = "dict" in _coll_binders
        if self._value_semantic:
            needs_array = (
                has_list_param
                or any(IRScanner.uses_for(body) for body in all_bodies)
                or any(IRScanner.uses_subscript(body) for body in all_bodies)
                or any(IRScanner.uses_arrayset(body) for body in all_bodies)
                or any(IRScanner.uses_array_lit(body) for body in all_bodies)
                or any(IRScanner.uses_str_split_comp(body) for body in all_bodies)
                or any(IRScanner.uses_ghost_type(body, {"array"}) for body in all_bodies)
                or axiom_needs_array
                or _binder_needs_array
                # the emit_ir ADT (emitted for any @mutable_state module OR — tier3-p1 — any
                # IR-node-typed param) declares `args_of : array emit_ir`, so `use array.Array`
                # is required even when the bodies use no other array. Both gates are False for
                # the corpus → byte-identical.
                or bool(getattr(self, "_mutable_state_classes", None))
                or bool(getattr(self, "_uses_ir_node_param", False))
                # the stmt_ir ADT theory (append convention OR the tree-walk
                # recogniser) declares `array int` body readers → needs Array.
                or self._uses_stmt_ir()
                # J1: the Call-internals theory declares `args_of : array emit_ir`
                # (via the full emit_ir theory it forces) → needs Array. Byte-inert
                # elsewhere (`_uses_call_kw` False for the whole corpus).
                or self._uses_call_kw()
                # L1: the tparam theory forces the full emit_ir theory (`args_of :
                # array emit_ir`) → needs Array. Byte-inert (`_uses_tparam` False
                # for the whole corpus).
                or self._uses_tparam()
            )
        else:
            needs_array = False
        needs_minmax = any(IRScanner.uses_minmax(body) for body in all_bodies)
        needs_continue = any(IRScanner.uses_continue(body) for body in all_bodies)
        needs_break = any(IRScanner.uses_break(body) for body in all_bodies)
        needs_return_exc = False
        needs_return_void = False
        needs_return_seq = False
        needs_return_seq_str = False
        needs_return_str = False
        needs_return_emit_ir = False
        tuple_return_arities: Set[int] = set()
        # value-model campaign incr5 (primitive c): synthesized-union (`Optional[X]`) return
        # types that need a dedicated `Return_<variant>` exception — a function returning a
        # `_union_*` variant WITH an early/in-loop return can't carry the variant through the
        # generic `exception Return int`. Parallel to needs_return_str/needs_return_emit_ir.
        union_return_types: Set[str] = set()
        n = len(functions)
        i = 0
        while i < n:
            func = functions[i]
            has_ret = IRScanner.has_in_loop_return(func["body"]) or IRScanner.has_early_return(func["body"])
            if has_ret:
                ret_type = IRScanner.find_return_type(func["body"])
                ann = func.get("return_annotation")
                if ret_type == "unit":
                    needs_return_void = True
                elif ret_type.startswith("(") and "," in ret_type:
                    # Tuple return — needs a dedicated Return_<arity> exception
                    # so the value carries through; the plain `exception Return int`
                    # would force `_coerce_to_int` to hash the whole tuple.
                    tuple_return_arities.add(ret_type.count(",") + 1)
                elif ret_type == "array int" or ann in ("list", "bytes", "bytearray"):
                    # return-arr.md: an array-returning function with early/in-loop returns.
                    # Why3 forbids a mutable `array int` exception payload, so carry the value
                    # through an IMMUTABLE `seq int` and materialize at the catch. (The array-ness
                    # often comes from the `-> list` annotation, not find_return_type.)
                    needs_return_seq = True
                    # str-list-elements: a list whose returned seq local carries STRING
                    # elements travels through the parallel `Return_seq_str (seq string)`.
                    # The type-driven signal `return_value_type == "string"` (the `-> List[str]`
                    # annotation, item34.md CF5) ALSO fires it: it is authoritative for the
                    # `array string` return type in `_compute_return_type` — and hence for the
                    # raise site's `Return_seq_str` (func_ret == "array string") — even when the
                    # body returns a list LITERAL (`return [x]` / `return []`) whose elements are
                    # not a seq-local Var and so are invisible to `_func_returns_string_seq`.
                    # ADDITIVE (keeps the always-on `needs_return_seq`): the extra int-typed
                    # `Return_seq` decl is unused-but-harmless, and any corpus function this newly
                    # fires for currently FAILS L3-tc (unbound `Return_seq_str`), so it cannot be
                    # in a passing baseline — byte-diff-0 preserved.
                    if (self._func_returns_string_seq(func)
                            or func.get("return_value_type") == "string"):
                        needs_return_seq_str = True
                elif ret_type == "string" or ann == "str":
                    # 10-1732-gap Gap 1: a faithful `string`-returning function with an
                    # early/in-loop return carries a `string` payload — the generic
                    # `exception Return int` would mis-type it. Mirror the Return_seq
                    # machinery with a dedicated `exception Return_str string`. (The
                    # string-ness usually comes from the `-> str` annotation, since
                    # find_return_type reports `int` for a string body.) Structured so a
                    # later `Return_<T>` generalization (real/record) slots in here.
                    needs_return_str = True
                elif isinstance(ann, str) and ann.startswith("_union_"):
                    # value-model campaign incr5 (primitive c): the function's return
                    # annotation resolves to a synthesized `_union_*` variant (an `Optional[X]`
                    # normalized by Module5). With an early/in-loop return the value travels
                    # through a dedicated `exception Return_<variant> <variant>` (declared
                    # below), NOT the generic `Return int`. The trusted union stubs have no
                    # early return (they hit this loop only via `has_ret`), so ONLY genuinely
                    # body-verified union walkers register — corpus-inert (a corpus Optional[X]
                    # function with an early return currently fails the `Return int` clash, so
                    # none is in a passing baseline).
                    union_return_types.add(ann)
                elif (IRScanner.returns_emit_ir_literal(func["body"])
                      or ann in ("ExprIR", "StmtIR", "IRNode", "ContractExprIR")):
                    # NODE-CTOR (self-tcb-reduction): the SAME need, reached via the
                    # DECLARED return annotation instead of a dict-literal body shape —
                    # a recursive-descent method annotated `-> "ExprIR"` whose early
                    # return carries a CLASS-constructed node (`return UnaryOp(op, …)`,
                    # lowered to `(IrUnaryOp …)` by `_call_irnode_constructor`). The
                    # literal-shape scanner cannot see through a class construction, so
                    # the annotation is the detector here. Same annotation set
                    # `_compute_return_type` already maps to `emit_ir`.
                    # Return_emit_ir infra: an emit_ir-returning function (a recursive
                    # `_csl_*`-style dispatcher building a `{"type": K}` IR-node literal)
                    # with an early/in-loop return carries the node payload through a
                    # dedicated `exception Return_emit_ir emit_ir` — the plain `exception
                    # Return int` would mis-type it (int is not emit_ir). Mirrors the
                    # Return_str/Return_seq machinery above. `find_return_type` reports
                    # `int` for a dict-literal body (like it does for string bodies), so
                    # this static literal-shape check (not `ret_type`/`ann`) is the
                    # detector — see IRScanner.returns_emit_ir_literal.
                    needs_return_emit_ir = True
                else:
                    needs_return_exc = True
            i += 1
        needs_string = (
            any(IRScanner.uses_ghost_type(body, {"string"}) for body in all_bodies)
            # strings-plan Stage 1: a runtime `str` param/local/return also needs string.String
            or needs_return_seq_str  # str-list-elements: `array string` / `seq string`
            or any("str" in f.get("symbol_table", {}).values() for f in functions)
            or any(f.get("return_annotation") == "str" for f in functions)
        )
        # 10-2300-spec-5: the `ord`/`chr` char<->int bridge needs `use string.Char`
        # (a sibling module of the already-used `string.String`, same trusted
        # `string.mlw`). Emitted ONLY when an `ord(...)`/`chr(...)` call is present —
        # absent from the corpus, so existing emission stays byte-identical.
        # string-codec Phase A': `ord`/`chr` may appear ONLY in a CONTRACT (the codec
        # round-trip's encoding precondition), and a cited Char-using axiom (the
        # field codec) references `Char.*` with no body occurrence at all — both must
        # also pull `use string.Char`.
        needs_char = any(IRScanner.uses_ord_chr(body) for body in all_bodies) \
            or any(IRScanner.uses_ord_chr(f.get("contracts", {})) for f in functions) \
            or any("Char." in self._AXIOM_REGISTRY.get(e.get("qualname", ""), "")
                   for f in functions for e in f.get("proof", []))
        # WL-02: a Python TRUE-division `/` (IR BinOp op "/") in a body or contract lowers
        # to a REAL division (`from_int a /. from_int b`) — Python `/` always returns a
        # float. This needs `real.RealInfix` (`/.`) AND `real.FromInt` (`from_int`), even
        # when the file has no explicit `float` var/return (the int-return misuse must
        # fail-close as a real-vs-int type error, not silently truncate). Distinct from
        # FLOOR division `//` (IR op "div"), which stays integer (WL-01).
        needs_truediv = (
            any(IRScanner.uses_true_division(body) for body in all_bodies)
            or any(IRScanner.uses_true_division(f.get("contracts", {})) for f in functions)
        )
        # no-more-int Stage D: a `float` param/local/return is Why3 `real`; RealInfix
        # provides the disambiguated `+.`/`-.`/`*.`/`/.`/`<.` operators alongside int.Int.
        needs_real = (
            any("float" in f.get("symbol_table", {}).values() for f in functions)
            or any(f.get("return_annotation") == "float" for f in functions)
            or needs_truediv  # WL-02: `/.` real division
        )
        # no-more-int-7 §B′: a `seq int`-valued dict (`Dict[_, List[int]]`) needs
        # `seq.Seq` for the immutable list-snapshot model.
        needs_seq = any(
            "seq" in v for f in functions for v in f.get("dict_value_types", {}).values()
        ) or any(f.get("seq_promoted_vars") for f in functions) \
          or needs_return_seq \
          or bool(getattr(self, "_mutable_state_classes", None)) \
          or any(t.startswith("seq ") for f in functions
                 for t in f.get("param_list_nested_elem", {}).values()) \
          or any(f.get("vararg_str_param") for f in functions) \
          or bool(getattr(self, "_module_str_list_constants", None)) \
          or self._uses_stmt_ir()
        # ^ W8 (ii): a `*vals: str` vararg param is a `seq string` -> `use seq.Seq`.
        #   Module5 records it only for a str-ANNOTATED vararg, so no corpus function
        #   triggers it (byte-identical).
        # ^ nested-list.md S2: a `List[List[τ]]` param is `array (seq τ)` → `use seq.Seq`.
        # ^ seq-model-pivot.md SQ1: a @mutable_state module may promote a REASSIGNED list-elem
        #   local to `seq` (decided during emission, after this import scan), so `use seq.Seq`
        #   must be present. The 627-corpus has no @mutable_state class → byte-identical.
        needs_map_ghost = any(IRScanner.uses_ghost_type(body, {"ghost_dict", "ghost_set"}) for body in all_bodies)
        needs_ghost_dict = any(IRScanner.uses_ghost_type(body, {"ghost_dict"}) for body in all_bodies)
        # Body-level Python dicts are modelled as `ref (map int (option int))`
        # (parallel to ghost dicts). Triggered by:
        #   - `find_array_and_dict_vars` detecting any `d = {}` / `d = dict()`
        #     / `d = {k: v}` / `s = set()` / `s = {a, b}` in the body.
        #   - inline set/dict literals (e.g. `held | {mutex}`) or
        #     `.add()`/`.discard()`/`.remove()` method calls anywhere in
        #     the IR — these emit `map_update_some` / `map_update_none`
        #     into the abstract-val block, which requires `use map.Map`
        #     and `use option.Option` in the preamble.
        needs_body_dict = False
        for body in all_bodies:
            _arr, body_dicts = IRScanner.find_array_and_dict_vars(body)
            if body_dicts or IRScanner.uses_inline_set_or_dict_ops(body):
                needs_body_dict = True
                break
        # Map types can also appear ONLY in function signatures (set/dict/
        # frozenset parameters lowered by `_param_type_str` to
        # `map int (option int)`), without any body-level map usage.
        # Without this check the preamble omits `use map.Map` and the
        # signature's `map` type symbol is unbound — see
        # `src/self-annotate/src/exception_model.py:predicate_definitions`
        # which takes a `set` parameter but has no body-level dict ops.
        if not needs_body_dict:
            for func in functions:
                if any(v in ("set", "dict", "frozenset")
                       for v in func.get("symbol_table", {}).values()):
                    needs_body_dict = True
                    break
        # cleared-array item 3: a function that RETURNS a set/dict/frozenset
        # (`-> Dict[int, int]` / `-> set`) has WhyML type `map int (option int)`
        # in its signature, so the map vocabulary must be imported even with no
        # body-level dict op — e.g. `def d(a) -> Dict: return {x: v for x in a}`
        # (a content-faithful dict comprehension). Mirrors the param-type check.
        if not needs_body_dict:
            for func in functions:
                if func.get("return_annotation") in ("set", "dict", "frozenset"):
                    needs_body_dict = True
                    break
        # nested-list.md S2: a `List[Dict[..]]`/`List[Set[..]]` param is
        # `array (map κ (option ν))` → needs `map.Map` + `option.Option`.
        if not needs_body_dict:
            for func in functions:
                if any(t.startswith("map ")
                       for t in func.get("param_list_nested_elem", {}).values()):
                    needs_body_dict = True
                    break
        # 07-1311 Q4: a `\forall m: dict;` binder needs `map.Map`/`option.Option` too.
        if _binder_needs_map:
            needs_body_dict = True
            needs_ghost_dict = True
        # option-of-record projection (boundary-1 G1 extension): an `Optional[<record>]`
        # param (symbol_table symtype `"option:<R>"`) lowers to `option <record>` in the
        # signature, so `option.Option` must be `use`d even with no body dict/map. Mirrors
        # the set/dict param-type check above. Gated on the `option:` symtype prefix →
        # byte-inert for every module without an Optional-of-record param.
        needs_option_record = any(
            isinstance(v, str) and v.startswith("option:")
            for func in functions
            for v in func.get("symbol_table", {}).values()
        )
        needs_list_ghost = any(IRScanner.uses_ghost_type(body, {"ghost_list"}) for body in all_bodies)
        needs_sum = any(IRScanner.uses_sum(func) for func in functions)
        needs_set_card = any(IRScanner.uses_set_card(func) for func in functions)
        needs_divmod = any(IRScanner.uses_divmod(body) for body in all_bodies)
        # `no_exception` predicate vocabulary is emitted if any function in
        # the file declares a no_exception clause (Phase 1 NoException
        # workplan). See src/pycsl/exception_model.py for the predicates.
        needs_no_exception = any(
            func.get("contracts", {}).get("no_exception") or
            func.get("contracts", {}).get("no_exception_all")
            for func in functions
        )
        bounded_sizes = {func["bounded_int"] for func in functions if func.get("bounded_int")}
        user_exceptions: Set[str] = set()
        n2 = len(all_bodies)
        i2 = 0
        while i2 < n2:
            user_exceptions |= IRScanner.collect_user_exceptions(all_bodies[i2])
            i2 += 1
        # Also surface exceptions named only in a `raises` CONTRACT clause
        # (e.g. an `\abstract` val with `raises SyntaxError when ...` and no
        # body raise) — collect_user_exceptions scans bodies, not specs, so
        # such an exception would otherwise be an unbound symbol in WhyML.
        for func in functions:
            for rc in func.get("contracts", {}).get("raises", []):
                exc = rc.get("exc_type")
                if exc:
                    user_exceptions.add(exc)
        # bigger-build.md Phase 1: a function whose body is the A-unit generic-fold
        # catamorphism (recognizer, fail-closed) routes to the type-derived walk
        # group and needs the L1 `pyval`/`pydict`/`size` theory. Gated + corpus-inert
        # (fires on 0/756 programs) → byte-diff-0.
        from module6_whyml.generic_fold import (
            recognize_generic_fold, recognize_setfold, recognize_substmap,
            recognize_self_method_calls,
            recognize_bool_existence, recognize_bool_multiway, recognize_frt,
            recognize_sawalk, recognize_cpwalk, recognize_pbexpr,
            recognize_dictfold,
            recognize_void_dispatch,
            recognize_stmt_setfold, recognize_void_generic_descend,
            recognize_wall2_items_walk,
            recognize_walk_dicts_generator, recognize_walk_dicts_bool_consumer,
            recognize_walk_dicts_void_consumer, recognize_walk_dicts_set_consumer,
            recognize_boolfold_isinstance,
            recognize_flat_tag_func_pred,
            recognize_type_existence, recognize_named_field_existence,
            recognize_pyval_string_walker, recognize_pyval_list_walker,
            recognize_pyval_flatten, recognize_ir_free_vars,
            recognize_check_class_invariants,
            recognize_check_gt3_schema_only,
            recognize_check_bounds,
            recognize_check_mutex_invariants,
            recognize_check_callable_params,
            recognize_check_fresh_globals,
            recognize_check_noreturn,
            recognize_first_tuple_return,
            recognize_find_assigned_vars,
            recognize_first_assign_value_ir,
            recognize_collect_mutations,
            recognize_find_iteration_mutations,
            recognize_build_method_writes_map,
            recognize_collect_record_fields,
            recognize_verify_module_groups,
            recognize_build_method_result_ensures_map,
            recognize_build_method_field_result_ensures_map,
            recognize_build_method_field_old_ensures_map,
            recognize_test_contains_map,
            recognize_is_linear_vc,
            recognize_handler_catches,
            recognize_subclasses_of,
            recognize_collect_escaping_exceptions,
            recognize_callee_implicit_exceptions,
            recognize_find_array_and_dict_vars,
            recognize_classify,
            recognize_global_call_target,
            recognize_method_edges,
            recognize_refs_bvar,
            recognize_cs_clause, recognize_check_contract_exprs,
            recognize_check_body_walk,
            recognize_check_subscript_assignments,
            recognize_check_contract_scope,
            recognize_check_clause_fold,
            recognize_check_no_exception, recognize_check_warn_fold)
        # NoReturn dead-successor WALKER + CALLER (ghost-assign-bc6): the stateful
        # bool-carry walker `_noreturn_walk_stmts` (#3) and its caller
        # `_check_noreturn_successors` (#4). Both are FORWARD REFERENCES (the
        # walker calls the textually-later `_stmt_is_noreturn_call`; the caller
        # calls the walker), so both are emitted DEFERRED — appended right after
        # the `_stmt_is_noreturn_call` group. `_nrw_funcs`/`_ccns_funcs` hold the
        # recognised func dicts + descriptors; the `_emitted` sets gate the
        # once-only append. The caller is recognised only when its walker is a
        # converted (recognised) walker name. Set up BEFORE the `needs_*` gates
        # (which read `self._nrw_names`). Corpus-inert.
        from module6_whyml.generic_fold import (
            recognize_noreturn_walk_stmts, recognize_check_noreturn_successors)
        self._nrw_funcs = [
            (f, recognize_noreturn_walk_stmts(f)) for f in functions
            if recognize_noreturn_walk_stmts(f) is not None]
        self._nrw_names = {f.get("name") for f, _ in self._nrw_funcs}
        self._nrw_emitted = set()
        self._ccns_funcs = [
            (f, recognize_check_noreturn_successors(f, self._nrw_names))
            for f in functions
            if recognize_check_noreturn_successors(f, self._nrw_names) is not None]
        self._ccns_names = {f.get("name") for f, _ in self._ccns_funcs}
        self._ccns_emitted = set()
        # ir-traversal-residual T3: the context-threading walk `_sa_walk` routes
        # to the env-threaded pyval/pydict group and additionally needs the
        # string-keyed `sdict` theory (`needs_sdict`, gated separately so the
        # already-landed pydict-group mirrors stay byte-identical).
        from module6_whyml.generic_fold import recognize_rewrite_ir_calls
        needs_sdict = any(
            # seven-levers §1 (Lever 1): `_rewrite_ir_calls`'s `rw` reads
            # `obj.get(...)` via the program-context `pget_dyn` reader (bridge
            # theory, emitted with the sdict block); route sdict on so the reader
            # is in scope.
            recognize_rewrite_ir_calls(f) is not None or
            recognize_sawalk(f) is not None or recognize_dictfold(f) is not None
            or recognize_pbexpr(f) is not None
            or recognize_cs_clause(f) is not None
            or recognize_check_class_invariants(f) is not None
            or recognize_check_gt3_schema_only(f) is not None
            or recognize_check_bounds(f) is not None
            or recognize_check_mutex_invariants(f) is not None
            or recognize_check_callable_params(f) is not None
            or recognize_check_fresh_globals(f) is not None
            or recognize_check_noreturn(f) is not None
            or recognize_first_tuple_return(f) is not None
            or recognize_find_assigned_vars(f) is not None
            or recognize_first_assign_value_ir(f) is not None
            or recognize_collect_mutations(f) is not None
            or recognize_find_iteration_mutations(f) is not None
            or recognize_test_contains_map(f) is not None
            or recognize_is_linear_vc(f) is not None
            or recognize_handler_catches(f) is not None
            or recognize_subclasses_of(f) is not None
            or recognize_classify(f) is not None
            or recognize_global_call_target(f) is not None
            or recognize_method_edges(f) is not None
            or recognize_check_contract_exprs(f) is not None
            or recognize_check_body_walk(f) is not None
            or recognize_check_subscript_assignments(f) is not None
            or recognize_check_contract_scope(f) is not None
            or recognize_check_clause_fold(f) is not None
            or recognize_check_no_exception(f) is not None
            or recognize_check_warn_fold(f) is not None
            for f in functions)
        # pdict-to-sdict-impl.md: the heterogeneous-func caller cluster
        # (`_check_contract_exprs` + the body-only `_check_checkpoints`/
        # `_check_ghost_string_ops` siblings) additionally needs the pydict->sdict
        # bridge theory (`pget_dyn`/`pget_list`/`pdict_to_sdict`). Gated separately
        # so every already-landed sdict mirror stays byte-identical; corpus-inert.
        from module6_whyml.generic_fold import (
            recognize_collect_noreturn_names, recognize_stmt_noreturn_call,
            recognize_noreturn_walk_stmts, recognize_check_noreturn_successors,
            recognize_rewrite_ir_calls)
        needs_pdict_bridge = any(
            recognize_check_contract_exprs(f) is not None
            or recognize_check_body_walk(f) is not None
            or recognize_check_subscript_assignments(f) is not None
            or recognize_check_contract_scope(f) is not None
            or recognize_check_clause_fold(f) is not None
            or recognize_check_no_exception(f) is not None
            or recognize_check_warn_fold(f) is not None
            # #1 `_collect_noreturn_names` reads `ir["functions"]` via `pget_list`.
            or recognize_collect_noreturn_names(f) is not None
            # #3/#4 the walker + caller read child/functions lists via `pget_list`.
            or recognize_noreturn_walk_stmts(f) is not None
            or recognize_check_noreturn_successors(f, self._nrw_names) is not None
            # class-invariant / gt3 checkers read fields/type_params via pget_list.
            or recognize_check_class_invariants(f) is not None
            or recognize_check_gt3_schema_only(f) is not None
            or recognize_check_bounds(f) is not None
            or recognize_check_mutex_invariants(f) is not None
            or recognize_check_callable_params(f) is not None
            or recognize_check_fresh_globals(f) is not None
            or recognize_check_noreturn(f) is not None
            or recognize_first_tuple_return(f) is not None
            or recognize_find_assigned_vars(f) is not None
            or recognize_first_assign_value_ir(f) is not None
            or recognize_collect_mutations(f) is not None
            or recognize_find_iteration_mutations(f) is not None
            or recognize_test_contains_map(f) is not None
            or recognize_is_linear_vc(f) is not None
            or recognize_handler_catches(f) is not None
            or recognize_subclasses_of(f) is not None
            or recognize_classify(f) is not None
            or recognize_global_call_target(f) is not None
            or recognize_method_edges(f) is not None
            # Lever 1 (`_rewrite_ir_calls`): the `rw` walk reads `obj.get(...)`
            # via `pget_dyn` (bridge theory).
            or recognize_rewrite_ir_calls(f) is not None
            for f in functions)
        # seven-levers §1 (Lever 1): the pydict WRITE half (`pput`/`pappend` +
        # the by-reference `#@ assigns` frame). Gated separately so every
        # already-landed pydict mirror stays byte-identical; corpus-inert (only
        # a construction recognizer sets it).
        from module6_whyml.generic_fold import recognize_substitute
        from module6_whyml.generic_fold import recognize_subst_params
        needs_pput = any(
            recognize_rewrite_ir_calls(f) is not None
            or recognize_substitute(f) is not None
            for f in functions)
        from module6_whyml.generic_fold import (
            recognize_closure_existence_pairs, recognize_lemma_string_search_pairs,
            recognize_func_returns_string_seq_pairs,
            recognize_returns_string_seq_pairs,
            recognize_struct_pack_targets_pairs,
            recognize_struct_unpack_targets_pairs,
            recognize_contract_referenced_names_pairs,
            recognize_field_decode_str_locals_pairs,
            recognize_string_elem_read_locals_pairs,
            recognize_callee_raised_direct_pairs,
            recognize_contract_referenced_var_names_pairs,
            recognize_collect_map_typed_locals_pairs,
            recognize_has_set_op_on_map_pairs,
            recognize_is_linear_expr_pairs,
            recognize_extract_array_lengths_pairs,
            recognize_final_pair, recognize_check_final, recognize_conc_cluster,
            recognize_scan2d_trio, recognize_symtab_set_dispatch)
        # CONCURRENCY CLUSTER (generic_fold.py): the mutually-trusted held-mutex
        # / lock-order protected-access walk {_check_concurrency,
        # _conc_check_shared_access, _conc_check_reads, _conc_stmts, _conc_stmt}
        # emitted as ONE self-contained `let rec` block (conc_spike.mlw 17/17,
        # emitted 18/18 Valid). None (no cluster) -> every other mirror + the
        # whole corpus byte-identical (self-annotate-mirror-only match).
        self._conc_cluster = recognize_conc_cluster(functions)
        self._conc_names = (
            set(self._conc_cluster["names"]) if self._conc_cluster else set())
        self._conc_emitted = False
        # UNION-NARROWING cluster (generic_fold.py): the 4-function
        # {_union_c8_walk, _union_c8_test_references_union_var,
        # _union_c8_recognized_guard, _union_c11_check_dead_arms} C8/C11 check,
        # emitted as ONE self-contained `let rec` block onto the pyval spine so
        # all four un-trust together (the driver `_check_union_narrowing` stays
        # \trusted). None (no cluster) -> every other mirror + the whole corpus
        # byte-identical (self-annotate-mirror-only match).
        from module6_whyml.generic_fold import recognize_union_cluster
        self._union_cluster = recognize_union_cluster(functions)
        self._union_names = (
            set(self._union_cluster["names"]) if self._union_cluster else set())
        self._union_emitted = False
        # FINAL PAIR FUSION (generic_fold.py): the `{_final_walk_body,
        # _final_check_stmt}` Final write-policy walker pair re-based onto the
        # pyval spine (mutually-recursive `let rec` group so `_final_check_stmt`
        # can be un-trusted). Module-level (needs both functions). None (no pair)
        # -> every other mirror + the whole corpus byte-identical.
        self._final_pair = recognize_final_pair(functions)
        self._final_pair_names = (
            set(self._final_pair["names"]) if self._final_pair else set())
        self._final_pair_emitted = False
        # SCAN-2D TRIO FUSION (generic_fold.py): the mutually-recursive
        # `{_scan_2d_in_expr,_scan_2d_in_stmt,_collect_2d_params}` 2-D-access
        # walker triad emitted as ONE self-contained `let rec … with …` group at
        # the first-reached member slot (real cross-calls between the lifted
        # siblings); set_add gated by the `Map.get pn nm` membership. Module-level
        # (needs all three). None (no trio) -> every other mirror + the whole
        # corpus byte-identical.
        self._scan2d_trio = recognize_scan2d_trio(functions)
        self._scan2d_trio_names = (
            set(self._scan2d_trio["names"]) if self._scan2d_trio else set())
        self._scan2d_trio_emitted = False
        # CHECK-FINAL CALLER (generic_fold.py): the `_check_final(ir)` Final
        # driver, re-based onto pyval and emitted RIGHT AFTER the pair group it
        # calls into. Gated on the pair (needs its walk-body name); None -> the
        # caller stays `\trusted` and every other mirror stays byte-identical.
        self._check_final_desc = None
        if self._final_pair:
            _wn = self._final_pair["walk_name"]
            for _f in functions:
                if isinstance(_f, dict):
                    _cfd = recognize_check_final(_f, _wn)
                    if _cfd is not None:
                        self._check_final_desc = _cfd
                        break
        self._check_final_name = (
            self._check_final_desc["cf_name"] if self._check_final_desc else None)
        needs_pydict = needs_sdict or (self._final_pair is not None) \
            or (self._scan2d_trio is not None) \
            or (self._conc_cluster is not None) \
            or (self._union_cluster is not None) or bool(
            recognize_closure_existence_pairs(functions)["outer_ids"]) or bool(
            recognize_lemma_string_search_pairs(functions)["outer_ids"]) or bool(
            recognize_func_returns_string_seq_pairs(functions)["outer_ids"]) or bool(
            recognize_returns_string_seq_pairs(functions)["outer_ids"]) or bool(
            recognize_struct_pack_targets_pairs(functions)["outer_ids"]) or bool(
            recognize_struct_unpack_targets_pairs(functions)["outer_ids"]) or bool(
            recognize_contract_referenced_names_pairs(functions)["outer_ids"]) or bool(
            recognize_field_decode_str_locals_pairs(functions)["outer_ids"]) or bool(
            recognize_string_elem_read_locals_pairs(functions)["outer_ids"]) or bool(
            recognize_callee_raised_direct_pairs(functions)["outer_ids"]) or bool(
            recognize_contract_referenced_var_names_pairs(functions)["outer_ids"]) or bool(
            recognize_collect_map_typed_locals_pairs(functions)["outer_ids"]) or bool(
            recognize_has_set_op_on_map_pairs(functions)["outer_ids"]) or bool(
            recognize_is_linear_expr_pairs(functions)["outer_ids"]) or bool(
            recognize_extract_array_lengths_pairs(functions)["outer_ids"]) or any(
            recognize_generic_fold(f) is not None or recognize_setfold(f) is not None
            or recognize_self_method_calls(f) is not None
            or recognize_substmap(f) is not None
            or recognize_substitute(f) is not None
            or recognize_subst_params(f) is not None
            or recognize_bool_existence(f) is not None
            or recognize_bool_multiway(f) is not None
            or recognize_frt(f) is not None
            or recognize_stmt_setfold(f) is not None
            or recognize_collect_escaping_exceptions(f) is not None
            or recognize_callee_implicit_exceptions(f) is not None
            or recognize_find_array_and_dict_vars(f) is not None
            or recognize_void_generic_descend(f) is not None
            or recognize_wall2_items_walk(f) is not None
            or recognize_walk_dicts_generator(f) is not None
            or recognize_walk_dicts_bool_consumer(f) is not None
            or recognize_walk_dicts_void_consumer(f) is not None
            or recognize_walk_dicts_set_consumer(f) is not None
            or recognize_boolfold_isinstance(f) is not None
            or recognize_flat_tag_func_pred(f) is not None
            or recognize_type_existence(f) is not None
            or recognize_named_field_existence(f) is not None
            or recognize_pyval_string_walker(f) is not None
            or recognize_pyval_list_walker(f) is not None
            or recognize_pyval_flatten(f) is not None
            or recognize_cpwalk(f) is not None
            or recognize_ir_free_vars(f) is not None
            # string-keyed-set NoReturn cluster: #1 `set_add`/`set_union` +
            # #2 `pystr_eq`/`Map.get` all live in the `needs_pydict` block.
            or recognize_collect_noreturn_names(f) is not None
            or recognize_stmt_noreturn_call(f) is not None
            # #3/#4 the walker + caller fold pyval/pydict/list with `pv_size`.
            or recognize_noreturn_walk_stmts(f) is not None
            or recognize_check_noreturn_successors(f, self._nrw_names) is not None
            # `_body_references_bvar_0` de-Bruijn depth-threading walk folds
            # pyval/pydict with `pv_size`/`size_dict` + `pystr_eq`.
            or recognize_refs_bvar(f) is not None
            # `_collect_mutations` ref-accumulator whole-stmt append folds
            # pyval/pydict/list (`pv_size`/`size_dict`/`size_list`) + `pystr_eq`.
            or recognize_collect_mutations(f) is not None
            or recognize_find_iteration_mutations(f) is not None
            # `_build_method_writes_map` folds pyval/pydict/list into a
            # `map string (list string)` result (`pv_size`/`size_dict`/`size_list`
            # + `Map.set`/`const`) + `pystr_eq`.
            or recognize_build_method_writes_map(f) is not None
            # `_collect_record_fields` StrSet set-collect + the
            # `_build_method_*_ensures_map` cluster fold pyval/pydict/list into a
            # `map string bool` / `map string (list pyval)` result (`pv_size`/
            # `size_dict`/`size_list` + `set_add`/`set_union`/`Map.set`/`const`) + `pystr_eq`.
            or recognize_collect_record_fields(f) is not None
            # `_verify_module_groups` folds pyval/pydict/list into a
            # `map string (list string)` result (`Map.set`/`Map.get`/`const`/`snoc`
            # + `pget_dyn`) via a pinned `__setappend`.
            or recognize_verify_module_groups(f) is not None
            or recognize_build_method_result_ensures_map(f) is not None
            or recognize_build_method_field_result_ensures_map(f) is not None
            or recognize_build_method_field_old_ensures_map(f) is not None
            # symtab-set-dispatch typing drivers (`_check_typeddict_access`/
            # `_check_namedtuple_access`/`_check_union_narrowing`): the pydict
            # `.items()` set-collect (`pget_dyn`/`pget_list`/`set_add`/`const`/
            # `Map.get`) then void-dispatch to a converted walker.
            or recognize_symtab_set_dispatch(
                f, {g.get("name"): g for g in functions if isinstance(g, dict)}) is not None
            # seven-levers §1 (Lever 1 — pydict WRITE half): `_rewrite_ir_calls`
            # folds pyval/pydict/list (`pv_size`/`size_dict`/`size_list`) and
            # `pput`s at Call nodes — needs the base pydict theory.
            or recognize_rewrite_ir_calls(f) is not None
            for f in functions)
        # G-void-dispatch-thin: the recognized wrapper's `stmts` is the built-in
        # Why3 `list int` (Cons/Nil, not the pyval/pydict L1 theory) — needs only
        # `list.List` in scope, gated separately from `needs_pydict`/
        # `needs_list_ghost` so their emission stays byte-identical. Gated +
        # never set by the reference corpus (self-annotate-mirror-only) → byte-diff-0.
        needs_void_dispatch = any(recognize_void_dispatch(f) is not None for f in functions)
        # class-variant-impl.md (driver-backlog item 3): the class-instance VARIANT
        # ADT carrier — the proof2why3 `Term` union (isinstance-dispatch + named-field
        # reads). Compute the `term` variant spec from the imported dataclass
        # type_decls + the file's fold usage; store it so the theory (gated) + the
        # dispatch both see the SAME spec. None (no term-fold) -> carrier off, corpus
        # + every other mirror byte-identical.
        from module6_whyml.generic_fold import (
            compute_term_adt_spec, recognize_term_isinstance_fold,
            recognize_term_isinstance_transform,
            recognize_term_list_build, recognize_term_flatten_arrow,
            recognize_term_free_vars, recognize_term_string_pp,
            recognize_term_pp_methods, recognize_pb_trio, recognize_cs_trio)
        # PB-TRIO FUSION (generic_fold.py): the mutually-recursive
        # `{_pb_stmt,_pb_body,_pb_descend}` statement-walker triad emitted as ONE
        # `let rec` group so `_pb_stmt` can be un-trusted. Module-level (needs all
        # three functions). None (no trio) -> every other mirror + the whole
        # corpus byte-identical. `_pb_trio_emitted` gates the once-only emission
        # (deferred to just after the `_pb_expr` group the trio calls into).
        self._pb_trio = recognize_pb_trio(functions)
        self._pb_trio_names = (
            set(self._pb_trio["names"]) if self._pb_trio else set())
        self._pb_trio_emitted = False
        # CS-TRIO FUSION: the `{_cs_stmt,_cs_body,_cs_descend}` scope-check triad
        # (cross-calls `_cs_clause`, deferred to just after the `_cs_clause`
        # group). Same once-only emit gating as the pb trio; corpus-inert.
        self._cs_trio = recognize_cs_trio(functions)
        self._cs_trio_names = (
            set(self._cs_trio["names"]) if self._cs_trio else set())
        self._cs_trio_emitted = False
        # pdict-to-sdict-impl.md (heterogeneous-func caller cluster): the
        # `_check_contract_exprs` caller is a FORWARD REFERENCE to its
        # `_pb_expr`/`_pb_body` callees (textually before them), so it is emitted
        # AFTER the `_pb_expr` group + pb-trio (same deferred-append plumbing).
        # `_cce_funcs` holds the recognised caller func dicts; `_cce_emitted`
        # gates the once-only append. Corpus-inert.
        from module6_whyml.generic_fold import recognize_check_contract_exprs
        self._cce_funcs = [
            f for f in functions if recognize_check_contract_exprs(f) is not None]
        self._cce_names = {f.get("name") for f in self._cce_funcs}
        self._cce_emitted = False
        # BODY-WALK caller siblings (`_check_checkpoints`/`_check_ghost_string_ops`):
        # each is a FORWARD REFERENCE to its `_cp_walk`/`_gso_walk` walker callee
        # (textually before it), so it is emitted AFTER its walker group, keyed on
        # the emitted walker's name. `_cbw_funcs` holds the recognised caller func
        # dicts (with their descriptors); `_cbw_emitted` gates each once-only append.
        from module6_whyml.generic_fold import recognize_check_body_walk
        self._cbw_funcs = [
            (f, recognize_check_body_walk(f)) for f in functions
            if recognize_check_body_walk(f) is not None]
        self._cbw_names = {f.get("name") for f, _ in self._cbw_funcs}
        self._cbw_emitted = set()
        # SYMTAB-SET-DISPATCH typing drivers (`_check_typeddict_access`/
        # `_check_namedtuple_access`/`_check_union_narrowing`): each BUILDS a
        # typed-var StrSet from `func["symbol_table"].items()` (membership/
        # startswith gate) then void-dispatches to an already-converted walker.
        # FORWARD REFERENCES (textually before their walker(s)), so emitted AFTER
        # all their walker deps (the `_check_final`/CSA precedent). `_ssd_funcs`
        # holds (caller, descriptor); `_ssd_walkers_seen` accumulates emitted
        # walker canon-names; `_ssd_emitted` gates each once-only append.
        from module6_whyml.generic_fold import recognize_symtab_set_dispatch
        _ssd_by_name = {f.get("name"): f for f in functions if isinstance(f, dict)}
        self._ssd_funcs = [
            (f, recognize_symtab_set_dispatch(f, _ssd_by_name)) for f in functions
            if recognize_symtab_set_dispatch(f, _ssd_by_name) is not None]
        self._ssd_names = {f.get("name") for f, _ in self._ssd_funcs}
        self._ssd_emitted = set()
        self._ssd_walkers_seen = set()
        # CLOSURE-FORM existence walk (`_body_has_diverging_construct`/
        # `_lemma_returns_value`): a `found=[False]` nested `def walk` existence
        # predicate whose lifted `walk` sibling shares the accumulator as an
        # int-erased global (a vacuous facade). Pair each OUTER wrapper with its
        # lifted `walk` (adjacency), emit the wrapper as the certified `list
        # pyval` existence catamorphism, and SUPPRESS the lifted `walk`. Keyed on
        # object identity (`id`) — the walks share the name `walk`, so a
        # name-keyed set would over-suppress. Corpus-inert (fires only on the
        # recognised mirror wrappers). See generic_fold.py module note.
        from module6_whyml.generic_fold import recognize_closure_existence_pairs
        _clx = recognize_closure_existence_pairs(functions)
        self._clx_outer_ids = _clx["outer_ids"]
        self._clx_walk_ids = _clx["walk_ids"]
        # STRING first-match SEARCH closure (`_lemma_calls_trusted`): the `hit=[""]`
        # string-accumulator sibling of the bool `found=[False]` closure. Same
        # OUTER+lifted-`walk` adjacency pairing; the wrapper emits a certified
        # first-match search catamorphism (`option string`, `map string bool`
        # set param membership), the lifted `walk` is SUPPRESSED. Keyed on `id`.
        # Corpus-inert (self-annotate-mirror-only). See generic_fold.py note.
        from module6_whyml.generic_fold import recognize_lemma_string_search_pairs
        _lss = recognize_lemma_string_search_pairs(functions)
        self._lss_outer_ids = _lss["outer_ids"]
        self._lss_walk_ids = _lss["walk_ids"]
        # `_func_returns_string_seq` (generic_fold.py boundary-A): the svt-guarded
        # `found=[False]` nested-`def rec` closure existence walk (Return-of-string-
        # typed-Var). Same OUTER+lifted-`rec` adjacency pairing as closure_existence,
        # but its own recognizer (5-stmt svt-guarded outer + a nested computed-key
        # `svt.get(v.get("name"))=="string"` leaf that INSPECTS svt's value). The
        # wrapper emits a mutual pyval/pydict/list existence catamorphism with `svt`
        # threaded UNCHANGED as a non-variant pydict param; the lifted `rec` is
        # SUPPRESSED. Keyed on `id`; corpus-inert (self-annotate-mirror-only).
        from module6_whyml.generic_fold import recognize_func_returns_string_seq_pairs
        _frss = recognize_func_returns_string_seq_pairs(functions)
        self._frss_outer_ids = _frss["outer_ids"]
        self._frss_walk_ids = _frss["walk_ids"]
        # `_returns_string_seq` (generic_fold.py): the SELF-STATE sibling of
        # `_func_returns_string_seq` (FunctionEmissionMixin instance method). Same
        # OUTER+lifted-`rec` adjacency pairing + shared walk grammar, but `svt` is sourced
        # from the self field `getattr(self,"_seq_value_types",{})` (opaque-but-real
        # `val <n>__svt (self):pydict`, REALLY read) and the walk is seeded with the PARAM
        # `body_stmts` directly. The lifted `rec` is SUPPRESSED. Keyed on `id`;
        # corpus-inert (self-annotate-mirror-only).
        from module6_whyml.generic_fold import recognize_returns_string_seq_pairs
        _rss = recognize_returns_string_seq_pairs(functions)
        self._rss_outer_ids = _rss["outer_ids"]
        self._rss_walk_ids = _rss["walk_ids"]
        # `_class_inv_refs_axiom_func` (generic_fold.py): the nonlocal-scalar-`hit` twin of
        # `_func_returns_string_seq`. Same OUTER+lifted-`_walk` adjacency pairing, but the
        # accumulator is a SCALAR `hit` (lowered to `||` short-circuit) and the leaf is a
        # `Map.get`-membership `node.get("func") in _axiom_logic_funcs` (opaque-but-real
        # self-source `val <n>__axset (self):map string bool`). The REAL type_decls->
        # class_invariants spine is walked. The lifted `_walk` is SUPPRESSED. Keyed on `id`;
        # corpus-inert (self-annotate-mirror-only).
        from module6_whyml.generic_fold import recognize_class_inv_refs_axiom_pairs
        _cira = recognize_class_inv_refs_axiom_pairs(functions)
        self._cira_outer_ids = _cira["outer_ids"]
        self._cira_walk_ids = _cira["walk_ids"]
        # `_inductive_refs_global_or_axiom_func` (generic_fold.py): the globals-set EXTENSION
        # of `_class_inv_refs_axiom_func`. Same nonlocal-scalar-`hit` walk, but an 8-stmt
        # outer that also builds `globals_names` from `ir["module_globals"]`, a 3-disjunct
        # leaf (axiom-fn membership + Var-name/object-name membership in globals_names), and a
        # triple-loop seed. `axset` stays opaque-but-real; `gset` is REALLY built from
        # `module_globals`. The lifted `_walk` is SUPPRESSED. Keyed on `id`; corpus-inert.
        from module6_whyml.generic_fold import recognize_inductive_refs_pairs
        _iroaf = recognize_inductive_refs_pairs(functions)
        self._iroaf_outer_ids = _iroaf["outer_ids"]
        self._iroaf_walk_ids = _iroaf["walk_ids"]
        # `_build_method_*_ensures_map` cluster (generic_fold.py): the map-valued propagation
        # maps whose nested `def result_only/classify/saw/refs_self_field_or_old` Module5
        # hoists to `<class>__<nested>` siblings (the two `classify` defs collide on ONE name).
        # The group-emit is self-contained, so every lifted sibling is SUPPRESSED. Keyed on
        # `id`; corpus-inert (self-annotate-mirror-only).
        from module6_whyml.generic_fold import recognize_build_method_ensures_map_pairs
        _bmem = recognize_build_method_ensures_map_pairs(functions)
        self._bmem_outer_ids = _bmem["outer_ids"]
        self._bmem_walk_ids = _bmem["walk_ids"]
        # `_collect_struct_pack_assign_targets` (generic_fold.py boundary-A SET-COLLECT):
        # the self-free `Set[str]` collector of `X = struct.pack(fmt, …)` assign targets —
        # same OUTER+lifted-`_scan` adjacency pairing, ref-accumulator `map string bool`.
        # The REAL `struct.pack` func + `target` are read off the pydict; only
        # `parse_format(fmt)!=None` is opaque. The lifted `_scan` is SUPPRESSED. Keyed on
        # `id`; corpus-inert (self-annotate-mirror-only; sole caller `_emit_body_code` is
        # `\trusted`, so the returned set never crosses into a converted caller).
        from module6_whyml.generic_fold import recognize_struct_pack_targets_pairs
        _spat = recognize_struct_pack_targets_pairs(functions)
        self._spat_outer_ids = _spat["outer_ids"]
        self._spat_walk_ids = _spat["walk_ids"]
        # `_collect_struct_unpack_array_targets` (generic_fold.py boundary-A SET-COLLECT):
        # the TUPLE-UNPACK twin of the pack collector — same OUTER+lifted-`_scan` adjacency
        # pairing, ref-accumulator `map string bool` with an index-threaded per-slot
        # set-fold over the REAL `targets` spine (BOTH branches reflected; only the per-slot
        # `array int` decision is opaque). The lifted `_scan` is SUPPRESSED. Keyed on `id`;
        # corpus-inert (self-annotate-mirror-only; sole callers are `\trusted` stubs).
        from module6_whyml.generic_fold import recognize_struct_unpack_targets_pairs
        _suat = recognize_struct_unpack_targets_pairs(functions)
        self._suat_outer_ids = _suat["outer_ids"]
        self._suat_walk_ids = _suat["walk_ids"]
        # `_contract_referenced_names` (generic_fold.py boundary-A SET-COLLECT): the
        # `Set[str]` sibling of `_func_returns_string_seq` — same OUTER+lifted-`_walk`
        # adjacency pairing, but the accumulator is a returned `map string bool` folded
        # with `set_union` (the leaf set_adds the real `node["func"]` string). The lifted
        # `_walk` is SUPPRESSED. Keyed on `id`; corpus-inert (self-annotate-mirror-only).
        from module6_whyml.generic_fold import recognize_contract_referenced_names_pairs
        _crn = recognize_contract_referenced_names_pairs(functions)
        self._crn_outer_ids = _crn["outer_ids"]
        self._crn_walk_ids = _crn["walk_ids"]
        # `_collect_field_decode_str_locals` (generic_fold.py Module5 lambda-lift
        # capture-threading SET-COLLECT): the field-decode-idiom local collector — same
        # OUTER+lifted-`rec` adjacency pairing + `set_union` skeleton as
        # `_contract_referenced_names`, but the nested `def rec` captures a mutable `out`
        # (re-expressed as the returned `map string bool`, NOT a by-ref effect) + the
        # immutable `self` (idiom self-call modeled OPAQUE). The lifted `rec` keeps its own
        # `\trusted` marker (bodyless `val`, unused) — the outer's group-emit is
        # self-contained. Keyed on `id`; corpus-inert (name-gated; sole caller
        # `_typed_local_vars` is `\trusted`).
        from module6_whyml.generic_fold import recognize_field_decode_str_locals_pairs
        _fdsl = recognize_field_decode_str_locals_pairs(functions)
        self._fdsl_outer_ids = _fdsl["outer_ids"]
        self._fdsl_walk_ids = _fdsl["walk_ids"]
        # `_collect_string_elem_read_locals` (generic_fold.py TWO-SEQUENTIAL-CATAMORPHISM
        # SET-COLLECT): same OUTER+lifted-`rec` adjacency pairing, but the walk carries a
        # CROSS-ACCUMULATOR dependency between two sets (`str_arrays` feeds `elem_reads`'s
        # membership test). Lowered to two sequential total `set_union` folds over the SAME
        # `map string bool` repr; the outer composes `= f2 body (f1 body)`. The lifted `rec`
        # is SUPPRESSED. Keyed on `id`; corpus-inert (name-gated).
        from module6_whyml.generic_fold import recognize_string_elem_read_locals_pairs
        _serl = recognize_string_elem_read_locals_pairs(functions)
        self._serl_outer_ids = _serl["outer_ids"]
        self._serl_walk_ids = _serl["walk_ids"]
        # `_callee_raised_direct` (generic_fold.py raises-registry SET-COLLECT): the raises-
        # registry sibling of `_contract_referenced_names` — same OUTER+lifted-`walk`
        # adjacency pairing + `set_union` skeleton, but the Call leaf looks the real `func`
        # up in the opaque-but-real self-source `_module_func_raises` registry val (`__mfr`,
        # ensures-free) and unions each real clause dict's real `exc_type` string. The lifted
        # `walk` is SUPPRESSED. Keyed on `id`; corpus-inert (self-annotate-mirror-only).
        from module6_whyml.generic_fold import recognize_callee_raised_direct_pairs
        _crd = recognize_callee_raised_direct_pairs(functions)
        self._crd_outer_ids = _crd["outer_ids"]
        self._crd_walk_ids = _crd["walk_ids"]
        # `_contract_referenced_var_names` (generic_fold.py boundary-A SET-COLLECT): the
        # bare-variable-NAME sibling of `_contract_referenced_names` — same OUTER+lifted-
        # `_walk` adjacency pairing + `set_union` skeleton, EXTENDED with a third folded
        # contract list (`assigns`) and a two-arm leaf (`Var`->`node["name"]`; `Attribute`
        # -> the nested `node["object"]`'s `["name"]`). The lifted `_walk` is SUPPRESSED.
        # Keyed on `id`; corpus-inert (self-annotate-mirror-only).
        from module6_whyml.generic_fold import \
            recognize_contract_referenced_var_names_pairs
        _crvn = recognize_contract_referenced_var_names_pairs(functions)
        self._crvn_outer_ids = _crvn["outer_ids"]
        self._crvn_walk_ids = _crvn["walk_ids"]
        # `_collect_map_typed_locals` (auto_trust.py, boundary-A SET-COLLECT): the
        # map-typed-local pre-pass — same OUTER+lifted-`walk` adjacency pairing as
        # `_collect_struct_pack_assign_targets`, but the leaf gate is `tgt and
        # _rhs_yields_map(value)` and the accumulator is a returned `map string bool`.
        # The lifted `walk` is SUPPRESSED. Keyed on `id`; corpus-inert (mirror-only).
        from module6_whyml.generic_fold import recognize_collect_map_typed_locals_pairs
        _cmtl = recognize_collect_map_typed_locals_pairs(functions)
        self._cmtl_outer_ids = _cmtl["outer_ids"]
        self._cmtl_walk_ids = _cmtl["walk_ids"]
        # `_has_set_op_on_map` (auto_trust.py): the recursive bool-existence predicate
        # over pyval — same OUTER+lifted-`yields_map` adjacency pairing; the flag-branches
        # test the real `left`/`right`/`iter` node with real `map_locals` membership. The
        # lifted `yields_map` is SUPPRESSED. Keyed on `id`; corpus-inert (mirror-only).
        from module6_whyml.generic_fold import recognize_has_set_op_on_map_pairs
        _hsom = recognize_has_set_op_on_map_pairs(functions)
        self._hsom_outer_ids = _hsom["outer_ids"]
        self._hsom_walk_ids = _hsom["walk_ids"]
        # `_is_linear_expr` (auto_trust.py): the nested `def _check(e)` linear-arith
        # classifier + its `return _check(expr)` staticmethod wrapper — OUTER+lifted-`_check`
        # adjacency pairing. The wrapper emits ONE recursive bool catamorphism over pyval
        # (every discriminant reflected from the real body); the lifted `_check` is
        # SUPPRESSED. Keyed on `id`; corpus-inert (self-annotate-mirror-only).
        from module6_whyml.generic_fold import recognize_is_linear_expr_pairs
        _ile = recognize_is_linear_expr_pairs(functions)
        self._ile_outer_ids = _ile["outer_ids"]
        self._ile_walk_ids = _ile["walk_ids"]
        # `_extract_array_lengths` (auto_trust.py): OUTER for-loop over `invs` paired with
        # its two lifted closures `_field_of`/`_int_of` (i+1, i+2). Builds
        # `map string (option int)` via a pinned `__setdefault` + faithful readers. The
        # lifted closures are SUPPRESSED. Keyed on `id`; corpus-inert (mirror-only).
        from module6_whyml.generic_fold import recognize_extract_array_lengths_pairs
        _eal = recognize_extract_array_lengths_pairs(functions)
        self._eal_outer_ids = _eal["outer_ids"]
        self._eal_walk_ids = _eal["walk_ids"]
        # MULTI-GUARD CASCADE `_check_*` caller (check-diverges-noreturn-impl.md):
        # the set of single-arg closure-existence-converted `list pyval -> bool`
        # predicate NAMES (`_body_has_diverging_construct`). A cascade guard that
        # calls one of these on the body list is emitted as a real predicate call;
        # a guard referencing an unconverted / differently-typed predicate keeps
        # the caller `\trusted` (fail-closed). Single-arg only (no extra params).
        self._clx_pred_names = {
            d["name"] for d in self._clx_outer_ids.values()
            if not d.get("extra_params")}
        # LEMMA-SOUNDNESS `_check_lemma` caller (lemma-soundness-impl.md): the set
        # of converted string-search predicate NAMES (`_lemma_calls_trusted`,
        # `list pyval -> map string bool -> string`). `_check_lemma` threads its
        # `trusted_funcs` set PARAM into one of these; a call to an unconverted /
        # differently-typed predicate keeps the caller `\trusted` (fail-closed).
        self._lss_pred_names = {
            d["name"] for d in self._lss_outer_ids.values()}
        # CHECK-SUBSCRIPT-ASSIGNMENTS caller (driver target #2): a body-only
        # caller running TWO `_sa_walk`-family walks with an annotation gate. It
        # is a forward reference to BOTH walkers, so it is DEFERRED until both
        # walker groups are emitted (tracked in `_emitted_walker_names`).
        from module6_whyml.generic_fold import (
            recognize_check_subscript_assignments, recognize_check_contract_scope)
        self._csa_funcs = [
            (f, recognize_check_subscript_assignments(f)) for f in functions
            if recognize_check_subscript_assignments(f) is not None]
        self._csa_names = {f.get("name") for f, _ in self._csa_funcs}
        self._csa_emitted = set()
        self._emitted_walker_names = set()
        # CHECK-CONTRACT-SCOPE caller (driver target #3): the per-key
        # `allow_result` scope check — a forward reference to `_cs_clause`/
        # `_cs_body`, DEFERRED to just after the `_cs_clause` group + cs-trio
        # (same append plumbing as `_check_contract_exprs` after the pb-trio).
        self._ccs_funcs = [
            (f, recognize_check_contract_scope(f)) for f in functions
            if recognize_check_contract_scope(f) is not None]
        self._ccs_names = {f.get("name") for f, _ in self._ccs_funcs}
        self._ccs_emitted = False
        self._term_adt_spec = compute_term_adt_spec(
            functions, self.ir.get("type_decls", []))
        # class-variant-impl.md T-transform: the Term->Term (constructor-rebuild)
        # transforms need the str->str module constants (op-swap maps) + the
        # abstract `val pystr_eq` string guard. Stash both; a transform sets
        # needs_term exactly like a bool fold.
        self._term_const_dicts = self.ir.get("module_const_dicts") or {}
        # class-variant-impl.md T-string: the term->string BUILD catamorphism
        # (`_pp`) needs the str->int module const dicts (`_BINOP_PREC` precedence
        # table) + the module int constants (`_PREC_*`) + `val pystr_eq`.
        self._term_const_int_dicts = self.ir.get("module_const_int_dicts") or {}
        _mc = self.ir.get("module_constants") or {}
        _term_transforms = [
            recognize_term_isinstance_transform(
                f, self._term_adt_spec, self._term_const_dicts)
            for f in functions] if self._term_adt_spec else []
        _term_pps = [
            recognize_term_string_pp(
                f, self._term_adt_spec, _mc, self._term_const_int_dicts)
            for f in functions] if self._term_adt_spec else []
        self._term_pp_names = {
            f["name"] for f, d in zip(functions, _term_pps) if d is not None}
        self._term_pp_mc = _mc
        needs_term_streq = any(
            d is not None and d.get("uses_streq") for d in _term_transforms) \
            or any(d is not None and (d.get("uses_streq") or d.get("binop_dicts"))
                   for d in _term_pps)
        # T-string: the pp catamorphism BUILDS a string -> it needs `str_concat_op`
        # (string concat) + `str_of_int` (IntLit `str()`). Gate their declaration
        # in the term theory (emit_why3.py's other functions don't pull them).
        needs_term_strbuild = any(d is not None for d in _term_pps)
        # class-variant-impl.md §OUTCOME-TS RESIDUAL: the RECORD⇄VARIANT BRIDGE
        # for the 5 ir.py per-class `.pp` METHODS. The family is recognized as a
        # WHOLE (every ctor's pp body parses into a string-build arm), synthesizing
        # a unified `pp_term : term -> string`. Sets needs_term (same certified
        # inductive) + the ctor-class set the record-field-type override consults.
        # `pp_term` uses the leaf pp methods' existing abstract `val`s
        # (str_concat_op/str_of_int) which sit after `type term` -> no strbuild flag.
        self._term_pp_family = recognize_term_pp_methods(
            functions, self._term_adt_spec)
        self._term_pp_method_classes = (
            set(self._term_pp_family["classes"]) if self._term_pp_family else set())
        # the record-field-type override applies ONLY to classes whose pp method is
        # CONVERTED (delegates) in THIS file -> a file that imports the pp methods as
        # `\trusted` vals keeps its records byte-identical.
        self._term_pp_convert_classes = (
            set(self._term_pp_family["convert_classes"])
            if self._term_pp_family else set())
        # `pp_term` is emitted ONCE (before the first per-class delegation); the
        # flag resets here per file.
        self._pp_term_emitted = False
        # class-variant-impl.md §OUTCOME-TL: the T-set/list LEAF algebras
        # (`mk_arrow_chain` list-fold builder, `flatten_arrow_chain` while-spine
        # tuple return) also set needs_term — same certified `term` inductive.
        needs_term = bool(self._term_adt_spec) and (any(
            recognize_term_isinstance_fold(f, self._term_adt_spec) is not None
            for f in functions) or any(d is not None for d in _term_transforms)
            or any(recognize_term_list_build(f, self._term_adt_spec) is not None
                   for f in functions)
            or any(recognize_term_flatten_arrow(f, self._term_adt_spec) is not None
                   for f in functions)
            or any(recognize_term_free_vars(f, self._term_adt_spec) is not None
                   for f in functions)
            or any(d is not None for d in _term_pps)
            or self._term_pp_family is not None)
        # §OUTCOME-TL: the `free_vars` set-fold needs `use bool.Bool` (orb/andb/notb
        # in `set_union`/`set_diff`). Gate it narrowly so needs_term files WITHOUT a
        # set-fold (emit_why3.py, canonical.py) stay byte-identical.
        _term_setfolds = [recognize_term_free_vars(f, self._term_adt_spec)
                          for f in functions] if self._term_adt_spec else []
        needs_term_setfold = any(
            d is not None and (d.get("uses_union") or d.get("uses_diff"))
            for d in _term_setfolds)
        if not needs_term:
            self._term_adt_spec = None
            self._term_const_dicts = {}
            self._term_const_int_dicts = {}
            self._term_pp_names = set()
            self._term_pp_family = None
            self._term_pp_method_classes = set()
            self._term_pp_convert_classes = set()
            needs_term_streq = False
            needs_term_setfold = False
            needs_term_strbuild = False
        self._needs_term_streq = needs_term_streq
        self._needs_term_strbuild = needs_term_strbuild
        # A frozen-dataclass term ctor with a `tuple` field emits an `array int`
        # RECORD field (`type app = { args: array int }`), which requires
        # `use array.Array`. Pull it when the term carrier is active and any ctor
        # dataclass has a tuple field. Gated on needs_term -> corpus (no term ADT)
        # byte-identical; the term mirrors already pull Array via other conditions.
        if needs_term and self._term_adt_spec:
            _ctors = set(self._term_adt_spec.get("ctors", {}))
            for _td in self.ir.get("type_decls", []):
                if _td.get("name") in _ctors and any(
                        f.get("type") == "tuple" for f in _td.get("fields", [])):
                    needs_array = True
                    break
        # crosscheck_ir.py self-state carrier (class-variant-impl.md §OUTCOME-CC):
        # a record field of value_type "opaque_term" (Module5 allow-list) gates
        # the self-state boolean recognizer + `val pystr_eq`. Corpus/other-mirror
        # never carry this value_type -> byte-inert everywhere else.
        from module6_whyml.generic_fold import (
            recognize_crosscheck_selfstate_bool, _uses_str_empty,
            recognize_crosscheck_term_method)
        self._has_opaque_term_fields = any(
            f.get("value_type") == "opaque_term"
            for td in self.ir.get("type_decls", [])
            if td.get("kind") == "record"
            for f in td.get("fields", []))
        needs_selfstate_streq = self._has_opaque_term_fields and any(
            recognize_crosscheck_selfstate_bool(f) is not None
            and _uses_str_empty(recognize_crosscheck_selfstate_bool(f)["expr"])
            for f in functions)
        # class-variant-impl.md §F4: a CONVERTED term-structural crosscheck
        # method that compares terms (`provers_agree`/`all_agree`, `==` on Term)
        # needs the DEFINED structural `term_eq`/`term_list_eq`/`strlist_eq`
        # emitted in the `term` theory. Gated on the recognizer matching (a still-
        # `\trusted` stub body `return False` never matches) AND the term spec
        # being present -> term_eq emits ONLY once an eq-method is converted;
        # corpus/other-mirror byte-inert (no opaque_term fields there).
        needs_term_eq = bool(
            self._has_opaque_term_fields and self._term_adt_spec and any(
                (recognize_crosscheck_term_method(f) or {}).get("uses_term_eq")
                for f in functions))
        self._needs_term_eq = needs_term_eq
        return {
            "needs_pydict": needs_pydict,
            "needs_term": needs_term,
            "needs_term_streq": needs_term_streq,
            "needs_term_setfold": needs_term_setfold,
            "needs_term_strbuild": needs_term_strbuild,
            "needs_selfstate_streq": needs_selfstate_streq,
            "needs_term_eq": needs_term_eq,
            "needs_sdict": needs_sdict,
            "needs_pdict_bridge": needs_pdict_bridge,
            "needs_pput": needs_pput,
            "needs_void_dispatch": needs_void_dispatch,
            "needs_array": needs_array,
            "needs_matrix": needs_matrix,
            "needs_minmax": needs_minmax,
            "needs_continue": needs_continue,
            "needs_break": needs_break,
            "needs_return_exc": needs_return_exc,
            "needs_return_seq": needs_return_seq,
            "needs_return_seq_str": needs_return_seq_str,
            "needs_return_str": needs_return_str,
            "needs_return_emit_ir": needs_return_emit_ir,
            "needs_return_void": needs_return_void,
            "needs_body_dict": needs_body_dict,
            "tuple_return_arities": tuple_return_arities,
            "union_return_types": union_return_types,
            "needs_string": needs_string,
            "needs_char": needs_char,
            "needs_real": needs_real,
            "needs_fromint": needs_truediv,
            "needs_seq": needs_seq,
            "needs_map_ghost": needs_map_ghost,
            "needs_ghost_dict": needs_ghost_dict,
            "needs_option_record": needs_option_record,
            "needs_list_ghost": needs_list_ghost,
            "needs_sum": needs_sum,
            "needs_set_card": needs_set_card,
            "needs_divmod": needs_divmod,
            "needs_no_exception": needs_no_exception,
            "bounded_sizes": bounded_sizes,
            "user_exceptions": user_exceptions,
            # compound-key const-map lowering: a tuple-keyed const dict needs
            # `map.Map` + `option.Option` + `list.List` in scope for its opaque
            # `val constant` and the defaulting `Map.get`/`Nil` at the getter site.
            "needs_compound_const_map": bool(
                self.ir.get("module_const_compound_dicts")),
        }

    def _emit_preamble_uses(self, needs: Dict[str, Any],
                            module_name: str = "PyCSL_Program") -> List[str]:
        """Phase A: emit module header and `use` declarations for libraries.

        `module_name` defaults to `PyCSL_Program` (the flat single-module path, byte-
        identical). The `_transpile_modular` path passes the per-module name so each
        emitted top-level `module <name>` gets the SAME shared infrastructure `use`s."""
        out = [
            f"module {module_name}",
            "  use int.Int",
            "  use int.EuclideanDivision",
            "  use ref.Ref",
        ]
        sorted_bsz = sorted(needs["bounded_sizes"])
        n = len(sorted_bsz)
        i = 0
        while i < n:
            out.append(f"  use mach.int.Int{sorted_bsz[i]}")
            i += 1
        if needs["needs_string"]:
            out.append("  use string.String")
        if needs.get("needs_char"):
            # 10-2300-spec-5: the char<->int bridge (ord/chr). `string.Char` is a
            # sibling module in the SAME trusted `string.mlw` as `string.String`; it
            # provides `code`/`chr`/`get`/`.contents` and the round-trip axioms
            # `chr_code`/`code_chr` — no PyCSL-owned axiom, no TCB growth beyond the use.
            out.append("  use string.Char")
        if needs.get("needs_real"):
            out.append("  use real.RealInfix")  # no-more-int Stage D — `+.`/`-.`/… on real
        if needs.get("needs_fromint"):
            # WL-02: `from_int : int -> real` lifts int operands of a Python TRUE-division
            # `/` into the reals before `/.`. Only emitted when a `/` is present, so
            # float-only programs (no `/` on ints) stay byte-identical.
            out.append("  use real.FromInt")
        if needs.get("needs_seq"):
            out.append("  use seq.Seq")  # no-more-int-7 §B′ — immutable list-snapshot value model
        if self._uses_pyconst_val():
            # pyconst_val value-variant ADT (self-tcb-reduction M5, B-bucket): the
            # `_py_expr_constant` complex branch truncates the real part of a PVComplex
            # `.value` — `int(expr.value.real)` -> `(real_trunc (pvreal_of expr.value))`,
            # where `real_trunc`'s spec is pinned to `truncate : real -> int` (`real.Truncate`).
            # GATED TIGHTLY on a Constant/`pyconst_val` field actually being present (only the
            # Module5 mirror harvests one) — NOT on the broad emit_ir-theory condition — so the
            # real-arithmetic axioms of `real.Truncate` are NOT injected into the SMT context of
            # every other full-theory mirror (that bloats their vacuity/proof search). A corpus
            # file (no pyconst_val field) never sees this use -> byte-identical.
            out.append("  use real.Truncate")
        if self._value_semantic:
            if needs["needs_matrix"]:
                out.append("  use matrix.Matrix")
            if needs["needs_minmax"]:
                out.append("  use int.MinMax")
            # self-field-dict-reflection (typed-ir §12): a record with a `dict`/`set`
            # FIELD (`map …`) needs `map.Map`/`map.Const` even if no body dict is used —
            # e.g. a @mutable_state emitter whose only map is `self.<field>`. Corpus
            # records with map fields already use a body dict → byte-identical.
            _record_has_map = any(
                f.get("type") in ("set", "dict", "frozenset")
                for td in self.ir.get("type_decls", [])
                for f in td.get("fields", []))
            if needs["needs_map_ghost"] or needs.get("needs_body_dict") or _record_has_map:
                out.append("  use map.Map")
                out.append("  use map.Const")
            if (needs["needs_ghost_dict"] or needs.get("needs_body_dict")
                    or _record_has_map or needs.get("needs_option_record")
                    or getattr(self, "_has_opaque_term_fields", False)):
                # Body-level Python dicts are modelled as
                # `ref (map int (option int))` (parallel to ghost dicts);
                # `None` marks absent keys. self-field-dict-reflection (§12): a record
                # `map …` field also needs `option`. option-of-record projection
                # (boundary-1 G1 extension): an `Optional[<record>]` param is
                # `option <record>` → needs `option.Option` too.
                out.append("  use option.Option")
            # `array.Array` MUST be imported AFTER `map.Map` — both
            # provide a `([])` operator, and when both are in scope the
            # later import wins. With map.Map imported last, `arr[i]` on
            # an `array int` is mis-resolved to `Map.get`, producing
            # "expected 'mu -> 'mu1, got array int @rho" type errors.
            # See ConcurrencyChecker (which combines body-set ops with
            # array-typed function parameters).
            if needs["needs_array"]:
                out.append("  use array.Array")
            if needs["needs_list_ghost"]:
                out.append("  use list.List")
                out.append("  use list.Length")
                out.append("  use list.NthNoOpt")
                out.append("  use list.Mem")
                out.append("  use list.Append")
            elif needs.get("needs_void_dispatch"):
                # G-void-dispatch-thin needs ONLY the bare `list.List` Cons/Nil
                # ADT (structural `variant { stmts }` recursion) — Length/
                # NthNoOpt/Mem/Append are unused axiom baggage that measurably
                # perturbed an unrelated pre-existing lemma's solver timing in
                # this file (`wf_ir_binds`, `_emit_pydict_theory`) when
                # included; omitting them restored it to Valid.
                out.append("  use list.List")
        else:
            out.append("  use map.Map")
            if needs["needs_list_ghost"]:
                out.append("  use list.List")
                out.append("  use list.Length")
                out.append("  use list.NthNoOpt")
                out.append("  use list.Mem")
                out.append("  use list.Append")
            elif needs.get("needs_void_dispatch"):
                out.append("  use list.List")
            if needs["needs_minmax"]:
                out.append("  use int.MinMax")
            out.append("")
            out.append("  type loc = int")
            out.append("  constant max_addr : int = 1073741824")
            hv = self._heap_var
            out.append(f"  val ghost {hv} : ref (map loc int)")
            out.append("")
            out.append(f"  predicate valid (m: map loc int) (base: loc) (n: int) =")
            out.append(f"    n >= 0 /\\ base >= 0 /\\ base + n <= max_addr")
            out.append("")
            out.append(f"  predicate separated (a: loc) (na: int) (b: loc) (nb: int) =")
            out.append(f"    a + na <= b \\/ b + nb <= a")
            out.append("")
        if needs.get("needs_compound_const_map"):
            # compound-key const-map lowering: ensure map.Map / option.Option /
            # list.List are in scope for the opaque `val constant` map and the
            # defaulting `Map.get … Nil` getter. Guarded appends keep the file
            # byte-identical for the corpus (the flag is never set there).
            for _u in ("  use map.Map", "  use option.Option", "  use list.List"):
                if _u not in out:
                    out.append(_u)
        if needs.get("needs_pydict"):
            # WALL-PLAN v2: the concrete-map pyval/pydict/doc theory
            # (`_emit_pydict_theory`) needs list/option/string; the A-unit
            # accumulator model (`set_add`/`ref (map string bool)`) needs map.Map +
            # map.Const. Emit any not already `use`d above. Gated + never set by the
            # reference corpus → byte-diff-0.
            for _u in ("  use list.List", "  use option.Option", "  use string.String",
                       "  use map.Map", "  use map.Const", "  use bool.Bool"):
                if _u not in out:
                    out.append(_u)
        if needs.get("needs_term"):
            # class-variant-impl.md: the `term` variant's constructors carry
            # `string` (Var/App/...), `list term` (App.args), `list string`
            # (Forall.binders) — need string.String + list.List in scope. Idempotent
            # guarded appends; a corpus file never sets `needs_term` -> byte-identical.
            for _u in ("  use string.String", "  use list.List"):
                if _u not in out:
                    out.append(_u)
        if needs.get("needs_term_setfold"):
            # §OUTCOME-TL: the `free_vars` set-of-strings result algebra
            # (`map string bool`) needs map.Map (get/set) + bool.Bool (orb/andb/notb
            # in the pointwise union/diff). Gated on a set-fold present -> needs_term
            # files WITHOUT one stay byte-identical.
            for _u in ("  use map.Map", "  use bool.Bool"):
                if _u not in out:
                    out.append(_u)
        if self._uses_pyval():
            # hval-value-model-wall (self-tcb-reduction, heterogeneous value model):
            # the `hval` sum + the `map string (option hval)` heterogeneous dict need
            # map.Map/map.Const (the empty base + Map.set/Map.get) and option.Option
            # (the `option hval` codomain) and string.String (the HStr carrier + the
            # native string keys). Idempotent guarded appends — a corpus file never sets
            # `_uses_pyval` (no `Dict[str, PyVal]` annotation) → byte-identical there.
            for _u in ("  use map.Map", "  use map.Const", "  use option.Option",
                       "  use string.String"):
                if _u not in out:
                    out.append(_u)
        return out

    def _emit_preamble_exceptions(self, needs: Dict[str, Any]) -> List[str]:
        """Phase B: emit exception type declarations."""
        out: List[str] = []
        if needs["needs_continue"]:
            out.append("")
            out.append("  exception PyCSL_Continue")
        if needs["needs_break"]:
            out.append("")
            out.append("  exception PyCSL_Break")
        if needs["needs_return_exc"]:
            out.append("")
            out.append("  exception Return int")
        if needs.get("needs_return_seq"):
            # return-arr.md: array-returning functions with early returns carry the value
            # through an IMMUTABLE seq (Why3 forbids a mutable array exception payload);
            # the catch materializes back to `array int`.
            out.append("")
            out.append("  exception Return_seq (Seq.seq int)")
        if needs.get("needs_return_seq_str"):
            # str-list-elements: a STRING-element list returns through this parallel
            # exception (the catch materializes the `seq string` to `array string`).
            out.append("")
            out.append("  exception Return_seq_str (Seq.seq string)")
        if needs.get("needs_return_str"):
            # 10-1732-gap Gap 1: a `string`-returning function with an early/in-loop
            # return carries an immutable `string` payload (parallel to Return_seq).
            out.append("")
            out.append("  exception Return_str string")
        if needs["needs_return_void"]:
            out.append("")
            out.append("  exception Return_void")
        for arity in sorted(needs.get("tuple_return_arities", set())):
            # Tuple returns: each arity gets its own exception carrying the
            # full tuple, avoiding the int-hash collapse the plain `Return int`
            # would force via `_coerce_to_int`.
            parts = ", ".join(["int"] * arity)
            out.append("")
            out.append(f"  exception Return_{arity} ({parts})")
        # NOTE (value-model incr5, primitive c): the `Return_<variant>` exceptions are NOT
        # declared here — they reference synthesized `_union_*` types that are emitted LATER by
        # `_emit_type_decls`, so they are emitted just AFTER it (see `_emit_union_return_exceptions`,
        # called from the transpiler right after `out += type_lines`).
        # Sanitize each user-exception name; collapse Python local-alias
        # imports (`from X import Y as _Y`) by deduping via set after
        # leading-underscore strip. See `safe_exc_name` in identifiers.py.
        sanitized_exc = sorted({safe_exc_name(n) for n in needs["user_exceptions"]})
        for exc in sanitized_exc:
            out.append(f"  exception {exc}")
        return out

    def _emit_union_return_exceptions(self, needs: Dict[str, Any],
                                      declared_types: Optional[Set[str]] = None) -> List[str]:
        """value-model campaign incr5 (primitive c): emit the `Return_<variant>` exceptions for
        synthesized-union (`Optional[X]`) return types that early-return. Emitted AFTER
        `_emit_type_decls` (the `_union_*` types must be in scope), so it is called from the
        transpiler right after the type declarations — NOT in `_emit_preamble_exceptions`. The
        name `Return_<type>` is kept identical in `_wrap_body_with_return_catch` (catch) and
        `_handle_return_stmt` (raise). Empty for a module with no early-returning union walker
        → byte-identical.

        A `union_return_types` entry names a synthesized `_union_*` type that MUST be in scope
        (declared by `_emit_type_decls`). When an IMPORTED trusted-stub function has an
        `Optional[X]` return annotation AND an early/in-loop return in its body, the scan
        (`preamble._collect_needs`) records its `_union_*` return type — but that type's
        `type_decl` was synthesized in the SOURCE module's IR and is NOT merged into the
        emitting module's `type_decls`, so it is never declared here. The stub itself emits as
        an abstract `val` with NO body, so no `raise Return_<ut>` / catch references the
        exception; emitting `exception Return_<ut> <ut>` for such an undeclared `ut` dangles an
        unbound type symbol and fails L3-tc for the WHOLE file. Skip any `ut` not in
        `declared_types` (the set `_emit_type_decls` actually declared). BYTE-INERT: a file that
        currently PASSES L3-tc cannot contain an undeclared `ut` in `union_return_types` (it
        would already fail on the unbound symbol), so no passing corpus emission changes; a
        genuinely body-verified local union walker has its `_union_*` type declared, so its
        `Return_<ut>` is still emitted unchanged."""
        out: List[str] = []
        for ut in sorted(needs.get("union_return_types", set())):
            if declared_types is not None and ut not in declared_types:
                continue
            out.append("")
            out.append(f"  exception Return_{ut} {ut}")
        return out

    def _emit_preamble_helpers(self, needs: Dict[str, Any]) -> List[str]:
        """Phase C: emit helper lemmas, pycsl_sum, pycsl_div, pycsl_mod function bodies."""
        out: List[str] = []
        # crosscheck_ir.py self-state carrier (class-variant-impl.md §OUTCOME-CC):
        # the string-empty test `not self.<strfield>` lowers to the abstract
        # `val pystr_eq` (result no VC constrains -> NOT an axiom, ledger 3; the
        # term-carrier precedent). Gated on the self-state recognizer; never
        # double-declared (pydict/term declare their own, and this file has
        # neither). Corpus/other-mirror byte-inert (needs_selfstate_streq False).
        if (needs.get("needs_selfstate_streq")
                and not needs.get("needs_pydict")
                and not needs.get("needs_term_streq")):
            out.append("")
            out.append("  (* crosscheck self-state string-empty guard"
                       " (result VC-free; ledger 3) *)")
            out.append("  val pystr_eq (a b: string) : bool")
        if needs.get("needs_list_ghost"):
            # axiom mem_head: base case of mem — makes \mem(x, \cons(x, l)) proofs tractable
            # without recursive unfolding. This is the head-match case of mem's definition,
            # so it is mathematically sound to assume it as an axiom.
            out.append("")
            out.append("  axiom mem_head : forall x: int, l: list int. mem x (Cons x l)")
        if needs["needs_sum"]:
            out.append("")
            out.append("  let rec function pycsl_sum (a: array int) (lo hi: int) : int")
            out.append("    requires { 0 <= lo }")
            out.append("    requires { hi <= Array.length a }")
            out.append("    variant { hi - lo }")
            out.append("  = if lo >= hi then 0 else a[lo] + pycsl_sum a (lo + 1) hi")
            out.append("")
            out.append("  let rec lemma pycsl_sum_snoc (a: array int) (lo hi: int) : unit")
            out.append("    requires { 0 <= lo <= hi <= Array.length a }")
            out.append("    variant { hi - lo }")
            out.append("    ensures { hi > lo -> pycsl_sum a lo hi = pycsl_sum a lo (hi - 1) + a[hi - 1] }")
            out.append("  = if lo < hi - 1 then pycsl_sum_snoc a (lo + 1) hi")
        if needs["needs_set_card"]:
            out.append("")
            out.append("  let rec function set_card (s: map int bool) (lo hi: int) : int")
            out.append("    requires { lo <= hi }")
            out.append("    variant { hi - lo }")
            out.append("  = if lo >= hi then 0")
            out.append("    else (if Map.get s lo then 1 else 0) + set_card s (lo + 1) hi")
            out.append("")
            out.append("  let rec lemma set_card_add_hi (s: map int bool) (lo hi: int) : unit")
            out.append("    requires { lo <= hi }")
            out.append("    variant { hi - lo }")
            out.append("    ensures { set_card (Map.set s hi true) lo (hi + 1) = set_card s lo hi + 1 }")
            out.append("  = if lo < hi then set_card_add_hi s (lo + 1) hi")
        if needs["needs_divmod"]:
            out.append("")
            # WL-01 FIX: Python `//` is FLOORED division (rounds toward -inf) and `%`
            # has the sign of the DIVISOR. Why3's int.EuclideanDivision `div`/`mod` use a
            # NON-NEGATIVE remainder, which AGREES with Python when y > 0 but DIVERGES
            # when y < 0 (e.g. (-7)//(-2): Euclidean 4, Python 3). We recover Python's
            # floored semantics by a sign-of-divisor correction: for a negative divisor
            # with a non-zero remainder, floordiv = div - 1 and floormod = mod + y. This
            # keeps the positive-divisor case byte-for-byte equal to Euclidean.
            if "ZeroDivisionError" in needs["user_exceptions"]:
                out.append("  let pycsl_div (x: int) (y: int) : int")
                out.append("    raises { ZeroDivisionError -> y = 0 }")
                out.append("    ensures { y <> 0 /\\ result = (if mod x y <> 0 && y < 0 then div x y - 1 else div x y) }")
                out.append("  = if y = 0 then raise ZeroDivisionError else (if mod x y <> 0 && y < 0 then div x y - 1 else div x y)")
                out.append("")
                out.append("  let pycsl_mod (x: int) (y: int) : int")
                out.append("    raises { ZeroDivisionError -> y = 0 }")
                out.append("    ensures { y <> 0 /\\ result = (if mod x y <> 0 && y < 0 then mod x y + y else mod x y) }")
                out.append("  = if y = 0 then raise ZeroDivisionError else (if mod x y <> 0 && y < 0 then mod x y + y else mod x y)")
            else:
                out.append("  let pycsl_div (x: int) (y: int) : int")
                out.append("    requires { [@expl:division by zero] y <> 0 }")
                out.append("    ensures { result = (if mod x y <> 0 && y < 0 then div x y - 1 else div x y) }")
                out.append("  = if mod x y <> 0 && y < 0 then div x y - 1 else div x y")
                out.append("")
                out.append("  let pycsl_mod (x: int) (y: int) : int")
                out.append("    requires { [@expl:modulo by zero] y <> 0 }")
                out.append("    ensures { result = (if mod x y <> 0 && y < 0 then mod x y + y else mod x y) }")
                out.append("  = if mod x y <> 0 && y < 0 then mod x y + y else mod x y")
        return out

    def _inductive_refs_global_or_axiom_func(self, ir: Dict[str, Any]) -> bool:
        """gap-9: True iff some `#@ inductive` rule applies an axiom-backing
        logic function (`_axiom_logic_funcs`) or references a module-global
        object (by name). Gates the axioms/globals-before-inductive reorder so
        only the os family triggers it (all other inductive files keep the
        historical emission order → byte-identical)."""
        inds = ir.get("inductive_decls", [])
        if not inds:
            return False
        axiom_fns = getattr(self, "_axiom_logic_funcs", set())
        globals_names = {g["name"] for g in ir.get("module_globals", [])}
        if not axiom_fns and not globals_names:
            return False

        hit = False

        def _walk(node: Any) -> None:
            nonlocal hit
            if hit:
                return
            if isinstance(node, dict):
                if node.get("type") == "Call" and node.get("func") in axiom_fns:
                    hit = True
                    return
                if node.get("type") == "Var" and node.get("name") in globals_names:
                    hit = True
                    return
                if isinstance(node.get("object"), str) and node["object"] in globals_names:
                    hit = True
                    return
                for v in node.values():
                    _walk(v)
            elif isinstance(node, list):
                for v in node:
                    _walk(v)

        for ind in inds:
            for m in [ind] + ind.get("members", []):
                for (_rname, clause_ir) in m.get("rules", []):
                    _walk(clause_ir)
        return hit

    def _class_inv_refs_axiom_func(self, ir: Dict[str, Any]) -> bool:
        """gap-12: True iff some `#@ class invariant` IR node applies an
        axiom-backing logic function (`_axiom_logic_funcs`, e.g. `slot_inode`/
        `slot_name`/`dir_lookup`). Gates the axiom-func-decls-before-record
        reorder (mirroring the gap-9 conditional reorder) so ONLY a module whose
        class invariant cites such a symbol triggers it; every existing corpus
        class invariant references only `\\length`/`self.disk[i]`/scalars, so the
        gate is False for the whole corpus and the type-decl emission stays
        byte-identical. Requires `_precompute_axiom_logic_funcs` to have run."""
        axiom_fns = getattr(self, "_axiom_logic_funcs", set())
        if not axiom_fns:
            return False

        hit = False

        def _walk(node: Any) -> None:
            nonlocal hit
            if hit:
                return
            if isinstance(node, dict):
                if node.get("type") == "Call" and node.get("func") in axiom_fns:
                    hit = True
                    return
                for v in node.values():
                    _walk(v)
            elif isinstance(node, list):
                for v in node:
                    _walk(v)

        for td in ir.get("type_decls", []):
            for inv in td.get("class_invariants", []):
                _walk(inv)
        return hit

    @staticmethod
    def _axiom_fn_prefix_match(qn: str, prefix: str) -> bool:
        """Whether cited qualname `qn` pulls the `_AXIOM_FUNCTIONS[prefix]` decls.

        A KEY ending in '.' is a NAMESPACE prefix (`UnixFs.Struct.i18.`,
        `UnixFs.Content.`) and matches any descendant qualname; any other key is a
        FULL lemma qualname and must match EXACTLY. This exactness is essential now
        that sibling faithful lemmas are textual prefixes of one another
        (`…round_trip_u16` ⊂ `…round_trip_u16u32`, `…round_trip_i32` ⊂
        `…round_trip_i32i32`): citing the multi-slot lemma must NOT drag in the
        single-slot val decls. Correct for every pre-existing entry (namespace keys
        already carry the trailing dot; exact-lemma keys are cited verbatim)."""
        if prefix.endswith("."):
            return qn.startswith(prefix)
        return qn == prefix

    def _precompute_axiom_logic_funcs(self, ir: Dict[str, Any]) -> None:
        """Populate `self._axiom_logic_funcs` — the NAMES of `val function FOO`
        / `function FOO` symbols declared by the `_AXIOM_FUNCTIONS` decls for
        the qualnames this module CITES (`#@ proof`).

        A contract call to one of these (e.g. `dir_lookup(self.disk, 5, name)`
        in `_dir_lookup`'s ensures, or `slot_inode(disk, 5, k)` inside the
        `name_present` inductive rule) must lower to the raw logic application
        `(FOO args)` bound to THIS registry symbol — NOT an arity-suffixed
        abstract `FOO_3` (a fresh, axiom-unconstrained symbol). That raw binding
        is what makes the cited axiom constrain the REAL scan — the risk-2
        load-bearing binding (see `_handle_call_expr`). Idempotent; safe to call
        before inductive emission AND again from `_emit_preamble_axioms`.
        """
        self._axiom_logic_funcs: Set[str] = set()
        # (a) qualnames this module CITES (`#@ proof`).
        seen: Set[str] = set()
        for func in ir.get("functions", []):
            for entry in func.get("proof", []):
                seen.add(entry["qualname"])

        def _names_of(decls: List[str]) -> Set[str]:
            out: Set[str] = set()
            for d in decls:
                parts = d.split()
                if len(parts) >= 3 and parts[0] == "val" and parts[1] == "function":
                    out.add(parts[2])
                elif len(parts) >= 2 and parts[0] == "function":
                    out.add(parts[1])
                # allocator-frame plan: an abstract `predicate FOO (args)` is a logic
                # symbol too (a Prop-valued axiom-function), e.g. `uniq`/
                # `inode_bytes_valid` referenced bare in a `#@ class invariant`. Without
                # this it would lower to an unbound arity-suffixed abstract op.
                elif len(parts) >= 2 and parts[0] == "predicate":
                    out.add(parts[1])
            return out

        cited_fn_names: Set[str] = set()
        for qn in sorted(seen):
            for prefix, fn_decls in self._AXIOM_FUNCTIONS.items():
                if self._axiom_fn_prefix_match(qn, prefix):
                    cited_fn_names |= _names_of(fn_decls)

        # (b) axiom-function names APPLIED by an `#@ inductive` rule, even when
        # the citation was stripped from injected trusted stubs (gap-9: the
        # importer drops the heavy UnixFs.Dir scan axiom but still emits the
        # `name_present` inductive, which references slot_inode/slot_name). Those
        # symbols must still bind to the registry `val function` (raw `(f args)`)
        # AND get their decls emitted (see `_inductive_referenced_axiom_decls`).
        all_fn_names: Set[str] = set()
        for fn_decls in self._AXIOM_FUNCTIONS.values():
            all_fn_names |= _names_of(fn_decls)
        ind_applied: Set[str] = set()

        def _walk(node: Any) -> None:
            if isinstance(node, dict):
                if node.get("type") == "Call" and node.get("func") in all_fn_names:
                    ind_applied.add(node["func"])
                for v in node.values():
                    _walk(v)
            elif isinstance(node, list):
                for v in node:
                    _walk(v)

        for ind in ir.get("inductive_decls", []):
            for m in [ind] + ind.get("members", []):
                for (_rname, clause_ir) in m.get("rules", []):
                    _walk(clause_ir)
        # Also any axiom-function NAME applied in a function's contract
        # (`_dir_lookup`'s `\result == dir_lookup(...)`, the syscalls'
        # `name_present(...)` arguments) — so `dir_lookup`/`slot_*` bind to the
        # registry symbol AND get declared even when the citation was stripped.
        for func in ir.get("functions", []):
            contracts = func.get("contracts", {}) or {}
            for key in ("requires", "ensures", "assigns"):
                _walk(contracts.get(key, []))

        # (c) gap-13: any axiom-function NAME applied in a `#@ class invariant`.
        # An IMPORTER that pulls in a class WITH such an invariant (e.g. a formal
        # test importing UnixInodeFileSystem) may cite NO Dir axiom and reference
        # the symbol ONLY in the inherited invariant — yet the invariant must
        # still lower to the raw bound `slot_inode disk 5 i` (NOT an arity-suffixed
        # abstract `slot_inode_3`, which is declared after the record and leaves
        # the invariant referencing an unbound symbol). Walk the invariants so the
        # symbol binds AND `_class_inv_refs_axiom_func` fires the decl/axiom hoist.
        for td in ir.get("type_decls", []):
            for inv in td.get("class_invariants", []):
                _walk(inv)

        self._axiom_logic_funcs = cited_fn_names | ind_applied

        # (d) TRANSITIVE closure over the class-invariant axioms that WILL be emitted.
        # `_emit_class_inv_axioms` emits a `_CLASS_INV_AXIOMS` axiom when its body mentions
        # an applied symbol (e.g. `uniq_intro`/`uniq_elim` are emitted because `uniq` is
        # applied in the inherited class invariant). But those axiom bodies ALSO reference
        # the backing `val function`s (`slot_inode`/`slot_name`) — which must be DECLARED
        # too, else the emitted axiom references an undeclared symbol. Without this an
        # importer (a formal test importing UnixInodeFileSystem) that applies only `uniq`
        # in the inherited invariant fails with `unbound function 'slot_inode'`. Iterate to
        # a fixpoint (plain substring match, consistent with `_emit_class_inv_axioms`).
        changed = True
        while changed:
            changed = False
            for qn in self._CLASS_INV_AXIOMS:
                body = self._AXIOM_REGISTRY.get(qn, "")
                if not any(fn in body for fn in self._axiom_logic_funcs):
                    continue
                for fn in all_fn_names:
                    if fn not in self._axiom_logic_funcs and fn in body:
                        self._axiom_logic_funcs.add(fn)
                        changed = True

    def _emit_class_inv_axioms(self, ir: Dict[str, Any]) -> List[str]:
        """gap-13: emit the class-invariant axioms (`_CLASS_INV_AXIOMS`) BEFORE the
        record type whose invariant applies the constrained symbols, so the
        establishment (`by`-witness) and per-method type-invariant VCs can see
        them (a Why3 `axiom` only constrains its symbols from its declaration
        onward). Only called when `_class_inv_refs_axiom_func` is True. Emits a
        class-inv axiom when its backing logic-function symbols are among the ones
        the invariant applies (`_axiom_logic_funcs`) — i.e. INDEPENDENT of whether
        THIS module cites it. This is what lets an IMPORTER that inherits the class
        invariant but cites no Dir axiom (e.g. a formal test importing
        UnixInodeFileSystem) still discharge the establishment VC via
        `empty_disk_slots_dead`. Records each in `self._class_inv_axioms_emitted`
        so the later `_emit_preamble_axioms` skips it (emitted exactly once). The
        backing `val function` decls are already emitted ahead of the record by
        `_emit_uncited_axiom_func_decls` (gap-12 Wall A), so no decls here."""
        applied = getattr(self, "_axiom_logic_funcs", set())
        out: List[str] = []
        emitted: Set[str] = set()
        for qn in sorted(self._CLASS_INV_AXIOMS):
            body = self._AXIOM_REGISTRY[qn]
            # The axiom is RELEVANT iff it constrains a symbol the invariant
            # applies (every `_CLASS_INV_AXIOMS` body mentions slot_inode/slot_name).
            if not any(fn in body for fn in applied):
                continue
            axiom_name = "pycsl_axiom_" + qn.replace(".", "_")
            provenance = ("definitional (conservative predicate definition; ZERO trust)"
                          if qn in self._DEFINITIONAL_AXIOMS
                          else "cross-validated Rocq + Lean")
            out.append(f"  (* {qn} — {provenance} *)")
            out.append(f"  axiom {axiom_name} : {body}")
            emitted.add(qn)
        if out:
            out.append("")
        self._class_inv_axioms_emitted = emitted
        return out

    def _emit_preamble_axioms(self, ir: Dict[str, Any]) -> List[str]:
        """Emit Why3 function decls + axioms for `#@ proof` cites.

        Scans every function in the program IR for `proof` entries.
        Dedups by qualname (Rocq + Lean cite the same target). Emits
        each axiom under a sanitized name `pycsl_axiom_<...>` and
        records the prover provenance in a Why3 comment.
        """
        # Record the axiom-block function/predicate decls ACTUALLY emitted for
        # this module, so the abstract-val dedup
        # (`_insert_abstract_val_block`) skips exactly those — not every entry
        # in `_AXIOM_FUNCTIONS`. A symbol like `permut` is declared here only
        # when its axiom is cited; a file that uses `\permutation` WITHOUT a
        # `#@ proof` still needs the abstract-ops declaration.
        # A decl already emitted EARLY (before an inductive block that references
        # it — `_emit_inductive_decls`) must not be re-declared here.
        already = set(getattr(self, "_axiom_emitted_decls", set()))
        # module-emission.md §2a — TRUSTED `verify_module`-tagged stub axiom suppression.
        # When a `#@ verify_module <G>` function is ALSO trusted on THIS gate path
        # (e.g. it is a `--fun`-filtered callee of a write helper, so `pycsl.py` marks
        # `f["trusted"]=True`), it is emitted as a bodyless trusted `val` carrying ONLY
        # its contract — its body is NOT proven here. Its cited `#@ proof` axioms exist
        # SOLELY to discharge that body's VC; consumers need only the trusted contract.
        # Leaving them in would co-reside the heavy read-family axioms
        # (field_to_str_round_trip / dir_scan_* / *_byte_decode) with the write goal
        # → the 9.4M-step Timeout. So we DROP a qualname iff it is cited ONLY by such
        # trusted+verify_module stubs (a qualname ALSO cited by a non-suppressed function
        # — e.g. the shared `slot_inode_nonneg` / `scan_reflects_present` — still emits
        # from that function's own cite). Net `\trusted` is UNCHANGED (the stub stays
        # the existing trusted boundary); only its supporting axioms leave this module's
        # SMT context. On the MODULAR path the tagged fn is NOT trusted (it is the
        # verify target whose body IS proven), so nothing is suppressed there. On the
        # default flat path with no trusted+verify_module fn this is a no-op (byte-id).
        kept_qualnames: Set[str] = set()
        for func in ir.get("functions", []):
            stub = bool(func.get("trusted")) and bool(func.get("verify_module"))
            if stub:
                continue  # its cited axioms exist only to prove its (unproven) body
            for entry in func.get("proof", []):
                kept_qualnames.add(entry["qualname"])
        # A qualname cited ONLY by a trusted+verify_module stub is dropped; one ALSO
        # cited by a non-suppressed function survives (it was added in the loop above).
        seen_qualnames: Set[str] = kept_qualnames
        if not seen_qualnames:
            return []

        # Pair each qualname with the registry entry; halt if any
        # unknown — failure is at transpile time.
        out: List[str] = []
        # Declare backing functions once each (e.g. `function gcd`).
        declared_fns: Set[str] = set(already)
        for qn in sorted(seen_qualnames):
            for prefix, fn_decls in self._AXIOM_FUNCTIONS.items():
                if self._axiom_fn_prefix_match(qn, prefix):
                    for fn_decl in fn_decls:
                        if fn_decl not in declared_fns:
                            out.append(f"  {fn_decl}")
                            declared_fns.add(fn_decl)
        self._axiom_emitted_decls = set(declared_fns)
        self._precompute_axiom_logic_funcs(ir)
        if declared_fns:
            out.append("")

        # gap-13: skip any class-invariant axiom already hoisted before the record
        # by `_emit_class_inv_axioms` (Why3 forbids re-declaring the same axiom).
        already_axioms = set(getattr(self, "_class_inv_axioms_emitted", set()))
        # Emit each axiom. Comment records the prover pairing.
        for qn in sorted(seen_qualnames):
            if qn in already_axioms:
                continue
            if qn not in self._AXIOM_REGISTRY:
                raise PyCSLIRError(
                    f"#@ proof {qn}: not in Module6 axiom registry. "
                    f"Either add the axiom body to _AXIOM_REGISTRY or run "
                    f"`proof2why3 emit` (when available — see "
                    f"docs/cross-validated-spec-sources.md)."
                )
            axiom_name = "pycsl_axiom_" + qn.replace(".", "_")
            body = self._AXIOM_REGISTRY[qn]
            # Provers cite this qualname — for the MVP we record both
            # under one cite. v1 emits the canonical-hash status from
            # the cross-check manifest.
            out.append(f"  (* {qn} — cross-validated Rocq + Lean *)")
            out.append(f"  axiom {axiom_name} : {body}")
        out.append("")
        return out

    def _emit_preamble_no_exception_predicates(self, needs: Dict[str, Any]) -> List[str]:
        """Phase D: emit the WhyML predicate library for `no_exception`.

        Only emitted when at least one function declares `no_exception`
        (per `needs_no_exception`). The predicate definitions come from
        `exception_model.PREDICATE_LIBRARY` — the single source of truth.
        """
        if not needs.get("needs_no_exception"):
            return []
        from exception_model import predicate_definitions
        out: List[str] = [""]
        for line in predicate_definitions():
            out.append(f"  {line}")
        return out

    def _term_pp_field_override(self, cls: Optional[str],
                                field: Optional[str]) -> Optional[str]:
        """class-variant-impl.md §OUTCOME-TS RESIDUAL (record⇄variant bridge, part a):
        for a term-ctor dataclass whose `.pp` family is recognized, override a
        RECURSIVE field's record type to the VARIANT field type (`term` / `list
        term` / `list string`) so the record→variant injection `pp_term (<Ctor>
        self.<f>...)` typechecks. Only the recursive/variant fields are overridden
        (scalar `string`/`int`/`bool` fields keep the emitter's default computation,
        so `boollit_value: int` etc stay byte-identical). Returns the WhyML type or
        None (no override). Gated on the pp family present (only ir.py) -> corpus +
        every other term mirror byte-identical."""
        classes = getattr(self, "_term_pp_convert_classes", None)
        spec = getattr(self, "_term_adt_spec", None)
        if not classes or not spec or cls not in classes:
            return None
        wt = dict(spec.get("ctors", {}).get(cls, [])).get(field)
        if wt in ("term", "list term", "list string"):
            return wt
        return None

    def _emit_term_theory(self, needs: Dict[str, Any]) -> List[str]:
        """class-variant-impl.md (driver-backlog item 3): emit the `term` VARIANT
        ADT (the proof2why3 `Term` union: Var|IntLit|BoolLit|App|BinOp|UnaryOp|
        Forall|Exists|Unsupported) — the class-instance-variant carrier for
        isinstance-dispatch + named-field reads. A `\trusted` walker
        (`contains_unsupported`) lowers onto a total positional `match` over this
        variant. The type is a plain inductive: constructors are DISTINCT +
        INJECTIVE (Why3 intrinsic), recursion (`App string (list term)`,
        `BinOp string term term`, ...) is structurally WELL-FOUNDED — co-landed
        AXIOM-FREE with the Rocq `Phase2i_TermIR.v` / Lean `TermIR.lean`
        certificate (ledger stays 3). Gated on `needs_term` -> the reference
        corpus (which never imports the proof2why3 Term ADT into a term-fold) and
        every other mirror emit byte-identical."""
        spec = getattr(self, "_term_adt_spec", None)
        if not needs.get("needs_term") or not spec:
            return []
        ctors = spec["ctors"]
        order = spec["order"]
        lines = [
            "  (* ==== class-variant-impl.md: the proof2why3 `Term` union as a Why3"
            " VARIANT (isinstance-dispatch + named-field carrier). Co-landed"
            " axiom-free with the Rocq/Lean TermIR certificate; ledger 3. Gated on"
            " `needs_term` -> corpus + every other mirror byte-identical. ==== *)",
            "  type term =",
        ]
        for c in order:
            tys = "".join(
                (" (" + wt + ")") if " " in wt else (" " + wt)
                for (_fn, wt) in ctors[c])
            lines.append(f"    | {c}{tys}")
        lines.append("")
        # class-variant-impl.md T-transform: a Term->Term const-map guard
        # (`if t.op in _MAP`) lowers to `pystr_eq` on the string field. It is an
        # abstract `val` whose result no VC constrains (contract is `ensures
        # True`) — NOT an axiom (ledger stays 3). Emit it here only when a
        # transform needs it AND the pydict theory (which also declares it) is
        # not present, so it is never declared twice.
        if ((getattr(self, "_needs_term_streq", False)
                or needs.get("needs_term_eq"))
                and not needs.get("needs_pydict")
                and not needs.get("needs_selfstate_streq")):
            # `needs_selfstate_streq` (the registry_skipped string-empty path)
            # already declares `val pystr_eq` via the preamble helpers — never
            # double-declare it here (term_eq reuses that one).
            lines.append("  (* T-transform const-map string guard (result VC-free; ledger 3) *)")
            lines.append("  val pystr_eq (a b: string) : bool")
            lines.append("")
        # class-variant-impl.md §F4: the DEFINED structural equality over the
        # certified `term` inductive — `a == b` on Term (crosscheck_ir
        # `provers_agree`/`all_agree`) lowers to `term_eq`. TOTAL, mutually
        # recursive with `term_list_eq` (App.args : list term) and `strlist_eq`
        # (Forall/Exists.binders : list string), structural `variant` (Why3-
        # intrinsic termination over the same Phase2i-certified inductive — NO
        # new certificate, NO axiom; `pystr_eq` is a VC-free `val`). Emitted
        # generically from the term spec so a field-type change flows.
        # T-string (`_pp`): the string-BUILD catamorphism needs string concat +
        # int->string. Abstract `val`s (str_concat_op is spec'd by `concat`; ledger
        # 3 — no axiom). Gated on the pp recognizer so non-pp term files stay
        # byte-identical.
        if getattr(self, "_needs_term_strbuild", False):
            lines.append("  (* T-string (`_pp`) string-build ops (ledger 3) *)")
            lines.append("  val str_concat_op (a: string) (b: string) : string")
            lines.append("    ensures { result = (concat a b) }")
            lines.append("    ensures { String.length result"
                         " = String.length a + String.length b }")
            lines.append("  val str_of_int (x: int) : string")
            lines.append("")
        if needs.get("needs_term_eq"):
            lines += self._emit_term_eq_defs(ctors, order)
        return lines

    def _emit_term_eq_defs(self, ctors: Dict[str, Any],
                           order: List[str]) -> List[str]:
        """Generate `term_eq`/`term_list_eq`/`strlist_eq` from the term spec
        (class-variant-impl.md §F4). Per-ctor arm ANDs the field-wise equality
        chosen by each field's WhyML type (string -> pystr_eq, int -> `=`,
        bool -> iff, term -> term_eq, list term -> term_list_eq, list string ->
        strlist_eq). Faithful (a field-type change flows); axiom-free (the
        Phase2i cert already certifies the inductive is well-formed / distinct /
        injective — the facts this total structural eq relies on)."""
        def _feq(wt: str, a: str, b: str) -> str:
            if wt == "string":
                return f"(pystr_eq {a} {b})"
            if wt == "int":
                return f"(if {a} = {b} then true else false)"
            if wt == "bool":
                return f"(if {a} then {b} else (not {b}))"
            if wt == "term":
                return f"(term_eq {a} {b})"
            if wt == "list term":
                return f"(term_list_eq {a} {b})"
            if wt == "list string":
                return f"(strlist_eq {a} {b})"
            return "false"                    # fail-closed (unreachable for spec)
        lines = [
            "  (* §F4: DEFINED structural term equality (mutual, terminating;"
            " ledger 3) *)",
            "  let rec term_eq (a b: term) : bool",
            "    variant { a }",
            "  = match a, b with",
        ]
        for c in order:
            flds = ctors[c]
            av = [f"a{i}" for i in range(len(flds))]
            bv = [f"b{i}" for i in range(len(flds))]
            lpat = f"{c} {' '.join(av)}".rstrip()
            rpat = f"{c} {' '.join(bv)}".rstrip()
            if flds:
                conj = " && ".join(
                    _feq(wt, av[i], bv[i]) for i, (_fn, wt) in enumerate(flds))
            else:
                conj = "true"
            lines.append(f"    | {lpat}, {rpat} -> {conj}")
        lines.append("    | _, _ -> false")
        lines.append("    end")
        lines.append("  with term_list_eq (xs ys: list term) : bool")
        lines.append("    variant { xs }")
        lines.append("  = match xs, ys with")
        lines.append("    | Nil, Nil -> true")
        lines.append("    | Cons x xs2, Cons y ys2 ->"
                     " (term_eq x y) && (term_list_eq xs2 ys2)")
        lines.append("    | _, _ -> false")
        lines.append("    end")
        lines.append("  with strlist_eq (xs ys: list string) : bool")
        lines.append("    variant { xs }")
        lines.append("  = match xs, ys with")
        lines.append("    | Nil, Nil -> true")
        lines.append("    | Cons x xs2, Cons y ys2 ->"
                     " (pystr_eq x y) && (strlist_eq xs2 ys2)")
        lines.append("    | _, _ -> false")
        lines.append("    end")
        lines.append("")
        return lines

    def _emit_pydict_theory(self, needs: Dict[str, Any]) -> List[str]:
        """WALL-PLAN v2 (generic-dict-str-any-2-plan.md §1 D1–D3, §2 E4, §3 F4):
        the concrete-map universal-value theory, promoted from the Phase-0 spike
        (`test-suite/corpus/conformance/spikes/v2_pydict_spike.mlw`, verdict
        `getting-better/tier3/wall-plan-v2-phase0.md`) into the emitter preamble.

        Pure inductive datatypes + a PROVEN lemma pack — NO `axiom` (R-C). The
        Rocq/Lean twins (`Phase2c_PyValDict.v` / `PyValDict.lean`) certify the same
        laws axiom-free, so the 3-axiom ledger is unchanged.

        ADDITIVE / inert: gated on `needs.get("needs_pydict")`, which nothing in
        the reference corpus sets (Phase 2 routing turns it on), so the emission is
        byte-diff-0 on the 756-program corpus. The required `use`s are emitted by
        `_emit_preamble_uses` under the same gate."""
        if not needs.get("needs_pydict"):
            return []
        return (self._pydict_theory_lines() + self._sdict_theory_lines(needs)
                + self._pyput_theory_lines(needs))

    def _pyput_theory_lines(self, needs: Dict[str, Any]) -> List[str]:
        """LEVER 1 (seven-levers.md §1): the WRITE half of the pydict value model
        — `pput` (Map.set over the certified assoc-list `pydict`) + `pappend`
        (list construct/append), with the characterizing law pack and the program
        wrappers/by-reference frames the emitter's construction recognizers call.

        `pput`/`pappend` are pure LOGIC `function`s with total structural bodies,
        so they add NO VC of their own; the laws (`get_pput_same`/`get_pput_other`/
        `size_dict_pput`/`mem_pput_same`/`size_pappend`/`mem_pappend`) are each a
        PROVEN `let rec lemma` (the recursion IS the induction) — NO `axiom`. The
        program `val pput_prog`/`pappend_prog` and the by-reference `val`
        `set_field_inplace`/`set_add_inplace` are realizable-by-construction (the
        logic functions witness a result satisfying each `ensures` EXISTS — the
        established `set_add` pattern), so they add no assumption a model couldn't
        realize. The Rocq/Lean twins (`Phase2c_PyValDict.v::pput/pappend` +
        `PyValDict.lean::pput/pappend`) certify the SAME laws axiom-free
        (`Print Assumptions`/`#print axioms` == 3), so the ledger is UNCHANGED.

        ADDITIVE / inert: gated on `needs_pput` (nothing in the reference corpus
        sets it; only a Lever-1 construction recognizer routes it on), so the
        emission is byte-diff-0 on the corpus. Requires the base `needs_pydict`
        theory (pydict/get/mem_key/pv_size/size_list/size_dict) in scope."""
        if not needs.get("needs_pput"):
            return []
        return [
            "",
            "  (* ==== seven-levers §1: the WRITE half — pput / pappend (construction) ==== *)",
            "  (* pput = total structural Map.set over the assoc-list pydict: replace the *)",
            "  (* value if the key is present, else cons the new binding. LOGIC function *)",
            "  (* (structural body => no VC of its own); irkey `=` is LOGIC equality here. *)",
            "  function pput (d: pydict) (k: irkey) (v: pyval) : pydict",
            "  = match d with",
            "    | DNil -> DCons k v DNil",
            "    | DCons k' v' rest ->",
            "        if k = k' then DCons k v rest else DCons k' v' (pput rest k v)",
            "    end",
            "",
            "  (* pappend = list construct/append (d.append / insert-at-end). *)",
            "  function pappend (l: list pyval) (x: pyval) : list pyval",
            "  = match l with Nil -> Cons x Nil | Cons h t -> Cons h (pappend t x) end",
            "",
            "  (* ---- the characterizing law pack (each a PROVEN `let rec lemma`, no axiom); *)",
            "  (* bodies match on the structure and recurse UNCONDITIONALLY, the SMT closes *)",
            "  (* the `k = k'` case split inside each arm's VC. Certified in Phase2c_PyValDict.v. *)",
            "  let rec lemma get_pput_same (d: pydict) (k: irkey) (v: pyval) : unit",
            "    ensures { get (pput d k v) k = Some v } variant { d }",
            "  = match d with DNil -> () | DCons _ _ rest -> get_pput_same rest k v end",
            "",
            "  let rec lemma get_pput_other (d: pydict) (k k2: irkey) (v: pyval) : unit",
            "    requires { k2 <> k }",
            "    ensures  { get (pput d k v) k2 = get d k2 } variant { d }",
            "  = match d with DNil -> () | DCons _ _ rest -> get_pput_other rest k k2 v end",
            "",
            "  let rec lemma size_dict_pput (d: pydict) (k: irkey) (v: pyval) : unit",
            "    ensures { size_dict (pput d k v) <= size_dict d + pv_size v + 1 }",
            "    ensures { size_dict (pput d k v) >= 0 }",
            "    variant { d }",
            "  = match d with",
            "    | DNil -> size_pos v",
            "    | DCons _ v' rest ->",
            "        size_pos v; size_pos v'; size_dict_nonneg rest; size_dict_pput rest k v",
            "    end",
            "",
            "  let rec lemma mem_pput_same (d: pydict) (k: irkey) (v: pyval) : unit",
            "    ensures { mem_key (pput d k v) k } variant { d }",
            "  = match d with DNil -> () | DCons _ _ rest -> mem_pput_same rest k v end",
            "",
            "  let rec lemma size_pappend (l: list pyval) (x: pyval) : unit",
            "    ensures { size_list (pappend l x) = size_list l + pv_size x + 1 }",
            "    variant { l }",
            "  = match l with Nil -> () | Cons _ t -> size_pappend t x end",
            "",
            "  (* ---- program wrappers (realizable-by-construction; the emitter calls THESE) *)",
            "  val pput_prog (d: pydict) (k: irkey) (v: pyval) : pydict",
            "    ensures { result = pput d k v }",
            "  val pappend_prog (l: list pyval) (x: pyval) : list pyval",
            "    ensures { result = pappend l x }",
            "",
            "  (* ---- by-reference mutation frames: the `#@ assigns d` (dict/set param) model. *)",
            "  (* `d[k]=v` on a by-value dict param lowers to a `ref pydict` in-place set; *)",
            "  (* `s.add e` on a Set[str] param to a `ref (map string bool)` bit-set. *)",
            "  val set_field_inplace (r: ref pydict) (k: irkey) (v: pyval) : unit",
            "    writes  { r }",
            "    ensures { !r = pput (old !r) k v }",
            "    ensures { get !r k = Some v }",
            "  val set_add_inplace (s: ref (map string bool)) (e: string) : unit",
            "    writes  { s }",
            "    ensures { !s = Map.set (old !s) e true }",
            "    ensures { Map.get !s e = true }",
        ]

    def _sdict_theory_lines(self, needs: Dict[str, Any]) -> List[str]:
        """ir-traversal-residual T3 (plan §5): the string-keyed symbol table
        `sdict` — a SECOND, deliberately-boring datatype whose keys are RUNTIME
        strings (not interned `irkey`), with an option-valued `slookup` (variant
        on the list, structural). Two facts keep computed-key reads in the solved
        discipline: (a) `pystr_eq`'s result is program code no VC constrains
        (insight C); (b) the read returns `option` with an explicit `None` arm
        (defensive totalization) — no string theory enters any VC. Pure inductive
        datatype + a defined function; certified axiom-free in
        `Phase2c_PyValDict.v` / `PyValDict.lean` (the 2nd/last certificate), so
        the 3-axiom ledger is UNCHANGED. Gated on `needs_sdict` (corpus-inert)."""
        if not needs.get("needs_sdict"):
            return []
        return [
            "",
            "  (* ==== ir-traversal-residual T3: string-keyed symbol table `sdict` ==== *)",
            "  (* keys are RUNTIME strings (not interned irkey); slookup is option-valued *)",
            "  (* (defensive totalization) + `pystr_eq`-tested (result no VC constrains). *)",
            "  type sdict = SNil | SCons string pyval sdict",
            "",
            "  let rec slookup (k: string) (s: sdict) : option pyval",
            "    variant { s }",
            "  = match s with",
            "    | SNil -> None",
            "    | SCons k' v rest -> if pystr_eq k k' then Some v else slookup k rest",
            "    end",
            "",
            "  (* census §3: the returned-`sdict` dict-fold `.update`-merge combinator. *)",
            "  (* Purely DEFINED list-concat over the certified `sdict`; totality is *)",
            "  (* discharged by Why3 (structural `variant`), no axiom — the returned-dict *)",
            "  (* model needs no new certificate beyond the already-certified `sdict`. *)",
            "  let rec sappend (a b: sdict) : sdict",
            "    variant { a }",
            "  = match a with",
            "    | SNil -> b",
            "    | SCons k v rest -> SCons k v (sappend rest b)",
            "    end",
        ] + self._pdict_bridge_theory_lines(needs)

    def _pdict_bridge_theory_lines(self, needs: Dict[str, Any]) -> List[str]:
        """pdict-to-sdict-impl.md (heterogeneous-func caller cluster): the
        `pydict -> sdict` extraction bridge a caller (`_check_contract_exprs`)
        needs to hand a function's `symbol_table` pydict field to the
        already-converted `sdict`-consuming walkers. `pget_dyn`/`pget_list` are
        the program-level dynamic-string-key readers (constructor `K_dyn` match,
        NOT irkey `=`, which resolves to int equality in program context);
        `irkey_to_string` is a TOTAL pure literal map (a genuine symbol_table has
        only `K_dyn s` keys, so its faithful case is the carried runtime string);
        `pdict_to_sdict` is the total, structurally-terminating conversion. All
        purely DEFINED over the already-certified `pydict`/`sdict` — NO new type,
        NO new axiom (ledger 3 unchanged). Gated on `needs_pdict_bridge`
        (corpus-inert; fires only for the recognised caller)."""
        if not needs.get("needs_pdict_bridge"):
            return []
        return [
            "",
            "  (* ==== pdict-to-sdict-impl.md: pydict -> sdict extraction bridge ==== *)",
            "  (* dynamic-string-key readers (constructor `K_dyn` match, never irkey `=`) *)",
            "  let rec pget_dyn (name: string) (d: pydict) : option pyval",
            "    variant { d }",
            "    ensures { match result with Some v -> pv_size v <= size_dict d | None -> true end }",
            "  = match d with",
            "    | DNil -> None",
            "    | DCons (K_dyn s) v rest -> if pystr_eq name s then Some v else pget_dyn name rest",
            "    | DCons _ _ rest -> pget_dyn name rest",
            "    end",
            "",
            "  let pget_list (name: string) (d: pydict) : list pyval",
            "    ensures { size_list result <= size_dict d }",
            "  = match pget_dyn name d with Some (PList xs) -> xs | _ -> Nil end",
            "",
            "  (* irkey -> string: TOTAL pure literal map (K_dyn carries its runtime string; *)",
            "  (* interned keys are totalised to their literal — never appear in a symbol_table). *)",
            "  let function irkey_to_string (k: irkey) : string",
            "  = match k with",
            '    | K_type   -> "type"   | K_left  -> "left"  | K_right  -> "right"',
            '    | K_op     -> "op"     | K_z     -> "z"     | K_value  -> "value"',
            '    | K_target -> "target" | K_body  -> "body"  | K_orelse -> "orelse"',
            '    | K_func   -> "func"   | K_name  -> "name"',
            "    | K_dyn s  -> s",
            "    end",
            "",
            "  (* total, structurally-terminating pydict -> sdict conversion (no axiom). *)",
            "  let rec function pdict_to_sdict (d: pydict) : sdict",
            "    variant { d }",
            "  = match d with",
            "    | DNil -> SNil",
            "    | DCons k v rest -> SCons (irkey_to_string k) v (pdict_to_sdict rest)",
            "    end",
        ]

    def _pydict_theory_lines(self) -> List[str]:
        return [
            "",
            "  (* ==== wall-plan v2: concrete-map universal-value theory (inert unless routed) ==== *)",
            "  (* D2 / R-B — interned IR keys: key (dis)equality is constructor reasoning, *)",
            "  (* zero string theory in any walker VC. `K_dyn s` is the computed-key fallback. *)",
            "  type irkey =",
            "    | K_type | K_left | K_right | K_op | K_z",
            "    | K_value | K_target | K_body | K_orelse | K_func | K_name",
            "    | K_dyn string",
            "",
            "  (* D1 / R-A — the strictly-positive concrete universal value (no arrow / no map *)",
            "  (* in any constructor); `pydict` is a bespoke assoc-list keyed by irkey. *)",
            "  type pyval =",
            "    | PInt  int",
            "    | PStr  string",
            "    | PBool bool",
            "    | PNone",
            "    | PList (list pyval)",
            "    | PDict pydict",
            "  with pydict =",
            "    | DNil",
            "    | DCons irkey pyval pydict",
            "",
            "  let function is_pdict (v: pyval) : bool = match v with PDict _ -> true | _ -> false end",
            "  let function is_plist (v: pyval) : bool = match v with PList _ -> true | _ -> false end",
            "  let function is_pstr  (v: pyval) : bool = match v with PStr  _ -> true | _ -> false end",
            "",
            "  (* get / mem_key : structural over the dict; key test is constructor (dis)equality. *)",
            "  function get (d: pydict) (k: irkey) : option pyval",
            "  = match d with",
            "    | DNil -> None",
            "    | DCons k' v rest -> if k = k' then Some v else get rest k",
            "    end",
            "",
            "  predicate mem_key (d: pydict) (k: irkey)",
            "  = match d with",
            "    | DNil -> false",
            "    | DCons k' _ rest -> k = k' \\/ mem_key rest k",
            "    end",
            "",
            "  function values (d: pydict) : list pyval",
            "  = match d with",
            "    | DNil -> Nil",
            "    | DCons _ v rest -> Cons v (values rest)",
            "    end",
            "",
            "  (* D3 — size measure: +1 per cons cell (list AND dict), so the HEAD recursion *)",
            "  (* strictly decreases even for a singleton (the spike's crux fix). *)",
            "  function pv_size (v: pyval) : int",
            "  = match v with",
            "    | PInt _ | PStr _ | PBool _ | PNone -> 1",
            "    | PList xs -> 1 + size_list xs",
            "    | PDict d  -> 1 + size_dict d",
            "    end",
            "  with size_list (l: list pyval) : int",
            "  = match l with Nil -> 0 | Cons h t -> 1 + pv_size h + size_list t end",
            "  with size_dict (d: pydict) : int",
            "  = match d with DNil -> 0 | DCons _ v rest -> 1 + pv_size v + size_dict rest end",
            "",
            "  (* R-C — the PROVEN lemma pack (`let rec lemma`: the recursion IS the induction). *)",
            "  let rec lemma size_pos (v: pyval) : unit",
            "    ensures { pv_size v > 0 } variant { v }",
            "  = match v with",
            "    | PList xs -> size_list_nonneg xs",
            "    | PDict d  -> size_dict_nonneg d",
            "    | _ -> () end",
            "  with lemma size_list_nonneg (l: list pyval) : unit",
            "    ensures { size_list l >= 0 } variant { l }",
            "  = match l with Nil -> () | Cons h t -> size_pos h; size_list_nonneg t end",
            "  with lemma size_dict_nonneg (d: pydict) : unit",
            "    ensures { size_dict d >= 0 } variant { d }",
            "  = match d with DNil -> () | DCons _ v rest -> size_pos v; size_dict_nonneg rest end",
            "",
            "  let rec lemma size_dict_mem (k: irkey) (d: pydict) : unit",
            "    ensures { mem_key d k -> match get d k with",
            "                             | Some w -> pv_size w < pv_size (PDict d)",
            "                             | None   -> true end }",
            "    variant { d }",
            "  = match d with DNil -> () | DCons _ _ rest -> size_dict_mem k rest end",
            "",
            "  (* E4 — wf_ir well-formedness + the compositionality lemma the unguarded read *)",
            "  (* discharges from. `wf_val` is the per-key expected-shape table (representative *)",
            "  (* here; `wf_ir_gen.py` emits the full per-(shape,key) predicate from ir_schema.py). *)",
            "  predicate wf_val (k: irkey) (v: pyval)",
            "  = match k with",
            "    | K_op | K_type | K_target | K_func | K_name ->",
            "        (match v with PStr _ -> true | _ -> false end)",
            "    | _ -> true",
            "    end",
            "",
            "  predicate wf_dict (d: pydict)",
            "  = match d with",
            "    | DNil -> true",
            "    | DCons k v rest -> wf_val k v /\\ wf_dict rest",
            "    end",
            "",
            "  predicate wf_ir (v: pyval)",
            "  = match v with PDict d -> wf_dict d | _ -> true end",
            "",
            "  let rec lemma wf_ir_binds (k: irkey) (d: pydict) : unit",
            "    requires { wf_dict d }",
            "    ensures  { forall v: pyval. get d k = Some v -> wf_val k v }",
            "    variant  { d }",
            "  = match d with",
            "    | DNil -> ()",
            "    | DCons _ _ rest -> wf_ir_binds k rest",
            "    end",
            "",
            "  (* F4 — the document ADT + render skeleton; only render touches strings, and no *)",
            "  (* walker VC ever carries a string term (projections flow PStr into DText opaquely). *)",
            "  type doc = DText string | DInt int | DCat doc doc | DDoc_nil",
            "  function int_to_str int : string   (* abstract (uninterpreted) — no axiom *)",
            "  function render (d: doc) : string",
            "  = match d with",
            "    | DText s -> s",
            "    | DInt n  -> int_to_str n",
            "    | DCat a b -> String.concat (render a) (render b)",
            "    | DDoc_nil -> String.empty",
            "    end",
            "",
            "  (* A-unit accumulator model (WL-05b): a Set[str] is `ref (map string bool)`; *)",
            "  (* `.add e` sets the membership bit. `pystr_eq` is the string-guard test *)",
            "  (* (payload equality; the walk contract is `ensures True`, so it need not *)",
            "  (* interpret the string — only type-check the guard). *)",
            "  val set_add (m: map string bool) (e: string) : map string bool",
            "    ensures { result = Map.set m e true }",
            "  val pystr_eq (a b: string) : bool",
            "",
            "  (* A-set result algebra (phase3.md §3.1): a RETURNED set is the same *)",
            "  (* `map string bool`; the `|=` union fold combinator is pointwise or. *)",
            "  (* PURELY DEFINED (map = string -> bool) — no axiom, certified by *)",
            "  (* construction, so the returned-set model needs no new certificate *)",
            "  (* beyond the already-certified L1 set repr. *)",
            "  let function set_union (a b: map string bool) : map string bool",
            "    = fun (k: string) -> orb (Map.get a k) (Map.get b k)",
            "",
        ]

    def _emit_preamble(self, needs: Dict[str, Any],
                       module_name: str = "PyCSL_Program") -> List[str]:
        """Emit the WhyML module header: use declarations, exception types, helper functions."""
        out = self._emit_preamble_uses(needs, module_name)
        out += self._emit_preamble_exceptions(needs)
        out += self._emit_preamble_helpers(needs)
        out += self._emit_pydict_theory(needs)
        out += self._emit_term_theory(needs)
        out += self._emit_preamble_no_exception_predicates(needs)
        # NOTE: `#@ proof` axioms are emitted by `transpile()` AFTER the type
        # declarations (not here) — an axiom may quantify over a user
        # `#@ datatype` (e.g. `forall x: json. …` for the A4 round-trip), which
        # must be declared first. Builtin-typed axioms (gcd/permut/…) are
        # order-insensitive, so this only repositions them, preserving pass/fail.
        out.append("")
        return out

    def _collect_critical_mutexes(self) -> List[str]:
        """Every mutex acquired by a `#@ critical`/`#@ acquires` section anywhere in
        the program, sorted (deterministic — the repo forbids hash-order emission).

        Used to declare the abstract diverging `acquire_<mutex>` operation per mutex:
        a lock-acquire can block forever (deadlock/contention), so it is faithfully
        modelled as a call that *may* diverge. This is what lets a worker carrying a
        `#@ \\diverges` effect type-check — its body genuinely can fail to terminate."""
        mutexes: Set[str] = set()

        def walk(stmts: Any) -> None:
            if not isinstance(stmts, list):
                return
            for s in stmts:
                if not isinstance(s, dict):
                    continue
                if s.get("stmt") == "CriticalSection" and s.get("mutex"):
                    mutexes.add(s["mutex"])
                for v in s.values():
                    if isinstance(v, list):
                        walk(v)
                    elif isinstance(v, dict):
                        walk([v])

        for func in self.ir.get("functions", []):
            walk(func.get("body", []))
        return sorted(mutexes)

    def _emit_shared_state(self) -> List[str]:
        """Emit shared variable declarations and mutex invariant predicates (concurrent model)."""
        out: List[str] = []
        shared_vars = self.ir.get("shared_vars", [])
        mutex_invariants_ir = self.ir.get("mutex_invariants", {})
        if shared_vars:
            self._shared_var_names = {sv["name"] for sv in shared_vars}
            out.append("  (* --- shared state (concurrent model) --- *)")
            n = len(shared_vars)
            i = 0
            while i < n:
                sv = shared_vars[i]
                safe_name = whyml_ident(sv["name"])
                out.append(f"  val {safe_name} : ref int")
                i += 1
            out.append("")
        if mutex_invariants_ir:
            # A logic `predicate` cannot dereference a program mutable `ref`
            # (WhyML forbids logic from seeing mutable program state). So each
            # mutex invariant is lowered as a predicate PARAMETERIZED by the
            # plain (un-deref'd) values of the shared vars it references, and
            # every PROGRAM-context use applies it to the dereferenced refs.
            sorted_mi = sorted(mutex_invariants_ir.items())
            n = len(sorted_mi)
            i = 0
            while i < n:
                mutex, inv_ir = sorted_mi[i]
                safe_mutex = safe_mutex_name(mutex)
                self._in_spec = True
                inv_str = self._expr_to_whyml(inv_ir, set())
                self._in_spec = False
                params = self._mutex_inv_params(mutex, inv_str)
                if params:
                    sig = " ".join(whyml_ident(v) for v in params)
                    inv_bare = inv_str
                    for v in params:
                        inv_bare = inv_bare.replace(f"!{whyml_ident(v)}", whyml_ident(v))
                    out.append(
                        f"  predicate {safe_mutex}_inv ({sig} : int) = {inv_bare}"
                    )
                else:
                    out.append(f"  predicate {safe_mutex}_inv = {inv_str}")
                i += 1
            out.append("")
            sorted_mi2 = sorted(mutex_invariants_ir.items())
            n2 = len(sorted_mi2)
            i2 = 0
            while i2 < n2:
                mutex2, inv_ir2 = sorted_mi2[i2]
                safe_mutex2 = safe_mutex_name(mutex2)
                self._in_spec = True
                inv_str2 = self._expr_to_whyml(inv_ir2, set())
                self._in_spec = False
                app = self._mutex_inv_application(mutex2, inv_str2)
                out.append(f"  let _check_initial_{safe_mutex2} () : unit =")
                out.append(f"    assert {{ {app} }}")
                out.append("")
                i2 += 1
        # Faithful concurrency: acquiring a lock can block forever
        # (deadlock/contention), so the acquire is modelled as an ABSTRACT
        # operation that MAY diverge. A worker whose body enters a critical
        # section therefore genuinely *may* fail to terminate, which justifies
        # the `#@ \diverges` effect the worker declares (`functions.py:~286`).
        # Without this, why3 sees a provably-terminating body and rejects the
        # effect ("this expression does not diverge"). One `val` per mutex,
        # sorted (no hash-order). Only emitted for programs with a critical
        # section, so non-concurrency `.mlw` is byte-identical.
        acquire_mutexes = self._collect_critical_mutexes()
        if acquire_mutexes:
            out.append("  (* lock-acquire may block forever — modelled as diverging *)")
            for mutex in acquire_mutexes:
                safe_mutex = safe_mutex_name(mutex)
                out.append(f"  val acquire_{safe_mutex} () : unit")
                out.append("    diverges")
                out.append("")
        return out

    def _mutex_inv_params(self, mutex: str, inv_str: str) -> List[str]:
        """The shared vars (sorted, deterministic) protected by `mutex` whose
        deref `!name` actually occurs in the lowered invariant `inv_str` — these
        become the parameterized predicate's `int` arguments."""
        names = sorted(
            sv["name"]
            for sv in self.ir.get("shared_vars", [])
            if sv.get("mutex") == mutex
        )
        return [v for v in names if f"!{whyml_ident(v)}" in inv_str]

    def _mutex_inv_application(self, mutex: str, inv_str: str) -> str:
        """Program-context application of `{mutex}_inv`: applied to the
        dereferenced shared refs it is parameterized by (or bare if none)."""
        safe_mutex = safe_mutex_name(mutex)
        params = self._mutex_inv_params(mutex, inv_str)
        if not params:
            return f"{safe_mutex}_inv"
        args = " ".join(f"!{whyml_ident(v)}" for v in params)
        return f"{safe_mutex}_inv {args}"

    def _inductive_referenced_axiom_decls(
            self, inductive_decls: List[Dict[str, Any]]) -> List[str]:
        """Return the `_AXIOM_FUNCTIONS` `val function` decls (registry order)
        applied by any inductive rule, so they can be emitted BEFORE the
        `inductive` block (the rule references them). Empty unless an inductive
        rule actually applies an axiom logic func → existing files unchanged."""
        # `_axiom_logic_funcs` already holds every axiom-function NAME applied by
        # an inductive rule OR a function contract (populated in
        # `_precompute_axiom_logic_funcs`). Emit the matching `val function`
        # decls — minus any the axiom block already emits (cited qualnames) so
        # there is no double declaration.
        used = set(getattr(self, "_axiom_logic_funcs", set()))
        already_names: Set[str] = set()
        for d in getattr(self, "_axiom_emitted_decls", set()):
            parts = d.split()
            if len(parts) >= 3 and parts[0] == "val" and parts[1] == "function":
                already_names.add(parts[2])
            elif len(parts) >= 2 and parts[0] in ("function", "predicate"):
                already_names.add(parts[1])
        used -= already_names
        if not used:
            return []
        # Collect the `val function` decls (registry order) whose symbol name is
        # actually applied by a rule — across ALL `_AXIOM_FUNCTIONS`, NOT just
        # cited qualnames. gap-9: the importer strips the heavy scan-axiom
        # citation from injected stubs (avoiding an E-matching OOM), but the
        # `name_present` inductive STILL needs `slot_inode`/`slot_name` declared.
        result: List[str] = []
        for prefix, fn_decls in self._AXIOM_FUNCTIONS.items():
            for d in fn_decls:
                parts = d.split()
                nm = (parts[2] if len(parts) >= 3 and parts[0] == "val"
                      and parts[1] == "function"
                      else (parts[1] if len(parts) >= 2
                            and parts[0] in ("function", "predicate") else None))
                if nm in used and d not in result:
                    result.append(d)
        return result

    def _emit_uncited_axiom_func_decls(self) -> List[str]:
        """Emit `val function` decls for axiom-backing logic symbols that are
        REFERENCED by a contract (in `self._axiom_logic_funcs`) but NOT already
        declared by the axiom block (`_axiom_emitted_decls`) or the early
        inductive emission. gap-9 importer case: a stripped UnixFs.Dir citation
        leaves no axiom block, yet `dir_lookup(disk, 5, name) >= 0` appears in
        the syscall/wrapper contracts. Empty unless such a referenced-but-
        undeclared symbol exists → existing files byte-identical."""
        wanted = set(getattr(self, "_axiom_logic_funcs", set()))
        if not wanted:
            return []
        already: Set[str] = set()
        for d in getattr(self, "_axiom_emitted_decls", set()):
            parts = d.split()
            if len(parts) >= 3 and parts[0] == "val" and parts[1] == "function":
                already.add(parts[2])
            elif len(parts) >= 2 and parts[0] in ("function", "predicate"):
                already.add(parts[1])
        wanted -= already
        if not wanted:
            return []
        out: List[str] = []
        for prefix, fn_decls in self._AXIOM_FUNCTIONS.items():
            for d in fn_decls:
                parts = d.split()
                nm = (parts[2] if len(parts) >= 3 and parts[0] == "val"
                      and parts[1] == "function"
                      else (parts[1] if len(parts) >= 2
                            and parts[0] in ("function", "predicate") else None))
                if nm in wanted:
                    out.append(f"  {d}")
                    self._axiom_emitted_decls = getattr(
                        self, "_axiom_emitted_decls", set()) | {d}
                    wanted.discard(nm)
        if out:
            out.append("")
        return out

    def _inductive_sig_whyml(self, signature: str) -> str:
        """inductive.md: a predicate's WhyML arg-type list (Why3 `inductive p t1 t2`
        takes UNNAMED arg types). From a source signature `"(n: int, x: Json)"`
        extract the types and map them (scalars stay, a datatype/class lowercases):
        `int json`."""
        inner = signature.strip().lstrip("(").rstrip(")").strip()
        if not inner:
            return ""
        scalars = {"int": "int", "bool": "bool", "str": "string", "float": "real"}
        # Collection params lower to their value-semantic Why3 type, matching the
        # rule-body lowering (a `disk: list` binder appears as `array int` in the
        # forall) — without this the header emits the unbound source type `list`.
        # A multi-word type (e.g. `array int`) must be parenthesised in the
        # space-separated Why3 inductive arg-type list.
        collections = {
            "list": "(array int)", "tuple": "(array int)",
            "bytes": "(array int)", "bytearray": "(array int)",
            "dict": "(map int (option int))",
        }
        types = []
        for part in inner.split(","):
            ty = part.split(":")[-1].strip() if ":" in part else "int"
            if ty in scalars:
                types.append(scalars[ty])
            elif ty in collections:
                types.append(collections[ty])
            else:
                types.append(whyml_ident(ty.lower()))
        return " ".join(types)

    def _emit_inductive_decls(self, inductive_decls: List[Dict[str, Any]]) -> List[str]:
        """inductive.md: emit each `#@ inductive` predicate as a Why3
        `inductive p t1 … = | Rule : clause … end`. Each rule's clause is the
        WhyML of its (contract-expression) Horn-clause body, lowered in spec
        context. Empty list → no output (byte-identical for non-inductive modules)."""
        if not inductive_decls:
            return []
        out: List[str] = []
        prev_spec = self._in_spec
        self._in_spec = True
        # If any inductive rule applies an axiom-backing logic function
        # (`slot_inode`/`slot_name`/… for the `name_present` existential), that
        # `val function` decl must be in scope BEFORE the `inductive` block.
        # Emit (and record as already-emitted) exactly those decls here; the
        # later `_emit_preamble_axioms` skips them via `_axiom_emitted_decls`.
        # Gated on the inductive actually referencing one → other files (gcd,
        # struct, perm) emit byte-identically.
        early = self._inductive_referenced_axiom_decls(inductive_decls)
        if early:
            for d in early:
                out.append(f"  {d}")
                self._axiom_emitted_decls = getattr(
                    self, "_axiom_emitted_decls", set()) | {d}
            out.append("")
        def _emit_member(kw: str, m: Dict[str, Any]) -> None:
            mname = whyml_ident(m["name"].lower())
            msig = self._inductive_sig_whyml(m["signature"])
            out.append(f"  {kw} {mname} {msig} =" if msig else f"  {kw} {mname} =")
            for (rname, clause_ir) in m["rules"]:
                clause = self._expr_to_whyml(clause_ir, set())
                out.append(f"    | {whyml_ident(rname).capitalize()} : {clause}")
        for ind in inductive_decls:
            # The head predicate uses `inductive`; each P2 mutual member uses `with`,
            # forming one Why3 group `inductive p … = | … with q … = | …`.
            _emit_member("inductive", ind)
            for m in ind.get("members", []):
                _emit_member("with", m)
            # A single Why3 `inductive` (or a `with`-joined group) takes NO closing
            # `end` (an `end` would close the enclosing module).
            out.append("")
        self._in_spec = prev_spec
        return out

    def _subst_self_in_expr(self, expr: Any, repl: str) -> Any:
        """fresh-globals.md: deep-copy an `#@ ensures` IR with every `self` receiver
        (FieldGet/Attribute `object == "self"`, and a bare `Var`/`Name` "self")
        rewritten to the module-global name `repl`. Used to re-target the CONSTRUCTOR
        post-state from `self` onto the named global singleton."""
        import copy as _copy

        def rec(e: Any) -> Any:
            if isinstance(e, dict):
                e = dict(e)
                if (e.get("type") in ("FieldGet", "Attribute")
                        and e.get("object") == "self"):
                    e["object"] = repl
                elif (e.get("type") in ("Var", "Name")
                        and e.get("name") == "self"):
                    e["name"] = repl
                for k, v in list(e.items()):
                    e[k] = rec(v)
                return e
            if isinstance(e, list):
                return [rec(x) for x in e]
            return e

        return rec(_copy.deepcopy(expr))

    def _fresh_globals_facts(self) -> List[str]:
        """fresh-globals.md: the WhyML conjunct strings for EVERY module-global
        singleton's constructor post-state (`#@ ensures`, `self` -> the global).
        Shared by `_emit_module_globals` (the proven-of-the-literal GOAL) and the
        `#@ fresh_globals` driver-entry `assume`, so the ASSUMED fact is provably
        the SAME fact that was CHECKED of the global's initializer (no drift)."""
        facts: List[str] = []
        prev_spec = self._in_spec
        prev_self = self._current_self_type
        self._in_spec = True
        for g in self.ir.get("module_globals", []):
            rec = self._record_types.get(g["class"])
            if rec is None:
                continue
            self._current_self_type = g["class"]
            for ens in rec.get("init_ensures", []) or []:
                retargeted = self._subst_self_in_expr(ens, whyml_ident(g["name"]))
                facts.append(self._expr_to_whyml(retargeted, set()))
        self._current_self_type = prev_self
        self._in_spec = prev_spec
        return facts

    def _emit_module_const_compound_maps(self) -> List[str]:
        """compound-key const-map lowering: emit each module-const dict with a
        compound (tuple) key + list value (`TRIGGERS`) as an OPAQUE Why3 map constant

            val constant <NAME> : map <key_whyml> (option (list <elem_whyml>))

        The content is UNMODELLED — sound under the weak `ensures True` contract of the
        getter — while the TYPE is faithful: the key is the native tuple, the value the
        `option`-wrapped list (so a `.get(k, [])` read defaults `None -> Nil`). Emitted
        after the type declarations (order-insensitive for an opaque val). Empty for
        every corpus program (no tuple-keyed const dict) → byte-identical."""
        mcc = getattr(self, "_module_const_compound_dicts", {}) or {}
        if not mcc:
            return []
        out: List[str] = []
        for name in sorted(mcc):
            meta = mcc[name]
            wid = whyml_ident(name)
            out.append(
                f"  val constant {wid} : map {meta['key_whyml']} "
                f"(option (list {meta['elem_whyml']}))")
        out.append("")
        return out

    def _emit_module_globals(self) -> List[str]:
        """inline.md Phase 1: emit each module-level global object instance `g = C(...)`
        as a Why3 mutable-record binding `let g : c = <constructor literal>`. The
        constructor `value` (a `Call` IR) reuses the record-construction lowering
        (`_call_record_constructor`); the record type `c` already carries the class
        invariant + `by` witness, which Why3 checks against the literal. Empty for
        modules with no object globals → byte-identical.

        fresh-globals.md: when a global's class declares a constructor `#@ ensures`,
        ALSO emit a `goal <g>_fresh_init` proving that post-state holds of the global's
        literal initializer. This is the PROOF that backs `#@ fresh_globals`' assumed
        entry fact — the constructor ensures is verified against the freshly
        constructed global (the `Array.make 64 0` witness), never assumed blind."""
        globals_ir = self.ir.get("module_globals", [])
        if not globals_ir:
            return []
        out: List[str] = []
        prev_spec = self._in_spec
        self._in_spec = True
        for g in globals_ir:
            rec = self._record_types.get(g["class"])
            if rec is None:
                continue   # not a known record class — skip (defensive)
            lit = self._expr_to_whyml(g["value"], set())
            out.append(f"  let {whyml_ident(g['name'])} : {rec['whyml_name']} = {lit}")
        # fresh-globals.md: PROVE the constructor `#@ ensures` holds of the freshly
        # constructed instance. A module-scope `goal` cannot reference the program-
        # level mutable `let <g>` binding, so the check is a program function that
        # RE-CONSTRUCTS the same constructor literal and carries the ensures as its
        # postcondition (`self` -> `result`). Why3 verifies the post against the
        # `Array.make 64 0` witness — the PROOF backing `#@ fresh_globals`' assumed
        # entry fact (the constructor ensures is verified, never assumed blind).
        prev_self = self._current_self_type
        for g in globals_ir:
            rec = self._record_types.get(g["class"])
            if rec is None or not (rec.get("init_ensures")):
                continue
            self._current_self_type = g["class"]
            lit = self._expr_to_whyml(g["value"], set())
            # Register `result` as an instance of this class so its array-field
            # subscripts (`result.fd_open[k]`) resolve to the `array int` `[k]`
            # form (mirroring the global), not the abstract `subscript_get`.
            self._module_global_classes["result"] = g["class"]
            posts = []
            for ens in rec["init_ensures"]:
                retargeted = self._subst_self_in_expr(ens, "result")
                posts.append(self._expr_to_whyml(retargeted, set()))
            self._module_global_classes.pop("result", None)
            posts = [p for p in posts if p and p != "true"]
            if not posts:
                continue
            gname = whyml_ident(g["name"]) + "_fresh_init"
            out.append(f"  let {gname} () : {rec['whyml_name']}")
            for p in posts:
                out.append(f"    ensures {{ {p} }}")
            out.append(f"  = {lit}")
            out.append("")
        self._current_self_type = prev_self
        self._in_spec = prev_spec
        out.append("")
        return out

    def _emit_exprir_theory(self) -> List[str]:
        """typed-ir-for-b-ceiling.md B-C1: the `exprir` algebraic sum + reflection
        projections, mirroring the `ir_schema.ExprIR` variants the emitter constructs
        inline. Lets an inline `{"type": "Var", …}` node lower to a TYPED value (an
        `exprir` constructor) that unifies with a real ExprIR field, and lets reflection
        (`.get("type")`/`.get("name")`) lower to a total projection. See §2.1.

        Emitted only for a module with a @mutable_state class (the emitter model);
        the 627-file corpus has none → byte-identical there."""
        return [
            "  (* tier3-p1 T3.1.1 (getting-better/tier3/ir-node-adt-signature.md §7,"
            " risk 7 / no-more-int): the faithful numeric-leaf carrier for a Number node —"
            " keeps int vs float distinct instead of coercing float→int. The Number"
            " constructor's int payload is refined onto this carrier in a later increment;"
            " declared here as the certified (Phase-0 spike) numeric leaf type. *)",
            "  type ir_num = INum int | IReal real",
            "",
            "  (* typed-ir-for-b-ceiling.md B-C1: typed IR-node sum for the emitter model."
            " tier3-p1 T3.1.1: extended with IrBinOp (op, left, right) — the EXPR-family"
            " operator node — realizing the Phase-0 spike design in the live emitter."
            " post-m1-census.md orelse_of mini-M1: extended with IrIfExpr (body, orelse) —"
            " the IfExpr ternary node — following the IrBinOp precedent verbatim."
            " ghost-handler-wall Q2/gh-spike.mlw::Q1FaithfulThirdChild: extended with"
            " IrTer3 (a, b, c) — a GENERIC 3-emit_ir-child node, following the"
            " IrBinOp/IrIfExpr precedent verbatim — for the 3-child ghost handlers"
            " (MapSetExpr(dict,key,value), SetCardExpr(set,lo,hi)) whose 3rd child"
            " previously fell through to the `svalue_of` sentinel (sound but"
            " value-degenerate; see ghost-handler-wall-response.md §1.4/§2)."
            " post-m1-census.md spec-op batch mini-M1: extended with the SPEC-OP"
            " family — IrUnaryOp/IrAt/IrArrayLen/IrInGlobals/IrInScope/IrValid/"
            " IrSeparated/IrLength2D/IrValid2D/IrIsSorted/IrArrayEq/IrPermutation/"
            " IrSum/IrAssignsRegion/IrForallItems — realizing the `_csl_unaryop`,"
            " `_csl_at`, `_csl_array_length`, `_csl_in_globals`, `_csl_in_scope`,"
            " `_csl_valid`, `_csl_separated`, `_csl_length2d`, `_csl_valid2d`,"
            " `_csl_is_sorted`, `_csl_array_eq`, `_csl_permutation`, `_csl_sum`,"
            " `_csl_assigns_region`, `_csl_forall_items` single-return CSL-AST-node"
            " constructions verbatim (IrBinOp precedent)."
            " post-m1-census.md map/set/list batch mini-M1: extended with the"
            " MAP/SET/LIST ghost-collection family — IrMapEmpty/IrMapGet/IrMapSet/"
            " IrMapEq/IrHasKey/IrMapRemove/IrSetEmpty/IrSetAdd/IrSetRemove/IrSetMem/"
            " IrSetUnion/IrSetInter/IrSetDiff/IrSetCard/IrSetSubset/IrSetEq/IrNil/"
            " IrCons/IrHd/IrTl/IrListLength/IrNth/IrMem/IrAppend — realizing the"
            " `_csl_map_empty`, `_csl_map_get`, `_csl_map_set`, `_csl_map_eq`,"
            " `_csl_has_key`, `_csl_map_remove`, `_csl_set_empty`, `_csl_set_add`,"
            " `_csl_set_remove`, `_csl_set_mem`, `_csl_set_union`, `_csl_set_inter`,"
            " `_csl_set_diff`, `_csl_set_card`, `_csl_set_subset`, `_csl_set_eq`,"
            " `_csl_nil`, `_csl_cons`, `_csl_hd`, `_csl_tl`, `_csl_list_length`,"
            " `_csl_nth`, `_csl_mem`, `_csl_append` single-return CSL-AST-node"
            " constructions verbatim (IrBinOp precedent)."
            " post-m1-census.md misc single-return batch mini-M1: extended with the"
            " STRING/TUPLE/GHOST + fieldless family — IrFst/IrSnd/IrCtorTest/"
            " IrCtorPayload/IrStrConcat/IrStrLength/IrStrSub/IrGhostCopy/"
            " IrGhostCopyRange/IrGhostMake/IrSliceAccess/IrSlice/IrNone/IrResult/"
            " IrNothing — realizing the `_csl_fst`, `_csl_snd`, `_csl_ctor_test`,"
            " `_csl_ctor_payload`, `_csl_strconcat`, `_csl_str_length`, `_csl_str_sub`,"
            " `_csl_ghost_copy`, `_csl_ghost_copy_range`, `_csl_ghost_make`,"
            " `_csl_slice`, `_csl_none`, `_csl_result`, `_csl_nothing` single-return"
            " CSL-AST-node constructions verbatim (IrBinOp precedent)."
            " IrSlice realizes the NESTED `{\"type\": \"Slice\", \"lower\":…, \"upper\":…,"
            " \"step\": None}` literal inside `_csl_slice`'s `SliceAccess` payload — a"
            " 2-level dict construction, the `\"value\"` sibling already lowering via the"
            " pre-existing IrVar."
            " cleanup batch (no-more-int doctrine): `_csl_number`/`_csl_bool` NOW convert —"
            " `CSLNumber.value` is a `float` record field lowering to `real`, carried by the"
            " NEW `IrNumF real` leaf (distinct from the pre-existing `IrNum int`, which the"
            " int-literal `{\"type\":\"Number\",\"value\":0}` in `_py_expr_name` keeps);"
            " `CSLBool.value` is a `bool` record field lowering to `int` (bool-as-int),"
            " carried by the NEW `IrBoolC int` leaf. The Number/IrNumF split is chosen at"
            " construction (expressions.py `_lower_irnode_construction`) by the value arg's"
            " type — a `real`-typed field read → `IrNumF`, an int literal → `IrNum`. Both"
            " leaves are childless (no size arm; `_ -> 1` catch-all covers them). *)",
            # J1 Call-internals value model (self-tcb-reduction, callinternals-oracle.mlw
            # Gate-R CONFIRMED): the keyword-node list + Name/Attribute-distinguishing
            # `kwval` — the value-model capability the emitter's Call-internals reflection
            # (`_collect_typevar_registry`-shaped `for kw in call.keywords: if kw.arg==...:
            # kw.value.id`) needs, which the bare-string callee currently COLLAPSES. Declared
            # as STANDALONE types BEFORE the emit_ir sum (kwval is a leaf string, carries no
            # emit_ir → keyword_list is strictly positive and standalone; the composition
            # probe proved folding it into the `with irlist` block hits a termination-measure
            # wall). Referenced from the new `IrCallKw` ctor's `keyword_list` field. Gated on
            # `_uses_call_kw` (a `CallKw`-annotated param/local; no corpus program or other
            # mirror carries it → the emit_ir theory stays byte-identical everywhere else).
            *(([
                "  (* J1 Call-internals value model (self-tcb-reduction,"
                " callinternals-oracle.mlw Gate-R CONFIRMED, axiom-free Z3-Valid): the"
                " keyword-node list + Name/Attribute-distinguishing kwval. KwName carries"
                " an ast.Name node's `.id`; KwAttr carries an ast.Attribute node's `.attr`"
                " — exactly the distinction the bare-string callee COLLAPSES. Standalone"
                " types BEFORE the emit_ir sum (kwval is a leaf string — carries no emit_ir"
                " — so keyword_list is strictly positive and does NOT need the `with irlist`"
                " mutual block, which the composition probe showed hits a termination-measure"
                " wall). keyword_list is a BESPOKE cons-list (KWNil/KWCons), NOT `seq`"
                " (respects the recorded seq non-strict-positivity wall). Gated on"
                " `_uses_call_kw` → every other emit_ir-theory file byte-identical. *)",
                "  type kwval = KwName string | KwAttr string",
                "  type keyword = { kw_arg: string; kw_value: kwval }",
                "  type keyword_list = KWNil | KWCons keyword keyword_list",
                "",
            ]) if self._uses_call_kw() else []),
            "  type emit_ir = IrVar string | IrAttr emit_ir string | IrStr string"
            " | IrNum int | IrNumF real | IrBoolC int | IrRaw string | IrOther string"
            " | IrCall string emit_ir int | IrSub emit_ir emit_ir"
            " | IrTuple emit_ir emit_ir"
            " | IrBinOp string emit_ir emit_ir"
            " | IrFieldGet string string"
            " | IrOld emit_ir | IrOldField string string"
            " | IrIfExpr emit_ir emit_ir"
            " | IrTer3 emit_ir emit_ir emit_ir"
            " | IrUnaryOp string emit_ir"
            " | IrAt emit_ir string"
            " | IrArrayLen string"
            " | IrInGlobals string"
            " | IrInScope string"
            " | IrValid string emit_ir"
            " | IrSeparated string emit_ir string emit_ir"
            " | IrLength2D string emit_ir emit_ir"
            " | IrValid2D string emit_ir emit_ir"
            " | IrIsSorted string emit_ir emit_ir"
            " | IrArrayEq emit_ir emit_ir"
            " | IrPermutation emit_ir emit_ir"
            " | IrSum string emit_ir emit_ir"
            " | IrAssignsRegion string emit_ir emit_ir"
            " | IrForallItems string string string emit_ir"
            " | IrMapEmpty | IrMapGet emit_ir emit_ir | IrMapSet emit_ir emit_ir emit_ir"
            " | IrMapEq emit_ir emit_ir | IrHasKey emit_ir emit_ir"
            " | IrMapRemove emit_ir emit_ir"
            " | IrSetEmpty | IrSetAdd emit_ir emit_ir | IrSetRemove emit_ir emit_ir"
            " | IrSetMem emit_ir emit_ir | IrSetUnion emit_ir emit_ir"
            " | IrSetInter emit_ir emit_ir | IrSetDiff emit_ir emit_ir"
            " | IrSetCard emit_ir emit_ir emit_ir | IrSetSubset emit_ir emit_ir"
            " | IrSetEq emit_ir emit_ir"
            " | IrNil | IrCons emit_ir emit_ir | IrHd emit_ir | IrTl emit_ir"
            " | IrListLength emit_ir | IrNth emit_ir emit_ir | IrMem emit_ir emit_ir"
            " | IrAppend emit_ir emit_ir"
            " | IrFst emit_ir | IrSnd emit_ir"
            " | IrCtorTest string string | IrCtorPayload string string int"
            " | IrStrConcat emit_ir emit_ir | IrStrLength emit_ir"
            " | IrStrSub emit_ir emit_ir emit_ir"
            " | IrGhostCopy string | IrGhostCopyRange string emit_ir emit_ir"
            " | IrGhostMake emit_ir emit_ir"
            " | IrSliceAccess emit_ir emit_ir | IrSlice emit_ir emit_ir"
            " | IrNone | IrResult | IrNothing"
            " | IrStarred emit_ir"
            " | IrNamedExpr string emit_ir"
            " | IrMkTupleN irlist"
            " | IrListN irlist"
            " | IrSetN irlist"
            " | IrCallN string irlist"
            " | IrForall string emit_ir iropt_str iropt_ir"
            " | IrExists string emit_ir iropt_str iropt_ir"
            " | IrSliceN iropt_ir iropt_ir iropt_ir"
            " | IrFunctionVariant emit_ir iropt_str"
            # _py_expr_lambda increment (self-tcb-reduction M5, C-bucket): the lambda-expr
            # node `IrLambda <params irlist> <body>` — inserted INSIDE the emit_ir type
            # (one implicit-concat string) via `+` so the `with` clauses stay on the same
            # line. Gated on `_uses_stmt_ir` (only the Module5 mirror's `_py_expr_lambda`
            # builds it) — every OTHER emit_ir-theory file (incl. corpus files that emit
            # `type emit_ir`, e.g. 0746) is byte-identical (empty string off-gate). size's
            # `| _ -> 1` catch-all covers it (flat for the measure).
            + (" | IrLambda irlist emit_ir"
               " | IrDictLit irlist irlist"
               " | IrGenExp emit_ir emit_ir"
               " | IrListComp emit_ir emit_ir"
               " | IrSetComp emit_ir emit_ir"
               " | IrDictComp emit_ir emit_ir emit_ir"
               if self._uses_stmt_ir() else "")
            # J1: the Call-with-keyword-internals ctor — func-name, the standalone
            # keyword_list (declared above), arg0, arity — PARALLEL to the existing
            # `IrCall string emit_ir int` (kind_of returns "Call" for both; non-injective
            # kind_of is sound, the IrCall/IrCallN precedent). size's `_ -> 1` catch-all
            # covers it (no recursive consumer reflects a keyword list back). Gated WITH
            # the standalone types on `_uses_call_kw` → byte-inert elsewhere.
            + (" | IrCallKw string keyword_list emit_ir int"
               if self._uses_call_kw() else "")
            # self-tcb-reduction family-B (parser clause parsers): the CONTRACT-CLAUSE
            # node ctors the recursive-descent `_ContractParser._parse_*` methods
            # construct. IrProofDecl carries the `#@ proof <prover> <qualname>` node's two
            # LEAF strings (`ProofDecl(prover, qualname)`, `_parse_proof`) — a childless
            # (for the `size` measure) leaf, covered by size's `_ -> 1` catch-all; no
            # consumer reflects it back (terminal parser output), so no discriminant /
            # size-decrease law is needed (the IrOldField two-leaf-string precedent).
            # Gated WITH its kind_of arm on `_uses_clause_ir` → byte-inert in every other
            # mirror + the whole corpus. The IrBinOp/IrCallKw structural-variant precedent.
            + (" | IrProofDecl string string"
               if self._uses_clause_ir() else "")
            # self-tcb-reduction family-B: IrClassInvariant carries the `#@ class
            # invariant <expr>` node's single EMIT_IR child (`ClassInvariant(expr)`,
            # `_parse_class_invariant`) — the parsed contract expression. size recurses
            # the real `expr` child (`1 + size e`, gated arm below); kind_of has its own
            # arm. Gated on `_uses_clause_ir` → byte-inert in every other mirror + the
            # whole corpus. The IrBinOp/IrForallItems emit_ir-child precedent.
            + (" | IrClassInvariant emit_ir"
               if self._uses_clause_ir() else "")
            # self-tcb-reduction family-B: IrRaisesDecl carries the `#@ raises <Exc> when
            # <cond>` node's LEAF-string exception name (`exc_type`) + its single EMIT_IR
            # condition child (`RaisesDecl(exc, self._parse_expr())`, `_parse_raises`).
            # size recurses the real `condition` child (`1 + size e`, gated arm below).
            # Gated on `_uses_clause_ir` → byte-inert everywhere else. The IrForallItems
            # (leading-strings + emit_ir child) precedent.
            + (" | IrRaisesDecl string emit_ir"
               if self._uses_clause_ir() else "")
            # self-tcb-reduction family-B (membership run): IrCSLIn / IrCSLNotIn carry
            # the `<e> in <coll>` / `<e> not in <coll>` node's TWO EMIT_IR children
            # (`CSLIn(element, collection)` / `CSLNotIn(element, collection)`,
            # `_parse_membership`). size recurses BOTH children (`1 + size l + size r`,
            # gated arms below; the IrGhostArraySetDecl / IrStrConcat two-emit_ir-child
            # precedent); kind_of has its own arm each. Gated on `_uses_clause_ir` →
            # byte-inert in every other mirror + the whole corpus.
            + (" | IrCSLIn emit_ir emit_ir | IrCSLNotIn emit_ir emit_ir"
               if self._uses_clause_ir() else "")
            # self-tcb-reduction family-B (_err-divergence run): IrLoopInvariant /
            # IrLoopVariant carry the `#@ loop invariant/variant <e>` node's single EMIT_IR
            # child (`LoopInvariant(expr)` / `LoopVariant(expr)`, `_parse_loop`). size
            # recurses the real `expr` child (`1 + size e`, gated arms below); kind_of has
            # its own arm each. Gated on `_uses_clause_ir` → byte-inert in every other mirror
            # + the whole corpus. The IrClassInvariant emit_ir-child precedent.
            + (" | IrLoopInvariant emit_ir | IrLoopVariant emit_ir"
               if self._uses_clause_ir() else "")
            # self-tcb-reduction family-B (_err-divergence run): IrInterfaceClause carries
            # the `#@ interface <kind> <clause>` node's LEAF-string kind + its EMIT_IR
            # payload (the wrapped Ensures/Requires/Assigns node); IrEnsures/IrRequires each
            # wrap the single emit_ir contract expression (`_parse_interface`). size recurses
            # the real emit_ir children (gated arms below). Gated `_uses_clause_ir` →
            # byte-inert. The IrRaisesDecl / IrClassInvariant precedents.
            + (" | IrInterfaceClause string emit_ir | IrEnsures emit_ir | IrRequires emit_ir"
               if self._uses_clause_ir() else "")
            # self-tcb-reduction family-B (ghost run): IrGhostAssignDecl carries the
            # `#@ ghost <name> <op> <e>` (opt. `: <type>`) node's LEAF-string `target` +
            # its EMIT_IR `value` child + LEAF-string `op` + LEAF-string `declared_type`
            # (`GhostAssignDecl(name, value, op[, declared_type=gtype])`, `_parse_ghost`);
            # `declared_type` defaults to the concrete string "int". IrGhostArraySetDecl
            # carries `#@ ghost <name>[<i>] = <e>` — LEAF-string `target` + EMIT_IR `index`
            # + EMIT_IR `value` (`GhostArraySetDecl(name, index, value)`). size recurses the
            # real emit_ir children (gated arms below); kind_of has its own arm each. Gated
            # `_uses_clause_ir` → byte-inert. The IrRaisesDecl (string+emit_ir) precedent.
            + (" | IrGhostAssignDecl string emit_ir string string"
               " | IrGhostArraySetDecl string emit_ir emit_ir"
               if self._uses_clause_ir() else "")
            # self-tcb-reduction family-B (footprint run): IrFootprint carries the
            # `#@ footprint <NAME>(<arg>)` node's LEAF-string `happy_name` + its single
            # EMIT_IR `arg` child (`Footprint(happy_name, self._parse_expr())`,
            # `_parse_footprint`). Same string-leaf + emit_ir-child shape as IrRaisesDecl.
            # size recurses the real `arg` child (gated arm below); kind_of has its own
            # arm. Gated `_uses_clause_ir` → byte-inert. The IrRaisesDecl precedent.
            + (" | IrFootprint string emit_ir"
               if self._uses_clause_ir() else "")
            # self-tcb-reduction family-B (mutex run): IrMutexInvariant carries the
            # `#@ mutex_invariant <MUTEX>: <EXPR>` node's LEAF-string `mutex` (the mutex
            # expression string, from the trusted `-> str` `_parse_mutex_expr_str`) + its
            # single EMIT_IR `expr` child (`MutexInvariant(mutex, self._parse_expr())`,
            # `_parse_mutex_invariant`). Same string-leaf + emit_ir-child shape as
            # IrRaisesDecl/IrFootprint. size recurses the real `expr` child (gated arm
            # below); kind_of has its own arm. Gated `_uses_clause_ir` → byte-inert.
            + (" | IrMutexInvariant string emit_ir"
               if self._uses_clause_ir() else "")
            # self-tcb-reduction family-B (shared run): IrSharedDecl carries the
            # `#@ shared <VAR> [protected_by <MUTEX>]` node's LEAF-string `variable` + its
            # OPTIONAL `mutex` string as a monomorphic-option `iropt_str` (`SharedDecl(name,
            # mutex)` / `SharedDecl(name, None)`, `_parse_shared`). No emit_ir child → NO
            # size arm (falls to `size`'s `_ -> 1` catch-all, the IrProofDecl leaf precedent);
            # the `iropt_str` domain is not recursed (the IrFunctionVariant precedent). kind_of
            # has its own arm. Gated `_uses_clause_ir` → byte-inert.
            + (" | IrSharedDecl string iropt_str"
               if self._uses_clause_ir() else "")
            # self-tcb-reduction family-B (mixin-decl run): IrSharedStateDecl carries the
            # `#@ shared_state <name>: <type>` node's two LEAF strings (SharedStateDecl(name,
            # type_str), `_parse_shared_state`). No emit_ir child → childless for the `size`
            # measure (the IrProofDecl two-leaf-string precedent, falls to size's `_ -> 1`
            # catch-all → NO size arm). kind_of has its own arm. Gated `_uses_clause_ir`.
            + (" | IrSharedStateDecl string string"
               if self._uses_clause_ir() else "")
            # self-tcb-reduction family-B (mixin-decl run): IrTouchesFieldDecl carries the
            # `#@ touches_field <name>: <type>` node's two LEAF strings (TouchesFieldDecl(
            # name, type_str), `_parse_touches_field`). No emit_ir child → NO size arm (the
            # IrProofDecl / IrSharedStateDecl precedent). kind_of has its own arm. Gated.
            + (" | IrTouchesFieldDecl string string"
               if self._uses_clause_ir() else "")
            # self-tcb-reduction family-B (mixin-decl run): IrMethodDependencyDecl carries
            # the `#@ depends_method/requires_method <m>: <sig>` node's three LEAF strings
            # (MethodDependencyDecl(method, sig, kind), `_parse_depends_method`; `sig` from
            # the converted `-> str` `_parse_mixin_method_sig`, `kind` the method's own
            # discriminator param). No emit_ir child → NO size arm (the IrProofDecl
            # leaf-string precedent). kind_of has its own arm. Gated `_uses_clause_ir`.
            + (" | IrMethodDependencyDecl string string string"
               if self._uses_clause_ir() else "")
            # self-tcb-reduction family-B (LIST-append clause parsers): IrComposeFromDecl /
            # IrConformsToDecl / IrLockOrder each carry the single `list string` field the
            # `.append`-loop clause parsers build (`ComposeFromDecl(mixins)` /
            # `ConformsToDecl(protocols)` / `LockOrder(order)`, `_parse_compose_from` /
            # `_parse_conforms_to` / `_parse_lock_order`). The payload is the growable
            # `seq string` the in-body list local lowers to (Seq.cons/snoc; the `_parse_act_names`
            # precedent — a `list string` returned/passed as `seq string`), NOT an emit_ir child
            # → childless for the `size` measure (falls to size's `_ -> 1` catch-all → NO size
            # arm; the IrProofDecl leaf precedent). kind_of has its own arm each. Gated
            # `_uses_clause_ir` → byte-inert in every other mirror + the whole corpus.
            + (" | IrComposeFromDecl (seq string)"
               " | IrConformsToDecl (seq string)"
               " | IrLockOrder (seq string)"
               if self._uses_clause_ir() else "")
            + "  with irlist = ILNil | ILCons emit_ir irlist"
            + "  with iropt_str = IrSNone | IrSSome string"
            + "  with iropt_ir = IrONone | IrOSome emit_ir",
            "",
            "  (* _py_expr fixed-child batch mini-M1: IrStarred carries the single"
            " emit_ir child (`_py_expr_starred`'s `value` field) — a GENERIC"
            " 1-emit_ir-child node, following the IrFst/IrHd single-child precedent"
            " (no discriminant/size-decrease lemma pair; those consumers are"
            " non-recursive single reads, same as this one). *)",
            "  (* B-C5: IrCall carries func name, first arg (arg0), arity; IrSub carries"
            " value and index sub-nodes — the emitter reflects on Call/Subscript IR."
            " B-C6: IrTuple carries the first two elements (elts[0], elts[1]) — the"
            " emitter reflects on a MkTuple node's `elts` in the ghost-dict `+=` branch."
            " tier3-p1: IrBinOp carries the operator string and the left/right sub-nodes."
            " orelse_of mini-M1: IrIfExpr carries the body (then/value) and orelse (else)"
            " sub-nodes — the emitter reflects on an IfExpr ternary's `.get(\"body\")`/"
            " `.get(\"orelse\")`. *)",
            "  (* isinstance-on-CSL-class recognizer (self-tcb-reduction M5, _csl_old):"
            " IrOld carries the single wrapped emit_ir sub-node (`_csl_old`'s FALSE"
            " branch `{\"type\":\"Old\",\"expr\":self._csl_to_ir(node.expr)}`); IrOldField"
            " carries the two LEAF strings of the flat `\\old(x.f)` node (`_csl_old`'s TRUE"
            " branch `{\"type\":\"OldField\",\"object\":node.expr.object,\"field\":"
            " node.expr.field}`, reading the CSLFieldAccess's raw `object`/`field` string"
            " fields). CSLFieldAccess-as-emit_ir is modeled as IrFieldGet (its raw"
            " (object:str, field:str) shape matches IrFieldGet string string exactly), so"
            " `isinstance(node.expr, CSLFieldAccess)` lowers to `is_fieldget node.expr` and"
            " the two reads project via `fgobject_of`/`field_of`. Neither node is reflected"
            " back (terminal outputs), so no discriminant/size-decrease law is needed —"
            " both fall to size's `_ -> 1` catch-all (the IrForallItems-domain precedent). *)",
            "  (* variadic content-law comprehension (FABLE-sanctioned): IrMkTupleN carries"
            " the VARIADIC element list of a tuple node (`_csl_mktuple`/`_py_expr_tuple`'s"
            " `elts` — an `array emit_ir` mapped through the recursive dispatcher). The"
            " payload is `irlist` — a MONOMORPHIC cons-list mutually-recursive WITH emit_ir"
            " (ILNil/ILCons), NOT the polymorphic library `list emit_ir`: the polymorphic"
            " `list.List` axioms, unavoidably in scope before the ADT type, made the emit_ir"
            " `size_*_dec` size-decrease lemmas EXPLODE (27-34M-step 30s timeout, measured);"
            " the self-contained `irlist` keeps them at ~30K steps (measured Valid, 0.03s)."
            " `irlen`/`irnth` (below) are its length/nth, used by the comprehension op's"
            " content law — declared AFTER the size lemmas so nothing perturbs them. The op"
            " emits BOTH a length law AND a per-index content law over a SHARED, per-dispatcher"
            " `emit_ir_disp__<disp>` `val function` (expressions.py `_content_comp` variadic"
            " branch). The content law pins map STRUCTURE — result[i] is a deterministic"
            " function of src[i] — NOT dispatcher value-semantics; honest labeling per the"
            " FABLE §6 condition 3. Non-vacuity holds by ILCons injectivity (a non-functional"
            " hostile is refuted). size's `_ -> 1` catch-all covers IrMkTupleN (no recursive"
            " consumer reflects a tuple's element list back — the IrStarred single-read"
            " precedent). IrListN/IrSetN carry the SAME `irlist` payload for `_py_expr_list`'s"
            " ArrayLit / `_py_expr_set`'s SetLit tuple-shaped element lists; IrCallN carries a"
            " func-name `string` + the `irlist` args of `_csl_call_expr`'s Call node (the"
            " content law over `emit_ir_disp__csl_to_ir`). Distinct ctors per node kind for"
            " clarity; each has its own kind_of arm (\"ArrayLit\"/\"SetLit\"/\"Call\"), all"
            " covered by size's `_ -> 1`. IrCallN's \"Call\" tag is intentionally shared with"
            " the pre-existing projection-reflection IrCall (non-injective kind_of is sound —"
            " the IrCall/IrCallN precedent). *)",
            "  (* optional-field builder (monomorphic-option ADTs): IrForall/IrExists carry a"
            " binder var (string), a body sub-node (emit_ir), and the two OPTIONAL binder"
            " fields of `_csl_forall`/`_csl_exists` — the typed/bounded `binder_type`"
            " (`Optional[str]`) and the `in S` `domain` (`Optional[ExprIR]`). The optionals"
            " are carried as MONOMORPHIC option-like ADTs — `iropt_str = IrSNone | IrSSome"
            " string` and `iropt_ir = IrONone | IrOSome emit_ir` — NOT the polymorphic library"
            " `option string`/`option emit_ir`: adding a polymorphic `option emit_ir` INSIDE"
            " the recursive emit_ir sum brings the `option.Option` library axioms into scope"
            " before the emit_ir/irlist `size_*_dec` size-decrease lemmas, exploding them to a"
            " 400s `--fun _csl_forall` TIMEOUT (measured, reverted 2026-07-16); the self-"
            " contained `iropt_ir` keeps them fast (the irlist precedent). The construction"
            " (expressions.py `_lower_irnode_construction`, `_QUANTIFIER_OPT_CTORS`) reads the"
            " Forall/Exists RECORD's `option` fields and converts them at the ctor arg:"
            " `match node.binder_type with Some s -> IrSSome s | None -> IrSNone` and"
            " `match node.domain with Some d -> IrOSome (csl_to_ir d) | None -> IrONone`."
            " size (below) recurses ONLY the body (`1 + size b`); the domain-opt is NOT"
            " counted (no consumer recurses a quantifier's domain — same as IrForallItems),"
            " so `iropt_ir`/`iropt_str` need NO size arm and stay out of the size lemmas. *)",
            "  (* optional-field ext (monomorphic-option ADTs): IrSliceN carries the THREE"
            " ternary-optional bounds of `_py_expr_slice` — `lower`/`upper`/`step`, each the"
            " Python `disp(expr.X) if expr.X else None` (an `Optional[ExprIR]` pure_ast Slice"
            " field, `_OPTIONAL_FIELDS['Slice']`). Each bound is carried as the SAME monomorphic"
            " `iropt_ir` the quantifier domain uses — NOT a bare emit_ir — so a MISSING bound is"
            " the honest `IrONone` and a present one `IrOSome (self._py_expr_to_ir v)`, reading"
            " the `option emit_ir` Slice record field and unwrapping at the ctor arg (expressions."
            " py `_lower_sliceN_optfield`, routed via the SliceN internal tag from functions.py"
            " `_recognize_slice_builder`). kind_of returns \"Slice\" (the real `.get(\"type\")`"
            " tag `_py_expr_slice` emits) — non-injective with the spec-side IrSlice (which drops"
            " step); the IrCall/IrCallN precedent. No consumer recurses a slice bound, so — like"
            " IrForall's domain — NO size arm is needed (falls to `_ -> 1`), keeping the size"
            " lemmas fast. *)",
            "  (* optional-field ext (monomorphic-option ADTs): IrFunctionVariant realizes the"
            " TYPE-LESS `_csl_function_variant` dict `{\"expr\": self._csl_to_ir(node.expr)}` +"
            " optional `if node.ordering: ir[\"ordering\"] = node.ordering`. It carries the"
            " required `expr` sub-node (a bare emit_ir — the `self._csl_to_ir(node.expr)`"
            " dispatch, so `_csl_function_variant` — itself a `_csl_to_ir` handler — stays"
            " emit_ir-typed) and the OPTIONAL `ordering` as `iropt_str`. `node.ordering` is a"
            " parser `expect_name()` token (Optional[str], NEVER the empty string), so the"
            " Python truthiness `if node.ordering:` is exactly presence: `match node.ordering"
            " with Some s -> IrSSome s | None -> IrSNone` (functions.py"
            " `_recognize_functionvariant_builder`, expressions.py"
            " `_lower_functionvariant_optfield`). kind_of returns \"FunctionVariant\" — a label"
            " only (the source dict is type-less, so nothing reflects `.get(\"type\")` on it);"
            " size recurses the real `expr` child (`1 + size e`), NOT the iropt_str. *)",
            "  let function kind_of (e: emit_ir) : string =",
            "    match e with",
            "    | IrVar _ -> \"Var\" | IrAttr _ _ -> \"Attribute\"",
            "    | IrStr _ -> \"String\" | IrNum _ -> \"Number\"",
            "    | IrNumF _ -> \"Number\" | IrBoolC _ -> \"Bool\"",
            "    | IrRaw _ -> \"RawWhyml\"",
            "    | IrCall _ _ _ -> \"Call\" | IrSub _ _ -> \"Subscript\"",
            "    | IrTuple _ _ -> \"MkTuple\"",
            "    | IrBinOp _ _ _ -> \"BinOp\"",
            "    | IrFieldGet _ _ -> \"FieldGet\"",
            "    | IrIfExpr _ _ -> \"IfExpr\"",
            "    | IrTer3 _ _ _ -> \"Ter3\"",
            "    | IrUnaryOp _ _ -> \"UnaryOp\"",
            "    | IrAt _ _ -> \"At\"",
            "    | IrArrayLen _ -> \"ArrayLen\"",
            "    | IrInGlobals _ -> \"InGlobals\"",
            "    | IrInScope _ -> \"InScope\"",
            "    | IrValid _ _ -> \"Valid\"",
            "    | IrSeparated _ _ _ _ -> \"Separated\"",
            "    | IrLength2D _ _ _ -> \"Length2D\"",
            "    | IrValid2D _ _ _ -> \"Valid2D\"",
            "    | IrIsSorted _ _ _ -> \"IsSorted\"",
            "    | IrArrayEq _ _ -> \"ArrayEq\"",
            "    | IrPermutation _ _ -> \"Permutation\"",
            "    | IrSum _ _ _ -> \"Sum\"",
            "    | IrAssignsRegion _ _ _ -> \"AssignsRegion\"",
            "    | IrForallItems _ _ _ _ -> \"ForallItems\"",
            "    | IrMapEmpty -> \"MapEmpty\" | IrMapGet _ _ -> \"MapGet\"",
            "    | IrMapSet _ _ _ -> \"MapSet\" | IrMapEq _ _ -> \"MapEq\"",
            "    | IrHasKey _ _ -> \"HasKey\" | IrMapRemove _ _ -> \"MapRemove\"",
            "    | IrSetEmpty -> \"SetEmpty\" | IrSetAdd _ _ -> \"SetAdd\"",
            "    | IrSetRemove _ _ -> \"SetRemove\" | IrSetMem _ _ -> \"SetMem\"",
            "    | IrSetUnion _ _ -> \"SetUnion\" | IrSetInter _ _ -> \"SetInter\"",
            "    | IrSetDiff _ _ -> \"SetDiff\" | IrSetCard _ _ _ -> \"SetCard\"",
            "    | IrSetSubset _ _ -> \"SetSubset\" | IrSetEq _ _ -> \"SetEq\"",
            "    | IrNil -> \"Nil\" | IrCons _ _ -> \"Cons\"",
            "    | IrHd _ -> \"Hd\" | IrTl _ -> \"Tl\"",
            "    | IrListLength _ -> \"ListLength\" | IrNth _ _ -> \"Nth\"",
            "    | IrMem _ _ -> \"Mem\" | IrAppend _ _ -> \"Append\"",
            "    | IrFst _ -> \"FstExpr\" | IrSnd _ -> \"SndExpr\"",
            "    | IrCtorTest _ _ -> \"CtorTest\" | IrCtorPayload _ _ _ -> \"CtorPayload\"",
            "    | IrStrConcat _ _ -> \"StrConcat\" | IrStrLength _ -> \"StrLength\"",
            "    | IrStrSub _ _ _ -> \"StrSub\"",
            "    | IrGhostCopy _ -> \"GhostCopy\" | IrGhostCopyRange _ _ _ -> \"GhostCopyRange\"",
            "    | IrGhostMake _ _ -> \"GhostMake\"",
            "    | IrSliceAccess _ _ -> \"SliceAccess\" | IrSlice _ _ -> \"Slice\"",
            "    | IrNone -> \"None\" | IrResult -> \"Result\" | IrNothing -> \"Nothing\"",
            "    | IrStarred _ -> \"Starred\"",
            "    | IrNamedExpr _ _ -> \"NamedExpr\"",
            "    | IrMkTupleN _ -> \"MkTuple\"",
            "    | IrListN _ -> \"ArrayLit\"",
            "    | IrSetN _ -> \"SetLit\"",
            "    | IrCallN _ _ -> \"Call\"",
            "    | IrForall _ _ _ _ -> \"Forall\"",
            "    | IrExists _ _ _ _ -> \"Exists\"",
            "    | IrSliceN _ _ _ -> \"Slice\"",
            "    | IrFunctionVariant _ _ -> \"FunctionVariant\"",
            "    | IrOld _ -> \"Old\" | IrOldField _ _ -> \"OldField\"",
            # _py_expr_lambda/dict/comprehension increments: the gated tags (gated WITH the
            # ctors above so kind_of stays exhaustive in both configurations — byte-inert).
            *(["    | IrLambda _ _ -> \"Lambda\""
               " | IrDictLit _ _ -> \"DictLit\""
               " | IrGenExp _ _ -> \"GenExp\""
               " | IrListComp _ _ -> \"ListComp\""
               " | IrSetComp _ _ -> \"SetComp\""
               " | IrDictComp _ _ _ -> \"DictComp\""]
              if self._uses_stmt_ir() else []),
            # J1: IrCallKw's "Call" tag (gated WITH the ctor so kind_of stays exhaustive
            # in both configs — kind_of has NO wildcard, so the arm is REQUIRED when the
            # ctor is present and ABSENT when it is not). Shares "Call" with IrCall/IrCallN
            # (non-injective kind_of is sound — the IrCall/IrCallN precedent).
            *(["    | IrCallKw _ _ _ _ -> \"Call\""]
              if self._uses_call_kw() else []),
            # self-tcb-reduction family-B: the clause-node kind_of arms (gated WITH the
            # ctors so kind_of stays exhaustive in both configs — kind_of has NO wildcard,
            # so the arm is REQUIRED when the ctor is present and ABSENT when it is not).
            *(["    | IrProofDecl _ _ -> \"ProofDecl\""]
              if self._uses_clause_ir() else []),
            *(["    | IrClassInvariant _ -> \"ClassInvariant\""]
              if self._uses_clause_ir() else []),
            *(["    | IrRaisesDecl _ _ -> \"RaisesDecl\""]
              if self._uses_clause_ir() else []),
            *(["    | IrCSLIn _ _ -> \"CSLIn\"",
               "    | IrCSLNotIn _ _ -> \"CSLNotIn\""]
              if self._uses_clause_ir() else []),
            *(["    | IrLoopInvariant _ -> \"LoopInvariant\"",
               "    | IrLoopVariant _ -> \"LoopVariant\""]
              if self._uses_clause_ir() else []),
            *(["    | IrInterfaceClause _ _ -> \"InterfaceClause\"",
               "    | IrEnsures _ -> \"Ensures\"",
               "    | IrRequires _ -> \"Requires\""]
              if self._uses_clause_ir() else []),
            *(["    | IrGhostAssignDecl _ _ _ _ -> \"GhostAssignDecl\"",
               "    | IrGhostArraySetDecl _ _ _ -> \"GhostArraySetDecl\""]
              if self._uses_clause_ir() else []),
            *(["    | IrFootprint _ _ -> \"Footprint\""]
              if self._uses_clause_ir() else []),
            *(["    | IrMutexInvariant _ _ -> \"MutexInvariant\""]
              if self._uses_clause_ir() else []),
            *(["    | IrSharedDecl _ _ -> \"SharedDecl\""]
              if self._uses_clause_ir() else []),
            *(["    | IrSharedStateDecl _ _ -> \"SharedStateDecl\""]
              if self._uses_clause_ir() else []),
            *(["    | IrTouchesFieldDecl _ _ -> \"TouchesFieldDecl\""]
              if self._uses_clause_ir() else []),
            *(["    | IrMethodDependencyDecl _ _ _ -> \"MethodDependencyDecl\""]
              if self._uses_clause_ir() else []),
            *(["    | IrComposeFromDecl _ -> \"ComposeFromDecl\"",
               "    | IrConformsToDecl _ -> \"ConformsToDecl\"",
               "    | IrLockOrder _ -> \"LockOrder\""]
              if self._uses_clause_ir() else []),
            "    | IrOther k -> k",
            "    end",
            "",
            "  (* tier3-p1 T3.1.2 (spike LAW 1): the BinOp constructor DISCRIMINANT — a"
            " match-based bool, NOT `kind_of e = \"BinOp\"`. The two agree on every REAL IR"
            " node (Module 5 never emits an IrOther whose kind is a registry tag — the"
            " commit-d2479fe9 fail-closed boundary), but `is_binop` EXCLUDES the IrOther"
            " catch-all, which is what makes the size-decrease law (below) hold and thus"
            " lets structural recursion over a projected sub-node terminate. *)",
            "  let function is_binop (e: emit_ir) : bool =",
            "    match e with IrBinOp _ _ _ -> true | _ -> false end",
            "",
            "  (* orelse_of mini-M1: the IfExpr constructor DISCRIMINANT, following is_binop"
            " verbatim — a match-based bool that EXCLUDES the IrOther catch-all, which is"
            " what makes the size-decrease laws (below) hold and thus lets structural"
            " recursion over a projected sub-node (body_of/orelse_of) terminate. *)",
            "  let function is_ifexpr (e: emit_ir) : bool =",
            "    match e with IrIfExpr _ _ -> true | _ -> false end",
            "",
            "  (* tier3-p1 increment 2 (complete the EXPR family, triage-ranked-tcb-tier3.md"
            " T3.1.2): the per-kind constructor DISCRIMINANTS. Each is a match-based bool that"
            " agrees with `kind_of e = \"K\"` on every REAL node yet EXCLUDES the IrOther"
            " catch-all — the guard shape under which the size-decrease laws hold. Registered"
            " in expressions.py::_KIND_DISCRIMINANT so `node.get(\"type\") == \"K\"` lowers to"
            " `(is_K node)` (the faithful match dispatch, not a string compare). *)",
            "  let function is_var (e: emit_ir) : bool =",
            "    match e with IrVar _ -> true | _ -> false end",
            "  let function is_num (e: emit_ir) : bool =",
            "    match e with IrNum _ -> true | _ -> false end",
            "  let function is_str (e: emit_ir) : bool =",
            "    match e with IrStr _ -> true | _ -> false end",
            "  let function is_sub (e: emit_ir) : bool =",
            "    match e with IrSub _ _ -> true | _ -> false end",
            "  let function is_attribute (e: emit_ir) : bool =",
            "    match e with IrAttr _ _ -> true | _ -> false end",
            "  let function is_call (e: emit_ir) : bool =",
            ("    match e with IrCall _ _ _ -> true | IrCallKw _ _ _ _ -> true"
             " | _ -> false end" if self._uses_call_kw() else
             "    match e with IrCall _ _ _ -> true | _ -> false end"),
            "  let function is_tuple (e: emit_ir) : bool =",
            "    match e with IrTuple _ _ -> true | _ -> false end",
            "  let function is_fieldget (e: emit_ir) : bool =",
            "    match e with IrFieldGet _ _ -> true | _ -> false end",
            # const-reflection value model (self-tcb-reduction, Tier-5 value-model wall):
            # the two COMPOUND const-node discriminants. `is_constant` spans ALL const-literal
            # leaves (`isinstance(x, ast.Constant)` <-> x lowered from an ast.Constant node,
            # which `_py_expr_constant` sends to IrNum/IrNumF/IrStr/IrBoolC/IrNone by value);
            # `is_num_or_float` is the tuple-of-types `isinstance(x.value, (int, float))` (the
            # NUMERIC subset IrNum/IrNumF). Both are definitional `let function`s over the
            # EXISTING leaves — like is_num/is_str/is_none — NO axiom, NO new ADT. Proven
            # axiom-free by getting-better/const-reflect-oracle.mlw (Z3 Valid, evil-twins
            # refuted). Gated on `_uses_const_reflect` (a file with an `isinstance(_, (int,
            # float))` reflect) -> corpus + every other mirror byte-identical.
            *(([
                "  (* const-reflection value model (self-tcb-reduction, Tier-5 value-model"
                " wall): the COMPOUND const-node discriminants. `is_constant` spans ALL"
                " const-literal leaves (`isinstance(x, ast.Constant)` <-> x lowered from an"
                " ast.Constant, which `_py_expr_constant` sends to IrNum/IrNumF/IrStr/IrBoolC/"
                " IrNone by value); `is_num_or_float` is the tuple-of-types `isinstance(x.value,"
                " (int, float))` (the numeric subset). Definitional `let function`s over the"
                " existing leaves (the is_num/is_str/is_none precedent) — NO axiom, NO new ADT."
                " Proven axiom-free by getting-better/const-reflect-oracle.mlw. *)",
                "  let function is_constant (e: emit_ir) : bool =",
                "    match e with IrNum _ -> true | IrNumF _ -> true | IrStr _ -> true"
                " | IrBoolC _ -> true | IrNone -> true | _ -> false end",
                "  let function is_num_or_float (e: emit_ir) : bool =",
                "    match e with IrNum _ -> true | IrNumF _ -> true | _ -> false end",
            ]) if self._uses_const_reflect() else []),
            *(([
                "  (* value-model campaign incr8: the None-literal DISCRIMINANT, HOISTED here from"
                " the `_py_expr_dict` dict-literal block below (both gated on `_uses_stmt_ir`) so"
                " the `isinstance(x, ast.Constant) and x.value is None` -> `is_none x` recognizer"
                " (expressions.py `_recognize_none_constant_guard`) can use it. A `None` literal"
                " `ast.Constant` lowers (via `_py_expr_constant`) to EXACTLY `IrNone`, so `is_none"
                " e` <-> \"e is a None literal\" — faithful, definitional `let function`, NO axiom."
                " Same `_uses_stmt_ir` gate as its former dict-block home, so a plain-emit_ir"
                " corpus file (no stmt_ir) stays byte-identical. *)",
                "  let function is_none (e: emit_ir) : bool =",
                "    match e with IrNone -> true | _ -> false end",
            ]) if self._uses_stmt_ir() else []),
            "",
            "  (* output-side slice-discrimination (self-tcb-reduction M5, _py_expr_subscript):"
            " the Slice-kind constructor DISCRIMINANT. `_py_expr_subscript` rewrites its"
            " input-side `isinstance(node.slice, ast.Slice)` test to the SOUND output-side"
            " `self._py_expr_to_ir(node.slice).get(\"type\") == \"Slice\"` — discriminating on"
            " the LOWERED slice's kind (expressions.py::_KIND_DISCRIMINANT `\"Slice\" ->"
            " is_slice`). Matches BOTH slice ctors so it agrees with `kind_of e = \"Slice\"`"
            " on every REAL node (the is_binop faithfulness law): IrSliceN (the 3-bound node"
            " `_py_expr_slice` actually emits) AND the spec-side IrSlice, while EXCLUDING the"
            " IrOther catch-all. No consumer recurses a slice sub-node here (a boolean test"
            " only), so — like the other EXPR discriminants — no size arm/lemma is needed. *)",
            "  let function is_slice (e: emit_ir) : bool =",
            "    match e with IrSlice _ _ -> true | IrSliceN _ _ _ -> true | _ -> false end",
            "",
            "  (* ghost-handler-wall Q2: the IrTer3 constructor DISCRIMINANT, following"
            " is_binop/is_ifexpr verbatim — a match-based bool that EXCLUDES the IrOther"
            " catch-all, which is what makes the size-decrease laws (below) hold. *)",
            "  let function is_ter3 (e: emit_ir) : bool =",
            "    match e with IrTer3 _ _ _ -> true | _ -> false end",
            "",
            "  (* tier3-p1 T3.1.2 (spike LAW 2): BinOp field projections. `op_of` reads the"
            " operator STRING leaf; `left_of`/`right_of` project the SUB-NODES. Total over"
            " the sum (a non-BinOp reads the empty string / the IrOther \"\" sentinel). *)",
            "  let function op_of (e: emit_ir) : string =",
            "    match e with IrBinOp o _ _ -> o | _ -> \"\" end",
            "",
            "  let function left_of (e: emit_ir) : emit_ir =",
            "    match e with IrBinOp _ l _ -> l | _ -> IrOther \"\" end",
            "",
            "  let function right_of (e: emit_ir) : emit_ir =",
            "    match e with IrBinOp _ _ r -> r | _ -> IrOther \"\" end",
            "",
            "  (* orelse_of mini-M1: IfExpr field projections, following left_of/right_of"
            " verbatim. `body_of` projects the then/value sub-node, `orelse_of` the else"
            " sub-node. Total over the sum (a non-IfExpr reads the IrOther \"\" sentinel). *)",
            "  let function body_of (e: emit_ir) : emit_ir =",
            "    match e with IrIfExpr b _ -> b | _ -> IrOther \"\" end",
            "",
            "  let function orelse_of (e: emit_ir) : emit_ir =",
            "    match e with IrIfExpr _ o -> o | _ -> IrOther \"\" end",
            "",
            "  (* ghost-handler-wall Q2 (self-tcb-reduction, ghost-handler-wall-response.md"
            " §2/gh-spike.mlw::Q1FaithfulThirdChild): IrTer3 field projections, following"
            " left_of/right_of/body_of/orelse_of verbatim — a GENERIC 3-emit_ir-child node"
            " reused by every 3-child ghost handler (not one constructor per handler)."
            " `ter_fst_of`/`ter_snd_of`/`ter_thd_of` project the 1st/2nd/3rd sub-node in"
            " declared dataclass field order (the same idx0/idx1/idx2 convention"
            " `_schema_swap_projectors` already uses for the 2-child swap family)."
            " Total over the sum (a non-Ter3 reads the IrOther \"\" sentinel). *)",
            "  let function ter_fst_of (e: emit_ir) : emit_ir =",
            "    match e with IrTer3 a _ _ -> a | _ -> IrOther \"\" end",
            "",
            "  let function ter_snd_of (e: emit_ir) : emit_ir =",
            "    match e with IrTer3 _ b _ -> b | _ -> IrOther \"\" end",
            "",
            "  let function ter_thd_of (e: emit_ir) : emit_ir =",
            "    match e with IrTer3 _ _ c -> c | _ -> IrOther \"\" end",
            "",
            "  (* tier3-p1 T3.1.4 (spike LAW 3): the structural subtree-size measure. The"
            " `variant { e }` is STRUCTURAL (recurses on pattern-bound sub-terms), so it"
            " discharges natively here. The `ensures { result >= 1 }` — proven at this"
            " definition, each recursive call assuming it — exposes `size e >= 1 > 0` to"
            " every caller, discharging the int-variant well-foundedness lower bound. *)",
            "  let rec function size (e: emit_ir) : int",
            "    ensures { result >= 1 }",
            "    variant { e }",
            "  = match e with",
            "    | IrBinOp _ l r -> 1 + size l + size r",
            "    | IrIfExpr b o -> 1 + size b + size o",
            "    | IrSub a b -> 1 + size a + size b",
            "    | IrTuple a b -> 1 + size a + size b",
            "    | IrAttr o _ -> 1 + size o",
            "    | IrCall _ a _ -> 1 + size a",
            "    | IrTer3 a b c -> 1 + size a + size b + size c",
            "    | IrUnaryOp _ e -> 1 + size e",
            "    | IrAt e _ -> 1 + size e",
            "    | IrValid _ l -> 1 + size l",
            "    | IrSeparated _ l1 _ l2 -> 1 + size l1 + size l2",
            "    | IrLength2D _ r c -> 1 + size r + size c",
            "    | IrValid2D _ r c -> 1 + size r + size c",
            "    | IrIsSorted _ l h -> 1 + size l + size h",
            "    | IrArrayEq l r -> 1 + size l + size r",
            "    | IrPermutation l r -> 1 + size l + size r",
            "    | IrSum _ l h -> 1 + size l + size h",
            "    | IrAssignsRegion _ l h -> 1 + size l + size h",
            "    | IrForallItems _ _ _ b -> 1 + size b",
            "    | IrMapGet d k -> 1 + size d + size k",
            "    | IrMapSet d k v -> 1 + size d + size k + size v",
            "    | IrMapEq l r -> 1 + size l + size r",
            "    | IrHasKey d k -> 1 + size d + size k",
            "    | IrMapRemove d k -> 1 + size d + size k",
            "    | IrSetAdd s e -> 1 + size s + size e",
            "    | IrSetRemove s e -> 1 + size s + size e",
            "    | IrSetMem e s -> 1 + size e + size s",
            "    | IrSetUnion l r -> 1 + size l + size r",
            "    | IrSetInter l r -> 1 + size l + size r",
            "    | IrSetDiff l r -> 1 + size l + size r",
            "    | IrSetCard s lo hi -> 1 + size s + size lo + size hi",
            "    | IrSetSubset l r -> 1 + size l + size r",
            "    | IrSetEq l r -> 1 + size l + size r",
            "    | IrCons h t -> 1 + size h + size t",
            "    | IrHd l -> 1 + size l",
            "    | IrTl l -> 1 + size l",
            "    | IrListLength l -> 1 + size l",
            "    | IrNth l i -> 1 + size l + size i",
            "    | IrMem e l -> 1 + size e + size l",
            "    | IrAppend l r -> 1 + size l + size r",
            "    | IrFst t -> 1 + size t",
            "    | IrSnd t -> 1 + size t",
            "    | IrStrConcat l r -> 1 + size l + size r",
            "    | IrStrLength s -> 1 + size s",
            "    | IrStrSub s l h -> 1 + size s + size l + size h",
            "    | IrGhostCopyRange _ l h -> 1 + size l + size h",
            "    | IrGhostMake sz d -> 1 + size sz + size d",
            "    | IrSliceAccess v s -> 1 + size v + size s",
            "    | IrSlice l h -> 1 + size l + size h",
            "    | IrStarred v -> 1 + size v",
            "    | IrNamedExpr _ v -> 1 + size v",
            "    | IrForall _ b _ _ -> 1 + size b",
            "    | IrExists _ b _ _ -> 1 + size b",
            "    | IrFunctionVariant e _ -> 1 + size e",
            # J2/J3 convergence: IrCallKw's size counts its arg0 child (parallel to
            # IrCall's `1 + size a`), so the `size_arg0_dec` lemma (`is_call e -> size
            # (arg0_of e) < size e`) stays VALID now that `is_call` also matches IrCallKw.
            # Without this arm IrCallKw falls to `| _ -> 1` and the lemma is FALSE.
            *(["    | IrCallKw _ _ a _ -> 1 + size a"] if self._uses_call_kw() else []),
            # self-tcb-reduction family-B: IrClassInvariant recurses its single emit_ir
            # child (`1 + size e`), gated WITH the ctor so the measure stays faithful in
            # Module2_Parser.mlw and byte-inert elsewhere. The IrForallItems-body precedent.
            *(["    | IrClassInvariant e -> 1 + size e"] if self._uses_clause_ir() else []),
            # self-tcb-reduction family-B: IrRaisesDecl recurses its emit_ir condition
            # child (`1 + size e`); the leading exception-name string is not counted
            # (the IrForallItems/IrSum leading-string precedent). Gated WITH the ctor.
            *(["    | IrRaisesDecl _ e -> 1 + size e"] if self._uses_clause_ir() else []),
            # self-tcb-reduction family-B (membership run): IrCSLIn / IrCSLNotIn recurse
            # BOTH emit_ir children (the IrGhostArraySetDecl / IrStrConcat precedent).
            *(["    | IrCSLIn l r -> 1 + size l + size r",
               "    | IrCSLNotIn l r -> 1 + size l + size r"]
              if self._uses_clause_ir() else []),
            *(["    | IrLoopInvariant e -> 1 + size e",
               "    | IrLoopVariant e -> 1 + size e"] if self._uses_clause_ir() else []),
            *(["    | IrInterfaceClause _ e -> 1 + size e",
               "    | IrEnsures e -> 1 + size e",
               "    | IrRequires e -> 1 + size e"] if self._uses_clause_ir() else []),
            # self-tcb-reduction family-B (ghost run): IrGhostAssignDecl recurses its single
            # emit_ir `value` child (`1 + size v`; leading `target` + trailing `op`/
            # `declared_type` strings not counted); IrGhostArraySetDecl recurses BOTH emit_ir
            # children `index` + `value` (the IrGhostCopyRange two-emit_ir-child precedent).
            # Gated WITH the ctors.
            *(["    | IrGhostAssignDecl _ v _ _ -> 1 + size v",
               "    | IrGhostArraySetDecl _ i v -> 1 + size i + size v"]
              if self._uses_clause_ir() else []),
            # self-tcb-reduction family-B (footprint run): IrFootprint recurses its single
            # emit_ir `arg` child (`1 + size a`; leading `happy_name` string not counted —
            # the IrRaisesDecl precedent). Gated WITH the ctor.
            *(["    | IrFootprint _ a -> 1 + size a"] if self._uses_clause_ir() else []),
            # self-tcb-reduction family-B (mutex run): IrMutexInvariant recurses its single
            # emit_ir `expr` child (`1 + size e`; leading `mutex` string not counted).
            # Gated WITH the ctor.
            *(["    | IrMutexInvariant _ e -> 1 + size e"] if self._uses_clause_ir() else []),
            "    | _ -> 1",
            "    end",
            "",
            "  (* tier3-p1 T3.1.4: the guarded size-DECREASE laws — a BinOp's left/right"
            " sub-node is strictly smaller than the node. PROVEN (no axiom) by case"
            " analysis on the sum + `size`'s `result >= 1`. These are the facts an"
            " emitter-shaped recursive function over an IR-node param needs at its"
            " recursive call sites (`f (node.get(\"left\"))`) to discharge termination. *)",
            "  lemma size_left_dec  : forall e: emit_ir. is_binop e -> size (left_of e) < size e",
            "  lemma size_right_dec : forall e: emit_ir. is_binop e -> size (right_of e) < size e",
            "",
            "  (* orelse_of mini-M1: the guarded size-DECREASE laws for IfExpr — a ternary's"
            " body/orelse sub-node is strictly smaller than the node. PROVEN (no axiom) by"
            " case analysis on the sum + `size`'s `result >= 1`, following size_left_dec/"
            " size_right_dec verbatim. These are the facts an emitter-shaped recursive"
            " function over an IR-node param needs at its recursive call sites"
            " (`f (node.get(\"body\", {}))`, `f (node.get(\"orelse\", {}))`) to discharge"
            " the injected `variant { size node }`. *)",
            "  lemma size_ifexpr_body_dec : forall e: emit_ir. is_ifexpr e -> size (body_of e) < size e",
            "  lemma size_ifexpr_orelse_dec : forall e: emit_ir. is_ifexpr e -> size (orelse_of e) < size e",
            "",
            "  (* ghost-handler-wall Q2: the guarded size-DECREASE laws for IrTer3 — each of"
            " the 3 sub-nodes is strictly smaller than the node. PROVEN (no axiom) by case"
            " analysis on the sum + `size`'s `result >= 1`, following size_left_dec/"
            " size_right_dec/size_ifexpr_body_dec verbatim. Not required by the two"
            " NON-recursive consumers (map_set/set_card just read each child once), but"
            " kept for parity with every other multi-child constructor's projector triple"
            " and to pre-clear any future recursive walker over IrTer3. *)",
            "  lemma size_ter_fst_dec : forall e: emit_ir. is_ter3 e -> size (ter_fst_of e) < size e",
            "  lemma size_ter_snd_dec : forall e: emit_ir. is_ter3 e -> size (ter_snd_of e) < size e",
            "  lemma size_ter_thd_dec : forall e: emit_ir. is_ter3 e -> size (ter_thd_of e) < size e",
            "",
            "  let function name_of (e: emit_ir) : string =",
            "    match e with IrVar n -> n | IrAttr _ a -> a | _ -> \"\" end",
            "",
            "  let function value_of (e: emit_ir) : string =",
            "    match e with IrStr v -> v | IrRaw v -> v | _ -> \"\" end",
            "",
            # self-tcb-reduction (_is_null_byte_lit): the INTEGER-value reader for a Number
            # leaf. `value_of` reads only the STRING leaves (IrStr/IrRaw), so a `Number` node's
            # `.get("value")` (an int) has no faithful projector — `_is_null_byte_lit`'s
            # `elts[0].get("value") == 0` would mis-lower to `str_hash_op (value_of elt) = 0`
            # (value_of = "" for every Number, so it cannot tell Number 0 from Number 5 —
            # vacuous). `num_of` projects IrNum's int payload, so `num_of elt = 0` is the
            # FAITHFUL int test. Definitional `let function`, NO axiom. GATED on
            # `_uses_null_byte_num_reader` (a file defining `_is_null_byte_lit`); no corpus
            # program defines it, so the emit_ir theory every corpus file emits stays
            # byte-identical. Routed ONLY inside `_is_null_byte_lit` via a scoped `.get("value")`
            # override, so every other handler's `.get("value")` keeps the string `value_of`.
            *(([
                "  let function num_of (e: emit_ir) : int =",
                "    match e with IrNum n -> n | _ -> 0 end",
                "",
            ]) if (self._uses_null_byte_num_reader() or self._uses_const_reflect()) else []),
            "  (* tier3-p1 increment 2 (§5e / risk-6 asymmetry): FieldGet projections."
            " FieldGet.object is a LEAF string (`fgobject_of` : string) — UNLIKE"
            " Attribute.object which is a SUB-node (`object_of` : emit_ir). FieldGet.field is"
            " also a leaf string (`field_of`). The two `object` reads have DIFFERENT result"
            " type-classes, so a naive \"object is a sub-node\" rule is wrong for FieldGet. *)",
            "  let function fgobject_of (e: emit_ir) : string =",
            "    match e with IrFieldGet o _ -> o | _ -> \"\" end",
            "",
            "  let function field_of (e: emit_ir) : string =",
            "    match e with IrFieldGet _ f -> f | _ -> \"\" end",
            "",
            "  let function object_of (e: emit_ir) : emit_ir =",
            "    match e with IrAttr o _ -> o | _ -> IrOther \"\" end",
            "",
            "  (* SAugAssign/SFieldAugAssign/SArraySet increment (self-tcb-reduction M5): the"
            " UNIFIED `.value` projector for `_py_stmt_augassign`, which reads `stmt.target"
            ".value` in BOTH the self-field branch (`stmt.target` is an IrAttr — its `.value`"
            " is the Attribute OBJECT sub-node) and the subscript branch (`stmt.target` is an"
            " IrSub — its `.value` is the Subscript ARRAY sub-node). A REFINEMENT of both"
            " `object_of` (IrAttr arm) and `svalue_of` (IrSub arm): it agrees with `svalue_of`"
            " on every non-IrAttr node and with `object_of` on every non-IrSub node, so each"
            " branch's guard pins which arm fires. Scoped to `_py_stmt_augassign` via"
            " `_EMIT_IR_HANDLER_ATTR_PROJ`. *)",
            "  let function avalue_of (e: emit_ir) : emit_ir =",
            "    match e with IrAttr o _ -> o | IrSub v _ -> v | _ -> IrOther \"\" end",
            "",
            "  let function func_of (e: emit_ir) : string =",
            ("    match e with IrCall f _ _ -> f | IrCallKw f _ _ _ -> f"
             " | _ -> \"\" end" if self._uses_call_kw() else
             "    match e with IrCall f _ _ -> f | _ -> \"\" end"),
            "",
            "  let function nargs_of (e: emit_ir) : int =",
            "    match e with IrCall _ _ n -> n | _ -> 0 end",
            "",
            "  let function arg0_of (e: emit_ir) : emit_ir =",
            ("    match e with IrCall _ a _ -> a | IrCallKw _ _ a _ -> a"
             " | _ -> IrOther \"\" end" if self._uses_call_kw() else
             "    match e with IrCall _ a _ -> a | _ -> IrOther \"\" end"),
            "",
            # J1: the Call-internals projectors (gated WITH the ctor on `_uses_call_kw`).
            # `call_keywords` reads an IrCallKw's keyword_list (`call.keywords`); the kwval
            # discriminant/projector pair (`is_kwname`/`kwname_id`/`is_kwattr`/`kwattr_of`)
            # reads the Name.id / Attribute.attr faithfully (`kw.value.id` / `kw.value.attr`);
            # `kw_arg_of`/`kw_value_of` read a keyword record's `.arg`/`.value`. All total
            # (a non-IrCallKw reads KWNil; a non-Name/Attr reads its sole string arm). NO
            # axiom — definitional `let function`s, exactly the oracle's shape. *)
            *(([
                "  let function call_keywords (e: emit_ir) : keyword_list =",
                "    match e with IrCallKw _ kws _ _ -> kws | _ -> KWNil end",
                "",
                "  (* J2/J3 convergence: indexed access over the bespoke keyword_list cons"
                " (the psl_len/psl_nth precedent) so the imperative `for kw in call.keywords`"
                " loop lowers to the standard index-bounded while. Total + structurally"
                " terminating (variant { l }); NO axiom. *)",
                "  let rec function kwl_len (l: keyword_list) : int =",
                "    match l with KWNil -> 0 | KWCons _ t -> 1 + kwl_len t end",
                "  let rec function kwl_nth (i: int) (l: keyword_list) : keyword",
                "    variant { l } =",
                "    match l with KWNil -> { kw_arg = \"\"; kw_value = KwName \"\" }",
                "    | KWCons h t -> if i <= 0 then h else kwl_nth (i-1) t end",
                "",
                "  let function kw_arg_of (k: keyword) : string = k.kw_arg",
                "  let function kw_value_of (k: keyword) : kwval = k.kw_value",
                "",
                "  let function is_kwname (v: kwval) : bool =",
                "    match v with KwName _ -> true | KwAttr _ -> false end",
                "  let function is_kwattr (v: kwval) : bool =",
                "    match v with KwAttr _ -> true | KwName _ -> false end",
                "  let function kwname_id (v: kwval) : string =",
                "    match v with KwName s -> s | KwAttr s -> s end",
                "  let function kwattr_of (v: kwval) : string =",
                "    match v with KwAttr s -> s | KwName s -> s end",
                "",
            ]) if self._uses_call_kw() else []),
            "  (* resync-campaign.md R1: the args LIST of a reflected Call node — opaque"
            " `array emit_ir` (sound; the ADT carries only arg0/nargs, so content is"
            " unmodelled). Used by the emitter's `val_ir.get(\"args\")`. *)",
            "  val args_of (e: emit_ir) : array emit_ir",
            "  (* cf6.md M1.1: the OPAQUE statement-list of a match case (`c.get(\"body\")`) —"
            " an `array int` (stmt-lists stay int-opaque, feeding `_stmts_to_whyml`), distinct"
            " from `args_of`'s reflected `array emit_ir`. *)",
            "  val stmts_of (e: emit_ir) : array int",
            "",
            "  let function svalue_of (e: emit_ir) : emit_ir =",
            "    match e with IrSub v _ -> v | _ -> IrOther \"\" end",
            "",
            "  let function sindex_of (e: emit_ir) : emit_ir =",
            "    match e with IrSub _ i -> i | _ -> IrOther \"\" end",
            "",
            "  let function elt0_of (e: emit_ir) : emit_ir =",
            "    match e with IrTuple a _ -> a | _ -> IrOther \"\" end",
            "",
            "  let function elt1_of (e: emit_ir) : emit_ir =",
            "    match e with IrTuple _ b -> b | _ -> IrOther \"\" end",
            "",
            "  (* tier3-p1 increment 2 (T3.1.4): the guarded size-DECREASE laws for the rest of"
            " the EXPR family — a Subscript's value/index, an Attribute's object, a Call's"
            " arg0, and a MkTuple's elt0/elt1 sub-node is strictly smaller than the node."
            " PROVEN (no axiom) by case analysis on the sum + `size`'s `result >= 1`. These"
            " are the facts an emitter-shaped recursive function over an IR-node param needs"
            " at each recursive call site (`f (node.get(\"value\"))`, `f (node.get(\"object\"))`,"
            " …) to discharge the injected `variant { size node }`. *)",
            "  lemma size_svalue_dec : forall e: emit_ir. is_sub e -> size (svalue_of e) < size e",
            "  lemma size_sindex_dec : forall e: emit_ir. is_sub e -> size (sindex_of e) < size e",
            "  lemma size_object_dec : forall e: emit_ir. is_attribute e -> size (object_of e) < size e",
            "  lemma size_arg0_dec   : forall e: emit_ir. is_call e -> size (arg0_of e) < size e",
            "  lemma size_elt0_dec   : forall e: emit_ir. is_tuple e -> size (elt0_of e) < size e",
            "  lemma size_elt1_dec   : forall e: emit_ir. is_tuple e -> size (elt1_of e) < size e",
            "",
            "  (* variadic content-law comprehension (FABLE-sanctioned): the length and nth of"
            " the monomorphic `irlist` (IrMkTupleN's payload). Declared AFTER the size"
            " size-decrease lemmas so their proofs never see these defining axioms. Used ONLY"
            " by the comprehension content-law op's `ensures` (an abstract `val` — assumed,"
            " never a VC here). `irnth`'s out-of-range/nil default is `IrOther \"\"` (the"
            " emit_ir absent-sentinel), total. Non-vacuity of the content law rests on ILCons"
            " INJECTIVITY: a non-functional hostile (unequal outputs on equal source elements)"
            " is refuted for every interpretation of the shared `emit_ir_disp__<disp>`. *)",
            "  let rec function irlen (l: irlist) : int",
            "    ensures { result >= 0 }",
            "    variant { l }",
            "  = match l with ILNil -> 0 | ILCons _ t -> 1 + irlen t end",
            "",
            "  let rec function irnth (i: int) (l: irlist) : emit_ir",
            "    variant { l }",
            "  = match l with ILNil -> IrOther \"\""
            " | ILCons h t -> if i <= 0 then h else irnth (i - 1) t end",
            "",
            "  (* self-ir-schema.md IR1: the typed slice of `self.ir` the emitter reflects on —"
            " `self.ir.get(\"shared_vars\", [])` is an array of these records"
            " (`sv[\"name\"]`/`sv.get(\"mutex\")`). Only the string TYPE is modelled; the"
            " content stays opaque via `ir_shared_vars`. *)",
            "  type sharedvar = { sv_name: string; sv_mutex: string }",
            "",
            # pyconst_val value-variant ADT (self-tcb-reduction M5, B-bucket): the WHOLE
            # block — type + `is_pv*`/`pv*_of` + `real_trunc`/`bytes_content_comp` — is emitted
            # ONLY in a file that actually harvested a Constant record (`_uses_pyconst_val`;
            # only the Module5 mirror). Every OTHER full-theory mirror gets NOTHING here, so it
            # stays byte-identical to the pre-feature emitter: adding the 7-constructor
            # `pyconst_val` datatype to their emit_ir theory made Why3's `split_vc` enumerate
            # its constructor cases, exploding the vacuity/proof sub-goal count on heavy
            # mirrors (e.g. `stmt_control_flow`'s `_handle_for_stmt`). Sound: no other mirror
            # references `pyconst_val`, so it is only ever declared where it is used. Corpus is
            # likewise fully inert (its emit_ir drivers have no Constant field).
            *(([
                "  (* pyconst_val value-variant ADT (self-tcb-reduction M5, B-bucket): the"
                " discriminated union of the Python CONSTANT scalar kinds an `ast.Constant`"
                " node's `.value` field holds — the value-model capability the resolver note"
                " (frontend/ir_resolve.py `_PURE_AST_FIELD_TABLE`, the \"_py_expr_constant"
                " blocked\" paragraph) named as the missing value-type-discrimination (the"
                " harvested `value` field was a single opaque leaf, not a discriminated union"
                " of Python scalar types). STANDALONE + MONOMORPHIC: DISJOINT from the emit_ir"
                " mutual-recursion block above (no `with`, no shared `size` induction), so it"
                " adds NO constructor to emit_ir's soundness induction and NO size-decrease"
                " obligation. `is_pv*` discriminants + total `pv*_of` projectors follow the"
                " emit_ir `is_binop`/`left_of` precedent. A `_py_expr_constant`-style"
                " `isinstance(expr.value, bool/str/int/bytes/complex)` / `expr.value is None` /"
                " `is ...` INPUT-side value-type test lowers to the matching `is_pv*`"
                " discriminant (module6_whyml/expressions.py `_handle_isinstance` / the `is"
                " None` handler). Co-landed with an AXIOM-FREE Rocq+Lean certificate"
                " (src/formal-semantics/rocq/Phase2c_PyConstVal.v + lean/PyCSL/PyConstVal.lean):"
                " the abstraction map py-scalar->pyconst_val is total + injective-per-kind, the"
                " `is_pv*` agree with Python isinstance/`is None`, and the `pv*_of` are exact"
                " on their variant. *)",
                "  type pyconst_val = PVNone | PVBool bool | PVInt int | PVStr string"
                " | PVBytes (seq int) | PVComplex real | PVEllipsis",
                "  let function is_pvnone (v: pyconst_val) : bool ="
                " match v with PVNone -> true | _ -> false end",
                "  let function is_pvbool (v: pyconst_val) : bool ="
                " match v with PVBool _ -> true | _ -> false end",
                "  let function is_pvint (v: pyconst_val) : bool ="
                " match v with PVInt _ -> true | _ -> false end",
                "  let function is_pvstr (v: pyconst_val) : bool ="
                " match v with PVStr _ -> true | _ -> false end",
                "  let function is_pvbytes (v: pyconst_val) : bool ="
                " match v with PVBytes _ -> true | _ -> false end",
                "  let function is_pvcomplex (v: pyconst_val) : bool ="
                " match v with PVComplex _ -> true | _ -> false end",
                "  let function is_pvellipsis (v: pyconst_val) : bool ="
                " match v with PVEllipsis -> true | _ -> false end",
                "  let function pvbool_of (v: pyconst_val) : bool ="
                " match v with PVBool b -> b | _ -> false end",
                "  let function pvint_of (v: pyconst_val) : int ="
                " match v with PVInt n -> n | _ -> 0 end",
                "  let function pvstr_of (v: pyconst_val) : string ="
                " match v with PVStr s -> s | _ -> \"\" end",
                "  let function pvbytes_of (v: pyconst_val) : seq int ="
                " match v with PVBytes b -> b | _ -> Seq.empty end",
                "  let function pvreal_of (v: pyconst_val) : real ="
                " match v with PVComplex r -> r | _ -> 0.0 end",
                # complex branch of `_py_expr_constant`: `int(expr.value.real)` is a real->int
                # truncation. Why3's `real.Truncate.truncate` is a LOGIC function (rejected in
                # a program/ghost-free context), so expose a program-callable wrapper PINNED by
                # `ensures` to that exact stdlib symbol — NOT an opaque `val` (its result is
                # fully determined by the trusted `truncate`, adding no PyCSL axiom / TCB).
                "  val function real_trunc (r: real) : int"
                "    ensures { result = truncate r }",
                # bytes content-comprehension: the CONTENT law for `[IrNum(b) for b in
                # <PVBytes payload>]` (the byte-literal branch). Total over the source seq,
                # per-index `IrNum (Seq.get s i)` + exact length — value-faithful, NOT an opaque
                # length-only stub. Abstract `val function` (its `ensures` is assumed, never a
                # VC), the `list_content_comp_N` precedent over a `seq int` source with the
                # `IrNum` leaf ctor. Non-vacuous: `IrNum` is injective.
                "  val function bytes_content_comp (s: seq int) : irlist",
                "    ensures { irlen result = Seq.length s }",
                "    ensures { forall i: int. 0 <= i < Seq.length s ->"
                " irnth i result = IrNum (Seq.get s i) }",
                "",
            ]) if self._uses_pyconst_val() else []),
            # stmt-list-append-mutation wall (self-tcb-reduction M5, C-bucket): the
            # STATEMENT-IR sum an `_py_stmt_*` handler appends to its `ir_stmts` list.
            # STANDALONE + MONOMORPHIC: DISJOINT from the emit_ir mutual-recursion block
            # above (no `with`, no shared `size` induction) — it REFERENCES emit_ir for a
            # statement's expr children (SReturn/SExpr) but emit_ir does NOT reference
            # stmt_ir, so the recursion is one-directional and stmt_ir adds NO constructor
            # to emit_ir's soundness/size induction. TAG-PRESERVING: `stmt_kind_of`
            # projects the node tag (SPass -> "Pass", SBreak -> "Break", …) — the honest
            # discriminant that KILLS the pre-feature `.append({"stmt":K})` -> integer-`0`
            # erasure (fable Oracle 3). Emitted ONLY where a `{"stmt":K}` node is actually
            # appended (`_uses_stmt_ir`; only the Module5 mirror + the wall reference
            # drivers) — every other full-theory mirror + the whole corpus is inert
            # (byte-identical). Co-landed with the axiom-free Rocq+Lean certificate
            # (src/formal-semantics/rocq/Phase2d_StmtIR.v + lean/PyCSL/StmtIR.lean): stmt_ir
            # is a well-founded inductive (size measure + decidable eq), the dict->ctor map
            # is total+injective on the recognized key-set, and the emit_ir child
            # introduces no mutual recursion. The mutable-ref append convention itself is a
            # Why3-intrinsic `writes` VC (no certificate clause needed — recorded in the
            # .v/.lean headers).
            *(([
                "  (* stmt-list-append-mutation wall (self-tcb-reduction M5, C-bucket):"
                " the statement-IR sum. SExpr carries one emit_ir expr child; SReturn"
                " carries the OPTIONAL return value as `iropt_ir` (`IrONone` for a bare"
                " `return`, `IrOSome e` for `return e`) — faithful to `ast.Return.value`"
                " being `option emit_ir` (the ternary `disp(stmt.value) if stmt.value else"
                " None`). The nullary/expr ctors are one-directional references to the"
                " emit_ir ADT above (and its `iropt_ir` sibling) — NOT mutual recursion"
                " WITH emit_ir, so no shared `size` obligation with it. *)",
                "  (* SUB-BODY recursion (self-tcb-reduction M5, C-bucket, this increment):"
                " the compound statements carry their nested statement body/orelse LISTS."
                " SWhile carries the loop TEST (emit_ir) + BODY; SIf carries the TEST +"
                " BODY + ORELSE; SFor carries the ITER (emit_ir) + BODY. The body list is a"
                " bespoke MONOMORPHIC cons-list `stmt_list = SLNil | SLCons stmt_ir"
                " stmt_list` — MUTUALLY recursive WITH stmt_ir (the `irlist` precedent)."
                " The literal `SWhile emit_ir (seq stmt_ir)` is Why3 TYPE-REJECTED (an"
                " abstract `seq` in a ctor arg is non-strictly-positive); `list stmt_ir`"
                " drags the polymorphic `list.List` axioms into scope and EXPLODES the"
                " emit_ir `size_*_dec` lemmas (the measured 27-34M-step blow-up). The"
                " bespoke `stmt_list` is strictly positive and keeps them fast. This"
                " mutual block is STILL one-directional w.r.t. emit_ir (stmt_ir/stmt_list"
                " reference emit_ir for expr children; emit_ir never mentions either), and"
                " is declared AFTER emit_ir's `size`/`size_*_dec` lemmas so nothing"
                " perturbs them. `stmt_kind_of` is the TAG-PRESERVING discriminant (the"
                " honest node tag, never erased to 0). Co-landed with the axiom-free"
                " Rocq+Lean certificate (Phase2d_StmtIR.v / StmtIR.lean) extended for the"
                " mutual `size_stmt`/`size_slist` measure. *)",
                "  (* SAssign + str-Constant recognizer (self-tcb-reduction M5, C-bucket,"
                " this increment): the ASSIGNMENT statement `x = v` carries the TARGET"
                " NAME (a bare `string` leaf — `stmt.target.id` projected via `name_of`,"
                " NOT an emit_ir sub-node) and the RHS VALUE (`emit_ir` — `py_expr_to_ir"
                " stmt.value`). FLAT (no sub-body list), so it falls in `size_stmt`'s"
                " `| _ -> 1` catch-all — NO change to the mutual size measure, the"
                " `size_stmt`/`size_slist` lemmas stay byte-identical. Shared by the"
                " `Assign` dict-key both `_py_stmt_annassign` (`x: T = v`) and — a later"
                " increment — `_py_stmt_assign`'s Name-target branch append. *)",
                "  (* SAugAssign/SFieldAugAssign/SArraySet increment (self-tcb-reduction"
                " M5, C-bucket, this increment): the augmented-assignment statement"
                " `x op= v` / `self.f op= v` / `c[k] op= v` (the `_py_stmt_augassign`"
                " three-branch dispatch). SAugAssign carries the TARGET NAME (string,"
                " `stmt.target.id` via `name_of`), the OP string (`py_op_to_str stmt.op`),"
                " and the RHS emit_ir (`py_expr_to_ir stmt.value`). SFieldAugAssign carries"
                " the self-FIELD NAME (string, `stmt.target.attr` via `name_of`), the OP"
                " string, and the RHS — the constant `object:\"self\"` is DROPPED (the guard"
                " `stmt.target.value.id == 'self'` pins it). SArraySet carries the ARRAY, the"
                " INDEX, and the desugared `(c[k]) op v` BinOp VALUE (all emit_ir). All three"
                " are FLAT (no sub-body list), so they fall in `size_stmt`'s `| _ -> 1`"
                " catch-all — NO change to the mutual size measure. *)",
                "  (* strlist — the monomorphic cons of names; STupleUnpack's targets field"
                " (`[elt.id for elt in target.elts if isinstance(elt, ast.Name)]`), the"
                " concrete compaction over the MkTuple elts (declared before stmt_ir since"
                " STupleUnpack carries it). *)",
                "  type strlist = SLNilS | SLConsS string strlist",
                "  type stmt_ir = SPass | SBreak | SContinue"
                " | SReturn iropt_ir | SExpr emit_ir"
                " | SAssign string emit_ir"
                " | SAssert emit_ir iropt_str"
                " | SAugAssign string string emit_ir"
                " | SFieldAugAssign string string emit_ir"
                " | SArraySet emit_ir emit_ir emit_ir"
                " | SWhile emit_ir stmt_list"
                " | SIf emit_ir stmt_list stmt_list"
                " | SFor emit_ir stmt_list"
                " | STry stmt_list handler_list stmt_list stmt_list"
                " | SMatch emit_ir match_case_list"
                " | SDelSubscript emit_ir emit_ir"
                " | SFieldAssign string string emit_ir"
                " | SArraySliceSet emit_ir iropt_ir iropt_ir emit_ir"
                " | STupleUnpack strlist emit_ir"
                " | SCriticalSection string stmt_list emit_ir emit_ir"
                " | SGhostArraySet string emit_ir emit_ir"
                " | SGhostAssign string emit_ir string string"
                "  with stmt_list = SLNil | SLCons stmt_ir stmt_list"
                "  with handler_list = HLNil | HLCons except_handler handler_list"
                "  with except_handler ="
                " { eh_exc_type: iropt_str; eh_name: iropt_str; eh_body: stmt_list }"
                "  with match_case_list = MCNil | MCCons match_case match_case_list"
                "  with match_case ="
                " { mc_pattern: emit_ir; mc_guard: iropt_ir; mc_body: stmt_list }",
                "  let function stmt_kind_of (s: stmt_ir) : string =",
                "    match s with",
                "    | SPass -> \"Pass\" | SBreak -> \"Break\""
                " | SContinue -> \"Continue\"",
                "    | SReturn _ -> \"Return\" | SExpr _ -> \"Expr\""
                " | SAssign _ _ -> \"Assign\"",
                "    | SAssert _ _ -> \"Assert\"",
                "    | SAugAssign _ _ _ -> \"AugAssign\""
                " | SFieldAugAssign _ _ _ -> \"FieldAugAssign\""
                " | SArraySet _ _ _ -> \"ArraySet\"",
                "    | SWhile _ _ -> \"While\" | SIf _ _ _ -> \"If\""
                " | SFor _ _ -> \"For\""
                " | STry _ _ _ _ -> \"Try\""
                " | SMatch _ _ -> \"Match\""
                " | SDelSubscript _ _ -> \"DelSubscript\""
                " | SFieldAssign _ _ _ -> \"FieldAssign\""
                " | SArraySliceSet _ _ _ _ -> \"ArraySliceSet\""
                " | STupleUnpack _ _ -> \"TupleUnpack\""
                " | SCriticalSection _ _ _ _ -> \"CriticalSection\""
                " | SGhostArraySet _ _ _ -> \"GhostArraySet\""
                " | SGhostAssign _ _ _ _ -> \"GhostAssign\"",
                "    end",
                "",
                "  (* The MUTUAL well-founded size measure over stmt_ir/stmt_list — the"
                " WhyML twin of the certificate's `size_stmt`/`size_slist`. size_stmt"
                " descends into the sub-body list (size_slist), which descends into each"
                " element (size_stmt), the mutual induction. Every node has size >= 1;"
                " a list has size >= 0. Does NOT descend into the FOREIGN emit_ir expr"
                " children (one-directional), so emit_ir's own `size` is untouched. *)",
                "  let rec function size_stmt (s: stmt_ir) : int",
                "    ensures { result >= 1 }",
                "    variant { s }",
                "  = match s with",
                "    | SWhile _ b -> 1 + size_slist b",
                "    | SIf _ b o -> 1 + size_slist b + size_slist o",
                "    | SFor _ b -> 1 + size_slist b",
                "    | STry b hs oe fb -> 1 + size_slist b + size_hlist hs"
                " + size_slist oe + size_slist fb",
                "    | SMatch _ cs -> 1 + size_mclist cs",
                "    | SCriticalSection _ b _ _ -> 1 + size_slist b",
                "    | _ -> 1",
                "    end",
                "  with function size_slist (l: stmt_list) : int",
                "    ensures { result >= 0 }",
                "    variant { l }",
                "  = match l with SLNil -> 0"
                " | SLCons h t -> size_stmt h + size_slist t end",
                "  with function size_hlist (l: handler_list) : int",
                "    ensures { result >= 0 }",
                "    variant { l }",
                "  = match l with HLNil -> 0"
                " | HLCons h t -> size_handler h + size_hlist t end",
                "  with function size_handler (h: except_handler) : int",
                "    ensures { result >= 0 }",
                "    variant { h }",
                "  = 1 + size_slist h.eh_body",
                "  with function size_mclist (l: match_case_list) : int",
                "    ensures { result >= 0 }",
                "    variant { l }",
                "  = match l with MCNil -> 0"
                " | MCCons c t -> size_mcase c + size_mclist t end",
                "  with function size_mcase (c: match_case) : int",
                "    ensures { result >= 0 }",
                "    variant { c }",
                "  = 1 + size_slist c.mc_body",
                "",
                "  (* sl_len : the LENGTH of a stmt_list — the observable the non-vacuity"
                " fixture proves (`sl_len body = <right count>`). *)",
                "  let rec function sl_len (l: stmt_list) : int",
                "    ensures { result >= 0 }",
                "    variant { l }",
                "  = match l with SLNil -> 0 | SLCons _ t -> 1 + sl_len t end",
                "",
                "  (* seq_to_sl : materialize a runtime `seq stmt_ir` (what the mutable-ref"
                " append convention grows, and what the trusted `_py_stmts_to_ir` sub-body"
                " dispatcher yields) into the pure `stmt_list` an SWhile/SIf/SFor ctor"
                " carries. Termination is Why3-INTRINSIC (`variant { Seq.length s - i }`"
                " over the index cursor); no certificate clause needed. The bridge lemma"
                " `seq_to_sl_len` pins the length: `sl_len (seq_to_sl s) = Seq.length s` —"
                " so a body of k runtime nodes yields a stmt_list of length k (NON-facade:"
                " an empty body is SLNil of length 0, a k-node body is a real k-long cons"
                " chain). Proven by the recursive lemma `seq_to_sl_from_len` (the recursion"
                " IS the induction), instantiated at i=0. *)",
                "  let rec function seq_to_sl_from (s: seq stmt_ir) (i: int) : stmt_list",
                "    requires { 0 <= i <= Seq.length s }",
                "    variant  { Seq.length s - i }",
                "  = if i >= Seq.length s then SLNil",
                "    else SLCons (Seq.get s i) (seq_to_sl_from s (i + 1))",
                "  let function seq_to_sl (s: seq stmt_ir) : stmt_list ="
                " seq_to_sl_from s 0",
                "",
                "  let rec lemma seq_to_sl_from_len (s: seq stmt_ir) (i: int)",
                "    requires { 0 <= i <= Seq.length s }",
                "    ensures  { sl_len (seq_to_sl_from s i) = Seq.length s - i }",
                "    variant  { Seq.length s - i }",
                "  = if i >= Seq.length s then () else seq_to_sl_from_len s (i + 1)",
                "  lemma seq_to_sl_len : forall s: seq stmt_ir."
                " sl_len (seq_to_sl s) = Seq.length s",
                "",
                "  (* STry + except_handler + handler_list increment (self-tcb-reduction"
                " M5, C-bucket): the TRY statement `try: <body> except <T> as <n>:"
                " <hbody> ... else: <orelse> finally: <finalbody>`. STry carries FOUR"
                " children: the body/orelse/finalbody sub-lists (each a `stmt_list` via"
                " `seq_to_sl`) and the HANDLER list — a `handler_list = HLNil | HLCons"
                " except_handler handler_list`, MUTUALLY recursive WITH stmt_ir/stmt_list"
                " (the `except_handler` record's `eh_body` field is a `stmt_list`, so the"
                " STry->handler_list->except_handler->stmt_list->stmt_ir cycle forces ONE"
                " mutual `with` block — a `seq except_handler` field is Why3 TYPE-REJECTED"
                " (abstract seq in a ctor arg is non-strictly-positive), the bespoke cons"
                " `handler_list` is strictly positive). except_handler = { eh_exc_type:"
                " iropt_str (the `\"|\".join` compaction of the caught exception TYPE names,"
                " `IrSNone` for a bare `except:`); eh_name: iropt_str (the `as <n>` bind,"
                " `IrSNone` if absent); eh_body: stmt_list (the handler body sub-list) }."
                " The 4-way mutual size measure (size_stmt/size_slist/size_hlist/"
                " size_handler) is declared above; the STry ctor's `_ -> 1` sibling covers"
                " nothing (STry has its own arm). Co-landed with the axiom-free Rocq+Lean"
                " certificate (Phase2d_StmtIR.v / StmtIR.lean) extended for STry +"
                " except_handler + handler_list + the compaction correctness. *)",
                "  (* hl_len : the LENGTH of a handler_list — the observable the"
                " non-vacuity fixture proves (`hl_len handlers = <right count>`). *)",
                "  let rec function hl_len (l: handler_list) : int",
                "    ensures { result >= 0 }",
                "    variant { l }",
                "  = match l with HLNil -> 0 | HLCons _ t -> 1 + hl_len t end",
                "",
                "  (* seq_to_hl : materialize a runtime `seq except_handler` (what the"
                " `handlers = []; for h in stmt.handlers: handlers.append(<rec>)` accumulator"
                " loop grows) into the pure `handler_list` the STry ctor carries. Termination"
                " is Why3-INTRINSIC (`variant { Seq.length s - i }`); the bridge lemma"
                " `seq_to_hl_len` pins `hl_len (seq_to_hl s) = Seq.length s` — a k-handler"
                " loop yields a real k-long cons chain (NON-facade: empty = HLNil length 0). *)",
                "  let rec function seq_to_hl_from (s: seq except_handler) (i: int)"
                " : handler_list",
                "    requires { 0 <= i <= Seq.length s }",
                "    variant  { Seq.length s - i }",
                "  = if i >= Seq.length s then HLNil",
                "    else HLCons (Seq.get s i) (seq_to_hl_from s (i + 1))",
                "  let function seq_to_hl (s: seq except_handler) : handler_list ="
                " seq_to_hl_from s 0",
                "  let rec lemma seq_to_hl_from_len (s: seq except_handler) (i: int)",
                "    requires { 0 <= i <= Seq.length s }",
                "    ensures  { hl_len (seq_to_hl_from s i) = Seq.length s - i }",
                "    variant  { Seq.length s - i }",
                "  = if i >= Seq.length s then () else seq_to_hl_from_len s (i + 1)",
                "  lemma seq_to_hl_len : forall s: seq except_handler."
                " hl_len (seq_to_hl s) = Seq.length s",
                "",
                "  (* SMatch + match_case + match_case_list increment (self-tcb-reduction"
                " M5, C-bucket): the MATCH statement `match <subject>: case <p> [if <g>]:"
                " <body> ...`. SMatch carries the SUBJECT (emit_ir) + the CASE list — a"
                " `match_case_list = MCNil | MCCons match_case match_case_list`, MUTUALLY"
                " recursive WITH stmt_ir/stmt_list (the `match_case` record's `mc_body` is a"
                " `stmt_list`, the same SMatch->match_case_list->match_case->stmt_list->"
                " stmt_ir cycle as STry/handler_list). match_case = { mc_pattern: emit_ir"
                " (`_match_pattern_to_ir(case.pattern)`, the trusted pattern dispatcher's"
                " emit_ir); mc_guard: iropt_ir (the `disp(case.guard) if case.guard else"
                " None` optional guard); mc_body: stmt_list (the case body sub-list) }."
                " The `size_mclist`/`size_mcase` measures are in the mutual block above. *)",
                "  let rec function mcl_len (l: match_case_list) : int",
                "    ensures { result >= 0 }",
                "    variant { l }",
                "  = match l with MCNil -> 0 | MCCons _ t -> 1 + mcl_len t end",
                "",
                "  let rec function seq_to_mcl_from (s: seq match_case) (i: int)"
                " : match_case_list",
                "    requires { 0 <= i <= Seq.length s }",
                "    variant  { Seq.length s - i }",
                "  = if i >= Seq.length s then MCNil",
                "    else MCCons (Seq.get s i) (seq_to_mcl_from s (i + 1))",
                "  let function seq_to_mcl (s: seq match_case) : match_case_list ="
                " seq_to_mcl_from s 0",
                "  let rec lemma seq_to_mcl_from_len (s: seq match_case) (i: int)",
                "    requires { 0 <= i <= Seq.length s }",
                "    ensures  { mcl_len (seq_to_mcl_from s i) = Seq.length s - i }",
                "    variant  { Seq.length s - i }",
                "  = if i >= Seq.length s then () else seq_to_mcl_from_len s (i + 1)",
                "  lemma seq_to_mcl_len : forall s: seq match_case."
                " mcl_len (seq_to_mcl s) = Seq.length s",
                "",
                "  (* The TYPED AST-input readers for `_py_stmt_match`: `py_match_node` models"
                " `ast.Match` (its `stmt` param), `ast_match_case` an `ast.match_case`"
                " element of `stmt.cases`. Opaque deterministic AST projectors (the typed"
                " analogue of iter_get/get_body + the `_match_pattern_to_ir`/`_py_stmts_to_ir`"
                " trusted dispatchers). `mc_pattern_ir` is the pattern lowered to emit_ir"
                " (`_match_pattern_to_ir(case.pattern)`, folded — the trusted pattern"
                " dispatcher yields a real emit_ir, NOT int-erased); `mc_guard_ast` the raw"
                " OPTIONAL guard as `iropt_ir` (`IrONone` = no guard, `IrOSome g` = `if g`);"
                " `mc_body_ast` the case body as `array int` (the `_py_stmts_to_ir`"
                " dispatcher's param type). Gated on `_uses_stmt_ir`. *)",
                "  type py_match_node",
                "  type ast_match_case",
                "  val function match_subject_ast (s: py_match_node) : emit_ir",
                "  val function match_cases_ast (s: py_match_node) : seq ast_match_case",
                "  val function mc_pattern_ir (c: ast_match_case) : emit_ir",
                "  val function mc_guard_ast (c: ast_match_case) : iropt_ir",
                "  val function mc_body_ast (c: ast_match_case) : array int",
                "",
                "  (* SDelSubscript increment (self-tcb-reduction M5, C-bucket): the typed"
                " AST reader for `_py_stmt_delete`. `py_delete_node` models `ast.Delete`"
                " (its `stmt` param); `del_targets_ast` reads `stmt.targets` as a `seq"
                " emit_ir` — each target already the emit_ir of a `_py_expr_to_ir`-lowered"
                " del target (a Subscript -> IrSub, a Name -> IrVar). Opaque deterministic"
                " AST reader (the typed analogue of iter_get). Gated on `_uses_stmt_ir`. *)",
                "  type py_delete_node",
                "  val function del_targets_ast (s: py_delete_node) : seq emit_ir",
                "",
                "  (* SCriticalSection increment (self-tcb-reduction M5, C-bucket): the typed"
                " AST reader for `_py_stmt_with`. `py_with_node` models `ast.With`;"
                " `with_body_ast` reads `stmt.body` (`array int`, the dispatcher param);"
                " `csl_mutex_ast` models the WEAVE-INJECTED `getattr(stmt,"
                " 'csl_critical_mutex', None) or getattr(stmt, 'csl_acquires', None)` mutex"
                " as an opaque `iropt_str` (the mutex NAME, `IrSNone` for a plain `with:`) —"
                " the weaver's `#@ critical`/`#@ acquires` attribute is runtime data on the"
                " With node, so the reader is the honest opaque model (NOT the generic"
                " getattr int-erasure). `mutex_invariant_ir` is the trusted"
                " `_get_mutex_invariant_ir(mutex)` (an emit_ir val, like the pattern"
                " dispatcher). Gated on `_uses_stmt_ir`. *)",
                "  type py_with_node",
                "  val function with_body_ast (s: py_with_node) : array int",
                "  val function csl_mutex_ast (s: py_with_node) : iropt_str",
                "  val function mutex_invariant_ir (mutex: string) : emit_ir",
                "",
                "  (* _py_expr_compare increment (self-tcb-reduction M5, C-bucket): the"
                " typed AST readers for `_py_expr_compare`. `py_compare_node` models"
                " `ast.Compare`; `compare_left_ast` reads `expr.left`, `compare_op0_ast`"
                " the FIRST comparison operator `expr.ops[0]` (an int cmpop, fed to the"
                " trusted `py_op_to_str`), `compare_comp0_ast` the FIRST comparator"
                " `expr.comparators[0]` (emit_ir) — the ast-LIST-HEAD projections (the same"
                " opaque head-reader shape as `_py_stmt_assign`'s `stmt.targets[0]`). Gated"
                " on `_uses_stmt_ir`. Reuses the certified IrBinOp ctor (no new ctor). *)",
                "  type py_compare_node",
                "  val function compare_left_ast (s: py_compare_node) : emit_ir",
                "  val function compare_op0_ast (s: py_compare_node) : int",
                "  val function compare_comp0_ast (s: py_compare_node) : emit_ir",
                "",
                "  (* _py_expr_boolop increment (self-tcb-reduction M5, C-bucket): the"
                " LEFT-FOLD `result = disp(values[0]); for v in values[1:]: result ="
                " {BinOp, op, left=result, right=disp(v)}`. `boolop_fold` is the CONCRETE"
                " recursive fold over the `values[1:]` irlist (each element re-lowered by"
                " the trusted `dispatch` = _py_expr_to_ir, then folded into a left-nested"
                " IrBinOp tree) — NOT an abstract length-only law (the fable vacuity trap)."
                " `boolop_is_and` is the `isinstance(expr.op, ast.And)` And/Or discriminant;"
                " `boolop_val0_ast` reads `values[0]`, `boolop_rest_ast` reads `values[1:]`"
                " (irlist). Gated on `_uses_stmt_ir`. Reuses the certified IrBinOp ctor. *)",
                "  type py_boolop_node",
                "  val function boolop_is_and (s: py_boolop_node) : bool",
                "  val function boolop_val0_ast (s: py_boolop_node) : emit_ir",
                "  val function boolop_rest_ast (s: py_boolop_node) : irlist",
                "  val function boolop_dispatch (e: emit_ir) : emit_ir",
                "  (* _emit_ghost_assign increment (self-tcb-reduction M5, C-bucket): the"
                " typed AST readers for `_emit_ghost_assign`. `py_ghost_node` models a ghost"
                " assignment object; `ghost_is_arrayset` the `isinstance(ga,"
                " GhostArraySetDecl)` CSL-class discriminant (opaque bool, like symtab_mem);"
                " `ghost_target_ast`/`ghost_op_ast` the target/op strings;"
                " `ghost_index_ast`/`ghost_value_ast` the raw CSL index/value nodes (fed to"
                " the trusted `csl_to_ir` = `_csl_to_ir`); `ghost_declared_type_ast` the"
                " `getattr(ga, 'declared_type', 'int')` default-folded string (like delete's"
                " getattr / csl_mutex_ast). Gated on `_uses_stmt_ir`. *)",
                "  type py_ghost_node",
                "  val function ghost_is_arrayset (g: py_ghost_node) : bool",
                "  val function ghost_target_ast (g: py_ghost_node) : string",
                "  val function ghost_op_ast (g: py_ghost_node) : string",
                "  val function ghost_declared_type_ast (g: py_ghost_node) : string",
                "  val function ghost_index_ast (g: py_ghost_node) : emit_ir",
                "  val function ghost_value_ast (g: py_ghost_node) : emit_ir",
                "  val function csl_to_ir (e: emit_ir) : emit_ir",
                "  (* _py_expr_lambda increment (self-tcb-reduction M5, C-bucket): the typed"
                " AST reader for `_py_expr_lambda`. `py_lambda_node` models `ast.Lambda`;"
                " `lambda_args_ast` reads `expr.args.args` (an irlist of arg name-nodes);"
                " `lambda_body_ast` reads `expr.body`. `lambda_param_names_of` is the"
                " CONCRETE `[arg.arg for arg in expr.args.args]` compaction — projecting"
                " `name_of` over the args irlist into IrVar param-name nodes (NOT an abstract"
                " length-only law); `lambda_param_names_prog` its program primitive. The"
                " IrLambda ctor carries the resulting params irlist + the body. *)",
                "  type py_lambda_node",
                "  val function lambda_args_ast (s: py_lambda_node) : irlist",
                "  val function lambda_body_ast (s: py_lambda_node) : emit_ir",
                "  function lambda_param_names_of (l: irlist) : irlist =",
                "    match l with",
                "    | ILNil -> ILNil",
                "    | ILCons a t -> ILCons (IrVar (name_of a))"
                " (lambda_param_names_of t)",
                "    end",
                "  val function lambda_param_names_prog (l: irlist) : irlist",
                "    ensures { result = lambda_param_names_of l }",
                "  (* _py_expr_dict increment (self-tcb-reduction M5, C-bucket): the DUAL"
                " child-list `keys=[disp(k) if k else None for k in expr.keys]; values="
                " [disp(v) for v in expr.values]`. `is_none` is the `k else None` truthiness"
                " test (a None key = IrNone, for `{**spread}`); `dict_keys_of` is the"
                " CONCRETE keys map WITH the None-guard (`if is_none k then IrNone else disp"
                " k`), `dict_values_of` the plain values map — NOT abstract length-only"
                " laws. `dict_dispatch` models the trusted `_py_expr_to_ir`. The IrDictLit"
                " ctor carries the two compacted irlists. (`is_none` is HOISTED to the"
                " unconditional discriminant block above — incr8.) *)",
                "  val function dict_dispatch (e: emit_ir) : emit_ir",
                "  function dict_keys_of (l: irlist) : irlist =",
                "    match l with",
                "    | ILNil -> ILNil",
                "    | ILCons k t -> ILCons (if is_none k then IrNone else dict_dispatch k)"
                " (dict_keys_of t)",
                "    end",
                "  function dict_values_of (l: irlist) : irlist =",
                "    match l with",
                "    | ILNil -> ILNil",
                "    | ILCons v t -> ILCons (dict_dispatch v) (dict_values_of t)",
                "    end",
                "  val function dict_keys_prog (l: irlist) : irlist",
                "    ensures { result = dict_keys_of l }",
                "  val function dict_values_prog (l: irlist) : irlist",
                "    ensures { result = dict_values_of l }",
                "  type py_dict_node",
                "  val function dict_keys_ast (s: py_dict_node) : irlist",
                "  val function dict_values_ast (s: py_dict_node) : irlist",
                "  (* _py_expr_listcomp/setcomp/dictcomp increment (self-tcb-reduction M5,"
                " C-bucket): the comprehension nodes — FIXED-CHILD (elt/key/value via disp)"
                " + the generators via the trusted `_comprehension_generators_to_ir` (an"
                " opaque emit_ir reader, like `_match_pattern_to_ir`). No child-list"
                " iteration. IrListComp/IrSetComp carry elt + generators; IrDictComp carries"
                " key + value + generators. *)",
                "  (* genexp-erasure-wall R2a: a GENERATOR expression had no Module-5 handler,"
                " so it reached the IR as UnknownPyExpr and its predicate + bound variable were"
                " destroyed. Same fixed-child shape as listcomp. *)",
                "  type py_genexp_node",
                "  val function genexp_elt_ast (s: py_genexp_node) : emit_ir",
                "  val function genexp_gens_ir (s: py_genexp_node) : emit_ir",
                "  type py_listcomp_node",
                "  val function listcomp_elt_ast (s: py_listcomp_node) : emit_ir",
                "  val function listcomp_gens_ir (s: py_listcomp_node) : emit_ir",
                "  type py_setcomp_node",
                "  val function setcomp_elt_ast (s: py_setcomp_node) : emit_ir",
                "  val function setcomp_gens_ir (s: py_setcomp_node) : emit_ir",
                "  type py_dictcomp_node",
                "  val function dictcomp_key_ast (s: py_dictcomp_node) : emit_ir",
                "  val function dictcomp_value_ast (s: py_dictcomp_node) : emit_ir",
                "  val function dictcomp_gens_ir (s: py_dictcomp_node) : emit_ir",
                "  (* base bool-recognizers (self-tcb-reduction M5, C-bucket): the"
                " `_is_typeddict_class`/`_is_namedtuple_class`/`_is_protocol_class` existence"
                " test `for b in node.bases: if isinstance(b, ast.Name/Attribute) and b.id/"
                " b.attr == <Base>: return True; return False`. `bases_has_name` is the"
                " CONCRETE recursive `any` fold over the bases irlist — a base MATCHES iff it"
                " is a Name/Attribute whose head name (`name_of`, which returns IrVar's name"
                " AND IrAttr's attr) equals the target — NOT an abstract length-only law."
                " `class_bases_ast` reads `node.bases`. Reuses the existing is_var/"
                " is_attribute/name_of discriminants (no new ctor). Gated on `_uses_stmt_ir`. *)",
                "  type py_classdef_node",
                "  val function class_bases_ast (n: py_classdef_node) : irlist",
                "  function bases_has_name (target: string) (l: irlist) : bool =",
                "    match l with",
                "    | ILNil -> false",
                "    | ILCons b t -> if (is_var b || is_attribute b)"
                " && (name_of b = target) then true else bases_has_name target t",
                "    end",
                "  val function bases_has_name_prog (target: string) (l: irlist) : bool",
                "    ensures { result = bases_has_name target l }",
                "  (* _is_final_annotation bool-recognizer (self-tcb-reduction M5, C-bucket):"
                " the FIXED-SHAPE test `isinstance(ann, ast.Name) and ann.id == \"Final\"` OR"
                " `isinstance(ann, ast.Subscript) and isinstance(ann.value, ast.Name) and"
                " ann.value.id == \"Final\"`. `is_final_ann` is the CONCRETE discriminant"
                " chain (is_var/name_of for the bare `Final`; is_sub/svalue_of/is_var/"
                " name_of for `Final[T]`). No child-list. Reuses existing discriminants. *)",
                "  function is_final_ann (ann: emit_ir) : bool =",
                "    (is_var ann && name_of ann = \"Final\")"
                " || (is_sub ann && is_var (svalue_of ann)"
                " && name_of (svalue_of ann) = \"Final\")",
                "  val function is_final_ann_prog (ann: emit_ir) : bool",
                "    ensures { result = is_final_ann ann }",
                "  let rec function boolop_fold (op: string) (acc: emit_ir) (rest: irlist)"
                " : emit_ir",
                "    variant { rest }",
                "  = match rest with",
                "    | ILNil -> acc",
                "    | ILCons v tl -> boolop_fold op"
                " (IrBinOp op acc (boolop_dispatch v)) tl",
                "    end",
                "",
                "  (* SFieldAssign/SArraySliceSet/STupleUnpack increment (self-tcb-reduction"
                " M5, C-bucket): the typed AST reader for `_py_stmt_assign`. `py_assign_node`"
                " models `ast.Assign`; `assign_target0_ast` reads `stmt.targets[0]` (the"
                " HEAD target, an emit_ir — Name/Attribute/Subscript/Tuple); `assign_value_ast`"
                " reads `stmt.value` (the RHS emit_ir). `symtab_mem` models the instance-state"
                " membership `target.value.id in self._cur_func_symtab` as an opaque"
                " name-keyed predicate (the symtab is runtime state; the membership RESULT is"
                " a sound abstract bool, deciding the named-base FieldAssign vs the module-"
                " global no-op). `sliceN_lower_of`/`sliceN_upper_of` project the IrSliceN"
                " OPTIONAL bounds (iropt_ir) for the `a[lo:hi] = v` ArraySliceSet branch."
                " Gated on `_uses_stmt_ir`. *)",
                "  type py_assign_node",
                "  val function assign_target0_ast (s: py_assign_node) : emit_ir",
                "  val function assign_value_ast (s: py_assign_node) : emit_ir",
                "  val function symtab_mem (key: string) : bool",
                "  let function sliceN_lower_of (e: emit_ir) : iropt_ir =",
                "    match e with IrSliceN lo _ _ -> lo | _ -> IrONone end",
                "  let function sliceN_upper_of (e: emit_ir) : iropt_ir =",
                "    match e with IrSliceN _ up _ -> up | _ -> IrONone end",
                "",
                "  (* The CONCRETE compaction of a Tuple exc_type `\"|\".join(n.id for n in"
                " h.type.elts if isinstance(n, ast.Name))`: `var_names_of` filters `is_var`"
                " + projects `name_of` over the MkTuple `elts` irlist; `join_pipe` inserts"
                " \"|\" BETWEEN the resulting names. NOT a length-only abstract law (the"
                " fable's vacuity trap) — a total structural recursion over the ALREADY-"
                " concrete `is_var`/`name_of` projectors. `pipe_join` is the program-level"
                " primitive the emitter emits (concat is logic-only in Why3), pinned by"
                " ensures to the EXACT concrete logic compaction `tuple_exc_type`. *)",
                "  (* the variadic-tuple discriminant + elts projector: `isinstance(h.type,"
                " ast.Tuple)` on the caught-exception type lowers to `is_mktuple` (the"
                " IrMkTupleN variadic ctor), `h.type.elts` to `elts_of` (its irlist"
                " payload). Gated on `_uses_stmt_ir` — only the mirror's `_py_stmt_try`"
                " compaction needs them, so the emit_ir theory of every OTHER file (and the"
                " whole corpus) stays byte-identical. *)",
                "  let function is_mktuple (e: emit_ir) : bool =",
                "    match e with IrMkTupleN _ -> true | _ -> false end",
                "  let function elts_of (e: emit_ir) : irlist =",
                "    match e with IrMkTupleN l -> l | _ -> ILNil end",
                "  function var_names_of (l: irlist) : strlist =",
                "    match l with",
                "    | ILNil -> SLNilS",
                "    | ILCons e rest -> if is_var e then SLConsS (name_of e)"
                " (var_names_of rest) else var_names_of rest",
                "    end",
                "  function join_pipe (l: strlist) : string =",
                "    match l with",
                "    | SLNilS -> \"\"",
                "    | SLConsS h t -> match t with"
                " | SLNilS -> h"
                " | SLConsS _ _ -> concat h (concat \"|\" (join_pipe t)) end",
                "    end",
                "  function tuple_exc_type (l: irlist) : string ="
                " join_pipe (var_names_of l)",
                "  val function pipe_join (l: irlist) : string",
                "    ensures { result = tuple_exc_type l }",
                "  (* STupleUnpack: the program-level primitive for `[elt.id for elt in"
                " target.elts if isinstance(elt, ast.Name)]` — the CONCRETE `var_names_of`"
                " strlist (filter is_var + project name_of), NOT the abstract length-only"
                " `list_content_comp_N` law (the fable's vacuity trap). Pinned by ensures to"
                " the concrete logic compaction. *)",
                "  val function var_names_prog (l: irlist) : strlist",
                "    ensures { result = var_names_of l }",
                "",
                "  (* The TYPED AST-input readers for `_py_stmt_try`: `py_try_node` models"
                " `ast.Try` (its `stmt` param), `ast_excepthandler` models an `ast."
                " ExceptHandler` element of `stmt.handlers`. These are OPAQUE deterministic"
                " AST projectors — the typed analogue of the trusted `iter_get`/`get_body`"
                " AST readers and the `self._py_stmts_to_ir` dispatcher (the Python AST is"
                " the untrusted INPUT; fidelity is about the OUTPUT STry/except_handler/"
                " compaction construction, which is concrete below). `eh_type_ast` returns"
                " the caught-exception type as an `iropt_ir` (`IrONone` = bare `except:`,"
                " `IrOSome t` = `except T`/`except (T1,T2)`); `eh_name_ast` the `as <n>`"
                " bind as `iropt_str`; the body readers return `array int` (the trusted"
                " `_py_stmts_to_ir` dispatcher's param type). Gated on `_uses_stmt_ir`. *)",
                "  type py_try_node",
                "  type ast_excepthandler",
                "  val function try_body_ast (s: py_try_node) : array int",
                "  val function try_handlers_ast (s: py_try_node) : seq ast_excepthandler",
                "  val function try_orelse_ast (s: py_try_node) : array int",
                "  val function try_finalbody_ast (s: py_try_node) : array int",
                "  val function eh_type_ast (h: ast_excepthandler) : iropt_ir",
                "  val function eh_name_ast (h: ast_excepthandler) : iropt_str",
                "  val function eh_body_ast (h: ast_excepthandler) : array int",
                "",
            ]) if self._uses_stmt_ir() else []),
            *(([
                "",
                "  (* pyast_stmt ADT (self-tcb-reduction giants, generic class-body lowering):"
                " the INPUT-side raw `ast.stmt` union a class-body iterator"
                " (`_collect_class_constants`) isinstance-dispatches over. `PS*` prefix"
                " (disjoint from the OUTPUT stmt_ir's SAssign). Carries emit_ir children (the"
                " already-lowered target/value/annotation exprs). `stmt_node_kind_of` +"
                " `is_K` discriminants + faithfulness lemmas (is_K <-> kind = \"K\") model the"
                " isinstance dispatch faithfully. Projectors `stmt_target0`/`stmt_value`/"
                " `stmt_annotation`/`def_name` read the children; `stmt_targets_len` the"
                " opaque `len(child.targets)` count. `psl` is the mutual-cons statement-list"
                " `node.body` iterates (the irlist precedent). `class_body_ast` reads the"
                " class-body psl; `ps_const_int` models the trusted `_const_int_value`;"
                " `ps_field_mem` the `target in field_names` membership. Gated on"
                " `_uses_pyast_stmt` -> corpus + every other mirror byte-identical. *)",
            ] + (["  type py_classdef_node"] if not self._uses_stmt_ir() else []) + [
                "  type pyast_stmt =",
                "    | PSAssign emit_ir emit_ir",
                "    | PSAnnAssign emit_ir emit_ir emit_ir",
                "    | PSClassDef string",
                "    | PSFunctionDef string",
                "    | PSOther",
                "  let function stmt_node_kind_of (s: pyast_stmt) : string =",
                "    match s with",
                "    | PSAssign _ _ -> \"Assign\"",
                "    | PSAnnAssign _ _ _ -> \"AnnAssign\"",
                "    | PSClassDef _ -> \"ClassDef\"",
                "    | PSFunctionDef _ -> \"FunctionDef\"",
                "    | PSOther -> \"Other\"",
                "    end",
                "  let predicate is_assign_node (s: pyast_stmt) ="
                " match s with PSAssign _ _ -> true | _ -> false end",
                "  let predicate is_annassign_node (s: pyast_stmt) ="
                " match s with PSAnnAssign _ _ _ -> true | _ -> false end",
                "  let predicate is_classdef_node (s: pyast_stmt) ="
                " match s with PSClassDef _ -> true | _ -> false end",
                "  let predicate is_functiondef_node (s: pyast_stmt) ="
                " match s with PSFunctionDef _ -> true | _ -> false end",
                "  lemma is_assign_faithful : forall s: pyast_stmt."
                " is_assign_node s <-> stmt_node_kind_of s = \"Assign\"",
                "  lemma is_annassign_faithful : forall s: pyast_stmt."
                " is_annassign_node s <-> stmt_node_kind_of s = \"AnnAssign\"",
                "  lemma is_classdef_faithful : forall s: pyast_stmt."
                " is_classdef_node s <-> stmt_node_kind_of s = \"ClassDef\"",
                "  lemma is_functiondef_faithful : forall s: pyast_stmt."
                " is_functiondef_node s <-> stmt_node_kind_of s = \"FunctionDef\"",
                "  let function stmt_target0 (s: pyast_stmt) : emit_ir =",
                "    match s with PSAssign t _ -> t | PSAnnAssign t _ _ -> t"
                " | _ -> IrOther \"\" end",
                "  let function stmt_value (s: pyast_stmt) : emit_ir =",
                "    match s with PSAssign _ v -> v | PSAnnAssign _ _ v -> v"
                " | _ -> IrOther \"\" end",
                "  let function stmt_annotation (s: pyast_stmt) : emit_ir =",
                "    match s with PSAnnAssign _ a _ -> a | _ -> IrOther \"\" end",
                "  let function def_name (s: pyast_stmt) : string =",
                "    match s with PSClassDef n -> n | PSFunctionDef n -> n | _ -> \"\" end",
                "  val function stmt_targets_len (s: pyast_stmt) : int",
                "  type psl = PSLNil | PSLCons pyast_stmt psl",
                "  let rec function psl_len (l: psl) : int ="
                " match l with PSLNil -> 0 | PSLCons _ t -> 1 + psl_len t end",
                "  let rec function psl_nth (i: int) (l: psl) : pyast_stmt",
                "    variant { l } =",
                "    match l with PSLNil -> PSOther"
                " | PSLCons h t -> if i <= 0 then h else psl_nth (i-1) t end",
                "  val function class_body_ast (n: py_classdef_node) : psl",
                "  val function ps_const_int (v: emit_ir) : option int",
                "  val function ps_field_mem (name: string) : bool",
                "  (* K2 convergence (self-tcb-reduction, nested-body + ast.walk dispatch):"
                " `stmt_body` reads the `.body` psl of a `pyast_stmt` LOCAL (the outer"
                " module-body loop var `stmt`, a ClassDef whose class body a nested"
                " `for cstmt in stmt.body` iterates); `ast_walk` is the faithful"
                " over-approximation of `ast.walk(<pyast_stmt local>)` — the recursive"
                " descendant enumeration as an opaque psl (consistent with `class_body_ast`"
                " opacity; the loop only isinstance-dispatches + reads projectors over each"
                " element, so an abstract psl is sound). Both are opaque `val function`s —"
                " NO new axiom. Gated WITH the block on `_uses_pyast_stmt`. *)",
                "  val function stmt_body (s: pyast_stmt) : psl",
                "  val function ast_walk (s: pyast_stmt) : psl",
            ] + ([
                "  (* J2/J3 convergence (self-tcb-reduction, module-body dispatch): the"
                " class-body giant generalized to `ast.Module` bodies. `py_module_node` is"
                " an `ast.Module` param whose `.body` reads the SAME shared `psl` cons-list"
                " (`_collect_typevar_registry` iterates `for stmt in node.body`). Distinct"
                " opaque AST-node type from py_classdef_node; reuses the whole pyast_stmt ADT"
                " + psl loop. Gated WITH the block on `_uses_pyast_stmt`. *)",
                "  type py_module_node",
                "  val function module_body_ast (n: py_module_node) : psl",
            ] if self._uses_pyast_module() else []) + [
                "",
            ]) if self._uses_pyast_stmt() else []),
            # L1 tparam reflection-node ADT (self-tcb-reduction, collector-family
            # unlock; getting-better/self-field-append-wall-impl.md §K5/§L1, K5 hand-
            # oracle scratchpad/k5_spike.mlw Z3-Valid + axiom-free). Models the PEP-695
            # `type_params` reflection the mirror's `_collect_type_params` dispatches
            # over: `type(tp).__name__` -> `tp_kind_of` (a NODE-KIND DISCRIMINANT, the
            # pyast_stmt/emit_ir precedent — NOT the dropped generic reflection);
            # `getattr(tp,"name")` -> `tp_name`; `getattr(tp,"bound")` -> `tp_bound`
            # (an emit_ir child, TypeVar only); the bound `isinstance`/`.id`/`.attr`
            # dispatch REUSES the existing emit_ir `is_var`/`is_attribute`/`name_of`
            # (K5-confirmed). `tparam_list` is a BESPOKE cons-list (TPNil/TPCons — NOT
            # seq, respecting the recorded seq non-strict-positivity wall);
            # `type_params_of` is an opaque `val function` (the `class_body_ast`
            # precedent, no new axiom). Gated on `_uses_tparam` (a `TParamNode`-annotated
            # param — a NEW sentinel name; no corpus program or other mirror carries it
            # -> the emit_ir theory stays byte-identical everywhere else). Axiom-free
            # (ADT + definitional projectors + the faithfulness lemmas; reuses the
            # emit_ir discriminants) -> ledger stays 3.
            *(([
                "",
                "  (* L1 tparam reflection-node ADT (self-tcb-reduction, collector-family"
                " unlock): the PEP-695 `type_params` node union `_collect_type_params`"
                " isinstance/type-name-dispatches over. `TP*` prefix (disjoint). TPTypeVar"
                " carries the bound sub-node as an emit_ir child (TypeVar only);"
                " ParamSpec/TypeVarTuple are bound-less. `tp_kind_of` maps"
                " `type(tp).__name__` to the kind discriminant (\"TypeVar\"/\"ParamSpec\"/"
                " \"TypeVarTuple\"); `tp_name` = `getattr(tp,\"name\")`; `tp_bound` ="
                " `getattr(tp,\"bound\")` (emit_ir); `is_K`<->`tp_kind_of=\"K\"`"
                " faithfulness lemmas model the reflection faithfully. The bound"
                " isinstance/`.id`/`.attr` dispatch reuses the existing emit_ir"
                " is_var/is_attribute/name_of. `tparam_list` is the bespoke cons-list"
                " `type_params_of` (an opaque val, class_body_ast precedent) yields."
                " Gated on `_uses_tparam` -> corpus + every other mirror byte-identical. *)",
                "  type tparam =",
                "    | TPTypeVar string emit_ir",
                "    | TPParamSpec string",
                "    | TPTypeVarTuple string",
                "  let function tp_kind_of (tp: tparam) : string =",
                "    match tp with",
                "    | TPTypeVar _ _ -> \"TypeVar\"",
                "    | TPParamSpec _ -> \"ParamSpec\"",
                "    | TPTypeVarTuple _ -> \"TypeVarTuple\"",
                "    end",
                "  let function tp_name (tp: tparam) : string =",
                "    match tp with TPTypeVar n _ -> n | TPParamSpec n -> n"
                " | TPTypeVarTuple n -> n end",
                "  let function tp_bound (tp: tparam) : emit_ir =",
                "    match tp with TPTypeVar _ b -> b | _ -> IrOther \"\" end",
                "  let predicate is_typevar (tp: tparam) ="
                " match tp with TPTypeVar _ _ -> true | _ -> false end",
                "  let predicate is_paramspec (tp: tparam) ="
                " match tp with TPParamSpec _ -> true | _ -> false end",
                "  let predicate is_typevartuple (tp: tparam) ="
                " match tp with TPTypeVarTuple _ -> true | _ -> false end",
                "  lemma is_typevar_faithful : forall tp: tparam."
                " is_typevar tp <-> tp_kind_of tp = \"TypeVar\"",
                "  lemma is_paramspec_faithful : forall tp: tparam."
                " is_paramspec tp <-> tp_kind_of tp = \"ParamSpec\"",
                "  lemma is_typevartuple_faithful : forall tp: tparam."
                " is_typevartuple tp <-> tp_kind_of tp = \"TypeVarTuple\"",
                "  type tparam_list = TPNil | TPCons tparam tparam_list",
                "  let rec function tpl_len (l: tparam_list) : int ="
                " match l with TPNil -> 0 | TPCons _ t -> 1 + tpl_len t end",
                "  let rec function tpl_nth (i: int) (l: tparam_list) : tparam",
                "    variant { l } =",
                "    match l with TPNil -> TPParamSpec \"\""
                " | TPCons h t -> if i <= 0 then h else tpl_nth (i-1) t end",
                "  type py_tparam_node",
                "  val function type_params_of (n: py_tparam_node) : tparam_list",
                # 7b (self-tcb-reduction L4b): `_collect_type_params`'s legacy `Generic[T]`
                # branch reflects on the SAME node as a ClassDef — `isinstance(node,
                # ast.ClassDef)` and `for b in node.bases`. `is_classdef_of` is the opaque
                # runtime-kind bool (the `symtab_mem` precedent, NO isinstance_op 0 0);
                # `bases_of` reads `node.bases` as an emit_ir `irlist` (the `class_bases_ast`
                # precedent, NO get_bases int fallback). Opaque vals -> NO new axiom.
                "  val function is_classdef_of (n: py_tparam_node) : bool",
                "  val function bases_of (n: py_tparam_node) : irlist",
                "",
            ]) if self._uses_tparam() else []),
        ]

    def _uses_tparam(self) -> bool:
        """L1 tparam reflection-node ADT (self-tcb-reduction, collector-family unlock):
        True iff some function in this file has a param/local annotated with the
        `TParamNode` sentinel type — the node whose `.type_params` the PEP-695 reflection
        loop iterates (`for tp in <node>.type_params`). Only then are the `tparam` ADT +
        `tparam_list` + `tp_kind_of`/`tp_name`/`tp_bound` projectors + `type_params_of`
        emitted into the emit_ir theory, so the certified tparam value model stays OUT of
        every other mirror's SMT context and the whole reference corpus (`TParamNode` is a
        NEW sentinel name; no corpus program or other mirror carries it -> byte-identical).
        The byte-inert gate, mirroring `_uses_call_kw`'s `CallKw` sentinel. Cached."""
        cached = getattr(self, "_uses_tparam_cache", None)
        if cached is not None:
            return cached
        result = any(
            v == "TParamNode"
            for fn in self.ir.get("functions", []) or []
            for v in (fn.get("symbol_table", {}) or {}).values()
        ) or any(
            v == "TParamNode"
            for fn in self.ir.get("functions", []) or []
            for v in (fn.get("param_annotations", {}) or {}).values()
        )
        self._uses_tparam_cache = result
        return result

    def _uses_pyast_stmt(self) -> bool:
        """pyast_stmt ADT (self-tcb-reduction giants): True iff some function in this file
        iterates a class-body — `for <x> in <p>.body` where `<p>` is a parameter annotated
        `ast.ClassDef` — the shape the generic class-body lowering handles (piece 2/3). Only
        the Module5 mirror's `_collect_class_constants` produces it, so the pyast_stmt theory
        + psl loop stay OUT of every other mirror's SMT context and the whole corpus
        (byte-identical). Cached."""
        cached = getattr(self, "_uses_pyast_stmt_cache", None)
        if cached is not None:
            return cached
        result = any(
            self._pyast_classdef_body_params(fn) or self._pyast_module_body_params(fn)
            for fn in self.ir.get("functions", []) or [])
        self._uses_pyast_stmt_cache = result
        return result

    def _uses_pyast_module(self) -> bool:
        """J2/J3 convergence (self-tcb-reduction, module-body dispatch): True iff some
        function iterates an `ast.Module` param's `.body` (`for stmt in node.body`). Only
        then are `type py_module_node` + `val module_body_ast` emitted (with the shared
        pyast_stmt block). Only the Module5 mirror's `_collect_typevar_registry` produces
        this shape -> byte-inert everywhere else. Cached."""
        cached = getattr(self, "_uses_pyast_module_cache", None)
        if cached is not None:
            return cached
        result = any(
            self._pyast_module_body_params(fn)
            for fn in self.ir.get("functions", []) or [])
        self._uses_pyast_module_cache = result
        return result

    def _pyast_module_body_params(self, func: Dict[str, Any]) -> Set[str]:
        """The parameters of `func` that are (a) annotated `ast.Module` AND (b) iterated
        via `for <x> in <param>.body`. These become `py_module_node` params whose `.body`
        reads the shared `module_body_ast` psl (module-body dispatch). Parallel to
        `_pyast_classdef_body_params`; the ONLY difference is the "Module" node tag."""
        return self._pyast_bodyparams_for_tag(func, "Module")

    def _pyast_classdef_body_params(self, func: Dict[str, Any]) -> Set[str]:
        """The parameters of `func` that are (a) annotated `ast.ClassDef` AND (b) iterated
        via `for <x> in <param>.body` somewhere in the body. These become `py_classdef_node`
        params whose `.body` reads the `class_body_ast` psl (generic class-body lowering)."""
        return self._pyast_bodyparams_for_tag(func, "ClassDef")

    def _pyast_bodyparams_for_tag(self, func: Dict[str, Any], tag: str) -> Set[str]:
        """Shared helper: params annotated `ast.<tag>` AND iterated via `for <x> in
        <param>.body`. `tag`="ClassDef" -> py_classdef_node/class_body_ast; "Module" ->
        py_module_node/module_body_ast."""
        pann = func.get("param_ast_node_types") or {}
        tag_params = {
            p for p, a in pann.items()
            if isinstance(a, str) and a == tag}
        if not tag_params:
            return set()
        found: Set[str] = set()

        def walk(stmts: Any) -> None:
            if not isinstance(stmts, list):
                return
            for st in stmts:
                if not isinstance(st, dict):
                    continue
                if st.get("stmt") in ("For", "ForStmt"):
                    it = st.get("iter", {})
                    if (isinstance(it, dict) and it.get("type") == "Attribute"
                            and it.get("attr") == "body"):
                        obj = it.get("object", {})
                        if (isinstance(obj, dict) and obj.get("type") == "Var"
                                and obj.get("name") in tag_params):
                            found.add(obj["name"])
                for v in st.values():
                    if isinstance(v, list):
                        walk(v)
                    elif isinstance(v, dict):
                        walk(v.get("body")) if isinstance(v.get("body"), list) else None
        walk(func.get("body"))
        return found

    # self-tcb-reduction family-B (parser clause parsers): the CSL-AST CONTRACT-CLAUSE
    # node kinds the recursive-descent `_ContractParser._parse_*` methods construct
    # (`ProofDecl(prover, qualname)`, `ClassInvariant(expr)`, `LoopInvariant(expr)`,
    # `LoopVariant(expr)`, `RaisesDecl(exc, cond)`, ...). Distinct from the EXPR family
    # (IrBinOp/IrVar/...) which appears inside ordinary contract expressions and thus
    # reaches the corpus — these clause kinds appear ONLY as a parser method's returned
    # node, never as a sub-expression of a corpus contract. Lowercased (the
    # `_record_types` key convention).
    _CLAUSE_IR_NODES = (
        "ProofDecl", "ClassInvariant", "LoopInvariant", "LoopVariant",
        "RaisesDecl",
        # self-tcb-reduction family-B (LIST-append clause parsers): the clause node
        # kinds whose sole field is a `list string` built by an `.append` loop
        # (`ComposeFromDecl(mixins)`, `ConformsToDecl(protocols)`, `LockOrder(order)` —
        # `_parse_compose_from`/`_parse_conforms_to`/`_parse_lock_order`).
        "ComposeFromDecl", "ConformsToDecl", "LockOrder",
    )

    def _uses_clause_ir(self) -> bool:
        """self-tcb-reduction family-B: True iff THIS file DEFINES one of the parser
        contract-clause node classes (`_CLAUSE_IR_NODES`) as a `record` type_decl. Only
        `frontend/Module2_Parser` defines them (both live and mirror), and it is the SOLE
        file that constructs them, so gating the clause `emit_ir` ctors + their `kind_of`
        arms on this keeps the emit_ir theory BYTE-IDENTICAL in every other mirror AND the
        whole reference corpus (no corpus program declares a `@mutable_state` class, let
        alone one of these clause classes). Reads `self.ir['type_decls']` DIRECTLY (the
        `_record_types` dict is populated LATE — during preamble record-decl emission,
        after the emit_ir theory is first realized — so a `_record_types` probe caches a
        false negative). The `_uses_call_kw` byte-inert-gate pattern verbatim. Cached."""
        cached = getattr(self, "_uses_clause_ir_cache", None)
        if cached is not None:
            return cached
        clause = set(self._CLAUSE_IR_NODES)
        result = any(
            td.get("kind") == "record" and td.get("name") in clause
            for td in (self.ir.get("type_decls", []) or []))
        self._uses_clause_ir_cache = result
        return result

    def _uses_stmt_ir(self) -> bool:
        """stmt-list-append-mutation wall (self-tcb-reduction M5, C-bucket): True iff some
        function in this file appends a statement-IR node — a `<list>.append({"stmt": K})`
        with a STRING-literal `"stmt"` kind — to a list parameter. That syntactic shape is
        the sole discriminator of the mutable-ref stmt-append convention; only the Module5
        mirror's `_py_stmt_*` handlers (and the wall reference drivers) produce it, so the
        stmt_ir theory block + the `ref (seq stmt_ir)` param typing stay OUT of every other
        mirror's SMT context and the whole corpus (byte-identical). Cached."""
        cached = getattr(self, "_uses_stmt_ir_cache", None)
        if cached is not None:
            return cached
        result = any(
            self._stmt_seq_append_params(fn)
            for fn in self.ir.get("functions", []) or []) \
            or self._uses_stmt_return_recogniser()
        self._uses_stmt_ir_cache = result
        return result

    def _uses_stmt_return_recogniser(self) -> bool:
        """tree-walk-wall-impl.md (self-tcb-reduction, GATE-S): True iff some
        function in this file is a `_body_has_return`-shaped stmt_ir tree-walk
        existence fold (`recognize_stmt_has`). It READS a statement tree (no
        `.append`), so `_uses_stmt_ir`'s append-shape probe misses it — this fires
        the SAME certified stmt_ir ADT + `size_*` theory emission the recogniser's
        `stmt_has`/`sl_has`/`hl_has`/`mcl_has` group references. Corpus-inert: only
        the Module5/core_ir_semantic mirror's NoReturn walkers have this shape, so
        every corpus program stays byte-identical. Cached."""
        cached = getattr(self, "_uses_stmt_return_recogniser_cache", None)
        if cached is not None:
            return cached
        from module6_whyml.generic_fold import recognize_stmt_has
        result = any(
            recognize_stmt_has(fn) is not None
            for fn in self.ir.get("functions", []) or [])
        self._uses_stmt_return_recogniser_cache = result
        return result

    def _uses_null_byte_num_reader(self) -> bool:
        """self-tcb-reduction (_is_null_byte_lit): True iff this file defines a
        `_is_null_byte_lit` function — the sole consumer of the `num_of` integer-value
        reader (which projects IrNum's int payload so `elts[0].get("value") == 0` reads
        faithfully). No corpus program defines a function by that name, so gating `num_of`'s
        emission on this keeps the emit_ir theory every corpus file emits byte-identical.
        Cached."""
        cached = getattr(self, "_uses_null_byte_num_reader_cache", None)
        if cached is not None:
            return cached
        result = any(
            str(fn.get("name", "")).endswith("_is_null_byte_lit")
            for fn in self.ir.get("functions", []) or [])
        self._uses_null_byte_num_reader_cache = result
        return result

    def _uses_call_kw(self) -> bool:
        """J1 Call-internals value model (self-tcb-reduction, callinternals-oracle.mlw
        Gate-R CONFIRMED): True iff some function in this file has a param/local annotated
        with the `CallKw` sentinel type — the receiving context that needs keyword-node
        inspection (`call.keywords` / `for kw in ...` / `kw.arg` / `kw.value.id`). Only
        then are the standalone `kwval`/`keyword`/`keyword_list` types + the `IrCallKw`
        ctor + its projectors emitted into the emit_ir theory, so the certified Call-
        internals value model stays OUT of every other mirror's SMT context and the whole
        reference corpus (`CallKw` is a NEW sentinel name; no corpus program or other
        mirror carries it → byte-identical). The byte-inert gate, mirroring `_uses_pyval`'s
        `Dict[str, PyVal]` sentinel. Cached."""
        cached = getattr(self, "_uses_call_kw_cache", None)
        if cached is not None:
            return cached
        result = any(
            v == "CallKw"
            for fn in self.ir.get("functions", []) or []
            for v in (fn.get("symbol_table", {}) or {}).values()
        ) or any(
            v == "CallKw"
            for fn in self.ir.get("functions", []) or []
            for v in (fn.get("param_annotations", {}) or {}).values()
        ) or any(
            # J2/J3 convergence: a `for <kw> in <call>.keywords` loop is the receiving
            # context that needs the keyword-node model (the `_collect_typevar_registry`
            # shape). No corpus program iterates `.keywords` -> byte-inert.
            self._has_keywords_iteration(fn)
            for fn in self.ir.get("functions", []) or [])
        self._uses_call_kw_cache = result
        return result

    def _has_keywords_iteration(self, func: Dict[str, Any]) -> bool:
        """J2/J3: True iff `func` iterates `for <x> in <y>.keywords` — the syntactic
        trigger for the Call-internals keyword model. Byte-inert (no corpus shape)."""
        found = [False]

        def rec(n: Any) -> None:
            if found[0]:
                return
            if isinstance(n, dict):
                if n.get("stmt") in ("For", "ForStmt"):
                    _it = n.get("iter", {})
                    if (isinstance(_it, dict) and _it.get("type") == "Attribute"
                            and _it.get("attr") == "keywords"):
                        found[0] = True
                        return
                for x in n.values():
                    rec(x)
            elif isinstance(n, list):
                for x in n:
                    rec(x)
        rec(func.get("body"))
        return found[0]

    def _uses_pyval(self) -> bool:
        """pyval heterogeneous value model (self-tcb-reduction, Tier-5 value-model wall):
        True iff some function in this file has a dict typed `Dict[str, PyVal]` — its
        `dict_value_types` carries the `"hval"` sentinel (set by Module5
        `_m5_get_dict_value_type` on a `Dict[str, PyVal]` annotation). Only then is the
        `hval` sum + `map string (option hval)` theory emitted, so the certified
        heterogeneous value variant stays OUT of every other mirror's SMT context and the
        whole reference corpus (no `Dict[str, PyVal]` annotation there → byte-identical).
        The value carrier `PyVal` is a NEW sentinel type name; this is the byte-inert gate
        (the `_uses_pyconst_val`/`_uses_pyast_stmt` precedent). Cached."""
        cached = getattr(self, "_uses_pyval_cache", None)
        if cached is not None:
            return cached
        # A dict value type is the bare `hval` sentinel (`Dict[str, PyVal]`) OR a
        # NESTED hval map (`Dict[str, Dict[str, PyVal]]` -> `map string (option hval)`,
        # J2/J3 convergence). Both need the `hval` theory. `hval` is a NEW type name
        # absent from the corpus -> byte-inert.
        result = any(
            isinstance(v, str) and (v == "hval" or "option hval" in v)
            for fn in self.ir.get("functions", []) or []
            for v in (fn.get("dict_value_types", {}) or {}).values())
        # K1 (seq-pyval self-field append): a `List[PyVal]`/`List[Dict[str, PyVal]]`
        # record field (value_type == "hval") lowers to `seq hval` and so ALSO needs
        # the `hval` theory in scope — fire the gate even when no function-local
        # `Dict[str, PyVal]` annotation is present. Corpus has no such field -> byte-inert.
        result = result or any(
            f.get("value_type") == "hval" or f.get("name") == "_record_types"
            for td in self.ir.get("type_decls", []) or []
            for f in td.get("fields", []) or [])
        # K4/#6 (local/return-position seq-pyval + scalar pyval return): a function that
        # RETURNS `seq hval` (`-> List[Dict[str, PyVal]]`, return_value_type "hval") or
        # a scalar `hval` (`-> PyVal`, return_annotation "PyVal") needs the `hval`
        # theory in scope even when no pyval FIELD is present. Corpus has neither
        # annotation -> byte-inert.
        result = result or any(
            fn.get("return_value_type") == "hval"
            or fn.get("return_annotation") == "PyVal"
            for fn in self.ir.get("functions", []) or [])
        self._uses_pyval_cache = result
        return result

    def _emit_pyval_theory(self) -> List[str]:
        """hval heterogeneous value model (self-tcb-reduction, Tier-5 value-model wall):
        the CERTIFIED faithful value variant for a heterogeneous `Dict[str, Any]`
        (`_render_match_pattern`-shaped) — proven axiom-free by the fable oracle
        (`getting-better/pyval-oracle.mlw`, Z3 Valid) and co-landed with the Rocq/Lean
        `Phase2f_PyVal` cert. Emit EXACTLY the oracle's shape (renamed carrier):

          type hval = HStr string | HInt int | HArr hval_list
                    | HMap (map string (option hval)) | HNode hval
          with hval_list = HNil | HCons hval hval_list

        NAME COLLISION (fixed here): the OLDER D1/R-A generic-fold value model
        (`_pydict_theory_lines`) also declares `type pyval` with `PInt|PStr|PBool|PNone|
        PList|PDict`. A file that needs BOTH gates (the first is `frontend/ir_resolve.py`,
        which imports Module3_Weaver AND Module5_IREmitter) emitted two clashing
        declarations — `Symbol PStr is already defined in the current scope`. The two
        types are NOT mergeable (the generic-fold `pv_size`/`size_pos` measure pack
        cannot extend over `HMap`'s map codomain), so this Tier-5 family carries the
        DISJOINT `h*` names and both theories now coexist in one scope.

        `HArr` recurses through the BESPOKE `hval_list` (HNil/HCons), NOT `seq hval` —
        Why3 rejects `seq` recursion as a non-strictly-positive occurrence (the hard
        refinement from Gate R). `HMap (map string (option hval))` is accepted (hval
        sits in the positive arrow codomain). Structural mutual recursion, NO `variant`
        clause (the `irlist`/`stmt_list` fold precedent — Why3 emits no termination VC).
        `size`/`size_pos` are the cert-side measure ONLY (no frontier fold needs them);
        they are NOT emitted here (kept out of every VC's SMT context). Gated on
        `_uses_pyval` → corpus + every other mirror byte-identical."""
        return [
            "  (* hval heterogeneous value model (self-tcb-reduction, Tier-5"
            " value-model wall): the faithful value carrier for a heterogeneous"
            " Python `Dict[str, Any]` — HStr/HInt/HArr/HMap/HNode. Proven axiom-free by"
            " the fable oracle (getting-better/pyval-oracle.mlw, Z3 Valid); co-landed with"
            " the Rocq/Lean Phase2f_PyVal cert. The `h*` names are DISJOINT from the older"
            " D1/R-A generic-fold `pyval`/`PStr` family (_pydict_theory_lines) so both"
            " value models can coexist in one scope. HArr recurses through the BESPOKE"
            " `hval_list` (HNil/HCons), NOT `seq hval` (Why3 rejects `seq` recursion as"
            " non-strictly-positive). R3: HMap's carrier is the BESPOKE assoc list"
            " `hpairs` (PNil/PCons), NOT a `map string (option hval)` — the map was"
            " non-iterable so `.values()` could not fold; the assoc list keeps the"
            " recursion structural and makes the read a terminating lookup fold"
            " (`pairs_get`). Structural mutual recursion, NO `variant` clause. Gated on"
            " `_uses_pyval` -> corpus byte-identical. The abstract-val insert point"
            " (`_find_abstract_val_insert_idx`, which skips `with`/`invariant`/`by` but"
            " NOT `|` arm lines) lands AFTER the whole mutual group + `pairs_get`. *)",
            "  type hval = HStr string | HInt int | HArr hval_list"
            " | HMap hpairs | HNode hval",
            "  with hval_list = HNil | HCons hval hval_list",
            "  with hpairs = PNil | PCons string hval hpairs",
            "  (* R3 carrier read: `.values()`-foldable lookup over the assoc list"
            " (the map carrier was non-iterable). Build PREPENDS a binding (PCons)."
            " A `let rec function` (usable in program `let` bindings — where the reads"
            " occur); `variant { p }` gives structural termination over the assoc-list"
            " cons. The key test is the opaque program primitive `hpairs_key_eq` (Why3"
            " has no native program string `=`; disjoint from the str-set `pystr_eq`);"
            " the DECIDABLE key equality + non-vacuity is certified in Phase2f_PyVal. *)",
            "  val hpairs_key_eq (a b: string) : bool",
            "  let rec function pairs_get (p: hpairs) (k: string) : option hval",
            "    variant { p }",
            "    = match p with",
            "      | PNil -> None",
            "      | PCons k' v t -> if hpairs_key_eq k k' then Some v else pairs_get t k",
            "      end",
            "  (* hval-retype (self-tcb-reduction Tier-5): project the string carrier out"
            " of an `hval` — the `HStr s` payload, else the empty string. A `let function`"
            " (usable in program `let`/guard positions, where the record-registry scan's"
            " `info.get(\"whyml_name\") == cls` compare + the Optional[str] return occur)."
            " Descends the REAL hval structure (non-vacuous), NOT an abstract reader. *)",
            "  let function hstr_of (h: hval) : string"
            " = match h with HStr s -> s | _ -> \"\" end",
            "  (* hval-retype (self-tcb-reduction Tier-5): the abstract `.values()`"
            " iterator over a `map string (option hval)` field — a native Why3 `map` is"
            " not finitely iterable, so the ENUMERATION is over-approximated (arbitrary"
            " length, arbitrary element), but each element is a REAL `hval` whose `.get`"
            " reads descend the actual structure via `pairs_get` (non-vacuous). Declared"
            " in the theory (not late via `_add_abstract_op`) so the decl is always in"
            " scope before the loop use, across the proof + vacuity re-emission paths. *)",
            "  (* LOGIC `function`s (not program `val`s) so `hval_values_len` is usable in"
            " the loop `variant` term (a logic context) — exactly like the psl-loop"
            " `psl_len`. Uninterpreted + total + effect-free, so also usable in the"
            " program while-condition + element `let`. NO axiom (the variant's `0 <=`"
            " bound falls out of the loop condition `idx < len`) -> ledger stays 3. *)",
            "  val function hval_values_len (m: map string (option hval)) : int",
            "  val function hval_values_get (m: map string (option hval)) (i: int) : hval",
            "",
        ]

    @staticmethod
    def _str_set_locals_of(func: Dict[str, Any]) -> Set[str]:
        """set-value-model-wall (self-tcb-reduction, Tier-5): the set of body locals
        of `func` that are an EMITTER-LOCAL `Set[str]` value — a local annotated
        `Set[str]` (`set_value_types[v] == "string"`) AND initialized with a bare
        `set()` call (`v = set()`) somewhere in the body. BOTH conditions are
        required so the corpus stays byte-identical: 0775's `s: Set[str] = None`
        (no `= set()`) and 0823/0833's `Set[int]` (element not "string") never
        qualify. Returns the empty set for every corpus function -> byte-inert.

        These locals lower to the executable `set.SetApp[string]` clone (`scope
        StrSet` in the preamble): `set()` -> `StrSet.empty ()`, `.add(x)` ->
        `StrSet.add x !s`, `x in s`/`x not in s` -> `StrSet.mem`/`not StrSet.mem`
        (a program bool guard). NO set-non-membership proof obligation is ever
        emitted (that times out — see set-value-model-wall-response.md §4)."""
        svt = func.get("set_value_types", {}) or {}
        candidates = {v for v, t in svt.items() if t == "string"}
        if not candidates:
            return set()
        found: Set[str] = set()

        def _is_empty_set_call(v: Any) -> bool:
            return (isinstance(v, dict) and v.get("type") == "Call"
                    and v.get("func") == "set" and not v.get("args"))

        def _walk(node: Any) -> None:
            if isinstance(node, dict):
                if (node.get("stmt") == "Assign"
                        and node.get("target") in candidates
                        and _is_empty_set_call(node.get("value"))):
                    found.add(node["target"])
                for _k in ("body", "orelse", "finalbody", "handlers"):
                    _v = node.get(_k)
                    if isinstance(_v, list):
                        _walk(_v)
            elif isinstance(node, list):
                for _s in node:
                    _walk(_s)

        _walk(func.get("body", []))
        return found

    def _uses_str_set(self) -> bool:
        """set-value-model-wall (self-tcb-reduction, Tier-5 value-model wall): True
        iff SOME function in this file has an emitter-local `Set[str]` value (an
        annotated `Set[str]` local initialized `= set()`; see `_str_set_locals_of`).
        Only then is the executable `set.SetApp[string]` clone (`scope StrSet`,
        `_emit_str_set_theory`) emitted, so the set theory stays OUT of every other
        mirror's SMT context and the whole reference corpus (no `Set[str] = set()`
        local there -> byte-identical). The `set.SetApp`/`set.Fset` theories are
        trusted Why3 stdlib and the string-eq `val` is a decidable primitive — NO
        project axiom is added (the ledger stays 3)."""
        cached = getattr(self, "_uses_str_set_cache", None)
        if cached is not None:
            return cached
        result = any(self._str_set_locals_of(fn)
                     for fn in self.ir.get("functions", []) or [])
        self._uses_str_set_cache = result
        return result

    def _uses_const_reflect(self) -> bool:
        """const-reflection value model (self-tcb-reduction, Tier-5 value-model wall;
        L1/L4a infra-witness): True iff SOME function in this file reflects on an emit_ir
        CONSTANT node via the tuple-of-types test `isinstance(<x>.value, (int, float))` —
        the numeric-Constant discriminant shape shared by `_collect_class_fields` /
        `_synthesize_*`. Only then are the `is_constant`/`is_num_or_float` COMPOUND
        discriminants (spanning the existing IrNum/IrNumF/IrStr/IrBoolC/IrNone const
        leaves) + the `num_of` int projector emitted into the emit_ir theory, so the
        const-reflection recognisers stay OUT of every other mirror's SMT context and the
        whole reference corpus (no `isinstance(_, (int, float))` there → byte-identical).
        The three lowerings are axiom-free `let function`s over EXISTING emit_ir leaves +
        the pre-existing `num_of` — NO new ADT/cert, ledger stays 3. Cached."""
        cached = getattr(self, "_uses_const_reflect_cache", None)
        if cached is not None:
            return cached
        result = any(
            self._has_num_or_float_isinstance(fn)
            for fn in self.ir.get("functions", []) or [])
        self._uses_const_reflect_cache = result
        return result

    def _has_num_or_float_isinstance(self, func: Dict[str, Any]) -> bool:
        """const-reflection: True iff `func` contains the const-reflection numeric test
        `isinstance(<x>.value, (int, float))` — an isinstance Call whose SECOND arg is the
        `(int, float)` tuple AND whose FIRST arg is a `.value` ATTRIBUTE read (the
        const-node value projection). Narrowing to the `.value`-attribute shape (exactly
        the `is_num_or_float` recogniser's trigger, expressions.py branch B) EXCLUDES a
        bare runtime `isinstance(v, (int, float))` value check on a plain scalar, so the
        gate fires only where the recogniser actually rewrites. Byte-inert (no corpus
        program reflects on a const node's `.value` this way)."""
        found = [False]

        def rec(n: Any) -> None:
            if found[0]:
                return
            if isinstance(n, dict):
                if (n.get("type") == "Call" and n.get("func") == "isinstance"):
                    _args = n.get("args") or []
                    _a0 = _args[0] if _args else None
                    if (len(_args) == 2 and self._is_int_float_tuple(_args[1])
                            and isinstance(_a0, dict)
                            and _a0.get("type") == "Attribute"
                            and _a0.get("attr") == "value"):
                        found[0] = True
                        return
                for x in n.values():
                    rec(x)
            elif isinstance(n, list):
                for x in n:
                    rec(x)
        rec(func.get("body"))
        return found[0]

    @staticmethod
    def _is_int_float_tuple(ir: Any) -> bool:
        """True iff `ir` is the tuple literal `(int, float)` — exactly two `Var` arms
        named `int` and `float` (the `isinstance(_, (int, float))` numeric class set)."""
        if not (isinstance(ir, dict) and ir.get("type") in ("Tuple", "MkTuple")):
            return False
        elts = ir.get("elts") or []
        if len(elts) != 2:
            return False
        names = {e.get("name") for e in elts
                 if isinstance(e, dict) and e.get("type") == "Var"}
        return names == {"int", "float"}

    def _emit_str_set_theory(self) -> List[str]:
        """set-value-model-wall (self-tcb-reduction, Tier-5): the EXECUTABLE
        emitter-local `Set[str]` value model — a `set.SetApp` clone over `string`,
        emitted as a nested `scope StrSet` so its `empty`/`add`/`mem`/`set` symbols
        do NOT collide with `list.Mem.mem`/`list.Append` in the flat program module.

        Proven axiom-free by the fable oracle (getting-better/set-oracle.mlw, Z3
        Valid: mem/dedup goals Valid, evil-twin non-vacuous, `eq'refn'vc` Valid).
        `set.SetApp`/`set.Fset` are trusted Why3 stdlib (their axioms are NOT
        PyCSL `_AXIOM_REGISTRY` entries — the ledger stays 3). `eq_str` is a
        DECIDABLE program-level string equality primitive (Python `s1 == s2`),
        NOT a project axiom — its refinement VC discharges (Valid).

        A `set()` lowers to `StrSet.empty ()` (`ref StrSet.set`, NOT `ref 0`),
        `s.add(x)` to `s := StrSet.add x !s`, `s |= t` to `s := StrSet.union !s t`
        (statements.py `_handle_augassign_stmt`; `union` is a plain `SetApp` val, no
        new axiom), and `x in s`/`x not in s` to a
        PROGRAM BOOL `StrSet.mem`/`not (StrSet.mem …)` guard. CRITICAL: NO
        set-non-membership assert/ensures is ever emitted (`assert { not (Fset.mem
        …) }` times out through the abstract set layer — see
        set-value-model-wall-response.md §4); the fixed type-safety + frame
        contract shape (`ensures True`) carries no such obligation. Gated on
        `_uses_str_set` -> corpus + every other mirror byte-identical."""
        return [
            "  (* set-value-model-wall (self-tcb-reduction, Tier-5 value-model wall):"
            " the EXECUTABLE emitter-local `Set[str]` value model — a `set.SetApp`"
            " clone over `string`. Nested `scope` so `empty`/`add`/`mem`/`set` do"
            " NOT collide with list.Mem/list.Append in the flat program module."
            " Proven axiom-free by getting-better/set-oracle.mlw (Z3 Valid). `eq_str`"
            " is a decidable program string-equality PRIMITIVE (Python `==`), NOT a"
            " project axiom — its refinement VC discharges. `set.SetApp`/`set.Fset`"
            " are trusted Why3 stdlib (NOT `_AXIOM_REGISTRY` entries) — the ledger"
            " stays 3. `set()`->`StrSet.empty ()`, `.add`->`StrSet.add`,"
            " `in`/`not in`->a PROGRAM BOOL `StrSet.mem`/`not StrSet.mem` guard; NO"
            " set-non-membership proof obligation is ever emitted (it times out). *)",
            "  scope StrSet",
            "    use string.String",
            "    val eq_str (x y: string) : bool ensures { result <-> x = y }",
            "    clone export set.SetApp with type elt = string, val eq = eq_str, axiom .",
            "  end",
            "",
        ]

    def _uses_pyconst_val(self) -> bool:
        """pyconst_val value-variant ADT (self-tcb-reduction M5, B-bucket): True iff this
        file actually harvested a Constant record — a `pyconst_val`-typed field is present in
        some `type_decl`. Only then is the real-truncation wrapper `real_trunc` (and its
        `use real.Truncate`) emitted, so the real-arithmetic axioms stay OUT of every other
        full-theory mirror's SMT context. The pure pyconst_val type + its non-real accessors +
        `bytes_content_comp` remain unconditional (axiom-free, cheap, unused-val-inert)."""
        for td in self.ir.get("type_decls", []) or []:
            for f in td.get("fields", []) or []:
                if f.get("type") == "PyConstVal":
                    return True
        return False

    def _reserved_exprir_symbols(self) -> Set[str]:
        """field-label/emit_ir-symbol collision fix: the set of top-level WhyML
        symbol names the `emit_ir` ADT theory (`_emit_exprir_theory`) declares —
        `let (rec) function` names, `val` declarations, `lemma` names, and inline
        record field labels (e.g. `sharedvar`'s `sv_name`/`sv_mutex`) all share
        Why3's global per-module namespace. A record field with one of these
        names (`size`, `kind_of`, `is_binop`, `left_of`, …) collides exactly like
        two records sharing a field — `_field_label`'s existing ambiguous-field
        qualification handles that shape once the name is registered here.

        Derived by parsing `_emit_exprir_theory()`'s OWN emitted text (not a
        hand-maintained duplicate list), so this set can never drift out of sync
        with the theory it protects against. Cached: the theory text is static
        per instance."""
        cached = getattr(self, "_reserved_exprir_symbols_cache", None)
        if cached is not None:
            return cached
        text = "\n".join(self._emit_exprir_theory())
        names: Set[str] = set()
        names.update(re.findall(r"\blet\s+(?:rec\s+)?function\s+(\w+)", text))
        names.update(re.findall(r"\bval\s+(\w+)", text))
        names.update(re.findall(r"\blemma\s+(\w+)", text))
        # inline record types declared within the theory (e.g. `sharedvar`) —
        # capture their field labels too.
        for rec_body in re.findall(r"\{([^{}]*)\}", text):
            names.update(re.findall(r"(\w+)\s*:", rec_body))
        self._reserved_exprir_symbols_cache = names
        return names

    # ------------------------------------------------------------------
    # theory-tailoring — minimal emit_ir for opaque-use mirrors
    # ------------------------------------------------------------------
    # The full `_emit_exprir_theory` (~80-ctor sum + kind_of + every
    # projector/discriminant + the recursive `size` + its size-decrease
    # LEMMAS + irlist/iropt/irnth/irlen) is emitted MONOLITHICALLY into every
    # mirror whose class is @mutable_state OR that carries an emit_ir param.
    # But some mirrors use emit_ir PURELY OPAQUELY — they pass emit_ir
    # params/locals to `trusted` `val`s and never CONSTRUCT a real IR-node
    # ctor nor PROJECT one (kind_of/left_of/size/is_*/irnth/...) in any PROVEN
    # (non-`trusted`) body. Those mirrors only need `type emit_ir` to EXIST (so
    # opaque params/locals/record-fields typecheck and the `IrOther ""`
    # absent-sentinel constructs) — not the 80-ctor theory. Emitting the
    # minimal surface for them keeps every VC's SMT context small, so they
    # prove ~4x faster. SOUND: each mirror is proven independently against its
    # OWN emit_ir, and a single-ctor emit_ir is sound for opaque use. This does
    # NOT change any conversion (count is unchanged) — pure emission
    # performance headroom.
    #
    # The RICH/OPAQUE decision is made by an EXPLICIT class-name ALLOW-LIST
    # (`_TAILOR_OPAQUE_MIRROR_CLASSES` in Module6_WhyMLTranspiler — currently
    # just `StatementEmissionMixin`; `ControlFlowStmtMixin` is NOT opaque, it
    # applies `svalue_of`, so it keeps the FULL theory) gated in
    # `_transpile` — corpus programs never define these emitter mixin classes,
    # so the tailoring is corpus-inert BY CONSTRUCTION (every corpus program
    # keeps the full theory / stays byte-identical). This deliberately does NOT
    # use a post-hoc emitted-body symbol scan (which mis-classified corpus
    # files and monomorphize in a prior attempt).

    def _emit_minimal_emit_ir_theory(self) -> List[str]:
        """The MINIMAL emit_ir surface for an OPAQUE-use mirror: just the bare
        types so opaque params/locals/record-fields typecheck and `IrOther ""`
        constructs. Drops the sum's rich ctors, kind_of, every
        projector/discriminant, `size` + its size-decrease lemmas, and
        irlist/iropt/irnth/irlen. `ir_num` and `sharedvar` are retained (both
        trivial, zero proof cost; `sharedvar` backs the separately-emitted
        `val ir_shared_vars : array sharedvar`). Selected by the class-name
        allow-list gate in `_transpile`."""
        return [
            "  (* theory-tailoring: MINIMAL emit_ir — this mirror uses emit_ir"
            " PURELY OPAQUELY (no IR-node ctor construction / no projection in"
            " any proven body), so only the bare type need exist. The full"
            " ~80-ctor theory (kind_of/size/projectors/lemmas/irlist/iropt) is"
            " dropped to keep every VC's SMT context small (~4x faster proof);"
            " sound because each mirror is proven against its OWN emit_ir."
            " Gated by an explicit class-name allow-list (corpus-inert by"
            " construction). See preamble.py::_emit_minimal_emit_ir_theory. *)",
            "  type ir_num = INum int | IReal real",
            "  type emit_ir = IrOther string",
            "  type sharedvar = { sv_name: string; sv_mutex: string }",
            "",
        ]

    def _record_default_literal(self, record_name: str, _seen=None,
                                _pins=None) -> str:
        """parser-primitives-wall-impl-2.md Gate S: a default WhyML record-literal for
        `record_name` (an already-declared record in `_record_types`), used as the
        ELEMENT witness of an `array <record>` field's `by` clause. Each field takes a
        type-appropriate zero (int→0, str→"", real→0.0, array→empty, map→empty), so the
        literal type-checks against the pure element record. Field labels are qualified
        the same way the record decl qualifies them (`_field_label`)."""
        rec = self._record_types[record_name]
        # W8/W1: a record-typed FIELD (the token `start`/`end` `Tuple[int, int]` slots,
        # which synthesize their own `pytuple_int_int` record) needs a NESTED record
        # literal, not the scalar `0` — otherwise the `by` witness of an
        # `array <record>` field does not type-check. `_seen` breaks a (self-)recursive
        # record chain: such a field falls back to the pre-existing scalar default.
        _seen = set(_seen or ())
        _seen.add(record_name)
        parts: List[str] = []
        for fld in rec["fields"]:
            ft = rec["field_types"].get(fld, "int")
            label = self._field_label(rec["whyml_name"], fld)
            if ft in getattr(self, "_record_types", {}) and ft not in _seen:
                v = self._record_default_literal(ft, _seen)
            elif ft in ("str", "string"):
                # Contract self-field subscript projection: a class invariant
                # `self.<f>[i].<sub> == "<lit>"` PINS this element field, so the
                # `by` witness must carry `<lit>` rather than `""` — otherwise the
                # (real) invariant has no exhibited inhabitant. `_pins` is empty
                # for every class without such an invariant -> byte-inert.
                # The contract names the element field by its WhyML LABEL (the
                # reserved-word-mangled `py_type` for a Python `type` field), so
                # match on the label as well as the raw Python name.
                _pd = _pins or {}
                _p = _pd.get(fld, _pd.get(label))
                v = ('"%s"' % _p) if isinstance(_p, str) else '""'
            elif ft in ("real", "float"):
                v = "0.0"
            elif ft in ("list", "tuple") or ft.startswith("array "):
                v = "(Array.make 0 0)"
            elif ft in ("dict", "set", "frozenset") or ft.startswith("map "):
                v = "(const (None: option int))"
            else:
                v = str(rec.get("defaults", {}).get(fld, 0))
            parts.append(f"{label} = {v}")
        return "{ " + "; ".join(parts) + " }"

    def _emit_type_decls(self, type_decls: List[Dict[str, Any]]) -> Tuple[List[str], Set[str]]:
        """Emit record type declarations. Returns (lines, declared_types)."""
        out: List[str] = []
        declared_types: Set[str] = set()
        # K1 (seq-hval self-field append): the `seq hval` self-fields + their
        # mangled append-target names (`self__field`), populated by the list-field
        # branch below and consumed at the statements.py append site + shadow-local
        # loop. Empty for the corpus (no `List[Dict[str, PyVal]]` field) -> byte-inert.
        self._pyval_seq_fields = set()
        self._pyval_seq_append_targets = set()
        # WhyML record field labels are global within a scope, so a field name
        # used by more than one record (e.g. an inherited field present in both
        # `base` and `sub`) collides. Qualify only those ambiguous names as
        # `<record>_<field>`; unique field names stay bare so existing
        # single-record files emit byte-identically (zero regression).
        _field_counts: Dict[str, int] = {}
        for _td in type_decls:
            if _td.get("kind") == "record":
                for _f in _td["fields"]:
                    _field_counts[_f["name"]] = _field_counts.get(_f["name"], 0) + 1
        self._ambiguous_fields = {fn for fn, c in _field_counts.items() if c > 1}
        # W8/W1: purity of a `List[<record>]` element is TRANSITIVE. A pinned element
        # record whose own field is itself a record (the token's `Tuple[int, int]`
        # `start`/`end` slots → the synthesized `pytuple_int_int`) stays MUTABLE, which
        # re-infects the element record ("instantiates pure type variable 'a with a
        # mutable type"). Close `_list_element_record_types` under record-typed fields
        # so the whole reachable record subtree is emitted pure. Empty in ⇒ empty out,
        # so a module with no `List[<record>]` element is untouched.
        _lert = set(getattr(self, "_list_element_record_types", set()))
        if _lert:
            _rec_names = {_td["name"] for _td in type_decls
                          if _td.get("kind") == "record"}
            _by_name = {_td["name"]: _td for _td in type_decls
                        if _td.get("kind") == "record"}
            _work = list(_lert)
            while _work:
                _cur = _work.pop()
                for _f in _by_name.get(_cur, {}).get("fields", []):
                    _ft = _f.get("type")
                    if _ft in _rec_names and _ft not in _lert:
                        _lert.add(_ft)
                        _work.append(_ft)
            self._list_element_record_types = _lert
        # typed-ir-for-b-ceiling.md §18: a record field whose name ALSO names a local
        # var in some method collides in Why3 — `stmt.ghost_type` resolves to the local
        # `ghost_type` ref ("ref int … cannot be applied"), not the field. Qualify those
        # fields (`<record>_<field>`) too, in both the decl and the access. Gated on
        # @mutable_state (the emitter model) → byte-identical for the corpus.
        if getattr(self, "_mutable_state_classes", None):
            _local_names: Set[str] = set()
            for _fn in self.ir.get("functions", []):
                _local_names |= set(IRScanner.find_assigned_vars(_fn.get("body", [])))
            _rec_fields = {f["name"] for td in type_decls
                           if td.get("kind") == "record" for f in td.get("fields", [])}
            self._ambiguous_fields |= (_rec_fields & _local_names)
            # ghost-assign-bc6: a record field whose name matches a top-level
            # symbol the `emit_ir` ADT theory declares (`size`, `kind_of`,
            # `is_*`, `*_of`, …) collides in Why3's shared module namespace —
            # qualify it the same way. Gated on `_mutable_state_classes` (the
            # SAME condition `_emit_exprir_theory()` fires under), so a
            # non-@mutable_state corpus program — which never emits the theory
            # — never has this collision and the qualification never fires
            # (byte-identical for the corpus).
            self._ambiguous_fields |= (_rec_fields & self._reserved_exprir_symbols())
        n = len(type_decls)
        i = 0
        _VPAY = {"int": "int", "bool": "int", "str": "string", "float": "real",
                 # self-tcb-reduction giants: an `Optional[ast.expr]` local's Some-arm
                 # carries the already-lowered emit_ir sub-node (`Arm_i_0 emit_ir`).
                 "emit_ir": "emit_ir",
                 # set/frozenset union-arm payload: the faithful StrSet model
                 # `map string bool` (matches the frozenset-RETURN model and the
                 # `_union_arm_whyml_type` inj/proj goal), NOT the int default that
                 # int-hashed a string key at a `k in <set>` membership site. No
                 # corpus program has an `Optional[set]`/`Union[..., set]` arm; the
                 # sole mirror consumer is `predicate_definitions.needed` -> inert.
                 # Parenthesized: the payload is a single ctor-argument position
                 # (`Arm_i_0 (map string bool)`), so the multi-token type needs its
                 # own parens or Why3 reads it as `map` applied to `string`/`bool`.
                 "set": "(map string bool)", "frozenset": "(map string bool)"}
        # no-more-int-3 A5a: declared `#@ datatype` names, so a constructor
        # payload that NAMES a datatype (a self-reference `Node(Tree, Tree)` or
        # another variant) resolves to that variant's Why3 type instead of the
        # `_VPAY` int default. A single self-recursive type emits directly
        # (`type tree = Leaf | Node tree tree`); Why3 handles the self-reference.
        _variant_names = {td["name"] for td in type_decls
                          if td.get("kind") == "variant"}
        # W8 capability (v): a constructor payload naming a declared RECORD type
        # (`Optional[_Tok]` -> `Arm_i_0 tok | Arm_i_None`) resolves to that
        # record's Why3 type, exactly as a payload naming another VARIANT
        # resolves to the variant's. Without it the payload fell to the `int`
        # default and every `return <record>` mistyped against the arm.
        _record_payload_types = {td["name"]: whyml_ident(td["name"].lower())
                                 for td in type_decls if td.get("kind") == "record"}

        def _fmt_variant(vtd: Dict[str, Any]) -> str:
            """Register a variant's WhyML mapping + constructors and return its
            `<name>['a…] = Ctor pay | …` body (sans the `type`/`with` keyword)."""
            # 07-0647-spec S1.1: the Why3 type name must be a legal, non-reserved
            # identifier — `whyml_ident` lowercases AND mangles reserved words
            # (`Match` → `py_match`, avoiding the `match` keyword), vs a raw `.lower()`.
            tn = whyml_ident(vtd["name"].lower())
            declared_types.add(tn)
            # A5d: a parametric datatype `Option[T]` → `type option 't = …`. Each
            # type parameter `T` becomes a Why3 type variable `'t`; a payload
            # naming a type param resolves to that variable (not the int default).
            tparams = vtd.get("type_params", []) or []
            _tpvar = {p: f"'{p.lower()}" for p in tparams}
            header = tn + ("".join(f" {_tpvar[p]}" for p in tparams) if tparams else "")
            self._variant_types[vtd["name"]] = {
                "whyml_name": tn,
                "constructors": {c["name"]: c for c in vtd["constructors"]}}
            cstrs: List[str] = []
            for c in vtd["constructors"]:
                pay = " ".join(
                    _tpvar[t] if t in _tpvar
                    else _VPAY[t] if t in _VPAY
                    else t.lower() if t in _variant_names
                    else _record_payload_types.get(t, "int")
                    for t in c.get("payload", []))
                self._constructors[c["name"]] = {
                    "type": vtd["name"], "whyml_type": tn,
                    "arity": c["arity"], "payload": c.get("payload", [])}
                cstrs.append(c["name"] + (f" {pay}" if pay else ""))
            return f"{header} = {' | '.join(cstrs)}"

        # A5a-residual: mutually-recursive datatypes (e.g. `Tree` ↔ `Forest`)
        # must share one Why3 `type a = … with b = …` block, else the first
        # names the sibling before it is declared. Group variants by SCC of the
        # cross-reference graph (a payload naming ANOTHER variant is an edge).
        # A group of size 1 (independent or single self-recursive) is unchanged
        # — emitted as a plain `type … = …` — so existing files stay
        # byte-identical.
        _vrefs: Dict[str, Set[str]] = {}
        for _td in type_decls:
            if _td.get("kind") != "variant":
                continue
            _r: Set[str] = set()
            for _c in _td["constructors"]:
                for _t in _c.get("payload", []):
                    if _t in _variant_names and _t != _td["name"]:
                        _r.add(_t)
            _vrefs[_td["name"]] = _r

        def _reach(start: str) -> Set[str]:
            seen: Set[str] = set()
            stack = list(_vrefs.get(start, ()))
            while stack:
                x = stack.pop()
                if x in seen:
                    continue
                seen.add(x)
                stack.extend(_vrefs.get(x, ()))
            return seen

        _reach_map = {nm: _reach(nm) for nm in _vrefs}
        _vorder = [td["name"] for td in type_decls if td.get("kind") == "variant"]
        _td_by_name = {td["name"]: td for td in type_decls if td.get("kind") == "variant"}
        _variant_groups: Dict[str, List[str]] = {}
        for nm in _vorder:
            grp = [m for m in _vorder
                   if m == nm or (m in _reach_map[nm] and nm in _reach_map.get(m, set()))]
            _variant_groups[nm] = grp
        _emitted_variants: Set[str] = set()

        while i < n:
            td = type_decls[i]
            if td.get("kind") == "variant":
                # sum-types: `type color = Red | Green | Blue` / `type shape = Circle int | …`
                name = td["name"]
                group = _variant_groups.get(name, [name])
                if len(group) > 1:
                    # mutually-recursive group → one `with`-joined block
                    if name in _emitted_variants:
                        i += 1
                        continue
                    out.append(f"  type {_fmt_variant(_td_by_name[group[0]])}")
                    for member in group[1:]:
                        out.append(f"  with {_fmt_variant(_td_by_name[member])}")
                    out.append("")
                    _emitted_variants.update(group)
                    i += 1
                    continue
                out.append(f"  type {_fmt_variant(td)}")
                out.append("")
                i += 1
                continue
            if td["kind"] == "record":
                # 07-0647-spec S1.1: reserved-word-safe Why3 type name (see variant above).
                type_name = whyml_ident(td["name"].lower())
                declared_types.add(type_name)
                self._record_types[td["name"]] = {
                    "whyml_name": type_name,
                    "fields": [f["name"] for f in td["fields"]],
                    "field_types": {f["name"]: f.get("type", "int") for f in td["fields"]},
                    # self-field-dict-reflection (typed-ir §12): per-field dict VALUE type,
                    # so `self.<dict-field>.get(k)` reads back the right type.
                    "field_value_types": {f["name"]: f["value_type"]
                                          for f in td["fields"] if f.get("value_type")},
                    # cleared-hash S4: per-field dict/set KEY type κ, so a
                    # `dict[str,ν]`/`set[str]` field lowers to `map string (option ν)`
                    # with the native, injective Why3 string key (retiring str_hash_op).
                    "field_key_types": {f["name"]: f["key_type"]
                                        for f in td["fields"] if f.get("key_type")},
                    "defaults": td.get("field_defaults", {}),
                    # base_op.md Tier A — parametrized construction C(a, b)
                    "init_params": td.get("init_params", []),
                    "init_body": td.get("init_body", []),
                    # fresh-globals.md — the constructor's `#@ ensures` (post-state),
                    # consumed by `_emit_module_globals` (proven-of-the-literal GOAL)
                    # and `#@ fresh_globals` (assumed-at-driver-entry fact).
                    "init_ensures": td.get("init_ensures", []),
                    # typing-engagement ty2 / 29-1700-typing-spec-5: gates the
                    # TypedDict subscript → record-field-read lowering and the
                    # dict-literal → record-literal lowering. False for every
                    # pre-existing record (byte-identical fallback).
                    "is_typeddict": bool(td.get("is_typeddict", False)),
                    # typing-engagement ty2 / 30-1700-typing-spec-6: gates the
                    # NamedTuple positional-subscript → record-field-read-by-
                    # index lowering. False for every pre-existing record
                    # (byte-identical fallback).
                    "is_namedtuple": bool(td.get("is_namedtuple", False)),
                }
                # hval-retype (self-tcb-reduction Tier-5): the emitter's own
                # `_record_types` field (`Dict[str, Any]` class->metadata registry) is
                # modelled as the faithful heterogeneous `map string (option hval)`, so
                # the metadata that drives BODY lowering must agree with the preamble
                # field decl: value_type "hval" (`_self_field_dict_nu` -> "hval", so
                # `info.get(...)` uses the real K7 pairs_get projection) and key_type
                # "string" (native string key). Name-keyed on the emitter-internal,
                # corpus-absent field -> reference corpus + every other mirror byte-inert.
                if "_record_types" in self._record_types[td["name"]]["field_types"]:
                    self._record_types[td["name"]]["field_types"]["_record_types"] = "dict"
                    self._record_types[td["name"]]["field_value_types"]["_record_types"] = "hval"
                    self._record_types[td["name"]]["field_key_types"]["_record_types"] = "string"
                # Class-body integer constants (e.g. `CAP = 64`) — resolved to
                # literals when referenced as `self.CONST` in a method/contract.
                consts = td.get("constants", {})
                if consts:
                    self._class_constants[type_name] = dict(consts)
                # 7b (self-tcb-reduction L4b): class-body string-SET constants
                # (`_GENERIC_BASE_NAMES = {"Generic"}`) — a `<x> in self.<CONST>`
                # membership lowers to a faithful `str_eq_op` disjunction over these.
                _ssc = td.get("str_set_constants", {})
                if _ssc:
                    if not hasattr(self, "_class_str_set_constants"):
                        self._class_str_set_constants = {}
                    self._class_str_set_constants[type_name] = {
                        k: list(v) for k, v in _ssc.items()}
                field_strs = []
                fields = td["fields"]
                nf = len(fields)
                # WL-04b (wrong-lowering-to-fix.md §WL-04 record residual): a record
                # used as a flat `List[<record>]` ELEMENT is emitted PURE (immutable
                # fields) — Why3 forbids a MUTABLE element inside `array` (the same
                # constraint the nested `array (seq τ)` model met). Module5 records
                # such names in `list_element_record_types`; only they drop `mutable`
                # (byte-identical for every record NOT used as a list element). A
                # record so pinned that is ALSO field-mutated in the body fails closed
                # at Why3 type-check (never a silent unsound update). Read-only at the
                # element position: tuples/NamedTuples are immutable; a projected
                # `List[<dataclass>]` reads its fields only.
                _list_elem_pure = td["name"] in getattr(
                    self, "_list_element_record_types", set())
                j = 0
                while j < nf:
                    f = fields[j]
                    prefix = "" if _list_elem_pure else (
                        "mutable " if f.get("mutable") else "")
                    # class-variant-impl.md §OUTCOME-TS RESIDUAL (record⇄variant
                    # bridge, part a): a recognized term-ctor's recursive field
                    # emits the VARIANT field type (`list term`/`term`/`list string`)
                    # so the record→variant injection typechecks. Gated on the pp
                    # family (ir.py only) -> corpus + other mirrors byte-identical.
                    _tpp = self._term_pp_field_override(td.get("name"), f.get("name"))
                    if _tpp is not None:
                        field_strs.append(
                            f"{prefix}{self._field_label(type_name, f['name'])}: {_tpp}")
                        j += 1
                        continue
                    ftype = f['type']
                    # Map Python-level type tags to WhyML types.
                    # `set`/`dict`/`frozenset` → `map int (option int)`
                    # (body-set/body-dict model). `list`/`tuple` →
                    # `array int`. Everything else collapses to `int`.
                    if ftype in ("set", "dict", "frozenset"):
                        # self-field-dict-reflection (typed-ir §12): a `dict[str, str]`
                        # field carries `option string` values so `self.f.get(k)` reads a
                        # string. Absent value_type → the legacy `option int`, byte-identical.
                        # cleared-hash S4: a string-KEYED field (κ=string, `key_type`) is
                        # `map string (option ν)` with the native Why3 string key; every
                        # field-dict op site reads the RAW string key (no str_hash_op).
                        # Absent key_type → the legacy `map int` (byte-identical).
                        _vt = f.get("value_type")
                        # hval-retype (self-tcb-reduction Tier-5): the emitter's own
                        # `_record_types` field (`Dict[str, Any]`, class->metadata registry)
                        # is retyped to the faithful heterogeneous `map string (option hval)`
                        # so `_field_type_for`/`_field_type_of` read `info.get("whyml_name")`
                        # / `info.get("field_types").get(field)` as REAL hval projections
                        # (pairs_get over the hpairs carrier), not the int-erased facade.
                        # Name-keyed (the field is emitter-internal + corpus-absent) -> the
                        # reference corpus + every other mirror stay byte-identical.
                        if f.get("name") == "_record_types":
                            _vt = "hval"
                        _kt = "string" if f.get("key_type") == "string" else "int"
                        if _vt == "string":
                            ftype = f"map {_kt} (option string)"
                        elif _vt == "hval":
                            # K6 (map-pyval self-field read, self-tcb-reduction Tier-5): a
                            # `Dict[str, PyVal]` self-field is the faithful heterogeneous
                            # `map {_kt} (option hval)` — so `self.f.get(k)` reads a real
                            # `option hval` (`Some v_ -> v_ | None -> (HInt 0)`) instead of
                            # the int-erased `map int (option int)` facade. The `pyval`
                            # theory is already pulled in by the `_uses_pyval` gate (it fires
                            # on any type_decl field value_type == "hval"), so NO new cert
                            # (ledger 3). `PyVal` is a corpus-absent sentinel -> byte-inert.
                            ftype = f"map {_kt} (option hval)"
                        elif isinstance(_vt, str) and _vt.startswith(("map ", "seq ", "array ")):
                            # nested-map.md: a NESTED collection value (`Dict[str, Dict[str,int]]`
                            # → value_type `map int (option int)`; `Dict[str, List[int]]` → `seq int`)
                            # is preserved as `map int (option (<inner>))`, NOT flattened to
                            # `option int`. `_m5_get_dict_value_type` already emits the inner type.
                            ftype = f"map {_kt} (option ({_vt}))"
                        else:
                            ftype = f"map {_kt} (option int)"
                    elif ftype in ("list", "tuple"):
                        # i-feel-good.md I-E: a `List[str]` field is `array string` (string
                        # elements) in a @mutable_state module (the emitter model + its
                        # imported IR records); the corpus has no such module → `array int`,
                        # byte-identical.
                        # variadic content-law comprehension (FABLE-sanctioned): a
                        # `List[ExprIR]` field (value_type "emit_ir" — MkTupleExpr.elts /
                        # the harvested pure_ast Tuple.elts) is `array emit_ir`. The gate is
                        # widened to match the SCALAR ExprIR->emit_ir mapping below (and the
                        # emit_ir-theory-emission gate): any @mutable_state module OR any
                        # IR-node-typed param (`_uses_ir_node_param`) — the Module5 mirror
                        # imports its IR records via the latter, not @mutable_state. Both
                        # gates are False for the corpus → `array int`, byte-identical.
                        if (f.get("value_type") == "hval"
                                and (getattr(self, "_mutable_state_classes", None)
                                     or getattr(self, "_uses_ir_node_param", False))):
                            # K1 (seq-pyval self-field append, self-tcb-reduction Tier-5):
                            # a `List[PyVal]` / `List[Dict[str, PyVal]]` field is the
                            # faithful growable `seq hval` (the fable-proven
                            # `getting-better/setenv_faithful.mlw` shape, element carrier
                            # `pyval`), so `self.f.append(x)` writes back a REAL
                            # `self.f <- Seq.snoc self.f (<pyval-wrap x>)` instead of the
                            # int-erased `array int` + `Array.make 1024 0` shadow-local
                            # facade (Bug 3). Record the field + its mangled append-target
                            # name so the statements.py append site + shadow-local loop
                            # gate to the write-back. Gated on `_mutable_state`/IR-node
                            # param AND the `pyval` element sentinel (absent from the
                            # corpus) -> byte-identical for every other mirror + corpus.
                            ftype = "seq hval"
                            self._pyval_seq_fields.add(f["name"])
                            self._pyval_seq_append_targets.add(
                                ("self." + f["name"]).replace(".", "_"))
                        elif (f.get("value_type") in ("string", "emit_ir")
                                and (getattr(self, "_mutable_state_classes", None)
                                     or getattr(self, "_uses_ir_node_param", False))):
                            ftype = f"array {f.get('value_type')}"
                        elif (f.get("value_type") in self._record_types
                                and (getattr(self, "_mutable_state_classes", None)
                                     or getattr(self, "_uses_ir_node_param", False))):
                            # parser-primitives-wall-impl-2.md Gate S: a
                            # `List[<record>]` field (value_type = the element record's
                            # class name, e.g. `_Tok`) is the faithful `array <record>`
                            # — was the element-erased `array int`, which made a
                            # record-returning field read (`self.toks[self.i] : _Tok`)
                            # mistype as int. The element record is emitted PURE
                            # (Why3 forbids a mutable element inside `array`;
                            # `list_element_record_types` pins it, dropping `mutable`).
                            # Same @mutable_state/IR-node gate as the string/emit_ir
                            # element branch above -> byte-inert for the corpus (no
                            # corpus record has a `List[<record>]` field).
                            ftype = f"array {self._record_types[f['value_type']]['whyml_name']}"
                        else:
                            ftype = "array int"
                    elif ftype == "option":
                        # optional-field builder (monomorphic-option ADTs): an
                        # `Optional[str]` / `Optional[ExprIR]` record field
                        # (Forall/Exists `binder_type`/`domain`) is a faithful
                        # `option string` / `option emit_ir` — read + converted to
                        # the monomorphic `iropt_str`/`iropt_ir` at the ctor arg
                        # (expressions.py `_lower_irnode_construction`). GATED on
                        # @mutable_state OR an IR-node-typed param (the same gate
                        # as the ExprIR->emit_ir field mapping below and the
                        # emit_ir-theory-emission gate): the Module5 mirror imports
                        # its IR records via the latter. Both gates are False for
                        # the corpus → the historical `int` collapse, byte-identical
                        # (only 3 corpus files carry any `Optional[...]` field, all
                        # non-@mutable_state → int).
                        _ov = f.get("value_type")
                        if _ov == "opaque_term":
                            # crosscheck_ir.py self-state carrier
                            # (class-variant-impl.md §OUTCOME-CC / §F3): an
                            # `Optional[Term]` canon field. When the certified
                            # `term` inductive is available in this file (the mirror
                            # imports the full 9-ctor Term union -> `_term_adt_spec`
                            # is derived, `type term` is emitted), the field is the
                            # FAITHFUL `option term` — so `isinstance(c, Unsupported)`
                            # / `c == d` (term_eq) over the canon fields lower onto
                            # the real inductive (F3/F4). Absent the inductive it
                            # degrades to an inhabitable `option int` (presence-only,
                            # the §OUTCOME-CC `registry_skipped` path). value_type
                            # "opaque_term" arises ONLY from the (class,field)
                            # allow-list in Module5 -> corpus/other-mirror byte-inert.
                            if getattr(self, "_term_adt_spec", None):
                                ftype = "option term"
                            else:
                                ftype = "option int"
                        elif (_ov in ("string", "emit_ir")
                                and (getattr(self, "_mutable_state_classes", None)
                                     or getattr(self, "_uses_ir_node_param", False))):
                            ftype = f"option {_ov}"
                        else:
                            ftype = "int"
                    elif ftype in ("string", "str"):
                        # 07-2333-rev2 TP-3 (Gap 6): a `str`-annotated field is a faithful
                        # Why3 `string` (was collapsed to `int`) — the class counterpart of
                        # the TP-1 str local / str param lowering.
                        ftype = "string"
                    elif ftype in ("real", "float"):
                        # wrong-lowering-to-fix.md §WL-03b: a `float`-annotated field (a
                        # `@dataclass`/`NamedTuple`/`self.f: float` field, or a synthesized
                        # `Tuple[int, float]` slot) is the faithful Why3 `real` (τ(float)=
                        # real, no-more-int Stage D) — was collapsed to `int`, truncating a
                        # fractional slot read. The record projection `p.f` / `a[i].f` /
                        # `t[1]` then reads a `real`. `real` is a PURE type, so such a record
                        # is legal as an `array` element (WL-04b PURE-element constraint).
                        ftype = "real"
                    elif (ftype in ("ExprIR", "StmtIR", "IRNode", "ContractExprIR")
                          and (getattr(self, "_mutable_state_classes", None)
                               or getattr(self, "_uses_ir_node_param", False))):
                        # typed-ir-for-b-ceiling.md B-C2: an ExprIR-valued field is the
                        # typed IR-node sum `emit_ir` — but ONLY when the `emit_ir` theory
                        # is actually emitted (same gate as Module6_WhyMLTranspiler's
                        # theory-emission at :519). A file that merely DEFINES/imports an
                        # ExprIR-field record without being @mutable_state (e.g. the
                        # Module2_Parser / Module3_Weaver mirrors, which own the CSL-AST
                        # dataclasses whose fields were retyped CSLNode->ExprIR for the
                        # Module5 construction build) does NOT emit the theory, so mapping
                        # the field to `emit_ir` there yields an `unbound type symbol
                        # 'emit_ir'`. Gate it: non-theory files fall through to the int
                        # default below (their pre-build behavior). Corpus-inert (no corpus
                        # record uses an ExprIR field).
                        ftype = "emit_ir"
                    elif (ftype == "PyConstVal"
                          and (getattr(self, "_mutable_state_classes", None)
                               or getattr(self, "_uses_ir_node_param", False))):
                        # pyconst_val value-variant ADT (self-tcb-reduction M5, B-bucket):
                        # a `.value`-of-`ast.Constant` field (harvested from the pure_ast
                        # Constant node, ir_resolve.py `_PURE_AST_FIELD_TABLE`) is the
                        # discriminated union of Python constant scalar kinds `pyconst_val`
                        # (preamble.py `_emit_exprir_theory`). GATED identically to the
                        # ExprIR->emit_ir mapping above (@mutable_state OR an IR-node-typed
                        # param — the Module5 mirror imports its pure_ast records via the
                        # latter), so the type is bound exactly where the theory is emitted.
                        # Both gates are False for the corpus -> falls through to the int
                        # default below, byte-identical.
                        ftype = "pyconst_val"
                    elif ftype in self._record_types:
                        # wrong-lowering.md §WL-03: a field whose type is another
                        # (already-declared) record — a synthesized `Tuple[T1, ...]`
                        # per-slot record used as a FIELD — is the nested record's
                        # Why3 type, so `self.f[i]` reads the faithful slot. The
                        # tuple records are appended to `type_decls` BEFORE the class
                        # records, so they are declared (and in `_record_types`) here.
                        ftype = self._record_types[ftype]["whyml_name"]
                    elif ftype != "int" and not ftype.startswith(("array ", "map ", "ref ", "string", "emit_ir")):
                        # Unrecognised tag (user-defined class etc.) —
                        # fall back to int rather than emitting an
                        # unbound type symbol.
                        ftype = "int"
                    field_strs.append(
                        f"{prefix}{self._field_label(type_name, f['name'])}: {ftype}")
                    j += 1
                out.append(f"  type {type_name} = {{ {'; '.join(field_strs)} }}")
                class_invs = td.get("class_invariants", [])
                if class_invs:
                    # PRE-PASS (contract self-field subscript projection): register
                    # `field -> element record class` BEFORE the invariants are
                    # lowered, so a class invariant `self.<f>[i].<sub>` reaches the
                    # self-field array-read projector (`expressions.py` W8 (iii))
                    # instead of the unbound `get_<sub>` getter. The witness loop
                    # below re-registers the SAME entries (idempotent); the gate is
                    # byte-for-byte the one used there, so this is inert wherever no
                    # `List[<record>]` field on a `@mutable_state`/IR-node class has a
                    # class invariant.
                    for _f in td["fields"]:
                        _vt0 = _f.get("value_type")
                        if (_f.get("type") in ("list", "tuple")
                                and _vt0 in self._record_types
                                and (getattr(self, "_mutable_state_classes", None)
                                     or getattr(self, "_uses_ir_node_param", False))):
                            if not hasattr(self, "_record_array_fields"):
                                self._record_array_fields = {}
                            self._record_array_fields[_f["name"]] = _vt0
                    self._in_spec = True
                    self._emit_record_ctx = type_name
                    # L0′ (challenging-the-plan §4.1): set the self-type so a `self.<field>[i]` access
                    # in the invariant resolves the field's array type (`_field_type_of` keys on
                    # `_current_self_type`) and lowers to `Array.get`, not the unbound `subscript_get`.
                    _prev_self = getattr(self, "_current_self_type", None)
                    self._current_self_type = type_name
                    n_inv = len(class_invs)
                    i_inv = 0
                    while i_inv < n_inv:
                        inv = class_invs[i_inv]
                        inv_str = self._expr_to_whyml(inv, set(), invariant_ctx=True)
                        out.append(f"    invariant {{ {inv_str} }}")
                        i_inv += 1
                    self._current_self_type = _prev_self
                    self._emit_record_ctx = None
                    self._in_spec = False
                    defaults = td.get("field_defaults", {})
                    field_names = [f["name"] for f in td["fields"]]
                    field_types = {f["name"]: f.get("type", "int") for f in td["fields"]}
                    # Pin array-field lengths from `\length(self.f) == N`
                    # invariants so the `by` witness builds an array of the
                    # right size.
                    array_lengths = self._extract_array_lengths(class_invs)
                    witness_vals = {fn: defaults.get(fn, 0) for fn in field_names}
                    if not self._check_witness_vals(witness_vals, class_invs, field_names):
                        combos = [
                            {fn: 0 for fn in field_names},
                            {fn: 1 for fn in field_names},
                            {fn: 10 for fn in field_names},
                        ]
                        nc = len(combos)
                        ic = 0
                        while ic < nc:
                            combo = combos[ic]
                            if self._check_witness_vals(combo, class_invs, field_names):
                                witness_vals = combo
                                break
                            ic += 1
                    # parser-primitives-wall-impl-2.md Gate S: an `array <record>`
                    # field (`List[<record>]`, value_type = the element record name)
                    # needs a record-LITERAL witness element, not the int `0` — else
                    # `Array.make N 0` mistypes against `array <record>`. Build a
                    # default record literal from the element record's field defaults.
                    array_elem_witnesses: Dict[str, str] = {}
                    # Contract self-field subscript projection: `{field: {sub: lit}}`
                    # pins read off `self.<f>[i].<sub> == "<lit>"` class invariants.
                    _elem_pins = self._extract_elem_field_pins(class_invs)
                    for _f in td["fields"]:
                        _vt = _f.get("value_type")
                        if (_f.get("type") in ("list", "tuple")
                                and _vt in self._record_types
                                and (getattr(self, "_mutable_state_classes", None)
                                     or getattr(self, "_uses_ir_node_param", False))):
                            array_elem_witnesses[_f["name"]] = \
                                self._record_default_literal(
                                    _vt, None, _elem_pins.get(_f["name"]))
                            # W8/W1: remember `field -> element record` so a local
                            # bound to `self.<field>[i]` (the token cursor's
                            # `t = self.toks[self.i]`) pre-declares a record ref
                            # instead of the int `ref 0`, and `len(self.<field>)`
                            # lowers to `Array.length`.
                            if not hasattr(self, "_record_array_fields"):
                                self._record_array_fields = {}
                            self._record_array_fields[_f["name"]] = _vt
                    # Qualify ambiguous field names in the witness too.
                    _q = lambda fn: self._field_label(type_name, fn)
                    out.append(f"    by {{ {self._build_witness_str([_q(fn) for fn in field_names], {_q(fn): v for fn, v in witness_vals.items()}, {_q(fn): t for fn, t in field_types.items()}, {_q(fn): l for fn, l in array_lengths.items()}, {_q(fn): w for fn, w in array_elem_witnesses.items()})} }}")
                out.append("")
                # UB-7.2 — hash/eq consistency. Module 5 marks classes
                # whose `__hash__` and `__eq__` are both defined.
                # `__hash__` and `__eq__` are dunders and Module 5
                # skips dunders for body emission, so we declare them
                # as abstract `val` functions here and emit the
                # consistency relationship.
                #
                # Default mode emits an *axiom* — the user is on the
                # hook to keep hash and eq consistent; the axiom
                # documents the assumption. Strict mode (CLI flag
                # `--strict-hash-eq-consistency`) emits a *goal* that
                # Why3 must discharge (typically via an external
                # `#@ proof rocq` citation).
                if td.get("has_hash") and td.get("has_eq"):
                    cls = td["name"].lower()
                    out.append(f"  (* UB-7.2 — hash/eq for {td['name']} *)")
                    out.append(f"  val function {cls}_hash_ (x: {cls}) : int")
                    out.append(f"  val function {cls}_eq_ (a: {cls}) (b: {cls}) : bool")
                    if getattr(self, "strict_hash_eq_consistency", False):
                        out.append(
                            f"  goal hash_eq_consistent_{cls}: forall a b: {cls}. "
                            f"{cls}_eq_ a b = True -> {cls}_hash_ a = {cls}_hash_ b")
                    else:
                        out.append(
                            f"  axiom hash_eq_consistent_{cls}: forall a b: {cls}. "
                            f"{cls}_eq_ a b = True -> {cls}_hash_ a = {cls}_hash_ b")
                    out.append("")
                elif td.get("is_unhashable"):
                    cls = td["name"].lower()
                    out.append(f"  (* UB-7.2 — class {td['name']} defines __eq__ "
                               f"without __hash__: unhashable, do not use as dict/set key *)")
                    out.append("")
            i += 1
        return out, declared_types

    def _emit_opaque_class_aliases(self, functions: List[Dict[str, Any]],
                                    out: List[str], declared_types: Set[str]) -> None:
        """Emit `type <cls> = int` aliases for classes used as `self_type`
        in methods but not declared as records."""
        for func in functions:
            if func.get("kind") == "method" and func.get("self_type"):
                st = whyml_ident(func["self_type"].lower())
                if st not in declared_types:
                    declared_types.add(st)
                    out.append(f"  type {st} = int")
                    out.append("")

