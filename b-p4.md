# b-p4-spec.md — Track B, Phase P4: applying opacity to `_pack_inode` and clearing the requires-bloat

**Date:** 2026-06-08
**Status:** Plan (for execution — P0–P3 landed; P4 in progress, blocked on a newly-surfaced requires-bloat)
**Owner:** [STDLIB] (`pure_lib/os/**`, the leaf restructure) + [TOOL] (`src/pycsl/**`, only if a value-
ensures form is needed)
**Origin:** `B-spec-rev2.md` §10 P4; the P4 byte-diff finding (the os stub narrows the *ensures* to 1
but inherits 18 field-range *requires* that ride the 8 call sites).
**Depends on:** B's feature P0–P3 (✓ landed: emission shape, parse, narrowing VC, interface-on-stub).
**One-line problem:** B soundly narrowed `_pack_inode`'s **ensures** (19 → 1), but the leaf-compositional
body genuinely **requires** the 18 field ranges, and **a requires cannot be narrowed** (it is unsound —
the narrowing VC correctly rejects it). So the ensures-bloat became a **requires-bloat**. The fix is not
more opacity; it is to **totalize the leaves** so `_pack_inode` requires only `\valid`.

---

## 1. What P4 found (the requires-bloat)

P0–P3 validated B as a feature: the os `_pack_inode` stub carries **1 ensures** (`\length == 64`), not
19. But the P4 byte-diff (committed-light vs interface) showed the *only* semantic change is **18 added
`requires`**:
```
requires { 0 <= fields[0] && fields[0] <= 4294967295 }   (size,  uint32)
requires { 0 <= fields[1] && fields[1] <= 65535 }        (link_count, uint16)
…                                                         (18 field-range preconditions)
```
These are **real**: `_pack_inode`'s body calls `_pack_uint32_be(fields[0])`, whose contract *requires*
`0 ≤ v ≤ 4294967295`. To call its value-contracted leaves, `_pack_inode` must establish each field is in
range — so the ranges are a genuine precondition of the *current* leaf-compositional body. They now ride
the **8 syscall call sites** (each caller must discharge them), so os does **not** reach 23 even though
the ensures-bloat is gone.

## 2. Why this is not a B bug, and why opacity cannot fix it

- **Ensures are covariant; requires are contravariant.** B narrows *postconditions* soundly because a
  function may always *promise less* than it proves (`definition_ensures ⟹ interface_ensures`). A
  *precondition* may never *demand less* than the body needs — narrowing `\valid ⟹ \valid ∧ ranges`
  would let a caller pass an out-of-range field the body can't handle. **The narrowing VC correctly
  rejects it (fail-loud).** That rejection is the tool working, not a gap.
- **Consequence:** no opacity-style mechanism can hide a requires. A rich precondition is **eliminated
  by totalizing the callee**, never **hidden**. (And HAPPY does not apply: HAPPY injects per-write
  *checks*; a requires needs an *assumable value fact* at the call — the dual. HAPPY produces
  obligations, not assumptions.)

So P4's real task is a **leaf restructure**, orthogonal to the (now-finished, sound) B feature.

## 3. The fix — totalize the leaves (precondition-side dual of B's ensures-narrowing)

Make each `_pack_uint{16,32}_be` **total** — accept *any* `int`, dropping the range *requires* — and
move the range from a precondition to a **guard on the value ensures**. Two forms; pick per §4.

**Form A — conditional value-ensures (recommended; no body change to the math):**
```python
#@ requires \valid_int(v)            # total: no range bound
#@ assigns \nothing
#@ ensures \length(\result) == 2
#@ ensures 0 <= \result[0] and \result[0] <= 255
#@ ensures 0 <= \result[1] and \result[1] <= 255
#@ ensures (0 <= v and v <= 65535) ==> (\result[0] * 256 + \result[1] == v)   # value GUARDED by range
def _pack_uint16_be(v: int) -> list: ...
```
The reconstruction promise is now *conditional* on the range. The leaf is callable on any int (so
`_pack_inode` needs no per-field range requires); the value fact is still available exactly when the
caller can show the field is in range — which is precisely where the round-trip lemma uses it.

**Form B — honest wrapping (if the model should reflect real byte truncation):**
```python
#@ ensures \result[0] * 256 + \result[1] == v mod 65536    # unguarded: packing truncates
```
Matches what byte-packing physically does (`v & 0xFFFF`). Stronger (unconditional) but changes the
modelled semantics; only choose if wrapping is the intended behaviour.

After either, `_pack_inode`'s contract becomes:
```python
#@ requires \valid(fields, 18)       # ONLY this — the 18 range requires are gone
#@ assigns \nothing
#@ ensures \length(\result) == 64
#@ ...field-value ensures (now guarded, for the round-trip lemma)...
#@ interface ensures \length(\result) == 64
```

## 4. Where the 18 ranges go (they are eliminated, not lost)

The ranges do not vanish from the math — they relocate from **8 call-site preconditions** to **one
lemma hypothesis**:
- The **round-trip lemma** (`A`/`B`-revealed/`D`) assumes `\valid(fields,18) ∧ (∀k. fields[k] in range_k)`
  and proves `unpack(pack(fields)) == fields`. It is proven **once**, where the ranges are available.
- The **8 syscalls** no longer carry the ranges (they call a total `_pack_inode`), so the os stub is
  `\length == 64` on **both** ensures and requires → the wall-#3 bloat is fully gone on both sides.

This is the exact dual of B: B moved the rich *ensures* off the stub into a revealed definition; this
moves the rich *requires* off the stub into the leaves' guard + the lemma hypothesis.

## 5. Decision: Form A vs Form B

| | Form A (conditional ensures) | Form B (wrapping) |
|---|---|---|
| Leaf callable on any int | ✓ | ✓ |
| `_pack_inode` requires only `\valid` | ✓ | ✓ |
| Models real truncation | no (silent on out-of-range) | ✓ |
| Round-trip lemma | assumes ranges (where it always did) | needs ranges too (wrap is identity in-range) |
| Body math change | **none** | **none** (ensures only) |
| Risk | a caller that forgets the range gets no value fact (fails loud at the lemma) | changes modelled semantics; review intent |

**Recommend Form A** — it is the minimal, behaviour-preserving change: the leaf still does the same
arithmetic, only its *contract* is totalized, and the value guarantee is recovered exactly where a
caller can prove the range (the round-trip lemma). Form B only if the os model should explicitly reflect
byte truncation.

## 6. Immediate next step — read `bt30bvc8a` before committing the leaf change

The os-alone run (`bt30bvc8a`, 1200s, no concurrent load) is the diagnostic:
- **If it returns goals-up (not a timeout):** confirms the 18 requires are *dischargeable but numerous*
  — i.e. the requires-bloat is real but lighter than the ensures-bloat was. Proceed to the leaf
  restructure (§3) expecting it to clear them.
- **If it times out with 0 prover results:** the requires-bloat is as fatal as the ensures-bloat — same
  conclusion, same fix, more urgency.
- **Either way the byte-diff already pins the cause** (the 18 requires are the only semantic change), so
  the leaf restructure is the fix regardless; `bt30bvc8a` only tells you how much headroom you start
  from.

## 7. Plan of record

| Step | Action | Gate | Owner |
|---|---|---|---|
| **S0** | Read `bt30bvc8a` (§6); record goals-up vs timeout | diagnostic logged | — |
| **S1** | **Commit the sound B feature as-is** (P0–P3 + the parse/VC/emission). It is correct and done; scope the commit to "B: opacity feature" and **document the requires finding** (§2) in `B-spec` §4. | corpus byte-clean (already ✓); B feature tests green | [TOOL] |
| **S2** | Totalize the four leaves (`_pack/_unpack_uint{16,32}_be`) via **Form A** (§3); drop range *requires*, guard the value *ensures* | **[PROVE]** each leaf proves standalone; **[byte-diff]** body math unchanged | [STDLIB] |
| **S3** | Drop `_pack_inode`'s 18 range requires → `requires \valid(fields,18)` only; keep `#@ interface ensures \length==64` | **[PROVE]** `_pack_inode` proves standalone; **[inspect]** stub now has **1 ensures + `\valid` requires only** (no 18 ranges) | [STDLIB] |
| **S4** | Re-prove the **round-trip lemma** under the totalized leaves (it now carries the range hypothesis it always needed) | **[PROVE]** `unpack(pack(x))==x` under `\valid ∧ ranges` (drivers 0657/0658 form) | [STDLIB] |
| **S5** | **Re-run os alone** with the totalized leaves + narrowed stub | **[PROVE]** os **holds at 23** and **finishes fast** (both ensures- and requires-bloat gone); os `formal_0001` 18/18 | [STDLIB] |
| **S6** | Full corpus sweep | **[byte-diff]** corpus clean; doc-coherency + stdlib-coverage green | [STDLIB] |

S1 is independent and should land now (the feature is sound); S2–S5 are the inode application; S5 is the
decisive wall-#3 result.

## 8. Acceptance for P4

1. The B feature (P0–P3) is committed, sound, and the **requires finding is documented** in `B-spec`
   §4 — **[commit / doc]**.
2. The four leaves are **total** (callable on any int); their body math is **byte-identical** —
   **[PROVE / byte-diff]**.
3. `_pack_inode`'s os stub carries **1 ensures + `\valid` requires only** — **no 18 range requires** —
   **[inspect]**.
4. The round-trip lemma re-proves under the totalized leaves — **[PROVE]**.
5. **os holds at 23 and finishes fast** with both bloats gone — **[PROVE]** — the decisive P4 outcome.
6. Corpus byte-clean; formal_0001 18/18 — **[byte-diff / PROVE]**.

## 9. Soundness & fail-safe

- **No requires is hidden** — totalizing *eliminates* the precondition (the leaf is genuinely total),
  never narrows it (§2). The narrowing VC's rejection of requires-narrowing stays intact and correct.
- **The value guarantee is not lost** — Form A makes it *conditional* on the range, recovered exactly
  where a caller proves the range (the round-trip lemma); a caller that cannot prove the range simply
  gets no value fact and **fails loud** at the lemma, never a wrong proof.
- **B itself is unchanged and sound** — this plan adds no opacity mechanism; it is a leaf-contract
  change beneath B.
- **Fail-safe ordering:** S1 (commit the sound feature) is independent of S2–S5 (the inode application);
  if the leaf restructure stalls, the B feature still lands and os is unchanged (no regression).

## 10. Out of scope

- Changing B's mechanism (it is sound and finished — this is a *consumer-side* leaf fix).
- HAPPY (does not apply — §2: it checks writes, it cannot supply an assumable precondition value).
- Track C's abstract-inode view (the alternative philosophy; a maintained range *class invariant* would
  be C's way to supply read-modify-write ranges, but it is heavier and incomplete for freshly-built
  inodes — totalizing the leaves is cheaper and total).
- Other codecs (`_pack_direntry` etc. — same totalize-the-leaves pattern, fold in after the inode case).

> **In one line:** P4 proved B narrows the *ensures* soundly (os stub: 1, not 19), but exposed that
> `_pack_inode`'s leaf-compositional body genuinely *requires* the 18 field ranges — and a **requires
> cannot be narrowed** (unsound; the VC rightly rejects it, and HAPPY does not apply). The fix is the
> precondition-side dual of B: **totalize the four leaves** (accept any int; guard the value ensures on
> the range — Form A, no body-math change), so `_pack_inode` requires only `\valid`, the 18 ranges
> relocate from 8 call sites to the one round-trip lemma hypothesis, and os reaches **23, fast**, with
> the bloat gone on *both* the ensures and requires sides; commit the sound B feature now (S1), then
> apply the leaf restructure (S2–S6), reading `bt30bvc8a` first only to see how much headroom you start
> from.
