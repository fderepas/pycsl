# Faithful `bytes` / `bytearray` / `struct` value model — status

This note tracks the phased plan to give PyCSL a faithful `bytes`/`bytearray` value model, and records
what is **DONE** versus the remaining **follow-on**. It is the doc referenced by
`wrong-lowering-to-fix.md` §WL-06 and the translational reference §T.15.

## The τ-blessed baseline (kept)

A `bytes`/`bytearray` value lowers to the coarse `array int` buffer (`τ(bytes)=int†`, translational
§T.15.1). This SHAPE is deliberate and unchanged — every phase below is **additive** on top of it.

## Phase status

| Phase | Content | Status |
|---|---|---|
| P1 | `bytes` literal → `ArrayLit` of the REAL byte values (Module5 `_py_expr_constant`); `b'\x00'*N` composes with the `[default]*size → Array.make` handler | ✅ DONE (translational §T.15.2) |
| P1a | `bytes(...)`/`bytearray(...)` constructor → `array int` (length/element contract) | ✅ DONE (test 0616) |
| P1a+ | constructor `ValueError`-as-precondition — `bytes([v])`/`bytearray([v])` raises `ValueError` for `v ∉ [0,256)`; modelled as `requires 0<=x[i]<256` on `bytes_new`/`bytearray_new` so an out-of-range element FAILS CLOSED (was: severity-1 unsound `bytes([300])[0]==300` proved a false normal-return) | ✅ DONE — **WL-06d** (translational §T.15.9; locks 0867/0868; spike `wl06d_str_encode_literal_spike.mlw`) |
| — | coherent `b[i]` READ (`Array.get`) + `len(b)` (`Array.length`) — no more broken `subscript_get` | ✅ DONE — **WL-06** (translational §T.15.6; locks 0824/0825) |
| — | faithful byte CONTENT of a `bytes` **LITERAL** (exact value reads PROVE) + byte-RANGE invariant `0 <= b[i] < 256` (derivable, no axiom) | ✅ DONE — **WL-06b** (translational §T.15.7; locks 0835/0836; spike `wl06b_bytes_content_spike.mlw`) |
| — | `bytes` **immutability** — a `bytes` element write `b[i]=v` is REJECTED (Python `TypeError`); `bytearray` element write stays a sound mutable array mutation | ✅ DONE — **WL-06b** (`core_ir_semantic._sa_immutable_walk`; locks 0837/0838) |
| P2a | byte-RANGE invariant `0 <= b[i] < 256` of an *unknown* `bytes`/`bytearray` **PARAMETER** — emitted as an IMPLICIT precondition (a type-level guarantee); range read PROVES with no user `requires`, specific-value claim stays UNPROVEN | ✅ DONE — **WL-06c** (`functions._bytes_param_range_requires`; translational §T.15.8; locks 0862/0863/0864; spike `wl06c_bytes_param_range_spike.mlw`) |
| P2b | EXACT CONTENT of an *unknown* `bytes` **PARAMETER** — the individual byte VALUES stay opaque `int` cells (coherent, distinct-index independent, now range-bounded); only a user `requires`/element bound can pin a value | ⛔ FOLLOW-ON |
| P3 | `str ↔ bytes` `.encode` / `.decode` (UTF-8 / ASCII round-trip) | 🟡 PARTIAL — ASCII str-LITERAL `.encode()` byte CONTENT is faithful (**WL-06d**, translational §T.15.9; locks 0865/0866; `_encode_string_literal`); a NON-literal / NON-ASCII `.encode()` and `.decode()` (beyond the cited field-decode idiom) stay opaque (documented boundary) |
| P4 | byte-string methods `.ljust` / `.split` / `.strip` / `.hex` | ⛔ FOLLOW-ON — audited SOUND (opaque / fail-closed TYPEERR: `.hex` and bytes `+` are TYPEERR; `.ljust`/`.rjust` carry a length law only; `b[i:j]` is opaque `array_slice`) |
| P5 | full `struct.pack` / `struct.unpack` round-trip **beyond** what cleared-pack (`Pycsl.Struct.*`) already gives | ⛔ FOLLOW-ON — audited SOUND (whitelisted scalar/`4s` shapes are faithful+cited; every non-whitelisted shape is opaque; extending needs a new Rocq+Lean round-trip proof, never `\trusted`) |

## What "DONE" means precisely (WL-06 + WL-06b)

- A `bytes`/`bytearray` `b[i]` read is a well-typed native `Array.get` (`int`), IndexError-guarded; `len(b)`
  is `Array.length b`.
- A `bytes` **literal**'s bytes are the exact Python byte values, so `b"abc"[0] == 97`,
  `b"\x01\xff\x80"[1] == 255` PROVE, `0 <= b[i] < 256` is derivable, and a false byte value stays UNPROVEN.
- A `bytes` value is **immutable**: `b[i] = v` is rejected (`PYCSL-SEM-SUBSCRIPT`); a `bytearray`/`list`
  is the mutable byte buffer.

## What "FOLLOW-ON" means

- The EXACT byte VALUE of a `bytes` **parameter** is unknown at compile time — its `b[i]` denotes a
  coherent but opaque `int` cell (body `b[i]` == contract `b[i]`, distinct indices independent). It is now
  RANGE-bounded (`0 <= b[i] < 256`, implicit, WL-06c / P2a) but the specific value is pinned only by an
  explicit `#@ requires` element bound.
- `encode`/`decode` and deeper `struct`/byte-method semantics would need format-string-aware emission plus
  cited round-trip lemmas (Rocq/Lean), NOT `\trusted` — out of scope of the wrong-lowering campaign.
