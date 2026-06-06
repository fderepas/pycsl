(* ir_driver.ml — Q4 U.4 driver: read Module 5 JSON IR, parse to
   json_value, run validate_ir + ir_to_stmt, print results.

   Compiles against the extracted Phase1b_IrToStmtExtract.ml.
   Uses Yojson for JSON parsing.

   Usage:
     ir_driver <case_id> <module5_json_file>

   Output (one TSV line):
     <case_id>\tvalid=<bool>\tir_to_stmt=<Some|None>\tnotes=<text>

   Invoked by bin/extraction-byte-diff-upward.sh per corpus case. *)

open IrToStmtExtract

(* ===== Conversions between OCaml strings and Rocq char list ===== *)

let to_char_list (s : string) : char list =
  let rec aux i acc =
    if i < 0 then acc else aux (i-1) (s.[i] :: acc)
  in aux (String.length s - 1) []

let of_char_list (cs : char list) : string =
  let buf = Buffer.create 64 in
  List.iter (Buffer.add_char buf) cs;
  Buffer.contents buf

(* ===== Yojson.Basic.t → json_value ===== *)

let rec of_yojson (y : Yojson.Basic.t) : json_value =
  match y with
  | `Null         -> JsonNull
  | `Bool b       -> JsonBool b
  | `Int n        -> JsonInt n
  | `Float f      -> JsonInt (int_of_float f)
  | `String s     -> JsonString (to_char_list s)
  | `List xs      -> JsonList (List.map of_yojson xs)
  | `Assoc kvs    ->
      JsonObject (List.map (fun (k, v) -> (to_char_list k, of_yojson v)) kvs)

(* ===== Print a short summary of an extracted stmt ===== *)

let rec stmt_kind (s : stmt) : string =
  match s with
  | SSkip                 -> "SSkip"
  | SAssign (_, _)        -> "SAssign"
  | SAugAssign (_, _, _)  -> "SAugAssign"
  | SArraySet (_, _, _)   -> "SArraySet"
  | SSeq (s1, s2)         ->
      Printf.sprintf "SSeq(%s,%s)" (stmt_kind s1) (stmt_kind s2)
  | SIf (_, _, _)         -> "SIf"
  | SWhile (_, _, _, _)   -> "SWhile"
  | SFor (_, _, _, _, _, _) -> "SFor"
  | SReturn _             -> "SReturn"
  | SContinue             -> "SContinue"
  | SBreak                -> "SBreak"
  | SAssert (_, _)        -> "SAssert"
  | STupleUnpack (_, _)   -> "STupleUnpack"
  | SGhostDecl (_, _, _)  -> "SGhostDecl"
  | SGhostAssign (_, _, _, _) -> "SGhostAssign"
  | SLabel _              -> "SLabel"
  | SRaise _              -> "SRaise"
  | STryCatch (_, _, _)   -> "STryCatch"
  | SFieldAssign (_, _, _) -> "SFieldAssign"
  | SFieldAugAssign (_, _, _, _) -> "SFieldAugAssign"
  | SCritical (_, _)      -> "SCritical"
  | SThreadEntry _        -> "SThreadEntry"

(* ===== Extract first function's body from a validated IR ===== *)

let lookup_field (k : string) (kvs : (char list * json_value) list)
    : json_value option =
  let rec aux = function
    | [] -> None
    | (ck, v) :: rest ->
        if of_char_list ck = k then Some v else aux rest
  in aux kvs

let first_function_body (ir : json_value) : json_value option =
  match ir with
  | JsonObject kvs ->
      (match lookup_field "functions" kvs with
       | Some (JsonList (f :: _)) ->
           (match f with
            | JsonObject fkvs -> lookup_field "body" fkvs
            | _ -> None)
       | _ -> None)
  | _ -> None

(* Find the FIRST stmt type in a JsonList of statements whose
   ir_to_stmt fails. Used for diagnostic when the converter
   returns None — tells us which constructor blocked. *)
let first_failing_stmt_type (body : json_value) : string =
  let rec stmt_type_of (s : json_value) : string =
    match s with
    | JsonObject kvs ->
        (match lookup_field "stmt" kvs with
         | Some (JsonString cs) -> of_char_list cs
         | _ -> "<no-stmt-field>")
    | _ -> "<not-object>"
  in
  match body with
  | JsonList xs ->
      let rec find_failing = function
        | [] -> "<empty-body>"
        | x :: rest ->
            match ir_to_stmt x with
            | Some _ -> find_failing rest
            | None -> stmt_type_of x
      in
      find_failing xs
  | _ -> stmt_type_of body

(* ===== Main ===== *)

let () =
  if Array.length Sys.argv <> 3 then begin
    Printf.eprintf "Usage: %s <case_id> <module5_json_file>\n" Sys.argv.(0);
    exit 2
  end;
  let case_id = Sys.argv.(1) in
  let json_path = Sys.argv.(2) in
  let yj =
    try Yojson.Basic.from_file json_path
    with e ->
      Printf.printf "%s\tvalid=false\tir_to_stmt=ERROR\tnotes=parse:%s\n"
        case_id (Printexc.to_string e);
      exit 0
  in
  let ir = of_yojson yj in
  let valid = validate_ir ir in
  if not valid then begin
    Printf.printf "%s\tvalid=false\tir_to_stmt=SKIP\tnotes=ir_invalid\n" case_id;
    exit 0
  end;
  match first_function_body ir with
  | None ->
      Printf.printf "%s\tvalid=true\tir_to_stmt=SKIP\tnotes=no_first_function_body\n" case_id
  | Some body ->
      (match ir_to_stmt body with
       | Some s ->
           Printf.printf "%s\tvalid=true\tir_to_stmt=Some(%s)\tnotes=ok\n"
             case_id (stmt_kind s)
       | None ->
           let blocker = first_failing_stmt_type body in
           Printf.printf "%s\tvalid=true\tir_to_stmt=None\tnotes=blocker:%s\n"
             case_id blocker)
