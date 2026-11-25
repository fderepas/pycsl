# run #9 executor u75: u73 over-refusals o4-o7 repaired, routes #635 (string-exec stdlib APIs) and #636 (module objects handed to library code)

Branch `run9-u75` (tree `/home/fabrice/git/pycsl-u75`), made from `run9-u73` (e1b967928) with `ghost-assign-bc6`
(ba48d5888, src / bin / test-suite = L21 main b959bb1b2) merged in before any change (53c770046, no conflict).
Brief: `scratchpad/run9/brief-u75.md`. Logs: `scratchpad/u75/logs/` (`L/` below), tools `scratchpad/u75/tools/`,
probes `scratchpad/u75/probes/{rt83,u75}/` (+ the u73 probe set under `scratchpad/u73/probes/`). Sweep `.mlw`
files are git-ignored (on disk under `L/G/`). Every job ran with `TMPDIR=scratchpad/u75/tmp`; no output of mine
contains EDQUOT / "Disk quota exceeded" / "No space left" (S.sh greps for it). oom_kill was 15 at the start and
end of every heavy job and on every probe line: no result VOID.

Trees (main .venv symlinked; kept for re-proof):
- `b1` = /home/fabrice/git/pycsl-u75-b1, detached at 53c770046 (my merge base = u73 src + L21; MEASURE base).
- `b2` = /home/fabrice/git/pycsl-u75-b2, detached at c001bbdbd (ghost-assign-bc6; src = L21 main).
- `h1` = /home/fabrice/git/pycsl-u75-h1, detached at df528157b (the fail-closed rules BEFORE narrowing: MEASURE).
- `h2` = /home/fabrice/git/pycsl-u75-h2, detached at 0891f99e7 (final src).

## 0. Status

- **Task 1 (u73 INTRODUCED over-refusals) REPAIRED.** rt83 o4 / o5 / o6 / o7 (CPython 4 = claim) are SUCCESS
  (full proof) at head, as at L21; u73 refused them. Every rt81 / rt83 false-proof probe and the u73 witnesses
  10470-10474 stay REFUSED (rt83 h6 / h8 controls: REFUSED, by rule M / the namespace-dict rule).
- **Task 2 (route #635, PRE-EXISTING false proofs s2 / s3 / s4) CLOSED**: REFUSED (`PYCSL-SEM-IMPORT-STATE-MANIPULATED`).
  t1 / v3 (`from test.support import swap_attr`) are also refused by the same list (`test`).
- **Task 3 (route #636, PRE-EXISTING false proofs u1 / u3 / v2 / t1 / v3) CLOSED**: u1 / u3 / v2 REFUSED by the new rule M
  (`PYCSL-SEM-IMPORT-MODULE-VALUE`), t1 / v3 by #635 (`test`). New u75 variants c1 (`m = pkg` then
  `update_wrapper(m, ...)`), c2 (the module passed to a PROGRAM function whose body hands it to
  `update_wrapper`), c3 (`update_wrapper(one, _two, assigned=("__code__",))` on a from-imported dependency function):
  all false proofs at L21 and u73 (CPython 2), REFUSED at head.
- **Over-refusal**: MEASURED on the fail-closed rules BEFORE narrowing (h1 vs b1): root 0 MOVED / **24 GONE** / 0
  APPEARED, pyref 0 / **16 GONE** / 0, mirror 0 / 0 / 0. After the narrowing (h2 vs b1): root 0 MOVED / **1 GONE**
  (declared: 6026) / 0 APPEARED, pyref 0 / 0 / 0, mirror 0 / 0 / 0 (diff -rq 0 lines). Lists in section 3.
- src changes: `src/pycsl/frontend/ir_resolve.py` (route #326's block in `resolve_imports`, and the u60 / u71 / u73
  walk inside `resolve_imports`; `_inject_functions` and the class resolvers untouched) and `src/pycsl/pycsl.py`
  (route #483's closure inside `_run_pipeline` only; nothing between `_BODY_EQ_RE` and `def main`). Both mirror
  twins are `\trusted` / outside the proved mirror set (u73 checked; mirror emission sweep 0 diff). No helper
  extracted (all inline), no new `\trusted` (365), no axiom (ledger 3), no gate / ratchet edited (bin/ change =
  6 census rows).
- Process deviation (stated plainly): the brief says one heavy job at a time. My QUICK probe batteries dev2 / dev3
  (`L/dev2.txt`, `L/dev3.txt`, 18:43-19:20Z) ran while my base sweep `S-b1` was queued and then running
  (started 18:48Z). Never more than two jobs of mine at once; from 19:20Z on, strictly one job at a time.

## 1. Rules (all inline)

**Task 1 (o4 / o5): the class-base / annotation escape counts only names that can be a MODULE object.** u73 made an
import-bound name in a class base or in a parameter / return / module / class annotation a module-object escape.
In those positions the name (or the attribute / subscript chain read off it) is now EVALUATED from its import
binding(s): `import X` -> the module; `from X import n` -> X is resolved as the walk resolves it (program view;
"F" local file, "S" the interpreter's own standard-library module object, read from `sys.modules` or imported
when it is one of a fixed list of side-effect-free modules) and n is looked up: a submodule (any directory entry
of that name, or an `__init__` that touches `__path__`) is a module (followed to its file when FileFinder's choice
is plain); in a local file, a name bound ONLY by undecorated `def` / `class` statements is "L" (a class or
function, never a module), a name bound otherwise (`X = 3`) is "V", a plain re-export (`from Y import n`, the
only binding) is followed to Y (at most 8 hops), an import / wildcard / `global` binding or no binding is "M"
(unknown, module-like); in a standard-library module, the attribute's actual value: a module, or "SN". The
escape is recorded at once for a module-like value (F / S / M). L / V / SN values are recorded only if a
reflective escape exists anywhere in the walk (`globals()`, `vars`, `__dict__`, `sys.modules`, an import of
`importlib` / `inspect` / an installed library, an annotation evaluator, a computed / reflective-name
`getattr` / `attrgetter` / `methodcaller`, ...): a module reaches such a binding only through a store whose value is
an import-rooted module value (refused by rule M below) or through such a reflective channel. An SN value further
needs a "planting" store (an import-rooted attribute store / delete / literal setattr, a namespace mapping, a
computed setattr). Why sound for the class base: PEP 560 calls `__mro_entries__` only for a base that is not a
type, so a class base never hands the module out; a typing alias such as `List[int]` is no module. A name bound
LOCALLY (a parameter, a store or a comprehension target in its function / lambda / comprehension scope, with no
`global` / import of it there) is not the import binding (`def g(os: C): return os.n`, corpus 10117).

**Task 1 (o6 / o7): the MODULE-HOOK scan, the #632 `__init__` check and route #483's copy.** A def or a Name store
binds `__getattr__` / `__mro_entries__` (`__dir__` in the #632 copies) in ITS OWN scope: the nearest enclosing
def / lambda / class whose BODY holds the binding (decorators, defaults and bases are evaluated outside), so a
class-body `__getattr__ = _fwd` (o6) or a function local is no module hook; the walrus in a module-level default
`def _f(x=(__getattr__ := _ga))` stays a module hook (probe u75 e3, REFUSED). The literal is a READ as the 2nd
argument of a two-argument `hasattr` / `getattr` call (o7) in a module that binds neither name; this admission is
withdrawn (MODULE-HOOK in the walk, route #483's message in the closure) when any reached module mentions
`builtins` / `__builtins__` (a rebound `getattr` could make it a store; probe e2, REFUSED). Writes through a literal
stay refused: `globals()[...]` (namespace-dict rule, rt83 h8), setattr at import time (#483, h6), `setattr(m, ...)`
of a module now also by rule M.

**Task 2 (route #635).** Route #326's dynamic-import list gains `timeit`, `code`, `codeop`, `cProfile`, `profile`,
`pdb`, `bdb`, `trace`, `doctest`, `test` (each only when it is the standard library's: a name that resolves to a
local file is the program's own module, read and verified like any other), with the existing condition (the
program also has an import resolved to a local file). New walk rule: any reached module OTHER than the program that
imports (anywhere, function bodies included) a standard-library module of the whole list (#326's + these)
REFUSES (`PYCSL-SEM-IMPORT-STATE-MANIPULATED`, new message): route #326 judges only the program and route #483 only
import-time code (and the calls it can follow). I did not apply #483's allow-list to the program file (not cheap:
it would refuse every program importing a module outside `_OKS483`; not measured).

**Task 3 (route #636): RULE M (`PYCSL-SEM-IMPORT-MODULE-VALUE`, new site).** In every module the walk reaches (the
program included), an import-bound name -- or an attribute / subscript chain read off one -- whose evaluated value
(above) is module-like (F / S / M) or a function / class of a local module (L), used as a VALUE, REFUSES. Value =
every position u71 counts as an escape except the ones below: a call argument to ANY callee (a program function
too: its parameter can be handed on, u75 c2), an assigned / returned / yielded / stored / iterated / keyword /
container value, an operand of a binary operator or a non-identity comparison (they hand it to the other operand's
method). Exempt: callee, attribute / subscript receiver, store / delete receiver, expression statement, raise,
decorator, except type (u71's list); an identity test (`is` / `is not`); for a MODULE object only (its special
methods are ModuleType's C code) a truth test, a unary operand, an f-string field, and a read by an unshadowed
builtin that only reads it (`hasattr(m, "<literal>")`, `print`, `repr`, `str`, `id`, `len`, `type(m)`, `dir`,
`hash`, `bool`, `callable`) unless a reached module mentions `builtins`. L / V / SN values count only with a
reflective escape (and SN with a planting store), as in Task 1. A byte-identical copy of an interpreter
standard-library file (the admitted repo-root `json/`, route #611 r12) is standard-library code and is not judged.
Soundness argument for the narrowing: a module object can only reach library code by being handed to it; every
hand-off of an import-bound module (directly or through a variable, a container, a parameter, a return) starts
with a value use of the import-bound name (refused), and every other way of obtaining a module object (reflection,
installed libraries) is a recorded escape that re-enables the L / V / SN cases.

Not covered (left OPEN, reported): a module object obtained REFLECTIVELY (`importlib.import_module("pkg")`,
`sys.modules[...]` in a dependency, `globals()["pkg"]`) and handed to library code is judged only through the
older rules (u71 escape -> stores judged; #326 / #483 / namespace-dict rules); a FUNCTION object of the PROGRAM
itself handed to `update_wrapper(..., assigned=("__code__",))` is outside import resolution (a separate route
candidate: a program function's behaviour can be replaced by library code).

Docs: u75 text next to u73's in `test-suite/annotations.md`, `docs/pycsl-static-semantics-reference.md`,
`docs/pycsl-translational-reference.md`.

## 2. Probes

Method (`tools/PB.sh`, inside `tools/chain2.sh`, one PRIO job 21:38-23:52Z): `--no-proof` of every probe (rt83 53,
rt81 45, u73 14, u75 14, u71's 108-line list of rt76 / rt78 / rt79 / u64 / u66 / u69 / u71 probes) and of every
u75 witness / helper, on h2 (head), b2 (L21 main) and b1 (u73 src); then a FULL proof (hoare, PYTHON_CPU_COUNT=2,
timeout 3600) of every probe / witness whose `--no-proof` reached SUCCESS on that tree. A `--no-proof` refusal /
type-check failure is final. Logs `L/PB-{h2,b2,b1}.txt`, per-run logs `L/PB-*/`. CPython: both interpreters, -B,
`ulimit -v 2000000`, script mode (`tools/cpy.sh`; `L/cpy-rt83.txt`, `L/cpy-u75.txt`, `L/cpy-rt81-u73.txt`,
`L/cpy-wit.txt`; for the --import-path / cwd probes of the u71 list u71's and u73's CPython logs); the two
interpreters agree on every probe. Full table: `L/Ptab.txt` (probe | CPython | L21 | u73 | head), rows that
differ: `L/Ptab-diff.txt`.

**No head SUCCESS that CPython contradicts; no head SUCCESS where L21 or u73 refused or failed, except the four
repaired o-probes and the u75 controls (all CPython = claim).**

| probe | CPython | L21 | u73 | head |
|---|---|---|---|---|
| rt83 o4 / o5 / o6 / o7 | 4 (= claim) | SUCCESS | REFUSED (REBOUND / HOOK) | **SUCCESS** |
| rt83 o5c | 4 | SUCCESS | SUCCESS | SUCCESS |
| rt83 s2 / s3 / s4 (#635) | 2 | **SUCCESS (false)** | **SUCCESS (false)** | REFUSED (STATE-MANIPULATED) |
| rt83 t1 / v3 (`test.support.swap_attr`) | 2 | **SUCCESS (false)** | **SUCCESS (false)** | REFUSED (STATE-MANIPULATED) |
| rt83 u1 / u3 / v2 (#636) | 2 | **SUCCESS (false)** | **SUCCESS (false)** | REFUSED (MODULE-VALUE) |
| u75 c1 / c2 / c3 (#636 variants) | 2 | **SUCCESS (false)** | **SUCCESS (false)** | REFUSED (MODULE-VALUE) |
| u75 d1 (timeit in a dependency function) | 2 | REFUSED (#483) | REFUSED (#483) | REFUSED (STATE-MANIPULATED, walk) |
| u75 a2 (`typing.List[int]` param) / a3 (`class D(pkg.k.Base)`) / e1 (function-local `__getattr__`) | 4 | SUCCESS | REFUSED | SUCCESS |
| u75 a5 (o4 + `globals()`) | 4 | REFUSED (REBOUND, u71 escape) | REFUSED | REFUSED (REBOUND) |
| u75 e2 (`import builtins` + `hasattr(x, "__getattr__")`) | 4 | REFUSED (#483) | REFUSED | REFUSED (MODULE-HOOK, fail-closed) |
| u75 e3 (walrus `__getattr__` in a module-level default) | 2 | REFUSED | REFUSED | REFUSED (MODULE-HOOK) |
| u75 c4 (`print(pkg.k.CONST)`, `sys.argv`, `if pkg.b`) | 1 | SUCCESS | SUCCESS | SUCCESS |
| u75 c7 (`isinstance(x, pkg.k.Base)`) | 1 (= claim) | SUCCESS | SUCCESS | REFUSED (fail-closed cost: a local class handed to a builtin) |
| rt83 o1 / o2 (`import unittest` / `pickle`) | 1 | SUCCESS | REFUSED | REFUSED (u73 #633, by design) |
| rt83 h6 / h9 / m1 / u2 / h11 | 2 / 3 | REFUSED | REFUSED | REFUSED (now MODULE-VALUE / REBOUND first) |
| rt83 f1 / f2 / f6 / f7 / f8 (ForwardRef latent) | 2 | TC-FAIL | TC-FAIL | TC-FAIL (unchanged, still latent) |
| rt83 y1 / r1c | 2 / AttributeError | FAIL | FAIL | FAIL |
| rt81 p2 / p2b / p8 / x1b / x3 / x4 / x9 / p4 / p4b, u73 k1 / k2 / m2 / q1 / q4 | 2-5 | **SUCCESS (false)** | REFUSED | REFUSED |
| u73 o1 / q2 (u73 fail-closed costs) | 1 / 2 | SUCCESS | REFUSED | REFUSED |

Every other probe has the same verdict on all three trees (`L/Ptab.txt`); some refusals now name a different
(earlier) rule, e.g. u71 e1-e11 / t1-t13 / y2-y6 move from #483 / rebound-name to MODULE-VALUE (still refused).

## 3. Over-refusal (cwd = tree root; compare once per tree; both counts asserted)

| sweep | h1 MEASURE (fail-closed, vs b1) | h2 final (vs b1) | logs |
|---|---|---|---|
| root | rc 1: 3348 / 3324, 0 MOVED / **24 GONE** / 0 APPEARED | rc 1 -> with `--expect-gone 6026...`: rc 0, 1 GONE (0 unexpected); raw: 3348 / 3355, 0 MOVED / **1 GONE** / 0 APPEARED, 8 new sources | `L/G/C-h1-root.txt`, `L/G/C-h2-root.txt`, `L/G/C-h2-root-declared.txt` |
| pyref | rc 1: 2185 / 2169, 0 / **16** / 0 | rc 0: 2185 / 2185, 0 / 0 / 0 | `L/G/C-h{1,2}-pyref.txt` |
| mirror (53) | rc 0, 0 / 0 / 0, diff -rq 0 lines | rc 0, 0 / 0 / 0, diff -rq 0 lines | `L/G/C-h{1,2}-mir.txt`, `L/G/D-h{1,2}-mir.txt` |

**MEASURE GONE list (h1, before narrowing; 40)**: root 0590, 0591, 10117_r610_os_name_plain_object_ctl,
10186_r613_json_namespace_dir_re_ctl, 10187_r613_json_identical_codecs_copy_ctl, 10188_r613_json_no_shadow_ctl,
10221_r613x_pkgmode_orders_agree_ctl, 10251_r617_imported_name_of_str_ctl, 10296_lvz2_r614_imported_keep_str_ctl,
10305_r613y_cwd_admitted_stdlib_copy_ctl, 1476_route143_same_source_import_on_both_sides_is_allowed,
4294_gen37_r326_sys_other_attrs_control, 4295_gen37_r326_sys_pure_read_control, 6026_gen37_r409_ctl_stdlib_obj,
6337_r428_ctl_stdlib_function_on_self, 7151_r461_ctl_module_allow_list, 7454_x3_r474_dep_str_const_aug,
7457_x3_r474_ctl_dep_const_bound_once, 7458_x3_r474_ctl_dep_str_const_bound_once,
7463_x3_r475_ctl_dep_utf8_cookie_nonascii, 7464_x3_r475_ctl_dep_latin1_cookie_ascii,
7573_f2_r474_control_dep_const_no_writer, 7574_f2_r474_control_pkg_no_writer, 7680_y2_r483_control_dep_constant_folds;
pyref 0115, 0117, 0200, and 13 `stdlib/json/*` files (JSONDecoder decode / raw_decode, JSONEncoder default /
encode / iterencode, dump, dumps; `_proves` and `_fails`). Causes (`L/GQ-h1fix.txt`, `L/GQ-h1fix2.txt`): the repo-root
`json/` stdlib copy judged as program code; a namespace-package PREFIX (`multi_file_lib`) counted as an installed
library (reflective escape); a re-exported constant (`from os import SEEK_SET`); a dependency's own-view resolution
of a package-qualified import; a parameter named like an import (10117); `hasattr(sys, ...)` / `len(sys.path)`;
`http` not loaded in pycsl's process. Each narrowing is in section 1 with its argument.

**Final GONE list (h2): 6026_gen37_r409_ctl_stdlib_obj** (a PASS control that puts the module `os.path` into a set
`{os.sep, os.getcwd, os.path}`: a module object stored in a container is exactly what rule M refuses; declared).

## 4. Witnesses (IDs 10490-10500 inside [10490, 10509]; CPython from the tree root, both interpreters, `L/cpy-wit.txt`)

| witness | CPython | L21 | u73 | head | header |
|---|---|---|---|---|---|
| 10490_r635_timeit_string_rebinds_submodule_false (s2) | 2 | SUCCESS (false) | SUCCESS (false) | REFUSED (STATE-MANIPULATED, #326) | FAIL |
| 10491_r635_code_interpreter_runsource_rebinds_submodule_false (s3) | 2 | SUCCESS (false) | SUCCESS (false) | REFUSED (STATE-MANIPULATED, #326) | FAIL |
| 10492_r635_dependency_function_runs_timeit_string_false (d1) | 2 | REFUSED (#483) | REFUSED (#483) | REFUSED (STATE-MANIPULATED, walk; new site) | FAIL |
| 10493_r636_update_wrapper_sets_package_submodule_false (u1) | 2 | SUCCESS (false) | SUCCESS (false) | REFUSED (MODULE-VALUE; new site) | FAIL |
| 10494_r636_update_wrapper_replaces_dependency_function_false (v2) | 2 | SUCCESS (false) | SUCCESS (false) | REFUSED (MODULE-VALUE) | FAIL |
| 10495_r636_module_through_local_function_to_update_wrapper_false (c2) | 2 | SUCCESS (false) | SUCCESS (false) | REFUSED (MODULE-VALUE) | FAIL |
| 10496_r631o_parameter_annotation_typing_alias_beside_store_ctl (o5) | 4 | SUCCESS | REFUSED | SUCCESS | PASS |
| 10497_r631o_imported_class_as_base_beside_store_ctl (o4) | 4 | SUCCESS | REFUSED | SUCCESS | PASS |
| 10498_r631o_dependency_class_body_getattr_ctl (o6) | 4 | SUCCESS | REFUSED | SUCCESS | PASS |
| 10499_r631o_dependency_hasattr_hook_name_read_ctl (o7) | 4 | SUCCESS | REFUSED | SUCCESS | PASS |
| 10500_r636o_module_constant_and_stdlib_attribute_arguments_ctl | 1 | SUCCESS | SUCCESS | SUCCESS | PASS |

Helpers (corpus root): `zu75a/` ... `zu75k/` (packages with b.py / c.py / k.py), `zu75c_run.py`, `zu75i_proxy.py`,
`zu75j_probe.py`; each helper's own run is SUCCESS (`L/W-final/`; zu75i_proxy's `_fwd` no longer always raises,
which made its own proof vacuous at h2). Census rows: the real `_census_row` (`tools/CR.sh`) for 10490-10495
(`L/CR-rows.tsv`), appended to `bin/refusal-witness-census.tsv`. Rule 38: the full IDs are unique; the 4-character
cut gains the `1049` / `1050` prefix duplicates with the older 4-digit files (the artefact u69 / u71 / u73 recorded;
`ls | cut -c1-4 | uniq -d` was already non-empty before u75).

## 5. Gates (final commit; `tools/chain3.sh` -> `tools/GATES.sh`, cwd = u75 worktree; one PRIO job)

Gate run on 46a2b74ce (src = h2 0891f99e7; + the helper fix) plus the 6 census rows, `L/chain3.txt`, `L/GATES/`;
one PRIO job 00:09-01:37Z, oom_kill 15 -> 15:

| gate | result | log |
|---|---|---|
| byte-diff root vs b1 | rc 0 with `--expect-gone 6026_gen37_r409_ctl_stdlib_obj`: 3348 / 3355, 0 MOVED, 1 GONE (0 unexpected), 0 APPEARED, 8 new sources | `L/G/C-h2-root-declared.txt` (raw: `L/G/C-h2-root.txt`) |
| byte-diff pyref vs b1 | rc 0: 2185 / 2185, 0 / 0 / 0 | `L/G/C-h2-pyref.txt` |
| mirror sweep 53 + diff -rq | rc 0, 0 / 0 / 0, 0 lines (no mirror emission moves: no re-proof owed) | `L/G/C-h2-mir.txt`, `L/G/D-h2-mir.txt` |
| check-self-annotate-sync / self-annotate-mirror-check / doc-coherency --check (fidelity) | rc 0 / 0 / 0 | `L/GATES/lg/{sync,mircheck,doccoh}.txt` |
| run-soundness-planes.sh (fast, full tee) | **rc 0: all 62 planes green** | `L/GATES/planes.txt` |
| check-refusal-witness-coverage | rc 0: 496 demonstrated (494 + MODULE-VALUE + the walk's STATE-MANIPULATED), 5 undemonstrated (ceiling 5) | `L/GATES/rwc.txt` |
| check-corpus-executes | rc 0 (only the known load failures) | `L/GATES/ce.txt` |
| frontend-only-conformance | rc 0 (10/10 byte-stable across PYTHONHASHSEED) | `L/GATES/foc.txt` |
| check-dropped-mutation | rc 0: 0 / 49 / 5 / 0 | `L/GATES/cdm.txt` |
| check-vacuous-drivers | rc 0 (every suite at or below its ratchet) | `L/GATES/cvd.txt` |
| check-assigns-writes-survival / check-trusted-frame-honesty / check-getattr-erasure (emit dir `L/GATES/lg/mir_emit`, 53) | rc 0 / 0 / 0 | `L/GATES/lg/*.txt` |
| witnesses + helpers, full proof on the final tree | FAIL witnesses REFUSED with the codes above, PASS controls SUCCESS (all contracts proven), every helper SUCCESS | `L/chain3.txt` [W], `L/W-final/` |
| \trusted | 365 (= main; unchanged) | `L/chain3.txt` [LG] |
| ledger | 3 (no allowlist / axiom change) | -- |

Probe batteries (section 2): `L/PB-h2.txt` (h2 = final src), `L/PB-b2.txt` (L21), `L/PB-b1.txt` (u73); oom_kill 15 on
every line.

## 6. Commits (branch run9-u75, not pushed)

- 53c770046 merge ghost-assign-bc6 (setup, no conflict).
- 9c8f54fe5 WIP h1: all three tasks (fail-closed), tools, probes, dev batteries.
- df528157b WIP h1b: rule M operand exemptions tightened (= the MEASURE tree h1).
- 53a81ba87 witnesses 10490-10500 + helpers, docs, gate tools.
- 0891f99e7 h2: the narrowing after the MEASURE (= final src).
- 46a2b74ce helper zu75i_proxy fix; sweep compares; PB h2.
- final: census rows 10490-10495, this report, gate / probe logs.

## 7. Open / for the driver

- Reflectively obtained module objects handed to library code (see section 1) and program-function objects
  mutated by library code (`update_wrapper(f, g, assigned=("__code__",))` on a PROGRAM def) are not covered.
- rt83 latent f1 / f2 / f6-f8 (`typing.ForwardRef(...).evaluate()` yields the module): still TC-FAIL (fail-safe);
  not addressed here (not in the brief). The computed-name `getattr` / `attrgetter` / `methodcaller` escape added
  for rule M's reflective case does not change them.
- Fail-closed costs on true programs that L21 proved: c7 (`isinstance(x, pkg.k.Base)`: a local class handed to a
  builtin; a metaclass `__instancecheck__` could receive it) and corpus 6026 (a module in a set); u73's own costs
  (rt83 o1 / o2, u73 o1 / q2) are unchanged.
- The SN case reads standard-library attribute values from pycsl's own interpreter (the same interpreter the claim
  is about; route #613 refuses local shadows); a standard-library module that later rebinds its own global to a
  module object would not be seen.

