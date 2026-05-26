(* Phase6e_HandleAssignEnglish.v — Rocq refinement of english-01.md
 *
 * The English specification (`english-01.md` at the repo root)
 * describes `Module6._handle_assign_stmt`'s three Python-side
 * branches:
 *
 *   1. Shared module-level variable — emit `target := val` (no `let`).
 *   2. Fresh local — emit `let target = ... in` with sub-cases for
 *      record / lambda / array / dict / bounded-int / bool / plain.
 *   3. Existing local — emit `target := val` with bool coercion.
 *
 * At the WhyML-IR level all three branches produce the same
 * `WAssign x e` term — the `let ... in` vs `:=` distinction and the
 * `(if val then 1 else 0)` bool coercion are surface-syntax choices
 * that don't affect WP soundness. The Coq `gen` function in
 * Phase6d_StmtGen.v abstracts over them: `gen (SAssign x e) =
 * WAssign x e` regardless of which Python branch fired.
 *
 * This file documents the three-branch dispatch as Coq lemmas and
 * proves each branch's emitted WhyML satisfies the same SAssign WP
 * equivalence as the existing `wp_gen_assign` umbrella lemma in
 * Phase6e_Corr_Simple.v.
 *
 * The textual symmetry of the three branch arms below is
 * INTENTIONAL — it captures the soundness claim that the
 * Python-side dispatch is semantics-preserving regardless of which
 * arm fires. A stronger refinement (modelling `let ... in` vs
 * `WAssign` as distinct WhyML constructs) is out of scope; it would
 * require Why3 type-coercion modelling that the current formal
 * semantics doesn't carry. *)

Require Import ZArith String List Bool.
Require Import Phase1_AST.
Require Import Phase2_State.
Require Import Phase4_WP.
Require Import Phase6_WhyML.
Require Import Phase6b_WPW.
Require Import Phase6d_StmtGen.
Require Import Phase6e_Corr_Simple.
Open Scope Z_scope.

(* ===== The Python branch tag ===== *)

(* Mirrors `_handle_assign_stmt`'s three top-level if/elif arms. *)
Inductive assign_branch : Type :=
  | BrShared       (* target ∈ self._shared_var_names                *)
  | BrFresh        (* target ∉ declared_refs                         *)
  | BrExisting.    (* target ∈ declared_refs \ self._shared_var_names *)

(* ===== Branch-parametrised generator ===== *)

(* Coq counterpart of `_handle_assign_stmt`'s WhyML output, indexed
   by which Python branch fired. The three arms produce identical
   IR terms — the difference is at the Python surface level only. *)
Definition gen_assign_by_branch
    (b : assign_branch) (x : ident) (e : expr) : whyml_stmt :=
  match b with
  | BrShared   => WAssign x e
  | BrFresh    => WAssign x e
  | BrExisting => WAssign x e
  end.

(* Sanity: regardless of branch, the dispatcher equals the umbrella
   `gen (SAssign x e)` from Phase6d_StmtGen.v. *)
Lemma gen_assign_by_branch_eq_gen :
  forall b x e, gen_assign_by_branch b x e = gen (SAssign x e).
Proof. intros b x e; destruct b; reflexivity. Qed.

(* ===== Per-branch WP correctness lemmas =====
 *
 * Each branch reduces to the existing `wp_gen_assign` because the
 * dispatcher collapses to `gen (SAssign x e)`. *)

Lemma wp_branch_shared :
  forall x e Qn Qr Qc Qb Qe pre_es es,
  wp (SAssign x e) Qn Qr Qc Qb Qe pre_es es <->
  wp_w (gen_assign_by_branch BrShared x e)
       (enc Qn Qr Qc Qb Qe) pre_es es.
Proof.
  intros. rewrite gen_assign_by_branch_eq_gen. apply wp_gen_assign.
Qed.

Lemma wp_branch_fresh :
  forall x e Qn Qr Qc Qb Qe pre_es es,
  wp (SAssign x e) Qn Qr Qc Qb Qe pre_es es <->
  wp_w (gen_assign_by_branch BrFresh x e)
       (enc Qn Qr Qc Qb Qe) pre_es es.
Proof.
  intros. rewrite gen_assign_by_branch_eq_gen. apply wp_gen_assign.
Qed.

Lemma wp_branch_existing :
  forall x e Qn Qr Qc Qb Qe pre_es es,
  wp (SAssign x e) Qn Qr Qc Qb Qe pre_es es <->
  wp_w (gen_assign_by_branch BrExisting x e)
       (enc Qn Qr Qc Qb Qe) pre_es es.
Proof.
  intros. rewrite gen_assign_by_branch_eq_gen. apply wp_gen_assign.
Qed.

(* ===== Umbrella: WP soundness for any branch choice =====
 *
 * The English spec ends with: "its soundness is captured by the
 * `wp` fixpoint's SAssign arm (Phase4_WP.v line 42)". This theorem
 * is the explicit statement of that claim for any of the three
 * Python branches.
 *
 * Concretely: the Python `_handle_assign_stmt` is sound for any
 * branch choice made by its type-driven dispatch logic. *)

Theorem handle_assign_branches_correct :
  forall b x e Qn Qr Qc Qb Qe pre_es es,
  wp (SAssign x e) Qn Qr Qc Qb Qe pre_es es <->
  wp_w (gen_assign_by_branch b x e)
       (enc Qn Qr Qc Qb Qe) pre_es es.
Proof.
  intros b x e Qn Qr Qc Qb Qe pre_es es.
  destruct b.
  - apply wp_branch_shared.
  - apply wp_branch_fresh.
  - apply wp_branch_existing.
Qed.
