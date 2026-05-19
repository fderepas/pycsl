/-
  Soundness.lean — PyCSL Soundness Theorem
  Port of Phase5b_Soundness.v
-/
import PyCSL.AST
import PyCSL.State
import PyCSL.SOS
import PyCSL.WP
import PyCSL.WhileInv

def outcomePost (Qn Qr Qc : State → Prop) : Outcome → Prop
  | .normal st'     => Qn st'
  | .returned st' _ => Qr st'
  | .continued st'  => Qc st'

theorem pycsl_soundness
    (st : State) (s : Stmt) (out : Outcome)
    (hExec : Exec st s out) :
    ∀ (Qn Qr Qc : State → Prop) (preSt : State),
    wp s Qn Qr Qc preSt st →
    outcomePost Qn Qr Qc out := by
  induction hExec with
  | execSkip => intro _ _ _ _ hWp; exact hWp
  | execAssign => intro _ _ _ _ hWp; exact hWp
  | execAugAssign => intro _ _ _ _ hWp; exact hWp
  | execArraySet => intro _ _ _ _ hWp; exact hWp
  | execSeq _ _ s2 _ _ _ _ ih1 ih2 =>
    intro Qn Qr Qc preSt hWp
    unfold wp at hWp
    exact ih2 Qn Qr Qc preSt
      (ih1 (fun st' => wp s2 Qn Qr Qc preSt st') Qr Qc preSt hWp)
  | execSeqReturn _ _ s2 _ _ _ ih =>
    intro Qn Qr Qc preSt hWp
    unfold wp at hWp
    exact ih (fun st' => wp s2 Qn Qr Qc preSt st') Qr Qc preSt hWp
  | execSeqContinue _ _ s2 _ _ ih =>
    intro Qn Qr Qc preSt hWp
    unfold wp at hWp
    exact ih (fun st' => wp s2 Qn Qr Qc preSt st') Qr Qc preSt hWp
  | execIfTrue _ _ _ _ _ hc _ ih =>
    intro Qn Qr Qc preSt hWp
    unfold wp at hWp
    exact ih Qn Qr Qc preSt (hWp.1 hc)
  | execIfFalse _ _ _ _ _ hc _ ih =>
    intro Qn Qr Qc preSt hWp
    unfold wp at hWp
    exact ih Qn Qr Qc preSt (hWp.2 hc)
  | execWhileTrue st _ _ _ _ st' _ hc _ _ ih1 ih2 =>
    intro Qn Qr Qc preSt hWp
    unfold wp at hWp
    obtain ⟨hInv, hPres, hPost⟩ := hWp
    have hBd := ih1 _ Qr _ preSt (hPres st hInv hc)
    simp [outcomePost] at hBd
    obtain ⟨hInv', _, _⟩ := hBd
    exact ih2 Qn Qr Qc preSt (by unfold wp; exact ⟨hInv', hPres, hPost⟩)
  | execWhileContinue st _ _ _ _ st' _ hc _ _ ih1 ih2 =>
    intro Qn Qr Qc preSt hWp
    unfold wp at hWp
    obtain ⟨hInv, hPres, hPost⟩ := hWp
    have hBd := ih1 _ Qr _ preSt (hPres st hInv hc)
    simp [outcomePost] at hBd
    obtain ⟨hInv', _, _⟩ := hBd
    exact ih2 Qn Qr Qc preSt (by unfold wp; exact ⟨hInv', hPres, hPost⟩)
  | execWhileFalse st _ _ _ _ hc =>
    intro Qn _ _ preSt hWp
    unfold wp at hWp
    exact hWp.2.2 st hWp.1 hc
  | execContinue => intro _ _ _ _ hWp; exact hWp
  | execReturn => intro _ _ _ _ hWp; exact hWp
