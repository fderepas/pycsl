(* Phase2h_TParam.v — axiom-free certificate for the `tparam` INPUT-side
   PEP-695 type-parameter value shape (self-tcb-reduction, collector-family
   unlock; L1).

   CO-LANDING COUPLING (the tier-3 / lesson-#5 rule, cf. Phase2e_PyAstStmt.v /
   Phase2g_CallKw.v): the WhyML `tparam` theory promoted into the emitter
   preamble (`module6_whyml/preamble.py`, gated on `_uses_tparam`) is a NEW
   value shape — the raw PEP-695 `ast.TypeVar`/`ast.ParamSpec`/`ast.TypeVarTuple`
   node union that `_collect_type_params` reflects over (`type(tp).__name__`,
   `getattr(tp,"name")`, `getattr(tp,"bound")` + the bound isinstance) — so it
   lands with a proof, not a trusted assumption.  This file certifies, against
   pure inductive datatypes with NO axiom, exactly what the emitter relies on:

     (a) `tparam` is a well-formed inductive carrying the FOREIGN emit_ir
         bound-child type (`TPTypeVar`'s bound is `emit`, which never mentions
         `tparam` — no mutual recursion), with DECIDABLE equality given
         decidable equality on `emit`;
     (b) `tp_kind_of` — the image of `type(tp).__name__` — is EXACT on every
         constructor, and the kind tags are pairwise DISTINCT (TypeVar /
         ParamSpec / TypeVarTuple are provably separate node identities);
     (c) the LOAD-BEARING faithfulness laws — the WhyML `is_K_faithful`
         lemmas — hold: `is_K tp = true <-> tp_kind_of tp = "K"` for K in
         {typevar, paramspec, typevartuple}.  These discharge in the WhyML
         whole-file proof; certified here they model the type-name reflection
         faithfully (a ParamSpec is NEVER read back as a TypeVar);
     (d) the projectors `tp_name` (: tparam -> string, the image of
         `getattr(tp,"name")`) and `tp_bound` (: tparam -> emit, the image of
         `getattr(tp,"bound")`) are EXACT on the constructor slots they read,
         with the SAME off-variant default as the WhyML (`IrOther ""` modelled
         by the abstract witness `emit0`) — and each carried field is OBSERVABLE
         (non-vacuity: never a shared 0 / int-erasure);
     (e) the type-parameter list `tparam_list = TPNil | TPCons tparam
         tparam_list` (the bespoke cons-list `type_params_of` yields, the
         `.type_params` loop iterates) has a WELL-FOUNDED length measure
         `tpl_len` and a TOTAL indexer `tpl_nth`: the tail is STRICTLY shorter
         than the cons, so the WhyML `tpl_nth`'s `variant { l }` structural
         recursion (equivalently the `tpl_len`-bounded loop) is certified to
         terminate — no infinite descent.

   The abstract WhyML `val function type_params_of` is NOT a `tparam` soundness
   obligation (an opaque reader, the `class_body_ast` precedent — no per-value
   law), modelled here by a Section variable, TOTAL by typing, exactly as the
   WhyML leaves it.  The bound sub-node's isinstance/`.id`/`.attr` dispatch
   reuses the EXISTING emit_ir `is_var`/`is_attribute`/`name_of` (certified in
   the emit_ir theory), so `tp_bound` need only be certified as an EXACT
   projector to `emit`.

   The `Print Assumptions` block at the bottom is the trust check: every result
   must be `Closed under the global context` (NO axiom) so the 3-axiom trust
   ledger (`proof_axiom_allowlist.py`) stays intact.  Nothing here is Admitted.
   Build: part of `make` (listed in `_CoqProject` after `Phase2g_CallKw.v`). *)

Require Import ZArith String List Bool Lia.
Import ListNotations.
Open Scope string_scope.

Section TParam.

(* The WhyML emit_ir bound-child type, abstracted (see header (a)): kept a
   Section variable so `tparam` provably carries a FOREIGN child — there is no
   `tparam` occurrence inside `emit`, hence no mutual recursion.  `emit0`
   witnesses the WhyML projector's off-variant default `IrOther ""`. *)
Variable emit : Type.
Variable emit0 : emit.
Variable emit_eq_dec : forall a b : emit, {a = b} + {a <> b}.

(* ===================================================================== *)
(* 1. The PEP-695 type-param ADT — mirrors the WhyML `type tparam`.        *)
(*    TPTypeVar carries (name, bound-node); ParamSpec/TypeVarTuple are      *)
(*    bound-less — exactly the WhyML `TPTypeVar string emit_ir |            *)
(*    TPParamSpec string | TPTypeVarTuple string`.                         *)
(* ===================================================================== *)

Inductive tparam : Type :=
  | TPTypeVar (name : string) (bound : emit)
  | TPParamSpec (name : string)
  | TPTypeVarTuple (name : string).

(* The kind discriminant — verbatim image of the WhyML `tp_kind_of`, the image
   of the Python `type(tp).__name__` reflection. *)
Definition tp_kind_of (tp : tparam) : string :=
  match tp with
  | TPTypeVar _ _    => "TypeVar"
  | TPParamSpec _    => "ParamSpec"
  | TPTypeVarTuple _ => "TypeVarTuple"
  end.

(* The isinstance/kind discriminants — verbatim images of the WhyML `is_K`
   predicates (WhyML `predicate` -> Coq bool). *)
Definition is_typevar (tp : tparam) : bool :=
  match tp with TPTypeVar _ _ => true | _ => false end.
Definition is_paramspec (tp : tparam) : bool :=
  match tp with TPParamSpec _ => true | _ => false end.
Definition is_typevartuple (tp : tparam) : bool :=
  match tp with TPTypeVarTuple _ => true | _ => false end.

(* The projectors — verbatim images of the WhyML `tp_name` (: string) and
   `tp_bound` (: emit_ir, with off-variant default `IrOther ""` = emit0). *)
Definition tp_name (tp : tparam) : string :=
  match tp with
  | TPTypeVar n _    => n
  | TPParamSpec n    => n
  | TPTypeVarTuple n => n
  end.
Definition tp_bound (tp : tparam) : emit :=
  match tp with
  | TPTypeVar _ b => b
  | _             => emit0
  end.

(* Decidable equality on `tparam`, given decidable equality on the foreign
   child `emit` — the well-formed-ADT obligation. *)
Definition tparam_eq_dec : forall x y : tparam, {x = y} + {x <> y}.
Proof. decide equality; (apply emit_eq_dec || apply string_dec). Defined.

(* ===================================================================== *)
(* 2. (b) `tp_kind_of` is EXACT per ctor, and the kind tags DISTINCT.      *)
(* ===================================================================== *)

Theorem kind_of_typevar : forall n b, tp_kind_of (TPTypeVar n b) = "TypeVar".
Proof. reflexivity. Qed.
Theorem kind_of_paramspec : forall n, tp_kind_of (TPParamSpec n) = "ParamSpec".
Proof. reflexivity. Qed.
Theorem kind_of_typevartuple : forall n, tp_kind_of (TPTypeVarTuple n) = "TypeVarTuple".
Proof. reflexivity. Qed.

(* The three kind tags are pairwise DISTINCT — the honest node identity: a
   TypeVar is never confused with a ParamSpec / TypeVarTuple node. *)
Theorem tag_typevar_neq_paramspec : forall n b m,
  tp_kind_of (TPTypeVar n b) <> tp_kind_of (TPParamSpec m).
Proof. intros; simpl; discriminate. Qed.
Theorem tag_typevar_neq_typevartuple : forall n b m,
  tp_kind_of (TPTypeVar n b) <> tp_kind_of (TPTypeVarTuple m).
Proof. intros; simpl; discriminate. Qed.
Theorem tag_paramspec_neq_typevartuple : forall n m,
  tp_kind_of (TPParamSpec n) <> tp_kind_of (TPTypeVarTuple m).
Proof. intros; simpl; discriminate. Qed.

(* The constructors themselves are distinct (no erasure to a common value). *)
Theorem ctor_typevar_neq_paramspec : forall n b m, TPTypeVar n b <> TPParamSpec m.
Proof. intros; discriminate. Qed.

(* ===================================================================== *)
(* 3. (c) The LOAD-BEARING faithfulness laws — the WhyML `is_K_faithful`.  *)
(*    `is_K tp = true <-> tp_kind_of tp = "K"`.                            *)
(* ===================================================================== *)

Theorem is_typevar_faithful : forall tp,
  is_typevar tp = true <-> tp_kind_of tp = "TypeVar".
Proof. intros tp; destruct tp; simpl; split; intro H; solve [reflexivity | discriminate]. Qed.

Theorem is_paramspec_faithful : forall tp,
  is_paramspec tp = true <-> tp_kind_of tp = "ParamSpec".
Proof. intros tp; destruct tp; simpl; split; intro H; solve [reflexivity | discriminate]. Qed.

Theorem is_typevartuple_faithful : forall tp,
  is_typevartuple tp = true <-> tp_kind_of tp = "TypeVarTuple".
Proof. intros tp; destruct tp; simpl; split; intro H; solve [reflexivity | discriminate]. Qed.

(* The three discriminants are moreover MUTUALLY EXCLUSIVE — at most one fires on
   any node (a corollary: a TypeVar node is not simultaneously recognized as a
   ParamSpec node). *)
Theorem is_typevar_not_paramspec : forall tp,
  is_typevar tp = true -> is_paramspec tp = false.
Proof. intros tp; destruct tp; simpl; solve [reflexivity | discriminate]. Qed.
Theorem is_paramspec_not_typevartuple : forall tp,
  is_paramspec tp = true -> is_typevartuple tp = false.
Proof. intros tp; destruct tp; simpl; solve [reflexivity | discriminate]. Qed.

(* ===================================================================== *)
(* 4. (d) The projectors are EXACT on the slots they read, and every       *)
(*    carried field is OBSERVABLE (non-vacuity: never a shared 0).         *)
(* ===================================================================== *)

Theorem tp_name_typevar : forall n b, tp_name (TPTypeVar n b) = n.
Proof. reflexivity. Qed.
Theorem tp_name_paramspec : forall n, tp_name (TPParamSpec n) = n.
Proof. reflexivity. Qed.
Theorem tp_name_typevartuple : forall n, tp_name (TPTypeVarTuple n) = n.
Proof. reflexivity. Qed.
Theorem tp_bound_typevar : forall n b, tp_bound (TPTypeVar n b) = b.
Proof. reflexivity. Qed.

(* Off-variant default agrees with the WhyML (`IrOther ""` = emit0): a
   bound-less ParamSpec/TypeVarTuple projects the default bound. *)
Theorem tp_bound_paramspec_default : forall n, tp_bound (TPParamSpec n) = emit0.
Proof. reflexivity. Qed.
Theorem tp_bound_typevartuple_default : forall n, tp_bound (TPTypeVarTuple n) = emit0.
Proof. reflexivity. Qed.

(* Per-field observability: TPTypeVar's name and bound are BOTH observed
   (independently) — the `T: bound` shape carries both faithfully, never
   int-erased to a shared value. *)
Theorem tptypevar_name_observable : forall n m b, n <> m -> TPTypeVar n b <> TPTypeVar m b.
Proof. intros n m b H C; inversion C; contradiction. Qed.
Theorem tptypevar_bound_observable : forall n b c, b <> c -> TPTypeVar n b <> TPTypeVar n c.
Proof. intros n b c H C; inversion C; contradiction. Qed.
(* ParamSpec / TypeVarTuple names are observed (distinct params are distinct
   nodes) — and a ParamSpec named `n` is never a TypeVarTuple named `n`. *)
Theorem tpparamspec_name_observable : forall n m, n <> m -> TPParamSpec n <> TPParamSpec m.
Proof. intros n m H C; inversion C; contradiction. Qed.
Theorem tptypevartuple_name_observable : forall n m, n <> m -> TPTypeVarTuple n <> TPTypeVarTuple m.
Proof. intros n m H C; inversion C; contradiction. Qed.
Theorem tpparamspec_neq_tptypevartuple_samename : forall n, TPParamSpec n <> TPTypeVarTuple n.
Proof. intros n C; discriminate. Qed.

(* ===================================================================== *)
(* 5. (e) The type-param list `tparam_list` — WELL-FOUNDED length + TOTAL   *)
(*    indexer (the WhyML `tparam_list` / `tpl_len` / `tpl_nth`).            *)
(* ===================================================================== *)

(* tpl_len/tpl_nth model the WhyML `int`-valued length/index (Z), so the
   well-foundedness comparisons below are in Z_scope. *)
Local Open Scope Z_scope.

Inductive tparam_list : Type :=
  | TPNil
  | TPCons (h : tparam) (t : tparam_list).

(* tpl_len — verbatim image of the WhyML `let rec function tpl_len`. *)
Fixpoint tpl_len (l : tparam_list) : Z :=
  match l with
  | TPNil       => 0
  | TPCons _ t  => 1 + tpl_len t
  end.

(* tpl_nth — verbatim image of the WhyML `let rec function tpl_nth` (default
   `TPParamSpec ""` on nil / overshoot; `variant { l }` structural recursion).
   Coq accepts the structural recursion on `l` directly: TOTAL by construction. *)
Fixpoint tpl_nth (i : Z) (l : tparam_list) : tparam :=
  match l with
  | TPNil       => TPParamSpec EmptyString
  | TPCons h t  => if Z.leb i 0 then h else tpl_nth (i - 1) t
  end.

(* Well-foundedness witnesses for the WhyML `variant { l }`: a list length is
   non-negative, and the TAIL is STRICTLY shorter than the cons that carries it —
   so no infinite descent, i.e. the tpl_nth loop terminates. *)
Theorem tpl_len_nonneg : forall l, 0 <= tpl_len l.
Proof. induction l as [| h t IH]; cbn [tpl_len]; lia. Qed.

Theorem tpl_len_cons : forall h t, tpl_len (TPCons h t) = 1 + tpl_len t.
Proof. reflexivity. Qed.

Theorem tpl_tail_len_lt : forall h t, tpl_len t < tpl_len (TPCons h t).
Proof. intros h t; cbn [tpl_len]; lia. Qed.

(* Totality is definitional; here the observable behaviour of the total indexer:
   at index 0 of a cons it reads the head; on nil it is the default. *)
Theorem tpl_nth_zero : forall h t, tpl_nth 0 (TPCons h t) = h.
Proof. reflexivity. Qed.
Theorem tpl_nth_nil : forall i, tpl_nth i TPNil = TPParamSpec EmptyString.
Proof. reflexivity. Qed.
Theorem tpl_nth_succ : forall i h t, (i > 0)%Z -> tpl_nth i (TPCons h t) = tpl_nth (i - 1) t.
Proof.
  intros i h t H; simpl.
  destruct (Z.leb i 0) eqn:E; [ apply Z.leb_le in E; lia | reflexivity ].
Qed.

(* An EMPTY type-param list (TPNil) and a NON-empty one (TPCons) are DISTINCT —
   the list is OBSERVABLE, not TPNil-erased; their lengths differ too. *)
Theorem tpl_empty_neq_nonempty : forall h t, TPNil <> TPCons h t.
Proof. intros h t C; discriminate. Qed.
Theorem tpl_len_grows_with_cons : forall h t, tpl_len t < tpl_len (TPCons h t).
Proof. intros h t; cbn [tpl_len]; lia. Qed.

(* Decidable equality on `tparam_list`, given the ctor-child eq_dec. *)
Definition tparam_list_eq_dec : forall x y : tparam_list, {x = y} + {x <> y}.
Proof. decide equality; apply tparam_eq_dec. Defined.

End TParam.

(* ===================================================================== *)
(* 6. VERDICT — assumption audit.  Every result must be `Closed under the  *)
(*    global context` (NO axiom): the 3-axiom trust ledger is intact.      *)
(* ===================================================================== *)

Print Assumptions tparam_eq_dec.
Print Assumptions kind_of_typevar.
Print Assumptions kind_of_paramspec.
Print Assumptions kind_of_typevartuple.
Print Assumptions tag_typevar_neq_paramspec.
Print Assumptions tag_typevar_neq_typevartuple.
Print Assumptions tag_paramspec_neq_typevartuple.
Print Assumptions ctor_typevar_neq_paramspec.
Print Assumptions is_typevar_faithful.
Print Assumptions is_paramspec_faithful.
Print Assumptions is_typevartuple_faithful.
Print Assumptions is_typevar_not_paramspec.
Print Assumptions is_paramspec_not_typevartuple.
Print Assumptions tp_name_typevar.
Print Assumptions tp_name_paramspec.
Print Assumptions tp_name_typevartuple.
Print Assumptions tp_bound_typevar.
Print Assumptions tp_bound_paramspec_default.
Print Assumptions tp_bound_typevartuple_default.
Print Assumptions tptypevar_name_observable.
Print Assumptions tptypevar_bound_observable.
Print Assumptions tpparamspec_name_observable.
Print Assumptions tptypevartuple_name_observable.
Print Assumptions tpparamspec_neq_tptypevartuple_samename.
Print Assumptions tpl_len_nonneg.
Print Assumptions tpl_len_cons.
Print Assumptions tpl_tail_len_lt.
Print Assumptions tpl_nth_zero.
Print Assumptions tpl_nth_nil.
Print Assumptions tpl_nth_succ.
Print Assumptions tpl_empty_neq_nonempty.
Print Assumptions tpl_len_grows_with_cons.
Print Assumptions tparam_list_eq_dec.
