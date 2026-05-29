/-
  VcFormula.lean — Phase 6C-β: VcFormula shallow embedding

  Defines VcFormula, a shallow embedding of the integer-arithmetic
  formula fragment that Why3 emits for PyCSL VCs.  No dependency on
  why3-semantics (which is Rocq-only).

  The key components:
    VcFormula     — inductive type for VC conjuncts
    evalVcFormula — denotational semantics (VcFormula → ExecState → ExecState → Prop)
    vcFormulaOf   — enumerates the n-th VcFormula for each WhyMLStmt

  Design rationale (monday-05.md, Root cause A):
    Since why3-semantics (formula_rep) is Rocq-only, we cannot import it
    in Lean 4.  Instead, VcFormula is a self-contained embedding whose
    semantics (evalVcFormula) is defined purely in Lean 4.

    The Rocq side (Phase6m_VcgSemBridge.v) CAN import why3-semantics and
    prove:
      eval_vc_formula_iff_formula_rep : evalVcFormula f es preEs ↔
        formula_rep pd pf vt vv (vc_formula_to_why3 f) Hval = true
    giving Rocq a fully proved path.

  Phase 6C-β connection:
    vcFormulaOf_sound (VcgSemBridge.lean):
      If all VcFormulas for (ws, Q, preEs, es) hold, then vcProp ws Q preEs es holds.
    why3ValidatesVcFormula (VcgSemBridge.lean):
      Why3Certificate ws Q → vcFormulaOf ws Q preEs es i = some f → evalVcFormula f es preEs.
    These two together replace module6EncodesMlw in the vcgBridge proof.
-/
import PyCSL.AST
import PyCSL.State
import PyCSL.WhyML
import PyCSL.WPW
import PyCSL.Why3Vcg

-- ===== VcFormula: shallow embedding of Why3's integer-arithmetic fragment =====

/-- VcFormula: a shallow embedding of the formula constructors that appear
    in the VCs for the 13 WhyMLStmt constructors.

    The constructor set covers:
    - Integer arithmetic comparisons using ContractExpr terms (le, lt, ge, eq)
    - Contract/invariant truth (contract) using evalC
    - Propositional connectives (and, impl, true_)
    - Escape hatch (prop) for complex goals involving ExecState quantification
      (used for VC2/VC3 of wWhile, both conjuncts of wIf, etc.)

    No dependency on why3-semantics.
    Rocq side: Phase6m_VcgSemBridge.v connects the structural constructors
    (le, lt, ge, eq, contract) to formula_rep from Cohen & JF (POPL 2024). -/
inductive VcFormula : Type where
  /-- Integer ≤: evalV es preEs e1 ≤ evalV es preEs e2 (wWhile variant). -/
  | le       (e1 e2 : ContractExpr) : VcFormula
  /-- Integer <: evalV es preEs e1 < evalV es preEs e2 (variant decrease). -/
  | lt       (e1 e2 : ContractExpr) : VcFormula
  /-- Integer ≥: evalV es preEs e1 ≥ evalV es preEs e2 (variant non-negative). -/
  | ge       (e1 e2 : ContractExpr) : VcFormula
  /-- Integer =: evalV es preEs e1 = evalV es preEs e2. -/
  | eq       (e1 e2 : ContractExpr) : VcFormula
  /-- Contract truth: evalC es preEs none c (invariants, assertions). -/
  | contract (c : ContractExpr)      : VcFormula
  /-- Conjunction. -/
  | and      (f1 f2 : VcFormula)    : VcFormula
  /-- Implication: f1 → f2. -/
  | impl     (f1 f2 : VcFormula)    : VcFormula
  /-- Arbitrary Prop (escape hatch for complex goals involving ExecState quantification).
      Used for wSeq, wIf, wTryCatch, and wWhile VC2/VC3 which quantify over ExecState. -/
  | prop     (P : Prop)              : VcFormula
  /-- Trivially true (structural placeholder; not returned by vcFormulaOf). -/
  | true_                            : VcFormula

-- ===== evalVcFormula: denotational semantics =====

/-- evalVcFormula f es preEs: the Prop denoted by VcFormula f
    at execution state es with pre-state preEs.

    The `prop` case returns the embedded Prop directly, ignoring (es, preEs).
    The structural cases use evalV and evalC from State.lean. -/
def evalVcFormula : VcFormula → ExecState → ExecState → Prop
  | .le e1 e2,    es, preEs => evalV es preEs e1 ≤ evalV es preEs e2
  | .lt e1 e2,    es, preEs => evalV es preEs e1 < evalV es preEs e2
  | .ge e1 e2,    es, preEs => evalV es preEs e1 ≥ evalV es preEs e2
  | .eq e1 e2,    es, preEs => evalV es preEs e1 = evalV es preEs e2
  | .contract c,  es, preEs => evalC es preEs none c
  | .and f1 f2,   es, preEs => evalVcFormula f1 es preEs ∧ evalVcFormula f2 es preEs
  | .impl f1 f2,  es, preEs => evalVcFormula f1 es preEs → evalVcFormula f2 es preEs
  | .prop P,      _,  _     => P
  | .true_,       _,  _     => True

-- ===== vcFormulaOf: enumerate VcFormulas for each WhyMLStmt =====

/-- vcFormulaOf ws Q preEs es n: the n-th VcFormula for (ws, Q) at states (preEs, es).

    This is the formal specification of what Module6 should emit for each VC.
    It enumerates the conjuncts of vcProp ws Q preEs es by index n.

    Index allocation (matching Why3's -a split_vc output order):
    - Most constructors: n=0 only (one conjunct, wrapping the full vcProp case as `.prop`).
    - wIf: n=0 (true branch), n=1 (false branch).
    - wAssert: n=0 (condition), n=1 (postcondition).
    - wWhile: n=0 (VC1: invariant entry), n=1 (VC2: body preservation), n=2 (VC3: exit).
    - All other n: none.

    The `.contract c` constructor is used for wWhile VC1 and wAssert VC0, where
    `evalVcFormula (.contract c) es preEs = evalC es preEs none c` connects to vcProp.
    All other cases use `.prop P` wrapping the exact vcProp conjunct.

    vcFormulaOf_sound (VcgSemBridge.lean) proves: if all VcFormulas hold at (es, preEs),
    then vcProp ws Q preEs es holds. -/
def vcFormulaOf (ws : WhyMLStmt) (Q : WpConts) (preEs es : ExecState) (n : Nat) :
    Option VcFormula :=
  match ws, n with

  -- wSkip: one VC — normal continuation at current state
  | .wSkip, 0 =>
    some (.prop (Q.wcN es))

  -- wAssign: one VC — normal continuation after register update
  | .wAssign x e, 0 =>
    some (.prop (Q.wcN (setReg es (update es.regState x (evalExpr es.regState e)))))

  -- wAugAssign: one VC — normal continuation after augmented assignment
  | .wAugAssign x op e, 0 =>
    let cur := match lookup es.regState x with | some (.int k) => k | _ => 0
    let nv  := evalBinopZ op cur (match evalExpr es.regState e with | .int k => k | _ => 0)
    some (.prop (Q.wcN (setReg es (update es.regState x (.int nv)))))

  -- wArraySet: one VC — normal continuation after array element update
  | .wArraySet arr i v, 0 =>
    let idx := match evalExpr es.regState i with | .int k => k | _ => 0
    let nv  := match evalExpr es.regState v with | .int k => k | _ => 0
    some (.prop (Q.wcN (setReg es (arrayUpdate es.regState arr idx nv))))

  -- wSeq: one VC — vcProp w1 with w2-threaded continuation
  | .wSeq w1 w2, 0 =>
    some (.prop (vcProp w1 { wcN := fun es' => vcProp w2 Q preEs es',
                             wcR := Q.wcR, wcC := Q.wcC, wcB := Q.wcB, wcE := Q.wcE }
                        preEs es))

  -- wIf: two VCs — true branch (n=0) and false branch (n=1)
  | .wIf cond w1 _, 0 =>
    some (.prop (evalBool es.regState cond = true → vcProp w1 Q preEs es))
  | .wIf cond _ w2, 1 =>
    some (.prop (evalBool es.regState cond = false → vcProp w2 Q preEs es))

  -- wWhile: three VCs matching Why3's -a split_vc output
  | .wWhile invs _ _ _, 0 =>
    -- VC1: invariant holds at loop entry (Why3 split_vc goal 1)
    some (.contract (cConj invs))
  | .wWhile invs vars cond body, 1 =>
    let inv := cConj invs
    let var := cFirst vars
    -- VC2: body preserves invariant and strictly decreases variant (goal 2)
    some (.prop (∀ es', evalC es' preEs none inv →
                        evalBool es'.regState cond = true →
                        let bodyDone es'' :=
                          evalC es'' preEs none inv ∧
                          evalV es'' preEs var < evalV es' preEs var ∧
                          evalV es'' preEs var ≥ 0
                        vcProp body { wcN := bodyDone, wcR := Q.wcR,
                                      wcC := bodyDone, wcB := Q.wcN, wcE := Q.wcE }
                               preEs es'))
  | .wWhile invs _ cond _, 2 =>
    let inv := cConj invs
    -- VC3: invariant ∧ ¬guard → normal postcondition (goal 3)
    some (.prop (∀ es', evalC es' preEs none inv →
                        evalBool es'.regState cond = false → Q.wcN es'))

  -- wRaise: one VC — dispatch to the appropriate continuation
  | .wRaise .excReturn,    0 => some (.prop (Q.wcR es))
  | .wRaise .excBreak,     0 => some (.prop (Q.wcB es))
  | .wRaise .excContinue,  0 => some (.prop (Q.wcC es))
  | .wRaise (.excNamed nm), 0 => some (.prop (Q.wcE nm es))

  -- wTryCatch: one VC — body with exception-dispatcher continuation
  | .wTryCatch body exc handler, 0 =>
    some (.prop (vcProp body { wcN := Q.wcN, wcR := Q.wcR, wcC := Q.wcC, wcB := Q.wcB,
                               wcE := fun exc' es' =>
                                 if exc' == exc then vcProp handler Q preEs es'
                                 else Q.wcE exc' es' }
                        preEs es))

  -- wGhostDecl: one VC — normal continuation after ghost declaration
  | .wGhostDecl x t e, 0 =>
    some (.prop (Q.wcN (setGhost es (ghostUpdate es.ghostSt x (evalGhostVal t es e)))))

  -- wGhostAssign: one VC — normal continuation after ghost augmented assignment
  | .wGhostAssign x _ op e, 0 =>
    let cur := ghostLookup es.ghostSt x
    let nv  := applyGhostAug op cur es e
    some (.prop (Q.wcN (setGhost es (ghostUpdate es.ghostSt x nv))))

  -- wLabel: one VC — normal continuation after label snapshot
  | .wLabel L, 0 =>
    some (.prop (Q.wcN (setLabels es ((L, es.ghostSt) :: es.labelSnaps))))

  -- wAssert: two VCs — condition truth (n=0) and normal continuation (n=1)
  | .wAssert cond _, 0 => some (.contract cond)
  | .wAssert _ _,   1 => some (.prop (Q.wcN es))

  -- All other (ws, n): no VC at that index
  | _, _ => none
