# run #9 executor u73: routes #631 (module object via class base / annotation / loader; module-level hooks), #632 (wildcard `__all__` invisible to the walk), #633 (string-resolved monkeypatch)

Branch `run9-u73` (tree `/home/fabrice/git/pycsl-u73`), made from `run9-u71` (9942c1199) with `ghost-assign-bc6`
merged in (e2acf55ce) before any change, and merged again after L21 landed (e0e1dad26, `ghost-assign-bc6` =
b959bb1b2). Both census conflicts were resolved as the exact union of rows. Brief: `scratchpad/run9/brief-u73.md`.
Logs: `scratchpad/u73/logs/` (`L/` below), tools: `scratchpad/u73/tools/`, probes: `scratchpad/u73/probes/` (copies of
the u71 probe set, i.e. rt76 / rt78 / rt79 / u64 / u66 / u69 / u71, plus rt81's 45 probes under `rt81/` and 14 new
ones under `u73/`). Sweep `.mlw` files are git-ignored (on disk under `L/G/`). oom_kill was 15 at the start and end of
every heavy job and on every probe line: no result VOID. Every job after 2026-11-23T22:35Z ran with
`TMPDIR=scratchpad/u73/tmp` (the /tmp user quota incident); no output of mine contains EDQUOT / "No space left".

Trees (main .venv symlinked; kept for re-proof):
- `b0` = /home/fabrice/git/pycsl-u73-b0, detached at c115e0a5a (L19).
- `bh` = /home/fabrice/git/pycsl-u73-bh, detached at 08e65645c (the V2D batch head rt81 reviewed).
- `b1` = /home/fabrice/git/pycsl-u73-b1, detached at e2acf55ce (my base, = u71 + bc6; the over-refusal measure base).
- `h1` = /home/fabrice/git/pycsl-u73-h1, detached at 392273698 (all src changes, docs, witnesses; the MEASURE).
- `b2` = /home/fabrice/git/pycsl-u73-b2, detached at b959bb1b2 (main after L21; the final gate base).
- `h2` = /home/fabrice/git/pycsl-u73-h2, detached at 1b2c1f078 (final src = h1 src + L21; the final gate head).

## 0. Status

- **#631** (p2 / p2b / p8, PRE-EXISTING false proofs) CLOSED: REFUSED at head (new site
  `PYCSL-SEM-IMPORT-MODULE-HOOK`). Latent p1b / p6b / p7 (annotation / loader escapes; fail-safe by a WhyML type error
  at L19 and bh) are now REFUSED at the import stage (rule E site). New u73 variants: m2 (`__getattr__` answering
  `__mro_entries__`, false proof at L19 / bh) REFUSED; a1 (`typing.get_type_hints` of a string annotation) and l1
  (`__spec__.loader.load_module`) REFUSED (type-check failure at L19 / bh).
- **#632** (x3 / x9 / x4 / x1b, PRE-EXISTING false proofs) CLOSED: REFUSED (WILDCARD-ALL-UNKNOWN). New variants q1
  (program wildcard of a `__getattr__` package, false proof) and q4 (plain `from pkg import __all__` then `.append`,
  false proof) REFUSED. The #483 closure carries the same rules (checked with `--verification-image`, where the walk is
  off: x3 / x4 / x1b / q4 / q1 REFUSED, c2 SUCCESS; `L/dev4.txt`).
- **#633** (p4 / p4b, PRE-EXISTING false proofs) CLOSED: REFUSED by route #326 (`PYCSL-SEM-IMPORT-STATE-MANIPULATED`).
  New variants k1 (`from unittest.mock import patch`) and k2 (`mock.patch.object`) REFUSED (both false proofs at L19 /
  bh).
- **Over-refusal measured BEFORE any narrowing (h1 vs b1): root / pyref / mirror 0 MOVED / 0 GONE / 0 APPEARED.
  GONE list EMPTY.** No narrowing was needed. Final gate sweeps (h2 vs b2): see section 5.
- Probe-level fail-closed costs (no corpus file): q2 (`__dir__` only; CPython ignores it for `import *`, claim true) and
  o1 (a lazy-loader `__getattr__` that only raises; claim true) were SUCCESS at L19 / bh and are REFUSED; rt79 g3 / g4 /
  g5 move FAIL -> REFUSED (no SUCCESS lost).
- src changes: `src/pycsl/frontend/ir_resolve.py` (only inside `resolve_imports`: route #326's list and the u60 / #621
  walk; `_inject_functions` and the class resolvers untouched) and `src/pycsl/pycsl.py` (only inside `_run_pipeline`'s
  #483 closure; nothing between `_BODY_EQ_RE` and `def main`). Both mirror twins are `\trusted` (checked). No helper
  extracted, no new `\trusted`, no axiom (ledger 3), no gate edited (bin/ change = census rows).

## 1. Rules (all inline)

**#631 escapes (walk, rule E').** These now count as a module-object ESCAPE, so every store receiver is judged:
- an import-rooted chain used as a CLASS BASE (it was an exempt position; PEP 560 passes a non-type base, itself, to its
  `__mro_entries__(bases)`);
- an import-bound name in a parameter / return / module-level / class-level annotation. Only a FUNCTION-LOCAL variable
  annotation stays exempt: CPython never evaluates it (measured with both interpreters, `L/` dev note: `x: undefined = 1`
  in a function runs; a class-level one raises NameError on `__annotations__`);
- the attributes `__loader__`, `__spec__`, `load_module`, `exec_module`, `module_from_spec`, `__annotations__`,
  `__annotate__`, `get_type_hints`, `get_annotations`, `evaluate_forward_ref`; the names `__loader__`, `__spec__`,
  `__annotations__`, `__annotate__`; an import of `annotationlib`; a from-import of `get_type_hints` /
  `get_annotations` / `evaluate_forward_ref` / `ForwardRef` / `call_annotate_function`.

**#631 hook refusal (walk, new site `PYCSL-SEM-IMPORT-MODULE-HOOK`).** A module-level `__mro_entries__` or
`__getattr__` binding in any reached module other than the program REFUSES. In the program (whose module object is
`__main__`) it refuses once a module can be a class base (an import-rooted base) or any escape exists. Detection is
fail-closed: a def of the name outside class bodies, a Store / Del of the name, an import alias naming or binding it, a
`global` / `nonlocal` of it, an attribute store / delete of it, or the literal string. Why unconditional outside the
program: a module-level `__getattr__` answers EVERY attribute the module does not bind (`from pkg import b` takes
`__getattr__("b")` before the submodule b.py that pycsl resolves, probe g1 / witness 10471), and `__mro_entries__`
runs for `class C(pkg)`.

**#632 (walk and #483 closure).** A wildcard of a package whose `__init__` has a module-level `__getattr__` / `__dir__` /
`__mro_entries__` hook (same detection) makes its `__all__` unknown (walk: WILDCARD-ALL-UNKNOWN; closure: route #483's
wildcard message). Any import alias naming or binding `__all__` (`from pkg import __all__ as A`, `from . import
__all__`, `... as __all__`) in a reached module now counts as an outside mention (walk). The #483 closure gets the whole
outside-mention rule (attribute `.__all__`, literal "__all__", `__all__` alias in any closure module once a wildcard of a
package is met), which it lacked; it matters where the walk is off (`--verification-image`).

**#633 (route #326).** The dynamic-import list (`importlib`, `imp`, `zipimport`, `pkgutil`, `runpy`) gains `unittest`
(any `unittest*` import: `mock.patch("pkg.b", K)` imports `pkg` by its dotted string and sets its attribute), `mock`
(the backport), `pydoc` (`locate`), `logging.config` (`import logging.config`, `from logging.config import ...`, `from
logging import config`: dotted-name resolution in configs), and `pickle` / `_pickle` / `shelve` (unpickling imports and
calls by name). As before it refuses only when the program also has an import resolved to a local file. pickle /
_pickle / shelve / pydoc / logging.config are fail-closed additions WITHOUT probes (rule 37: no payload-like inputs).
Measured cost: 0 GONE.

Docs: u73 text added next to u71's in `test-suite/annotations.md`, `docs/pycsl-static-semantics-reference.md`,
`docs/pycsl-translational-reference.md`.

## 2. Probes (cwd = tree root unless the probe has a `cwd` file; b0 = L19, bh = 08e65645c, head = h1)

Method: `--no-proof` on every probe and witness on the three trees (`tools/Q.sh`, QUICK, `L/Q-{h1,bh,b0}.txt`), then a
full proof (hoare, PYTHON_CPU_COUNT=2, timeout 3600) of every probe whose `--no-proof` run reached "Verification
SUCCESS" on that tree, and of every u73 witness / helper (`tools/J.sh`, inside `tools/chain1.sh`, `L/chain1.txt`, logs
`L/J-{h1,bh,b0}/`). A `--no-proof` refusal / type-check failure is final and is reported as such. CPython: both
interpreters, -B, ulimit -v 2000000 (`L/cpy-rt81.txt`, `L/cpy-u73.txt`, u71's `scratchpad/u71/logs/cpython-all.txt`); the
two interpreters agree everywhere. Full table (193 rows): `L/Ptab.txt` (probe | CPython | b0 | bh | head).

Every probe whose verdict differs between bh and head:

| probe | CPython | b0 (L19) | bh (08e65645c) | head |
|---|---|---|---|---|
| rt81 p2 / p2b / p8 (#631) | 2 | **SUCCESS (false)** | **SUCCESS (false)** | REFUSED (MODULE-HOOK) |
| u73 m2 (`__getattr__` answers `__mro_entries__`) | 2 | **SUCCESS (false)** | **SUCCESS (false)** | REFUSED (MODULE-HOOK) |
| rt81 p1b / p6b / p7, p5 | 2 | TC-FAIL | TC-FAIL | REFUSED (rule E / escape) |
| u73 a1 (`get_type_hints` string annotation) / l1 (`__spec__.loader`) | 2 | TC-FAIL | TC-FAIL | REFUSED (rule E) |
| u73 g1 (`__getattr__` answers a from-import target) | 2 | FAIL | FAIL | REFUSED (MODULE-HOOK) |
| rt81 x3 / x9 / x4 / x1b (#632) | 5 | **SUCCESS (false)** | **SUCCESS (false)** | REFUSED (WILDCARD-ALL-UNKNOWN) |
| u73 q1 (program wildcard, `__getattr__` `__all__`) | 3 | **SUCCESS (false)** | **SUCCESS (false)** | REFUSED (WILDCARD-ALL-UNKNOWN) |
| u73 q4 (`from pkg import __all__` + append) | 5 | **SUCCESS (false)** | **SUCCESS (false)** | REFUSED (WILDCARD-ALL-UNKNOWN) |
| rt81 p4 / p4b, u73 k1 / k2 (#633) | 2 | **SUCCESS (false)** | **SUCCESS (false)** | REFUSED (STATE-MANIPULATED) |
| u73 q2 (`__dir__` only) | 2 (= claim) | SUCCESS | SUCCESS | REFUSED (fail-closed cost, as the brief asks) |
| u73 o1 (lazy `__getattr__` that only raises) | 1 (= claim) | SUCCESS | SUCCESS | REFUSED (fail-closed cost) |
| rt79 g3 / g4 / g5 (package `__getattr__`) | 2 / 2 / 5 | FAIL | FAIL | REFUSED (MODULE-HOOK) |

Unchanged bh = head (and b0 where noted in `L/Ptab.txt`): the PASS controls u73 c1 (`class C(pkg.Base)`), c1f (`from pkg
import Base`), c2 (benign wildcard) SUCCESS on all three trees; u73 m1 REFUSED everywhere (older rebound-name rule);
every other rt76 / rt78 / rt79 / u64 / u66 / u69 / u71 / rt81 probe (rt81 a1-a13, p1, p3, p3b, x1, x2, x7, z*; rt79
r1 SUCCESS (CPython 4), d8, w2, z1, n1-n6, y2-y6 ...). **No head SUCCESS that CPython contradicts; no head SUCCESS where
bh refused.** (The rt76 and rt79 lists both contain a probe named `r1`; `L/Ptab.txt` shows both rows.)

## 3. Over-refusal (cwd = tree root)

| sweep | h1 (MEASURE, vs b1 = e2acf55ce) | h2 (final, vs b2 = main b959bb1b2) | logs |
|---|---|---|---|
| root | rc 0, 3343 / 3348: 0 MOVED / 0 GONE / 0 APPEARED, 5 new sources | rc 0, 3343 / 3348: 0 / 0 / 0, 5 new sources | `L/G/C-h1-root.txt`, `L/G/C-h2-root.txt` |
| pyref | rc 0, 2185 / 2185: 0 / 0 / 0 | rc 0, 2185 / 2185: 0 / 0 / 0 | `L/G/C-h{1,2}-pyref.txt` |
| mirror (53) | rc 0: 0 / 0 / 0, diff -rq 0 lines | rc 0: 0 / 0 / 0, diff -rq 0 lines | `L/G/C-h{1,2}-mir.txt`, `L/G/D-h{1,2}-mir.txt` |

**GONE list: EMPTY** (h1). New sources: 10475, 10476 and the helpers zu73h / zu73i / zu73q that emit. Sweep logs:
`L/S-base.txt`, `L/chain1.txt`, `L/chain2.txt`.

## 4. Witnesses (IDs 10470-10476 inside [10470, 10489]; CPython from the tree root)

| witness | CPython | b0 | bh | head | header |
|---|---|---|---|---|---|
| 10470_r631_module_mro_entries_class_base_rebinds_submodule_false (p2 shape) | 2 | SUCCESS (false) | SUCCESS (false) | REFUSED (MODULE-HOOK, new site) | FAIL |
| 10471_r631_module_getattr_answers_submodule_from_import_false (g1 shape) | 2 | FAIL | FAIL | REFUSED (MODULE-HOOK) | FAIL |
| 10472_r632_dependency_wildcard_all_from_module_getattr_false (x3 shape) | 5 | SUCCESS (false) | SUCCESS (false) | REFUSED (WILDCARD-ALL-UNKNOWN) | FAIL |
| 10473_r632_dependency_wildcard_all_extended_through_import_alias_false (x4 shape) | 5 | SUCCESS (false) | SUCCESS (false) | REFUSED (WILDCARD-ALL-UNKNOWN) | FAIL |
| 10474_r633_mock_patch_string_rebinds_submodule_false (p4 shape) | 2 | SUCCESS (false) | SUCCESS (false) | REFUSED (STATE-MANIPULATED) | FAIL |
| 10475_r631o_class_with_imported_base_class_ctl | 1 | SUCCESS | SUCCESS | SUCCESS | PASS |
| 10476_r632o_program_wildcard_literal_all_no_getattr_ctl | 1 | SUCCESS | SUCCESS | SUCCESS | PASS |

Helpers (corpus dir): `zu73a/`, `zu73c/`, `zu73d.py`, `zu73e/`, `zu73h.py`, `zu73i.py`, `zu73j.py`, `zu73k/`, `zu73m/`,
`zu73n/`, `zu73o/`, `zu73q.py`. Their own runs: zu73d / zu73j REFUSED at head (correct: their own run executes the
wildcard); zu73k/* and zu73e/w, zu73k/w REFUSED on every tree (pre-existing rules: imports of the claimed file, rebound
names); zu73a/`__init__` and zu73e/`__init__` TC-FAIL on every tree; the rest SUCCESS on every tree. Census: real
`_census_row` (`tools/CR.sh`) for 10470-10474 appended (`L/CR-rows.tsv`). Rule 38: full IDs unique; the 4-character cut
gains the `1047` prefix duplicate (an existing `1047_route39...`), the same artefact u69 / u71 recorded.

## 5. Gates (final src = h2 1b2c1f078 + census rows; `tools/chain2.sh` -> `tools/GATES.sh`, cwd = u73 tree)

First gate run (`L/GATES/`, on 1b2c1f078 + the 5 census rows; one NORMAL job, oom_kill 15 -> 15):

| gate | result | log |
|---|---|---|
| byte-diff root / pyref vs main b959bb1b2 | rc 0 / rc 0, 0 MOVED, 0 GONE, 0 APPEARED (5 new sources) | `L/G/C-h2-root.txt`, `L/G/C-h2-pyref.txt` |
| mirror sweep 53 + diff -rq | rc 0, 0 lines (no mirror emission moves: no re-proof owed) | `L/G/C-h2-mir.txt`, `L/G/D-h2-mir.txt` |
| check-self-annotate-sync / self-annotate-mirror-check / doc-coherency --check (fidelity) | rc 0 / 0 / 0 | `L/GATES/lg/{sync,mircheck,doccoh}.txt` |
| run-soundness-planes.sh (fast, full tee) | **rc 1: 61 / 62, RED check-vacuous-drivers** (pycsl-reference EMPTY placeholders 17 > ratchet 8: my 9 helpers `one()` / `three()` were `ensures \result == <lit>` over `return <lit>`) | `L/GATES/planes.txt` |
| check-refusal-witness-coverage | rc 0: 494 demonstrated, 5 undemonstrated (ceiling 5); the new site MODULE-HOOK is demonstrated by 10470 / 10471 | `L/GATES/rwc.txt` |
| check-corpus-executes | rc 0 (only the known load failures) | `L/GATES/ce.txt` |
| frontend-only-conformance | rc 0 | `L/GATES/foc.txt` |
| check-dropped-mutation | rc 0: 0 / 49 / 5 / 0 | `L/GATES/cdm.txt` |
| check-assigns-writes-survival / check-trusted-frame-honesty / check-getattr-erasure | rc 0 / 0 / 0 (emit dir `L/GATES/lg/mir_emit`, 53) | `L/GATES/lg/*.txt` |
| \trusted | 365 (= main after L21; unchanged by u73) | `L/chain2.txt` [LG] |
| ledger | 3 (no allowlist / axiom change) | -- |

FIX for the red plane (0d07f75d3): the 9 helpers now carry `#@ assigns \nothing` as well (a true, stronger contract,
the u71 helper shape), which takes them out of the vacuous-driver population; no ratchet was touched. Re-gate after the
fix: `tools/gates3.sh` (vacuous-drivers alone, witnesses + helpers full proofs, census-row re-check, fast planes,
rwc, corpus-executes), log `L/gates3.txt`, `L/GATES3/`:

GATES3 on 875fc4f6c (= 0d07f75d3 src / corpus / census; one NORMAL job 15:53-16:36Z, oom_kill 15 -> 15):
check-vacuous-drivers rc 0 (pycsl-reference trivial 9 = ratchet 9, empty back at the ratchet); all u73 witnesses and
helpers re-proved with unchanged verdicts (`L/GATES3/w/`); the re-generated census rows are byte-identical to the
committed ones; **run-soundness-planes.sh rc 0: all 62 planes green** (`L/GATES3/planes.txt`); check-refusal-witness-
coverage rc 0 (494 demonstrated, 5 undemonstrated, ceiling 5); check-corpus-executes rc 0. The fidelity and ledger
planes and the sweeps above are unaffected by the helper edit (no src / mirror change; the helpers are new sources the
compare ignores) and are not re-run.

## 6. Commits (branch run9-u73, not pushed)

- e2acf55ce merge ghost-assign-bc6 (setup; census union).
- 392273698 WIP h1: all src changes, docs, witnesses 10470-10476 + helpers, probes, tools.
- d2edb07fa, 829ab81b4 WIP: dev logs, `--no-proof` batteries.
- e0e1dad26 merge ghost-assign-bc6 after L21 (census union).
- e50f4e810 WIP: h1 sweep compare, chain2 tools.
- 1b2c1f078 10471 docstring (its base verdict is FAIL, not a false proof); full-proof batteries + probe table.
- 0d07f75d3 census rows 10470-10474; helper `assigns \nothing`; gate sweeps and gate logs.
- 875fc4f6c report draft.
- final: this report + gates3 logs.

## 7. Open / for the driver

- The hook rule refuses every module-level `__getattr__` in a reached non-program module (PEP 562 lazy loaders
  included): probe o1 shows the cost; the corpus has none (0 GONE). A narrower faithful model would need the hook's
  answers.
- `__dir__` in a wildcard package is refused as the brief asks, although CPython's `import *` does not consult it (q2).
- pickle / _pickle / shelve / pydoc / logging.config joined #326 without probes (rule 37).
- Still not covered (as u71): an aliased `setattr` (`sa = setattr`) run at RUN time in a program function, and
  computed-name `setattr(m, "b"[:1], K)` on a non-import receiver (rule E records only literal names).
