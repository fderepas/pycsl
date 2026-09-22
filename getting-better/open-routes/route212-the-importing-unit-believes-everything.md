# Route #212 — the importing unit believes every contract of an imported module

**Status:** **OPEN** (gen #30). SEV-1, demonstrated twice, with the price of the repair
recorded and the mechanism it needs BUILT but opt-in.

## Two demonstrations, neither needing a single unusual annotation

**(a) A class invariant.** Owner:

```python
#@ class invariant self.v >= 0
class C:
    def __init__(self) -> None: self.v = 0
    #@ assigns self.v
    def sink(self) -> None: self.v = 0 - 5      # breaks the invariant
```

Compiled alone the owner FAILS, correctly. An importer then PROVED

```python
#@ ensures \result >= 0
def probe() -> int:
    c = C(); c.sink(); return c.v
```

CPython answers **-5**, and the TRUE twin `\result == 0 - 5` was REFUSED in that same
importer — the full decisive signature.

**(b) A plain frame lie — no class, no invariant, no `#@ interface`.** Owner declares
`#@ assigns \nothing` over a body that writes `a[0]`; it FAILS alone; the importer of it
PROVED `x - a[0] == 0` where CPython answers -4.

So route #204's repair (interface frames) closed a NARROW SPECIAL CASE of a WIDE hole.

## Why it is open

Route #205's move — re-emit the obligation in the unit that believes it — works for an
`#@ interface` because its goal needs only CONTRACTS. It does NOT work for a frame or a
class invariant: those need the METHOD BODIES, and not lowering imported bodies is the
whole point of the import boundary.

The two cheap alternatives are both wrong. Refusing every import of an invariant-bearing
class breaks legitimate multi-file programs (0441, 0443). Dropping the invariant from
imported records weakens every honest importer.

What it really needs is a **module-level verification certificate**, and the IR has no
provenance field on a function at all.

## What was built anyway: `--verify-imports` (OFF by default)

It resolves each import with the shipping `_resolve_module_path`, verifies the module in a
subprocess carrying the same flag (so verification is TRANSITIVE), passes a seen-set
through `PYCSL_VERIFIED_IMPORTS` so a cycle terminates and a diamond is verified once, and
refuses with `PYCSL-SEM-IMPORT-UNVERIFIED` naming the module that failed.

* dishonest pair: `SUCCESS` without the flag, `PIPELINE ERROR` with it (witness **1722**)
* honest pair: `SUCCESS` both ways (control **1723**)

It stays opt-in, and the reason is a measurement rather than caution: of the **30 distinct
local modules the corpus imports, 23 verify standalone and 7 do not** — five of those seven
are deliberately-bad fixtures whose non-verification IS the scenario of an expected-FAIL
witness, and two (`r143_viaconsts`, `r182_divider`) fail for CONTEXT reasons with
PASS-expected importers. `r143_viaconsts` cannot even resolve the constant its own contract
names when compiled alone.

>>> "VERIFY THE DEPENDENCY STANDALONE" IS NOT ALWAYS WELL-DEFINED. A module can be
>>> meaningful only inside an importing context, so a module-level certificate cannot
>>> simply mean "this file verifies on its own". That is the design note for whoever
>>> closes this route.

## Carrier in the corpus

`1721` (expected FAIL) is the single-file half — the owner module whose `sink()` breaks its
own declared invariant. The two-file halves live in the probe ledger with their exact
commands, because the runner compiles one file at a time.
