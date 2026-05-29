(* Phase6L_EmitAugAssign.v — Sub-α.3: full state coverage for wAugAssign
   =====================================================================

   Module 6's `_handle_augassign_stmt` (statements.py:783-827) has
   THREE branches keyed on the operator and target type:

     1. raw_op ∈ {&, |, ^, <<, >>, **}    → bitwise abstract op call
     2. raw_op == "+" AND target ∈ array_locals/array_params
                                          → array_extend (concat)
     3. default                           → `target := !target op val`

   On inputs of formal `binop` type (OpAdd, OpSub, OpMul, OpDiv):

     - Branch 1: UNREACHABLE — formal `binop` has no bitwise variants
     - Branch 2: UNREACHABLE — formal `expr` cannot populate
                 array_locals (no ArrayLit), and formal AST doesn't
                 expose array-typed parameter classification
     - Branch 3: the only reachable branch

   So the acceptable set is a singleton (modulo `op_translate`
   mapping):

       target ++ " := !" ++ target ++ " " ++ op_translate(raw_op)
              ++ " " ++ pretty_expr val

   With `op_translate` mapping:
     OpAdd → "+"    OpSub → "-"
     OpMul → "*"    OpDiv → "div"   (per identifiers.py:OP_MAP)

   Note: this is the statement-level operator translation, NOT the
   expression-level. At expression level (inside pretty_expr's BinOp
   arm), OpDiv in body context wraps with `pycsl_div` and possibly
   no_exception assert — see Sub-α.2's "presentational gap" note.

   Python source: src/pycsl/module6_whyml/statements.py:783-827
                  src/pycsl/module6_whyml/identifiers.py:OP_MAP
*)

Require Import String List ZArith.
Require Import Phase1_AST.
Require Import Phase6_WhyML.
Require Import Phase6d_StmtGen.
Require Import Phase6L_EmitStmt.
Require Import Phase6L_EmitAssign.

Import ListNotations.
Open Scope string_scope.

(* ===== Statement-level operator translation =====

   Mirrors Python's `op_translate(raw_op)` for the operators that
   appear in `_handle_augassign_stmt`'s default branch on formal
   `binop`. *)

Definition op_translate_aug (op : binop) : string :=
  match op with
  | OpAdd => "+"
  | OpSub => "-"
  | OpMul => "*"
  | OpDiv => "div"   (* identifiers.py:OP_MAP["/"] = "div" *)
  | OpMod => "mod"
  end.

(* ===== emit_aug_assign: formal model of _handle_augassign_stmt =====

   For inputs on formal `binop`, only the default branch fires.
   Emits `target := !target op val`.

   Python correspondent: src/pycsl/module6_whyml/statements.py:824
*)

Definition emit_aug_assign (x : ident) (op : binop) (e : expr) : string :=
  x ++ " := !" ++ x ++ " " ++ op_translate_aug op ++ " " ++ pretty_expr e.

(* ===== acceptable_aug_assign_emissions =====

   On formal `binop`, the acceptable set is a singleton — the
   default-branch form. Bitwise and array-extend variants are
   excluded with rationale documented in the file header. *)

Definition acceptable_aug_assign_emissions
           (x : ident) (op : binop) (e : expr) : list string :=
  [ x ++ " := !" ++ x ++ " " ++ op_translate_aug op ++ " " ++ pretty_expr e ].

(* ===== Correctness theorem ===== *)

Theorem emit_aug_assign_correct :
  forall x op e,
    In (emit_aug_assign x op e) (acceptable_aug_assign_emissions x op e).
Proof.
  intros x op e.
  unfold emit_aug_assign, acceptable_aug_assign_emissions.
  simpl. left. reflexivity.
Qed.

(* ===== Tie-in to gen =====

   gen (SAugAssign x op e) = WAugAssign x op e by definition. Extend
   the state-aware emit_stmt_s to handle WAugAssign. *)

Definition emit_stmt_s2 (s : assign_state) (ws : whyml_stmt) : string :=
  match ws with
  | WSkip              => "()"
  | WAssign x e        => emit_assign s x e
  | WAugAssign x op e  => emit_aug_assign x op e
  | _                  => emit_stmt ws
  end.

Theorem emit_stmt_s2_aug_assign_correct :
  forall s x op e,
    In (emit_stmt_s2 s (gen (SAugAssign x op e)))
       (acceptable_aug_assign_emissions x op e).
Proof.
  intros s x op e. simpl. apply emit_aug_assign_correct.
Qed.

(* Preserve compatibility with wSkip and wAssign through the new dispatch. *)

Lemma emit_stmt_s2_skip : forall s, emit_stmt_s2 s (gen SSkip) = "()".
Proof. reflexivity. Qed.

Theorem emit_stmt_s2_assign_correct :
  forall s x e,
    In (emit_stmt_s2 s (gen (SAssign x e))) (acceptable_assign_emissions s x e).
Proof.
  intros s x e. simpl. apply emit_assign_correct.
Qed.
