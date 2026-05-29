(* Phase0_IrJson.v — Q4 U.1 sketch: Rocq inductive matching
   Module 5's `pycsl_ir.json` shape.

   Mirrors the TypedDicts in `src/pycsl/ir_schema.py:25-68`:
     - ContractsIR (requires/ensures/assigns/raises/no_exception)
     - FunctionIR (name/contracts/body/...)
     - ProgramIR (type_decls/functions/shared_vars/mutex_invariants/...)

   STATUS: pure shape, no semantics. This is U.1 only — the
   inductive structure of Module 5's IR output. U.2 (`ir_to_stmt`)
   and U.3 (validate_ir_correspondence) are deferred to future work.

   Statement bodies and expressions are modelled as opaque
   `json_value` placeholders. U.2 will refine these into structured
   inductives matching ir_schema.py's recursive dict shapes. *)

Require Import ZArith String List.

(* ===== json_value: shape of unmodelled nested dicts ===== *)

(* The TypedDicts use `Dict[str, Any]` for statements and
   expressions — model those as an opaque json_value for now.
   U.2 will refine into a structured AST. *)
Inductive json_value : Type :=
  | JsonNull
  | JsonBool   (b : bool)
  | JsonInt    (n : Z)
  | JsonString (s : string)
  | JsonList   (vs : list json_value)
  | JsonObject (kvs : list (string * json_value)).

(* ===== contracts_ir: matches ContractsIR (ir_schema.py) ===== *)

Record contracts_ir : Type := mkContractsIR {
  ci_requires         : list json_value;
  ci_ensures          : list json_value;
  ci_assigns          : list json_value;
  ci_raises           : list json_value;
  ci_no_exception     : list string;
  ci_no_exception_all : bool
}.

(* ===== function_ir: matches FunctionIR (ir_schema.py) ===== *)

Record function_ir : Type := mkFunctionIR {
  fi_name              : string;
  fi_symbol_table      : list (string * string);
  fi_return_annotation : string;
  fi_contracts         : contracts_ir;
  fi_body              : list json_value;
  fi_function_variants : list json_value;
  fi_diverges          : bool;
  fi_trusted           : bool;
  fi_bounded_int       : option Z;
  fi_pure              : bool;
  fi_array2d_params    : list string;
  fi_array1d_params    : list string;
  fi_kind              : string;
  fi_self_type         : string
}.

(* ===== program_ir: matches ProgramIR (ir_schema.py) ===== *)

Record program_ir : Type := mkProgramIR {
  pi_type_decls       : list json_value;
  pi_functions        : list function_ir;
  pi_shared_vars      : list json_value;
  pi_mutex_invariants : list (string * json_value);
  pi_thread_entries   : list string;
  pi_lock_order       : list string
}.
