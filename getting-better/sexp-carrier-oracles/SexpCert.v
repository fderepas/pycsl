(* Coupling-rule spike (§10.5): does the sexp value carrier certify AXIOM-FREE? *)
Require Import ZArith String List Lia.
Local Open Scope Z_scope.

Inductive sexp : Type := SAtom (a:string) | SList (l:slist)
with slist : Type := SNil | SCons (h:sexp) (t:slist).

Fixpoint ssize (s:sexp) : Z := match s with SAtom _ => 1 | SList l => 1 + lsize l end
with lsize (l:slist) : Z := match l with SNil => 0 | SCons h t => ssize h + lsize t end.

Scheme sexp_mut := Induction for sexp Sort Prop
with   slist_mut := Induction for slist Sort Prop.

(* well-foundedness: the measure descends, so every walk/fold over sexp terminates *)
Theorem ssize_pos : forall s, ssize s >= 1.
Proof. apply (sexp_mut (fun s => ssize s >= 1) (fun l => lsize l >= 0));
  intros; cbn [ssize lsize] in *; lia. Qed.
Theorem lsize_nonneg : forall l, lsize l >= 0.
Proof. apply (slist_mut (fun s => ssize s >= 1) (fun l => lsize l >= 0));
  intros; cbn [ssize lsize] in *; lia. Qed.
(* fold-termination witness: a cons tail is strictly shorter *)
Theorem tail_lt : forall h t, lsize t < lsize (SCons h t).
Proof. intros h t; cbn [lsize]; pose proof (ssize_pos h); lia. Qed.
(* observability: atoms are distinct/injective (a string stays a string) *)
Theorem satom_inj : forall a b, SAtom a = SAtom b -> a = b.
Proof. intros a b H; injection H; auto. Qed.
Theorem atom_neq_list : forall a l, SAtom a <> SList l.
Proof. intros a l H; discriminate. Qed.

Print Assumptions ssize_pos.
Print Assumptions lsize_nonneg.
Print Assumptions tail_lt.
