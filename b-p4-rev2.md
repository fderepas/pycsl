# b-p4-rev2.md — Track B Phase P4, re-examined: the requires-bloat is faithful, so don't totalize

**Date:** 2026-06-08 (my independent rev. of `b-p4.md`)
**Status:** Analysis + revised plan. P0–P3 **committed** (`b3d65d1`); the os-alone diagnostic
(`bt30bvc8a`) **timed out at 1200s**; `_pack_inode` reverted to its committed light contract.
**Owner:** [STDLIB] + [TOOL].
**Relationship to `b-p4.md`:** I agree with its diagnosis and its covariance argument, and I credit its
clean framing. **I disagree with its central recommendation (Form A / "totalize the leaves").** Verified
facts show the leaves are *genuinely partial* (Python raises out-of-range), so totalizing is **unfaithful**
— it trades the project's faithfulness doctrine for proof affordability. This document argues the
requires-bloat is not a defect to dodge but the codec's *real precondition surfacing*, and its faithful
home is **Track C (an invariant that supplies the ranges)** or **the standalone round-trip (status quo)**
— not an unfaithful leaf totalization.

---

## 1. Status since `b-p4.md` was written (its S0/S1 are done)

- **S0 (read `bt30bvc8a`):** done. The os proof, run **alone** (no concurrent load), **timed out at
  1200s with 0 prover results** — so the 18 field-range `requires` are *as fatal as the ensures-bloat
  was*, not merely numerous. The byte-diff already pinned them as the only semantic change.
- **S1 (commit the sound B feature):** done — `b3d65d1` (P0–P3: parse `#@ interface`/`#@ reveal`,
  narrowing VC, interface-on-stub; driver 0660; corpus 0 confirmed fails; os held at 23). The B feature
  is sound and finished. `b-impl.md §12` documents the requires finding.

So the open question is *only* §3 of `b-p4.md` — the leaf restructure — and that is where I depart.

## 2. Where I agree with `b-p4.md`

- **The requires-bloat is real and is not a B bug.** B narrows *ensures* (covariant — a function may
  promise less); a *requires* is contravariant — it may never demand less than the body needs, so the
  narrowing VC **correctly rejects** `\valid ⟹ \valid ∧ ranges` (fail-loud). That rejection is the tool
  working.
- **Opacity cannot hide a requires**, and **HAPPY does not apply** (it injects per-write *checks*, i.e.
  obligations; a requires needs an *assumable* value at the call — the dual). Both correct.
- So the requires must be **eliminated at the source**, not hidden. The disagreement is over *what
  "eliminate" may faithfully mean.*

## 3. The objection `b-p4.md` misses: totalizing the leaves is **unfaithful**

`b-p4.md` Form A makes `_pack_uint16_be` "total — callable on any int," dropping `requires 0<=v<=65535`
and guarding the value ensures. **But the real function is not total.**

> **Provenance (source of truth: `pure_lib/os/UnixInodeFileSystem.py`, the actual symbol — not a
> reconstruction).** The committed function is, verbatim:
> ```python
> def _pack_uint16_be(v: int) -> list:
>     return bytes([v // 256, v % 256])
> ```
> Loaded from that file and **executed**:
> ```
> _pack_uint16_be(65535) = b'\xff\xff'
> _pack_uint16_be(70000) -> ValueError: bytes must be in range(0, 256)   # 70000//256 = 273 > 255
> ```
> (Methodology note, 2026-06-08: an earlier check ran a *hand-typed* `bytes([70000//256, 70000%256])`
> snippet — a reconstruction that happened to match the body but was not the real symbol. This claim is
> now grounded by importing and calling the actual function. Behavioral claims must be verified against
> the real symbol, never a retyped approximation.)

So `_pack_uint16_be`'s body `bytes([v//256, v%256])` **raises `ValueError` for `v > 65535`.** The
committed leaf models this faithfully: `#@ requires 0 <= v and v <= 65535`. The precondition is *real* —
it is the domain on which the function returns rather than raises.

- **Form A says the function returns (a length-2 array) for any int.** That is false; for `v>65535` it
  raises. Form A therefore **misrepresents the codec's control flow** — exactly the "modeling convenience
  over faithful semantics" the project has repeatedly rejected (memory: *semantics-vs-modeling*,
  *no-more-int*; the user "prefers faithful semantics over convenience," e.g. faithful `KeyError` for
  dict reads).
- **Form B (wrapping, `v mod 65536`) is worse** — it claims the function silently truncates when it
  actually *raises*. (It also likely trips the contract grammar, which has no `<<`/`>>` and uncertain
  `mod` support — but the semantic objection is the real one.)
- **The faithful "total" form would be `raises ValueError when not (0<=v<=65535)`** — and that
  *reintroduces the bloat*: `_pack_inode` calling the leaf would **propagate the raise**, so its callers
  must prove no-raise (i.e. establish the ranges) to call it. Faithful ⇒ the range obligation returns.

> **Therefore there is no faithful *and* affordable totalization.** The requires-bloat is *inherent to
> the faithful model*: the leaves genuinely need the ranges (or raise), so `_pack_inode` genuinely needs
> them, so any caller does. Form A escapes the bloat *only by lying about the codec.*

## 4. The faithful resolutions (the real choice P4 forces)

| Option | Faithful? | Affordable in os? | Notes |
|---|---|---|---|
| **(a) Keep real preconditions** | ✓ | ✗ | the requires-bloat → os times out (`bt30bvc8a`). The honest cost of a verified faithful codec inside os. |
| **(b) Model the raise** (`raises ValueError when out-of-range`) | ✓ | ✗ | callers must prove no-raise ⇒ need the ranges ⇒ same bloat, faithfully. |
| **(c) Ranges hold by CONSTRUCTION — supply them via an invariant** | ✓ | ✓ (if reachable) | inode fields are bounded by their *type* (a uint16 field ∈ [0,65535]). A **representation/type invariant** discharges the ranges once, not per call. **This is Track C.** Gated on **L0″** (functions/logic-view in invariants — the earlier C-probe wall). |
| **(d) Status quo: standalone round-trip (0658) + light os `_pack_inode`** | ✓ | ✓ | already faithful and affordable — the codec round-trip is proven standalone with the *real* preconditions; os uses a light codec. Just not "in os." |
| **(e) Form A — totalize** | **✗** | ✓ | b-p4.md's pick; affordable but unfaithful (§3). |

**The requires-bloat is the signal pointing at (c).** The reason the fields are in range is that the
filesystem *maintains* them in range — which is precisely a representation invariant, i.e. Track C's
coupling/`Valid()` predicate. `b-p4.md §10` dismisses C as "heavier and incomplete for freshly-built
inodes," but a freshly-built inode is built from *typed* fields that are in range by construction — the
invariant covers it. So C is not incomplete here; it is the *faithful* discharge of the very requires
that totalizing would unfaithfully erase.

## 5. Recommendation (my departure from `b-p4.md`)

**Do not totalize the leaves.** It is the wrong trade under this project's faithfulness doctrine, and
the requires-bloat it dodges is real codec semantics, not noise.

1. **Keep the leaves faithful** (real `requires 0<=v<=65535`, as committed). Do **not** run b-p4.md
   S2–S6.
2. **Recognize P4-via-B is the wrong vehicle for `_pack_inode`.** B (ensures-opacity) is done and
   general; it cannot carry a function whose *precondition* is the bloat. The inode round-trip's faithful
   in-os home is **Track C** (the representation invariant supplies the field ranges), which is gated on
   **L0″** (the unbound-function-in-invariant wall from `challenging-the-plan2.md`).
3. **Until C is reachable, the faithful resting point is (d):** the round-trip proven standalone (0658,
   real preconditions) + a light os `_pack_inode`. This is already true and already faithful — no
   unfaithful change buys anything it doesn't already have.
4. **If — and only if — the user explicitly accepts the faithfulness trade** (modeling the leaves as
   total for verification leverage, knowing Python raises), Form A becomes available, but as an
   **explicit, ledgered modeling divergence** ("`_pack_uint{16,32}_be` modeled total; Python raises
   `ValueError` out-of-range"), never the silent default. I would not choose it.

**So the user's prompt "take on L1" (totalize) is, by my read, the move to *not* make** — or to make
only with eyes open about the faithfulness cost. The faithful next step is **L0″ → C**, or accept (d).

## 6. What is actually worth doing now

- **B feature: nothing more** — it is committed, sound, general (any importer of any rich-contract
  function benefits). It was never the blocker for the *requires* side; that was always a codec-domain
  question.
- **For the inode round-trip:** the decision is **C (faithful, needs L0″) vs status-quo (d)** — not
  totalize. If pursuing C, L0″ (let a class invariant reference a logic view of the codec) is the gating
  tool fix, and the representation invariant `∀k. fields[k] ∈ range_k` is what discharges the ranges
  faithfully and once.
- **One cheap probe** worth running before committing to C: confirm a *typed* inode record (fields
  carrying their `[0,MAX]` bounds as a record/type invariant) discharges `_pack_inode`'s real
  preconditions at a call site **without** the per-call bloat — i.e. that C's invariant actually
  collapses the 18×8 obligations. (Reason to design the probe; run it to decide — the discipline that
  has overturned every estimate so far.)

## 7. Revised plan of record

| Step | Action | Gate |
|---|---|---|
| **R0** | (done) B feature committed `b3d65d1`; requires finding in `b-impl.md §12` | ✓ |
| **R1** | **Do not totalize.** Record the faithfulness objection (§3) so Form A is not silently adopted | this doc |
| **R2** | Probe (§6): does a typed-inode representation invariant discharge `_pack_inode`'s real range requires at a call site without per-call bloat? | **[PROVE/measure]** ranges discharged from the invariant; no 18×8 blowup |
| **R3a** | If R2 green and L0″ landed → pursue **Track C** (abstract inode + coupling invariant; round-trip consumed once at `_write_inode`) | os holds at 23 *faithfully* |
| **R3b** | If C is out of reach → **accept (d)**: standalone round-trip (0658) + light os codec is the faithful-affordable resting point; stop | no regression; documented |
| **R4** | *(only on explicit user opt-in)* Form A as a ledgered modeling divergence | ledger entry; os at 23 with the divergence noted |

## 8. Soundness / faithfulness ledger

- **The committed leaves stay faithful** — real `requires`, reflecting the real `ValueError` domain.
- **Totalizing is a faithfulness divergence, not a soundness hole** — Form A is *sound* (a total leaf is
  a consistent spec); it is *unfaithful* (it doesn't match Python). The distinction matters here because
  the project optimizes for faithfulness, so this belongs in the modeling ledger, gated on explicit
  consent — exactly the place `\trusted`-style trust assumptions are recorded.
- **B is unchanged and sound.** This analysis adds no mechanism; it is a *decision* about the codec's
  domain model.

> **In one line:** `b-p4.md` is right that the requires-bloat is real and that opacity/HAPPY can't fix
> it — but its fix (totalize the leaves) is **unfaithful**: `_pack_uint16_be` genuinely raises
> `ValueError` out-of-range (verified), so "callable on any int" lies about the codec, and a *faithful*
> total form (`raises …`) just reintroduces the bloat. There is no faithful-and-affordable totalization;
> the requires-bloat is the codec's real precondition surfacing, and its faithful home is **Track C** (a
> representation invariant that supplies the field ranges by construction, gated on L0″) or the
> **already-faithful status quo** (standalone round-trip 0658 + light os codec) — *not* a leaf
> totalization. Keep the leaves faithful; decide C-vs-standalone; reach for Form A only as an explicit,
> ledgered modeling divergence the user opts into.
