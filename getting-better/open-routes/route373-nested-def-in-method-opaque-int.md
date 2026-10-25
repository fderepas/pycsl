# OPEN ROUTE #373 — A NESTED `def` IN A METHOD IS LOWERED AS AN OPAQUE `val g_0 () : int`
**Status: REPAIRED, candidate (gen #37, 2026-10-25; r373 executor off dc378283c — erasure, see REPAIR). Was OPEN, Severity 1.** Red-team round 28 (2026-10-25, probes around the #357-#367 repairs); driver-reproduced on main 863a844aa (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt28/driver-repro.txt`).
Witnesses `witnesses-r373/`: `e04_nested_def_sub.py`, `e32_nested_def_default_self.py`, `e37_nested_def_noann.py`, `e63_nested_def_ne.py`, `e64_nested_def_mul.py`, `e79_nd_self_unannotated_eq.py`, `e83_nd_str_mul0.py`, `e84_nd_list_mul0.py`.

A nested def closing over `self` (field-less class) is lowered at the call site to an abstract int, so `t - t == 0`, `t == t`, `t * 0 == 0` prove; R325 catches float / `W()` bodies only. Slips past #357/R325/R252. CPython AssertionError (1, 0, -1).

Repair: Apply the any_ret / R325 erasure to calls of lifted nested defs, or refuse the opaque `val` stand-in.

## REPAIR (2026-10-25, r373 executor off dc378283c, repaired with routes #374 / #375 / #376; code 39d61190 + 9d029328, corpus e8488149 + 0c64cab1, census 98378213, docs f19c7b7a + c037431b (annotations §7.36, translational §T.6.47))
**Design: erase the result (route #249's device), measured mirror-inert.** Module 5 lifts a def nested in a METHOD to a method
of the class (`w__g (self: w)`), so its bare call `g()` resolves to no unit and Module 6 emits the call stub `val g_0 () : int`
— an `int` with every int law whatever `g` returns (the lifted body is never connected to the call). In
`_reset_function_state`'s route #255 resolution (mirror twin `\trusted`, inline), an unresolved plain call spelling that is
the name of a def nested in a method of the file (computed from the source in `_run_pipeline`, `nested_method_defs_r373`) and
the short name of a lifted method joins `any_ret` unless every method so named is annotated `-> int` / `-> bool` (an
unconstrained int over-approximates those). The result is then route #249's arbitrary object: uninterpreted `==` / `!=` /
arithmetic, route #252's refusal into a builtin-typed slot. A nested def in a plain function is lifted to a module function and
resolved normally (unchanged). The opaque-`val` refusal was not needed.
**Probe table** (full proof via heavy.sh; base = dc378283c worktree; CPython violates each, `__main__` ground truth in the corpus file):
| witness | corpus | base | after |
|---|---|---|---|
| e04 `def g() -> "W": return self`, `t - t`, `__sub__` -> 1 | 5050 | rc=0 PROVED | rc=1 REFUSED (R252 flow into `-> int`) |
| e32 `def g(w: "W" = self)` | 5051 | rc=0 PROVED | rc=1 REFUSED |
| e37 unannotated `def g(): return self` | 5052 | rc=0 PROVED | rc=1 REFUSED |
| e63 `t != t`, `__ne__` -> True | 5053 | rc=0 PROVED | rc=1 FAIL (`pycsl_py_ne`) |
| e64 `t * t >= 0`, `__mul__` -> -1 | 5054 | rc=0 PROVED | rc=1 REFUSED |
| e79 unannotated, `t == t`, `__eq__` -> False | 5055 | rc=0 PROVED | rc=1 FAIL |
| e83 `-> str`, `t * 0 == 0` | 5056 | rc=0 PROVED | rc=1 FAIL |
| e84 `-> List[int]`, `t * 0 == 0` | 5057 | rc=0 PROVED | rc=1 FAIL |
| control: nested `-> int` in a method, nested def in a plain function, `t - t == 0` | 5090 | rc=0 PROVED | rc=0 PROVED |
**Blast radius** (base worktree at dc378283c vs candidate 9d029328, `bin/byte-diff-sweep.sh` + `bin/byte-diff-compare.py`,
shared by routes #373-#376): root 2341 base / 2357 candidate, **0 MOVED / 0 GONE / 0 APPEARED** (17 of the 37 new sources
emit, the rest refuse; one GONE in the first compare, `1723_route212_verify_imports_control`, is a resource artefact —
`--verify-imports` proves its dependency inside the emission and timed out under load; it failed the same way at BASE when
re-run standalone, and re-emitted individually via heavy.sh it is byte-IDENTICAL to the base emission); pyref 2186/2186
0/0/0; mirror 53/53 0/0/0 (`bin/mirror-emit-sweep.sh`, `--min-files 50`) — **no mirror mover, no OWED whole-file proof**.
MEASURED on the way (first candidate, then narrowed): the mirror GONE'd `errors.py` (a bare `__str__` call spelling matched a
method's short name: the #373 rule is now keyed on the SOURCE's nested-in-a-method def names), `module6_whyml/expressions` and
`statements` (`getattr(self, "_x", d)` on emitter mixins deriving from IMPORTED mixins: the "outside base = unknown" arm of #376
was dropped, a recorded residual), and MOVED `frontend/pure_ast` (`self.set_precedence(p, *node.comparators)`: a starred CALL
argument is asserted under `no_exception` only). Ledger 3, no new def, one new refusal code
(`PYCSL-R376-GETATTR-CLASS-BINDING`, 2 raise sites, both witnessed), no gate loosened.
**Gates** (one run for routes #373-#376 on the final tree; logs in the executor scratchpad `r373/g/`): witnesses / controls
above (full proof via heavy.sh, base dc378283c vs candidate); byte-diff root + pyref and mirror sweep (above, rc=0 after the
1723 re-emission); `check-self-annotate-sync.sh` rc=0 (926 verbatim); `self-annotate-mirror-check.sh` rc=0 (53);
`check-trusted-reasons` rc=0 (420 / 420, unclassified 259); `check-trusted-raises-honesty` rc=0 (19 / 61, ratchet 61 — the
R376 raises sit in `_lower_getattr`, which has no mirror twin; #373 / #375 add no raise); `check-assigns-underdeclaration
--transitive` rc=0; `check-dropped-mutation` rc=0 (0 / 51 / 5 / 0); `check-refusal-witness-coverage` rc=0 (303 demonstrated,
5 not = ceiling 5; rows 5050-5082 via `_census_row`); `doc-coherency --check` rc=0; `check-getattr-erasure` HEAVYGETATTR;
`check-assumed-facts` HEAVYASSUMED; `run-soundness-planes.sh` (fast) HEAVYPLANES; `check-stdlib-modules-verify` HEAVYSTDLIB.
**Residuals.** (1) A nested `-> int` / `-> bool` def's call is still an unconstrained int stub: its body / contract does not
reach the call (sound, incomplete). (2) Its name is matched file-wide, not per enclosing method (two methods with nested defs of
one name share the decision; conservative). (3) Lambdas bound in a method keep route #255's argument propagation.
