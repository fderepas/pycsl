"""Test json.loads L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import json  # noqa: F401


#@ requires True
#@ ensures True
def use_loads(x: int) -> int:
    return json.loads(x)


if __name__ == "__main__":
    pass
