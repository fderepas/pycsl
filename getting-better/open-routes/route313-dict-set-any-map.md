# OPEN ROUTE #313 — DICT/SET VALUES LOWERED TO `(any_map ())` DROP THEIR EFFECTS (display args, dict-returning calls, field stores)
**Status: REPAIRED (gen #37, 2026-10-23; opened the same day), Severity 1.** Red-team round 15; driver-reproduced on main 65b22999 (rc=0; CPython violates).
Witnesses `witnesses-r313/`: `gd({0: inc(xs)})` (t04), `len({0: inc(xs)})` -> `let _ = (any_map ()) in 1` (i04): a dict display is lowered
faithfully only when the enclosing function returns a map (expressions.py ~21780), otherwise `(any_map ())` — #310's text check
passes vacuously; `gd(mkd(xs))` with Dict-typed param emits `(gd (any_map ()))`, the call vanishes (s09; set variant s02 `gs(mks(xs))`);
field store `k.d = {0: inc(xs)}` / `{**mkd(xs)}` -> `k.d <- (any_map ())` (u01, u07; statements.py ~3285).
Repair: never replace an expression containing an effectful call by `(any_map ())`/`(any_set ..)`: evaluate effects in order then havoc
the value, or refuse. Census every `any_map`/`any_set`/`any_array` emission site.

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
| 4003 i04 `len({0: inc(xs)})` (`let _ = (any_map ()) in 1`) | PROVED | FAIL |
| 4004 s02 `gs(mks(xs))` Set param | PROVED | FAIL |
| 4005 s09 `gd(mkd(xs))` Dict param (`gd (any_map ())`) | PROVED | FAIL |
| 4006 t04 `gd({0: inc(xs)})` | PROVED | FAIL |
| 4007 u01 `k.d = {0: inc(xs)}` field store | PROVED | FAIL |
| 4008 u07 `k.d = {**mkd(xs)}` | PROVED | FAIL |
| CONTROLS 4018 `len({0: inc(xs)})`, 4019 `gd(mkd(xs))`, 4020 `k.d = {0: inc(xs)}`, each then `xs[0] == 1` | FAIL | PASS |

CENSUS of havoc emission sites (`any_map`/`any_set`/`any_array`; no `any_set` is emitted anywhere):
- `_build`-dict fallback `(any_map ())` for a keyed literal (expressions ~21941) -> the DictLit node's own choke point
  evaluates its effectful keys/values (`let _ = (inc xs) in (any_map ())`) -> FIXED (i04, t04, u01).
- call-argument coercion to a map parameter (expressions ~9226) -> the Call's choke point -> FIXED (s02, s09, t04).
- record constructor / dataclass field havocs (expressions ~15807-15885, ~16094-16100) -> constructor arguments pass the
  Call choke point -> FIXED (v02); constructor/`__init__` lowering itself is route #315's (not touched).
- field store `obj.f <- (any_map ())` when the RHS is not map-shaped (statements ~3285, un-trusted mirror twin, not
  edited): measured with probes `c/g01-g08` + h03-h05 — every effectful RHS is either kept (`dict(mkd(xs))`,
  `set(mkl(xs))`, a dict-comp, a display now self-evaluating), fail-closed L3-tc, or REFUSED (`mkd(xs) or {}`, an
  `IfExpr`, `{**k.d, 0: inc(xs)}`, set operators) -> safe, measured unreachable.
- `_coerce_to_int` map arm -> via the choke point (#312).
Residual: the statements ~3285 site keeps its text-keyed decision (unreachable with an effect by the census).

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
