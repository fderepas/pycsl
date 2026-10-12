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
