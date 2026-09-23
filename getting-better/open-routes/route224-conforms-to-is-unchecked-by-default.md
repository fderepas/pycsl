# Route #224 (CLOSED, same day) — a declared `#@ conforms_to` is UNCHECKED by default, with no warning

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


---

## CLOSED (2026-09-23, gen #31) — repair 2, exactly as priced above

**The goal follows the DIRECTIVE.** `_populate_protocol_conformance` now tags each pair it
appends to the `overrides` IR list with `"from_conforms_to": True`, and
`Module6_WhyMLTranspiler` calls `_emit_subtyping_goals(functions, conforms_to_only=True)`
when `--check-behavioral-subtyping` is OFF. Both transpile paths (flat and
`#@ verify_module`) take the same rule.

**The implicit inheritance overrides keep their opt-in behaviour exactly**, and that is the
half that was easy to get wrong. The obvious over-broad version — "emit every `overrides`
refinement goal by default" — would have turned on the Liskov obligation for every based
class in the corpus, a change nobody asked for and nobody wrote down. Only the pairs an
explicit `#@ conforms_to` created are tagged, and only those are emitted. Control `1856`
pins it.

MEASURED:

| file | before | after |
|---|---|---|
| the carrier (no flags) | `All contracts formally proven` | **FAILED** |
| the control (`--check-behavioral-subtyping`) | FAILED | FAILED (unchanged) |
| corpus `1806` (already carries the flag, expected FAIL) | FAILED | FAILED |
| corpus `1807` (already carries the flag, control) | SUCCESS | SUCCESS |
| corpus `1753` / `1754` / `1837` | REFUSED | REFUSED |

ZERO corpus verdict changes, because the only two `#@ conforms_to` files that reach
emission already pass the flag in their own `# pycsl-flags`. IR conformance: 38 goldens,
0 MISMATCH — no golden is a conformance driver, so the new IR key moves nothing.

The carrier moved into the corpus as **witness `1855`** (expected FAIL, NO
`# pycsl-flags` — the whole point) with **control `1856`** (a REFINING conformance still
verifies by default). `bin/check-open-route-carriers.py`'s two route-#224 rows are retired
in the same commit, the disposition route #218's entry took: the carrier files stay as
historical evidence and are no longer gated, because an entry asserting SUCCESS would make
that plane red for the right reason at the wrong time.

**What is NOT closed, and is a different route:** #212, the importing unit that believes
every contract of an imported module with `--verify-imports` OFF by default. The shape is
the same ("the DEFAULT still believes") and the argument that closed this one — *an
explicit directive the user wrote should carry its own obligation* — does not transfer,
because an `import` is not a declaration of intent about contracts.
