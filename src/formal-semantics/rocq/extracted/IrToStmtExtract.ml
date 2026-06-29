
(** val eqb : char list -> char list -> bool **)

let rec eqb s1 s2 =
  match s1 with
  | [] -> (match s2 with
           | [] -> true
           | _::_ -> false)
  | c1::s1' ->
    (match s2 with
     | [] -> false
     | c2::s2' -> if (=) c1 c2 then eqb s1' s2' else false)

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

(** val find_assoc :
    char list -> (char list * json_value) list -> json_value option **)

let rec find_assoc key = function
| [] -> None
| p::rest ->
  let (k, v) = p in if eqb k key then Some v else find_assoc key rest

(** val json_field_get : char list -> json_value -> json_value option **)

let json_field_get key = function
| JsonObject kvs -> find_assoc key kvs
| _ -> None

(** val json_to_string : json_value -> char list option **)

let json_to_string = function
| JsonString s -> Some s
| _ -> None

(** val json_to_z : json_value -> int option **)

let json_to_z = function
| JsonInt n -> Some n
| _ -> None

(** val json_to_list : json_value -> json_value list option **)

let json_to_list = function
| JsonList xs -> Some xs
| _ -> None

(** val option_map_list :
    ('a1 -> 'a2 option) -> 'a1 list -> 'a2 list option **)

let rec option_map_list f = function
| [] -> Some []
| x::rest ->
  (match f x with
   | Some y ->
     (match option_map_list f rest with
      | Some ys -> Some (y::ys)
      | None -> None)
   | None -> None)

(** val string_to_binop : char list -> binop option **)

let string_to_binop s =
  if eqb s ('+'::[])
  then Some OpAdd
  else if eqb s ('-'::[])
       then Some OpSub
       else if eqb s ('*'::[])
            then Some OpMul
            else if eqb s ('/'::[])
                 then Some OpDiv
                 else if eqb s ('d'::('i'::('v'::[])))
                      then Some OpDiv
                      else if eqb s ('/'::('/'::[]))
                           then Some OpDiv
                           else if eqb s ('%'::[])
                                then Some OpMod
                                else if eqb s ('m'::('o'::('d'::[])))
                                     then Some OpMod
                                     else None

(** val string_to_cmpop : char list -> cmpop option **)

let string_to_cmpop s =
  if eqb s ('='::('='::[]))
  then Some OpEq
  else if eqb s ('!'::('='::[]))
       then Some OpNe
       else if eqb s ('<'::[])
            then Some OpLt
            else if eqb s ('<'::('='::[]))
                 then Some OpLe
                 else if eqb s ('>'::[])
                      then Some OpGt
                      else if eqb s ('>'::('='::[])) then Some OpGe else None

(** val aug_string_to_binop : char list -> binop option **)

let aug_string_to_binop =
  string_to_binop

(** val string_to_aug_op : char list -> aug_op option **)

let string_to_aug_op s =
  if eqb s ('+'::('='::[]))
  then Some AugAdd
  else if eqb s ('-'::('='::[]))
       then Some AugSub
       else if eqb s ('*'::('='::[])) then Some AugMul else None

(** val string_to_ghost_type : char list -> ghost_type option **)

let string_to_ghost_type s =
  if eqb s ('i'::('n'::('t'::[])))
  then Some GTInt
  else if eqb s ('s'::('t'::('r'::('i'::('n'::('g'::[]))))))
       then Some GTString
       else if eqb s ('a'::('r'::('r'::('a'::('y'::[])))))
            then Some GTArray
            else if eqb s
                      ('g'::('h'::('o'::('s'::('t'::('_'::('d'::('i'::('c'::('t'::[]))))))))))
                 then Some GTDict
                 else if eqb s
                           ('g'::('h'::('o'::('s'::('t'::('_'::('l'::('i'::('s'::('t'::[]))))))))))
                      then Some GTList
                      else if eqb s
                                ('g'::('h'::('o'::('s'::('t'::('_'::('s'::('e'::('t'::[])))))))))
                           then Some GTSet
                           else if eqb s
                                     ('t'::('u'::('p'::('l'::('e'::('2'::[]))))))
                                then Some GTTuple2
                                else if eqb s
                                          ('t'::('u'::('p'::('l'::('e'::('3'::[]))))))
                                     then Some GTTuple3
                                     else if eqb s
                                               ('t'::('u'::('p'::('l'::('e'::('4'::[]))))))
                                          then Some GTTuple4
                                          else None

(** val ir_to_expr : int -> json_value -> expr option **)

let rec ir_to_expr fuel e =
  (fun fO fS n -> if n=0 then fO () else fS (n-1))
    (fun _ -> None)
    (fun n ->
    let dispatch = fun t ->
      if eqb t ('N'::('u'::('m'::('b'::('e'::('r'::[]))))))
      then (match json_field_get ('v'::('a'::('l'::('u'::('e'::[]))))) e with
            | Some v ->
              (match json_to_z v with
               | Some k -> Some (EInt k)
               | None -> None)
            | None -> None)
      else if eqb t ('V'::('a'::('r'::[])))
           then (match json_field_get ('n'::('a'::('m'::('e'::[])))) e with
                 | Some v ->
                   (match json_to_string v with
                    | Some s -> Some (EVar s)
                    | None -> None)
                 | None -> None)
           else if eqb t ('U'::('n'::('a'::('r'::('y'::('O'::('p'::[])))))))
                then let operand_opt =
                       match json_field_get
                               ('o'::('p'::('e'::('r'::('a'::('n'::('d'::[])))))))
                               e with
                       | Some v -> Some v
                       | None ->
                         json_field_get ('e'::('x'::('p'::('r'::[])))) e
                     in
                     (match json_field_get ('o'::('p'::[])) e with
                      | Some opv ->
                        (match operand_opt with
                         | Some operand ->
                           (match json_to_string opv with
                            | Some s ->
                              (match s with
                               | [] -> None
                               | a::s0 ->
                                 (* If this appears, you're using Ascii internals. Please don't *)
 (fun f c ->
  let n = Char.code c in
  let h i = (n land (1 lsl i)) <> 0 in
  f (h 0) (h 1) (h 2) (h 3) (h 4) (h 5) (h 6) (h 7))
                                   (fun b b0 b1 b2 b3 b4 b5 b6 ->
                                   if b
                                   then if b0
                                        then if b1
                                             then None
                                             else if b2
                                                  then if b3
                                                       then None
                                                       else if b4
                                                            then if b5
                                                                 then None
                                                                 else 
                                                                   if b6
                                                                   then None
                                                                   else 
                                                                    (match s0 with
                                                                    | [] ->
                                                                    ir_to_expr
                                                                    n operand
                                                                    | _::_ ->
                                                                    None)
                                                            else None
                                                  else None
                                        else if b1
                                             then if b2
                                                  then if b3
                                                       then None
                                                       else if b4
                                                            then if b5
                                                                 then None
                                                                 else 
                                                                   if b6
                                                                   then None
                                                                   else 
                                                                    (match s0 with
                                                                    | [] ->
                                                                    (match 
                                                                    ir_to_expr
                                                                    n operand with
                                                                    | Some e' ->
                                                                    Some
                                                                    (ENeg e')
                                                                    | None ->
                                                                    None)
                                                                    | _::_ ->
                                                                    None)
                                                            else None
                                                  else None
                                             else None
                                   else None)
                                   a)
                            | None -> None)
                         | None -> None)
                      | None -> None)
                else if eqb t ('B'::('i'::('n'::('O'::('p'::[])))))
                     then (match json_field_get ('o'::('p'::[])) e with
                           | Some opv ->
                             (match json_field_get
                                      ('l'::('e'::('f'::('t'::[])))) e with
                              | Some lv ->
                                (match json_field_get
                                         ('r'::('i'::('g'::('h'::('t'::[])))))
                                         e with
                                 | Some rv ->
                                   (match json_to_string opv with
                                    | Some opstr ->
                                      (match string_to_binop opstr with
                                       | Some op ->
                                         (match ir_to_expr n lv with
                                          | Some le ->
                                            (match ir_to_expr n rv with
                                             | Some re ->
                                               Some (EBinOp (op, le, re))
                                             | None ->
                                               (match string_to_cmpop opstr with
                                                | Some cop ->
                                                  (match ir_to_expr n lv with
                                                   | Some le0 ->
                                                     (match ir_to_expr n rv with
                                                      | Some re ->
                                                        Some (ECmp (cop, le0,
                                                          re))
                                                      | None -> None)
                                                   | None -> None)
                                                | None -> None))
                                          | None ->
                                            (match string_to_cmpop opstr with
                                             | Some cop ->
                                               (match ir_to_expr n lv with
                                                | Some le ->
                                                  (match ir_to_expr n rv with
                                                   | Some re ->
                                                     Some (ECmp (cop, le, re))
                                                   | None -> None)
                                                | None -> None)
                                             | None -> None))
                                       | None ->
                                         (match string_to_cmpop opstr with
                                          | Some cop ->
                                            (match ir_to_expr n lv with
                                             | Some le ->
                                               (match ir_to_expr n rv with
                                                | Some re ->
                                                  Some (ECmp (cop, le, re))
                                                | None -> None)
                                             | None -> None)
                                          | None -> None))
                                    | None -> None)
                                 | None -> None)
                              | None -> None)
                           | None -> None)
                     else if eqb t
                               ('S'::('u'::('b'::('s'::('c'::('r'::('i'::('p'::('t'::[])))))))))
                          then (match json_field_get
                                        ('v'::('a'::('l'::('u'::('e'::[])))))
                                        e with
                                | Some arrv ->
                                  (match json_field_get
                                           ('i'::('n'::('d'::('e'::('x'::[])))))
                                           e with
                                   | Some idxv ->
                                     (match json_field_get
                                              ('t'::('y'::('p'::('e'::[]))))
                                              arrv with
                                      | Some arrtype ->
                                        (match json_to_string arrtype with
                                         | Some s ->
                                           (match s with
                                            | [] -> None
                                            | a::s0 ->
                                              (* If this appears, you're using Ascii internals. Please don't *)
 (fun f c ->
  let n = Char.code c in
  let h i = (n land (1 lsl i)) <> 0 in
  f (h 0) (h 1) (h 2) (h 3) (h 4) (h 5) (h 6) (h 7))
                                                (fun b b0 b1 b2 b3 b4 b5 b6 ->
                                                if b
                                                then None
                                                else if b0
                                                     then if b1
                                                          then if b2
                                                               then None
                                                               else if b3
                                                                    then 
                                                                    if b4
                                                                    then None
                                                                    else 
                                                                    if b5
                                                                    then 
                                                                    if b6
                                                                    then None
                                                                    else 
                                                                    (match s0 with
                                                                    | [] ->
                                                                    None
                                                                    | a0::s1 ->
                                                                    (* If this appears, you're using Ascii internals. Please don't *)
 (fun f c ->
  let n = Char.code c in
  let h i = (n land (1 lsl i)) <> 0 in
  f (h 0) (h 1) (h 2) (h 3) (h 4) (h 5) (h 6) (h 7))
                                                                    (fun b7 b8 b9 b10 b11 b12 b13 b14 ->
                                                                    if b7
                                                                    then 
                                                                    if b8
                                                                    then None
                                                                    else 
                                                                    if b9
                                                                    then None
                                                                    else 
                                                                    if b10
                                                                    then None
                                                                    else 
                                                                    if b11
                                                                    then None
                                                                    else 
                                                                    if b12
                                                                    then 
                                                                    if b13
                                                                    then 
                                                                    if b14
                                                                    then None
                                                                    else 
                                                                    (match s1 with
                                                                    | [] ->
                                                                    None
                                                                    | a1::s2 ->
                                                                    (* If this appears, you're using Ascii internals. Please don't *)
 (fun f c ->
  let n = Char.code c in
  let h i = (n land (1 lsl i)) <> 0 in
  f (h 0) (h 1) (h 2) (h 3) (h 4) (h 5) (h 6) (h 7))
                                                                    (fun b15 b16 b17 b18 b19 b20 b21 b22 ->
                                                                    if b15
                                                                    then None
                                                                    else 
                                                                    if b16
                                                                    then 
                                                                    if b17
                                                                    then None
                                                                    else 
                                                                    if b18
                                                                    then None
                                                                    else 
                                                                    if b19
                                                                    then 
                                                                    if b20
                                                                    then 
                                                                    if b21
                                                                    then 
                                                                    if b22
                                                                    then None
                                                                    else 
                                                                    (match s2 with
                                                                    | [] ->
                                                                    (match 
                                                                    json_field_get
                                                                    ('n'::('a'::('m'::('e'::[]))))
                                                                    arrv with
                                                                    | Some namev ->
                                                                    (match 
                                                                    json_to_string
                                                                    namev with
                                                                    | Some nm ->
                                                                    (match 
                                                                    ir_to_expr
                                                                    n idxv with
                                                                    | Some ie ->
                                                                    Some
                                                                    (ESubscript
                                                                    (nm, ie))
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | _::_ ->
                                                                    None)
                                                                    else None
                                                                    else None
                                                                    else None
                                                                    else None)
                                                                    a1)
                                                                    else None
                                                                    else None
                                                                    else None)
                                                                    a0)
                                                                    else None
                                                                    else None
                                                          else None
                                                     else None)
                                                a)
                                         | None -> None)
                                      | None -> None)
                                   | None -> None)
                                | None -> None)
                          else if eqb t ('C'::('a'::('l'::('l'::[]))))
                               then (match json_field_get
                                             ('f'::('u'::('n'::('c'::[])))) e with
                                     | Some funcv ->
                                       (match json_field_get
                                                ('a'::('r'::('g'::('s'::[]))))
                                                e with
                                        | Some argsv ->
                                          (match json_to_string funcv with
                                           | Some fname ->
                                             (match fname with
                                              | [] ->
                                                (match json_to_list argsv with
                                                 | Some args ->
                                                   (match option_map_list
                                                            (ir_to_expr n)
                                                            args with
                                                    | Some converted ->
                                                      Some (ECall (fname,
                                                        converted))
                                                    | None -> None)
                                                 | None -> None)
                                              | a::s ->
                                                (* If this appears, you're using Ascii internals. Please don't *)
 (fun f c ->
  let n = Char.code c in
  let h i = (n land (1 lsl i)) <> 0 in
  f (h 0) (h 1) (h 2) (h 3) (h 4) (h 5) (h 6) (h 7))
                                                  (fun b b0 b1 b2 b3 b4 b5 b6 ->
                                                  if b
                                                  then (match json_to_list
                                                                argsv with
                                                        | Some args ->
                                                          (match option_map_list
                                                                   (ir_to_expr
                                                                    n) args with
                                                           | Some converted ->
                                                             Some (ECall
                                                               (fname,
                                                               converted))
                                                           | None -> None)
                                                        | None -> None)
                                                  else if b0
                                                       then (match json_to_list
                                                                    argsv with
                                                             | Some args ->
                                                               (match 
                                                                option_map_list
                                                                  (ir_to_expr
                                                                    n) args with
                                                                | Some converted ->
                                                                  Some (ECall
                                                                    (fname,
                                                                    converted))
                                                                | None -> None)
                                                             | None -> None)
                                                       else if b1
                                                            then if b2
                                                                 then 
                                                                   if b3
                                                                   then 
                                                                    (match 
                                                                    json_to_list
                                                                    argsv with
                                                                    | Some args ->
                                                                    (match 
                                                                    option_map_list
                                                                    (ir_to_expr
                                                                    n) args with
                                                                    | Some converted ->
                                                                    Some
                                                                    (ECall
                                                                    (fname,
                                                                    converted))
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                   else 
                                                                    if b4
                                                                    then 
                                                                    if b5
                                                                    then 
                                                                    if b6
                                                                    then 
                                                                    (match 
                                                                    json_to_list
                                                                    argsv with
                                                                    | Some args ->
                                                                    (match 
                                                                    option_map_list
                                                                    (ir_to_expr
                                                                    n) args with
                                                                    | Some converted ->
                                                                    Some
                                                                    (ECall
                                                                    (fname,
                                                                    converted))
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    else 
                                                                    (match s with
                                                                    | [] ->
                                                                    (match 
                                                                    json_to_list
                                                                    argsv with
                                                                    | Some args ->
                                                                    (match 
                                                                    option_map_list
                                                                    (ir_to_expr
                                                                    n) args with
                                                                    | Some converted ->
                                                                    Some
                                                                    (ECall
                                                                    (fname,
                                                                    converted))
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | a0::s0 ->
                                                                    (* If this appears, you're using Ascii internals. Please don't *)
 (fun f c ->
  let n = Char.code c in
  let h i = (n land (1 lsl i)) <> 0 in
  f (h 0) (h 1) (h 2) (h 3) (h 4) (h 5) (h 6) (h 7))
                                                                    (fun b7 b8 b9 b10 b11 b12 b13 b14 ->
                                                                    if b7
                                                                    then 
                                                                    if b8
                                                                    then 
                                                                    (match 
                                                                    json_to_list
                                                                    argsv with
                                                                    | Some args ->
                                                                    (match 
                                                                    option_map_list
                                                                    (ir_to_expr
                                                                    n) args with
                                                                    | Some converted ->
                                                                    Some
                                                                    (ECall
                                                                    (fname,
                                                                    converted))
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    else 
                                                                    if b9
                                                                    then 
                                                                    if b10
                                                                    then 
                                                                    (match 
                                                                    json_to_list
                                                                    argsv with
                                                                    | Some args ->
                                                                    (match 
                                                                    option_map_list
                                                                    (ir_to_expr
                                                                    n) args with
                                                                    | Some converted ->
                                                                    Some
                                                                    (ECall
                                                                    (fname,
                                                                    converted))
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    else 
                                                                    if b11
                                                                    then 
                                                                    (match 
                                                                    json_to_list
                                                                    argsv with
                                                                    | Some args ->
                                                                    (match 
                                                                    option_map_list
                                                                    (ir_to_expr
                                                                    n) args with
                                                                    | Some converted ->
                                                                    Some
                                                                    (ECall
                                                                    (fname,
                                                                    converted))
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    else 
                                                                    if b12
                                                                    then 
                                                                    if b13
                                                                    then 
                                                                    if b14
                                                                    then 
                                                                    (match 
                                                                    json_to_list
                                                                    argsv with
                                                                    | Some args ->
                                                                    (match 
                                                                    option_map_list
                                                                    (ir_to_expr
                                                                    n) args with
                                                                    | Some converted ->
                                                                    Some
                                                                    (ECall
                                                                    (fname,
                                                                    converted))
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    else 
                                                                    (match s0 with
                                                                    | [] ->
                                                                    (match 
                                                                    json_to_list
                                                                    argsv with
                                                                    | Some args ->
                                                                    (match 
                                                                    option_map_list
                                                                    (ir_to_expr
                                                                    n) args with
                                                                    | Some converted ->
                                                                    Some
                                                                    (ECall
                                                                    (fname,
                                                                    converted))
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | a1::s1 ->
                                                                    (* If this appears, you're using Ascii internals. Please don't *)
 (fun f c ->
  let n = Char.code c in
  let h i = (n land (1 lsl i)) <> 0 in
  f (h 0) (h 1) (h 2) (h 3) (h 4) (h 5) (h 6) (h 7))
                                                                    (fun b15 b16 b17 b18 b19 b20 b21 b22 ->
                                                                    if b15
                                                                    then 
                                                                    (match 
                                                                    json_to_list
                                                                    argsv with
                                                                    | Some args ->
                                                                    (match 
                                                                    option_map_list
                                                                    (ir_to_expr
                                                                    n) args with
                                                                    | Some converted ->
                                                                    Some
                                                                    (ECall
                                                                    (fname,
                                                                    converted))
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    else 
                                                                    if b16
                                                                    then 
                                                                    if b17
                                                                    then 
                                                                    if b18
                                                                    then 
                                                                    if b19
                                                                    then 
                                                                    (match 
                                                                    json_to_list
                                                                    argsv with
                                                                    | Some args ->
                                                                    (match 
                                                                    option_map_list
                                                                    (ir_to_expr
                                                                    n) args with
                                                                    | Some converted ->
                                                                    Some
                                                                    (ECall
                                                                    (fname,
                                                                    converted))
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    else 
                                                                    if b20
                                                                    then 
                                                                    if b21
                                                                    then 
                                                                    if b22
                                                                    then 
                                                                    (match 
                                                                    json_to_list
                                                                    argsv with
                                                                    | Some args ->
                                                                    (match 
                                                                    option_map_list
                                                                    (ir_to_expr
                                                                    n) args with
                                                                    | Some converted ->
                                                                    Some
                                                                    (ECall
                                                                    (fname,
                                                                    converted))
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    else 
                                                                    (match s1 with
                                                                    | [] ->
                                                                    (match 
                                                                    json_to_list
                                                                    argsv with
                                                                    | Some args ->
                                                                    (match args with
                                                                    | [] ->
                                                                    (match 
                                                                    option_map_list
                                                                    (ir_to_expr
                                                                    n) args with
                                                                    | Some converted ->
                                                                    Some
                                                                    (ECall
                                                                    (fname,
                                                                    converted))
                                                                    | None ->
                                                                    None)
                                                                    | arg::l ->
                                                                    (match l with
                                                                    | [] ->
                                                                    (match 
                                                                    json_field_get
                                                                    ('t'::('y'::('p'::('e'::[]))))
                                                                    arg with
                                                                    | Some argtype ->
                                                                    (match 
                                                                    json_to_string
                                                                    argtype with
                                                                    | Some s2 ->
                                                                    (match s2 with
                                                                    | [] ->
                                                                    (match 
                                                                    option_map_list
                                                                    (ir_to_expr
                                                                    n)
                                                                    (arg::[]) with
                                                                    | Some args0 ->
                                                                    Some
                                                                    (ECall
                                                                    (('l'::('e'::('n'::[]))),
                                                                    args0))
                                                                    | None ->
                                                                    None)
                                                                    | a2::s3 ->
                                                                    (* If this appears, you're using Ascii internals. Please don't *)
 (fun f c ->
  let n = Char.code c in
  let h i = (n land (1 lsl i)) <> 0 in
  f (h 0) (h 1) (h 2) (h 3) (h 4) (h 5) (h 6) (h 7))
                                                                    (fun b23 b24 b25 b26 b27 b28 b29 b30 ->
                                                                    if b23
                                                                    then 
                                                                    (match 
                                                                    option_map_list
                                                                    (ir_to_expr
                                                                    n)
                                                                    (arg::[]) with
                                                                    | Some args0 ->
                                                                    Some
                                                                    (ECall
                                                                    (('l'::('e'::('n'::[]))),
                                                                    args0))
                                                                    | None ->
                                                                    None)
                                                                    else 
                                                                    if b24
                                                                    then 
                                                                    if b25
                                                                    then 
                                                                    if b26
                                                                    then 
                                                                    (match 
                                                                    option_map_list
                                                                    (ir_to_expr
                                                                    n)
                                                                    (arg::[]) with
                                                                    | Some args0 ->
                                                                    Some
                                                                    (ECall
                                                                    (('l'::('e'::('n'::[]))),
                                                                    args0))
                                                                    | None ->
                                                                    None)
                                                                    else 
                                                                    if b27
                                                                    then 
                                                                    if b28
                                                                    then 
                                                                    (match 
                                                                    option_map_list
                                                                    (ir_to_expr
                                                                    n)
                                                                    (arg::[]) with
                                                                    | Some args0 ->
                                                                    Some
                                                                    (ECall
                                                                    (('l'::('e'::('n'::[]))),
                                                                    args0))
                                                                    | None ->
                                                                    None)
                                                                    else 
                                                                    if b29
                                                                    then 
                                                                    if b30
                                                                    then 
                                                                    (match 
                                                                    option_map_list
                                                                    (ir_to_expr
                                                                    n)
                                                                    (arg::[]) with
                                                                    | Some args0 ->
                                                                    Some
                                                                    (ECall
                                                                    (('l'::('e'::('n'::[]))),
                                                                    args0))
                                                                    | None ->
                                                                    None)
                                                                    else 
                                                                    (match s3 with
                                                                    | [] ->
                                                                    (match 
                                                                    option_map_list
                                                                    (ir_to_expr
                                                                    n)
                                                                    (arg::[]) with
                                                                    | Some args0 ->
                                                                    Some
                                                                    (ECall
                                                                    (('l'::('e'::('n'::[]))),
                                                                    args0))
                                                                    | None ->
                                                                    None)
                                                                    | a3::s4 ->
                                                                    (* If this appears, you're using Ascii internals. Please don't *)
 (fun f c ->
  let n = Char.code c in
  let h i = (n land (1 lsl i)) <> 0 in
  f (h 0) (h 1) (h 2) (h 3) (h 4) (h 5) (h 6) (h 7))
                                                                    (fun b31 b32 b33 b34 b35 b36 b37 b38 ->
                                                                    if b31
                                                                    then 
                                                                    if b32
                                                                    then 
                                                                    (match 
                                                                    option_map_list
                                                                    (ir_to_expr
                                                                    n)
                                                                    (arg::[]) with
                                                                    | Some args0 ->
                                                                    Some
                                                                    (ECall
                                                                    (('l'::('e'::('n'::[]))),
                                                                    args0))
                                                                    | None ->
                                                                    None)
                                                                    else 
                                                                    if b33
                                                                    then 
                                                                    (match 
                                                                    option_map_list
                                                                    (ir_to_expr
                                                                    n)
                                                                    (arg::[]) with
                                                                    | Some args0 ->
                                                                    Some
                                                                    (ECall
                                                                    (('l'::('e'::('n'::[]))),
                                                                    args0))
                                                                    | None ->
                                                                    None)
                                                                    else 
                                                                    if b34
                                                                    then 
                                                                    (match 
                                                                    option_map_list
                                                                    (ir_to_expr
                                                                    n)
                                                                    (arg::[]) with
                                                                    | Some args0 ->
                                                                    Some
                                                                    (ECall
                                                                    (('l'::('e'::('n'::[]))),
                                                                    args0))
                                                                    | None ->
                                                                    None)
                                                                    else 
                                                                    if b35
                                                                    then 
                                                                    (match 
                                                                    option_map_list
                                                                    (ir_to_expr
                                                                    n)
                                                                    (arg::[]) with
                                                                    | Some args0 ->
                                                                    Some
                                                                    (ECall
                                                                    (('l'::('e'::('n'::[]))),
                                                                    args0))
                                                                    | None ->
                                                                    None)
                                                                    else 
                                                                    if b36
                                                                    then 
                                                                    if b37
                                                                    then 
                                                                    if b38
                                                                    then 
                                                                    (match 
                                                                    option_map_list
                                                                    (ir_to_expr
                                                                    n)
                                                                    (arg::[]) with
                                                                    | Some args0 ->
                                                                    Some
                                                                    (ECall
                                                                    (('l'::('e'::('n'::[]))),
                                                                    args0))
                                                                    | None ->
                                                                    None)
                                                                    else 
                                                                    (match s4 with
                                                                    | [] ->
                                                                    (match 
                                                                    option_map_list
                                                                    (ir_to_expr
                                                                    n)
                                                                    (arg::[]) with
                                                                    | Some args0 ->
                                                                    Some
                                                                    (ECall
                                                                    (('l'::('e'::('n'::[]))),
                                                                    args0))
                                                                    | None ->
                                                                    None)
                                                                    | a4::s5 ->
                                                                    (* If this appears, you're using Ascii internals. Please don't *)
 (fun f c ->
  let n = Char.code c in
  let h i = (n land (1 lsl i)) <> 0 in
  f (h 0) (h 1) (h 2) (h 3) (h 4) (h 5) (h 6) (h 7))
                                                                    (fun b39 b40 b41 b42 b43 b44 b45 b46 ->
                                                                    if b39
                                                                    then 
                                                                    (match 
                                                                    option_map_list
                                                                    (ir_to_expr
                                                                    n)
                                                                    (arg::[]) with
                                                                    | Some args0 ->
                                                                    Some
                                                                    (ECall
                                                                    (('l'::('e'::('n'::[]))),
                                                                    args0))
                                                                    | None ->
                                                                    None)
                                                                    else 
                                                                    if b40
                                                                    then 
                                                                    if b41
                                                                    then 
                                                                    (match 
                                                                    option_map_list
                                                                    (ir_to_expr
                                                                    n)
                                                                    (arg::[]) with
                                                                    | Some args0 ->
                                                                    Some
                                                                    (ECall
                                                                    (('l'::('e'::('n'::[]))),
                                                                    args0))
                                                                    | None ->
                                                                    None)
                                                                    else 
                                                                    if b42
                                                                    then 
                                                                    (match 
                                                                    option_map_list
                                                                    (ir_to_expr
                                                                    n)
                                                                    (arg::[]) with
                                                                    | Some args0 ->
                                                                    Some
                                                                    (ECall
                                                                    (('l'::('e'::('n'::[]))),
                                                                    args0))
                                                                    | None ->
                                                                    None)
                                                                    else 
                                                                    if b43
                                                                    then 
                                                                    if b44
                                                                    then 
                                                                    if b45
                                                                    then 
                                                                    if b46
                                                                    then 
                                                                    (match 
                                                                    option_map_list
                                                                    (ir_to_expr
                                                                    n)
                                                                    (arg::[]) with
                                                                    | Some args0 ->
                                                                    Some
                                                                    (ECall
                                                                    (('l'::('e'::('n'::[]))),
                                                                    args0))
                                                                    | None ->
                                                                    None)
                                                                    else 
                                                                    (match s5 with
                                                                    | [] ->
                                                                    (match 
                                                                    json_field_get
                                                                    ('n'::('a'::('m'::('e'::[]))))
                                                                    arg with
                                                                    | Some nv ->
                                                                    (match 
                                                                    json_to_string
                                                                    nv with
                                                                    | Some nm ->
                                                                    Some
                                                                    (ELen nm)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | _::_ ->
                                                                    (match 
                                                                    option_map_list
                                                                    (ir_to_expr
                                                                    n)
                                                                    (arg::[]) with
                                                                    | Some args0 ->
                                                                    Some
                                                                    (ECall
                                                                    (('l'::('e'::('n'::[]))),
                                                                    args0))
                                                                    | None ->
                                                                    None))
                                                                    else 
                                                                    (match 
                                                                    option_map_list
                                                                    (ir_to_expr
                                                                    n)
                                                                    (arg::[]) with
                                                                    | Some args0 ->
                                                                    Some
                                                                    (ECall
                                                                    (('l'::('e'::('n'::[]))),
                                                                    args0))
                                                                    | None ->
                                                                    None)
                                                                    else 
                                                                    (match 
                                                                    option_map_list
                                                                    (ir_to_expr
                                                                    n)
                                                                    (arg::[]) with
                                                                    | Some args0 ->
                                                                    Some
                                                                    (ECall
                                                                    (('l'::('e'::('n'::[]))),
                                                                    args0))
                                                                    | None ->
                                                                    None)
                                                                    else 
                                                                    (match 
                                                                    option_map_list
                                                                    (ir_to_expr
                                                                    n)
                                                                    (arg::[]) with
                                                                    | Some args0 ->
                                                                    Some
                                                                    (ECall
                                                                    (('l'::('e'::('n'::[]))),
                                                                    args0))
                                                                    | None ->
                                                                    None)
                                                                    else 
                                                                    (match 
                                                                    option_map_list
                                                                    (ir_to_expr
                                                                    n)
                                                                    (arg::[]) with
                                                                    | Some args0 ->
                                                                    Some
                                                                    (ECall
                                                                    (('l'::('e'::('n'::[]))),
                                                                    args0))
                                                                    | None ->
                                                                    None))
                                                                    a4)
                                                                    else 
                                                                    (match 
                                                                    option_map_list
                                                                    (ir_to_expr
                                                                    n)
                                                                    (arg::[]) with
                                                                    | Some args0 ->
                                                                    Some
                                                                    (ECall
                                                                    (('l'::('e'::('n'::[]))),
                                                                    args0))
                                                                    | None ->
                                                                    None)
                                                                    else 
                                                                    (match 
                                                                    option_map_list
                                                                    (ir_to_expr
                                                                    n)
                                                                    (arg::[]) with
                                                                    | Some args0 ->
                                                                    Some
                                                                    (ECall
                                                                    (('l'::('e'::('n'::[]))),
                                                                    args0))
                                                                    | None ->
                                                                    None)
                                                                    else 
                                                                    (match 
                                                                    option_map_list
                                                                    (ir_to_expr
                                                                    n)
                                                                    (arg::[]) with
                                                                    | Some args0 ->
                                                                    Some
                                                                    (ECall
                                                                    (('l'::('e'::('n'::[]))),
                                                                    args0))
                                                                    | None ->
                                                                    None))
                                                                    a3)
                                                                    else 
                                                                    (match 
                                                                    option_map_list
                                                                    (ir_to_expr
                                                                    n)
                                                                    (arg::[]) with
                                                                    | Some args0 ->
                                                                    Some
                                                                    (ECall
                                                                    (('l'::('e'::('n'::[]))),
                                                                    args0))
                                                                    | None ->
                                                                    None)
                                                                    else 
                                                                    (match 
                                                                    option_map_list
                                                                    (ir_to_expr
                                                                    n)
                                                                    (arg::[]) with
                                                                    | Some args0 ->
                                                                    Some
                                                                    (ECall
                                                                    (('l'::('e'::('n'::[]))),
                                                                    args0))
                                                                    | None ->
                                                                    None)
                                                                    else 
                                                                    (match 
                                                                    option_map_list
                                                                    (ir_to_expr
                                                                    n)
                                                                    (arg::[]) with
                                                                    | Some args0 ->
                                                                    Some
                                                                    (ECall
                                                                    (('l'::('e'::('n'::[]))),
                                                                    args0))
                                                                    | None ->
                                                                    None)
                                                                    else 
                                                                    (match 
                                                                    option_map_list
                                                                    (ir_to_expr
                                                                    n)
                                                                    (arg::[]) with
                                                                    | Some args0 ->
                                                                    Some
                                                                    (ECall
                                                                    (('l'::('e'::('n'::[]))),
                                                                    args0))
                                                                    | None ->
                                                                    None))
                                                                    a2)
                                                                    | None ->
                                                                    (match 
                                                                    option_map_list
                                                                    (ir_to_expr
                                                                    n)
                                                                    (arg::[]) with
                                                                    | Some args0 ->
                                                                    Some
                                                                    (ECall
                                                                    (('l'::('e'::('n'::[]))),
                                                                    args0))
                                                                    | None ->
                                                                    None))
                                                                    | None ->
                                                                    None)
                                                                    | _::_ ->
                                                                    (match 
                                                                    option_map_list
                                                                    (ir_to_expr
                                                                    n) args with
                                                                    | Some converted ->
                                                                    Some
                                                                    (ECall
                                                                    (fname,
                                                                    converted))
                                                                    | None ->
                                                                    None)))
                                                                    | None ->
                                                                    None)
                                                                    | _::_ ->
                                                                    (match 
                                                                    json_to_list
                                                                    argsv with
                                                                    | Some args ->
                                                                    (match 
                                                                    option_map_list
                                                                    (ir_to_expr
                                                                    n) args with
                                                                    | Some converted ->
                                                                    Some
                                                                    (ECall
                                                                    (fname,
                                                                    converted))
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None))
                                                                    else 
                                                                    (match 
                                                                    json_to_list
                                                                    argsv with
                                                                    | Some args ->
                                                                    (match 
                                                                    option_map_list
                                                                    (ir_to_expr
                                                                    n) args with
                                                                    | Some converted ->
                                                                    Some
                                                                    (ECall
                                                                    (fname,
                                                                    converted))
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    else 
                                                                    (match 
                                                                    json_to_list
                                                                    argsv with
                                                                    | Some args ->
                                                                    (match 
                                                                    option_map_list
                                                                    (ir_to_expr
                                                                    n) args with
                                                                    | Some converted ->
                                                                    Some
                                                                    (ECall
                                                                    (fname,
                                                                    converted))
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    else 
                                                                    (match 
                                                                    json_to_list
                                                                    argsv with
                                                                    | Some args ->
                                                                    (match 
                                                                    option_map_list
                                                                    (ir_to_expr
                                                                    n) args with
                                                                    | Some converted ->
                                                                    Some
                                                                    (ECall
                                                                    (fname,
                                                                    converted))
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    else 
                                                                    (match 
                                                                    json_to_list
                                                                    argsv with
                                                                    | Some args ->
                                                                    (match 
                                                                    option_map_list
                                                                    (ir_to_expr
                                                                    n) args with
                                                                    | Some converted ->
                                                                    Some
                                                                    (ECall
                                                                    (fname,
                                                                    converted))
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    else 
                                                                    (match 
                                                                    json_to_list
                                                                    argsv with
                                                                    | Some args ->
                                                                    (match 
                                                                    option_map_list
                                                                    (ir_to_expr
                                                                    n) args with
                                                                    | Some converted ->
                                                                    Some
                                                                    (ECall
                                                                    (fname,
                                                                    converted))
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None))
                                                                    a1)
                                                                    else 
                                                                    (match 
                                                                    json_to_list
                                                                    argsv with
                                                                    | Some args ->
                                                                    (match 
                                                                    option_map_list
                                                                    (ir_to_expr
                                                                    n) args with
                                                                    | Some converted ->
                                                                    Some
                                                                    (ECall
                                                                    (fname,
                                                                    converted))
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    else 
                                                                    (match 
                                                                    json_to_list
                                                                    argsv with
                                                                    | Some args ->
                                                                    (match 
                                                                    option_map_list
                                                                    (ir_to_expr
                                                                    n) args with
                                                                    | Some converted ->
                                                                    Some
                                                                    (ECall
                                                                    (fname,
                                                                    converted))
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    else 
                                                                    (match 
                                                                    json_to_list
                                                                    argsv with
                                                                    | Some args ->
                                                                    (match 
                                                                    option_map_list
                                                                    (ir_to_expr
                                                                    n) args with
                                                                    | Some converted ->
                                                                    Some
                                                                    (ECall
                                                                    (fname,
                                                                    converted))
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    else 
                                                                    (match 
                                                                    json_to_list
                                                                    argsv with
                                                                    | Some args ->
                                                                    (match 
                                                                    option_map_list
                                                                    (ir_to_expr
                                                                    n) args with
                                                                    | Some converted ->
                                                                    Some
                                                                    (ECall
                                                                    (fname,
                                                                    converted))
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None))
                                                                    a0)
                                                                    else 
                                                                    (match 
                                                                    json_to_list
                                                                    argsv with
                                                                    | Some args ->
                                                                    (match 
                                                                    option_map_list
                                                                    (ir_to_expr
                                                                    n) args with
                                                                    | Some converted ->
                                                                    Some
                                                                    (ECall
                                                                    (fname,
                                                                    converted))
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    else 
                                                                    (match 
                                                                    json_to_list
                                                                    argsv with
                                                                    | Some args ->
                                                                    (match 
                                                                    option_map_list
                                                                    (ir_to_expr
                                                                    n) args with
                                                                    | Some converted ->
                                                                    Some
                                                                    (ECall
                                                                    (fname,
                                                                    converted))
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                 else 
                                                                   (match 
                                                                    json_to_list
                                                                    argsv with
                                                                    | Some args ->
                                                                    (match 
                                                                    option_map_list
                                                                    (ir_to_expr
                                                                    n) args with
                                                                    | Some converted ->
                                                                    Some
                                                                    (ECall
                                                                    (fname,
                                                                    converted))
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                            else (match 
                                                                  json_to_list
                                                                    argsv with
                                                                  | Some args ->
                                                                    (match 
                                                                    option_map_list
                                                                    (ir_to_expr
                                                                    n) args with
                                                                    | Some converted ->
                                                                    Some
                                                                    (ECall
                                                                    (fname,
                                                                    converted))
                                                                    | None ->
                                                                    None)
                                                                  | None ->
                                                                    None))
                                                  a)
                                           | None -> None)
                                        | None -> None)
                                     | None -> None)
                               else if eqb t
                                         ('F'::('i'::('e'::('l'::('d'::('G'::('e'::('t'::[]))))))))
                                    then (match json_field_get
                                                  ('o'::('b'::('j'::('e'::('c'::('t'::[]))))))
                                                  e with
                                          | Some objv ->
                                            (match json_field_get
                                                     ('f'::('i'::('e'::('l'::('d'::[])))))
                                                     e with
                                             | Some fv ->
                                               (match json_to_string objv with
                                                | Some obj ->
                                                  (match json_to_string fv with
                                                   | Some f ->
                                                     Some (EFieldGet (obj, f))
                                                   | None -> None)
                                                | None -> None)
                                             | None -> None)
                                          | None -> None)
                                    else if eqb t
                                              ('N'::('a'::('m'::('e'::('d'::('E'::('x'::('p'::('r'::[])))))))))
                                         then (match json_field_get
                                                       ('v'::('a'::('l'::('u'::('e'::[])))))
                                                       e with
                                               | Some v -> ir_to_expr n v
                                               | None -> None)
                                         else None
    in
    (match json_field_get ('t'::('y'::('p'::('e'::[])))) e with
     | Some tv ->
       (match json_to_string tv with
        | Some t -> dispatch t
        | None -> None)
     | None -> None))
    fuel

(** val default_expr_fuel : int **)

let default_expr_fuel =
  Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    0)))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))

(** val ir_to_contract_expr : int -> json_value -> contract_expr option **)

let rec ir_to_contract_expr fuel e =
  (fun fO fS n -> if n=0 then fO () else fS (n-1))
    (fun _ -> None)
    (fun n ->
    let dispatch = fun t ->
      if eqb t ('N'::('u'::('m'::('b'::('e'::('r'::[]))))))
      then (match json_field_get ('v'::('a'::('l'::('u'::('e'::[]))))) e with
            | Some v ->
              (match json_to_z v with
               | Some k -> Some (CInt k)
               | None -> None)
            | None -> None)
      else if eqb t ('V'::('a'::('r'::[])))
           then (match json_field_get ('n'::('a'::('m'::('e'::[])))) e with
                 | Some v ->
                   (match json_to_string v with
                    | Some s -> Some (CVar s)
                    | None -> None)
                 | None -> None)
           else if eqb t ('R'::('e'::('s'::('u'::('l'::('t'::[]))))))
                then Some CResult
                else if eqb t
                          ('B'::('o'::('o'::('l'::('L'::('i'::('t'::[])))))))
                     then (match json_field_get
                                   ('v'::('a'::('l'::('u'::('e'::[]))))) e with
                           | Some v ->
                             (match v with
                              | JsonBool b -> Some (CBoolLit b)
                              | _ -> None)
                           | None -> None)
                     else if eqb t
                               ('L'::('e'::('n'::('g'::('t'::('h'::[]))))))
                          then (match json_field_get
                                        ('n'::('a'::('m'::('e'::[])))) e with
                                | Some v ->
                                  (match json_to_string v with
                                   | Some s -> Some (CLength s)
                                   | None -> None)
                                | None -> None)
                          else if eqb t
                                    ('S'::('u'::('b'::('s'::('c'::('r'::('i'::('p'::('t'::[])))))))))
                               then (match json_field_get
                                             ('v'::('a'::('l'::('u'::('e'::[])))))
                                             e with
                                     | Some arrv ->
                                       (match json_field_get
                                                ('i'::('n'::('d'::('e'::('x'::[])))))
                                                e with
                                        | Some idxv ->
                                          (match json_field_get
                                                   ('t'::('y'::('p'::('e'::[]))))
                                                   arrv with
                                           | Some arrtype ->
                                             (match json_to_string arrtype with
                                              | Some s ->
                                                (match s with
                                                 | [] -> None
                                                 | a::s0 ->
                                                   (* If this appears, you're using Ascii internals. Please don't *)
 (fun f c ->
  let n = Char.code c in
  let h i = (n land (1 lsl i)) <> 0 in
  f (h 0) (h 1) (h 2) (h 3) (h 4) (h 5) (h 6) (h 7))
                                                     (fun b b0 b1 b2 b3 b4 b5 b6 ->
                                                     if b
                                                     then None
                                                     else if b0
                                                          then if b1
                                                               then if b2
                                                                    then None
                                                                    else 
                                                                    if b3
                                                                    then 
                                                                    if b4
                                                                    then None
                                                                    else 
                                                                    if b5
                                                                    then 
                                                                    if b6
                                                                    then None
                                                                    else 
                                                                    (match s0 with
                                                                    | [] ->
                                                                    None
                                                                    | a0::s1 ->
                                                                    (* If this appears, you're using Ascii internals. Please don't *)
 (fun f c ->
  let n = Char.code c in
  let h i = (n land (1 lsl i)) <> 0 in
  f (h 0) (h 1) (h 2) (h 3) (h 4) (h 5) (h 6) (h 7))
                                                                    (fun b7 b8 b9 b10 b11 b12 b13 b14 ->
                                                                    if b7
                                                                    then 
                                                                    if b8
                                                                    then None
                                                                    else 
                                                                    if b9
                                                                    then None
                                                                    else 
                                                                    if b10
                                                                    then None
                                                                    else 
                                                                    if b11
                                                                    then None
                                                                    else 
                                                                    if b12
                                                                    then 
                                                                    if b13
                                                                    then 
                                                                    if b14
                                                                    then None
                                                                    else 
                                                                    (match s1 with
                                                                    | [] ->
                                                                    None
                                                                    | a1::s2 ->
                                                                    (* If this appears, you're using Ascii internals. Please don't *)
 (fun f c ->
  let n = Char.code c in
  let h i = (n land (1 lsl i)) <> 0 in
  f (h 0) (h 1) (h 2) (h 3) (h 4) (h 5) (h 6) (h 7))
                                                                    (fun b15 b16 b17 b18 b19 b20 b21 b22 ->
                                                                    if b15
                                                                    then None
                                                                    else 
                                                                    if b16
                                                                    then 
                                                                    if b17
                                                                    then None
                                                                    else 
                                                                    if b18
                                                                    then None
                                                                    else 
                                                                    if b19
                                                                    then 
                                                                    if b20
                                                                    then 
                                                                    if b21
                                                                    then 
                                                                    if b22
                                                                    then None
                                                                    else 
                                                                    (match s2 with
                                                                    | [] ->
                                                                    (match 
                                                                    json_field_get
                                                                    ('n'::('a'::('m'::('e'::[]))))
                                                                    arrv with
                                                                    | Some namev ->
                                                                    (match 
                                                                    json_to_string
                                                                    namev with
                                                                    | Some nm ->
                                                                    (match 
                                                                    ir_to_contract_expr
                                                                    n idxv with
                                                                    | Some ie ->
                                                                    Some
                                                                    (CSubscript
                                                                    (nm, ie))
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | _::_ ->
                                                                    None)
                                                                    else None
                                                                    else None
                                                                    else None
                                                                    else None)
                                                                    a1)
                                                                    else None
                                                                    else None
                                                                    else None)
                                                                    a0)
                                                                    else None
                                                                    else None
                                                               else None
                                                          else None)
                                                     a)
                                              | None -> None)
                                           | None -> None)
                                        | None -> None)
                                     | None -> None)
                               else if eqb t ('O'::('l'::('d'::[])))
                                    then (match json_field_get
                                                  ('o'::('p'::('e'::('r'::('a'::('n'::('d'::[])))))))
                                                  e with
                                          | Some v ->
                                            (match ir_to_contract_expr n v with
                                             | Some ce -> Some (COld ce)
                                             | None -> None)
                                          | None -> None)
                                    else if eqb t
                                              ('U'::('n'::('a'::('r'::('y'::('O'::('p'::[])))))))
                                         then let operand_opt =
                                                match json_field_get
                                                        ('o'::('p'::('e'::('r'::('a'::('n'::('d'::[])))))))
                                                        e with
                                                | Some v -> Some v
                                                | None ->
                                                  json_field_get
                                                    ('e'::('x'::('p'::('r'::[]))))
                                                    e
                                              in
                                              (match json_field_get
                                                       ('o'::('p'::[])) e with
                                               | Some opv ->
                                                 (match operand_opt with
                                                  | Some operand ->
                                                    (match json_to_string opv with
                                                     | Some s ->
                                                       (match s with
                                                        | [] -> None
                                                        | a::s0 ->
                                                          (* If this appears, you're using Ascii internals. Please don't *)
 (fun f c ->
  let n = Char.code c in
  let h i = (n land (1 lsl i)) <> 0 in
  f (h 0) (h 1) (h 2) (h 3) (h 4) (h 5) (h 6) (h 7))
                                                            (fun b b0 b1 b2 b3 b4 b5 b6 ->
                                                            if b
                                                            then if b0
                                                                 then 
                                                                   if b1
                                                                   then None
                                                                   else 
                                                                    if b2
                                                                    then 
                                                                    if b3
                                                                    then None
                                                                    else 
                                                                    if b4
                                                                    then 
                                                                    if b5
                                                                    then None
                                                                    else 
                                                                    if b6
                                                                    then None
                                                                    else 
                                                                    (match s0 with
                                                                    | [] ->
                                                                    ir_to_contract_expr
                                                                    n operand
                                                                    | _::_ ->
                                                                    None)
                                                                    else None
                                                                    else None
                                                                 else 
                                                                   if b1
                                                                   then 
                                                                    if b2
                                                                    then 
                                                                    if b3
                                                                    then None
                                                                    else 
                                                                    if b4
                                                                    then 
                                                                    if b5
                                                                    then None
                                                                    else 
                                                                    if b6
                                                                    then None
                                                                    else 
                                                                    (match s0 with
                                                                    | [] ->
                                                                    (match 
                                                                    ir_to_contract_expr
                                                                    n operand with
                                                                    | Some e' ->
                                                                    Some
                                                                    (CNeg e')
                                                                    | None ->
                                                                    None)
                                                                    | _::_ ->
                                                                    None)
                                                                    else None
                                                                    else None
                                                                   else None
                                                            else if b0
                                                                 then 
                                                                   if b1
                                                                   then 
                                                                    if b2
                                                                    then 
                                                                    if b3
                                                                    then None
                                                                    else 
                                                                    if b4
                                                                    then 
                                                                    if b5
                                                                    then 
                                                                    if b6
                                                                    then None
                                                                    else 
                                                                    (match s0 with
                                                                    | [] ->
                                                                    None
                                                                    | a0::s1 ->
                                                                    (* If this appears, you're using Ascii internals. Please don't *)
 (fun f c ->
  let n = Char.code c in
  let h i = (n land (1 lsl i)) <> 0 in
  f (h 0) (h 1) (h 2) (h 3) (h 4) (h 5) (h 6) (h 7))
                                                                    (fun b7 b8 b9 b10 b11 b12 b13 b14 ->
                                                                    if b7
                                                                    then 
                                                                    if b8
                                                                    then 
                                                                    if b9
                                                                    then 
                                                                    if b10
                                                                    then 
                                                                    if b11
                                                                    then None
                                                                    else 
                                                                    if b12
                                                                    then 
                                                                    if b13
                                                                    then 
                                                                    if b14
                                                                    then None
                                                                    else 
                                                                    (match s1 with
                                                                    | [] ->
                                                                    None
                                                                    | a1::s2 ->
                                                                    (* If this appears, you're using Ascii internals. Please don't *)
 (fun f c ->
  let n = Char.code c in
  let h i = (n land (1 lsl i)) <> 0 in
  f (h 0) (h 1) (h 2) (h 3) (h 4) (h 5) (h 6) (h 7))
                                                                    (fun b15 b16 b17 b18 b19 b20 b21 b22 ->
                                                                    if b15
                                                                    then None
                                                                    else 
                                                                    if b16
                                                                    then None
                                                                    else 
                                                                    if b17
                                                                    then 
                                                                    if b18
                                                                    then None
                                                                    else 
                                                                    if b19
                                                                    then 
                                                                    if b20
                                                                    then 
                                                                    if b21
                                                                    then 
                                                                    if b22
                                                                    then None
                                                                    else 
                                                                    (match s2 with
                                                                    | [] ->
                                                                    (match 
                                                                    ir_to_contract_expr
                                                                    n operand with
                                                                    | Some e' ->
                                                                    Some
                                                                    (CNot e')
                                                                    | None ->
                                                                    None)
                                                                    | _::_ ->
                                                                    None)
                                                                    else None
                                                                    else None
                                                                    else None
                                                                    else None)
                                                                    a1)
                                                                    else None
                                                                    else None
                                                                    else None
                                                                    else None
                                                                    else None
                                                                    else None)
                                                                    a0)
                                                                    else None
                                                                    else None
                                                                    else None
                                                                   else None
                                                                 else None)
                                                            a)
                                                     | None -> None)
                                                  | None -> None)
                                               | None -> None)
                                         else if eqb t
                                                   ('B'::('i'::('n'::('O'::('p'::[])))))
                                              then (match json_field_get
                                                            ('o'::('p'::[])) e with
                                                    | Some opv ->
                                                      (match json_field_get
                                                               ('l'::('e'::('f'::('t'::[]))))
                                                               e with
                                                       | Some lv ->
                                                         (match json_field_get
                                                                  ('r'::('i'::('g'::('h'::('t'::[])))))
                                                                  e with
                                                          | Some rv ->
                                                            (match json_to_string
                                                                    opv with
                                                             | Some opstr ->
                                                               (match 
                                                                ir_to_contract_expr
                                                                  n lv with
                                                                | Some le ->
                                                                  (match 
                                                                   ir_to_contract_expr
                                                                    n rv with
                                                                   | Some re ->
                                                                    (match 
                                                                    string_to_binop
                                                                    opstr with
                                                                    | Some op ->
                                                                    Some
                                                                    (CBinOp
                                                                    (op, le,
                                                                    re))
                                                                    | None ->
                                                                    if 
                                                                    eqb opstr
                                                                    ('='::('='::[]))
                                                                    then 
                                                                    Some (CEq
                                                                    (le, re))
                                                                    else 
                                                                    if 
                                                                    eqb opstr
                                                                    ('!'::('='::[]))
                                                                    then 
                                                                    Some (CNe
                                                                    (le, re))
                                                                    else 
                                                                    if 
                                                                    eqb opstr
                                                                    ('<'::[])
                                                                    then 
                                                                    Some (CLt
                                                                    (le, re))
                                                                    else 
                                                                    if 
                                                                    eqb opstr
                                                                    ('<'::('='::[]))
                                                                    then 
                                                                    Some (CLe
                                                                    (le, re))
                                                                    else 
                                                                    if 
                                                                    eqb opstr
                                                                    ('>'::[])
                                                                    then 
                                                                    Some (CGt
                                                                    (le, re))
                                                                    else 
                                                                    if 
                                                                    eqb opstr
                                                                    ('>'::('='::[]))
                                                                    then 
                                                                    Some (CGe
                                                                    (le, re))
                                                                    else 
                                                                    if 
                                                                    eqb opstr
                                                                    ('a'::('n'::('d'::[])))
                                                                    then 
                                                                    Some
                                                                    (CAnd
                                                                    (le, re))
                                                                    else 
                                                                    if 
                                                                    eqb opstr
                                                                    ('o'::('r'::[]))
                                                                    then 
                                                                    Some (COr
                                                                    (le, re))
                                                                    else 
                                                                    if 
                                                                    eqb opstr
                                                                    ('i'::('m'::('p'::('l'::('i'::('e'::('s'::[])))))))
                                                                    then 
                                                                    Some
                                                                    (CImplies
                                                                    (le, re))
                                                                    else 
                                                                    if 
                                                                    eqb opstr
                                                                    ('i'::('f'::('f'::[])))
                                                                    then 
                                                                    Some
                                                                    (CIff
                                                                    (le, re))
                                                                    else None)
                                                                   | None ->
                                                                    None)
                                                                | None -> None)
                                                             | None -> None)
                                                          | None -> None)
                                                       | None -> None)
                                                    | None -> None)
                                              else if eqb t
                                                        ('S'::('t'::('r'::('i'::('n'::('g'::[]))))))
                                                   then (match json_field_get
                                                                 ('v'::('a'::('l'::('u'::('e'::[])))))
                                                                 e with
                                                         | Some v ->
                                                           (match json_to_string
                                                                    v with
                                                            | Some s ->
                                                              Some
                                                                (CStringLit s)
                                                            | None -> None)
                                                         | None -> None)
                                                   else if eqb t
                                                             ('F'::('o'::('r'::('a'::('l'::('l'::[]))))))
                                                        then (match json_field_get
                                                                    ('v'::('a'::('r'::[])))
                                                                    e with
                                                              | Some xv ->
                                                                (match 
                                                                 json_field_get
                                                                   ('b'::('o'::('d'::('y'::[]))))
                                                                   e with
                                                                 | Some bodyv ->
                                                                   (match 
                                                                    json_to_string
                                                                    xv with
                                                                    | Some x ->
                                                                    (match 
                                                                    ir_to_contract_expr
                                                                    n bodyv with
                                                                    | Some b ->
                                                                    Some
                                                                    (CForall
                                                                    (x, b))
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                 | None ->
                                                                   None)
                                                              | None -> None)
                                                        else if eqb t
                                                                  ('E'::('x'::('i'::('s'::('t'::('s'::[]))))))
                                                             then (match 
                                                                   json_field_get
                                                                    ('v'::('a'::('r'::[])))
                                                                    e with
                                                                   | Some xv ->
                                                                    (match 
                                                                    json_field_get
                                                                    ('b'::('o'::('d'::('y'::[]))))
                                                                    e with
                                                                    | Some bodyv ->
                                                                    (match 
                                                                    json_to_string
                                                                    xv with
                                                                    | Some x ->
                                                                    (match 
                                                                    ir_to_contract_expr
                                                                    n bodyv with
                                                                    | Some b ->
                                                                    Some
                                                                    (CExists
                                                                    (x, b))
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                   | None ->
                                                                    None)
                                                             else if 
                                                                    eqb t
                                                                    ('C'::('h'::('a'::('i'::('n'::('e'::('d'::('S'::('u'::('b'::('s'::('c'::('r'::('i'::('p'::('t'::[]))))))))))))))))
                                                                  then 
                                                                    (match 
                                                                    json_field_get
                                                                    ('a'::('r'::('r'::[])))
                                                                    e with
                                                                    | Some arrv ->
                                                                    (match 
                                                                    json_field_get
                                                                    ('i'::('n'::('d'::('e'::('x'::('1'::[]))))))
                                                                    e with
                                                                    | Some i1v ->
                                                                    (match 
                                                                    json_field_get
                                                                    ('i'::('n'::('d'::('e'::('x'::('2'::[]))))))
                                                                    e with
                                                                    | Some i2v ->
                                                                    (match 
                                                                    json_to_string
                                                                    arrv with
                                                                    | Some arr ->
                                                                    (match 
                                                                    ir_to_contract_expr
                                                                    n i1v with
                                                                    | Some i1 ->
                                                                    (match 
                                                                    ir_to_contract_expr
                                                                    n i2v with
                                                                    | Some i2 ->
                                                                    Some
                                                                    (CChainedSubscript
                                                                    (arr, i1,
                                                                    i2))
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                  else 
                                                                    if 
                                                                    eqb t
                                                                    ('A'::('t'::[]))
                                                                    then 
                                                                    (match 
                                                                    json_field_get
                                                                    ('e'::('x'::('p'::('r'::[]))))
                                                                    e with
                                                                    | Some expv ->
                                                                    (match 
                                                                    json_field_get
                                                                    ('l'::('a'::('b'::('e'::('l'::[])))))
                                                                    e with
                                                                    | Some lblv ->
                                                                    (match 
                                                                    ir_to_contract_expr
                                                                    n expv with
                                                                    | Some ce ->
                                                                    (match 
                                                                    json_to_string
                                                                    lblv with
                                                                    | Some lbl ->
                                                                    Some (CAt
                                                                    (ce, lbl))
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    else 
                                                                    if 
                                                                    eqb t
                                                                    ('M'::('a'::('p'::('E'::('m'::('p'::('t'::('y'::[]))))))))
                                                                    then 
                                                                    Some
                                                                    CGMapEmpty
                                                                    else 
                                                                    if 
                                                                    eqb t
                                                                    ('G'::('h'::('o'::('s'::('t'::('M'::('a'::('p'::('E'::('m'::('p'::('t'::('y'::[])))))))))))))
                                                                    then 
                                                                    Some
                                                                    CGMapEmpty
                                                                    else 
                                                                    if 
                                                                    eqb t
                                                                    ('M'::('a'::('p'::('G'::('e'::('t'::[]))))))
                                                                    then 
                                                                    let map_opt =
                                                                    match 
                                                                    json_field_get
                                                                    ('m'::('a'::('p'::[])))
                                                                    e with
                                                                    | Some v ->
                                                                    Some v
                                                                    | None ->
                                                                    json_field_get
                                                                    ('d'::('i'::('c'::('t'::[]))))
                                                                    e
                                                                    in
                                                                    (
                                                                    match map_opt with
                                                                    | Some mv ->
                                                                    (match 
                                                                    json_field_get
                                                                    ('k'::('e'::('y'::[])))
                                                                    e with
                                                                    | Some kv ->
                                                                    (match 
                                                                    ir_to_contract_expr
                                                                    n mv with
                                                                    | Some m ->
                                                                    (match 
                                                                    ir_to_contract_expr
                                                                    n kv with
                                                                    | Some k ->
                                                                    Some
                                                                    (CGMapGet
                                                                    (m, k))
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    else 
                                                                    if 
                                                                    eqb t
                                                                    ('M'::('a'::('p'::('S'::('e'::('t'::[]))))))
                                                                    then 
                                                                    let map_opt =
                                                                    match 
                                                                    json_field_get
                                                                    ('m'::('a'::('p'::[])))
                                                                    e with
                                                                    | Some v ->
                                                                    Some v
                                                                    | None ->
                                                                    json_field_get
                                                                    ('d'::('i'::('c'::('t'::[]))))
                                                                    e
                                                                    in
                                                                    (
                                                                    match map_opt with
                                                                    | Some mv ->
                                                                    (match 
                                                                    json_field_get
                                                                    ('k'::('e'::('y'::[])))
                                                                    e with
                                                                    | Some kv ->
                                                                    (match 
                                                                    json_field_get
                                                                    ('v'::('a'::('l'::('u'::('e'::[])))))
                                                                    e with
                                                                    | Some vv ->
                                                                    (match 
                                                                    ir_to_contract_expr
                                                                    n mv with
                                                                    | Some m ->
                                                                    (match 
                                                                    ir_to_contract_expr
                                                                    n kv with
                                                                    | Some k ->
                                                                    (match 
                                                                    ir_to_contract_expr
                                                                    n vv with
                                                                    | Some v ->
                                                                    Some
                                                                    (CGMapSet
                                                                    (m, k, v))
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    else 
                                                                    if 
                                                                    eqb t
                                                                    ('H'::('a'::('s'::('K'::('e'::('y'::[]))))))
                                                                    then 
                                                                    let map_opt =
                                                                    match 
                                                                    json_field_get
                                                                    ('m'::('a'::('p'::[])))
                                                                    e with
                                                                    | Some v ->
                                                                    Some v
                                                                    | None ->
                                                                    json_field_get
                                                                    ('d'::('i'::('c'::('t'::[]))))
                                                                    e
                                                                    in
                                                                    (
                                                                    match map_opt with
                                                                    | Some mv ->
                                                                    (match 
                                                                    json_field_get
                                                                    ('k'::('e'::('y'::[])))
                                                                    e with
                                                                    | Some kv ->
                                                                    (match 
                                                                    ir_to_contract_expr
                                                                    n mv with
                                                                    | Some m ->
                                                                    (match 
                                                                    ir_to_contract_expr
                                                                    n kv with
                                                                    | Some k ->
                                                                    Some
                                                                    (CGHasKey
                                                                    (m, k))
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    else 
                                                                    if 
                                                                    eqb t
                                                                    ('N'::('i'::('l'::[])))
                                                                    then 
                                                                    Some CGNil
                                                                    else 
                                                                    if 
                                                                    eqb t
                                                                    ('G'::('h'::('o'::('s'::('t'::('N'::('i'::('l'::[]))))))))
                                                                    then 
                                                                    Some CGNil
                                                                    else 
                                                                    if 
                                                                    (||)
                                                                    (eqb t
                                                                    ('G'::('h'::('o'::('s'::('t'::('C'::('o'::('n'::('s'::[]))))))))))
                                                                    (eqb t
                                                                    ('C'::('o'::('n'::('s'::[])))))
                                                                    then 
                                                                    (match 
                                                                    json_field_get
                                                                    ('h'::('e'::('a'::('d'::[]))))
                                                                    e with
                                                                    | Some hv ->
                                                                    (match 
                                                                    json_field_get
                                                                    ('t'::('a'::('i'::('l'::[]))))
                                                                    e with
                                                                    | Some tv ->
                                                                    (match 
                                                                    ir_to_contract_expr
                                                                    n hv with
                                                                    | Some h ->
                                                                    (match 
                                                                    ir_to_contract_expr
                                                                    n tv with
                                                                    | Some t0 ->
                                                                    Some
                                                                    (CGCons
                                                                    (h, t0))
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    else 
                                                                    if 
                                                                    eqb t
                                                                    ('G'::('h'::('o'::('s'::('t'::('L'::('i'::('s'::('t'::('L'::('e'::('n'::[]))))))))))))
                                                                    then 
                                                                    (match 
                                                                    json_field_get
                                                                    ('l'::('i'::('s'::('t'::[]))))
                                                                    e with
                                                                    | Some lv ->
                                                                    (match 
                                                                    ir_to_contract_expr
                                                                    n lv with
                                                                    | Some l ->
                                                                    Some
                                                                    (CGListLen
                                                                    l)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    else 
                                                                    if 
                                                                    eqb t
                                                                    ('S'::('e'::('t'::('E'::('m'::('p'::('t'::('y'::[]))))))))
                                                                    then 
                                                                    Some
                                                                    CGSetEmpty
                                                                    else 
                                                                    if 
                                                                    eqb t
                                                                    ('G'::('h'::('o'::('s'::('t'::('S'::('e'::('t'::('E'::('m'::('p'::('t'::('y'::[])))))))))))))
                                                                    then 
                                                                    Some
                                                                    CGSetEmpty
                                                                    else 
                                                                    if 
                                                                    (||)
                                                                    (eqb t
                                                                    ('G'::('h'::('o'::('s'::('t'::('S'::('e'::('t'::('A'::('d'::('d'::[]))))))))))))
                                                                    (eqb t
                                                                    ('S'::('e'::('t'::('A'::('d'::('d'::[])))))))
                                                                    then 
                                                                    (match 
                                                                    json_field_get
                                                                    ('e'::('l'::('e'::('m'::[]))))
                                                                    e with
                                                                    | Some ev ->
                                                                    (match 
                                                                    json_field_get
                                                                    ('s'::('e'::('t'::[])))
                                                                    e with
                                                                    | Some sv ->
                                                                    (match 
                                                                    ir_to_contract_expr
                                                                    n ev with
                                                                    | Some el ->
                                                                    (match 
                                                                    ir_to_contract_expr
                                                                    n sv with
                                                                    | Some s ->
                                                                    Some
                                                                    (CGSetAdd
                                                                    (el, s))
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    else 
                                                                    if 
                                                                    (||)
                                                                    (eqb t
                                                                    ('G'::('h'::('o'::('s'::('t'::('S'::('e'::('t'::('M'::('e'::('m'::[]))))))))))))
                                                                    (eqb t
                                                                    ('S'::('e'::('t'::('M'::('e'::('m'::[])))))))
                                                                    then 
                                                                    (match 
                                                                    json_field_get
                                                                    ('e'::('l'::('e'::('m'::[]))))
                                                                    e with
                                                                    | Some ev ->
                                                                    (match 
                                                                    json_field_get
                                                                    ('s'::('e'::('t'::[])))
                                                                    e with
                                                                    | Some sv ->
                                                                    (match 
                                                                    ir_to_contract_expr
                                                                    n ev with
                                                                    | Some el ->
                                                                    (match 
                                                                    ir_to_contract_expr
                                                                    n sv with
                                                                    | Some s ->
                                                                    Some
                                                                    (CGSetMem
                                                                    (el, s))
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    else 
                                                                    if 
                                                                    (||)
                                                                    (eqb t
                                                                    ('G'::('h'::('o'::('s'::('t'::('S'::('e'::('t'::('C'::('a'::('r'::('d'::[])))))))))))))
                                                                    (eqb t
                                                                    ('S'::('e'::('t'::('C'::('a'::('r'::('d'::[]))))))))
                                                                    then 
                                                                    (match 
                                                                    json_field_get
                                                                    ('s'::('e'::('t'::[])))
                                                                    e with
                                                                    | Some sv ->
                                                                    (match 
                                                                    ir_to_contract_expr
                                                                    n sv with
                                                                    | Some s ->
                                                                    Some
                                                                    (CGSetCard
                                                                    s)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    else 
                                                                    if 
                                                                    eqb t
                                                                    ('M'::('k'::('T'::('u'::('p'::('l'::('e'::[])))))))
                                                                    then 
                                                                    (match 
                                                                    json_field_get
                                                                    ('e'::('l'::('t'::('s'::[]))))
                                                                    e with
                                                                    | Some eltsv ->
                                                                    (match 
                                                                    json_to_list
                                                                    eltsv with
                                                                    | Some l ->
                                                                    (match l with
                                                                    | [] ->
                                                                    None
                                                                    | a::l0 ->
                                                                    (match l0 with
                                                                    | [] ->
                                                                    None
                                                                    | b::l1 ->
                                                                    (match l1 with
                                                                    | [] ->
                                                                    (match 
                                                                    ir_to_contract_expr
                                                                    n a with
                                                                    | Some ca ->
                                                                    (match 
                                                                    ir_to_contract_expr
                                                                    n b with
                                                                    | Some cb ->
                                                                    Some
                                                                    (CGMkTuple2
                                                                    (ca, cb))
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | c::l2 ->
                                                                    (match l2 with
                                                                    | [] ->
                                                                    (match 
                                                                    ir_to_contract_expr
                                                                    n a with
                                                                    | Some ca ->
                                                                    (match 
                                                                    ir_to_contract_expr
                                                                    n b with
                                                                    | Some cb ->
                                                                    (match 
                                                                    ir_to_contract_expr
                                                                    n c with
                                                                    | Some cc ->
                                                                    Some
                                                                    (CGMkTuple3
                                                                    (ca, cb,
                                                                    cc))
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | d::l3 ->
                                                                    (match l3 with
                                                                    | [] ->
                                                                    (match 
                                                                    ir_to_contract_expr
                                                                    n a with
                                                                    | Some ca ->
                                                                    (match 
                                                                    ir_to_contract_expr
                                                                    n b with
                                                                    | Some cb ->
                                                                    (match 
                                                                    ir_to_contract_expr
                                                                    n c with
                                                                    | Some cc ->
                                                                    (match 
                                                                    ir_to_contract_expr
                                                                    n d with
                                                                    | Some cd ->
                                                                    Some
                                                                    (CGMkTuple4
                                                                    (ca, cb,
                                                                    cc, cd))
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | _::_ ->
                                                                    None)))))
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    else 
                                                                    if 
                                                                    eqb t
                                                                    ('F'::('s'::('t'::('E'::('x'::('p'::('r'::[])))))))
                                                                    then 
                                                                    (match 
                                                                    json_field_get
                                                                    ('t'::('u'::('p'::('l'::('e'::[])))))
                                                                    e with
                                                                    | Some tv ->
                                                                    (match 
                                                                    ir_to_contract_expr
                                                                    n tv with
                                                                    | Some t0 ->
                                                                    Some
                                                                    (CGFst t0)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    else 
                                                                    if 
                                                                    eqb t
                                                                    ('S'::('n'::('d'::('E'::('x'::('p'::('r'::[])))))))
                                                                    then 
                                                                    (match 
                                                                    json_field_get
                                                                    ('t'::('u'::('p'::('l'::('e'::[])))))
                                                                    e with
                                                                    | Some tv ->
                                                                    (match 
                                                                    ir_to_contract_expr
                                                                    n tv with
                                                                    | Some t0 ->
                                                                    Some
                                                                    (CGSnd t0)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    else 
                                                                    if 
                                                                    eqb t
                                                                    ('P'::('r'::('o'::('j'::('E'::('x'::('p'::('r'::[]))))))))
                                                                    then 
                                                                    (match 
                                                                    json_field_get
                                                                    ('t'::('u'::('p'::('l'::('e'::[])))))
                                                                    e with
                                                                    | Some tv ->
                                                                    (match 
                                                                    json_field_get
                                                                    ('i'::('n'::('d'::('e'::('x'::[])))))
                                                                    e with
                                                                    | Some idxv ->
                                                                    (match 
                                                                    ir_to_contract_expr
                                                                    n tv with
                                                                    | Some te ->
                                                                    (match 
                                                                    json_to_z
                                                                    idxv with
                                                                    | Some z0 ->
                                                                    ((fun f0 fp fn z -> if z=0 then f0 () else if z>0 then fp z else fn (-z))
                                                                    (fun _ ->
                                                                    Some
                                                                    (CGFst
                                                                    te))
                                                                    (fun p ->
                                                                    (fun f2p1 f2p f1 p ->
  if p<=1 then f1 () else if p mod 2 = 0 then f2p (p/2) else f2p1 (p/2))
                                                                    (fun p0 ->
                                                                    (fun f2p1 f2p f1 p ->
  if p<=1 then f1 () else if p mod 2 = 0 then f2p (p/2) else f2p1 (p/2))
                                                                    (fun _ ->
                                                                    None)
                                                                    (fun _ ->
                                                                    None)
                                                                    (fun _ ->
                                                                    Some
                                                                    (CGFth
                                                                    te))
                                                                    p0)
                                                                    (fun p0 ->
                                                                    (fun f2p1 f2p f1 p ->
  if p<=1 then f1 () else if p mod 2 = 0 then f2p (p/2) else f2p1 (p/2))
                                                                    (fun _ ->
                                                                    None)
                                                                    (fun _ ->
                                                                    None)
                                                                    (fun _ ->
                                                                    Some
                                                                    (CGTrd
                                                                    te))
                                                                    p0)
                                                                    (fun _ ->
                                                                    Some
                                                                    (CGSnd
                                                                    te))
                                                                    p)
                                                                    (fun _ ->
                                                                    None)
                                                                    z0)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    else 
                                                                    if 
                                                                    eqb t
                                                                    ('I'::('s'::('S'::('o'::('r'::('t'::('e'::('d'::[]))))))))
                                                                    then 
                                                                    (match 
                                                                    json_field_get
                                                                    ('a'::('r'::('r'::[])))
                                                                    e with
                                                                    | Some av ->
                                                                    (match 
                                                                    json_field_get
                                                                    ('l'::('o'::[]))
                                                                    e with
                                                                    | Some lov ->
                                                                    (match 
                                                                    json_field_get
                                                                    ('h'::('i'::[]))
                                                                    e with
                                                                    | Some hiv ->
                                                                    (match 
                                                                    json_to_string
                                                                    av with
                                                                    | Some arr ->
                                                                    (match 
                                                                    ir_to_contract_expr
                                                                    n lov with
                                                                    | Some lo ->
                                                                    (match 
                                                                    ir_to_contract_expr
                                                                    n hiv with
                                                                    | Some hi ->
                                                                    Some
                                                                    (CIsSorted
                                                                    (arr, lo,
                                                                    hi))
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    else 
                                                                    if 
                                                                    eqb t
                                                                    ('S'::('u'::('m'::[])))
                                                                    then 
                                                                    (match 
                                                                    json_field_get
                                                                    ('a'::('r'::('r'::[])))
                                                                    e with
                                                                    | Some av ->
                                                                    (match 
                                                                    json_field_get
                                                                    ('l'::('o'::[]))
                                                                    e with
                                                                    | Some lov ->
                                                                    (match 
                                                                    json_field_get
                                                                    ('h'::('i'::[]))
                                                                    e with
                                                                    | Some hiv ->
                                                                    (match 
                                                                    json_to_string
                                                                    av with
                                                                    | Some arr ->
                                                                    (match 
                                                                    ir_to_contract_expr
                                                                    n lov with
                                                                    | Some lo ->
                                                                    (match 
                                                                    ir_to_contract_expr
                                                                    n hiv with
                                                                    | Some hi ->
                                                                    Some
                                                                    (CSum
                                                                    (arr, lo,
                                                                    hi))
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    else 
                                                                    if 
                                                                    eqb t
                                                                    ('S'::('l'::('i'::('c'::('e'::[])))))
                                                                    then 
                                                                    (match 
                                                                    json_field_get
                                                                    ('a'::('r'::('r'::[])))
                                                                    e with
                                                                    | Some av ->
                                                                    (match 
                                                                    json_field_get
                                                                    ('l'::('o'::[]))
                                                                    e with
                                                                    | Some lov ->
                                                                    (match 
                                                                    json_field_get
                                                                    ('h'::('i'::[]))
                                                                    e with
                                                                    | Some hiv ->
                                                                    (match 
                                                                    json_to_string
                                                                    av with
                                                                    | Some arr ->
                                                                    (match 
                                                                    ir_to_contract_expr
                                                                    n lov with
                                                                    | Some lo ->
                                                                    (match 
                                                                    ir_to_contract_expr
                                                                    n hiv with
                                                                    | Some hi ->
                                                                    Some
                                                                    (CSlice
                                                                    (arr, lo,
                                                                    hi))
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    else 
                                                                    if 
                                                                    eqb t
                                                                    ('I'::('n'::[]))
                                                                    then 
                                                                    (match 
                                                                    json_field_get
                                                                    ('e'::('l'::('e'::('m'::[]))))
                                                                    e with
                                                                    | Some ev ->
                                                                    (match 
                                                                    json_field_get
                                                                    ('c'::('o'::('n'::('t'::('a'::('i'::('n'::('e'::('r'::[])))))))))
                                                                    e with
                                                                    | Some cv ->
                                                                    (match 
                                                                    ir_to_contract_expr
                                                                    n ev with
                                                                    | Some el ->
                                                                    (match 
                                                                    ir_to_contract_expr
                                                                    n cv with
                                                                    | Some c ->
                                                                    Some (CIn
                                                                    (el, c))
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    else 
                                                                    if 
                                                                    eqb t
                                                                    ('N'::('o'::('t'::('I'::('n'::[])))))
                                                                    then 
                                                                    (match 
                                                                    json_field_get
                                                                    ('e'::('l'::('e'::('m'::[]))))
                                                                    e with
                                                                    | Some ev ->
                                                                    (match 
                                                                    json_field_get
                                                                    ('c'::('o'::('n'::('t'::('a'::('i'::('n'::('e'::('r'::[])))))))))
                                                                    e with
                                                                    | Some cv ->
                                                                    (match 
                                                                    ir_to_contract_expr
                                                                    n ev with
                                                                    | Some el ->
                                                                    (match 
                                                                    ir_to_contract_expr
                                                                    n cv with
                                                                    | Some c ->
                                                                    Some
                                                                    (CNotIn
                                                                    (el, c))
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    else 
                                                                    if 
                                                                    eqb t
                                                                    ('S'::('t'::('r'::('C'::('o'::('n'::('c'::('a'::('t'::[])))))))))
                                                                    then 
                                                                    (match 
                                                                    json_field_get
                                                                    ('l'::('e'::('f'::('t'::[]))))
                                                                    e with
                                                                    | Some lv ->
                                                                    (match 
                                                                    json_field_get
                                                                    ('r'::('i'::('g'::('h'::('t'::[])))))
                                                                    e with
                                                                    | Some rv ->
                                                                    (match 
                                                                    ir_to_contract_expr
                                                                    n lv with
                                                                    | Some l ->
                                                                    (match 
                                                                    ir_to_contract_expr
                                                                    n rv with
                                                                    | Some r ->
                                                                    Some
                                                                    (CGStrConcat
                                                                    (l, r))
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    else 
                                                                    if 
                                                                    eqb t
                                                                    ('S'::('t'::('r'::('L'::('e'::('n'::('g'::('t'::('h'::[])))))))))
                                                                    then 
                                                                    (match 
                                                                    json_field_get
                                                                    ('s'::('t'::('r'::('i'::('n'::('g'::[]))))))
                                                                    e with
                                                                    | Some sv ->
                                                                    (match 
                                                                    ir_to_contract_expr
                                                                    n sv with
                                                                    | Some s ->
                                                                    Some
                                                                    (CGStrLen
                                                                    s)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    else 
                                                                    if 
                                                                    eqb t
                                                                    ('G'::('h'::('o'::('s'::('t'::('C'::('o'::('p'::('y'::[])))))))))
                                                                    then 
                                                                    (match 
                                                                    json_field_get
                                                                    ('a'::('r'::('r'::[])))
                                                                    e with
                                                                    | Some av ->
                                                                    (match 
                                                                    json_to_string
                                                                    av with
                                                                    | Some arr ->
                                                                    Some
                                                                    (CGCopy
                                                                    arr)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    else 
                                                                    if 
                                                                    eqb t
                                                                    ('G'::('h'::('o'::('s'::('t'::('M'::('a'::('k'::('e'::[])))))))))
                                                                    then 
                                                                    (match 
                                                                    json_field_get
                                                                    ('s'::('i'::('z'::('e'::[]))))
                                                                    e with
                                                                    | Some sv ->
                                                                    (match 
                                                                    json_field_get
                                                                    ('d'::('e'::('f'::('a'::('u'::('l'::('t'::[])))))))
                                                                    e with
                                                                    | Some dv ->
                                                                    (match 
                                                                    ir_to_contract_expr
                                                                    n sv with
                                                                    | Some s ->
                                                                    (match 
                                                                    ir_to_contract_expr
                                                                    n dv with
                                                                    | Some d ->
                                                                    Some
                                                                    (CGMake
                                                                    (s, d))
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    else 
                                                                    if 
                                                                    eqb t
                                                                    ('G'::('h'::('o'::('s'::('t'::('C'::('o'::('p'::('y'::('R'::('a'::('n'::('g'::('e'::[]))))))))))))))
                                                                    then 
                                                                    (match 
                                                                    json_field_get
                                                                    ('a'::('r'::('r'::[])))
                                                                    e with
                                                                    | Some av ->
                                                                    (match 
                                                                    json_field_get
                                                                    ('l'::('o'::[]))
                                                                    e with
                                                                    | Some lov ->
                                                                    (match 
                                                                    json_field_get
                                                                    ('h'::('i'::[]))
                                                                    e with
                                                                    | Some hiv ->
                                                                    (match 
                                                                    json_to_string
                                                                    av with
                                                                    | Some arr ->
                                                                    (match 
                                                                    ir_to_contract_expr
                                                                    n lov with
                                                                    | Some lo ->
                                                                    (match 
                                                                    ir_to_contract_expr
                                                                    n hiv with
                                                                    | Some hi ->
                                                                    Some
                                                                    (CGCopyRange
                                                                    (arr, lo,
                                                                    hi))
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    else None
    in
    (match json_field_get ('t'::('y'::('p'::('e'::[])))) e with
     | Some tv ->
       (match json_to_string tv with
        | Some t -> dispatch t
        | None -> None)
     | None -> None))
    fuel

(** val default_contract_fuel : int **)

let default_contract_fuel =
  Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    0)))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))

(** val ir_to_stmt_n : int -> json_value -> stmt option **)

let rec ir_to_stmt_n fuel j =
  (fun fO fS n -> if n=0 then fO () else fS (n-1))
    (fun _ -> None)
    (fun n ->
    match j with
    | JsonList ss ->
      let rec fold_seq = function
      | [] -> Some SSkip
      | s::rest ->
        (match rest with
         | [] -> ir_to_stmt_n n s
         | _::_ ->
           (match ir_to_stmt_n n s with
            | Some sh ->
              (match fold_seq rest with
               | Some st -> Some (SSeq (sh, st))
               | None -> None)
            | None -> None))
      in fold_seq ss
    | _ ->
      (match json_field_get ('s'::('t'::('m'::('t'::[])))) j with
       | Some tv ->
         (match json_to_string tv with
          | Some t ->
            if eqb t ('P'::('a'::('s'::('s'::[]))))
            then Some SSkip
            else if eqb t ('E'::('x'::('p'::('r'::[]))))
                 then Some SSkip
                 else if eqb t ('B'::('r'::('e'::('a'::('k'::[])))))
                      then Some SBreak
                      else if eqb t
                                ('C'::('o'::('n'::('t'::('i'::('n'::('u'::('e'::[]))))))))
                           then Some SContinue
                           else if eqb t
                                     ('A'::('s'::('s'::('i'::('g'::('n'::[]))))))
                                then (match json_field_get
                                              ('t'::('a'::('r'::('g'::('e'::('t'::[]))))))
                                              j with
                                      | Some tgt ->
                                        (match json_field_get
                                                 ('v'::('a'::('l'::('u'::('e'::[])))))
                                                 j with
                                         | Some valv ->
                                           (match json_to_string tgt with
                                            | Some name ->
                                              (match ir_to_expr
                                                       default_expr_fuel valv with
                                               | Some e ->
                                                 Some (SAssign (name, e))
                                               | None -> None)
                                            | None -> None)
                                         | None -> None)
                                      | None -> None)
                                else if eqb t
                                          ('A'::('u'::('g'::('A'::('s'::('s'::('i'::('g'::('n'::[])))))))))
                                     then (match json_field_get
                                                   ('t'::('a'::('r'::('g'::('e'::('t'::[]))))))
                                                   j with
                                           | Some tgt ->
                                             (match json_field_get
                                                      ('o'::('p'::[])) j with
                                              | Some opv ->
                                                (match json_field_get
                                                         ('v'::('a'::('l'::('u'::('e'::[])))))
                                                         j with
                                                 | Some valv ->
                                                   (match json_to_string tgt with
                                                    | Some name ->
                                                      (match json_to_string
                                                               opv with
                                                       | Some opstr ->
                                                         (match aug_string_to_binop
                                                                  opstr with
                                                          | Some op ->
                                                            (match ir_to_expr
                                                                    default_expr_fuel
                                                                    valv with
                                                             | Some e ->
                                                               Some
                                                                 (SAugAssign
                                                                 (name, op,
                                                                 e))
                                                             | None -> None)
                                                          | None -> None)
                                                       | None -> None)
                                                    | None -> None)
                                                 | None -> None)
                                              | None -> None)
                                           | None -> None)
                                     else if eqb t
                                               ('A'::('r'::('r'::('a'::('y'::('S'::('e'::('t'::[]))))))))
                                          then (match json_field_get
                                                        ('a'::('r'::('r'::('a'::('y'::[])))))
                                                        j with
                                                | Some arrv ->
                                                  (match json_field_get
                                                           ('i'::('n'::('d'::('e'::('x'::[])))))
                                                           j with
                                                   | Some idxv ->
                                                     (match json_field_get
                                                              ('v'::('a'::('l'::('u'::('e'::[])))))
                                                              j with
                                                      | Some valv ->
                                                        (match json_field_get
                                                                 ('t'::('y'::('p'::('e'::[]))))
                                                                 arrv with
                                                         | Some arrtype ->
                                                           (match json_to_string
                                                                    arrtype with
                                                            | Some s ->
                                                              (match s with
                                                               | [] -> None
                                                               | a::s0 ->
                                                                 (* If this appears, you're using Ascii internals. Please don't *)
 (fun f c ->
  let n = Char.code c in
  let h i = (n land (1 lsl i)) <> 0 in
  f (h 0) (h 1) (h 2) (h 3) (h 4) (h 5) (h 6) (h 7))
                                                                   (fun b b0 b1 b2 b3 b4 b5 b6 ->
                                                                   if b
                                                                   then None
                                                                   else 
                                                                    if b0
                                                                    then 
                                                                    if b1
                                                                    then 
                                                                    if b2
                                                                    then None
                                                                    else 
                                                                    if b3
                                                                    then 
                                                                    if b4
                                                                    then None
                                                                    else 
                                                                    if b5
                                                                    then 
                                                                    if b6
                                                                    then None
                                                                    else 
                                                                    (match s0 with
                                                                    | [] ->
                                                                    None
                                                                    | a0::s1 ->
                                                                    (* If this appears, you're using Ascii internals. Please don't *)
 (fun f c ->
  let n = Char.code c in
  let h i = (n land (1 lsl i)) <> 0 in
  f (h 0) (h 1) (h 2) (h 3) (h 4) (h 5) (h 6) (h 7))
                                                                    (fun b7 b8 b9 b10 b11 b12 b13 b14 ->
                                                                    if b7
                                                                    then 
                                                                    if b8
                                                                    then None
                                                                    else 
                                                                    if b9
                                                                    then None
                                                                    else 
                                                                    if b10
                                                                    then None
                                                                    else 
                                                                    if b11
                                                                    then None
                                                                    else 
                                                                    if b12
                                                                    then 
                                                                    if b13
                                                                    then 
                                                                    if b14
                                                                    then None
                                                                    else 
                                                                    (match s1 with
                                                                    | [] ->
                                                                    None
                                                                    | a1::s2 ->
                                                                    (* If this appears, you're using Ascii internals. Please don't *)
 (fun f c ->
  let n = Char.code c in
  let h i = (n land (1 lsl i)) <> 0 in
  f (h 0) (h 1) (h 2) (h 3) (h 4) (h 5) (h 6) (h 7))
                                                                    (fun b15 b16 b17 b18 b19 b20 b21 b22 ->
                                                                    if b15
                                                                    then None
                                                                    else 
                                                                    if b16
                                                                    then 
                                                                    if b17
                                                                    then None
                                                                    else 
                                                                    if b18
                                                                    then None
                                                                    else 
                                                                    if b19
                                                                    then 
                                                                    if b20
                                                                    then 
                                                                    if b21
                                                                    then 
                                                                    if b22
                                                                    then None
                                                                    else 
                                                                    (match s2 with
                                                                    | [] ->
                                                                    (match 
                                                                    json_field_get
                                                                    ('n'::('a'::('m'::('e'::[]))))
                                                                    arrv with
                                                                    | Some namev ->
                                                                    (match 
                                                                    json_to_string
                                                                    namev with
                                                                    | Some nm ->
                                                                    (match 
                                                                    ir_to_expr
                                                                    default_expr_fuel
                                                                    idxv with
                                                                    | Some ie ->
                                                                    (match 
                                                                    ir_to_expr
                                                                    default_expr_fuel
                                                                    valv with
                                                                    | Some ve ->
                                                                    Some
                                                                    (SArraySet
                                                                    (nm, ie,
                                                                    ve))
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | _::_ ->
                                                                    None)
                                                                    else None
                                                                    else None
                                                                    else None
                                                                    else None)
                                                                    a1)
                                                                    else None
                                                                    else None
                                                                    else None)
                                                                    a0)
                                                                    else None
                                                                    else None
                                                                    else None
                                                                    else None)
                                                                   a)
                                                            | None -> None)
                                                         | None -> None)
                                                      | None -> None)
                                                   | None -> None)
                                                | None -> None)
                                          else if eqb t
                                                    ('R'::('e'::('t'::('u'::('r'::('n'::[]))))))
                                               then (match json_field_get
                                                             ('v'::('a'::('l'::('u'::('e'::[])))))
                                                             j with
                                                     | Some valv ->
                                                       (match ir_to_expr
                                                                default_expr_fuel
                                                                valv with
                                                        | Some e ->
                                                          Some (SReturn e)
                                                        | None -> None)
                                                     | None -> None)
                                               else if eqb t ('I'::('f'::[]))
                                                    then (match json_field_get
                                                                  ('t'::('e'::('s'::('t'::[]))))
                                                                  j with
                                                          | Some testv ->
                                                            (match json_field_get
                                                                    ('b'::('o'::('d'::('y'::[]))))
                                                                    j with
                                                             | Some bodyv ->
                                                               (match 
                                                                json_field_get
                                                                  ('o'::('r'::('e'::('l'::('s'::('e'::[]))))))
                                                                  j with
                                                                | Some orelsev ->
                                                                  (match 
                                                                   ir_to_expr
                                                                    default_expr_fuel
                                                                    testv with
                                                                   | Some c ->
                                                                    (match 
                                                                    ir_to_stmt_n
                                                                    n bodyv with
                                                                    | Some b ->
                                                                    (match 
                                                                    ir_to_stmt_n
                                                                    n orelsev with
                                                                    | Some o ->
                                                                    Some (SIf
                                                                    (c, b, o))
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                   | None ->
                                                                    None)
                                                                | None -> None)
                                                             | None -> None)
                                                          | None -> None)
                                                    else if eqb t
                                                              ('W'::('h'::('i'::('l'::('e'::[])))))
                                                         then (match 
                                                               json_field_get
                                                                 ('t'::('e'::('s'::('t'::[]))))
                                                                 j with
                                                               | Some testv ->
                                                                 (match 
                                                                  json_field_get
                                                                    ('b'::('o'::('d'::('y'::[]))))
                                                                    j with
                                                                  | Some bodyv ->
                                                                    let inv_opt =
                                                                    match 
                                                                    json_field_get
                                                                    ('i'::('n'::('v'::('a'::('r'::('i'::('a'::('n'::('t'::('s'::[]))))))))))
                                                                    j with
                                                                    | Some inv_list_v ->
                                                                    (match 
                                                                    json_to_list
                                                                    inv_list_v with
                                                                    | Some l ->
                                                                    (match l with
                                                                    | [] ->
                                                                    Some
                                                                    (CBoolLit
                                                                    true)
                                                                    | first::_ ->
                                                                    ir_to_contract_expr
                                                                    default_contract_fuel
                                                                    first)
                                                                    | None ->
                                                                    Some
                                                                    (CBoolLit
                                                                    true))
                                                                    | None ->
                                                                    Some
                                                                    (CBoolLit
                                                                    true)
                                                                    in
                                                                    let var_opt =
                                                                    match 
                                                                    json_field_get
                                                                    ('v'::('a'::('r'::('i'::('a'::('n'::('t'::('s'::[]))))))))
                                                                    j with
                                                                    | Some var_list_v ->
                                                                    (match 
                                                                    json_to_list
                                                                    var_list_v with
                                                                    | Some l ->
                                                                    (match l with
                                                                    | [] ->
                                                                    Some
                                                                    (CInt 0)
                                                                    | first::_ ->
                                                                    ir_to_contract_expr
                                                                    default_contract_fuel
                                                                    first)
                                                                    | None ->
                                                                    Some
                                                                    (CInt 0))
                                                                    | None ->
                                                                    Some
                                                                    (CInt 0)
                                                                    in
                                                                    (
                                                                    match inv_opt with
                                                                    | Some inv ->
                                                                    (match var_opt with
                                                                    | Some var ->
                                                                    (match 
                                                                    ir_to_expr
                                                                    default_expr_fuel
                                                                    testv with
                                                                    | Some c ->
                                                                    (match 
                                                                    ir_to_stmt_n
                                                                    n bodyv with
                                                                    | Some b ->
                                                                    Some
                                                                    (SWhile
                                                                    (inv,
                                                                    var, c,
                                                                    b))
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                  | None ->
                                                                    None)
                                                               | None -> None)
                                                         else if eqb t
                                                                   ('A'::('s'::('s'::('e'::('r'::('t'::[]))))))
                                                              then (match 
                                                                    json_field_get
                                                                    ('t'::('e'::('s'::('t'::[]))))
                                                                    j with
                                                                    | Some testv ->
                                                                    (match 
                                                                    ir_to_contract_expr
                                                                    default_contract_fuel
                                                                    testv with
                                                                    | Some c ->
                                                                    let msg =
                                                                    match 
                                                                    json_field_get
                                                                    ('m'::('s'::('g'::[])))
                                                                    j with
                                                                    | Some mv ->
                                                                    (match 
                                                                    json_to_string
                                                                    mv with
                                                                    | Some s ->
                                                                    s
                                                                    | None ->
                                                                    [])
                                                                    | None ->
                                                                    []
                                                                    in
                                                                    Some
                                                                    (SAssert
                                                                    (c, msg))
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                              else if 
                                                                    eqb t
                                                                    ('L'::('a'::('b'::('e'::('l'::[])))))
                                                                   then 
                                                                    (match 
                                                                    json_field_get
                                                                    ('n'::('a'::('m'::('e'::[]))))
                                                                    j with
                                                                    | Some nv ->
                                                                    (match 
                                                                    json_to_string
                                                                    nv with
                                                                    | Some s ->
                                                                    Some
                                                                    (SLabel s)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                   else 
                                                                    if 
                                                                    eqb t
                                                                    ('R'::('a'::('i'::('s'::('e'::[])))))
                                                                    then 
                                                                    (match 
                                                                    json_field_get
                                                                    ('e'::('x'::('c'::('_'::('t'::('y'::('p'::('e'::[]))))))))
                                                                    j with
                                                                    | Some ev ->
                                                                    (match 
                                                                    json_to_string
                                                                    ev with
                                                                    | Some s ->
                                                                    Some
                                                                    (SRaise s)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    Some
                                                                    (SRaise
                                                                    ('P'::('y'::('C'::('S'::('L'::('_'::('E'::('x'::('c'::('e'::('p'::('t'::('i'::('o'::('n'::[])))))))))))))))))
                                                                    else 
                                                                    if 
                                                                    eqb t
                                                                    ('T'::('r'::('y'::[])))
                                                                    then 
                                                                    (match 
                                                                    json_field_get
                                                                    ('b'::('o'::('d'::('y'::[]))))
                                                                    j with
                                                                    | Some bodyv ->
                                                                    (match 
                                                                    json_field_get
                                                                    ('h'::('a'::('n'::('d'::('l'::('e'::('r'::('s'::[]))))))))
                                                                    j with
                                                                    | Some handlers_v ->
                                                                    (match 
                                                                    json_to_list
                                                                    handlers_v with
                                                                    | Some l ->
                                                                    (match l with
                                                                    | [] ->
                                                                    None
                                                                    | handler::l0 ->
                                                                    (match l0 with
                                                                    | [] ->
                                                                    (match 
                                                                    json_field_get
                                                                    ('e'::('x'::('c'::('_'::('t'::('y'::('p'::('e'::[]))))))))
                                                                    handler with
                                                                    | Some etv ->
                                                                    (match 
                                                                    json_field_get
                                                                    ('b'::('o'::('d'::('y'::[]))))
                                                                    handler with
                                                                    | Some hbodyv ->
                                                                    (match 
                                                                    json_to_string
                                                                    etv with
                                                                    | Some exc ->
                                                                    (match 
                                                                    ir_to_stmt_n
                                                                    n bodyv with
                                                                    | Some b ->
                                                                    (match 
                                                                    ir_to_stmt_n
                                                                    n hbodyv with
                                                                    | Some h ->
                                                                    Some
                                                                    (STryCatch
                                                                    (b, exc,
                                                                    h))
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | _::_ ->
                                                                    None))
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    else 
                                                                    if 
                                                                    eqb t
                                                                    ('C'::('r'::('i'::('t'::('i'::('c'::('a'::('l'::('S'::('e'::('c'::('t'::('i'::('o'::('n'::[])))))))))))))))
                                                                    then 
                                                                    (match 
                                                                    json_field_get
                                                                    ('m'::('u'::('t'::('e'::('x'::[])))))
                                                                    j with
                                                                    | Some mv ->
                                                                    (match 
                                                                    json_field_get
                                                                    ('b'::('o'::('d'::('y'::[]))))
                                                                    j with
                                                                    | Some bodyv ->
                                                                    (match 
                                                                    json_to_string
                                                                    mv with
                                                                    | Some m ->
                                                                    (match 
                                                                    ir_to_stmt_n
                                                                    n bodyv with
                                                                    | Some b ->
                                                                    Some
                                                                    (SCritical
                                                                    (m, b))
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    else 
                                                                    if 
                                                                    eqb t
                                                                    ('G'::('h'::('o'::('s'::('t'::('A'::('s'::('s'::('i'::('g'::('n'::[])))))))))))
                                                                    then 
                                                                    (match 
                                                                    json_field_get
                                                                    ('t'::('a'::('r'::('g'::('e'::('t'::[]))))))
                                                                    j with
                                                                    | Some tgt ->
                                                                    (match 
                                                                    json_field_get
                                                                    ('o'::('p'::[]))
                                                                    j with
                                                                    | Some opv ->
                                                                    (match 
                                                                    json_field_get
                                                                    ('g'::('h'::('o'::('s'::('t'::('_'::('t'::('y'::('p'::('e'::[]))))))))))
                                                                    j with
                                                                    | Some gtv ->
                                                                    (match 
                                                                    json_field_get
                                                                    ('v'::('a'::('l'::('u'::('e'::[])))))
                                                                    j with
                                                                    | Some valv ->
                                                                    (match 
                                                                    json_to_string
                                                                    tgt with
                                                                    | Some name ->
                                                                    (match 
                                                                    json_to_string
                                                                    opv with
                                                                    | Some opstr ->
                                                                    (match 
                                                                    json_to_string
                                                                    gtv with
                                                                    | Some gtstr ->
                                                                    (match 
                                                                    string_to_ghost_type
                                                                    gtstr with
                                                                    | Some gt ->
                                                                    (match 
                                                                    ir_to_contract_expr
                                                                    default_contract_fuel
                                                                    valv with
                                                                    | Some ce ->
                                                                    if 
                                                                    eqb opstr
                                                                    ('='::[])
                                                                    then 
                                                                    Some
                                                                    (SGhostDecl
                                                                    (name,
                                                                    gt, ce))
                                                                    else 
                                                                    (match 
                                                                    string_to_aug_op
                                                                    opstr with
                                                                    | Some aug ->
                                                                    Some
                                                                    (SGhostAssign
                                                                    (name,
                                                                    gt, aug,
                                                                    ce))
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    else 
                                                                    if 
                                                                    eqb t
                                                                    ('F'::('i'::('e'::('l'::('d'::('A'::('s'::('s'::('i'::('g'::('n'::[])))))))))))
                                                                    then 
                                                                    (match 
                                                                    json_field_get
                                                                    ('o'::('b'::('j'::('e'::('c'::('t'::[]))))))
                                                                    j with
                                                                    | Some objv ->
                                                                    (match 
                                                                    json_field_get
                                                                    ('f'::('i'::('e'::('l'::('d'::[])))))
                                                                    j with
                                                                    | Some fv ->
                                                                    (match 
                                                                    json_field_get
                                                                    ('v'::('a'::('l'::('u'::('e'::[])))))
                                                                    j with
                                                                    | Some valv ->
                                                                    (match 
                                                                    json_to_string
                                                                    objv with
                                                                    | Some self_id ->
                                                                    (match 
                                                                    json_to_string
                                                                    fv with
                                                                    | Some f ->
                                                                    (match 
                                                                    ir_to_expr
                                                                    default_expr_fuel
                                                                    valv with
                                                                    | Some e ->
                                                                    Some
                                                                    (SFieldAssign
                                                                    (self_id,
                                                                    f, e))
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    else 
                                                                    if 
                                                                    eqb t
                                                                    ('F'::('o'::('r'::[])))
                                                                    then 
                                                                    (match 
                                                                    json_field_get
                                                                    ('t'::('a'::('r'::('g'::('e'::('t'::[]))))))
                                                                    j with
                                                                    | Some tgtv ->
                                                                    (match 
                                                                    json_field_get
                                                                    ('i'::('t'::('e'::('r'::[]))))
                                                                    j with
                                                                    | Some iterv ->
                                                                    (match 
                                                                    json_field_get
                                                                    ('b'::('o'::('d'::('y'::[]))))
                                                                    j with
                                                                    | Some bodyv ->
                                                                    (match 
                                                                    json_to_string
                                                                    tgtv with
                                                                    | Some x ->
                                                                    (match 
                                                                    json_field_get
                                                                    ('t'::('y'::('p'::('e'::[]))))
                                                                    iterv with
                                                                    | Some itype ->
                                                                    (match 
                                                                    json_to_string
                                                                    itype with
                                                                    | Some s ->
                                                                    (match s with
                                                                    | [] ->
                                                                    None
                                                                    | a::s0 ->
                                                                    (* If this appears, you're using Ascii internals. Please don't *)
 (fun f c ->
  let n = Char.code c in
  let h i = (n land (1 lsl i)) <> 0 in
  f (h 0) (h 1) (h 2) (h 3) (h 4) (h 5) (h 6) (h 7))
                                                                    (fun b b0 b1 b2 b3 b4 b5 b6 ->
                                                                    if b
                                                                    then 
                                                                    if b0
                                                                    then 
                                                                    if b1
                                                                    then None
                                                                    else 
                                                                    if b2
                                                                    then None
                                                                    else 
                                                                    if b3
                                                                    then None
                                                                    else 
                                                                    if b4
                                                                    then None
                                                                    else 
                                                                    if b5
                                                                    then 
                                                                    if b6
                                                                    then None
                                                                    else 
                                                                    (match s0 with
                                                                    | [] ->
                                                                    None
                                                                    | a0::s1 ->
                                                                    (* If this appears, you're using Ascii internals. Please don't *)
 (fun f c ->
  let n = Char.code c in
  let h i = (n land (1 lsl i)) <> 0 in
  f (h 0) (h 1) (h 2) (h 3) (h 4) (h 5) (h 6) (h 7))
                                                                    (fun b7 b8 b9 b10 b11 b12 b13 b14 ->
                                                                    if b7
                                                                    then 
                                                                    if b8
                                                                    then None
                                                                    else 
                                                                    if b9
                                                                    then None
                                                                    else 
                                                                    if b10
                                                                    then None
                                                                    else 
                                                                    if b11
                                                                    then None
                                                                    else 
                                                                    if b12
                                                                    then 
                                                                    if b13
                                                                    then 
                                                                    if b14
                                                                    then None
                                                                    else 
                                                                    (match s1 with
                                                                    | [] ->
                                                                    None
                                                                    | a1::s2 ->
                                                                    (* If this appears, you're using Ascii internals. Please don't *)
 (fun f c ->
  let n = Char.code c in
  let h i = (n land (1 lsl i)) <> 0 in
  f (h 0) (h 1) (h 2) (h 3) (h 4) (h 5) (h 6) (h 7))
                                                                    (fun b15 b16 b17 b18 b19 b20 b21 b22 ->
                                                                    if b15
                                                                    then None
                                                                    else 
                                                                    if b16
                                                                    then None
                                                                    else 
                                                                    if b17
                                                                    then 
                                                                    if b18
                                                                    then 
                                                                    if b19
                                                                    then None
                                                                    else 
                                                                    if b20
                                                                    then 
                                                                    if b21
                                                                    then 
                                                                    if b22
                                                                    then None
                                                                    else 
                                                                    (match s2 with
                                                                    | [] ->
                                                                    None
                                                                    | a2::s3 ->
                                                                    (* If this appears, you're using Ascii internals. Please don't *)
 (fun f c ->
  let n = Char.code c in
  let h i = (n land (1 lsl i)) <> 0 in
  f (h 0) (h 1) (h 2) (h 3) (h 4) (h 5) (h 6) (h 7))
                                                                    (fun b23 b24 b25 b26 b27 b28 b29 b30 ->
                                                                    if b23
                                                                    then None
                                                                    else 
                                                                    if b24
                                                                    then None
                                                                    else 
                                                                    if b25
                                                                    then 
                                                                    if b26
                                                                    then 
                                                                    if b27
                                                                    then None
                                                                    else 
                                                                    if b28
                                                                    then 
                                                                    if b29
                                                                    then 
                                                                    if b30
                                                                    then None
                                                                    else 
                                                                    (match s3 with
                                                                    | [] ->
                                                                    (match 
                                                                    json_field_get
                                                                    ('f'::('u'::('n'::('c'::[]))))
                                                                    iterv with
                                                                    | Some fnv ->
                                                                    (match 
                                                                    json_field_get
                                                                    ('a'::('r'::('g'::('s'::[]))))
                                                                    iterv with
                                                                    | Some argsv ->
                                                                    (match 
                                                                    json_to_string
                                                                    fnv with
                                                                    | Some s4 ->
                                                                    (match s4 with
                                                                    | [] ->
                                                                    None
                                                                    | a3::s5 ->
                                                                    (* If this appears, you're using Ascii internals. Please don't *)
 (fun f c ->
  let n = Char.code c in
  let h i = (n land (1 lsl i)) <> 0 in
  f (h 0) (h 1) (h 2) (h 3) (h 4) (h 5) (h 6) (h 7))
                                                                    (fun b31 b32 b33 b34 b35 b36 b37 b38 ->
                                                                    if b31
                                                                    then None
                                                                    else 
                                                                    if b32
                                                                    then 
                                                                    if b33
                                                                    then None
                                                                    else 
                                                                    if b34
                                                                    then None
                                                                    else 
                                                                    if b35
                                                                    then 
                                                                    if b36
                                                                    then 
                                                                    if b37
                                                                    then 
                                                                    if b38
                                                                    then None
                                                                    else 
                                                                    (match s5 with
                                                                    | [] ->
                                                                    None
                                                                    | a4::s6 ->
                                                                    (* If this appears, you're using Ascii internals. Please don't *)
 (fun f c ->
  let n = Char.code c in
  let h i = (n land (1 lsl i)) <> 0 in
  f (h 0) (h 1) (h 2) (h 3) (h 4) (h 5) (h 6) (h 7))
                                                                    (fun b39 b40 b41 b42 b43 b44 b45 b46 ->
                                                                    if b39
                                                                    then 
                                                                    if b40
                                                                    then None
                                                                    else 
                                                                    if b41
                                                                    then None
                                                                    else 
                                                                    if b42
                                                                    then None
                                                                    else 
                                                                    if b43
                                                                    then None
                                                                    else 
                                                                    if b44
                                                                    then 
                                                                    if b45
                                                                    then 
                                                                    if b46
                                                                    then None
                                                                    else 
                                                                    (match s6 with
                                                                    | [] ->
                                                                    None
                                                                    | a5::s7 ->
                                                                    (* If this appears, you're using Ascii internals. Please don't *)
 (fun f c ->
  let n = Char.code c in
  let h i = (n land (1 lsl i)) <> 0 in
  f (h 0) (h 1) (h 2) (h 3) (h 4) (h 5) (h 6) (h 7))
                                                                    (fun b47 b48 b49 b50 b51 b52 b53 b54 ->
                                                                    if b47
                                                                    then None
                                                                    else 
                                                                    if b48
                                                                    then 
                                                                    if b49
                                                                    then 
                                                                    if b50
                                                                    then 
                                                                    if b51
                                                                    then None
                                                                    else 
                                                                    if b52
                                                                    then 
                                                                    if b53
                                                                    then 
                                                                    if b54
                                                                    then None
                                                                    else 
                                                                    (match s7 with
                                                                    | [] ->
                                                                    None
                                                                    | a6::s8 ->
                                                                    (* If this appears, you're using Ascii internals. Please don't *)
 (fun f c ->
  let n = Char.code c in
  let h i = (n land (1 lsl i)) <> 0 in
  f (h 0) (h 1) (h 2) (h 3) (h 4) (h 5) (h 6) (h 7))
                                                                    (fun b55 b56 b57 b58 b59 b60 b61 b62 ->
                                                                    if b55
                                                                    then 
                                                                    if b56
                                                                    then 
                                                                    if b57
                                                                    then 
                                                                    if b58
                                                                    then None
                                                                    else 
                                                                    if b59
                                                                    then None
                                                                    else 
                                                                    if b60
                                                                    then 
                                                                    if b61
                                                                    then 
                                                                    if b62
                                                                    then None
                                                                    else 
                                                                    (match s8 with
                                                                    | [] ->
                                                                    None
                                                                    | a7::s9 ->
                                                                    (* If this appears, you're using Ascii internals. Please don't *)
 (fun f c ->
  let n = Char.code c in
  let h i = (n land (1 lsl i)) <> 0 in
  f (h 0) (h 1) (h 2) (h 3) (h 4) (h 5) (h 6) (h 7))
                                                                    (fun b63 b64 b65 b66 b67 b68 b69 b70 ->
                                                                    if b63
                                                                    then 
                                                                    if b64
                                                                    then None
                                                                    else 
                                                                    if b65
                                                                    then 
                                                                    if b66
                                                                    then None
                                                                    else 
                                                                    if b67
                                                                    then None
                                                                    else 
                                                                    if b68
                                                                    then 
                                                                    if b69
                                                                    then 
                                                                    if b70
                                                                    then None
                                                                    else 
                                                                    (match s9 with
                                                                    | [] ->
                                                                    (match 
                                                                    json_to_list
                                                                    argsv with
                                                                    | Some l ->
                                                                    (match l with
                                                                    | [] ->
                                                                    None
                                                                    | start::l0 ->
                                                                    (match l0 with
                                                                    | [] ->
                                                                    (match 
                                                                    ir_to_expr
                                                                    default_expr_fuel
                                                                    start with
                                                                    | Some n0 ->
                                                                    (match 
                                                                    ir_to_stmt_n
                                                                    n bodyv with
                                                                    | Some body ->
                                                                    let inv =
                                                                    CBoolLit
                                                                    true
                                                                    in
                                                                    let var =
                                                                    CInt 0
                                                                    in
                                                                    Some
                                                                    (SSeq
                                                                    ((SAssign
                                                                    (x, (EInt
                                                                    0))),
                                                                    (SWhile
                                                                    (inv,
                                                                    var,
                                                                    (ECmp
                                                                    (OpLt,
                                                                    (EVar x),
                                                                    n0)),
                                                                    (SSeq
                                                                    (body,
                                                                    (SAugAssign
                                                                    (x,
                                                                    OpAdd,
                                                                    (EInt
                                                                    1)))))))))
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | stop::l1 ->
                                                                    (match l1 with
                                                                    | [] ->
                                                                    (match 
                                                                    ir_to_expr
                                                                    default_expr_fuel
                                                                    start with
                                                                    | Some s10 ->
                                                                    (match 
                                                                    ir_to_expr
                                                                    default_expr_fuel
                                                                    stop with
                                                                    | Some e ->
                                                                    (match 
                                                                    ir_to_stmt_n
                                                                    n bodyv with
                                                                    | Some body ->
                                                                    let inv =
                                                                    CBoolLit
                                                                    true
                                                                    in
                                                                    let var =
                                                                    CInt 0
                                                                    in
                                                                    Some
                                                                    (SSeq
                                                                    ((SAssign
                                                                    (x,
                                                                    s10)),
                                                                    (SWhile
                                                                    (inv,
                                                                    var,
                                                                    (ECmp
                                                                    (OpLt,
                                                                    (EVar x),
                                                                    e)),
                                                                    (SSeq
                                                                    (body,
                                                                    (SAugAssign
                                                                    (x,
                                                                    OpAdd,
                                                                    (EInt
                                                                    1)))))))))
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | step::l2 ->
                                                                    (match l2 with
                                                                    | [] ->
                                                                    (match 
                                                                    ir_to_expr
                                                                    default_expr_fuel
                                                                    start with
                                                                    | Some s10 ->
                                                                    (match 
                                                                    ir_to_expr
                                                                    default_expr_fuel
                                                                    stop with
                                                                    | Some e ->
                                                                    (match 
                                                                    ir_to_expr
                                                                    default_expr_fuel
                                                                    step with
                                                                    | Some k ->
                                                                    (match 
                                                                    ir_to_stmt_n
                                                                    n bodyv with
                                                                    | Some body ->
                                                                    let inv =
                                                                    CBoolLit
                                                                    true
                                                                    in
                                                                    let var =
                                                                    CInt 0
                                                                    in
                                                                    Some
                                                                    (SSeq
                                                                    ((SAssign
                                                                    (x,
                                                                    s10)),
                                                                    (SWhile
                                                                    (inv,
                                                                    var,
                                                                    (ECmp
                                                                    (OpLt,
                                                                    (EVar x),
                                                                    e)),
                                                                    (SSeq
                                                                    (body,
                                                                    (SAugAssign
                                                                    (x,
                                                                    OpAdd,
                                                                    k))))))))
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | _::_ ->
                                                                    None))))
                                                                    | None ->
                                                                    None)
                                                                    | _::_ ->
                                                                    None)
                                                                    else None
                                                                    else None
                                                                    else None
                                                                    else None)
                                                                    a7)
                                                                    else None
                                                                    else None
                                                                    else None
                                                                    else None
                                                                    else None)
                                                                    a6)
                                                                    else None
                                                                    else None
                                                                    else None
                                                                    else None
                                                                    else None)
                                                                    a5)
                                                                    else None
                                                                    else None
                                                                    else None)
                                                                    a4)
                                                                    else None
                                                                    else None
                                                                    else None
                                                                    else None)
                                                                    a3)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | _::_ ->
                                                                    None)
                                                                    else None
                                                                    else None
                                                                    else None
                                                                    else None)
                                                                    a2)
                                                                    else None
                                                                    else None
                                                                    else None
                                                                    else None)
                                                                    a1)
                                                                    else None
                                                                    else None
                                                                    else None)
                                                                    a0)
                                                                    else None
                                                                    else None
                                                                    else 
                                                                    if b0
                                                                    then 
                                                                    if b1
                                                                    then 
                                                                    if b2
                                                                    then None
                                                                    else 
                                                                    if b3
                                                                    then 
                                                                    if b4
                                                                    then None
                                                                    else 
                                                                    if b5
                                                                    then 
                                                                    if b6
                                                                    then None
                                                                    else 
                                                                    (match s0 with
                                                                    | [] ->
                                                                    None
                                                                    | a0::s1 ->
                                                                    (* If this appears, you're using Ascii internals. Please don't *)
 (fun f c ->
  let n = Char.code c in
  let h i = (n land (1 lsl i)) <> 0 in
  f (h 0) (h 1) (h 2) (h 3) (h 4) (h 5) (h 6) (h 7))
                                                                    (fun b7 b8 b9 b10 b11 b12 b13 b14 ->
                                                                    if b7
                                                                    then 
                                                                    if b8
                                                                    then None
                                                                    else 
                                                                    if b9
                                                                    then None
                                                                    else 
                                                                    if b10
                                                                    then None
                                                                    else 
                                                                    if b11
                                                                    then None
                                                                    else 
                                                                    if b12
                                                                    then 
                                                                    if b13
                                                                    then 
                                                                    if b14
                                                                    then None
                                                                    else 
                                                                    (match s1 with
                                                                    | [] ->
                                                                    None
                                                                    | a1::s2 ->
                                                                    (* If this appears, you're using Ascii internals. Please don't *)
 (fun f c ->
  let n = Char.code c in
  let h i = (n land (1 lsl i)) <> 0 in
  f (h 0) (h 1) (h 2) (h 3) (h 4) (h 5) (h 6) (h 7))
                                                                    (fun b15 b16 b17 b18 b19 b20 b21 b22 ->
                                                                    if b15
                                                                    then None
                                                                    else 
                                                                    if b16
                                                                    then 
                                                                    if b17
                                                                    then None
                                                                    else 
                                                                    if b18
                                                                    then None
                                                                    else 
                                                                    if b19
                                                                    then 
                                                                    if b20
                                                                    then 
                                                                    if b21
                                                                    then 
                                                                    if b22
                                                                    then None
                                                                    else 
                                                                    (match s2 with
                                                                    | [] ->
                                                                    (match 
                                                                    json_field_get
                                                                    ('n'::('a'::('m'::('e'::[]))))
                                                                    iterv with
                                                                    | Some namev ->
                                                                    (match 
                                                                    json_to_string
                                                                    namev with
                                                                    | Some arr ->
                                                                    (match 
                                                                    ir_to_stmt_n
                                                                    n bodyv with
                                                                    | Some body ->
                                                                    let inv =
                                                                    match 
                                                                    json_field_get
                                                                    ('i'::('n'::('v'::('a'::('r'::('i'::('a'::('n'::('t'::('s'::[]))))))))))
                                                                    j with
                                                                    | Some il ->
                                                                    (match 
                                                                    json_to_list
                                                                    il with
                                                                    | Some l ->
                                                                    (match l with
                                                                    | [] ->
                                                                    CBoolLit
                                                                    true
                                                                    | first::_ ->
                                                                    (match 
                                                                    ir_to_contract_expr
                                                                    default_contract_fuel
                                                                    first with
                                                                    | Some ce ->
                                                                    ce
                                                                    | None ->
                                                                    CBoolLit
                                                                    true))
                                                                    | None ->
                                                                    CBoolLit
                                                                    true)
                                                                    | None ->
                                                                    CBoolLit
                                                                    true
                                                                    in
                                                                    let var =
                                                                    match 
                                                                    json_field_get
                                                                    ('v'::('a'::('r'::('i'::('a'::('n'::('t'::('s'::[]))))))))
                                                                    j with
                                                                    | Some vl ->
                                                                    (match 
                                                                    json_to_list
                                                                    vl with
                                                                    | Some l ->
                                                                    (match l with
                                                                    | [] ->
                                                                    CInt 0
                                                                    | first::_ ->
                                                                    (match 
                                                                    ir_to_contract_expr
                                                                    default_contract_fuel
                                                                    first with
                                                                    | Some ce ->
                                                                    ce
                                                                    | None ->
                                                                    CInt 0))
                                                                    | None ->
                                                                    CInt 0)
                                                                    | None ->
                                                                    CInt 0
                                                                    in
                                                                    Some
                                                                    (SFor (x,
                                                                    arr, inv,
                                                                    var,
                                                                    body,
                                                                    true))
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | _::_ ->
                                                                    None)
                                                                    else None
                                                                    else None
                                                                    else None
                                                                    else None)
                                                                    a1)
                                                                    else None
                                                                    else None
                                                                    else None)
                                                                    a0)
                                                                    else None
                                                                    else None
                                                                    else None
                                                                    else None)
                                                                    a)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    else 
                                                                    if 
                                                                    eqb t
                                                                    ('T'::('u'::('p'::('l'::('e'::('U'::('n'::('p'::('a'::('c'::('k'::[])))))))))))
                                                                    then 
                                                                    (match 
                                                                    json_field_get
                                                                    ('t'::('a'::('r'::('g'::('e'::('t'::('s'::[])))))))
                                                                    j with
                                                                    | Some tgtsv ->
                                                                    (match 
                                                                    json_field_get
                                                                    ('v'::('a'::('l'::('u'::('e'::[])))))
                                                                    j with
                                                                    | Some valv ->
                                                                    (match 
                                                                    json_to_list
                                                                    tgtsv with
                                                                    | Some tlist ->
                                                                    (match 
                                                                    option_map_list
                                                                    json_to_string
                                                                    tlist with
                                                                    | Some xs ->
                                                                    (match 
                                                                    ir_to_expr
                                                                    default_expr_fuel
                                                                    valv with
                                                                    | Some e ->
                                                                    Some
                                                                    (STupleUnpack
                                                                    (xs, e))
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    else 
                                                                    if 
                                                                    eqb t
                                                                    ('F'::('i'::('e'::('l'::('d'::('A'::('u'::('g'::('A'::('s'::('s'::('i'::('g'::('n'::[]))))))))))))))
                                                                    then 
                                                                    (match 
                                                                    json_field_get
                                                                    ('o'::('b'::('j'::('e'::('c'::('t'::[]))))))
                                                                    j with
                                                                    | Some objv ->
                                                                    (match 
                                                                    json_field_get
                                                                    ('f'::('i'::('e'::('l'::('d'::[])))))
                                                                    j with
                                                                    | Some fv ->
                                                                    (match 
                                                                    json_field_get
                                                                    ('o'::('p'::[]))
                                                                    j with
                                                                    | Some opv ->
                                                                    (match 
                                                                    json_field_get
                                                                    ('v'::('a'::('l'::('u'::('e'::[])))))
                                                                    j with
                                                                    | Some valv ->
                                                                    (match 
                                                                    json_to_string
                                                                    objv with
                                                                    | Some self_id ->
                                                                    (match 
                                                                    json_to_string
                                                                    fv with
                                                                    | Some f ->
                                                                    (match 
                                                                    json_to_string
                                                                    opv with
                                                                    | Some opstr ->
                                                                    (match 
                                                                    aug_string_to_binop
                                                                    opstr with
                                                                    | Some op ->
                                                                    (match 
                                                                    ir_to_expr
                                                                    default_expr_fuel
                                                                    valv with
                                                                    | Some e ->
                                                                    Some
                                                                    (SFieldAugAssign
                                                                    (self_id,
                                                                    f, op, e))
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    | None ->
                                                                    None)
                                                                    else None
          | None -> None)
       | None -> None))
    fuel

(** val default_stmt_fuel : int **)

let default_stmt_fuel =
  Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    0)))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))

(** val ir_to_stmt : json_value -> stmt option **)

let ir_to_stmt j =
  ir_to_stmt_n default_stmt_fuel j

(** val json_has_key : char list -> (char list * json_value) list -> bool **)

let rec json_has_key key = function
| [] -> false
| p::rest ->
  let (k, _) = p in if eqb k key then true else json_has_key key rest

(** val json_obj_has_all_keys : char list list -> json_value -> bool **)

let json_obj_has_all_keys keys = function
| JsonObject kvs ->
  let rec all_present = function
  | [] -> true
  | k::rest -> (&&) (json_has_key k kvs) (all_present rest)
  in all_present keys
| _ -> false

(** val json_is_object : json_value -> bool **)

let json_is_object = function
| JsonObject _ -> true
| _ -> false

(** val required_top : char list list **)

let required_top =
  ('t'::('y'::('p'::('e'::('_'::('d'::('e'::('c'::('l'::('s'::[]))))))))))::(('f'::('u'::('n'::('c'::('t'::('i'::('o'::('n'::('s'::[])))))))))::[])

(** val required_function : char list list **)

let required_function =
  ('n'::('a'::('m'::('e'::[]))))::(('s'::('y'::('m'::('b'::('o'::('l'::('_'::('t'::('a'::('b'::('l'::('e'::[]))))))))))))::(('r'::('e'::('t'::('u'::('r'::('n'::('_'::('a'::('n'::('n'::('o'::('t'::('a'::('t'::('i'::('o'::('n'::[])))))))))))))))))::(('c'::('o'::('n'::('t'::('r'::('a'::('c'::('t'::('s'::[])))))))))::(('b'::('o'::('d'::('y'::[]))))::(('f'::('u'::('n'::('c'::('t'::('i'::('o'::('n'::('_'::('v'::('a'::('r'::('i'::('a'::('n'::('t'::('s'::[])))))))))))))))))::(('d'::('i'::('v'::('e'::('r'::('g'::('e'::('s'::[]))))))))::(('t'::('r'::('u'::('s'::('t'::('e'::('d'::[])))))))::(('b'::('o'::('u'::('n'::('d'::('e'::('d'::('_'::('i'::('n'::('t'::[])))))))))))::[]))))))))

(** val required_contracts : char list list **)

let required_contracts =
  ('r'::('e'::('q'::('u'::('i'::('r'::('e'::('s'::[]))))))))::(('e'::('n'::('s'::('u'::('r'::('e'::('s'::[])))))))::(('a'::('s'::('s'::('i'::('g'::('n'::('s'::[])))))))::(('r'::('a'::('i'::('s'::('e'::('s'::[]))))))::[])))

(** val validate_contracts : json_value -> bool **)

let validate_contracts j =
  json_obj_has_all_keys required_contracts j

(** val validate_function : json_value -> bool **)

let validate_function j =
  (&&) (json_obj_has_all_keys required_function j)
    (match j with
     | JsonObject kvs ->
       let rec lookup_contracts = function
       | [] -> false
       | p::rest ->
         let (k, v) = p in
         if eqb k
              ('c'::('o'::('n'::('t'::('r'::('a'::('c'::('t'::('s'::[])))))))))
         then validate_contracts v
         else lookup_contracts rest
       in lookup_contracts kvs
     | _ -> false)

(** val validate_functions_list : json_value list -> bool **)

let rec validate_functions_list = function
| [] -> true
| f::rest -> (&&) (validate_function f) (validate_functions_list rest)

(** val validate_ir : json_value -> bool **)

let validate_ir j =
  (&&) ((&&) (json_is_object j) (json_obj_has_all_keys required_top j))
    (match j with
     | JsonObject kvs ->
       let rec lookup_functions = function
       | [] -> false
       | p::rest ->
         let (k, v) = p in
         if eqb k
              ('f'::('u'::('n'::('c'::('t'::('i'::('o'::('n'::('s'::[])))))))))
         then (match v with
               | JsonList fs -> validate_functions_list fs
               | _ -> false)
         else lookup_functions rest
       in lookup_functions kvs
     | _ -> false)
