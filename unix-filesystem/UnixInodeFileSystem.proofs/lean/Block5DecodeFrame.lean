/- Validation of UnixFs.Dir.block5_decode_frame (gap-13, Wall M) -- Lean 4
   mirror of ../rocq/Block5DecodeFrame.v.

   The decode-locality lemma: the abstract per-slot decode slot_inode/slot_name
   (disk, 5, k) reads ONLY the 32-byte dirent of slot k inside block 5's region
   [2560,3072). Two disks agreeing on every byte of [2560,3072) thus have
   identical block-5 decode at every slot k in [0,16). Modeled faithfully over
   an abstract byte reader rd with nameDecode taking the 30 name bytes
   explicitly; no funext, no induction.

   Verified under Lean 4.30.0 (core only, no Mathlib). No sorry. -/

namespace UnixFs
namespace Dir
section Scan

variable {byteDisk : Type} {nameT : Type}

def slotOff5 (k : Int) : Int := 2560 + 32 * k

def slotInode (rd : byteDisk → Int → Int) (d : byteDisk) (k : Int) : Int :=
  256 * (rd d (slotOff5 k)) + rd d (slotOff5 k + 1)

def slotName
    (rd : byteDisk → Int → Int)
    (nameDecode :
      Int→Int→Int→Int→Int→Int→Int→Int→Int→Int→Int→Int→Int→Int→Int→
      Int→Int→Int→Int→Int→Int→Int→Int→Int→Int→Int→Int→Int→Int→Int→ nameT)
    (d : byteDisk) (k : Int) : nameT :=
  nameDecode (rd d (slotOff5 k + 2)) (rd d (slotOff5 k + 3)) (rd d (slotOff5 k + 4)) (rd d (slotOff5 k + 5)) (rd d (slotOff5 k + 6)) (rd d (slotOff5 k + 7)) (rd d (slotOff5 k + 8)) (rd d (slotOff5 k + 9)) (rd d (slotOff5 k + 10)) (rd d (slotOff5 k + 11)) (rd d (slotOff5 k + 12)) (rd d (slotOff5 k + 13)) (rd d (slotOff5 k + 14)) (rd d (slotOff5 k + 15)) (rd d (slotOff5 k + 16)) (rd d (slotOff5 k + 17)) (rd d (slotOff5 k + 18)) (rd d (slotOff5 k + 19)) (rd d (slotOff5 k + 20)) (rd d (slotOff5 k + 21)) (rd d (slotOff5 k + 22)) (rd d (slotOff5 k + 23)) (rd d (slotOff5 k + 24)) (rd d (slotOff5 k + 25)) (rd d (slotOff5 k + 26)) (rd d (slotOff5 k + 27)) (rd d (slotOff5 k + 28)) (rd d (slotOff5 k + 29)) (rd d (slotOff5 k + 30)) (rd d (slotOff5 k + 31))

theorem block5_decode_frame
    (rd : byteDisk → Int → Int)
    (nameDecode :
      Int→Int→Int→Int→Int→Int→Int→Int→Int→Int→Int→Int→Int→Int→Int→
      Int→Int→Int→Int→Int→Int→Int→Int→Int→Int→Int→Int→Int→Int→Int→ nameT)
    (d0 d1 : byteDisk)
    (Hagree : ∀ b, 2560 ≤ b → b < 3072 → rd d0 b = rd d1 b) :
    ∀ k, 0 ≤ k → k < 16 →
      slotInode rd d1 k = slotInode rd d0 k ∧
      slotName rd nameDecode d1 k = slotName rd nameDecode d0 k := by
  intro k Hk0 Hk16
  have e : ∀ i, 0 ≤ i → i < 32 → rd d1 (slotOff5 k + i) = rd d0 (slotOff5 k + i) := by
    intro i Hi0 Hi32
    exact (Hagree (slotOff5 k + i) (by unfold slotOff5; omega) (by unfold slotOff5; omega)).symm
  refine ⟨?_, ?_⟩
  · unfold slotInode slotOff5
    rw [Hagree (2560 + 32 * k) (by omega) (by omega),
        Hagree (2560 + 32 * k + 1) (by omega) (by omega)]
  · unfold slotName
    rw [e 2 (by omega) (by omega), e 3 (by omega) (by omega), e 4 (by omega) (by omega),
        e 5 (by omega) (by omega), e 6 (by omega) (by omega), e 7 (by omega) (by omega),
        e 8 (by omega) (by omega), e 9 (by omega) (by omega), e 10 (by omega) (by omega),
        e 11 (by omega) (by omega), e 12 (by omega) (by omega), e 13 (by omega) (by omega),
        e 14 (by omega) (by omega), e 15 (by omega) (by omega), e 16 (by omega) (by omega),
        e 17 (by omega) (by omega), e 18 (by omega) (by omega), e 19 (by omega) (by omega),
        e 20 (by omega) (by omega), e 21 (by omega) (by omega), e 22 (by omega) (by omega),
        e 23 (by omega) (by omega), e 24 (by omega) (by omega), e 25 (by omega) (by omega),
        e 26 (by omega) (by omega), e 27 (by omega) (by omega), e 28 (by omega) (by omega),
        e 29 (by omega) (by omega), e 30 (by omega) (by omega), e 31 (by omega) (by omega)]

#print axioms block5_decode_frame

end Scan
end Dir
end UnixFs
