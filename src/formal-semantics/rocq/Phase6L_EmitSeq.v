(* Phase6L_EmitSeq.v — Sub-α.5: wSeq + recursive emit_stmt
   =========================================================

   Module 6's sequencing is INLINED into every per-statement
   handler: each handler returns `code ++ ";\n" ++ rest_code`
   where `rest_code = _stmts_to_whyml(rest, ...)` (statements.py:
   1042). There is no separate Seq handler; sequencing is the
   list-traversal pattern of `_stmts_to_whyml`.

   In the formal model, `gen` produces `WSeq w1 w2` for `SSeq s1
   s2`, so the formal Seq node IS explicit. The correspondence is
   that the formal Seq emission is `emit w1 ++ ";\n" ++ emit w2` —
   exactly the recursive concatenation pattern.

   This file introduces:

     - `emit_stmt_full : assign_state → whyml_stmt → string` —
       a Fixpoint subsuming the per-construct dispatches from
       Sub-α.1 through Sub-α.4, with WSeq as the recursive arm.
     - `acceptable_seq_emissions` — singleton containing the
       recursive concatenation.
     - `emit_seq_correct` — proved by rfl.

   The previous state-aware dispatches (`emit_stmt_s`,
   `emit_stmt_s2`, `emit_stmt_s4`) are non-recursive Definitions
   from before WSeq was added. `emit_stmt_full` is the unified
   recursive successor.

   Python source: src/pycsl/module6_whyml/statements.py:1042
*)

Require Import String List ZArith Ascii.
Require Import Phase1_AST.
Require Import Phase6_WhyML.
Require Import Phase6d_StmtGen.
Require Import Phase6L_EmitStmt.
Require Import Phase6L_EmitAssign.
Require Import Phase6L_EmitAugAssign.
Require Import Phase6L_EmitArraySet.

Import ListNotations.
Open Scope string_scope.

(* The newline-separator used between statements in a sequence. *)
Definition seq_sep : string := ";" ++ String "010" "".

(* ===== emit_stmt_full: recursive state-aware emission =====

   Fixpoint over whyml_stmt. Each fully-implemented constructor
   delegates to its per-construct emit function from earlier
   Sub-α files. WSeq is the recursive arm. *)

Fixpoint emit_stmt_full (s : assign_state) (ws : whyml_stmt) : string :=
  match ws with
  | WSkip                  => "()"
  | WAssign x e            => emit_assign s x e
  | WAugAssign x op e      => emit_aug_assign x op e
  | WArraySet arr i v      => emit_array_set arr i v
  | WSeq w1 w2             => emit_stmt_full s w1 ++ seq_sep
                                ++ emit_stmt_full s w2
  (* Stubs for pending Sub-α.6 through Sub-α.13.
     Each will be replaced by `emit_<construct> ...` in its PR. *)
  | WIf _ _ _              => ""
  | WWhile _ _ _ _         => ""
  | WRaise _               => ""
  | WTryCatch _ _ _        => ""
  | WGhostDecl _ _ _       => ""
  | WGhostAssign _ _ _ _   => ""
  | WLabel _               => ""
  | WAssert _ _            => ""
  | WAssume _              => ""
  end.

(* ===== acceptable_seq_emissions =====

   Module 6 emits sequence as `code1 ;\n code2`. The acceptable
   set is a singleton (the only surface form). *)

Definition acceptable_seq_emissions
           (s : assign_state) (w1 w2 : whyml_stmt) : list string :=
  [ emit_stmt_full s w1 ++ seq_sep ++ emit_stmt_full s w2 ].

(* ===== Correctness theorem ===== *)

Theorem emit_seq_correct :
  forall s w1 w2,
    In (emit_stmt_full s (WSeq w1 w2)) (acceptable_seq_emissions s w1 w2).
Proof.
  intros s w1 w2.
  unfold acceptable_seq_emissions. simpl. left. reflexivity.
Qed.

(* Tie-in to gen: gen (SSeq s1 s2) = WSeq (gen s1) (gen s2). *)

Theorem emit_stmt_full_seq_correct :
  forall s s1 s2,
    In (emit_stmt_full s (gen (SSeq s1 s2)))
       (acceptable_seq_emissions s (gen s1) (gen s2)).
Proof.
  intros. simpl. apply emit_seq_correct.
Qed.

(* ===== Compatibility lemmas =====

   The full fixpoint subsumes the earlier per-Sub-α state-aware
   definitions. We re-state the correctness theorems against
   `emit_stmt_full` so downstream consumers can use the unified
   function. *)

Theorem emit_stmt_full_skip :
  forall s, emit_stmt_full s WSkip = "()".
Proof. reflexivity. Qed.

Theorem emit_stmt_full_assign_correct :
  forall s x e,
    In (emit_stmt_full s (WAssign x e)) (acceptable_assign_emissions s x e).
Proof.
  intros. simpl. apply emit_assign_correct.
Qed.

Theorem emit_stmt_full_aug_assign_correct :
  forall s x op e,
    In (emit_stmt_full s (WAugAssign x op e))
       (acceptable_aug_assign_emissions x op e).
Proof.
  intros. simpl. apply emit_aug_assign_correct.
Qed.

Theorem emit_stmt_full_array_set_correct :
  forall s arr i v,
    In (emit_stmt_full s (WArraySet arr i v))
       (acceptable_array_set_emissions arr i v).
Proof.
  intros. simpl. apply emit_array_set_correct.
Qed.
