# OPEN ROUTE #402 — A USER `__hash__` ON THE STATIC CLASS ITSELF IS NEVER CALLED IN THE MODEL
**Status: OPEN, Severity 1.** Found by executor e1 (run #3, residual of route #395), driver-reproduced 2026-10-26 on the e1+e2
integration tree (rc=0 "Verification SUCCESS"; CPython `ValueError: h`). Witness `witnesses-r402/p1_own_hash_raise.py`:
`class D` defines `def __hash__(self)` that raises when `self.x == 1`; `f(d: D)` builds `{d}` under `#@ no_exception \all`.

Mechanism: a hashing position checks only whether the value's class is HASHABLE (route #349 family / §7.46-§7.50); a class that
defines `__hash__` counts as hashable, and the call to that `__hash__` (and to `__eq__` on a collision) is not emitted, so its
exceptions and preconditions are invisible. #395 (e1) requires a verified `no_exception \all` `__hash__` only on file SUBCLASSES;
requiring it on the static class too refuses PASS controls 4694, 4940, 5043 (measured by e1).

Repair options: (a) lower every hashing position as a call to the class's `__hash__` (with its contract: `raises`, `requires`),
the faithful model; (b) refuse unless the class's `__hash__` is verified `#@ no_exception \all` and give 4694/4940/5043 that
contract (their `__hash__` bodies are total); measure (b) first.
