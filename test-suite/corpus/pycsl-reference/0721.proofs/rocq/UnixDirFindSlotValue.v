(* Value theorem for _dir_find_slot: the SLOT-INDEX dual of dir_scan_result.
   _dir_find_slot returns the INDEX (0..15) of the LAST live slot matching
   `name`, or -1 — whereas _dir_lookup (UnixDirScanValue.v) returns the
   matched slot's INODE. This cross-validates the dir_find_slot_result marker
   family: the read-side fidelity that the returned slot index decodes to a
   LIVE entry named `name` (slot_inode <> 0 /\ slot_name = name).

   Same shape and the SAME abstract per-slot decode (slot_inode/slot_name) as
   UnixDirScan.v / UnixDirScanValue.v, over the EXISTING `matches` predicate.
   Verified under Coq 8.20.1. No Admitted, no Axiom (Section Variables only). *)
Require Import Coq.ZArith.ZArith.
Require Import Coq.Bool.Bool.
Require Import Lia.
Open Scope Z_scope.

Module UnixFs.
Module Dir.
Section FindSlot.
Variable disk : Type.
Variable name_t : Type.
Variable slot_inode : disk -> Z -> Z -> Z.
Variable slot_name  : disk -> Z -> Z -> name_t.
Variable eqn : name_t -> name_t -> bool.
Hypothesis eqn_spec : forall a b, eqn a b = true <-> a = b.

(* A slot k is a live match for `name` in block `blk` — IDENTICAL to the
   `matches` of UnixDirScan.v (the inode-range conjunct slot_inode < 32 is
   carried by _dir_find_slot's loop the same way). *)
Definition matches (d : disk) (blk : Z) (name : name_t) (k : Z) : Prop :=
  slot_inode d blk k <> 0 /\ slot_inode d blk k < 32 /\ slot_name d blk k = name.

(* The running SLOT-INDEX scan over the first i slots, mirroring
   _dir_find_slot's loop body `if name==pathname and inode!=0: found = i`.
   It keeps the LAST matching INDEX (recurse first, then test slot j); when
   slot j matches the carried `found` becomes the INDEX zj (not the inode). *)
Fixpoint fscan (d : disk) (blk : Z) (name : name_t) (i : nat) (found : Z) : Z :=
  match i with
  | O => found
  | S j =>
      let f := fscan d blk name j found in
      let zj := Z.of_nat j in
      if andb (negb (Z.eqb (slot_inode d blk zj) 0))
              (andb (Z.ltb (slot_inode d blk zj) 32)
                    (eqn (slot_name d blk zj) name))
      then zj
      else f
  end.

(* The carry invariant proved at every prefix length i: if the running
   index `found` started >= 0 then it is a live match, AND the result is
   either the start value or a live in-range index. We instantiate at the
   loop init found = -1 below; the general form makes the induction go
   through cleanly. *)
Lemma fscan_result_matches : forall (d : disk) (blk : Z) (name : name_t) (i : nat) (start : Z),
  let r := fscan d blk name i start in
  ( (0 <= r < Z.of_nat i /\ matches d blk name r) \/ r = start ).
Proof.
  intros d blk name i start. induction i as [| j IH].
  - (* base: fscan = start. *)
    simpl. right. reflexivity.
  - (* step: peel slot j. *)
    simpl.
    set (zj := Z.of_nat j) in *.
    remember (andb (negb (Z.eqb (slot_inode d blk zj) 0))
                   (andb (Z.ltb (slot_inode d blk zj) 32)
                         (eqn (slot_name d blk zj) name))) as guard eqn:Hguard.
    destruct guard.
    + (* guard true: result = index zj, a live match. *)
      symmetry in Hguard.
      apply andb_true_iff in Hguard. destruct Hguard as [Hne Hrest].
      apply andb_true_iff in Hrest. destruct Hrest as [Hlt Heqn].
      apply negb_true_iff in Hne. apply Z.eqb_neq in Hne.
      apply Z.ltb_lt in Hlt. apply eqn_spec in Heqn.
      left. split.
      * split. apply Nat2Z.is_nonneg. lia.
      * unfold matches. repeat split; assumption.
    + (* guard false: result = fscan over j; classify via IH. *)
      destruct IH as [ [Hrng Hm] | Heq ].
      * left. split; [ lia | exact Hm ].
      * right. exact Heq.
Qed.

(* dir_find_slot d blk name := fscan d blk name 16 (-1). *)
Definition dir_find_slot (d : disk) (blk : Z) (name : name_t) : Z :=
  fscan d blk name 16 (-1).

(* The MARKER: dir_find_slot_result d blk name r holds iff r is exactly the
   bounded 16-slot index scan result. DEFINITIONAL (zero TCB). *)
Definition dir_find_slot_result (d : disk) (blk : Z) (name : name_t) (r : Z) : Prop :=
  fscan d blk name 16 (-1) = r.

(* dir_find_slot_result_intro (DEFINITIONAL, zero trust): the marker from the
   closed loop result. *)
Theorem dir_find_slot_result_intro :
  forall (d : disk) (blk : Z) (name : name_t) (r : Z),
    fscan d blk name 16 (-1) = r -> dir_find_slot_result d blk name r.
Proof. intros. unfold dir_find_slot_result. exact H. Qed.

(* dir_find_slot_result_value (cross-validated VALUE lemma — the load-bearing
   slot-index fidelity): when r >= 0, slot r decodes to a live entry named
   `name`. This is exactly _dir_find_slot's two fidelity ensures
   (slot_inode <> 0  /\  slot_name = name). The whole last-match argument is
   discharged offline here; SMT only applies this O(1) implication. *)
Theorem dir_find_slot_result_value :
  forall (d : disk) (blk : Z) (name : name_t) (r : Z),
    dir_find_slot_result d blk name r ->
    r >= 0 ->
    slot_inode d blk r <> 0 /\ slot_name d blk r = name.
Proof.
  intros d blk name r Hmk Hpos. unfold dir_find_slot_result in Hmk.
  pose proof (fscan_result_matches d blk name 16 (-1)) as Hinv.
  cbv zeta in Hinv. rewrite Hmk in Hinv.
  destruct Hinv as [ [Hrng Hm] | Heq ].
  - unfold matches in Hm. destruct Hm as [Hne [_ Hnm]]. split; assumption.
  - (* r = -1 here (start = -1), contradicts r >= 0 *)
    lia.
Qed.

(* dir_find_slot_result_range (DEFINITIONAL, zero trust): r is in [-1, 16).
   Mirrors _dir_find_slot's `\result >= -1 and \result < 16` (the body proves
   the range directly; this lemma confirms the marker is consistent with it). *)
Theorem dir_find_slot_result_range :
  forall (d : disk) (blk : Z) (name : name_t) (r : Z),
    dir_find_slot_result d blk name r -> -1 <= r < 16.
Proof.
  intros d blk name r Hmk. unfold dir_find_slot_result in Hmk.
  pose proof (fscan_result_matches d blk name 16 (-1)) as Hinv.
  cbv zeta in Hinv. rewrite Hmk in Hinv.
  replace (Z.of_nat 16) with 16 in Hinv by reflexivity.
  destruct Hinv as [ [Hrng _] | Heq ].
  - lia.
  - lia.
Qed.

End FindSlot.
End Dir.
End UnixFs.

(* ===== Prefix-marker form: a NON-inductive loop-carry rung ===== *)
Module Prefix.
Section P.
Variable disk : Type.
Variable name_t : Type.
Variable slot_inode : disk -> Z -> Z -> Z.
Variable slot_name  : disk -> Z -> Z -> name_t.
Variable eqn : name_t -> name_t -> bool.
Hypothesis eqn_spec : forall a b, eqn a b = true <-> a = b.

(* dir_find_slot_prefix d blk name i r : "r is the index-scan result over the
   first i slots" -- the loop-carry marker. i is the loop counter; r is
   `found` (the slot index). *)
Definition dir_find_slot_prefix (d:disk) (blk:Z) (name:name_t) (i:Z) (r:Z) : Prop :=
  (0 <= i <= 16) /\
  UnixFs.Dir.fscan disk name_t slot_inode slot_name eqn d blk name (Z.to_nat i) (-1) = r.

(* Base: prefix 0 has result -1 (the loop init). *)
Theorem dir_find_slot_prefix_base :
  forall d blk name, dir_find_slot_prefix d blk name 0 (-1).
Proof. intros. unfold dir_find_slot_prefix. simpl. split; [lia | reflexivity]. Qed.

(* Step: the loop-body update. From prefix i with result r, peeling slot i
   (zi = i) gives prefix (i+1) with the body's `if` update. This is EXACTLY
   the loop body `if name==pathname and inode!=0: found = i` (when matched,
   found becomes the INDEX i, not the inode). *)
Theorem dir_find_slot_prefix_step :
  forall d blk name i r,
    0 <= i < 16 ->
    dir_find_slot_prefix d blk name i r ->
    ( (slot_inode d blk i <> 0 /\ slot_inode d blk i < 32 /\ slot_name d blk i = name)
        -> dir_find_slot_prefix d blk name (i+1) i ) /\
    ( ~(slot_inode d blk i <> 0 /\ slot_inode d blk i < 32 /\ slot_name d blk i = name)
        -> dir_find_slot_prefix d blk name (i+1) r ).
Proof.
  intros d blk name i r Hi [Hib Hpre].
  assert (Hni : Z.to_nat (i+1) = S (Z.to_nat i)).
  { rewrite Z2Nat.inj_add by lia. simpl. lia. }
  assert (Hzi : Z.of_nat (Z.to_nat i) = i) by (rewrite Z2Nat.id; lia).
  split.
  - intros [Hne [Hlt Hnm]]. unfold dir_find_slot_prefix. split; [lia|].
    rewrite Hni. simpl. rewrite Hpre. rewrite Hzi.
    assert (Hg: andb (negb (Z.eqb (slot_inode d blk i) 0))
                     (andb (Z.ltb (slot_inode d blk i) 32)
                           (eqn (slot_name d blk i) name)) = true).
    { apply andb_true_iff. split.
      - apply negb_true_iff. apply Z.eqb_neq. exact Hne.
      - apply andb_true_iff. split. apply Z.ltb_lt. exact Hlt. apply eqn_spec. exact Hnm. }
    rewrite Hg. reflexivity.
  - intros Hno. unfold dir_find_slot_prefix. split; [lia|].
    rewrite Hni. simpl. rewrite Hpre. rewrite Hzi.
    assert (Hg: andb (negb (Z.eqb (slot_inode d blk i) 0))
                     (andb (Z.ltb (slot_inode d blk i) 32)
                           (eqn (slot_name d blk i) name)) = false).
    { destruct (andb (negb (Z.eqb (slot_inode d blk i) 0))
                     (andb (Z.ltb (slot_inode d blk i) 32)
                           (eqn (slot_name d blk i) name))) eqn:E; [|reflexivity].
      exfalso. apply Hno.
      apply andb_true_iff in E. destruct E as [E1 E2].
      apply andb_true_iff in E2. destruct E2 as [E2 E3].
      apply negb_true_iff in E1. apply Z.eqb_neq in E1.
      apply Z.ltb_lt in E2. apply eqn_spec in E3. tauto. }
    rewrite Hg. reflexivity.
Qed.

(* Closeout: prefix 16 is the full dir_find_slot value, folded to the result
   marker. *)
Theorem dir_find_slot_prefix_close :
  forall d blk name r,
    dir_find_slot_prefix d blk name 16 r ->
    UnixFs.Dir.dir_find_slot_result disk name_t slot_inode slot_name eqn d blk name r.
Proof.
  intros d blk name r [_ H]. unfold UnixFs.Dir.dir_find_slot_result.
  simpl in H. exact H.
Qed.

End P.
End Prefix.
