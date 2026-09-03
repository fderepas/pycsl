"""Test 0984 — a Python `assert` reaching a handler that catches `AssertionError` is
REFUSED. The `assert` is lowered to a NO-OP, so that handler is dead in the model and is
the branch Python actually takes.

The emitted body of

    def f(n: int) -> int:
        assert n > 0
        return n

is `(); n`. The assertion is neither checked nor assumed.

OUTSIDE a handler that is CONSERVATIVE and sound — the model must discharge the
postcondition on the path Python aborts, which is strictly harder — so the 1450 `assert`
statements elsewhere in this tree are untouched. INSIDE a `try` it is UNSOUND. Measured,
before this refusal, four shapes, every one printing SUCCESS over `#@ ensures \result == 1`
while Python returns 2:

    try:                              try:
        assert 1 == 2                     v: int = g(-1)      # g asserts n > 0
        return 1                          return 1
    except AssertionError:            except AssertionError:   /  except Exception:
        return 2                          return 2

`AssertionError` is deliberately absent from `exception_model.KNOWN_EXCEPTIONS` (it has no
mathematical implicit trigger), so `#@ no_exception \all` does not cover it either and no
existing plane sees this. Callee exception propagation itself is FINE and was checked
separately: an explicit `raise ValueError` caught by `except ValueError` or by
`except Exception`, and a `1 // 0` caught by `except ZeroDivisionError`, all correctly FAIL
the same false postcondition. The leak is specific to `assert`, the one statement the model
erases.

The refusal covers the INTERPROCEDURAL form as well — a same-module callee that
transitively contains an `assert` is treated exactly like a lexical one.

CENSUS: 0 across `pycsl-reference`, `python-reference`, the mirror, `src/pycsl_lib`, the
live emitter and `tests/` — 3565 files, 454 `try` statements, 1450 `assert` statements, and
ZERO in this shape. Corpus emission byte-identical across all 820 files; mirror L3-tc 53/53;
`src/pycsl_lib` L3-tc unchanged.

REOPENING CAPABILITY: model `assert P` as `if not P: raise AssertionError`, i.e. give
`AssertionError` an explicit (not implicit) trigger in the exception model. The handler
becomes reachable and this refusal can go.

This file is `pycsl-expected: FAIL`: the refusal IS the expected verdict.
"""
# pycsl-expected: FAIL


#@ requires True
#@ ensures \result == 1
#@ assigns \nothing
def driver() -> int:
    try:
        assert 1 == 2
        return 1
    except AssertionError:
        return 2
