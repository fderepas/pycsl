
val eqb : char list -> char list -> bool

type json_value =
| JsonNull
| JsonBool of bool
| JsonInt of int
| JsonString of char list
| JsonList of json_value list
| JsonObject of (char list * json_value) list

type contracts_ir = { ci_requires : json_value list;
                      ci_ensures : json_value list;
                      ci_assigns : json_value list;
                      ci_raises : json_value list;
                      ci_no_exception : char list list;
                      ci_no_exception_all : bool }

type function_ir = { fi_name : char list;
                     fi_symbol_table : (char list * char list) list;
                     fi_return_annotation : char list;
                     fi_contracts : contracts_ir; fi_body : json_value list;
                     fi_function_variants : json_value list;
                     fi_diverges : bool; fi_trusted : bool;
                     fi_bounded_int : int option; fi_pure : bool;
                     fi_array2d_params : char list list;
                     fi_array1d_params : char list list; fi_kind : char list;
                     fi_self_type : char list }

type program_ir = { pi_type_decls : json_value list;
                    pi_functions : function_ir list;
                    pi_shared_vars : json_value list;
                    pi_mutex_invariants : (char list * json_value) list;
                    pi_thread_entries : char list list;
                    pi_lock_order : char list list }

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

val find_assoc :
  char list -> (char list * json_value) list -> json_value option

val json_field_get : char list -> json_value -> json_value option

val json_to_string : json_value -> char list option

val json_to_z : json_value -> int option

val json_to_list : json_value -> json_value list option

val option_map_list : ('a1 -> 'a2 option) -> 'a1 list -> 'a2 list option

val string_to_binop : char list -> binop option

val string_to_cmpop : char list -> cmpop option

val aug_string_to_binop : char list -> binop option

val string_to_aug_op : char list -> aug_op option

val string_to_ghost_type : char list -> ghost_type option

val ir_to_expr : int -> json_value -> expr option

val default_expr_fuel : int

val ir_to_contract_expr : int -> json_value -> contract_expr option

val default_contract_fuel : int

val ir_to_stmt_n : int -> json_value -> stmt option

val default_stmt_fuel : int

val ir_to_stmt : json_value -> stmt option

val json_has_key : char list -> (char list * json_value) list -> bool

val json_obj_has_all_keys : char list list -> json_value -> bool

val json_is_object : json_value -> bool

val required_top : char list list

val required_function : char list list

val required_contracts : char list list

val validate_contracts : json_value -> bool

val validate_function : json_value -> bool

val validate_functions_list : json_value list -> bool

val validate_ir : json_value -> bool
