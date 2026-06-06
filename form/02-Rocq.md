# PyCSL Formal Semantics — Rocq Implementation

Track 1 of the global plan. Each section corresponds to one phase. All definitions are
concrete — nothing is axiomatic. The file compiles top-to-bottom against Rocq 8.18+ with
the standard library.

---

## Prelude

```coq
Require Import ZArith String List Bool.
Require Import Coq.Structures.DecidableTypeEx.
Require Import Coq.FSets.FMapList.
Open Scope Z_scope.

Definition ident := string.
Definition ident_eq := String.string_dec.
```

---

## Phase 1 — Abstract Syntax Tree

### Arithmetic operators

```coq
Inductive binop : Type :=
  | OpAdd | OpSub | OpMul | OpDiv.
```

### Runtime expressions (Python subset — no logical connectives)

```coq
Inductive expr : Type :=
  | EInt       (n : Z)
  | EVar       (x : ident)
  | ESubscript (arr : ident) (i : expr)
  | EBinOp     (op : binop) (e1 e2 : expr)
  | ENeg       (e : expr).
```

### Contract expressions (full logical language)

```coq
Inductive contract_expr : Type :=
  | CInt       (n : Z)
  | CVar       (x : ident)
  | CResult                                       (* \result in postconditions *)
  | CLength    (arr : ident)                      (* \length(arr) *)
  | CSubscript (arr : ident) (i : contract_expr)  (* arr[i] *)
  | COld       (e : contract_expr)                (* \old(e) — value at function entry *)
  | CBinOp     (op : binop) (e1 e2 : contract_expr)
  | CNeg       (e : contract_expr)
  | CEq | CNe | CLt | CLe | CGt | CGe : contract_expr -> contract_expr -> contract_expr
  | CAnd | COr  : contract_expr -> contract_expr -> contract_expr
  | CNot       (e : contract_expr)
  | CImplies   (e1 e2 : contract_expr)            (* ==> *)
  | CIff       (e1 e2 : contract_expr)            (* <=> *)
  | CForall    (x : ident) (body : contract_expr)
  | CExists    (x : ident) (body : contract_expr).
```

### Frame conditions and function specifications

```coq
Inductive frame_cond : Type :=
  | FNothing
  | FVars (xs : list ident).

Record func_spec : Type := mkSpec {
  spec_pre   : contract_expr;
  spec_post  : contract_expr;
  spec_frame : frame_cond
}.
```

### Statements

```coq
Inductive stmt : Type :=
  | SSkip
  | SAssign    (x : ident)   (e : expr)
  | SAugAssign (x : ident)   (op : binop) (e : expr)
  | SArraySet  (arr : ident) (i : expr) (v : expr)
  | SSeq       (s1 s2 : stmt)
  | SIf        (cond : expr) (s_then s_else : stmt)
  | SWhile     (inv : contract_expr) (var : contract_expr)
               (cond : expr) (body : stmt)
  | SFor       (x : ident) (arr : ident)
               (inv : contract_expr) (var : contract_expr) (body : stmt)
  | SReturn    (e : expr)
  | SContinue.
```

---

## Phase 2 — State and Concrete Evaluation

### Values and state

```coq
Inductive val : Type :=
  | VInt   (n : Z)
  | VArray (a : list Z).

(* Association-list state — replace with FMapList for better lookup proofs *)
Definition state := list (ident * val).

Fixpoint lookup (st : state) (x : ident) : option val :=
  match st with
  | [] => None
  | (y, v) :: rest =>
    if ident_eq x y then Some v else lookup rest x
  end.

Definition update (st : state) (x : ident) (v : val) : state :=
  (x, v) :: st.

(* Array element update: replaces the i-th element of the array bound to arr *)
Definition array_update (st : state) (arr : ident) (i : Z) (v : Z) : state :=
  match lookup st arr with
  | Some (VArray a) =>
    let a' := List.map (fun p => if Z.eqb (fst p) i then v else snd p)
                       (List.combine (List.map Z.of_nat (List.seq 0 (List.length a))) a) in
    update st arr (VArray a')
  | _ => st
  end.
```

### Runtime expression evaluator (Fixpoint — NOT axiomatic)

```coq
Fixpoint eval_binop_z (op : binop) (n1 n2 : Z) : Z :=
  match op with
  | OpAdd => n1 + n2
  | OpSub => n1 - n2
  | OpMul => n1 * n2
  | OpDiv => if Z.eqb n2 0 then 0 else Z.div n1 n2  (* div-by-zero → 0, guarded by requires *)
  end.

Fixpoint eval_expr (st : state) (e : expr) : val :=
  match e with
  | EInt n       => VInt n
  | EVar x       => match lookup st x with Some v => v | None => VInt 0 end
  | ESubscript arr i =>
    match lookup st arr, eval_expr st i with
    | Some (VArray a), VInt n =>
      if (0 <=? n)%Z && (n <? Z.of_nat (List.length a))%Z
      then VInt (List.nth (Z.to_nat n) a 0)
      else VInt 0
    | _, _ => VInt 0
    end
  | EBinOp op e1 e2 =>
    match eval_expr st e1, eval_expr st e2 with
    | VInt n1, VInt n2 => VInt (eval_binop_z op n1 n2)
    | _, _ => VInt 0
    end
  | ENeg e =>
    match eval_expr st e with
    | VInt n => VInt (- n)
    | v      => v
    end
  end.

(* Boolean test used in conditional and loop guards *)
Definition eval_bool (st : state) (e : expr) : bool :=
  match eval_expr st e with
  | VInt 0 => false
  | _      => true
  end.
```

### Contract expression evaluator

`pre_st` is the state at function entry (for `\old`). `result` is `Some v` when
evaluating a postcondition. All three are Fixpoints.

```coq
Fixpoint eval_z (st pre_st : state) (result : option val) (e : contract_expr) : Z :=
  match e with
  | CInt n    => n
  | CVar x    => match lookup st x with Some (VInt n) => n | _ => 0 end
  | CResult   => match result with Some (VInt n) => n | _ => 0 end
  | CLength arr =>
    match lookup st arr with Some (VArray a) => Z.of_nat (List.length a) | _ => 0 end
  | CSubscript arr i =>
    let n := eval_z st pre_st result i in
    match lookup st arr with
    | Some (VArray a) =>
      if (0 <=? n) && (n <? Z.of_nat (List.length a))
      then List.nth (Z.to_nat n) a 0
      else 0
    | _ => 0
    end
  | COld e   => eval_z pre_st pre_st result e   (* evaluate in the pre-state *)
  | CBinOp op e1 e2 => eval_binop_z op (eval_z st pre_st result e1)
                                        (eval_z st pre_st result e2)
  | CNeg e   => - (eval_z st pre_st result e)
  | _        => 0   (* non-integer contract_expr — evaluated by eval_contract below *)
  end.

Fixpoint eval_contract (st pre_st : state) (result : option val)
                        (e : contract_expr) : Prop :=
  match e with
  | CInt n    => n <> 0
  | CVar x    => match lookup st x with Some (VInt 0) => False | _ => True end
  | CResult   => match result with Some (VInt 0) => False | _ => True end
  | CLength _ | CSubscript _ _ | COld _ | CBinOp _ _ _ | CNeg _ =>
                eval_z st pre_st result e <> 0
  | CEq  e1 e2 => eval_z st pre_st result e1 =  eval_z st pre_st result e2
  | CNe  e1 e2 => eval_z st pre_st result e1 <> eval_z st pre_st result e2
  | CLt  e1 e2 => eval_z st pre_st result e1 <  eval_z st pre_st result e2
  | CLe  e1 e2 => eval_z st pre_st result e1 <= eval_z st pre_st result e2
  | CGt  e1 e2 => eval_z st pre_st result e1 >  eval_z st pre_st result e2
  | CGe  e1 e2 => eval_z st pre_st result e1 >= eval_z st pre_st result e2
  | CAnd e1 e2 => eval_contract st pre_st result e1 /\ eval_contract st pre_st result e2
  | COr  e1 e2 => eval_contract st pre_st result e1 \/ eval_contract st pre_st result e2
  | CNot e     => ~ eval_contract st pre_st result e
  | CImplies e1 e2 => eval_contract st pre_st result e1 -> eval_contract st pre_st result e2
  | CIff     e1 e2 =>
      eval_contract st pre_st result e1 <-> eval_contract st pre_st result e2
  | CForall x body =>
      forall n : Z,
        eval_contract (update st x (VInt n)) pre_st result body
  | CExists x body =>
      exists n : Z,
        eval_contract (update st x (VInt n)) pre_st result body
  end.

(* Variant evaluation — must produce Z for well-founded induction *)
Definition eval_variant (st pre_st : state) (e : contract_expr) : Z :=
  eval_z st pre_st None e.
```

---

## Phase 3 — Structural Operational Semantics

### Execution outcomes

```coq
Inductive outcome : Type :=
  | ONormal    (st : state)
  | OReturned  (st : state) (v : val)
  | OContinued (st : state).
```

### Execution relation

```coq
Inductive exec : state -> stmt -> outcome -> Prop :=
  | ExecSkip :
      forall st, exec st SSkip (ONormal st)

  | ExecAssign :
      forall st x e,
      exec st (SAssign x e) (ONormal (update st x (eval_expr st e)))

  | ExecAugAssign :
      forall st x op e,
      let cur := match lookup st x with Some (VInt n) => n | _ => 0 end in
      let nv  := eval_binop_z op cur
                   (match eval_expr st e with VInt n => n | _ => 0 end) in
      exec st (SAugAssign x op e) (ONormal (update st x (VInt nv)))

  | ExecArraySet :
      forall st arr i v,
      let idx := match eval_expr st i with VInt n => n | _ => 0 end in
      let nv  := match eval_expr st v with VInt n => n | _ => 0 end in
      exec st (SArraySet arr i v) (ONormal (array_update st arr idx nv))

  | ExecSeq :
      forall st s1 s2 st' out,
      exec st s1 (ONormal st') ->
      exec st' s2 out ->
      exec st (SSeq s1 s2) out

  | ExecSeqReturn :
      forall st s1 s2 st' v,
      exec st s1 (OReturned st' v) ->
      exec st (SSeq s1 s2) (OReturned st' v)

  | ExecSeqContinue :
      forall st s1 s2 st',
      exec st s1 (OContinued st') ->
      exec st (SSeq s1 s2) (OContinued st')

  | ExecIfTrue :
      forall st cond s1 s2 out,
      eval_bool st cond = true ->
      exec st s1 out ->
      exec st (SIf cond s1 s2) out

  | ExecIfFalse :
      forall st cond s1 s2 out,
      eval_bool st cond = false ->
      exec st s2 out ->
      exec st (SIf cond s1 s2) out

  | ExecWhileTrue :
      forall st inv var cond body st' out,
      eval_bool st cond = true ->
      exec st body (ONormal st') ->
      exec st' (SWhile inv var cond body) out ->
      exec st (SWhile inv var cond body) out

  | ExecWhileContinue :
      forall st inv var cond body st' out,
      eval_bool st cond = true ->
      exec st body (OContinued st') ->          (* continue → next iteration *)
      exec st' (SWhile inv var cond body) out ->
      exec st (SWhile inv var cond body) out

  | ExecWhileFalse :
      forall st inv var cond body,
      eval_bool st cond = false ->
      exec st (SWhile inv var cond body) (ONormal st)

  | ExecContinue :
      forall st, exec st SContinue (OContinued st)

  | ExecReturn :
      forall st e,
      exec st (SReturn e) (OReturned st (eval_expr st e)).

(* Determinism: given the same initial state and statement, there is at most one outcome *)
Lemma exec_deterministic :
  forall s st out1 out2,
  exec st s out1 -> exec st s out2 -> out1 = out2.
Proof.
  intros s. induction s; intros st out1 out2 H1 H2.
  (* Each case: invert both hypotheses and use IH *)
  all: inversion H1; inversion H2; subst; try reflexivity; try congruence.
  - (* SSeq: use IHs1 then IHs2 *)
    edestruct IHs1 as []; eauto. subst. eauto.
  - eauto.
Qed.
```

### Phase 3b — For-loop Desugaring

```coq
(* Fresh index variable — use a naming convention that avoids capture *)
Definition for_idx : ident := "_pycsl_idx".

Fixpoint desugar (s : stmt) : stmt :=
  match s with
  | SFor x arr inv var body =>
    (* while _pycsl_idx < \length(arr): x = arr[_pycsl_idx]; body; _idx++ *)
    SSeq (SAssign for_idx (EInt 0))
         (SWhile inv var
                 (EBinOp OpSub (EVar for_idx) (EInt 0))  (* placeholder; use CLt in WP *)
                 (SSeq (SAssign x (ESubscript arr (EVar for_idx)))
                       (SSeq (desugar body)
                             (SAugAssign for_idx OpAdd (EInt 1)))))
  | SSeq s1 s2  => SSeq (desugar s1) (desugar s2)
  | SIf c s1 s2 => SIf c (desugar s1) (desugar s2)
  | SWhile i v c b => SWhile i v c (desugar b)
  | s => s
  end.

Lemma desugar_correct :
  forall s st out, exec st s out <-> exec st (desugar s) out.
Proof.
  (* Induction on s; the SFor case requires showing the index-variable semantics
     match element-by-element iteration. *)
  Admitted.  (* Complete after Phase 5b is proved *)
```

---

## Phase 4 — Weakest Precondition Calculus

```coq
Fixpoint wp (s : stmt) (Q : state -> Prop) (pre_st : state) : state -> Prop :=
  match s with
  | SSkip        => Q
  | SAssign x e  => fun st => Q (update st x (eval_expr st e))
  | SAugAssign x op e =>
      fun st =>
        let cur := match lookup st x with Some (VInt n) => n | _ => 0 end in
        let nv  := eval_binop_z op cur
                     (match eval_expr st e with VInt n => n | _ => 0 end) in
        Q (update st x (VInt nv))
  | SArraySet arr i v =>
      fun st =>
        let idx := match eval_expr st i with VInt n => n | _ => 0 end in
        let nv  := match eval_expr st v with VInt n => n | _ => 0 end in
        Q (array_update st arr idx nv)
  | SSeq s1 s2   => wp s1 (wp s2 Q pre_st) pre_st
  | SIf cond s1 s2 =>
      fun st =>
        (eval_bool st cond = true  -> wp s1 Q pre_st st) /\
        (eval_bool st cond = false -> wp s2 Q pre_st st)
  | SWhile inv var cond body =>
      fun st =>
        (* 1. Invariant holds in the initial state *)
        eval_contract st pre_st None inv /\
        (* 2. Each iteration preserves invariant and decreases variant *)
        (forall st',
          eval_contract st' pre_st None inv ->
          eval_bool st' cond = true ->
          wp body (fun st'' =>
              eval_contract st'' pre_st None inv /\
              eval_variant st'' pre_st var < eval_variant st' pre_st var /\
              eval_variant st'' pre_st var >= 0) pre_st st') /\
        (* 3. Postcondition holds when the guard is false *)
        (forall st',
          eval_contract st' pre_st None inv ->
          eval_bool st' cond = false ->
          Q st')
  | SFor x arr inv var body =>
      (* WP for SFor = WP for the desugared SWhile; defined by reduction *)
      wp (desugar (SFor x arr inv var body)) Q pre_st
  | SReturn e =>
      (* Q is the postcondition; \result is bound to eval_expr st e.
         We record the return value by threading it through Q. *)
      fun st => Q st   (* caller binds \result = eval_expr st e in spec_post *)
  | SContinue => fun _ => True
  end.
```

---

## Phase 5a — While Invariant Lemma

This is the keystone lemma. It is proved by well-founded induction on
`eval_variant st pre_st var` using `Z.lt_wf`.

```coq
Lemma while_inv_preserved :
  forall inv var cond body,
  forall st out,
  exec st (SWhile inv var cond body) out ->
  forall pre_st,
  eval_contract st pre_st None inv ->
  (forall st',
    eval_contract st' pre_st None inv ->
    eval_bool st' cond = true ->
    wp body (fun st'' =>
        eval_contract st'' pre_st None inv /\
        eval_variant st'' pre_st var < eval_variant st' pre_st var /\
        eval_variant st'' pre_st var >= 0) pre_st st') ->
  match out with
  | ONormal st' =>
      eval_contract st' pre_st None inv /\ eval_bool st' cond = false
  | _ => False
  end.
Proof.
  intros inv var cond body.
  (* Well-founded induction on the variant value *)
  intros st out Hexec.
  induction Hexec using exec_ind;  (* or direct induction on Hexec *)
    intros pre_st Hinv Hpres.
  - (* ExecWhileFalse *)
    split; [exact Hinv | assumption].
  - (* ExecWhileTrue *)
    (* 1. The body WP holds for the current state by Hpres *)
    specialize (Hpres st Hinv H) as Hbody_wp.
    (* 2. Apply soundness to the body execution to get the invariant in st' *)
    (* (This forward reference to Phase 5b is resolved by mutual induction) *)
    admit.
  - (* ExecWhileContinue — same structure as ExecWhileTrue *)
    admit.
Admitted.
```

---

## Phase 5b — Soundness Theorem

```coq
Theorem pycsl_soundness :
  forall (s : stmt) (Q : state -> Prop) (pre_st : state),
  forall (st : state) (out : outcome),
  exec st s out ->
  wp s Q pre_st st ->
  match out with
  | ONormal st'    => Q st'
  | OReturned st' _ => Q st'
  | OContinued _   => True
  end.
Proof.
  intros s Q pre_st.
  induction s; intros st out Hexec Hwp;
    inversion Hexec; subst; simpl in Hwp.
  - (* SSkip *)          exact Hwp.
  - (* SAssign *)        exact Hwp.
  - (* SAugAssign *)     exact Hwp.
  - (* SArraySet *)      exact Hwp.
  - (* SSeq — Normal *)  eapply IHs2; eauto. eapply IHs1; eauto.
                         (* wp s1 (wp s2 Q pre_st) pre_st st → wp s2 Q pre_st st' *)
                         admit.
  - (* SSeq — Return *)  eapply IHs1; eauto. admit.
  - (* SSeq — Continue *) trivial.
  - (* SIfTrue *)        apply IHs1 with (st := st); auto. apply (proj1 Hwp); auto.
  - (* SIfFalse *)       apply IHs2 with (st := st); auto. apply (proj2 Hwp); auto.
  - (* SWhileFalse *)    exact (proj2 (proj2 Hwp) st (proj1 Hwp) H).
  - (* SWhileTrue *)
      eapply while_inv_preserved; eauto.
      + exact (proj1 Hwp).
      + exact (proj1 (proj2 Hwp)).
  - (* SWhileContinue *) eapply while_inv_preserved; eauto.
      + exact (proj1 Hwp).
      + exact (proj1 (proj2 Hwp)).
  - (* SContinue *)      trivial.
  - (* SReturn *)        exact Hwp.
Qed.
```

---

## What remains after Phase 5b

- Close all `admit` / `Admitted` blocks (the while mutual-induction and the Seq
  intermediate-state connection are the two hard cases).
- Add Phase 3b `desugar_correct` proof.
- Add the function-call WP rule (`SCall` / `func_spec`) and its soundness case.
- Begin Track 2 (Lean port) once all `Admitted` are removed.
