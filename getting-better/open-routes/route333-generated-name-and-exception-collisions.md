# OPEN ROUTE #333 — #327 RESIDUAL COLLISIONS: user exception names merged by safe_exc_name (incl. with BUILTINS) and generated prefixes (_idx_*) shadowing user names
**Status: REPAIRED (gen #37, 2026-10-24; candidate, see REPAIR), was OPEN (2026-10-24), Severity 1.** Red-team round 21; driver-reproduced on main ec549509 (rc=0; CPython violates).
Witnesses `witnesses-r333/`: `class _ValueError(Exception)` raised, `except ValueError: return 1` under no_exception \all — safe_exc_name strips the `_`, WhyML
`raise ValueError ... with ValueError -> ..`: CPython propagates, pycsl proves no exception (c21); `_E` / `E` user exceptions merge, first arm wins (c01);
the generated loop counter `_idx_<var>` shadows a user local `_idx_i`: read (c02c: user value 5, model reads the counter 0) and write (c02d: writing
`_idx_i = 10` overwrites the counter, loop exits early). R327 only reserves `_tu_*`; other generated prefixes are unreserved: `_len_idx_`, `_any_`,
`_lf_`, `_cc_`, `_csrc_`, `v_`, `r`...
Repair: (a) exception-tag mangling must be injective and disjoint from builtin exception tags (or refuse a user exception class whose mangled
name collides with any other exception tag, builtin or user); (b) reserve EVERY generated identifier prefix/name: census the emitter for
generated binders and refuse user names in those namespaces (extend PYCSL-R327-IDENT-COLLISION), or rename generated binders into a namespace
no Python identifier can produce.

## REPAIR (2026-10-24, r333 executor off 0c2d49cc; commits 432e5fff, 0e8af983, 2448673c (code + corpus), 9ba21f16 (census), e3115268 (docs))
**Design (measured first).** Both repair shapes were priced on the base emission of every file (scratch scripts in the r333 worktree, removed after the run):
| option | root (2203 emitted) | pyref (2186) | mirror (53) |
|---|---|---|---|
| RENAME every generated binder into a namespace no Python name reaches (e.g. a `'`-marked name) | 586 files re-emit (93 for `_idx_` alone) | 12 (3) | 37 (17): whole-file proofs re-OWED |
| blanket refusal of every `_`-prefixed user name in a function | 33 | 1 | 26 (GONE: forbidden) |
| REFUSE a user-spelled name in the CENSUSED generated namespace + exception-tag merges (landed) | 0 | 0 | 0 |
Rule `PYCSL-R327-IDENT-COLLISION` (same code, route #333 text), inline in #327's `_run_pipeline` block before Module 6 (no new
def, mirror twin `\trusted`, ledger 3):
- (a) EXCEPTION TAGS. `safe_exc_name` strips leading underscores. A user EXCEPTION class (a source `class` whose base is a
  builtin `BaseException` subclass or another such class, transitively, or which is named by an IR `exc_type`) is refused when
  its stripped name equals that of ANOTHER source class, an imported name, or a builtin exception name. Kept: a `#@ raises Y`
  tag that is only the stripped spelling of the file's own `_Y` (the mirror's `_ContractSyntaxError` / `raises
  ContractSyntaxError`, measured), and import aliases (`from m import Y as _Y`: no class). A class spelled EXACTLY like a
  builtin is #305's refusal (3780-3785, unchanged).
- (b) GENERATED BINDERS. Every function-scope name of #327's scan (params, `Var` reads incl. globals, binding targets of body and
  contracts) that the USER spelled (a source `Name` / `arg`, or a token of a `#@` line) is refused when `whyml_ident` of it is
  in `_rsv333`. A first cut also read the front end's own IR names and refused 34 root files (`_for_target` of tuple-target
  `for`, `_inl_discard__inl3` of the inliner); a second cut counted a METHOD named `_for_target` (mirror `frontend/pure_ast`)
  as user-spelled — both fixed, measured 0/0/0 after.

**Census of generated identifiers** (empirical: every binder of the 2203 + 2186 + 53 base emissions not equal to a source
name, cross-checked against the emitter's literal / f-string binders):
- RESERVED (scope can enclose user code, or cheap to reserve): prefixes `_idx_` (for-range counter, stmt_control_flow 997),
  `_len_idx_`, `_stop_idx_`, `_hv_idx_`, `_rl_idx_`, `_callit_idx_`, `_split_idx_`, `_seqlit_idx_`, `_pycsl_` (desugar
  `_pycsl_cmp_` / `_pycsl_multi_`, `_pycsl_seq*`, `_pycsl_it310*`, `_pycsl_dk*`/`_pycsl_dv*`, `_pycsl_range_hdr`),
  `__pycsl_` (slice source), `_any_` (havoc `_any_<v>_<k>`, `_any_fold_*`), `_all_fold_`, `_inl_` (inliner), `_tu_` (#327),
  `_u_` (union arm binder), `_lf_`, `_cc_`, `_csrc_`, `_cdf_`, `_mem_`, `_dk_` (contract `in` quantifiers), `_h_f_`,
  `_r230_`, `_r251_` (operand lets), `_class_`, `_union_`, `_pf_`, `_wl<k>c_`, `__and_`, `__or_`, `__happy_`,
  `_for_target`; exact `_alit _u _hl _rec_ _row _ci _celt _si _csl_forall _s_eq _pyobj_state _mi _hin _kin _pin _lin _hln
  _lln _sln _fk _cj _ae _ri _swr _fr _fi _res _mnk _hfm _sfm _nmap __fd __fr`.
- NOT reserved, measured closed (the binder's scope holds only generated text): `_k` (`fun (_k: string) -> false`), `_r`
  (`Some _r -> _r.<label>`), `_v` (`Some _v -> _v` / `disp _v`), `v_` / `r` (#327), the generic-fold helpers' `v_<field>` /
  `l_<name>` (their own `let rec` parameter scope). `_k`, `_r`, `_v` are user names in 3 root + 3 mirror files.
- Top-level generated symbols (`hval_*`, `pycsl_*`, `str_*_op`, `get_<attr>`, `<cls>__<m>` ...): a user top-level name
  equal to one is a Why3 duplicate-symbol error (fail-closed); a user LOCAL equal to one shadows a function and is ill-typed
  at its generated call (fail-closed) — not reserved.
- Single-letter generated quantifier binders (`i`, `x`, `h`, `l`, `k`): probed with a user name of the same spelling in the
  enclosed position (`all(x != i for x in xs)` with param `i`, `[x + k for x in xs]`, `any(x == h and x == l ...)`): all
  three FAIL honestly (rc=1, CPython 1) — no collision observed; RESIDUAL (not proven hygienic).

**Probe table** (full proofs via heavy.sh; CPython rc 1 = contract violated):
| witness | corpus | base | after |
|---|---|---|---|
| c21 `class _ValueError` vs `except ValueError`, no_exception | 4400 | rc=0 PROVED | rc=1 REFUSED R327 (#333) |
| c01 `_E` / `E` merged, first arm wins | 4401 | rc=0 PROVED | rc=1 REFUSED |
| c02c user `_idx_i` read as the counter | 4402 | rc=0 PROVED | rc=1 REFUSED |
| c02d user `_idx_i` write ends the loop | 4403 | rc=0 PROVED | rc=1 REFUSED |
| p01 user `_len_idx_i` beside a for (not filed, truthful main) | - | rc=1 FAIL | rc=1 REFUSED |
| p02 user `_any_x_0` beside a havocked while (not filed) | - | rc=1 FAIL | rc=1 REFUSED |
| control `_Private` alone | 4404 | rc=0 | rc=0 PROVED |
| control `_AErr` / `BErr` | 4405 | rc=0 | rc=0 PROVED |
| control `_i`, `_r`, `idx_i` beside a for | 4406 | rc=0 | rc=0 PROVED |

**Blast radius.** Root 2203 base / 2206 candidate emitted (3 new controls): 0 MOVED, 0 GONE, 0 APPEARED; pyref 2186/2186
0/0/0; mirror 53/53 0/0/0 (`--min-files 50`). No MOVED mirror file, so no L3 type-check and NO OWED whole-file proof.
**Gates** (exit codes; logs in `.r333tmp/`, removed after the run; base sweeps were taken in this worktree at 0c2d49cc before
any edit): byte-diff-compare root rc=0, pyref rc=0, mirror rc=0; check-self-annotate-sync.sh rc=0 (926 functions);
self-annotate-mirror-check.sh rc=0 (53); run-soundness-planes.sh fast 61/61 rc=0; doc-coherency --check rc=0;
check-assumed-facts rc=0 (ledger 3); check-trusted-raises-honesty rc=0 (61 silent, ratchet 61);
check-refusal-witness-coverage rc=0 (281 demonstrated / 5 not, ceiling 5; rows 4400-4403 by `_census_row`, main-tree paths);
check-dropped-mutation rc=0. `--slow` planes NOT run (heavy queue shared).
**Residuals.** (1) exception classes defined in an IMPORTED module (inlined dependencies) are not in the source scan; their
merge with a local class is unmeasured. (2) the generated-binder census is empirical + grep: a future emitter binder outside
`_rsv333` is unguarded until added (the comment at `_rsv333` names this route). (3) single-letter generated quantifier
binders: probed, not proven hygienic. (4) an inlined CALLEE's user local in the reserved namespace is renamed by the inliner
and is not user-spelled in THIS source (checked when that module is verified itself).
