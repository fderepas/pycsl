# run #8 executor u60: route #613 round 4 (review rt72; refusal-only, import resolver)

Branch `run8-u60`, tree `/home/fabrice/git/pycsl-u60`, base `run8-int73` = c31a5c7eb. Brief
`scratchpad/run8/brief-u60.md`. Review: `scratchpad/rt72/FINDINGS.txt` (probes copied to
`scratchpad/u60/probes/{a1,a1x,o}`). Logs: `/home/fabrice/git/pycsl-u60/scratchpad/u60/logs/`
(abbreviated `L/`). Tools: `/home/fabrice/git/pycsl-u60/scratchpad/u60/tools/`. Base snapshot
(int73 + the witnesses copied in, untracked): `/home/fabrice/git/pycsl-u60-base`. Gate snapshot:
`/home/fabrice/git/pycsl-u60-g1` (a5e94e022). Measurement snapshot: `/home/fabrice/git/pycsl-u60-m1b`
(0f0868f35).

## 0. Status

- A1 (PRE-EXISTING gap, false claim PROVED at base): CLOSED, refusal-only, in
  `src/pycsl/frontend/ir_resolve.py::resolve_imports` (inline, no helper; the mirror twin of
  `resolve_imports` is `\trusted` with `raises` declared, so the mirror emission does not move:
  53 / 53, `diff -rq` 0 lines). `_resolve_module_path` and `_run_pipeline` are NOT edited.
- O1 (over-refusal introduced by u58 G6): NOT narrowed. Measured: no sound narrowing exists on
  this host (section 3). Refused rather than approximated.
- Over-refusal of A1, measured before the witnesses existed (M1b): corpus root 3309 / 3309,
  pyref 2185 / 2185, mirror 53 / 53, byte-identical to int73 (0 MOVED / 0 GONE / 0 APPEARED).
- No new `\trusted` (grep 367, unchanged). Proof-axiom ledger 3 (`proof_axiom_allowlist.py`
  untouched, `git diff c31a5c7eb` empty). No gate loosened, no ratchet re-baselined.
- oom_kill 15 at the start and end of every job (M1b, G1, P1). No result is VOID.
- Two of my queued heavy jobs were cancelled before they took a slot: M1 on 33e603b22, superseded
  by the refined rule, and a stand-alone census job, folded into J1. I checked each one first: no
  output directory existed, its only child was heavy.sh's own `sleep 1`, and the parent chain led
  to my shell. No other process was touched.

## 1. A1: a dependency's absolute imports, `PYCSL-SEM-IMPORT-DEPENDENCY-SEARCH-ORDER`

**Defect (rt72).** pycsl believes a local dependency's contracts as they were verified with the
dependency as its own script, i.e. with the DEPENDENCY's directory as the first root. CPython
runs the program with `sys.path[0]` = the PROGRAM's (realpath) directory, then PYTHONPATH
(`--import-path`), so (no implicit relative import in Python 3) `lib/dep.py`'s
`from zqh72 import one` loads `P/zqh72.py`, not `lib/zqh72.py`. `--deep` does not help: it
resolves from the dependency's directory too.

**Rule** (top-level `resolve_imports` call only, inside the route #613 block, after the closure
check so every earlier refusal keeps its message; script mode only):

- Worklist from the program: every local module it reaches. That is each file an import
  resolves to (absolute or relative), plus the package `__init__.py` chain CPython runs before
  a dotted module, transitively. Every `Import` / `ImportFrom` anywhere in each file is taken
  (flow-insensitive). For `from m import n`, `m.n` is tried as a submodule too. pycsl's own
  stdlib model root `Lib/` is not followed: CPython runs the interpreter's stdlib there, and the
  closure check judges its imports.
- Each ABSOLUTE import of a reached module outside the program's directory is resolved twice
  with `_resolve_module_path`: from the module's own path (how its contracts were verified) and
  from the program's (how CPython loads it). Each outcome is a file, none, or refused(code).
- **REFUSED** when the module's own directory gives a FILE, or gives none for a stdlib / builtin
  name (pycsl's model), and the program's view differs: another file, none, or a refusal.
- **Admitted** when a non-stdlib name gives none (or a refusal) from the module's own directory.
  pycsl models such an import as an unconstrained external. Measured
  (`L/qun/`, `scratchpad/u60/probes/un/P/dep.mlw`): `from zz_nomod_u60 import one` lowers to
  `val one_0 () : int`, with no postcondition. So what that verification proved holds of
  whatever module CPython loads. This is the case of the package-qualified
  `from multi_file_lib.circ_b import func_b` inside `multi_file_lib/circ_a.py` (0065 / 0186 /
  0187), which the first, stricter draft would have refused. That draft never ran a sweep; the
  refinement came from reading the corpus before M1.
- Relative imports are package-relative in both views: they are followed, not compared.
- Under the DECLARED `--verification-image` the check is skipped (u58's token-checked mode).
  That mode makes no CPython-run claim, and the mirror's dependencies resolve to the LIVE
  `src/pycsl` on purpose (`--import-path src/pycsl`), so today's resolution is kept. The mirror
  sweep and `check-stdlib-modules-verify` declare the mode.

**Docs:** `test-suite/annotations.md` (the §7.16 import paragraph),
`docs/pycsl-static-semantics-reference.md`, `docs/pycsl-translational-reference.md` (§T.6
$\rho$ paragraph), the route613 file (section "u60 round 4"). doc-coherency rc 0.

**Evidence, rt72 probes (cwd = tree root):**

| probe | CPython (`L/cpython-witnesses.txt`, both interpreters) | base int73 (h / t / s) | head (h / t / s) |
|---|---|---|---|
| a1 `P/prog.py` | `P/zqh72.py loaded`, result 2 | PROVED / VF / VF | REFUSED x3 (A1) |
| a1 `P/lib/dep.py` (own script) | (its own script: lib/zqh72, faithful) | PROVED / VF / VF | PROVED / VF / VF (unchanged) |
| a1x `P/prog.py --import-path X` | `P/zqh72x.py loaded`, result 2 | PROVED / VF / VF | REFUSED x3 (A1) |
| a1x `X/depx.py` (own script) | — | PROVED / VF / VF | PROVED / VF / VF (unchanged) |
| a1s (same-root control, ex-10333) | result 1 | PROVED / VF / VF | PROVED / VF / VF (unchanged) |

Quick (emission) at head, `L/q3-head/`: a1 / a1x REFUSED, a1s and the dependencies' own runs emit.

h / t / s = hoare / typed / store full proofs, PYTHON_CPU_COUNT=2, cwd = tree root, `L/P1/summary.txt`,
logs `L/P1/pr-pycsl-u60-base/`, `L/P1/pr-pycsl-u60-g1/` (oom_kill 15 at every start and end). VF =
VERIFY-FAIL. Under typed / store every imported-stub program fails the same way at base and at head,
controls included, with Why3's "This function depends on external variables, it cannot be used as
pure" (`L/P1/pr-pycsl-u60-base/10332_*.proof-typed.log`): unrelated to the route (u52 / u58 note
the same). Typecheck-mode probe batch (`L/P1/q-base.txt`, `L/P1/q-g1.txt`): a1 / a1x emit at base
and are REFUSED at head; a1s and the dependencies emit at both; the o-probes are REFUSED at both
(TRANSITIVE-SHADOW: u58's G6 is in int73).

## 2. Witnesses (10330-10332; `multi_file_lib/r613z/`, corpus-root helpers `r613z_one.py`, `r613z_two.py`)

| id | shape | CPython | base int73 (h / t / s) | head (h / t / s) |
|---|---|---|---|---|
| 10330 FAIL | prog -> package `multi_file_lib.r613z.lib.dep` -> `from r613z_one import one`; lib/r613z_one.py `== 1`, ./r613z_one.py returns 2 | "PROGRAM-DIR r613z_one.py loaded", result 2 | PROVED / VF / VF (claim `== 1` FALSE) | REFUSED x3 (A1) |
| 10331 FAIL | a1x shape: `--import-path multi_file_lib/r613z/X`, X/r613z_depx.py -> `r613z_two`; X copy `== 1`, ./r613z_two.py returns 2 | (PYTHONPATH = X) "PROGRAM-DIR r613z_two.py loaded", result 2 | PROVED / VF / VF (claim `== 1` FALSE) | REFUSED x3 (A1) |
| 10332 PASS | package module `lib2/dep2.py` imports its sibling `from .r613z_one import one` while ./r613z_one.py exists | result 1 | PROVED / VF / VF | PROVED / VF / VF |

- A fourth control, 10333 (an `--import-path` module importing a module only that root holds),
  was moved OUT of the corpus to the probe `a1s`. `check-corpus-executes` loads every
  `multi_file_lib` helper from the corpus root, where the helper's bare sibling import cannot
  resolve, and the alternative was a new KNOWN_LOAD_FAILURES entry, i.e. widening a gate's
  allowlist. The commit message of a5e94e022 still says "10330-10333"; the committed files are
  10330-10332.
- Census rows through `_census_row` (`L/census-rows.tsv`, appended to
  `bin/refusal-witness-census.tsv` by J1): 10330 / 10331 REFUSAL with the A1 message.
- refusal-witness-coverage: 514 raise sites, 485 demonstrated, 5 undemonstrated = ceiling (so the
  new DEPENDENCY-SEARCH-ORDER site is demonstrated, by 10330 / 10331), 10 unmatchable = ceiling.

## 3. O1 (over-refusal introduced by u58's G6): NOT narrowed -- no sound narrowing exists on this host

The brief's rule: judge a site-package-only name only when the program's import closure (with the
stdlib table and the startup-hook closure) reaches a site-package module. Measured
(`L/O1/`, tools `tools/bridge.py`, `tools/o1data.py`, `tools/o1mod.py`, `tools/o1mod_nomain.py`;
real CPython 3.14.4 sources, the venv's site dir and the base installation's dist-packages):

1. **The closure always contains the builtins** (route #613's founding rule, u52): their C code
   imports modules no source shows, so every stdlib module is a possible member. The
   interpreter binary cannot bound that set below "all stdlib" soundly (a fixed-name C import
   would be a string literal, but the binary already carries `unittest`, `doctest`, `pdb`,
   `ensurepip`, `concurrent` as strings: `L/O1/binary-strings.txt`, and a string scan is
   evidence, not a proof).
2. **From the stdlib table, site code is always reached.** Top-level table (the one pycsl
   caches): from ALL stdlib names it reaches the site modules `pip` (`ensurepip`),
   `setuptools` (`test`) and `apport_python_hook` (the stdlib-directory `sitecustomize`),
   `L/O1/bridge.txt`; even from the single seed `json` the forward closure has 258 stdlib
   tops including `test` -> `setuptools` (`L/O1/o1data.txt`). A finer MODULE-level graph
   (`o1mod.py`) still reaches it: `setuptools <- test.support <- multiprocessing.util <-
   multiprocessing.connection <- concurrent.futures.process <- concurrent.futures <-
   asyncio.base_events <- asyncio <- pdb <- doctest <- heapq` (heapq's `__main__` block)
   from a 23-module core seed (`L/O1/o1mod-coreseed.txt`); pruning every non-program
   `if __name__ == "__main__":` / `TYPE_CHECKING` block (sound: an imported module is never
   `__main__`) removes that chain for the core seed (`o1mod-nomain-coreseed.txt`: no site
   module) but NOT for the conservative all-stdlib seed of point 1 (`pip <- ensurepip`,
   `setuptools <- test.support <- multiprocessing.util`, `o1mod-nomain-allstdlib.txt`) and not
   for a program that imports `unittest` (`-> asyncio -> concurrent.futures ->
   multiprocessing.util -> test.support -> setuptools`).
3. **Reached site code loads ANY installed distribution.** `setuptools.dist` /
   `pkg_resources` load entry points (`importlib.metadata` -> `import_module(<metadata
   name>)`), and 12 of the reached site tops make computed `__import__` / `import_module`
   calls (`pip`, `setuptools`, `pkg_resources`, `numpy`, `jinja2`, ...; `L/O1/o1data.txt`).
   Once one of them is reachable, every installed top-level module, and every name its
   sources import, is a module the run may load -- exactly u58's set.

So the rule the brief describes is a no-op on this host (it would judge the full u58 set for
every program), and a narrowing that DOES drop names (`validate`, `checks`, `testing`, `path`,
`parent`, ...) needs an unprovable premise: a bounded set of C-level imports (point 1) and no
computed import in reached site code (point 3). Refusing rather than approximating, I made no
O1 change; the rt72 o-probes stay REFUSED at head exactly as at base (`L/P1/q-base.txt`,
`L/P1/q-g1.txt`).
What a sound narrowing would need (not done): a module-level stdlib + site table with the
`__main__` pruning, PLUS a proof that the interpreter's C-level imports are a fixed, listed
set (e.g. an audit of CPython's `PyImport_Import*` call sites for this exact build), PLUS
treating any computed import in a reached site module as "everything".

## 4. Gates (snapshot `pycsl-u60-g1` @ a5e94e022, PRIO, `L/G1/summary.txt`; baselines `run8/v72`)

- byte-diff root vs `v72/bd-int` (comparator once): rc 0, 3309 baseline / 3312 candidate, 0
  MOVED / 0 GONE / 0 APPEARED, 3 new source files ignored. Those are the new `.mlw` of 10332,
  `r613z_one`, `r613z_two`; 10330 / 10331 are refused (`L/G1/C-root.txt`).
- byte-diff pyref vs `v72/bd-int/pyref`: rc 0, 2185 / 2185, 0 / 0 / 0 (`L/G1/C-pyref.txt`).
- mirror vs `v72/mir-int`: 53 emitted, `diff -rq` 0 lines, compare rc 0, 53 / 53, 0 / 0 / 0
  (`L/G1/D.txt`, `D-cmp.txt`).
- fidelity: check-self-annotate-sync rc 0, self-annotate-mirror-check rc 0, doc-coherency rc 0.
- fast planes (teed, `L/G1/F-planes.log`): rc 0, "all 62 plane(s) green (fast + the CONVERSION
  TIER)". `--slow` was NOT run (brief).
- check-refusal-witness-coverage rc 0 (above); check-corpus-executes rc 0 (`L/G1/P-ce.log`).
- ledger slow planes, individually, emit dir `L/G1/emit_mir`: check-assigns-writes-survival
  rc 0; check-trusted-frame-honesty rc 0 (86 = ratchet); check-getattr-erasure rc 0 (DECLARED 0,
  ABSENT 27, UNKNOWN 75).
- frontend-only 10 / 10 determinism rc 0; core-only 38 / 38 rc 0.
- count-trusted rc 0, `grep '#@ \trusted' src/self-annotate/src` = 367 (unchanged). Ledger 3.
- check-stdlib-modules-verify (`--verification-image src`, A1 skipped by design): rc 0, 104
  modules, 83 VERIFY, 21 do not (FAILS 3, REFUSED 17, TIMEOUT 1), "the non-verifying set is the
  known one (21)" = u58's 83 / 21 (`L/G1/P-stdlib.log`).
- warm `--no-proof` of 10188: 1.50 s / 1.47 s at M1b (u58: 1.41 s); 1.74 s at G1 under a loaded
  machine (`L/M1b/time.txt`, `L/G1/time.txt`). The A1 walk parses the reached local modules once.

## 5. Residuals

- A1 compares pycsl's two resolutions. pycsl's model roots (`src/`, `Lib/`, the cwd) sit in both
  views between the program's directory and `--import-path`, unlike CPython (u58's G7 residual).
  A dependency's import named only through a computed name (`importlib.import_module(x)`) is not
  followed (the route #326 STATE-MANIPULATED rule refuses the machinery beside a local import in
  the PROGRAM, and in a dependency's top level).
- A1 follows every import statement, function bodies included (flow-insensitive). An import a
  dependency never executes can therefore refuse the program. This is fail-closed and measured
  at 0 over-refusal.
- O1: u58's over-refusal stands as documented (a local module named like one of ~370 installed /
  imported names is refused).
- The u52 / u55 / u58 residuals (TOCTOU, writable install dir, PYTHONPATH and interpreter
  environment, program-chosen dynamic imports, `/proc` token) stand.

## 6. Commits (branch run8-u60, not pushed)

- 33e603b22 WIP: A1 first draft (pre-measurement; never swept)
- 445111201 A1 refined (dependency-side file / stdlib-model only); docs
- 0f0868f35 A1 message wording (the M1b measurement tree)
- a5e94e022 witnesses 10330-10332 + census rows (the G1-gated tree)
- the final report commit (this file + the route613 section; docs only)

## 7. Exact commands

- M1b: `HEAVY_PRIO=1 scratchpad/heavy/heavy.sh scratchpad/u60/tools/M.sh 0f0868f35 pycsl-u60-m1b L/M1b`
  (`tools/msweep.sh`: the byte-diff-sweep and mirror-emit-sweep command lines plus a per-file
  verdict TSV, cwd = tree root).
- J1 (census -> commit -> G1 -> P1 -> tc probes): `HEAVY_PRIO=1 scratchpad/heavy/heavy.sh
  scratchpad/u60/tools/J1.sh` (`tools/census.py`, `tools/G.sh`, `tools/P.sh`, `tools/wq.sh`,
  `tools/q.sh`).
- Quick probes: `HEAVY_QUICK=1 scratchpad/heavy/heavy.sh scratchpad/u60/tools/q.sh <tree> <out> [tc]`;
  CPython: `tools/cpy-w.sh <tree>` (cwd = tree root, `-B`, ulimit, both interpreters).
- O1 data: `timeout 300 bash -c 'ulimit -v 3000000; .venv/bin/python3 -I scratchpad/u60/tools/<o1 tool>.py [seeds]'`
  (reads only the stdlib and site directories; no pycsl import).
- PYTHON_CPU_COUNT=2 for every proof; cwd = the tree root.
