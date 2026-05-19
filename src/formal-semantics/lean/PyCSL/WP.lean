/-
  WP.lean — Weakest Precondition Calculus
  Port of Phase4_WP.v

  Uses three continuations: Qn (normal), Qr (return), Qc (continue)
  to correctly handle early termination in sequences and continue in loops.

  The SWhile body_done uses LOCAL variant bounds (< at iter state st',
  not initial state st) making the WP self-similar across iterations.
-/
import PyCSL.AST
import PyCSL.State
import PyCSL.DesugarDef

def wp : Stmt → (Qn Qr Qc : State → Prop) → (preSt st : State) → Prop
  | .skip, Qn, _, _, _, st => Qn st

  | .assign x e, Qn, _, _, _, st =>
    Qn (update st x (evalExpr st e))

  | .augAssign x op e, Qn, _, _, _, st =>
    let cur := match lookup st x with | some (.int n) => n | _ => 0
    let nv := evalBinopZ op cur (match evalExpr st e with | .int n => n | _ => 0)
    Qn (update st x (.int nv))

  | .arraySet arr i v, Qn, _, _, _, st =>
    let idx := match evalExpr st i with | .int n => n | _ => 0
    let nv := match evalExpr st v with | .int n => n | _ => 0
    Qn (arrayUpdate st arr idx nv)

  | .seq s1 s2, Qn, Qr, Qc, preSt, st =>
    wp s1 (fun st' => wp s2 Qn Qr Qc preSt st') Qr Qc preSt st

  | .ite cond s1 s2, Qn, Qr, Qc, preSt, st =>
    (evalBool st cond = true  → wp s1 Qn Qr Qc preSt st) ∧
    (evalBool st cond = false → wp s2 Qn Qr Qc preSt st)

  | .while_ inv var cond body, Qn, Qr, _, preSt, st =>
    evalContract st preSt none inv ∧
    (∀ st', evalContract st' preSt none inv →
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
              preSt st') ∧
    (∀ st', evalContract st' preSt none inv →
            evalBool st' cond = false → Qn st')

  | .for_ x arr inv var body, Qn, Qr, _, preSt, st =>
    let st0 := update st forIdx (.int 0)
    evalContract st0 preSt none inv ∧
    (∀ st',
      evalContract st' preSt none inv →
      evalZ st' preSt none (.var forIdx) < evalZ st' preSt none (.length arr) →
      let st1 := update st' x (evalExpr st' (.subscript arr (.var forIdx)))
      wp body (fun st2 =>
        let curIdx := match lookup st2 forIdx with | some (.int n) => n | _ => 0
        let st3 := update st2 forIdx (.int (curIdx + 1))
        evalContract st3 preSt none inv ∧
        evalVariant st3 preSt var < evalVariant st' preSt var ∧
        evalVariant st3 preSt var ≥ 0)
        Qr
        (fun st2 =>
        let curIdx := match lookup st2 forIdx with | some (.int n) => n | _ => 0
        let st3 := update st2 forIdx (.int (curIdx + 1))
        evalContract st3 preSt none inv ∧
        evalVariant st3 preSt var < evalVariant st' preSt var ∧
        evalVariant st3 preSt var ≥ 0)
        preSt st1) ∧
    (∀ st',
      evalContract st' preSt none inv →
      evalZ st' preSt none (.var forIdx) ≥ evalZ st' preSt none (.length arr) →
      Qn st')

  | .ret e, _, Qr, _, _, st =>
    Qr (update st "\result" (evalExpr st e))

  | .continue_, _, _, Qc, _, st =>
    Qc st
