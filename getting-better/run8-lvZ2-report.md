# Run #8 lvZ2 report: restricted Path type separation (T) + the separable R614 alias / callee closure

Executor lvZ2, driver run #8, batch C repair round 3.

- Branch `run8-lvZ2`: tree `/home/fabrice/git/pycsl-lvZ2`, base `run8-lvZ` 9ccd552c7.
- Separable R614 branch `run8-lvZ2-r614`: tree `/home/fabrice/git/pycsl-lvZ2r`, same base 9ccd552c7.
- Never pushed.
- Log paths are relative to `scratchpad/lvZ2/` in the lvZ2 tree unless absolute.
- oom_kill was 15 at the start and end of every heavy job (rule 17/22).

## 1. Verdict

**SPIKE go.** Recorded in progress.txt at 2026-11-20T02:29:50Z, before the 06:00Z time box.

Every INTRODUCED channel that rt65 / rt67 / rt70 found now fails closed:
- (T) closes it by typing: it is a Why3 type error.
- R614 also refuses it before any WhyML is emitted.

`_sha256_file` stays VERIFIED and non-vacuous.

One sound control is over-refused: 10251, see section 7.

## 2. Commits

(T), branch run8-lvZ2:
- def8951b8: spike, restricted `py_path`; witnesses 10280-10288.
- a9b1e10a7: docs.
- 824211b16: 10288 reworked; stale comment; probe logs.
- ea706103e: spike evidence and R614-v1 over-refusal evidence.
- Merges of the R614 branch: 2c9cd2c1b, 59d3dd36b, 68a6d1182, 384239c7a.
- 1792fe03a: g1 gate evidence; census rows 10280-10285.
- 55539d7ad: merge of the R614 census rows. This is the FINAL merged gate commit (the snapshot
  `/home/fabrice/git/pycsl-lvZ2f`).
- cf6e6ed79 / f4c5553b3 / REPORT_COMMIT: evidence and this report.

Separable R614 part, branch run8-lvZ2-r614. It is refusal-only and lands without (T):
- 2281b58da: unresolved annotation aliases are Path-ish; imported callees are no longer hidden by unit
  defs; dotted / unknown local-module callees; witnesses 10289-10296; docs.
- 51a6452fb: measured narrowing (section 5); docs.
- d4b3f3398: fix for an IndexError on a single call-built binding.
- 04c14cbae: 10296 drops its frame claim.
- 7068e8094: census rows 10289-10295.

## 3. What (T) does (restricted)

Only the modelled constructor's result changes type. The #31-erased `p: Path` parameter, the `-> Path`
return, and every other Path lowering are byte-unchanged.

Lowerings:
- **The type.** `type py_path` is declared once in the abstract block (`abstract_ops._insert_abstract_val_block`).
- **The constructor.** `Path(<str>)` lowers to `val function ext_path_of_str_op (s: string) : py_path`.
  - lvX's guards apply unchanged: the `from pathlib import Path` binding, route #610's tables, a string argument.
  - The op is still deterministic and law-free.
  - `_is_string_expr` no longer calls the result a string.
- **Locals.** A local holds a modelled Path when every binding of it in the function is a single-target
  `n = Path(<one arg>)`.
  - Source table: `pycsl.py::_run_pipeline` builds `transpiler.ppath_locals_lvz2`, beside route #599 / #610.
  - The same constructor test is applied on top of the table.
  - Such a local is let-bound at its assignment, never given the `ref 0` pre-decl (`statements._emit_body_code`).
- **To a string.** `str(p)`, `os.fspath(p)` (the module, unshadowed), `f"{p}"` and an `os.path.*`
  argument lower to `val function path_str_op (p: py_path) : string`.
  - It has no inverse, no injectivity, and no relation to `s`.
- **Equality.** `p == q` / `!=` of two modelled Paths lowers to `val path_eq_op (a b: py_path) : bool
  ensures { result <-> (a = b) }`; in a contract it is `a = b`.
  - It is equality of the abstract values, not string equality; no law relates it to `str` or `path_str_op`.
  - This keeps `Path(s) == Path(s)` provable (control 10140), which CPython agrees with.
  - Why it is sound: the abstract value is the Path, the constructor is deterministic, and every op on
    `py_path` is law-free. Equal Paths therefore have equal `str` (congruence), which CPython also guarantees.
- **The reads lvQ / lvV / lvX use on a modelled Path take `py_path`:**
  - `.read_bytes()` inside the sha model: `ext_ppath_read_bytes_op (p: py_path)`, with the same raises as
    the string twin;
  - `.exists()` / `.is_file()` / `.is_dir()`: `ppath_*_op (p: py_path) : int`;
  - the string-typed twins remain for the erased Path values.
- **Fail-closed by typing.** Any other meeting of a `py_path` with a `str`, an int, or a user / imported /
  dotted callee's parameter is a Why3 type error:
  - `p == str(p)`, ordering, `p in [str(p)]`, a dict key;
  - an imported `ident` / `keep`, rt70 m19 / m20 / m24.
- **Code placement.** All Module 6 code is inline in methods whose mirror twins are `\trusted`
  (`_handle_call_expr`, `_is_string_expr`, `_handle_binop`, `_handle_fstring_expr`, `_emit_body_code`,
  `_insert_abstract_val_block`), plus `_handle_os_path_call`, which has no mirror twin.
  - There is no new def or method, no `\trusted`, and no axiom.

## 4. Spike measurement (bat1 S1, snapshot def8951b8 = pure (T); one NORMAL job, cwd = snapshot root)

| plane | result | log |
|---|---|---|
| corpus root vs `/home/fabrice/git/pycsl/scratchpad/run8/v69/bd-int` | 3295 / 3303; **6 MOVED**, 0 GONE, 0 APPEARED, 8 new sources | `sw1/cmp-root.txt` |
| pyref | 2185 / 2185; 0 / 0 / 0 | `sw1/cmp-pyref.txt` |
| mirror vs `v69/mir-int` | 53 / 53; **only `pycsl.mlw` moved** | `sw1/mir-diffq.txt`, `sw1/mir-diff.txt` |

- **The 6 corpus movers** are exactly the lvX / u53 Path witnesses: 10140, 10141, 10142, 10144, 10145 and
  10205.
  - lvX's M1 list predates them, so it could not include them.
  - Each mover changes only from string ops to `py_path` ops.
  - They were re-proved in g1 (section 6): every verdict is unchanged.
  - No other corpus file moved.
- **The `pycsl.mlw` mirror diff:**
  - `type py_path` is added;
  - `ext_path_of_str_op : py_path`;
  - `_sha256_file`'s body uses `ext_ppath_read_bytes_op !_p`.
  - No verified body outside `pycsl.py` moves.

## 5. Probes before / after (QUICK `--no-proof`; base = run8-lvZ 9ccd552c7, `logs/emit-base.tsv`)

The probe set has 169 probes from rt65, rt67 and rt70 (`plist.txt`). They are copied under `probes/`.

**rt70 INTRODUCED: m24, m19, m20.**
- Base: they emit string lowerings (rt70: `str_eq_op !q !q`).
- (T): all three are L3-tc, e.g. "py_path, but is expected to have type string" (`logs/emit-sp1`).
- Merged: refused by R614 (`logs/emit-pr-q5.tsv`, `emit-mw3`).

**rt65 / rt67 INTRODUCED.**
- Probes: rt65 a01, a19, a20, b03, b09, b10, d06, g01, g03; rt67 m02, m05.
- Already refused at base by u53 / lvZ's R614, and still refused.
- With R614 disabled (throwaway tree, removed; `logs/emit-x1`), (T) alone makes every one of them L3-tc.

**Sound controls still admitted under (T):**
- rt65 w10140, b11, b33, b34, c01, c04;
- rt67 n14, n16, o01, o03, o04, o08, w10140.

**Over-refused (fail-closed):**
- rt70 m26: an imported static method; opaque at base.

**`_sha256_file` non-vacuity probes:**
- rt65 c01 / c04 emit with `ext_ppath_read_bytes_op`.
- The real gate is S4 in section 6.

## 6. Gates (battery g1 on snapshot `/home/fabrice/git/pycsl-lvZ2g` at ea706103e; one NORMAL job, 05:55-10:29Z, PYTHON_CPU_COUNT=2, oom 15->15)

| gate | result | log |
|---|---|---|
| corpus root vs v69 bd-int | 3295 / 3303; 6 MOVED (the same 6 Path witnesses), **0 GONE**, 0 APPEARED | `g1/sw/cmp-root.txt` |
| pyref | 2185 / 2185; 0 / 0 / 0, OK | `g1/sw/cmp-pyref.txt` |
| mirror | 53 / 53; only `pycsl.mlw` moved, byte-identical to the spike's | `g1/sw/mir-diffq.txt` |
| census rows (`_census_row`) | 10280-10283 REFUSAL (R614); 10284 / 10285 VERIFY-FAIL. The 10289-10295 rows of g1 recorded the IndexError and were superseded by r1 | `g1/census-rows.tsv` |
| witnesses x3 | the table below | `g1/wit.tsv`, `g1/wit.<id>.<model>.log` |
| `--fun _sha256_file` (mirror `pycsl.py`) | SUCCESS, 754 / 754 Valid, rc 0 | `g1/fun.log` |
| leaf (`#@ assert 1 == 2` after `_p = Path(path)`) | FAILED: only the assertion sub-goal is unproven (754 / 756) | `g1/leaf.log` |
| mutant (`_n7 = 7 // len(path)`) | FAILED: `pycsl_div` precondition (754 / 756); the file was restored byte-identically | `g1/mut.log` |
| fidelity (sync / mirror-check / doc-coherency) | rc 0 / 0 / 0 | `g1/E-*.log` |
| fast planes (teed) | rc 0, 62 / 62 green | `g1/planes.log` |
| check-refusal-witness-coverage | rc 0: 481 demonstrated, 5 undemonstrated (ceiling 5) | `g1/pl.check-refusal-witness-coverage.log` |
| check-getattr-erasure | rc 0: DECLARED 0, ABSENT 27, UNKNOWN 75 | `g1/pl.check-getattr-erasure.log` |
| check-claim-vacuity | rc 0: 1791 / 8673, at the ceiling 1791 | `g1/pl.check-claim-vacuity.log` |
| check-assumed-facts | rc 0: 434 assumed facts, all reviewed | `g1/pl.check-assumed-facts.log` |
| check-assigns-writes-survival (single-underscore emit dir `g1/emit1`) | rc 0: TRAP 1398 / TRAP-NMS 1501 | `g1/pl.check-assigns-writes-survival.log` |
| check-trusted-frame-honesty | rc 0 | `g1/pl.check-trusted-frame-honesty.log` |
| count-trusted-directives | rc 0: markers 337, grep-substring **365** (unchanged) | `g1/pl.count-trusted-directives.log` |
| frontend-only / core-only conformance | rc 0 / 0 (38 OK / 0 MISMATCH; determinism 10 / 10) | `g1/fe-conf.log`, `g1/core-conf.log` |
| proof-axiom ledger | **3**: `git diff run8-lvZ -- src/pycsl/proof_axiom_allowlist.py` is empty; a law-free op is no axiom | |

Witness verdicts (Valid / total in brackets):

| id | expected | hoare | typed | store |
|---|---|---|---|---|
| 10280 m24 shape (imported TAT `ident`) | FAIL | REFUSED | REFUSED | REFUSED |
| 10281 m19 shape (method hides the import) | FAIL | REFUSED | REFUSED | REFUSED |
| 10282 m20 shape (dotted callee) | FAIL | REFUSED | REFUSED | REFUSED |
| 10283 ordering of two modelled Paths | FAIL | REFUSED | REFUSED | REFUSED |
| 10284 `p.exists()` is law-free | FAIL | FAILED 0/2 | FAILED 1/3 | FAILED 1/3 |
| 10285 `str(p) == s` not derivable | FAIL | FAILED 1/3 | FAILED 1/3 | FAILED 1/3 |
| 10286 control `os.fspath(p) == str(p)` | PASS | SUCCESS 2/2 | SUCCESS 2/2 | SUCCESS 2/2 |
| 10287 control `f"{p}" == str(p)` | PASS | SUCCESS 2/2 | SUCCESS 2/2 | SUCCESS 2/2 |
| 10288 control `str(p)` deterministic | PASS | SUCCESS 2/2 | SUCCESS 2/2 | SUCCESS 2/2 |
| 10140 control `Path(s) == Path(s)` (moved) | PASS | SUCCESS 2/2 | FAILED | FAILED |
| 10141 / 10142 / 10144 / 10205 (moved) | FAIL | FAILED | FAILED | FAILED |
| 10145 control, `_sha256_file` shape under `except OSError` (moved) | PASS | SUCCESS 17/17 | SUCCESS 34/34 | SUCCESS 34/34 |
| 10252 control | PASS | SUCCESS | SUCCESS | SUCCESS |
| 10251 control (Path to an imported `name_of(p: Path)`) | PASS | **FAILED (L3-tc)** | FAILED | FAILED |

- 10140's typed / store FAILED is pre-existing. lvX reported the same `let function` frame rejection.
- All of 10280-10283 are also L3-tc under (T) alone.

The REFUSAL / FAILED verdicts of 10289-10296 are covered in section 8.

## 7. Residuals

**Over-refusal of control 10251 (lvZ's witness, expected PASS).**
- The shape: a modelled `Path(s)` passed to an imported parameter annotated `Path`. That parameter is
  #31-erased to `string`, so under (T) the call is a Why3 type error.
- This is fail-closed, not a false proof.
- Module 6 cannot tell a Path-annotated `str` parameter from a real `str` one: both are `"str"` in the IR.
  Inserting `path_str_op` at every `str` parameter would re-open rt67 m05.
- A sound repair would need R614 to export the source-checked "Path argument to a Path-annotated
  parameter" call sites to Module 6, so that only those are wrapped. Not done.
- I did not flip 10251's expectation (rule 8). **The reference suite will report 10251 as an unexpected
  FAIL until the driver decides.**

Other residuals:
- rt70 m26 (an imported static method) is now refused; it was opaque at base.
- Modelled-Path `/`, `.parent`, `.name`, `.resolve()`, `mkdir`, `write_text`, `Path.cwd()` are type errors
  (`/`, `.parent`) or refused (R7Q). No corpus or mirror file uses them on a constructor result.
- The #31 erasure of `p: Path` parameters / returns is unchanged and still string-typed. That is
  pre-existing and out of scope; R614 covers it.

## 8. Separable R614 part (driver scope addition 22:25Z)

The rule is fail-closed and lives in the ROUTE #614 block of `pycsl.py::_run_pipeline`, a `\trusted` twin.
It is refusal-only: an admitted unit emits byte-identical WhyML.

**(a) Unresolved annotation aliases.** The pass collects every name and dotted tail of the unit's
annotations (string annotations parsed). Each one it cannot show innocuous is added to the Path aliases:
- a binding by a call whose arguments mention a Path class, an unresolved or type-expression / call-bound
  name, a Path import, or a nested call / lambda / starred value:
  `TypeAliasType("Fp", Path)`, `typing.TypeAliasType`, `NewType("P", Path)`, `TypeVar(bound=Path)`;
- a PEP 695 type parameter whose bound / default is suspicious in that way;
- any non-type binding of the name;
- an import from a local dependency that binds the name otherwise, or whose source is unparsable;
- an unbound name when the unit star-imports a non-stdlib module.

Each dependency's signature names get the same test, one level deep.

**(b) Callees.**
- Imported callees are no longer hidden by unit defs of the same name (rt70 m19).
- Every top-level def and every top-level class method of a local dependency is keyed under three
  spellings: the local one, the dotted-module one (rt70 m20) and `Class.method`.
- `from pkg import mod` resolves to the submodule.
- An unkeyed dotted callee rooted at a local module import is UNKNOWN when a typed stub may still reach
  it: the result is path-ish and a path-ish argument is refused.

**Over-refusal measured BEFORE narrowing.**
- Snapshot 2281b58da, bat1 S2, against v69 int.
- In that version, every call-built, unbound or non-local annotation name was an alias.

| plane | result | log |
|---|---|---|
| corpus root | 46 GONE (17 expected PASS, 26 FAIL, 3 unlabelled), 0 MOVED | `swR/cmp-root.txt`, `swR/gone-exp.tsv` |
| pyref | 0 / 0 / 0 | `swR/cmp-pyref.txt` |
| mirror | **15 / 53 refused** | `swR/mir-diffq.txt` |

**What drove the over-refusal:**
- the emitter's unbound IR type names (`"ExprIR"`, `TParamNode`);
- `from frontend import pure_ast as ast` read as the `frontend` package;
- dynamic `_N("Assign")` attributes;
- imported-class static calls.

**The narrowing (51a6452fb), and why it is sound.**
- A name the front end cannot resolve stays an opaque value; #31 / #336 never makes it a `string`.
- Kept as NOT aliases:
  - an unbound name without such a star import;
  - an import the shared resolver `frontend.ir_resolve._resolve_module_path` (Module 5's own) cannot
    find;
  - a call binding with innocuous arguments.
- The narrowing also adds the submodule resolution and the keyed class methods.
- The unknown dotted-callee rule is limited to unreadable modules, star imports, re-exports and missing
  methods.

**After the narrowing.**
- Re-emission of the 46 corpus and 15 mirror units: all 46 and all 15 emit
  (`logs/emit-gone-q5.tsv`, `logs/mir-q5.txt`).
- g1 sweep of the merged branch: 0 GONE in the corpus, mirror only `pycsl.mlw`.
- r1 sweep of the R614 branch: 3295 / 3298, 0 MOVED, 0 GONE, 0 APPEARED; pyref 0 / 0 / 0; mirror 53 / 53, `diff -rq` empty (`r1/sw/`): refusal-only, byte-inert.

**Bug found by the census and fixed (d4b3f3398).**
- A single call-built binding was unpacked as an import tuple, raising IndexError.
- So 10289-10291 / 10293 "refused" by a crash in g1, not by R614.
- After the fix: `PYCSL-R614-PATH-STR-CONFLATED` (`logs/emit-rfix*`).

**Probes after R614** (`logs/emit-pr-q5.tsv`, `emit-rfix2`).
- Now REFUSED R614:
  - rt70 t01 / t03 / t04 / m07 / m23 / m24 (PRE-EXISTING TypeAliasType erasure);
  - rt70 m19 / m20 / m26;
  - NewType / TypeVar(bound=Path): rt67 n03 / n26.
- Also refused (fail-closed): rt70 m08 / m11 (re-export / transitive alias).
- Still admitted (opaque, no false proof): m16, m17, m18.

**Witnesses 10289-10296 on the R614 branch (r1, snapshot 04c14cbae):** 10289-10295 are REFUSED (`PYCSL-R614-PATH-STR-CONFLATED`, checked in all 21 logs) in hoare / typed / store; control 10296 is SUCCESS 2/2 in all three; census 7 rows, all REFUSAL (`r1/wit.tsv`, `r1/census-rows.tsv`)

## 9. Mirror movers and proofs

- Moved: only `pycsl.mlw` (the `_sha256_file` home). It is the same in the spike, in g1 and in r1.
- `--fun _sha256_file`: SUCCESS 754 / 754 (g1).
- Whole-file mirror `pycsl.py` proof (HEAVY_LOW=1, PYTHON_CPU_COUNT=2): SUCCESS, 821 / 821 Valid, rc 0, 5661 s, oom 15->15, on the final merged snapshot 55539d7ad (`wf1/wf.status`, `wf1/wf.log`)
- expressions / statements are not owed: their mirror emissions did not move.

## 10. What was gated on which commit

- **ea706103e (g1).** Full battery.
- **04c14cbae (r1).** The R614 branch: sweep, census and witnesses.
- **55539d7ad (final merge).** The whole-file mirror proof (wf1). The delta battery f1 (fidelity, fast
  planes with the final census rows, conformance) gave: fidelity rc 0 / 0 / 0; fast planes rc 0, 62 / 62 green, including check-refusal-witness-coverage and count-trusted-directives on the final census; frontend-only / core-only conformance rc 0 / 0; oom 15->15. Window 18:52-19:29Z (`f1/summary.txt`, `f1/planes.log`).
- **src delta ea706103e -> 55539d7ad.** It is only the 2-line R614 IndexError fix in `pycsl.py`'s
  `\trusted`-twin `_run_pipeline`, plus 10296's dropped frame claim and the census rows.
  - r1 measured the fixed R614 code byte-inert on corpus, pyref and mirror.
  - A corpus re-sweep of 55539d7ad itself was dropped from f1 for the time box: the heavy queue held
    bat4 from 13:30Z.

## 11. Counts

- `\trusted`: 365 (grep-substring), markers 337, unchanged.
- Proof-axiom ledger: 3.
- No new `#@ \trusted`, no axiom, no `#@ proof`, no helper method.
