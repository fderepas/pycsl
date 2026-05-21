/-
  SOS.lean — Structural Operational Semantics
  Port of Phase3_SOS.v

  Exec is an inductive Prop with 14 constructors.
  ExecReturn binds "\result" in the state to match the WP.
  Uses 3-continuation model: Normal, Returned, Continued.
-/
import PyCSL.AST
import PyCSL.State
import PyCSL.DesugarDef

inductive Outcome where
  | normal    (st : State)
  | returned  (st : State) (v : Val)
  | continued (st : State)

inductive Exec : State → Stmt → Outcome → Prop where
  | execSkip (st : State) :
    Exec st .skip (.normal st)

  | execAssign (st : State) (x : Ident) (e : Expr) :
    Exec st (.assign x e) (.normal (update st x (evalExpr st e)))

  | execAugAssign (st : State) (x : Ident) (op : Binop) (e : Expr) :
    Exec st (.augAssign x op e)
      (.normal (update st x (.int
        (evalBinopZ op
          (match lookup st x with | some (.int n) => n | _ => 0)
          (match evalExpr st e with | .int n => n | _ => 0)))))

  | execArraySet (st : State) (arr : Ident) (i v : Expr) :
    Exec st (.arraySet arr i v)
      (.normal (arrayUpdate st arr
        (match evalExpr st i with | .int n => n | _ => 0)
        (match evalExpr st v with | .int n => n | _ => 0)))

  | execSeq (st : State) (s1 s2 : Stmt) (st' : State) (out : Outcome) :
    Exec st s1 (.normal st') →
    Exec st' s2 out →
    Exec st (.seq s1 s2) out

  | execSeqReturn (st : State) (s1 s2 : Stmt) (st' : State) (v : Val) :
    Exec st s1 (.returned st' v) →
    Exec st (.seq s1 s2) (.returned st' v)

  | execSeqContinue (st : State) (s1 s2 : Stmt) (st' : State) :
    Exec st s1 (.continued st') →
    Exec st (.seq s1 s2) (.continued st')

  | execIfTrue (st : State) (cond : Expr) (s1 s2 : Stmt) (out : Outcome) :
    evalBool st cond = true →
    Exec st s1 out →
    Exec st (.ite cond s1 s2) out

  | execIfFalse (st : State) (cond : Expr) (s1 s2 : Stmt) (out : Outcome) :
    evalBool st cond = false →
    Exec st s2 out →
    Exec st (.ite cond s1 s2) out

  | execWhileTrue (st : State) (inv var : ContractExpr) (cond : Expr)
      (body : Stmt) (st' : State) (out : Outcome) :
    evalBool st cond = true →
    Exec st body (.normal st') →
    Exec st' (.while_ inv var cond body) out →
    Exec st (.while_ inv var cond body) out

  | execWhileContinue (st : State) (inv var : ContractExpr) (cond : Expr)
      (body : Stmt) (st' : State) (out : Outcome) :
    evalBool st cond = true →
    Exec st body (.continued st') →
    Exec st' (.while_ inv var cond body) out →
    Exec st (.while_ inv var cond body) out

  | execWhileFalse (st : State) (inv var : ContractExpr) (cond : Expr)
      (body : Stmt) :
    evalBool st cond = false →
    Exec st (.while_ inv var cond body) (.normal st)

  | execContinue (st : State) :
    Exec st .continue_ (.continued st)

  | execReturn (st : State) (e : Expr) :
    Exec st (.ret e)
      (.returned (update st "\result" (evalExpr st e)) (evalExpr st e))

  | execFor (st : State) (x arr : Ident) (inv var : ContractExpr) (body : Stmt) (out : Outcome) :
    Exec st (desugar (.for_ x arr inv var body)) out →
    Exec st (.for_ x arr inv var body) out

theorem exec_deterministic {st : State} {s : Stmt} {out1 out2 : Outcome}
    (h1 : Exec st s out1) (h2 : Exec st s out2) : out1 = out2 := by
  induction h1 generalizing out2 with
  | execSkip => cases h2; rfl
  | execAssign => cases h2; rfl
  | execAugAssign => cases h2; rfl
  | execArraySet => cases h2; rfl
  | execSeq _ _ _ _ _ h1a h1b ih1a ih1b =>
    cases h2 with
    | execSeq _ _ _ _ _ h2a h2b =>
      have := ih1a h2a; injection this with heq; subst heq; exact ih1b h2b
    | execSeqReturn _ _ _ _ _ h2a => have := ih1a h2a; injection this
    | execSeqContinue _ _ _ _ h2a => have := ih1a h2a; injection this
  | execSeqReturn _ _ _ _ _ h1a ih1 =>
    cases h2 with
    | execSeq _ _ _ _ _ h2a _ => have := ih1 h2a; injection this
    | execSeqReturn _ _ _ _ _ h2a => exact ih1 h2a
    | execSeqContinue _ _ _ _ h2a => have := ih1 h2a; injection this
  | execSeqContinue _ _ _ _ h1a ih1 =>
    cases h2 with
    | execSeq _ _ _ _ _ h2a _ => have := ih1 h2a; injection this
    | execSeqReturn _ _ _ _ _ h2a => have := ih1 h2a; injection this
    | execSeqContinue _ _ _ _ h2a => exact ih1 h2a
  | execIfTrue _ _ _ _ _ hc _ ih =>
    cases h2 with
    | execIfTrue _ _ _ _ _ hc2 h2b => exact ih h2b
    | execIfFalse _ _ _ _ _ hc2 _ => simp [hc] at hc2
  | execIfFalse _ _ _ _ _ hc _ ih =>
    cases h2 with
    | execIfTrue _ _ _ _ _ hc2 _ => simp [hc] at hc2
    | execIfFalse _ _ _ _ _ hc2 h2b => exact ih h2b
  | execWhileTrue _ _ _ _ _ _ _ hc h1a h1b ih1a ih1b =>
    cases h2 with
    | execWhileTrue _ _ _ _ _ _ _ hc2 h2a h2b =>
      have := ih1a h2a; injection this with heq; subst heq; exact ih1b h2b
    | execWhileContinue _ _ _ _ _ _ _ hc2 h2a _ =>
      have := ih1a h2a; injection this
    | execWhileFalse _ _ _ _ _ hc2 => simp [hc] at hc2
  | execWhileContinue _ _ _ _ _ _ _ hc h1a h1b ih1a ih1b =>
    cases h2 with
    | execWhileTrue _ _ _ _ _ _ _ hc2 h2a _ =>
      have := ih1a h2a; injection this
    | execWhileContinue _ _ _ _ _ _ _ hc2 h2a h2b =>
      have := ih1a h2a; injection this with heq; subst heq; exact ih1b h2b
    | execWhileFalse _ _ _ _ _ hc2 => simp [hc] at hc2
  | execWhileFalse _ _ _ _ _ hc =>
    cases h2 with
    | execWhileTrue _ _ _ _ _ _ _ hc2 _ _ => simp [hc] at hc2
    | execWhileContinue _ _ _ _ _ _ _ hc2 _ _ => simp [hc] at hc2
    | execWhileFalse => rfl
  | execContinue => cases h2; rfl
  | execReturn => cases h2; rfl
  | execFor _ _ _ _ _ _ _ hprem ih =>
    cases h2 with
    | execFor _ _ _ _ _ _ _ hprem2 => exact ih hprem2
