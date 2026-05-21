/-
  Desugar.lean — Desugaring correctness theorem
  Port of Phase3b_Desugar.v

  desugar_correct : freshInStmt forIdx s = true →
    Exec st s out ↔ Exec st (desugar s) out

  Strategy:
  - Forward: induction on the Exec derivation.
  - Backward: induction on the statement s.
  - SWhile backward: use while_body_swap (induction on Exec with a FREE body
    variable) to avoid the "non-variable index" tactic restriction.
-/
import PyCSL.AST
import PyCSL.State
import PyCSL.SOS
import PyCSL.DesugarDef

-- while_body_swap_aux: generalized with a free Stmt variable s (required by
-- the `induction` tactic) and an equation s = .while_ inv var cond body1.
-- The `induction hw` works because s IS a single free variable.
private theorem while_body_swap_aux {inv var : ContractExpr} {cond : Expr}
    {body1 body2 : Stmt}
    (ih : ∀ st out, Exec st body1 out → Exec st body2 out) :
    ∀ {st : State} {s : Stmt} {out : Outcome},
    s = .while_ inv var cond body1 →
    Exec st s out →
    Exec st (.while_ inv var cond body2) out := by
  intro st s out heq hw
  induction hw with
  | execWhileTrue _ _ _ _ _ _ _ hc hbody _ _ ih_rec =>
    simp only [Stmt.while_.injEq] at heq
    obtain ⟨rfl, rfl, rfl, rfl⟩ := heq
    exact .execWhileTrue _ _ _ _ _ _ _ hc (ih _ _ hbody) (ih_rec rfl)
  | execWhileContinue _ _ _ _ _ _ _ hc hbody _ _ ih_rec =>
    simp only [Stmt.while_.injEq] at heq
    obtain ⟨rfl, rfl, rfl, rfl⟩ := heq
    exact .execWhileContinue _ _ _ _ _ _ _ hc (ih _ _ hbody) (ih_rec rfl)
  | execWhileFalse _ _ _ _ _ hc =>
    simp only [Stmt.while_.injEq] at heq
    obtain ⟨rfl, rfl, rfl, rfl⟩ := heq
    exact .execWhileFalse _ _ _ _ _ hc
  -- Non-while cases: heq equates a non-while constructor with .while_, which is False.
  | execSkip _ => simp at heq
  | execAssign _ _ _ => simp at heq
  | execAugAssign _ _ _ _ => simp at heq
  | execArraySet _ _ _ _ => simp at heq
  | execSeq _ _ _ _ _ _ _ _ _ => simp at heq
  | execSeqReturn _ _ _ _ _ _ _ => simp at heq
  | execSeqContinue _ _ _ _ _ _ => simp at heq
  | execIfTrue _ _ _ _ _ _ _ _ => simp at heq
  | execIfFalse _ _ _ _ _ _ _ _ => simp at heq
  | execContinue _ => simp at heq
  | execReturn _ _ => simp at heq
  | execFor _ _ _ _ _ _ _ _ _ => simp at heq

-- while_body_swap: specialize while_body_swap_aux to hw : Exec st (.while_ ...) out.
private def while_body_swap {inv var : ContractExpr} {cond : Expr}
    {body1 body2 : Stmt}
    (ih : ∀ st out, Exec st body1 out → Exec st body2 out)
    {st : State} {out : Outcome}
    (hw : Exec st (.while_ inv var cond body1) out) :
    Exec st (.while_ inv var cond body2) out :=
  while_body_swap_aux ih rfl hw

-- while_bwd_desugar: convert while(desugar body) back to while(body).
private theorem while_bwd_desugar {body : Stmt} {inv var : ContractExpr} {cond : Expr}
    (ih : ∀ st out, freshInStmt forIdx body = true →
          Exec st (desugar body) out → Exec st body out)
    (hfresh : freshInStmt forIdx body = true) :
    ∀ st out, Exec st (.while_ inv var cond (desugar body)) out →
              Exec st (.while_ inv var cond body) out :=
  fun st out hw => while_body_swap (fun st out h => ih st out hfresh h) hw

-- Forward direction: exec st s out → exec st (desugar s) out.
theorem desugar_correct_fwd (st : State) (s : Stmt) (out : Outcome)
    (hfresh : freshInStmt forIdx s = true)
    (h : Exec st s out) : Exec st (desugar s) out := by
  induction h with
  | execSkip st => exact .execSkip st
  | execAssign st x e => exact .execAssign st x e
  | execAugAssign st x op e => exact .execAugAssign st x op e
  | execArraySet st arr i v => exact .execArraySet st arr i v
  | execSeq _ _ _ _ _ _ _ ih1 ih2 =>
    simp only [freshInStmt, Bool.and_eq_true] at hfresh
    simp only [desugar]
    exact .execSeq _ _ _ _ _ (ih1 hfresh.1) (ih2 hfresh.2)
  | execSeqReturn _ _ _ _ _ _ ih1 =>
    simp only [freshInStmt, Bool.and_eq_true] at hfresh
    simp only [desugar]
    exact .execSeqReturn _ _ _ _ _ (ih1 hfresh.1)
  | execSeqContinue _ _ _ _ _ ih1 =>
    simp only [freshInStmt, Bool.and_eq_true] at hfresh
    simp only [desugar]
    exact .execSeqContinue _ _ _ _ (ih1 hfresh.1)
  | execIfTrue _ _ _ _ _ hc _ ih1 =>
    simp only [freshInStmt, Bool.and_eq_true] at hfresh
    simp only [desugar]
    exact .execIfTrue _ _ _ _ _ hc (ih1 hfresh.1)
  | execIfFalse _ _ _ _ _ hc _ ih2 =>
    simp only [freshInStmt, Bool.and_eq_true] at hfresh
    simp only [desugar]
    exact .execIfFalse _ _ _ _ _ hc (ih2 hfresh.2)
  | execWhileTrue _ _ _ _ _ _ _ hc _ _ ih_body ih_rec =>
    simp only [freshInStmt] at hfresh
    simp only [desugar]
    exact .execWhileTrue _ _ _ _ _ _ _ hc (ih_body hfresh) (ih_rec hfresh)
  | execWhileContinue _ _ _ _ _ _ _ hc _ _ ih_body ih_rec =>
    simp only [freshInStmt] at hfresh
    simp only [desugar]
    exact .execWhileContinue _ _ _ _ _ _ _ hc (ih_body hfresh) (ih_rec hfresh)
  | execWhileFalse st inv var cond body hc =>
    simp only [desugar]
    exact .execWhileFalse st inv var cond _ hc
  | execContinue st => exact .execContinue st
  | execReturn st e => exact .execReturn st e
  | execFor _ _ _ _ _ _ _ hprem _ =>
    exact hprem

-- Backward direction: exec st (desugar s) out → exec st s out.
theorem desugar_correct_bwd (s : Stmt) (st : State) (out : Outcome)
    (hfresh : freshInStmt forIdx s = true)
    (hd : Exec st (desugar s) out) : Exec st s out := by
  induction s generalizing st out with
  | skip      => exact hd
  | assign    => exact hd
  | augAssign => exact hd
  | arraySet  => exact hd
  | seq s1 s2 ih1 ih2 =>
    -- ih1 : ∀ st out, fresh s1 → Exec st (desugar s1) out → Exec st s1 out
    simp only [freshInStmt, Bool.and_eq_true] at hfresh
    simp only [desugar] at hd
    cases hd with
    | execSeq _ _ _ st' _ h1 h2 =>
      exact .execSeq _ _ _ _ _ (ih1 _ _ hfresh.1 h1) (ih2 _ _ hfresh.2 h2)
    | execSeqReturn _ _ _ _ _ h1 =>
      exact .execSeqReturn _ _ _ _ _ (ih1 _ _ hfresh.1 h1)
    | execSeqContinue _ _ _ _ h1 =>
      exact .execSeqContinue _ _ _ _ (ih1 _ _ hfresh.1 h1)
  | ite c s1 s2 ih1 ih2 =>
    simp only [freshInStmt, Bool.and_eq_true] at hfresh
    simp only [desugar] at hd
    cases hd with
    | execIfTrue  _ _ _ _ _ hc hb => exact .execIfTrue  _ _ _ _ _ hc (ih1 _ _ hfresh.1 hb)
    | execIfFalse _ _ _ _ _ hc hb => exact .execIfFalse _ _ _ _ _ hc (ih2 _ _ hfresh.2 hb)
  | while_ inv var cond body ih =>
    -- ih : ∀ st out, fresh body → Exec st (desugar body) out → Exec st body out
    simp only [freshInStmt] at hfresh
    simp only [desugar] at hd
    exact while_bwd_desugar ih hfresh _ _ hd
  | for_ x arr inv var body _ =>
    exact .execFor _ _ _ _ _ _ _ hd
  | ret       => exact hd
  | continue_ => exact hd

theorem desugar_correct (st : State) (s : Stmt) (out : Outcome)
    (hfresh : freshInStmt forIdx s = true) :
    Exec st s out ↔ Exec st (desugar s) out :=
  ⟨desugar_correct_fwd st s out hfresh, desugar_correct_bwd s st out hfresh⟩

-- =====================================================================
-- Phase 1a — Category B desugaring correctness lemmas
-- =====================================================================

-- Feature 29 — walrusAssign is definitionally equal to assign
theorem walrusAssign_eq (x : Ident) (e : Expr) :
    walrusAssign x e = .assign x e := rfl

theorem exec_walrusAssign (st : State) (x : Ident) (e : Expr) (out : Outcome) :
    Exec st (walrusAssign x e) out ↔ Exec st (.assign x e) out := by
  rfl

-- Feature 28 — tupleUnpack2 is a sequence of two subscript assignments.
theorem tupleUnpack2_eq (arr x y : Ident) :
    tupleUnpack2 arr x y =
    .seq (.assign x (.subscript arr (.int 0)))
         (.assign y (.subscript arr (.int 1))) := rfl

theorem exec_tupleUnpack2_normal (st : State) (arr x y : Ident) :
    let st1 := update st x (evalExpr st (.subscript arr (.int 0)))
    Exec st (tupleUnpack2 arr x y)
      (.normal (update st1 y (evalExpr st1 (.subscript arr (.int 1))))) :=
  .execSeq _ _ _ _ _ (.execAssign ..) (.execAssign ..)

-- Feature 30 — Empty match reduces to default.
theorem desugarMatch_nil (scrutinee : Expr) (default : Stmt) :
    desugarMatch scrutinee [] default = default := rfl

-- Single-arm match executes body when scrutinee = n.
theorem exec_desugarMatch_hit (st : State) (scrutinee : Expr) (n : Int)
    (body default : Stmt) (out : Outcome)
    (hval : evalExpr st scrutinee = .int n) (hbody : Exec st body out) :
    Exec st (desugarMatch scrutinee [(n, body)] default) out := by
  simp [desugarMatch]
  apply Exec.execIfFalse
  · simp [evalBool, evalExpr, hval, evalBinopZ]
  · exact hbody

-- Single-arm match executes default when scrutinee ≠ n.
theorem exec_desugarMatch_miss (st : State) (scrutinee : Expr) (n m : Int)
    (body default : Stmt) (out : Outcome)
    (hval : evalExpr st scrutinee = .int n) (hne : n ≠ m)
    (hdef : Exec st default out) :
    Exec st (desugarMatch scrutinee [(m, body)] default) out := by
  simp only [desugarMatch]
  apply Exec.execIfTrue
  · simp only [evalBool, evalExpr, hval, evalBinopZ]
    have hd : n - m ≠ 0 := by omega
    split
    · rename_i h; injection h; omega
    · rfl
  · exact hdef
