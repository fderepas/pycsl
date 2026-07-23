# driver-backlog.md — the standing, PRE-AUTHORIZED escalation ladder for autonomous runs

The self-tcb-reduction-driver autonomous loop works THIS list, top-to-bottom, without stopping to
ask. Every item here is user-authorized for autonomous pursuit (including session-scale and
certificate-touching builds). The loop escalates to the next item when the cheaper work above it is
exhausted, and only STOPS at the deadline or when every item below is BROKEN / CERTIFIED-BOUNDARY.

**Authority (set by the user, 2026-07-24): FULL.** Auto-pursue every item, including
certificate-touching builds. The only things still gated per-instance are IRREVERSIBLE / OUTWARD
actions — `git push`, anything destructive/outward-facing — never the build/verify itself.

**Discipline that still applies to every item (non-negotiable):** spike-first + refutation-exit (a
wall that refutes is CERTIFIED-BOUNDARY, recorded, NOT ground on); lesson (p) census-first ("does an
existing certified capability already do this?" — enumerate the value models / recognizers before
scoping a new build); the full three-plane gate battery driver-verified fresh; ledger stays 3;
foreground-only sub-agents (lesson n). A checkpoint (commit + one line to
`getting-better/driver-progress.log`) marks each item transition — a breadcrumb, never a stop.

## Ladder (priority order — work top-down)

1. **Cheap drain (always first, §P).** Any `\trusted` stub a fresh census rates `cheap_win==true`.
   Re-run after every wall breaks (a break may unlock cheap follow-ons).

2. **Recognizer-reach extensions (bounded, low-ROI but real).**
   - set-membership + subject-first-param discriminant for `recognize_type_existence` → unblocks
     `_union_c8_test_references_union_var` (measured: ~1 stub; over-engineering-adjacent, do it only
     if item 1 is dry and nothing richer is ready).

3. **The structure-returning `Any`-walker class (session-scale, the big remaining vein).** The mirror
   is dominated by walkers that RETURN a string/dict/list (`_expr_to_whyml`, `_to_bool`, the
   `_build_method_*_ensures_map` family, the `visit_X` unparse family) rather than a bool. The
   bool-existence recognizer cannot model these. This needs a value-PRODUCING tree-transform model
   (not just existence). Spike whether the certified pyval/pydict/stmt_ir catamorphisms can carry a
   RETURNED value before scoping anything new (lesson p). Highest count-ROI if it opens.

4. **The closure / nested-`def` walker family (dropped-closure blocker).** `_check`-style wrappers
   solved; the `found=[False]` / nested-`def` lambda-lift family (`_body_has_raise`,
   `_body_has_diverging_construct`, `_lemma_*`) still drops the closure at emission. Needs the
   emitter to recognize a nested-def existence walker whole. Spike-gate.

5. **R2c — contract-grammar genexp** (`#@ assert all(x >= 0 for x in a)` does not parse). Repairs the
   spec plane of the any/all fold. Independent of R2d/R2e. Grammar work in `Module2_Parser.py`; may
   be its own subsystem — SPLIT and record if so.

6. **R2e — string/capture folds** (element-type parameterization + string-predicate lowering +
   closure-capture threading + `startswith`). 4 coordinated capabilities; clears
   `_handle_fieldassign_stmt` + `_union_arm_tag` (~2 sites) + 11 banked. Session-scale.

7. **The 3 session-scale vacuity residuals** (`_emit_new_ghost_ref`, `_handle_mktuple_expr`,
   `_collect_class_constants`) — each erases a param that flows only into a `\trusted` sibling; needs
   the sibling converted + a value-model feature (e.g. set-param-by-reference). Also the live-tool
   `Set[str].add(param)→()` faithfulness bug (lesson h family) — a real all-users fix worth doing
   under item 7.

8. **Soundness/gate hardening (do opportunistically, never a reason to stop).** The self-state vacuity
   gate's LOWER-BOUND partials; a `check-self-annotate-sync.sh` audit; the 5 flagged judgment-call
   lessons (i,k,g,j',m) carve-outs. Small, bounded, always-available filler between walls.

## Exhaustion = STOP (the ONLY early-stop condition now)
The loop stops before the deadline ONLY when items 1–8 are each BROKEN or CERTIFIED-BOUNDARY for the
current tree — a genuinely empty ladder. "Bounded work ran out" is NOT a stop condition; escalate to
the next session-scale item instead. When you DO record a CERTIFIED-BOUNDARY, note what NEW capability
would reopen it, so a future run (or a future ladder edit) can pick it back up.
