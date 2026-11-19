# Run #8 lvZ report: routes #614 + #617, a pathlib Path value is identified with its string

Executor lvZ, driver run #8. Tree `/home/fabrice/git/pycsl-lvZ`, branch `run8-lvZ` (base `run8-int70`
ff01853ec). Spike branch `run8-lvZ-spikeT` (fdb9e6419). Never pushed. Log paths are relative to
`scratchpad/lvZ/` in the tree unless absolute.

## 1. Spike (T): Path as its own abstract WhyML type `py_path`

Branch `run8-lvZ-spikeT`, commit fdb9e6419 (measurement only, not for landing).

What the spike does:
- Module5 `_m5_path_ann_tag` tags `Path` / `PurePath` / `PosixPath` / `PurePosixPath` annotations (also
  through #31's alias resolution and `Optional[..]`) `py_path` instead of `str`. The Windows flavours are
  excluded: `PureWindowsPath("A") == PureWindowsPath("a")` while their `str`s differ.
- Module6: a `py_path` parameter / `-> Path` return is `py_path`; `type py_path` is declared once in the
  abstract block. `Path(<str>)` is `ext_path_of_str_op : string -> py_path`. `str(p)` / `os.fspath(p)` /
  `f"{p}"` is the law-free `path_str_op : py_path -> string`. `p / s` is `ppath_div_op`, `.parent`,
  `.stem` / `.name` / `.suffix`, `.resolve()`, `.is_file()` / `.is_dir()` / `.exists()`, `Path.cwd()`,
  `mkdir` / `write_text` / `read_bytes` take or return `py_path`. `os.path.*` of a `py_path` argument
  wraps it in `path_str_op`. `Path == Path` is `path_eq_op` (equality on the abstract type).
- Everything else that mixes a `py_path` with a `str`, or orders two of them, falls through to the
  existing lowerings and is a Why3 type error (fail-closed).

### Measurement (battery `bat1`, step S1; one NORMAL heavy job, cwd = snapshot tree root, oom_kill 15 -> 15)

| plane | result | log |
|---|---|---|
| corpus root vs `scratchpad/run8/v69/bd-int` | 3295 / 3295; **24 MOVED**, 0 GONE, 0 APPEARED | `bat1/spike-cmp-root.txt`, `bat1/spike-moved-root.txt` |
| pyref | 2185 / 2185; 0 / 0 / 0 | `bat1/spike-cmp-pyref.txt` |
| mirror vs `scratchpad/run8/v69/mir-int` | 53 / 53; **9 MOVED** | `bat1/spike-cmp-mir.txt`, `bat1/spike-mir-diff.txt` |

- The 24 moved corpus files are exactly the Path-lowering files (lvQ / lvV / lvX / u44 / u53 / gen36 ch14
  witnesses). About 12 of them are expected-PASS, and each would owe a re-proof.
- At the L3-tc level, none of the 66 corpus files that mention Path changed category
  (`logs/emit-spkcorp` vs `logs/emit-rcorp`).
- The 9 mirror movers are `pycsl`, `audit_proof` and `audit_proof_reverify`, plus 6 others:
  `frontend/import_classifier` and `proof2why3/{crosscheck, crosscheck_ir, extract, extract_lean_meta,
  sertop}`.
- Two of those 6 have VERIFIED bodies that move:
  - `proof2why3.crosscheck._module_namespace_of` (`let function ... (rocq_file: py_path)`);
  - `proof2why3.extract_lean_meta.lean_meta_available` (`let ... (proofs_dir: py_path)`, now with
    `ppath_div_op` / `ppath_isfile_op`).
- The landing would also have to inline the spike's classifier method `_lvz_is_path_expr`. It is a new
  method in a mirrored file, so it is counted by the mirror-coverage ratchet.

Probes (QUICK `--no-proof`, `logs/emit-spk1` vs `logs/emit-before`):
- All 16 rt67 shapes that emitted string lowerings at base became L3-tc type errors: m01 m02 m05 n02 n17
  n18 n19 n24 n27-n31.
- One sound control was over-refused: o03 (`f"{p}" == str(p)`). Route #307 rebinds the f-string operand
  to a fresh name that the classifier cannot see.
- o04 and o08 (`os.path` of a Path) were over-refused in that run. The `os.path` wrap fixed them before
  fdb9e6419, but they were not re-measured.

**Recommendation: (R).** By the driver's rule, (T) fails on both counts:
- it moves verified mirror bodies beyond `pycsl.py` / `audit_proof*`;
- it costs 24 corpus re-proofs.

(T) remains the principled direction. It needs a run that owns `proof2why3` and `import_classifier`
mirror re-proofs and can inline the classifier.

## 2. Option taken: (R), the R614 extension (`src/pycsl/pycsl.py::_run_pipeline`, the ROUTE #614 block)

Why (R): the driver's default rule (section 1). It is refusal-only: an admitted file emits byte-identical WhyML.
It is all inline in `_run_pipeline`, whose mirror twin is `\trusted`. There is no new def or method, no
Module 6 change, no `\trusted`, and no axiom.

What changed:
- **(a) Aliases.** A name is a Path ALIAS when it is bound, anywhere and to a fixpoint, by a TYPE
  EXPRESSION that mentions a Path class or an alias:
  - the binding forms: `X: T = v`, `X = v`, PEP 695 `type X = v`;
  - a type expression is a name, attribute, string, subscript or `|` union, never containing a
    call, lambda or walrus.
  - Also aliases: an import binding of a Path class (`Path as Fp`), and a name imported from a local
    dependency where it is such an alias.
  - Aliases join the annotation pattern `_pa614` (body and IR contract tests alike) and the Path-class
    set `_pc614`.
- **(b) Imported callees.** For every import whose module resolves locally
  (`frontend.ir_resolve._resolve_module_path`), the dependency's source is parsed and its own aliases are
  resolved.
  - Each imported function the unit calls (injected `\trusted` stubs) gets its declared `def`:
    `from m import f`, `import m` + `m.f`, `from m import *`. The `def` is None when absent, e.g. a
    re-export.
  - A call is path-ish when that `def` returns a Path, is None, or has an unannotated return with a
    path-ish argument.
  - Every dependency function or METHOD declared `-> Path` joins the Path-returning names (by name, as
    the unit's own do).
  - A path-ish argument to an imported parameter not annotated Path, or to an unknown signature, is
    REFUSED. This applies in the body and in the IR contract walk.
- **Gate widened.** The pass now also runs on every unit that imports a name: rt67 m01's importer never
  spells `Path`.

Docs: `test-suite/annotations.md` §7.614 (paragraph "Route #617"); `docs/pycsl-translational-reference.md`
(the PATH / STR CONFLATION paragraph).

## 3. rt65 / rt67 probes, before (ff01853ec, `logs/emit-before`) and after (`logs/emit-r3`, `logs/emit-r3b`)

- **rt65.** Every confirmed false proof was already REFUSED at base by u53's R614, and still is: a01 a07 a19
  a20 b03 b09 b10 g01 g03 d06, also g02. No rt65 probe changed category. Every admitted rt65 / rt67
  probe emits BYTE-IDENTICAL WhyML: 23 / 23 `.mlw` compared, 0 differ. The controls are among them:
  w10140, c01, c04 (`_sha256_file` non-vacuity) and b11.
- **rt67 confirmed false proofs (SUCCESS at base) are now REFUSED (`PYCSL-R614-PATH-STR-CONFLATED`):**
  - m01: imported `-> Path`;
  - m02: imported `ident`;
  - m05: Path passed to an imported `str` parameter;
  - n02: `TypeAlias`;
  - n17: `!=` branch;
  - n18: ordering;
  - n24: PEP 695.
- **rt67 shapes emitted but not proved by rt67, now REFUSED:** n27 (`TypeAlias = pathlib.Path`), n28
  (`ensures \result == p`), n29 (`in`), n30 (dict key), n31 (method), n19 (vacuous `requires p == "a"`).
  m06 (imported `-> Tuple[Path, int]`) was L3-tc and is now refused too.
- **Now refused although sound at base** (opaque int, so no false proof possible): n01 (`PathT = Path`), n20
  (`TypeAlias = "Path"`), n25 (`Path as Fp`). These are fail-closed over-refusals of probe shapes, not
  corpus files.
- **Unchanged:**
  - sound controls o01 o03 o04 o08 n14 n16 w10140;
  - NewType / TypeVar n03 n26 (opaque int, no false proof);
  - the L3-tc and other-route refusals.
- **Own probes** (`probes/lvz`; CPython 3.14.4 ulimit'd agrees with each claim being false):
  - q01 imported alias, q02 `import h; h.mk`, q05 alias chain, q07 `Optional` alias, q08 `type Fp =
    pathlib.Path` and q10 `from h import *` emitted string lowerings at base (`logs/emit-lvz-base`,
    `emit-lvz3-base`). All are REFUSED now.
  - q11 re-export and q12 imported class method are refused (q11 by R325 at base and now).
  - q13 (imported class field) and q14 are L3-tc / refused.
  - Control q04 is admitted.

## 4. Witnesses (corpus 10240-10254; helper `test-suite/corpus/pycsl-reference/multi_file_lib/r617_pathlib.py`)

The CPython expectation holds for all of them (ulimit'd, `python3 -E -s -B`).

At base ff01853ec (`logs/emit-wit-base`), every one except 10253's first draft EMITTED. That draft was
replaced because u53's contract walk already refused it.

| id | shape | expected | hoare | typed | store |
|---|---|---|---|---|---|
| 10240 | `Fp: TypeAlias = Path`, `p == str(p)` | FAIL | REFUSED R614 | REFUSED | REFUSED |
| 10241 | `type Fp = Path` | FAIL | REFUSED | REFUSED | REFUSED |
| 10242 | alias ordering by parts | FAIL | REFUSED | REFUSED | REFUSED |
| 10243 | alias `!=` branch | FAIL | REFUSED | REFUSED | REFUSED |
| 10244 | alias of `Optional[Path]` | FAIL | REFUSED | REFUSED | REFUSED |
| 10245 | alias chain `A = Path; B: TypeAlias = A` | FAIL | REFUSED | REFUSED | REFUSED |
| 10246 | alias imported from a dependency | FAIL | REFUSED | REFUSED | REFUSED |
| 10247 | imported `mk(s) -> Path` | FAIL | REFUSED | REFUSED | REFUSED |
| 10248 | imported `ident(p: Path) -> Path` | FAIL | REFUSED | REFUSED | REFUSED |
| 10249 | Path to imported `keep(x: str)` | FAIL | REFUSED | REFUSED | REFUSED |
| 10250 | `import ... as lib; lib.mk(s)` | FAIL | REFUSED | REFUSED | REFUSED |
| 10251 | control: Path to imported `name_of(p: Path) -> str` | PASS | SUCCESS 2/2 | see below | see below |
| 10252 | control: alias, `str(p)` compared | PASS | SUCCESS 2/2 | SUCCESS 2/2 | SUCCESS 2/2 |
| 10253 | alias `p in [str(p)]` | FAIL | REFUSED | REFUSED | REFUSED |
| 10254 | `from ... import *`, `mk(s)` | FAIL | REFUSED | REFUSED | REFUSED |

Logs: `bat1/wit.tsv`, `bat1/wit.<id>.<model>.log`. oom_kill was 15 -> 15 on every run.

10251 in typed / store FAILED 1/3 at 3fc8f5079:
- Its `#@ assigns \nothing` cannot hold, because the injected stub `name_of` declares no frame
  (`val name_of .. writes { int_mem }`, `logs/10251.typed.mlw`).
- This is a property of the witness's claim, not of the change. The frame claim was dropped at e5b2f55c8.
- The re-proof is in section 5 (`bat2/wit.tsv`).

Census rows: 13 rows via `_census_row` (all REFUSAL), measured in the battery (`bat1/census-rows.tsv`) and
appended to `bin/refusal-witness-census.tsv`.

## 5. Gates (battery `bat1`: ONE NORMAL heavy job, 15:06-18:07Z, cwd = snapshot root `/home/fabrice/git/pycsl-lvZr` at 3fc8f5079; oom_kill 15 -> 15 throughout)

Between 3fc8f5079 and e5b2f55c8, `src/` is identical. The only changes are the census rows, 10251's
dropped frame claim, the report and the evidence.

| gate | result | log |
|---|---|---|
| corpus root byte-diff vs `scratchpad/run8/v69/bd-int` (comparator once) | 3295 baseline / 3297 candidate; 0 MOVED, 0 GONE, 0 APPEARED; 2 new sources (10251, 10252, the only emitting witnesses); OK, rc 0 | `bat1/R-cmp-root.txt` |
| pyref byte-diff | 2185 / 2185; 0 / 0 / 0; OK, rc 0 | `bat1/R-cmp-pyref.txt` |
| mirror sweep vs `scratchpad/run8/v69/mir-int` | 53 / 53; 0 MOVED; `diff -rq` empty; rc 0 | `bat1/R-cmp-mir.txt`, `bat1/R-mir-diff.txt` |
| M1 moved list | EMPTY: no corpus file moved, so no re-proof is owed and no over-refusal of an expected-PASS file | as above |
| fidelity (sync / mirror-check / doc-coherency) | rc 0 / 0 / 0 | `bat1/E-*.log` |
| fast planes (`run-soundness-planes.sh`, teed) | rc 0; 62 / 62 green (23 slow planes not run, as for u53) | `bat1/planes.log` |
| check-refusal-witness-coverage | rc 0: 481 demonstrated, 5 undemonstrated (ceiling 5) | `bat1/pl.check-refusal-witness-coverage.log` |
| check-assigns-writes-survival (single-underscore emit dir `bat1/emit1`, 53 files) | rc 0: HOLE 0, TRAP 1398 / TRAP-NMS 1501 | `bat1/pl.check-assigns-writes-survival.log` |
| check-trusted-frame-honesty (same dir) | rc 0 | `bat1/pl.check-trusted-frame-honesty.log` |
| check-getattr-erasure | rc 0: DECLARED 0, ABSENT 27, UNKNOWN 75 | `bat1/pl.check-getattr-erasure.log` |
| check-claim-vacuity | rc 0: 1791 / 8654, at the ceiling 1791 | `bat1/pl.check-claim-vacuity.log` |
| count-trusted-directives | rc 0: markers 337, grep-substring **365** (unchanged) | `bat1/pl.count-trusted-directives.log` |
| frontend-only / core-only conformance | rc 0 / 0: 38 OK / 0 MISMATCH; determinism 10 / 10 | `bat1/fe-conf.log`, `bat1/core-conf.log` |
| proof-axiom ledger | 3: `src/pycsl/proof_axiom_allowlist.py` has no diff vs run8-int70; no axiom, no `#@ proof` | `git diff run8-int70 -- src/pycsl/proof_axiom_allowlist.py` |
| `_sha256_file` | still VERIFIED: the mirror `pycsl.mlw` is byte-identical to int70's, so the `let` body is unchanged. Still non-vacuous: rt65 c01 / c04 emit byte-identical WhyML to base, where rt67 measured FAILED 0/2 and 1/3 | `bat1/R-mir-diff.txt`, `logs/emit-before/c04_sha_leaf_false.mlw` vs `logs/emit-r3/` |

Mirror movers: none. No mirror whole-file proof is owed, so expressions / statements are not owed.

## 6. Residuals

**The root is not removed.** In the model, a Path is still a `string`. (R) refuses every channel found so far.
(T), the `py_path` type, would close the class by typing. Its cost is measured in section 1.

Channels (R) does not follow:
- A Path FIELD of an IMPORTED class (`b = h.Box(Path(s)); b.p`, probe q13; also rt67 m04): it fails
  closed today by L3-tc, not by R614.
- Imported module-level Path CONSTANTS (rt67 m03): refused by R325, not R614.
- A dependency that cannot be resolved by `_resolve_module_path`: R614 treats only resolvable local
  dependencies specially. Other imported names keep u53's module / imported-name admissions.
- Aliases that are VALUES rather than type expressions (a Path class reached through a call or a
  container): not aliases, so not tracked.

New over-refusals and pending re-proof:
- Over-refusal: a parameter annotated through a plain alias or the `"Path"`-string alias (rt67 n01 / n20 /
  n25) is now refused where it was an opaque int at base. That is sound but over-refused. No corpus file is
  affected.
- Over-refusal: any call to a re-exported dependency function (its `def` not found in the named module) is
  path-ish, so comparing its result with a `str` is refused.
- 10251 in typed / store at e5b2f55c8 (frame claim dropped): see section 7.

Older residuals, kept from u53:
- Annotation honesty is trusted.
- 2160 (two non-`Path(..)` Path operands) stays refused.

## 7. Commits (branch run8-lvZ, never pushed)

- 39f967c89 WIP (R): aliases + imported callees; witnesses 10240-10253
- 3fc8f5079 (R): star imports, re-exports, imported Path-returning methods; 10254; docs
- c49917934 battery script; 4366f1790 WIP
- 8df908e6c spike measurement -> (R)
- e5b2f55c8 (R) gated: census rows; bat1 evidence; 10251 frame claim dropped
- (spike, branch run8-lvZ-spikeT) fdb9e6419
