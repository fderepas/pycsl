/- unix-filesystem/UnixInodeFileSystem.proofs/lean/InsertPreservesUnique.lean

   Validation of UnixFs.Dir.insert_preserves_unique (gap-12) — Lean 4 mirror of
   the Rocq proof in ../rocq/InsertPreservesUnique.v.

   The INSERT companion of remove_reflects_absent (UnixDirScanAbsent.lean): the
   maintenance lemma for the directory-uniqueness class invariant. Inserting a
   fresh (not-already-live) name at one slot, with all other slots unchanged,
   cannot manufacture a duplicate-live-name pair. Finite 4-way case split, no
   induction; cross / off-diagonal cases closed by the freshness / pre-state
   uniqueness hypotheses, integers by omega.

   Verified under Lean 4.30.0. No sorry.
   #print axioms = [propext, Quot.sound] ⊆ allowlist. -/

namespace UnixFs
namespace Dir

section Scan

variable {disk : Type} {name_t : Type}
variable (slot_inode : disk → Int → Int → Int)
variable (slot_name  : disk → Int → Int → name_t)

theorem insert_preserves_unique
    (d0 d1 : disk) (blk s : Int) (nm : name_t)
    (_Hnn : ∀ j, 0 ≤ slot_inode d0 blk j)
    (_Hs : 0 ≤ s ∧ s < 16)
    (Hinv0 : ∀ i j, 0 ≤ i → i < 16 → 0 ≤ j → j < 16 →
        slot_inode d0 blk i ≠ 0 → slot_inode d0 blk i < 32 →
        slot_inode d0 blk j ≠ 0 → slot_inode d0 blk j < 32 →
        slot_name d0 blk i = slot_name d0 blk j → i = j)
    (Hfresh : ∀ k, 0 ≤ k → k < 16 →
        slot_inode d0 blk k ≠ 0 → slot_inode d0 blk k < 32 →
        slot_name d0 blk k ≠ nm)
    (Hframe : ∀ k, 0 ≤ k → k < 16 → k ≠ s →
        slot_inode d1 blk k = slot_inode d0 blk k ∧
        slot_name  d1 blk k = slot_name  d0 blk k)
    (Hsnm : slot_name d1 blk s = nm) :
    ∀ i j, 0 ≤ i → i < 16 → 0 ≤ j → j < 16 →
        slot_inode d1 blk i ≠ 0 → slot_inode d1 blk i < 32 →
        slot_inode d1 blk j ≠ 0 → slot_inode d1 blk j < 32 →
        slot_name d1 blk i = slot_name d1 blk j → i = j := by
  intro i j Hi Hib Hj Hjb Hil Hilb Hjl Hjlb Hnameq
  rcases Decidable.em (i = s) with Eis | Nis
  · rcases Decidable.em (j = s) with Ejs | Njs
    · omega
    · -- i = s, j ≠ s : j live on d0, name(j)=nm, contradicts Hfresh
      exfalso
      subst Eis
      obtain ⟨Hij, Hnj⟩ := Hframe j Hj Hjb Njs
      apply Hfresh j Hj Hjb
      · rw [← Hij]; exact Hjl
      · rw [← Hij]; exact Hjlb
      · rw [← Hnj, ← Hnameq]; exact Hsnm
  · rcases Decidable.em (j = s) with Ejs | Njs
    · -- j = s, i ≠ s : symmetric
      exfalso
      subst Ejs
      obtain ⟨Hii, Hni⟩ := Hframe i Hi Hib Nis
      apply Hfresh i Hi Hib
      · rw [← Hii]; exact Hil
      · rw [← Hii]; exact Hilb
      · rw [← Hni, Hnameq]; exact Hsnm
    · -- i ≠ s, j ≠ s : both decode equal d0, Hinv0 applies
      obtain ⟨Hii, Hni⟩ := Hframe i Hi Hib Nis
      obtain ⟨Hij, Hnj⟩ := Hframe j Hj Hjb Njs
      apply Hinv0 i j Hi Hib Hj Hjb
      · rw [← Hii]; exact Hil
      · rw [← Hii]; exact Hilb
      · rw [← Hij]; exact Hjl
      · rw [← Hij]; exact Hjlb
      · rw [← Hni, ← Hnj]; exact Hnameq

#print axioms insert_preserves_unique

end Scan

end Dir
end UnixFs
