# D-spec.md — Track D: the Rocq/Lean bridge (kernel-checked round-trip; opacity + durability layer)

**Date:** 2026-06-08
**Status:** Spec (for review — no code changed)
**Owner:** [TOOL] (`src/pycsl/**`, the Why3 bridge) + [FORMAL] (`src/formal-semantics/**`, the proof)
**Origin:** `opaque-and-refine.md` (rev. 2) §2, §6–§8 (D is the durability/opacity layer); `try.md`
§3.6 (the round-trip, already SMT-proven by composition); `formal.md` (the existing Lean 4 + Rocq
`pycsl_soundness` setup D extends).
**Concept:** **opacity + durability** — a kernel-checked, solver-independent round-trip exposed as an
opaque lemma (statement only).
**Relationship:** **a layer *under* Track B or C — never a substitute.** D hardens what the round-trip
rests on; it does **not** keep os light (B/C do) and does **not** add proving capability (the round-trip
is already proven). **Least urgent of the four** — a foundation-hardening investment.

---

## 1. D's defining constraint (state this first): D does NOT solve wall #3

> Per `opaque-and-refine.md` §2: **an external proof, attached as a rich contract on the os `_pack_inode`
> stub, bloats the 8 call sites exactly as before.** The bloat is *what propagates to call sites*, not
> *how the fact was proved.* **D alone keeps nothing light.**

D is the **durability/opacity layer over B or C**: B (opacity) or C (refinement) keeps os light; D then
swaps the round-trip's **SMT discharge** for a **kernel-checked** one. D is meaningless without B or C
underneath it — and pairing it with them is the entire point.

## 2. Goal & non-goal

**Goal.** A **kernel-checked** (Lean 4 / Rocq), **solver-independent** proof of the codec round-trip
`unpack_view(pack_view(x)) == x` (field-wise), exposed to Why3 as the **discharge** of the round-trip
lemma — so **B's definition contract** / **C's logic-view round-trip lemma** rests on a kernel proof,
not on Alt-Ergo/Z3 heuristics. Value = **durability** (immune to solver drift) + **opacity** (the
proof-assistant's `Qed` exposes only the *statement*).

**Non-goal.** Keeping os light (that is B/C — §1). Adding proving *capability* — the round-trip is
**already proven** by leaf-composition (`try.md` §3.6; drivers 0657/0658), so D **hardens, it does not
enable.** Replacing B or C. Proving facts other than the foundational round-trip. A fully kernel-checked
os (D is scoped to *the round-trip lemma*).

## 3. What D actually buys (durability + opacity, not capability)

The round-trip already proves under SMT, cheaply, by composing the leaf value+inverse contracts
(`try.md` §3.6 — the move that beat the array-state wall). D adds **two** things and **no** new
capability:

- **Kernel-checking → durability.** The Lean/Rocq kernel verifies the proof, **immune to SMT
  heuristic/version drift.** The array-state cost that §3.6 beat *by composition* becomes a **permanent,
  solver-independent** fact — it can never silently regress when Alt-Ergo/Z3 change.
- **`Qed`-opacity → a hiding boundary.** A proof-assistant lemma closed with `Qed` exposes only its
  **statement**; clients see the round-trip *fact*, never the proof. This is the same opacity B/C want
  for the codec, delivered at the proof level.

**Why bother, given the SMT proof works?** Because the round-trip is **foundational** — B's definition
contract and C's coupling invariant *both* rest on it. A foundational lemma is exactly what is worth
kernel-checking; a regression there would silently undermine B and C. D is **not necessary for
correctness today**; it is the right hardening for the one fact everything else leans on.

## 4. The mechanism: Why3's Coq/Isabelle/PVS realization (the established bridge)

Why3 can **realize** theories in a proof assistant: a Why3 lemma can be **discharged by a Coq/Lean
proof** instead of (or alongside) an SMT solver. So D is:

1. Prove the round-trip in **Lean 4 and Rocq** (matching the existing `src/formal-semantics` dual-prover
   setup — `formal.md`).
2. **Realize/replay** that proof as the discharge of the **Why3 round-trip lemma** whose *statement* is
   what B's definition / C's logic-view round-trip lemma references.

The lemma's **statement** is what the os model (via B/C) sees; the **proof** is kernel-checked off to
the side. This is the standard "trusted lemma from a proof assistant" pattern — with the TCB
consequence decided in §5.

## 5. The TCB decision — REPLAY vs AXIOMATIZE (the heart of D's soundness)

How Why3 consumes the proof-assistant proof determines whether D **grows** the trusted base. This is the
key soundness choice, recorded per the project's Soundness-Ledger discipline.

| | **AXIOMATIZE** | **REPLAY (Why3 realization)** *(preferred)* |
|---|---|---|
| How | prove the round-trip in Lean/Rocq *separately*; **assert** its statement in Why3 as an axiom | Why3 **generates** the obligation; the Lean/Rocq proof **discharges** it; the kernel checks |
| TCB adds | the kernel **+ an unverified hand-correspondence** ("the Lean statement == the Why3 lemma" and "the axiom matches the proof") | the kernel + the Why3 realization driver — **both established; no new unverified correspondence** |
| Risk | a **translation gap** (the Lean statement subtly differs from the Why3 lemma) is silent | none beyond the (small, trusted) kernel + driver |
| Verdict | fallback only, with the correspondence **ledgered** | **principled choice — keeps the TCB minimal** |

**Recommendation: REPLAY.** It keeps the TCB at *Why3 core + kernel + realization driver* (all
well-established) and eliminates the translation gap, because Why3 itself generates the statement the
proof must discharge. **AXIOMATIZE** is acceptable only when the statement is trivial and the
correspondence obvious — and then the hand-correspondence is an explicit **Soundness-Ledger** entry
(D-axiomatize adds the kernel + the translation to the TCB; D-replay does not, beyond the kernel).

## 6. The formal-semantics connection (where the proof lives)

`src/formal-semantics/` already proves `pycsl_soundness` in **Lean 4 + Rocq** under a strict discipline
(`formal.md`): both provers in sync, **0 `sorry` / 0 `Admitted`**, `make proof` clean. D's round-trip
proof lives **there**, alongside the soundness theorem, under the same discipline — and reuses the leaf
value+inverse lemmas it composes from (proving them there if absent).

## 7. What gets proven in Lean/Rocq (and why it is *easy* there)

The round-trip over the logic views (C's form) / the 18-field codec (B's definition form):

```
∀ fields. valid(fields, 18) → ∀ k. 0 ≤ k < 18 → unpack_view(pack_view(fields))[k] == fields[k]
```

Proven by the **same leaf-compositional structure as §3.6** — the uint16/uint32 pack/unpack are inverses
by **div/mod arithmetic** (`(v // 256, v % 256)` reconstructs `v` for `0 ≤ v ≤ 0xFFFF`), composed over
the 18 fields. **This is easy in a proof assistant:** div/mod inverse lemmas + a fold over 18 fields,
with **none of the SMT array-state cost** (proof assistants handle the byte/array math structurally).
**So D's *proof* is not the hard part** — the work is the **bridge** (§4–§5 realization) and the
**dual-prover sync** (§6).

## 8. Dependencies & what D backs

| | |
|---|---|
| **D backs** | B's **definition** contract (the 18-field round-trip) / C's **logic-view round-trip lemma** — their interface/reveal (B) or logic-view (C) surface is **unchanged**; D swaps the round-trip's SMT discharge for a kernel one |
| **D needs** | **B or C** to have established the opacity/refinement structure (D does not keep os light — §1); the Why3 Coq/Lean **realization** machinery; the existing `src/formal-semantics` setup |
| **D's urgency** | **lowest** — the SMT round-trip works today (§3.6); D is a durability investment, justified because the round-trip is foundational |

## 9. Soundness & fail-safe

- **The round-trip is proven** — kernel-checked under **replay**, or kernel-proven-and-asserted under
  **axiomatize** (§5).
- **TCB:** **replay → no growth** beyond Why3 core + kernel (both trusted); **axiomatize → + the
  statement-correspondence** (ledgered). The choice is recorded (umbrella §10 discipline).
- **Fail-safe.** If the Lean/Rocq proof fails, the round-trip lemma is **unproven → fail-loud**; B's
  definition / C's coupling cannot rest on it (they fall back to the SMT discharge or are blocked — never
  a wrong proof). A **wrong statement** (the axiomatize translation gap) is the one risk **replay
  eliminates** by construction.
- **Dual-prover sync** (`formal.md` discipline): both Lean and Rocq must prove it; a divergence catches
  an error the kernel of one prover alone might miss.

## 10. Comparison with the state of the art

- **Coq `Qed`-opacity** is D's opacity boundary (clients see the statement, not the proof).
- **Why3 realizations** (Coq/Isabelle/PVS) are D's mechanism — the established proof-assistant bridge.
- **Dafny** has *no* direct analogue (it is SMT-only); D's value — a **foundational fact checked by a
  small kernel rather than a heuristic solver** — is closer to **seL4** (Isabelle) or **F\***/Coq-backed
  verification, where the critical lemmas rest on a kernel, not on solver heuristics.
- The "trusted lemma from a proof assistant" pattern: **replay shrinks the TCB; axiomatize grows it**
  (§5) — D defaults to replay precisely for that reason.

## 11. Phasing

| Phase | Delivers | Gate | Owner |
|---|---|---|---|
| **P0** | prove the round-trip (leaf value/inverse lemmas + 18-field composition) in **Lean 4 AND Rocq**, under the `formal.md` discipline | **[PROVE-kernel]** both provers, **0 `sorry`/`Admitted`**, `make proof` clean; dual-sync | [FORMAL] |
| **P1** | the **Why3 realization bridge** — discharge the Why3 round-trip lemma by **replaying** the Lean/Rocq proof (preferred) or **axiomatize-with-ledgered-correspondence** (fallback); **decide replay vs axiomatize** | **[realize]** the Why3 lemma is discharged by the kernel proof; **[ledger]** the TCB consequence recorded | [TOOL] |
| **P2** | wire D **under B or C** — B's definition round-trip / C's logic-view round-trip lemma now discharged by D (kernel) instead of SMT; the B-interface / C-logic-view surface **unchanged** | **[byte-diff]** os unaffected (D does not touch the bloat — B/C keep it light); **[PROVE]** the lemma now rests on the kernel proof | [TOOL]+[STDLIB] |
| **P3** | **durability test** — confirm the round-trip survives a solver version/heuristic change (the whole point: kernel-checked = immune) | **[PROVE]** the lemma holds across a solver bump; **[ledger]** final Soundness-Ledger entry (replay: none; axiomatize: kernel + translation) | [TOOL]+[FORMAL] |

P0 is easy (§7); the real work is P1 (the bridge + the replay/axiomatize decision) and P2 (wiring it
under B/C without disturbing the os surface).

## 12. Acceptance criteria

1. The round-trip is proven in **both Lean 4 and Rocq**, **0 `sorry`/`Admitted`** — **[PROVE-kernel]**.
2. The Why3 round-trip lemma is **discharged by the kernel proof** (replay preferred) — **[realize]**.
3. **B's definition / C's logic-view round-trip lemma rests on the kernel proof**; the B/C surface is
   **unchanged**; **os is unaffected** (D does not touch wall #3) — **[byte-diff / inspect]**.
4. The **TCB consequence is recorded** in the Soundness Ledger — **replay: no growth beyond the kernel;
   axiomatize: + the statement-correspondence** — **[ledger]**.
5. A deliberately-**false** round-trip statement **fails the kernel proof** (replay) or is **caught by
   dual-prover divergence** — **[PROVE-neg]**.
6. The round-trip **survives a solver version/heuristic change** (durability) — **[PROVE]**.

## 13. Relationship to A / B / C

- **A — reduces to B** (probed); D could back A's lemma too, but A runs on B's opacity (umbrella §3, §7).
- **B / C — D is a layer *under* them.** D backs B's **definition** contract or C's **logic-view
  round-trip lemma** with a kernel proof (durability + opacity); the B-interface/reveal or C-logic-view
  surface is unchanged. **D does not keep os light — B/C do** (§1).
- **Sequencing (umbrella rev. 2 §8):** L0′ (done) → **B (near-term route)** → L0″ → C affordability
  re-test → **D (durability, last/optional)**. D is the **least urgent**: a foundation-hardening
  investment, justified because the round-trip is foundational (B and C both rest on it) and
  solver-independence matters for a fact that critical.

## 14. Out of scope

Keeping os light (B/C); the L0″ / parametric-HAPPY / opacity tool features (B/C); proving facts other
than the foundational round-trip; other codecs (`_pack_direntry`/`_unpack_direntry` — identical bridge
pattern, fold in after the inode round-trip); a fully kernel-checked os model (D is scoped to the
round-trip lemma); the axiomatize hand-correspondence as anything other than a **ledgered fallback**
(replay is the default, §5).

> **In one line:** D does **not** solve wall #3 and adds **no** proving capability — the round-trip is
> already SMT-proven by composition; D is the **durability + opacity layer under B or C**, supplying a
> **kernel-checked, solver-independent** proof of the codec round-trip (easy in Lean 4 / Rocq via the
> §3.6 leaf composition — div/mod inverses + an 18-field fold) exposed to Why3 via **realization**, so
> B's definition contract / C's logic-view round-trip lemma rests on a small kernel rather than SMT
> heuristics; **replay** is the default (no TCB growth beyond the kernel) and **axiomatize** a ledgered
> fallback (adds the statement-correspondence) — making D the least-urgent, foundation-hardening track,
> worthwhile precisely because the round-trip is the one fact everything else leans on.
