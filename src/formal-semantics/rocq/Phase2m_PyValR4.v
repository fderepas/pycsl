(* Phase2m_PyValR4.v — axiom-free certificate for the FROZEN r4 mixed-value type `hval`
   and its observable operations (wall dict-value-model-r4, Gate P step C, executor ce4).
   SUCCESSOR of Phase2f_PyVal.v (which is left untouched and still builds): Phase2f
   certifies the 5-constructor R3 carrier with a PREPEND `pairs_set`; this file certifies
   the 9-constructor carrier frozen in getting-better/dict-value-model-r4-impl.md §2.1 and
   the operations of §2.3, against the WhyML companion getting-better/dict-r4-theory.mlw
   (module DictR4Theory).  Every definition below carries the SAME name, argument order,
   match structure and recursion / fold direction as its WhyML twin; WhyML's program `=`
   on bool / int / real / string is `Bool.eqb` / `Z.eqb` / `F_eqb` / `String.eqb`.

   THE REAL CARRIER.  Rocq's stdlib `R` is axiomatised (ClassicalDedekindReals etc.), so a
   theorem that decides equality on `R` would leak non-allowlisted axioms.  `HFloat` is
   therefore over an ABSTRACT carrier `F` (section variables), with exactly the laws the
   WhyML theory relies on, all TRUE of Why3's `real` (classical equality; `from_int`
   injective = stdlib `real.FromInt.Injective`; `hreal_int_of` = its `val` spec):
     F_eqb_spec        : F_eqb a b = true <-> a = b            (program `=` on real)
     from_int_inj      : from_int i = from_int j -> i = j       (FromInt.Injective)
     hreal_int_of_some : hreal_int_of f = Some i -> from_int i = f   (the val's ensures)
     hreal_int_of_none : hreal_int_of f = None -> forall i, from_int i <> f
   `0.0` is `from_int 0` (Why3 FromInt.Zero), `1.0` is `from_int 1` (FromInt.One).
   After `End PyValR4.` every theorem is universally quantified over the carrier and its
   laws, hence holds for EVERY model, in particular Why3's reals; section 9 exhibits a
   concrete axiom-free model (integers + non-integral points) so the laws are satisfiable.
   The four law-free wrong-tag vals (`hval_opaque_str`, `hval_opaque_int`,
   `hval_len_other`, `hval_tuple_other`) are section variables too: every law holds for
   every interpretation of them.

   ROUTE (e2) (user decision log 848): the emitted theory declares `pairs_get` uninterpreted
   with its two defining equations as WhyML axioms; they are realised here by the lemmas
   `pairs_get_nil` and `pairs_get_cons` of the certified recursive `pairs_get`.

   Verdict: the `Print Assumptions` block at the bottom must print `Closed under the global
   context` for every result (NO axiom; the 3-axiom ledger of proof_axiom_allowlist.py /
   Phase5b / Phase6i is untouched).  Nothing here is Admitted.
   Build: part of `make` (listed in `_CoqProject` after `Phase2l_PyAstExpr.v`). *)

Require Import ZArith String List Bool Lia.
Import ListNotations.

Section PyValR4.

Local Open Scope string_scope.
Local Open Scope Z_scope.

(* ===================================================================== *)
(* 0. The abstract real carrier and its laws.                             *)
(* ===================================================================== *)

Variable F : Type.
Variable F_eqb : F -> F -> bool.
Hypothesis F_eqb_spec : forall a b : F, F_eqb a b = true <-> a = b.
Variable from_int : Z -> F.
Hypothesis from_int_inj : forall i j : Z, from_int i = from_int j -> i = j.
Variable hreal_int_of : F -> option Z.
Hypothesis hreal_int_of_some : forall f i, hreal_int_of f = Some i -> from_int i = f.
Hypothesis hreal_int_of_none : forall f, hreal_int_of f = None -> forall i, from_int i <> f.

(* ===================================================================== *)
(* 1. The frozen 9-constructor mutual inductive.                          *)
(* ===================================================================== *)

Inductive hval : Type :=
  | HNone
  | HBool  (b : bool)
  | HInt   (n : Z)
  | HFloat (f : F)
  | HStr   (s : string)
  | HTuple (l : hval_list)
  | HArr   (l : hval_list)
  | HMap   (p : hpairs)
  | HNode  (v : hval)
with hval_list : Type :=
  | HNil
  | HCons (h : hval) (t : hval_list)
with hpairs : Type :=
  | PNil
  | PCons (k : string) (v : hval) (t : hpairs).

Scheme hval_mut := Induction for hval Sort Prop
with hval_list_mut := Induction for hval_list Sort Prop
with hpairs_mut := Induction for hpairs Sort Prop.

(* the law-free wrong-tag arms (uninterpreted in WhyML) *)
Variable hval_opaque_str : hval -> string.
Variable hval_opaque_int : hval -> Z.
Variable hval_len_other : hval -> Z.
Variable hval_tuple_other : hval -> hval.

(* WhyML `hpairs_key_eq` (val function, `result <-> a = b`) is realised by String.eqb. *)
Local Notation hpairs_key_eq := String.eqb.

Lemma key_refl : forall s, String.eqb s s = true.
Proof. intros s; apply String.eqb_eq; reflexivity. Qed.

Theorem hpairs_key_eq_spec : forall a b, hpairs_key_eq a b = true <-> a = b.
Proof. intros a b; apply String.eqb_eq. Qed.

Theorem hreal_int_of_from_int : forall i, hreal_int_of (from_int i) = Some i.
Proof.
  intros i; destruct (hreal_int_of (from_int i)) as [j|] eqn:E.
  - apply hreal_int_of_some in E; apply from_int_inj in E; subst; reflexivity.
  - exfalso; exact (hreal_int_of_none _ E i eq_refl).
Qed.

(* ===================================================================== *)
(* 2. size / size_pos (well-foundedness), injectivity, disequalities.     *)
(* ===================================================================== *)

Fixpoint size (v : hval) : Z :=
  match v with
  | HTuple l => 1 + list_size l
  | HArr l   => 1 + list_size l
  | HMap p   => 1 + pairs_size p
  | HNode n  => 1 + size n
  | _        => 1
  end
with list_size (l : hval_list) : Z :=
  match l with
  | HNil      => 0
  | HCons h t => size h + list_size t
  end
with pairs_size (p : hpairs) : Z :=
  match p with
  | PNil        => 0
  | PCons _ v t => size v + pairs_size t
  end.

Theorem size_pos : forall v : hval, size v >= 1.
Proof.
  apply (hval_mut (fun v => size v >= 1) (fun l => list_size l >= 0)
                  (fun p => pairs_size p >= 0));
    intros; cbn [size list_size pairs_size] in *; lia.
Qed.
Theorem list_size_nonneg : forall l : hval_list, list_size l >= 0.
Proof.
  apply (hval_list_mut (fun v => size v >= 1) (fun l => list_size l >= 0)
                       (fun p => pairs_size p >= 0));
    intros; cbn [size list_size pairs_size] in *; lia.
Qed.
Theorem pairs_size_nonneg : forall p : hpairs, pairs_size p >= 0.
Proof.
  apply (hpairs_mut (fun v => size v >= 1) (fun l => list_size l >= 0)
                    (fun p => pairs_size p >= 0));
    intros; cbn [size list_size pairs_size] in *; lia.
Qed.
Theorem list_tail_size_lt : forall h t, list_size t < list_size (HCons h t).
Proof. intros h t; cbn [list_size]; pose proof (size_pos h); lia. Qed.
Theorem pairs_tail_size_lt : forall k v t, pairs_size t < pairs_size (PCons k v t).
Proof. intros k v t; cbn [pairs_size]; pose proof (size_pos v); lia. Qed.
Theorem size_sub_tuple : forall l, list_size l < size (HTuple l).
Proof. intros; cbn [size]; lia. Qed.
Theorem size_sub_arr : forall l, list_size l < size (HArr l).
Proof. intros; cbn [size]; lia. Qed.
Theorem size_sub_map : forall p, pairs_size p < size (HMap p).
Proof. intros; cbn [size]; lia. Qed.
Theorem size_sub_node : forall v, size v < size (HNode v).
Proof. intros; cbn [size]; lia. Qed.

Theorem hbool_inj  : forall a b, HBool a = HBool b -> a = b.
Proof. intros a b H; injection H; auto. Qed.
Theorem hint_inj   : forall a b, HInt a = HInt b -> a = b.
Proof. intros a b H; injection H; auto. Qed.
Theorem hfloat_inj : forall a b, HFloat a = HFloat b -> a = b.
Proof. intros a b H; injection H; auto. Qed.
Theorem hstr_inj   : forall a b, HStr a = HStr b -> a = b.
Proof. intros a b H; injection H; auto. Qed.
Theorem htuple_inj : forall a b, HTuple a = HTuple b -> a = b.
Proof. intros a b H; injection H; auto. Qed.
Theorem harr_inj   : forall a b, HArr a = HArr b -> a = b.
Proof. intros a b H; injection H; auto. Qed.
Theorem hmap_inj   : forall a b, HMap a = HMap b -> a = b.
Proof. intros a b H; injection H; auto. Qed.
Theorem hnode_inj  : forall a b, HNode a = HNode b -> a = b.
Proof. intros a b H; injection H; auto. Qed.
Theorem hcons_inj : forall h t h' t', HCons h t = HCons h' t' -> h = h' /\ t = t'.
Proof. intros h t h' t' H; injection H; auto. Qed.
Theorem pcons_inj : forall k v t k' v' t',
  PCons k v t = PCons k' v' t' -> k = k' /\ v = v' /\ t = t'.
Proof. intros k v t k' v' t' H; injection H; auto. Qed.
Theorem hnil_neq_hcons : forall h t, HNil <> HCons h t.
Proof. intros h t; discriminate. Qed.
Theorem pnil_neq_pcons : forall k v t, PNil <> PCons k v t.
Proof. intros k v t; discriminate. Qed.

(* the 36 pairwise constructor disequalities *)
Theorem neq_none_bool : forall b2, HNone <> (HBool b2).
Proof. intros b2; discriminate. Qed.
Theorem neq_none_int : forall n2, HNone <> (HInt n2).
Proof. intros n2; discriminate. Qed.
Theorem neq_none_float : forall f2, HNone <> (HFloat f2).
Proof. intros f2; discriminate. Qed.
Theorem neq_none_str : forall s2, HNone <> (HStr s2).
Proof. intros s2; discriminate. Qed.
Theorem neq_none_tuple : forall l2, HNone <> (HTuple l2).
Proof. intros l2; discriminate. Qed.
Theorem neq_none_arr : forall l2, HNone <> (HArr l2).
Proof. intros l2; discriminate. Qed.
Theorem neq_none_map : forall p2, HNone <> (HMap p2).
Proof. intros p2; discriminate. Qed.
Theorem neq_none_node : forall v2, HNone <> (HNode v2).
Proof. intros v2; discriminate. Qed.
Theorem neq_bool_int : forall b1 n2, (HBool b1) <> (HInt n2).
Proof. intros b1 n2; discriminate. Qed.
Theorem neq_bool_float : forall b1 f2, (HBool b1) <> (HFloat f2).
Proof. intros b1 f2; discriminate. Qed.
Theorem neq_bool_str : forall b1 s2, (HBool b1) <> (HStr s2).
Proof. intros b1 s2; discriminate. Qed.
Theorem neq_bool_tuple : forall b1 l2, (HBool b1) <> (HTuple l2).
Proof. intros b1 l2; discriminate. Qed.
Theorem neq_bool_arr : forall b1 l2, (HBool b1) <> (HArr l2).
Proof. intros b1 l2; discriminate. Qed.
Theorem neq_bool_map : forall b1 p2, (HBool b1) <> (HMap p2).
Proof. intros b1 p2; discriminate. Qed.
Theorem neq_bool_node : forall b1 v2, (HBool b1) <> (HNode v2).
Proof. intros b1 v2; discriminate. Qed.
Theorem neq_int_float : forall n1 f2, (HInt n1) <> (HFloat f2).
Proof. intros n1 f2; discriminate. Qed.
Theorem neq_int_str : forall n1 s2, (HInt n1) <> (HStr s2).
Proof. intros n1 s2; discriminate. Qed.
Theorem neq_int_tuple : forall n1 l2, (HInt n1) <> (HTuple l2).
Proof. intros n1 l2; discriminate. Qed.
Theorem neq_int_arr : forall n1 l2, (HInt n1) <> (HArr l2).
Proof. intros n1 l2; discriminate. Qed.
Theorem neq_int_map : forall n1 p2, (HInt n1) <> (HMap p2).
Proof. intros n1 p2; discriminate. Qed.
Theorem neq_int_node : forall n1 v2, (HInt n1) <> (HNode v2).
Proof. intros n1 v2; discriminate. Qed.
Theorem neq_float_str : forall f1 s2, (HFloat f1) <> (HStr s2).
Proof. intros f1 s2; discriminate. Qed.
Theorem neq_float_tuple : forall f1 l2, (HFloat f1) <> (HTuple l2).
Proof. intros f1 l2; discriminate. Qed.
Theorem neq_float_arr : forall f1 l2, (HFloat f1) <> (HArr l2).
Proof. intros f1 l2; discriminate. Qed.
Theorem neq_float_map : forall f1 p2, (HFloat f1) <> (HMap p2).
Proof. intros f1 p2; discriminate. Qed.
Theorem neq_float_node : forall f1 v2, (HFloat f1) <> (HNode v2).
Proof. intros f1 v2; discriminate. Qed.
Theorem neq_str_tuple : forall s1 l2, (HStr s1) <> (HTuple l2).
Proof. intros s1 l2; discriminate. Qed.
Theorem neq_str_arr : forall s1 l2, (HStr s1) <> (HArr l2).
Proof. intros s1 l2; discriminate. Qed.
Theorem neq_str_map : forall s1 p2, (HStr s1) <> (HMap p2).
Proof. intros s1 p2; discriminate. Qed.
Theorem neq_str_node : forall s1 v2, (HStr s1) <> (HNode v2).
Proof. intros s1 v2; discriminate. Qed.
Theorem neq_tuple_arr : forall l1 l2, (HTuple l1) <> (HArr l2).
Proof. intros l1 l2; discriminate. Qed.
Theorem neq_tuple_map : forall l1 p2, (HTuple l1) <> (HMap p2).
Proof. intros l1 p2; discriminate. Qed.
Theorem neq_tuple_node : forall l1 v2, (HTuple l1) <> (HNode v2).
Proof. intros l1 v2; discriminate. Qed.
Theorem neq_arr_map : forall l1 p2, (HArr l1) <> (HMap p2).
Proof. intros l1 p2; discriminate. Qed.
Theorem neq_arr_node : forall l1 v2, (HArr l1) <> (HNode v2).
Proof. intros l1 v2; discriminate. Qed.
Theorem neq_map_node : forall p1 v2, (HMap p1) <> (HNode v2).
Proof. intros p1 v2; discriminate. Qed.

(* ===================================================================== *)
(* 3. The dict carrier: pairs_get (+ the route-(e2) equations), the       *)
(*    emitted replace-first/append pairs_set, membership, length, nodup.  *)
(* ===================================================================== *)

Fixpoint pairs_get (p : hpairs) (k : string) : option hval :=
  match p with
  | PNil => None
  | PCons k' v t => if hpairs_key_eq k k' then Some v else pairs_get t k
  end.

(* route (e2): the two WhyML axioms `pairs_get_nil` / `pairs_get_cons`, LITERALLY
   (`if k = k' then ..` is WhyML's decidable logic test, here `string_dec k k'`). *)
Theorem pairs_get_nil : forall k, pairs_get PNil k = None.
Proof. reflexivity. Qed.
Theorem pairs_get_cons : forall k k' v t,
  pairs_get (PCons k' v t) k = (if string_dec k k' then Some v else pairs_get t k).
Proof.
  intros k k' v t; cbn [pairs_get].
  destruct (String.eqb_spec k k') as [E|N]; destruct (string_dec k k') as [E'|N'];
    try reflexivity; contradiction.
Qed.

(* verbatim the emitted pairs_set (preamble.py:8281-8287 at ca505a20c) *)
Fixpoint pairs_set (p : hpairs) (k : string) (v : hval) : hpairs :=
  match p with
  | PNil => PCons k v PNil
  | PCons k' w t => if hpairs_key_eq k k' then PCons k' v t else PCons k' w (pairs_set t k v)
  end.

Definition pairs_mem (p : hpairs) (k : string) : bool :=
  match pairs_get p k with None => false | Some _ => true end.
Arguments pairs_mem : simpl never.

Fixpoint hpairs_len (p : hpairs) : Z :=
  match p with PNil => 0 | PCons _ _ t => 1 + hpairs_len t end.

Fixpoint pairs_nodup (p : hpairs) : bool :=
  match p with PNil => true | PCons k _ t => negb (pairs_mem t k) && pairs_nodup t end.

Fixpoint pairs_keys_in (q p : hpairs) : bool :=
  match q with PNil => true | PCons k _ t => pairs_mem p k && pairs_keys_in t p end.

Fixpoint hpairs_keys (p : hpairs) : hval_list :=
  match p with PNil => HNil | PCons k _ t => HCons (HStr k) (hpairs_keys t) end.

Theorem pairs_set_get : forall p k v j,
  pairs_get (pairs_set p k v) j = if hpairs_key_eq j k then Some v else pairs_get p j.
Proof.
  induction p as [|k' w t IH]; intros k v j; cbn [pairs_set pairs_get].
  - reflexivity.
  - destruct (String.eqb_spec k k') as [E|N]; cbn [pairs_get].
    + subst k'. destruct (String.eqb j k); reflexivity.
    + destruct (String.eqb_spec j k') as [E2|N2].
      * subst j. destruct (String.eqb_spec k' k) as [E3|_]; [congruence|reflexivity].
      * rewrite IH. reflexivity.
Qed.

Theorem read_same_key : forall p k v, pairs_get (pairs_set p k v) k = Some v.
Proof. intros p k v; rewrite pairs_set_get, key_refl; reflexivity. Qed.

Theorem read_other_key : forall p k k' v,
  k' <> k -> pairs_get (pairs_set p k v) k' = pairs_get p k'.
Proof.
  intros p k k' v H; rewrite pairs_set_get.
  destruct (String.eqb_spec k' k); [contradiction|reflexivity].
Qed.

Theorem mem_set : forall p k v j,
  pairs_mem (pairs_set p k v) j = (hpairs_key_eq j k || pairs_mem p j).
Proof.
  intros p k v j; unfold pairs_mem; rewrite pairs_set_get.
  destruct (String.eqb j k); reflexivity.
Qed.

Theorem nodup_preserved : forall p k v,
  pairs_nodup p = true -> pairs_nodup (pairs_set p k v) = true.
Proof.
  intros p k v; induction p as [|k' w t IH]; intros H.
  - reflexivity.
  - cbn [pairs_nodup] in H. apply andb_true_iff in H as [H1 H2].
    cbn [pairs_set]. destruct (String.eqb_spec k k') as [E|N].
    + cbn [pairs_nodup]. rewrite H1, H2. reflexivity.
    + cbn [pairs_nodup]. rewrite mem_set.
      destruct (String.eqb_spec k' k) as [E'|_]; [congruence|].
      cbn [orb]. rewrite H1, (IH H2). reflexivity.
Qed.

Theorem len_set : forall p k v,
  hpairs_len (pairs_set p k v)
  = if pairs_mem p k then hpairs_len p else hpairs_len p + 1.
Proof.
  intros p k v; induction p as [|k' w t IH].
  - reflexivity.
  - unfold pairs_mem; cbn [pairs_set pairs_get hpairs_len].
    destruct (String.eqb_spec k k') as [E|N]; cbn [hpairs_len].
    + reflexivity.
    + rewrite IH. unfold pairs_mem. destruct (pairs_get t k); cbv beta iota; lia.
Qed.

Theorem hpairs_len_nonneg : forall p, hpairs_len p >= 0.
Proof. induction p; cbn [hpairs_len]; lia. Qed.

(* ---- the literal construction: a LEFT fold of pairs_set ---- *)
Fixpoint pairs_build (acc : hpairs) (l : list (string * hval)) : hpairs :=
  match l with
  | [] => acc
  | (k, v) :: t => pairs_build (pairs_set acc k v) t
  end.

Fixpoint kv_last (l : list (string * hval)) (k : string) : option hval :=
  match l with
  | [] => None
  | (k', v) :: t =>
      match kv_last t k with
      | Some w => Some w
      | None => if hpairs_key_eq k k' then Some v else None
      end
  end.

Theorem build_is_fold_left : forall l acc,
  pairs_build acc l = fold_left (fun p kv => pairs_set p (fst kv) (snd kv)) l acc.
Proof.
  induction l as [|[k v] t IH]; intros acc; cbn [pairs_build fold_left fst snd];
    [reflexivity | apply IH].
Qed.

Theorem build_fold_read_back : forall l acc k,
  pairs_get (pairs_build acc l) k
  = match kv_last l k with Some w => Some w | None => pairs_get acc k end.
Proof.
  induction l as [|[k' v] t IH]; intros acc k; cbn [pairs_build kv_last].
  - reflexivity.
  - rewrite IH. destruct (kv_last t k); [reflexivity|].
    rewrite pairs_set_get. destruct (String.eqb k k'); reflexivity.
Qed.

Theorem build_nodup : forall l acc,
  pairs_nodup acc = true -> pairs_nodup (pairs_build acc l) = true.
Proof.
  induction l as [|[k v] t IH]; intros acc H; cbn [pairs_build];
    [exact H | apply IH, nodup_preserved, H].
Qed.

(* last-wins: {"a": a, "a": b}["a"] == b, and the dict has ONE key *)
Theorem build_last_wins : forall a b,
  pairs_get (pairs_build PNil [("a", a); ("a", b)]) "a" = Some b.
Proof. intros; reflexivity. Qed.
Theorem build_len_dup : forall a b,
  hpairs_len (pairs_build PNil [("a", a); ("a", b)]) = 1.
Proof. intros; reflexivity. Qed.
(* insertion order: {"a": a, "b": b} is the list a-then-b (iteration order) *)
Theorem build_insertion_order : forall a b,
  pairs_build PNil [("a", a); ("b", b)] = PCons "a" a (PCons "b" b PNil).
Proof. intros; reflexivity. Qed.

(* ---- membership predicate and the lookup/nodup bridge ---- *)
Fixpoint InP (k : string) (v : hval) (p : hpairs) : Prop :=
  match p with
  | PNil => False
  | PCons k' v' t => (k = k' /\ v = v') \/ InP k v t
  end.

Lemma get_InP : forall p k v, pairs_get p k = Some v -> InP k v p.
Proof.
  induction p as [|k' v' t IH]; cbn [pairs_get InP]; intros k v H; [discriminate|].
  revert H; destruct (String.eqb_spec k k') as [E|N]; intro H.
  - left; split; [exact E | congruence].
  - right; apply IH; exact H.
Qed.

Lemma InP_mem : forall p k v, InP k v p -> pairs_mem p k = true.
Proof.
  induction p as [|k' v' t IH]; intros k v H; cbn [InP] in H; [contradiction|].
  unfold pairs_mem; cbn [pairs_get].
  destruct (String.eqb_spec k k') as [E|N]; [reflexivity|].
  destruct H as [[E _]|H]; [contradiction|].
  specialize (IH k v H); unfold pairs_mem in IH; exact IH.
Qed.

Lemma mem_get : forall p k, pairs_mem p k = true -> exists v, pairs_get p k = Some v.
Proof.
  intros p k; unfold pairs_mem; destruct (pairs_get p k) as [v|]; intros H;
    [exists v; reflexivity | discriminate].
Qed.

Lemma InP_get_nodup : forall p k v,
  pairs_nodup p = true -> InP k v p -> pairs_get p k = Some v.
Proof.
  induction p as [|k' v' t IH]; intros k v Hn Hi; cbn [InP] in Hi; [contradiction|].
  cbn [pairs_nodup] in Hn; apply andb_true_iff in Hn as [Hm Ht].
  cbn [pairs_get]. destruct Hi as [[E1 E2]|Hi].
  - subst k v. rewrite key_refl. reflexivity.
  - destruct (String.eqb_spec k k') as [E|N].
    + subst k. rewrite (InP_mem t k' v Hi) in Hm. cbn in Hm. discriminate.
    + apply IH; assumption.
Qed.


(* ===================================================================== *)
(* 4. Python equality: the cross-type numeric tower, structural sequences, *)
(*    order-independent dict equality.                                    *)
(* ===================================================================== *)

Definition hbool_int (b : bool) : Z := if b then 1 else 0.
Arguments hbool_int : simpl never.

Fixpoint hval_eq (a b : hval) {struct a} : bool :=
  match a with
  | HNone => match b with HNone => true | _ => false end
  | HBool x => match b with
               | HBool y => if x then y else negb y
               | HInt j => Z.eqb (hbool_int x) j
               | HFloat g => match hreal_int_of g with Some j => Z.eqb (hbool_int x) j | None => false end
               | _ => false
               end
  | HInt i => match b with
              | HBool y => Z.eqb i (hbool_int y)
              | HInt j => Z.eqb i j
              | HFloat g => match hreal_int_of g with Some j => Z.eqb i j | None => false end
              | _ => false
              end
  | HFloat f => match b with
                | HBool y => match hreal_int_of f with Some i => Z.eqb i (hbool_int y) | None => false end
                | HInt j => match hreal_int_of f with Some i => Z.eqb i j | None => false end
                | HFloat g => F_eqb f g
                | _ => false
                end
  | HStr s => match b with HStr t => hpairs_key_eq s t | _ => false end
  | HTuple l => match b with HTuple m => hlist_eq l m | _ => false end
  | HArr l => match b with HArr m => hlist_eq l m | _ => false end
  | HMap p => match b with HMap q => pairs_incl p q && pairs_keys_in q p | _ => false end
  | HNode x => match b with HNode y => hval_eq x y | _ => false end
  end
with hlist_eq (l m : hval_list) {struct l} : bool :=
  match l with
  | HNil => match m with HNil => true | _ => false end
  | HCons x t => match m with HCons y u => hval_eq x y && hlist_eq t u | _ => false end
  end
with pairs_incl (p q : hpairs) {struct p} : bool :=
  match p with
  | PNil => true
  | PCons k v t => (match pairs_get q k with Some w => hval_eq v w | None => false end)
                   && pairs_incl t q
  end.

(* deep well-formedness: every nested dict carrier is duplicate-free (true of every
   Python dict, and preserved by pairs_set / the literal fold: nodup_preserved,
   build_nodup) *)
Fixpoint hval_wf (v : hval) : bool :=
  match v with
  | HTuple l => hlist_wf l
  | HArr l => hlist_wf l
  | HMap p => pairs_nodup p && hpairs_wf p
  | HNode x => hval_wf x
  | _ => true
  end
with hlist_wf (l : hval_list) : bool :=
  match l with HNil => true | HCons x t => hval_wf x && hlist_wf t end
with hpairs_wf (p : hpairs) : bool :=
  match p with PNil => true | PCons _ x t => hval_wf x && hpairs_wf t end.

Lemma wf_InP : forall p k v, hpairs_wf p = true -> InP k v p -> hval_wf v = true.
Proof.
  induction p as [|k' v' t IH]; intros k v H Hi; simpl in Hi; [contradiction|].
  simpl in H; apply andb_true_iff in H as [H1 H2].
  destruct Hi as [[_ E]|Hi]; [subst v; exact H1 | exact (IH k v H2 Hi)].
Qed.

Lemma incl_spec : forall p q,
  pairs_incl p q = true <->
  (forall k v, InP k v p -> exists w, pairs_get q k = Some w /\ hval_eq v w = true).
Proof.
  induction p as [|k v t IH]; intros q; simpl.
  - split; [intros _ k v [] | intros _; reflexivity].
  - rewrite andb_true_iff, IH. split.
    + intros [H1 H2] k' v' [[E1 E2]|Hi].
      * subst k' v'. destruct (pairs_get q k) as [w|];
          [exists w; split; [reflexivity | exact H1] | discriminate H1].
      * apply H2; exact Hi.
    + intros H. split.
      * destruct (H k v (or_introl (conj eq_refl eq_refl))) as [w [E1 E2]].
        rewrite E1; exact E2.
      * intros k' v' Hi; apply H; right; exact Hi.
Qed.

Lemma keys_in_spec : forall q p,
  pairs_keys_in q p = true <-> (forall k v, InP k v q -> pairs_mem p k = true).
Proof.
  induction q as [|k v t IH]; intros p; simpl.
  - split; [intros _ k v [] | intros _; reflexivity].
  - rewrite andb_true_iff, IH. split.
    + intros [H1 H2] k' v' [[E1 _]|Hi]; [subst k'; exact H1 | exact (H2 k' v' Hi)].
    + intros H; split.
      * exact (H k v (or_introl (conj eq_refl eq_refl))).
      * intros k' v' Hi; exact (H k' v' (or_intror Hi)).
Qed.

(* ---- reflexivity (on well-formed values; HFloat carries no NaN) ---- *)
Definition refl_P (a : hval) := hval_wf a = true -> hval_eq a a = true.
Definition refl_Q (l : hval_list) := hlist_wf l = true -> hlist_eq l l = true.
Definition refl_R (p : hpairs) := forall k v, InP k v p -> refl_P v.

Theorem hval_eq_refl : forall a, hval_wf a = true -> hval_eq a a = true.
Proof.
  apply (hval_mut refl_P refl_Q refl_R); unfold refl_P, refl_Q, refl_R; simpl.
  - intros _; reflexivity.
  - intros b _; destruct b; reflexivity.
  - intros n _; apply Z.eqb_refl.
  - intros f _; apply F_eqb_spec; reflexivity.
  - intros s _; apply key_refl.
  - intros l IH H; exact (IH H).
  - intros l IH H; exact (IH H).
  - intros p IH H. apply andb_true_iff in H as [Hn Hw]. apply andb_true_iff; split.
    + apply incl_spec. intros k v Hi. exists v. split.
      * apply InP_get_nodup; assumption.
      * exact (IH k v Hi (wf_InP p k v Hw Hi)).
    + apply keys_in_spec. intros k v Hi. exact (InP_mem p k v Hi).
  - intros v IH H; exact (IH H).
  - intros _; reflexivity.
  - intros h IHh t IHt H. apply andb_true_iff in H as [H1 H2].
    rewrite (IHh H1), (IHt H2). reflexivity.
  - intros k v [].
  - intros k v IHv t IHt k' v' [[_ E]|Hi]; [subst v'; exact IHv | exact (IHt k' v' Hi)].
Qed.

(* ---- symmetry (on well-formed values) ---- *)
Definition sym_P (a : hval) := forall b, hval_wf a = true -> hval_wf b = true ->
  hval_eq a b = true -> hval_eq b a = true.
Definition sym_Q (l : hval_list) := forall m, hlist_wf l = true -> hlist_wf m = true ->
  hlist_eq l m = true -> hlist_eq m l = true.
Definition sym_R (p : hpairs) := forall k v, InP k v p -> sym_P v.

Theorem hval_eq_sym_true : forall a b, hval_wf a = true -> hval_wf b = true ->
  hval_eq a b = true -> hval_eq b a = true.
Proof.
  apply (hval_mut sym_P sym_Q sym_R); unfold sym_P, sym_Q, sym_R; simpl.
  - intros b _ _ H; destruct b; simpl in *; try discriminate H; reflexivity.
  - intros x b _ _ H; destruct b as [|y|j|g|s|l|l|p|v]; simpl in *; try discriminate H.
    + revert H; destruct x, y; simpl; auto.
    + rewrite Z.eqb_sym; exact H.
    + revert H; destruct (hreal_int_of g); intro H; [rewrite Z.eqb_sym; exact H | discriminate H].
  - intros i b _ _ H; destruct b as [|y|j|g|s|l|l|p|v]; simpl in *; try discriminate H.
    + rewrite Z.eqb_sym; exact H.
    + rewrite Z.eqb_sym; exact H.
    + revert H; destruct (hreal_int_of g); intro H; [rewrite Z.eqb_sym; exact H | discriminate H].
  - intros f b _ _ H; destruct b as [|y|j|g|s|l|l|p|v]; simpl in *; try discriminate H.
    + revert H; destruct (hreal_int_of f); intro H; [rewrite Z.eqb_sym; exact H | discriminate H].
    + revert H; destruct (hreal_int_of f); intro H; [rewrite Z.eqb_sym; exact H | discriminate H].
    + apply F_eqb_spec in H; apply F_eqb_spec; symmetry; exact H.
  - intros s b _ _ H; destruct b; simpl in *; try discriminate H.
    apply String.eqb_eq in H; subst; apply key_refl.
  - intros l IH b Ha Hb H; destruct b; simpl in *; try discriminate H.
    exact (IH _ Ha Hb H).
  - intros l IH b Ha Hb H; destruct b; simpl in *; try discriminate H.
    exact (IH _ Ha Hb H).
  - intros p IH b Ha Hb H; destruct b as [| | | | | | |q|]; simpl in *; try discriminate H.
    apply andb_true_iff in Ha as [Hpn Hpw]. apply andb_true_iff in Hb as [Hqn Hqw].
    apply andb_true_iff in H as [Hi Hk].
    rewrite incl_spec in Hi. rewrite keys_in_spec in Hk.
    apply andb_true_iff; split.
    + apply incl_spec. intros k w Hw.
      destruct (mem_get _ _ (Hk k w Hw)) as [v Hv]. exists v. split; [exact Hv|].
      pose proof (get_InP _ _ _ Hv) as HvIn.
      destruct (Hi k v HvIn) as [w' [Hw' Heq]].
      rewrite (InP_get_nodup q k w Hqn Hw) in Hw'. injection Hw' as Ew. subst w'.
      exact (IH k v HvIn w (wf_InP p k v Hpw HvIn) (wf_InP q k w Hqw Hw) Heq).
    + apply keys_in_spec. intros k v Hv. destruct (Hi k v Hv) as [w [Hw _]].
      unfold pairs_mem; rewrite Hw; reflexivity.
  - intros v IH b Ha Hb H; destruct b; simpl in *; try discriminate H.
    exact (IH _ Ha Hb H).
  - intros m _ _ H; destruct m; simpl in *; [reflexivity | discriminate H].
  - intros h IHh t IHt m Hl Hm H; destruct m as [|y u]; simpl in *; [discriminate H|].
    apply andb_true_iff in Hl as [Hh Ht]; apply andb_true_iff in Hm as [Hy Hu].
    apply andb_true_iff in H as [H1 H2].
    rewrite (IHh y Hh Hy H1), (IHt u Ht Hu H2). reflexivity.
  - intros k v [].
  - intros k v IHv t IHt k' v' [[_ E]|Hi]; [subst v'; exact IHv | exact (IHt k' v' Hi)].
Qed.

Theorem hval_eq_sym : forall a b, hval_wf a = true -> hval_wf b = true ->
  hval_eq a b = hval_eq b a.
Proof.
  intros a b Ha Hb.
  destruct (hval_eq a b) eqn:E1; destruct (hval_eq b a) eqn:E2; try reflexivity.
  - pose proof (hval_eq_sym_true a b Ha Hb E1); congruence.
  - pose proof (hval_eq_sym_true b a Hb Ha E2); congruence.
Qed.

(* ---- dict equality depends on the lookups only: ORDER-INDEPENDENT ---- *)
Theorem eq_map_iff : forall p q, pairs_nodup p = true ->
  (hval_eq (HMap p) (HMap q) = true <->
   (forall k, pairs_mem p k = pairs_mem q k) /\
   (forall k v w, pairs_get p k = Some v -> pairs_get q k = Some w -> hval_eq v w = true)).
Proof.
  intros p q Hn. simpl. rewrite andb_true_iff, incl_spec, keys_in_spec. split.
  - intros [Hi Hk]. split.
    + intros k. destruct (pairs_mem p k) eqn:Ep; destruct (pairs_mem q k) eqn:Eq;
        try reflexivity.
      * destruct (mem_get _ _ Ep) as [v Hv].
        destruct (Hi k v (get_InP _ _ _ Hv)) as [w [Hw _]].
        unfold pairs_mem in Eq; rewrite Hw in Eq; discriminate Eq.
      * destruct (mem_get _ _ Eq) as [w Hw].
        rewrite (Hk k w (get_InP _ _ _ Hw)) in Ep; discriminate Ep.
    + intros k v w Hv Hw. destruct (Hi k v (get_InP _ _ _ Hv)) as [w' [Hw' E]].
      rewrite Hw in Hw'. injection Hw' as Ew. subst w'. exact E.
  - intros [Hm Hv]. split.
    + intros k v Hi. pose proof (InP_get_nodup p k v Hn Hi) as Hg.
      assert (Hq : pairs_mem q k = true)
        by (rewrite <- Hm; unfold pairs_mem; rewrite Hg; reflexivity).
      destruct (mem_get _ _ Hq) as [w Hw]. exists w; split; [exact Hw|].
      exact (Hv k v w Hg Hw).
    + intros k w Hi. rewrite Hm. exact (InP_mem q k w Hi).
Qed.

Theorem eq_dict_order_independent : forall p p' c,
  pairs_nodup p = true -> pairs_nodup p' = true ->
  (forall k, pairs_get p k = pairs_get p' k) ->
  hval_eq (HMap p) c = hval_eq (HMap p') c.
Proof.
  intros p p' c Hp Hp' H. destruct c as [| | | | | | |q|]; try reflexivity.
  apply Bool.eq_true_iff_eq. rewrite (eq_map_iff p q Hp), (eq_map_iff p' q Hp').
  split; intros [A B]; split.
  - intros k; unfold pairs_mem in *; rewrite <- H; apply A.
  - intros k v w Hv Hw; apply (B k v w); [rewrite H; exact Hv | exact Hw].
  - intros k; unfold pairs_mem in *; rewrite H; apply A.
  - intros k v w Hv Hw; apply (B k v w); [rewrite <- H; exact Hv | exact Hw].
Qed.

(* ---- the numeric tower is Python's: equality of the mathematical value ---- *)
Definition hnum (v : hval) : option F :=
  match v with
  | HBool b => Some (from_int (hbool_int b))
  | HInt i => Some (from_int i)
  | HFloat f => Some f
  | _ => None
  end.

Lemma zeq_from_int : forall i j, Z.eqb i j = true <-> from_int i = from_int j.
Proof.
  intros i j; rewrite Z.eqb_eq; split; intro X; [subst; reflexivity | apply from_int_inj; exact X].
Qed.

Lemma int_float : forall i g,
  (match hreal_int_of g with Some j => Z.eqb i j | None => false end) = true <-> from_int i = g.
Proof.
  intros i g; destruct (hreal_int_of g) as [j|] eqn:E.
  - apply hreal_int_of_some in E. rewrite Z.eqb_eq.
    split; intro X; [rewrite X; exact E | apply from_int_inj; congruence].
  - split; intro X; [discriminate X | exfalso; exact (hreal_int_of_none g E i X)].
Qed.

Lemma float_int : forall f j,
  (match hreal_int_of f with Some i => Z.eqb i j | None => false end) = true <-> f = from_int j.
Proof.
  intros f j; destruct (hreal_int_of f) as [i|] eqn:E.
  - apply hreal_int_of_some in E. rewrite Z.eqb_eq.
    split; intro X; [rewrite <- E, X; reflexivity | apply from_int_inj; congruence].
  - split; intro X; [discriminate X | exfalso; exact (hreal_int_of_none f E j (eq_sym X))].
Qed.

Theorem eq_numeric_tower : forall a b fa fb, hnum a = Some fa -> hnum b = Some fb ->
  (hval_eq a b = true <-> fa = fb).
Proof.
  intros a b fa fb Ha Hb.
  destruct a as [|x|i|f|s|l|l|p|v]; cbn [hnum] in Ha; try discriminate Ha;
    injection Ha as Ea; subst fa;
  destruct b as [|y|j|g|s'|m|m|q|w]; cbn [hnum] in Hb; try discriminate Hb;
    injection Hb as Eb; subst fb; cbn [hval_eq].
  all: first [ apply zeq_from_int | apply int_float | apply float_int | apply F_eqb_spec
             | (destruct x, y; unfold hbool_int; simpl; split; intro X;
                try reflexivity; try discriminate X; apply from_int_inj in X; discriminate X) ].
Qed.

(* ---- the cross-type equality table (Python ground truth) ---- *)
Theorem eq_true_one : hval_eq (HBool true) (HInt 1) = true.
Proof. reflexivity. Qed.
Theorem eq_one_true : hval_eq (HInt 1) (HBool true) = true.
Proof. reflexivity. Qed.
Theorem eq_false_zero : hval_eq (HBool false) (HInt 0) = true.
Proof. reflexivity. Qed.
Theorem eq_true_two : hval_eq (HBool true) (HInt 2) = false.
Proof. reflexivity. Qed.
Theorem eq_one_onef : hval_eq (HInt 1) (HFloat (from_int 1)) = true.
Proof. cbn [hval_eq]; rewrite hreal_int_of_from_int; reflexivity. Qed.
Theorem eq_onef_one : hval_eq (HFloat (from_int 1)) (HInt 1) = true.
Proof. cbn [hval_eq]; rewrite hreal_int_of_from_int; reflexivity. Qed.
Theorem eq_true_onef : hval_eq (HBool true) (HFloat (from_int 1)) = true.
Proof. cbn [hval_eq]; rewrite hreal_int_of_from_int; reflexivity. Qed.
Theorem eq_int_nonintegral : forall i g, hreal_int_of g = None -> hval_eq (HInt i) (HFloat g) = false.
Proof. intros i g E; cbn [hval_eq]; rewrite E; reflexivity. Qed.
Theorem eq_str_int : forall s i, hval_eq (HStr s) (HInt i) = false.
Proof. reflexivity. Qed.
Theorem eq_one_str_one : hval_eq (HStr "1") (HInt 1) = false.
Proof. reflexivity. Qed.
Theorem eq_none_zero : hval_eq HNone (HInt 0) = false.
Proof. reflexivity. Qed.
Theorem eq_none_false : hval_eq HNone (HBool false) = false.
Proof. reflexivity. Qed.
Theorem eq_none_none : hval_eq HNone HNone = true.
Proof. reflexivity. Qed.
Theorem eq_tuple_list : forall l m, hval_eq (HTuple l) (HArr m) = false.
Proof. reflexivity. Qed.
Theorem eq_tuple1_list1 : hval_eq (HTuple (HCons (HInt 1) HNil)) (HArr (HCons (HInt 1) HNil)) = false.
Proof. reflexivity. Qed.
Theorem eq_list_tuple : forall l m, hval_eq (HArr l) (HTuple m) = false.
Proof. reflexivity. Qed.
Theorem eq_dict_order : forall x y, hval_wf x = true -> hval_wf y = true ->
  hval_eq (HMap (PCons "a" x (PCons "b" y PNil))) (HMap (PCons "b" y (PCons "a" x PNil))) = true.
Proof.
  intros x y Hx Hy. simpl. rewrite (hval_eq_refl x Hx), (hval_eq_refl y Hy). reflexivity.
Qed.


(* ---- one-level unfoldings of hval_eq at a LITERAL (the emitter inlines these RHS
        at `v == <literal>`; statements match the WhyML lemmas hval_eq_*_lit) ---- *)
Theorem hval_eq_int_lit : forall v n, hval_eq v (HInt n) =
  match v with
  | HInt i => Z.eqb i n
  | HBool b => Z.eqb (hbool_int b) n
  | HFloat f => match hreal_int_of f with Some j => Z.eqb j n | None => false end
  | _ => false
  end.
Proof. intros v n; destruct v; reflexivity. Qed.

Theorem hval_eq_bool_lit : forall v x, hval_eq v (HBool x) =
  match v with
  | HInt i => Z.eqb i (hbool_int x)
  | HBool b => Z.eqb (hbool_int b) (hbool_int x)
  | HFloat f => match hreal_int_of f with Some j => Z.eqb j (hbool_int x) | None => false end
  | _ => false
  end.
Proof.
  intros v x; destruct v as [|b| | | | | | | ]; try reflexivity.
  destruct b, x; reflexivity.
Qed.

Theorem hval_eq_intfloat_lit : forall v n, hval_eq v (HFloat (from_int n)) =
  match v with
  | HInt i => Z.eqb i n
  | HBool b => Z.eqb (hbool_int b) n
  | HFloat f => match hreal_int_of f with Some j => Z.eqb j n | None => false end
  | _ => false
  end.
Proof.
  intros v n; destruct v as [|b|i|f|s|l|l|p|x]; cbn [hval_eq];
    try rewrite hreal_int_of_from_int; try reflexivity.
  apply Bool.eq_true_iff_eq. rewrite F_eqb_spec, float_int. split; intro H; exact H.
Qed.

Theorem hval_eq_float_lit : forall v c, hreal_int_of c = None ->
  hval_eq v (HFloat c) = match v with HFloat f => F_eqb f c | _ => false end.
Proof. intros v c H; destruct v; cbn [hval_eq]; try rewrite H; reflexivity. Qed.

Theorem hval_eq_none_lit : forall v, hval_eq v HNone = match v with HNone => true | _ => false end.
Proof. intros v; destruct v; reflexivity. Qed.

Theorem hval_eq_str_lit : forall v t,
  hval_eq v (HStr t) = match v with HStr s => hpairs_key_eq s t | _ => false end.
Proof. intros v t; destruct v; reflexivity. Qed.

(* ===================================================================== *)
(* 5. Key canonicalisation and hashability.                               *)
(* ===================================================================== *)

Fixpoint hval_canon (v : hval) : hval :=
  match v with
  | HBool b => HInt (hbool_int b)
  | HFloat f => match hreal_int_of f with Some i => HInt i | None => HFloat f end
  | HTuple l => HTuple (hlist_canon l)
  | _ => v
  end
with hlist_canon (l : hval_list) : hval_list :=
  match l with HNil => HNil | HCons x t => HCons (hval_canon x) (hlist_canon t) end.

Fixpoint hval_hashable (v : hval) : bool :=
  match v with
  | HNone => true | HBool _ => true | HInt _ => true | HFloat _ => true | HStr _ => true
  | HTuple l => hlist_hashable l
  | _ => false
  end
with hlist_hashable (l : hval_list) : bool :=
  match l with HNil => true | HCons x t => hval_hashable x && hlist_hashable t end.

Lemma zeq_hint : forall i j, Z.eqb i j = true <-> HInt i = HInt j.
Proof. intros i j; rewrite Z.eqb_eq; split; intro X; [subst; reflexivity | injection X; auto]. Qed.
Lemma streq_hstr : forall s t, String.eqb s t = true <-> HStr s = HStr t.
Proof. intros s t; rewrite String.eqb_eq; split; intro X; [subst; reflexivity | injection X; auto]. Qed.

Lemma float_canon : forall f g,
  F_eqb f g = true <->
  (match hreal_int_of f with Some i => HInt i | None => HFloat f end) =
  (match hreal_int_of g with Some i => HInt i | None => HFloat g end).
Proof.
  intros f g. rewrite F_eqb_spec.
  destruct (hreal_int_of f) as [i|] eqn:Ef; destruct (hreal_int_of g) as [j|] eqn:Eg.
  - apply hreal_int_of_some in Ef; apply hreal_int_of_some in Eg. split; intro X.
    + rewrite <- Ef, <- Eg in X. apply from_int_inj in X. subst; reflexivity.
    + injection X as Eij. subst j. rewrite <- Ef, <- Eg; reflexivity.
  - split; intro X; [exfalso | discriminate X].
    apply hreal_int_of_some in Ef. apply (hreal_int_of_none g Eg i). congruence.
  - split; intro X; [exfalso | discriminate X].
    apply hreal_int_of_some in Eg. apply (hreal_int_of_none f Ef j). congruence.
  - split; intro X; [subst; reflexivity | injection X; auto].
Qed.

Ltac coh_finish :=
  repeat match goal with
         | |- context [hreal_int_of ?g] => let E := fresh "E" in destruct (hreal_int_of g) eqn:E
         end;
  cbv beta iota;
  first [ apply zeq_hint | apply streq_hstr
        | solve [split; intro; discriminate]
        | solve [split; intro; reflexivity] ].

Ltac coh_case :=
  first [ solve [apply float_canon]
        | solve [match goal with
                 | |- (if ?x then ?y else negb ?y) = true <-> _ =>
                     destruct x, y; unfold hbool_int; simpl; split; intro;
                     try reflexivity; discriminate
                 end]
        | solve [coh_finish] ].

Definition coh_P (a : hval) := forall b, hval_hashable a = true -> hval_hashable b = true ->
  (hval_eq a b = true <-> hval_canon a = hval_canon b).
Definition coh_Q (l : hval_list) := forall m, hlist_hashable l = true -> hlist_hashable m = true ->
  (hlist_eq l m = true <-> hlist_canon l = hlist_canon m).
Definition coh_R (p : hpairs) := True.

Theorem eq_canon_coherent : forall a b, hval_hashable a = true -> hval_hashable b = true ->
  (hval_eq a b = true <-> hval_canon a = hval_canon b).
Proof.
  apply (hval_mut coh_P coh_Q coh_R); unfold coh_P, coh_Q, coh_R; simpl.
  - intros b _ Hb; destruct b; simpl in *; try discriminate Hb; coh_case.
  - intros x b _ Hb; destruct b; simpl in *; try discriminate Hb; coh_case.
  - intros i b _ Hb; destruct b; simpl in *; try discriminate Hb; coh_case.
  - intros f b _ Hb; destruct b; simpl in *; try discriminate Hb; coh_case.
  - intros s b _ Hb; destruct b; simpl in *; try discriminate Hb; coh_case.
  - intros l IH b Ha Hb; destruct b as [| | | | |m| | |]; simpl in *; try discriminate Hb;
      try coh_case.
    rewrite (IH m Ha Hb). split; intro X; [rewrite X; reflexivity | injection X; auto].
  - intros l _ b Ha; discriminate Ha.
  - intros p _ b Ha; discriminate Ha.
  - intros v _ b Ha; discriminate Ha.
  - intros m _ Hm; destruct m; simpl; split; intro X; try reflexivity; discriminate X.
  - intros h IHh t IHt m Hl Hm; destruct m as [|y u]; simpl in *.
    + split; intro X; discriminate X.
    + apply andb_true_iff in Hl as [Hh Ht]; apply andb_true_iff in Hm as [Hy Hu].
      rewrite andb_true_iff, (IHh y Hh Hy), (IHt u Ht Hu).
      split; [intros [E1 E2]; rewrite E1, E2; reflexivity
             | intro X; injection X as E1 E2; split; assumption].
  - exact I.
  - intros; exact I.
Qed.

Theorem hval_eq_refl_hashable : forall a, hval_hashable a = true -> hval_eq a a = true.
Proof. intros a H; apply (proj2 (eq_canon_coherent a a H H)); reflexivity. Qed.

Theorem canon_true : hval_canon (HBool true) = HInt 1.
Proof. reflexivity. Qed.
Theorem canon_false : hval_canon (HBool false) = HInt 0.
Proof. reflexivity. Qed.
Theorem canon_onef : hval_canon (HFloat (from_int 1)) = HInt 1.
Proof. cbn [hval_canon]; rewrite hreal_int_of_from_int; reflexivity. Qed.
Theorem canon_nonintegral : forall g, hreal_int_of g = None -> hval_canon (HFloat g) = HFloat g.
Proof. intros g E; cbn [hval_canon]; rewrite E; reflexivity. Qed.
Theorem canon_merges_keys : hval_canon (HInt 1) = hval_canon (HBool true) /\
                            hval_canon (HInt 1) = hval_canon (HFloat (from_int 1)).
Proof. split; [reflexivity | symmetry; apply canon_onef]. Qed.
Theorem hashable_scalars : forall b i f s,
  hval_hashable HNone = true /\ hval_hashable (HBool b) = true /\ hval_hashable (HInt i) = true /\
  hval_hashable (HFloat f) = true /\ hval_hashable (HStr s) = true.
Proof. intros; repeat split. Qed.
Theorem hashable_tuple : forall x t,
  hval_hashable (HTuple (HCons x t)) = (hval_hashable x && hval_hashable (HTuple t)).
Proof. reflexivity. Qed.
Theorem unhashable_list : forall l, hval_hashable (HArr l) = false.
Proof. reflexivity. Qed.
Theorem unhashable_dict : forall p, hval_hashable (HMap p) = false.
Proof. reflexivity. Qed.
Theorem unhashable_node : forall v, hval_hashable (HNode v) = false.
Proof. reflexivity. Qed.
Theorem unhashable_tuple_of_list : forall l,
  hval_hashable (HTuple (HCons (HArr l) HNil)) = false.
Proof. reflexivity. Qed.

(* ===================================================================== *)
(* 6. Python truthiness over all 9 tags.                                  *)
(* ===================================================================== *)

Definition hval_truthy (h : hval) : bool :=
  match h with
  | HNone => false
  | HBool b => b
  | HInt i => negb (Z.eqb i 0)
  | HFloat f => negb (F_eqb f (from_int 0))      (* `0.0` = from_int 0, FromInt.Zero *)
  | HStr s => negb (hpairs_key_eq s "")
  | HTuple l => match l with HNil => false | _ => true end
  | HArr l => match l with HNil => false | _ => true end
  | HMap p => match p with PNil => false | _ => true end
  | HNode _ => true
  end.

(* the falsy values of Python: None False 0 0.0 "" () [] {} *)
Theorem truthy_none : hval_truthy HNone = false.
Proof. reflexivity. Qed.
Theorem truthy_false : hval_truthy (HBool false) = false.
Proof. reflexivity. Qed.
Theorem truthy_zero : hval_truthy (HInt 0) = false.
Proof. reflexivity. Qed.
Theorem truthy_fzero : hval_truthy (HFloat (from_int 0)) = false.
Proof. cbn [hval_truthy]. rewrite (proj2 (F_eqb_spec _ _) eq_refl). reflexivity. Qed.
Theorem truthy_empty_str : hval_truthy (HStr "") = false.
Proof. reflexivity. Qed.
Theorem truthy_empty_tuple : hval_truthy (HTuple HNil) = false.
Proof. reflexivity. Qed.
Theorem truthy_empty_list : hval_truthy (HArr HNil) = false.
Proof. reflexivity. Qed.
Theorem truthy_empty_dict : hval_truthy (HMap PNil) = false.
Proof. reflexivity. Qed.
(* everything else is truthy *)
Theorem truthy_true : hval_truthy (HBool true) = true.
Proof. reflexivity. Qed.
Theorem truthy_int : forall i, i <> 0 -> hval_truthy (HInt i) = true.
Proof. intros i H; cbn [hval_truthy]; destruct (Z.eqb_spec i 0); [contradiction | reflexivity]. Qed.
Theorem truthy_float : forall f, f <> from_int 0 -> hval_truthy (HFloat f) = true.
Proof.
  intros f H; cbn [hval_truthy]. destruct (F_eqb f (from_int 0)) eqn:E; [|reflexivity].
  apply F_eqb_spec in E; contradiction.
Qed.
Theorem truthy_str : forall s, s <> "" -> hval_truthy (HStr s) = true.
Proof. intros s H; cbn [hval_truthy]; destruct (String.eqb_spec s ""); [contradiction | reflexivity]. Qed.
Theorem truthy_tuple : forall x l, hval_truthy (HTuple (HCons x l)) = true.
Proof. reflexivity. Qed.
Theorem truthy_list : forall x l, hval_truthy (HArr (HCons x l)) = true.
Proof. reflexivity. Qed.
Theorem truthy_dict : forall k x p, hval_truthy (HMap (PCons k x p)) = true.
Proof. reflexivity. Qed.
Theorem truthy_node : forall n, hval_truthy (HNode n) = true.
Proof. reflexivity. Qed.
(* completeness: a falsy value IS one of the eight Python falsy values *)
Theorem truthy_false_iff : forall v, hval_truthy v = false <->
  v = HNone \/ v = HBool false \/ v = HInt 0 \/ v = HFloat (from_int 0) \/
  v = HStr "" \/ v = HTuple HNil \/ v = HArr HNil \/ v = HMap PNil.
Proof.
  intros v; split.
  - destruct v as [|b|n|f|s|l|l|p|x]; cbn [hval_truthy].
    + intros _; left; reflexivity.
    + destruct b; intro X; [discriminate X|]. right; left; reflexivity.
    + destruct (Z.eqb_spec n 0) as [E|N]; intro X;
        [subst; do 2 right; left; reflexivity | discriminate X].
    + destruct (F_eqb f (from_int 0)) eqn:E; intro X; [|discriminate X].
      apply F_eqb_spec in E; subst; do 3 right; left; reflexivity.
    + destruct (String.eqb_spec s "") as [E|N]; intro X;
        [subst; do 4 right; left; reflexivity | discriminate X].
    + destruct l; intro X; [do 5 right; left; reflexivity | discriminate X].
    + destruct l; intro X; [do 6 right; left; reflexivity | discriminate X].
    + destruct p; intro X; [do 7 right; reflexivity | discriminate X].
    + intro X; discriminate X.
  - intros [E|[E|[E|[E|[E|[E|[E|E]]]]]]]; subst;
      first [ apply truthy_fzero | reflexivity ].
Qed.

(* ===================================================================== *)
(* 7. Projections.                                                        *)
(* ===================================================================== *)

Definition hstr_of (h : hval) : string :=
  match h with HStr s => s | _ => hval_opaque_str h end.
Definition hint_of (h : hval) : Z :=
  match h with HInt i => i | HBool b => hbool_int b | _ => hval_opaque_int h end.

Theorem proj_on_tag_str : forall s, hstr_of (HStr s) = s.
Proof. reflexivity. Qed.
Theorem proj_on_tag_int : forall i, hint_of (HInt i) = i.
Proof. reflexivity. Qed.
Theorem proj_on_tag_bool : forall b, hint_of (HBool b) = if b then 1 else 0.
Proof. reflexivity. Qed.
Theorem proj_off_tag_str : forall h, (forall s, h <> HStr s) -> hstr_of h = hval_opaque_str h.
Proof. intros h H; destruct h; try reflexivity; exfalso; eapply H; reflexivity. Qed.
Theorem proj_off_tag_int : forall h, (forall i, h <> HInt i) -> (forall b, h <> HBool b) ->
  hint_of h = hval_opaque_int h.
Proof. intros h H1 H2; destruct h; try reflexivity; exfalso; [eapply H2 | eapply H1]; reflexivity. Qed.
(* totality: the projections are total functions on hval (no partiality, no junk value
   on the tag: off-tag is the uninterpreted arm) *)
Theorem proj_total : forall h, exists s i, hstr_of h = s /\ hint_of h = i.
Proof. intros h; exists (hstr_of h), (hint_of h); split; reflexivity. Qed.

(* ===================================================================== *)
(* 8. Sequences: len / nth / tuple / snoc.                                *)
(* ===================================================================== *)

Fixpoint hval_list_len (l : hval_list) : Z :=
  match l with HNil => 0 | HCons _ t => 1 + hval_list_len t end.

(* verbatim the emitted hval_list_nth (out-of-range arm `HInt 0`) *)
Fixpoint hval_list_nth (l : hval_list) (i : Z) : hval :=
  match l with
  | HNil => HInt 0
  | HCons x t => if Z.leb i 0 then x else hval_list_nth t (i - 1)
  end.

Definition hstr_len (s : string) : Z := Z.of_nat (String.length s).

Definition hval_len (h : hval) : Z :=
  match h with
  | HStr s => hstr_len s
  | HTuple l => hval_list_len l
  | HArr l => hval_list_len l
  | HMap p => hpairs_len p
  | _ => hval_len_other h
  end.

Definition hval_tuple (h : hval) : hval :=
  match h with
  | HTuple l => HTuple l
  | HArr l => HTuple l
  | HMap p => HTuple (hpairs_keys p)
  | _ => hval_tuple_other h
  end.

Fixpoint hval_list_snoc (l : hval_list) (x : hval) : hval_list :=
  match l with HNil => HCons x HNil | HCons h t => HCons h (hval_list_snoc t x) end.

Fixpoint InL (x : hval) (l : hval_list) : Prop :=
  match l with HNil => False | HCons y t => x = y \/ InL x t end.

Theorem len_nonneg : forall l, hval_list_len l >= 0.
Proof. induction l as [|x t IH]; cbn [hval_list_len]; lia. Qed.

Theorem nth_head : forall x t, hval_list_nth (HCons x t) 0 = x.
Proof. reflexivity. Qed.

Theorem nth_tail : forall x t i, i >= 0 -> hval_list_nth (HCons x t) (i + 1) = hval_list_nth t i.
Proof.
  intros x t i H; cbn [hval_list_nth].
  destruct (Z.leb_spec (i + 1) 0); [lia|]. cbv beta iota. f_equal; lia.
Qed.

Theorem nth_in_range : forall l i, 0 <= i < hval_list_len l -> InL (hval_list_nth l i) l.
Proof.
  induction l as [|x t IH]; intros i H; cbn [hval_list_len] in H; [lia|].
  cbn [hval_list_nth InL]. destruct (Z.leb_spec i 0).
  - left; reflexivity.
  - right. cbv beta iota. apply IH. pose proof (len_nonneg t); lia.
Qed.

Theorem snoc_len : forall l x, hval_list_len (hval_list_snoc l x) = hval_list_len l + 1.
Proof. induction l as [|h t IH]; intros x; cbn [hval_list_snoc hval_list_len]; [reflexivity | rewrite IH; lia]. Qed.

Theorem snoc_nth_last : forall l x, hval_list_nth (hval_list_snoc l x) (hval_list_len l) = x.
Proof.
  induction l as [|h t IH]; intros x; cbn [hval_list_snoc hval_list_len hval_list_nth].
  - reflexivity.
  - pose proof (len_nonneg t). destruct (Z.leb_spec (1 + hval_list_len t) 0); [lia|]. cbv beta iota.
    replace (1 + hval_list_len t - 1) with (hval_list_len t) by lia. apply IH.
Qed.

Theorem keys_len : forall p, hval_list_len (hpairs_keys p) = hpairs_len p.
Proof. induction p as [|k v t IH]; cbn [hpairs_keys hval_list_len hpairs_len]; [reflexivity | rewrite IH; reflexivity]. Qed.

Theorem len_str : forall s, hval_len (HStr s) = Z.of_nat (String.length s).
Proof. reflexivity. Qed.
Theorem len_tuple : forall l, hval_len (HTuple l) = hval_list_len l.
Proof. reflexivity. Qed.
Theorem len_arr : forall l, hval_len (HArr l) = hval_list_len l.
Proof. reflexivity. Qed.
Theorem len_map : forall p, hval_len (HMap p) = hpairs_len p.
Proof. reflexivity. Qed.
Theorem len_nonneg_on_tag : forall h,
  (exists s, h = HStr s) \/ (exists l, h = HTuple l) \/ (exists l, h = HArr l) \/ (exists p, h = HMap p) ->
  hval_len h >= 0.
Proof.
  intros h [[s E]|[[l E]|[[l E]|[p E]]]]; subst; cbn [hval_len];
    [unfold hstr_len; lia | apply len_nonneg | apply len_nonneg | apply hpairs_len_nonneg].
Qed.
(* the dict literal's len counts DISTINCT keys (last-wins fold) *)
Theorem len_literal_dup : forall a b, hval_len (HMap (pairs_build PNil [("a", a); ("a", b)])) = 1.
Proof. reflexivity. Qed.

Theorem tuple_preserves_elems : forall l,
  hval_tuple (HArr l) = HTuple l /\ hval_tuple (HTuple l) = HTuple l /\
  hval_len (hval_tuple (HArr l)) = hval_len (HArr l) /\
  (forall i, match hval_tuple (HArr l) with HTuple l' => hval_list_nth l' i | _ => HNone end
             = hval_list_nth l i).
Proof. intros l; repeat split; intros; reflexivity. Qed.
Theorem tuple_of_dict_keys : forall p, hval_tuple (HMap p) = HTuple (hpairs_keys p) /\
  hval_len (hval_tuple (HMap p)) = hval_len (HMap p).
Proof. intros p; split; [reflexivity | cbn [hval_tuple hval_len]; apply keys_len]. Qed.

End PyValR4.

(* ===================================================================== *)
(* 9. A concrete axiom-free model of the carrier laws (satisfiability):   *)
(*    (n, false) is the integer n, (n, true) is the non-integral n + 1/2. *)
(* ===================================================================== *)

Definition CF : Type := (Z * bool)%type.
Definition cf_eqb (a b : CF) : bool := Z.eqb (fst a) (fst b) && Bool.eqb (snd a) (snd b).
Definition cf_from_int (i : Z) : CF := (i, false).
Definition cf_int_of (f : CF) : option Z := if snd f then None else Some (fst f).

Theorem cf_eqb_spec : forall a b : CF, cf_eqb a b = true <-> a = b.
Proof.
  intros [x p] [y q]; unfold cf_eqb; cbn [fst snd].
  rewrite andb_true_iff, Z.eqb_eq. split.
  - intros [-> E]. apply Bool.eqb_prop in E. subst; reflexivity.
  - intros E; injection E as -> ->. split; [reflexivity | apply Bool.eqb_reflx].
Qed.
Theorem cf_from_int_inj : forall i j, cf_from_int i = cf_from_int j -> i = j.
Proof. intros i j E; injection E; auto. Qed.
Theorem cf_int_of_some : forall f i, cf_int_of f = Some i -> cf_from_int i = f.
Proof.
  intros [n b] i; unfold cf_int_of, cf_from_int; cbn [fst snd].
  destruct b; intro E; [discriminate E | injection E as ->; reflexivity].
Qed.
Theorem cf_int_of_none : forall f, cf_int_of f = None -> forall i, cf_from_int i <> f.
Proof.
  intros [n b]; unfold cf_int_of, cf_from_int; cbn [fst snd].
  destruct b; intros E i X; [discriminate X | discriminate E].
Qed.

(* the model instantiates every section theorem; two computed witnesses: *)
Theorem model_half_ne_int : forall i,
  @hval_eq CF cf_eqb cf_int_of (@HInt CF i) (@HFloat CF (0%Z, true)) = false.
Proof. reflexivity. Qed.
Theorem model_one_eq_onef :
  @hval_eq CF cf_eqb cf_int_of (@HInt CF 1%Z) (@HFloat CF (cf_from_int 1%Z)) = true.
Proof. reflexivity. Qed.
Theorem model_eq_sym : forall a b : hval CF,
  hval_wf CF a = true -> hval_wf CF b = true ->
  @hval_eq CF cf_eqb cf_int_of a b = @hval_eq CF cf_eqb cf_int_of b a.
Proof.
  intros a b Ha Hb. eapply hval_eq_sym.
  all: first [ exact cf_eqb_spec | exact cf_from_int_inj | exact cf_int_of_some
             | exact cf_int_of_none | exact Ha | exact Hb ].
Qed.

(* ===================================================================== *)
(* 9b. The WhyML `val hreal_int_of` spec is the EQUATION                  *)
(*       result = if from_int (truncate f) = f then Some (truncate f)    *)
(*                else None                                               *)
(*     (real.Truncate; Truncate_int : truncate (from_int i) = i).  Any    *)
(*     function given by that equation satisfies the two carrier laws     *)
(*     hreal_int_of_some / hreal_int_of_none used above.                  *)
(* ===================================================================== *)

Section IntOfRealisation.
Variable G : Type.
Variable G_eqb : G -> G -> bool.
Hypothesis G_eqb_spec : forall a b : G, G_eqb a b = true <-> a = b.
Variable g_from_int : Z -> G.
Variable g_truncate : G -> Z.
Hypothesis truncate_from_int : forall i, g_truncate (g_from_int i) = i.

Definition int_of_eqn (f : G) : option Z :=
  if G_eqb (g_from_int (g_truncate f)) f then Some (g_truncate f) else None.

Theorem int_of_eqn_some : forall f i, int_of_eqn f = Some i -> g_from_int i = f.
Proof.
  intros f i; unfold int_of_eqn.
  destruct (G_eqb (g_from_int (g_truncate f)) f) eqn:E; intro H; [|discriminate H].
  injection H as <-. apply G_eqb_spec; exact E.
Qed.

Theorem int_of_eqn_none : forall f, int_of_eqn f = None -> forall i, g_from_int i <> f.
Proof.
  intros f; unfold int_of_eqn.
  destruct (G_eqb (g_from_int (g_truncate f)) f) eqn:E; intro H; [discriminate H|].
  intros i X. subst f. rewrite truncate_from_int in E.
  rewrite (proj2 (G_eqb_spec _ _) eq_refl) in E. discriminate E.
Qed.
End IntOfRealisation.

(* ===================================================================== *)
(* 10. VERDICT — assumption audit: every line must print                 *)
(*     `Closed under the global context` (NO axiom; ledger stays 3).      *)
(* ===================================================================== *)

Print Assumptions key_refl.
Print Assumptions hpairs_key_eq_spec.
Print Assumptions hreal_int_of_from_int.
Print Assumptions size_pos.
Print Assumptions list_size_nonneg.
Print Assumptions pairs_size_nonneg.
Print Assumptions list_tail_size_lt.
Print Assumptions pairs_tail_size_lt.
Print Assumptions size_sub_tuple.
Print Assumptions size_sub_arr.
Print Assumptions size_sub_map.
Print Assumptions size_sub_node.
Print Assumptions hbool_inj.
Print Assumptions hint_inj.
Print Assumptions hfloat_inj.
Print Assumptions hstr_inj.
Print Assumptions htuple_inj.
Print Assumptions harr_inj.
Print Assumptions hmap_inj.
Print Assumptions hnode_inj.
Print Assumptions hcons_inj.
Print Assumptions pcons_inj.
Print Assumptions hnil_neq_hcons.
Print Assumptions pnil_neq_pcons.
Print Assumptions neq_none_bool.
Print Assumptions neq_none_int.
Print Assumptions neq_none_float.
Print Assumptions neq_none_str.
Print Assumptions neq_none_tuple.
Print Assumptions neq_none_arr.
Print Assumptions neq_none_map.
Print Assumptions neq_none_node.
Print Assumptions neq_bool_int.
Print Assumptions neq_bool_float.
Print Assumptions neq_bool_str.
Print Assumptions neq_bool_tuple.
Print Assumptions neq_bool_arr.
Print Assumptions neq_bool_map.
Print Assumptions neq_bool_node.
Print Assumptions neq_int_float.
Print Assumptions neq_int_str.
Print Assumptions neq_int_tuple.
Print Assumptions neq_int_arr.
Print Assumptions neq_int_map.
Print Assumptions neq_int_node.
Print Assumptions neq_float_str.
Print Assumptions neq_float_tuple.
Print Assumptions neq_float_arr.
Print Assumptions neq_float_map.
Print Assumptions neq_float_node.
Print Assumptions neq_str_tuple.
Print Assumptions neq_str_arr.
Print Assumptions neq_str_map.
Print Assumptions neq_str_node.
Print Assumptions neq_tuple_arr.
Print Assumptions neq_tuple_map.
Print Assumptions neq_tuple_node.
Print Assumptions neq_arr_map.
Print Assumptions neq_arr_node.
Print Assumptions neq_map_node.
Print Assumptions pairs_get_nil.
Print Assumptions pairs_get_cons.
Print Assumptions pairs_set_get.
Print Assumptions read_same_key.
Print Assumptions read_other_key.
Print Assumptions mem_set.
Print Assumptions nodup_preserved.
Print Assumptions len_set.
Print Assumptions hpairs_len_nonneg.
Print Assumptions build_is_fold_left.
Print Assumptions build_fold_read_back.
Print Assumptions build_nodup.
Print Assumptions build_last_wins.
Print Assumptions build_len_dup.
Print Assumptions build_insertion_order.
Print Assumptions get_InP.
Print Assumptions InP_mem.
Print Assumptions mem_get.
Print Assumptions InP_get_nodup.
Print Assumptions wf_InP.
Print Assumptions incl_spec.
Print Assumptions keys_in_spec.
Print Assumptions hval_eq_refl.
Print Assumptions hval_eq_sym_true.
Print Assumptions hval_eq_sym.
Print Assumptions eq_map_iff.
Print Assumptions eq_dict_order_independent.
Print Assumptions zeq_from_int.
Print Assumptions int_float.
Print Assumptions float_int.
Print Assumptions eq_numeric_tower.
Print Assumptions eq_true_one.
Print Assumptions eq_one_true.
Print Assumptions eq_false_zero.
Print Assumptions eq_true_two.
Print Assumptions eq_one_onef.
Print Assumptions eq_onef_one.
Print Assumptions eq_true_onef.
Print Assumptions eq_int_nonintegral.
Print Assumptions eq_str_int.
Print Assumptions eq_one_str_one.
Print Assumptions eq_none_zero.
Print Assumptions eq_none_false.
Print Assumptions eq_none_none.
Print Assumptions eq_tuple_list.
Print Assumptions eq_tuple1_list1.
Print Assumptions eq_list_tuple.
Print Assumptions eq_dict_order.
Print Assumptions zeq_hint.
Print Assumptions streq_hstr.
Print Assumptions float_canon.
Print Assumptions eq_canon_coherent.
Print Assumptions hval_eq_refl_hashable.
Print Assumptions canon_true.
Print Assumptions canon_false.
Print Assumptions canon_onef.
Print Assumptions canon_nonintegral.
Print Assumptions canon_merges_keys.
Print Assumptions hashable_scalars.
Print Assumptions hashable_tuple.
Print Assumptions unhashable_list.
Print Assumptions unhashable_dict.
Print Assumptions unhashable_node.
Print Assumptions unhashable_tuple_of_list.
Print Assumptions truthy_none.
Print Assumptions truthy_false.
Print Assumptions truthy_zero.
Print Assumptions truthy_fzero.
Print Assumptions truthy_empty_str.
Print Assumptions truthy_empty_tuple.
Print Assumptions truthy_empty_list.
Print Assumptions truthy_empty_dict.
Print Assumptions truthy_true.
Print Assumptions truthy_int.
Print Assumptions truthy_float.
Print Assumptions truthy_str.
Print Assumptions truthy_tuple.
Print Assumptions truthy_list.
Print Assumptions truthy_dict.
Print Assumptions truthy_node.
Print Assumptions truthy_false_iff.
Print Assumptions proj_on_tag_str.
Print Assumptions proj_on_tag_int.
Print Assumptions proj_on_tag_bool.
Print Assumptions proj_off_tag_str.
Print Assumptions proj_off_tag_int.
Print Assumptions proj_total.
Print Assumptions len_nonneg.
Print Assumptions nth_head.
Print Assumptions nth_tail.
Print Assumptions nth_in_range.
Print Assumptions snoc_len.
Print Assumptions snoc_nth_last.
Print Assumptions keys_len.
Print Assumptions len_str.
Print Assumptions len_tuple.
Print Assumptions len_arr.
Print Assumptions len_map.
Print Assumptions len_nonneg_on_tag.
Print Assumptions len_literal_dup.
Print Assumptions tuple_preserves_elems.
Print Assumptions tuple_of_dict_keys.
Print Assumptions cf_eqb_spec.
Print Assumptions cf_from_int_inj.
Print Assumptions cf_int_of_some.
Print Assumptions cf_int_of_none.
Print Assumptions model_half_ne_int.
Print Assumptions model_one_eq_onef.
Print Assumptions model_eq_sym.
Print Assumptions int_of_eqn_some.
Print Assumptions int_of_eqn_none.
Print Assumptions hval_eq_int_lit.
Print Assumptions hval_eq_bool_lit.
Print Assumptions hval_eq_intfloat_lit.
Print Assumptions hval_eq_float_lit.
Print Assumptions hval_eq_none_lit.
Print Assumptions hval_eq_str_lit.
