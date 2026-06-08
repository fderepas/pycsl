# os-bodyvc-spec.md (rev2) — LEAF-FIRST: correct pack/unpack contracts before any syscall body-VC

**Date:** 2026-06-08
**Status:** Spec (rev. 2, leaf-first — reviewer feedback incorporated; no code changed)
**Owner:** PyCSL [TOOL] (`src/pycsl/**`) for L0, then [STDLIB] (`pure_lib/os/**`) for L1–L3
**Origin:** 08-1537-req-rev2 — the 21 mkdir/unlink/access goals failed the no_inline soundness gate
(sys_* don't prove standalone). Rev1 of this spec jumped straight to syscall body-VCs. **That was
wrong.** ([[os-coverage-progress]])

**Reviewer correction (the thesis of rev2):** *start with leaf functions; without correct leaves it is
not going to work.* The syscall body-VCs can never prove **value** properties (what files/inodes
actually contain) while the byte pack/unpack leaves only assert **length**. Example given:
`_pack_uint16_be` must say not just `\length(\result) == 2` but that the bytes RECONSTRUCT the input —
`\result[0]*256 + \result[1] == v` for `0 <= v <= 0xFFFF`. Rev1 specified the roof before the
foundation.

---

## 0. What "leaf-first" exposed immediately (measured)

Strengthening `_pack_uint16_be` to the value postcondition does NOT prove — and the reason is a
**[TOOL] gap**, not a contract or solver issue:

```
ensures { ((subscript_get result 0) * 256 + (subscript_get result 1)) = v }   (* emitted *)
```
**`\result[i]` in a contract lowers to the OPAQUE `subscript_get result i`, not the real
`Array.get` (`result[i]`).** `subscript_get` is uninterpreted, so nothing connects `\result[0]` to the
bytes the body actually wrote — the value postcondition is unprovable *by construction*.

**Confirmed:** hand-patching the emitted `.mlw` to use real `result[i]` makes it **prove (12/12 Valid)**
— the body already carries the link (`bytes_new` has `ensures result[i] = x[i]`), and `(v/256)*256 +
v%256 == v` is the div/mod identity. So the leaf is provable; only the opaque `subscript_get` in the
*contract* blocks it.

**This gap blocks EVERY value postcondition over an array result or array field** — i.e. all of
inode/direntry/disk content reasoning. It must be fixed first. This is precisely the leaf-first point:
the lowest layer (how `\result[i]` even lowers) was the real blocker, invisible from the syscall layer.

## 1. The layer stack (fix bottom-up; each layer is a prerequisite for the next)

| Layer | Owner | Content | Prereq |
|---|---|---|---|
| **L0** | [TOOL] | contract/spec `\result[i]` and array-field `[i]` → `Array.get`, not `subscript_get` | — |
| **L1** | [STDLIB] | `_pack/_unpack_uint16/32_be` — VALUE contracts + round-trip | L0 |
| **L2** | [STDLIB] | `_pack/_unpack_inode`, `_pack/_unpack_direntry` — field-wise round-trip | L1 |
| **L3** | [STDLIB] | `sys_mkdir/unlink/access` body-VCs (then `#@ no_inline`, clearing the 21) | L2 |

### L0 — [TOOL] contract array-indexing → `Array.get`  (THE foundation)
`_handle_subscript` (`expressions.py:1483`, `subscript_get` fallback at :1648) emits the opaque op when
the indexed object isn't a recognized array *local*. In **spec context** the object can be `\result`
(a `Result` node) or a self-field, whose array-ness is known from `_func_return_type` / the field type
but isn't checked. **Fix:** when `self._in_spec` (or `invariant_ctx`) and the object is array-typed —
`Result` with `_func_return_type == "array int"`, or an array-typed field/param — emit `<obj>[index]`
(`Array.get`) instead of `subscript_get`. Gate: a driver whose `ensures \result[0]*256+\result[1]==v`
proves (the `_pack_uint16_be` shape); corpus byte-identical (the change only fires where the type is
known — opaque cases still use `subscript_get`).

*Grammar note:* the contract grammar has **no `<<`** (parse error). State byte composition
arithmetically — `\result[0]*256 + \result[1] == v` — equivalently and provably (the bit-shift body
maps to `/256`,`%256`). Adding `<<`/`>>` to the contract grammar is an optional [TOOL] nicety, NOT
required; `*256`/`//256` suffice and prove. (If the *body* keeps bitwise `(v>>8)&0xFF`, that lowers to
uninterpreted `bit_*` ops and the value post won't prove — so either write the body arithmetically
`v//256, v%256` (equal for `0<=v<=0xFFFF`, recommended) or add a cross-validated bit↔arith lemma.)

### L1 — [STDLIB] byte pack/unpack leaves (value + round-trip)
```python
#@ requires 0 <= v and v <= 65535
#@ assigns \nothing
#@ ensures \length(\result) == 2
#@ ensures 0 <= \result[0] and \result[0] <= 255 and 0 <= \result[1] and \result[1] <= 255
#@ ensures \result[0] * 256 + \result[1] == v        # the bytes reconstruct v
def _pack_uint16_be(v: int) -> list:
    return bytes([v // 256, v % 256])                 # arithmetic body (= the bitwise one for v<=0xFFFF)

#@ requires \valid(data, 2) and offset >= 0 and 0 <= data[offset] <= 255 and 0 <= data[offset+1] <= 255
#@ assigns \nothing
#@ ensures \result == data[offset] * 256 + data[offset+1]   # exact value, not just >= 0
#@ ensures 0 <= \result and \result <= 65535
def _unpack_uint16_be(data: list, offset: int) -> int: ...
```
…and `_pack/_unpack_uint32_be` analogously (`* 16777216 + …`). The **round-trip lemma is then free**:
`_unpack_uint16_be(_pack_uint16_be(v), 0) == v` — the property every disk read/write ultimately needs.
(Today's `ensures \result >= 0` / `\length == 2` are too weak — they assert nothing about content.)

### L2 — [STDLIB] inode/direntry pack/unpack (field-wise round-trip)
`_pack_inode`/`_unpack_inode` (18 fields) and `_pack_direntry`/`_unpack_direntry` compose the L1 leaves.
Contract each field: `_unpack_inode(_pack_inode(fields))[k] == fields[k]`. Provable once L1's value
contracts hold (they currently can't be expressed — L0). This is what lets `_read_inode` after
`_write_inode` recover the inode — the missing link under every syscall's "Unknown" postcondition.

### L3 — [STDLIB] syscall body-VCs (now on a correct base)
With L1/L2 giving real value+round-trip facts, `sys_mkdir`/`sys_unlink`/`sys_access` can prove
standalone (then `#@ no_inline` per the `open` template, clearing the 21). The remaining work here is
the *structural* VCs rev1 listed — Type-invariant (`\length(disk)==131072` through slice-writes),
Index-bounds (`p_block*512+i*32 < 131072`), Array-creation-size, callee Preconditions — via intermediate
`#@ assert`s + tightened helper contracts (`_alloc_inode`/`_alloc_block`/`_write_entry` ranges), lemma
only as last resort. **Carry-overs from `open`:** the `pathname: str` no_inline param boundary (str the
caller chain per wrapper) and body-derived comma-`writes` `assigns`.

## 2. Phasing & acceptance (bottom-up; each gates the next)
1. **L0** — `\result[i]`/array-field `[i]` → `Array.get` in spec. Accept: the `_pack_uint16_be` value
   driver proves; corpus byte-identical; doc-coherency green. **Nothing above starts until L0 lands.**
2. **L1** — uint pack/unpack value+round-trip contracts prove (drivers per function + a round-trip driver).
3. **L2** — inode/direntry field-wise round-trip proves.
4. **L3** — each sys_* proves standalone (the 08-1537-rev2 soundness gate, now passable) → `#@ no_inline`
   → the 21 wrapper goals clear. Target os 23 → as low as 2; count each method only when it actually
   proves (not projected). Full os proof + os formal_0001 18/18 + corpus each step.

## 3. Risks
- **L0 blast radius** — array indexing appears in many contracts; the fix must fire ONLY where the
  array type is known (else regress opaque cases). Byte-identical corpus is the gate.
- **Body-vs-contract bitwise** — if [STDLIB] wants to keep bitwise bodies (`(v>>8)&0xFF`) for fidelity,
  the value post needs a cross-validated bit↔arith lemma; the arithmetic body avoids it and is equal
  under the `<= 0xFFFF` precondition. Recommend arithmetic bodies for the pack leaves.
- **L3 Type-invariant-over-131072-array** may still need the `slice_write_preserves_length` lemma
  (rev1 §7) — unchanged, but now downstream of correct leaves rather than blocking everything.

> **In one line (rev2):** the spec was wrong to start at the syscalls — leaf-first, the very first
> thing the byte-pack leaf needs (`\result[0]*256+\result[1]==v`) can't even be *expressed* because
> contract `\result[i]` lowers to the opaque `subscript_get` instead of `Array.get` (confirmed: patch
> it and the leaf proves 12/12). So **L0 is a [TOOL] fix** (spec array-indexing → `Array.get`), then
> L1 pack/unpack value+round-trip, then L2 inode/direntry round-trip, then L3 the syscall body-VCs —
> bottom-up, each layer a prerequisite, because without correct leaves the syscall proofs have nothing
> true to build on.
