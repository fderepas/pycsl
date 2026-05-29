(* Phase2_State.v — Values, state, and concrete evaluators *)

Require Import ZArith String List Bool.
Require Import Coq.Arith.PeanoNat.
Require Import Phase1_AST.
Open Scope Z_scope.

(* Runtime values *)
Inductive val : Type :=
  | VInt   (n : Z)
  | VArray (a : list Z).

(* Association-list state *)
Definition state := list (ident * val).

(* State lookup *)
Fixpoint lookup (st : state) (x : ident) : option val :=
  match st with
  | nil => None
  | (y, v) :: rest =>
    if String.eqb x y then Some v else lookup rest x
  end.

(* State update — cons-based shadowing *)
Definition update (st : state) (x : ident) (v : val) : state :=
  (x, v) :: st.

(* Array element update *)
Definition array_update (st : state) (arr : ident) (i : Z) (v : Z) : state :=
  match lookup st arr with
  | Some (VArray a) =>
    let idx := Z.to_nat i in
    if (0 <=? i) && (i <? Z.of_nat (List.length a)) then
      let a' := List.app (List.firstn idx a) (List.app (v :: nil) (List.skipn (S idx) a)) in
      update st arr (VArray a')
    else st
  | _ => st
  end.

(* ===== Phase 1 helper functions ===== *)

(* Sum of array elements: a[idx] + a[idx+1] + ... (count elements) *)
Fixpoint sum_list_from (a : list Z) (idx count : nat) : Z :=
  match count with
  | O => 0
  | S n => List.nth idx a 0 + sum_list_from a (S idx) n
  end.

Definition sum_list_range (a : list Z) (lo hi : nat) : Z :=
  if Nat.ltb lo hi then sum_list_from a lo (hi - lo) else 0.

(* Non-decreasing (sorted) predicate for count consecutive elements from lo *)
Fixpoint sorted_list_from (a : list Z) (lo count : nat) : Prop :=
  match count with
  | O => True
  | S n =>
    match n with
    | O => True
    | _ => List.nth lo a 0 <= List.nth (S lo) a 0 /\ sorted_list_from a (S lo) n
    end
  end.

Definition sorted_list_range (a : list Z) (lo hi : nat) : Prop :=
  if Nat.ltb lo hi then sorted_list_from a lo (hi - lo) else True.

(* ===== Phase 3a: ghost state types ===== *)

(* Ghost values — Phase 3b: all supported ghost types *)
Inductive ghost_val : Type :=
  | GVInt    (n : Z)
  | GVString (s : string)
  | GVArray  (a : list Z)
  | GVList   (l : list Z)
  | GVDict   (d : list (Z * Z))   (* association-list model for ghost_dict *)
  | GVSet    (s : list Z)          (* sorted-list model for ghost_set *)
  | GVTuple2 (a b : Z)
  | GVTuple3 (a b c : Z)
  | GVTuple4 (a b c d : Z).

(* Ghost state: maps ghost variable names to ghost values *)
Definition ghost_state := list (ident * ghost_val).

(* Label snapshots: ghost_state recorded at each SLabel point *)
Definition label_env := list (ident * ghost_state).

(* Ghost state lookup *)
Fixpoint ghost_lookup (gst : ghost_state) (x : ident) : option ghost_val :=
  match gst with
  | nil => None
  | (y, v) :: rest => if String.eqb x y then Some v else ghost_lookup rest x
  end.

(* Ghost state update (cons-based shadowing) *)
Definition ghost_update (gst : ghost_state) (x : ident) (v : ghost_val) : ghost_state :=
  (x, v) :: gst.

(* Label env lookup *)
Fixpoint label_lookup (lenv : label_env) (L : ident) : option ghost_state :=
  match lenv with
  | nil => None
  | (M, gst) :: rest => if String.eqb L M then Some gst else label_lookup rest L
  end.

(* Full execution state — used from Phase 3a onwards *)
Record exec_state : Type := mkExecState {
  reg_state   : state;
  ghost_st    : ghost_state;
  label_snaps : label_env
}.

(* Convenience constructors *)
Definition mk_exec_state (st : state) : exec_state :=
  {| reg_state := st; ghost_st := nil; label_snaps := nil |}.

Definition set_reg (es : exec_state) (st : state) : exec_state :=
  {| reg_state := st; ghost_st := es.(ghost_st); label_snaps := es.(label_snaps) |}.

Definition set_ghost (es : exec_state) (gst : ghost_state) : exec_state :=
  {| reg_state := es.(reg_state); ghost_st := gst; label_snaps := es.(label_snaps) |}.

Definition set_labels (es : exec_state) (lenv : label_env) : exec_state :=
  {| reg_state := es.(reg_state); ghost_st := es.(ghost_st); label_snaps := lenv |}.

(* ===== Arithmetic on Z ===== *)
Definition eval_binop_z (op : binop) (n1 n2 : Z) : Z :=
  match op with
  | OpAdd => n1 + n2
  | OpSub => n1 - n2
  | OpMul => n1 * n2
  | OpDiv => if Z.eqb n2 0 then 0 else Z.div n1 n2
  | OpMod => if Z.eqb n2 0 then 0 else Z.modulo n1 n2
  end.

(* Comparison evaluator: returns 0 (false) or 1 (true) — Python semantics. *)
Definition eval_cmpop_z (op : cmpop) (n1 n2 : Z) : Z :=
  if (match op with
      | OpEq => Z.eqb n1 n2
      | OpNe => negb (Z.eqb n1 n2)
      | OpLt => Z.ltb n1 n2
      | OpLe => Z.leb n1 n2
      | OpGt => Z.gtb n1 n2
      | OpGe => Z.geb n1 n2
      end)
  then 1 else 0.

(* Runtime expression evaluator — total function *)
Fixpoint eval_expr (st : state) (e : expr) : val :=
  match e with
  | EInt n => VInt n
  | EVar x => match lookup st x with Some v => v | None => VInt 0 end
  | ESubscript arr i =>
    match lookup st arr, eval_expr st i with
    | Some (VArray a), VInt n =>
      if (0 <=? n) && (n <? Z.of_nat (List.length a))
      then VInt (List.nth (Z.to_nat n) a 0)
      else VInt 0
    | _, _ => VInt 0
    end
  | ELen arr =>
    match lookup st arr with
    | Some (VArray a) => VInt (Z.of_nat (List.length a))
    | _ => VInt 0
    end
  | EBinOp op e1 e2 =>
    match eval_expr st e1, eval_expr st e2 with
    | VInt n1, VInt n2 => VInt (eval_binop_z op n1 n2)
    | _, _ => VInt 0
    end
  | ENeg e =>
    match eval_expr st e with
    | VInt n => VInt (- n)
    | v => v
    end
  | ECmp op e1 e2 =>
    match eval_expr st e1, eval_expr st e2 with
    | VInt n1, VInt n2 => VInt (eval_cmpop_z op n1 n2)
    | _, _ => VInt 0
    end
  | EFieldGet obj f =>
    (* Q4 U.4 (2026-05-29): name-flatten obj.f into a synthetic
       variable "obj.f" and look up in the runtime state. Module 6
       emits flat names matching this convention. *)
    match lookup st (obj ++ "." ++ f) with
    | Some v => v
    | None   => VInt 0
    end
  | ECall _ _ =>
    (* Q4 U.4 (2026-05-29): generic call defaults to VInt 0.
       No function semantics at this layer; downstream code with
       a function-interpretation table can intercept. *)
    VInt 0
  end.

(* Boolean test for conditional/loop guards *)
Definition eval_bool (st : state) (e : expr) : bool :=
  match eval_expr st e with
  | VInt 0 => false
  | _ => true
  end.

(* Integer extraction from contract expressions *)
Fixpoint eval_z (st pre_st : state) (result : option val)
                (e : contract_expr) : Z :=
  match e with
  | CInt n => n
  | CVar x => match lookup st x with Some (VInt n) => n | _ => 0 end
  | CResult => match result with Some (VInt n) => n | _ => 0 end
  | CLength arr =>
    match lookup st arr with
    | Some (VArray a) => Z.of_nat (List.length a)
    | _ => 0
    end
  | CSubscript arr i =>
    let n := eval_z st pre_st result i in
    match lookup st arr with
    | Some (VArray a) =>
      if (0 <=? n) && (n <? Z.of_nat (List.length a))
      then List.nth (Z.to_nat n) a 0
      else 0
    | _ => 0
    end
  | COld e => eval_z pre_st pre_st result e
  | CBinOp op e1 e2 =>
    eval_binop_z op (eval_z st pre_st result e1) (eval_z st pre_st result e2)
  | CNeg e => - (eval_z st pre_st result e)
  (* Phase 1 additions *)
  | CChainedSubscript arr i j =>
    (* Typed model needed for full 2D semantics; placeholder in Hoare model *)
    let n := eval_z st pre_st result i in
    match lookup st arr with
    | Some (VArray a) =>
      if (0 <=? n) && (n <? Z.of_nat (List.length a))
      then List.nth (Z.to_nat n) a 0
      else 0
    | _ => 0
    end
  | CBoolLit b => if b then 1 else 0
  | CNoneLit => 0
  | CStringLit _ => 0
  | CIsSorted _ _ _ => 0   (* boolean predicate — use eval_contract *)
  | CSum arr lo hi =>
    let lo_z := eval_z st pre_st result lo in
    let hi_z := eval_z st pre_st result hi in
    match lookup st arr with
    | Some (VArray a) =>
      sum_list_range a (Z.to_nat lo_z) (Z.to_nat hi_z)
    | _ => 0
    end
  | CSlice _ _ _ => 0      (* array-valued expression — placeholder *)
  | CIn _ _ | CNotIn _ _ => 0  (* boolean — use eval_contract *)
  (* Phase 2 additions *)
  | CResultSubscript i =>
    let n := eval_z st pre_st result i in
    match result with
    | Some (VArray a) =>
      if (0 <=? n) && (n <? Z.of_nat (List.length a))
      then List.nth (Z.to_nat n) a 0
      else 0
    | _ => 0
    end
  | CCall _ _ => 0    (* function calls: opaque in Hoare model *)
  (* Phase 3 — \at: evaluated against label snapshot *)
  | CAt e L =>
    match label_lookup nil L with   (* label_snaps not in scope here; see eval_contract_es *)
    | Some _ => 0
    | None => 0
    end
  (* All Phase 3b ghost atoms, Phase 4+: return 0 in base evaluator *)
  | _ => 0
  end.

(* Phase 3e helpers: list length and string length computable without full evaluator.
   These live in Phase2_State.v (not Phase3_SOS.v) to avoid import circularity. *)

Fixpoint ghost_list_length_es (es : exec_state) (e : ghost_expr) : Z :=
  match e with
  | CGNil => 0
  | CGCons _ t => 1 + ghost_list_length_es es t
  | CGAppend l1 l2 =>
    ghost_list_length_es es l1 + ghost_list_length_es es l2
  | CGTl l => Z.max 0 (ghost_list_length_es es l - 1)
  | CVar x =>
    match ghost_lookup es.(ghost_st) x with
    | Some (GVList lst) => Z.of_nat (List.length lst)
    | Some (GVArray a)  => Z.of_nat (List.length a)
    | Some (GVSet s)    => Z.of_nat (List.length s)
    | _ => 0
    end
  | _ => 0
  end.

Fixpoint ghost_string_length_es (es : exec_state) (e : ghost_expr) : Z :=
  match e with
  | CVar x =>
    match ghost_lookup es.(ghost_st) x with
    | Some (GVString str) => Z.of_nat (String.length str)
    | _ => 0
    end
  | CGStrConcat s1 s2 =>
    ghost_string_length_es es s1 + ghost_string_length_es es s2
  | _ => 0
  end.

Fixpoint ghost_set_mem_es (es : exec_state) (elem : Z) (e : ghost_expr) : bool :=
  match e with
  | CGSetEmpty => false
  | CGSetAdd h s =>
    let hv := eval_z es.(reg_state) es.(reg_state) None h in
    if Z.eqb hv elem then true else ghost_set_mem_es es elem s
  | CVar x =>
    match ghost_lookup es.(ghost_st) x with
    | Some (GVSet lst) => List.existsb (Z.eqb elem) lst
    | _ => false
    end
  | _ => false
  end.

Fixpoint ghost_set_card_es (es : exec_state) (e : ghost_expr) : Z :=
  match e with
  | CGSetEmpty => 0
  | CGSetAdd h s =>
    let hv := eval_z es.(reg_state) es.(reg_state) None h in
    if ghost_set_mem_es es hv s
    then ghost_set_card_es es s
    else 1 + ghost_set_card_es es s
  | CVar x =>
    match ghost_lookup es.(ghost_st) x with
    | Some (GVSet lst) => Z.of_nat (List.length lst)
    | _ => 0
    end
  | _ => 0
  end.

(* Phase 3.3 / 3d mutual fixpoint: ghost_list_nth_es and eval_z_es are mutually
   recursive so that CGCons element heads are evaluated with full exec_state
   awareness — ghost int variables resolved from ghost_st, not just reg_state. *)
Fixpoint ghost_list_nth_es (es pre_es : exec_state) (result : option val)
                           (e : ghost_expr) (idx : Z) : Z :=
  match e with
  | CGNil => 0
  | CGCons h t =>
    if Z.eqb idx 0
    then eval_z_es es pre_es result h
    else ghost_list_nth_es es pre_es result t (idx - 1)
  | CGAppend l1 l2 =>
    let len1 := ghost_list_length_es es l1 in
    if (0 <=? idx) && (idx <? len1)
    then ghost_list_nth_es es pre_es result l1 idx
    else ghost_list_nth_es es pre_es result l2 (idx - len1)
  | CGTl l => ghost_list_nth_es es pre_es result l (idx + 1)
  | CVar x =>
    match ghost_lookup es.(ghost_st) x with
    | Some (GVList lst) =>
      if (0 <=? idx) && (idx <? Z.of_nat (List.length lst))
      then List.nth (Z.to_nat idx) lst 0 else 0
    | Some (GVArray a) =>
      if (0 <=? idx) && (idx <? Z.of_nat (List.length a))
      then List.nth (Z.to_nat idx) a 0 else 0
    | _ => 0
    end
  | _ => 0
  end
(* Phase 3d: exec_state-aware integer evaluator.
   Handles CVar with ghost_state fallback and CAt via label snapshot lookup.
   This closes the gap where \at(ghost_var + 1, L) returned 0 in eval_z. *)
with eval_z_es (es pre_es : exec_state) (result : option val)
               (e : contract_expr) : Z :=
  match e with
  | CInt n => n
  | CVar x =>
    match lookup es.(reg_state) x with
    | Some (VInt n) => n
    | _ =>
      match ghost_lookup es.(ghost_st) x with
      | Some (GVInt n) => n
      | _ => 0
      end
    end
  | CResult => match result with Some (VInt n) => n | _ => 0 end
  | CLength arr =>
    match lookup es.(reg_state) arr with
    | Some (VArray a) => Z.of_nat (List.length a)
    | _ => 0
    end
  | CSubscript arr i =>
    let n := eval_z_es es pre_es result i in
    match lookup es.(reg_state) arr with
    | Some (VArray a) =>
      if (0 <=? n) && (n <? Z.of_nat (List.length a))
      then List.nth (Z.to_nat n) a 0
      else 0
    | _ => 0
    end
  | COld e' => eval_z_es pre_es pre_es result e'
  | CBinOp op e1 e2 =>
    eval_binop_z op (eval_z_es es pre_es result e1) (eval_z_es es pre_es result e2)
  | CNeg e' => - (eval_z_es es pre_es result e')
  | CAt e' L =>
    match label_lookup es.(label_snaps) L with
    | Some gst => eval_z_es (set_ghost es gst) pre_es result e'
    | None => 0
    end
  | CSum arr lo hi =>
    let lo_z := eval_z_es es pre_es result lo in
    let hi_z := eval_z_es es pre_es result hi in
    match lookup es.(reg_state) arr with
    | Some (VArray a) => sum_list_range a (Z.to_nat lo_z) (Z.to_nat hi_z)
    | _ => 0
    end
  (* Phase 3e: Tuple projections — CGMkTuple* + CVar lookup *)
  | CGFst t =>
    match t with
    | CGMkTuple2 e1 _     => eval_z_es es pre_es result e1
    | CGMkTuple3 e1 _ _   => eval_z_es es pre_es result e1
    | CGMkTuple4 e1 _ _ _ => eval_z_es es pre_es result e1
    | CVar x =>
      match ghost_lookup es.(ghost_st) x with
      | Some (GVTuple2 a _) => a | Some (GVTuple3 a _ _) => a
      | Some (GVTuple4 a _ _ _) => a | _ => 0 end
    | _ => 0
    end
  | CGSnd t =>
    match t with
    | CGMkTuple2 _ e2     => eval_z_es es pre_es result e2
    | CGMkTuple3 _ e2 _   => eval_z_es es pre_es result e2
    | CGMkTuple4 _ e2 _ _ => eval_z_es es pre_es result e2
    | CVar x =>
      match ghost_lookup es.(ghost_st) x with
      | Some (GVTuple2 _ b) => b | Some (GVTuple3 _ b _) => b
      | Some (GVTuple4 _ b _ _) => b | _ => 0 end
    | _ => 0
    end
  | CGTrd t =>
    match t with
    | CGMkTuple3 _ _ e3   => eval_z_es es pre_es result e3
    | CGMkTuple4 _ _ e3 _ => eval_z_es es pre_es result e3
    | CVar x =>
      match ghost_lookup es.(ghost_st) x with
      | Some (GVTuple3 _ _ c) => c | Some (GVTuple4 _ _ c _) => c | _ => 0 end
    | _ => 0
    end
  | CGFth t =>
    match t with
    | CGMkTuple4 _ _ _ e4 => eval_z_es es pre_es result e4
    | CVar x =>
      match ghost_lookup es.(ghost_st) x with
      | Some (GVTuple4 _ _ _ d) => d | _ => 0 end
    | _ => 0
    end
  (* Phase 3e: List/set/string sizes — full expression support *)
  | CGListLen l => ghost_list_length_es es l
  | CGSetCard s => ghost_set_card_es es s
  | CGStrLen s => ghost_string_length_es es s
  (* Phase 3e: Ghost list element access — all list expression forms *)
  | CGNth l i =>
    let idx := eval_z_es es pre_es result i in
    ghost_list_nth_es es pre_es result l idx
  (* All other ghost atoms and unhandled cases: delegate to base evaluator *)
  | _ => eval_z es.(reg_state) pre_es.(reg_state) result e
  end.

(* Array membership helper for CIn / CNotIn — defined before eval_contract *)
Definition eval_array_in (st pre_st : state) (result : option val)
                         (elem container : contract_expr) : Prop :=
  let v := eval_z st pre_st result elem in
  match container with
  | CVar arr =>
    match lookup st arr with
    | Some (VArray a) => List.In v a
    | _ => False
    end
  | _ => False
  end.

(* Logical evaluation of contract expressions *)
Fixpoint eval_contract (st pre_st : state) (result : option val)
                       (e : contract_expr) : Prop :=
  match e with
  | CInt n => n <> 0
  | CVar x =>
    match lookup st x with Some (VInt 0) => False | _ => True end
  | CResult =>
    match result with Some (VInt 0) => False | _ => True end
  | CLength _ | CSubscript _ _ | COld _ | CBinOp _ _ _ | CNeg _ =>
    eval_z st pre_st result e <> 0
  | CEq  e1 e2 => eval_z st pre_st result e1 =  eval_z st pre_st result e2
  | CNe  e1 e2 => eval_z st pre_st result e1 <> eval_z st pre_st result e2
  | CLt  e1 e2 => eval_z st pre_st result e1 <  eval_z st pre_st result e2
  | CLe  e1 e2 => eval_z st pre_st result e1 <= eval_z st pre_st result e2
  | CGt  e1 e2 => eval_z st pre_st result e1 >  eval_z st pre_st result e2
  | CGe  e1 e2 => eval_z st pre_st result e1 >= eval_z st pre_st result e2
  | CAnd e1 e2 =>
    eval_contract st pre_st result e1 /\ eval_contract st pre_st result e2
  | COr  e1 e2 =>
    eval_contract st pre_st result e1 \/ eval_contract st pre_st result e2
  | CNot e => ~ eval_contract st pre_st result e
  | CImplies e1 e2 =>
    eval_contract st pre_st result e1 -> eval_contract st pre_st result e2
  | CIff e1 e2 =>
    eval_contract st pre_st result e1 <-> eval_contract st pre_st result e2
  | CForall x body =>
    forall n : Z,
      eval_contract (update st x (VInt n)) pre_st result body
  | CExists x body =>
    exists n : Z,
      eval_contract (update st x (VInt n)) pre_st result body
  (* Phase 1 additions *)
  | CChainedSubscript arr i j =>
    eval_z st pre_st result (CChainedSubscript arr i j) <> 0
  | CBoolLit b => b = true
  | CNoneLit => False
  | CStringLit s => s <> ""
  | CIsSorted arr lo hi =>
    let lo_z := eval_z st pre_st result lo in
    let hi_z := eval_z st pre_st result hi in
    match lookup st arr with
    | Some (VArray a) => sorted_list_range a (Z.to_nat lo_z) (Z.to_nat hi_z)
    | _ => True
    end
  | CSum arr lo hi =>
    eval_z st pre_st result (CSum arr lo hi) <> 0
  | CSlice _ _ _ => True   (* placeholder; slice equality handled by typed model *)
  | CIn elem container =>
    eval_array_in st pre_st result elem container
  | CNotIn elem container =>
    ~ eval_array_in st pre_st result elem container
  (* Phase 2 additions *)
  | CResultSubscript i =>
    eval_z st pre_st result (CResultSubscript i) <> 0
  | CCall _ _ => True     (* opaque in Hoare model; axiomatized by \trusted *)
  (* Phase 3 — \at: base model returns True (no label tracking without exec_state) *)
  | CAt _ _ => True
  (* Phase 3b ghost atoms — all opaque in base evaluator *)
  | CGMapEmpty | CGNil | CGSetEmpty => True
  | CGMapGet _ _ | CGMapSet _ _ _ | CGMapRemove _ _ => True
  | CGHasKey _ _ | CGMapEq _ _ => True
  | CGCons _ _ | CGHd _ | CGTl _ | CGListLen _ => True
  | CGNth _ _ | CGListMem _ _ | CGAppend _ _ => True
  | CGSetAdd _ _ | CGSetRemove _ _ | CGSetMem _ _ => True
  | CGSetCard _ | CGSetUnion _ _ | CGSetInter _ _ => True
  | CGSetDiff _ _ | CGSetSubset _ _ | CGSetEq _ _ => True
  | CGMkTuple2 _ _ | CGMkTuple3 _ _ _ | CGMkTuple4 _ _ _ _ => True
  | CGFst _ | CGSnd _ | CGTrd _ | CGFth _ => True
  | CGStrConcat _ _ | CGStrLen _ | CGStrNth _ _ => True
  | CGMake _ _ | CGCopy _ | CGCopyRange _ _ _ => True
  end.

(* Variant evaluation — produces Z for well-founded induction *)
Definition eval_variant (st pre_st : state) (e : contract_expr) : Z :=
  eval_z st pre_st None e.

(* ===== Phase 3c: exec_state-aware contract evaluator (CAt support) ===== *)

(* eval_contract_es: evaluates contract_expr with full exec_state access.
   Handles CAt by looking up the label snapshot in es.(label_snaps).
   All non-logical, non-CAt cases delegate to eval_contract for simplicity.
   Ghost variables referenced directly (not via \at) fall through to reg_state
   lookup — full ghost-var resolution in arithmetic requires eval_z_es (Phase 3d). *)
Fixpoint eval_contract_es (es pre_es : exec_state) (result : option val)
                           (e : contract_expr) : Prop :=
  match e with
  (* CAt: evaluate expr at the ghost_state snapshot recorded at label L *)
  | CAt expr L =>
    match label_lookup es.(label_snaps) L with
    | Some gst => eval_contract_es (set_ghost es gst) pre_es result expr
    | None => True
    end
  (* Logical connectives: must recurse through eval_contract_es *)
  | CAnd e1 e2 =>
    eval_contract_es es pre_es result e1 /\ eval_contract_es es pre_es result e2
  | COr e1 e2 =>
    eval_contract_es es pre_es result e1 \/ eval_contract_es es pre_es result e2
  | CNot e' => ~ eval_contract_es es pre_es result e'
  | CImplies e1 e2 =>
    eval_contract_es es pre_es result e1 -> eval_contract_es es pre_es result e2
  | CIff e1 e2 =>
    eval_contract_es es pre_es result e1 <-> eval_contract_es es pre_es result e2
  | CForall x body =>
    forall n : Z,
      eval_contract_es (set_reg es (update es.(reg_state) x (VInt n))) pre_es result body
  | CExists x body =>
    exists n : Z,
      eval_contract_es (set_reg es (update es.(reg_state) x (VInt n))) pre_es result body
  (* CVar: check reg_state first, then ghost_state *)
  | CVar x =>
    match lookup es.(reg_state) x with
    | Some (VInt 0) => False
    | Some _ => True
    | None =>
      match ghost_lookup es.(ghost_st) x with
      | Some (GVInt 0) => False
      | Some _ => True
      | None => True
      end
    end
  (* Phase 3d: arithmetic truth cases use eval_z_es for ghost-state awareness *)
  | CInt n => n <> 0
  | CResult =>
    match result with Some (VInt 0) => False | _ => True end
  | CLength _ | CSubscript _ _ | COld _ | CBinOp _ _ _ | CNeg _ =>
    eval_z_es es pre_es result e <> 0
  (* Phase 3d: comparison operators use eval_z_es so ghost vars resolve *)
  | CEq e1 e2 => eval_z_es es pre_es result e1 =  eval_z_es es pre_es result e2
  | CNe e1 e2 => eval_z_es es pre_es result e1 <> eval_z_es es pre_es result e2
  | CLt e1 e2 => eval_z_es es pre_es result e1 <  eval_z_es es pre_es result e2
  | CLe e1 e2 => eval_z_es es pre_es result e1 <= eval_z_es es pre_es result e2
  | CGt e1 e2 => eval_z_es es pre_es result e1 >  eval_z_es es pre_es result e2
  | CGe e1 e2 => eval_z_es es pre_es result e1 >= eval_z_es es pre_es result e2
  (* All remaining cases: delegate to base evaluator *)
  | _ => eval_contract es.(reg_state) pre_es.(reg_state) result e
  end.
