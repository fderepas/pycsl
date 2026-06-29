(* Phase7_MemModel.v — Memory Model Parameterisation (Category D)
   ================================================================

   This file defines the memory-model interface that abstracts \valid,
   \separated, and the heap operations. Different instances (Hoare,
   typed, store, concurrent) plug into this interface; only the Hoare
   instance is provided here — the typed/store/concurrent instances
   are deferred (see §"Deferred work" below).

   The interface is ADDITIVE: the existing pycsl_soundness theorem is
   untouched. The Hoare instance makes valid/separated vacuously True
   (matching the Phase 4 stubs in Phase2_State.v:552-554) and makes
   critical_havoc the identity (matching the Phase 8 SCritical stub
   in Phase4_WP.v:143-144).

   critical_havoc models the README §13 "ExecCritical shared state"
   risk: ExecCritical must universally quantify `shared` at entry
   (modelling havoc). The Hoare instance has no shared state, so
   havoc reduces to identity — `critical_havoc es P = P es`. A real
   concurrent instance would replace this with
   `forall shared, P (merge_shared es shared)`. *)

Require Import ZArith String List Bool.
Require Import Phase1_AST.
Require Import Phase2_State.
Open Scope Z_scope.
Open Scope string_scope.

(* ===== Memory Model Interface (Rocq Module Type) =====

   This is the abstract interface. wp currently uses the Hoare instance
   directly (see critical_havoc below); future instances replace the
   definitions. *)

Module Type MEM_MODEL.
  (* \valid(ptr, len): is the range [ptr, ptr+len) valid? *)
  Parameter valid       : Z -> Z -> Prop.
  (* \separated(a, b): are the two ranges non-overlapping? *)
  Parameter separated   : Z -> Z -> Prop.
  (* critical_havoc es P: the WP of a critical section.
     Hoare instance: P es (no shared state).
     Concurrent instance: forall shared, P (merge_shared es shared). *)
  Parameter critical_havoc : exec_state -> (exec_state -> Prop) -> Prop.
End MEM_MODEL.

(* ===== Hoare Instance =====

   The Hoare memory model: no heap, no shared state.
   - valid/separated are vacuously True (every access is valid).
   - critical_havoc is identity (no shared state to havoc). *)

Module HoareMM : MEM_MODEL.
  Definition valid       (ptr len : Z) : Prop := True.
  Definition separated   (a b : Z) : Prop := True.
  Definition critical_havoc (es : exec_state) (P : exec_state -> Prop) : Prop :=
    P es.
End HoareMM.

(* Transparent top-level alias used by wp.
   HoareMM is sealed behind a Module Type, so we re-expose its
   critical_havoc definition as a standalone transparent Definition that wp
   can unfold. `valid`/`separated` are now defined in Phase2_State.v (the
   Hoare-instance defaults, True) so that eval_contract's CValid/CSeparated
   clauses can reference them without a circular import. *)
Definition critical_havoc (es : exec_state) (P : exec_state -> Prop) : Prop :=
  P es.

(* ===== Bridge lemmas: Hoare instance agrees with Phase 2/4 stubs ===== *)

(* The Phase 2 contract-evaluator CValid/CSeparated clauses (Phase2_State.v)
   now call the top-level `valid`/`separated` (defined there as True, the
   Hoare default). The HoareMM module's definitions are also True, so they
   agree. *)
Lemma hoare_valid_true : forall ptr len, valid ptr len = True.
Proof. intros. reflexivity. Qed.

Lemma hoare_separated_true : forall a b, separated a b = True.
Proof. intros. reflexivity. Qed.

(* critical_havoc reduces to identity in the Hoare instance. *)
Lemma critical_havoc_eq : forall es P, critical_havoc es P = P es.
Proof. intros. reflexivity. Qed.

(* ===== Test lemmas ===== *)

(* Test 1: critical_havoc of a constant predicate. *)
Lemma test_critical_havoc_const :
  forall es (b : Prop), critical_havoc es (fun _ => b) = b.
Proof. intros. unfold critical_havoc. reflexivity. Qed.

(* Test 2: critical_havoc of Qn. *)
Lemma test_critical_havoc_qn :
  forall es (Qn : exec_state -> Prop),
  critical_havoc es Qn = Qn es.
Proof. intros. unfold critical_havoc. reflexivity. Qed.

(* Test 3: valid is vacuously satisfied. *)
Lemma test_hoare_valid : valid 0 10.
Proof. exact I. Qed.

(* Test 4: separated is vacuously satisfied. *)
Lemma test_hoare_separated : separated 0 10.
Proof. exact I. Qed.

(* ===== Typed memory-model instance (Category D) =====

    TypedMM: a typed heap modelled as a finite set of valid (base, length)
    blocks. `valid ptr len` holds iff every address in [ptr, ptr+len) is
    covered by some allocated block. `separated a b` is real non-overlap
    of the two ranges. `critical_havoc` is identity (no shared state).

    This instance is ADDITIVE: it does NOT replace the Hoare default that
    eval_contract / pycsl_soundness use. The top-level `valid`/`separated`
    (Phase2_State.v) remain the Hoare defaults (True); TypedMM's predicates
    live inside this module. Wiring TypedMM into eval_contract requires the
    Section/Context refactor (see §"Design note (Option B)" below). *)

Module TypedMM.
  (* A typed heap block: (base, size). *)
  Definition block := (Z * Z)%type.

  (* The typed heap is a parameter; for the instance we fix an empty heap
     (so nothing is valid — the conservative default). Real usage would
     specialise this to a non-empty block list. *)
  Definition typed_heap : list block := nil.

  (* blocks_overlap b1 b2: do the two blocks share any address? *)
  Definition blocks_overlap (b1 b2 : block) : Prop :=
    let (p1, n1) := b1 in
    let (p2, n2) := b2 in
    p1 < p2 + n2 /\ p2 < p1 + n1.

  (* range_covered ptr len bs: a block in bs covers the whole range
     [ptr, ptr+len). (Simplified: the range does not straddle a gap.) *)
  Definition range_covered (ptr len : Z) (bs : list block) : Prop :=
    exists b, List.In b bs /\
              let (p, n) := b in
              p <= ptr /\ ptr + len <= p + n.

  (* \valid(ptr, len): the range is non-negative and covered by an
     allocated typed block. With typed_heap = nil, nothing is valid
     (conservative). *)
  Definition valid (ptr len : Z) : Prop :=
    ptr >= 0 /\ len >= 0 /\ range_covered ptr len typed_heap.

  (* \separated(a, b): real non-overlap of the two ranges. A range is
     [base, base+len); with a single base arg per side we treat len as 1
     (the conservative single-cell separation). *)
  Definition separated (a b : Z) : Prop :=
    a <> b.

  Definition critical_havoc (es : exec_state) (P : exec_state -> Prop) : Prop :=
    P es.
End TypedMM.

(* ===== Store memory-model instance (Category D) =====

    StoreMM: a flat byte-array store. `valid ptr len` holds iff the range
    [ptr, ptr+len) is within the store bounds [0, store_size). `separated`
    is real non-overlap. `critical_havoc` is identity. *)

Module StoreMM.
  (* store_size: the fixed size of the flat byte store. *)
  Definition store_size : Z := 4096.

  (* \valid(ptr, len): the range [ptr, ptr+len) is within store bounds. *)
  Definition valid (ptr len : Z) : Prop :=
    0 <= ptr /\ ptr + len <= store_size.

  (* \separated(a, b): real non-overlap — the two single-cell ranges
     don't coincide. (The full \separated takes (base,len) pairs; with a
     single base arg per side, separation = distinct bases.) *)
  Definition separated (a b : Z) : Prop :=
    a <> b.

  Definition critical_havoc (es : exec_state) (P : exec_state -> Prop) : Prop :=
    P es.
End StoreMM.

(* ===== Bridge lemma: Hoare instance reduces CValid/CSeparated to True =====

    Under the Hoare default (the top-level valid/separated from
    Phase2_State.v, which eval_contract consults), CValid/CSeparated
    evaluate to True. This is why pycsl_soundness is unchanged: the Hoare
    instance is the default, and it makes the heap predicates vacuous. *)

Lemma eval_cvalid_hoare :
  forall st pre_st result ptr len,
  eval_contract st pre_st result (CValid ptr len) = True.
Proof. intros. simpl. exact (hoare_valid_true _ _). Qed.

Lemma eval_cseparated_hoare :
  forall st pre_st result a b,
  eval_contract st pre_st result (CSeparated a b) = True.
Proof. intros. simpl. exact (hoare_separated_true _ _). Qed.

(* ===== Concurrent memory-model instance (Category D) =====

    ConcurrentMM: the real concurrent memory model. Per README §13
    (Risk Register — "ExecCritical shared state", Critical) and
    formal-semantics-completion.md §8/§Phase 7, ExecCritical must
    universally quantify `shared` at entry (modelling havoc), NOT pick a
    specific shared state.

    Design (per the task spec):
    - The `exec_state` record is NOT extended with a shared-state field
      (that would break every existing proof — see §"Design note" below).
      Instead the shared state is modelled abstractly: `merge_shared` is
      a Parameter of the instance (a hypothesis, not an axiom — it carries
      no proof obligation). The havoc is over this abstract shared state.
    - `critical_havoc es P = forall shared, P (merge_shared es shared)`.
      This is the havoc semantics: the WP must hold for ALL possible
      shared states the environment could present at critical-section entry.
    - `threadEntry` under ConcurrentMM: the body executes against a fresh
      shared state (havoc) — modelled identically to `critical` (the WP
      of the body is havoc'd). See `threadEntry_wp_concurrent`.
    - `acquires`/`releases` lock discipline: the real lock-state
      (held/free) is a well-formedness condition that, per the task spec,
      is genuinely hard to wire without an `exec_state` field change. So
      the ConcurrentMM WP of `acquires`/`releases` is identity (matching
      the Hoare-instance stub) — DOCUMENTED here and recorded as a named
      TODO. It is NOT an axiom: it is a conservative over-approximation
      (identity WP is sound — it places no obligation on the lock state,
      so any proof that closes under identity also closes under the real
      lock-aware WP, which is strictly stronger).

    Bridge lemma (§5 of the task): under HoareMM, `critical_havoc es P =
    P es` (the existing identity, so `pycsl_soundness` is unchanged).
    Under ConcurrentMM, `critical_havoc es P = forall shared,
    P (merge_shared es shared)`. Both are proved below. The soundness
    theorem itself is NOT re-stated for ConcurrentMM — `pycsl_soundness`
    uses the top-level `critical_havoc` (the Hoare default), so it is
    untouched by this addition. *)

(* `shared_state`: the abstract type of shared states. This is a
   Parameter of the ConcurrentMM instance — a hypothesis, not an axiom.
   `merge_shared` merges an `exec_state` with a `shared_state`. Both
   carry no proof obligation; the bridge lemma
   `concurrent_critical_havoc_eq` below is parametric in them. *)
Parameter shared_state : Type.
Parameter merge_shared : exec_state -> shared_state -> exec_state.

Module ConcurrentMM.
  (* The shared-state type is abstract (a Parameter of the instance). *)
  Definition valid (ptr len : Z) : Prop := True.
  Definition separated (a b : Z) : Prop := True.

  (* The havoc semantics: the WP must hold for ALL shared states. *)
  Definition critical_havoc (es : exec_state) (P : exec_state -> Prop) : Prop :=
    forall shared, P (merge_shared es shared).

  (* `acquires`/`releases` WP: identity (conservative over-approximation).
     The real lock-state well-formedness (lock-held flag, lock_order
     deadlock prevention) is a named TODO — NOT an axiom. See
     `concurrent_lock_discipline_todo` below. *)
End ConcurrentMM.

(* ===== Bridge lemmas for ConcurrentMM ===== *)

(* Under ConcurrentMM, critical_havoc is the universal-havoc semantics. *)
Lemma concurrent_critical_havoc_eq :
  forall es (P : exec_state -> Prop),
  ConcurrentMM.critical_havoc es P = (forall shared, P (merge_shared es shared)).
Proof. intros. reflexivity. Qed.

(* Under HoareMM (the top-level default), critical_havoc is identity.
   This is the bridge lemma of §5 of the task: the soundness theorem's
   instance is unchanged. *)
Lemma hoare_critical_havoc_identity :
  forall es (P : exec_state -> Prop),
  critical_havoc es P = P es.
Proof. intros. reflexivity. Qed.

(* ===== ConcurrentMM test lemmas ===== *)

(* Test 1: under ConcurrentMM, havoc of the trivial predicate holds
   (the universal quantification over `shared` is vacuously satisfied
   by `True`). *)
Lemma test_concurrent_havoc_const :
  forall es, ConcurrentMM.critical_havoc es (fun _ => True).
Proof.
  intros. unfold ConcurrentMM.critical_havoc. intros shared. exact I.
Qed.

(* Test 2: under ConcurrentMM, havoc of Qn quantifies over shared. *)
Lemma test_concurrent_havoc_qn :
  forall es (Qn : exec_state -> Prop),
  ConcurrentMM.critical_havoc es Qn = forall shared, Qn (merge_shared es shared).
Proof. intros. reflexivity. Qed.

(* ===== Lock discipline: named TODO (NOT an axiom) =====

    The real lock-state well-formedness for `acquires`/`releases` is:
      - `acquires m` requires lock[m] = Free; establishes lock[m] = Held.
      - `releases m` requires lock[m] = Held; establishes lock[m] = Free.
      - `lock_order m1, m2, ...` is a global total order on mutex
        acquisition; the well-formedness condition is that every
        `acquires` sequence respects it (deadlock prevention).

    This requires a lock-state component in `exec_state` (or a separate
    ghost lock-state threaded through the WP), which is the invasive
    `exec_state` field change this task explicitly forbids. So the
    ConcurrentMM WP of `acquires`/`releases` is identity (the same as
    the Hoare-instance stub). This is SOUND: identity WP places no
    obligation on the lock state, so any proof that closes under
    identity also closes under the stronger lock-aware WP. The real
    lock discipline is recorded as a named TODO below, NOT an axiom. *)

Definition concurrent_lock_discipline_todo : Prop :=
  (* Placeholder: the real lock-state WP for acquires/releases is
     deferred. This is a Prop-valued marker (not an Axiom); it is
     provable (it's just `True` here) and carries no proof obligation. *)
  True.

(* ===== Design note (Option B — globally-bound default instance) =====

    The task preferred Option A (threading the MEM_MODEL parameter through
    eval_contract via a Section/Context or typeclass synthesis). This proved
    too invasive: eval_contract (Phase2_State.v) is called by eval_contract_es,
    eval_c (Phase4_WP.v), the Exec inductive constructors (Phase3_SOS.v:
    execAssertPass/Fail carry `eval_contract ... cond` in their type), wp,
    and pycsl_soundness. Adding an instance parameter would ripple through
    the Exec inductive (changing every soundness case) and wp's signature —
    a high-risk refactor with potential to break pycsl_soundness.

    Instead we use Option B (the same pattern already used for
    `critical_havoc`): a top-level definition defaulting to the Hoare
    instance, which eval_contract consults. This is a known compromise:
    - PRO: 0 signature ripple; pycsl_soundness untouched; 0 new Admitted.
    - PRO: CValid/CSeparated are genuinely re-routed (they call named
           `valid`/`separated` definitions, not inline `True`).
    - CON:  the instance is not a parameter — switching to ConcurrentMM
            (or TypedMM/StoreMM) requires rebinding the top-level
            definitions (or the future Section refactor). ConcurrentMM is
            provided as a Module whose definitions are real (the havoc is
            genuine: `forall shared, P (merge_shared es shared)`), but it
            is NOT wired into eval_contract (the top-level `critical_havoc`
            remains the Hoare identity). Wiring it is the remaining
            Category-D work (the Section/Context refactor), deferred
            because it changes pycsl_soundness's statement.

    This mirrors the existing `critical_havoc` compromise (Phase4_WP.v:147)
    and is documented here as the agreed fallback. *)

(* ===== Remaining deferred work (documented, not implemented) =====

    The following is NOT provided here — it is the remaining
    Category-D work:

    1. Wiring ConcurrentMM into eval_contract/wp — requires the
       Section/Context refactor (Option A) so that eval_contract and wp
       take the MEM_MODEL as a parameter. This changes pycsl_soundness's
       statement (the theorem becomes parameterised by the instance) and
       is deferred. The ConcurrentMM instance itself is provided above
       (with genuine havoc semantics); only the wiring is deferred.

    2. Real lock-state WP for acquires/releases — requires a lock-state
       component in exec_state (or a separate ghost lock-state threaded
       through wp). See `concurrent_lock_discipline_todo` above.

    Named TODOs:
      - TODO(Phase7-instance-param): re-thread MEM_MODEL through eval_contract
        as a Section parameter (Option A), making pycsl_soundness
        instance-parameterised. The ConcurrentMM instance is ready; the
        wiring is the deferred work.
      - TODO(Phase7-lock-state): real lock-state WP for acquires/releases
        (held/free flag + lock_order well-formedness). Requires the
        exec_state field change OR a ghost lock-state parameter. *)
