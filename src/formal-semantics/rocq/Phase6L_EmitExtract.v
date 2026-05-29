(* Phase6L_EmitExtract.v — CC.5 byte-diff foundation: extract to OCaml
   ======================================================================

   Sets up Rocq Extraction directives to produce OCaml code for
   `emit_stmt_full_complete` and its dependencies. The extracted
   OCaml is the reference implementation for the CC.5 byte-diff
   validation against Module 6's Python emission.

   Extraction outputs `extracted/EmitExtract.ml` + `.mli`. Run the
   build target `Phase6L_EmitExtract.vo` to trigger extraction.

   Pipeline (this file = step 1; remaining = handoff):

     1. THIS FILE: extract emit_stmt_full_complete → OCaml.        ✅
     2. OCaml driver (extracted/driver.ml):
          - constructs whyml_stmt test inputs
          - calls emit_stmt_full_complete on each
          - prints { case_id, formal_output } to stdout
     3. Python equivalent (bin/extraction-byte-diff.py):
          - parses the OCaml driver's output
          - constructs equivalent inputs in Module 6's IR format
          - runs Module 6 on each
          - prints { case_id, module6_output }
     4. bin/extraction-byte-diff.sh:
          - runs both drivers, diffs case-by-case, reports PASS/FAIL
     5. test-suite/extraction-byte-diff/cases.txt:
          - documented test cases shared by both drivers
*)

Require Import String List ZArith Ascii.
Require Import Phase1_AST.
Require Import Phase6_WhyML.
Require Import Phase6d_StmtGen.
Require Import Phase6L_EmitStmt.
Require Import Phase6L_EmitAssign.
Require Import Phase6L_EmitAugAssign.
Require Import Phase6L_EmitArraySet.
Require Import Phase6L_EmitSeq.
Require Import Phase6L_EmitSimple.
Require Import Phase6L_EmitBlocks.
Require Import Phase6L_EmitComposition.
Require Import Phase6L_EmitStateAware.

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

(* String and ascii via ExtrOcamlString already maps to OCaml's
   `char list` representation. We keep that for now. For native
   OCaml strings, the driver converts via Bytes/String.of_seq. *)

(* ===== What to extract =====

   The composition theorem's underlying function plus the
   per-construct emit functions and pretty-printers. These are
   the load-bearing definitions for the CC.5 byte-diff check. *)

Extraction "extracted/EmitExtract.ml"
  emit_stmt_full_complete
  acceptable_emit
  emit_assign
  emit_aug_assign
  emit_array_set
  emit_if
  emit_while
  emit_try_catch
  emit_ghost_decl
  emit_ghost_assign
  emit_raise
  emit_label
  emit_assert
  pretty_expr
  pretty_contract_expr
  pretty_binop
  z_to_string
  exc_to_string
  op_translate_aug
  aug_op_str
  gen
  emit_stmt_state_aware
  emit_cont
  pretty_expr_state
  to_bool_state
  empty_aware_state
  emit_ghost_decl_aware.
