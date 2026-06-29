/-
  SoundnessVerified.lean — Verified Soundness via WhyML Correspondence

  Phase 6A+6B (monday-02.md) — TCB reduction for why3ImplementsWpW:

  OLD (pre-6A):
    axiom why3ImplementsWpW : Why3Certificate ws Q → wpW ws Q preEs es
    (trusted both Why3's VCG algorithm AND Why3's provers)

  NEW (Phase 6C, current):
    axiom module6EncodesMlw (VcgEmission.lean) : Why3Certificate ws Q → vcProp ws Q preEs es
      [axiom — Phase 6C-α/β proof obligation; replaces the sorry in vcgBridge]
    def vcgBridge (VcgEmission.lean) : Why3Certificate ws Q → vcProp ws Q preEs es
      [proved — no sorry; proved from module6EncodesMlw]
    theorem vcgSound (Why3Vcg.lean) : vcProp ws Q preEs es ↔ wpW ws Q preEs es
      [proved — no axioms beyond propext/Classical.choice/Quot.sound]
    theorem why3ImplementsWpW_derived := vcgSound.mp ∘ vcgBridge
      [depends on module6EncodesMlw, but that axiom is named + documented]

  `#print axioms why3ImplementsWpW_derived` lists `module6EncodesMlw` explicitly
  (not sorryAx) — a named axiom documenting exactly what is trusted.

  The old why3ImplementsWpW axiom is kept for backward compatibility until
  all callers migrate to why3ImplementsWpW_derived.

  Verified soundness path (unchanged):
  1. why3ImplementsWpW_derived ← vcgBridge (sorry) + vcgSound (proved)
  2. wpW (gen s) (enc ...) preEs es
  3. wpGenCorrect (CorrMain) → wp s Qn Qr Qc Qb Qe preEs es
  4. pycsl_soundness (Soundness) → outcomePost Qn Qr Qc Qb Qe out
-/
import PyCSL.AST
import PyCSL.State
import PyCSL.SOS
import PyCSL.WP
import PyCSL.Soundness
import PyCSL.WhyML
import PyCSL.WPW
import PyCSL.StmtGen
import PyCSL.CorrMain
import PyCSL.Why3Trust   -- provides Why3Certificate, SmtCertificate
import PyCSL.Why3Vcg     -- provides vcProp, vcgSound (Phase 6A)
import PyCSL.VcgEmission -- provides module6EncodesMlw, vcgBridge (Phase 6C)

-- ===== Phase 6C: derived theorem using vcgBridge (proved) + vcgSound (proved) =====

-- why3ImplementsWpW_derived: wpW follows from vcgBridge + vcgSound.
-- The trust chain is now:
--   Why3Certificate  →(vcgBridge→module6EncodesMlw, axiom)→  vcProp
--                    →(vcgSound.mp, proved)→  wpW
-- The axiom module6EncodesMlw is named and documented (Phase 6C proof obligation).
-- vcgBridge itself has NO sorry — it is proved from the axiom.
theorem why3ImplementsWpW_derived
    (ws : WhyMLStmt) (Q : WpConts) (preEs es : ExecState) :
    Why3Certificate ws Q → wpW ws Q preEs es :=
  fun hcert => (vcgSound ws Q preEs es).mp (vcgBridge ws Q preEs es hcert)

-- ===== Corollary: wpW → wp via correspondence =====

-- wpW_implies_wp: bridges wpW back to the PyCSL WP using wpGenCorrect.
theorem wpW_implies_wp
    (s : Stmt) (hem : isEmittable s) (Qn Qr Qc Qb : ExecState → Prop) (Qe : Ident → ExecState → Prop)
    (preEs es : ExecState)
    (h : wpW (gen s) (enc Qn Qr Qc Qb Qe) preEs es) :
    wp s Qn Qr Qc Qb Qe preEs es :=
  (wpGenCorrect s hem Qn Qr Qc Qb Qe preEs es).mpr h

-- ===== Verified soundness theorem =====

-- pycslSoundnessVerified: end-to-end soundness via the WhyML correspondence path.
-- Takes wpW (gen s) (enc ...) as the hypothesis (produced by why3ImplementsWpW_derived
-- from a Why3 VCG certificate + vcgBridge), chains through wpGenCorrect and
-- pycsl_soundness.
theorem pycslSoundnessVerified
    (s : Stmt) (hem : isEmittable s)
    (Qn Qr Qc Qb : ExecState → Prop) (Qe : Ident → ExecState → Prop)
    (preEs es : ExecState) (out : Outcome)
    (hExec : Exec es s out)
    (hWpW : wpW (gen s) (enc Qn Qr Qc Qb Qe) preEs es) :
    outcomePost Qn Qr Qc Qb Qe out :=
  pycsl_soundness es s out Qn Qr Qc Qb Qe preEs hExec
    (wpW_implies_wp s hem Qn Qr Qc Qb Qe preEs es hWpW)
