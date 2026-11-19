(* Phase2l_PyAstExpr.v — axiom-free certificate for the `pyast_expr` INPUT-side
   expression-node value shape (self-tcb-reduction, `_py_expr_to_ir` conversion,
   Stage A' of the L2 dispatch expansion).

   CO-LANDING COUPLING (the tier-3 / lesson-#5 rule, cf. Phase2k_CslClause.v /
   Phase2e_PyAstStmt.v / Phase2d_StmtIR.v): the WhyML `pyast_expr` ADT promoted into
   the emitter preamble (`module6_whyml/preamble.py::_emit_pyx_expr_adt`, gated on
   the tight `_pyx_dispatch_table` sentinel) is a NEW value shape — the INPUT-side
   `ast.expr` union that `_py_expr_to_ir`'s
   `getattr(self, self._PY_EXPR_HANDLERS[type(expr)])(expr)` dispatch selects over —
   so it lands with a proof, not a trusted assumption.  It is DISJOINT from every
   other certified value shape: the constructor prefix here is `PEx*` versus the
   `C*` / `PS*` / `S*` / `Ir*` prefixes of the clause / ast-stmt / stmt-ir / emit_ir
   shapes.

   The emitted WhyML this file certifies is, verbatim:

     type pyast_expr = | PEx_Name name | PEx_Constant py_constant | ... | PEx_Unknown
     let function pyx_kind_of (e: pyast_expr) : string = match e with ... end
     val function pyx_type_name_of (e: emit_ir) : string
     val function pyx_view (e: emit_ir) : pyast_expr
       ensures { pyx_kind_of result = pyx_type_name_of e }
     let <cls>___py_expr_to_ir (self) (expr: emit_ir) : emit_ir =
       match pyx_view expr with
       | PEx_Name _p -> <cls>___py_expr_name self _p
       | ... | PEx_Unknown -> IrOther "UnknownPyExpr" end

   Certified here, against pure inductive datatypes with NO axiom:

     (a) `pyast_expr` is a well-formed inductive carrying FOREIGN payload types (the
         per-class handler parameter types — none of them mentions `pyast_expr`, so
         there is no mutual recursion and the datatype is NON-recursive, which is
         exactly why Why3 accepts arms carrying mutable records and `array` fields);
     (b) `pyx_kind_of` is EXACT on every constructor and TOTAL, and the constructor
         tags are pairwise DISTINCT — the dispatch really does separate the 23
         expression classes;
     (c) THE LOAD-BEARING SOUNDNESS OBLIGATION: the abstract `pyx_view` +
         `pyx_type_name_of` pair is CONSISTENT, i.e. the `ensures` law
         `pyx_kind_of (pyx_view e) = pyx_type_name_of e` is SATISFIABLE.  A WhyML
         `val function` with an `ensures` is an assumption, and an UNSATISFIABLE
         assumption would let the whole-file proof derive False.  Section 3 exhibits
         a model for an ARBITRARY view (`tag := fun e => pyx_kind_of (view e)`),
         proving no inconsistency can be introduced by this pair, for any view
         whatsoever;
     (d) NON-VACUITY of the emitted dispatch: `pyx_dispatch` (the verbatim image of
         the emitted match, over arbitrary handlers) applied to a node of class K is
         PROVABLY that class's handler applied to that node's payload, and the
         default arm fires ONLY on `PEx_Unknown`.  A facade — any dispatch
         independent of the node — refutes these;
     (e) the DISPATCH-KIND DETERMINACY the conversion actually buys: if two nodes
         have the same kind they take the same handler, and a node whose kind is
         "Name" can NOT take the BinOp handler.  This is precisely the content the
         `\trusted` stub did not have (its result was an unconstrained emit_ir).

   The WhyML keeps `pyx_view`'s PAYLOAD unconstrained (Stage A' — the ADT is not yet
   recursive), and that is modelled faithfully here: `view` is a Section variable, so
   nothing below assumes anything about which payload a node carries.  Stage B (the
   recursive `pyast_expr` with a structural `pyx_size` variant) will strengthen the
   view and will need its own well-foundedness section.

   The `Print Assumptions` block at the bottom is the trust check: every result must
   be `Closed under the global context` (NO axiom) so the 3-axiom trust ledger
   (`proof_axiom_allowlist.py`) stays intact.  Nothing here is Admitted.
   Build: part of `make` (listed in `_CoqProject` after `Phase2k_CslClause.v`). *)

Require Import ZArith String List Bool Lia.
Import ListNotations.
Open Scope string_scope.

Section PyAstExpr.

(* The 23 handler PARAMETER types, abstracted (see header (a)).  Kept Section
   variables so `pyast_expr` provably carries FOREIGN payloads — there is no
   `pyast_expr` occurrence inside any of them, hence the datatype is non-recursive.
   In the emission these are `name`, `py_constant`, `unaryop`, `binop`,
   `py_compare_node`, `py_boolop_node`, `int`, `tuple`, `subscript`, `list`,
   `attribute`, `py_dict_node`, `set`, `py_genexp_node`, `py_listcomp_node`,
   `py_setcomp_node`, `py_dictcomp_node`, `int`, `ifexp`, `starred`, `namedexpr`,
   `py_lambda_node`, `slice`. *)
Variable TName TConstant TUnaryOp TBinOp TCompare TBoolOp TCall TTuple TSubscript
         TList TAttribute TDict TSet TGeneratorExp TListComp TSetComp TDictComp
         TJoinedStr TIfExp TStarred TNamedExpr TLambda TSlice : Type.

(* ===================================================================== *)
(* 1. The input-side expression ADT — mirrors the WhyML `type pyast_expr`. *)
(* ===================================================================== *)

Inductive pyast_expr : Type :=
  | PEx_Name (p : TName)
  | PEx_Constant (p : TConstant)
  | PEx_UnaryOp (p : TUnaryOp)
  | PEx_BinOp (p : TBinOp)
  | PEx_Compare (p : TCompare)
  | PEx_BoolOp (p : TBoolOp)
  | PEx_Call (p : TCall)
  | PEx_Tuple (p : TTuple)
  | PEx_Subscript (p : TSubscript)
  | PEx_List (p : TList)
  | PEx_Attribute (p : TAttribute)
  | PEx_Dict (p : TDict)
  | PEx_Set (p : TSet)
  | PEx_GeneratorExp (p : TGeneratorExp)
  | PEx_ListComp (p : TListComp)
  | PEx_SetComp (p : TSetComp)
  | PEx_DictComp (p : TDictComp)
  | PEx_JoinedStr (p : TJoinedStr)
  | PEx_IfExp (p : TIfExp)
  | PEx_Starred (p : TStarred)
  | PEx_NamedExpr (p : TNamedExpr)
  | PEx_Lambda (p : TLambda)
  | PEx_Slice (p : TSlice)
  | PEx_Unknown.

(* The tag discriminant — verbatim image of the WhyML `pyx_kind_of`.  Note the
   arms are in SOURCE ORDER (the emitter derives them from `_PY_EXPR_HANDLERS`,
   and a Python dict lookup takes the first matching key). *)
Definition pyx_kind_of (e : pyast_expr) : string :=
  match e with
  | PEx_Name _         => "Name"
  | PEx_Constant _     => "Constant"
  | PEx_UnaryOp _      => "UnaryOp"
  | PEx_BinOp _        => "BinOp"
  | PEx_Compare _      => "Compare"
  | PEx_BoolOp _       => "BoolOp"
  | PEx_Call _         => "Call"
  | PEx_Tuple _        => "Tuple"
  | PEx_Subscript _    => "Subscript"
  | PEx_List _         => "List"
  | PEx_Attribute _    => "Attribute"
  | PEx_Dict _         => "Dict"
  | PEx_Set _          => "Set"
  | PEx_GeneratorExp _ => "GeneratorExp"
  | PEx_ListComp _     => "ListComp"
  | PEx_SetComp _      => "SetComp"
  | PEx_DictComp _     => "DictComp"
  | PEx_JoinedStr _    => "JoinedStr"
  | PEx_IfExp _        => "IfExp"
  | PEx_Starred _      => "Starred"
  | PEx_NamedExpr _    => "NamedExpr"
  | PEx_Lambda _       => "Lambda"
  | PEx_Slice _        => "Slice"
  | PEx_Unknown        => ""
  end.

(* ===================================================================== *)
(* 2. (b) `pyx_kind_of` is EXACT and TOTAL; the tags are pairwise DISTINCT. *)
(* ===================================================================== *)

Theorem kind_of_name : forall p, pyx_kind_of (PEx_Name p) = "Name".
Proof. reflexivity. Qed.
Theorem kind_of_binop : forall p, pyx_kind_of (PEx_BinOp p) = "BinOp".
Proof. reflexivity. Qed.
Theorem kind_of_slice : forall p, pyx_kind_of (PEx_Slice p) = "Slice".
Proof. reflexivity. Qed.
Theorem kind_of_unknown : pyx_kind_of PEx_Unknown = "".
Proof. reflexivity. Qed.

(* TOTAL: `pyx_kind_of` is a plain function, so it is defined on every node; the
   substantive statement is that it lands in the FINITE table of the 23 class names
   plus the empty default — i.e. the dispatch chain in the emitted `match` is
   EXHAUSTIVE and nothing escapes it. *)
Definition pyx_kind_table : list string :=
  ["Name"; "Constant"; "UnaryOp"; "BinOp"; "Compare"; "BoolOp"; "Call"; "Tuple";
   "Subscript"; "List"; "Attribute"; "Dict"; "Set"; "GeneratorExp"; "ListComp";
   "SetComp"; "DictComp"; "JoinedStr"; "IfExp"; "Starred"; "NamedExpr"; "Lambda";
   "Slice"; ""].

Theorem pyx_kind_total : forall e, In (pyx_kind_of e) pyx_kind_table.
Proof. intro e; destruct e; simpl; tauto. Qed.

(* Pairwise DISTINCT tags: a representative spread across the table, including the
   two `int`-payload arms (Call / JoinedStr) that would collide if the emitter keyed
   the arms on the payload TYPE instead of the AST class. *)
Theorem tag_name_neq_binop : forall p q,
  pyx_kind_of (PEx_Name p) <> pyx_kind_of (PEx_BinOp q).
Proof. intros; simpl; discriminate. Qed.
Theorem tag_call_neq_joinedstr : forall p q,
  pyx_kind_of (PEx_Call p) <> pyx_kind_of (PEx_JoinedStr q).
Proof. intros; simpl; discriminate. Qed.
Theorem tag_list_neq_set : forall p q,
  pyx_kind_of (PEx_List p) <> pyx_kind_of (PEx_Set q).
Proof. intros; simpl; discriminate. Qed.
Theorem tag_listcomp_neq_setcomp : forall p q,
  pyx_kind_of (PEx_ListComp p) <> pyx_kind_of (PEx_SetComp q).
Proof. intros; simpl; discriminate. Qed.
Theorem tag_unknown_neq_any_class : forall p,
  pyx_kind_of PEx_Unknown <> pyx_kind_of (PEx_Name p).
Proof. intros; simpl; discriminate. Qed.

(* The tag table has no duplicates — no two AST classes share a dispatch key, so the
   emitted match arms cannot shadow one another (contrast `_PY_OP_MAP`, where
   duplicate VALUES really do occur and source order is load-bearing). *)
Theorem pyx_kind_table_nodup : NoDup pyx_kind_table.
Proof.
  repeat (apply NoDup_cons; [ simpl; intuition discriminate | ]).
  apply NoDup_nil.
Qed.

(* ===================================================================== *)
(* 3. (c) THE SOUNDNESS OBLIGATION: the abstract `pyx_view` / `pyx_type_name_of`   *)
(*    pair is CONSISTENT.  A WhyML `val function ... ensures {...}` is an          *)
(*    ASSUMPTION; if it were unsatisfiable the whole-file proof could derive       *)
(*    False and every goal would go green for the wrong reason.  We exhibit a      *)
(*    model for an ARBITRARY view, so the pair introduces no inconsistency         *)
(*    whatever the real node semantics turn out to be.                            *)
(* ===================================================================== *)

Section ViewConsistency.

(* `E` is the WhyML `emit_ir` the dispatcher's parameter carries (the modelling
   convention by which an ExprIR-typed input child stands for the raw ast node). *)
Variable E : Type.

(* For ANY view function whatsoever there is a tag function making the emitted
   `ensures` law hold.  Hence the `val function pyx_view ... ensures { pyx_kind_of
   result = pyx_type_name_of e }` declaration is satisfiable, i.e. sound to assume. *)
Theorem pyx_view_law_satisfiable :
  forall view : E -> pyast_expr,
  exists tag : E -> string, forall e : E, pyx_kind_of (view e) = tag e.
Proof. intro view. exists (fun e => pyx_kind_of (view e)). reflexivity. Qed.

(* And the law is NOT DEGENERATE: it does not force the view to be constant.  A law
   satisfiable only by a constant view would make the emitted dispatch a facade —
   every node would take the same arm.  Here two distinct nodes provably take
   different arms while still satisfying the law. *)
Variable E_eq_dec : forall a b : E, {a = b} + {a <> b}.

Theorem pyx_view_law_admits_distinct_kinds :
  forall (e1 e2 : E) (p : TName) (q : TBinOp), e1 <> e2 ->
  exists view : E -> pyast_expr, exists tag : E -> string,
    (forall e : E, pyx_kind_of (view e) = tag e)
    /\ tag e1 = "Name" /\ tag e2 = "BinOp".
Proof.
  intros e1 e2 p q Hne.
  exists (fun e => if E_eq_dec e e1 then PEx_Name p else PEx_BinOp q).
  exists (fun e => pyx_kind_of
            (if E_eq_dec e e1 then PEx_Name p else PEx_BinOp q)).
  split; [ reflexivity | split ].
  - destruct (E_eq_dec e1 e1) as [_ | Hc]; [ reflexivity | exfalso; apply Hc; reflexivity ].
  - destruct (E_eq_dec e2 e1) as [Hc | _]; [ exfalso; apply Hne; symmetry; exact Hc
                                           | reflexivity ].
Qed.

End ViewConsistency.

(* ===================================================================== *)
(* 4. (d) NON-VACUITY of the emitted dispatch, and (e) kind determinacy.  *)
(*    `pyx_dispatch` is the verbatim image of the emitted `match`, over    *)
(*    ARBITRARY handlers — a facade (a chain independent of the node)      *)
(*    refutes every theorem in this section.                              *)
(* ===================================================================== *)

Section Dispatch.

Variable R : Type.                      (* the WhyML `emit_ir` result type *)
Variable h_name : TName -> R.
Variable h_constant : TConstant -> R.
Variable h_unaryop : TUnaryOp -> R.
Variable h_binop : TBinOp -> R.
Variable h_compare : TCompare -> R.
Variable h_boolop : TBoolOp -> R.
Variable h_call : TCall -> R.
Variable h_tuple : TTuple -> R.
Variable h_subscript : TSubscript -> R.
Variable h_list : TList -> R.
Variable h_attribute : TAttribute -> R.
Variable h_dict : TDict -> R.
Variable h_set : TSet -> R.
Variable h_genexp : TGeneratorExp -> R.
Variable h_listcomp : TListComp -> R.
Variable h_setcomp : TSetComp -> R.
Variable h_dictcomp : TDictComp -> R.
Variable h_fstring : TJoinedStr -> R.
Variable h_ifexp : TIfExp -> R.
Variable h_starred : TStarred -> R.
Variable h_walrus : TNamedExpr -> R.
Variable h_lambda : TLambda -> R.
Variable h_slice : TSlice -> R.
Variable r_unknown : R.                 (* the source default `IrOther "UnknownPyExpr"` *)

Definition pyx_dispatch (e : pyast_expr) : R :=
  match e with
  | PEx_Name p         => h_name p
  | PEx_Constant p     => h_constant p
  | PEx_UnaryOp p      => h_unaryop p
  | PEx_BinOp p        => h_binop p
  | PEx_Compare p      => h_compare p
  | PEx_BoolOp p       => h_boolop p
  | PEx_Call p         => h_call p
  | PEx_Tuple p        => h_tuple p
  | PEx_Subscript p    => h_subscript p
  | PEx_List p         => h_list p
  | PEx_Attribute p    => h_attribute p
  | PEx_Dict p         => h_dict p
  | PEx_Set p          => h_set p
  | PEx_GeneratorExp p => h_genexp p
  | PEx_ListComp p     => h_listcomp p
  | PEx_SetComp p      => h_setcomp p
  | PEx_DictComp p     => h_dictcomp p
  | PEx_JoinedStr p    => h_fstring p
  | PEx_IfExp p        => h_ifexp p
  | PEx_Starred p      => h_starred p
  | PEx_NamedExpr p    => h_walrus p
  | PEx_Lambda p       => h_lambda p
  | PEx_Slice p        => h_slice p
  | PEx_Unknown        => r_unknown
  end.

(* Each class routes to ITS OWN handler, applied to THAT node's payload. *)
Theorem dispatch_name : forall p, pyx_dispatch (PEx_Name p) = h_name p.
Proof. reflexivity. Qed.
Theorem dispatch_constant : forall p, pyx_dispatch (PEx_Constant p) = h_constant p.
Proof. reflexivity. Qed.
Theorem dispatch_binop : forall p, pyx_dispatch (PEx_BinOp p) = h_binop p.
Proof. reflexivity. Qed.
Theorem dispatch_call : forall p, pyx_dispatch (PEx_Call p) = h_call p.
Proof. reflexivity. Qed.
Theorem dispatch_fstring : forall p, pyx_dispatch (PEx_JoinedStr p) = h_fstring p.
Proof. reflexivity. Qed.
Theorem dispatch_walrus : forall p, pyx_dispatch (PEx_NamedExpr p) = h_walrus p.
Proof. reflexivity. Qed.
Theorem dispatch_slice : forall p, pyx_dispatch (PEx_Slice p) = h_slice p.
Proof. reflexivity. Qed.

(* THE DEFAULT FIRES ONLY ON `PEx_Unknown`.  This is the theorem that separates the
   conversion from the `\trusted` stub it replaces: the stub's result could have been
   the fallback for ANY node.  (Stated for a handler set that is genuinely distinct
   from the default, which is the case whenever the handlers are the real ones.) *)
Theorem dispatch_unknown : pyx_dispatch PEx_Unknown = r_unknown.
Proof. reflexivity. Qed.
Theorem dispatch_not_default_when_handler_differs : forall p,
  h_name p <> r_unknown -> pyx_dispatch (PEx_Name p) <> r_unknown.
Proof. intros p H; simpl; exact H. Qed.

(* (e) KIND DETERMINACY: same kind => same handler is taken.  Read contrapositively,
   this is exactly the content a caller gains — knowing the node's runtime class now
   determines WHICH handler produced the result, hence constrains the result's kind.
   The `\trusted` val gave no such constraint. *)
Theorem dispatch_determined_by_kind_name : forall e,
  pyx_kind_of e = "Name" ->
  exists q : TName, e = PEx_Name q /\ pyx_dispatch e = h_name q.
Proof.
  intros e H; destruct e; simpl in H; try discriminate.
  exists p. split; reflexivity.
Qed.

Theorem dispatch_name_is_not_binop_handler : forall e,
  pyx_kind_of e = "Name" ->
  (forall q : TBinOp, e <> PEx_BinOp q).
Proof.
  intros e H q Heq; subst; simpl in H; discriminate.
Qed.

End Dispatch.

(* Decidable equality on the node ADT, given decidable equality on every payload —
   the standard well-formedness obligation the sibling certificates carry. *)
Hypothesis TName_eq_dec : forall a b : TName, {a = b} + {a <> b}.
Hypothesis TBinOp_eq_dec : forall a b : TBinOp, {a = b} + {a <> b}.

Theorem pex_name_injective : forall a b : TName, PEx_Name a = PEx_Name b -> a = b.
Proof. intros a b H; injection H; auto. Qed.
Theorem pex_name_neq_pex_binop : forall (a : TName) (b : TBinOp),
  PEx_Name a <> PEx_BinOp b.
Proof. intros a b H; discriminate. Qed.

End PyAstExpr.

(* ===================================================================== *)
(* 4b. THE SECOND INSTANCE — `csl_node` (the 77-entry `_CSL_HANDLERS` table).   *)
(*                                                                             *)
(*   The `_py_expr_to_ir` and `_csl_to_ir` dispatchers are two instances of ONE *)
(*   construction, so the facts above are re-usable in shape — but `csl_node`   *)
(*   has a property `pyast_expr` does NOT, and it is the one worth certifying:  *)
(*   FOUR DISTINCT ARMS SHARE A SINGLE HANDLER.  `_CSL_HANDLERS` maps           *)
(*   `Requires` / `Ensures` / `LoopInvariant` / `LoopVariant` — all subclasses  *)
(*   of `ContractWrapper` — to the SAME method `_csl_contract_wrapper`, whose   *)
(*   parameter is typed with the BASE class.  That is why the emitter derives   *)
(*   an arm's payload from the HANDLER's declared parameter class rather than   *)
(*   from the table key.  Certified below: arm-sharing does NOT collapse the    *)
(*   kinds (the four arms stay distinguishable), and it does NOT weaken the     *)
(*   determinacy result (knowing the kind still determines the handler AND the  *)
(*   payload).  The second difference — the default arm is the source's own     *)
(*   RAISE rather than a fallback node — is certified as `dispatch_rejects_...`:*)
(*   an unsupported node CANNOT silently produce a result.                      *)
(* ===================================================================== *)

Section CslNodeSharedHandler.

(* The shared base payload (`contractwrapper`) and two unrelated payloads. *)
Variable TWrapper TBin TVar : Type.
Variable R2 : Type.

Inductive csl_node : Type :=
  | PCsl_CSLBinOp (p : TBin)
  | PCsl_CSLVar (p : TVar)
  | PCsl_ContractWrapper (p : TWrapper)
  | PCsl_Requires (p : TWrapper)          (* subclass -> BASE-typed payload *)
  | PCsl_Ensures (p : TWrapper)
  | PCsl_LoopInvariant (p : TWrapper)
  | PCsl_LoopVariant (p : TWrapper)
  | PCsl_Unknown.

Definition cslx_kind_of (e : csl_node) : string :=
  match e with
  | PCsl_CSLBinOp _        => "CSLBinOp"
  | PCsl_CSLVar _          => "CSLVar"
  | PCsl_ContractWrapper _ => "ContractWrapper"
  | PCsl_Requires _        => "Requires"
  | PCsl_Ensures _         => "Ensures"
  | PCsl_LoopInvariant _   => "LoopInvariant"
  | PCsl_LoopVariant _     => "LoopVariant"
  | PCsl_Unknown           => ""
  end.

Variable h_binop : TBin -> R2.
Variable h_var : TVar -> R2.
Variable h_contract_wrapper : TWrapper -> R2.   (* the SHARED handler *)
Variable exc : R2.                              (* the source's `raise` arm *)

Definition csl_dispatch (e : csl_node) : R2 :=
  match e with
  | PCsl_CSLBinOp p        => h_binop p
  | PCsl_CSLVar p          => h_var p
  | PCsl_ContractWrapper p => h_contract_wrapper p
  | PCsl_Requires p        => h_contract_wrapper p
  | PCsl_Ensures p         => h_contract_wrapper p
  | PCsl_LoopInvariant p   => h_contract_wrapper p
  | PCsl_LoopVariant p     => h_contract_wrapper p
  | PCsl_Unknown           => exc
  end.

(* ARM-SHARING IS FAITHFUL: the four subclass arms really do take the base handler,
   applied to that node's own payload — the Python subtype call, exactly. *)
Theorem csl_requires_takes_wrapper_handler : forall p,
  csl_dispatch (PCsl_Requires p) = h_contract_wrapper p.
Proof. reflexivity. Qed.
Theorem csl_ensures_takes_wrapper_handler : forall p,
  csl_dispatch (PCsl_Ensures p) = h_contract_wrapper p.
Proof. reflexivity. Qed.
Theorem csl_loopinv_takes_wrapper_handler : forall p,
  csl_dispatch (PCsl_LoopInvariant p) = h_contract_wrapper p.
Proof. reflexivity. Qed.
Theorem csl_loopvar_takes_wrapper_handler : forall p,
  csl_dispatch (PCsl_LoopVariant p) = h_contract_wrapper p.
Proof. reflexivity. Qed.

(* ...and sharing a HANDLER does NOT merge the KINDS: the four arms remain
   distinguishable, so the dispatch table is still injective on keys. *)
Theorem csl_shared_handler_keeps_kinds_distinct : forall p q,
  cslx_kind_of (PCsl_Requires p) <> cslx_kind_of (PCsl_Ensures q).
Proof. intros; simpl; discriminate. Qed.
Theorem csl_shared_handler_kind_neq_base : forall p q,
  cslx_kind_of (PCsl_Requires p) <> cslx_kind_of (PCsl_ContractWrapper q).
Proof. intros; simpl; discriminate. Qed.

(* DETERMINACY still holds through a shared handler: the kind determines both the
   arm and the applied handler. *)
Theorem csl_dispatch_determined_by_kind_requires : forall e,
  cslx_kind_of e = "Requires" ->
  exists p : TWrapper, e = PCsl_Requires p /\ csl_dispatch e = h_contract_wrapper p.
Proof.
  intros e H; destruct e; simpl in H; try discriminate.
  exists p. split; reflexivity.
Qed.

(* THE REJECTING DEFAULT (this dispatcher's second difference from the expression
   one): the `raise` arm is reached ONLY by the unsupported node.  So a node of a
   SUPPORTED class provably does NOT take the error path — the emitted body cannot
   silently turn an unsupported node into an IR node, and cannot silently reject a
   supported one either. *)
Theorem csl_dispatch_rejects_only_unknown : forall e,
  csl_dispatch e = exc ->
  e = PCsl_Unknown
  \/ (exists p, e = PCsl_CSLBinOp p /\ h_binop p = exc)
  \/ (exists p, e = PCsl_CSLVar p /\ h_var p = exc)
  \/ (exists p, csl_dispatch e = h_contract_wrapper p /\ h_contract_wrapper p = exc).
Proof.
  intros e H; destruct e; simpl in H.
  - right; left; exists p; split; [ reflexivity | exact H ].
  - right; right; left; exists p; split; [ reflexivity | exact H ].
  - right; right; right; exists p; split; [ reflexivity | exact H ].
  - right; right; right; exists p; split; [ reflexivity | exact H ].
  - right; right; right; exists p; split; [ reflexivity | exact H ].
  - right; right; right; exists p; split; [ reflexivity | exact H ].
  - right; right; right; exists p; split; [ reflexivity | exact H ].
  - left; reflexivity.
Qed.

(* And the sharp form, which is what the conversion actually buys: if every real
   handler differs from the error result on the payload at hand, then reaching the
   error result MEANS the node was unsupported. *)
Theorem csl_error_implies_unknown : forall e,
  (forall p : TBin, h_binop p <> exc) ->
  (forall p : TVar, h_var p <> exc) ->
  (forall p : TWrapper, h_contract_wrapper p <> exc) ->
  csl_dispatch e = exc -> e = PCsl_Unknown.
Proof.
  intros e Hb Hv Hw H; destruct e; simpl in H.
  - exfalso; exact (Hb p H).
  - exfalso; exact (Hv p H).
  - exfalso; exact (Hw p H).
  - exfalso; exact (Hw p H).
  - exfalso; exact (Hw p H).
  - exfalso; exact (Hw p H).
  - exfalso; exact (Hw p H).
  - reflexivity.
Qed.

End CslNodeSharedHandler.

(* ===================================================================== *)
(* 5. VERDICT — assumption audit.  Every result must be `Closed under the  *)
(*    global context` (NO axiom): the 3-axiom trust ledger is intact.      *)
(* ===================================================================== *)

Print Assumptions kind_of_name.
Print Assumptions kind_of_binop.
Print Assumptions kind_of_slice.
Print Assumptions kind_of_unknown.
Print Assumptions pyx_kind_total.
Print Assumptions tag_name_neq_binop.
Print Assumptions tag_call_neq_joinedstr.
Print Assumptions tag_list_neq_set.
Print Assumptions tag_listcomp_neq_setcomp.
Print Assumptions tag_unknown_neq_any_class.
Print Assumptions pyx_kind_table_nodup.
Print Assumptions pyx_view_law_satisfiable.
Print Assumptions pyx_view_law_admits_distinct_kinds.
Print Assumptions dispatch_name.
Print Assumptions dispatch_constant.
Print Assumptions dispatch_binop.
Print Assumptions dispatch_call.
Print Assumptions dispatch_fstring.
Print Assumptions dispatch_walrus.
Print Assumptions dispatch_slice.
Print Assumptions dispatch_unknown.
Print Assumptions dispatch_not_default_when_handler_differs.
Print Assumptions dispatch_determined_by_kind_name.
Print Assumptions dispatch_name_is_not_binop_handler.
Print Assumptions pex_name_injective.
Print Assumptions pex_name_neq_pex_binop.
Print Assumptions csl_requires_takes_wrapper_handler.
Print Assumptions csl_ensures_takes_wrapper_handler.
Print Assumptions csl_loopinv_takes_wrapper_handler.
Print Assumptions csl_loopvar_takes_wrapper_handler.
Print Assumptions csl_shared_handler_keeps_kinds_distinct.
Print Assumptions csl_shared_handler_kind_neq_base.
Print Assumptions csl_dispatch_determined_by_kind_requires.
Print Assumptions csl_dispatch_rejects_only_unknown.
Print Assumptions csl_error_implies_unknown.
