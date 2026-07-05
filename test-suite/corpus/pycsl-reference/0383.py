"""Test 0383 — interprocedural: caller no_exception E vs callee raises { E }.

The callee `maybe_raise` declares `raises { ZeroDivisionError when n == 0 }`.
The caller declares `no_exception ZeroDivisionError` and strengthens its
precondition to `n != 0`. Module 6 emits an inline
`assert { not (n == 0) }` before the call site; the caller's precondition
discharges it.

Note: the local `m = n` is required to dodge TR-BUG-2 (functions with
`raises` but no local mutation are emitted as `let function` which
WhyML rejects as effectful). See pycsl-annotate skill §"Real-World".
"""
_ = 0  # anchor
#@ requires True
#@ ensures \result == 256 // n
#@ raises ZeroDivisionError when n == 0
#@ assigns \nothing
def maybe_raise(n: int) -> int:
    m = n
    if m == 0:
        raise ZeroDivisionError
    return 256 // m

#@ requires n != 0
#@ ensures \result == 256 // n
#@ assigns \nothing
#@ no_exception ZeroDivisionError
def safe_caller(n: int) -> int:
    return maybe_raise(n)


if __name__ == "__main__":
    assert safe_caller(8) == 32
