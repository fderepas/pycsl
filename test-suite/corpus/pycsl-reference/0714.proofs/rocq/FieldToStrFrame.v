(* Validation of UnixFs.Field.field_to_str_frame (string-codec Phase A',
 * DISJOINT-REGION FRAME).
 *
 * The byte-locality twin of field_to_str_round_trip. In Why3 the axiom is
 * stated over an ABSTRACT logic function
 *
 *   field_to_str : array int -> int -> int -> string
 *
 * constrained only by axioms; this file EXHIBITS the SAME concrete model as
 * FieldToStrRoundTrip.v (the scan-to-first-null decode) and proves the frame
 * over it, witnessing the axiom's consistency.
 *
 * The frame: the decode of a `width`-byte null-padded field at `off` depends
 * ONLY on the bytes d[off..off+width). If two disks d0, d1 agree byte-for-byte
 * over that window, they decode to the SAME name. This is the disjoint-region
 * twin of the retired block5_decode_frame (which required FULL block agreement);
 * a blit rewriting one slot leaves every OTHER slot's name window untouched, so
 * agreement on the single field's window is all this frame asks for.
 *
 * Faithful interpretation of the Why3 symbols (the cross-validation contract,
 * IDENTICAL to FieldToStrRoundTrip.v):
 *   - Why3 `string`              <-> `list Z`.
 *   - `array int` read `d[b]`    <-> an abstract byte reader `rd : Z -> Z`.
 *   - `field_to_str d off width` <-> `scan rd off (Z.to_nat width)` : the
 *                                     bytes d[off..off+width), read as chars,
 *                                     up to the first null (Python `'>Ns'`).
 *   - string equality `=`        <-> list equality.
 *
 * Two disks d0, d1 are modelled by two abstract byte readers rd0, rd1; the
 * byte-frame antecedent `forall i. 0 <= i < width -> d0[off+i] = d1[off+i]`
 * becomes `forall i. 0 <= i < width -> rd0 (off+i) = rd1 (off+i)`.
 *
 * Verified under Coq 8.20.1. No Admitted, no Axiom (only Section Variables). *)

Require Import Coq.ZArith.ZArith.
Require Import Coq.Lists.List.
Require Import Lia.
Import ListNotations.
Open Scope Z_scope.

Module UnixFs.
Module Field.
Section Frame.

(* Two abstract byte readers, one per disk state. *)
Variable rd0 : Z -> Z.
Variable rd1 : Z -> Z.

(* The concrete decode: read up to `fuel` bytes from `off`, stopping at the
   first null byte (the SAME scan as FieldToStrRoundTrip.v). *)
Fixpoint scan (rd : Z -> Z) (off : Z) (fuel : nat) : list Z :=
  match fuel with
  | O => []
  | S m => if Z.eqb (rd off) 0 then [] else rd off :: scan rd (Z.succ off) m
  end.

Definition field_to_str (rd : Z -> Z) (off width : Z) : list Z :=
  scan rd off (Z.to_nat width).

(* Core induction: if rd0 and rd1 agree on every offset the scan reads within
   `fuel` bytes from `off`, the two scans are equal. The scan reads off,
   off+1, ..., off+fuel-1, i.e. off + j for 0 <= j < fuel; the hypothesis is
   stated over exactly that index set. *)
Lemma scan_frame :
  forall (fuel : nat) (off : Z),
    (forall j, (j < fuel)%nat -> rd0 (off + Z.of_nat j) = rd1 (off + Z.of_nat j)) ->
    scan rd0 off fuel = scan rd1 off fuel.
Proof.
  induction fuel as [| m IH]; intros off Hagree.
  - reflexivity.
  - (* head byte: rd0 off = rd1 off (j = 0). *)
    assert (Hhead : rd0 off = rd1 off).
    { specialize (Hagree 0%nat ltac:(lia)).
      rewrite Z.add_0_r in Hagree. exact Hagree. }
    simpl scan. rewrite Hhead.
    destruct (Z.eqb (rd1 off) 0) eqn:Hb.
    + reflexivity.
    + f_equal.
      apply IH. intros j Hj.
      specialize (Hagree (S j) ltac:(lia)).
      replace (Z.succ off + Z.of_nat j) with (off + Z.of_nat (S j)) by lia.
      exact Hagree.
Qed.

(* The frame, stated to MIRROR the Why3 axiom: width is an int with 0 <= width;
   the byte-agreement hypothesis is over the int index set 0 <= i < width. *)
Theorem field_to_str_frame :
  forall (off width : Z),
    0 <= width ->
    (forall i, 0 <= i < width -> rd0 (off + i) = rd1 (off + i)) ->
    field_to_str rd0 off width = field_to_str rd1 off width.
Proof.
  intros off width Hw Hagree.
  unfold field_to_str.
  apply scan_frame.
  intros j Hj.
  (* j < Z.to_nat width  ->  0 <= Z.of_nat j < width *)
  apply Hagree.
  split.
  - lia.
  - rewrite <- (Z2Nat.id width) by lia.
    apply Nat2Z.inj_lt. exact Hj.
Qed.

Print Assumptions field_to_str_frame.

End Frame.
End Field.
End UnixFs.
