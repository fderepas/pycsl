# Convergence metric implementation — status
LAST-UPDATED: 2026-09-14T19:55:00Z
PHASE-1-PROBE-LEDGER: DONE
PHASE-2-VERIFIED-FRACTION: DONE
PHASE-3-REASON-TAXONOMY: DONE (build, per the 2026-09-14 amendment)  (side file + checker; tagging track OPEN: unclassified 458/459; NOT yet wired into run-soundness-planes.sh)
PHASE-4-SILENT-RAISE-BURNDOWN: IN-PROGRESS  (70 -> 69 -> 62, 8 of 70 declared)
PHASE-5-BLIND-RECAPTURE-RUNBOOK: DONE (runbook only, per scope limit)
PHASE-6-GENERATED-SAMPLER: DONE-AUTHORING / BLOCKED:box-busy for the sweep
OVERALL: INCOMPLETE
NEXT-ACTION: Continue Phase 4. THE NEXT CHEAPEST BATCH IS `proof2why3/canonical.py` — EIGHT SILENT stubs in ONE file (_ac_normalize, _alpha_rename, _dedup_arrow_chain, _flatten_foralls, _iff_app_to_binop, _normalize_names, _sort_arrow_hypotheses, substitute), and ALL EIGHT live bodies raise exactly `TypeError`, so it is one exception name across the batch. Plus `proof2why3/normalize.py::_alpha_rename` (same live function, so same name) for nine. *** CAVEAT THAT COSTS TIME: unlike increment 3's batch, canonical.py has NO whole-file proof on record anywhere in the tree (searched: proofs46/48/49 and every scratchpad wN/proofs) — so the successor must FIRST run a baseline proof of canonical.py AT HEAD and only then edit, or there is nothing to compare against. Budget for that. *** VERIFY THE NEVER-CALLED-IN-FILE PROPERTY PER STUB BEFORE EDITING (emit the baseline .mlw, confirm each name occurs ONLY at its own `val` line; derived union TYPE names like `_union__x_1` are declarations, not applications). Phase 3 BUILD IS DONE (6ff56694): the taxonomy lives in getting-better/trusted-reasons.tsv, checked by bin/check-trusted-reasons.py (rc 0; --self-test rc 0). Two Phase-3 follow-ups need NO idle box and can run while the driver runs: (a) wire check-trusted-reasons.py into run-soundness-planes.sh as its own commit, updating every "34 planes" citation to 35 in the same pass; (b) the tagging track — lower MAX_UNCLASSIFIED from 458 by citing measured backlog headings, never by guessing. Do NOT retry the in-band `reason:` token.

## SUPERVISOR SCHEDULING POLICY — SET BY THE USER 2026-09-13 ~18:35Z
THE DRIVER IS PAUSED BETWEEN GENERATIONS TO GIVE THIS WORK THE BOX.
When the current driver generation finishes, the supervisor spawns THIS implementation
agent FIRST and lets it take one increment on an idle box, THEN launches the next driver
generation. Rationale: Phases 3, 4 and the Phase-6 sweep need an idle box; the driver
campaign runs suites/planes/proofs back-to-back for the whole 96h window, so waiting for a
natural gap never fires. The between-generation gap is free box time.
PRIORITY ORDER ON AN IDLE BOX: Phase 4 burn-down FIRST.
*** REVISED 2026-09-14 BY INCREMENT 3, AND THE REASON MATTERS. *** The original order put
Phase 3 first. That was wrong for an IDLE box: `convergence-metric-implement.md` §1 says in
its own words that Phases 1-3 are pure bookkeeping and "can run ALONGSIDE a live driver
generation", while Phases 4-6 consume the box. Phase 3 Option 2 is a side file plus a
histogram — ZERO prover time — so spending a scarce idle window on it WASTES the window.
Phase 4 is the only unblocked phase that actually needs the box (whole-file re-proofs).
SO: Phase 4 on an idle box; Phase 3 whenever, including while the driver runs.
The Phase 6 sweep is LAST and may be deferred to after the window closes (Thu Sep 17).
Take ONE increment, leave the tree clean and committed, update this file, and stop — do not
hold the box longer than the increment needs; the driver is waiting on you.

## COMMITS
  10e58637  Phase 1 — probe ledger + yield reporter + driver rule
  5774b32a  Phase 2 — verified fraction from proof verdicts   (fea721a9 prose repair)
  758fc276  Phase 5 — blind recapture runbook
  184f81cb  Phase 6 — generated differential sampler (authored, not swept)
  e474a883  Phase 3 pilot — gate FIRED, finding written, edit reverted
  46aaaf5c  Phase 4 batch 1 — SILENT 70 -> 69 (exec_splice)
  09d397f7  Phase 4 batch 2 — SILENT 69 -> 62 (seven stubs, six mirror files)
  6ff56694  Phase 3 build — out-of-band reason taxonomy (side file + checker), cherry-picked from 4aa51563

## THE CORRECTED VERIFIED-FRACTION TRIPLE  (bin/verified-fraction.py --staleness=file)
      (1) verified / live      499 / 3225 = 15.47 %
      (2) unproven-perimeter   644 defs in 27 of 53 mirror files
      (3) unmirrored ratchets  MAX_UNMIRRORED_DEFS=549  MAX_UNMIRRORED_FILES=41
          OLDEST PROOF RELIED ON  2026-09-02
          FALSIFICATION GUARD     OK — did not rise since HEAD~1
  Report's figure was 914/3236 = 28.2 %. Population: 26 PROVED / 7 STALE / 18 NO-PROOF /
  2 FAILED. STRICT FLOOR IS 0.00 % (--staleness=strict): no proof in this repo survives a
  single commit to src/pycsl, and the driver commits several times a day.

## PHASE 3 PILOT RECIPE — HISTORICAL: RUN 2026-09-13, GATE FIRED (e474a883). DO NOT RE-RUN; SEE THE 2026-09-14 AMENDMENT IN convergence-metric-implement.md
  PILOT FILE: src/self-annotate/src/frontend/exec_splice.py
    Chosen because it has exactly ONE real marker (line 35, inside `_ExecSplicer`) AND a
    passing whole-file proof on record (w49_exec_splice, rc=0), so there is a baseline and
    a re-proof is cheap. Three other files also have 1 marker — exception_model.py,
    ir_schema.py, module6_whyml/expr_ghost_collections.py — but all three are NO-PROOF.
    NOTE: line 4 of the file contains the marker text inside the MODULE DOCSTRING. That is
    one of the 25 known offset lines. DO NOT EDIT LINE 4 — edit only line 35.
  EDIT: append ` reason:<bucket>` to line 35 only.
  THEN, IN ORDER:
    1. why3 prove --type-only on the edited mirror
    2. emit that file's .mlw and diff against HEAD — MUST BE BYTE-IDENTICAL
    3. bash bin/check-self-annotate-sync.sh      — delta ZERO
    4. bash bin/self-annotate-mirror-check.sh    — delta ZERO
  IF EMISSION MOVES BY ONE BYTE: STOP. That is a comment-level token changing emission,
  which is route-shaped and is the #96 pattern. Write it up as a FINDING and stop Phase 3.

## NOTES
- THE DRIVER IS LIVE AND THE BOX HAS BEEN BUSY SINCE ~16:25Z: `bin/run-reference-tests.sh
  --jobs 6` (suite99), VERDICT=ALIVE, 35 live processes. Phases 3, 4 and the Phase-6 sweep
  are BLOCKED on it. A later spawn will find it free. Route #99 landed at 275146d9 during
  this spawn and is already in probes.tsv.
- .git/index.lock collided twice with the driver; both resolved by waiting 20 s and
  retrying. Never delete the lock.
- THE DRIVER RULE IS ON DISK IN getting-better/.driver-worker-prompt.md BUT THAT FILE IS
  GITIGNORED, so it is NOT version-controlled and is not in any commit. A successor must
  re-check it exists before relying on it.
- PHASE 1 BACK-FILL IS ASYMMETRIC. Every LIVE row was recoverable; FAIL-CLOSED rows exist
  only where a generation wrote a no-finding section. So w49/4/11/16/17 and
  generator=unknown read ~100 % yield as an ARTEFACT OF THE RECORD. Only the
  carve-out-census rows are safe to compare across generations. DO NOT quote the 41.5 %
  aggregate as "the yield". Caveat is in the TSV header.
- PHASE 1 SCHEMA DEFECT FOUND BY ITS OWN ACCEPTANCE TEST and recorded, not silently fixed:
  two probes had been filed OUT-OF-SCOPE because CPython raises, when the record says they
  were RUN AND REFUSED. Rule now: verdict records what the MEASUREMENT returned.
- PHASE 2 STATED LIMITATION: proof run time is the log file's mtime, a proxy a copy would
  inflate. Checked by hand that mtimes are spread over genuine run times, not bulked.
- PHASE 5 FINDING: the blind is STRUCTURALLY PARTIAL. Withholding the three documents the
  report names is NOT sufficient — 271 corpus witness filenames, 20 differential drivers,
  367 commit subjects, 88 getting-better files and 27 src/ files name routes. The last two
  cannot be withheld without changing the artefact under study (src/ names routes in its own
  comments, and reading the emitter IS the hunter's method). Partial sight raises m, which
  lowers N-hat — the SAME direction as the shared-method bias, so the two COMPOUND.
- PHASE 3 IS BIGGER THAN THE PLAN IMPLIES. `unclassified -> 0` is the stated acceptance,
  but driver-backlog.md carries only 4 `[CORRECTNESS]` and 17 `[COST/SCALE]` tagged
  paragraphs against 459 markers across 45 files. Most markers will start `unclassified`
  and driving that bucket to zero is a multi-generation task, not "one pass over 459 lines".
  Say so when Phase 3 lands rather than tagging speculatively — a `correctness:` tag is a
  CLAIM, and this repo's boundary claims have been refuted repeatedly.
- PHASE 4 IS UNDER WAY: MAX_SILENT 70 -> 69 -> 62, lowered ONLY by declaring. Rule:
  order batches by the cheap property gen #16 measured — a `raises` on a val declared but
  never called in-file adds no VC. NEVER raise MAX_SILENT to make the ratchet pass.

## INCREMENT 2 (2026-09-13 ~19:00-20:10Z, idle box granted by the supervisor)

### PHASE 3 PILOT — GATE FIRED. Commit e474a883.
The `reason:` token is NOT byte-inert: it is a PARSE ERROR that REFUSES THE WHOLE FILE.
`Module2_Parser.py:1411 _parse_trusted` accepts `\trusted [reviewer: ID]` and then RETURNS;
the caller raises at :1321 "unexpected trailing input". MINIMAL PAIR shows it is not
`reason:` but ANY trailing token. Reproduced on a second file (exception_model.py:77), so
the scale claim — all 45 marker-bearing files, 459 markers — is measured, not inferred.
CONSEQUENCE IS WORSE THAN "EMISSION MOVED": a refused file emits NO .mlw at all, so a
diff-the-common-files byte sweep reports ZERO CHANGES — a FALSE GREEN. This is route
#42/#50 live, and a demonstration that byte-diff-compare.py's GONE arm earns its keep.
The PARSE gate caught it; the byte-diff would not have.
FULL WRITE-UP: getting-better/open-routes/finding-reason-token-refuses-the-whole-file.md
DO NOT RETRY THE IN-BAND TOKEN. Choose option 2 (out-of-band taxonomy side file).

### PHASE 4 — FIRST BATCH LANDED. Commit 46aaaf5c. SILENT 70 -> 69.
exec_splice.py::_ExecSplicer.visit_Expr now declares `#@ raises PyCSLParseError when True`.
MAX_SILENT lowered 70 -> 69, monotonically. THE BOUND WAS NEVER RAISED.
The `when True` is an OVER-APPROXIMATION and is recorded as one in the ratchet history and
the commit: the real condition (constant-exec whose literal fails to parse / splices a
non-whitelisted stmt / contains a nested exec) is not expressible against a parameter that
lowers to an opaque `int`. Same idiom as ir_schema.py:171 and desugar.py:56.
Acceptance: parse+type L1/L2/L3-tc OK; whole-file re-proof rc=0 with ZERO non-Valid goals
checked INDEPENDENTLY of the SUCCESS banner (proofs49/cm4_exec_splice.{log,rc}, 2m14s);
markers unchanged at 459; check-self-annotate-sync.sh rc=0; mirror-check delta zero.
Cheap property verified BEFORE editing: the stub is never called in-file (baseline .mlw
line 285 declares the val and never applies it), so the raises adds no VC.

### PLANE BATTERY
19 fast planes green (proofs49/cm4_planes_fast.rc, rc=0, 45s). THEN THE FULL SET:
**ALL 34 PLANES GREEN, rc=0** (proofs49/cm4_planes_all.{log,rc}, ~40 min, `--slow`),
including check-trusted-frame-honesty and BOTH differential corpora.
The 34 was verified by COUNTING the `ok` lines (`grep -c '    ok '` -> 34), not by reading
the summary line — gen #15 counted wrong and that is how the 19-vs-34 error happened.
THE SET IS 34 = 19 FAST + 15 SLOW.
Gen #15's error was to treat the fast 19 as the whole set; the omitted 15 include
check-trusted-frame-honesty and BOTH differential corpora, i.e. the closest relatives of a
trusted-stub raises change. NEVER report "planes green" from the fast set alone.
METHODOLOGY CARRIED FORWARD: an A/B comparison controls for CHANGE, never for COVERAGE.
Applied here — the Phase 3 baseline was coverage-checked (the emitted .mlw demonstrably
contains the marked function as a bodyless val) rather than merely compared against itself.

### PRE-EXISTING, NOT MINE
self-annotate-mirror-check.sh is rc=1 at HEAD on expr_ghost_collections.py / statements.py /
stmt_control_flow.py. Confirmed pre-existing: `git diff HEAD --stat` was empty when first
observed and none of those files was touched. Same family as
finding-L1-fidelity-plane-red-at-head.md.

## INCREMENT 3 (2026-09-14 ~11:15-12:10Z, idle box granted by the supervisor)

### THE CHOICE: PHASE 4, NOT PHASE 3 — AND WHY
The handoff's priority order said Phase 3 first. I took Phase 4 instead, deliberately.
`convergence-metric-implement.md` §1 states that Phases 1-3 are pure bookkeeping and can run
ALONGSIDE a live driver generation, and that Phases 4-6 consume the box. Phase 3 Option 2 is
a side file plus a histogram: ZERO prover time. Spending a scarce idle window on it would
have burned the one resource Phase 4 cannot proceed without. The priority block above is
amended accordingly. Phase 3 is NOT deprioritised — it is rescheduled onto driver time.

### PHASE 4 — SECOND BATCH LANDED. SILENT 69 -> 62.
SEVEN stubs across SIX mirror files, every exception name read off the LIVE AST:
  proof2why3/crosscheck.py::_load_axiom_registry        RuntimeError
  proof2why3/crosscheck_ir.py::_load_axiom_registry     RuntimeError
  proof2why3/sertop.py::_sexp_parse                     ValueError
  frontend/ConcurrencyChecker.py::check                 PyCSLSemanticError
  frontend/import_classifier.py::check_imports          PyCSLSemanticError
  frontend/ir_inline.py::_expand                        PyCSLSemanticError
  frontend/ir_inline.py::_inline_calls                  PyCSLSemanticError
MAX_SILENT lowered 69 -> 62, monotonically. THE BOUND WAS NEVER RAISED.
All seven `when True` are OVER-APPROXIMATIONS and are declared as such in the ratchet
history, with the real condition written out per stub and the reason it is not expressible.
ONE OF THEM IS WORTH SINGLING OUT: `_sexp_parse`'s FIRST raise path (`not tokens`) IS
expressible — `tokens` lowers to `array string` — but declaring only that path would
UNDER-approximate, and an under-approximating `raises` is a FALSE declaration, not a tighter
one. Over-approximating is the safe direction; it is strictly weaker than the silent stub.

### CHEAP PROPERTY VERIFIED PER STUB *BEFORE* EDITING (all 7/7)
Baseline `.mlw` emitted for each of the six files first; each of the seven names occurs
EXACTLY ONCE in its emission, at its own bodyless `val` line, and nowhere else — so each
`raises` adds no VC. The only other textual hits are derived union TYPE names
(`_union__inline_calls_2`, `_union__expand_1`, `_union_concurrencychecker_0`), which are
declarations, not applications. Recording that distinction because it is the thing that
would silently make this batch expensive if a successor mistook it for a call site.

### GATE VERDICTS, EACH WITH ITS POPULATION
  emit + `why3 prove --type-only`   6/6 files rc=0, and EVERY FILE GREW (3254->3315,
        9216->9277, 5103->5137, 2521->2594, 12933->13006, 31108->31192). The growth is the
        point: increment 2's `reason:` token produced NO .mlw at all, and a common-files
        byte diff read that as zero changes. A green here that did not grow would be that
        same false green. CHECKED, not assumed.
  emission diff base->after         EXACTLY 7 `raises { E -> true }` clauses + 4 new
        `exception E` declarations. Nothing else moved; no other `val` touched.
  whole-file re-proofs              6 files, 503 goals, 0 non-Valid, all rc=0
        (`getting-better/proofs49/cm5_{crosscheck,crosscheck_ir,sertop,concurrency,
        import_class,ir_inline}.{log,rc}`; 12.8s/37.0s/55.6s/12.4s/137.0s/162.0s).
        Non-Valid counted by grepping the prover verdicts, INDEPENDENTLY of the banner.
  check-trusted-raises-honesty      population 75, 13 declared / 62 SILENT, ratchet 62, rc=0
  ^ NEGATIVE TEST OF THAT RATCHET   planted defect (deleted the new `#@ raises` line from
        sertop.py) -> rc=1, "SILENT RATCHET BROKEN — 63 > 62", and it NAMED the exact stub.
        Restored; rc back to 0. The green is believed because the red was demonstrated.
  count-trusted-directives          markers 459 / grep 484 / offset 25 / unattached 0, rc=0
        — UNCHANGED, as it must be: a `#@ raises` line is not a `\trusted` marker.
  check-self-annotate-sync.sh       rc=0 over 887 un-trusted mirror functions
  self-annotate-mirror-check.sh     rc=1, DELTA ZERO — the same three pre-existing files
        (expr_ghost_collections.py, statements.py, stmt_control_flow.py), none of mine.
        Pre-existing at HEAD; same family as finding-L1-fidelity-plane-red-at-head.md.

### REFERENCE SUITE DELIBERATELY NOT RE-RUN, AND THE REASON IS CHECKABLE
`git diff --name-only` contains NO path under `src/pycsl/`. The shipped compiler is
byte-unchanged, so the 3430/3448 baseline cannot move. The diff is six mirror files plus the
ratchet constant. Stating the check rather than the conclusion so the next reader can redo it
in one command. If a successor's Phase-4 batch ever touches `src/pycsl/`, this reasoning
EXPIRES and the suite must be run.

### A NOTE ON WHAT THE RATCHET DOES NOT CHECK
`check-trusted-raises-honesty.py`'s `declared` test matches any `#@` line containing the word
`raises`. It does NOT check that the declared exception NAME is the one the live body raises.
So the seven names above are on the author, not on the tool; each was read off the live AST by
hand and is recorded in the ratchet history. A successor could satisfy this ratchet with a
wrong name and nothing would say so — worth a future hardening, and cheap: the checker already
computes `KINDS[name]` for exactly this purpose and simply never compares it.

## LANDING 2026-09-14 ~19:50Z (supervising session) — increment 3 committed, Phase 3 built

### WHY A SUPERVISOR COMMITTED INCREMENT 3
The increment-3 agent (session 72fe2917) finished its gates and launched a 34-plane re-check
at 15:34, then its session ended (transcript last written 15:44) BEFORE it committed. The
re-check completed unattended: cm6_planes_all rc=0, 34/34 `ok` lines counted, 2158 s. The
tree was left dirty and the box sat idle ~11:30-19:40; no driver generation was launched.
TREE IDENTITY WAS CHECKED, NOT ASSUMED: every modified file's mtime is 11:22-11:28, HEAD did
not move after 11:17, so the 15:34 plane run covered exactly the committed tree. Cheap gates
re-run at commit time: trusted-raises-honesty 13/62 rc=0; markers 459; self-annotate-sync rc=0;
no path under src/pycsl/. Landed as 09d397f7 with cm5_* and cm6_planes_all evidence.

### PHASE 3 BUILD — 6ff56694 (built by a delegate in a worktree, verified independently)
Side file getting-better/trusted-reasons.tsv (459 rows = 459 markers), checker
bin/check-trusted-reasons.py (both attachment directions, reason grammar, backlog-heading
cite rule, zero-input guard, MAX_UNCLASSIFIED=458 ratchet, --sync/--write, --self-test,
histogram), shared walk bin/trusted_markers.py, histogram in count-trusted-directives --metrics,
dated AMENDMENT in convergence-metric-implement.md §Phase 3 redefining DONE.
Histogram: correctness 0 · cost-scale 1 (Module5_IREmitter _py_stmts_to_ir, cite
"L2 `_py_stmts_to_ir`") · spent-rc0 0 · unclassified 458.
SUPERVISOR VERIFICATION, INDEPENDENT OF THE DELEGATE'S REPORT:
  - a from-scratch marker->qualname walk produced 459 keys IDENTICAL to the TSV's (no dups);
  - count-trusted-directives default output byte-identical vs the 3c4f290c version (rc 0),
    and with --emit-dir on an empty dir (rc 2 both); extracted helpers AST-identical;
  - defects planted beyond the delegate's self-test all went red (rc 1): qualname case change,
    right name in wrong file, trailing space in a reason, extra column, marker removed from a
    mirror copy (orphan), stub added to a mirror copy (missing + ratchet); positive controls
    (spent-rc0; correctness with a real unique heading) rc 0;
  - after the cherry-pick onto 09d397f7: check rc 0, --self-test rc 0, --metrics rc 0,
    markers 459, raises-honesty 62 rc 0.
KNOWN AND ACCEPTED: CRLF TSVs are tolerated (keys still match). A NEW `\trusted` marker breaks
MAX_UNCLASSIFIED even after --sync --write, until it is classified — intended (forces
classification at spend time) but it is driver friction once the plane is wired.
NOT DONE: wiring into run-soundness-planes.sh (34 -> 35); the tagging track; no slow planes
were re-run for 6ff56694 — it touches no src/ path and only adds a standalone checker, and the
one existing plane it edits (count-trusted-directives.py) was diffed output-identical.
