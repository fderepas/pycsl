
val negb : bool -> bool

val fst : ('a1 * 'a2) -> 'a1

val snd : ('a1 * 'a2) -> 'a2



val add : int -> int -> int

module Nat :
 sig
  val sub : int -> int -> int

  val ltb : int -> int -> bool

  val divmod : int -> int -> int -> int -> int * int

  val div : int -> int -> int

  val modulo : int -> int -> int
 end

module Pos :
 sig
  val iter_op : ('a1 -> 'a1 -> 'a1) -> int -> 'a1 -> 'a1

  val to_nat : int -> int
 end

val existsb : ('a1 -> bool) -> 'a1 list -> bool

val eqb : char list -> char list -> bool

val append : char list -> char list -> char list

type ident = char list

type binop =
| OpAdd
| OpSub
| OpMul
| OpDiv
| OpMod

type cmpop =
| OpEq
| OpNe
| OpLt
| OpLe
| OpGt
| OpGe

type expr =
| EInt of int
| EVar of ident
| ESubscript of ident * expr
| ELen of ident
| EBinOp of binop * expr * expr
| ENeg of expr
| ECmp of cmpop * expr * expr
| EFieldGet of ident * ident
| ECall of ident * expr list

type contract_expr =
| CInt of int
| CVar of ident
| CResult
| CLength of ident
| CSubscript of ident * contract_expr
| COld of contract_expr
| CBinOp of binop * contract_expr * contract_expr
| CNeg of contract_expr
| CEq of contract_expr * contract_expr
| CNe of contract_expr * contract_expr
| CLt of contract_expr * contract_expr
| CLe of contract_expr * contract_expr
| CGt of contract_expr * contract_expr
| CGe of contract_expr * contract_expr
| CAnd of contract_expr * contract_expr
| COr of contract_expr * contract_expr
| CNot of contract_expr
| CImplies of contract_expr * contract_expr
| CIff of contract_expr * contract_expr
| CForall of ident * contract_expr
| CExists of ident * contract_expr
| CChainedSubscript of ident * contract_expr * contract_expr
| CBoolLit of bool
| CNoneLit
| CStringLit of char list
| CIsSorted of ident * contract_expr * contract_expr
| CSum of ident * contract_expr * contract_expr
| CSlice of ident * contract_expr * contract_expr
| CIn of contract_expr * contract_expr
| CNotIn of contract_expr * contract_expr
| CResultSubscript of contract_expr
| CCall of ident * contract_expr list
| CAt of contract_expr * ident
| CGMapEmpty
| CGMapGet of contract_expr * contract_expr
| CGMapSet of contract_expr * contract_expr * contract_expr
| CGMapRemove of contract_expr * contract_expr
| CGHasKey of contract_expr * contract_expr
| CGMapEq of contract_expr * contract_expr
| CGNil
| CGCons of contract_expr * contract_expr
| CGHd of contract_expr
| CGTl of contract_expr
| CGListLen of contract_expr
| CGNth of contract_expr * contract_expr
| CGListMem of contract_expr * contract_expr
| CGAppend of contract_expr * contract_expr
| CGSetEmpty
| CGSetAdd of contract_expr * contract_expr
| CGSetRemove of contract_expr * contract_expr
| CGSetMem of contract_expr * contract_expr
| CGSetCard of contract_expr
| CGSetUnion of contract_expr * contract_expr
| CGSetInter of contract_expr * contract_expr
| CGSetDiff of contract_expr * contract_expr
| CGSetSubset of contract_expr * contract_expr
| CGSetEq of contract_expr * contract_expr
| CGMkTuple2 of contract_expr * contract_expr
| CGMkTuple3 of contract_expr * contract_expr * contract_expr
| CGMkTuple4 of contract_expr * contract_expr * contract_expr * contract_expr
| CGFst of contract_expr
| CGSnd of contract_expr
| CGTrd of contract_expr
| CGFth of contract_expr
| CGStrConcat of contract_expr * contract_expr
| CGStrLen of contract_expr
| CGStrNth of contract_expr * contract_expr
| CGMake of contract_expr * contract_expr
| CGCopy of ident
| CGCopyRange of ident * contract_expr * contract_expr
| CValid of contract_expr * contract_expr
| CSeparated of contract_expr * contract_expr
| CLength2d of ident
| CValid2d of contract_expr * contract_expr * contract_expr
| CClassInvariant of ident * contract_expr

type aug_op =
| AugAdd
| AugSub
| AugMul

type ghost_type =
| GTInt
| GTString
| GTArray
| GTDict
| GTList
| GTSet
| GTTuple2
| GTTuple3
| GTTuple4

type ghost_expr = contract_expr

type stmt =
| SSkip
| SAssign of ident * expr
| SAugAssign of ident * binop * expr
| SArraySet of ident * expr * expr
| SSeq of stmt * stmt
| SIf of expr * stmt * stmt
| SWhile of contract_expr * contract_expr * expr * stmt
| SFor of ident * ident * contract_expr * contract_expr * stmt * bool
| SReturn of expr
| SContinue
| SBreak
| SAssert of contract_expr * char list
| STupleUnpack of ident list * expr
| SGhostDecl of ident * ghost_type * ghost_expr
| SGhostAssign of ident * ghost_type * aug_op * ghost_expr
| SLabel of ident
| SRaise of ident
| STryCatch of stmt * ident * stmt
| SFieldAssign of ident * ident * expr
| SFieldAugAssign of ident * ident * binop * expr
| SCritical of ident * stmt
| SThreadEntry of stmt
| SAcquires of ident
| SReleases of ident

type whyml_exc =
| ExcReturn
| ExcBreak
| ExcContinue
| ExcNamed of ident

type whyml_stmt =
| WSkip
| WAssign of ident * expr
| WAugAssign of ident * binop * expr
| WArraySet of ident * expr * expr
| WSeq of whyml_stmt * whyml_stmt
| WIf of expr * whyml_stmt * whyml_stmt
| WWhile of contract_expr list * contract_expr list * expr * whyml_stmt
| WRaise of whyml_exc
| WTryCatch of whyml_stmt * ident * whyml_stmt
| WGhostDecl of ident * ghost_type * ghost_expr
| WGhostAssign of ident * ghost_type * aug_op * ghost_expr
| WLabel of ident
| WAssert of contract_expr * char list
| WAssume of contract_expr

val c_conj : contract_expr list -> contract_expr

val c_first : contract_expr list -> contract_expr

val for_idx : ident

val gen_lift_continue : whyml_stmt -> whyml_stmt -> whyml_stmt

val gen : stmt -> whyml_stmt

val acceptable_skip_emissions : char list list

val digit_char : int -> char

val nat_to_string_aux : int -> int -> char list

val nat_to_string : int -> char list

val z_to_string : int -> char list

val pretty_binop : binop -> char list

val pretty_cmpop : cmpop -> char list

val pretty_expr : expr -> char list

type assign_state = { as_shared_vars : ident list;
                      as_declared_refs : ident list;
                      as_bounded_int : char list option }

val ident_in : ident -> ident list -> bool

val emit_assign : assign_state -> ident -> expr -> char list

val acceptable_assign_emissions :
  assign_state -> ident -> expr -> char list list

val op_translate_aug : binop -> char list

val emit_aug_assign : ident -> binop -> expr -> char list

val acceptable_aug_assign_emissions : ident -> binop -> expr -> char list list

val emit_array_set : ident -> expr -> expr -> char list

val acceptable_array_set_emissions : ident -> expr -> expr -> char list list

val seq_sep : char list

val exc_to_string : whyml_exc -> char list

val emit_raise : whyml_exc -> char list

val acceptable_raise_emissions : whyml_exc -> char list list

val emit_label : ident -> char list

val acceptable_label_emissions : ident -> char list list

val emit_assert : contract_expr -> char list -> char list

val acceptable_assert_emissions : contract_expr -> char list -> char list list

val newline : char list

val pretty_contract_expr : contract_expr -> char list

val emit_if :
  assign_state -> expr -> whyml_stmt -> whyml_stmt -> (assign_state ->
  whyml_stmt -> char list) -> char list

val acceptable_if_emissions :
  assign_state -> expr -> whyml_stmt -> whyml_stmt -> (assign_state ->
  whyml_stmt -> char list) -> char list list

val emit_while :
  assign_state -> contract_expr list -> contract_expr list -> expr ->
  whyml_stmt -> (assign_state -> whyml_stmt -> char list) -> char list

val acceptable_while_emissions :
  assign_state -> contract_expr list -> contract_expr list -> expr ->
  whyml_stmt -> (assign_state -> whyml_stmt -> char list) -> char list list

val emit_try_catch :
  assign_state -> whyml_stmt -> ident -> whyml_stmt -> (assign_state ->
  whyml_stmt -> char list) -> char list

val acceptable_try_catch_emissions :
  assign_state -> whyml_stmt -> ident -> whyml_stmt -> (assign_state ->
  whyml_stmt -> char list) -> char list list

val emit_ghost_decl : ident -> ghost_type -> ghost_expr -> char list

val acceptable_ghost_decl_emissions :
  ident -> ghost_type -> ghost_expr -> char list list

val aug_op_str : aug_op -> char list

val emit_ghost_assign :
  ident -> ghost_type -> aug_op -> ghost_expr -> char list

val acceptable_ghost_assign_emissions :
  ident -> ghost_type -> aug_op -> ghost_expr -> char list list

val emit_stmt_full_complete : assign_state -> whyml_stmt -> char list

val acceptable_emit : assign_state -> stmt -> char list list

type aware_state = { aw_shared_vars : ident list;
                     aw_declared_refs : ident list;
                     aw_local_refs : ident list;
                     aw_array_locals : ident list;
                     aw_bounded_int : char list option }

val aware_in : ident -> ident list -> bool

val pretty_expr_state : aware_state -> expr -> char list

val to_bool_state : aware_state -> expr -> char list

val pretty_contract_expr_state : aware_state -> contract_expr -> char list

val is_bool_expr : expr -> bool

val coerce_int_rhs : aware_state -> expr -> char list

val nl : char list

val concat_with_sep : char list -> char list -> char list

val scope_body : char list -> char list

val emit_invariant_lines : aware_state -> contract_expr list -> char list

val emit_variant_lines : aware_state -> contract_expr list -> char list

val emit_ghost_decl_aware :
  aware_state -> ident -> ghost_type -> ghost_expr -> char list

val emit_ghost_assign_aware :
  aware_state -> ident -> ghost_type -> aug_op -> ghost_expr -> char list

val emit_cont : aware_state -> whyml_stmt -> char list -> char list

val emit_stmt_state_aware : aware_state -> whyml_stmt -> char list

val empty_aware_state : aware_state
