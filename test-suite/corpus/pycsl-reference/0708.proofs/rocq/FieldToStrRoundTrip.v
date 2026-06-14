(* Validation of UnixFs.Field.field_to_str_round_trip (string-codec Phase A').
 *
 * The string <-> fixed-width null-padded byte-field codec ROUND-TRIP. In Why3
 * the axiom is stated over an ABSTRACT logic function
 *
 *   field_to_str : array int -> int -> int -> string
 *
 * constrained ONLY by the round-trip axiom; this file EXHIBITS a concrete model
 * (the scan-to-first-null decode) and proves the round-trip over it, witnessing
 * the axiom's consistency exactly as EmptyDiskSlotsDead.v / Block5DecodeFrame.v
 * do for the abstract slot_inode / slot_name.
 *
 * Faithful interpretation of the Why3 symbols (the cross-validation contract):
 *   - Why3 `string`              <-> `list Z` (a char is its code in 0..255;
 *                                     the round-trip needs no range bound).
 *   - `String.length name`       <-> `Z.of_nat (length name)`.
 *   - `Char.code (Char.get name i)` (the i-th char's byte)
 *                                <-> `nth (Z.to_nat i) name 0`.
 *   - `array int` read `d[b]`    <-> an abstract byte reader `rd : Z -> Z`
 *                                     (rd b = byte b of disk d), as in
 *                                     EmptyDiskSlotsDead.v / Block5DecodeFrame.v.
 *   - `field_to_str d off width` <-> `scan rd off (Z.to_nat width)` : the
 *                                     bytes d[off..off+width), read as chars,
 *                                     up to the first null (Python `'>Ns'`).
 *   - string equality `=`        <-> list equality (Why3 string extensionality
 *                                     -- equal length + equal char-at-i -- IS
 *                                     structural list equality; this is the fact
 *                                     SMT cannot discharge but Rocq gets for free
 *                                     by `induction`).
 *
 * The Why3 axiom's index hypotheses quantify `forall i:int. 0 <= i < length`;
 * here they are stated over `j:nat, j < length name`, the EXACT same index set
 * (a non-negative int below the length is a nat below the length).
 *
 * Verified under Coq 8.20.1. No Admitted, no Axiom (only Section Variables). *)

Require Import Coq.ZArith.ZArith.
Require Import Coq.Lists.List.
Require Import Lia.
Import ListNotations.
Open Scope Z_scope.

Module UnixFs.
Module Field.
Section Codec.

(* The abstract byte reader: rd b is the byte at absolute offset b of the disk. *)
Variable rd : Z -> Z.

(* The concrete decode: read up to `fuel` bytes starting at `off`, stopping at
   the first null byte. This is the faithful model of the Python '>Ns' field
   decode (null-terminated, width-bounded). *)
Fixpoint scan (off : Z) (fuel : nat) : list Z :=
  match fuel with
  | O => []
  | S m => if Z.eqb (rd off) 0 then [] else rd off :: scan (Z.succ off) m
  end.

Definition field_to_str (off width : Z) : list Z := scan off (Z.to_nat width).

(* The byte of name at position j, matching `Char.code (Char.get name j)`. *)
Definition byte_at (name : list Z) (j : nat) : Z := nth j name 0.

(* Core induction: the scan recovers `name` exactly when, within `fuel` bytes,
   every name byte is present, none is null, and (if there is room) a null
   terminator follows. *)
Lemma scan_round_trip :
  forall (name : list Z) (off : Z) (fuel : nat),
    (length name <= fuel)%nat ->
    (forall j, (j < length name)%nat -> byte_at name j <> 0) ->
    (forall j, (j < length name)%nat -> rd (off + Z.of_nat j) = byte_at name j) ->
    ((length name < fuel)%nat -> rd (off + Z.of_nat (length name)) = 0) ->
    scan off fuel = name.
Proof.
  induction name as [| a name' IH]; intros off fuel Hlen Hnn Hbytes Hterm.
  - (* empty name: either fuel = 0, or the terminator byte at off is null. *)
    destruct fuel as [| m].
    + reflexivity.
    + simpl. cbn [length] in Hterm.
      assert (Hz : rd off = 0).
      { specialize (Hterm ltac:(lia)). rewrite Z.add_0_r in Hterm. exact Hterm. }
      rewrite Hz. reflexivity.
  - (* a :: name' : the head byte is present and non-null, recurse on the tail. *)
    destruct fuel as [| m]; [ cbn [length] in Hlen; lia | ].
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

(* The round-trip, stated to MIRROR the Why3 axiom: width is an int with
   0 <= length name <= width; the bytes/no-null/terminator hypotheses are over
   the int index set 0 <= i < length name. *)
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
  (* width >= 0 since length name >= 0; so Z.to_nat width >= length name. *)
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

Print Assumptions field_to_str_round_trip.

End Codec.
End Field.
End UnixFs.
