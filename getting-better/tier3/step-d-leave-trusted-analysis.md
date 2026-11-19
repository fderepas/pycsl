# tier-3 v2 — Step D: leave-trusted soundness analysis of the residual

Closes `triage-ranked-tcb-tier3-phase3-v2.md` §4 Step D / §6. Rigorous false-verifies-vs-fail-stop
analysis of the stubs the PATH-1 harvest left `\trusted`, matching the Phase-4 rigor
(`getting-better/tier3/phase4-peripheral-decision.md`). After the harvest the mirror sits at count
**1240**; this classifies the residual so the campaign is closed honestly, not just numerically.

The residual has **two distinct categories** — they must not be conflated:

## Category 1 — the 2 UNMODELLABLE stubs → LEAVE-TRUSTED (by-design)

`IRScanner.find_named_expr_targets(obj: Any, targets: Set[str]) -> None` (ir_scanner.py:61) and
`_collect_assign_targets(self, node: Any, acc: Set[str]) -> None` (functions.py:378). Both recursively
walk an **untyped `Any` tree** (dict via `.values()`, list) and **mutate a by-reference `Set[str]`
accumulator** (`.add`). Doubly outside the ADT: generic `.values()` reflection (no typed `.get("type")`
dispatch) **and** by-ref set-param mutation (the WL-05 rejection class).

**Why LEAVE-TRUSTED is correct — the pure_ast reasoning, not "it's minor":**
The self-annotation's fixed contract shape is **type-safety + frame** (`requires True / ensures True /
assigns \nothing`) — it never expresses the property that actually matters here: *"this correctly
identifies ALL assigned / NamedExpr-target variables."* There is no spec to verify that against. So a
converted version would prove only that the walker is well-typed and effect-framed — **not** that its
variable analysis is correct. **Conversion would add ≈0 soundness value** — the same conclusion Phase 4
reached for `pure_ast`.

**False-verify vs fail-stop (honest):** these helpers feed the emitter's frame/ref analysis (which
variables are assigned → declared / `ref`). A bug that *under-collects* a target could, in a bad case,
loosen a `writes` frame and let a caller prove a variable unchanged when it changes — a *potential*
false-verify path (not pure fail-stop). **But that risk is unchanged by leaving them trusted**: the
weak fixed contract a conversion could prove would not catch a wrong-variable-set bug either. The real
controls are elsewhere and unaffected: (a) the reference corpus (a mis-framed emission is overwhelmingly
a Why3 type-check failure = fail-stop, or a caught proof failure), and (b) the formal-semantics
translation-scheme soundness (LINK 2). **Verdict: LEAVE-TRUSTED** — conversion is impossible (WL-05)
and would not close the gap that matters. *Flip only if* a frame-faithfulness spec + a by-ref-set model
existed to verify these against — neither does.

## Category 2 — the 141 SEMANTIC-CEILING stubs → TRUSTED-PENDING (not leave-trusted)

The census's 141 "other-blocker" stubs (85 `Dict[str,Any]` value-typing, 43 collection-result modeling,
13 emitter string/self-state/WhyML-gen bugs) are a **different residual**: they are trusted **because
they are blocked by value-model gaps the IR-node ADT does not address** (raw-dict field typing,
collection-result modeling, f-string-hash emission) — **not** because conversion is pointless.

**Honest status:** these remain in the self-annotation TCB, **unconverted**. They are **not a soundness
hole** — a `\trusted` stub proves nothing false; it is *assumed*, and the live tool's correctness on
user programs rests on the corpus + LINK-1/2/3, not on these being self-proven. They are **convertible
in principle** if the underlying value-model features (`Dict[str,Any]` typing, faithful collection
results, string-emission fixes) were built — a **separate, larger effort with its own ROI question**,
which the tier-1/2/3 yield history (8 / 0 / 9) suggests is also low-return and should be demand-driven,
not campaigned. They are **explicitly NOT declared leave-trusted here** — that decision is deferred to
whoever scopes the value-model work, with the data in `whole-body-census.md`.

## Bottom line (campaign closure)

- **Certified foundation** (independently verified): the IR-node ADT self-verification is feasible +
  sound, 3-axiom ledger held. Durable deliverable.
- **Harvest:** 9 `ir_scanner` walkers converted, **count 1249 → 1240**, whole-body-proven, zero build.
- **Residual, honestly split:** **2 LEAVE-TRUSTED** (Category 1, conversion impossible + valueless) +
  **141 TRUSTED-PENDING** (Category 2, blocked by separate value-model gaps, low-ROI, demand-driven if
  ever) + the **4 irreducible floor** stubs (I/O + hashlib).
- **The ADT's total reachable payoff was ≤ 19 of 164** — the campaign is closed at its honest floor;
  no ADT build is worth doing. Marker campaign **CLOSED**.
