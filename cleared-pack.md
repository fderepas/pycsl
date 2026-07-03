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
