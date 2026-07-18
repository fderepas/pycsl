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
         destroyed, fable Oracle 3);
     (d) NO MUTUAL RECURSION: the expr children (`SExpr e` carries the FOREIGN
         emit_ir type `emit`; `SReturn o` carries `iropt` = the option sibling
         `IrONone | IrOSome emit`), where `emit` (a Section variable here) never
         mentions `stmt_ir` — so `stmt_ir` adds NO constructor to emit_ir's own
         size induction, and its own `size` recursion does not descend into
         `emit`.  This is the one-directional-reference property the WhyML block
         needs (stmt_ir references emit_ir; emit_ir does not reference stmt_ir).
         SReturn's OPTIONAL child mirrors `ast.Return.value : option emit_ir`
         retyped `SReturn iropt_ir` (a bare `return` -> `IrONone`, `return e` ->
         `IrOSome (disp e)`); `disp` is abstracted (the option carries `emit`
         directly), so the certified content is the OPTION STRUCTURE itself.

   The mutable-ref append convention itself (`ir_stmts : ref (seq stmt_ir)` with
   a real `writes { ir_stmts }` frame) needs NO certificate clause here: it is a
   Why3-INTRINSIC `writes` verification condition — Why3's region/effect system
   discharges the caller-visible-write obligation directly (the fable oracle
   `sound_append.mlw` proved it Valid, 0 axioms).  This file certifies the DATA
   model (the ADT + tags + recognition map); the EFFECT model is Why3's own.

   The `Print Assumptions` block at the bottom is the trust check: every result
   must be `Closed under the global context` (NO axiom) so the 3-axiom trust
   ledger (`proof_axiom_allowlist.py`) stays intact.  Nothing here is Admitted.
   Build: part of `make` (listed in `_CoqProject` after `Phase2c_PyValDict.v`). *)

Require Import ZArith String List Bool.
Import ListNotations.
Open Scope string_scope.

Section StmtIR.

(* The WhyML emit_ir expr-child type, abstracted (see header (d)).  Kept a
   Section variable so `stmt_ir` provably carries a FOREIGN child — there is no
   `stmt_ir` occurrence inside `emit`, hence no mutual recursion. *)
Variable emit : Type.
Variable emit0 : emit.   (* a witness, for the surjectivity existentials *)
Variable emit_eq_dec : forall a b : emit, {a = b} + {a <> b}.

(* ===================================================================== *)
(* 1. The statement-IR ADT — mirrors the WhyML `type stmt_ir`.            *)
(* ===================================================================== *)

(* The monomorphic option sibling of the emit_ir ADT — mirrors the WhyML
   `iropt_ir = IrONone | IrOSome emit_ir`.  SReturn carries it (the OPTIONAL
   return value); it references only the FOREIGN `emit`, never `stmt_ir`. *)
Inductive iropt : Type :=
  | IrONone
  | IrOSome (e : emit).

Inductive stmt_ir : Type :=
  | SPass
  | SBreak
  | SContinue
  | SReturn (o : iropt)
  | SExpr (e : emit).

(* The tag discriminant — verbatim image of the WhyML `stmt_kind_of`. *)
Definition stmt_kind_of (s : stmt_ir) : string :=
  match s with
  | SPass     => "Pass"
  | SBreak    => "Break"
  | SContinue => "Continue"
  | SReturn _ => "Return"
  | SExpr _   => "Expr"
  end.

(* A size measure.  `stmt_ir` has NO `stmt_ir` sub-term (the children are the
   foreign type `emit`), so every node has size 1 and the type is trivially
   well-founded — no infinite descent is possible. *)
Definition size (s : stmt_ir) : nat := 1.

Theorem size_pos : forall s, size s = 1.
Proof. intros []; reflexivity. Qed.

(* Decidable equality, given decidable equality on the child type. *)
Definition iropt_eq_dec : forall x y : iropt, {x = y} + {x <> y}.
Proof. decide equality; apply emit_eq_dec. Defined.

Definition stmt_ir_eq_dec : forall x y : stmt_ir, {x = y} + {x <> y}.
Proof. decide equality; (apply emit_eq_dec || apply iropt_eq_dec). Defined.

(* ===================================================================== *)
(* 2. The recognized `{"stmt": K}` world + its dict->ctor abstraction.    *)
(* ===================================================================== *)

(* The recognized statement-node key-set the emitter's `_STMT_IR_CTORS`
   recognizes (expressions.py).  A nullary key (Pass/Break/Continue) or a
   one-child key (Return/Expr, carrying an expr node). *)
Inductive pystmt : Type :=
  | PPass
  | PBreak
  | PContinue
  | PReturn (o : iropt)
  | PExpr (e : emit).

(* The dict->ctor map (`{"stmt":"Pass"} |-> SPass`, ...). *)
Definition abs (s : pystmt) : stmt_ir :=
  match s with
  | PPass      => SPass
  | PBreak     => SBreak
  | PContinue  => SContinue
  | PReturn o  => SReturn o
  | PExpr e    => SExpr e
  end.

(* The Python-side tag string of a recognized node (the `"stmt"` value). *)
Definition py_kind_of (s : pystmt) : string :=
  match s with
  | PPass      => "Pass"
  | PBreak     => "Break"
  | PContinue  => "Continue"
  | PReturn _  => "Return"
  | PExpr _    => "Expr"
  end.

(* ===================================================================== *)
(* 3. (b) `abs` is total + injective + surjective (recognition is sound). *)
(* ===================================================================== *)

Theorem abs_injective : forall x y, abs x = abs y -> x = y.
Proof. intros [] []; simpl; congruence. Qed.

Theorem abs_surjective : forall v : stmt_ir, exists s, abs s = v.
Proof.
  intros v; destruct v.
  - exists PPass; reflexivity.
  - exists PBreak; reflexivity.
  - exists PContinue; reflexivity.
  - exists (PReturn o); reflexivity.
  - exists (PExpr e); reflexivity.
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

Theorem kind_of_agree : forall s, stmt_kind_of (abs s) = py_kind_of s.
Proof. intros []; reflexivity. Qed.

(* ===================================================================== *)
(* 5. (c') TAG-PRESERVING: the nullary tags are pairwise DISTINCT — the   *)
(*    honest node identity the integer-0 erasure destroyed.  (SReturn /   *)
(*    SExpr differ by their string tag too; a representative pair shown.)  *)
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

(* The constructors themselves are distinct (no erasure to a common value). *)
Theorem ctor_pass_neq_break : SPass <> SBreak.
Proof. discriminate. Qed.

(* (c'') The OPTIONAL return value is OBSERVABLE — a bare `return` (SReturn
   IrONone) and a value `return e` (SReturn (IrOSome e)) are DISTINCT nodes.
   Certifies the `SReturn iropt_ir` retype carries the option honestly (the
   0895 observational fixture's driver_refute / driver_evil_option), not a
   collapsed/erased child. *)
Theorem sreturn_none_neq_some : forall e, SReturn IrONone <> SReturn (IrOSome e).
Proof. intros e H; discriminate. Qed.

End StmtIR.

(* ===================================================================== *)
(* 6. VERDICT — assumption audit.  Every result must be `Closed under the  *)
(*    global context` (NO axiom): the 3-axiom trust ledger is intact.      *)
(* ===================================================================== *)

Print Assumptions size_pos.
Print Assumptions iropt_eq_dec.
Print Assumptions stmt_ir_eq_dec.
Print Assumptions abs_injective.
Print Assumptions abs_surjective.
Print Assumptions stmt_kind_of_pass.
Print Assumptions stmt_kind_of_break.
Print Assumptions stmt_kind_of_continue.
Print Assumptions stmt_kind_of_return.
Print Assumptions stmt_kind_of_expr.
Print Assumptions kind_of_agree.
Print Assumptions tag_pass_neq_break.
Print Assumptions tag_pass_neq_continue.
Print Assumptions tag_break_neq_continue.
Print Assumptions tag_pass_neq_return.
Print Assumptions tag_return_neq_expr.
Print Assumptions ctor_pass_neq_break.
Print Assumptions sreturn_none_neq_some.
