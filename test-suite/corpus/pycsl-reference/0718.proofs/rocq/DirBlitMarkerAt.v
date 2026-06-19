(* Validation of the BLOCK-PARAMETERIZED ("at an arbitrary block") form of the
 * ROUTE-1 unique-marker byte-rung directory-entry maintenance facts:
 *   UnixFs.Dir.dir_blit_marker_at_intro
 *   UnixFs.Dir.dir_blit_marker_at_value_inode
 *   UnixFs.Dir.dir_blit_marker_at_value_name
 *   UnixFs.Dir.dir_blit_marker_at_frame_only
 *
 * CONTEXT (test-supervise-sl, 2026-06-19): the landed block-5 marker family
 * (0716 DirBlitMarker.v) is HARDCODED to the root directory block 5 — its
 * marker references rd d1 (slot_off 5 s) and the byte-region frame rd d1
 * (5*512 + b), and its corollaries conclude slot_inode d1 5 s / slot_name d1 5 s.
 * That family discharges _write_dir_entry / _zero_entry, which always mutate
 * self.dir (block 5). But _write_entry mutates self.disk at an ARBITRARY block
 * `block_num` (its ensures reference slot_inode(self.disk, block_num, slot) /
 * slot_name(self.disk, block_num, slot)) — so the block-5 family does NOT apply.
 *
 * THE GENERALIZATION: this file is the block-5 family with the constant `5`
 * replaced by a Variable `blk` everywhere it appears as the mutated block (the
 * slot_off block argument and the byte-region-frame base blk*512). slot_off,
 * slot_inode, slot_name, scan, field_to_str, name_list/name_val are ALREADY
 * generic over the block argument (slot_off blk k = blk*512 + 32*k); only the
 * marker DEFINITION and the corollary conclusions were specialised to 5. The
 * block-5 theorems are the blk := 5 instances of THESE — same proof, 5 -> blk.
 *
 * SCOPE: _write_entry's ensures are VALUE (slot_inode/slot_name at slot) +
 * FRAME (forall k <> slot). It does NOT maintain the block-5 directory uniqueness
 * invariants uniq/slots_lt32 (those are self.dir/block-5 facts that the live-insert
 * callers _write_dir_entry establish, NOT a property of an arbitrary-block write).
 * So this file proves the block-parameterized INTRO + the two VALUE corollaries
 * (inode, name) + the FRAME corollary — exactly the four facts _write_entry needs —
 * and NOT a block-parameterized `insert` (no uniq/slots_lt32 over arbitrary blk).
 *
 * Faithful interpretation: IDENTICAL to DirBlitMarker.v for the shared symbols
 * (the `array int` reader rd, the 256*b0+b1 inode decode, the field_to_str
 * scan-to-null name decode, `name` as its char-code list); the marker is the SAME
 * conservative DEFINITION of the abstract WhyML predicate, generalised over blk.
 *
 * Verified under Coq 8.20.x.  No Admitted, no Axiom (only Section Variables). *)

Require Import Coq.ZArith.ZArith.
Require Import Coq.Lists.List.
Require Import Lia.
Import ListNotations.
Open Scope Z_scope.

Module UnixFs.
Module Dir.
Section MarkerAt.

Variable disk : Type.
Variable rd : disk -> Z -> Z.

Variable name_t : Type.
Variable nchar : name_t -> Z -> Z.
Variable nlen : name_t -> Z.

Definition slot_off (blk k : Z) : Z := blk * 512 + 32 * k.

Definition slot_inode (d : disk) (blk k : Z) : Z :=
  256 * (rd d (slot_off blk k)) + rd d (slot_off blk k + 1).

Fixpoint scan (rdf : Z -> Z) (off : Z) (fuel : nat) : list Z :=
  match fuel with
  | O => []
  | S m => if Z.eqb (rdf off) 0 then [] else rdf off :: scan rdf (Z.succ off) m
  end.

Definition field_to_str (rdf : Z -> Z) (off width : Z) : list Z :=
  scan rdf off (Z.to_nat width).

Definition slot_name (d : disk) (blk k : Z) : list Z :=
  field_to_str (rd d) (slot_off blk k + 2) 30.

Fixpoint name_list (nm : name_t) (fuel : nat) (i : Z) : list Z :=
  match fuel with
  | O => []
  | S m => nchar nm i :: name_list nm m (i + 1)
  end.

Definition name_val (nm : name_t) : list Z := name_list nm (Z.to_nat (nlen nm)) 0.

(* ---- THE BLOCK-PARAMETERIZED MARKER: the conservative DEFINITION of the abstract
 * WhyML predicate `dir_blit_marker_at d0 d1 blk s b0 b1 nm`, generalised over the
 * mutated block `blk`. IDENTICAL to dir_blit_marker but with the block argument of
 * slot_off and the byte-region-frame base (blk*512) parameterised. *)

Definition dir_blit_marker_at (d0 d1 : disk) (blk s b0 b1 : Z) (nm : name_t) : Prop :=
  0 <= nlen nm
  /\ nlen nm <= 30
  /\ rd d1 (slot_off blk s) = b0
  /\ rd d1 (slot_off blk s + 1) = b1
  /\ (forall i : Z, 0 <= i < nlen nm -> nchar nm i <> 0)
  /\ (forall i : Z, 0 <= i < nlen nm -> rd d1 (slot_off blk s + 2 + i) = nchar nm i)
  /\ (nlen nm < 30 -> rd d1 (slot_off blk s + 2 + nlen nm) = 0)
  /\ (forall b : Z, 0 <= b < 512 ->
        (b < 32 * s \/ 32 * s + 32 <= b) ->
        rd d1 (blk * 512 + b) = rd d0 (blk * 512 + b)).

(* ---- the scan frame (identical to FieldToStrFrame.v / DirBlitMarker.v) ---- *)

Lemma scan_frame :
  forall (rda rdb : Z -> Z) (fuel : nat) (off : Z),
    (forall j, (j < fuel)%nat -> rda (off + Z.of_nat j) = rdb (off + Z.of_nat j)) ->
    scan rda off fuel = scan rdb off fuel.
Proof.
  intros rda rdb.
  induction fuel as [| m IH]; intros off Hagree.
  - reflexivity.
  - assert (Hhead : rda off = rdb off).
    { specialize (Hagree 0%nat ltac:(lia)).
      rewrite Z.add_0_r in Hagree. exact Hagree. }
    simpl scan. rewrite Hhead.
    destruct (Z.eqb (rdb off) 0) eqn:Hb.
    + reflexivity.
    + f_equal.
      apply IH. intros j Hj.
      specialize (Hagree (S j) ltac:(lia)).
      replace (Z.succ off + Z.of_nat j) with (off + Z.of_nat (S j)) by lia.
      exact Hagree.
Qed.

Lemma field_to_str_frame :
  forall (rda rdb : Z -> Z) (off width : Z),
    0 <= width ->
    (forall i, 0 <= i < width -> rda (off + i) = rdb (off + i)) ->
    field_to_str rda off width = field_to_str rdb off width.
Proof.
  intros rda rdb off width Hw Hagree.
  unfold field_to_str. apply scan_frame.
  intros j Hj.
  apply Hagree. split.
  - lia.
  - rewrite <- (Z2Nat.id width) by lia.
    apply Nat2Z.inj_lt. exact Hj.
Qed.

(* ---- the byte-region frame -> slot frame bridge, GENERALISED over blk.
 * IDENTICAL to DirBlitMarker.v slot_frame_of_region with 5 -> blk. *)

Lemma slot_frame_of_region_at :
  forall (d0 d1 : disk) (blk s : Z),
    0 <= s < 16 ->
    (forall b : Z, 0 <= b < 512 ->
        (b < 32 * s \/ 32 * s + 32 <= b) ->
        rd d1 (blk * 512 + b) = rd d0 (blk * 512 + b)) ->
    forall k : Z, 0 <= k < 16 -> k <> s ->
      slot_inode d1 blk k = slot_inode d0 blk k /\
      slot_name  d1 blk k = slot_name  d0 blk k.
Proof.
  intros d0 d1 blk s Hs Hframe.
  assert (Hslotbytes :
    forall k : Z, 0 <= k < 16 -> k <> s ->
      forall j, 0 <= j < 32 -> rd d1 (slot_off blk k + j) = rd d0 (slot_off blk k + j)).
  { intros k Hk Hne j Hj.
    assert (Hbeq : slot_off blk k + j = blk * 512 + (32 * k + j)) by (unfold slot_off; lia).
    rewrite Hbeq.
    apply Hframe.
    - lia.
    - destruct (Z_lt_le_dec k s) as [Hks | Hsk].
      + left. lia.
      + right. assert (s < k) by lia. lia. }
  intros k Hk Hne. split.
  - unfold slot_inode.
    pose proof (Hslotbytes k Hk Hne 0 ltac:(lia)) as Hb0k.
    pose proof (Hslotbytes k Hk Hne 1 ltac:(lia)) as Hb1k.
    rewrite Z.add_0_r in Hb0k.
    rewrite Hb0k, Hb1k. reflexivity.
  - unfold slot_name. apply field_to_str_frame; [ lia |].
    intros i Hi.
    replace (slot_off blk k + 2 + i) with (slot_off blk k + (2 + i)) by lia.
    apply (Hslotbytes k Hk Hne (2 + i) ltac:(lia)).
Qed.

(* ---- the name byte->decode round-trip, GENERALISED over blk.
 * scan_recovers is block-agnostic (it quantifies the field offset `off`); only
 * name_round_trip threads slot_off blk s + 2, with 5 -> blk. *)

Lemma scan_recovers :
  forall (rdf : Z -> Z) (nm : name_t) (fuel : nat) (off : Z) (i : Z),
    0 <= i ->
    i + Z.of_nat fuel = 30 ->
    nlen nm <= 30 ->
    i <= nlen nm ->
    (forall t, i <= t < nlen nm -> nchar nm t <> 0) ->
    (forall t, i <= t < nlen nm -> rdf (off + (t - i)) = nchar nm t) ->
    (nlen nm < 30 -> rdf (off + (nlen nm - i)) = 0) ->
    scan rdf off fuel = name_list nm (Z.to_nat (nlen nm - i)) i.
Proof.
  intros rdf nm.
  induction fuel as [| m IH]; intros off i Hi Hwf Hl30 Hile Hnn Hbytes Hnull.
  - assert (nlen nm - i = 0) by lia.
    replace (Z.to_nat (nlen nm - i)) with 0%nat by (rewrite H; reflexivity).
    reflexivity.
  - simpl scan.
    destruct (Z_lt_le_dec i (nlen nm)) as [Hlt | Hge].
    + assert (Hb : rdf off = nchar nm i).
      { specialize (Hbytes i ltac:(lia)).
        replace (off + (i - i)) with off in Hbytes by lia. exact Hbytes. }
      assert (Hnz : nchar nm i <> 0) by (apply Hnn; lia).
      rewrite Hb.
      assert (Heqb : Z.eqb (nchar nm i) 0 = false) by (apply Z.eqb_neq; exact Hnz).
      rewrite Heqb.
      assert (Hstep : Z.to_nat (nlen nm - i) = S (Z.to_nat (nlen nm - (i + 1)))).
      { rewrite <- Z2Nat.inj_succ by lia. f_equal. lia. }
      rewrite Hstep. simpl name_list. f_equal.
      apply IH.
      * lia.
      * lia.
      * lia.
      * lia.
      * intros t Ht. apply Hnn. lia.
      * intros t Ht. specialize (Hbytes t ltac:(lia)).
        replace (Z.succ off + (t - (i + 1))) with (off + (t - i)) by lia. exact Hbytes.
      * intros Hlt2. specialize (Hnull Hlt2).
        replace (Z.succ off + (nlen nm - (i + 1))) with (off + (nlen nm - i)) by lia.
        exact Hnull.
    + assert (Hieq : i = nlen nm) by lia.
      assert (Hlen_lt : nlen nm < 30) by lia.
      assert (Hzero : rdf off = 0).
      { specialize (Hnull Hlen_lt).
        rewrite <- Hieq in Hnull.
        replace (off + (i - i)) with off in Hnull by lia.
        exact Hnull. }
      rewrite Hzero. simpl.
      assert (nlen nm - i = 0) by lia.
      replace (Z.to_nat (nlen nm - i)) with 0%nat by (rewrite H; reflexivity).
      reflexivity.
Qed.

Lemma name_round_trip_at :
  forall (d : disk) (nm : name_t) (blk s : Z),
    0 <= nlen nm -> nlen nm <= 30 ->
    (forall i, 0 <= i < nlen nm -> nchar nm i <> 0) ->
    (forall i, 0 <= i < nlen nm -> rd d (slot_off blk s + 2 + i) = nchar nm i) ->
    (nlen nm < 30 -> rd d (slot_off blk s + 2 + nlen nm) = 0) ->
    slot_name d blk s = name_val nm.
Proof.
  intros d nm blk s Hlen0 Hlen30 Hnn Hbytes Hnull.
  unfold slot_name, field_to_str, name_val.
  rewrite (scan_recovers (rd d) nm (Z.to_nat 30) (slot_off blk s + 2) 0).
  - f_equal. lia.
  - lia.
  - reflexivity.
  - lia.
  - lia.
  - intros t Ht. apply Hnn. lia.
  - intros t Ht.
    replace (slot_off blk s + 2 + (t - 0)) with (slot_off blk s + 2 + t) by lia.
    apply Hbytes. lia.
  - intros Hlt.
    replace (slot_off blk s + 2 + (nlen nm - 0)) with (slot_off blk s + 2 + nlen nm) by lia.
    apply Hnull. lia.
Qed.

(* ---- dir_blit_marker_at_intro: byte facts -> marker (DEFINITIONAL, zero trust) ---- *)

Theorem dir_blit_marker_at_intro :
  forall (d0 d1 : disk) (blk s b0 b1 : Z) (nm : name_t),
    0 <= nlen nm -> nlen nm <= 30 ->
    rd d1 (slot_off blk s) = b0 ->
    rd d1 (slot_off blk s + 1) = b1 ->
    (forall i : Z, 0 <= i < nlen nm -> nchar nm i <> 0) ->
    (forall i : Z, 0 <= i < nlen nm -> rd d1 (slot_off blk s + 2 + i) = nchar nm i) ->
    (nlen nm < 30 -> rd d1 (slot_off blk s + 2 + nlen nm) = 0) ->
    (forall b : Z, 0 <= b < 512 ->
        (b < 32 * s \/ 32 * s + 32 <= b) ->
        rd d1 (blk * 512 + b) = rd d0 (blk * 512 + b)) ->
    dir_blit_marker_at d0 d1 blk s b0 b1 nm.
Proof.
  intros d0 d1 blk s b0 b1 nm Hl0 Hl30 Hb0 Hb1 Hnn Hbytes Hnull Hframe.
  unfold dir_blit_marker_at.
  repeat split; try assumption.
Qed.

Print Assumptions dir_blit_marker_at_intro.

(* ---- dir_blit_marker_at_value_inode: the inode VALUE decode at slot s.
 * From the marker conclude slot_inode d1 blk s = 256*b0+b1 -- the two inode-byte
 * conjuncts only. Zero new TCB. *)

Theorem dir_blit_marker_at_value_inode :
  forall (d0 d1 : disk) (blk s b0 b1 : Z) (nm : name_t),
    dir_blit_marker_at d0 d1 blk s b0 b1 nm ->
    slot_inode d1 blk s = 256 * b0 + b1.
Proof.
  intros d0 d1 blk s b0 b1 nm Hmark.
  destruct Hmark as
    [_ [_ [Hb0 [Hb1 [_ [_ [_ _]]]]]]].
  unfold slot_inode. rewrite Hb0, Hb1. reflexivity.
Qed.

Print Assumptions dir_blit_marker_at_value_inode.

(* ---- dir_blit_marker_at_value_name: the name VALUE decode at slot s.
 * From the marker (= the byte facts, by definition) conclude
 * slot_name d1 blk s = name_val nm, via the byte round-trip. This is the
 * `Hvaln` sub-derivation of dir_blit_marker_insert (name_round_trip), exposed
 * as its own block-parameterized theorem. _write_entry needs it for the
 * slot_name(self.disk, block_num, slot) == name ensures. Zero new TCB. *)

Theorem dir_blit_marker_at_value_name :
  forall (d0 d1 : disk) (blk s b0 b1 : Z) (nm : name_t),
    dir_blit_marker_at d0 d1 blk s b0 b1 nm ->
    slot_name d1 blk s = name_val nm.
Proof.
  intros d0 d1 blk s b0 b1 nm Hmark.
  destruct Hmark as
    [Hnl0 [Hnl30 [_ [_ [Hnn [Hbytes [Hnull _]]]]]]].
  apply name_round_trip_at; assumption.
Qed.

Print Assumptions dir_blit_marker_at_value_name.

(* ---- dir_blit_marker_at_frame_only: the SLOT-LOCALITY FRAME, marker-keyed,
 * GENERALISED over blk. Every slot k <> s decodes identically in d1 and d0 --
 * `slot_frame_of_region_at` applied to the marker's byte-region-frame conjunct.
 * Zero new TCB. *)

Theorem dir_blit_marker_at_frame_only :
  forall (d0 d1 : disk) (blk s b0 b1 : Z) (nm : name_t),
    dir_blit_marker_at d0 d1 blk s b0 b1 nm ->
    0 <= s < 16 ->
    forall k : Z, 0 <= k < 16 -> k <> s ->
      slot_inode d1 blk k = slot_inode d0 blk k /\
      slot_name  d1 blk k = slot_name  d0 blk k.
Proof.
  intros d0 d1 blk s b0 b1 nm Hmark Hs.
  destruct Hmark as
    [_ [_ [_ [_ [_ [_ [_ Hframe]]]]]]].
  exact (slot_frame_of_region_at d0 d1 blk s Hs Hframe).
Qed.

Print Assumptions dir_blit_marker_at_frame_only.

End MarkerAt.
End Dir.
End UnixFs.
