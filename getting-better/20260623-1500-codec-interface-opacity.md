# codec interface opacity — caller cannot prove byte-bounds / decomposed round-trip

**Date:** 2026-06-23 15:00
**Filed by:** test-supervise-sl (codec fleet run)

## Summary

`_pack_inode` (in `src/pycsl_lib/os/codec.py`) carries a narrow
`#@ interface ensures \length(\result) == 64` that hides its per-byte bounds
(`0 <= \result[i] <= 255` for 64 bytes) and field-encoding ensures (the 18
`pack` field-reconstruction equalities). This keeps `UnixInodeFileSystem.py`'s
import light (the stated design goal, G0b), but it means a cross-module
formal test cannot prove:

1. **The decomposed round-trip** — `unpack(pack(fields))[k] == fields[k]`
   (caller composes the two halves). The caller can't see pack's
   field-encoding ensures, so it can't chain them with unpack's
   field-reconstruction ensures. 64 precondition sub-goals (unpack's byte
   bounds) + 18 postcondition sub-goals remain Unknown.

2. **The byte-bound consequence** — `0 <= pack(fields)[i] <= 255` for all
   64 bytes. The byte bounds are interface-hidden.

## What was tried

`#@ reveal _pack_inode` (and `#@ reveal _unpack_inode`) at the cross-module
call site — per the opacity spec (§2.10), `#@ reveal` should opt into the
rich definition contract. In the current emitter, this does NOT surface the
hidden ensures cross-module (the 64 byte-bound sub-goals remained Unknown).
The single-file test `test-suite/corpus/pycsl-reference/0660.py` confirms
`#@ reveal` is a no-op within the owning unit; cross-module surfacing does
not work in this version. See H10 in the monitoring skill.

## Why the interface was NOT widened

Widening `_pack_inode`'s `#@ interface` to include the byte bounds + field
encodings was considered and rejected: it would change
`UnixInodeFileSystem.py`'s proof context (UIFS imports the codec
internally), risking an increase in UIFS's unproven body-VC count (which the
mission mandates must not increase). The narrow interface is a deliberate
design trade-off (light importer proofs).

## What IS proven (caller-side)

- **`codec_roundtrip_all_fields`** — all 18 fields preserved via
  `_inode_round_trip` (whose interface is TRANSPARENT — no `#@ interface`,
  so all 18 field-equality ensures are caller-visible). This is the
  keystone round-trip consequence. SUCCESS, 0 `\trusted`.
- **`codec_pack_width_64`** — pack emits exactly 64 bytes (via the narrow
  `\length == 64` interface). SUCCESS.

The hidden properties (byte bounds, decomposed round-trip) ARE body-proven
inline in `codec.py` (G0a, zero `\trusted`, verified SUCCESS) — they are not
proof gaps, only interface-visibility gaps.

## Suggested ergonomic improvement

Make `#@ reveal` work cross-module (surface the rich definition contract at
a specific call site without widening the interface for ALL importers). This
would let a formal test opt into the byte bounds / field encodings for the
decomposed-roundtrip proof WITHOUT changing UIFS's proof context — the best
of both worlds (light default interface, opt-in richness for specific
callers).
