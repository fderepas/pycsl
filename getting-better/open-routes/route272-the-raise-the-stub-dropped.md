# OPEN ROUTE #272 — A CALLEE'S UNDECLARED ESCAPING `raise` IS DROPPED AT THE CALL; `no_exception \all` PROVES

**Status: REPAIRED (gen #36, 2026-10-18; opened the same day), Severity 1.** Residual of the #269 repair; driver-reproduced at HEAD 6859202e (rc=0;
CPython raises ValueError for `C().m(1)`).
Witness `witnesses-r272/selfcall_undeclared_raise_no_exception.py`: `chk(k)` raises ValueError for k > 0 without
`#@ raises`; `m` (`no_exception \all`) calls `self.chk(k)` and proves. With a declared `#@ raises` the call is
correctly asserted.
Mechanism: undeclared exceptions use the partial-correctness reading for the callee itself, but the caller's stub
(`val self_chk_...`) carries no `raises`, so a `no_exception` caller never sees the possible exception.
Repair: a callee whose body may raise (any modelled raise site, declared or not) must expose that at every call
site under `no_exception` (refuse, or an unprovable obligation), for every call form (self./obj./Class./function).

## Repair (gen #36, 2026-10-18)

### Probe table (measured at 5fe6cbdd; CPython raises ValueError in every row but the controls)

| shape | base | after |
|---|---|---|
| `self.chk(k)`, `chk` raises undeclared, caller `no_exception \all` (witness; 2940) | PROVED | refused |
| `c.chk(k)`, `c: C` parameter (2941) | PROVED | refused |
| `C.chk(k)`, `@staticmethod` (2942) | PROVED | refused |
| `C().chk(k)`, fresh receiver (2943) | PROVED | refused |
| `self.d.chk(k)`, field receiver (2944) | PROVED | refused |
| chain `m -> self.mid -> self.chk`, `mid` has nothing to declare (2945) | PROVED | refused |
| chain `m -> f (module fn) -> C().chk` (2946) | PROVED | refused |
| `C.chk(k)` static, `raises ValueError when k > 0` DECLARED (2947) | PROVED | refused |
| `C().chk(k)`, DECLARED (2948) | PROVED | refused |
| `mid` DECLARES `raises ValueError when k < 0` but a ValueError reaches it through `self.chk` (2949) | PROVED | refused |
| named `no_exception ValueError` over `self.chk(k)` (2950) | PROVED | refused |
| control: declared `self.chk`, caller `requires k <= 0` (2951) | PASS | PASS |
| control: call caught by `except ValueError`; `no_exception KeyError` untouched by a ValueError (2952) | PASS | PASS |
| control: module function `chk(k)` raising (2953) — Why3 effect typing ("raises unlisted exception") | FAIL | FAIL (rule silent) |
| `super().chk(k)` | refused (route #161) | same |
| `C(k)` whose `__init__` raises, directly or through `mk(k)` | refused (route #179) | same |
| imported method `d.chk(k)` | refused (route #207, bodyless) | same |
| imported module function `chk(k)` | FAIL (its stub carries the `raises` its body shows) | same |

### Rule (inline in `pycsl._run_pipeline`, after route #243; mirror twin `\trusted`)
`PYCSL-SEM-UNDECLARED-CALLEE-RAISE` (ir-semantic, refused). HIDDEN(call) = what the callee may raise
that the call site cannot see:
* METHOD callee: its escaping undeclared `raise`s (handler-aware within the callee; a bare / computed
  `raise` is UNKNOWN), plus its DECLARED `raises` when the receiver form is not one the route
  #100/#105/#186 wrap resolves (`self.…`, or a variable bound to a class of this unit: class-typed,
  constructor-bound local, module-global instance) — i.e. `C.m(...)` and `C().m(...)` — plus
  HIDDEN-OUT of the callee;
* module-function callee: HIDDEN-OUT only (its own `raise` is seen by Why3's effect typing);
* HIDDEN-OUT(g) = union of HIDDEN over g's calls not caught by an enclosing handler of g, to a fixed
  point. A declared `raises` on g does NOT excuse an exception arriving that way (the hidden path never
  checks g's condition — 2949).
A function claiming `no_exception` (`\all`: any exception; a named list: a listed class, a subclass,
or a name outside the modelled hierarchy) with a call whose HIDDEN set it covers, outside a handler
that catches it, is refused. Callees are resolved on route #263's call graph (an unresolved receiver
names every method of that name — over-approximation). `\trusted` / `\abstract` / imported callees
speak by their contract only. Nothing is computed when no function of the unit claims `no_exception`.
Ledger 3; no new def.

### Imported callees (documented)
An imported module function's stub carries `raises { E }` for its own escaping raise (FAIL as for an
in-unit function); an imported METHOD is bodyless here and route #207 refuses it under `no_exception`.
RESIDUAL (measured, still PROVES after): an imported function whose exception arrives through a stub
INSIDE the dependency is not seen by the importing unit — `libx272.py`: `class D` with `chk` raising
ValueError undeclared, `def f(k): return D().chk(k)`; main `from libx272 import f`, `m(k)` with
`#@ no_exception \all`, `f(k); return 7`. `f`'s stub carries no `raises` (its body has no raise of
its own) and imported bodies are not walked by this rule. The dependency itself, verified alone, is
accepted (no `no_exception` there). Closing it means walking imported bodies into the rule (their
calls into the dependency's own classes), i.e. route #269 R5's cross-module edges — left OPEN.
Also out of scope, documented: IMPLICIT exceptions of an uncontracted callee stay ambient (§2.1.13),
and `\all` is the Phase-1 KNOWN set — a function's OWN `raise MyErr` (user class) under
`no_exception \all` still proves (no change; the call-site rule counts a user class as covered).

### Blast radius (M1)
Census first: the rule only computes when a function of the unit claims `no_exception` — 158 corpus
files (all in `pycsl-reference`; 0 in `python-reference`; 0 `#@ no_exception` in the 53 mirror files).
All 158 run `--no-proof` after the patch: 0 refused by the new rule (a first draft that admitted only
class-TYPED variable receivers refused 8 — 1294-1297, 1414/1415/1417/1420, constructor-bound locals and
module-global instances whose declared `raises` the wrap DOES resolve — so the good-receiver set was
widened to match `find_record_var_classes` / `_module_global_classes`).
Corpus byte-diff vs a baseline worktree at 5fe6cbdd: root 1755/1758, 0 MOVED / 0 GONE / 0 APPEARED
(3 new sources: the emitting controls 2951-2953); pyref 2186/2186, 0/0/0. Mirror emit sweep 53/53,
0 MOVED / 0 GONE. Witnesses 2940-2950 PROVED -> refused; controls 2951/2952 PASS -> PASS, 2953 FAIL ->
FAIL (Why3 effect typing, rule silent). Ledgers: refusal-witness census +12 own rows (the plane's own
`_census_row`, own files only; 226 -> 227 demonstrated); truth-args unchanged (2952's `m2` carries
`requires k <= 0` so no admitted argument raises). Planes `--slow` 84/84; mirror sync and mirror-check rc=0.
