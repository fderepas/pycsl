(* Phase6L_ComposeIfWhile.v — issue #74
   ============================================================================
   The if/while PROGRAM-LEVEL composition step that Z3 4.13.3 times out on in the
   Why3 layer (`src/self-annotate/pycsl-wp-spec.mlw`, module PyCSL_WP_Compose),
   proved here with explicit Rocq tactics. Z3's string theory explodes on the
   compositional `handle_if_code`/`handle_while_code` templates spliced with `seq`;
   Rocq rewrites them step-by-step, so the same proof goes through trivially.

   This is a SELF-CONTAINED mirror of the Why3 module's abstract interface:
     - the abstract evaluator and code emitters are Parameters;
     - the PER-ARM coherence facts (already PROVED in Why3 as `*_code_state_coherent`
       lemmas) are taken as Axioms here — they are the hypotheses, not the result;
     - the COMPOSITION (the new contribution) is proved as Theorems.
   Trust basis: the axioms below are the Why3-proved per-arm lemmas; only the
   composition is added. See `src/self-annotate/arm-coverage.md` §3.
   ========================================================================== *)

Require Import String List ZArith.
Import ListNotations.
Local Open Scope string_scope.

(* ── Abstract domain (mirrors PyCSL_WP_Spec) ─────────────────────────────── *)
Parameter value : Type.
Parameter VInt  : Z -> value.
Parameter state : Type.
Definition ident := string.
Parameter update : state -> ident -> value -> state.
Parameter arr_set_state : state -> ident -> Z -> Z -> state.
Definition resultId : ident := "result"%string.

(* Truthiness: `vnz v = true`  <->  `v <> VInt 0` (the Why3 `cond_val <> VInt 0`). *)
Parameter vnz : value -> bool.

(* ── Abstract WhyML string evaluator + code emitters (mirror PyCSL_WP_Code) ── *)
Parameter eval_whyml_expr  : string -> state -> value.
Parameter eval_whyml_stmts : string -> state -> state.

Parameter handle_skip_code      : string -> string -> string.            (* indent rest *)
Parameter handle_assign_code    : ident -> string -> string -> string -> bool -> string.
Parameter handle_array_set_code : ident -> string -> string -> string -> string -> string.
Parameter handle_if_code        : string -> string -> string -> string -> bool -> string.
Parameter handle_while_code     : string -> string -> string -> string -> string -> string.
Parameter handle_return_code    : string -> string -> bool -> string.
Parameter handle_continue_code  : string -> string.

(* The opaque statement separator (`";\n"` in Why3 — its value is irrelevant to
   the composition, only `seq_semantics` matters). *)
Parameter sep : string.

(* abstract loop denotation (the Why3 `while_fix`; its adequacy = open wp_for_desugar) *)
Parameter while_fix : string -> string -> state -> state.   (* cond_str body_str st *)

(* ── PER-ARM coherence facts — AXIOMS here, PROVED in Why3 ────────────────── *)
Axiom eval_empty :
  forall st, eval_whyml_stmts EmptyString st = st.

Axiom seq_semantics :
  forall s1 s2 st,
    eval_whyml_stmts (s1 ++ sep ++ s2) st
    = eval_whyml_stmts s2 (eval_whyml_stmts s1 st).

Axiom skip_coh :
  forall indent rest st,
    eval_whyml_stmts (handle_skip_code indent rest) st = eval_whyml_stmts rest st.

Axiom assign_coh :
  forall x ev indent rest st e_val,
    eval_whyml_expr ev st = e_val ->
    eval_whyml_stmts (handle_assign_code x ev indent rest true) st
    = eval_whyml_stmts rest (update st x e_val).

Axiom array_set_coh :
  forall arr is vs indent rest st iv nv,
    eval_whyml_expr is st = VInt iv ->
    eval_whyml_expr vs st = VInt nv ->
    eval_whyml_stmts (handle_array_set_code arr is vs indent rest) st
    = eval_whyml_stmts rest (arr_set_state st arr iv nv).

Axiom if_else_coh :
  forall cond then_ else_ indent st cond_val,
    eval_whyml_expr cond st = cond_val ->
    eval_whyml_stmts (handle_if_code cond then_ else_ indent true) st
    = if vnz cond_val then eval_whyml_stmts then_ st else eval_whyml_stmts else_ st.

Axiom while_coh :
  forall cond inv var body indent st,
    eval_whyml_stmts (handle_while_code cond inv var body indent) st
    = while_fix cond body st.

Axiom return_coh :
  forall ev indent st e_val,
    eval_whyml_expr ev st = e_val ->
    eval_whyml_stmts (handle_return_code ev indent false) st = update st resultId e_val.

Axiom continue_coh :
  forall indent st, eval_whyml_stmts (handle_continue_code indent) st = st.

(* ── Expression IR (mirrors the compose module) ──────────────────────────── *)
Parameter expr_ir   : Type.
Parameter emit_expr : expr_ir -> string.
Parameter eval_e    : expr_ir -> state -> value.
Parameter eval_int  : expr_ir -> state -> Z.
Axiom expr_coherent : forall e st, eval_whyml_expr (emit_expr e) st = eval_e e st.
Axiom eval_e_int    : forall e st, eval_e e st = VInt (eval_int e st).

(* ── The Z3-HARD steps: if / while composition, in 2 rewrites each ────────── *)

(* if-step: emitting `if … ;\n rest`, then evaluating, dispatches on the cond and
   threads the chosen branch's effect into `rest`. (This is the per-disjunct +
   seq combination Z3 cannot case-split.) *)
Theorem if_step :
  forall c tcode ecode indent rc st,
    eval_whyml_stmts
      (handle_if_code (emit_expr c) tcode ecode indent true ++ sep ++ rc) st
    = eval_whyml_stmts rc
        (if vnz (eval_e c st)
         then eval_whyml_stmts tcode st
         else eval_whyml_stmts ecode st).
Proof.
  intros c tcode ecode indent rc st.
  rewrite seq_semantics.
  rewrite (if_else_coh (emit_expr c) tcode ecode indent st (eval_e c st)
                       (expr_coherent c st)).
  reflexivity.
Qed.

(* while-step: emitting `while … ;\n rest`, then evaluating, threads the loop's
   (abstract) effect into `rest`. *)
Theorem while_step :
  forall c inv var body indent rc st,
    eval_whyml_stmts
      (handle_while_code (emit_expr c) inv var body indent ++ sep ++ rc) st
    = eval_whyml_stmts rc (while_fix (emit_expr c) body st).
Proof.
  intros c inv var body indent rc st.
  rewrite seq_semantics.
  rewrite (while_coh (emit_expr c) inv var body indent st).
  reflexivity.
Qed.

(* ── The modeled language (mirrors PyCSL_WP_Compose) ──────────────────────── *)
(* Blocks are encoded with `Sk_seq` (not `list`), so every recursion is pure
   structural recursion on `simple` and the standard `simple_ind` already gives
   the if-branch IHs — no nested-list guardedness or custom induction needed. *)
Inductive simple : Type :=
  | Sk_skip
  | Sk_assign (x: ident) (e: expr_ir)
  | Sk_arrset (a: ident) (i v: expr_ir)
  | Sk_seq    (s1 s2: simple)
  | Sk_if     (c: expr_ir) (tb eb: simple).

Inductive stmt : Type :=
  | St_simple   (s: simple)
  | St_return   (e: expr_ir)
  | St_continue
  | St_while    (c: expr_ir) (body: simple).

Definition sel (c: expr_ir) (st: state) (a b: state) : state :=
  if vnz (eval_e c st) then a else b.

Fixpoint wp_one (s: simple) (st: state) : state :=
  match s with
  | Sk_skip         => st
  | Sk_assign x e   => update st x (eval_e e st)
  | Sk_arrset a i v => arr_set_state st a (eval_int i st) (eval_int v st)
  | Sk_seq s1 s2    => wp_one s2 (wp_one s1 st)
  | Sk_if c tb eb   => sel c st (wp_one tb st) (wp_one eb st)
  end.

(* the empty-block "()" terminator a branch ends with *)
Definition brk (indent: string) : string := handle_skip_code indent EmptyString.

(* CPS emitter: `rc` is the emission of the continuation. *)
Fixpoint emit_one (s: simple) (rc: string) (indent: string) : string :=
  match s with
  | Sk_skip         => handle_skip_code indent rc
  | Sk_assign x e   => handle_assign_code x (emit_expr e) indent rc true
  | Sk_arrset a i v => handle_array_set_code a (emit_expr i) (emit_expr v) indent rc
  | Sk_seq s1 s2    => emit_one s1 (emit_one s2 rc indent) indent
  | Sk_if c tb eb   =>
      handle_if_code (emit_expr c) (emit_one tb (brk indent) indent)
                     (emit_one eb (brk indent) indent) indent true
      ++ sep ++ rc
  end.

(* a branch's "()" terminator evaluates to the identity *)
Lemma brk_id : forall indent st, eval_whyml_stmts (brk indent) st = st.
Proof. intros. unfold brk. rewrite skip_coh. apply eval_empty. Qed.

(* COMPOSITION over the simple fragment — standard structural induction on `simple`. *)
Lemma emit_one_coherent :
  forall s rc st indent,
    eval_whyml_stmts (emit_one s rc indent) st = eval_whyml_stmts rc (wp_one s st).
Proof.
  induction s as [ | x e | a i v | s1 IH1 s2 IH2 | c tb IHtb eb IHeb ];
    intros rc st indent; simpl.
  - (* Sk_skip *) apply skip_coh.
  - (* Sk_assign *) apply (assign_coh x (emit_expr e) indent rc st (eval_e e st)). apply expr_coherent.
  - (* Sk_arrset *)
    rewrite (array_set_coh a (emit_expr i) (emit_expr v) indent rc st
               (eval_int i st) (eval_int v st)).
    + reflexivity.
    + rewrite expr_coherent. apply eval_e_int.
    + rewrite expr_coherent. apply eval_e_int.
  - (* Sk_seq *) rewrite IH1. rewrite IH2. reflexivity.
  - (* Sk_if *)
    rewrite if_step.
    rewrite (IHtb (brk indent) st indent). rewrite brk_id.
    rewrite (IHeb (brk indent) st indent). rewrite brk_id.
    unfold sel. reflexivity.
Qed.

(* ── Top-level program: simple statements + while + early-exit terminators ──── *)
Fixpoint wp_stmts (ss: list stmt) (st: state) (indent: string) : state :=
  match ss with
  | []        => st
  | s :: rest =>
      match s with
      | St_return e    => update st resultId (eval_e e st)
      | St_continue    => st
      | St_simple sp   => wp_stmts rest (wp_one sp st) indent
      | St_while c body=> wp_stmts rest
                            (while_fix (emit_expr c) (emit_one body (brk indent) indent) st) indent
      end
  end.

Fixpoint emit_stmts (ss: list stmt) (indent: string) : string :=
  match ss with
  | []        => brk indent
  | s :: rest =>
      match s with
      | St_return e    => handle_return_code (emit_expr e) indent false
      | St_continue    => handle_continue_code indent
      | St_simple sp   => emit_one sp (emit_stmts rest indent) indent
      | St_while c body=>
          handle_while_code (emit_expr c) EmptyString EmptyString
                            (emit_one body (brk indent) indent) indent
          ++ sep ++ emit_stmts rest indent
      end
  end.

(* FINISH LINK 3 — the whole-program composition theorem, INCLUDING if (inside the
   simple fragment) and while. eval(emit_stmts ss) st = wp_stmts ss st. *)
Theorem emit_stmts_coherent :
  forall ss st indent,
    eval_whyml_stmts (emit_stmts ss indent) st = wp_stmts ss st indent.
Proof.
  induction ss as [ | s rest IH ]; intros st indent; simpl.
  - (* [] *) apply brk_id.
  - destruct s as [ sp | e | | c body ].
    + (* St_simple *) rewrite emit_one_coherent. rewrite IH. reflexivity.
    + (* St_return *) apply (return_coh (emit_expr e) indent st (eval_e e st)). apply expr_coherent.
    + (* St_continue *) apply continue_coh.
    + (* St_while *) rewrite while_step. rewrite IH. reflexivity.
Qed.

(* ── Reflection back to Why3 ──────────────────────────────────────────────────
   `emit_stmts_coherent` is the Rocq proof of exactly the statement that times out
   in Z3 4.13.3 for the if/while arms (Why3 `PyCSL_WP_Compose.emit_stmts_coherent`,
   issue #74). The per-arm `*_coh` axioms above are the Why3-PROVED
   `*_code_state_coherent` lemmas; only the COMPOSITION (proved here in <40 lines of
   explicit rewriting) was the Z3 wall. The Why3 layer cites this as the
   audited-by-Rocq closure of the if/while composition. *)
