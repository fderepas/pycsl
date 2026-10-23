/-
  PyVal.lean — axiom-free certificate for the `hval` heterogeneous value model
  (self-tcb-reduction, Tier-5 value-model wall).  The Lean twin of
  `rocq/Phase2f_PyVal.v`.

  R3 CARRIER SWAP: the `HMap` arm's carrier is now an association LIST
  (`HPairs = PNil | PCons key hval HPairs`), NOT a `String → Option HVal` map.
  The map carrier was non-iterable, so `.values()` over a heterogeneous
  `Dict[str, Any]` could not fold; the assoc-list carrier makes `.values()` a
  terminating STRUCTURAL fold (its measure `size (.HMap p) = 1 + pairsSize p`
  DESCENDS into the pairs).

  CO-LANDING COUPLING (the tier-3 rule, cf. PyConstVal.lean / PyAstStmt.lean): the
  WhyML `hval` theory promoted into the emitter preamble
  (`module6_whyml/preamble.py::_emit_pyval_theory`, gated on `_uses_pyval`) is a NEW
  value shape — the faithful carrier for a heterogeneous Python `Dict[str, Any]`
  (HStr / HInt / HArr / HMap / HNode) — so it lands with a proof, not a trusted
  assumption.  Certified here, against pure inductive datatypes with NO axiom:

    (a) `HVal` is a well-formed MUTUAL inductive over THREE types: `HArr` recurses
        through the BESPOKE `HValList` (HNil / HCons) and `HMap` through the BESPOKE
        `HPairs` (PNil / PCons) — NOT a `Seq`/map (the Why3-rejected shape); the
        assoc list keeps the recursion structural;
    (b) the LOAD-BEARING measure `size` / `listSize` / `pairsSize` is well-founded —
        `size v ≥ 1` (the WhyML `size_pos`, needing MUTUAL structural induction over
        all three types; proven here), `listSize l ≥ 0`, `pairsSize p ≥ 0`, and the
        tail of a cons is STRICTLY shorter in BOTH carriers — so any `.values()`
        fold over `HPairs` terminates;
    (c) the value carriers are OBSERVABLE + DISTINCT — a string value is NEVER
        erased to an int (`HStr s ≠ HInt n`): the no-more-int faithfulness;
    (d) the make-or-break heterogeneous DICT read is faithful — over the assoc-list
        carrier `HPairs`, the `pairsGet` lookup fold reads a key's value back as
        `HStr arm_ctor` and the EVIL TWIN (a wrong value) is provably UNprovable
        (non-vacuity).

  `HVal` has no decidable equality (the emitter never needs it — reads are
  `pairsGet` key-projections) — so it is not claimed.

  Verdict decided by `#print axioms` at the bottom: only the standard Lean kernel
  axioms (propext, Classical.choice, Quot.sound) may appear — NO 4th,
  extension-specific axiom — so the 3-axiom trust ledger stays intact.  Nothing
  here is left unproven.
-/

namespace PyValCert

-- ===================================================================== --
-- 1. The heterogeneous value ADT — mirrors the WhyML `type hval`.       --
-- ===================================================================== --

mutual
inductive HVal where
  | HStr  (s : String)
  | HInt  (n : Int)
  | HArr  (l : HValList)
  | HMap  (p : HPairs)          -- R3: assoc-list carrier, not a map
  | HNode (v : HVal)
inductive HValList where
  | HNil
  | HCons (h : HVal) (t : HValList)
inductive HPairs where          -- R3: the NEW third mutually-recursive type
  | PNil
  | PCons (k : String) (v : HVal) (t : HPairs)
end

-- size / listSize / pairsSize — verbatim image of the WhyML cert-side measure.
-- The measure now DESCENDS into the map's pairs — `HMap` is no longer flat
-- weight-1 — which is exactly what makes `.values()` a terminating fold.
mutual
def size : HVal → Int
  | .HStr _  => 1
  | .HInt _  => 1
  | .HArr l  => 1 + listSize l
  | .HMap p  => 1 + pairsSize p   -- R3: was `=> 1`, flat
  | .HNode n => 1 + size n
def listSize : HValList → Int
  | .HNil      => 0
  | .HCons h t => size h + listSize t
def pairsSize : HPairs → Int      -- R3: NEW
  | .PNil        => 0
  | .PCons _ v t => size v + pairsSize t
end

-- ===================================================================== --
-- 2. (b) Well-foundedness: `size v ≥ 1` + `listSize l ≥ 0` + `pairsSize   --
--    p ≥ 0`, by MUTUAL structural induction over all three carriers.      --
-- ===================================================================== --

mutual
theorem size_pos : ∀ v : HVal, size v ≥ 1
  | .HStr _  => by simp [size]
  | .HInt _  => by simp [size]
  | .HArr l  => by have h := listSize_nonneg l; simp [size]; omega
  | .HMap p  => by have h := pairsSize_nonneg p; simp [size]; omega
  | .HNode n => by have h := size_pos n; simp [size]; omega
theorem listSize_nonneg : ∀ l : HValList, listSize l ≥ 0
  | .HNil      => by simp [listSize]
  | .HCons h t => by
      have h1 := size_pos h; have h2 := listSize_nonneg t; simp [listSize]; omega
theorem pairsSize_nonneg : ∀ p : HPairs, pairsSize p ≥ 0
  | .PNil        => by simp [pairsSize]
  | .PCons _ v t => by
      have h1 := size_pos v; have h2 := pairsSize_nonneg t; simp [pairsSize]; omega
end

theorem size_pstr  (s : String) : size (.HStr s) = 1 := by simp [size]
theorem size_pint  (n : Int)    : size (.HInt n) = 1 := by simp [size]
theorem size_pmap  (p : HPairs) : size (.HMap p) = 1 + pairsSize p := by simp [size]
theorem size_parr  (l : HValList) : size (.HArr l) = 1 + listSize l := by simp [size]
theorem size_pnode (n : HVal) : size (.HNode n) = 1 + size n := by simp [size]

theorem listSize_nil  : listSize .HNil = 0 := by simp [listSize]
theorem listSize_cons (h : HVal) (t : HValList) :
    listSize (.HCons h t) = size h + listSize t := by simp [listSize]
theorem pairsSize_nil  : pairsSize .PNil = 0 := by simp [pairsSize]
theorem pairsSize_cons (k : String) (v : HVal) (t : HPairs) :
    pairsSize (.PCons k v t) = size v + pairsSize t := by simp [pairsSize]

-- The TAIL of a cons is STRICTLY shorter — the termination witness for any
-- structural fold, in BOTH the list carrier AND the new pairs carrier (the WhyML
-- has no `variant` clause).  The pairs witness makes `.values()` folds terminate.
theorem list_tail_size_lt (h : HVal) (t : HValList) :
    listSize t < listSize (.HCons h t) := by
  have := size_pos h; simp [listSize]; omega
theorem pairs_tail_size_lt (k : String) (v : HVal) (t : HPairs) :
    pairsSize t < pairsSize (.PCons k v t) := by
  have := size_pos v; simp [pairsSize]; omega

-- ===================================================================== --
-- 3. (c) Value carriers are OBSERVABLE + DISTINCT — the no-more-int       --
--    faithfulness: a string stays a string, never erased to an int.       --
-- ===================================================================== --

theorem pstr_inj (a b : String) : HVal.HStr a = HVal.HStr b → a = b := by
  intro h; injection h
theorem pstr_neq (a b : String) : a ≠ b → HVal.HStr a ≠ HVal.HStr b := by
  intro h c; injection c with h'; exact h h'
theorem pint_inj (a b : Int) : HVal.HInt a = HVal.HInt b → a = b := by
  intro h; injection h

-- THE make-or-break distinctness: a HStr value is NEVER a HInt value.
theorem pstr_neq_pint (s : String) (n : Int) : HVal.HStr s ≠ HVal.HInt n := by
  intro c; injection c
theorem pstr_neq_parr (s : String) (l : HValList) : HVal.HStr s ≠ HVal.HArr l := by
  intro c; injection c
theorem parr_neq_pnode (l : HValList) (v : HVal) : HVal.HArr l ≠ HVal.HNode v := by
  intro c; injection c
theorem parr_inj (a b : HValList) : HVal.HArr a = HVal.HArr b → a = b := by
  intro h; injection h
theorem pmap_inj (a b : HPairs) : HVal.HMap a = HVal.HMap b → a = b := by
  intro h; injection h

-- ===================================================================== --
-- 4. (d) The heterogeneous DICT read is faithful — the make-or-break.     --
--    R3: over the assoc-list carrier `HPairs`, the read is the `pairsGet`  --
--    lookup FOLD; `pairsSet` PREPENDS a binding (`PCons`), as the emitter   --
--    `_build_dict_literal_map` builds the assoc list.                       --
-- ===================================================================== --

def pairsGet (p : HPairs) (k : String) : Option HVal :=
  match p with
  | .PNil => none
  | .PCons k' v t => if k = k' then some v else pairsGet t k

def pairsSet (p : HPairs) (k : String) (v : HVal) : HPairs := .PCons k v p

theorem read_same_key (p : HPairs) (k : String) (v : HVal) :
    pairsGet (pairsSet p k v) k = some v := by
  simp [pairsGet, pairsSet]

theorem read_other_key (p : HPairs) (k k' : String) (v : HVal) :
    k' ≠ k → pairsGet (pairsSet p k v) k' = pairsGet p k' := by
  intro h; simp [pairsGet, pairsSet, h]

-- The oracle's `read_variable_faithful`: build the
-- {"pattern": "Constructor", "ctor": arm_ctor, "captures": ["x"]} dict as an
-- assoc list and read "ctor" — the string VARIABLE arm_ctor projects back
-- FAITHFULLY.
def build (arm_ctor : String) : HPairs :=
  .PCons "pattern"  (.HStr "Constructor")
  (.PCons "ctor"    (.HStr arm_ctor)
  (.PCons "captures" (.HArr (.HCons (.HStr "x") .HNil))
  .PNil))

theorem read_variable_faithful (arm_ctor : String) :
    pairsGet (build arm_ctor) "ctor" = some (HVal.HStr arm_ctor) := by
  simp [build, pairsGet]

theorem read_literal_faithful (arm_ctor : String) :
    pairsGet (build arm_ctor) "pattern" = some (HVal.HStr "Constructor") := by
  simp [build, pairsGet]

theorem read_list_faithful (arm_ctor : String) :
    pairsGet (build arm_ctor) "captures"
      = some (HVal.HArr (.HCons (.HStr "x") .HNil)) := by
  simp [build, pairsGet]

-- EVIL TWIN (non-vacuity): a WRONG value read is provably UNprovable.
theorem read_evil_wrong_value (arm_ctor : String) :
    arm_ctor ≠ "wrong" →
    pairsGet (build arm_ctor) "ctor" ≠ some (HVal.HStr "wrong") := by
  intro h c
  rw [read_variable_faithful] at c
  apply h
  injection c with c'; injection c'

-- EVIL TWIN (empty-list refute): the bound key does NOT read `none`.
theorem read_evil_empty (arm_ctor : String) :
    pairsGet (build arm_ctor) "ctor" ≠ none := by
  rw [read_variable_faithful]; simp

-- An absent key reads `none` from the empty assoc list.
theorem read_missing_none (k : String) : pairsGet .PNil k = none := by
  simp [pairsGet]

end PyValCert

-- ===================================================================== --
-- 5. VERDICT — axiom audit. Only the 3 standard Lean kernel axioms may   --
--    appear (propext, Classical.choice, Quot.sound); NO 4th axiom.       --
-- ===================================================================== --

#print axioms PyValCert.size_pos
#print axioms PyValCert.listSize_nonneg
#print axioms PyValCert.pairsSize_nonneg
#print axioms PyValCert.size_pstr
#print axioms PyValCert.size_parr
#print axioms PyValCert.size_pmap
#print axioms PyValCert.size_pnode
#print axioms PyValCert.listSize_cons
#print axioms PyValCert.pairsSize_cons
#print axioms PyValCert.list_tail_size_lt
#print axioms PyValCert.pairs_tail_size_lt
#print axioms PyValCert.pstr_inj
#print axioms PyValCert.pstr_neq
#print axioms PyValCert.pint_inj
#print axioms PyValCert.pstr_neq_pint
#print axioms PyValCert.pstr_neq_parr
#print axioms PyValCert.parr_neq_pnode
#print axioms PyValCert.parr_inj
#print axioms PyValCert.pmap_inj
#print axioms PyValCert.read_same_key
#print axioms PyValCert.read_other_key
#print axioms PyValCert.read_variable_faithful
#print axioms PyValCert.read_literal_faithful
#print axioms PyValCert.read_list_faithful
#print axioms PyValCert.read_evil_wrong_value
#print axioms PyValCert.read_evil_empty
#print axioms PyValCert.read_missing_none
