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
| — | coherent `b[i]` READ (`Array.get`) + `len(b)` (`Array.length`) — no more broken `subscript_get` | ✅ DONE — **WL-06** (translational §T.15.6; locks 0824/0825) |
| — | faithful byte CONTENT of a `bytes` **LITERAL** (exact value reads PROVE) + byte-RANGE invariant `0 <= b[i] < 256` (derivable, no axiom) | ✅ DONE — **WL-06b** (translational §T.15.7; locks 0835/0836; spike `wl06b_bytes_content_spike.mlw`) |
| — | `bytes` **immutability** — a `bytes` element write `b[i]=v` is REJECTED (Python `TypeError`); `bytearray` element write stays a sound mutable array mutation | ✅ DONE — **WL-06b** (`core_ir_semantic._sa_immutable_walk`; locks 0837/0838) |
| P2 | CONTENT of an *unknown* `bytes` (a **PARAMETER**) — currently opaque `int` cells (coherent, distinct-index independent); only a user `requires`/element bound can constrain it | ⛔ FOLLOW-ON |
| P3 | `str ↔ bytes` `.encode` / `.decode` (UTF-8 / ASCII round-trip) | ⛔ FOLLOW-ON |
| P4 | byte-string methods `.ljust` / `.split` / `.strip` / `.hex` | ⛔ FOLLOW-ON |
| P5 | full `struct.pack` / `struct.unpack` round-trip **beyond** what cleared-pack (`Pycsl.Struct.*`) already gives | ⛔ FOLLOW-ON (cleared-pack round-trip DONE separately) |

## What "DONE" means precisely (WL-06 + WL-06b)

- A `bytes`/`bytearray` `b[i]` read is a well-typed native `Array.get` (`int`), IndexError-guarded; `len(b)`
  is `Array.length b`.
- A `bytes` **literal**'s bytes are the exact Python byte values, so `b"abc"[0] == 97`,
  `b"\x01\xff\x80"[1] == 255` PROVE, `0 <= b[i] < 256` is derivable, and a false byte value stays UNPROVEN.
- A `bytes` value is **immutable**: `b[i] = v` is rejected (`PYCSL-SEM-SUBSCRIPT`); a `bytearray`/`list`
  is the mutable byte buffer.

## What "FOLLOW-ON" means

- The CONTENT of a `bytes` **parameter** is unknown at compile time — its `b[i]` denotes a coherent but
  opaque `int` cell (body `b[i]` == contract `b[i]`, distinct indices independent). Constrain it with an
  explicit `#@ requires` element bound.
- `encode`/`decode` and deeper `struct`/byte-method semantics would need format-string-aware emission plus
  cited round-trip lemmas (Rocq/Lean), NOT `\trusted` — out of scope of the wrong-lowering campaign.
