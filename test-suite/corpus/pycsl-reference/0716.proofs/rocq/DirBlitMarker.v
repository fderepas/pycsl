(* Validation of the ROUTE-1 UNIQUE-MARKER form of the folded byte-rung
 * directory-invariant maintenance facts:
 *   UnixFs.Dir.dir_blit_marker_intro
 *   UnixFs.Dir.dir_blit_marker_insert
 *
 * CONTEXT (test-supervise-sl route 1, 2026-06-19): the byte-keyed fold
 * insert/zero_preserves_dir_invariant_blit (0715, keyed [d1[2560 + 32*s]]) is
 * correct logic but its byte key matches the SHAPE disk[2560 + <expr>] that every
 * block-5 byte read produces, so the WhyML axiom fires inside the pure-byte helper
 * _blit_dir_entry and E-match-explodes. Worse, citing the byte VALUE keystones
 * (slot_inode_byte_decode keyed [disk[blk*512+32*k]], slot_name_byte_decode,
 * field_to_str_round_trip) at the real mutator EMITS them MODULE-WIDE, and their
 * generic disk[...] / field_to_str triggers E-match-explode _blit_dir_entry's
 * _pad_name byte loop (Timeout 8,605,711,403 steps, measured).
 *
 * THE FIX: route the ENTIRE maintenance fact — including BOTH slot VALUE decodes
 * (inode AND name) — through a SINGLE UNIQUE uninterpreted predicate
 *   dir_blit_marker d0 d1 s b0 b1 name
 * whose WhyML trigger is [dir_blit_marker d0 d1 s b0 b1 name]. The marker atom
 * materializes ONLY where the genuine mutator body asserts it; the os body cites
 * ONLY the marker intro+insert (NOT slot_inode_byte_decode / slot_name_byte_decode /
 * field_to_str_round_trip), so NO byte-decode/string keystone is emitted module-wide
 * and NO sibling byte mutator is poisoned. All the byte->slot and byte->string
 * decode reasoning is discharged INSIDE this kernel proof.
 *
 * Faithful interpretation (the cross-validation contract — IDENTICAL to
 * SlotInodeByteDecode.v / SlotNameByteDecode.v / FieldToStrRoundTrip.v /
 * FieldToStrFrame.v / DirInvariantMaintenance.v for the shared symbols):
 *   - `array int` read d[b]    <-> abstract byte reader rd : disk -> Z -> Z.
 *   - slot_inode d blk k       <-> 256 * rd d (slot_off blk k) + rd d (slot_off blk k + 1).
 *   - slot_name d blk k        <-> field_to_str over rd d (scan-to-first-null name
 *                                  decode of the 30-byte field at slot_off blk k + 2).
 *   - uniq / slots_lt32        <-> the FOLDED block-5 predicates.
 *   - dir_blit_marker d0 d1 s b0 b1 name <-> the CONJUNCTION of ALL byte facts a blit
 *                                  at slot s establishes (the two inode bytes, the
 *                                  per-char name-field bytes, the null-pad, the
 *                                  byte-region frame) PLUS the name well-formedness the
 *                                  round-trip needs (len<=30, no embedded null). A
 *                                  CONSERVATIVE DEFINITION of the abstract WhyML
 *                                  predicate, so the intro is definitional (one
 *                                  direction of the iff) and the insert theorem unfolds
 *                                  it and derives the conclusion.
 *
 * Verified under Coq 8.20.x.  No Admitted, no Axiom (only Section Variables). *)

Require Import Coq.ZArith.ZArith.
Require Import Coq.Lists.List.
Require Import Lia.
Import ListNotations.
Open Scope Z_scope.

Module UnixFs.
Module Dir.
Section Marker.

Variable disk : Type.
(* rd d b : the byte at offset b of disk d. *)
Variable rd : disk -> Z -> Z.

(* The name is modelled (as in FieldToStrRoundTrip.v) as a list of its char
 * codes; `nchar nm i` is the code of char i, `nlen nm` is its length. *)
Variable name_t : Type.
Variable nchar : name_t -> Z -> Z.
Variable nlen : name_t -> Z.

Definition slot_off (blk k : Z) : Z := blk * 512 + 32 * k.

(* ---- the concrete decodes (identical to the keystone proofs) ---- *)

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

(* the name as its char-code list (the value `slot_name` is compared against) *)
Fixpoint name_list (nm : name_t) (fuel : nat) (i : Z) : list Z :=
  match fuel with
  | O => []
  | S m => nchar nm i :: name_list nm m (i + 1)
  end.

Definition name_val (nm : name_t) : list Z := name_list nm (Z.to_nat (nlen nm)) 0.

(* ---- the FOLDED block-5 invariants (identical to DirInvariantMaintenance.v) ---- *)

Definition uniq (d : disk) : Prop :=
  forall i j : Z,
    0 <= i < 16 -> 0 <= j < 16 ->
    slot_inode d 5 i <> 0 -> slot_inode d 5 i < 32 ->
    slot_inode d 5 j <> 0 -> slot_inode d 5 j < 32 ->
    slot_name d 5 i = slot_name d 5 j -> i = j.

Definition slots_lt32 (d : disk) : Prop :=
  forall k : Z, 0 <= k < 16 -> slot_inode d 5 k < 32.

(* ---- THE MARKER: the conservative DEFINITION of the abstract WhyML predicate ----
 *
 * `dir_blit_marker d0 d1 s b0 b1 nm` is DEFINED as the conjunction of ALL the byte
 * facts a blit at slot s establishes plus the name well-formedness. This makes the
 * intro one direction of an iff (definitional, zero trust) and packages the byte +
 * string facts so the insert theorem carries only the marker. *)

Definition dir_blit_marker (d0 d1 : disk) (s b0 b1 : Z) (nm : name_t) : Prop :=
  0 <= nlen nm
  /\ nlen nm <= 30
  /\ rd d1 (slot_off 5 s) = b0
  /\ rd d1 (slot_off 5 s + 1) = b1
  /\ (forall i : Z, 0 <= i < nlen nm -> nchar nm i <> 0)
  /\ (forall i : Z, 0 <= i < nlen nm -> rd d1 (slot_off 5 s + 2 + i) = nchar nm i)
  /\ (nlen nm < 30 -> rd d1 (slot_off 5 s + 2 + nlen nm) = 0)
  /\ (forall b : Z, 0 <= b < 512 ->
        (b < 32 * s \/ 32 * s + 32 <= b) ->
        rd d1 (5 * 512 + b) = rd d0 (5 * 512 + b)).

(* ---- the scan frame (identical to FieldToStrFrame.v) ---- *)

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

(* ---- the byte-region frame -> slot frame bridge (the heart of the fold) ----
 * IDENTICAL to 0715 DirBlitInvariant.v, proved ONCE and applied opaquely. *)

Lemma slot_frame_of_region :
  forall (d0 d1 : disk) (s : Z),
    0 <= s < 16 ->
    (forall b : Z, 0 <= b < 512 ->
        (b < 32 * s \/ 32 * s + 32 <= b) ->
        rd d1 (5 * 512 + b) = rd d0 (5 * 512 + b)) ->
    forall k : Z, 0 <= k < 16 -> k <> s ->
      slot_inode d1 5 k = slot_inode d0 5 k /\
      slot_name  d1 5 k = slot_name  d0 5 k.
Proof.
  intros d0 d1 s Hs Hframe.
  assert (Hslotbytes :
    forall k : Z, 0 <= k < 16 -> k <> s ->
      forall j, 0 <= j < 32 -> rd d1 (slot_off 5 k + j) = rd d0 (slot_off 5 k + j)).
  { intros k Hk Hne j Hj.
    assert (Hbeq : slot_off 5 k + j = 5 * 512 + (32 * k + j)) by (unfold slot_off; lia).
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
    replace (slot_off 5 k + 2 + i) with (slot_off 5 k + (2 + i)) by lia.
    apply (Hslotbytes k Hk Hne (2 + i) ltac:(lia)).
Qed.

(* ---- the name byte->decode round-trip (identical model to FieldToStrRoundTrip.v) ----
 *
 * If the field at off holds the name's char codes for i < len, a null at len (when
 * len < width), and len <= width with no embedded null, then field_to_str off width
 * recovers the name's char-code list. Proved by induction on the field width / fuel. *)

(* fuel is exactly the number of remaining field bytes (width - i). At i = nlen nm:
 * if fuel = 0 we are at the field boundary (len = width), base case; if fuel > 0 the
 * field has a trailing null (len < width), which scan reads to stop. We carry the
 * invariant `nlen nm - i = Z.of_nat fuel`-free by guarding the null hypothesis with
 * `nlen nm < off-relative width`, supplied as `i < nlen nm \/ (i = nlen nm /\ fuel>0
 * -> null)`. We keep it simple: the os call always has fuel = 30 - i, len <= 30. *)
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
  - (* fuel = 0 => i = 30 >= nlen nm and i <= nlen nm => nlen nm - i = 0 *)
    assert (nlen nm - i = 0) by lia.
    replace (Z.to_nat (nlen nm - i)) with 0%nat by (rewrite H; reflexivity).
    reflexivity.
  - simpl scan.
    destruct (Z_lt_le_dec i (nlen nm)) as [Hlt | Hge].
    + (* i < nlen nm : the byte is the (nonzero) char code, recurse *)
      assert (Hb : rdf off = nchar nm i).
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
    + (* i = nlen nm : len < 30 (since fuel = S m > 0 => i = 30 - S m < 30, and
         i = nlen nm), so the trailing null fires; scan stops, name_list empty *)
      assert (Hieq : i = nlen nm) by lia.
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

Lemma name_round_trip :
  forall (d : disk) (nm : name_t) (s : Z),
    0 <= nlen nm -> nlen nm <= 30 ->
    (forall i, 0 <= i < nlen nm -> nchar nm i <> 0) ->
    (forall i, 0 <= i < nlen nm -> rd d (slot_off 5 s + 2 + i) = nchar nm i) ->
    (nlen nm < 30 -> rd d (slot_off 5 s + 2 + nlen nm) = 0) ->
    slot_name d 5 s = name_val nm.
Proof.
  intros d nm s Hlen0 Hlen30 Hnn Hbytes Hnull.
  unfold slot_name, field_to_str, name_val.
  rewrite (scan_recovers (rd d) nm (Z.to_nat 30) (slot_off 5 s + 2) 0).
  - f_equal. lia.
  - lia.
  - reflexivity.
  - lia.
  - lia.
  - intros t Ht. apply Hnn. lia.
  - intros t Ht.
    replace (slot_off 5 s + 2 + (t - 0)) with (slot_off 5 s + 2 + t) by lia.
    apply Hbytes. lia.
  - intros Hlt.
    replace (slot_off 5 s + 2 + (nlen nm - 0)) with (slot_off 5 s + 2 + nlen nm) by lia.
    apply Hnull. lia.
Qed.

(* ---- dir_blit_marker_intro: byte facts -> marker (DEFINITIONAL, zero trust) ---- *)

Theorem dir_blit_marker_intro :
  forall (d0 d1 : disk) (s b0 b1 : Z) (nm : name_t),
    0 <= nlen nm -> nlen nm <= 30 ->
    rd d1 (slot_off 5 s) = b0 ->
    rd d1 (slot_off 5 s + 1) = b1 ->
    (forall i : Z, 0 <= i < nlen nm -> nchar nm i <> 0) ->
    (forall i : Z, 0 <= i < nlen nm -> rd d1 (slot_off 5 s + 2 + i) = nchar nm i) ->
    (nlen nm < 30 -> rd d1 (slot_off 5 s + 2 + nlen nm) = 0) ->
    (forall b : Z, 0 <= b < 512 ->
        (b < 32 * s \/ 32 * s + 32 <= b) ->
        rd d1 (5 * 512 + b) = rd d0 (5 * 512 + b)) ->
    dir_blit_marker d0 d1 s b0 b1 nm.
Proof.
  intros d0 d1 s b0 b1 nm Hl0 Hl30 Hb0 Hb1 Hnn Hbytes Hnull Hframe.
  unfold dir_blit_marker.
  repeat split; try assumption.
Qed.

Print Assumptions dir_blit_marker_intro.

(* ---- dir_blit_marker_insert: marker + uniq/slots_lt32 d0 + range + freshness
 *      -> slot_inode value + slot_name value (= name_val) + frame + uniq d1 +
 *      slots_lt32 d1.  Same invariant logic as 0715, with the name VALUE derived
 *      from the byte round-trip, all behind the marker. *)

Theorem dir_blit_marker_insert :
  forall (d0 d1 : disk) (s b0 b1 : Z) (nm : name_t),
    dir_blit_marker d0 d1 s b0 b1 nm ->
    uniq d0 ->
    slots_lt32 d0 ->
    0 <= s < 16 ->
    256 * b0 + b1 <> 0 ->
    256 * b0 + b1 < 32 ->
    (forall k : Z, 0 <= k < 16 -> k <> s ->
        slot_inode d0 5 k <> 0 -> slot_inode d0 5 k < 32 ->
        slot_name d0 5 k <> name_val nm) ->
       slot_inode d1 5 s = 256 * b0 + b1
    /\ slot_name d1 5 s = name_val nm
    /\ (forall k : Z, 0 <= k < 16 -> k <> s ->
           slot_inode d1 5 k = slot_inode d0 5 k /\
           slot_name  d1 5 k = slot_name  d0 5 k)
    /\ uniq d1
    /\ slots_lt32 d1.
Proof.
  intros d0 d1 s b0 b1 nm Hmark Hu0 Hl0 Hs Hlive Hlt Hfresh.
  destruct Hmark as
    [Hnl0 [Hnl30 [Hb0 [Hb1 [Hnn [Hbytes [Hnull Hframe]]]]]]].
  pose proof (slot_frame_of_region d0 d1 s Hs Hframe) as Hsf.
  assert (Hvali : slot_inode d1 5 s = 256 * b0 + b1).
  { unfold slot_inode. rewrite Hb0, Hb1. reflexivity. }
  assert (Hvaln : slot_name d1 5 s = name_val nm).
  { apply name_round_trip; assumption. }
  assert (Hu1 : uniq d1).
  { intros i j Hi Hj Hil Hilt Hjl Hjlt Hnm.
    destruct (Z.eq_dec i s) as [His | His];
    destruct (Z.eq_dec j s) as [Hjs | Hjs].
    - subst; reflexivity.
    - exfalso. subst i.
      destruct (Hsf j Hj Hjs) as [Hji Hjn].
      apply (Hfresh j Hj Hjs).
      + rewrite <- Hji; exact Hjl.
      + rewrite <- Hji; exact Hjlt.
      + rewrite <- Hjn, <- Hnm, Hvaln. reflexivity.
    - exfalso. subst j.
      destruct (Hsf i Hi His) as [Hii Hin].
      apply (Hfresh i Hi His).
      + rewrite <- Hii; exact Hil.
      + rewrite <- Hii; exact Hilt.
      + rewrite <- Hin, Hnm, Hvaln. reflexivity.
    - destruct (Hsf i Hi His) as [Hii Hin].
      destruct (Hsf j Hj Hjs) as [Hji Hjn].
      apply (Hu0 i j Hi Hj).
      + rewrite <- Hii; exact Hil.
      + rewrite <- Hii; exact Hilt.
      + rewrite <- Hji; exact Hjl.
      + rewrite <- Hji; exact Hjlt.
      + rewrite <- Hin, <- Hjn; exact Hnm. }
  assert (Hl1 : slots_lt32 d1).
  { intros k Hk. destruct (Z.eq_dec k s) as [He | Hne].
    - subst k. rewrite Hvali. exact Hlt.
    - destruct (Hsf k Hk Hne) as [Hki _]. rewrite Hki. apply Hl0. exact Hk. }
  exact (conj Hvali (conj Hvaln (conj Hsf (conj Hu1 Hl1)))).
Qed.

Print Assumptions dir_blit_marker_insert.

(* ---- dir_blit_marker_frame_only (SPIKE-2): the SLOT-LOCALITY FRAME alone.
 * A STRICT corollary of the marker: every slot k <> s decodes identically in
 * d1 and d0 — needing ONLY the marker (= the byte facts, by definition) and the
 * slot-in-range fact, NOT uniq/slots_lt32/range/freshness. It is exactly
 * `slot_frame_of_region` applied to the marker's byte-region-frame conjunct (the
 * SAME sub-derivation dir_blit_marker_insert performs to obtain its frame
 * conjunct Hsf). Exposed as its own theorem so the WhyML lean frame-only
 * marker-keyed axiom can close _write_dir_entry's two `forall k<>s` frame
 * postconditions DIRECTLY in the full-module aggregate context. Zero new TCB. *)

Theorem dir_blit_marker_frame_only :
  forall (d0 d1 : disk) (s b0 b1 : Z) (nm : name_t),
    dir_blit_marker d0 d1 s b0 b1 nm ->
    0 <= s < 16 ->
    forall k : Z, 0 <= k < 16 -> k <> s ->
      slot_inode d1 5 k = slot_inode d0 5 k /\
      slot_name  d1 5 k = slot_name  d0 5 k.
Proof.
  intros d0 d1 s b0 b1 nm Hmark Hs.
  destruct Hmark as
    [_ [_ [_ [_ [_ [_ [_ Hframe]]]]]]].
  exact (slot_frame_of_region d0 d1 s Hs Hframe).
Qed.

Print Assumptions dir_blit_marker_frame_only.

End Marker.
End Dir.
End UnixFs.
