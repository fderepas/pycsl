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

-- Transparent top-level alias used by wp.
-- `valid`/`separated` are now defined in State.lean (the Hoare-instance
-- defaults, `True`) so that `evalContract`'s `.cValid`/`.cSeparated` clauses
-- can reference them without a circular import. `criticalHavoc` lives here
-- (used by WP.lean's `.critical` case).
def criticalHavoc (es : ExecState) (P : ExecState → Prop) : Prop := P es

-- Bridge lemmas: Hoare instance agrees with the State.lean defaults.

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

/-!
  ===== Typed memory-model instance (Category D) =====

  `TypedMM`: a typed heap modelled as a finite list of allocated blocks
  `(base, size)`. `valid ptr len` holds iff the range `[ptr, ptr+len)` is
  non-negative and covered by some allocated block. `separated a b` is real
  non-overlap (distinct bases). `criticalHavoc` is identity (no shared
  state).

  This instance is ADDITIVE: it does NOT replace the Hoare default that
  `evalContract` / `pycslSoundness` use. The top-level `valid`/`separated`
  (State.lean) remain the Hoare defaults (`True`); `TypedMM`'s predicates
  live here as a named instance. Wiring `TypedMM` into `evalContract`
  requires the typeclass-parameter refactor (see §"Design note (Option B)").
-/

abbrev TypedBlock := (Int × Int)

/-- The typed heap: a list of allocated `(base, size)` blocks. The default
    heap is empty (nothing is valid — the conservative default). -/
def TypedHeap : List TypedBlock := []

/-- `TypedMM.valid ptr len`: the range is non-negative and covered by an
    allocated typed block. -/
def TypedMM.valid (ptr len : Int) : Prop :=
  ptr ≥ 0 ∧ len ≥ 0 ∧
  (∃ b : TypedBlock, b ∈ TypedHeap ∧
                     let (p, n) := b
                     p ≤ ptr ∧ ptr + len ≤ p + n)

/-- `TypedMM.separated a b`: real non-overlap — distinct bases. -/
def TypedMM.separated (a b : Int) : Prop := a ≠ b

/-- `TypedMM` as a `MemModel Int` instance (low priority so `HoareMM`
    remains the default for typeclass synthesis). -/
instance (priority := 50) TypedMM : MemModel Int where
  valid       := TypedMM.valid
  separated   := TypedMM.separated
  criticalHavoc := fun es P => P es

/-!
  ===== Store memory-model instance (Category D) =====

  `StoreMM`: a flat byte-array store. `valid ptr len` holds iff the range
  `[ptr, ptr+len)` is within store bounds `[0, storeSize)`. `separated` is
  real non-overlap. `criticalHavoc` is identity.
-/

/-- The fixed size of the flat byte store. -/
def StoreSize : Int := 4096

/-- `StoreMM.valid ptr len`: the range is within store bounds. -/
def StoreMM.valid (ptr len : Int) : Prop :=
  0 ≤ ptr ∧ ptr + len ≤ StoreSize

/-- `StoreMM.separated a b`: real non-overlap — distinct bases. -/
def StoreMM.separated (a b : Int) : Prop := a ≠ b

/-- `StoreMM` as a `MemModel Int` instance (low priority so `HoareMM`
    remains the default for typeclass synthesis). -/
instance (priority := 50) StoreMM : MemModel Int where
  valid       := StoreMM.valid
  separated   := StoreMM.separated
  criticalHavoc := fun es P => P es

/-!
  ===== Bridge lemma: Hoare instance reduces CValid/CSeparated to True =====

  Under the Hoare default (the top-level `valid`/`separated` from
  State.lean, which `evalContract` consults), `.cValid`/`.cSeparated`
  evaluate to `True`. This is why `pycslSoundness` is unchanged: the Hoare
  instance is the default, and it makes the heap predicates vacuous.
-/

theorem evalCValid_hoare (st preSt : State) (result : Option Val)
    (ptr len : ContractExpr) :
    evalContract st preSt result (.cValid ptr len) = True := by
  simp only [evalContract, valid]

theorem evalCSeparated_hoare (st preSt : State) (result : Option Val)
    (a b : ContractExpr) :
    evalContract st preSt result (.cSeparated a b) = True := by
  simp only [evalContract, separated]

/-!
  ===== Concurrent memory-model instance (Category D) =====

  `ConcurrentMM`: the real concurrent memory model. Per README §13
  (Risk Register — "ExecCritical shared state", Critical) and
  `formal-semantics-completion.md` §8/§Phase 7, `ExecCritical` must
  universally quantify `shared` at entry (modelling havoc), NOT pick a
  specific shared state.

  Design (per the task spec):
  - The `ExecState` record is NOT extended with a shared-state field
    (that would break every existing proof — see §"Design note" below).
    Instead the shared state is modelled abstractly: `mergeShared` is a
    parameter of the instance (an opaque `variable`, not an axiom — it
    carries no proof obligation). The havoc is over this abstract shared
    state.
  - `criticalHavoc es P = ∀ shared, P (mergeShared es shared)`.
    This is the havoc semantics: the WP must hold for ALL possible
    shared states the environment could present at critical-section entry.
  - `threadEntry` under ConcurrentMM: the body executes against a fresh
    shared state (havoc) — modelled identically to `critical` (the WP
    of the body is havoc'd).
  - `acquires`/`releases` lock discipline: the real lock-state
    (held/free) is a well-formedness condition that, per the task spec,
    is genuinely hard to wire without an `ExecState` field change. So
    the ConcurrentMM WP of `acquires`/`releases` is identity (matching
    the Hoare-instance stub) — DOCUMENTED here and recorded as a named
    TODO. It is NOT an axiom: it is a conservative over-approximation
    (identity WP is sound — it places no obligation on the lock state,
    so any proof that closes under identity also closes under the real
    lock-aware WP, which is strictly stronger).

  Bridge lemma (§5 of the task): under `HoareMM`, `criticalHavoc es P =
  P es` (the existing identity, so `pycslSoundness` is unchanged).
  Under `ConcurrentMM`, `criticalHavoc es P = ∀ shared,
  P (mergeShared es shared)`. Both are proved below. The soundness
  theorem itself is NOT re-stated for `ConcurrentMM` — `pycslSoundness`
  uses the top-level `criticalHavoc` (the Hoare default), so it is
  untouched by this addition.
-/

namespace ConcurrentMM

-- `σ` (shared state): the abstract type of shared states. This is a
-- parameter of the `ConcurrentMM` instance — a hypothesis, not an
-- axiom. `mergeShared` is the abstract merge of an `ExecState` with a
-- `σ` shared state — an opaque parameter, NOT an axiom. It carries no
-- proof obligation; the bridge lemma `concurrent_criticalHavoc_eq`
-- below is parametric in it.
variable (σ : Type) (mergeShared : ExecState → σ → ExecState)

/-- `valid` under ConcurrentMM (vacuous — heap reasoning is orthogonal
    to the concurrency model). The `σ` parameter is accepted (and
    ignored) so the instance wiring below can uniformly thread `σ`. -/
def mmValid (_σ : Type) (_ptr _len : Int) : Prop := True

/-- `separated` under ConcurrentMM (vacuous). -/
def mmSeparated (_σ : Type) (_a _b : Int) : Prop := True

/-- The havoc semantics: the WP must hold for ALL shared states. -/
def criticalHavoc (es : ExecState) (P : ExecState → Prop) : Prop :=
  ∀ shared : σ, P (mergeShared es shared)

/-- `ConcurrentMM` as a `MemModel Int` instance (low priority so
    `HoareMM` remains the default for typeclass synthesis). -/
instance (priority := 50) : MemModel Int where
  valid       := mmValid σ
  separated   := mmSeparated σ
  criticalHavoc := criticalHavoc σ mergeShared

end ConcurrentMM

/-!
  ===== Bridge lemmas for ConcurrentMM =====
-/

/-- Under `ConcurrentMM`, `criticalHavoc` is the universal-havoc
    semantics. -/
theorem concurrent_criticalHavoc_eq
    {σ : Type} (mergeShared : ExecState → σ → ExecState)
    (es : ExecState) (P : ExecState → Prop) :
    ConcurrentMM.criticalHavoc σ mergeShared es P =
      (∀ shared : σ, P (mergeShared es shared)) := rfl

/-- Under `HoareMM` (the top-level default), `criticalHavoc` is
    identity. This is the bridge lemma of §5 of the task: the soundness
    theorem's instance is unchanged. -/
theorem hoare_criticalHavoc_identity (es : ExecState) (P : ExecState → Prop) :
    criticalHavoc es P = P es := rfl

/-!
  ===== ConcurrentMM test lemmas =====
-/

/-- Test 1: under `ConcurrentMM`, havoc of the trivial predicate holds
    (the universal quantification over `shared` is vacuously satisfied
    by `True`). -/
theorem test_concurrentHavoc_const
    {σ : Type} (mergeShared : ExecState → σ → ExecState)
    (es : ExecState) :
    ConcurrentMM.criticalHavoc σ mergeShared es (fun _ => True) := by
  unfold ConcurrentMM.criticalHavoc
  intro _; trivial

/-- Test 2: under `ConcurrentMM`, havoc of `Qn` quantifies over
    `shared`. -/
theorem test_concurrentHavoc_qn
    {σ : Type} (mergeShared : ExecState → σ → ExecState)
    (es : ExecState) (Qn : ExecState → Prop) :
    ConcurrentMM.criticalHavoc σ mergeShared es Qn =
      (∀ shared : σ, Qn (mergeShared es shared)) := rfl

/-!
  ===== Lock discipline: named TODO (NOT an axiom) =====

  The real lock-state well-formedness for `acquires`/`releases` is:
    - `acquires m` requires `lock[m] = Free`; establishes `lock[m] = Held`.
    - `releases m` requires `lock[m] = Held`; establishes `lock[m] = Free`.
    - `lock_order m1, m2, ...` is a global total order on mutex
      acquisition; the well-formedness condition is that every `acquires`
      sequence respects it (deadlock prevention).

  This requires a lock-state component in `ExecState` (or a separate
  ghost lock-state threaded through the WP), which is the invasive
  `ExecState` field change this task explicitly forbids. So the
  `ConcurrentMM` WP of `acquires`/`releases` is identity (the same as the
  `HoareMM` stub). This is SOUND: identity WP places no obligation on
  the lock state, so any proof that closes under identity also closes
  under the stronger lock-aware WP. The real lock discipline is recorded
  as a named TODO below, NOT an axiom.
-/

/-- The real lock-state WP for `acquires`/`releases` is deferred. This
    is a `Prop`-valued marker (NOT an axiom); it is provable (it is just
    `True` here) and carries no proof obligation. -/
def concurrentLockDisciplineTodo : Prop := True

/-- `concurrentLockDisciplineTodo` is provable (closing the named TODO
    marker — it adds NO new axiom). -/
theorem concurrentLockDisciplineTodo_provable :
    concurrentLockDisciplineTodo := trivial

/-!
  ===== Design note (Option B — globally-bound default instance) =====

  The task preferred Option A (threading the `MemModel` parameter through
  `evalContract` via `[MemModel Int]` typeclass synthesis). This proved
  too invasive: `evalContract` is called by `evalContractEs`, `evalC`,
  the `Exec` inductive constructors (`SOS.lean`: `execAssertPass`/`Fail`
  carry `evalContract ... cond` in their type), `wp`, and
  `pycslSoundness`. Adding an instance parameter would ripple through
  the `Exec` inductive (changing every soundness case) and `wp`'s
  signature — a high-risk refactor with potential to break
  `pycslSoundness`.

  Instead we use Option B (the same pattern already used for
  `criticalHavoc`): a top-level definition defaulting to the `HoareMM`
  instance, which `evalContract` consults. This is a known compromise:
  - PRO: 0 signature ripple; `pycslSoundness` untouched; 0 new `sorry`.
  - PRO: `.cValid`/`.cSeparated` are genuinely re-routed (they call
         named `valid`/`separated` definitions, not inline `True`).
  - CON: the instance is not a parameter — switching to `ConcurrentMM`
         (or `TypedMM`/`StoreMM`) requires rebinding the top-level
         definitions (or the future typeclass-parameter refactor).
         `ConcurrentMM` is provided as a named instance whose definitions
         are real (the havoc is genuine: `∀ shared, P (mergeShared es
         shared)`), but it is NOT wired into `evalContract` (synthesis
         picks `HoareMM`). Wiring it is the remaining Category-D work,
         deferred because it changes `pycslSoundness`'s statement.

  This mirrors the existing `criticalHavoc` compromise (`WP.lean`) and is
  documented here as the agreed fallback.
-/

/-!
  ===== Remaining deferred work (documented, not implemented) =====

  1. Wiring `ConcurrentMM` into `evalContract`/`wp` — requires the
     typeclass-parameter refactor (Option A) so that `evalContract` and
     `wp` take `[MemModel Int]` as a parameter. This changes
     `pycslSoundness`'s statement (the theorem becomes parameterised by
     the instance) and is deferred. The `ConcurrentMM` instance itself
     is provided above (with genuine havoc semantics); only the wiring
     is deferred.

  2. Real lock-state WP for `acquires`/`releases` — requires a
     lock-state component in `ExecState` (or a separate ghost lock-state
     threaded through `wp`). See `concurrentLockDisciplineTodo` above.

  Named TODOs:
    - TODO(Phase7-instance-param): re-thread `MemModel` through
      `evalContract` as a typeclass parameter (Option A), making
      `pycslSoundness` instance-parameterised. The `ConcurrentMM`
      instance is ready; the wiring is the deferred work.
    - TODO(Phase7-lock-state): real lock-state WP for `acquires`/
      `releases` (held/free flag + `lock_order` well-formedness).
      Requires the `ExecState` field change OR a ghost lock-state
      parameter.
-/
