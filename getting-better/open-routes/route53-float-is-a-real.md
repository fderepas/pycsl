# OPEN ROUTE #53 — A PYTHON `float` IS MODELLED AS AN EXACT REAL, SO ROUNDING DOES NOT EXIST
# (found 2026-09-08 by relaunch #49 at `223424b9`)

## The demonstration (`scratchpad/w49/probeinv/fl3.py`, `[+] Verification SUCCESS`)

```python
#@ ensures \result == 0.3          # <-- FALSE OF THE PROGRAM
#@ assigns \nothing
def f() -> float:
    return 0.1 + 0.2               # Python: 0.30000000000000004
```

and through a parameter as well (`fl4.py`, also `SUCCESS`):

```python
#@ requires x == 0.1
#@ ensures \result == 0.3
def f(x: float) -> float:
    return x + 0.2
```

`τ(float) = real` (docs/pycsl-static-semantics-reference.md:193). Why3's `real` is the
EXACT mathematical real, where `0.1 + 0.2 = 0.3` holds; Python's `float` is IEEE 754
binary64, where it does not. The model therefore proves an equality the program refutes.

**THIS IS THE DOCUMENTED MODEL, WHICH IS WHY IT MATTERS.** The static-semantics reference
introduces `τ(float) = real` as the FIX for "the unsound `τ(float) = int`", and the README
lists the model's float limitations as "mixed float-int & transcendentals out of scope".
Neither says that the model is exact where the language rounds. A limitation nobody wrote
down is one every reader assumes away.

## The ordering direction is affected too, and it is the sneakier one

`0.1 + 0.2 > 0.3` is TRUE in Python (`0.30000000000000004 > 0.3`) and FALSE over the reals.
Measured: the *guard* form fails closed today (`fl2.py`) because a float literal comparison
in a body guard is not modelled at all — a completeness gap that happens to hide half of this
route. The CONTRACT form is what decides, and that is what fl3/fl4 exercise.

## CENSUS (this tree)

    pycsl-reference files mentioning `float`            17
    files with a `: float` / `-> float` annotation      10 (both corpora)
    mirror files with a float annotation                 4
    src/pycsl_lib float mentions                        63

So a repair is NOT byte-inert and its cost must be measured against those.

## THREE CANDIDATE REPAIRS

1. **Model the real thing.** Why3 has `ieee_float.Float64`; the arithmetic operators become
   `fadd`/`fsub`/`fmul` with a rounding mode, and `0.1` is the binary64 literal nearest to
   one tenth. This is the only repair that makes float contracts MEAN what they say. Cost:
   every float lowering changes, SMT support for FP is uneven (Z3 has it, Alt-Ergo is
   partial), and the corpus's float drivers must be re-proved.
2. **Refuse the decidable float claim.** Keep `real`, but refuse an EQUALITY (and the
   orderings) in a contract when either side is a COMPUTED float — an arithmetic expression
   rather than a literal or a parameter. Fail-closed, cheap, and it states the truth: this
   model cannot decide such a claim. Cost: the ten annotated files, several of which exist
   precisely to state float postconditions.
3. **Carry the error.** Lower float arithmetic to `real` plus an explicit relative-error
   bound (`|r - (a+b)| <= eps * |a+b|`, `eps = 2^-53`), so `\result == 0.3` becomes
   unprovable while `|\result - 0.3| < 1e-9` still proves. The faithful middle, and the
   most work.

**RECOMMENDATION: (2) FIRST, as a fail-closed stop-gap that can land in one increment, with
(1) or (3) recorded as the real repair.** The campaign's rule is that a wrong answer is worse
than no answer, and today this model gives a wrong answer to the FIRST question anyone asks
about a float.
