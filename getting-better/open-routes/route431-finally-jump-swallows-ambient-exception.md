# OPEN ROUTE #431: a jump in `finally:` swallows an AMBIENT implicit exception, and a falsified `ensures` is proved

**Status: OPEN, Severity 1.** Found by executor `rg` on 2026-10-28 (driver run #3, wall cycle #2, spike S0 of
`getting-better/dict-value-model-r3-impl.md`). This route is the reason route R-gate (claim-gated `#UND`
hashing refusal) was certified as a boundary instead of built. It refutes the premise that an exception
PyCSL treats as *ambient* (un-modelled, outside every claim) only ends a function **abnormally**.

Carriers (3), gated by `bin/check-open-route-carriers.py` as SUCCESS today:
- `route431-carrier-finally-return-swallows-keyerror.py` (l3n);
- `route431-carrier-finally-return-swallows-hash.py` (l3o);
- `route431-carrier-caller-finally-swallows-callee-hash.py` (l3p).

```
#431 `return` IN A `finally:` TURNS AN AMBIENT EXCEPTION INTO A NORMAL RETURN                (3)
  l3o  #@ requires len(out) == 1  #@ ensures out[0] == 1  #@ assigns out[0]
       def f(m: Dict[str, Any], out: List[int]) -> None:
           out[0] = 2
           try:     n = hash(m.get("a")); out[0] = 1
           finally: return
       base 289fe6029: rc=0 "Verification SUCCESS"          CPython f({"a": [1]}, o): o == [2]
  l3p  the hash in an un-claimed callee `h` (ensures \result == 1), and the caller does
       `out[0] = 2; try: out[0] = h(m) finally: return`
       rc=0 "Verification SUCCESS"                           CPython o == [2]
  l3n  the l3o shape with a KeyError `x = d["a"]` (d: Dict[str, int]) instead of the hash
       rc=0 "Verification SUCCESS"                           CPython f({}, o): o == [2]
  WhyML (l3o): `out[0] <- 2; n := (hash_1 ...); out[0] <- 1; ()`. The `finally` return lowers
  to `()` on the normal path, which is faithful when the try body raises nothing. CPython
  discards the in-flight exception when `finally` executes `return`. No function in either
  witness claims `no_exception`, so every exception here is ambient, and the ambient
  exception becomes a NORMAL return whose state the proved `ensures` misdescribes.
  Not covered by:
    - route #21 (a `finally` WITH handlers);
    - route #156 (a jump in the try BODY of a handler-less try);
    - route #174 (a handler that can catch an un-modelled exception);
    - route #257 (non-inert context managers, incl. contextlib.suppress: probe l3h REFUSED).
  The jump sits in the FINALBODY, which none of them inspects.
  Fail-closed neighbours (probes in systematic-soundness-r3/rg-dict-r3/probes/):
    - l3g / l3j / l3k: `return r` in finally of an `-> int` function, a Why3 type error;
    - l3q: `break` in finally inside a loop, FAILED.
  REPAIR (proposed, not built): refuse a `return` / `break` / `continue` lexically inside a
  `finally:` block (not counting a nested def / class, nor a loop nested in the finally for
  break / continue) in a non-trusted function, inline next to route #156 in `_run_pipeline`.
  PEP 765 makes the same shape a SyntaxWarning in CPython 3.14.
  COST, measured (AST census, systematic-soundness-r3/rg-dict-r3/spike/finally_census.py):
    0 such jumps in 4149 root corpus files, 2217 pyref files, 53 mirrors, 104 pycsl_lib modules.
```
