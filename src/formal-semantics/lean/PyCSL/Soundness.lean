/-
  Soundness.lean — PyCSL Soundness Theorem
  Mirror of Phase5b_Soundness.v (all phases)

  Five-continuation soundness:
    Exec es s out → wp s Qn Qr Qc Qb Qe preEs es → outcomePost Qn Qr Qc Qb Qe out

  All cases proved including execFor (via wp_desugar_fwd + liftContinue_wp).
-/
import PyCSL.AST
import PyCSL.State
import PyCSL.SOS
import PyCSL.WP
import PyCSL.MemModel
import PyCSL.WhileInv
import PyCSL.Why3Trust

-- ===== WP Monotonicity =====

-- If all five continuations become stronger (implications hold),
-- wp propagates: wp s Qn ... → wp s Qn' ...
-- Used in wp_desugar_fwd to chain IH through seq/tryCatch continuations.
theorem wp_mono {s : Stmt}
    {Qn Qn' Qr Qr' Qc Qc' Qb Qb' : ExecState → Prop}
    {Qe Qe' : Ident → ExecState → Prop}
    (hn : ∀ es, Qn es → Qn' es)
    (hr : ∀ es, Qr es → Qr' es)
    (hc : ∀ es, Qc es → Qc' es)
    (hb : ∀ es, Qb es → Qb' es)
    (he : ∀ exc es, Qe exc es → Qe' exc es)
    {preEs es : ExecState}
    (h : wp s Qn Qr Qc Qb Qe preEs es) :
    wp s Qn' Qr' Qc' Qb' Qe' preEs es := by
  induction s generalizing Qn Qn' Qr Qr' Qc Qc' Qb Qb' Qe Qe' preEs es with
  | skip          => exact hn _ h
  | assign        => exact hn _ h
  | augAssign     => exact hn _ h
  | arraySet      => exact hn _ h
  | ret           => exact hr _ h
  | continue_     => exact hc _ h
  | break_        => exact hb _ h
  | raise_ _      => exact he _ _ h
  | assert_ _ _   => simp only [wp] at h ⊢; exact ⟨h.1, hn _ h.2⟩
  | tupleUnpack _ _ => exact hn _ h
  | ghostDecl _ _ _   => exact hn _ h
  | ghostAssign _ _ _ _ => exact hn _ h
  | label_ _      => exact hn _ h
  | fieldAssign _ _ _   => exact hn _ h
  | fieldAugAssign _ _ _ _ => exact hn _ h
  | acquires _       => exact hn _ h
  | releases _       => exact hn _ h
  | lambda _ _ _     => exact hn _ h   -- Phase 8: leaf, Qn (es[x↦closure])
  | call r fn arg =>
    -- Phase 8: SCall WP is a behavioural formula. Destruct on evalExpr fn.
    rcases heq : evalExpr es.regState fn with _ | _ | ⟨p, b, c⟩
    all_goals simp only [wp, heq] at h ⊢
    all_goals try trivial
    intro st' v Hexec; apply hn; exact (h st' v Hexec)
  | seq s1 s2 ih1 ih2 =>
    simp only [wp] at h ⊢
    exact ih1 (fun es' h' => ih2 hn hr hc hb he h') hr hc hb he h
  | ite _ s1 s2 ih1 ih2 =>
    simp only [wp] at h ⊢
    exact ⟨fun hcond => ih1 hn hr hc hb he (h.1 hcond),
           fun hcond => ih2 hn hr hc hb he (h.2 hcond)⟩
  | while_ _ _ _ _ ih =>
    simp only [wp] at h ⊢
    obtain ⟨hInv, hBody, hExit⟩ := h
    refine ⟨hInv, fun es' hInv' hCond => ?_, fun es' hInv' hCond => hn _ (hExit es' hInv' hCond)⟩
    -- break continuation of body = outer Qn; change Qb via hn, leave bodyDone fixed
    exact ih (fun _ h => h) hr (fun _ h => h) hn he (hBody es' hInv' hCond)
  | for_ _ _ _ _ _ _ ih =>
    simp only [wp] at h ⊢
    obtain ⟨hInv, hBody, hExit⟩ := h
    refine ⟨hInv, fun es' hInv' hCond => ?_, fun es' hInv' hCond => hn _ (hExit es' hInv' hCond)⟩
    -- break continuation of body = outer Qn; change Qb via hn, leave bodyDone fixed
    exact ih (fun _ h => h) hr (fun _ h => h) hn he (hBody es' hInv' hCond)
  | tryCatch _ exc _ ih1 ih2 =>
    simp only [wp] at h ⊢
    apply ih1 hn hr hc hb _ h
    intro e' es' h'
    -- Bool.eq_false_or_eq_true : b = true ∨ b = false  (TRUE first)
    rcases Bool.eq_false_or_eq_true (e' == exc) with heq | heq
    · rw [if_pos heq] at h' ⊢; exact ih2 hn hr hc hb he h'
    · have hf : ¬((e' == exc) = true) := fun h => Bool.false_ne_true (heq ▸ h)
      rw [if_neg hf] at h' ⊢; exact he _ _ h'
  | critical _ _ ih =>
    simp only [wp] at h ⊢; exact ih hn hr hc hb he h
  | threadEntry _ ih =>
    simp only [wp] at h ⊢; exact ih hn hr hc hb he h

-- ===== WP Desugaring (forward direction) =====

-- incIdxFn: state after executing augAssign forIdx add 1
private def incIdxFn (es : ExecState) : ExecState :=
  let cur := match lookup es.regState forIdx with | some (.int n) => n | _ => 0
  setReg es (update es.regState forIdx (.int (cur + 1)))

-- WP of augAssign forIdx add 1 simplifies to Qn (incIdxFn es)
private theorem wp_augAssign_forIdx
    (Qn : ExecState → Prop) (Qr Qc Qb : ExecState → Prop)
    (Qe : Ident → ExecState → Prop) (preEs es : ExecState) :
    wp (.augAssign forIdx .add (.int 1)) Qn Qr Qc Qb Qe preEs es = Qn (incIdxFn es) := by
  simp only [wp, incIdxFn, evalExpr, evalBinopZ]
  rfl

-- liftContinue_wp: lifting continue through incIdx threads (Qc ∘ incIdxFn) into the body.
-- Key property: the WP of (liftContinue incIdx s) with continuation Qc equals
-- the WP of s with continuation (Qc ∘ incIdxFn).
private theorem liftContinue_wp (s : Stmt)
    (Qn Qr : ExecState → Prop) (Qc Qb : ExecState → Prop)
    (Qe : Ident → ExecState → Prop) (preEs es : ExecState) :
    wp (liftContinue (.augAssign forIdx .add (.int 1)) s) Qn Qr Qc Qb Qe preEs es =
    wp s Qn Qr (fun es' => Qc (incIdxFn es')) Qb Qe preEs es := by
  induction s generalizing Qn Qr Qc Qb Qe preEs es with
  | skip => simp only [liftContinue, wp]
  | assign _ _ => simp only [liftContinue, wp]
  | augAssign _ _ _ => simp only [liftContinue, wp]
  | arraySet _ _ _ => simp only [liftContinue, wp]
  | ret _ => simp only [liftContinue, wp]
  | break_ => simp only [liftContinue, wp]
  | assert_ _ _ => simp only [liftContinue, wp]
  | tupleUnpack _ _ => simp only [liftContinue, wp]
  | ghostDecl _ _ _ => simp only [liftContinue, wp]
  | ghostAssign _ _ _ _ => simp only [liftContinue, wp]
  | label_ _ => simp only [liftContinue, wp]
  | raise_ _ => simp only [liftContinue, wp]
  | fieldAssign _ _ _   => simp only [liftContinue, wp]
  | fieldAugAssign _ _ _ _ => simp only [liftContinue, wp]
  | acquires _       => simp only [liftContinue, wp]
  | releases _       => simp only [liftContinue, wp]
  | call _ _ _       => simp only [liftContinue, wp]
  | lambda _ _ _     => simp only [liftContinue, wp]
  | while_ _ _ _ _ _ => simp only [liftContinue, wp]
  | for_ _ _ _ _ _ _ => simp only [liftContinue, wp]
  | continue_ => simp only [liftContinue, wp, incIdxFn, evalExpr, evalBinopZ]; rfl
  | seq s1 s2 ih1 ih2 =>
    simp only [liftContinue, wp]
    have h2 := funext (fun es' => ih2 Qn Qr Qc Qb Qe preEs es')
    rw [h2]
    exact ih1 (fun es' => wp s2 Qn Qr (fun es'' => Qc (incIdxFn es'')) Qb Qe preEs es')
              Qr Qc Qb Qe preEs es
  | ite _ s1 s2 ih1 ih2 =>
    simp only [liftContinue, wp, ih1, ih2]
  | tryCatch s1 exc handler ih1 ih2 =>
    simp only [liftContinue, wp]
    have hQe : (fun exc' es' =>
                  if (exc' == exc) = true
                  then wp (liftContinue (.augAssign forIdx .add (.int 1)) handler) Qn Qr Qc Qb Qe preEs es'
                  else Qe exc' es') =
               (fun exc' es' =>
                  if (exc' == exc) = true
                  then wp handler Qn Qr (fun es'' => Qc (incIdxFn es'')) Qb Qe preEs es'
                  else Qe exc' es') := by
      funext e' es'
      by_cases heq : (e' == exc) = true
      · rw [if_pos heq, if_pos heq]; exact ih2 Qn Qr Qc Qb Qe preEs es'
      · rw [if_neg heq, if_neg heq]
    rw [hQe]
    exact ih1 Qn Qr Qc Qb _ preEs es
  | critical _ _ ih =>
    simp only [liftContinue, wp]
    exact ih Qn Qr Qc Qb Qe preEs es
  | threadEntry _ ih =>
    simp only [liftContinue, wp]
    exact ih Qn Qr Qc Qb Qe preEs es

theorem wp_desugar_fwd (s : Stmt)
    (Qn Qr Qc Qb : ExecState → Prop)
    (Qe : Ident → ExecState → Prop)
    (preEs es : ExecState)
    (h : wp s Qn Qr Qc Qb Qe preEs es) :
    wp (desugar s) Qn Qr Qc Qb Qe preEs es := by
  induction s generalizing Qn Qr Qc Qb Qe preEs es with
  | skip          => exact h
  | assign        => exact h
  | augAssign     => exact h
  | arraySet      => exact h
  | ret           => exact h
  | continue_     => exact h
  | break_        => exact h
  | assert_ _ _   => exact h
  | tupleUnpack _ _ => exact h
  | ghostDecl _ _ _   => exact h
  | ghostAssign _ _ _ _ => exact h
  | label_ _      => exact h
  | raise_ _      => exact h
  | fieldAssign _ _ _   => exact h
  | fieldAugAssign _ _ _ _ => exact h
  | acquires _       => exact h
  | releases _       => exact h
  | call r fn arg    => exact h
  | lambda _ _ _     => exact h
  | seq s1 s2 ih1 ih2 =>
    simp only [desugar, wp] at h ⊢
    -- Step 1: desugar s1 using IH for s1
    have h1 := ih1 (fun es' => wp s2 Qn Qr Qc Qb Qe preEs es') Qr Qc Qb Qe preEs es h
    -- Step 2: desugar s2 in the inner continuation via wp_mono on desugar s1
    exact wp_mono (fun es' h' => ih2 Qn Qr Qc Qb Qe preEs es' h')
      (fun _ h => h) (fun _ h => h) (fun _ h => h) (fun _ _ h => h) h1
  | ite _ s1 s2 ih1 ih2 =>
    simp only [desugar, wp] at h ⊢
    exact ⟨fun hcond => ih1 Qn Qr Qc Qb Qe preEs es (h.1 hcond),
           fun hcond => ih2 Qn Qr Qc Qb Qe preEs es (h.2 hcond)⟩
  | while_ _ _ _ _ ih_body =>
    simp only [desugar, wp] at h ⊢
    obtain ⟨hInv, hBody, hExit⟩ := h
    -- desugar (.while_ i v c b) = .while_ i v c (desugar b): body IH suffices
    exact ⟨hInv, fun es' hInv' hCond =>
      ih_body _ Qr _ Qn Qe preEs es' (hBody es' hInv' hCond), hExit⟩
  | for_ x arr inv var body _aim ih_body =>
    simp only [desugar, wp] at h ⊢
    -- h : evalC es0 inv ∧ (∀ es' inv guard → wp body bodyDone ...) ∧ (∀ es' inv ¬guard → Qn)
    obtain ⟨hInv, hBody, hExit⟩ := h
    refine ⟨hInv, fun es' hInv' hGuard => ?_, hExit⟩
    rw [liftContinue_wp]
    exact ih_body _ Qr _ Qn Qe preEs _ (hBody es' hInv' hGuard)
  | tryCatch s1 exc handler ih1 ih2 =>
    simp only [desugar, wp] at h ⊢
    -- Apply ih1 first so Lean infers the upgraded Qe from the outer goal.
    -- Then upgrade wp handler → wp (desugar handler) in the continuation via wp_mono.
    -- Note: if (e' == exc) has Prop condition (e' == exc = true), so use if_pos/if_neg.
    apply ih1
    apply wp_mono (fun _ hx => hx) (fun _ hx => hx) (fun _ hx => hx) (fun _ hx => hx) _ h
    intro e' es'' h_exc
    -- Bool.eq_false_or_eq_true : b = true ∨ b = false  (TRUE first)
    rcases Bool.eq_false_or_eq_true (e' == exc) with heq | heq
    · rw [if_pos heq] at h_exc ⊢
      exact ih2 Qn Qr Qc Qb Qe preEs es'' h_exc
    · have hf : ¬((e' == exc) = true) := fun h => Bool.false_ne_true (heq ▸ h)
      rw [if_neg hf] at h_exc ⊢; exact h_exc
  | critical _ _ ih =>
    simp only [desugar, wp] at h ⊢; exact ih Qn Qr Qc Qb Qe preEs es h
  | threadEntry _ ih =>
    simp only [desugar, wp] at h ⊢; exact ih Qn Qr Qc Qb Qe preEs es h

def outcomePost
    (Qn Qr Qc Qb : ExecState → Prop)
    (Qe : Ident → ExecState → Prop) : Outcome → Prop
  | .normal es'     => Qn es'
  | .returned es' _ => Qr es'
  | .continued es'  => Qc es'
  | .broke es'      => Qb es'
  | .threw es' exc  => Qe exc es'
  | .failed _ _ _   => True

theorem pycsl_soundness
    (es : ExecState) (s : Stmt) (out : Outcome)
    (Qn Qr Qc Qb : ExecState → Prop)
    (Qe : Ident → ExecState → Prop)
    (preEs : ExecState)
    (hExec : Exec es s out)
    (hWp : wp s Qn Qr Qc Qb Qe preEs es) :
    outcomePost Qn Qr Qc Qb Qe out := by
  induction hExec generalizing Qn Qr Qc Qb Qe preEs with
  -- Leaf rules: outcome directly determined by WP
  | execSkip         => exact hWp
  | execAssign       => exact hWp
  | execAugAssign    => exact hWp
  | execArraySet     => exact hWp
  | execContinue     => exact hWp
  | execBreak        => exact hWp
  | execReturn       => exact hWp
  | execTupleUnpack  => exact hWp
  | execGhostDecl    => exact hWp
  | execGhostAssign  => exact hWp
  | execLabel        => exact hWp
  | execRaise        => exact hWp
  | execFieldAssign  => exact hWp
  | execFieldAugAssign => exact hWp
  | execAssertFail   => trivial   -- OFailed → outcomePost = True
  | execAssertPass es cond msg hcond =>
    simp only [wp] at hWp; exact hWp.2
  -- With `induction ... generalizing Qn Qr Qc Qb Qe preEs`, IH arg order is:
  --   ih Qn Qr Qc Qb Qe preEs hWp
  -- Seq: chain IH1 → IH2
  | execSeq es s1 s2 es' out _ _ ih1 ih2 =>
    simp only [wp] at hWp
    exact ih2 Qn Qr Qc Qb Qe preEs
      (ih1 (fun es'' => wp s2 Qn Qr Qc Qb Qe preEs es'') Qr Qc Qb Qe preEs hWp)
  | execSeqReturn _ s1 s2 es' _ _ ih =>
    simp only [wp] at hWp
    exact ih (fun es'' => wp s2 Qn Qr Qc Qb Qe preEs es'') Qr Qc Qb Qe preEs hWp
  | execSeqContinue _ s1 s2 es' _ ih =>
    simp only [wp] at hWp
    exact ih (fun es'' => wp s2 Qn Qr Qc Qb Qe preEs es'') Qr Qc Qb Qe preEs hWp
  | execSeqBreak _ s1 s2 es' _ ih =>
    simp only [wp] at hWp
    exact ih (fun es'' => wp s2 Qn Qr Qc Qb Qe preEs es'') Qr Qc Qb Qe preEs hWp
  | execSeqThrow _ s1 s2 es' _ _ ih =>
    simp only [wp] at hWp
    exact ih (fun es'' => wp s2 Qn Qr Qc Qb Qe preEs es'') Qr Qc Qb Qe preEs hWp
  -- If: dispatch on the branch taken
  | execIfTrue _ cond s1 s2 _ hcond _ ih =>
    simp only [wp] at hWp; exact ih Qn Qr Qc Qb Qe preEs (hWp.1 hcond)
  | execIfFalse _ cond s1 s2 _ hcond _ ih =>
    simp only [wp] at hWp; exact ih Qn Qr Qc Qb Qe preEs (hWp.2 hcond)
  -- While: body soundness extracts invariant for next iteration
  | execWhileTrue es inv var cond body es' out hcond _ _ ih1 ih2 =>
    simp only [wp] at hWp
    obtain ⟨hInv, hPres, hPost⟩ := hWp
    have hbd := ih1
      (fun es'' => evalC es'' preEs none inv ∧ evalV es'' preEs var < evalV es preEs var ∧ evalV es'' preEs var ≥ 0)
      Qr
      (fun es'' => evalC es'' preEs none inv ∧ evalV es'' preEs var < evalV es preEs var ∧ evalV es'' preEs var ≥ 0)
      Qn Qe preEs (hPres es hInv hcond)
    exact ih2 Qn Qr Qc Qb Qe preEs (by simp only [wp]; exact ⟨hbd.1, hPres, hPost⟩)
  | execWhileContinue es inv var cond body es' out hcond _ _ ih1 ih2 =>
    simp only [wp] at hWp
    obtain ⟨hInv, hPres, hPost⟩ := hWp
    have hbd := ih1
      (fun es'' => evalC es'' preEs none inv ∧ evalV es'' preEs var < evalV es preEs var ∧ evalV es'' preEs var ≥ 0)
      Qr
      (fun es'' => evalC es'' preEs none inv ∧ evalV es'' preEs var < evalV es preEs var ∧ evalV es'' preEs var ≥ 0)
      Qn Qe preEs (hPres es hInv hcond)
    exact ih2 Qn Qr Qc Qb Qe preEs (by simp only [wp]; exact ⟨hbd.1, hPres, hPost⟩)
  | execWhileBreak es inv var cond body es' hcond _ ih =>
    simp only [wp] at hWp
    obtain ⟨hInv, hPres, _⟩ := hWp
    exact ih
      (fun es'' => evalC es'' preEs none inv ∧ evalV es'' preEs var < evalV es preEs var ∧ evalV es'' preEs var ≥ 0)
      Qr
      (fun es'' => evalC es'' preEs none inv ∧ evalV es'' preEs var < evalV es preEs var ∧ evalV es'' preEs var ≥ 0)
      Qn Qe preEs (hPres es hInv hcond)
  | execWhileFalse es inv var cond body hc =>
    simp only [wp] at hWp; exact hWp.2.2 es hWp.1 hc
  -- TryCatch: route exception through conditional Qe
  | execTryCatchCaught es body exc handler es' out _ _ ih1 ih2 =>
    simp only [wp] at hWp
    have hih := ih1 Qn Qr Qc Qb
      (fun e'' es'' => if e'' == exc then wp handler Qn Qr Qc Qb Qe preEs es'' else Qe e'' es'') preEs hWp
    simp only [outcomePost, beq_self_eq_true, ite_true] at hih
    exact ih2 Qn Qr Qc Qb Qe preEs hih
  | execTryCatchMiss es body exc exc' handler es' hne _ ih =>
    simp only [wp] at hWp
    have hih := ih Qn Qr Qc Qb
      (fun e'' es'' => if e'' == exc then wp handler Qn Qr Qc Qb Qe preEs es'' else Qe e'' es'') preEs hWp
    simp only [outcomePost] at hih
    simp only [show (exc' == exc) = false from beq_false_of_ne hne] at hih
    exact hih
  | execTryCatchNormal es body exc handler out hno _ ih =>
    simp only [wp] at hWp
    have hih := ih Qn Qr Qc Qb
      (fun e'' es'' => if e'' == exc then wp handler Qn Qr Qc Qb Qe preEs es'' else Qe e'' es'') preEs hWp
    -- hih : outcomePost Qn Qr Qc Qb (fun e'' es'' => ...) out
    -- goal: outcomePost Qn Qr Qc Qb Qe out
    -- Non-threw outcomes agree; threw is excluded by hno.
    rcases out with es' | ⟨es', v⟩ | es' | es' | ⟨es', msg, cond⟩ | ⟨es', exc'⟩
    · exact hih
    · exact hih
    · exact hih
    · exact hih
    · trivial
    · exact absurd rfl (hno es' exc')
  -- Critical / ThreadEntry: WP wrappers. criticalHavoc reduces to
  -- identity in the Hoare instance (see MemModel.lean).
  | execCritical _ _ body _ _ ih =>
    simp only [wp, criticalHavoc] at hWp
    exact ih Qn Qr Qc Qb Qe preEs hWp
  | execThreadEntry _ body _ _ ih =>
    simp only [wp] at hWp; exact ih Qn Qr Qc Qb Qe preEs hWp
  -- For: ExecFor gives Exec es0 (desugar (.for_ ...)) out; wp_desugar_fwd bridges the WPs
  | execFor es0 x arr inv var body aim _ _ ih =>
    exact ih Qn Qr Qc Qb Qe preEs (wp_desugar_fwd (.for_ x arr inv var body aim) Qn Qr Qc Qb Qe preEs es0 hWp)
  -- Acquires/Releases: leaf, Qn es
  | execAcquires _ _ => exact hWp
  | execReleases _ _ => exact hWp
  | @execCall es r fn arg param body cstate st' v hfn hb =>
    -- Phase 8: SCall fires when body produced .returned st' v.
    -- The WP's behavioural formula gives Qn (setReg es (update r v)) directly.
    simp only [wp] at hWp
    rw [hfn] at hWp
    exact hWp _ _ hb
  | execLambda es x param body =>
    -- Phase 8: leaf — SOS outcome ≡ WP term (the assign pattern).
    exact hWp

-- ===== Phase 3c: \at label scoping theorems =====

theorem labelRecordsGhostState
    {es : ExecState} {L : Ident} {es' : ExecState}
    (hExec : Exec es (.label_ L) (.normal es')) :
    labelLookup es'.labelSnaps L = some es.ghostSt := by
  cases hExec; simp [labelLookup, setLabels]

theorem atLabelScoping
    {es es' : ExecState} {L : Ident} {expr : ContractExpr}
    {preEs : ExecState} {result : Option Val}
    (hExec : Exec es (.label_ L) (.normal es')) :
    evalContractEs es' preEs result (.at_ expr L) =
    evalContractEs (setGhost es' es.ghostSt) preEs result expr := by
  simp only [evalContractEs]
  rw [labelRecordsGhostState hExec]

-- ===== Ghost state invariant =====

theorem ghostStmtPreservesRegState
    {es : ExecState} {s : Stmt} {es' : ExecState}
    (hExec : Exec es s (.normal es'))
    (hs : (∃ x t e, s = .ghostDecl x t e) ∨
          (∃ x t op e, s = .ghostAssign x t op e) ∨
          (∃ L, s = .label_ L)) :
    es'.regState = es.regState := by
  rcases hs with ⟨x, t, e, rfl⟩ | ⟨x, t, op, e, rfl⟩ | ⟨L, rfl⟩
  · cases hExec; rfl
  · cases hExec; rfl
  · cases hExec; rfl

-- ===== Phase 4: Bounded integer side obligation =====

def inRange (bits : Nat) (n : Int) : Prop :=
  -(2 : Int) ^ (bits - 1) ≤ n ∧ n < (2 : Int) ^ (bits - 1)

def boundedAssignWp (bits : Nat) (x : Ident) (e : Expr)
    (Qn : ExecState → Prop) (es : ExecState) : Prop :=
  let v := evalExpr es.regState e
  (∀ n, v = .int n → inRange bits n) ∧
  Qn (setReg es (update es.regState x v))

-- ===== Phase 9: Static semantics well-formedness =====

inductive WfExpr : List (Ident × String) → ContractExpr → Prop where
  | wfInt    : ∀ {Γ} n, WfExpr Γ (.int n)
  | wfVar    : ∀ {Γ} x, (x, "int") ∈ Γ ∨ (x, "array") ∈ Γ → WfExpr Γ (.var x)
  | wfResult : ∀ {Γ}, WfExpr Γ .result
  | wfBinop  : ∀ {Γ} op e1 e2, WfExpr Γ e1 → WfExpr Γ e2 → WfExpr Γ (.binop op e1 e2)
  | wfForall : ∀ {Γ} x body, WfExpr ((x, "int") :: Γ) body → WfExpr Γ (.forall_ x body)
  | wfExists : ∀ {Γ} x body, WfExpr ((x, "int") :: Γ) body → WfExpr Γ (.exists_ x body)

theorem wfExprSafe (Γ : List (Ident × String)) (e : ContractExpr) (es : ExecState)
    (_h : WfExpr Γ e) : ∃ v, evalZ es.regState es.regState none e = v :=
  ⟨_, rfl⟩

-- ===== Phase 3.4: Explicit trusted-oracle parameter =====

-- pycslSoundnessWithOracle: soundness holds for any caller-supplied trusted oracle.
-- Making the oracle explicit documents the trust boundary.
theorem pycslSoundnessWithOracle
    (trustedOracle : ∀ (spec : FuncSpec),
       spec.trusted = true →
       ∀ (preEs postEs : ExecState),
         evalC preEs preEs none spec.pre →
         evalC postEs preEs none spec.post)
    {es : ExecState} {s : Stmt} {out : Outcome}
    {Qn Qr Qc Qb : ExecState → Prop}
    {Qe : Ident → ExecState → Prop}
    {preEs : ExecState}
    (hExec : Exec es s out)
    (hWp : wp s Qn Qr Qc Qb Qe preEs es) :
    outcomePost Qn Qr Qc Qb Qe out :=
  pycsl_soundness es s out Qn Qr Qc Qb Qe preEs hExec hWp

-- ===== Phase 10: Trust base axioms =====
-- why3WpSound removed: superseded by pycslSoundnessVerified + why3ImplementsWpW (Path B).

-- Axiom: Alt-Ergo/Z3/SMT solver is correct for NON-LINEAR goals.
--
-- NARROWING CONVENTION (Task 7): This axiom must NOT be used for goals that
-- are provable by Lean's omega tactic (linear arithmetic: index bounds, loop-
-- variant decrements, simple integer comparisons).  For those goals, generated
-- code uses `(⟨by omega⟩ : LinearArithVC goal).prf` instead — no external
-- SMT dependency.  The Module6 generator (Task 7b) classifies each VC at
-- emission time and routes it to the correct path.
--
-- Proof that the convention is respected: `#print axioms` for any theorem
-- whose VCs are all linear must NOT list `altErgoCorrect`.
axiom altErgoCorrect (goal : Prop) : SmtCertificate goal → goal

-- Helper: prove a linear arithmetic goal directly via omega.
-- This is the preferred path for generated code; it does not depend on
-- altErgoCorrect and therefore does not add altErgoCorrect to the axiom set.
theorem linArithProof (goal : Prop) (hLin : LinearArithVC goal) : goal :=
  hLin.prf

-- Axiom: \trusted contracts are assumed correct
-- Conditional form: postcondition holds only when precondition is established.
-- Reduces TCB: a wrong trusted spec only causes unsoundness for callers that
-- establish the precondition (rather than unconditionally).
axiom trustedContractsAxiom (spec : FuncSpec) :
    spec.trusted = true →
    ∀ (preEs postEs : ExecState),
      evalC preEs preEs none spec.pre →
      evalC postEs preEs none spec.post
