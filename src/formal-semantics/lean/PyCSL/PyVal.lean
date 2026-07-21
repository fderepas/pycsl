/-
  PyVal.lean — axiom-free certificate for the `hval` heterogeneous value model
  (self-tcb-reduction, Tier-5 value-model wall).  The Lean twin of
  `rocq/Phase2f_PyVal.v`.

  CO-LANDING COUPLING (the tier-3 rule, cf. PyConstVal.lean / PyAstStmt.lean): the
  WhyML `hval` theory promoted into the emitter preamble
  (`module6_whyml/preamble.py::_emit_pyval_theory`, gated on `_uses_pyval`) is a NEW
  value shape — the faithful carrier for a heterogeneous Python `Dict[str, Any]`
  (HStr / HInt / HArr / HMap / HNode) — so it lands with a proof, not a trusted
  assumption.  Certified here, against pure inductive datatypes with NO axiom:

    (a) `HVal` is a well-formed (mutual) inductive: `HArr` recurses through the
        BESPOKE `HValList` (HNil / HCons), NOT a `Seq` (the Why3-rejected shape);
        `HMap` carries `String → Option HVal` with `HVal` in the POSITIVE arrow
        codomain (Lean's positivity checker accepts it, exactly as Why3 does);
    (b) the LOAD-BEARING measure `size` / `listSize` is well-founded — `size v ≥ 1`
        (the WhyML `size_pos`, needing MUTUAL structural induction; proven here),
        `listSize l ≥ 0`, and the tail of a cons is STRICTLY shorter;
    (c) the value carriers are OBSERVABLE + DISTINCT — a string value is NEVER
        erased to an int (`HStr s ≠ HInt n`): the no-more-int faithfulness;
    (d) the make-or-break heterogeneous DICT read is faithful — modelling the WhyML
        `map string (option hval)` as `String → Option HVal`, the string VARIABLE
        arm reads back as `HStr arm_ctor` and the EVIL TWIN (a wrong value) is
        provably UNprovable (non-vacuity).

  `HVal` has no decidable equality (the `HMap` functional field) — the emitter
  never needs it (reads are `Map.get` key-projections) — so it is not claimed.

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
  | HMap  (m : String → Option HVal)
  | HNode (v : HVal)
inductive HValList where
  | HNil
  | HCons (h : HVal) (t : HValList)
end

-- size / listSize — verbatim image of the WhyML cert-side measure.  HMap's map
-- has an INFINITE domain, so `size` counts the node only (documented deferral).
mutual
def size : HVal → Int
  | .HStr _  => 1
  | .HInt _  => 1
  | .HArr l  => 1 + listSize l
  | .HMap _  => 1
  | .HNode n => 1 + size n
def listSize : HValList → Int
  | .HNil      => 0
  | .HCons h t => size h + listSize t
end

-- ===================================================================== --
-- 2. (b) Well-foundedness: `size v ≥ 1` + `listSize l ≥ 0`, by MUTUAL     --
--    structural induction.                                                --
-- ===================================================================== --

mutual
theorem size_pos : ∀ v : HVal, size v ≥ 1
  | .HStr _  => by simp [size]
  | .HInt _  => by simp [size]
  | .HArr l  => by have h := listSize_nonneg l; simp [size]; omega
  | .HMap _  => by simp [size]
  | .HNode n => by have h := size_pos n; simp [size]; omega
theorem listSize_nonneg : ∀ l : HValList, listSize l ≥ 0
  | .HNil      => by simp [listSize]
  | .HCons h t => by
      have h1 := size_pos h; have h2 := listSize_nonneg t; simp [listSize]; omega
end

theorem size_pstr  (s : String) : size (.HStr s) = 1 := by simp [size]
theorem size_pint  (n : Int)    : size (.HInt n) = 1 := by simp [size]
theorem size_pmap  (m : String → Option HVal) : size (.HMap m) = 1 := by simp [size]
theorem size_parr  (l : HValList) : size (.HArr l) = 1 + listSize l := by simp [size]
theorem size_pnode (n : HVal) : size (.HNode n) = 1 + size n := by simp [size]

theorem listSize_nil  : listSize .HNil = 0 := by simp [listSize]
theorem listSize_cons (h : HVal) (t : HValList) :
    listSize (.HCons h t) = size h + listSize t := by simp [listSize]

-- The TAIL of a cons is STRICTLY shorter — the termination witness for any
-- structural fold over `HValList` (the WhyML has no `variant` clause).
theorem list_tail_size_lt (h : HVal) (t : HValList) :
    listSize t < listSize (.HCons h t) := by
  have := size_pos h; simp [listSize]; omega

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

-- ===================================================================== --
-- 4. (d) The heterogeneous DICT read is faithful — the make-or-break.     --
-- ===================================================================== --

def emptyMap : String → Option HVal := fun _ => none
def mapGet (m : String → Option HVal) (k : String) : Option HVal := m k
def mapSet (m : String → Option HVal) (k : String) (v : Option HVal) :
    String → Option HVal :=
  fun k' => if k = k' then v else m k'

theorem read_same_key (m : String → Option HVal) (k : String) (v : Option HVal) :
    mapGet (mapSet m k v) k = v := by
  simp [mapGet, mapSet]

theorem read_other_key (m : String → Option HVal) (k k' : String) (v : Option HVal) :
    k ≠ k' → mapGet (mapSet m k v) k' = mapGet m k' := by
  intro h; simp [mapGet, mapSet, h]

-- The oracle's `read_variable_faithful`: build the
-- {"pattern": "Constructor", "ctor": arm_ctor, "captures": ["x"]} dict and read
-- "ctor" — the string VARIABLE arm_ctor projects back FAITHFULLY.
def build (arm_ctor : String) : String → Option HVal :=
  mapSet
    (mapSet
      (mapSet emptyMap "pattern" (some (.HStr "Constructor")))
                       "ctor"    (some (.HStr arm_ctor)))
                       "captures" (some (.HArr (.HCons (.HStr "x") .HNil)))

theorem read_variable_faithful (arm_ctor : String) :
    mapGet (build arm_ctor) "ctor" = some (HVal.HStr arm_ctor) := by
  simp [build, mapGet, mapSet]

theorem read_literal_faithful (arm_ctor : String) :
    mapGet (build arm_ctor) "pattern" = some (HVal.HStr "Constructor") := by
  simp [build, mapGet, mapSet]

theorem read_list_faithful (arm_ctor : String) :
    mapGet (build arm_ctor) "captures"
      = some (HVal.HArr (.HCons (.HStr "x") .HNil)) := by
  simp [build, mapGet, mapSet]

-- EVIL TWIN (non-vacuity): a WRONG value read is provably UNprovable.
theorem read_evil_wrong_value (arm_ctor : String) :
    arm_ctor ≠ "wrong" →
    mapGet (build arm_ctor) "ctor" ≠ some (HVal.HStr "wrong") := by
  intro h c
  rw [read_variable_faithful] at c
  apply h
  injection c with c'; injection c'

-- EVIL TWIN (empty-map refute): the set key does NOT read `none`.
theorem read_evil_empty (arm_ctor : String) :
    mapGet (build arm_ctor) "ctor" ≠ none := by
  rw [read_variable_faithful]; simp

end PyValCert

-- ===================================================================== --
-- 5. VERDICT — axiom audit. Only the 3 standard Lean kernel axioms may   --
--    appear (propext, Classical.choice, Quot.sound); NO 4th axiom.       --
-- ===================================================================== --

#print axioms PyValCert.size_pos
#print axioms PyValCert.listSize_nonneg
#print axioms PyValCert.size_pstr
#print axioms PyValCert.size_parr
#print axioms PyValCert.size_pnode
#print axioms PyValCert.listSize_cons
#print axioms PyValCert.list_tail_size_lt
#print axioms PyValCert.pstr_inj
#print axioms PyValCert.pstr_neq
#print axioms PyValCert.pint_inj
#print axioms PyValCert.pstr_neq_pint
#print axioms PyValCert.pstr_neq_parr
#print axioms PyValCert.parr_neq_pnode
#print axioms PyValCert.parr_inj
#print axioms PyValCert.read_same_key
#print axioms PyValCert.read_other_key
#print axioms PyValCert.read_variable_faithful
#print axioms PyValCert.read_literal_faithful
#print axioms PyValCert.read_list_faithful
#print axioms PyValCert.read_evil_wrong_value
#print axioms PyValCert.read_evil_empty
