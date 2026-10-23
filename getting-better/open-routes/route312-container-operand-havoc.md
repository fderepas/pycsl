# OPEN ROUTE #312 — A SLICE / sorted(...) / list_new OPERAND COERCED TO `(any int)` DROPS THE CALLS INSIDE IT (#310 marks displays only)
**Status: REPAIRED (gen #37, 2026-10-23; opened the same day), Severity 1.** Red-team round 15; driver-reproduced on main 65b22999 (rc=0; CPython violates).
Witnesses `witnesses-r312/`: `ys[0:inc(xs)][0]` -> `subscript_get (any int) 0` (d01); sum/max/count/index of a slice (d04, h07);
`for _ in ys[0:inc(xs)]` (d05); `sorted([inc(xs), 0])[0]` (e03); `print(slice)` (i08); unannotated param `g(ys[0:inc(xs)])` (r01);
constructor arg (v02). Mechanism: `_coerce_to_int` (expressions.py ~1175) erases any text starting with `Array.sub`, `array_slice`,
`sorted_1`, `list_new_arr`; #310's effect marking covers tuple/set/list/dict DISPLAYS only.
Repair: apply #310's rule to EVERY erased/coerced expression (evaluate the effectful sub-expressions in Python order then erase the
value, or refuse) — key the check on the IR expression's effectfulness, not on the emitted text prefix.

## REPAIR (2026-10-23, r311 executor off d4e39ef2; commits 9aa6a84d + census + route docs; one family with #311-#314)

SHARED MECHANISM (measured: the chokepoint exists). Route #310's `_expr_to_whyml` block (the one choke point every
operand of a program n-ary node passes through; `\trusted` mirror twin) is generalised from DISPLAY operands to EVERY
effectful operand (route #307's predicate on the IR: a call not known pure, walrus, yield, await). A non-display
operand is NOT marked (its lowering may be position-dependent: a callee's parameter type selects the `.to_dict()`
conversion — marking moved the mirror's `stmt_control_flow`); its standalone lowering is a PROBE (abstract ops it
registers are withdrawn; a probe that raises out of position gives no verdict) and the node is re-emitted unchanged
(`_pycsl_r311n`, stripped on entry, stops the re-entry from probing again). If the probe text is ABSENT from the
node's lowering the operand was erased (coerced to `(any int)`, `(any_map ())`, a dropped receiver/argument/keyword):
it is evaluated first (`let _ = <operand> in <node>`) under #310's position conditions, else REFUSED (conditional arm,
after a non-inert unbound operand, or a not-known-pure call of it RE-DERIVED in the node — it would run twice). It is
left dropped when every not-known-pure call in it lowers to an effect-free abstract `val` (no
writes/raises/requires/reads/diverges), to `(any T)` or to an application-free text (`{ x = 0 }`): nothing to evaluate
in the model (keeps `len(list(chain(a, b)))`, `name.encode().zfill(..)`, `K().m()` byte-identical). `for` over ANY
erased effectful iterable is materialised (`_classify_iterable`, `\trusted` twin). No new def/field; ledger 3; no IR change.

| witness | d4e39ef2 | after |
|---|---|---|
| 3993 d01 `ys[0:inc(xs)][0]` (`subscript_get (any int) 0`) | PROVED | FAIL |
| 3994 d04 `sum(ys[0:inc(xs)])` | PROVED | FAIL |
| 3995 d05 `for v in ys[0:inc(xs)]` | PROVED | FAIL (materialised) |
| 3996 e03 `sorted([inc(xs), 0])[0]` | PROVED | FAIL |
| 3997 h07 `ys[0:inc(xs)].count(1)` | PROVED | FAIL |
| 3998 i08 `print(ys[0:inc(xs)])` | PROVED | FAIL |
| 3999 r01 `g(ys[0:inc(xs)])` unannotated param | PROVED | FAIL |
| 4000 v02 constructor arg `L(ys[0:inc(xs)])` (`{ p = (any_array ()) }`) | PROVED | FAIL |
| 4001 census `max(ys[0:inc(xs)])` | PROVED | FAIL |
| CONTROLS 4016 `ys[0:inc(xs)][0]` then `xs[0] == 1`, 4017 `for` over the slice then `xs[0] == 1` | FAIL | PASS |

Census of `_coerce_to_int` consumers with an effectful slice/sorted operand (probes `c/h17-h24`): `list(slice)` (h17),
list-comp over a slice (h21) keep the call; `ys + slice` (h18), `1 in slice` (h19), `str(slice)` (h22), `len(..) * 0`
(h24) fail-closed L3-tc at base and after; `q.extend(slice)` (h23) REFUSED both; `max` (h20) FIXED.
Residual: an operand whose lowering raises out of position gives no probe verdict (none found).

Blast radius: corpus root 1 MOVED / 0 GONE / 0 APPEARED (2121 base / 2144 candidate, 23 new sources = 29 witnesses
minus 6 refusals): 0425 (`.decode('utf-8', errors='ignore')` -> `decode_2 <utf-8> <ignore>`, route #314's positional
rewrite; re-proved PASS -> PASS); pyref 0/0/0 (2186/2186); mirror 0/0/0 (53/53) — nothing OWED. Intermediate candidates
measured and removed: marking non-display operands (mirror `stmt_control_flow` moved: `stmt_to_pymap` -> `to_emit_ir`),
hoisting model-inert library calls (0530/0547/0548/0588/0589/0598 lost `let function`/gained vals), hoisting dropped
constructor receivers `{ x = 0 }` (1581/1582/1615/2880/2888, pyref 0060), withdrawing a base dead decl (mirror pycsl.py),
refusing `sort(key=..)` (2260 and 5 mirror files via Module1_Ingestor) and `decode(errors=..)` (0425). No previously
proved corpus file fails; no latent false proof surfaced.
Gates: witnesses (tables); controls 4015-4020 FAIL -> PASS; byte-diff-compare root rc=0 (`--expect-moved 0425`), pyref
rc=0; mirror-emit-sweep base/after rc=0, compare `--min-files 50` rc=0 (0 movers); check-self-annotate-sync.sh rc=0
(926 verbatim); self-annotate-mirror-check.sh rc=0; run-soundness-planes.sh fast: see README entry; doc-coherency
--check rc=0; check-assumed-facts rc=0; trusted-raises-honesty rc=0; trusted-frame-honesty rc=0;
check-refusal-witness-coverage rc=0 (258 demonstrated / 5, was 257; rows for 3990-4014 via `_census_row`). Ledger 3.
Docs: annotations.md §7.9, static-semantics refusal table, translational §T.6.20.
