# Run #8 executor u51: route #612 (`Callable` parameters assumed pure), SOUNDNESS BATCH S2

Branch `run8-u51` (worktree `/home/fabrice/git/pycsl-u51`), base `0057c8b94`. Commit only, nothing pushed.
`\trusted` 367 (unchanged; no file under `src/self-annotate` touched). Proof-axiom ledger unchanged
(`src/pycsl/proof_axiom_allowlist.py` untouched). oom_kill 0 at the start and end of every heavy job
(`scratchpad/u51/phase1.oom`, `job2.oom`).

## Commits

| commit | content |
|---|---|
| `b446e220b` | WIP (gated as g1): the rule in `_run_pipeline`, witnesses 10170-10178, the 1878 rewrite, docs §T.TY3.8 / §12.17, route file, probe kit |
| (this commit) | census rows for 10170-10176 (`_census_row`), witness docstring corrections (10170-10176 base verdict wording), CPython results, this report |

## 1. Measurement (base 0057c8b94)

grep / AST read plus QUICK emissions (`scratchpad/u51/q-before/`).

| population | files with a `Callable[...]` parameter | emitting | referencing the parameter |
|---|---|---|---|
| `pycsl-reference` (3275 mlw) | 15 | 5: 1853, 1854, 1878, 2586, 6641 | **1: 1878** |
| `python-reference` (2185 mlw) | 0 | - | - |
| mirror (53) | 0 | - | - |
| `src/pycsl_lib` | 0 (only a comment) | - | - |

- The other 10 files are refused by the existing rules: 1314, 1745, 1750, 1751, 1752, 1792, 1852, 1877, 2586 and 6616.
- 2586 (`Optional[Callable]`) lowers to the erased `Any`, so it carries no `callable:` tag.
- The files that emit rely on the arrow parameter only as a declaration, except 1878 (`requires f(x) >= 0` / `return f(x)`).

## 2. Probes (`getting-better/open-routes/witnesses-r612/p01..p21`; CPython results in `cpython-results.txt`)

Each probe was run under CPython with ulimit. The pycsl verdicts below are full proofs in the hoare model:
- BEFORE: base snapshot `scratchpad/u51/basetree` (git archive of 0057c8b94), logs in `scratchpad/u51/before/`;
- AFTER: `b446e220b`, logs in `scratchpad/u51/after/`.

| probe | shape | CPython | BEFORE | AFTER |
|---|---|---|---|---|
| p01 | `f(s) == f(s)` (lvX) | VIOLATION False | **PROVED** | REFUSED R612 |
| p02 | `ensures \result == f(x)` / `return f(x)` | VIOLATION | **PROVED** | REFUSED R612 |
| p03 | `requires f(x) >= 0` then `return f(x)` | VIOLATION -1 | **PROVED** | REFUSED R612 |
| p04 | `f(0)` then `len(xs)` | VIOLATION 2 | **PROVED** | REFUSED R612 |
| p05 | `f(x) - f(x)` around another statement | VIOLATION -1 | **PROVED** | REFUSED R612 |
| p06 | raising callable under `no_exception \all` | VIOLATION ValueError | refused (no_exception unknown call) | REFUSED R612 |
| p07 | non-returning callable, partial claim | (not run: never returns) | PROVED (partial correctness: not a false claim) | REFUSED R612 |
| p08 | unannotated alias `g = f` | VIOLATION | Why3 type error (`g` is an `int` ref) | REFUSED R612 |
| p09 | Callable FIELD `b.f(x)` | VIOLATION | refused (method / attribute ambiguity) | same |
| p10 | passed to a user function that applies it | VIOLATION | **PROVED** | REFUSED R612 |
| p11 | `map(f, xs)` | VIOLATION | refused R325 | REFUSED R612 |
| p12 | `f.__call__(x)` | VIOLATION | not proved (Unknown) | REFUSED R612 |
| p13 | `#@ assert a == f(x)` after `a = f(x)` | (ghost claim) | **PROVED** | REFUSED R612 |
| p14 | callable appends to caller's list under `assigns \nothing` | VIOLATION | **PROVED** | REFUSED R612 |
| p15 | CONTROL: declared, not referenced | ok 2 | PROVED | PROVED |
| p16 | `(f)(x)` | VIOLATION | **PROVED** | REFUSED R612 |
| p17 | method parameter | VIOLATION | **PROVED** | REFUSED R612 |
| p18 | Callable FIELD `h.cb(x)` | VIOLATION | refused (method / attribute ambiguity) | same |
| p19 | annotated alias `g: Callable[...] = f` | VIOLATION | Why3 type error | REFUSED R612 |
| p20 | `sorted(xs, key=f)` | VIOLATION | refused (keyword discarded) | REFUSED R612 |
| p21 | lambda wrapping `f` | VIOLATION | **PROVED** | REFUSED R612 |

## 3. The rule and why it was chosen

The check is `PYCSL-R612-CALLABLE-ASSUMED-PURE`, in `src/pycsl/pycsl.py::_run_pipeline`:
- inline, with no new helper;
- placed immediately before the Module 6 transpiler, after every other IR-semantic refusal, so every existing witness keeps its diagnostic;
- the mirror twin of `_run_pipeline` is `\trusted`.

What it refuses:
- It applies to every `symbol_table` name tagged `callable:` (a parameter or an annotated local).
- Such a name may be DECLARED but not REFERENCED anywhere in the function's IR (body, nested lambdas, every contract / assertion / invariant).
- Two cases are refused: a `Call` whose `func` is the name or `<name>.<attr>`, and a `Var` of the name.

Why not a fresh value per call:
- A per-call `any` result removes only assumptions 1-2 (equal calls; a contract application equals the body call).
- Soundness would also need a havoc of every caller-visible location at each call (p04, p14) and a refusal of every `no_exception` / termination claim (p06, p07).
- The census says that machinery would serve 0 programs: the only emitting file that references a Callable parameter is 1878, and its claim is false in CPython (p03).

Why not refuse Callable parameters outright:
- It would also take 1853, 1854 and 6641 (and 10177), whose claims are sound and never mention the callable.

## 4. Witnesses 10170-10179 (x3 memory models)

Logs: `scratchpad/u51/{before,after}{,-typed,-store}/`.

| file | hoare BEFORE / AFTER | typed BEFORE / AFTER | store BEFORE / AFTER |
|---|---|---|---|
| 10170 two calls equal | PROVED / REFUSED | not proved* / REFUSED | not proved* / REFUSED |
| 10171 body vs ensures | PROVED / REFUSED | not proved* / REFUSED | not proved* / REFUSED |
| 10172 requires then call | PROVED / REFUSED | not proved* / REFUSED | not proved* / REFUSED |
| 10173 effect, then `len(xs)` | PROVED / REFUSED | not proved* / REFUSED | not proved* / REFUSED |
| 10174 `f.__call__` (hardening) | Unknown / REFUSED | Unknown / REFUSED | Unknown / REFUSED |
| 10175 annotated alias (hardening) | Why3 type error / REFUSED | type error / REFUSED | type error / REFUSED |
| 10176 method parameter | **PROVED / REFUSED** | **PROVED / REFUSED** | **PROVED / REFUSED** |
| 10177 CONTROL declared-only | PROVED / PROVED | not proved* / not proved* | not proved* / not proved* |
| 10178 CONTROL verified function by name | PROVED / PROVED | not proved* / not proved* | not proved* / not proved* |

\* typed / store: the pre-existing Why3 error "This function depends on external variables, it cannot be used as pure" on a `let function`. It is identical at base and HEAD, and is the same pre-existing class the u50 report records.

Census rows: 10170-10176 are added by `scratchpad/u51/census_rows.py`, which calls `_census_row` from `bin/check-refusal-witness-coverage.py`. Log: `scratchpad/u51/census-rows.log`.
- `--append-new` was NOT used: at base it would have run 507 unrelated expected-FAIL witnesses that have no row. It was started inside phase1, then killed (my process, verified through its parent chain) before it wrote anything.

## 5. Gates (g1 on snapshot worktree `/home/fabrice/git/pycsl-u51-s1` @ `b446e220b`)

Log directory `scratchpad/u51/g1/` (`summary.txt`); the gate script is `scratchpad/u51/gate.sh`, cwd = tree root.

**Corpus byte-diff, root** (`C-root.txt`):
- 3275 baseline vs 3277 candidate; the 2 new files are controls 10177 and 10178;
- **1 MOVED**: `1878`, the intended SOURCE change. Its diff is exactly the removed `requires { (f x) >= 0 }` and body `(f x)` becoming `0`, plus the `(* linear *)` tag on the ensures;
- 0 GONE, 0 APPEARED;
- 1878 re-proved: PROVED (`after/1878*.out`).

**Corpus byte-diff, pyref:** 2185 / 2185, 0 MOVED / 0 GONE / 0 APPEARED.

**Newly refused expected-PASS files:** none. Old 1878 would have been the only one; its claim was false (see p03).

**Mirror sweep** vs `base8/mir`: 53 / 53, **0 diff lines**. No mirror file moved, so no re-proof is owed.

**Fidelity:** sync rc 0, mirror-check rc 0, doc-coherency rc 0.

**Fast planes** (`P-planes.log`, full): **61 / 62**. The single RED is `check-refusal-witness-coverage`: 475 demonstrated / **6** not, against a ceiling of 5. The new raise site had no census row yet. **After the rows** (job2, on the working tree, `scratchpad/u51/coverage2.log`): rc 0, **476 demonstrated / 5** (ceiling 5), 3801 witnesses censused. doc-coherency was re-run on the final tree: rc 0 (`doc2.log`). job2 oom_kill was 5 at its start and 5 at its end; the rise from 0 happened between my jobs, during other executors' jobs, so no result of mine is void.

**Individual planes:** all rc 0.

| plane | result |
|---|---|
| check-getattr-erasure | DECLARED 0, ABSENT 27, UNKNOWN 75 |
| check-claim-vacuity | 1791 at ceiling |
| frontend-only-conformance | rc 0 |
| core-only-conformance | 38 / 38 (IR goldens) |
| check-assigns-writes-survival | rc 0 |
| check-trusted-frame-honesty | rc 0 |
| count-trusted-directives | OK, 367 `\trusted` in `src/self-annotate/src` |

## 6. Residuals

- **Callable FIELDS** (`self.cb: Callable[...]`, then `h.cb(x)`) carry no `callable:` symbol tag, so R612 does not see them. Today they are refused by the Module 6 method / attribute-ambiguity rule (p09, p18). If that rule is ever narrowed, the purity hole reopens for fields.
- `typing-engagement/ty3/conformance_callable/S5_pass.py` and `D1_no_blend.py` (`ensures \result == f(n)`) are now refused. No gate runs them, and their claim is the false claim of 10171. They were left unedited.
- Module-level `Callable`-annotated globals were not probed.
- typed / store: the pre-existing `let function` purity error means no Callable control proves in those models, at base or at HEAD.
