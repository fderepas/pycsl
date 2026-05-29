/-
  WhileInv.lean — While loop invariant preservation lemma
  Mirror of Phase5a_WhileInv.v (all phases)

  while_not_continued: while loops never produce OContinued or OBroke
    (SBreak inside SWhile produces ONormal, not OBroke)
  while_inv_preserved: structural induction on Exec derivation
-/
import PyCSL.AST
import PyCSL.State
import PyCSL.SOS
import PyCSL.WP

-- Auxiliary: generalizes the statement index so induction works.
private theorem while_nc_aux
    {es : ExecState} {sw : Stmt} {out : Outcome}
    (h : Exec es sw out)
    {inv var : ContractExpr} {cond : Expr} {body : Stmt}
    (heq : sw = .while_ inv var cond body) :
    (∀ es', out ≠ .continued es') ∧ (∀ es', out ≠ .broke es') := by
  induction h generalizing inv var cond body with
  | execWhileTrue _ _ _ _ _ _ _ _ _ _ _ ih2 => exact ih2 heq
  | execWhileContinue _ _ _ _ _ _ _ _ _ _ _ ih2 => exact ih2 heq
  | execWhileBreak _ _ _ _ _ _ _ _ _ =>
    exact ⟨fun _ h => by simp at h, fun _ h => by simp at h⟩
  | execWhileFalse _ _ _ _ _ _ =>
    exact ⟨fun _ h => by simp at h, fun _ h => by simp at h⟩
  | execSkip _ => exact absurd heq (by simp)
  | execAssign _ _ _ => exact absurd heq (by simp)
  | execAugAssign _ _ _ _ => exact absurd heq (by simp)
  | execArraySet _ _ _ _ => exact absurd heq (by simp)
  | execSeq _ _ _ _ _ _ _ _ _ => exact absurd heq (by simp)
  | execSeqReturn _ _ _ _ _ _ _ => exact absurd heq (by simp)
  | execSeqContinue _ _ _ _ _ _ => exact absurd heq (by simp)
  | execSeqBreak _ _ _ _ _ _ => exact absurd heq (by simp)
  | execSeqThrow _ _ _ _ _ _ _ => exact absurd heq (by simp)
  | execIfTrue _ _ _ _ _ _ _ _ => exact absurd heq (by simp)
  | execIfFalse _ _ _ _ _ _ _ _ => exact absurd heq (by simp)
  | execContinue _ => exact absurd heq (by simp)
  | execBreak _ => exact absurd heq (by simp)
  | execReturn _ _ => exact absurd heq (by simp)
  | execAssertPass _ _ _ _ => exact absurd heq (by simp)
  | execAssertFail _ _ _ _ => exact absurd heq (by simp)
  | execTupleUnpack _ _ _ => exact absurd heq (by simp)
  | execGhostDecl _ _ _ _ => exact absurd heq (by simp)
  | execGhostAssign _ _ _ _ _ => exact absurd heq (by simp)
  | execLabel _ _ => exact absurd heq (by simp)
  | execRaise _ _ => exact absurd heq (by simp)
  | execTryCatchCaught _ _ _ _ _ _ _ _ _ _ => exact absurd heq (by simp)
  | execTryCatchMiss _ _ _ _ _ _ _ _ _ => exact absurd heq (by simp)
  | execTryCatchNormal _ _ _ _ _ _ _ _ => exact absurd heq (by simp)
  | execFieldAssign _ _ _ _ => exact absurd heq (by simp)
  | execFieldAugAssign _ _ _ _ _ => exact absurd heq (by simp)
  | execCritical _ _ _ _ _ _ => exact absurd heq (by simp)
  | execThreadEntry _ _ _ _ _ => exact absurd heq (by simp)
  | execFor _ _ _ _ _ _ _ _ _ _ => exact absurd heq (by simp)

-- While loops exit via ONormal, OReturned, OThrew, or OFailed — never OContinued or OBroke.
theorem while_not_continued
    {es : ExecState} {inv var : ContractExpr} {cond : Expr} {body : Stmt}
    {out : Outcome}
    (h : Exec es (.while_ inv var cond body) out) :
    (∀ es', out ≠ .continued es') ∧ (∀ es', out ≠ .broke es') :=
  while_nc_aux h rfl

-- =====================================================================
-- while_inv_preserved — Structural induction on the Exec derivation.
--
-- Strategy: wrap the result type in an opaque def to prevent Lean from
-- elaborating `match out with ...` as a dependent match on the Exec proof.
-- A private key lemma takes `{sw}` + `heq` so induction on `hExec` works
-- with `sw` as a free variable; `inv/var/cond/body` are NOT generalized
-- so `hPres`/`hPost` remain applicable throughout the IH chain.
-- =====================================================================

private def outcomeResult (Qn Qr : ExecState → Prop)
    (Qe : Ident → ExecState → Prop) : Outcome → Prop
  | .normal es'     => Qn es'
  | .returned es' _ => Qr es'
  | _               => True

private theorem while_inv_key
    (cond : Expr) (body : Stmt) (inv var : ContractExpr)
    (Qn Qr : ExecState → Prop)
    (Qe : Ident → ExecState → Prop)
    (preEs : ExecState)
    (hBodySound : ∀ es0 out0 Qn0 Qr0 Qc0 Qb0 Qe0,
       Exec es0 body out0 →
       wp body Qn0 Qr0 Qc0 Qb0 Qe0 preEs es0 →
       match out0 with
       | .normal es'      => Qn0 es'
       | .returned es' _  => Qr0 es'
       | .continued es'   => Qc0 es'
       | .broke es'       => Qb0 es'
       | .threw es' exc   => Qe0 exc es'
       | .failed _ _ _    => True)
    (hPres : ∀ es', evalC es' preEs none inv →
                    evalBool es'.regState cond = true →
                    let bodyDone es'' :=
                      evalC es'' preEs none inv ∧
                      evalV es'' preEs var < evalV es' preEs var ∧
                      evalV es'' preEs var ≥ 0
                    wp body bodyDone Qr bodyDone Qn Qe preEs es')
    (hPost : ∀ es', evalC es' preEs none inv →
                    evalBool es'.regState cond = false → Qn es')
    {sw : Stmt} {esI : ExecState} {out0 : Outcome}
    (hExec : Exec esI sw out0)
    (heq : sw = .while_ inv var cond body)
    (hInv0 : evalC esI preEs none inv)
    (hNonNeg0 : evalV esI preEs var ≥ 0) :
    outcomeResult Qn Qr Qe out0 := by
  -- Revert the index-dependent hypotheses so induction doesn't auto-abstract inv/var/cond/body.
  -- After induction, intro them back; inv/var/cond/body remain as fixed outer params.
  revert heq hInv0 hNonNeg0
  induction hExec with
  | execWhileTrue esI invW varW condW bodyW esB outW hcond hbody hrec _ ih_rec =>
    intro heq hInv0 hNonNeg0
    -- Save heq before simp so we can pass it unchanged to ih_rec.
    -- obtain ⟨rfl⟩ would eliminate the outer inv/var/cond/body params (they appear newer
    -- in the motive than the constructor vars). Use rw on specific hyps instead.
    have heq_orig := heq
    simp only [Stmt.while_.injEq] at heq
    obtain ⟨_, _, h3, h4⟩ := heq
    rw [h3] at hcond
    rw [h4] at hbody
    have hbdone : evalC esB preEs none inv ∧ evalV esB preEs var < evalV esI preEs var ∧
                  evalV esB preEs var ≥ 0 :=
      hBodySound esI (.normal esB)
        (fun es'' => evalC es'' preEs none inv ∧ evalV es'' preEs var < evalV esI preEs var ∧ evalV es'' preEs var ≥ 0)
        Qr
        (fun es'' => evalC es'' preEs none inv ∧ evalV es'' preEs var < evalV esI preEs var ∧ evalV es'' preEs var ≥ 0)
        Qn Qe hbody (hPres esI hInv0 hcond)
    exact ih_rec heq_orig hbdone.1 hbdone.2.2
  | execWhileContinue esI invW varW condW bodyW esC outW hcond hbody hrec _ ih_rec =>
    intro heq hInv0 hNonNeg0
    have heq_orig := heq
    simp only [Stmt.while_.injEq] at heq
    obtain ⟨_, _, h3, h4⟩ := heq
    rw [h3] at hcond
    rw [h4] at hbody
    have hbdone : evalC esC preEs none inv ∧ evalV esC preEs var < evalV esI preEs var ∧
                  evalV esC preEs var ≥ 0 :=
      hBodySound esI (.continued esC)
        (fun es'' => evalC es'' preEs none inv ∧ evalV es'' preEs var < evalV esI preEs var ∧ evalV es'' preEs var ≥ 0)
        Qr
        (fun es'' => evalC es'' preEs none inv ∧ evalV es'' preEs var < evalV esI preEs var ∧ evalV es'' preEs var ≥ 0)
        Qn Qe hbody (hPres esI hInv0 hcond)
    exact ih_rec heq_orig hbdone.1 hbdone.2.2
  | execWhileBreak esI invW varW condW bodyW esK hcond hbody _ =>
    intro heq hInv0 hNonNeg0
    simp only [Stmt.while_.injEq] at heq
    obtain ⟨_, _, h3, h4⟩ := heq
    rw [h3] at hcond
    rw [h4] at hbody
    exact hBodySound esI (.broke esK)
      (fun es'' => evalC es'' preEs none inv ∧ evalV es'' preEs var < evalV esI preEs var ∧ evalV es'' preEs var ≥ 0)
      Qr
      (fun es'' => evalC es'' preEs none inv ∧ evalV es'' preEs var < evalV esI preEs var ∧ evalV es'' preEs var ≥ 0)
      Qn Qe hbody (hPres esI hInv0 hcond)
  | execWhileFalse esI invW varW condW bodyW hcond =>
    intro heq hInv0 _
    simp only [Stmt.while_.injEq] at heq
    obtain ⟨_, _, h3, _⟩ := heq
    rw [h3] at hcond
    exact hPost esI hInv0 hcond
  -- All non-while constructors: heq is absurd (intro just to get it in context)
  | execSkip _ => intro heq; simp at heq
  | execAssign _ _ _ => intro heq; simp at heq
  | execAugAssign _ _ _ _ => intro heq; simp at heq
  | execArraySet _ _ _ _ => intro heq; simp at heq
  | execSeq _ _ _ _ _ _ _ _ _ => intro heq; simp at heq
  | execSeqReturn _ _ _ _ _ _ _ => intro heq; simp at heq
  | execSeqContinue _ _ _ _ _ _ => intro heq; simp at heq
  | execSeqBreak _ _ _ _ _ _ => intro heq; simp at heq
  | execSeqThrow _ _ _ _ _ _ _ => intro heq; simp at heq
  | execIfTrue _ _ _ _ _ _ _ _ => intro heq; simp at heq
  | execIfFalse _ _ _ _ _ _ _ _ => intro heq; simp at heq
  | execContinue _ => intro heq; simp at heq
  | execBreak _ => intro heq; simp at heq
  | execReturn _ _ => intro heq; simp at heq
  | execAssertPass _ _ _ _ => intro heq; simp at heq
  | execAssertFail _ _ _ _ => intro heq; simp at heq
  | execTupleUnpack _ _ _ => intro heq; simp at heq
  | execGhostDecl _ _ _ _ => intro heq; simp at heq
  | execGhostAssign _ _ _ _ _ => intro heq; simp at heq
  | execLabel _ _ => intro heq; simp at heq
  | execRaise _ _ => intro heq; simp at heq
  | execTryCatchCaught _ _ _ _ _ _ _ _ _ _ => intro heq; simp at heq
  | execTryCatchMiss _ _ _ _ _ _ _ _ _ => intro heq; simp at heq
  | execTryCatchNormal _ _ _ _ _ _ _ _ => intro heq; simp at heq
  | execFieldAssign _ _ _ _ => intro heq; simp at heq
  | execFieldAugAssign _ _ _ _ _ => intro heq; simp at heq
  | execCritical _ _ _ _ _ _ => intro heq; simp at heq
  | execThreadEntry _ _ _ _ _ => intro heq; simp at heq
  | execFor _ _ _ _ _ _ _ _ _ _ => intro heq; simp at heq

theorem while_inv_preserved
    (cond : Expr) (body : Stmt) (inv var : ContractExpr)
    (Qn Qr : ExecState → Prop)
    (Qe : Ident → ExecState → Prop)
    (preEs es : ExecState)
    (hBodySound : ∀ es0 out0 Qn0 Qr0 Qc0 Qb0 Qe0,
       Exec es0 body out0 →
       wp body Qn0 Qr0 Qc0 Qb0 Qe0 preEs es0 →
       match out0 with
       | .normal es'      => Qn0 es'
       | .returned es' _  => Qr0 es'
       | .continued es'   => Qc0 es'
       | .broke es'       => Qb0 es'
       | .threw es' exc   => Qe0 exc es'
       | .failed _ _ _    => True)
    (hInv : evalC es preEs none inv)
    (hNonNeg : evalV es preEs var ≥ 0)
    (hPres : ∀ es', evalC es' preEs none inv →
                    evalBool es'.regState cond = true →
                    let bodyDone es'' :=
                      evalC es'' preEs none inv ∧
                      evalV es'' preEs var < evalV es' preEs var ∧
                      evalV es'' preEs var ≥ 0
                    wp body bodyDone Qr bodyDone Qn Qe preEs es')
    (hPost : ∀ es', evalC es' preEs none inv →
                    evalBool es'.regState cond = false → Qn es')
    (out : Outcome)
    (hExec : Exec es (.while_ inv var cond body) out) :
    match out with
    | .normal es'     => Qn es'
    | .returned es' _ => Qr es'
    | .continued _    => True
    | .broke _        => True
    | .threw _ _      => True
    | .failed _ _ _   => True := by
  -- Apply the key lemma; cases out eliminates the dependent match on hExec.
  have hk := while_inv_key cond body inv var Qn Qr Qe preEs hBodySound hPres hPost hExec rfl hInv hNonNeg
  cases out with
  | normal es'     => exact hk
  | returned es' v => exact hk
  | continued _    => exact True.intro
  | broke _        => exact True.intro
  | threw _ _      => exact True.intro
  | failed _ _ _   => exact True.intro
