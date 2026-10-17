# OPEN ROUTE #257 — A BARE `with <cm>:` DROPS `__enter__`/`__exit__` WHEN THE CM IS IMPORTED OR A `@contextmanager` METHOD

**Status: OPEN (gen #36, 2026-10-17), Severity 1.** Found by the ch18 re-drain census; driver-reproduced at HEAD
88157755 (both rc=0 "All contracts formally proven"; CPython f() = 1, claims `\result == 0`).

## Witnesses (`getting-better/census-ch18/repro/`)
- `xmod/w2524_bare_with_imported_cm.py` (+ `xmod/cmlib.py`, run with `--import-path .../xmod`): an imported
  context-manager class whose `__enter__` mutates the receiver; emitted body `let c = { n = 0 } in (); c.n`.
- `w2526_bare_with_contextmanager_method_framed.py`: an in-file `@contextmanager` method writing `self.n`.
- True twins w2525 / w2527 fail (completeness); controls w2520/w2521 (CM class in the same file) are refused.

## Mechanism
`Module5_IREmitter._py_stmt_with` lowers a bare `with` to its body; the route #38/#39 guard refuses only when the
SAME FILE defines a context-manager class — imported CM classes and `@contextmanager` generator methods escape it.

## Repair direction
Fail-closed: refuse every bare `with <expr>:` whose CM is not a known-inert builtin (e.g. a lock modelled by the
concurrency layer) — imported classes, `@contextmanager` functions/methods, any call result — or model
`__enter__`/`__exit__` effects. Measure blast radius (the mirror's own `with self.block():` sites).
