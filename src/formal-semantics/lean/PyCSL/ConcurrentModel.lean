/-
  ConcurrentModel.lean — the real concurrent model: havoc-aware SOS + WP for
  `.critical`, and lock-state for `.acquires`/`.releases` (Category D residual).
  Lean parity with Phase7c_ConcurrentModel.v.
  ============================================================================
  Phase 7b proved `.critical` sound for any *sub-identity* memory model, but
  ConcurrentMM's havoc is sub-identity only under a *neutral shared state*
  crutch, because the SOS ran the body on `es` unchanged. This file removes the
  crutch by giving the concurrency constructs a genuine operational semantics
  and re-proving soundness against it — additively, 0 new axioms / 0 sorry.

  No `ExecState` field change: the shared state and per-mutex lock state live in
  the existing `regState` under RESERVED identifiers (as `"\result"` /
  `_pycsl_idx` already are). Once the SOS HAVOCS the shared cell, the WP's
  `∀ a` is discharged by instantiating at the SOS's chosen `a` — no neutral
  shared needed.
-/

import PyCSL.SOS
import PyCSL.WP
import PyCSL.Soundness

namespace PyCSL

/-! ===== Reserved register keys for lock state and shared state ===== -/

def lockKey (m : Ident) : Ident := "$lock." ++ m
def sharedKey : Ident := "$shared"

def lockFree (es : ExecState) (m : Ident) : Prop :=
  lookup es.regState (lockKey m) = some (.int 0)
def lockHeld (es : ExecState) (m : Ident) : Prop :=
  lookup es.regState (lockKey m) = some (.int 1)
def setLock (es : ExecState) (m : Ident) (v : Int) : ExecState :=
  setReg es (update es.regState (lockKey m) (.int v))
def setShared (es : ExecState) (a : List Int) : ExecState :=
  setReg es (update es.regState sharedKey (.array a))

/-! ===== Concurrent WP for the three constructs ===== -/

def wpCAcquires (m : Ident) (Qn : ExecState → Prop) (es : ExecState) : Prop :=
  lockFree es m ∧ Qn (setLock es m 1)
def wpCReleases (m : Ident) (Qn : ExecState → Prop) (es : ExecState) : Prop :=
  lockHeld es m ∧ Qn (setLock es m 0)
def wpCCritical (body : Stmt)
    (Qn Qr Qc Qb : ExecState → Prop) (Qe : Ident → ExecState → Prop)
    (preEs es : ExecState) : Prop :=
  ∀ a : List Int, wp body Qn Qr Qc Qb Qe preEs (setShared es a)

/-- `wpCCritical` is a concrete instance of the abstract ConcurrentMM havoc
    (`∀ shared, P (mergeShared es shared)`) with `shared = List Int`,
    `mergeShared = setShared`. -/
def concHavoc (es : ExecState) (P : ExecState → Prop) : Prop :=
  ∀ a : List Int, P (setShared es a)

theorem wpCCritical_is_havoc
    (body : Stmt) (Qn Qr Qc Qb : ExecState → Prop) (Qe : Ident → ExecState → Prop)
    (preEs es : ExecState) :
    wpCCritical body Qn Qr Qc Qb Qe preEs es
      = concHavoc es (fun es' => wp body Qn Qr Qc Qb Qe preEs es') := rfl

/-! ===== Concurrent operational semantics (havoc-aware) ===== -/

inductive ExecC : ExecState → Stmt → Outcome → Prop where
  | execCAcquire (es : ExecState) (m : Ident) :
      lockFree es m → ExecC es (.acquires m) (.normal (setLock es m 1))
  | execCRelease (es : ExecState) (m : Ident) :
      lockHeld es m → ExecC es (.releases m) (.normal (setLock es m 0))
  | execCCritical (es : ExecState) (mutex : Ident) (body : Stmt) (a : List Int) (out : Outcome) :
      Exec (setShared es a) body out → ExecC es (.critical mutex body) out

/-! ===== Soundness of the concurrent constructs ===== -/

theorem concSoundAcquires
    (es : ExecState) (m : Ident) (out : Outcome)
    (Qn Qr Qc Qb : ExecState → Prop) (Qe : Ident → ExecState → Prop)
    (hwp : wpCAcquires m Qn es) (hexec : ExecC es (.acquires m) out) :
    outcomePost Qn Qr Qc Qb Qe out := by
  cases hexec
  exact hwp.2

theorem concSoundReleases
    (es : ExecState) (m : Ident) (out : Outcome)
    (Qn Qr Qc Qb : ExecState → Prop) (Qe : Ident → ExecState → Prop)
    (hwp : wpCReleases m Qn es) (hexec : ExecC es (.releases m) out) :
    outcomePost Qn Qr Qc Qb Qe out := by
  cases hexec
  exact hwp.2

/-- The havoc WP is discharged by instantiating at the shared state the SOS
    chose, then reducing to the proved `pycsl_soundness` on the body. NO
    neutral-shared hypothesis is needed. -/
theorem concSoundCritical
    (es : ExecState) (mutex : Ident) (body : Stmt) (out : Outcome)
    (Qn Qr Qc Qb : ExecState → Prop) (Qe : Ident → ExecState → Prop) (preEs : ExecState)
    (hwp : wpCCritical body Qn Qr Qc Qb Qe preEs es)
    (hexec : ExecC es (.critical mutex body) out) :
    outcomePost Qn Qr Qc Qb Qe out := by
  cases hexec
  rename_i a hbody
  exact pycsl_soundness (setShared es a) body out Qn Qr Qc Qb Qe preEs hbody (hwp a)

/-! ===== Lock discipline ===== -/

theorem lockLookupSet (es : ExecState) (m : Ident) (v : Int) :
    lookup (setLock es m v).regState (lockKey m) = some (.int v) := by
  simp [setLock, setReg, lookup, update]

theorem acquireMakesHeld (es : ExecState) (m : Ident) : lockHeld (setLock es m 1) m := by
  unfold lockHeld; exact lockLookupSet es m 1

theorem releaseMakesFree (es : ExecState) (m : Ident) : lockFree (setLock es m 0) m := by
  unfold lockFree; exact lockLookupSet es m 0

theorem lockFreeNotHeld (es : ExecState) (m : Ident) : lockFree es m → ¬ lockHeld es m := by
  intro hf hh; unfold lockFree at hf; unfold lockHeld at hh
  rw [hf] at hh; simp at hh

theorem acquireReleaseRoundtrip (es : ExecState) (m : Ident) :
    lockFree (setLock (setLock es m 1) m 0) m :=
  releaseMakesFree _ _

/-! ===== lock_order well-formedness (deadlock-prevention core) ===== -/

def idxOf : List Ident → Ident → Nat
  | [], _ => 0
  | x :: rest, m => if x == m then 0 else (idxOf rest m) + 1

/-- `orderSorted order held`: `held` is a stack (head = most recent); priorities
    strictly DECREASE down the stack (the head has the highest priority). -/
def orderSorted (order : List Ident) : List Ident → Prop
  | [] => True
  | [_] => True
  | m :: m' :: rest => idxOf order m' < idxOf order m ∧ orderSorted order (m' :: rest)

def acquireRespectsOrder (order held : List Ident) (m : Ident) : Prop :=
  match held with
  | [] => True
  | top :: _ => idxOf order top < idxOf order m

theorem acquirePreservesOrder (order held : List Ident) (m : Ident)
    (hs : orderSorted order held) (hr : acquireRespectsOrder order held m) :
    orderSorted order (m :: held) := by
  cases held with
  | nil => trivial
  | cons top rest =>
    simp only [acquireRespectsOrder] at hr
    exact ⟨hr, hs⟩

end PyCSL
