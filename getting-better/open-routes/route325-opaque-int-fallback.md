# OPEN ROUTE #325 — EVERY UNMODELLED VALUE FALLS BACK TO AN OPAQUE `int` (whatever its Python type): int-only laws are proved of floats, strings, lists
**Status: OPEN (gen #37, 2026-10-24), Severity 1.** Red-team round 19; driver-reproduced on main (rc=0; CPython violates).
Root cause: the fallbacks `val constant f : int`, `get_X (m) : int`, `getattr_c`, `subscript_get`, and unmodelled calls `val m_f_0 (..) : int`
type an unknown value as INT, so `x % 1 == 0`, `int(x) == x`, `x * 0 == 0`, `x < E or x == E or x >= E+1` are provable of floats/strings/lists.
#322's name-keyed refusal of math/cmath/sys float constants is one symptom and is bypassable (F1). Witnesses `witnesses-r325/` (+ helper consts19.py):
- F1 (#322 bypasses): re-export `consts19.PI` (p01) / `from consts19 import PI` (p02), `importlib.import_module("math").pi` (p03),
  `__import__("math").pi` (p04), `m = math; m.pi` (p05), module-level `M = math` (p07).
- F2 (values): main-file globals `EPS = 0.5` (t06: `x < EPS or x >= EPS+1 or x == EPS` proved, CPython False at x=1), `F = 0.5` (r05),
  annotated `F: float = 0.5` still int (r12), `X = mk()` list (r13), `int(F) == F` with F=2.5 (t03); class attrs `C.R` (c01), `self.R` (c06),
  `Color.RED.value` (c05), `T[0]` of a global float tuple (c07); user-module attrs `consts19.F` (r02), `consts19.S * 0 == 0` (q02).
- F3 (calls): `time.time()` (p08), `random.random()` (q01), `os.getcwd() * 0 == 0` (q03), `float.fromhex` (q07).
FLOAT-FINITE does not cover this (floats are typed int, not real). Repair: an opaque fallback must be typed by the value's known Python type
(literal/annotation/return annotation/stub) — a non-int known type must NOT get int theory: use an abstract opaque type (or real for float
under FLOAT-FINITE) or refuse int arithmetic/comparison over it; an UNKNOWN type must not be assumed int either (refuse int laws over it, or a
fresh abstract type). Census every int-typed opaque fallback emission site; supersede/subsume the #322 name-keyed refusal.
