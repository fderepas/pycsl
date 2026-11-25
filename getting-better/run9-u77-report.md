# Run #9 u77 report: rt87 b1 repaired (FLOAT-FINITE now declared for the float-field PyVal path); rt87 c15 repaired (receiver-class narrowing of PYCSL-FUNCTION-FRAME)

Executor u77, driver run #9, short soundness repair. Branch `run9-u77` in `/home/fabrice/git/pycsl-u77`, created from `run9-u76` (cb5dc921c). Never pushed.

- Base tree (detached at the run9-u76 tip cb5dc921c): `/home/fabrice/git/pycsl-u77b`.
- Head snapshot tree: `/home/fabrice/git/pycsl-u77h`. The sweeps and G ran at 8c3985346, with the 4 census rows in its working tree. It was then moved to 85b031a88 for G3 / G4.
- Paths are relative to `scratchpad/u77/` unless absolute.
- Every heavy job went through heavy.sh with `HEAVY_PRIO=1` (granted by the brief), `PYTHON_CPU_COUNT=2` and `TMPDIR=scratchpad/u77/tmp`. The `--no-proof` wrappers ran with `HEAVY_QUICK=1`.
- oom_kill was 15 before and after every job. No counted log contains EDQUOT, "Disk quota exceeded" or "No space left".

## Verdict

- **b1 (INTRODUCED reporting gap): REPAIRED by the reporting option.** `--soundness-report` now lists FLOAT-FINITE for every function whose body reads a `float`-typed record field. This is a superset of every program-context site where `_pyval_wrap` emits the u76 carrier.
  - b1 at head is PROVED under the declared model, and the report lists `FLOAT-FINITE ... relied on by f: a float record field read (r.x)`.
  - Under `--strict-float-finite` it is REFUSED (route #606, unchanged).
  - At run9-u76 the report listed only BUILTIN-EXACT and LATIN1-STR.
  - No emission changes: the edit is in `pycsl.py::_build_soundness_report`, outside the `_BODY_EQ_RE` .. `def main` region, and its mirror twin is `\trusted`. u74's `_to_cache_payload` conversion is untouched and still VERIFIED: the mirror emission is byte-identical, so the u76 whole-file proofs carry over.
- **c15 (INTRODUCED over-refusal): REPAIRED, sound and cheap.** In the PYCSL-FUNCTION-FRAME measurement only, a dotted call `x.m(..)` whose receiver class is statically known is resolved to that class's family (itself, its ancestors, its descendants). Otherwise the any-class union stays. The emitted frames (`_eff316`: written / positions / global) and the method rules are unchanged.
- **Movement vs run9-u76** (measured once per tree, cwd = tree root): **0 MOVED / 0 GONE / 0 APPEARED** for the corpus root, pyref and mirror. No mirror file moved, so no whole-file proof is owed.

## 1. b1: FLOAT-FINITE for the float-field PyVal carrier (src/pycsl/pycsl.py, `_build_soundness_report`)

**Cause (rt87 KEY FINDING 4).** The FLOAT-FINITE detector fires in two cases:
- for a comparison whose operand subtree mentions a float;
- for any comparison in a function "holding a PyVal value" (`_ma_pv`: the string `PyVal` in the symbol table / annotations).

In b1:
- `PyVal = Any` is recorded as `dict`, so `_ma_pv` is false;
- the float field `r.x` is read inside the dict literal, not as an operand of `d["a"] == d["a"]`.

The comparison can also sit in ANOTHER function from the wrap. Probe `c/b1r.py` shows this: `mk(r)` returns `{"a": r.x}` and `g` compares.

**Fix.** For every function, its body is walked for a `FieldGet` / `Attribute` read whose field name is `float`-typed in some record (`_ma_fields`, by name, as the existing detector does). Such a function gets a FLOAT-FINITE entry whether or not it contains a comparison: `"<f>: a float record field read (r.x): a PyVal value built from it is HFloat, a Why3 real (hval_eq reflexive; route #606, rt87 b1)"`.
- `_pyval_wrap`'s float arm fires only on a program-context `Attribute` / `FieldGet` whose `_field_type_of` is `float`, so every program that emits the wrap is covered.
- The rule over-reports any float field read, which is allowed ("over-, never under-reported").
- The docs row is in `docs/pycsl-translational-reference.md` (the FLOAT-FINITE paragraph).

**Evidence** (`c/h|b/<probe>/*.log`; QUICK `--no-proof --soundness-report`, and `--strict-float-finite`):

| probe | head report | run9-u76 report | head `--strict-float-finite` | full proof head |
|---|---|---|---|---|
| b1 (`d["a"] == d["a"]` in f) | FLOAT-FINITE (relied on by f), BUILTIN-EXACT, LATIN1-STR | BUILTIN-EXACT, LATIN1-STR only | REFUSED (route #606 PyVal compare) | PROVED (10530) |
| b1r (wrap in `mk`, compare in `g`) | FLOAT-FINITE (relied on by mk) | not listed | REFUSED | L3-tc fail-closed (no emission, both trees) |

## 2. c15: receiver-class narrowing of the PYCSL-FUNCTION-FRAME measurement (src/pycsl/Module6_WhyMLTranspiler.py, `transpile`, route #316 block)

A name has a statically known class when either holds:
- it is a parameter annotated with a record class;
- it is a local whose every binding (`_bind316`: assign, for, unpack, walrus) is a constructor call `C(..)` of one record class C.

In both cases the name must occur in the SSA-renamed body ONLY as:
- a `Var` read;
- a field access / store `object`;
- that constructor binding's `target`.

Anything else disqualifies the name: a rebinding, a for / unpack / with / except target, a shadowing nested parameter, a name list such as `global`. For such a name, a single-dot call `x.m(..)` gets the allowed method prefixes `{C} ∪ ancestors(C) ∪ descendants(C)`, lower-cased like the method names. Ancestors are included because inherited methods are cloned under the subclass prefix, and descendants because an override is reachable through a base-typed value. If no candidate matches, every same-named method is used, as before.

A second fixpoint `_effn316` uses the narrowed candidates. It is consulted ONLY for a non-method's `undeclared` (owner side) and for the importer-side body measurement `_bodyw634`. `_eff316` and every emitted `writes` stay as before. `PYCSL-METHOD-FRAME` still uses `_eff316`.

The mirror twin of `transpile` is `\trusted`, so no §10.4 re-port is owed. The code is inline (no helper). The docs row is in `docs/pycsl-static-semantics-reference.md` §frame rules.

| probe / witness | shape | CPython | head | run9-u76 |
|---|---|---|---|---|
| c15 / 10532 | `f(r: R)` `assigns \nothing` returns pure `r.total()`; unrelated S.total writes self | `3 R(a=1, b=2)` | PROVED | REFUSED PYCSL-FUNCTION-FRAME |
| c15n / 10533 | R.total itself writes `self.a` | `0 R(a=2, b=2)` | REFUSED | REFUSED |
| c15i / 10534 | R inherits a self-writing `total` from base B | `0 R(a=2, b=2)` | REFUSED | REFUSED |
| c15l / 10535 | local `q = R(..)`; `q.total()` | `3 R(a=1, b=2)` | PROVED | REFUSED |
| c15w / 10536 | `q = r`, conditionally `q = s` (S writes) | `0 R(a=1, b=2) S(n=1)` | REFUSED (`r`, `s`) | REFUSED |
| 10537 (+ helper zu77a) | importer of c15's f | `CPython g(R(1,2)) = 1` | PROVED | REFUSED (importer) |

## 3. Movement vs run9-u76 (`sw.sh`: base sweep in pycsl-u77b at cb5dc921c, head sweep in pycsl-u77h at 8c3985346, each with cwd = its tree root; `logs/sw.out`)

| plane | base | head | MOVED | GONE | APPEARED | log |
|---|---|---|---|---|---|---|
| corpus root | 3356 | 3361 | 0 | 0 | 0 (+5 new sources: 10530, 10532, 10535, 10537, zu77a) | `sw/head/C-root.txt` (rc 0) |
| pyref | 2185 | 2185 | 0 | 0 | 0 | `sw/head/C-pyref.txt` (rc 0) |
| mirror | 53 | 53 | 0 | 0 | 0 | `sw/head/C-mir.txt` (rc 0), `sw/head/diffrq-mir.txt` (0 lines) |

The sweep emitted 3357 / 6410 (base) and 3362 / 6419 (head) source files. oom_kill was 15 at the start and the end.

## 4. Witnesses (corpus IDs 10530-10537 + helper `zu77a.py`; full proofs on the final snapshot `wit/hs/`, earlier run `wit/h/`, base `wit/b/`; CPython `wit/cpython.txt`)

| id | expected | head (snapshot) | run9-u76 |
|---|---|---|---|
| 10530 | PASS, `# pycsl-model-assumption: FLOAT-FINITE` (b1 shape) | PROVED; report lists FLOAT-FINITE (`wit/h/10530.report.log`) | PROVED, FLOAT-FINITE NOT listed (`wit/b/10530.report.log`) |
| 10531 | FAIL, `--strict-float-finite` | REFUSED (ir-semantic route #606) | REFUSED |
| 10532 | PASS (c15 control) | PROVED | REFUSED PYCSL-FUNCTION-FRAME |
| 10533 | FAIL | REFUSED PYCSL-FUNCTION-FRAME | REFUSED |
| 10534 | FAIL | REFUSED PYCSL-FUNCTION-FRAME | REFUSED |
| 10535 | PASS (local constructor) | PROVED | REFUSED |
| 10536 | FAIL (alias fallback) | REFUSED PYCSL-FUNCTION-FRAME | REFUSED |
| 10537 | PASS (importer) | PROVED | REFUSED |

- The census rows for the 4 FAIL witnesses come from the REAL `_census_row` (`cen_rows.py`, `logs/CEN.out`).
- Numeric duplicate corpus ids: 0.

## 5. Gates (snapshot pycsl-u77h; `logs/GG.out`, `logs/G/`)

- G = `GG.sh` / `G.sh`: snapshot pycsl-u77h at 8c3985346 plus the 4 census rows, i.e. the src / bin of 85b031a88. Log: `logs/GG.out`.
- G3 / G4: pycsl-u77h moved to 85b031a88 after the S field-default fix. Logs: `logs/G3.out`, `logs/G4.out`.

| gate | result | log |
|---|---|---|
| byte-diff root vs run9-u76 | rc 0: 0 MOVED / 0 GONE / 0 APPEARED (+5 new sources) | `sw/head/C-root.txt` |
| byte-diff pyref | rc 0: 2185 / 2185, 0 / 0 / 0 | `sw/head/C-pyref.txt` |
| mirror | rc 0: 53 / 53, 0 / 0 / 0; `diff -rq` empty | `sw/head/C-mir.txt`, `sw/head/diffrq-mir.txt` |
| check-assigns-writes-survival (single-underscore emission dir, 53 files) | rc 0 (HOLE 0, HOLE-NOWRITES 8, TRAP 1398 <= 1399, TRAP-NMS 1501) | `logs/G/lg/check-assigns-writes-survival.txt` |
| check-trusted-frame-honesty | rc 0 (0/1, 0/63) | `logs/G/lg/check-trusted-frame-honesty.txt` |
| check-getattr-erasure | rc 0 (DECLARED 0) | `logs/G/lg/check-getattr-erasure.txt` |
| check-assigns-underdeclaration | rc 0 (TRAP 3 / HOLE 0) | `logs/G/underdecl.txt` |
| fidelity: check-self-annotate-sync / self-annotate-mirror-check / doc-coherency / sibling-concrete / stdlib-contract | rc 0 / 0 / 0 / 0 / 0 | `logs/G/{sync,mircheck,doccoh,sibfid,stdfid}.txt` |
| run-soundness-planes.sh (fast + conversion tier), teed | **61 / 62** on G. The one red plane was `check-corpus-contract-truth`, caused by the NEW files: it default-constructs `S()` to run the zero-argument `S.total` (`ensures \result == 0`), and S had a required field (10532, 10535, zu77a). Fixed in 85b031a88 (`n: int = 0`). On 85b031a88 that plane is rc 0 (`logs/G3/check-corpus-contract-truth.txt`). The other corpus-reading planes, run individually, are all rc 0: check-corpus-executes, check-corpus-contract-truth-args, check-claim-vacuity (1791 at the ceiling), check-refusal-witness-coverage (494 demonstrated) (`logs/G4/*.txt`). The full 62-plane run was NOT repeated on 85b031a88 (time box); its src / bin equal G's, and only those three corpus files differ. | `logs/G/planes.txt`, `logs/G3/`, `logs/G4/` |
| count-trusted-directives | rc 0; `\trusted` (canonical grep) **364** | `logs/G/count-trusted.txt`, `logs/GG.out` |
| proof-axiom ledger | `proof_axiom_allowlist.py` diff vs run9-u76: 0 lines (ledger 3) | `logs/GG.out` |
| witnesses on the snapshot | 8 / 8 as expected, both before (`wit/hs/`) and after (`wit/hs3/`, `logs/G3.out`) the S fix | |
| duplicate numeric corpus ids | 0 | `logs/G4.out` |

- oom_kill was 15 throughout.
- Rule 34 (tooling): `pycsl.py` changed only in `_build_soundness_report`, which is not proof tooling. No mirror emission moved, so the u76 whole-file proofs of `audit_proof_reverify` / `audit_proof` (and the rest) carry over on byte-identical `.mlw`. The vacuity / dispatch code is unchanged.

## 6. Commits (branch run9-u77, never pushed)

- 8c3985346 -- b1 detector (pycsl.py), c15 narrowing (Module6_WhyMLTranspiler.py), docs, witnesses 10530-10537 + zu77a, probe sources and scripts
- 85b031a88 -- census rows (real `_census_row`) for 10531 / 10533 / 10534 / 10536; S field default in 10532 / 10535 / zu77a; sweep compares
- this report commit (report + gate logs)

**Not addressed (pre-existing, rt87 KEY FINDINGS 1-3, route #643):** the a1 partial record frame, the d1b / s1 dict and set parameters, and the g9 module-global write. They are out of this brief's scope.
