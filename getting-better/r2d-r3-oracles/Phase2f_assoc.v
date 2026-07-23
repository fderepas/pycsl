(* R3 §6a spike: does the assoc-LIST HMap carrier re-certify the hval soundness core
   AXIOM-FREE? Standalone (stdlib only). If Print Assumptions is empty, §6a PASSES. *)
Require Import ZArith String List Bool Lia.
Local Open Scope Z_scope.

(* hval with the assoc-list HMap carrier (was `string -> option hval`, an infinite map). *)
Inductive hval : Type :=
  | HStr  (s : string)
  | HInt  (n : Z)
  | HArr  (l : hval_list)
  | HMap  (p : hpairs)          (* CHANGED: assoc-list, not a map *)
  | HNode (v : hval)
with hval_list : Type :=
  | HNil
  | HCons (h : hval) (t : hval_list)
with hpairs : Type :=            (* NEW third mutually-recursive type *)
  | PNil
  | PCons (k : string) (v : hval) (t : hpairs).

(* size now DESCENDS into the map's pairs -> HMap is no longer flat weight-1. *)
Fixpoint size (v : hval) : Z :=
  match v with
  | HStr _  => 1 | HInt _ => 1
  | HArr l  => 1 + list_size l
  | HMap p  => 1 + pairs_size p          (* CHANGED: was `=> 1` *)
  | HNode n => 1 + size n
  end
with list_size (l : hval_list) : Z :=
  match l with HNil => 0 | HCons h t => size h + list_size t end
with pairs_size (p : hpairs) : Z :=      (* NEW *)
  match p with PNil => 0 | PCons _ v t => size v + pairs_size t end.

Scheme hval_mut  := Induction for hval Sort Prop
with   list_mut  := Induction for hval_list Sort Prop
with   pairs_mut := Induction for hpairs Sort Prop.

(* Well-foundedness by MUTUAL structural induction over all THREE types. *)
Theorem size_pos : forall v, size v >= 1.
Proof.
  apply (hval_mut (fun v => size v >= 1) (fun l => list_size l >= 0)
                  (fun p => pairs_size p >= 0));
    intros; cbn [size list_size pairs_size] in *; lia.
Qed.

Theorem list_size_nonneg : forall l, list_size l >= 0.
Proof.
  apply (list_mut (fun v => size v >= 1) (fun l => list_size l >= 0)
                  (fun p => pairs_size p >= 0));
    intros; cbn [size list_size pairs_size] in *; lia.
Qed.

Theorem pairs_size_nonneg : forall p, pairs_size p >= 0.
Proof.
  apply (pairs_mut (fun v => size v >= 1) (fun l => list_size l >= 0)
                   (fun p => pairs_size p >= 0));
    intros; cbn [size list_size pairs_size] in *; lia.
Qed.

(* size EXACT on the new HMap ctor — the measure descends, honestly. *)
Theorem size_pmap : forall p, size (HMap p) = 1 + pairs_size p.
Proof. reflexivity. Qed.

(* Fold-termination witnesses: the tail of a cons is STRICTLY shorter, in BOTH
   the list carrier AND the new pairs carrier — so `.values()` folds terminate. *)
Theorem list_tail_lt : forall h t, list_size t < list_size (HCons h t).
Proof. intros h t; cbn [list_size]; pose proof (size_pos h); lia. Qed.
Theorem pairs_tail_lt : forall k v t, pairs_size t < pairs_size (PCons k v t).
Proof. intros k v t; cbn [pairs_size]; pose proof (size_pos v); lia. Qed.

(* Observability/distinctness carries over unchanged. *)
Theorem pstr_inj : forall a b, HStr a = HStr b -> a = b.
Proof. intros a b H; injection H; auto. Qed.
Theorem pairs_empty_neq_cons : forall k v t, PNil <> PCons k v t.
Proof. intros; discriminate. Qed.

(* THE TRUST CHECK. *)
Print Assumptions size_pos.
Print Assumptions list_size_nonneg.
Print Assumptions pairs_size_nonneg.
Print Assumptions pairs_tail_lt.
