/-
  CorrSimple.lean — WP Correspondence for Simple Statements
  Proves wp s Qn Qr Qc Qb Qe preEs es ↔ wpW (gen s) (enc Qn Qr Qc Qb Qe) preEs es
  for all non-loop, non-try-catch Stmt constructors.
  Every case follows by simp unfolding.
-/
import PyCSL.AST
import PyCSL.State
import PyCSL.WP
import PyCSL.WhyML
import PyCSL.WPW
import PyCSL.ExprTrans
import PyCSL.StmtGen

theorem wpGen_skip (Qn Qr Qc Qb : ExecState → Prop) (Qe : Ident → ExecState → Prop)
    (preEs es : ExecState) :
    wp .skip Qn Qr Qc Qb Qe preEs es ↔ wpW (gen .skip) (enc Qn Qr Qc Qb Qe) preEs es := by
  simp [wp, gen, wpW, enc]

theorem wpGen_assign (x : Ident) (e : Expr)
    (Qn Qr Qc Qb : ExecState → Prop) (Qe : Ident → ExecState → Prop)
    (preEs es : ExecState) :
    wp (.assign x e) Qn Qr Qc Qb Qe preEs es ↔
    wpW (gen (.assign x e)) (enc Qn Qr Qc Qb Qe) preEs es := by
  simp [wp, gen, wpW, enc]

theorem wpGen_augAssign (x : Ident) (op : Binop) (e : Expr)
    (Qn Qr Qc Qb : ExecState → Prop) (Qe : Ident → ExecState → Prop)
    (preEs es : ExecState) :
    wp (.augAssign x op e) Qn Qr Qc Qb Qe preEs es ↔
    wpW (gen (.augAssign x op e)) (enc Qn Qr Qc Qb Qe) preEs es := by
  -- simp reduces both sides to Qn (setReg ...) but leaves A ↔ A unclosed
  -- (match wildcards elaborate separately); close with id/id
  constructor <;> intro h <;> simpa [wp, gen, wpW, enc] using h

theorem wpGen_arraySet (arr : Ident) (i v : Expr)
    (Qn Qr Qc Qb : ExecState → Prop) (Qe : Ident → ExecState → Prop)
    (preEs es : ExecState) :
    wp (.arraySet arr i v) Qn Qr Qc Qb Qe preEs es ↔
    wpW (gen (.arraySet arr i v)) (enc Qn Qr Qc Qb Qe) preEs es := by
  constructor <;> intro h <;> simpa [wp, gen, wpW, enc] using h

-- SReturn: gen (SReturn e) = WSeq (WAssign "\result" e) (WRaise excReturn)
-- wp_w unfolds: wc_r applied to set_reg … = Qr (set_reg …) = wp (SReturn e) …
theorem wpGen_return (e : Expr)
    (Qn Qr Qc Qb : ExecState → Prop) (Qe : Ident → ExecState → Prop)
    (preEs es : ExecState) :
    wp (.ret e) Qn Qr Qc Qb Qe preEs es ↔
    wpW (gen (.ret e)) (enc Qn Qr Qc Qb Qe) preEs es := by
  simp [wp, gen, wpW, enc]

theorem wpGen_continue
    (Qn Qr Qc Qb : ExecState → Prop) (Qe : Ident → ExecState → Prop)
    (preEs es : ExecState) :
    wp .continue_ Qn Qr Qc Qb Qe preEs es ↔
    wpW (gen .continue_) (enc Qn Qr Qc Qb Qe) preEs es := by
  simp [wp, gen, wpW, enc]

theorem wpGen_break
    (Qn Qr Qc Qb : ExecState → Prop) (Qe : Ident → ExecState → Prop)
    (preEs es : ExecState) :
    wp .break_ Qn Qr Qc Qb Qe preEs es ↔
    wpW (gen .break_) (enc Qn Qr Qc Qb Qe) preEs es := by
  simp [wp, gen, wpW, enc]

theorem wpGen_assert (cond : ContractExpr) (msg : String)
    (Qn Qr Qc Qb : ExecState → Prop) (Qe : Ident → ExecState → Prop)
    (preEs es : ExecState) :
    wp (.assert_ cond msg) Qn Qr Qc Qb Qe preEs es ↔
    wpW (gen (.assert_ cond msg)) (enc Qn Qr Qc Qb Qe) preEs es := by
  simp [wp, gen, wpW, enc]

theorem wpGen_ghostDecl (x : Ident) (t : GhostType) (e : GhostExpr)
    (Qn Qr Qc Qb : ExecState → Prop) (Qe : Ident → ExecState → Prop)
    (preEs es : ExecState) :
    wp (.ghostDecl x t e) Qn Qr Qc Qb Qe preEs es ↔
    wpW (gen (.ghostDecl x t e)) (enc Qn Qr Qc Qb Qe) preEs es := by
  simp [wp, gen, wpW, enc]

theorem wpGen_ghostAssign (x : Ident) (t : GhostType) (op : AugOp) (e : GhostExpr)
    (Qn Qr Qc Qb : ExecState → Prop) (Qe : Ident → ExecState → Prop)
    (preEs es : ExecState) :
    wp (.ghostAssign x t op e) Qn Qr Qc Qb Qe preEs es ↔
    wpW (gen (.ghostAssign x t op e)) (enc Qn Qr Qc Qb Qe) preEs es := by
  simp [wp, gen, wpW, enc]

theorem wpGen_label (L : Ident)
    (Qn Qr Qc Qb : ExecState → Prop) (Qe : Ident → ExecState → Prop)
    (preEs es : ExecState) :
    wp (.label_ L) Qn Qr Qc Qb Qe preEs es ↔
    wpW (gen (.label_ L)) (enc Qn Qr Qc Qb Qe) preEs es := by
  simp [wp, gen, wpW, enc]

theorem wpGen_raise (exc : Ident)
    (Qn Qr Qc Qb : ExecState → Prop) (Qe : Ident → ExecState → Prop)
    (preEs es : ExecState) :
    wp (.raise_ exc) Qn Qr Qc Qb Qe preEs es ↔
    wpW (gen (.raise_ exc)) (enc Qn Qr Qc Qb Qe) preEs es := by
  simp [wp, gen, wpW, enc]

theorem wpGen_tupleUnpack (xs : List Ident) (e : Expr)
    (Qn Qr Qc Qb : ExecState → Prop) (Qe : Ident → ExecState → Prop)
    (preEs es : ExecState) :
    wp (.tupleUnpack xs e) Qn Qr Qc Qb Qe preEs es ↔
    wpW (gen (.tupleUnpack xs e)) (enc Qn Qr Qc Qb Qe) preEs es := by
  simp [wp, gen, wpW, enc]

theorem wpGen_fieldAssign (selfId f : Ident) (e : Expr)
    (Qn Qr Qc Qb : ExecState → Prop) (Qe : Ident → ExecState → Prop)
    (preEs es : ExecState) :
    wp (.fieldAssign selfId f e) Qn Qr Qc Qb Qe preEs es ↔
    wpW (gen (.fieldAssign selfId f e)) (enc Qn Qr Qc Qb Qe) preEs es := by
  simp [wp, gen, wpW, enc]

theorem wpGen_fieldAugAssign (selfId f : Ident) (op : Binop) (e : Expr)
    (Qn Qr Qc Qb : ExecState → Prop) (Qe : Ident → ExecState → Prop)
    (preEs es : ExecState) :
    wp (.fieldAugAssign selfId f op e) Qn Qr Qc Qb Qe preEs es ↔
    wpW (gen (.fieldAugAssign selfId f op e)) (enc Qn Qr Qc Qb Qe) preEs es := by
  simp [wp, gen, wpW, enc]
