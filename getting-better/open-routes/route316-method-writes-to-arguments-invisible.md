# OPEN ROUTE #316 — A METHOD'S WRITES TO ITS ARGUMENTS (AND TO MODULE-LEVEL OBJECTS) ARE INVISIBLE TO EVERY CALLER
**Status: OPEN (gen #37, 2026-10-23), Severity 1.** Red-team round 16; driver-reproduced on main eb75cbcf (e13c, e32, e07c, r01, w11 rc=0; CPython violates).
Mechanism: a call to a user method (instance, @staticmethod, `self.` sibling) goes through a generated `val` stub whose `writes` come ONLY
from the method's `assigns` on `self` (no assigns -> `val p_bump_0 () : unit`, not even self); the method body `let p__bump` is checked
only against a frame on `self`'s fields (`ensures { self.n = old self.n }`). A body writing a list parameter (`xs[0] = 5`, `xs[0] += 1`,
forwarding xs to a contracted mutator) or a field of a module-level object verifies, and every caller assumes nothing changed; a
declared `#@ assigns \nothing` / `#@ assigns self.n` is never checked against parameter writes (e32, e06b); a sibling call
`self.poke(self.xs)` mutates the object's own field through the parameter (n05); a subclass override mutating the argument called through
a base-typed variable passes the #277 refinement check because neither declares assigns (r01); method writing a field of module-level
`gq = Q()` (w11; the plain-function twin w12 is faithful). Dict/set params, .append/.reverse/del already fail closed.
Emitted (e13c): `val p_bump_1 (x0: array int) : unit` (no writes) ... `let p__bump (self: p) (xs: array int) : unit ensures { self.n = old self.n } = if Array.length xs > 0 then xs[0] <- 5`.
Repair: make method stubs carry the same frame discipline as plain functions: the method body must be checked against its declared
`assigns` for ALL locations (params, globals, self), the default frame (no assigns) must be inferred/checked like plain functions (or
the call refused), and the stub's `writes` must include every parameter/global location the method may write.
