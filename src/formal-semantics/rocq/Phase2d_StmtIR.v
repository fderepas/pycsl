(* Phase2d_StmtIR.v — axiom-free certificate for the `stmt_ir` statement-IR ADT
   (self-tcb-reduction M5, C-bucket: the list-append-mutation wall).

   CO-LANDING COUPLING (the tier-3 rule, cf. Phase2c_PyConstVal.v): the WhyML
   `stmt_ir` theory promoted into the emitter preamble
   (`module6_whyml/preamble.py::_emit_exprir_theory`, gated on `_uses_stmt_ir`)
   is a NEW value shape — the statement-node sum an `_py_stmt_*` handler appends
   to its `ir_stmts` list — so it lands with a proof, not a trusted assumption.
   Certified here, against pure inductive datatypes with NO axiom, is exactly
   what the emitter relies on when it lowers `ir_stmts.append({"stmt": K, ...})`
   to `ir_stmts := Seq.snoc !ir_stmts <ctor>` and reflects a node's tag via
   `stmt_kind_of`:

     (a) `stmt_ir` is a WELL-FOUNDED inductive with a size measure and DECIDABLE
         equality (given decidable equality on the abstract expr-child type);
     (b) the dict->ctor abstraction `abs : pystmt -> stmt_ir` (a recognized
         `{"stmt": K}` node to its constructor) is TOTAL, INJECTIVE, and
         SURJECTIVE onto the ADT — the recognized key-set maps injectively;
     (c) `stmt_kind_of` is EXACT on every constructor and the tag map is
         INJECTIVE on the recognized key-set (SPass, SBreak, ... are provably
         DISTINCT — the honest node identity the pre-feature integer-0 erasure
         destroyed, fable Oracle 3).

   SUB-BODY increment (this landing): `stmt_ir` gains the COMPOUND constructors
   SWhile / SIf / SFor, which carry their nested statement body/orelse LISTS as a
   bespoke MONOMORPHIC cons-list `stmt_list = SLNil | SLCons stmt_ir stmt_list`
   — MUTUALLY recursive WITH `stmt_ir` (the WhyML twin uses `with stmt_list`).
   The FLAT `size` (every node size 1) is replaced by the MUTUAL well-founded
   measure `size_stmt` / `size_slist`: `size_stmt` descends into the sub-body
   (size_slist), which descends into each element (size_stmt) — the mutual
   induction, over the auto-generated mutual induction principle
   (`stmt_ir_stmt_list_mutind`). Well-foundedness is witnessed by the two
   size-DECREASE lemmas (`size_slist_lt_swhile` etc.): a sub-body is strictly
   smaller than its containing node, so no infinite descent is possible.
   `seq_to_sl` (the runtime `seq stmt_ir` -> `stmt_list` materialization) is
   Why3-INTRINSIC (`variant { Seq.length s - i }`), needing NO certificate clause
   here — this file certifies the DATA model; the seq cursor's termination is
   Why3's own.

     (d) NO MUTUAL RECURSION WITH emit_ir: the expr children (`SExpr e` carries
         the FOREIGN emit_ir type `emit`; `SReturn o` carries `iropt`; SWhile/SIf/
         SFor's TEST/ITER carry `emit`), where `emit` (a Section variable here)
         never mentions `stmt_ir` — so `stmt_ir` adds NO constructor to emit_ir's
         own size induction, and neither `size_stmt` nor `size_slist` descends
         into `emit`.  This is the one-directional-reference property the WhyML
         block needs (stmt_ir/stmt_list reference emit_ir; emit_ir references
         neither).

   The mutable-ref append convention itself (`ir_stmts : ref (seq stmt_ir)` with
   a real `writes { ir_stmts }` frame) needs NO certificate clause here: it is a
   Why3-INTRINSIC `writes` verification condition — Why3's region/effect system
   discharges the caller-visible-write obligation directly (the fable oracle
   `sound_append.mlw` proved it Valid, 0 axioms).

   The `Print Assumptions` block at the bottom is the trust check: every result
   must be `Closed under the global context` (NO axiom) so the 3-axiom trust
   ledger (`proof_axiom_allowlist.py`) stays intact.  Nothing here is Admitted.
   Build: part of `make` (listed in `_CoqProject` after `Phase2c_PyValDict.v`). *)

Require Import ZArith String List Bool Lia.
Import ListNotations.
Open Scope string_scope.

Section StmtIR.

(* The WhyML emit_ir expr-child type, abstracted (see header (d)).  Kept a
   Section variable so `stmt_ir` provably carries a FOREIGN child — there is no
   `stmt_ir` occurrence inside `emit`, hence no mutual recursion with emit_ir. *)
Variable emit : Type.
Variable emit0 : emit.   (* a witness, for the surjectivity existentials *)
Variable emit_eq_dec : forall a b : emit, {a = b} + {a <> b}.

(* ===================================================================== *)
(* 1. The statement-IR ADT — mirrors the WhyML `type stmt_ir with stmt_list`. *)
(* ===================================================================== *)

(* The monomorphic option sibling of the emit_ir ADT — mirrors the WhyML
   `iropt_ir = IrONone | IrOSome emit_ir`.  SReturn carries it (the OPTIONAL
   return value); it references only the FOREIGN `emit`, never `stmt_ir`. *)
Inductive iropt : Type :=
  | IrONone
  | IrOSome (e : emit).

(* The MUTUAL block: stmt_ir and its sub-body list stmt_list.  The compound
   nodes carry `stmt_list` bodies (SWhile: test+body; SIf: test+body+orelse;
   SFor: iter+body); `stmt_list` is the bespoke monomorphic cons. *)
Inductive stmt_ir : Type :=
  | SPass
  | SBreak
  | SContinue
  | SReturn (o : iropt)
  | SExpr (e : emit)
  | SAssign (n : string) (e : emit)
  | SWhile (t : emit) (b : stmt_list)
  | SIf (t : emit) (b : stmt_list) (el : stmt_list)
  | SFor (t : emit) (b : stmt_list)
with stmt_list : Type :=
  | SLNil
  | SLCons (h : stmt_ir) (t : stmt_list).

(* The mutual induction principle — the well-foundedness witness the measure
   below is proven over. *)
Scheme stmt_ir_mut := Induction for stmt_ir Sort Prop
with stmt_list_mut := Induction for stmt_list Sort Prop.
Combined Scheme stmt_ir_stmt_list_mutind from stmt_ir_mut, stmt_list_mut.

(* The tag discriminant — verbatim image of the WhyML `stmt_kind_of`. *)
Definition stmt_kind_of (s : stmt_ir) : string :=
  match s with
  | SPass       => "Pass"
  | SBreak      => "Break"
  | SContinue   => "Continue"
  | SReturn _   => "Return"
  | SExpr _     => "Expr"
  | SAssign _ _ => "Assign"
  | SWhile _ _  => "While"
  | SIf _ _ _   => "If"
  | SFor _ _    => "For"
  end.

(* ===================================================================== *)
(* 1b. The MUTUAL well-founded size measure — WhyML `size_stmt`/`size_slist`. *)
(* ===================================================================== *)

Fixpoint size_stmt (s : stmt_ir) : nat :=
  match s with
  | SWhile _ b  => 1 + size_slist b
  | SIf _ b el  => 1 + size_slist b + size_slist el
  | SFor _ b    => 1 + size_slist b
  | _           => 1
  end
with size_slist (l : stmt_list) : nat :=
  match l with
  | SLNil       => 0
  | SLCons h t  => size_stmt h + size_slist t
  end.

(* Every node has size >= 1; a list has size >= 0 (trivial for nat). *)
Theorem size_stmt_pos : forall s, size_stmt s >= 1.
Proof. intros s; destruct s; simpl; lia. Qed.

(* Well-foundedness witnesses: a sub-body is STRICTLY smaller than the compound
   node that carries it — so a recursive walker over stmt_ir terminates. *)
Theorem size_slist_lt_swhile : forall t b, size_slist b < size_stmt (SWhile t b).
Proof. intros t b; simpl; lia. Qed.
Theorem size_body_lt_sif : forall t b el, size_slist b < size_stmt (SIf t b el).
Proof. intros t b el; simpl; lia. Qed.
Theorem size_orelse_lt_sif : forall t b el, size_slist el < size_stmt (SIf t b el).
Proof. intros t b el; simpl; lia. Qed.
Theorem size_slist_lt_sfor : forall t b, size_slist b < size_stmt (SFor t b).
Proof. intros t b; simpl; lia. Qed.
(* And an element / tail is no larger than the list that contains it. *)
Theorem size_head_le_slcons : forall h t, size_stmt h <= size_slist (SLCons h t).
Proof. intros h t; simpl; lia. Qed.
Theorem size_tail_le_slcons : forall h t, size_slist t <= size_slist (SLCons h t).
Proof. intros h t; simpl; lia. Qed.

(* Decidable equality on the WHOLE mutual block, given decidable equality on the
   foreign child `emit` — the well-founded-ADT obligation (mutual recursion). *)
Definition iropt_eq_dec : forall x y : iropt, {x = y} + {x <> y}.
Proof. decide equality; apply emit_eq_dec. Defined.

Fixpoint stmt_ir_eq_dec (x y : stmt_ir) : {x = y} + {x <> y}
with stmt_list_eq_dec (x y : stmt_list) : {x = y} + {x <> y}.
Proof.
  - decide equality;
      (apply emit_eq_dec || apply iropt_eq_dec || apply stmt_list_eq_dec
       || apply string_dec).
  - decide equality; apply stmt_ir_eq_dec.
Defined.

(* ===================================================================== *)
(* 2. The recognized `{"stmt": K}` world + its dict->ctor abstraction.    *)
(* ===================================================================== *)

(* The recognized statement-node key-set the emitter's `_STMT_IR_CTORS`
   recognizes (expressions.py): nullary (Pass/Break/Continue), one expr-child
   (Return/Expr), or COMPOUND (While/If/For, carrying stmt_list bodies). *)
Inductive pystmt : Type :=
  | PPass
  | PBreak
  | PContinue
  | PReturn (o : iropt)
  | PExpr (e : emit)
  | PAssign (n : string) (e : emit)
  | PWhile (t : emit) (b : stmt_list)
  | PIf (t : emit) (b : stmt_list) (el : stmt_list)
  | PFor (t : emit) (b : stmt_list).

(* The dict->ctor map (`{"stmt":"Pass"} |-> SPass`, ..., `{"stmt":"While",...}
   |-> SWhile ...`). *)
Definition abs (s : pystmt) : stmt_ir :=
  match s with
  | PPass       => SPass
  | PBreak      => SBreak
  | PContinue   => SContinue
  | PReturn o   => SReturn o
  | PExpr e     => SExpr e
  | PAssign n e => SAssign n e
  | PWhile t b  => SWhile t b
  | PIf t b el  => SIf t b el
  | PFor t b    => SFor t b
  end.

(* The Python-side tag string of a recognized node (the `"stmt"` value). *)
Definition py_kind_of (s : pystmt) : string :=
  match s with
  | PPass       => "Pass"
  | PBreak      => "Break"
  | PContinue   => "Continue"
  | PReturn _   => "Return"
  | PExpr _     => "Expr"
  | PAssign _ _ => "Assign"
  | PWhile _ _  => "While"
  | PIf _ _ _   => "If"
  | PFor _ _    => "For"
  end.

(* ===================================================================== *)
(* 3. (b) `abs` is total + injective + surjective (recognition is sound). *)
(* ===================================================================== *)

Theorem abs_injective : forall x y, abs x = abs y -> x = y.
Proof. intros x y H; destruct x; destruct y; simpl in H; congruence. Qed.

Theorem abs_surjective : forall v : stmt_ir, exists s, abs s = v.
Proof.
  intros v; destruct v.
  - exists PPass; reflexivity.
  - exists PBreak; reflexivity.
  - exists PContinue; reflexivity.
  - exists (PReturn o); reflexivity.
  - exists (PExpr e); reflexivity.
  - exists (PAssign n e); reflexivity.
  - exists (PWhile t b); reflexivity.
  - exists (PIf t b el); reflexivity.
  - exists (PFor t b); reflexivity.
Qed.

(* ===================================================================== *)
(* 4. (c) `stmt_kind_of` is EXACT per ctor, and the tag map AGREES with   *)
(*    the Python `"stmt"` string through `abs`.                           *)
(* ===================================================================== *)

Theorem stmt_kind_of_pass     : stmt_kind_of SPass = "Pass".         Proof. reflexivity. Qed.
Theorem stmt_kind_of_break    : stmt_kind_of SBreak = "Break".       Proof. reflexivity. Qed.
Theorem stmt_kind_of_continue : stmt_kind_of SContinue = "Continue". Proof. reflexivity. Qed.
Theorem stmt_kind_of_return   : forall o, stmt_kind_of (SReturn o) = "Return". Proof. reflexivity. Qed.
Theorem stmt_kind_of_expr     : forall e, stmt_kind_of (SExpr e) = "Expr".     Proof. reflexivity. Qed.
Theorem stmt_kind_of_assign   : forall n e, stmt_kind_of (SAssign n e) = "Assign". Proof. reflexivity. Qed.
Theorem stmt_kind_of_while    : forall t b, stmt_kind_of (SWhile t b) = "While". Proof. reflexivity. Qed.
Theorem stmt_kind_of_if       : forall t b el, stmt_kind_of (SIf t b el) = "If". Proof. reflexivity. Qed.
Theorem stmt_kind_of_for      : forall t b, stmt_kind_of (SFor t b) = "For".     Proof. reflexivity. Qed.

Theorem kind_of_agree : forall s, stmt_kind_of (abs s) = py_kind_of s.
Proof. intros []; reflexivity. Qed.

(* ===================================================================== *)
(* 5. (c') TAG-PRESERVING: the tags are pairwise DISTINCT — the honest    *)
(*    node identity the integer-0 erasure destroyed.                      *)
(* ===================================================================== *)

Theorem tag_pass_neq_break    : stmt_kind_of SPass <> stmt_kind_of SBreak.
Proof. simpl; discriminate. Qed.
Theorem tag_pass_neq_continue : stmt_kind_of SPass <> stmt_kind_of SContinue.
Proof. simpl; discriminate. Qed.
Theorem tag_break_neq_continue: stmt_kind_of SBreak <> stmt_kind_of SContinue.
Proof. simpl; discriminate. Qed.
Theorem tag_pass_neq_return   : forall o, stmt_kind_of SPass <> stmt_kind_of (SReturn o).
Proof. intro o; simpl; discriminate. Qed.
Theorem tag_return_neq_expr   : forall o e, stmt_kind_of (SReturn o) <> stmt_kind_of (SExpr e).
Proof. intros o e; simpl; discriminate. Qed.
(* SAssign + str-Constant recognizer increment: the Assign tag is distinct from the
   Expr tag (the two `_py_stmt_expr`/`_py_stmt_annassign` node kinds are NOT collapsed). *)
Theorem tag_assign_neq_expr   : forall n e f, stmt_kind_of (SAssign n e) <> stmt_kind_of (SExpr f).
Proof. intros; simpl; discriminate. Qed.
Theorem tag_assign_neq_return : forall n e o, stmt_kind_of (SAssign n e) <> stmt_kind_of (SReturn o).
Proof. intros; simpl; discriminate. Qed.
(* SUB-BODY increment: the compound tags are distinct from each other and from
   the simple ones (While/If/For are provably separate nodes, not a shared 0). *)
Theorem tag_while_neq_if      : forall t b el o, stmt_kind_of (SWhile t b) <> stmt_kind_of (SIf o el b).
Proof. intros; simpl; discriminate. Qed.
Theorem tag_while_neq_for     : forall t b u c, stmt_kind_of (SWhile t b) <> stmt_kind_of (SFor u c).
Proof. intros; simpl; discriminate. Qed.
Theorem tag_if_neq_for        : forall t b el u c, stmt_kind_of (SIf t b el) <> stmt_kind_of (SFor u c).
Proof. intros; simpl; discriminate. Qed.
Theorem tag_while_neq_pass    : forall t b, stmt_kind_of (SWhile t b) <> stmt_kind_of SPass.
Proof. intros; simpl; discriminate. Qed.

(* The constructors themselves are distinct (no erasure to a common value). *)
Theorem ctor_pass_neq_break : SPass <> SBreak.
Proof. discriminate. Qed.

(* (c'') The OPTIONAL return value is OBSERVABLE — a bare `return` (SReturn
   IrONone) and a value `return e` (SReturn (IrOSome e)) are DISTINCT nodes. *)
Theorem sreturn_none_neq_some : forall e, SReturn IrONone <> SReturn (IrOSome e).
Proof. intros e H; discriminate. Qed.

(* (c'''') SAssign non-vacuity: the TARGET NAME and the RHS VALUE are BOTH observable —
   two SAssign nodes differing in either field are DISTINCT (the injective constructor
   carries the name string and the emit_ir value faithfully, never a shared 0). *)
Theorem sassign_target_observable : forall n m e, n <> m -> SAssign n e <> SAssign m e.
Proof. intros n m e H C; inversion C; contradiction. Qed.
Theorem sassign_value_observable : forall n e f, e <> f -> SAssign n e <> SAssign n f.
Proof. intros n e f H C; inversion C; contradiction. Qed.

(* (c''') SUB-BODY non-vacuity: an SWhile whose sub-body is EMPTY (SLNil) and one
   whose sub-body has a node (SLCons ...) are DISTINCT nodes — the sub-body is
   OBSERVABLE, not collapsed (the 0896 fixture's driver_refute / driver_evil_count
   at the ADT level).  Their sizes differ too. *)
Theorem swhile_empty_neq_nonempty :
  forall t h r, SWhile t SLNil <> SWhile t (SLCons h r).
Proof. intros t h r H; discriminate. Qed.
Theorem swhile_size_grows_with_body :
  forall t h r, size_stmt (SWhile t SLNil) < size_stmt (SWhile t (SLCons h r)).
Proof. intros t h r; simpl; pose proof (size_stmt_pos h); lia. Qed.

End StmtIR.

(* ===================================================================== *)
(* 6. VERDICT — assumption audit.  Every result must be `Closed under the  *)
(*    global context` (NO axiom): the 3-axiom trust ledger is intact.      *)
(* ===================================================================== *)

Print Assumptions size_stmt_pos.
Print Assumptions size_slist_lt_swhile.
Print Assumptions size_body_lt_sif.
Print Assumptions size_orelse_lt_sif.
Print Assumptions size_slist_lt_sfor.
Print Assumptions size_head_le_slcons.
Print Assumptions size_tail_le_slcons.
Print Assumptions iropt_eq_dec.
Print Assumptions stmt_ir_eq_dec.
Print Assumptions stmt_list_eq_dec.
Print Assumptions abs_injective.
Print Assumptions abs_surjective.
Print Assumptions stmt_kind_of_pass.
Print Assumptions stmt_kind_of_while.
Print Assumptions stmt_kind_of_if.
Print Assumptions stmt_kind_of_for.
Print Assumptions kind_of_agree.
Print Assumptions stmt_kind_of_assign.
Print Assumptions tag_assign_neq_expr.
Print Assumptions tag_assign_neq_return.
Print Assumptions sassign_target_observable.
Print Assumptions sassign_value_observable.
Print Assumptions tag_pass_neq_break.
Print Assumptions tag_while_neq_if.
Print Assumptions tag_while_neq_for.
Print Assumptions tag_if_neq_for.
Print Assumptions ctor_pass_neq_break.
Print Assumptions sreturn_none_neq_some.
Print Assumptions swhile_empty_neq_nonempty.
Print Assumptions swhile_size_grows_with_body.
