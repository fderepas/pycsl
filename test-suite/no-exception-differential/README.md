# `no_exception` DIFFERENTIAL DRIVERS

Each driver here is a small program that declares `#@ no_exception \all` and, under
`if __name__ == "__main__":`, RUNS the thing it declares. The plane
`bin/check-no-exception-differential.py` executes both halves and compares them:

    CPython raises an exception the contract CLAIMS  +  PyCSL PROVES   ->  RED.
                                          A positive claim that the body raises nothing of
                                          that kind, made about a body that demonstrably
                                          raises exactly that kind.
    ... same, but PyCSL refuses       ->  green (the honest answer).
    CPython raises something the contract does NOT claim  ->  OUT OF SCOPE. Reported on
                                          every run, never fatal, never silent.
    CPython RETURNS +  PyCSL PROVES   ->  green (and this is the direction that keeps the
                                          gate from being satisfiable by refusing everything).
    CPython RETURNS +  PyCSL refuses   -> reported as INCOMPLETE, not failed.

## WHY THE VERDICT IS KEYED ON THE EXCEPTION *CLASS*

The first version of this plane ruled RED on `CPython RAISES + PyCSL PROVES`, with no notion
of which exceptions the contract actually claims. **That is a false-positive generator**, and
it matters because of how a gate like this dies: it can only be right by being BIG, and a gate
that cries wolf gets quieted by deleting the offending driver.

`\all` does not mean "every exception Python has". It expands to `KNOWN_EXCEPTIONS`, which is
**five names** — `ZeroDivisionError`, `IndexError`, `KeyError`, `ValueError`, `StopIteration`.
A body that aborts with `AssertionError`, `TypeError`, `AttributeError`, `OverflowError` or
`RecursionError` violates nothing its contract said. `d39_assert_out_of_scope.py` is exactly
such a driver, kept here deliberately: `assert` is lowered to `()` (route #16) and
`AssertionError` is deliberately outside the model, so that driver must report OUT OF SCOPE —
and the fact that it is reported at all is the point. **That population is the honest measure
of how much weaker `\all` is than its name**, and it is printed on every run rather than
being quietly counted as a pass.

Matching uses the model's own subclass relation (`exception_model.handler_catches`), so a
claim over `OSError` is violated by a raised `FileNotFoundError`.

**THE SCOPE CHECK IS FAIL-CLOSED.** If the driver exits non-zero and the exception class
cannot be named, the class is recorded as `?` and treated as IN SCOPE — an unparseable
failure keeps the old, conservative verdict rather than quietly excusing itself.

**NEGATIVE-TESTED, because narrowing a gate is exactly the kind of change that silently
disables one.** With route #66's `chr` trigger row commented out, `d05_chr_negative.py`
measures `raised=ValueError, in_scope=True, proves=True` and the plane reports UNSOUND. The
class check does not soften a genuine route: `ValueError` is one of the five.

**WHY THIS SHAPE.** Six separate soundness routes in the exception model (#64, #65, #66,
#68, #71, #72) were found one probe at a time, and every probe aimed at that surface found
something. The common fact is that **nothing relates `exception_model.TRIGGERS` to the
operations the emitter actually EMITS**. `bin/check-trigger-rows-live.py` scans FROM the
table and cannot see a MISSING row — it reported green on all six.

This gate scans from the other side, and it does not ask anyone to curate a list of what
Python raises: **it RUNS CPython and finds out.** A driver cannot lie about its own
behaviour, so the population can only be wrong by being too small — which is visible, and
which the zero-input guard below turns into a failure rather than a silent pass.

## ADDING A DRIVER

One function, a `#@ no_exception` contract, and a `__main__` block that calls it with
arguments that exercise the edge case. Nothing else. The plane infers everything it needs by
running it — including which exception class CPython actually raised.

**Drivers worth adding are the ones where the hazard has MOVED.** A guard keyed on a
syntactic location is defeated by moving the hazard one step, which happened five separate
times in one generation. `d30`-`d33` are the standing checks on that: the same raising
operation placed in a CALLEE, in a LOOP body, in a TAKEN BRANCH, and behind a call that
slices. All four currently refuse; if one ever starts proving, a guard has been stepped
around.
