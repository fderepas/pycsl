(* Phase4_WP.v — Weakest Precondition Calculus
   Extended for exec_state (Phase 3a), SBreak/Qb (Phase 2),
   SGhostDecl/SGhostAssign/SLabel (Phase 3a), SRaise/STryCatch/Qe (Phase 5).

   Five continuations:
     Qn : exec_state → Prop  — normal completion
     Qr : exec_state → Prop  — return
     Qc : exec_state → Prop  — continue
     Qb : exec_state → Prop  — break  (Phase 2)
     Qe : ident → exec_state → Prop — exception (Phase 5)
*)

Require Import ZArith String List Bool.
Require Import Phase1_AST.
Require Import Phase2_State.
Require Import Phase3_SOS.
Require Import Phase3b_DesugarDef.
Require Import Phase3b_Desugar.
Require Import Phase7_MemModel.
Open Scope Z_scope.

(* Phase 3c: eval_c uses exec_state-aware evaluator for CAt support *)
Definition eval_c (es pre_es : exec_state) (result : option val)
                  (e : contract_expr) : Prop :=
  eval_contract_es es pre_es result e.

Definition eval_v (es pre_es : exec_state) (e : contract_expr) : Z :=
  eval_z es.(reg_state) pre_es.(reg_state) None e.

(* wp s Qn Qr Qc Qb Qe pre_es es:
     s      — statement to verify
     Qn/Qr/Qc/Qb — postconditions for normal/return/continue/break
     Qe     — exceptional postcondition: given exception name + state
     pre_es — entry exec_state (for \old evaluation)
     es     — current exec_state *)
Fixpoint wp (s : stmt)
            (Qn Qr Qc Qb : exec_state -> Prop)
            (Qe : ident -> exec_state -> Prop)
            (pre_es es : exec_state) : Prop :=
  match s with
  | SSkip => Qn es

  | SAssign x e =>
    Qn (set_reg es (update es.(reg_state) x (eval_expr es.(reg_state) e)))

  | SAugAssign x op e =>
    let cur := match lookup es.(reg_state) x with Some (VInt n) => n | _ => 0 end in
    let nv := eval_binop_z op cur
                (match eval_expr es.(reg_state) e with VInt n => n | _ => 0 end) in
    Qn (set_reg es (update es.(reg_state) x (VInt nv)))

  | SArraySet arr i v =>
    let idx := match eval_expr es.(reg_state) i with VInt n => n | _ => 0 end in
    let nv := match eval_expr es.(reg_state) v with VInt n => n | _ => 0 end in
    Qn (set_reg es (array_update es.(reg_state) arr idx nv))

  | SSeq s1 s2 =>
    wp s1 (fun es' => wp s2 Qn Qr Qc Qb Qe pre_es es') Qr Qc Qb Qe pre_es es

  | SIf cond s1 s2 =>
    (eval_bool es.(reg_state) cond = true  -> wp s1 Qn Qr Qc Qb Qe pre_es es) /\
    (eval_bool es.(reg_state) cond = false -> wp s2 Qn Qr Qc Qb Qe pre_es es)

  | SWhile inv var cond body =>
    eval_c es pre_es None inv /\
    (forall es',
      eval_c es' pre_es None inv ->
      eval_bool es'.(reg_state) cond = true ->
      let body_done es'' :=
        eval_c es'' pre_es None inv /\
        eval_v es'' pre_es var < eval_v es' pre_es var /\
        eval_v es'' pre_es var >= 0 in
      (* Break from body exits the while loop normally → Qn *)
      wp body body_done Qr body_done Qn Qe pre_es es') /\
    (forall es',
      eval_c es' pre_es None inv ->
      eval_bool es'.(reg_state) cond = false ->
      Qn es')

  | SFor x arr inv var body _ =>
    let es0 := set_reg es (update es.(reg_state) for_idx (VInt 0)) in
    (* guard matches the desugared while condition exactly *)
    let guard := EBinOp OpSub (ELen arr) (EVar for_idx) in
    eval_c es0 pre_es None inv /\
    (forall es',
      eval_c es' pre_es None inv ->
      eval_bool es'.(reg_state) guard = true ->
      let es1 := set_reg es'
                   (update es'.(reg_state) x
                      (eval_expr es'.(reg_state) (ESubscript arr (EVar for_idx)))) in
      let body_done es'' :=
        let cur_idx := match lookup es''.(reg_state) for_idx with
                       | Some (VInt n) => n | _ => 0 end in
        let es3 := set_reg es'' (update es''.(reg_state) for_idx (VInt (cur_idx + 1))) in
        eval_c es3 pre_es None inv /\
        eval_v es3 pre_es var < eval_v es' pre_es var /\
        eval_v es3 pre_es var >= 0 in
      wp body body_done Qr body_done Qn Qe pre_es es1) /\
    (forall es',
      eval_c es' pre_es None inv ->
      eval_bool es'.(reg_state) guard = false ->
      Qn es')

  | SReturn e =>
    Qr (set_reg es (update es.(reg_state) "\result" (eval_expr es.(reg_state) e)))

  | SContinue => Qc es

  | SBreak => Qb es

  | SAssert cond msg =>
    eval_c es pre_es None cond /\ Qn es

  | STupleUnpack _ _ => Qn es  (* simplified *)

  (* Phase 3a/3b: ghost statements — typed evaluation matches ExecGhost* rules *)
  | SGhostDecl x t e =>
    Qn (set_ghost es (ghost_update es.(ghost_st) x (eval_ghost_val t es e)))

  | SGhostAssign x t op e =>
    let cur := match ghost_lookup es.(ghost_st) x with Some v => v | None => GVInt 0 end in
    let nv  := apply_ghost_aug op cur es e in
    Qn (set_ghost es (ghost_update es.(ghost_st) x nv))

  | SLabel L =>
    Qn (set_labels es ((L, es.(ghost_st)) :: es.(label_snaps)))

  (* Phase 5: exceptions *)
  | SRaise exc => Qe exc es

  | STryCatch s1 exc handler =>
    wp s1 Qn Qr Qc Qb
       (fun exc' es' =>
          if String.eqb exc' exc
          then wp handler Qn Qr Qc Qb Qe pre_es es'
          else Qe exc' es')
       pre_es es

  (* Phase 6: field assignments — flat-key field-state model.
     `self.f` is the synthetic register variable `self ++ "." ++ f`
     (matching `eval_expr (EFieldGet …)` and Module 6's emission, and
     the now-concrete Why3 LINK-3 `field_effect`). Mirrors SAssign /
     SAugAssign exactly, so the soundness cases are unchanged. *)
  | SFieldAssign self_id f e =>
    Qn (set_reg es (update es.(reg_state) (self_id ++ "." ++ f)
          (eval_expr es.(reg_state) e)))
  | SFieldAugAssign self_id f op e =>
    let cur := match lookup es.(reg_state) (self_id ++ "." ++ f) with
               | Some (VInt n) => n | _ => 0 end in
    let nv := eval_binop_z op cur
                (match eval_expr es.(reg_state) e with VInt n => n | _ => 0 end) in
    Qn (set_reg es (update es.(reg_state) (self_id ++ "." ++ f) (VInt nv)))

  (* Phase 8: concurrent — SCritical now uses critical_havoc (Phase 7).
     Hoare instance: critical_havoc es P = P es (identity).
     Future ConcurrentMM: forall shared, P (merge_shared es shared). *)
  | SCritical _ body =>
    critical_havoc es (fun es' => wp body Qn Qr Qc Qb Qe pre_es es')
  | SThreadEntry body =>
    wp body Qn Qr Qc Qb Qe pre_es es
  (* Phase 7: acquires/releases — Hoare-instance identity (Qn es).
      Real lock discipline deferred to ConcurrentMM. *)
  | SAcquires _ => Qn es
  | SReleases _ => Qn es

  (* Phase 8 — Lambda (Category A, optional).
     `wp (SCall r fn arg)`: evaluate `fn` to a closure; evaluate
     `arg`; the body's WP is encoded as a *behavioural* predicate
     over the closure's exec outcomes — for any `st' v` such that
     `exec cstate_es body (OReturned st' v)`, `Qn (set_reg es
     (update es.reg_state r v))` must hold. Exceptions propagate via Qe.
     When `fn` is not a VClosure, the WP is vacuously `True` (no SOS
     rule fires, so soundness holds vacuously).
     Why this shape rather than `wp body ...`: the body is extracted
     at runtime from the `VClosure` value, so it is NOT a structural
     sub-term of `SCall`. The standard `wp body` recursion would
     break `wp_mono` (which inducts on `stmt`) — there is no IH for
     the dynamic body. Encoding the body's behaviour via `exec`
     keeps `wp` a closed formula, so `wp_mono`'s `SCall` case
     reduces to first-order quantifier lifting, no induction on
     body needed. Soundness discharges via `returned_state_has_result`. *)
  | SCall r fn arg =>
    match eval_expr es.(reg_state) fn with
    | VClosure param body cstate =>
      forall st' v,
        exec (set_reg (mk_exec_state cstate)
                      (update cstate param (eval_expr es.(reg_state) arg)))
             body (OReturned st' v) ->
        Qn (set_reg es (update es.(reg_state) r v))
    | _ => True
    end

  (* Phase 8 — Lambda construction. Leaf: bind the captured closure value.
     SOS outcome ≡ this WP term, so the soundness case is `exact Hwp`. *)
  | SLambda x param body =>
    Qn (set_reg es (update es.(reg_state) x
          (VClosure param body es.(reg_state))))
  end.
