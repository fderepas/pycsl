(* Phase6L_EmitArraySet.v — Sub-α.4: wArraySet
   ================================================

   Module 6's `_handle_array_set_stmt` (statements.py:563-657) has
   multiple branches depending on:

     - memory_model (hoare/concurrent vs other)
     - arr.type (Var vs Subscript vs Attribute/FieldGet)
     - var membership (array_locals / dict_locals / symbol_table)
     - no_exception scope (IndexError → assert prepend)

   On a formal `SArraySet arr i v` where `arr : ident` (NOT an
   expression) and `i, v : expr`:

     - Branch (2D-array, arr.type=="Subscript"): UNREACHABLE — formal
       `SArraySet`'s `arr` field is a bare ident, not nested.
     - is_array (var ∈ array_locals etc.): the canonical case for
       well-formed PyCSL programs that produce SArraySet.
       Emission: `arr ++ "[" ++ pretty_expr i ++ "] <- " ++ pretty_expr v`
       Optional no_exception prefix on IndexError: deferred.
     - is_dict: UNREACHABLE on formal expr — requires dict-typed Var.
     - subscript_set fallback (var not classified): could fire for
       unclassified-state inputs. Emission:
         `"subscript_set " ++ arr ++ " " ++ pretty_expr i ++ " " ++ pretty_expr v`
     - heap-model branch (memory_model != hoare/concurrent): out of
       scope; PyCSL's default is hoare or concurrent.

   The acceptable set thus has two elements (is_array form +
   subscript_set fallback), under the assumption memory_model is
   hoare or concurrent.

   Python source: src/pycsl/module6_whyml/statements.py:563-657
*)

Require Import String List ZArith.
Require Import Phase1_AST.
Require Import Phase6_WhyML.
Require Import Phase6d_StmtGen.
Require Import Phase6L_EmitStmt.
Require Import Phase6L_EmitAssign.

Import ListNotations.
Open Scope string_scope.

(* ===== emit_array_set: formal model =====

   Picks the canonical is_array branch. Module 6's actual selection
   depends on var-classification state. *)

Definition emit_array_set (arr : ident) (i v : expr) : string :=
  arr ++ "[" ++ pretty_expr i ++ "] <- " ++ pretty_expr v.

(* ===== acceptable_array_set_emissions =====

   Two surface forms Module 6 may emit for SArraySet arr i v:
   - is_array branch: native WhyML array update syntax
   - subscript_set fallback: abstract subscript_set call

   Both are listed; the formal emit_array_set chooses the first. *)

Definition acceptable_array_set_emissions
           (arr : ident) (i v : expr) : list string :=
  [ arr ++ "[" ++ pretty_expr i ++ "] <- " ++ pretty_expr v ;
    "subscript_set " ++ arr ++ " " ++ pretty_expr i ++ " " ++ pretty_expr v ].

(* ===== Correctness theorem ===== *)

Theorem emit_array_set_correct :
  forall arr i v,
    In (emit_array_set arr i v) (acceptable_array_set_emissions arr i v).
Proof.
  intros arr i v.
  unfold emit_array_set, acceptable_array_set_emissions.
  simpl. left. reflexivity.
Qed.

(* ===== State-aware dispatch ===== *)

Definition emit_stmt_s4 (s : assign_state) (ws : whyml_stmt) : string :=
  match ws with
  | WSkip                  => "()"
  | WAssign x e            => emit_assign s x e
  | WArraySet arr i v      => emit_array_set arr i v
  | _                      => emit_stmt ws
  end.

Theorem emit_stmt_s4_array_set_correct :
  forall s arr i v,
    In (emit_stmt_s4 s (gen (SArraySet arr i v)))
       (acceptable_array_set_emissions arr i v).
Proof.
  intros s arr i v. simpl. apply emit_array_set_correct.
Qed.
