# OPEN ROUTE #264 — READING A NEVER-ASSIGNED LOCAL IS MODELLED AS 0 (UnboundLocalError IGNORED)

**Status: OPEN (gen #36, 2026-10-17), Severity 1.** Red-team round 3; driver-reproduced at HEAD 13451c8d (s03/s04/s06 rc=0;
CPython UnboundLocalError). Witnesses `witnesses-r264/`: s04 (`if c: y = 1` then `return y`), s03 (`n += 1` with n
unbound), s06 (`del x; return x`), s01/s07 (module global assigned without `global` -> local, read first).
Mechanism: every local is hoisted as `let y = ref 0 in` with no definite-assignment check; `del name` emits `()`.
PyCSL claims normal termination by default, so a raising path proving a postcondition is unsound.
Repair: a definite-assignment analysis (Python scoping: a name assigned anywhere in the function is local); a read
that is not definitely assigned on every path is refused (or an unprovable `assert false` on that path); `del x`
makes x unassigned.
