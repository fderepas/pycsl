/-
  MemModelSoundness.lean — instance-parameterised soundness + non-vacuity of
  the typed/store memory models (Category D). Lean parity with
  Phase7b_MemModelSoundness.v.
  ============================================================================
  `MemModel.lean` defines the memory-model interface and four instances
  (Hoare / Typed / Store / Concurrent). This file closes — ADDITIVELY, on top
  of the proved `pycsl_soundness`, with 0 new axioms / 0 sorry — the two
  things left open there:

    • `critical_sound_param`: for ANY memory model whose `criticalHavoc` is
      *sub-identity*, the `.critical` construct (the only WP arm consulting
      the memory model) is sound, reducing to `pycsl_soundness` on the body.
      The global `wp` is unchanged.
    • per-instance corollaries: Hoare/Typed/Store are sub-identity outright
      (identity `criticalHavoc`); ConcurrentMM is sub-identity given a
      neutral shared state (a hypothesis, NOT an axiom). This is "soundness
      proven for each instance" for the memory-model-sensitive construct.
    • discrimination/non-vacuity lemmas for the typed/store predicates.

  The residual (the gate's "1") is the genuinely-hard concurrent model: a
  havoc-aware SOS for `.critical` plus a lock-state for `acquires`/`releases`,
  both needing the deferred `ExecState` field change.
-/

import PyCSL.SOS
import PyCSL.WP
import PyCSL.MemModel
import PyCSL.Soundness

namespace PyCSL

/-- A memory model's `criticalHavoc` is *sub-identity* when whatever it claims
    of `P` at entry state `es` entails `P es`. The `.critical` soundness case
    needs exactly this. -/
def chSubIdentity (ch : ExecState → (ExecState → Prop) → Prop) : Prop :=
  ∀ es P, ch es P → P es

/-- Instance-parameterised soundness of the critical-section construct: for
    ANY sub-identity `ch`, `.critical` is sound. Reduces to `pycsl_soundness`
    on the body; the global `wp` is not changed. -/
theorem critical_sound_param
    (ch : ExecState → (ExecState → Prop) → Prop)
    (hsub : chSubIdentity ch)
    (es : ExecState) (mutex : Ident) (body : Stmt) (out : Outcome)
    (Qn Qr Qc Qb : ExecState → Prop) (Qe : Ident → ExecState → Prop)
    (preEs : ExecState)
    (hExec : Exec es (.critical mutex body) out)
    (hCh : ch es (fun es' => wp body Qn Qr Qc Qb Qe preEs es')) :
    outcomePost Qn Qr Qc Qb Qe out := by
  cases hExec with
  | execCritical _ _ _ _ hb =>
    exact pycsl_soundness es body out Qn Qr Qc Qb Qe preEs hb (hsub _ _ hCh)

/-- Hoare / Typed / Store all use the identity `criticalHavoc` — sub-identity. -/
theorem identity_chSubIdentity : chSubIdentity criticalHavoc :=
  fun _ _ h => h

/-- Soundness of `.critical` under the identity havoc (Hoare/Typed/Store). -/
theorem critical_sound_identity
    (es : ExecState) (mutex : Ident) (body : Stmt) (out : Outcome)
    (Qn Qr Qc Qb : ExecState → Prop) (Qe : Ident → ExecState → Prop)
    (preEs : ExecState)
    (hExec : Exec es (.critical mutex body) out)
    (hCh : criticalHavoc es (fun es' => wp body Qn Qr Qc Qb Qe preEs es')) :
    outcomePost Qn Qr Qc Qb Qe out :=
  critical_sound_param criticalHavoc identity_chSubIdentity
    es mutex body out Qn Qr Qc Qb Qe preEs hExec hCh

/-- ConcurrentMM is sub-identity GIVEN a neutral shared state `s0` with
    `mergeShared es s0 = es` (a hypothesis, NOT an axiom). -/
theorem concurrent_chSubIdentity {σ : Type} (mergeShared : ExecState → σ → ExecState)
    (s0 : σ) (hneutral : ∀ es, mergeShared es s0 = es) :
    chSubIdentity (ConcurrentMM.criticalHavoc σ mergeShared) := by
  intro es P h
  unfold ConcurrentMM.criticalHavoc at h
  have hs := h s0
  rw [hneutral] at hs
  exact hs

/-- Soundness of `.critical` under ConcurrentMM, given a neutral shared state. -/
theorem critical_sound_concurrent {σ : Type} (mergeShared : ExecState → σ → ExecState)
    (s0 : σ) (hneutral : ∀ es, mergeShared es s0 = es)
    (es : ExecState) (mutex : Ident) (body : Stmt) (out : Outcome)
    (Qn Qr Qc Qb : ExecState → Prop) (Qe : Ident → ExecState → Prop)
    (preEs : ExecState)
    (hExec : Exec es (.critical mutex body) out)
    (hCh : ConcurrentMM.criticalHavoc σ mergeShared es
             (fun es' => wp body Qn Qr Qc Qb Qe preEs es')) :
    outcomePost Qn Qr Qc Qb Qe out :=
  critical_sound_param (ConcurrentMM.criticalHavoc σ mergeShared)
    (concurrent_chSubIdentity mergeShared s0 hneutral)
    es mutex body out Qn Qr Qc Qb Qe preEs hExec hCh

/-! ===== Non-vacuity / discrimination of the typed/store predicates ===== -/

/-- A covering block covers its own range (the typed `valid` body is
    genuinely satisfiable on a non-empty heap). -/
theorem typed_covering_witness (p n : Int) :
    ∃ b : TypedBlock, b ∈ ([(p, n)] : List TypedBlock) ∧
      (match b with | (p', n') => p' ≤ p ∧ p + n ≤ p' + n') :=
  ⟨(p, n), by simp, by simp⟩

/-- Under the empty default heap, nothing is valid — TypedMM is not vacuously
    `True` (it correctly rejects). -/
theorem typed_valid_empty_false : ¬ TypedMM.valid 0 10 := by
  unfold TypedMM.valid TypedHeap
  simp

/-- `TypedMM.separated` discriminates distinct vs. coinciding bases. -/
theorem typed_separated_distinct : TypedMM.separated 0 1 := by
  unfold TypedMM.separated; omega

theorem typed_separated_same_false : ¬ TypedMM.separated 5 5 := by
  unfold TypedMM.separated; omega

/-- `StoreMM.valid`: in-bounds is valid, out-of-bounds is not. -/
theorem store_valid_in_bounds : StoreMM.valid 0 10 := by
  unfold StoreMM.valid StoreSize; omega

theorem store_valid_oob_false : ¬ StoreMM.valid 4090 100 := by
  unfold StoreMM.valid StoreSize; omega

/-- `StoreMM.separated` discriminates distinct vs. coinciding cells. -/
theorem store_separated_distinct : StoreMM.separated 0 1 := by
  unfold StoreMM.separated; omega

theorem store_separated_same_false : ¬ StoreMM.separated 5 5 := by
  unfold StoreMM.separated; omega

end PyCSL
