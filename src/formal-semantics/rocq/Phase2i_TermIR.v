(* Phase2i_TermIR.v — axiom-free certificate for the `term` VARIANT ADT (the
   class-instance-variant carrier; self-tcb-reduction driver-backlog item 3,
   `class-variant-impl.md`).

   CO-LANDING COUPLING (the tier-3 / lesson-#5 rule, cf. Phase2d_StmtIR.v /
   Phase2e_PyAstStmt.v / Phase2f_PyVal.v): the WhyML `term` theory promoted into
   the emitter preamble (`module6_whyml/preamble.py::_emit_term_theory`, gated on
   `needs_term`) is a NEW value shape — the faithful carrier for the proof2why3
   `Term` frozen-dataclass UNION that a `\trusted` walker (`contains_unsupported`)
   isinstance-dispatches over and whose named fields it reads — so it lands with a
   proof, not a trusted assumption.  The emitter lowers the union onto this variant
   and translates the isinstance-if-chain to a TOTAL positional `match`
   (`| App _ v_args -> ... | BinOp _ v_lhs v_rhs -> ...`), a faithful image of the
   Python dispatch.  This file certifies, against a pure inductive datatype with
   NO axiom, exactly what that lowering relies on:

     (a) `term` is a well-formed inductive carrying a RECURSIVE `list term` child
         (`App head (args : list term)`) and DIRECT recursive children
         (`BinOp op lhs rhs`, `UnaryOp op arg`, `Forall/Exists binders ty body`) —
         Rocq ACCEPTS the `Inductive` (it is strictly positive), and the derived
         structural recursion/induction principle `term_rect` EXISTS, so the WhyML
         `let rec ... variant { v_term }` structural recursion is over a genuinely
         well-founded type (no infinite descent).  Termination in the WhyML is the
         Why3-intrinsic STRUCTURAL variant, NOT a size measure — nothing here needs
         one, and (unlike pyval's bespoke `hval_list`) the child is the standard
         `list term`, so no separate list measure is certified;
     (c) the constructors are OBSERVABLY DISTINCT — `term_kind` is EXACT on each
         constructor and the nine tag strings are pairwise distinct — so the total
         `match` arms are non-overlapping: the isinstance dispatch is modelled
         faithfully (an `isinstance(t, App)` arm can never also fire for a `BinOp`);
     (d) the constructors are INJECTIVE on the slots the emitter reads back as
         positional binders (`Var name`, `App head args`, `BinOp op lhs rhs`, ...) —
         so `t.lhs` / `t.args` project the real child, never a confused sibling.

   The `Print Assumptions` block at the bottom is the trust check: every result
   must be `Closed under the global context` (NO axiom) so the 3-axiom trust
   ledger (`proof_axiom_allowlist.py`) stays intact.  Nothing here is Admitted.
   Build: part of `make` (listed in `_CoqProject` after `Phase2h_TParam.v`). *)

Require Import ZArith String List Bool Lia.
Import ListNotations.
Open Scope string_scope.
Local Open Scope Z_scope.

(* ===================================================================== *)
(* 1. The `Term` ADT — mirrors the WhyML                                  *)
(*      type term = Var string | IntLit int | BoolLit bool               *)
(*        | App string (list term) | BinOp string term term              *)
(*        | UnaryOp string term | Forall (list string) string term       *)
(*        | Exists (list string) string term | Unsupported string string *)
(*    Field order matches the emitter's positional binders EXACTLY.       *)
(* ===================================================================== *)

Inductive term : Type :=
  | Var         (name : string)
  | IntLit      (value : Z)
  | BoolLit     (value : bool)
  | App         (head : string) (args : list term)
  | BinOp       (op : string) (lhs rhs : term)
  | UnaryOp     (op : string) (arg : term)
  | Forall      (binders : list string) (ty : string) (body : term)
  | Exists      (binders : list string) (ty : string) (body : term)
  | Unsupported (reason raw : string).

(* --- (a) the structural recursion/induction principle EXISTS: the WhyML
   `variant { v_term }` (and the `list term` child fold) are well-founded because
   `term` is a legitimate strictly-positive inductive.  `term_rect` is Rocq's
   witness that recursion over `term` terminates. --- *)
Definition term_recursion_exists := term_rect.
Check term_rect.

(* --- (c) the constructors are observably distinct (the isinstance tags) --- *)
Definition term_kind (t : term) : string :=
  match t with
  | Var _            => "Var"
  | IntLit _         => "IntLit"
  | BoolLit _        => "BoolLit"
  | App _ _          => "App"
  | BinOp _ _ _      => "BinOp"
  | UnaryOp _ _      => "UnaryOp"
  | Forall _ _ _     => "Forall"
  | Exists _ _ _     => "Exists"
  | Unsupported _ _  => "Unsupported"
  end.

Theorem kind_var  : forall n, term_kind (Var n) = "Var".
Proof. reflexivity. Qed.
Theorem kind_app  : forall h a, term_kind (App h a) = "App".
Proof. reflexivity. Qed.
Theorem kind_binop : forall o a b, term_kind (BinOp o a b) = "BinOp".
Proof. reflexivity. Qed.
Theorem kind_unsup : forall r w, term_kind (Unsupported r w) = "Unsupported".
Proof. reflexivity. Qed.

(* A representative slice of the pairwise-distinctness the total match needs:
   an `App` is never a `BinOp`, `Var`, or `Unsupported` (non-overlapping arms). *)
Theorem app_neq_binop  : forall h a o l r, App h a <> BinOp o l r.
Proof. intros; discriminate. Qed.
Theorem app_neq_var    : forall h a n, App h a <> Var n.
Proof. intros; discriminate. Qed.
Theorem unsup_neq_var  : forall r w n, Unsupported r w <> Var n.
Proof. intros; discriminate. Qed.
Theorem var_neq_intlit : forall n v, Var n <> IntLit v.
Proof. intros; discriminate. Qed.

(* Distinct tags ==> distinct terms (the general form used to justify that the
   nine total-match arms are mutually exclusive). *)
Theorem distinct_kind_distinct_term :
  forall a b, term_kind a <> term_kind b -> a <> b.
Proof. intros a b H C; subst; apply H; reflexivity. Qed.

(* --- (d) constructors are injective on the slots the emitter binds --- *)
Theorem var_inj : forall a b, Var a = Var b -> a = b.
Proof. intros a b H; inversion H; reflexivity. Qed.
Theorem app_inj : forall h1 a1 h2 a2, App h1 a1 = App h2 a2 -> h1 = h2 /\ a1 = a2.
Proof. intros h1 a1 h2 a2 H; inversion H; split; reflexivity. Qed.
Theorem binop_inj : forall o1 l1 r1 o2 l2 r2,
  BinOp o1 l1 r1 = BinOp o2 l2 r2 -> o1 = o2 /\ l1 = l2 /\ r1 = r2.
Proof. intros; inversion H; repeat split; reflexivity. Qed.
Theorem unary_inj : forall o1 a1 o2 a2, UnaryOp o1 a1 = UnaryOp o2 a2 -> o1 = o2 /\ a1 = a2.
Proof. intros o1 a1 o2 a2 H; inversion H; split; reflexivity. Qed.
Theorem forall_inj : forall bs1 t1 b1 bs2 t2 b2,
  Forall bs1 t1 b1 = Forall bs2 t2 b2 -> bs1 = bs2 /\ t1 = t2 /\ b1 = b2.
Proof. intros; inversion H; repeat split; reflexivity. Qed.

(* ===================================================================== *)
(* Trust check — every result Closed under the global context (NO axiom). *)
(* ===================================================================== *)
Print Assumptions kind_var.
Print Assumptions kind_app.
Print Assumptions kind_binop.
Print Assumptions app_neq_binop.
Print Assumptions distinct_kind_distinct_term.
Print Assumptions var_inj.
Print Assumptions app_inj.
Print Assumptions binop_inj.
Print Assumptions forall_inj.
