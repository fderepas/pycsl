/-
  CallKw.lean — axiom-free certificate for the `emit_ir` Call-internals value model
  (self-tcb-reduction, Tier-5 value-model wall, J1).  The Lean twin of
  `rocq/Phase2g_CallKw.v`.

  CO-LANDING COUPLING (the tier-3 rule, cf. PyAstStmt.lean / PyVal.lean): the WhyML
  keyword-node theory promoted into the emitter preamble
  (`module6_whyml/preamble.py::_emit_exprir_theory`, the standalone `kwval` /
  `keyword` / `keyword_list` types + the `IrCallKw` ctor + its projectors, gated on
  `_uses_call_kw`) is a NEW value shape — the faithful carrier for a Python Call
  node's `keywords` list, with the Name/Attribute distinction the bare-string callee
  currently COLLAPSES — so it lands with a proof, not a trusted assumption.  The
  Gate-R oracle (`getting-better/callinternals-oracle.mlw`, Z3-Valid, axiom-free)
  fixed the shape; certified here, against pure inductive datatypes with NO axiom:

    (a) `KeywordList` is a well-formed inductive: a BESPOKE cons-list (KWNil / KWCons),
        NOT a `Seq` (the Why3-rejected shape); `Kwval` is a LEAF-string variant
        (KwName / KwAttr) carrying no keyword, so KeywordList is standalone;
    (b) the measure `kwlistSize` is well-founded — `kwlistSize l ≥ 0` and the tail of
        a cons is STRICTLY shorter (the `for kw in call.keywords` termination witness);
    (c) the carriers are OBSERVABLE + DISTINCT — `KwName` / `KwAttr` injective and
        `KwName s ≠ KwAttr t`: the ast.Name(.id) vs ast.Attribute(.attr) distinction
        is NEVER collapsed;
    (d) the make-or-break bound-EXTRACTION is faithful — `extractBound` iterates the
        keyword list, matches `kw.arg = "bound"`, projects `.id` / `.attr` faithfully
        (the string VARIABLE reads back as `some v`, no int-erasure), a non-bound list
        reads `none`, the multi-element case iterates, and the EVIL TWIN (a wrong
        value) is provably UNprovable (non-vacuity).

  Verdict decided by `#print axioms` at the bottom: only the standard Lean kernel
  axioms (propext, Classical.choice, Quot.sound) may appear — NO 4th, extension-
  specific axiom — so the 3-axiom trust ledger stays intact.  Nothing is unproven.
-/

namespace CallKwCert

-- ===================================================================== --
-- 1. The keyword-node ADT — mirrors the WhyML types.                    --
-- ===================================================================== --

inductive Kwval where
  | KwName (s : String)
  | KwAttr (s : String)

structure Keyword where
  kwArg   : String
  kwValue : Kwval

inductive KeywordList where
  | KWNil
  | KWCons (k : Keyword) (t : KeywordList)

open Kwval KeywordList

-- (a)+(c) the discriminant + guarded projectors (is_kwname / kwname_id / kwattr_of).
def isKwName (v : Kwval) : Bool :=
  match v with | .KwName _ => true | .KwAttr _ => false

def kwnameId (v : Kwval) : String :=
  match v with | .KwName s => s | .KwAttr s => s
def kwattrOf (v : Kwval) : String :=
  match v with | .KwAttr s => s | .KwName s => s

-- ===================================================================== --
-- 2. (b) The keyword-list measure is well-founded.                       --
-- ===================================================================== --

def kwlistSize : KeywordList → Int
  | .KWNil      => 0
  | .KWCons _ t => 1 + kwlistSize t

theorem kwlistSize_nonneg : ∀ l : KeywordList, kwlistSize l ≥ 0
  | .KWNil      => by simp [kwlistSize]
  | .KWCons _ t => by have := kwlistSize_nonneg t; simp [kwlistSize]; omega

theorem kwlistSize_nil : kwlistSize .KWNil = 0 := by simp [kwlistSize]
theorem kwlistSize_cons (k : Keyword) (t : KeywordList) :
    kwlistSize (.KWCons k t) = 1 + kwlistSize t := by simp [kwlistSize]

-- The TAIL of a cons is STRICTLY shorter — the `for kw in call.keywords`
-- termination witness (the WhyML program `let rec` `variant { kws }`).
theorem kwlist_tail_size_lt (k : Keyword) (t : KeywordList) :
    kwlistSize t < kwlistSize (.KWCons k t) := by
  have := kwlistSize_nonneg t; simp [kwlistSize]; omega

-- ===================================================================== --
-- 3. (c) The carriers are OBSERVABLE + DISTINCT — the Name(.id) vs       --
--    Attribute(.attr) distinction is NEVER collapsed.                    --
-- ===================================================================== --

theorem kwname_inj (a b : String) : Kwval.KwName a = Kwval.KwName b → a = b := by
  intro h; injection h
theorem kwattr_inj (a b : String) : Kwval.KwAttr a = Kwval.KwAttr b → a = b := by
  intro h; injection h

-- THE make-or-break distinctness: a Name node is NEVER an Attribute node.
theorem kwname_neq_kwattr (s t : String) : Kwval.KwName s ≠ Kwval.KwAttr t := by
  intro c; injection c

theorem isKwName_name (s : String) : isKwName (.KwName s) = true := by simp [isKwName]
theorem isKwName_attr (s : String) : isKwName (.KwAttr s) = false := by simp [isKwName]
theorem kwnameId_name (s : String) : kwnameId (.KwName s) = s := by simp [kwnameId]
theorem kwattrOf_attr (s : String) : kwattrOf (.KwAttr s) = s := by simp [kwattrOf]

-- ===================================================================== --
-- 4. (d) The bound-EXTRACTION is faithful — the make-or-break.           --
-- ===================================================================== --

def extractBound : KeywordList → Option String
  | .KWNil        => none
  | .KWCons k rest =>
      if k.kwArg = "bound" then
        (if isKwName k.kwValue then some (kwnameId k.kwValue)
         else some (kwattrOf k.kwValue))
      else extractBound rest

-- G1: the Name arm projects `.id` FAITHFULLY — the string VARIABLE v reads back
-- as `some v`, NO int-erasure.
theorem extract_name_faithful (v : String) :
    extractBound (.KWCons { kwArg := "bound", kwValue := .KwName v } .KWNil) = some v := by
  simp [extractBound, isKwName, kwnameId]

-- G2: the Attribute arm projects `.attr` faithfully.
theorem extract_attr_faithful (a : String) :
    extractBound (.KWCons { kwArg := "bound", kwValue := .KwAttr a } .KWNil) = some a := by
  simp [extractBound, isKwName, kwattrOf]

-- G3: a keyword list with NO "bound" arg reads `none` (real discrimination).
theorem extract_no_bound_none (v : String) :
    extractBound (.KWCons { kwArg := "other", kwValue := .KwName v } .KWNil) = none := by
  simp [extractBound]

-- G4: the for-loop ACTUALLY iterates — "bound" found AFTER a non-bound head.
theorem extract_iterate_finds (v a : String) :
    extractBound
      (.KWCons { kwArg := "notit", kwValue := .KwAttr a }
        (.KWCons { kwArg := "bound", kwValue := .KwName v } .KWNil)) = some v := by
  simp [extractBound, isKwName, kwnameId]

-- G5 (EVIL TWIN): a WRONG projected value is provably UNprovable (non-vacuity).
theorem extract_evil_wrong_value (v : String) :
    v ≠ "wrong" →
    extractBound (.KWCons { kwArg := "bound", kwValue := .KwName v } .KWNil)
      ≠ some "wrong" := by
  intro h c; rw [extract_name_faithful] at c; apply h; injection c

-- G6: the model produces a SPECIFIC value distinguishable from a wrong constant.
theorem extract_concrete_discriminates :
    extractBound (.KWCons { kwArg := "bound", kwValue := .KwName "aaa" } .KWNil) = some "aaa"
    ∧ extractBound (.KWCons { kwArg := "bound", kwValue := .KwName "aaa" } .KWNil) ≠ some "bbb" := by
  refine ⟨by simp [extractBound, isKwName, kwnameId], ?_⟩
  rw [extract_name_faithful]; simp

end CallKwCert

-- ===================================================================== --
-- 5. VERDICT — axiom audit. Only the 3 standard Lean kernel axioms may   --
--    appear (propext, Classical.choice, Quot.sound); NO 4th axiom.       --
-- ===================================================================== --

#print axioms CallKwCert.kwlistSize_nonneg
#print axioms CallKwCert.kwlistSize_nil
#print axioms CallKwCert.kwlistSize_cons
#print axioms CallKwCert.kwlist_tail_size_lt
#print axioms CallKwCert.kwname_inj
#print axioms CallKwCert.kwattr_inj
#print axioms CallKwCert.kwname_neq_kwattr
#print axioms CallKwCert.isKwName_name
#print axioms CallKwCert.isKwName_attr
#print axioms CallKwCert.kwnameId_name
#print axioms CallKwCert.kwattrOf_attr
#print axioms CallKwCert.extract_name_faithful
#print axioms CallKwCert.extract_attr_faithful
#print axioms CallKwCert.extract_no_bound_none
#print axioms CallKwCert.extract_iterate_finds
#print axioms CallKwCert.extract_evil_wrong_value
#print axioms CallKwCert.extract_concrete_discriminates
