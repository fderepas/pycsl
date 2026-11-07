# OPEN ROUTE #329 — THE `is` REFUSALS (#42, #52) ARE SKIPPED IN AN IF-EXPRESSION TEST AND UNDER `not`
**Status: REPAIRED (gen #37, 2026-10-24; candidate, see REPAIR), was OPEN (2026-10-24), Severity 1.** Red-team round 20; driver-reproduced on main a8dec3db..1333328f (rc=0; CPython violates).
Witnesses `witnesses-r329/`: `x = 1; return 7 if x is True else 0` emits `if (!x = 1)` and proves 7 (b31); `if not (x is True): return 0` (b26, #42's
own exploit wrapped in `not`); int-parameter variants (b41, b42); #52's runtime-built string `b is c` inside an if-expression (b43). The refusal sits in
_expr_to_whyml (expressions.py ~21239) keyed on the `py_is` marker; conditions lowered by the if-expression-test / `not` path never reach it.
Plain `if x is True:`, `return x is True`, `bool(x is True)`, `(x is True) == True`, `x is not True` are refused.
Repair: apply the refusal at every condition-lowering path (if-expression test, not, while/if tests, comprehension filters, assert, boolean
operators) — ideally at the IR level for every Compare with `is`/`is not` whose operands are not None/sentinel-safe.

## REPAIR (2026-10-24, r327 executor off aa1cf01c; commits 329d3a10 (code), edf5b05e (corpus, census, docs) + route docs)
**Root cause (measured on the IR).** The `py_is` marker IS present in every bypass (`If.test = UnaryOp(not, BinOp(==, py_is))`,
`IfExpr.test = BinOp(==, py_is)`). The refusals sat behind `isinstance(expr, dict)`: a ROOT condition reaches `_expr_to_whyml`
as the wire dict, but a nested one is re-read by the typed dispatch (`_expr_from_dict_inner` of the parent), and
`ir_schema.expr_from_dict` turns a child carrying the extra `py_is` key into an `OpaqueExpr` — which skipped the guard and
went through route #249's arm to `_handle_binop` as plain `=`. So EVERY typed parent (`not`, if-expression, `and`/`or`,
comprehension filter, ...) bypassed both #42 and #52, not only the two shapes filed.
**Fix.** In `_expr_to_whyml` (mirror twin `\trusted`), the #42/#52 block now reads `expr.raw` of an opaque `is` node as well as
a wire dict (`_r329_raw`); the rules themselves are unchanged. One choke point covers every lowering position, so no
per-position patch and no IR-level copy of the whitelist (an IR-level refusal would hit the mirror's bespoke tri-state sites,
see route #42). No new def, no new raise site, ledger 3.
**Positions measured** (x = 1 unless noted; base -> after, full proofs):
| shape | corpus | base | after |
|---|---|---|---|
| `return 7 if x is True else 0` (b31) | 4315 | rc=0 PROVED | rc=1 REFUSED #42 |
| `if not (x is True): return 0` (b26) | 4316 | rc=0 PROVED | rc=1 REFUSED #42 |
| param `n == 1`, `7 if n is True else 0` (b41) | 4317 | rc=0 PROVED | rc=1 REFUSED #42 |
| param, `if not (n is True)` (b42) | 4318 | rc=0 PROVED | rc=1 REFUSED #42 |
| `7 if b is c else 0`, run-time-built str (b43) | 4319 | rc=0 PROVED | rc=1 REFUSED #52 |
| `7 if not (n is True) and n == n else 0` | 4320 | rc=0 PROVED | rc=1 REFUSED #42 |
| `elif not (x is not True)` | 4322 | rc=0 PROVED | rc=1 REFUSED #42 |
| `0 if x is not True else 7` | 4323 | rc=0 PROVED | rc=1 REFUSED #42 |
| `while x is True and k < 1` / `if y > 0 and x is True` / `return x < 0 or x is True` / `[v for v in xs if v is True]` | - | rc=1 (already refused / FAIL) | rc=1 |
| `assert x is True` | - | rc=0 | rc=0 — the assert TEST IS ERASED by design (route #84: a failing assert is the aborting path); not an `is` lowering. See residual (2). |
| control `7 if not (x is not None) else 0` (singleton) | 4326 | rc=0 | rc=0 PROVED |
| control `7 if not (x is not x) else 0` (same variable) | 4327 | rc=0 | rc=0 PROVED |

**Blast radius.** Corpus root (2190 base / 2194 candidate emitted, 4 new control sources): 0 MOVED, 0 GONE, 0 APPEARED; pyref
2186/2186 0/0/0; mirror 53/53 0/0/0 (`--min-files 50`) — no OWED proof, no latent false proof. The only existing corpus file whose
outcome text changes is 4260 (#325's lambda case-fold witness, REFUSED before and after; its refusal is now R327 — census row
re-measured). A first cut refused two MIRROR files (`frontend/__init__`, `frontend/ir_resolve`: the inlined dependency
`_subst_var` reads `isinstance(node, Var)` beside its parameter `var`); the class operand of `isinstance` / `issubclass` lowers
to a type tag spelled with the source name, never a variable, and is exempt (2a1e8474) — measured 53/53 after.
**Gates** (exit codes; logs in the r327 worktree, removed after the run): witness tables above (full proofs, heavy.sh);
byte-diff-compare root rc=0, pyref rc=0, mirror rc=0 (base worktree at aa1cf01c, compared once per tree);
check-self-annotate-sync.sh rc=0 (926 functions), self-annotate-mirror-check.sh rc=0 (53); run-soundness-planes.sh fast 61/61
rc=0; doc-coherency --check rc=0; check-assumed-facts rc=0 (ledger 3); check-trusted-raises-honesty rc=0 (61 silent, ratchet 61);
check-refusal-witness-coverage rc=0 (278 demonstrated / 5 not, ceiling 5; rows for 4300-4311, 4315-4323 written by `_census_row`,
paths of the main tree); check-dropped-mutation rc=0. `--slow` planes NOT run (heavy queue shared).
**Residuals.** (1) the #52 blacklist keeps its stated residue (an unannotated local holding a string is not typed `str`). (2) NEW
SUSPECTED FALSE PROOF, outside this route: an `assert` test is erased (route #84) even under `#@ no_exception \all`, so
`x = 1; assert x == 2; return 7` with `no_exception \all` PROVES (CPython: AssertionError) — repro kept at
`/tmp/claude-1000/-home-fabrice-git-pycsl/0119d6ca-595a-4b95-ab54-21d812c2f0f2/scratchpad/r327-assert-noexc-all.py`.
