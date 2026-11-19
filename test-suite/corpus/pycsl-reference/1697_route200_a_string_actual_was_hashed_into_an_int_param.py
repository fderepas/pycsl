r"""Test 1697 - ROUTE #200 carrier (gen #30): a STRING LITERAL actual reaching a parameter the callee DECLARES `int` was replaced by `stable_hash` of its own text, so a contract of the callee that NAMES that integer decided. `bin/check-argument-coercion.py` left this substitution standing with the caveat that "a caller cannot predict the hash it would have to name in a contract to exploit it -- but that is a claim about difficulty, not about soundness, so re-probe it if anything ever makes the hash predictable". Nothing had to: `stable_hash` is deterministic and ships in `src/pycsl/module6_whyml/identifiers.py`, and `stable_hash('"a"')` is 747471683. This emitted `(callee 747471683)` and PROVED `\result == 1` while CPython answers 2; the TRUE twin `\result == 2` was REFUSED. Now REFUSED at Module 4 (`PYCSL-SEM-STRARG`), route #51's answer one argument position to the left: a refusal is sound in every clause position, where a `false` would be fail-OPEN in a precondition. This file must FAIL.
"""
# pycsl-expected: FAIL

_ = 0  # anchor


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
