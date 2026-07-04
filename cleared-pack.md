# cleared-pack.md — de-opaque struct pack/unpack (round-trip law)

**Goal.** Make `struct.pack`/`struct.unpack` content-faithful enough to prove the ROUND-TRIP —
`unpack(fmt, pack(fmt, x0, …, xN)) == (x0, …, xN)` — and the size law `len(pack(...)) == calcsize(fmt)`.
Today `struct_pack_<slot>` / `struct_unpack_<slot>` are fully-opaque abstract functions with NO relating
law, so a pack-then-unpack (the dominant real usage — serialize an inode, read it back) proves nothing.

**Feature** (emission changes). This is the NARROWEST of the opacity plans and the most self-contained
(one op family, one file). The round-trip law is SOUND for a well-formed format with in-range values —
`struct.pack`/`unpack` ARE inverse there — so this is honest, not a smuggled axiom.

---

## 1. Context / verdict (today, with citations)

- `struct.pack(fmt, x0…xN)` → `val function struct_pack_<slot_id> (fmt: int) (x0: t0) … : array int`
  (struct_format.py; slot_id from the format's type sequence). `struct.unpack(fmt, data)` →
  `val function struct_unpack_<slot_id> (fmt: int) (data: array int) : (t0, …, tN)`.
- Both are abstract with NO law connecting them, and the size is not tied to `calcsize`. So
  `unpack(pack(x)) == x` (the whole point of a struct round-trip — filesystem inode blit/read, the os
  corpus) is unprovable.
- **Root cause:** pack/unpack are emitted independently per call site; the inverse relationship is never
  stated.

**Verdict.** For each `<slot_id>` (a fixed type sequence), emit pack + unpack as a matched pair carrying:
(1) the size law `Array.length (pack fmt args) = calcsize_<slot>`; (2) the ROUND-TRIP law
`unpack fmt (pack fmt args) = args`; both guarded by the well-formed-format + in-range preconditions.

---

## 2. Gate B — SMT-feasibility spike FIRST (hand-write `.mlw`)

Confirm the round-trip law over a tuple result reasons cleanly (tuple equality + the guard):

```whyml
module PackSpike
  use int.Int use array.Array
  (* one slot shape: (int, int) at 8 bytes, little-endian '<ii' *)
  val pack2 (a b: int) : array int
    requires { -2147483648 <= a <= 2147483647 /\ -2147483648 <= b <= 2147483647 }  (* i-range *)
    ensures  { Array.length result = 8 }
  val unpack2 (data: array int) : (int, int)
    requires { Array.length data = 8 }
  (* the make-or-break inverse law, as a joint axiom about the pair *)
  axiom roundtrip2 : forall a b.
      -2147483648 <= a <= 2147483647 -> -2147483648 <= b <= 2147483647 ->
      unpack2 (pack2 a b) = (a, b)
  goal rt_a : forall a b. (-2147483648 <= a <= 2147483647) -> (-2147483648 <= b <= 2147483647) ->
      let (a', _) = unpack2 (pack2 a b) in a' = a
  goal rt_b : forall a b. (-2147483648 <= a <= 2147483647) -> (-2147483648 <= b <= 2147483647) ->
      let (_, b') = unpack2 (pack2 a b) in b' = b
end
```
- Record **Valid + timing** (Alt-Ergo, Z3). Tuple-projection through the axiom should be near-instant.
- **Verify the guard is load-bearing** — WITHOUT the i-range `requires`, the round-trip is FALSE (`pack`
  truncates/overflows) → the axiom would be unsound. The spike must show the guarded law is Valid AND
  that dropping the guard makes a counterexample (a value outside range breaks the round-trip). This is
  the soundness proof that the law is honest, not a lie.
- Decide: emit the round-trip as a joint `axiom` about the matched pair (cited, honest) vs an `ensures`
  on a single "pack-then-unpack" helper. Prefer the ensures-on-helper form if the corpus always
  round-trips at one site; use the axiom only if pack and unpack are at separate sites (the os case).

---

## 3. Stages

**S0 — spike (above)** → GO/NO-GO + the guard-necessity demonstration committed.

**S1 — the size law.** Attach `Array.length (struct_pack_<slot> fmt args) = <calcsize of slot>` to every
pack val (calcsize is a compile-time constant per slot). Low risk, immediately useful (bounds checks on
the packed buffer). Sequence this first — it's additive and needs no round-trip.

**S2 — the in-range guard.** Emit the per-field range `requires` on pack (i→[-2³¹,2³¹), B→[0,256), …
from the format chars). This is the PRECONDITION that makes the round-trip honest; without it, S3 is
unsound. Reject (UB rule) or leave opaque a pack whose args can't be shown in range.

**S3 — the round-trip law.** For a matched `pack_<slot>`/`unpack_<slot>` pair, emit the guarded inverse
law. Prefer the ensures-on-a-`_pack_then_unpack` helper when both occur in one function; else the cited
joint axiom (added to `proof_axiom_allowlist` WITH a `cite:` provenance note, since it's a real trusted
boundary — the byte-layout inverse — that Why3 can't derive from the opaque bodies).

**S4 — per-field extraction (optional, higher value).** `unpack(data)[k] == <the k-th field's decode of
data>` — a per-field content law, so partial reads (`unpack(...)[0]`) are faithful without a full
round-trip. Spike separately; guard on the byte offsets.

**S5 — self-annotate mirror + os corpus re-verify.** The os filesystem code (inode blit → read-back, the
`dirscan`/`_write_dir_entry` family) is the prime consumer — re-run its proofs; a previously-vacuous or
unprovable read-back should now discharge honestly. Cross-check against the os differential oracle.

---

## 4. Critical files
- `src/pycsl/module6_whyml/struct_format.py` — `struct_pack_<slot>`/`struct_unpack_<slot>` emission,
  `calcsize`, the slot_id/type-sequence logic, the format-char → range map.
- `src/pycsl/module6_whyml/preamble.py` — the matched-pair `val` + law emission; `proof_axiom_allowlist`
  entry (S3) with `cite:`.
- os corpus (`test-suite/corpus/…/os`) — the round-trip consumers.

## 5. Out-of-scope / soundness
- The round-trip law is SOUND ONLY under the in-range + well-formed-format guard (S2) — NEVER emit it
  ungarded. A pack whose args can't be shown in range stays opaque (size law only) or is rejected (UB-7.x).
- Native vs standard sizes/endianness: model the STANDARD sizes (`<`/`>`/`=` prefixes) per the format;
  native (`@`) alignment is out of scope → opaque.
- `s`/`p` (fixed bytes) and float (`f`/`d`) slots: size law yes; round-trip for float only if the real
  encoding is modeled (defer — keep opaque). Do NOT claim a float round-trip you can't back.
- The round-trip AXIOM (if used) must be honest (it IS true for standard struct) and CITED — never a
  tautology or an `Admitted`.

## 6. Gates (FEATURE — not byte-diff 0)
Full-corpus proof sweep green (os-heavy); emission differential = exactly the struct-using programs; the
os round-trip drivers now PROVE (were opaque/vacuous); `proof_axiom_allowlist` gains only the cited
round-trip law (audited via `pycsl --audit-proof`); τ-table/struct-semantics doc + UB catalog (native
alignment, out-of-range) updated; mirror re-verifies.

## 7. Reference corpus
Drivers, each `#@ ensures` a claim opaque today: pack/unpack round-trip (`#@ ensures unpack(pack(a,b)) ==
(a,b)` under the range `requires`); size law (`len(pack(...)) == calcsize`); a per-field read; a NEGATIVE
driver (`# pycsl-expected: FAIL`) with an OUT-OF-RANGE value showing the round-trip is NOT claimed there
(guard is load-bearing). Update annotations.md + traceability; keep a golden `.expected.mlw` (force-add).

**Expected outcome:** standard-size struct pack/unpack round-trips and sizes become provable (the os
inode-blit/read-back corpus discharges honestly), guarded by an in-range precondition; native alignment,
float encodings, and out-of-range packs remain the honest, documented residual.

---

## RESIDUALS CLOSED (autonomous, branch ghost-assign-bc6) — items 1–5

**Status: ALL FIVE RESIDUALS RESOLVED.** The single-slot faithful family (S1–S3 below)
was widened to a per-field width/signedness tag; the remaining boundaries are closed as
implemented-and-proven or evidence-backed documented boundaries.

- **Item 1 — MULTI-SLOT standard-int: DONE (implemented + proven + gated).** The blocker
  (the legacy `slot_id` encoded only WhyML types, so `'>HH'` and `'<ii'` collided on
  `struct_pack_i2`) is CLOSED by a per-field width/signedness-tagged `slot_id`
  (`struct_format.faithful_slots()` → tag-join; `'>HH'`=`u16u16` vs `'<ii'`=`i32i32` are
  now distinct symbols). Faithful multi-slot shapes `u16u32` (`'>HI'`, unsigned) and
  `i32i32` (`'<ii'`, signed) carry per-field in-range `requires`, a size law, and a guarded
  tuple round-trip axiom anchored by concrete byte-codec Rocq+Lean proofs
  (`0777`/`0778.proofs/{rocq,lean}/StructResiduals.*`: `round_trip_u16u32`, `round_trip_i32i32`,
  size + guard-necessity). Drivers `0777` (u16u32 round-trip + size, PROVES), `0780`
  (out-of-range field, `# pycsl-expected: FAIL`). `coqc` exit 0 / `lean` exit 0 / `--audit-proof`
  green.
- **Item 2 — SIGNED integers (`h`/`i`/`l`/`q`): DONE.** Two's-complement byte codecs for
  `i16` (`'>h'`), `i32` (`'>i'`/`'>l'`), `i64` (`'>q'`), signed range guard
  `[-2^(8N-1), 2^(8N-1))`. Round-trip proven across the WHOLE range (positive/negative halves +
  INT_MIN) in Rocq+Lean (`round_trip_i16/i32/i64`, derived from the unsigned round-trip via a
  modular two's-complement argument; `urt64` = 8-digit base-256 telescoping — NO width was
  intractable). Driver `0778` (i16/i32/i64 round-trip + size, PROVES), `0781` (out-of-range,
  FAIL).
- **Item 3 — floats + `s`/`p`: DONE (`s`) / DOCUMENTED-YAGNI (`f`/`d`).** Fixed-bytes `s4`
  (`'>4s'`) implemented as byte-array identity `unpack(pack d)==d` under `len(d)==N`, size law,
  cited proof (`round_trip_s4`/`size_s4`, `firstn 4 d = d`). Driver `0779` (PROVES). `p`
  (Pascal) kept as size-law-only legacy boundary (length-prefix byte makes the round-trip
  conditional). **Float `f`/`d`: DOCUMENTED YAGNI exit (UB §7.4c) with the specific failing
  step** — the IEEE-754 sign/exponent/mantissa bit-extraction does NOT lower to PyCSL's int/real
  model (no `real → bits` total function / no bit-cast in scope); size law kept, round-trip
  opacity note added, no faked axiom.
- **Item 4 — native (`@`) alignment: CLOSED-AS-BOUNDARY (REJECTED + UB rule).** A `'@'`-prefixed
  format is now REJECTED at transpilation with a clear diagnostic
  (`expressions.py:_handle_struct_call`; `calcsize()` also returns `None` for `'@'`). New UB
  catalog rule **§7.4b**. Rejection (not silent opacity) chosen because native size/padding is
  platform-dependent and an opaque model could carry a wrongly-sized `len(...)` claim. Negative
  driver `0782` (FAIL with UB-7.4b). No existing `.py` corpus program uses `'@'` → zero
  regression.
- **Item 5 — S4 per-field / S5 os re-key: CLOSED-AS-SUPERSEDED (definitive).** `0665`'s
  zero-trust pure-Python body codec (`pack16`/`pack32`/`pack_inode`) already gives the os inode
  blit/read-back an honest, AXIOM-FREE round-trip (axiom-registry.md cautionary note: removing all
  struct citations left os "fully proven, 0 unproven goals"). Re-keying os to any struct axiom
  would RE-INTRODUCE an axiom it no longer needs — so S5 is SUPERSEDED, not pending. S4 per-field:
  for the single-slot faithful shapes the field IS the value (round-trip delivers it); the new
  multi-slot round-trip delivers each field via tuple projection (drivers `0777`/`0778` prove
  `\result == field_k`); a separate per-field content axiom is subsumed and, for wide/legacy
  shapes, dominated by the `0665` body codec. Both verified by pointing at `0665` + the
  body-verified os (`0420`–`0425` + `0665` verify unchanged).

---

## EXECUTION RECORD (autonomous, cleared-pack) — original single-slot delivery

**Status: COMPLETE** (S0–S3 delivered; S4/S5 documented sound boundaries — see choices.md).

- **S0 — spike: GO.** `spikes/cleared-pack/pack_spike.mlw` + `S0-VERDICT.md`. Guarded round-trip Valid
  on Alt-Ergo (8 steps) & Z3; concrete byte model proves the guard load-bearing
  (`unpack(pack 65536)=0≠65536`); unguarded law correctly not provable (Timeout). Commit c4646dc9.
- **S1 size law + S2 in-range guard + S3 round-trip — DONE** for a single standard-size UNSIGNED-int
  slot (`'>H'`=u16, `'>I'`/`'>L'`=u32) via the new `Pycsl.Struct.Std` family
  (`struct_format.faithful_uint_slot()` → `struct_{pack,unpack}_fu16/fu32`). Pack `val` carries the size
  `ensures` (`length=calcsize`) AND the in-range `requires` (a call-site VC; faithful to CPython's
  out-of-range `struct.error`). Round-trip is a cited axiom `Pycsl.Struct.Std.round_trip_u{16,32}`.
  Commit 57fae2a2.
- **Cited Rocq+Lean anchor.** `test-suite/corpus/pycsl-reference/0753.proofs/{rocq/Struct.v,lean/Struct.lean}`:
  pack/unpack DEFINED as concrete big-endian base-256 byte codecs; theorems `round_trip_u16/u32`,
  `size_u16/u32`, `guard_necessity_u16/u32`. Rocq `coqc` exit 0 (no Admitted/Axiom); Lean 4.31 exit 0
  (`#print axioms ⊆ {propext, Classical.choice, Quot.sound}`, no sorry). `pycsl --audit-proof 0753`: 8/8.
- **Reference drivers.** `0753.py` (positive: round-trip + size law, u16 & u32 — PROVES) and `0754.py`
  (`# pycsl-expected: FAIL` negative: out-of-range value ⇒ guard is load-bearing — FAILS as required).
- **S4 (per-field extraction): YAGNI exit** — single-slot ⇒ the field IS the value; multi-slot per-field
  content is already zero-trust via 0665's body codec. See choices.md.
- **S5 (os re-key): documented boundary** — os multi-slot formats are out of the single-slot faithful
  scope, AND the body-verified os already eliminated the struct axiom (0665-style codec), so re-keying
  would RE-INTRODUCE an axiom it no longer needs. See choices.md.
- **Docs.** axiom-registry.md (+`Pycsl.Struct.Std.*` row), abstract-op.md, UB catalog §7.4a
  (out-of-range → `struct.error`, native alignment, signed/float/multi-slot residual), traceability
  12.5.6. doc-coherency `--check`: green. Commit 7c310b3e.
- **Gates.** Existing struct tests 0420–0425 + 0665 verify unchanged (faithful path is scoped to
  single-slot standard-uint formats; emission inert elsewhere). Full corpus sweep: see final report.
  `proof_axiom_allowlist` unchanged (cited axioms go through the registry + `--audit-proof`).
  Mirror-sync (`bin/sync-mirror-bodies.py`) NOT run — `libcst` unavailable in this environment;
  the changed emitter files are not in the self-annotation suite (which runs only `errors.py`), so no
  self-annotation regression; changes are additive.
