(* Phase1_AST.v — Abstract Syntax Tree for PyCSL formal semantics *)
(* Part of the PyCSL formal verification project *)

Require Import ZArith String List.
Open Scope Z_scope.
Open Scope string_scope.

Definition ident := string.
Definition ident_eq := String.eqb.

(* Decidable equality for identifiers *)
Lemma ident_eq_dec : forall (x y : ident), {x = y} + {x <> y}.
Proof. apply String.string_dec. Defined.

(* Arithmetic binary operators *)
Inductive binop : Type :=
  | OpAdd | OpSub | OpMul | OpDiv | OpMod.

(* Comparison operators — return 0/1 in the runtime int domain. *)
Inductive cmpop : Type :=
  | OpEq | OpNe | OpLt | OpLe | OpGt | OpGe.

(* Runtime expressions — Python subset; comparisons return 0/1. *)
Inductive expr : Type :=
  | EInt       (n : Z)
  | EVar       (x : ident)
  | ESubscript (arr : ident) (i : expr)
  | ELen       (arr : ident)
  | EBinOp     (op : binop) (e1 e2 : expr)
  | ENeg       (e : expr)
  | ECmp       (op : cmpop) (e1 e2 : expr)
  (* Q4 U.4 expansion (2026-05-29): class field read.
     `EFieldGet obj f` represents `obj.f` at the expression level.
     Evaluation flattens to a synthesized variable name (obj ++ "." ++ f)
     looked up in the runtime state; downstream code that maintains an
     explicit object-field state can intercept this constructor. *)
  | EFieldGet  (obj : ident) (f : ident)
  (* Q4 U.4 expansion (2026-05-29): generic function/method call.
     `ECall func args` represents calling an arbitrary function.
     Evaluation defaults to VInt 0 — no function semantics; the
     constructor is a structural placeholder that downstream code
     with function-interpretation infrastructure can intercept. *)
  | ECall      (func : ident) (args : list expr).

(* ===== Decidable equality on operators and runtime expressions =====
   Added 2026-05-29 for CC.4 Module 4 citation. These structural-
   decidability lemmas anchor Module4_SemanticAnalyzer's well-
   formedness analysis: any algorithm that compares two `expr`
   values for structural equality can rely on `expr_eq_dec` being
   total. The semantic analyzer's `isinstance` dispatch over
   CSLNode subtypes (Python `==` on AST nodes) is the
   programmer-side analogue of this kernel-checked totality. *)

Lemma binop_eq_dec : forall (a b : binop), {a = b} + {a <> b}.
Proof. decide equality. Defined.

Lemma cmpop_eq_dec : forall (a b : cmpop), {a = b} + {a <> b}.
Proof. decide equality. Defined.

Lemma expr_eq_dec : forall (a b : expr), {a = b} + {a <> b}.
Proof.
  fix expr_eq_dec 1.
  decide equality.
  - apply Z.eq_dec.
  - apply ident_eq_dec.
  - apply ident_eq_dec.
  - apply ident_eq_dec.
  - apply binop_eq_dec.
  - apply cmpop_eq_dec.
  - apply ident_eq_dec.
  - apply ident_eq_dec.
  - apply (list_eq_dec expr_eq_dec).
  - apply ident_eq_dec.
Defined.

(* Contract expressions — full logical language with \result, \old, quantifiers *)
Inductive contract_expr : Type :=
  | CInt       (n : Z)
  | CVar       (x : ident)
  | CResult
  | CLength    (arr : ident)
  | CSubscript (arr : ident) (i : contract_expr)
  | COld       (e : contract_expr)
  | CBinOp     (op : binop) (e1 e2 : contract_expr)
  | CNeg       (e : contract_expr)
  | CEq        (e1 e2 : contract_expr)
  | CNe        (e1 e2 : contract_expr)
  | CLt        (e1 e2 : contract_expr)
  | CLe        (e1 e2 : contract_expr)
  | CGt        (e1 e2 : contract_expr)
  | CGe        (e1 e2 : contract_expr)
  | CAnd       (e1 e2 : contract_expr)
  | COr        (e1 e2 : contract_expr)
  | CNot       (e : contract_expr)
  | CImplies   (e1 e2 : contract_expr)
  | CIff       (e1 e2 : contract_expr)
  | CForall    (x : ident) (body : contract_expr)
  | CExists    (x : ident) (body : contract_expr)
  (* Phase 1 — expression language completeness *)
  | CChainedSubscript (arr : ident) (i j : contract_expr)
  | CBoolLit          (b : bool)
  | CNoneLit
  | CStringLit        (s : string)
  | CIsSorted         (arr : ident) (lo hi : contract_expr)
  | CSum              (arr : ident) (lo hi : contract_expr)
  | CSlice            (arr : ident) (lo hi : contract_expr)
  | CIn               (elem container : contract_expr)
  | CNotIn            (elem container : contract_expr)
  (* Phase 2 — function/statement completeness *)
  | CResultSubscript  (i : contract_expr)
  | CCall             (fname : ident) (args : list contract_expr)
  (* Phase 3 — ghost/label expressions *)
  | CAt               (e : contract_expr) (label : ident)
  (* Phase 3b — ghost dict atoms *)
  | CGMapEmpty
  | CGMapGet    (d k : contract_expr)
  | CGMapSet    (d k v : contract_expr)
  | CGMapRemove (d k : contract_expr)
  | CGHasKey    (d k : contract_expr)
  | CGMapEq     (d1 d2 : contract_expr)
  (* Phase 3b — ghost list atoms *)
  | CGNil
  | CGCons      (h t : contract_expr)
  | CGHd        (l : contract_expr)
  | CGTl        (l : contract_expr)
  | CGListLen   (l : contract_expr)
  | CGNth       (l i : contract_expr)
  | CGListMem   (x l : contract_expr)
  | CGAppend    (l1 l2 : contract_expr)
  (* Phase 3b — ghost set atoms *)
  | CGSetEmpty
  | CGSetAdd    (x s : contract_expr)
  | CGSetRemove (x s : contract_expr)
  | CGSetMem    (x s : contract_expr)
  | CGSetCard   (s : contract_expr)
  | CGSetUnion  (s1 s2 : contract_expr)
  | CGSetInter  (s1 s2 : contract_expr)
  | CGSetDiff   (s1 s2 : contract_expr)
  | CGSetSubset (s1 s2 : contract_expr)
  | CGSetEq     (s1 s2 : contract_expr)
  (* Phase 3b — ghost tuple atoms *)
  | CGMkTuple2  (a b : contract_expr)
  | CGMkTuple3  (a b c : contract_expr)
  | CGMkTuple4  (a b c d : contract_expr)
  | CGFst       (t : contract_expr)
  | CGSnd       (t : contract_expr)
  | CGTrd       (t : contract_expr)
  | CGFth       (t : contract_expr)
  (* Phase 3b — ghost string atoms *)
  | CGStrConcat (s1 s2 : contract_expr)
  | CGStrLen    (s : contract_expr)
  | CGStrNth    (s i : contract_expr)
  (* Phase 3b — ghost array atoms *)
  | CGMake      (n v : contract_expr)
  | CGCopy      (arr : ident)
  | CGCopyRange (arr : ident) (lo hi : contract_expr)
  (* Phase 4 — Category C library predicates (contract-expr extensions).
     These add ContractExpr constructors + eval_contract clauses ONLY;
     they do NOT extend Stmt/Exec/wp, so pycsl_soundness is unaffected.

     Heap-dependent predicates (\valid, \separated, \valid2d) are modelled
     as Hoare-model stubs (True): the Hoare model has no heap, so the
     predicates are vacuously satisfied. They become real when Phase 7
     (memory-model parameterisation) lands a heap interface.

     \length2d extends the existing \length (modelled) to 2D arrays. In
     the flat-array model (VArray (list Z)) there is no 2D structure, so
     \length2d(arr) returns length(arr). The rows/cols args from the pure
     AST (Length2D.base/rows/cols) are elided — no flat-model meaning. *)
   | CValid     (ptr len : contract_expr)
   | CSeparated (a b : contract_expr)
   | CLength2d  (arr : ident)
   | CValid2d   (ptr rows cols : contract_expr)
   (* Phase 6 — class invariants (Category A).
      `CClassInvariant cls inv` is a contract-level construct: `cls` names
      the class (a tag for the future heap/record model in Phase 7), and
      `inv` is the invariant predicate (a contract_expr evaluated over the
      current state). The Hoare model evaluates `CClassInvariant cls inv`
      exactly as `inv`; the class tag is carried for documentation and for
      the Phase 7 record-typed-state instance, where it will scope the
      predicate to the named record's fields.

      This is NOT a new Stmt: invariant-wrapping around method bodies is
      modelled as a derived lemma (Phase6n_ClassInvariants.v) that
      instantiates `pycsl_soundness` with the invariant as both the
      assumed precondition and the ensured normal postcondition. *)
   | CClassInvariant (class_name : ident) (invariant_ : contract_expr).

(* Frame conditions *)
Inductive frame_cond : Type :=
  | FNothing
  | FVars (xs : list ident).

(* Bounded integer model *)
Inductive int_model : Type :=
  | IMUnbounded
  | IMBounded (bits : nat).

(* Function specifications — extended for Phase 2+ *)
Record func_spec : Type := mkSpec {
  spec_pre          : contract_expr;
  spec_post         : contract_expr;
  spec_frame        : frame_cond;
  spec_variant      : option contract_expr;   (* \variant *)
  spec_diverges     : bool;                   (* \diverges *)
  spec_trusted        : bool;                   (* \trusted *)
  spec_reviewer       : option string;          (* Q1.L.4: \trusted reviewer: <id> *)
  spec_raises         : list (ident * contract_expr); (* raises ExcType when cond *)
  spec_int_model      : int_model;              (* assumes bounded_int(N) *)
  spec_no_exception   : list ident;             (* Q1.L.1: no_exception E1, E2, ... *)
  spec_allow_finalizer : bool                   (* Q1.L.3: \allow_finalizer (transpiler-gating only) *)
}.

(* Augmented assignment operators *)
Inductive aug_op : Type :=
  | AugAdd | AugSub | AugMul.

(* Ghost types — one per supported WhyML type *)
Inductive ghost_type : Type :=
  | GTInt | GTString | GTArray | GTDict | GTList | GTSet
  | GTTuple2 | GTTuple3 | GTTuple4.

(* Ghost expressions: same grammar as contract_expr for now *)
Definition ghost_expr := contract_expr.

(* Statements — SWhile carries mandatory inv and var annotations *)
Inductive stmt : Type :=
  | SSkip
  | SAssign    (x : ident)   (e : expr)
  | SAugAssign (x : ident)   (op : binop) (e : expr)
  | SArraySet  (arr : ident) (i : expr) (v : expr)
  | SSeq       (s1 s2 : stmt)
  | SIf        (cond : expr) (s_then s_else : stmt)
  | SWhile     (inv : contract_expr) (var : contract_expr)
               (cond : expr) (body : stmt)
  | SFor       (x : ident) (arr : ident)
               (inv : contract_expr) (var : contract_expr) (body : stmt)
               (allow_iter_mut : bool)  (* Q1.L.2: \allow_iteration_mutation (transpiler-gating only) *)
  | SReturn    (e : expr)
  | SContinue
  (* Phase 2 additions *)
  | SBreak
  | SAssert    (cond : contract_expr) (msg : string)
  | STupleUnpack (xs : list ident) (e : expr)
  (* Phase 3a ghost/label additions *)
  | SGhostDecl   (x : ident) (t : ghost_type) (init : ghost_expr)
  | SGhostAssign (x : ident) (t : ghost_type) (op : aug_op) (rhs : ghost_expr)
  | SLabel       (name : ident)
  (* Phase 5 exception additions *)
  | SRaise       (exc : ident)
  | STryCatch    (body : stmt) (exc : ident) (handler : stmt)
  (* Phase 6 class field additions *)
  | SFieldAssign    (self_id f : ident) (e : expr)
  | SFieldAugAssign (self_id f : ident) (op : binop) (e : expr)
  (* Phase 8 concurrent additions *)
  | SCritical    (mutex : ident) (body : stmt)
  | SThreadEntry (body : stmt)
  (* Phase 7 (Category D) concurrency primitives.
     `acquires m` / `releases m` take/release a mutex. In the Hoare
     instance (no lock state) these are identity (ONormal es, Qn es);
     the real lock discipline (lock-held flag, deadlock prevention via
     lock_order) is the deferred ConcurrentMM instance work — see
     Phase7_MemModel.v §"Deferred work". *)
  | SAcquires    (mutex : ident)
  | SReleases    (mutex : ident).
