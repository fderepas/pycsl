# triage-ranked-tcb-tier3-phase3.md — tier-3 execution status (what worked, what failed, what's next)

Honest status of the TIER-3 execution (`triage-ranked-tcb-tier3.md`) as of 2026-07-06.
Branch `ghost-assign-bc6`, green (fidelity 80/80 verbatim, mirror-check 51/51, conformance 38/38,
doc-coherency in sync). `\trusted` count **1249** (canonical: `grep -rF '\trusted' src/self-annotate/src --include='*.py'`).

---

## 1. Headline

The tier-3 **foundation is built and CERTIFIED** (feasibility proven, emitter ADT lands, Rocq+Lean
certificate co-landed, peripheral decision made). The tier-3 **marker payoff is NOT yet realized** —
zero `\trusted` stubs have been converted *via the ADT*. The count moved 1252 → 1249 only on three
incidental string-leaf stubs that read no IR node. The next increment (list-shaped kinds) is the
gate to the first real ADT-enabled conversions.

---

## 2. What SUCCEEDED (committed, branch green)

| phase | commit | result |
|---|---|---|
| P0 feasibility | `ee27b0cd`, `b830805f` | **GO both sides.** WhyML variant ADT spike: pure mutual recursion + termination `variant` + discriminant/projection, Valid on Alt-Ergo+Z3, **0 axioms**. Rocq+Lean Phase-7 record-valued-`val` spike: read-back/frame/conservativity `Qed.`/sorry-free, ledger stays at 3. |
| P1 prereq | `d2479fe9` | 11 out-of-registry emitter tags reconciled (all normalize-aliases, none needs a ctor); `Opaque` fail-closed boundary sharpened; byte-diff 0; conformance 38/38. |
| P1 expr ADT | `8993a5b9`, `d989985f` | IR-node variant ADT recognizer for **9 expr kinds** (BinOp, Var, Number, String, Subscript, Attribute, Call, MkTuple, FieldGet): discriminant (`is_K`) + field projection + structural-recursion `variant`. **Removed the `emit_ir`-unbound wall** that blocked tier-1/tier-2. Locks 0878–0881. |
| P3 certificate | `959f30c3` | Record-valued `val` promoted from spike into the **real** Rocq+Lean build (`Phase2b_RecordVal.v`, `RecordVal.lean`, both compiled). Read-back/frame/conservativity proved; `pycsl_soundness`/`pycslSoundnessVerified` re-prove UNCHANGED; `Print Assumptions`/`#print axioms` **byte-identical to baseline — no 4th axiom**. Coupling for the expr ADT satisfied. |
| P4 decision | `d4bcf2c1` | `pure_ast` + `proof2why3` both **leave-trusted**, rigorously argued: `proof2why3` is fail-stop-only (off the runtime trust path, cannot false-verify); `pure_ast` can false-verify in principle but conversion wouldn't close the source→IR-faithfulness gap (the CPython differential oracle is the real control). |
| P2 (partial) | `e73ec7c6`, `1a3479b4` | Re-triage + 3 conversions (count 1252 → 1249). |

**The high-value, high-uncertainty questions are answered:** the value ADT is expressible soundly in
WhyML (P0/P1) AND certifiable without growing the TCB (P3). Tier-3 is **de-risked**.

---

## 3. What FAILED / did NOT deliver (honest)

### 3.1 The ADT enabled ZERO marker conversions so far (the core miss)
Count 1252 → 1249, but the 3 conversions (`_array_coerce_arg`, `_emit_new_ghost_ref`,
`_wrap_body_with_return_catch`) are **string/f-string leaves that read no IR node** — incidental stubs
missed by earlier iterations, **not** ADT-enabled. Net ADT-enabled conversions: **0**.

### 3.2 Phase-2 re-triage under FULL proof: every IR-reading handler still blocked
The expr-scalar ADT removed the *typecheck* error (`emit_ir` now binds) but **no whole-body port of an
IR-reading handler discharges**. Concrete blockers (Phase-2 re-triage, ledger `1a3479b4`):
- **B1 — `.get("value")` scalar-vs-subnode overload:** `Number.value`/`String.value` are scalar leaves,
  but the recognizer maps `value`→sub-node projection → `int`/`string` type clash.
- **B2 — list-shaped `.get("elts")/.get("args")`** lowers to an OPAQUE `array emit_ir` — can't iterate
  faithfully (the deferred `ArrayLit`/`SetLit`/`Tuple`/`DictLit` kinds).
- **B3 — list-recursion termination VC:** the `ir_scanner` bool scanners typecheck but the PROOF FAILS —
  recursion over a node *list* has no `size` measure (`variant` is injected only for scalar `emit_ir`
  params). **0/18 `ir_scanner` stubs convert.** (This is the same "`--no-proof` over-counts" lesson as
  tier-1.)
- **B4 — dict/map field builders** (`functions._build_method_*`, `types._collect_*`) and **str-tag
  inference** (`types.py`) — separate value-model gaps, not addressed by the expr ADT.

### 3.3 The feasibility-check was over-optimistic
P1 inc-3 reported "4/4 real handler idioms lower via the ADT" — but that tested the ADT idiom **in
isolation** (a scratchpad probe of each handler's reflection shape), NOT a whole-body port. Phase-2's
whole-body ports then failed (B1–B3). **Lesson: the per-increment feasibility check must port a WHOLE
body and full-prove it, not a fragment** — otherwise it overstates the Phase-2 yield.

### 3.4 Process/infra failures observed
- **Agent-spawn misfires:** the list-shaped-kinds increment agent misfired **2× consecutively**
  (returns in ~3 s, 0 tool uses, echoes its own system prompt) — a transient infra glitch currently
  blocking clean delegation of the next increment. (Seen once earlier too — string-or-and.)
- **Earlier tier-2a revert (context):** the set-model feature was built then REVERTED
  (`768f5392`→`5c4b87e0`) because its conversion needed IR-reflection in a verified emitter method that
  couldn't self-verify — the finding that *motivated* tier-3. Not a tier-3 failure, but the origin.
- **Build-artifact churn:** the Rocq `make` in P3 dirtied ~130 tracked `.vo`/`.glob`/`.aux` (regenerable;
  restored). The repo tracking compiled Rocq artifacts is a standing hygiene issue.

---

## 4. What I PLAN to do (forward plan, ordered)

The Phase-2 re-triage gave a precise guide. The path to the FIRST real ADT payoff:

**Step 1 — list-shaped-kinds increment (the pivotal unlock).** Closes B2 + B3.
- `preamble.py::_emit_exprir_theory`: add `ArrayLit`/`SetLit`/`Tuple`/`DictLit` ctors with a structural
  **`list emit_ir`** field; add the mutual **`size_list : list emit_ir -> int`** (`with size`).
- `expressions.py`: `elts_of`/`args_of` → `list emit_ir` + faithful iteration lowering.
- `functions.py`: inject `variant { size_list <param> }` for a function recursive over a `list emit_ir`.
- The Phase-0 spike already PROVED this exact shape — realize + lock it.
- **Unblocks the `ir_scanner` family (~34 stubs, the largest cluster) + the list-projection readers.**

**Step 2 — scalar-value-leaf split.** Closes B1.
- Split `.get("value")` by receiver-kind: `Number.value`→`ir_num`/int, `String.value`→string.
- Unblocks the `expressions.py` literal/affine-form readers.

**Step 3 — re-sweep (Phase 2).** Convert the newly-unblocked cluster (`ir_scanner` list-scanners +
literal readers) via the streamlined SL gate (per-function proof). **This is the first real ADT marker
payoff** — expected to move the count meaningfully (~+30 from `ir_scanner` alone if they discharge).

**Step 4 — stmt family + contract family Phase-1 increments**, each followed by a Phase-2 re-sweep.
Then B4 (dict/map builders, str-tag inference) as separate value-model increments.

**Gating (every increment):** spike both provers (no axiom); reference locks (POS + `# pycsl-expected:
FAIL` twin); reference byte-diff 0; conformance 38/38; **feasibility check = a WHOLE-BODY port that
full-proves** (not an idiom fragment — §3.3 lesson); coupling check (list projections return `list
emit_ir`, covered by the conservative `path_get` certificate — likely no new Phase-3 lemma; flag if a
genuinely new value shape appears). Single-writer on the mirror.

**On-demand Phase-3:** the conservative certificate (`959f30c3`) covers generic field-reads. A new
value shape (unlikely for list-of-subnode) would trigger a co-landing lemma per the coupling rule.

---

## 5. Immediate next action + the delegation blocker

The next increment is **Step 1 (list-shaped kinds)**. It is currently blocked by the agent-spawn
misfire (§3.4). Resolution options:
- **(A) Bank the certified foundation, resume the payoff-grind as a dedicated fresh effort** — also
  sidesteps the transient spawn glitch. *(Recommended: strong certified stopping point; the rest is a
  multi-session, delegation-heavy grind.)*
- **(B) Retry the delegation** — may glitch again.
- **(C) Build Step 1 inline** (no sub-agent) — avoids the glitch, but does large emitter + spike + proof
  work directly in the main context.

## 6. Realistic assessment
Tier-3 is a **multi-session build**. The foundation (feasibility + expr ADT + certificate + peripheral
decision) is DONE and certified — genuine, durable, de-risking work. The marker payoff requires more
work than §4 first estimated (see §7 — the forward plan is corrected by independent review).

---

## 7. Independent adversarial review — findings that CHANGE the forward plan

An independent reviewer fact-checked this doc against repo ground truth and stress-tested §4. Full
report: `getting-better/tier3/plan-review.md`. Verdict: **status doc is honest and the FOUNDATION
claims reproduce cleanly — but §4's central quantitative claim does not survive scrutiny. Proceed with
changes.**

### 7.1 CONFIRMED (independently reproduced) — the foundation is solid
- Rocq clean `make` green; `Print Assumptions pycsl_soundness`/`_verified` = only the 2 base extensionality
  axioms, **no 4th/RecordVal axiom**; `Phase2b_RecordVal` all-`Qed`. Lean `lake build` 39/39;
  `#print axioms pycslSoundnessVerified` = the 3-axiom ledger, no `sorryAx`.
- The Phase-0 spike discharges on Alt-Ergo+Z3 (best-of-N), all 4 false twins stay UNPROVEN.
- Conformance 38/38, mirror-check 51/51, count 1249, locks 0878–0881 exist, the 3 P2 conversions are
  exactly the string leaves claimed. **All 5 verify items reproduced** — the "certified, ledger held,
  de-risked foundation" claim is SOUND.

### 7.2 REFUTED / CORRECTED — the forward plan (§4) was wrong on its key point
1. **Step 1 is NOT the `ir_scanner` unlock (most severe — §4 Step 1/3 corrected).** The 34 `ir_scanner`
   stubs split into: **10 generic `obj: Any` walkers** that recurse via `for v in obj.values()` over an
   untyped `Dict[str,Any]` tree — a typed WhyML variant has **no `.values()`**, so these have **no
   faithful ADT path** without rewriting live source (a genuinely *unsolved* modeling problem, not
   volume); and **22 `stmts: List[int]` structured scanners** that need the **stmt-node ADT (Step 4)**,
   NOT Step 1's expr list-kinds. **Step 1 unblocks neither.** The "~+30 from `ir_scanner`" projection is
   unsupported — and this **repeats the very §3.3 "feasibility-in-isolation over-optimism" this doc
   claimed to have fixed.**
2. **The Step-1 coupling justification was wrong.** `path_get` (Phase2b) is nested *scalar* record
   projection; it models NO list-of-subnode type and NO `size_list`. §4's "list projections covered by
   the conservative `path_get` certificate" is incorrect — `size_list` soundness is a Why3-intrinsic
   termination VC, not something `path_get` certifies.
3. **"No research risk, just execution volume" is overstated.** Generic heterogeneous `.values()`
   reflection is an unsolved modeling problem; B4 (dict/map builders) is a separate value-model gap.
4. **The certificate is a conservative side-car, not an integration.** `val7` sits *alongside* the core
   `val` (no `VRec` in the core inductive) — which is *why* the ledger held. Genuine feasibility proof,
   but "the emitter ADT is certified by the Phase-7 model" implies tighter coupling than exists.
5. **Opportunity cost is real.** tier-1 = 8, tier-2 = 0, tier-3 = 0 ADT-enabled conversions; the
   `ensures True` P2 conversions reduce count without behavioral content. The value-first "leave-trusted"
   doctrine likely applies to MORE of the frontier than the plans concede.

### 7.3 Corrected forward plan
- **Re-scope Step 1** and **re-baseline the payoff projection** — the `ir_scanner` cluster is NOT freed
  by expr list-kinds. Before any further build, a **whole-body full-proof feasibility pass** (not
  idiom-in-isolation) must identify the *actually*-convertible set. Expect it to be smaller and to need
  the **stmt-node ADT** first for the structured scanners, while the generic-`Any`-tree walkers may be
  **genuinely unmodellable → leave-trusted**.
- Given tier-1/2/3 marker yields (8 / 0 / 0) and finding #5, seriously weigh **stopping the marker
  campaign** and banking the certified foundation as the deliverable, rather than continuing a
  multi-session grind whose realized payoff is far smaller and harder than §4 projected.
