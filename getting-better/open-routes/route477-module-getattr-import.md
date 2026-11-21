# OPEN ROUTE #477 — PEP 562 MODULE __getattr__ NOT RUN BY THE IMPORT CHECK
**Status: REPAIRED (executor x3, driver run #3, 2026-10-30), Severity 1.** Red-team round 39 (2026-10-29, on d6abee90b after #463-#473: 918 probes + 1064 mode re-proofs / 141 confirmed (probe, mode) pairs; rt38's 142 counted all closed). Census TSV `scratchpad/rt39/census.tsv`; the family block below is quoted from `scratchpad/rt39/FINDINGS.txt`.
Witnesses `witnesses-r477/` (3): `g30_b328_helper_module_getattr_raises.py`, `g38_q721_getattr_raises_attr_for_g.py`, `g38_q724_getattr_plus_def_shadow.py`.

Driver repro: `scratchpad/rp39/repro.sh` (session scratchpad) on d6abee90b, 2026-10-29T23:41Z: all 16 rt39 verify exemplars (2+ per family) rc=0 Verification SUCCESS and CPython breaches, reproduced by the driver.

```
F4 PEP 562 MODULE __getattr__ NOT RUN BY THE IMPORT CHECK (3)
  WHAT: route #466 binds `from M import n` to UNKNOWN as soon as the program module M defines `__getattr__`, without calling it; CPython's from-import first probes `M.__path__` (PyImport_ImportModuleLevelObject suppresses only AttributeError) and then reads n, both through M.__getattr__, so a raising __getattr__ fails the import
  EXEMPLAR: g30/b328_helper_module_getattr_raises.py (h328.py has only `def __getattr__(name): d = {}; return d[name]`; f's module does `from h328 import g`)
  CPYTHON: KeyError: '__path__' at import: CPython's `from h328 import g` first probes `h328.__path__` through __getattr__ (PyImport_ImportModuleLevelObject suppresses only AttributeError) -- the module never imports; q721 (a __getattr__ raising AttributeError) -> ImportError: cannot import name 'g'; q724 a REAL `def g` next to a raising __getattr__ still raises KeyError('__path__').
  WHY IT PROVES: Route #466's from-import binder (pycsl.py:24268-24273): `elif "__getattr__" in _td466: _L466[name] = _UK466` -- a name the program module does not bind is accepted as UNKNOWN as soon as the module defines `__getattr__`, and the function is never called (route #461's older static check, pycsl.py:23762-23764, likewise counts a `def __getattr__` as binding every name). The import machinery's own `__path__` probe is not modelled at all, so even a bound name (q724) passes.
  PROPOSED SYSTEMATIC REPAIR: RUN IT OR REFUSE IT: for a program module (role J / M) whose dict has `__getattr__`, perform the from-import exactly as CPython does -- the `__path__` probe (only AttributeError suppressed), then `getattr(module, name)` -- through the same allow-listed evaluator #466 uses for top-level code (the `__getattr__` placeholder refuses if it would have to run unverified code); if the call cannot be evaluated, REFUSE (PYCSL-R466-IMPORTED-MODULE-RAISES) instead of binding UNKNOWN. Witness: the 3 F4 probes (+ q725, a lambda `__getattr__`, already refused); control: a module without `__getattr__`.
  PROBES: g30/b328_helper_module_getattr_raises.py g38/q721_getattr_raises_attr_for_g.py g38/q724_getattr_plus_def_shadow.py
```

## Repair (executor x3, driver run #3, 2026-10-30)

REFUSE BY DEFAULT, inside route #466's run (`pycsl.py` `_run_pipeline`, inline, mirror twin `\trusted`, no
axiom): a from-import (any name, `*` included -- the check sits before the star branch) of a program module (role
J / M) whose namespace holds `__getattr__` is REFUSED (`PYCSL-R466-IMPORTED-MODULE-RAISES`, message naming route
#477) -- the verifier does not run that function, and CPython calls it for the `__path__` probe and for any
unbound name; and a claimed function's read `h.g` of a name such a module does not bind is refused too (#466's
attribute check used to skip modules with `__getattr__`). All 3 witnesses: PROVED at base 8aaa864ca, REFUSED
(route #477) at the repair. Corpus `7470`-`7473`, control `7474` (no `__getattr__`). annotations.md 7.312.
