(* Validation of UnixFs.Dir.slot_name_byte_decode (Gap-5 keystone, STRING half).
 *
 * The byte->decode fact for the directory per-slot NAME field, the string twin
 * of slot_inode_byte_decode (SlotInodeByteDecode.v, the inode half).
 *
 * A directory slot is 32 bytes (struct '>H30s'): a 2-byte big-endian inode field
 * followed by a 30-byte null-padded name field. slot_name (disk, blk, k) is the
 * decoded name in the 30-byte field at byte offset blk*512 + 32*k + 2 of the
 * disk -- i.e. exactly field_to_str disk (blk*512 + 32*k + 2) 30 (the SAME
 * scan-to-first-null '>Ns' decode validated in FieldToStrRoundTrip.v).
 *
 * This file states slot_name OVER the field_to_str codec (slot_name d blk k =
 * field_to_str d (slot_off blk k + 2) 30) and proves the WRITE-DIRECTION
 * round-trip: if the 30 name-field bytes of slot k are byte-for-byte the
 * null-padded encoding of `name` (every name byte present and non-null, a null
 * terminator if shorter than 30, name <= 30), then slot_name d blk k = name.
 *
 * This composes the slot offset (the inode field is 2 bytes, so the name field
 * starts at off + 2) with the already-cross-validated field_to_str round-trip.
 * It lets a directory write helper that has just blitted a fresh dirent name
 * (and proved disk[off+2+i] = ord(name[i]) for i < len, disk[off+2+len] = 0)
 * conclude slot_name d blk k = name -- the string twin of the inode write rung.
 *
 * UNLIKE the inode byte-decode (a finite 2-byte equation SMT applies in O(1)),
 * the name decode is by string EXTENSIONALITY over the 30-byte scan, which
 * E-match-explodes in Alt-Ergo/Z3 (the measured ~23M-step string wall). So this
 * is the SAME cited-axiom trust class as field_to_str_round_trip: SMT only
 * APPLIES it, the extensionality reasoning is discharged here once, offline.
 *
 * Faithful interpretation of the Why3 symbols (the cross-validation contract):
 *   - Why3 `string`              <-> `list Z` (a char is its code; the scan
 *                                     model needs no 0..255 bound).
 *   - `String.length name`       <-> `Z.of_nat (length name)`.
 *   - `Char.code (Char.get name i)` <-> `nth (Z.to_nat i) name 0`.
 *   - `array int` read `d[b]`    <-> abstract byte reader `rd : Z -> Z`.
 *   - `field_to_str d off width` <-> `scan rd off (Z.to_nat width)`
 *                                     (FieldToStrRoundTrip.v, line by line).
 *   - `slot_name d blk k`        <-> `field_to_str (slot_off blk k + 2) 30`.
 *   - string equality `=`        <-> list equality (Why3 string extensionality
 *                                     IS structural list equality; the fact SMT
 *                                     cannot discharge, free here by induction).
 *
 * Verified under Coq 8.20.1. No Admitted, no Axiom (only Section Variables). *)

Require Import Coq.ZArith.ZArith.
Require Import Coq.Lists.List.
Require Import Lia.
Import ListNotations.
Open Scope Z_scope.

Module UnixFs.
Module Dir.
Section Scan.

(* The abstract byte reader: rd b is the byte at absolute offset b of the disk. *)
Variable rd : Z -> Z.

(* ---- The field_to_str codec, identical to FieldToStrRoundTrip.v ---- *)

Fixpoint scan (off : Z) (fuel : nat) : list Z :=
  match fuel with
  | O => []
  | S m => if Z.eqb (rd off) 0 then [] else rd off :: scan (Z.succ off) m
  end.

Definition field_to_str (off width : Z) : list Z := scan off (Z.to_nat width).

Definition byte_at (name : list Z) (j : nat) : Z := nth j name 0.

(* The field_to_str round-trip (re-proved here so this file is self-contained;
   the SAME theorem as FieldToStrRoundTrip.v). *)
Lemma scan_round_trip :
  forall (name : list Z) (off : Z) (fuel : nat),
    (length name <= fuel)%nat ->
    (forall j, (j < length name)%nat -> byte_at name j <> 0) ->
    (forall j, (j < length name)%nat -> rd (off + Z.of_nat j) = byte_at name j) ->
    ((length name < fuel)%nat -> rd (off + Z.of_nat (length name)) = 0) ->
    scan off fuel = name.
Proof.
  induction name as [| a name' IH]; intros off fuel Hlen Hnn Hbytes Hterm.
  - destruct fuel as [| m].
    + reflexivity.
    + simpl. cbn [length] in Hterm.
      assert (Hz : rd off = 0).
      { specialize (Hterm ltac:(lia)). rewrite Z.add_0_r in Hterm. exact Hterm. }
      rewrite Hz. reflexivity.
  - destruct fuel as [| m]; [ cbn [length] in Hlen; lia | ].
    cbn [length] in Hlen.
    assert (Ha : rd off = a).
    { specialize (Hbytes 0%nat ltac:(cbn [length]; lia)).
      unfold byte_at in Hbytes. cbn [nth] in Hbytes.
      rewrite Z.add_0_r in Hbytes. exact Hbytes. }
    assert (Ha0 : a <> 0).
    { specialize (Hnn 0%nat ltac:(cbn [length]; lia)).
      unfold byte_at in Hnn. cbn [nth] in Hnn. exact Hnn. }
    simpl scan. rewrite Ha.
    replace (a =? 0) with false by (symmetry; apply Z.eqb_neq; exact Ha0).
    f_equal.
    apply IH.
    + lia.
    + intros j Hj. specialize (Hnn (S j) ltac:(cbn [length]; lia)).
      unfold byte_at in *. cbn [nth] in Hnn. exact Hnn.
    + intros j Hj. specialize (Hbytes (S j) ltac:(cbn [length]; lia)).
      unfold byte_at in *. cbn [nth] in Hbytes.
      replace (Z.succ off + Z.of_nat j) with (off + Z.of_nat (S j)) by lia.
      exact Hbytes.
    + intros Hlt. specialize (Hterm ltac:(cbn [length]; lia)).
      cbn [length] in Hterm.
      replace (Z.succ off + Z.of_nat (length name')) with
              (off + Z.of_nat (S (length name'))) by lia.
      exact Hterm.
Qed.

Theorem field_to_str_round_trip :
  forall (name : list Z) (off width : Z),
    0 <= Z.of_nat (length name) ->
    Z.of_nat (length name) <= width ->
    (forall i, 0 <= i < Z.of_nat (length name) ->
        nth (Z.to_nat i) name 0 <> 0) ->
    (forall i, 0 <= i < Z.of_nat (length name) ->
        rd (off + i) = nth (Z.to_nat i) name 0) ->
    (Z.of_nat (length name) < width -> rd (off + Z.of_nat (length name)) = 0) ->
    field_to_str off width = name.
Proof.
  intros name off width _ Hle Hnn Hbytes Hterm.
  unfold field_to_str.
  assert (Hw0 : 0 <= width) by lia.
  apply scan_round_trip.
  - rewrite Z2Nat.inj_le in Hle by lia. rewrite Nat2Z.id in Hle. exact Hle.
  - intros j Hj. unfold byte_at.
    specialize (Hnn (Z.of_nat j)).
    rewrite Nat2Z.id in Hnn. apply Hnn. split; [ lia | ]. lia.
  - intros j Hj. unfold byte_at.
    specialize (Hbytes (Z.of_nat j)).
    rewrite Nat2Z.id in Hbytes. rewrite Hbytes; [ reflexivity | ].
    split; [ lia | lia ].
  - intros Hlt. apply Hterm.
    rewrite <- (Z2Nat.id width) by lia.
    rewrite <- Nat2Z.inj_lt. exact Hlt.
Qed.

(* ---- The directory-slot NAME field over the codec ---- *)

(* Slot offset: a slot is 32 bytes, blk is a 512-byte block. *)
Definition slot_off (blk k : Z) : Z := blk * 512 + 32 * k.

(* slot_name reads the 30-byte name field, which starts 2 bytes into the slot
   (after the 2-byte inode field): field_to_str at off + 2, width 30. *)
Definition slot_name (blk k : Z) : list Z := field_to_str (slot_off blk k + 2) 30.

(* WRITE-DIRECTION: if the 30 name-field bytes of slot k are byte-for-byte the
   null-padded encoding of `name` (name fits in 30, no embedded null, the bytes
   are present at off+2+i, a null terminator follows if shorter than 30), then
   slot_name blk k = name. This is field_to_str_round_trip specialised to
   off = slot_off blk k + 2, width = 30. *)
Theorem slot_name_byte_decode :
  forall (name : list Z) (blk k : Z),
    Z.of_nat (length name) <= 30 ->
    (forall i, 0 <= i < Z.of_nat (length name) ->
        nth (Z.to_nat i) name 0 <> 0) ->
    (forall i, 0 <= i < Z.of_nat (length name) ->
        rd (slot_off blk k + 2 + i) = nth (Z.to_nat i) name 0) ->
    (Z.of_nat (length name) < 30 ->
        rd (slot_off blk k + 2 + Z.of_nat (length name)) = 0) ->
    slot_name blk k = name.
Proof.
  intros name blk k Hle Hnn Hbytes Hterm.
  unfold slot_name.
  apply field_to_str_round_trip.
  - lia.
  - exact Hle.
  - exact Hnn.
  - exact Hbytes.
  - exact Hterm.
Qed.

Print Assumptions slot_name_byte_decode.

End Scan.
End Dir.
End UnixFs.
