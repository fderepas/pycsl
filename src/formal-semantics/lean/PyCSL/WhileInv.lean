/-
  WhileInv.lean — While loop invariant preservation lemma
  Port of Phase5a_WhileInv.v

  Includes while_not_continued (while loops never produce OContinued)
  and while_inv_preserved (well-founded induction on variant).
-/
import PyCSL.AST
import PyCSL.State
import PyCSL.SOS
import PyCSL.WP

theorem while_not_continued
    {st : State} {inv var : ContractExpr} {cond : Expr} {body : Stmt}
    {out : Outcome}
    (h : Exec st (.while_ inv var cond body) out) :
    ∀ st', out ≠ .continued st' := by
  sorry -- Helper lemma; while loops never produce OContinued

theorem while_inv_preserved
    (cond : Expr) (body : Stmt) (inv var : ContractExpr)
    (Qn Qr : State → Prop) (preSt st : State)
    (hBodySound : ∀ st0 out0 Qn0 Qr0 Qc0,
       Exec st0 body out0 →
       wp body Qn0 Qr0 Qc0 preSt st0 →
       match out0 with
       | .normal st' => Qn0 st'
       | .returned st' _ => Qr0 st'
       | .continued st' => Qc0 st')
    (hInv : evalContract st preSt none inv)
    (hNonNeg : evalVariant st preSt var ≥ 0)
    (hPres : ∀ st', evalContract st' preSt none inv →
                    evalBool st' cond = true →
                    wp body (fun st'' =>
                      evalContract st'' preSt none inv ∧
                      evalVariant st'' preSt var < evalVariant st' preSt var ∧
                      evalVariant st'' preSt var ≥ 0)
                      Qr
                      (fun st'' =>
                      evalContract st'' preSt none inv ∧
                      evalVariant st'' preSt var < evalVariant st' preSt var ∧
                      evalVariant st'' preSt var ≥ 0)
                      preSt st')
    (hPost : ∀ st', evalContract st' preSt none inv →
                    evalBool st' cond = false → Qn st')
    (out : Outcome)
    (hExec : Exec st (.while_ inv var cond body) out) :
    match out with
    | .normal st' => Qn st'
    | .returned st' _ => Qr st'
    | .continued _ => True := by
  sorry -- Well-founded induction on evalVariant; mirrors Rocq proof
