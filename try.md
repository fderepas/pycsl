# try.md — the leaf-compositional inode round-trip: context, the wall, and every solution tried

**Date:** 2026-06-08
**Status:** Retrospective (what worked, what didn't, and why)
**Scope:** the attempt to prove `_unpack_inode(_pack_inode(x))[k] == x[k]` for the os inode codec —
the L2 rung of `os-bodyvc-spec.md`. Outcome: **round-trip proven standalone (drivers 0657/0658);
cannot be folded into the whole-os proof at acceptable cost** — a module-granularity limit, not a
soundness or expressivity one.

---

## 1. Context — how we got to the inode round-trip

### 1.1 The os module and the "remaining 23"
`pure_lib/os/` is PyCSL's Unix-filesystem stdlib model: a `UnixInodeFileSystem` class holding a
131072-byte `disk: array int`, with syscalls (`sys_open`, `sys_write`, `sys_mkdir`, …) and a binary
inode/direntry codec (`_pack_inode`/`_unpack_inode`, `_pack_uint{16,32}_be`/`_unpack_*`). Over this
session the os unproven-goal count was driven **47 → 23**:
- 47 → 45: fixed `sys_write`'s false loop invariant.
- 45 → 39: `#@ no_inline` modular boundary on `sys_write` (proves standalone; callers reuse its
  contract instead of re-proving the inlined body).
- 39 → 33: `Return_seq` + `.append()`-as-seq-growth (array-returning functions with early returns).
- 33 → 23: `#@ no_inline` on `sys_open` (`os.open`'s 10 blow-ups).

The remaining 23 are postcondition goals on the disk-mutating syscalls (`makedirs`/`unlink`/`mkdir`/
`access`/…). They failed the no_inline **soundness gate** — the `sys_*` don't prove standalone (their
bodies have Type-invariant + bounds + array-creation VCs over the 131072-byte disk). So they need
**body-VC work**, not no_inline.

### 1.2 The reviewer's correction: leaf-first
The first `os-bodyvc-spec` jumped straight to the syscall body-VCs. The reviewer's correction was
decisive: **"start with leaf functions; without correct leaves it is not going to work."** A verified
os whose `_read_inode`/`_write_inode` don't provably round-trip is hollow — the syscalls sit on a codec
whose *value* behaviour is unspecified. Concretely: `_pack_uint16_be` must say not just
`\length(\result) == 2` but that the bytes **reconstruct** the input — `\result[0]*256 + \result[1]
== v` — and `_unpack` must be its inverse. So the work was re-ordered bottom-up:

```
L0  [TOOL]    contract `\result[i]` must lower to Array.get, not opaque subscript_get
L1  [STDLIB]  byte pack/unpack leaves: VALUE + inverse contracts
L2  [STDLIB]  inode/direntry codec: field-wise round-trip (THIS DOC)
L3  [STDLIB]  syscall body-VCs (sits above L2)
```

### 1.3 The goal of L2
Prove `_unpack_inode(_pack_inode(fields))[k] == fields[k]` for all 18 inode fields — i.e. the codec is
a faithful, invertible serialization. This is *model correctness*: it is what would let a syscall prove
"the inode I wrote is the inode I read." (The remaining 23 syscall goals are *return codes* and don't
need it — but a meaningful os model does.)

---

## 2. The layered difficulty (three distinct walls)

The round-trip turned out to sit on top of **three independent obstacles**, each invisible from the
layer above. Leaf-first surfaced them one at a time.

1. **Tool gaps** (L0, L2-arg, L2-passthrough) — the round-trip couldn't even be *expressed* or *composed*
   until three transpiler gaps were closed.
2. **The SMT array-state wall** — proving byte-decomposition over a 64-element array times out, even
   though the identical fact proves over a 4-element array.
3. **Module-granularity / import-propagation** — a rich contract on a function *imported* by os bloats
   every call site in the os proof, and there's no way to import a *narrowed* contract.

The first wall was *crossable* (tool fixes). The second was *crossable by composition* (the technical
win). The third is *architectural* — and is why the round-trip can't live in the os module today.

---

## 3. Solutions tried (chronological, with evidence)

### 3.1 L0 — contract array-indexing → `Array.get` (`1a38500`)
**Tried:** strengthen `_pack_uint16_be` with `\result[0]*256 + \result[1] == v`.
**Found:** it didn't prove — the emitted ensures was `(subscript_get result 0) * 256 + … == v`. In a
contract, `\result[i]` lowered to the **opaque `subscript_get`** (an uninterpreted `val`), not real
`Array.get` — so nothing connected `\result[0]` to the bytes the body wrote. **No value postcondition
over an array result could even be expressed.**
**Proof of diagnosis:** hand-patching the `.mlw` to `result[0]` → proved **12/12 Valid**.
**Fix:** `_handle_subscript` now emits `result[i]` (Array.get) for a `Result` node in spec context when
`_func_return_type == "array int"` (a logic term, no bounds-assert wrapper). Opaque-typed reads still
fall through to `subscript_get`. Driver 0655. Corpus byte-identical (the branch fires only where the
array type is known). **This was the true foundation — invisible from the syscall layer.**

*Side note (grammar):* `<<` is not in the contract grammar (parse error after `<`). Byte composition is
written arithmetically — `\result[0]*256 + \result[1]` — which is equivalent and provable.

### 3.2 L1 — leaf value + inverse contracts (`7978d61`)
**Tried:** value+inverse contracts on all four uint leaves (`_pack/_unpack_uint{16,32}_be`).
**Found:** the bodies were *bitwise* (`(v>>8)&0xFF`), which lower to **uninterpreted** `bit_*` ops — the
value post won't prove from a bitwise body without a lemma. Rewriting the body arithmetically
(`v//256`, `v%256`) — exactly equal under the `0<=v<=0xFFFF` precondition — proves directly (div/mod).
Also fixed a genuine bug: `_unpack`'s precondition was `\valid(data, 2)` (absolute), which does NOT
bound `data[offset]`/`data[offset+1]` for arbitrary `offset` → corrected to `\valid(data, offset+2)`.
**Result:** all four leaves prove standalone with value contracts. The round-trip is now *expressible*.

### 3.3 L2 sub-gap 1 — seq→array arg-materialize (`6adaaf4`)
**Tried:** the existing `_pack_inode` (`parts = []; parts += _pack_*(…); return bytes(parts)`).
**Found:** `parts` is seq-promoted (grown via `+=`), so `bytes(parts)` is `bytes(seq int)` but
`bytes_new` expects `array int` → Why3 **`@rho` type error**. The real `_pack_inode` *failed to even
generate standalone* — it only ever worked because it's inlined.
**Fix:** `_materialize_if_seq` bridges a `_seq_locals` arg seq→array via the return-arr `materialize`
val, applied at the `bytes()`/`bytearray()` handler — extending materialize from *return* boundaries to
*call-arg* boundaries. `_pack_inode` now generates standalone. Driver 0656.

### 3.4 L2 sub-gap 2 — array-returning call args pass through coercion (`922d5e6`)
**Tried:** the round-trip by contract composition — `unpack16(pack16(x), 0) == x`.
**Found:** it failed; the emitted body was `(unpack16 (Array.make 1 0) 0)` — `pack16(x)` (an
array-returning **call**) was **clobbered to a placeholder** `(Array.make 1 0)` by `_array_coerce_arg`
(a string heuristic that recognized `Array.make`/`Array.get`/identifiers but not a function
application). The value of `pack16(x)` was discarded, so the round-trip had nothing to compose.
**Fix:** a function-application arg `(fn arg…)` / array-literal `(let _alit …)` now passes through;
only genuinely-scalar args (`0`, numeric exprs) get the placeholder.
**Result:** **`unpack16(pack16(x), 0) == x` proves purely by contract composition** (driver 0657) — no
body tracking. This is the mechanism the whole stack was building toward.

### 3.5 Inode pack, attempt A — direct write-at-offsets + field contracts (REVERTED)
**Tried:** restructure `_pack_inode` to `out = [0]*64; out[k] = fields[f]//…` (write each byte
arithmetically at its known offset, block loop unrolled), with 18 per-field VALUE ensures
(`\result[o]*2^24 + … == fields[k]`).
**Found:** the body generates cleanly and **proves `\length == 64` standalone**, but the per-field
value ensures **TIME OUT**. The single unproven goal was a **Timeout** (the ensures were correctly
lowered to `Array.get`, not subscript_get). The *identical* 4-term uint32 decomposition that proved in
the 4-byte LEAF (`_pack_uint32_be`) times out here because the solver **re-derives the div/mod while
carrying all 64 `out[i]` assignments** — the large-array state. Even reducing to *two* field contracts
still timed out. **This is the SMT array-state wall.**
**Reverted** — a function can't partially prove.

### 3.6 Inode pack, attempt B — leaf-COMPOSITIONAL (THE BREAKTHROUGH; proved standalone but reverted)
**Insight:** don't make SMT re-derive the byte arithmetic over the big array — **reuse the leaf's
already-proven contract**. Pack each field by CALLING the leaf and COPYING its bytes:
```python
out = [0] * 64
b0 = _pack_uint32_be(fields[0]); out[0]=b0[0]; out[1]=b0[1]; out[2]=b0[2]; out[3]=b0[3]
b1 = _pack_uint16_be(fields[1]); out[4]=b1[0]; out[5]=b1[1]
…  # all 18 fields
return bytes(out)
```
Then the field ensures `out[0]*2^24 + … == fields[0]` follows from `_pack_uint32_be`'s ensures
(`b0[0]*2^24 + … == fields[0]`) plus `out[0..3] == b0[0..3]` — **by composition, no fresh div/mod
proof**. This is the same mechanism as §3.4-passthrough, lifted one level.
**Found:** the full 18-field `_pack_inode` **proves all 18 field-value ensures standalone** (`--fun`,
~minutes). **Composition beat the array-state wall with zero Rocq/Lean/axiom.** (Validated first on a
focused 64-byte / 2-field probe, then scaled.) This is the technical win of the whole exercise.
**But:** see §3.7 — it can't be committed to the os module.

### 3.7 Full os integration — the proof-cost / module-granularity wall (REVERTED)
**Tried:** run the whole-os proof (`pycsl.py pure_lib/os/__init__.py`) with the leaf-compositional,
18-field `_pack_inode`.
**Found:** the os proof **did not complete in 1700s** (0 prover results emitted), even though os
**generates in 3s** — so it's *pure proof cost*, not a generation hang or a regression.
**Root cause (measured in the os `.mlw`):** `_pack_inode` is **imported** by `os/__init__` and emitted
as a **`val` stub** (`val _pack_inode (fields: array int) : array int`) — it is *already modular, not
inlined*; the os proof **assumes** its contract (the body is verified separately in the
`UnixInodeFileSystem` unit). The stub carries the function's **full contract = 19 ensures** (1 length +
18 field), and `_pack_inode` is **called at 8 sites**. So all 18 field ensures propagate into all 8
syscall proof contexts (≈144 extra heap-laden hypotheses), and the solver drowns — the syscalls don't
*need* the field values (they prove return codes) but must carry them.

### 3.8 `#@ no_inline` on `_pack_inode` — confirmed NO-OP (REVERTED)
**Tried:** the hypothesis that a modular boundary would let os reuse `_pack_inode`'s contract cheaply.
**Found (empirically):** `_pack_inode` is **already a modular `val` import-stub** — it was never
inlined. `#@ no_inline` targets *inlined methods on module-global instances*; applied to a free
imported function it is a **no-op**: the os `.mlw` still showed `val _pack_inode` carrying all **19
ensures**. The bloat is the contract propagating to call sites, which `no_inline` does not touch. And
the import propagates the *full* contract — there is no mechanism to import a *narrowed* one.

### 3.9 Resolution (`82e0129`, `a76a781`) — prove it standalone, keep os light
- `_pack_inode` keeps its LIGHT contract (`\length == 64`) in the shared module → **os holds at 23**.
- The codec round-trip is proven in **isolated drivers**: 0657 (uint round-trip), 0658 (inode-codec
  round-trip — pack via leaf-composition + unpack, `roundtrip(x,y) == x`).
- The leaf-compositional **technique** and the round-trip **property** are both verified; the os module
  stays affordable.

---

## 4. The three root causes, named

| Wall | Nature | Crossable? | How |
|---|---|---|---|
| **Tool gaps** (L0/L2-arg/L2-pass) | the round-trip couldn't be expressed/composed | ✅ yes | three transpiler fixes (subscript→Array.get, arg-materialize, call-arg passthrough) |
| **SMT array-state** | re-deriving byte math over a 64-element array times out | ✅ yes | **compose from the proven leaf** instead of re-deriving (zero external proof) |
| **Module-granularity** | a rich contract on an *imported* function bloats every os call site; no narrowed import | ⛔ no (today) | would need **true separate compilation**: verify `_pack_inode` in its own unit, import a reduced contract |

## 5. What is proven vs not
- **Proven (standalone, committed):** all 4 uint leaves' value+inverse contracts (L1); the uint
  round-trip by composition (0657); the inode-codec round-trip by leaf-composition (0658); the full
  18-field `_pack_inode` field contracts *standalone* (demonstrated, then reverted from the module).
- **Not in the os model:** the inode round-trip as a contract on os's `_pack_inode` — blocked by the
  module-granularity wall (§3.7/§3.8), not by soundness or SMT.
- **os:** held at **23** throughout; no regression.

## 6. Lessons (now in skills csl-philosophy / pycsl-annotate / pycsl-stdlib-coverage)
1. **Leaf-first.** Fix the leaves (value+round-trip contracts) before composers/top; each layer surfaces
   the one foundational gap beneath it (L0 and the L2 arg-materialize were both invisible from the top).
2. **Compose, don't re-derive.** The cheapest escape from "SMT can't" over a large state is to reuse an
   already-proven leaf contract by composition — cheaper than a cross-validated lemma, and far cheaper
   than discharging the raw VC.
3. **Proof-TIME ≠ provability.** A contract that proves in `--fun` can make the whole-module proof
   intractable. Verifiability and verification-cost are distinct constraints.
4. **Contracts on an imported function are not free at the boundary.** They ride the import stub into
   every caller's context. A heavy/rich contract wants either a modular boundary that *narrows* on
   import (separate compilation) or to stay out of the shared module.
5. **`#@ no_inline` is for inlined methods, not imported free functions** — know which mechanism a
   symbol uses before reaching for a boundary directive.

## 7. The path forward (if the round-trip must live *in* the os model)
True separate compilation: verify `UnixInodeFileSystem`'s codec (`_pack_inode`/`_unpack_inode`) as its
own verification unit with the full 18-field round-trip contracts, then have `os/__init__` import a
**narrowed** contract (`\length == 64`) — so the syscall proofs aren't bloated while the codec's
round-trip is still established. That's a transpiler/architecture change (per-unit compilation +
contract narrowing on import) PyCSL doesn't support today; the isolated drivers (0657/0658) are the
current, honest stand-in.
