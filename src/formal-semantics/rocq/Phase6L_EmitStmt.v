(* Phase6L_EmitStmt.v — Sub-α pilot
   ================================================

   Pilot for Q2 Sub-α of `closer-to-code.md`: a per-construct
   formalization of Module 6's WhyML string emission.

   This file is the **smallest** entry point of the Sub-α series — it
   formalizes the emission of a single construct (`wSkip`) end-to-end:

   1. Defines `emit_stmt : whyml_stmt -> string`, the formal model of
      what Module 6's emission pipeline (Python:
      `src/pycsl/module6_whyml/statements.py:_stmts_to_whyml`)
      produces for each `whyml_stmt` constructor.

   2. Defines `acceptable_<construct>_emissions` predicates — small
      lists of strings naming the surface-syntax alternatives Module 6
      may emit. For wSkip the set is a singleton; for richer
      constructs (wAssign with `let x = ...` vs `x := ...` vs the
      bool-coerced form) the set has several elements.

   3. Proves `emit_<construct>_correct`: for every well-formed
      `S<Construct>` input, the formal emission `emit_stmt (gen
      (S<Construct> ...))` lies in the acceptable set.

   The pilot demonstrates the methodology end-to-end. Subsequent PRs
   extend `emit_stmt` and add per-construct theorems for the remaining
   14 constructs (wAssign, wAugAssign, wArraySet, wSeq, wIf, wWhile,
   wFor, wTryCatch, wRaise, wReturn, wCriticalSection, wGhost*, wLabel,
   plus expression emission). See `closer-to-code.md` §Quarter 2 for
   the full schedule.

   Trust-chain impact: when all 15 per-construct theorems land,
   `module6_encodes_mlw` (the single Phase 6C axiom) becomes derivable
   from the per-construct theorems plus the extraction-extensional
   claim (Sub-α). The aggregate axiom can then be replaced by a
   composition lemma.

   Python correspondent: see
   `src/pycsl/module6_whyml/statements.py` (dispatch in
   `_stmts_to_whyml` around line 1034) and `expressions.py`
   (expression-emission dispatch).
*)

Require Import String List.
Require Import Phase1_AST.
Require Import Phase6_WhyML.
Require Import Phase6d_StmtGen.

Import ListNotations.
Open Scope string_scope.

(* ===== emit_stmt: formal model of Module 6's WhyML emission =====

   Returns the bare WhyML expression for a statement. Indentation is
   a separate concern handled by the Python `indent` parameter in
   `_stmts_to_whyml`; the formal model captures the indentation-free
   form.

   This pilot defines only the wSkip case fully. Other cases return
   the empty string as a placeholder; subsequent PRs extend the match
   arms one at a time, each accompanied by its own correctness
   theorem (see below). *)

(* Becomes Fixpoint when WSeq's recursive case is implemented in
   Sub-α.5. For now no constructor recurses, so Definition is exact. *)
Definition emit_stmt (ws : whyml_stmt) : string :=
  match ws with
  | WSkip => "()"

  (* --- Pending per-construct PRs (Sub-α.2 through Sub-α.13) ---
     Each placeholder will be replaced with the real emission in a
     dedicated PR. Until then they return "" so the function is
     total; the correctness theorems below only assert wSkip.        *)
  | WAssign _ _              => ""
  | WAugAssign _ _ _         => ""
  | WArraySet _ _ _          => ""
  | WSeq _ _                 => ""
  | WIf _ _ _                => ""
  | WWhile _ _ _ _           => ""
  | WRaise _                 => ""
  | WTryCatch _ _ _          => ""
  | WGhostDecl _ _ _         => ""
  | WGhostAssign _ _ _ _     => ""
  | WLabel _                 => ""
  | WAssert _ _              => ""
  | WAssume _                => ""
  end.

(* ===== Per-construct acceptable-emission predicates ===== *)

(* wSkip — Module 6 emits the literal `()` (Python source:
   `module6_whyml/statements.py:1115` — `code = f"{indent}()"`).
   The acceptable set is a singleton. *)

Definition acceptable_skip_emissions : list string := ["()"].

(* ===== Per-construct correctness theorems ===== *)

(* The pilot theorem: for every input that reaches `gen SSkip`, the
   formal emission lies in the acceptable set. *)

Theorem emit_skip_correct :
  In (emit_stmt (gen SSkip)) acceptable_skip_emissions.
Proof.
  simpl. left. reflexivity.
Qed.

(* ===== Sanity: emit_stmt is the identity-after-gen on wSkip ===== *)

Lemma emit_stmt_gen_skip : emit_stmt (gen SSkip) = "()".
Proof. reflexivity. Qed.

(* ===== Notes for the next PR (Sub-α.2: wAssign) =====

   The wAssign case is the first non-trivial pilot. Module 6's
   `_handle_assign_stmt` (statements.py:61) emits one of three
   surface forms depending on whether the target is a shared
   variable, a fresh local, or an existing local. The acceptable
   set for wAssign therefore has multiple elements:

     Definition acceptable_assign_emissions (x : ident) (e : expr) : list string :=
       [ "let " ++ x ++ " = " ++ pretty_expr e ++ " in" ;  (* fresh local *)
         x ++ " := " ++ pretty_expr e ;                    (* existing local *)
         x ++ " := " ++ pretty_expr_bool_coerced e         (* bool target *)
       ].

   The theorem `emit_assign_correct` proves that whichever branch
   `_handle_assign_stmt` takes, the emitted string is in this list.

   This pattern repeats for every construct. The work per construct
   is: identify Module 6's emission alternatives, define the
   acceptable predicate, prove correctness by case analysis on
   `gen`'s output. ~3 days per construct per the plan.

   Until `pretty_expr` is defined, wAssign and downstream constructs
   ship as `""` placeholders here. The placeholder is a stub that
   makes `emit_stmt` total without committing to a specific output;
   no correctness theorem is asserted for it. *)
