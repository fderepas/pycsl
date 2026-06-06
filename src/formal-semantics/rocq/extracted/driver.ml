(* driver.ml — OCaml driver for the extracted emit_stmt_full_complete.

   Compiles with the extracted Rocq code (EmitExtract.ml). For each
   hand-coded whyml_stmt test case, prints a TSV line:

     <case_id>\t<json-encoded-formal-output>

   The shell wrapper (bin/extraction-byte-diff.sh) compares these
   outputs to Module 6 Python output on equivalent inputs.

   Case IDs and inputs are documented in
   test-suite/extraction-byte-diff/cases.txt. *)

open EmitExtract

(* Conversion: OCaml string ↔ Rocq char list (extracted type). *)
let to_char_list (s : string) : char list =
  let rec aux i acc =
    if i < 0 then acc else aux (i-1) (s.[i] :: acc)
  in aux (String.length s - 1) []

let of_char_list (cs : char list) : string =
  let buf = Buffer.create 64 in
  List.iter (Buffer.add_char buf) cs;
  Buffer.contents buf

(* JSON-encode a string: escape backslash, double-quote, controls. *)
let json_str (s : string) : string =
  let buf = Buffer.create (String.length s + 2) in
  Buffer.add_char buf '"';
  String.iter (fun c ->
    match c with
    | '"'  -> Buffer.add_string buf "\\\""
    | '\\' -> Buffer.add_string buf "\\\\"
    | '\n' -> Buffer.add_string buf "\\n"
    | '\t' -> Buffer.add_string buf "\\t"
    | c when Char.code c < 0x20 ->
        Buffer.add_string buf (Printf.sprintf "\\u%04x" (Char.code c))
    | c -> Buffer.add_char buf c
  ) s;
  Buffer.add_char buf '"';
  Buffer.contents buf

(* Default empty state. *)
let empty_state : assign_state =
  { as_shared_vars   = [];
    as_declared_refs = [];
    as_bounded_int   = None }

let state_with_declared (xs : string list) : assign_state =
  { as_shared_vars   = [];
    as_declared_refs = List.map to_char_list xs;
    as_bounded_int   = None }

(* State-aware (refined) constructors. *)
let empty_aware : aware_state =
  { aw_shared_vars   = [];
    aw_declared_refs = [];
    aw_local_refs    = [];
    aw_array_locals  = [];
    aw_bounded_int   = None }

let aware_with
    ?(shared = []) ?(declared = []) ?(locals = [])
    ?(arrays = []) ?(bounded = None) () : aware_state =
  { aw_shared_vars   = List.map to_char_list shared;
    aw_declared_refs = List.map to_char_list declared;
    aw_local_refs    = List.map to_char_list locals;
    aw_array_locals  = List.map to_char_list arrays;
    aw_bounded_int   = bounded }

(* ---- Test cases. Add new cases here AND in
        test-suite/extraction-byte-diff/cases.txt + the
        Python comparison side (bin/extraction-byte-diff.py). ---- *)

let case_id_x_str x = (x, to_char_list "x")
let case_id_y_str y = (y, to_char_list "y")

let run_case (id : string) (state : assign_state) (ws : whyml_stmt) : unit =
  let out = emit_stmt_full_complete state ws in
  Printf.printf "%s\t%s\n" id (json_str (of_char_list out))

(* Same case_id, but uses the state-aware printer. *)
let run_case_aware
    (id : string) (state : aware_state) (ws : whyml_stmt) : unit =
  let out = emit_stmt_state_aware state ws in
  Printf.printf "%s\t%s\n" id (json_str (of_char_list out))

let () =
  (* All cases use the state-aware printer. State per case mirrors
     Module 6's per-case configuration (set up in the Python
     comparison side bin/extraction-byte-diff.py). *)

  (* skip *)
  run_case_aware "skip" empty_aware WSkip;

  (* assign-fresh: x = 1 (fresh local — let-in scoping) *)
  run_case_aware "assign-fresh" empty_aware
    (WAssign (to_char_list "x", EInt 1));

  (* assign-existing: x ∈ declared_refs → x := 1 *)
  run_case_aware "assign-existing"
    (aware_with ~declared:["x"] ())
    (WAssign (to_char_list "x", EInt 1));

  (* augassign-add *)
  run_case_aware "augassign-add"
    (aware_with ~declared:["x"] ())
    (WAugAssign (to_char_list "x", OpAdd, EInt 2));

  (* arrayset — neutral state → subscript_set fallback *)
  run_case_aware "arrayset" empty_aware
    (WArraySet (to_char_list "a", EVar (to_char_list "i"), EInt 7));

  (* seq-skip-skip *)
  run_case_aware "seq-skip-skip" empty_aware
    (WSeq (WSkip, WSkip));

  (* raise-* *)
  run_case_aware "raise-break" empty_aware (WRaise ExcBreak);
  run_case_aware "raise-continue" empty_aware (WRaise ExcContinue);
  run_case_aware "raise-named-foo" empty_aware
    (WRaise (ExcNamed (to_char_list "Foo")));

  (* label *)
  run_case_aware "label-L" empty_aware
    (WLabel (to_char_list "L"));

  (* ===== Expanded corpus ===== *)

  (* seq-assign-existing-twice: x ∈ declared *)
  run_case_aware "seq-assign-existing-twice"
    (aware_with ~declared:["x"] ())
    (WSeq (WAssign (to_char_list "x", EInt 1),
           WAssign (to_char_list "x", EInt 2)));

  (* seq-augassign-twice *)
  run_case_aware "seq-augassign-twice"
    (aware_with ~declared:["x"] ())
    (WSeq (WAugAssign (to_char_list "x", OpAdd, EInt 1),
           WAugAssign (to_char_list "x", OpAdd, EInt 2)));

  run_case_aware "augassign-sub"
    (aware_with ~declared:["x"] ())
    (WAugAssign (to_char_list "x", OpSub, EInt 3));

  run_case_aware "augassign-mul"
    (aware_with ~declared:["x"] ())
    (WAugAssign (to_char_list "x", OpMul, EInt 2));

  (* assign-binop-add: x existing, y is in local_refs → !y *)
  run_case_aware "assign-binop-add"
    (aware_with ~declared:["x"; "y"] ~locals:["y"] ())
    (WAssign (to_char_list "x",
              EBinOp (OpAdd, EVar (to_char_list "y"), EInt 1)));

  (* assign-len: arr NOT in array_locals → iter_length *)
  run_case_aware "assign-len"
    (aware_with ~declared:["x"] ())
    (WAssign (to_char_list "x", ELen (to_char_list "arr")));

  (* assign-subscript: arr NOT in array_locals → subscript_get *)
  run_case_aware "assign-subscript"
    (aware_with ~declared:["x"] ())
    (WAssign (to_char_list "x",
              ESubscript (to_char_list "arr", EInt 0)));

  (* assert-true *)
  run_case_aware "assert-true" empty_aware
    (WAssert (CBoolLit true, to_char_list "ok"));

  (* if-skip-skip: test wrapped with bool-coerce *)
  run_case_aware "if-skip-skip"
    (aware_with ~declared:["x"] ())
    (WIf (EVar (to_char_list "x"), WSkip, WSkip));

  (* while-trivial: condition x → (x <> 0) *)
  run_case_aware "while-trivial"
    (aware_with ~declared:["x"] ())
    (WWhile ([CBoolLit true], [CInt 0],
             EVar (to_char_list "x"), WSkip));

  (* try-catch *)
  run_case_aware "try-catch-simple" empty_aware
    (WTryCatch (WSkip, to_char_list "E", WSkip));

  (* ghost-decl-int: scoping let-ghost → "()" continuation *)
  run_case_aware "ghost-decl-int" empty_aware
    (WGhostDecl (to_char_list "gx", GTInt, CInt 0));

  (* ghost-decl-array: scoping, no ref *)
  run_case_aware "ghost-decl-array" empty_aware
    (WGhostDecl (to_char_list "ga", GTArray, CVar (to_char_list "src")));

  (* ghost-assign-int-add *)
  run_case_aware "ghost-assign-int-add" empty_aware
    (WGhostAssign (to_char_list "gx", GTInt, AugAdd, CInt 1));

  run_case_aware "ghost-assign-int-sub" empty_aware
    (WGhostAssign (to_char_list "gx", GTInt, AugSub, CInt 1));

  (* nested-seq: skip ; skip ; skip *)
  run_case_aware "nested-seq" empty_aware
    (WSeq (WSkip, WSeq (WSkip, WSkip)));

  ()
