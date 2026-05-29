(* Phase6L_EmitStateAware.v — refined state-aware pretty-printer
   ================================================================

   A parallel pretty-printer that refines `emit_stmt_full_complete`
   (Sub-α.14) with state-awareness matching Module 6's actual
   emission rules. Used by the CC.5 byte-diff tool to reduce DIFFs
   without disturbing the proved per-construct theorems.

   Refinements vs. structural printer:

     - DIFF-D (ref-deref): pretty_expr_state emits `!x` for variables
       in `as_local_refs` (matches Module 6's `_handle_var_expr`).
     - DIFF-A (abstract-op wrappers):
         · `ELen arr`       → `(iter_length arr)` when arr ∉ array_locals
                              `(Array.length arr)` otherwise
         · `ESubscript a i` → `(subscript_get a i)` when a ∉ array_locals
                              `a[i]` otherwise
     - DIFF-B (bool-coercion): if/while conditions wrapped as
                              `(<expr> <> 0)` matching Module 6's `_to_bool`.
     - DIFF-T (trailing-rest convention): `emit_cont` threads a
       continuation string. Scoping constructs (fresh `let-in`,
       `let ghost`, `label`) substitute `()` when continuation is
       empty, mirroring Module 6's
       `if not rest_code: rest_code = f"{indent}()"`.
     - DIFF-S (state-dependent dispatch): arrayset picks `arr[i] <- v`
       when arr ∈ array_locals, `subscript_set arr i v` otherwise.

   This file does NOT replace `emit_stmt_full_complete`. The
   composition lemma in `Phase6L_EmitComposition.v` continues to
   apply to the structural printer. The state-aware variant is for
   empirical byte-diff validation against Module 6.

   To validate that the state-aware printer agrees with the
   structural printer's *acceptable sets* (a future theorem),
   structural induction on Stmt is sufficient — every
   state-aware output remains in the acceptable set.
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
Require Import Phase6L_EmitSimple.
Require Import Phase6L_EmitBlocks.

Import ListNotations.
Open Scope string_scope.

(* ===== Extended state for runtime emission ===== *)

Record aware_state : Type := mkAwareState {
  aw_shared_vars   : list ident;     (* Module 6: _shared_var_names *)
  aw_declared_refs : list ident;     (* Module 6: declared_refs *)
  aw_local_refs    : list ident;     (* Module 6: local_refs (for `!x` deref) *)
  aw_array_locals  : list ident;     (* Module 6: _array_locals (native `[i]` access) *)
  aw_bounded_int   : option string
}.

Definition aware_in (x : ident) (xs : list ident) : bool :=
  existsb (String.eqb x) xs.

(* ===== State-aware expression pretty-printer ===== *)

Fixpoint pretty_expr_state (s : aware_state) (e : expr) : string :=
  match e with
  | EInt n           => z_to_string n
  | EVar x           =>
      if aware_in x s.(aw_local_refs) then "!" ++ x
      else if aware_in x s.(aw_shared_vars) then "!" ++ x
      else x
  | ESubscript a i   =>
      if aware_in a s.(aw_array_locals) then
        a ++ "[" ++ pretty_expr_state s i ++ "]"
      else
        "(subscript_get " ++ a ++ " " ++ pretty_expr_state s i ++ ")"
  | ELen a           =>
      if aware_in a s.(aw_array_locals) then
        "(Array.length " ++ a ++ ")"
      else
        "(iter_length " ++ a ++ ")"
  | EBinOp op e1 e2  =>
      (* Module 6 emits division in body context as (pycsl_div a b)
         to flag the no_exception trigger. Other ops are infix. *)
      match op with
      | OpDiv => "(pycsl_div " ++ pretty_expr_state s e1
                   ++ " " ++ pretty_expr_state s e2 ++ ")"
      | _     => "(" ++ pretty_expr_state s e1 ++ " " ++ pretty_binop op
                   ++ " " ++ pretty_expr_state s e2 ++ ")"
      end
  | ENeg e1          => "(- " ++ pretty_expr_state s e1 ++ ")"
  | ECmp op e1 e2    =>
      "(" ++ pretty_expr_state s e1 ++ " " ++ pretty_cmpop op
          ++ " " ++ pretty_expr_state s e2 ++ ")"
  | EFieldGet obj f  => obj ++ "." ++ f
  | ECall func args  =>
      func ++ "(" ++
        (fix args_str (xs : list expr) : string :=
           match xs with
           | nil => ""
           | x :: nil => pretty_expr_state s x
           | x :: rest => pretty_expr_state s x ++ ", " ++ args_str rest
           end) args ++ ")"
  end.

(* ===== Bool coercion (matches Module 6's _to_bool) =====
   Already-bool expressions (ECmp) are emitted as-is; int-typed
   expressions get the `<> 0` wrap. *)

Definition to_bool_state (s : aware_state) (e : expr) : string :=
  match e with
  | ECmp _ _ _ => pretty_expr_state s e
  | _          => "(" ++ pretty_expr_state s e ++ " <> 0)"
  end.

(* ===== State-aware contract pretty-printer =====
   Like `pretty_contract_expr` but emits `!x` for CVar/CLength on
   ref-tracked variables, matching Module 6's behavior in
   `_handle_var_expr` when invariants are emitted with local_refs
   passed in. *)
Fixpoint pretty_contract_expr_state
         (s : aware_state) (c : contract_expr) : string :=
  match c with
  | CInt n               => z_to_string n
  | CVar x               =>
      if aware_in x s.(aw_local_refs) then "!" ++ x
      else if aware_in x s.(aw_shared_vars) then "!" ++ x
      else x
  | CBoolLit b           => if b then "true" else "false"
  | CNoneLit             => "None"
  | CStringLit s         => """" ++ s ++ """"
  | CResult              => "result"
  | CLength a            =>
      if aware_in a s.(aw_array_locals) then
        "(Array.length " ++ a ++ ")"
      else
        "(iter_length " ++ a ++ ")"
  | CSubscript a i       => a ++ "[" ++ pretty_contract_expr_state s i ++ "]"
  | COld e               => "(old " ++ pretty_contract_expr_state s e ++ ")"
  | CBinOp op e1 e2      =>
      (* Spec context: Module 6 emits OpDiv as `(div a b)` (function-
         call form), other ops infix. *)
      match op with
      | OpDiv => "(div " ++ pretty_contract_expr_state s e1
                   ++ " " ++ pretty_contract_expr_state s e2 ++ ")"
      | _     => "(" ++ pretty_contract_expr_state s e1 ++ " "
                   ++ pretty_binop op ++ " "
                   ++ pretty_contract_expr_state s e2 ++ ")"
      end
  | CNeg e               => "(- " ++ pretty_contract_expr_state s e ++ ")"
  | CEq e1 e2            => "(" ++ pretty_contract_expr_state s e1 ++ " = "
                                ++ pretty_contract_expr_state s e2 ++ ")"
  | CNe e1 e2            => "(" ++ pretty_contract_expr_state s e1 ++ " <> "
                                ++ pretty_contract_expr_state s e2 ++ ")"
  | CLt e1 e2            => "(" ++ pretty_contract_expr_state s e1 ++ " < "
                                ++ pretty_contract_expr_state s e2 ++ ")"
  | CLe e1 e2            => "(" ++ pretty_contract_expr_state s e1 ++ " <= "
                                ++ pretty_contract_expr_state s e2 ++ ")"
  | CGt e1 e2            => "(" ++ pretty_contract_expr_state s e1 ++ " > "
                                ++ pretty_contract_expr_state s e2 ++ ")"
  | CGe e1 e2            => "(" ++ pretty_contract_expr_state s e1 ++ " >= "
                                ++ pretty_contract_expr_state s e2 ++ ")"
  | CAnd e1 e2           => "(" ++ pretty_contract_expr_state s e1 ++ " && "
                                ++ pretty_contract_expr_state s e2 ++ ")"
  | COr e1 e2            => "(" ++ pretty_contract_expr_state s e1 ++ " || "
                                ++ pretty_contract_expr_state s e2 ++ ")"
  | CNot e               => "(not " ++ pretty_contract_expr_state s e ++ ")"
  | CImplies e1 e2       => "(" ++ pretty_contract_expr_state s e1 ++ " -> "
                                ++ pretty_contract_expr_state s e2 ++ ")"
  | CIff e1 e2           => "(" ++ pretty_contract_expr_state s e1 ++ " <-> "
                                ++ pretty_contract_expr_state s e2 ++ ")"
  | CForall x body       => "(forall " ++ x ++ " : int. "
                                ++ pretty_contract_expr_state s body ++ ")"
  | CExists x body       => "(exists " ++ x ++ " : int. "
                                ++ pretty_contract_expr_state s body ++ ")"
  (* Ghost array atoms (Module 6 emissions per expressions.py:941-952) *)
  | CGCopy a             => "(Array.copy " ++ a ++ ")"
  | CGCopyRange a lo hi  => "(Array.sub " ++ a ++ " "
                                ++ pretty_contract_expr_state s lo ++ " ("
                                ++ pretty_contract_expr_state s hi ++ " - "
                                ++ pretty_contract_expr_state s lo ++ "))"
  | CGMake n v           => "(Array.make "
                                ++ pretty_contract_expr_state s n ++ " "
                                ++ pretty_contract_expr_state s v ++ ")"
  (* Ghost map/set atoms (expressions.py:954-956, 994) *)
  | CGMapEmpty           => "(const (None: option int))"
  | CGSetEmpty           => "(const false)"
  (* Ghost tuple atoms *)
  | CGMkTuple2 a b       => "(" ++ pretty_contract_expr_state s a ++ ", "
                                ++ pretty_contract_expr_state s b ++ ")"
  | CGMkTuple3 a b c     => "(" ++ pretty_contract_expr_state s a ++ ", "
                                ++ pretty_contract_expr_state s b ++ ", "
                                ++ pretty_contract_expr_state s c ++ ")"
  | CGMkTuple4 a b c d   => "(" ++ pretty_contract_expr_state s a ++ ", "
                                ++ pretty_contract_expr_state s b ++ ", "
                                ++ pretty_contract_expr_state s c ++ ", "
                                ++ pretty_contract_expr_state s d ++ ")"
  | CGFst t              => "(fst " ++ pretty_contract_expr_state s t ++ ")"
  | CGSnd t              => "(snd " ++ pretty_contract_expr_state s t ++ ")"
  (* Ghost list atoms *)
  | CGNil                => "Nil"
  | CGCons h t           => "(Cons " ++ pretty_contract_expr_state s h
                                ++ " " ++ pretty_contract_expr_state s t ++ ")"
  | _                    => "?contract?"
  end.

(* ===== Int coercion for bool-typed RHS (matches Module 6's _val_is_bool branch) =====

   When assigning a bool-typed expression (a comparison or boolean op)
   to an int slot, Module 6 wraps with `(if <e> then 1 else 0)`. Our
   formal expr's ECmp constructor is the bool-shaped subset (boolean
   ops are not yet in formal expr).
*)
Definition is_bool_expr (e : expr) : bool :=
  match e with
  | ECmp _ _ _ => true
  | _          => false
  end.

Definition coerce_int_rhs (s : aware_state) (e : expr) : string :=
  if is_bool_expr e then
    "(if " ++ pretty_expr_state s e ++ " then 1 else 0)"
  else
    pretty_expr_state s e.

(* ===== Continuation helpers ===== *)

Definition nl : string := String "010" "".

(* Combine body with continuation. When cont is empty, the result
   is exactly `body` (no trailing chars to interfere with proofs);
   when non-empty, append `;\n` and the continuation. *)
Definition concat_with_sep (body cont : string) : string :=
  match cont with
  | EmptyString => body
  | _           => body ++ ";" ++ nl ++ cont
  end.

(* For scoping constructs (let-in, label-in), substitute "()" when
   continuation is empty. *)
Definition scope_body (cont : string) : string :=
  match cont with
  | EmptyString => "()"
  | _           => cont
  end.

(* Emit a list of `invariant { c }` lines, one per element. Module 6
   iterates `invariants` and emits one line each (statements.py:121-128). *)
Fixpoint emit_invariant_lines
         (s : aware_state) (invs : list contract_expr) : string :=
  match invs with
  | nil => ""
  | c :: rest =>
      "invariant { " ++ pretty_contract_expr_state s c ++ " }" ++ nl
        ++ emit_invariant_lines s rest
  end.

(* Same shape for variant lines (statements.py:129-136). *)
Fixpoint emit_variant_lines
         (s : aware_state) (vars : list contract_expr) : string :=
  match vars with
  | nil => ""
  | c :: rest =>
      "variant { " ++ pretty_contract_expr_state s c ++ " }" ++ nl
        ++ emit_variant_lines s rest
  end.

(* ===== Ghost-decl emission (state-aware, scoping form) =====

   Module 6: `let ghost X <binding> in <rest-or-()>` where the
   binding depends on ghost type. Uses the state-aware contract
   printer so ghost atoms (CGCopy, CGSetEmpty, etc.) match Module 6.
   For GTList + CGNil, Module 6 type-annotates as `(Nil: list int)`. *)

Definition emit_ghost_decl_aware
           (s : aware_state) (x : ident) (t : ghost_type)
           (e : ghost_expr) : string :=
  let val := pretty_contract_expr_state s e in
  match t with
  | GTArray => "let ghost " ++ x ++ " = " ++ val ++ " in"
  | GTList  =>
      match e with
      | CGNil => "let ghost " ++ x ++ " = ref (Nil: list int) in"
      | _     => "let ghost " ++ x ++ " = ref " ++ val ++ " in"
      end
  | _       => "let ghost " ++ x ++ " = ref " ++ val ++ " in"
  end.

(* State-aware ghost-assign emission (replaces the structural
   emit_ghost_assign from Phase6L_EmitBlocks.v for byte-diff use). *)
Definition emit_ghost_assign_aware
           (s : aware_state) (x : ident) (t : ghost_type)
           (op : aug_op) (e : ghost_expr) : string :=
  let val := pretty_contract_expr_state s e in
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
  | GTDict =>
      (* Module 6's _handle_ghost_assign_stmt special-cases dict + += with
         a 2-tuple value into a Map.set with `Some v`. *)
      match op, e with
      | AugAdd, CGMkTuple2 k v =>
          "ghost " ++ x ++ " := (Map.set !" ++ x ++ " "
            ++ pretty_contract_expr_state s k ++ " (Some "
            ++ pretty_contract_expr_state s v ++ "))"
      | _, _ => "ghost " ++ x ++ " := " ++ val
      end
  | _ =>
      "ghost " ++ x ++ " := " ++ val
  end.

(* ===== emit_cont: CPS-style state-aware emission =====

   Threads a continuation string through the recursion. For scoping
   constructs the continuation becomes the body (with "()"
   substitution when empty); for non-scoping constructs the
   continuation is appended with ";\n". *)

Fixpoint emit_cont
         (s : aware_state) (ws : whyml_stmt) (cont : string) : string :=
  match ws with
  | WSkip => concat_with_sep "()" cont

  | WAssign x e =>
      let rhs := coerce_int_rhs s e in
      if aware_in x s.(aw_shared_vars) then
        concat_with_sep (x ++ " := " ++ rhs) cont
      else if negb (aware_in x s.(aw_declared_refs)) then
        (* Fresh local — scoping let-in *)
        let prefix :=
          match s.(aw_bounded_int) with
          | Some bits => "let " ++ x ++ " = ref ("
                           ++ rhs
                           ++ " : int" ++ bits ++ ") in" ++ nl
          | None      => "let " ++ x ++ " = ref "
                           ++ rhs ++ " in" ++ nl
          end in
        prefix ++ scope_body cont
      else
        concat_with_sep (x ++ " := " ++ rhs) cont

  | WAugAssign x op e =>
      concat_with_sep
        (x ++ " := !" ++ x ++ " " ++ op_translate_aug op ++ " "
           ++ pretty_expr_state s e) cont

  | WArraySet a i v =>
      let body :=
        if aware_in a s.(aw_array_locals) then
          a ++ "[" ++ pretty_expr_state s i ++ "] <- "
            ++ pretty_expr_state s v
        else
          "subscript_set " ++ a ++ " " ++ pretty_expr_state s i ++ " "
                            ++ pretty_expr_state s v
      in concat_with_sep body cont

  | WSeq w1 w2 =>
      emit_cont s w1 (emit_cont s w2 cont)

  | WIf c t f =>
      (* When the else branch is WSkip, Module 6 omits the else
         clause entirely (no source `else:` in Python). *)
      let body :=
        match f with
        | WSkip => "if " ++ to_bool_state s c ++ " then begin" ++ nl
                   ++ emit_cont s t "" ++ nl ++ "end"
        | _     => "if " ++ to_bool_state s c ++ " then begin" ++ nl
                   ++ emit_cont s t "" ++ nl
                   ++ "end else begin" ++ nl
                   ++ emit_cont s f "" ++ nl ++ "end"
        end
      in concat_with_sep body cont

  | WWhile invs vars c body =>
      concat_with_sep
        ("while " ++ to_bool_state s c ++ " do" ++ nl
           ++ emit_invariant_lines s invs
           ++ emit_variant_lines s vars
           ++ emit_cont s body "" ++ nl
           ++ "done") cont

  | WRaise exc =>
      concat_with_sep ("raise " ++ exc_to_string exc) cont

  | WTryCatch body exc handler =>
      concat_with_sep
        ("try" ++ nl
           ++ emit_cont s body "" ++ nl
           ++ "with " ++ exc ++ " -> " ++ nl
           ++ emit_cont s handler "" ++ nl
           ++ "end") cont

  | WGhostDecl x t e =>
      emit_ghost_decl_aware s x t e ++ nl ++ scope_body cont

  | WGhostAssign x t op e =>
      concat_with_sep (emit_ghost_assign_aware s x t op e) cont

  | WLabel L =>
      "label " ++ L ++ " in" ++ nl ++ scope_body cont

  | WAssert cond _ =>
      (* Spec-level assert (`assert { cond }`). Python `assert` statements
         that Module 6 erases to `()` are converted to WSkip by the
         IR-to-Rocq-AST bridge, so WAssert here represents a true
         spec-level assertion (e.g., critical-section prove_invariant). *)
      concat_with_sep
        ("assert { " ++ pretty_contract_expr_state s cond ++ " }") cont
  | WAssume cond =>
      concat_with_sep
        ("assume { " ++ pretty_contract_expr_state s cond ++ " }") cont
  end.

(* ===== Top-level state-aware emission =====

   Calls emit_cont with empty continuation. *)

Definition emit_stmt_state_aware
           (s : aware_state) (ws : whyml_stmt) : string :=
  emit_cont s ws "".

(* ===== Constructor of default aware_state ===== *)

Definition empty_aware_state : aware_state :=
  {| aw_shared_vars   := nil;
     aw_declared_refs := nil;
     aw_local_refs    := nil;
     aw_array_locals  := nil;
     aw_bounded_int   := None |}.

(* ===== Sanity lemmas =====

   The state-aware printer's output is in the acceptable set
   documented by the structural printer's per-construct lemmas.
   The full correspondence theorem would require structural
   induction; here we record the trivial cases as sanity. *)

Lemma emit_state_aware_skip :
  forall s, emit_stmt_state_aware s WSkip = "()".
Proof. reflexivity. Qed.

Lemma emit_state_aware_skip_with_cont :
  forall s, emit_cont s WSkip "" = "()".
Proof. reflexivity. Qed.
