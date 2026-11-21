"""Test json.load L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# Route #255 (gen #36): expected PASS until route #255; expected FAIL (REFUSED) now. The stub
# `json.load` in src/pycsl_lib/json has NO return annotation, so its result is an erased (`Any`)
# value, and returning it from a function declared `-> int` is refused (route #252). CPython
# returns a `parsed JSON value` here, not an `int`: the driver's own annotation is false.
# pycsl-expected: FAIL
_ = 0  # anchor
import json  # noqa: F401


#@ requires True
#@ ensures True
def use_load(x: int) -> int:
    return json.load(x)


if __name__ == "__main__":
    pass
