/-
  CslClause.lean — axiom-free certificate for the `csl_clause` contract-clause
  value shape (self-tcb-reduction, `_act_guard` conversion).  The Lean twin of
  `rocq/Phase2k_CslClause.v`.

  CO-LANDING COUPLING (the tier-3 / lesson-#5 rule, cf. PyAstStmt.lean /
  StmtIR.lean): the WhyML `csl_clause` theory promoted into the emitter preamble
  (`module6_whyml/preamble.py`, gated on the tight `_uses_act_guard` sentinel) is
  a NEW value shape — the contract-clause union an `Act`'s `.clauses` list
  carries, which `_act_guard` filters (`isinstance(cl, Given)`) and projects
  (`cl.expr`) over — so it lands with a proof, not a trusted assumption.
  DISJOINT from every other certified shape: the ctor prefix here is `C*`
  (`CGiven` — a contract clause) vs the `PS*`/`S*`/`Ir*` ast / stmt-ir / emit_ir
  prefixes.  Certified here, against pure inductive datatypes with NO axiom:

    (a) `CslClause` is a well-formed inductive carrying the FOREIGN emit_ir
        expr-child type `ε` (`.expr`, never mentions `CslClause` — no mutual
        recursion), with DECIDABLE equality given decidable equality on `ε`;
    (b) `clauseKindOf` is EXACT per ctor, tags pairwise DISTINCT;
    (c) the LOAD-BEARING faithfulness laws — the WhyML `is_K_faithful` lemmas:
        `isKNode s = true ↔ clauseKindOf s = "K"` for K ∈ {given, requires,
        ensures, assigns} — the ones that discharge in the WhyML whole-file
        proof, here certified to model the `isinstance(cl, Given)` dispatch
        faithfully;
    (d) the projector `clauseExprOf : CslClause → ε` is EXACT on the `.expr`
        slot every ctor carries (TOTAL — every clause wraps an expr), and the
        carried expr is OBSERVABLE (non-vacuity);
    (e) the clause list `ClauseList = ClNil | ClCons CslClause ClauseList` (the
        `act.clauses` iterated) has a WELL-FOUNDED length `clLen` and a TOTAL
        indexer `clNth`: the tail is STRICTLY shorter than the cons, so the WhyML
        `cl_nth`/`act_guard_fold` `variant { l }` structural recursion is
        certified to terminate.

  The abstract WhyML `val` `act_clauses_of` is NOT a `csl_clause` soundness
  obligation (an opaque reader of the `Act` node's `.clauses`) — modelled as a
  variable, TOTAL by typing, exactly as the WhyML leaves it.

  Verdict decided by `#print axioms` at the bottom: only standard Lean kernel
  axioms — or NONE — may appear; NO 4th, extension-specific axiom, so the
  3-axiom trust ledger stays intact.
-/

namespace CslClauseCert

variable {ε : Type}

-- ===================================================================== --
-- 1. The contract-clause ADT — mirrors the WhyML `type csl_clause`.      --
--    Each ctor wraps the clause's `.expr` — exactly the WhyML             --
--    `CGiven emit_ir | CRequires emit_ir | CEnsures emit_ir | CAssigns …`.--
-- ===================================================================== --

inductive CslClause (ε : Type) where
  | CGiven (e : ε)
  | CRequires (e : ε)
  | CEnsures (e : ε)
  | CAssigns (e : ε)
  deriving DecidableEq

/-- The tag discriminant — verbatim image of the WhyML `clause_kind_of`. -/
def clauseKindOf : CslClause ε → String
  | .CGiven _    => "Given"
  | .CRequires _ => "Requires"
  | .CEnsures _  => "Ensures"
  | .CAssigns _  => "Assigns"

/-- The isinstance discriminants — WhyML `is_K_node` predicates.  `isGivenNode`
    is the load-bearing one: `_act_guard` filters `isinstance(cl, Given)`. -/
def isGivenNode : CslClause ε → Bool
  | .CGiven _ => true | _ => false
def isRequiresNode : CslClause ε → Bool
  | .CRequires _ => true | _ => false
def isEnsuresNode : CslClause ε → Bool
  | .CEnsures _ => true | _ => false
def isAssignsNode : CslClause ε → Bool
  | .CAssigns _ => true | _ => false

/-- The projector — WhyML `clause_expr_of`.  TOTAL: every ctor carries an
    `.expr`, so no off-variant default. -/
def clauseExprOf : CslClause ε → ε
  | .CGiven e    => e
  | .CRequires e => e
  | .CEnsures e  => e
  | .CAssigns e  => e

-- ===================================================================== --
-- 2. (b) `clauseKindOf` EXACT per ctor + tags DISTINCT.                  --
-- ===================================================================== --

theorem kindOf_given (e : ε) : clauseKindOf (.CGiven e) = "Given" := rfl
theorem kindOf_requires (e : ε) : clauseKindOf (.CRequires e) = "Requires" := rfl
theorem kindOf_ensures (e : ε) : clauseKindOf (.CEnsures e) = "Ensures" := rfl
theorem kindOf_assigns (e : ε) : clauseKindOf (.CAssigns e) = "Assigns" := rfl

theorem tag_given_neq_requires (a b : ε) :
    clauseKindOf (.CGiven a) ≠ clauseKindOf (.CRequires b) := by
  simp only [clauseKindOf]; decide
theorem tag_given_neq_ensures (a b : ε) :
    clauseKindOf (.CGiven a) ≠ clauseKindOf (.CEnsures b) := by
  simp only [clauseKindOf]; decide
theorem tag_given_neq_assigns (a b : ε) :
    clauseKindOf (.CGiven a) ≠ clauseKindOf (.CAssigns b) := by
  simp only [clauseKindOf]; decide
theorem tag_requires_neq_ensures (a b : ε) :
    clauseKindOf (.CRequires a) ≠ clauseKindOf (.CEnsures b) := by
  simp only [clauseKindOf]; decide
theorem tag_requires_neq_assigns (a b : ε) :
    clauseKindOf (.CRequires a) ≠ clauseKindOf (.CAssigns b) := by
  simp only [clauseKindOf]; decide
theorem tag_ensures_neq_assigns (a b : ε) :
    clauseKindOf (.CEnsures a) ≠ clauseKindOf (.CAssigns b) := by
  simp only [clauseKindOf]; decide

-- ===================================================================== --
-- 3. (c) THE LOAD-BEARING faithfulness laws: isKNode s ↔ kind = "K".     --
-- ===================================================================== --

theorem is_given_faithful (s : CslClause ε) :
    isGivenNode s = true ↔ clauseKindOf s = "Given" := by
  cases s <;> simp [isGivenNode, clauseKindOf]
theorem is_requires_faithful (s : CslClause ε) :
    isRequiresNode s = true ↔ clauseKindOf s = "Requires" := by
  cases s <;> simp [isRequiresNode, clauseKindOf]
theorem is_ensures_faithful (s : CslClause ε) :
    isEnsuresNode s = true ↔ clauseKindOf s = "Ensures" := by
  cases s <;> simp [isEnsuresNode, clauseKindOf]
theorem is_assigns_faithful (s : CslClause ε) :
    isAssignsNode s = true ↔ clauseKindOf s = "Assigns" := by
  cases s <;> simp [isAssignsNode, clauseKindOf]

/-- The Given discriminant is MUTUALLY EXCLUSIVE with the others — the
    `_act_guard` filter is honest (a Given is not also a Requires/Ensures/
    Assigns). -/
theorem is_given_not_requires (s : CslClause ε) :
    isGivenNode s = true → isRequiresNode s = false := by
  cases s <;> simp [isGivenNode, isRequiresNode]
theorem is_given_not_ensures (s : CslClause ε) :
    isGivenNode s = true → isEnsuresNode s = false := by
  cases s <;> simp [isGivenNode, isEnsuresNode]
theorem is_given_not_assigns (s : CslClause ε) :
    isGivenNode s = true → isAssignsNode s = false := by
  cases s <;> simp [isGivenNode, isAssignsNode]

-- ===================================================================== --
-- 4. (d) Projector EXACT + every carried expr OBSERVABLE (non-vacuity).  --
-- ===================================================================== --

theorem exprOf_given (e : ε) : clauseExprOf (.CGiven e) = e := rfl
theorem exprOf_requires (e : ε) : clauseExprOf (.CRequires e) = e := rfl
theorem exprOf_ensures (e : ε) : clauseExprOf (.CEnsures e) = e := rfl
theorem exprOf_assigns (e : ε) : clauseExprOf (.CAssigns e) = e := rfl

theorem cgiven_expr_observable (e f : ε) (h : e ≠ f) :
    (CslClause.CGiven e) ≠ CslClause.CGiven f := by
  intro he; cases he; exact h rfl
theorem crequires_expr_observable (e f : ε) (h : e ≠ f) :
    (CslClause.CRequires e) ≠ CslClause.CRequires f := by
  intro he; cases he; exact h rfl
theorem censures_expr_observable (e f : ε) (h : e ≠ f) :
    (CslClause.CEnsures e) ≠ CslClause.CEnsures f := by
  intro he; cases he; exact h rfl
theorem cassigns_expr_observable (e f : ε) (h : e ≠ f) :
    (CslClause.CAssigns e) ≠ CslClause.CAssigns f := by
  intro he; cases he; exact h rfl
/-- A Given and a Requires carrying the SAME expr are still distinct clauses. -/
theorem cgiven_neq_crequires (e : ε) :
    (CslClause.CGiven e) ≠ CslClause.CRequires e := by
  intro he; cases he

-- ===================================================================== --
-- 5. (e) The clause list `ClauseList` — WELL-FOUNDED length + TOTAL      --
--    indexer (`clLen`/`clNth`; Nat length ⇒ well-founded automatically,  --
--    the faithful non-negative model of the WhyML `int` length).        --
-- ===================================================================== --

inductive ClauseList (ε : Type) where
  | ClNil
  | ClCons (h : CslClause ε) (t : ClauseList ε)

def clLen : ClauseList ε → Nat
  | .ClNil      => 0
  | .ClCons _ t => 1 + clLen t

/-- TOTAL indexer — WhyML `cl_nth` (default `CAssigns dflt` on nil/overshoot). -/
def clNth (dflt : ε) : Nat → ClauseList ε → CslClause ε
  | _,     .ClNil      => .CAssigns dflt
  | 0,     .ClCons h _ => h
  | n + 1, .ClCons _ t => clNth dflt n t

/-- Well-foundedness witness for the WhyML `variant { l }`: the TAIL is STRICTLY
    shorter than the cons that carries it — so `_act_guard`'s fold terminates. -/
theorem clLen_cons (h : CslClause ε) (t : ClauseList ε) :
    clLen (.ClCons h t) = 1 + clLen t := rfl
theorem clTail_len_lt (h : CslClause ε) (t : ClauseList ε) :
    clLen t < clLen (.ClCons h t) := by simp only [clLen]; omega

/-- Totality — observable behaviour of the total indexer. -/
theorem clNth_zero (d : ε) (h : CslClause ε) (t : ClauseList ε) :
    clNth d 0 (.ClCons h t) = h := rfl
theorem clNth_nil (d : ε) (i : Nat) : clNth d i (.ClNil : ClauseList ε) = .CAssigns d := by
  cases i <;> rfl
theorem clNth_succ (d : ε) (i : Nat) (h : CslClause ε) (t : ClauseList ε) :
    clNth d (i + 1) (.ClCons h t) = clNth d i t := rfl
theorem cl_empty_neq_nonempty (h : CslClause ε) (t : ClauseList ε) :
    (ClauseList.ClNil : ClauseList ε) ≠ ClauseList.ClCons h t := by intro he; cases he
theorem cl_len_grows_with_cons (h : CslClause ε) (t : ClauseList ε) :
    clLen t < clLen (.ClCons h t) := by simp only [clLen]; omega

-- ===================================================================== --
-- 6. The `_act_guard` fold itself — a certified reference model.  Filters --
--    `given` clauses, projects `.expr`, folds with a left-nested `and`.   --
--    Parameterised over the emit-level `and`-ctor + `True` literal (in    --
--    WhyML: `IrBinOp "and"` and `IrBoolC 1`).                             --
-- ===================================================================== --

section GuardFold
variable (irAnd : ε → ε → ε) (irTrue : ε)

/-- Accumulator carries `none` until the first `given` (`g = givens[0]`), then
    `some g`; each further given conjoins with `irAnd`. -/
def actGuardFold : Option ε → ClauseList ε → ε
  | acc,    .ClNil      => match acc with | none => irTrue | some g => g
  | acc,    .ClCons c rest =>
      if isGivenNode c then
        match acc with
        | none   => actGuardFold (some (clauseExprOf c)) rest
        | some g => actGuardFold (some (irAnd g (clauseExprOf c))) rest
      else actGuardFold acc rest

def actGuard (l : ClauseList ε) : ε := actGuardFold irAnd irTrue none l

theorem actGuard_empty : actGuard irAnd irTrue (.ClNil : ClauseList ε) = irTrue := rfl
theorem actGuard_no_given_single (e : ε) :
    actGuard irAnd irTrue (.ClCons (.CRequires e) .ClNil) = irTrue := rfl
theorem actGuard_one_given (e : ε) :
    actGuard irAnd irTrue (.ClCons (.CGiven e) .ClNil) = e := rfl
theorem actGuard_two_givens (e f : ε) :
    actGuard irAnd irTrue (.ClCons (.CGiven e) (.ClCons (.CGiven f) .ClNil)) = irAnd e f := rfl
theorem actGuard_skips_leading_nongiven (a e : ε) :
    actGuard irAnd irTrue (.ClCons (.CRequires a) (.ClCons (.CGiven e) .ClNil)) = e := rfl
theorem actGuard_skips_interleaved_nongiven (e a f : ε) :
    actGuard irAnd irTrue
      (.ClCons (.CGiven e) (.ClCons (.CEnsures a) (.ClCons (.CGiven f) .ClNil))) = irAnd e f := rfl
end GuardFold

end CslClauseCert

-- ===================================================================== --
-- 7. VERDICT — axiom audit. Only standard Lean kernel axioms may appear; --
--    NO 4th, extension-specific axiom — the 3-axiom ledger stays intact. --
-- ===================================================================== --

#print axioms CslClauseCert.kindOf_given
#print axioms CslClauseCert.kindOf_requires
#print axioms CslClauseCert.kindOf_ensures
#print axioms CslClauseCert.kindOf_assigns
#print axioms CslClauseCert.tag_given_neq_requires
#print axioms CslClauseCert.tag_given_neq_ensures
#print axioms CslClauseCert.tag_given_neq_assigns
#print axioms CslClauseCert.tag_requires_neq_ensures
#print axioms CslClauseCert.tag_requires_neq_assigns
#print axioms CslClauseCert.tag_ensures_neq_assigns
#print axioms CslClauseCert.is_given_faithful
#print axioms CslClauseCert.is_requires_faithful
#print axioms CslClauseCert.is_ensures_faithful
#print axioms CslClauseCert.is_assigns_faithful
#print axioms CslClauseCert.is_given_not_requires
#print axioms CslClauseCert.is_given_not_ensures
#print axioms CslClauseCert.is_given_not_assigns
#print axioms CslClauseCert.exprOf_given
#print axioms CslClauseCert.exprOf_requires
#print axioms CslClauseCert.exprOf_ensures
#print axioms CslClauseCert.exprOf_assigns
#print axioms CslClauseCert.cgiven_expr_observable
#print axioms CslClauseCert.crequires_expr_observable
#print axioms CslClauseCert.censures_expr_observable
#print axioms CslClauseCert.cassigns_expr_observable
#print axioms CslClauseCert.cgiven_neq_crequires
#print axioms CslClauseCert.clLen_cons
#print axioms CslClauseCert.clTail_len_lt
#print axioms CslClauseCert.clNth_zero
#print axioms CslClauseCert.clNth_nil
#print axioms CslClauseCert.clNth_succ
#print axioms CslClauseCert.cl_empty_neq_nonempty
#print axioms CslClauseCert.cl_len_grows_with_cons
#print axioms CslClauseCert.actGuard_empty
#print axioms CslClauseCert.actGuard_no_given_single
#print axioms CslClauseCert.actGuard_one_given
#print axioms CslClauseCert.actGuard_two_givens
#print axioms CslClauseCert.actGuard_skips_leading_nongiven
#print axioms CslClauseCert.actGuard_skips_interleaved_nongiven
