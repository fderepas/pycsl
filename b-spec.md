# B-spec-rev2.md — Track B: opaque-on-export + `#@ reveal` (contract narrowing on import; opacity as a feature)

**Date:** 2026-06-08 (rev. 2 — re-grounded on probe rounds 1–2)
**Status:** Spec (for review — no code changed)
**Owner:** [TOOL] (`src/pycsl/**`) — a transpiler feature; [STDLIB] consumes it at P4.
**Origin:** `opaque-and-refine.md` (rev. 2) §4, §7–§8; `try.md` §3.7 (the module-granularity wall) and
**§7** ("the path forward": *verify `_pack_inode` in its own unit with the full 18-field contract, then
import a narrowed one* — "PyCSL doesn't support [it] today"). **Re-grounded** by `challenging-the-
plan.md`/`challenging-the-plan2.md`: probes proved **A reduces to B**, so B is no longer optional.
**Concept:** **opacity, first-class** — the Dafny `{:opaque}`/`reveal` + export-sets analogue.
**Relationship:** **B is now the near-term route** (umbrella rev. 2 §8). A's lemma route *depends on*
B; C (data refinement) is the higher-cost principled target, gated on tool fixes B does not need.

**Revision 2 — what the probes changed for B.**
1. **B is promoted from "if narrowing recurs" to the near-term route.** Round 1 probed that the
   round-trip `#@ lemma` proves **only** with `_pack_inode`'s **rich** contract; with the light exported
   contract it **FAILS**. The rich contract is exactly the import-stub bloat — so **only opacity (B)
   can both make the round-trip provable and keep os light.** A reduces to B.
2. **B's two contracts now have probe-anchored roles:** the **definition** contract is the *rich*
   contract the round-trip proof needs; the **interface** contract is the *narrow* one that keeps os's
   8 syscalls light. B is the substrate; any round-trip lemma (A) sits on top of it (§2, §12).
3. The feature design (interface/definition + `#@ reveal` + the narrowing VC) is **unchanged and
   correct** — the probes moved B's *priority*, not its *mechanism*.

---

## 1. Goal & non-goal

**Goal.** A first-class mechanism giving a function **two contracts**:
- a **definition contract** — rich, verified against the body (here: `_pack_inode`'s 18 field-ensures,
  leaf-compositional, proven standalone — `try.md` §3.6); and
- an **interface contract** — narrow, what importers/callers see by default (here: `\length == 64`);

with **`#@ reveal`** opting a specific caller into the definition. So the 18 field-ensures are verified
once but ride **only the revealing call sites**, not all 8 syscalls — turning the `18 × 8 ≈ 144`-
hypothesis bloat (`try.md` §3.7) into `18 × (revealing sites only)`. This **realizes `try.md` §7** as a
*feature*, not an architecture rewrite, and is the **near-term route** to "os stays at 23 while the
round-trip is established and cited" (umbrella rev. 2 §8).

**Non-goal.** Re-litigating A (the probes settled it: A reduces to B — §2). C's abstraction barrier +
HAPPY + the L0″ functions-in-invariants prerequisite. D's kernel proof. The 23 *return-code* goals
(`08-1537`'s `#@ no_inline`). `fuel`/reveal-depth tuning (v2).

## 2. A reduces to B (probed) — what that means for this spec

Round 1's A-probe is the reason B is load-bearing:

| Probe | Result |
|---|---|
| rich `_pack_inode` contract + round-trip `#@ lemma` | **SUCCESS** — `∀x. unpack(pack(x)) == x` proves |
| **light** `_pack_inode` contract + round-trip `#@ lemma` | **FAILED** — no field-value info to compose from |

So the round-trip proof **needs the rich contract**, and the rich contract on the export stub **is** the
bloat. The only way to have *both* a provable round-trip *and* a light os is **opacity**: keep the rich
**definition** (so the round-trip proves where it is visible) and export the narrow **interface** (so
the 8 syscalls stay light). That is exactly B. Concretely, B subsumes A in one of two shapes:

- **(i) reveal-and-compose (no separate lemma):** a faithfulness client writes `#@ reveal _pack_inode`
  (and `#@ reveal _unpack_inode`); the round-trip follows by composing their *revealed definition
  contracts* at that site.
- **(ii) lemma-over-the-definition (A on top of B):** prove a `#@ lemma round_trip` in the codec unit
  *where the definition is visible* (so it proves — the probe's SUCCESS row), then `#@ uses` it in
  clients. A's lemma is now provable **because** B exposes the rich contract in the lemma's unit.

Either way, **os's `_pack_inode` stub carries only the interface (`\length == 64`)** and the rich facts
are revealed/used only where needed. A is not a separate cheap track; it is *a way to phrase the
round-trip on top of B's opacity.*

## 3. The surface

```python
class UnixInodeFileSystem:
    #@ requires \valid(fields, 18)
    #@ assigns \nothing
    #@ ensures \length(\result) == 64
    #@ ensures \result[0]*16777216 + \result[1]*65536 + \result[2]*256 + \result[3] == fields[0]
    #@ ensures \result[4]*256 + \result[5] == fields[1]
    #@ ...                                       # full 18-field DEFINITION contract (verified vs body)
    #@ interface ensures \length(\result) == 64  # the narrow INTERFACE: what importers see by default
    def _pack_inode(self, fields: list) -> list: ...
```

```python
#@ reveal _pack_inode             # this caller opts into _pack_inode's DEFINITION contract
#@ ensures \result == fields[k]
def write_then_read_field(self, n, fields, k): ...
```

- Existing `#@ requires/assigns/ensures` = the **definition** (verified against the body — *unchanged*).
- Optional **`#@ interface <clauses>`** = the exported narrow view.
- **Absent `#@ interface` ⇒ interface = definition** (fully transparent — *all existing code byte-
  identical*, §9). **Opacity is opt-in.**
- **`#@ reveal <fn>`** in a caller exposes `<fn>`'s definition *at that caller only*.

## 4. The soundness obligation — the narrowing is a *proven weakening* (interface ⊑ definition)

A **narrowing VC** discharges that the interface is a sound weakening of the definition (directions
matter — a wrong-direction approximation is unsound):

- **ensures:** `definition_post ⟹ interface_post` — the interface promises **less**; the hidden facts
  are the gap. (Codec: `(\length==64 ∧ 18 fields) ⟹ \length==64` — trivial.) *Primary B mechanism.*
- **assigns:** `definition_assigns ⊆ interface_assigns` — the interface may claim **more** writes
  (over-approximation is safe).
- **requires:** `interface_pre ⟹ definition_pre` — a caller establishing the interface precondition
  implies the body's. (Normally **equal**; the codec keeps `\valid(fields,18)` on both.)

> **Opacity narrows, never widens.** An `#@ interface` clause claiming *more* than the definition
> proves — a stronger `ensures`, a narrower `assigns`, a weaker `requires` — **fails the narrowing VC**
> and the function is **rejected (fail-loud)**. A client can only ever rely on *less* than is true.

## 5. What rides the import (the wall #3 fix, directly)

os's `_pack_inode` `val` stub carries **only the interface** (`\length == 64`); the 18 field-ensures
are verified in the owning unit and are **not on the export stub** — reachable only via `#@ reveal`. So
the **8 syscalls** carry **1** fact (os holds at 23, byte-identical) and a `#@ reveal`ing client carries
the **18** — and only it. The bloat `18 × 8` becomes `18 × (revealing sites)`. (Contrast C, which
removes the codec from the syscalls' world entirely but costs the L0″ fix + a refactor; B keeps the
codec *revealable* and ships sooner.)

## 6. The [TOOL] work ("Medium" — a real feature)

1. **Parse** `#@ interface` (grammar / Module2) as a clause-set distinct from the definition clauses.
2. **Verify** the definition against the body — **unchanged** (the §3.6 18-field proof already does it).
3. **Discharge the narrowing VC** (Module4/5): `definition ⊑ interface` per §4; **fail-loud** on
   over-claim (a negative driver claiming an unproven fact must be **rejected**).
4. **Emit the interface on the export `val` stub** (Module6): importers see the narrow contract — the
   line that fixes §5.
5. **`#@ reveal <fn>`** in a caller: re-emit `<fn>`'s **definition** contract at that site (restore the
   rich facts there only); this is also what makes shape (i)/(ii) of §2 work.

P0 (§10) fixes the *implementation shape* (two `val`s vs a reveal-gated contract) against Why3.

## 7. Comparison with Dafny (B is the most Dafny-like track)

| B construct | Dafny mechanism | Note |
|---|---|---|
| `#@ interface` + definition split | export sets: `provides f` vs `reveals f` | importers pick a view |
| hide rich post by default | `function {:opaque} f` | body+post hidden from callers |
| `#@ reveal f` in a caller | `reveal f();` | exposes the definition per proof |
| narrowing VC (`definition ⊑ interface`) | (the revealed post *is* the proven one) | B makes the weakening an **explicit, checked** obligation |
| reveal-depth (v2, out of scope) | `{:fuel f,0,0}` | unfolding control |

Two differences: (1) Dafny's `provides` exposes the *signature only*; B's `#@ interface` is a **custom
narrow contract** (`\length == 64`, not just the signature) — strictly more expressive. (2) Dafny
couples opacity to a function's *body*; B couples it to the *contract*, with the narrowing **explicitly
proven** (§4). The shared lesson (umbrella §9): **opacity is a proof-cost mechanism** — which the 1700s
blow-up *and* the probe series confirm.

## 8. Soundness & fail-safe

- **Definition verified against the body** (status quo, §3.6) — no new trust.
- **Interface is a proven weakening** (the narrowing VC, §4) — not asserted.
- **`#@ reveal` re-exposes a *proven* contract** — the definition the body already established.
- **No TCB growth.**
- **Fail-safe.** An over-claiming interface fails the narrowing VC → function rejected, **fail-loud**;
  never a silent wrong narrowing in a client. A false *definition* fails the body's own proof
  (anti-`\trusted`). If P0 finds Why3 cannot carry the interface/definition split, **no module is
  changed** until the shape is settled (status quo, no regression).

## 9. Blast radius & gating

- **`#@ interface` absent ⇒ interface = definition ⇒ every existing function byte-identical** (opacity
  is opt-in) — the headline safety property.
- Applying `#@ interface ensures \length == 64` to `_pack_inode` (definition = the §3.6 18-field): os's
  **8 syscalls see `\length == 64`** — **byte-identical to today, os held at 23** — and a `#@ reveal`ing
  client carries the 18 (measured: only there).
- Gate each step: narrowing VC discharges; the negative (over-claim) driver is rejected; os byte-diff
  (the 8 syscalls unchanged); the revealing client proves; full `bin/run-reference-tests.sh --pycsl`,
  os `formal_0001` 18/18, stdlib-coverage + doc-coherency green.

## 10. Phasing

| Phase | Delivers | Gate | Owner |
|---|---|---|---|
| **P0** | implementation-shape probe: narrow-on-import + rich-on-reveal in a hand-written `.mlw` (two `val`s? reveal-gated contract?) | the `.mlw` exhibits both; **fixes the emission model** | [TOOL] |
| **P1** | parse `#@ interface`; **default interface = definition** | **[byte-diff]** entire corpus byte-identical (opt-in proven) | [TOOL] |
| **P2** | the **narrowing VC** (§4): `definition ⊑ interface`; fail-loud on over-claim | **[PROVE]** a sound narrowing discharges; **[PROVE-neg]** an over-claiming interface is **rejected** | [TOOL] |
| **P3** | emit interface on the export stub; **`#@ reveal`** restores the definition at a caller | **[PROVE]** a revealing caller sees the definition; **[measure]** a non-revealing caller carries only the interface | [TOOL] |
| **P4** | apply to `_pack_inode` (definition = §3.6 18-field; interface = `\length == 64`); a `#@ reveal` read-back client proves a field fact — and the round-trip via §2(i) reveal-and-compose or §2(ii) lemma-over-the-definition | **[byte-diff]** os's 8 syscalls unchanged, held at 23; **[PROVE]** the revealing client + the round-trip; **[measure]** the 18 ride only there | [STDLIB]+[TOOL] |
| **P5** | corpus sweep; generalize (`_pack_direntry`, other rich-contract functions) | corpus PASS; each application byte-diff-gated | [STDLIB]+[TOOL] |

P0 fixes the shape; P1–P3 build the feature (P1 proves opt-in safety, P2 the soundness gate, P3 the two
emission behaviours); P4 applies it to the codec **and discharges the round-trip on top of B** (§2);
P5 generalizes.

## 11. Acceptance criteria

1. **`#@ interface` parses; absent ⇒ interface = definition ⇒ corpus byte-identical** — **[byte-diff]**.
2. The narrowing VC discharges for `_pack_inode` (`definition ⟹ \length == 64`) — **[PROVE]**; an
   `#@ interface` claiming an **unproven** fact is **rejected** — **[PROVE-neg / fail-loud]**.
3. os's 8 syscalls see **only `\length == 64`**; **held at 23**, byte-identical — **[byte-diff/inspect]**.
4. A `#@ reveal _pack_inode` client proves a field fact, and the 18 field-ensures ride **only** the
   revealing site (no extra hypotheses at the other 7) — **[PROVE / measure]**.
5. **The round-trip is established on top of B** — either §2(i) reveal-and-compose proves
   `unpack(pack(x)) == x` at a revealing client, or §2(ii) a `#@ lemma round_trip` proves in the codec
   unit and is `#@ uses`-cited — **[PROVE]** (this is the concrete discharge of "A reduces to B").
6. Existing transparent functions (no `#@ interface`) are unchanged — **[byte-diff]**.

## 12. Relationship to A / C / D

- **A — reduces to B (probed, §2).** A's `#@ lemma`/`#@ uses` is not a cheap standalone route; the
  lemma needs the rich contract, which only B's opacity can hide on export. So **A runs on top of B**:
  B's definition makes the round-trip provable; B's interface keeps os light; the lemma (if used at all)
  is proven where the definition is visible and cited elsewhere (or skipped entirely via §2(i)).
- **C — the higher-cost principled sibling.** B keeps the codec *visible on reveal* (clients can reason
  about bytes when they `#@ reveal`); C puts it *below an abstraction barrier* (syscalls reason about an
  abstract inode and never see bytes), but needs **L0″ (functions/logic-view in invariants)** + HAPPY +
  a refactor (umbrella rev. 2 §5–§8). **B ships sooner; C is the eventual structural answer.**
- **D — durability layer.** D's kernel-checked round-trip can back B's *definition* contract
  (solver-independence); the interface/reveal surface is unchanged. D never substitutes for B.
- **Sequencing (umbrella rev. 2 §8):** L0′ (done) → **B (near-term route)** → L0″ → C affordability
  re-test → D (durability). **B is the step to do now.**

## 13. Out of scope

A's lemma route as a *standalone* mechanism (it runs on B — §2); the abstraction barrier + HAPPY + L0″
(Track C); the Rocq/Lean realization (Track D); `fuel`/reveal-depth tuning (v2); the `#@ no_inline`
return-code work (`08-1537`); applications beyond `_pack_inode` + one demonstrating driver until P5.

> **In one line (rev. 2):** B is the feature `try.md` §7 asked for — a rich **definition** contract
> (verified against the body, = the §3.6 18-field `_pack_inode`) plus a narrow **interface** contract
> (`\length == 64`, what importers see), proven a sound weakening by a **narrowing VC**, with **`#@
> reveal`** opting a caller into the definition — so the 18 field-ensures ride only the revealing sites
> and os's 8 syscalls stay at `\length == 64` (held at 23, byte-identical, opacity opt-in). The round-2
> probes elevated B from "if it recurs" to **the near-term route**: **A reduces to B** (the round-trip
> lemma needs the rich contract only opacity can hide), and C is the higher-cost structural target
> gated on L0″ — so B is the step to ship now, fail-loud on any interface that claims more than the
> definition proves.
