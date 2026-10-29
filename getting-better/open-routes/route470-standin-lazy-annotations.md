# OPEN ROUTE #470 — m1 STAND-IN OBJECTS lack PEP 649 lazy annotations: a file def / class is a synthesized placeholder at import time, so reading its `__annotations__` (which CPython 3.14 evaluates on first access) does not evaluate an undefined annotation name (NameError at import)
**Status: REPAIRED (executor x2, driver run #3, 2026-10-29), Severity 1.** Red-team round 38 (2026-10-29, on a9eac4a08 after #460-#462: 688 probes / 155 proved / 142 confirmed; rt37's 83 all closed except #463 / #464). Census TSV `scratchpad/rt38/census.tsv`; the family block below is quoted from `scratchpad/rt38/FINDINGS.txt`.
Witnesses `witnesses-r470/` (7): `g6_s649_func_annotations_lazy.py`, `g6_s651_class_annotations_lazy.py`, `g6_s673_method_annotations.py`, `g6_s675_len_class_annotations.py`, `g6_s676_return_annotation_lazy.py`, `g6_s677_ann_undefined_attr.py`, `g6_s678_ann_div_zero.py`.

Driver repro: 17/17 family exemplars (scratchpad/rt38/verify/, F8 without --import-path) rc=0 Verification SUCCESS on main a9eac4a08 at 2026-10-29T14:55Z, each violating under CPython (scratchpad/rt38/driver-repro.txt).

```
F6 m1 STAND-IN OBJECTS lack PEP 649 lazy annotations: a file def / class is a synthesized placeholder at import time, so reading its `__annotations__` (which CPython 3.14 evaluates on first access) does not evaluate an undefined annotation name (NameError at import) (7)
  EXEMPLAR: g6/s649_func_annotations_lazy.py (`def g(x: UndefZZ) -> int: return 1` then `X = g.__annotations__` at module level)
  CPYTHON: NameError: name 'UndefZZ' is not defined at import (CPython 3.14 evaluates a PEP 649 lazy annotation on first access); same for C.__annotations__, C.m.__annotations__, a return annotation, `x: os.zz_none` (AttributeError), `x: 1 // 0` (ZeroDivisionError)
  WHY IT PROVES: m1 binds a file def / class to a synthesized stand-in (a placeholder function / a class built from a synthesized namespace) whose `__annotations__` is not the real lazily-evaluated annotate function of the source, so reading it cannot raise; `inspect.signature` / `annotationlib` / `typing.get_type_hints` are refused (s650 / s617) but a bare attribute read is admitted.
  PROPOSED SYSTEMATIC REPAIR: Allow-list the stand-ins' attributes: a read of `__annotations__` / `__annotate__` / `__signature__` / `__wrapped__` (any dunder not synthesized faithfully) of a file def or class is REFUSED under a claim, or synthesize the real `__annotate__` by compiling each annotation expression and evaluating it in the module namespace m1 has built at the point of the read (what CPython does). Witnesses s649 s651 s673 s675-s678; control: `X = g.__name__` (PASS).
  PROBES: g6/s649_func_annotations_lazy.py g6/s651_class_annotations_lazy.py g6/s673_method_annotations.py g6/s675_len_class_annotations.py g6/s676_return_annotation_lazy.py g6/s677_ann_undefined_attr.py g6/s678_ann_div_zero.py
```

## REPAIR (executor x2, driver run #3, 2026-10-29, off daf5c3d1f; annotations §7.292, translational §T.6.302)

Inside m1's #461 block. Allow-list the stand-ins' attributes: an attribute read, or `getattr` / `hasattr` with a
constant name, is REFUSED for `__annotations__` / `__annotate__` / `__annotate_func__` / `__annotations_cache__` of
anything; for any dunder other than `__name__` / `__qualname__` / `__func__` / `__self__` / `__wrapped__` of a
placeholder def or an object wrapping one (bound method, `staticmethod`, `classmethod`, `property`, an object whose
static `__wrapped__` is one: `lru_cache`, `functools.wraps`); and for `__doc__` / `__firstlineno__` /
`__static_attributes__` / `__type_params__` of a synthesized class or of its instance, and a class's `__dict__`
(none of these is synthesized as CPython builds it). `inspect.*`, `typing.get_type_hints`, `annotationlib` were already
outside the pure set. Code `PYCSL-R461-IMPORT-RAISES`.

Witnesses 7350-7355 (s649 s651 s673 s676 s677 s678; all 7 of `witnesses-r470/` measured REFUSED). Control 7371
(`g.__name__`, `C.m.__qualname__`, a class field): PROVED at base and candidate.

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
- Annotations are still not EVALUATED for real (the refusal is the allow-list option); a dataclass / NamedTuple
  reads its namespace annotations through m1's soft strings (m1's residual).
