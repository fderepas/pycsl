# ROUTE #156 — a handler-less `finally` is DROPPED when the try body jumps out

**Status: REPAIR DRAFTED by gen #29 (worktree wtH, with #155); battery G pending.** Severity 1.
Generator: continue-census on route #21's own fence ("a `try ... finally:` with NO handlers IS modelled").

## Measured at `52a02d5a`

    x = 0
    try:
        try:
            raise ValueError
        finally:
            x = 7
    except ValueError:
        pass
    return x              #@ ensures \result != 7   <-- PROVED; CPython 7

`_handle_try_stmt` emits a `finally` only when there are no handlers AND `"raise" not in body_str`;
a `return`/`raise`/`break`/`continue` in the body lowers to a `raise`, so the block silently
vanished. Route #21 refused the WITH-handlers half; route #37 refused the jumping `else`.

## Repair

`pycsl.py::_run_pipeline` refuses a handler-less `try/finally` whose body contains a
Return/Raise/Break/Continue in any non-trusted function (PYCSL-R156), before emission — the route
#37 placement, because `_handle_try_stmt` is a converted mirror method. `check-dropped-mutation`
classifies the shape REFUSED; TRYFINAL 9 -> 5. Witnesses 1528/1529 (XFAIL), 1530 (PASS control).
