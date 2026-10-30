# OPEN ROUTE #479 — THE `...` LITERAL IS THE INTEGER 0 IN A CONDITIONAL-EXPRESSION TEST (ROUTE #40 RESIDUE)
**Status: REPAIRED (executor o1, driver run #3; see REPAIR below), Severity 1.** Red-team round 39 (2026-10-29, on d6abee90b after #463-#473: 918 probes + 1064 mode re-proofs / 141 confirmed (probe, mode) pairs; rt38's 142 counted all closed). Census TSV `scratchpad/rt39/census.tsv`; the family block below is quoted from `scratchpad/rt39/FINDINGS.txt`.
Witnesses `witnesses-r479/` (7): `g62_b3204_ellipsis_truthy.py`, `g63_e3300_ellipsis_ifexp.py`, `g63_e3302_ellipsis_not_ifexp.py`, `g63_e3308_ellipsis_ifexp_ensures.py`, `g63_e3309_ellipsis_or.py`, `g68_e3810_ellipsis_ternary_value_cmp.py`, `g68_e3812_ellipsis_in_nested_ternary_test.py`.

Driver repro: `scratchpad/rp39/repro.sh` (session scratchpad) on d6abee90b, 2026-10-29T23:41Z: all 16 rt39 verify exemplars (2+ per family) rc=0 Verification SUCCESS and CPython breaches, reproduced by the driver.

```
F6 THE `...` LITERAL IS THE INTEGER 0 IN A CONDITIONAL-EXPRESSION TEST (ROUTE #40 RESIDUE) (7)
  WHAT: route #40 made `...` an opaque `pycsl_ellipsis` only where the IR DICT reaches `_expr_to_whyml` with its `py_ellipsis` marker; the test of a ternary `X if ... else Y` (also `not ...` there, including `not ... or X`, a nested ternary test) and `...` as a ternary VALUE is lowered from the typed `NumberExpr` that `expr_from_dict` built WITHOUT the marker, so it is the literal `0` -- falsy -- while `...` is truthy
  EXEMPLAR: g62/b3204_ellipsis_truthy.py (`#@ no_exception \all`, `return 1 // (n - n) if ... else 1`); g63/e3308_ellipsis_ifexp_ensures.py (`#@ ensures \result == 0`, `return 1 if ... else 0`)
  CPYTHON: b3204: ZeroDivisionError (`...` is truthy, so the division runs); e3308: f() returns 1 -> VIOLATION contract; e3302 `1 if not ... else X` and e3309 `not ... or X` likewise run X.
  WHY IT PROVES: The emitted WhyML is `(if (0 <> 0) then <division> else 1)`: route #40 (module6_whyml/expressions.py:21635-21675) replaced the literal by the opaque `pycsl_ellipsis` ONLY when `_expr_to_whyml` receives the IR DICT carrying Module 5's `py_ellipsis` marker (frontend/Module5_IREmitter.py:1649 `{"type":"Number","value":0,"py_ellipsis":True}`); the route's own comment records that `expr_from_dict` DROPS the marker, and the conditional-expression test (and `not` / boolean operators inside it) is lowered from the typed `NumberExpr` -- so the test is the integer 0 again. The `if` / `while` / variable spellings (e3303, e3304, e3301) are opaque and fail closed, which is how the residue hid.
  PROPOSED SYSTEMATIC REPAIR: CARRY THE SINGLETON IN THE TYPE, NOT IN A DICT KEY: give `...` its own IR node kind (`EllipsisLit`, like `None`), never a `Number`, so no conversion can turn it into 0; until then, allow-list polarity: `expr_from_dict` must REFUSE (not drop) any dict key it does not map, which makes every marker-carrying node fail closed wherever the typed path is taken. Witness: the 5 F6 probes; control: `x = ...; return 1 if x is ... else 0` keeps proving 1.
  PROBES: g62/b3204_ellipsis_truthy.py g63/e3300_ellipsis_ifexp.py g63/e3302_ellipsis_not_ifexp.py g63/e3308_ellipsis_ifexp_ensures.py g63/e3309_ellipsis_or.py g68/e3810_ellipsis_ternary_value_cmp.py g68/e3812_ellipsis_in_nested_ternary_test.py
```

## REPAIR (executor o1, driver run #3, 2026-10-30, off main 8aaa864ca)

**The marker is read on every carrier.** The exact path: Module 5 emits `...` as `{"type":"Number","value":0,
"py_ellipsis":True}`; inside a typed parent (`IfExprExpr.test`, `UnaryOpExpr.expr`, a BoolOp operand, a ternary
arm) `ir_schema.expr_from_dict` keeps that child as an `OpaqueExpr(kind="Number", raw=<dict>)` (its key set differs
from `NumberExpr`'s); route #40's test at the top of `_expr_to_whyml` looked only for a DICT carrying the marker, so
the opaque carrier fell through to the generic dispatch, which re-reads `raw` with `_expr_from_dict_inner` -- a
`NumberExpr(0)` -- and `...` was the literal `0`. The test now reads the node's payload whichever carrier holds it
(`expressions.py`, `_expr_to_whyml`, `\trusted` in the mirror: no mirror body change), so every position lowers
`...` to the opaque `pycsl_ellipsis`. With route #480's repair `pycsl_ellipsis` is also an R325 origin: as an
operand (`(1 if c else ...) + 1`) it is REFUSED; in a truth test / `=` it is opaque and the claim fails closed.
Witness verdicts on c186b936f (`--no-proof` emission + full proof): all 7 NOT-PROVED (Unknown on the guarded
division / postcondition): g62_b3204, g63_e3300, g63_e3302, g63_e3308, g63_e3309, g68_e3810, g68_e3812.
Corpus witnesses 7490-7495 (PROVED at base, FAIL now); controls 7515 (`x = ...; x is ...` proves 1), 7516.
Residual: a truth test of `...` is opaque (fail closed), not modelled as True -- an honest `if ...:` claim
(CPython: always taken) does not prove.
