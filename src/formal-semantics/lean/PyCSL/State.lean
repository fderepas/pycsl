/-
  State.lean — Values, state, ghost state, and evaluators
  Mirror of Phase2_State.v (all phases).
-/
import PyCSL.AST

inductive Val where
  | int     (n : Int)
  | array   (a : List Int)
  /-- Phase 8 — Lambda (Category A, optional).
      `.closure param body closure` is the reified closure value of a
      lambda: it captures the defining state `closure` so that `.call`
      can later execute `body` in `closure[param -> argval]`. The captured
      state is a plain `List (Ident × Val)` (regState only); ghost and
      label snapshots are not captured by this minimal model. This is the
      defunctionalized closure representation (no WhyML function value). -/
  | closure (param : Ident) (body : Stmt) (closure : List (Ident × Val))
  deriving Repr

abbrev State := List (Ident × Val)

def lookup (st : State) (x : Ident) : Option Val :=
  match st with
  | [] => none
  | (y, v) :: rest => if x == y then some v else lookup rest x

def update (st : State) (x : Ident) (v : Val) : State := (x, v) :: st

def arrayUpdate (st : State) (arr : Ident) (i : Int) (v : Int) : State :=
  match lookup st arr with
  | some (.array a) =>
    let idx := i.toNat
    if 0 ≤ i ∧ i < a.length then
      let a' := a.take idx ++ [v] ++ a.drop (idx + 1)
      update st arr (.array a')
    else st
  | _ => st

-- ===== Phase 1 helper functions =====

def sumListFrom (a : List Int) (idx count : Nat) : Int :=
  match count with
  | 0     => 0
  | n + 1 => a.getD idx 0 + sumListFrom a (idx + 1) n

def sumListRange (a : List Int) (lo hi : Nat) : Int :=
  if lo < hi then sumListFrom a lo (hi - lo) else 0

def sortedListFrom (a : List Int) (lo count : Nat) : Prop :=
  match count with
  | 0 => True
  | n + 1 =>
    match n with
    | 0 => True
    | _ => a.getD lo 0 ≤ a.getD (lo + 1) 0 ∧ sortedListFrom a (lo + 1) n

def sortedListRange (a : List Int) (lo hi : Nat) : Prop :=
  if lo < hi then sortedListFrom a lo (hi - lo) else True

-- ===== Phase 3a: Ghost state =====

-- Phase 3b: all supported ghost types
inductive GhostVal where
  | int    (n : Int)
  | string (s : String)
  | array  (a : List Int)
  | list   (l : List Int)
  | dict   (d : List (Int × Int))   -- association-list model for ghost_dict
  | set    (s : List Int)            -- sorted-list model for ghost_set
  | tuple2 (a b : Int)
  | tuple3 (a b c : Int)
  | tuple4 (a b c d : Int)
  deriving Repr

abbrev GhostState := List (Ident × GhostVal)
abbrev LabelEnv   := List (Ident × GhostState)

def ghostLookup (gst : GhostState) (x : Ident) : Option GhostVal :=
  match gst with
  | [] => none
  | (y, v) :: rest => if x == y then some v else ghostLookup rest x

def ghostUpdate (gst : GhostState) (x : Ident) (v : GhostVal) : GhostState :=
  (x, v) :: gst

def labelLookup (lenv : LabelEnv) (l : Ident) : Option GhostState :=
  match lenv with
  | [] => none
  | (m, gst) :: rest => if l == m then some gst else labelLookup rest l

structure ExecState where
  regState   : State
  ghostSt    : GhostState
  labelSnaps : LabelEnv
  deriving Repr

def mkExecState (st : State) : ExecState :=
  { regState := st, ghostSt := [], labelSnaps := [] }

def setReg (es : ExecState) (st : State) : ExecState :=
  { es with regState := st }

def setGhost (es : ExecState) (gst : GhostState) : ExecState :=
  { es with ghostSt := gst }

def setLabels (es : ExecState) (lenv : LabelEnv) : ExecState :=
  { es with labelSnaps := lenv }

-- ===== Arithmetic =====

def evalBinopZ (op : Binop) (n1 n2 : Int) : Int :=
  match op with
  | .add => n1 + n2
  | .sub => n1 - n2
  | .mul => n1 * n2
  | .div => if n2 == 0 then 0 else n1 / n2
  | .mod_ => if n2 == 0 then 0 else n1 % n2

/-- Comparison evaluator: returns 0 (false) or 1 (true). -/
def evalCmpOpZ (op : CmpOp) (n1 n2 : Int) : Int :=
  let b := match op with
    | .eq => n1 == n2
    | .ne => n1 != n2
    | .lt => n1 < n2
    | .le => n1 ≤ n2
    | .gt => n1 > n2
    | .ge => n1 ≥ n2
  if b then 1 else 0

def evalExpr (st : State) : Expr → Val
  | .int n => .int n
  | .var x => (lookup st x).getD (.int 0)
  | .subscript arr i =>
    match lookup st arr, evalExpr st i with
    | some (.array a), .int n =>
      if 0 ≤ n ∧ n < a.length then .int (a.getD n.toNat 0)
      else .int 0
    | _, _ => .int 0
  | .len arr =>
    match lookup st arr with
    | some (.array a) => .int a.length
    | _ => .int 0
  | .binop op e1 e2 =>
    match evalExpr st e1, evalExpr st e2 with
    | .int n1, .int n2 => .int (evalBinopZ op n1 n2)
    | _, _ => .int 0
  | .neg e =>
    match evalExpr st e with
    | .int n => .int (-n)
    | v => v
  | .cmp op e1 e2 =>
    match evalExpr st e1, evalExpr st e2 with
    | .int n1, .int n2 => .int (evalCmpOpZ op n1 n2)
    | _, _ => .int 0
  | .fieldGet obj f =>
    -- Q4 U.4 (2026-05-29): name-flatten obj.f → "obj.f" lookup.
    (lookup st (obj ++ "." ++ f)).getD (.int 0)
  | .call _ _ =>
    -- Q4 U.4 (2026-05-29): generic call defaults to int 0.
    .int 0

def evalBool (st : State) (e : Expr) : Bool :=
  match evalExpr st e with
  | .int 0 => false
  | _ => true

-- Array membership helper for in_/notIn
def evalArrayIn (st preSt : State) (result : Option Val)
                (evalZ : State → State → Option Val → ContractExpr → Int)
                (elem container : ContractExpr) : Prop :=
  let v := evalZ st preSt result elem
  match container with
  | .var arr =>
    match lookup st arr with
    | some (.array a) => v ∈ a
    | _ => False
  | _ => False

-- ===== Phase 7 (Category D): Memory-model predicates (Hoare default) =====

/-- These top-level definitions are the Hoare-instance `valid`/`separated`
    (both `True`). `evalContract`'s `.cValid`/`.cSeparated` clauses call
    them, so the heap-dependent predicates are re-routed through a named
    MemModel surface rather than being inline `True`. `MemModel.lean`
    provides the `MemModel` class, the `HoareMM` instance (whose definitions
    are provably equal to these), and the new `TypedMM`/`StoreMM` instances
    with real heap predicates. `pycslSoundness` uses these Hoare defaults
    (unchanged). -/
def valid (ptr len : Int) : Prop := True
def separated (a b : Int) : Prop := True

mutual
  def evalZ (st preSt : State) (result : Option Val) : ContractExpr → Int
    | .int n => n
    | .var x => match lookup st x with | some (.int n) => n | _ => 0
    | .result => match result with | some (.int n) => n | _ => 0
    | .length arr =>
      match lookup st arr with
      | some (.array a) => a.length
      | _ => 0
    | .cLength2d arr =>
      -- Phase 4: \length2d — flat-array model: returns \length(arr).
      -- No 2D structure in Val.array (List Int); rows/cols elided.
      match lookup st arr with
      | some (.array a) => a.length
      | _ => 0
    | .subscript arr i =>
      let n := evalZ st preSt result i
      match lookup st arr with
      | some (.array a) =>
        if 0 ≤ n ∧ n < a.length then a.getD n.toNat 0
        else 0
      | _ => 0
    | .old e => evalZ preSt preSt result e
    | .binop op e1 e2 =>
      evalBinopZ op (evalZ st preSt result e1) (evalZ st preSt result e2)
    | .neg e => -(evalZ st preSt result e)
    -- Phase 1 additions
    | .chainedSubscript arr i _ =>
      let n := evalZ st preSt result i
      match lookup st arr with
      | some (.array a) =>
        if 0 ≤ n ∧ n < a.length then a.getD n.toNat 0
        else 0
      | _ => 0
    | .boolLit b => if b then 1 else 0
    | .noneLit => 0
    | .stringLit _ => 0
    | .sum arr lo hi =>
      let loZ := evalZ st preSt result lo
      let hiZ := evalZ st preSt result hi
      match lookup st arr with
      | some (.array a) => sumListRange a loZ.toNat hiZ.toNat
      | _ => 0
    | _ => 0

  def evalContract (st preSt : State) (result : Option Val) : ContractExpr → Prop
    | .int n => n ≠ 0
    | .var x => match lookup st x with | some (.int 0) => False | _ => True
    | .result => match result with | some (.int 0) => False | _ => True
    | .length _ => evalZ st preSt result (.length "") ≠ 0
    | .cLength2d arr => evalZ st preSt result (.cLength2d arr) ≠ 0
    | .subscript arr i => evalZ st preSt result (.subscript arr i) ≠ 0
    | .old e => evalZ st preSt result (.old e) ≠ 0
    | .binop op e1 e2 => evalZ st preSt result (.binop op e1 e2) ≠ 0
    | .neg e => evalZ st preSt result (.neg e) ≠ 0
    | .eq  e1 e2 => evalZ st preSt result e1 = evalZ st preSt result e2
    | .ne  e1 e2 => evalZ st preSt result e1 ≠ evalZ st preSt result e2
    | .lt  e1 e2 => evalZ st preSt result e1 < evalZ st preSt result e2
    | .le  e1 e2 => evalZ st preSt result e1 ≤ evalZ st preSt result e2
    | .gt  e1 e2 => evalZ st preSt result e1 > evalZ st preSt result e2
    | .ge  e1 e2 => evalZ st preSt result e1 ≥ evalZ st preSt result e2
    | .and e1 e2 => evalContract st preSt result e1 ∧ evalContract st preSt result e2
    | .or  e1 e2 => evalContract st preSt result e1 ∨ evalContract st preSt result e2
    | .not e => ¬ evalContract st preSt result e
    | .implies e1 e2 => evalContract st preSt result e1 → evalContract st preSt result e2
    | .iff e1 e2 => evalContract st preSt result e1 ↔ evalContract st preSt result e2
    | .forall_ x body =>
      ∀ n : Int, evalContract (update st x (.int n)) preSt result body
    | .exists_ x body =>
      ∃ n : Int, evalContract (update st x (.int n)) preSt result body
    -- Phase 1 additions
    | .boolLit b => b = true
    | .noneLit => False
    | .stringLit s => s ≠ ""
    | .isSorted arr lo hi =>
      let loZ := evalZ st preSt result lo
      let hiZ := evalZ st preSt result hi
      match lookup st arr with
      | some (.array a) => sortedListRange a loZ.toNat hiZ.toNat
      | _ => True
    | .in_ elem container =>
      let v := evalZ st preSt result elem
      match container with
      | .var arr => match lookup st arr with
                    | some (.array a) => v ∈ a
                    | _ => False
      | _ => False
    | .notIn elem container =>
      let v := evalZ st preSt result elem
      ¬ match container with
        | .var arr => match lookup st arr with
                      | some (.array a) => v ∈ a
                      | _ => False
        | _ => False
    -- Phase 4 — Category C library predicates (heap-dependent).
    -- \valid, \separated, \valid2d are heap-dependent; Phase 7 (memory-model
    -- parameterisation) re-routes \valid/\separated through the MemModel
    -- interface. The top-level `valid`/`separated` definitions below
    -- (Hoare instance: True) are what evalContract consults; alternative
    -- instances (TypedMM, StoreMM in MemModel.lean) provide real heap
    -- predicates but do NOT replace the Hoare default used by
    -- pycslSoundness. This mirrors how `criticalHavoc` is re-routed
    -- (WP.lean, defined in MemModel.lean). See MemModel.lean §"Design
    -- note (Option B)" for the compromise rationale. \valid2d remains
    -- True (no 2D heap model yet).
    | .cValid ptr len =>
      valid (evalZ st preSt result ptr) (evalZ st preSt result len)
    | .cSeparated a b =>
      separated (evalZ st preSt result a) (evalZ st preSt result b)
    | .cValid2d _ _ _ => True
    -- Phase 6 — class invariant: evaluate the predicate over current state.
    -- The className tag is documentation-only in the Hoare model; the
    -- Phase 7 record/heap instance will scope it to the named record.
    | .cClassInvariant _ inv => evalContract st preSt result inv
    | _ => True
    end

def evalVariant (st preSt : State) (e : ContractExpr) : Int :=
  evalZ st preSt none e

-- Ghost evaluator (integer expressions)
def evalGhostInt (es : ExecState) (e : GhostExpr) : Int :=
  evalZ es.regState es.regState none e

def applyAugOp (op : AugOp) (cur rhs : Int) : Int :=
  match op with
  | .add => cur + rhs
  | .sub => cur - rhs
  | .mul => cur * rhs

-- Phase 3b: typed ghost evaluators

-- Ghost list evaluator — CGNil/CGCons/CGAppend/CGTl → List Int
def evalGhostList (es : ExecState) : GhostExpr → List Int
  | .cgNil          => []
  | .cgCons h t     => evalGhostInt es h :: evalGhostList es t
  | .cgAppend l1 l2 => evalGhostList es l1 ++ evalGhostList es l2
  | .cgTl l         => (evalGhostList es l).tail
  | .var x          => match ghostLookup es.ghostSt x with | some (.list l) => l | _ => []
  | _               => []

-- Sorted-list helpers for ghost_set model
def setAddZ (x : Int) : List Int → List Int
  | []      => [x]
  | h :: t  =>
    if x < h then x :: h :: t
    else if x == h then h :: t
    else h :: setAddZ x t

def setRemoveZ (x : Int) : List Int → List Int
  | []      => []
  | h :: t  => if x == h then t else h :: setRemoveZ x t

-- Ghost set evaluator — sorted-list model
def evalGhostSet (es : ExecState) : GhostExpr → List Int
  | .cgSetEmpty        => []
  | .cgSetAdd elem s   => setAddZ (evalGhostInt es elem) (evalGhostSet es s)
  | .cgSetRemove elem s => setRemoveZ (evalGhostInt es elem) (evalGhostSet es s)
  | .var x             => match ghostLookup es.ghostSt x with | some (.set s) => s | _ => []
  | _                  => []

-- Ghost dict evaluator — association-list model with map-set/remove support
def evalGhostDict (es : ExecState) : GhostExpr → List (Int × Int)
  | .cgMapEmpty         => []
  | .cgMapSet d k v     =>
    let dict := evalGhostDict es d
    let kk   := evalGhostInt es k
    let vv   := evalGhostInt es v
    (kk, vv) :: dict.filter (fun p => p.1 != kk)
  | .cgMapRemove d k    =>
    let dict := evalGhostDict es d
    let kk   := evalGhostInt es k
    dict.filter (fun p => p.1 != kk)
  | .var x              => match ghostLookup es.ghostSt x with | some (.dict d) => d | _ => []
  | _                   => []

-- Ghost string evaluator — concatenation and variable lookup
def evalGhostString (es : ExecState) : GhostExpr → String
  | .var x             => match ghostLookup es.ghostSt x with | some (.string s) => s | _ => ""
  | .cgStrConcat s1 s2 => evalGhostString es s1 ++ evalGhostString es s2
  | _                  => ""

-- Ghost tuple evaluators — evaluate expression as tuple components
def evalGhostTuple2 (es : ExecState) : GhostExpr → Int × Int
  | .cgMkTuple2 a b => (evalGhostInt es a, evalGhostInt es b)
  | .var x          => match ghostLookup es.ghostSt x with | some (.tuple2 a b) => (a, b) | _ => (0, 0)
  | _               => (0, 0)

def evalGhostTuple3 (es : ExecState) : GhostExpr → Int × Int × Int
  | .cgMkTuple3 a b c => (evalGhostInt es a, evalGhostInt es b, evalGhostInt es c)
  | .var x            => match ghostLookup es.ghostSt x with | some (.tuple3 a b c) => (a, b, c) | _ => (0, 0, 0)
  | _                 => (0, 0, 0)

def evalGhostTuple4 (es : ExecState) : GhostExpr → Int × Int × Int × Int
  | .cgMkTuple4 a b c d => (evalGhostInt es a, evalGhostInt es b, evalGhostInt es c, evalGhostInt es d)
  | .var x              => match ghostLookup es.ghostSt x with | some (.tuple4 a b c d) => (a, b, c, d) | _ => (0, 0, 0, 0)
  | _                   => (0, 0, 0, 0)

-- Typed ghost value evaluator — dispatches on GhostType
def evalGhostVal (t : GhostType) (es : ExecState) (e : GhostExpr) : GhostVal :=
  match t with
  | .int    => .int    (evalGhostInt es e)
  | .string => .string (evalGhostString es e)
  | .array  => .array  (evalGhostList es e)
  | .list   => .list   (evalGhostList es e)
  | .dict   => .dict   (evalGhostDict es e)
  | .set    => .set    (evalGhostSet es e)
  | .tuple2 => let (a, b)       := evalGhostTuple2 es e; .tuple2 a b
  | .tuple3 => let (a, b, c)    := evalGhostTuple3 es e; .tuple3 a b c
  | .tuple4 => let (a, b, c, d) := evalGhostTuple4 es e; .tuple4 a b c d

-- Typed augmented assignment for ghost values
def applyGhostAug (op : AugOp) (curOpt : Option GhostVal) (es : ExecState) (rhs : GhostExpr) : GhostVal :=
  let cur := curOpt.getD (.int 0)
  match cur with
  | .int n  => .int (applyAugOp op n (evalGhostInt es rhs))
  | .list l =>
    match op with
    | .add => .list (l ++ evalGhostList es rhs)
    | _    => .list l
  | .array a =>
    match op with
    | .add => .array (a ++ evalGhostList es rhs)
    | _    => .array a
  | .string s =>
    match op with
    | .add => .string (s ++ evalGhostString es rhs)
    | _    => .string s
  | .dict _ => .dict (evalGhostDict es rhs)
  | .set  _ => .set  (evalGhostSet  es rhs)
  | _ => cur

-- Phase 3d / 3.3 mutual: evalZEs and evalGhostListFull are mutually recursive
-- so that CGCons element heads are evaluated with full exec_state awareness.
mutual

def evalZEs (es preEs : ExecState) (result : Option Val) : ContractExpr → Int
  | .int n    => n
  | .var x    =>
    match lookup es.regState x with
    | some (.int n) => n
    | _ => match ghostLookup es.ghostSt x with | some (.int n) => n | _ => 0
  | .result   => match result with | some (.int n) => n | _ => 0
  | .length arr =>
    match lookup es.regState arr with
    | some (.array a) => a.length
    | _ => 0
  | .cLength2d arr =>
    -- Phase 4: \length2d — flat-array model: returns \length(arr).
    match lookup es.regState arr with
    | some (.array a) => a.length
    | _ => 0
  | .subscript arr i =>
    let n := evalZEs es preEs result i
    match lookup es.regState arr with
    | some (.array a) => if 0 ≤ n ∧ n < a.length then a.getD n.toNat 0 else 0
    | _ => 0
  | .old e    => evalZEs preEs preEs result e
  | .binop op e1 e2 =>
    evalBinopZ op (evalZEs es preEs result e1) (evalZEs es preEs result e2)
  | .neg e    => -(evalZEs es preEs result e)
  | .at_ e L  =>
    match labelLookup es.labelSnaps L with
    | some gst => evalZEs (setGhost es gst) preEs result e
    | none     => 0
  | .sum arr lo hi =>
    let loZ := evalZEs es preEs result lo
    let hiZ := evalZEs es preEs result hi
    match lookup es.regState arr with
    | some (.array a) => sumListRange a loZ.toNat hiZ.toNat
    | _ => 0
  -- Phase 3e: Tuple projections — cgMkTuple* + CVar lookup
  | .cgFst t  =>
    match t with
    | .cgMkTuple2 e1 _     => evalZEs es preEs result e1
    | .cgMkTuple3 e1 _ _   => evalZEs es preEs result e1
    | .cgMkTuple4 e1 _ _ _ => evalZEs es preEs result e1
    | .var x => match ghostLookup es.ghostSt x with
                | some (.tuple2 a _) => a | some (.tuple3 a _ _) => a
                | some (.tuple4 a _ _ _) => a | _ => 0
    | _ => 0
  | .cgSnd t  =>
    match t with
    | .cgMkTuple2 _ e2     => evalZEs es preEs result e2
    | .cgMkTuple3 _ e2 _   => evalZEs es preEs result e2
    | .cgMkTuple4 _ e2 _ _ => evalZEs es preEs result e2
    | .var x => match ghostLookup es.ghostSt x with
                | some (.tuple2 _ b) => b | some (.tuple3 _ b _) => b
                | some (.tuple4 _ b _ _) => b | _ => 0
    | _ => 0
  | .cgTrd t  =>
    match t with
    | .cgMkTuple3 _ _ e3   => evalZEs es preEs result e3
    | .cgMkTuple4 _ _ e3 _ => evalZEs es preEs result e3
    | .var x => match ghostLookup es.ghostSt x with
                | some (.tuple3 _ _ c) => c | some (.tuple4 _ _ c _) => c | _ => 0
    | _ => 0
  | .cgFth t  =>
    match t with
    | .cgMkTuple4 _ _ _ e4 => evalZEs es preEs result e4
    | .var x => match ghostLookup es.ghostSt x with
                | some (.tuple4 _ _ _ d) => d | _ => 0
    | _ => 0
  -- Phase 3e: List/set/string sizes — full expression support
  | .cgListLen l => (evalGhostList es l).length
  | .cgSetCard s => (evalGhostSet  es s).length
  | .cgStrLen s  => (evalGhostString es s).length
  -- Phase 3e: Ghost list element access — full ghost_state awareness for heads
  | .cgNth l i =>
    let idx := evalZEs es preEs result i
    let lst := evalGhostListFull es preEs result l
    if 0 ≤ idx ∧ idx < lst.length then lst.getD idx.toNat 0 else 0
  | e => evalZ es.regState preEs.regState result e
  termination_by e => sizeOf e

def evalGhostListFull (es preEs : ExecState) (result : Option Val) : ContractExpr → List Int
  | .cgNil          => []
  | .cgCons h t     => evalZEs es preEs result h :: evalGhostListFull es preEs result t
  | .cgAppend l1 l2 => evalGhostListFull es preEs result l1 ++ evalGhostListFull es preEs result l2
  | .cgTl l         => (evalGhostListFull es preEs result l).tail
  | .var x          => match ghostLookup es.ghostSt x with | some (.list l) => l | _ => []
  | _               => []
  termination_by e => sizeOf e

end

-- Phase 3c: exec_state-aware contract evaluator (CAt support)
-- Handles CAt by looking up label snapshots in es.labelSnaps.
-- Phase 3d: comparison operators use evalZEs for ghost-state-aware arithmetic.
def evalContractEs (es preEs : ExecState) (result : Option Val) : ContractExpr → Prop
  | .at_ expr L =>
    match labelLookup es.labelSnaps L with
    | some gst => evalContractEs (setGhost es gst) preEs result expr
    | none     => True
  | .and e1 e2 =>
    evalContractEs es preEs result e1 ∧ evalContractEs es preEs result e2
  | .or  e1 e2 =>
    evalContractEs es preEs result e1 ∨ evalContractEs es preEs result e2
  | .not e'     => ¬ evalContractEs es preEs result e'
  | .implies e1 e2 =>
    evalContractEs es preEs result e1 → evalContractEs es preEs result e2
  | .iff e1 e2 =>
    evalContractEs es preEs result e1 ↔ evalContractEs es preEs result e2
  | .forall_ x body =>
    ∀ n : Int, evalContractEs (setReg es (update es.regState x (.int n))) preEs result body
  | .exists_ x body =>
    ∃ n : Int, evalContractEs (setReg es (update es.regState x (.int n))) preEs result body
  | .var x =>
    match lookup es.regState x with
    | some (.int 0) => False
    | some _        => True
    | none          =>
      match ghostLookup es.ghostSt x with
      | some (.int 0) => False
      | some _        => True
      | none          => True
  -- Phase 3d: arithmetic truth cases use evalZEs
  | .int n           => n ≠ 0
  | .result          => match result with | some (.int 0) => False | _ => True
  | .length arr      => evalZEs es preEs result (.length arr) ≠ 0
  | .cLength2d arr   => evalZEs es preEs result (.cLength2d arr) ≠ 0
  | .subscript arr i => evalZEs es preEs result (.subscript arr i) ≠ 0
  | .old e'          => evalZEs es preEs result (.old e') ≠ 0
  | .binop op e1 e2  => evalZEs es preEs result (.binop op e1 e2) ≠ 0
  | .neg e'          => evalZEs es preEs result (.neg e') ≠ 0
  -- Phase 3d: comparison operators use evalZEs for ghost-state awareness
  | .eq  e1 e2 => evalZEs es preEs result e1 = evalZEs es preEs result e2
  | .ne  e1 e2 => evalZEs es preEs result e1 ≠ evalZEs es preEs result e2
  | .lt  e1 e2 => evalZEs es preEs result e1 < evalZEs es preEs result e2
  | .le  e1 e2 => evalZEs es preEs result e1 ≤ evalZEs es preEs result e2
  | .gt  e1 e2 => evalZEs es preEs result e1 > evalZEs es preEs result e2
  | .ge  e1 e2 => evalZEs es preEs result e1 ≥ evalZEs es preEs result e2
  | e => evalContract es.regState preEs.regState result e

-- Exec-state lifted evaluators (Phase 3c: evalC uses evalContractEs for CAt support)
def evalC (es preEs : ExecState) (result : Option Val) (e : ContractExpr) : Prop :=
  evalContractEs es preEs result e

def evalV (es preEs : ExecState) (e : ContractExpr) : Int :=
  evalZ es.regState preEs.regState none e
