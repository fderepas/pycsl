/-
  Tests.lean — Concrete evaluation tests for the PyCSL formalization
  Mirror of Tests.v (all phases). Updated for ExecState-based Exec.
-/
import PyCSL.AST
import PyCSL.State
import PyCSL.SOS
import PyCSL.WP
import PyCSL.WhileInv
import PyCSL.Soundness
import PyCSL.SoundnessVerified
import PyCSL.Desugar
import PyCSL.EmitStmtSurface
import PyCSL.EmitAssign
import PyCSL.EmitAugAssign
import PyCSL.EmitArraySet
import PyCSL.EmitSeq
import PyCSL.EmitBlocks
import PyCSL.EmitComposition

def esEmpty : ExecState := mkExecState []

-- Test 1: Assign x = 42
theorem test_assign :
    Exec esEmpty (.assign "x" (.int 42))
      (.normal (setReg esEmpty (update [] "x" (.int 42)))) :=
  .execAssign esEmpty "x" (.int 42)

-- Test 2: Sequential assignment x=1; y=2
theorem test_seq_assign :
    let st1 := update [] "x" (.int 1)
    let es1  := setReg esEmpty st1
    Exec esEmpty
      (.seq (.assign "x" (.int 1)) (.assign "y" (.int 2)))
      (.normal (setReg es1 (update st1 "y" (.int 2)))) :=
  .execSeq esEmpty _ _ _ _
    (.execAssign esEmpty "x" (.int 1))
    (.execAssign _ "y" (.int 2))

-- Test 3: If-then-else with true condition
theorem test_if_true (es : ExecState) (hc : evalBool es.regState (.int 1) = true) :
    Exec es (.ite (.int 1) (.assign "x" (.int 10)) (.assign "x" (.int 20)))
      (.normal (setReg es (update es.regState "x" (.int 10)))) :=
  .execIfTrue es _ _ _ _ hc (.execAssign es "x" (.int 10))

-- Test 4: Skip is identity
theorem test_skip (es : ExecState) : Exec es .skip (.normal es) :=
  .execSkip es

-- Test 5: Return produces OReturned with \result bound
theorem test_return :
    Exec esEmpty (.ret (.int 7))
      (.returned
        (setReg esEmpty (update [] "\\result" (.int 7)))
        (.int 7)) :=
  .execReturn esEmpty (.int 7)

-- Test 6: Continue produces OContinued
theorem test_continue (es : ExecState) : Exec es .continue_ (.continued es) :=
  .execContinue es

-- Test 7: Break produces OBroke
theorem test_break (es : ExecState) : Exec es .break_ (.broke es) :=
  .execBreak es

-- Test 8: WP for Skip is identity
theorem test_wp_skip (es : ExecState)
    (Qn Qr Qc Qb : ExecState → Prop) (Qe : Ident → ExecState → Prop)
    (preEs : ExecState) :
    wp .skip Qn Qr Qc Qb Qe preEs es ↔ Qn es := by
  simp [wp]

-- Test 9: WP for Assign substitutes
theorem test_wp_assign (es : ExecState)
    (Qr Qc Qb : ExecState → Prop) (Qe : Ident → ExecState → Prop)
    (preEs : ExecState) :
    wp (.assign "x" (.int 42))
       (fun es' => lookup es'.regState "x" = some (.int 42))
       Qr Qc Qb Qe preEs es := by
  simp [wp, setReg, update, lookup, evalExpr]

-- Test 10: Soundness applied to Skip
theorem test_soundness_skip (es : ExecState) (P : ExecState → Prop)
    (hP : P es) :
    P es :=
  pycsl_soundness es .skip (.normal es) P (fun _ => True) (fun _ => True) (fun _ => True)
    (fun _ _ => True) esEmpty (.execSkip es) hP

-- Test 11: Soundness applied to Assign
theorem test_soundness_assign (es : ExecState) :
    Exec es (.assign "x" (.int 5))
      (.normal (setReg es (update es.regState "x" (.int 5)))) →
    lookup (setReg es (update es.regState "x" (.int 5))).regState "x" = some (.int 5) :=
  fun hExec =>
    pycsl_soundness es (.assign "x" (.int 5))
      (.normal (setReg es (update es.regState "x" (.int 5))))
      (fun es' => lookup es'.regState "x" = some (.int 5))
      (fun _ => True) (fun _ => True) (fun _ => True) (fun _ _ => True)
      esEmpty hExec (by
        show lookup (("x", Val.int 5) :: es.regState) "x" = some (.int 5)
        simp [lookup])

-- Test 12: Augmented assign
theorem test_aug_assign :
    let st  := [("x", Val.int 10)]
    let es  := mkExecState st
    Exec es (.augAssign "x" .add (.int 5))
      (.normal (setReg es (update st "x" (.int 15)))) :=
  Exec.execAugAssign _ _ _ _

-- Test 13: Assert passes when condition holds
theorem test_assert_pass (es : ExecState)
    (h : evalContract es.regState es.regState none (.int 1)) :
    Exec es (.assert_ (.int 1) "unreachable") (.normal es) :=
  .execAssertPass es (.int 1) "unreachable" h

-- Test 14: Ghost declaration updates ghost state
theorem test_ghost_decl :
    Exec esEmpty (.ghostDecl "g" .int (.int 0))
      (.normal (setGhost esEmpty (ghostUpdate esEmpty.ghostSt "g" (.int 0)))) :=
  .execGhostDecl esEmpty "g" .int (.int 0)

-- Test 15: Label records ghost snapshot
theorem test_label :
    Exec esEmpty (.label_ "PRE")
      (.normal (setLabels esEmpty [("PRE", esEmpty.ghostSt)])) :=
  .execLabel esEmpty "PRE"

-- Test 16: walrusAssign is identical to assign
theorem test_walrus_assign_exec :
    Exec esEmpty (walrusAssign "x" (.int 7))
      (.normal (setReg esEmpty (update [] "x" (.int 7)))) :=
  .execAssign esEmpty "x" (.int 7)

-- Test 17: desugar_match single hit
theorem test_match_hit :
    let st := update [] "v" (.int 42)
    let es := mkExecState st
    Exec es
      (desugarMatch (.var "v") [(42, .assign "r" (.int 1))] (.assign "r" (.int 0)))
      (.normal (setReg es (update st "r" (.int 1)))) := by
  apply exec_desugarMatch_hit
  · show (lookup (update [] "v" (.int 42)) "v").getD (.int 0) = .int 42
    simp [update, lookup]
  · exact .execAssign _ "r" (.int 1)

-- Test 18: Exception — raise and catch
theorem test_raise_catch :
    Exec esEmpty
      (.tryCatch (.raise_ "ValueError") "ValueError" (.assign "x" (.int 0)))
      (.normal (setReg esEmpty (update [] "x" (.int 0)))) :=
  .execTryCatchCaught esEmpty (.raise_ "ValueError") "ValueError"
    (.assign "x" (.int 0)) esEmpty _
    (.execRaise esEmpty "ValueError")
    (.execAssign esEmpty "x" (.int 0))

-- Test 19: CBoolLit true evaluates to True
theorem test_boollit_true :
    evalContract [] [] none (.boolLit true) := by
  simp [evalContract]

-- Test 20: CIsSorted empty range is trivially sorted
theorem test_is_sorted_empty (st : List (Ident × Val)) :
    evalContract st st none (.isSorted "a" (.int 0) (.int 0)) := by
  simp only [evalContract, evalZ]
  -- sortedListRange a 0 0 = if 0 < 0 then ... else True = True (vacuous)
  split <;> simp only [sortedListRange] <;>
    (split <;> first | omega | trivial)

-- ===== Axiom audit =====
-- Lists all axioms (propositional + classical) that pycsl_soundness depends on.
-- Expected: [propext, Classical.choice, Quot.sound]
--           (no sorryAx — all for-loop and try-catch lemmas proved)
#print axioms pycsl_soundness

-- Verified path (via WhyML correspondence):
-- Expected: [propext, Classical.choice, Quot.sound]
--           (pycslSoundnessVerified takes wpW as a hypothesis, no axioms)
#print axioms pycslSoundnessVerified

-- ===== Phase 6A+6B+6C axiom audit (monday-02.md / monday-03.md) =====
-- vcgSound: VCG correctness proof — no domain axioms.
-- Expected: [propext, Classical.choice, Quot.sound]
#print axioms vcgSound

-- vcgBridge: Stage B-3 — proved from why3ValidatesEmitted (NO sorry, NO module6EncodesMlw).
-- Expected: [why3ValidatesEmitted, propext, Classical.choice, Quot.sound]
-- (why3ValidatesVcFormula is now a proved THEOREM, not an axiom)
#print axioms vcgBridge

-- why3ImplementsWpW_derived: proved from vcgBridge + vcgSound.
-- Expected: [why3ValidatesEmitted, propext, Classical.choice, Quot.sound]
-- (same as vcgBridge — why3ValidatesEmitted is the sole prover-trust axiom after B-3)
#print axioms why3ImplementsWpW_derived

-- emitSkipCorrect: Sub-α pilot (Q2 of closer-to-code.md).
-- Per-construct emission correctness for wSkip. Expected: [] (pure rfl).
-- When all 15 Sub-α constructs land, the module6EncodesMlw axiom can be
-- discharged as a composition of these per-construct lemmas.
#print axioms PyCSL.emitSkipCorrect

-- emitAssignCorrect: Sub-α.2 (full state coverage for wAssign).
-- For every state s, x, e: emitAssign s x e is in acceptableAssignEmissions.
-- Covers shared/declared/bounded_int/default branches on formal Expr type.
#print axioms PyCSL.emitAssignCorrect
#print axioms PyCSL.emitStmtStringStateAssignCorrect

-- emitAugAssignCorrect: Sub-α.3 (wAugAssign).
-- For every x, op, e: emitAugAssign x op e ∈ acceptableAugAssignEmissions.
-- Singleton acceptable set (bitwise/array-extend branches unreachable on formal Binop).
#print axioms PyCSL.emitAugAssignCorrect

-- emitArraySetCorrect: Sub-α.4 (wArraySet).
-- is_array form + subscript_set fallback both accepted.
#print axioms PyCSL.emitArraySetCorrect

-- emitSeqCorrect: Sub-α.5 (wSeq recursive composition).
-- The recursive concatenation `emit w1 ++ ";\n" ++ emit w2`.
#print axioms PyCSL.emitSeqCorrect

-- emitRaiseCorrect / emitLabelCorrect / emitAssertCorrect: Sub-α.8/.12/.13.
-- Single-line constructs, singleton acceptable sets.
#print axioms PyCSL.emitRaiseCorrect
#print axioms PyCSL.emitLabelCorrect
#print axioms PyCSL.emitAssertCorrect

-- emitIfCorrect / emitWhileCorrect / emitTryCatchCorrect: Sub-α.6/.7/.9.
-- Multi-line block constructs. wIf has 3 acceptable forms (with/without else
-- and body_returns_value); wWhile and wTryCatch each have a single canonical form.
#print axioms PyCSL.emitIfCorrect
#print axioms PyCSL.emitWhileCorrect
#print axioms PyCSL.emitTryCatchCorrect

-- emitGhostDeclCorrect / emitGhostAssignCorrect: Sub-α.10/.11.
-- Per-ghost-type emission for ghost variable declarations and assignments.
#print axioms PyCSL.emitGhostDeclCorrect
#print axioms PyCSL.emitGhostAssignCorrect

-- emitStmtFullCompleteSound: Sub-α.14 (aggregate composition lemma).
-- For every Stmt s, the formal emission lies in the per-construct
-- acceptable set. Discharges all 22 Stmt constructors via the per-
-- construct Sub-α theorems plus structural unfolding.
#print axioms PyCSL.emitStmtFullCompleteSound

-- Note: the parallel state-aware refinement correspondence
-- (`emit_stmt_state_aware_sound` in Phase6L_EmitStateAwareCorr.v)
-- is Rocq-only — the state-aware printer is exposed only via Rocq
-- extraction for the CC.5 byte-diff tooling. The Lean side keeps
-- the structural composition lemma as its canonical correctness
-- theorem.
