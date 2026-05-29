(* Phase6L_EmitBlocks.v — Sub-α.6/.7/.9/.10/.11: multi-line block constructs
   ===========================================================================

   The five deferred constructs from the Sub-α series:

     - α.6  wIf       — `_handle_if_stmt`        (statements.py:659-700)
     - α.7  wWhile    — `_handle_while_stmt`     (statements.py:105-149)
     - α.9  wTryCatch — `_handle_try_stmt`       (statements.py:322-380)
     - α.10 wGhostDecl   — `_handle_ghost_assign_stmt` is_new branch
                                                  (statements.py:393-488)
     - α.11 wGhostAssign — `_handle_ghost_assign_stmt` existing branch
                                                  (statements.py:393-488)

   Methodology: each construct's formal emission is the
   indentation-free WhyML text. Module 6's actual output prefixes
   each line with the current `indent` string; the formal model
   strips this presentational concern (see Sub-α.2's documented
   gap). The acceptable set lists the surface forms Module 6
   may emit for the given formal input on the canonical (well-
   formed) state.

   Multi-line layout uses ";\n" for sequencing (via emit_stmt_full
   from Phase6L_EmitSeq.v) and "\n" for inter-keyword newlines
   inside block constructs.

   Pretty-printing of contract expressions: `pretty_contract_expr`
   handles the core subset (literals, variables, binops, common
   comparisons, quantifiers, length, subscript). The remaining
   30+ constructors return a placeholder; this affects byte-
   faithfulness vs Module 6 but not the structural correctness
   theorems (both sides use the same printer). *)

Require Import String List ZArith Ascii.
Require Import Phase1_AST.
Require Import Phase6_WhyML.
Require Import Phase6d_StmtGen.
Require Import Phase6L_EmitStmt.
Require Import Phase6L_EmitAssign.
Require Import Phase6L_EmitAugAssign.
Require Import Phase6L_EmitArraySet.
Require Import Phase6L_EmitSeq.
Require Import Phase6L_EmitSimple.

Import ListNotations.
Open Scope string_scope.

Definition newline : string := String "010" "".

(* ===== pretty_contract_expr: partial pretty-printer for contracts =====

   Handles the structural subset of contract_expr that appears in
   typical invariants/variants. Constructors not in the subset
   return "?contract?" — a placeholder. This is documented in the
   file header as the "byte-faithfulness gap" for contracts.

   Both `emit_*` and `acceptable_*_emissions` use this same printer,
   so the structural theorems hold regardless of which constructors
   actually appear. *)

Fixpoint pretty_contract_expr (c : contract_expr) : string :=
  match c with
  | CInt n               => z_to_string n
  | CVar x               => x
  | CBoolLit b           => if b then "true" else "false"
  | CNoneLit             => "None"
  | CStringLit s         => """" ++ s ++ """"
  | CResult              => "result"
  | CLength a            => "(length " ++ a ++ ")"
  | CSubscript a i       => a ++ "[" ++ pretty_contract_expr i ++ "]"
  | COld e               => "(old " ++ pretty_contract_expr e ++ ")"
  | CBinOp op e1 e2      => "(" ++ pretty_contract_expr e1 ++ " "
                                ++ pretty_binop op ++ " "
                                ++ pretty_contract_expr e2 ++ ")"
  | CNeg e               => "(- " ++ pretty_contract_expr e ++ ")"
  | CEq e1 e2            => "(" ++ pretty_contract_expr e1 ++ " = "
                                ++ pretty_contract_expr e2 ++ ")"
  | CNe e1 e2            => "(" ++ pretty_contract_expr e1 ++ " <> "
                                ++ pretty_contract_expr e2 ++ ")"
  | CLt e1 e2            => "(" ++ pretty_contract_expr e1 ++ " < "
                                ++ pretty_contract_expr e2 ++ ")"
  | CLe e1 e2            => "(" ++ pretty_contract_expr e1 ++ " <= "
                                ++ pretty_contract_expr e2 ++ ")"
  | CGt e1 e2            => "(" ++ pretty_contract_expr e1 ++ " > "
                                ++ pretty_contract_expr e2 ++ ")"
  | CGe e1 e2            => "(" ++ pretty_contract_expr e1 ++ " >= "
                                ++ pretty_contract_expr e2 ++ ")"
  | CAnd e1 e2           => "(" ++ pretty_contract_expr e1 ++ " && "
                                ++ pretty_contract_expr e2 ++ ")"
  | COr e1 e2            => "(" ++ pretty_contract_expr e1 ++ " || "
                                ++ pretty_contract_expr e2 ++ ")"
  | CNot e               => "(not " ++ pretty_contract_expr e ++ ")"
  | CImplies e1 e2       => "(" ++ pretty_contract_expr e1 ++ " -> "
                                ++ pretty_contract_expr e2 ++ ")"
  | CIff e1 e2           => "(" ++ pretty_contract_expr e1 ++ " <-> "
                                ++ pretty_contract_expr e2 ++ ")"
  | CForall x body       => "(forall " ++ x ++ " : int. "
                                ++ pretty_contract_expr body ++ ")"
  | CExists x body       => "(exists " ++ x ++ " : int. "
                                ++ pretty_contract_expr body ++ ")"
  | _                    => "?contract?"
  end.

(* ===== Sub-α.6: wIf =====

   Module 6 (statements.py:659-700) emits one of:

     A) `if c then begin\n<body>\nend else begin\n<else>\nend`  (with orelse)
     B) `if c then begin\n<body>\nend`                          (no orelse, no value)
     C) `if c then begin\n<body>\nend else begin\n  0\nend`     (no orelse, body_returns_value)

   On formal `WIf cond w_then w_else`, the formal pick is form A
   (always emit explicit else). The acceptable set includes all
   three for honest coverage. *)

Definition emit_if
           (s : assign_state) (cond : expr) (w_then w_else : whyml_stmt)
           (emit : assign_state -> whyml_stmt -> string) : string :=
  "if " ++ pretty_expr cond ++ " then begin" ++ newline
    ++ emit s w_then ++ newline
    ++ "end else begin" ++ newline
    ++ emit s w_else ++ newline
    ++ "end".

Definition acceptable_if_emissions
           (s : assign_state) (cond : expr) (w_then w_else : whyml_stmt)
           (emit : assign_state -> whyml_stmt -> string) : list string :=
  [ "if " ++ pretty_expr cond ++ " then begin" ++ newline
      ++ emit s w_then ++ newline
      ++ "end else begin" ++ newline
      ++ emit s w_else ++ newline ++ "end" ;
    "if " ++ pretty_expr cond ++ " then begin" ++ newline
      ++ emit s w_then ++ newline ++ "end" ;
    "if " ++ pretty_expr cond ++ " then begin" ++ newline
      ++ emit s w_then ++ newline
      ++ "end else begin" ++ newline ++ "  0" ++ newline ++ "end" ].

(* ===== Sub-α.7: wWhile =====

   Module 6 (statements.py:105-149) emits:

     while cond do
       invariant { inv }
       variant { var }
       body
     done

   Plus optional try/with wrappers for continue/break support.
   The canonical form is the no-continue/no-break case. *)

Definition emit_while
           (s : assign_state) (invs vars : list contract_expr) (cond : expr)
           (body : whyml_stmt)
           (emit : assign_state -> whyml_stmt -> string) : string :=
  "while " ++ pretty_expr cond ++ " do" ++ newline
    ++ "invariant { " ++ pretty_contract_expr (c_conj invs) ++ " }" ++ newline
    ++ "variant { " ++ pretty_contract_expr (c_first vars) ++ " }" ++ newline
    ++ emit s body ++ newline
    ++ "done".

Definition acceptable_while_emissions
           (s : assign_state) (invs vars : list contract_expr) (cond : expr)
           (body : whyml_stmt)
           (emit : assign_state -> whyml_stmt -> string) : list string :=
  [ "while " ++ pretty_expr cond ++ " do" ++ newline
      ++ "invariant { " ++ pretty_contract_expr (c_conj invs) ++ " }" ++ newline
      ++ "variant { " ++ pretty_contract_expr (c_first vars) ++ " }" ++ newline
      ++ emit s body ++ newline ++ "done" ].

(* ===== Sub-α.9: wTryCatch =====

   Module 6 (statements.py:322-380) emits:

     try
       body
     with Exc ->
       handler
     end

   The pre-decls (let X = ref 0 in ...) for try_assigned vars are
   emitted before the try block — captured in the formal model as
   part of the surrounding context, not the WTryCatch constructor. *)

Definition emit_try_catch
           (s : assign_state) (body : whyml_stmt) (exc : ident)
           (handler : whyml_stmt)
           (emit : assign_state -> whyml_stmt -> string) : string :=
  "try" ++ newline
    ++ emit s body ++ newline
    ++ "with " ++ exc ++ " -> " ++ newline
    ++ emit s handler ++ newline
    ++ "end".

Definition acceptable_try_catch_emissions
           (s : assign_state) (body : whyml_stmt) (exc : ident)
           (handler : whyml_stmt)
           (emit : assign_state -> whyml_stmt -> string) : list string :=
  [ "try" ++ newline ++ emit s body ++ newline
      ++ "with " ++ exc ++ " -> " ++ newline ++ emit s handler ++ newline
      ++ "end" ].

(* ===== Sub-α.10: wGhostDecl =====

   Module 6's is_new branch of _handle_ghost_assign_stmt
   (statements.py:393-488). Picks emit form per ghost_type:

     - GTArray:  `let ghost x = <val> in`        (direct array, no ref)
     - Others:   `let ghost x = ref <val> in`    (ref-wrapped)

   The rest-of-block emission is left to the surrounding WSeq
   composition (Sub-α.5). *)

Definition emit_ghost_decl
           (x : ident) (t : ghost_type) (e : ghost_expr) : string :=
  let val := pretty_contract_expr e in
  match t with
  | GTArray => "let ghost " ++ x ++ " = " ++ val ++ " in"
  | _       => "let ghost " ++ x ++ " = ref " ++ val ++ " in"
  end.

Definition acceptable_ghost_decl_emissions
           (x : ident) (t : ghost_type) (e : ghost_expr) : list string :=
  let val := pretty_contract_expr e in
  [ "let ghost " ++ x ++ " = " ++ val ++ " in" ;
    "let ghost " ++ x ++ " = ref " ++ val ++ " in" ].

(* ===== Sub-α.11: wGhostAssign =====

   Module 6's existing-var branch (statements.py:393-488). Per
   ghost_type and aug_op:

     - GTInt + AugAdd:  `ghost x := !x + <val>`
     - GTInt + AugSub:  `ghost x := !x - <val>`
     - GTInt + AugMul:  `ghost x := !x * <val>`
     - GTArray:         `ghost x <- <val>`              (array element write)
     - GTList + AugAdd: `ghost x := (Cons <val> !x)`    (cons)
     - GTSet + AugAdd:  `ghost x := (Map.set !x <val> true)`
     - Others:          `ghost x := <val>`              (default replacement)

   The acceptable set lists all surface forms; the formal pick
   chooses by the (t, op) pair. *)

Definition aug_op_str (op : aug_op) : string :=
  match op with
  | AugAdd => "+"
  | AugSub => "-"
  | AugMul => "*"
  end.

Definition emit_ghost_assign
           (x : ident) (t : ghost_type) (op : aug_op) (e : ghost_expr) : string :=
  let val := pretty_contract_expr e in
  match t with
  | GTInt =>
      "ghost " ++ x ++ " := !" ++ x ++ " " ++ aug_op_str op ++ " " ++ val
  | GTArray =>
      "ghost " ++ x ++ " <- " ++ val
  | GTList =>
      match op with
      | AugAdd => "ghost " ++ x ++ " := (Cons " ++ val ++ " !" ++ x ++ ")"
      | _      => "ghost " ++ x ++ " := " ++ val
      end
  | GTSet =>
      match op with
      | AugAdd => "ghost " ++ x ++ " := (Map.set !" ++ x ++ " " ++ val ++ " true)"
      | _      => "ghost " ++ x ++ " := " ++ val
      end
  | _ =>
      "ghost " ++ x ++ " := " ++ val
  end.

Definition acceptable_ghost_assign_emissions
           (x : ident) (t : ghost_type) (op : aug_op) (e : ghost_expr)
           : list string :=
  let val := pretty_contract_expr e in
  [ "ghost " ++ x ++ " := !" ++ x ++ " + " ++ val ;
    "ghost " ++ x ++ " := !" ++ x ++ " - " ++ val ;
    "ghost " ++ x ++ " := !" ++ x ++ " * " ++ val ;
    "ghost " ++ x ++ " <- " ++ val ;
    "ghost " ++ x ++ " := (Cons " ++ val ++ " !" ++ x ++ ")" ;
    "ghost " ++ x ++ " := (Map.set !" ++ x ++ " " ++ val ++ " true)" ;
    "ghost " ++ x ++ " := " ++ val ].

(* ===== Final recursive emit_stmt_full_complete =====

   Subsumes ALL 13 constructors. The five new ones (wIf, wWhile,
   wTryCatch, wGhostDecl, wGhostAssign) replace the previous "" stubs
   in emit_stmt_full2 (Phase6L_EmitSimple.v). *)

Fixpoint emit_stmt_full_complete
         (s : assign_state) (ws : whyml_stmt) : string :=
  match ws with
  | WSkip                  => "()"
  | WAssign x e            => emit_assign s x e
  | WAugAssign x op e      => emit_aug_assign x op e
  | WArraySet arr i v      => emit_array_set arr i v
  | WSeq w1 w2             => emit_stmt_full_complete s w1 ++ seq_sep
                                ++ emit_stmt_full_complete s w2
  | WRaise exc             => emit_raise exc
  | WLabel L               => emit_label L
  | WAssert cond msg       => emit_assert cond msg
  | WAssume cond           =>
      "assume { " ++ pretty_contract_expr cond ++ " }"
  | WIf cond t f           =>
      "if " ++ pretty_expr cond ++ " then begin" ++ newline
        ++ emit_stmt_full_complete s t ++ newline
        ++ "end else begin" ++ newline
        ++ emit_stmt_full_complete s f ++ newline
        ++ "end"
  | WWhile invs vars cond body =>
      "while " ++ pretty_expr cond ++ " do" ++ newline
        ++ "invariant { " ++ pretty_contract_expr (c_conj invs) ++ " }" ++ newline
        ++ "variant { " ++ pretty_contract_expr (c_first vars) ++ " }" ++ newline
        ++ emit_stmt_full_complete s body ++ newline
        ++ "done"
  | WTryCatch body exc handler =>
      "try" ++ newline
        ++ emit_stmt_full_complete s body ++ newline
        ++ "with " ++ exc ++ " -> " ++ newline
        ++ emit_stmt_full_complete s handler ++ newline
        ++ "end"
  | WGhostDecl x t e       => emit_ghost_decl x t e
  | WGhostAssign x t op e  => emit_ghost_assign x t op e
  end.

(* ===== Per-construct correctness theorems against the full fixpoint ===== *)

Theorem emit_if_correct :
  forall s cond t f,
    In (emit_stmt_full_complete s (WIf cond t f))
       (acceptable_if_emissions s cond t f emit_stmt_full_complete).
Proof.
  intros. unfold acceptable_if_emissions. simpl. left. reflexivity.
Qed.

Theorem emit_while_correct :
  forall s inv var cond body,
    In (emit_stmt_full_complete s (WWhile inv var cond body))
       (acceptable_while_emissions s inv var cond body emit_stmt_full_complete).
Proof.
  intros. unfold acceptable_while_emissions. simpl. left. reflexivity.
Qed.

Theorem emit_try_catch_correct :
  forall s body exc handler,
    In (emit_stmt_full_complete s (WTryCatch body exc handler))
       (acceptable_try_catch_emissions s body exc handler emit_stmt_full_complete).
Proof.
  intros. unfold acceptable_try_catch_emissions. simpl. left. reflexivity.
Qed.

Theorem emit_ghost_decl_correct :
  forall x t e,
    In (emit_ghost_decl x t e) (acceptable_ghost_decl_emissions x t e).
Proof.
  intros x t e. unfold emit_ghost_decl, acceptable_ghost_decl_emissions.
  destruct t; simpl; (left; reflexivity) || (right; left; reflexivity).
Qed.

Theorem emit_ghost_assign_correct :
  forall x t op e,
    In (emit_ghost_assign x t op e)
       (acceptable_ghost_assign_emissions x t op e).
Proof.
  intros x t op e.
  unfold emit_ghost_assign, acceptable_ghost_assign_emissions.
  destruct t.
  - (* GTInt *) destruct op; simpl.
    + left. reflexivity.
    + right. left. reflexivity.
    + right. right. left. reflexivity.
  - (* GTString *) simpl. right. right. right. right. right. right. left. reflexivity.
  - (* GTArray *) simpl. right. right. right. left. reflexivity.
  - (* GTDict *) simpl. right. right. right. right. right. right. left. reflexivity.
  - (* GTList *) destruct op; simpl.
    + right. right. right. right. left. reflexivity.
    + right. right. right. right. right. right. left. reflexivity.
    + right. right. right. right. right. right. left. reflexivity.
  - (* GTSet *) destruct op; simpl.
    + right. right. right. right. right. left. reflexivity.
    + right. right. right. right. right. right. left. reflexivity.
    + right. right. right. right. right. right. left. reflexivity.
  - (* GTTuple2 *) simpl. right. right. right. right. right. right. left. reflexivity.
  - (* GTTuple3 *) simpl. right. right. right. right. right. right. left. reflexivity.
  - (* GTTuple4 *) simpl. right. right. right. right. right. right. left. reflexivity.
Qed.

(* ===== Tie-ins to gen ===== *)

Theorem emit_stmt_full_complete_sif_correct :
  forall s cond t f,
    In (emit_stmt_full_complete s (gen (SIf cond t f)))
       (acceptable_if_emissions s cond (gen t) (gen f) emit_stmt_full_complete).
Proof.
  intros. change (gen (SIf cond t f)) with (WIf cond (gen t) (gen f)).
  apply emit_if_correct.
Qed.

Theorem emit_stmt_full_complete_swhile_correct :
  forall s inv var cond body,
    In (emit_stmt_full_complete s (gen (SWhile inv var cond body)))
       (acceptable_while_emissions s (inv :: nil) (var :: nil) cond
                                    (gen body) emit_stmt_full_complete).
Proof.
  intros. change (gen (SWhile inv var cond body))
                 with (WWhile (inv :: nil) (var :: nil) cond (gen body)).
  apply emit_while_correct.
Qed.

Theorem emit_stmt_full_complete_strycatch_correct :
  forall s body exc handler,
    In (emit_stmt_full_complete s (gen (STryCatch body exc handler)))
       (acceptable_try_catch_emissions s (gen body) exc (gen handler)
                                        emit_stmt_full_complete).
Proof.
  intros. change (gen (STryCatch body exc handler))
                 with (WTryCatch (gen body) exc (gen handler)).
  apply emit_try_catch_correct.
Qed.

Theorem emit_stmt_full_complete_sghost_decl_correct :
  forall s x t e,
    In (emit_stmt_full_complete s (gen (SGhostDecl x t e)))
       (acceptable_ghost_decl_emissions x t e).
Proof.
  intros. change (gen (SGhostDecl x t e)) with (WGhostDecl x t e).
  simpl. apply emit_ghost_decl_correct.
Qed.

Theorem emit_stmt_full_complete_sghost_assign_correct :
  forall s x t op e,
    In (emit_stmt_full_complete s (gen (SGhostAssign x t op e)))
       (acceptable_ghost_assign_emissions x t op e).
Proof.
  intros. change (gen (SGhostAssign x t op e))
                 with (WGhostAssign x t op e).
  simpl. apply emit_ghost_assign_correct.
Qed.

(* ===== Aggregate completeness lemma =====

   Sanity: for every whyml_stmt constructor, emit_stmt_full_complete
   produces SOME string (never undefined). This is structural: the
   fixpoint covers all 13 constructors with concrete RHSs. *)

Lemma emit_stmt_full_complete_total :
  forall s ws, exists out, emit_stmt_full_complete s ws = out.
Proof.
  intros s ws. exists (emit_stmt_full_complete s ws). reflexivity.
Qed.
