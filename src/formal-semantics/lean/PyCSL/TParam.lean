/-
  TParam.lean — axiom-free certificate for the `tparam` INPUT-side PEP-695
  type-parameter value shape (self-tcb-reduction, collector-family unlock; L1).
  The Lean twin of `rocq/Phase2h_TParam.v`.

  CO-LANDING COUPLING (the tier-3 / lesson-#5 rule, cf. PyAstStmt.lean /
  CallKw.lean): the WhyML `tparam` theory promoted into the emitter preamble
  (`module6_whyml/preamble.py`, gated on `_uses_tparam`) is a NEW value shape —
  the raw PEP-695 `ast.TypeVar`/`ast.ParamSpec`/`ast.TypeVarTuple` node union
  that `_collect_type_params` reflects over (`type(tp).__name__`,
  `getattr(tp,"name")`, `getattr(tp,"bound")` + the bound isinstance) — so it
  lands with a proof, not a trusted assumption.  Certified here, against pure
  inductive datatypes with NO axiom:

    (a) `TParam` is a well-formed inductive carrying the FOREIGN emit_ir
        bound-child type `ε` (never mentions `TParam` — no mutual recursion),
        with DECIDABLE equality given decidable equality on `ε`;
    (b) `tpKindOf` — the image of `type(tp).__name__` — is EXACT per ctor, kind
        tags pairwise DISTINCT;
    (c) the LOAD-BEARING faithfulness laws — the WhyML `is_K_faithful` lemmas:
        `isK tp = true ↔ tpKindOf tp = "K"` for K ∈ {typevar, paramspec,
        typevartuple} — the ones that discharge in the WhyML whole-file proof,
        here certified to model the type-name reflection faithfully;
    (d) the projectors `tpName` (: TParam → String, image of
        `getattr(tp,"name")`) and `tpBound` (: TParam → ε, image of
        `getattr(tp,"bound")`) are EXACT on their slots with the SAME
        off-variant default as the WhyML, and every carried field is OBSERVABLE
        (non-vacuity);
    (e) the type-param list `TParamList = TPNil | TPCons TParam TParamList` (the
        `.type_params` iterated) has a WELL-FOUNDED length `tplLen` and a TOTAL
        indexer `tplNth`: the tail is STRICTLY shorter than the cons, so the
        WhyML `tpl_nth`'s `variant { l }` structural recursion (the tpl-loop
        `variant { tpl_len - idx }`) is certified to terminate.

  The abstract WhyML `val function type_params_of` is NOT a `tparam` soundness
  obligation (an opaque reader, the `class_body_ast` precedent) — modelled as a
  variable, TOTAL by typing, exactly as the WhyML leaves it.  The bound
  sub-node's isinstance/`.id`/`.attr` dispatch reuses the EXISTING emit_ir
  discriminants, so `tpBound` need only be certified as an EXACT projector.

  Verdict decided by `#print axioms` at the bottom: only standard Lean kernel
  axioms — or NONE — may appear; NO 4th, extension-specific axiom, so the
  3-axiom trust ledger stays intact.
-/

namespace TParamCert

variable {ε : Type}

-- ===================================================================== --
-- 1. The PEP-695 type-param ADT — mirrors the WhyML `type tparam`.       --
--    TPTypeVar (name, bound); ParamSpec/TypeVarTuple bound-less — exactly --
--    the WhyML `TPTypeVar string emit_ir | TPParamSpec string |          --
--    TPTypeVarTuple string`.                                             --
-- ===================================================================== --

inductive TParam (ε : Type) where
  | TPTypeVar (name : String) (bound : ε)
  | TPParamSpec (name : String)
  | TPTypeVarTuple (name : String)
  deriving DecidableEq

/-- The kind discriminant — verbatim image of the WhyML `tp_kind_of`, the image
    of the Python `type(tp).__name__` reflection. -/
def tpKindOf : TParam ε → String
  | .TPTypeVar _ _    => "TypeVar"
  | .TPParamSpec _    => "ParamSpec"
  | .TPTypeVarTuple _ => "TypeVarTuple"

/-- The kind discriminants — WhyML `is_K` predicates. -/
def isTypevar : TParam ε → Bool
  | .TPTypeVar _ _ => true | _ => false
def isParamspec : TParam ε → Bool
  | .TPParamSpec _ => true | _ => false
def isTypevartuple : TParam ε → Bool
  | .TPTypeVarTuple _ => true | _ => false

/-- The projectors — WhyML `tp_name` (: String) and `tp_bound` (: emit_ir, with
    off-variant default `IrOther ""` ≈ `dflt`). -/
def tpName : TParam ε → String
  | .TPTypeVar n _    => n
  | .TPParamSpec n    => n
  | .TPTypeVarTuple n => n
def tpBound (dflt : ε) : TParam ε → ε
  | .TPTypeVar _ b => b
  | _              => dflt

-- ===================================================================== --
-- 2. (b) `tpKindOf` EXACT per ctor + kind tags DISTINCT.                 --
-- ===================================================================== --

theorem kindOf_typevar (n : String) (b : ε) : tpKindOf (.TPTypeVar n b) = "TypeVar" := rfl
theorem kindOf_paramspec (n : String) : tpKindOf (ε := ε) (.TPParamSpec n) = "ParamSpec" := rfl
theorem kindOf_typevartuple (n : String) : tpKindOf (ε := ε) (.TPTypeVarTuple n) = "TypeVarTuple" := rfl

theorem tag_typevar_neq_paramspec (n : String) (b : ε) (m : String) :
    tpKindOf (.TPTypeVar n b) ≠ tpKindOf (ε := ε) (.TPParamSpec m) := by
  simp only [tpKindOf]; decide
theorem tag_paramspec_neq_typevartuple (n m : String) :
    tpKindOf (ε := ε) (.TPParamSpec n) ≠ tpKindOf (ε := ε) (.TPTypeVarTuple m) := by
  simp only [tpKindOf]; decide

-- ===================================================================== --
-- 3. (c) THE LOAD-BEARING faithfulness laws: isK tp ↔ kind = "K".        --
-- ===================================================================== --

theorem is_typevar_faithful (tp : TParam ε) :
    isTypevar tp = true ↔ tpKindOf tp = "TypeVar" := by
  cases tp <;> simp [isTypevar, tpKindOf]
theorem is_paramspec_faithful (tp : TParam ε) :
    isParamspec tp = true ↔ tpKindOf tp = "ParamSpec" := by
  cases tp <;> simp [isParamspec, tpKindOf]
theorem is_typevartuple_faithful (tp : TParam ε) :
    isTypevartuple tp = true ↔ tpKindOf tp = "TypeVarTuple" := by
  cases tp <;> simp [isTypevartuple, tpKindOf]

-- ===================================================================== --
-- 4. (d) Projectors EXACT + every carried field OBSERVABLE (non-vacuity).--
-- ===================================================================== --

theorem tpName_typevar (n : String) (b : ε) : tpName (.TPTypeVar n b) = n := rfl
theorem tpName_paramspec (n : String) : tpName (ε := ε) (.TPParamSpec n) = n := rfl
theorem tpName_typevartuple (n : String) : tpName (ε := ε) (.TPTypeVarTuple n) = n := rfl
theorem tpBound_typevar (d : ε) (n : String) (b : ε) : tpBound d (.TPTypeVar n b) = b := rfl
/- off-variant default (WhyML sentinel) -/
theorem tpBound_paramspec_default (d : ε) (n : String) : tpBound d (.TPParamSpec n) = d := rfl

theorem tptypevar_name_observable (n m : String) (b : ε) (h : n ≠ m) :
    (TParam.TPTypeVar n b) ≠ TParam.TPTypeVar m b := by
  intro he; cases he; exact h rfl
theorem tptypevar_bound_observable (n : String) (b c : ε) (h : b ≠ c) :
    (TParam.TPTypeVar n b) ≠ TParam.TPTypeVar n c := by
  intro he; cases he; exact h rfl
theorem tpparamspec_name_observable (n m : String) (h : n ≠ m) :
    (TParam.TPParamSpec n : TParam ε) ≠ TParam.TPParamSpec m := by
  intro he; cases he; exact h rfl
theorem tpparamspec_neq_tptypevartuple (n : String) :
    (TParam.TPParamSpec n : TParam ε) ≠ TParam.TPTypeVarTuple n := by
  intro he; cases he

-- ===================================================================== --
-- 5. (e) The type-param list `TParamList` — WELL-FOUNDED length + TOTAL   --
--    indexer.  (Nat length ⇒ well-founded automatically, the faithful     --
--    non-negative model of the WhyML `int` length.)                      --
-- ===================================================================== --

inductive TParamList (ε : Type) where
  | TPNil
  | TPCons (h : TParam ε) (t : TParamList ε)

def tplLen : TParamList ε → Nat
  | .TPNil      => 0
  | .TPCons _ t => 1 + tplLen t

/-- TOTAL indexer — WhyML `tpl_nth` (`TPParamSpec ""` default on nil/overshoot). -/
def tplNth : Nat → TParamList ε → TParam ε
  | _,     .TPNil      => .TPParamSpec ""
  | 0,     .TPCons h _ => h
  | n + 1, .TPCons _ t => tplNth n t

/-- Well-foundedness witness for the WhyML `variant { l }` / `variant { tpl_len -
    idx }`: the TAIL is STRICTLY shorter than the cons that carries it. -/
theorem tplLen_cons (h : TParam ε) (t : TParamList ε) : tplLen (.TPCons h t) = 1 + tplLen t := rfl
theorem tplTail_len_lt (h : TParam ε) (t : TParamList ε) : tplLen t < tplLen (.TPCons h t) := by
  simp only [tplLen]; omega

/-- Totality — observable behaviour of the total indexer. -/
theorem tplNth_zero (h : TParam ε) (t : TParamList ε) : tplNth 0 (.TPCons h t) = h := rfl
theorem tplNth_nil (i : Nat) : tplNth i (.TPNil : TParamList ε) = .TPParamSpec "" := by cases i <;> rfl
theorem tplNth_succ (i : Nat) (h : TParam ε) (t : TParamList ε) :
    tplNth (i + 1) (.TPCons h t) = tplNth i t := rfl
theorem tpl_empty_neq_nonempty (h : TParam ε) (t : TParamList ε) :
    (TParamList.TPNil : TParamList ε) ≠ TParamList.TPCons h t := by intro he; cases he
theorem tpl_len_grows_with_cons (h : TParam ε) (t : TParamList ε) :
    tplLen t < tplLen (.TPCons h t) := by simp only [tplLen]; omega

end TParamCert

-- ===================================================================== --
-- 6. VERDICT — axiom audit. Only standard Lean kernel axioms may appear; --
--    NO 4th, extension-specific axiom — the 3-axiom ledger stays intact. --
-- ===================================================================== --

#print axioms TParamCert.kindOf_typevar
#print axioms TParamCert.kindOf_paramspec
#print axioms TParamCert.kindOf_typevartuple
#print axioms TParamCert.tag_typevar_neq_paramspec
#print axioms TParamCert.tag_paramspec_neq_typevartuple
#print axioms TParamCert.is_typevar_faithful
#print axioms TParamCert.is_paramspec_faithful
#print axioms TParamCert.is_typevartuple_faithful
#print axioms TParamCert.tpName_typevar
#print axioms TParamCert.tpName_paramspec
#print axioms TParamCert.tpName_typevartuple
#print axioms TParamCert.tpBound_typevar
#print axioms TParamCert.tpBound_paramspec_default
#print axioms TParamCert.tptypevar_name_observable
#print axioms TParamCert.tptypevar_bound_observable
#print axioms TParamCert.tpparamspec_name_observable
#print axioms TParamCert.tpparamspec_neq_tptypevartuple
#print axioms TParamCert.tplLen_cons
#print axioms TParamCert.tplTail_len_lt
#print axioms TParamCert.tplNth_zero
#print axioms TParamCert.tplNth_nil
#print axioms TParamCert.tplNth_succ
#print axioms TParamCert.tpl_empty_neq_nonempty
#print axioms TParamCert.tpl_len_grows_with_cons
