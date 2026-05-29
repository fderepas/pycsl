/-
  CorrLoops.lean — WP Correspondence for Loop and Compound Statements
  Proves the correspondence for SSeq, SIf, SWhile, SFor, SCritical, SThreadEntry.
  These are the inductive cases requiring the IH on sub-terms.
-/
import PyCSL.AST
import PyCSL.State
import PyCSL.WP
import PyCSL.WhyML
import PyCSL.WPW
import PyCSL.StmtGen
import PyCSL.CorrSimple

-- ===== SSeq =====

theorem wpGen_seq (s1 s2 : Stmt)
    (Qn Qr Qc Qb : ExecState → Prop) (Qe : Ident → ExecState → Prop)
    (preEs es : ExecState)
    (ih1 : ∀ Qn' Qr' Qc' Qb' (Qe' : Ident → ExecState → Prop) preEs' es',
           wp s1 Qn' Qr' Qc' Qb' Qe' preEs' es' ↔
           wpW (gen s1) (enc Qn' Qr' Qc' Qb' Qe') preEs' es')
    (ih2 : ∀ Qn' Qr' Qc' Qb' (Qe' : Ident → ExecState → Prop) preEs' es',
           wp s2 Qn' Qr' Qc' Qb' Qe' preEs' es' ↔
           wpW (gen s2) (enc Qn' Qr' Qc' Qb' Qe') preEs' es') :
    wp (.seq s1 s2) Qn Qr Qc Qb Qe preEs es ↔
    wpW (gen (.seq s1 s2)) (enc Qn Qr Qc Qb Qe) preEs es := by
  -- LHS: wp s1 (fun es' => wp s2 Qn Qr Qc Qb Qe preEs es') Qr Qc Qb Qe preEs es
  -- RHS: wpW (gen s1) {wcN := fun es' => wpW (gen s2) (enc Qn Qr Qc Qb Qe) preEs es',
  --                    wcR := Qr, wcC := Qc, wcB := Qb, wcE := Qe} preEs es
  simp only [wp, gen, wpW, enc]
  -- After simp: LHS = wp s1 (fun es' => wp s2 ...) Qr Qc Qb Qe preEs es
  --             RHS = wpW (gen s1) {wcN := fun es' => wpW (gen s2) ..., ...} preEs es
  rw [ih1 (fun es' => wp s2 Qn Qr Qc Qb Qe preEs es') Qr Qc Qb Qe preEs es]
  -- Now goal: wpW (gen s1) (enc (fun es' => wp s2 ...) Qr Qc Qb Qe) preEs es ↔
  --           wpW (gen s1) {wcN := fun es' => wpW (gen s2) ..., ...} preEs es
  apply wpW_congr (gen s1) _ _ preEs es
  · -- wcN: wp s2 Qn ... ↔ wpW (gen s2) (enc Qn ...) for each es'
    intro es'
    exact ih2 Qn Qr Qc Qb Qe preEs es'
  · intro _; exact Iff.rfl    -- wcR
  · intro _; exact Iff.rfl    -- wcC
  · intro _; exact Iff.rfl    -- wcB
  · intro _ _; exact Iff.rfl  -- wcE

-- ===== SIf =====

theorem wpGen_if (cond : Expr) (s1 s2 : Stmt)
    (Qn Qr Qc Qb : ExecState → Prop) (Qe : Ident → ExecState → Prop)
    (preEs es : ExecState)
    (ih1 : ∀ Qn' Qr' Qc' Qb' (Qe' : Ident → ExecState → Prop) preEs' es',
           wp s1 Qn' Qr' Qc' Qb' Qe' preEs' es' ↔
           wpW (gen s1) (enc Qn' Qr' Qc' Qb' Qe') preEs' es')
    (ih2 : ∀ Qn' Qr' Qc' Qb' (Qe' : Ident → ExecState → Prop) preEs' es',
           wp s2 Qn' Qr' Qc' Qb' Qe' preEs' es' ↔
           wpW (gen s2) (enc Qn' Qr' Qc' Qb' Qe') preEs' es') :
    wp (.ite cond s1 s2) Qn Qr Qc Qb Qe preEs es ↔
    wpW (gen (.ite cond s1 s2)) (enc Qn Qr Qc Qb Qe) preEs es := by
  simp [wp, gen, wpW, enc]
  constructor
  · intro ⟨ht, hf⟩
    exact ⟨fun h => (ih1 Qn Qr Qc Qb Qe preEs es).mp (ht h),
           fun h => (ih2 Qn Qr Qc Qb Qe preEs es).mp (hf h)⟩
  · intro ⟨ht, hf⟩
    exact ⟨fun h => (ih1 Qn Qr Qc Qb Qe preEs es).mpr (ht h),
           fun h => (ih2 Qn Qr Qc Qb Qe preEs es).mpr (hf h)⟩

-- ===== SWhile =====

theorem wpGen_while (inv var : ContractExpr) (cond : Expr) (body : Stmt)
    (Qn Qr Qc Qb : ExecState → Prop) (Qe : Ident → ExecState → Prop)
    (preEs es : ExecState)
    (ihBody : ∀ Qn' Qr' Qc' Qb' (Qe' : Ident → ExecState → Prop) preEs' es',
              wp body Qn' Qr' Qc' Qb' Qe' preEs' es' ↔
              wpW (gen body) (enc Qn' Qr' Qc' Qb' Qe') preEs' es') :
    wp (.while_ inv var cond body) Qn Qr Qc Qb Qe preEs es ↔
    wpW (gen (.while_ inv var cond body)) (enc Qn Qr Qc Qb Qe) preEs es := by
  simp [wp, gen, wpW, enc, cConj, cFirst]
  -- After simp, goal is: evalC es … inv → (∀ es', ... exit …) → (body_iff)
  -- simp extracted the common A and C clauses, leaving only the body ↔ to prove.
  intro hinv hexit
  constructor
  · intro hbody es' hinv' hcond
    exact (ihBody
      (fun es'' => evalC es'' preEs none inv ∧ evalV es'' preEs var < evalV es' preEs var ∧ 0 ≤ evalV es'' preEs var)
      Qr
      (fun es'' => evalC es'' preEs none inv ∧ evalV es'' preEs var < evalV es' preEs var ∧ 0 ≤ evalV es'' preEs var)
      Qn Qe preEs es').mp (hbody es' hinv' hcond)
  · intro hbody es' hinv' hcond
    exact (ihBody
      (fun es'' => evalC es'' preEs none inv ∧ evalV es'' preEs var < evalV es' preEs var ∧ 0 ≤ evalV es'' preEs var)
      Qr
      (fun es'' => evalC es'' preEs none inv ∧ evalV es'' preEs var < evalV es' preEs var ∧ 0 ≤ evalV es'' preEs var)
      Qn Qe preEs es').mpr (hbody es' hinv' hcond)

-- ===== genLiftContinue_wpW: intermediate lemma for SFor =====

/-- Structural lemma: genLiftContinue replaces shallow continue-raises with
    `inc; continue`.  The wpW of the lifted tree equals the wpW of the original
    tree with `wcC` replaced by "run inc then trigger wcC".
    Requires `hInc`: inc is wcN-only (fires only wcN regardless of other continuations). -/
theorem genLiftContinue_wpW (inc : WhyMLStmt)
    (hInc : ∀ (Q1 Q2 : WpConts) preEs es,
            (∀ e, Q1.wcN e ↔ Q2.wcN e) →
            (wpW inc Q1 preEs es ↔ wpW inc Q2 preEs es))
    (w : WhyMLStmt) (Q : WpConts) (preEs es : ExecState) :
    wpW (genLiftContinue inc w) Q preEs es ↔
    wpW w { wcN := Q.wcN, wcR := Q.wcR,
            wcC := fun es' => wpW inc
                    { wcN := Q.wcC, wcR := Q.wcR, wcC := Q.wcC, wcB := Q.wcB, wcE := Q.wcE }
                    preEs es',
            wcB := Q.wcB, wcE := Q.wcE }
        preEs es := by
  induction w generalizing Q preEs es with
  | wSkip      => simp only [genLiftContinue, wpW]
  | wAssign    => simp only [genLiftContinue, wpW]
  | wAugAssign => simp only [genLiftContinue, wpW]
  | wArraySet  => simp only [genLiftContinue, wpW]
  | wSeq w1 w2 ih1 ih2 =>
    simp only [genLiftContinue, wpW]
    rw [ih1 { wcN := fun es' => wpW (genLiftContinue inc w2) Q preEs es',
              wcR := Q.wcR, wcC := Q.wcC, wcB := Q.wcB, wcE := Q.wcE } preEs es]
    apply wpW_congr
    · intro es'; exact ih2 Q preEs es'
    · intro _; exact Iff.rfl
    · intro _; exact Iff.rfl
    · intro _; exact Iff.rfl
    · intro _ _; exact Iff.rfl
  | wIf _cond wThen wElse ih1 ih2 =>
    simp only [genLiftContinue, wpW]
    constructor
    · intro ⟨ht, hf⟩
      exact ⟨fun h => (ih1 Q preEs es).mp (ht h),
             fun h => (ih2 Q preEs es).mp (hf h)⟩
    · intro ⟨ht, hf⟩
      exact ⟨fun h => (ih1 Q preEs es).mpr (ht h),
             fun h => (ih2 Q preEs es).mpr (hf h)⟩
  | wWhile =>
    -- genLiftContinue is identity on wWhile; wpW wWhile does not use wcC
    simp only [genLiftContinue]; exact Iff.rfl
  | wRaise exc =>
    rcases exc with _ | _ | _ | n
    · simp only [genLiftContinue, wpW]   -- excReturn: both sides = Q.wcR es
    · simp only [genLiftContinue, wpW]   -- excBreak: both sides = Q.wcB es
    · simp only [genLiftContinue, wpW]   -- excContinue: both sides = wpW inc {wcN:=Q.wcC,...} (simp closes via eta)
    · simp only [genLiftContinue, wpW]   -- excNamed: both sides = Q.wcE n es
  | wTryCatch w1 exc w2 ih1 ih2 =>
    simp only [genLiftContinue, wpW]
    rw [ih1 { wcN := Q.wcN, wcR := Q.wcR, wcC := Q.wcC, wcB := Q.wcB,
               wcE := fun exc' es' =>
                 if exc' == exc then wpW (genLiftContinue inc w2) Q preEs es'
                 else Q.wcE exc' es' } preEs es]
    apply wpW_congr
    · intro _; exact Iff.rfl
    · intro _; exact Iff.rfl
    · -- wcC: inner exc continuation differs; hInc applies since both have wcN = Q.wcC
      intro es'
      apply hInc
      intro _; exact Iff.rfl
    · intro _; exact Iff.rfl
    · -- wcE: split on whether exc' matches the caught exception
      intro exc' es'
      constructor <;> intro h
      · cases hb : (exc' == exc) <;> simp only [hb, ite_true] at h ⊢
        · exact h
        · exact (ih2 Q preEs es').mp h
      · cases hb : (exc' == exc) <;> simp only [hb, ite_true] at h ⊢
        · exact h
        · exact (ih2 Q preEs es').mpr h
  | wGhostDecl   => simp only [genLiftContinue, wpW]
  | wGhostAssign => simp only [genLiftContinue, wpW]
  | wLabel       => simp only [genLiftContinue, wpW]
  | wAssert      => simp only [genLiftContinue, wpW]

-- ===== SFor =====

theorem wpGen_for (x arr : Ident) (inv var : ContractExpr) (body : Stmt) (aim : Bool)
    (Qn Qr Qc Qb : ExecState → Prop) (Qe : Ident → ExecState → Prop)
    (preEs es : ExecState)
    (ihBody : ∀ Qn' Qr' Qc' Qb' (Qe' : Ident → ExecState → Prop) preEs' es',
              wp body Qn' Qr' Qc' Qb' Qe' preEs' es' ↔
              wpW (gen body) (enc Qn' Qr' Qc' Qb' Qe') preEs' es') :
    wp (.for_ x arr inv var body aim) Qn Qr Qc Qb Qe preEs es ↔
    wpW (gen (.for_ x arr inv var body aim)) (enc Qn Qr Qc Qb Qe) preEs es := by
  simp only [wp, gen, enc, wpW]
  -- inc: the index-increment step (fires only wcN)
  have hInc : ∀ (Q1 Q2 : WpConts) (pe e1 : ExecState),
      (∀ ev, Q1.wcN ev ↔ Q2.wcN ev) →
      (wpW (.wAugAssign forIdx .add (.int 1)) Q1 pe e1 ↔
       wpW (.wAugAssign forIdx .add (.int 1)) Q2 pe e1) := by
    intro Q1 Q2 pe e1 h; simp only [wpW]; exact h _
  constructor
  -- → direction: wp (SFor ...) → wpW (gen (SFor ...))
  · rintro ⟨hinv, hbody, hexit⟩
    refine ⟨hinv, fun es' hinv' hguard => ?_, hexit⟩
    have hb := hbody es' hinv' hguard
    -- Local abbreviations (let-bound, transparent for definitional equality)
    let inc : WhyMLStmt := .wAugAssign forIdx .add (.int 1)
    let es1 := setReg es' (update es'.regState x
                  (evalExpr es'.regState (.subscript arr (.var forIdx))))
    let bdw : ExecState → Prop := fun es'' =>
      evalC es'' preEs none inv ∧
      evalV es'' preEs var < evalV es' preEs var ∧
      evalV es'' preEs var ≥ 0
    let bd : ExecState → Prop := fun es'' =>
      let curIdx := match lookup es''.regState forIdx with | some (.int n) => n | _ => 0
      bdw (setReg es'' (update es''.regState forIdx (.int (curIdx + 1))))
    -- Bridge hb: after simp, hb has the inline bodyDone form; bd is definitionally equal
    change (wp body bd Qr bd Qn Qe preEs es1) at hb
    -- Apply IH forward: wp body bd ... → wpW (gen body) (enc bd ...) ...
    rw [ihBody bd Qr bd Qn Qe preEs es1] at hb
    -- hb : wpW (gen body) (enc bd Qr bd Qn Qe) preEs es1
    -- Goal: wpW (genLiftContinue inc (gen body)) { wcN := bd, wcR := Qr, wcC := bdw, wcB := Qn, wcE := Qe } preEs es1
    change (wpW (genLiftContinue inc (gen body))
               { wcN := bd, wcR := Qr, wcC := bdw, wcB := Qn, wcE := Qe } preEs es1)
    -- Apply genLiftContinue_wpW (←): gen_lift ↔ gen body Q_mod where Q_mod.wcC ≡ bd
    -- The Q_mod.wcC = fun es'' => wpW inc { wcN := bdw, ... } preEs es'' = bd (definitionally)
    exact (genLiftContinue_wpW inc hInc (gen body)
             { wcN := bd, wcR := Qr, wcC := bdw, wcB := Qn, wcE := Qe } preEs es1).mpr hb
  -- ← direction: wpW (gen (SFor ...)) → wp (SFor ...)
  · rintro ⟨hinv, hbody, hexit⟩
    refine ⟨hinv, fun es' hinv' hguard => ?_, hexit⟩
    have hb := hbody es' hinv' hguard
    let inc : WhyMLStmt := .wAugAssign forIdx .add (.int 1)
    let es1 := setReg es' (update es'.regState x
                  (evalExpr es'.regState (.subscript arr (.var forIdx))))
    let bdw : ExecState → Prop := fun es'' =>
      evalC es'' preEs none inv ∧
      evalV es'' preEs var < evalV es' preEs var ∧
      evalV es'' preEs var ≥ 0
    let bd : ExecState → Prop := fun es'' =>
      let curIdx := match lookup es''.regState forIdx with | some (.int n) => n | _ => 0
      bdw (setReg es'' (update es''.regState forIdx (.int (curIdx + 1))))
    -- Bridge hb: after simp, hb has the expanded WhyML form
    change (wpW (genLiftContinue inc (gen body))
               { wcN := bd, wcR := Qr, wcC := bdw, wcB := Qn, wcE := Qe } preEs es1) at hb
    -- Apply genLiftContinue_wpW (→): gives wpW (gen body) Q_mod where Q_mod.wcC ≡ bd
    have hb2 := (genLiftContinue_wpW inc hInc (gen body)
                   { wcN := bd, wcR := Qr, wcC := bdw, wcB := Qn, wcE := Qe } preEs es1).mp hb
    -- Apply IH backward: wpW (gen body) (enc bd ...) → wp body bd ...
    -- hb2 has Q_mod.wcC ≡ bd definitionally, so exact closes via kernel conversion
    change (wp body bd Qr bd Qn Qe preEs es1)
    exact (ihBody bd Qr bd Qn Qe preEs es1).mpr hb2

-- ===== SCritical / SThreadEntry (transparent) =====

theorem wpGen_critical (mutex : Ident) (body : Stmt)
    (Qn Qr Qc Qb : ExecState → Prop) (Qe : Ident → ExecState → Prop)
    (preEs es : ExecState)
    (ihBody : ∀ Qn' Qr' Qc' Qb' (Qe' : Ident → ExecState → Prop) preEs' es',
              wp body Qn' Qr' Qc' Qb' Qe' preEs' es' ↔
              wpW (gen body) (enc Qn' Qr' Qc' Qb' Qe') preEs' es') :
    wp (.critical mutex body) Qn Qr Qc Qb Qe preEs es ↔
    wpW (gen (.critical mutex body)) (enc Qn Qr Qc Qb Qe) preEs es := by
  simp [wp, gen]
  exact ihBody Qn Qr Qc Qb Qe preEs es

theorem wpGen_threadEntry (body : Stmt)
    (Qn Qr Qc Qb : ExecState → Prop) (Qe : Ident → ExecState → Prop)
    (preEs es : ExecState)
    (ihBody : ∀ Qn' Qr' Qc' Qb' (Qe' : Ident → ExecState → Prop) preEs' es',
              wp body Qn' Qr' Qc' Qb' Qe' preEs' es' ↔
              wpW (gen body) (enc Qn' Qr' Qc' Qb' Qe') preEs' es') :
    wp (.threadEntry body) Qn Qr Qc Qb Qe preEs es ↔
    wpW (gen (.threadEntry body)) (enc Qn Qr Qc Qb Qe) preEs es := by
  simp [wp, gen]
  exact ihBody Qn Qr Qc Qb Qe preEs es
