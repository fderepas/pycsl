/-
  WPW.lean — WP Semantics for the WhyML Subset
  Defines WpConts (exception-encoded continuation record),
  enc (packs 5 loose continuations into WpConts),
  and wpW (WP semantics for WhyMLStmt, structurally parallel to wp).

  Key invariant: wpW mirrors wp case-by-case.
  Full correspondence proved in CorrMain.lean.
-/
import PyCSL.AST
import PyCSL.State
import PyCSL.WP
import PyCSL.WhyML

-- ===== Exception-encoded continuation record =====

structure WpConts where
  wcN : ExecState → Prop   -- normal completion
  wcR : ExecState → Prop   -- return
  wcC : ExecState → Prop   -- continue
  wcB : ExecState → Prop   -- break
  wcE : Ident → ExecState → Prop  -- named exception

-- enc: pack the five loose continuations into a WpConts record
def enc (Qn Qr Qc Qb : ExecState → Prop) (Qe : Ident → ExecState → Prop) : WpConts :=
  { wcN := Qn, wcR := Qr, wcC := Qc, wcB := Qb, wcE := Qe }

-- ===== wpW: WP semantics for the WhyML subset =====
-- Every case directly mirrors the corresponding wp case in WP.lean.
-- SWhile body: wc_b := Q.wcN (break exits loop normally),
--              wc_c := bodyDone (continue re-enters).

def wpW : WhyMLStmt → WpConts → (preEs es : ExecState) → Prop
  | .wSkip, Q, _, es => Q.wcN es

  | .wAssign x e, Q, _, es =>
    Q.wcN (setReg es (update es.regState x (evalExpr es.regState e)))

  | .wAugAssign x op e, Q, _, es =>
    let cur := match lookup es.regState x with | some (.int n) => n | _ => 0
    let nv  := evalBinopZ op cur (match evalExpr es.regState e with | .int n => n | _ => 0)
    Q.wcN (setReg es (update es.regState x (.int nv)))

  | .wArraySet arr i v, Q, _, es =>
    let idx := match evalExpr es.regState i with | .int n => n | _ => 0
    let nv  := match evalExpr es.regState v with | .int n => n | _ => 0
    Q.wcN (setReg es (arrayUpdate es.regState arr idx nv))

  | .wSeq w1 w2, Q, preEs, es =>
    wpW w1 { wcN := fun es' => wpW w2 Q preEs es',
             wcR := Q.wcR, wcC := Q.wcC, wcB := Q.wcB, wcE := Q.wcE }
        preEs es

  | .wIf cond w1 w2, Q, preEs, es =>
    (evalBool es.regState cond = true  → wpW w1 Q preEs es) ∧
    (evalBool es.regState cond = false → wpW w2 Q preEs es)

  | .wWhile invs vars cond body, Q, preEs, es =>
    let inv := cConj invs
    let var := cFirst vars
    evalC es preEs none inv ∧
    (∀ es', evalC es' preEs none inv →
            evalBool es'.regState cond = true →
            let bodyDone es'' :=
              evalC es'' preEs none inv ∧
              evalV es'' preEs var < evalV es' preEs var ∧
              evalV es'' preEs var ≥ 0
            wpW body { wcN := bodyDone, wcR := Q.wcR,
                       wcC := bodyDone, wcB := Q.wcN, wcE := Q.wcE }
                preEs es') ∧
    (∀ es', evalC es' preEs none inv →
            evalBool es'.regState cond = false → Q.wcN es')

  | .wRaise .excReturn,    Q, _, es => Q.wcR es
  | .wRaise .excBreak,     Q, _, es => Q.wcB es
  | .wRaise .excContinue,  Q, _, es => Q.wcC es
  | .wRaise (.excNamed n), Q, _, es => Q.wcE n es

  | .wTryCatch body exc handler, Q, preEs, es =>
    wpW body { wcN := Q.wcN, wcR := Q.wcR, wcC := Q.wcC, wcB := Q.wcB,
               wcE := fun exc' es' =>
                 if exc' == exc then wpW handler Q preEs es'
                 else Q.wcE exc' es' }
        preEs es

  | .wGhostDecl x t e, Q, _, es =>
    Q.wcN (setGhost es (ghostUpdate es.ghostSt x (evalGhostVal t es e)))

  | .wGhostAssign x _ op e, Q, _, es =>
    let cur := ghostLookup es.ghostSt x
    let nv  := applyGhostAug op cur es e
    Q.wcN (setGhost es (ghostUpdate es.ghostSt x nv))

  | .wLabel L, Q, _, es =>
    Q.wcN (setLabels es ((L, es.ghostSt) :: es.labelSnaps))

  | .wAssert cond _, Q, preEs, es =>
    evalC es preEs none cond ∧ Q.wcN es

-- ===== Monotonicity of wpW =====

theorem wpW_mono
    (ws : WhyMLStmt) (Q Q' : WpConts) (preEs es : ExecState)
    (hn : ∀ e, Q.wcN e → Q'.wcN e) (hr : ∀ e, Q.wcR e → Q'.wcR e)
    (hc : ∀ e, Q.wcC e → Q'.wcC e) (hb : ∀ e, Q.wcB e → Q'.wcB e)
    (he : ∀ x e, Q.wcE x e → Q'.wcE x e) :
    wpW ws Q preEs es → wpW ws Q' preEs es := by
  induction ws generalizing Q Q' preEs es with
  | wSkip =>      intro Hwp; exact hn _ Hwp
  | wAssign =>    intro Hwp; exact hn _ Hwp
  | wAugAssign => intro Hwp; exact hn _ Hwp
  | wArraySet =>  intro Hwp; exact hn _ Hwp
  -- wSeq: pass modified Q/Q' fully positionally to avoid named-arg position confusion
  | wSeq w1 w2 ih1 ih2 =>
    intro Hwp
    simp only [wpW] at *
    apply ih1
      { wcN := fun es' => wpW w2 Q  preEs es', wcR := Q.wcR,  wcC := Q.wcC,  wcB := Q.wcB,  wcE := Q.wcE }
      { wcN := fun es' => wpW w2 Q' preEs es', wcR := Q'.wcR, wcC := Q'.wcC, wcB := Q'.wcB, wcE := Q'.wcE }
      preEs es
    · intro es' hes'; exact ih2 Q Q' preEs es' hn hr hc hb he hes'
    · exact hr
    · exact hc
    · exact hb
    · exact he
    · exact Hwp
  | wIf cond w1 w2 ih1 ih2 =>
    intro Hwp
    simp only [wpW] at *
    exact ⟨fun h => ih1 Q Q' preEs es hn hr hc hb he (Hwp.1 h),
           fun h => ih2 Q Q' preEs es hn hr hc hb he (Hwp.2 h)⟩
  -- wWhile: pass modified body continuations fully positionally
  | wWhile invs vars cond body ih =>
    intro Hwp
    simp only [wpW] at *
    obtain ⟨hinv, hbody, hexit⟩ := Hwp
    refine ⟨hinv, fun es' hinv' hcond => ?_, fun es' hinv' hcond => hn _ (hexit es' hinv' hcond)⟩
    apply ih
      { wcN := fun es'' => evalC es'' preEs none (cConj invs) ∧ evalV es'' preEs (cFirst vars) < evalV es' preEs (cFirst vars) ∧ evalV es'' preEs (cFirst vars) ≥ 0,
        wcR := Q.wcR,
        wcC := fun es'' => evalC es'' preEs none (cConj invs) ∧ evalV es'' preEs (cFirst vars) < evalV es' preEs (cFirst vars) ∧ evalV es'' preEs (cFirst vars) ≥ 0,
        wcB := Q.wcN, wcE := Q.wcE }
      { wcN := fun es'' => evalC es'' preEs none (cConj invs) ∧ evalV es'' preEs (cFirst vars) < evalV es' preEs (cFirst vars) ∧ evalV es'' preEs (cFirst vars) ≥ 0,
        wcR := Q'.wcR,
        wcC := fun es'' => evalC es'' preEs none (cConj invs) ∧ evalV es'' preEs (cFirst vars) < evalV es' preEs (cFirst vars) ∧ evalV es'' preEs (cFirst vars) ≥ 0,
        wcB := Q'.wcN, wcE := Q'.wcE }
      preEs es'
    · intro _ h; exact h
    · exact hr
    · intro _ h; exact h
    · exact hn
    · exact he
    · exact hbody es' hinv' hcond
  -- wRaise: dispatch on exc constructors using rcases
  | wRaise exc =>
    intro Hwp
    rcases exc with _ | _ | _ | n
    · simp only [wpW] at *; exact hr _ Hwp
    · simp only [wpW] at *; exact hb _ Hwp
    · simp only [wpW] at *; exact hc _ Hwp
    · simp only [wpW] at *; exact he _ _ Hwp
  -- wTryCatch: pass modified Q/Q' fully positionally
  | wTryCatch body exc handler ih1 ih2 =>
    intro Hwp
    simp only [wpW] at *
    apply ih1
      { wcN := Q.wcN,  wcR := Q.wcR,  wcC := Q.wcC,  wcB := Q.wcB,
        wcE := fun exc' es' => if exc' == exc then wpW handler Q  preEs es' else Q.wcE  exc' es' }
      { wcN := Q'.wcN, wcR := Q'.wcR, wcC := Q'.wcC, wcB := Q'.wcB,
        wcE := fun exc' es' => if exc' == exc then wpW handler Q' preEs es' else Q'.wcE exc' es' }
      preEs es
    · exact hn
    · exact hr
    · exact hc
    · exact hb
    · intro exc' es' hes'
      -- reduce record projections definitionally, then case-split on the Bool
      have hes'' : if exc' == exc then wpW handler Q preEs es' else Q.wcE exc' es' := hes'
      show if exc' == exc then wpW handler Q' preEs es' else Q'.wcE exc' es'
      cases hbool : (exc' == exc) <;> simp [hbool] at hes'' ⊢
      · exact he _ _ hes''
      · exact ih2 Q Q' preEs es' hn hr hc hb he hes''
    · exact Hwp
  | wGhostDecl =>  intro Hwp; exact hn _ Hwp
  | wGhostAssign => intro Hwp; exact hn _ Hwp
  | wLabel =>      intro Hwp; exact hn _ Hwp
  | wAssert =>
    intro Hwp
    simp only [wpW] at *
    exact ⟨Hwp.1, hn _ Hwp.2⟩

-- ===== Congruence of wpW w.r.t. extensionally equal continuations =====

theorem wpW_congr
    (ws : WhyMLStmt) (Q Q' : WpConts) (preEs es : ExecState)
    (hn : ∀ e, Q.wcN e ↔ Q'.wcN e)
    (hr : ∀ e, Q.wcR e ↔ Q'.wcR e)
    (hc : ∀ e, Q.wcC e ↔ Q'.wcC e)
    (hb : ∀ e, Q.wcB e ↔ Q'.wcB e)
    (he : ∀ x e, Q.wcE x e ↔ Q'.wcE x e) :
    wpW ws Q preEs es ↔ wpW ws Q' preEs es :=
  ⟨wpW_mono ws Q Q' preEs es
     (fun e h => (hn e).mp h) (fun e h => (hr e).mp h) (fun e h => (hc e).mp h)
     (fun e h => (hb e).mp h) (fun x e h => (he x e).mp h),
   wpW_mono ws Q' Q preEs es
     (fun e h => (hn e).mpr h) (fun e h => (hr e).mpr h) (fun e h => (hc e).mpr h)
     (fun e h => (hb e).mpr h) (fun x e h => (he x e).mpr h)⟩
