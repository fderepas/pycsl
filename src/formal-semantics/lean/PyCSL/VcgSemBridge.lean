/-
  VcgSemBridge.lean — Phase 6C-β: VcFormula soundness bridge

  Connects the VcFormula shallow embedding (VcFormula.lean) to vcProp
  (Why3Vcg.lean), enabling vcgBridge to be proved from the narrower
  axiom why3ValidatesVcFormula instead of module6EncodesMlw.

  Key components:
    why3ValidatesVcFormula — narrower axiom (per-VC trust, not whole-vcProp)
    vcFormulaOf_sound       — proved theorem: all VcFormulas hold → vcProp holds

  Architecture after Phase 6C-β:

    Why3Certificate ws Q
          │
          │ (why3ValidatesVcFormula, axiom — per-VC claim)
          ▼
    evalVcFormula (vcFormulaOf ws Q preEs es i) es preEs   for each i
          │
          │ (vcFormulaOf_sound, PROVED — structural induction on ws)
          ▼
    vcProp ws Q preEs es
          │
          │ (vcgSound.mp, PROVED in Phase 6A)
          ▼
    wpW ws Q preEs es

  Comparison with module6EncodesMlw:
    OLD: module6EncodesMlw (VcgEmission.lean)
           Why3Certificate ws Q → vcProp ws Q preEs es
         [Trusts both emission fidelity AND Why3 prover soundness, as one claim]

    NEW: why3ValidatesVcFormula
           Why3Certificate ws Q →
           vcFormulaOf ws Q preEs es i = some f →
           evalVcFormula f es preEs
         [Trusts only Why3's prover for a specific named formula at a specific
          VC index. Module6 emission fidelity is expressed separately as the
          axiom "vcFormulaOf is the correct spec" (Stage B-1 in monday-05.md).]

  References:
    monday-05.md — Root cause A (formula_rep is Rocq) and Stage B-1 (vcFormulaOf)
    monday-03.md — Phase 6C architecture (Sub-lemmas α and β)
    Cohen & JF (POPL 2024) — formula_rep (Rocq side in Phase6m_VcgSemBridge.v)
-/
import PyCSL.VcFormula
import PyCSL.Why3Trust
import PyCSL.EmitVcList

-- ===== why3ValidatesEmitted: Q3 Sub-β port — PROVED Lemma (was Axiom) =====

/-- Q3 Sub-β port to Lean (2026-05-29): was Axiom; now PROVED Lemma.

    After the cert-as-witness refactor in `Why3Trust.lean`,
    `Why3Certificate ws Q` IS the witness function. This theorem
    becomes a trivial composition: extract the index from
    `f ∈ emitVcList` via `emitVcList_mem_imp_vcFormulaOf`, then
    apply the cert at that index.

    Rocq analogue: `why3_validates_emitted` in
    `Phase6m_VcgSemBridge.v` (also PROVED post-Sub-β).

    Trust state: the prior axiom is REPLACED by `Why3CertConstruct`
    (in `Why3Trust.lean`), which sits at the cert construction site
    rather than the projection site. -/
theorem why3ValidatesEmitted
    (ws : WhyMLStmt) (Q : WpConts) (preEs es : ExecState) (f : VcFormula) :
    Why3Certificate ws Q →
    f ∈ emitVcList ws Q preEs es →
    evalVcFormula f es preEs := by
  intro cert hMem
  obtain ⟨i, hi⟩ := emitVcList_mem_imp_vcFormulaOf hMem
  exact cert.witness preEs es i f hi

-- ===== why3ValidatesVcFormula: Stage B-3 — upgraded from Axiom to Theorem =====

/-- why3ValidatesVcFormula: PROVED THEOREM after Stage B-3 (was Axiom before B-3).

    Proof chain:
      vcFormulaOf ws Q preEs es i = some f
        → f ∈ emitVcList ws Q preEs es   (vcFormulaOf_mem_emitVcList, EmitVcList.lean)
        → evalVcFormula f es preEs        (why3ValidatesEmitted, axiom above)

    The vcFormulaOf_mem_emitVcList step uses:
      index bound (vcFormulaOf_index_lt) → range membership → filterMap membership
        → emitVcList membership via emitStmt_correct (all proved by rfl).

    TCB after B-3: why3ValidatesEmitted is the sole prover-trust axiom.
    Emission fidelity is captured in emitStmt_correct (proved, no axioms beyond propext).

    Rocq analogue: why3_validates_vc_formula in Phase6m_VcgSemBridge.v
    (upgraded from Axiom to Lemma by the same B-3 construction). -/
theorem why3ValidatesVcFormula
    (ws : WhyMLStmt) (Q : WpConts) (preEs es : ExecState)
    (i : Nat) (f : VcFormula) :
    Why3Certificate ws Q →
    vcFormulaOf ws Q preEs es i = some f →
    evalVcFormula f es preEs :=
  fun cert hf =>
    why3ValidatesEmitted ws Q preEs es f cert (vcFormulaOf_mem_emitVcList hf)

-- ===== vcFormulaOf_sound: assembles all VcFormulas into vcProp =====

/-- vcFormulaOf_sound: if every VcFormula for (ws, Q, preEs, es) holds,
    then vcProp ws Q preEs es holds.

    Proof strategy: case analysis on ws.
    For each constructor, the relevant VcFormulas (via hAllVcs) are exactly
    the conjuncts of vcProp, so the proof is trivial assembly.

    Specifically:
    - Simple cases (wSkip, wAssign, wAugAssign, wArraySet, wSeq, wRaise,
      wTryCatch, wGhostDecl, wGhostAssign, wLabel):
        vcFormulaOf ... 0 = some (.prop P), so hAllVcs 0 _ rfl : P, and
        vcProp ... = P (after definitional unfolding).
    - wIf: hAllVcs 0 and 1 give the two implications; vcProp is their conjunction.
    - wAssert: hAllVcs 0 gives evalC (via .contract), hAllVcs 1 gives Q.wcN es.
    - wWhile: hAllVcs 0 gives evalC (VC1), hAllVcs 1 gives the body VC (VC2),
      hAllVcs 2 gives the exit case (VC3); vcProp is their conjunction.

    No axioms beyond propext (needed by evalVcFormula via Prop). -/
theorem vcFormulaOf_sound
    (ws : WhyMLStmt) (Q : WpConts) (preEs es : ExecState)
    (hAllVcs : ∀ n f, vcFormulaOf ws Q preEs es n = some f → evalVcFormula f es preEs) :
    vcProp ws Q preEs es := by
  cases ws with

  -- ===== Simple cases: one VC = the entire vcProp conjunct as .prop =====

  | wSkip =>
    -- vcFormulaOf wSkip Q preEs es 0 = some (.prop (Q.wcN es))
    -- evalVcFormula (.prop (Q.wcN es)) es preEs = Q.wcN es = vcProp wSkip Q preEs es
    exact hAllVcs 0 _ rfl

  | wAssign x e =>
    exact hAllVcs 0 _ rfl

  | wAugAssign x op e =>
    exact hAllVcs 0 _ rfl

  | wArraySet arr i v =>
    exact hAllVcs 0 _ rfl

  | wSeq w1 w2 =>
    -- vcFormulaOf (wSeq w1 w2) Q preEs es 0 = some (.prop (vcProp w1 {wcN := vcProp w2 ...} preEs es))
    -- which is definitionally equal to vcProp (wSeq w1 w2) Q preEs es
    exact hAllVcs 0 _ rfl

  -- ===== wIf: two VCs = two implications =====

  | wIf cond w1 w2 =>
    -- vcProp (wIf cond w1 w2) Q preEs es = (cond=true → vcProp w1 ...) ∧ (cond=false → vcProp w2 ...)
    exact ⟨hAllVcs 0 _ rfl, hAllVcs 1 _ rfl⟩

  -- ===== wWhile: three VCs = VC1 ∧ VC2 ∧ VC3 =====

  | wWhile invs vars cond body =>
    -- VC1: evalC es preEs none (cConj invs)  (from .contract (cConj invs))
    have h0 := hAllVcs 0 (.contract (cConj invs)) rfl
    -- VC2: body preservation (from .prop (∀ es', ...))
    have h1 := hAllVcs 1 _ rfl
    -- VC3: exit case (from .prop (∀ es', ...))
    have h2 := hAllVcs 2 _ rfl
    -- Assemble the three-conjunct vcProp wWhile
    exact ⟨h0, h1, h2⟩

  -- ===== wRaise: one VC per exception constructor =====

  | wRaise exc =>
    cases exc with
    | excReturn   => exact hAllVcs 0 _ rfl
    | excBreak    => exact hAllVcs 0 _ rfl
    | excContinue => exact hAllVcs 0 _ rfl
    | excNamed nm => exact hAllVcs 0 _ rfl

  -- ===== wTryCatch: one VC = body vcProp with exception threading =====

  | wTryCatch body exc handler =>
    exact hAllVcs 0 _ rfl

  -- ===== Ghost and label cases: one VC each =====

  | wGhostDecl x t e =>
    exact hAllVcs 0 _ rfl

  | wGhostAssign x t op e =>
    exact hAllVcs 0 _ rfl

  | wLabel L =>
    exact hAllVcs 0 _ rfl

  -- ===== wAssert: two VCs = condition truth ∧ Q.wcN es =====

  | wAssert cond msg =>
    -- VC0: evalC es preEs none cond  (from .contract cond)
    -- VC1: Q.wcN es                  (from .prop (Q.wcN es))
    exact ⟨hAllVcs 0 (.contract cond) rfl, hAllVcs 1 _ rfl⟩
