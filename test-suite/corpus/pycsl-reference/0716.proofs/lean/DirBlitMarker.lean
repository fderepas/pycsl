/- Validation of the ROUTE-1 UNIQUE-MARKER form of the folded byte-rung
   directory-invariant maintenance facts -- Lean 4 mirror of
   ../rocq/DirBlitMarker.v:
     UnixFs.Dir.dir_blit_marker_intro
     UnixFs.Dir.dir_blit_marker_insert

   CONTEXT (test-supervise-sl route 1, 2026-06-19): the byte-keyed fold (0715) is
   correct logic but its byte key matches disk[2560 + <expr>] and explodes inside the
   pure-byte helper _blit_dir_entry; worse, citing the byte VALUE keystones
   (slot_inode_byte_decode, slot_name_byte_decode, field_to_str_round_trip) at the
   real mutator EMITS them MODULE-WIDE and their generic disk[...] / field_to_str
   triggers E-match-explode _blit_dir_entry's byte loop (Timeout 8.6e9 steps).

   THE FIX: route the ENTIRE maintenance fact -- including BOTH slot VALUE decodes
   (inode AND name) -- through a SINGLE UNIQUE uninterpreted predicate
   dir_blit_marker d0 d1 s b0 b1 name, triggered [dir_blit_marker ...]. The os body
   cites ONLY the marker intro+insert, so NO byte-decode/string keystone is emitted
   module-wide and NO sibling byte mutator is poisoned. All byte->slot and
   byte->string decode reasoning is discharged INSIDE this kernel proof.

   Faithful interpretation (IDENTICAL to the keystone proofs for the shared symbols;
   `name` modelled as char-code list, as in FieldToStrRoundTrip).

   Verified under Lean 4 (core only, no Mathlib). No sorry. -/

namespace UnixFs
namespace Dir
section Marker

variable {Disk : Type}
variable (rd : Disk → Int → Int)
variable {Name : Type}
variable (nchar : Name → Int → Int)
variable (nlen : Name → Int)

def slot_off (blk k : Int) : Int := blk * 512 + 32 * k

def slot_inode (d : Disk) (blk k : Int) : Int :=
  256 * rd d (slot_off blk k) + rd d (slot_off blk k + 1)

def scan (rdf : Int → Int) (off : Int) : Nat → List Int
  | 0 => []
  | Nat.succ m => if rdf off = 0 then [] else rdf off :: scan rdf (off + 1) m

def field_to_str (rdf : Int → Int) (off width : Int) : List Int :=
  scan rdf off width.toNat

def slot_name (d : Disk) (blk k : Int) : List Int :=
  field_to_str (rd d) (slot_off blk k + 2) 30

def name_list (nm : Name) : Nat → Int → List Int
  | 0, _ => []
  | Nat.succ m, i => nchar nm i :: name_list nm m (i + 1)

def name_val (nm : Name) : List Int := name_list nchar nm (nlen nm).toNat 0

def uniq (d : Disk) : Prop :=
  ∀ i j : Int, 0 ≤ i → i < 16 → 0 ≤ j → j < 16 →
    slot_inode rd d 5 i ≠ 0 → slot_inode rd d 5 i < 32 →
    slot_inode rd d 5 j ≠ 0 → slot_inode rd d 5 j < 32 →
    slot_name rd d 5 i = slot_name rd d 5 j → i = j

def slots_lt32 (d : Disk) : Prop :=
  ∀ k : Int, 0 ≤ k → k < 16 → slot_inode rd d 5 k < 32

/-- THE MARKER: the conservative DEFINITION of the abstract WhyML predicate as the
    conjunction of ALL byte facts a blit establishes plus name well-formedness. -/
def dir_blit_marker (d0 d1 : Disk) (s b0 b1 : Int) (nm : Name) : Prop :=
  0 ≤ nlen nm
  ∧ nlen nm ≤ 30
  ∧ rd d1 (slot_off 5 s) = b0
  ∧ rd d1 (slot_off 5 s + 1) = b1
  ∧ (∀ i : Int, 0 ≤ i → i < nlen nm → nchar nm i ≠ 0)
  ∧ (∀ i : Int, 0 ≤ i → i < nlen nm → rd d1 (slot_off 5 s + 2 + i) = nchar nm i)
  ∧ (nlen nm < 30 → rd d1 (slot_off 5 s + 2 + nlen nm) = 0)
  ∧ (∀ b : Int, 0 ≤ b → b < 512 →
        (b < 32 * s ∨ 32 * s + 32 ≤ b) →
        rd d1 (5 * 512 + b) = rd d0 (5 * 512 + b))

theorem scan_frame (rd0 rd1 : Int → Int) :
    ∀ (fuel : Nat) (off : Int),
      (∀ j, j < fuel → rd0 (off + (j : Int)) = rd1 (off + (j : Int))) →
      scan rd0 off fuel = scan rd1 off fuel := by
  intro fuel
  induction fuel with
  | zero => intro off _; rfl
  | succ m ih =>
    intro off hagree
    have hhead : rd0 off = rd1 off := by
      have h := hagree 0 (by omega); simpa using h
    have htail : scan rd0 (off + 1) m = scan rd1 (off + 1) m := by
      apply ih (off + 1)
      intro j hj
      have h := hagree (j + 1) (by omega)
      have hcast : off + ((j : Int) + 1) = off + 1 + (j : Int) := by omega
      push_cast at h; rw [hcast] at h; exact h
    simp only [scan, hhead, htail]

theorem field_to_str_frame
    (rd0 rd1 : Int → Int) (off width : Int)
    (_hw : 0 ≤ width)
    (hagree : ∀ i : Int, 0 ≤ i → i < width → rd0 (off + i) = rd1 (off + i)) :
    field_to_str rd0 off width = field_to_str rd1 off width := by
  unfold field_to_str
  apply scan_frame rd0 rd1 width.toNat off
  intro j hj
  have hjw : (j : Int) < width := by
    have : ((width.toNat : Int)) = width := Int.toNat_of_nonneg _hw
    omega
  have h := hagree (j : Int) (by omega) hjw
  simpa using h

theorem slot_frame_of_region (d0 d1 : Disk) (s : Int)
    (hs0 : 0 ≤ s) (hs1 : s < 16)
    (hframe : ∀ b : Int, 0 ≤ b → b < 512 →
        (b < 32 * s ∨ 32 * s + 32 ≤ b) →
        rd d1 (5 * 512 + b) = rd d0 (5 * 512 + b)) :
    ∀ k : Int, 0 ≤ k → k < 16 → k ≠ s →
      slot_inode rd d1 5 k = slot_inode rd d0 5 k ∧
      slot_name rd d1 5 k = slot_name rd d0 5 k := by
  have hslotbytes : ∀ k : Int, 0 ≤ k → k < 16 → k ≠ s →
      ∀ j : Int, 0 ≤ j → j < 32 →
        rd d1 (slot_off 5 k + j) = rd d0 (slot_off 5 k + j) := by
    intro k hk0 hk1 hne j hj0 hj1
    have hbeq : slot_off 5 k + j = 5 * 512 + (32 * k + j) := by unfold slot_off; omega
    rw [hbeq]
    apply hframe
    · omega
    · omega
    · omega
  intro k hk0 hk1 hne
  refine ⟨?_, ?_⟩
  · unfold slot_inode
    have hb0 := hslotbytes k hk0 hk1 hne 0 (by omega) (by omega)
    have hb1 := hslotbytes k hk0 hk1 hne 1 (by omega) (by omega)
    simp only [Int.add_zero] at hb0
    rw [hb0, hb1]
  · unfold slot_name
    apply field_to_str_frame (rd d1) (rd d0) (slot_off 5 k + 2) 30 (by omega)
    intro i hi0 hi1
    have hcast : slot_off 5 k + 2 + i = slot_off 5 k + (2 + i) := by omega
    rw [hcast]
    exact hslotbytes k hk0 hk1 hne (2 + i) (by omega) (by omega)

/-- the name byte->decode round-trip (identical model to FieldToStrRoundTrip). -/
theorem scan_recovers (rdf : Int → Int) (nm : Name) :
    ∀ (fuel : Nat) (off i : Int),
      0 ≤ i →
      i + (fuel : Int) = 30 →
      nlen nm ≤ 30 →
      i ≤ nlen nm →
      (∀ t, i ≤ t → t < nlen nm → nchar nm t ≠ 0) →
      (∀ t, i ≤ t → t < nlen nm → rdf (off + (t - i)) = nchar nm t) →
      (nlen nm < 30 → rdf (off + (nlen nm - i)) = 0) →
      scan rdf off fuel = name_list nchar nm (nlen nm - i).toNat i := by
  intro fuel
  induction fuel with
  | zero =>
    intro off i _ hwf _ hile _ _ _
    have h0 : nlen nm - i = 0 := by simp at hwf; omega
    rw [h0]; simp [scan, name_list]
  | succ m ih =>
    intro off i hi hwf hl30 hile hnn hbytes hnull
    by_cases hlt : i < nlen nm
    · -- the byte is the (nonzero) char code, recurse
      have hb : rdf off = nchar nm i := by
        have h := hbytes i (by omega) hlt
        have : off + (i - i) = off := by omega
        rw [this] at h; exact h
      have hnz : nchar nm i ≠ 0 := hnn i (by omega) hlt
      have hstep : (nlen nm - i).toNat = Nat.succ (nlen nm - (i + 1)).toNat := by omega
      rw [hstep]
      simp only [scan, hb, name_list, if_neg hnz]
      congr 1
      apply ih (off + 1) (i + 1)
      · omega
      · push_cast; omega
      · omega
      · omega
      · intro t ht0 ht1; exact hnn t (by omega) ht1
      · intro t ht0 ht1
        have h := hbytes t (by omega) ht1
        have hc : off + (t - i) = off + 1 + (t - (i + 1)) := by omega
        rw [hc] at h; exact h
      · intro hlt2
        have h := hnull hlt2
        have hc : off + (nlen nm - i) = off + 1 + (nlen nm - (i + 1)) := by omega
        rw [hc] at h; exact h
    · -- i = nlen nm and fuel > 0 => len < 30 => trailing null fires
      have hieq : i = nlen nm := by omega
      have hlen_lt : nlen nm < 30 := by omega
      have hzero : rdf off = 0 := by
        have h := hnull hlen_lt
        rw [← hieq] at h
        have : off + (i - i) = off := by omega
        rw [this] at h; exact h
      have h0 : nlen nm - i = 0 := by omega
      rw [h0]
      simp [scan, name_list, hzero]

theorem name_round_trip (d : Disk) (nm : Name) (s : Int)
    (hlen0 : 0 ≤ nlen nm) (hlen30 : nlen nm ≤ 30)
    (hnn : ∀ i, 0 ≤ i → i < nlen nm → nchar nm i ≠ 0)
    (hbytes : ∀ i, 0 ≤ i → i < nlen nm → rd d (slot_off 5 s + 2 + i) = nchar nm i)
    (hnull : nlen nm < 30 → rd d (slot_off 5 s + 2 + nlen nm) = 0) :
    slot_name rd d 5 s = name_val nchar nlen nm := by
  unfold slot_name field_to_str name_val
  have h30 : (30 : Int).toNat = 30 := by decide
  rw [h30]
  have hwf : (0 : Int) + ((30 : Nat) : Int) = 30 := by simp
  have hbytes' : ∀ t : Int, 0 ≤ t → t < nlen nm →
      rd d (slot_off 5 s + 2 + (t - 0)) = nchar nm t := by
    intro t ht0 ht1
    have h := hbytes t ht0 ht1
    have he : slot_off 5 s + 2 + (t - 0) = slot_off 5 s + 2 + t := by omega
    rw [he]; exact h
  have hnull' : nlen nm < 30 → rd d (slot_off 5 s + 2 + (nlen nm - 0)) = 0 := by
    intro hlt
    have h := hnull hlt
    have he : slot_off 5 s + 2 + (nlen nm - 0) = slot_off 5 s + 2 + nlen nm := by omega
    rw [he]; exact h
  have hrec := scan_recovers (nchar := nchar) (nlen := nlen) (rd d) nm 30
    (slot_off 5 s + 2) 0
    (by omega) hwf hlen30 (by omega) hnn hbytes' hnull'
  have hz : (nlen nm - 0).toNat = (nlen nm).toNat := by congr 1; omega
  rw [hrec, hz]

/-- dir_blit_marker_intro: byte facts -> marker (DEFINITIONAL, zero trust). -/
theorem dir_blit_marker_intro (d0 d1 : Disk) (s b0 b1 : Int) (nm : Name)
    (hl0 : 0 ≤ nlen nm) (hl30 : nlen nm ≤ 30)
    (hb0 : rd d1 (slot_off 5 s) = b0)
    (hb1 : rd d1 (slot_off 5 s + 1) = b1)
    (hnn : ∀ i : Int, 0 ≤ i → i < nlen nm → nchar nm i ≠ 0)
    (hbytes : ∀ i : Int, 0 ≤ i → i < nlen nm → rd d1 (slot_off 5 s + 2 + i) = nchar nm i)
    (hnull : nlen nm < 30 → rd d1 (slot_off 5 s + 2 + nlen nm) = 0)
    (hframe : ∀ b : Int, 0 ≤ b → b < 512 →
        (b < 32 * s ∨ 32 * s + 32 ≤ b) →
        rd d1 (5 * 512 + b) = rd d0 (5 * 512 + b)) :
    dir_blit_marker rd nchar nlen d0 d1 s b0 b1 nm :=
  ⟨hl0, hl30, hb0, hb1, hnn, hbytes, hnull, hframe⟩

/-- dir_blit_marker_insert: marker + uniq/slots_lt32 d0 + range + freshness ->
    slot_inode value + slot_name value (= name_val) + frame + uniq d1 + slots_lt32 d1. -/
theorem dir_blit_marker_insert (d0 d1 : Disk) (s b0 b1 : Int) (nm : Name)
    (hmark : dir_blit_marker rd nchar nlen d0 d1 s b0 b1 nm)
    (hu0 : uniq rd d0)
    (hl0 : slots_lt32 rd d0)
    (hs0 : 0 ≤ s) (hs1 : s < 16)
    (_hlive : 256 * b0 + b1 ≠ 0)
    (hlt : 256 * b0 + b1 < 32)
    (hfresh : ∀ k : Int, 0 ≤ k → k < 16 → k ≠ s →
        slot_inode rd d0 5 k ≠ 0 → slot_inode rd d0 5 k < 32 →
        slot_name rd d0 5 k ≠ name_val nchar nlen nm) :
       slot_inode rd d1 5 s = 256 * b0 + b1
    ∧ slot_name rd d1 5 s = name_val nchar nlen nm
    ∧ (∀ k : Int, 0 ≤ k → k < 16 → k ≠ s →
           slot_inode rd d1 5 k = slot_inode rd d0 5 k ∧
           slot_name rd d1 5 k = slot_name rd d0 5 k)
    ∧ uniq rd d1
    ∧ slots_lt32 rd d1 := by
  obtain ⟨hnl0, hnl30, hb0, hb1, hnn, hbytes, hnull, hframe⟩ := hmark
  have hsf := slot_frame_of_region rd d0 d1 s hs0 hs1 hframe
  have hvali : slot_inode rd d1 5 s = 256 * b0 + b1 := by
    unfold slot_inode; rw [hb0, hb1]
  have hvaln : slot_name rd d1 5 s = name_val nchar nlen nm :=
    name_round_trip rd nchar nlen d1 nm s hnl0 hnl30 hnn hbytes hnull
  have hu1 : uniq rd d1 := by
    intro i j hi0 hi1 hj0 hj1 hil hilt hjl hjlt hnm
    by_cases his : i = s <;> by_cases hjs : j = s
    · rw [his, hjs]
    · exfalso; subst his
      obtain ⟨hji, hjn⟩ := hsf j hj0 hj1 hjs
      apply hfresh j hj0 hj1 hjs (by rw [← hji]; exact hjl) (by rw [← hji]; exact hjlt)
      rw [← hjn, ← hnm, hvaln]
    · exfalso; subst hjs
      obtain ⟨hii, hin⟩ := hsf i hi0 hi1 his
      apply hfresh i hi0 hi1 his (by rw [← hii]; exact hil) (by rw [← hii]; exact hilt)
      rw [← hin, hnm, hvaln]
    · obtain ⟨hii, hin⟩ := hsf i hi0 hi1 his
      obtain ⟨hji, hjn⟩ := hsf j hj0 hj1 hjs
      exact hu0 i j hi0 hi1 hj0 hj1
        (by rw [← hii]; exact hil) (by rw [← hii]; exact hilt)
        (by rw [← hji]; exact hjl) (by rw [← hji]; exact hjlt)
        (by rw [← hin, ← hjn]; exact hnm)
  have hl1 : slots_lt32 rd d1 := by
    intro k hk0 hk1
    by_cases hks : k = s
    · rw [hks, hvali]; exact hlt
    · obtain ⟨hki, _⟩ := hsf k hk0 hk1 hks
      rw [hki]; exact hl0 k hk0 hk1
  exact ⟨hvali, hvaln, hsf, hu1, hl1⟩

/-- dir_blit_marker_frame_only (SPIKE-2): the SLOT-LOCALITY FRAME alone. A STRICT
    corollary of the marker — every slot k ≠ s decodes identically in d1 and d0,
    needing ONLY the marker (= the byte facts, by definition) and the slot-in-range
    fact, NOT uniq/slots_lt32/range/freshness. It is `slot_frame_of_region` applied
    to the marker's byte-region-frame conjunct (the same sub-derivation
    dir_blit_marker_insert performs to obtain its frame conjunct hsf). Zero new TCB. -/
theorem dir_blit_marker_frame_only (d0 d1 : Disk) (s b0 b1 : Int) (nm : Name)
    (hmark : dir_blit_marker rd nchar nlen d0 d1 s b0 b1 nm)
    (hs0 : 0 ≤ s) (hs1 : s < 16) :
    ∀ k : Int, 0 ≤ k → k < 16 → k ≠ s →
      slot_inode rd d1 5 k = slot_inode rd d0 5 k ∧
      slot_name rd d1 5 k = slot_name rd d0 5 k := by
  obtain ⟨_, _, _, _, _, _, _, hframe⟩ := hmark
  exact slot_frame_of_region rd d0 d1 s hs0 hs1 hframe

#print axioms dir_blit_marker_intro
#print axioms dir_blit_marker_insert
#print axioms dir_blit_marker_frame_only

/-- dir_blit_marker_value_inode (ZERO-ENTRY corollary): the inode VALUE decode
    alone. From the marker conclude slot_inode d1 5 s = 256*b0+b1 — needing ONLY
    the marker's two inode-byte conjuncts, NOT liveness/uniq/slots_lt32/freshness.
    The `hvali` sub-derivation of dir_blit_marker_insert, exposed as its own
    theorem; it does NOT need 256*b0+b1 ≠ 0, so it applies to _zero_entry
    (b0=b1=0 ⇒ slot_inode d1 5 s = 0). Zero new TCB. -/
theorem dir_blit_marker_value_inode (d0 d1 : Disk) (s b0 b1 : Int) (nm : Name)
    (hmark : dir_blit_marker rd nchar nlen d0 d1 s b0 b1 nm) :
    slot_inode rd d1 5 s = 256 * b0 + b1 := by
  obtain ⟨_, _, hb0, hb1, _, _, _, _⟩ := hmark
  unfold slot_inode
  rw [hb0, hb1]

#print axioms dir_blit_marker_value_inode

/-- dir_blit_marker_intro_zero (ZERO-ENTRY intro corollary): establish the marker
    for a ZEROED entry (b0=b1=0, EMPTY name) from the MINIMAL byte facts. The
    general dir_blit_marker_intro needs EIGHT hypotheses; for nlen nm = 0 the two
    per-char foralls are vacuous, the len bounds are trivial, and the null-pad
    collapses to the single byte fact rd d1 (slot_off 5 s + 2) = 0. So the marker
    follows from just three byte facts (the two inode bytes = 0, the head name byte
    = 0) plus the byte-region frame — a far cheaper establishment than the general
    intro, exposed as its own theorem so _zero_entry folds the marker in ONE cheap
    marker-keyed step in the full-module aggregate context. Zero new TCB — a strict
    specialisation of the marker DEFINITION. -/
theorem dir_blit_marker_intro_zero (d0 d1 : Disk) (s b0 b1 : Int) (nm : Name)
    (hnl : nlen nm = 0)
    (hb0 : rd d1 (slot_off 5 s) = b0)
    (hb1 : rd d1 (slot_off 5 s + 1) = b1)
    (hpad : rd d1 (slot_off 5 s + 2) = 0)
    (hframe : ∀ b : Int, 0 ≤ b → b < 512 →
        (b < 32 * s ∨ 32 * s + 32 ≤ b) →
        rd d1 (5 * 512 + b) = rd d0 (5 * 512 + b)) :
    dir_blit_marker rd nchar nlen d0 d1 s b0 b1 nm := by
  refine ⟨?_, ?_, hb0, hb1, ?_, ?_, ?_, hframe⟩
  · rw [hnl]; omega
  · rw [hnl]; omega
  · intro i _ hi; rw [hnl] at hi; omega
  · intro i _ hi; rw [hnl] at hi; omega
  · intro _; rw [hnl]; simpa using hpad

#print axioms dir_blit_marker_intro_zero


end Marker
end Dir
end UnixFs
