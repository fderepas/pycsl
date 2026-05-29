/-
  VcgEmission.lean — Phase 6C / Stage B-3: vcgBridge proved from why3ValidatesEmitted

  Architecture (after Stage B-3, monday-05.md):

    Phase 6A (Why3Vcg.lean):
      theorem vcgSound : vcProp ws Q preEs es ↔ wpW ws Q preEs es
      [proved — no domain axioms]

    Phase 6C-β (monday-05.md):
      theorem vcFormulaOf_sound (VcgSemBridge.lean — proved, no domain axioms)
      axiom why3ValidatesEmitted (VcgSemBridge.lean — prover-only trust)
      theorem why3ValidatesVcFormula (VcgSemBridge.lean — PROVED from B-3)
      def vcgBridge := vcFormulaOf_sound + why3ValidatesVcFormula
        [NO sorry — proved]

    Stage B-3 (monday-05.md):
      theorem emitStmt_correct (EmitVcList.lean — proved by rfl)
        [emission fidelity: emitVcList = vcFormulaOf_list]
      axiom why3ValidatesEmitted (VcgSemBridge.lean — prover-only, narrower)
      theorem why3ValidatesVcFormula — PROVED from why3ValidatesEmitted + emitStmt_correct

  TCB after B-3:
    `#print axioms vcgBridge`
      → [why3ValidatesEmitted, propext, Classical.choice, Quot.sound]
    why3ValidatesEmitted trusts ONLY prover soundness for specific emitVcList formulas.
    Emission fidelity is captured in emitStmt_correct (proved, no axioms beyond propext).

  References:
    Cohen & Johnson-Freyd (POPL 2024) — formula_rep / satisfies / valid
    Herms, Marche, Monate (CAV 2012) — wWhile proof template
-/
import PyCSL.WhyML
import PyCSL.WPW
import PyCSL.Why3Vcg
import PyCSL.Why3Trust
import PyCSL.VcgSemBridge   -- Phase 6C-β: why3ValidatesVcFormula + vcFormulaOf_sound

-- ===== vcgBridge: Stage B-3 — proved via why3ValidatesEmitted + vcFormulaOf_sound =====

/-- vcgBridge: certified bridge from a Why3Certificate to vcProp.

    Stage B-3 trust chain:
      Why3Certificate ws Q
        →(why3ValidatesVcFormula, THEOREM after B-3)→ evalVcFormula (vcFormulaOf..i) es preEs
        →(vcFormulaOf_sound, proved)→                 vcProp ws Q preEs es
        →(vcgSound.mp, proved)→                       wpW ws Q preEs es
        →(wpGenCorrect.mpr, proved)→                  wp s Qn ... preEs es
        →(pycsl_soundness, proved)→                   outcomePost Qn ... out

    why3ValidatesVcFormula is now a PROVED THEOREM (not an Axiom), derived from:
      - why3ValidatesEmitted (Axiom — prover soundness for f in emitVcList)
      - emitStmt_correct (Theorem, proved by rfl — emission fidelity)
      - vcFormulaOf_mem_emitVcList (Theorem, proved — index to list membership)

    `#print axioms vcgBridge`
      → [why3ValidatesEmitted, propext, Classical.choice, Quot.sound]
      (why3ValidatesVcFormula no longer appears as an Axiom)

    Why `def` (not `opaque`): transparency makes why3ValidatesEmitted visible
    in `#print axioms`, so the axiom name appears explicitly in the audit. -/
def vcgBridge
    (ws : WhyMLStmt) (Q : WpConts) (preEs es : ExecState)
    (cert : Why3Certificate ws Q) : vcProp ws Q preEs es :=
  vcFormulaOf_sound ws Q preEs es fun i f hf =>
    why3ValidatesVcFormula ws Q preEs es i f cert hf
