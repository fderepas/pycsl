"""Test json.dump L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import json  # noqa: F401


#@ requires True
#@ ensures True
# (#44) `json.dump(obj, fp)` takes TWO arguments and returns None. This driver
# passed ONE and returned the result into an `int`, so it died at
# "call to 'dump' passes 1 positional argument(s) but parameter 'fp' has no
# default (arity 2)" — a generated-test defect, not an emitter one.
def use_dump(x: int) -> None:
    json.dump(x, x)


if __name__ == "__main__":
    pass
