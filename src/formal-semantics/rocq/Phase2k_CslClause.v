(* Phase2k_CslClause.v — axiom-free certificate for the `csl_clause` contract-clause
   value shape (self-tcb-reduction, `_act_guard` conversion).

   CO-LANDING COUPLING (the tier-3 / lesson-#5 rule, cf. Phase2e_PyAstStmt.v /
   Phase2d_StmtIR.v): the WhyML `csl_clause` theory promoted into the emitter
   preamble (`module6_whyml/preamble.py`, gated on the tight `_uses_act_guard`
   sentinel) is a NEW value shape — the contract-clause union an `Act`'s
   `.clauses` list carries, which `_act_guard` filters (`isinstance(cl, Given)`)
   and projects (`cl.expr`) over — so it lands with a proof, not a trusted
   assumption.  It is DISJOINT from every other certified value shape: the
   constructor prefix here is `C*` (`CGiven` — a contract clause) versus the
   `PS*`/`S*`/`Ir*` prefixes of the ast / stmt-ir / emit_ir shapes.  This file
   certifies, against pure inductive datatypes with NO axiom, exactly what the
   emitter relies on when `_act_guard` filters + folds the `given` clauses:

     (a) `csl_clause` is a well-formed inductive carrying the FOREIGN emit_ir
         expr-child type (`.expr`, an `emit`, which never mentions `csl_clause`
         — no mutual recursion), with DECIDABLE equality given decidable
         equality on `emit`;
     (b) `clause_kind_of` is EXACT on every constructor, and the ctor tags are
         pairwise DISTINCT (Given / Requires / Ensures / Assigns are provably
         separate clause identities);
     (c) the LOAD-BEARING faithfulness laws — the WhyML `is_K_faithful` lemmas —
         hold: `is_K_node s = true <-> clause_kind_of s = "K"` for
         K in {given, requires, ensures, assigns}.  These discharge in the WhyML
         whole-file proof; certified here they model the `isinstance(cl, Given)`
         dispatch faithfully;
     (d) the projector `clause_expr_of : csl_clause -> emit` is EXACT on the
         `.expr` slot every constructor carries (a TOTAL projection — every
         clause wraps an expr), and the carried expr is OBSERVABLE (non-vacuity);
     (e) the clause list `clause_list = ClNil | ClCons csl_clause clause_list`
         (the `act.clauses` iterated — the bespoke-cons `keyword_list`/`psl`
         precedent) has a WELL-FOUNDED length measure `cl_len` and a TOTAL
         indexer `cl_nth`: the tail is STRICTLY shorter than the cons, so the
         WhyML `cl_nth`'s `variant { l }` structural recursion (equivalently the
         `act_guard_fold`'s `variant { l }`) is certified to terminate — no
         infinite descent.

   The abstract WhyML `val` `act_clauses_of` is NOT a `csl_clause` soundness
   obligation (an opaque reader of the `Act` node's `.clauses`, no per-value
   law) — modelled here by a Section variable, TOTAL by typing, exactly as the
   WhyML leaves it (the `py_functiondef_node`/`func_body_ast` precedent).

   The `Print Assumptions` block at the bottom is the trust check: every result
   must be `Closed under the global context` (NO axiom) so the 3-axiom trust
   ledger (`proof_axiom_allowlist.py`) stays intact.  Nothing here is Admitted.
   Build: part of `make` (listed in `_CoqProject` after `Phase2j_MethodRecv.v`). *)

Require Import ZArith String List Bool Lia.
Import ListNotations.
Open Scope string_scope.

Section CslClause.

(* The WhyML emit_ir expr-child type, abstracted (see header (a)): kept a Section
   variable so `csl_clause` provably carries a FOREIGN child — there is no
   `csl_clause` occurrence inside `emit`, hence no mutual recursion.  `emit0`
   witnesses off-variant projector defaults (unused here — the projector is
   total — but kept for parallelism with the ast/stmt certificates). *)
Variable emit : Type.
Variable emit0 : emit.
Variable emit_eq_dec : forall a b : emit, {a = b} + {a <> b}.

(* ===================================================================== *)
(* 1. The contract-clause ADT — mirrors the WhyML `type csl_clause`.       *)
(*    Each constructor wraps the clause's `.expr` (the WhyML                *)
(*    `CGiven emit_ir | CRequires emit_ir | CEnsures emit_ir |             *)
(*     CAssigns emit_ir` whose projector reads the expr from position 1).  *)
(* ===================================================================== *)

Inductive csl_clause : Type :=
  | CGiven (e : emit)
  | CRequires (e : emit)
  | CEnsures (e : emit)
  | CAssigns (e : emit).

(* The tag discriminant — verbatim image of the WhyML `clause_kind_of`. *)
Definition clause_kind_of (s : csl_clause) : string :=
  match s with
  | CGiven _    => "Given"
  | CRequires _ => "Requires"
  | CEnsures _  => "Ensures"
  | CAssigns _  => "Assigns"
  end.

(* The isinstance discriminants — verbatim images of the WhyML `is_K_node`
   predicates (WhyML `predicate` -> Coq bool).  `is_given_node` is the
   load-bearing one: `_act_guard` filters `isinstance(cl, Given)`. *)
Definition is_given_node (s : csl_clause) : bool :=
  match s with CGiven _ => true | _ => false end.
Definition is_requires_node (s : csl_clause) : bool :=
  match s with CRequires _ => true | _ => false end.
Definition is_ensures_node (s : csl_clause) : bool :=
  match s with CEnsures _ => true | _ => false end.
Definition is_assigns_node (s : csl_clause) : bool :=
  match s with CAssigns _ => true | _ => false end.

(* The projector — verbatim image of the WhyML `clause_expr_of`.  TOTAL: every
   constructor carries an `.expr`, so there is no off-variant default (the
   `_act_guard` fold only ever projects a `CGiven`, but the projection is
   defined on every clause). *)
Definition clause_expr_of (s : csl_clause) : emit :=
  match s with
  | CGiven e    => e
  | CRequires e => e
  | CEnsures e  => e
  | CAssigns e  => e
  end.

(* Decidable equality on `csl_clause`, given decidable equality on the foreign
   child `emit` — the well-formed-ADT obligation. *)
Definition csl_clause_eq_dec : forall x y : csl_clause, {x = y} + {x <> y}.
Proof. decide equality; apply emit_eq_dec. Defined.

(* ===================================================================== *)
(* 2. (b) `clause_kind_of` is EXACT per ctor, and the tags DISTINCT.       *)
(* ===================================================================== *)

Theorem kind_of_given : forall e, clause_kind_of (CGiven e) = "Given".
Proof. reflexivity. Qed.
Theorem kind_of_requires : forall e, clause_kind_of (CRequires e) = "Requires".
Proof. reflexivity. Qed.
Theorem kind_of_ensures : forall e, clause_kind_of (CEnsures e) = "Ensures".
Proof. reflexivity. Qed.
Theorem kind_of_assigns : forall e, clause_kind_of (CAssigns e) = "Assigns".
Proof. reflexivity. Qed.

(* The four tags are pairwise DISTINCT — the honest clause identity: a Given is
   never confused with a Requires / Ensures / Assigns clause. *)
Theorem tag_given_neq_requires : forall a b,
  clause_kind_of (CGiven a) <> clause_kind_of (CRequires b).
Proof. intros; simpl; discriminate. Qed.
Theorem tag_given_neq_ensures : forall a b,
  clause_kind_of (CGiven a) <> clause_kind_of (CEnsures b).
Proof. intros; simpl; discriminate. Qed.
Theorem tag_given_neq_assigns : forall a b,
  clause_kind_of (CGiven a) <> clause_kind_of (CAssigns b).
Proof. intros; simpl; discriminate. Qed.
Theorem tag_requires_neq_ensures : forall a b,
  clause_kind_of (CRequires a) <> clause_kind_of (CEnsures b).
Proof. intros; simpl; discriminate. Qed.
Theorem tag_requires_neq_assigns : forall a b,
  clause_kind_of (CRequires a) <> clause_kind_of (CAssigns b).
Proof. intros; simpl; discriminate. Qed.
Theorem tag_ensures_neq_assigns : forall a b,
  clause_kind_of (CEnsures a) <> clause_kind_of (CAssigns b).
Proof. intros; simpl; discriminate. Qed.

(* The constructors themselves are distinct (no erasure to a common value). *)
Theorem ctor_given_neq_requires : forall a b, CGiven a <> CRequires b.
Proof. intros; discriminate. Qed.

(* ===================================================================== *)
(* 3. (c) The LOAD-BEARING faithfulness laws — the WhyML `is_K_faithful`.  *)
(*    `is_K_node s = true <-> clause_kind_of s = "K"`.                     *)
(* ===================================================================== *)

Theorem is_given_faithful : forall s,
  is_given_node s = true <-> clause_kind_of s = "Given".
Proof. intros s; destruct s; simpl; split; intro H; solve [reflexivity | discriminate]. Qed.

Theorem is_requires_faithful : forall s,
  is_requires_node s = true <-> clause_kind_of s = "Requires".
Proof. intros s; destruct s; simpl; split; intro H; solve [reflexivity | discriminate]. Qed.

Theorem is_ensures_faithful : forall s,
  is_ensures_node s = true <-> clause_kind_of s = "Ensures".
Proof. intros s; destruct s; simpl; split; intro H; solve [reflexivity | discriminate]. Qed.

Theorem is_assigns_faithful : forall s,
  is_assigns_node s = true <-> clause_kind_of s = "Assigns".
Proof. intros s; destruct s; simpl; split; intro H; solve [reflexivity | discriminate]. Qed.

(* The four discriminants are moreover MUTUALLY EXCLUSIVE — at most one fires on
   any clause (a Given clause is not simultaneously recognized as a Requires /
   Ensures / Assigns clause).  This is what makes the `_act_guard` filter honest:
   the `given` selection excludes every non-Given clause. *)
Theorem is_given_not_requires : forall s,
  is_given_node s = true -> is_requires_node s = false.
Proof. intros s; destruct s; simpl; solve [reflexivity | discriminate]. Qed.
Theorem is_given_not_ensures : forall s,
  is_given_node s = true -> is_ensures_node s = false.
Proof. intros s; destruct s; simpl; solve [reflexivity | discriminate]. Qed.
Theorem is_given_not_assigns : forall s,
  is_given_node s = true -> is_assigns_node s = false.
Proof. intros s; destruct s; simpl; solve [reflexivity | discriminate]. Qed.

(* ===================================================================== *)
(* 4. (d) The projector is EXACT on the `.expr` slot, and every carried     *)
(*    expr is OBSERVABLE (non-vacuity: never a shared 0/sentinel).         *)
(* ===================================================================== *)

Theorem clause_expr_of_given : forall e, clause_expr_of (CGiven e) = e.
Proof. reflexivity. Qed.
Theorem clause_expr_of_requires : forall e, clause_expr_of (CRequires e) = e.
Proof. reflexivity. Qed.
Theorem clause_expr_of_ensures : forall e, clause_expr_of (CEnsures e) = e.
Proof. reflexivity. Qed.
Theorem clause_expr_of_assigns : forall e, clause_expr_of (CAssigns e) = e.
Proof. reflexivity. Qed.

(* Per-clause observability: each constructor's carried expr is observed (two
   Givens with distinct exprs are distinct clauses) — so the `_act_guard` fold's
   `cl.expr` reads a REAL, distinguishable operand, never an erased constant. *)
Theorem cgiven_expr_observable : forall e f, e <> f -> CGiven e <> CGiven f.
Proof. intros e f H C; inversion C; contradiction. Qed.
Theorem crequires_expr_observable : forall e f, e <> f -> CRequires e <> CRequires f.
Proof. intros e f H C; inversion C; contradiction. Qed.
Theorem censures_expr_observable : forall e f, e <> f -> CEnsures e <> CEnsures f.
Proof. intros e f H C; inversion C; contradiction. Qed.
Theorem cassigns_expr_observable : forall e f, e <> f -> CAssigns e <> CAssigns f.
Proof. intros e f H C; inversion C; contradiction. Qed.
(* A Given and a Requires carrying the SAME expr are still distinct clauses —
   the clause kind is not erased by the shared expr. *)
Theorem cgiven_neq_crequires_samexpr : forall e, CGiven e <> CRequires e.
Proof. intros e C; discriminate. Qed.

(* ===================================================================== *)
(* 5. (e) The clause list `clause_list` — WELL-FOUNDED length + TOTAL       *)
(*    indexer (the WhyML `clause_list` / `cl_len` / `cl_nth`, and the       *)
(*    `act_guard_fold` `variant { l }`).                                    *)
(* ===================================================================== *)

(* cl_len/cl_nth model the WhyML `int`-valued length/index (Z), so the
   well-foundedness comparisons below are in Z_scope. *)
Local Open Scope Z_scope.

Inductive clause_list : Type :=
  | ClNil
  | ClCons (h : csl_clause) (t : clause_list).

(* cl_len — verbatim image of the WhyML `let rec function cl_len`. *)
Fixpoint cl_len (l : clause_list) : Z :=
  match l with
  | ClNil      => 0
  | ClCons _ t => 1 + cl_len t
  end.

(* cl_nth — verbatim image of the WhyML `let rec function cl_nth` (default
   CAssigns of the abstract witness on nil/overshoot; `variant { l }` structural
   recursion).  Coq accepts the structural recursion on `l` directly: `cl_nth`
   is TOTAL by construction. *)
Fixpoint cl_nth (i : Z) (l : clause_list) : csl_clause :=
  match l with
  | ClNil      => CAssigns emit0
  | ClCons h t => if Z.leb i 0 then h else cl_nth (i - 1) t
  end.

(* Well-foundedness witnesses for the WhyML `variant { l }` (both `cl_nth` and
   `act_guard_fold`): a list length is non-negative, and the TAIL is STRICTLY
   shorter than the cons that carries it — so no infinite descent, i.e. the
   `_act_guard` fold over `act.clauses` terminates. *)
Theorem cl_len_nonneg : forall l, 0 <= cl_len l.
Proof. induction l as [| h t IH]; cbn [cl_len]; lia. Qed.

Theorem cl_len_cons : forall h t, cl_len (ClCons h t) = 1 + cl_len t.
Proof. reflexivity. Qed.

Theorem cl_tail_len_lt : forall h t, cl_len t < cl_len (ClCons h t).
Proof. intros h t; cbn [cl_len]; lia. Qed.

(* Totality is definitional; here the observable behaviour of the total indexer:
   at index 0 of a cons it reads the head; on nil it is the (abstract) default. *)
Theorem cl_nth_zero : forall h t, cl_nth 0 (ClCons h t) = h.
Proof. reflexivity. Qed.
Theorem cl_nth_nil : forall i, cl_nth i ClNil = CAssigns emit0.
Proof. reflexivity. Qed.
Theorem cl_nth_succ : forall i h t, (i > 0)%Z -> cl_nth i (ClCons h t) = cl_nth (i - 1) t.
Proof.
  intros i h t H; simpl.
  destruct (Z.leb i 0) eqn:E; [ apply Z.leb_le in E; lia | reflexivity ].
Qed.

(* An EMPTY clause list (ClNil) and a NON-empty one (ClCons) are DISTINCT — the
   `act.clauses` list is OBSERVABLE, not ClNil-erased (so the `if not givens`
   empty-guard is a real test); their lengths differ too. *)
Theorem cl_empty_neq_nonempty : forall h t, ClNil <> ClCons h t.
Proof. intros h t C; discriminate. Qed.
Theorem cl_len_grows_with_cons : forall h t, cl_len t < cl_len (ClCons h t).
Proof. intros h t; cbn [cl_len]; lia. Qed.

(* Decidable equality on `clause_list`, given the ctor-child eq_dec. *)
Definition clause_list_eq_dec : forall x y : clause_list, {x = y} + {x <> y}.
Proof. decide equality; apply csl_clause_eq_dec. Defined.

(* ===================================================================== *)
(* 6. The `_act_guard` fold itself — a certified reference model.  Filters   *)
(*    `given` clauses, projects `.expr`, folds with a left-nested `and`:     *)
(*    `if not givens then IrBoolC 1 else fold BinOp "and"`.  Certified TOTAL  *)
(*    + STRUCTURALLY TERMINATING (the WhyML `act_guard_fold`'s `variant`).    *)
(*    Parameterised over the emit-level `and`-constructor + the `True` literal *)
(*    so it is agnostic to the emit_ir representation (in WhyML: `IrBinOp     *)
(*    "and"` and `IrBoolC 1`).                                                *)
(* ===================================================================== *)

Section GuardFold.
  Variable ir_and : emit -> emit -> emit.   (* WhyML `fun g e -> IrBinOp "and" g e` *)
  Variable ir_true : emit.                  (* WhyML `IrBoolC 1` *)

  (* The accumulator carries `None` until the first `given` is seen (`g =
     givens[0]`), then `Some g`; each further given conjoins with `ir_and`. *)
  Fixpoint act_guard_fold (acc : option emit) (l : clause_list) : emit :=
    match l with
    | ClNil => match acc with None => ir_true | Some g => g end
    | ClCons c rest =>
        if is_given_node c
        then match acc with
             | None   => act_guard_fold (Some (clause_expr_of c)) rest
             | Some g => act_guard_fold (Some (ir_and g (clause_expr_of c))) rest
             end
        else act_guard_fold acc rest
    end.

  Definition act_guard (l : clause_list) : emit := act_guard_fold None l.

  (* Reference-semantics checks (the WhyML whole-file proof re-derives these):
     no givens -> the `True` literal; a single given -> its own expr, un-wrapped
     (no spurious `and`); two givens -> `and g0 g1` (left-nested). *)
  Theorem act_guard_empty : act_guard ClNil = ir_true.
  Proof. reflexivity. Qed.
  Theorem act_guard_no_given_single : forall e,
    act_guard (ClCons (CRequires e) ClNil) = ir_true.
  Proof. reflexivity. Qed.
  Theorem act_guard_one_given : forall e,
    act_guard (ClCons (CGiven e) ClNil) = e.
  Proof. reflexivity. Qed.
  Theorem act_guard_two_givens : forall e f,
    act_guard (ClCons (CGiven e) (ClCons (CGiven f) ClNil)) = ir_and e f.
  Proof. reflexivity. Qed.
  (* A leading non-given is SKIPPED, not conjoined: [Requires; Given e] -> e. *)
  Theorem act_guard_skips_leading_nongiven : forall a e,
    act_guard (ClCons (CRequires a) (ClCons (CGiven e) ClNil)) = e.
  Proof. reflexivity. Qed.
  (* An interleaved non-given between two givens is SKIPPED: the two givens still
     conjoin directly (the filter drops the Ensures). *)
  Theorem act_guard_skips_interleaved_nongiven : forall e a f,
    act_guard (ClCons (CGiven e) (ClCons (CEnsures a) (ClCons (CGiven f) ClNil)))
    = ir_and e f.
  Proof. reflexivity. Qed.
End GuardFold.

End CslClause.

(* ===================================================================== *)
(* 7. VERDICT — assumption audit.  Every result must be `Closed under the  *)
(*    global context` (NO axiom): the 3-axiom trust ledger is intact.      *)
(* ===================================================================== *)

Print Assumptions csl_clause_eq_dec.
Print Assumptions kind_of_given.
Print Assumptions kind_of_requires.
Print Assumptions kind_of_ensures.
Print Assumptions kind_of_assigns.
Print Assumptions tag_given_neq_requires.
Print Assumptions tag_given_neq_ensures.
Print Assumptions tag_given_neq_assigns.
Print Assumptions tag_requires_neq_ensures.
Print Assumptions tag_requires_neq_assigns.
Print Assumptions tag_ensures_neq_assigns.
Print Assumptions ctor_given_neq_requires.
Print Assumptions is_given_faithful.
Print Assumptions is_requires_faithful.
Print Assumptions is_ensures_faithful.
Print Assumptions is_assigns_faithful.
Print Assumptions is_given_not_requires.
Print Assumptions is_given_not_ensures.
Print Assumptions is_given_not_assigns.
Print Assumptions clause_expr_of_given.
Print Assumptions clause_expr_of_requires.
Print Assumptions clause_expr_of_ensures.
Print Assumptions clause_expr_of_assigns.
Print Assumptions cgiven_expr_observable.
Print Assumptions crequires_expr_observable.
Print Assumptions censures_expr_observable.
Print Assumptions cassigns_expr_observable.
Print Assumptions cgiven_neq_crequires_samexpr.
Print Assumptions cl_len_nonneg.
Print Assumptions cl_len_cons.
Print Assumptions cl_tail_len_lt.
Print Assumptions cl_nth_zero.
Print Assumptions cl_nth_nil.
Print Assumptions cl_nth_succ.
Print Assumptions cl_empty_neq_nonempty.
Print Assumptions cl_len_grows_with_cons.
Print Assumptions clause_list_eq_dec.
Print Assumptions act_guard_empty.
Print Assumptions act_guard_no_given_single.
Print Assumptions act_guard_one_given.
Print Assumptions act_guard_two_givens.
Print Assumptions act_guard_skips_leading_nongiven.
Print Assumptions act_guard_skips_interleaved_nongiven.
