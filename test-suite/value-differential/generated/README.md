# GENERATED value-differential corpus — DO NOT HAND-EDIT

Written by `bin/gen-differential-drivers.py`. Regenerate, never patch.

The standing `check-value-differential.py` run SKIPS this directory by
construction (`os.listdir` does not recurse) — the same mechanism that
keeps `negative-test/` out. Run it explicitly:

    bin/check-value-differential.py --generated

Yield = RED / generated, reported per family. Converging = RED per 200
falls to 0 across THREE CONSECUTIVE RUNS WITH THE TEMPLATE SET FROZEN
(`bin/gen-differential-drivers.py --fingerprint`). Adding a family resets
the clock FOR THAT FAMILY ONLY.

```
BLIND SPOTS OF THIS SAMPLER — state these next to every yield figure:
  * Constructs OUTSIDE the template set. Templates are themselves a generator, so template
    coverage is the same blind spot one level up. This is ONE independent instrument over a
    template set someone chose: a real improvement over zero, NOT a solution.
  * Anything needing a `#@ requires` richer than `\result == <int>`.
  * UNSOUND REFUSAL MESSAGE TEXT. Route #90 came from a guard's own remediation advice, and
    no program-level sampler can see English prose. 62 advice-bearing messages remain
    unsampled by anything mechanical; the advice-audit generator stays manual.
  * A family whose fingerprint moved has a RESET convergence clock. Three consecutive
    zero-RED runs only count with the template set FROZEN.
```
