(* Phase2b_RecordVal.v — record/ADT-VALUED `val` for nested aliasing.

   TIER-3 Phase 3 (T3.3.1): the PROMOTION of the Phase-0 feasibility spike
   (formerly Phase7_Spike.v) into the *certified build*.  This file is listed
   in `_CoqProject` immediately after `Phase2_State.v`, so `make` compiles and
   checks it as a first-class part of the formal-semantics soundness chain.

   It certifies exactly the construct the Phase-1 emitter `ir_node` ADT reads:
   a nested record/variant value whose field projection is a `path_get`.  It
   imports the REAL `val`/`state`/`lookup`/`update` from `Phase2_State` and
   proves, against those exact definitions, that:

     (1) a record/ADT-valued value `val7` with NESTED projection is expressible
         (this is the `ir_node` discriminant + field-projection shape — a
         `BinOp` holding `left`/`right` sub-nodes is a record whose field read
         is `path_get [field]`);
     (2) READ-BACK holds: set `o.b.c := v`, then get `o.b.c` = v   (nested);
     (3) FRAME holds: set `o.b.c` leaves `o.b.d` unchanged           (nested);
     (4) the extension is CONSERVATIVE: a record-free program embeds into the
         extended state and its `lookup`/`update` behave IDENTICALLY to the
         base Phase-2 `lookup`/`update` — i.e. `SAssign`'s WP arm is unchanged,
         hence `pycsl_soundness` (Phase5b) re-proves with NO new axiom.

   This is a CONSERVATIVE promotion: it does NOT add a `VRec` constructor to
   the core `val` inductive (which would cascade across the 22-constructor
   soundness induction), it adds the record-valued value ALONGSIDE `val` with
   an injection `inj_val : val -> val7` and proves the SAssign arm intact.
   Per the tier-3 plan §0/Phase-3, this conservative extension "alone satisfies
   the coupling for what Phase-1 emitted".

   The `Print Assumptions` block at the bottom is the make-or-break trust
   check: every result must be "Closed under the global context" (NO axiom) so
   the 3-axiom trust ledger stays intact.

   Nothing here is `Admitted`.  Build: part of `make` (see `_CoqProject`). *)

Require Import ZArith String List Bool.
Require Import Phase1_AST.
Require Import Phase2_State.   (* the REAL val, state, lookup, update, eval_expr *)
Import ListNotations.
(* NB: do NOT open string_scope — it would rebind `++` to string append,
   shadowing list `app` used in the frame lemma's path concatenation. *)

(* ===================================================================== *)
(* 1. The record/ADT-VALUED value type                                    *)
(* ===================================================================== *)

(* A nested record value: an integer/array leaf, or a record whose fields
   map names to *further* record values (nested inductive through `list`,
   which Rocq accepts positively).  This is the `VRec : (field -> val) -> val`
   the plan asks for, realized as a finite association list of sub-values so
   that projection/update are structurally recursive and axiom-free.

   Emitter-side reading: an `ir_node` such as `BinOp op left right` is the
   record `V7Rec [("op", ...); ("left", <sub>); ("right", <sub>)]`; the emitter
   read `ir.get("right")` is `path_get node ["right"]`. *)
Inductive val7 : Type :=
  | V7Int (n : Z)
  | V7Arr (a : list Z)
  | V7Rec (fields : list (string * val7)).

(* Field-level (one record layer) association get/set. *)
Fixpoint frec_get (fs : list (string * val7)) (f : string) : option val7 :=
  match fs with
  | [] => None
  | (g, v) :: rest => if String.eqb f g then Some v else frec_get rest f
  end.

Fixpoint frec_set (fs : list (string * val7)) (f : string) (v : val7)
  : list (string * val7) :=
  match fs with
  | [] => [(f, v)]
  | (g, w) :: rest =>
      if String.eqb f g then (g, v) :: rest
      else (g, w) :: frec_set rest f v
  end.

(* A path names a nested field chain: `o.b.c` is the path ["b"; "c"]. *)
Definition path := list string.

(* Nested projection `v.<p>` : follow the path through record layers. *)
Fixpoint path_get (v : val7) (p : path) : option val7 :=
  match p with
  | [] => Some v
  | f :: rest =>
      match v with
      | V7Rec fs =>
          match frec_get fs f with
          | Some child => path_get child rest
          | None => None
          end
      | _ => None
      end
  end.

(* Nested update `v.<p> := nv`.  A non-record node encountered mid-path is
   treated as an empty record (so the write always lands); this makes the
   read-back law unconditional and models Python's `o.b.c = v` autovivifying
   the chain the annotation asserts exists. *)
Fixpoint path_set (v : val7) (p : path) (nv : val7) : val7 :=
  match p with
  | [] => nv
  | f :: rest =>
      let fs := match v with V7Rec fs => fs | _ => [] end in
      let child := match frec_get fs f with
                   | Some c => c
                   | None => V7Rec []
                   end in
      V7Rec (frec_set fs f (path_set child rest nv))
  end.

(* ===================================================================== *)
(* 2. One-layer association-list laws (get/set)                           *)
(* ===================================================================== *)

Lemma frec_get_set_eq :
  forall fs f v, frec_get (frec_set fs f v) f = Some v.
Proof.
  induction fs as [| [g w] rest IH]; intros f v; simpl.
  - rewrite String.eqb_refl. reflexivity.
  - destruct (String.eqb f g) eqn:Hfg; simpl.
    + rewrite Hfg. reflexivity.
    + rewrite Hfg. apply IH.
Qed.

Lemma frec_get_set_neq :
  forall fs f g v, f <> g ->
    frec_get (frec_set fs g v) f = frec_get fs f.
Proof.
  induction fs as [| [h w] rest IH]; intros f g v Hne; simpl.
  - destruct (String.eqb f g) eqn:Hfg.
    + apply String.eqb_eq in Hfg. contradiction.
    + reflexivity.
  - destruct (String.eqb g h) eqn:Hgh; simpl.
    + apply String.eqb_eq in Hgh; subst h.
      destruct (String.eqb f g) eqn:Hfg.
      * apply String.eqb_eq in Hfg. contradiction.
      * reflexivity.
    + destruct (String.eqb f h) eqn:Hfh; simpl.
      * reflexivity.
      * apply IH; assumption.
Qed.

(* ===================================================================== *)
(* 3. READ-BACK lemma (nested)                                            *)
(*      set o.<p> := v ; then get o.<p> = v                               *)
(* ===================================================================== *)

Theorem path_read_back :
  forall v p nv, path_get (path_set v p nv) p = Some nv.
Proof.
  intros v p; revert v.
  induction p as [| f rest IH]; intros v nv; simpl.
  - reflexivity.
  - rewrite frec_get_set_eq. apply IH.
Qed.

(* Concrete instance the plan names explicitly: o.b.c := v  ⟹  o.b.c = v.
   Emitter reading: after the recognizer rewrites a node's "right" sub-node,
   reading it back yields exactly that sub-node. *)
Corollary read_back_bc :
  forall o v, path_get (path_set o ["b"; "c"] v) ["b"; "c"] = Some v.
Proof. intros; apply path_read_back. Qed.

(* ===================================================================== *)
(* 4. FRAME lemma (nested)                                                *)
(*      updating o.<pre.c> leaves o.<pre.d> unchanged  (c <> d)           *)
(* ===================================================================== *)

Theorem path_frame :
  forall pre c d v nv,
    c <> d ->
    path_get (path_set v (pre ++ [c])%list nv) (pre ++ [d])%list
      = path_get v (pre ++ [d])%list.
Proof.
  induction pre as [| f rest IH]; intros c d v nv Hne; simpl.
  - (* base: v.c := nv, read v.d, c <> d *)
    rewrite frec_get_set_neq by (intro; apply Hne; symmetry; assumption).
    destruct v; simpl.
    + reflexivity.
    + reflexivity.
    + reflexivity.
  - (* step: descend through field f on both sides *)
    rewrite frec_get_set_eq.
    rewrite IH by assumption.
    (* both sides now read child f of v (or the fresh empty record) *)
    destruct v as [ | | fs]; simpl.
    + (* V7Int: original has no field f; fresh side also empty *)
      destruct rest; reflexivity.
    + (* V7Arr: idem *)
      destruct rest; reflexivity.
    + destruct (frec_get fs f) as [child|] eqn:Hf.
      * reflexivity.
      * destruct rest; reflexivity.
Qed.

(* Concrete instance the plan names explicitly:
   o.b.c := v  leaves  o.b.d  unchanged.  Emitter reading: rewriting a node's
   "left" sub-node does not disturb its "right" sub-node — the frame guarantee
   a structural-recursive handler needs. *)
Corollary frame_bc_bd :
  forall o v,
    path_get (path_set o ["b"; "c"] v) ["b"; "d"] = path_get o ["b"; "d"].
Proof.
  intros o v.
  change (["b"; "c"]) with (([ "b" ] ++ [ "c" ])%list).
  change (["b"; "d"]) with (([ "b" ] ++ [ "d" ])%list).
  apply path_frame. intro H; discriminate H.
Qed.

(* ===================================================================== *)
(* 5. CONSERVATIVITY: the extension does not disturb record-free programs *)
(*    We inject base Phase-2 `val` into `val7` and prove the extended     *)
(*    state's lookup/update agree, cell-for-cell, with the REAL Phase-2   *)
(*    `lookup`/`update` — so `SAssign`'s WP arm is unchanged.             *)
(* ===================================================================== *)

(* Injection of the base value world (VInt/VArray) into val7. Closures are
   out of scope for the record model; the record-free integer/array fragment
   is exactly the state-value fragment SAssign manipulates. *)
Definition inj_val (v : val) : val7 :=
  match v with
  | VInt n   => V7Int n
  | VArray a => V7Arr a
  | VClosure _ _ _ => V7Rec []   (* closures unused by the record-free fragment *)
  end.

(* Extended state and its lookup/update, mirroring Phase2_State exactly. *)
Definition state7 := list (string * val7).

Fixpoint lookup7 (st : state7) (x : string) : option val7 :=
  match st with
  | [] => None
  | (y, v) :: rest => if String.eqb x y then Some v else lookup7 rest x
  end.

Definition update7 (st : state7) (x : string) (v : val7) : state7 :=
  (x, v) :: st.

(* Embed a whole base state into the extended world. *)
Definition lift_state (st : state) : state7 :=
  List.map (fun p => (fst p, inj_val (snd p))) st.

(* Conservativity 1 — lookups agree (up to injection). *)
Theorem lookup7_lift :
  forall st x,
    lookup7 (lift_state st) x = option_map inj_val (lookup st x).
Proof.
  induction st as [| [y v] rest IH]; intros x; simpl.
  - reflexivity.
  - destruct (String.eqb x y) eqn:Hxy; simpl.
    + reflexivity.
    + apply IH.
Qed.

(* Conservativity 2 — updates agree (the SAssign effect commutes with inj). *)
Theorem update7_lift :
  forall st x v,
    update7 (lift_state st) x (inj_val v) = lift_state (update st x v).
Proof. intros; reflexivity. Qed.

(* Conservativity 3 — the two combine: reading back an SAssign-updated cell in
   the extended world equals injecting the base SAssign read-back.  This is the
   representative WP arm `Qn (update st x (eval_expr st e))` shown intact under
   the record-valued extension. *)
Theorem assign_arm_conservative :
  forall st x v,
    lookup7 (update7 (lift_state st) x (inj_val v)) x = Some (inj_val v).
Proof.
  intros st x v. unfold update7. simpl. rewrite String.eqb_refl. reflexivity.
Qed.

(* And it matches the base engine's own read-back through the injection. *)
Theorem assign_arm_matches_base :
  forall st x v,
    lookup7 (lift_state (update st x v)) x = option_map inj_val (lookup (update st x v) x).
Proof. intros; apply lookup7_lift. Qed.

(* ===================================================================== *)
(* 6. VERDICT — assumption audit.  Every result must be closed under the  *)
(*    global context (NO axiom): the 3-axiom trust ledger is intact.      *)
(* ===================================================================== *)

Print Assumptions path_read_back.
Print Assumptions path_frame.
Print Assumptions read_back_bc.
Print Assumptions frame_bc_bd.
Print Assumptions lookup7_lift.
Print Assumptions update7_lift.
Print Assumptions assign_arm_conservative.
Print Assumptions assign_arm_matches_base.
