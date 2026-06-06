/-
  unix-filesystem/UnixInodeFileSystem.proofs/lean/UnixInodeFileSystem.lean

  Lean 4 twin of ../rocq/UnixInodeFileSystem.v. Proves the theorems cited by
  `#@ proof lean` directives in ../../UnixInodeFileSystem.py.

  The witness functions are defined at TOP LEVEL with the SAME symbol names as
  the Module 6 `_AXIOM_REGISTRY` (`bit_and`, `struct_pack_iN`,
  `struct_unpack_iN`) and over `Int` (matching the registry's `int`), so the
  proof-statement cross-check (`bin/check-proof-crosscheck.sh`) sees identical
  symbols and types across Rocq, Lean, and the registry. The cited theorems
  live in the `UnixFs.{Bitmap,Struct.iN}` namespaces.

  No `sorry`, no extra axioms (core Lean 4 only — no mathlib).
-/

-- --- Top-level witness functions (names/types match the registry) ---

/-- Bitwise AND over `Int`, via the `Nat` operation on the magnitudes. -/
def bit_and (x y : Int) : Int := ((x.toNat &&& y.toNat : Nat) : Int)

def struct_pack_i1a1 (_fmt : Int) (x0 : Int) (x1 : List Int) : List Int := x0 :: x1
def struct_unpack_i1a1 (_fmt : Int) (data : List Int) : Int × List Int :=
  match data with
  | h :: rest => (h, rest)
  | []        => (0, [])

def struct_pack_i2 (_fmt x0 x1 : Int) : List Int := [x0, x1]
def struct_unpack_i2 (_fmt : Int) (data : List Int) : Int × Int :=
  match data with
  | x0 :: x1 :: _ => (x0, x1)
  | _ => (0, 0)

def struct_pack_i18 (_fmt x0 x1 x2 x3 x4 x5 x6 x7 x8 x9
                          x10 x11 x12 x13 x14 x15 x16 x17 : Int) : List Int :=
  [x0, x1, x2, x3, x4, x5, x6, x7, x8,
   x9, x10, x11, x12, x13, x14, x15, x16, x17]
def struct_unpack_i18 (_fmt : Int) (data : List Int) :
    Int × Int × Int × Int × Int × Int × Int × Int × Int ×
    Int × Int × Int × Int × Int × Int × Int × Int × Int :=
  match data with
  | x0 :: x1 :: x2 :: x3 :: x4 :: x5 :: x6 :: x7 :: x8 ::
    x9 :: x10 :: x11 :: x12 :: x13 :: x14 :: x15 :: x16 :: x17 :: _ =>
      (x0, x1, x2, x3, x4, x5, x6, x7, x8,
       x9, x10, x11, x12, x13, x14, x15, x16, x17)
  | _ => (0, 0, 0, 0, 0, 0, 0, 0, 0,
          0, 0, 0, 0, 0, 0, 0, 0, 0)

-- --- Cited theorems (qualnames match the `#@ proof lean` directives) ---

namespace UnixFs.Bitmap

theorem bit_and_one_in_zero_one (n : Int) : 0 ≤ bit_and n 1 ∧ bit_and n 1 < 2 := by
  unfold bit_and
  have hle : n.toNat &&& (1 : Int).toNat ≤ 1 := Nat.and_le_right
  omega

end UnixFs.Bitmap

namespace UnixFs.Struct.i1a1
theorem round_trip (fmt x0 : Int) (x1 : List Int) :
    struct_unpack_i1a1 fmt (struct_pack_i1a1 fmt x0 x1) = (x0, x1) := rfl
end UnixFs.Struct.i1a1

namespace UnixFs.Struct.i2
theorem round_trip (fmt x0 x1 : Int) :
    struct_unpack_i2 fmt (struct_pack_i2 fmt x0 x1) = (x0, x1) := rfl
end UnixFs.Struct.i2

namespace UnixFs.Struct.i18
theorem round_trip (fmt x0 x1 x2 x3 x4 x5 x6 x7 x8 x9
                        x10 x11 x12 x13 x14 x15 x16 x17 : Int) :
    struct_unpack_i18 fmt (struct_pack_i18 fmt x0 x1 x2 x3 x4 x5 x6 x7 x8 x9
                             x10 x11 x12 x13 x14 x15 x16 x17)
    = (x0, x1, x2, x3, x4, x5, x6, x7, x8,
       x9, x10, x11, x12, x13, x14, x15, x16, x17) := rfl
end UnixFs.Struct.i18
