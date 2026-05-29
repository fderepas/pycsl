(* Phase1b_IrToStmtExtract.v — Q4 U.4 first slice: extract ir_to_stmt to OCaml.

   Mirrors Phase6L_EmitExtract.v for the upward direction: the
   extracted OCaml code is the reference implementation that the
   byte-diff orchestrator drives against Module 5's actual JSON IR.

   Extraction outputs `extracted/IrToStmtExtract.ml` + `.mli`. Run
   `make Phase1b_IrToStmtExtract.vo` to trigger extraction.

   Pipeline (this file = step 1; remaining = follow-up):

     1. THIS FILE: extract ir_to_stmt → OCaml.                       ← step 1
     2. OCaml driver (extracted/ir_driver.ml):
          - reads Module 5 JSON IR from stdin
          - parses into json_value-isomorphic structure
          - calls ir_to_stmt
          - prints { case_id, formal_stmt_repr } to stdout
     3. Python equivalent (bin/byte-diff-ir-to-stmt.py):
          - runs Module 5 on each .py corpus file
          - invokes the OCaml driver with each IR JSON
          - records output
     4. bin/extraction-byte-diff-upward.sh:
          - orchestrates pipeline, reports PASS/FAIL per corpus case

   This file delivers step 1 only. Steps 2-4 are deferred. *)

Require Import String List ZArith Ascii.
Require Import Phase0_IrJson.
Require Import Phase1_AST.
Require Import Phase1b_IrToStmt.
Require Import Phase1c_ValidateIr.

(* ===== Extraction language and OCaml mappings ===== *)

Require Coq.extraction.Extraction.
Require Coq.extraction.ExtrOcamlBasic.
Require Coq.extraction.ExtrOcamlString.
Require Coq.extraction.ExtrOcamlZInt.
Require Coq.extraction.ExtrOcamlNatInt.

Extraction Language OCaml.

(* Map Rocq booleans / option / list to native OCaml. *)
Extract Inductive bool => "bool" [ "true" "false" ].
Extract Inductive option => "option" [ "Some" "None" ].
Extract Inductive list => "list" [ "[]" "(::)" ].

(* ===== What to extract =====

   The full ir_to_stmt converter plus the IR shape (json_value /
   contracts_ir / function_ir / program_ir) so the driver can
   construct them from parsed JSON, plus validate_ir so the
   driver can pre-validate before conversion. *)

Extraction "extracted/IrToStmtExtract.ml"
  json_value
  contracts_ir
  function_ir
  program_ir
  json_field_get
  json_to_string
  json_to_z
  json_to_list
  string_to_binop
  string_to_cmpop
  string_to_aug_op
  string_to_ghost_type
  ir_to_expr
  ir_to_contract_expr
  ir_to_stmt_n
  ir_to_stmt
  validate_ir
  validate_function
  validate_contracts.
