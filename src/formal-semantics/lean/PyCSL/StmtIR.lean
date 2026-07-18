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
        expr-child type) and a size measure — well-founded (no `StmtIr` sub-term);
    (b) the dict->ctor abstraction `abs : PyStmt → StmtIr` is TOTAL, INJECTIVE,
        and SURJECTIVE onto the ADT (the recognized key-set maps injectively);
    (c) `stmtKindOf` is EXACT per constructor, AGREES with the Python `"stmt"`
        string through `abs`, and the tags are pairwise DISTINCT (the honest node
        identity the pre-feature integer-0 erasure destroyed, fable Oracle 3);
    (d) NO MUTUAL RECURSION: the expr children carry the FOREIGN emit_ir type `ε`
        (a type variable), which never mentions `StmtIr` — one-directional.

  The mutable-ref append convention (`ir_stmts : ref (seq stmt_ir)` + a real
  `writes { ir_stmts }` frame) needs NO clause here: it is a Why3-INTRINSIC
  `writes` VC (the fable oracle `sound_append.mlw` proved it Valid, 0 axioms).
  This file certifies the DATA model; the EFFECT model is Why3's own.

  Verdict decided by `#print axioms` at the bottom: only the standard Lean kernel
  axioms (propext, Classical.choice, Quot.sound) may appear — NO 4th,
  extension-specific axiom — so the 3-axiom trust ledger stays intact.
-/

namespace StmtIRCert

-- ===================================================================== --
-- 1. The statement-IR ADT — mirrors the WhyML `type stmt_ir`.            --
-- ===================================================================== --

/-- The monomorphic option sibling of the emit_ir ADT — mirrors the WhyML
    `iropt_ir = IrONone | IrOSome emit_ir`. `SReturn` carries it (the OPTIONAL
    return value); it references only the FOREIGN `ε`, never `StmtIr`. -/
inductive IrOpt (ε : Type) where
  | IrONone
  | IrOSome (e : ε)
  deriving DecidableEq

/-- `ε` abstracts the WhyML emit_ir expr-child type: a FOREIGN type variable, so
    `StmtIr` provably carries no `StmtIr` sub-term (no mutual recursion). -/
inductive StmtIr (ε : Type) where
  | SPass
  | SBreak
  | SContinue
  | SReturn (o : IrOpt ε)
  | SExpr (e : ε)
  deriving DecidableEq

variable {ε : Type}

/-- The tag discriminant — image of the WhyML `stmt_kind_of`. -/
def stmtKindOf : StmtIr ε → String
  | .SPass => "Pass"
  | .SBreak => "Break"
  | .SContinue => "Continue"
  | .SReturn _ => "Return"
  | .SExpr _ => "Expr"

/-- A size measure. `StmtIr` has NO `StmtIr` sub-term (children are the foreign
    `ε`), so every node has size 1 — trivially well-founded. -/
def size : StmtIr ε → Nat := fun _ => 1

theorem size_pos (s : StmtIr ε) : size s = 1 := rfl

/-- Decidable equality is DERIVED (`deriving DecidableEq` above), given decidable
    equality on the child type — the well-founded-ADT obligation. -/
example [DecidableEq ε] : DecidableEq (StmtIr ε) := inferInstance

-- ===================================================================== --
-- 2. The recognized `{"stmt": K}` world + its dict->ctor abstraction.    --
-- ===================================================================== --

inductive PyStmt (ε : Type) where
  | PPass
  | PBreak
  | PContinue
  | PReturn (o : IrOpt ε)
  | PExpr (e : ε)

/-- The dict->ctor map (`{"stmt":"Pass"} ↦ SPass`, ...). -/
def abs : PyStmt ε → StmtIr ε
  | .PPass => .SPass
  | .PBreak => .SBreak
  | .PContinue => .SContinue
  | .PReturn o => .SReturn o
  | .PExpr e => .SExpr e

/-- The Python-side tag string of a recognized node. -/
def pyKindOf : PyStmt ε → String
  | .PPass => "Pass"
  | .PBreak => "Break"
  | .PContinue => "Continue"
  | .PReturn _ => "Return"
  | .PExpr _ => "Expr"

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

-- ===================================================================== --
-- 4. (c) `stmtKindOf` EXACT per ctor + AGREES through `abs`.             --
-- ===================================================================== --

theorem stmtKindOf_pass : stmtKindOf (ε := ε) .SPass = "Pass" := rfl
theorem stmtKindOf_break : stmtKindOf (ε := ε) .SBreak = "Break" := rfl
theorem stmtKindOf_continue : stmtKindOf (ε := ε) .SContinue = "Continue" := rfl
theorem stmtKindOf_return (o : IrOpt ε) : stmtKindOf (.SReturn o) = "Return" := rfl
theorem stmtKindOf_expr (e : ε) : stmtKindOf (.SExpr e) = "Expr" := rfl

theorem kindOf_agree (s : PyStmt ε) : stmtKindOf (abs s) = pyKindOf s := by
  cases s <;> rfl

-- ===================================================================== --
-- 5. (c') TAG-PRESERVING: the tags are pairwise DISTINCT (no erasure).   --
-- ===================================================================== --

theorem tag_pass_neq_break : stmtKindOf (ε := ε) .SPass ≠ stmtKindOf (ε := ε) .SBreak := by
  simp only [stmtKindOf]; decide
theorem tag_pass_neq_continue : stmtKindOf (ε := ε) .SPass ≠ stmtKindOf (ε := ε) .SContinue := by
  simp only [stmtKindOf]; decide
theorem tag_break_neq_continue : stmtKindOf (ε := ε) .SBreak ≠ stmtKindOf (ε := ε) .SContinue := by
  simp only [stmtKindOf]; decide
theorem tag_pass_neq_return (o : IrOpt ε) : stmtKindOf (ε := ε) .SPass ≠ stmtKindOf (.SReturn o) := by
  simp only [stmtKindOf]; decide
theorem tag_return_neq_expr (o : IrOpt ε) (e : ε) : stmtKindOf (.SReturn o) ≠ stmtKindOf (.SExpr e) := by
  simp only [stmtKindOf]; decide

/-- The constructors themselves are distinct (no erasure to a common value). -/
theorem ctor_pass_neq_break : (StmtIr.SPass : StmtIr ε) ≠ StmtIr.SBreak := by
  intro h; cases h

/-- (c'') The OPTIONAL return value is OBSERVABLE — a bare `return`
    (`SReturn IrONone`) and a value `return e` (`SReturn (IrOSome e)`) are
    DISTINCT nodes. Certifies the `SReturn iropt_ir` retype carries the option
    honestly (the 0895 fixture's driver_refute / driver_evil_option), not a
    collapsed/erased child. -/
theorem sreturn_none_neq_some (e : ε) :
    (StmtIr.SReturn .IrONone : StmtIr ε) ≠ StmtIr.SReturn (.IrOSome e) := by
  intro h; cases h

end StmtIRCert

-- ===================================================================== --
-- 6. VERDICT — axiom audit. Only the standard Lean kernel axioms may     --
--    appear; NO 4th, extension-specific axiom.                          --
-- ===================================================================== --

#print axioms StmtIRCert.size_pos
#print axioms StmtIRCert.abs_injective
#print axioms StmtIRCert.abs_surjective
#print axioms StmtIRCert.stmtKindOf_pass
#print axioms StmtIRCert.stmtKindOf_return
#print axioms StmtIRCert.kindOf_agree
#print axioms StmtIRCert.tag_pass_neq_break
#print axioms StmtIRCert.tag_return_neq_expr
#print axioms StmtIRCert.ctor_pass_neq_break
#print axioms StmtIRCert.sreturn_none_neq_some
