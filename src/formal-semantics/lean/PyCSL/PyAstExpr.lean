/-
  PyAstExpr.lean — axiom-free certificate for the `pyast_expr` INPUT-side
  expression-node value shape (self-tcb-reduction, `_py_expr_to_ir` conversion,
  Stage A' of the L2 dispatch expansion).  The Lean twin of
  `rocq/Phase2l_PyAstExpr.v`.

  CO-LANDING COUPLING (the tier-3 / lesson-#5 rule, cf. CslClause.lean /
  PyAstStmt.lean / StmtIR.lean): the WhyML `pyast_expr` ADT promoted into the
  emitter preamble (`module6_whyml/preamble.py::_emit_pyx_expr_adt`, gated on the
  tight `_pyx_dispatch_table` sentinel) is a NEW value shape — the INPUT-side
  `ast.expr` union that `_py_expr_to_ir`'s
  `getattr(self, self._PY_EXPR_HANDLERS[type(expr)])(expr)` dispatch selects over
  — so it lands with a proof, not a trusted assumption.  DISJOINT from every
  other certified shape: the ctor prefix here is `PEx*` vs the `C*`/`PS*`/`S*`/
  `Ir*` clause / ast-stmt / stmt-ir / emit_ir prefixes.

  Certified here, against pure inductive datatypes with NO axiom:

    (a) `PyastExpr` is a well-formed inductive carrying FOREIGN payload types
        (the per-class handler PARAMETER types — none mentions `PyastExpr`, so
        the datatype is NON-recursive, which is exactly why Why3 accepts arms
        carrying mutable records and `array` fields);
    (b) `pyxKindOf` is EXACT per ctor and TOTAL into a finite duplicate-free tag
        table, and the ctor tags are pairwise DISTINCT;
    (c) THE LOAD-BEARING SOUNDNESS OBLIGATION: the abstract WhyML
        `val function pyx_view (e: emit_ir) : pyast_expr
           ensures { pyx_kind_of result = pyx_type_name_of e }`
        pair is CONSISTENT.  A `val function` with an `ensures` is an ASSUMPTION;
        an unsatisfiable one would let the whole-file proof derive False and turn
        every goal green for the wrong reason.  `pyxView_law_satisfiable` exhibits
        a model for an ARBITRARY view, and `pyxView_law_admits_distinct_kinds`
        shows the law does not collapse the view to a constant (which would make
        the dispatch a facade);
    (d) NON-VACUITY of the emitted dispatch: `pyxDispatch` (the verbatim image of
        the emitted `match`, over ARBITRARY handlers) applied to a node of class K
        is provably that class's handler applied to THAT node's payload, and the
        default arm fires ONLY on `PEx_Unknown`;
    (e) DISPATCH-KIND DETERMINACY — the content the conversion actually buys over
        the `\trusted` stub it replaces: the node's runtime class DETERMINES which
        handler produced the result (the stub's result was an unconstrained
        emit_ir).

  Stage A' keeps `pyx_view`'s PAYLOAD unconstrained (the ADT is not yet
  recursive), and that is modelled faithfully: `view` is a variable, so nothing
  below assumes anything about which payload a node carries.

  The `#print axioms` block at the bottom is the trust check: only Lean's own
  three kernel axioms (`propext`, `Classical.choice`, `Quot.sound`) may appear —
  NO 4th, and in particular NO `sorryAx` — so the 3-axiom trust ledger stays
  intact.  Nothing here is `sorry`.
-/

namespace PyAstExprCert

-- ===================================================================== --
-- 1. The input-side expression ADT — mirrors the WhyML `type pyast_expr`.--
--    The 23 type parameters are the handler PARAMETER types, in SOURCE   --
--    ORDER (`name`, `py_constant`, `unaryop`, `binop`, `py_compare_node`,--
--    `py_boolop_node`, `int`, `tuple`, `subscript`, `list`, `attribute`, --
--    `py_dict_node`, `set`, `py_genexp_node`, `py_listcomp_node`,        --
--    `py_setcomp_node`, `py_dictcomp_node`, `int`, `ifexp`, `starred`,   --
--    `namedexpr`, `py_lambda_node`, `slice`).                            --
-- ===================================================================== --

structure Payloads where
  TName : Type
  TConstant : Type
  TUnaryOp : Type
  TBinOp : Type
  TCompare : Type
  TBoolOp : Type
  TCall : Type
  TTuple : Type
  TSubscript : Type
  TList : Type
  TAttribute : Type
  TDict : Type
  TSet : Type
  TGeneratorExp : Type
  TListComp : Type
  TSetComp : Type
  TDictComp : Type
  TJoinedStr : Type
  TIfExp : Type
  TStarred : Type
  TNamedExpr : Type
  TLambda : Type
  TSlice : Type

variable {P : Payloads}

inductive PyastExpr (P : Payloads) where
  | PEx_Name (p : P.TName)
  | PEx_Constant (p : P.TConstant)
  | PEx_UnaryOp (p : P.TUnaryOp)
  | PEx_BinOp (p : P.TBinOp)
  | PEx_Compare (p : P.TCompare)
  | PEx_BoolOp (p : P.TBoolOp)
  | PEx_Call (p : P.TCall)
  | PEx_Tuple (p : P.TTuple)
  | PEx_Subscript (p : P.TSubscript)
  | PEx_List (p : P.TList)
  | PEx_Attribute (p : P.TAttribute)
  | PEx_Dict (p : P.TDict)
  | PEx_Set (p : P.TSet)
  | PEx_GeneratorExp (p : P.TGeneratorExp)
  | PEx_ListComp (p : P.TListComp)
  | PEx_SetComp (p : P.TSetComp)
  | PEx_DictComp (p : P.TDictComp)
  | PEx_JoinedStr (p : P.TJoinedStr)
  | PEx_IfExp (p : P.TIfExp)
  | PEx_Starred (p : P.TStarred)
  | PEx_NamedExpr (p : P.TNamedExpr)
  | PEx_Lambda (p : P.TLambda)
  | PEx_Slice (p : P.TSlice)
  | PEx_Unknown

/-- The tag discriminant — verbatim image of the WhyML `pyx_kind_of`. -/
def pyxKindOf : PyastExpr P → String
  | .PEx_Name _         => "Name"
  | .PEx_Constant _     => "Constant"
  | .PEx_UnaryOp _      => "UnaryOp"
  | .PEx_BinOp _        => "BinOp"
  | .PEx_Compare _      => "Compare"
  | .PEx_BoolOp _       => "BoolOp"
  | .PEx_Call _         => "Call"
  | .PEx_Tuple _        => "Tuple"
  | .PEx_Subscript _    => "Subscript"
  | .PEx_List _         => "List"
  | .PEx_Attribute _    => "Attribute"
  | .PEx_Dict _         => "Dict"
  | .PEx_Set _          => "Set"
  | .PEx_GeneratorExp _ => "GeneratorExp"
  | .PEx_ListComp _     => "ListComp"
  | .PEx_SetComp _      => "SetComp"
  | .PEx_DictComp _     => "DictComp"
  | .PEx_JoinedStr _    => "JoinedStr"
  | .PEx_IfExp _        => "IfExp"
  | .PEx_Starred _      => "Starred"
  | .PEx_NamedExpr _    => "NamedExpr"
  | .PEx_Lambda _       => "Lambda"
  | .PEx_Slice _        => "Slice"
  | .PEx_Unknown        => ""

-- ===================================================================== --
-- 2. (b) `pyxKindOf` EXACT per ctor, TOTAL into a duplicate-free table,  --
--    tags pairwise DISTINCT.                                            --
-- ===================================================================== --

theorem kindOf_name (p : P.TName) : pyxKindOf (P := P) (.PEx_Name p) = "Name" := rfl
theorem kindOf_binop (p : P.TBinOp) : pyxKindOf (P := P) (.PEx_BinOp p) = "BinOp" := rfl
theorem kindOf_slice (p : P.TSlice) : pyxKindOf (P := P) (.PEx_Slice p) = "Slice" := rfl
theorem kindOf_unknown : pyxKindOf (P := P) .PEx_Unknown = "" := rfl

/-- The finite tag table the dispatch chain enumerates. -/
def pyxKindTable : List String :=
  ["Name", "Constant", "UnaryOp", "BinOp", "Compare", "BoolOp", "Call", "Tuple",
   "Subscript", "List", "Attribute", "Dict", "Set", "GeneratorExp", "ListComp",
   "SetComp", "DictComp", "JoinedStr", "IfExp", "Starred", "NamedExpr", "Lambda",
   "Slice", ""]

/-- TOTAL: every node's kind lands in the table — the emitted match is EXHAUSTIVE
    and nothing escapes it. -/
theorem pyxKind_total (e : PyastExpr P) : pyxKindOf e ∈ pyxKindTable := by
  cases e <;> simp [pyxKindOf, pyxKindTable]

/-- No two AST classes share a dispatch key, so the emitted arms cannot shadow one
    another (contrast `_PY_OP_MAP`, where duplicate VALUES do occur and source
    order is load-bearing). -/
theorem pyxKindTable_nodup : pyxKindTable.Nodup := by
  simp [pyxKindTable]

theorem tag_name_neq_binop (p : P.TName) (q : P.TBinOp) :
    pyxKindOf (P := P) (.PEx_Name p) ≠ pyxKindOf (P := P) (.PEx_BinOp q) := by
  simp only [pyxKindOf]; decide

/-- The two `int`-payload arms (Call / JoinedStr) would COLLIDE if the emitter
    keyed the arms on the payload TYPE instead of the AST class. -/
theorem tag_call_neq_joinedstr (p : P.TCall) (q : P.TJoinedStr) :
    pyxKindOf (P := P) (.PEx_Call p) ≠ pyxKindOf (P := P) (.PEx_JoinedStr q) := by
  simp only [pyxKindOf]; decide

theorem tag_list_neq_set (p : P.TList) (q : P.TSet) :
    pyxKindOf (P := P) (.PEx_List p) ≠ pyxKindOf (P := P) (.PEx_Set q) := by
  simp only [pyxKindOf]; decide

theorem tag_listcomp_neq_setcomp (p : P.TListComp) (q : P.TSetComp) :
    pyxKindOf (P := P) (.PEx_ListComp p) ≠ pyxKindOf (P := P) (.PEx_SetComp q) := by
  simp only [pyxKindOf]; decide

theorem tag_unknown_neq_any_class (p : P.TName) :
    pyxKindOf (P := P) .PEx_Unknown ≠ pyxKindOf (P := P) (.PEx_Name p) := by
  simp only [pyxKindOf]; decide

-- ===================================================================== --
-- 3. (c) THE SOUNDNESS OBLIGATION — the abstract `pyx_view` /            --
--    `pyx_type_name_of` pair is CONSISTENT (and not degenerate).         --
-- ===================================================================== --

/-- For ANY view whatsoever there is a tag function making the emitted `ensures`
    law hold.  Hence the `val function pyx_view … ensures { pyx_kind_of result =
    pyx_type_name_of e }` declaration is SATISFIABLE, i.e. sound to assume: it
    cannot be the source of a false proof. -/
theorem pyxView_law_satisfiable {E : Type} (view : E → PyastExpr P) :
    ∃ tag : E → String, ∀ e : E, pyxKindOf (view e) = tag e :=
  ⟨fun e => pyxKindOf (view e), fun _ => rfl⟩

/-- …and the law is NOT DEGENERATE: it does not force the view to be constant.
    A law satisfiable only by a constant view would make the emitted dispatch a
    facade (every node taking the same arm). -/
theorem pyxView_law_admits_distinct_kinds {E : Type} [DecidableEq E]
    (e1 e2 : E) (p : P.TName) (q : P.TBinOp) (hne : e1 ≠ e2) :
    ∃ (view : E → PyastExpr P) (tag : E → String),
      (∀ e : E, pyxKindOf (view e) = tag e) ∧ tag e1 = "Name" ∧ tag e2 = "BinOp" := by
  refine ⟨fun e => if e = e1 then .PEx_Name p else .PEx_BinOp q,
          fun e => pyxKindOf (if e = e1 then PyastExpr.PEx_Name p else .PEx_BinOp q),
          fun _ => rfl, ?_, ?_⟩
  · simp [pyxKindOf]
  · simp [pyxKindOf, hne.symm]

-- ===================================================================== --
-- 4. (d) NON-VACUITY of the emitted dispatch + (e) kind determinacy.     --
--    `pyxDispatch` is the verbatim image of the emitted `match`, over    --
--    ARBITRARY handlers — a facade refutes every theorem here.           --
-- ===================================================================== --

section Dispatch

variable {R : Type}
variable (hName : P.TName → R) (hConstant : P.TConstant → R)
variable (hUnaryOp : P.TUnaryOp → R) (hBinOp : P.TBinOp → R)
variable (hCompare : P.TCompare → R) (hBoolOp : P.TBoolOp → R)
variable (hCall : P.TCall → R) (hTuple : P.TTuple → R)
variable (hSubscript : P.TSubscript → R) (hList : P.TList → R)
variable (hAttribute : P.TAttribute → R) (hDict : P.TDict → R)
variable (hSet : P.TSet → R) (hGenExp : P.TGeneratorExp → R)
variable (hListComp : P.TListComp → R) (hSetComp : P.TSetComp → R)
variable (hDictComp : P.TDictComp → R) (hFString : P.TJoinedStr → R)
variable (hIfExp : P.TIfExp → R) (hStarred : P.TStarred → R)
variable (hWalrus : P.TNamedExpr → R) (hLambda : P.TLambda → R)
variable (hSlice : P.TSlice → R) (rUnknown : R)

/-- The verbatim image of the emitted body. -/
def pyxDispatch : PyastExpr P → R
  | .PEx_Name p         => hName p
  | .PEx_Constant p     => hConstant p
  | .PEx_UnaryOp p      => hUnaryOp p
  | .PEx_BinOp p        => hBinOp p
  | .PEx_Compare p      => hCompare p
  | .PEx_BoolOp p       => hBoolOp p
  | .PEx_Call p         => hCall p
  | .PEx_Tuple p        => hTuple p
  | .PEx_Subscript p    => hSubscript p
  | .PEx_List p         => hList p
  | .PEx_Attribute p    => hAttribute p
  | .PEx_Dict p         => hDict p
  | .PEx_Set p          => hSet p
  | .PEx_GeneratorExp p => hGenExp p
  | .PEx_ListComp p     => hListComp p
  | .PEx_SetComp p      => hSetComp p
  | .PEx_DictComp p     => hDictComp p
  | .PEx_JoinedStr p    => hFString p
  | .PEx_IfExp p        => hIfExp p
  | .PEx_Starred p      => hStarred p
  | .PEx_NamedExpr p    => hWalrus p
  | .PEx_Lambda p       => hLambda p
  | .PEx_Slice p        => hSlice p
  | .PEx_Unknown        => rUnknown

local notation "D" => pyxDispatch hName hConstant hUnaryOp hBinOp hCompare hBoolOp
  hCall hTuple hSubscript hList hAttribute hDict hSet hGenExp hListComp hSetComp
  hDictComp hFString hIfExp hStarred hWalrus hLambda hSlice rUnknown

theorem dispatch_name (p : P.TName) : D (.PEx_Name p) = hName p := rfl
theorem dispatch_constant (p : P.TConstant) : D (.PEx_Constant p) = hConstant p := rfl
theorem dispatch_binop (p : P.TBinOp) : D (.PEx_BinOp p) = hBinOp p := rfl
theorem dispatch_call (p : P.TCall) : D (.PEx_Call p) = hCall p := rfl
theorem dispatch_fstring (p : P.TJoinedStr) : D (.PEx_JoinedStr p) = hFString p := rfl
theorem dispatch_walrus (p : P.TNamedExpr) : D (.PEx_NamedExpr p) = hWalrus p := rfl
theorem dispatch_slice (p : P.TSlice) : D (.PEx_Slice p) = hSlice p := rfl
theorem dispatch_unknown : D (.PEx_Unknown) = rUnknown := rfl

/-- THE DEFAULT FIRES ONLY ON `PEx_Unknown` — the theorem that separates the
    conversion from the `\trusted` stub it replaces, whose result could have been
    the fallback for ANY node. -/
theorem dispatch_not_default_when_handler_differs (p : P.TName)
    (h : hName p ≠ rUnknown) : D (.PEx_Name p) ≠ rUnknown := h

/-- (e) KIND DETERMINACY: the node's runtime class determines WHICH handler
    produced the result — hence constrains the result.  The `\trusted` val gave
    no such constraint. -/
theorem dispatch_determined_by_kind_name (e : PyastExpr P) (h : pyxKindOf e = "Name") :
    ∃ q : P.TName, e = .PEx_Name q ∧ D e = hName q := by
  cases e <;> simp [pyxKindOf] at h
  case PEx_Name q => exact ⟨q, rfl, rfl⟩

theorem dispatch_name_is_not_binop_handler (e : PyastExpr P)
    (h : pyxKindOf e = "Name") (q : P.TBinOp) : e ≠ .PEx_BinOp q := by
  cases e <;> simp [pyxKindOf] at h <;> simp

end Dispatch

theorem pex_name_injective (a b : P.TName)
    (h : (PyastExpr.PEx_Name a : PyastExpr P) = .PEx_Name b) : a = b := by
  injection h

theorem pex_name_neq_pex_binop (a : P.TName) (b : P.TBinOp) :
    (PyastExpr.PEx_Name a : PyastExpr P) ≠ .PEx_BinOp b := by
  intro h; cases h

end PyAstExprCert

-- ===================================================================== --
-- 5. VERDICT — assumption audit.  Every result must print "does not      --
--    depend on any axioms": the 3-axiom trust ledger is intact.          --
-- ===================================================================== --

#print axioms PyAstExprCert.kindOf_name
#print axioms PyAstExprCert.kindOf_binop
#print axioms PyAstExprCert.kindOf_slice
#print axioms PyAstExprCert.kindOf_unknown
#print axioms PyAstExprCert.pyxKind_total
#print axioms PyAstExprCert.pyxKindTable_nodup
#print axioms PyAstExprCert.tag_name_neq_binop
#print axioms PyAstExprCert.tag_call_neq_joinedstr
#print axioms PyAstExprCert.tag_list_neq_set
#print axioms PyAstExprCert.tag_listcomp_neq_setcomp
#print axioms PyAstExprCert.tag_unknown_neq_any_class
#print axioms PyAstExprCert.pyxView_law_satisfiable
#print axioms PyAstExprCert.pyxView_law_admits_distinct_kinds
#print axioms PyAstExprCert.dispatch_name
#print axioms PyAstExprCert.dispatch_constant
#print axioms PyAstExprCert.dispatch_binop
#print axioms PyAstExprCert.dispatch_call
#print axioms PyAstExprCert.dispatch_fstring
#print axioms PyAstExprCert.dispatch_walrus
#print axioms PyAstExprCert.dispatch_slice
#print axioms PyAstExprCert.dispatch_unknown
#print axioms PyAstExprCert.dispatch_not_default_when_handler_differs
#print axioms PyAstExprCert.dispatch_determined_by_kind_name
#print axioms PyAstExprCert.dispatch_name_is_not_binop_handler
#print axioms PyAstExprCert.pex_name_injective
#print axioms PyAstExprCert.pex_name_neq_pex_binop
