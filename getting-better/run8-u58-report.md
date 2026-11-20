# run #8 executor u58: route #613 round 3 (review rt69; refusal-only, import resolver)

Branch `run8-u58`, tree `/home/fabrice/git/pycsl-u58`, base `run8-int72` = fa1f72ca1. Brief
`scratchpad/run8/brief-u58.md`, plus the driver's added item (inherited mode environment variables).
Review: `scratchpad/rt69/FINDINGS.txt`. Logs: `/home/fabrice/git/pycsl-u58/scratchpad/u58/logs/`
(abbreviated `L/`). Tools: `/home/fabrice/git/pycsl-u58/scratchpad/u58/tools/`.

## 0. Status

- DONE. Gated on snapshot `pycsl-u58-g1` @ 74033e710 (`L/G1/`). The one red there,
  check-corpus-executes on the new control 10307, is fixed in 624b4ded3 and re-gated on
  `pycsl-u58-g2` (`L/G2/`).
- No new `\trusted` (grep 366, unchanged). Proof-axiom ledger 3 (`proof_axiom_allowlist.py`
  untouched). No gate loosened, no ratchet re-baselined. The one narrowing (item 3, G6) concerns
  ONLY names this round added, and was measured before it was made.
- Every edited live method has a `\trusted` mirror twin (`_resolve_module_path`,
  `resolve_imports`, `main`, `_build_soundness_report`): the mirror emission does not move
  (53 / 53, `diff -rq` 0 lines).
- oom_kill was 15 at the start and at the end of every job (M0, G1, G2, P1). No result is VOID.

## 1. `--as-package-module` WITHDRAWN (driver decision 1)

- `main()` (pycsl.py): `--as-package-module ROOT` and `--as-package-module=ROOT` exit rc 2 with
  "[!] Error: --as-package-module is not supported in this release (route #613: withdrawn after
  review rt69 ...)", before `_parse_args`, so nothing is verified.
- The code paths are REMOVED, not left unreachable: the g02 block in `_resolve_module_path`
  (PACKAGE-MODE-ORDER), the g08 parent-chain block in `resolve_imports` (PACKAGE-MODE-PARENT),
  `_pkg613`, the AS-PACKAGE-MODULE soundness-report entry, and its docs (annotations.md §7.16,
  concrete-syntax §11.3, static-semantics, translational §T.6.29). The two codes no longer exist.
- `check-stdlib-modules-verify` passes `--verification-image src` instead of
  `--as-package-module src`. Verdicts: see §5.
- Corpus: 10220 / 10222 keep the flag and are now rc 2 (FAIL, header note; census rows
  re-measured through `_census_row`, which classes an rc-2 run without a PIPELINE ERROR as
  VERIFY-FAIL). 10221 (a PASS control of the mode) drops the flag and is a script-mode control;
  its emission is byte-identical (no MOVED).
- rt69 probes, head (`L/q2/probes/`, `L/P1/q-pycsl-u58-g1/`): n01, n02, n03b, n05, n08, n10b,
  n13 (`__pycsl_r613_entry__.py`), o06, o07 all rc 2. Base int72: see `L/P1/q-pycsl-u58-base/`.

## 2. G3: no rule depends on a program file name

- The only basename test (`os.path.basename(main_file) != "__pycsl_r613_entry__.py"`) was in the
  removed g02 block. `grep` finds no other name test in src/pycsl.
- The closure check still places a notional entry path in a root (`_chk613`, the per-root judge);
  only its DIRECTORY is used (documented in the code).
- Probe (`L/envq/g3-entryname`): a SCRIPT literally named `__pycsl_r613_entry__.py` beside a local
  `re.py`, importing json, is REFUSED (TRANSITIVE-SHADOW), like any other name.

## 3. G5 / G6 / G7 (pre-existing gaps), refusal-only

All inline (no helper), in `src/pycsl/frontend/ir_resolve.py`.

**G7, `_resolve_module_path` (`PYCSL-SEM-IMPORT-CWD-ROOT`). Choice: REFUSE.** A module found FIRST
in pycsl's own cwd, when the cwd is not the program's directory (or its realpath), an
`--import-path` root or pycsl's `src/` / `Lib/` model roots, is refused, UNLESS it is a stdlib /
builtin name whose local copy passed #326 / #611 (an admitted byte-identical copy, the repo-root
`./json/`): then CPython loads the interpreter's own module, the same source file for file, so the
result is what CPython runs. Measured: 0 corpus / pyref / mirror files move (§4); the `./json/`
case is exactly that exception (control 10305; 10221 too).

**G5, `_resolve_module_path` (`PYCSL-SEM-IMPORT-NAMESPACE-PORTION-SHADOWED`).** A dotted import
whose TOP-LEVEL directory in the hit's root has no `__init__.py` (a namespace portion) is refused
when any other root CPython searches holds an entry of that top-level name (module, package,
directory or artifact): the program directory and its realpath, `--import-path`, the stdlib
directories, the site directories of the interpreter / its base installation / the user, and the
directories their `.pth` files add. Only the top level needs the look (below a regular package the
`__path__` is its own directory; a portion no other root holds is the whole namespace).

**G6, `resolve_imports` closure (`PYCSL-SEM-IMPORT-TRANSITIVE-SHADOW`).** The judged names also hold
every top-level module importable from the site directories (+ `.pth` dirs) and every top-level
name imported ANYWHERE by any `.py` there (the brief's simpler, more conservative variant;
literal `__import__` / `import_module` names too). Same per-entry judgement as stdlib names
(local module or package refused; bare directory refused unless a regular STDLIB module outranks
it; artifacts through #611). Cache `src/pycsl/__pycache__/r613-site-imports-<key40>.json`, key over
the stdlib key, the site-dir list, each dir's listing and every `.py`'s (relpath, size, mtime_ns),
re-walked each run; stale / foreign / malformed tables are rebuilt. The site graph also feeds the
refusal's chain (`program -> lark -> regex -> .../regex.py`). On this host: ~6500 site `.py`,
cold build 25-42 s once per interpreter / site change, warm `--no-proof` 1.41 s (u55: 1.37 s;
`L/G1/time.txt`).

**Narrowing (after measurement, §4), G6 names only.** A name ONLY third-party code brings in is not
judged in pycsl's cwd when the cwd is no CPython root (not the program dir / realpath / an
`--import-path` root) — G7's own premise. Every name judged before u58 is still judged in the cwd.

## 4. Over-refusal, measured BEFORE the narrowing (M0, snapshot `pycsl-u58-m0` @ 1d09b14a7)

`L/M0/summary.txt`, per-file verdicts `L/M0/sw/verdicts.tsv` (same command lines as the gate sweeps,
cwd = tree root), compared with int72's emission (`run8/v71`):

| tree | GONE vs int72 | cause |
|---|---|---|
| corpus root | 3299 / 3299 | G6: the repo root's bare `foobar/` dir (cwd; `foobar` is named in setuptools / pip / numpy sources) refused every program (5863 refusal messages name it) |
| pyref | 2185 / 2185 | same (2208 messages) |
| mirror | 53 / 53 | same |
| G7 / G5 | 0 in M0 | they fire before the closure check; their full measure is G1 below (they were not narrowed) |
| (1) | 10220 / 10221 / 10222 rc 2 | the withdrawn mode (10221 then got its flag dropped) |

After the narrowing (G1, @ 74033e710): corpus root 3299 baseline / 3302 candidate, 0 MOVED / 0 GONE
/ 0 APPEARED (the +3 are the new PASS controls 10305-10307); pyref 2185 / 2185, 0 / 0 / 0; mirror
53 / 53, 0 / 0 / 0. So G5, G7 and the narrowed G6 refuse NO previously emitting corpus, pyref or
mirror file, and the stdlib-modules plane keeps its verdicts (§5).

## 5. Gates

G1 (snapshot `pycsl-u58-g1` @ 74033e710, PRIO, `L/G1/summary.txt`):

- byte-diff root / pyref / mirror: §4 (rc 0 each; `C-root.txt`, `C-pyref.txt`, `D.txt`, `D-cmp.txt`).
- fidelity: sync rc 0, mirror-check rc 0; doc-coherency rc 0.
- fast planes: 61 / 62, the one red check-corpus-executes: `10307 ... No module named 'lark'`
  (the harness loads PASS drivers with /usr/bin/python3). Fixed in 624b4ded3 (10307 is
  `--no-proof`, an emission control, like the python-reference lark drivers); G2 below.
- refusal-witness-coverage rc 0: 483 demonstrated (PACKAGE-MODE-ORDER / -PARENT gone, CWD-ROOT /
  NAMESPACE-PORTION-SHADOWED added, witnessed by 10304 / 10302), ceilings unchanged.
- assigns-writes-survival rc 0; trusted-frame-honesty rc 0 (86 = ratchet); getattr-erasure rc 0
  (DECLARED 0, ABSENT 27, UNKNOWN 75).
- frontend-only 10/10 determinism rc 0; core-only 38 / 38 rc 0.
- count-trusted rc 0, grep 366. Ledger: `git diff fa1f72ca1 -- proof_axiom_allowlist.py` empty (3).
- stdlib-modules-verify (now `--verification-image src`): rc 0, 104 modules, 83 VERIFY, 21 do not
  (FAILS 3, REFUSED 17, TIMEOUT 1), "the non-verifying set is the known one (21)" = u55's 83 / 21
  (`L/G1/P-stdlib.log`).
- G2 (snapshot `pycsl-u58-g2` @ a9e77eff7; vs 74033e710 only the 10307 header / flag differs in
  src / bin / test-suite; `L/G2/summary.txt`): 10307 emission byte-identical to G1's (cmp rc 0);
  check-corpus-executes rc 0; fast planes **62 / 62 green**, rc 0; refusal-witness-coverage rc 0
  (483 demonstrated, 5 undemonstrated = ceiling, 10 unmatchable = ceiling); doc-coherency rc 0.
  (P1 proved 10307 in hoare at both trees before it became `--no-proof`.)
- `--slow` was not run (brief).

## 6. The driver's added item: an inherited mode variable never enables a mode

- `main()`: an inherited `PYCSL_VERIFICATION_IMAGE` is honoured only with
  `PYCSL_VERIFICATION_IMAGE_TOKEN` = the pid of a pycsl run that declared the flag: that pid must be
  this process or an ancestor (`/proc/<pid>/stat` chain) AND its own command line
  (`/proc/<pid>/cmdline`, the original argv) must carry `--verification-image`. Otherwise both
  variables are dropped (script mode) with a note. The flag sets both. The resolver re-checks the
  same token (a caller that skips `main`). An inherited `PYCSL_AS_PACKAGE_MODULE` is dropped with a
  note (no rc 2: the variable alone changes nothing).
- Evidence (`L/envq/`, quick, cwd = tree root), mirror file `module6_whyml/scc.py` (refused in
  script mode, emitted under the mode): plain REFUSED; env only REFUSED; env + token 1 (init)
  REFUSED; env + bogus token REFUSED; env + the calling shell's pid REFUSED; `--verification-image`
  emits. n09 with / without `PYCSL_AS_PACKAGE_MODULE`: the same refusal; 10188 with it: emits as
  without.
- The mirror sweep (which passes the flag) is byte-identical, so the hand-down is intact.

## 7. Witnesses (10300-10307; `multi_file_lib/r613y/`, repo-root `r613y_cwd_helperq.py`)

CPython (`L/cpython-witnesses.txt`, `tools/cpy-w.sh`: cwd = tree root, PYTHONPATH = the
--import-path root, script mode, both interpreters, -B, ulimit):

| id | shape | CPython | base int72 h / t / s | head h / t / s |
|---|---|---|---|---|
| 10300 FAIL | `--as-package-module test-suite/corpus` (rt69 n13 / rt66 g02 shape) | -m: root/r613x_g02.py, 2 | REFUSED x3 (PACKAGE-MODE-ORDER) | rc 2 x3 (withdrawn) |
| 10301 FAIL | `--as-package-module=test-suite/corpus` (n10b shape) | — | PROVED / VF / VF | rc 2 x3 |
| 10302 FAIL | G5 = n09: bare `lark/utils.py` in the --import-path root | venv: site-packages lark.utils, "result True" (system python3, no lark: local, False) | PROVED / VF / VF (claim `\result == False` FALSE) | REFUSED x3 NAMESPACE-PORTION-SHADOWED |
| 10303 FAIL | G6 = n23d: `import lark`, `regex.py` in the --import-path root | venv: "LOCAL regex.py loaded" x2, "result 7" | PROVED / VF / VF (claim `== 3` FALSE) | REFUSED x3 TRANSITIVE-SHADOW (`program -> lark -> regex`) |
| 10304 FAIL | G7 = n24: `r613y_cwd_helperq` in the cwd (tree root) and in --import-path | both: the --import-path copy, "result 2" | PROVED / VF / VF (claim `== 1` FALSE) | REFUSED x3 CWD-ROOT |
| 10305 PASS | cwd's admitted `./json/` | Lib/json, "result 1" | PROVED / VF / VF | identical |
| 10306 PASS | bare `multi_file_lib/` portion, unique name | the local file, "result 1" | PROVED / VF / VF | identical |
| 10307 PASS | `import lark`, no shadow | venv "result 3" | PROVED / VF / VF | identical |
| 10221 PASS | (flag dropped) script mode, json | — | PROVED / VF / VF (with the flag) | PROVED / VF / VF |

Typed / store VERIFY-FAIL is unrelated to the route: every json / import control fails the same
way at base (u52 §2). Logs: `L/P1/pr-pycsl-u58-base/`, `L/P1/pr-pycsl-u58-g1/`, summary
`L/P1/summary.txt` (oom_kill 15 at every start and end). The rt69 probes themselves (`L/P1/q-*`,
typecheck mode): at base n01 n02 n03b n05 n08 n09 n10b n13 n23 n23b n23c n23d n24 all EMIT; at head
every `--as-package-module` probe is rc 2, n09 REFUSED (G5), n23 / n23b / n23c / n23d REFUSED (G6,
chain `program -> lark -> regex`), n24 REFUSED (G7, cwd = n24/C); n06 / n07 script controls refused
as at base, o06 in script mode emits as at base. Census rows (via `_census_row`, `L/census-rows2.tsv`):
10302 / 10303 / 10304 REFUSAL; 10300 / 10301 / 10220 / 10222 VERIFY-FAIL (rc 2, no PIPELINE ERROR).

## 8. Residuals

- G7: pycsl's `src/` and `Lib/` model roots are not CPython roots either (the editable install's
  `.pth` on this host names a directory that does not exist); they are pycsl's model library
  roots by design and are exempt. PYTHONPATH holding the cwd (or `""`) at run time is the
  environment residual.
- G6: flow-insensitive over all site sources (dead branches, test trees: `foobar`, `mod`, `pkg1`).
  A local module named like any of ~370 installed / imported names beside a program is refused
  (none in the corpus). The table reflects pycsl's interpreter and its base installation's site
  dirs at verification time; another interpreter, a `.pth` added later, or a PYTHONPATH package's
  own imports remain residual. A `.pth`-added directory that contains pycsl's own `src/` would
  make the names `pycsl` / `pycsl_lib` judged (over-refusal; not the case here).
- G5 judges the top-level portion against the CPython roots pycsl can see; a PYTHONPATH entry
  not given as `--import-path` is residual.
- The token check reads `/proc` (Linux); without `/proc` an inherited value is always dropped
  (fail-closed to script mode).
- #612 (rt69, harmless today, NOT fixed here per the driver): d19 emits a `__call__` postcondition
  `self.n = old self.n` over a body that increments `self.n`; the VC fails, so nothing false
  proves, but the auto-frame is wrong.
- The u52 / u55 residuals (TOCTOU, writable install dir, program-chosen dynamic imports) stand.

## 9. Commits (branch run8-u58, not pushed)

- 1d09b14a7 WIP: withdrawal, G7, G5, G6 (pre-narrowing; the M0 measurement tree)
- 9d9c0e888 G6 narrowing; inherited-env token; witnesses 10300-10307; 10220-10222; docs
- ddebc59ce, 3b07a2e44 G5 / G7 messages relative to cwd (tree-independent census rows)
- 74033e710 census rows (the G1-gated tree)
- 624b4ded3 10307 `--no-proof`
- a9e77eff7 report draft + route613 section (the G2-gated tree)
- the final report commit (this file; docs only)

Snapshot trees left for the driver: `/home/fabrice/git/pycsl-u58-m0`, `-g1`, `-g2`, `-base`
(int72 + the witnesses copied in).

## 10. Exact commands

- M0: `HEAVY_PRIO=1 scratchpad/heavy/heavy.sh tools/M.sh 1d09b14a7 pycsl-u58-m0 L/M0`
- J1 (census -> commit -> G1 -> P1): `HEAVY_PRIO=1 scratchpad/heavy/heavy.sh tools/J1.sh`
  (`tools/G.sh`, `tools/P.sh`, `tools/census.sh`, `tools/wq.sh`, `tools/q.sh`)
- quick probes: `HEAVY_QUICK=1 scratchpad/heavy/heavy.sh tools/q2.sh <tree> L/q2`,
  `tools/envq.sh <tree> L/envq`
- PYTHON_CPU_COUNT=2 for every proof; cwd = the tree root except the n24 probe (cwd = n24/C).
