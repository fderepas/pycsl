# Route #224 (OPEN) — a declared `#@ conforms_to` is UNCHECKED by default, with no warning

**Found:** 2026-09-23, gen #31, **by the first run of a new plane**
(`bin/check-directive-enforcement.py`), which asks of each documented `#@` directive: if I
write it and then VIOLATE it, does anything happen?

## The decisive pair

```python
from typing import Protocol

class P(Protocol):
    #@ ensures \result == 99
    def m(self) -> int: ...


#@ conforms_to P
class C:
    def __init__(self) -> None:
        self.v: int = 0

    #@ ensures \result == 1        # does NOT refine `\result == 99`
    def m(self) -> int:
        return 1
```

    $ pycsl.py <file>
    [+] Verification SUCCESS! All contracts formally proven.

    $ pycsl.py <file> --check-behavioral-subtyping --memory-model hoare
    [-] Verification FAILED or INCOMPLETE.

**No warning of any kind** in the default run — the only diagnostic is a Why3 "unused
variable self".

## The mechanism, and the documentation that pulls two ways

`#@ conforms_to P` populates the existing `overrides` IR list with `(C__m, P__m)` pairs.
Only `--check-behavioral-subtyping` turns those pairs into the refinement goal
`((pre_P -> pre_C) /\ (post_C -> post_P))`. Without the flag the pairs sit in the IR and
nothing reads them.

`test-suite/annotations.md` §12.15 says both things, three lines apart:

> `#@ conforms_to P1, P2, …` (a class-level directive, parallel to `#@ compose_from`)
> declares that a class conforms to the named protocols, **synthesizing per-method
> contract-refinement VCs**.

and then, in the Static plane paragraph:

> Conformance `C conforms to P` (declared via `#@ conforms_to P`) populates the EXISTING
> `overrides` IR list with `(C__m, P__m)` pairs; **`--check-behavioral-subtyping` emits the
> per-method refinement goal**.

The first sentence is the one a reader takes away, and it attributes the VCs to the
DIRECTIVE. The second attributes the goal to the FLAG. Both are in the normative document.

## Why it is a route and not a documented limitation

It is the same shape as **route #212** (an importing unit believes every contract of an
imported module; `--verify-imports` is OFF by default), which gen #30 recorded as OPEN for
exactly this reason: *the DEFAULT still believes*. The tool prints `All contracts formally
proven` over a module carrying a declared obligation that nothing checked, and says nothing
about the omission. A flag that must be remembered is not a check; it is a check plus a way
to forget it.

## Repairs, un-priced

1. **Warn** when `#@ conforms_to` is present and `--check-behavioral-subtyping` is off. One
   line, honest, and it does not change any verdict.
2. **Emit the refinement goal whenever `#@ conforms_to` is written**, flag or not — the
   directive is an explicit, opt-in declaration, so the goal it names could simply follow it.
   This is the repair the §12.15 opening sentence already describes.
3. **Refuse** `#@ conforms_to` without the flag. Loudest, and probably too loud: the
   directive also drives non-goal machinery.

Repair 2 is the one to price first, and it is a small corpus question rather than a value-model
one: the population is the three corpus files that declare `#@ conforms_to`.

## Carrier

* `route224-carrier-conforms-to-unchecked-by-default.py` — expects SUCCESS (the default run)
* `route224-control-conforms-to-with-the-flag.py` — expects FAILED (the same file under
  `--check-behavioral-subtyping`), which is what localises the gap to the DEFAULT rather than
  to the checker.
