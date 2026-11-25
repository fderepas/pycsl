# Run #10 brief: put `\trusted` reduction first

Written 2026-11-25 during run #9, at the user's request. The run #10 driver reads this file before anything else. It adds to scratchpad/run9/RULES.md; where the two conflict on ordering, this file wins. Every soundness rule in RULES.md still applies.

## Why

`\trusted` went from 366 to 365 in run #9, and from 366 to 367 to 366 in run #8, so it barely moved in either run. Most executor time and most heavy slots went to closing PRE-EXISTING soundness routes that red teams found. Run #9 had about 25 of them: #619-#643. Those fixes were worth having. But under the old ordering, every new finding pushed conversions back, so the count stayed flat. Run #10 changes the ordering.

## Priorities (in order)

1. **Land L24 first, if run #9 did not land it.** L24 is the `run9-u77` branch, made of u74, u76 and u77. It holds the `_to_cache_payload` conversion (`\trusted` 365 to 364) and closes route #634. Its integration battery (A-F) and a red team on u77 are still owed. See run #9 log entries 1402, 1405 and 1415.
2. **Start with a cost census of all remaining stubs. It is static only, so it needs no heavy slot.** For each `\trusted` stub, record:
   - how many new emitter capabilities (links) it needs;
   - how many live rewrites;
   - whether it hits a capability boundary, for example termination;
   - whether converting it would move any emission outside the mirror.

   Rank by that cost, not by function size. u74's measurements are an example: `parse_format` needs at least 6 links and 2 rewrites, and `bases_closure` needs a termination model, which is a boundary.
3. **Convert the cheapest stubs first.** Prefer conversions that leave the corpus byte-for-byte unchanged and move only the mirror. They need no new emitter semantics, so red-team rounds stay short. Time-box each stub to 24 h. A stub that runs over is recorded as a boundary, with the measured cost, and the driver moves on.
4. **Share batteries.** Group several cheap conversions behind one integration battery. An F `--slow` run takes about 7 h, so one battery per stub is too slow.

## Capacity split

- **Conversions get at least 2 of every 3 executor slots.** They also get first claim on one of the two heavy slots.
- **A red-team finding INTRODUCED by a batch still blocks that batch from landing.** This is unchanged and not negotiable.
- **A PRE-EXISTING finding is recorded as a route, with a witness when cheap. It does NOT pre-empt conversion work.** At most one soundness executor runs at a time.
  - Exception: a realistic user-program false proof, meaning one a normal program could hit, goes to the front of the soundness queue. It still does not stop conversions that are already running.
- **Soundness-forced re-trusts (+1) are still allowed, and still counted as not progress.**

## Heavy-slot policy

- Do not run a full mirror re-proof campaign like c20. Use the proof-map rule instead: whole-file proofs only for mirror files whose emission moved.
- The 29 unrun c20 jobs (scratchpad/run9/c20-jobs.HOLD.txt) run only when a slot would otherwise sit idle. They are: `stmt_control_flow` vacuity, then `statements`, then `expressions`.

## Reporting

- Report the `\trusted` count in every hourly STATUS and at every landing.
- At the end, list each stub that was attempted, with its outcome: VERIFIED, boundary with its cost, or time-boxed out.

## Open inputs carried over from run #9 (soundness queue, in this order)

- Route #642: program-file gaps in rule M and #635. Suggested fix: apply #483's stdlib allow-list to the program file (rt86).
- Route #643: four more variants of #634: a partial record frame, a dict parameter, a set parameter, and a module global (rt87).
- Routes #637-#641: wrong-body bindings across modules. rt85's FINDINGS have the fix directions.
- v1f, V1D (#613), #618, and rt82 W1 / W2.
- Over-refusals still waiting on the user's decision:
  - `--import-path ""`, and an `--import-path` directory that does not exist;
  - rt85 O1-O4;
  - `os.path` in a set (6026);
  - rt86 o3 / m1 / m4;
  - the `f = b.f` assign re-export (log 1409);
  - any that u77 left open.

  Until the user decides, they stay declared.

- 2026-11-25T13:15Z (run #9 driver): L23 LANDED (af47df99f = u73 + u75; routes #631 / #632 / #633 / #635 (listed modules) / #636 closed). Declared over-refusals it adds to the "waiting on the user" list: rt86 o3 / m1 / m4, 6026, and the `f = b.f` assign re-export (qe72, 10451; log 1409). L24 = run9-u77 (u74 + u76 + u77) is in battery v85; rt88 found no false proof in u77 but a latent fail-closed defect K1 (descendant overrides missing from the receiver family; repair u78 in flight).
