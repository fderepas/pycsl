# OPEN ROUTE #379 — `**mapping` / `*` ARGUMENTS ARE DROPPED AT CALLS
**Status: OPEN, Severity 1.** Red-team round 29 (2026-10-25, probes around the #226 increment and #369-#372); driver-reproduced on main 919533395 (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt29/driver-repro.txt`).
Witnesses `witnesses-r379/`: `b02_star_kwargs.py`, `b25_kwargs_dict_var_init.py`, `b26_kwargs_plus_pos.py`, `b27_kwargs_value_used.py`, `b47_kwargs_inline_display.py`, `b48_kwargs_explicit_init.py`, `b50_kwargs_param_dict.py`, `b52_kwargs_partial.py`, `b57_kwargs_function_noexc.py`.

`D(**{"x": 5})` lowers to `{ x = 0 }` (b27/b47/b48 prove `.x == 0`, CPython 5); `D(1, **{"y": 7}).y` proves 0 (CPython 7); `D(**kw)` with `kw: Dict[str, int]` under no_exception (b50); unknown / duplicate keys (b02/b25/b26) and a plain function call `h(1, **kw)` (b57) prove no_exception, CPython TypeError. #369's arity residual, now value-unsound.

Repair: Refuse `*` / `**` call arguments unless the mapping / sequence is a literal display expandable to keywords / positionals, then arity-check.
