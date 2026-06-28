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

(* Transparent top-level aliases used by wp.
   HoareMM is sealed behind a Module Type, so we re-expose its
   definitions as standalone transparent Definitions that wp can unfold. *)
Definition valid (ptr len : Z) : Prop := True.
Definition separated (a b : Z) : Prop := True.
Definition critical_havoc (es : exec_state) (P : exec_state -> Prop) : Prop :=
  P es.

(* ===== Bridge lemmas: Hoare instance agrees with Phase 4 stubs ===== *)

(* The Phase 4 contract-evaluator stubs (Phase2_State.v:552-554) model
   CValid/CSeparated/CValid2d as True. The Hoare instance's valid/
   separated are also True, so they agree. *)

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

(* ===== Deferred work (documented, not implemented) =====

   The following instances are NOT provided here — they are the
   remaining Category-D work:

   1. TypedMM  — heap with typed cells; valid(ptr,len) checks the
                 heap contains a typed block at ptr of size >= len.
   2. StoreMM  — single-heap model with store semantics.
   3. ConcurrentMM — real concurrent model: critical_havoc becomes
                     forall shared, P (merge_shared es shared);
                     acquires/releases gain real lock-state;
                     threadEntry spawns with a fresh shared state.

   These require threading the MEM_MODEL parameter through eval_contract,
   exec, and wp — an architectural change. The current additive design
   hardcodes the Hoare instance in critical_havoc (used by wp's SCritical
   case) and leaves eval_contract's CValid/CSeparated stubs as True
   (matching HoareMM). Switching instances requires:
     - re-proving pycsl_soundness against the new instance's
       critical_havoc (the SCritical soundness case changes);
     - re-routing eval_contract's CValid/CSeparated clauses through the
       instance's valid/separated.

   Named TODOs:
     - TODO(Phase7-typed): TypedMM instance with real \valid.
     - TODO(Phase7-store): StoreMM instance with real \separated.
     - TODO(Phase7-concurrent): ConcurrentMM instance with real havoc
       (forall shared, P (merge_shared es shared)) and lock-state for
       acquires/releases. *)
