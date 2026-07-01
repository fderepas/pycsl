/-
  SOS.lean — Structural Operational Semantics
  Mirror of Phase3_SOS.v (all phases)

  Exec is an inductive Prop over ExecState.
  Outcome carries exec_state in all branches.
  Five outcome kinds: Normal, Returned, Continued, Broke, Failed, Threw.
-/
import PyCSL.AST
import PyCSL.State
import PyCSL.DesugarDef

inductive Outcome where
  | normal    (es : ExecState)
  | returned  (es : ExecState) (v : Val)
  | continued (es : ExecState)
  | broke     (es : ExecState)
  | failed    (es : ExecState) (msg : String) (cond : ContractExpr)
  | threw     (es : ExecState) (exc : Ident)
  deriving Repr

inductive Exec : ExecState → Stmt → Outcome → Prop where

  | execSkip (es : ExecState) :
    Exec es .skip (.normal es)

  | execAssign (es : ExecState) (x : Ident) (e : Expr) :
    Exec es (.assign x e)
      (.normal (setReg es (update es.regState x (evalExpr es.regState e))))

  | execAugAssign (es : ExecState) (x : Ident) (op : Binop) (e : Expr) :
    Exec es (.augAssign x op e)
      (.normal (setReg es (update es.regState x (.int
        (evalBinopZ op
          (match lookup es.regState x with | some (.int n) => n | _ => 0)
          (match evalExpr es.regState e with | .int n => n | _ => 0))))))

  | execArraySet (es : ExecState) (arr : Ident) (i v : Expr) :
    Exec es (.arraySet arr i v)
      (.normal (setReg es (arrayUpdate es.regState arr
        (match evalExpr es.regState i with | .int n => n | _ => 0)
        (match evalExpr es.regState v with | .int n => n | _ => 0))))

  | execSeq (es : ExecState) (s1 s2 : Stmt) (es' : ExecState) (out : Outcome) :
    Exec es s1 (.normal es') →
    Exec es' s2 out →
    Exec es (.seq s1 s2) out

  | execSeqReturn (es : ExecState) (s1 s2 : Stmt) (es' : ExecState) (v : Val) :
    Exec es s1 (.returned es' v) →
    Exec es (.seq s1 s2) (.returned es' v)

  | execSeqContinue (es : ExecState) (s1 s2 : Stmt) (es' : ExecState) :
    Exec es s1 (.continued es') →
    Exec es (.seq s1 s2) (.continued es')

  | execSeqBreak (es : ExecState) (s1 s2 : Stmt) (es' : ExecState) :
    Exec es s1 (.broke es') →
    Exec es (.seq s1 s2) (.broke es')

  | execSeqThrow (es : ExecState) (s1 s2 : Stmt) (es' : ExecState) (exc : Ident) :
    Exec es s1 (.threw es' exc) →
    Exec es (.seq s1 s2) (.threw es' exc)

  | execIfTrue (es : ExecState) (cond : Expr) (s1 s2 : Stmt) (out : Outcome) :
    evalBool es.regState cond = true →
    Exec es s1 out →
    Exec es (.ite cond s1 s2) out

  | execIfFalse (es : ExecState) (cond : Expr) (s1 s2 : Stmt) (out : Outcome) :
    evalBool es.regState cond = false →
    Exec es s2 out →
    Exec es (.ite cond s1 s2) out

  | execWhileTrue (es : ExecState) (inv var : ContractExpr) (cond : Expr)
      (body : Stmt) (es' : ExecState) (out : Outcome) :
    evalBool es.regState cond = true →
    Exec es body (.normal es') →
    Exec es' (.while_ inv var cond body) out →
    Exec es (.while_ inv var cond body) out

  | execWhileContinue (es : ExecState) (inv var : ContractExpr) (cond : Expr)
      (body : Stmt) (es' : ExecState) (out : Outcome) :
    evalBool es.regState cond = true →
    Exec es body (.continued es') →
    Exec es' (.while_ inv var cond body) out →
    Exec es (.while_ inv var cond body) out

  | execWhileBreak (es : ExecState) (inv var : ContractExpr) (cond : Expr)
      (body : Stmt) (es' : ExecState) :
    evalBool es.regState cond = true →
    Exec es body (.broke es') →
    Exec es (.while_ inv var cond body) (.normal es')

  | execWhileFalse (es : ExecState) (inv var : ContractExpr) (cond : Expr)
      (body : Stmt) :
    evalBool es.regState cond = false →
    Exec es (.while_ inv var cond body) (.normal es)

  | execContinue (es : ExecState) :
    Exec es .continue_ (.continued es)

  | execBreak (es : ExecState) :
    Exec es .break_ (.broke es)

  | execReturn (es : ExecState) (e : Expr) :
    Exec es (.ret e)
      (.returned
        (setReg es (update es.regState "\\result" (evalExpr es.regState e)))
        (evalExpr es.regState e))

  | execAssertPass (es : ExecState) (cond : ContractExpr) (msg : String) :
    evalContract es.regState es.regState none cond →
    Exec es (.assert_ cond msg) (.normal es)

  | execAssertFail (es : ExecState) (cond : ContractExpr) (msg : String) :
    ¬ evalContract es.regState es.regState none cond →
    Exec es (.assert_ cond msg) (.failed es msg cond)

  | execTupleUnpack (es : ExecState) (xs : List Ident) (e : Expr) :
    Exec es (.tupleUnpack xs e) (.normal es)

  | execGhostDecl (es : ExecState) (x : Ident) (t : GhostType) (e : GhostExpr) :
    Exec es (.ghostDecl x t e)
      (.normal (setGhost es (ghostUpdate es.ghostSt x (evalGhostVal t es e))))

  | execGhostAssign (es : ExecState) (x : Ident) (t : GhostType) (op : AugOp) (e : GhostExpr) :
    Exec es (.ghostAssign x t op e)
      (.normal (setGhost es (ghostUpdate es.ghostSt x
        (applyGhostAug op (ghostLookup es.ghostSt x) es e))))

  | execLabel (es : ExecState) (L : Ident) :
    Exec es (.label_ L)
      (.normal (setLabels es ((L, es.ghostSt) :: es.labelSnaps)))

  | execRaise (es : ExecState) (exc : Ident) :
    Exec es (.raise_ exc) (.threw es exc)

  | execTryCatchCaught (es : ExecState) (body : Stmt) (exc : Ident) (handler : Stmt)
      (es' : ExecState) (out : Outcome) :
    Exec es body (.threw es' exc) →
    Exec es' handler out →
    Exec es (.tryCatch body exc handler) out

  | execTryCatchMiss (es : ExecState) (body : Stmt) (exc exc' : Ident) (handler : Stmt)
      (es' : ExecState) :
    exc' ≠ exc →
    Exec es body (.threw es' exc') →
    Exec es (.tryCatch body exc handler) (.threw es' exc')

  | execTryCatchNormal (es : ExecState) (body : Stmt) (exc : Ident) (handler : Stmt)
      (out : Outcome) :
    (∀ es' e, out ≠ .threw es' e) →
    Exec es body out →
    Exec es (.tryCatch body exc handler) out

  -- Phase 6: flat-key field-state model — `self.f` is the synthetic
  -- register variable `selfId ++ "." ++ f` (the same name evalExpr's
  -- .fieldGet reads and Module 6 emits), so a write updates exactly the
  -- key a later read observes. Mirrors execAssign / execAugAssign.
  | execFieldAssign (es : ExecState) (selfId f : Ident) (e : Expr) :
    Exec es (.fieldAssign selfId f e)
      (.normal (setReg es (update es.regState (selfId ++ "." ++ f) (evalExpr es.regState e))))

  | execFieldAugAssign (es : ExecState) (selfId f : Ident) (op : Binop) (e : Expr) :
    Exec es (.fieldAugAssign selfId f op e)
      (.normal (setReg es (update es.regState (selfId ++ "." ++ f) (.int
        (evalBinopZ op
          (match lookup es.regState (selfId ++ "." ++ f) with | some (.int n) => n | _ => 0)
          (match evalExpr es.regState e with | .int n => n | _ => 0))))))

  | execCritical (es : ExecState) (mutex : Ident) (body : Stmt) (out : Outcome) :
    Exec es body out →
    Exec es (.critical mutex body) out

  | execThreadEntry (es : ExecState) (body : Stmt) (out : Outcome) :
    Exec es body out →
    Exec es (.threadEntry body) out

  | execFor (es : ExecState) (x arr : Ident) (inv var : ContractExpr)
      (body : Stmt) (aim : Bool) (out : Outcome) :
    Exec es (desugar (.for_ x arr inv var body aim)) out →
    Exec es (.for_ x arr inv var body aim) out

  /-- Phase 7: acquires/releases — Hoare-instance identity stubs.
      No lock state in ExecState; real lock discipline is the deferred
      ConcurrentMM instance (see MemModel.lean §"Deferred work"). -/
  | execAcquires (es : ExecState) (m : Ident) :
    Exec es (.acquires m) (.normal es)

  | execReleases (es : ExecState) (m : Ident) :
    Exec es (.releases m) (.normal es)

  /-- Phase 8 — Lambda (Category A, optional).
      `.call r fn arg`: evaluate `fn` to a `.closure param body cstate`,
      evaluate `arg` to `argval`, execute `body` in `cstate[param -> argval]`,
      and on `.returned st' v` bind `r -> v` in the ORIGINAL state.
      Other body outcomes (normal/break/continue/throw/fail) are stuck. -/
  | execCall (es : ExecState) (r : Ident) (fn arg : Expr)
      (param : Ident) (body : Stmt) (cstate : State)
      (st' : ExecState) (v : Val)
    (hfn : evalExpr es.regState fn = .closure param body cstate)
    (hb : Exec (setReg (mkExecState cstate)
                        (update cstate param (evalExpr es.regState arg)))
                body (.returned st' v)) :
    Exec es (.call r fn arg)
      (.normal (setReg es (update es.regState r v)))

  /-- Phase 8 — Lambda construction. Binds the closure value capturing the
      current regState. Leaf; mirrors execAssign. -/
  | execLambda (es : ExecState) (x param : Ident) (body : Stmt) :
    Exec es (.lambda x param body)
      (.normal (setReg es (update es.regState x (.closure param body es.regState))))

theorem exec_deterministic {es : ExecState} {s : Stmt} {out1 out2 : Outcome}
    (h1 : Exec es s out1) (h2 : Exec es s out2) : out1 = out2 := by
  induction h1 generalizing out2 with
  | execSkip _ => cases h2; rfl
  | execAssign _ _ _ => cases h2; rfl
  | execAugAssign _ _ _ _ => cases h2; rfl
  | execArraySet _ _ _ _ => cases h2; rfl
  | execContinue _ => cases h2; rfl
  | execBreak _ => cases h2; rfl
  | execReturn _ _ => cases h2; rfl
  | execTupleUnpack _ _ _ => cases h2; rfl
  | execGhostDecl _ _ _ _ => cases h2; rfl
  | execGhostAssign _ _ _ _ _ => cases h2; rfl
  | execLabel _ _ => cases h2; rfl
  | execRaise _ _ => cases h2; rfl
  | execFieldAssign _ _ _ _ => cases h2; rfl
  | execFieldAugAssign _ _ _ _ _ => cases h2; rfl
  | execLambda _ _ _ _ => cases h2; rfl
  | execAssertPass _ _ _ hcond =>
    cases h2 with
    | execAssertPass => rfl
    | execAssertFail _ _ _ hneg => exact absurd hcond hneg
  | execAssertFail _ _ _ hneg =>
    cases h2 with
    | execAssertPass _ _ _ hcond => exact absurd hcond hneg
    | execAssertFail => rfl
  | execSeq _ _ _ _ _ _ _ ih1 ih2 =>
    cases h2 with
    | execSeq _ _ _ _ _ hs1' hs2' =>
      have heq := ih1 hs1'; injection heq with hes; subst hes; exact ih2 hs2'
    | execSeqReturn _ _ _ _ _ hs1' => exact absurd (ih1 hs1') (by simp)
    | execSeqContinue _ _ _ _ hs1' => exact absurd (ih1 hs1') (by simp)
    | execSeqBreak _ _ _ _ hs1' => exact absurd (ih1 hs1') (by simp)
    | execSeqThrow _ _ _ _ _ hs1' => exact absurd (ih1 hs1') (by simp)
  | execSeqReturn _ _ _ _ _ _ ih =>
    cases h2 with
    | execSeq _ _ _ _ _ hs1' _ => exact absurd (ih hs1') (by simp)
    | execSeqReturn _ _ _ _ _ hs1' =>
      have heq := ih hs1'; injection heq with hes hv; subst hes; subst hv; rfl
    | execSeqContinue _ _ _ _ hs1' => exact absurd (ih hs1') (by simp)
    | execSeqBreak _ _ _ _ hs1' => exact absurd (ih hs1') (by simp)
    | execSeqThrow _ _ _ _ _ hs1' => exact absurd (ih hs1') (by simp)
  | execSeqContinue _ _ _ _ _ ih =>
    cases h2 with
    | execSeq _ _ _ _ _ hs1' _ => exact absurd (ih hs1') (by simp)
    | execSeqReturn _ _ _ _ _ hs1' => exact absurd (ih hs1') (by simp)
    | execSeqContinue _ _ _ _ hs1' =>
      have heq := ih hs1'; injection heq with hes; subst hes; rfl
    | execSeqBreak _ _ _ _ hs1' => exact absurd (ih hs1') (by simp)
    | execSeqThrow _ _ _ _ _ hs1' => exact absurd (ih hs1') (by simp)
  | execSeqBreak _ _ _ _ _ ih =>
    cases h2 with
    | execSeq _ _ _ _ _ hs1' _ => exact absurd (ih hs1') (by simp)
    | execSeqReturn _ _ _ _ _ hs1' => exact absurd (ih hs1') (by simp)
    | execSeqContinue _ _ _ _ hs1' => exact absurd (ih hs1') (by simp)
    | execSeqBreak _ _ _ _ hs1' =>
      have heq := ih hs1'; injection heq with hes; subst hes; rfl
    | execSeqThrow _ _ _ _ _ hs1' => exact absurd (ih hs1') (by simp)
  | execSeqThrow _ _ _ _ _ _ ih =>
    cases h2 with
    | execSeq _ _ _ _ _ hs1' _ => exact absurd (ih hs1') (by simp)
    | execSeqReturn _ _ _ _ _ hs1' => exact absurd (ih hs1') (by simp)
    | execSeqContinue _ _ _ _ hs1' => exact absurd (ih hs1') (by simp)
    | execSeqBreak _ _ _ _ hs1' => exact absurd (ih hs1') (by simp)
    | execSeqThrow _ _ _ _ _ hs1' =>
      have heq := ih hs1'; injection heq with hes hexc; subst hes; subst hexc; rfl
  | execIfTrue _ _ _ _ _ hcond _ ih =>
    cases h2 with
    | execIfTrue _ _ _ _ _ _ h' => exact ih h'
    | execIfFalse _ _ _ _ _ hc' _ => simp [hcond] at hc'
  | execIfFalse _ _ _ _ _ hcond _ ih =>
    cases h2 with
    | execIfTrue _ _ _ _ _ hc' _ => simp [hcond] at hc'
    | execIfFalse _ _ _ _ _ _ h' => exact ih h'
  | execWhileTrue _ _ _ _ _ _ _ hcond _ _ ih1 ih2 =>
    cases h2 with
    | execWhileTrue _ _ _ _ _ _ _ _ hb' hr' =>
      have heq := ih1 hb'; injection heq with hes; subst hes; exact ih2 hr'
    | execWhileContinue _ _ _ _ _ _ _ _ hb' _ => exact absurd (ih1 hb') (by simp)
    | execWhileBreak _ _ _ _ _ _ _ hb' => exact absurd (ih1 hb') (by simp)
    | execWhileFalse _ _ _ _ _ hc' => simp [hcond] at hc'
  | execWhileContinue _ _ _ _ _ _ _ hcond _ _ ih1 ih2 =>
    cases h2 with
    | execWhileTrue _ _ _ _ _ _ _ _ hb' _ => exact absurd (ih1 hb') (by simp)
    | execWhileContinue _ _ _ _ _ _ _ _ hb' hr' =>
      have heq := ih1 hb'; injection heq with hes; subst hes; exact ih2 hr'
    | execWhileBreak _ _ _ _ _ _ _ hb' => exact absurd (ih1 hb') (by simp)
    | execWhileFalse _ _ _ _ _ hc' => simp [hcond] at hc'
  | execWhileBreak _ _ _ _ _ _ hcond _ ih =>
    cases h2 with
    | execWhileTrue _ _ _ _ _ _ _ _ hb' _ => exact absurd (ih hb') (by simp)
    | execWhileContinue _ _ _ _ _ _ _ _ hb' _ => exact absurd (ih hb') (by simp)
    | execWhileBreak _ _ _ _ _ _ _ hb' =>
      have heq := ih hb'; injection heq with hes; subst hes; rfl
    | execWhileFalse _ _ _ _ _ hc' => simp [hcond] at hc'
  | execWhileFalse _ _ _ _ _ hcond =>
    cases h2 with
    | execWhileTrue _ _ _ _ _ _ _ hc' _ _ => simp [hcond] at hc'
    | execWhileContinue _ _ _ _ _ _ _ hc' _ _ => simp [hcond] at hc'
    | execWhileBreak _ _ _ _ _ _ hc' _ => simp [hcond] at hc'
    | execWhileFalse _ _ _ _ _ _ => rfl
  | execTryCatchCaught _ _ exc _ es' _ ht _ ih1 ih2 =>
    cases h2 with
    | execTryCatchCaught _ _ _ _ _ _ ht' hh' =>
      have heq := ih1 ht'; injection heq with hes _; subst hes; exact ih2 hh'
    | execTryCatchMiss _ _ _ exc' _ _ hne ht' =>
      have heq := ih1 ht'; injection heq with _ hexc; exact absurd hexc.symm hne
    | execTryCatchNormal _ _ _ _ _ hnot hb' =>
      exact absurd (ih1 hb').symm (hnot es' exc)
  | execTryCatchMiss _ _ _ exc' _ es' hne _ ih =>
    cases h2 with
    | execTryCatchCaught _ _ _ _ _ _ ht' _ =>
      have heq := ih ht'; injection heq with _ hexc; exact absurd hexc hne
    | execTryCatchMiss _ _ _ _ _ _ _ ht' =>
      have heq := ih ht'; injection heq with hes hexc; subst hes; subst hexc; rfl
    | execTryCatchNormal _ _ _ _ _ hnot hb' =>
      exact absurd (ih hb').symm (hnot es' exc')
  | execTryCatchNormal _ _ _ _ _ hnot _ ih =>
    cases h2 with
    | execTryCatchCaught _ _ _ _ es'' _ ht' _ =>
      exact absurd (ih ht') (hnot es'' _)
    | execTryCatchMiss _ _ _ exc' _ es'' _ ht' =>
      exact absurd (ih ht') (hnot es'' exc')
    | execTryCatchNormal _ _ _ _ _ _ hb' => exact ih hb'
  | execCritical _ _ _ _ hb ih =>
    cases h2 with | execCritical _ _ _ _ hb' => exact ih hb'
  | execThreadEntry _ _ _ hb ih =>
    cases h2 with | execThreadEntry _ _ _ hb' => exact ih hb'
  | execFor _ _ _ _ _ _ _ _ hd ih =>
    cases h2 with | execFor _ _ _ _ _ _ _ _ hd' => exact ih hd'
  | execAcquires _ _ => cases h2; rfl
  | execReleases _ _ => cases h2; rfl
  | @execCall es r fn arg param body cstate st' v hfn hb ih =>
    cases h2 with
    | execCall _ _ _ _ param' body' cstate' st'' v' hfn' hb' =>
      -- From hfn and hfn': VClosure params must match
      have : evalExpr es.regState fn = .closure param' body' cstate' := hfn'
      rw [hfn] at this
      injection this with hp hb_eq hc
      subst param'; subst body'; subst cstate'
      -- Body exec determinism: st' = st'', v = v'
      have heq := ih hb'; injection heq with hst hv; subst st''; subst v'
      rfl

/--
  Phase 8 keystone: `\result` is bound to the returned value.
  PROVED — 0 sorry. Uses a helper `outcomeHasResult` to avoid
  Lean's dependent-match issue with `induction` on `Exec`. -/
def outcomeHasResult (out : Outcome) : Prop :=
  match out with
  | .returned st' v => lookup st'.regState "\\result" = some v
  | _ => True

theorem returnedStateHasResult {es : ExecState} {s : Stmt} {out : Outcome}
    (h : Exec es s out) : outcomeHasResult out := by
  induction h with
  | execReturn _ _ => simp [outcomeHasResult, lookup, update, setReg]
  | execSeq _ _ _ _ _ _ _ _ ih2 => exact ih2
  | execSeqReturn _ _ _ _ _ _ ih => exact ih
  | execIfTrue _ _ _ _ _ _ _ ih => exact ih
  | execIfFalse _ _ _ _ _ _ _ ih => exact ih
  | execWhileTrue _ _ _ _ _ _ _ _ _ _ ih1 ih2 => exact ih2
  | execWhileContinue _ _ _ _ _ _ _ _ _ _ ih1 ih2 => exact ih2
  | execTryCatchCaught _ _ _ _ _ _ _ _ ih1 ih2 => exact ih2
  | execTryCatchNormal _ _ _ _ _ _ _ ih => exact ih
  | execCritical _ _ _ _ _ ih => exact ih
  | execThreadEntry _ _ _ _ ih => exact ih
  | execFor _ _ _ _ _ _ _ _ _ ih => exact ih
  | _ => trivial
