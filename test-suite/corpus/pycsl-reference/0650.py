"""Test 0650 — `#@ no_inline`: a modular-verification boundary (no-inline.md).

A method on a module-global instance marked `#@ no_inline` is NOT spliced into its callers. Instead
its body is verified once (emitted as a `let`), and each caller reuses its CONTRACT — Module6 lowers
the call as a contract-call to an abstract `val` carrying the callee's result-only `ensures` (resolved
via `_resolve_dotted_signature`'s module-global branch). So `caller` discharges `\result == 7` from
`seven`'s `ensures`, never re-proving `seven`'s body. This avoids re-proving a large body in every
caller's context (the os `sys_write` inlining blow-up). Soundness: the body stays a verified `let`, so
a false `ensures` would fail the callee — nothing is moved into the TCB.
"""


class Lib:
    def __init__(self) -> None:
        self.x: int = 0

    #@ ensures \result == 7
    #@ assigns \nothing
    #@ no_inline
    def seven(self) -> int:
        return 7


_lib = Lib()


#@ ensures \result == 7
#@ assigns \nothing
def caller() -> int:
    return _lib.seven()
