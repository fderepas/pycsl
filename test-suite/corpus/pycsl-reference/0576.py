"""Test 0576 — module-level global object instance, field read (inline.md Phase 1).

`acc = Account()` at module scope is a single, named, statically-known instance. It is
modeled as a Why3 mutable-record global `let acc : account = { balance = 0 }` (the record
type carries the class invariant + `by` witness). A function reading `acc.balance` lowers
it to the record field and is emitted as a program `let` (NOT a logic `let function` — a
function depending on mutable global state cannot be pure).
"""
# pycsl-flags: --memory-model hoare

#@ class invariant self.balance >= 0
class Account:
    def __init__(self) -> None:
        self.balance: int = 0


acc = Account()


#@ ensures \result == acc.balance
#@ ensures \result >= 0
#@ assigns \nothing
def peek() -> int:
    return acc.balance
