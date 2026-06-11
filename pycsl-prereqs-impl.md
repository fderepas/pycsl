# pycsl-prereqs-impl.md — Implementation Guide for the P-series (TY0 → P-1 → P-4 → P-3, P-2 design in parallel)

**Status:** Implementation guide (executable work order for a Claude Code session).
**Origin:** `pycsl-prereqs-spec.md` (the normative spec for P-1…P-4; its §7 ordering and
§8 acceptance criteria are binding here); the `pycsl-stdlib-coverage` convergence loop
(the coordinator / worker / paired-document protocol this guide adapts);
`typing-global-overview.md` (TY0 and GT5); `refactor.md` (laws + standing gate);
`ir.md` (wire contract + versioning policy).
**Scope:** TY0 (specify the existing implicit annotation subset), then P-1, P-4, P-3
implemented to DONE, and P-2 **D0 (design spec) + D1 (probes) only** — P-2's D2/D3
implementation is deliberately last per the spec and out of scope here; this guide ends
with P-2's probe verdicts recorded, not its code.

---

## 1. What carries over from the os loop, and what inverts

The convergence loop that proved `os` worked because each agent had a **separate concern
and therefore a tailored squeeze**: the stdlib-agent squeezed between the library
reference and CPython; the test-agent squeezed between the English spec and the public
API (and physically unable to simulate); the tool-agent squeezed between the gap document
and the byte-diff gates; the coordinator's approval editorial, never a rubber stamp.

The P-series keeps the loop's shape and **inverts its direction**. In the stdlib loop the
*model* was the deliverable and tool changes were reactive (gap-driven). Here the **core
is the deliverable** — every P-item lands in `src/pycsl/` (Module 2 grammar, Module 5
emitter, `ir_schema.py`, `core_ir_semantic.py`, Module 6) — and what plays the stdlib
module's role of "the thing that pushes and validates the tool" is the **consumer
driver**: corpus drivers that exercise the new surface exactly as a future front-end
will. The separation of concerns survives intact, with the squeezes re-tailored:

| Agent | Builds | Squeezed from above by | Squeezed from below by | Forbidden move |
|---|---|---|---|---|
| **coordinator** (main thread) | approvals, sequencing, gate verdicts | `pycsl-prereqs-spec.md` §7–§8 | the standing gate's actual output | editing source; approving a spec it has not amended-or-judged |
| **core-agent** (≈ tool-agent, now primary) | the P-item inside `src/pycsl/` + its docs | the P-item's section of the prereqs spec (the strongest behaviour it mandates — incl. the ACSL alignment) | `refactor.md` laws + **total additivity** ("a P-item that changes an existing driver's emission has violated its own contract") | weakening a gate to make an item land; touching drivers to make them pass |
| **driver-agent** (≈ test-agent) | the PROVE / PROVE-neg corpus drivers | the spec's acceptance criteria + the *documented* surface syntax | what actually proves through `pycsl` | reading the core implementation. It gets the surface grammar + the spec's acceptance lines, **never** `src/pycsl/` internals — so a driver cannot be tuned to implementation quirks; it exercises the contract, exactly as the test-agent could not simulate `sys_*` |
| **probe-agent** (≈ stdlib-agent's "pin reality first" role) | minimal Why3/WhyML experiments + recorded verdicts; TY0 witness drivers | the design's claim to be tested (one claim per probe) | **Why3's actual behaviour** — the execution ground truth | implementing anything; a probe writes a verdict, never a fix |

Two protocol rules from the skill are kept verbatim because they are what made it work:

1. **The paired traceability documents and the STATUS handshake.** Forward work and
   reactive gaps both flow through dated pairs:
   - `DD-HHMM-pseries-spec-N.md` — the core-agent's concrete implementation plan for a
     P-item (or the gap answer), opened at **`STATUS: DRAFT`** → coordinator sets
     **`APPROVED`** (after *editorial* judgment — add, modify, or remove parts to speed
     convergence) → core-agent implements, gates, sets **`DONE`**.
   - `DD-HHMM-pseries-gap-N.md` — written by the **driver-agent** (the implemented
     surface diverges from the spec'd acceptance) or the **probe-agent** (a verdict
     contradicts a design assumption). Same `DD-HHMM-N` as the spec doc that answers it.
   No edit to `src/pycsl/` ever happens from a `DRAFT`. Approval gates the *plan*, the
   higher-risk half, before any code — exactly the os-loop discipline.
2. **Author separation is physical, not honorary.** The driver-agent's delegation prompt
   contains the surface syntax and acceptance lines only. If it needs to know how the
   feature behaves, it runs `pycsl` on a driver and reads the verdict — it never reads
   the diff.

Claude Code constraint: subagents cannot spawn subagents, so the **main thread is the
coordinator**, chaining the three workers per item, strictly sequenced within each chain.

---

## 2. Subagent definitions

Drop these in `.claude/agents/`. All three preload the project skills; the driver-agent
deliberately omits the core-internals knowledge it must not have.

```markdown
---
name: pseries-core-agent
description: MUST BE USED to design and implement exactly one P-series item (TY0 transcription, P-1, P-4 lowering, P-3, or P-2 D0 design spec) inside src/pycsl/ and the reference docs. Writes the DD-HHMM-pseries-spec-N.md plan first (STATUS: DRAFT), implements only on APPROVED, gates with total additivity.
tools: Read, Write, Edit, Bash, Grep, Glob
model: opus
effort: high
memory: project
skills: [pycsl-annotate, pycsl-docs, csl-philosophy]
---
You implement one P-series item against its section of pycsl-prereqs-spec.md.
Hard rules:
- Total additivity: byte-identical emission for every existing driver, the core-only
  goldens (28/28) and frontend-only goldens identical, determinism re-verified 4-5x
  (PYTHONHASHSEED=0). If your change alters an existing driver's emission, your change
  is wrong by definition - revert and redesign.
- Transcribe the spec, do not improvise: P-1's grammar is the ACSL binder grammar with
  `integer`; P-4's lowering is WhyML `label Name in`/`at Name`; P-3's two halves
  (obligation: computed write set SUBSET-OF declared targets, fail-loud; payoff: the
  complement-preservation invariant anchored at LoopEntry) are specified, not optional.
- Every new keyword/clause lands in the three reference docs + annotations.md in the
  same change; bin/doc-coherency.py --check green is part of DONE, as is ir.md's
  compatibility table when the IR version moves (P-3: 1.2; widen ACCEPTED_IR_VERSIONS,
  re-verify round-trip identity).
- You never write the acceptance drivers (the driver-agent owns them) and never edit
  them to pass. You do not declare done: DONE is the coordinator's gates passing.
Workflow: write DD-HHMM-pseries-spec-N.md (DRAFT) with exact change surface, IR impact,
and gates; STOP for approval; on APPROVED implement, run the standing gate, set DONE.
```

```markdown
---
name: pseries-driver-agent
description: MUST BE USED to write the PROVE and PROVE-neg corpus drivers for one P-series item, from the surface syntax and the spec's acceptance criteria ONLY. Never reads src/pycsl/ internals or diffs.
tools: Read, Write, Edit, Bash, Grep, Glob
model: opus
effort: high
skills: [pycsl-annotate, csl-philosophy]
---
You write the acceptance drivers for one P-item. You are given the documented surface
syntax and the acceptance lines from pycsl-prereqs-spec.md SS8 - nothing else. You may
run pycsl on your drivers and read verdicts; you may NOT read src/pycsl/ or any diff.
Each item needs: every positive driver the spec names ([PROVE]), every negative
([PROVE-neg], failing with a LOCATED error at the right place), and for P-3 the payoff
driver - a region-scoped loop whose post-loop proof PROVES WITH the clause and FAILS
WITHOUT it (run both ways; both verdicts are the deliverable). A driver that passes for
the wrong reason, or a negative that fails at the wrong site, is a gap: write
DD-HHMM-pseries-gap-N.md (symptom, minimal reproducer, expected-vs-actual against the
spec line) and stop.
```

```markdown
---
name: pseries-probe-agent
description: MUST BE USED to run probe questions before implementation: the P-4 Module 6 label-lowering probe, the P-2 D1 Why3 feasibility probes (seq/ref/view discipline), and TY0's witness drivers pinning current front-end annotation behaviour. Records verdicts; never implements fixes.
tools: Read, Write, Edit, Bash, Grep, Glob
model: opus
skills: [pycsl-annotate]
---
You answer ONE probe question at a time with a minimal experiment and a recorded
verdict (the 07-1732 probes are the template: one claim, one .mlw or one driver, one
PASS/FAIL line with the evidence path). P-4 probe: does Module 6 today lower Label +
At{label} for an ARBITRARY label, or only built-ins riding on `old`? TY0 probes: for
each annotation form, a witness driver pinning what the front-end currently does
(interprets / ignores / rejects). P-2 D1 probes: each load-bearing claim of the D0
design (e.g. scalar out-param as region-free `ref int` rebind; before/after reasoning
without prophecy; the aliasing rejection mechanism) gets its own Why3 probe. You write
verdicts, never fixes; a surprising verdict is a gap document, not a workaround.
```

---

## 3. Sources of truth per activity

The workflow is squeeze-driven, so every activity names its authorities before it
starts. The coordinator includes the relevant rows in each delegation prompt (subagents
start with fresh context).

| Activity | Upper bound (normative) | Lower bound (execution ground truth) | Pin |
|---|---|---|---|
| **TY0** | none to invent — TY0 *is* the transcription of S7 (current `pure_ast`/`ir_resolve`/Module 6 TypeInference behaviour) into the three references, GT5 (forward-ref resolution order) included | the code's actual behaviour | probe-agent witness drivers, one per annotation form (interpreted / ignored / rejected) |
| **P-1 typed binders** | prereqs spec §2 + the **ACSL manual's** binder grammar and `integer`-vs-concrete-type distinction (in PyCSL both map to math int; the distinction becomes real only in bounded-type front-ends) | the existing `binder_type` IR field and `core_ir_semantic`'s typed-binder check (no schema change permitted) | the [PROVE-neg]: unknown binder type → the *existing* located error |
| **P-4 `\at` anchors** | prereqs spec §5 + ACSL `\at(e, L)` semantics | **Why3's actual label semantics** (`label Name in …`, `e at Name`) and what Module 6 *currently* lowers — unknown until probed | the P-4 probe verdict (CCSL P0's deliverable), recorded before any lowering work |
| **P-3 `loop assigns`** | prereqs spec §4 + ACSL `loop assigns` frame semantics; `ir.md` §2 versioning policy for the additive 1.2 field | Why3's loop model (wholesale havoc of written arrays; **no** loop `writes` clause — the motivating absence) + Module 6's existing body write-effect computation | the payoff driver (proves only with the clause) + both fail-loud negatives |
| **P-2 D0/D1 borrow design** | prereqs spec §3's mandated questions (model shape, aliasing discipline, additive IR surface, O-style soundness obligations); the three consumers' semantics (C out-params, Rust `&mut`, Go pointers) as the claims to serve | `07-1705-spec-rev4` + the **07-1732 probe results** (#8: `ref (array int)` cannot rebind; #9: `ref (seq int)` can) and the new D1 probes | every load-bearing design claim has a recorded probe verdict **before D2 is even scheduled** |
| **Cross-cutting** | `refactor.md` laws; `ir.md` wire contract | the standing gate's machine output (corpus byte-diff, goldens, os standing count, formal_0001 18/18, doc-coherency, TCB ledger) | every item's DONE |

---

## 4. The per-item pipeline

```
coordinator delegates item I (spec section + SoT rows + acceptance lines in prompt)
        │
        ├─ probe-agent runs I's probes (only where I has them: TY0, P-4, P-2)
        │        verdict recorded ── surprising verdict → gap doc → coordinator re-plans
        ▼
core-agent writes DD-HHMM-pseries-spec-N.md  (STATUS: DRAFT)
        ▼
GATE A  coordinator EDITORIAL approval (judge, amend, cut, sharpen) → STATUS: APPROVED
        ▼
core-agent implements + runs the standing gate                → STATUS: DONE (claimed)
        ▼
driver-agent writes the [PROVE]/[PROVE-neg] drivers (surface + acceptance lines only)
        ▼
GATE B  coordinator verifies: all spec §8 lines for I pass; standing gate green;
        divergence → driver-agent's gap doc → loop (N := N+1)
        ▼
item I DONE → next item in the chain
```

Note the order: the **driver-agent runs after the implementation exists** (it needs the
surface to exercise) but writes from the spec, not the diff — the same way the
test-agent wrote from the English spec after the model existed. A gap at GATE B reopens
the item with a paired gap/spec exchange, exactly the os-loop turn.

---

## 5. Execution order and the two chains

Per prereqs spec §7, plus the TY0 carve-out. **Sequential within a chain; the chains
are independent; P-2 design runs in parallel and stops at D1.**

```
TY0 ──▶ P-1 ────────────────────────────────▶ (chain A done)
P-4 probe ──▶ P-4 lowering (if gap real) ──▶ P-3 (IR 1.2)   (chain B)
P-2 D0 design spec ──▶ D1 probes ──▶ STOP (D2/D3 out of scope)   (parallel)
```

### Item TY0 — specify the implicit annotation subset *(transcription; zero code)*
- **probe-agent:** one witness driver per annotation form the front-end touches today
  (scalars, known class names, container shapes, `None` returns, string/lazy
  annotations) with the observed disposition recorded.
- **core-agent:** transcribes the verdicts into the three references (+ GT5's
  forward-reference resolution order and failure modes), `# cite:`-anchored to S7
  file:line. **No `src/pycsl/` behaviour change** — the standing gate passes trivially,
  which is itself the check.
- **driver-agent:** reads *only* the new reference sections and predicts each witness
  driver's outcome; a wrong prediction means the transcription is ambiguous — gap doc.
- **Acceptance:** every witness driver's behaviour derivable from the written spec
  alone; doc-coherency green; corpus byte-identical [byte-diff trivially].

### Item P-1 — typed quantifier binders with `integer` *(grammar + emitter; no IR change)*
- No probe. core-agent: Module 2 binder-position type names (`integer` keyword
  normalizing to IR tag `"int"`; classes/datatypes resolving against `type_decls`),
  Module 5 fills `Forall/Exists.binder_type` **directly** (no inference pass); untyped
  binders stay accepted (deprecated, horizon open per O-6); docs mark typed as the form.
- driver-agent: one driver per binder-type class — `integer`, concrete class, datatype
  — each `\forall integer k. 0 <= k ==> …` round-tripping dump → ingest → prove
  [PROVE]; the negative — unknown type name → the existing located error [PROVE-neg].
- **Acceptance:** spec §8.2 + corpus and both conformance corpora untouched.

### Item P-4 — arbitrary `\at` label anchors *(probe first; no IR change)*
- **probe-agent first**, and the verdict forks the item: if Module 6 already lowers
  arbitrary `Label`+`At{label}`, P-4 collapses to drivers + docs; if the gap is real
  (expected), core-agent maps `Label name` → WhyML `label Name in …` at statement
  position, `At{e, L}` → `e at Name`, keeps `Pre`/`Old` on their existing `old`
  lowering, sanitizes label names deterministically (content-ordered), and emits
  `LoopEntry` (never user-written) before any P-3-clause loop.
- driver-agent: ghost label + `\at` read-back proves [PROVE]; undeclared label in `\at`
  is a located error [PROVE-neg]; corpus byte-identical (nothing existing emits the new
  lowering).
- **Acceptance:** spec §8.5.

### Item P-3 — `loop assigns` as a core feature *(IR 1.2; requires P-4 DONE)*
- core-agent, both halves fail-loud: the optional `assigns` field on `While`/`For`
  (absent ⇒ byte-identical today-behaviour); **obligation half** — Module 6 checks the
  computed body write set ⊆ declared targets, located rejection outside the clause;
  **payoff half** — per declared region `a[lo..hi]`, synthesize
  `∀k. ¬(lo ≤ k ≤ hi) ⟹ a[k] = (a at LoopEntry)[k]` (the unhavocked complement — the
  region-scoped preservation HAPPY reasoning wants, and the obligation a region-escaping
  write fails). `#@ loop assigns` ships in the same change. `ACCEPTED_IR_VERSIONS`
  widens to {1.0, 1.1, 1.2}; 1.1 documents stay ingestable; round-trip identity
  re-verified; `ir.md` table updated.
- driver-agent: the **payoff driver** — post-loop proof that PROVES with the clause and
  FAILS without (both runs recorded) [PROVE]; scalar write outside the clause →
  rejected; write outside the declared region → fails the invariant's preservation
  [PROVE-neg ×2]; every clause-less loop byte-identical (the opt-in proof).
- **Acceptance:** spec §8.4 + §8.1; os at its standing count and formal_0001 18/18
  re-confirmed (this is the item most likely to disturb them).

### Item P-2 — D0 design spec + D1 probes *(parallel; stops before code)*
- core-agent (designer mode): `DD-HHMM-pseries-spec-N.md` answering the spec's four
  mandated questions — model shape (seq/ref/view, value = immutable view, mutation =
  region-free `ref` rebind, the Creusot shape **without prophecy**, stating where it
  suffices: scalar `int*` ≈ `ref int`; and where it does not: struct borrows,
  reborrowing, two-phase aliasing), the `f(&x,&x)` aliasing discipline (fail-loud is
  the floor; choose the mechanism), the additive IR surface (a 1.2 document without the
  new nodes stays valid → 1.3), and the O-style soundness obligations (a write through
  a borrow is visible to the lender; an aliased mutable borrow is never silently
  admitted).
- probe-agent: one Why3 probe per load-bearing claim, 07-1732-style, each with a
  recorded verdict.
- **Acceptance:** spec §8.3 — design + verdicts exist; **no schema change, no code**;
  byte-diff trivially. D2 may not be scheduled until every named probe has a verdict.

---

## 6. Definition of done (global)

The engagement is done when: TY0's reference sections are landed and
prediction-checked; P-1, P-4, P-3 are at `STATUS: DONE` with every §8 acceptance line
machine-verified; P-2's D0 spec and D1 verdicts are recorded with D2 explicitly *not
started*; after **every** item the standing gate passed (corpus byte-diff, core-only
goldens 28/28, frontend-only goldens, determinism ×4–5, os standing count,
formal_0001 18/18, doc-coherency green, TCB ledger unchanged or shrunk); and the
paired-document trail is complete — every `src/pycsl/` change traceable to an APPROVED
spec doc, every spec doc to the prereqs-spec section or gap that motivated it. Do not
mark any item done because the core-agent reported success: DONE is the gates passing,
with the driver-agent's independently-authored drivers as the witness — the same
discipline that closed `os`.
