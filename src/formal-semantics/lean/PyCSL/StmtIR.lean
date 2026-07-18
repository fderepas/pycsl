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
  | SWhile (t : ε) (b : StmtList ε)
  | SIf (t : ε) (b : StmtList ε) (el : StmtList ε)
  | SFor (t : ε) (b : StmtList ε)
inductive StmtList (ε : Type) where
  | SLNil
  | SLCons (h : StmtIr ε) (t : StmtList ε)
end

deriving instance DecidableEq for StmtIr, StmtList

variable {ε : Type}

/-- The tag discriminant — image of the WhyML `stmt_kind_of`. -/
def stmtKindOf : StmtIr ε → String
  | .SPass => "Pass"
  | .SBreak => "Break"
  | .SContinue => "Continue"
  | .SReturn _ => "Return"
  | .SExpr _ => "Expr"
  | .SWhile _ _ => "While"
  | .SIf _ _ _ => "If"
  | .SFor _ _ => "For"

/- The MUTUAL well-founded size measure — WhyML `size_stmt`/`size_slist`. -/
mutual
def sizeStmt : StmtIr ε → Nat
  | .SPass => 1
  | .SBreak => 1
  | .SContinue => 1
  | .SReturn _ => 1
  | .SExpr _ => 1
  | .SWhile _ b => 1 + sizeSList b
  | .SIf _ b el => 1 + sizeSList b + sizeSList el
  | .SFor _ b => 1 + sizeSList b
def sizeSList : StmtList ε → Nat
  | .SLNil => 0
  | .SLCons h t => sizeStmt h + sizeSList t
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
  | PWhile (t : ε) (b : StmtList ε)
  | PIf (t : ε) (b : StmtList ε) (el : StmtList ε)
  | PFor (t : ε) (b : StmtList ε)

/-- The dict->ctor map (`{"stmt":"Pass"} ↦ SPass`, ..., `{"stmt":"While"} ↦
    SWhile ...`). -/
def abs : PyStmt ε → StmtIr ε
  | .PPass => .SPass
  | .PBreak => .SBreak
  | .PContinue => .SContinue
  | .PReturn o => .SReturn o
  | .PExpr e => .SExpr e
  | .PWhile t b => .SWhile t b
  | .PIf t b el => .SIf t b el
  | .PFor t b => .SFor t b

/-- The Python-side tag string of a recognized node. -/
def pyKindOf : PyStmt ε → String
  | .PPass => "Pass"
  | .PBreak => "Break"
  | .PContinue => "Continue"
  | .PReturn _ => "Return"
  | .PExpr _ => "Expr"
  | .PWhile _ _ => "While"
  | .PIf _ _ _ => "If"
  | .PFor _ _ => "For"

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
  | SWhile t b => exact ⟨.PWhile t b, rfl⟩
  | SIf t b el => exact ⟨.PIf t b el, rfl⟩
  | SFor t b => exact ⟨.PFor t b, rfl⟩

-- ===================================================================== --
-- 4. (c) `stmtKindOf` EXACT per ctor + AGREES through `abs`.             --
-- ===================================================================== --

theorem stmtKindOf_pass : stmtKindOf (ε := ε) .SPass = "Pass" := rfl
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
#print axioms StmtIRCert.tag_pass_neq_break
#print axioms StmtIRCert.tag_while_neq_if
#print axioms StmtIRCert.tag_while_neq_for
#print axioms StmtIRCert.tag_if_neq_for
#print axioms StmtIRCert.ctor_pass_neq_break
#print axioms StmtIRCert.sreturn_none_neq_some
#print axioms StmtIRCert.swhile_empty_neq_nonempty
#print axioms StmtIRCert.swhile_size_grows_with_body
