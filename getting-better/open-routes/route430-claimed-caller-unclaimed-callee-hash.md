# OPEN ROUTE #430: a `no_exception \all` caller calls an un-claimed callee that hashes an underivable value

**Status: REPAIRED, Severity 1** (executor h430, driver run #3, 2026-10-28; see REPAIR below). Found by executor `rg` on 2026-10-28 (driver run #3, wall cycle #2,
`getting-better/dict-value-model-r3-impl.md` §6 / spike S0). This is the review's `p_claim_calls_unclaimed`
(`dict-value-model-r3-response.md` O7), now proved end to end. It is recorded separately on purpose: route
R-gate (intra-procedural) does not close it and was not widened to do so.

Carrier: `route430-carrier-claimed-caller-unclaimed-hash-callee.py` (probe l3d). It is gated by `bin/check-open-route-carriers.py` as SUCCESS today.

```
#430 CLAIMED CALLER, UN-CLAIMED CALLEE, AMBIENT HASH TypeError                              (1)
  l3d  h(m): s = {m.get("a")}; return 1        (no claim; m: Dict[str, Any])
       #@ no_exception \all  #@ ensures \result == 1
       caller(m): return h(m)
       base 289fe6029: rc=0 "Verification SUCCESS" (full proof, heavy.sh)
       CPython: TypeError: cannot use 'list' as a set element  (caller({"a": [1]}))
  WhyML: `let caller (m) : int ensures { result = 1 } = (h m)`. There is no assert at the call:
  the callee is ambient for every exception the caller does not see (skill
  pycsl-exception-model, "Inter-procedural rules").
  KNOWN exceptions are covered: route #178 refuses a claimed caller of an un-claimed same-file
  callee that may raise KeyError / IndexError / ValueError implicitly (probe l3c's message), and
  route #182 adds ZeroDivisionError for trusted callees. No route covers the TypeError of a
  hashing site, and no route covers a `#UND` hash in an un-claimed callee.
  REPAIR (proposed, not built): extend route #178's transitive callee summary
  (module6_whyml/functions.py ~1563) or the #349 pass with a "may raise TypeError by hashing"
  bit. A same-file function (transitively) holding an underivable (#UND / no-source) hashed leaf
  and not itself claiming `no_exception \all` makes a `no_exception \all` caller REFUSED.
  It must be costed first. R-gate's S1 scan finds 0 claimed mirror functions, so the mirror
  cost is bounded by the claimed callers of #UND-hashing callees, not yet measured.
```

## REPAIR (executor h430, driver run #3, 2026-10-28, off 725a1c7e5 + the route #431 repair 6038e1352; annotations §7.132, translational §T.6.143)

Route #178's callee summary gained the bit, inline where #178 computes it (`_reset_function_state` in
`src/pycsl/module6_whyml/functions.py`, `\trusted` in the mirror):
- **The source of the bit.** The #349-#383 hashing pass in `_run_pipeline` (the same walk as route R-gate,
  annotations §7.131) records every function holding an unguarded hashed leaf whose derived classes contain
  `#UND` or are empty, or a hashed iterable whose elements may be `#UND` (`_und430`; a nested `def`'s site
  counts for the enclosing function too). It reaches Module 6 as `transpiler.und_hash_r430`, kept off the IR
  like `class_bases_r304`.
- **The summary.** Under `no_exception \all`, the active set gains `TypeError`. A function in `und_hash_r430`
  that does not claim `\all` itself gains `TypeError` in its raw summary. The existing transitive closure
  over same-file calls / methods carries it to callers.
- **The refusal.** A call in the claimed body whose callee summary meets only `TypeError` is refused with
  `PYCSL-R430-CALLEE-UNDERIVABLE-HASH`. KeyError / IndexError / ValueError keep route #178's message, so no
  existing census row moves.

Witnesses (expected FAIL), PROVED at base 725a1c7e5 -> REFUSED: 6460 (l3d: `return h(m)`), 6461 (transitive,
`caller -> mid -> h`, `seen.add(m.get("k"))`), 6462 (`return h(m, s, n)` with `h` testing `m.get("a") in s`).
Controls (expected PASS), PROVED at base and candidate: 6463 (the callee hashes a `str`), 6464 (an
un-claimed caller of the same `#UND`-hashing callee). The carrier is REFUSED; its row in
`bin/check-open-route-carriers.py` asserts REFUSED. Not a witness: a method callee with a `Dict[str, Any]`
parameter fails Why3 typing at base (fail-closed), so the shape was replaced by 6462.

**Cost, measured with the sweeps** (combined candidate with route R-gate, byte-diff vs 725a1c7e5): root 0
MOVED / 1 GONE (5069, expected FAIL, now refused by R-gate, not by #430) / 0 APPEARED; pyref 2186 / 2186
0 / 0 / 0; mirrors 53 / 53 0 / 0 / 0 (no mirror refusal, no OWED proof: no mirror function claims `\all`);
`pycsl_lib` screen identical. So no PASS file in any tree has a claimed caller of a `#UND`-hashing callee.

Residual: the bit is computed for functions of THIS file. An imported (`pycsl_lib` or user-module)
function's hashing is not summarised; its body is its own module's business (route #182 covers its
divisions). A dynamic call (a callable value) is not resolved by #178's name matching.

