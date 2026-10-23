# OPEN ROUTE #314 — KEYWORD ARGUMENTS OF str METHODS ARE DROPPED (with their effects)
**Status: REPAIRED (gen #37, 2026-10-23; opened the same day), Severity 1.** Red-team round 15; driver-reproduced on main 65b22999 (rc=0; CPython violates).
Witnesses `witnesses-r314/`: `'{a}'.format(a=inc(xs))` emits `(format_1 <hash>)` (m07); `'a b'.split(sep=str(inc(xs)))` (n07);
`'abc'.encode(errors=str(inc(xs)))` (o08). Builtins refuse keyword arguments; str methods silently drop them.
Repair: refuse keyword arguments on str (and other builtin-type) methods unless the lowering consumes them faithfully; at minimum
evaluate their effects in order (#307) before the opaque op.

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

Rule (#314, `_reset_function_state`, beside route #275's builtin-keyword scan; `\trusted` twin): a call whose method
name is a public method of str/bytes/bytearray/list/dict/set/frozenset/tuple/int/float, that no user definition
shadows, with a keyword argument is REFUSED ("`.<m>(..., <kw>=...)` is not modelled ... (route #314)"), except
`sort` (gen #36 ch16's in-place havoc; effectful keys refused there) and a STRING-LITERAL `encoding=`/`errors=` of
`encode`/`decode` with at most one positional argument, rewritten to its positional slot (CPython's signature:
`decode('utf-8', errors='ignore')` IS `decode('utf-8', 'ignore')`; `encoding` defaults to 'utf-8'). Even without
the refusal the choke point would evaluate the dropped keyword's effects (measured), but the VALUE ignored the keyword.

| witness | d4e39ef2 | after |
|---|---|---|
| 4009 m07 `'{a}'.format(a=inc(xs))` | PROVED | REFUSED |
| 4010 n07 `'a b'.split(sep=str(inc(xs)))` | PROVED | REFUSED |
| 4011 o08 `'abc'.encode(errors=str(inc(xs)))` (emitted the literal bytes) | PROVED | REFUSED |
| 4012 `'{a}'.format(a=1) == '{a}'.format(a=2)` (keyword value ignored; `format_1` is a fresh `val`, so not provable) | FAIL | REFUSED |
| 4013 `d.get(1, default=1)` (CPython TypeError) | FAIL | REFUSED |
| 4014 `len('a,b'.split(sep=','))` | FAIL | REFUSED |
| corpus 0425 `.decode('utf-8', errors='ignore')` (control, now `decode_2`) | PASS | PASS |

Census (probes `k/k01-k14`): `startswith(prefix=)`, `splitlines(keepends=)`, `split(maxsplit=)`, `replace(count=)`,
`expandtabs(tabsize=)`, `decode(errors=)`, `encode(errors=)`, `format(a=)`, `get(default=)` all dropped the keyword at
base -> REFUSED (string-literal encode/decode rewritten); `sorted(xs, reverse=True)` (builtin, route #275) unchanged;
`xs.sort(reverse=True)` on a local was already refused (in-place mutation).
Residuals: (1) a library-stub class method named like a builtin-type method and not visible as a user definition
would be refused (completeness; none in corpus/pyref/mirror); (2) positional arguments of opaque str methods are
hashed per literal — not this route.

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
