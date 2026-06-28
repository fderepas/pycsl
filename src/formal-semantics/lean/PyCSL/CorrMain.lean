/-
  CorrMain.lean — Full WP Correspondence Theorem
  Combines CorrSimple, CorrLoops, CorrExc into the master theorem by
  structural induction on s:

    theorem wpGenCorrect :
      ∀ (s : Stmt) (Qn Qr Qc Qb : ExecState → Prop)
        (Qe : Ident → ExecState → Prop) (preEs es : ExecState),
      wp s Qn Qr Qc Qb Qe preEs es ↔
      wpW (gen s) (enc Qn Qr Qc Qb Qe) preEs es.

  Simple cases dispatch to CorrSimple lemmas.
  Inductive cases use CorrLoops and CorrExc lemmas with the IH.
-/
import PyCSL.AST
import PyCSL.State
import PyCSL.WP
import PyCSL.WhyML
import PyCSL.WPW
import PyCSL.StmtGen
import PyCSL.CorrSimple
import PyCSL.CorrLoops
import PyCSL.CorrExc

-- ===== Master WP correspondence theorem =====

-- Phase 8 gap: `induction s` does not work for mutually inductive
-- `Stmt` (Lean requires `mutual`/`rec` for mutual inductives, and
-- the existing proof structure doesn't use that). The theorem is
-- admitted as a whole — this is a regression from the pre-Phase-8
-- state where `Stmt` was a plain inductive. The fix would be to
-- rewrite `wpGenCorrect` as a mutual `partial def`/theorem using
-- `mutual ... end` with companion lemmas for `Expr.lambda`. Deferred.
theorem wpGenCorrect (s : Stmt) :
    ∀ (Qn Qr Qc Qb : ExecState → Prop) (Qe : Ident → ExecState → Prop)
      (preEs es : ExecState),
    wp s Qn Qr Qc Qb Qe preEs es ↔
    wpW (gen s) (enc Qn Qr Qc Qb Qe) preEs es := by
  sorry

-- ===== Corollary: wpW (gen s) implies wp s =====

theorem wpW_gen_implies_wp
    (s : Stmt) (Qn Qr Qc Qb : ExecState → Prop) (Qe : Ident → ExecState → Prop)
    (preEs es : ExecState)
    (h : wpW (gen s) (enc Qn Qr Qc Qb Qe) preEs es) :
    wp s Qn Qr Qc Qb Qe preEs es :=
  (wpGenCorrect s Qn Qr Qc Qb Qe preEs es).mpr h
