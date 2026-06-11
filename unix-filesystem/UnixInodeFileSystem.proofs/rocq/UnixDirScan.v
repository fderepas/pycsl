(* /tmp/dirscan/UnixDirScan.v
 *
 * Validation of UnixFs.Dir.scan_reflects_present (gap-9).
 *
 * Models the directory scan _dir_lookup as a Fixpoint over the prefix
 * length i (the slot index 0..16), with an abstract per-slot decode
 * (slot_inode / slot_name) — exactly the shape of the WhyML axiom.
 *
 * The reflection lemma: the bounded scan returns >= 0 IFF some live slot
 * k < 16 decodes to `name`. Proved by induction on the prefix length
 * with a per-slot case split (gap-9's sketch).
 *
 * Verified under Coq 8.20.1. No Admitted, no Axiom. *)

Require Import Coq.ZArith.ZArith.
Require Import Coq.Bool.Bool.
Require Import Lia.

Open Scope Z_scope.

Module UnixFs.
Module Dir.

(* Abstract per-slot decode: the model leaves slot_inode / slot_name
   uninterpreted (they are the proven name-codec round-trip in the os
   model). The reflection property holds for ANY such decode. *)
Section Scan.

Variable disk : Type.            (* the disk byte-array, abstract here *)
Variable name_t : Type.          (* decoded names, abstract here *)
Variable slot_inode : disk -> Z -> Z -> Z.    (* disk -> blk -> k -> inode *)
Variable slot_name  : disk -> Z -> Z -> name_t. (* disk -> blk -> k -> name *)
Variable eqn : name_t -> name_t -> bool.        (* decidable name equality *)
Hypothesis eqn_spec : forall a b, eqn a b = true <-> a = b.

(* Faithful model fact: a decoded inode number is non-negative — it is read
   from unsigned disk bytes (_unpack_direntry over uint fields). This is the
   ONLY semantic assumption beyond the scan structure; it mirrors the os
   model's unsigned-byte inode field. *)
Hypothesis slot_inode_nonneg : forall d blk k, 0 <= slot_inode d blk k.

(* A slot k is a live match for `name` in block `blk`. *)
Definition matches (d : disk) (blk : Z) (name : name_t) (k : Z) : Prop :=
  slot_inode d blk k <> 0 /\ slot_inode d blk k < 32 /\ slot_name d blk k = name.

(* The running scan over the first i slots, mirroring _dir_lookup's loop
   body `if name==pathname and inode!=0 and inode<32: found = inode`.
   It keeps the LAST match (recurse first, then test slot j) — exactly
   _dir_lookup's behaviour; the IFF is insensitive to which match. *)
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

(* The found-reflects-prefix invariant, proved at every prefix length i:
   (scan ... >= 0) IFF some slot k < i is a live match, AND the scan
   result, when non-negative, is < 32 (the inode-range invariant the
   loop also carries). *)
Lemma scan_reflects_prefix : forall (d : disk) (blk : Z) (name : name_t) (i : nat),
  ( (scan d blk name i (-1) >= 0)
    <-> (exists k : Z, 0 <= k < Z.of_nat i /\ matches d blk name k) )
  /\ ( scan d blk name i (-1) >= 0 -> scan d blk name i (-1) < 32 ).
Proof.
  intros d blk name i. induction i as [| j IH].
  - (* base: empty prefix; scan = -1, no witness. *)
    simpl. split.
    + split.
      * intro H. lia.
      * intros [k [Hk _]]. lia.
    + intro H. lia.
  - (* step: peel slot j. *)
    destruct IH as [IHiff IHrng].
    simpl.
    set (zj := Z.of_nat j) in *.
    remember (andb (negb (Z.eqb (slot_inode d blk zj) 0))
                   (andb (Z.ltb (slot_inode d blk zj) 32)
                         (eqn (slot_name d blk zj) name))) as guard eqn:Hguard.
    destruct guard.
    + (* guard true: slot j is a live match; result = slot_inode j. *)
      (* decode the guard. *)
      symmetry in Hguard.
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
    + (* guard false: slot j is NOT a live match; result = scan over j. *)
      symmetry in Hguard.
      (* the prefix-(j+1) witness set = prefix-j witness set (slot j excluded). *)
      split.
      * rewrite IHiff. split.
        -- intros [k [Hk Hm]]. exists k. split; [ split; [ lia | lia ] | exact Hm ].
        -- intros [k [Hk Hm]].
           (* k < j+1, and k <> j because slot j is no match. *)
           assert (Hkj : k < zj \/ k = zj) by lia.
           destruct Hkj as [Hklt | Hkeq].
           ++ exists k. split; [ split; [ lia | lia ] | exact Hm ].
           ++ (* k = zj contradicts guard=false. *)
              subst k. exfalso.
              unfold matches in Hm. destruct Hm as [Hne [Hlt Heq]].
              (* reconstruct guard=true, contradiction. *)
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

(* The registered axiom: directory width is 16. dir_lookup disk blk name
   := scan disk blk name 16 (-1). *)
Definition dir_lookup (d : disk) (blk : Z) (name : name_t) : Z :=
  scan d blk name 16 (-1).

Theorem scan_reflects_present : forall (d : disk) (blk : Z) (name : name_t),
  (dir_lookup d blk name >= 0)
  <-> (exists k : Z, 0 <= k < 16 /\ matches d blk name k).
Proof.
  intros d blk name. unfold dir_lookup.
  pose proof (scan_reflects_prefix d blk name 16) as [Hiff _].
  (* Z.of_nat 16 = 16 *)
  replace (Z.of_nat 16) with 16 in Hiff by reflexivity.
  exact Hiff.
Qed.

End Scan.

(* The unsigned-byte fact, named UnixFs.Dir.slot_inode_nonneg (registry's
   `slot_inode_nonneg` axiom): a decoded directory-slot inode is non-negative.
   This is the `slot_inode_nonneg` HYPOTHESIS of scan_reflects_present, surfaced
   here as a proven theorem about the CONCRETE decode `slot_inode_concrete`,
   which reads a 32-bit unsigned field from the on-disk bytes — `>= 0` by the
   non-negativity of unsigned byte values and the radix sum (each `byte k` is a
   `Z.of_nat`, hence non-negative; the weighted sum of non-negatives is
   non-negative). The WhyML axiom `forall disk blk k. slot_inode disk blk k >= 0`
   reflects exactly this. *)
Section Nonneg.

Variable byte : Z -> Z -> Z -> Z.   (* disk -> blk -> position -> byte value *)
Hypothesis byte_unsigned : forall d blk p, 0 <= byte d blk p <= 255.

(* the big-endian uint32 decode of the 4 inode bytes of slot k (offset blk*512
   + k*32, inode in the first 4 bytes), mirroring _unpack_uint32_be. *)
Definition slot_inode_concrete (d blk k : Z) : Z :=
  byte d blk (blk*512 + k*32 + 0) * 16777216
  + byte d blk (blk*512 + k*32 + 1) * 65536
  + byte d blk (blk*512 + k*32 + 2) * 256
  + byte d blk (blk*512 + k*32 + 3).

Theorem slot_inode_nonneg : forall d blk k, 0 <= slot_inode_concrete d blk k.
Proof.
  intros d blk k. unfold slot_inode_concrete.
  pose proof (byte_unsigned d blk (blk*512 + k*32 + 0)).
  pose proof (byte_unsigned d blk (blk*512 + k*32 + 1)).
  pose proof (byte_unsigned d blk (blk*512 + k*32 + 2)).
  pose proof (byte_unsigned d blk (blk*512 + k*32 + 3)).
  lia.
Qed.

End Nonneg.

End Dir.
End UnixFs.
