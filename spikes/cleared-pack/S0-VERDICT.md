# cleared-pack S0 — SMT-feasibility spike VERDICT: **GO**

Round-trip led the spike (make-or-break). Results (Why3 1.8.2):

| goal | statement | Alt-Ergo | Z3 |
|------|-----------|----------|----|
| `rt_a` (abstract) | guarded round-trip over abstract `struct_pack_fu16`/`struct_unpack_fu16` + joint axiom | Valid 0.03s / 8 steps | Valid 468 steps |
| `rt_guarded` (concrete) | `0<=x<65536 -> unpack_be16(be16_hi x)(be16_lo x) = x` | Valid 0.04s / 57 steps | Valid 6674 steps |
| `guard_necessity_breaks` | `unpack_be16(be16_hi 65536)(be16_lo 65536) = 0` (round-trip BREAKS just out of range) | Valid | Valid |
| `rt_unguarded` (must NOT prove) | drop the guard ⇒ FALSE at x>=65536 | **Timeout** (correct: not a theorem) | — |

**Conclusions.**
- The guarded round-trip discharges instantly via the joint axiom + tuple/scalar projection.
- The in-range guard is **load-bearing**: a concrete byte model shows `unpack(pack 65536) = 0 ≠ 65536`,
  and the unguarded law is not provable. Dropping the guard yields a counterexample ⇒ the law is honest.
- Emit form: **cited joint axiom** over the abstract matched pair (pack & unpack occur at separate sites
  in the os round-trip usage), anchored by concrete-byte-codec Rocq+Lean proofs. WIDTH-tagged symbol
  (`fu16`) keeps it collision-sound vs the legacy `iN` family (see choices.md).
