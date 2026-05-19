/-
  AST.lean — Abstract Syntax Tree for PyCSL formal semantics
  Port of Phase1_AST.v
-/

abbrev Ident := String

inductive Binop where
  | add | sub | mul | div
  deriving DecidableEq, Repr

inductive Expr where
  | int       (n : Int)
  | var       (x : Ident)
  | subscript (arr : Ident) (i : Expr)
  | binop     (op : Binop) (e1 e2 : Expr)
  | neg       (e : Expr)
  deriving Repr

inductive ContractExpr where
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
  deriving Repr

inductive FrameCond where
  | nothing
  | vars (xs : List Ident)
  deriving Repr

structure FuncSpec where
  pre   : ContractExpr
  post  : ContractExpr
  frame : FrameCond
  deriving Repr

inductive Stmt where
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
  deriving Repr
