(* Phase2d_StmtIR.v — axiom-free certificate for the `stmt_ir` statement-IR ADT
   (self-tcb-reduction M5, C-bucket: the list-append-mutation wall).

   CO-LANDING COUPLING (the tier-3 rule, cf. Phase2c_PyConstVal.v): the WhyML
   `stmt_ir` theory promoted into the emitter preamble
   (`module6_whyml/preamble.py::_emit_exprir_theory`, gated on `_uses_stmt_ir`)
   is a NEW value shape — the statement-node sum an `_py_stmt_*` handler appends
   to its `ir_stmts` list — so it lands with a proof, not a trusted assumption.
   Certified here, against pure inductive datatypes with NO axiom, is exactly
   what the emitter relies on when it lowers `ir_stmts.append({"stmt": K, ...})`
   to `ir_stmts := Seq.snoc !ir_stmts <ctor>` and reflects a node's tag via
   `stmt_kind_of`:

     (a) `stmt_ir` is a WELL-FOUNDED inductive with a size measure and DECIDABLE
         equality (given decidable equality on the abstract expr-child type);
     (b) the dict->ctor abstraction `abs : pystmt -> stmt_ir` (a recognized
         `{"stmt": K}` node to its constructor) is TOTAL, INJECTIVE, and
         SURJECTIVE onto the ADT — the recognized key-set maps injectively;
     (c) `stmt_kind_of` is EXACT on every constructor and the tag map is
         INJECTIVE on the recognized key-set (SPass, SBreak, ... are provably
         DISTINCT — the honest node identity the pre-feature integer-0 erasure
         destroyed, fable Oracle 3).

   SUB-BODY increment (this landing): `stmt_ir` gains the COMPOUND constructors
   SWhile / SIf / SFor, which carry their nested statement body/orelse LISTS as a
   bespoke MONOMORPHIC cons-list `stmt_list = SLNil | SLCons stmt_ir stmt_list`
   — MUTUALLY recursive WITH `stmt_ir` (the WhyML twin uses `with stmt_list`).
   The FLAT `size` (every node size 1) is replaced by the MUTUAL well-founded
   measure `size_stmt` / `size_slist`: `size_stmt` descends into the sub-body
   (size_slist), which descends into each element (size_stmt) — the mutual
   induction, over the auto-generated mutual induction principle
   (`stmt_ir_stmt_list_mutind`). Well-foundedness is witnessed by the two
   size-DECREASE lemmas (`size_slist_lt_swhile` etc.): a sub-body is strictly
   smaller than its containing node, so no infinite descent is possible.
   `seq_to_sl` (the runtime `seq stmt_ir` -> `stmt_list` materialization) is
   Why3-INTRINSIC (`variant { Seq.length s - i }`), needing NO certificate clause
   here — this file certifies the DATA model; the seq cursor's termination is
   Why3's own.

     (d) NO MUTUAL RECURSION WITH emit_ir: the expr children (`SExpr e` carries
         the FOREIGN emit_ir type `emit`; `SReturn o` carries `iropt`; SWhile/SIf/
         SFor's TEST/ITER carry `emit`), where `emit` (a Section variable here)
         never mentions `stmt_ir` — so `stmt_ir` adds NO constructor to emit_ir's
         own size induction, and neither `size_stmt` nor `size_slist` descends
         into `emit`.  This is the one-directional-reference property the WhyML
         block needs (stmt_ir/stmt_list reference emit_ir; emit_ir references
         neither).

   The mutable-ref append convention itself (`ir_stmts : ref (seq stmt_ir)` with
   a real `writes { ir_stmts }` frame) needs NO certificate clause here: it is a
   Why3-INTRINSIC `writes` verification condition — Why3's region/effect system
   discharges the caller-visible-write obligation directly (the fable oracle
   `sound_append.mlw` proved it Valid, 0 axioms).

   The `Print Assumptions` block at the bottom is the trust check: every result
   must be `Closed under the global context` (NO axiom) so the 3-axiom trust
   ledger (`proof_axiom_allowlist.py`) stays intact.  Nothing here is Admitted.
   Build: part of `make` (listed in `_CoqProject` after `Phase2c_PyValDict.v`). *)

Require Import ZArith String List Bool Lia.
Import ListNotations.
Open Scope string_scope.

Section StmtIR.

(* The WhyML emit_ir expr-child type, abstracted (see header (d)).  Kept a
   Section variable so `stmt_ir` provably carries a FOREIGN child — there is no
   `stmt_ir` occurrence inside `emit`, hence no mutual recursion with emit_ir. *)
Variable emit : Type.
Variable emit0 : emit.   (* a witness, for the surjectivity existentials *)
Variable emit_eq_dec : forall a b : emit, {a = b} + {a <> b}.

(* ===================================================================== *)
(* 1. The statement-IR ADT — mirrors the WhyML `type stmt_ir with stmt_list`. *)
(* ===================================================================== *)

(* The monomorphic option sibling of the emit_ir ADT — mirrors the WhyML
   `iropt_ir = IrONone | IrOSome emit_ir`.  SReturn carries it (the OPTIONAL
   return value); it references only the FOREIGN `emit`, never `stmt_ir`. *)
Inductive iropt : Type :=
  | IrONone
  | IrOSome (e : emit).

(* The monomorphic option-STRING sibling — mirrors the WhyML `iropt_str = IrSNone
   | IrSSome string`.  SAssert carries it (the OPTIONAL assert-message STRING, the
   `stmt.msg` string-literal Constant); it references NO type variable, so it never
   mentions `stmt_ir`. *)
Inductive ioptstr : Type :=
  | ISNone
  | ISSome (s : string).

(* strl — the monomorphic string cons; STupleUnpack's `targets` compaction (`[elt.id
   for elt in target.elts if isinstance(elt, ast.Name)]`).  References NO type variable,
   so it never mentions stmt_ir. *)
Inductive strl : Type :=
  | TgtNil
  | TgtCons (s : string) (t : strl).

(* The MUTUAL block: stmt_ir and its sub-body list stmt_list.  The compound
   nodes carry `stmt_list` bodies (SWhile: test+body; SIf: test+body+orelse;
   SFor: iter+body); `stmt_list` is the bespoke monomorphic cons.  SAssert carries
   the TEST expr (foreign `emit`) + the OPTIONAL msg string (`ioptstr`). *)
Inductive stmt_ir : Type :=
  | SPass
  | SBreak
  | SContinue
  | SReturn (o : iropt)
  | SExpr (e : emit)
  | SAssign (n : string) (e : emit)
  | SAssert (t : emit) (m : ioptstr)
  | SAugAssign (n : string) (op : string) (e : emit)
  | SFieldAugAssign (f : string) (op : string) (e : emit)
  | SArraySet (a : emit) (i : emit) (v : emit)
  | SWhile (t : emit) (b : stmt_list)
  | SIf (t : emit) (b : stmt_list) (el : stmt_list)
  | SFor (t : emit) (b : stmt_list)
  (* STry increment: FOUR children — body / handlers / orelse / finalbody.  The
     handler list is `handler_list`, a bespoke monomorphic cons over the
     `except_handler` record, MUTUALLY recursive WITH stmt_ir/stmt_list (the
     record's `eh_body` is a `stmt_list`, so the whole cycle is one mutual block —
     a `seq except_handler` field would break strict positivity). *)
  | STry (b : stmt_list) (hs : handler_list) (oe : stmt_list) (fb : stmt_list)
  (* SMatch increment: SUBJECT (foreign emit) + the CASE list.  match_case_list is a
     bespoke monomorphic cons over the `match_case` record, MUTUALLY recursive WITH
     stmt_ir/stmt_list (the record's `mc_body` is a `stmt_list`). *)
  | SMatch (subj : emit) (cs : match_case_list)
  (* SDelSubscript increment: a subscript-delete `del d[k]` — array + index, both
     FOREIGN emit children (FLAT, no sub-body list). *)
  | SDelSubscript (arr : emit) (idx : emit)
  (* _py_stmt_assign increment: three FLAT ctors.  SFieldAssign carries the base NAME
     (string, `"self"` or `target.value.id`), the FIELD name (string), the RHS (emit).
     SArraySliceSet carries the ARRAY (emit), the OPTIONAL lower/upper bounds (iropt),
     the RHS (emit).  STupleUnpack carries the compaction of Name targets (`strl`, a
     bespoke string cons) + the RHS (emit). *)
  | SFieldAssign (base : string) (fld : string) (v : emit)
  | SArraySliceSet (arr : emit) (lo : iropt) (up : iropt) (v : emit)
  | STupleUnpack (tgts : strl) (v : emit)
  (* SCriticalSection increment (_py_stmt_with mutex branch): the mutex NAME (string),
     the guarded BODY (stmt_list — COMPOUND, mutually recursive), the assume/prove
     invariants (foreign emit). *)
  | SCriticalSection (mtx : string) (b : stmt_list) (ai : emit) (pi : emit)
  (* _emit_ghost_assign increment: two FLAT ghost-stmt ctors.  SGhostArraySet carries the
     target NAME (string), the index + value (foreign emit).  SGhostAssign carries the
     target (string), the value (emit), the op (string), the declared ghost_type (string). *)
  | SGhostArraySet (tgt : string) (idx : emit) (v : emit)
  | SGhostAssign (tgt : string) (v : emit) (op : string) (gty : string)
with stmt_list : Type :=
  | SLNil
  | SLCons (h : stmt_ir) (t : stmt_list)
with handler_list : Type :=
  | HLNil
  | HLCons (h : except_handler) (t : handler_list)
with except_handler : Type :=
  | MkEH (eh_exc_type : ioptstr) (eh_name : ioptstr) (eh_body : stmt_list)
with match_case_list : Type :=
  | MCNil
  | MCCons (c : match_case) (t : match_case_list)
with match_case : Type :=
  | MkMC (mc_pattern : emit) (mc_guard : iropt) (mc_body : stmt_list).

(* The mutual induction principle — the well-foundedness witness the measure
   below is proven over.  4-way: stmt_ir / stmt_list / handler_list /
   except_handler. *)
Scheme stmt_ir_mut := Induction for stmt_ir Sort Prop
with stmt_list_mut := Induction for stmt_list Sort Prop
with handler_list_mut := Induction for handler_list Sort Prop
with except_handler_mut := Induction for except_handler Sort Prop
with match_case_list_mut := Induction for match_case_list Sort Prop
with match_case_mut := Induction for match_case Sort Prop.
Combined Scheme stmt_ir_stmt_list_mutind from stmt_ir_mut, stmt_list_mut,
  handler_list_mut, except_handler_mut, match_case_list_mut, match_case_mut.

(* The tag discriminant — verbatim image of the WhyML `stmt_kind_of`. *)
Definition stmt_kind_of (s : stmt_ir) : string :=
  match s with
  | SPass       => "Pass"
  | SBreak      => "Break"
  | SContinue   => "Continue"
  | SReturn _   => "Return"
  | SExpr _     => "Expr"
  | SAssign _ _ => "Assign"
  | SAssert _ _ => "Assert"
  | SAugAssign _ _ _ => "AugAssign"
  | SFieldAugAssign _ _ _ => "FieldAugAssign"
  | SArraySet _ _ _ => "ArraySet"
  | SWhile _ _  => "While"
  | SIf _ _ _   => "If"
  | SFor _ _    => "For"
  | STry _ _ _ _ => "Try"
  | SMatch _ _  => "Match"
  | SDelSubscript _ _ => "DelSubscript"
  | SFieldAssign _ _ _ => "FieldAssign"
  | SArraySliceSet _ _ _ _ => "ArraySliceSet"
  | STupleUnpack _ _ => "TupleUnpack"
  | SCriticalSection _ _ _ _ => "CriticalSection"
  | SGhostArraySet _ _ _ => "GhostArraySet"
  | SGhostAssign _ _ _ _ => "GhostAssign"
  end.

(* ===================================================================== *)
(* 1b. The MUTUAL well-founded size measure — WhyML `size_stmt`/`size_slist`. *)
(* ===================================================================== *)

Fixpoint size_stmt (s : stmt_ir) : nat :=
  match s with
  | SWhile _ b  => 1 + size_slist b
  | SIf _ b el  => 1 + size_slist b + size_slist el
  | SFor _ b    => 1 + size_slist b
  | STry b hs oe fb => 1 + size_slist b + size_hlist hs
                        + size_slist oe + size_slist fb
  | SMatch _ cs => 1 + size_mclist cs
  | SCriticalSection _ b _ _ => 1 + size_slist b
  | _           => 1
  end
with size_slist (l : stmt_list) : nat :=
  match l with
  | SLNil       => 0
  | SLCons h t  => size_stmt h + size_slist t
  end
with size_hlist (l : handler_list) : nat :=
  match l with
  | HLNil       => 0
  | HLCons h t  => size_handler h + size_hlist t
  end
with size_handler (h : except_handler) : nat :=
  match h with
  | MkEH _ _ b  => 1 + size_slist b
  end
with size_mclist (l : match_case_list) : nat :=
  match l with
  | MCNil       => 0
  | MCCons c t  => size_mcase c + size_mclist t
  end
with size_mcase (c : match_case) : nat :=
  match c with
  | MkMC _ _ b  => 1 + size_slist b
  end.

(* Every node has size >= 1; a list has size >= 0 (trivial for nat). *)
Theorem size_stmt_pos : forall s, size_stmt s >= 1.
Proof. intros s; destruct s; simpl; lia. Qed.

(* STry sub-bodies are STRICTLY smaller than the STry node — the 4-way mutual
   well-foundedness witnesses (a recursive walker over STry terminates). *)
Theorem size_try_body_lt : forall b hs oe fb,
  size_slist b < size_stmt (STry b hs oe fb).
Proof. intros; simpl; lia. Qed.
Theorem size_try_handlers_lt : forall b hs oe fb,
  size_hlist hs < size_stmt (STry b hs oe fb).
Proof. intros; simpl; lia. Qed.
Theorem size_try_orelse_lt : forall b hs oe fb,
  size_slist oe < size_stmt (STry b hs oe fb).
Proof. intros; simpl; lia. Qed.
Theorem size_try_final_lt : forall b hs oe fb,
  size_slist fb < size_stmt (STry b hs oe fb).
Proof. intros; simpl; lia. Qed.
(* A handler / its tail is no larger than the handler_list that contains it, and
   a handler's body is strictly smaller than the handler. *)
Theorem size_handler_le_hlcons : forall h t,
  size_handler h <= size_hlist (HLCons h t).
Proof. intros; simpl; lia. Qed.
Theorem size_hltail_le_hlcons : forall h t,
  size_hlist t <= size_hlist (HLCons h t).
Proof. intros; simpl; lia. Qed.
Theorem size_ehbody_lt_handler : forall x n b,
  size_slist b < size_handler (MkEH x n b).
Proof. intros; simpl; lia. Qed.
(* SMatch: the case-list is strictly smaller than the SMatch node; a case / its
   tail is no larger than the case-list; a case's body is smaller than the case. *)
Theorem size_match_cases_lt : forall s cs,
  size_mclist cs < size_stmt (SMatch s cs).
Proof. intros; simpl; lia. Qed.
Theorem size_mcase_le_mccons : forall c t,
  size_mcase c <= size_mclist (MCCons c t).
Proof. intros; simpl; lia. Qed.
Theorem size_mctail_le_mccons : forall c t,
  size_mclist t <= size_mclist (MCCons c t).
Proof. intros; simpl; lia. Qed.
Theorem size_mcbody_lt_mcase : forall p g b,
  size_slist b < size_mcase (MkMC p g b).
Proof. intros; simpl; lia. Qed.
Theorem size_mcase_pos : forall c, size_mcase c >= 1.
Proof. intros c; destruct c; simpl; lia. Qed.

(* Well-foundedness witnesses: a sub-body is STRICTLY smaller than the compound
   node that carries it — so a recursive walker over stmt_ir terminates. *)
Theorem size_slist_lt_swhile : forall t b, size_slist b < size_stmt (SWhile t b).
Proof. intros t b; simpl; lia. Qed.
Theorem size_body_lt_sif : forall t b el, size_slist b < size_stmt (SIf t b el).
Proof. intros t b el; simpl; lia. Qed.
Theorem size_orelse_lt_sif : forall t b el, size_slist el < size_stmt (SIf t b el).
Proof. intros t b el; simpl; lia. Qed.
Theorem size_slist_lt_sfor : forall t b, size_slist b < size_stmt (SFor t b).
Proof. intros t b; simpl; lia. Qed.
(* And an element / tail is no larger than the list that contains it. *)
Theorem size_head_le_slcons : forall h t, size_stmt h <= size_slist (SLCons h t).
Proof. intros h t; simpl; lia. Qed.
Theorem size_tail_le_slcons : forall h t, size_slist t <= size_slist (SLCons h t).
Proof. intros h t; simpl; lia. Qed.

(* Decidable equality on the WHOLE mutual block, given decidable equality on the
   foreign child `emit` — the well-founded-ADT obligation (mutual recursion). *)
Definition iropt_eq_dec : forall x y : iropt, {x = y} + {x <> y}.
Proof. decide equality; apply emit_eq_dec. Defined.

Definition ioptstr_eq_dec : forall x y : ioptstr, {x = y} + {x <> y}.
Proof. decide equality; apply string_dec. Defined.

Definition strl_eq_dec : forall x y : strl, {x = y} + {x <> y}.
Proof. decide equality; apply string_dec. Defined.

Fixpoint stmt_ir_eq_dec (x y : stmt_ir) : {x = y} + {x <> y}
with stmt_list_eq_dec (x y : stmt_list) : {x = y} + {x <> y}
with handler_list_eq_dec (x y : handler_list) : {x = y} + {x <> y}
with except_handler_eq_dec (x y : except_handler) : {x = y} + {x <> y}
with match_case_list_eq_dec (x y : match_case_list) : {x = y} + {x <> y}
with match_case_eq_dec (x y : match_case) : {x = y} + {x <> y}.
Proof.
  - decide equality;
      (apply emit_eq_dec || apply iropt_eq_dec || apply ioptstr_eq_dec
       || apply stmt_list_eq_dec || apply handler_list_eq_dec
       || apply match_case_list_eq_dec || apply strl_eq_dec || apply string_dec).
  - decide equality; apply stmt_ir_eq_dec.
  - decide equality; apply except_handler_eq_dec.
  - decide equality; (apply ioptstr_eq_dec || apply stmt_list_eq_dec).
  - decide equality; apply match_case_eq_dec.
  - decide equality; (apply emit_eq_dec || apply iropt_eq_dec || apply stmt_list_eq_dec).
Defined.

(* ===================================================================== *)
(* 2. The recognized `{"stmt": K}` world + its dict->ctor abstraction.    *)
(* ===================================================================== *)

(* The recognized statement-node key-set the emitter's `_STMT_IR_CTORS`
   recognizes (expressions.py): nullary (Pass/Break/Continue), one expr-child
   (Return/Expr), or COMPOUND (While/If/For, carrying stmt_list bodies). *)
Inductive pystmt : Type :=
  | PPass
  | PBreak
  | PContinue
  | PReturn (o : iropt)
  | PExpr (e : emit)
  | PAssign (n : string) (e : emit)
  | PAssert (t : emit) (m : ioptstr)
  | PAugAssign (n : string) (op : string) (e : emit)
  | PFieldAugAssign (f : string) (op : string) (e : emit)
  | PArraySet (a : emit) (i : emit) (v : emit)
  | PWhile (t : emit) (b : stmt_list)
  | PIf (t : emit) (b : stmt_list) (el : stmt_list)
  | PFor (t : emit) (b : stmt_list)
  | PTry (b : stmt_list) (hs : handler_list) (oe : stmt_list) (fb : stmt_list)
  | PMatch (subj : emit) (cs : match_case_list)
  | PDelSubscript (arr : emit) (idx : emit)
  | PFieldAssign (base : string) (fld : string) (v : emit)
  | PArraySliceSet (arr : emit) (lo : iropt) (up : iropt) (v : emit)
  | PTupleUnpack (tgts : strl) (v : emit)
  | PCriticalSection (mtx : string) (b : stmt_list) (ai : emit) (pi : emit)
  | PGhostArraySet (tgt : string) (idx : emit) (v : emit)
  | PGhostAssign (tgt : string) (v : emit) (op : string) (gty : string).

(* The dict->ctor map (`{"stmt":"Pass"} |-> SPass`, ..., `{"stmt":"While",...}
   |-> SWhile ...`). *)
Definition abs (s : pystmt) : stmt_ir :=
  match s with
  | PPass       => SPass
  | PBreak      => SBreak
  | PContinue   => SContinue
  | PReturn o   => SReturn o
  | PExpr e     => SExpr e
  | PAssign n e => SAssign n e
  | PAssert t m => SAssert t m
  | PAugAssign n op e => SAugAssign n op e
  | PFieldAugAssign f op e => SFieldAugAssign f op e
  | PArraySet a i v => SArraySet a i v
  | PWhile t b  => SWhile t b
  | PIf t b el  => SIf t b el
  | PFor t b    => SFor t b
  | PTry b hs oe fb => STry b hs oe fb
  | PMatch subj cs => SMatch subj cs
  | PDelSubscript a i => SDelSubscript a i
  | PFieldAssign b f v => SFieldAssign b f v
  | PArraySliceSet a lo up v => SArraySliceSet a lo up v
  | PTupleUnpack t v => STupleUnpack t v
  | PCriticalSection m b ai pi => SCriticalSection m b ai pi
  | PGhostArraySet t i v => SGhostArraySet t i v
  | PGhostAssign t v op g => SGhostAssign t v op g
  end.

(* The Python-side tag string of a recognized node (the `"stmt"` value). *)
Definition py_kind_of (s : pystmt) : string :=
  match s with
  | PPass       => "Pass"
  | PBreak      => "Break"
  | PContinue   => "Continue"
  | PReturn _   => "Return"
  | PExpr _     => "Expr"
  | PAssign _ _ => "Assign"
  | PAssert _ _ => "Assert"
  | PAugAssign _ _ _ => "AugAssign"
  | PFieldAugAssign _ _ _ => "FieldAugAssign"
  | PArraySet _ _ _ => "ArraySet"
  | PWhile _ _  => "While"
  | PIf _ _ _   => "If"
  | PFor _ _    => "For"
  | PTry _ _ _ _ => "Try"
  | PMatch _ _  => "Match"
  | PDelSubscript _ _ => "DelSubscript"
  | PFieldAssign _ _ _ => "FieldAssign"
  | PArraySliceSet _ _ _ _ => "ArraySliceSet"
  | PTupleUnpack _ _ => "TupleUnpack"
  | PCriticalSection _ _ _ _ => "CriticalSection"
  | PGhostArraySet _ _ _ => "GhostArraySet"
  | PGhostAssign _ _ _ _ => "GhostAssign"
  end.

(* ===================================================================== *)
(* 3. (b) `abs` is total + injective + surjective (recognition is sound). *)
(* ===================================================================== *)

Theorem abs_injective : forall x y, abs x = abs y -> x = y.
Proof. intros x y H; destruct x; destruct y; simpl in H; congruence. Qed.

Theorem abs_surjective : forall v : stmt_ir, exists s, abs s = v.
Proof.
  intros v; destruct v.
  - exists PPass; reflexivity.
  - exists PBreak; reflexivity.
  - exists PContinue; reflexivity.
  - exists (PReturn o); reflexivity.
  - exists (PExpr e); reflexivity.
  - exists (PAssign n e); reflexivity.
  - exists (PAssert t m); reflexivity.
  - exists (PAugAssign n op e); reflexivity.
  - exists (PFieldAugAssign f op e); reflexivity.
  - exists (PArraySet a i v); reflexivity.
  - exists (PWhile t b); reflexivity.
  - exists (PIf t b el); reflexivity.
  - exists (PFor t b); reflexivity.
  - exists (PTry b hs oe fb); reflexivity.
  - exists (PMatch subj cs); reflexivity.
  - exists (PDelSubscript arr idx); reflexivity.
  - exists (PFieldAssign base fld v); reflexivity.
  - exists (PArraySliceSet arr lo up v); reflexivity.
  - exists (PTupleUnpack tgts v); reflexivity.
  - exists (PCriticalSection mtx b ai pi); reflexivity.
  - exists (PGhostArraySet tgt idx v); reflexivity.
  - exists (PGhostAssign tgt v op gty); reflexivity.
Qed.

(* ===================================================================== *)
(* 4. (c) `stmt_kind_of` is EXACT per ctor, and the tag map AGREES with   *)
(*    the Python `"stmt"` string through `abs`.                           *)
(* ===================================================================== *)

Theorem stmt_kind_of_pass     : stmt_kind_of SPass = "Pass".         Proof. reflexivity. Qed.
Theorem stmt_kind_of_break    : stmt_kind_of SBreak = "Break".       Proof. reflexivity. Qed.
Theorem stmt_kind_of_continue : stmt_kind_of SContinue = "Continue". Proof. reflexivity. Qed.
Theorem stmt_kind_of_return   : forall o, stmt_kind_of (SReturn o) = "Return". Proof. reflexivity. Qed.
Theorem stmt_kind_of_expr     : forall e, stmt_kind_of (SExpr e) = "Expr".     Proof. reflexivity. Qed.
Theorem stmt_kind_of_assign   : forall n e, stmt_kind_of (SAssign n e) = "Assign". Proof. reflexivity. Qed.
Theorem stmt_kind_of_assert   : forall t m, stmt_kind_of (SAssert t m) = "Assert". Proof. reflexivity. Qed.
(* SAugAssign/SFieldAugAssign/SArraySet increment: the three augmented-assignment tags
   are EXACT on their constructors. *)
Theorem stmt_kind_of_augassign : forall n op e, stmt_kind_of (SAugAssign n op e) = "AugAssign". Proof. reflexivity. Qed.
Theorem stmt_kind_of_fieldaugassign : forall f op e, stmt_kind_of (SFieldAugAssign f op e) = "FieldAugAssign". Proof. reflexivity. Qed.
Theorem stmt_kind_of_arrayset : forall a i v, stmt_kind_of (SArraySet a i v) = "ArraySet". Proof. reflexivity. Qed.
Theorem stmt_kind_of_while    : forall t b, stmt_kind_of (SWhile t b) = "While". Proof. reflexivity. Qed.
Theorem stmt_kind_of_if       : forall t b el, stmt_kind_of (SIf t b el) = "If". Proof. reflexivity. Qed.
Theorem stmt_kind_of_for      : forall t b, stmt_kind_of (SFor t b) = "For".     Proof. reflexivity. Qed.

Theorem kind_of_agree : forall s, stmt_kind_of (abs s) = py_kind_of s.
Proof. intros []; reflexivity. Qed.

(* ===================================================================== *)
(* 5. (c') TAG-PRESERVING: the tags are pairwise DISTINCT — the honest    *)
(*    node identity the integer-0 erasure destroyed.                      *)
(* ===================================================================== *)

Theorem tag_pass_neq_break    : stmt_kind_of SPass <> stmt_kind_of SBreak.
Proof. simpl; discriminate. Qed.
Theorem tag_pass_neq_continue : stmt_kind_of SPass <> stmt_kind_of SContinue.
Proof. simpl; discriminate. Qed.
Theorem tag_break_neq_continue: stmt_kind_of SBreak <> stmt_kind_of SContinue.
Proof. simpl; discriminate. Qed.
Theorem tag_pass_neq_return   : forall o, stmt_kind_of SPass <> stmt_kind_of (SReturn o).
Proof. intro o; simpl; discriminate. Qed.
Theorem tag_return_neq_expr   : forall o e, stmt_kind_of (SReturn o) <> stmt_kind_of (SExpr e).
Proof. intros o e; simpl; discriminate. Qed.
(* SAssign + str-Constant recognizer increment: the Assign tag is distinct from the
   Expr tag (the two `_py_stmt_expr`/`_py_stmt_annassign` node kinds are NOT collapsed). *)
Theorem tag_assign_neq_expr   : forall n e f, stmt_kind_of (SAssign n e) <> stmt_kind_of (SExpr f).
Proof. intros; simpl; discriminate. Qed.
Theorem tag_assign_neq_return : forall n e o, stmt_kind_of (SAssign n e) <> stmt_kind_of (SReturn o).
Proof. intros; simpl; discriminate. Qed.
(* SAssert increment: the Assert tag is distinct from the Expr and Assign tags
   (the `_py_stmt_assert` node is NOT collapsed onto a sibling statement kind). *)
Theorem tag_assert_neq_expr   : forall t m e, stmt_kind_of (SAssert t m) <> stmt_kind_of (SExpr e).
Proof. intros; simpl; discriminate. Qed.
Theorem tag_assert_neq_assign : forall t m n e, stmt_kind_of (SAssert t m) <> stmt_kind_of (SAssign n e).
Proof. intros; simpl; discriminate. Qed.
(* SAugAssign/SFieldAugAssign/SArraySet increment: the three augmented-assignment tags are
   pairwise distinct AND distinct from the plain Assign tag (an `x op= v` is NOT collapsed
   onto `x = v`, and the three target shapes are separate node kinds). *)
Theorem tag_augassign_neq_assign : forall n op e m f, stmt_kind_of (SAugAssign n op e) <> stmt_kind_of (SAssign m f).
Proof. intros; simpl; discriminate. Qed.
Theorem tag_augassign_neq_fieldaug : forall n op e f g h, stmt_kind_of (SAugAssign n op e) <> stmt_kind_of (SFieldAugAssign f g h).
Proof. intros; simpl; discriminate. Qed.
Theorem tag_augassign_neq_arrayset : forall n op e a i v, stmt_kind_of (SAugAssign n op e) <> stmt_kind_of (SArraySet a i v).
Proof. intros; simpl; discriminate. Qed.
Theorem tag_fieldaug_neq_arrayset : forall f g h a i v, stmt_kind_of (SFieldAugAssign f g h) <> stmt_kind_of (SArraySet a i v).
Proof. intros; simpl; discriminate. Qed.
(* SUB-BODY increment: the compound tags are distinct from each other and from
   the simple ones (While/If/For are provably separate nodes, not a shared 0). *)
Theorem tag_while_neq_if      : forall t b el o, stmt_kind_of (SWhile t b) <> stmt_kind_of (SIf o el b).
Proof. intros; simpl; discriminate. Qed.
Theorem tag_while_neq_for     : forall t b u c, stmt_kind_of (SWhile t b) <> stmt_kind_of (SFor u c).
Proof. intros; simpl; discriminate. Qed.
Theorem tag_if_neq_for        : forall t b el u c, stmt_kind_of (SIf t b el) <> stmt_kind_of (SFor u c).
Proof. intros; simpl; discriminate. Qed.
Theorem tag_while_neq_pass    : forall t b, stmt_kind_of (SWhile t b) <> stmt_kind_of SPass.
Proof. intros; simpl; discriminate. Qed.

(* The constructors themselves are distinct (no erasure to a common value). *)
Theorem ctor_pass_neq_break : SPass <> SBreak.
Proof. discriminate. Qed.

(* (c'') The OPTIONAL return value is OBSERVABLE — a bare `return` (SReturn
   IrONone) and a value `return e` (SReturn (IrOSome e)) are DISTINCT nodes. *)
Theorem sreturn_none_neq_some : forall e, SReturn IrONone <> SReturn (IrOSome e).
Proof. intros e H; discriminate. Qed.

(* (c'''') SAssign non-vacuity: the TARGET NAME and the RHS VALUE are BOTH observable —
   two SAssign nodes differing in either field are DISTINCT (the injective constructor
   carries the name string and the emit_ir value faithfully, never a shared 0). *)
Theorem sassign_target_observable : forall n m e, n <> m -> SAssign n e <> SAssign m e.
Proof. intros n m e H C; inversion C; contradiction. Qed.
Theorem sassign_value_observable : forall n e f, e <> f -> SAssign n e <> SAssign n f.
Proof. intros n e f H C; inversion C; contradiction. Qed.

(* (c''''') SAssert non-vacuity: the OPTIONAL msg string is OBSERVABLE — an assert
   WITHOUT a message (SAssert t ISNone) and one WITH a string message (SAssert t
   (ISSome s)) are DISTINCT nodes; two present messages differing in text are
   DISTINCT; and the TEST expr is observable too.  The conditional msg-add is a real
   option (IrSSome/IrSNone), never a shared 0 — the `if stmt.msg ...` guard is honest. *)
Theorem sassert_msg_none_neq_some : forall t s, SAssert t ISNone <> SAssert t (ISSome s).
Proof. intros t s H; discriminate. Qed.
Theorem sassert_msg_observable : forall t s r, s <> r -> SAssert t (ISSome s) <> SAssert t (ISSome r).
Proof. intros t s r H C; inversion C; contradiction. Qed.
Theorem sassert_test_observable : forall t u m, t <> u -> SAssert t m <> SAssert u m.
Proof. intros t u m H C; inversion C; contradiction. Qed.

(* (c'''''') SAugAssign/SFieldAugAssign/SArraySet non-vacuity: every carried field is
   OBSERVABLE — the injective constructors carry the target/field NAME, the OP string, and
   the emit_ir sub-nodes faithfully, never a shared 0.  If two nodes differ in any field
   they are DISTINCT (the 0900 fixture's driver_refute / evil twins at the ADT level). *)
Theorem saugassign_target_observable : forall n m op e, n <> m -> SAugAssign n op e <> SAugAssign m op e.
Proof. intros n m op e H C; inversion C; contradiction. Qed.
Theorem saugassign_op_observable : forall n op1 op2 e, op1 <> op2 -> SAugAssign n op1 e <> SAugAssign n op2 e.
Proof. intros n op1 op2 e H C; inversion C; contradiction. Qed.
Theorem saugassign_value_observable : forall n op e f, e <> f -> SAugAssign n op e <> SAugAssign n op f.
Proof. intros n op e f H C; inversion C; contradiction. Qed.
Theorem sfieldaug_field_observable : forall f g op e, f <> g -> SFieldAugAssign f op e <> SFieldAugAssign g op e.
Proof. intros f g op e H C; inversion C; contradiction. Qed.
Theorem sarrayset_array_observable : forall a b i v, a <> b -> SArraySet a i v <> SArraySet b i v.
Proof. intros a b i v H C; inversion C; contradiction. Qed.
Theorem sarrayset_index_observable : forall a i j v, i <> j -> SArraySet a i v <> SArraySet a j v.
Proof. intros a i j v H C; inversion C; contradiction. Qed.
Theorem sarrayset_value_observable : forall a i v w, v <> w -> SArraySet a i v <> SArraySet a i w.
Proof. intros a i v w H C; inversion C; contradiction. Qed.

(* (c''') SUB-BODY non-vacuity: an SWhile whose sub-body is EMPTY (SLNil) and one
   whose sub-body has a node (SLCons ...) are DISTINCT nodes — the sub-body is
   OBSERVABLE, not collapsed (the 0896 fixture's driver_refute / driver_evil_count
   at the ADT level).  Their sizes differ too. *)
Theorem swhile_empty_neq_nonempty :
  forall t h r, SWhile t SLNil <> SWhile t (SLCons h r).
Proof. intros t h r H; discriminate. Qed.
Theorem swhile_size_grows_with_body :
  forall t h r, size_stmt (SWhile t SLNil) < size_stmt (SWhile t (SLCons h r)).
Proof. intros t h r; simpl; pose proof (size_stmt_pos h); lia. Qed.

(* ===================================================================== *)
(* STry + except_handler + handler_list observability (non-vacuity).       *)
(* ===================================================================== *)

(* Tag: STry projects "Try", distinct from every sibling compound tag. *)
Theorem stmt_kind_of_try : forall b hs oe fb, stmt_kind_of (STry b hs oe fb) = "Try".
Proof. reflexivity. Qed.
Theorem tag_try_neq_while : forall b hs oe fb t c,
  stmt_kind_of (STry b hs oe fb) <> stmt_kind_of (SWhile t c).
Proof. intros; simpl; discriminate. Qed.
Theorem tag_try_neq_if : forall b hs oe fb t c d,
  stmt_kind_of (STry b hs oe fb) <> stmt_kind_of (SIf t c d).
Proof. intros; simpl; discriminate. Qed.

(* The four STry children are INDEPENDENTLY observable: change any one and the
   node differs (never collapsed to a shared 0 — the fixture's evil twins). *)
Theorem stry_body_observable : forall b c hs oe fb,
  b <> c -> STry b hs oe fb <> STry c hs oe fb.
Proof. intros b c hs oe fb H C; inversion C; contradiction. Qed.
Theorem stry_handlers_observable : forall b hs ks oe fb,
  hs <> ks -> STry b hs oe fb <> STry b ks oe fb.
Proof. intros b hs ks oe fb H C; inversion C; contradiction. Qed.
Theorem stry_orelse_observable : forall b hs oe pe fb,
  oe <> pe -> STry b hs oe fb <> STry b hs pe fb.
Proof. intros b hs oe pe fb H C; inversion C; contradiction. Qed.
Theorem stry_final_observable : forall b hs oe fb gb,
  fb <> gb -> STry b hs oe fb <> STry b hs oe gb.
Proof. intros b hs oe fb gb H C; inversion C; contradiction. Qed.

(* An EMPTY handler_list (HLNil) and a NON-empty one (HLCons) yield DISTINCT STry
   nodes — the handler list is observable, not HLNil-erased (the fixture's
   empty-list evil twin).  Their sizes differ too. *)
Theorem stry_handlers_empty_neq_nonempty : forall b oe fb h r,
  STry b HLNil oe fb <> STry b (HLCons h r) oe fb.
Proof. intros; discriminate. Qed.
Theorem size_handler_pos : forall h, size_handler h >= 1.
Proof. intros h; destruct h; simpl; lia. Qed.
Theorem stry_size_grows_with_handlers : forall b oe fb h r,
  size_stmt (STry b HLNil oe fb) < size_stmt (STry b (HLCons h r) oe fb).
Proof. intros; simpl; pose proof (size_handler_pos h); lia. Qed.

(* The except_handler record's three slots are observable. *)
Theorem eh_exc_type_observable : forall x y n b,
  x <> y -> MkEH x n b <> MkEH y n b.
Proof. intros x y n b H C; inversion C; contradiction. Qed.
Theorem eh_name_observable : forall x n m b,
  n <> m -> MkEH x n b <> MkEH x m b.
Proof. intros x n m b H C; inversion C; contradiction. Qed.
Theorem eh_body_observable : forall x n b c,
  b <> c -> MkEH x n b <> MkEH x n c.
Proof. intros x n b c H C; inversion C; contradiction. Qed.
Theorem eh_exc_none_neq_some : forall s n b,
  MkEH ISNone n b <> MkEH (ISSome s) n b.
Proof. intros; discriminate. Qed.

(* ===================================================================== *)
(* SMatch + match_case + match_case_list observability (non-vacuity).       *)
(* ===================================================================== *)

Theorem stmt_kind_of_match : forall s cs, stmt_kind_of (SMatch s cs) = "Match".
Proof. reflexivity. Qed.
Theorem tag_match_neq_try : forall s cs b hs oe fb,
  stmt_kind_of (SMatch s cs) <> stmt_kind_of (STry b hs oe fb).
Proof. intros; simpl; discriminate. Qed.
Theorem tag_match_neq_if : forall s cs t b el,
  stmt_kind_of (SMatch s cs) <> stmt_kind_of (SIf t b el).
Proof. intros; simpl; discriminate. Qed.

(* The SMatch subject + case-list are INDEPENDENTLY observable. *)
Theorem smatch_subject_observable : forall s u cs,
  s <> u -> SMatch s cs <> SMatch u cs.
Proof. intros s u cs H C; inversion C; contradiction. Qed.
Theorem smatch_cases_observable : forall s cs ds,
  cs <> ds -> SMatch s cs <> SMatch s ds.
Proof. intros s cs ds H C; inversion C; contradiction. Qed.

(* An EMPTY case-list (MCNil) and a NON-empty one yield DISTINCT SMatch nodes —
   the case list is observable, not MCNil-erased.  Sizes differ too. *)
Theorem smatch_cases_empty_neq_nonempty : forall s c r,
  SMatch s MCNil <> SMatch s (MCCons c r).
Proof. intros; discriminate. Qed.
Theorem smatch_size_grows_with_cases : forall s c r,
  size_stmt (SMatch s MCNil) < size_stmt (SMatch s (MCCons c r)).
Proof. intros; simpl; pose proof (size_mcase_pos c); lia. Qed.

(* The match_case record's three slots are observable — the guard's None/Some is
   distinguished (the fixture's guarded-vs-unguarded case). *)
Theorem mc_pattern_observable : forall p q g b,
  p <> q -> MkMC p g b <> MkMC q g b.
Proof. intros p q g b H C; inversion C; contradiction. Qed.
Theorem mc_guard_observable : forall p g h b,
  g <> h -> MkMC p g b <> MkMC p h b.
Proof. intros p g h b H C; inversion C; contradiction. Qed.
Theorem mc_body_observable : forall p g b c,
  b <> c -> MkMC p g b <> MkMC p g c.
Proof. intros p g b c H C; inversion C; contradiction. Qed.
Theorem mc_guard_none_neq_some : forall p e b,
  MkMC p IrONone b <> MkMC p (IrOSome e) b.
Proof. intros; discriminate. Qed.

(* ===================================================================== *)
(* SDelSubscript observability (non-vacuity).  FLAT node — size 1.         *)
(* ===================================================================== *)

Theorem stmt_kind_of_delsubscript : forall a i,
  stmt_kind_of (SDelSubscript a i) = "DelSubscript".
Proof. reflexivity. Qed.
Theorem tag_delsubscript_neq_pass : forall a i,
  stmt_kind_of (SDelSubscript a i) <> stmt_kind_of SPass.
Proof. intros; simpl; discriminate. Qed.
Theorem tag_delsubscript_neq_match : forall a i s cs,
  stmt_kind_of (SDelSubscript a i) <> stmt_kind_of (SMatch s cs).
Proof. intros; simpl; discriminate. Qed.
Theorem size_delsubscript_flat : forall a i, size_stmt (SDelSubscript a i) = 1.
Proof. reflexivity. Qed.
(* Both the ARRAY and the INDEX are observable — change either and the node differs
   (never collapsed to a shared 0). *)
Theorem sdelsub_array_observable : forall a b i,
  a <> b -> SDelSubscript a i <> SDelSubscript b i.
Proof. intros a b i H C; inversion C; contradiction. Qed.
Theorem sdelsub_index_observable : forall a i j,
  i <> j -> SDelSubscript a i <> SDelSubscript a j.
Proof. intros a i j H C; inversion C; contradiction. Qed.

(* ===================================================================== *)
(* _py_stmt_assign ctors observability (non-vacuity).  All FLAT — size 1.  *)
(* ===================================================================== *)

Theorem stmt_kind_of_fieldassign : forall b f v,
  stmt_kind_of (SFieldAssign b f v) = "FieldAssign".
Proof. reflexivity. Qed.
Theorem stmt_kind_of_arrayslice : forall a lo up v,
  stmt_kind_of (SArraySliceSet a lo up v) = "ArraySliceSet".
Proof. reflexivity. Qed.
Theorem stmt_kind_of_tupleunpack : forall t v,
  stmt_kind_of (STupleUnpack t v) = "TupleUnpack".
Proof. reflexivity. Qed.
Theorem tag_fieldassign_neq_assign : forall b f v n e,
  stmt_kind_of (SFieldAssign b f v) <> stmt_kind_of (SAssign n e).
Proof. intros; simpl; discriminate. Qed.
Theorem tag_arrayslice_neq_arrayset : forall a lo up v ar i vv,
  stmt_kind_of (SArraySliceSet a lo up v) <> stmt_kind_of (SArraySet ar i vv).
Proof. intros; simpl; discriminate. Qed.
Theorem size_assign_ctors_flat : forall b f v a lo up w t x,
  size_stmt (SFieldAssign b f v) = 1
  /\ size_stmt (SArraySliceSet a lo up w) = 1
  /\ size_stmt (STupleUnpack t x) = 1.
Proof. intros; repeat split; reflexivity. Qed.

(* SFieldAssign: base / field / value each observable; the self-base vs a named base
   is distinguished (the self-Attribute vs symtab-Attribute branches). *)
Theorem sfieldassign_base_observable : forall b c f v,
  b <> c -> SFieldAssign b f v <> SFieldAssign c f v.
Proof. intros b c f v H C; inversion C; contradiction. Qed.
Theorem sfieldassign_field_observable : forall b f g v,
  f <> g -> SFieldAssign b f v <> SFieldAssign b g v.
Proof. intros b f g v H C; inversion C; contradiction. Qed.
Theorem sfieldassign_value_observable : forall b f v w,
  v <> w -> SFieldAssign b f v <> SFieldAssign b f w.
Proof. intros b f v w H C; inversion C; contradiction. Qed.

(* SArraySliceSet: the OPTIONAL lower/upper bounds distinguish None from Some (the
   `a[:hi]` / `a[lo:]` / `a[lo:hi]` shapes). *)
Theorem sarrayslice_lower_none_neq_some : forall a e up v,
  SArraySliceSet a IrONone up v <> SArraySliceSet a (IrOSome e) up v.
Proof. intros; discriminate. Qed.
Theorem sarrayslice_upper_none_neq_some : forall a lo e v,
  SArraySliceSet a lo IrONone v <> SArraySliceSet a lo (IrOSome e) v.
Proof. intros; discriminate. Qed.
Theorem sarrayslice_array_observable : forall a b lo up v,
  a <> b -> SArraySliceSet a lo up v <> SArraySliceSet b lo up v.
Proof. intros a b lo up v H C; inversion C; contradiction. Qed.

(* STupleUnpack: the targets compaction is observable — an EMPTY name-list (all elts
   filtered) differs from a non-empty one (a real Name target survived). *)
Theorem stupleunpack_targets_observable : forall t u v,
  t <> u -> STupleUnpack t v <> STupleUnpack u v.
Proof. intros t u v H C; inversion C; contradiction. Qed.
Theorem stupleunpack_empty_neq_nonempty : forall s r v,
  STupleUnpack TgtNil v <> STupleUnpack (TgtCons s r) v.
Proof. intros; discriminate. Qed.

(* ===================================================================== *)
(* SCriticalSection observability (non-vacuity).  COMPOUND — sub-body.     *)
(* ===================================================================== *)

Theorem stmt_kind_of_critical : forall m b ai pi,
  stmt_kind_of (SCriticalSection m b ai pi) = "CriticalSection".
Proof. reflexivity. Qed.
Theorem tag_critical_neq_try : forall m b ai pi bb hs oe fb,
  stmt_kind_of (SCriticalSection m b ai pi) <> stmt_kind_of (STry bb hs oe fb).
Proof. intros; simpl; discriminate. Qed.
(* The mutex name, the assume/prove invariants, and the sub-body are each observable. *)
Theorem scritical_mutex_observable : forall m n b ai pi,
  m <> n -> SCriticalSection m b ai pi <> SCriticalSection n b ai pi.
Proof. intros m n b ai pi H C; inversion C; contradiction. Qed.
Theorem scritical_assume_observable : forall m b a c pi,
  a <> c -> SCriticalSection m b a pi <> SCriticalSection m b c pi.
Proof. intros m b a c pi H C; inversion C; contradiction. Qed.
(* An EMPTY guarded body and a non-empty one are DISTINCT (the sub-body is observed,
   not collapsed); their sizes differ. *)
Theorem scritical_body_empty_neq_nonempty : forall m ai pi h r,
  SCriticalSection m SLNil ai pi <> SCriticalSection m (SLCons h r) ai pi.
Proof. intros; discriminate. Qed.
Theorem scritical_size_grows_with_body : forall m ai pi h r,
  size_stmt (SCriticalSection m SLNil ai pi)
    < size_stmt (SCriticalSection m (SLCons h r) ai pi).
Proof. intros; simpl; pose proof (size_stmt_pos h); lia. Qed.

(* ===================================================================== *)
(* SGhostArraySet / SGhostAssign observability (non-vacuity).  FLAT.       *)
(* ===================================================================== *)

Theorem stmt_kind_of_ghostarrayset : forall t i v,
  stmt_kind_of (SGhostArraySet t i v) = "GhostArraySet".
Proof. reflexivity. Qed.
Theorem stmt_kind_of_ghostassign : forall t v op g,
  stmt_kind_of (SGhostAssign t v op g) = "GhostAssign".
Proof. reflexivity. Qed.
Theorem tag_ghostarrayset_neq_ghostassign : forall t i v u w op g,
  stmt_kind_of (SGhostArraySet t i v) <> stmt_kind_of (SGhostAssign u w op g).
Proof. intros; simpl; discriminate. Qed.
Theorem sghostarrayset_target_observable : forall t u i v,
  t <> u -> SGhostArraySet t i v <> SGhostArraySet u i v.
Proof. intros t u i v H C; inversion C; contradiction. Qed.
Theorem sghostarrayset_index_observable : forall t i j v,
  i <> j -> SGhostArraySet t i v <> SGhostArraySet t j v.
Proof. intros t i j v H C; inversion C; contradiction. Qed.
Theorem sghostassign_op_observable : forall t v op1 op2 g,
  op1 <> op2 -> SGhostAssign t v op1 g <> SGhostAssign t v op2 g.
Proof. intros t v op1 op2 g H C; inversion C; contradiction. Qed.
Theorem sghostassign_gtype_observable : forall t v op g h,
  g <> h -> SGhostAssign t v op g <> SGhostAssign t v op h.
Proof. intros t v op g h H C; inversion C; contradiction. Qed.

End StmtIR.

(* ===================================================================== *)
(* 5b. The CONCRETE compaction of a Tuple exc_type — the WhyML twin of      *)
(*     `var_names_of` / `join_pipe` / `tuple_exc_type`                      *)
(*     (`"|".join(n.id for n in h.type.elts if isinstance(n, ast.Name))`).  *)
(*     Modelled CONCRETELY (a tiny `cemit` node type with `is_varc`/`namec`) *)
(*     so observability is provable NON-vacuously: the fable's warning is    *)
(*     that a LENGTH-ONLY abstract law is vacuous; this proves the EXACT     *)
(*     projected string, and an evil-twin wrong string is refutable.         *)
(* ===================================================================== *)

Section Compaction.

(* A minimal concrete emit-node: a Name-var carrying its id, or "other". *)
Inductive cemit : Type := CVar (id : string) | COther.
Definition is_varc (e : cemit) : bool := match e with CVar _ => true | _ => false end.
Definition namec (e : cemit) : string := match e with CVar n => n | _ => "" end.

(* The MkTuple elts payload — the WhyML monomorphic `irlist`. *)
Definition cirlist := list cemit.

(* strlist = the WhyML `strlist = SLNilS | SLConsS string strlist`. *)
Inductive strlist : Type := SLNilS | SLConsS (h : string) (t : strlist).

(* var_names_of : filter `is_varc` + project `namec` over the elts. *)
Fixpoint var_names_of (l : cirlist) : strlist :=
  match l with
  | nil => SLNilS
  | e :: rest => if is_varc e then SLConsS (namec e) (var_names_of rest)
                 else var_names_of rest
  end.

(* join_pipe : "|".join — separator BETWEEN names. *)
Fixpoint join_pipe (l : strlist) : string :=
  match l with
  | SLNilS => ""
  | SLConsS h t =>
      match t with
      | SLNilS => h
      | SLConsS _ _ => h ++ "|" ++ join_pipe t
      end
  end.

Definition tuple_exc_type (l : cirlist) : string := join_pipe (var_names_of l).

(* OBSERVABILITY (non-vacuity): a mixed elts list [CVar "A"; COther; CVar "B"]
   drops the non-Name and joins to EXACTLY "A|B".  A LENGTH-ONLY law could not
   prove this. *)
Theorem compaction_observe :
  tuple_exc_type (CVar "A" :: COther :: CVar "B" :: nil) = "A|B".
Proof. reflexivity. Qed.

(* Single Name: the "|".join of one element is that element (no separator). *)
Theorem compaction_single :
  tuple_exc_type (CVar "X" :: nil) = "X".
Proof. reflexivity. Qed.

(* EVIL TWIN: the compaction is NOT the wrong string — refutable, so the string
   is genuinely pinned (non-vacuous). *)
Theorem compaction_evil_twin :
  tuple_exc_type (CVar "A" :: COther :: CVar "B" :: nil) <> "A|C".
Proof. discriminate. Qed.

(* The filter drops non-Name elements: a list of only non-Names compacts to "". *)
Theorem compaction_drops_nonvar :
  tuple_exc_type (COther :: COther :: nil) = "".
Proof. reflexivity. Qed.

End Compaction.

(* ===================================================================== *)
(* 5c. The CONCRETE boolop LEFT-FOLD — the WhyML twin of `boolop_fold`      *)
(*     (`result = disp(v0); for v in values[1:]: result = BinOp op result   *)
(*     (disp v)`).  Modelled CONCRETELY (a tiny `bexpr` with an IrBinOp2    *)
(*     ctor) so the left-nested tree is provable NON-vacuously: a length-   *)
(*     only law could not distinguish the fold's SHAPE.                     *)
(* ===================================================================== *)

Section BoolopFold.

(* A minimal concrete emit-node: a leaf var, or a binary op node (op + two kids). *)
Inductive bexpr : Type :=
  | BVar (id : string)
  | BBinOp (op : string) (l : bexpr) (r : bexpr).

(* boolop_fold : left-fold `values[1:]` into a left-nested BBinOp tree, applying the
   (here identity) dispatcher to each operand — the WhyML `boolop_fold` twin. *)
Fixpoint bfold (op : string) (acc : bexpr) (rest : list bexpr) : bexpr :=
  match rest with
  | nil => acc
  | v :: tl => bfold op (BBinOp op acc v) tl
  end.

(* OBSERVABILITY (non-vacuity): a 3-operand `a and b and c` folds to the LEFT-nested
   tree `((a and b) and c)` — NOT the right-nested `(a and (b and c))`. *)
Theorem bfold_observe :
  bfold "and" (BVar "a") (BVar "b" :: BVar "c" :: nil)
    = BBinOp "and" (BBinOp "and" (BVar "a") (BVar "b")) (BVar "c").
Proof. reflexivity. Qed.

(* Single operand: `a and b` -> `(a and b)`. *)
Theorem bfold_single :
  bfold "and" (BVar "a") (BVar "b" :: nil) = BBinOp "and" (BVar "a") (BVar "b").
Proof. reflexivity. Qed.

(* Empty tail: `a` (a degenerate 1-value BoolOp) folds to just `a`. *)
Theorem bfold_empty : bfold "or" (BVar "a") nil = BVar "a".
Proof. reflexivity. Qed.

(* EVIL TWIN: the fold is LEFT-nested, NOT right-nested — refutable, so the tree
   SHAPE is genuinely pinned (non-vacuous). *)
Theorem bfold_evil_right_nested :
  bfold "and" (BVar "a") (BVar "b" :: BVar "c" :: nil)
    <> BBinOp "and" (BVar "a") (BBinOp "and" (BVar "b") (BVar "c")).
Proof. simpl; discriminate. Qed.

End BoolopFold.

(* ===================================================================== *)
(* 5d. The CONCRETE lambda param-name compaction — the WhyML twin of        *)
(*     `lambda_param_names_of` (`[arg.arg for arg in expr.args.args]`).      *)
(*     Modelled CONCRETELY (project the arg name, rewrap as a var-node) so   *)
(*     the param list is provable NON-vacuously.                            *)
(* ===================================================================== *)

Section LambdaParams.

(* A minimal concrete arg/var node: a var carrying its name. *)
Inductive lnode : Type := LVar (id : string).
Definition lname (a : lnode) : string := match a with LVar n => n end.

(* lambda_param_names_of : project the name from each arg, rewrap as a var-node —
   the WhyML `lambda_param_names_of` twin (over the args list). *)
Fixpoint lparams (l : list lnode) : list lnode :=
  match l with
  | nil => nil
  | a :: t => LVar (lname a) :: lparams t
  end.

(* OBSERVABILITY (non-vacuity): a 2-param lambda `lambda x, y: ...` yields exactly
   the param-name list `[x; y]`. *)
Theorem lparams_observe :
  lparams (LVar "x" :: LVar "y" :: nil) = LVar "x" :: LVar "y" :: nil.
Proof. reflexivity. Qed.

Theorem lparams_empty : lparams nil = nil.
Proof. reflexivity. Qed.

(* EVIL TWIN: the params are `[x; y]`, NOT `[x; z]` — refutable, so the names are
   genuinely pinned (non-vacuous, not length-only). *)
Theorem lparams_evil_wrong_name :
  lparams (LVar "x" :: LVar "y" :: nil) <> LVar "x" :: LVar "z" :: nil.
Proof. simpl; discriminate. Qed.

End LambdaParams.

(* ===================================================================== *)
(* 6. VERDICT — assumption audit.  Every result must be `Closed under the  *)
(*    global context` (NO axiom): the 3-axiom trust ledger is intact.      *)
(* ===================================================================== *)

Print Assumptions size_stmt_pos.
Print Assumptions size_try_body_lt.
Print Assumptions size_try_handlers_lt.
Print Assumptions size_try_orelse_lt.
Print Assumptions size_try_final_lt.
Print Assumptions size_handler_le_hlcons.
Print Assumptions size_hltail_le_hlcons.
Print Assumptions size_ehbody_lt_handler.
Print Assumptions handler_list_eq_dec.
Print Assumptions except_handler_eq_dec.
Print Assumptions stmt_kind_of_try.
Print Assumptions tag_try_neq_while.
Print Assumptions tag_try_neq_if.
Print Assumptions stry_body_observable.
Print Assumptions stry_handlers_observable.
Print Assumptions stry_orelse_observable.
Print Assumptions stry_final_observable.
Print Assumptions stry_handlers_empty_neq_nonempty.
Print Assumptions stry_size_grows_with_handlers.
Print Assumptions eh_exc_type_observable.
Print Assumptions eh_name_observable.
Print Assumptions eh_body_observable.
Print Assumptions eh_exc_none_neq_some.
Print Assumptions compaction_observe.
Print Assumptions compaction_single.
Print Assumptions compaction_evil_twin.
Print Assumptions compaction_drops_nonvar.
Print Assumptions bfold_observe.
Print Assumptions bfold_single.
Print Assumptions bfold_empty.
Print Assumptions bfold_evil_right_nested.
Print Assumptions size_match_cases_lt.
Print Assumptions size_mcase_le_mccons.
Print Assumptions size_mctail_le_mccons.
Print Assumptions size_mcbody_lt_mcase.
Print Assumptions match_case_list_eq_dec.
Print Assumptions match_case_eq_dec.
Print Assumptions stmt_kind_of_match.
Print Assumptions tag_match_neq_try.
Print Assumptions tag_match_neq_if.
Print Assumptions smatch_subject_observable.
Print Assumptions smatch_cases_observable.
Print Assumptions smatch_cases_empty_neq_nonempty.
Print Assumptions smatch_size_grows_with_cases.
Print Assumptions mc_pattern_observable.
Print Assumptions mc_guard_observable.
Print Assumptions mc_body_observable.
Print Assumptions mc_guard_none_neq_some.
Print Assumptions stmt_kind_of_delsubscript.
Print Assumptions tag_delsubscript_neq_pass.
Print Assumptions tag_delsubscript_neq_match.
Print Assumptions size_delsubscript_flat.
Print Assumptions sdelsub_array_observable.
Print Assumptions sdelsub_index_observable.
Print Assumptions strl_eq_dec.
Print Assumptions stmt_kind_of_fieldassign.
Print Assumptions stmt_kind_of_arrayslice.
Print Assumptions stmt_kind_of_tupleunpack.
Print Assumptions tag_fieldassign_neq_assign.
Print Assumptions tag_arrayslice_neq_arrayset.
Print Assumptions size_assign_ctors_flat.
Print Assumptions sfieldassign_base_observable.
Print Assumptions sfieldassign_field_observable.
Print Assumptions sfieldassign_value_observable.
Print Assumptions sarrayslice_lower_none_neq_some.
Print Assumptions sarrayslice_upper_none_neq_some.
Print Assumptions sarrayslice_array_observable.
Print Assumptions stupleunpack_targets_observable.
Print Assumptions stupleunpack_empty_neq_nonempty.
Print Assumptions stmt_kind_of_critical.
Print Assumptions tag_critical_neq_try.
Print Assumptions scritical_mutex_observable.
Print Assumptions scritical_assume_observable.
Print Assumptions scritical_body_empty_neq_nonempty.
Print Assumptions scritical_size_grows_with_body.
Print Assumptions stmt_kind_of_ghostarrayset.
Print Assumptions stmt_kind_of_ghostassign.
Print Assumptions tag_ghostarrayset_neq_ghostassign.
Print Assumptions sghostarrayset_target_observable.
Print Assumptions sghostarrayset_index_observable.
Print Assumptions sghostassign_op_observable.
Print Assumptions sghostassign_gtype_observable.
Print Assumptions lparams_observe.
Print Assumptions lparams_empty.
Print Assumptions lparams_evil_wrong_name.
Print Assumptions size_slist_lt_swhile.
Print Assumptions size_body_lt_sif.
Print Assumptions size_orelse_lt_sif.
Print Assumptions size_slist_lt_sfor.
Print Assumptions size_head_le_slcons.
Print Assumptions size_tail_le_slcons.
Print Assumptions iropt_eq_dec.
Print Assumptions ioptstr_eq_dec.
Print Assumptions stmt_ir_eq_dec.
Print Assumptions stmt_list_eq_dec.
Print Assumptions abs_injective.
Print Assumptions abs_surjective.
Print Assumptions stmt_kind_of_pass.
Print Assumptions stmt_kind_of_while.
Print Assumptions stmt_kind_of_if.
Print Assumptions stmt_kind_of_for.
Print Assumptions kind_of_agree.
Print Assumptions stmt_kind_of_assign.
Print Assumptions stmt_kind_of_assert.
Print Assumptions stmt_kind_of_augassign.
Print Assumptions stmt_kind_of_fieldaugassign.
Print Assumptions stmt_kind_of_arrayset.
Print Assumptions tag_augassign_neq_assign.
Print Assumptions tag_augassign_neq_fieldaug.
Print Assumptions tag_augassign_neq_arrayset.
Print Assumptions tag_fieldaug_neq_arrayset.
Print Assumptions saugassign_target_observable.
Print Assumptions saugassign_op_observable.
Print Assumptions saugassign_value_observable.
Print Assumptions sfieldaug_field_observable.
Print Assumptions sarrayset_array_observable.
Print Assumptions sarrayset_index_observable.
Print Assumptions sarrayset_value_observable.
Print Assumptions tag_assign_neq_expr.
Print Assumptions tag_assign_neq_return.
Print Assumptions tag_assert_neq_expr.
Print Assumptions tag_assert_neq_assign.
Print Assumptions sassign_target_observable.
Print Assumptions sassign_value_observable.
Print Assumptions sassert_msg_none_neq_some.
Print Assumptions sassert_msg_observable.
Print Assumptions sassert_test_observable.
Print Assumptions tag_pass_neq_break.
Print Assumptions tag_while_neq_if.
Print Assumptions tag_while_neq_for.
Print Assumptions tag_if_neq_for.
Print Assumptions ctor_pass_neq_break.
Print Assumptions sreturn_none_neq_some.
Print Assumptions swhile_empty_neq_nonempty.
Print Assumptions swhile_size_grows_with_body.
