/-
  Desugar.lean — Desugaring correctness theorem
  Mirror of Phase3b_Desugar.v (all phases)

  desugar_correct : freshInStmt forIdx s = true →
    Exec es s out ↔ Exec es (desugar s) out
-/
import PyCSL.AST
import PyCSL.State
import PyCSL.SOS
import PyCSL.DesugarDef

-- =====================================================================
-- Helper: backward direction for while loops
-- Uses suffices+generalize trick to allow induction on the Exec derivation
-- =====================================================================

private theorem bwd_while_aux {b : Stmt}
    (ih_b : ∀ (es : ExecState) (out : Outcome), Exec es (desugar b) out → Exec es b out)
    {es : ExecState} {out : Outcome} {inv var : ContractExpr} {cond : Expr}
    (hd : Exec es (.while_ inv var cond (desugar b)) out) :
    Exec es (.while_ inv var cond b) out := by
  suffices h : ∀ {sw : Stmt}, Exec es sw out →
      sw = .while_ inv var cond (desugar b) → Exec es (.while_ inv var cond b) out from
    h hd rfl
  intro sw hd' heq
  induction hd' generalizing inv var cond with
  -- While cases: handle via injection + subst + IH
  | execWhileTrue _ _ _ _ _ _ _ hcond hbody hrec ih_body ih_rec =>
    injection heq with h1 h2 h3 h4; subst h1; subst h2; subst h3; subst h4
    exact .execWhileTrue _ _ _ _ _ _ _ hcond (ih_b _ _ hbody) (ih_rec hrec rfl)
  | execWhileContinue _ _ _ _ _ _ _ hcond hbody hrec ih_body ih_rec =>
    injection heq with h1 h2 h3 h4; subst h1; subst h2; subst h3; subst h4
    exact .execWhileContinue _ _ _ _ _ _ _ hcond (ih_b _ _ hbody) (ih_rec hrec rfl)
  | execWhileBreak _ _ _ _ _ _ hcond hbody ih_body =>
    injection heq with h1 h2 h3 h4; subst h1; subst h2; subst h3; subst h4
    exact .execWhileBreak _ _ _ _ _ _ hcond (ih_b _ _ hbody)
  | execWhileFalse _ _ _ _ _ hcond =>
    injection heq with h1 h2 h3 h4; subst h1; subst h2; subst h3; subst h4
    exact .execWhileFalse _ _ _ _ _ hcond
  -- All other constructors: heq is contradictory (non-while stmt ≠ while_)
  | execSkip _ => simp at heq
  | execAssign _ _ _ => simp at heq
  | execAugAssign _ _ _ _ => simp at heq
  | execArraySet _ _ _ _ => simp at heq
  | execSeq _ _ _ _ _ _ _ _ _ => simp at heq
  | execSeqReturn _ _ _ _ _ _ _ => simp at heq
  | execSeqContinue _ _ _ _ _ _ => simp at heq
  | execSeqBreak _ _ _ _ _ _ => simp at heq
  | execSeqThrow _ _ _ _ _ _ _ => simp at heq
  | execIfTrue _ _ _ _ _ _ _ _ => simp at heq
  | execIfFalse _ _ _ _ _ _ _ _ => simp at heq
  | execContinue _ => simp at heq
  | execBreak _ => simp at heq
  | execReturn _ _ => simp at heq
  | execAssertPass _ _ _ _ => simp at heq
  | execAssertFail _ _ _ _ => simp at heq
  | execTupleUnpack _ _ _ => simp at heq
  | execGhostDecl _ _ _ _ => simp at heq
  | execGhostAssign _ _ _ _ _ => simp at heq
  | execLabel _ _ => simp at heq
  | execRaise _ _ => simp at heq
  | execTryCatchCaught _ _ _ _ _ _ _ _ _ _ => simp at heq
  | execTryCatchMiss _ _ _ _ _ _ _ _ _ => simp at heq
  | execTryCatchNormal _ _ _ _ _ _ _ _ => simp at heq
  | execFieldAssign _ _ _ _ => simp at heq
  | execFieldAugAssign _ _ _ _ _ => simp at heq
  | execCritical _ _ _ _ _ _ => simp at heq
  | execThreadEntry _ _ _ _ _ => simp at heq
  | execFor _ _ _ _ _ _ _ _ _ _ => simp at heq

-- =====================================================================
-- Forward direction: Exec es s out → Exec es (desugar s) out
-- =====================================================================

theorem desugar_correct_fwd (es : ExecState) (s : Stmt) (out : Outcome)
    (hfresh : freshInStmt forIdx s = true)
    (h : Exec es s out) : Exec es (desugar s) out := by
  induction h with
  -- Leaf cases: desugar is identity
  | execSkip _ => exact .execSkip _
  | execAssign _ _ _ => exact .execAssign ..
  | execAugAssign _ _ _ _ => exact .execAugAssign ..
  | execArraySet _ _ _ _ => exact .execArraySet ..
  | execContinue _ => exact .execContinue _
  | execBreak _ => exact .execBreak _
  | execReturn _ _ => exact .execReturn ..
  | execAssertPass _ _ _ hpass => exact .execAssertPass _ _ _ hpass
  | execAssertFail _ _ _ hfail => exact .execAssertFail _ _ _ hfail
  | execTupleUnpack _ _ _ => exact .execTupleUnpack ..
  | execGhostDecl _ _ _ _ => exact .execGhostDecl ..
  | execGhostAssign _ _ _ _ _ => exact .execGhostAssign ..
  | execLabel _ _ => exact .execLabel ..
  | execRaise _ _ => exact .execRaise ..
  | execFieldAssign _ _ _ _ => exact .execFieldAssign ..
  | execFieldAugAssign _ _ _ _ _ => exact .execFieldAugAssign ..
  -- Seq cases: desugar (.seq s1 s2) = .seq (desugar s1) (desugar s2)
  | execSeq _ _ _ _ _ _ _ ih1 ih2 =>
    simp only [freshInStmt, Bool.and_eq_true] at hfresh
    exact .execSeq _ _ _ _ _ (ih1 hfresh.1) (ih2 hfresh.2)
  | execSeqReturn _ _ _ _ _ _ ih1 =>
    simp only [freshInStmt, Bool.and_eq_true] at hfresh
    exact .execSeqReturn _ _ _ _ _ (ih1 hfresh.1)
  | execSeqContinue _ _ _ _ _ ih1 =>
    simp only [freshInStmt, Bool.and_eq_true] at hfresh
    exact .execSeqContinue _ _ _ _ (ih1 hfresh.1)
  | execSeqBreak _ _ _ _ _ ih1 =>
    simp only [freshInStmt, Bool.and_eq_true] at hfresh
    exact .execSeqBreak _ _ _ _ (ih1 hfresh.1)
  | execSeqThrow _ _ _ _ _ _ ih1 =>
    simp only [freshInStmt, Bool.and_eq_true] at hfresh
    exact .execSeqThrow _ _ _ _ _ (ih1 hfresh.1)
  -- If cases: desugar (.ite c s1 s2) = .ite c (desugar s1) (desugar s2)
  | execIfTrue _ _ _ _ _ hcond _ ih1 =>
    simp only [freshInStmt, Bool.and_eq_true] at hfresh
    exact .execIfTrue _ _ _ _ _ hcond (ih1 hfresh.1)
  | execIfFalse _ _ _ _ _ hcond _ ih1 =>
    simp only [freshInStmt, Bool.and_eq_true] at hfresh
    exact .execIfFalse _ _ _ _ _ hcond (ih1 hfresh.2)
  -- While cases: desugar (.while_ i v c b) = .while_ i v c (desugar b)
  | execWhileTrue _ _ _ _ _ _ _ hcond _ _ ih1 ih2 =>
    simp only [freshInStmt] at hfresh
    exact .execWhileTrue _ _ _ _ _ _ _ hcond (ih1 hfresh) (ih2 hfresh)
  | execWhileContinue _ _ _ _ _ _ _ hcond _ _ ih1 ih2 =>
    simp only [freshInStmt] at hfresh
    exact .execWhileContinue _ _ _ _ _ _ _ hcond (ih1 hfresh) (ih2 hfresh)
  | execWhileBreak _ _ _ _ _ _ hcond _ ih1 =>
    simp only [freshInStmt] at hfresh
    exact .execWhileBreak _ _ _ _ _ _ hcond (ih1 hfresh)
  | execWhileFalse _ _ _ _ _ hcond =>
    exact .execWhileFalse _ _ _ _ _ hcond
  -- TryCatch cases: desugar (.tryCatch b exc h) = .tryCatch (desugar b) exc (desugar h)
  | execTryCatchCaught _ _ _ _ _ _ _ _ ih1 ih2 =>
    simp only [freshInStmt, Bool.and_eq_true] at hfresh
    exact .execTryCatchCaught _ _ _ _ _ _ (ih1 hfresh.1) (ih2 hfresh.2)
  | execTryCatchMiss _ _ _ _ _ _ hne _ ih1 =>
    simp only [freshInStmt, Bool.and_eq_true] at hfresh
    exact .execTryCatchMiss _ _ _ _ _ _ hne (ih1 hfresh.1)
  | execTryCatchNormal _ _ _ _ _ hnot _ ih1 =>
    simp only [freshInStmt, Bool.and_eq_true] at hfresh
    exact .execTryCatchNormal _ _ _ _ _ hnot (ih1 hfresh.1)
  -- Critical: desugar (.critical m b) = .critical m (desugar b)
  | execCritical _ _ _ _ _ ih1 =>
    simp only [freshInStmt] at hfresh
    exact .execCritical _ _ _ _ (ih1 hfresh)
  -- ThreadEntry: desugar (.threadEntry b) = .threadEntry (desugar b)
  | execThreadEntry _ _ _ _ ih1 =>
    simp only [freshInStmt] at hfresh
    exact .execThreadEntry _ _ _ (ih1 hfresh)
  -- For: execFor provides Exec es (desugar .for_...) out directly
  | execFor _ _ _ _ _ _ _ _ h _ => exact h

-- =====================================================================
-- Backward direction: Exec es (desugar s) out → Exec es s out
-- =====================================================================

theorem desugar_correct_bwd (s : Stmt) (es : ExecState) (out : Outcome)
    (hfresh : freshInStmt forIdx s = true)
    (hd : Exec es (desugar s) out) : Exec es s out := by
  match s with
  -- Leaf cases: desugar is identity
  | .skip => exact hd
  | .assign _ _ => exact hd
  | .augAssign _ _ _ => exact hd
  | .arraySet _ _ _ => exact hd
  | .continue_ => exact hd
  | .break_ => exact hd
  | .ret _ => exact hd
  | .assert_ _ _ => exact hd
  | .tupleUnpack _ _ => exact hd
  | .ghostDecl _ _ _ => exact hd
  | .ghostAssign _ _ _ _ => exact hd
  | .label_ _ => exact hd
  | .raise_ _ => exact hd
  | .fieldAssign _ _ _ => exact hd
  | .fieldAugAssign _ _ _ _ => exact hd
  -- For: use execFor rule
  | .for_ _ _ _ _ _ _ => exact .execFor _ _ _ _ _ _ _ _ hd
  -- Seq: case-split on hd to recover sub-execs on desugared s1, s2
  | .seq s1 s2 =>
    simp only [desugar] at hd
    simp only [freshInStmt, Bool.and_eq_true] at hfresh
    cases hd with
    | execSeq _ _ _ es' _ h1 h2 =>
      exact .execSeq _ _ _ es' _
        (desugar_correct_bwd s1 es _ hfresh.1 h1)
        (desugar_correct_bwd s2 es' _ hfresh.2 h2)
    | execSeqReturn _ _ _ es' v h1 =>
      exact .execSeqReturn _ _ _ es' v (desugar_correct_bwd s1 es _ hfresh.1 h1)
    | execSeqContinue _ _ _ es' h1 =>
      exact .execSeqContinue _ _ _ es' (desugar_correct_bwd s1 es _ hfresh.1 h1)
    | execSeqBreak _ _ _ es' h1 =>
      exact .execSeqBreak _ _ _ es' (desugar_correct_bwd s1 es _ hfresh.1 h1)
    | execSeqThrow _ _ _ es' exc h1 =>
      exact .execSeqThrow _ _ _ es' exc (desugar_correct_bwd s1 es _ hfresh.1 h1)
  -- Ite: case-split on hd
  | .ite c s1 s2 =>
    simp only [desugar] at hd
    simp only [freshInStmt, Bool.and_eq_true] at hfresh
    cases hd with
    | execIfTrue _ _ _ _ _ hcond h1 =>
      exact .execIfTrue _ _ _ _ _ hcond (desugar_correct_bwd s1 es _ hfresh.1 h1)
    | execIfFalse _ _ _ _ _ hcond h2 =>
      exact .execIfFalse _ _ _ _ _ hcond (desugar_correct_bwd s2 es _ hfresh.2 h2)
  -- While: use bwd_while_aux which handles loop unrolling
  | .while_ inv var cond body =>
    simp only [freshInStmt] at hfresh
    simp only [desugar] at hd
    exact bwd_while_aux (fun es' out' h => desugar_correct_bwd body es' out' hfresh h) hd
  -- TryCatch
  | .tryCatch b exc hndlr =>
    simp only [desugar] at hd
    simp only [freshInStmt, Bool.and_eq_true] at hfresh
    cases hd with
    | execTryCatchCaught _ _ _ _ es' _ h1 h2 =>
      exact .execTryCatchCaught _ _ _ _ es' _
        (desugar_correct_bwd b es _ hfresh.1 h1)
        (desugar_correct_bwd hndlr es' _ hfresh.2 h2)
    | execTryCatchMiss _ _ _ _ _ _ hne h1 =>
      exact .execTryCatchMiss _ _ _ _ _ _ hne (desugar_correct_bwd b es _ hfresh.1 h1)
    | execTryCatchNormal _ _ _ _ _ hnot h1 =>
      exact .execTryCatchNormal _ _ _ _ _ hnot (desugar_correct_bwd b es _ hfresh.1 h1)
  -- Critical
  | .critical mutex b =>
    simp only [desugar] at hd
    simp only [freshInStmt] at hfresh
    cases hd with
    | execCritical _ _ _ _ h1 =>
      exact .execCritical _ _ _ _ (desugar_correct_bwd b es _ hfresh h1)
  -- ThreadEntry
  | .threadEntry b =>
    simp only [desugar] at hd
    simp only [freshInStmt] at hfresh
    cases hd with
    | execThreadEntry _ _ _ h1 =>
      exact .execThreadEntry _ _ _ (desugar_correct_bwd b es _ hfresh h1)
termination_by sizeOf s

theorem desugar_correct (es : ExecState) (s : Stmt) (out : Outcome)
    (hfresh : freshInStmt forIdx s = true) :
    Exec es s out ↔ Exec es (desugar s) out :=
  ⟨desugar_correct_fwd es s out hfresh, desugar_correct_bwd s es out hfresh⟩

-- =====================================================================
-- Phase 1a — Category B desugaring correctness lemmas
-- =====================================================================

theorem walrusAssign_eq (x : Ident) (e : Expr) :
    walrusAssign x e = .assign x e := rfl

theorem exec_walrusAssign (es : ExecState) (x : Ident) (e : Expr) (out : Outcome) :
    Exec es (walrusAssign x e) out ↔ Exec es (.assign x e) out := Iff.rfl

theorem tupleUnpack2_eq (arr x y : Ident) :
    tupleUnpack2 arr x y =
    .seq (.assign x (.subscript arr (.int 0)))
         (.assign y (.subscript arr (.int 1))) := rfl

theorem exec_tupleUnpack2_normal (es : ExecState) (arr x y : Ident) :
    let st1 := update es.regState x (evalExpr es.regState (.subscript arr (.int 0)))
    let es1 := setReg es st1
    Exec es (tupleUnpack2 arr x y)
      (.normal (setReg es1 (update es1.regState y
        (evalExpr es1.regState (.subscript arr (.int 1)))))) :=
  .execSeq es _ _ _ _ (.execAssign ..) (.execAssign ..)

theorem desugarMatch_nil (scrutinee : Expr) (default : Stmt) :
    desugarMatch scrutinee [] default = default := rfl

theorem exec_desugarMatch_hit (es : ExecState) (scrutinee : Expr) (n : Int)
    (body default : Stmt) (out : Outcome)
    (hval : evalExpr es.regState scrutinee = .int n)
    (hbody : Exec es body out) :
    Exec es (desugarMatch scrutinee [(n, body)] default) out := by
  simp [desugarMatch]
  apply Exec.execIfFalse
  · simp [evalBool, evalExpr, hval, evalBinopZ]
  · exact hbody

theorem exec_desugarMatch_miss (es : ExecState) (scrutinee : Expr) (n m : Int)
    (body default : Stmt) (out : Outcome)
    (hval : evalExpr es.regState scrutinee = .int n) (hne : n ≠ m)
    (hdef : Exec es default out) :
    Exec es (desugarMatch scrutinee [(m, body)] default) out := by
  simp only [desugarMatch]
  apply Exec.execIfTrue
  · simp only [evalBool, evalExpr, hval, evalBinopZ]
    have hd : n - m ≠ 0 := by omega
    split
    · rename_i h; injection h; omega
    · rfl
  · exact hdef
