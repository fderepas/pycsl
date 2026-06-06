"""Test json.dumps L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import json  # noqa: F401


#@ requires True
#@ ensures True
def use_dumps(x: int) -> int:
    return json.dumps(x)


if __name__ == "__main__":
    pass
