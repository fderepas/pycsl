# `_write_dir_entry` goal #2 (slot_name Postcondition) — CLOSED zero-trust; residual is now PURELY goal #3 (frame + invariant maintenance)

DATE: 2026-06-18
LOOP: test-supervise-sl (residual goal #2 of `_write_dir_entry`)
STATUS: **GOAL #2 CLOSED at the method level** (slot_name write-side Postcondition
`slot_name(self.dir,5,slot)==name` discharges **Valid**, zero-trust, no weakening, no
bare `\trusted`, no new TCB axiom). NOT shipped — the partial rung reds the full body
gate (baseline 3 → 8) because goal #3 (slot-locality frame + uniq/slots_lt32
invariant maintenance) remains and the byte-keystone EMISSION additionally poisons
the directory mutators' invariant VCs. All experiments REVERTED; tree byte-identical
to HEAD; stash empty. Net `\trusted` delta 0 (campaign target stays 7).

## Bottom line
- **Goal #2 (the string-extensionality round-trip wall) is solvable** with a
  doctrine-compliant restructure — NO new axiom, NO weakening. The mission crux
  hypothesis is CONFIRMED, with one decisive addition: the wall was NOT only the
  string round-trip; it was the **method-call contract gap** on the opaque-offset
  blit helper. `sibling_concrete` is the key that turns the OOM into Valid.
- **Goal #3 (frame + invariant maintenance) is the new, precisely-located residual**
  — a human-gated TCB decision (a new folded cross-validated lemma), per doctrine NOT
  closeable autonomously.

## What was tried, measured (full body gate "N goal(s) remain", PYTHONHASHSEED=0)

Baseline (committed, `_write_dir_entry` `\trusted`): **3** goals remain
(`_unpack_direntry`×2 Precondition, `sys_rename`; the `_now`/`sys_write` OOM is the
documented non-deterministic aggregate noise).

### Experiment 1 — de-trust + inline byte-loop + 3 keystone cites + length/no-null requires
Restructured the body: literal-offset inode bytes (`self.dir[entry_offset]=inode//256`,
`+1=inode%256`) + an INLINE 30-byte null-padded name loop with byte-frame loop
invariants, then `#@ assert field_to_str(self.dir, entry_offset+2, 30)==name`. Added
`#@ proof rocq/lean` for `slot_inode_byte_decode`, `slot_name_byte_decode`,
`field_to_str_round_trip`; added `requires \str_length(name)<=30` and the no-embedded-null
`requires \forall i<len. ord(name[i])!=0` (field_to_str_round_trip's antecedent).
`--fun`: **4 goals**, with the slot_name assert and Postcondition exploding (OOM /
Timeout 6.6e9, 5.0e9 steps). The inline loop materializes `self.dir[off+i]` terms
per-iteration → the byte-keyed keystone trigger and the slot_inode/slot_name-keyed
uniq/slots_lt32 axiom web coexist → the documented global E-matching explosion.

### Experiment 2 — opaque-offset byte-only helper `_blit_name_field` (structural lesson)
Factored the name blit into a separate method `_blit_name_field(self, off, name)` whose
contract names NO `slot_name`/`field_to_str` (PURE BYTES, opaque `off`) — exactly
0712's `encode_name_field` shape. The byte-keyed trigger `disk[blk*512+32*k+2]` cannot
match an opaque `off`, so the loop proves clean. `_write_dir_entry` calls it and applies
the keystones ONCE at `#@ assert field_to_str(...)==name`.
- `_blit_name_field` `--fun`: its byte Postconditions are **Valid**; its 2 residuals are
  **Type invariant** (uniq/slots_lt32 over the mutated `self.dir`) — **Unknown ~320K
  steps without the keystones emitted, Timeout ~5–6M with them emitted**.
- `_write_dir_entry` `--fun`: the slot_name assert and Postcondition still **OOM** —
  because the abstract `val` helper's self-field-referencing byte ensures
  (`self.dir[off+i]==ord(name[i])`) DO NOT PROPAGATE across the method-call boundary
  (the known field-referencing-ensures propagation gap). The antecedent never reaches
  the decode site.

### Experiment 3 (DECISIVE) — `_blit_name_field` + `#@ sibling_concrete`
Marked the helper `#@ sibling_concrete` so its REAL verified byte semantics inline at
the call site (the helper's contract gap is bypassed; the byte facts are concretely in
hand). `--fun unixinodefilesystem___write_dir_entry`:
- **Assertion `field_to_str(self.dir, entry_offset+2, 30)==name` → Valid (48029 steps).**
- **Postcondition `slot_name(self.dir,5,slot)==name` → Valid (~50K steps).** ← GOAL #2.
- Postcondition `slot_inode(self.dir,5,slot)==inode_num` → Valid (inode keystone).
- Postcondition slot_inode FRAME `∀k≠slot` → Valid.
- Postcondition **slot_name FRAME `∀k≠slot. slot_name unchanged` → Out of memory.** ← goal #3.
- **Type invariant `uniq(self.dir)`/`slots_lt32(self.dir)` → Timeout (3.1e9 / 2.0e8 steps).** ← goal #3 class.

Full body gate (authoritative): **8 goals remain** (baseline 3 + 5 new). The 5 new,
categorized: `_write_dir_entry` Type-invariant (uniq/slots_lt32), `_write_dir_entry`
Postcondition (slot_name FRAME), `_blit_name_field` Type-invariant, `_blit_name_field`
Loop-invariant-preservation (keystone-poisoned), and the keystone emission spilling
into a sibling mutator's VC. The slot_name VALUE Postcondition is NOT among the
unproven — it is gone (Valid).

## The decisive findings (two, both reusable)

1. **The structural lesson ("keep the string axiom out of the byte-blit loop") is
   NECESSARY but, alone, INSUFFICIENT — the opaque-offset helper hits the method-call
   contract gap.** A byte-only helper with a self-field-referencing quantified ensures
   (`self.dir[off+i]==ord(name[i])`) does NOT propagate to the caller as an abstract
   `val`, so the round-trip antecedent never arrives at the decode site (OOM). The fix
   is `#@ sibling_concrete`: inline the helper's REAL verified semantics so the byte
   facts are concrete at the call site. With it, BOTH string axioms (the bridge
   `slot_name_byte_decode` and the round-trip `field_to_str_round_trip`) fire EXACTLY
   ONCE, O(1), and the slot_name VALUE Postcondition is Valid (~50K steps) — the
   ~23M-step string wall is GONE.

2. **Goal #2 (slot_name VALUE) and goal #3 (frame + uniq/slots_lt32 maintenance) are
   SEPARABLE at the obligation level but NOT at the ship level.** Goal #2 closes
   cleanly. Goal #3 remains because: (a) ANY method that `assigns self.dir` incurs the
   uniq/slots_lt32 Type-invariant VC, whose maintenance lemmas (`insert_preserves_*`)
   were RETIRED from emission when the mutators were trusted; and (b) the byte-decode
   keystones, once EMITTED (mandatory for goal #2), poison those invariant VCs
   (measured: `_blit_name_field` Type-invariant 320K Unknown → 5–6M Timeout the moment
   the keystones are in the module). So a partial rung that closes only goal #2 reds the
   body gate (3→8) = a REGRESSION → not shippable, reverted.

## The precise residual / GAP (routed to the human)
Goal #3 = the slot_name slot-locality frame `∀k≠slot. slot_name unchanged` + the
`uniq(self.dir)`/`slots_lt32(self.dir)` invariant maintenance, AND the keystone-emission
pollution of every directory mutator's invariant VC. The doctrine-compliant close
(per keystone doc 20260617-1039 §"What a future session needs") is a FOLDED
cross-validated lemma (the `insert_preserves_uniq`/`insert_preserves_slots_lt32` family
extended with the byte rung folded away) keyed so NO byte term and NO slot_inode/slot_name
term coexist in any VC — i.e. NEW cross-validated Rocq+Lean axioms. Authoring + adopting
those is a **human-gated TCB decision** (doctrine option (b)), not the loop's to take.
Until that lands, the full write-side dirscan trust stays.

## Cross-validation re-confirmed (the cited substrate, this run)
- `0708.proofs/rocq/FieldToStrRoundTrip.v`: coqc clean, 0 error/admit/axiom.
- `0711.proofs/rocq/SlotInodeByteDecode.v`: coqc clean.
- `0712.proofs/rocq/SlotNameByteDecode.v`: coqc clean; `Print Assumptions
  slot_name_byte_decode` → Section Variables only (`rd : Z -> Z`), 0 Axiom/Admitted
  (Closed under the global context).

## Ergonomic gap surfaced (PyCSL feature candidate)
The opaque-offset blit helper had to be `#@ sibling_concrete` to deliver its byte
postconditions, because the **method-call contract propagation drops self-field-
referencing quantified ensures** (`self.dir[off+i]==expr`). A targeted propagation of
self-field-referencing quantified single-region byte ensures across the import/method
boundary (the byte-frame twin of the `_build_method_result_frame_ensures_map` /
`#@ propagate_frame` work that landed for `\result`-frames) would let the helper stay a
clean abstract `val` and remove the need to inline it — making the structural-lesson
pattern usable WITHOUT `sibling_concrete`'s VC-size cost.
