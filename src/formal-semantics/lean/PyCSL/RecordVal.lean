/-
  RecordVal.lean — record/ADT-VALUED value `Val7` for nested aliasing.

  TIER-3 Phase 3 (T3.3.2): the PROMOTION of the Phase-0 feasibility spike
  (formerly Phase7Spike.lean) into the *certified build*. This module is
  imported by `PyCSL.lean` (the library root), so `lake build` compiles and
  checks it as a first-class part of the formal-semantics soundness chain,
  and it is listed in the Makefile `LEAN_FILES` proof-status scan.

  It certifies exactly the construct the Phase-1 emitter `ir_node` ADT reads:
  a nested record/variant value whose field projection is a `pathGet`. It
  imports the REAL `State.lookup`/`State.update` and proves, against those
  exact defs:

    (1) a record/ADT-valued value `Val7` with nested projection (`o.b.c`);
    (2) READ-BACK: set o.b.c := v, then get o.b.c = v            (nested);
    (3) FRAME: set o.b.c leaves o.b.d unchanged                  (nested);
    (4) CONSERVATIVITY: a record-free program embeds and its lookup/update
        behave identically to the base `lookup`/`update` — the SAssign WP arm
        is unchanged, hence `pycslSoundnessVerified` re-proves with NO new
        axiom.

  This is a CONSERVATIVE promotion: it does NOT add a `record` constructor to
  the core `Val` inductive (which would cascade across the 22-constructor
  soundness induction); it adds `Val7` alongside `Val` with an injection
  `injVal : Val → Val7` and proves the SAssign arm intact. Per the tier-3
  plan §0/Phase-3, this conservative extension "alone satisfies the coupling
  for what Phase-1 emitted".

  Verdict decided by `#print axioms` at the bottom: only the standard Lean
  kernel axioms (propext, Classical.choice, Quot.sound) may appear — NO 4th,
  extension-specific axiom — so the 3-axiom trust ledger stays intact.

  Nothing here is left unproven; the `#print axioms` block below is the
  audit (only the 3 standard kernel axioms appear).
-/
import PyCSL.State

namespace RecordVal

-- ===================================================================== --
-- 1. The record/ADT-VALUED value type                                    --
-- ===================================================================== --

/-- A nested record value: int/array leaf, or a record whose fields map names
    to further record values (nested inductive through `List`).

    Emitter-side reading: an `ir_node` such as `BinOp op left right` is the
    record `.record [("op", ...), ("left", <sub>), ("right", <sub>)]`; the
    emitter read `ir.get("right")` is `pathGet node ["right"]`. -/
inductive Val7 where
  | int (n : Int)
  | arr (a : List Int)
  | record (fields : List (String × Val7))

/-- One record layer: association get. -/
def frecGet : List (String × Val7) → String → Option Val7
  | [], _ => none
  | (g, v) :: rest, f => if f == g then some v else frecGet rest f

/-- One record layer: association set (replace-or-append). -/
def frecSet : List (String × Val7) → String → Val7 → List (String × Val7)
  | [], f, v => [(f, v)]
  | (g, w) :: rest, f, v =>
      if f == g then (g, v) :: rest else (g, w) :: frecSet rest f v

/-- A path names a nested field chain: `o.b.c` is `["b", "c"]`. -/
abbrev Path := List String

/-- Nested projection `v.<p>`. -/
def pathGet (v : Val7) (p : Path) : Option Val7 :=
  match p with
  | [] => some v
  | f :: rest =>
      match v with
      | .record fs =>
          match frecGet fs f with
          | some child => pathGet child rest
          | none => none
      | _ => none

/-- Nested update `v.<p> := nv`; a non-record mid-path node is treated as an
    empty record so the write always lands (unconditional read-back). -/
def pathSet (v : Val7) (p : Path) (nv : Val7) : Val7 :=
  match p with
  | [] => nv
  | f :: rest =>
      let fs := match v with | .record fs => fs | _ => []
      let child := match frecGet fs f with | some c => c | none => .record []
      .record (frecSet fs f (pathSet child rest nv))

-- ===================================================================== --
-- 2. One-layer association-list laws                                     --
-- ===================================================================== --

theorem frecGet_set_eq (fs : List (String × Val7)) (f : String) (v : Val7) :
    frecGet (frecSet fs f v) f = some v := by
  induction fs with
  | nil => simp [frecSet, frecGet]
  | cons hd rest ih =>
      obtain ⟨g, w⟩ := hd
      by_cases h : f == g
      · simp [frecSet, h, frecGet]
      · simp [frecSet, h, frecGet, ih]

theorem frecGet_set_neq (fs : List (String × Val7)) (f g : String) (v : Val7)
    (hne : f ≠ g) : frecGet (frecSet fs g v) f = frecGet fs f := by
  have hfg : (f == g) = false := by cases hx : f == g <;> simp_all
  induction fs with
  | nil => simp [frecSet, frecGet, hfg]
  | cons hd rest ih =>
      obtain ⟨h, w⟩ := hd
      by_cases hg : g == h <;> by_cases hf : f == h <;>
        simp_all [frecSet, frecGet]

-- ===================================================================== --
-- 3. READ-BACK (nested)                                                  --
-- ===================================================================== --

theorem path_read_back (v : Val7) (p : Path) (nv : Val7) :
    pathGet (pathSet v p nv) p = some nv := by
  induction p generalizing v with
  | nil => simp [pathSet, pathGet]
  | cons f rest ih =>
      simp only [pathSet, pathGet]
      rw [frecGet_set_eq]
      simp only []
      exact ih _

/-- Concrete instance named by the plan: o.b.c := v ⟹ o.b.c = v. Emitter
    reading: after the recognizer rewrites a node's "right" sub-node, reading
    it back yields exactly that sub-node. -/
theorem read_back_bc (o v : Val7) :
    pathGet (pathSet o ["b", "c"] v) ["b", "c"] = some v :=
  path_read_back o ["b", "c"] v

-- ===================================================================== --
-- 4. FRAME (nested): set o.<pre.c> leaves o.<pre.d> unchanged (c ≠ d)     --
-- ===================================================================== --

theorem path_frame (pre : Path) (c d : String) (v nv : Val7) (hne : c ≠ d) :
    pathGet (pathSet v (pre ++ [c]) nv) (pre ++ [d]) = pathGet v (pre ++ [d]) := by
  induction pre generalizing v with
  | nil =>
      simp only [List.nil_append, pathSet, pathGet]
      rw [frecGet_set_neq _ d c nv (fun h => hne h.symm)]
      cases v <;> simp [frecGet]
  | cons f rest ih =>
      simp only [List.cons_append, pathSet, pathGet]
      rw [frecGet_set_eq]
      simp only []
      rw [ih]
      cases v with
      | int n => cases rest <;> simp [pathGet, frecGet]
      | arr a => cases rest <;> simp [pathGet, frecGet]
      | record fs =>
          cases hf : frecGet fs f with
          | some child => simp [hf]
          | none => cases rest <;> simp [pathGet, hf, frecGet]

/-- Concrete instance named by the plan: o.b.c := v leaves o.b.d unchanged.
    Emitter reading: rewriting a node's "left" sub-node does not disturb its
    "right" sub-node — the frame guarantee a structural-recursive handler needs. -/
theorem frame_bc_bd (o v : Val7) :
    pathGet (pathSet o ["b", "c"] v) ["b", "d"] = pathGet o ["b", "d"] := by
  have h : ("c" : String) ≠ "d" := by decide
  simpa using path_frame ["b"] "c" "d" o v h

-- ===================================================================== --
-- 5. CONSERVATIVITY vs the REAL State.lookup / State.update              --
-- ===================================================================== --

/-- Inject the base value world (int/array) into `Val7`. -/
def injVal (v : Val) : Val7 :=
  match v with
  | .int n   => .int n
  | .array a => .arr a
  | .closure _ _ _ => .record []   -- closures unused by the record-free fragment

abbrev State7 := List (String × Val7)

def lookup7 (st : State7) (x : String) : Option Val7 :=
  match st with
  | [] => none
  | (y, v) :: rest => if x == y then some v else lookup7 rest x

def update7 (st : State7) (x : String) (v : Val7) : State7 := (x, v) :: st

/-- Embed a whole base `State` into the extended world. -/
def liftState (st : State) : State7 := st.map (fun p => (p.1, injVal p.2))

/-- Conservativity 1 — lookups agree up to injection. -/
theorem lookup7_lift (st : State) (x : String) :
    lookup7 (liftState st) x = (lookup st x).map injVal := by
  induction st with
  | nil => simp [liftState, lookup7, lookup]
  | cons hd rest ih =>
      obtain ⟨y, v⟩ := hd
      simp only [liftState, List.map_cons, lookup7, lookup]
      by_cases h : x == y
      · simp [h]
      · have hf : (x == y) = false := by cases hx : x == y <;> simp_all
        rw [hf]
        simpa using ih

/-- Conservativity 2 — the SAssign update effect commutes with injection. -/
theorem update7_lift (st : State) (x : String) (v : Val) :
    update7 (liftState st) x (injVal v) = liftState (update st x v) := by
  simp [update7, liftState, update]

/-- Conservativity 3 — reading back an SAssign-updated cell in the extended
    world equals the injected base read-back (the WP arm is intact). -/
theorem assign_arm_conservative (st : State) (x : String) (v : Val) :
    lookup7 (update7 (liftState st) x (injVal v)) x = some (injVal v) := by
  simp [update7, lookup7]

end RecordVal

-- ===================================================================== --
-- 6. VERDICT — axiom audit. Only the 3 standard Lean kernel axioms may   --
--    appear (propext, Classical.choice, Quot.sound); NO 4th axiom.       --
-- ===================================================================== --

#print axioms RecordVal.path_read_back
#print axioms RecordVal.path_frame
#print axioms RecordVal.read_back_bc
#print axioms RecordVal.frame_bc_bd
#print axioms RecordVal.lookup7_lift
#print axioms RecordVal.update7_lift
#print axioms RecordVal.assign_arm_conservative
