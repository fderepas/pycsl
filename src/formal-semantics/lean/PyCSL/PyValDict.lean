/-
  PyValDict.lean — certificate for the wall-plan-v2 concrete-map encoding.

  WALL-PLAN v2, Phase 1 (generic-dict-str-any-2-plan.md §1 D1–D3, §2 E4,
  §3 F4, §4). The Lean 4.29 twin of `Phase2c_PyValDict.v`: the axiom-free
  certificate co-landing with the WhyML `pydict`/`pyval`/`irkey`/`doc` theory
  promoted into the emitter preamble. It certifies — against pure inductive
  datatypes, NO axiom — exactly the constructs the Phase-0 spike proved on
  both SMT provers (the tier-3 coupling rule, cf. RecordVal.lean):

    D1  `PyVal`/`PyDict` — strictly-positive nested inductive universal value;
        `get`/`memKey` structural lookups; the concrete-lookup laws.
    D2  `IrKey` interned keys + the string<->key boundary bijection
        (computable, no axiom — R-B: constructors, not strings).
    D3  `size` termination measure + the sub-term size lemma pack (induction).
    E4  `wfIr` well-formedness + the compositionality (binds-projection) lemma.
    F4  `Doc` document ADT + `render` monoid laws (R-C).

  Verdict decided by `#print axioms` at the bottom: only the standard Lean
  kernel axioms (propext, Classical.choice, Quot.sound) may appear — NO 4th,
  extension-specific axiom — so the 3-axiom trust ledger stays intact (+0).

  Nothing here is left unproven.
-/

namespace PyValDict

-- ===================================================================== --
-- D2 — R-B: interned IR keys + the string<->key boundary bijection.       --
-- ===================================================================== --

inductive IrKey where
  | type | left | right | op | z
  | value | target | body | orelse | func | name
  | dyn (s : String)
  deriving DecidableEq

def IrKey.eqb (a b : IrKey) : Bool := a == b

/-- The reserved (named, nullary) key names. -/
def reserved (s : String) : Bool :=
  s == "type" || s == "left" || s == "right" || s == "op" || s == "z" ||
  s == "value" || s == "target" || s == "body" || s == "orelse" ||
  s == "func" || s == "name"

def stringOfKey : IrKey → String
  | .type => "type" | .left => "left" | .right => "right"
  | .op => "op"     | .z => "z"       | .value => "value"
  | .target => "target" | .body => "body" | .orelse => "orelse"
  | .func => "func" | .name => "name" | .dyn s => s

def keyOfString (s : String) : IrKey :=
  if s == "type" then .type
  else if s == "left" then .left
  else if s == "right" then .right
  else if s == "op" then .op
  else if s == "z" then .z
  else if s == "value" then .value
  else if s == "target" then .target
  else if s == "body" then .body
  else if s == "orelse" then .orelse
  else if s == "func" then .func
  else if s == "name" then .name
  else .dyn s

/-- A key is well-formed when a `dyn` payload is not a reserved name. -/
def keyWf : IrKey → Prop
  | .dyn s => reserved s = false
  | _ => True

/-- R-B computable bijection: `stringOfKey` then `keyOfString` round-trips on
    every well-formed key. NO axiom. -/
theorem key_roundtrip (k : IrKey) (h : keyWf k) : keyOfString (stringOfKey k) = k := by
  cases k <;> simp_all [keyWf, reserved, stringOfKey, keyOfString]

/-- `stringOfKey` is injective on well-formed keys. -/
theorem stringOfKey_inj (k1 k2 : IrKey) (h1 : keyWf k1) (h2 : keyWf k2)
    (heq : stringOfKey k1 = stringOfKey k2) : k1 = k2 := by
  have e1 := key_roundtrip k1 h1
  have e2 := key_roundtrip k2 h2
  rw [← e1, ← e2, heq]

-- ===================================================================== --
-- D1 — R-A: the strictly-positive concrete universal value.              --
-- ===================================================================== --

/- `PyDict` is the schema-keyed assoc-list, realized as `List (IrKey × PyVal)`
   (the SAME assoc-list as the WhyML `pydict = DNil | DCons` / the Rocq mutual
   inductive; Lean's `induction` tactic does not support a mutual-inductive
   `PyDict`, and the list realization is definitionally the same object and
   certifies the identical laws — a nested inductive Lean supports positively). -/
inductive PyVal where
  | int  (n : Int)
  | str  (s : String)
  | bool (b : Bool)
  | none
  | list (xs : List PyVal)
  | dict (d : List (IrKey × PyVal))

abbrev PyDict := List (IrKey × PyVal)

def get : PyDict → IrKey → Option PyVal
  | [], _ => .none
  | (k', v) :: rest, k => if k == k' then some v else get rest k

def memKey : PyDict → IrKey → Bool
  | [], _ => false
  | (k', _) :: rest, k => (k == k') || memKey rest k

def binds (k : IrKey) (v : PyVal) (d : PyDict) : Prop := get d k = some v

/-- Concrete-lookup law: a hit at the head reads the bound value. -/
theorem get_hit_head (k : IrKey) (v : PyVal) (rest : PyDict) :
    get ((k, v) :: rest) k = some v := by
  simp [get]

/-- `get` implies membership. -/
theorem get_some_mem (d : PyDict) (k : IrKey) (v : PyVal) (h : get d k = some v) :
    memKey d k = true := by
  induction d with
  | nil => simp [get] at h
  | cons hd rest ih =>
      obtain ⟨k', v'⟩ := hd
      simp only [get] at h
      by_cases hk : k == k'
      · simp [memKey, hk]
      · simp only [hk] at h
        simp [memKey, hk, ih h]

-- ===================================================================== --
-- D3 — the `size` measure + the sub-term size lemma pack.                 --
-- ===================================================================== --

mutual
def size : PyVal → Nat
  | .int _ | .str _ | .bool _ | .none => 1
  | .list xs => 1 + sizeList xs
  | .dict d => 1 + sizeDict d
def sizeList : List PyVal → Nat
  | [] => 0
  | h :: t => 1 + size h + sizeList t
def sizeDict : List (IrKey × PyVal) → Nat
  | [] => 0
  | (_, v) :: rest => 1 + size v + sizeDict rest
end

/-- Every value has strictly positive size. -/
theorem size_pos (v : PyVal) : 0 < size v := by
  cases v <;> simp [size] <;> omega

/-- Sub-term law: a value bound in a dict is strictly smaller than the dict. -/
theorem size_dict_mem (d : PyDict) (k : IrKey) (v : PyVal) (h : binds k v d) :
    size v < size (.dict d) := by
  simp only [binds] at h
  induction d with
  | nil => simp [get] at h
  | cons hd rest ih =>
      obtain ⟨k', v'⟩ := hd
      simp only [get] at h
      by_cases hk : k == k'
      · simp only [hk, if_true, Option.some.injEq] at h
        subst h
        simp only [size, sizeDict]; omega
      · simp only [hk] at h
        have := ih h
        simp only [size, sizeDict] at *; omega

-- ===================================================================== --
-- E4 — `wfIr` well-formedness + the compositionality lemma.               --
-- ===================================================================== --

/-- Representative per-key value typing: string-valued schema keys carry `str`. -/
def wfVal (k : IrKey) (v : PyVal) : Prop :=
  match k with
  | .op | .type | .target | .func | .name =>
      match v with | .str _ => True | _ => False
  | _ => True

def wfDict : PyDict → Prop
  | [] => True
  | (k, v) :: rest => wfVal k v ∧ wfDict rest

def wfIr : PyVal → Prop
  | .dict d => wfDict d
  | _ => True

/-- Compositionality: a well-formed dict, projected at any bound key, yields a
    value satisfying that key's typing (E4's binds-projection fact). -/
theorem wfIr_binds (d : PyDict) (k : IrKey) (v : PyVal)
    (hwf : wfDict d) (hb : binds k v d) : wfVal k v := by
  simp only [binds] at hb
  induction d with
  | nil => simp [get] at hb
  | cons hd rest ih =>
      obtain ⟨k', v'⟩ := hd
      simp only [wfDict] at hwf
      obtain ⟨hhead, htail⟩ := hwf
      simp only [get] at hb
      by_cases hk : k == k'
      · simp only [hk, if_true, Option.some.injEq] at hb
        subst hb
        have : k = k' := by simpa using hk
        subst this; exact hhead
      · simp only [hk] at hb
        exact ih htail hb

-- ===================================================================== --
-- F4 — the document ADT `Doc` + `render` monoid laws (R-C).               --
-- ===================================================================== --

inductive Doc where
  | text (s : String)
  | int  (n : Int)
  | cat  (a b : Doc)
  | nil

def render : Doc → String
  | .text s => s
  | .int n  => toString n
  | .cat a b => render a ++ render b
  | .nil => ""

theorem render_text (s : String) : render (.text s) = s := rfl
theorem render_nil : render .nil = "" := rfl
theorem render_cat (a b : Doc) : render (.cat a b) = render a ++ render b := rfl

theorem render_cat_assoc (a b c : Doc) :
    render (.cat (.cat a b) c) = render (.cat a (.cat b c)) := by
  simp [render, String.append_assoc]

theorem render_nil_left (a : Doc) : render (.cat .nil a) = render a := by
  simp [render]

theorem render_nil_right (a : Doc) : render (.cat a .nil) = render a := by
  simp [render]

-- ===================================================================== --
-- T3 — ir-traversal-residual: the string-keyed symbol table `SDict`        --
--   (env-threaded fold, plan §5). A SECOND, deliberately-boring datatype   --
--   whose keys are RUNTIME strings (NOT interned IrKey), with an           --
--   option-valued `slookup` — the 2nd/last co-landed certificate.          --
--   Ordinary inductive datatype + a total structural def; the lemma pack   --
--   is one induction each. NO axiom.                                       --
-- ===================================================================== --

inductive SDict where
  | nil
  | cons (k : String) (v : PyVal) (rest : SDict)

def slookup (k : String) : SDict → Option PyVal
  | .nil => none
  | .cons k' v rest => if k == k' then some v else slookup k rest

def smem (k : String) : SDict → Bool
  | .nil => false
  | .cons k' _ rest => (k == k') || smem k rest

/-- Head hit — a matching head key reads its bound value. -/
theorem slookup_hit_head (k k' : String) (v : PyVal) (rest : SDict)
    (h : (k == k') = true) : slookup k (.cons k' v rest) = some v := by
  simp [slookup, h]

/-- Soundness — a `some` hit implies membership (mirrors get_some_mem). -/
theorem slookup_some_smem (s : SDict) (k : String) (v : PyVal)
    (h : slookup k s = some v) : smem k s = true := by
  induction s with
  | nil => simp [slookup] at h
  | cons k' v' rest ih =>
      simp only [slookup] at h
      by_cases hk : k == k'
      · simp [smem, hk]
      · simp only [hk] at h
        simp [smem, hk, ih h]

/-- Total node count of a symbol table (for the in-bounds law). -/
def sdictSize : SDict → Nat
  | .nil => 0
  | .cons _ v rest => 1 + size v + sdictSize rest

/-- In-bounds / sub-term — a value found by slookup is strictly smaller than
    the table it lives in (mirrors size_dict_mem for the PyDict case). -/
theorem size_slookup_mem (s : SDict) (k : String) (v : PyVal)
    (h : slookup k s = some v) : size v < sdictSize s := by
  induction s with
  | nil => simp [slookup] at h
  | cons k' v' rest ih =>
      simp only [slookup] at h
      by_cases hk : k == k'
      · simp only [hk, if_true, Option.some.injEq] at h
        subst h
        simp only [sdictSize]; omega
      · simp only [hk] at h
        have := ih h
        simp only [sdictSize]; omega

-- ===================================================================== --
-- §10.5 — THE WRITE HALF (Lever 1): `pput` (Map.set over the assoc list)   --
--   + `pappend` (list construct/append), with the characterizing law pack. --
--   Co-lands with the WhyML `pput`/`pappend` promoted into the emitter      --
--   preamble; certifies (NO 4th axiom) the laws the Lever-1 spike proved.   --
-- ===================================================================== --

/-- `pput` — total structural Map.set: replace the value if the key is
    present, else cons the new binding.  Realizability (totality) justifies
    the WhyML program `val pput_prog ... ensures {result = pput ...}` wrapper. -/
def pput : PyDict → IrKey → PyVal → PyDict
  | [], k, v => [(k, v)]
  | (k', v') :: rest, k, v =>
      if k == k' then (k, v) :: rest else (k', v') :: pput rest k v

/-- (W1) write-then-read the SAME key returns the written value. -/
theorem get_pput_same (d : PyDict) (k : IrKey) (v : PyVal) :
    get (pput d k v) k = some v := by
  induction d with
  | nil => simp [pput, get]
  | cons hd rest ih =>
      obtain ⟨k', v'⟩ := hd
      simp only [pput]
      by_cases hk : k == k'
      · simp [get, hk]
      · simp only [hk, if_false, Bool.false_eq_true]
        simp only [get, hk, if_false, Bool.false_eq_true]
        exact ih

/-- (W2) a write at `k` does not disturb any OTHER key's binding. -/
theorem get_pput_other (d : PyDict) (k k2 : IrKey) (v : PyVal) (hne : k2 ≠ k) :
    get (pput d k v) k2 = get d k2 := by
  induction d with
  | nil =>
      simp only [pput, get]
      have : ¬ (k2 == k) := by simpa using hne
      simp [this]
  | cons hd rest ih =>
      obtain ⟨k', v'⟩ := hd
      simp only [pput]
      by_cases hk : k == k'
      · simp only [hk, if_true]
        have hkk : k = k' := by simpa using hk
        subst hkk
        simp only [get]
        have hnk : ¬ (k2 == k) := by simpa using hne
        simp only [hnk, if_false, Bool.false_eq_true]
      · simp only [hk, if_false, Bool.false_eq_true]
        simp only [get]
        by_cases hk2 : k2 == k'
        · simp only [hk2, if_true]
        · simp only [hk2, if_false, Bool.false_eq_true]
          exact ih

/-- (W3) the key is a member after a write. -/
theorem mem_pput_same (d : PyDict) (k : IrKey) (v : PyVal) :
    memKey (pput d k v) k = true := by
  induction d with
  | nil => simp [pput, memKey]
  | cons hd rest ih =>
      obtain ⟨k', v'⟩ := hd
      simp only [pput]
      by_cases hk : k == k'
      · simp [memKey, hk]
      · simp only [hk, if_false, Bool.false_eq_true]
        simp [memKey, hk, ih]

/-- (W4) SIZE composition: a write grows the dict by at most `size v + 1`. -/
theorem size_dict_pput (d : PyDict) (k : IrKey) (v : PyVal) :
    sizeDict (pput d k v) ≤ sizeDict d + size v + 1 := by
  induction d with
  | nil => simp only [pput, sizeDict]; omega
  | cons hd rest ih =>
      obtain ⟨k', v'⟩ := hd
      simp only [pput]
      by_cases hk : k == k'
      · simp only [hk, if_true, sizeDict]; omega
      · simp only [hk, if_false, Bool.false_eq_true, sizeDict]; omega

/-- `pappend` — list construct/append (d.append / insert-at-end). -/
def pappend : List PyVal → PyVal → List PyVal
  | [], x => [x]
  | h :: t, x => h :: pappend t x

/-- (W5) append adds exactly one cell of weight `1 + size x`. -/
theorem size_list_pappend (l : List PyVal) (x : PyVal) :
    sizeList (pappend l x) = sizeList l + size x + 1 := by
  induction l with
  | nil => simp only [pappend, sizeList]; omega
  | cons h t ih => simp only [pappend, sizeList, ih]; omega

/-- (W6) the appended element is a member of the result. -/
theorem mem_pappend (l : List PyVal) (x : PyVal) : x ∈ pappend l x := by
  induction l with
  | nil => simp [pappend]
  | cons h t ih => simp [pappend]; exact Or.inr ih

end PyValDict

-- ===================================================================== --
-- VERDICT — axiom audit. Only the 3 standard Lean kernel axioms may       --
--   appear; NO 4th, extension-specific axiom (ledger intact, +0).         --
-- ===================================================================== --

#print axioms PyValDict.get_pput_same
#print axioms PyValDict.get_pput_other
#print axioms PyValDict.mem_pput_same
#print axioms PyValDict.size_dict_pput
#print axioms PyValDict.size_list_pappend
#print axioms PyValDict.mem_pappend
#print axioms PyValDict.key_roundtrip
#print axioms PyValDict.stringOfKey_inj
#print axioms PyValDict.get_hit_head
#print axioms PyValDict.get_some_mem
#print axioms PyValDict.size_pos
#print axioms PyValDict.size_dict_mem
#print axioms PyValDict.wfIr_binds
#print axioms PyValDict.render_cat_assoc
#print axioms PyValDict.render_nil_left
#print axioms PyValDict.render_nil_right
#print axioms PyValDict.slookup_hit_head
#print axioms PyValDict.slookup_some_smem
#print axioms PyValDict.size_slookup_mem
