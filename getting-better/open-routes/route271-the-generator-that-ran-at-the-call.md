# OPEN ROUTE #271 — CALLING A GENERATOR FUNCTION RUNS ITS BODY EAGERLY IN THE MODEL

**Status: OPEN (gen #36, 2026-10-17), Severity 1.** Red-team round 4; driver-reproduced at HEAD eced7036 (rc=0; CPython 0).
Witness `witnesses-r271/h05_gen_method_field_eager.py`: method `bump(self) -> Iterator[int]` does `self.n += 1;
yield 0`; `c = C(); c.bump(); return c.n` proves `\result == 1`. `yield` lowers to `let _ = (any int) in ()` and the
function becomes an eager unit procedure whose `ensures self.n == old + 1` (itself false in Python) is applied at the
call.
Repair: a function containing `yield` must not be emitted as an eager procedure: refuse generator functions with
side effects / contracts about state (fail-closed), or model the call as returning an opaque generator with NO
effect, the body's effects happening only on iteration (refuse iteration unless modelled).
