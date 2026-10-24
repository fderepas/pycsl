# OPEN ROUTE #333 — #327 RESIDUAL COLLISIONS: user exception names merged by safe_exc_name (incl. with BUILTINS) and generated prefixes (_idx_*) shadowing user names
**Status: OPEN (gen #37, 2026-10-24), Severity 1.** Red-team round 21; driver-reproduced on main ec549509 (rc=0; CPython violates).
Witnesses `witnesses-r333/`: `class _ValueError(Exception)` raised, `except ValueError: return 1` under no_exception \all — safe_exc_name strips the `_`, WhyML
`raise ValueError ... with ValueError -> ..`: CPython propagates, pycsl proves no exception (c21); `_E` / `E` user exceptions merge, first arm wins (c01);
the generated loop counter `_idx_<var>` shadows a user local `_idx_i`: read (c02c: user value 5, model reads the counter 0) and write (c02d: writing
`_idx_i = 10` overwrites the counter, loop exits early). R327 only reserves `_tu_*`; other generated prefixes are unreserved: `_len_idx_`, `_any_`,
`_lf_`, `_cc_`, `_csrc_`, `v_`, `r`...
Repair: (a) exception-tag mangling must be injective and disjoint from builtin exception tags (or refuse a user exception class whose mangled
name collides with any other exception tag, builtin or user); (b) reserve EVERY generated identifier prefix/name: census the emitter for
generated binders and refuse user names in those namespaces (extend PYCSL-R327-IDENT-COLLISION), or rename generated binders into a namespace
no Python identifier can produce.
