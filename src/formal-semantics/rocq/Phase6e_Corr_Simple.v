(* Phase6e_Corr_Simple.v — WP Correspondence for Simple Statements
   Proves wp s Qn Qr Qc Qb Qe pre_es es ↔ wp_w (gen s) (enc Qn Qr Qc Qb Qe) pre_es es
   for all non-loop, non-try-catch stmt constructors.

   Every case follows by unfolding both sides and using tauto / reflexivity.
   The SReturn case uses technical note §7.5 from full6-01.md:
     gen (SReturn e) = WSeq (WAssign "\result" e) (WRaise ExcReturn)
     whose wp_w unfolds to enc.(wc_r) (set_reg ...) = Qr (set_reg ...). *)

Require Import ZArith String List Bool.
Require Import Phase1_AST.
Require Import Phase2_State.
Require Import Phase4_WP.
Require Import Phase6_WhyML.
Require Import Phase6b_WPW.
Require Import Phase6c_ExprTrans.
Require Import Phase6d_StmtGen.
Open Scope Z_scope.

(* ===== Correspondence lemmas for simple (non-loop) statements ===== *)

Lemma wp_gen_skip :
  forall Qn Qr Qc Qb Qe pre_es es,
  wp SSkip Qn Qr Qc Qb Qe pre_es es <->
  wp_w (gen SSkip) (enc Qn Qr Qc Qb Qe) pre_es es.
Proof. intros. simpl. tauto. Qed.

Lemma wp_gen_assign :
  forall x e Qn Qr Qc Qb Qe pre_es es,
  wp (SAssign x e) Qn Qr Qc Qb Qe pre_es es <->
  wp_w (gen (SAssign x e)) (enc Qn Qr Qc Qb Qe) pre_es es.
Proof. intros. simpl. tauto. Qed.

Lemma wp_gen_aug_assign :
  forall x op e Qn Qr Qc Qb Qe pre_es es,
  wp (SAugAssign x op e) Qn Qr Qc Qb Qe pre_es es <->
  wp_w (gen (SAugAssign x op e)) (enc Qn Qr Qc Qb Qe) pre_es es.
Proof. intros. simpl. tauto. Qed.

Lemma wp_gen_array_set :
  forall arr i v Qn Qr Qc Qb Qe pre_es es,
  wp (SArraySet arr i v) Qn Qr Qc Qb Qe pre_es es <->
  wp_w (gen (SArraySet arr i v)) (enc Qn Qr Qc Qb Qe) pre_es es.
Proof. intros. simpl. tauto. Qed.

Lemma wp_gen_return :
  forall e Qn Qr Qc Qb Qe pre_es es,
  wp (SReturn e) Qn Qr Qc Qb Qe pre_es es <->
  wp_w (gen (SReturn e)) (enc Qn Qr Qc Qb Qe) pre_es es.
Proof.
  (* gen (SReturn e) = WSeq (WAssign "\result" e) (WRaise ExcReturn)
     wp_w unfolds:
       wp_w (WAssign "\result" e) {wc_n := fun es' => wp_w (WRaise ExcReturn) (enc ...) pre_es es', ...} pre_es es
     = (fun es' => wp_w (WRaise ExcReturn) (enc ...) pre_es es') (set_reg es (update ... "\result" ...))
     = wp_w (WRaise ExcReturn) (enc ...) pre_es (set_reg es ...)
     = (enc Qn Qr Qc Qb Qe).(wc_r) (set_reg es ...)
     = Qr (set_reg es ...)
     = wp (SReturn e) Qn Qr Qc Qb Qe pre_es es  ✓ *)
  intros. simpl. unfold enc. simpl. tauto.
Qed.

Lemma wp_gen_continue :
  forall Qn Qr Qc Qb Qe pre_es es,
  wp SContinue Qn Qr Qc Qb Qe pre_es es <->
  wp_w (gen SContinue) (enc Qn Qr Qc Qb Qe) pre_es es.
Proof. intros. simpl. unfold enc. simpl. tauto. Qed.

Lemma wp_gen_break :
  forall Qn Qr Qc Qb Qe pre_es es,
  wp SBreak Qn Qr Qc Qb Qe pre_es es <->
  wp_w (gen SBreak) (enc Qn Qr Qc Qb Qe) pre_es es.
Proof. intros. simpl. unfold enc. simpl. tauto. Qed.

Lemma wp_gen_assert :
  forall cond msg Qn Qr Qc Qb Qe pre_es es,
  wp (SAssert cond msg) Qn Qr Qc Qb Qe pre_es es <->
  wp_w (gen (SAssert cond msg)) (enc Qn Qr Qc Qb Qe) pre_es es.
Proof. intros. simpl. unfold enc. simpl. tauto. Qed.

Lemma wp_gen_tuple_unpack :
  forall xs e Qn Qr Qc Qb Qe pre_es es,
  wp (STupleUnpack xs e) Qn Qr Qc Qb Qe pre_es es <->
  wp_w (gen (STupleUnpack xs e)) (enc Qn Qr Qc Qb Qe) pre_es es.
Proof. intros. simpl. unfold enc. simpl. tauto. Qed.

Lemma wp_gen_ghost_decl :
  forall x t e Qn Qr Qc Qb Qe pre_es es,
  wp (SGhostDecl x t e) Qn Qr Qc Qb Qe pre_es es <->
  wp_w (gen (SGhostDecl x t e)) (enc Qn Qr Qc Qb Qe) pre_es es.
Proof. intros. simpl. unfold enc. simpl. tauto. Qed.

Lemma wp_gen_ghost_assign :
  forall x t op e Qn Qr Qc Qb Qe pre_es es,
  wp (SGhostAssign x t op e) Qn Qr Qc Qb Qe pre_es es <->
  wp_w (gen (SGhostAssign x t op e)) (enc Qn Qr Qc Qb Qe) pre_es es.
Proof. intros. simpl. unfold enc. simpl. tauto. Qed.

Lemma wp_gen_label :
  forall L Qn Qr Qc Qb Qe pre_es es,
  wp (SLabel L) Qn Qr Qc Qb Qe pre_es es <->
  wp_w (gen (SLabel L)) (enc Qn Qr Qc Qb Qe) pre_es es.
Proof. intros. simpl. unfold enc. simpl. tauto. Qed.

Lemma wp_gen_raise :
  forall exc Qn Qr Qc Qb Qe pre_es es,
  wp (SRaise exc) Qn Qr Qc Qb Qe pre_es es <->
  wp_w (gen (SRaise exc)) (enc Qn Qr Qc Qb Qe) pre_es es.
Proof. intros. simpl. unfold enc. simpl. tauto. Qed.

Lemma wp_gen_field_assign :
  forall self_id f e Qn Qr Qc Qb Qe pre_es es,
  wp (SFieldAssign self_id f e) Qn Qr Qc Qb Qe pre_es es <->
  wp_w (gen (SFieldAssign self_id f e)) (enc Qn Qr Qc Qb Qe) pre_es es.
Proof. intros. simpl. unfold enc. simpl. tauto. Qed.

Lemma wp_gen_field_aug_assign :
  forall self_id f op e Qn Qr Qc Qb Qe pre_es es,
  wp (SFieldAugAssign self_id f op e) Qn Qr Qc Qb Qe pre_es es <->
  wp_w (gen (SFieldAugAssign self_id f op e)) (enc Qn Qr Qc Qb Qe) pre_es es.
Proof. intros. simpl. unfold enc. simpl. tauto. Qed.

(* Phase 7: acquires/releases — gen → WSkip, wp → Qn es *)
Lemma wp_gen_acquires :
  forall m Qn Qr Qc Qb Qe pre_es es,
  wp (SAcquires m) Qn Qr Qc Qb Qe pre_es es <->
  wp_w (gen (SAcquires m)) (enc Qn Qr Qc Qb Qe) pre_es es.
Proof. intros. simpl. unfold enc. simpl. tauto. Qed.

Lemma wp_gen_releases :
  forall m Qn Qr Qc Qb Qe pre_es es,
  wp (SReleases m) Qn Qr Qc Qb Qe pre_es es <->
  wp_w (gen (SReleases m)) (enc Qn Qr Qc Qb Qe) pre_es es.
Proof. intros. simpl. unfold enc. simpl. tauto. Qed.
