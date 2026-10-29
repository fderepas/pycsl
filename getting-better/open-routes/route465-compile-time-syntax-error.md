# OPEN ROUTE #465 — COMPILE-TIME SyntaxError not judged: the file is read with ast.parse only, which does not run CPython's symtable / compiler passes, so a module that CPython refuses to COMPILE (late `from __future__`, `global` / `nonlocal` of a parameter, assignment / parameter named `__debug__`, `await` / `yield`-in-comprehension / async comprehension outside their scope, `return <value>` in an async generator, duplicate type parameter, too many statically nested blocks, ...) -- even inside an UNcalled helper -- proves its claimed functions; likewise the PEP 263 coding cookie is ignored (an `ascii` / unknown-encoding cookie over non-ASCII text proves) (SyntaxError before any code runs)
**Status: REPAIRED (executor x2, driver run #3, 2026-10-29), Severity 1.** Red-team round 38 (2026-10-29, on a9eac4a08 after #460-#462: 688 probes / 155 proved / 142 confirmed; rt37's 83 all closed except #463 / #464). Census TSV `scratchpad/rt38/census.tsv`; the family block below is quoted from `scratchpad/rt38/FINDINGS.txt`.
Witnesses `witnesses-r465/` (20): `g1_c100_future_late.py`, `g1_c101_param_global.py`, `g1_c110_assign_debug.py`, `g1_c113_await_outside_async.py`, `g1_c116_in_f_param_global.py`, `g1_c124_typeparam_dup.py`, `g1_c132_yield_in_listcomp.py`, `g1_c138_async_gen_return_value.py`, `g1_c140_debug_param.py`, `g1_c142_typealias_yield.py`, `g1_c144_in_f_debug_assign.py`, `g1_c145_in_f_await.py`, `g1_c148_in_f_yield_comp.py`, `g1_c149_method_param_global.py`, `g1_c152_future_after_docstring_import.py`, `g1_c154_return_value_async_gen_in_f.py`, `g1_c155_nested_blocks_25.py`, `g14_e140_ascii_cookie_nonascii_comment.py`, `g14_e141_unknown_encoding_cookie.py`, `g14_e147_ascii_cookie_nonascii_in_docstring_of_helper.py`.

Driver repro: 17/17 family exemplars (scratchpad/rt38/verify/, F8 without --import-path) rc=0 Verification SUCCESS on main a9eac4a08 at 2026-10-29T14:55Z, each violating under CPython (scratchpad/rt38/driver-repro.txt).

```
F1 COMPILE-TIME SyntaxError not judged: the file is read with ast.parse only, which does not run CPython's symtable / compiler passes, so a module that CPython refuses to COMPILE (late `from __future__`, `global` / `nonlocal` of a parameter, assignment / parameter named `__debug__`, `await` / `yield`-in-comprehension / async comprehension outside their scope, `return <value>` in an async generator, duplicate type parameter, too many statically nested blocks, ...) -- even inside an UNcalled helper -- proves its claimed functions; likewise the PEP 263 coding cookie is ignored (an `ascii` / unknown-encoding cookie over non-ASCII text proves) (SyntaxError before any code runs) (20)
  EXEMPLAR: g1/c116_in_f_param_global.py (`def f(n: int) -> int: global n; return 1`, no_exception \all) and g1/c101_param_global.py (the same `global x` inside an UNcalled helper h)
  CPYTHON: SyntaxError: name 'n' is parameter and global -- the module never compiles; same for every probe of the family (late __future__, __debug__ target / parameter, await / yield-in-comprehension outside scope, return <value> in an async generator, duplicate type parameter, 25 nested blocks) ; g14: a `# -*- coding: ascii -*-` / `coding: zz-unknown` cookie over non-ASCII text (SyntaxError: encoding problem)
  WHY IT PROVES: pycsl reads the file with ast.parse (PyCF_ONLY_AST), which stops before CPython's future / symtable / compiler passes; grep finds no compile() / symtable call in src/pycsl. Of the 53 g1 shapes (51 rejected by CPython's compiler) 17 PROVE under no_exception \all; the other 34 are refused or fail only by accident of an unrelated route (#66 / #180 / #264 / #275 / #301 / #461) or a why3 type error -- no check looks at compilability. The text is also decoded as UTF-8 whatever the PEP 263 cookie says (g14 e140 / e141 / e147 PROVE).
  PROPOSED SYSTEMATIC REPAIR: ONE real-compiler gate, allow-list polarity, no claim gating needed: in Module 1, read the BYTES and decode them with CPython's own `importlib.util.decode_source` / `tokenize.open` (honours the PEP 263 cookie and BOM), then run CPython's own `compile(src, path, 'exec', flags=0, dont_inherit=True, optimize=0)` (which runs future.c, symtable.c and the compiler checks) on the verified file AND on every locally-resolved imported module; any SyntaxError (or ValueError for NUL bytes) is a PIPELINE ERROR naming CPython's message. Witnesses: c100 / c101 / c110 / c113 / c116 / c124 / c132 / c138 / c140 / c142 / c155 (expected refused); control: the same files with the offending line removed (PASS).
  PROBES: g1/c100_future_late.py g1/c101_param_global.py g1/c110_assign_debug.py g1/c113_await_outside_async.py g1/c116_in_f_param_global.py g1/c124_typeparam_dup.py g1/c132_yield_in_listcomp.py g1/c138_async_gen_return_value.py g1/c140_debug_param.py g1/c142_typealias_yield.py g1/c144_in_f_debug_assign.py g1/c145_in_f_await.py g1/c148_in_f_yield_comp.py g1/c149_method_param_global.py g1/c152_future_after_docstring_import.py g1/c154_return_value_async_gen_in_f.py g1/c155_nested_blocks_25.py g14/e140_ascii_cookie_nonascii_comment.py g14/e141_unknown_encoding_cookie.py g14/e147_ascii_cookie_nonascii_in_docstring_of_helper.py
```

## REPAIR (executor x2, driver run #3, 2026-10-29, off daf5c3d1f; annotations §7.290, translational §T.6.300)

Code inline in `_run_pipeline` just before #461's block (mirror twin `\trusted`; no new def, no axiom, no emission
change). NO claim gating (a module that does not compile runs nothing): the bytes of the claimed file are decoded by
CPython's own `tokenize.detect_encoding` (PEP 263 cookie, BOM) -- a decode failure, an unknown encoding, or a decoded
text different from the verified text (read as UTF-8; BOM and newlines normalised) is refused -- then CPython's own
`compile(bytes, file, "exec", dont_inherit=True, optimize=0)` runs (future.c, symtable.c, the compiler); any
SyntaxError / ValueError (or a compiler RecursionError / MemoryError / OverflowError) is refused with CPython's message
and line. A SyntaxWarning is CPython's default (the module runs) and is not refused. Code `PYCSL-R465-COMPILE-ERROR`.

Witnesses 7330-7341 (12 of the 20 red-team files: e140 / e141 cookies, c100 / c101 / c110 / c113 / c116 / c124 /
c132 / c138 / c142 / c155; all 20 of `witnesses-r465/` measured REFUSED with this code). Control 7369 (a `utf-8`
cookie over non-ASCII text, `from __future__ import annotations` after the docstring, a `global` read, `async def` +
`await`, a generator): PROVED at base and candidate. Advice probes `witnesses-r465/advice/` (the `global` dropped; the
cookie made `utf-8`).

OVER-REFUSAL COST, measured (candidate vs base emission of main daf5c3d1f = 33f7ac681's): byte-diff root 2604 -> 2608 .mlw, 0 MOVED / 0 GONE / 0 APPEARED (4 new controls); pyref 2186 / 2186 0/0/0; mirror 53 / 53 0/0/0 (no OWED proof). Static screens: CPython `compile()` + cookie decode of all 6937 corpus / pyref / mirror / pycsl_lib files: only the 12 new #465 witnesses fail; 1274 claimed files scanned for function-body classes, module-dunder reads and dunder attribute reads -- the one PASS file the first cut refused (5590, `class C(B)` over a class `B` of the same def) is admitted by the narrow row below; 0 corpus PASS file refused.


## GATES (routes #465 / #469 / #470 / #471 together, worktree pycsl-x2 off daf5c3d1f, 2026-10-29)
Fidelity: check-self-annotate-sync rc=0 (938 verbatim), self-annotate-mirror-check rc=0 (53). Byte-diff vs
`scratchpad/v13/ca` (emission of 33f7ac681, docs-only since): root 2604 -> 2608 0 MOVED / 0 GONE / 0 APPEARED (4 new
controls); pyref 2186 / 2186 0/0/0; mirror vs `v13/ma` 53 / 53 0/0/0 (no OWED proof). Soundness planes: first run 1 of 61
RED -- check-dropped-mutation CTXBIND 52 > 51, the compile gate's own `with open(..) as` (DIAGNOSED: a new `with ... as`
binding in the scanned emitter; repaired by `pathlib.Path(..).read_bytes()`, not by moving the ratchet), re-run
run-soundness-planes rc=0, 61 / 61 green. Ledgers: trusted-reasons rc=0 (409 <-> 409), assumed-facts --emit-dir rc=0, refusal-witness-coverage rc=0
(365 demonstrated, census +39 rows via `_census_row`), refusal-advice-audited rc=0 (191 / 254, R465 FOLLOWABLE),
dropped-mutation rc=0 (51 ctxbind), getattr-erasure rc=0, open-route-carriers rc=0, trusted-frame-honesty rc=0,
trusted-raises-honesty rc=0, clause-survival --emit-dir rc=0 (10 ledgered), stdlib-modules-verify rc=0, doc-coherency
rc=0. `\trusted` lines 437 (= base). Candidate: 39 witnesses REFUSED, 4 controls + 4 advice probes Verification
SUCCESS. Base daf5c3d1f: 18 sampled witnesses (7330 7333 7336 7341 7342 7343 7344 7345 7349 7350 7351 7355 7356 7360
7361 7364 7365 7367) and the 4 controls Verification SUCCESS. Compile screen (CPython `compile` + cookie decode) of 6937
corpus / pyref / mirror / pycsl_lib files: 12 failures, all the new #465 witnesses; 99 files carry a SyntaxWarning
(refusing warnings would cost them).

## RESIDUALS
- Imported user modules are not compiled here (executor x1 extends #461 across imported modules: #466 / #467 / #468).
- `python -W error` turns a SyntaxWarning into a SyntaxError; the default interpreter does not, and neither does
  this gate.
