# OPEN ROUTE #317 — AN IMPORTED FUNCTION/METHOD WITHOUT A CONTRACT IS ASSUMED TO WRITE NOTHING (an invented frame, never checked)
**Status: REPAIRED (gen #37, 2026-10-23; opened the same day; inferred frame + refusals), Severity 2 (trust boundary).** Red-team round 16; driver-reproduced on main eb75cbcf (o01 rc=0; CPython violates).
Witnesses `witnesses-r317/`: `from rt16helper import poke` where `poke(xs)` does `xs[0] = 5` with NO contract (o01); imported class method
(o03). Imports lower to `val poke (xs: array int) : unit` with no `writes`; the helper module itself proves rc=0 alone (its default frame
is not stated), yet the combined program is false. annotations.md says imported functions are "trusted stubs (contracts assumed)" —
but here no contract was written: the frame `writes nothing` is invented. With an explicit `assigns \nothing` the helper fails to
type-check (q01), so honest contracts are safe.
Repair: an imported callee with no `assigns` must get the same default frame as a local function (inferred from its verified body, or
`writes` every mutable argument), or the call is refused; document the default frame of imported stubs.

## REPAIR (2026-10-23, r316 executor, repaired together with route #316 — see that file's REPAIR section for the analysis)
Imported functions arrive in the IR as `\trusted` functions WITH their bodies (`ir_resolve` / `pycsl.py` inject them), so
the default frame is INFERRED from the body exactly like a local function's: `_emit_function_block` adds `writes { p }`
to the bodyless `val` of any `\trusted`/imported function with no `#@ assigns`, for every list parameter its body may
write (conservative fixpoint, transitive through its own callees); an imported CLASS method's call stub gets `writes
{ x_i }` through the #316 path. A written non-list parameter cannot be framed -> `PYCSL-VAL-ARG-UNFRAMED`. A stub WITH
`#@ assigns` keeps its declared (assumed) frame. Documented: annotations.md "Multi-file imports" (default frame of an
imported / `\trusted` stub), static-semantics "routes #316 / #317", translational §T.6.22.

| probe | corpus | CPython | 6821931b | after |
|---|---|---|---|---|
| o01_import_fn (`poke(xs)`, no contract) | 4080 | violates | PROVED | FAIL (`val poke ... writes { xs }`) |
| o03_import_cls (`h.poke(ys)`) | 4081 | violates | PROVED | FAIL (stub `writes { x0 }`) |
| u02 local `\trusted` writes record arg | 4085 | violates | PROVED | REFUSED (PYCSL-VAL-ARG-UNFRAMED) |
| k02 imported reader (control) | 4091 | ok | PROVED | PROVED |

Blast radius: shared with #316 (corpus 1 mover, pyref 0, mirror 0 — the mirror imports live modules as trusted bodies,
none of whose list-parameter writes reaches an emitted `val`). Residual: a body-less import (a `.pyi`-style stub with
`...`) infers an empty frame; the old "writes every mutable argument" default is not applied to it (no such import is
resolvable today: imports are `.py` files).
