# OPEN ROUTE #431: a jump in `finally:` swallows an AMBIENT implicit exception, and a falsified `ensures` is proved

**Status: REPAIRED, Severity 1** (executor h430, driver run #3, 2026-10-28; see REPAIR below). Found by executor `rg` on 2026-10-28 (driver run #3, wall cycle #2, spike S0 of
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

## REPAIR (executor h430, driver run #3, 2026-10-28, off 725a1c7e5; annotations §7.130, translational §T.6.141)

`_run_pipeline` (src/pycsl/pycsl.py), inline next to route #156 on the final IR: in a function that is not
`\trusted` / `\abstract` / a trusted parent's helper, a `Try` / `TryStar` whose `finalbody` holds a `Return`
(anywhere), or a `Break` / `Continue` that is not under a `For` / `While` of that `finalbody`, is REFUSED with
`PYCSL-R431-FINALLY-JUMP-SWALLOWS-EXCEPTION`. A nested `def` is lifted to a sibling by Module 5, so its own
`finally:` jump is refused as its own function (witness 6457). The mirror twin of `_run_pipeline` is
`\trusted`; no new `def` in a mirrored file; no WhyML change.

- **Witnesses** (expected FAIL), PROVED at base 725a1c7e5 -> REFUSED: 6450 (l3o, hash), 6451 (l3n, KeyError),
  6452 (l3p, caller's finally over a callee's hash), 6457 (the l3o shape in a nested `def`). FAIL at base
  (Why3 type error, fail-closed) -> REFUSED before lowering: 6453 (`continue` in finally), 6454 (l3q,
  `break` in finally).
- **Controls** (expected PASS), PROVED at base and candidate: 6455 (a jump-free `finally`, `return` after the
  `try`: the message's advice), 6456 (`-> int`, the finally updates a local, `return r` after the `try`).
- **Carriers.** The three #431 carriers are REFUSED; their rows in `bin/check-open-route-carriers.py` now
  assert REFUSED.
- **Cost, re-measured** (byte-diff vs a 725a1c7e5 baseline): root 2512 -> 2514 .mlw, 0 MOVED / 0 GONE /
  0 APPEARED (2 new control sources); pyref 2186 / 2186 0 / 0 / 0; mirrors 53 / 53 0 / 0 / 0; `pycsl_lib`
  --no-proof screen identical (104 files, rc0 87). That is the AST census's 0, measured on emission.

**Other channels that end an exception in a normal return** (probes `c01`-`c10` in
`getting-better/systematic-soundness-r3/h430-r430-431/probes/`, each REFUSED at base and candidate; CPython
returns normally from the swallowed TypeError in every one):

| probe | channel | refused by |
|---|---|---|
| c01 | a file context manager whose `__exit__` returns True | routes #38 / #39 (a `with` over a file context-manager class) |
| c02 / c09 | `except BaseException` in the function / in a caller | route #174 |
| c03 | `except* TypeError` | the desugar refusal (`TryStar` not modelled) |
| c04 / c05 | a nested `def`'s own `except TypeError`, or the outer function catching it | route #174 (the lifted nested function is checked as its own function) |
| c06 | `finally: return` inside a nested `def` | route #431 (this repair); PROVED at base |
| c07 / c08 | a generator's `except BaseException` / `finally: return` (the `close()` / iteration channel) | route #271 (a generator call is not modelled) |
| c10 | `continue` in a loop's `finally` | route #431 (FAIL at base, Why3 type error) |

Together with rg's S0 (`l3a`, `l3b`, `l3f`, `l3i`: #174; `l3c`: #178; `l3h`: #257), no measured channel turns
an ambient exception of an un-claimed function into a normal return any more.

**S0 re-run** (rg-dict-r3/probes/l3*.py, full proofs on the candidate): l3g, l3j, l3k, l3m, l3n, l3o, l3p,
l3q REFUSED by #431; l3a, l3b, l3f, l3i by #174; l3c by #178; l3h by #257; l3e rejected (`no_exception
TypeError` is not a known exception); l3l PROVED, correctly (no jump in its `finally`: the TypeError
propagates and the `ensures` describes normal returns only); l3d PROVED, which is route #430 (a claimed
caller, not a swallow). Logs: `getting-better/systematic-soundness-r3/h430-r430-431/`.

