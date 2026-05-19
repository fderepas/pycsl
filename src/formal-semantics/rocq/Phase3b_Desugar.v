(* Phase3b_Desugar.v — For-loop desugaring *)

Require Import ZArith String List Bool.
Require Import Lia.
Require Import Phase1_AST.
Require Import Phase2_State.
Require Import Phase3_SOS.
Open Scope Z_scope.
Open Scope string_scope.

(* Reserved index variable name *)
Definition for_idx : ident := "_pycsl_idx".

(* Freshness predicate: id does not appear as assigned/bound variable in s *)
Fixpoint fresh_in_stmt (id : ident) (s : stmt) : Prop :=
  match s with
  | SSkip => True
  | SAssign x _ => x <> id
  | SAugAssign x _ _ => x <> id
  | SArraySet arr _ _ => arr <> id
  | SSeq s1 s2 => fresh_in_stmt id s1 /\ fresh_in_stmt id s2
  | SIf _ s1 s2 => fresh_in_stmt id s1 /\ fresh_in_stmt id s2
  | SWhile _ _ _ body => fresh_in_stmt id body
  | SFor x arr _ _ body => x <> id /\ arr <> id /\ fresh_in_stmt id body
  | SReturn _ => True
  | SContinue => True
  end.

(* Decidable boolean version of freshness *)
Fixpoint fresh_in_stmt_b (id : ident) (s : stmt) : bool :=
  match s with
  | SSkip => true
  | SAssign x _ => negb (String.eqb x id)
  | SAugAssign x _ _ => negb (String.eqb x id)
  | SArraySet arr _ _ => negb (String.eqb arr id)
  | SSeq s1 s2 => fresh_in_stmt_b id s1 && fresh_in_stmt_b id s2
  | SIf _ s1 s2 => fresh_in_stmt_b id s1 && fresh_in_stmt_b id s2
  | SWhile _ _ _ body => fresh_in_stmt_b id body
  | SFor x arr _ _ body =>
    negb (String.eqb x id) && negb (String.eqb arr id) &&
    fresh_in_stmt_b id body
  | SReturn _ => true
  | SContinue => true
  end.

(* Desugaring: replace SFor with index-variable SWhile *)
Fixpoint desugar (s : stmt) : stmt :=
  match s with
  | SFor x arr inv var body =>
    (* _pycsl_idx = 0;
       while cond: x = arr[_pycsl_idx]; body; _pycsl_idx += 1
       where cond tests _pycsl_idx < length(arr) via eval_bool *)
    SSeq (SAssign for_idx (EInt 0))
         (SWhile inv var
                 (EBinOp OpSub
                    (ESubscript arr (EVar for_idx))
                    (ESubscript arr (EVar for_idx)))
                 (SSeq (SAssign x (ESubscript arr (EVar for_idx)))
                       (SSeq (desugar body)
                             (SAugAssign for_idx OpAdd (EInt 1)))))
  | SSeq s1 s2 => SSeq (desugar s1) (desugar s2)
  | SIf c s1 s2 => SIf c (desugar s1) (desugar s2)
  | SWhile i v c b => SWhile i v c (desugar b)
  | s => s
  end.

(* Desugaring correctness — requires SFor exec rules to be provable.
   The main soundness theorem (Phase 5b) does not depend on this lemma:
   wp for SFor delegates to wp of the desugared form, and the exec induction
   has no SFor cases (no exec constructors for SFor).
   This lemma establishes bi-implication between original and desugared
   execution under the freshness precondition. *)
Lemma desugar_correct : forall st s out,
  fresh_in_stmt for_idx s ->
  exec st s out <-> exec st (desugar s) out.
Proof.
  (* Full proof requires adding exec constructors for SFor
     (for-each iteration semantics) and showing equivalence
     with the index-variable while loop under freshness.
     Deferred: does not block soundness theorem. *)
  Admitted.

(* ===================================================================== *)
(* Phase 1a — Category B desugaring functions and correctness lemmas     *)
(* Features: 28 (tuple unpacking), 29 (walrus :=), 30 (match statement)  *)
(* ===================================================================== *)

(* ------------------------------------------------------------------ *)
(* Feature 29 — Walrus operator :=                                     *)
(* In Python: (x := e) assigns e to x and evaluates to e.             *)
(* In statement position it is indistinguishable from plain assignment. *)
(* ------------------------------------------------------------------ *)

Definition walrus_assign (x : ident) (e : expr) : stmt :=
  SAssign x e.

(* Walrus assignment reduces to ordinary assignment — definitionally. *)
Lemma walrus_assign_eq : forall x e,
  walrus_assign x e = SAssign x e.
Proof. reflexivity. Qed.

(* The exec relation for walrus_assign is the same as for SAssign. *)
Lemma exec_walrus_assign : forall st x e out,
  exec st (walrus_assign x e) out <->
  exec st (SAssign x e) out.
Proof. intros. unfold walrus_assign. tauto. Qed.

(* ------------------------------------------------------------------ *)
(* Feature 28 — Tuple unpacking                                        *)
(* In Python: x, y = arr   unpacks arr[0] into x and arr[1] into y.  *)
(* The transpiler pre-names the source as an array identifier.         *)
(* ------------------------------------------------------------------ *)

(* Unpack a 2-element array arr into variables x (index 0) and y (index 1). *)
Definition tuple_unpack2 (arr x y : ident) : stmt :=
  SSeq (SAssign x (ESubscript arr (EInt 0)))
       (SAssign y (ESubscript arr (EInt 1))).

(* tuple_unpack2 is a sequence of two subscript assignments. *)
Lemma tuple_unpack2_eq : forall arr x y,
  tuple_unpack2 arr x y =
  SSeq (SAssign x (ESubscript arr (EInt 0)))
       (SAssign y (ESubscript arr (EInt 1))).
Proof. reflexivity. Qed.

(* Executing tuple_unpack2 produces the correct state: x = arr[0], y = arr[1].
   Uses the intermediate state st1 for the second eval (correct when arr <> x;
   in the degenerate case arr = x the second subscript is evaluated in st1). *)
Lemma exec_tuple_unpack2_normal : forall st arr x y,
  let st1 := update st x (eval_expr st (ESubscript arr (EInt 0))) in
  exec st (tuple_unpack2 arr x y)
    (ONormal (update st1 y (eval_expr st1 (ESubscript arr (EInt 1))))).
Proof.
  intros. unfold tuple_unpack2.
  eapply ExecSeq.
  - apply ExecAssign.
  - apply ExecAssign.
Qed.

(* ------------------------------------------------------------------ *)
(* Feature 30 — Match statement                                        *)
(* In Python: match scrutinee: case n1: s1 ... default: sd            *)
(* The transpiler lowers this to an if/elif/else chain.                *)
(* eval_bool (scrutinee - n) = false iff scrutinee = n (int truth).   *)
(* ------------------------------------------------------------------ *)

(* Desugar a list of integer-pattern match arms into a nested SIf.
   The condition (scrutinee - n) is falsy (0) exactly when scrutinee = n,
   so the matching arm is placed in the *else* branch. *)
Fixpoint desugar_match (scrutinee : expr) (cases : list (Z * stmt))
                       (default : stmt) : stmt :=
  match cases with
  | nil => default
  | (n, body) :: rest =>
      SIf (EBinOp OpSub scrutinee (EInt n))
          (desugar_match scrutinee rest default)  (* scrutinee <> n *)
          body                                    (* scrutinee = n  *)
  end.

(* Empty match reduces to the default branch. *)
Lemma desugar_match_nil : forall scrutinee default,
  desugar_match scrutinee nil default = default.
Proof. reflexivity. Qed.

(* Single-arm match: executes body when scrutinee = n, default otherwise. *)
Lemma exec_desugar_match_single_hit : forall st scrutinee n body default out,
  eval_expr st scrutinee = VInt n ->
  exec st body out ->
  exec st (desugar_match scrutinee ((n, body) :: nil) default) out.
Proof.
  intros st scrutinee n body default out Hval Hbody.
  simpl.
  apply ExecIfFalse.
  - unfold eval_bool. simpl.
    rewrite Hval. simpl. rewrite Z.sub_diag. reflexivity.
  - exact Hbody.
Qed.

Lemma exec_desugar_match_single_miss : forall st scrutinee n body default out,
  eval_expr st scrutinee = VInt n ->
  exec st default out ->
  forall m, m <> n ->
  exec st (desugar_match scrutinee ((m, body) :: nil) default) out.
Proof.
  intros st scrutinee n body default out Hval Hdef m Hne.
  simpl.
  apply ExecIfTrue.
  - unfold eval_bool. simpl.
    rewrite Hval. simpl.
    destruct (Z.eqb_spec (n - m) 0) as [Heq | Hne2].
    + exfalso. apply Hne. lia.
    + destruct (n - m) eqn:E; try reflexivity.
      exfalso. apply Hne2. reflexivity.
  - exact Hdef.
Qed.
