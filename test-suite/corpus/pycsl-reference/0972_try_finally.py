"""Test 0972 — a `finally:` block is part of the function, and dropping it PROVED A FALSE
POSTCONDITION.

Module 6's `_handle_try_stmt` read `stmt.body` and `stmt.handlers` and NEITHER
`stmt.orelse` NOR `stmt.finalbody` — even though Module 5 carries both into the IR. The
cleanup block was simply absent from the model. Measured, before the fix:

    #@ ensures self.v == 1                     <-- FALSE OF THE PROGRAM
    def go(self) -> None:
        try:
            self.v = 1
        finally:
            self.v = 2

    [+] Verification SUCCESS! All contracts formally proven.

The emitted body was `self.v <- 1; ()`. Real Python leaves `self.v == 2`. THREE CONVERTED,
PROVED mirror methods were live victims — `pure_ast.visit_Try`, `pure_ast.visit_TryStar`
and `functions._refine_tuple_return_type` — each a save/restore whose RESTORE was missing
from the model, so the model claimed the saved state was still in place.

THE FIX EMITS THE SAFE CASE AND COUNTS THE REST. Python runs `finally` on EVERY exit path —
normal completion, a caught exception, an uncaught one, `return`/`break`/`continue` — and
only the first is expressible by appending the block, so it is appended exactly when no
other path exists: no handlers, and no `raise` anywhere in the LOWERED body (every jump-out
lowers to a `raise`, so one test of the emitted string covers them all, including nested
ones). Everything else keeps today's behaviour and is counted by
`bin/check-dropped-mutation.py`'s TRYFINAL ratchet.

NEGATIVE TEST: with the emission removed, `ensures self.v == 2` goes Unknown (the model
stops at `self.v <- 1`) and `driver`'s `\\result == 2` with it.
"""
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


class Box:
    #@ requires True
    #@ ensures self.v == 0
    #@ assigns self.v
    def __init__(self) -> None:
        self.v: int = 0

    #@ requires True
    #@ ensures self.v == 2
    #@ assigns self.v
    def go(self) -> None:
        try:
            self.v = 1
        finally:
            self.v = 2


#@ requires True
#@ ensures \result == 2
#@ assigns \nothing
def driver() -> int:
    b = Box()
    b.go()
    return b.v
