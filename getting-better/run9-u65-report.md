# run #9 executor u65 -- routes #619 / #620 (non-vacuity gate escapes found by red team rt75)

Branch `run9-u65` (worktree `/home/fabrice/git/pycsl-u65`), base **b1400b11c** (= ghost-assign-bc6 at
log 1284; contains L19 c115e0a5a, the u62 / u63 probe builder). Base tree for every base measurement:
detached worktree `/home/fabrice/git/pycsl-u65b` at b1400b11c. Never pushed. Logs below are relative to
`scratchpad/u65/` in the branch.

## 1. Summary

| item | base b1400b11c | head |
|---|---|---|
| rt75 c12 (vacuous `f` = 2nd member of `let rec g ... with function f`) | Verification SUCCESS | FAILED, vacuous `f` |
| rt75 c19 (top-level `def c__m -> NoReturn` + vacuous method `C.m`, both `c__m`) | Verification SUCCESS | REFUSED `PYCSL-SEM-WHYML-NAME-CLASH` |
| NEW c22 (module `def f -> NoReturn` rebound by a vacuous `def f`) | Verification SUCCESS | FAILED, vacuous `f` |
| rt75 F3 c13 (`let lemma l1`) | FAILED, reported as `lemma` | FAILED, reported as `l1` |
| controls c01 / c12b / c21 | FAILED vacuous | FAILED vacuous (unchanged) |

Three pre-existing escapes closed (c12, c19, and a third one found while measuring #620: c22). No
`\trusted` added (366), no axiom (ledger 3), no gate loosened. Every edit is in two functions whose mirror
twins are `\trusted` (`_run_pipeline`, `_run_vacuity_gate`); `_function_body_eqs` / `_LET_FN_RE`
(verified twin) are untouched.

## 2. Route #619: every member of a program `let rec ... with ...` group is probed

`src/pycsl/pycsl.py::_run_vacuity_gate`. The probe builder only recognised `^  let` headers, so the
second and later members of a program mutual-recursion group (`  with [function |ghost |lemma ]name`)
had no probe. Now:

- A header is `^  (let [rec ]|with )(function |ghost |lemma )*<name>`. A `with` line is a header ONLY
  when the group was opened by `let`. Any other top-level declaration (`^\S`, or `^  val|function|
  predicate|lemma|axiom|goal|type|constant|inductive|coinductive|exception|use|clone|scope|end|meta`)
  ends the `let` group. So members of logic groups (`function ... with function`, `type ... with`,
  `predicate ... with`) are never probed. These are not program functions.
- A `with` member is split like a `let` (u62) when its body `=` is on the header line. Its probe goes
  before its OWN `  =` line, as for a `let`. The constant rule (u63) applies unchanged.
- The u62 rescan now reads the header kinds the split pass recorded (`_t619`). The result is identical
  for every `let` line.
- Route #267's per-function body now also ends at a `  with` line, so each member's call sites are its
  own. Route #260's back-scan for `raises` stops at the member's own `with` header.
- F3: `lemma` is skipped like `function` / `ghost` in the header, so `let lemma l1` is probed AND
  reported as `l1`. It used to be reported as "lemma". Its verdict is unchanged (it fails safe).

Preamble functions whose body `=` is indented 4 spaces (`    = match ...`, e.g. `hval_canon` /
`with function hlist_canon`) are still not probed. This was already true for their `let` first members
at base. The `^  =` body convention is unchanged and out of scope.

## 3. Route #620: one WhyML name per definition; ambiguous exempt names fail closed

`src/pycsl/pycsl.py::_run_pipeline`, at the fully resolved IR, just before the exempt set is computed.

(a) **Refusal `PYCSL-SEM-WHYML-NAME-CLASH`** (`PyCSLSemanticError`, stage `ir-semantic`). The IR
functions are grouped by `whyml_ident(IR name)`. Two distinct definitions in one group are refused. A
method `C.m` has the IR name `c__m`, so it meets a module `def c__m`. `F` / `f`, `py_range` / `range`
and similar pairs meet the same way. Two kinds of group are skipped:
- A group containing a route #122 `lifted_name_collision` is skipped. Module 6 refuses it with its own
  message, and keeping that message keeps the existing census rows valid.
- A **same-scope rebinding** is skipped: same IR name, same kind, same `self_type`. See the
  measurement just below.

**MEASURED BEFORE NARROWING** (broad rule = every group of 2+ distinct IR functions, lifted ones
excepted; head sweep `sw/head`, evidence `sw/broad/root-vs-v75.diff`):

| population | refused |
|---|---|
| corpus root (3325) | **2**: `7194_r463_ctl_unclaimed_def_rebound`, `7548_r476_ctl_two_defs_before_main` |
| pyref (2185) | 0 |
| mirror (53) | 0 |

Both refused files are `# pycsl-expected: PASS` controls of routes #463 / #476. In each, a module-level
`def` is bound twice. CPython keeps the last binding and so does the model. A `#@` claim on a dead
binding is already refused by route #463 (Module 3), and a class-body rebinding is refused by routes
#377 / #378 (probe c23). These are rebindings of ONE Python name, not two definitions, so I excluded
them. **Driver: this narrowing is my decision. Without it those 2 PASS controls are over-refused.
Please confirm it or overrule it.** After the narrowing: 0 corpus / 0 pyref / 0 mirror refusals except
the witness 10362.

(b) **Exemption fails closed.** `args._vacuity_exempt` no longer contains a WhyML name that two or more
IR functions map to. That covers rebindings and route #122 lifted collisions. This alone closes a
THIRD escape, found while checking the rebinding case:

- Probe c22 / witness 10364: a module-level `def f(x) -> NoReturn` is rebound by a live `def f` whose
  `requires` is contradictory and which claims `\result == 99`. The dead binding's annotation is not a
  `#@` claim, so route #463 admits it.
- The model keeps the live def. The exempt set held `f` from the dead binding, so the live def's probe
  was skipped. Result at base: **Verification SUCCESS** (CPython: 1).
- Head: FAILED, vacuous `f`.

## 4. Witnesses (corpus IDs 10360-10364, inside [10360, 10379])

| file | header | base | head |
|---|---|---|---|
| 10360_r619_mutrec_with_member_vacuous_false | FAIL | SUCCESS | FAILED (vacuous `f`) |
| 10361_r619_mutrec_with_member_ctl | PASS | SUCCESS | SUCCESS (both members probed) |
| 10362_r620_method_toplevel_whyml_name_clash_false | FAIL | SUCCESS | REFUSED `PYCSL-SEM-WHYML-NAME-CLASH` |
| 10363_r620_method_toplevel_distinct_names_ctl | PASS | SUCCESS | SUCCESS |
| 10364_r620_rebound_noreturn_def_exempts_live_vacuous_false | FAIL | SUCCESS | FAILED (vacuous `f`) |

Full proofs: `logs/FP.txt`, `logs/FP/{base,head}/*.log`. Command: `heavy.sh bash tools/FP.sh` →
`tools/p.sh`, with cwd = tree root, PYTHON_CPU_COUNT=2 and timeout 3600. oom_kill was 15 -> 15 on every
proof. Every head verdict equals the header. The FAIL witnesses print `VIOLATION contract` under CPython
and the controls print `result`.

Census row: the row for 10362 is the REAL `_census_row` output (cwd = tree root, relative path,
`tools/CR.py`), appended to `bin/refusal-witness-census.tsv`. The verify-fail witnesses (10360, 10364)
are not refusals and get no row, as in u64.

Rule 38: `ls ... | cut -c1-4 | sort | uniq -d` gains one line, `1036`. This is the 4-character cut of
10360-10364 against `1036_route40_ellipsis_truthiness.py`, the same artefact as u64's `1034`. With the
full numeric ID (`sed 's/_.*//'`) there is no new duplicate.

## 5. Probe census (type-only, `tools/census.sh`, emissions = v75 {mir-int, bd-int, bd-int/pyref})

The per-function probes of this tree's `_run_vacuity_gate` were checked with `why3 prove --type-only`
(`tools/pfcensus.py`). Result: **0 rejected among the 5430 emissions that type-check on their own**
(17393 probes). The 380 rejected probes all sit in the 133 emissions that already fail type-checking at
base. Per-file probe counts at base vs head use the real gate with a recorder (`tools/count.py`;
`census/count-{base,head}.tsv`):

| class | files | probes base | probes head | delta | files changed | files with fewer |
|---|---|---|---|---|---|---|
| mirror | 53 | 3541 | 4076 | **+535** | 29 | 0 |
| corpus root | 3325 | 11404 | 11493 | +89 | 33 | 0 |
| pyref | 2185 | 2204 | 2204 | 0 | 0 | 0 |
| total | 5563 | 17149 | 17773 | +624 | 62 | 0 |

No probe owner present at base is lost at head (multiset compare of the owner headers). New owners:
78 `with lemma` members (the mirror's `let rec lemma ... with lemma` groups), 35 `with function`, and
the remaining `with <mangled mirror helper>` members (e.g. `_collect_protect_index_sites__walkl`).
Biggest movers: Module5_IREmitter 224 -> 310, ir_scanner 208 -> 285, core_ir_semantic 285 -> 352,
pure_ast 208 -> 260.

**COST NOTE for the mirror campaign.** The mirror gains 535 probes (+15 %). By log 1282's measurement
(about 15 min per probe on statements.py with 1 worker), the vacuity phases of the big mirror files
grow accordingly. This is a tooling change (pycsl.py), so mirror proof carry-over is void under the
proof-map rule, as the driver anticipated in log 1284.

## 6. Gates

All gates ran on **f43343311**, the final src / bin / test-suite state; later commits only add the report
and logs. They ran as ONE NORMAL heavy job, `heavy.sh bash scratchpad/u65/tools/FINAL.sh`, whose output
is in `logs/FINAL.txt`. oom_kill was 15 at the start and 15 at the end (10:38Z -> 12:53Z).

| gate | result | log |
|---|---|---|
| byte-diff root: base b1400b11c (`pycsl-u65b`) vs head (`sw/head2`), cwd = each tree root, `tools/basesweep` = run9/bin/basesweep.sh | rc 0: 3325 / 3329 .mlw, 0 MOVED, 0 GONE, 0 APPEARED. 5 new sources: 10360 / 10361 / 10363 / 10364 emit, 10362 is refused (declared) | `logs/G/C-root.txt` |
| byte-diff pyref | rc 0: 2185 / 2185, 0 / 0 / 0 | `logs/G/C-pyref.txt` |
| mirror sweep (53 files) | compare rc 0, 53 / 53, 0 / 0 / 0; `diff -rq` **0 lines** (no mirror file moved) | `logs/G/C-mir.txt`, `logs/G/D-mir.txt` |
| check-self-annotate-sync.sh | rc 0 | `logs/G/lg/sync.txt` |
| self-annotate-mirror-check.sh | rc 0 | `logs/G/lg/mircheck.txt` |
| doc-coherency.py --check | rc 0 | `logs/G/lg/doccoh.txt` |
| run-soundness-planes.sh (fast, teed in full) | rc 0, **62 / 62** ok | `logs/G/planes.txt` |
| check-directive-enforcement | rc 0 (ratchet 53) | `logs/G/directive.txt` |
| check-stdlib-modules-verify | rc 0 (known 21 non-verifying) | `logs/G/stdlib.txt` |
| check-refusal-witness-coverage | rc 0: 517 sites, **488 demonstrated, 5 undemonstrated** (ceiling 5). The new `PYCSL-SEM-WHYML-NAME-CLASH` site is demonstrated by 10362: it is not in `--list-unwitnessed` | `logs/G/rwc.txt`, `logs/G/rwc-unwitnessed.txt` |
| check-corpus-executes | rc 0: 2608 / 2616 load (the 8 known), 1704 / 1704 self-checks | `logs/G/ce.txt` |
| check-assigns-writes-survival (head mirror emission, single-underscore dir) | rc 0 | `logs/G/lg/check-assigns-writes-survival.txt` |
| check-trusted-frame-honesty | rc 0 | `logs/G/lg/check-trusted-frame-honesty.txt` |
| check-getattr-erasure | rc 0 | `logs/G/lg/check-getattr-erasure.txt` |
| type-only probe census (head tooling, v75 emissions) | 0 rejected / 5430 type-checking emissions (17393 probes). The witness emissions add 7 probes, 0 rejected | `census/chunk.0?.log`, `logs/G/wit-census.log` |
| full proofs, base and head | every row of §1 and §4 as stated; oom 15 -> 15 | `logs/FP.txt` |
| `\trusted` count | 366 (unchanged) | `logs/FINAL.txt` ([LG] trusted 366) |
| ledger | 3: `proof_axiom_allowlist.py` not edited, no axiom added | -- |

Emission is unchanged for every file that emits at base: root, pyref and mirror are all 0 MOVED. The
only behaviour changes are (i) the vacuity gate's probe set, which is tooling, and (ii) refusal of a
distinct-definition WhyML name clash. This refusal fires on 0 corpus / pyref / mirror files besides
10362.

**Proof-map note.** `src/pycsl/pycsl.py` changed in `_run_vacuity_gate` and `_run_pipeline`, and
`bin/refusal-witness-census.tsv` gained one row. Both are tooling changes, so mirror whole-file proof
carry-over is void. The mirror gains 535 probes (§5).

## 7. Incidents

- One of my progress lines landed in the MAIN worktree's untracked `progress.txt`. Cause: a
  `cd X && nohup ... &` then `echo >> progress.txt` in the same shell command, so the `cd` ran only in
  the backgrounded subshell. I deleted exactly that line at once; nothing else in the main worktree
  was touched.
- A queued `CR.py` heavy job (timeout 900, waiting for a slot) was killed by me before it started
  (pid 890104, parent chain checked, it was mine). Its work moved into `tools/FINAL.sh`.

## 8. Commits

Branch `run9-u65`, not pushed:
- 6ac337907: WIP, route #619 scan + route #620 refusal / fail-closed exemption + witnesses 10360-10363
- bbf8b14bb: WIP, #620 narrowed (same-scope rebinding excluded, after the measurement), witness 10364, docs
  (static-semantics NR4 + vacuity gate; translational NR4)
- cbdff32e1: full-proof logs, base and head
- cb5096563: probe census + gate scripts
- f43343311: census row for 10362 (final src / bin / test-suite state; gates ran here)
- final: this report + gate logs

Sweep directories are not committed because of their size. They are at
`/home/fabrice/git/pycsl-u65/scratchpad/u65/sw/{base,head,head2}`: `head` is the broad-rule measurement
and `head2` is the final one. The base tree `/home/fabrice/git/pycsl-u65b` (detached at b1400b11c) is
kept for the driver's re-run.
