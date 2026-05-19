/-
  Tests.lean — Concrete evaluation tests for the PyCSL formalization
  Port of Tests.v
-/
import PyCSL.AST
import PyCSL.State
import PyCSL.SOS
import PyCSL.WP
import PyCSL.WhileInv
import PyCSL.Soundness

def stEmpty : State := []

-- Test 1: Assign x = 42
theorem test_assign :
    Exec stEmpty (.assign "x" (.int 42))
      (.normal (update stEmpty "x" (.int 42))) :=
  .execAssign stEmpty "x" (.int 42)

-- Test 2: Sequential assignment x=1; y=2
theorem test_seq_assign :
    Exec stEmpty
      (.seq (.assign "x" (.int 1)) (.assign "y" (.int 2)))
      (.normal (update (update stEmpty "x" (.int 1)) "y" (.int 2))) :=
  .execSeq stEmpty _ _ _ _
    (.execAssign stEmpty "x" (.int 1))
    (.execAssign _ "y" (.int 2))

-- Test 3: Skip is identity
theorem test_skip (st : State) : Exec st .skip (.normal st) :=
  .execSkip st

-- Test 4: Return produces OReturned with \result bound
theorem test_return :
    Exec stEmpty (.ret (.int 7))
      (.returned (update stEmpty "\result" (.int 7)) (.int 7)) :=
  .execReturn stEmpty (.int 7)

-- Test 5: Continue produces OContinued
theorem test_continue (st : State) : Exec st .continue_ (.continued st) :=
  .execContinue st

-- Test 6: WP for Skip is identity
theorem test_wp_skip (st : State) (Qn Qr Qc : State → Prop) (preSt : State) :
    wp .skip Qn Qr Qc preSt st ↔ Qn st := by
  simp [wp]

-- Test 7: exec_deterministic
theorem test_deterministic {st : State} {out1 out2 : Outcome}
    (h1 : Exec st (.assign "x" (.int 1)) out1)
    (h2 : Exec st (.assign "x" (.int 1)) out2) :
    out1 = out2 :=
  exec_deterministic h1 h2

-- Test 8: while_not_continued — while loops never produce OContinued
theorem test_while_not_continued
    {st : State} {inv var : ContractExpr} {cond : Expr} {body : Stmt}
    {out : Outcome}
    (h : Exec st (.while_ inv var cond body) out)
    (st' : State) : out ≠ .continued st' :=
  while_not_continued h st'

-- Test 9: soundness applied to skip
theorem test_soundness_skip (st : State) (Q : State → Prop)
    (hQ : Q st) :
    Q st :=
  pycsl_soundness st .skip (.normal st) (.execSkip st) Q (fun _ => True) (fun _ => True) st hQ

-- Test 10: If-then-else with true condition (int 1 is truthy)
theorem test_if_true :
    Exec stEmpty
      (.ite (.int 1) (.assign "x" (.int 1)) (.assign "x" (.int 2)))
      (.normal (update stEmpty "x" (.int 1))) :=
  .execIfTrue stEmpty _ _ _ _ rfl (.execAssign _ "x" (.int 1))

-- Test 11: If-then-else with false condition (int 0 is falsy)
theorem test_if_false :
    Exec stEmpty
      (.ite (.int 0) (.assign "x" (.int 1)) (.assign "x" (.int 2)))
      (.normal (update stEmpty "x" (.int 2))) :=
  .execIfFalse stEmpty _ _ _ _ rfl (.execAssign _ "x" (.int 2))
