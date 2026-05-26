/-
  WP.lean — Weakest Precondition Calculus
  Mirror of Phase4_WP.v (all phases)

  Five continuations:
    Qn : ExecState → Prop  — normal completion
    Qr : ExecState → Prop  — return
    Qc : ExecState → Prop  — continue
    Qb : ExecState → Prop  — break  (Phase 2)
    Qe : Ident → ExecState → Prop — exception (Phase 5)

  Critical invariant: SWhile body's break continuation = Qn
  (SBreak inside SWhile exits the loop normally → ONormal).
-/
import PyCSL.AST
import PyCSL.State
import PyCSL.DesugarDef

def wp : Stmt
       → (Qn Qr Qc Qb : ExecState → Prop)
       → (Qe : Ident → ExecState → Prop)
       → (preEs es : ExecState)
       → Prop
  | .skip, Qn, _, _, _, _, _, es => Qn es

  | .assign x e, Qn, _, _, _, _, _, es =>
    Qn (setReg es (update es.regState x (evalExpr es.regState e)))

  | .augAssign x op e, Qn, _, _, _, _, _, es =>
    let cur := match lookup es.regState x with | some (.int n) => n | _ => 0
    let nv  := evalBinopZ op cur
                 (match evalExpr es.regState e with | .int n => n | _ => 0)
    Qn (setReg es (update es.regState x (.int nv)))

  | .arraySet arr i v, Qn, _, _, _, _, _, es =>
    let idx := match evalExpr es.regState i with | .int n => n | _ => 0
    let nv  := match evalExpr es.regState v with | .int n => n | _ => 0
    Qn (setReg es (arrayUpdate es.regState arr idx nv))

  | .seq s1 s2, Qn, Qr, Qc, Qb, Qe, preEs, es =>
    wp s1 (fun es' => wp s2 Qn Qr Qc Qb Qe preEs es') Qr Qc Qb Qe preEs es

  | .ite cond s1 s2, Qn, Qr, Qc, Qb, Qe, preEs, es =>
    (evalBool es.regState cond = true  → wp s1 Qn Qr Qc Qb Qe preEs es) ∧
    (evalBool es.regState cond = false → wp s2 Qn Qr Qc Qb Qe preEs es)

  | .while_ inv var cond body, Qn, Qr, _, _, Qe, preEs, es =>
    evalC es preEs none inv ∧
    (∀ es', evalC es' preEs none inv →
            evalBool es'.regState cond = true →
            let bodyDone es'' :=
              evalC es'' preEs none inv ∧
              evalV es'' preEs var < evalV es' preEs var ∧
              evalV es'' preEs var ≥ 0
            -- break exits loop normally → Qn
            wp body bodyDone Qr bodyDone Qn Qe preEs es') ∧
    (∀ es', evalC es' preEs none inv →
            evalBool es'.regState cond = false → Qn es')

  | .for_ x arr inv var body, Qn, Qr, _, _, Qe, preEs, es =>
    let es0 := setReg es (update es.regState forIdx (.int 0))
    -- guard: len(arr) - forIdx ≠ 0 (matches the desugared while_ condition exactly)
    let guard := Expr.binop .sub (.len arr) (.var forIdx)
    evalC es0 preEs none inv ∧
    (∀ es', evalC es' preEs none inv →
            evalBool es'.regState guard = true →
            let es1 := setReg es'
                         (update es'.regState x
                           (evalExpr es'.regState (.subscript arr (.var forIdx))))
            let bodyDone es'' :=
              let curIdx := match lookup es''.regState forIdx with
                            | some (.int n) => n | _ => 0
              let es3 := setReg es'' (update es''.regState forIdx (.int (curIdx + 1)))
              evalC es3 preEs none inv ∧
              evalV es3 preEs var < evalV es' preEs var ∧
              evalV es3 preEs var ≥ 0
            wp body bodyDone Qr bodyDone Qn Qe preEs es1) ∧
    (∀ es', evalC es' preEs none inv →
            evalBool es'.regState guard = false →
            Qn es')

  | .ret e, _, Qr, _, _, _, _, es =>
    Qr (setReg es (update es.regState "\\result" (evalExpr es.regState e)))

  | .continue_, _, _, Qc, _, _, _, es => Qc es

  | .break_, _, _, _, Qb, _, _, es => Qb es

  | .assert_ cond msg, Qn, _, _, _, _, preEs, es =>
    evalC es preEs none cond ∧ Qn es

  | .tupleUnpack _ _, Qn, _, _, _, _, _, es => Qn es

  | .ghostDecl x t e, Qn, _, _, _, _, _, es =>
    Qn (setGhost es (ghostUpdate es.ghostSt x (evalGhostVal t es e)))

  | .ghostAssign x _ op e, Qn, _, _, _, _, _, es =>
    let cur := ghostLookup es.ghostSt x
    let nv  := applyGhostAug op cur es e
    Qn (setGhost es (ghostUpdate es.ghostSt x nv))

  | .label_ L, Qn, _, _, _, _, _, es =>
    Qn (setLabels es ((L, es.ghostSt) :: es.labelSnaps))

  | .raise_ exc, _, _, _, _, Qe, _, es => Qe exc es

  | .tryCatch s1 exc handler, Qn, Qr, Qc, Qb, Qe, preEs, es =>
    wp s1 Qn Qr Qc Qb
       (fun exc' es' =>
          if exc' == exc
          then wp handler Qn Qr Qc Qb Qe preEs es'
          else Qe exc' es')
       preEs es

  | .fieldAssign _ _ _, Qn, _, _, _, _, _, es => Qn es
  | .fieldAugAssign _ _ _ _, Qn, _, _, _, _, _, es => Qn es

  | .critical _ body, Qn, Qr, Qc, Qb, Qe, preEs, es =>
    wp body Qn Qr Qc Qb Qe preEs es

  | .threadEntry body, Qn, Qr, Qc, Qb, Qe, preEs, es =>
    wp body Qn Qr Qc Qb Qe preEs es
