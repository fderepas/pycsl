# OPEN ROUTE #311 — SLICE BOUNDS ARE EVALUATED RIGHT-TO-LEFT (#307 residual 4 is reachable)
**Status: REPAIRED (gen #37, 2026-10-23; opened the same day), Severity 1.** Red-team round 15; driver-reproduced on main 65b22999 (rc=0; CPython violates).
Witness `witnesses-r311/a05b_slice_start.py`: `zs = ys[xs[0]:inc(xs)]` emits `Array.sub ys (xs[0]) ((inc xs) - xs[0])`; Why3 evaluates
the arguments right-to-left so the start bound is read AFTER the call; pycsl proves `zs[0] == 2`, CPython gives 1.
Repair: route slice bounds (start, stop, step) through the #307 let-sequencing (receiver, start, stop, step in Python order) or refuse an
effectful bound; census every slice lowering (Array.sub, array_slice, str substring, slice assignment, del slice).

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

Rule (#311): `SliceAccess` (`ys[lo:hi:st]`) joins #307's n-ary kinds with operands receiver, lo, hi, st (nested path
`("slice", "lo")` supported by the re-emission): `zs = ys[xs[0]:inc(xs)]` -> `let s1 = xs[0] in Array.sub ys s1 ((inc
xs) - s1)`; str slices likewise (`str_sub_op`); an effectful container receiver before an effectful bound is REFUSED
(#307 REFERENCE rule).

| witness | d4e39ef2 | after |
|---|---|---|
| 3990 a05b `ys[xs[0]:inc(xs)]` (route witness) | PROVED | FAIL |
| 3991 `s[xs[0]:inc(xs)]` on a str (near-miss) | FAIL | FAIL (now sequenced) |
| CONTROL 4015 the same slice, CPython value `zs[0] == 1` | FAIL | PASS |

CENSUS of slice lowerings (probes `c/s*`, executor scratchpad `r311/`): Array.sub with effectful upper and non-inert
lower (s01) -> SEQUENCED; str slice (s04/s05) -> SEQUENCED; slice then index `ys[xs[0]:inc(xs)][0]` (s07) erased at base
(`subscript_get (any int)`, call dropped, value havocked) -> now FAIL-CLOSED L3-tc (the sequenced text is no longer
recognised by `_coerce_to_int`'s `Array.sub` prefix); open-ended `ys[inc(xs) - 1:][0]` (s09) -> evaluated; slice
assignment `ys[a:f()] = v` (s02, s10) -> fail-closed L3-tc at base and after; `del ys[0:f()]` (s03) and a step
`ys[0:4:f()]` (s08) -> REFUSED at base and after; `len(ys[0:f()])` (s06) -> fail-closed L3-tc both.
Residuals: (1) s07's completeness loss (fail-closed); (2) slice assignment/del keep their (fail-closed) lowering.

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
(926 verbatim); self-annotate-mirror-check.sh rc=0; run-soundness-planes.sh fast 61/61 rc=0 (first run 59/61, see README); doc-coherency
--check rc=0; check-assumed-facts rc=0; trusted-raises-honesty rc=0; trusted-frame-honesty rc=0;
check-refusal-witness-coverage rc=0 (258 demonstrated / 5, was 257; rows for 3990-4014 via `_census_row`). Ledger 3.
Docs: annotations.md §7.9, static-semantics refusal table, translational §T.6.20.
