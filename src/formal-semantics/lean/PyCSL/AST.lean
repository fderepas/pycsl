/-
  AST.lean — Abstract Syntax Tree for PyCSL formal semantics
  Mirror of Phase1_AST.v (all phases).
-/

abbrev Ident := String

inductive Binop where
  | add | sub | mul | div
  deriving DecidableEq, Repr

inductive CmpOp where
  | eq | ne | lt | le | gt | ge
  deriving DecidableEq, Repr

inductive Expr where
  | int       (n : Int)
  | var       (x : Ident)
  | subscript (arr : Ident) (i : Expr)
  | len       (arr : Ident)
  | binop     (op : Binop) (e1 e2 : Expr)
  | neg       (e : Expr)
  | cmp       (op : CmpOp) (e1 e2 : Expr)
  deriving Repr

inductive ContractExpr where
  -- Phase 0 (original)
  | int       (n : Int)
  | var       (x : Ident)
  | result
  | length    (arr : Ident)
  | subscript (arr : Ident) (i : ContractExpr)
  | old       (e : ContractExpr)
  | binop     (op : Binop) (e1 e2 : ContractExpr)
  | neg       (e : ContractExpr)
  | eq        (e1 e2 : ContractExpr)
  | ne        (e1 e2 : ContractExpr)
  | lt        (e1 e2 : ContractExpr)
  | le        (e1 e2 : ContractExpr)
  | gt        (e1 e2 : ContractExpr)
  | ge        (e1 e2 : ContractExpr)
  | and       (e1 e2 : ContractExpr)
  | or        (e1 e2 : ContractExpr)
  | not       (e : ContractExpr)
  | implies   (e1 e2 : ContractExpr)
  | iff       (e1 e2 : ContractExpr)
  | forall_   (x : Ident) (body : ContractExpr)
  | exists_   (x : Ident) (body : ContractExpr)
  -- Phase 1 — expression language completeness
  | chainedSubscript (arr : Ident) (i j : ContractExpr)
  | boolLit   (b : Bool)
  | noneLit
  | stringLit (s : String)
  | isSorted  (arr : Ident) (lo hi : ContractExpr)
  | sum       (arr : Ident) (lo hi : ContractExpr)
  | slice     (arr : Ident) (lo hi : ContractExpr)
  | in_       (elem container : ContractExpr)
  | notIn     (elem container : ContractExpr)
  -- Phase 2 — function/statement completeness
  | resultSubscript (i : ContractExpr)
  | call      (fname : Ident) (args : List ContractExpr)
  -- Phase 3 — ghost/label
  | at_       (e : ContractExpr) (label : Ident)
  -- Phase 3b — ghost dict atoms
  | cgMapEmpty
  | cgMapGet    (d k : ContractExpr)
  | cgMapSet    (d k v : ContractExpr)
  | cgMapRemove (d k : ContractExpr)
  | cgHasKey    (d k : ContractExpr)
  | cgMapEq     (d1 d2 : ContractExpr)
  -- Phase 3b — ghost list atoms
  | cgNil
  | cgCons      (h t : ContractExpr)
  | cgHd        (l : ContractExpr)
  | cgTl        (l : ContractExpr)
  | cgListLen   (l : ContractExpr)
  | cgNth       (l i : ContractExpr)
  | cgListMem   (x l : ContractExpr)
  | cgAppend    (l1 l2 : ContractExpr)
  -- Phase 3b — ghost set atoms
  | cgSetEmpty
  | cgSetAdd    (x s : ContractExpr)
  | cgSetRemove (x s : ContractExpr)
  | cgSetMem    (x s : ContractExpr)
  | cgSetCard   (s : ContractExpr)
  | cgSetUnion  (s1 s2 : ContractExpr)
  | cgSetInter  (s1 s2 : ContractExpr)
  | cgSetDiff   (s1 s2 : ContractExpr)
  | cgSetSubset (s1 s2 : ContractExpr)
  | cgSetEq     (s1 s2 : ContractExpr)
  -- Phase 3b — ghost tuple atoms
  | cgMkTuple2  (a b : ContractExpr)
  | cgMkTuple3  (a b c : ContractExpr)
  | cgMkTuple4  (a b c d : ContractExpr)
  | cgFst       (t : ContractExpr)
  | cgSnd       (t : ContractExpr)
  | cgTrd       (t : ContractExpr)
  | cgFth       (t : ContractExpr)
  -- Phase 3b — ghost string atoms
  | cgStrConcat (s1 s2 : ContractExpr)
  | cgStrLen    (s : ContractExpr)
  | cgStrNth    (s i : ContractExpr)
  -- Phase 3b — ghost array atoms
  | cgMake      (n v : ContractExpr)
  | cgCopy      (arr : Ident)
  | cgCopyRange (arr : Ident) (lo hi : ContractExpr)
  deriving Repr

inductive FrameCond where
  | nothing
  | vars (xs : List Ident)
  deriving Repr

inductive IntModel where
  | unbounded
  | bounded (bits : Nat)
  deriving Repr

structure FuncSpec where
  pre          : ContractExpr
  post         : ContractExpr
  frame        : FrameCond
  variant      : Option ContractExpr
  diverges     : Bool
  trusted      : Bool
  reviewer     : Option String           -- Q1.L.4: \trusted reviewer: <id>
  raises       : List (Ident × ContractExpr)
  intModel     : IntModel
  noException  : List Ident               -- Q1.L.1: no_exception E1, E2, ...
  deriving Repr

inductive AugOp where
  | add | sub | mul
  deriving DecidableEq, Repr

inductive GhostType where
  | int | string | array | dict | list | set
  | tuple2 | tuple3 | tuple4
  deriving DecidableEq, Repr

abbrev GhostExpr := ContractExpr

inductive Stmt where
  -- Phase 0 (original)
  | skip
  | assign    (x : Ident)   (e : Expr)
  | augAssign (x : Ident)   (op : Binop) (e : Expr)
  | arraySet  (arr : Ident) (i : Expr) (v : Expr)
  | seq       (s1 s2 : Stmt)
  | ite       (cond : Expr) (sThen sElse : Stmt)
  | while_    (inv var : ContractExpr) (cond : Expr) (body : Stmt)
  | for_      (x arr : Ident) (inv var : ContractExpr) (body : Stmt)
  | ret       (e : Expr)
  | continue_
  -- Phase 2 additions
  | break_
  | assert_   (cond : ContractExpr) (msg : String)
  | tupleUnpack (xs : List Ident) (e : Expr)
  -- Phase 3a ghost/label
  | ghostDecl   (x : Ident) (t : GhostType) (init : GhostExpr)
  | ghostAssign (x : Ident) (t : GhostType) (op : AugOp) (rhs : GhostExpr)
  | label_      (name : Ident)
  -- Phase 5 exceptions
  | raise_      (exc : Ident)
  | tryCatch    (body : Stmt) (exc : Ident) (handler : Stmt)
  -- Phase 6 field assignment
  | fieldAssign    (selfId f : Ident) (e : Expr)
  | fieldAugAssign (selfId f : Ident) (op : Binop) (e : Expr)
  -- Phase 8 concurrent
  | critical    (mutex : Ident) (body : Stmt)
  | threadEntry (body : Stmt)
  deriving Repr
