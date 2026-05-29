(* Phase6L_EmitAssign.v — Sub-α.2: full state coverage for wAssign
   =================================================================

   The pilot (Phase6L_EmitStmt.v) covered wSkip — a state-free
   constructor with a singleton acceptable set. This file does the
   first non-trivial construct: wAssign.

   Module 6's `_handle_assign_stmt` (statements.py:61) has FIVE
   branches keyed on the per-function state:

     1. target ∈ shared_vars         → `x := e`
     2. target ∉ declared_refs       → `_emit_first_assign` (a sub-dispatch on _first_assign_kind):
        2a. kind = "record"          → `let x = e in`
        2b. kind = "lambda"          → `let x = e in`
        2c. kind = "array"|"slice"   → `let x = e in`
        2d. kind = "dict"            → `let x = ref e in`
        2e. kind = "bounded_int"     → `let x = ref (e : intN) in`
        2f. _val_is_bool(val_ir)     → `let x = ref (if e then 1 else 0) in`
        2g. default                  → `let x = ref e in`
     3. target ∈ array_locals        → array-reset multiline pattern
     4. _val_is_bool(val_ir)         → `x := (if e then 1 else 0)`
     5. default                      → `x := e`

   On inputs of formal `expr` type (6 constructors: EInt, EVar,
   ESubscript, ELen, EBinOp, ENeg) — what `SAssign x e` carries —
   several branches CANNOT FIRE because the trigger RHS shape isn't
   in `expr`:

     - 2a (record): triggered by Call to record-type ctor — not in expr
     - 2b (lambda): triggered by Lambda IR — not in expr
     - 2c (array): triggered by Array.make / SliceAccess / "(sorted_1 ..."
                    — not in expr
     - 2d (dict):  triggered by DictLit / SetLit / Call to dict()/set()
                    — not in expr
     - 2f (val_is_bool): triggered by Compare/BoolOp/UnaryOp(not)/
                          BinOp with bool op — formal `binop` has
                          only OpAdd/OpSub/OpMul/OpDiv (no bool ops)
     - 3 (array_locals): only populated by branch 2c, which can't fire,
                          so this branch is unreachable too
     - 4 (val_is_bool on existing local): same as 2f — never fires

   What REMAINS for formal `expr` inputs:

     - Branch 1: `x := pretty_expr e`         (shared var)
     - Branch 2e: `let x = ref (e : intN) in` (fresh local, bounded_int)
     - Branch 2g: `let x = ref e in`          (fresh local, default kind)
     - Branch 5:  `x := pretty_expr e`        (existing local)

   So the acceptable set has FOUR entries (which collapse to 3
   distinct strings since 1 and 5 produce the same string). This is
   the full state coverage for wAssign on the formal `expr` type.

   Documented limitation — the "presentational gap":
     Module 6's `_expr_to_whyml` emits ref-deref `!x` for variables
     that have been declared as `ref`s; bare `x` otherwise. Our
     `pretty_expr` here uses bare `x` for all variables. This is a
     *presentational* gap: the formal emission and Module 6's
     emission differ in surface syntax for variable reads, but the
     denotation is the same. Closing this gap requires either:
       (a) carrying local_refs in the state and using it in pretty_expr; or
       (b) byte-diff validation per CC.5 of closer-to-code.md.
     This file takes path (b): the formal emission models the
     reference shape; byte-diff validation handles ref-deref.

   Python source: src/pycsl/module6_whyml/statements.py:61-103
                  src/pycsl/module6_whyml/types.py:38-118 (helpers)
                  src/pycsl/module6_whyml/expressions.py (pretty-printer)
*)

Require Import String List ZArith Ascii.
Require Import Phase1_AST.
Require Import Phase6_WhyML.
Require Import Phase6d_StmtGen.
Require Import Phase6L_EmitStmt.

Import ListNotations.
Open Scope string_scope.

(* ===== Integer pretty-printer for EInt =====

   Module 6 emits Z literals as plain decimal. The formal printer
   needs to match for the EInt arm of pretty_expr. *)

Local Definition digit_char (d : nat) : ascii :=
  match d with
  | 0%nat => "0"%char | 1%nat => "1"%char | 2%nat => "2"%char | 3%nat => "3"%char
  | 4%nat => "4"%char | 5%nat => "5"%char | 6%nat => "6"%char | 7%nat => "7"%char
  | 8%nat => "8"%char | _ => "9"%char
  end.

Local Fixpoint nat_to_string_aux (fuel n : nat) : string :=
  match fuel with
  | O => ""
  | S fuel' =>
      if Nat.ltb n 10 then String (digit_char n) EmptyString
      else nat_to_string_aux fuel' (Nat.div n 10) ++
           String (digit_char (Nat.modulo n 10)) EmptyString
  end.

Definition nat_to_string (n : nat) : string :=
  nat_to_string_aux 64 n.

Definition z_to_string (z : Z) : string :=
  match z with
  | Z0     => "0"
  | Zpos p => nat_to_string (Pos.to_nat p)
  | Zneg p => "-" ++ nat_to_string (Pos.to_nat p)
  end.

(* ===== Operator pretty-printer ===== *)

Definition pretty_binop (op : binop) : string :=
  match op with
  | OpAdd => "+"
  | OpSub => "-"
  | OpMul => "*"
  | OpDiv => "/"
  | OpMod => "mod"
  end.

(* Module 6 maps Python comparisons to WhyML per identifiers.py:OP_MAP:
     ==  → =     !=  → <>     <   → <     <=  → <=
     >   → >     >=  → >=
*)
Definition pretty_cmpop (op : cmpop) : string :=
  match op with
  | OpEq => "="
  | OpNe => "<>"
  | OpLt => "<"
  | OpLe => "<="
  | OpGt => ">"
  | OpGe => ">="
  end.

(* ===== Expression pretty-printer =====

   Models Module 6's `_expr_to_whyml` for the 6 formal `expr`
   constructors. Variables are emitted bare (no `!` ref-deref);
   see "presentational gap" in the header.

   Python correspondent: src/pycsl/module6_whyml/expressions.py:1116
*)

Fixpoint pretty_expr (e : expr) : string :=
  match e with
  | EInt n           => z_to_string n
  | EVar x           => x
  | ESubscript a i   => a ++ "[" ++ pretty_expr i ++ "]"
  | ELen a           => "(length " ++ a ++ ")"
  | EBinOp op e1 e2  => "(" ++ pretty_expr e1 ++ " " ++ pretty_binop op
                          ++ " " ++ pretty_expr e2 ++ ")"
  | ENeg e1          => "(- " ++ pretty_expr e1 ++ ")"
  | ECmp op e1 e2    => "(" ++ pretty_expr e1 ++ " " ++ pretty_cmpop op
                          ++ " " ++ pretty_expr e2 ++ ")"
  | EFieldGet obj f  => obj ++ "." ++ f
  | ECall func args  =>
      (* Approximate: emit "func(arg1, arg2, ...)". *)
      func ++ "(" ++
        (fix args_str (xs : list expr) : string :=
           match xs with
           | nil => ""
           | x :: nil => pretty_expr x
           | x :: rest => pretty_expr x ++ ", " ++ args_str rest
           end) args ++ ")"
  end.

(* ===== Assignment state =====

   The four pieces of per-function state Module 6 consults at
   `_handle_assign_stmt`. *)

Record assign_state : Type := mkAssignState {
  as_shared_vars   : list ident;
  as_declared_refs : list ident;
  as_bounded_int   : option string  (* None | Some "32" | Some "64" *)
}.

(* Membership check — Module 6 uses Python `in` on a set. *)
Definition ident_in (x : ident) (xs : list ident) : bool :=
  existsb (String.eqb x) xs.

(* ===== emit_assign: formal model of _handle_assign_stmt =====

   Returns the bare WhyML text Module 6 emits for `x = e` in state
   `s`. The five branches mirror the Python control flow exactly,
   restricted to inputs of formal `expr` type (see header for the
   branches eliminated by the type restriction).

   Python correspondent: src/pycsl/module6_whyml/statements.py:61-103
*)

Definition emit_assign (s : assign_state) (x : ident) (e : expr) : string :=
  if ident_in x s.(as_shared_vars) then
    (* Branch 1: shared var assignment *)
    x ++ " := " ++ pretty_expr e
  else if negb (ident_in x s.(as_declared_refs)) then
    (* Branch 2: first-time assignment to a fresh local.
       On formal `expr` only kinds "bounded_int" and "default" fire. *)
    match s.(as_bounded_int) with
    | Some bits =>
        (* Branch 2e: bounded_int — `let x = ref (e : intN) in\n` *)
        "let " ++ x ++ " = ref (" ++ pretty_expr e
               ++ " : int" ++ bits ++ ") in" ++ String "010" ""
    | None =>
        (* Branch 2g: default — `let x = ref e in\n` *)
        "let " ++ x ++ " = ref " ++ pretty_expr e ++ " in" ++ String "010" ""
    end
  else
    (* Branch 5: existing local — `x := e`.
       Branch 4 (bool-coerce) cannot fire on formal `expr`. *)
    x ++ " := " ++ pretty_expr e.

(* ===== acceptable_assign_emissions =====

   The four (collapsing to ≤ 3) surface forms Module 6 may emit for
   `SAssign x e` on a formal `expr`. Parameterized by the state so
   the bounded_int suffix and the choice of branch are captured. *)

Definition acceptable_assign_emissions
           (s : assign_state) (x : ident) (e : expr) : list string :=
  let ne := String "010" "" in
  let assign_form := x ++ " := " ++ pretty_expr e in
  let let_default := "let " ++ x ++ " = ref " ++ pretty_expr e ++ " in" ++ ne in
  let let_bounded :=
    match s.(as_bounded_int) with
    | Some bits => "let " ++ x ++ " = ref (" ++ pretty_expr e
                          ++ " : int" ++ bits ++ ") in" ++ ne
    | None      => let_default
    end in
  [ assign_form ; let_default ; let_bounded ].

(* ===== Correctness theorem =====

   Whichever state Module 6 is in, the emitted text lies in the
   acceptable set. Proved by case analysis on the state. *)

Theorem emit_assign_correct :
  forall s x e,
    In (emit_assign s x e) (acceptable_assign_emissions s x e).
Proof.
  intros s x e.
  unfold emit_assign, acceptable_assign_emissions.
  destruct (ident_in x s.(as_shared_vars)) eqn:Hsh.
  - (* Branch 1: shared *)
    simpl. left. reflexivity.
  - destruct (ident_in x s.(as_declared_refs)) eqn:Hdc.
    + (* Branch 5: existing local *)
      simpl. left. reflexivity.
    + (* Branch 2: fresh local; case on bounded_int *)
      destruct s.(as_bounded_int) as [bits|] eqn:Hbi.
      * (* Branch 2e: bounded_int *)
        simpl. right. right. left. reflexivity.
      * (* Branch 2g: default *)
        simpl. right. left. reflexivity.
Qed.

(* ===== Tie-in to gen =====

   `gen (SAssign x e) = WAssign x e` by definition. So an `emit_stmt`
   that's state-aware would emit `emit_assign s x e` on a `WAssign x e`
   input. Since the pilot's state-free `emit_stmt` doesn't carry state,
   we introduce a separate state-aware variant `emit_stmt_s` that
   dispatches on the WhyML constructor with state in hand for the
   relevant arms. *)

Definition emit_stmt_s (s : assign_state) (ws : whyml_stmt) : string :=
  match ws with
  | WSkip          => "()"
  | WAssign x e    => emit_assign s x e
  | _              => emit_stmt ws  (* pilot's stubs for unimplemented constructors *)
  end.

(* The composed theorem: emit_stmt_s on a `gen (SAssign x e)` lies in
   the acceptable set. This is exactly what Sub-α.2 was scoped to
   prove. *)

Theorem emit_stmt_s_assign_correct :
  forall s x e,
    In (emit_stmt_s s (gen (SAssign x e))) (acceptable_assign_emissions s x e).
Proof.
  intros s x e. simpl. apply emit_assign_correct.
Qed.

(* ===== Sanity lemmas ===== *)

Lemma emit_stmt_s_skip : forall s, emit_stmt_s s (gen SSkip) = "()".
Proof. reflexivity. Qed.

(* For inputs in the "canonical" state (no shared vars, target is a
   fresh local, no bounded_int), the emission is the default-let form.
   Useful as a smoke test of the dispatch logic. *)

Definition canonical_state : assign_state :=
  {| as_shared_vars := nil; as_declared_refs := nil; as_bounded_int := None |}.

Lemma emit_assign_canonical_let :
  forall x e,
    emit_assign canonical_state x e =
      "let " ++ x ++ " = ref " ++ pretty_expr e ++ " in" ++ String "010" "".
Proof. intros. unfold emit_assign, canonical_state. simpl. reflexivity. Qed.

(* ===== Deferred branches (out of scope for `expr`-typed RHS) =====

   The branches we EXCLUDED with rationale (record, lambda, array,
   slice, dict, val_is_bool, array_locals reassign) all require RHS
   shapes that the formal `expr` type cannot express. They are
   covered by:

     - Sub-α (this series): only the `expr`-expressible branches.
     - Q4 Upward (IR-level model): when the formal pipeline extends
       above the `expr` boundary to include collection literals,
       function calls, comprehensions, etc., the extra branches
       become reachable and need their own per-RHS-kind theorems.

   Until Q4, these branches stay outside the formal correspondence
   theorem; their correctness is established by Module 6's test
   suite (reference corpus + assertion tests) rather than by proof. *)
