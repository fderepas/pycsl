# OPEN ROUTE #288 — ELEMENT STORE THROUGH A LIST RETURNED BY A CALL IS NOT SEEN AS ALIASING
**Status: REPAIRED (gen #37, 2026-10-20; opened the same day), Severity 1.** Red-team round 8; driver-reproduced at 8d906404 (rc=0; CPython violates).
Witnesses `witnesses-r288/`. a009/a010/a013: `b = ident2(a); b[0] = 5; return a[0]` proves `== 1` (CPython 5) when the callee is imported (a `val` with a fresh result; also under --verify-imports); a012 same-file \trusted callee; a015/a020/a017/a021 same-file VERIFIED callee with an early return (Return_seq snapshot -> copy). #283 refuses mutator methods / augmented assignment on such aliases but not subscript stores. Repair: element stores (and every write) through a list bound from a call that may return (an alias of) a parameter are refused unless the callee provably returns a fresh list; an imported/trusted callee is "may alias" by default.

## REPAIR (2026-10-20, worktree pycsl-rB off 7313506b)
Root cause (located on the emission of each witness): `b = ident2(a)` lowers to `let b = (ident2 a) in
b[0] <- 5`, and the callee's result is a region DISTINCT from `a` for Why3 whenever the callee is a `val` —
imported (also under `--verify-imports`: the caller still sees the interface `val`), `\trusted`, or a
verified body whose `return` goes through `raise (Return_seq (snapshot x))` (an early return, a return in a
loop: a COPY). #283's partner rule (B) ran only for a SEQ-PROMOTED target and its mutation set was #279's
(mutator methods, augmented assignment; element stores only for a chained temporary), so an element store —
or a store through the partner — was never seen.

Probe table (`pycsl.py`, rc; CPython ground truth in each corpus file's `__main__`; base = 7313506b; census
probes under `scratchpad/rB/p288`):

| shape | base | after |
|---|---|---|
| imported `b: List[int] = ident2(a); b[0] = 5; return a[0]` (a009 / 3370) | PROVED | REFUSED |
| same under `--verify-imports` (a010 / 3371) | PROVED | REFUSED |
| same-file `\trusted` callee (a012 / 3372) | PROVED | REFUSED |
| imported, on a PARAMETER, `\result == \old(a[0])` (a013 / 3373) | PROVED | REFUSED |
| verified callee with an early return (a015 / 3374), `b[0] += 4` (a017 / 3375) | PROVED | REFUSED |
| REVERSE: `b = pick(a, c); a[0] = 5; return b[0]` (a020 / 3376); imported reverse | PROVED | REFUSED |
| return from inside a loop, unannotated `b` (a021 / 3377) | PROVED | REFUSED |
| store in a loop (3379) | PROVED | REFUSED |
| slice store `b[0:1] = [9]` (3378), `b = tid(tid(a))` (3381), store in an `if`, `c = b; c[0] = 5`, `b[1] *= 3`, `b = pick(a, c)` unannotated | emitted (proof verdict OWED, see gates) | REFUSED |
| the alias handed to a WRITING callee `setfirst(b)` (`assigns x[0]`) (3380) | PROVED | REFUSED |
| imported writer `push(b)` | emitted (proof OWED) | REFUSED |
| `del b[0]` | REFUSED (list `del`) | REFUSED (this rule first) |
| `b = a if c > 0 else [9, 9]; b[0] = 5`, `b = a or [9, 9]; b[0] = 5` | FAIL (no-effect `subscript_set`, ill-typed) | REFUSED (#289's gate) |
| controls 3382: FRESH-returning callee with list-free arguments stored through; read-only returned alias | PASS | PASS |
| `b = tid(a); a[1] = 6; return a[1]` (alias never used again) | PASS | REFUSED (coarse, see residuals) |

Rule (inline in `_handle_assign_stmt`, #283's block; mirror twin `\trusted` and already declaring `#@ raises`;
no new def/field; #283's message and code `PYCSL-M6-MUTATION-THROUGH-RETURNED-ALIAS` reused, so its census
rows stand): (i) the PARTNER set is collected for ANY list-valued target — seq-promoted, symbol-table `list`,
or an RHS that `_rhs_yields_array` (an unannotated call returning a list) — instead of only a seq-promoted one;
an index READ of a 1-D list (`make(a[0])`) contributes only its index (a scalar is not the list); (ii) with a
partner set, the flow-sensitive #279 walk now also refuses an ELEMENT STORE, a SLICE STORE and `del` through
any live name (target or partner), and a live name passed as a direct argument to a user/imported function
whose declared `assigns` is not exactly `\nothing` (name-keyed on the last component; a collision only refuses
more; library callees remain #162's). An imported/trusted callee is "may alias" by construction: no freshness
analysis (measured population of the coarse cut: 0, see blast radius).
Census (the family): every store/write form through a call-bound list was probed — element store, augmented
element store, slice store, `del`, store in a loop / `if`, nested call, two-step name alias, reverse-direction
store, writing callee (same-file and imported), conditional / `or` selection (#289's gate) — each REFUSED.
Mutator methods / `+=` on the alias were already #283 (B)/#279. Dict/set aliases bound from a call: the store
lowers through `map_update` on a COPY too, but every probe (`e = idd(d); e[1] = 2`) is ill-typed (fail-closed)
before and after — residual, not reached by this rule.
Blast radius (sweep at the final tree, base = worktree at 7313506b; the emission legs of `bin/byte-diff-sweep.sh` /
`bin/mirror-emit-sweep.sh` run per file through `heavy.sh` — identical flags — because slot 1 was held for hours by
another executor's `--slow` battery): corpus root 0 MOVED / 4 GONE / 0 APPEARED (1841 -> 1840 + 3 new emitting
sources 3382/3388/3399; GONE = 0849 (#289), 1314/1315/1317 (#290), all `# pycsl-expected: FAIL`, now REFUSED; their
census rows re-measured VERIFY-FAIL -> REFUSAL through `_census_row`), byte-diff-compare root rc=0 with exactly
those four `--expect-gone`; pyref 0/0/0 (2186/2186) rc=0; mirror 0/0/0 (53/53) rc=0 — the first mirror run caught
`stmt_control_flow` GONE on the STRING LITERAL `"subscript_set"` in its emission, fixed with a quote guard, re-measured
inert. No mover, so no whole-file re-proof is owed.
Gates (logs under the rB scratchpad): the 14 route witnesses rc=0 -> rc=1 (refused); corpus witnesses
3370-3381/3383-3387/3389-3398 rc=1 after (refused); controls 3382/3388/3399 rc=0 after. check-self-annotate-sync.sh
rc=0 (923 verbatim); self-annotate-mirror-check.sh rc=0 (53); `run-soundness-planes.sh` (fast) rc=0, 61/61 green;
refusal-witness census +27 rows (3370-3398 expected-FAIL) and 4 re-measured, coverage rc=0 (244 demonstrated, 4
undemonstrated, ceiling 5); refusal-advice-audited rc=0; trusted-raises-honesty rc=0 (silent 61 = ratchet: no new
raise in a `\trusted`-stubbed method — `_handle_assign_stmt`, `_handle_call_expr`, `_run_pipeline` already raise);
mirror-coverage rc=0 (549/41 unchanged: no new def). Ledger unchanged (3 axioms); no `\trusted` marker added.
`--slow` battery OWED: `bin/run-soundness-planes.sh --slow` (via heavy.sh; not run — slot contention).
Residuals: coarse by design — a write through the partner while the alias is still LIVE refuses even when the alias
is never read again (`b = tid(a); a[1] = 6; return a[1]`, a PASS before); a FRESH-returning callee given a list
argument is "may alias" (`b = double(a); b[0] = 1` refuses). Measured population of both in root/pyref/mirror: 0
(0 MOVED / 0 GONE). OPEN SIBLING (found by this census, NOT repaired here): a DICT bound from a call,
`e = idd(d); e[1] = 2; return d[1]` with a `\trusted` identity `idd`, EMITS `let e = ref (idd !d) in e :=
map_update_some !e 1 2` — a copy — so `\result == 1` is expected to PROVE (CPython 2); emission measured at base and
after, proof not run (slot contention). Repro: rB scratchpad `p288/dict_alias.py`. Needs the same partner rule over
`_dict_locals`/dict parameters. A callee reached
through a computed callee or a bound-method value is #290's.
OWED (base verdicts not measured, slot contention; each emits at base, refuses after): `heavy.sh .venv/bin/python
src/pycsl/pycsl.py <file>` in a worktree at 7313506b for 3378, 3381, 3387 (expected PROVED) and controls 3382/3388/3399
(expected PASS); measured at base: 3370-3374/3379/3380 PROVED, the 14 route witnesses PROVED, the same-shape probes
of 3383-3386/3389-3398 PROVED.
