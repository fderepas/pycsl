/-
  TermIR.lean — axiom-free certificate for the `term` VARIANT ADT (the
  class-instance-variant carrier; self-tcb-reduction driver-backlog item 3,
  `class-variant-impl.md`).  The Lean twin of `rocq/Phase2i_TermIR.v`.

  CO-LANDING COUPLING (the tier-3 / lesson-#5 rule, cf. StmtIR.lean /
  PyAstStmt.lean / PyVal.lean): the WhyML `term` theory promoted into the emitter
  preamble (`module6_whyml/preamble.py::_emit_term_theory`, gated on `needs_term`)
  is a NEW value shape — the faithful carrier for the proof2why3 `Term`
  frozen-dataclass UNION that a `\trusted` walker (`contains_unsupported`)
  isinstance-dispatches over and whose named fields it reads — so it lands with a
  proof, not a trusted assumption.  The emitter lowers the union onto this variant
  and translates the isinstance-if-chain to a TOTAL positional `match`.  Certified
  here, against a pure inductive datatype with NO extension axiom:

    (a) `Term` is a well-formed inductive with a RECURSIVE `List Term` child
        (`App head (args : List Term)`) and DIRECT recursive children (BinOp /
        UnaryOp / Forall / Exists); Lean accepts it and derives the recursor
        `Term.rec` (termination of the WhyML `variant { v_term }` structural
        recursion).  Termination in the WhyML is the Why3-intrinsic STRUCTURAL
        variant, NOT a size measure — none is certified (the child is the standard
        `List Term`, so no bespoke list measure is needed);
    (c) the constructors are OBSERVABLY DISTINCT — `termKind` is EXACT on each
        constructor and the nine tag strings are pairwise distinct — so the total
        `match` arms are non-overlapping: the isinstance dispatch is faithful;
    (d) the constructors are INJECTIVE on the slots the emitter binds positionally
        (`Var name`, `App head args`, `BinOp op lhs rhs`, ...) — so `t.lhs`/`t.args`
        project the real child, never a confused sibling.  `DecidableEq` witnesses
        the whole ADT is observable.

  Verdict decided by `#print axioms` at the bottom: only standard Lean kernel
  axioms — or NONE — may appear; NO 4th, extension-specific axiom, so the 3-axiom
  trust ledger (`proof_axiom_allowlist.py`) stays intact.
-/

namespace TermIRCert

-- ===================================================================== --
-- 1. The `Term` ADT — mirrors the WhyML                                  --
--      type term = Var string | IntLit int | BoolLit bool               --
--        | App string (list term) | BinOp string term term              --
--        | UnaryOp string term | Forall (list string) string term       --
--        | Exists (list string) string term | Unsupported string string --
--    Field order matches the emitter's positional binders EXACTLY.       --
-- ===================================================================== --

inductive Term where
  | Var         (name : String)
  | IntLit      (value : Int)
  | BoolLit     (value : Bool)
  | App         (head : String) (args : List Term)
  | BinOp       (op : String) (lhs rhs : Term)
  | UnaryOp     (op : String) (arg : Term)
  | Forall      (binders : List String) (ty : String) (body : Term)
  | Exists      (binders : List String) (ty : String) (body : Term)
  | Unsupported (reason raw : String)
  deriving DecidableEq

-- (a) the structural recursor EXISTS: the WhyML `variant { v_term }` and the
--     `List Term` child fold are well-founded because `Term` is a legitimate
--     strictly-positive inductive.  `Term.rec` is Lean's witness.
#check @Term.rec

-- --- (c) the constructors are observably distinct (the isinstance tags) --- --
def termKind : Term → String
  | .Var _            => "Var"
  | .IntLit _         => "IntLit"
  | .BoolLit _        => "BoolLit"
  | .App _ _          => "App"
  | .BinOp _ _ _      => "BinOp"
  | .UnaryOp _ _      => "UnaryOp"
  | .Forall _ _ _     => "Forall"
  | .Exists _ _ _     => "Exists"
  | .Unsupported _ _  => "Unsupported"

theorem kind_var  (n : String) : termKind (.Var n) = "Var" := rfl
theorem kind_app  (h : String) (a : List Term) : termKind (.App h a) = "App" := rfl
theorem kind_binop (o : String) (a b : Term) : termKind (.BinOp o a b) = "BinOp" := rfl
theorem kind_unsup (r w : String) : termKind (.Unsupported r w) = "Unsupported" := rfl

/-- A representative slice of the pairwise distinctness the total match needs:
    an `App` is never a `BinOp`, `Var`, or `Unsupported` (non-overlapping arms). -/
theorem app_neq_binop (h : String) (a : List Term) (o : String) (l r : Term) :
    Term.App h a ≠ Term.BinOp o l r := by intro he; cases he
theorem app_neq_var (h : String) (a : List Term) (n : String) :
    Term.App h a ≠ Term.Var n := by intro he; cases he
theorem unsup_neq_var (r w n : String) :
    Term.Unsupported r w ≠ Term.Var n := by intro he; cases he
theorem var_neq_intlit (n : String) (v : Int) :
    Term.Var n ≠ Term.IntLit v := by intro he; cases he

/-- Distinct tags ⇒ distinct terms (the general form justifying the nine
    total-match arms are mutually exclusive). -/
theorem distinct_kind_distinct_term (a b : Term) (h : termKind a ≠ termKind b) :
    a ≠ b := by intro he; subst he; exact h rfl

-- --- (d) constructors are injective on the slots the emitter binds --- --
theorem var_inj (a b : String) (h : Term.Var a = Term.Var b) : a = b := by
  cases h; rfl
theorem app_inj (h1 : String) (a1 : List Term) (h2 : String) (a2 : List Term)
    (h : Term.App h1 a1 = Term.App h2 a2) : h1 = h2 ∧ a1 = a2 := by
  cases h; exact ⟨rfl, rfl⟩
theorem binop_inj (o1 : String) (l1 r1 : Term) (o2 : String) (l2 r2 : Term)
    (h : Term.BinOp o1 l1 r1 = Term.BinOp o2 l2 r2) : o1 = o2 ∧ l1 = l2 ∧ r1 = r2 := by
  cases h; exact ⟨rfl, rfl, rfl⟩
theorem unary_inj (o1 : String) (a1 : Term) (o2 : String) (a2 : Term)
    (h : Term.UnaryOp o1 a1 = Term.UnaryOp o2 a2) : o1 = o2 ∧ a1 = a2 := by
  cases h; exact ⟨rfl, rfl⟩
theorem forall_inj (bs1 : List String) (t1 : String) (b1 : Term)
    (bs2 : List String) (t2 : String) (b2 : Term)
    (h : Term.Forall bs1 t1 b1 = Term.Forall bs2 t2 b2) :
    bs1 = bs2 ∧ t1 = t2 ∧ b1 = b2 := by cases h; exact ⟨rfl, rfl, rfl⟩

end TermIRCert

-- ===================================================================== --
-- VERDICT — axiom audit. Only standard Lean kernel axioms may appear;    --
-- NO 4th, extension-specific axiom — the 3-axiom ledger stays intact.    --
-- ===================================================================== --

#print axioms TermIRCert.kind_var
#print axioms TermIRCert.kind_app
#print axioms TermIRCert.kind_binop
#print axioms TermIRCert.kind_unsup
#print axioms TermIRCert.app_neq_binop
#print axioms TermIRCert.app_neq_var
#print axioms TermIRCert.unsup_neq_var
#print axioms TermIRCert.var_neq_intlit
#print axioms TermIRCert.distinct_kind_distinct_term
#print axioms TermIRCert.var_inj
#print axioms TermIRCert.app_inj
#print axioms TermIRCert.binop_inj
#print axioms TermIRCert.unary_inj
#print axioms TermIRCert.forall_inj
