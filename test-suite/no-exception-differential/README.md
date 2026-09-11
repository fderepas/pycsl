# `no_exception` DIFFERENTIAL DRIVERS

Each driver here is a small program that declares `#@ no_exception \all` and, under
`if __name__ == "__main__":`, RUNS the thing it declares. The plane
`bin/check-no-exception-differential.py` executes both halves and compares them:

    CPython RAISES  +  PyCSL PROVES   ->  RED. A positive claim that the body raises nothing,
                                          made about a body that demonstrably raises.
    CPython RAISES  +  PyCSL refuses  ->  green (the honest answer).
    CPython RETURNS +  PyCSL PROVES   ->  green (and this is the direction that keeps the
                                          gate from being satisfiable by refusing everything).
    CPython RETURNS +  PyCSL refuses   -> reported as INCOMPLETE, not failed.

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
running it.
