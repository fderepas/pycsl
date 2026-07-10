from __future__ import annotations

from typing import Any, Dict, List, Set, Tuple

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
        tuple_return_arities: Set[int] = set()
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
                    if self._func_returns_string_seq(func):
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
                 for t in f.get("param_list_nested_elem", {}).values())
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
            recognize_bool_existence, recognize_frt, recognize_sawalk,
            recognize_dictfold)
        # ir-traversal-residual T3: the context-threading walk `_sa_walk` routes
        # to the env-threaded pyval/pydict group and additionally needs the
        # string-keyed `sdict` theory (`needs_sdict`, gated separately so the
        # already-landed pydict-group mirrors stay byte-identical).
        needs_sdict = any(
            recognize_sawalk(f) is not None or recognize_dictfold(f) is not None
            for f in functions)
        needs_pydict = needs_sdict or any(
            recognize_generic_fold(f) is not None or recognize_setfold(f) is not None
            or recognize_substmap(f) is not None
            or recognize_bool_existence(f) is not None
            or recognize_frt(f) is not None
            for f in functions)
        return {
            "needs_pydict": needs_pydict,
            "needs_sdict": needs_sdict,
            "needs_array": needs_array,
            "needs_matrix": needs_matrix,
            "needs_minmax": needs_minmax,
            "needs_continue": needs_continue,
            "needs_break": needs_break,
            "needs_return_exc": needs_return_exc,
            "needs_return_seq": needs_return_seq,
            "needs_return_seq_str": needs_return_seq_str,
            "needs_return_str": needs_return_str,
            "needs_return_void": needs_return_void,
            "needs_body_dict": needs_body_dict,
            "tuple_return_arities": tuple_return_arities,
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
                    or _record_has_map or needs.get("needs_option_record")):
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
        else:
            out.append("  use map.Map")
            if needs["needs_list_ghost"]:
                out.append("  use list.List")
                out.append("  use list.Length")
                out.append("  use list.NthNoOpt")
                out.append("  use list.Mem")
                out.append("  use list.Append")
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
        # Sanitize each user-exception name; collapse Python local-alias
        # imports (`from X import Y as _Y`) by deduping via set after
        # leading-underscore strip. See `safe_exc_name` in identifiers.py.
        sanitized_exc = sorted({safe_exc_name(n) for n in needs["user_exceptions"]})
        for exc in sanitized_exc:
            out.append(f"  exception {exc}")
        return out

    def _emit_preamble_helpers(self, needs: Dict[str, Any]) -> List[str]:
        """Phase C: emit helper lemmas, pycsl_sum, pycsl_div, pycsl_mod function bodies."""
        out: List[str] = []
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
        return self._pydict_theory_lines() + self._sdict_theory_lines(needs)

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
            " the IfExpr ternary node — following the IrBinOp precedent verbatim. *)",
            "  type emit_ir = IrVar string | IrAttr emit_ir string | IrStr string"
            " | IrNum int | IrRaw string | IrOther string"
            " | IrCall string emit_ir int | IrSub emit_ir emit_ir"
            " | IrTuple emit_ir emit_ir"
            " | IrBinOp string emit_ir emit_ir"
            " | IrFieldGet string string"
            " | IrIfExpr emit_ir emit_ir",
            "",
            "  (* B-C5: IrCall carries func name, first arg (arg0), arity; IrSub carries"
            " value and index sub-nodes — the emitter reflects on Call/Subscript IR."
            " B-C6: IrTuple carries the first two elements (elts[0], elts[1]) — the"
            " emitter reflects on a MkTuple node's `elts` in the ghost-dict `+=` branch."
            " tier3-p1: IrBinOp carries the operator string and the left/right sub-nodes."
            " orelse_of mini-M1: IrIfExpr carries the body (then/value) and orelse (else)"
            " sub-nodes — the emitter reflects on an IfExpr ternary's `.get(\"body\")`/"
            " `.get(\"orelse\")`. *)",
            "  let function kind_of (e: emit_ir) : string =",
            "    match e with",
            "    | IrVar _ -> \"Var\" | IrAttr _ _ -> \"Attribute\"",
            "    | IrStr _ -> \"String\" | IrNum _ -> \"Number\"",
            "    | IrRaw _ -> \"RawWhyml\"",
            "    | IrCall _ _ _ -> \"Call\" | IrSub _ _ -> \"Subscript\"",
            "    | IrTuple _ _ -> \"MkTuple\"",
            "    | IrBinOp _ _ _ -> \"BinOp\"",
            "    | IrFieldGet _ _ -> \"FieldGet\"",
            "    | IrIfExpr _ _ -> \"IfExpr\"",
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
            "    match e with IrCall _ _ _ -> true | _ -> false end",
            "  let function is_tuple (e: emit_ir) : bool =",
            "    match e with IrTuple _ _ -> true | _ -> false end",
            "  let function is_fieldget (e: emit_ir) : bool =",
            "    match e with IrFieldGet _ _ -> true | _ -> false end",
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
            "  let function name_of (e: emit_ir) : string =",
            "    match e with IrVar n -> n | IrAttr _ a -> a | _ -> \"\" end",
            "",
            "  let function value_of (e: emit_ir) : string =",
            "    match e with IrStr v -> v | IrRaw v -> v | _ -> \"\" end",
            "",
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
            "  let function func_of (e: emit_ir) : string =",
            "    match e with IrCall f _ _ -> f | _ -> \"\" end",
            "",
            "  let function nargs_of (e: emit_ir) : int =",
            "    match e with IrCall _ _ n -> n | _ -> 0 end",
            "",
            "  let function arg0_of (e: emit_ir) : emit_ir =",
            "    match e with IrCall _ a _ -> a | _ -> IrOther \"\" end",
            "",
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
            "  (* self-ir-schema.md IR1: the typed slice of `self.ir` the emitter reflects on —"
            " `self.ir.get(\"shared_vars\", [])` is an array of these records"
            " (`sv[\"name\"]`/`sv.get(\"mutex\")`). Only the string TYPE is modelled; the"
            " content stays opaque via `ir_shared_vars`. *)",
            "  type sharedvar = { sv_name: string; sv_mutex: string }",
            "",
        ]

    def _emit_type_decls(self, type_decls: List[Dict[str, Any]]) -> Tuple[List[str], Set[str]]:
        """Emit record type declarations. Returns (lines, declared_types)."""
        out: List[str] = []
        declared_types: Set[str] = set()
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
        n = len(type_decls)
        i = 0
        _VPAY = {"int": "int", "bool": "int", "str": "string", "float": "real"}
        # no-more-int-3 A5a: declared `#@ datatype` names, so a constructor
        # payload that NAMES a datatype (a self-reference `Node(Tree, Tree)` or
        # another variant) resolves to that variant's Why3 type instead of the
        # `_VPAY` int default. A single self-recursive type emits directly
        # (`type tree = Leaf | Node tree tree`); Why3 handles the self-reference.
        _variant_names = {td["name"] for td in type_decls
                          if td.get("kind") == "variant"}

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
                    else (t.lower() if t in _variant_names else "int")
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
                # Class-body integer constants (e.g. `CAP = 64`) — resolved to
                # literals when referenced as `self.CONST` in a method/contract.
                consts = td.get("constants", {})
                if consts:
                    self._class_constants[type_name] = dict(consts)
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
                        _kt = "string" if f.get("key_type") == "string" else "int"
                        if _vt == "string":
                            ftype = f"map {_kt} (option string)"
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
                        if (f.get("value_type") in ("string", "emit_ir")
                                and getattr(self, "_mutable_state_classes", None)):
                            ftype = f"array {f.get('value_type')}"
                        else:
                            ftype = "array int"
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
                    elif ftype in ("ExprIR", "StmtIR", "IRNode", "ContractExprIR"):
                        # typed-ir-for-b-ceiling.md B-C2: an ExprIR-valued field is the
                        # typed IR-node sum `emit_ir`. Only in a @mutable_state mirror.
                        ftype = "emit_ir"
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
                    # Qualify ambiguous field names in the witness too.
                    _q = lambda fn: self._field_label(type_name, fn)
                    out.append(f"    by {{ {self._build_witness_str([_q(fn) for fn in field_names], {_q(fn): v for fn, v in witness_vals.items()}, {_q(fn): t for fn, t in field_types.items()}, {_q(fn): l for fn, l in array_lengths.items()})} }}")
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

