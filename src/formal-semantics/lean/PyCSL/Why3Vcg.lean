/-
  Why3Vcg.lean — Certified VCG for the WhyML Subset (Phase 6A)

  Defines vcProp, a formally-specified VCG that mirrors the verification
  conditions Why3 generates for (ws, Q).  Proves vcgSound : vcProp ↔ wpW
  by structural induction on WhyMLStmt.

  This is Phase 6A of Task 6 (monday-02.md — plan to eliminate
  why3ImplementsWpW from the TCB).

  Architecture after Phase 6A:
    why3ImplementsWpW (old axiom) is REPLACED by:
      axiom why3DischargesVcs : Why3Certificate ws Q → vcProp ws Q preEs es
      theorem why3ImplementsWpW_derived := vcgSound.mp ∘ why3DischargesVcs
    The new axiom only trusts Why3's provers; VCG correctness is proved here.

  Phase 6B will add vcgBridge (with a documented sorry) to Why3Trust.lean.
  Phase 6C will replace the sorry by connecting vcProp to the .mlw emission.

  Reference: Herms, Marché, Monate (CAV 2012) — Lemma 11 + Theorem 13
  are the template for the wWhile case (three-conjunct invariant argument).
-/
import PyCSL.AST
import PyCSL.State
import PyCSL.WhyML
import PyCSL.WPW

-- ===== vcProp: The formally-specified VCG =====

/-- vcProp ws Q preEs es: the verification condition generated for (ws, Q).

    Each case mirrors what Why3's VCG produces for the corresponding
    WhyMLStmt constructor:
    - Simple cases (wSkip, wAssign, wAugAssign, wArraySet, wGhostDecl,
      wGhostAssign, wLabel, wAssert): identical to wpW by construction.
    - wSeq, wIf, wTryCatch: recursive in sub-statements with the same
      continuation threading as wpW.
    - wWhile: three explicit conjuncts matching the VCs that Why3's
      `-a split_vc` option produces (VC1: invariant holds at entry;
      VC2: body preserves invariant and decreases variant; VC3: exit case).
    - wRaise: continuation dispatch identical to wpW.

    vcgSound (below) proves vcProp = wpW propositionally for all cases.

    Phase 6C will connect this definition to the actual .mlw output by
    Module 6 (the `src/pycsl/Module6_WhyMLTranspiler.py` facade +
    `src/pycsl/module6_whyml/` mixin subpackage, post-refactor),
    replacing the sorry in Why3Trust.vcgBridge. -/
def vcProp : WhyMLStmt → WpConts → (preEs es : ExecState) → Prop
  | .wSkip, Q, _, es => Q.wcN es

  | .wAssign x e, Q, _, es =>
    Q.wcN (setReg es (update es.regState x (evalExpr es.regState e)))

  | .wAugAssign x op e, Q, _, es =>
    let cur := match lookup es.regState x with | some (.int n) => n | _ => 0
    let nv  := evalBinopZ op cur (match evalExpr es.regState e with | .int n => n | _ => 0)
    Q.wcN (setReg es (update es.regState x (.int nv)))

  | .wArraySet arr i v, Q, _, es =>
    let idx := match evalExpr es.regState i with | .int n => n | _ => 0
    let nv  := match evalExpr es.regState v with | .int n => n | _ => 0
    Q.wcN (setReg es (arrayUpdate es.regState arr idx nv))

  | .wSeq w1 w2, Q, preEs, es =>
    vcProp w1 { wcN := fun es' => vcProp w2 Q preEs es',
                wcR := Q.wcR, wcC := Q.wcC, wcB := Q.wcB, wcE := Q.wcE }
           preEs es

  | .wIf cond w1 w2, Q, preEs, es =>
    (evalBool es.regState cond = true  → vcProp w1 Q preEs es) ∧
    (evalBool es.regState cond = false → vcProp w2 Q preEs es)

  | .wWhile invs vars cond body, Q, preEs, es =>
    let inv := cConj invs
    let var := cFirst vars
    -- VC1: invariant holds at loop entry (Why3 split_vc goal 1)
    evalC es preEs none inv ∧
    -- VC2: body preserves invariant and decreases variant (Why3 split_vc goal 2)
    (∀ es', evalC es' preEs none inv →
            evalBool es'.regState cond = true →
            let bodyDone es'' :=
              evalC es'' preEs none inv ∧
              evalV es'' preEs var < evalV es' preEs var ∧
              evalV es'' preEs var ≥ 0
            vcProp body { wcN := bodyDone, wcR := Q.wcR,
                          wcC := bodyDone, wcB := Q.wcN, wcE := Q.wcE }
                   preEs es') ∧
    -- VC3: invariant ∧ ¬guard → postcondition (Why3 split_vc goal 3)
    (∀ es', evalC es' preEs none inv →
            evalBool es'.regState cond = false → Q.wcN es')

  | .wRaise .excReturn,    Q, _, es => Q.wcR es
  | .wRaise .excBreak,     Q, _, es => Q.wcB es
  | .wRaise .excContinue,  Q, _, es => Q.wcC es
  | .wRaise (.excNamed n), Q, _, es => Q.wcE n es

  | .wTryCatch body exc handler, Q, preEs, es =>
    vcProp body { wcN := Q.wcN, wcR := Q.wcR, wcC := Q.wcC, wcB := Q.wcB,
                  wcE := fun exc' es' =>
                    if exc' == exc then vcProp handler Q preEs es'
                    else Q.wcE exc' es' }
           preEs es

  | .wGhostDecl x t e, Q, _, es =>
    Q.wcN (setGhost es (ghostUpdate es.ghostSt x (evalGhostVal t es e)))

  | .wGhostAssign x _ op e, Q, _, es =>
    let cur := ghostLookup es.ghostSt x
    let nv  := applyGhostAug op cur es e
    Q.wcN (setGhost es (ghostUpdate es.ghostSt x nv))

  | .wLabel L, Q, _, es =>
    Q.wcN (setLabels es ((L, es.ghostSt) :: es.labelSnaps))

  | .wAssert cond _, Q, preEs, es =>
    evalC es preEs none cond ∧ Q.wcN es

-- ===== vcgSound: vcProp ↔ wpW =====

/-- vcgSound: vcProp is equivalent to wpW for all WhyML statements.

    This is the central theorem of Phase 6A.  It proves that our
    formally-specified VCG (vcProp) correctly captures the weakest
    precondition semantics (wpW) for all 13 WhyMLStmt constructors.

    Proof strategy: structural induction on ws.
    - 9 simple cases (wSkip, wAssign, wAugAssign, wArraySet, wRaise,
      wGhostDecl, wGhostAssign, wLabel, wAssert): both sides reduce to
      the same expression; simp closes the goal.
    - wSeq, wTryCatch: use IH on the sub-statement + wpW_congr to bridge
      the continuation containing vcProp to the one containing wpW.
    - wIf: apply IH on each branch.
    - wWhile (hardest case): the three-conjunct structure is identical
      in vcProp and wpW; the IH closes the body VC.  Template: Herms
      et al. (CAV 2012), Lemma 11 (WP soundness for single step) and
      Theorem 13 (induction over execution derivation). -/
theorem vcgSound (ws : WhyMLStmt) (Q : WpConts) (preEs es : ExecState) :
    vcProp ws Q preEs es ↔ wpW ws Q preEs es := by
  induction ws generalizing Q preEs es with
  -- ===== Simple cases: both sides reduce to the same Prop =====
  -- wSkip, wAssign, wGhostDecl, wGhostAssign, wLabel, wAssert: simp closes via Iff.rfl.
  -- wAugAssign, wArraySet: simp unfolds but leaves A ↔ A with match expressions;
  --   `constructor <;> intro h <;> exact h` closes any A ↔ A goal.
  | wSkip      => simp only [vcProp, wpW]
  | wAssign    => simp only [vcProp, wpW]
  | wAugAssign => simp only [vcProp, wpW]; constructor <;> intro h <;> exact h
  | wArraySet  => simp only [vcProp, wpW]; constructor <;> intro h <;> exact h
  | wGhostDecl   => simp only [vcProp, wpW]
  | wGhostAssign => simp only [vcProp, wpW]
  | wLabel       => simp only [vcProp, wpW]
  | wAssert      => simp only [vcProp, wpW]
  -- ===== wRaise: dispatch on exception constructor =====
  -- All four cases reduce to the same continuation component on both sides.
  | wRaise exc =>
    rcases exc with _ | _ | _ | n <;> simp only [vcProp, wpW]
  -- ===== wSeq: continuations differ in wcN (vcProp w2 vs wpW w2) =====
  -- Step 1: vcProp w1 Qvc ↔ wpW w1 Qvc    by ih1
  -- Step 2: wpW w1 Qvc    ↔ wpW w1 Qwp    by wpW_congr using ih2 for wcN
  | wSeq w1 w2 ih1 ih2 =>
    simp only [vcProp, wpW]
    exact Iff.trans (ih1 _ preEs es)
      (wpW_congr w1 _ _ preEs es
        (fun es' => ih2 Q preEs es')   -- wcN: vcProp w2 ↔ wpW w2
        (fun _ => Iff.rfl)             -- wcR: identical
        (fun _ => Iff.rfl)             -- wcC: identical
        (fun _ => Iff.rfl)             -- wcB: identical
        (fun _ _ => Iff.rfl))          -- wcE: identical
  -- ===== wIf: both branches use the same Q; apply IH on each =====
  | wIf cond wt we iht ihe =>
    simp only [vcProp, wpW]
    exact ⟨fun ⟨ht, he⟩ => ⟨fun h => (iht Q preEs es).mp (ht h),
                              fun h => (ihe Q preEs es).mp (he h)⟩,
           fun ⟨ht, he⟩ => ⟨fun h => (iht Q preEs es).mpr (ht h),
                              fun h => (ihe Q preEs es).mpr (he h)⟩⟩
  -- ===== wWhile: three-conjunct structure is identical on both sides =====
  -- VC1 (invariant holds) and VC3 (exit case) are identical.
  -- VC2 (body): vcProp body bodyQ ↔ wpW body bodyQ by IH.
  -- The body continuation bodyQ is the same in both vcProp and wpW.
  | wWhile invs vars cond body ih =>
    simp only [vcProp, wpW]
    constructor
    · -- Forward: vcProp (.wWhile ...) → wpW (.wWhile ...)
      intro ⟨hinv, hbody, hexit⟩
      refine ⟨hinv, ?_, hexit⟩
      intro es' hinv' hcond
      -- hbody es' hinv' hcond : vcProp body bodyQ preEs es'
      -- Apply IH at bodyQ to convert vcProp body bodyQ → wpW body bodyQ
      exact (ih { wcN := fun es'' => evalC es'' preEs none (cConj invs) ∧
                                     evalV es'' preEs (cFirst vars) < evalV es' preEs (cFirst vars) ∧
                                     evalV es'' preEs (cFirst vars) ≥ 0,
                  wcR := Q.wcR,
                  wcC := fun es'' => evalC es'' preEs none (cConj invs) ∧
                                     evalV es'' preEs (cFirst vars) < evalV es' preEs (cFirst vars) ∧
                                     evalV es'' preEs (cFirst vars) ≥ 0,
                  wcB := Q.wcN, wcE := Q.wcE }
               preEs es').mp (hbody es' hinv' hcond)
    · -- Backward: wpW (.wWhile ...) → vcProp (.wWhile ...)
      intro ⟨hinv, hbody, hexit⟩
      refine ⟨hinv, ?_, hexit⟩
      intro es' hinv' hcond
      -- hbody es' hinv' hcond : wpW body bodyQ preEs es'
      -- Apply IH at bodyQ to convert wpW body bodyQ → vcProp body bodyQ
      exact (ih { wcN := fun es'' => evalC es'' preEs none (cConj invs) ∧
                                     evalV es'' preEs (cFirst vars) < evalV es' preEs (cFirst vars) ∧
                                     evalV es'' preEs (cFirst vars) ≥ 0,
                  wcR := Q.wcR,
                  wcC := fun es'' => evalC es'' preEs none (cConj invs) ∧
                                     evalV es'' preEs (cFirst vars) < evalV es' preEs (cFirst vars) ∧
                                     evalV es'' preEs (cFirst vars) ≥ 0,
                  wcB := Q.wcN, wcE := Q.wcE }
               preEs es').mpr (hbody es' hinv' hcond)
  -- ===== wTryCatch: continuations differ in wcE (vcProp handler vs wpW handler) =====
  -- Step 1: vcProp body Qvc ↔ wpW body Qvc    by ih1
  -- Step 2: wpW body Qvc    ↔ wpW body Qwp    by wpW_congr using ih2 for wcE
  | wTryCatch body exc handler ih1 ih2 =>
    simp only [vcProp, wpW]
    exact Iff.trans (ih1 _ preEs es)
      (wpW_congr body _ _ preEs es
        (fun _ => Iff.rfl)             -- wcN: identical
        (fun _ => Iff.rfl)             -- wcR: identical
        (fun _ => Iff.rfl)             -- wcC: identical
        (fun _ => Iff.rfl)             -- wcB: identical
        (fun exc' es' => by            -- wcE: if match then vcProp/wpW handler else Q.wcE
          -- Bool case analysis: split on whether exc' matches the caught exception.
          cases hb : (exc' == exc)
          · simp [hb]                  -- false: both sides = Q.wcE exc' es'
          · simp [hb]                  -- true: both sides = vcProp/wpW handler
            exact ih2 Q preEs es'))
