/-
  PyValR4.lean — axiom-free certificate for the FROZEN r4 mixed-value type `HVal` and its
  observable operations (wall dict-value-model-r4, Gate P step C, executor ce4).  The Lean
  twin of `rocq/Phase2m_PyValR4.v`, and the SUCCESSOR of `PyVal.lean` (left untouched).
  Companion WhyML: getting-better/dict-r4-theory.mlw (module DictR4Theory).  Every
  operation carries the WhyML name verbatim (snake_case), the same argument order, the same
  match structure and the same recursion / fold direction.  WhyML program `=` on
  bool / int / real / string is `if x then y else !y` / `decide (i = j)` / `F_eqb` /
  `hpairs_key_eq` (= `decide (a = b)`).

  THE REAL CARRIER: Lean core has no `Real` (no Mathlib in this lake project), and Lean's
  `Float` is IEEE (NaN, non-Leibniz `==`), so `HFloat` is over an abstract carrier `F`
  with the class `RealCarrier` holding exactly the laws the WhyML theory relies on, all true
  of Why3's `real` (`F_eqb_spec`: program equality; `from_int_inj`: stdlib
  `real.FromInt.Injective`; `hreal_int_of_some` / `_none`: the `val hreal_int_of` spec).
  `0.0` is `from_int 0` (FromInt.Zero), `1.0` is `from_int 1` (FromInt.One).  Every
  theorem quantifies over `[RealCarrier F]`, so it holds for every model; `ModelCF` at the
  end is a concrete instance (satisfiability).  The four law-free wrong-tag vals are the
  class `OpaqueArms`; every law holds for every instance.

  ROUTE (e2) (user decision log 848): the two WhyML axioms on `pairs_get` are realised by
  `pairs_get_nil` / `pairs_get_cons` below.

  Verdict: `#print axioms` at the bottom — only the allowlisted kernel axioms (propext,
  Classical.choice, Quot.sound) may appear; NO 4th axiom; no `sorry`.
-/

namespace PyValR4Cert

class RealCarrier (F : Type) where
  F_eqb : F → F → Bool
  F_eqb_spec : ∀ a b : F, F_eqb a b = true ↔ a = b
  from_int : Int → F
  from_int_inj : ∀ i j : Int, from_int i = from_int j → i = j
  hreal_int_of : F → Option Int
  hreal_int_of_some : ∀ f i, hreal_int_of f = some i → from_int i = f
  hreal_int_of_none : ∀ f, hreal_int_of f = none → ∀ i, from_int i ≠ f

open RealCarrier

-- ===================================================================== --
-- 1. The frozen 9-constructor mutual inductive.                          --
-- ===================================================================== --

mutual
inductive HVal (F : Type) where
  | HNone
  | HBool  (b : Bool)
  | HInt   (n : Int)
  | HFloat (f : F)
  | HStr   (s : String)
  | HTuple (l : HValList F)
  | HArr   (l : HValList F)
  | HMap   (p : HPairs F)
  | HNode  (v : HVal F)
inductive HValList (F : Type) where
  | HNil
  | HCons (h : HVal F) (t : HValList F)
inductive HPairs (F : Type) where
  | PNil
  | PCons (k : String) (v : HVal F) (t : HPairs F)
end

class OpaqueArms (F : Type) where
  hval_opaque_str : HVal F → String
  hval_opaque_int : HVal F → Int
  hval_len_other : HVal F → Int
  hval_tuple_other : HVal F → HVal F

open OpaqueArms

variable {F : Type}

def hpairs_key_eq (a b : String) : Bool := decide (a = b)

theorem key_refl (s : String) : hpairs_key_eq s s = true := by simp [hpairs_key_eq]
theorem hpairs_key_eq_spec (a b : String) : hpairs_key_eq a b = true ↔ a = b := by
  simp [hpairs_key_eq]

theorem hreal_int_of_from_int [RealCarrier F] (i : Int) :
    hreal_int_of (from_int i : F) = some i := by
  cases h : hreal_int_of (from_int i : F) with
  | some j =>
      have e := from_int_inj _ _ (hreal_int_of_some _ _ h)
      rw [e]
  | none => exact absurd rfl (hreal_int_of_none _ h i)

-- ===================================================================== --
-- 2. size / size_pos, injectivity, the 36 disequalities.                 --
-- ===================================================================== --

mutual
def size : HVal F → Int
  | .HNone => 1
  | .HBool _ => 1
  | .HInt _ => 1
  | .HFloat _ => 1
  | .HStr _ => 1
  | .HTuple l => 1 + list_size l
  | .HArr l => 1 + list_size l
  | .HMap p => 1 + pairs_size p
  | .HNode n => 1 + size n
def list_size : HValList F → Int
  | .HNil => 0
  | .HCons h t => size h + list_size t
def pairs_size : HPairs F → Int
  | .PNil => 0
  | .PCons _ v t => size v + pairs_size t
end

mutual
theorem size_pos : ∀ v : HVal F, size v ≥ 1
  | .HNone => by simp [size]
  | .HBool _ => by simp [size]
  | .HInt _ => by simp [size]
  | .HFloat _ => by simp [size]
  | .HStr _ => by simp [size]
  | .HTuple l => by have h := list_size_nonneg l; simp [size]; omega
  | .HArr l => by have h := list_size_nonneg l; simp [size]; omega
  | .HMap p => by have h := pairs_size_nonneg p; simp [size]; omega
  | .HNode n => by have h := size_pos n; simp [size]; omega
theorem list_size_nonneg : ∀ l : HValList F, list_size l ≥ 0
  | .HNil => by simp [list_size]
  | .HCons h t => by
      have h1 := size_pos h; have h2 := list_size_nonneg t; simp [list_size]; omega
theorem pairs_size_nonneg : ∀ p : HPairs F, pairs_size p ≥ 0
  | .PNil => by simp [pairs_size]
  | .PCons _ v t => by
      have h1 := size_pos v; have h2 := pairs_size_nonneg t; simp [pairs_size]; omega
end

theorem list_tail_size_lt (h : HVal F) (t : HValList F) :
    list_size t < list_size (.HCons h t) := by
  have := size_pos h; simp [list_size]; omega
theorem pairs_tail_size_lt (k : String) (v : HVal F) (t : HPairs F) :
    pairs_size t < pairs_size (.PCons k v t) := by
  have := size_pos v; simp [pairs_size]; omega
theorem size_sub_tuple (l : HValList F) : list_size l < size (.HTuple l) := by
  simp only [size]; omega
theorem size_sub_arr (l : HValList F) : list_size l < size (.HArr l) := by
  simp only [size]; omega
theorem size_sub_map (p : HPairs F) : pairs_size p < size (.HMap p) := by
  simp only [size]; omega
theorem size_sub_node (v : HVal F) : size v < size (.HNode v) := by
  simp only [size]; omega

theorem hbool_inj (a b : Bool) : (HVal.HBool a : HVal F) = .HBool b → a = b := by
  intro h; injection h
theorem hint_inj (a b : Int) : (HVal.HInt a : HVal F) = .HInt b → a = b := by
  intro h; injection h
theorem hfloat_inj (a b : F) : (HVal.HFloat a : HVal F) = .HFloat b → a = b := by
  intro h; injection h
theorem hstr_inj (a b : String) : (HVal.HStr a : HVal F) = .HStr b → a = b := by
  intro h; injection h
theorem htuple_inj (a b : HValList F) : HVal.HTuple a = .HTuple b → a = b := by
  intro h; injection h
theorem harr_inj (a b : HValList F) : HVal.HArr a = .HArr b → a = b := by
  intro h; injection h
theorem hmap_inj (a b : HPairs F) : HVal.HMap a = .HMap b → a = b := by
  intro h; injection h
theorem hnode_inj (a b : HVal F) : HVal.HNode a = .HNode b → a = b := by
  intro h; injection h
theorem hcons_inj (h h' : HVal F) (t t' : HValList F) :
    HValList.HCons h t = .HCons h' t' → h = h' ∧ t = t' := by
  intro e; injection e with e1 e2; exact ⟨e1, e2⟩
theorem pcons_inj (k k' : String) (v v' : HVal F) (t t' : HPairs F) :
    HPairs.PCons k v t = .PCons k' v' t' → k = k' ∧ v = v' ∧ t = t' := by
  intro e; injection e with e1 e2 e3; exact ⟨e1, e2, e3⟩
theorem hnil_neq_hcons (h : HVal F) (t : HValList F) : (HValList.HNil : HValList F) ≠ .HCons h t := by
  intro e; cases e
theorem pnil_neq_pcons (k : String) (v : HVal F) (t : HPairs F) : (HPairs.PNil : HPairs F) ≠ .PCons k v t := by
  intro e; cases e

-- the 36 pairwise constructor disequalities
theorem neq_none_bool (b2 : Bool) : (HVal.HNone : HVal F) ≠ HVal.HBool b2 := by intro h; cases h
theorem neq_none_int (n2 : Int) : (HVal.HNone : HVal F) ≠ HVal.HInt n2 := by intro h; cases h
theorem neq_none_float (f2 : F) : (HVal.HNone : HVal F) ≠ HVal.HFloat f2 := by intro h; cases h
theorem neq_none_str (s2 : String) : (HVal.HNone : HVal F) ≠ HVal.HStr s2 := by intro h; cases h
theorem neq_none_tuple (l2 : HValList F) : (HVal.HNone : HVal F) ≠ HVal.HTuple l2 := by intro h; cases h
theorem neq_none_arr (l2 : HValList F) : (HVal.HNone : HVal F) ≠ HVal.HArr l2 := by intro h; cases h
theorem neq_none_map (p2 : HPairs F) : (HVal.HNone : HVal F) ≠ HVal.HMap p2 := by intro h; cases h
theorem neq_none_node (v2 : HVal F) : (HVal.HNone : HVal F) ≠ HVal.HNode v2 := by intro h; cases h
theorem neq_bool_int (b1 : Bool) (n2 : Int) : (HVal.HBool b1 : HVal F) ≠ HVal.HInt n2 := by intro h; cases h
theorem neq_bool_float (b1 : Bool) (f2 : F) : (HVal.HBool b1 : HVal F) ≠ HVal.HFloat f2 := by intro h; cases h
theorem neq_bool_str (b1 : Bool) (s2 : String) : (HVal.HBool b1 : HVal F) ≠ HVal.HStr s2 := by intro h; cases h
theorem neq_bool_tuple (b1 : Bool) (l2 : HValList F) : (HVal.HBool b1 : HVal F) ≠ HVal.HTuple l2 := by intro h; cases h
theorem neq_bool_arr (b1 : Bool) (l2 : HValList F) : (HVal.HBool b1 : HVal F) ≠ HVal.HArr l2 := by intro h; cases h
theorem neq_bool_map (b1 : Bool) (p2 : HPairs F) : (HVal.HBool b1 : HVal F) ≠ HVal.HMap p2 := by intro h; cases h
theorem neq_bool_node (b1 : Bool) (v2 : HVal F) : (HVal.HBool b1 : HVal F) ≠ HVal.HNode v2 := by intro h; cases h
theorem neq_int_float (n1 : Int) (f2 : F) : (HVal.HInt n1 : HVal F) ≠ HVal.HFloat f2 := by intro h; cases h
theorem neq_int_str (n1 : Int) (s2 : String) : (HVal.HInt n1 : HVal F) ≠ HVal.HStr s2 := by intro h; cases h
theorem neq_int_tuple (n1 : Int) (l2 : HValList F) : (HVal.HInt n1 : HVal F) ≠ HVal.HTuple l2 := by intro h; cases h
theorem neq_int_arr (n1 : Int) (l2 : HValList F) : (HVal.HInt n1 : HVal F) ≠ HVal.HArr l2 := by intro h; cases h
theorem neq_int_map (n1 : Int) (p2 : HPairs F) : (HVal.HInt n1 : HVal F) ≠ HVal.HMap p2 := by intro h; cases h
theorem neq_int_node (n1 : Int) (v2 : HVal F) : (HVal.HInt n1 : HVal F) ≠ HVal.HNode v2 := by intro h; cases h
theorem neq_float_str (f1 : F) (s2 : String) : (HVal.HFloat f1 : HVal F) ≠ HVal.HStr s2 := by intro h; cases h
theorem neq_float_tuple (f1 : F) (l2 : HValList F) : (HVal.HFloat f1 : HVal F) ≠ HVal.HTuple l2 := by intro h; cases h
theorem neq_float_arr (f1 : F) (l2 : HValList F) : (HVal.HFloat f1 : HVal F) ≠ HVal.HArr l2 := by intro h; cases h
theorem neq_float_map (f1 : F) (p2 : HPairs F) : (HVal.HFloat f1 : HVal F) ≠ HVal.HMap p2 := by intro h; cases h
theorem neq_float_node (f1 : F) (v2 : HVal F) : (HVal.HFloat f1 : HVal F) ≠ HVal.HNode v2 := by intro h; cases h
theorem neq_str_tuple (s1 : String) (l2 : HValList F) : (HVal.HStr s1 : HVal F) ≠ HVal.HTuple l2 := by intro h; cases h
theorem neq_str_arr (s1 : String) (l2 : HValList F) : (HVal.HStr s1 : HVal F) ≠ HVal.HArr l2 := by intro h; cases h
theorem neq_str_map (s1 : String) (p2 : HPairs F) : (HVal.HStr s1 : HVal F) ≠ HVal.HMap p2 := by intro h; cases h
theorem neq_str_node (s1 : String) (v2 : HVal F) : (HVal.HStr s1 : HVal F) ≠ HVal.HNode v2 := by intro h; cases h
theorem neq_tuple_arr (l1 : HValList F) (l2 : HValList F) : (HVal.HTuple l1 : HVal F) ≠ HVal.HArr l2 := by intro h; cases h
theorem neq_tuple_map (l1 : HValList F) (p2 : HPairs F) : (HVal.HTuple l1 : HVal F) ≠ HVal.HMap p2 := by intro h; cases h
theorem neq_tuple_node (l1 : HValList F) (v2 : HVal F) : (HVal.HTuple l1 : HVal F) ≠ HVal.HNode v2 := by intro h; cases h
theorem neq_arr_map (l1 : HValList F) (p2 : HPairs F) : (HVal.HArr l1 : HVal F) ≠ HVal.HMap p2 := by intro h; cases h
theorem neq_arr_node (l1 : HValList F) (v2 : HVal F) : (HVal.HArr l1 : HVal F) ≠ HVal.HNode v2 := by intro h; cases h
theorem neq_map_node (p1 : HPairs F) (v2 : HVal F) : (HVal.HMap p1 : HVal F) ≠ HVal.HNode v2 := by intro h; cases h

-- ===================================================================== --
-- 3. The dict carrier.                                                   --
-- ===================================================================== --

def pairs_get : HPairs F → String → Option (HVal F)
  | .PNil, _ => none
  | .PCons k' v t, k => if hpairs_key_eq k k' then some v else pairs_get t k

-- route (e2): the two WhyML axioms, LITERALLY (`if k = k' then ..`).
theorem pairs_get_nil (k : String) : pairs_get (.PNil : HPairs F) k = none := by
  simp [pairs_get]
theorem pairs_get_cons (k k' : String) (v : HVal F) (t : HPairs F) :
    pairs_get (.PCons k' v t) k = (if k = k' then some v else pairs_get t k) := by
  simp [pairs_get, hpairs_key_eq]

-- verbatim the emitted pairs_set (preamble.py:8281-8287 at ca505a20c)
def pairs_set : HPairs F → String → HVal F → HPairs F
  | .PNil, k, v => .PCons k v .PNil
  | .PCons k' w t, k, v =>
      if hpairs_key_eq k k' then .PCons k' v t else .PCons k' w (pairs_set t k v)

def pairs_mem (p : HPairs F) (k : String) : Bool :=
  match pairs_get p k with
  | none => false
  | some _ => true

def hpairs_len : HPairs F → Int
  | .PNil => 0
  | .PCons _ _ t => 1 + hpairs_len t

def pairs_nodup : HPairs F → Bool
  | .PNil => true
  | .PCons k _ t => !(pairs_mem t k) && pairs_nodup t

def pairs_keys_in : HPairs F → HPairs F → Bool
  | .PNil, _ => true
  | .PCons k _ t, p => pairs_mem p k && pairs_keys_in t p

def hpairs_keys : HPairs F → HValList F
  | .PNil => .HNil
  | .PCons k _ t => .HCons (.HStr k) (hpairs_keys t)

theorem pairs_mem_iff (p : HPairs F) (k : String) :
    pairs_mem p k = true ↔ ∃ v, pairs_get p k = some v := by
  unfold pairs_mem; cases pairs_get p k <;> simp

theorem pairs_set_get : ∀ (p : HPairs F) (k : String) (v : HVal F) (j : String),
    pairs_get (pairs_set p k v) j = if hpairs_key_eq j k then some v else pairs_get p j
  | .PNil, k, v, j => by simp [pairs_set, pairs_get]
  | .PCons k' w t, k, v, j => by
      have ih := pairs_set_get t k v j
      by_cases h1 : k = k' <;> by_cases h2 : j = k' <;> by_cases h3 : j = k <;>
        simp_all [pairs_get, pairs_set, hpairs_key_eq]

theorem read_same_key (p : HPairs F) (k : String) (v : HVal F) :
    pairs_get (pairs_set p k v) k = some v := by
  rw [pairs_set_get]; simp [hpairs_key_eq]

theorem read_other_key (p : HPairs F) (k k' : String) (v : HVal F) :
    k' ≠ k → pairs_get (pairs_set p k v) k' = pairs_get p k' := by
  intro h; rw [pairs_set_get]; simp [hpairs_key_eq, h]

theorem mem_set (p : HPairs F) (k : String) (v : HVal F) (j : String) :
    pairs_mem (pairs_set p k v) j = (hpairs_key_eq j k || pairs_mem p j) := by
  unfold pairs_mem; rw [pairs_set_get]
  by_cases h : j = k <;> simp [hpairs_key_eq, h]

theorem nodup_preserved : ∀ (p : HPairs F) (k : String) (v : HVal F),
    pairs_nodup p = true → pairs_nodup (pairs_set p k v) = true
  | .PNil, k, v, _ => by simp [pairs_set, pairs_nodup, pairs_mem, pairs_get]
  | .PCons k' w t, k, v, h => by
      have ih := nodup_preserved t k v
      simp [pairs_nodup] at h
      by_cases h1 : k = k'
      · simp [pairs_set, hpairs_key_eq, h1, pairs_nodup, h.1, h.2]
      · have h2 : ¬ k' = k := fun e => h1 e.symm
        simp [pairs_set, hpairs_key_eq, h1, pairs_nodup, mem_set, h2, h.1, ih h.2]

theorem len_set : ∀ (p : HPairs F) (k : String) (v : HVal F),
    hpairs_len (pairs_set p k v) = if pairs_mem p k then hpairs_len p else hpairs_len p + 1
  | .PNil, k, v => by simp [pairs_set, hpairs_len, pairs_mem, pairs_get]
  | .PCons k' w t, k, v => by
      have ih := len_set t k v
      by_cases h1 : k = k'
      · simp [pairs_set, hpairs_key_eq, h1, hpairs_len, pairs_mem, pairs_get]
      · rw [show pairs_set (.PCons k' w t) k v = .PCons k' w (pairs_set t k v) by
              simp [pairs_set, hpairs_key_eq, h1]]
        rw [show pairs_mem (.PCons k' w t) k = pairs_mem t k by
              simp [pairs_mem, pairs_get, hpairs_key_eq, h1]]
        simp only [hpairs_len]; rw [ih]
        by_cases hm : pairs_mem t k = true <;> simp [hm] <;> omega

theorem hpairs_len_nonneg : ∀ p : HPairs F, hpairs_len p ≥ 0
  | .PNil => by simp [hpairs_len]
  | .PCons _ _ t => by have := hpairs_len_nonneg t; simp [hpairs_len]; omega

-- ---- the literal construction: a LEFT fold of pairs_set ----
def pairs_build : HPairs F → List (String × HVal F) → HPairs F
  | acc, [] => acc
  | acc, (k, v) :: t => pairs_build (pairs_set acc k v) t

def kv_last : List (String × HVal F) → String → Option (HVal F)
  | [], _ => none
  | (k', v) :: t, k =>
      match kv_last t k with
      | some w => some w
      | none => if hpairs_key_eq k k' then some v else none

theorem build_is_fold_left : ∀ (l : List (String × HVal F)) (acc : HPairs F),
    pairs_build acc l = l.foldl (fun p kv => pairs_set p kv.1 kv.2) acc
  | [], acc => by simp [pairs_build]
  | (k, v) :: t, acc => by simp [pairs_build, build_is_fold_left t]

theorem build_fold_read_back : ∀ (l : List (String × HVal F)) (acc : HPairs F) (k : String),
    pairs_get (pairs_build acc l) k
    = match kv_last l k with | some w => some w | none => pairs_get acc k
  | [], acc, k => by simp [pairs_build, kv_last]
  | (k', v) :: t, acc, k => by
      have ih := build_fold_read_back t (pairs_set acc k' v) k
      simp only [pairs_build, kv_last]
      rw [ih]
      cases kv_last t k with
      | some w => rfl
      | none =>
          rw [pairs_set_get]
          by_cases h : k = k' <;> simp [hpairs_key_eq, h]

theorem build_nodup : ∀ (l : List (String × HVal F)) (acc : HPairs F),
    pairs_nodup acc = true → pairs_nodup (pairs_build acc l) = true
  | [], acc, h => by simpa [pairs_build] using h
  | (k, v) :: t, acc, h => by
      simp only [pairs_build]; exact build_nodup t _ (nodup_preserved acc k v h)

theorem build_last_wins (a b : HVal F) :
    pairs_get (pairs_build .PNil [("a", a), ("a", b)]) "a" = some b := by
  simp [pairs_build, pairs_set, pairs_get, hpairs_key_eq]
theorem build_len_dup (a b : HVal F) :
    hpairs_len (pairs_build .PNil [("a", a), ("a", b)]) = 1 := by
  simp [pairs_build, pairs_set, hpairs_len, hpairs_key_eq]
theorem build_insertion_order (ka kb : String) (a b : HVal F) (h : kb ≠ ka) :
    pairs_build .PNil [(ka, a), (kb, b)] = .PCons ka a (.PCons kb b .PNil) := by
  simp [pairs_build, pairs_set, hpairs_key_eq, h]

-- ---- membership predicate and the lookup/nodup bridge ----
def InP : String → HVal F → HPairs F → Prop
  | _, _, .PNil => False
  | k, v, .PCons k' v' t => (k = k' ∧ v = v') ∨ InP k v t

theorem get_InP : ∀ (p : HPairs F) (k : String) (v : HVal F),
    pairs_get p k = some v → InP k v p
  | .PNil, k, v, h => by simp [pairs_get] at h
  | .PCons k' v' t, k, v, h => by
      by_cases e : k = k'
      · simp [pairs_get, hpairs_key_eq, e] at h
        simp [InP, e, h]
      · simp [pairs_get, hpairs_key_eq, e] at h
        simp only [InP]; exact Or.inr (get_InP t k v h)

theorem InP_mem : ∀ (p : HPairs F) (k : String) (v : HVal F), InP k v p → pairs_mem p k = true
  | .PNil, k, v, h => by simp [InP] at h
  | .PCons k' v' t, k, v, h => by
      have ih := InP_mem t k v
      by_cases e : k = k'
      · simp [pairs_mem, pairs_get, hpairs_key_eq, e]
      · simp only [InP] at h
        have h' : InP k v t := by
          rcases h with ⟨e1, _⟩ | h
          · exact absurd e1 e
          · exact h
        have := ih h'
        rw [show pairs_mem (.PCons k' v' t) k = pairs_mem t k by
              simp [pairs_mem, pairs_get, hpairs_key_eq, e]]
        exact this

theorem InP_get_nodup : ∀ (p : HPairs F) (k : String) (v : HVal F),
    pairs_nodup p = true → InP k v p → pairs_get p k = some v
  | .PNil, k, v, _, h => by simp [InP] at h
  | .PCons k' v' t, k, v, hn, h => by
      simp [pairs_nodup] at hn
      simp only [InP] at h
      rcases h with ⟨e1, e2⟩ | h
      · subst e1; subst e2; simp [pairs_get, hpairs_key_eq]
      · by_cases e : k = k'
        · subst e
          have := InP_mem t k v h
          simp_all
        · rw [show pairs_get (.PCons k' v' t) k = pairs_get t k by
                simp [pairs_get, hpairs_key_eq, e]]
          exact InP_get_nodup t k v hn.2 h

-- ===================================================================== --
-- 4. Python equality.                                                    --
-- ===================================================================== --

def hbool_int (b : Bool) : Int := if b then 1 else 0

mutual
def hval_eq [RealCarrier F] (a b : HVal F) : Bool :=
  match a with
  | .HNone => match b with
    | .HNone => true
    | _ => false
  | .HBool x => match b with
    | .HBool y => if x then y else !y
    | .HInt j => decide (hbool_int x = j)
    | .HFloat g => (match hreal_int_of g with | some j => decide (hbool_int x = j) | none => false)
    | _ => false
  | .HInt i => match b with
    | .HBool y => decide (i = hbool_int y)
    | .HInt j => decide (i = j)
    | .HFloat g => (match hreal_int_of g with | some j => decide (i = j) | none => false)
    | _ => false
  | .HFloat f => match b with
    | .HBool y => (match hreal_int_of f with | some i => decide (i = hbool_int y) | none => false)
    | .HInt j => (match hreal_int_of f with | some i => decide (i = j) | none => false)
    | .HFloat g => F_eqb f g
    | _ => false
  | .HStr s => match b with
    | .HStr t => hpairs_key_eq s t
    | _ => false
  | .HTuple l => match b with
    | .HTuple m => hlist_eq l m
    | _ => false
  | .HArr l => match b with
    | .HArr m => hlist_eq l m
    | _ => false
  | .HMap p => match b with
    | .HMap q => pairs_incl p q && pairs_keys_in q p
    | _ => false
  | .HNode x => match b with
    | .HNode y => hval_eq x y
    | _ => false
def hlist_eq [RealCarrier F] (l m : HValList F) : Bool :=
  match l with
  | .HNil => match m with
    | .HNil => true
    | _ => false
  | .HCons x t => match m with
    | .HCons y u => hval_eq x y && hlist_eq t u
    | _ => false
def pairs_incl [RealCarrier F] (p q : HPairs F) : Bool :=
  match p with
  | .PNil => true
  | .PCons k v t =>
      (match pairs_get q k with | some w => hval_eq v w | none => false) && pairs_incl t q
end

mutual
def hval_wf : HVal F → Bool
  | .HNone => true
  | .HBool _ => true
  | .HInt _ => true
  | .HFloat _ => true
  | .HStr _ => true
  | .HTuple l => hlist_wf l
  | .HArr l => hlist_wf l
  | .HMap p => pairs_nodup p && hpairs_wf p
  | .HNode x => hval_wf x
def hlist_wf : HValList F → Bool
  | .HNil => true
  | .HCons x t => hval_wf x && hlist_wf t
def hpairs_wf : HPairs F → Bool
  | .PNil => true
  | .PCons _ x t => hval_wf x && hpairs_wf t
end

theorem wf_InP : ∀ (p : HPairs F) (k : String) (v : HVal F),
    hpairs_wf p = true → InP k v p → hval_wf v = true
  | .PNil, _, _, _, h => by simp [InP] at h
  | .PCons k' v' t, k, v, hw, h => by
      simp [hpairs_wf] at hw
      simp only [InP] at h
      rcases h with ⟨_, e⟩ | h
      · rw [e]; exact hw.1
      · exact wf_InP t k v hw.2 h

theorem incl_spec [RealCarrier F] : ∀ (p q : HPairs F),
    pairs_incl p q = true ↔
    (∀ k v, InP k v p → ∃ w, pairs_get q k = some w ∧ hval_eq v w = true)
  | .PNil, q => by simp [pairs_incl, InP]
  | .PCons k v t, q => by
      have ih := incl_spec t q
      constructor
      · intro h k' v' hi
        simp only [pairs_incl, Bool.and_eq_true] at h
        simp only [InP] at hi
        rcases hi with ⟨e1, e2⟩ | hi
        · rw [e1, e2]
          cases hq : pairs_get q k with
          | some w => rw [hq] at h; exact ⟨w, rfl, h.1⟩
          | none => rw [hq] at h; simp at h
        · exact ih.1 h.2 k' v' hi
      · intro h
        simp only [pairs_incl, Bool.and_eq_true]
        refine ⟨?_, ih.2 (fun k' v' hi => h k' v' (by simp only [InP]; exact Or.inr hi))⟩
        obtain ⟨w, hw, he⟩ := h k v (by simp [InP])
        rw [hw]; exact he

theorem keys_in_spec : ∀ (q p : HPairs F),
    pairs_keys_in q p = true ↔ (∀ k v, InP k v q → pairs_mem p k = true)
  | .PNil, p => by simp [pairs_keys_in, InP]
  | .PCons k v t, p => by
      have ih := keys_in_spec t p
      constructor
      · intro h k' v' hi
        simp only [pairs_keys_in, Bool.and_eq_true] at h
        simp only [InP] at hi
        rcases hi with ⟨e1, _⟩ | hi
        · rw [e1]; exact h.1
        · exact ih.1 h.2 k' v' hi
      · intro h
        simp only [pairs_keys_in, Bool.and_eq_true]
        exact ⟨h k v (by simp [InP]),
               ih.2 (fun k' v' hi => h k' v' (by simp only [InP]; exact Or.inr hi))⟩

-- ---- reflexivity (well-formed values; HFloat carries no NaN) ----
mutual
theorem hval_eq_refl [RealCarrier F] : ∀ a : HVal F, hval_wf a = true → hval_eq a a = true
  | .HNone, _ => by simp [hval_eq]
  | .HBool b, _ => by cases b <;> simp [hval_eq]
  | .HInt n, _ => by simp [hval_eq]
  | .HFloat f, _ => by simp [hval_eq, (F_eqb_spec f f).2 rfl]
  | .HStr s, _ => by simp [hval_eq, hpairs_key_eq]
  | .HTuple l, h => by
      simp only [hval_eq]; exact hlist_eq_refl l (by simpa [hval_wf] using h)
  | .HArr l, h => by
      simp only [hval_eq]; exact hlist_eq_refl l (by simpa [hval_wf] using h)
  | .HMap p, h => by
      simp [hval_wf] at h
      simp only [hval_eq, Bool.and_eq_true]
      refine ⟨(incl_spec p p).2 ?_, (keys_in_spec p p).2 ?_⟩
      · intro k v hi
        exact ⟨v, InP_get_nodup p k v h.1 hi, pairs_refl p k v hi (wf_InP p k v h.2 hi)⟩
      · intro k v hi; exact InP_mem p k v hi
  | .HNode x, h => by
      simp only [hval_eq]; exact hval_eq_refl x (by simpa [hval_wf] using h)
theorem hlist_eq_refl [RealCarrier F] : ∀ l : HValList F, hlist_wf l = true → hlist_eq l l = true
  | .HNil, _ => by simp [hlist_eq]
  | .HCons x t, h => by
      simp [hlist_wf] at h
      simp only [hlist_eq, Bool.and_eq_true]
      exact ⟨hval_eq_refl x h.1, hlist_eq_refl t h.2⟩
theorem pairs_refl [RealCarrier F] : ∀ (p : HPairs F) (k : String) (v : HVal F),
    InP k v p → hval_wf v = true → hval_eq v v = true
  | .PNil, _, _, h, _ => by simp [InP] at h
  | .PCons k' v' t, k, v, h, hw => by
      simp only [InP] at h
      rcases h with ⟨_, e⟩ | h
      · rw [e] at hw ⊢; exact hval_eq_refl v' hw
      · exact pairs_refl t k v h hw
end

-- ---- the numeric tower is Python's: equality of the mathematical value ----
def hnum [RealCarrier F] : HVal F → Option F
  | .HNone => none
  | .HBool b => some (from_int (hbool_int b))
  | .HInt i => some (from_int i)
  | .HFloat f => some f
  | .HStr _ => none
  | .HTuple _ => none
  | .HArr _ => none
  | .HMap _ => none
  | .HNode _ => none

theorem zeq_from_int [RealCarrier F] (i j : Int) :
    decide (i = j) = true ↔ (from_int i : F) = from_int j := by
  constructor
  · intro h; have e : i = j := of_decide_eq_true h; rw [e]
  · intro h; exact decide_eq_true (from_int_inj _ _ h)

theorem int_float [RealCarrier F] (i : Int) (g : F) :
    (match hreal_int_of g with | some j => decide (i = j) | none => false) = true ↔
    from_int i = g := by
  cases hg : hreal_int_of g with
  | some j =>
      have e := hreal_int_of_some g j hg
      constructor
      · intro h; have e2 : i = j := of_decide_eq_true h; rw [e2]; exact e
      · intro h; exact decide_eq_true (from_int_inj _ _ (h.trans e.symm))
  | none =>
      constructor
      · intro h; exact absurd h (by simp)
      · intro h; exact absurd h (hreal_int_of_none g hg i)

theorem float_int [RealCarrier F] (f : F) (j : Int) :
    (match hreal_int_of f with | some i => decide (i = j) | none => false) = true ↔
    f = from_int j := by
  cases hf : hreal_int_of f with
  | some i =>
      have e := hreal_int_of_some f i hf
      constructor
      · intro h; have e2 : i = j := of_decide_eq_true h; rw [← e, e2]
      · intro h; exact decide_eq_true (from_int_inj _ _ (e.trans h))
  | none =>
      constructor
      · intro h; exact absurd h (by simp)
      · intro h; exact absurd h.symm (hreal_int_of_none f hf j)

theorem bool_bool [RealCarrier F] (x y : Bool) :
    (if x then y else !y) = true ↔ (from_int (hbool_int x) : F) = from_int (hbool_int y) := by
  cases x <;> cases y <;> simp [hbool_int] <;> intro h <;> have e := from_int_inj _ _ h <;> omega

theorem eq_numeric_tower [RealCarrier F] (a b : HVal F) (fa fb : F)
    (ha : hnum a = some fa) (hb : hnum b = some fb) :
    (hval_eq a b = true ↔ fa = fb) := by
  cases a <;> cases b <;> simp [hnum] at ha hb <;> subst ha <;> subst hb <;> simp only [hval_eq]
  all_goals first
    | exact zeq_from_int _ _ | exact int_float _ _ | exact float_int _ _
    | exact F_eqb_spec _ _ | exact bool_bool _ _

theorem num_sym [RealCarrier F] (a b : HVal F) (fa fb : F)
    (ha : hnum a = some fa) (hb : hnum b = some fb)
    (h : hval_eq a b = true) : hval_eq b a = true :=
  (eq_numeric_tower b a fb fa hb ha).2 ((eq_numeric_tower a b fa fb ha hb).1 h).symm

-- ---- symmetry (well-formed values) ----
mutual
theorem hval_eq_sym_true [RealCarrier F] : ∀ (a b : HVal F), hval_wf a = true →
    hval_wf b = true → hval_eq a b = true → hval_eq b a = true
  | .HNone, b, _, _, h => by cases b <;> simp_all [hval_eq]
  | .HBool x, b, _, _, h => by
      cases b with
      | HBool y => exact num_sym (.HBool x) (.HBool y) _ _ rfl rfl h
      | HInt j => exact num_sym (.HBool x) (.HInt j) _ _ rfl rfl h
      | HFloat g => exact num_sym (.HBool x) (.HFloat g) _ _ rfl rfl h
      | _ => simp [hval_eq] at h
  | .HInt i, b, _, _, h => by
      cases b with
      | HBool y => exact num_sym (.HInt i) (.HBool y) _ _ rfl rfl h
      | HInt j => exact num_sym (.HInt i) (.HInt j) _ _ rfl rfl h
      | HFloat g => exact num_sym (.HInt i) (.HFloat g) _ _ rfl rfl h
      | _ => simp [hval_eq] at h
  | .HFloat f, b, _, _, h => by
      cases b with
      | HBool y => exact num_sym (.HFloat f) (.HBool y) _ _ rfl rfl h
      | HInt j => exact num_sym (.HFloat f) (.HInt j) _ _ rfl rfl h
      | HFloat g => exact num_sym (.HFloat f) (.HFloat g) _ _ rfl rfl h
      | _ => simp [hval_eq] at h
  | .HStr s, b, _, _, h => by
      cases b with
      | HStr t => simp_all [hval_eq, hpairs_key_eq]
      | _ => simp [hval_eq] at h
  | .HTuple l, b, ha, hb, h => by
      cases b with
      | HTuple m =>
          simp only [hval_eq] at h ⊢
          exact hlist_eq_sym_true l m (by simpa [hval_wf] using ha) (by simpa [hval_wf] using hb) h
      | _ => simp [hval_eq] at h
  | .HArr l, b, ha, hb, h => by
      cases b with
      | HArr m =>
          simp only [hval_eq] at h ⊢
          exact hlist_eq_sym_true l m (by simpa [hval_wf] using ha) (by simpa [hval_wf] using hb) h
      | _ => simp [hval_eq] at h
  | .HMap p, b, ha, hb, h => by
      cases b with
      | HMap q =>
          simp [hval_wf] at ha hb
          simp only [hval_eq, Bool.and_eq_true] at h ⊢
          have hi := (incl_spec p q).1 h.1
          have hk := (keys_in_spec q p).1 h.2
          refine ⟨(incl_spec q p).2 ?_, (keys_in_spec p q).2 ?_⟩
          · intro k w hw
            obtain ⟨v, hv⟩ := (pairs_mem_iff p k).1 (hk k w hw)
            have hvIn := get_InP p k v hv
            obtain ⟨w', hw', heq⟩ := hi k v hvIn
            have hgq := InP_get_nodup q k w hb.1 hw
            rw [hgq] at hw'
            injection hw' with e
            rw [← e] at heq
            exact ⟨v, hv, pairs_sym p k v hvIn w (wf_InP p k v ha.2 hvIn) (wf_InP q k w hb.2 hw) heq⟩
          · intro k v hv
            obtain ⟨w, hw, _⟩ := hi k v hv
            exact (pairs_mem_iff q k).2 ⟨w, hw⟩
      | _ => simp [hval_eq] at h
  | .HNode x, b, ha, hb, h => by
      cases b with
      | HNode y =>
          simp only [hval_eq] at h ⊢
          exact hval_eq_sym_true x y (by simpa [hval_wf] using ha) (by simpa [hval_wf] using hb) h
      | _ => simp [hval_eq] at h
theorem hlist_eq_sym_true [RealCarrier F] : ∀ (l m : HValList F), hlist_wf l = true →
    hlist_wf m = true → hlist_eq l m = true → hlist_eq m l = true
  | .HNil, m, _, _, h => by cases m <;> simp_all [hlist_eq]
  | .HCons x t, m, hl, hm, h => by
      cases m with
      | HNil => simp [hlist_eq] at h
      | HCons y u =>
          simp [hlist_wf] at hl hm
          simp only [hlist_eq, Bool.and_eq_true] at h ⊢
          exact ⟨hval_eq_sym_true x y hl.1 hm.1 h.1, hlist_eq_sym_true t u hl.2 hm.2 h.2⟩
theorem pairs_sym [RealCarrier F] : ∀ (p : HPairs F) (k : String) (v : HVal F), InP k v p →
    ∀ b, hval_wf v = true → hval_wf b = true → hval_eq v b = true → hval_eq b v = true
  | .PNil, _, _, h, _, _, _, _ => by simp [InP] at h
  | .PCons k' v' t, k, v, h, b, hw, hbw, he => by
      simp only [InP] at h
      rcases h with ⟨_, e⟩ | h
      · rw [e] at hw he ⊢; exact hval_eq_sym_true v' b hw hbw he
      · exact pairs_sym t k v h b hw hbw he
end

theorem hval_eq_sym [RealCarrier F] (a b : HVal F) (ha : hval_wf a = true) (hb : hval_wf b = true) :
    hval_eq a b = hval_eq b a :=
  Bool.eq_iff_iff.2 ⟨hval_eq_sym_true a b ha hb, hval_eq_sym_true b a hb ha⟩

-- ---- dict equality depends on the lookups only: ORDER-INDEPENDENT ----
theorem eq_map_iff [RealCarrier F] (p q : HPairs F) (hn : pairs_nodup p = true) :
    hval_eq (.HMap p) (.HMap q) = true ↔
    (∀ k, pairs_mem p k = pairs_mem q k) ∧
    (∀ k v w, pairs_get p k = some v → pairs_get q k = some w → hval_eq v w = true) := by
  simp only [hval_eq, Bool.and_eq_true]
  rw [incl_spec, keys_in_spec]
  constructor
  · rintro ⟨hi, hk⟩
    refine ⟨fun k => ?_, fun k v w hv hw => ?_⟩
    · cases ep : pairs_mem p k <;> cases eqq : pairs_mem q k <;> try rfl
      · obtain ⟨w, hw⟩ := (pairs_mem_iff q k).1 eqq
        have := hk k w (get_InP q k w hw); rw [ep] at this; exact absurd this (by decide)
      · obtain ⟨v, hv⟩ := (pairs_mem_iff p k).1 ep
        obtain ⟨w, hw, _⟩ := hi k v (get_InP p k v hv)
        have := (pairs_mem_iff q k).2 ⟨w, hw⟩; rw [eqq] at this; exact absurd this (by decide)
    · obtain ⟨w', hw', e⟩ := hi k v (get_InP p k v hv)
      rw [hw] at hw'; injection hw' with e'; rw [e']; exact e
  · rintro ⟨hm, hv⟩
    refine ⟨fun k v hi => ?_, fun k w hi => ?_⟩
    · have hg := InP_get_nodup p k v hn hi
      have hq : pairs_mem q k = true := by rw [← hm]; exact (pairs_mem_iff p k).2 ⟨v, hg⟩
      obtain ⟨w, hw⟩ := (pairs_mem_iff q k).1 hq
      exact ⟨w, hw, hv k v w hg hw⟩
    · rw [hm]; exact InP_mem q k w hi

theorem eq_dict_order_independent [RealCarrier F] (p p' : HPairs F) (c : HVal F)
    (hp : pairs_nodup p = true) (hp' : pairs_nodup p' = true)
    (h : ∀ k, pairs_get p k = pairs_get p' k) :
    hval_eq (.HMap p) c = hval_eq (.HMap p') c := by
  have hm : ∀ k, pairs_mem p k = pairs_mem p' k := fun k => by simp only [pairs_mem, h k]
  cases c with
  | HMap q =>
      apply Bool.eq_iff_iff.2
      rw [eq_map_iff p q hp, eq_map_iff p' q hp']
      constructor
      · rintro ⟨A, B⟩
        exact ⟨fun k => (hm k).symm.trans (A k), fun k v w hv hw => B k v w ((h k).trans hv) hw⟩
      · rintro ⟨A, B⟩
        exact ⟨fun k => (hm k).trans (A k), fun k v w hv hw => B k v w ((h k).symm.trans hv) hw⟩
  | _ => simp [hval_eq]

-- ---- the cross-type equality table (Python ground truth) ----
theorem eq_true_one [RealCarrier F] : hval_eq (.HBool true) (.HInt 1 : HVal F) = true := by
  simp [hval_eq, hbool_int]
theorem eq_one_true [RealCarrier F] : hval_eq (.HInt 1) (.HBool true : HVal F) = true := by
  simp [hval_eq, hbool_int]
theorem eq_false_zero [RealCarrier F] : hval_eq (.HBool false) (.HInt 0 : HVal F) = true := by
  simp [hval_eq, hbool_int]
theorem eq_true_two [RealCarrier F] : hval_eq (.HBool true) (.HInt 2 : HVal F) = false := by
  simp [hval_eq, hbool_int]
theorem eq_one_onef [RealCarrier F] :
    hval_eq (.HInt 1) (.HFloat (from_int 1 : F)) = true := by
  simp [hval_eq, hreal_int_of_from_int]
theorem eq_onef_one [RealCarrier F] :
    hval_eq (.HFloat (from_int 1 : F)) (.HInt 1) = true := by
  simp [hval_eq, hreal_int_of_from_int]
theorem eq_true_onef [RealCarrier F] :
    hval_eq (.HBool true) (.HFloat (from_int 1 : F)) = true := by
  simp [hval_eq, hreal_int_of_from_int, hbool_int]
theorem eq_int_nonintegral [RealCarrier F] (i : Int) (g : F) (hg : hreal_int_of g = none) :
    hval_eq (.HInt i) (.HFloat g) = false := by
  simp [hval_eq, hg]
theorem eq_str_int [RealCarrier F] (s : String) (i : Int) :
    hval_eq (.HStr s) (.HInt i : HVal F) = false := by simp [hval_eq]
theorem eq_one_str_one [RealCarrier F] : hval_eq (.HStr "1") (.HInt 1 : HVal F) = false := by
  simp [hval_eq]
theorem eq_none_zero [RealCarrier F] : hval_eq .HNone (.HInt 0 : HVal F) = false := by
  simp [hval_eq]
theorem eq_none_false [RealCarrier F] : hval_eq .HNone (.HBool false : HVal F) = false := by
  simp [hval_eq]
theorem eq_none_none [RealCarrier F] : hval_eq .HNone (.HNone : HVal F) = true := by
  simp [hval_eq]
theorem eq_tuple_list [RealCarrier F] (l m : HValList F) : hval_eq (.HTuple l) (.HArr m) = false := by
  simp [hval_eq]
theorem eq_list_tuple [RealCarrier F] (l m : HValList F) : hval_eq (.HArr l) (.HTuple m) = false := by
  simp [hval_eq]
theorem eq_tuple1_list1 [RealCarrier F] :
    hval_eq (.HTuple (.HCons (.HInt 1) .HNil)) (.HArr (.HCons (.HInt 1) .HNil) : HVal F) = false := by
  simp [hval_eq]
theorem eq_dict_order [RealCarrier F] (ka kb : String) (x y : HVal F) (hab : ka ≠ kb)
    (hx : hval_wf x = true) (hy : hval_wf y = true) :
    hval_eq (.HMap (.PCons ka x (.PCons kb y .PNil))) (.HMap (.PCons kb y (.PCons ka x .PNil)))
    = true := by
  have hba : kb ≠ ka := fun e => hab e.symm
  simp [hval_eq, pairs_incl, pairs_keys_in, pairs_mem, pairs_get, hpairs_key_eq, hab, hba,
    hval_eq_refl x hx, hval_eq_refl y hy]


-- ---- one-level unfoldings of hval_eq at a LITERAL (the emitter inlines these RHS at
--      `v == <literal>`; statements match the WhyML lemmas hval_eq_*_lit) ----
theorem hval_eq_int_lit [RealCarrier F] (v : HVal F) (n : Int) :
    hval_eq v (.HInt n) =
    (match v with
     | .HInt i => decide (i = n)
     | .HBool b => decide (hbool_int b = n)
     | .HFloat f => (match hreal_int_of f with | some j => decide (j = n) | none => false)
     | _ => false) := by
  cases v <;> first | rfl | simp [hval_eq]

theorem hval_eq_bool_lit [RealCarrier F] (v : HVal F) (x : Bool) :
    hval_eq v (.HBool x) =
    (match v with
     | .HInt i => decide (i = hbool_int x)
     | .HBool b => decide (hbool_int b = hbool_int x)
     | .HFloat f => (match hreal_int_of f with | some j => decide (j = hbool_int x) | none => false)
     | _ => false) := by
  cases v with
  | HBool b => cases b <;> cases x <;> simp [hval_eq, hbool_int]
  | _ => first | rfl | simp [hval_eq]

theorem hval_eq_intfloat_lit [RealCarrier F] (v : HVal F) (n : Int) :
    hval_eq v (.HFloat (from_int n)) =
    (match v with
     | .HInt i => decide (i = n)
     | .HBool b => decide (hbool_int b = n)
     | .HFloat f => (match hreal_int_of f with | some j => decide (j = n) | none => false)
     | _ => false) := by
  cases v with
  | HFloat f =>
      exact Bool.eq_iff_iff.2 ((F_eqb_spec _ _).trans (float_int f n).symm)
  | _ => first | rfl | simp [hval_eq, hreal_int_of_from_int]

theorem hval_eq_float_lit [RealCarrier F] (v : HVal F) (c : F) (hc : hreal_int_of c = none) :
    hval_eq v (.HFloat c) = (match v with | .HFloat f => F_eqb f c | _ => false) := by
  cases v <;> first | rfl | simp [hval_eq, hc]

theorem hval_eq_none_lit [RealCarrier F] (v : HVal F) :
    hval_eq v .HNone = (match v with | .HNone => true | _ => false) := by
  cases v <;> first | rfl | simp [hval_eq]

theorem hval_eq_str_lit [RealCarrier F] (v : HVal F) (t : String) :
    hval_eq v (.HStr t) = (match v with | .HStr s => hpairs_key_eq s t | _ => false) := by
  cases v <;> first | rfl | simp [hval_eq]

-- ===================================================================== --
-- 5. Key canonicalisation and hashability.                               --
-- ===================================================================== --

mutual
def hval_canon [RealCarrier F] : HVal F → HVal F
  | .HNone => .HNone
  | .HBool b => .HInt (hbool_int b)
  | .HInt i => .HInt i
  | .HFloat f => (match hreal_int_of f with | some i => .HInt i | none => .HFloat f)
  | .HStr s => .HStr s
  | .HTuple l => .HTuple (hlist_canon l)
  | .HArr l => .HArr l
  | .HMap p => .HMap p
  | .HNode x => .HNode x
def hlist_canon [RealCarrier F] : HValList F → HValList F
  | .HNil => .HNil
  | .HCons x t => .HCons (hval_canon x) (hlist_canon t)
end

mutual
def hval_hashable : HVal F → Bool
  | .HNone => true
  | .HBool _ => true
  | .HInt _ => true
  | .HFloat _ => true
  | .HStr _ => true
  | .HTuple l => hlist_hashable l
  | .HArr _ => false
  | .HMap _ => false
  | .HNode _ => false
def hlist_hashable : HValList F → Bool
  | .HNil => true
  | .HCons x t => hval_hashable x && hlist_hashable t
end

theorem float_canon [RealCarrier F] (f g : F) :
    F_eqb f g = true ↔
    ((match hreal_int_of f with | some i => HVal.HInt i | none => HVal.HFloat f) =
     (match hreal_int_of g with | some i => HVal.HInt i | none => HVal.HFloat g)) := by
  rw [F_eqb_spec]
  cases hf : hreal_int_of f with
  | some i =>
    cases hg : hreal_int_of g with
    | some j =>
      have ef := hreal_int_of_some f i hf
      have eg := hreal_int_of_some g j hg
      constructor
      · intro h; have e : i = j := from_int_inj _ _ (ef.trans (h.trans eg.symm)); rw [e]
      · intro h; injection h with e; rw [← ef, ← eg, e]
    | none =>
      have ef := hreal_int_of_some f i hf
      constructor
      · intro h; exact absurd (ef.trans h) (hreal_int_of_none g hg i)
      · intro h; cases h
  | none =>
    cases hg : hreal_int_of g with
    | some j =>
      have eg := hreal_int_of_some g j hg
      constructor
      · intro h; exact absurd (eg.trans h.symm) (hreal_int_of_none f hf j)
      · intro h; cases h
    | none =>
      constructor
      · intro h; rw [h]
      · intro h; injection h with e

mutual
theorem eq_canon_coherent [RealCarrier F] : ∀ (a b : HVal F), hval_hashable a = true →
    hval_hashable b = true → (hval_eq a b = true ↔ hval_canon a = hval_canon b)
  | .HNone, b, _, hb => by
      cases b <;> first
        | (simp [hval_hashable] at hb; done)
        | (simp only [hval_eq, hval_canon] <;> simp [hpairs_key_eq]; done)
        | (simp only [hval_eq, hval_canon] <;> split <;> simp_all; done)
  | .HBool x, b, _, hb => by
      cases b <;> first
        | (simp [hval_hashable] at hb; done)
        | (simp only [hval_eq, hval_canon]; rename_i y; cases x <;> cases y <;> simp [hbool_int]; done)
        | (simp only [hval_eq, hval_canon] <;> simp [hpairs_key_eq]; done)
        | (simp only [hval_eq, hval_canon] <;> split <;> simp_all; done)
  | .HInt i, b, _, hb => by
      cases b <;> first
        | (simp [hval_hashable] at hb; done)
        | (simp only [hval_eq, hval_canon] <;> simp [hpairs_key_eq]; done)
        | (simp only [hval_eq, hval_canon] <;> split <;> simp_all; done)
  | .HFloat f, b, _, hb => by
      cases b <;> first
        | (simp [hval_hashable] at hb; done)
        | (simp only [hval_eq, hval_canon]; exact float_canon _ _)
        | (simp only [hval_eq, hval_canon] <;> simp [hpairs_key_eq]; done)
        | (simp only [hval_eq, hval_canon] <;> split <;> simp_all; done)
  | .HStr s, b, _, hb => by
      cases b <;> first
        | (simp [hval_hashable] at hb; done)
        | (simp only [hval_eq, hval_canon] <;> simp [hpairs_key_eq]; done)
        | (simp only [hval_eq, hval_canon] <;> split <;> simp_all; done)
  | .HTuple l, b, ha, hb => by
      cases b with
      | HTuple m =>
          simp only [hval_eq, hval_canon, HVal.HTuple.injEq]
          exact hlist_coherent l m (by simpa [hval_hashable] using ha)
            (by simpa [hval_hashable] using hb)
      | _ => first
        | (simp [hval_hashable] at hb; done)
        | (simp only [hval_eq, hval_canon] <;> simp [hpairs_key_eq]; done)
        | (simp only [hval_eq, hval_canon] <;> split <;> simp_all; done)
  | .HArr _, _, ha, _ => by simp [hval_hashable] at ha
  | .HMap _, _, ha, _ => by simp [hval_hashable] at ha
  | .HNode _, _, ha, _ => by simp [hval_hashable] at ha
theorem hlist_coherent [RealCarrier F] : ∀ (l m : HValList F), hlist_hashable l = true →
    hlist_hashable m = true → (hlist_eq l m = true ↔ hlist_canon l = hlist_canon m)
  | .HNil, m, _, _ => by cases m <;> simp [hlist_eq, hlist_canon]
  | .HCons x t, m, hl, hm => by
      cases m with
      | HNil => simp [hlist_eq, hlist_canon]
      | HCons y u =>
          simp [hlist_hashable] at hl hm
          simp only [hlist_eq, hlist_canon, Bool.and_eq_true, HValList.HCons.injEq]
          rw [eq_canon_coherent x y hl.1 hm.1, hlist_coherent t u hl.2 hm.2]
end

theorem hval_eq_refl_hashable [RealCarrier F] (a : HVal F) (h : hval_hashable a = true) :
    hval_eq a a = true := (eq_canon_coherent a a h h).2 rfl

theorem canon_true [RealCarrier F] : hval_canon (.HBool true : HVal F) = .HInt 1 := by
  simp [hval_canon, hbool_int]
theorem canon_false [RealCarrier F] : hval_canon (.HBool false : HVal F) = .HInt 0 := by
  simp [hval_canon, hbool_int]
theorem canon_onef [RealCarrier F] : hval_canon (.HFloat (from_int 1 : F)) = .HInt 1 := by
  simp [hval_canon, hreal_int_of_from_int]
theorem canon_nonintegral [RealCarrier F] (g : F) (hg : hreal_int_of g = none) :
    hval_canon (.HFloat g) = .HFloat g := by simp [hval_canon, hg]
theorem canon_merges_keys [RealCarrier F] :
    hval_canon (.HInt 1 : HVal F) = hval_canon (.HBool true) ∧
    hval_canon (.HInt 1 : HVal F) = hval_canon (.HFloat (from_int 1 : F)) := by
  simp [hval_canon, hbool_int, hreal_int_of_from_int]
theorem hashable_scalars (b : Bool) (i : Int) (f : F) (s : String) :
    hval_hashable (.HNone : HVal F) = true ∧ hval_hashable (.HBool b : HVal F) = true ∧
    hval_hashable (.HInt i : HVal F) = true ∧ hval_hashable (.HFloat f) = true ∧
    hval_hashable (.HStr s : HVal F) = true := by simp [hval_hashable]
theorem hashable_tuple (x : HVal F) (t : HValList F) :
    hval_hashable (.HTuple (.HCons x t)) = (hval_hashable x && hval_hashable (.HTuple t)) := by
  simp [hval_hashable, hlist_hashable]
theorem unhashable_list (l : HValList F) : hval_hashable (.HArr l) = false := by simp [hval_hashable]
theorem unhashable_dict (p : HPairs F) : hval_hashable (.HMap p) = false := by simp [hval_hashable]
theorem unhashable_node (v : HVal F) : hval_hashable (.HNode v) = false := by simp [hval_hashable]
theorem unhashable_tuple_of_list (l : HValList F) :
    hval_hashable (.HTuple (.HCons (.HArr l) .HNil)) = false := by
  simp [hval_hashable, hlist_hashable]

-- ===================================================================== --
-- 6. Python truthiness over all 9 tags.                                  --
-- ===================================================================== --

def hval_truthy [RealCarrier F] : HVal F → Bool
  | .HNone => false
  | .HBool b => b
  | .HInt i => !(decide (i = 0))
  | .HFloat f => !(F_eqb f (from_int 0))       -- `0.0` = from_int 0 (FromInt.Zero)
  | .HStr s => !(hpairs_key_eq s "")
  | .HTuple l => (match l with | .HNil => false | _ => true)
  | .HArr l => (match l with | .HNil => false | _ => true)
  | .HMap p => (match p with | .PNil => false | _ => true)
  | .HNode _ => true

theorem truthy_none [RealCarrier F] : hval_truthy (.HNone : HVal F) = false := by simp [hval_truthy]
theorem truthy_false [RealCarrier F] : hval_truthy (.HBool false : HVal F) = false := by
  simp [hval_truthy]
theorem truthy_zero [RealCarrier F] : hval_truthy (.HInt 0 : HVal F) = false := by
  simp [hval_truthy]
theorem truthy_fzero [RealCarrier F] : hval_truthy (.HFloat (from_int 0 : F)) = false := by
  simp [hval_truthy, (F_eqb_spec (from_int 0 : F) (from_int 0)).2 rfl]
theorem truthy_empty_str [RealCarrier F] : hval_truthy (.HStr "" : HVal F) = false := by
  simp [hval_truthy, hpairs_key_eq]
theorem truthy_empty_tuple [RealCarrier F] : hval_truthy (.HTuple .HNil : HVal F) = false := by
  simp [hval_truthy]
theorem truthy_empty_list [RealCarrier F] : hval_truthy (.HArr .HNil : HVal F) = false := by
  simp [hval_truthy]
theorem truthy_empty_dict [RealCarrier F] : hval_truthy (.HMap .PNil : HVal F) = false := by
  simp [hval_truthy]
theorem truthy_true [RealCarrier F] : hval_truthy (.HBool true : HVal F) = true := by
  simp [hval_truthy]
theorem truthy_int [RealCarrier F] (i : Int) (h : i ≠ 0) : hval_truthy (.HInt i : HVal F) = true := by
  simp [hval_truthy, h]
theorem truthy_float [RealCarrier F] (f : F) (h : f ≠ from_int 0) :
    hval_truthy (.HFloat f) = true := by
  have e : F_eqb f (from_int 0) = false := by
    cases e : F_eqb f (from_int 0) with
    | false => rfl
    | true => exact absurd ((F_eqb_spec _ _).1 e) h
  simp [hval_truthy, e]
theorem truthy_str [RealCarrier F] (s : String) (h : s ≠ "") : hval_truthy (.HStr s : HVal F) = true := by
  simp [hval_truthy, hpairs_key_eq, h]
theorem truthy_tuple [RealCarrier F] (x : HVal F) (l : HValList F) :
    hval_truthy (.HTuple (.HCons x l)) = true := by simp [hval_truthy]
theorem truthy_list [RealCarrier F] (x : HVal F) (l : HValList F) :
    hval_truthy (.HArr (.HCons x l)) = true := by simp [hval_truthy]
theorem truthy_dict [RealCarrier F] (k : String) (x : HVal F) (p : HPairs F) :
    hval_truthy (.HMap (.PCons k x p)) = true := by simp [hval_truthy]
theorem truthy_node [RealCarrier F] (n : HVal F) : hval_truthy (.HNode n) = true := by
  simp [hval_truthy]
theorem truthy_false_iff [RealCarrier F] (v : HVal F) : hval_truthy v = false ↔
    v = .HNone ∨ v = .HBool false ∨ v = .HInt 0 ∨ v = .HFloat (from_int 0) ∨
    v = .HStr "" ∨ v = .HTuple .HNil ∨ v = .HArr .HNil ∨ v = .HMap .PNil := by
  cases v with
  | HNone => simp [hval_truthy]
  | HBool b => cases b <;> simp [hval_truthy]
  | HInt i => simp [hval_truthy]
  | HFloat f => simp [hval_truthy, F_eqb_spec]
  | HStr s => simp [hval_truthy, hpairs_key_eq]
  | HTuple l => cases l <;> simp [hval_truthy]
  | HArr l => cases l <;> simp [hval_truthy]
  | HMap p => cases p <;> simp [hval_truthy]
  | HNode n => simp [hval_truthy]

-- ===================================================================== --
-- 7. Projections.                                                        --
-- ===================================================================== --

def hstr_of [OpaqueArms F] (h : HVal F) : String :=
  match h with
  | .HStr s => s
  | _ => hval_opaque_str h
def hint_of [OpaqueArms F] (h : HVal F) : Int :=
  match h with
  | .HInt i => i
  | .HBool b => hbool_int b
  | _ => hval_opaque_int h

theorem proj_on_tag_str [OpaqueArms F] (s : String) : hstr_of (.HStr s : HVal F) = s := rfl
theorem proj_on_tag_int [OpaqueArms F] (i : Int) : hint_of (.HInt i : HVal F) = i := rfl
theorem proj_on_tag_bool [OpaqueArms F] (b : Bool) :
    hint_of (.HBool b : HVal F) = if b then 1 else 0 := rfl
theorem proj_off_tag_str [OpaqueArms F] (h : HVal F) (hn : ∀ s, h ≠ .HStr s) :
    hstr_of h = hval_opaque_str h := by
  cases h with
  | HStr s => exact absurd rfl (hn s)
  | _ => rfl
theorem proj_off_tag_int [OpaqueArms F] (h : HVal F) (h1 : ∀ i, h ≠ .HInt i) (h2 : ∀ b, h ≠ .HBool b) :
    hint_of h = hval_opaque_int h := by
  cases h with
  | HInt i => exact absurd rfl (h1 i)
  | HBool b => exact absurd rfl (h2 b)
  | _ => rfl
theorem proj_total [OpaqueArms F] (h : HVal F) : ∃ s i, hstr_of h = s ∧ hint_of h = i :=
  ⟨hstr_of h, hint_of h, rfl, rfl⟩

-- ===================================================================== --
-- 8. Sequences: len / nth / tuple / snoc.                                --
-- ===================================================================== --

def hval_list_len : HValList F → Int
  | .HNil => 0
  | .HCons _ t => 1 + hval_list_len t

-- verbatim the emitted hval_list_nth (out-of-range arm `HInt 0`)
def hval_list_nth : HValList F → Int → HVal F
  | .HNil, _ => .HInt 0
  | .HCons x t, i => if i ≤ 0 then x else hval_list_nth t (i - 1)

def hstr_len (s : String) : Int := s.length

def hval_len [OpaqueArms F] (h : HVal F) : Int :=
  match h with
  | .HStr s => hstr_len s
  | .HTuple l => hval_list_len l
  | .HArr l => hval_list_len l
  | .HMap p => hpairs_len p
  | _ => hval_len_other h

def hval_tuple [OpaqueArms F] (h : HVal F) : HVal F :=
  match h with
  | .HTuple l => .HTuple l
  | .HArr l => .HTuple l
  | .HMap p => .HTuple (hpairs_keys p)
  | _ => hval_tuple_other h

def hval_list_snoc : HValList F → HVal F → HValList F
  | .HNil, x => .HCons x .HNil
  | .HCons h t, x => .HCons h (hval_list_snoc t x)

def InL : HVal F → HValList F → Prop
  | _, .HNil => False
  | x, .HCons y t => x = y ∨ InL x t

theorem len_nonneg : ∀ l : HValList F, hval_list_len l ≥ 0
  | .HNil => by simp [hval_list_len]
  | .HCons _ t => by have := len_nonneg t; simp [hval_list_len]; omega

theorem nth_head (x : HVal F) (t : HValList F) : hval_list_nth (.HCons x t) 0 = x := by
  simp [hval_list_nth]

theorem nth_tail (x : HVal F) (t : HValList F) (i : Int) (h : i ≥ 0) :
    hval_list_nth (.HCons x t) (i + 1) = hval_list_nth t i := by
  have hn : ¬ (i + 1 ≤ 0) := by omega
  simp only [hval_list_nth]; rw [if_neg hn]; congr 1; omega

theorem nth_in_range : ∀ (l : HValList F) (i : Int), 0 ≤ i ∧ i < hval_list_len l →
    InL (hval_list_nth l i) l
  | .HNil, i, h => by simp [hval_list_len] at h <;> omega
  | .HCons x t, i, h => by
      simp only [hval_list_len] at h
      simp only [hval_list_nth, InL]
      by_cases hi : i ≤ 0
      · rw [if_pos hi]; left; rfl
      · rw [if_neg hi]; right
        exact nth_in_range t (i - 1) (by have := len_nonneg t; omega)

theorem snoc_len : ∀ (l : HValList F) (x : HVal F),
    hval_list_len (hval_list_snoc l x) = hval_list_len l + 1
  | .HNil, x => by simp [hval_list_snoc, hval_list_len]
  | .HCons _ t, x => by
      have ih := snoc_len t x
      simp only [hval_list_snoc, hval_list_len]; rw [ih]; omega

theorem snoc_nth_last : ∀ (l : HValList F) (x : HVal F),
    hval_list_nth (hval_list_snoc l x) (hval_list_len l) = x
  | .HNil, x => by simp [hval_list_snoc, hval_list_len, hval_list_nth]
  | .HCons _ t, x => by
      have ih := snoc_nth_last t x
      have hl := len_nonneg t
      simp only [hval_list_snoc, hval_list_len, hval_list_nth]
      rw [if_neg (by omega)]
      rw [show 1 + hval_list_len t - 1 = hval_list_len t by omega]; exact ih

theorem keys_len : ∀ p : HPairs F, hval_list_len (hpairs_keys p) = hpairs_len p
  | .PNil => by simp [hpairs_keys, hval_list_len, hpairs_len]
  | .PCons _ _ t => by
      have ih := keys_len t
      simp only [hpairs_keys, hval_list_len, hpairs_len]; rw [ih]

theorem len_str [OpaqueArms F] (s : String) : hval_len (.HStr s : HVal F) = s.length := rfl
theorem len_tuple [OpaqueArms F] (l : HValList F) : hval_len (.HTuple l) = hval_list_len l := rfl
theorem len_arr [OpaqueArms F] (l : HValList F) : hval_len (.HArr l) = hval_list_len l := rfl
theorem len_map [OpaqueArms F] (p : HPairs F) : hval_len (.HMap p) = hpairs_len p := rfl
theorem len_nonneg_on_tag [OpaqueArms F] (h : HVal F)
    (ht : (∃ s, h = .HStr s) ∨ (∃ l, h = .HTuple l) ∨ (∃ l, h = .HArr l) ∨ (∃ p, h = .HMap p)) :
    hval_len h ≥ 0 := by
  rcases ht with ⟨s, rfl⟩ | ⟨l, rfl⟩ | ⟨l, rfl⟩ | ⟨p, rfl⟩
  · simp [hval_len, hstr_len]
  · exact len_nonneg l
  · exact len_nonneg l
  · exact hpairs_len_nonneg p
theorem len_literal_dup [OpaqueArms F] (a b : HVal F) :
    hval_len (.HMap (pairs_build .PNil [("a", a), ("a", b)])) = 1 := by
  simp [hval_len, pairs_build, pairs_set, hpairs_key_eq, hpairs_len]

theorem tuple_preserves_elems [OpaqueArms F] (l : HValList F) :
    hval_tuple (.HArr l) = .HTuple l ∧ hval_tuple (.HTuple l) = .HTuple l ∧
    hval_len (hval_tuple (.HArr l)) = hval_len (.HArr l) ∧
    (∀ i, (match hval_tuple (.HArr l) with | .HTuple l' => hval_list_nth l' i | _ => .HNone)
          = hval_list_nth l i) :=
  ⟨rfl, rfl, rfl, fun _ => rfl⟩
theorem tuple_of_dict_keys [OpaqueArms F] (p : HPairs F) :
    hval_tuple (.HMap p) = .HTuple (hpairs_keys p) ∧
    hval_len (hval_tuple (.HMap p)) = hval_len (.HMap p) :=
  ⟨rfl, keys_len p⟩

-- ===================================================================== --
-- 9. A concrete model of the carrier laws (satisfiability).              --
-- ===================================================================== --

structure CF where
  n : Int
  half : Bool
  deriving DecidableEq

instance : RealCarrier CF where
  F_eqb a b := decide (a = b)
  F_eqb_spec a b := by simp
  from_int i := ⟨i, false⟩
  from_int_inj i j h := by injection h
  hreal_int_of f := if f.half then none else some f.n
  hreal_int_of_some f i h := by
    cases f with
    | mk n hf => cases hf <;> simp_all
  hreal_int_of_none f h i := by
    cases f with
    | mk n hf => cases hf <;> simp_all

theorem model_half_ne_int (i : Int) :
    hval_eq (.HInt i : HVal CF) (.HFloat ⟨0, true⟩) = false := rfl
theorem model_one_eq_onef :
    hval_eq (.HInt 1 : HVal CF) (.HFloat (from_int 1)) = true := eq_one_onef
theorem model_eq_sym (a b : HVal CF) (ha : hval_wf a = true) (hb : hval_wf b = true) :
    hval_eq a b = hval_eq b a := hval_eq_sym a b ha hb

-- ===================================================================== --
-- 9b. The WhyML `val hreal_int_of` spec is the EQUATION                  --
--   result = if from_int (truncate f) = f then Some (truncate f) else None --
-- (real.Truncate; Truncate_int : truncate (from_int i) = i).  Any        --
-- function given by it satisfies the carrier laws hreal_int_of_some/none. --
-- ===================================================================== --

def int_of_eqn {G : Type} (eqb : G → G → Bool) (fi : Int → G) (trunc : G → Int) (f : G) :
    Option Int :=
  if eqb (fi (trunc f)) f then some (trunc f) else none

theorem int_of_eqn_some {G : Type} (eqb : G → G → Bool) (eqb_spec : ∀ a b, eqb a b = true ↔ a = b)
    (fi : Int → G) (trunc : G → Int) (f : G) (i : Int)
    (h : int_of_eqn eqb fi trunc f = some i) : fi i = f := by
  unfold int_of_eqn at h
  cases e : eqb (fi (trunc f)) f with
  | true => rw [e] at h; simp at h; rw [← h]; exact (eqb_spec _ _).1 e
  | false => rw [e] at h; simp at h

theorem int_of_eqn_none {G : Type} (eqb : G → G → Bool) (eqb_spec : ∀ a b, eqb a b = true ↔ a = b)
    (fi : Int → G) (trunc : G → Int) (htf : ∀ i, trunc (fi i) = i) (f : G)
    (h : int_of_eqn eqb fi trunc f = none) (i : Int) : fi i ≠ f := by
  intro x
  unfold int_of_eqn at h
  subst x
  rw [htf i, (eqb_spec (fi i) (fi i)).2 rfl] at h
  simp at h

end PyValR4Cert

-- ===================================================================== --
-- 10. VERDICT — axiom audit: only propext / Classical.choice / Quot.sound --
--     may appear (proof_axiom_allowlist.py); NO 4th axiom; no sorry.     --
-- ===================================================================== --

#print axioms PyValR4Cert.key_refl
#print axioms PyValR4Cert.hpairs_key_eq_spec
#print axioms PyValR4Cert.hreal_int_of_from_int
#print axioms PyValR4Cert.size_pos
#print axioms PyValR4Cert.list_size_nonneg
#print axioms PyValR4Cert.pairs_size_nonneg
#print axioms PyValR4Cert.list_tail_size_lt
#print axioms PyValR4Cert.pairs_tail_size_lt
#print axioms PyValR4Cert.size_sub_tuple
#print axioms PyValR4Cert.size_sub_arr
#print axioms PyValR4Cert.size_sub_map
#print axioms PyValR4Cert.size_sub_node
#print axioms PyValR4Cert.hbool_inj
#print axioms PyValR4Cert.hint_inj
#print axioms PyValR4Cert.hfloat_inj
#print axioms PyValR4Cert.hstr_inj
#print axioms PyValR4Cert.htuple_inj
#print axioms PyValR4Cert.harr_inj
#print axioms PyValR4Cert.hmap_inj
#print axioms PyValR4Cert.hnode_inj
#print axioms PyValR4Cert.hcons_inj
#print axioms PyValR4Cert.pcons_inj
#print axioms PyValR4Cert.hnil_neq_hcons
#print axioms PyValR4Cert.pnil_neq_pcons
#print axioms PyValR4Cert.neq_none_bool
#print axioms PyValR4Cert.neq_none_int
#print axioms PyValR4Cert.neq_none_float
#print axioms PyValR4Cert.neq_none_str
#print axioms PyValR4Cert.neq_none_tuple
#print axioms PyValR4Cert.neq_none_arr
#print axioms PyValR4Cert.neq_none_map
#print axioms PyValR4Cert.neq_none_node
#print axioms PyValR4Cert.neq_bool_int
#print axioms PyValR4Cert.neq_bool_float
#print axioms PyValR4Cert.neq_bool_str
#print axioms PyValR4Cert.neq_bool_tuple
#print axioms PyValR4Cert.neq_bool_arr
#print axioms PyValR4Cert.neq_bool_map
#print axioms PyValR4Cert.neq_bool_node
#print axioms PyValR4Cert.neq_int_float
#print axioms PyValR4Cert.neq_int_str
#print axioms PyValR4Cert.neq_int_tuple
#print axioms PyValR4Cert.neq_int_arr
#print axioms PyValR4Cert.neq_int_map
#print axioms PyValR4Cert.neq_int_node
#print axioms PyValR4Cert.neq_float_str
#print axioms PyValR4Cert.neq_float_tuple
#print axioms PyValR4Cert.neq_float_arr
#print axioms PyValR4Cert.neq_float_map
#print axioms PyValR4Cert.neq_float_node
#print axioms PyValR4Cert.neq_str_tuple
#print axioms PyValR4Cert.neq_str_arr
#print axioms PyValR4Cert.neq_str_map
#print axioms PyValR4Cert.neq_str_node
#print axioms PyValR4Cert.neq_tuple_arr
#print axioms PyValR4Cert.neq_tuple_map
#print axioms PyValR4Cert.neq_tuple_node
#print axioms PyValR4Cert.neq_arr_map
#print axioms PyValR4Cert.neq_arr_node
#print axioms PyValR4Cert.neq_map_node
#print axioms PyValR4Cert.pairs_get_nil
#print axioms PyValR4Cert.pairs_get_cons
#print axioms PyValR4Cert.pairs_mem_iff
#print axioms PyValR4Cert.pairs_set_get
#print axioms PyValR4Cert.read_same_key
#print axioms PyValR4Cert.read_other_key
#print axioms PyValR4Cert.mem_set
#print axioms PyValR4Cert.nodup_preserved
#print axioms PyValR4Cert.len_set
#print axioms PyValR4Cert.hpairs_len_nonneg
#print axioms PyValR4Cert.build_is_fold_left
#print axioms PyValR4Cert.build_fold_read_back
#print axioms PyValR4Cert.build_nodup
#print axioms PyValR4Cert.build_last_wins
#print axioms PyValR4Cert.build_len_dup
#print axioms PyValR4Cert.build_insertion_order
#print axioms PyValR4Cert.get_InP
#print axioms PyValR4Cert.InP_mem
#print axioms PyValR4Cert.InP_get_nodup
#print axioms PyValR4Cert.wf_InP
#print axioms PyValR4Cert.incl_spec
#print axioms PyValR4Cert.keys_in_spec
#print axioms PyValR4Cert.hval_eq_refl
#print axioms PyValR4Cert.hlist_eq_refl
#print axioms PyValR4Cert.pairs_refl
#print axioms PyValR4Cert.zeq_from_int
#print axioms PyValR4Cert.int_float
#print axioms PyValR4Cert.float_int
#print axioms PyValR4Cert.bool_bool
#print axioms PyValR4Cert.eq_numeric_tower
#print axioms PyValR4Cert.num_sym
#print axioms PyValR4Cert.hval_eq_sym_true
#print axioms PyValR4Cert.hlist_eq_sym_true
#print axioms PyValR4Cert.pairs_sym
#print axioms PyValR4Cert.hval_eq_sym
#print axioms PyValR4Cert.eq_map_iff
#print axioms PyValR4Cert.eq_dict_order_independent
#print axioms PyValR4Cert.eq_true_one
#print axioms PyValR4Cert.eq_one_true
#print axioms PyValR4Cert.eq_false_zero
#print axioms PyValR4Cert.eq_true_two
#print axioms PyValR4Cert.eq_one_onef
#print axioms PyValR4Cert.eq_onef_one
#print axioms PyValR4Cert.eq_true_onef
#print axioms PyValR4Cert.eq_int_nonintegral
#print axioms PyValR4Cert.eq_str_int
#print axioms PyValR4Cert.eq_one_str_one
#print axioms PyValR4Cert.eq_none_zero
#print axioms PyValR4Cert.eq_none_false
#print axioms PyValR4Cert.eq_none_none
#print axioms PyValR4Cert.eq_tuple_list
#print axioms PyValR4Cert.eq_list_tuple
#print axioms PyValR4Cert.eq_tuple1_list1
#print axioms PyValR4Cert.eq_dict_order
#print axioms PyValR4Cert.float_canon
#print axioms PyValR4Cert.eq_canon_coherent
#print axioms PyValR4Cert.hlist_coherent
#print axioms PyValR4Cert.hval_eq_refl_hashable
#print axioms PyValR4Cert.canon_true
#print axioms PyValR4Cert.canon_false
#print axioms PyValR4Cert.canon_onef
#print axioms PyValR4Cert.canon_nonintegral
#print axioms PyValR4Cert.canon_merges_keys
#print axioms PyValR4Cert.hashable_scalars
#print axioms PyValR4Cert.hashable_tuple
#print axioms PyValR4Cert.unhashable_list
#print axioms PyValR4Cert.unhashable_dict
#print axioms PyValR4Cert.unhashable_node
#print axioms PyValR4Cert.unhashable_tuple_of_list
#print axioms PyValR4Cert.truthy_none
#print axioms PyValR4Cert.truthy_false
#print axioms PyValR4Cert.truthy_zero
#print axioms PyValR4Cert.truthy_fzero
#print axioms PyValR4Cert.truthy_empty_str
#print axioms PyValR4Cert.truthy_empty_tuple
#print axioms PyValR4Cert.truthy_empty_list
#print axioms PyValR4Cert.truthy_empty_dict
#print axioms PyValR4Cert.truthy_true
#print axioms PyValR4Cert.truthy_int
#print axioms PyValR4Cert.truthy_float
#print axioms PyValR4Cert.truthy_str
#print axioms PyValR4Cert.truthy_tuple
#print axioms PyValR4Cert.truthy_list
#print axioms PyValR4Cert.truthy_dict
#print axioms PyValR4Cert.truthy_node
#print axioms PyValR4Cert.truthy_false_iff
#print axioms PyValR4Cert.proj_on_tag_str
#print axioms PyValR4Cert.proj_on_tag_int
#print axioms PyValR4Cert.proj_on_tag_bool
#print axioms PyValR4Cert.proj_off_tag_str
#print axioms PyValR4Cert.proj_off_tag_int
#print axioms PyValR4Cert.proj_total
#print axioms PyValR4Cert.len_nonneg
#print axioms PyValR4Cert.nth_head
#print axioms PyValR4Cert.nth_tail
#print axioms PyValR4Cert.nth_in_range
#print axioms PyValR4Cert.snoc_len
#print axioms PyValR4Cert.snoc_nth_last
#print axioms PyValR4Cert.keys_len
#print axioms PyValR4Cert.len_str
#print axioms PyValR4Cert.len_tuple
#print axioms PyValR4Cert.len_arr
#print axioms PyValR4Cert.len_map
#print axioms PyValR4Cert.len_nonneg_on_tag
#print axioms PyValR4Cert.len_literal_dup
#print axioms PyValR4Cert.tuple_preserves_elems
#print axioms PyValR4Cert.tuple_of_dict_keys
#print axioms PyValR4Cert.model_half_ne_int
#print axioms PyValR4Cert.model_one_eq_onef
#print axioms PyValR4Cert.model_eq_sym
#print axioms PyValR4Cert.int_of_eqn_some
#print axioms PyValR4Cert.int_of_eqn_none
#print axioms PyValR4Cert.hval_eq_int_lit
#print axioms PyValR4Cert.hval_eq_bool_lit
#print axioms PyValR4Cert.hval_eq_intfloat_lit
#print axioms PyValR4Cert.hval_eq_float_lit
#print axioms PyValR4Cert.hval_eq_none_lit
#print axioms PyValR4Cert.hval_eq_str_lit
