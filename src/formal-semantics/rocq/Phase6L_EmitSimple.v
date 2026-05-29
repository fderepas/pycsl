(* Phase6L_EmitSimple.v — Sub-α.8/α.12/α.13: wRaise, wLabel, wAssert
   ===================================================================

   Three simple single-line constructs grouped in one file:

   - wRaise: Module 6 emits `raise <exc_name>` per the exception
     variant. Source: statements.py:1098-1100 (raise),
     1117-1119 (break), 1089-1091 (continue).

   - wLabel: Module 6 emits `label L in <rest>` where the label
     scopes over the rest of the block. Source: statements.py:
     1051-1056.

   - wAssert: Module 6 maps Python `assert` to `()` (no-op) per
     statements.py:1093-1096. The formal `WAssert cond msg`
     constructor's Module 6 correspondent is the empty unit
     expression. This is a divergence between the formal model
     (where WAssert carries semantic content) and Module 6 (which
     erases it). Documented for trust-chain readers.

   Python source: src/pycsl/module6_whyml/statements.py
*)

Require Import String List ZArith Ascii.
Require Import Phase1_AST.
Require Import Phase6_WhyML.
Require Import Phase6d_StmtGen.
Require Import Phase6L_EmitStmt.
Require Import Phase6L_EmitAssign.
Require Import Phase6L_EmitAugAssign.
Require Import Phase6L_EmitArraySet.
Require Import Phase6L_EmitSeq.

Import ListNotations.
Open Scope string_scope.

(* ===== Sub-α.8: wRaise ===== *)

(* Maps the formal whyml_exc to the Python-emitted exception name. *)
Definition exc_to_string (exc : whyml_exc) : string :=
  match exc with
  | ExcReturn       => "PyCSL_Return"   (* internal: SReturn lifts via raise *)
  | ExcBreak        => "PyCSL_Break"    (* statements.py:1119 *)
  | ExcContinue     => "PyCSL_Continue" (* statements.py:1091 *)
  | ExcNamed name   => name             (* statements.py:1099-1100 *)
  end.

Definition emit_raise (exc : whyml_exc) : string :=
  "raise " ++ exc_to_string exc.

Definition acceptable_raise_emissions (exc : whyml_exc) : list string :=
  [ "raise " ++ exc_to_string exc ].

Theorem emit_raise_correct :
  forall exc, In (emit_raise exc) (acceptable_raise_emissions exc).
Proof.
  intros. unfold emit_raise, acceptable_raise_emissions.
  simpl. left. reflexivity.
Qed.

(* ===== Sub-α.12: wLabel =====

   Module 6 emits `label L in\n<rest>` where rest is the remainder
   of the block. In the formal model, `WLabel L` is a standalone
   statement; the "rest" of the block is the right-hand side of a
   surrounding WSeq node. So `WLabel L` alone emits just the
   `label L in` prefix — the rest comes from the WSeq composition.

   This is a *structural* difference between Module 6's inline
   sequencing and the formal model's explicit WSeq:
     Module 6: label L in <rest>
     Formal:   WSeq (WLabel L) <rest>  → "label L in\n" ++ emit <rest>

   The composition aligns at the WSeq level (see emit_stmt_full's
   wSeq case in Phase6L_EmitSeq.v). *)

Definition emit_label (L : ident) : string :=
  "label " ++ L ++ " in".

Definition acceptable_label_emissions (L : ident) : list string :=
  [ "label " ++ L ++ " in" ].

Theorem emit_label_correct :
  forall L, In (emit_label L) (acceptable_label_emissions L).
Proof.
  intros. unfold emit_label, acceptable_label_emissions.
  simpl. left. reflexivity.
Qed.

(* ===== Sub-α.13: wAssert =====

   Module 6 erases Python `assert` (statements.py:1093-1096):
     `code = f'{indent}()'`
   The acceptable surface is `()`. The formal `WAssert cond msg`
   carries content but Module 6's output ignores it. *)

Definition emit_assert (cond : contract_expr) (msg : string) : string :=
  "()".

Definition acceptable_assert_emissions
           (cond : contract_expr) (msg : string) : list string :=
  [ "()" ].

Theorem emit_assert_correct :
  forall cond msg,
    In (emit_assert cond msg) (acceptable_assert_emissions cond msg).
Proof.
  intros. unfold emit_assert, acceptable_assert_emissions.
  simpl. left. reflexivity.
Qed.

(* ===== Extended fixpoint covering wRaise / wLabel / wAssert =====

   Replaces the "" stubs in `emit_stmt_full` for these three
   constructors. *)

Fixpoint emit_stmt_full2 (s : assign_state) (ws : whyml_stmt) : string :=
  match ws with
  | WSkip                  => "()"
  | WAssign x e            => emit_assign s x e
  | WAugAssign x op e      => emit_aug_assign x op e
  | WArraySet arr i v      => emit_array_set arr i v
  | WSeq w1 w2             => emit_stmt_full2 s w1 ++ seq_sep
                                ++ emit_stmt_full2 s w2
  | WRaise exc             => emit_raise exc
  | WLabel L               => emit_label L
  | WAssert cond msg       => emit_assert cond msg
  | WAssume _              => "()"  (* not used at this layer *)
  (* Pending Sub-α.6/.7/.9/.10/.11: wIf, wWhile, wTryCatch, wGhostDecl, wGhostAssign *)
  | WIf _ _ _              => ""
  | WWhile _ _ _ _         => ""
  | WTryCatch _ _ _        => ""
  | WGhostDecl _ _ _       => ""
  | WGhostAssign _ _ _ _   => ""
  end.

Theorem emit_stmt_full2_raise_correct :
  forall s exc,
    In (emit_stmt_full2 s (WRaise exc)) (acceptable_raise_emissions exc).
Proof. intros. simpl. apply emit_raise_correct. Qed.

Theorem emit_stmt_full2_label_correct :
  forall s L,
    In (emit_stmt_full2 s (WLabel L)) (acceptable_label_emissions L).
Proof. intros. simpl. apply emit_label_correct. Qed.

Theorem emit_stmt_full2_assert_correct :
  forall s cond msg,
    In (emit_stmt_full2 s (WAssert cond msg))
       (acceptable_assert_emissions cond msg).
Proof. intros. simpl. apply emit_assert_correct. Qed.

(* Tie-ins to gen for SRaise/SLabel/SAssert. *)

Theorem emit_stmt_full2_sraise_correct :
  forall s exc,
    In (emit_stmt_full2 s (gen (SRaise exc)))
       (acceptable_raise_emissions (ExcNamed exc)).
Proof.
  intros s exc.
  change (gen (SRaise exc)) with (WRaise (ExcNamed exc)).
  simpl. left. reflexivity.
Qed.

Theorem emit_stmt_full2_slabel_correct :
  forall s L,
    In (emit_stmt_full2 s (gen (SLabel L))) (acceptable_label_emissions L).
Proof.
  intros s L.
  change (gen (SLabel L)) with (WLabel L).
  simpl. left. reflexivity.
Qed.

Theorem emit_stmt_full2_sassert_correct :
  forall s cond msg,
    In (emit_stmt_full2 s (gen (SAssert cond msg)))
       (acceptable_assert_emissions cond msg).
Proof.
  intros s cond msg.
  change (gen (SAssert cond msg)) with (WAssert cond msg).
  simpl. left. reflexivity.
Qed.
