/-
  MemModel.lean — Memory Model Parameterisation (Category D)
  ==========================================================

  Mirror of Phase7_MemModel.v. This file defines the memory-model
  interface that abstracts \valid, \separated, and the heap operations.
  Different instances (Hoare, typed, store, concurrent) plug into this
  interface; only the Hoare instance is provided here — the
  typed/store/concurrent instances are deferred (see §"Deferred work"
  below).

  The interface is ADDITIVE: the existing pycsl_soundness theorem is
  untouched. The Hoare instance makes valid/separated vacuously True
  (matching the Phase 4 stubs in State.lean:270-272) and makes
  criticalHavoc the identity (matching the Phase 8 .critical stub in
  WP.lean:118-119).

  criticalHavoc models the README §13 "ExecCritical shared state"
  risk: ExecCritical must universally quantify `shared` at entry
  (modelling havoc). The Hoare instance has no shared state, so
  havoc reduces to identity — `criticalHavoc es P = P es`. A real
  concurrent instance would replace this with
  `∀ shared, P (mergeShared es shared)`.
-/
import PyCSL.AST
import PyCSL.State

/-- Memory model interface. Instances plug into this; only Hoare is
    provided here (typed/store/concurrent deferred). -/
class MemModel (ι : Type) where
  /-- \valid(ptr, len): is the range [ptr, ptr+len) valid? -/
  valid       : ι → ι → Prop
  /-- \separated(a, b): are the two ranges non-overlapping? -/
  separated   : ι → ι → Prop
  /-- criticalHavoc es P: the WP of a critical section.
      Hoare instance: P es (no shared state).
      Concurrent instance: ∀ shared, P (mergeShared es shared). -/
  criticalHavoc : ExecState → (ExecState → Prop) → Prop

/-- Hoare memory model: no heap, no shared state.
    - valid/separated are vacuously True (every access is valid).
    - criticalHavoc is identity (no shared state to havoc). -/
instance HoareMM : MemModel Int where
  valid _ _         := True
  separated _ _     := True
  criticalHavoc es P := P es

-- Transparent top-level aliases used by wp.
def valid (ptr len : Int) : Prop := True
def separated (a b : Int) : Prop := True
def criticalHavoc (es : ExecState) (P : ExecState → Prop) : Prop := P es

-- Bridge lemmas: Hoare instance agrees with Phase 4 stubs.

theorem hoare_valid_true (ptr len : Int) : valid ptr len = True := rfl
theorem hoare_separated_true (a b : Int) : separated a b = True := rfl
theorem criticalHavoc_eq (es : ExecState) (P : ExecState → Prop) :
    criticalHavoc es P = P es := rfl

-- Test lemmas

theorem test_criticalHavoc_const (es : ExecState) (b : Prop) :
    criticalHavoc es (fun _ => b) = b := rfl

theorem test_criticalHavoc_qn (es : ExecState) (Qn : ExecState → Prop) :
    criticalHavoc es Qn = Qn es := rfl

theorem test_hoare_valid : valid 0 10 := trivial
theorem test_hoare_separated : separated 0 10 := trivial

/-
  ===== Deferred work (documented, not implemented) =====

  The following instances are NOT provided here — they are the
  remaining Category-D work:

  1. TypedMM     — heap with typed cells; valid(ptr,len) checks the
                    heap contains a typed block at ptr of size >= len.
  2. StoreMM     — single-heap model with store semantics.
  3. ConcurrentMM — real concurrent model: criticalHavoc becomes
                     ∀ shared, P (mergeShared es shared); acquires/
                     releases gain real lock-state; threadEntry spawns
                     with a fresh shared state.

  These require threading the MemModel parameter through evalContract,
  Exec, and wp — an architectural change. The current additive design
  hardcodes the Hoare instance in criticalHavoc (used by wp's .critical
  case) and leaves evalContract's .cValid/.cSeparated stubs as True
  (matching HoareMM). Switching instances requires:
    - re-proving pycsl_soundness against the new instance's
      criticalHavoc (the .critical soundness case changes);
    - re-routing evalContract's .cValid/.cSeparated clauses through the
      instance's valid/separated.

  Named TODOs:
    - TODO(Phase7-typed):     TypedMM instance with real \valid.
    - TODO(Phase7-store):     StoreMM instance with real \separated.
    - TODO(Phase7-concurrent): ConcurrentMM instance with real havoc
      (∀ shared, P (mergeShared es shared)) and lock-state for
      acquires/releases.
-/
