# A-spec.md — Track A: round-trip lemma extraction + selective `#@ uses` (opacity by hand)

**Date:** 2026-06-08
**Status:** Spec (for review — no code changed)
**Owner:** [STDLIB] (`pure_lib/**`) primary + **small** [TOOL] (`src/pycsl/**`) confirmation/enablement
**Origin:** `opaque-and-refine.md` §6 Track A; `try.md` §3.6 (the leaf-compositional breakthrough) and
§3.7–3.9 (the module-granularity wall and the "park it in drivers" resolution it forces).
**Concept:** **opacity by hand** — Why3-native, via PyCSL's existing `#@ lemma` / `#@ uses`.
**Relationship:** A is the *special case* of Track B (manual citation vs a first-class
opaque-on-export/`reveal` feature). A and Track C each keep os affordable; **A is the cheapest** — it
reuses drivers 0657/0658 and the `#@ lemma`/`#@ uses` surface that already exists.

---

## 1. Goal & non-goal

**Goal.** Make the inode-codec round-trip a **first-class, citable proven fact** that a
faithfulness-needing proof can *use*, **without** its rich (18-field) contract ever riding
`_pack_inode`'s import stub into the **8 syscall call sites** — so os stays affordable (held at 23)
*and* the round-trip is **connected to the model** rather than parked in isolated drivers
(0657/0658, the current `try.md` §3.9 stand-in).

**Non-goal.** Reducing the 23 remaining *return-code* goals (that is `08-1537`'s `#@ no_inline` work —
the syscalls prove return codes and *do not need* the round-trip). Building the opaque-export feature
(Track B). Abstracting the inode away (Track C). Bridging to Rocq/Lean (Track D). Other codecs
(direntry etc. — same pattern, fold in later).

A is a **faithfulness-enabler kept cheap**, not a count-reducer: it turns "the codec round-trip is
proven *in isolation*" into "the codec round-trip is a *citable lemma in the os model*," at near-zero
proof-cost to the syscalls that don't need it.

## 2. The mechanism: a *lemma*, not a *contract*

The entire wall (`try.md` §3.7) is that the round-trip, *as 18 field-ensures on `_pack_inode`'s `val`
stub*, is reproduced at **every** call site (8 × 18 ≈ 144 heap-laden hypotheses), even in syscalls that
never read back. The fix is to change *where the round-trip lives*:

> A **contract on the function** emits its facts at **every call**. A **lemma** is **one quantified
> fact**, in scope **only where `use`d**, instantiated **only where its trigger matches**.

So Track A:
- **Keeps `_pack_inode`'s interface contract at `\length == 64`** — *everywhere*, including the codec
  unit. The rich 18-field facts are **never** a function contract (this is the key difference from
  Track B, which gives `_pack_inode` two contracts).
- **States the round-trip as a `#@ lemma round_trip`**, proven **leaf-compositionally** (the §3.6
  breakthrough), in a codec lemma unit where `_pack_inode`/`_unpack_inode` **bodies** are available
  (a `#@ lemma` is verified in-toolchain with bodies, so the leaf composition discharges it).
- **Reveals it via `#@ uses round_trip`** in — and only in — a proof that needs read-back.

This is **opacity by hand**: the round-trip is hidden by default (not on any stub), `reveal`ed
manually (`#@ uses`) exactly where needed. A syscall proving a return code never cites it, so it
carries **none** of the 18 facts.

## 3. The lemma, precisely

```
#@ lemma round_trip:
#@     \forall fields.
#@         \valid(fields, 18) ==>
#@         \forall k. 0 <= k and k < 18 ==>
#@             _unpack_inode(_pack_inode(fields))[k] == fields[k]
```

- **Proof:** the leaf-compositional `_pack_inode` (calls `_pack_uint{16,32}_be` and copies their bytes;
  each field-ensures follows from the leaf's value contract — `try.md` §3.6) composed with
  `_unpack_inode`. **Already validated standalone** (0658 proves exactly this; 0657 the uint case). No
  fresh div/mod over the 64-byte array, so it **beats the array-state wall by composition** — zero
  Rocq/Lean/axiom.
- **Trigger:** the `_unpack_inode(_pack_inode ·)` pattern, so the lemma fires only on read-back goals
  and never speculatively in unrelated syscall contexts.
- **Crucially, the lemma references the *symbols* `_pack_inode`/`_unpack_inode`, not their
  contracts.** Once proven, it is a standalone quantified fact; a client that `use`s it gets the fact,
  **not** the 18 field-ensures (those were never anywhere but inside this lemma's own proof).

## 4. Unit structure (the opacity boundary)

| Unit | `_pack_inode` contract seen | Has the round-trip? |
|---|---|---|
| `UnixInodeFileSystem` / `os/__init__` (the shared model) | **`\length == 64`** (narrow — unchanged from §3.9) | **No** — never on the stub |
| codec lemma unit (promotes 0658) | `\length == 64` *as contract*; **bodies inlined for the lemma proof** | **Yes** — `#@ lemma round_trip`, proven leaf-compositionally |
| a faithfulness-needing client (read-back driver / future syscall goal) | `\length == 64` | **cites** it via `#@ uses round_trip` |

The boundary is exactly "the round-trip is a *lemma*, parked outside the function contract; clients
opt in." Because A puts the round-trip **only** in the lemma (never as a second contract on
`_pack_inode`), it needs **no** two-contract / narrowed-import feature — that is what distinguishes A
(possible today) from B (a tool feature).

## 5. What A enables

A read-back goal — e.g. a driver (and later a real syscall) that writes then reads the same inode:

```python
#@ uses round_trip
#@ ensures \result == fields[k]          # the inode I wrote is the inode I read
def write_then_read_field(n, fields, k): ...
    self._write_inode(n, fields)         # disk[512+64n:+64] := _pack_inode(fields)
    out = self._read_inode(n)            # _unpack_inode(disk[512+64n:+64])
    return out[k]
```

proves via the cited `round_trip` (given the slice is undisturbed — see §8 note), while the **other 7
syscalls** (return-code goals) **do not** cite it and carry none of the 18 facts. **os holds at 23**;
the round-trip is now a model-connected, reusable fact instead of a parked driver.

## 6. The [TOOL] question — P0 probe (decides whether A is [STDLIB]-only)

PyCSL already has `#@ lemma` (Module4 `_validate_lemma`) and `#@ uses` (lemma ordering, per the static-
semantics reference). P0 measures whether they already do the three things A needs:

1. **Prove** a `#@ lemma` whose body composes `_pack_inode`/`_unpack_inode` (needs their bodies /
   leaf-compositional facts) — expected yes (it's the 0658 proof as a lemma).
2. **Cite** it via `#@ uses round_trip` so the **quantified proposition** enters *one function's* proof
   context — **without** re-inlining `_pack_inode` or re-introducing its rich field facts.
3. **Scope** it: a function that does **not** `#@ uses` it sees nothing extra (no bloat).

- **If all three hold → A is [STDLIB]-only** (write the lemma; cite it; measure). No tool work.
- **If (2)/(3) leak** (citing drags `_pack_inode`'s body/contract, or the lemma globalizes) → that is
  the small, scoped **[TOOL]** gap: *scoped lemma citation* (export a lemma; `#@ uses` brings the
  proposition into one context only). P0 turns "little/no tool work" from a hope into a measurement.

## 7. Soundness

- **Established, not assumed.** `round_trip` is **proven** (leaf-composition; 0657/0658), discharged by
  Why3/SMT — not an axiom. **No TCB growth.**
- **The narrow interface is sound.** `\length == 64` is a true *under-statement* of the codec's
  behaviour; opacity **narrows, never widens** — a client can only rely on *less* than is true, never
  more. (Reusing a lemma adds a *proven* fact, not an assumed one.)
- **Anti-`\trusted` (fail-loud).** A deliberately-false `round_trip` **fails the lemma's own proof** in
  the codec unit — it cannot pass and silently mislead a client (the lemma is proven, then used; an
  unproven lemma is rejected, not propagated).
- **Fail-safe on the mechanism.** If P0 shows `#@ uses` cannot scope the lemma, **os is not modified**:
  the round-trip stays in drivers (status quo, no regression) until the scoped-citation [TOOL] gap
  closes. The unsafe outcome (rich facts silently bloating, or a wrong narrowing) never occurs.

## 8. Blast radius & gating

os is **byte-identical** except the one function that `#@ uses round_trip`; the other syscalls are
untouched. os **holds at 23** (or improves, if a read-back goal was the thing failing). Gate each step:
codec unit proves `round_trip` standalone (have, via 0658), the citing driver proves, full
`bin/run-reference-tests.sh --pycsl` byte-diff/PASS, os `formal_0001` 18/18, stdlib-coverage +
doc-coherency green.

*Frame note (defer to C/§HAPPY).* The read-back example assumes `_write_inode(n,…)` left the slice it
reads undisturbed. Proving *that* (a write to inode `n` doesn't disturb inode `m`'s slice) is the
**HAPPY confinement / refinement** problem of Track C — A does **not** solve it; A makes the *codec*
fact citable. A read-back driver in A should therefore read back **immediately** after the write (no
intervening writes), so the slice-preservation obligation is trivial; the general case is C.

## 9. Phasing

| Phase | Delivers | Gate | Owner |
|---|---|---|---|
| **P0** | feasibility probe (§6): cite `round_trip` in a minimal read-back driver cross-unit; measure scope (bloat? rich-contract drag?) | the driver PROVES and os is byte-identical with the lemma *uncited* elsewhere; **decides [STDLIB]-only vs small [TOOL] gap** | [TOOL] |
| **P1** | promote the round-trip from 0658's driver assertions to a first-class **`#@ lemma round_trip`** in the codec unit; prove it leaf-compositionally | **[PROVE]** `round_trip` standalone; **[typecheck]** `_pack_inode`'s contract is still `\length == 64` (no rich contract on the stub) | [STDLIB] |
| **P2** | a read-back driver that **`#@ uses round_trip`** and proves `\result == fields[k]` (immediate read-after-write, §8) | **[PROVE]** the driver; **[byte-diff]** os byte-identical, held at 23; **[PROVE-neg]** a false `round_trip` fails the codec unit's own proof | [STDLIB] |
| **P3** *(only if P0 found a gap)* | **scoped lemma citation**: export a lemma; `#@ uses` brings the proposition into one function's context without dragging `_pack_inode`'s body/contract | **[PROVE]** P2 with the citing function carrying *only* the round-trip fact (measured: no extra heap hypotheses) | [TOOL] |
| **P4** *(optional)* | wire a real syscall read-back goal where meaningful (immediate read-after-write) | **[PROVE]**; corpus PASS | [STDLIB] |

P0 gates everything; P1/P2 are the deliverable; P3 is contingent on P0; P4 is opportunistic.

## 10. Acceptance criteria

1. `round_trip` is a **first-class proven `#@ lemma`** (not driver-parked) — **[PROVE]**.
2. A read-back driver proves `\result == fields[k]` via **`#@ uses round_trip`** — **[PROVE]**.
3. os is **byte-identical** for syscalls that do not cite the lemma; **held at 23** — **[byte-diff]**.
4. A deliberately-false `round_trip` **fails the codec unit's own proof**, never a client — **[PROVE-neg]**.
5. `_pack_inode`'s interface contract remains **`\length == 64`** (no rich contract on the os stub) —
   **[typecheck/inspect]**.
6. If P0 found a gap, the citing function carries **only** the round-trip fact (measured: no extra
   heap-laden hypotheses at the other 7 sites) — **[measure]**.

## 11. Relationship to B / C / D

- **B (opacity as a feature)** generalizes A: A's `#@ uses` is a manual `reveal`; B gives `_pack_inode`
  *two contracts* (narrow interface + rich definition) with first-class `reveal`/export. **Graduate
  A→B when interface-narrowing recurs** across codecs/serializers and hand-written lemmas multiply.
- **C (refinement + HAPPY)** is the principled sibling: instead of citing a codec lemma, the syscalls
  reason over an **abstract inode** and never touch the bytes, with HAPPY confining each write so the
  coupling invariant stays affordable. A's §8 frame note is exactly what C discharges.
- **D (Rocq/Lean bridge)** can supply `round_trip`'s proof **kernel-checked and solver-independent**
  (durability) underneath A — exposed as the *same* opaque lemma, cited the *same* way; A's `#@ uses`
  is the citation surface either way. D is a *durability layer under A*, not a replacement.

## 12. Out of scope

The `#@ no_inline` return-code work (`08-1537`); the opaque-on-export feature (Track B); the abstract
inode view + HAPPY confinement (Track C); the Rocq/Lean realization (Track D); non-inode codecs
(`_pack_direntry`/`_unpack_direntry` — identical lemma pattern, fold in once the inode lemma lands);
the general (non-immediate) read-back / slice-preservation obligation (Track C).

> **In one line:** keep `_pack_inode` narrow (`\length == 64`) *everywhere* and put the round-trip in a
> proven **`#@ lemma`** (leaf-compositional, = drivers 0657/0658 promoted), revealed only where needed
> via **`#@ uses`** — so a read-back proof can cite the codec's faithfulness while the 7 return-code
> syscalls carry none of the 18 field-facts; os stays at 23, the round-trip becomes a model-connected
> citable fact instead of a parked driver, and the only open question (P0) is whether PyCSL's existing
> `#@ lemma`/`#@ uses` already scope the citation — if not, that small scoped-citation gap is the sole
> [TOOL] work, with os left untouched (fail-loud) until it closes.
