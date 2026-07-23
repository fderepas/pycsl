(* Phase2f_PyVal.v — axiom-free certificate for the `hval` heterogeneous value
   model (self-tcb-reduction, Tier-5 value-model wall).

   R3 CARRIER SWAP: the `HMap` arm's carrier is now an association LIST
   (`hpairs = PNil | PCons key hval hpairs`), NOT a Why3 `map string (option
   hval)`.  The map carrier was non-iterable, so `.values()` over a heterogeneous
   `Dict[str, Any]` could not fold; the assoc-list carrier makes `.values()` a
   terminating STRUCTURAL fold (its measure `size (HMap p) = 1 + pairs_size p`
   DESCENDS into the pairs).  This is what de-vacuifies the IRScanner predicates.

   CO-LANDING COUPLING (the tier-3 rule, cf. Phase2c_PyConstVal.v /
   Phase2d_StmtIR.v / Phase2e_PyAstStmt.v): the WhyML `hval` theory promoted into
   the emitter preamble (`module6_whyml/preamble.py::_emit_pyval_theory`, gated on
   `_uses_pyval`) is a NEW value shape — the faithful carrier for a heterogeneous
   Python `Dict[str, Any]` (HStr / HInt / HArr / HMap / HNode) — so it lands with a
   proof, not a trusted assumption.  The build (`_build_dict_literal_map` hval
   branch) tags each dict value into its `hval` constructor and prepends it to the
   `hpairs` assoc list; the read (`_dv_missing_default` / the `pairs_get` lookup
   fold) projects it back; this file certifies, against pure inductive datatypes
   with NO axiom, exactly what the emitter relies on:

     (a) `hval` is a well-formed MUTUAL inductive over THREE types: `HArr` recurses
         through the BESPOKE `hval_list` (HNil / HCons) and `HMap` through the
         BESPOKE `hpairs` (PNil / PCons) — NOT `seq`/`map`, the strictly-positive
         shape Why3 accepts (the `seq hval` recursion is Why3-rejected; the assoc
         list keeps the recursion structural).  No `variant` clause — the mutual
         structural recursion is inferred;
     (b) the LOAD-BEARING measure `size` / `list_size` / `pairs_size` (the WhyML
         cert-side measure) is well-founded: `size v >= 1` (the WhyML `size_pos`
         lemma that SMT alone cannot discharge — it needs MUTUAL structural
         induction over all three types; here it is proven), `list_size l >= 0`,
         `pairs_size p >= 0`, and the tail of a cons is STRICTLY shorter in BOTH
         the list carrier AND the new pairs carrier — so any `.values()` fold over
         `hpairs` terminates (no infinite descent);
     (c) the value carriers are OBSERVABLE and DISTINCT — `HStr` is injective, and a
         string value is NEVER erased to an int (`HStr s <> HInt n`): the
         no-more-int faithfulness the whole value model exists to protect;
     (d) the make-or-break heterogeneous DICT read is faithful: over the assoc-list
         carrier `hpairs`, the `pairs_get` lookup fold reads a key's value back
         FAITHFULLY (`read_same_key` / `read_variable_faithful`), a distinct key is
         untouched (`read_other_key`), and the EVIL TWIN — a WRONG value read — is
         provably UNprovable (non-vacuity).

   `hval` has NO decidable equality (an honest boundary; the emitter never needs
   it — reads are `pairs_get` key-projections, compared by Leibniz `=` in the WhyML
   goals — so it is deliberately not claimed).  `size` / `size_pos` are CERT-ONLY
   (no frontier fold needs them; they are NOT emitted into any VC).

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
(*      type hval = HStr string | HInt int | HArr hval_list             *)
(*                 | HMap hpairs | HNode hval                            *)
(*      with hval_list = HNil | HCons hval hval_list                    *)
(*      with hpairs    = PNil | PCons string hval hpairs.               *)
(* ===================================================================== *)

Inductive hval : Type :=
  | HStr  (s : string)
  | HInt  (n : Z)
  | HArr  (l : hval_list)
  | HMap  (p : hpairs)          (* R3: assoc-list carrier, not a map *)
  | HNode (v : hval)
with hval_list : Type :=
  | HNil
  | HCons (h : hval) (t : hval_list)
with hpairs : Type :=            (* R3: the NEW third mutually-recursive type *)
  | PNil
  | PCons (k : string) (v : hval) (t : hpairs).

(* size / list_size / pairs_size — verbatim image of the WhyML cert-side measure
   (mutually recursive, NO variant clause).  The measure now DESCENDS into the
   map's pairs — `HMap` is no longer flat weight-1 — which is exactly what makes
   `.values()` a terminating fold. *)
Fixpoint size (v : hval) : Z :=
  match v with
  | HStr _  => 1
  | HInt _  => 1
  | HArr l  => 1 + list_size l
  | HMap p  => 1 + pairs_size p         (* R3: was `=> 1`, flat *)
  | HNode n => 1 + size n
  end
with list_size (l : hval_list) : Z :=
  match l with
  | HNil      => 0
  | HCons h t => size h + list_size t
  end
with pairs_size (p : hpairs) : Z :=     (* R3: NEW *)
  match p with
  | PNil        => 0
  | PCons _ v t => size v + pairs_size t
  end.

(* The MUTUAL induction principle over all THREE types (Coq's auto-generated
   `hval_ind` is weak / non-mutual — this is the analogue of Why3's
   `induction_ty_lex`). *)
Scheme pyval_mut := Induction for hval Sort Prop
with pyval_list_mut := Induction for hval_list Sort Prop
with pyval_pairs_mut := Induction for hpairs Sort Prop.

(* ===================================================================== *)
(* 2. (b) Well-foundedness: `size v >= 1` (the WhyML `size_pos`) + its     *)
(*    companions `list_size l >= 0` and `pairs_size p >= 0`, by MUTUAL     *)
(*    structural induction over all three carriers.                        *)
(* ===================================================================== *)

Theorem size_pos : forall v : hval, size v >= 1.
Proof.
  apply (pyval_mut (fun v => size v >= 1) (fun l => list_size l >= 0)
                   (fun p => pairs_size p >= 0));
    intros; cbn [size list_size pairs_size] in *; lia.
Qed.

Theorem list_size_nonneg : forall l : hval_list, list_size l >= 0.
Proof.
  apply (pyval_list_mut (fun v => size v >= 1) (fun l => list_size l >= 0)
                        (fun p => pairs_size p >= 0));
    intros; cbn [size list_size pairs_size] in *; lia.
Qed.

Theorem pairs_size_nonneg : forall p : hpairs, pairs_size p >= 0.
Proof.
  apply (pyval_pairs_mut (fun v => size v >= 1) (fun l => list_size l >= 0)
                         (fun p => pairs_size p >= 0));
    intros; cbn [size list_size pairs_size] in *; lia.
Qed.

(* size is EXACT on each constructor (the measure is honest, not degenerate). *)
Theorem size_pstr  : forall s, size (HStr s) = 1.
Proof. reflexivity. Qed.
Theorem size_pint  : forall n, size (HInt n) = 1.
Proof. reflexivity. Qed.
Theorem size_pmap  : forall p, size (HMap p) = 1 + pairs_size p.  (* R3: descends *)
Proof. reflexivity. Qed.
Theorem size_parr  : forall l, size (HArr l) = 1 + list_size l.
Proof. reflexivity. Qed.
Theorem size_pnode : forall n, size (HNode n) = 1 + size n.
Proof. reflexivity. Qed.

Theorem list_size_nil  : list_size HNil = 0.
Proof. reflexivity. Qed.
Theorem list_size_cons : forall h t, list_size (HCons h t) = size h + list_size t.
Proof. reflexivity. Qed.
Theorem pairs_size_nil  : pairs_size PNil = 0.
Proof. reflexivity. Qed.
Theorem pairs_size_cons : forall k v t,
  pairs_size (PCons k v t) = size v + pairs_size t.
Proof. reflexivity. Qed.

(* The TAIL of a cons is STRICTLY shorter — the termination witness for any
   structural fold, in BOTH the list carrier AND the new pairs carrier (the WhyML
   has no `variant` clause because Why3 infers exactly this descent).  The pairs
   witness is what makes `.values()` fold over a dict terminate. *)
Theorem list_tail_size_lt : forall h t, list_size t < list_size (HCons h t).
Proof. intros h t; cbn [list_size]; pose proof (size_pos h); lia. Qed.
Theorem pairs_tail_size_lt : forall k v t, pairs_size t < pairs_size (PCons k v t).
Proof. intros k v t; cbn [pairs_size]; pose proof (size_pos v); lia. Qed.

(* A non-empty carrier is DISTINCT from the empty one (a captured list / pairs is
   OBSERVABLE, not HNil/PNil-erased). *)
Theorem list_empty_neq_cons : forall h t, HNil <> HCons h t.
Proof. intros h t C; discriminate. Qed.
Theorem pairs_empty_neq_cons : forall k v t, PNil <> PCons k v t.
Proof. intros k v t C; discriminate. Qed.

(* ===================================================================== *)
(* 3. (c) Value carriers are OBSERVABLE + DISTINCT — the no-more-int       *)
(*    faithfulness: a string stays a string, never erased to an int.       *)
(* ===================================================================== *)

Theorem pstr_inj : forall a b, HStr a = HStr b -> a = b.
Proof. intros a b H; inversion H; reflexivity. Qed.
Theorem pstr_neq : forall a b, a <> b -> HStr a <> HStr b.
Proof. intros a b H C; inversion C; contradiction. Qed.
Theorem pint_inj : forall a b, HInt a = HInt b -> a = b.
Proof. intros a b H; inversion H; reflexivity. Qed.

(* THE make-or-break distinctness: a HStr value is NEVER a HInt value — the
   string is not int-hashed / int-erased (the whole point of the model). *)
Theorem pstr_neq_pint  : forall s n, HStr s <> HInt n.
Proof. intros s n C; discriminate. Qed.
Theorem pstr_neq_parr  : forall s l, HStr s <> HArr l.
Proof. intros s l C; discriminate. Qed.
Theorem parr_neq_pnode : forall l v, HArr l <> HNode v.
Proof. intros l v C; discriminate. Qed.
(* HArr carries the captured list observably (distinct lists → distinct values). *)
Theorem parr_inj : forall a b, HArr a = HArr b -> a = b.
Proof. intros a b H; inversion H; reflexivity. Qed.
(* HMap carries the captured pairs observably (distinct pairs → distinct values). *)
Theorem pmap_inj : forall a b, HMap a = HMap b -> a = b.
Proof. intros a b H; inversion H; reflexivity. Qed.

(* ===================================================================== *)
(* 4. (d) The heterogeneous DICT read is faithful — the make-or-break.     *)
(*    R3: over the assoc-list carrier `hpairs`, the read is the `pairs_get` *)
(*    lookup FOLD (terminating by `pairs_tail_size_lt`), the WhyML analogue *)
(*    of what the emitter emits.  Pointwise laws — NO functional             *)
(*    extensionality, so still axiom-free.  `pairs_set` PREPENDS a binding    *)
(*    (`PCons`), exactly as `_build_dict_literal_map` builds the assoc list.  *)
(* ===================================================================== *)

Fixpoint pairs_get (p : hpairs) (k : string) : option hval :=
  match p with
  | PNil        => None
  | PCons k' v t => if string_dec k k' then Some v else pairs_get t k
  end.

Definition pairs_set (p : hpairs) (k : string) (v : hval) : hpairs := PCons k v p.

Theorem read_same_key : forall p k v, pairs_get (pairs_set p k v) k = Some v.
Proof.
  intros p k v; cbn [pairs_get pairs_set];
  destruct (string_dec k k) as [_|N]; [reflexivity | now contradiction N].
Qed.

Theorem read_other_key : forall p k k' v,
  k' <> k -> pairs_get (pairs_set p k v) k' = pairs_get p k'.
Proof.
  intros p k k' v H; cbn [pairs_get pairs_set];
  destruct (string_dec k' k) as [E|_]; [now contradiction H | reflexivity].
Qed.

(* The oracle's `read_variable_faithful`: build the
   {"pattern": "Constructor", "ctor": arm_ctor, "captures": ["x"]} dict as an
   assoc list and read "ctor" — the string VARIABLE arm_ctor projects back
   FAITHFULLY as `Some (HStr arm_ctor)`, with NO int-erasure. *)
Definition build (arm_ctor : string) : hpairs :=
  PCons "pattern"  (HStr "Constructor")
  (PCons "ctor"    (HStr arm_ctor)
  (PCons "captures" (HArr (HCons (HStr "x") HNil))
  PNil)).

Theorem read_variable_faithful : forall arm_ctor : string,
  pairs_get (build arm_ctor) "ctor" = Some (HStr arm_ctor).
Proof.
  intros arm_ctor; cbn [pairs_get build].
  destruct (string_dec "ctor" "pattern") as [E|_]; [discriminate E|].
  destruct (string_dec "ctor" "ctor") as [_|N]; [reflexivity | now contradiction N].
Qed.

Theorem read_literal_faithful : forall arm_ctor : string,
  pairs_get (build arm_ctor) "pattern" = Some (HStr "Constructor").
Proof.
  intros arm_ctor; cbn [pairs_get build].
  destruct (string_dec "pattern" "pattern") as [_|N]; [reflexivity | now contradiction N].
Qed.

Theorem read_list_faithful : forall arm_ctor : string,
  pairs_get (build arm_ctor) "captures" = Some (HArr (HCons (HStr "x") HNil)).
Proof.
  intros arm_ctor; cbn [pairs_get build].
  destruct (string_dec "captures" "pattern") as [E|_]; [discriminate E|].
  destruct (string_dec "captures" "ctor") as [E|_]; [discriminate E|].
  destruct (string_dec "captures" "captures") as [_|N]; [reflexivity | now contradiction N].
Qed.

(* EVIL TWIN (non-vacuity): a WRONG value read is provably UNprovable — when
   arm_ctor <> "wrong", the "ctor" read is NOT `Some (HStr "wrong")`.  This is
   what makes the model non-vacuous (an int-erased / empty-list lowering would let
   this false theorem through). *)
Theorem read_evil_wrong_value : forall arm_ctor : string,
  arm_ctor <> "wrong" ->
  pairs_get (build arm_ctor) "ctor" <> Some (HStr "wrong").
Proof.
  intros arm_ctor H C.
  rewrite read_variable_faithful in C.
  apply H. apply pstr_inj. inversion C. reflexivity.
Qed.

(* EVIL TWIN (empty-list refute): the missing-key sentinel is `None`, so a claim
   that a bound key reads `None` is UNprovable (the old drop-bug's false theorem). *)
Theorem read_evil_empty : forall arm_ctor : string,
  pairs_get (build arm_ctor) "ctor" <> None.
Proof.
  intros arm_ctor C; rewrite read_variable_faithful in C; discriminate C.
Qed.

(* An absent key reads `None` from the empty assoc list (the missing-key
   sentinel is honest, not a fabricated value). *)
Theorem read_missing_none : forall k, pairs_get PNil k = None.
Proof. reflexivity. Qed.

End PyVal.

(* ===================================================================== *)
(* 5. VERDICT — assumption audit.  Every result must be `Closed under the  *)
(*    global context` (NO axiom): the 3-axiom trust ledger is intact.      *)
(* ===================================================================== *)

Print Assumptions size_pos.
Print Assumptions list_size_nonneg.
Print Assumptions pairs_size_nonneg.
Print Assumptions size_pstr.
Print Assumptions size_pint.
Print Assumptions size_pmap.
Print Assumptions size_parr.
Print Assumptions size_pnode.
Print Assumptions list_size_nil.
Print Assumptions list_size_cons.
Print Assumptions pairs_size_nil.
Print Assumptions pairs_size_cons.
Print Assumptions list_tail_size_lt.
Print Assumptions pairs_tail_size_lt.
Print Assumptions list_empty_neq_cons.
Print Assumptions pairs_empty_neq_cons.
Print Assumptions pstr_inj.
Print Assumptions pstr_neq.
Print Assumptions pint_inj.
Print Assumptions pstr_neq_pint.
Print Assumptions pstr_neq_parr.
Print Assumptions parr_neq_pnode.
Print Assumptions parr_inj.
Print Assumptions pmap_inj.
Print Assumptions read_same_key.
Print Assumptions read_other_key.
Print Assumptions read_variable_faithful.
Print Assumptions read_literal_faithful.
Print Assumptions read_list_faithful.
Print Assumptions read_evil_wrong_value.
Print Assumptions read_evil_empty.
Print Assumptions read_missing_none.
