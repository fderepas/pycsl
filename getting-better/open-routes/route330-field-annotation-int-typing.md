# OPEN ROUTE #330 — INSTANCE FIELDS, MODEL-OP RESULTS AND BARE/COMPLEX ANNOTATIONS TYPED `int` (int laws proved of floats/strs/complex)
**Status: OPEN (gen #37, 2026-10-24), Severity 1.** Red-team round 20; driver-reproduced on main a8dec3db..1333328f (rc=0; CPython violates).
Witnesses `witnesses-r330/`: `self.r = 2.5` then `int(c.r) == c.r` proves (i07; field `{ r = (any int) }`), `c.r % 1 == 0` (a07), `self.r` in a method (i03),
via a parameter `c: C` (i04), `self.s = "ab"` emitted `{ s = 0 }` then `c.s * 0 == 0` (i11); model-op results int-encoded: `repr(n) * 0 == 0` (r02),
`f"{n}" * 0 == 0` (r07); bare `xs: List` / `xs: list` give int elements (d08, e11b; #249 residual); `z: complex` typed int so `z*z != -1` proves
(CPython False for 1j) (e10; #43 only refuses complex LITERALS).
Repair: extend #325's taint to instance fields whose initialiser/annotation is not int, to model-op results that encode non-int values, to
bare/unknown element annotations, and refuse (or type correctly) a `complex` annotation.
