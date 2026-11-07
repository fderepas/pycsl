"""Test json.loads L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# Route #255 (gen #36): expected PASS until route #255; expected FAIL (REFUSED) now. The stub
# `json.loads` in src/pycsl_lib/json has NO return annotation, so its result is an erased (`Any`)
# value, and returning it from a function declared `-> int` is refused (route #252). CPython
# returns a `parsed JSON value` here, not an `int`: the driver's own annotation is false.
# pycsl-expected: FAIL
_ = 0  # anchor
import json  # noqa: F401


#@ requires True
#@ ensures True
# (#44) `json.loads` DECLARES `raises JSONDecodeError` and `raises TypeError`
# in its stub, so a driver calling it must declare them too — otherwise the
# emission is 'this expression raises unlisted exception ...'. The STUB is
# honest here and the driver was under-specified.
#@ raises JSONDecodeError when True
#@ raises TypeError when True
def use_loads(x: int) -> int:
    return json.loads(x)


if __name__ == "__main__":
    pass
