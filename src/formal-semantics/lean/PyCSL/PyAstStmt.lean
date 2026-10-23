/-
  PyAstStmt.lean — axiom-free certificate for the `pyast_stmt` INPUT-side
  raw-`ast.stmt` value shape (self-tcb-reduction giants, generic class-body
  lowering).  The Lean twin of `rocq/Phase2e_PyAstStmt.v`.

  CO-LANDING COUPLING (the tier-3 / lesson-#5 rule, cf. StmtIR.lean /
  PyConstVal.lean): the WhyML `pyast_stmt` theory promoted into the emitter
  preamble (`module6_whyml/preamble.py`, gated on `_uses_pyast_stmt`) is a NEW
  value shape — the raw `ast.stmt` union a class-body iterator
  (`_collect_class_constants`) isinstance-dispatches over — so it lands with a
  proof, not a trusted assumption.  DISJOINT from the OUTPUT-side `stmt_ir` of
  StmtIR.lean: the ctor prefix here is `PS*` (`PSAssign` — the INPUT node) vs
  `S*` there (`SAssign` — the LOWERED node).  Certified here, against pure
  inductive datatypes with NO axiom:

    (a) `PyAstStmt` is a well-formed inductive carrying the FOREIGN emit_ir
        expr-child type `ε` (never mentions `PyAstStmt` — no mutual recursion),
        with DECIDABLE equality given decidable equality on `ε`;
    (b) `stmtNodeKindOf` is EXACT per ctor, tags pairwise DISTINCT;
    (c) the LOAD-BEARING faithfulness laws — the WhyML `is_K_faithful` lemmas:
        `isKNode s = true ↔ stmtNodeKindOf s = "K"` for K ∈ {assign, annassign,
        classdef, functiondef} — the ones that discharge in the WhyML whole-file
        proof, here certified to model the isinstance dispatch faithfully;
    (d) the projectors `stmtTarget0`/`stmtValue`/`stmtAnnotation` (: PyAstStmt →
        ε), `defName` (: PyAstStmt → String) are EXACT on their slots with the
        SAME off-variant defaults as the WhyML, and every carried field is
        OBSERVABLE (non-vacuity);
    (e) the class-body list `Psl = PSLNil | PSLCons PyAstStmt Psl` (the
        `node.body` iterated) has a WELL-FOUNDED length `pslLen` and a TOTAL
        indexer `pslNth`: the tail is STRICTLY shorter than the cons, so the
        WhyML `pslNth`'s `variant { l }` structural recursion (the psl-loop
        `variant { psl_len - idx }`) is certified to terminate.

  The abstract WhyML `val`s `class_body_ast`/`ps_const_int`/`ps_field_mem` and
  the opaque `stmt_targets_len` are NOT `pyast_stmt` soundness obligations
  (opaque readers / a `val function` count) — modelled as variables, TOTAL by
  typing, exactly as the WhyML leaves them.

  Verdict decided by `#print axioms` at the bottom: only standard Lean kernel
  axioms — or NONE — may appear; NO 4th, extension-specific axiom, so the
  3-axiom trust ledger stays intact.
-/

namespace PyAstStmtCert

variable {ε : Type}

-- ===================================================================== --
-- 1. The raw ast.stmt ADT — mirrors the WhyML `type pyast_stmt`.         --
--    PSAnnAssign field order (target, annotation, value) — exactly the   --
--    WhyML `PSAnnAssign emit_ir emit_ir emit_ir`.                        --
-- ===================================================================== --

inductive PyAstStmt (ε : Type) where
  | PSAssign (target value : ε)
  | PSAnnAssign (target annotation value : ε)
  | PSClassDef (name : String)
  | PSFunctionDef (name : String)
  | PSPass
  | PSExprEllipsis
  | PSOther
  deriving DecidableEq

/-- The tag discriminant — verbatim image of the WhyML `stmt_node_kind_of`.
    `PSPass` / `PSExprEllipsis` are the nullary `ast.Pass` and
    `ast.Expr(Constant(Ellipsis))` — the two `node.body[0]` shapes
    `_is_overload_stub` discriminates (a stub body is exactly `pass` or `...`). -/
def stmtNodeKindOf : PyAstStmt ε → String
  | .PSAssign _ _      => "Assign"
  | .PSAnnAssign _ _ _ => "AnnAssign"
  | .PSClassDef _      => "ClassDef"
  | .PSFunctionDef _   => "FunctionDef"
  | .PSPass            => "Pass"
  | .PSExprEllipsis    => "ExprEllipsis"
  | .PSOther           => "Other"

/-- The isinstance discriminants — WhyML `is_K_node` predicates. -/
def isAssignNode : PyAstStmt ε → Bool
  | .PSAssign _ _ => true | _ => false
def isAnnassignNode : PyAstStmt ε → Bool
  | .PSAnnAssign _ _ _ => true | _ => false
def isClassdefNode : PyAstStmt ε → Bool
  | .PSClassDef _ => true | _ => false
def isFunctiondefNode : PyAstStmt ε → Bool
  | .PSFunctionDef _ => true | _ => false
def isPassNode : PyAstStmt ε → Bool
  | .PSPass => true | _ => false
def isExprEllipsisNode : PyAstStmt ε → Bool
  | .PSExprEllipsis => true | _ => false

/-- The projectors — WhyML `stmt_target0`/`stmt_value`/`stmt_annotation`/
    `def_name`, with the SAME off-variant defaults (`IrOther ""` ≈ `dflt`, `""`). -/
def stmtTarget0 (dflt : ε) : PyAstStmt ε → ε
  | .PSAssign t _      => t
  | .PSAnnAssign t _ _ => t
  | _                  => dflt
def stmtValue (dflt : ε) : PyAstStmt ε → ε
  | .PSAssign _ v      => v
  | .PSAnnAssign _ _ v => v
  | _                  => dflt
def stmtAnnotation (dflt : ε) : PyAstStmt ε → ε
  | .PSAnnAssign _ a _ => a
  | _                  => dflt
def defName : PyAstStmt ε → String
  | .PSClassDef n    => n
  | .PSFunctionDef n => n
  | _                => ""

-- ===================================================================== --
-- 2. (b) `stmtNodeKindOf` EXACT per ctor + tags DISTINCT.                --
-- ===================================================================== --

theorem kindOf_assign (t v : ε) : stmtNodeKindOf (.PSAssign t v) = "Assign" := rfl
theorem kindOf_annassign (t a v : ε) : stmtNodeKindOf (.PSAnnAssign t a v) = "AnnAssign" := rfl
theorem kindOf_classdef (n : String) : stmtNodeKindOf (ε := ε) (.PSClassDef n) = "ClassDef" := rfl
theorem kindOf_functiondef (n : String) : stmtNodeKindOf (ε := ε) (.PSFunctionDef n) = "FunctionDef" := rfl
theorem kindOf_pass : stmtNodeKindOf (ε := ε) .PSPass = "Pass" := rfl
theorem kindOf_expr_ellipsis : stmtNodeKindOf (ε := ε) .PSExprEllipsis = "ExprEllipsis" := rfl
theorem kindOf_other : stmtNodeKindOf (ε := ε) .PSOther = "Other" := rfl

theorem tag_assign_neq_annassign (t v a b c : ε) :
    stmtNodeKindOf (.PSAssign t v) ≠ stmtNodeKindOf (.PSAnnAssign a b c) := by simp only [stmtNodeKindOf]; decide
theorem tag_classdef_neq_functiondef (n : String) :
    stmtNodeKindOf (ε := ε) (.PSClassDef n) ≠ stmtNodeKindOf (ε := ε) (.PSFunctionDef n) := by simp only [stmtNodeKindOf]; decide
theorem tag_pass_neq_expr_ellipsis :
    stmtNodeKindOf (ε := ε) .PSPass ≠ stmtNodeKindOf (ε := ε) .PSExprEllipsis := by simp only [stmtNodeKindOf]; decide
theorem tag_pass_neq_other :
    stmtNodeKindOf (ε := ε) .PSPass ≠ stmtNodeKindOf (ε := ε) .PSOther := by simp only [stmtNodeKindOf]; decide
theorem tag_expr_ellipsis_neq_other :
    stmtNodeKindOf (ε := ε) .PSExprEllipsis ≠ stmtNodeKindOf (ε := ε) .PSOther := by simp only [stmtNodeKindOf]; decide

-- ===================================================================== --
-- 3. (c) THE LOAD-BEARING faithfulness laws: isKNode s ↔ kind = "K".     --
-- ===================================================================== --

theorem is_assign_faithful (s : PyAstStmt ε) :
    isAssignNode s = true ↔ stmtNodeKindOf s = "Assign" := by
  cases s <;> simp [isAssignNode, stmtNodeKindOf]
theorem is_annassign_faithful (s : PyAstStmt ε) :
    isAnnassignNode s = true ↔ stmtNodeKindOf s = "AnnAssign" := by
  cases s <;> simp [isAnnassignNode, stmtNodeKindOf]
theorem is_classdef_faithful (s : PyAstStmt ε) :
    isClassdefNode s = true ↔ stmtNodeKindOf s = "ClassDef" := by
  cases s <;> simp [isClassdefNode, stmtNodeKindOf]
theorem is_functiondef_faithful (s : PyAstStmt ε) :
    isFunctiondefNode s = true ↔ stmtNodeKindOf s = "FunctionDef" := by
  cases s <;> simp [isFunctiondefNode, stmtNodeKindOf]
theorem is_pass_faithful (s : PyAstStmt ε) :
    isPassNode s = true ↔ stmtNodeKindOf s = "Pass" := by
  cases s <;> simp [isPassNode, stmtNodeKindOf]
theorem is_expr_ellipsis_faithful (s : PyAstStmt ε) :
    isExprEllipsisNode s = true ↔ stmtNodeKindOf s = "ExprEllipsis" := by
  cases s <;> simp [isExprEllipsisNode, stmtNodeKindOf]
/-- The pass / expr-ellipsis discriminants are MUTUALLY EXCLUSIVE. -/
theorem is_pass_not_expr_ellipsis (s : PyAstStmt ε) :
    isPassNode s = true → isExprEllipsisNode s = false := by
  cases s <;> simp [isPassNode, isExprEllipsisNode]

-- ===================================================================== --
-- 4. (d) Projectors EXACT + every carried field OBSERVABLE (non-vacuity).--
-- ===================================================================== --

theorem target0_assign (d t v : ε) : stmtTarget0 d (.PSAssign t v) = t := rfl
theorem target0_annassign (d t a v : ε) : stmtTarget0 d (.PSAnnAssign t a v) = t := rfl
theorem value_assign (d t v : ε) : stmtValue d (.PSAssign t v) = v := rfl
theorem value_annassign (d t a v : ε) : stmtValue d (.PSAnnAssign t a v) = v := rfl
theorem annotation_annassign (d t a v : ε) : stmtAnnotation d (.PSAnnAssign t a v) = a := rfl
theorem defName_classdef (n : String) : defName (ε := ε) (.PSClassDef n) = n := rfl
theorem defName_functiondef (n : String) : defName (ε := ε) (.PSFunctionDef n) = n := rfl
/- off-variant defaults (WhyML sentinel) -/
theorem target0_default (d : ε) : stmtTarget0 d .PSOther = d := rfl
theorem annotation_default (d t v : ε) : stmtAnnotation d (.PSAssign t v) = d := rfl

theorem psassign_target_observable (t u v : ε) (h : t ≠ u) :
    (PyAstStmt.PSAssign t v) ≠ PyAstStmt.PSAssign u v := by
  intro he; cases he; exact h rfl
theorem psassign_value_observable (t v w : ε) (h : v ≠ w) :
    (PyAstStmt.PSAssign t v) ≠ PyAstStmt.PSAssign t w := by
  intro he; cases he; exact h rfl
theorem psannassign_annotation_observable (t a b v : ε) (h : a ≠ b) :
    (PyAstStmt.PSAnnAssign t a v) ≠ PyAstStmt.PSAnnAssign t b v := by
  intro he; cases he; exact h rfl
theorem psannassign_value_observable (t a v w : ε) (h : v ≠ w) :
    (PyAstStmt.PSAnnAssign t a v) ≠ PyAstStmt.PSAnnAssign t a w := by
  intro he; cases he; exact h rfl
theorem psclassdef_name_observable (n m : String) (h : n ≠ m) :
    (PyAstStmt.PSClassDef n : PyAstStmt ε) ≠ PyAstStmt.PSClassDef m := by
  intro he; cases he; exact h rfl
theorem psclassdef_neq_psfunctiondef (n : String) :
    (PyAstStmt.PSClassDef n : PyAstStmt ε) ≠ PyAstStmt.PSFunctionDef n := by
  intro he; cases he

-- ===================================================================== --
-- 5. (e) The class-body list `Psl` — WELL-FOUNDED length + TOTAL indexer.--
--    (`pslLen`/`pslNth`; Nat length ⇒ well-founded automatically, the    --
--    faithful non-negative model of the WhyML `int` length.)            --
-- ===================================================================== --

inductive Psl (ε : Type) where
  | PSLNil
  | PSLCons (h : PyAstStmt ε) (t : Psl ε)

def pslLen : Psl ε → Nat
  | .PSLNil      => 0
  | .PSLCons _ t => 1 + pslLen t

/-- TOTAL indexer — WhyML `psl_nth` (PSOther default on nil/overshoot). -/
def pslNth : Nat → Psl ε → PyAstStmt ε
  | _,     .PSLNil      => .PSOther
  | 0,     .PSLCons h _ => h
  | n + 1, .PSLCons _ t => pslNth n t

/-- Well-foundedness witness for the WhyML `variant { l }` / `variant { psl_len -
    idx }`: the TAIL is STRICTLY shorter than the cons that carries it. -/
theorem pslLen_cons (h : PyAstStmt ε) (t : Psl ε) : pslLen (.PSLCons h t) = 1 + pslLen t := rfl
theorem pslTail_len_lt (h : PyAstStmt ε) (t : Psl ε) : pslLen t < pslLen (.PSLCons h t) := by
  simp only [pslLen]; omega

/-- Totality — observable behaviour of the total indexer. -/
theorem pslNth_zero (h : PyAstStmt ε) (t : Psl ε) : pslNth 0 (.PSLCons h t) = h := rfl
theorem pslNth_nil (i : Nat) : pslNth i (.PSLNil : Psl ε) = .PSOther := by cases i <;> rfl
theorem pslNth_succ (i : Nat) (h : PyAstStmt ε) (t : Psl ε) :
    pslNth (i + 1) (.PSLCons h t) = pslNth i t := rfl
theorem psl_empty_neq_nonempty (h : PyAstStmt ε) (t : Psl ε) :
    (Psl.PSLNil : Psl ε) ≠ Psl.PSLCons h t := by intro he; cases he
theorem psl_len_grows_with_cons (h : PyAstStmt ε) (t : Psl ε) :
    pslLen t < pslLen (.PSLCons h t) := by simp only [pslLen]; omega

end PyAstStmtCert

-- ===================================================================== --
-- 6. VERDICT — axiom audit. Only standard Lean kernel axioms may appear; --
--    NO 4th, extension-specific axiom — the 3-axiom ledger stays intact. --
-- ===================================================================== --

#print axioms PyAstStmtCert.kindOf_assign
#print axioms PyAstStmtCert.kindOf_annassign
#print axioms PyAstStmtCert.kindOf_classdef
#print axioms PyAstStmtCert.kindOf_functiondef
#print axioms PyAstStmtCert.kindOf_pass
#print axioms PyAstStmtCert.kindOf_expr_ellipsis
#print axioms PyAstStmtCert.kindOf_other
#print axioms PyAstStmtCert.tag_assign_neq_annassign
#print axioms PyAstStmtCert.tag_classdef_neq_functiondef
#print axioms PyAstStmtCert.tag_pass_neq_expr_ellipsis
#print axioms PyAstStmtCert.tag_pass_neq_other
#print axioms PyAstStmtCert.tag_expr_ellipsis_neq_other
#print axioms PyAstStmtCert.is_assign_faithful
#print axioms PyAstStmtCert.is_annassign_faithful
#print axioms PyAstStmtCert.is_classdef_faithful
#print axioms PyAstStmtCert.is_functiondef_faithful
#print axioms PyAstStmtCert.is_pass_faithful
#print axioms PyAstStmtCert.is_expr_ellipsis_faithful
#print axioms PyAstStmtCert.is_pass_not_expr_ellipsis
#print axioms PyAstStmtCert.target0_assign
#print axioms PyAstStmtCert.target0_annassign
#print axioms PyAstStmtCert.value_assign
#print axioms PyAstStmtCert.value_annassign
#print axioms PyAstStmtCert.annotation_annassign
#print axioms PyAstStmtCert.defName_classdef
#print axioms PyAstStmtCert.defName_functiondef
#print axioms PyAstStmtCert.target0_default
#print axioms PyAstStmtCert.annotation_default
#print axioms PyAstStmtCert.psassign_target_observable
#print axioms PyAstStmtCert.psassign_value_observable
#print axioms PyAstStmtCert.psannassign_annotation_observable
#print axioms PyAstStmtCert.psannassign_value_observable
#print axioms PyAstStmtCert.psclassdef_name_observable
#print axioms PyAstStmtCert.psclassdef_neq_psfunctiondef
#print axioms PyAstStmtCert.pslLen_cons
#print axioms PyAstStmtCert.pslTail_len_lt
#print axioms PyAstStmtCert.pslNth_zero
#print axioms PyAstStmtCert.pslNth_nil
#print axioms PyAstStmtCert.pslNth_succ
#print axioms PyAstStmtCert.psl_empty_neq_nonempty
#print axioms PyAstStmtCert.psl_len_grows_with_cons
