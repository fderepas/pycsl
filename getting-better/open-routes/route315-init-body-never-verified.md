# OPEN ROUTE #315 — `__init__` BODIES ARE NEVER EMITTED OR VERIFIED: CONSTRUCTOR CALLS DROP ARGUMENT MUTATIONS AND CALLEE PRECONDITIONS
**Status: OPEN (gen #37, 2026-10-23), Severity 1.** Red-team round 15; driver-reproduced on main 65b22999 (rc=0; CPython violates).
Witnesses `witnesses-r315/`: `k = K(xs)` lowers to a bare record literal `{ n = 0 }`: `a[0] += 1` in __init__ (j01), `self.n = inc(a)` (j02),
effectful field initialisers (j03-j08 incl. print, if-condition call), explicit `#@ assigns a[0]`/`ensures` on __init__ ignored (j09),
callee precondition inside __init__ never checked: `K([])` calls `first(a)` (`requires len(a) >= 1`) — CPython IndexError, pycsl proves
`== 1` (j11); user exception __init__ mutating its argument (b04, #310 residual 4). Route #150 (draft) covers effects on `self` only.
Repair: verify every user `__init__` as a function (its own contract, default `assigns` = its fields only) and lower `K(args)` as a call to
it (pre-check requires, apply assigns/ensures, build the record from its ensures/body) — or refuse any class whose `__init__` is not
provably effect-free on arguments and precondition-free (pure field initialisation from parameters/literals).
