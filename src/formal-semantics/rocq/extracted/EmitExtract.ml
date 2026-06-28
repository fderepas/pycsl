
(** val negb : bool -> bool **)

let negb = function
| true -> false
| false -> true

(** val fst : ('a1 * 'a2) -> 'a1 **)

let fst = function
| (x, _) -> x

(** val snd : ('a1 * 'a2) -> 'a2 **)

let snd = function
| (_, y) -> y



(** val add : int -> int -> int **)

let rec add = (+)

module Nat =
 struct
  (** val sub : int -> int -> int **)

  let rec sub n m =
    (fun fO fS n -> if n=0 then fO () else fS (n-1))
      (fun _ -> n)
      (fun k ->
      (fun fO fS n -> if n=0 then fO () else fS (n-1))
        (fun _ -> n)
        (fun l -> sub k l)
        m)
      n

  (** val ltb : int -> int -> bool **)

  let ltb n m =
    (<=) (Stdlib.Int.succ n) m

  (** val divmod : int -> int -> int -> int -> int * int **)

  let rec divmod x y q u =
    (fun fO fS n -> if n=0 then fO () else fS (n-1))
      (fun _ -> (q, u))
      (fun x' ->
      (fun fO fS n -> if n=0 then fO () else fS (n-1))
        (fun _ -> divmod x' y (Stdlib.Int.succ q) y)
        (fun u' -> divmod x' y q u')
        u)
      x

  (** val div : int -> int -> int **)

  let div x y =
    (fun fO fS n -> if n=0 then fO () else fS (n-1))
      (fun _ -> y)
      (fun y' -> fst (divmod x y' 0 y'))
      y

  (** val modulo : int -> int -> int **)

  let modulo x y =
    (fun fO fS n -> if n=0 then fO () else fS (n-1))
      (fun _ -> x)
      (fun y' -> sub y' (snd (divmod x y' 0 y')))
      y
 end

module Pos =
 struct
  (** val iter_op : ('a1 -> 'a1 -> 'a1) -> int -> 'a1 -> 'a1 **)

  let rec iter_op op p a =
    (fun f2p1 f2p f1 p ->
  if p<=1 then f1 () else if p mod 2 = 0 then f2p (p/2) else f2p1 (p/2))
      (fun p0 -> op a (iter_op op p0 (op a a)))
      (fun p0 -> iter_op op p0 (op a a))
      (fun _ -> a)
      p

  (** val to_nat : int -> int **)

  let to_nat x =
    iter_op add x (Stdlib.Int.succ 0)
 end

(** val existsb : ('a1 -> bool) -> 'a1 list -> bool **)

let rec existsb f = function
| [] -> false
| a::l0 -> (||) (f a) (existsb f l0)

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

(** val append : char list -> char list -> char list **)

let rec append s1 s2 =
  match s1 with
  | [] -> s2
  | c::s1' -> c::(append s1' s2)

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
| SCall of ident * expr * expr

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

(** val c_conj : contract_expr list -> contract_expr **)

let rec c_conj = function
| [] -> CBoolLit true
| c::rest -> (match rest with
              | [] -> c
              | _::_ -> CAnd (c, (c_conj rest)))

(** val c_first : contract_expr list -> contract_expr **)

let c_first = function
| [] -> CInt 0
| c::_ -> c

(** val for_idx : ident **)

let for_idx =
  '_'::('p'::('y'::('c'::('s'::('l'::('_'::('i'::('d'::('x'::[])))))))))

(** val gen_lift_continue : whyml_stmt -> whyml_stmt -> whyml_stmt **)

let rec gen_lift_continue inc w = match w with
| WSeq (w1, w2) ->
  WSeq ((gen_lift_continue inc w1), (gen_lift_continue inc w2))
| WIf (c, w1, w2) ->
  WIf (c, (gen_lift_continue inc w1), (gen_lift_continue inc w2))
| WRaise exc ->
  (match exc with
   | ExcContinue -> WSeq (inc, (WRaise ExcContinue))
   | _ -> w)
| WTryCatch (body, exc, h) ->
  WTryCatch ((gen_lift_continue inc body), exc, (gen_lift_continue inc h))
| _ -> w

(** val gen : stmt -> whyml_stmt **)

let rec gen = function
| SAssign (x, e) -> WAssign (x, e)
| SAugAssign (x, op, e) -> WAugAssign (x, op, e)
| SArraySet (arr, i, v) -> WArraySet (arr, i, v)
| SSeq (s1, s2) -> WSeq ((gen s1), (gen s2))
| SIf (cond, t, f) -> WIf (cond, (gen t), (gen f))
| SWhile (inv, var, cond, body) ->
  WWhile ((inv::[]), (var::[]), cond, (gen body))
| SFor (x, arr, inv, var, body, _) ->
  let inc = WAugAssign (for_idx, OpAdd, (EInt 1)) in
  WSeq ((WAssign (for_idx, (EInt 0))), (WWhile ((inv::[]), (var::[]), (EBinOp
  (OpSub, (ELen arr), (EVar for_idx))), (WSeq ((WAssign (x, (ESubscript (arr,
  (EVar for_idx))))), (WSeq ((gen_lift_continue inc (gen body)), inc)))))))
| SReturn e ->
  WSeq ((WAssign (('\\'::('r'::('e'::('s'::('u'::('l'::('t'::[]))))))), e)),
    (WRaise ExcReturn))
| SContinue -> WRaise ExcContinue
| SBreak -> WRaise ExcBreak
| SAssert (cond, msg) -> WAssert (cond, msg)
| SGhostDecl (x, t, e) -> WGhostDecl (x, t, e)
| SGhostAssign (x, t, op, e) -> WGhostAssign (x, t, op, e)
| SLabel l -> WLabel l
| SRaise exc -> WRaise (ExcNamed exc)
| STryCatch (body, exc, handler) -> WTryCatch ((gen body), exc, (gen handler))
| SCritical (_, body) -> gen body
| SThreadEntry body -> gen body
| _ -> WSkip

(** val acceptable_skip_emissions : char list list **)

let acceptable_skip_emissions =
  ('('::(')'::[]))::[]

(** val digit_char : int -> char **)

let digit_char d =
  (fun fO fS n -> if n=0 then fO () else fS (n-1))
    (fun _ -> '0')
    (fun n ->
    (fun fO fS n -> if n=0 then fO () else fS (n-1))
      (fun _ -> '1')
      (fun n0 ->
      (fun fO fS n -> if n=0 then fO () else fS (n-1))
        (fun _ -> '2')
        (fun n1 ->
        (fun fO fS n -> if n=0 then fO () else fS (n-1))
          (fun _ -> '3')
          (fun n2 ->
          (fun fO fS n -> if n=0 then fO () else fS (n-1))
            (fun _ -> '4')
            (fun n3 ->
            (fun fO fS n -> if n=0 then fO () else fS (n-1))
              (fun _ -> '5')
              (fun n4 ->
              (fun fO fS n -> if n=0 then fO () else fS (n-1))
                (fun _ -> '6')
                (fun n5 ->
                (fun fO fS n -> if n=0 then fO () else fS (n-1))
                  (fun _ -> '7')
                  (fun n6 ->
                  (fun fO fS n -> if n=0 then fO () else fS (n-1))
                    (fun _ -> '8')
                    (fun _ -> '9')
                    n6)
                  n5)
                n4)
              n3)
            n2)
          n1)
        n0)
      n)
    d

(** val nat_to_string_aux : int -> int -> char list **)

let rec nat_to_string_aux fuel n =
  (fun fO fS n -> if n=0 then fO () else fS (n-1))
    (fun _ -> [])
    (fun fuel' ->
    if Nat.ltb n (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
         (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
         (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ 0))))))))))
    then (digit_char n)::[]
    else append
           (nat_to_string_aux fuel'
             (Nat.div n (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
               (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
               (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
               (Stdlib.Int.succ 0))))))))))))
           ((digit_char
              (Nat.modulo n (Stdlib.Int.succ (Stdlib.Int.succ
                (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
                (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
                (Stdlib.Int.succ (Stdlib.Int.succ 0))))))))))))::[]))
    fuel

(** val nat_to_string : int -> char list **)

let nat_to_string n =
  nat_to_string_aux (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ (Stdlib.Int.succ
    (Stdlib.Int.succ
    0)))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))) n

(** val z_to_string : int -> char list **)

let z_to_string z0 =
  (fun f0 fp fn z -> if z=0 then f0 () else if z>0 then fp z else fn (-z))
    (fun _ -> '0'::[])
    (fun p -> nat_to_string (Pos.to_nat p))
    (fun p -> append ('-'::[]) (nat_to_string (Pos.to_nat p)))
    z0

(** val pretty_binop : binop -> char list **)

let pretty_binop = function
| OpAdd -> '+'::[]
| OpSub -> '-'::[]
| OpMul -> '*'::[]
| OpDiv -> '/'::[]
| OpMod -> 'm'::('o'::('d'::[]))

(** val pretty_cmpop : cmpop -> char list **)

let pretty_cmpop = function
| OpEq -> '='::[]
| OpNe -> '<'::('>'::[])
| OpLt -> '<'::[]
| OpLe -> '<'::('='::[])
| OpGt -> '>'::[]
| OpGe -> '>'::('='::[])

(** val pretty_expr : expr -> char list **)

let rec pretty_expr = function
| EInt n -> z_to_string n
| EVar x -> x
| ESubscript (a, i) ->
  append a (append ('['::[]) (append (pretty_expr i) (']'::[])))
| ELen a ->
  append ('('::('l'::('e'::('n'::('g'::('t'::('h'::(' '::[]))))))))
    (append a (')'::[]))
| EBinOp (op, e1, e2) ->
  append ('('::[])
    (append (pretty_expr e1)
      (append (' '::[])
        (append (pretty_binop op)
          (append (' '::[]) (append (pretty_expr e2) (')'::[]))))))
| ENeg e1 ->
  append ('('::('-'::(' '::[]))) (append (pretty_expr e1) (')'::[]))
| ECmp (op, e1, e2) ->
  append ('('::[])
    (append (pretty_expr e1)
      (append (' '::[])
        (append (pretty_cmpop op)
          (append (' '::[]) (append (pretty_expr e2) (')'::[]))))))
| EFieldGet (obj, f) -> append obj (append ('.'::[]) f)
| ECall (func, args) ->
  append func
    (append ('('::[])
      (append
        (let rec args_str = function
         | [] -> []
         | x::rest ->
           (match rest with
            | [] -> pretty_expr x
            | _::_ ->
              append (pretty_expr x) (append (','::(' '::[])) (args_str rest)))
         in args_str args) (')'::[])))

type assign_state = { as_shared_vars : ident list;
                      as_declared_refs : ident list;
                      as_bounded_int : char list option }

(** val ident_in : ident -> ident list -> bool **)

let ident_in x xs =
  existsb (eqb x) xs

(** val emit_assign : assign_state -> ident -> expr -> char list **)

let emit_assign s x e =
  if ident_in x s.as_shared_vars
  then append x (append (' '::(':'::('='::(' '::[])))) (pretty_expr e))
  else if negb (ident_in x s.as_declared_refs)
       then (match s.as_bounded_int with
             | Some bits ->
               append ('l'::('e'::('t'::(' '::[]))))
                 (append x
                   (append
                     (' '::('='::(' '::('r'::('e'::('f'::(' '::('('::[]))))))))
                     (append (pretty_expr e)
                       (append (' '::(':'::(' '::('i'::('n'::('t'::[]))))))
                         (append bits
                           (append (')'::(' '::('i'::('n'::[])))) ('\n'::[])))))))
             | None ->
               append ('l'::('e'::('t'::(' '::[]))))
                 (append x
                   (append
                     (' '::('='::(' '::('r'::('e'::('f'::(' '::[])))))))
                     (append (pretty_expr e)
                       (append (' '::('i'::('n'::[]))) ('\n'::[]))))))
       else append x (append (' '::(':'::('='::(' '::[])))) (pretty_expr e))

(** val acceptable_assign_emissions :
    assign_state -> ident -> expr -> char list list **)

let acceptable_assign_emissions s x e =
  let ne = '\n'::[] in
  let assign_form =
    append x (append (' '::(':'::('='::(' '::[])))) (pretty_expr e))
  in
  let let_default =
    append ('l'::('e'::('t'::(' '::[]))))
      (append x
        (append (' '::('='::(' '::('r'::('e'::('f'::(' '::[])))))))
          (append (pretty_expr e) (append (' '::('i'::('n'::[]))) ne))))
  in
  let let_bounded =
    match s.as_bounded_int with
    | Some bits ->
      append ('l'::('e'::('t'::(' '::[]))))
        (append x
          (append (' '::('='::(' '::('r'::('e'::('f'::(' '::('('::[]))))))))
            (append (pretty_expr e)
              (append (' '::(':'::(' '::('i'::('n'::('t'::[]))))))
                (append bits (append (')'::(' '::('i'::('n'::[])))) ne))))))
    | None -> let_default
  in
  assign_form::(let_default::(let_bounded::[]))

(** val op_translate_aug : binop -> char list **)

let op_translate_aug = function
| OpAdd -> '+'::[]
| OpSub -> '-'::[]
| OpMul -> '*'::[]
| OpDiv -> 'd'::('i'::('v'::[]))
| OpMod -> 'm'::('o'::('d'::[]))

(** val emit_aug_assign : ident -> binop -> expr -> char list **)

let emit_aug_assign x op e =
  append x
    (append (' '::(':'::('='::(' '::('!'::[])))))
      (append x
        (append (' '::[])
          (append (op_translate_aug op) (append (' '::[]) (pretty_expr e))))))

(** val acceptable_aug_assign_emissions :
    ident -> binop -> expr -> char list list **)

let acceptable_aug_assign_emissions x op e =
  (append x
    (append (' '::(':'::('='::(' '::('!'::[])))))
      (append x
        (append (' '::[])
          (append (op_translate_aug op) (append (' '::[]) (pretty_expr e)))))))::[]

(** val emit_array_set : ident -> expr -> expr -> char list **)

let emit_array_set arr i v =
  append arr
    (append ('['::[])
      (append (pretty_expr i)
        (append (']'::(' '::('<'::('-'::(' '::[]))))) (pretty_expr v))))

(** val acceptable_array_set_emissions :
    ident -> expr -> expr -> char list list **)

let acceptable_array_set_emissions arr i v =
  (append arr
    (append ('['::[])
      (append (pretty_expr i)
        (append (']'::(' '::('<'::('-'::(' '::[]))))) (pretty_expr v)))))::(
    (append
      ('s'::('u'::('b'::('s'::('c'::('r'::('i'::('p'::('t'::('_'::('s'::('e'::('t'::(' '::[]))))))))))))))
      (append arr
        (append (' '::[])
          (append (pretty_expr i) (append (' '::[]) (pretty_expr v))))))::[])

(** val seq_sep : char list **)

let seq_sep =
  append (';'::[]) ('\n'::[])

(** val exc_to_string : whyml_exc -> char list **)

let exc_to_string = function
| ExcReturn ->
  'P'::('y'::('C'::('S'::('L'::('_'::('R'::('e'::('t'::('u'::('r'::('n'::[])))))))))))
| ExcBreak ->
  'P'::('y'::('C'::('S'::('L'::('_'::('B'::('r'::('e'::('a'::('k'::[]))))))))))
| ExcContinue ->
  'P'::('y'::('C'::('S'::('L'::('_'::('C'::('o'::('n'::('t'::('i'::('n'::('u'::('e'::[])))))))))))))
| ExcNamed name -> name

(** val emit_raise : whyml_exc -> char list **)

let emit_raise exc =
  append ('r'::('a'::('i'::('s'::('e'::(' '::[])))))) (exc_to_string exc)

(** val acceptable_raise_emissions : whyml_exc -> char list list **)

let acceptable_raise_emissions exc =
  (append ('r'::('a'::('i'::('s'::('e'::(' '::[])))))) (exc_to_string exc))::[]

(** val emit_label : ident -> char list **)

let emit_label l =
  append ('l'::('a'::('b'::('e'::('l'::(' '::[]))))))
    (append l (' '::('i'::('n'::[]))))

(** val acceptable_label_emissions : ident -> char list list **)

let acceptable_label_emissions l =
  (append ('l'::('a'::('b'::('e'::('l'::(' '::[]))))))
    (append l (' '::('i'::('n'::[])))))::[]

(** val emit_assert : contract_expr -> char list -> char list **)

let emit_assert _ _ =
  '('::(')'::[])

(** val acceptable_assert_emissions :
    contract_expr -> char list -> char list list **)

let acceptable_assert_emissions _ _ =
  ('('::(')'::[]))::[]

(** val newline : char list **)

let newline =
  '\n'::[]

(** val pretty_contract_expr : contract_expr -> char list **)

let rec pretty_contract_expr = function
| CInt n -> z_to_string n
| CVar x -> x
| CResult -> 'r'::('e'::('s'::('u'::('l'::('t'::[])))))
| CLength a ->
  append ('('::('l'::('e'::('n'::('g'::('t'::('h'::(' '::[]))))))))
    (append a (')'::[]))
| CSubscript (a, i) ->
  append a (append ('['::[]) (append (pretty_contract_expr i) (']'::[])))
| COld e ->
  append ('('::('o'::('l'::('d'::(' '::[])))))
    (append (pretty_contract_expr e) (')'::[]))
| CBinOp (op, e1, e2) ->
  append ('('::[])
    (append (pretty_contract_expr e1)
      (append (' '::[])
        (append (pretty_binop op)
          (append (' '::[]) (append (pretty_contract_expr e2) (')'::[]))))))
| CNeg e ->
  append ('('::('-'::(' '::[]))) (append (pretty_contract_expr e) (')'::[]))
| CEq (e1, e2) ->
  append ('('::[])
    (append (pretty_contract_expr e1)
      (append (' '::('='::(' '::[])))
        (append (pretty_contract_expr e2) (')'::[]))))
| CNe (e1, e2) ->
  append ('('::[])
    (append (pretty_contract_expr e1)
      (append (' '::('<'::('>'::(' '::[]))))
        (append (pretty_contract_expr e2) (')'::[]))))
| CLt (e1, e2) ->
  append ('('::[])
    (append (pretty_contract_expr e1)
      (append (' '::('<'::(' '::[])))
        (append (pretty_contract_expr e2) (')'::[]))))
| CLe (e1, e2) ->
  append ('('::[])
    (append (pretty_contract_expr e1)
      (append (' '::('<'::('='::(' '::[]))))
        (append (pretty_contract_expr e2) (')'::[]))))
| CGt (e1, e2) ->
  append ('('::[])
    (append (pretty_contract_expr e1)
      (append (' '::('>'::(' '::[])))
        (append (pretty_contract_expr e2) (')'::[]))))
| CGe (e1, e2) ->
  append ('('::[])
    (append (pretty_contract_expr e1)
      (append (' '::('>'::('='::(' '::[]))))
        (append (pretty_contract_expr e2) (')'::[]))))
| CAnd (e1, e2) ->
  append ('('::[])
    (append (pretty_contract_expr e1)
      (append (' '::('&'::('&'::(' '::[]))))
        (append (pretty_contract_expr e2) (')'::[]))))
| COr (e1, e2) ->
  append ('('::[])
    (append (pretty_contract_expr e1)
      (append (' '::('|'::('|'::(' '::[]))))
        (append (pretty_contract_expr e2) (')'::[]))))
| CNot e ->
  append ('('::('n'::('o'::('t'::(' '::[])))))
    (append (pretty_contract_expr e) (')'::[]))
| CImplies (e1, e2) ->
  append ('('::[])
    (append (pretty_contract_expr e1)
      (append (' '::('-'::('>'::(' '::[]))))
        (append (pretty_contract_expr e2) (')'::[]))))
| CIff (e1, e2) ->
  append ('('::[])
    (append (pretty_contract_expr e1)
      (append (' '::('<'::('-'::('>'::(' '::[])))))
        (append (pretty_contract_expr e2) (')'::[]))))
| CForall (x, body) ->
  append ('('::('f'::('o'::('r'::('a'::('l'::('l'::(' '::[]))))))))
    (append x
      (append (' '::(':'::(' '::('i'::('n'::('t'::('.'::(' '::[]))))))))
        (append (pretty_contract_expr body) (')'::[]))))
| CExists (x, body) ->
  append ('('::('e'::('x'::('i'::('s'::('t'::('s'::(' '::[]))))))))
    (append x
      (append (' '::(':'::(' '::('i'::('n'::('t'::('.'::(' '::[]))))))))
        (append (pretty_contract_expr body) (')'::[]))))
| CBoolLit b ->
  if b
  then 't'::('r'::('u'::('e'::[])))
  else 'f'::('a'::('l'::('s'::('e'::[]))))
| CNoneLit -> 'N'::('o'::('n'::('e'::[])))
| CStringLit s -> append ('"'::[]) (append s ('"'::[]))
| _ -> '?'::('c'::('o'::('n'::('t'::('r'::('a'::('c'::('t'::('?'::[])))))))))

(** val emit_if :
    assign_state -> expr -> whyml_stmt -> whyml_stmt -> (assign_state ->
    whyml_stmt -> char list) -> char list **)

let emit_if s cond w_then w_else emit =
  append ('i'::('f'::(' '::[])))
    (append (pretty_expr cond)
      (append
        (' '::('t'::('h'::('e'::('n'::(' '::('b'::('e'::('g'::('i'::('n'::[])))))))))))
        (append newline
          (append (emit s w_then)
            (append newline
              (append
                ('e'::('n'::('d'::(' '::('e'::('l'::('s'::('e'::(' '::('b'::('e'::('g'::('i'::('n'::[]))))))))))))))
                (append newline
                  (append (emit s w_else)
                    (append newline ('e'::('n'::('d'::[]))))))))))))

(** val acceptable_if_emissions :
    assign_state -> expr -> whyml_stmt -> whyml_stmt -> (assign_state ->
    whyml_stmt -> char list) -> char list list **)

let acceptable_if_emissions s cond w_then w_else emit =
  (append ('i'::('f'::(' '::[])))
    (append (pretty_expr cond)
      (append
        (' '::('t'::('h'::('e'::('n'::(' '::('b'::('e'::('g'::('i'::('n'::[])))))))))))
        (append newline
          (append (emit s w_then)
            (append newline
              (append
                ('e'::('n'::('d'::(' '::('e'::('l'::('s'::('e'::(' '::('b'::('e'::('g'::('i'::('n'::[]))))))))))))))
                (append newline
                  (append (emit s w_else)
                    (append newline ('e'::('n'::('d'::[])))))))))))))::(
    (append ('i'::('f'::(' '::[])))
      (append (pretty_expr cond)
        (append
          (' '::('t'::('h'::('e'::('n'::(' '::('b'::('e'::('g'::('i'::('n'::[])))))))))))
          (append newline
            (append (emit s w_then) (append newline ('e'::('n'::('d'::[])))))))))::(
    (append ('i'::('f'::(' '::[])))
      (append (pretty_expr cond)
        (append
          (' '::('t'::('h'::('e'::('n'::(' '::('b'::('e'::('g'::('i'::('n'::[])))))))))))
          (append newline
            (append (emit s w_then)
              (append newline
                (append
                  ('e'::('n'::('d'::(' '::('e'::('l'::('s'::('e'::(' '::('b'::('e'::('g'::('i'::('n'::[]))))))))))))))
                  (append newline
                    (append (' '::(' '::('0'::[])))
                      (append newline ('e'::('n'::('d'::[])))))))))))))::[]))

(** val emit_while :
    assign_state -> contract_expr list -> contract_expr list -> expr ->
    whyml_stmt -> (assign_state -> whyml_stmt -> char list) -> char list **)

let emit_while s invs vars cond body emit =
  append ('w'::('h'::('i'::('l'::('e'::(' '::[]))))))
    (append (pretty_expr cond)
      (append (' '::('d'::('o'::[])))
        (append newline
          (append
            ('i'::('n'::('v'::('a'::('r'::('i'::('a'::('n'::('t'::(' '::('{'::(' '::[]))))))))))))
            (append (pretty_contract_expr (c_conj invs))
              (append (' '::('}'::[]))
                (append newline
                  (append
                    ('v'::('a'::('r'::('i'::('a'::('n'::('t'::(' '::('{'::(' '::[]))))))))))
                    (append (pretty_contract_expr (c_first vars))
                      (append (' '::('}'::[]))
                        (append newline
                          (append (emit s body)
                            (append newline ('d'::('o'::('n'::('e'::[])))))))))))))))))

(** val acceptable_while_emissions :
    assign_state -> contract_expr list -> contract_expr list -> expr ->
    whyml_stmt -> (assign_state -> whyml_stmt -> char list) -> char list list **)

let acceptable_while_emissions s invs vars cond body emit =
  (append ('w'::('h'::('i'::('l'::('e'::(' '::[]))))))
    (append (pretty_expr cond)
      (append (' '::('d'::('o'::[])))
        (append newline
          (append
            ('i'::('n'::('v'::('a'::('r'::('i'::('a'::('n'::('t'::(' '::('{'::(' '::[]))))))))))))
            (append (pretty_contract_expr (c_conj invs))
              (append (' '::('}'::[]))
                (append newline
                  (append
                    ('v'::('a'::('r'::('i'::('a'::('n'::('t'::(' '::('{'::(' '::[]))))))))))
                    (append (pretty_contract_expr (c_first vars))
                      (append (' '::('}'::[]))
                        (append newline
                          (append (emit s body)
                            (append newline ('d'::('o'::('n'::('e'::[]))))))))))))))))))::[]

(** val emit_try_catch :
    assign_state -> whyml_stmt -> ident -> whyml_stmt -> (assign_state ->
    whyml_stmt -> char list) -> char list **)

let emit_try_catch s body exc handler emit =
  append ('t'::('r'::('y'::[])))
    (append newline
      (append (emit s body)
        (append newline
          (append ('w'::('i'::('t'::('h'::(' '::[])))))
            (append exc
              (append (' '::('-'::('>'::(' '::[]))))
                (append newline
                  (append (emit s handler)
                    (append newline ('e'::('n'::('d'::[]))))))))))))

(** val acceptable_try_catch_emissions :
    assign_state -> whyml_stmt -> ident -> whyml_stmt -> (assign_state ->
    whyml_stmt -> char list) -> char list list **)

let acceptable_try_catch_emissions s body exc handler emit =
  (append ('t'::('r'::('y'::[])))
    (append newline
      (append (emit s body)
        (append newline
          (append ('w'::('i'::('t'::('h'::(' '::[])))))
            (append exc
              (append (' '::('-'::('>'::(' '::[]))))
                (append newline
                  (append (emit s handler)
                    (append newline ('e'::('n'::('d'::[])))))))))))))::[]

(** val emit_ghost_decl : ident -> ghost_type -> ghost_expr -> char list **)

let emit_ghost_decl x t e =
  let val0 = pretty_contract_expr e in
  (match t with
   | GTArray ->
     append
       ('l'::('e'::('t'::(' '::('g'::('h'::('o'::('s'::('t'::(' '::[]))))))))))
       (append x
         (append (' '::('='::(' '::[])))
           (append val0 (' '::('i'::('n'::[]))))))
   | _ ->
     append
       ('l'::('e'::('t'::(' '::('g'::('h'::('o'::('s'::('t'::(' '::[]))))))))))
       (append x
         (append (' '::('='::(' '::('r'::('e'::('f'::(' '::[])))))))
           (append val0 (' '::('i'::('n'::[])))))))

(** val acceptable_ghost_decl_emissions :
    ident -> ghost_type -> ghost_expr -> char list list **)

let acceptable_ghost_decl_emissions x _ e =
  let val0 = pretty_contract_expr e in
  (append
    ('l'::('e'::('t'::(' '::('g'::('h'::('o'::('s'::('t'::(' '::[]))))))))))
    (append x
      (append (' '::('='::(' '::[]))) (append val0 (' '::('i'::('n'::[])))))))::(
  (append
    ('l'::('e'::('t'::(' '::('g'::('h'::('o'::('s'::('t'::(' '::[]))))))))))
    (append x
      (append (' '::('='::(' '::('r'::('e'::('f'::(' '::[])))))))
        (append val0 (' '::('i'::('n'::[])))))))::[])

(** val aug_op_str : aug_op -> char list **)

let aug_op_str = function
| AugAdd -> '+'::[]
| AugSub -> '-'::[]
| AugMul -> '*'::[]

(** val emit_ghost_assign :
    ident -> ghost_type -> aug_op -> ghost_expr -> char list **)

let emit_ghost_assign x t op e =
  let val0 = pretty_contract_expr e in
  (match t with
   | GTInt ->
     append ('g'::('h'::('o'::('s'::('t'::(' '::[]))))))
       (append x
         (append (' '::(':'::('='::(' '::('!'::[])))))
           (append x
             (append (' '::[])
               (append (aug_op_str op) (append (' '::[]) val0))))))
   | GTArray ->
     append ('g'::('h'::('o'::('s'::('t'::(' '::[]))))))
       (append x (append (' '::('<'::('-'::(' '::[])))) val0))
   | GTList ->
     (match op with
      | AugAdd ->
        append ('g'::('h'::('o'::('s'::('t'::(' '::[]))))))
          (append x
            (append
              (' '::(':'::('='::(' '::('('::('C'::('o'::('n'::('s'::(' '::[]))))))))))
              (append val0 (append (' '::('!'::[])) (append x (')'::[]))))))
      | _ ->
        append ('g'::('h'::('o'::('s'::('t'::(' '::[]))))))
          (append x (append (' '::(':'::('='::(' '::[])))) val0)))
   | GTSet ->
     (match op with
      | AugAdd ->
        append ('g'::('h'::('o'::('s'::('t'::(' '::[]))))))
          (append x
            (append
              (' '::(':'::('='::(' '::('('::('M'::('a'::('p'::('.'::('s'::('e'::('t'::(' '::('!'::[]))))))))))))))
              (append x
                (append (' '::[])
                  (append val0 (' '::('t'::('r'::('u'::('e'::(')'::[])))))))))))
      | _ ->
        append ('g'::('h'::('o'::('s'::('t'::(' '::[]))))))
          (append x (append (' '::(':'::('='::(' '::[])))) val0)))
   | _ ->
     append ('g'::('h'::('o'::('s'::('t'::(' '::[]))))))
       (append x (append (' '::(':'::('='::(' '::[])))) val0)))

(** val acceptable_ghost_assign_emissions :
    ident -> ghost_type -> aug_op -> ghost_expr -> char list list **)

let acceptable_ghost_assign_emissions x _ _ e =
  let val0 = pretty_contract_expr e in
  (append ('g'::('h'::('o'::('s'::('t'::(' '::[]))))))
    (append x
      (append (' '::(':'::('='::(' '::('!'::[])))))
        (append x (append (' '::('+'::(' '::[]))) val0)))))::((append
                                                                ('g'::('h'::('o'::('s'::('t'::(' '::[]))))))
                                                                (append x
                                                                  (append
                                                                    (' '::(':'::('='::(' '::('!'::[])))))
                                                                    (append x
                                                                    (append
                                                                    (' '::('-'::(' '::[])))
                                                                    val0)))))::(
  (append ('g'::('h'::('o'::('s'::('t'::(' '::[]))))))
    (append x
      (append (' '::(':'::('='::(' '::('!'::[])))))
        (append x (append (' '::('*'::(' '::[]))) val0)))))::((append
                                                                ('g'::('h'::('o'::('s'::('t'::(' '::[]))))))
                                                                (append x
                                                                  (append
                                                                    (' '::('<'::('-'::(' '::[]))))
                                                                    val0)))::(
  (append ('g'::('h'::('o'::('s'::('t'::(' '::[]))))))
    (append x
      (append
        (' '::(':'::('='::(' '::('('::('C'::('o'::('n'::('s'::(' '::[]))))))))))
        (append val0 (append (' '::('!'::[])) (append x (')'::[])))))))::(
  (append ('g'::('h'::('o'::('s'::('t'::(' '::[]))))))
    (append x
      (append
        (' '::(':'::('='::(' '::('('::('M'::('a'::('p'::('.'::('s'::('e'::('t'::(' '::('!'::[]))))))))))))))
        (append x
          (append (' '::[])
            (append val0 (' '::('t'::('r'::('u'::('e'::(')'::[]))))))))))))::(
  (append ('g'::('h'::('o'::('s'::('t'::(' '::[]))))))
    (append x (append (' '::(':'::('='::(' '::[])))) val0)))::[]))))))

(** val emit_stmt_full_complete : assign_state -> whyml_stmt -> char list **)

let rec emit_stmt_full_complete s = function
| WSkip -> '('::(')'::[])
| WAssign (x, e) -> emit_assign s x e
| WAugAssign (x, op, e) -> emit_aug_assign x op e
| WArraySet (arr, i, v) -> emit_array_set arr i v
| WSeq (w1, w2) ->
  append (emit_stmt_full_complete s w1)
    (append seq_sep (emit_stmt_full_complete s w2))
| WIf (cond, t, f) ->
  append ('i'::('f'::(' '::[])))
    (append (pretty_expr cond)
      (append
        (' '::('t'::('h'::('e'::('n'::(' '::('b'::('e'::('g'::('i'::('n'::[])))))))))))
        (append newline
          (append (emit_stmt_full_complete s t)
            (append newline
              (append
                ('e'::('n'::('d'::(' '::('e'::('l'::('s'::('e'::(' '::('b'::('e'::('g'::('i'::('n'::[]))))))))))))))
                (append newline
                  (append (emit_stmt_full_complete s f)
                    (append newline ('e'::('n'::('d'::[]))))))))))))
| WWhile (invs, vars, cond, body) ->
  append ('w'::('h'::('i'::('l'::('e'::(' '::[]))))))
    (append (pretty_expr cond)
      (append (' '::('d'::('o'::[])))
        (append newline
          (append
            ('i'::('n'::('v'::('a'::('r'::('i'::('a'::('n'::('t'::(' '::('{'::(' '::[]))))))))))))
            (append (pretty_contract_expr (c_conj invs))
              (append (' '::('}'::[]))
                (append newline
                  (append
                    ('v'::('a'::('r'::('i'::('a'::('n'::('t'::(' '::('{'::(' '::[]))))))))))
                    (append (pretty_contract_expr (c_first vars))
                      (append (' '::('}'::[]))
                        (append newline
                          (append (emit_stmt_full_complete s body)
                            (append newline ('d'::('o'::('n'::('e'::[])))))))))))))))))
| WRaise exc -> emit_raise exc
| WTryCatch (body, exc, handler) ->
  append ('t'::('r'::('y'::[])))
    (append newline
      (append (emit_stmt_full_complete s body)
        (append newline
          (append ('w'::('i'::('t'::('h'::(' '::[])))))
            (append exc
              (append (' '::('-'::('>'::(' '::[]))))
                (append newline
                  (append (emit_stmt_full_complete s handler)
                    (append newline ('e'::('n'::('d'::[]))))))))))))
| WGhostDecl (x, t, e) -> emit_ghost_decl x t e
| WGhostAssign (x, t, op, e) -> emit_ghost_assign x t op e
| WLabel l -> emit_label l
| WAssert (cond, msg) -> emit_assert cond msg
| WAssume cond ->
  append ('a'::('s'::('s'::('u'::('m'::('e'::(' '::('{'::(' '::[])))))))))
    (append (pretty_contract_expr cond) (' '::('}'::[])))

(** val acceptable_emit : assign_state -> stmt -> char list list **)

let acceptable_emit state s = match s with
| SAssign (x, e) -> acceptable_assign_emissions state x e
| SAugAssign (x, op, e) -> acceptable_aug_assign_emissions x op e
| SArraySet (arr, i, v) -> acceptable_array_set_emissions arr i v
| SSeq (s1, s2) ->
  (append (emit_stmt_full_complete state (gen s1))
    (append seq_sep (emit_stmt_full_complete state (gen s2))))::[]
| SIf (cond, t, f) ->
  acceptable_if_emissions state cond (gen t) (gen f) emit_stmt_full_complete
| SWhile (inv, var, cond, body) ->
  acceptable_while_emissions state (inv::[]) (var::[]) cond (gen body)
    emit_stmt_full_complete
| SFor (_, _, _, _, _, _) -> (emit_stmt_full_complete state (gen s))::[]
| SReturn e ->
  (append
    (emit_assign state ('\\'::('r'::('e'::('s'::('u'::('l'::('t'::[]))))))) e)
    (append seq_sep
      ('r'::('a'::('i'::('s'::('e'::(' '::('P'::('y'::('C'::('S'::('L'::('_'::('R'::('e'::('t'::('u'::('r'::('n'::[]))))))))))))))))))))::[]
| SContinue -> acceptable_raise_emissions ExcContinue
| SBreak -> acceptable_raise_emissions ExcBreak
| SAssert (cond, msg) -> acceptable_assert_emissions cond msg
| SGhostDecl (x, t, e) -> acceptable_ghost_decl_emissions x t e
| SGhostAssign (x, t, op, e) -> acceptable_ghost_assign_emissions x t op e
| SLabel l -> acceptable_label_emissions l
| SRaise exc -> acceptable_raise_emissions (ExcNamed exc)
| STryCatch (body, exc, h) ->
  acceptable_try_catch_emissions state (gen body) exc (gen h)
    emit_stmt_full_complete
| SCritical (_, body) -> (emit_stmt_full_complete state (gen body))::[]
| SThreadEntry body -> (emit_stmt_full_complete state (gen body))::[]
| _ -> acceptable_skip_emissions

type aware_state = { aw_shared_vars : ident list;
                     aw_declared_refs : ident list;
                     aw_local_refs : ident list;
                     aw_array_locals : ident list;
                     aw_bounded_int : char list option }

(** val aware_in : ident -> ident list -> bool **)

let aware_in x xs =
  existsb (eqb x) xs

(** val pretty_expr_state : aware_state -> expr -> char list **)

let rec pretty_expr_state s = function
| EInt n -> z_to_string n
| EVar x ->
  if aware_in x s.aw_local_refs
  then append ('!'::[]) x
  else if aware_in x s.aw_shared_vars then append ('!'::[]) x else x
| ESubscript (a, i) ->
  if aware_in a s.aw_array_locals
  then append a (append ('['::[]) (append (pretty_expr_state s i) (']'::[])))
  else append
         ('('::('s'::('u'::('b'::('s'::('c'::('r'::('i'::('p'::('t'::('_'::('g'::('e'::('t'::(' '::[])))))))))))))))
         (append a
           (append (' '::[]) (append (pretty_expr_state s i) (')'::[]))))
| ELen a ->
  if aware_in a s.aw_array_locals
  then append
         ('('::('A'::('r'::('r'::('a'::('y'::('.'::('l'::('e'::('n'::('g'::('t'::('h'::(' '::[]))))))))))))))
         (append a (')'::[]))
  else append
         ('('::('i'::('t'::('e'::('r'::('_'::('l'::('e'::('n'::('g'::('t'::('h'::(' '::[])))))))))))))
         (append a (')'::[]))
| EBinOp (op, e1, e2) ->
  (match op with
   | OpDiv ->
     append
       ('('::('p'::('y'::('c'::('s'::('l'::('_'::('d'::('i'::('v'::(' '::[])))))))))))
       (append (pretty_expr_state s e1)
         (append (' '::[]) (append (pretty_expr_state s e2) (')'::[]))))
   | _ ->
     append ('('::[])
       (append (pretty_expr_state s e1)
         (append (' '::[])
           (append (pretty_binop op)
             (append (' '::[]) (append (pretty_expr_state s e2) (')'::[])))))))
| ENeg e1 ->
  append ('('::('-'::(' '::[]))) (append (pretty_expr_state s e1) (')'::[]))
| ECmp (op, e1, e2) ->
  append ('('::[])
    (append (pretty_expr_state s e1)
      (append (' '::[])
        (append (pretty_cmpop op)
          (append (' '::[]) (append (pretty_expr_state s e2) (')'::[]))))))
| EFieldGet (obj, f) -> append obj (append ('.'::[]) f)
| ECall (func, args) ->
  append func
    (append ('('::[])
      (append
        (let rec args_str = function
         | [] -> []
         | x::rest ->
           (match rest with
            | [] -> pretty_expr_state s x
            | _::_ ->
              append (pretty_expr_state s x)
                (append (','::(' '::[])) (args_str rest)))
         in args_str args) (')'::[])))

(** val to_bool_state : aware_state -> expr -> char list **)

let to_bool_state s e = match e with
| ECmp (_, _, _) -> pretty_expr_state s e
| _ ->
  append ('('::[])
    (append (pretty_expr_state s e)
      (' '::('<'::('>'::(' '::('0'::(')'::[])))))))

(** val pretty_contract_expr_state :
    aware_state -> contract_expr -> char list **)

let rec pretty_contract_expr_state s = function
| CInt n -> z_to_string n
| CVar x ->
  if aware_in x s.aw_local_refs
  then append ('!'::[]) x
  else if aware_in x s.aw_shared_vars then append ('!'::[]) x else x
| CResult -> 'r'::('e'::('s'::('u'::('l'::('t'::[])))))
| CLength a ->
  if aware_in a s.aw_array_locals
  then append
         ('('::('A'::('r'::('r'::('a'::('y'::('.'::('l'::('e'::('n'::('g'::('t'::('h'::(' '::[]))))))))))))))
         (append a (')'::[]))
  else append
         ('('::('i'::('t'::('e'::('r'::('_'::('l'::('e'::('n'::('g'::('t'::('h'::(' '::[])))))))))))))
         (append a (')'::[]))
| CSubscript (a, i) ->
  append a
    (append ('['::[]) (append (pretty_contract_expr_state s i) (']'::[])))
| COld e ->
  append ('('::('o'::('l'::('d'::(' '::[])))))
    (append (pretty_contract_expr_state s e) (')'::[]))
| CBinOp (op, e1, e2) ->
  (match op with
   | OpDiv ->
     append ('('::('d'::('i'::('v'::(' '::[])))))
       (append (pretty_contract_expr_state s e1)
         (append (' '::[])
           (append (pretty_contract_expr_state s e2) (')'::[]))))
   | _ ->
     append ('('::[])
       (append (pretty_contract_expr_state s e1)
         (append (' '::[])
           (append (pretty_binop op)
             (append (' '::[])
               (append (pretty_contract_expr_state s e2) (')'::[])))))))
| CNeg e ->
  append ('('::('-'::(' '::[])))
    (append (pretty_contract_expr_state s e) (')'::[]))
| CEq (e1, e2) ->
  append ('('::[])
    (append (pretty_contract_expr_state s e1)
      (append (' '::('='::(' '::[])))
        (append (pretty_contract_expr_state s e2) (')'::[]))))
| CNe (e1, e2) ->
  append ('('::[])
    (append (pretty_contract_expr_state s e1)
      (append (' '::('<'::('>'::(' '::[]))))
        (append (pretty_contract_expr_state s e2) (')'::[]))))
| CLt (e1, e2) ->
  append ('('::[])
    (append (pretty_contract_expr_state s e1)
      (append (' '::('<'::(' '::[])))
        (append (pretty_contract_expr_state s e2) (')'::[]))))
| CLe (e1, e2) ->
  append ('('::[])
    (append (pretty_contract_expr_state s e1)
      (append (' '::('<'::('='::(' '::[]))))
        (append (pretty_contract_expr_state s e2) (')'::[]))))
| CGt (e1, e2) ->
  append ('('::[])
    (append (pretty_contract_expr_state s e1)
      (append (' '::('>'::(' '::[])))
        (append (pretty_contract_expr_state s e2) (')'::[]))))
| CGe (e1, e2) ->
  append ('('::[])
    (append (pretty_contract_expr_state s e1)
      (append (' '::('>'::('='::(' '::[]))))
        (append (pretty_contract_expr_state s e2) (')'::[]))))
| CAnd (e1, e2) ->
  append ('('::[])
    (append (pretty_contract_expr_state s e1)
      (append (' '::('&'::('&'::(' '::[]))))
        (append (pretty_contract_expr_state s e2) (')'::[]))))
| COr (e1, e2) ->
  append ('('::[])
    (append (pretty_contract_expr_state s e1)
      (append (' '::('|'::('|'::(' '::[]))))
        (append (pretty_contract_expr_state s e2) (')'::[]))))
| CNot e ->
  append ('('::('n'::('o'::('t'::(' '::[])))))
    (append (pretty_contract_expr_state s e) (')'::[]))
| CImplies (e1, e2) ->
  append ('('::[])
    (append (pretty_contract_expr_state s e1)
      (append (' '::('-'::('>'::(' '::[]))))
        (append (pretty_contract_expr_state s e2) (')'::[]))))
| CIff (e1, e2) ->
  append ('('::[])
    (append (pretty_contract_expr_state s e1)
      (append (' '::('<'::('-'::('>'::(' '::[])))))
        (append (pretty_contract_expr_state s e2) (')'::[]))))
| CForall (x, body) ->
  append ('('::('f'::('o'::('r'::('a'::('l'::('l'::(' '::[]))))))))
    (append x
      (append (' '::(':'::(' '::('i'::('n'::('t'::('.'::(' '::[]))))))))
        (append (pretty_contract_expr_state s body) (')'::[]))))
| CExists (x, body) ->
  append ('('::('e'::('x'::('i'::('s'::('t'::('s'::(' '::[]))))))))
    (append x
      (append (' '::(':'::(' '::('i'::('n'::('t'::('.'::(' '::[]))))))))
        (append (pretty_contract_expr_state s body) (')'::[]))))
| CBoolLit b ->
  if b
  then 't'::('r'::('u'::('e'::[])))
  else 'f'::('a'::('l'::('s'::('e'::[]))))
| CNoneLit -> 'N'::('o'::('n'::('e'::[])))
| CStringLit s0 -> append ('"'::[]) (append s0 ('"'::[]))
| CGMapEmpty ->
  '('::('c'::('o'::('n'::('s'::('t'::(' '::('('::('N'::('o'::('n'::('e'::(':'::(' '::('o'::('p'::('t'::('i'::('o'::('n'::(' '::('i'::('n'::('t'::(')'::(')'::[])))))))))))))))))))))))))
| CGNil -> 'N'::('i'::('l'::[]))
| CGCons (h, t) ->
  append ('('::('C'::('o'::('n'::('s'::(' '::[]))))))
    (append (pretty_contract_expr_state s h)
      (append (' '::[]) (append (pretty_contract_expr_state s t) (')'::[]))))
| CGSetEmpty ->
  '('::('c'::('o'::('n'::('s'::('t'::(' '::('f'::('a'::('l'::('s'::('e'::(')'::[]))))))))))))
| CGMkTuple2 (a, b) ->
  append ('('::[])
    (append (pretty_contract_expr_state s a)
      (append (','::(' '::[]))
        (append (pretty_contract_expr_state s b) (')'::[]))))
| CGMkTuple3 (a, b, c0) ->
  append ('('::[])
    (append (pretty_contract_expr_state s a)
      (append (','::(' '::[]))
        (append (pretty_contract_expr_state s b)
          (append (','::(' '::[]))
            (append (pretty_contract_expr_state s c0) (')'::[]))))))
| CGMkTuple4 (a, b, c0, d) ->
  append ('('::[])
    (append (pretty_contract_expr_state s a)
      (append (','::(' '::[]))
        (append (pretty_contract_expr_state s b)
          (append (','::(' '::[]))
            (append (pretty_contract_expr_state s c0)
              (append (','::(' '::[]))
                (append (pretty_contract_expr_state s d) (')'::[]))))))))
| CGFst t ->
  append ('('::('f'::('s'::('t'::(' '::[])))))
    (append (pretty_contract_expr_state s t) (')'::[]))
| CGSnd t ->
  append ('('::('s'::('n'::('d'::(' '::[])))))
    (append (pretty_contract_expr_state s t) (')'::[]))
| CGMake (n, v) ->
  append
    ('('::('A'::('r'::('r'::('a'::('y'::('.'::('m'::('a'::('k'::('e'::(' '::[]))))))))))))
    (append (pretty_contract_expr_state s n)
      (append (' '::[]) (append (pretty_contract_expr_state s v) (')'::[]))))
| CGCopy a ->
  append
    ('('::('A'::('r'::('r'::('a'::('y'::('.'::('c'::('o'::('p'::('y'::(' '::[]))))))))))))
    (append a (')'::[]))
| CGCopyRange (a, lo, hi) ->
  append
    ('('::('A'::('r'::('r'::('a'::('y'::('.'::('s'::('u'::('b'::(' '::[])))))))))))
    (append a
      (append (' '::[])
        (append (pretty_contract_expr_state s lo)
          (append (' '::('('::[]))
            (append (pretty_contract_expr_state s hi)
              (append (' '::('-'::(' '::[])))
                (append (pretty_contract_expr_state s lo) (')'::(')'::[])))))))))
| _ -> '?'::('c'::('o'::('n'::('t'::('r'::('a'::('c'::('t'::('?'::[])))))))))

(** val is_bool_expr : expr -> bool **)

let is_bool_expr = function
| ECmp (_, _, _) -> true
| _ -> false

(** val coerce_int_rhs : aware_state -> expr -> char list **)

let coerce_int_rhs s e =
  if is_bool_expr e
  then append ('('::('i'::('f'::(' '::[]))))
         (append (pretty_expr_state s e)
           (' '::('t'::('h'::('e'::('n'::(' '::('1'::(' '::('e'::('l'::('s'::('e'::(' '::('0'::(')'::[]))))))))))))))))
  else pretty_expr_state s e

(** val nl : char list **)

let nl =
  '\n'::[]

(** val concat_with_sep : char list -> char list -> char list **)

let concat_with_sep body cont = match cont with
| [] -> body
| _::_ -> append body (append (';'::[]) (append nl cont))

(** val scope_body : char list -> char list **)

let scope_body cont = match cont with
| [] -> '('::(')'::[])
| _::_ -> cont

(** val emit_invariant_lines :
    aware_state -> contract_expr list -> char list **)

let rec emit_invariant_lines s = function
| [] -> []
| c::rest ->
  append
    ('i'::('n'::('v'::('a'::('r'::('i'::('a'::('n'::('t'::(' '::('{'::(' '::[]))))))))))))
    (append (pretty_contract_expr_state s c)
      (append (' '::('}'::[])) (append nl (emit_invariant_lines s rest))))

(** val emit_variant_lines :
    aware_state -> contract_expr list -> char list **)

let rec emit_variant_lines s = function
| [] -> []
| c::rest ->
  append
    ('v'::('a'::('r'::('i'::('a'::('n'::('t'::(' '::('{'::(' '::[]))))))))))
    (append (pretty_contract_expr_state s c)
      (append (' '::('}'::[])) (append nl (emit_variant_lines s rest))))

(** val emit_ghost_decl_aware :
    aware_state -> ident -> ghost_type -> ghost_expr -> char list **)

let emit_ghost_decl_aware s x t e =
  let val0 = pretty_contract_expr_state s e in
  (match t with
   | GTArray ->
     append
       ('l'::('e'::('t'::(' '::('g'::('h'::('o'::('s'::('t'::(' '::[]))))))))))
       (append x
         (append (' '::('='::(' '::[])))
           (append val0 (' '::('i'::('n'::[]))))))
   | GTList ->
     (match e with
      | CGNil ->
        append
          ('l'::('e'::('t'::(' '::('g'::('h'::('o'::('s'::('t'::(' '::[]))))))))))
          (append x
            (' '::('='::(' '::('r'::('e'::('f'::(' '::('('::('N'::('i'::('l'::(':'::(' '::('l'::('i'::('s'::('t'::(' '::('i'::('n'::('t'::(')'::(' '::('i'::('n'::[]))))))))))))))))))))))))))
      | _ ->
        append
          ('l'::('e'::('t'::(' '::('g'::('h'::('o'::('s'::('t'::(' '::[]))))))))))
          (append x
            (append (' '::('='::(' '::('r'::('e'::('f'::(' '::[])))))))
              (append val0 (' '::('i'::('n'::[])))))))
   | _ ->
     append
       ('l'::('e'::('t'::(' '::('g'::('h'::('o'::('s'::('t'::(' '::[]))))))))))
       (append x
         (append (' '::('='::(' '::('r'::('e'::('f'::(' '::[])))))))
           (append val0 (' '::('i'::('n'::[])))))))

(** val emit_ghost_assign_aware :
    aware_state -> ident -> ghost_type -> aug_op -> ghost_expr -> char list **)

let emit_ghost_assign_aware s x t op e =
  let val0 = pretty_contract_expr_state s e in
  (match t with
   | GTInt ->
     append ('g'::('h'::('o'::('s'::('t'::(' '::[]))))))
       (append x
         (append (' '::(':'::('='::(' '::('!'::[])))))
           (append x
             (append (' '::[])
               (append (aug_op_str op) (append (' '::[]) val0))))))
   | GTArray ->
     append ('g'::('h'::('o'::('s'::('t'::(' '::[]))))))
       (append x (append (' '::('<'::('-'::(' '::[])))) val0))
   | GTDict ->
     (match op with
      | AugAdd ->
        (match e with
         | CGMkTuple2 (k, v) ->
           append ('g'::('h'::('o'::('s'::('t'::(' '::[]))))))
             (append x
               (append
                 (' '::(':'::('='::(' '::('('::('M'::('a'::('p'::('.'::('s'::('e'::('t'::(' '::('!'::[]))))))))))))))
                 (append x
                   (append (' '::[])
                     (append (pretty_contract_expr_state s k)
                       (append
                         (' '::('('::('S'::('o'::('m'::('e'::(' '::[])))))))
                         (append (pretty_contract_expr_state s v)
                           (')'::(')'::[])))))))))
         | _ ->
           append ('g'::('h'::('o'::('s'::('t'::(' '::[]))))))
             (append x (append (' '::(':'::('='::(' '::[])))) val0)))
      | _ ->
        append ('g'::('h'::('o'::('s'::('t'::(' '::[]))))))
          (append x (append (' '::(':'::('='::(' '::[])))) val0)))
   | GTList ->
     (match op with
      | AugAdd ->
        append ('g'::('h'::('o'::('s'::('t'::(' '::[]))))))
          (append x
            (append
              (' '::(':'::('='::(' '::('('::('C'::('o'::('n'::('s'::(' '::[]))))))))))
              (append val0 (append (' '::('!'::[])) (append x (')'::[]))))))
      | _ ->
        append ('g'::('h'::('o'::('s'::('t'::(' '::[]))))))
          (append x (append (' '::(':'::('='::(' '::[])))) val0)))
   | GTSet ->
     (match op with
      | AugAdd ->
        append ('g'::('h'::('o'::('s'::('t'::(' '::[]))))))
          (append x
            (append
              (' '::(':'::('='::(' '::('('::('M'::('a'::('p'::('.'::('s'::('e'::('t'::(' '::('!'::[]))))))))))))))
              (append x
                (append (' '::[])
                  (append val0 (' '::('t'::('r'::('u'::('e'::(')'::[])))))))))))
      | _ ->
        append ('g'::('h'::('o'::('s'::('t'::(' '::[]))))))
          (append x (append (' '::(':'::('='::(' '::[])))) val0)))
   | _ ->
     append ('g'::('h'::('o'::('s'::('t'::(' '::[]))))))
       (append x (append (' '::(':'::('='::(' '::[])))) val0)))

(** val emit_cont : aware_state -> whyml_stmt -> char list -> char list **)

let rec emit_cont s ws cont =
  match ws with
  | WSkip -> concat_with_sep ('('::(')'::[])) cont
  | WAssign (x, e) ->
    let rhs = coerce_int_rhs s e in
    if aware_in x s.aw_shared_vars
    then concat_with_sep
           (append x (append (' '::(':'::('='::(' '::[])))) rhs)) cont
    else if negb (aware_in x s.aw_declared_refs)
         then let prefix =
                match s.aw_bounded_int with
                | Some bits ->
                  append ('l'::('e'::('t'::(' '::[]))))
                    (append x
                      (append
                        (' '::('='::(' '::('r'::('e'::('f'::(' '::('('::[]))))))))
                        (append rhs
                          (append
                            (' '::(':'::(' '::('i'::('n'::('t'::[]))))))
                            (append bits
                              (append (')'::(' '::('i'::('n'::[])))) nl))))))
                | None ->
                  append ('l'::('e'::('t'::(' '::[]))))
                    (append x
                      (append
                        (' '::('='::(' '::('r'::('e'::('f'::(' '::[])))))))
                        (append rhs (append (' '::('i'::('n'::[]))) nl))))
              in
              append prefix (scope_body cont)
         else concat_with_sep
                (append x (append (' '::(':'::('='::(' '::[])))) rhs)) cont
  | WAugAssign (x, op, e) ->
    concat_with_sep
      (append x
        (append (' '::(':'::('='::(' '::('!'::[])))))
          (append x
            (append (' '::[])
              (append (op_translate_aug op)
                (append (' '::[]) (pretty_expr_state s e))))))) cont
  | WArraySet (a, i, v) ->
    let body =
      if aware_in a s.aw_array_locals
      then append a
             (append ('['::[])
               (append (pretty_expr_state s i)
                 (append (']'::(' '::('<'::('-'::(' '::[])))))
                   (pretty_expr_state s v))))
      else append
             ('s'::('u'::('b'::('s'::('c'::('r'::('i'::('p'::('t'::('_'::('s'::('e'::('t'::(' '::[]))))))))))))))
             (append a
               (append (' '::[])
                 (append (pretty_expr_state s i)
                   (append (' '::[]) (pretty_expr_state s v)))))
    in
    concat_with_sep body cont
  | WSeq (w1, w2) -> emit_cont s w1 (emit_cont s w2 cont)
  | WIf (c, t, f) ->
    let body =
      match f with
      | WSkip ->
        append ('i'::('f'::(' '::[])))
          (append (to_bool_state s c)
            (append
              (' '::('t'::('h'::('e'::('n'::(' '::('b'::('e'::('g'::('i'::('n'::[])))))))))))
              (append nl
                (append (emit_cont s t [])
                  (append nl ('e'::('n'::('d'::[]))))))))
      | _ ->
        append ('i'::('f'::(' '::[])))
          (append (to_bool_state s c)
            (append
              (' '::('t'::('h'::('e'::('n'::(' '::('b'::('e'::('g'::('i'::('n'::[])))))))))))
              (append nl
                (append (emit_cont s t [])
                  (append nl
                    (append
                      ('e'::('n'::('d'::(' '::('e'::('l'::('s'::('e'::(' '::('b'::('e'::('g'::('i'::('n'::[]))))))))))))))
                      (append nl
                        (append (emit_cont s f [])
                          (append nl ('e'::('n'::('d'::[]))))))))))))
    in
    concat_with_sep body cont
  | WWhile (invs, vars, c, body) ->
    concat_with_sep
      (append ('w'::('h'::('i'::('l'::('e'::(' '::[]))))))
        (append (to_bool_state s c)
          (append (' '::('d'::('o'::[])))
            (append nl
              (append (emit_invariant_lines s invs)
                (append (emit_variant_lines s vars)
                  (append (emit_cont s body [])
                    (append nl ('d'::('o'::('n'::('e'::[])))))))))))) cont
  | WRaise exc ->
    concat_with_sep
      (append ('r'::('a'::('i'::('s'::('e'::(' '::[]))))))
        (exc_to_string exc)) cont
  | WTryCatch (body, exc, handler) ->
    concat_with_sep
      (append ('t'::('r'::('y'::[])))
        (append nl
          (append (emit_cont s body [])
            (append nl
              (append ('w'::('i'::('t'::('h'::(' '::[])))))
                (append exc
                  (append (' '::('-'::('>'::(' '::[]))))
                    (append nl
                      (append (emit_cont s handler [])
                        (append nl ('e'::('n'::('d'::[]))))))))))))) cont
  | WGhostDecl (x, t, e) ->
    append (emit_ghost_decl_aware s x t e) (append nl (scope_body cont))
  | WGhostAssign (x, t, op, e) ->
    concat_with_sep (emit_ghost_assign_aware s x t op e) cont
  | WLabel l ->
    append ('l'::('a'::('b'::('e'::('l'::(' '::[]))))))
      (append l
        (append (' '::('i'::('n'::[]))) (append nl (scope_body cont))))
  | WAssert (cond, _) ->
    concat_with_sep
      (append
        ('a'::('s'::('s'::('e'::('r'::('t'::(' '::('{'::(' '::[])))))))))
        (append (pretty_contract_expr_state s cond) (' '::('}'::[])))) cont
  | WAssume cond ->
    concat_with_sep
      (append
        ('a'::('s'::('s'::('u'::('m'::('e'::(' '::('{'::(' '::[])))))))))
        (append (pretty_contract_expr_state s cond) (' '::('}'::[])))) cont

(** val emit_stmt_state_aware : aware_state -> whyml_stmt -> char list **)

let emit_stmt_state_aware s ws =
  emit_cont s ws []

(** val empty_aware_state : aware_state **)

let empty_aware_state =
  { aw_shared_vars = []; aw_declared_refs = []; aw_local_refs = [];
    aw_array_locals = []; aw_bounded_int = None }
