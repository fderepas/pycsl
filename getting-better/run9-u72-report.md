# run #9 u72 report -- O1-O5 repaired (one identity per definition), routes #628 / #629 / #630

Branch `run9-u72` (worktree /home/fabrice/git/pycsl-u72) = run9-u70 (40f4d17f3) + merge of ghost-assign-bc6
(L20; the base tree is f6435f70d, whose src / bin / test-suite / docs equal 4acebf73c). Not pushed.
Logs: `scratchpad/u72/logs/` (relative to the tree root). Tools: `scratchpad/u72/tools/`.


## 1. Design (FAITHFUL repair, not a narrowing)

All code is inline in `src/pycsl/frontend/ir_resolve.py` (no helper extracted); every edited function's mirror
twin is `\trusted` (`_process_dependency`, `_inject_functions`, `_resolve_direct_imports`,
`_resolve_wildcard_imports`, `_resolve_module_imports`, `_resolve_imported_classes`,
`_resolve_imported_base_classes`). `pycsl.py`, `resolve_imports`, `_resolve_module_path` and the #621 / #622 /
rule-E code are untouched.

### 1.1 `_inject_functions`: one identity per definition (replaces the u70 blanket refusal)

Each batch entry carries its origin file (`_r143_dep_file`, set by `_process_dependency`) and its in-file name
(`_u72_orig` when a caller renamed it: an import alias, a followed re-export). Two transient markers set by the
callers and only READ here (never popped, never copied into the IR; section 5 says why): `_u72_bound` (the PROGRAM binds this emitted name to this def:
a from-import local, a wildcard name the program does not redefine, a class method reached by its mangled
`<class>__m`) and `_u72_keep` (the target of a module-qualified call). Per entry:

* name free and not reserved -> injected under its name (unchanged behaviour, byte-identical emission);
* the entry present under the name IS this def (same file, same IR minus `proof`) -> skipped (unchanged);
* program-bound and the name is held by another def -> REFUSED, `PYCSL-SEM-IMPORT-FUNCTION-NAME-CLASH`
  (one program name cannot denote both);
* otherwise (a transitive in-file callee, a module-qualified target, a class's module helper) -> injected
  under a fresh `<name>_from_<module>[_k]`; every call of the batch that CPython binds to it (the same file's
  calls, by in-file name, in bodies AND contracts) is rewritten on a deep copy (the cache is shared); the emitted names go back to the caller through `ir_data["_u72_names"]`
  (popped by the caller); a call whose callee is a formal parameter of the calling function is left alone. A renamed entry nothing in the
  batch reaches and the caller does not keep is dropped (as the old code dropped it), so a program whose own
  def wins (O1) emits exactly what L20 emitted.

The reservation table `_u72_reserved` (set by `_resolve_imported_classes`, the first pass; popped by
`_resolve_imported_base_classes`, the last): each from-import local of the program -> (file, imported name),
each builtin the program calls without defining it -> (None, name). A non-bound dependency def whose name is
reserved for ANOTHER binding is renamed, so it can never capture the program's own name (probes x02, x03).

### 1.2 Route #628 (`_process_dependency` + `_resolve_module_imports`)

A requested name that is not an in-file def is followed to its origin when the binding is statically certain:
bound at exactly one site of any form in the module (the route #474 census), no namespace writer pycsl cannot see
(`*`, `globals()`, `setattr`, `__dict__`, ...), and that site is a top-level `from M import X [as name]`
(relative included: package `__init__` re-exports) or `name = b.X` with `b` bound once by a top-level
`import M [as b]`; a package `__init__` hop is refused when a submodule of that name exists. Up to 8 hops. The
origin def is returned under the requested name with its own file tag and in-file name, so it gets its own
identity. The module-qualified caller binds `m.f` to the emitted name of that def; a non-dotted `m.f` that
reaches no def keeps the old bare rewrite (an opaque call) only when nothing can capture the bare name (no
function / type of the IR has it, the program does not call it bare, it is not reserved), and the bare name is
then reserved; otherwise `m.f` stays opaque. `m.C(...)` beside `from m import C` keeps constructing the class.

### 1.3 Route #629 (`_resolve_imported_base_classes`)

The importer's own source says which module each attribute base `r.T` names. For each tail: the file `r`
resolves to is T's only admissible source; REFUSED (`PYCSL-SEM-IMPORT-BASE-CLASS-AMBIGUOUS`) when one tail is
reached through two modules, also written bare with another source, or names a class the file imports under
that name from another module (a local class of that name stays route #345's). A bare-only base that a module
import defines is refused when the bare name is bound by a wildcard import, by a from-import of another source,
by another binding, or when two module imports define it.

### 1.4 Route #630 (`_resolve_imported_classes`, `_resolve_imported_base_classes`)

Methods and helpers go through `_inject_functions` as one batch: methods are program-bound (a program
`def base__m` / `def c__m` is refused), helpers take a fresh name when their name is taken and the batch's
method bodies / contracts are rewritten, so an inlined `obj.m()` calls the library's helper. The base-class pass
also brings, under a fresh name, each module helper a method calls whose name is taken or reserved.

## 2. Over-refusal measure (sweeps; no narrowing was needed)

`scratchpad/u72/tools/S.sh` (byte-diff-sweep + mirror-emit-sweep, cwd = tree root, plain heavy.sh NORMAL).
Base: detached tree `/home/fabrice/git/pycsl-u72-b0` at f6435f70d (L20 src). Head: snapshot
`/home/fabrice/git/pycsl-u72-h1` at f158e6395, whose src / bin / test-suite equal the final commit's except the
census rows and the 10463 control body (section 4). Compare: `tools/CMP.sh` (bin/byte-diff-compare.py + `diff -rq`).

| plane | result | log |
|---|---|---|
| root | 3329 base / 3360 head .mlw; 0 MOVED, 0 GONE, 0 APPEARED; 31 new sources (u70's 8 witnesses + qa70 / qb70, u72's 12 emitted witnesses + 9 helpers) | `logs/G/C1/C-root.txt` |
| pyref | 2185 / 2185; 0 MOVED, 0 GONE, 0 APPEARED | `logs/G/C1/C-pyref.txt` |
| mirror | 53 / 53; 0 MOVED, 0 GONE, 0 APPEARED; `diff -rq` 0 lines | `logs/G/C1/C-mir.txt`, `logs/G/C1/D-mir.txt` |

GONE list: EMPTY. MOVED list: EMPTY (no moved mirror file). Re-measured on the FINAL code 6e897ac6a (snapshot
`/home/fabrice/git/pycsl-u72-h3`, `logs/G/h3/`, compare `logs/G/C3/`): identical result (0 / 0 / 0, 31 new sources). Sweep logs: `logs/S-base.txt`, `logs/S-h1.txt`.
oom_kill 15 -> 15 on both sweeps.

Refusal-to-refusal message changes are invisible to byte-diff, so `tools/RM.sh` re-ran (`--no-proof`) the 184
census REFUSAL witnesses that import a local module on L20 and head: exactly ONE message changes,
`1471_route143_contract_calls_a_helper_the_importer_redefines` (route #143's Call-name carrier): its `lim` is
now bound to the dependency's own `lim` under a fresh name, so #143 no longer fires, and the program is refused
by the no_exception reachability rule instead (CPython raises ValueError: still refused, fail-safe). Its census
row is regenerated (section 4). `logs/RM/{b0,h1}.tsv`, `logs/RM/diff.txt`.

## 3. Probes: CPython and full proofs (u70 40f4d17f3, head f158e6395; L20 column see below)

`tools/P3.sh f1 tools/probes.lst` (p.sh: cwd = tree root, PYTHON_CPU_COUNT=2, cap 3600 s, oom_kill 15 -> 15 on
every file). Per-file logs: `logs/f1-{u70,h1}/`; summaries `logs/P3-f1.txt`; table built by `tools/table.py`;
CPython: `logs/cpython-{rt80,rt77,u72,witnesses}.txt` (`python3 -B -E -s`, ulimit'd, cwd = probe dir).
The first L20 (b0) pass is VOID (61 logs hit "Disk quota exceeded" on /tmp; kept as `logs/f1-b0-VOID-quota/`);
its re-run with TMPDIR under the worktree is `logs/P3-f1-b0.txt`, `logs/f1-b0/` (0 quota hits, oom 15 -> 15).
Full table (CPython, L20, u70, head for all 152 files): `logs/probe-table.md`.

Key rows (head = this branch):

| probe | shape | CPython | L20 | u70 | head |
|---|---|---|---|---|---|
| g01 (O1) | star import then local def, true | 2 | SUCCESS | REFUSED | SUCCESS |
| p01 / p04 (O2 / O3) | lib-private `_h` vs program `_h`, true | 6 | SUCCESS | REFUSED | SUCCESS |
| p02 / p03 (O4 / O5) | two libs each with private `_h`, true | 3 | SUCCESS | REFUSED | SUCCESS |
| 10460-10461 (O4 / O5 witnesses) | two libs' private `_h`, true | assert ok | SUCCESS | REFUSED | SUCCESS |
| w19c | two libs' `helper`, true claim | 3 | FAILED (wrong body) | REFUSED | SUCCESS |
| a01 a04 a05 a06 a07 a09 (R1a-f) | re-export captured by another def, false | 1/3/3/1/1/2 | SUCCESS (false proof) | SUCCESS (false proof) | FAILED |
| x02 / x08 (new) | direct / star re-export captured by another lib's `f` | 3 | SUCCESS (false proof) | SUCCESS (false proof) | FAILED |
| x03 (new) | lib `abs` captured the program's builtin `abs` | 10 | SUCCESS (false proof) | SUCCESS (false proof) | FAILED |
| d05 d06 d08 d09 (R2) | base tail reached from two modules | 21/1/1/21 | SUCCESS (false proof) | SUCCESS (false proof) | REFUSED BASE-CLASS-AMBIGUOUS |
| x05 (new) | star-imported bare base vs module import | 1 | SUCCESS (false proof) | SUCCESS (false proof) | REFUSED |
| d11 (R3a), w06 | program `def base__m` / `def c__m` | 1 | SUCCESS | SUCCESS / SUCCESS | REFUSED NAME-CLASH |
| e04 (R3b), x09 (new) | inlined method calls program helper | 1 | SUCCESS (false proof) | SUCCESS (false proof) | FAILED |
| 10462 / 10464 | re-export / inlined-helper TRUE claims | assert ok | FAILED (wrong body) | FAILED | SUCCESS |
| w14 w14b f01 f03 f04 e02 w19 | u70's refusals, false claims | 1/1/3/3/1/2/3 | SUCCESS | REFUSED | FAILED (faithful binding) |
| x04 x07 j01 g03 w14c 10424-10427 | controls | | SUCCESS | SUCCESS | SUCCESS |

Every other rt77 / rt80 probe has the same class at head as at u70 (refused by the same pre-existing route, or
FAILED); the rt77 #619 / #620 vacuity probes FAIL at head as at L20 (e05 / e08 / v04b were SUCCESS only at
u70's pre-L20 base). No probe is SUCCESS at head with a claim CPython contradicts. Full table:
`logs/probe-table.md`.

## 4. Witnesses (corpus IDs 10450-10464 of [10450, 10469])

Helpers in the corpus root: qc72 (`f` -> 1), qd72 (`from qc72 import f`), qe72 (`f = _b.f`), qf72 (`f` -> 2),
qg72 / qh72 (class `Base`, m -> 1 / 2), qi72 (class C whose m calls its own `helper` -> 1), qj72 / qk72
(private `_h` -> 1 / 2 used by `x` / `y`). All full-prove SUCCESS on u70 and head.

| witness | header | CPython | u70 | head |
|---|---|---|---|---|
| 10450_r628_reexport_qualified_local_def_false | FAIL | 1 | SUCCESS | FAILED |
| 10451_r628_assign_reexport_local_def_false | FAIL | 1 | SUCCESS | FAILED |
| 10452_r628_reexport_vs_other_lib_qualified_false | FAIL | 3 | SUCCESS | FAILED |
| 10453_r629_two_libs_same_base_tail_false | FAIL | 21 | SUCCESS | REFUSED BASE-CLASS-AMBIGUOUS |
| 10454_r629_from_import_vs_qualified_base_false | FAIL | 1 | SUCCESS | REFUSED BASE-CLASS-AMBIGUOUS |
| 10455_r630_local_def_named_like_inherited_method_false | FAIL | 1 | SUCCESS | REFUSED NAME-CLASH |
| 10456_r630_inlined_method_calls_local_helper_false | FAIL | 1 | SUCCESS | FAILED |
| 10457-10461 (O1-O5 controls) | PASS | assert ok | REFUSED | SUCCESS |
| 10462_r628_reexport_followed_ctl | PASS | assert ok | FAILED | SUCCESS |
| 10463_r629_single_lib_attribute_base_ctl | PASS | assert ok | see note | see note |
| 10464_r630_inlined_method_library_helper_ctl | PASS | assert ok | FAILED | SUCCESS |

u70's 10420-10423 (FAIL) are now FAILED (faithful binding) instead of REFUSED; their docstrings say so.
10424-10427 stay SUCCESS. Note 10463: its first form (`X().m()`) FAILED on u70 and head (the constructor call
is opaque, pre-existing); it was changed to `g(x: X) -> x.m()` (commit 8e4faccb7, CPython re-checked) and its
final form full-proves SUCCESS on L20, u70 and head (`logs/w63-*`).
Census rows: `tools/CR.sh` (the real `_census_row`, cwd-relative) for 10420-10423, 10450-10456 and 1471, merged
by `tools/merge_census.py` into `bin/refusal-witness-census.tsv` (`logs/CR-rows.tsv`).
L20 verdicts: 10450-10456 SUCCESS (false proofs); 10457-10461 SUCCESS; 10462 / 10464 FAILED (the true claim is
unprovable against the wrong body); 10463 SUCCESS; u70's 10420-10423 SUCCESS (false proofs). `logs/probe-table.md`
shows 10463's FIRST form (FAILED everywhere); its final form is in `logs/w63-*`.

## 5. Gates

All on the final snapshot `/home/fabrice/git/pycsl-u72-h3` = 6e897ac6a (src / bin / test-suite / docs equal the
final commit's), ONE NORMAL job `tools/FINAL2.sh` run with HEAVY_PRIO=1 (driver grant), TMPDIR under the worktree,
oom_kill 15 -> 15. Summary `logs/FINAL2.txt`; details `logs/GATES3/`.

| gate | result | log |
|---|---|---|
| check-assigns-writes-survival / check-trusted-frame-honesty / check-getattr-erasure | rc 0 / 0 / 0 (emit dir `logs/GATES3/lg/mir_emit`, 53 .mlw) | `logs/GATES3/lg/*.txt` |
| check-self-annotate-sync / self-annotate-mirror-check / doc-coherency | rc 0 / 0 / 0 | `logs/GATES3/lg/{sync,mircheck,doccoh}.txt` |
| run-soundness-planes.sh (fast + conversion tier, full tee) | rc 0, 62 / 62 ok | `logs/GATES3/planes.txt` |
| check-refusal-witness-coverage | rc 0: 490 demonstrated (u70: 488), 5 undemonstrated (ceiling 5), 10 unmatchable (ceiling 10) | `logs/GATES3/rwc.txt` |
| check-corpus-executes | rc 0 (only the KNOWN load failures) | `logs/GATES3/ce.txt` |
| frontend-only-conformance | rc 0 | `logs/GATES3/foc.txt` |
| check-dropped-mutation | rc 0: 0 dropped / 49 ctxbind (ratchet 51) / 5 tryfinal / 0 dangling | `logs/GATES3/cdm.txt` |
| \trusted | 366 | `logs/FINAL2.txt` [LG] |
| proof-axiom ledger | 3 (`proof_axiom_allowlist.py` untouched; `git diff ghost-assign-bc6 HEAD -- src bin` = ir_resolve.py + census rows) | -- |
| byte-diff root / pyref / mirror on 6e897ac6a | re-swept on h3: root 3329 / 3360, pyref 2185 / 2185, mirror 53 / 53; 0 MOVED, 0 GONE, 0 APPEARED; mirror `diff -rq` 0; rc 0 | `logs/G/C3/` |

**Ratchet found and repaired (check-trusted-frame-honesty, route #401).** The first gate run, on 8e4faccb7
(`logs/GATES/lg/check-trusted-frame-honesty.txt`), was RED: `param-frame-honesty: trusted RATCHET BROKEN -- 10 > 9`,
`[!] UNNAMED frontend/ir_resolve.py _inject_functions dep_funcs ['.pop() L2384', '.pop() L2385']`. The live body
popped the transient markers off the entries of its parameter `dep_funcs` (and replaced entries in place), a write
the `\trusted` stub's frame does not declare, so every caller would be allowed to assume `dep_funcs` unchanged.
Fix (6e897ac6a): the markers are only READ, every entry is injected as a marker-free copy, and the emitted names
return through `ir_data["_u72_names"]` (popped by each caller). After: `param-frame-honesty(trusted): ... 9 declare
a frame omitting a parameter ... 17 of them ledgered`, rc 0 (`logs/GATES3/lg/check-trusted-frame-honesty.txt`).
The 151 probe / witness emissions are byte-identical before and after the fix (`logs/e2-h1` vs `logs/e3-head`,
`logs/E-e3-head.txt`). That first run was then stopped by me (its remaining gates ran on the superseded code).


## 6. Open / for the driver

- Census rows (real `_census_row`, `logs/CR-rows.tsv`, merged into `bin/refusal-witness-census.tsv`): 10420-10423
  REFUSAL -> VERIFY-FAIL, 10450-10452 / 10456 VERIFY-FAIL, 10453-10455 REFUSAL, 1471 new message (it embeds the
  snapshot path `/home/fabrice/git/pycsl-u72-h2/...` of the dependency, as any absolute-path refusal does).
- 10463 (final form) full-proves SUCCESS on L20, u70 and head (`logs/w63-*`).
- Residuals I know of: (a) a dependency function passed as a VALUE (`map(_h, xs)`) inside an inlined method body
  is not renamed (only `Call` nodes are); (b) a module-qualified `m.C()` constructor for two libraries' same-named
  classes now ends as an R325 refusal (o01), was opaque before; (c) a dependency-internal call whose callee
  name is also a LOCAL variable (not a parameter) of the caller is rewritten (only formal parameters are
  excluded); only matters for inlined bodies.
- The `_same` test (same file + same IR minus `proof`) can fail for a def first injected with rewritten calls and
  later requested raw under the program's own name: it is then refused (fail-safe, not seen in any sweep).

## 7. Commits (branch run9-u72, not pushed)

b4f20828b merge L20 + untrack progress.txt; 1de6f4d1f core rule + witnesses; e6d824c13 / ce47fd13e / 2fa565c55 /
f158e6395 #629 refinements, m.C() fix, wildcard reservation; then WIP evidence commits up to 8e4faccb7 (10463
control) and this report.
