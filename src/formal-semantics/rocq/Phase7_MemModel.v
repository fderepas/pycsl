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
    - CON:  the instance is not a parameter — switching to TypedMM/StoreMM
            requires rebinding the top-level definitions (or the future
            Section refactor). TypedMM/StoreMM are provided as Modules
            whose definitions are real, but they are NOT wired into
            eval_contract. Wiring them is the remaining Category-D work
            (the Section/Context refactor), deferred because it changes
            pycsl_soundness's statement.

    This mirrors the existing `critical_havoc` compromise (Phase4_WP.v:147)
    and is documented here as the agreed fallback. *)

(* ===== Remaining deferred work (documented, not implemented) =====

   The following instances are NOT provided here — they are the
   remaining Category-D work:

   1. ConcurrentMM — real concurrent model: critical_havoc becomes
                      forall shared, P (merge_shared es shared);
                      acquires/releases gain real lock-state;
                      threadEntry spawns with a fresh shared state.

   2. Wiring TypedMM/StoreMM into eval_contract — requires the
      Section/Context refactor (Option A) so that eval_contract takes the
      MEM_MODEL as a parameter. This changes pycsl_soundness's statement
      (the theorem becomes parameterised by the instance) and is deferred.

   Named TODOs:
     - TODO(Phase7-concurrent): ConcurrentMM instance with real havoc
       (forall shared, P (merge_shared es shared)) and lock-state for
       acquires/releases.
     - TODO(Phase7-instance-param): re-thread MEM_MODEL through eval_contract
       as a Section parameter (Option A), making pycsl_soundness
       instance-parameterised. *)
