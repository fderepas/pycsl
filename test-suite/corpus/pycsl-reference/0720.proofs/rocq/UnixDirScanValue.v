(* Value theorem for dir_lookup: the read-side dual of scan_reflects_present.
   Cross-validation spike for the dir_scan_result marker. *)
Require Import Coq.ZArith.ZArith.
Require Import Coq.Bool.Bool.
Require Import Lia.
Open Scope Z_scope.

Module UnixFs.
Module Dir.
Section Scan.
Variable disk : Type.
Variable name_t : Type.
Variable slot_inode : disk -> Z -> Z -> Z.
Variable slot_name  : disk -> Z -> Z -> name_t.
Variable eqn : name_t -> name_t -> bool.
Hypothesis eqn_spec : forall a b, eqn a b = true <-> a = b.
Hypothesis slot_inode_nonneg : forall d blk k, 0 <= slot_inode d blk k.

Definition matches (d : disk) (blk : Z) (name : name_t) (k : Z) : Prop :=
  slot_inode d blk k <> 0 /\ slot_inode d blk k < 32 /\ slot_name d blk k = name.

Fixpoint scan (d : disk) (blk : Z) (name : name_t) (i : nat) (found : Z) : Z :=
  match i with
  | O => found
  | S j =>
      let f := scan d blk name j found in
      let zj := Z.of_nat j in
      if andb (negb (Z.eqb (slot_inode d blk zj) 0))
              (andb (Z.ltb (slot_inode d blk zj) 32)
                    (eqn (slot_name d blk zj) name))
      then slot_inode d blk zj
      else f
  end.

Definition dir_lookup (d : disk) (blk : Z) (name : name_t) : Z :=
  scan d blk name 16 (-1).

(* The MARKER: dir_scan_result d blk name r holds iff r is exactly the
   bounded 16-slot scan result. This is the read-side dual of dir_blit_marker:
   a unique atom that, when established (from the body's loop result), carries
   the VALUE conclusion across SMT. DEFINITIONAL (zero TCB). *)
Definition dir_scan_result (d : disk) (blk : Z) (name : name_t) (r : Z) : Prop :=
  scan d blk name 16 (-1) = r.

(* dir_scan_result_value (cross-validated VALUE lemma): the marker carries the
   value equality dir_lookup = r. Trivial by definition of dir_lookup and the
   marker -- the inductive existential witness is DISCHARGED OFFLINE here. *)
Theorem dir_scan_result_value :
  forall (d : disk) (blk : Z) (name : name_t) (r : Z),
    dir_scan_result d blk name r -> dir_lookup d blk name = r.
Proof.
  intros d blk name r H. unfold dir_lookup, dir_scan_result in *. exact H.
Qed.

(* dir_scan_result_intro (DEFINITIONAL, zero trust): the marker is established
   from the closed loop result.  The body's `found` after the full 16-slot loop
   equals scan d blk name 16 (-1).  Stated over the loop-prefix value invariant:
   if found = scan d blk name 16 (-1), the marker holds. *)
Theorem dir_scan_result_intro :
  forall (d : disk) (blk : Z) (name : name_t) (r : Z),
    scan d blk name 16 (-1) = r -> dir_scan_result d blk name r.
Proof.
  intros. unfold dir_scan_result. exact H.
Qed.

End Scan.
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

(* dir_scan_prefix d blk name i r : "r is the scan result over the first i slots"
   -- the loop-carry marker. i is the loop counter; r is `found`. *)
Definition dir_scan_prefix (d:disk) (blk:Z) (name:name_t) (i:Z) (r:Z) : Prop :=
  (0 <= i <= 16) /\
  UnixFs.Dir.scan disk name_t slot_inode slot_name eqn d blk name (Z.to_nat i) (-1) = r.

(* Base: prefix 0 has result -1 (the loop init). *)
Theorem dir_scan_prefix_base :
  forall d blk name, dir_scan_prefix d blk name 0 (-1).
Proof. intros. unfold dir_scan_prefix. simpl. split; [lia | reflexivity]. Qed.

(* Step: the loop-body update. From prefix i with result r, peeling slot i
   (zi = i) gives prefix (i+1) with the body's `if` update. This is EXACTLY the
   loop body `if name==pathname and inode!=0 and inode<32: found = inode`. *)
Theorem dir_scan_prefix_step :
  forall d blk name i r,
    0 <= i < 16 ->
    dir_scan_prefix d blk name i r ->
    ( (slot_inode d blk i <> 0 /\ slot_inode d blk i < 32 /\ slot_name d blk i = name)
        -> dir_scan_prefix d blk name (i+1) (slot_inode d blk i) ) /\
    ( ~(slot_inode d blk i <> 0 /\ slot_inode d blk i < 32 /\ slot_name d blk i = name)
        -> dir_scan_prefix d blk name (i+1) r ).
Proof.
  intros d blk name i r Hi [Hib Hpre].
  assert (Hni : Z.to_nat (i+1) = S (Z.to_nat i)).
  { rewrite Z2Nat.inj_add by lia. simpl. lia. }
  assert (Hzi : Z.of_nat (Z.to_nat i) = i) by (rewrite Z2Nat.id; lia).
  split.
  - intros [Hne [Hlt Hnm]]. unfold dir_scan_prefix. split; [lia|].
    rewrite Hni. simpl. rewrite Hpre. rewrite Hzi.
    assert (Hg: andb (negb (Z.eqb (slot_inode d blk i) 0))
                     (andb (Z.ltb (slot_inode d blk i) 32)
                           (eqn (slot_name d blk i) name)) = true).
    { apply andb_true_iff. split.
      - apply negb_true_iff. apply Z.eqb_neq. exact Hne.
      - apply andb_true_iff. split. apply Z.ltb_lt. exact Hlt. apply eqn_spec. exact Hnm. }
    rewrite Hg. reflexivity.
  - intros Hno. unfold dir_scan_prefix. split; [lia|].
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

(* Closeout: prefix 16 is the full dir_lookup value. *)
Theorem dir_scan_prefix_close :
  forall d blk name r,
    dir_scan_prefix d blk name 16 r ->
    UnixFs.Dir.dir_lookup disk name_t slot_inode slot_name eqn d blk name = r.
Proof.
  intros d blk name r [_ H]. unfold UnixFs.Dir.dir_lookup.
  simpl in H. exact H.
Qed.

End P.
End Prefix.
