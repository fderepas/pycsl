(* Phase2f_PyVal.v — axiom-free certificate for the `pyval` heterogeneous value
   model (self-tcb-reduction, Tier-5 value-model wall).

   CO-LANDING COUPLING (the tier-3 rule, cf. Phase2c_PyConstVal.v /
   Phase2d_StmtIR.v / Phase2e_PyAstStmt.v): the WhyML `pyval` theory promoted into
   the emitter preamble (`module6_whyml/preamble.py::_emit_pyval_theory`, gated on
   `_uses_pyval`) is a NEW value shape — the faithful carrier for a heterogeneous
   Python `Dict[str, Any]` (PStr / PInt / PArr / PMap / PNode) — so it lands with a
   proof, not a trusted assumption.  The build (`_build_dict_literal_map` pyval
   branch) tags each dict value into its `pyval` constructor and the read
   (`_dv_missing_default` / `Map.get`) projects it back; this file certifies,
   against pure inductive datatypes with NO axiom, exactly what the emitter relies
   on:

     (a) `pyval` is a well-formed inductive: `PArr` recurses through the BESPOKE
         `pyval_list` (PNil / PCons), NOT `seq` — the strictly-positive shape Why3
         accepts (the `seq pyval` recursion is Why3-rejected); `PMap` carries a
         `string -> option pyval` map, with `pyval` in the POSITIVE arrow codomain
         (Coq, like Why3, accepts the occurrence).  No `variant` clause — the mutual
         structural recursion is inferred;
     (b) the LOAD-BEARING measure `size` / `list_size` (the WhyML cert-side measure)
         is well-founded: `size v >= 1` (the WhyML `size_pos` lemma that SMT alone
         cannot discharge — it needs mutual structural induction; here it is proven),
         `list_size l >= 0`, and the tail of a cons is STRICTLY shorter — so any
         fold over `pyval_list` terminates (no infinite descent);
     (c) the value carriers are OBSERVABLE and DISTINCT — `PStr` is injective, and a
         string value is NEVER erased to an int (`PStr s <> PInt n`): the
         no-more-int faithfulness the whole value model exists to protect;
     (d) the make-or-break heterogeneous DICT read is faithful: modelling the WhyML
         `map string (option pyval)` as `string -> option pyval` with `Map.get` /
         `Map.set`, the string VARIABLE arm reads back FAITHFULLY as `PStr arm_ctor`
         (the oracle's `read_variable_faithful`), a distinct key is untouched, and
         the EVIL TWIN — a WRONG value read — is provably UNprovable (non-vacuity).

   `pyval` has NO decidable equality (the `PMap` functional field makes value
   equality undecidable) — an honest boundary; the emitter never needs it (reads are
   `Map.get` key-projections, compared by Leibniz `=` in the WhyML goals), so it is
   deliberately not claimed.  `size` / `size_pos` are CERT-ONLY (no frontier fold
   needs them; they are NOT emitted into any VC).

   The `Print Assumptions` block at the bottom is the trust check: every result must
   be `Closed under the global context` (NO axiom) so the 3-axiom trust ledger
   (`proof_axiom_allowlist.py`) stays intact.  Nothing here is Admitted.
   Build: part of `make` (listed in `_CoqProject` after `Phase2e_PyAstStmt.v`). *)

Require Import ZArith String List Bool Lia.
Import ListNotations.
Open Scope string_scope.

Section PyVal.

Local Open Scope Z_scope.

(* ===================================================================== *)
(* 1. The heterogeneous value ADT — mirrors the WhyML                     *)
(*      type pyval = PStr string | PInt int | PArr pyval_list             *)
(*                 | PMap (map string (option pyval)) | PNode pyval        *)
(*      with pyval_list = PNil | PCons pyval pyval_list.                   *)
(* ===================================================================== *)

Inductive pyval : Type :=
  | PStr  (s : string)
  | PInt  (n : Z)
  | PArr  (l : pyval_list)
  | PMap  (m : string -> option pyval)
  | PNode (v : pyval)
with pyval_list : Type :=
  | PNil
  | PCons (h : pyval) (t : pyval_list).

(* size / list_size — verbatim image of the WhyML cert-side measure (mutually
   recursive, NO variant clause).  PMap's map has an INFINITE domain, so `size`
   counts the node only (documented deferral, exactly as the WhyML). *)
Fixpoint size (v : pyval) : Z :=
  match v with
  | PStr _  => 1
  | PInt _  => 1
  | PArr l  => 1 + list_size l
  | PMap _  => 1
  | PNode n => 1 + size n
  end
with list_size (l : pyval_list) : Z :=
  match l with
  | PNil      => 0
  | PCons h t => size h + list_size t
  end.

(* The MUTUAL induction principle (Coq's auto-generated `pyval_ind` is weak /
   non-mutual — this is the analogue of Why3's `induction_ty_lex`). *)
Scheme pyval_mut := Induction for pyval Sort Prop
with pyval_list_mut := Induction for pyval_list Sort Prop.

(* ===================================================================== *)
(* 2. (b) Well-foundedness: `size v >= 1` (the WhyML `size_pos`) + its     *)
(*    companion `list_size l >= 0`, by MUTUAL structural induction.        *)
(* ===================================================================== *)

Theorem size_pos : forall v : pyval, size v >= 1.
Proof.
  apply (pyval_mut (fun v => size v >= 1) (fun l => list_size l >= 0));
    intros; cbn [size list_size] in *; lia.
Qed.

Theorem list_size_nonneg : forall l : pyval_list, list_size l >= 0.
Proof.
  apply (pyval_list_mut (fun v => size v >= 1) (fun l => list_size l >= 0));
    intros; cbn [size list_size] in *; lia.
Qed.

(* size is EXACT on each constructor (the measure is honest, not degenerate). *)
Theorem size_pstr  : forall s, size (PStr s) = 1.
Proof. reflexivity. Qed.
Theorem size_pint  : forall n, size (PInt n) = 1.
Proof. reflexivity. Qed.
Theorem size_pmap  : forall m, size (PMap m) = 1.
Proof. reflexivity. Qed.
Theorem size_parr  : forall l, size (PArr l) = 1 + list_size l.
Proof. reflexivity. Qed.
Theorem size_pnode : forall n, size (PNode n) = 1 + size n.
Proof. reflexivity. Qed.

Theorem list_size_nil  : list_size PNil = 0.
Proof. reflexivity. Qed.
Theorem list_size_cons : forall h t, list_size (PCons h t) = size h + list_size t.
Proof. reflexivity. Qed.

(* The TAIL of a cons is STRICTLY shorter — the termination witness for any
   structural fold over `pyval_list` (the WhyML has no `variant` clause because
   Why3 infers exactly this descent). *)
Theorem list_tail_size_lt : forall h t, list_size t < list_size (PCons h t).
Proof. intros h t; cbn [list_size]; pose proof (size_pos h); lia. Qed.

(* A non-empty list is DISTINCT from the empty one (a captured list is
   OBSERVABLE, not PNil-erased). *)
Theorem list_empty_neq_cons : forall h t, PNil <> PCons h t.
Proof. intros h t C; discriminate. Qed.

(* ===================================================================== *)
(* 3. (c) Value carriers are OBSERVABLE + DISTINCT — the no-more-int       *)
(*    faithfulness: a string stays a string, never erased to an int.       *)
(* ===================================================================== *)

Theorem pstr_inj : forall a b, PStr a = PStr b -> a = b.
Proof. intros a b H; inversion H; reflexivity. Qed.
Theorem pstr_neq : forall a b, a <> b -> PStr a <> PStr b.
Proof. intros a b H C; inversion C; contradiction. Qed.
Theorem pint_inj : forall a b, PInt a = PInt b -> a = b.
Proof. intros a b H; inversion H; reflexivity. Qed.

(* THE make-or-break distinctness: a PStr value is NEVER a PInt value — the
   string is not int-hashed / int-erased (the whole point of the model). *)
Theorem pstr_neq_pint  : forall s n, PStr s <> PInt n.
Proof. intros s n C; discriminate. Qed.
Theorem pstr_neq_parr  : forall s l, PStr s <> PArr l.
Proof. intros s l C; discriminate. Qed.
Theorem parr_neq_pnode : forall l v, PArr l <> PNode v.
Proof. intros l v C; discriminate. Qed.
(* PArr carries the captured list observably (distinct lists → distinct values). *)
Theorem parr_inj : forall a b, PArr a = PArr b -> a = b.
Proof. intros a b H; inversion H; reflexivity. Qed.

(* ===================================================================== *)
(* 4. (d) The heterogeneous DICT read is faithful — the make-or-break.     *)
(*    Model the WhyML `map string (option pyval)` (= `string -> option v`) *)
(*    with `Map.get` / `Map.set`.  Pointwise laws — NO functional           *)
(*    extensionality, so still axiom-free.                                  *)
(* ===================================================================== *)

Definition pmap := string -> option pyval.
Definition empty_map : pmap := fun _ => None.
Definition map_get (m : pmap) (k : string) : option pyval := m k.
Definition map_set (m : pmap) (k : string) (v : option pyval) : pmap :=
  fun k' => if string_dec k k' then v else m k'.

Theorem read_same_key : forall m k v, map_get (map_set m k v) k = v.
Proof.
  intros m k v; unfold map_get, map_set;
  destruct (string_dec k k) as [_|N]; [reflexivity | now contradiction N].
Qed.

Theorem read_other_key : forall m k k' v,
  k <> k' -> map_get (map_set m k v) k' = map_get m k'.
Proof.
  intros m k k' v H; unfold map_get, map_set;
  destruct (string_dec k k') as [E|_]; [contradiction | reflexivity].
Qed.

(* The oracle's `read_variable_faithful`: build the
   {"pattern": "Constructor", "ctor": arm_ctor, "captures": ["x"]} dict and read
   "ctor" — the string VARIABLE arm_ctor projects back FAITHFULLY as
   `Some (PStr arm_ctor)`, with NO int-erasure. *)
Definition build (arm_ctor : string) : pmap :=
  map_set
    (map_set
      (map_set empty_map "pattern" (Some (PStr "Constructor")))
                         "ctor"    (Some (PStr arm_ctor)))
                         "captures" (Some (PArr (PCons (PStr "x") PNil))).

Theorem read_variable_faithful : forall arm_ctor : string,
  map_get (build arm_ctor) "ctor" = Some (PStr arm_ctor).
Proof.
  intros arm_ctor; unfold build, map_get, map_set, empty_map.
  destruct (string_dec "captures" "ctor") as [E|_]; [discriminate E|].
  destruct (string_dec "ctor" "ctor") as [_|N]; [reflexivity | now contradiction N].
Qed.

Theorem read_literal_faithful : forall arm_ctor : string,
  map_get (build arm_ctor) "pattern" = Some (PStr "Constructor").
Proof.
  intros arm_ctor; unfold build, map_get, map_set, empty_map.
  destruct (string_dec "captures" "pattern") as [E|_]; [discriminate E|].
  destruct (string_dec "ctor" "pattern") as [E|_]; [discriminate E|].
  destruct (string_dec "pattern" "pattern") as [_|N]; [reflexivity | now contradiction N].
Qed.

Theorem read_list_faithful : forall arm_ctor : string,
  map_get (build arm_ctor) "captures" = Some (PArr (PCons (PStr "x") PNil)).
Proof.
  intros arm_ctor; unfold build, map_get, map_set, empty_map.
  destruct (string_dec "captures" "captures") as [_|N]; [reflexivity | now contradiction N].
Qed.

(* EVIL TWIN (non-vacuity): a WRONG value read is provably UNprovable — when
   arm_ctor <> "wrong", the "ctor" read is NOT `Some (PStr "wrong")`.  This is
   what makes the model non-vacuous (an int-erased / empty-map lowering would let
   this false theorem through). *)
Theorem read_evil_wrong_value : forall arm_ctor : string,
  arm_ctor <> "wrong" ->
  map_get (build arm_ctor) "ctor" <> Some (PStr "wrong").
Proof.
  intros arm_ctor H C.
  rewrite read_variable_faithful in C.
  apply H. apply pstr_inj. inversion C. reflexivity.
Qed.

(* EVIL TWIN (empty-map refute): the missing-key sentinel is `None`, so a claim
   that a set key reads `None` is UNprovable (the old drop-bug's false theorem). *)
Theorem read_evil_empty : forall arm_ctor : string,
  map_get (build arm_ctor) "ctor" <> None.
Proof.
  intros arm_ctor C; rewrite read_variable_faithful in C; discriminate C.
Qed.

End PyVal.

(* ===================================================================== *)
(* 5. VERDICT — assumption audit.  Every result must be `Closed under the  *)
(*    global context` (NO axiom): the 3-axiom trust ledger is intact.      *)
(* ===================================================================== *)

Print Assumptions size_pos.
Print Assumptions list_size_nonneg.
Print Assumptions size_pstr.
Print Assumptions size_pint.
Print Assumptions size_pmap.
Print Assumptions size_parr.
Print Assumptions size_pnode.
Print Assumptions list_size_nil.
Print Assumptions list_size_cons.
Print Assumptions list_tail_size_lt.
Print Assumptions list_empty_neq_cons.
Print Assumptions pstr_inj.
Print Assumptions pstr_neq.
Print Assumptions pint_inj.
Print Assumptions pstr_neq_pint.
Print Assumptions pstr_neq_parr.
Print Assumptions parr_neq_pnode.
Print Assumptions parr_inj.
Print Assumptions read_same_key.
Print Assumptions read_other_key.
Print Assumptions read_variable_faithful.
Print Assumptions read_literal_faithful.
Print Assumptions read_list_faithful.
Print Assumptions read_evil_wrong_value.
Print Assumptions read_evil_empty.
