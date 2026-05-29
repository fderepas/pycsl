/-
  CorrExc.lean — WP Correspondence for Exception Handling
  Proves the correspondence for STryCatch.
  gen (.tryCatch s exc handler) = .wTryCatch (gen s) exc (gen handler).
  Both wp and wpW override the exception continuation to dispatch on the
  exception name.  Full proof needs IHs from CorrMain.
-/
import PyCSL.AST
import PyCSL.State
import PyCSL.WP
import PyCSL.WhyML
import PyCSL.WPW
import PyCSL.StmtGen
import PyCSL.CorrSimple

theorem wpGen_tryCatch
    (s handler : Stmt) (exc : Ident)
    (Qn Qr Qc Qb : ExecState → Prop) (Qe : Ident → ExecState → Prop)
    (preEs es : ExecState)
    -- IH for body
    (ihs : ∀ Qn' Qr' Qc' Qb' (Qe' : Ident → ExecState → Prop) preEs' es',
           wp s Qn' Qr' Qc' Qb' Qe' preEs' es' ↔
           wpW (gen s) (enc Qn' Qr' Qc' Qb' Qe') preEs' es')
    -- IH for handler
    (ihh : ∀ Qn' Qr' Qc' Qb' (Qe' : Ident → ExecState → Prop) preEs' es',
           wp handler Qn' Qr' Qc' Qb' Qe' preEs' es' ↔
           wpW (gen handler) (enc Qn' Qr' Qc' Qb' Qe') preEs' es') :
    wp (.tryCatch s exc handler) Qn Qr Qc Qb Qe preEs es ↔
    wpW (gen (.tryCatch s exc handler)) (enc Qn Qr Qc Qb Qe) preEs es := by
  -- Both sides: apply body IH with modified Qe that dispatches on exc.
  -- LHS Qe: fun exc' es' => if exc' == exc then wp handler Qn Qr Qc Qb Qe preEs es' else Qe exc' es'
  -- RHS Qe: fun exc' es' => if exc' == exc then wpW (gen handler) (enc ..) preEs es' else Qe exc' es'
  simp only [wp, gen, wpW, enc]
  rw [ihs Qn Qr Qc Qb
    (fun exc' es' => if exc' == exc then wp handler Qn Qr Qc Qb Qe preEs es' else Qe exc' es')
    preEs es]
  -- Now apply wpW_congr to convert the modified Qe
  apply wpW_congr (gen s) _ _ preEs es
  · intro _; exact Iff.rfl    -- wcN
  · intro _; exact Iff.rfl    -- wcR
  · intro _; exact Iff.rfl    -- wcC
  · intro _; exact Iff.rfl    -- wcB
  · -- wcE: for each exc', es':
    --   (if exc'==exc then wp handler ... else Qe exc' es')
    -- ↔ (if exc'==exc then wpW (gen handler) (enc ...) ... else Qe exc' es')
    intro exc' es'
    -- enc must be in the simp set so the field projection on h/goal reduces
    constructor <;> intro h
    · -- mp direction
      cases hb : (exc' == exc) <;> simp only [hb, ite_true, enc] at h ⊢
      · exact h
      · exact (ihh Qn Qr Qc Qb Qe preEs es').mp h
    · -- mpr direction
      cases hb : (exc' == exc) <;> simp only [hb, ite_true, enc] at h ⊢
      · exact h
      · exact (ihh Qn Qr Qc Qb Qe preEs es').mpr h
