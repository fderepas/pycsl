# OPEN ROUTE #331 — `no_exception \all` OVER ARITHMETIC ON A None / str INSTANCE FIELD (CPython TypeError, pycsl proves no exception)
**Status: OPEN (gen #37, 2026-10-24), Severity 1.** Red-team round 20; driver-reproduced on main a8dec3db..1333328f (rc=0; CPython violates).
Witnesses `witnesses-r331/`: `self.r = None` then `c.r * 0` — record `{ r = pycsl_none }` with plain int arithmetic (o09); Optional field `c.r + 1 > c.r`
(o12); str field `c.s - c.s` (o10). Route #230's None guard covers locals and container reads, not fields.
Repair: arithmetic on a field whose declared/initialised type is Optional/None/str (or not provably int) must carry the #230 None/type
obligation under no_exception, or be refused; coordinate with #330's field typing.
