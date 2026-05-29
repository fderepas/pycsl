/-
  CorrMain.lean — Full WP Correspondence Theorem
  Combines CorrSimple, CorrLoops, CorrExc into the master theorem by
  structural induction on s:

    theorem wpGenCorrect :
      ∀ (s : Stmt) (Qn Qr Qc Qb : ExecState → Prop)
        (Qe : Ident → ExecState → Prop) (preEs es : ExecState),
      wp s Qn Qr Qc Qb Qe preEs es ↔
      wpW (gen s) (enc Qn Qr Qc Qb Qe) preEs es.

  Simple cases dispatch to CorrSimple lemmas.
  Inductive cases use CorrLoops and CorrExc lemmas with the IH.
-/
import PyCSL.AST
import PyCSL.State
import PyCSL.WP
import PyCSL.WhyML
import PyCSL.WPW
import PyCSL.StmtGen
import PyCSL.CorrSimple
import PyCSL.CorrLoops
import PyCSL.CorrExc

-- ===== Master WP correspondence theorem =====

theorem wpGenCorrect (s : Stmt) :
    ∀ (Qn Qr Qc Qb : ExecState → Prop) (Qe : Ident → ExecState → Prop)
      (preEs es : ExecState),
    wp s Qn Qr Qc Qb Qe preEs es ↔
    wpW (gen s) (enc Qn Qr Qc Qb Qe) preEs es := by
  induction s with
  | skip =>
    intros; exact wpGen_skip _ _ _ _ _ _ _
  | assign x e =>
    intros; exact wpGen_assign x e _ _ _ _ _ _ _
  | augAssign x op e =>
    intros; exact wpGen_augAssign x op e _ _ _ _ _ _ _
  | arraySet arr i v =>
    intros; exact wpGen_arraySet arr i v _ _ _ _ _ _ _
  | ret e =>
    intros; exact wpGen_return e _ _ _ _ _ _ _
  | continue_ =>
    intros; exact wpGen_continue _ _ _ _ _ _ _
  | break_ =>
    intros; exact wpGen_break _ _ _ _ _ _ _
  | assert_ cond msg =>
    intros; exact wpGen_assert cond msg _ _ _ _ _ _ _
  | tupleUnpack xs e =>
    intros; exact wpGen_tupleUnpack xs e _ _ _ _ _ _ _
  | ghostDecl x t e =>
    intros; exact wpGen_ghostDecl x t e _ _ _ _ _ _ _
  | ghostAssign x t op e =>
    intros; exact wpGen_ghostAssign x t op e _ _ _ _ _ _ _
  | label_ L =>
    intros; exact wpGen_label L _ _ _ _ _ _ _
  | raise_ exc =>
    intros; exact wpGen_raise exc _ _ _ _ _ _ _
  | fieldAssign selfId f e =>
    intros; exact wpGen_fieldAssign selfId f e _ _ _ _ _ _ _
  | fieldAugAssign selfId f op e =>
    intros; exact wpGen_fieldAugAssign selfId f op e _ _ _ _ _ _ _
  | seq s1 s2 ih1 ih2 =>
    intros Qn Qr Qc Qb Qe preEs es
    exact wpGen_seq s1 s2 Qn Qr Qc Qb Qe preEs es ih1 ih2
  | ite cond s1 s2 ih1 ih2 =>
    intros Qn Qr Qc Qb Qe preEs es
    exact wpGen_if cond s1 s2 Qn Qr Qc Qb Qe preEs es ih1 ih2
  | while_ inv var cond body ih =>
    intros Qn Qr Qc Qb Qe preEs es
    exact wpGen_while inv var cond body Qn Qr Qc Qb Qe preEs es ih
  | for_ x arr inv var body aim ih =>
    intros Qn Qr Qc Qb Qe preEs es
    exact wpGen_for x arr inv var body aim Qn Qr Qc Qb Qe preEs es ih
  | tryCatch s exc handler ih1 ih2 =>
    intros Qn Qr Qc Qb Qe preEs es
    exact wpGen_tryCatch s handler exc Qn Qr Qc Qb Qe preEs es ih1 ih2
  | critical mutex body ih =>
    intros Qn Qr Qc Qb Qe preEs es
    exact wpGen_critical mutex body Qn Qr Qc Qb Qe preEs es ih
  | threadEntry body ih =>
    intros Qn Qr Qc Qb Qe preEs es
    exact wpGen_threadEntry body Qn Qr Qc Qb Qe preEs es ih

-- ===== Corollary: wpW (gen s) implies wp s =====

theorem wpW_gen_implies_wp
    (s : Stmt) (Qn Qr Qc Qb : ExecState → Prop) (Qe : Ident → ExecState → Prop)
    (preEs es : ExecState)
    (h : wpW (gen s) (enc Qn Qr Qc Qb Qe) preEs es) :
    wp s Qn Qr Qc Qb Qe preEs es :=
  (wpGenCorrect s Qn Qr Qc Qb Qe preEs es).mpr h
