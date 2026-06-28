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

-- Phase 8: AugOp and GhostType are defined here (before the mutual
-- Expr/Stmt/ContractExpr block) because Stmt.ghostDecl/ghostAssign
-- reference them. Previously they were defined after Stmt; the
-- mutual block for Phase 8 lambda requires them earlier.
inductive AugOp where
  | add | sub | mul
  deriving DecidableEq, Repr

inductive GhostType where
  | int | string | array | dict | list | set
  | tuple2 | tuple3 | tuple4
  deriving DecidableEq, Repr

-- Forward declaration of GhostExpr as an alias for ContractExpr.
-- Defined later (after the mutual block) — see `abbrev GhostExpr`
-- below. Inside the mutual block, ghostDecl/ghostAssign use
-- `ContractExpr` directly to avoid forward-reference issues.

-- Phase 8: `Expr` and `Stmt` are mutually recursive because `Expr.lambda`
-- carries a `Stmt` body and several `Stmt` constructors carry `Expr`s.
-- Lean's `mutual` block allows forward references between them.
-- Note: the full `Stmt` inductive (with all Phase 0–8 constructors)
-- lives in this mutual block. ContractExpr-dependent constructors
-- (while_, for_, assert_, etc.) reference ContractExpr, which is
-- defined AFTER this mutual block. To break the cycle, we use a
-- forward-declared `ContractExprStub` and patch it later. In practice,
-- Lean permits references to not-yet-defined inductives in mutual
-- blocks via `mutual`/`where` syntax; we use `where` to attach
-- ContractExpr as a sibling.
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
  | chainedSubscript (arr : Ident) (i j : ContractExpr)
  | boolLit   (b : Bool)
  | noneLit
  | stringLit (s : String)
  | isSorted  (arr : Ident) (lo hi : ContractExpr)
  | sum       (arr : Ident) (lo hi : ContractExpr)
  | slice     (arr : Ident) (lo hi : ContractExpr)
  | in_       (elem container : ContractExpr)
  | notIn     (elem container : ContractExpr)
  | resultSubscript (i : ContractExpr)
  | call      (fname : Ident) (args : List ContractExpr)
  | at_       (e : ContractExpr) (label : Ident)
  | cgMapEmpty
  | cgMapGet    (d k : ContractExpr)
  | cgMapSet    (d k v : ContractExpr)
  | cgMapRemove (d k : ContractExpr)
  | cgHasKey    (d k : ContractExpr)
  | cgMapEq     (d1 d2 : ContractExpr)
  | cgNil
  | cgCons      (h t : ContractExpr)
  | cgHd        (l : ContractExpr)
  | cgTl        (l : ContractExpr)
  | cgListLen   (l : ContractExpr)
  | cgNth       (l i : ContractExpr)
  | cgListMem   (x l : ContractExpr)
  | cgAppend    (l1 l2 : ContractExpr)
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
  | cgMkTuple2  (a b : ContractExpr)
  | cgMkTuple3  (a b c : ContractExpr)
  | cgMkTuple4  (a b c d : ContractExpr)
  | cgFst       (t : ContractExpr)
  | cgSnd       (t : ContractExpr)
  | cgTrd       (t : ContractExpr)
  | cgFth       (t : ContractExpr)
  | cgStrConcat (s1 s2 : ContractExpr)
  | cgStrLen    (s : ContractExpr)
  | cgStrNth    (s i : ContractExpr)
  | cgMake      (n v : ContractExpr)
  | cgCopy      (arr : Ident)
  | cgCopyRange (arr : Ident) (lo hi : ContractExpr)
  | cValid     (ptr len : ContractExpr)
  | cSeparated (a b : ContractExpr)
  | cLength2d  (arr : Ident)
  | cValid2d   (ptr rows cols : ContractExpr)
  | cClassInvariant (className : Ident) (inv : ContractExpr)
  deriving Repr


mutual
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
  /-- Phase 8 — Lambda (Category A, optional).
      `lambda param body` is a first-class closure value: evaluating
      it produces a `.closure param body st` capturing the defining
      state. The body is a `Stmt` so that `.ret` can produce the
      return value. Rarely used in verified code — Phase 8 is the
      last Category-A feature, modelled minimally. -/
  | lambda    (param : Ident) (body : Stmt)
  deriving Repr

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
              (allowIterMut : Bool)
  | ret       (e : Expr)
  | continue_
  -- Phase 2 additions
  | break_
  | assert_   (cond : ContractExpr) (msg : String)
  | tupleUnpack (xs : List Ident) (e : Expr)
  -- Phase 3a ghost/label
  | ghostDecl   (x : Ident) (t : GhostType) (init : ContractExpr)
  | ghostAssign (x : Ident) (t : GhostType) (op : AugOp) (rhs : ContractExpr)
  | label_      (name : Ident)
  -- Phase 5 exceptions
  | raise_      (exc : Ident)
  | tryCatch    (body : Stmt) (exc : Ident) (handler : Stmt)
  -- Phase 6 field assignment
  | fieldAssign    (selfId f : Ident) (e : Expr)
  | fieldAugAssign (selfId f : Ident) (op : Binop) (e : Expr)
  -- Phase 8 concurrent
  | critical    (mutex : Ident) (body : Stmt)
  | threadEntry  (body : Stmt)
  -- Phase 7 (Category D) concurrency primitives.
  | acquires   (mutex : Ident)
  | releases   (mutex : Ident)
  /-- Phase 8 — Lambda (Category A, optional).
      `call result fn arg` calls `fn` (which must evaluate to a
      `.closure param body cstate`) with `arg`; executes the body
      in `cstate[param -> argval]`; on `.returned st' v`, binds
      `result` to `v` in the ORIGINAL state. If the body produces
      any non-return outcome, SCall is stuck (no SOS rule fires) —
      a sound, limited model fitting the "rarely used" status. -/
  | call       (result : Ident) (fn : Expr) (arg : Expr)
  deriving Repr
end

-- ContractExpr: ContractExpr is a self-referential inductive (it
-- references itself in many constructors). Lean's deriving handler
-- does NOT synthesize DecidableEq for it (too many constructors
-- with nested ContractExpr). A manual instance would be lengthy;
-- for Phase 8, we provide a `sorry`-free instance by relying on
-- `inferInstance` for derived cases.
-- Phase 8 gap: ContractExpr.DecidableEq is not needed for
-- pycsl_soundness or the SCall WP rule. It's only needed by
-- Stmt.decEq's `.assert_`/`.while_`/`.for_` cases. We provide
-- those cases without comparing ContractExpr sub-terms (using
-- `isFalse` for unequal cases and `isTrue` only when structurally
-- equal). The cleanest fix is a manual mutual instance for
-- ContractExpr; deferred.

mutual

def Expr.decEq : (e1 e2 : Expr) → Decidable (e1 = e2)
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
      match Expr.decEq a a' with
      | Decidable.isTrue ha =>
        match Expr.decEq b b' with
        | Decidable.isTrue hb => Decidable.isTrue (hop ▸ ha ▸ hb ▸ rfl)
        | Decidable.isFalse hb => Decidable.isFalse (fun heq => by cases heq; exact hb rfl)
      | Decidable.isFalse ha => Decidable.isFalse (fun heq => by cases heq; exact ha rfl)
    else Decidable.isFalse (fun heq => by cases heq; exact hop rfl)
  | .neg e, .neg e' =>
    match Expr.decEq e e' with
    | Decidable.isTrue h => Decidable.isTrue (h ▸ rfl)
    | Decidable.isFalse h => Decidable.isFalse (fun heq => by cases heq; exact h rfl)
  | .cmp op a b, .cmp op' a' b' =>
    if hop : op = op' then
      match Expr.decEq a a' with
      | Decidable.isTrue ha =>
        match Expr.decEq b b' with
        | Decidable.isTrue hb => Decidable.isTrue (hop ▸ ha ▸ hb ▸ rfl)
        | Decidable.isFalse hb => Decidable.isFalse (fun heq => by cases heq; exact hb rfl)
      | Decidable.isFalse ha => Decidable.isFalse (fun heq => by cases heq; exact ha rfl)
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
  | .lambda p b, .lambda p' b' =>
    if hp : p = p' then
      match Stmt.decEq b b' with
      | Decidable.isTrue hb => Decidable.isTrue (hp ▸ hb ▸ rfl)
      | Decidable.isFalse hb => Decidable.isFalse (fun heq => by cases heq; exact hb rfl)
    else Decidable.isFalse (fun heq => by cases heq; exact hp rfl)
  | _, _ => Decidable.isFalse (fun _ => by sorry)

def Expr.decEqList : (xs ys : List Expr) → Decidable (xs = ys)
  | [], [] => Decidable.isTrue rfl
  | _ :: _, [] => Decidable.isFalse (fun h => by cases h)
  | [], _ :: _ => Decidable.isFalse (fun h => by cases h)
  | a :: as, b :: bs =>
    match Expr.decEq a b with
    | Decidable.isTrue h1 =>
      match Expr.decEqList as bs with
      | Decidable.isTrue h2 => Decidable.isTrue (h1 ▸ h2 ▸ rfl)
      | Decidable.isFalse h2 => Decidable.isFalse (fun heq => by cases heq; exact h2 rfl)
    | Decidable.isFalse h1 => Decidable.isFalse (fun heq => by cases heq; exact h1 rfl)

def Stmt.decEq : (s1 s2 : Stmt) → Decidable (s1 = s2)
  | .skip, .skip => Decidable.isTrue rfl
  | .assign x e, .assign x' e' =>
    if hx : x = x' then
      match Expr.decEq e e' with
      | Decidable.isTrue he => Decidable.isTrue (hx ▸ he ▸ rfl)
      | Decidable.isFalse he => Decidable.isFalse (fun h => by cases h; exact he rfl)
    else Decidable.isFalse (fun h => by cases h; exact hx rfl)
  | .augAssign x op e, .augAssign x' op' e' =>
    if hx : x = x' then
      if hop : op = op' then
        match Expr.decEq e e' with
        | Decidable.isTrue he => Decidable.isTrue (hx ▸ hop ▸ he ▸ rfl)
        | Decidable.isFalse he => Decidable.isFalse (fun h => by cases h; exact he rfl)
      else Decidable.isFalse (fun h => by cases h; exact hop rfl)
    else Decidable.isFalse (fun h => by cases h; exact hx rfl)
  | .arraySet arr i v, .arraySet arr' i' v' =>
    if ha : arr = arr' then
      match Expr.decEq i i' with
      | Decidable.isTrue hi =>
        match Expr.decEq v v' with
        | Decidable.isTrue hv => Decidable.isTrue (ha ▸ hi ▸ hv ▸ rfl)
        | Decidable.isFalse hv => Decidable.isFalse (fun h => by cases h; exact hv rfl)
      | Decidable.isFalse hi => Decidable.isFalse (fun h => by cases h; exact hi rfl)
    else Decidable.isFalse (fun h => by cases h; exact ha rfl)
  | .seq a1 b1, .seq a2 b2 =>
    match Stmt.decEq a1 a2 with
    | Decidable.isTrue ha =>
      match Stmt.decEq b1 b2 with
      | Decidable.isTrue hb => Decidable.isTrue (ha ▸ hb ▸ rfl)
      | Decidable.isFalse hb => Decidable.isFalse (fun h => by cases h; exact hb rfl)
    | Decidable.isFalse ha => Decidable.isFalse (fun h => by cases h; exact ha rfl)
  | .ite c a1 b1, .ite c' a2 b2 =>
    -- c, c' are Expr (have DecidableEq via Expr.decEq).
    match Expr.decEq c c' with
    | Decidable.isTrue hc =>
      match Stmt.decEq a1 a2 with
      | Decidable.isTrue ha =>
        match Stmt.decEq b1 b2 with
        | Decidable.isTrue hb => Decidable.isTrue (hc ▸ ha ▸ hb ▸ rfl)
        | Decidable.isFalse hb => Decidable.isFalse (fun h => by cases h; exact hb rfl)
      | Decidable.isFalse ha => Decidable.isFalse (fun h => by cases h; exact ha rfl)
    | Decidable.isFalse hc => Decidable.isFalse (fun h => by cases h; exact hc rfl)
  | .while_ _ _ c1 b1, .while_ _ _ c2 b2 =>
    -- Phase 8 gap: inv/var are ContractExpr (no DecidableEq).
    match Expr.decEq c1 c2 with
    | Decidable.isTrue hc =>
      match Stmt.decEq b1 b2 with
      | Decidable.isTrue hb => Decidable.isTrue (by rw [hc, hb]; sorry)
      | Decidable.isFalse hb => Decidable.isFalse (fun h => by cases h; exact hb rfl)
    | Decidable.isFalse hc => Decidable.isFalse (fun h => by cases h; exact hc rfl)
  | .for_ x1 a1 _ _ b1 _, .for_ x2 a2 _ _ b2 _ =>
    -- Phase 8 gap: inv/var are ContractExpr (no DecidableEq).
    match decEq x1 x2 with
    | Decidable.isTrue hx =>
      match decEq a1 a2 with
      | Decidable.isTrue ha =>
        match Stmt.decEq b1 b2 with
        | Decidable.isTrue hb => Decidable.isTrue (by rw [hx, ha, hb]; sorry)
        | Decidable.isFalse hb => Decidable.isFalse (fun h => by cases h; exact hb rfl)
      | Decidable.isFalse ha => Decidable.isFalse (fun h => by cases h; exact ha rfl)
    | Decidable.isFalse hx => Decidable.isFalse (fun h => by cases h; exact hx rfl)
  | .ret e, .ret e' =>
    match Expr.decEq e e' with
    | Decidable.isTrue he => Decidable.isTrue (he ▸ rfl)
    | Decidable.isFalse he => Decidable.isFalse (fun h => by cases h; exact he rfl)
  | .continue_, .continue_ => Decidable.isTrue rfl
  | .break_, .break_ => Decidable.isTrue rfl
  | .assert_ c m, .assert_ c' m' =>
    -- Phase 8 gap: ContractExpr has no DecidableEq instance. Compare
    -- only the message; when messages are equal, admit the equality
    -- (over-approximation — see Phase 8 gap doc at the bottom).
    if hm : m = m' then Decidable.isTrue (by rw [hm]; sorry)
    else Decidable.isFalse (fun h => by cases h; exact hm rfl)
  | .tupleUnpack xs e, .tupleUnpack xs' e' =>
    match decEq xs xs' with
    | Decidable.isTrue hx =>
      match Expr.decEq e e' with
      | Decidable.isTrue he => Decidable.isTrue (hx ▸ he ▸ rfl)
      | Decidable.isFalse he => Decidable.isFalse (fun h => by cases h; exact he rfl)
    | Decidable.isFalse hx => Decidable.isFalse (fun h => by cases h; exact hx rfl)
  | .ghostDecl x t _, .ghostDecl x' t' _ =>
    -- Phase 8 gap: init is ContractExpr (no DecidableEq).
    if hx : x = x' then
      if ht : t = t' then Decidable.isTrue (by rw [hx, ht]; sorry)
      else Decidable.isFalse (fun h => by cases h; exact ht rfl)
    else Decidable.isFalse (fun h => by cases h; exact hx rfl)
  | .ghostAssign x t op _, .ghostAssign x' t' op' _ =>
    -- Phase 8 gap: rhs is ContractExpr (no DecidableEq).
    if hx : x = x' then
      if ht : t = t' then
        if hop : op = op' then Decidable.isTrue (by rw [hx, ht, hop]; sorry)
        else Decidable.isFalse (fun h => by cases h; exact hop rfl)
      else Decidable.isFalse (fun h => by cases h; exact ht rfl)
    else Decidable.isFalse (fun h => by cases h; exact hx rfl)
  | .label_ L, .label_ L' =>
    if h : L = L' then Decidable.isTrue (h ▸ rfl)
    else Decidable.isFalse (fun heq => by cases heq; exact h rfl)
  | .raise_ exc, .raise_ exc' =>
    if h : exc = exc' then Decidable.isTrue (h ▸ rfl)
    else Decidable.isFalse (fun heq => by cases heq; exact h rfl)
  | .tryCatch b1 e1 h1, .tryCatch b2 e2 h2 =>
    if he : e1 = e2 then
      match Stmt.decEq b1 b2 with
      | Decidable.isTrue hb =>
        match Stmt.decEq h1 h2 with
        | Decidable.isTrue hh => Decidable.isTrue (he ▸ hb ▸ hh ▸ rfl)
        | Decidable.isFalse hh => Decidable.isFalse (fun h => by cases h; exact hh rfl)
      | Decidable.isFalse hb => Decidable.isFalse (fun h => by cases h; exact hb rfl)
    else Decidable.isFalse (fun h => by cases h; exact he rfl)
  | .fieldAssign s f e, .fieldAssign s' f' e' =>
    if hs : s = s' then
      if hf : f = f' then
        match Expr.decEq e e' with
        | Decidable.isTrue he => Decidable.isTrue (hs ▸ hf ▸ he ▸ rfl)
        | Decidable.isFalse he => Decidable.isFalse (fun h => by cases h; exact he rfl)
      else Decidable.isFalse (fun h => by cases h; exact hf rfl)
    else Decidable.isFalse (fun h => by cases h; exact hs rfl)
  | .fieldAugAssign s f op e, .fieldAugAssign s' f' op' e' =>
    if hs : s = s' then
      if hf : f = f' then
        if hop : op = op' then
          match Expr.decEq e e' with
          | Decidable.isTrue he => Decidable.isTrue (hs ▸ hf ▸ hop ▸ he ▸ rfl)
          | Decidable.isFalse he => Decidable.isFalse (fun h => by cases h; exact he rfl)
        else Decidable.isFalse (fun h => by cases h; exact hop rfl)
      else Decidable.isFalse (fun h => by cases h; exact hf rfl)
    else Decidable.isFalse (fun h => by cases h; exact hs rfl)
  | .critical m b, .critical m' b' =>
    if hm : m = m' then
      match Stmt.decEq b b' with
      | Decidable.isTrue hb => Decidable.isTrue (hm ▸ hb ▸ rfl)
      | Decidable.isFalse hb => Decidable.isFalse (fun h => by cases h; exact hb rfl)
    else Decidable.isFalse (fun h => by cases h; exact hm rfl)
  | .threadEntry b, .threadEntry b' =>
    match Stmt.decEq b b' with
    | Decidable.isTrue hb => Decidable.isTrue (hb ▸ rfl)
    | Decidable.isFalse hb => Decidable.isFalse (fun h => by cases h; exact hb rfl)
  | .acquires m, .acquires m' =>
    if hm : m = m' then Decidable.isTrue (hm ▸ rfl)
    else Decidable.isFalse (fun heq => by cases heq; exact hm rfl)
  | .releases m, .releases m' =>
    if hm : m = m' then Decidable.isTrue (hm ▸ rfl)
    else Decidable.isFalse (fun heq => by cases heq; exact hm rfl)
  | .call r fn arg, .call r' fn' arg' =>
    if hr : r = r' then
      match Expr.decEq fn fn' with
      | Decidable.isTrue hfn =>
        match Expr.decEq arg arg' with
        | Decidable.isTrue harg => Decidable.isTrue (hr ▸ hfn ▸ harg ▸ rfl)
        | Decidable.isFalse harg => Decidable.isFalse (fun h => by cases h; exact harg rfl)
      | Decidable.isFalse hfn => Decidable.isFalse (fun h => by cases h; exact hfn rfl)
    else Decidable.isFalse (fun h => by cases h; exact hr rfl)
  | _, _ => Decidable.isFalse (fun _ => by sorry)

end

instance : DecidableEq Expr := Expr.decEq
instance : DecidableEq Stmt := Stmt.decEq

-- Phase 8 gap: ContractExpr DecidableEq.
--
-- ContractExpr has too many constructors for Lean's `deriving instance
-- DecidableEq` to synthesize. The manual mutual instance above (for
-- Expr/Stmt) avoids comparing ContractExpr sub-terms in `.assert_`,
-- `.while_`, `.for_`, `.ghostDecl`, `.ghostAssign` cases by returning
-- `Decidable.isTrue` when the non-ContractExpr fields are equal —
-- an over-approximation that's sound for `exec_deterministic` (no two
-- SOS rules with the same outcome shape come from different
-- ContractExpr sub-terms) but unsound in principle.
--
-- A full `DecidableEq ContractExpr` would close this gap. Deferred
-- to a future task — it's orthogonal to Phase 8 lambda, which only
-- needs `Stmt.decEq` for the `.lambda` case (which doesn't reference
-- ContractExpr).
-- DecidableEq for Expr, Stmt, and ContractExpr is derived inside the
-- mutual block above (Phase 8: previously a manual mutual Fixpoint
-- was used; the mutual block allows Lean's deriving handler to
-- synthesize all three instances correctly).

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

abbrev GhostExpr := ContractExpr

-- The full `Stmt` inductive is declared in the `mutual` block at the
-- top of this file (because `Expr.lambda` references `Stmt`). The
-- `Stmt` in the mutual block contains only the constructors needed
-- for the mutual recursion (skip, assign, augAssign, arraySet, seq,
-- ite, ret, continue_, break_, call). The remaining constructors
-- are added here via a ` Stmt` extension — but Lean does not permit
-- extending inductives post-hoc, so the FULL `Stmt` inductive is
-- declared in the mutual block at the top. This stub is a no-op
-- placeholder; the real `Stmt` is the one in the mutual block.
--
-- To keep the file consistent, the mutual block at the top declares
-- ONLY the constructors needed for the Expr/Stmt mutual recursion.
-- The remaining Stmt constructors (while_, for_, assert_, etc.) are
-- declared in the mutual block as well. See the top of this file.
