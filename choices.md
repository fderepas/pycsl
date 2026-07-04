# choices.md — autonomous-execution decision log

Decisions made without supervision during the autonomous execution of
`cleared-pack.md` → `cleared-hash.md` → `cleared-array.md` → `cleared-string.md`.
Standing directive: **always favor rigor**; spend the time to do things well.

Each entry: `## <plan> — <decision>` then **Context / Options / Choice / Rationale**.

---

## cleared-pack S0 — scope the faithful path to single-slot standard integer formats; keep legacy abstract family as documented boundary

**Context.** `struct.pack`/`struct.unpack` lower (expressions.py `_handle_struct_call`) to
abstract `val function struct_pack_<slot_id>`/`struct_unpack_<slot_id>` symbols. `slot_id`
(struct_format.py) encodes only WhyML *types* (`iN` for N int slots), NOT the format chars'
ranges — so `'>HH'` (two uint16) and `'<ii'` (two int32) COLLIDE on `struct_pack_i2`. A single
faithful in-range guard per `slot_id` is therefore either unsound (widest range lets a truncating
value through) or useless (narrowest = bool). The existing `UnixFs.Struct.{i1a1,i2,i18}.round_trip`
axioms are UNGUARDED shape-model witnesses (`struct_pack_i2 := [x0;x1]`, proven by `reflexivity`);
they are consumed by the deep, slow, vacuity-prone os corpus (`src/pycsl_lib/os/UnixInodeFileSystem.py`)
and 5 green corpus tests (0420-0425). Separately, **0665** already realises the *superior* body-faithful
route: hand-written byte codecs (`pack16`/`pack32`/`pack_inode`) that prove the guarded round-trip by
SMT COMPOSITION of value contracts with **zero axioms** — explicitly to ELIMINATE the i18 axiom.

**Options.**
1. Re-key ALL pack/unpack emission to a range-aware `slot_id` and re-verify os + rename the witness
   Coq/Lean module. Cleanest in theory; HIGH risk (destabilises the heavy os proof base I cannot cheaply
   re-verify) and large churn (witness rename, os re-key).
2. Attach a single guard per existing `slot_id`. Unsound (collision) or useless.
3. Route ONLY single-slot pure-integer STANDARD formats (`'>H'`,`'>I'`, ...) — which NO existing
   test/os uses (all existing slots are multi-slot/array: i1a1,i2,i18) — through a NEW faithful path
   with a WIDTH-tagged symbol (`struct_pack_fu16` etc.), size law (`length = calcsize`), in-range
   `requires` (faithful: real `struct.pack` RAISES `struct.error` out-of-range for standard sizes), and
   a guarded round-trip axiom anchored by cited Rocq+Lean byte-codec proofs. Leave legacy i1a1/i2/i18
   untouched (documented coarser boundary). Additive, sound (width in the symbol name ⇒ no collision),
   zero os churn, exercises the exact cited-proof mechanism the DoD names.

**Choice.** Option 3.

**Rationale.** Maximises rigor achievable without destabilising the os proof base: the faithful family
is byte-honest (size + guarded round-trip + guard-necessity all anchored by cross-validated Rocq+Lean),
the guard is load-bearing at BOTH the pack precondition (matches Python's out-of-range `struct.error`)
and the axiom antecedent, and the width tag makes it collision-sound. The legacy unguarded shape-model
axioms and the full-os re-key (plan S5) are recorded as a documented residual: 0665 already shows the
zero-trust body-faithful elimination path for i18, which supersedes re-keying the abstract family.

## cleared-pack S4 (per-field extraction) — YAGNI exit; documented boundary

**Context.** S4 asks for a per-field content law `unpack(data)[k] == <k-th field decode of data>`.
**Options.** (1) Add a per-field decode axiom over the abstract `struct_unpack_f*`; (2) skip.
**Choice.** Skip (documented boundary).
**Rationale.** The faithful family (S1–S3) targets a SINGLE-slot format, so "the k-th field" is the
whole value — the round-trip already delivers it (`unpack(pack x)==x`). A per-field content law only
adds value for MULTI-slot formats, which are out of the faithful family's scope (choices.md S0 entry).
The zero-trust way to get per-field content for multi-slot codecs already exists — the body-faithful
0665 codec exposes each field's exact byte-decode as an SMT-discharged `ensures` with NO axiom, which
strictly dominates a per-field abstract axiom. Adding an abstract per-field axiom here would be effort
on a hypothesis no corpus goal consumes (cf. the axiom-registry cautionary note on vestigial struct
axioms). Recorded as a residual in the UB catalog §7.4a.

## cleared-pack S5 (os corpus re-key) — keep os on legacy family; documented boundary

**Context.** S5 asks to re-verify the os inode blit/read-back corpus against the faithful round-trip.
**Options.** (1) Re-key `src/pycsl_lib/os/UnixInodeFileSystem.py` (multi-slot '>IHHHHHII10Ixx' / '>H30s')
to a faithful multi-slot family; (2) leave os as-is.
**Choice.** Leave os on its existing path (documented boundary).
**Rationale.** (a) The faithful family is single-slot by construction (S0 soundness scope); os uses
multi-slot formats, which would require the range-aware multi-slot machinery the S0 entry explicitly
deferred to avoid destabilising the heavy os proof base. (b) More decisively, the body-verified
`src/pycsl_lib/os` ALREADY eliminated the struct round-trip axiom via the 0665-style pure-Python byte
codec (see axiom-registry.md cautionary note: "removing all eight [citations] left the os fully proven,
0 unproven goals"). The os read-back is therefore ALREADY honest — re-keying it to a new faithful
struct axiom would RE-INTRODUCE an axiom the body-verified os no longer needs. The only os path still on
the abstract codec is the separate `struct.pack`-based stub, whose legacy `UnixFs.Struct.*` axioms are
retained and documented. No os regression: 0420–0425 + 0665 verify unchanged.
