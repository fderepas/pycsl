# cleared-pack RESIDUALS — S0 SMT-feasibility spike verdict: **GO**

Fixture: `cleared-pack-multislot-signed.mlw` (Why3 1.8.2, Alt-Ergo 2.6.2, Z3 4.13.3).
Covers the three NEW encoding shapes of the residuals: multi-slot standard-int
(item 1), signed (item 2), fixed-bytes `s` (item 3). Each leads with the
make-or-break round-trip goal; a dedicated module leads with guard-necessity.

| goal | shape | Alt-Ergo | Z3 |
|---|---|---|---|
| ms_field0 (tuple proj field 0) | u16u32 multi-slot | Valid 0.04s / 18 st | Valid 0.01s / 6469 st |
| ms_field1 (tuple proj field 1) | u16u32 multi-slot | Valid 0.03s / 18 st | Valid 0.01s / 6470 st |
| ms_size (size law as bound) | u16u32 multi-slot | Valid 0.03s / 12 st | Valid 0.01s / 8129 st |
| sgn_pos (round-trip, in-range) | i32 signed | Valid 0.04s / 8 st | Valid 0.01s / 837 st |
| sgn_neg (round-trip at INT32_MIN) | i32 signed | Valid 0.03s / 5 st | Valid 0.01s / 7422 st |
| s_roundtrip (array identity) | s4 fixed-bytes | Valid 0.03s / 6 st | Valid 0.00s / 971 st |
| u16_guarded (concrete codec, guarded) | u16 | Valid 0.03s / 57 st | Valid 0.01s / 6674 st |
| u16_guard_necessity (counterexample) | u16 | Valid 0.03s / 47 st | Valid 0.01s / 505 st |
| **u16_unguarded_UNPROVABLE** (must NOT prove) | u16 | **Timeout 10s** | **Timeout 10s** |

**Verdict: GO on items 1, 2, 3.**
- The multi-field round-trip axiom projects each field cleanly through the tuple
  (no E-matching blowup; AE step counts tiny). The per-field width+sign-tagged
  guard is the antecedent — so `>HH` (u16u16) and `<ii` (i32i32) NO LONGER collide
  (distinct symbols, distinct guards), closing the choices.md S0 blocker.
- Signed round-trip holds across the WHOLE range including the negative half and
  INT32_MIN (two's-complement) — the byte codec is anchored concretely in the Rocq/
  Lean proofs; the abstract axiom reasons instantly.
- The `s` fixed-bytes round-trip is array identity under `length d = N` and
  discharges fast (same shape as the legacy i1a1 array-tuple round-trip, but here
  guarded + byte-codec-anchored).
- **Guard is load-bearing (soundness proof):** the concrete codec proves
  `unpack(pack 65536)=0 ≠ 65536` (u16_guard_necessity Valid) AND the UNGUARDED
  universal law times out on BOTH provers (u16_unguarded_UNPROVABLE) — it is FALSE,
  so the in-range `requires` is not decoration.

Decision: emit each shape's round-trip as a cited joint AXIOM over the matched
`struct_{pack,unpack}_f<tags>` pair (pack and unpack occur at separate sites in the
round-trip drivers), guarded by the per-field in-range `requires`, anchored by
extended Rocq+Lean byte-codec proofs — exactly the single-slot mechanism, widened
to a per-field width/signedness tag.
