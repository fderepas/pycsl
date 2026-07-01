(* Phase3_SOS.v — Structural Operational Semantics
   Extended with exec_state (Phase 3a), SBreak/SAssert (Phase 2),
   SGhostDecl/SGhostAssign/SLabel (Phase 3a), SRaise/STryCatch (Phase 5),
   SCritical/SThreadEntry (Phase 8). *)

Require Import ZArith String List Bool.
Require Import Phase1_AST.
Require Import Phase2_State.
Require Import Phase3b_DesugarDef.
Open Scope Z_scope.

(* ===== Execution outcomes =====
   Now carry full exec_state so ghost and label tracking is preserved. *)
Inductive outcome : Type :=
  | ONormal    (es : exec_state)
  | OReturned  (es : exec_state) (v : val)
  | OContinued (es : exec_state)
  | OBroke     (es : exec_state)             (* Phase 2: break *)
  | OFailed    (es : exec_state) (msg : string)  (* Phase 2: assert failure *)
  | OThrew     (es : exec_state) (exc : ident).  (* Phase 5: exception *)

(* ===== Ghost expression evaluator =====
   Evaluates ghost_expr (= contract_expr) in exec_state context. *)
Definition eval_ghost_int (es : exec_state) (e : ghost_expr) : Z :=
  eval_z es.(reg_state) es.(reg_state) None e.

(* Apply augmented assignment operation to a ghost int value *)
Definition apply_aug_op (op : aug_op) (cur rhs : Z) : Z :=
  match op with
  | AugAdd => cur + rhs
  | AugSub => cur - rhs
  | AugMul => cur * rhs
  end.

(* ===== Phase 3b: typed ghost evaluators ===== *)

(* Ghost list evaluator — evaluates CGNil/CGCons/CGAppend/CGTl into list Z *)
Fixpoint eval_ghost_list (es : exec_state) (e : ghost_expr) : list Z :=
  match e with
  | CGNil          => nil
  | CGCons h t     => eval_ghost_int es h :: eval_ghost_list es t
  | CGAppend l1 l2 => eval_ghost_list es l1 ++ eval_ghost_list es l2
  | CGTl l         => match eval_ghost_list es l with _ :: t => t | nil => nil end
  | CVar x         => match ghost_lookup es.(ghost_st) x with
                      | Some (GVList l) => l | _ => nil end
  | _              => nil
  end.

(* Sorted-list helpers for ghost_set model *)
Fixpoint set_add_z (x : Z) (s : list Z) : list Z :=
  match s with
  | nil => x :: nil
  | h :: t =>
    if Z.ltb x h then x :: h :: t
    else if Z.eqb x h then s
    else h :: set_add_z x t
  end.

Fixpoint set_remove_z (x : Z) (s : list Z) : list Z :=
  match s with
  | nil => nil
  | h :: t => if Z.eqb x h then t else h :: set_remove_z x t
  end.

(* Ghost set evaluator — sorted-list model *)
Fixpoint eval_ghost_set (es : exec_state) (e : ghost_expr) : list Z :=
  match e with
  | CGSetEmpty         => nil
  | CGSetAdd elem s    => set_add_z (eval_ghost_int es elem) (eval_ghost_set es s)
  | CGSetRemove elem s => set_remove_z (eval_ghost_int es elem) (eval_ghost_set es s)
  | CVar x             => match ghost_lookup es.(ghost_st) x with
                          | Some (GVSet s) => s | _ => nil end
  | _                  => nil
  end.

(* Ghost dict evaluator — association-list model.
   CGMapSet d k v: update key k to v in dict d (replaces existing binding).
   CGMapRemove d k: remove key k from dict d. *)
Fixpoint eval_ghost_dict (es : exec_state) (e : ghost_expr) : list (Z * Z) :=
  match e with
  | CGMapEmpty => nil
  | CGMapSet d k v =>
    let dict := eval_ghost_dict es d in
    let kz   := eval_ghost_int es k in
    let vz   := eval_ghost_int es v in
    (kz, vz) :: List.filter (fun p => negb (Z.eqb (fst p) kz)) dict
  | CGMapRemove d k =>
    let dict := eval_ghost_dict es d in
    let kz   := eval_ghost_int es k in
    List.filter (fun p => negb (Z.eqb (fst p) kz)) dict
  | CVar x => match ghost_lookup es.(ghost_st) x with
              | Some (GVDict d) => d | _ => nil end
  | _      => nil
  end.

(* Ghost string evaluator — concatenation and variable lookup *)
Fixpoint eval_ghost_string (es : exec_state) (e : ghost_expr) : string :=
  match e with
  | CVar x => match ghost_lookup es.(ghost_st) x with
              | Some (GVString s) => s | _ => "" end
  | CGStrConcat s1 s2 =>
    String.append (eval_ghost_string es s1) (eval_ghost_string es s2)
  | _ => ""
  end.

(* Ghost tuple evaluators — evaluate expressions as tuple components *)
Definition eval_ghost_tuple2 (es : exec_state) (e : ghost_expr) : Z * Z :=
  match e with
  | CGMkTuple2 e1 e2 =>
    (eval_ghost_int es e1, eval_ghost_int es e2)
  | CVar x => match ghost_lookup es.(ghost_st) x with
              | Some (GVTuple2 a b) => (a, b) | _ => (0, 0) end
  | _ => (0, 0)
  end.

Definition eval_ghost_tuple3 (es : exec_state) (e : ghost_expr) : Z * Z * Z :=
  match e with
  | CGMkTuple3 e1 e2 e3 =>
    (eval_ghost_int es e1, eval_ghost_int es e2, eval_ghost_int es e3)
  | CVar x => match ghost_lookup es.(ghost_st) x with
              | Some (GVTuple3 a b c) => (a, b, c) | _ => (0, 0, 0) end
  | _ => (0, 0, 0)
  end.

Definition eval_ghost_tuple4 (es : exec_state) (e : ghost_expr) : Z * Z * Z * Z :=
  match e with
  | CGMkTuple4 e1 e2 e3 e4 =>
    (eval_ghost_int es e1, eval_ghost_int es e2,
     eval_ghost_int es e3, eval_ghost_int es e4)
  | CVar x => match ghost_lookup es.(ghost_st) x with
              | Some (GVTuple4 a b c d) => (a, b, c, d) | _ => (0, 0, 0, 0) end
  | _ => (0, 0, 0, 0)
  end.

(* Typed ghost value evaluator — dispatches on ghost_type *)
Definition eval_ghost_val (t : ghost_type) (es : exec_state) (e : ghost_expr) : ghost_val :=
  match t with
  | GTInt    => GVInt    (eval_ghost_int es e)
  | GTString => GVString (eval_ghost_string es e)
  | GTArray  => GVArray  (eval_ghost_list es e)
  | GTList   => GVList   (eval_ghost_list es e)
  | GTDict   => GVDict   (eval_ghost_dict es e)
  | GTSet    => GVSet    (eval_ghost_set es e)
  | GTTuple2 =>
    match eval_ghost_tuple2 es e with (a, b)       => GVTuple2 a b       end
  | GTTuple3 =>
    match eval_ghost_tuple3 es e with (a, b, c)    => GVTuple3 a b c     end
  | GTTuple4 =>
    match eval_ghost_tuple4 es e with (a, b, c, d) => GVTuple4 a b c d   end
  end.

(* Typed augmented assignment for ghost values.
   cur: current ghost_val from ghost_st; rhs: ghost_expr to evaluate as RHS.
   For collections (dict, set), rhs is the full new-value expression incorporating cur. *)
Definition apply_ghost_aug (op : aug_op) (cur : ghost_val) (es : exec_state) (rhs : ghost_expr) : ghost_val :=
  match cur with
  | GVInt n =>
    GVInt (apply_aug_op op n (eval_ghost_int es rhs))
  | GVList l =>
    match op with
    | AugAdd => GVList (l ++ eval_ghost_list es rhs)
    | _ => GVList l
    end
  | GVArray a =>
    match op with
    | AugAdd => GVArray (a ++ eval_ghost_list es rhs)
    | _ => GVArray a
    end
  | GVString s =>
    match op with
    | AugAdd => GVString (String.append s (eval_ghost_string es rhs))
    | _ => GVString s
    end
  | GVDict _ =>
    GVDict (eval_ghost_dict es rhs)
  | GVSet _ =>
    GVSet (eval_ghost_set es rhs)
  | _ => cur   (* GVTuple*: no standard augmented-assign semantics *)
  end.

(* ===== Execution relation =====
   exec es s out: starting from exec_state es, statement s produces outcome out.
   All outcomes carry an exec_state. Ghost stmts only change ghost_st/label_snaps. *)
Inductive exec : exec_state -> stmt -> outcome -> Prop :=

  | ExecSkip :
      forall es, exec es SSkip (ONormal es)

  | ExecAssign :
      forall es x e,
      exec es (SAssign x e)
        (ONormal (set_reg es (update es.(reg_state) x (eval_expr es.(reg_state) e))))

  | ExecAugAssign :
      forall es x op e,
      let cur := match lookup es.(reg_state) x with Some (VInt n) => n | _ => 0 end in
      let nv  := eval_binop_z op cur
                   (match eval_expr es.(reg_state) e with VInt n => n | _ => 0 end) in
      exec es (SAugAssign x op e)
        (ONormal (set_reg es (update es.(reg_state) x (VInt nv))))

  | ExecArraySet :
      forall es arr i v,
      let idx := match eval_expr es.(reg_state) i with VInt n => n | _ => 0 end in
      let nv  := match eval_expr es.(reg_state) v with VInt n => n | _ => 0 end in
      exec es (SArraySet arr i v)
        (ONormal (set_reg es (array_update es.(reg_state) arr idx nv)))

  | ExecSeq :
      forall es s1 s2 es' out,
      exec es s1 (ONormal es') ->
      exec es' s2 out ->
      exec es (SSeq s1 s2) out

  | ExecSeqReturn :
      forall es s1 s2 es' v,
      exec es s1 (OReturned es' v) ->
      exec es (SSeq s1 s2) (OReturned es' v)

  | ExecSeqContinue :
      forall es s1 s2 es',
      exec es s1 (OContinued es') ->
      exec es (SSeq s1 s2) (OContinued es')

  | ExecSeqBreak :
      forall es s1 s2 es',
      exec es s1 (OBroke es') ->
      exec es (SSeq s1 s2) (OBroke es')

  | ExecSeqThrow :
      forall es s1 s2 es' exc,
      exec es s1 (OThrew es' exc) ->
      exec es (SSeq s1 s2) (OThrew es' exc)

  | ExecIfTrue :
      forall es cond s1 s2 out,
      eval_bool es.(reg_state) cond = true ->
      exec es s1 out ->
      exec es (SIf cond s1 s2) out

  | ExecIfFalse :
      forall es cond s1 s2 out,
      eval_bool es.(reg_state) cond = false ->
      exec es s2 out ->
      exec es (SIf cond s1 s2) out

  | ExecWhileTrue :
      forall es inv var cond body es' out,
      eval_bool es.(reg_state) cond = true ->
      exec es body (ONormal es') ->
      exec es' (SWhile inv var cond body) out ->
      exec es (SWhile inv var cond body) out

  | ExecWhileContinue :
      forall es inv var cond body es' out,
      eval_bool es.(reg_state) cond = true ->
      exec es body (OContinued es') ->
      exec es' (SWhile inv var cond body) out ->
      exec es (SWhile inv var cond body) out

  | ExecWhileBreak :
      forall es inv var cond body es',
      eval_bool es.(reg_state) cond = true ->
      exec es body (OBroke es') ->
      exec es (SWhile inv var cond body) (ONormal es')

  | ExecWhileFalse :
      forall es inv var cond body,
      eval_bool es.(reg_state) cond = false ->
      exec es (SWhile inv var cond body) (ONormal es)

  | ExecContinue :
      forall es, exec es SContinue (OContinued es)

  | ExecBreak :
      forall es, exec es SBreak (OBroke es)

  | ExecReturn :
      forall es e,
      exec es (SReturn e)
        (OReturned
           (set_reg es (update es.(reg_state) "\result" (eval_expr es.(reg_state) e)))
           (eval_expr es.(reg_state) e))

  | ExecAssertPass :
      forall es cond msg,
      eval_contract es.(reg_state) es.(reg_state) None cond ->
      exec es (SAssert cond msg) (ONormal es)

  | ExecAssertFail :
      forall es cond msg,
      ~ eval_contract es.(reg_state) es.(reg_state) None cond ->
      exec es (SAssert cond msg) (OFailed es msg)

  | ExecTupleUnpack :
      forall es xs e,
      exec es (STupleUnpack xs e) (ONormal es)  (* simplified: no list destructuring *)

  (* Phase 3a/3b: ghost statements — typed evaluation via eval_ghost_val *)
  | ExecGhostDecl :
      forall es x t e,
      exec es (SGhostDecl x t e)
        (ONormal (set_ghost es (ghost_update es.(ghost_st) x (eval_ghost_val t es e))))

  | ExecGhostAssign :
      forall es x t op e,
      let cur := match ghost_lookup es.(ghost_st) x with Some v => v | None => GVInt 0 end in
      let nv  := apply_ghost_aug op cur es e in
      exec es (SGhostAssign x t op e)
        (ONormal (set_ghost es (ghost_update es.(ghost_st) x nv)))

  | ExecLabel :
      forall es L,
      exec es (SLabel L)
        (ONormal (set_labels es ((L, es.(ghost_st)) :: es.(label_snaps))))

  (* Phase 5: exception statements *)
  | ExecRaise :
      forall es exc,
      exec es (SRaise exc) (OThrew es exc)

  | ExecTryCatchCaught :
      forall es s1 exc handler es' out,
      exec es s1 (OThrew es' exc) ->
      exec es' handler out ->
      exec es (STryCatch s1 exc handler) out

  | ExecTryCatchMiss :
      forall es s1 exc handler es' exc',
      exec es s1 (OThrew es' exc') ->
      exc' <> exc ->
      exec es (STryCatch s1 exc handler) (OThrew es' exc')

  | ExecTryCatchNormal :
      forall es s1 exc handler es',
      exec es s1 (ONormal es') ->
      exec es (STryCatch s1 exc handler) (ONormal es')

  (* Phase 6: field assignment — flat-key field-state model.
     `self.f` is the synthetic register variable `self ++ "." ++ f`
     (the same name Module 6 emits and that `eval_expr (EFieldGet …)`
     reads), so a write updates exactly the key a later read observes.
     This matches the now-concrete Why3 LINK-3 `field_effect`. *)
  | ExecFieldAssign :
      forall es self_id f e,
      exec es (SFieldAssign self_id f e)
        (ONormal (set_reg es (update es.(reg_state) (self_id ++ "." ++ f)
                    (eval_expr es.(reg_state) e))))

  | ExecFieldAugAssign :
      forall es self_id f op e,
      let cur := match lookup es.(reg_state) (self_id ++ "." ++ f) with
                 | Some (VInt n) => n | _ => 0 end in
      let nv  := eval_binop_z op cur
                   (match eval_expr es.(reg_state) e with VInt n => n | _ => 0 end) in
      exec es (SFieldAugAssign self_id f op e)
        (ONormal (set_reg es (update es.(reg_state) (self_id ++ "." ++ f) (VInt nv))))

  (* Phase 8: concurrent statements (placeholder — Phase 8 adds proper semantics) *)
  | ExecCritical :
      forall es mutex body out,
      exec es body out ->
      exec es (SCritical mutex body) out

  | ExecThreadEntry :
      forall es body out,
      exec es body out ->
      exec es (SThreadEntry body) out

  (* SFor desugars to index-variable SWhile *)
  | ExecFor :
      forall es x arr inv var body aim out,
      exec es (desugar (SFor x arr inv var body aim)) out ->
      exec es (SFor x arr inv var body aim) out

  (* Phase 7: acquires/releases — Hoare-instance identity stubs.
     No lock state in exec_state; real lock discipline is the deferred
     ConcurrentMM instance (see Phase7_MemModel.v). *)
  | ExecAcquires :
      forall es m,
      exec es (SAcquires m) (ONormal es)

  | ExecReleases :
      forall es m,
      exec es (SReleases m) (ONormal es)

  (* Phase 8 — Lambda (Category A, optional). *)
  | ExecCall :
      forall es r fn arg param body cstate st' v,
      eval_expr es.(reg_state) fn = VClosure param body cstate ->
      exec (set_reg (mk_exec_state cstate)
                    (update cstate param (eval_expr es.(reg_state) arg)))
           body (OReturned st' v) ->
      exec es (SCall r fn arg) (ONormal (set_reg es (update es.(reg_state) r v)))

  (* Phase 8 — Lambda construction. `SLambda x param body` binds the
     closure value capturing the current reg_state. Leaf; mirrors ExecAssign. *)
  | ExecLambda :
      forall es x param body,
      exec es (SLambda x param body)
        (ONormal (set_reg es (update es.(reg_state) x
                    (VClosure param body es.(reg_state))))).

Lemma lookup_update_eq :
  forall (st : state) (x : ident) (v : val),
  lookup (update st x v) x = Some v.
Proof.
  intros st x v. unfold update. simpl.
  rewrite String.eqb_refl. reflexivity.
Qed.

Lemma returned_state_has_result :
  forall es s out,
  exec es s out ->
  match out with
  | OReturned st' v => lookup st'.(reg_state) "\result" = Some v
  | _ => True
  end.
Proof.
  intros es s out H.
  induction H; simpl in *;
    try exact I;
    try assumption;
    try reflexivity.
Qed.

(* ===== Determinism ===== *)
Lemma exec_deterministic :
  forall es s out1 out2,
  exec es s out1 -> exec es s out2 -> out1 = out2.
Proof.
  intros es s out1 out2 H1 H2.
  revert out2 H2.
  induction H1; intros out2 H2; inversion H2; subst;
    try reflexivity; try congruence; try contradiction;
    repeat (
      match goal with
      (* Phase 8 ExecCall: unify VClosure parameters from the two hfn premises *)
      | [ H1 : eval_expr ?st ?fn = VClosure ?p1 ?b1 ?c1,
          H2 : eval_expr ?st ?fn = VClosure ?p2 ?b2 ?c2 |- _ ] =>
          rewrite H1 in H2; injection H2 as Hp Hb Hc; subst
      | [ IH : forall o, exec ?e ?s o -> ?r = o,
          H  : exec ?e ?s ?o |- _ ] =>
          apply IH in H;
          first [ discriminate H
                | injection H; intros; subst
                | idtac ]
      end);
    try reflexivity; try congruence; try contradiction; auto.
Qed.
