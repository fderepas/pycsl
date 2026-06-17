# Dirscan write-side retirement: the keystone trigger does not fire on the real body — precise GAP

STATUS: GAP (confirmed, precisely located). No TCB change (8 `\trusted` unchanged).
No `preamble.py` change. Working tree byte-identical to HEAD after the experiment.

## Mission
Step-2 pilot: retire ONE `\trusted reviewer: dirscan-fidelity` on a directory-mutating
helper, maintaining `uniq(self.dir)` / `slots_lt32(self.dir)` over byte-materialized
state, using the now-merged byte-VALUE decode keystones (0711 `slot_inode_byte_decode`,
0712 `slot_name_byte_decode`) and the gap-17 folded-atom maintenance lemmas. Pilot
target: `_write_dir_entry` (the simplest dir mutator — one `Array.blit` into `self.dir`).

## What was PINNED (the explosion, measured)
De-trusting `_write_dir_entry` and running `--fun unixinodefilesystem___write_dir_entry`
(PYTHONHASHSEED=0) reproduces 5 unproven goals:

- 2× **Postcondition** — `slot_inode/slot_name(self.dir,5,slot) == inode_num/name`
  (Unknown 353K / **Timeout 68M steps** on the slot_name ensure).
- 2× **Postcondition** — the `\forall k != slot` slot-locality FRAME ensures
  (Timeout 6.8M / **68M steps**).
- 2× **Type invariant** — re-establishing `uniq(self.dir)` / `slots_lt32(self.dir)`
  post-mutation (Unknown ~350K steps) — this is obligation (iii).

## ROOT CAUSE #1 (FIXED here, then reverted) — leaf pack contracts discard byte VALUES
The keystone `slot_inode_byte_decode` needs, at the blit site, the per-byte facts
`self.dir[off]=b0, self.dir[off+1]=b1` with `256*b0+b1 = inode_num`. But the body does
`self.dir[off:off+32] = _pack_direntry(inode_num, _pad_name(name))`, and:

- `_pack_uint16_be` had **no contract at all** (bare `return bytes([v//256, v%256])`).
- `_pack_direntry` ensured ONLY `\length(\result) == 32` — it threw away
  `\result[0]*256+\result[1] == inode_num` and `\result[i+2] == name_bytes[i]`.

So the packed buffer's byte VALUES were unrecoverable at the blit — the keystone had
nothing to decode. This is exactly the leaf-first doctrine: the leaf VALUE contracts
were missing.

**Fix proven (both `--fun` SUCCESS):** added value ensures to `_pack_uint16_be`
(`\result[0]*256+\result[1]==v`, byte bounds, `\length==2`) and to `_pack_direntry`
(`\result[0]*256+\result[1]==inode_num`, `\forall i<30. \result[i+2]==name_bytes[i]`).
`_pad_name` already carries the per-byte name ensures. With these, the slot_name
explosion dropped from **68M → 1.5M steps** — real progress, but still Timeout.

## ROOT CAUSE #2 (the actual WALL — not closeable autonomously)
Even with the byte VALUES available and explicit body asserts
(`self.dir[entry_offset]=packed[0]`, `... *256+... = inode_num`), the keystone
**still does not fire**, because of its deliberately-narrow trigger:

    slot_inode_byte_decode : forall ... [disk[blk * 512 + 32 * k]]. ...

The real body indexes through a let-bound ref: `self.dir[!entry_offset]`, where
`entry_offset := block_num*512 + slot*32`. The trigger term `disk[blk*512 + 32*k]`
does NOT match `self.dir[!entry_offset]` (deref vs literal product; and the body's
`slot*32` vs the trigger's `32*k`). The narrow byte-keyed trigger — the very safety
that keeps the keystone from the measured GLOBAL E-matching explosion on the
ubiquitous abstract `slot_inode` atoms — is precisely what prevents it from
instantiating at the mutator site. The `slot_inode(...slot)==inode_num` assert then
times out at **8.5M steps** with the keystone never applied.

Confirmed by inspecting the emitted `.mlw` (assert at the deref index; trigger never
fires).

## Why no autonomous closure (doctrine-compliant routes all blocked)
- **Widen the keystone trigger to `[slot_inode disk blk k]`** — explicitly rejected in
  the keystone's own design note and `os_coverage_progress` ("DON'T concretize
  slot_name"): it re-introduces the measured global explosion and risks the green
  `__init__` gate. NOT zero-TCB-safe, NOT autonomous.
- **A new `slot_inode`-keyed bridge axiom applied O(1) at the site** — a cited
  cross-validated axiom is a HUMAN-GATED TCB decision under the binding doctrine,
  never the loop's to take.
- **Why3 normalization so `!entry_offset` matches the literal product** — tool work
  of unknown tractability; not a contract/fold change.
- The Type-invariant (obligation iii) is downstream of the same wall: it needs
  `insert_preserves_uniq_folded` / `insert_preserves_slots_lt32` re-emitted (they were
  RETIRED from emission in M4 #1 because the mutators were trusted vals) PLUS a
  freshness `requires` (the inserted name is not already live — held by the caller
  `sys_open`/`sys_mkdir`, which are themselves `\trusted`+`no_inline` vals). The
  `field_to_str_round_trip` for the name half additionally needs a "no embedded null"
  precondition on `name`.

Per doctrine: removing the `\trusted` reds the gate (5→7 goals) → REGRESSION →
reverted. Logged GAP, routed to the human.

## BANKABLE result (the honest progress)
The leaf VALUE contracts on `_pack_uint16_be` and `_pack_direntry` are correct, proven,
and the genuinely-missing foundation. They are **independently safe** and could be
landed on their own (they only strengthen leaf postconditions, both `--fun` SUCCESS) —
they do not by themselves retire any trust but they are rung 1 of the eventual
retirement. NOT landed in this run (the mission is trust-retirement, not partial
rung-laying; and landing them touches a load-bearing module — flag for human).

## The precise remaining work to retire the write-side dirscan trust (human-gated)
1. (done, proven) leaf VALUE contracts on `_pack_uint16_be` / `_pack_direntry`.
2. Make the keystone fire at the mutator: EITHER index the blit by the literal
   `block_num*512 + 32*slot` (no ref) AND align `slot*32`→`32*slot`, OR add a narrow
   `slot_inode`-keyed bridge applied once (TCB decision).
3. `requires` on `_write_dir_entry`: `len(name) <= 30`, no-embedded-null
   (`\forall i<len(name). ord(name[i]) != 0`), inode liveness — discharged by callers.
4. Re-emit `insert_preserves_uniq_folded` + `insert_preserves_slots_lt32`
   (`_CLASS_INV_AXIOMS`) and a self.dir slot-locality frame for the `\forall k != slot`
   frame ensures; add the freshness `requires`.
5. Re-verify `--fun` + FULL body gate + `__init__` gate green; full-corpus byte-diff
   ×2; confirm TCB 8→7.

The pattern, IF it lands on `_write_dir_entry`, generalizes to `_write_entry`
(self.disk twin) and `_zero_entry` (the remove primitive, simpler: no name, sets
inode 0 — `zero_preserves_*` already banked); the three READ-side helpers
(`_dir_lookup`/`_dir_find_slot`/`_dir_find_free`) are a separate class (scan closed-form
fidelity, not a single write).
