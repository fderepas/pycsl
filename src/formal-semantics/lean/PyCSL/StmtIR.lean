/-
  StmtIR.lean — axiom-free certificate for the `stmt_ir` statement-IR ADT
  (self-tcb-reduction M5, C-bucket: the list-append-mutation wall).  The Lean
  twin of `rocq/Phase2d_StmtIR.v`.

  CO-LANDING COUPLING (the tier-3 rule, cf. PyConstVal.lean): the WhyML
  `stmt_ir` theory promoted into the emitter preamble
  (`module6_whyml/preamble.py::_emit_exprir_theory`, gated on `_uses_stmt_ir`)
  is a NEW value shape — the statement-node sum an `_py_stmt_*` handler appends
  to its `ir_stmts` list — so it lands with a proof, not a trusted assumption.
  Certified here, against pure inductive datatypes with NO axiom:

    (a) `StmtIr` has DECIDABLE equality (given decidable equality on the abstract
        expr-child type) and a size measure — well-founded;
    (b) the dict->ctor abstraction `abs : PyStmt → StmtIr` is TOTAL, INJECTIVE,
        and SURJECTIVE onto the ADT (the recognized key-set maps injectively);
    (c) `stmtKindOf` is EXACT per constructor, AGREES with the Python `"stmt"`
        string through `abs`, and the tags are pairwise DISTINCT (the honest node
        identity the pre-feature integer-0 erasure destroyed, fable Oracle 3);
    (d) NO MUTUAL RECURSION WITH emit_ir: the expr children carry the FOREIGN
        emit_ir type `ε` (a type variable), which never mentions `StmtIr`.

  SUB-BODY increment (this landing): `StmtIr` gains the COMPOUND constructors
  SWhile / SIf / SFor, carrying nested statement body/orelse LISTS as a bespoke
  MONOMORPHIC cons-list `StmtList` — MUTUALLY recursive WITH `StmtIr` (the WhyML
  twin uses `with stmt_list`).  The flat `size` (≡1) is replaced by the MUTUAL
  measure `sizeStmt` / `sizeSList`, well-founded by the two size-DECREASE lemmas
  (a sub-body is strictly smaller than its containing node).  `seq_to_sl` (the
  runtime materialization) is Why3-intrinsic, needing no clause here.

  Verdict decided by `#print axioms` at the bottom: only the standard Lean kernel
  axioms (propext, Classical.choice, Quot.sound) — or NONE — may appear; NO 4th,
  extension-specific axiom — so the 3-axiom trust ledger stays intact.
-/

namespace StmtIRCert

-- ===================================================================== --
-- 1. The statement-IR ADT — mirrors the WhyML `type stmt_ir with stmt_list`. --
-- ===================================================================== --

/-- The monomorphic option sibling of the emit_ir ADT — mirrors the WhyML
    `iropt_ir = IrONone | IrOSome emit_ir`. `SReturn` carries it; it references
    only the FOREIGN `ε`, never `StmtIr`. -/
inductive IrOpt (ε : Type) where
  | IrONone
  | IrOSome (e : ε)
  deriving DecidableEq

/-- The monomorphic option-STRING sibling — mirrors the WhyML `iropt_str = IrSNone
    | IrSSome string`. `SAssert` carries it (the OPTIONAL assert-message string); it
    references NO type variable, so it never mentions `StmtIr`. -/
inductive IrOptStr where
  | ISNone
  | ISSome (s : String)
  deriving DecidableEq

/- The MUTUAL block: `StmtIr` and its sub-body list `StmtList`. `ε` abstracts
   the WhyML emit_ir expr-child type (a FOREIGN type variable, so no `StmtIr`
   sub-term appears through it — no mutual recursion with emit_ir). The COMPOUND
   ctors carry `StmtList` bodies (SWhile: test+body; SIf: test+body+orelse;
   SFor: iter+body). -/
mutual
inductive StmtIr (ε : Type) where
  | SPass
  | SBreak
  | SContinue
  | SReturn (o : IrOpt ε)
  | SExpr (e : ε)
  | SAssign (n : String) (e : ε)
  | SAssert (t : ε) (m : IrOptStr)
  | SAugAssign (n : String) (op : String) (e : ε)
  | SFieldAugAssign (f : String) (op : String) (e : ε)
  | SArraySet (a : ε) (i : ε) (v : ε)
  | SWhile (t : ε) (b : StmtList ε)
  | SIf (t : ε) (b : StmtList ε) (el : StmtList ε)
  | SFor (t : ε) (b : StmtList ε)
  -- STry increment: body / handlers / orelse / finalbody. The handler list is a
  -- bespoke monomorphic cons over the `ExceptHandler` record, MUTUALLY recursive
  -- WITH StmtIr/StmtList (the record's `ehBody` is a `StmtList`).
  | STry (b : StmtList ε) (hs : HandlerList ε) (oe : StmtList ε) (fb : StmtList ε)
  -- SMatch increment: subject + case list. MatchCaseList is a bespoke cons over the
  -- MatchCase record (its `mcBody` is a StmtList — same mutual cycle).
  | SMatch (subj : ε) (cs : MatchCaseList ε)
  -- SDelSubscript increment: `del d[k]` — array + index (FLAT, no sub-body).
  | SDelSubscript (arr : ε) (idx : ε)
inductive StmtList (ε : Type) where
  | SLNil
  | SLCons (h : StmtIr ε) (t : StmtList ε)
inductive HandlerList (ε : Type) where
  | HLNil
  | HLCons (h : ExceptHandler ε) (t : HandlerList ε)
inductive ExceptHandler (ε : Type) where
  | MkEH (ehExcType : IrOptStr) (ehName : IrOptStr) (ehBody : StmtList ε)
inductive MatchCaseList (ε : Type) where
  | MCNil
  | MCCons (c : MatchCase ε) (t : MatchCaseList ε)
inductive MatchCase (ε : Type) where
  | MkMC (mcPattern : ε) (mcGuard : IrOpt ε) (mcBody : StmtList ε)
end

deriving instance DecidableEq for StmtIr, StmtList, HandlerList, ExceptHandler,
  MatchCaseList, MatchCase

variable {ε : Type}

/-- The tag discriminant — image of the WhyML `stmt_kind_of`. -/
def stmtKindOf : StmtIr ε → String
  | .SPass => "Pass"
  | .SBreak => "Break"
  | .SContinue => "Continue"
  | .SReturn _ => "Return"
  | .SExpr _ => "Expr"
  | .SAssign _ _ => "Assign"
  | .SAssert _ _ => "Assert"
  | .SAugAssign _ _ _ => "AugAssign"
  | .SFieldAugAssign _ _ _ => "FieldAugAssign"
  | .SArraySet _ _ _ => "ArraySet"
  | .SWhile _ _ => "While"
  | .SIf _ _ _ => "If"
  | .SFor _ _ => "For"
  | .STry _ _ _ _ => "Try"
  | .SMatch _ _ => "Match"
  | .SDelSubscript _ _ => "DelSubscript"

/- The MUTUAL well-founded size measure — WhyML `size_stmt`/`size_slist`. -/
mutual
def sizeStmt : StmtIr ε → Nat
  | .SPass => 1
  | .SBreak => 1
  | .SContinue => 1
  | .SReturn _ => 1
  | .SExpr _ => 1
  | .SAssign _ _ => 1
  | .SAssert _ _ => 1
  | .SAugAssign _ _ _ => 1
  | .SFieldAugAssign _ _ _ => 1
  | .SArraySet _ _ _ => 1
  | .SWhile _ b => 1 + sizeSList b
  | .SIf _ b el => 1 + sizeSList b + sizeSList el
  | .SFor _ b => 1 + sizeSList b
  | .STry b hs oe fb => 1 + sizeSList b + sizeHList hs + sizeSList oe + sizeSList fb
  | .SMatch _ cs => 1 + sizeMCList cs
  | .SDelSubscript _ _ => 1
def sizeSList : StmtList ε → Nat
  | .SLNil => 0
  | .SLCons h t => sizeStmt h + sizeSList t
def sizeHList : HandlerList ε → Nat
  | .HLNil => 0
  | .HLCons h t => sizeHandler h + sizeHList t
def sizeHandler : ExceptHandler ε → Nat
  | .MkEH _ _ b => 1 + sizeSList b
def sizeMCList : MatchCaseList ε → Nat
  | .MCNil => 0
  | .MCCons c t => sizeMCase c + sizeMCList t
def sizeMCase : MatchCase ε → Nat
  | .MkMC _ _ b => 1 + sizeSList b
end

theorem sizeStmt_pos (s : StmtIr ε) : sizeStmt s ≥ 1 := by
  cases s <;> simp [sizeStmt] <;> omega

/-- Well-foundedness witnesses: a sub-body is STRICTLY smaller than its
    compound node — so a recursive walker over `StmtIr` terminates. -/
theorem sizeSList_lt_swhile (t : ε) (b : StmtList ε) :
    sizeSList b < sizeStmt (StmtIr.SWhile t b) := by
  show sizeSList b < 1 + sizeSList b; omega
theorem sizeBody_lt_sif (t : ε) (b el : StmtList ε) :
    sizeSList b < sizeStmt (StmtIr.SIf t b el) := by
  show sizeSList b < 1 + sizeSList b + sizeSList el; omega
theorem sizeSList_lt_sfor (t : ε) (b : StmtList ε) :
    sizeSList b < sizeStmt (StmtIr.SFor t b) := by
  show sizeSList b < 1 + sizeSList b; omega

/-- Decidable equality on the WHOLE mutual block (`deriving` handles the mutual
    recursion), given decidable equality on the foreign child type. -/
example [DecidableEq ε] : DecidableEq (StmtIr ε) := inferInstance
example [DecidableEq ε] : DecidableEq (StmtList ε) := inferInstance

-- ===================================================================== --
-- 2. The recognized `{"stmt": K}` world + its dict->ctor abstraction.    --
-- ===================================================================== --

inductive PyStmt (ε : Type) where
  | PPass
  | PBreak
  | PContinue
  | PReturn (o : IrOpt ε)
  | PExpr (e : ε)
  | PAssign (n : String) (e : ε)
  | PAssert (t : ε) (m : IrOptStr)
  | PAugAssign (n : String) (op : String) (e : ε)
  | PFieldAugAssign (f : String) (op : String) (e : ε)
  | PArraySet (a : ε) (i : ε) (v : ε)
  | PWhile (t : ε) (b : StmtList ε)
  | PIf (t : ε) (b : StmtList ε) (el : StmtList ε)
  | PFor (t : ε) (b : StmtList ε)
  | PTry (b : StmtList ε) (hs : HandlerList ε) (oe : StmtList ε) (fb : StmtList ε)
  | PMatch (subj : ε) (cs : MatchCaseList ε)
  | PDelSubscript (arr : ε) (idx : ε)

/-- The dict->ctor map (`{"stmt":"Pass"} ↦ SPass`, ..., `{"stmt":"While"} ↦
    SWhile ...`). -/
def abs : PyStmt ε → StmtIr ε
  | .PPass => .SPass
  | .PBreak => .SBreak
  | .PContinue => .SContinue
  | .PReturn o => .SReturn o
  | .PExpr e => .SExpr e
  | .PAssign n e => .SAssign n e
  | .PAssert t m => .SAssert t m
  | .PAugAssign n op e => .SAugAssign n op e
  | .PFieldAugAssign f op e => .SFieldAugAssign f op e
  | .PArraySet a i v => .SArraySet a i v
  | .PWhile t b => .SWhile t b
  | .PIf t b el => .SIf t b el
  | .PFor t b => .SFor t b
  | .PTry b hs oe fb => .STry b hs oe fb
  | .PMatch subj cs => .SMatch subj cs
  | .PDelSubscript a i => .SDelSubscript a i

/-- The Python-side tag string of a recognized node. -/
def pyKindOf : PyStmt ε → String
  | .PPass => "Pass"
  | .PBreak => "Break"
  | .PContinue => "Continue"
  | .PReturn _ => "Return"
  | .PExpr _ => "Expr"
  | .PAssign _ _ => "Assign"
  | .PAssert _ _ => "Assert"
  | .PAugAssign _ _ _ => "AugAssign"
  | .PFieldAugAssign _ _ _ => "FieldAugAssign"
  | .PArraySet _ _ _ => "ArraySet"
  | .PWhile _ _ => "While"
  | .PIf _ _ _ => "If"
  | .PFor _ _ => "For"
  | .PTry _ _ _ _ => "Try"
  | .PMatch _ _ => "Match"
  | .PDelSubscript _ _ => "DelSubscript"

-- ===================================================================== --
-- 3. (b) `abs` is total + injective + surjective.                        --
-- ===================================================================== --

theorem abs_injective : Function.Injective (abs (ε := ε)) := by
  intro x y h
  cases x <;> cases y <;> simp_all [abs]

theorem abs_surjective : ∀ v : StmtIr ε, ∃ s, abs s = v := by
  intro v
  cases v with
  | SPass => exact ⟨.PPass, rfl⟩
  | SBreak => exact ⟨.PBreak, rfl⟩
  | SContinue => exact ⟨.PContinue, rfl⟩
  | SReturn o => exact ⟨.PReturn o, rfl⟩
  | SExpr e => exact ⟨.PExpr e, rfl⟩
  | SAssign n e => exact ⟨.PAssign n e, rfl⟩
  | SAssert t m => exact ⟨.PAssert t m, rfl⟩
  | SAugAssign n op e => exact ⟨.PAugAssign n op e, rfl⟩
  | SFieldAugAssign f op e => exact ⟨.PFieldAugAssign f op e, rfl⟩
  | SArraySet a i v => exact ⟨.PArraySet a i v, rfl⟩
  | SWhile t b => exact ⟨.PWhile t b, rfl⟩
  | SIf t b el => exact ⟨.PIf t b el, rfl⟩
  | SFor t b => exact ⟨.PFor t b, rfl⟩
  | STry b hs oe fb => exact ⟨.PTry b hs oe fb, rfl⟩
  | SMatch subj cs => exact ⟨.PMatch subj cs, rfl⟩
  | SDelSubscript a i => exact ⟨.PDelSubscript a i, rfl⟩

-- ===================================================================== --
-- 4. (c) `stmtKindOf` EXACT per ctor + AGREES through `abs`.             --
-- ===================================================================== --

theorem stmtKindOf_pass : stmtKindOf (ε := ε) .SPass = "Pass" := rfl
theorem stmtKindOf_assign (n : String) (e : ε) : stmtKindOf (.SAssign n e) = "Assign" := rfl
theorem stmtKindOf_assert (t : ε) (m : IrOptStr) : stmtKindOf (.SAssert t m) = "Assert" := rfl
-- SAugAssign/SFieldAugAssign/SArraySet increment: the three tags are EXACT per constructor.
theorem stmtKindOf_augassign (n op : String) (e : ε) : stmtKindOf (.SAugAssign n op e) = "AugAssign" := rfl
theorem stmtKindOf_fieldaugassign (f op : String) (e : ε) : stmtKindOf (.SFieldAugAssign f op e) = "FieldAugAssign" := rfl
theorem stmtKindOf_arrayset (a i v : ε) : stmtKindOf (.SArraySet a i v) = "ArraySet" := rfl
theorem stmtKindOf_return (o : IrOpt ε) : stmtKindOf (.SReturn o) = "Return" := rfl
theorem stmtKindOf_while (t : ε) (b : StmtList ε) : stmtKindOf (.SWhile t b) = "While" := rfl
theorem stmtKindOf_if (t : ε) (b el : StmtList ε) : stmtKindOf (.SIf t b el) = "If" := rfl
theorem stmtKindOf_for (t : ε) (b : StmtList ε) : stmtKindOf (.SFor t b) = "For" := rfl

theorem kindOf_agree (s : PyStmt ε) : stmtKindOf (abs s) = pyKindOf s := by
  cases s <;> rfl

-- ===================================================================== --
-- 5. (c') TAG-PRESERVING: the tags are pairwise DISTINCT (no erasure).   --
-- ===================================================================== --

theorem tag_pass_neq_break : stmtKindOf (ε := ε) .SPass ≠ stmtKindOf (ε := ε) .SBreak := by
  simp only [stmtKindOf]; decide
theorem tag_return_neq_expr (o : IrOpt ε) (e : ε) : stmtKindOf (.SReturn o) ≠ stmtKindOf (.SExpr e) := by
  simp only [stmtKindOf]; decide
-- SAssign + str-Constant recognizer increment: the Assign tag is distinct from Expr/Return.
theorem tag_assign_neq_expr (n : String) (e f : ε) : stmtKindOf (.SAssign n e) ≠ stmtKindOf (.SExpr f) := by
  simp only [stmtKindOf]; decide
theorem tag_assign_neq_return (n : String) (e : ε) (o : IrOpt ε) : stmtKindOf (.SAssign n e) ≠ stmtKindOf (.SReturn o) := by
  simp only [stmtKindOf]; decide
-- SAssert increment: the Assert tag is distinct from the Expr and Assign tags.
theorem tag_assert_neq_expr (t : ε) (m : IrOptStr) (e : ε) : stmtKindOf (.SAssert t m) ≠ stmtKindOf (.SExpr e) := by
  simp only [stmtKindOf]; decide
theorem tag_assert_neq_assign (t : ε) (m : IrOptStr) (n : String) (e : ε) : stmtKindOf (.SAssert t m) ≠ stmtKindOf (.SAssign n e) := by
  simp only [stmtKindOf]; decide
-- SAugAssign/SFieldAugAssign/SArraySet increment: pairwise distinct + distinct from plain Assign.
theorem tag_augassign_neq_assign (n op : String) (e : ε) (m : String) (f : ε) : stmtKindOf (.SAugAssign n op e) ≠ stmtKindOf (.SAssign m f) := by
  simp only [stmtKindOf]; decide
theorem tag_augassign_neq_fieldaug (n op : String) (e : ε) (f g : String) (h : ε) : stmtKindOf (.SAugAssign n op e) ≠ stmtKindOf (.SFieldAugAssign f g h) := by
  simp only [stmtKindOf]; decide
theorem tag_augassign_neq_arrayset (n op : String) (e a i v : ε) : stmtKindOf (.SAugAssign n op e) ≠ stmtKindOf (.SArraySet a i v) := by
  simp only [stmtKindOf]; decide
theorem tag_fieldaug_neq_arrayset (f g : String) (h a i v : ε) : stmtKindOf (.SFieldAugAssign f g h) ≠ stmtKindOf (.SArraySet a i v) := by
  simp only [stmtKindOf]; decide
theorem tag_while_neq_if (t : ε) (b : StmtList ε) (o : ε) (c d : StmtList ε) :
    stmtKindOf (.SWhile t b) ≠ stmtKindOf (.SIf o c d) := by simp only [stmtKindOf]; decide
theorem tag_while_neq_for (t : ε) (b : StmtList ε) (u : ε) (c : StmtList ε) :
    stmtKindOf (.SWhile t b) ≠ stmtKindOf (.SFor u c) := by simp only [stmtKindOf]; decide
theorem tag_if_neq_for (t : ε) (b el : StmtList ε) (u : ε) (c : StmtList ε) :
    stmtKindOf (.SIf t b el) ≠ stmtKindOf (.SFor u c) := by simp only [stmtKindOf]; decide

/-- The constructors themselves are distinct (no erasure to a common value). -/
theorem ctor_pass_neq_break : (StmtIr.SPass : StmtIr ε) ≠ StmtIr.SBreak := by
  intro h; cases h

/-- (c'') The OPTIONAL return value is OBSERVABLE. -/
theorem sreturn_none_neq_some (e : ε) :
    (StmtIr.SReturn .IrONone : StmtIr ε) ≠ StmtIr.SReturn (.IrOSome e) := by
  intro h; cases h

/-- (c'''') SAssign non-vacuity: the TARGET NAME and the RHS VALUE are BOTH observable. -/
theorem sassign_target_observable (n m : String) (e : ε) (h : n ≠ m) :
    (StmtIr.SAssign n e) ≠ StmtIr.SAssign m e := by
  intro he; cases he; exact h rfl
theorem sassign_value_observable (n : String) (e f : ε) (h : e ≠ f) :
    (StmtIr.SAssign n e) ≠ StmtIr.SAssign n f := by
  intro he; cases he; exact h rfl

/-- (c''''') SAssert non-vacuity: the OPTIONAL msg string and the TEST expr are BOTH
    observable — an assert without a message (SAssert t ISNone) and one with a string
    message (SAssert t (ISSome s)) are DISTINCT; two present messages differing in text
    are DISTINCT; the test expr is observable. The conditional msg-add is a real option. -/
theorem sassert_msg_none_neq_some (t : ε) (s : String) :
    (StmtIr.SAssert t .ISNone) ≠ StmtIr.SAssert t (.ISSome s) := by
  intro he; cases he
theorem sassert_msg_observable (t : ε) (s r : String) (h : s ≠ r) :
    (StmtIr.SAssert t (.ISSome s)) ≠ StmtIr.SAssert t (.ISSome r) := by
  intro he; cases he; exact h rfl
theorem sassert_test_observable (t u : ε) (m : IrOptStr) (h : t ≠ u) :
    (StmtIr.SAssert t m) ≠ StmtIr.SAssert u m := by
  intro he; cases he; exact h rfl

/-- (c'''''') SAugAssign/SFieldAugAssign/SArraySet non-vacuity: every carried field is
    OBSERVABLE — the target/field NAME, the OP string, and the emit_ir sub-nodes are carried
    faithfully by the injective constructors, never a shared 0 (the 0900 fixture at the ADT
    level). -/
theorem saugassign_target_observable (n m op : String) (e : ε) (h : n ≠ m) :
    (StmtIr.SAugAssign n op e) ≠ StmtIr.SAugAssign m op e := by
  intro he; cases he; exact h rfl
theorem saugassign_op_observable (n op1 op2 : String) (e : ε) (h : op1 ≠ op2) :
    (StmtIr.SAugAssign n op1 e) ≠ StmtIr.SAugAssign n op2 e := by
  intro he; cases he; exact h rfl
theorem saugassign_value_observable (n op : String) (e f : ε) (h : e ≠ f) :
    (StmtIr.SAugAssign n op e) ≠ StmtIr.SAugAssign n op f := by
  intro he; cases he; exact h rfl
theorem sfieldaug_field_observable (f g op : String) (e : ε) (h : f ≠ g) :
    (StmtIr.SFieldAugAssign f op e) ≠ StmtIr.SFieldAugAssign g op e := by
  intro he; cases he; exact h rfl
theorem sarrayset_array_observable (a b i v : ε) (h : a ≠ b) :
    (StmtIr.SArraySet a i v) ≠ StmtIr.SArraySet b i v := by
  intro he; cases he; exact h rfl
theorem sarrayset_index_observable (a i j v : ε) (h : i ≠ j) :
    (StmtIr.SArraySet a i v) ≠ StmtIr.SArraySet a j v := by
  intro he; cases he; exact h rfl
theorem sarrayset_value_observable (a i v w : ε) (h : v ≠ w) :
    (StmtIr.SArraySet a i v) ≠ StmtIr.SArraySet a i w := by
  intro he; cases he; exact h rfl

/-- (c''') SUB-BODY non-vacuity: an SWhile with an EMPTY sub-body and one with a
    node are DISTINCT nodes (the sub-body is OBSERVABLE), and their sizes differ
    (the 0896 fixture's driver_refute / driver_evil_count at the ADT level). -/
theorem swhile_empty_neq_nonempty (t : ε) (h : StmtIr ε) (r : StmtList ε) :
    (StmtIr.SWhile t .SLNil) ≠ StmtIr.SWhile t (.SLCons h r) := by
  intro he; cases he
theorem swhile_size_grows_with_body (t : ε) (h : StmtIr ε) (r : StmtList ε) :
    sizeStmt (StmtIr.SWhile t .SLNil) < sizeStmt (StmtIr.SWhile t (.SLCons h r)) := by
  have := sizeStmt_pos h
  simp [sizeStmt, sizeSList]; omega

-- ===================================================================== --
-- STry + ExceptHandler + HandlerList observability (non-vacuity).        --
-- ===================================================================== --

theorem sizeHandler_pos (h : ExceptHandler ε) : sizeHandler h ≥ 1 := by
  cases h <;> simp [sizeHandler] <;> omega
theorem sizeTry_handlers_lt (b : StmtList ε) (hs : HandlerList ε) (oe fb : StmtList ε) :
    sizeHList hs < sizeStmt (StmtIr.STry b hs oe fb) := by
  simp [sizeStmt]; omega
theorem sizeTry_body_lt (b : StmtList ε) (hs : HandlerList ε) (oe fb : StmtList ε) :
    sizeSList b < sizeStmt (StmtIr.STry b hs oe fb) := by
  simp [sizeStmt]; omega
theorem sizeEhBody_lt_handler (x n : IrOptStr) (b : StmtList ε) :
    sizeSList b < sizeHandler (ExceptHandler.MkEH x n b) := by
  simp only [sizeHandler]; omega

theorem stmtKindOf_try (b : StmtList ε) (hs : HandlerList ε) (oe fb : StmtList ε) :
    stmtKindOf (StmtIr.STry b hs oe fb) = "Try" := rfl
theorem tag_try_neq_while (b : StmtList ε) (hs : HandlerList ε) (oe fb : StmtList ε)
    (t : ε) (c : StmtList ε) :
    stmtKindOf (StmtIr.STry b hs oe fb) ≠ stmtKindOf (StmtIr.SWhile t c) := by
  simp only [stmtKindOf]; decide

/-- The four STry children + the handler-list are INDEPENDENTLY observable. -/
theorem stry_handlers_observable (b : StmtList ε) (hs ks : HandlerList ε)
    (oe fb : StmtList ε) (h : hs ≠ ks) :
    (StmtIr.STry b hs oe fb) ≠ StmtIr.STry b ks oe fb := by
  intro he; cases he; exact h rfl
theorem stry_body_observable (b c : StmtList ε) (hs : HandlerList ε)
    (oe fb : StmtList ε) (h : b ≠ c) :
    (StmtIr.STry b hs oe fb) ≠ StmtIr.STry c hs oe fb := by
  intro he; cases he; exact h rfl
theorem stry_handlers_empty_neq_nonempty (b oe fb : StmtList ε)
    (h : ExceptHandler ε) (r : HandlerList ε) :
    (StmtIr.STry b .HLNil oe fb) ≠ StmtIr.STry b (.HLCons h r) oe fb := by
  intro he; cases he
theorem stry_size_grows_with_handlers (b oe fb : StmtList ε)
    (h : ExceptHandler ε) (r : HandlerList ε) :
    sizeStmt (StmtIr.STry b .HLNil oe fb)
      < sizeStmt (StmtIr.STry b (.HLCons h r) oe fb) := by
  have := sizeHandler_pos h
  simp [sizeStmt, sizeHList]; omega

/-- The ExceptHandler record's three slots are observable. -/
theorem eh_exc_type_observable (x y n : IrOptStr) (b : StmtList ε) (h : x ≠ y) :
    (ExceptHandler.MkEH x n b) ≠ (ExceptHandler.MkEH (ε := ε) y n b) := by
  intro he; cases he; exact h rfl
theorem eh_name_observable (x n m : IrOptStr) (b : StmtList ε) (h : n ≠ m) :
    (ExceptHandler.MkEH x n b) ≠ (ExceptHandler.MkEH (ε := ε) x m b) := by
  intro he; cases he; exact h rfl
theorem eh_body_observable (x n : IrOptStr) (b c : StmtList ε) (h : b ≠ c) :
    (ExceptHandler.MkEH x n b) ≠ ExceptHandler.MkEH x n c := by
  intro he; cases he; exact h rfl
theorem eh_exc_none_neq_some (s : String) (n : IrOptStr) (b : StmtList ε) :
    (ExceptHandler.MkEH .ISNone n b) ≠ (ExceptHandler.MkEH (ε := ε) (.ISSome s) n b) := by
  intro he; cases he

-- ===================================================================== --
-- SMatch + MatchCase + MatchCaseList observability (non-vacuity).         --
-- ===================================================================== --

theorem sizeMCase_pos (c : MatchCase ε) : sizeMCase c ≥ 1 := by
  cases c <;> simp [sizeMCase] <;> omega
theorem sizeMatch_cases_lt (s : ε) (cs : MatchCaseList ε) :
    sizeMCList cs < sizeStmt (StmtIr.SMatch s cs) := by
  simp only [sizeStmt]; omega
theorem sizeMCBody_lt_mcase (p : ε) (g : IrOpt ε) (b : StmtList ε) :
    sizeSList b < sizeMCase (MatchCase.MkMC p g b) := by
  simp only [sizeMCase]; omega

theorem stmtKindOf_match (s : ε) (cs : MatchCaseList ε) :
    stmtKindOf (StmtIr.SMatch s cs) = "Match" := rfl
theorem tag_match_neq_try (s : ε) (cs : MatchCaseList ε)
    (b : StmtList ε) (hs : HandlerList ε) (oe fb : StmtList ε) :
    stmtKindOf (StmtIr.SMatch s cs) ≠ stmtKindOf (StmtIr.STry b hs oe fb) := by
  simp only [stmtKindOf]; decide

theorem smatch_subject_observable (s u : ε) (cs : MatchCaseList ε) (h : s ≠ u) :
    (StmtIr.SMatch s cs) ≠ StmtIr.SMatch u cs := by
  intro he; cases he; exact h rfl
theorem smatch_cases_observable (s : ε) (cs ds : MatchCaseList ε) (h : cs ≠ ds) :
    (StmtIr.SMatch s cs) ≠ StmtIr.SMatch s ds := by
  intro he; cases he; exact h rfl
theorem smatch_cases_empty_neq_nonempty (s : ε) (c : MatchCase ε) (r : MatchCaseList ε) :
    (StmtIr.SMatch s .MCNil) ≠ StmtIr.SMatch s (.MCCons c r) := by
  intro he; cases he
theorem smatch_size_grows_with_cases (s : ε) (c : MatchCase ε) (r : MatchCaseList ε) :
    sizeStmt (StmtIr.SMatch s .MCNil) < sizeStmt (StmtIr.SMatch s (.MCCons c r)) := by
  have := sizeMCase_pos c
  simp [sizeStmt, sizeMCList]; omega

theorem mc_pattern_observable (p q : ε) (g : IrOpt ε) (b : StmtList ε) (h : p ≠ q) :
    (MatchCase.MkMC p g b) ≠ MatchCase.MkMC q g b := by
  intro he; cases he; exact h rfl
theorem mc_guard_observable (p : ε) (g k : IrOpt ε) (b : StmtList ε) (h : g ≠ k) :
    (MatchCase.MkMC p g b) ≠ MatchCase.MkMC p k b := by
  intro he; cases he; exact h rfl
theorem mc_body_observable (p : ε) (g : IrOpt ε) (b c : StmtList ε) (h : b ≠ c) :
    (MatchCase.MkMC p g b) ≠ MatchCase.MkMC p g c := by
  intro he; cases he; exact h rfl
theorem mc_guard_none_neq_some (p : ε) (e : ε) (b : StmtList ε) :
    (MatchCase.MkMC p .IrONone b) ≠ MatchCase.MkMC p (.IrOSome e) b := by
  intro he; cases he

-- ===================================================================== --
-- SDelSubscript observability (non-vacuity). FLAT node — size 1.          --
-- ===================================================================== --

theorem stmtKindOf_delsubscript (a i : ε) :
    stmtKindOf (StmtIr.SDelSubscript a i) = "DelSubscript" := rfl
theorem tag_delsubscript_neq_pass (a i : ε) :
    stmtKindOf (StmtIr.SDelSubscript a i) ≠ stmtKindOf (ε := ε) .SPass := by
  simp only [stmtKindOf]; decide
theorem size_delsubscript_flat (a i : ε) :
    sizeStmt (StmtIr.SDelSubscript a i) = 1 := rfl
theorem sdelsub_array_observable (a b i : ε) (h : a ≠ b) :
    (StmtIr.SDelSubscript a i) ≠ StmtIr.SDelSubscript b i := by
  intro he; cases he; exact h rfl
theorem sdelsub_index_observable (a i j : ε) (h : i ≠ j) :
    (StmtIr.SDelSubscript a i) ≠ StmtIr.SDelSubscript a j := by
  intro he; cases he; exact h rfl

-- ===================================================================== --
-- 5b. The CONCRETE Tuple-exc_type compaction — WhyML var_names_of /       --
--     join_pipe / tuple_exc_type. Modelled concretely so observability    --
--     is provable NON-vacuously (a length-only law would be vacuous).     --
-- ===================================================================== --

inductive CEmit where | CVar (id : String) | COther
def isVarc : CEmit → Bool | .CVar _ => true | .COther => false
def namec : CEmit → String | .CVar n => n | .COther => ""

inductive StrList where | SLNilS | SLConsS (h : String) (t : StrList)

def varNamesOf : List CEmit → StrList
  | [] => .SLNilS
  | e :: rest => if isVarc e then .SLConsS (namec e) (varNamesOf rest)
                 else varNamesOf rest

def joinPipe : StrList → String
  | .SLNilS => ""
  | .SLConsS h t => match t with
                    | .SLNilS => h
                    | .SLConsS _ _ => h ++ "|" ++ joinPipe t

def tupleExcType (l : List CEmit) : String := joinPipe (varNamesOf l)

theorem compaction_observe :
    tupleExcType [.CVar "A", .COther, .CVar "B"] = "A|B" := rfl
theorem compaction_single : tupleExcType [.CVar "X"] = "X" := rfl
theorem compaction_evil_twin :
    tupleExcType [.CVar "A", .COther, .CVar "B"] ≠ "A|C" := by decide
theorem compaction_drops_nonvar : tupleExcType [.COther, .COther] = "" := rfl

end StmtIRCert

-- ===================================================================== --
-- 6. VERDICT — axiom audit. Only the standard Lean kernel axioms may     --
--    appear; NO 4th, extension-specific axiom.                          --
-- ===================================================================== --

#print axioms StmtIRCert.sizeStmt_pos
#print axioms StmtIRCert.sizeSList_lt_swhile
#print axioms StmtIRCert.sizeBody_lt_sif
#print axioms StmtIRCert.sizeSList_lt_sfor
#print axioms StmtIRCert.abs_injective
#print axioms StmtIRCert.abs_surjective
#print axioms StmtIRCert.stmtKindOf_pass
#print axioms StmtIRCert.stmtKindOf_while
#print axioms StmtIRCert.stmtKindOf_if
#print axioms StmtIRCert.stmtKindOf_for
#print axioms StmtIRCert.kindOf_agree
#print axioms StmtIRCert.stmtKindOf_assign
#print axioms StmtIRCert.stmtKindOf_assert
#print axioms StmtIRCert.stmtKindOf_augassign
#print axioms StmtIRCert.stmtKindOf_fieldaugassign
#print axioms StmtIRCert.stmtKindOf_arrayset
#print axioms StmtIRCert.tag_augassign_neq_assign
#print axioms StmtIRCert.tag_augassign_neq_fieldaug
#print axioms StmtIRCert.tag_augassign_neq_arrayset
#print axioms StmtIRCert.tag_fieldaug_neq_arrayset
#print axioms StmtIRCert.saugassign_target_observable
#print axioms StmtIRCert.saugassign_op_observable
#print axioms StmtIRCert.saugassign_value_observable
#print axioms StmtIRCert.sfieldaug_field_observable
#print axioms StmtIRCert.sarrayset_array_observable
#print axioms StmtIRCert.sarrayset_index_observable
#print axioms StmtIRCert.sarrayset_value_observable
#print axioms StmtIRCert.tag_assign_neq_expr
#print axioms StmtIRCert.tag_assign_neq_return
#print axioms StmtIRCert.tag_assert_neq_expr
#print axioms StmtIRCert.tag_assert_neq_assign
#print axioms StmtIRCert.sassign_target_observable
#print axioms StmtIRCert.sassign_value_observable
#print axioms StmtIRCert.sassert_msg_none_neq_some
#print axioms StmtIRCert.sassert_msg_observable
#print axioms StmtIRCert.sassert_test_observable
#print axioms StmtIRCert.tag_pass_neq_break
#print axioms StmtIRCert.tag_while_neq_if
#print axioms StmtIRCert.tag_while_neq_for
#print axioms StmtIRCert.tag_if_neq_for
#print axioms StmtIRCert.ctor_pass_neq_break
#print axioms StmtIRCert.sreturn_none_neq_some
#print axioms StmtIRCert.swhile_empty_neq_nonempty
#print axioms StmtIRCert.swhile_size_grows_with_body
#print axioms StmtIRCert.sizeHandler_pos
#print axioms StmtIRCert.sizeTry_handlers_lt
#print axioms StmtIRCert.sizeTry_body_lt
#print axioms StmtIRCert.sizeEhBody_lt_handler
#print axioms StmtIRCert.stmtKindOf_try
#print axioms StmtIRCert.tag_try_neq_while
#print axioms StmtIRCert.stry_handlers_observable
#print axioms StmtIRCert.stry_body_observable
#print axioms StmtIRCert.stry_handlers_empty_neq_nonempty
#print axioms StmtIRCert.stry_size_grows_with_handlers
#print axioms StmtIRCert.eh_exc_type_observable
#print axioms StmtIRCert.eh_name_observable
#print axioms StmtIRCert.eh_body_observable
#print axioms StmtIRCert.eh_exc_none_neq_some
#print axioms StmtIRCert.compaction_observe
#print axioms StmtIRCert.compaction_single
#print axioms StmtIRCert.compaction_evil_twin
#print axioms StmtIRCert.compaction_drops_nonvar
#print axioms StmtIRCert.sizeMCase_pos
#print axioms StmtIRCert.sizeMatch_cases_lt
#print axioms StmtIRCert.sizeMCBody_lt_mcase
#print axioms StmtIRCert.stmtKindOf_match
#print axioms StmtIRCert.tag_match_neq_try
#print axioms StmtIRCert.smatch_subject_observable
#print axioms StmtIRCert.smatch_cases_observable
#print axioms StmtIRCert.smatch_cases_empty_neq_nonempty
#print axioms StmtIRCert.smatch_size_grows_with_cases
#print axioms StmtIRCert.mc_pattern_observable
#print axioms StmtIRCert.mc_guard_observable
#print axioms StmtIRCert.mc_body_observable
#print axioms StmtIRCert.mc_guard_none_neq_some
#print axioms StmtIRCert.stmtKindOf_delsubscript
#print axioms StmtIRCert.tag_delsubscript_neq_pass
#print axioms StmtIRCert.size_delsubscript_flat
#print axioms StmtIRCert.sdelsub_array_observable
#print axioms StmtIRCert.sdelsub_index_observable
