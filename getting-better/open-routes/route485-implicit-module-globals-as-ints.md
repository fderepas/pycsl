# OPEN ROUTE #485 — IMPLICIT MODULE GLOBALS THAT ARE NOT IN dir(builtins) (`__file__`, `__cached__`, `__builtins__`) ARE OPAQUE INTS (ROUTE #480 RESIDUE)
**Status: REPAIRED (executor y3, driver run #3; see REPAIR below), Severity 1.** Red-team round 40 (2026-10-30, on dcf424f75 after #475-#480 repaired / #474 partial: 624 probes + 1009 mode re-proofs / 129 confirmed (probe, mode) pairs on 103 probes; rt39's 141 all closed). Census TSV `scratchpad/rt40/census.tsv`; the family block below is quoted from `scratchpad/rt40/FINDINGS.txt`.
Witnesses `witnesses-r485/` (10): `g86_b9005_dunder_file_plus.py`, `g86_b9007_dunder_builtins_plus.py`, `g90_d9400_file_lt.py`, `g90_d9401_file_neg.py`, `g90_d9404_file_ens_value.py`, `g90_d9405_file_aug.py`, `g90_d9406_cached_plus.py`, `g90_d9407_builtins_lt.py`, `g90_d9412_file_bitand.py`, `g90_d9413_file_pow.py`.

Driver repro: `scratchpad/rp40/repro.sh` (session scratchpad) on dcf424f75, 2026-10-30T07:30Z: all 16 rt40 verify exemplars (2+ per family, F5 under --memory-model typed / store) rc=0 Verification SUCCESS and CPython breaches, reproduced by the driver.

```
F4 IMPLICIT MODULE GLOBALS THAT ARE NOT IN dir(builtins) (`__file__`, `__cached__`, `__builtins__`) ARE OPAQUE INTS (ROUTE #480 RESIDUE) (10)
  WHAT: route #480 made every builtin object an R325 origin, keyed on `dir(builtins)` minus the names the file binds; the module's implicit globals `__file__` (str), `__cached__` (None in a script) and `__builtins__` (a module) are not in `dir(builtins)` and are not bound syntactically, so their `val constant` fallback is still an int with no origin
  EXEMPLAR: g86/b9005_dunder_file_plus.py (`#@ no_exception \all`, `def f(n: int) -> int: return __file__ + n`); g90/d9404_file_ens_value.py (`#@ ensures \result == 0`, `return __file__ * 0`)
  CPYTHON: TypeError: can only concatenate str (not "int") to str (b9005; also `__file__ < n`, `-__file__`, `__file__ & 1`, `__file__ ** 2`, `x = __file__; x += n`); `__file__ * 0` is '' -> VIOLATION contract; `__cached__ + n` TypeError (NoneType); `__builtins__ + n`, `__builtins__ < n` TypeError (module)
  WHY IT PROVES: pycsl.py:21236-21238 (route #480): `_bio480 = {'pycsl_ellipsis'} | {... for _x480 in dir(_bi325) if _x480 not in _bind325 ...}` -- the origin set is built from the builtins MODULE's dir(); `__file__`, `__cached__`, `__builtins__` are module-instance globals CPython inserts into every module's namespace, not attributes of `builtins` (`__name__`, `__doc__`, `__spec__`, `__loader__`, `__package__` ARE in dir(builtins) and are refused: b9006, b9008, b9009). The emitted WhyML is `val constant __file__ : int` ... `(__file__ + n)`.
  PROPOSED SYSTEMATIC REPAIR: ORIGIN = EVERY UNMODELLED FREE NAME: make the origin set the complement of what the emitter MODELS (the known-int `__debug__`, the file's bindings, the emitter-internal pattern variables route #480 measured), not `dir(builtins)`; at minimum add the module-instance globals (`__file__`, `__cached__`, `__builtins__`, `__annotations__`, `__dict__`, `__path__`, `__loader__`) and the class-body / method implicit names (`__module__`, `__qualname__`, `__class__`). Witness: the F4 probes; control: `__debug__ + n` (7517) and `len(print.__doc__) + n` keep proving.
  PROBES: g86/b9005_dunder_file_plus.py g86/b9007_dunder_builtins_plus.py g90/d9400_file_lt.py g90/d9401_file_neg.py g90/d9404_file_ens_value.py g90/d9405_file_aug.py g90/d9406_cached_plus.py g90/d9407_builtins_lt.py g90/d9412_file_bitand.py g90/d9413_file_pow.py
```

## REPAIR (executor y3, driver run #3, 2026-10-30, off main 0c61bfc3f)

**Origin = every name the file never binds (allow-list polarity).** Inline in `_run_pipeline` (`src/pycsl/pycsl.py`,
route #325's block right after #480's builtin-object set; the mirror twin of `_run_pipeline` is `\trusted`, no new def,
no axiom, no new diagnostic code). A Python name that is LOADED somewhere in the file but bound NOWHERE -- no Name
store / del target in any scope, no parameter, def, class, import alias, `global` / `nonlocal`, `except .. as`, match
capture -- is resolved by CPython in the module's own namespace (its implicit globals: `__file__`, `__cached__`,
`__builtins__`, `__annotations__`, `__path__`, `__spec__`, ...) or in builtins, or is a NameError; it is never a value the
file computed, so its R325 fallback is an ORIGIN (`__debug__` stays the one known int; `from m import *` files keep #325's
star rule). This subsumes #480's `dir(builtins)` set and needs no list of CPython's module-namespace keys (the class-body
/ method implicit names `__module__`, `__qualname__`, `__class__` fall under it too). #480's measured exclusion holds:
the emitter-internal pattern variables of corpus 0534 / 0546 are BOUND Python names there, and both files are byte-inert.

Witnesses (10/10 REFUSED, PYCSL-R325-OPAQUE-INT-FALLBACK, all PROVED at base): b9005, b9007, d9400, d9401, d9404, d9405,
d9406, d9407, d9412, d9413. Corpus 7590-7595 (expected FAIL), control 7596 (`len(__file__)`), with #480's 7517 / 7521.
