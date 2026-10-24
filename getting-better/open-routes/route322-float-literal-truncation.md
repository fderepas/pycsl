# OPEN ROUTE #322 — FLOAT LITERALS TRUNCATED TO INT IN abs()/sum() FOLDS; FLOAT MODULE CONSTANTS READ AS OPAQUE INTS
**Status: OPEN (gen #37, 2026-10-23), Severity 1.** Red-team round 18 (stdlib/builtin model); driver-reproduced on main 3b07a838 (rc=0; CPython violates).
Witnesses `witnesses-r322/`: `abs(2.5) == 2` and `abs(0.5) == 0` prove (g01-g03; expressions.py ~12129 `abs(int(val))`); `sum([0.5, 0.5]) == 0`
proves (h01; ~7625 `sum(int(e["value"]) ...)`); `math.pi % 1 == 0` proves through integer `pycsl_mod` (s05; ~17734 generic
`val get_{attr} (x: int) : int`; SEV-2, int-erasure family #62/#64 but a live false proof).
Repair: constant folds must only apply to int literals (never int() a float); a float module constant must be typed real (FLOAT-FINITE) or
refused in int arithmetic; census every literal fold using int() over a value that may be a float.

## REPAIR (2026-10-23, r322 executor off 67edf13c, finished by r322b; commits 6899062d (code + witnesses + docs) + d9a53ce5 (star-import / getattr bypasses) + route docs)
**Census of `int()`-over-a-possibly-float literal folds** (every site the diff touches; the rest of the 30 `(int, float)` tests in
`src/pycsl` compare/dedupe by VALUE — `1 == 1.0` in CPython too — or already exclude a non-integral float (#148/#236)):

| site | before | after |
|---|---|---|
| `expressions.py` `abs(<lit>)` / `int(<lit>)` fold (~12132) | `abs(int(v))` for a float `v` | `abs` folds INT literals only; `int(<finite float>)` keeps its fold (it IS the truncation); `int(inf/nan)` not folded |
| `expressions.py` `sum([<lits>])` (~7620) | `sum(int(e))` over floats | INT literals only |
| `expressions.py` `sum(<known local>)` (~7632) | `int("0.5")` crashed (PIPELINE ERROR) | INT spellings only |
| `expressions.py` affine slice bound (~9656) | `int(v)` for an integral float | INT literal only (a float bound is a CPython TypeError) |
| `types.py` list known-element map (~155) | `str(int(e))` over float elements | INT elements only |
| `types.py` dict known-value map (~247) | `str(int(v))` over float values | INT values only (float value shadows the key) |
| `Module5_IREmitter.py` NamedTuple default (~2981) | `int(2.5)` default | non-integral float is no default (required argument) |
| `Module5_IREmitter.py` `__init__`-annotated default (~3494) | `int(2.5)` default | non-integral float is no default |
| `Module5_IREmitter.py` dataclass default (~3681) | `int(2.5)` default | field UNKNOWN (fails closed) |
| `auto_trust.py` `_extract_array_lengths` (~152) | `int(v)` of an invariant length bound | unchanged: only sizes a `by`-clause witness, whose VC is still proved (no false-proof path) |

**Float module constants: sound refusal** `PYCSL-R322-FLOAT-MODULE-CONSTANT` (`_run_pipeline`, inline, IR walk + module/class-level
bindings read off the parsed source; no IR change, no new def; the `_run_pipeline` mirror is `\trusted`): `math`/`cmath` `pi e tau inf
nan infj nanj` and `sys.float_info`, through `import m [as a]`, `from m import c [as n]`, `from m import *` and `getattr(a, "c")` /
`getattr(a, <non-literal>)` (the last two found by r322b: `from math import *; pi % 1 == 0` and `getattr(math, "pi") % 1 == 0` were still
PROVED through `val constant pi : int` / `pycsl_getattr_missing_* : int`). Typing them `real` is the FLOAT-FINITE model's job.

Probe table (CPython ground truth in each `__main__`; base = 67edf13c; after = d9a53ce5; L3-tc = emitted WhyML rejected by the type
checker, a FAIL):

| witness | CPython | base | after |
|---|---|---|---|
| 4190 abs float literal eq | violates | PROVED* | FAIL (L3-tc, `abs` over a real) |
| 4191 abs float literal return | violates | PROVED* | FAIL (L3-tc) |
| 4192 abs(0.5) == 0 | violates | PROVED* | FAIL (L3-tc) |
| 4193 sum([0.5, 0.5]) == 0 | violates | PROVED* | FAIL (L3-tc) |
| 4194 math.pi % 1 == 0 | violates | PROVED* | REFUSED (#322) |
| 4195 from math import pi | violates | PROVED* | REFUSED (#322) |
| 4196 math.tau local | violates | PROVED* | REFUSED (#322) |
| 4197 module-level PI = math.pi | violates | PROVED* | REFUSED (#322) |
| 4198 sys.float_info | violates | PROVED* | REFUSED (#322) |
| 4199 NamedTuple `r: int = 2.5` | violates | PROVED* | REFUSED (NamedTuple arity: no default) |
| 4203 abs int literal (control) | ok | PROVED | PROVED |
| 4204 int(2.5) == 2 (control) | ok | PROVED | PROVED |
| 4205 sum int literals (control) | ok | PROVED | PROVED |
| 4206 sum int local (control) | ok | PROVED | PROVED |
| 4207 sys.maxsize int (control) | ok | PROVED | PROVED |
| witnesses-r322 g01/g02/g03, h01, s05 | violate | PROVED | FAIL (L3-tc) / FAIL / FAIL / FAIL (L3-tc) / REFUSED |
| scratch t01 `from math import *` / t02 `getattr(math,"pi")` / t03 local import / t04 default param `math.pi` / t12 `cmath.inf` | violate | PROVED (emits) | REFUSED (#322) |

(* 4190-4199 at base: emitted and type-checked (L3-tc ok) at 67edf13c; the PROVED verdict is the r322 executor's measured base
proof of the matching scratch probe (g01-g03, h01, s05, s08, s10, s13, s14, g12), not a re-run of the corpus file — OWED if a
literal base re-proof is wanted.) Scratch probes not in the corpus
(no ids left in 4190-4211): t01/t02 (the bypasses fixed in d9a53ce5), t03/t04/t12 (already refused by 6899062d), t05/t06/t09
(`max(0.5, 0)`, `min(2.5, 3)`, `abs(-0.5)`: L3-tc at base and after), t07 `sum((0.5, 0.5))` (opaque `sum_1 (any int)`, unchanged).
