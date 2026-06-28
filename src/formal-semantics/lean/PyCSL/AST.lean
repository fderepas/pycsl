/-
  AST.lean — Abstract Syntax Tree for PyCSL formal semantics
  Mirror of Phase1_AST.v (all phases).
-/

abbrev Ident := String

inductive Binop where
  | add | sub | mul | div | mod_  -- mod_ to avoid Lean's reserved word
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
  | fieldGet  (obj : Ident) (f : Ident)  -- Q4 U.4 expansion (2026-05-29)
  | call      (func : Ident) (args : List Expr)  -- Q4 U.4 (2026-05-29)
  deriving Repr
  -- Q4 U.4 (2026-05-29): `deriving DecidableEq` doesn't synthesize for
  -- nested `List Expr` (the .call args). 2026-05-30: manual
  -- DecidableEq + DecidableEqList instances written via mutual recursion
  -- below; Module 4 Lean citation upgraded from the `PyCSL.AST.Expr`
  -- anchor to the real `instDecidableEqExpr`. Parity with Rocq's
  -- `expr_eq_dec` (which uses `list_eq_dec expr_eq_dec` for the .call
  -- args case).

namespace Expr

mutual

protected def decEq : (e1 e2 : Expr) → Decidable (e1 = e2) := fun e1 e2 =>
  match e1, e2 with
  | .int n, .int m =>
      if h : n = m then Decidable.isTrue (h ▸ rfl)
      else Decidable.isFalse (fun heq => by cases heq; exact h rfl)
  | .var x, .var y =>
      if h : x = y then Decidable.isTrue (h ▸ rfl)
      else Decidable.isFalse (fun heq => by cases heq; exact h rfl)
  | .subscript a i, .subscript b j =>
      if hab : a = b then
        match Expr.decEq i j with
        | Decidable.isTrue hij => Decidable.isTrue (hab ▸ hij ▸ rfl)
        | Decidable.isFalse hij => Decidable.isFalse (fun heq => by cases heq; exact hij rfl)
      else Decidable.isFalse (fun heq => by cases heq; exact hab rfl)
  | .len a, .len b =>
      if h : a = b then Decidable.isTrue (h ▸ rfl)
      else Decidable.isFalse (fun heq => by cases heq; exact h rfl)
  | .binop op a b, .binop op' a' b' =>
      if hop : op = op' then
        match Expr.decEq a a', Expr.decEq b b' with
        | Decidable.isTrue ha, Decidable.isTrue hb =>
            Decidable.isTrue (hop ▸ ha ▸ hb ▸ rfl)
        | Decidable.isTrue _, Decidable.isFalse hb =>
            Decidable.isFalse (fun heq => by cases heq; exact hb rfl)
        | Decidable.isFalse ha, _ =>
            Decidable.isFalse (fun heq => by cases heq; exact ha rfl)
      else Decidable.isFalse (fun heq => by cases heq; exact hop rfl)
  | .neg e, .neg e' =>
      match Expr.decEq e e' with
      | Decidable.isTrue h => Decidable.isTrue (h ▸ rfl)
      | Decidable.isFalse h => Decidable.isFalse (fun heq => by cases heq; exact h rfl)
  | .cmp op a b, .cmp op' a' b' =>
      if hop : op = op' then
        match Expr.decEq a a', Expr.decEq b b' with
        | Decidable.isTrue ha, Decidable.isTrue hb =>
            Decidable.isTrue (hop ▸ ha ▸ hb ▸ rfl)
        | Decidable.isTrue _, Decidable.isFalse hb =>
            Decidable.isFalse (fun heq => by cases heq; exact hb rfl)
        | Decidable.isFalse ha, _ =>
            Decidable.isFalse (fun heq => by cases heq; exact ha rfl)
      else Decidable.isFalse (fun heq => by cases heq; exact hop rfl)
  | .fieldGet o f, .fieldGet o' f' =>
      if ho : o = o' then
        if hf : f = f' then Decidable.isTrue (ho ▸ hf ▸ rfl)
        else Decidable.isFalse (fun heq => by cases heq; exact hf rfl)
      else Decidable.isFalse (fun heq => by cases heq; exact ho rfl)
  | .call f args, .call f' args' =>
      if hf : f = f' then
        match Expr.decEqList args args' with
        | Decidable.isTrue ha => Decidable.isTrue (hf ▸ ha ▸ rfl)
        | Decidable.isFalse ha => Decidable.isFalse (fun heq => by cases heq; exact ha rfl)
      else Decidable.isFalse (fun heq => by cases heq; exact hf rfl)
  -- Cross-constructor cases. Every entry: heads differ → `nomatch heq`.
  | .int _, .var _ | .int _, .subscript _ _ | .int _, .len _
  | .int _, .binop _ _ _ | .int _, .neg _ | .int _, .cmp _ _ _
  | .int _, .fieldGet _ _ | .int _, .call _ _
  | .var _, .int _ | .var _, .subscript _ _ | .var _, .len _
  | .var _, .binop _ _ _ | .var _, .neg _ | .var _, .cmp _ _ _
  | .var _, .fieldGet _ _ | .var _, .call _ _
  | .subscript _ _, .int _ | .subscript _ _, .var _ | .subscript _ _, .len _
  | .subscript _ _, .binop _ _ _ | .subscript _ _, .neg _
  | .subscript _ _, .cmp _ _ _ | .subscript _ _, .fieldGet _ _
  | .subscript _ _, .call _ _
  | .len _, .int _ | .len _, .var _ | .len _, .subscript _ _
  | .len _, .binop _ _ _ | .len _, .neg _ | .len _, .cmp _ _ _
  | .len _, .fieldGet _ _ | .len _, .call _ _
  | .binop _ _ _, .int _ | .binop _ _ _, .var _ | .binop _ _ _, .subscript _ _
  | .binop _ _ _, .len _ | .binop _ _ _, .neg _ | .binop _ _ _, .cmp _ _ _
  | .binop _ _ _, .fieldGet _ _ | .binop _ _ _, .call _ _
  | .neg _, .int _ | .neg _, .var _ | .neg _, .subscript _ _
  | .neg _, .len _ | .neg _, .binop _ _ _ | .neg _, .cmp _ _ _
  | .neg _, .fieldGet _ _ | .neg _, .call _ _
  | .cmp _ _ _, .int _ | .cmp _ _ _, .var _ | .cmp _ _ _, .subscript _ _
  | .cmp _ _ _, .len _ | .cmp _ _ _, .binop _ _ _ | .cmp _ _ _, .neg _
  | .cmp _ _ _, .fieldGet _ _ | .cmp _ _ _, .call _ _
  | .fieldGet _ _, .int _ | .fieldGet _ _, .var _ | .fieldGet _ _, .subscript _ _
  | .fieldGet _ _, .len _ | .fieldGet _ _, .binop _ _ _ | .fieldGet _ _, .neg _
  | .fieldGet _ _, .cmp _ _ _ | .fieldGet _ _, .call _ _
  | .call _ _, .int _ | .call _ _, .var _ | .call _ _, .subscript _ _
  | .call _ _, .len _ | .call _ _, .binop _ _ _ | .call _ _, .neg _
  | .call _ _, .cmp _ _ _ | .call _ _, .fieldGet _ _ =>
      Decidable.isFalse (fun heq => by cases heq)

protected def decEqList : (xs ys : List Expr) → Decidable (xs = ys) := fun xs ys =>
  match xs, ys with
  | [], [] => Decidable.isTrue rfl
  | _ :: _, [] => Decidable.isFalse (fun h => by cases h)
  | [], _ :: _ => Decidable.isFalse (fun h => by cases h)
  | a :: as, b :: bs =>
      match Expr.decEq a b, Expr.decEqList as bs with
      | Decidable.isTrue h1, Decidable.isTrue h2 => Decidable.isTrue (h1 ▸ h2 ▸ rfl)
      | Decidable.isTrue _, Decidable.isFalse h2 =>
          Decidable.isFalse (fun heq => by cases heq; exact h2 rfl)
      | Decidable.isFalse h1, _ =>
          Decidable.isFalse (fun heq => by cases heq; exact h1 rfl)

end

instance : DecidableEq Expr := Expr.decEq

end Expr

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
  /-- Phase 4 — Category C library predicates (contract-expr extensions).
      These add ContractExpr constructors + evalContract clauses ONLY;
      they do NOT extend Stmt/Exec/wp, so pycsl_soundness is unaffected.

      Heap-dependent predicates (\valid, \separated, \valid2d) are modelled
      as Hoare-model stubs (True): the Hoare model has no heap, so the
      predicates are vacuously satisfied. They become real when Phase 7
      (memory-model parameterisation) lands a heap interface.

      \length2d extends the existing \length (modelled) to 2D arrays. In
      the flat-array model (Val.array (List Int)) there is no 2D structure,
      so \length2d(arr) returns length(arr). The rows/cols args from the
      pure AST (Length2D.base/rows/cols) are elided — no flat-model meaning. -/
  | cValid     (ptr len : ContractExpr)
  | cSeparated (a b : ContractExpr)
  | cLength2d  (arr : Ident)
  | cValid2d   (ptr rows cols : ContractExpr)
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
  noException  : List Ident              -- Q1.L.1: no_exception E1, E2, ...
  allowFinalizer : Bool                  -- Q1.L.3: \allow_finalizer (transpiler-gating only)
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
              (allowIterMut : Bool)  -- Q1.L.2: \allow_iteration_mutation (transpiler-gating only)
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
