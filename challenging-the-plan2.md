# challenging-the-plan2.md — probing the A/B/C/D plan, round 2 (L0′ applied, C re-probed)

**Date:** 2026-06-08
**Status:** Probe report, round 2 (standalone; supersedes the forward-looking parts of
`challenging-the-plan.md`). The L0′ tool fix that round 1 *recommended* is now **applied**, and the
C-probe **re-run**. New finding: L0′ works and inline couplings scale — **but the realistic
function-call coupling hits a further wall.**
**Subject:** `opaque-and-refine.md`'s four tracks (A lemma-extraction, B opaque-on-export, C
data-refinement, D Rocq/Lean bridge) for putting the inode round-trip into the os model without the
proof-cost bloat. This document is self-contained: it recaps round 1, then reports round 2.

---

## 1. Recap of round 1 (`challenging-the-plan.md`)

The plan recommended **"A now (cheapest) → C as the principled target."** Two probes refuted it.

- **A-probe** — state the round-trip as a `#@ lemma` while the pack function keeps a LIGHT exported
  contract (the only way A avoids the import bloat). Result:
  - rich pack contract + lemma → **SUCCESS** (the quantified `∀x. unpack(pack(x))==x` proves);
  - light pack contract + lemma → **FAILED** (no field-value info to compose from).
  - **Verdict: A reduces to B.** The lemma needs the rich contract, which is exactly what rides the
    import stub into call sites; only opacity (B) can hide it. There is no cheap standalone A.

- **C-probe** — a coupling invariant `ginode[n] == unpack(disk[slice])`, the heart of refinement.
  Result: **FAILED to compile** — `self.disk[n]` in a class invariant lowered to an **unbound
  `subscript_get`** (the L0 array-indexing gap recurring for array *fields in class invariants*). The
  affordability question was **unreachable** — it didn't compile.
  - **Verdict: C is blocked on a tool prerequisite** (an L0-style fix), *before* its central
    affordability claim can be tested.

Round 1's recommended next step: **apply the L0′ fix → re-probe C affordability.** That is round 2.

---

## 2. L0′ — the fix, applied

Round 1 §4.1 specified the fix; it is now implemented (two parts):

1. **`preamble.py`** — during class-invariant emission, set `_current_self_type = type_name` (and
   restore). Root cause of the round-1 failure: that block set `_in_spec`/`_emit_record_ctx` but **not**
   `_current_self_type`, so `_field_type_of("self.disk")` returned `None` → the subscript handler's
   field branch never fired → unbound `subscript_get`.
2. **`expressions.py`** — an L0-style early return: for an array-typed `Attribute`/`FieldGet` in spec
   context, emit `(field[index])` (`Array.get`) directly — no bounds-assert wrapper (an invariant is a
   logic term). Mirrors the shipped L0 `Result`-node fix (`1a38500`), extended to field access.

**Gate status:** os formal_0001 **18/18**, corpus **0 confirmed fails** (os full-proof re-confirm in
flight at time of writing). The change fires only in spec context where the field's array type is
known, so body reads and opaque cases are byte-identical.

---

## 3. Round-2 finding: L0′ unblocks inline couplings AND they scale — but the realistic shape doesn't

With L0′ applied, three C-probes were run, escalating toward the real os shape.

### 3.1 Inline coupling, small — **PROVES (3s)**
The round-1 probe (8 inodes; `_v{n} == self.disk[2n]*256 + self.disk[2n+1]`; `write0` touches inode 0's
slice, the other 7 couplings preserved by frame) **now compiles and proves in 3s.** L0′ closed the
expressibility gap; the frame proof (other inodes untouched) is cheap.

### 3.2 Inline coupling, count-scaled — **PROVES (6s @ 32 inodes)**
Scaled to **32 inodes** (the os's `MAX_INODES`), same shape. **SUCCESS in 6s.** So the *count*
dimension — the per-write frame obligation over many inodes — **scales linearly and stays affordable.**
This directly answers round-1's open affordability worry *for inline couplings*: it is not a wall.

### 3.3 Function-call coupling (the REAL os shape) — **UNBOUND (1s)**
The real os coupling is `ginode[n] == unpack_inode(disk[slice])` — it **calls the unpack function**.
Probed minimally as `self._v0 == unpack16(self.disk, 0)` in a class invariant:

```
Verification FAILED — unbound function or predicate symbol 'unpack16'   (1s)
```

**A class invariant cannot call a module function**, because class invariants are emitted in the type
declaration (preamble), *before* the functions are declared. So the clean refinement shape — coupling
via `unpack_inode(...)` — does not even compile. This is **a new wall, distinct from L0′.**

---

## 4. The updated verdict on Track C

| C dimension | Round 2 result |
|---|---|
| Expressibility of array-field access in invariants (the round-1 blocker) | ✅ **fixed by L0′** |
| Inline coupling, frame over many inodes (the round-1 affordability worry) | ✅ **affordable** — 32 inodes, 6s, linear |
| Realistic coupling `ginode[n] == unpack_inode(disk[slice])` (function call in invariant) | ⛔ **unbound** — functions not in scope in a class invariant (new wall) |
| Inline alternative for the real 18-field inode (no function call) | ⚠️ untested, but would inline the 18-field byte math into the invariant × 32 inodes → re-introduces the SMT array-state cost in the invariant (the very wall §2/wall-#2 of `try.md`) |

**So Track C is *less* "just a refactor" than `opaque-and-refine.md` framed it.** It needs, in order:
1. **L0′** (done) — array-field access in invariants. ✅
2. **A second tool fix** — let a class invariant reference module functions (`unpack_inode`), i.e.
   declare type-independent logic/program functions *before* the type decls, or expose a logic view of
   the codec usable in the invariant. ⛔ not done.
3. **Then** the affordability re-test at the *real* coupling (18-field unpack × 32 inodes), which may
   still hit the array-state cost the inline form would incur.

The inline couplings proving (3.1/3.2) is genuine progress and shows the *frame* is not the wall — but
the *codec-in-the-invariant* is, and it's the part that matters for the os.

## 5. Revised plan ordering (rounds 1 + 2 combined)

1. **L0′ [TOOL]** — array-field access in invariants/contracts → `Array.get`. **DONE** (this round;
   gated corpus-clean + formal 18/18). Independently valuable: any class invariant over an array field
   now works.
2. **Function-in-class-invariant [TOOL]** — required before the *realistic* C coupling compiles. Size:
   medium (emission-ordering or a logic-view of the codec). **This is now C's true gating prerequisite,
   not the refactor.**
3. **C affordability re-test** — only meaningful after (2); test `ginode[n] == unpack_inode(disk[slice])`
   × 32 inodes. If it blows up (likely, per the array-state lesson), C needs HAPPY framing *and* a
   logic-view codec — i.e. C is the **highest-cost** track, not the near-term one.
4. **B (opacity / contract-narrowing-on-import)** — the prerequisite for A *and* the general
   force-multiplier (every imported codec hits the import-bloat). Given C's deepening cost, **B is now
   the more likely near-term route to the actual goal** (os stays light; round-trip established
   elsewhere and cited).
5. **D (Rocq/Lean)** — durability/opacity layer over A or C; never a substitute for them (does not touch
   the bloat).

**Net re-ordering vs round 1:** round 1 corrected "A cheapest" → "A is B" and "C is a refactor" → "C
needs L0′." Round 2 adds: **L0′ alone is not enough for C — the realistic coupling needs a second tool
fix (functions in invariants), pushing C's cost up and making B the more realistic near-term path.**

## 6. The through-line (both rounds)

Every step of this investigation, a *reasoned* premise was overturned by a *run* probe:
- "External proof solves the bloat" → no (it's about what propagates to call sites). [`try.md`]
- "A is cheapest" → no, A is B. [round 1]
- "C is a refactor" → no, C needs L0′ to even compile. [round 1]
- "L0′ unblocks C" → partly: inline couplings scale, but the *real* function-call coupling is unbound.
  [round 2]

The concepts (opacity, refinement, HAPPY) remain correct; their **cost and ordering** keep moving as
probes replace estimates. The discipline holds: **reason to design the probe, run the probe to decide
the plan.**

> **In one line:** L0′ is applied and works — inline coupling invariants now compile and scale (32
> inodes, 6s) — but the realistic refinement coupling `ginode[n] == unpack_inode(disk[slice])` is
> **`unbound`** because a class invariant can't call a module function; so Track C needs a *second*
> tool fix (functions-in-invariants) on top of L0′ and is the highest-cost track, which — combined with
> round 1's "A reduces to B" — makes **Track B (opacity) the more realistic near-term path** to keeping
> os light while the round-trip is established and cited.
