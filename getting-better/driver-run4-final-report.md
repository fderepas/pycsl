# Driver run #4 — final report (self-tcb-reduction-driver, AUTONOMOUS, 96 h)

Window: 2026-10-31T14:35Z .. 2026-11-04T14:35Z (deadline file `getting-better/.driver-deadline` = 1793802904).
Branch `ghost-assign-bc6`, commits `dd6b1b4cc..HEAD` (local only, never pushed). Run-log entries 336-452
(`getting-better/driver-run-log.md`); landing breadcrumbs in `getting-better/driver-progress.log`; driver notes in the
session scratchpad `run4-notes.md`.

## 1. Iterations and landings
- 117 run-log entries (336-452), ~235 commits on the branch since dd6b1b4cc (all commit-only).
- Every landing went through the driver's own battery (integration worktree int<N> = main + executor picks, then
  v<N>): new corpus files vs their `pycsl-expected`, a sample of every route's witnesses x default / typed / store,
  corpus root + pyref byte-diff against the previous main's emission, mirror emission sweep (every mover re-proved
  whole-file BY THE DRIVER on the integrated tree), fidelity (sync, mirror-check, doc-coherency), and the --slow planes
  (85/85) — i.e. the slow planes ran at every landing, not only once a day.
- Landings (main): cross-mixin B0/B1/B2 (1217d2745) and B4 `#@ declared_in`; sw1 swallowed-exceptions plane;
  routes #496 / #498-#500; #501-#505; #506; #507-#509; #510-#518; the lex-char-class conversion; #519 / #520 + #510
  residual (v30); #523 #525 #527 #528 (v31); #529-#539 (v32); #521 #522 #524 #526 (v33); the whyml_ident conversion
  (v34); #540-#545 (v35); #546-#555 (v37); #557 #559 #563 #564 (v38, the last landing, 4606c27d4).
- Red-team rounds rt43-rt53 (11 rounds), each starting with a convergence re-proof of the previous round's confirmed
  pairs (every convergence check: the previous pairs all refused or not proved once their repair landed):
  rt44 139 -> rt45 15 -> rt46 134 -> rt47 192 -> rt48 76 -> rt49 275 -> rt50 342 -> rt51 301 -> rt52 263 -> rt53 252 confirmed
  (probe, mode) pairs; rt43 was a clean convergence round (rt42's 139/139 refused). Default mode carried almost every
  false proof; typed / store fail closed except rt52's three import families.

## 2. Stubs converted and trusted count
- `\trusted` grep lines: start 437 -> end 415 (−22); TCB net −4 (`#@ declared_in` is a distinct, counted class).
- Conversions (verbatim live body, whole-file proof 0 non-Valid, non-vacuous, driver re-proved every mover):
  - cross-mixin B4: 20 interface stubs re-declared `#@ declared_in` (gross −20, net −2: the declarations are
    checked by the declaration-conformance plane B2; user-decision item 7 below);
  - proof2why3/parser.py::lex (lex-char-class wall BROKEN: deterministic is* predicates over computed receivers, a
    definitional isalnum, the `in "<literal>"` fold, a proved module str-list literal) — 417 -> 416;
  - module6_whyml/identifiers.py::whyml_ident (lever lv6, str-iteration chain: unicodedata.normalize as a law-free
    op, `sep.join(<char-filter genexp>)` as an inline executable fold, a `for` target over a str typed string) —
    416 -> 415; movers identifiers 23/0, pure_ast 3408/0, pycsl 743/0.
- No re-trust this run. Proof-axiom ledger 3 throughout.

## 3. Walls
- cross-mixin-declaration-stubs (carried from run #3): B0/B1/B2 landed after the 5.5 h statements.py proof
  (24605/0) + Transpiler / stmt_control_flow re-proofs; B4 `declared_in` landed.
- lex-char-class: full cycle (report -> independent fable review -> impl -> spike lx1 REFINES -> build lx2) —
  BROKEN, 1 conversion; six movers re-proved by the driver.
- boolop-value-model lever: CERTIFIED-BOUNDARY (CORRECTNESS).
- closure-lift lever: measured, 0 direct yield (COST/SCALE, a link in long chains).
- str-iteration lever (lv6): BROKEN, 1 conversion; reopening = a module-level Set[str] literal with a membership law
  (WHYML_RESERVED, ~80 elements: COST/SCALE).
- Census cv7 (all trusted stubs, 11-01): no cheap stub remained; binding constraint stays the value-model seam
  (int-erasure, R325, in-place mutators). rt49-rt52 kept finding the REFUSAL side of that same seam (values the model
  erases to int / None not modelled), now fenced by #521-#545.

## 4. Routes
- Opened this run: #496-#564 (69), each driver-reproduced (exemplars rc 0 SUCCESS + a CPython breach) before opening.
- Repaired and landed: #496, #498-#555, #557, #559, #563, #564 (64 routes) — every repair refuse-by-default, no new axiom, witnesses refused in
  all three models, corpus witnesses + controls + census rows + advice audit + annotations §7 + route docs.
- Still open: #497 (user decision); #556 #558 #560 #561 #562 (opened from rt53 at the end of the run, first in line for run #5: builtin objects as haystacks, bytes(n) as an opaque int, IntEnum members, generator consumers and comprehension bodies); named residual of #546 (a Tuple nested in Optional / Union / a container still collapses its slots — accepted to keep the mirror stmt_control_flow emission inert before the deadline).
- Integration-only defects the driver caught and fixed (each would have been a red battery on main): three
  cross-executor interactions where two refuse-by-default repairs, each green on its own tree, over-refused the other's
  control or the mirror (8486: #534 x #539; 8367: #527 x #526; the mirror identifiers.py: lv6 x #542 through a false
  `int` annotation), plus a hand merge of two executors' blocks in the #315 judge (#529 x #533). Lesson banked:
  integration batteries must re-run every executor's controls and the full mirror sweep, not only the union of
  their own gates.
- Slow-plane note: one load-induced timeout (check-internal-crash-free on 7341, 359 s emission on the old main)
  re-run alone green; recorded, not loosened.

## 5. User-decision items (not decided by the driver)
1. #497 `\abstract` with an executable body (counted as trust, or refuse executing bodies?).
2. +1 trusted errors.PyCSLError.__init__ (proves with `requires line >= 0`; 92 construction sites).
3. #429 Latin-1 upper/lower closure (also: ord_op's `0 <= ord(c) < 256` is the Latin-1 model).
4. #414 MemoryError assumption.
5. #461 / top-level execution policy (the verifier partially executes module top levels).
6. Severity classifications (#461 Severity-2, #488 Severity-2).
7. cross-mixin B4: `#@ declared_in` as a distinct counted class.
8. The dict-model boundary (conversions as a certified boundary) and the #UND hashing residual.
9. heavy.sh: 2 shared slots starve the queue with 4-5 executors (waits of 30-60 min per job this run); a 3rd NORMAL
   slot, or per-executor quotas.

## 6. Leftover worktrees
- /home/fabrice/git/pycsl -- main worktree (branch ghost-assign-bc6, HEAD after the report commit); unrelated dirty files
  untouched (heavy.sh, session.txt, .aux / .olean artifacts, w7 / w8 gitlinks, the external commit aa95e0789's leftovers).
- /home/fabrice/git/pycsl-v-s1base -- the driver's verification base (detached, used for exemplar repros); safe to remove.
- No executor / integration worktree is left (u3-u24, rt43-rt53, lv6, int13-int31 all pruned after landing).

## 7. Lessons (run4)
- Rule 3 / heavy queue: with 3-5 executors the queue, not the code, sets the pace; serialise by GO files when a
  multi-hour LOW proof runs, and keep every job <= 20-30 min.
- Executors that end a turn waiting on a monitor that already fired stall silently (rt50 twice): briefs now say
  "never end your turn while waiting; poll your own outputs".
- CPython overflow probes are memory bombs (the 11-01 OOM): CPython checks run inside heavy.sh or under ulimit.
- Census: never `--append-new` over the backlog; append only one's own rows with `_census_row`.
- Integration interactions (section 4) — the controls of every executor are part of every integration battery.

## 8. Final-main convergence check (2026-11-04T13:15Z, main 06c92aa69)
The driver re-ran the exemplars it had reproduced before opening routes #540-#564 (29 probes, default mode) on the
final main: every exemplar of a REPAIRED route is refused (R540 R541 R542 R543 R545 R549 R551 R552 R554 R555 R557 R559
R563 R564) or NOT PROVED on its fence obligation (#544 #546 #547 #548 #550 #553); the exemplars of the five OPEN
routes #556 #558 #560 #561 #562 still prove (Verification SUCCESS) — consistent with section 4. Output:
session scratchpad `conv.out`.
