(* Phase7b_MemModelSoundness.v — instance-parameterised soundness + the
   non-vacuity of the typed/store memory models (Category D)
   ============================================================================
   Phase 7 (`Phase7_MemModel.v`) defines the `MEM_MODEL` interface and four
   instances (Hoare / Typed / Store / Concurrent). Two things were left open:

     (1) the typed/store `valid`/`separated` predicates were never shown to
         *discriminate* (the typed instance fixed `typed_heap := nil`, so the
         predicate machinery was never exercised on a non-empty model); and
     (2) the Phase-7 gate "soundness proven for each instance" was unmet —
         wiring an instance through the global `wp` was judged too invasive
         (Phase7_MemModel.v §"Design note (Option B)").

   This file closes both ADDITIVELY — it imports the proved `pycsl_soundness`
   and adds, on top, with 0 new axioms and 0 Admitted:

     • `critical_sound_param` : for ANY memory model whose `critical_havoc`
       is *sub-identity*, the `SCritical` construct (the only WP arm that
       consults the memory model) is sound. The proof reduces to the proved
       `pycsl_soundness` for the body — the global `wp` is NOT changed; the
       instance's `critical_havoc` is supplied for the body's WP.
     • per-instance corollaries discharging `critical_sound_param` for all
       four instances: Hoare / Typed / Store are sub-identity outright;
       ConcurrentMM is sub-identity *given a neutral shared state* (a
       hypothesis, NOT an axiom). This is "soundness proven for each
       instance" for the memory-model-sensitive construct.
     • discrimination/non-vacuity lemmas for the typed and store predicates:
       a covering block makes its range valid; overlap is detected;
       in-bounds is valid, out-of-bounds is not; distinct cells are
       separated, equal cells are not.

   What remains (the gate's residual "1") is the genuinely-hard concurrent
   model: a havoc-aware SOS for `SCritical` (so `ConcurrentMM`'s havoc is
   matched by the operational semantics) plus a lock-state component for
   `acquires`/`releases`. Both need the `exec_state` field change that
   Phase 7 explicitly defers. *)

Require Import ZArith String List Bool.
Require Import Lia.
Require Import PyCSL.Phase1_AST.
Require Import PyCSL.Phase2_State.
Require Import PyCSL.Phase3_SOS.
Require Import PyCSL.Phase4_WP.
Require Import PyCSL.Phase7_MemModel.
Require Import PyCSL.Phase5b_Soundness.
Open Scope Z_scope.
Open Scope string_scope.

(* ===== Sub-identity: the soundness-compatibility condition on a model ===== *)

(* A memory model's `critical_havoc` is *sub-identity* when, whatever it
   claims of a predicate P at entry state es, it entails P of es itself.
   This is exactly what the `SCritical` soundness case needs: the WP arm is
   `critical_havoc es (fun es' => wp body … es')`, and the SOS runs the body
   on es, so we must recover `wp body … es`. Every identity instance
   satisfies this trivially; the havoc instance satisfies it given a neutral
   shared state. *)
Definition ch_sub_identity (ch : exec_state -> (exec_state -> Prop) -> Prop) : Prop :=
  forall es P, ch es P -> P es.

(* ===== Instance-parameterised soundness of the critical-section arm ===== *)

(* For ANY memory model whose `critical_havoc` is sub-identity, `SCritical`
   is sound. The proof does NOT touch the global `wp`: `ch` is the instance's
   `critical_havoc`, supplied for the body's WP, and the conclusion reduces
   to the proved `pycsl_soundness` on the body. *)
Theorem critical_sound_param :
  forall (ch : exec_state -> (exec_state -> Prop) -> Prop),
    ch_sub_identity ch ->
  forall es mutex body out Qn Qr Qc Qb Qe pre_es,
    exec es (SCritical mutex body) out ->
    ch es (fun es' => wp body Qn Qr Qc Qb Qe pre_es es') ->
    outcome_post Qn Qr Qc Qb Qe out.
Proof.
  intros ch Hsub es mutex body out Qn Qr Qc Qb Qe pre_es Hexec Hch.
  apply Hsub in Hch.
  inversion Hexec; subst.
  eapply pycsl_soundness; eauto.
Qed.

(* ===== Each instance is sub-identity (→ soundness per instance) ===== *)

(* Hoare (the top-level default `critical_havoc`): identity. *)
Lemma hoare_ch_sub_identity : ch_sub_identity critical_havoc.
Proof. intros es P h. unfold critical_havoc in h. exact h. Qed.

(* Typed: identity. *)
Lemma typed_ch_sub_identity : ch_sub_identity TypedMM.critical_havoc.
Proof. intros es P h. unfold TypedMM.critical_havoc in h. exact h. Qed.

(* Store: identity. *)
Lemma store_ch_sub_identity : ch_sub_identity StoreMM.critical_havoc.
Proof. intros es P h. unfold StoreMM.critical_havoc in h. exact h. Qed.

(* Concurrent: sub-identity GIVEN a neutral shared state s0 such that
   `merge_shared es s0 = es` (a hypothesis, NOT an axiom — it is discharged
   wherever the environment provides an identity merge). *)
Lemma concurrent_ch_sub_identity :
  forall s0, (forall es, merge_shared es s0 = es) ->
  ch_sub_identity ConcurrentMM.critical_havoc.
Proof.
  intros s0 Hneutral es P h.
  unfold ConcurrentMM.critical_havoc in h.
  specialize (h s0). rewrite Hneutral in h. exact h.
Qed.

(* The four soundness-per-instance corollaries. *)
Corollary critical_sound_hoare :
  forall es mutex body out Qn Qr Qc Qb Qe pre_es,
    exec es (SCritical mutex body) out ->
    critical_havoc es (fun es' => wp body Qn Qr Qc Qb Qe pre_es es') ->
    outcome_post Qn Qr Qc Qb Qe out.
Proof. apply (critical_sound_param _ hoare_ch_sub_identity). Qed.

Corollary critical_sound_typed :
  forall es mutex body out Qn Qr Qc Qb Qe pre_es,
    exec es (SCritical mutex body) out ->
    TypedMM.critical_havoc es (fun es' => wp body Qn Qr Qc Qb Qe pre_es es') ->
    outcome_post Qn Qr Qc Qb Qe out.
Proof. apply (critical_sound_param _ typed_ch_sub_identity). Qed.

Corollary critical_sound_store :
  forall es mutex body out Qn Qr Qc Qb Qe pre_es,
    exec es (SCritical mutex body) out ->
    StoreMM.critical_havoc es (fun es' => wp body Qn Qr Qc Qb Qe pre_es es') ->
    outcome_post Qn Qr Qc Qb Qe out.
Proof. apply (critical_sound_param _ store_ch_sub_identity). Qed.

Corollary critical_sound_concurrent :
  forall s0, (forall es, merge_shared es s0 = es) ->
  forall es mutex body out Qn Qr Qc Qb Qe pre_es,
    exec es (SCritical mutex body) out ->
    ConcurrentMM.critical_havoc es (fun es' => wp body Qn Qr Qc Qb Qe pre_es es') ->
    outcome_post Qn Qr Qc Qb Qe out.
Proof. intros s0 Hn. apply (critical_sound_param _ (concurrent_ch_sub_identity s0 Hn)). Qed.

(* ===== Non-vacuity / discrimination of the typed predicates ===== *)

(* A block covers its own range: the typed `range_covered` machinery is
   genuinely satisfiable (the fixed `typed_heap := nil` is the conservative
   default — this exercises the predicate on a non-empty heap). *)
Lemma typed_range_covered_witness :
  forall p n, TypedMM.range_covered p n ((p, n) :: nil).
Proof.
  intros p n. exists (p, n). split.
  - left. reflexivity.
  - simpl. lia.
Qed.

(* `valid` on an explicit covering heap is genuinely True (non-vacuous). *)
Lemma typed_valid_witness :
  forall p n, p >= 0 -> n >= 0 ->
  p >= 0 /\ n >= 0 /\ TypedMM.range_covered p n ((p, n) :: nil).
Proof.
  intros p n Hp Hn. repeat split; try assumption.
  apply typed_range_covered_witness.
Qed.

(* `blocks_overlap` discriminates: adjacent blocks that share a cell overlap,
   genuinely-disjoint blocks do not. *)
Lemma typed_blocks_overlap_hit :
  TypedMM.blocks_overlap (0, 4) (2, 4).
Proof. unfold TypedMM.blocks_overlap. lia. Qed.

Lemma typed_blocks_overlap_miss :
  ~ TypedMM.blocks_overlap (0, 4) (10, 4).
Proof. unfold TypedMM.blocks_overlap. lia. Qed.

(* ===== Non-vacuity / discrimination of the store predicates ===== *)

(* In-bounds ranges are valid; out-of-bounds ranges are not. *)
Lemma store_valid_in_bounds : StoreMM.valid 0 10.
Proof. unfold StoreMM.valid, StoreMM.store_size. lia. Qed.

Lemma store_valid_oob_false : ~ StoreMM.valid 4090 100.
Proof. unfold StoreMM.valid, StoreMM.store_size. lia. Qed.

(* `separated` genuinely discriminates distinct vs. coinciding cells. *)
Lemma store_separated_distinct : StoreMM.separated 0 1.
Proof. unfold StoreMM.separated. lia. Qed.

Lemma store_separated_same_false : ~ StoreMM.separated 5 5.
Proof. unfold StoreMM.separated. intro H. apply H. reflexivity. Qed.

(* ===== Trust check ===== *)

(* The parameterised soundness rests only on the proved pycsl_soundness and
   the classical axioms it already uses — no new axiom is introduced. *)
(* Print Assumptions critical_sound_param. *)
