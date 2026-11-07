# OPEN ROUTE #289 — A TUPLE HOLDING A LIST IS OPAQUE AND WRITES THROUGH ITS ELEMENT ARE NO-OPS
**Status: REPAIRED (gen #37, 2026-10-20; opened the same day), Severity 1.** Red-team round 8; driver-reproduced at 8d906404 (rc=0; CPython violates).
Witnesses `witnesses-r289/`. a028 `t: Tuple[List[int], int] = (xs, 0); b = t[0]; b[0] = 5; return xs[0]` proves `== \old(xs[0])` (CPython 5); a025 local variant (`return a[0]` folded to 1). The tuple lowers to `any int` and the store to a no-effect `val subscript_set (x:int)`. Repair: refuse stores/mutation through any value extracted from a tuple/container holding a mutable (or model it); census container-of-mutable shapes.

## REPAIR (2026-10-20, worktree pycsl-rB off 7313506b)
Root cause (located on the emission): a tuple holding a list is erased to `t := (any int)`; an element
taken from it is an int (`b := (subscript_get !t 0)`), and a store through that int reaches the last
fallback of `_handle_array_set_stmt`: `subscript_set !b 0 5` against `val subscript_set (x: int) (i: int)
(v: int) : unit` — no `writes`, no result: a NO-OP. The mutation of the aliased list is absent.

Probe table (`pycsl.py`, rc; base = 7313506b; 22-probe census under `scratchpad/rB/p289`, CPython violates
every claim):

| shape | base | after |
|---|---|---|
| `t: Tuple[List[int], int] = (xs, 0); b = t[0]; b[0] = 5; return xs[0]` (a028 / 3383) | PROVED | REFUSED |
| local twin (a025 / 3384), `t[0][0] = 5` (3385), nested tuple `((a, 0), 0)` (3386), unannotated tuple + `b[0] += 4` (3387), `(a, a)` second slot | PROVED | REFUSED |
| `t = mk(a)` (tuple returned by a call), tuple unpack `b, k = t` / `b, k = (a, 0)`, `List[List[int]]` element, `Dict[int, List[int]]` value, NamedTuple / dataclass field (`t.xs`), `b: List[int] = t[0]` annotated | FAIL (ill-typed, L3-tc) | unchanged FAIL (fail-closed) |
| `t[0].append(5)` / `b.append(5)` / `b.reverse()` on the element | REFUSED (#280 / #283 A / #14) | unchanged |
| partner write `a[0] = 5; return t[0][0]` | FAIL (`subscript_get` of `any int`: unknown) | unchanged FAIL |
| control 3388: a store through the list's own name beside a tuple | PASS | PASS |

Rule (`pycsl.py::_run_pipeline`, a GATE on the emission, next to #269's vanished-call check; new code
`PYCSL-SEM-STORE-THROUGH-OPAQUE-ELEMENT`): any APPLICATION of the abstract `subscript_set` (occurrences
beyond its `val` declaration) is refused, whatever reached it — that op has no modelled effect, so every use
is a dropped mutation. Placed as a gate rather than a `raise` in `_handle_array_set_stmt`, whose mirror stub is
`\trusted` with no `#@ raises` and whose live body raises nothing today (lesson d5: the raise would move
`check-trusted-raises-honesty`); `_run_pipeline` already raises. A faithful model (a tuple of an `array int`
and scalars) is the value-model capability routes #13/#17 need; measured disproportionate to the population
(below).
Census (container-of-mutable shapes): tuple (annotated, unannotated, nested, returned, unpacked), list of
lists, dict of lists, NamedTuple field, dataclass field — the stores that EMITTED all lowered to
`subscript_set` and are refused; the others are ill-typed before and after. Measured population of
`subscript_set` applications at 7313506b: corpus root 1 (0849, a `List[Dict[int,int]]` inner store,
`# pycsl-expected: FAIL`, ill-typed), pyref 0, mirror 0.
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
Residuals: a partner write read back through the tuple (`a[0] = 5; return t[0][0]`) is UNKNOWN (`subscript_get` of
`any int`) and FAILS — sound, incomplete; every other container-of-mutable shape probed (list of lists, dict of
lists, NamedTuple/dataclass field, unpacking, a tuple returned by a call, an annotated element) is ill-typed
before and after (fail-closed by L3-tc, not by this gate). A faithful tuple-of-array model remains the #13/#17
value-model capability.
OWED (base verdicts not measured, slot contention; each emits at base, refuses after): `heavy.sh .venv/bin/python
src/pycsl/pycsl.py <file>` in a worktree at 7313506b for 3378, 3381, 3387 (expected PROVED) and controls 3382/3388/3399
(expected PASS); measured at base: 3370-3374/3379/3380 PROVED, the 14 route witnesses PROVED, the same-shape probes
of 3383-3386/3389-3398 PROVED.
