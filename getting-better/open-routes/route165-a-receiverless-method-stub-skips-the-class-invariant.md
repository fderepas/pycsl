# ROUTE #165 — a receiver-less method stub propagates a postcondition that relies on a broken class invariant

**Status: REPAIR DRAFTED by gen #29 (worktree wtL, on top of battery J's candidate).** Severity 1.

## Measured at `0a9723c0`

    #@ class invariant self.x >= 0
    class C:  def __init__(self): self.x = 1
              #@ ensures \result >= 0
              def get(self) -> int: return self.x
    c = C(); c.x = -5; return c.get()        #@ ensures \result >= 0   PROVED   (CPython -5)

The call lowered to `val c_get_0 () : int ensures { result >= 0 }` — no receiver — so the broken type
invariant of `c` was never checked. Route #70 already withholds a callee's postcondition when it has a
`requires`; a class invariant is the same implicit precondition.

## Repair

For a `<local>.<m>(...)` call whose receiver's class declares invariants and no other path passes the
receiver, the stub takes `(self: <class>)` and the call passes the receiver; Why3 then demands the
invariant at the call. Invariant-preserving controls keep proving. Witnesses 1561 (XFAIL), 1562/1563
(PASS).
