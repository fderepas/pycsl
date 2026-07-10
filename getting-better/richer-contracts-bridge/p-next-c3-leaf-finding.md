# P-next (C3-on-live) — measured leaf-first refutation (2026-07-10)

**User chose "continue bridge (P-next)": attempt the `_expr_to_whyml` lift / more emit_F arms to extend
C3-on-live.** Measured before build (§10.2). **Verdict: C3-on-live is NOT a bounded lift — blocked at the
LEAF renderer by Unicode normalization.**

The theorem-schema said C3-on-live is "gated on lifting the recursive `_expr_to_whyml` — verified-compiler-
scale." A leaf-first spike (lift just the identifier/var renderer so a handler over a bare *variable*
argument could reach C3) shows the wall is DEEPER: **`whyml_ident`** — the identifier mangler every handler
renders through, even for a bare variable — computes:
- `unicodedata.normalize('NFD', ch)` (Unicode canonical DECOMPOSITION) over `ord(ch) > 127` codepoints, +
  ASCII-filter, + `WHYML_RESERVED` membership + case-lowering.

A *deterministic WhyML logic model* of `whyml_ident` would have to model the **Unicode NFD decomposition
tables** — a char-level Unicode string wall (beyond W2's simple char-iteration, which does no codepoint
arithmetic or normalization). So the trusted-`val` rendering boundary bottoms out in a **non-logic-
modellable leaf**, not merely the recursive dispatcher. No bounded engineering step provides Unicode NFD in
WhyML logic.

**Consequence.** C3-on-live is gated on modelling Unicode normalization in WhyML — refuted as a bounded
build. The bridge's live-code reach is **capped at C1/C2** (the banked wins), by a *measured* wall, not
momentum. This vindicates the extensional design: LINK-3 coherence treats the emitter's output AS the string
it is (whatever `whyml_ident` computes), covering the semantics without a deterministic re-statement — which
is precisely why the semantic guarantee correctly lives on the coherence side, per method-arm, formally.
Recorded in `src/formal-semantics/bridge-theorem-schema.md` §2 (keep-current). No code, no new axiom.
