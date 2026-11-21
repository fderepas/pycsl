# run #8 executor u59 -- route #429 follow-up (review rt71): narrowing 2 over the import closure

Branch `run8-u59` (worktree `/home/fabrice/git/pycsl-u59`), base `run8-int73` (c31a5c7eb). Commit only, never pushed.

## Commits
* `f57b98601` WIP: first variant (closure + per-code-point cancellation). SUPERSEDED: it refused the mirror desugar /
  Module5_IREmitter.
* `f11922e05` the rule as landed (`src/pycsl/pycsl.py`, `test-suite/annotations.md` §7.611,
  `docs/pycsl-translational-reference.md` §T.6.101a (4)). The witnesses 10320-10324 and their dependencies came in
  with f57b98601.
* `578c57342` census rows for 10320-10323 (`bin/refusal-witness-census.tsv`, through `_census_row`).
* the report commit (this file + the route429 file u59 section).

## The gap
rt71: narrowing 2 decided "held elsewhere" on the MAIN file only. A str value of an IMPORTED module (a stub's parameter
default, a stub's contract literal) holding "€" was excused when the main file held "€" as `raise` / `print` text:
`len(h3()) == 3` PROVED (CPython 1). This was pre-existing.

## The rule (inline in `_run_pipeline`; mirror twin `\trusted`, no mirror re-port owed)
An excused value now also needs both of these:
1. **Emitted position** (`_np429`). Route #411's literal scan keeps a stack of open parentheses. From each literal above
   Latin-1 it walks outward. It may cross only `(str_concat_op ..)` groups, a group the literal opens, or a group whose
   first element is the inner group. The walk must reach one of these:
   * `(E ..)` right after `raise`;
   * `(str_hash_op ..)` directly in `(print_1 ..)`;
   * a transparent group right after `let _ =` (a builtin raise's discarded message).

   Anything else is not excused: a stub default, a contract term, a call argument.
2. **Import closure.** Every module reached by any `import` / `from .. import`, transitively, is read. It is resolved
   by `_resolve_module_path`, including package prefixes and the `X.Y` submodule form. In each non-main module, these
   join `_ne429`:
   * every str constant outside that module's own raise / print text (docstrings included);
   * every `#@` string token.

   If the resolver refuses an import, or a module cannot be read or parsed, nothing is excused.

Why it is sound: a payload is never read. Handler arms are wildcards, route #233 refuses `except .. as e` reads, and
builtin tags carry no payload. `print_1` and `let _ =` throw the value away. `str_concat_op` has no precondition. So no
obligation or claim depends on an excused literal, whichever module produced it.

Narrowest-rule choice: I measured the brief's "never excuse anything a non-main module holds, cancel on any non-main
code point" first (f57b98601). It refused desugar and Module5_IREmitter. Their closure reaches the LIVE `frontend`
package through `--import-path src/pycsl`, and its messages carry the same U+2014. That is not a hole, because none of
that text enters those emissions. The emitted-position condition closes rt71's class at the point where it happens: the
dependency value lands as a call argument or a contract term.

## Probes, before -> after (logs `scratchpad/u59/e4/` emission, `scratchpad/u59/w2/` full pipeline x3, oom 15 -> 15)
| probe | before | after |
|---|---|---|
| rt71 k05 (default + raise) | PROVED 2/2 (rt71 logs/ph2) | REFUSED R429 hoare/typed/store |
| rt71 h01 (contract + raise) | PROVED 2/2 (rt71 logs/ph2) | REFUSED x3 |
| rt71 h02 (contract + print) | emitted rc 0 (rt71 logs/e7h) | REFUSED x3 |
| rt71 k01 (`import m; m.h()`) | emitted rc 0 (rt71 logs/e9h) | REFUSED x3 |
| controls k05b / h01b | REFUSED | REFUSED x3 |
| u57 n1 | R506 | R506 x3 |
| u57 n2 / n3 / n7 / n8 / n9 / n10 | R429 | R429 x3 |
| u57 n4 / n5 (excusal controls) | PROVE | PROVE x3 |
| u57 n6 | FAIL, not refused | FAIL x3, not refused |
| new t1 (re-export) / t2 (`from pkg import mod`) | - | FAIL x3, not refused: the import is opaque (`val h3_0 () : int`), no literal enters |

## Witnesses (corpus IDs 10320-10324 used; 10325-10329 unused)
* 10320-10323 are expected FAIL and REFUSED x3.
* 10324 is the control. It PROVED in hoare (2 Valid). typed / store fail Why3 typing ("variable int_mem does not
  occur"). That is pre-existing, because the rule does not change the emission.
* u57's 10260-10279 re-run x3 give u57's verdicts: 13 x 3 REFUSED; 10269 / 10270 / 10273 FAIL; 10276 / 10277 PROVE
  x3; 10278 / 10279 PROVE in hoare.

## Over-refusal and gates (f11922e05; the census rows for the plane runs = 578c57342)
* byte-diff vs `run8/v72/bd-int`:
  * root: 3309 / 3310, 0 MOVED / 0 GONE / 0 APPEARED, 1 new source (10324). `scratchpad/u59/C2-root.txt`, rc 0.
  * pyref: 2185 / 2185, 0 / 0 / 0. `scratchpad/u59/C2-pyref.txt`, rc 0.
  * one comparator run per tree; sweeps `scratchpad/u59/bd2`, `scratchpad/u59/sweeps2.out`, oom 15 -> 15.
* mirror vs `v72/mir-int`: 53 / 53, 0 MOVED / 0 GONE / 0 APPEARED. `scratchpad/u59/D2-mir.txt`, rc 0. The first
  variant's 51 / 53 is in `scratchpad/u59/D-mir.txt`.
* fidelity: check-self-annotate-sync rc 0, self-annotate-mirror-check rc 0, doc-coherency --check rc 0
  (`scratchpad/u59/gates/E-*.log`).
* fast planes: rc 0, 62 / 62 ok (`scratchpad/u59/gates/planes-fast.log`). Not run with --slow.
* check-refusal-witness-coverage run on its own: OK, 484 demonstrated, 5 undemonstrated (ceiling 5)
  (`gates/refusal-witness-coverage.log`).
* count-trusted-directives: OK, 339 markers / 367 grep (unchanged against run8-int73).
* proof-axiom allowlist: no diff (ledger 3).
* oom_kill stayed at 15 for every job.

## Notes
* The rule is still a syntactic allow-list. The emitted-position walk trusts that `raise (E ..)` payloads and
  `let _ =` / `print_1` results are unread. That is the same assumption as u57's guarantee, now checked on the emitted
  text instead of the source.
* Process slip: one progress line was accidentally appended to the MAIN worktree's untracked `progress.txt` (a `cd`
  inside a backgrounded `&&` chain). It was removed seconds later (that file's last line is u60's again). Nothing else
  in the main tree was touched.
