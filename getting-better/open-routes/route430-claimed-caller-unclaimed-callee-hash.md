# OPEN ROUTE #430: a `no_exception \all` caller calls an un-claimed callee that hashes an underivable value

**Status: OPEN, Severity 1.** Found by executor `rg` on 2026-10-28 (driver run #3, wall cycle #2,
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
