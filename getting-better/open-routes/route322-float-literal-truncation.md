# OPEN ROUTE #322 — FLOAT LITERALS TRUNCATED TO INT IN abs()/sum() FOLDS; FLOAT MODULE CONSTANTS READ AS OPAQUE INTS
**Status: OPEN (gen #37, 2026-10-23), Severity 1.** Red-team round 18 (stdlib/builtin model); driver-reproduced on main 3b07a838 (rc=0; CPython violates).
Witnesses `witnesses-r322/`: `abs(2.5) == 2` and `abs(0.5) == 0` prove (g01-g03; expressions.py ~12129 `abs(int(val))`); `sum([0.5, 0.5]) == 0`
proves (h01; ~7625 `sum(int(e["value"]) ...)`); `math.pi % 1 == 0` proves through integer `pycsl_mod` (s05; ~17734 generic
`val get_{attr} (x: int) : int`; SEV-2, int-erasure family #62/#64 but a live false proof).
Repair: constant folds must only apply to int literals (never int() a float); a float module constant must be typed real (FLOAT-FINITE) or
refused in int arithmetic; census every literal fold using int() over a value that may be a float.
