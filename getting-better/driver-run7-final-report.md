# Driver run #7: final report (self-tcb-reduction-driver, AUTONOMOUS, 96 h)

DRAFT. It is updated until the end of the run.

- **Window:** 2026-11-13T09:22Z to 2026-11-17T09:21:52Z (`getting-better/.driver-deadline` = 1794907312).
- **Branch:** `ghost-assign-bc6`. Commit-only: nothing was pushed.
- **Run log:** entries 828 onward in `getting-better/driver-run-log.md`.
- **Plan of record:** `getting-better/driver-run5-plan.md`, with the lessons of run #6, 2 proof slots and PRIO for driver proofs.
- **Main track:** from hour ~5 on, by user decision (log 838), the dict value model. It ran as a full wall cycle:
  - report `getting-better/dict-value-model-r4.md`;
  - Gate R review `-r4-response.md`;
  - Gate P plan `-r4-impl.md`;
  - Gate S spike `-r4-spike.md`.

## 1. Results

- **`\trusted`: 389 → 383 at L9, and 376 at the L10 candidate (int61), pending its battery.** The batch E branch run7-lvT is at 374.
- **Proof-axiom ledger:** 3 throughout. No proof-assistant axiom was added.
- **WhyML assumed facts:** one new reviewed family, CERTIFIED-DEFINITIONAL. It contains the two route-(e2) `pairs_get` equations, realised by Rocq and Lean lemmas. This is the single sanctioned exception to "no new axioms" (user decision (d), log 848). It is counted in the assumed-facts plane, not in the proof-axiom ledger.

(To be completed: landings table, per-stub list, proof hours, routes, decisions, lessons, end state.)
