# ROUTE #241 (REPAIRED) — A GENERATOR ACTUAL TO AN `Any` PARAMETER IS THE LITERAL `0`

**Status: REPAIRED (gen #36, 2026-10-15; opened the same day), Severity 1.** Recorded as a residual by the #239 repair executor;
driver-reproduced at HEAD ab2c2d4f (rc=0 "Verification SUCCESS"; CPython `m()` = 0).

## Witness
`witnesses-r241/genexp_actual_is_zero.py`: `g(x: Any)` with `ensures x == 0 ==> \result == 1`;
`m()` returns `g(v for v in [1])` with `ensures \result == 1` PROVES. Emission: `g 0`.

## Mechanism
Route #41's generator erasure (a generator value lowered to the literal `0`), one position over: a call
ACTUAL rather than a local binding (#239 made the local-binding form a fresh `(any int)`).

## Repair direction
An erased generator (or any erased value) in actual position must be a fresh `(any int)` (or refused),
never a definite constant. Census other erased-value-as-constant sites in actual / return / field-store
positions.

## Census — erased values in actual / return / field-store / container-element / default / keyword / compare
positions (each claim false in CPython; "base" = 1e4b380e; probes `scratchpad/r240/q/`)
| value | actual | `== 0` | list element | return `-> Any` | field store | kwarg | default |
|---|---|---|---|---|---|---|---|
| generator `(v for v in [1])` | **PROVED** `g 0` | **PROVED** `0 = 0` | **PROVED** `Array.make 1 (0)` | **PROVED** `= 0` | **PROVED** `c.x <- 0` | **PROVED** | FAIL (default not modelled) |
| set literal / tuple literal | `(any int)` (#239) FAIL | map / tuple term, ill-typed FAIL | FAIL | FAIL | FAIL | `(any int)` FAIL | refused |
| set/list/dict comprehension, `frozenset`, `range` | opaque `*_comp_0` / `frozenset_1` / `py_range_1` val, FAIL | FAIL | FAIL | FAIL | — | — | — |
| lambda | `(fun q -> q)`, ill-typed FAIL | FAIL | FAIL | FAIL | — | — | — |
| bytes literal | array, ill-typed FAIL | FAIL | FAIL | FAIL | — | — | — |
| complex `1j` | refused | refused | refused | refused | — | — | — |
| `UnknownPyExpr` | `(any int)` since #115 | | | | | | |
Only the GENERATOR was exploitable, and in every position: the one shared source is the `GenExp` fallback arm of
`_expr_to_whyml` (`return "0"`). Spec context is unreachable (a generator in a `#@` clause is a PyCSL syntax error).
`Slice` / `SliceExpr` keep `0` (no value position reaches them; baseline rows unchanged).

## Repair landed (gen #36, 2026-10-15)
- `_expr_to_whyml` GenExp arm: `(any int)` (fresh per evaluation, rejected in a logic context), the route-#115
  `UnknownPyExpr` answer. Every position above now reads an unknown value (2242-2247 FAIL on the postcondition).
- `_array_coerce_arg` (converted mirror twin, re-ported VERBATIM into both mirror copies, `expressions.py` and the
  `statements.py` sibling_concrete copy): `(any int)` takes the `0` arm's unconstrained `(any (array int))`, so a
  generator in an array slot (`sorted(...)`, a `List[int]` param) keeps its route-#193 answer instead of an ill-typed
  pass-through.
- `_try_emit_any_all_fold`: an erased iterable spelled `(any int)` declines like `0` (no mirror twin).
- `bin/check-singleton-constant-lowering.py`: the `("_expr_to_whyml", '"GenExp"', "0")` baseline row RETIRED (the
  plane asked for it: the arm no longer answers a constant), with a history note.
No new def, raise, refusal or axiom; ledger 3.

## Witnesses (corpus, `gen36_r240` / `gen36_r241`)
False claims PROVED at 1e4b380e and FAILING after: 2240, 2241, 2249 (#240, post Unknown), 2248 (#240, fail-closed
L3-tc on the contract), 2242-2247 (#241, post Unknown/Timeout). Controls PASS at base and after: 2250
(`isinstance(<bool>, int)` still TRUE), 2251 (`isinstance(<str>, bool)` still FALSE), 2252 (a generator actual
never compared). CPython ground truth: `scratchpad/r240/ground.py` / `ground.log`.

## Gates (logs: `/tmp/claude-1000/.../scratchpad/r240/`)
- Witnesses: `witness_base_final.log` (13/13 rc=0 at base), `witness_after_final.log` (10 FAIL, 3 controls PASS).
- Corpus byte-diff vs a fresh 1e4b380e worktree: root 1560 baseline / 1573 candidate, 0 MOVED, 0 GONE, 0 APPEARED,
  13 new sources; pyref 2198/2198, 1 MOVED (`0140`, `sum(x for x in range(5))`: `sum_1 0` -> `sum_1 (any int)`),
  re-proved FAIL at base and after (its expected verdict).
- Mirror: 4 MOVED — `frontend/module_collect` (`not isinstance(value.value, bool)` was the SAME term as the int test
  just before it, so the branch was DEAD; now the opaque `py_isinstance_bool_int_op`), `frontend/pure_ast` and
  `module6_whyml/expressions` (`join_1`/`sum_1` of a generator: `0` -> `(any int)`), `module6_whyml/{expressions,
  statements}` (`_array_coerce_arg`). All `why3 --type-only` clean; the 7 functions holding a moved line re-proved
  per function (`why3 prove -a split_vc -P z3 -t 30 -G <fn>'vc`): 1010 goals, 0 non-Valid.
- Planes 61/61 (after retiring the singleton row and dropping the bool-declared exception, see route #240).
  Sync rc=0 (915 verbatim), mirror-check rc=0. Ledger 3.

## Residuals (NOT repaired here)
- **A `let function` freezes `(any int)`.** `def r() -> Any: return (v for v in [1])` emits `let function r () :
  int = (any int)`, and Why3 proves `r () = r ()`, so `if r() == r(): return 1` PROVES `\result == 1` while CPython
  compares two distinct generator objects (0) — at base too (`scratchpad/r240/res/rr.py`). Same mechanism as route
  #240's residual 1; it predates this route (route #115's `UnknownPyExpr` and every program `val` in a `let
  function` body share it). Needs its own route.
- A generator DEFAULT argument is not modelled at all (`g()` with `x: Any = <genexp>` FAILS both sides) — not
  exploitable, recorded.
