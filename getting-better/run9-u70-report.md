# run #9 u70 report -- routes #624 / #625 (review rt77 F1 / F2): one WhyML name per imported function

Branch `run9-u70` (worktree /home/fabrice/git/pycsl-u70), base `daa36070b` (ghost-assign-bc6). Not pushed.
Logs: `scratchpad/u70/logs/` (paths below are relative to the tree root).

## 0. Summary

- Both routes were PRE-EXISTING false proofs at base, and CPython contradicts them. Each is now REFUSED with
  `PYCSL-SEM-IMPORT-FUNCTION-NAME-CLASH`. The probe u03 (a direct import and a module-qualified import of two
  libraries' `helper`) was a third false proof at base and is now refused too.
- The only src change is in `src/pycsl/frontend/ir_resolve.py::_inject_functions` (+38 lines, inline, no helper).
  Its mirror twin is `\trusted`, and so are the twins of all three callers. `pycsl.py` is not touched.
  `resolve_imports`, `_resolve_module_path` and the #621 / #622 code are not touched.
- Over-refusal: root 0 MOVED / 0 GONE, pyref 0 / 0, mirror 0 / 0 (`diff -rq` empty). The GONE list is EMPTY.
  No expected-PASS corpus file is refused, and no mirror file is refused.
- No new `\trusted` (366), ledger 3, no gate or tool edited (bin/: 4 census rows).

## 1. Rule

Old behaviour: `_inject_functions` inserted a dependency stub only "if no function of that name is present yet".
When the name was already taken, the dependency function was silently SKIPPED. A module-qualified call
`m.f()` is rewritten to the bare `f`, so it then bound to whatever `f` was present: a local `def f`, or
another library's `f`.

New rule. Injecting a dependency function whose name the IR already holds is admitted (as a no-op) only when
the entry present IS that same dependency function. That means two things:
- the same origin file: the `_r143_dep_file` tag that `_process_dependency` sets on every dependency
  function (a program's own `def` has no tag);
- the same IR: dict equality. Both entries are shallow copies of the one cached entry, so this holds for the
  same function reached twice. It fails when an alias rename lands on a *different* function of the same file.

Anything else raises `PyCSLSemanticError(stage="imports", code="PYCSL-SEM-IMPORT-FUNCTION-NAME-CLASH")`. The
error names the function, the dependency's file, and either "a function the program defines itself" or the
other file. Its `filename` is the dependency's cwd-relative path.

Why refuse instead of keeping both under distinct names: binding each qualified call to its own definition
would mean renaming inside the resolvers' call rewrite (`_rewrite_ir_calls`) and every dependency-internal
call site. That is a larger change, and nothing here shows it is faithful, so the default (refusal) is kept.

Documented in: `docs/pycsl-static-semantics-reference.md` (the import-rule paragraph),
`docs/pycsl-translational-reference.md` (no-image list), and `test-suite/annotations.md` (§7.16 import entry).

## 2. Probes, head vs base, with CPython

Probes: `scratchpad/u70/probes/` (copies of rt77 w14 / w14b / w14c / w17 / w18 / w19 / w19c plus the libs, and
new u01-u07). Full proofs: `logs/P-b0/`, `logs/P-h1/` (both in `logs/chainB.txt`). --no-proof: `logs/q1.txt`.
CPython (system and venv python, `-B`, ulimit'd, cwd /tmp): `logs/cpython.txt`. oom_kill stayed 15 throughout.

| probe | shape | CPython | base daa36070b | head |
|---|---|---|---|---|
| w14 (F1) | `import rt77lib_val` + local `def val1`; claims `== 2` | 1 | SUCCESS (false proof) | REFUSED NAME-CLASH |
| w14b (F1b) | same via `import ... as L` | 1 | SUCCESS (false proof) | REFUSED NAME-CLASH |
| w14c (ctl) | qualified call, no clash, `== 1` | 1 | SUCCESS | SUCCESS |
| w17 (ctl) | `from lib import val1 as v1` + local val1, false `== 2` | 1 | FAILED | FAILED (unchanged) |
| w18 (ctl) | local `rt77lib_val__val1`, false `== 2` | 1 | FAILED | FAILED (unchanged) |
| w19 (F2) | `liba.helper() + libb.helper()`, false `== 2 or == 4` | 3 | SUCCESS (false proof) | REFUSED NAME-CLASH |
| w19c (F2c) | same, true `== 3` | 3 | FAILED | REFUSED NAME-CLASH |
| u01 (ctl) | same dependency function twice (`lib.val1()` + `from lib import val1`) | 2 | SUCCESS | SUCCESS |
| u02 (ctl) | `from liba import helper as ha` + `from libb import helper` | 3 | SUCCESS | SUCCESS |
| u03 | `liba.helper()` + `from libb import helper`, false `== 2 or == 4` | 3 | SUCCESS (false proof) | REFUSED NAME-CLASH |
| u04 | two star imports, `helper()` | 2 | REFUSED (existing star rule) | same |
| u05 | lib's `f` calls lib's `_h`, program defines `_h` | 1 | REFUSED (existing imported-contract rule) | REFUSED NAME-CLASH (fires earlier) |
| u06 | `from lib import val1` then local `def val1` | 2 | REFUSED (existing rebind rule) | same |
| u07 (ctl) | `A.helper() + A.helper()` | 2 | SUCCESS | SUCCESS |

The w14c / w17 / w18 controls are unchanged. w19c was not provable before, and now it is refused. This is the
expected price of the refusal; `from ... import helper as ...` is the admitted rewrite (u02 / 10426).

## 3. Over-refusal measure (BEFORE any narrowing; none was needed)

Sweeps (`scratchpad/u70/tools/S.sh`, cwd = tree root, plain heavy.sh NORMAL). Base: detached tree
`/home/fabrice/git/pycsl-u70-b0` at daa36070b. Head: snapshot `/home/fabrice/git/pycsl-u70-h1` at c40ecbb43.
The src / docs / test-suite of c40ecbb43 equal the final commit's, apart from 4 census rows in bin/.

| plane | result | log |
|---|---|---|
| root | 3325 baseline / 3331 candidate .mlw; 0 MOVED, 0 GONE, 0 APPEARED, 6 new sources (4 PASS controls + qa70 + qb70); rc 0 | `logs/G/C1-root.txt` |
| pyref | 2185 / 2185; 0 MOVED, 0 GONE; rc 0 | `logs/G/C1-pyref.txt` |
| mirror | 53 / 53; 0 MOVED, 0 GONE; rc 0; `diff -rq` 0 lines | `logs/G/C1-mir.txt`, `logs/G/D1-mir.txt` |

GONE list: EMPTY. Sweep logs: `logs/S-base.txt`, `logs/G/{base,h1}/{bd,mir}.log`.

## 4. Witnesses (corpus IDs 10420-10427 of [10420, 10434])

Helpers live in the program directory (the corpus root): `qa70.py` (`val1` -> 1, `helper` -> 1) and `qb70.py`
(`helper` -> 2). Both full-prove SUCCESS on base and head. CPython: `logs/cpython-witnesses.txt`.
Proofs: `logs/W-h1/`, `logs/W-b0/` (`logs/chainB.txt`).

| witness | header | CPython | base | head |
|---|---|---|---|---|
| 10420_r624_module_qualified_call_local_def_false | FAIL | result 1 | SUCCESS (false proof) | REFUSED NAME-CLASH |
| 10421_r624_alias_qualified_call_local_def_false | FAIL | result 1 | SUCCESS (false proof) | REFUSED NAME-CLASH |
| 10422_r625_two_libs_same_function_false | FAIL | result 3 | SUCCESS (false proof) | REFUSED NAME-CLASH |
| 10423_r625_qualified_and_from_import_two_libs_false | FAIL | result 3 | SUCCESS (false proof) | REFUSED NAME-CLASH |
| 10424_r624_qualified_call_no_clash_ctl | PASS | assert ok | SUCCESS | SUCCESS |
| 10425_r624_from_import_alias_beside_local_def_ctl (`from qa70 import val1 as v1`) | PASS | assert ok | SUCCESS | SUCCESS |
| 10426_r625_alias_two_libs_ctl | PASS | assert ok | SUCCESS | SUCCESS |
| 10427_r624_same_dependency_function_twice_ctl | PASS | assert ok | SUCCESS | SUCCESS |

Census rows: the real `_census_row` (`scratchpad/u70/tools/CR.sh`, cwd-relative paths) for 10420-10423 were
appended to `bin/refusal-witness-census.tsv` (`logs/CR-rows.tsv`, rc 0).

Rule 38: the 4-character cut gains `1042` / `1043`-style artefacts (10420-10427 vs `1042_route41_*`). This is
the same kind of cut artefact the driver accepted for u64 / u66. The cut was already non-empty at base
(the `NNNN.proofs/` directories). The helpers `qa70` / `qb70` are unique cuts.

## 5. Gates (final src; snapshot `/home/fabrice/git/pycsl-u70-h2` at 47aad7d7f; `tools/GATES.sh`, NORMAL)

Run: `GT=/home/fabrice/git/pycsl-u70-h2 heavy.sh bash scratchpad/u70/tools/GATES.sh scratchpad/u70/logs/GATES`.
Summary: `logs/GATES.txt`, rc 0, oom_kill 15 -> 15. The src / bin / docs / test-suite of h2 = the final commit.

| gate | result | log |
|---|---|---|
| byte-diff root / pyref / mirror | 0 MOVED, 0 GONE (none declared), mirror `diff -rq` 0 (section 3) | `logs/G/C1-*.txt`, `logs/G/D1-mir.txt` |
| check-self-annotate-sync | rc 0 (986 un-trusted mirror functions verbatim) | `logs/GATES/lg/sync.txt` |
| self-annotate-mirror-check | rc 0 (53 mirrors in sync) | `logs/GATES/lg/mircheck.txt` |
| doc-coherency --check | rc 0 | `logs/GATES/lg/doccoh.txt` |
| run-soundness-planes.sh (fast + conversion tier, full tee) | rc 0, 62 / 62 ok | `logs/GATES/planes.txt` |
| check-refusal-witness-coverage | rc 0: 488 demonstrated, 5 undemonstrated (ceiling 5), 10 unmatchable (ceiling 10). Both ceilings hold, so the new NAME-CLASH site is demonstrated by the 10420-10423 rows | `logs/GATES/rwc.txt` |
| check-corpus-executes | rc 0: 2612 / 2620 load (the 8 failures are the KNOWN ones), 1706 / 1706 self-checks | `logs/GATES/ce.txt` |
| frontend-only-conformance | rc 0: 38 OK / 0 MISMATCH | `logs/GATES/foc.txt` |
| check-dropped-mutation | rc 0: 0 dropped / 49 ctxbind (ratchet 51) / 5 tryfinal / 0 dangling | `logs/GATES/cdm.txt` |
| check-assigns-writes-survival / check-trusted-frame-honesty / check-getattr-erasure | rc 0 / 0 / 0 (emit dir `logs/GATES/lg/mir_emit`, 53 .mlw, single-underscore naming; full outputs kept) | `logs/GATES/lg/*.txt` |
| \trusted | 366 | `logs/GATES.txt` [LG] |
| proof-axiom ledger | 3 (`proof_axiom_allowlist.py` untouched; `git diff daa36070b HEAD -- src bin` = ir_resolve.py + 4 census rows) | -- |
| rt77 w-probes head vs base, with CPython | section 2 | `logs/P-b0/`, `logs/P-h1/`, `logs/cpython.txt` |

## 6. Commits (branch run9-u70, not pushed)

- c40ecbb43 WIP: rule, docs, witnesses 10420-10427, probes
- 5834f2860 WIP: base sweep logs, gate tools
- 47aad7d7f census rows 10420-10423; sweep compares; witness + probe proofs
- final: gate logs + this report

## 7. Open / for the driver

- `--deep` diamond (not measured by any corpus file): with `--deep`, a function that libc gives to both liba and
  libb is tagged once as liba's and once as libb's. Reaching it through both would now be refused, which is
  conservative. No corpus / pyref / mirror file hits this case (0 GONE).
- The refusal fires for any taken name, including a dependency's transitive in-file callee (u05). At base, u05
  was already refused by a different rule.
