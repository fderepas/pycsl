# OPEN ROUTE #310 — A TUPLE VALUE ASSIGNED TO A NAME IS HAVOCKED TO `(any ...)`, DROPPING THE EFFECTS OF CALLS INSIDE IT
**Status: REPAIRED (gen #37, 2026-10-23; opened the same day), Severity 1.** Found by the r307 executor (census); driver-reproduced on main (rc=0; CPython violates).
Witness `witnesses-r310/e_tuple_drop.py`: `xs = [0]; t = (inc(xs), 0); return xs[0]` with `ensures \result == 0` proves (CPython
returns 1); `inc` has `assigns a[0]`. The tuple assignment lowers to the havoc `(any int)` (unused-tuple / erased tuple local) so the
call `inc(xs)` and its write never happen in the model.
Repair direction: never havoc an expression that contains an effectful sub-expression (call with non-empty assigns/raises/unknown,
walrus, yield/await): either emit the effects (evaluate the elements in Python order, then havoc/erase only the VALUE) or refuse.
Census every erasure/havoc site that discards an expression (`any T` for erased values, unused tuple/record locals, discarded
expression statements, #252 erased reads) for effect-dropping.

## REPAIR (2026-10-23, r310 executor off 09e2b7c9; commits 3283ea08 + 9dabe2f8 + 0a031495 + route docs)
**Census first** (probes `p*/q*/r*/a*/e*` in the executor scratchpad `r310/census/`, each `xs = [0]; <shape>; return xs[0]`
with `ensures \result == 0`, CPython 1; `--no-proof` emission at base, then proofs of every candidate): 24 shapes emitted
WITHOUT the call and PROVED at 09e2b7c9; 31 kept the call and FAILED; 13 were already refused (comprehensions, `assert`,
starred/tuple-unpack, computed callee #290, async); 15 were fail-closed L3-tc.

Probe table (`pycsl.py` whole-file, rc; CPython ground truth in each corpus file's `__main__`):

| witness | 09e2b7c9 | after |
|---|---|---|
| 3960 `t = (inc(xs), 0)` (route witness) | PROVED | FAIL |
| 3961 `s = {inc(xs)}` | PROVED | FAIL |
| 3962 `t = (0, inc(xs))` | PROVED | FAIL |
| 3963 `_ = (inc(xs), 0)` | PROVED | FAIL |
| 3964 `t = ((inc(xs), 0), 1)` | PROVED | FAIL |
| 3965 `n = len((inc(xs), 0))` (len folded to 2) | PROVED | FAIL |
| 3966 `n = len([inc(xs)])` (folded to 1) | PROVED | FAIL |
| 3967 `m = max((inc(xs), 0))` (`max_1 (any int)`) | PROVED | FAIL |
| 3968 `v = (inc(xs), 0)[1]` | PROVED | FAIL |
| 3969 `print((inc(xs), 0))` | PROVED | FAIL |
| 3970 `t = (inc(xs), 0) if c else (0, 0)` (conditional arm) | PROVED | REFUSED |
| 3971 `for _ in (inc(xs), 0): pass` | PROVED | FAIL |
| 3972 `d = {1: (inc(xs), 0)}` (dict-literal fold) | PROVED | FAIL |
| 3973 `d[0] = (inc(xs), 0)` | PROVED | FAIL |
| 3974 `ys[0] = (inc(xs), 0)` | PROVED | FAIL |
| 3975 `ys.append((inc(xs), 0))` (`Seq.snoc !ys (any int)`) | PROVED | FAIL |
| 3976 `raise ValueError((inc(xs), 0))` in try/except | PROVED | FAIL |
| 3977 `raise ValueError(inc(xs))` in try/except | PROVED | FAIL |
| 3978 `raise ValueError("m", inc(xs))` (2nd argument dropped by Module 5) | PROVED | REFUSED |
| 3979 `t = (k.bump(), 0)` (method field write) | PROVED | FAIL |
| 3980 `o.m((inc(xs), 0))` on an `Any` receiver | PROVED | FAIL |
| CONTROLS 3981 pure user call `(sq(2), 0)`, 3982 pure reads `(xs[0], 1)`, 3984 pure builtin `(len(xs), 0)` (emission byte-identical), 3983 tuple-returning callee | PASS | PASS |
| CONTROLS (CPython value 1): 3985 `t = (inc(xs), 0)`, 3986 `len((inc(xs), 0))`, 3987 `for` over the display, 3988 `append`, 3989 `raise ValueError(inc(xs))` | FAIL | PASS |

Also measured (not in the corpus, the ID range is full): `p48` annotated `x: Tuple[int, int] = (..)`, `p63`/`p65` rebound
tuple local, `p64` set alias, `p76` `(sum([inc(xs)]), 0)` (now fail-closed L3-tc: the evaluated text is ill-typed),
`p77` `(t, inc(xs))`, `a09` `y = o.m((inc(xs), 0))`, `r14` `raise ValueError(f"{inc(xs)}")` (fail-closed L3-tc: the
f-string guard puts the call in an `assert`), `r22` `raise .. from KeyError(inc(xs))` (REFUSED) — all PROVED at base.

Rule (inline, no new def/field; every touched function's mirror twin is `\trusted`; ledger 3; no IR change). EFFECTFUL
= route #307's predicate (a call not known pure, walrus, `yield`, `await`); at statement sites it is probed exactly as the
#307 dict fold does — "the display is let-sequenced before a copy of itself" — and the abstract-op registry is restored
when the probe says pure (byte-inertness):
- `_expr_to_whyml` (#307 block, now also walking one-operand nodes and `IfExpr` arms without binding them): an effectful
  tuple/set/list/dict display operand that #307 does not bind is lowered once and MARKED with its own text; if the
  re-emitted node no longer contains that text (coerced, `len` folded, dropped by a fallback), the node becomes
  `let _ = <display> in <node>` when every earlier operand is inert or bound and no later one is bound; otherwise (an
  `IfExpr` arm, a display after an unbound non-inert operand) REFUSED ("an effectful expression is erased here (route
  #310)"). `@mutable_state` dict displays are excluded (the #307 residual).
- `_handle_assign_stmt`: an erased tuple/set binding becomes `(let _ = <display> in (any int))` (the display is already
  #307-sequenced); pure ones keep `(any int)`.
- `_handle_array_set_stmt`: an erased stored display is evaluated before the store (`let _ = <display> in` — Python
  evaluates the value first). `_build_dict_literal_map`: an erased value display is evaluated at its fold position.
- `_classify_iterable`: an erased iterable display is materialised once before the loop (`_for_iter_materialize`).
- `_stmts_to_whyml`: an expression-statement call whose lowering drops an effectful display argument evaluates it first
  when every earlier operand is inert; `raise E(a)` evaluates an effectful `a` (Module 5's `exc_value`) before `raise E`.
- `_run_pipeline` (source AST): a `raise` whose second/keyword argument, `from` cause or computed exception contains a
  call (outside `str repr len int float bool type format hex oct bin abs isinstance chr ord`), walrus, `await`, `yield` is
  REFUSED (`PYCSL-SEM-ERASED-EFFECT-R310`).

CENSUS of havoc / erasure / discard sites (site -> effect-dropping? -> verdict):
- tuple/set local binding `(any int)` (`_handle_assign_stmt`; incl. `_`, annotated, rebound, nested, `None`-then-tuple) -> YES -> FIXED (evaluated).
- `GenExp` binding `(any int)` -> NO (lazy; an eager first iterable with a call is already refused, p18) -> safe.
- `UnknownPyExpr` (`(any int)`; children erased in Module 5) -> computed callees refused by #290; `await` refused (async); others are unhandled AST kinds with no call -> safe (a01, #290).
- `_coerce_to_int` tuple / array / map arms (max, subscript, print, `Any`-receiver method args, dict value, stores) -> YES -> FIXED at the consumers (choke point / store / fold); a conditional arm -> REFUSED.
- `len` of a display folded from its shape -> YES -> FIXED (choke point).
- `for` over a display (`iter_length (any int)`) -> YES -> FIXED (materialised).
- `ys.append(<display>)` (`Seq.snoc !ys (any int)`) -> YES -> FIXED; other mutators with a non-inert earlier operand are refused upstream (`insert`, `setdefault`, `update`, computed receivers, field receivers: e01-e09) -> RESIDUAL hoist path unreachable.
- `raise E(a)` -> YES (a dropped) -> FIXED; 2nd/keyword args, `from`, computed exception -> YES -> REFUSED.
- discarded expression statements `(inc(xs), 0)`, `[inc(xs)]`, `inc(xs) + 1`, f-strings, `print(..)`, `str.format`, `str()`, `hash/repr/id/type/callable` of a call, `is None` -> NO (the call is kept; all FAIL at base).
- f-string / format erasures with a call part -> NO (kept or fail-closed L3-tc).
- comprehensions with an effectful element (list/set/dict comp, `sum`/`any` genexp) -> already REFUSED.
- `assert <effectful>` -> already REFUSED (route #84).
- tuple unpacking `a, b = inc(xs), 0` -> already REFUSED.
- record construction `P(inc(xs), 0)` (b01) -> NO (kept; FAIL at base).
- `#252` erased (`Any`) reads/operations (`o.m(inc(xs))`, `o[inc(xs)]`, `o + inc(xs)`) -> NO (argument kept); a display argument -> YES -> FIXED (3980).
- tuple-returning functions / tuple returns -> NO (a real Why3 tuple; #307 sequences it).

Blast radius: corpus root 0 MOVED / 0 GONE / 0 APPEARED (2093 base / 2121 candidate, 28 new sources = the 30 witnesses
minus the 2 refusals); pyref 0/0/0 (2186/2186); mirror 0/0/0 (53/53; a first candidate moved Module3_Weaver and
Module5_IREmitter by probe-registered abstract ops and hoisted `@mutable_state` `(any_map ())` texts — both removed). No
previously-proved corpus file moved, so no latent false proof or regression surfaced.
Gates: witnesses rc=0 -> rc!=0 (table); controls PASS; byte-diff-compare root rc=0, pyref rc=0; mirror-emit-sweep
base/after rc=0, compare `--min-files 50` rc=0 (0 movers, nothing OWED); check-self-annotate-sync.sh rc=0 (926 verbatim);
self-annotate-mirror-check.sh rc=0; run-soundness-planes.sh fast (see README entry); doc-coherency --check rc=0;
check-assumed-facts rc=0; trusted-raises-honesty rc=0 (61 silent, ratchet 61); trusted-frame-honesty rc=0;
check-refusal-witness-coverage rc=0 (257 demonstrated / 5 undemonstrated, ceiling 5; rows for 3960-3980 via
`_census_row`). Ledger 3. Docs: annotations.md §7.8, static-semantics refusal table, translational §T.6.19.
OWED: none (no mirror mover).
Residuals: (1) a statement-level call that drops an effectful display after a non-inert operand keeps its lowering
(measured unreachable: e01-e09 are refused upstream); (2) an evaluated display whose text never type-checked before is now
fail-closed L3-tc (`(sum([inc(xs)]), 0)`, f-string `raise` argument) — completeness, not soundness; (3) `@mutable_state`
dict displays (IR-node constructions, mirror-only) keep `(any_map ())` (the #307 residual); (4) a user exception class
whose `__init__` has effects: `raise E(a)` evaluates `a` but not the constructor; (5) effectful sub-expressions erased
by Module 5 itself into `UnknownPyExpr` beyond #290's computed callees (none found by the probes).
