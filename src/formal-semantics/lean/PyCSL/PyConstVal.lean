/-
  PyConstVal.lean — axiom-free certificate for the `pyconst_val` value-variant
  ADT (self-tcb-reduction M5, B-bucket).  The Lean twin of
  `rocq/Phase2c_PyConstVal.v`.

  CO-LANDING COUPLING (the tier-3 rule, cf. RecordVal.lean / PyValDict.lean):
  the WhyML `pyconst_val` theory promoted into the emitter preamble
  (`module6_whyml/preamble.py::_emit_exprir_theory`) is a NEW value shape — the
  discriminated union of the Python constant scalar kinds an `ast.Constant`
  node's `.value` field holds — so it lands with a proof, not a trusted
  assumption.  Certified here, against pure inductive datatypes with NO axiom,
  is exactly what `_py_expr_constant` relies on when lowering `expr.value is
  None` / `isinstance(expr.value, bool/str/int/bytes/complex)` / `expr.value is
  ...`:

    (a) the abstraction map `abs : PyScalar → PyConstVal` is TOTAL, INJECTIVE
        (hence injective per kind), and SURJECTIVE onto the ADT;
    (b) each `isPv*` discriminant AGREES with the matching Python `isinstance` /
        `is None` / `is ...` test;
    (c) each `pv*Of` projector is EXACT on its own variant, directly and via `abs`.

  The WhyML `PVComplex real` payload is abstracted by a type variable `ρ` (Lean's
  `Real` pulls in mathlib) — the structural facts hold for ANY payload, `real`
  included.  The abstract WhyML `val`s `bytes_content_comp` / `real_trunc` are
  not certified here: `real_trunc` is pinned by `ensures` to Why3 stdlib
  `truncate`; `bytes_content_comp`'s content law is an in-WhyML assumed spec
  (non-vacuous by `IrNum` injectivity).

  Verdict decided by `#print axioms` at the bottom: only the standard Lean kernel
  axioms (propext, Classical.choice, Quot.sound) may appear — NO 4th,
  extension-specific axiom — so the 3-axiom trust ledger stays intact.  Nothing
  here is left unproven.
-/

namespace PyConstValCert

-- ===================================================================== --
-- 1. The value-variant ADT — mirrors the WhyML `type pyconst_val`.       --
-- ===================================================================== --

/-- `ρ` abstracts the WhyML `PVComplex real` payload (see header). -/
inductive PyConstVal (ρ : Type) where
  | PVNone
  | PVBool (b : Bool)
  | PVInt (n : Int)
  | PVStr (s : String)
  | PVBytes (bs : List Int)
  | PVComplex (r : ρ)
  | PVEllipsis

variable {ρ : Type}

/-- Discriminants — images of the WhyML `is_pv*` match bodies. -/
def isPvnone : PyConstVal ρ → Bool | .PVNone => true | _ => false
def isPvbool : PyConstVal ρ → Bool | .PVBool _ => true | _ => false
def isPvint : PyConstVal ρ → Bool | .PVInt _ => true | _ => false
def isPvstr : PyConstVal ρ → Bool | .PVStr _ => true | _ => false
def isPvbytes : PyConstVal ρ → Bool | .PVBytes _ => true | _ => false
def isPvcomplex : PyConstVal ρ → Bool | .PVComplex _ => true | _ => false
def isPvellipsis : PyConstVal ρ → Bool | .PVEllipsis => true | _ => false

/-- Total projectors — images of the WhyML `pv*_of`, SAME defaults. -/
def pvboolOf : PyConstVal ρ → Bool | .PVBool b => b | _ => false
def pvintOf : PyConstVal ρ → Int | .PVInt n => n | _ => 0
def pvstrOf : PyConstVal ρ → String | .PVStr s => s | _ => ""
def pvbytesOf : PyConstVal ρ → List Int | .PVBytes bs => bs | _ => []
def pvrealOf [Inhabited ρ] : PyConstVal ρ → ρ | .PVComplex r => r | _ => default

-- ===================================================================== --
-- 2. The Python constant-scalar world + its isinstance / is-None tests.   --
-- ===================================================================== --

inductive PyScalar (ρ : Type) where
  | SNone
  | SBool (b : Bool)
  | SInt (n : Int)
  | SStr (s : String)
  | SBytes (bs : List Int)
  | SComplex (r : ρ)
  | SEllipsis

/-- Python's runtime type tests. `SBool`/`SInt` are DISJOINT — matching the
    emitter's branch order (`isinstance(x, bool)` before the int fall-through),
    so a Python bool never reaches the `PVInt` arm. -/
def pyIsNone : PyScalar ρ → Bool | .SNone => true | _ => false
def pyIsBool : PyScalar ρ → Bool | .SBool _ => true | _ => false
def pyIsInt : PyScalar ρ → Bool | .SInt _ => true | _ => false
def pyIsStr : PyScalar ρ → Bool | .SStr _ => true | _ => false
def pyIsBytes : PyScalar ρ → Bool | .SBytes _ => true | _ => false
def pyIsComplex : PyScalar ρ → Bool | .SComplex _ => true | _ => false
def pyIsEllipsis : PyScalar ρ → Bool | .SEllipsis => true | _ => false

/-- The abstraction map: a Python constant scalar to its ADT variant. -/
def abs : PyScalar ρ → PyConstVal ρ
  | .SNone      => .PVNone
  | .SBool b    => .PVBool b
  | .SInt n     => .PVInt n
  | .SStr s     => .PVStr s
  | .SBytes bs  => .PVBytes bs
  | .SComplex r => .PVComplex r
  | .SEllipsis  => .PVEllipsis

-- ===================================================================== --
-- 3. (a) `abs` is total + injective (per kind) + surjective.             --
-- ===================================================================== --

theorem abs_injective : Function.Injective (abs (ρ := ρ)) := by
  intro x y h
  cases x <;> cases y <;> simp_all [abs]

theorem abs_surjective : ∀ v : PyConstVal ρ, ∃ s, abs s = v := by
  intro v
  cases v with
  | PVNone => exact ⟨.SNone, rfl⟩
  | PVBool b => exact ⟨.SBool b, rfl⟩
  | PVInt n => exact ⟨.SInt n, rfl⟩
  | PVStr s => exact ⟨.SStr s, rfl⟩
  | PVBytes bs => exact ⟨.SBytes bs, rfl⟩
  | PVComplex r => exact ⟨.SComplex r, rfl⟩
  | PVEllipsis => exact ⟨.SEllipsis, rfl⟩

-- ===================================================================== --
-- 4. (b) each `isPv*` AGREES with the matching Python type test.         --
-- ===================================================================== --

theorem isPvnone_agree (s : PyScalar ρ) : isPvnone (abs s) = pyIsNone s := by
  cases s <;> rfl
theorem isPvbool_agree (s : PyScalar ρ) : isPvbool (abs s) = pyIsBool s := by
  cases s <;> rfl
theorem isPvint_agree (s : PyScalar ρ) : isPvint (abs s) = pyIsInt s := by
  cases s <;> rfl
theorem isPvstr_agree (s : PyScalar ρ) : isPvstr (abs s) = pyIsStr s := by
  cases s <;> rfl
theorem isPvbytes_agree (s : PyScalar ρ) : isPvbytes (abs s) = pyIsBytes s := by
  cases s <;> rfl
theorem isPvcomplex_agree (s : PyScalar ρ) : isPvcomplex (abs s) = pyIsComplex s := by
  cases s <;> rfl
theorem isPvellipsis_agree (s : PyScalar ρ) : isPvellipsis (abs s) = pyIsEllipsis s := by
  cases s <;> rfl

-- ===================================================================== --
-- 5. (c) each `pv*Of` is EXACT on its own variant (direct + via `abs`).  --
-- ===================================================================== --

theorem pvboolOf_exact (b : Bool) : pvboolOf (ρ := ρ) (.PVBool b) = b := rfl
theorem pvintOf_exact (n : Int) : pvintOf (ρ := ρ) (.PVInt n) = n := rfl
theorem pvstrOf_exact (s : String) : pvstrOf (ρ := ρ) (.PVStr s) = s := rfl
theorem pvbytesOf_exact (bs : List Int) : pvbytesOf (ρ := ρ) (.PVBytes bs) = bs := rfl
theorem pvrealOf_exact [Inhabited ρ] (r : ρ) : pvrealOf (.PVComplex r) = r := rfl

theorem pvboolOf_abs (b : Bool) : pvboolOf (abs (ρ := ρ) (.SBool b)) = b := rfl
theorem pvintOf_abs (n : Int) : pvintOf (abs (ρ := ρ) (.SInt n)) = n := rfl
theorem pvstrOf_abs (s : String) : pvstrOf (abs (ρ := ρ) (.SStr s)) = s := rfl
theorem pvbytesOf_abs (bs : List Int) : pvbytesOf (abs (ρ := ρ) (.SBytes bs)) = bs := rfl
theorem pvrealOf_abs [Inhabited ρ] (r : ρ) : pvrealOf (abs (.SComplex r)) = r := rfl

end PyConstValCert

-- ===================================================================== --
-- 6. VERDICT — axiom audit. Only the 3 standard Lean kernel axioms may   --
--    appear (propext, Classical.choice, Quot.sound); NO 4th axiom.       --
-- ===================================================================== --

#print axioms PyConstValCert.abs_injective
#print axioms PyConstValCert.abs_surjective
#print axioms PyConstValCert.isPvnone_agree
#print axioms PyConstValCert.isPvbool_agree
#print axioms PyConstValCert.isPvint_agree
#print axioms PyConstValCert.isPvstr_agree
#print axioms PyConstValCert.isPvbytes_agree
#print axioms PyConstValCert.isPvcomplex_agree
#print axioms PyConstValCert.isPvellipsis_agree
#print axioms PyConstValCert.pvboolOf_exact
#print axioms PyConstValCert.pvrealOf_exact
#print axioms PyConstValCert.pvboolOf_abs
#print axioms PyConstValCert.pvrealOf_abs
