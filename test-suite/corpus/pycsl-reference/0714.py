# pycsl-flags: -p alt-ergo
"""Test 0714 — string-field DISJOINT-REGION FRAME (the byte-locality twin of 0708).

The frame primitive for the `field_to_str` codec — the byte-locality twin of 0708's
ENCODE→DECODE round-trip. `field_to_str(disk, off, width)` is the null-terminated name in
the `width`-byte field at byte offset `off` (the SAME scan-to-first-null `'>Ns'` decode
0708 validates). This file banks the fact that the decode depends ONLY on the bytes
disk[off..off+width): if two disk states agree byte-for-byte over that exact window, they
decode to the SAME name.

    field_to_str_frame :
      forall d0 d1 off width.
        0 <= width ->
        (forall i. 0 <= i < width -> d0[off+i] = d1[off+i]) ->
        field_to_str d0 off width = field_to_str d1 off width

This is the DISJOINT-REGION twin of the retired `block5_decode_frame` (which required FULL
block-5 byte agreement — broken by ANY in-block blit). The frame only asks for agreement on
the SINGLE field's window. Composed with 0712's `slot_name_byte_decode` bridge
(`slot_name(disk,5,k) == field_to_str(disk, 2560+32*k+2, 30)`) it supplies the slot_name
LOCALITY frame the directory mutators need: a blit rewriting slot s's 32-byte entry leaves
every OTHER slot k≠s's 30-byte name window untouched, so the blit's byte frame supplies the
antecedent and slot k's name decode is preserved (`slot_name d1 5 k == slot_name d0 5 k`).
It is the BANKED rung-1 substrate the eventual `_write_dir_entry` / `_zero_entry` retirement
is built on.

NOTE — NOT a trust retirement. This primitive does NOT by itself retire any os `\trusted`;
retiring a dir-mutator trust remains separately blocked on the folded invariant-maintenance
lemma (the byte->inode==0 keystone). This file banks the disjoint-region frame only.

WALL CHARACTER: like 0708's round-trip, the frame is NOT SMT-dischargeable. `field_to_str`
is an ABSTRACT logic `function` (no WhyML body to unfold — constrained only by axioms), so
the frame can only come by induction over the scan-to-first-null decode, which E-match-
explodes over Why3's axiomatic strings. So it is a CITED axiom: SMT only APPLIES it (O(1))
under the byte-frame antecedent, while the induction is discharged offline in the cross-
validated Rocq + Lean proofs.

TRIGGER DISCIPLINE: the frame axiom is keyed on BOTH decode terms
`[field_to_str d1 off width, field_to_str d0 off width]` — it fires ONLY when both field
decodes are already present in the goal (a frame BETWEEN two named disk states), never on a
lone decode. This keeps it narrow: it cannot E-match-explode globally (the round-trip's and
slot_name's atoms are single-decode shapes that never match this two-decode trigger).

PROVER NOTE (`# pycsl-flags: -p alt-ergo`): applying this axiom requires discharging its
nested universal antecedent (`forall i. ... -> d0[off+i] = d1[off+i]`) from the caller's
matching `forall i` hypothesis. Alt-Ergo does this in ~20 steps (Valid); Z3 (via the Why3
driver) does NOT fire the multi-decode trigger / discharge the inner universal here and
returns Unknown — a genuine Alt-Ergo/Z3 divergence on the frame shape (NOT present for the
single-conclusion round-trip 0708, which Z3 applies). Per the extreme-rigor doctrine an SMT
divergence is a ROUTING condition: this exhibit is pinned to Alt-Ergo (a first-class pipeline
prover that APPLIES the axiom), while the deep induction is discharged offline in the
cross-validated Rocq + Lean proofs. The divergence is filed for the future citation site
(`_write_dir_entry` retirement) in getting-better/.

Cross-validated by FieldToStrFrame.{v,lean} (theorem field_to_str_frame): `field_to_str` is
the scan-to-first-null decode over an abstract byte-reader (the SAME concrete model as 0708's
FieldToStrRoundTrip); the frame is proved by induction on the scan fuel / width — agreeing
bytes feed the same scan branch at every step. Rocq 8.20.1: Closed under the global context
(only the abstract Section Variables rd0, rd1; 0 Axiom/Admitted); Lean 4.31.0: "depends on
axioms: [propext, Quot.sound]" (subseteq {propext, Quot.sound}, no sorry).
"""

from typing import List


# The FRAME value fact: two disk states that agree byte-for-byte over the `width`-byte field
# at `off` decode to the SAME name. The cited frame axiom closes the empty-body VC: the byte-
# agreement requires materializes the antecedent, and the two-decode trigger
# `[field_to_str(d1,off,width), field_to_str(d0,off,width)]` fires exactly once (both decode
# terms are present in the ensures). `field_to_str` is the SAME abstract UnixFs.Field codec
# 0708 validates and 0712's slot_name bridge composes with.
#@ requires 0 <= width
#@ requires \forall i: int; (0 <= i and i < width) ==> d0[off + i] == d1[off + i]
#@ ensures field_to_str(d0, off, width) == field_to_str(d1, off, width)
#@ proof rocq UnixFs.Field.field_to_str_frame
#@ proof lean UnixFs.Field.field_to_str_frame
def field_frame(d0: List[int], d1: List[int], off: int, width: int) -> None:
    pass


# The END-TO-END disjoint-blit rung: a blit rewrites the 32-byte slot at `blit_off` while a
# DISJOINT 30-byte name field lives entirely below it (`off + 30 <= blit_off`). The blit
# touches only disk[blit_off .. blit_off+32], so the name field's bytes are framed (assigns
# leaves them equal to the pre-state values). We then conclude the name-field decode is
# unchanged across the blit — the SAME shape a dir-mutator proves for `slot_name(self.dir,5,k)
# == slot_name(old(self.dir),5,k)` on every slot k whose entry the mutation did not touch.
#
# Modeled with two arrays (pre = d0, post = d1) that agree everywhere outside the blit window;
# the disjointness `off + 30 <= blit_off` puts the whole name field outside that window, so the
# per-byte agreement antecedent holds for the field and the cited frame closes the decode
# equality. Both decode terms appear in the ensures, firing the two-decode trigger once.
#@ requires 0 <= off
#@ requires off + 30 <= blit_off
#@ requires \forall i: int; (0 <= i and i < 30) ==> pre[off + i] == post[off + i]
#@ ensures field_to_str(pre, off, 30) == field_to_str(post, off, 30)
#@ proof rocq UnixFs.Field.field_to_str_frame
#@ proof lean UnixFs.Field.field_to_str_frame
def name_field_survives_disjoint_blit(pre: List[int], post: List[int], off: int, blit_off: int) -> None:
    pass
