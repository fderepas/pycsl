# Route #200 — a string actual was hashed into a declared `int` parameter

**Status:** CLOSED (gen #30). SEV-1. Decisive signature present. Closed by a Module 4
REFUSAL, not by an opaque.

## The claim that was wrong — and it was a plane's own caveat

`bin/check-argument-coercion.py`, a plane written THIS generation to classify every
argument substitution, left one standing with this note:

> What remains here is the STRING/TUPLE hash (routes #113/#114): it is injective-by-luck
> only, and a caller cannot predict the hash it would have to name in a contract to exploit
> it — **but that is a claim about difficulty, not about soundness, so re-probe it if
> anything ever makes the hash predictable.**

Nothing had to make it predictable. `stable_hash` is a deterministic function whose source
ships in this repository (`src/pycsl/module6_whyml/identifiers.py`):

```
stable_hash('"a"') == 747471683
```

## The witness

```python
#@ requires True
#@ ensures p == 747471683 ==> \result == 1
#@ ensures p != 747471683 ==> \result == 2
def callee(p: int) -> int:
    if p == 747471683:
        return 1
    return 2

#@ ensures \result == 1
def probe() -> int:
    return callee("a")
```

Emitted `(callee 747471683)`; `\result == 1` PROVED. CPython answers 2. The TRUE twin
`\result == 2` was REFUSED.

Note the callee contract shape. `ensures True` on the callee hides this entire family —
which is why the call boundary survived 199 routes. The contract has to be TRUE OF THE
CALLEE'S OWN BODY and READ the property the substitution changes.

Corpus: `1697_route200_a_string_actual_was_hashed_into_an_int_param.py` (expected FAIL),
`1698_route200_a_declared_type_actual_still_passes.py` (control, PASSES).

## The family, measured spelling by spelling

| spelling | emission | verdict |
|---|---|---|
| `callee("a")` plain call | `(callee 747471683)` | **THE ROUTE** |
| `k.callee("a")` method call | — | already refused |
| `callee((1, 2))` tuple actual | `(callee (any int))` | closed by #194 |
| `callee([])` empty-list actual | — | closed by #195 |

Routes #194/#195 took the collection spellings of this same arm. The string literal is the
one they did not reach, and the hash is what makes it decidable.

## Why a refusal, and why at Module 4

A census of `_coerce_dotted_args` over all 53 mirror emissions found **46** string-literal-
into-`int`-param sites. In every one the parameter is `int` **by erasure** — the callee's
parameter carries no annotation, so the `val` declares `int`. In the witness the parameter
is `int` **by declaration** and the actual is a `str`: a type error Python does not enforce
and the model BELIEVES. That is route #51's situation one argument position to the left,
and route #51's answer is a refusal.

Keying the refusal on the DECLARED annotation leaves all 46 erased sites untouched. Dry-run
of the exact predicate before writing it:

| tree | files | hits |
|---|---|---|
| `test-suite/corpus/pycsl-reference` | 1622 | 0 |
| `src/self-annotate/src` | 53 | 0 |
| `test-suite/corpus/python-reference` | 2217 | 0 |
| `src/pycsl_lib` | 104 | 0 |

**Why inline in `run_ir_semantic_checks`.** The choke-point rule (route #29's note). A new
module-level helper in `core_ir_semantic.py` is an ABSENT function on
`bin/check-mirror-coverage.py` — gen #30 paid for that lesson once already — and a mirror
twin for it, trusted stub or converted, moves that file's emission and buys a whole-file
re-proof. `run_ir_semantic_checks` is `\trusted` in the mirror, so its body needs only
signature parity: no marker, no emission move, no re-proof, no coverage change.

## What the arm's own note now says

`check-argument-coercion.py`'s entry was rewritten rather than deleted. The hash
substitution is still there, and it is now sound **by construction** rather than by
difficulty: every actual that can reach it has an un-annotated parameter, whose callee can
carry no contract naming it. The standing condition is recorded with it — if a
declared-scalar param ever reaches that arm again, the refusal has a hole.

**The lesson is about the caveat, not the arm:** a caveat that rests on an attacker's
difficulty is not a soundness argument, and this one stood for a whole generation inside a
plane written to find exactly this.

## Prediction vs measurement

| | predicted | measured |
|---|---|---|
| the witness | REFUSED by the pipeline (`PYCSL-SEM-STRARG`) | REFUSED |
| the TRUE twin | also refused (that is what a refusal means) | also refused |
| corpus + mirror byte-diff | ZERO | see the battery record in `driver-progress.log` |
