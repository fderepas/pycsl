(* Phase1b_IrToStmt.v — Q4 U.2 sketch: ir_to_stmt for the simple subset.

   Translates `json_value` (Phase0_IrJson.v's shape mirror of Module 5's
   IR output) into the formal `stmt` type (Phase1_AST.v). This is the
   FIRST SLICE of U.2 — only the simple-subset cases:

     Statements:  Pass, Assign, AugAssign, ArraySet, Return
     Expressions: Number, Var, UnaryOp (negation), BinOp, ECmp (via Compare),
                  Subscript (Var only), Call (len only)
     Sequence:    list of statements → right-leaning SSeq chain

   Status (2026-05-29):
   - Pure structural converter; no semantic theorems yet.
   - U.3 (`validate_ir_correspondence`) and U.5 (`py_module5_emit ast =
     Some j → ir_to_stmt j ≠ None`) are deferred to follow-up sessions.
   - Compound statements (If/While/Try/Raise/Assert/Label/GhostAssign/
     CriticalSection) are deferred — they're in the Python converter
     at `bin/ir-to-rocq-ast.py` but not modelled here yet.

   Reuses dispatch structure from `bin/ir-to-rocq-ast.py`. *)

Require Import ZArith String List Bool.
Require Import Phase0_IrJson.
Require Import Phase1_AST.
Open Scope string_scope.

(* ===== Helpers: extract typed fields from json_value ===== *)

(* find_assoc: look up a key in a list of (key, value) pairs. *)
Fixpoint find_assoc (key : string) (kvs : list (string * json_value))
    : option json_value :=
  match kvs with
  | nil => None
  | (k, v) :: rest =>
      if String.eqb k key then Some v else find_assoc key rest
  end.

(* json_field_get: extract a named field from a JsonObject. *)
Definition json_field_get (key : string) (obj : json_value)
    : option json_value :=
  match obj with
  | JsonObject kvs => find_assoc key kvs
  | _              => None
  end.

(* json_to_string / json_to_z / json_to_list: type projections. *)
Definition json_to_string (v : json_value) : option string :=
  match v with JsonString s => Some s | _ => None end.

Definition json_to_z (v : json_value) : option Z :=
  match v with JsonInt n => Some n | _ => None end.

Definition json_to_list (v : json_value) : option (list json_value) :=
  match v with JsonList xs => Some xs | _ => None end.

(* Map an option-returning function over a list, returning None if any
   element maps to None. *)
Fixpoint option_map_list {A B : Type} (f : A -> option B) (xs : list A)
    : option (list B) :=
  match xs with
  | nil => Some nil
  | x :: rest =>
      match f x, option_map_list f rest with
      | Some y, Some ys => Some (y :: ys)
      | _, _            => None
      end
  end.

(* ===== binop / aug_op string → constructor maps ===== *)

(* Mirrors BINOP_MAP in bin/ir-to-rocq-ast.py.
   Module 5 emits Python's `//` integer division as "div" and
   plain `/` as "/". We map both to OpDiv (the formal `expr`
   has no separate float division — runtime expressions are
   integer-only in PyCSL). *)
Definition string_to_binop (s : string) : option binop :=
  if String.eqb s "+"   then Some OpAdd
  else if String.eqb s "-"   then Some OpSub
  else if String.eqb s "*"   then Some OpMul
  else if String.eqb s "/"   then Some OpDiv
  else if String.eqb s "div" then Some OpDiv
  else if String.eqb s "//"  then Some OpDiv
  else if String.eqb s "%"   then Some OpMod
  else if String.eqb s "mod" then Some OpMod
  else None.

(* Mirrors CMPOP_MAP in bin/ir-to-rocq-ast.py. *)
Definition string_to_cmpop (s : string) : option cmpop :=
  if String.eqb s "=="  then Some OpEq
  else if String.eqb s "!="  then Some OpNe
  else if String.eqb s "<"   then Some OpLt
  else if String.eqb s "<="  then Some OpLe
  else if String.eqb s ">"   then Some OpGt
  else if String.eqb s ">="  then Some OpGe
  else None.

(* For SAugAssign: the formal AST uses binop (not aug_op).
   The Python AUG_OP_MAP only allows {+, -, *, /}. *)
Definition aug_string_to_binop (s : string) : option binop :=
  string_to_binop s.

(* For SGhostAssign: the formal AST uses aug_op (only AugAdd/Sub/Mul).
   Mirrors GHOST_AUG_OP_MAP in bin/ir-to-rocq-ast.py. *)
Definition string_to_aug_op (s : string) : option aug_op :=
  if String.eqb s "+=" then Some AugAdd
  else if String.eqb s "-=" then Some AugSub
  else if String.eqb s "*=" then Some AugMul
  else None.

(* Mirrors GHOST_TYPE_MAP in bin/ir-to-rocq-ast.py. *)
Definition string_to_ghost_type (s : string) : option ghost_type :=
  if String.eqb s "int" then Some GTInt
  else if String.eqb s "string" then Some GTString
  else if String.eqb s "array" then Some GTArray
  else if String.eqb s "ghost_dict" then Some GTDict
  else if String.eqb s "ghost_list" then Some GTList
  else if String.eqb s "ghost_set" then Some GTSet
  else if String.eqb s "tuple2" then Some GTTuple2
  else if String.eqb s "tuple3" then Some GTTuple3
  else if String.eqb s "tuple4" then Some GTTuple4
  else None.

(* ===== ir_to_expr: convert IR JSON expression to formal expr =====

   Mirrors conv_expr() in bin/ir-to-rocq-ast.py for the simple subset.

   Implementation note: the recursion goes through `json_field_get`,
   which Coq's syntactic termination checker cannot see as
   structurally decreasing on `json_value`. We use the standard
   `fuel : nat` pattern — the recursion is structural on fuel.
   Real-world IR depths are bounded; a large constant (e.g. 1000)
   suffices for any practical Module 5 output. *)

Fixpoint ir_to_expr (fuel : nat) (e : json_value) : option expr :=
  match fuel with
  | O => None
  | S n =>
    let dispatch (t : string) : option expr :=
      if String.eqb t "Number" then
        match json_field_get "value" e with
        | Some v => match json_to_z v with
                    | Some k => Some (EInt k)
                    | None   => None
                    end
        | None   => None
        end
      else if String.eqb t "Var" then
        match json_field_get "name" e with
        | Some v => match json_to_string v with
                    | Some s => Some (EVar s)
                    | None   => None
                    end
        | None   => None
        end
      else if String.eqb t "UnaryOp" then
        (* Only "-" (negation) supported. Module 5 emits the operand
           under either "operand" or "expr" depending on context;
           accept both. *)
        let operand_opt :=
          match json_field_get "operand" e with
          | Some v => Some v
          | None   => json_field_get "expr" e
          end in
        match json_field_get "op" e, operand_opt with
        | Some opv, Some operand =>
            match json_to_string opv with
            | Some "-" =>
                match ir_to_expr n operand with
                | Some e' => Some (ENeg e')
                | None    => None
                end
            | Some "+" =>
                (* Unary plus = identity. *)
                ir_to_expr n operand
            | _ => None
            end
        | _, _ => None
        end
      else if String.eqb t "BinOp" then
        match json_field_get "op" e, json_field_get "left" e, json_field_get "right" e with
        | Some opv, Some lv, Some rv =>
            match json_to_string opv with
            | Some opstr =>
                match string_to_binop opstr, ir_to_expr n lv, ir_to_expr n rv with
                | Some op, Some le, Some re => Some (EBinOp op le re)
                | _, _, _ =>
                    (* Fall through: try as cmpop *)
                    match string_to_cmpop opstr, ir_to_expr n lv, ir_to_expr n rv with
                    | Some cop, Some le, Some re => Some (ECmp cop le re)
                    | _, _, _ => None
                    end
                end
            | None => None
            end
        | _, _, _ => None
        end
      else if String.eqb t "Subscript" then
        (* Only Var-based subscript: arr is a Var, index is arbitrary expr. *)
        match json_field_get "value" e, json_field_get "index" e with
        | Some arrv, Some idxv =>
            match json_field_get "type" arrv with
            | Some arrtype =>
                match json_to_string arrtype with
                | Some "Var" =>
                    match json_field_get "name" arrv with
                    | Some namev =>
                        match json_to_string namev, ir_to_expr n idxv with
                        | Some nm, Some ie => Some (ESubscript nm ie)
                        | _, _ => None
                        end
                    | None => None
                    end
                | _ => None
                end
            | None => None
            end
        | _, _ => None
        end
      else if String.eqb t "Call" then
        (* `len(arr)` with arr a Var → ELen (special-cased for the
           builtin). Other calls become ECall func [args...].
           Mirrors bin/ir-to-rocq-ast.py's Call handler. *)
        match json_field_get "func" e, json_field_get "args" e with
        | Some funcv, Some argsv =>
            match json_to_string funcv, json_to_list argsv with
            | Some "len", Some (arg :: nil) =>
                (* Special case: len(Var(name)) → ELen name *)
                match json_field_get "type" arg with
                | Some argtype =>
                    match json_to_string argtype with
                    | Some "Var" =>
                        match json_field_get "name" arg with
                        | Some nv =>
                            match json_to_string nv with
                            | Some nm => Some (ELen nm)
                            | None    => None
                            end
                        | None => None
                        end
                    | _ =>
                        (* len of non-Var: fall back to ECall *)
                        match option_map_list (ir_to_expr n) (arg :: nil) with
                        | Some args => Some (ECall "len" args)
                        | None      => None
                        end
                    end
                | None => None
                end
            | Some fname, Some args =>
                (* General Call: ECall fname [converted args].
                   If any arg fails to convert, the whole Call returns None. *)
                match option_map_list (ir_to_expr n) args with
                | Some converted => Some (ECall fname converted)
                | None           => None
                end
            | _, _ => None
            end
        | _, _ => None
        end
      else if String.eqb t "FieldGet" then
        (* EFieldGet obj f — class field read at the expr level.
           Added with the Q4 U.4 expr extension (2026-05-29). *)
        match json_field_get "object" e, json_field_get "field" e with
        | Some objv, Some fv =>
            match json_to_string objv, json_to_string fv with
            | Some obj, Some f => Some (EFieldGet obj f)
            | _, _ => None
            end
        | _, _ => None
        end
      else if String.eqb t "NamedExpr" then
        (* Python's walrus `(z := v)` — evaluates v and binds z to it,
           then returns v. We can't model the binding side effect in
           pure expr conversion; convert to the value expression only.
           This is a semantic approximation; downstream code must
           account for the lost binding. *)
        match json_field_get "value" e with
        | Some v => ir_to_expr n v
        | None   => None
        end
      else None
    in
    match json_field_get "type" e with
    | Some tv =>
        match json_to_string tv with
        | Some t => dispatch t
        | None   => None
        end
    | None => None
    end
  end.

(* Default fuel for top-level callers: 1000 is more than enough for
   any practical Module 5 output. *)
Definition default_expr_fuel : nat := 1000%nat.

(* ===== ir_to_contract_expr: convert IR JSON contract-expression to formal contract_expr =====

   Used for SWhile.inv, SWhile.var, SAssert.cond and ghost expressions.
   Covers the subset that Module 5 emits for the simple test cases:
   - Number, Var → CInt, CVar
   - BinOp (arithmetic) → CBinOp
   - Compare/BinOp (comparison) → CEq/CNe/CLt/CLe/CGt/CGe
   - logical (and/or/not) → CAnd/COr/CNot
   - UnaryOp "-" → CNeg
   - Result, Old, Length, Subscript → CResult/COld/CLength/CSubscript
   - BoolLit (true/false) → CBoolLit

   Compound + quantifiers (forall/exists, implies/iff, chained subscript)
   deferred to follow-up sessions. *)

Fixpoint ir_to_contract_expr (fuel : nat) (e : json_value) : option contract_expr :=
  match fuel with
  | O => None
  | S n =>
    let dispatch (t : string) : option contract_expr :=
      if String.eqb t "Number" then
        match json_field_get "value" e with
        | Some v => match json_to_z v with
                    | Some k => Some (CInt k)
                    | None   => None
                    end
        | None   => None
        end
      else if String.eqb t "Var" then
        match json_field_get "name" e with
        | Some v => match json_to_string v with
                    | Some s => Some (CVar s)
                    | None   => None
                    end
        | None   => None
        end
      else if String.eqb t "Result" then Some CResult
      else if String.eqb t "BoolLit" then
        match json_field_get "value" e with
        | Some v => match v with
                    | JsonBool b => Some (CBoolLit b)
                    | _ => None
                    end
        | None => None
        end
      else if String.eqb t "Length" then
        match json_field_get "name" e with
        | Some v => match json_to_string v with
                    | Some s => Some (CLength s)
                    | None   => None
                    end
        | None   => None
        end
      else if String.eqb t "Subscript" then
        match json_field_get "value" e, json_field_get "index" e with
        | Some arrv, Some idxv =>
            match json_field_get "type" arrv with
            | Some arrtype =>
                match json_to_string arrtype with
                | Some "Var" =>
                    match json_field_get "name" arrv with
                    | Some namev =>
                        match json_to_string namev,
                              ir_to_contract_expr n idxv with
                        | Some nm, Some ie => Some (CSubscript nm ie)
                        | _, _ => None
                        end
                    | None => None
                    end
                | _ => None
                end
            | None => None
            end
        | _, _ => None
        end
      else if String.eqb t "Old" then
        match json_field_get "operand" e with
        | Some v => match ir_to_contract_expr n v with
                    | Some ce => Some (COld ce)
                    | None    => None
                    end
        | None   => None
        end
      else if String.eqb t "UnaryOp" then
        (* Module 5 emits operand under "operand" or "expr". *)
        let operand_opt :=
          match json_field_get "operand" e with
          | Some v => Some v
          | None   => json_field_get "expr" e
          end in
        match json_field_get "op" e, operand_opt with
        | Some opv, Some operand =>
            match json_to_string opv with
            | Some "-" =>
                match ir_to_contract_expr n operand with
                | Some e' => Some (CNeg e')
                | None    => None
                end
            | Some "not" =>
                match ir_to_contract_expr n operand with
                | Some e' => Some (CNot e')
                | None    => None
                end
            | Some "+" =>
                (* Unary plus = identity. *)
                ir_to_contract_expr n operand
            | _ => None
            end
        | _, _ => None
        end
      else if String.eqb t "BinOp" then
        match json_field_get "op" e,
              json_field_get "left" e,
              json_field_get "right" e with
        | Some opv, Some lv, Some rv =>
            match json_to_string opv with
            | Some opstr =>
                match ir_to_contract_expr n lv, ir_to_contract_expr n rv with
                | Some le, Some re =>
                    (* Try arithmetic binop first *)
                    match string_to_binop opstr with
                    | Some op => Some (CBinOp op le re)
                    | None =>
                        (* Try comparison *)
                        if String.eqb opstr "==" then Some (CEq le re)
                        else if String.eqb opstr "!=" then Some (CNe le re)
                        else if String.eqb opstr "<"  then Some (CLt le re)
                        else if String.eqb opstr "<=" then Some (CLe le re)
                        else if String.eqb opstr ">"  then Some (CGt le re)
                        else if String.eqb opstr ">=" then Some (CGe le re)
                        (* Try logical *)
                        else if String.eqb opstr "and" then Some (CAnd le re)
                        else if String.eqb opstr "or"  then Some (COr le re)
                        else if String.eqb opstr "implies" then Some (CImplies le re)
                        else if String.eqb opstr "iff" then Some (CIff le re)
                        else None
                    end
                | _, _ => None
                end
            | None => None
            end
        | _, _, _ => None
        end
      else if String.eqb t "String" then
        (* CStringLit *)
        match json_field_get "value" e with
        | Some v => match json_to_string v with
                    | Some s => Some (CStringLit s)
                    | None   => None
                    end
        | None   => None
        end
      else if String.eqb t "Forall" then
        (* CForall x body — IR uses "var" / "body" fields *)
        match json_field_get "var" e, json_field_get "body" e with
        | Some xv, Some bodyv =>
            match json_to_string xv, ir_to_contract_expr n bodyv with
            | Some x, Some b => Some (CForall x b)
            | _, _ => None
            end
        | _, _ => None
        end
      else if String.eqb t "Exists" then
        match json_field_get "var" e, json_field_get "body" e with
        | Some xv, Some bodyv =>
            match json_to_string xv, ir_to_contract_expr n bodyv with
            | Some x, Some b => Some (CExists x b)
            | _, _ => None
            end
        | _, _ => None
        end
      else if String.eqb t "ChainedSubscript" then
        (* CChainedSubscript arr i j — IR uses "arr" / "index1" / "index2" *)
        match json_field_get "arr" e,
              json_field_get "index1" e,
              json_field_get "index2" e with
        | Some arrv, Some i1v, Some i2v =>
            match json_to_string arrv,
                  ir_to_contract_expr n i1v,
                  ir_to_contract_expr n i2v with
            | Some arr, Some i1, Some i2 =>
                Some (CChainedSubscript arr i1 i2)
            | _, _, _ => None
            end
        | _, _, _ => None
        end
      else if String.eqb t "At" then
        (* CAt e label — IR uses "expr" / "label" *)
        match json_field_get "expr" e, json_field_get "label" e with
        | Some expv, Some lblv =>
            match ir_to_contract_expr n expv, json_to_string lblv with
            | Some ce, Some lbl => Some (CAt ce lbl)
            | _, _ => None
            end
        | _, _ => None
        end
      (* ===== Ghost dict/map atoms ===== *)
      else if String.eqb t "MapEmpty" then Some CGMapEmpty
      else if String.eqb t "GhostMapEmpty" then Some CGMapEmpty
      else if String.eqb t "MapGet" then
        (* Module 5 emits the dict argument under either "map" or "dict". *)
        let map_opt :=
          match json_field_get "map" e with
          | Some v => Some v
          | None   => json_field_get "dict" e
          end in
        match map_opt, json_field_get "key" e with
        | Some mv, Some kv =>
            match ir_to_contract_expr n mv, ir_to_contract_expr n kv with
            | Some m, Some k => Some (CGMapGet m k)
            | _, _ => None
            end
        | _, _ => None
        end
      else if String.eqb t "MapSet" then
        let map_opt :=
          match json_field_get "map" e with
          | Some v => Some v
          | None   => json_field_get "dict" e
          end in
        match map_opt,
              json_field_get "key" e,
              json_field_get "value" e with
        | Some mv, Some kv, Some vv =>
            match ir_to_contract_expr n mv,
                  ir_to_contract_expr n kv,
                  ir_to_contract_expr n vv with
            | Some m, Some k, Some v => Some (CGMapSet m k v)
            | _, _, _ => None
            end
        | _, _, _ => None
        end
      else if String.eqb t "HasKey" then
        let map_opt :=
          match json_field_get "map" e with
          | Some v => Some v
          | None   => json_field_get "dict" e
          end in
        match map_opt, json_field_get "key" e with
        | Some mv, Some kv =>
            match ir_to_contract_expr n mv, ir_to_contract_expr n kv with
            | Some m, Some k => Some (CGHasKey m k)
            | _, _ => None
            end
        | _, _ => None
        end
      (* ===== Ghost list atoms ===== *)
      else if String.eqb t "Nil" then Some CGNil
      else if String.eqb t "GhostNil" then Some CGNil
      else if String.eqb t "GhostCons" || String.eqb t "Cons" then
        match json_field_get "head" e, json_field_get "tail" e with
        | Some hv, Some tv =>
            match ir_to_contract_expr n hv, ir_to_contract_expr n tv with
            | Some h, Some t => Some (CGCons h t)
            | _, _ => None
            end
        | _, _ => None
        end
      else if String.eqb t "GhostListLen" then
        match json_field_get "list" e with
        | Some lv =>
            match ir_to_contract_expr n lv with
            | Some l => Some (CGListLen l)
            | None   => None
            end
        | None => None
        end
      (* ===== Ghost set atoms ===== *)
      else if String.eqb t "SetEmpty" then Some CGSetEmpty
      else if String.eqb t "GhostSetEmpty" then Some CGSetEmpty
      else if String.eqb t "GhostSetAdd" || String.eqb t "SetAdd" then
        match json_field_get "elem" e, json_field_get "set" e with
        | Some ev, Some sv =>
            match ir_to_contract_expr n ev, ir_to_contract_expr n sv with
            | Some el, Some s => Some (CGSetAdd el s)
            | _, _ => None
            end
        | _, _ => None
        end
      else if String.eqb t "GhostSetMem" || String.eqb t "SetMem" then
        match json_field_get "elem" e, json_field_get "set" e with
        | Some ev, Some sv =>
            match ir_to_contract_expr n ev, ir_to_contract_expr n sv with
            | Some el, Some s => Some (CGSetMem el s)
            | _, _ => None
            end
        | _, _ => None
        end
      else if String.eqb t "GhostSetCard" || String.eqb t "SetCard" then
        match json_field_get "set" e with
        | Some sv =>
            match ir_to_contract_expr n sv with
            | Some s => Some (CGSetCard s)
            | None   => None
            end
        | None => None
        end
      (* ===== Ghost tuple atoms ===== *)
      else if String.eqb t "MkTuple" then
        (* Python `MkTuple` uses `elts` list of 2/3/4 elements,
           mapped to CGMkTuple2/3/4 by arity. *)
        match json_field_get "elts" e with
        | Some eltsv =>
            match json_to_list eltsv with
            | Some (a :: b :: nil) =>
                match ir_to_contract_expr n a, ir_to_contract_expr n b with
                | Some ca, Some cb => Some (CGMkTuple2 ca cb)
                | _, _ => None
                end
            | Some (a :: b :: c :: nil) =>
                match ir_to_contract_expr n a,
                      ir_to_contract_expr n b,
                      ir_to_contract_expr n c with
                | Some ca, Some cb, Some cc => Some (CGMkTuple3 ca cb cc)
                | _, _, _ => None
                end
            | Some (a :: b :: c :: d :: nil) =>
                match ir_to_contract_expr n a,
                      ir_to_contract_expr n b,
                      ir_to_contract_expr n c,
                      ir_to_contract_expr n d with
                | Some ca, Some cb, Some cc, Some cd =>
                    Some (CGMkTuple4 ca cb cc cd)
                | _, _, _, _ => None
                end
            | _ => None
            end
        | None => None
        end
      else if String.eqb t "FstExpr" then
        match json_field_get "tuple" e with
        | Some tv =>
            match ir_to_contract_expr n tv with
            | Some t => Some (CGFst t)
            | None   => None
            end
        | None => None
        end
      else if String.eqb t "SndExpr" then
        match json_field_get "tuple" e with
        | Some tv =>
            match ir_to_contract_expr n tv with
            | Some t => Some (CGSnd t)
            | None   => None
            end
        | None => None
        end
      else if String.eqb t "ProjExpr" then
        (* ProjExpr tuple_expr index → CGFst/CGSnd/CGTrd/CGFth by index. *)
        match json_field_get "tuple" e, json_field_get "index" e with
        | Some tv, Some idxv =>
            match ir_to_contract_expr n tv, json_to_z idxv with
            | Some te, Some 0%Z => Some (CGFst te)
            | Some te, Some 1%Z => Some (CGSnd te)
            | Some te, Some 2%Z => Some (CGTrd te)
            | Some te, Some 3%Z => Some (CGFth te)
            | _, _ => None
            end
        | _, _ => None
        end
      else if String.eqb t "IsSorted" then
        match json_field_get "arr" e,
              json_field_get "lo" e,
              json_field_get "hi" e with
        | Some av, Some lov, Some hiv =>
            match json_to_string av,
                  ir_to_contract_expr n lov,
                  ir_to_contract_expr n hiv with
            | Some arr, Some lo, Some hi => Some (CIsSorted arr lo hi)
            | _, _, _ => None
            end
        | _, _, _ => None
        end
      else if String.eqb t "Sum" then
        match json_field_get "arr" e,
              json_field_get "lo" e,
              json_field_get "hi" e with
        | Some av, Some lov, Some hiv =>
            match json_to_string av,
                  ir_to_contract_expr n lov,
                  ir_to_contract_expr n hiv with
            | Some arr, Some lo, Some hi => Some (CSum arr lo hi)
            | _, _, _ => None
            end
        | _, _, _ => None
        end
      else if String.eqb t "Slice" then
        match json_field_get "arr" e,
              json_field_get "lo" e,
              json_field_get "hi" e with
        | Some av, Some lov, Some hiv =>
            match json_to_string av,
                  ir_to_contract_expr n lov,
                  ir_to_contract_expr n hiv with
            | Some arr, Some lo, Some hi => Some (CSlice arr lo hi)
            | _, _, _ => None
            end
        | _, _, _ => None
        end
      else if String.eqb t "In" then
        (* CIn elem container *)
        match json_field_get "elem" e, json_field_get "container" e with
        | Some ev, Some cv =>
            match ir_to_contract_expr n ev, ir_to_contract_expr n cv with
            | Some el, Some c => Some (CIn el c)
            | _, _ => None
            end
        | _, _ => None
        end
      else if String.eqb t "NotIn" then
        match json_field_get "elem" e, json_field_get "container" e with
        | Some ev, Some cv =>
            match ir_to_contract_expr n ev, ir_to_contract_expr n cv with
            | Some el, Some c => Some (CNotIn el c)
            | _, _ => None
            end
        | _, _ => None
        end
      (* ===== Ghost string atoms ===== *)
      else if String.eqb t "StrConcat" then
        match json_field_get "left" e, json_field_get "right" e with
        | Some lv, Some rv =>
            match ir_to_contract_expr n lv, ir_to_contract_expr n rv with
            | Some l, Some r => Some (CGStrConcat l r)
            | _, _ => None
            end
        | _, _ => None
        end
      else if String.eqb t "StrLength" then
        match json_field_get "string" e with
        | Some sv =>
            match ir_to_contract_expr n sv with
            | Some s => Some (CGStrLen s)
            | None   => None
            end
        | None => None
        end
      (* ===== Ghost array atoms (CGCopy / CGMake / CGCopyRange) ===== *)
      else if String.eqb t "GhostCopy" then
        match json_field_get "arr" e with
        | Some av =>
            match json_to_string av with
            | Some arr => Some (CGCopy arr)
            | None     => None
            end
        | None => None
        end
      else if String.eqb t "GhostMake" then
        match json_field_get "size" e, json_field_get "default" e with
        | Some sv, Some dv =>
            match ir_to_contract_expr n sv, ir_to_contract_expr n dv with
            | Some s, Some d => Some (CGMake s d)
            | _, _ => None
            end
        | _, _ => None
        end
      else if String.eqb t "GhostCopyRange" then
        match json_field_get "arr" e,
              json_field_get "lo" e,
              json_field_get "hi" e with
        | Some av, Some lov, Some hiv =>
            match json_to_string av,
                  ir_to_contract_expr n lov,
                  ir_to_contract_expr n hiv with
            | Some arr, Some lo, Some hi => Some (CGCopyRange arr lo hi)
            | _, _, _ => None
            end
        | _, _, _ => None
        end
      else None
    in
    match json_field_get "type" e with
    | Some tv =>
        match json_to_string tv with
        | Some t => dispatch t
        | None   => None
        end
    | None => None
    end
  end.

Definition default_contract_fuel : nat := 1000%nat.

(* ===== ir_to_stmt: convert IR JSON statement to formal stmt =====

   Mirrors conv_stmt() in bin/ir-to-rocq-ast.py for the simple subset.
   Compound statements (If/While/Try/Raise/Assert/Label/GhostAssign/
   CriticalSection) return None for now — extending coverage is the
   next slice. *)

(* ===== ir_to_stmt_n: unified fuel-based dispatcher =====

   Handles BOTH JsonList (right-leaning SSeq fold) AND object-shaped
   statements (with a "stmt" discriminator). The fuel parameter
   bounds the depth of nested compound statements (If body containing
   another If, etc.). 1000 is enough for any practical Module 5 output.

   For JsonList: the inner `fix go` is structurally recursive on the
   list, calling `ir_to_stmt_n` (with decremented fuel) on each
   element. This lets us avoid mutual recursion. *)
Fixpoint ir_to_stmt_n (fuel : nat) (j : json_value) : option stmt :=
  match fuel with
  | O => None
  | S n =>
    match j with
    | JsonList ss =>
        (* Right-leaning SSeq fold. *)
        (fix fold_seq (xs : list json_value) : option stmt :=
          match xs with
          | nil       => Some SSkip
          | s :: nil  => ir_to_stmt_n n s
          | s :: rest =>
              match ir_to_stmt_n n s, fold_seq rest with
              | Some sh, Some st => Some (SSeq sh st)
              | _, _             => None
              end
          end) ss
    | _ =>
        (* Object-shaped statement: dispatch on "stmt" field. *)
        match json_field_get "stmt" j with
        | Some tv =>
            match json_to_string tv with
            | Some t =>
                if String.eqb t "Pass" then Some SSkip
                else if String.eqb t "Expr" then
                  (* Bare expression statement (typically a method call
                     evaluated for side effects). Formal model erases to
                     SSkip — ECall has no state effect at this layer. *)
                  Some SSkip
                else if String.eqb t "Break" then Some SBreak
                else if String.eqb t "Continue" then Some SContinue
                else if String.eqb t "Assign" then
                  match json_field_get "target" j, json_field_get "value" j with
                  | Some tgt, Some valv =>
                      match json_to_string tgt,
                            ir_to_expr default_expr_fuel valv with
                      | Some name, Some e => Some (SAssign name e)
                      | _, _ => None
                      end
                  | _, _ => None
                  end
                else if String.eqb t "AugAssign" then
                  match json_field_get "target" j,
                        json_field_get "op" j,
                        json_field_get "value" j with
                  | Some tgt, Some opv, Some valv =>
                      match json_to_string tgt, json_to_string opv with
                      | Some name, Some opstr =>
                          match aug_string_to_binop opstr,
                                ir_to_expr default_expr_fuel valv with
                          | Some op, Some e => Some (SAugAssign name op e)
                          | _, _ => None
                          end
                      | _, _ => None
                      end
                  | _, _, _ => None
                  end
                else if String.eqb t "ArraySet" then
                  match json_field_get "array" j,
                        json_field_get "index" j,
                        json_field_get "value" j with
                  | Some arrv, Some idxv, Some valv =>
                      match json_field_get "type" arrv with
                      | Some arrtype =>
                          match json_to_string arrtype with
                          | Some "Var" =>
                              match json_field_get "name" arrv with
                              | Some namev =>
                                  match json_to_string namev,
                                        ir_to_expr default_expr_fuel idxv,
                                        ir_to_expr default_expr_fuel valv with
                                  | Some nm, Some ie, Some ve =>
                                      Some (SArraySet nm ie ve)
                                  | _, _, _ => None
                                  end
                              | None => None
                              end
                          | _ => None
                          end
                      | None => None
                      end
                  | _, _, _ => None
                  end
                else if String.eqb t "Return" then
                  match json_field_get "value" j with
                  | Some valv =>
                      match ir_to_expr default_expr_fuel valv with
                      | Some e => Some (SReturn e)
                      | None   => None
                      end
                  | None => None
                  end
                else if String.eqb t "If" then
                  match json_field_get "test" j,
                        json_field_get "body" j,
                        json_field_get "orelse" j with
                  | Some testv, Some bodyv, Some orelsev =>
                      match ir_to_expr default_expr_fuel testv,
                            ir_to_stmt_n n bodyv,
                            ir_to_stmt_n n orelsev with
                      | Some c, Some b, Some o => Some (SIf c b o)
                      | _, _, _ => None
                      end
                  | _, _, _ => None
                  end
                else if String.eqb t "While" then
                  (* Module 5 emits invariants/variants as lists.
                     The formal SWhile takes single inv/var; we use
                     the FIRST element of each list (matching c_first
                     and head-of-conjunction conventions). Missing
                     lists default to CBoolLit true. *)
                  match json_field_get "test" j, json_field_get "body" j with
                  | Some testv, Some bodyv =>
                      let inv_opt :=
                        match json_field_get "invariants" j with
                        | Some inv_list_v =>
                            match json_to_list inv_list_v with
                            | Some (first :: _) =>
                                ir_to_contract_expr default_contract_fuel first
                            | _ => Some (CBoolLit true)
                            end
                        | None => Some (CBoolLit true)
                        end in
                      let var_opt :=
                        match json_field_get "variants" j with
                        | Some var_list_v =>
                            match json_to_list var_list_v with
                            | Some (first :: _) =>
                                ir_to_contract_expr default_contract_fuel first
                            | _ => Some (CInt 0)
                            end
                        | None => Some (CInt 0)
                        end in
                      match inv_opt, var_opt,
                            ir_to_expr default_expr_fuel testv,
                            ir_to_stmt_n n bodyv with
                      | Some inv, Some var, Some c, Some b =>
                          Some (SWhile inv var c b)
                      | _, _, _, _ => None
                      end
                  | _, _ => None
                  end
                else if String.eqb t "Assert" then
                  match json_field_get "test" j with
                  | Some testv =>
                      match ir_to_contract_expr default_contract_fuel testv with
                      | Some c =>
                          let msg :=
                            match json_field_get "msg" j with
                            | Some mv => match json_to_string mv with
                                         | Some s => s
                                         | None   => ""
                                         end
                            | None => ""
                            end in
                          Some (SAssert c msg)
                      | None => None
                      end
                  | None => None
                  end
                else if String.eqb t "Label" then
                  match json_field_get "name" j with
                  | Some nv => match json_to_string nv with
                               | Some s => Some (SLabel s)
                               | None   => None
                               end
                  | None    => None
                  end
                else if String.eqb t "Raise" then
                  match json_field_get "exc_type" j with
                  | Some ev => match json_to_string ev with
                               | Some s => Some (SRaise s)
                               | None   => None
                               end
                  | None    => Some (SRaise "PyCSL_Exception")
                  end
                else if String.eqb t "Try" then
                  (* Single-handler form only. *)
                  match json_field_get "body" j, json_field_get "handlers" j with
                  | Some bodyv, Some handlers_v =>
                      match json_to_list handlers_v with
                      | Some (handler :: nil) =>
                          match json_field_get "exc_type" handler,
                                json_field_get "body" handler with
                          | Some etv, Some hbodyv =>
                              match json_to_string etv,
                                    ir_to_stmt_n n bodyv,
                                    ir_to_stmt_n n hbodyv with
                              | Some exc, Some b, Some h =>
                                  Some (STryCatch b exc h)
                              | _, _, _ => None
                              end
                          | _, _ => None
                          end
                      | _ => None
                      end
                  | _, _ => None
                  end
                else if String.eqb t "CriticalSection" then
                  (* Formal SCritical mutex body — concurrency-out-of-scope
                     for Hoare WP; assume_invariant/prove_invariant from
                     the IR are dropped at this layer. *)
                  match json_field_get "mutex" j, json_field_get "body" j with
                  | Some mv, Some bodyv =>
                      match json_to_string mv, ir_to_stmt_n n bodyv with
                      | Some m, Some b => Some (SCritical m b)
                      | _, _ => None
                      end
                  | _, _ => None
                  end
                else if String.eqb t "GhostAssign" then
                  (* op="=" → SGhostDecl; op in {+=,-=,*=} → SGhostAssign. *)
                  match json_field_get "target" j,
                        json_field_get "op" j,
                        json_field_get "ghost_type" j,
                        json_field_get "value" j with
                  | Some tgt, Some opv, Some gtv, Some valv =>
                      match json_to_string tgt,
                            json_to_string opv,
                            json_to_string gtv with
                      | Some name, Some opstr, Some gtstr =>
                          match string_to_ghost_type gtstr,
                                ir_to_contract_expr default_contract_fuel valv with
                          | Some gt, Some ce =>
                              if String.eqb opstr "=" then
                                Some (SGhostDecl name gt ce)
                              else
                                match string_to_aug_op opstr with
                                | Some aug => Some (SGhostAssign name gt aug ce)
                                | None     => None
                                end
                          | _, _ => None
                          end
                      | _, _, _ => None
                      end
                  | _, _, _, _ => None
                  end
                else if String.eqb t "FieldAssign" then
                  (* SFieldAssign self_id f e — self.f = e.
                     The RHS must be a simple expr (formal expr
                     doesn't model FieldGet); if the IR's value
                     contains FieldGet, ir_to_expr returns None
                     and the whole conversion fails gracefully. *)
                  match json_field_get "object" j,
                        json_field_get "field" j,
                        json_field_get "value" j with
                  | Some objv, Some fv, Some valv =>
                      match json_to_string objv,
                            json_to_string fv,
                            ir_to_expr default_expr_fuel valv with
                      | Some self_id, Some f, Some e =>
                          Some (SFieldAssign self_id f e)
                      | _, _, _ => None
                      end
                  | _, _, _ => None
                  end
                else if String.eqb t "For" then
                  (* Two cases handled:
                     (a) `for x in Var(arr)` → SFor x arr inv var body true (direct).
                     (b) `for i in range(N)` → desugar to:
                           SSeq (SAssign i 0)
                                (SWhile (CBoolLit true) (CInt 0)
                                        (ECmp OpLt (EVar i) N)
                                        (SSeq <body> (SAugAssign i OpAdd 1))) *)
                  match json_field_get "target" j,
                        json_field_get "iter" j,
                        json_field_get "body" j with
                  | Some tgtv, Some iterv, Some bodyv =>
                      match json_to_string tgtv,
                            json_field_get "type" iterv with
                      | Some x, Some itype =>
                          match json_to_string itype with
                          | Some "Var" =>
                              (* Case (a) *)
                              match json_field_get "name" iterv with
                              | Some namev =>
                                  match json_to_string namev,
                                        ir_to_stmt_n n bodyv with
                                  | Some arr, Some body =>
                                      let inv :=
                                        match json_field_get "invariants" j with
                                        | Some il =>
                                            match json_to_list il with
                                            | Some (first :: _) =>
                                                match ir_to_contract_expr default_contract_fuel first with
                                                | Some ce => ce
                                                | None    => CBoolLit true
                                                end
                                            | _ => CBoolLit true
                                            end
                                        | None => CBoolLit true
                                        end in
                                      let var :=
                                        match json_field_get "variants" j with
                                        | Some vl =>
                                            match json_to_list vl with
                                            | Some (first :: _) =>
                                                match ir_to_contract_expr default_contract_fuel first with
                                                | Some ce => ce
                                                | None    => CInt 0
                                                end
                                            | _ => CInt 0
                                            end
                                        | None => CInt 0
                                        end in
                                      Some (SFor x arr inv var body true)
                                  | _, _ => None
                                  end
                              | None => None
                              end
                          | Some "Call" =>
                              (* Case (b): `for i in range(...)` desugar.
                                 Handles 1-arg range(N) and 2-arg
                                 range(start, stop). *)
                              match json_field_get "func" iterv,
                                    json_field_get "args" iterv with
                              | Some fnv, Some argsv =>
                                  match json_to_string fnv, json_to_list argsv with
                                  | Some "range", Some (bound :: nil) =>
                                      (* range(N): i = 0; while i < N *)
                                      match ir_to_expr default_expr_fuel bound,
                                            ir_to_stmt_n n bodyv with
                                      | Some N, Some body =>
                                          let inv := CBoolLit true in
                                          let var := CInt 0 in
                                          Some (SSeq
                                                  (SAssign x (EInt 0))
                                                  (SWhile inv var
                                                    (ECmp OpLt (EVar x) N)
                                                    (SSeq body
                                                          (SAugAssign x OpAdd (EInt 1)))))
                                      | _, _ => None
                                      end
                                  | Some "range", Some (start :: stop :: nil) =>
                                      (* range(start, stop): i = start; while i < stop *)
                                      match ir_to_expr default_expr_fuel start,
                                            ir_to_expr default_expr_fuel stop,
                                            ir_to_stmt_n n bodyv with
                                      | Some s, Some e, Some body =>
                                          let inv := CBoolLit true in
                                          let var := CInt 0 in
                                          Some (SSeq
                                                  (SAssign x s)
                                                  (SWhile inv var
                                                    (ECmp OpLt (EVar x) e)
                                                    (SSeq body
                                                          (SAugAssign x OpAdd (EInt 1)))))
                                      | _, _, _ => None
                                      end
                                  | _, _ => None
                                  end
                              | _, _ => None
                              end
                          | _ => None
                          end
                      | _, _ => None
                      end
                  | _, _, _ => None
                  end
                else if String.eqb t "TupleUnpack" then
                  (* STupleUnpack xs e — "targets" is JsonList of JsonStrings.
                     Value side is ir_to_expr; may fail for compound calls. *)
                  match json_field_get "targets" j,
                        json_field_get "value" j with
                  | Some tgtsv, Some valv =>
                      match json_to_list tgtsv with
                      | Some tlist =>
                          match option_map_list json_to_string tlist,
                                ir_to_expr default_expr_fuel valv with
                          | Some xs, Some e => Some (STupleUnpack xs e)
                          | _, _ => None
                          end
                      | None => None
                      end
                  | _, _ => None
                  end
                else if String.eqb t "FieldAugAssign" then
                  (* SFieldAugAssign self_id f op e — self.f op= e. *)
                  match json_field_get "object" j,
                        json_field_get "field" j,
                        json_field_get "op" j,
                        json_field_get "value" j with
                  | Some objv, Some fv, Some opv, Some valv =>
                      match json_to_string objv,
                            json_to_string fv,
                            json_to_string opv with
                      | Some self_id, Some f, Some opstr =>
                          match aug_string_to_binop opstr,
                                ir_to_expr default_expr_fuel valv with
                          | Some op, Some e =>
                              Some (SFieldAugAssign self_id f op e)
                          | _, _ => None
                          end
                      | _, _, _ => None
                      end
                  | _, _, _, _ => None
                  end
                else None
            | None => None
            end
        | None => None
        end
    end
  end.

Definition default_stmt_fuel : nat := 1000%nat.

(* ===== ir_to_stmt: top-level converter ===== *)

Definition ir_to_stmt (j : json_value) : option stmt :=
  ir_to_stmt_n default_stmt_fuel j.

(* ===== Smoke test ===== *)

(* Build a sample IR for `x = 42` and verify ir_to_stmt produces
   `Some (SAssign "x" (EInt 42))`. *)
Definition sample_assign_ir : json_value :=
  JsonObject
    (("stmt", JsonString "Assign") ::
     ("target", JsonString "x") ::
     ("value",
      JsonObject (("type", JsonString "Number") ::
                  ("value", JsonInt 42) :: nil)) ::
     nil).

Example ir_to_stmt_assign_ok :
  ir_to_stmt sample_assign_ir = Some (SAssign "x" (EInt 42)).
Proof. reflexivity. Qed.

(* Build a sample IR for `arr[i] = x + 1` to exercise ArraySet + BinOp. *)
Definition sample_array_set_ir : json_value :=
  JsonObject
    (("stmt", JsonString "ArraySet") ::
     ("array",
      JsonObject (("type", JsonString "Var") ::
                  ("name", JsonString "arr") :: nil)) ::
     ("index",
      JsonObject (("type", JsonString "Var") ::
                  ("name", JsonString "i") :: nil)) ::
     ("value",
      JsonObject (("type", JsonString "BinOp") ::
                  ("op", JsonString "+") ::
                  ("left",
                   JsonObject (("type", JsonString "Var") ::
                               ("name", JsonString "x") :: nil)) ::
                  ("right",
                   JsonObject (("type", JsonString "Number") ::
                               ("value", JsonInt 1) :: nil)) :: nil)) ::
     nil).

Example ir_to_stmt_array_set_ok :
  ir_to_stmt sample_array_set_ir =
    Some (SArraySet "arr" (EVar "i") (EBinOp OpAdd (EVar "x") (EInt 1))).
Proof. reflexivity. Qed.

(* Build a sample IR for a body `[x = 1; pass]` to exercise sequencing. *)
Definition sample_seq_ir : json_value :=
  JsonList
    (JsonObject (("stmt", JsonString "Assign") ::
                 ("target", JsonString "x") ::
                 ("value",
                  JsonObject (("type", JsonString "Number") ::
                              ("value", JsonInt 1) :: nil)) :: nil) ::
     JsonObject (("stmt", JsonString "Pass") :: nil) ::
     nil).

Example ir_to_stmt_seq_ok :
  ir_to_stmt sample_seq_ir = Some (SSeq (SAssign "x" (EInt 1)) SSkip).
Proof. reflexivity. Qed.

(* ===== Compound-statement smoke tests (Q4 U.2 expansion, 2026-05-29) ===== *)

(* Sample IR for `break` *)
Example ir_to_stmt_break_ok :
  ir_to_stmt (JsonObject (("stmt", JsonString "Break") :: nil)) = Some SBreak.
Proof. reflexivity. Qed.

(* Sample IR for `continue` *)
Example ir_to_stmt_continue_ok :
  ir_to_stmt (JsonObject (("stmt", JsonString "Continue") :: nil)) = Some SContinue.
Proof. reflexivity. Qed.

(* Sample IR for `if x: pass else: pass` *)
Definition sample_if_ir : json_value :=
  JsonObject
    (("stmt", JsonString "If") ::
     ("test",
      JsonObject (("type", JsonString "Var") ::
                  ("name", JsonString "x") :: nil)) ::
     ("body",
      JsonList (JsonObject (("stmt", JsonString "Pass") :: nil) :: nil)) ::
     ("orelse",
      JsonList (JsonObject (("stmt", JsonString "Pass") :: nil) :: nil)) ::
     nil).

Example ir_to_stmt_if_ok :
  ir_to_stmt sample_if_ir = Some (SIf (EVar "x") SSkip SSkip).
Proof. reflexivity. Qed.

(* Sample IR for `while x < 10: x = x + 1` (with single inv/var) *)
Definition sample_while_ir : json_value :=
  JsonObject
    (("stmt", JsonString "While") ::
     ("test",
      JsonObject (("type", JsonString "BinOp") ::
                  ("op", JsonString "<") ::
                  ("left",
                   JsonObject (("type", JsonString "Var") ::
                               ("name", JsonString "x") :: nil)) ::
                  ("right",
                   JsonObject (("type", JsonString "Number") ::
                               ("value", JsonInt 10) :: nil)) :: nil)) ::
     ("invariants",
      JsonList (JsonObject (("type", JsonString "Number") ::
                            ("value", JsonInt 1) :: nil) :: nil)) ::
     ("variants",
      JsonList (JsonObject (("type", JsonString "Number") ::
                            ("value", JsonInt 0) :: nil) :: nil)) ::
     ("body",
      JsonList (JsonObject (("stmt", JsonString "Assign") ::
                            ("target", JsonString "x") ::
                            ("value",
                             JsonObject (("type", JsonString "BinOp") ::
                                         ("op", JsonString "+") ::
                                         ("left",
                                          JsonObject (("type", JsonString "Var") ::
                                                      ("name", JsonString "x") :: nil)) ::
                                         ("right",
                                          JsonObject (("type", JsonString "Number") ::
                                                      ("value", JsonInt 1) :: nil)) :: nil)) ::
                            nil) :: nil)) ::
     nil).

Example ir_to_stmt_while_ok :
  ir_to_stmt sample_while_ir =
    Some (SWhile (CInt 1) (CInt 0)
                 (ECmp OpLt (EVar "x") (EInt 10))
                 (SAssign "x" (EBinOp OpAdd (EVar "x") (EInt 1)))).
Proof. reflexivity. Qed.

(* Sample IR for `label foo` *)
Example ir_to_stmt_label_ok :
  ir_to_stmt (JsonObject (("stmt", JsonString "Label") ::
                          ("name", JsonString "foo") :: nil)) =
    Some (SLabel "foo").
Proof. reflexivity. Qed.

(* Sample IR for `raise MyExc` *)
Example ir_to_stmt_raise_ok :
  ir_to_stmt (JsonObject (("stmt", JsonString "Raise") ::
                          ("exc_type", JsonString "MyExc") :: nil)) =
    Some (SRaise "MyExc").
Proof. reflexivity. Qed.

(* Sample IR for `assert x` *)
Example ir_to_stmt_assert_ok :
  ir_to_stmt (JsonObject (("stmt", JsonString "Assert") ::
                          ("test",
                           JsonObject (("type", JsonString "Var") ::
                                       ("name", JsonString "x") :: nil)) ::
                          ("msg", JsonString "must hold") :: nil)) =
    Some (SAssert (CVar "x") "must hold").
Proof. reflexivity. Qed.

(* Sample IR for ghost declaration `ghost g : int = 0` *)
Example ir_to_stmt_ghost_decl_ok :
  ir_to_stmt (JsonObject (("stmt", JsonString "GhostAssign") ::
                          ("target", JsonString "g") ::
                          ("op", JsonString "=") ::
                          ("ghost_type", JsonString "int") ::
                          ("value",
                           JsonObject (("type", JsonString "Number") ::
                                       ("value", JsonInt 0) :: nil)) :: nil)) =
    Some (SGhostDecl "g" GTInt (CInt 0)).
Proof. reflexivity. Qed.

(* Sample IR for ghost augassign `ghost g += 1` *)
Example ir_to_stmt_ghost_aug_ok :
  ir_to_stmt (JsonObject (("stmt", JsonString "GhostAssign") ::
                          ("target", JsonString "g") ::
                          ("op", JsonString "+=") ::
                          ("ghost_type", JsonString "int") ::
                          ("value",
                           JsonObject (("type", JsonString "Number") ::
                                       ("value", JsonInt 1) :: nil)) :: nil)) =
    Some (SGhostAssign "g" GTInt AugAdd (CInt 1)).
Proof. reflexivity. Qed.

(* Sample IR for critical section `with lock my_mutex: pass` *)
Example ir_to_stmt_critical_ok :
  ir_to_stmt (JsonObject (("stmt", JsonString "CriticalSection") ::
                          ("mutex", JsonString "my_mutex") ::
                          ("body",
                           JsonList (JsonObject (("stmt", JsonString "Pass") :: nil) :: nil)) ::
                          nil)) =
    Some (SCritical "my_mutex" SSkip).
Proof. reflexivity. Qed.

(* Sample IR for try-except: `try: x = 1 except MyExc: pass` *)
Example ir_to_stmt_try_ok :
  ir_to_stmt (JsonObject
                (("stmt", JsonString "Try") ::
                 ("body",
                  JsonList (JsonObject (("stmt", JsonString "Assign") ::
                                        ("target", JsonString "x") ::
                                        ("value",
                                         JsonObject (("type", JsonString "Number") ::
                                                     ("value", JsonInt 1) :: nil)) :: nil) :: nil)) ::
                 ("handlers",
                  JsonList (JsonObject
                              (("exc_type", JsonString "MyExc") ::
                               ("body",
                                JsonList (JsonObject
                                            (("stmt", JsonString "Pass") :: nil) :: nil)) ::
                               nil) :: nil)) :: nil)) =
    Some (STryCatch (SAssign "x" (EInt 1)) "MyExc" SSkip).
Proof. reflexivity. Qed.

(* ===== Contract-expr expansion smoke tests (2026-05-29) ===== *)

(* String literal: "hello" *)
Example ir_to_contract_string_ok :
  ir_to_contract_expr default_contract_fuel
    (JsonObject (("type",  JsonString "String") ::
                 ("value", JsonString "hello") :: nil)) =
    Some (CStringLit "hello").
Proof. reflexivity. Qed.

(* Forall: forall i. i > 0 *)
Example ir_to_contract_forall_ok :
  ir_to_contract_expr default_contract_fuel
    (JsonObject (("type", JsonString "Forall") ::
                 ("var",  JsonString "i") ::
                 ("body",
                  JsonObject (("type", JsonString "BinOp") ::
                              ("op",   JsonString ">") ::
                              ("left",
                               JsonObject (("type", JsonString "Var") ::
                                           ("name", JsonString "i") :: nil)) ::
                              ("right",
                               JsonObject (("type", JsonString "Number") ::
                                           ("value", JsonInt 0) :: nil)) ::
                              nil)) :: nil)) =
    Some (CForall "i" (CGt (CVar "i") (CInt 0))).
Proof. reflexivity. Qed.

(* Exists: exists i. arr[i] == 0 *)
Example ir_to_contract_exists_ok :
  ir_to_contract_expr default_contract_fuel
    (JsonObject (("type", JsonString "Exists") ::
                 ("var",  JsonString "i") ::
                 ("body",
                  JsonObject (("type", JsonString "BinOp") ::
                              ("op",   JsonString "==") ::
                              ("left",
                               JsonObject (("type", JsonString "Subscript") ::
                                           ("value",
                                            JsonObject (("type", JsonString "Var") ::
                                                        ("name", JsonString "arr") :: nil)) ::
                                           ("index",
                                            JsonObject (("type", JsonString "Var") ::
                                                        ("name", JsonString "i") :: nil)) :: nil)) ::
                              ("right",
                               JsonObject (("type", JsonString "Number") ::
                                           ("value", JsonInt 0) :: nil)) :: nil)) :: nil)) =
    Some (CExists "i" (CEq (CSubscript "arr" (CVar "i")) (CInt 0))).
Proof. reflexivity. Qed.

(* At-label: \at(x, L1) *)
Example ir_to_contract_at_ok :
  ir_to_contract_expr default_contract_fuel
    (JsonObject (("type",  JsonString "At") ::
                 ("expr",
                  JsonObject (("type", JsonString "Var") ::
                              ("name", JsonString "x") :: nil)) ::
                 ("label", JsonString "L1") :: nil)) =
    Some (CAt (CVar "x") "L1").
Proof. reflexivity. Qed.
