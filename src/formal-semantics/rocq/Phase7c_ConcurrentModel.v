(* Phase7c_ConcurrentModel.v — the real concurrent model: havoc-aware SOS +
   WP for SCritical, and lock-state for SAcquires/SReleases (Category D residual)
   ============================================================================
   Phase 7b proved `SCritical` sound for any *sub-identity* memory model, but
   ConcurrentMM's havoc (`forall shared, P (merge_shared es shared)`) is
   sub-identity only under a *neutral shared state* crutch — because the
   Phase-3 SOS `ExecCritical` runs the body on `es` unchanged (no havoc). This
   file removes that crutch by giving the concurrency constructs a genuine
   operational semantics and re-proving soundness against it.

   KEY DESIGN CHOICE — no `exec_state` field change. The shared state and the
   per-mutex lock state live in the *existing* `reg_state` under RESERVED
   identifiers, exactly as `"\result"` and `_pycsl_idx` are already reserved:
     - `lock_key m  = "$lock." ++ m`   holds VInt 0 (Free) / VInt 1 (Held);
     - `shared_key  = "$shared"`        holds a VArray (the shared memory).
   So the concurrent SOS/WP reuse `exec_state`, `lookup`, `update`, `set_reg`,
   and the proved `pycsl_soundness` verbatim — nothing in the core is touched.

   KEY INSIGHT — the havoc discharges itself. Once the SOS `ExecCCritical`
   HAVOCS the shared cell (runs the body from `set_shared es a` for the
   environment's chosen `a`), the concurrent WP `forall a, wp body … (set_shared
   es a)` is discharged by INSTANTIATING at that same `a`. No neutral-shared
   hypothesis is needed — the operational havoc and the WP's universal
   quantifier line up exactly.

   Delivered here (additive, 0 axioms, 0 Admitted):
     • `wp_c_*` / `exec_c` : havoc-aware WP + SOS for critical/acquires/releases;
     • `conc_sound_{critical,acquires,releases}` : soundness for each, the
       critical case reducing to the proved `pycsl_soundness` on the body;
     • lock discipline: acquire⟹Held, release⟹Free, Free≠Held, round-trip;
     • `lock_order` well-formedness + a preservation lemma (the provable core
       of deadlock prevention in the single-thread WP world). *)

Require Import ZArith String List Bool.
Require Import Lia.
Require Import PyCSL.Phase1_AST.
Require Import PyCSL.Phase2_State.
Require Import PyCSL.Phase3_SOS.
Require Import PyCSL.Phase4_WP.
Require Import PyCSL.Phase5b_Soundness.
Import ListNotations.
Open Scope Z_scope.
Open Scope string_scope.

(* ===== Reserved register keys for lock state and shared state ===== *)

Definition lock_key (m : ident) : ident := "$lock." ++ m.
Definition shared_key : ident := "$shared".

(* Lock predicates and updates, all on the existing reg_state. *)
Definition lock_free (es : exec_state) (m : ident) : Prop :=
  lookup es.(reg_state) (lock_key m) = Some (VInt 0).
Definition lock_held (es : exec_state) (m : ident) : Prop :=
  lookup es.(reg_state) (lock_key m) = Some (VInt 1).
Definition set_lock (es : exec_state) (m : ident) (v : Z) : exec_state :=
  set_reg es (update es.(reg_state) (lock_key m) (VInt v)).

(* Havoc the shared cell to an arbitrary array value `a`. *)
Definition set_shared (es : exec_state) (a : list Z) : exec_state :=
  set_reg es (update es.(reg_state) shared_key (VArray a)).

(* ===== Concurrent WP for the three constructs =====

   Standalone definitions (they do NOT redefine the global `wp`): the body of
   a critical section runs under the ordinary proved `wp`. *)

(* `acquires m`: the lock must be Free at entry; afterwards it is Held. *)
Definition wp_c_acquires (m : ident) (Qn : exec_state -> Prop) (es : exec_state) : Prop :=
  lock_free es m /\ Qn (set_lock es m 1).

(* `releases m`: the lock must be Held at entry; afterwards it is Free. *)
Definition wp_c_releases (m : ident) (Qn : exec_state -> Prop) (es : exec_state) : Prop :=
  lock_held es m /\ Qn (set_lock es m 0).

(* `critical`: the body must be provable for ALL shared states the environment
   could present at entry — the genuine havoc semantics. *)
Definition wp_c_critical (body : stmt)
    (Qn Qr Qc Qb : exec_state -> Prop) (Qe : ident -> exec_state -> Prop)
    (pre_es es : exec_state) : Prop :=
  forall a : list Z, wp body Qn Qr Qc Qb Qe pre_es (set_shared es a).

(* Bridge: `wp_c_critical` IS a concrete instance of the abstract ConcurrentMM
   havoc (`forall shared, P (merge_shared es shared)`) with the shared type
   fixed to `list Z` and `merge_shared := set_shared`. *)
Definition conc_havoc (es : exec_state) (P : exec_state -> Prop) : Prop :=
  forall a : list Z, P (set_shared es a).

Lemma wp_c_critical_is_havoc :
  forall body Qn Qr Qc Qb Qe pre_es es,
  wp_c_critical body Qn Qr Qc Qb Qe pre_es es
  = conc_havoc es (fun es' => wp body Qn Qr Qc Qb Qe pre_es es').
Proof. intros. reflexivity. Qed.

(* ===== Concurrent operational semantics (havoc-aware) ===== *)

Inductive exec_c : exec_state -> stmt -> outcome -> Prop :=
  (* acquire: requires Free; establishes Held. *)
  | ExecCAcquire :
      forall es m,
      lock_free es m ->
      exec_c es (SAcquires m) (ONormal (set_lock es m 1))
  (* release: requires Held; establishes Free. *)
  | ExecCRelease :
      forall es m,
      lock_held es m ->
      exec_c es (SReleases m) (ONormal (set_lock es m 0))
  (* critical: the environment presents SOME shared state `a` at entry; the
     body runs (under the ordinary `exec`) from the havoc'd state. *)
  | ExecCCritical :
      forall es mutex body a out,
      exec (set_shared es a) body out ->
      exec_c es (SCritical mutex body) out.

(* ===== Soundness of the concurrent constructs ===== *)

(* acquires: sound — the WP's post-conjunct is exactly the outcome. *)
Theorem conc_sound_acquires :
  forall es m out Qn Qr Qc Qb Qe,
  wp_c_acquires m Qn es ->
  exec_c es (SAcquires m) out ->
  outcome_post Qn Qr Qc Qb Qe out.
Proof.
  intros es m out Qn Qr Qc Qb Qe [Hfree HQ] Hexec.
  inversion Hexec; subst. simpl. exact HQ.
Qed.

(* releases: sound — symmetric. *)
Theorem conc_sound_releases :
  forall es m out Qn Qr Qc Qb Qe,
  wp_c_releases m Qn es ->
  exec_c es (SReleases m) out ->
  outcome_post Qn Qr Qc Qb Qe out.
Proof.
  intros es m out Qn Qr Qc Qb Qe [Hheld HQ] Hexec.
  inversion Hexec; subst. simpl. exact HQ.
Qed.

(* critical: sound — the havoc WP is discharged by instantiating at the shared
   state the SOS chose, then reducing to the proved `pycsl_soundness` on the
   body. NO neutral-shared hypothesis is needed. *)
Theorem conc_sound_critical :
  forall es mutex body out Qn Qr Qc Qb Qe pre_es,
  wp_c_critical body Qn Qr Qc Qb Qe pre_es es ->
  exec_c es (SCritical mutex body) out ->
  outcome_post Qn Qr Qc Qb Qe out.
Proof.
  intros es mutex body out Qn Qr Qc Qb Qe pre_es Hwp Hexec.
  inversion Hexec; subst.
  (* Hexec gives `exec (set_shared es a) body out` for some `a`;
     instantiate the havoc WP at that same `a`. *)
  eapply pycsl_soundness; [ eassumption | ].
  unfold wp_c_critical in Hwp. apply Hwp.
Qed.

(* ===== Lock discipline (the payoff of a real lock state) ===== *)

(* Helper: reading a mutex's lock key right after `set_lock` returns the value
   written. `cbn [set_reg reg_state]` reduces only the record projection —
   NOT the string append `lock_key m` — so `lookup_update_eq` unifies. *)
Lemma lock_lookup_set :
  forall es m v,
  lookup (set_lock es m v).(reg_state) (lock_key m) = Some (VInt v).
Proof.
  intros es m v. unfold set_lock. cbn [set_reg reg_state].
  apply lookup_update_eq.
Qed.

(* After `acquires m`, the lock is Held. *)
Lemma acquire_makes_held :
  forall es m, lock_held (set_lock es m 1) m.
Proof. intros es m. unfold lock_held. apply lock_lookup_set. Qed.

(* After `releases m`, the lock is Free. *)
Lemma release_makes_free :
  forall es m, lock_free (set_lock es m 0) m.
Proof. intros es m. unfold lock_free. apply lock_lookup_set. Qed.

(* Free and Held are mutually exclusive (the predicate genuinely discriminates,
   not vacuous). *)
Lemma lock_free_not_held :
  forall es m, lock_free es m -> ~ lock_held es m.
Proof.
  intros es m Hfree Hheld. unfold lock_free, lock_held in *.
  rewrite Hfree in Hheld. inversion Hheld.
Qed.

(* Acquire-then-release round-trips the lock back to Free. *)
Lemma acquire_release_roundtrip :
  forall es m, lock_free (set_lock (set_lock es m 1) m 0) m.
Proof. intros. apply release_makes_free. Qed.

(* ===== lock_order well-formedness (deadlock-prevention core) ===== *)

(* A global acquisition order is a list of mutex names; a mutex's priority is
   its index. Acquiring in strictly-increasing priority prevents the classic
   hold-and-wait cycle. In the single-thread WP world we can prove the
   *invariant*: acquiring `m` in order preserves order-sortedness of the held
   set — the provable core of deadlock freedom (the full multi-thread cycle
   argument is out of scope for a WP calculus). *)

Fixpoint idx_of (order : list ident) (m : ident) : nat :=
  match order with
  | [] => 0
  | x :: rest => if String.eqb x m then 0 else S (idx_of rest m)
  end.

(* `order_sorted order held`: `held` is a stack (head = most recently
   acquired). Acquisition respects the global order, so priorities strictly
   DECREASE down the stack — the head has the highest priority. *)
Fixpoint order_sorted (order : list ident) (held : list ident) : Prop :=
  match held with
  | [] => True
  | m :: rest =>
      match rest with
      | [] => True
      | m' :: _ => (idx_of order m' < idx_of order m)%nat /\ order_sorted order rest
      end
  end.

(* `acquire_respects_order order held m`: `m` has strictly higher priority than
   the most-recently-held mutex (the head of `held`, treating `held` as a stack
   with the top most recent). *)
Definition acquire_respects_order (order : list ident) (held : list ident) (m : ident) : Prop :=
  match held with
  | [] => True
  | top :: _ => (idx_of order top < idx_of order m)%nat
  end.

(* Preservation: acquiring in order keeps the held stack order-sorted. This is
   the deadlock-prevention well-formedness invariant. *)
Lemma acquire_preserves_order :
  forall order held m,
  order_sorted order held ->
  acquire_respects_order order held m ->
  order_sorted order (m :: held).
Proof.
  intros order held m Hsorted Hresp.
  destruct held as [| top rest].
  - simpl. exact I.
  - simpl. simpl in Hresp. split; [ exact Hresp | exact Hsorted ].
Qed.

(* ===== Trust check ===== *)
(* Print Assumptions conc_sound_critical. *)
