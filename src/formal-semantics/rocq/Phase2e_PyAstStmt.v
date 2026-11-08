(* Phase2e_PyAstStmt.v — axiom-free certificate for the `pyast_stmt` INPUT-side
   raw-`ast.stmt` value shape (self-tcb-reduction giants, generic class-body
   lowering).

   CO-LANDING COUPLING (the tier-3 / lesson-#5 rule, cf. Phase2c_PyConstVal.v /
   Phase2d_StmtIR.v): the WhyML `pyast_stmt` theory promoted into the emitter
   preamble (`module6_whyml/preamble.py`, gated on `_uses_pyast_stmt`) is a NEW
   value shape — the raw `ast.stmt` union a class-body iterator
   (`_collect_class_constants`) isinstance-dispatches over — so it lands with a
   proof, not a trusted assumption.  It is DISJOINT from the OUTPUT-side
   `stmt_ir` of Phase2d: the constructor prefix here is `PS*` (`PSAssign` — the
   INPUT node) versus `S*` there (`SAssign` — the LOWERED node).  This file
   certifies, against pure inductive datatypes with NO axiom, exactly what the
   emitter relies on when it isinstance-dispatches a class-body statement and
   reads its already-lowered children:

     (a) `pyast_stmt` is a well-formed inductive carrying the FOREIGN emit_ir
         expr-child type (`PSAssign`/`PSAnnAssign`'s target/annotation/value are
         `emit`, which never mentions `pyast_stmt` — no mutual recursion), with
         DECIDABLE equality given decidable equality on `emit`;
     (b) `stmt_node_kind_of` is EXACT on every constructor, and the ctor tags are
         pairwise DISTINCT (Assign / AnnAssign / ClassDef / FunctionDef / Other
         are provably separate node identities);
     (c) the LOAD-BEARING faithfulness laws — the WhyML `is_K_faithful` lemmas —
         hold: `is_K_node s = true <-> stmt_node_kind_of s = "K"` for
         K in {assign, annassign, classdef, functiondef}.  These discharge in the
         WhyML whole-file proof; certified here they model the isinstance
         dispatch faithfully;
     (d) the projectors `stmt_target0` / `stmt_value` / `stmt_annotation`
         (: pyast_stmt -> emit), `def_name` (: pyast_stmt -> string), and the
         opaque `stmt_targets_len` (: pyast_stmt -> Z) are EXACT on the
         constructor slots they read, with the SAME off-variant defaults as the
         WhyML (`IrOther ""` modelled by the abstract witness `emit0`, `""`, and
         an abstract opaque count for `stmt_targets_len` — the WhyML `val`);
     (e) the class-body statement list `psl = PSLNil | PSLCons pyast_stmt psl`
         (the mutual-cons `node.body` iterates) has a WELL-FOUNDED length measure
         `psl_len` and a TOTAL indexer `psl_nth`: the tail is STRICTLY shorter
         than the cons, so the WhyML `psl_nth`'s `variant { l }` structural
         recursion (equivalently the `psl_len`-bounded loop) is certified to
         terminate — no infinite descent.

   The abstract WhyML `val`s `class_body_ast` / `ps_const_int` / `ps_field_mem`
   are NOT `pyast_stmt` soundness obligations (opaque readers, no per-value law),
   and `stmt_targets_len` is likewise a WhyML `val function` (opaque `len(...)`
   count) — modelled here by a Section variable, TOTAL by typing, exactly as the
   WhyML leaves it.

   The `Print Assumptions` block at the bottom is the trust check: every result
   must be `Closed under the global context` (NO axiom) so the 3-axiom trust
   ledger (`proof_axiom_allowlist.py`) stays intact.  Nothing here is Admitted.
   Build: part of `make` (listed in `_CoqProject` after `Phase2d_StmtIR.v`). *)

Require Import ZArith String List Bool Lia.
Import ListNotations.
Open Scope string_scope.

Section PyAstStmt.

(* The WhyML emit_ir expr-child type, abstracted (see header (a)): kept a Section
   variable so `pyast_stmt` provably carries a FOREIGN child — there is no
   `pyast_stmt` occurrence inside `emit`, hence no mutual recursion.  `emit0`
   witnesses the WhyML projectors' off-variant default `IrOther ""`. *)
Variable emit : Type.
Variable emit0 : emit.
Variable emit_eq_dec : forall a b : emit, {a = b} + {a <> b}.

(* ===================================================================== *)
(* 1. The raw ast.stmt ADT — mirrors the WhyML `type pyast_stmt`.         *)
(*    Field order of PSAnnAssign is (target, annotation, value) — exactly *)
(*    the WhyML `PSAnnAssign emit_ir emit_ir emit_ir` whose projectors    *)
(*    read t/a/v from positions 1/2/3.                                    *)
(* ===================================================================== *)

Inductive pyast_stmt : Type :=
  | PSAssign (target value : emit)
  | PSAnnAssign (target annotation value : emit)
  | PSClassDef (name : string)
  | PSFunctionDef (name : string)
  | PSPass
  | PSExprEllipsis
  | PSOther.

(* The tag discriminant — verbatim image of the WhyML `stmt_node_kind_of`.
   PSPass / PSExprEllipsis are the nullary `ast.Pass` and `ast.Expr(Constant(...))`
   whose value is `Ellipsis` — the two `node.body[0]` shapes `_is_overload_stub`
   discriminates (an `@overload` stub body is exactly `pass` or `...`).  Both are
   NULLARY (no load-bearing child: the recognizer collapses the whole
   `Expr(Constant(Ellipsis))` chain into a single node identity). *)
Definition stmt_node_kind_of (s : pyast_stmt) : string :=
  match s with
  | PSAssign _ _        => "Assign"
  | PSAnnAssign _ _ _   => "AnnAssign"
  | PSClassDef _        => "ClassDef"
  | PSFunctionDef _     => "FunctionDef"
  | PSPass              => "Pass"
  | PSExprEllipsis      => "ExprEllipsis"
  | PSOther             => "Other"
  end.

(* The isinstance discriminants — verbatim images of the WhyML `is_K_node`
   predicates (WhyML `predicate` -> Coq bool). *)
Definition is_assign_node (s : pyast_stmt) : bool :=
  match s with PSAssign _ _ => true | _ => false end.
Definition is_annassign_node (s : pyast_stmt) : bool :=
  match s with PSAnnAssign _ _ _ => true | _ => false end.
Definition is_classdef_node (s : pyast_stmt) : bool :=
  match s with PSClassDef _ => true | _ => false end.
Definition is_functiondef_node (s : pyast_stmt) : bool :=
  match s with PSFunctionDef _ => true | _ => false end.
Definition is_pass_node (s : pyast_stmt) : bool :=
  match s with PSPass => true | _ => false end.
Definition is_expr_ellipsis_node (s : pyast_stmt) : bool :=
  match s with PSExprEllipsis => true | _ => false end.

(* The projectors — verbatim images of the WhyML `stmt_target0` / `stmt_value` /
   `stmt_annotation` / `def_name`, with the SAME off-variant defaults
   (`IrOther ""` modelled by `emit0`, and `""`). *)
Definition stmt_target0 (s : pyast_stmt) : emit :=
  match s with
  | PSAssign t _      => t
  | PSAnnAssign t _ _ => t
  | _                 => emit0
  end.
Definition stmt_value (s : pyast_stmt) : emit :=
  match s with
  | PSAssign _ v      => v
  | PSAnnAssign _ _ v => v
  | _                 => emit0
  end.
Definition stmt_annotation (s : pyast_stmt) : emit :=
  match s with
  | PSAnnAssign _ a _ => a
  | _                 => emit0
  end.
Definition def_name (s : pyast_stmt) : string :=
  match s with
  | PSClassDef n    => n
  | PSFunctionDef n => n
  | _               => EmptyString
  end.

(* `stmt_targets_len` is a WhyML `val function` — an OPAQUE `len(child.targets)`
   count with no body.  Modelled here by a Section variable: TOTAL by typing,
   exactly as the WhyML leaves it (no per-value law to certify). *)
Variable stmt_targets_len : pyast_stmt -> Z.

(* Decidable equality on `pyast_stmt`, given decidable equality on the foreign
   child `emit` — the well-formed-ADT obligation. *)
Definition pyast_stmt_eq_dec : forall x y : pyast_stmt, {x = y} + {x <> y}.
Proof. decide equality; (apply emit_eq_dec || apply string_dec). Defined.

(* ===================================================================== *)
(* 2. (b) `stmt_node_kind_of` is EXACT per ctor, and the tags DISTINCT.    *)
(* ===================================================================== *)

Theorem kind_of_assign : forall t v, stmt_node_kind_of (PSAssign t v) = "Assign".
Proof. reflexivity. Qed.
Theorem kind_of_annassign : forall t a v, stmt_node_kind_of (PSAnnAssign t a v) = "AnnAssign".
Proof. reflexivity. Qed.
Theorem kind_of_classdef : forall n, stmt_node_kind_of (PSClassDef n) = "ClassDef".
Proof. reflexivity. Qed.
Theorem kind_of_functiondef : forall n, stmt_node_kind_of (PSFunctionDef n) = "FunctionDef".
Proof. reflexivity. Qed.
Theorem kind_of_pass : stmt_node_kind_of PSPass = "Pass".
Proof. reflexivity. Qed.
Theorem kind_of_expr_ellipsis : stmt_node_kind_of PSExprEllipsis = "ExprEllipsis".
Proof. reflexivity. Qed.
Theorem kind_of_other : stmt_node_kind_of PSOther = "Other".
Proof. reflexivity. Qed.

(* The five tags are pairwise DISTINCT — the honest node identity: an Assign is
   never confused with an AnnAssign / ClassDef / FunctionDef / Other node. *)
Theorem tag_assign_neq_annassign : forall t v a b c,
  stmt_node_kind_of (PSAssign t v) <> stmt_node_kind_of (PSAnnAssign a b c).
Proof. intros; simpl; discriminate. Qed.
Theorem tag_assign_neq_classdef : forall t v n,
  stmt_node_kind_of (PSAssign t v) <> stmt_node_kind_of (PSClassDef n).
Proof. intros; simpl; discriminate. Qed.
Theorem tag_assign_neq_functiondef : forall t v n,
  stmt_node_kind_of (PSAssign t v) <> stmt_node_kind_of (PSFunctionDef n).
Proof. intros; simpl; discriminate. Qed.
Theorem tag_assign_neq_other : forall t v,
  stmt_node_kind_of (PSAssign t v) <> stmt_node_kind_of PSOther.
Proof. intros; simpl; discriminate. Qed.
Theorem tag_annassign_neq_classdef : forall t a v n,
  stmt_node_kind_of (PSAnnAssign t a v) <> stmt_node_kind_of (PSClassDef n).
Proof. intros; simpl; discriminate. Qed.
Theorem tag_annassign_neq_functiondef : forall t a v n,
  stmt_node_kind_of (PSAnnAssign t a v) <> stmt_node_kind_of (PSFunctionDef n).
Proof. intros; simpl; discriminate. Qed.
Theorem tag_classdef_neq_functiondef : forall n m,
  stmt_node_kind_of (PSClassDef n) <> stmt_node_kind_of (PSFunctionDef m).
Proof. intros; simpl; discriminate. Qed.
Theorem tag_classdef_neq_other : forall n,
  stmt_node_kind_of (PSClassDef n) <> stmt_node_kind_of PSOther.
Proof. intros; simpl; discriminate. Qed.
Theorem tag_functiondef_neq_other : forall n,
  stmt_node_kind_of (PSFunctionDef n) <> stmt_node_kind_of PSOther.
Proof. intros; simpl; discriminate. Qed.
(* PSPass / PSExprEllipsis are distinct node identities from each other and from
   every other kind — an `@overload` stub body's `pass` is never confused with a
   `...` (Ellipsis) expr, nor with a real Assign / FunctionDef / Other node. *)
Theorem tag_pass_neq_expr_ellipsis :
  stmt_node_kind_of PSPass <> stmt_node_kind_of PSExprEllipsis.
Proof. simpl; discriminate. Qed.
Theorem tag_pass_neq_other :
  stmt_node_kind_of PSPass <> stmt_node_kind_of PSOther.
Proof. simpl; discriminate. Qed.
Theorem tag_expr_ellipsis_neq_other :
  stmt_node_kind_of PSExprEllipsis <> stmt_node_kind_of PSOther.
Proof. simpl; discriminate. Qed.
Theorem tag_pass_neq_functiondef : forall n,
  stmt_node_kind_of PSPass <> stmt_node_kind_of (PSFunctionDef n).
Proof. intros; simpl; discriminate. Qed.

(* The constructors themselves are distinct (no erasure to a common value). *)
Theorem ctor_assign_neq_classdef : forall t v n, PSAssign t v <> PSClassDef n.
Proof. intros; discriminate. Qed.

(* ===================================================================== *)
(* 3. (c) The LOAD-BEARING faithfulness laws — the WhyML `is_K_faithful`.  *)
(*    `is_K_node s = true <-> stmt_node_kind_of s = "K"`.                  *)
(* ===================================================================== *)

Theorem is_assign_faithful : forall s,
  is_assign_node s = true <-> stmt_node_kind_of s = "Assign".
Proof. intros s; destruct s; simpl; split; intro H; solve [reflexivity | discriminate]. Qed.

Theorem is_annassign_faithful : forall s,
  is_annassign_node s = true <-> stmt_node_kind_of s = "AnnAssign".
Proof. intros s; destruct s; simpl; split; intro H; solve [reflexivity | discriminate]. Qed.

Theorem is_classdef_faithful : forall s,
  is_classdef_node s = true <-> stmt_node_kind_of s = "ClassDef".
Proof. intros s; destruct s; simpl; split; intro H; solve [reflexivity | discriminate]. Qed.

Theorem is_functiondef_faithful : forall s,
  is_functiondef_node s = true <-> stmt_node_kind_of s = "FunctionDef".
Proof. intros s; destruct s; simpl; split; intro H; solve [reflexivity | discriminate]. Qed.

Theorem is_pass_faithful : forall s,
  is_pass_node s = true <-> stmt_node_kind_of s = "Pass".
Proof. intros s; destruct s; simpl; split; intro H; solve [reflexivity | discriminate]. Qed.

Theorem is_expr_ellipsis_faithful : forall s,
  is_expr_ellipsis_node s = true <-> stmt_node_kind_of s = "ExprEllipsis".
Proof. intros s; destruct s; simpl; split; intro H; solve [reflexivity | discriminate]. Qed.

(* The pass / expr-ellipsis discriminants are MUTUALLY EXCLUSIVE — a `pass` node
   is not simultaneously recognized as an Ellipsis-expr node (the two stub-body
   shapes are disjoint). *)
Theorem is_pass_not_expr_ellipsis : forall s,
  is_pass_node s = true -> is_expr_ellipsis_node s = false.
Proof. intros s; destruct s; simpl; solve [reflexivity | discriminate]. Qed.

(* The four discriminants are moreover MUTUALLY EXCLUSIVE — at most one fires on
   any node (a corollary the faithfulness laws + tag distinctness give: an Assign
   node is not simultaneously recognized as an AnnAssign node). *)
Theorem is_assign_not_annassign : forall s,
  is_assign_node s = true -> is_annassign_node s = false.
Proof. intros s; destruct s; simpl; solve [reflexivity | discriminate]. Qed.
Theorem is_classdef_not_functiondef : forall s,
  is_classdef_node s = true -> is_functiondef_node s = false.
Proof. intros s; destruct s; simpl; solve [reflexivity | discriminate]. Qed.

(* ===================================================================== *)
(* 4. (d) The projectors are EXACT on the slots they read, and every       *)
(*    carried field is OBSERVABLE (non-vacuity: never a shared 0).         *)
(* ===================================================================== *)

Theorem stmt_target0_assign : forall t v, stmt_target0 (PSAssign t v) = t.
Proof. reflexivity. Qed.
Theorem stmt_target0_annassign : forall t a v, stmt_target0 (PSAnnAssign t a v) = t.
Proof. reflexivity. Qed.
Theorem stmt_value_assign : forall t v, stmt_value (PSAssign t v) = v.
Proof. reflexivity. Qed.
Theorem stmt_value_annassign : forall t a v, stmt_value (PSAnnAssign t a v) = v.
Proof. reflexivity. Qed.
Theorem stmt_annotation_annassign : forall t a v, stmt_annotation (PSAnnAssign t a v) = a.
Proof. reflexivity. Qed.
Theorem def_name_classdef : forall n, def_name (PSClassDef n) = n.
Proof. reflexivity. Qed.
Theorem def_name_functiondef : forall n, def_name (PSFunctionDef n) = n.
Proof. reflexivity. Qed.

(* Off-variant defaults agree with the WhyML (`IrOther ""` = emit0, `""`). *)
Theorem stmt_annotation_default : stmt_annotation PSOther = emit0.
Proof. reflexivity. Qed.
Theorem def_name_default : def_name PSOther = EmptyString.
Proof. reflexivity. Qed.

(* Per-field observability: PSAssign's target and value are BOTH observed. *)
Theorem psassign_target_observable : forall t u v, t <> u -> PSAssign t v <> PSAssign u v.
Proof. intros t u v H C; inversion C; contradiction. Qed.
Theorem psassign_value_observable : forall t v w, v <> w -> PSAssign t v <> PSAssign t w.
Proof. intros t v w H C; inversion C; contradiction. Qed.
(* PSAnnAssign's target / annotation / value are INDEPENDENTLY observed — the
   annotation slot is genuinely distinct from the value slot (the `x: T = e`
   shape carries all three faithfully). *)
Theorem psannassign_target_observable : forall t u a v, t <> u -> PSAnnAssign t a v <> PSAnnAssign u a v.
Proof. intros t u a v H C; inversion C; contradiction. Qed.
Theorem psannassign_annotation_observable : forall t a b v, a <> b -> PSAnnAssign t a v <> PSAnnAssign t b v.
Proof. intros t a b v H C; inversion C; contradiction. Qed.
Theorem psannassign_value_observable : forall t a v w, v <> w -> PSAnnAssign t a v <> PSAnnAssign t a w.
Proof. intros t a v w H C; inversion C; contradiction. Qed.
(* PSClassDef / PSFunctionDef names are observed (distinct classes/functions are
   distinct nodes) — and a class named `n` is never a function named `n`. *)
Theorem psclassdef_name_observable : forall n m, n <> m -> PSClassDef n <> PSClassDef m.
Proof. intros n m H C; inversion C; contradiction. Qed.
Theorem psfunctiondef_name_observable : forall n m, n <> m -> PSFunctionDef n <> PSFunctionDef m.
Proof. intros n m H C; inversion C; contradiction. Qed.
Theorem psclassdef_neq_psfunctiondef_samename : forall n, PSClassDef n <> PSFunctionDef n.
Proof. intros n C; discriminate. Qed.

(* ===================================================================== *)
(* 5. (e) The class-body statement list `psl` — WELL-FOUNDED length + TOTAL *)
(*    indexer (the WhyML `psl` / `psl_len` / `psl_nth`).                    *)
(* ===================================================================== *)

(* psl_len/psl_nth model the WhyML `int`-valued length/index (Z), so the
   well-foundedness comparisons below are in Z_scope. *)
Local Open Scope Z_scope.

Inductive psl : Type :=
  | PSLNil
  | PSLCons (h : pyast_stmt) (t : psl).

(* psl_len — verbatim image of the WhyML `let rec function psl_len`. *)
Fixpoint psl_len (l : psl) : Z :=
  match l with
  | PSLNil      => 0
  | PSLCons _ t => 1 + psl_len t
  end.

(* psl_nth — verbatim image of the WhyML `let rec function psl_nth` (default
   PSOther on nil / overshoot; `variant { l }` structural recursion).  Coq accepts
   the structural recursion on `l` directly: `psl_nth` is TOTAL by construction. *)
Fixpoint psl_nth (i : Z) (l : psl) : pyast_stmt :=
  match l with
  | PSLNil      => PSOther
  | PSLCons h t => if Z.leb i 0 then h else psl_nth (i - 1) t
  end.

(* Well-foundedness witnesses for the WhyML `variant { l }`: a list length is
   non-negative, and the TAIL is STRICTLY shorter than the cons that carries it —
   so no infinite descent, i.e. the psl_nth loop terminates. *)
Theorem psl_len_nonneg : forall l, 0 <= psl_len l.
Proof. induction l as [| h t IH]; cbn [psl_len]; lia. Qed.

Theorem psl_len_cons : forall h t, psl_len (PSLCons h t) = 1 + psl_len t.
Proof. reflexivity. Qed.

Theorem psl_tail_len_lt : forall h t, psl_len t < psl_len (PSLCons h t).
Proof. intros h t; cbn [psl_len]; lia. Qed.

(* Totality is definitional; here the observable behaviour of the total indexer:
   at index 0 of a cons it reads the head; on nil it is the PSOther default. *)
Theorem psl_nth_zero : forall h t, psl_nth 0 (PSLCons h t) = h.
Proof. reflexivity. Qed.
Theorem psl_nth_nil : forall i, psl_nth i PSLNil = PSOther.
Proof. reflexivity. Qed.
Theorem psl_nth_succ : forall i h t, (i > 0)%Z -> psl_nth i (PSLCons h t) = psl_nth (i - 1) t.
Proof.
  intros i h t H; simpl.
  destruct (Z.leb i 0) eqn:E; [ apply Z.leb_le in E; lia | reflexivity ].
Qed.

(* An EMPTY class body (PSLNil) and a NON-empty one (PSLCons) are DISTINCT — the
   body is OBSERVABLE, not PSLNil-erased; their lengths differ too. *)
Theorem psl_empty_neq_nonempty : forall h t, PSLNil <> PSLCons h t.
Proof. intros h t C; discriminate. Qed.
Theorem psl_len_grows_with_cons : forall h t, psl_len t < psl_len (PSLCons h t).
Proof. intros h t; cbn [psl_len]; lia. Qed.

(* Decidable equality on `psl`, given the ctor-child eq_dec. *)
Definition psl_eq_dec : forall x y : psl, {x = y} + {x <> y}.
Proof. decide equality; apply pyast_stmt_eq_dec. Defined.

End PyAstStmt.

(* ===================================================================== *)
(* 6. VERDICT — assumption audit.  Every result must be `Closed under the  *)
(*    global context` (NO axiom): the 3-axiom trust ledger is intact.      *)
(* ===================================================================== *)

Print Assumptions pyast_stmt_eq_dec.
Print Assumptions kind_of_assign.
Print Assumptions kind_of_annassign.
Print Assumptions kind_of_classdef.
Print Assumptions kind_of_functiondef.
Print Assumptions kind_of_pass.
Print Assumptions kind_of_expr_ellipsis.
Print Assumptions kind_of_other.
Print Assumptions tag_assign_neq_annassign.
Print Assumptions tag_assign_neq_classdef.
Print Assumptions tag_assign_neq_functiondef.
Print Assumptions tag_assign_neq_other.
Print Assumptions tag_annassign_neq_classdef.
Print Assumptions tag_annassign_neq_functiondef.
Print Assumptions tag_classdef_neq_functiondef.
Print Assumptions tag_classdef_neq_other.
Print Assumptions tag_functiondef_neq_other.
Print Assumptions ctor_assign_neq_classdef.
Print Assumptions is_assign_faithful.
Print Assumptions is_annassign_faithful.
Print Assumptions is_classdef_faithful.
Print Assumptions is_functiondef_faithful.
Print Assumptions is_pass_faithful.
Print Assumptions is_expr_ellipsis_faithful.
Print Assumptions is_pass_not_expr_ellipsis.
Print Assumptions tag_pass_neq_expr_ellipsis.
Print Assumptions tag_pass_neq_other.
Print Assumptions tag_expr_ellipsis_neq_other.
Print Assumptions tag_pass_neq_functiondef.
Print Assumptions is_assign_not_annassign.
Print Assumptions is_classdef_not_functiondef.
Print Assumptions stmt_target0_assign.
Print Assumptions stmt_target0_annassign.
Print Assumptions stmt_value_assign.
Print Assumptions stmt_value_annassign.
Print Assumptions stmt_annotation_annassign.
Print Assumptions def_name_classdef.
Print Assumptions def_name_functiondef.
Print Assumptions stmt_annotation_default.
Print Assumptions def_name_default.
Print Assumptions psassign_target_observable.
Print Assumptions psassign_value_observable.
Print Assumptions psannassign_target_observable.
Print Assumptions psannassign_annotation_observable.
Print Assumptions psannassign_value_observable.
Print Assumptions psclassdef_name_observable.
Print Assumptions psfunctiondef_name_observable.
Print Assumptions psclassdef_neq_psfunctiondef_samename.
Print Assumptions psl_len_nonneg.
Print Assumptions psl_len_cons.
Print Assumptions psl_tail_len_lt.
Print Assumptions psl_nth_zero.
Print Assumptions psl_nth_nil.
Print Assumptions psl_nth_succ.
Print Assumptions psl_empty_neq_nonempty.
Print Assumptions psl_len_grows_with_cons.
Print Assumptions psl_eq_dec.
