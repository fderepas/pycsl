# W-SB — implementation plan (from `string-builder-wall.md` + `string-builder-wall-response.md`)

Gate P: every step is SPIKE-FIRST with a REFUTATION EXIT; the three-L-plane battery
(fidelity, whole-file Why3 of every mirror whose emission moves, corpus+pyref byte-diff — M1 if
non-zero) + ledger 3 + non-vacuity gates every landing. Order follows the review's §6.

## S0 — fail-open L3-tc (precondition for every later measurement)  [cost: minutes]
Make `_why3_typecheck` return ok=False when why3 is absent (live + mirror verbatim).
Refutation exit: `env -i … pycsl.py <ill-typed> --no-proof` still prints SUCCESS -> stop, re-plan.
Gates: fidelity; whole-file proof of mirror `pycsl.py` (its emission moves); fast planes.

## S1 — route #231 (f-string spec / conversion dropped)  [cost: hours, in worktree r231]
Executor builds the spec-keyed opaque lowering (D1) or the fail-closed refusal (D0, the
reviewer's minimal sound step). Witnesses: `f"{b:02x}"==f"{b}"`, `f"{s!r}"==f"{s}"`,
`\result == s` over `f"{s!r}"` (FAIL); spec-free twins + 1705/1706 (PASS).
Refutation exit: any spec-free f-string's emission moves, or a witness still proves.

## S2 — A(i): carry declared `List[str]` element types outside `@mutable_state`  [spike first]
Spike on ONE marker, `identifiers.whyml_ident` (and the builder shape of
`whyml_string_literal`): populate `_array_elem_types`/`_seq_value_types` from declared
`List[str]` annotations (params, annotated locals, str loop targets), consumers restricted to
`.append` / `join` / `+` / `return`. Re-run the first-error probe before/after.
REFUTE (-> CERTIFIED-BOUNDARY for A(i), record, stop) if (a) the first error does not move off
the `Seq.snoc` line, or (b) the corpus sweep moves any file other than by an intended re-typing
that still proves. A move to a NON-SB next blocker is a PASS for the spike (the #64 prior: the
unit of work is the marker's whole chain).
## S3 — A(ii) definitional join: only if S2 reaches a contract that needs join CONTENT.
## S4 — `.get` on a str->str dict constant / `.encode` / `%`: only when a chain probe reaches them.

Expected count payoff is SMALL (string-builder is the first blocker of only 16/435 stubs); the
value of W-SB is (1) the Sev-1 repair, (2) an honest instrument, (3) one link in the #64 chains.

## S2 RESULT (gen #36, 2026-10-12) — REFUTED by criterion (a); A(i) parked as a LOW-ROI COST/SCALE lever
The mechanism WORKS (builder probe and `", ".join(xs)` over a `List[str]` param go L3-tc ✗ -> ✓,
emitting `str_join_seq` / `str_join_arr`; patch kept at `getting-better/wsb/s2-ai.patch`, 79 lines:
declared `List[str]` locals -> `seq_value_types = "string"` via `_detect_seq_promotion`; params via
`param_list_flat_elem`). But on BOTH spike markers the first error stays on the `Seq.snoc` line,
because the APPENDED ELEMENT is itself produced int-erased upstream:
  * `whyml_ident`: `''.join(c for c in decomp ...)` (join over a GENERATOR) emits `(join_1 0)`, and
    `unicodedata.normalize` is an opaque int; the live `sanitized = []` is unannotated anyway.
  * `whyml_string_literal`: `_WHYML_STR_ESCAPES.get(ch)` (no default) is an int val (route C); with it
    removed, the next error is `ch.encode` (route E).
So A(i) pays only together with C (str->str dict-constant `.get`), E (`.encode`), a generator join,
and `unicodedata` — a chain of 4-5 capabilities for <= 2 markers. Classified COST/SCALE (not a
correctness boundary); ROI ranks it BELOW the in-place-mutator wall (#61a: first blocker of 77
stubs by the W-SB census). Reopen when a chain probe of a higher-ROI lever needs it.
W-SB net: route #231 (Sev-1) repaired, S0 instrument fix landed; count unchanged.
