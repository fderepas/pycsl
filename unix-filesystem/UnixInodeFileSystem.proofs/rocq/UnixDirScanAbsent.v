(* unix-filesystem/UnixInodeFileSystem.proofs/rocq/UnixDirScanAbsent.v
 *
 * Validation of UnixFs.Dir.remove_reflects_absent (gap-11).
 *
 * Reuses the scan_reflects_prefix induction (gap-9) verbatim, then derives
 * the ABSENCE direction: after zeroing the matching slot s (slot s now dead,
 * remove-witness) and under name-uniqueness (no OTHER live slot decodes to
 * `name`), the bounded scan returns < 0.
 *
 * Verified under Coq 8.20.1. No Admitted, no Axiom. *)

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

(* gap-9 lemma, verbatim. *)
Lemma scan_reflects_prefix : forall (d : disk) (blk : Z) (name : name_t) (i : nat),
  ( (scan d blk name i (-1) >= 0)
    <-> (exists k : Z, 0 <= k < Z.of_nat i /\ matches d blk name k) )
  /\ ( scan d blk name i (-1) >= 0 -> scan d blk name i (-1) < 32 ).
Proof.
  intros d blk name i. induction i as [| j IH].
  - simpl. split.
    + split.
      * intro H. lia.
      * intros [k [Hk _]]. lia.
    + intro H. lia.
  - destruct IH as [IHiff IHrng].
    simpl.
    set (zj := Z.of_nat j) in *.
    remember (andb (negb (Z.eqb (slot_inode d blk zj) 0))
                   (andb (Z.ltb (slot_inode d blk zj) 32)
                         (eqn (slot_name d blk zj) name))) as guard eqn:Hguard.
    destruct guard.
    + symmetry in Hguard.
      apply andb_true_iff in Hguard. destruct Hguard as [Hne Hrest].
      apply andb_true_iff in Hrest. destruct Hrest as [Hlt Heqn].
      apply negb_true_iff in Hne. apply Z.eqb_neq in Hne.
      apply Z.ltb_lt in Hlt.
      apply eqn_spec in Heqn.
      assert (Hm : matches d blk name zj).
      { unfold matches. repeat split; assumption. }
      split.
      * split.
        -- intro _H. exists zj. split; [ split; [ apply Nat2Z.is_nonneg | lia ] | exact Hm ].
        -- intro _H. pose proof (slot_inode_nonneg d blk zj). lia.
      * intro _H. lia.
    + symmetry in Hguard.
      split.
      * rewrite IHiff. split.
        -- intros [k [Hk Hm]]. exists k. split; [ split; [ lia | lia ] | exact Hm ].
        -- intros [k [Hk Hm]].
           assert (Hkj : k < zj \/ k = zj) by lia.
           destruct Hkj as [Hklt | Hkeq].
           ++ exists k. split; [ split; [ lia | lia ] | exact Hm ].
           ++ subst k. exfalso.
              unfold matches in Hm. destruct Hm as [Hne [Hlt Heq]].
              assert (Hg : andb (negb (Z.eqb (slot_inode d blk zj) 0))
                                (andb (Z.ltb (slot_inode d blk zj) 32)
                                      (eqn (slot_name d blk zj) name)) = true).
              { apply andb_true_iff. split.
                - apply negb_true_iff. apply Z.eqb_neq. exact Hne.
                - apply andb_true_iff. split.
                  + apply Z.ltb_lt. exact Hlt.
                  + apply eqn_spec. exact Heq. }
              rewrite Hg in Hguard. discriminate.
      * exact IHrng.
Qed.

Definition dir_lookup (d : disk) (blk : Z) (name : name_t) : Z :=
  scan d blk name 16 (-1).

(* gap-11: the ABSENCE reflection.
   Given:
     - the slot-decode non-negativity antecedent (as gap-9),
     - 0 <= s < 16,
     - the remove-witness: slot s is now dead (slot_inode disk blk s = 0),
     - uniqueness: every OTHER slot k <> s that decodes to `name` is dead,
   conclude dir_lookup disk blk name < 0.

   Proof: the matches-set over [0,16) is empty, so by the `->` direction of
   scan_reflects_prefix's IFF the scan cannot be >= 0. *)
Theorem remove_reflects_absent :
  forall (d : disk) (blk : Z) (name : name_t) (s : Z),
    ( forall j : Z, 0 <= slot_inode d blk j ) ->
    0 <= s < 16 ->
    slot_inode d blk s = 0 ->
    ( forall k : Z, 0 <= k < 16 -> k <> s ->
        slot_name d blk k = name -> slot_inode d blk k = 0 ) ->
    dir_lookup d blk name < 0.
Proof.
  intros d blk name s _Hnn Hs Hwit Huniq.
  unfold dir_lookup.
  pose proof (scan_reflects_prefix d blk name 16) as [Hiff Hrng].
  replace (Z.of_nat 16) with 16 in Hiff by reflexivity.
  (* show NOT (scan >= 0) by showing the witness set is empty. *)
  destruct (Z_ge_lt_dec (scan d blk name 16 (-1)) 0) as [Hge | Hlt].
  - (* scan >= 0 leads to a contradiction. *)
    exfalso.
    apply Hiff in Hge. destruct Hge as [k [Hk Hm]].
    unfold matches in Hm. destruct Hm as [Hne [Hltk Hnm]].
    (* either k = s (then slot dead, contradicts live) or k <> s (then
       uniqueness makes it dead, contradicts live). *)
    destruct (Z.eq_dec k s) as [Hks | Hks].
    + subst k. rewrite Hwit in Hne. apply Hne. reflexivity.
    + pose proof (Huniq k Hk Hks Hnm) as Hdead. apply Hne. exact Hdead.
  - exact Hlt.
Qed.

(* The abstract directory-uniqueness predicate at block 5 (matches
   RemoveUniqueAbsent.v / UnixFs.Dir.uniq) and the slot-range invariant. *)
Definition uniq (d : disk) : Prop :=
  forall i j : Z,
    0 <= i < 16 -> 0 <= j < 16 ->
    slot_inode d 5 i <> 0 -> slot_inode d 5 i < 32 ->
    slot_inode d 5 j <> 0 -> slot_inode d 5 j < 32 ->
    slot_name d 5 i = slot_name d 5 j -> i = j.

Definition slots_lt32 (d : disk) : Prop :=
  forall k : Z, 0 <= k < 16 -> slot_inode d 5 k < 32.

(* UnixFs.Dir.dir_lookup_remove_absent (M4 rename — add+remove COEXISTENCE fix).
   The COMBINED, NARROW-trigger absence: remove_unique_absent (produces the
   empty-matches witness from uniqueness) FUSED with remove_reflects_absent
   (concludes dir_lookup < 0), as ONE applied fact keyed on the removed slot s.
   nm-free: the absent name IS the removed slot's old name slot_name d0 5 s, so
   the WhyML axiom triggers on [slot_inode d1 5 s, slot_inode d0 5 s] (the removed
   slot) — NOT on dir_lookup. In sys_rename this fires once for the oldpath slot
   and never matches the per-slot dir_lookup(slot_name k) terms the presence
   witness creates, so presence and absence stop coexisting in the E-matching. *)
Theorem dir_lookup_remove_absent :
  forall (d0 d1 : disk) (s : Z),
    ( forall j : Z, 0 <= slot_inode d1 5 j ) ->
    uniq d0 -> slots_lt32 d0 ->
    0 <= s < 16 -> slot_inode d0 5 s <> 0 -> slot_inode d1 5 s = 0 ->
    ( forall k : Z, 0 <= k < 16 -> k <> s -> slot_inode d1 5 k = slot_inode d0 5 k ) ->
    ( forall k : Z, 0 <= k < 16 -> k <> s -> slot_name  d1 5 k = slot_name  d0 5 k ) ->
    dir_lookup d1 5 (slot_name d0 5 s) < 0.
Proof.
  intros d0 d1 s Hnn Huniq Hlt32 Hs Hs0live Hs1dead Hframei Hframen.
  apply (remove_reflects_absent d1 5 (slot_name d0 5 s) s Hnn Hs Hs1dead).
  (* witness: every OTHER slot named (slot_name d0 5 s) is dead on d1 — the
     remove_unique_absent argument, inlined. *)
  intros k Hk Hks Hname.
  destruct (Z.eq_dec (slot_inode d1 5 k) 0) as [Hz | Hnz].
  - exact Hz.
  - exfalso.
    rewrite (Hframei k Hk Hks) in Hnz.
    rewrite (Hframen k Hk Hks) in Hname.
    assert (Hk32 : slot_inode d0 5 k < 32) by (apply Hlt32; lia).
    assert (Hs32 : slot_inode d0 5 s < 32) by (apply Hlt32; lia).
    assert (Heq : k = s) by (apply (Huniq k s); try lia; assumption).
    lia.
Qed.

End Scan.

End Dir.
End UnixFs.
